# Threads 自動投稿 — 現行構成の棚卸し

> 稼働中の仕組みをここに書き出す。移行判断のための現状把握。

## 現状（記入）

- **アカウント**: @【要確認】（`threads-app` は投稿先アカウント名を設定に持たない。認証トークンに紐づく1アカウント運用）
- **投稿頻度**: 1日2本（午前・午後、JST）
- **投稿時間**: cron-job.org 側の設定次第（`threads-app` 自体はスケジュールを持たない）
- **実行環境**: GitHub Actions（`workflow_dispatch`）。内蔵の `schedule` は遅延が大きいため使わず、
  外部cronサービス **cron-job.org** から1日2回キックする方式
- **スクリプトの所在**: `C:\Claude\プライベート\投資\threads-app`（Basel とは別リポジトリ。
  `note-app` / `stock-app` と同じユーザーが運営する共通基盤の一部）
- **投稿の仕組み**: **Meta公式 Threads API**（`https://graph.threads.net`）。
  コンテナ作成→（`_wait_until_ready`でポーリング）→公開、の2段階
- **認証方式**: Meta for Developers のユーザートークン生成ツールで発行した60日長期トークン
  （通常のOAuth短期→交換フローとは別物）。`threads_auth`（Supabase）に保存し、
  投稿の都度、期限が近ければ `threads_client.py` が自動更新
- **投稿ネタの供給元**: **RSS＋Claude自動生成**（`common/rss.py` のフィード→Claude API で要約・
  コメント生成）。**`marketing/threads/queue.md` は読んでいない**（Basel固有の告知はここに
  含まれず、別途手動投稿が必要）
- **テーマ・note誘導のローテーション**: DBの投稿件数から決定的に算出（`common/rotation.py`）。
  テーマは 経済→投資→フリーランス→Claude を4件ごとに循環、3件に1回 note.com へ一般的な誘導を挿入
  （**Basel各部の特定記事への誘導ではない**）
- **承認フロー**: なし。生成→即時公開が完全自動（Streamlit画面は投稿履歴の閲覧のみ）
- **永続化**: 他アプリと共有の Supabaseプロジェクト（`threads_auth` / `threads_posts`）

## 規約チェック

- [x] 使っている投稿方式は Meta の規約で許可されているか → **公式 Threads API**（`threads_basic` /
  `threads_content_publish` スコープ、Threadsテスター登録済み）なので問題なし
- [x] 大量・機械的投稿とみなされる頻度になっていないか → 1日2本（午前・午後）で低リスク
- [x] トークン・認証情報がリポジトリにコミットされていないか → `.env` は `.gitignore` 済み・
  未トラック確認済み（2026-09-05）。トークン自体はSupabaseの `threads_auth` に保存

## 会社化にあたっての方針

- **公式APIなのでこのまま継続**（移行不要）。ただし現状は Basel の `queue.md` と完全に独立した
  別物の仕組み（RSS×Claudeで経済/投資/フリーランス/Claudeねたを自動生成・自動投稿）で、
  Basel各部（開発2/3/5部）の告知は乗っていない
- 選択肢:
  1. **このまま2本立てで運用**（自動＝汎用ねた保険、queue.md＝Basel各部の告知は手動投稿）
  2. `threads-app` の note誘導ロジック（3件に1回）に Basel の `queue.md` を読ませて統合する
     （要改修。効果が見えてから検討でよい）
- 当面は 1. で運用し、手動投稿の手間が無視できなくなったら 2. を検討

## 移行後の連携

- 投稿ネタ: `marketing/threads/queue.md` に集約 → `social-writer` がカレンダー化 → スクリプトはそのカレンダーを読む
- 実績: 週次で `marketing/threads/log.csv` に記録
