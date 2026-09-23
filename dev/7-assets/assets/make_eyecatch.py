#!/usr/bin/env python3
"""開発7部 — note見出し画像（サムネイル）を生成する（他部と同じハイブリッド方式）。

背景は`scripts/ai_image.py`で生成した固定の背景画像（`bg-note.png`／`bg-ig.png`。
硬貨の上から芽が伸びる様子＋家族写真をイメージした、深いティール×ゴールドの配色）を
シリーズ横断で使い回し、その上に記事ごとの文字（シリーズ名・回数・タイトル）だけを
matplotlibで重ねる。背景は記事ごとに作り直さない（費用と一貫性のため）。

note用（1280x670）とInstagram用（4:5・1080x1350）の2サイズを出力。

使い方:
  python make_eyecatch.py "第1回" "今すぐ始める！家計見直しとライフプランの作り方" \\
      "【月5万円】子育て世代の王道資産形成" drafts/01
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

BG = "#1c2e2a"       # 深いティールグリーン（信頼・成長）
ACCENT = "#d4a94f"   # 落ち着いたゴールド（お金）
TITLE = "#f5f7f3"
SUB = "#c9d6cf"
MUTE = "#8fa39a"


def _wrap(text: str, limit: int) -> list[str]:
    """句読点（！、。）の直後を優先して`limit`文字以内で改行する。長いタイトルは3行以上になる。"""
    breakers = "！、。"
    lines: list[str] = []
    remaining = text
    while len(remaining) > limit:
        cut = -1
        for i in range(min(limit, len(remaining) - 1), 0, -1):
            if remaining[i - 1] in breakers:
                cut = i
                break
        if cut == -1:
            cut = limit
        lines.append(remaining[:cut])
        remaining = remaining[cut:]
    if remaining:
        lines.append(remaining)
    return lines


def _render(series: str, label: str, title: str, out: Path, size: str, bg_path: Path | None) -> None:
    if size == "ig":
        W, H = 1080, 1350
        y_series, y_tick, y_label, y_title = 0.87, 0.80, 0.72, 0.575
        fs_series, fs_label, fs_title = 15, 22, 30
        wrap_limit = 9
        panel_h = 0.62
    else:
        W, H = 1280, 670
        y_series, y_tick, y_label, y_title = 0.80, 0.72, 0.60, 0.44
        fs_series, fs_label, fs_title = 13, 19, 27
        wrap_limit = 9
        panel_w = 0.62

    lines = _wrap(title, wrap_limit)
    if len(lines) >= 3:
        fs_title = int(fs_title * 0.8)

    fig = plt.figure(figsize=(W / 200, H / 200), dpi=200)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    if bg_path is not None and Path(bg_path).exists():
        img = np.asarray(Image.open(bg_path).convert("RGB"))
        ax.imshow(img, extent=[0, 1, 0, 1], aspect="auto", zorder=0)
        if size == "ig":
            ax.add_patch(plt.Rectangle((0, 1 - panel_h), 1, panel_h, color=BG, alpha=0.76, zorder=1))
        else:
            ax.add_patch(plt.Rectangle((0, 0), panel_w, 1, color=BG, alpha=0.76, zorder=1))
    else:
        ax.add_patch(plt.Rectangle((0, 0), 1, 1, color=BG, zorder=0))

    ax.add_patch(plt.Rectangle((0, 0), 1, 0.015, color=ACCENT, zorder=2))
    ax.add_patch(plt.Rectangle((0.075, y_tick), 0.06, 0.012, color=ACCENT, zorder=2))

    ax.text(0.075, y_series, series, fontsize=fs_series, color=MUTE, va="center", zorder=3)
    ax.text(0.075, y_label, label, fontsize=fs_label, color=ACCENT, fontweight="bold", va="center", zorder=3)
    line_gap = 0.075 if size == "ig" else 0.105
    for i, ln in enumerate(lines):
        t = ax.text(0.075, y_title - i * line_gap, ln, fontsize=fs_title, color=TITLE,
                    fontweight="bold", va="center", zorder=3)
        t.set_path_effects([pe.withStroke(linewidth=1.3, foreground=TITLE)])

    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=200, facecolor=BG)
    plt.close(fig)
    print("saved:", out)


def eyecatch(series: str, label: str, title: str, out_dir: Path) -> None:
    bg_note = HERE / "bg-note.png"
    bg_ig = HERE / "bg-ig.png"
    _render(series, label, title, out_dir / "eyecatch.png", "note", bg_note)
    _render(series, label, title, out_dir / "eyecatch-ig.png", "ig", bg_ig)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("使い方: python make_eyecatch.py <回数> <タイトル> <シリーズ名> [出力先]")
        raise SystemExit(1)
    label, title, series = sys.argv[1], sys.argv[2], sys.argv[3]
    out_dir = Path(sys.argv[4]) if len(sys.argv) >= 5 else HERE.parent / "drafts"
    eyecatch(series, label, title, out_dir)
