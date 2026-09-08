#!/usr/bin/env python3
"""note マガジン「新車ランキングで読む 働き方と投資（月刊）」の見出し画像を生成する。

出力: dev/2-cars/assets/magazine-cover.png（1280x670 = note推奨の 1.91:1）
サムネイル（make_eyecatch.py）と同じ濃紺＋アンバー配色。他部と差別化。
noteのマガジントップでは中央の横帯だけが表示されるため、主要素（タイトル＋
1行タグライン）は上下中央の安全帯（bottom基準で y=0.40〜0.80）に収める。
文言や色を変えたらこのスクリプトを実行し直す。
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.patheffects as pe  # noqa: E402
from matplotlib import font_manager  # noqa: E402

OUT = Path(__file__).with_name("magazine-cover.png")

for _name in ("Noto Sans CJK JP", "Noto Sans JP", "IPAexGothic",
              "Meiryo", "Yu Gothic", "MS Gothic", "Hiragino Sans"):
    try:
        if font_manager.findfont(_name, fallback_to_default=False):
            matplotlib.rcParams["font.family"] = _name
            break
    except Exception:  # noqa: BLE001
        continue

BG = "#26364a"      # 濃紺
ACCENT = "#e0a13c"  # アンバー
TITLE = "#f4f6fa"
SUB = "#9fb0c4"
MUTE = "#6f8098"

W, H = 1280, 670
fig = plt.figure(figsize=(W / 200, H / 200), dpi=200)
ax = fig.add_axes([0, 0, 1, 1])
ax.axis("off")
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)

ax.add_patch(plt.Rectangle((0, 0), 1, 1, color=BG))
ax.add_patch(plt.Rectangle((0, 0), 1, 0.02, color=ACCENT))              # 下端ライン（SNS用）
ax.add_patch(plt.Rectangle((0.075, 0.635), 0.075, 0.017, color=ACCENT))  # タイトル上バー

_title = ax.text(0.072, 0.535, "新車ランキングで読む 働き方と投資",
                 fontsize=25, color=TITLE, fontweight="bold", va="center")
_title.set_path_effects([pe.withStroke(linewidth=1.4, foreground=TITLE)])

ax.text(0.075, 0.43,
        "毎月の総合TOP5に共通する構造から、働き方と投資を考える",
        fontsize=11.5, color=SUB, va="center")

ax.text(0.075, 0.23, "毎月更新   ｜   無料マガジン",
        fontsize=11, color=MUTE, va="center")

fig.savefig(OUT, dpi=200, facecolor=BG)
plt.close(fig)
print(f"saved: {OUT} ({W}x{H})")
