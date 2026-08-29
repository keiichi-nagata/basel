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
- `instagram/` — 立ち上げ後に使用
