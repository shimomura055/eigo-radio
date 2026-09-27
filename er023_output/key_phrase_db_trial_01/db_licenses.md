# db_licenses — KEY-PHRASE-DB-BASED-SELECTION-TRIAL-01 群1DB引用・ライセンス記録

Trial専用の内部照合DB。すべて非公開・非再配布(社内照合ロジックが参照
するのみ)。管理ID: KEY-PHRASE-DB-BASED-SELECTION-TRIAL-01。

## 1. CEFR-J Vocabulary Profile Version 1.6

- 取得元: http://cefr-j.org/data/CEFRJ_wordlist_ver1.6.zip (取得日時
  2026-09-27、直接HTTP GETで取得成功。ページ上は「使用許諾に同意して
  いただいてダウンロード」という案内文言があるが、実際のzipファイル
  URLはクリックスルー認証を要求せず直接取得できた。設計doc・db_survey
  で記録した引用条件をそのまま尊重する)。
- 収録: 7,801見出し語(headword/pos/CEFR、`ALL`シート)。うち144件は
  スペースを含む複数語見出し(word-only中心という設計docの記述通り、
  ただし完全にゼロではない)。
- 引用表記(公式指定形式、本Trialでの内部利用に際し記録):
  > 『CEFR-J Wordlist Version 1.6』東京外国語大学投野由紀夫研究室.
  > （URL: http://cefr-j.org/download.html より2026年9月ダウンロード）
- ライセンス: 引用を条件に研究・教育・商用利用無償(逐語は
  `docs/pm/db_survey_key_phrase_sources_01.md`4節)。本Trialは内部
  照合用途であり配布・改変公開は行わない。
- ローカルコピー: `db/cefr_j/CEFR-J_Wordlist_Ver1.6.xlsx`(Trial内部
  照合専用、外部公開・再配布しない)。

## 2. NGSL / NAWL / BSL / NGSL-Spoken

- 取得元: https://www.newgeneralservicelist.com (`.org`は乗っ取りドメイン
  のため不参照、db_survey 5節参照)。
  - NGSL: `/s/NGSL_12_lemmatized_for_teaching.csv`
  - NAWL: `/s/NAWL_12_lemmatized_for_teaching.csv`
  - BSL: `/s/BSL_120_lemmatized_for_teaching.csv`
  - NGSL-Spoken: `/s/NGSL-Spoken_12_lemmatized_for_teaching.csv`
  (すべて取得日時2026-09-27、直接HTTP GET成功、静的直リンクを`/new-
  general-service-list`等の各ページHTMLから発見)。
- 収録: 各リストの見出し語+活用形(同一行にlemma+inflected formsを
  カンマ区切りで記載、例: `abandon,abandons,abandoned,abandoning`)。
  word-only(phrase/idiom収録なし)。
- 引用表記(公式サイト記載の一般的な扱いに従い、本Trial内部記録として):
  > NGSL / NAWL / BSL / NGSL-Spoken, © Dr. Charles Browne et al.,
  > newgeneralservicelist.com. Released under Creative Commons
  > (具体的なCC変種番号はサイト上で明示確認できず、db_survey 5節の
  > とおりUNRESOLVED詳細。「商用利用を含め無償」の方針文言は明確に
  > 確認済み)。
- ライセンス: 商用利用含め無償と公式サイトに明記(db_survey 5節逐語
  引用)。CC変種の具体的な条項番号は未確認(Production採用前に確認
  推奨、Fableレビュー論点6で既指摘)。
- ローカルコピー: `db/ngsl/*.csv`(Trial内部照合専用)。

## 3. Wiktionary(英語版、CC BY-SA 4.0 / GFDL)

- 取得方法: **フル dump は取得していない**。MediaWiki API
  (`action=query&list=categorymembers`)経由で以下3カテゴリのタイトル
  一覧を取得(ns=0のみ、pageid/title、本文・定義文は取得していない)。
  - `Category:English idioms`: 10,632件(22 API call、31.9秒)
  - `Category:English phrasal verbs`: 5,169件(11 API call、12.2秒)
  - `Category:English proverbs`: 1,588件(4 API call、4.8秒)
  - 合計: 37 API call、約48.9秒、タイトル文字列のみ保存(本文非取得)。
- **`Category:English multiword terms`(225,910件)は取得方法を変更**
  (詳細は`wiktionary_ingest_log.md`)。全件タイトルdumpは規模が大きく
  Trialの目的(6本文の候補照合)に対して非効率なため、6本文から生成
  した2〜5-gram候補のうち他DB未一致のものに限定し、候補単位で
  `action=query&titles=<候補1>|<候補2>|...&prop=categories&
  clcategories=Category:English%20multiword%20terms`を50件バッチで
  照会するtargeted lookup方式に切り替えた(dump全体は取得していない、
  カテゴリタグの有無のみ確認、ページ本文は取得していない)。
- ライセンス: CC BY-SA 4.0(商用可・ShareAlike条件あり)。本Trialは
  内部照合専用DBとして保持し、外部への再配布・公開は行わない
  (db_survey 9節)。将来Wiktionary由来データを含む複合成果物を外部
  公開する場合は法務確認が必要(未解決事項として記録するのみ、本
  Trialでは実施しない)。
- ローカルコピー: `db/wiktionary/idioms.json` / `phrasal_verbs.json` /
  `proverbs.json`(タイトルのみ、Trial内部照合専用)。multiword terms
  のtargeted lookup結果は各記事フォルダの`wiktionary_multiword_lookup.jsonl`
  に記録(候補・一致有無・照会日時のみ、カテゴリ一覧全体は保存しない)。

## Trial終了後の扱い

上記ローカルコピーはすべてTrial専用(`er023_output/key_phrase_db_trial_01/`)
に閉じ込め、Production経路(`er003_key_words_*`)へは一切配線していない。
Production採用の判断は`APPROVED_FOR_PRODUCTION`をユーザーが宣言した後、
別タスクで改めてライセンス条件(NGSL CC変種番号・CEFR-J引用掲載場所・
Wiktionary ShareAlike運用ルール、Fableレビュー論点6)を確定する。
