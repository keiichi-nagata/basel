#!/usr/bin/env python3
"""各号（各エリア）のnote見出し画像（サムネイル）を生成する。

使い方:
  python make_eyecatch.py                              → 北海道編を assets/2026-10/eyecatch.png に生成
  python make_eyecatch.py "2026年11月" "東北編" assets/2026-11/eyecatch.png

1280x670（note推奨 1.91:1）。マガジン表紙（make_cover.py）と同じ明るい配色。
"""
from __future__ import annotations

import sys
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

BG = "#fdf1e3"
ACCENT = "#e2703a"
TITLE = "#3a2c22"
MUTE = "#8a6d55"

SERIES = "エリア別 温泉宿ランキング（月刊）"


def eyecatch(label: str, subtitle: str, out: Path) -> None:
    W, H = 1280, 670
    fig = plt.figure(figsize=(W / 200, H / 200), dpi=200)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, color=BG))
    ax.add_patch(plt.Rectangle((0, 0), 1, 0.02, color=ACCENT))
    ax.add_patch(plt.Rectangle((0.075, 0.70), 0.06, 0.014, color=ACCENT))

    ax.text(0.075, 0.775, SERIES, fontsize=13, color=MUTE, va="center")
    ax.text(0.075, 0.60, label, fontsize=20, color=ACCENT, fontweight="bold", va="center")

    t = ax.text(0.075, 0.45, subtitle, fontsize=25, color=TITLE,
                fontweight="bold", va="center")
    t.set_path_effects([pe.withStroke(linewidth=1.3, foreground=TITLE)])

    ax.text(0.075, 0.22, "楽天トラベル×じゃらん 独自採点 ｜ 宿ランキングTOP5",
            fontsize=12, color=MUTE, va="center")

    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=200, facecolor=BG)
    plt.close(fig)
    print("saved:", out)


if __name__ == "__main__":
    here = Path(__file__).parent
    if len(sys.argv) >= 3:
        label, subtitle = sys.argv[1], sys.argv[2]
        out = Path(sys.argv[3]) if len(sys.argv) >= 4 else here / "eyecatch.png"
    else:
        label, subtitle = "2026年10月", "北海道温泉編"
        out = here / "2026-10" / "eyecatch.png"
    eyecatch(label, subtitle, out)
