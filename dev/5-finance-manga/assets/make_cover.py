#!/usr/bin/env python3
"""開発5部 note マガジンの見出し画像を生成する。

出力: dev/5-finance-manga/assets/magazine-cover.png（1280x670 = note推奨の 1.91:1）
noteのマガジントップは中央の横帯だけ表示されるため、主要素（フック1行＋サブ1行）を
上下中央の安全帯に収める。文言・色を変えたら実行し直す。
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

BG = "#16233a"       # 濃紺（信頼・学び）
ACCENT = "#e0b64d"   # ゴールド
TITLE = "#f6f8fc"
SUB = "#b7c2d4"
MUTE = "#7f8ba0"

W, H = 1280, 670
fig = plt.figure(figsize=(W / 200, H / 200), dpi=200)
ax = fig.add_axes([0, 0, 1, 1])
ax.axis("off")
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)

ax.add_patch(plt.Rectangle((0, 0), 1, 1, color=BG))
ax.add_patch(plt.Rectangle((0, 0), 1, 0.02, color=ACCENT))          # 下端ライン（SNS用）
ax.add_patch(plt.Rectangle((0.075, 0.635), 0.075, 0.017, color=ACCENT))  # タイトル上バー

_title = ax.text(0.072, 0.535, "未来の自分に10万円を託すなら？",
                 fontsize=25, color=TITLE, fontweight="bold", va="center")
_title.set_path_effects([pe.withStroke(linewidth=1.3, foreground=TITLE)])

ax.text(0.075, 0.435,
        "中学生からの金融リテラシー ｜ マンガで学ぶ 全10回（＋序章）",
        fontsize=12, color=SUB, va="center")

# 安全帯の外（SNSシェア時のみ見える）
ax.text(0.075, 0.22, "稼ぐ・守る・増やす を、お小遣いとゲームのたとえで",
        fontsize=11, color=MUTE, va="center")

fig.savefig(OUT, dpi=200, facecolor=BG)
plt.close(fig)
print(f"saved: {OUT} ({W}x{H})")
