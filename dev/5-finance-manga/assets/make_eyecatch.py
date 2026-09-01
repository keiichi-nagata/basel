#!/usr/bin/env python3
"""各エピソードのnote見出し画像（タイトルカード）を生成する。

使い方:
  python make_eyecatch.py                → 序章を assets/00/eyecatch.png に生成
  python make_eyecatch.py "第1回" "なぜ今「お金の勉強」が必要なの？" assets/01/eyecatch.png

1280x670（note推奨 1.91:1）。マガジン表紙と同じ配色。中央帯に文言を収める。
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

BG = "#16233a"
ACCENT = "#e0b64d"
TITLE = "#f6f8fc"
MUTE = "#8f9bb0"

SERIES = "中学生からの金融の授業"


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

    ax.text(0.075, 0.22, "お小遣い・ゲーム・推し活のたとえで学ぶ ｜ マンガ連載",
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
        label, subtitle = "序章", "未来の自分に10万円を託すなら？"
        out = here / "00" / "eyecatch.png"
    eyecatch(label, subtitle, out)
