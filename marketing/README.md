# マーケティング部

## 役割

Threads / Instagram で発信し、note（無料マガジン + 有料note）へ誘導する。

## 現状

- Threads: 自動投稿 1日2本 稼働中（設定は `threads/config.md`）
- Instagram: アカウントのみ。開発3部の立ち上げ後に運用開始

## 方針

- リンク直貼りの投稿ばかりにしない。価値のある単発投稿（考察の一部、豆知識、問いかけ）を主にし、誘導は一定比率に抑える。
- アフィリンクや「PR案件noteへの誘導」を含む投稿は、投稿内に広告である旨を明記（`sop/disclosure.md`）。
- 非公式ツールでの自動化はアカウント停止リスク。**Threads API / Instagram コンテンツ公開API（プロアカウント + Facebookページ連携）**、または Buffer 等の公認スケジューラを使う。現行スクリプトの方式を `threads/config.md` で棚卸しし、規約準拠か確認する。

## 週次の流れ

1. 各開発部から今週のSNS文面が `threads/queue.md` に入る
2. `social-writer` が不足分の単発ネタを補充し、1週間分の投稿カレンダーを `calendar.md` に組む
3. 社長がざっと目を通す（炎上リスク・誤情報チェック）
4. 予約投稿にセット
5. 週明けに実績を `threads/log.csv` に記録 → 経理部のKPIへ

## フォルダ

- `calendar.md` — 投稿カレンダー（1週間ぶん）
- `threads/config.md` — 自動投稿の構成・認証方式・投稿時間
- `threads/queue.md` — 各部から届いた投稿ネタの入り口
- `threads/log.csv` — 投稿実績（インプレ等）
- `instagram/` — Instagram運用（`README.md` にキャプションテンプレ・UTM運用）

## 流入元計測（UTM）— 2026-09-12〜

**背景**: noteのダッシュボードの「流入元」は、Threads/Instagramのアプリ内ブラウザ経由だと
リファラーが送られず「no referrer」に、記事間を回遊した2クリック目以降は「note.com」に
計上されてしまう。**このため「note.com」比率が高く見えても、実際はThreads/Instagram発の
流入が過小評価されている可能性が高い。** 正しく計測するため、外部リンクにはUTMを付ける。

- **Threads**: `marketing/threads/queue_to_pending.py` に `--link` を渡すと
  `utm_source=threads&utm_medium=social&utm_campaign=<部・期間から自動生成>` が自動付与される
  （本文中の同じURL文字列も自動で置き換わる。無効化は `--no-utm`）。
- **Instagram フィード投稿**: キャプション内のURLはリンクにならないため、**プロフィールのリンク（bio）に
  固定でUTMを付けておく**（例: `?utm_source=instagram&utm_medium=bio`）。個別の投稿ごとの
  出し分けはできないため、IG経由の流入は「まとめて」計測される前提。
- **Instagram ストーリーズ**: リンクスティッカーには投稿ごとに
  `utm_source=instagram&utm_medium=story&utm_campaign=<部・期間>` を付けたURLを使う（個別計測が可能）。
- 数週間ぶんデータが貯まったら、noteの流入元グラフの「note.com」「no referrer」の実態が
  変わって見えるはずなので、`finance/kpi.csv` の振り返り時にあわせて確認する。

## note内で見つけてもらうための改善（外部流入とは別に、並行してやること）

- ハッシュタグ・カテゴリ選定を毎回見直す（`sop/publish-note.md` のチェックに追加済み）
- タイトル・サムネイルのクリック率（インプレッション→PV）を意識する。薄い場合はサムネ/タイトルを疑う
- 自分の過去記事同士を意図的に相互リンクする（開発4部の温泉宿⇔お土産が実例）
