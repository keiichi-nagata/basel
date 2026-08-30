# 手動入力フォールバック

`collect.py` は各ソースの自動取得に失敗すると、このフォルダの
`YYYY-Www.<source>.json` を読む。5分で貼れる分量。貼ったら再実行するだけ。

対象週 `YYYY-Www` は「直近で完了した月〜日」。例: 2026年9月1日(月)〜9月7日(日) → `2026-W36`。

## `2026-W36.tver.json` — TVer週間ドラマランキング

tver.jp/ranking のドラマ・週間から上位10〜20件。

```json
[
  {"rank": 1, "title": "作品名"},
  {"rank": 2, "title": "作品名"}
]
```

## `2026-W36.netflix.json` — Netflix Japan 週間Top10（TV）

netflix.com/tudum/top10/japan/tv から。`weeks` はランクイン累計週（不明なら 0）。

```json
[
  {"rank": 1, "title": "作品名", "weeks": 3},
  {"rank": 2, "title": "作品名", "weeks": 1}
]
```

## `2026-W36.trends.json` — Google トレンド（過去7日・日本）

trends.google.co.jp で対象作品名を比較し、相対値（0〜100）を読む。

```json
{
  "作品名A": 100,
  "作品名B": 62
}
```

## 注意

- `title` は TVer / Netflix の表記に合わせる。表記ゆれがあると別作品として扱われる。
- これらの手動ファイルはコミットしてよい（小さく、再現性のため）。
