#!/usr/bin/env python3
"""開発2部 — 月次記事のnote見出し画像（サムネイル）を生成する。

note用（1280x670）とInstagram用（4:5・1080x1350）の2サイズを出力。

使い方:
  python make_eyecatch.py                                  → 2026年8月号を assets/2026-08/ に生成
  python make_eyecatch.py "2026年9月号" "今月のテーマ1行" assets/2026-09
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

BG = "#26364a"       # 濃紺（クルマ＋分析の落ち着き。他部と差別化）
ACCENT = "#e0a13c"   # アンバー
TITLE = "#f4f6fa"
MUTE = "#9fb0c4"

SERIES = "新車販売台数ランキング × 働き方・投資"


def _wrap(subtitle: str, limit: int) -> list[str]:
    if len(subtitle) <= limit:
        return [subtitle]
    if "、" in subtitle:
        head, tail = subtitle.split("、", 1)
        return [head + "、", tail]
    mid = len(subtitle) // 2
    return [subtitle[:mid], subtitle[mid:]]


def _render(label: str, subtitle: str, out: Path, size: str) -> None:
    if size == "ig":
        W, H = 1080, 1350
        y_series, y_tick, y_label, y_sub, y_tag = 0.86, 0.79, 0.71, 0.575, 0.40
        fs_label, fs_sub, fs_tag = 22, 30, 14
        lines = _wrap(subtitle, 10)
    else:
        W, H = 1280, 670
        y_series, y_tick, y_label, y_sub, y_tag = 0.775, 0.715, 0.60, 0.44, 0.22
        fs_label, fs_sub, fs_tag = 19, 27, 12
        lines = _wrap(subtitle, 18)

    fig = plt.figure(figsize=(W / 200, H / 200), dpi=200)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, color=BG))
    ax.add_patch(plt.Rectangle((0, 0), 1, 0.015, color=ACCENT))
    ax.add_patch(plt.Rectangle((0.075, y_tick), 0.06, 0.012, color=ACCENT))

    ax.text(0.075, y_series, SERIES, fontsize=12.5, color=MUTE, va="center")
    ax.text(0.075, y_label, label, fontsize=fs_label, color=ACCENT, fontweight="bold", va="center")
    line_gap = 0.075 if size == "ig" else 0.11
    for i, ln in enumerate(lines):
        t = ax.text(0.075, y_sub - i * line_gap, ln, fontsize=fs_sub, color=TITLE,
                    fontweight="bold", va="center")
        t.set_path_effects([pe.withStroke(linewidth=1.3, foreground=TITLE)])
    ax.text(0.075, y_tag, "登録車＋軽 総合TOP5から読む", fontsize=fs_tag, color=MUTE, va="center")

    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=200, facecolor=BG)
    plt.close(fig)
    print("saved:", out)


def eyecatch(label: str, subtitle: str, out_dir: Path) -> None:
    _render(label, subtitle, out_dir / "eyecatch.png", "note")
    _render(label, subtitle, out_dir / "eyecatch-ig.png", "ig")


if __name__ == "__main__":
    here = Path(__file__).parent
    if len(sys.argv) >= 3:
        label, subtitle = sys.argv[1], sys.argv[2]
        out_dir = Path(sys.argv[3]) if len(sys.argv) >= 4 else here
    else:
        label, subtitle = "2026年8月号", "供給が止まると、数字はこう動く"
        out_dir = here / "2026-08"
    eyecatch(label, subtitle, out_dir)
