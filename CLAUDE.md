# CLAUDE.md — Basel 一人会社ワークスペース

## これは何か
SNS収益化を目的に、Claude Code で運営する一人会社（個人事業主）のリポジトリ。
「部署」= フォルダ + `.claude/agents/` のサブエージェント + `sop/` の手順書。

## まず読むもの
- `README.md` — 会社概要・意思決定ルール・KPI定義
- `STATE.md` — 現在地（毎週月曜に更新する生きたダッシュボード）
- `docs/org.md` — 各部の責務と定期業務カレンダー
- `docs/roadmap-90days.md` — フェーズ計画
- `docs/decisions/` — 意思決定ログ

## 絶対ルール
- **外部への公開・投稿・課金・API送信・提携申請は実行しない。** 社長（ユーザー）の承認後に社長 or 専用スクリプトが行う。エージェントはドラフトまで。
- アフィリンクを含む記事/投稿には必ず広告表記（`sop/disclosure.md`）。
- ランキングの数値は一次ソース由来＋出典URL明記。他サイトのランキング表を転載しない。
- シークレット・APIキー・トークンをコミットしない（`.gitignore` 済み）。スクショ指示にも含めない。
- 数値は該当ファイル由来のみ。不明は `【未入力】`/`【要確認】` と書き、推測で埋めない。

## 部門とエージェント
| 部門 | フォルダ | エージェント | 主な手順書 |
|---|---|---|---|
| 開発1部 アプリ+有料note（**維持モード**・新規停止） | `dev/1-apps/` | `app-note-writer` | `sop/publish-note.md` |
| 開発2部 車ランキング | `dev/2-cars/` | `ranking-writer` | `sop/ranking-magazine-workflow.md` |
| 開発3部 ドラマランキング（無料・集客エンジン） | `dev/3-drama/` | `ranking-writer` | `sop/ranking-magazine-workflow.md` |
| 開発4部 温泉ランキング | `dev/4-onsen/` | `ranking-writer` | （3部の型を流用） |
| 開発5部 金融マンガ（**有料・プロダクト主軸**） | `dev/5-finance-manga/` | `manga-edu-writer` | `sop/manga-episode-workflow.md` |
| マーケ部 | `marketing/` | `social-writer` | `marketing/README.md` |
| 企画部 | `planning/` | `researcher` | `planning/README.md` |
| 経理部 | `finance/` | `bookkeeper` | `sop/weekly-close.md` |

## 定期リズム
- 毎日: Threads 2本（マーケ）
- 月曜: 週次締め（`sop/weekly-close.md`）→ KPI更新 → STATE.md 更新 → 企画の棚卸し
- 週次(曜日固定): ドラマnote 1本
- 月初: 車note 1本、前月PL締め

## コミット
公開・週次締め・大きな更新のたびにコミット。メッセージ例: `publish: 3-drama 2026-W36` / `weekly: 2026-W36`。
