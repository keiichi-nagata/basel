#!/usr/bin/env python3
"""開発2部 — 月次「新車販売台数ランキングTOP5」のデータ組み立て。

台数データの取得:
  1. 自販連「ブランド通称名別ランキング」ページ → 年度累計XLSX（登録車・軽/輸入を除く）
  2. 全軽自協「軽四輪車新車販売確報」一覧 → 対象月ページ → Excel（軽の通称名別）
  どちらもエクセルを openpyxl で解析。取得/解析に失敗したら
  dev/2-cars/data/inputs/YYYY-MM.json（手動貼付）へフォールバックする。

そのあと:
  - 登録車＋軽を台数降順にして総合TOP5
  - dev/2-cars/prices.json の最安価格を結合（無ければ【価格要確認】）
  - 前月の data/YYYY-MM.json と突き合わせて順位変動・新規ランクインを算出
  - dev/2-cars/data/YYYY-MM.json と drafts/YYYY-MM.md（template準拠・分析欄は空）を生成

使い方:
  python dev/2-cars/pipeline/collect.py            # 前月を対象（毎月8日ごろ想定）
  python dev/2-cars/pipeline/collect.py 2026-08
"""
from __future__ import annotations

import io
import json
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urljoin

try:  # Windows コンソールの文字化け対策
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # noqa: BLE001
    pass

CARS_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = CARS_DIR / "data"
INPUT_DIR = DATA_DIR / "inputs"
RAW_DIR = DATA_DIR / "raw"
DRAFT_DIR = CARS_DIR / "drafts"
PRICES_PATH = CARS_DIR / "prices.json"

JADA_PAGE = "https://www.jada.or.jp/pages/340/"
JLMA_TUSHO = "https://www.zenkeijikyo.or.jp/statistics/tushosoku"  # 軽 通称名別 新車販売速報（最新月）
# 過去月フォールバック用の .xls（tushosoku4-YYMM.xls、公開は対象月の翌月フォルダ）
JLMA_XLS_TMPL = "https://www.zenkeijikyo.or.jp/zenkei17/zen/wp-content/uploads/{py}/{pm:02d}/tushosoku4-{yy}{mm}.xls"


def _zen2han(s: str) -> str:
    """全角英数字・記号を半角に（例: Ｎ-ＢＯＸ → N-BOX）。"""
    return s.translate({c: c - 0xFEE0 for c in range(0xFF01, 0xFF5F)}).replace("−", "-")
UA = {"User-Agent": "basel-cars/1.0 (+https://github.com/keiichi-nagata/basel)"}
HTTP_TIMEOUT = 40


# --------------------------------------------------------------------------- utils
def target_month(arg: str | None) -> str:
    if arg:
        return arg
    t = date.today()
    y, m = (t.year, t.month - 1) if t.month > 1 else (t.year - 1, 12)
    return f"{y:04d}-{m:02d}"


def prev_month(month: str) -> str:
    y, m = map(int, month.split("-"))
    y, m = (y, m - 1) if m > 1 else (y - 1, 12)
    return f"{y:04d}-{m:02d}"


def load_prices() -> dict:
    try:
        raw = json.loads(PRICES_PATH.read_text(encoding="utf-8"))
        return {k: v for k, v in raw.items() if not k.startswith("_")}
    except Exception:  # noqa: BLE001
        return {}


def yen_to_man(yen: int | None) -> str:
    return f"{yen / 10000:.1f}万円〜" if yen else "【価格要確認】"


def yoy_str(pct: float | None) -> str:
    if pct is None:
        return "—"
    return f"+{pct:.1f}%" if pct >= 0 else f"▲{abs(pct):.1f}%"


# ----------------------------------------------------------------- Excel 取得・解析
def _http_get(url: str) -> bytes:
    import requests
    r = requests.get(url, headers=UA, timeout=HTTP_TIMEOUT)
    r.raise_for_status()
    return r.content


def _save_raw(name: str, data: bytes) -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    (RAW_DIR / name).write_bytes(data)


def _workbook_rows(xbytes: bytes) -> list[tuple[str, list[list]]]:
    """xlsx/xls どちらでも [(シート名, 行の2次元リスト), ...] を返す。"""
    if xbytes[:2] == b"PK":  # xlsx (zip)
        import openpyxl
        wb = openpyxl.load_workbook(io.BytesIO(xbytes), data_only=True)
        return [(ws.title, [list(r) for r in ws.iter_rows(values_only=True)])
                for ws in wb.worksheets]
    if xbytes[:4] == b"\xd0\xcf\x11\xe0":  # 旧 xls (OLE2)
        import xlrd
        wb = xlrd.open_workbook(file_contents=xbytes)
        out = []
        for sh in wb.sheets():
            out.append((sh.name,
                        [[sh.cell_value(r, c) for c in range(sh.ncols)]
                         for r in range(sh.nrows)]))
        return out
    raise ValueError("未知のExcel形式（xlsx/xls いずれでもない）")


def _dump_structure(name: str, xbytes: bytes) -> None:
    """解析がうまくいかないとき用に、シート名と先頭行をテキストで残す。"""
    try:
        lines = []
        for title, rows in _workbook_rows(xbytes):
            lines.append(f"=== sheet: {title} ===")
            for i, row in enumerate(rows[:35]):
                lines.append(f"{i:2d} | " + " | ".join("" if c is None else str(c) for c in row))
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        (RAW_DIR / name).write_text("\n".join(lines), encoding="utf-8")
        print(f"[構造ダンプ] {RAW_DIR / name}")
    except Exception as exc:  # noqa: BLE001
        print(f"[構造ダンプ失敗] {exc}")


_NAME_KEYS = ("通称名", "車名", "名称")
_UNIT_KEYS = ("当月", "本月", "台数")
_YOY_KEYS = ("前年対比", "前年同月比", "前年比")
_MAKER_KEYS = ("メーカー", "ブランド名", "銘柄", "会社名")


def _parse_ranking_xlsx(xbytes: bytes, is_index_yoy: bool = True) -> list[dict]:
    """通称名別ランキングの表を含むシートを探し、行を取り出す（xlsx/xls 両対応）。

    ヘッダー行（通称名 と 台数/当月 を含む行）を検出し、列名でマッピングする。
    前年対比は「前年＝100 の指数」で入っていることが多い → is_index_yoy なら -100 する。
    """
    for _title, raw_rows in _workbook_rows(xbytes):
        rows = [[("" if c is None else c) for c in r] for r in raw_rows]

        def norm(c: object) -> str:
            return str(c).replace(" ", "").replace("　", "").strip()

        hdr_i = header = None
        for i, r in enumerate(rows[:40]):
            cells = [norm(c) for c in r]
            has_name = any(any(k in c for k in _NAME_KEYS) for c in cells)
            has_unit = any(any(k in c for k in _UNIT_KEYS) for c in cells)
            if has_name and has_unit:
                hdr_i, header = i, cells
                break
        if hdr_i is None:
            continue

        def col_of(keys: tuple[str, ...]) -> int | None:
            for j, c in enumerate(header):
                if any(k in c for k in keys):
                    return j
            return None

        name_c = col_of(_NAME_KEYS)
        unit_c = col_of(_UNIT_KEYS)
        yoy_c = col_of(_YOY_KEYS)
        maker_c = col_of(_MAKER_KEYS)
        if name_c is None or unit_c is None:
            continue

        out: list[dict] = []
        blanks = 0
        for r in rows[hdr_i + 1:]:
            name = str(r[name_c]).strip() if name_c < len(r) else ""
            if not name or name in ("合計", "計", "総計", "その他"):
                blanks += 1
                if blanks >= 5 and out:
                    break
                continue
            blanks = 0
            try:
                units = int(float(str(r[unit_c]).replace(",", "")))
            except (ValueError, TypeError):
                continue
            yoy = None
            if yoy_c is not None and yoy_c < len(r) and str(r[yoy_c]).strip():
                try:
                    v = float(str(r[yoy_c]).replace(",", "").replace("%", ""))
                    yoy = round(v - 100, 1) if is_index_yoy else round(v, 1)
                except ValueError:
                    pass
            maker = ""
            if maker_c is not None and maker_c < len(r):
                maker = str(r[maker_c]).strip()
            out.append({"model": name, "maker": maker, "units": units, "yoy_pct": yoy})
        if out:
            return out[:20]
    return []


def _pick_href(html: str, want_ext: tuple[str, ...], *needles: str) -> str | None:
    """html 内の href のうち、拡張子が合致し、周辺テキストに needles を全て含むものを返す。"""
    for m in re.finditer(r'href="([^"]+)"', html):
        href = m.group(1)
        if not href.lower().split("?")[0].endswith(want_ext):
            continue
        ctx = html[max(0, m.start() - 400): m.end() + 400]
        if all(n in ctx for n in needles):
            return href
    return None


def fetch_jada(month: str) -> list[dict]:
    """自販連 pages/340 の『ブランド通称名別ランキング』年度累計XLSXを取得・解析。"""
    year = month.split("-")[0]
    try:
        html = _http_get(JADA_PAGE).decode("utf-8", "replace")
        href = (_pick_href(html, (".xlsx", ".xls"), "通称名別", f"{year}年")
                or _pick_href(html, (".xlsx", ".xls"), "通称名別"))
        if not href:
            print("[jada] 通称名別ランキングのExcelリンクが見つからない")
            return []
        xbytes = _http_get(urljoin(JADA_PAGE, href))
        _save_raw(f"jada_{month}.xlsx", xbytes)
        rows = _parse_ranking_xlsx(xbytes, is_index_yoy=True)
        if not rows:
            _dump_structure(f"jada_{month}_structure.txt", xbytes)
            print("[jada] 解析0件。構造ダンプ（data/raw/）を確認 → 列の探し方を調整")
        else:
            print(f"[jada] {len(rows)}件 取得（{href}）")
        return rows
    except Exception as exc:  # noqa: BLE001
        print(f"[jada] 取得失敗: {exc}")
        return []


_JLMA_STOP = {"合計", "計", "総計", "その他", "通称名", "メーカー", "本月", "車種", "車名"}


def _to_int(s: str) -> int | None:
    try:
        return int(float(str(s).replace(",", "").strip()))
    except (ValueError, TypeError):
        return None


def _parse_jlma_html(html: str) -> list[dict]:
    """tushosoku ページの通称名別テーブルを解析。

    行の並びは概ね [ラベル/順位, メーカー, 通称名, 本月, 前月, 前月比, 前年同月, 前年同月比, …]
    だが、メーカーが rowspan で省かれ [通称名, 本月, …] になる行もある。
    → 「非数値のセル mi で、mi+1 が整数、mi+5 が指数(前年同月比)」を通称名行とみなす。
    前年同月比は前年＝100 の指数なので -100 する。
    """
    seen: dict[str, dict] = {}
    for tbl in re.findall(r"<table[^>]*>(.*?)</table>", html, re.S):
        if "通称名" not in tbl:
            continue
        for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", tbl, re.S):
            cells = [re.sub(r"<[^>]+>", "", c).strip()
                     for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S)]
            if len(cells) < 6:
                continue
            for mi in range(len(cells) - 5):
                name = _zen2han(cells[mi]).strip()
                if not name or _to_int(cells[mi]) is not None or name in _JLMA_STOP:
                    continue
                units = _to_int(cells[mi + 1])
                if units is None or units < 10:
                    continue
                yoy = None
                try:
                    v = float(str(cells[mi + 5]).replace(",", ""))
                    if 0 < v < 2000:
                        yoy = round(v - 100, 1)
                except ValueError:
                    pass
                maker = _zen2han(cells[mi - 1]).strip() if mi >= 1 and _to_int(cells[mi - 1]) is None else ""
                prev = seen.get(name)
                if prev is None or units > prev["units"]:
                    seen[name] = {"model": name, "maker": maker,
                                  "units": units, "yoy_pct": yoy}
                break
    return sorted(seen.values(), key=lambda x: x["units"], reverse=True)[:20]


def fetch_jlma(month: str) -> list[dict]:
    """全軽自協『軽四輪車 通称名別 新車販売速報』（tushosoku）から取得。

    tushosoku ページは最新月のみ。対象月＝最新月なら HTMLテーブルを解析、
    そうでなければ tushosoku4-YYMM.xls を直URLで取得して解析する。
    """
    y, mo = month.split("-")
    mo_i, yy = int(mo), y[2:]
    try:
        html = _http_get(JLMA_TUSHO).decode("utf-8", "replace")
        h1 = " ".join(re.sub(r"<[^>]+>", "", m) for m in re.findall(r"<h1[^>]*>(.*?)</h1>", html, re.S))
        if f"{y}年{mo_i}月" in h1 or f"{y}年{mo:0>2}月" in h1:
            rows = _parse_jlma_html(html)
            if rows:
                print(f"[jlma] {len(rows)}件 取得（{JLMA_TUSHO} HTML）")
                return rows
            _save_raw(f"jlma_{month}.html", html.encode("utf-8"))
            print("[jlma] HTMLテーブル解析0件。data/raw/ のHTMLを確認")
        else:
            print(f"[jlma] tushosoku は現在『{h1.strip()[:40]}』。対象月と違うため .xls を試行")

        py, pm = (int(y), mo_i + 1) if mo_i < 12 else (int(y) + 1, 1)
        xurl = JLMA_XLS_TMPL.format(py=py, pm=pm, yy=yy, mm=mo)
        xbytes = _http_get(xurl)
        _save_raw(f"jlma_{month}.xls", xbytes)
        rows = _parse_ranking_xlsx(xbytes, is_index_yoy=True)
        if rows:
            print(f"[jlma] {len(rows)}件 取得（{xurl}）")
        else:
            _dump_structure(f"jlma_{month}_structure.txt", xbytes)
            print("[jlma] .xls 解析0件。構造ダンプ（data/raw/）を確認")
        return rows
    except Exception as exc:  # noqa: BLE001
        print(f"[jlma] 取得失敗: {exc}")
        return []


def load_manual(month: str) -> dict | None:
    p = INPUT_DIR / f"{month}.json"
    if p.exists():
        print(f"[manual] 手動入力を使用: {p.relative_to(CARS_DIR.parent.parent)}")
        return json.loads(p.read_text(encoding="utf-8"))
    return None


# --------------------------------------------------------------------------- build
def build(month: str) -> dict:
    registered = fetch_jada(month)
    kei = fetch_jlma(month)
    src_meta = {"registered": {"url": JADA_PAGE}, "kei": {"url": JLMA_TUSHO}}

    if not registered or not kei:
        manual = load_manual(month)
        if manual:
            registered = registered or manual.get("registered", [])
            kei = kei or manual.get("kei", [])
            src_meta["registered"] = manual.get("source_registered", src_meta["registered"])
            src_meta["kei"] = manual.get("source_kei", src_meta["kei"])

    if not registered and not kei:
        print(f"⚠️ 台数データが取れませんでした。data/inputs/{month}.json に貼って再実行してください。")
        raise SystemExit(1)
    if not registered or not kei:
        print("⚠️ 片方のソースが空です（登録車 or 軽）。inputs で補完すると総合順位が正確になります。")

    rows = []
    for seg, label in ((registered, "登録車"), (kei, "軽")):
        for r in seg:
            rows.append({"model": r["model"].strip(), "maker": r.get("maker", "").strip(),
                         "units": int(r["units"]), "yoy_pct": r.get("yoy_pct"), "segment": label})
    rows.sort(key=lambda x: x["units"], reverse=True)
    top5 = rows[:5]

    prices = load_prices()
    for i, r in enumerate(top5, start=1):
        r["rank"] = i
        p = prices.get(r["model"], {})
        r["price_from_yen"] = p.get("from")
        r["price_as_of"] = p.get("as_of")
        r["price_source"] = p.get("source")

    prev_path = DATA_DIR / f"{prev_month(month)}.json"
    prev_ranks = {}
    if prev_path.exists():
        prev = json.loads(prev_path.read_text(encoding="utf-8"))
        prev_ranks = {it["model"]: it["rank"] for it in prev.get("items", [])}
    for r in top5:
        pr = prev_ranks.get(r["model"])
        r["prev_rank"] = pr
        r["rank_change"] = ("NEW" if pr is None and prev_ranks
                            else (None if pr is None else pr - r["rank"]))

    return {
        "month": month,
        "collected_at": date.today().isoformat(),
        "sources": {**src_meta, "prices": "dev/2-cars/prices.json"},
        "price_needs_check": [r["model"] for r in top5 if not r["price_from_yen"]],
        "items": top5,
    }


def render_draft(data: dict) -> str:
    y, m = data["month"].split("-")
    L: list[str] = []
    L.append(f"# 【{y}年{int(m)}月】新車販売台数ランキングTOP5から見える、〔その月のテーマ1フレーズ〕")
    L.append("")
    L.append("〔導入：今月のデータである旨。2回目以降は前月からの変化に軽く触れる〕")
    ch = [f"{r['model']}（前月{r['prev_rank']}位→{r['rank']}位）" for r in data["items"]
          if isinstance(r.get("rank_change"), int) and r["rank_change"] != 0]
    nc = [r["model"] for r in data["items"] if r.get("rank_change") == "NEW"]
    if ch:
        L.append(f"（順位変動メモ: {', '.join(ch)}）")
    if nc:
        L.append(f"（新規ランクイン: {', '.join(nc)}）")
    L.append("")
    L.append(f"## {y}年{int(m)}月 新車販売台数TOP5（登録車＋軽自動車 総合）")
    L.append("")
    L.append("| 順位 | 車種 | メーカー | 販売台数 | 前年同月比 | 新車価格（下限） |")
    L.append("|---|---|---|---|---|---|")
    for r in data["items"]:
        L.append(f"| {r['rank']} | {r['model']} | {r['maker']} | {r['units']:,}台 "
                 f"| {yoy_str(r['yoy_pct'])} | {yen_to_man(r['price_from_yen'])} |")
    L.append("")
    as_of = next((r["price_as_of"] for r in data["items"] if r.get("price_as_of")), "YYYY-MM")
    L.append("※台数は自販連・全軽自協発表の統計をもとに集計。価格は各車の最も安いグレードの"
             "車両本体価格（税込・メーカー希望小売価格）の目安で、時期やグレード改定により変動します。"
             f"（価格取得時点: {as_of}）")
    if data["price_needs_check"]:
        L.append("")
        L.append(f"> ⚠️ 価格未登録: {', '.join(data['price_needs_check'])} "
                 "→ メーカー公式で確認して `dev/2-cars/prices.json` に追記")
    L.append("")
    L.append("## 各車の特徴と「なぜ売れているか」")
    L.append("")
    L.append("【car-column-writer 記入】5台それぞれ2〜4文。1位はやや厚めに。"
             "一部改良・モデルチェンジ・補助金など今月の要因を WebSearch で確認。裏が取れないことは【要確認】")
    for r in data["items"]:
        L.append("")
        L.append(f"**{r['rank']}位 {r['model']}（{r['maker']}）**")
        L.append("（記入）")
    L.append("")
    L.append("## この5台に共通する構造")
    L.append("")
    L.append("【car-column-writer 記入】TOP5を俯瞰して一段抽象化（価格帯・サイズ・装備・購買層など、その月のパターン）")
    L.append("")
    L.append("## 働き方・投資への示唆")
    L.append("")
    L.append("【car-column-writer 記入】上の抽象化を、フリーランスの働き方／投資判断に接続。必須:")
    L.append("- 働き方の「地味な改善」の具体例を1つ（仕事術など・抽象論で終わらせない）")
    L.append("- 投資は「積立投資」「複利」など行動に移しやすいキーワードと結びつける")
    L.append("- 段落の最後に読者への問いかけ1行 ＋ 小さな行動を促す一言で締める")
    L.append("")
    L.append("---")
    L.append("このシリーズは毎月更新予定です。次回もぜひ読みにきてください。")
    L.append("")
    L.append("より踏み込んだ分析（個別モデルの戦略分析や投資的な視点）は有料note側でも発信しています。")
    L.append("")
    L.append("〔アフィリンクを入れる号は冒頭に広告表記（`sop/disclosure.md`）。相性の良い案件を1〜2個まで〕")
    L.append("")
    return "\n".join(L)


def main() -> int:
    for d in (DATA_DIR, INPUT_DIR, DRAFT_DIR):
        d.mkdir(parents=True, exist_ok=True)
    month = target_month(sys.argv[1] if len(sys.argv) > 1 else None)
    print(f"対象月: {month}")
    data = build(month)
    (DATA_DIR / f"{month}.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    (DRAFT_DIR / f"{month}.md").write_text(render_draft(data), encoding="utf-8")
    print(f"生成: data/{month}.json / drafts/{month}.md")
    print("TOP5: " + " / ".join(
        f"{r['rank']}.{r['model']}({r['units']:,},{yoy_str(r['yoy_pct'])})" for r in data["items"]))
    if data["price_needs_check"]:
        print(f"⚠️ 価格未登録: {', '.join(data['price_needs_check'])} → prices.json に追記")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
