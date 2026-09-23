#!/usr/bin/env python3
"""note マガジン「子育て世代の王道資産形成」の見出し画像を生成する。

出力: dev/7-assets/assets/magazine-cover.png（1280x670 = note推奨の 1.91:1）
サムネイル（make_eyecatch.py）と同じ背景・配色を使う。
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
import numpy as np  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from PIL import Image  # noqa: E402

HERE = Path(__file__).parent
OUT = HERE / "magazine-cover.png"
BG_PATH = HERE / "bg-note.png"

for _name in ("Yu Gothic", "Meiryo", "MS Gothic", "IPAexGothic",
              "Hiragino Sans", "Noto Sans CJK JP", "Noto Sans JP"):
    try:
        if font_manager.findfont(_name, fallback_to_default=False):
            matplotlib.rcParams["font.family"] = _name
            break
    except Exception:  # noqa: BLE001
        continue

BG = "#1c2e2a"       # 深いティールグリーン
ACCENT = "#d4a94f"   # 落ち着いたゴールド
TITLE = "#f5f7f3"
SUB = "#c9d6cf"

W, H = 1280, 670
fig = plt.figure(figsize=(W / 200, H / 200), dpi=200)
ax = fig.add_axes([0, 0, 1, 1])
ax.axis("off")
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)

if BG_PATH.exists():
    img = np.asarray(Image.open(BG_PATH).convert("RGB"))
    ax.imshow(img, extent=[0, 1, 0, 1], aspect="auto", zorder=0)
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, color=BG, alpha=0.55, zorder=1))
else:
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, color=BG, zorder=0))

ax.add_patch(plt.Rectangle((0, 0), 1, 0.02, color=ACCENT, zorder=2))              # 下端ライン
ax.add_patch(plt.Rectangle((0.075, 0.635), 0.075, 0.017, color=ACCENT, zorder=2))  # タイトル上バー

_title = ax.text(0.072, 0.535, "子育て世代の王道資産形成",
                 fontsize=25, color=TITLE, fontweight="bold", va="center", zorder=3)
_title.set_path_effects([pe.withStroke(linewidth=1.4, foreground=TITLE)])

ax.text(0.075, 0.43,
        "【月5万円】我慢しない家計管理と、失敗しない資産形成の王道",
        fontsize=11.5, color=SUB, va="center", zorder=3)

fig.savefig(OUT, dpi=200, facecolor=BG)
plt.close(fig)
print(f"saved: {OUT} ({W}x{H})")
