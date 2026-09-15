#!/usr/bin/env python3
"""開発6部 — 各号のnote見出し画像／Instagram用画像を生成する。

使い方:
  python dev/6-markets/assets/make_eyecatch.py                      → 2026年8月号を両サイズ生成
  python dev/6-markets/assets/make_eyecatch.py "2026年8月" dev/6-markets/assets/2026-08

配色はマガジン表紙（make_cover.py）と同じグラファイト＋緑/赤（マーケット/データ）。
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.patheffects as pe  # noqa: E402
from matplotlib import font_manager  # noqa: E402

for _name in ("Yu Gothic", "Meiryo", "MS Gothic", "IPAexGothic",
              "Hiragino Sans", "Noto Sans CJK JP", "Noto Sans JP"):
    try:
        if font_manager.findfont(_name, fallback_to_default=False):
            matplotlib.rcParams["font.family"] = _name
            break
    except Exception:  # noqa: BLE001
        continue

BG = "#20242e"
CARD = "#2b2f3a"
TITLE = "#f3f4f6"
MUTE = "#9aa2ad"
UP = "#38b676"
DOWN = "#e0605f"

SERIES = "資産クラス別 月間リターンランキング（月刊）"
_BARS = [0.42, 0.68, 0.95, 0.55, 0.30, 0.78, 0.18, 0.62]      # 高さ（相対）
_DIR = [1, 1, 1, 1, -1, 1, -1, -1]                             # 上げ/下げ


def _bars(ax, x0, y0, w, h) -> None:
    n = len(_BARS)
    bw = w / (n * 1.6)
    for i, (bh, d) in enumerate(zip(_BARS, _DIR)):
        x = x0 + i * (w / n)
        col = UP if d > 0 else DOWN
        ax.add_patch(plt.Rectangle((x, y0), bw, h * bh, facecolor=col,
                                    edgecolor="none", alpha=0.9))


def _render(label: str, out: Path, size: str) -> None:
    if size == "ig":
        W, H = 1080, 1350
        y_series, y_tick, y_label, y_title, y_tag = 0.915, 0.85, 0.79, 0.685, 0.575
        fs_label, fs_title, fs_tag = 21, 25, 14
        tagline = "株・金・債券・REIT・原油・ビットコイン"
        bar_box = (0.08, 0.13, 0.84, 0.30)
    else:
        W, H = 1280, 670
        y_series, y_tick, y_label, y_title, y_tag = 0.80, 0.735, 0.61, 0.45, 0.22
        fs_label, fs_title, fs_tag = 19, 27, 12
        tagline = "円建てで10クラスを毎月ランキング"
        bar_box = (0.73, 0.08, 0.24, 0.26)

    fig = plt.figure(figsize=(W / 200, H / 200), dpi=200)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, color=BG))
    _bars(ax, *bar_box)
    ax.add_patch(plt.Rectangle((0, 0), 1, 0.014, color=UP))
    ax.add_patch(plt.Rectangle((0.075, y_tick), 0.06, 0.011, color=UP))

    ax.text(0.075, y_series, SERIES, fontsize=13, color=MUTE, va="center")
    ax.text(0.075, y_label, label, fontsize=fs_label, color=UP, fontweight="bold", va="center")
    t = ax.text(0.075, y_title, "資産クラス別\n月間リターンランキング", fontsize=fs_title,
                color=TITLE, fontweight="bold", va="center", linespacing=1.25)
    t.set_path_effects([pe.withStroke(linewidth=1.2, foreground=BG)])
    ax.text(0.075, y_tag, tagline, fontsize=fs_tag, color=MUTE, va="center")

    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=200, facecolor=BG)
    plt.close(fig)
    print("saved:", out)


def eyecatch(label: str, out_dir: Path) -> None:
    _render(label, out_dir / "eyecatch.png", "note")
    _render(label, out_dir / "eyecatch-ig.png", "ig")


if __name__ == "__main__":
    here = Path(__file__).parent
    if len(sys.argv) >= 2:
        label = sys.argv[1]
        out_dir = Path(sys.argv[2]) if len(sys.argv) >= 3 else here
    else:
        label = "2026年8月"
        out_dir = here / "2026-08"
    eyecatch(label, out_dir)
