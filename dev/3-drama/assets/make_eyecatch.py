#!/usr/bin/env python3
"""毎週のnote見出し画像／Instagram用画像を生成する（開発4部と同じハイブリッド方式）。

背景は`scripts/ai_image.py`で生成した固定の背景画像（`eyecatch-bg-note.png`／
`eyecatch-bg-ig.png`。テレビ・映画好きの部屋をイメージした暗い配色、既存の
`make_cover.py`と同じ配色）を毎週使い回し、その上に週ごとの文字（週番号・
今週1位の作品名・タグライン）だけをmatplotlibで重ねる。背景は週替わりで
作り直さない（費用と一貫性のため）。

使い方:
  python dev/3-drama/assets/make_eyecatch.py "2026-W37" "9月7日〜9月13日" "1位: VIVANT"
      → assets/2026-W37/eyecatch.png（note 1280x670）と eyecatch-ig.png（IG 1080x1350）
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

for _name in ("Noto Sans CJK JP", "Noto Sans JP", "IPAexGothic",
              "Meiryo", "Yu Gothic", "MS Gothic", "Hiragino Sans"):
    try:
        if font_manager.findfont(_name, fallback_to_default=False):
            matplotlib.rcParams["font.family"] = _name
            break
    except Exception:  # noqa: BLE001
        continue

HERE = Path(__file__).parent
# 2026-09-16: 暗い配色から、明るく温かみのある配色に変更（社長フィードバック）
BG = "#fdf6ea"
ACCENT = "#e8a33d"
TITLE = "#2b2118"
SUB = "#6b5d4a"
MUTE = "#9c8f7a"
SERIES = "話題のドラマ総合ランキング（週刊）"
DEFAULT_TAGLINE = "TVer×Netflix×Google検索トレンド ｜ 独自の話題度指標"


def _render(week_label: str, period: str, top_line: str, out: Path, size: str,
            bg_path: Path | None, tagline: str) -> None:
    if size == "ig":
        W, H = 1080, 1350
        y_series, y_tick, y_label, y_sub, y_tag = 0.905, 0.815, 0.745, 0.63, 0.545
        fs_label, fs_sub, fs_tag = 22, 30, 15
        panel_h = 0.50
    else:  # note
        W, H = 1280, 670
        y_series, y_tick, y_label, y_sub, y_tag = 0.80, 0.72, 0.575, 0.40, 0.20
        fs_label, fs_sub, fs_tag = 18, 26, 12
        panel_w = 0.60

    if len(top_line) > 12:
        fs_sub = int(fs_sub * 0.8)
    if size == "ig" and len(tagline) > 20:
        fs_tag = int(fs_tag * 0.78)
    if size == "note" and len(tagline) > 18:
        fs_tag = int(fs_tag * 0.82)

    fig = plt.figure(figsize=(W / 200, H / 200), dpi=200)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    if bg_path is not None and Path(bg_path).exists():
        img = np.asarray(Image.open(bg_path).convert("RGB"))
        ax.imshow(img, extent=[0, 1, 0, 1], aspect="auto", zorder=0)
        if size == "ig":
            ax.add_patch(plt.Rectangle((0, 1 - panel_h), 1, panel_h, color=BG, alpha=0.72, zorder=1))
        else:
            ax.add_patch(plt.Rectangle((0, 0), panel_w, 1, color=BG, alpha=0.72, zorder=1))
    else:
        ax.add_patch(plt.Rectangle((0, 0), 1, 1, color=BG, zorder=0))

    ax.add_patch(plt.Rectangle((0, 0), 1, 0.015, color=ACCENT, zorder=2))
    ax.add_patch(plt.Rectangle((0.075, y_tick), 0.06, 0.012, color=ACCENT, zorder=2))

    ax.text(0.075, y_series, SERIES, fontsize=13, color=MUTE, va="center", zorder=3)
    ax.text(0.075, y_label, f"{week_label}／{period}", fontsize=fs_label, color=ACCENT,
            fontweight="bold", va="center", zorder=3)
    t = ax.text(0.075, y_sub, top_line, fontsize=fs_sub, color=TITLE, fontweight="bold",
                va="center", zorder=3)
    t.set_path_effects([pe.withStroke(linewidth=1.2, foreground=TITLE)])
    ax.text(0.075, y_tag, tagline, fontsize=fs_tag, color=SUB, va="center", zorder=3)

    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=200, facecolor=BG)
    plt.close(fig)
    print("saved:", out)


def eyecatch(week_label: str, period: str, top_line: str, out_dir: Path,
             tagline: str = DEFAULT_TAGLINE) -> None:
    """note用（eyecatch.png）とInstagram用（eyecatch-ig.png）を両方生成する。"""
    bg_note = HERE / "eyecatch-bg-note.png"
    bg_ig = HERE / "eyecatch-bg-ig.png"
    _render(week_label, period, top_line, out_dir / "eyecatch.png", "note", bg_note, tagline)
    _render(week_label, period, top_line, out_dir / "eyecatch-ig.png", "ig", bg_ig, tagline)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("使い方: python make_eyecatch.py <週番号> <期間> <トップライン> [出力先]")
        raise SystemExit(1)
    week_label, period, top_line = sys.argv[1], sys.argv[2], sys.argv[3]
    out_dir = Path(sys.argv[4]) if len(sys.argv) >= 5 else HERE / week_label
    eyecatch(week_label, period, top_line, out_dir)
