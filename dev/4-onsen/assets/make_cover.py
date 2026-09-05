#!/usr/bin/env python3
"""note マガジン「エリア別 温泉宿ランキング（月刊）」の見出し画像を生成する。

出力: dev/4-onsen/assets/magazine-cover.png（1280x670 = note推奨の 1.91:1）
他部（開発3部・5部）は暗い配色だが、この部は**明るい配色**で差別化する
（温泉の湯気・あたたかさをイメージした暖色系）。
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

BG = "#fdf1e3"      # 温泉の湯気をイメージした明るいクリーム色
ACCENT = "#e2703a"  # あたたかみのあるテラコッタ・オレンジ
TITLE = "#3a2c22"   # 明るい背景に映える濃い暖色ブラウン
SUB = "#8a6d55"
MUTE = "#b9a48d"

W, H = 1280, 670
fig = plt.figure(figsize=(W / 200, H / 200), dpi=200)
ax = fig.add_axes([0, 0, 1, 1])
ax.axis("off")
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)

ax.add_patch(plt.Rectangle((0, 0), 1, 1, color=BG))
ax.add_patch(plt.Rectangle((0, 0), 1, 0.02, color=ACCENT))          # 下端ライン（SNS用）
# マガジントップは中央の細い横帯（おおよそ y=0.33〜0.67）だけ表示される。
# タイトル＋タグラインをその中に収める。
ax.add_patch(plt.Rectangle((0.075, 0.635), 0.075, 0.017, color=ACCENT))  # タイトル上バー

_title = ax.text(0.072, 0.535, "エリア別 温泉宿ランキング",
                 fontsize=28, color=TITLE, fontweight="bold", va="center")
_title.set_path_effects([pe.withStroke(linewidth=1.4, foreground=TITLE)])

ax.text(0.075, 0.43,
        "楽天トラベル×じゃらんの独自採点で、毎月1エリアの宿TOP5を紹介",
        fontsize=12, color=SUB, va="center")

# 安全帯の外（SNSシェア時のみ見える）
ax.text(0.075, 0.23, "毎月更新   ｜   無料マガジン",
        fontsize=11, color=MUTE, va="center")

fig.savefig(OUT, dpi=200, facecolor=BG)
plt.close(fig)
print(f"saved: {OUT} ({W}x{H})")
