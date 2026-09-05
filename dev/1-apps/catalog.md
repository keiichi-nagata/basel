# 有料note カタログ（開発1部）

既存の投稿をここに集約する。note本文はnote側が正。ここには「メタ情報 + 元ソースの所在 + 数字」を置く。

## 一覧

| # | タイトル | 公開日 | 価格 | 累計販売数 | 累計売上 | 公開リポジトリ（note記事が案内・顧客用） | 開発用リポジトリ（ローカル作業フォルダの`origin`） | note URL |
|---|---|---|---|---|---|---|---|---|
| 1 | 家族カレンダーの入手・公開ガイド＆Claude Codeカスタマイズ手順 | 2026-08-13 | ¥1,200 | 0 | ¥0 | https://github.com/basel5freedom/family-calendar | https://github.com/keiichi-nagata/family-calendar（個人情報等あり・非公開想定） | https://note.com/basel5/n/na85fc66ac331 |
| 2 | iCloud写真ダウンローダー（Google Colab版）の入手・公開ガイド＆Claude Codeカスタマイズ手順 | 2026-08-17 | ¥1,200 | 0 | ¥0 | https://github.com/basel5freedom/icloud-photo-organizer | なし（ローカルはgit管理外） | https://note.com/basel5/n/n656ffa6f2dec |
| 3 | GitHub Driveの入手・公開ガイド＆Claude Codeカスタマイズ手順 | 2026-08-17 | ¥1,200 | 0 | ¥0 | https://github.com/basel5freedom/github-drive-app | なし（開発フォルダがそのまま公開リポジトリを指す。個人情報削除等の移行工程を経ていない） | https://note.com/basel5/n/n8ac12f4c5834 |
| 4 | 医療費控除明細自動作成アプリの入手・公開ガイド＆Claude Codeカスタマイズ手順 | 2026-08-24 | ¥1,200 | 0 | ¥0 | https://github.com/basel5freedom/iryouhi-kojo-meisai | https://github.com/keiichi-nagata/iryouhi-kojo-meisai（個人情報等あり・非公開想定） | https://note.com/basel5/n/nd22238facdea |
| 5 | 家族アルバムアプリの入手・公開ガイド＆Claude Codeカスタマイズ手順 | 2026-09-01 | ¥1,200 | 0 | ¥0 | https://github.com/basel5freedom/family-album | https://github.com/keiichi-nagata/family-album（非公開） | https://note.com/basel5/n/ncbc5331a45b2 |

売上0円（2026-09-05時点、社長確認）。5本とも公開済み（8/13〜9/1）だが、購入は出ていない状態。#は公開順。
**公開リポジトリはすべて `basel5freedom`**（2026-09-05に実リポジトリを確認）。

## 公開の作り方（ワークフロー）

1. `keiichi-nagata` 側（開発用リポジトリ／ローカル作業フォルダ）でアプリを作成
2. 個人情報等を削除し、`basel5freedom` 側へ移行して公開
3. `basel5freedom` 側は **README を削除**（購入者がREADMEだけで同じものを自作できてしまうのを防ぐため。
   noteの有料エリアで手順を読んだ人だけが再現できるようにする狙い）
4. アプリ完成後、ローカルの修正は基本的に行っていない
5. 今後ローカルを修正した場合、`basel5freedom` へ反映するかどうかは**都度判断**（自動同期ではない）

GitHub Drive のみこの2段階を経ておらず、開発フォルダ＝公開リポジトリ（`basel5freedom`）を直接指している。

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
