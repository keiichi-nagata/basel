# SOP — 既存事業の引き継ぎ（会社化の初期タスク）

個々に走っている活動を、このリポジトリの運営に一本化するための手順。1回だけ実施。

## 1. リポジトリを基点にする

- [x] `git init` 済み
- [ ] 初回コミット（雛形一式）
- [ ] リモート（GitHub のプライベートリポジトリ）を作成して push
- [ ] 毎作業後にコミットする習慣（最低: 公開のたびに1コミット）

## 2. 開発1部（有料note 4本 + 5本目）

- [ ] `dev/1-apps/catalog.md` の一覧表に4本を記入（タイトル/公開日/価格/URL/対象リポジトリ）
- [ ] 各noteの詳細テンプレを埋める（サポート範囲・陳腐化リスク）
- [ ] 対象アプリのソースがローカルにあるなら `dev/1-apps/pipeline/<app名>/` に整理 or 別リポジトリのURLを記録
- [ ] 5本目は `pipeline/` で作業し、`sop/publish-note.md` の手順で公開
- [ ] 既存4本の累計販売数・売上を `catalog.md` と `finance/ledger.csv` に記録

## 3. 開発2部（車note 1本・単発・アフィリなし）

- [ ] `dev/2-cars/published/0001-first-note.md` を記入
- [ ] note側でマガジンを新規作成し、この記事を追加（単発 → マガジン）
- [ ] 次号(#2)から `sop/ranking-magazine-workflow.md` の型で運用
- [ ] アフィリを入れるなら: 相性の良いA8案件を1つ提携 → 冒頭に広告表記を追記

## 4. 開発3部（準備中）＝ 今期MVP

- [ ] `dev/3-drama/sources.md` のデータソースを1つに決める（規約確認）
- [ ] A8.net でVOD案件を1つ提携申請
- [ ] `dev/3-drama/README.md` の「独自の切り口」を1つ決めて記入
- [ ] 1本目を `drafts/` で手動作成 → 公開 → `published/` に記録

## 5. マーケ部（Threads 自動投稿 1日2本・稼働中）

- [ ] `marketing/threads/config.md` に現行構成を書き出す
- [ ] 投稿方式が公式API/公認ツールか確認。非公式なら移行タスクを STATE.md に起票
- [ ] 認証情報がリポジトリにコミットされていないか確認（`.gitignore` 済みだが実ファイルの位置も確認）
- [ ] 投稿ネタの供給を `marketing/threads/queue.md` に一本化
- [ ] 既存の投稿実績（あれば）を `marketing/threads/log.csv` にインポート

## 6. 経理部

- [ ] 事業用口座・カードの直近明細から `finance/ledger.csv` に売上・経費を入力
- [ ] 会計ソフトを1つ決める（未導入なら）。青色65万控除は e-Tax 前提
- [ ] 直近のASP（A8）管理画面の確定報酬を `ledger.csv` に記録
- [ ] `finance/kpi.csv` にベースライン（現在のフォロワー数・直近のnote閲覧）を1行入れる

## 7. アカウント棚卸し

- [ ] note / Threads / Instagram の URL・ハンドルを STATE.md に記入
- [ ] Instagram をプロアカウント化（運用開始は3部の後でよいが、切替だけ先にやっておくと後が楽）
- [ ] もしもアフィリエイト の登録申請（Amazon/楽天リンクを使う布石）

## 完了の定義

STATE.md の「資産インベントリ」が実データで埋まり、`finance/ledger.csv` と `kpi.csv` に
最低1行ずつ実データが入り、初回コミットが GitHub に push されている。
