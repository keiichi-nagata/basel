#!/usr/bin/env python3
"""開発6部 — noteマガジンの表紙画像を生成する（assets/magazine-cover.png）。

使い方: python dev/6-markets/assets/make_cover.py

noteのマガジン表紙は一覧・関連表示で**中央の正方形にトリミングされる**ため、
文字は必ずキャンバス中央の正方形（1280x670なら幅670pxぶん＝x軸で0.24〜0.76）に収める。
バーの装飾も同じ安全域内に収め、キャンバスの左右は余白として残す。
配色は各号のサムネイル（make_eyecatch.py）と揃える。
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.patheffects as pe  # noqa: E402
from matplotlib import font_manager  # noqa: E402

for _name in ("Noto Sans CJK JP", "Noto Sans JP", "IPAexGothic",
              "Meiryo", "Yu Gothic", "MS Gothic", "Hiragino Sans"):
    try:
        if font_manager.findfont(_name, fallback_to_default=False):
            matplotlib.rcParams["font.family"] = _name
            break
    except Exception:  # noqa: BLE001
        continue

BG = "#20242e"
TITLE = "#f3f4f6"
MUTE = "#9aa2ad"
UP = "#38b676"
DOWN = "#e0605f"
BARS = [0.30, 0.55, 0.85, 0.50, 0.95, 0.35, 0.70]
DIRS = [1, 1, 1, -1, 1, -1, 1]

CX = 0.5           # 中央正方形の中心（キャンバス中央と一致）
SAFE_W = 0.50       # 中央正方形の内側にさらに少し余白を取った安全域の幅


def main() -> None:
    W, H = 1280, 670
    fig = plt.figure(figsize=(W / 200, H / 200), dpi=200)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, color=BG))

    # 中央正方形の安全域にだけ棒グラフを置く（装飾）
    x0, y0, w, h = CX - SAFE_W / 2, 0.09, SAFE_W, 0.19
    n = len(BARS)
    for i, (bh, d) in enumerate(zip(BARS, DIRS)):
        x = x0 + i * (w / n)
        ax.add_patch(plt.Rectangle((x, y0), w / (n * 1.5), h * bh,
                                    facecolor=UP if d > 0 else DOWN, edgecolor="none", alpha=0.9))

    ax.add_patch(plt.Rectangle((0, 0), 1, 0.016, color=UP))
    ax.add_patch(plt.Rectangle((CX - 0.035, 0.875), 0.07, 0.013, color=UP))
    ax.text(CX, 0.815, "月刊", fontsize=14, color=UP, fontweight="bold", ha="center", va="center")
    t = ax.text(CX, 0.635, "資産クラス別\n月間リターンランキング", fontsize=18.5, color=TITLE,
                fontweight="bold", ha="center", va="center", linespacing=1.35)
    t.set_path_effects([pe.withStroke(linewidth=1.2, foreground=BG)])
    ax.text(CX, 0.44, "株・金・債券・REIT・原油\nビットコイン。円建てで並べて読む。",
            fontsize=10.5, color=MUTE, ha="center", va="center", linespacing=1.5)

    out = Path(__file__).parent / "magazine-cover.png"
    fig.savefig(out, dpi=200, facecolor=BG)
    plt.close(fig)
    print("saved:", out)


if __name__ == "__main__":
    main()
