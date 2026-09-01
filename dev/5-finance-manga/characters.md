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
- Midjourney基準プロンプト（英語）:
  `flat modern anime style, a 14-year-old Japanese girl named Mio, short black bob with straight bangs, mustard yellow hoodie, expressive, simple classroom background, soft muted colors, thin clean linework, waist up --ar 3:4 --cref <URL> --sref <URL>`

## センセ（解説役 / ナビゲーター）

- 30代。ミオの担任 or 近所の頼れる大人。おだやかで、たとえ話がうまい。時々おおげさ
- 外見: 短めの黒髪、無精ひげ薄め、ラフな襟付きシャツ（青系）＋カーディガン、丸メガネ
- 表情バリエーション: にっこり / 説明中（人差し指を立てる）/ 困り笑い / 真剣
- Midjourney基準プロンプト（英語）:
  `flat modern anime style, a friendly Japanese man in his 30s named Sensei, short black hair, light stubble, round glasses, blue collared shirt with cardigan, warm calm expression, simple background, soft muted colors, thin clean linework, waist up --ar 3:4 --cref <URL> --sref <URL>`

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
