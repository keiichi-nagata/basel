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

### 開発5部（金融マンガ）
- [ ] 序章の初速を `dev/5-finance-manga/published/00.md` に記入（9/4ごろ）＋振り返り欄
- [ ] 第1回のコマ16枚を生成 → Canva組版 → 全文無料で公開 → マガジン追加
- [ ] （公開後）第2回の脚本を依頼

### マーケ部
- [ ] `marketing/threads/queue.md` の告知3本（開発5部 連載開始／うまい棒／第1回予告）を投稿フローに流す
- [ ] `marketing/threads/config.md` に現行の自動投稿の仕組みを書き出す

---

## 🗓 近いうち（Phase 1〜2）

- [ ] 開発2部 — 既存の車note1本をマガジン化＋記録（`dev/2-cars/published/0001-first-note.md`）
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

- [x] 2026-09-02 開発5部 序章を無料公開（https://note.com/basel5/n/n8ddb16b8b430）
- [x] 2026-09-02 開発5部 新設・カリキュラム確定（`docs/decisions/0003`）、序章＋第1回の脚本、図・見出し画像
- [x] 2026-08-31 開発3部 パイプライン完成・CI検証、2026-W35 を初公開
- [x] 2026-08-30 秘密情報インシデント対応（`.enc` 除去・TMDBトークン再発行）
- [x] 2026-08-29 会社リポジトリ雛形・各部scaffold
