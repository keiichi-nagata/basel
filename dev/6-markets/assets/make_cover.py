#!/usr/bin/env python3
"""開発6部 — noteマガジンの表紙画像を生成する（assets/magazine-cover.png）。

使い方: python dev/6-markets/assets/make_cover.py

noteのマガジン表紙は一覧・関連表示で**中央付近が正方形/円形にトリミングされる**ため、
文字はキャンバスの上下左右に大きく余白を残し、**縦横とも中央のごく狭い帯**（目安: 幅60%・
高さ40%）に収める。装飾の棒グラフは省き、テキストだけをコンパクトに中央配置する。
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

CX, CY = 0.5, 0.5  # キャンバス中央＝トリミングの中心と仮定


def main() -> None:
    W, H = 1280, 670
    fig = plt.figure(figsize=(W / 200, H / 200), dpi=200)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, color=BG))

    # 縦方向も中央に寄せ、上下左右に大きく余白を残す（トリミングで欠けない狭い帯に収める）
    ax.add_patch(plt.Rectangle((CX - 0.035, CY + 0.225), 0.07, 0.012, color=UP))
    ax.text(CX, CY + 0.175, "月刊", fontsize=12, color=UP, fontweight="bold", ha="center", va="center")
    t = ax.text(CX, CY + 0.015, "資産クラス別\n月間リターンランキング", fontsize=15.5, color=TITLE,
                fontweight="bold", ha="center", va="center", linespacing=1.5)
    t.set_path_effects([pe.withStroke(linewidth=1.0, foreground=BG)])
    ax.text(CX, CY - 0.16, "株・金・債券・REIT・原油\nビットコイン。円建てで並べて読む。",
            fontsize=9.5, color=MUTE, ha="center", va="center", linespacing=1.6)

    out = Path(__file__).parent / "magazine-cover.png"
    fig.savefig(out, dpi=200, facecolor=BG)
    plt.close(fig)
    print("saved:", out)


if __name__ == "__main__":
    main()
