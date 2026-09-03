#!/usr/bin/env python3
"""開発2部 — 月次「新車販売台数ランキングTOP5」のデータ組み立て。

自販連（登録車）・全軽自協（軽）の車名別データは月次PDF（URL不定）のため自動取得しない。
手動で貼った  dev/2-cars/data/inputs/YYYY-MM.json  を読み、

  - 登録車＋軽を1リストにして台数降順 → 総合TOP5
  - dev/2-cars/prices.json の最安価格を結合（無ければ【価格要確認】）
  - 前月の data/YYYY-MM.json と突き合わせて順位変動・新規ランクインを算出
  - dev/2-cars/data/YYYY-MM.json（構造データ）と drafts/YYYY-MM.md（template準拠の下書き）を生成

使い方:
  python dev/2-cars/pipeline/collect.py            # 前月を対象（毎月8日ごろ想定）
  python dev/2-cars/pipeline/collect.py 2026-08    # 対象月を明示
"""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

CARS_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = CARS_DIR / "data"
INPUT_DIR = DATA_DIR / "inputs"
DRAFT_DIR = CARS_DIR / "drafts"
PRICES_PATH = CARS_DIR / "prices.json"


def target_month(arg: str | None) -> str:
    if arg:
        return arg
    t = date.today()
    y, m = (t.year, t.month - 1) if t.month > 1 else (t.year - 1, 12)
    return f"{y:04d}-{m:02d}"


def load_prices() -> dict:
    try:
        raw = json.loads(PRICES_PATH.read_text(encoding="utf-8"))
        return {k: v for k, v in raw.items() if not k.startswith("_")}
    except Exception:  # noqa: BLE001
        return {}


def yen_to_man(yen: int | None) -> str:
    if not yen:
        return "【価格要確認】"
    return f"{yen / 10000:.1f}万円〜"


def yoy_str(pct: float | None) -> str:
    if pct is None:
        return "—"
    if pct >= 0:
        return f"+{pct:.1f}%"
    return f"▲{abs(pct):.1f}%"


def prev_month(month: str) -> str:
    y, m = map(int, month.split("-"))
    y, m = (y, m - 1) if m > 1 else (y - 1, 12)
    return f"{y:04d}-{m:02d}"


def build(month: str) -> dict:
    src_path = INPUT_DIR / f"{month}.json"
    if not src_path.exists():
        print(f"⚠️ 入力がありません: {src_path.relative_to(CARS_DIR.parent.parent)}")
        print("   inputs/README.md の形で登録車・軽の車名別データを貼ってください。")
        raise SystemExit(1)
    src = json.loads(src_path.read_text(encoding="utf-8"))

    rows = []
    for seg, label in (("registered", "登録車"), ("kei", "軽")):
        for r in src.get(seg, []):
            rows.append({
                "model": r["model"].strip(),
                "maker": r.get("maker", "").strip(),
                "units": int(r["units"]),
                "yoy_pct": r.get("yoy_pct"),
                "segment": label,
            })
    rows.sort(key=lambda x: x["units"], reverse=True)
    top5 = rows[:5]

    prices = load_prices()
    for i, r in enumerate(top5, start=1):
        r["rank"] = i
        p = prices.get(r["model"], {})
        r["price_from_yen"] = p.get("from")
        r["price_as_of"] = p.get("as_of")
        r["price_source"] = p.get("source")

    # 前月比
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

    missing_price = [r["model"] for r in top5 if not r["price_from_yen"]]
    return {
        "month": month,
        "collected_at": date.today().isoformat(),
        "sources": {
            "registered": src.get("source_registered", {}),
            "kei": src.get("source_kei", {}),
            "prices": "dev/2-cars/prices.json",
        },
        "price_needs_check": missing_price,
        "items": top5,
    }


def render_draft(data: dict) -> str:
    y, m = data["month"].split("-")
    L: list[str] = []
    L.append(f"# 【{y}年{int(m)}月】新車販売台数ランキングTOP5から見える、〔その月のテーマ1フレーズ〕")
    L.append("")
    L.append("〔導入：今月のデータである旨。2回目以降は前月からの変化に軽く触れる〕")
    changes = [f"{r['model']}（前月{r['prev_rank']}位→{r['rank']}位）"
               for r in data["items"]
               if isinstance(r.get("rank_change"), int) and r["rank_change"] != 0]
    newcomers = [r["model"] for r in data["items"] if r.get("rank_change") == "NEW"]
    if changes:
        L.append(f"（順位変動メモ: {', '.join(changes)}）")
    if newcomers:
        L.append(f"（新規ランクイン: {', '.join(newcomers)}）")
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
    print("TOP5: " + " / ".join(f"{r['rank']}.{r['model']}" for r in data["items"]))
    if data["price_needs_check"]:
        print(f"⚠️ 価格未登録: {', '.join(data['price_needs_check'])} → prices.json に追記")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
