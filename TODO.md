# TODO — 社長の残タスク

やることの一元管理。完了したら `[x]` にして「完了ログ」へ移す。
戦略の全体像は `docs/roadmap-90days.md`、現在地は `STATE.md`。

最終更新: 2026-09-02

---

## 🔁 毎週の定例（くり返し・消さない）

- [ ] **月曜**: 週次締め（`sop/weekly-close.md`）→ KPI更新 → STATE.md 更新 → `planning/ideas.md` 棚卸し
- [ ] **月曜**: 開発3部 — PRブランチを開く → 分析を依頼 → レビュー → note公開（`published/` 記録・PRマージ）
- [ ] **毎日**: Threads 2本（`marketing/threads/queue.md` から）
- [ ] 開発5部 — 1話ずつ制作（脚本は依頼済みが先行。コマ生成＋Canva＋公開）

---

## 🔥 今すぐ / 今週

### 会社全体
- [ ] 未pushのコミットを `git push`
- [ ] `finance/ledger.csv` に直近の売上・経費（有料note5本、Midjourney/Canva等のサブスク）を入力
- [ ] `STATE.md` の「資産インベントリ」空欄（note/Threads/IG のURL・ハンドル、ASP）を実データで埋める
- [ ] `dev/1-apps/catalog.md` に有料note4〜5本の情報を記入（維持モードでも記録は残す）

### 開発3部（ドラマ）
- [ ] 来週月曜、手動2周目（分析執筆→公開）。問題なければ次週 `/schedule` 化
- [ ] もしもアフィリエイト・afb に申請（U-NEXT / Amazon Prime Video 用）

### 開発2部（車）— アフィリエイト
- [x] A8.net で提携申請：akippa（駐車場シェア）／保険スクエアbang!（自動車保険一括見積もり・ウェブクルー）
- [ ] 提携が承認されたら、発行URL（px.a8.net/…）を `dev/2-cars/affiliates.json` の該当 `url` に貼る → 8月号から自動で広告表記＋関連リンクが入る

### 開発5部（金融マンガ）
- [x] 序章の初速を記入（ビュー18 / スキ1 / コメ0）→ 母数が小さい。振り返り欄は引き続き空欄
- [x] 第1回の初速を記入（ビュー9 / スキ0 / コメ0）→ 序章より少ない。導線が弱い可能性、要観察
- [x] 第1回の次回予告文を確認 → 価格の言及なし（内容紹介のみ）のため修正不要と確認済み
- [ ] 第2回の初速・購入数/売上を `published/02.md` に記入（9/7ごろ）
- [x] 第2回をマガジン「中学生からの金融の授業」に追加
- [x] 第2回をThreadsで告知
- [ ] 序章・第1回のビューが伸びていない件、次の週次締めで様子見（IG/Threads告知が後追いだったため。改善しなければ導線を見直す）

### マーケ部
- [x] `marketing/threads/config.md` に現行の自動投稿の仕組みを書き出す
  → **判明**: 自動投稿（1日2本）は `queue.md` を読まない別基盤（RSS×Claude自動生成、公式API）
- [x] 開発部の告知 → 承認 → 自動投稿の仕組みを実装・導入完了（2026-09-05）
      `queue_to_pending.py` ＋ threads-app「承認待ち」画面（https://investment-apps-2y8upkj8jzy75k4xtykzpy.streamlit.app/）
      manual_postsテーブル作成・再デプロイ・テスト投稿の却下まで確認済み。次回公開から実運用

---

## 🗓 近いうち（Phase 1〜2）

- [x] 開発2部 — パイプライン整備（collect.py / car-column-writer / SOP / prices.json / 月次Action）
- [x] 開発2部 — 7月記事 note 公開済み（https://note.com/basel5/n/n400eac7620fd）→ `published/2026-07.md` にURL記入
- [ ] 開発2部 — マガジン（名称未定）を作成し、7月記事を追加。冒頭に注記・シリーズ説明を整える
- [ ] 開発2部 — 8日ごろ: `python dev/2-cars/pipeline/collect.py 2026-08`（台数は自動取得。失敗時のみ `data/inputs/2026-08.json` に手貼り）→ car-column-writer で執筆 → 公開
- [ ] 経理 — 8月PL締め（`sop/weekly-close.md` 月次）→ `finance/reports/2026-08.md`。会計ソフト導入の判断
- [ ] Instagram — プロアカウント化＋Facebookページ連携（開発3部が軌道に乗ったら）
- [ ] 開発5部 — 序章〜第2回まで無料で出し、読まれ方を見て有料ラインの引き方・コマ数を確定
- [ ] 開発3部 — 分析執筆まで自動化する `/schedule` routine 化

## 📦 あとで（Phase 2〜3）

- [ ] 経理ダッシュボード生成（`finance/dashboard.html`、実データ4週間ぶん貯まってから）
- [ ] 開発4部 温泉マガジンを3部の型で立ち上げ
- [ ] 開発5部 — 売れたら絵の外注（キャラ発注 or 1話外注）を検討
- [ ] マーケ — 予約投稿API / Buffer で半自動化
- [ ] 3ヶ月PLを締めて法人化の是非を検討（当面は個人事業）

---

## ✅ 完了ログ（直近のみ）

- [x] 2026-09-05 マーケ部 開発部の告知→承認→Threads自動投稿の仕組みを導入（threads-app「承認待ち」画面）
- [x] 2026-09-05 開発5部 第2回を¥200で公開（初の有料回。https://note.com/basel5/n/n111a2e726a2d）
- [x] 2026-09-03 開発5部 第1回を無料公開（https://note.com/basel5/n/nc7c5b170893f）
- [x] 2026-09-02 開発5部 序章を無料公開（https://note.com/basel5/n/n8ddb16b8b430）
- [x] 2026-09-02 開発5部 新設・カリキュラム確定（`docs/decisions/0003`）、序章＋第1回の脚本、図・見出し画像
- [x] 2026-08-31 開発3部 パイプライン完成・CI検証、2026-W35 を初公開
- [x] 2026-08-30 秘密情報インシデント対応（`.enc` 除去・TMDBトークン再発行）
- [x] 2026-08-29 会社リポジトリ雛形・各部scaffold
