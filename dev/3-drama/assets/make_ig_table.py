#!/usr/bin/env python3
"""開発3部 — Instagram用（4:5・1080x1350）のTOP5ランキング表を生成する。

note/Threads用の横長表（`pipeline/collect.py` の render_png）はIGだと文字が
小さくなりすぎるため、IGはTOP5に絞った縦長版を使う。マガジン表紙
（`assets/make_cover.py`）と同じダーク配色。

使い方:
  python dev/3-drama/assets/make_ig_table.py 2026-W36
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

DRAMA_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = DRAMA_DIR / "data"
DRAFT_DIR = DRAMA_DIR / "drafts"

BG = "#14171d"
PANEL = "#1e232c"
ACCENT = "#e5484d"
TITLE = "#f5f7fa"
SUB = "#aeb7c4"
MUTE = "#79828f"


def _jp_font() -> str | None:
    from matplotlib import font_manager

    for name in ("Noto Sans CJK JP", "Noto Sans JP", "IPAexGothic", "IPAGothic",
                 "TakaoPGothic", "Yu Gothic", "Meiryo", "MS Gothic", "Hiragino Sans"):
        try:
            if font_manager.findfont(name, fallback_to_default=False):
                return name
        except Exception:  # noqa: BLE001
            continue
    return None


def _short(title: str, n: int = 16) -> str:
    return title if len(title) <= n else title[: n - 1] + "…"


def render(data: dict, out_path: Path) -> bool:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        font = _jp_font()
        if font:
            matplotlib.rcParams["font.family"] = font

        wk = data["week"].replace("2026-W", "第") + "週"
        rng = data.get("range", {})
        sub = f"{rng.get('from', '')} 〜 {rng.get('to', '')}"
        items = data["items"][:5]

        W, H = 1080, 1350
        fig = plt.figure(figsize=(W / 200, H / 200), dpi=200)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.axis("off")
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.add_patch(plt.Rectangle((0, 0), 1, 1, color=BG))
        ax.add_patch(plt.Rectangle((0, 0), 1, 0.015, color=ACCENT))

        ax.text(0.07, 0.93, "話題のドラマ 総合ランキング", fontsize=21, color=TITLE,
                fontweight="bold", va="center")
        ax.text(0.07, 0.885, f"2026年 {wk}（{sub}）", fontsize=12, color=SUB, va="center")
        ax.text(0.07, 0.855, "TVer週間 × Netflix Japan Top10 × Google検索トレンド の合成指標",
                fontsize=10, color=MUTE, va="center")

        # 行
        top_y, row_h = 0.78, 0.135
        for i, it in enumerate(items):
            y = top_y - i * row_h
            ax.add_patch(plt.Rectangle((0.05, y - row_h * 0.42), 0.90, row_h * 0.84,
                                        color=PANEL, zorder=1))
            ax.text(0.10, y, str(it["rank"]), fontsize=26, color=ACCENT,
                    fontweight="bold", va="center", ha="center")
            ax.text(0.17, y + 0.018, _short(it["title"]), fontsize=16, color=TITLE,
                    fontweight="bold", va="center")
            a = it["components"]["A_tver"]
            b = it["components"]["B_netflix"]
            c = it["components"]["C_trends"]
            parts = [f"合成 {it['composite_score']:.0f}",
                     f"TVer {a['rank']}位" if a else "TVer —",
                     f"Netflix {b['rank']}位" if b else "Netflix —",
                     f"トレンド {c:.0f}" if c is not None else "トレンド —"]
            ax.text(0.17, y - 0.028, "  /  ".join(parts), fontsize=10.5, color=SUB, va="center")

        ax.text(0.07, 0.10, "6〜10位と各作品の解説はプロフィールのリンクから（note）",
                fontsize=11, color=SUB, va="center")
        ax.text(0.07, 0.065, "※横断的な視聴数ではなく「話題度」の合成指標です",
                fontsize=9, color=MUTE, va="center")

        fig.savefig(out_path, dpi=200, facecolor=BG)
        plt.close(fig)
        print("saved:", out_path)
        return True
    except Exception as exc:  # noqa: BLE001
        print(f"[ig] 生成失敗: {exc}")
        return False


def main() -> int:
    if len(sys.argv) < 2:
        print("使い方: python make_ig_table.py 2026-Www")
        return 1
    week = sys.argv[1]
    p = DATA_DIR / f"{week}.json"
    if not p.exists():
        print(f"データが見つかりません: {p}")
        return 1
    data = json.loads(p.read_text(encoding="utf-8"))
    ok = render(data, DRAFT_DIR / f"{week}-ig.png")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
