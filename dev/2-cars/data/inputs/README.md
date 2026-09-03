# 手動入力（毎月・約10分）

自販連・全軽自協の月報PDFから、車名別の上位を `YYYY-MM.json` に貼る。

対象月 `YYYY-MM` は**前月**（例: 8日に9月分は出ないので、8日実行なら 8月分＝`2026-08`）。

## `2026-08.json` の形

```json
{
  "month": "2026-08",
  "source_registered": { "url": "自販連 月報PDFのURL", "published": "2026-09-06" },
  "source_kei": { "url": "全軽自協 PDFのURL", "published": "2026-09-05" },
  "registered": [
    { "model": "ヤリス", "maker": "トヨタ", "units": 13679, "yoy_pct": -1.6 },
    { "model": "カローラ", "maker": "トヨタ", "units": 11000, "yoy_pct": 5.2 }
  ],
  "kei": [
    { "model": "N-BOX", "maker": "ホンダ", "units": 22506, "yoy_pct": 34.7 },
    { "model": "スペーシア", "maker": "スズキ", "units": 13883, "yoy_pct": -5.3 }
  ]
}
```

- `registered` = 登録車（乗用車）車名別。上位10〜15件
- `kei` = 軽自動車 車名別。上位8〜10件
- `units` = 台数（整数）、`yoy_pct` = 前年同月比（％。減少はマイナス。「▲5.3%」なら `-5.3`）
- TOP5に入りそうな車種はもれなく。10位以下は入れなくてよい

`collect.py` が登録車＋軽をまとめて台数降順ソート → 総合TOP5 → `prices.json` の価格を結合 →
前月比を算出 → `data/2026-08.json` と `drafts/2026-08.md` を生成する。
