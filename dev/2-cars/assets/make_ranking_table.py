#!/usr/bin/env python3
"""開発2部 — 月次「新車販売台数ランキングTOP5」の表を画像化。

`dev/2-cars/data/YYYY-MM.json` を読み、note/SNSにそのまま貼れる表PNGを
`dev/2-cars/drafts/YYYY-MM.png` に書き出す（noteでMarkdown表が崩れるため）。
開発3部・4部の表画像と同じ方式。

使い方:
  python dev/2-cars/pipeline/../assets/make_ranking_table.py 2026-08
  （= python dev/2-cars/assets/make_ranking_table.py 2026-08）
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

CARS_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = CARS_DIR / "data"
DRAFT_DIR = CARS_DIR / "drafts"

BG = "#f4f2ec"
HEADER = "#26364a"       # 濃紺（クルマ＋分析の落ち着き）
ACCENT = "#c8781e"       # アンバー
ROW_ALT = "#eae7de"


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


def _yoy(pct) -> str:
    if pct is None:
        return "—"
    return f"+{pct:.1f}%" if pct >= 0 else f"▲{abs(pct):.1f}%"


def _man(yen) -> str:
    return f"{yen / 10000:.1f}万円〜" if yen else "—"


def render(data: dict, out_path: Path) -> bool:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        font = _jp_font()
        if font:
            matplotlib.rcParams["font.family"] = font
        else:
            print("[png] 日本語フォントが見つからず文字化けの可能性（fonts-noto-cjk を導入）")

        y, m = data["month"].split("-")
        headers = ["順位", "車種", "メーカー", "販売台数", "前年同月比", "新車価格"]
        rows = []
        for it in data["items"]:
            tag = ""
            if it.get("rank_change") == "NEW":
                tag = "  NEW"
            rows.append([
                str(it["rank"]),
                it["model"] + tag,
                it.get("maker", ""),
                f"{it['units']:,}台",
                _yoy(it.get("yoy_pct")),
                _man(it.get("price_from_yen")),
            ])

        fig, ax = plt.subplots(figsize=(10.0, 1.4 + 0.62 * len(rows)))
        ax.axis("off")
        ax.set_title(f"【{y}年{int(m)}月】新車販売台数ランキング TOP5（登録車＋軽 総合）",
                     fontsize=15, fontweight="bold", pad=18, loc="left", color=HEADER)
        tbl = ax.table(cellText=rows, colLabels=headers, loc="center", cellLoc="center")
        tbl.auto_set_font_size(False)
        tbl.set_fontsize(11.5)
        tbl.scale(1, 1.75)
        widths = [0.08, 0.24, 0.14, 0.18, 0.18, 0.18]
        for (r, col), cell in tbl.get_celld().items():
            cell.set_width(widths[col])
            cell.set_edgecolor("#cfcabb")
            if r == 0:
                cell.set_facecolor(HEADER)
                cell.set_text_props(color="white", fontweight="bold")
            else:
                if col == 1:
                    cell.set_text_props(ha="left")
                    cell.PAD = 0.03
                cell.set_facecolor("#ffffff" if r % 2 else ROW_ALT)
        fig.text(0.5, 0.02,
                 "台数は自販連・全軽自協発表の統計をもとに集計。価格は最安グレードの車両本体価格（税込）の目安。",
                 ha="center", fontsize=8, color="#8a8578")
        fig.savefig(out_path, dpi=200, bbox_inches="tight", facecolor=BG)
        plt.close(fig)
        print(f"生成: {out_path}")
        return True
    except Exception as exc:  # noqa: BLE001
        print(f"[png] 生成失敗: {exc}")
        return False


def main() -> int:
    if len(sys.argv) < 2:
        print("使い方: python make_ranking_table.py YYYY-MM")
        return 1
    month = sys.argv[1]
    p = DATA_DIR / f"{month}.json"
    if not p.exists():
        print(f"データが見つかりません: {p}")
        return 1
    data = json.loads(p.read_text(encoding="utf-8"))
    DRAFT_DIR.mkdir(parents=True, exist_ok=True)
    ok = render(data, DRAFT_DIR / f"{month}.png")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
