# SOP — 開発2部 月次車ランキングの制作フロー

頻度: 毎月1本。実行の目安は**毎月8日ごろ**（自販連・全軽自協の前月データ公表＝6日前後 ＋ 数日の余裕）。

## 1. データを貼る（約10分・手動）

- 自販連の月報PDF（車名別・登録車）と全軽自協のPDF（車名別・軽）を開く（`dev/2-cars/sources.md`）
- 上位（登録車10〜15件／軽8〜10件）を `dev/2-cars/data/inputs/YYYY-MM.json` に貼る（`inputs/README.md` の形）
  - `YYYY-MM` は前月
- 出典URL・公表日も同ファイルに記入

## 2. 組み立て（自動）

```
python dev/2-cars/pipeline/collect.py            # 前月を対象
python dev/2-cars/pipeline/collect.py 2026-08    # 月を明示
```

→ `data/YYYY-MM.json`（総合TOP5・価格結合・前月比）と `drafts/YYYY-MM.md`（表入り・分析欄は空）を生成。
- `⚠️ 価格未登録` が出たら、メーカー公式で最安グレード価格を確認して `dev/2-cars/prices.json` に追記 → collect.py を再実行

## 3. 執筆（`car-column-writer` エージェント / または Claude Code に直接依頼）

- 「`dev/2-cars/drafts/YYYY-MM.md` の `【car-column-writer 記入】` を `sop/car-column-workflow.md` と `.claude/agents/car-column-writer.md` に沿って書いて」
- 各車の「なぜ売れた/落ちた」は WebSearch で確認（一部改良・MC・補助金・為替など）
- 「働き方・投資への示唆」は必須要素（地味な改善の具体例／積立・複利／問いかけ＋行動）を満たす

## 4. 社長レビュー（公開前・必須）

- [ ] 台数・順位・前年同月比が `data/YYYY-MM.json`（＝一次PDF）と一致
- [ ] `【要確認】` `【価格要確認】` を解消（数字・価格・改良の事実）
- [ ] 「自販連・全軽自協発表の統計をもとに集計」の注記がある。他サイトの表を転載していない
- [ ] 投資の話が一般論の範囲（特定銘柄・商品の推奨や個別助言になっていない）
- [ ] 「働き方・投資への示唆」が抽象論で終わっていない（具体例・行動喚起がある）
- [ ] アフィリンクを入れた号は冒頭に広告表記（`sop/disclosure.md`）

## 5. 公開・記録

- `sop/publish-note.md` に沿ってnote公開、マガジンに追加
- `dev/2-cars/published/YYYY-MM.md` に URL・公開時刻・初速メモ
- SNS文面を `marketing/threads/queue.md` / `marketing/instagram/queue.md` へ
- 公開48時間後の初速を published に記録 → 週次で `finance/kpi.csv`

## 品質の下限

- 出典のない数字を書かない。順位は必ずデータ由来
- 「AIが書いた一般論」だけの考察は不可。毎号「車 → 働き方・投資」の接続を必ず入れる（＝独自の切り口）
