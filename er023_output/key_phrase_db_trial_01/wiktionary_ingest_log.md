# wiktionary_ingest_log — KEY-PHRASE-DB-BASED-SELECTION-TRIAL-01

Fableレビュー論点3(「Wiktionaryデータの取り込み方法(dump解析か
API/カテゴリ抽出か)が設計に未記載」)への対応として、Trial着手前に
以下の方式を確定した。

## 決定: API/カテゴリ抽出方式(dump解析は行わない)

- 理由: 本Trialの対象は既存確定本文6本(合計約2,000語)のみであり、
  Wiktionary英語版のフルXMLダンプ(数GB、数百万エントリ)を解析する
  ことは目的に対して過大。MediaWiki API(`categorymembers`)で必要な
  カテゴリのタイトル一覧のみを取得する方が高速・低負荷。
- 実測: `Category:English idioms`(10,632件、22 call、31.9秒)、
  `Category:English phrasal verbs`(5,169件、11 call、12.2秒)、
  `Category:English proverbs`(1,588件、4 call、4.8秒)。合計37 call・
  約48.9秒。API費用: ¥0(Wiktionary API利用は無償・認証不要)。

## `Category:English multiword terms`(225,910件)の扱い変更

- 上記3カテゴリと同じ全件dump方式を適用すると、225,910件は
  約470 API call・数分〜十数分規模になり、かつ6本文の候補照合には
  ほぼ使われない語が大半を占める(idiom/phrasal verb/proverbでカバー
  されない残りの複合語全般を含む巨大カテゴリのため)。
- そのため、このカテゴリのみ**候補単位のtargeted lookup**に変更した:
  1. 6本文からdeterministic抽出した2〜5-gram候補のうち、idioms/
     phrasal_verbs/proverbsのいずれにも一致しなかったものを対象とする。
  2. 対象候補を50件ずつバッチ化し、
     `action=query&titles=<cand1>|<cand2>|...&prop=categories&
     clcategories=Category:English%20multiword%20terms&cllimit=500`
     で照会。返り値に該当カテゴリが含まれていれば一致とみなす。
  3. 保存するのは「候補文字列・一致有無・照会日時」のみ(各記事フォルダの
     `wiktionary_multiword_lookup.jsonl`)。カテゴリタイトル一覧全体・
     ページ本文は取得・保存しない。
- 実測件数・所要時間は各記事の`extraction_summary.json`に記録する
  (`wiktionary_multiword_targeted_lookup_calls`/`_candidates`/
  `_elapsed_sec`)。

## Wiktionaryカテゴリタグ精度・網羅性についての観測(未検証事項の記録)

- `Category:English idioms`/`phrasal verbs`/`proverbs`は編集者が手動で
  カテゴリタグを付与する仕組みであり、口語表現・discourse marker的な
  chunk(例: "as far as"、"in terms of"のような機能的定型表現)は
  idiomとしてタグ付けされていない場合がある。これはWiktionaryの
  カバレッジの限界であり、本Trialのfallback発動率に影響し得る
  (設計doc B-1節で既に指摘されていた「Wiktionaryのidiom/phraseカテゴリ
  タグの精度・網羅性に依存する」という懸念を、実データで確認する
  形になる)。
