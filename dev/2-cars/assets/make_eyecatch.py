#!/usr/bin/env python3
"""開発2部 — 月次記事・号外のnote見出し画像（サムネイル）を生成する（他部と同じハイブリッド方式）。

背景は`scripts/ai_image.py`で生成した固定の背景画像（`eyecatch-bg-note.png`／
`eyecatch-bg-ig.png`。車＋データ分析をイメージした濃紺＋アンバー配色）を使い回し、
その上に号ごとの文字（号数・見出し1行）だけをmatplotlibで重ねる。背景は号ごとに
作り直さない（費用と一貫性のため。2026-09-17、社長の要望で単色背景から写真調の
背景に変更）。

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
import numpy as np  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from PIL import Image  # noqa: E402

for _name in ("Yu Gothic", "Meiryo", "MS Gothic", "IPAexGothic",
              "Hiragino Sans", "Noto Sans CJK JP", "Noto Sans JP"):
    try:
        if font_manager.findfont(_name, fallback_to_default=False):
            matplotlib.rcParams["font.family"] = _name
            break
    except Exception:  # noqa: BLE001
        continue

HERE = Path(__file__).parent

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


def _render(label: str, subtitle: str, tag: str, out: Path, size: str, bg_path: Path | None) -> None:
    if size == "ig":
        W, H = 1080, 1350
        y_series, y_tick, y_label, y_sub, y_tag = 0.86, 0.79, 0.71, 0.575, 0.40
        fs_label, fs_sub, fs_tag = 22, 30, 14
        lines = _wrap(subtitle, 10)
        panel_h = 0.62
    else:
        W, H = 1280, 670
        y_series, y_tick, y_label, y_sub, y_tag = 0.775, 0.715, 0.60, 0.44, 0.22
        fs_label, fs_sub, fs_tag = 19, 27, 12
        lines = _wrap(subtitle, 9)
        panel_w = 0.62

    fig = plt.figure(figsize=(W / 200, H / 200), dpi=200)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    if bg_path is not None and Path(bg_path).exists():
        img = np.asarray(Image.open(bg_path).convert("RGB"))
        ax.imshow(img, extent=[0, 1, 0, 1], aspect="auto", zorder=0)
        if size == "ig":
            ax.add_patch(plt.Rectangle((0, 1 - panel_h), 1, panel_h, color=BG, alpha=0.74, zorder=1))
        else:
            ax.add_patch(plt.Rectangle((0, 0), panel_w, 1, color=BG, alpha=0.74, zorder=1))
    else:
        ax.add_patch(plt.Rectangle((0, 0), 1, 1, color=BG, zorder=0))

    ax.add_patch(plt.Rectangle((0, 0), 1, 0.015, color=ACCENT, zorder=2))
    ax.add_patch(plt.Rectangle((0.075, y_tick), 0.06, 0.012, color=ACCENT, zorder=2))

    ax.text(0.075, y_series, SERIES, fontsize=12.5, color=MUTE, va="center", zorder=3)
    ax.text(0.075, y_label, label, fontsize=fs_label, color=ACCENT, fontweight="bold", va="center", zorder=3)
    line_gap = 0.075 if size == "ig" else 0.11
    for i, ln in enumerate(lines):
        t = ax.text(0.075, y_sub - i * line_gap, ln, fontsize=fs_sub, color=TITLE,
                    fontweight="bold", va="center", zorder=3)
        t.set_path_effects([pe.withStroke(linewidth=1.3, foreground=TITLE)])
    ax.text(0.075, y_tag, tag, fontsize=fs_tag, color=MUTE, va="center", zorder=3)

    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=200, facecolor=BG)
    plt.close(fig)
    print("saved:", out)


def eyecatch(label: str, subtitle: str, out_dir: Path, tag: str = "登録車＋軽 総合TOP5から読む") -> None:
    bg_note = HERE / "eyecatch-bg-note.png"
    bg_ig = HERE / "eyecatch-bg-ig.png"
    _render(label, subtitle, tag, out_dir / "eyecatch.png", "note", bg_note)
    _render(label, subtitle, tag, out_dir / "eyecatch-ig.png", "ig", bg_ig)


if __name__ == "__main__":
    if len(sys.argv) >= 3:
        label, subtitle = sys.argv[1], sys.argv[2]
        out_dir = Path(sys.argv[3]) if len(sys.argv) >= 4 else HERE / label
    else:
        label, subtitle = "2026年8月号", "供給が止まると、数字はこう動く"
        out_dir = HERE / "2026-08"
    eyecatch(label, subtitle, out_dir)
