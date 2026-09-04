# 開発2部 — 新車販売台数ランキング & 働き方・投資コラム

## 成果物

月次・無料note（マガジン）。「車種別TOP5 → 各車の理由 → 共通構造 → 働き方・投資への示唆」の
エッセイ型。アフィリンクは当面なし（入れるなら保険・書籍・生活系を1〜2個・広告表記つき）。

## 更新サイクル

- 毎月8日ごろ（自販連・全軽自協の前月データ公表＝6日前後 ＋ 数日の余裕）
- 手順: `sop/car-column-workflow.md`

## パイプライン

1. **組み立て**（自動）: `python dev/2-cars/pipeline/collect.py [YYYY-MM]`
   → 自販連（登録車エクセル）・全軽自協（軽の速報テーブル/xls）をDL・解析
   → 登録車＋軽を台数降順にして総合TOP5 → `prices.json` の価格を結合 → 前月比を算出
   → `data/YYYY-MM.json` と `drafts/YYYY-MM.md`（表入り・分析欄は空）
   （毎月8日ごろ GitHub Actions `cars-monthly` が実行して PR を開く）
2. **取得失敗時のみ**: `data/inputs/YYYY-MM.json` に車名別上位を手貼りして再実行（`sources.md` 参照）
3. **執筆**: `car-column-writer` エージェントが各車の理由（WebSearch）・共通構造・示唆を執筆
4. **レビュー → note公開 → マガジン追加 → `published/YYYY-MM.md` 記録**

## フォルダ

- `sources.md` — データソース（自販連/全軽自協/価格）と運用（確定版）
- `template.md` — 記事の型（7セクション固定）
- `prices.json` — 車名 → 最安グレード価格の蓄積（TOP5に未登録なら記事に `【価格要確認】`）
- `affiliates.json` — 車関連アフィリンク（A8/afb で提携 → url を貼ると毎号の下書きに広告表記＋関連リンク節を自動挿入）
- `pipeline/collect.py` — 自販連/全軽自協からエクセルを取得 → 総合TOP5を組み立て
- `pipeline/requirements.txt` — `requests` / `openpyxl` / `xlrd==1.2.0`（旧 .xls 用）
- `data/inputs/` — 取得失敗時の手動フォールバック（`YYYY-MM.json`。`2026-07.json` が例）
- `data/` — `YYYY-MM.json`（生成データ。前月比の計算に使う）
- `drafts/` — `YYYY-MM.md`（下書き）
- `published/` — `YYYY-MM.md`（公開記録）
- `2026年7月_車種別販売台数ランキングTOP5.md` — 第1回の記事本文（新フォーマットの見本）
- `自動化指示書_note下書き生成.md` — 元の指示書（内容は上記に反映済み）

## 独自の切り口（毎号）

TOP5に共通する構造 → フリーランスの働き方（地味な改善の積み重ね）・積立/複利の投資判断、への接続。
