#!/usr/bin/env python3
"""note マガジンの見出し画像を生成する。

出力: dev/3-drama/assets/magazine-cover.png（1280x670 = note推奨の 1.91:1）
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

BG = "#14171d"
ACCENT = "#e5484d"
TITLE = "#f5f7fa"
SUB = "#aeb7c4"
MUTE = "#79828f"

W, H = 1280, 670
fig = plt.figure(figsize=(W / 200, H / 200), dpi=200)
ax = fig.add_axes([0, 0, 1, 1])
ax.axis("off")
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)

ax.add_patch(plt.Rectangle((0, 0), 1, 1, color=BG))
ax.add_patch(plt.Rectangle((0, 0), 1, 0.02, color=ACCENT))          # 下端ライン（SNS用）
ax.add_patch(plt.Rectangle((0.075, 0.865), 0.08, 0.02, color=ACCENT))  # タイトル上バー

_title = ax.text(0.072, 0.60, "話題のドラマ\n総合ランキング",
                 fontsize=37, color=TITLE, fontweight="bold", va="center", linespacing=1.15)
_title.set_path_effects([pe.withStroke(linewidth=1.8, foreground=TITLE)])

ax.text(0.075, 0.29,
        "TVer週間  ・  Netflix Japan Top10  ・  検索トレンドを合成した独自指標",
        fontsize=13, color=SUB, va="center")

# 安全帯の外（SNSシェア時のみ見える）
ax.text(0.075, 0.13, "毎週月曜更新   ｜   無料マガジン",
        fontsize=11.5, color=MUTE, va="center")

fig.savefig(OUT, dpi=200, facecolor=BG)
plt.close(fig)
print(f"saved: {OUT} ({W}x{H})")
