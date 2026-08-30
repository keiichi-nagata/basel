#!/usr/bin/env python3
"""話題のドラマ総合ランキング — 週次データ収集.

TVer週間 / Netflix Japan Top10 / Google トレンド を集め、TMDB で作品メタ
（日本語タイトル・話数・あらすじ・日本の配信状況）を補完し、合成スコアを
計算して

    dev/3-drama/data/YYYY-Www.json    生データ + スコア内訳 + 出典
    dev/3-drama/drafts/YYYY-Www.md    template.md 準拠の下書き（AI分析欄は空）

を生成する。処理順は「収集 → TMDB補完 → 日本語タイトル確定・アニメ除外 →
その日本語名で Google トレンド取得 → 合成 → 出力」。各ソースは取得失敗時に

    dev/3-drama/data/inputs/YYYY-Www.<source>.json

を手動フォールバックとして読む（フォーマットは inputs/README.md）。
公開前の人手レビューは会社ルールで必須。

合成式（ADR 0002）:
  A = TVer週間順位を 0-100 正規化   score = 100 * (N - rank + 1) / N
  B = Netflix Japan Top10 順位を同式で正規化（N=10）
  C = Google トレンド（過去7日・日本）の相対値 0-100
  合成スコア = その作品に存在する要素だけの単純平均
  ランク付け条件: A または B の少なくとも一方に入っていること（アニメは除外）
"""
from __future__ import annotations

import csv
import io
import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import requests

try:  # Windows コンソールの文字化け対策（ファイル出力は常に UTF-8）
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # noqa: BLE001
    pass

REPO_ROOT = Path(__file__).resolve().parents[3]


def _load_dotenv() -> None:
    """依存を増やさず .env を読む（ローカル実行用。CI では Secrets が環境変数）。"""
    candidates = [REPO_ROOT / ".env", REPO_ROOT / ".env.txt", Path.cwd() / ".env"]
    env_path = next((p for p in candidates if p.exists()), None)
    if env_path is None:
        print(f"[env] .env が見つかりません（探索: {', '.join(str(p) for p in candidates)}）")
        return
    loaded = []
    for line in env_path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip().removeprefix("export ").removeprefix("set ").strip()
        val = val.strip().strip('"').strip("'")
        if key and val:
            os.environ.setdefault(key, val)
            loaded.append(key)
    print(f"[env] {env_path} を読み込み: {', '.join(loaded) or '(空)'}")


_load_dotenv()

DRAMA_DIR = REPO_ROOT / "dev" / "3-drama"
DATA_DIR = DRAMA_DIR / "data"
INPUT_DIR = DATA_DIR / "inputs"
DRAFT_DIR = DRAMA_DIR / "drafts"

JST = timezone(timedelta(hours=9))
TMDB_BASE = "https://api.themoviedb.org/3"
NETFLIX_TSV_URL = "https://www.netflix.com/tudum/top10/data/all-weeks-countries.tsv"
TVER_LIST_LEN_CAP = 20
HTTP_TIMEOUT = 30
USER_AGENT = "basel-drama-ranking/1.0 (+https://github.com/keiichi-nagata/basel)"
TMDB_ATTRIBUTION = (
    "This product uses the TMDB API and JustWatch data but is not endorsed "
    "or certified by TMDB or JustWatch."
)
# ドラマ以外として除外する TMDB TV ジャンル（アニメ・リアリティ・トーク・ニュース）
EXCLUDE_GENRES = {16: "アニメ", 10764: "リアリティ", 10767: "トーク", 10763: "ニュース"}

# もしも承認等で扱えるようになったら affiliates.json に URL を入れる（下で読み込み）
AFFILIATE_CANDIDATES = {"ABEMA", "Abema TV", "Amazon Prime Video", "U-NEXT", "Hulu",
                        "DMM TV", "Lemino", "dアニメストア", "TELASA", "FOD"}
AFFILIATES_PATH = DRAMA_DIR / "affiliates.json"


def _load_affiliates() -> dict[str, str]:
    try:
        raw = json.loads(AFFILIATES_PATH.read_text(encoding="utf-8"))
        return {k: v for k, v in raw.items() if not k.startswith("_") and isinstance(v, str) and v}
    except Exception:  # noqa: BLE001
        return {}


AFFILIATE_URLS = _load_affiliates()

# 見放題だけを見る。rent/buy は含めない。
SVOD_KINDS = ("flatrate", "free", "ads")
PROVIDER_NORMALIZE = {
    "Disney Plus": "Disney+",
    "Netflix Standard with Ads": "Netflix",
    "Amazon Prime Video with Ads": "Amazon Prime Video",
    "TELESA": "TELASA",
}


# --------------------------------------------------------------------------- utils
def target_week(now: datetime | None = None) -> dict[str, str]:
    """直近で完了した週（月〜日）を返す。月曜早朝に走らせる前提。"""
    now = now or datetime.now(JST)
    today = now.date()
    this_monday = today - timedelta(days=today.weekday())
    last_monday = this_monday - timedelta(days=7)
    last_sunday = this_monday - timedelta(days=1)
    iso_year, iso_week, _ = last_monday.isocalendar()
    return {
        "week": f"{iso_year}-W{iso_week:02d}",
        "from": last_monday.isoformat(),
        "to": last_sunday.isoformat(),
        "sunday": last_sunday.isoformat(),
        "year": iso_year,
    }


def load_manual(week: str, source: str) -> Any | None:
    path = INPUT_DIR / f"{week}.{source}.json"
    if path.exists():
        print(f"[{source}] 手動入力ファイルを使用: {path.relative_to(REPO_ROOT)}")
        return json.loads(path.read_text(encoding="utf-8"))
    return None


def norm_rank(rank: int | None, list_len: int) -> float:
    if not rank or rank < 1:
        return 0.0
    return round(100 * (list_len - rank + 1) / list_len, 1)


_ZERO_WIDTH = str.maketrans({c: None for c in "﻿​‌‍⁠"})


def clean_title(s: str) -> str:
    return (s or "").translate(_ZERO_WIDTH).strip()


def squash(s: str) -> str:
    return "".join(clean_title(s).split()).replace("　", "").lower()


# ---------------------------------------------------------------------- collectors
def fetch_netflix(week_sunday: str, week: str) -> list[dict]:
    """Netflix 公式 Tudum の週次データファイル（全週×国のTSV）から日本のTVを抽出。"""
    try:
        resp = requests.get(
            NETFLIX_TSV_URL, headers={"User-Agent": USER_AGENT}, timeout=HTTP_TIMEOUT
        )
        resp.raise_for_status()
        rows = list(csv.DictReader(io.StringIO(resp.text), delimiter="\t"))

        def is_jp_tv(r: dict) -> bool:
            return r.get("country_iso2") == "JP" and "TV" in (r.get("category") or "").upper()

        picked = [r for r in rows if is_jp_tv(r) and r.get("week") == week_sunday]
        if not picked:
            earlier = sorted(
                (r for r in rows if is_jp_tv(r) and (r.get("week") or "") <= week_sunday),
                key=lambda r: r["week"],
            )
            if earlier:
                latest = earlier[-1]["week"]
                picked = [r for r in earlier if r["week"] == latest]
                print(f"[netflix] 対象週 {week_sunday} のデータ無し。直近の {latest} を使用")
        result = [
            {
                "rank": int(r["weekly_rank"]),
                "title": clean_title(r.get("show_title") or r.get("season_title") or ""),
                "weeks": int(r.get("cumulative_weeks_in_top_10") or 0),
            }
            for r in picked
            if r.get("weekly_rank")
        ]
        result.sort(key=lambda x: x["rank"])
        if result:
            return result
        print("[netflix] 取得0件。フォールバックへ")
    except Exception as exc:  # noqa: BLE001
        print(f"[netflix] 取得失敗: {exc}")
    return load_manual(week, "netflix") or []


TVER_PLATFORM_API = "https://platform-api.tver.jp"
TVER_HEADERS = {
    "User-Agent": USER_AGENT,
    "Origin": "https://tver.jp",
    "Referer": "https://tver.jp/",
    "x-tver-platform-type": "web",
}
# callEpisodeRanking は13ジャンルのランキング束を返す。その中の group id を選ぶ。
TVER_RANKING_PATH_DEFAULT = "/service/api/v1/callEpisodeRanking"
TVER_RANKING_GROUP = os.environ.get("TVER_RANKING_GROUP", "drama")  # drama / classicdrama 等


def _tver_auth() -> dict | None:
    """browser/create ハンドシェイクで platform_uid / platform_token を得る。"""
    try:
        resp = requests.post(
            f"{TVER_PLATFORM_API}/v2/api/platform_users/browser/create",
            headers={**TVER_HEADERS, "Content-Type": "application/x-www-form-urlencoded"},
            data="device_type=pc",
            timeout=HTTP_TIMEOUT,
        )
        resp.raise_for_status()
        r = resp.json().get("result", {})
        if r.get("platform_uid") and r.get("platform_token"):
            return {"platform_uid": r["platform_uid"], "platform_token": r["platform_token"]}
    except Exception as exc:  # noqa: BLE001
        print(f"[tver] 認証取得失敗: {exc}")
    return None


def _tver_episodes_to_rows(episodes: list, exclude_nhk: bool = True) -> list[dict]:
    out, seen = [], set()
    for ep in episodes or []:
        if not isinstance(ep, dict):
            continue
        c = ep.get("content") if isinstance(ep.get("content"), dict) else ep
        if exclude_nhk and c.get("isNHKContent"):
            continue
        title = (c.get("seriesTitle") or c.get("title") or "").strip()
        if not title or title in seen:
            continue
        seen.add(title)
        out.append({"rank": ep.get("rank", len(out) + 1), "title": title,
                    "broadcaster": c.get("broadcasterName")})
        if len(out) >= TVER_LIST_LEN_CAP:
            break
    for i, r in enumerate(out, start=1):
        r["rank"] = i
    return out


def _tver_parse(payload: Any, group: str = TVER_RANKING_GROUP) -> list[dict]:
    """callEpisodeRanking 応答から指定ジャンルグループの [{"rank","title"}] を取り出す。

    応答は result.contents = [ {type:"...Ranking", content:{id:"drama"...}, contents:[episode...]}, ... ]
    という13ジャンルの束。id が一致するグループの内側 contents を使う。
    グループ構造でない場合はフラットに episode 列として解釈する。
    """
    node = payload.get("result", payload) if isinstance(payload, dict) else payload
    groups = node.get("contents") if isinstance(node, dict) else node
    if not isinstance(groups, list) or not groups:
        return []
    if isinstance(groups[0], dict) and isinstance(groups[0].get("contents"), list):
        chosen = next(
            (g for g in groups if str((g.get("content") or {}).get("id", "")).lower() == group),
            None,
        )
        if chosen is None:
            avail = [str((g.get("content") or {}).get("id")) for g in groups]
            print(f"[tver] グループ '{group}' が無い。利用可能: {', '.join(avail)}")
            return []
        return _tver_episodes_to_rows(chosen.get("contents", []))
    return _tver_episodes_to_rows(groups)


def fetch_tver(week: str) -> list[dict]:
    """TVer 週間ドラマランキング。

    browser/create ハンドシェイク → callEpisodeRanking を叩き、応答内の
    '{TVER_RANKING_GROUP}' グループ（既定: drama）を取り出す。失敗時は手動入力
    （data/inputs/<week>.tver.json）へ自動フォールバックする。
    環境変数: TVER_RANKING_URL（完全URL上書き）/ TVER_RANKING_PATH（パス上書き）/
    TVER_RANKING_GROUP（グループid）。
    """
    full_url = os.environ.get("TVER_RANKING_URL", "").strip()
    path = os.environ.get("TVER_RANKING_PATH", "").strip() or TVER_RANKING_PATH_DEFAULT

    auth = _tver_auth()
    if not auth:
        print("[tver] 認証取れず。手動入力（inputs/README.md）を使用")
        return load_manual(week, "tver") or []

    url = full_url or f"{TVER_PLATFORM_API}{path}"
    try:
        resp = requests.get(url, headers=TVER_HEADERS, params=auth, timeout=HTTP_TIMEOUT)
        if resp.status_code != 200:
            print(f"[tver] {url} -> HTTP {resp.status_code}")
            return load_manual(week, "tver") or []
        payload = resp.json()
        raw_dir = DATA_DIR / "raw"
        raw_dir.mkdir(parents=True, exist_ok=True)
        (raw_dir / f"tver_{week}.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        rows = _tver_parse(payload)
        if rows:
            print(f"[tver] {TVER_RANKING_GROUP} グループから {len(rows)}件")
            return rows
        print("[tver] 0件。フォールバックへ")
    except Exception as exc:  # noqa: BLE001
        print(f"[tver] 取得失敗: {exc}")
    return load_manual(week, "tver") or []


def fetch_trends(titles: list[str], week: str) -> dict[str, float]:
    """Google トレンド（過去7日, geo=JP）の相対関心度を 0-100 で返す。

    pytrends は 5 語/バッチ制限があるため、先頭語をアンカーに複数バッチを連結する。
    Google のレート制限で落ちやすいので、失敗時は手動入力へフォールバック。
    キーワードは日本語タイトルで渡すこと（英題だと検索ボリュームがほぼ出ない）。
    """
    titles = [t for t in dict.fromkeys(t.strip() for t in titles) if t]
    if not titles:
        return {}
    try:
        from pytrends.request import TrendReq

        pt = TrendReq(hl="ja-JP", tz=-540)
        anchor = titles[0]
        rest = titles[1:]
        batches = (
            [titles]
            if len(titles) <= 5
            else [[anchor, *rest[i : i + 4]] for i in range(0, len(rest), 4)]
        )
        raw: dict[str, float] = {}
        anchor_ref: float | None = None
        for bi, batch in enumerate(batches):
            df = None
            for attempt in range(3):
                try:
                    pt.build_payload(batch, timeframe="now 7-d", geo="JP")
                    df = pt.interest_over_time()
                    break
                except Exception as exc:  # noqa: BLE001
                    print(f"[trends] batch {bi} try {attempt + 1} 失敗: {exc}")
                    time.sleep(12)
            if df is None or df.empty:
                continue
            means = {k: float(df[k].mean()) for k in batch if k in df.columns}
            if bi == 0:
                anchor_ref = means.get(anchor) or 1.0
                raw.update(means)
            else:
                a = means.get(anchor) or 0.0
                factor = (anchor_ref / a) if (anchor_ref and a) else 0.0
                for k, v in means.items():
                    if k != anchor:
                        raw[k] = v * factor
            time.sleep(6)
        if raw:
            mx = max(raw.values()) or 1.0
            return {k: round(100 * v / mx, 1) for k, v in raw.items()}
        print("[trends] 全バッチ失敗。フォールバックへ")
    except Exception as exc:  # noqa: BLE001
        print(f"[trends] 取得失敗: {exc}")
    manual = load_manual(week, "trends")
    return {str(k): float(v) for k, v in manual.items()} if manual else {}


# -------------------------------------------------------------------------- tmdb
def tmdb_get(path: str, params: dict | None = None) -> dict:
    token = os.environ.get("TMDB_API_TOKEN")
    if not token:
        raise RuntimeError("TMDB_API_TOKEN 未設定（.env または GitHub Secrets）")
    resp = requests.get(
        f"{TMDB_BASE}{path}",
        headers={"Authorization": f"Bearer {token}", "accept": "application/json"},
        params=params or {},
        timeout=HTTP_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()


def _year_of(date_str: str) -> int:
    head = (date_str or "")[:4]
    return int(head) if head.isdigit() else 0


def _pick_candidate(title: str, results: list[dict], ref_year: int) -> dict | None:
    """検索結果から最も妥当な1件を選ぶ。

    優先度: original_name の一致 > 表記の部分一致 > 新しめの年代 > 人気度。
    Netflix TSV は英題で来るため、日本語作品では original_name（原題）との一致が効く。
    """
    if not results:
        return None
    q = squash(title)

    def score(c: dict) -> float:
        s = 0.0
        orig = squash(c.get("original_name", ""))
        name = squash(c.get("name", ""))
        if q and orig and q == orig:
            s += 40
        elif q and (q in orig or q in name or (orig and orig in q)):
            s += 18
        yr = _year_of(c.get("first_air_date", ""))
        if yr:
            s -= max(0, ref_year - yr) * 1.2   # 古いほど減点（緩め）
            if yr > ref_year:
                s -= (yr - ref_year) * 1.5     # 未来作は強めに減点
        else:
            s -= 12
        s += min(float(c.get("popularity") or 0.0), 400.0) * 0.02
        return s

    return max(results, key=score)


def clean_providers(jp_block: dict) -> list[str]:
    names: list[str] = []
    for kind in SVOD_KINDS:
        for p in jp_block.get(kind, []) or []:
            name = p["provider_name"]
            # 「◯◯ Amazon Channel」等のチャンネル販売はベース名に寄せる
            for suffix in (" Amazon Channel", " Apple TV Channel", " Channel"):
                if name.endswith(suffix):
                    name = name[: -len(suffix)]
            name = PROVIDER_NORMALIZE.get(name, name)
            if name and name not in names:
                names.append(name)
    return names


def enrich_tmdb(title: str, ref_year: int) -> dict:
    info: dict[str, Any] = {
        "tmdb_id": None,
        "matched_title": None,
        "match_confidence": "low",
        "excluded_genre": None,   # "アニメ" / "リアリティ" 等。非Noneならランク対象外
        "overview": "",
        "season_number": None,
        "episodes_aired": None,
        "episodes_total": None,
        "episodes_uncertain": True,
        "first_air_date": "",
        "providers_jp": [],
        "needs_check": True,
    }
    try:
        results = tmdb_get(
            "/search/tv",
            {"query": title, "language": "ja-JP", "region": "JP", "include_adult": "false"},
        ).get("results") or []
        cand = _pick_candidate(title, results, ref_year)
        if not cand:
            print(f"[tmdb] '{title}' 一致なし")
            return info
        tid = cand["id"]
        detail = tmdb_get(f"/tv/{tid}", {"language": "ja-JP"})
        genres = [g["id"] for g in detail.get("genres", [])]
        orig = detail.get("original_name") or ""
        matched = clean_title(detail.get("name") or orig)
        info["tmdb_id"] = tid
        info["matched_title"] = matched
        info["excluded_genre"] = next(
            (label for gid, label in EXCLUDE_GENRES.items() if gid in genres), None
        )
        info["overview"] = (detail.get("overview") or "").strip()
        total = detail.get("number_of_episodes")
        lea = detail.get("last_episode_to_air") or {}
        info["season_number"] = lea.get("season_number")
        info["episodes_aired"] = lea.get("episode_number")
        # TMDB は地上波作品で number_of_episodes が実話数より小さいことがある → 無効化
        if total and info["episodes_aired"] and total < info["episodes_aired"]:
            total = None
        info["episodes_total"] = total
        info["episodes_uncertain"] = info["episodes_aired"] is None or total is None
        info["first_air_date"] = detail.get("first_air_date") or ""
        jp = (tmdb_get(f"/tv/{tid}/watch/providers").get("results") or {}).get("JP") or {}
        info["providers_jp"] = clean_providers(jp)

        q, so, sm = squash(title), squash(orig), squash(matched)
        # 短いクエリ（例 "Sai"）は完全一致のみ許可。長ければ部分一致も可
        name_hit = bool(q) and (
            q == so
            or (len(q) >= 4 and (q in so or q in sm or (so and so in q)))
        )
        yr = _year_of(info["first_air_date"])
        recent = bool(yr) and (ref_year - 3) <= yr <= (ref_year + 1)
        has_body = bool(info["overview"])
        # あらすじが取れて年代も妥当なら「照合OK」。それ以外は必ず要確認
        if recent and has_body:
            info["match_confidence"] = "ok"
            info["needs_check"] = not (name_hit or info["episodes_aired"] is not None)
        else:
            info["match_confidence"] = "low"
            info["needs_check"] = True
            info["episodes_uncertain"] = True
    except Exception as exc:  # noqa: BLE001
        print(f"[tmdb] '{title}' 取得失敗: {exc}")
    return info


# --------------------------------------------------------------------- composite
def assemble_slots(tver: list[dict], netflix: list[dict]) -> dict[str, dict]:
    tver_len = min(max(len(tver), 1), TVER_LIST_LEN_CAP)
    slots: dict[str, dict] = {}

    def slot(t: str) -> dict:
        return slots.setdefault(
            squash(t), {"title": t.strip(), "source_title": t.strip(),
                        "A": None, "B": None, "C": None}
        )

    for row in tver:
        slot(row["title"])["A"] = {"rank": row["rank"], "score": norm_rank(row["rank"], tver_len)}
    for row in netflix:
        slot(row["title"])["B"] = {
            "rank": row["rank"], "weeks": row.get("weeks"),
            "score": norm_rank(row["rank"], 10),
        }
    return slots


def finalize_ranking(slots: dict[str, dict]) -> list[dict]:
    items: list[dict] = []
    for s in slots.values():
        if not (s["A"] or s["B"]):
            continue
        comps = [c for c in (
            s["A"]["score"] if s["A"] else None,
            s["B"]["score"] if s["B"] else None,
            s["C"],
        ) if c is not None]
        s["composite"] = round(sum(comps) / len(comps), 1) if comps else 0.0
        items.append(s)
    items.sort(key=lambda x: x["composite"], reverse=True)
    for i, s in enumerate(items, start=1):
        s["rank"] = i
    return items


# ------------------------------------------------------------------------ output
def provider_affiliate(name: str) -> str:
    if AFFILIATE_URLS.get(name):
        return "linked"
    if name in AFFILIATE_CANDIDATES:
        return "pending"
    return "none"


def provider_label(name: str) -> str:
    url = AFFILIATE_URLS.get(name)
    if url:
        return f"[{name}（無料トライアル）]({url}) [PR]"
    if name in AFFILIATE_CANDIDATES:
        return f"{name}（提携準備中）"
    return name


def episode_text(meta: dict) -> str:
    ep = meta.get("episodes_aired")
    if not ep:
        return "【話数要確認】"
    return f"第{ep}話まで【要確認】" if meta.get("episodes_uncertain") else f"第{ep}話まで"


def assemble_json(wk: dict, items: list[dict], excluded: list[dict],
                  tver, netflix, trends) -> dict:
    now = datetime.now(JST).isoformat(timespec="seconds")
    out_items = []
    for s in items:
        meta = s.get("meta", {})
        out_items.append(
            {
                "rank": s["rank"],
                "title": s["title"],
                "source_title": s.get("source_title", s["title"]),
                "composite_score": s["composite"],
                "components": {"A_tver": s["A"], "B_netflix": s["B"], "C_trends": s["C"]},
                "tmdb_id": meta.get("tmdb_id"),
                "matched_title": meta.get("matched_title"),
                "match_confidence": meta.get("match_confidence", "low"),
                "episodes": {
                    "season": meta.get("season_number"),
                    "aired": meta.get("episodes_aired"),
                    "total": meta.get("episodes_total"),
                    "uncertain": meta.get("episodes_uncertain", True),
                },
                "overview": meta.get("overview", ""),
                "providers_jp": [
                    {"name": n, "affiliate": provider_affiliate(n)}
                    for n in meta.get("providers_jp", [])
                ],
                "first_air_date": meta.get("first_air_date", ""),
            }
        )
    return {
        "week": wk["week"],
        "range": {"from": wk["from"], "to": wk["to"]},
        "collected_at": now,
        "sources": {
            "tver": {"count": len(tver), "fetched_at": now},
            "netflix": {"url": NETFLIX_TSV_URL, "count": len(netflix), "fetched_at": now},
            "google_trends": {"timeframe": "now 7-d", "geo": "JP", "count": len(trends),
                              "fetched_at": now},
            "tmdb": {"attribution": TMDB_ATTRIBUTION, "fetched_at": now},
        },
        "excluded": [{"title": e["title"], "matched": e["meta"].get("matched_title"),
                      "reason": e["meta"].get("excluded_genre")} for e in excluded],
        "items": out_items,
    }


def render_draft(wk: dict, items: list[dict]) -> str:
    L: list[str] = []
    L.append("> この記事はプロモーション（アフィリエイトリンク）を含みます。")
    L.append("")
    L.append(f"## 話題のドラマ総合ランキング（{wk['week']} / {wk['from']} 〜 {wk['to']}）")
    L.append("")
    L.append(
        "TVer週間ランキング・Netflix Japan 週間Top10・Google検索トレンドを合成した"
        "「話題度」の総合指標です。横断的な視聴数そのものを測ったものではありません。"
        "対象は民放ドラマ＋配信ドラマ（NHK作品・アニメ・リアリティ番組は指標の性質上ランク外）。"
    )
    L.append("")
    L.append("| 順位 | 作品 | 合成 | TVer(A) | Netflix(B) | トレンド(C) | 話数 | 主な配信 |")
    L.append("|---|---|---|---|---|---|---|---|")
    for s in items:
        meta = s.get("meta", {})
        a = f"{s['A']['rank']}位" if s["A"] else "—"
        b = f"{s['B']['rank']}位" if s["B"] else "—"
        c = f"{s['C']}" if s["C"] is not None else "—"
        provs = "／".join(meta.get("providers_jp", [])[:3]) or "【要確認】"
        flag = " ⚠️別作品の可能性" if meta.get("match_confidence") == "low" else ""
        L.append(
            f"| {s['rank']} | {s['title']}{flag} | {s['composite']} | {a} | {b} | {c} "
            f"| {episode_text(meta)} | {provs} |"
        )
    L.append("")
    L.append(
        f"出典: TVer週間ランキング（{wk['to']}時点）／ Netflix Tudum Top 10 Japan（{wk['to']}時点）"
        f"／ Google トレンド（{wk['from']}〜{wk['to']}）"
    )
    L.append("")
    L.append("## 各作品")
    L.append("")
    for s in items:
        meta = s.get("meta", {})
        head = f"### {s['rank']}位: {s['title']}"
        if meta.get("episodes_aired"):
            head += f"（{episode_text(meta)}）"
        L.append(head)
        L.append("")
        if meta.get("match_confidence") == "low":
            L.append("- ⚠️ **TMDBの照合信頼度が低い**。作品名・話数・配信を必ず確認して修正")
        ov = (meta.get("overview") or "").strip()
        L.append(f"- **あらすじ**: {ov if ov else '【要記入: 公式サイトを基に2〜3文で】'}")
        if ov:
            L.append("  - ※TMDB由来。公式サイトで確認し、自分の言葉に書き直すこと")
        prov_lines = [provider_label(n) for n in meta.get("providers_jp", [])]
        L.append(f"- **配信**: {' / '.join(prov_lines) if prov_lines else '【要確認】'}")
        L.append("- **人気の理由（AI分析）**: 【ranking-writer 記入】事実（キャスト・原作・話題の"
                 "出来事）と指標の動き（トレンドがスパイク型かじわ伸びか／TVerとNetflixどちらで強いか）を根拠に")
        L.append("")
    L.append("## 今週の定点観測 —「リアタイ型」か「見逃し・配信型」か")
    L.append("")
    L.append("【ranking-writer 記入】TVer順位（見逃し）と放送直後のトレンドの立ち上がり方から、"
             "各作品が本放送で見られているか後追いで伸びているかを分析。")
    L.append("")
    L.append("## 来週の注目")
    L.append("")
    L.append("【ranking-writer 記入】次回予告・新規スタート作品から。")
    L.append("")
    L.append("## このランキングの作り方")
    L.append("")
    L.append(
        "TVer週間ランキング順位、Netflix Japan 週間Top10順位、Google検索トレンド（過去7日）の"
        "3要素を各0〜100に正規化し、その作品に存在する要素の単純平均を合成スコアとしています。"
        "TVer・Netflixのいずれにも入らない作品、アニメ、恋愛リアリティー等のバラエティは対象外です。"
        "配信状況は TMDB / JustWatch のデータを利用しています（TMDBの公認を受けたものではありません）。"
    )
    L.append("")
    L.append("## 次回")
    L.append("")
    L.append("来週〔曜日〕更新。マガジンのフォローで通知が届きます。")
    L.append("（開発1部の有料noteへの1行導線）")
    L.append("")
    return "\n".join(L)


def _jp_font() -> str | None:
    from matplotlib import font_manager

    for name in ("Noto Sans CJK JP", "Noto Sans JP", "IPAexGothic", "IPAGothic",
                 "TakaoPGothic", "Yu Gothic", "Meiryo", "MS Gothic", "Hiragino Sans"):
        try:
            if font_manager.findfont(name, fallback_to_default=False):
                return name
        except Exception:  # noqa: BLE001
            continue
    return None


def render_png(wk: dict, items: list[dict], out_path: Path) -> bool:
    """note / SNS にそのまま貼れるランキング表の画像を書き出す。失敗しても致命的にしない。"""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        font = _jp_font()
        if font:
            matplotlib.rcParams["font.family"] = font
        else:
            print("[png] 日本語フォントが見つからず文字化けの可能性（fonts-noto-cjk を導入）")

        headers = ["順位", "作品", "合成", "TVer", "Netflix", "トレンド"]
        rows = []
        for s in items:
            rows.append([
                str(s["rank"]),
                s["title"] + ("  ※要確認" if s["meta"].get("match_confidence") == "low" else ""),
                f"{s['composite']:.0f}",
                f"{s['A']['rank']}位" if s["A"] else "—",
                f"{s['B']['rank']}位" if s["B"] else "—",
                f"{s['C']:.0f}" if s["C"] is not None else "—",
            ])

        fig, ax = plt.subplots(figsize=(9.2, 1.3 + 0.5 * len(rows)))
        ax.axis("off")
        ax.set_title(f"話題のドラマ総合ランキング  {wk['from']}〜{wk['to']}",
                     fontsize=15, fontweight="bold", pad=18, loc="left")
        tbl = ax.table(cellText=rows, colLabels=headers, loc="center", cellLoc="center")
        tbl.auto_set_font_size(False)
        tbl.set_fontsize(11)
        tbl.scale(1, 1.6)
        widths = [0.07, 0.5, 0.09, 0.1, 0.11, 0.12]
        for (r, col), cell in tbl.get_celld().items():
            cell.set_width(widths[col])
            cell.set_edgecolor("#d0d0d0")
            if r == 0:
                cell.set_facecolor("#2b2b2b")
                cell.set_text_props(color="white", fontweight="bold")
            else:
                if col == 1:
                    cell.set_text_props(ha="left")
                    cell.PAD = 0.03
                cell.set_facecolor("#ffffff" if r % 2 else "#f4f6f8")
        fig.text(0.5, 0.02,
                 "TVer週間 / Netflix Japan Top10 / Google トレンドの合成指標（横断視聴数ではありません）",
                 ha="center", fontsize=8, color="#888888")
        fig.savefig(out_path, dpi=200, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        print(f"生成: {out_path.relative_to(REPO_ROOT)}")
        return True
    except Exception as exc:  # noqa: BLE001
        print(f"[png] 生成失敗（スキップ）: {exc}")
        return False


# -------------------------------------------------------------------------- main
def main() -> int:
    for d in (DATA_DIR, INPUT_DIR, DRAFT_DIR):
        d.mkdir(parents=True, exist_ok=True)

    wk = target_week()
    print(f"対象週: {wk['week']} ({wk['from']} 〜 {wk['to']})")

    tver = fetch_tver(wk["week"])
    netflix = fetch_netflix(wk["sunday"], wk["week"])
    print(f"  TVer: {len(tver)}件 / Netflix: {len(netflix)}件")

    slots = assemble_slots(tver, netflix)

    # TMDB 補完 → 日本語タイトル確定・アニメ除外
    kept: dict[str, dict] = {}
    excluded: list[dict] = []
    for key, s in slots.items():
        meta = enrich_tmdb(s["source_title"], wk["year"])
        s["meta"] = meta
        matched = meta.get("matched_title") or ""
        # 照合できた作品は TMDB の正式表記を採用（Netflix TSV は英題・表記ゆれのため）
        if matched and (
            meta.get("match_confidence") == "ok"
            or any(ord(ch) > 0x2E7F for ch in matched)
        ):
            s["title"] = matched
        if meta.get("excluded_genre"):
            print(f"  除外({meta['excluded_genre']}): {s['source_title']} -> {matched}")
            excluded.append(s)
            continue
        kept[key] = s
        time.sleep(0.25)

    # 同一 tmdb_id は同じ作品（TVer日本語名 × Netflix英題）としてマージ
    merged: dict[str, dict] = {}
    for s in kept.values():
        tid = s["meta"].get("tmdb_id")
        mkey = f"tmdb:{tid}" if tid else f"raw:{squash(s['title'])}"
        if mkey not in merged:
            merged[mkey] = s
            continue
        m = merged[mkey]
        m["A"] = m["A"] or s["A"]
        m["B"] = m["B"] or s["B"]
        if s["meta"].get("match_confidence") == "ok" and m["meta"].get("match_confidence") != "ok":
            m["meta"], m["title"] = s["meta"], s["title"]

    # 確定した日本語タイトルで Google トレンド
    trends = fetch_trends([s["title"] for s in merged.values()], wk["week"])
    print(f"  Trends: {len(trends)}件")
    for s in merged.values():
        s["C"] = trends.get(s["title"])

    items = finalize_ranking(merged)[:10]
    if not items:
        print("⚠️ ランキング対象0件。data/inputs/ に手動データを置いて再実行してください")
        return 1

    data = assemble_json(wk, items, excluded, tver, netflix, trends)
    (DATA_DIR / f"{wk['week']}.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (DRAFT_DIR / f"{wk['week']}.md").write_text(render_draft(wk, items), encoding="utf-8")
    render_png(wk, items, DRAFT_DIR / f"{wk['week']}.png")

    available = [
        name for name, ok in (("TVer", tver), ("Netflix", netflix), ("Trends", trends)) if ok
    ]
    low = sum(1 for s in items if s["meta"].get("match_confidence") == "low")
    print(f"生成: data/{wk['week']}.json / drafts/{wk['week']}.md")
    print(f"取得できたソース: {', '.join(available) or 'なし'}／ 照合要確認: {low}件")
    if len(available) < 2:
        print("⚠️ 有効ソースが2つ未満です。手動入力（inputs/README.md 参照）で補完を推奨")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
