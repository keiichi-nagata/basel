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
- `affiliates.json` — 配信サービス名→アフィリLPのURL。URLを入れるとその週から配信欄が自動でリンク化（`[PR]`付き）。空＝「提携準備中」表示
- `pipeline/collect.py` — 自動収集スクリプト（+ `requirements.txt`）
- `data/` — 週次の生データ＋スコア内訳（`YYYY-Www.json`）
- `data/inputs/` — 自動取得が失敗したときの手動フォールバック（`inputs/README.md`）
- `drafts/` — `YYYY-Www.md`（本文下書き、`ranking-writer` が分析を追記）＋ `YYYY-Www.png`（note/SNS貼付用のランキング表画像）
- `published/` — `YYYY-Www.md`（公開済みのメタ記録）

## note への貼り方

- ランキング表は `drafts/YYYY-Www.png` を画像として貼る（Markdownの表はnoteで崩れる）。同じ画像を Threads/Instagram にも流用。
- 各作品の詳細・アフィリリンクは `drafts/YYYY-Www.md` の各作品セクションをそのまま本文に。
- 冒頭の「本記事はアフィリエイト広告（PR）を含みます」は、アフィリリンクを含む号では景表法（ステマ規制）上**必須**。テンプレに常時入れておく。

## 実行

- 自動: `.github/workflows/drama-weekly.yml`（毎週月曜 06:00 JST → レビュー用PRを作成）
- 手動: Actions タブ → drama-weekly → Run workflow、またはローカルで
  `python dev/3-drama/pipeline/collect.py`（`.env` に `TMDB_API_TOKEN`）

## ワークフロー

`sop/ranking-magazine-workflow.md`＋`sources.md` のパイプライン節に従う。要点:

1. 週次 routine が `collect.*` を実行 → `data/YYYY-Www.json` と `drafts/YYYY-Www.md`（分析欄は空）
2. `ranking-writer` が各作品のあらすじ要約・人気の理由・定点観測を執筆、要確認箇所に `【要確認】`
3. 社長レビュー: 順位・作品名・話数・配信状況・出典を照合、ネタバレ配慮、広告表記
4. note公開 → SNS文面を `marketing/threads/queue.md` へ
5. `published/` にメタ記録、初速を `finance/kpi.csv` へ

## 独自の切り口（AIに任せない = このマガジンの価値）

**「リアタイ型」か「見逃し・配信型」か。** TVer順位（見逃し視聴の強さ）と、放送直後のGoogleトレンドの立ち上がり方を突き合わせ、各作品が本放送で見られているか後追いで伸びているかを毎週同じ枠で分析する。v2で個人視聴率が入ると精度が上がる。
