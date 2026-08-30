#!/usr/bin/env python3
"""note マガジンの見出し画像を生成する。

出力: dev/3-drama/assets/magazine-cover.png（1920x1005, note推奨の 1.91:1）
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

BG = "#14171d"
ACCENT = "#e5484d"
TITLE = "#f5f7fa"
SUB = "#aeb7c4"
MUTE = "#79828f"

W, H = 1920, 1005
fig = plt.figure(figsize=(W / 200, H / 200), dpi=200)
ax = fig.add_axes([0, 0, 1, 1])
ax.axis("off")
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)

ax.add_patch(plt.Rectangle((0, 0), 1, 1, color=BG))
# 下端のアクセントライン
ax.add_patch(plt.Rectangle((0, 0), 1, 0.012, color=ACCENT))
# タイトル上の短いアクセントバー
ax.add_patch(plt.Rectangle((0.075, 0.845), 0.10, 0.016, color=ACCENT))

_title = ax.text(0.072, 0.80, "話題のドラマ\n総合ランキング",
                 fontsize=53, color=TITLE, fontweight="bold", va="top", linespacing=1.22)
# Windows の細字フォント対策に軽く縁取りして太く見せる
_title.set_path_effects([pe.withStroke(linewidth=2.2, foreground=TITLE)])

ax.text(0.075, 0.375,
        "TVer週間  ・  Netflix Japan Top10  ・  Google検索トレンド",
        fontsize=19, color=SUB, va="top")
ax.text(0.075, 0.305,
        "を合成した、独自の“話題度”指標で毎週ランキング",
        fontsize=19, color=SUB, va="top")

ax.text(0.075, 0.15, "毎週月曜更新   ｜   無料マガジン",
        fontsize=17, color=MUTE, va="top")

fig.savefig(OUT, dpi=200, facecolor=BG)
plt.close(fig)
print(f"saved: {OUT}")
