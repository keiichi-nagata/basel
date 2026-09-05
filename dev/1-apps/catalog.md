# 有料note カタログ（開発1部）

既存の投稿をここに集約する。note本文はnote側が正。ここには「メタ情報 + 元ソースの所在 + 数字」を置く。

## 一覧

| # | タイトル | 公開日 | 価格 | 累計販売数 | 累計売上 | 公開リポジトリ（顧客が使う） | ローカル作業パス | note URL |
|---|---|---|---|---|---|---|---|---|
| 1 | 家族カレンダーの入手・公開ガイド＆Claude Codeカスタマイズ手順 | 2026-08-13 | ¥1,200 | 0 | ¥0 | https://github.com/keiichi-nagata/family-calendar | `C:\Claude\プライベート\家族カレンダー` | https://note.com/basel5/n/na85fc66ac331 |
| 2 | iCloud写真ダウンローダー（Google Colab版）の入手・公開ガイド＆Claude Codeカスタマイズ手順 | 2026-08-17 | ¥1,200 | 0 | ¥0 | https://github.com/basel5freedom/icloud-photo-organizer | `C:\Claude\プライベート\iCloud`（※ローカルはgit管理外。公開リポジトリを直接運用） | https://note.com/basel5/n/n656ffa6f2dec |
| 3 | GitHub Driveの入手・公開ガイド＆Claude Codeカスタマイズ手順 | 2026-08-17 | ¥1,200 | 0 | ¥0 | https://github.com/basel5freedom/github-drive-app | `C:\Claude\プライベート\ファイル共有` | https://note.com/basel5/n/n8ac12f4c5834 |
| 4 | 医療費控除明細自動作成アプリの入手・公開ガイド＆Claude Codeカスタマイズ手順 | 2026-08-24 | ¥1,200 | 0 | ¥0 | https://github.com/keiichi-nagata/iryouhi-kojo-meisai | `C:\Claude\プライベート\医療費明細自動作成` | https://note.com/basel5/n/nd22238facdea |
| 5 | 家族アルバムアプリの入手・公開ガイド＆Claude Codeカスタマイズ手順 | 2026-09-01 | ¥1,200 | 0 | ¥0 | https://github.com/keiichi-nagata/family-album | `C:\Claude\プライベート\家族アルバム` | https://note.com/basel5/n/ncbc5331a45b2 |

売上0円（2026-09-05時点、社長確認）。5本とも公開済み（8/13〜9/1）だが、購入は出ていない状態。#は公開順。

**公開リポジトリのアカウントが混在**: 3本は `keiichi-nagata`（個人アカウント）、2本（GitHub Drive・iCloud）は
`basel5freedom`。顧客からは別々の作者に見える可能性があるので、今後は `basel5freedom` に統一するか
方針を決めておくとよい（既存3本の移管は破壊的操作になるため急がなくてよい）。

## 各noteの詳細テンプレ

### note #N: タイトル

- **公開日 / 最終更新**:
- **価格**:
- **対象アプリのリポジトリ**: （URL / ローカルパス）
- **想定読者**:
- **含まれるもの**: 手順書 / サンプルコード / 図
- **サポート範囲**:
- **既知の陳腐化リスク**: 依存サービスの仕様変更で手順が古くなる箇所
- **メンテ履歴**:
  - YYYY-MM-DD: （何を直したか）

## 横展開メモ

- 5本分たまったら「まとめマガジン」or「バンドル」を検討。
- 各無料マガジン（2〜4部）の末尾に「アプリを自分で作りたい人向け」の1行 + リンクを固定設置。
