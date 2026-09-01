#!/usr/bin/env python3
"""序章のMidjourney不要パーツを生成する。

出力:
  dev/5-finance-manga/assets/00/zu1-umaibou.png  … 図1 うまい棒の値段のうつりかわり
  dev/5-finance-manga/assets/00/shime.png        … 締めコマ（黒背景＋白文字）

文言・色を変えたら実行し直す。note には他のコマ画像と一緒に縦スクロールで貼る。
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.patheffects as pe  # noqa: E402
from matplotlib import font_manager  # noqa: E402

OUT = Path(__file__).with_name("00")
OUT.mkdir(parents=True, exist_ok=True)

for _name in ("Noto Sans CJK JP", "Noto Sans JP", "IPAexGothic",
              "Meiryo", "Yu Gothic", "MS Gothic", "Hiragino Sans"):
    try:
        if font_manager.findfont(_name, fallback_to_default=False):
            matplotlib.rcParams["font.family"] = _name
            break
    except Exception:  # noqa: BLE001
        continue


# ---------------------------------------------------------------- 図1 うまい棒
def zu1() -> None:
    ink = "#1f2937"
    paper = "#fbf7ee"
    jump = "#e0824d"      # 値上げの強調色
    flat = "#9aa5b1"      # 据え置き区間

    W, H = 1080, 780
    fig = plt.figure(figsize=(W / 200, H / 200), dpi=200)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, color=paper))

    ax.text(0.06, 0.90, "うまい棒の値段のうつりかわり",
            fontsize=22, color=ink, fontweight="bold", va="center")

    # 時間軸（意図的に圧縮：42年ぶんは長く、2年半ぶんは詰める）
    y = 0.58
    x0, x1, x2, x3 = 0.08, 0.58, 0.71, 0.88
    ax.plot([x0, x1], [y, y], color=flat, lw=9, solid_capstyle="round")
    ax.plot([x1, x2], [y, y], color=jump, lw=9, solid_capstyle="round")
    ax.plot([x2, x3], [y, y], color=jump, lw=9, solid_capstyle="round")
    for x in (x1, x2):
        ax.plot([x], [y], marker="o", ms=15, color=jump, zorder=5)

    # 価格（線の上）
    ax.text(x0, y + 0.13, "10円", fontsize=27, color=ink, fontweight="bold",
            ha="left", va="center")
    ax.text(x1, y + 0.13, "12円", fontsize=27, color=ink, fontweight="bold",
            ha="center", va="center")
    ax.text(0.95, y + 0.13, "15円", fontsize=31, color=jump, fontweight="bold",
            ha="right", va="center")

    # 年（線の下）
    def yr(x, text, ha="center"):
        ax.text(x, y - 0.11, text, fontsize=12.5, color=ink, ha=ha, va="center")
    yr((x0 + x1) / 2, "1979〜2022年（約42年）")
    yr(x1, "2022年4月")
    yr(x3, "2024年10月", ha="right")

    ax.text(0.06, 0.30,
            "42年ずっと10円 → たった2年半で2回値上げ",
            fontsize=17, color=jump, fontweight="bold", va="center")
    ax.text(0.06, 0.15,
            "＝ 同じ10円玉では、うまい棒が買えなくなった",
            fontsize=16, color=ink, va="center")

    fig.savefig(OUT / "zu1-umaibou.png", dpi=200, facecolor=paper)
    plt.close(fig)
    print("saved:", OUT / "zu1-umaibou.png")


# ------------------------------------------------------------- 締めコマ
def shime() -> None:
    bg = "#14171d"
    accent = "#e0b64d"
    white = "#f6f8fc"
    mute = "#8a94a3"

    W, H = 1080, 1350
    fig = plt.figure(figsize=(W / 200, H / 200), dpi=200)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, color=bg))
    ax.add_patch(plt.Rectangle((0.5 - 0.07, 0.635), 0.14, 0.007, color=accent))

    t = ax.text(0.5, 0.52,
                "未来の自分に10万円を託すなら、\nどこに置きますか？",
                fontsize=23, color=white, fontweight="bold",
                ha="center", va="center", linespacing=1.6)
    t.set_path_effects([pe.withStroke(linewidth=1.2, foreground=white)])

    ax.text(0.5, 0.37, "次回から、一緒に考えていきます。",
            fontsize=15, color=mute, ha="center", va="center")

    ax.add_patch(plt.Rectangle((0, 0), 1, 0.02, color=accent))
    ax.text(0.5, 0.115,
            "『未来の自分に10万円を託す』\n中学生からの金融の授業 ｜ マガジンをフォローで更新通知",
            fontsize=12, color=mute, ha="center", va="center", linespacing=1.9)

    fig.savefig(OUT / "shime.png", dpi=200, facecolor=bg)
    plt.close(fig)
    print("saved:", OUT / "shime.png")


# -------------------------------------------------- 第1回 図1「2つの稼ぎ方」
def zu_two_ways() -> None:
    out = Path(__file__).with_name("01")
    out.mkdir(parents=True, exist_ok=True)
    ink = "#1f2937"
    paper = "#fbf7ee"
    left_c = "#5b7a99"    # 労働＝落ち着いた青
    right_c = "#d99b3d"   # 投資＝ゴールド
    band = "#16233a"

    W, H = 1080, 820
    fig = plt.figure(figsize=(W / 200, H / 200), dpi=200)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, color=paper))
    ax.text(0.5, 0.93, "2つの稼ぎ方", fontsize=24, color=ink,
            fontweight="bold", ha="center", va="center")

    # 中央の仕切り
    ax.plot([0.5, 0.5], [0.16, 0.84], color="#d8d2c4", lw=2)

    def column(cx, color, head, sub, icon, bullets):
        ax.text(cx, 0.80, head, fontsize=19, color=color, fontweight="bold",
                ha="center", va="center")
        ax.text(cx, 0.745, sub, fontsize=12, color=ink, ha="center", va="center")
        icon(cx, 0.62)
        for i, b in enumerate(bullets):
            ax.text(cx, 0.45 - i * 0.09, "・" + b, fontsize=14, color=ink,
                    ha="center", va="center")

    def person(cx, cy):
        ax.add_patch(plt.Circle((cx, cy + 0.055), 0.028, color=left_c))
        ax.add_patch(plt.Polygon([[cx - 0.055, cy - 0.06], [cx + 0.055, cy - 0.06],
                                  [cx + 0.035, cy + 0.02], [cx - 0.035, cy + 0.02]],
                                 closed=True, color=left_c))

    def coins(cx, cy):
        for k, dx in enumerate((-0.05, 0.0, 0.05)):
            ax.add_patch(plt.Circle((cx + dx, cy - 0.02 + k * 0.012), 0.033,
                                    color=right_c, ec=paper, lw=2))
        ax.text(cx + 0.05, cy + 0.0, "¥", fontsize=15, color=paper,
                ha="center", va="center", fontweight="bold")

    column(0.25, left_c, "自分が働く", "（労働収入）", person,
           ["時間と体力を使う", "1日24時間まで", "休むと止まる"])
    column(0.75, right_c, "お金に働いてもらう", "（投資収入）", coins,
           ["お金がお金を生む", "いくつも“働き手”を持てる", "休んでも動く"])

    ax.add_patch(plt.Rectangle((0.08, 0.05), 0.84, 0.08, color=band))
    ax.text(0.5, 0.09, "両方を使うのが、お金の育て方",
            fontsize=16, color=paper, fontweight="bold", ha="center", va="center")

    fig.savefig(out / "zu1-two-ways.png", dpi=200, facecolor=paper)
    plt.close(fig)
    print("saved:", out / "zu1-two-ways.png")


if __name__ == "__main__":
    import sys
    if "01" in sys.argv:
        zu_two_ways()
    else:
        zu1()
        shime()
