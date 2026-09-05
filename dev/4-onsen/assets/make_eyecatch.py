#!/usr/bin/env python3
"""各号（各エリア）のnote見出し画像／Instagram用画像を生成する。

使い方:
  python make_eyecatch.py                                      → 北海道編を両サイズ生成
  python make_eyecatch.py "2026年11月" "東北編" assets/2026-11 [motif]
      → assets/2026-11/eyecatch.png（note 1280x670）と eyecatch-ig.png（IG 1080x1350）

motif はエリアを連想させる簡単な自作イラスト（写真は著作権リスクがあるため使わない）。
現状用意しているのは "hokkaido"（雪山＋紅葉＋湯気）のみ。他エリアは追加時にモチーフを増やす。

配色はマガジン表紙（make_cover.py）と同じ明るい暖色系。
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
MOUNTAIN = "#c9a98a"
SNOW = "#fff8f0"
LEAF_COLORS = ("#e2703a", "#d4a24c", "#c1452f")

SERIES = "エリア別 温泉宿ランキング（月刊）"


def _snow_peak(ax, base_l, apex, base_r) -> None:
    ax.add_patch(mpatches.Polygon([base_l, apex, base_r], closed=True,
                                   facecolor=MOUNTAIN, edgecolor="none", zorder=1))
    sx, sy = apex
    ax.add_patch(mpatches.Polygon([(sx - 0.032, sy - 0.085), (sx, sy), (sx + 0.032, sy - 0.085)],
                                   closed=True, facecolor=SNOW, edgecolor="none", zorder=2))


def _scatter_leaves(ax, seed, xr, yr, n) -> None:
    rng = random.Random(seed)
    for _ in range(n):
        x, y = rng.uniform(*xr), rng.uniform(*yr)
        w = rng.uniform(0.012, 0.02)
        ax.add_patch(mpatches.Ellipse((x, y), w, w * rng.uniform(1.4, 1.8),
                                       angle=rng.uniform(0, 360), facecolor=rng.choice(LEAF_COLORS),
                                       edgecolor="none", alpha=0.85, zorder=3))


def _steam(ax, x0s, top) -> None:
    for i, x0 in enumerate(x0s):
        ys = np.linspace(0.0, top, 40)
        ax.plot(x0 + 0.018 * np.sin(ys * 18 + i), ys, color="#d8c9b8",
                linewidth=2.2, alpha=0.6, zorder=2)


def _hokkaido_side(ax) -> None:
    """note用（横長）: 右側に雪山。"""
    _snow_peak(ax, (0.60, 0.0), (0.70, 0.34), (0.80, 0.0))
    _snow_peak(ax, (0.70, 0.0), (0.80, 0.44), (0.90, 0.0))
    _snow_peak(ax, (0.82, 0.0), (0.93, 0.52), (1.03, 0.0))
    _scatter_leaves(ax, 4, (0.60, 1.05), (0.05, 0.58), 16)
    _steam(ax, (0.90, 0.955, 1.01), 0.30)


def _hokkaido_bottom(ax) -> None:
    """Instagram用（縦長）: 下部いっぱいに雪山。"""
    _snow_peak(ax, (-0.05, 0.0), (0.18, 0.30), (0.42, 0.0))
    _snow_peak(ax, (0.28, 0.0), (0.52, 0.40), (0.78, 0.0))
    _snow_peak(ax, (0.60, 0.0), (0.85, 0.33), (1.08, 0.0))
    _scatter_leaves(ax, 7, (0.0, 1.05), (0.05, 0.52), 20)
    _steam(ax, (0.44, 0.50, 0.56), 0.26)


MOTIFS = {"hokkaido": (_hokkaido_side, _hokkaido_bottom)}


def _render(label, subtitle, out, motif, size) -> None:
    if size == "ig":
        W, H = 1080, 1350
        y_series, y_tick, y_label, y_sub, y_tag = 0.905, 0.815, 0.745, 0.645, 0.545
        fs_label, fs_sub, fs_tag = 24, 34, 15
        tagline = "楽天トラベル×じゃらんの独自採点"
        motif_idx = 1
    else:  # note
        W, H = 1280, 670
        y_series, y_tick, y_label, y_sub, y_tag = 0.775, 0.715, 0.60, 0.45, 0.22
        fs_label, fs_sub, fs_tag = 20, 25, 12
        tagline = "楽天トラベル×じゃらん 独自採点 ｜ 宿ランキングTOP5"
        motif_idx = 0

    fig = plt.figure(figsize=(W / 200, H / 200), dpi=200)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, color=BG))
    if motif in MOTIFS:
        MOTIFS[motif][motif_idx](ax)
    ax.add_patch(plt.Rectangle((0, 0), 1, 0.015, color=ACCENT))
    ax.add_patch(plt.Rectangle((0.075, y_tick), 0.06, 0.012, color=ACCENT))

    ax.text(0.075, y_series, SERIES, fontsize=13, color=MUTE, va="center")
    ax.text(0.075, y_label, label, fontsize=fs_label, color=ACCENT, fontweight="bold", va="center")
    t = ax.text(0.075, y_sub, subtitle, fontsize=fs_sub, color=TITLE, fontweight="bold", va="center")
    t.set_path_effects([pe.withStroke(linewidth=1.3, foreground=TITLE)])
    ax.text(0.075, y_tag, tagline, fontsize=fs_tag, color=MUTE, va="center")

    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=200, facecolor=BG)
    plt.close(fig)
    print("saved:", out)


def eyecatch(label: str, subtitle: str, out_dir: Path, motif: str | None = None) -> None:
    """note用（eyecatch.png）とInstagram用（eyecatch-ig.png）を両方生成する。"""
    _render(label, subtitle, out_dir / "eyecatch.png", motif, "note")
    _render(label, subtitle, out_dir / "eyecatch-ig.png", motif, "ig")


if __name__ == "__main__":
    here = Path(__file__).parent
    if len(sys.argv) >= 3:
        label, subtitle = sys.argv[1], sys.argv[2]
        out_dir = Path(sys.argv[3]) if len(sys.argv) >= 4 else here
        motif = sys.argv[4] if len(sys.argv) >= 5 else None
    else:
        label, subtitle = "2026年9月", "北海道温泉編"
        out_dir = here / "2026-09"
        motif = "hokkaido"
    eyecatch(label, subtitle, out_dir, motif)
