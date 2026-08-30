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
ANIMATION_GENRE_ID = 16

# TMDB の provider 名 -> 記事で使うアフィリ区分。提携済み/申請中のみ有効。
AFFILIATE_BY_PROVIDER = {
    "ABEMA": "abema",           # 提携済み
    "Abema TV": "abema",
    "Amazon Prime Video": "amazon",  # もしも/Amazonアソシエイト 承認後に有効
}
# 見放題だけを見る。rent/buy は含めない。
SVOD_KINDS = ("flatrate", "free", "ads")
PROVIDER_NORMALIZE = {
    "Disney Plus": "Disney+",
    "Netflix Standard with Ads": "Netflix",
    "Amazon Prime Video with Ads": "Amazon Prime Video",
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


def fetch_tver(week: str) -> list[dict]:
    """TVer 週間ドラマランキング。

    TVer には公式に開かれたランキングAPIが無い。非公開エンドポイントは仕様変更・
    規約リスクがあるため v1 では自動取得を試みたうえで、失敗時は手動入力
    （data/inputs/<week>.tver.json）へ自動フォールバックする。
    """
    endpoint = os.environ.get("TVER_RANKING_URL", "").strip()
    if endpoint:
        try:
            resp = requests.get(
                endpoint, headers={"User-Agent": USER_AGENT}, timeout=HTTP_TIMEOUT
            )
            resp.raise_for_status()
            payload = resp.json()
            rows = payload if isinstance(payload, list) else payload.get("contents", [])
            result = []
            for i, row in enumerate(rows[:TVER_LIST_LEN_CAP], start=1):
                title = (
                    row.get("title")
                    or row.get("seriesTitle")
                    or (row.get("content") or {}).get("title")
                    or ""
                ).strip()
                if title:
                    result.append({"rank": row.get("rank", i), "title": title})
            if result:
                return result
            print("[tver] エンドポイントから0件。フォールバックへ")
        except Exception as exc:  # noqa: BLE001
            print(f"[tver] 自動取得失敗: {exc}")
    else:
        print("[tver] TVER_RANKING_URL 未設定。手動入力を使用")
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
            name = PROVIDER_NORMALIZE.get(p["provider_name"], p["provider_name"])
            if name not in names:
                names.append(name)
    return names


def enrich_tmdb(title: str, ref_year: int) -> dict:
    info: dict[str, Any] = {
        "tmdb_id": None,
        "matched_title": None,
        "match_confidence": "low",
        "is_anime": False,
        "overview": "",
        "overview_source": "TMDB (要・公式サイトで確認して自分の言葉に書き直す)",
        "season_number": None,
        "episodes_aired": None,
        "episodes_total": None,
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
        info["is_anime"] = ANIMATION_GENRE_ID in genres
        info["overview"] = (detail.get("overview") or "").strip()
        info["episodes_total"] = detail.get("number_of_episodes")
        lea = detail.get("last_episode_to_air") or {}
        info["season_number"] = lea.get("season_number")
        info["episodes_aired"] = lea.get("episode_number")
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
def provider_label(name: str) -> str:
    aff = AFFILIATE_BY_PROVIDER.get(name, "none")
    if aff == "abema":
        return f"{name} [PR]（★ABEMAアフィリリンクを差し込む）"
    if aff == "amazon":
        return f"{name} [PR]（★もしも/Amazonアソシエイト承認後にリンク）"
    return name


def episode_text(meta: dict) -> str:
    ep = meta.get("episodes_aired")
    return f"第{ep}話まで" if ep else "【話数要確認】"


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
                    "needs_check": meta.get("needs_check", True),
                },
                "overview": meta.get("overview", ""),
                "providers_jp": [
                    {"name": n, "affiliate": AFFILIATE_BY_PROVIDER.get(n, "none")}
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
        "excluded_anime": [{"title": e["title"], "matched": e["meta"].get("matched_title")}
                           for e in excluded],
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
        "対象は民放ドラマ＋配信ドラマ（NHK作品・アニメは指標の性質上ランク外）。"
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
        "TVer・Netflixのいずれにも入らない作品、およびアニメは対象外です。配信状況は "
        "TMDB / JustWatch のデータを利用しています（TMDBの公認を受けたものではありません）。"
    )
    L.append("")
    L.append("## 次回")
    L.append("")
    L.append("来週〔曜日〕更新。マガジンのフォローで通知が届きます。")
    L.append("（開発1部の有料noteへの1行導線）")
    L.append("")
    return "\n".join(L)


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
        if meta.get("is_anime"):
            print(f"  除外(アニメ): {s['source_title']} -> {matched}")
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
