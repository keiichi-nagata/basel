#!/usr/bin/env python3
"""開発6部 — 資産クラス別 月間リターンランキングの表を画像化。

`dev/6-markets/data/YYYY-MM.json` を読み、note/SNSに貼れる表PNGを
`dev/6-markets/drafts/YYYY-MM.png` に書き出す（noteでMarkdown表が崩れるため）。
開発2・3・4部の表画像と同じ方式。

使い方:
  python dev/6-markets/assets/make_ranking_table.py 2026-08
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
DATA_DIR = BASE / "data"
DRAFT_DIR = BASE / "drafts"

BG = "#eef0f3"           # クールなライトグレー（マーケット/データ）
HEADER = "#2b2f3a"       # グラファイト
ROW_ALT = "#e3e6ea"
UP = "#1f7a54"           # 上昇（緑）
DOWN = "#b23b3b"         # 下落（赤）


def _jp_font() -> str | None:
    from matplotlib import font_manager

    for name in ("Yu Gothic", "Meiryo", "MS Gothic", "IPAexGothic", "IPAGothic",
                 "TakaoPGothic", "Hiragino Sans", "Noto Sans CJK JP", "Noto Sans JP"):
        try:
            if font_manager.findfont(name, fallback_to_default=False):
                return name
        except Exception:  # noqa: BLE001
            continue
    return None


def _pct(v) -> str:
    if v is None:
        return "—"
    return f"+{v:.2f}%" if v >= 0 else f"▲{abs(v):.2f}%"


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
        headers = ["順位", "資産クラス", "連動指数（円建て）", "月間リターン", "年初来"]
        rows, ret_vals = [], []
        for it in data["items"]:
            rows.append([
                str(it.get("rank", "—")),
                it["name"],
                it["tracks"],
                _pct(it.get("month_return_pct")),
                _pct(it.get("ytd_return_pct")),
            ])
            ret_vals.append(it.get("month_return_pct"))

        fig, ax = plt.subplots(figsize=(11.2, 1.5 + 0.6 * len(rows)))
        ax.axis("off")
        ax.set_title(f"【{y}年{int(m)}月】資産クラス別 月間リターンランキング（円建て）",
                     fontsize=15, fontweight="bold", pad=18, loc="left", color=HEADER)
        tbl = ax.table(cellText=rows, colLabels=headers, loc="center", cellLoc="center")
        tbl.auto_set_font_size(False)
        tbl.set_fontsize(10.5)
        tbl.scale(1, 1.75)
        widths = [0.055, 0.17, 0.40, 0.165, 0.165]
        for (r, col), cell in tbl.get_celld().items():
            cell.set_width(widths[col])
            cell.set_edgecolor("#c9ced6")
            if r == 0:
                cell.set_facecolor(HEADER)
                cell.set_text_props(color="white", fontweight="bold")
                continue
            cell.set_facecolor("#ffffff" if r % 2 else ROW_ALT)
            if col in (1, 2):
                cell.set_text_props(ha="left")
                cell.PAD = 0.03
            if col in (3, 4):
                v = ret_vals[r - 1] if col == 3 else data["items"][r - 1].get("ytd_return_pct")
                if v is not None:
                    cell.set_text_props(color=UP if v >= 0 else DOWN, fontweight="bold")
        fig.text(0.5, 0.02,
                 "各資産クラスを代表する東京市場上場の円建てETF等の月末終値から算出（為替換算なし・分配金は含まない）。"
                 "過去の実績であり将来の成果を示すものではありません。",
                 ha="center", fontsize=7.5, color="#8a8f98")
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
