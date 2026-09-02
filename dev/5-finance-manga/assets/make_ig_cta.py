#!/usr/bin/env python3
"""Instagramカルーセルの最後に足すCTAカードを生成する。

出力: dev/5-finance-manga/assets/ig-cta.png（1080x1350, フィード4:5）
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.patheffects as pe  # noqa: E402
from matplotlib import font_manager  # noqa: E402

OUT = Path(__file__).with_name("ig-cta.png")

for _name in ("Noto Sans CJK JP", "Noto Sans JP", "IPAexGothic",
              "Meiryo", "Yu Gothic", "MS Gothic", "Hiragino Sans"):
    try:
        if font_manager.findfont(_name, fallback_to_default=False):
            matplotlib.rcParams["font.family"] = _name
            break
    except Exception:  # noqa: BLE001
        continue

BG = "#16233a"
ACCENT = "#e0b64d"
WHITE = "#f6f8fc"
MUTE = "#8f9bb0"

W, H = 1080, 1350
fig = plt.figure(figsize=(W / 200, H / 200), dpi=200)
ax = fig.add_axes([0, 0, 1, 1])
ax.axis("off")
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.add_patch(plt.Rectangle((0, 0), 1, 1, color=BG))
ax.add_patch(plt.Rectangle((0, 0), 1, 0.016, color=ACCENT))
ax.add_patch(plt.Rectangle((0.5 - 0.06, 0.70), 0.12, 0.012, color=ACCENT))

ax.text(0.5, 0.78, "中学生からの金融の授業", fontsize=15, color=MUTE,
        ha="center", va="center")

t = ax.text(0.5, 0.60, "続きは note で", fontsize=40, color=WHITE,
            fontweight="bold", ha="center", va="center")
t.set_path_effects([pe.withStroke(linewidth=1.6, foreground=WHITE)])

ax.text(0.5, 0.48, "序章・第1回は無料", fontsize=20, color=WHITE,
        ha="center", va="center")

ax.text(0.5, 0.32, "▶ プロフィールのリンクから", fontsize=18, color=ACCENT,
        ha="center", va="center")

ax.text(0.5, 0.12,
        "お小遣い・ゲーム・推し活のたとえで\n“稼ぐ・守る・増やす” を親子で",
        fontsize=14, color=MUTE, ha="center", va="center", linespacing=1.8)

fig.savefig(OUT, dpi=200, facecolor=BG)
plt.close(fig)
print("saved:", OUT)
