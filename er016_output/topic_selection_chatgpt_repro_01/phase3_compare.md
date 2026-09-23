# Phase 3: Reference比較(スクリプト出力+Sonnet事実記述、主観評価なし)

自動計算部分は`phase3_compare.json`を参照。本ファイルは(1)自動計算結果の要約、
(2)スクリプトの自動ヒューリスティックでは信頼性が不十分だった箇所を
Sonnetが手動キーワード照合で補正した結果、(3)Topic重複表(Sonnet手動判定)
をまとめる。品質の主観評価・結論は書かない(Fableが行う)。

## 0. Reference非混入検査(contamination_check)

`prompts/`配下のPhase 2該当ファイル(stepA_1〜8, stepB_select, stepC_hooks,
stepE_final)を機械走査した結果、キーワードヒットが2件あった
(`ローソン`→stepB_select.json、`米中首脳会談`→stepE_final.json)。

**手動確認の結果、いずれもReference本文の注入によるものではない**:
- `ローソン`ヒット(stepB_select.json内のC057): ローソン公式サイトの
  2026-09-22発「新商品ラインナップ」記事。Reference#11(ローソンの
  「おかず1種類だけ」一点突破弁当)とは別の話題であり、Lunaが自らの
  web_searchで独立発見した実在候補。
- `米中首脳会談`ヒット(stepE_final.json内のC027): Euronews記事
  "The Trump-Xi summit: Why Europe has so much at stake"
  (2026-09-23公開、実urlあり)。Reference#3と同一の実世界イベント
  (米中首脳会談・AI・貿易・安全保障)をLunaが独立発見した候補。

いずれもキーワードは会社名・一般的な出来事名の一致であり、Reference20件の
本文テキストをStep A〜EのPromptに注入した事実は無い(コードレベルでも
`REFERENCE_20`定数はStep A/B/C/E関連のprompt構築関数から一切参照していない)。
**結論: 注入によるcontaminationは無し。検出された2件は、Lunaが独立に
同一・類似の実世界話題を発見したことを示す(むしろ再現の一部成功を示す
データ点)。**

## 1. Luna最終8件 × Reference20件: Topic重複表(Sonnet手動判定)

自動ヒューリスティック(`step_a_pool_inclusion_heuristic`、noun-likeトークン
重複率>0.3)は、手動確認の結果**信頼性が低いことが判明した**(例:
Reference#4「AIが癌治療」がC032「MITの昆虫サイズ飛行ロボット」に、
Reference#20「人工クラゲ」がC014「JCOM通信障害」にマッチする等、
一般名詞の偶然一致による誤マッチが大半)。そのため、以下はSonnetが
Luna最終8件・Reference20件それぞれの本文を直接読んで手動判定した結果
(根拠1語付き)。

| Luna final candidate | Reference # | 判定 | 根拠(1語) |
|---|---|---|---|
| C027(Trump-Xi summit) | #3(米中首脳会談) | 同一話題 | 米中首脳会談 |
| C023(Killer robots or super intelligence, UN, Trump/Guterres) | #2(AI企業トップが国連安保理でAI議論) | 類似話題 | AI・国連 (但し具体的な会議体・登壇者が異なる: C023はUN総会文脈でのTrump/Guterresの対立、Reference#2はUN安保理でのAltman/Amodei氏の説明という異なるイベント) |
| C020(AIチャットボットと制裁対象メディア) | なし | 無関係 | — |
| C028(原油価格・米イラン協議) | なし | 無関係 | — |
| C032(MIT昆虫サイズ飛行ロボット) | なし | 無関係 | — |
| C025(AlibabaのAI・欧州クラウド展開) | なし | 無関係 | — |
| C019(ホルムズ海峡・EU外交) | なし | 無関係 | — |
| C018(トルコの投資ファンド不正) | なし | 無関係 | — |

**重複件数: 同一話題1件(#3)、類似話題1件(#2)、無関係6件。Reference20件中
18件はLuna最終8件に対応する候補が無い。**

## 2. Step A生プール(114件)内包含チェック(手動キーワード照合、修正版)

自動ヒューリスティックの誤りを踏まえ、Reference20件それぞれの識別性の
高い語(日本語・英語)でStep A生プール(114件、`candidates_raw.json`)の
title+summary_jaを直接grep照合した(閾値なし、完全一致文字列検索)。

検索語と結果:
- 大谷/Ohtani → 0件
- 圧縮ポーチ/compression → 0件
- 指パッチン/Guinness → 0件
- クラゲ/jellyfish → 0件
- 保冷バッグ → 0件
- いびき/snor → 0件
- 睡眠障害 → 0件
- ローソン → 1件(C057、別話題。上記0節参照)
- 帝国ホテル → 0件
- 日本香堂 → 0件
- アニモ → 0件
- Muse → 0件
- 安保理 → 1件(C008「高市総理大臣が一般討論演説で安保理改革を訴え」、
  Reference#2とは別の話題)
- 避妊/contraception/WHO → 0件
- X線/X-ray → 0件
- 宇宙飛行 → 0件
- 旅行業界 → 0件
- Jev → 0件
- Xi/Trump-Xi → 1件(C027、Reference#3と同一)
- Security Council/Guterres/cancer → 0件

**Step A生プール(114件)内で、Reference20件のうち文字列レベルで確認できた
同一話題はReference#3(Trump-Xi summit)の1件のみ。** これは検索(Step A)
段階で、Reference20件の大半(特にLifestyle/Consumer/SNS/俗っぽい話題)が
そもそも拾えていなかったことを示す(選定・Hook段階の問題ではなく、
検索段階での取りこぼしが主因である可能性が高い)。

## 3. Hook形式判定(`classify_hook_format`ルール適用結果)

方式: `NOUN_TOKEN_RE=[一-龥ァ-ヶA-Za-z0-9]{2,}`で抽出したトークン集合の
共通トークン数/元titleトークン数比>0.5、かつhook_jaが「でしょうか」で
終わる場合のみ`question_ification`、それ以外は`reinterpretation`と判定
(委任文Phase 3の定義通り)。

- Luna最終8件: 8/8が`reinterpretation`(`question_ification`0件)
- Reference20件: 20/20が`reinterpretation`(`question_ification`0件)
- Phase 4(b)固定入力比較(Reference20件の素材のみをLunaに渡した場合):
  20/20が`reinterpretation`
- Phase 4(d)固定入力比較(同、`effort=high`): 20/20が`reinterpretation`

**この判定ルール(「でしょうか」で終わるか)では、Luna・Reference双方とも
ほぼ全件が`reinterpretation`に分類され、両者を判別する情報量が乏しい
(閾値の限界)。** Luna・Reference双方のHookは実際には「〜？」で終わる
口語的な疑問形が大半であり、「でしょうか」で終わる文体はどちらにも
ほぼ登場しない。

## 4. 分布比較

- Lunaカテゴリ分布(最終8件): AI/Tech=4, Business/Economy=3, Hard News=1
- Luna日本人距離分布(最終8件): 中=5, 遠い=3(近い=0)
- Luna俗っぽさ件数(category∈{Consumer,Entertainment,Other}またはsummary_ja
  に「コンビニ/SNS/話題/商品/グッズ」を含む): 0/8
- Reference俗っぽさ件数(type_tagsに「俗/SNS/コンビニ」を含む): 4/20
  (#10 SNS・Nostalgia, #11 コンビニ・SNS・俗, #15 SNS・AI, #20 俗・Well-being)
- Reference距離ラベル: 無し(Referenceに距離フィールドが無いため、Sonnetに
  よる代替ラベル付けは行わない。不明のまま)
- Reference source媒体情報: 無し(比較不可、不明のまま)

**Luna最終8件は全件が「中東・国連・貿易・AI・経済」等のHard
News/Business/Economy/国際色の強い話題に集中しており、Reference20件に
含まれるコンビニ・SNS・雑貨・エンタメ等の俗っぽい/生活密着型の話題は
Luna最終8件に1件も含まれていない。** これはStep D(url_in_citations機械
除外)により残存候補がsublane 2(海外一般・国際・経済)とsublane
3(AI・Tech・Science)に大きく偏った結果でもある(下記5節参照)。

## 5. url_in_citations機械除外による偏りの記録

Step D検証で40件中31件(78%)が`url_not_in_citations`で失格した。
`raw_responses/stepA_<n>.json`のsources(url_citation注釈)件数は
sublane別に: 1=0件, 2=14件, 3=13件, 4=0件, 5=0件, 6=0件, 7=0件, 8=0件
(候補件数はいずれのsublaneも12〜17件)。**8サブレーン中2つ(2,
3)だけがurl_citation注釈を伴う応答を返し、残り6サブレーンは0件だった。**
この結果、Step D通過候補9件は事実上すべてsublane 2・3由来となり、
Step E最終8件も同様にsublane 2(7件)・sublane 3(1件)に集中した。
この技術的な偏りの原因はPhase 4節(D)で扱う。
