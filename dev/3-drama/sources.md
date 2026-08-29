# 開発3部 データソース（確定版 v1）

決定の経緯: `docs/decisions/0002-drama-ranking-methodology.md`

## クレーム（記事タイトル・見出しの言い回し）

- ○「話題のドラマ総合ランキング（合成指標）」
- ○「TVer週間・Netflix Japan Top10・Google検索トレンドを合成」
- ✕「視聴されている順番」「視聴数No.1」など、横断視聴数を測定できているかのような断定はしない
  （測定不能／景表法・優良誤認リスク）

## 合成ランキングの定義（MVP: 1〜4号）

3つの構成要素を各 0〜100 に正規化し、**その作品に存在する要素だけの単純平均**を合成スコアとする。

| 要素 | ソース | 正規化 |
|---|---|---|
| A: 見逃し配信 | TVer 週間ランキング（ドラマ、上位N=20） | `score = 100 * (N - rank + 1) / N`、圏外は要素なし |
| B: 配信SVOD | Netflix Japan 週間 Top 10（TV、N=10） | 同上、圏外は要素なし |
| C: 話題度 | Google トレンド（過去7日、対象作品群の相対値 0〜100） | 値をそのまま使用 |

- **ランク付けの条件**: A・B の少なくとも一方に入っていること（Cだけの作品は対象外）。
- NHK作品（大河・朝ドラ等）は A に乗らないため v1 では原則圏外になる → 記事内で「本ランキングは民放＋配信が対象」と明記。
- 表には合成スコアだけでなく **A/B/C の内訳を併記**（算出の透明性＝マガジンの信頼性）。
- 算出方法（この節の要約＋重み）を毎号の記事末尾に固定掲載する。

### v2以降で追加（2ヶ月目〜、`0002` ADR参照）

個人視聴率／コア視聴率（ビデオリサーチ、報道引用）、U-NEXT週間、Filmarks満足度。追加時に重み付けへ移行し、変更履歴を記事に残す。

## 項目別ソース

| 記事に載せる項目 | ソース | 取得 | 注意 |
|---|---|---|---|
| 合成順位（A/B/C） | 上表のとおり | 自動（下記パイプライン） | Netflix・TVerは公式に開かれたAPIではない → 週1回・低頻度・出典明記で運用。仕様変更でスクレイパーが壊れる前提でメンテ枠を持つ |
| 何話まで進行 | TMDB（`last_episode_to_air` / `number_of_episodes`）＋ **地上波は番組公式サイト/番組表で最終確認** | 自動取得→レビューで確認 | TMDBは日本の地上波が遅延・欠落しがち。draftに `【話数要確認】` を残す |
| あらすじ | 番組公式サイト／プレス資料を読み、**自分で2〜3文に要約** | AIドラフト→人が確認 | Wikipedia等の丸写し不可。公式のコピーそのままも避ける |
| 配信状況 | TMDB watch/providers（region=JP、JustWatch連携） | 自動 | **「JustWatch」の帰属表示が必須**。24時間更新なので放送直後は反映遅れあり。主要作品はレビューで目視確認 |
| 人気の理由（AI分析） | 上記メタ＋Googleトレンドの形（スパイク/じわ伸び）＋Filmarksのレビュー傾向（出典明記で引用） | `ranking-writer` がドラフト | 意見と事実を書き分け。未確認情報を断定しない |
| ポスター/画像 | 当面**使わない**。順位表は自作のテキストグラフィック | — | ポスター・場面写真の著作権は制作会社。TMDB画像もライセンスは各社。将来、局のプレス用許諾素材のみ検討 |

## 自動収集パイプライン

`dev/3-drama/pipeline/collect.*`（実装言語は未確定。Python想定）

```
1. fetch_tver()      TVer ランキングAPI(ドラマ・週間) → [{rank, title, series_id}]
2. fetch_netflix()   netflix.com/tudum/top10/japan/tv → [{rank, title, weeks_in_top10}]
3. titles = union(1, 2)
4. fetch_trends(titles)   Google トレンド(過去7日) → {title: 0-100}
5. enrich_tmdb(titles)    TMDB検索 → overview, 話数, watch/providers(JP), first_air_date
6. composite()       A/B/C を正規化・平均・ソート（ランク条件を適用）
7. 出力:
   - dev/3-drama/data/YYYY-Www.json   （生データ＋スコア内訳＋各出典URL・取得時刻）
   - dev/3-drama/drafts/YYYY-Www.md    （template.md に流し込んだ下書き。AI分析欄は空 or 【要確認】）
8. ranking-writer が draft の AI分析・要約を執筆 → 人がレビュー → 公開は手動
```

- スケジュール: `/schedule` で週次 routine（例: 毎週月曜 06:00）。手順6まで自動、公開は社長承認。
- **公開前の人手レビュー（10分）は会社ルール（CLAUDE.md）。スクレイパーのズレ・事実誤認の最終防波堤なので自動化しない。**

### 週次データ JSON スキーマ（`data/YYYY-Www.json`）

```json
{
  "week": "2026-W36",
  "range": {"from": "2026-08-31", "to": "2026-09-06"},
  "collected_at": "2026-09-07T06:00:00+09:00",
  "sources": {
    "tver": {"url": "", "fetched_at": ""},
    "netflix": {"url": "https://www.netflix.com/tudum/top10/japan/tv", "fetched_at": ""},
    "google_trends": {"timeframe": "now 7-d", "geo": "JP", "fetched_at": ""},
    "tmdb": {"attribution": "This product uses the TMDB API and JustWatch data; not endorsed by TMDB.", "fetched_at": ""}
  },
  "items": [
    {
      "rank": 1,
      "title": "",
      "composite_score": 0.0,
      "components": {"A_tver": {"rank": null, "score": null},
                     "B_netflix": {"rank": null, "weeks": null, "score": null},
                     "C_trends": 0},
      "tmdb_id": null,
      "episodes": {"aired": null, "total": null, "needs_check": true},
      "overview_source_url": "",
      "providers_jp": [{"name": "", "affiliate": "abema|amazon|none"}],
      "first_air_date": ""
    }
  ]
}
```

## アフィリエイト対応（現状: VOD はABEMAのみ提携済み）

| 配信先 | 提携 | 記事での扱い |
|---|---|---|
| ABEMA（ABEMAプレミアム） | **済** | 配信ありなら `[PR]` リンク設置 |
| U-NEXT | 未（A8に案件なし。バリューコマース／アクセストレードは審査落ち） | テキストで「U-NEXTで配信中」と記載のみ。→ **もしもアフィリエイト・afb に申請**（`sop/affiliate-rules.md`）。通ればリンク化 |
| Amazon Prime Video | 未 | もしも or Amazonアソシエイト通過後に作品ページリンク |
| Netflix | 不可（アフィリエイト制度なし） | 「Netflixで配信中」と記載のみ |
| Disney+ / Hulu 等 | 未 | テキストのみ。ASP開拓の状況で更新 |

- 各作品行に「配信: ◯◯（提携先は[PR]リンク／その他はテキスト）」を必ず表示。
- 冒頭に広告表記（`sop/disclosure.md`）。提携が1つでもリンクを含む号は表記必須。

## 規約チェック（半年ごと・最終確認日を記入）

| 項目 | 最終確認日 | メモ |
|---|---|---|
| TVer ランキング取得の可否（利用規約 / robots.txt） | — | 週1・低頻度・出典明記の前提で判断 |
| Netflix Tudum ページ参照（ToS上はスクレイピング制限あり） | — | 公式配布データ（TSV等）があればそちらを優先。無ければ週1参照・出典明記 |
| TMDB API 利用規約（帰属表示 / 商用） | — | 「JustWatch」帰属を記事フッターに固定 |
| Google トレンド（pytrends は非公式ライブラリ） | — | レート制限で落ちうる。失敗時は前週値＋`【要確認】` |
