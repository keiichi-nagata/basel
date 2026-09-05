#!/usr/bin/env python3
"""開発4部 — 月次ランキング表の画像化。

`dev/4-onsen/data/YYYY-MM.json` を読み、note/SNSにそのまま貼れる
ランキング表PNGを `dev/4-onsen/drafts/YYYY-MM.png` に書き出す。
開発3部（`dev/3-drama/pipeline/collect.py` の render_png）と同じ方式。

使い方:
  python dev/4-onsen/assets/make_ranking_table.py 2026-09
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ONSEN_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ONSEN_DIR / "data"
DRAFT_DIR = ONSEN_DIR / "drafts"


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


def render_png(data: dict, out_path: Path) -> bool:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        font = _jp_font()
        if font:
            matplotlib.rcParams["font.family"] = font
        else:
            print("[png] 日本語フォントが見つからず文字化けの可能性（fonts-noto-cjk を導入）")

        headers = ["順位", "宿名", "エリア", "独自採点", "楽天トラベル", "じゃらん"]
        rows = []
        for it in data["items"]:
            rows.append([
                str(it["rank"]),
                it["name"],
                it.get("location", ""),
                f"{it['score']:.1f}",
                f"{it['rakuten']['score']:.2f}（{it['rakuten']['review_count']:,}件）",
                f"{it['jalan']['score']:.2f}（{it['jalan']['review_count']:,}件）",
            ])

        y, m = data["month"].split("-")
        fig, ax = plt.subplots(figsize=(10.5, 1.3 + 0.6 * len(rows)))
        ax.axis("off")
        ax.set_title(f"【{y}年{int(m)}月】{data['area']}温泉 宿ランキングTOP5",
                     fontsize=15, fontweight="bold", pad=18, loc="left")
        tbl = ax.table(cellText=rows, colLabels=headers, loc="center", cellLoc="center")
        tbl.auto_set_font_size(False)
        tbl.set_fontsize(11)
        tbl.scale(1, 1.7)
        widths = [0.06, 0.30, 0.14, 0.1, 0.20, 0.20]
        for (r, col), cell in tbl.get_celld().items():
            cell.set_width(widths[col])
            cell.set_edgecolor("#d0d0d0")
            if r == 0:
                cell.set_facecolor("#2b6b5e")
                cell.set_text_props(color="white", fontweight="bold")
            else:
                if col == 1:
                    cell.set_text_props(ha="left")
                    cell.PAD = 0.03
                cell.set_facecolor("#ffffff" if r % 2 else "#f2f7f5")
        fig.text(0.5, 0.02,
                 "独自採点＝楽天トラベル・じゃらんの宿泊者評価（各5点満点）の単純平均。実際の宿泊体験ではありません。",
                 ha="center", fontsize=8, color="#888888")
        fig.savefig(out_path, dpi=200, bbox_inches="tight", facecolor="white")
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
    data_path = DATA_DIR / f"{month}.json"
    if not data_path.exists():
        print(f"データが見つかりません: {data_path}")
        return 1
    data = json.loads(data_path.read_text(encoding="utf-8"))
    DRAFT_DIR.mkdir(parents=True, exist_ok=True)
    ok = render_png(data, DRAFT_DIR / f"{month}.png")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
