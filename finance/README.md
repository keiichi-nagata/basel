# 経理部

## 役割

SNS由来の収益とコストを管理する。KPIは週次、PLは月次。
確定申告は青色（承認済み）。実際の記帳は会計ソフト（freee / マネーフォワード等）で行い、
本リポジトリは「速報値と分析」を担う。会計ソフトが正、リポジトリは経営判断用。

## ファイル

- `ledger.csv` — 売上・経費の明細（速報。月末に会計ソフトへ突合）
- `kpi.csv` — ファネル数値（週次）
- `reports/YYYY-MM.md` — 月次PLと振り返り

## 売上カテゴリ

- `paid_note` — 有料note販売（開発1部）
- `affiliate` — アフィリエイト報酬（ASP別に memo へ）
- `other` — その他

## 経費カテゴリ（家事按分が要るものは memo に按分率）

- `ai_api` — Claude / API 利用料
- `tools` — スケジューラ、デザイン、ドメイン等のサブスク
- `infra` — サーバ / ホスティング
- `books_research` — 資料・書籍
- `fees` — 振込・決済手数料
- `other`

## 週次（月曜）

1. `bookkeeper` に前週の `ledger.csv` 追加分と `marketing/threads/log.csv`、各部の初速メモを集計させる
2. `kpi.csv` に1行追加
3. 各ファネル段の「率」を出し、最小の段を STATE.md の「今週の焦点」に反映

## 月次（月初）

1. 前月の `ledger.csv` を締め、会計ソフトと突合
2. `reports/YYYY-MM.md` を生成（売上/経費/利益、KPI推移、次月の打ち手）
3. インボイス: 現状は免税事業者の想定。ASP報酬や取引先の要請で必要が出たら見直し。

## ダッシュボード（Phase 2 で着手・`docs/roadmap-90days.md`）

`finance/dashboard.html` を `bookkeeper` が週次・月次の締めで再生成する。`ledger.csv` /
`kpi.csv` を読む1枚もの（部門別P&L・ファネル率・週次トレンド・各部の稼働状態・
今週のボトルネック）。リアルタイムではなく「最終記帳時点」の鮮度。着手条件は実データ4週間ぶん。
