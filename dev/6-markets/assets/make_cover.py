#!/usr/bin/env python3
"""開発6部 — noteマガジンの表紙画像を生成する（assets/magazine-cover.png）。

使い方: python dev/6-markets/assets/make_cover.py
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
BARS = [0.30, 0.52, 0.70, 0.95, 0.44, 0.80, 0.22, 0.60, 0.38, 0.88]
DIRS = [1, 1, 1, 1, -1, 1, -1, 1, -1, 1]


def main() -> None:
    W, H = 1280, 670
    fig = plt.figure(figsize=(W / 200, H / 200), dpi=200)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, color=BG))

    x0, y0, w, h = 0.09, 0.055, 0.82, 0.20
    n = len(BARS)
    for i, (bh, d) in enumerate(zip(BARS, DIRS)):
        x = x0 + i * (w / n)
        ax.add_patch(plt.Rectangle((x, y0), w / (n * 1.7), h * bh,
                                    facecolor=UP if d > 0 else DOWN, edgecolor="none", alpha=0.9))

    ax.add_patch(plt.Rectangle((0, 0), 1, 0.016, color=UP))
    ax.add_patch(plt.Rectangle((0.09, 0.87), 0.07, 0.013, color=UP))
    ax.text(0.09, 0.795, "月刊", fontsize=15, color=UP, fontweight="bold", va="center")
    t = ax.text(0.09, 0.60, "資産クラス別\n月間リターンランキング", fontsize=29, color=TITLE,
                fontweight="bold", va="center", linespacing=1.28)
    t.set_path_effects([pe.withStroke(linewidth=1.4, foreground=BG)])
    ax.text(0.09, 0.37, "株・金・債券・REIT・原油・ビットコイン。円建てで並べて読む。",
            fontsize=13, color=MUTE, va="center")

    out = Path(__file__).parent / "magazine-cover.png"
    fig.savefig(out, dpi=200, facecolor=BG)
    plt.close(fig)
    print("saved:", out)


if __name__ == "__main__":
    main()
