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
- [ ] 序章の初速を `dev/5-finance-manga/published/00.md` に記入（9/4ごろ）＋振り返り欄
- [x] 第1回を公開（2026-09-03 https://note.com/basel5/n/nc7c5b170893f）
- [ ] 第1回の初速を `published/01.md` に記入（9/5ごろ）
- [ ] **第1回の公開済み記事**：次回予告の「第3回から有料」を「第2回から有料」に手直し（note上で編集）
- [x] 第2回の価格を ¥200 に決定（README/queue/ADR 反映済み）
- [ ] 第2回のコマ16枚制作 → Canva（コマ8とコマ9の間で「ここから有料」設定）→ ¥200 で公開

### マーケ部
- [ ] `marketing/threads/queue.md` の告知3本（開発5部 連載開始／うまい棒／第1回予告）を投稿フローに流す
- [ ] `marketing/threads/config.md` に現行の自動投稿の仕組みを書き出す

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

- [x] 2026-09-02 開発5部 序章を無料公開（https://note.com/basel5/n/n8ddb16b8b430）
- [x] 2026-09-02 開発5部 新設・カリキュラム確定（`docs/decisions/0003`）、序章＋第1回の脚本、図・見出し画像
- [x] 2026-08-31 開発3部 パイプライン完成・CI検証、2026-W35 を初公開
- [x] 2026-08-30 秘密情報インシデント対応（`.enc` 除去・TMDBトークン再発行）
- [x] 2026-08-29 会社リポジトリ雛形・各部scaffold
