# キャラクターバイブル & 絵柄トンマナ

Midjourney等で画像を生成するときの「見た目の固定」用。キャラは**2人だけ**に絞る
（一貫性が崩れにくい・生成コストが低い）。

## 絵柄トンマナ

- フラットな学習まんが調。線は細め、彩度は控えめ、影は少なめ
- 背景はシンプル（教室・部屋・カフェ・公園程度）。書き込みすぎない
- 1エピソード 12〜18コマ。バストアップ〜ウエストアップを中心に（全身は崩れやすい）
- コマの縦横比は縦長（`--ar 3:4` 目安）。Canvaで縦に連結する
- **日本語テキストは一切Midjourneyで出さない**。すべてCanvaで吹き出し＋フォントで入れる
- Midjourney推奨: `--cref <キャラ基準画像URL>`（キャラ参照）＋ `--sref <スタイル基準画像URL>`（絵柄参照）を毎回固定。seedもメモして再利用

## ミオ（疑問役 / 主人公）

- 中学2年・14歳。お金の話は苦手。素直でツッコミ役。行動が先に出るタイプ
- 外見: 肩までの黒髪ボブ、前髪ぱっつん、からし色のフーディー、緑のリュック。メガネなし
- 表情バリエーション: 驚き / きょとん / ひらめき / むくれ / 前のめり

## センセ（解説役 / ナビゲーター）

- 30代。ミオの担任 or 近所の頼れる大人。おだやかで、たとえ話がうまい。時々おおげさ
- 外見: 短めの黒髪、無精ひげ薄め、ラフな襟付きシャツ（青系）＋カーディガン、丸メガネ
- 表情バリエーション: にっこり / 説明中（人差し指を立てる）/ 困り笑い / 真剣

> 実際に使うMidjourneyプロンプトは、下の「# キャラクター作成ブリーフ」にまとめてあります。
> コマを描くときのプロンプトは `dev/5-finance-manga/scripts/00-prologue.md` の各コマに書いてあります。

## 一貫性を保つコツ（Midjourneyの弱点対策）

- 服装・髪型は毎回まったく同じにする（言葉でも固定、画像でも `--cref`）
- 1コマ1人を基本に。2人同時のコマは崩れやすいので数を絞る
- 顔の細部（目の形など）の微差は許容。気になる箇所はCanvaで簡易補修 or 別カット再生成
- 決まった良いカットは「表情パーツ集」としてストックし、Canvaで使い回す
- どうしても安定しないときは、生成ではなく**同じカットの使い回し＋セリフ差し替え**で乗り切る

## 図解のトンマナ

- キャラ絵とは別レイヤーで、Canvaの図形・アイコンで作る（生成に頼らない）
- 色は2〜3色に絞る。数字は大きく。矢印で流れを示す
- 図解こそがこの教材の価値の中心。1回に1〜2枚は必ず入れる

## 文字のルール（全エピソード共通）

- **すべて横書きで統一**（セリフ・図解・本文とも。縦書きと混ぜない）
  - 理由: スマホ縦スクロール／noteに最適、Canvaで扱いやすい、数字・用語（10円・NISA・複利…）がそのまま入る
- 数字は算用数字のまま（10万円、10円→12円→15円）
- フォント: 丸ゴシック系を1つに固定（序章で選んだもの）
- サイズ: 本文 24〜28、強調の一言だけ 32前後
- 色: 黒文字／白〜薄色の吹き出し
- 吹き出しの種類: 声に出す＝しっぽ付き／心の中＝モクモク

---

# キャラクター作成ブリーフ（1回だけ・Midjourney）

序章を実際に描く前に、この手順でキャラの「基準画像」を作り、下の欄にURLを固定する。

## 手順

1. 下のプロンプトで **キャラシート** と **単体ポートレート2〜3枚** を各キャラ生成
   （**この段階のプロンプトには `--cref` / `--sref` / `--oref` を付けない**。いま作っているのが、その"参照画像"だから）
2. いちばん線がきれいで表情がニュートラルな **単体ポートレート1枚** を各キャラでアップスケール
   → その画像のURLが、そのキャラの `--cref`（毎コマ固定）
3. 全体の色・絵柄がいちばん好みの1枚を選び、そのURLを `--sref`（シリーズ通して固定）
4. コマ生成では **`--oref <キャラURL> --ow 100 --sref <共通URL>`** を使う
   （Midjourney V8系は `--cref`/`--cw` 非対応。`--ow` は 1〜1000・初期100、似なければ 200〜400 に上げる）
5. 選んだURLを下の「基準」欄に記入 → 脚本の各コマのプロンプトに付けて使う

## プロンプトの貼り方

- 下の各プロンプトを囲む `` ` `` （バッククォート）は Markdown の装飾。**バッククォートは含めず、中身だけ**をコピーする
- 1プロンプト＝1行。先頭の `character reference sheet ...` から末尾の `--ar 3:2`（or `--ar 3:4`）までを全部コピーして、Midjourneyの入力欄に貼って Enter

## ミオ（疑問役）

- キャラシート:
  `character reference sheet of "Mio", a 14-year-old Japanese middle-school girl, short black bob with straight blunt bangs, mustard-yellow zip hoodie over a white tee, green backpack, no glasses, cheerful and expressive. front view and 3/4 view, plus 5 facial expressions (bright smile, surprised, thinking with finger on chin, sulking, eager leaning-in). plain light-grey background, flat modern anime style, thin clean linework, soft muted colors, no text --ar 3:2`
- 単体ポートレート:
  `flat modern anime style, Mio (14yo Japanese girl, short black bob with blunt bangs, mustard-yellow zip hoodie, white tee), neutral friendly expression, plain light-grey background, thin clean linework, soft muted colors, waist up, no text --ar 3:4`

## センセ（解説役）

- キャラシート:
  `character reference sheet of "Sensei", a friendly Japanese man in his early 30s, short black hair, light stubble, round glasses, blue collared shirt under a grey cardigan, calm and warm. front view and 3/4 view, plus 4 facial expressions (gentle smile, explaining with raised index finger, troubled smile, serious). plain light-grey background, flat modern anime style, thin clean linework, soft muted colors, no text --ar 3:2`
- 単体ポートレート:
  `flat modern anime style, Sensei (Japanese man early 30s, short black hair, light stubble, round glasses, blue collared shirt, grey cardigan), calm warm expression, plain light-grey background, thin clean linework, soft muted colors, waist up, no text --ar 3:4`

## 基準（生成したら記入）

| 項目 | 値 |
|---|---|
| ミオ `--oref` URL | https://cdn.midjourney.com/0048acd8-0fe1-4f47-9577-993f454d7aa8/0_2.png |
| センセ `--oref` URL | https://cdn.midjourney.com/275ab916-3c0f-49d5-896e-1def306527e6/0_1.png |
| 共通 `--sref` URL | https://cdn.midjourney.com/042330eb-cb53-49e4-9ede-862e908e2e83/0_1.png |
| `--ow`（重み） | 100（似なければ 200〜400） |
| Midjourney バージョン | V8系（`--cref`/`--cw` 非対応 → `--oref`/`--ow` を使用） |
