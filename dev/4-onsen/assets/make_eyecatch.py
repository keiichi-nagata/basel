#!/usr/bin/env python3
"""各号（各エリア）のnote見出し画像（サムネイル）を生成する。

使い方:
  python make_eyecatch.py                              → 北海道編を assets/2026-10/eyecatch.png に生成
  python make_eyecatch.py "2026年11月" "東北編" assets/2026-11/eyecatch.png [motif]

motif はエリアを連想させる簡単な自作イラスト（写真は著作権リスクがあるため使わない）。
現状用意しているのは "hokkaido"（雪山＋紅葉＋湯気）のみ。他エリアは追加時にモチーフを増やす。

1280x670（note推奨 1.91:1）。マガジン表紙（make_cover.py）と同じ明るい配色。
"""
from __future__ import annotations

import random
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.patches as mpatches  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.patheffects as pe  # noqa: E402
import numpy as np  # noqa: E402
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


def _draw_hokkaido_motif(ax) -> None:
    """大雪山系の雪山・紅葉・温泉の湯気をイメージした自作イラスト（右側、x=0.60〜）。"""
    mountain_color = "#c9a98a"
    snow_color = "#fff8f0"
    leaf_colors = ["#e2703a", "#d4a24c", "#c1452f"]

    peaks = [
        ((0.60, 0.0), (0.70, 0.34), (0.80, 0.0)),
        ((0.70, 0.0), (0.80, 0.44), (0.90, 0.0)),
        ((0.82, 0.0), (0.93, 0.52), (1.03, 0.0)),
    ]
    for base_l, apex, base_r in peaks:
        ax.add_patch(mpatches.Polygon([base_l, apex, base_r], closed=True,
                                       facecolor=mountain_color, edgecolor="none", zorder=1))
        sx, sy = apex
        snow = [(sx - 0.032, sy - 0.085), (sx, sy), (sx + 0.032, sy - 0.085)]
        ax.add_patch(mpatches.Polygon(snow, closed=True, facecolor=snow_color,
                                       edgecolor="none", zorder=2))

    rng = random.Random(4)
    for _ in range(16):
        x = rng.uniform(0.60, 1.05)
        y = rng.uniform(0.05, 0.58)
        w = rng.uniform(0.012, 0.02)
        h = w * rng.uniform(1.4, 1.8)
        angle = rng.uniform(0, 360)
        color = rng.choice(leaf_colors)
        ax.add_patch(mpatches.Ellipse((x, y), w, h, angle=angle, facecolor=color,
                                       edgecolor="none", alpha=0.85, zorder=3))

    for i, x0 in enumerate((0.90, 0.955, 1.01)):
        ys = np.linspace(0.0, 0.30, 40)
        xs = x0 + 0.018 * np.sin(ys * 18 + i)
        ax.plot(xs, ys, color="#d8c9b8", linewidth=2.2, alpha=0.6, zorder=2)


MOTIFS = {"hokkaido": _draw_hokkaido_motif}


def eyecatch(label: str, subtitle: str, out: Path, motif: str | None = None) -> None:
    W, H = 1280, 670
    fig = plt.figure(figsize=(W / 200, H / 200), dpi=200)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, color=BG))
    if motif and motif in MOTIFS:
        MOTIFS[motif](ax)
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
        motif = sys.argv[4] if len(sys.argv) >= 5 else None
    else:
        label, subtitle = "2026年10月", "北海道温泉編"
        out = here / "2026-10" / "eyecatch.png"
        motif = "hokkaido"
    eyecatch(label, subtitle, out, motif)
