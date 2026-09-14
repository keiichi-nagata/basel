# TODO — 社長の残タスク

やることの一元管理。完了したら `[x]` にして「完了ログ」へ移す。
戦略の全体像は `docs/roadmap-90days.md`、現在地は `STATE.md`。

最終更新: 2026-09-10

---

## 🔁 毎週の定例（くり返し・消さない）

- [ ] **月曜**: 週次締め（`sop/weekly-close.md`）→ KPI更新 → STATE.md 更新 → `planning/ideas.md` 棚卸し
- [ ] **月曜**: 開発3部 — Action＋`/schedule`ルーチンが `drama/auto-collect` に分析入りPRを用意する → 社長はレビュー → note公開（`published/` 記録・PRマージ）→ Threads/IG告知
- [ ] **毎日**: Threads 2本（`marketing/threads/queue.md` から）
- [ ] 開発5部 — 1話ずつ制作（脚本は依頼済みが先行。コマ生成＋Canva＋公開）

---

## 🔥 今すぐ / 今週

### マーケ部・画像生成の自動化（2026-09-12〜）
- [x] `scripts/ai_image.py`（OpenAI APIで背景アート生成→matplotlibで文字を上重ね、のハイブリッド方式）を用意
- [x] platform.openai.com で支払い方法を登録・APIキー発行・`.env`設定済み（社長対応）
- [x] 開発4部・熊本特別編で初の試験生成（2026-09-14）: `dev/4-onsen/assets/make_eyecatch.py` に
      `bg_path`対応を追加（AI背景の上に半透明パネル+文字を重ねる）。宿・お土産とも note用/IG用の
      4枚を生成、見た目良好で採用。今後の号（開発2/4/6部）に展開するかは反応を見て判断

### 開発3部（ドラマ）
- [x] 2周目（2026-W36）公開＋Threads/Instagram告知（2026-09-09 https://note.com/basel5/n/n373dc87cf1de、PR #3 マージ済み）
- [ ] W36 の初速を `published/2026-W36.md` に記入（9/11ごろ）
- [x] `/schedule` ルーチン `drama-weekly-analysis` を作成（毎週月曜8:30 JST、cron `30 23 * * 0`、
      trig_01NSjEFvcB9YmbPstbaWC8s8）。Action収集 → ルーチンが分析執筆＋IG画像＋PR仕上げ
- [ ] 初回自動実行（2026-09-14 8:30 JST、W37）の結果をレビュー → 問題なければ運用に乗せる
- [ ] もしもアフィリエイト・afb に申請（U-NEXT / Amazon Prime Video 用）

### 開発2部（車）— アフィリエイト
- [x] アース・カー（カーシェア）・akippa（空き駐車場シェア）を `affiliates.json` に登録、8月号の関連リンクを2方向（支出↓／収入↑）に改稿
- [x] 公開済みの8月号note記事の「関連リンク（PR）」をakippa追加の2方向版に差し替え済み（2026-09-10）
- [ ] 保険スクエアbang!（自動車保険）の承認が下りたら発行URLを `affiliates.json` に貼る → 次号以降に自動掲載

### 開発5部（金融マンガ）
- [ ] 第2回の初速・購入数/売上を `published/02.md` に記入（9/7ごろ）
- [ ] 序章・第1回のビューが伸びていない件、次の週次締めで様子見（IG/Threads告知が後追いだったため。改善しなければ導線を見直す）

### 開発4部（温泉宿ランキング＋お土産ランキング・2026-09-05 新設）
- [x] 2026年9月号（北海道・温泉宿）を公開（2026-09-06 https://note.com/basel5/n/n15a2f404324c）
- [x] Threads・Instagramで告知（2026-09-06）
- [ ] 温泉宿9月号の初速を `published/2026-09.md` に記入（9/8ごろ）
- [x] お土産ランキングを新設（`omiyage/` 一式・独自採点＝楽天市場＋Amazonレビュー平均・`docs/decisions/0004` 第7項）
- [x] 2026年9月号（北海道・お土産）を公開（2026-09-11 https://note.com/basel5/n/na14b74a39363）
- [x] 楽天アフィリエイトでお土産TOP5各商品の楽天市場リンクを発行 →「買う」欄に反映（2026-09-11）
- [x] お土産9月号: Threads/Instagram告知（2026-09-11。`omiyage/published/2026-09.md` にURL記入済み）
- [ ] お土産9月号: 温泉宿と同じマガジン「エリア別 温泉宿ランキング（月刊）」に追加
- [ ] お土産9月号の初速を `omiyage/published/2026-09.md` に記入（9/13ごろ）
- [ ] 10月号: 東北エリアのリサーチ・執筆（温泉宿＋お土産の2本。9月下旬〜10月初旬に着手）
- [x] 【特別編】令和8年熊本地震(2026-07-28)復興支援・熊本県単独・広告なし の温泉宿＋お土産を公開
      （2026-09-15。温泉宿 https://note.com/basel5/n/nb857cdd2ab15／
      お土産 https://note.com/basel5/n/n6a1b0a003074。`published/2026-kumamoto-special.md`に記録）
- [x] 熊本特別編: Instagram投稿完了（2026-09-15。温泉宿 https://www.instagram.com/p/DdRk4Gyj1Jh/／
      お土産 https://www.instagram.com/p/DdRlHIQD_j3/）
- [x] 熊本特別編: Threads投稿完了（2026-09-15。宿・お土産1本ずつ。温泉宿
      https://www.threads.com/@basel_freedom/post/DdRmjtWmtX1／お土産
      https://www.threads.com/@basel_freedom/post/DdRnEX3mtON）。残り2本は`queue.md`に持ち越しストックとして保持
- [ ] 熊本特別編: 初速を両`published/2026-kumamoto-special.md`に記入（9/17ごろ）

### 開発6部（資産クラス別 月間リターンランキング・2026-09-11 新設）
- [x] 企画I-002を採用 → 開発6部を新設（`dev/6-markets/` 一式・`universe.json`・`collect.py`・`docs/decisions/0006`・
      `ranking-writer`/`org.md`/`disclosure.md` 更新）
- [x] 2026年8月号の下書き・表画像・サムネイル・マガジン表紙を作成（`drafts/2026-08.md`。1位BTC+26.9%）
- [x] 2026年8月号を公開（2026-09-12 https://note.com/basel5/n/n27e046cffded。アフィリなし・PR表記なし）
- [x] Threads/Instagram告知（2026-09-12。`published/2026-08.md` にURL記入済み）
- [ ] noteでマガジン「資産クラス別 月間リターンランキング（月刊）」を作成し8月号を追加（表紙は作成済み）
- [ ] A8で証券口座・NISA・純金積立・暗号資産取引所の案件を精査（開設のみで成果のもの）→ 提携 → 9月号から「口座」節を追加
- [ ] 8月号の初速を `published/2026-08.md` に記入（9/14ごろ）
- [ ] 9月号（＝四半期振り返り回）を月初に作成。反応が良ければ Action＋`/schedule` で半自動化を検討

### トレード部（自動デイトレード・2026-09-10 新設）
- [x] 部を新設（`trade/` scaffold・戦略v1・kabu-api-notes・`docs/decisions/0005`・`trade-ops` エージェント・各docs更新）
- [x] bot本体の置き場所を決定：`投資/daytrade-bot/`。kabuステーション＋botはこのClaude Code PCで常時起動
- [x] v1 の流れを確定：1日1銘柄／9:00に始値基準で指値買い＋損切り逆指値／11:30前場引けで成行決済（`trade/strategy.md`）
- [x] 三菱UFJ eスマート証券の口座開設が完了（2026-09-12）。信用取引口座も開設完了（2026-09-12）
      （bot v1の売買区分は**信用取引（日計り）**と確認。`trade/strategy.md` 判断ログ参照）
- [x] このPCにkabuステーションをインストール済み（2026-09-12。社長が実施）
- [x] API有効化・本番用/検証用パスワード設定済み（2026-09-12）
- [x] kabuステーションAPI 利用規定PDFを通読（2026-09-12。`trade/kabu-api-notes.md` に反映）
- [ ] **kabuステーションの「ソフトリミット」（現状300万円）を、v1の想定投入額に見合う額まで下げる**（多重防御）
- [x] 戦略をv1.1に更新（1銘柄→複数銘柄・株数は予算額から逆算・決済セッションは前場固定/設定上は後場も選べる・
      購入条件と売買履歴はGitHub管理。`trade/strategy.md` 判断ログ参照）
- [x] `投資/daytrade-bot/` に設定Web画面（stock-app方式・Streamlit+Supabase）のスキャフォールド作成（2026-09-12。
      当初GitHub編集のYAML方式で作ったが想定と違ったため作り直し）
- [ ] Supabaseで `daytrade-bot/supabase_schema.sql` を実行（`daytrade_settings`・`daytrade_trades` テーブル作成）
- [ ] `daytrade-bot/scripts/hash_password.py` でパスワードハッシュを生成 → `.env`/Streamlit Secretsに設定
- [ ] 設定画面をローカル確認 or Streamlit Community Cloudにデプロイ
- [ ] 設定画面で `guardrails.md` の数値（購入件数上限・予算額・利確損切り%等）を入力
- [ ] `guardrails.md` の信用取引固有項目（保証金率・追証ライン・日計り手数料）をeスマート証券の案内で確認して記入
- [ ] `guardrails.md` の残りの数値（購入件数上限・市場フィルタ初期値・1銘柄あたりの予算額・買い指値の置き方・
      利確%・損切り%・ギャップ許容・キルスイッチ・週損失上限）を確定
- [ ] 指値・逆指値価格の呼値（最小価格変動単位）対応をdaytrade-bot側で検証（単純な四捨五入だと価格帯によって発注が弾かれる可能性）
- [ ] 検証用APIパスワードでの試験実行が可能かAPIドキュメントで確認（段階導入に追加できないか）
- [ ] PCを平日8:30〜11:45は起動・kabuステーション常駐に（スリープ／自動更新再起動に注意）
- [ ] 税理士に所得区分（事業所得 / 譲渡所得）を相談
- [ ] `finance/trade-pnl.csv` を作成（列: date,realized_pnl_jpy,fees_jpy,memo）
- [x] `daytrade-bot/` Stage A（発注しないログモード。yfinanceでシミュレーション）を実装（2026-09-13）
      → `migrations/2026-09-13_trade_log_columns.sql` をSupabase SQL Editorで実行
      → `python scripts/run_daily.py --date 2026-09-12` で動作確認
- [x] Stage B: kabuステーション検証用APIで`common/kabu_client.py`の動作確認完了（2026-09-13）。
      token/board/positions/ordersは本番で実機確認、sendorderもDelivType修正後Result:0を確認。
      検証用環境はOrderId=null等で実際の約定はシミュレートせず、検証はここが天井と判断
- [x] Stage C 初回トライアル実施（2026-09-14）→ **自動発注(API)は失敗（Code:100368「株式信用新規の注文は
      抑止されております」）。ただし同一銘柄・同株数の手動(kabuステーション画面)発注は成功**
      （信用新規買 09:31 単価2,612円100株）→ API固有の制限の可能性が浮上（口座全体の審査待ちではなさそう）
- [x] 手動で決済（信用返済売）も実施（2026-09-14。「時間指定W指値」指値2,743円/60分後or2,481円以下で
      成行転換）→ **実現損益 +3,518円**。`trade/journal/2026-09.md`・`daytrade_trades`に記録済み
- [ ] eスマート証券に確認: 「手動は通るがkabuステーションAPI経由の信用新規注文だけがCode:100368で
      拒否される。APIでの信用取引に手動とは別の許可・待機期間があるか」
- [ ] API制限の原因判明・解消後、あらためて`run_live_once.py`で自動発注の本番トライアルを再実施
- [ ] 決済（売り）の自動化は当面見送り。今回の手動決済の挙動を踏まえて設計を検討
- [ ] 開発1部 catalog #7-8（おすすめ株アプリの作り方 / デイトレ自動化のやり方）を執筆（免責は `sop/publish-note.md` の投資・トレード系note節）

---

## 🗓 近いうち（Phase 1〜2）

- [x] 開発2部 — パイプライン整備（collect.py / car-column-writer / SOP / prices.json / 月次Action）
- [x] 開発2部 — 7月記事 note 公開済み（https://note.com/basel5/n/n400eac7620fd）→ `published/2026-07.md` にURL記入
- [x] 開発2部 — マガジン「新車ランキングで読む 働き方と投資（月刊）」を作成、7月号・8月号を追加（2026-09-09）
- [x] 開発2部 — 8月号: collect.py で自動取得＋分析執筆済み（`drafts/2026-08.md`。TOP5にカローラNEW）
- [x] 開発2部 — 8月号を公開（2026-09-09 https://note.com/basel5/n/na441df85b797）＋Threads/IG告知＋マガジン追加
- [ ] 開発2部 — 8月号の初速を `published/2026-08.md` に記入（9/11ごろ）
- [ ] 経理 — 8月PL締め（`sop/weekly-close.md` 月次）→ `finance/reports/2026-08.md`。会計ソフト導入の判断
- [x] Instagram — プロアカウント化（@basel_freed）
- [ ] Instagram — Facebookページ連携（開発3部が軌道に乗ったら。プロアカウント化は済）
- [ ] 開発5部 — 序章〜第2回まで無料で出し、読まれ方を見て有料ラインの引き方・コマ数を確定
- [x] 開発3部 — 分析執筆まで自動化する `/schedule` routine 化（2026-09-09）

## 📦 あとで（Phase 2〜3）

- [ ] 経理ダッシュボード生成（`finance/dashboard.html`、実データ4週間ぶん貯まってから）
- [ ] 開発5部 — 売れたら絵の外注（キャラ発注 or 1話外注）を検討
- [ ] マーケ — 予約投稿API / Buffer で半自動化
- [ ] 3ヶ月PLを締めて法人化の是非を検討（当面は個人事業）

---

## ✅ 完了ログ（直近のみ）

- [x] 2026-09-05 開発4部 新設。独自採点＝楽天トラベル＋じゃらん評価の単純平均、口コミは体験談化せず
      第三者要約、と方針確定（`docs/decisions/0004-onsen-ranking-methodology.md`）。scaffold一式作成
- [x] 2026-09-05 会社全体 開発1部カタログを実態に合わせて訂正
      （公開リポジトリはすべて`basel5freedom`。keiichi-nagata側は開発用/個人用ミラーと判明）
- [x] 2026-09-05 マーケ部 自動投稿の朝テーマを「経済」に固定（`1926411`。閲覧数が優勢だったため）
- [x] 2026-09-05 マーケ部 ハッシュタグ「#」抜けを調査 → 原因は**Threads側の表示仕様**
      （先頭のハッシュタグを「トピック」としてヘッダーに昇格表示する際、本文の「#」を省いて表示する。
      投稿履歴DBでは`#経済 #行動経済学 #資産形成`と正しく送信されていることを確認済み）。
      コード側の問題ではないため対応不要と結論。念のためのプロンプト強化＋後処理補正は`ec3295b`で実施済み
- [x] 2026-09-05 マーケ部 開発部の告知→承認→Threads自動投稿の仕組みを導入・動作確認済み（threads-app「承認待ち」画面）
- [x] 2026-09-05 マーケ部 `marketing/threads/config.md` に現行の自動投稿の仕組みを棚卸し
      （自動投稿=`queue.md`を読まない別基盤・RSS×Claude自動生成・公式API、と判明）
- [x] 2026-09-05 開発2部 A8.netで提携申請：akippa（駐車場シェア）／保険スクエアbang!（自動車保険一括見積もり）
- [x] 2026-09-05 開発5部 第1回・第2回をInstagram/Threadsで告知、第2回をマガジン追加
- [x] 2026-09-05 開発5部 序章・第1回・第2回の初速を記録（序章 ビュー18/スキ1、第1回 ビュー9/スキ0）
- [x] 2026-09-05 会社全体 未pushコミットをまとめてpush（53件）
- [x] 2026-09-05 開発5部 第2回を¥200で公開（初の有料回。https://note.com/basel5/n/n111a2e726a2d）
- [x] 2026-09-03 開発5部 第1回を無料公開（https://note.com/basel5/n/nc7c5b170893f）
- [x] 2026-09-02 開発5部 序章を無料公開（https://note.com/basel5/n/n8ddb16b8b430）
- [x] 2026-09-02 開発5部 新設・カリキュラム確定（`docs/decisions/0003`）、序章＋第1回の脚本、図・見出し画像
- [x] 2026-08-31 開発3部 パイプライン完成・CI検証、2026-W35 を初公開
- [x] 2026-08-30 秘密情報インシデント対応（`.enc` 除去・TMDBトークン再発行）
- [x] 2026-08-29 会社リポジトリ雛形・各部scaffold
