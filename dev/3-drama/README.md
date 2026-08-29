# 開発3部 — 話題のドラマ総合ランキング & AI分析【今期MVP】

## 成果物

週次・無料note（マガジン）。「話題のドラマ総合ランキング（合成指標）」＋各作品のあらすじ・話数・配信状況・人気の理由AI分析。
アフィリンクは提携済みの配信先のみ（現状ABEMA。詳細は `sources.md` のアフィリ対応表）。

## ランキングの定義（重要）

TVer週間 + Netflix Japan Top10 + Google検索トレンド を各0〜100正規化し、存在する要素の単純平均。
**「視聴されている順番」ではなく「話題度の合成指標」。** 断定表現は使わない。詳細と根拠は `sources.md`、決定経緯は `docs/decisions/0002-drama-ranking-methodology.md`。

## 更新サイクル

- **公開曜日**: （固定する。例: 毎週月曜 12:00）
- 対象期間: 前週（月〜日）
- 所要目安: 収集は自動（月曜早朝の routine）→ `ranking-writer` がドラフト → 社長レビュー10〜30分 → 公開

## フォルダ

- `sources.md` — データソース・合成式・パイプライン設計・アフィリ対応表（確定版）
- `template.md` — note雛形
- `pipeline/` — 自動収集スクリプト（`collect.*`）
- `data/` — 週次の生データ＋スコア内訳（JSONスキーマは `sources.md`）
- `drafts/` — `YYYY-Www.md`（作業中）
- `published/` — `YYYY-Www.md`（公開済みのメタ記録）

## ワークフロー

`sop/ranking-magazine-workflow.md`＋`sources.md` のパイプライン節に従う。要点:

1. 週次 routine が `collect.*` を実行 → `data/YYYY-Www.json` と `drafts/YYYY-Www.md`（分析欄は空）
2. `ranking-writer` が各作品のあらすじ要約・人気の理由・定点観測を執筆、要確認箇所に `【要確認】`
3. 社長レビュー: 順位・作品名・話数・配信状況・出典を照合、ネタバレ配慮、広告表記
4. note公開 → SNS文面を `marketing/threads/queue.md` へ
5. `published/` にメタ記録、初速を `finance/kpi.csv` へ

## 独自の切り口（AIに任せない = このマガジンの価値）

**「リアタイ型」か「見逃し・配信型」か。** TVer順位（見逃し視聴の強さ）と、放送直後のGoogleトレンドの立ち上がり方を突き合わせ、各作品が本放送で見られているか後追いで伸びているかを毎週同じ枠で分析する。v2で個人視聴率が入ると精度が上がる。
