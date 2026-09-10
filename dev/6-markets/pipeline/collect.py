#!/usr/bin/env python3
"""開発6部 — 資産クラス別 月間リターンランキングのデータ収集。

`universe.json` の各資産クラス（東京市場の円建てETF等）について、
対象月の月末終値と前月末終値から月間リターンを計算し、年初来リターンも添えて
`dev/6-markets/data/YYYY-MM.json` に保存する。

- 為替換算はしない（対象はすべて円建て銘柄）。分配金は含まない＝価格リターン。
- 他サイトのランキング表は使わない。終値から自分で計算する（出典＝各ティッカーの市場終値）。

使い方:
  python dev/6-markets/pipeline/collect.py 2026-08
  python dev/6-markets/pipeline/collect.py            # 前月を自動で対象にする
"""
from __future__ import annotations

import json
import sys
from datetime import date, datetime
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
UNIVERSE = BASE / "universe.json"
DATA_DIR = BASE / "data"


def _target_month(argv: list[str]) -> str:
    if len(argv) >= 2:
        return argv[1]
    today = date.today()
    y, m = (today.year, today.month - 1) if today.month > 1 else (today.year - 1, 12)
    return f"{y:04d}-{m:02d}"


def _prev_month(ym: str) -> str:
    y, m = (int(x) for x in ym.split("-"))
    y, m = (y, m - 1) if m > 1 else (y - 1, 12)
    return f"{y:04d}-{m:02d}"


def main() -> int:
    month = _target_month(sys.argv)
    y, m = (int(x) for x in month.split("-"))
    prev = _prev_month(month)
    py = int(prev.split("-")[0])

    try:
        import pandas as pd
        import yfinance as yf
    except Exception as exc:  # noqa: BLE001
        print(f"依存関係が読めません（pip install yfinance pandas）: {exc}")
        return 1

    uni = json.loads(UNIVERSE.read_text(encoding="utf-8"))
    classes = uni["classes"]
    tickers = [c["ticker"] for c in classes]

    # 前々年末〜対象月翌月頭まで取り、月末終値（月次リサンプル）を作る
    start = f"{py - 1}-12-01"
    end_y, end_m = (y, m + 1) if m < 12 else (y + 1, 1)
    end = f"{end_y:04d}-{end_m:02d}-05"
    raw = yf.download(tickers, start=start, end=end, interval="1d",
                      progress=False, auto_adjust=True)
    close = raw["Close"] if "Close" in getattr(raw, "columns", []) else raw
    if isinstance(close, pd.Series):
        close = close.to_frame()
    monthly = close.resample("ME").last()

    def _val(ticker: str, ym: str):
        rows = monthly[monthly.index.strftime("%Y-%m") == ym]
        if rows.empty or ticker not in monthly.columns:
            return None, None
        v = rows[ticker].iloc[0]
        if pd.isna(v):
            return None, None
        return float(v), rows.index[0].strftime("%Y-%m-%d")

    ytd_base_ym = f"{y - 1}-12"
    items = []
    for c in classes:
        t = c["ticker"]
        cur, cur_d = _val(t, month)
        prv, prv_d = _val(t, prev)
        yb, yb_d = _val(t, ytd_base_ym)
        ret = round((cur / prv - 1) * 100, 2) if cur and prv else None
        ytd = round((cur / yb - 1) * 100, 2) if cur and yb else None
        items.append({
            "class_key": c["key"],
            "name": c["name"],
            "ticker": t,
            "tracks": c["tracks"],
            "vehicle": c["vehicle"],
            "month_return_pct": ret,
            "ytd_return_pct": ytd,
            "prev_close": round(prv, 2) if prv else None,
            "month_close": round(cur, 2) if cur else None,
            "prev_close_date": prv_d,
            "month_close_date": cur_d,
            "note": None if ret is not None else "終値が取得できず。ティッカーを再確認【要確認】",
        })

    ranked = sorted((x for x in items if x["month_return_pct"] is not None),
                    key=lambda x: x["month_return_pct"], reverse=True)
    for i, x in enumerate(ranked, 1):
        x["rank"] = i
    missing = [x for x in items if x["month_return_pct"] is None]

    out = {
        "month": month,
        "prev_month": prev,
        "collected_at": datetime.now().strftime("%Y-%m-%d"),
        "methodology": (
            "各資産クラスを代表する東京市場上場の円建てETF等の月末終値をもとに、"
            "前月末→対象月末の騰落率を算出（為替換算なし・分配金を含まない価格リターン）。"
            "年初来は前年12月末終値を基準。出典＝各ティッカーの市場終値（yfinance取得）。"
        ),
        "items": ranked + missing,
    }
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / f"{month}.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"保存: {path}")
    for x in ranked:
        print(f"  {x['rank']:>2}. {x['name']:<14} {x['month_return_pct']:+6.2f}%  (YTD {x['ytd_return_pct']:+.2f}%)")
    for x in missing:
        print(f"  --. {x['name']:<14} 取得失敗 {x['ticker']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
