# Threads 自動投稿 — 現行構成の棚卸し

> 稼働中の仕組みをここに書き出す。移行判断のための現状把握。

## 現状（記入）

- **アカウント**: @【要確認】（`threads-app` は投稿先アカウント名を設定に持たない。認証トークンに紐づく1アカウント運用）
- **管理画面（Streamlit）**: https://investment-apps-2y8upkj8jzy75k4xtykzpy.streamlit.app/
  （投稿履歴の確認・「承認待ち」ページはここ）
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

- **公式APIなのでこのまま継続**（移行不要）。1日2本の自動投稿（経済/投資/フリーランス/Claudeねた）
  はそのまま。Basel各部の告知は下の「承認キュー」経由で同じ投稿基盤に相乗りする形にした
  （2026-09-05、`decision`不要の実装タスクとして実施）

## 開発部の告知 → 承認 → 自動投稿（2026-09-05 実装）

Basel で記事/アプリを公開したら、この経路で告知できる:

1. Claude が告知文を作成（`marketing/threads/queue.md` に記載するのと同時に）
2. `python marketing/threads/queue_to_pending.py --source "basel:<部>:<回>" --content "..." --link "URL"`
   で threads-app の Supabase（`manual_posts`テーブル、status=pending）に登録
   - Supabase接続情報は threads-app の `.env` をそのまま読む（Baselには複製しない）
3. 社長が threads-app の Streamlit画面「承認待ち」ページで内容を確認し、
   **「承認して投稿」を押すと、既存の `threads_client.post()`（公式Threads API）でその場で投稿**
   - 却下も可（status=rejected のまま残る。再送するなら手動でThreads投稿）
4. 投稿後は `threads_posts`（投稿履歴）にも記録され、トップページの履歴一覧にも出る

1日2回の自動生成投稿とは完全に独立（お互いのcron・ロジックに影響しない）。

**導入時に一度だけ必要な作業（社長）**:
- [ ] threads-app の Supabase SQL Editor で `supabase_schema.sql` の `manual_posts` テーブル作成分を実行
- [ ] Streamlit アプリ（threads-app）を再デプロイ／再起動して `pages/1_承認待ち.py` を反映
- [ ] テスト投稿1件（`queue_to_pending.py` → Streamlitで承認）して一連の流れを確認

## 移行後の連携

- 投稿ネタ: `marketing/threads/queue.md` に集約 → `social-writer` がカレンダー化。実際の投稿は
  上記の承認キュー経由（Threads自動投稿本体の改修は不要）
- 実績: 週次で `marketing/threads/log.csv` に記録
