# conflict_check.md — KEY-PHRASE-LEVEL-SPEC-TRIAL-01

既存Production Key Phrase仕様(`er003_v1_n3_01_scaffold_generate.py`の
`run_key_phrases`/`run_key_phrase_selection`が呼ぶ`er003_b1_p2_keywords.py`
[選定]/`er003_key_words_canonicalization.py`[正規化]/
`er003_key_words_production.py`[selector/schema本体、L方式=Listening
Blocker Rankingの本番版]、およびschemaの元定義
`er003_key_words_min_unit.py`)を実際に読み、本Trialの新方針との相違を
事実として列挙する。**このTrialは既存関数を一切import・呼び出しせず、
`er017_key_phrase_level_spec_trial_01.py`は独立したPrompt・schema・
API呼び出しを新規に持つ**(既存Production仕様は無変更)。

## 1. 個数
- 既存: `PRODUCTION_ITEM_COUNT = 5`(A2/B1共通、5件固定)。
- 新Trial: 5個固定。
- 相違なし(件数のみ一致)。

## 2. Standard/Advanced(A2/B1)の選定基準の違い
- 既存: A2(`er003_v1_iran01_a2_generate.py`)もB1相当
  (`er003_b1_p2_keywords.py`)も**同一のPrompt template**
  (`er003_v1_translator_briefs/b1_p2_keywords_l_prompt_template.txt`)を
  そのまま再利用している。選定基準はレベルに関わらず同一で、「初回
  リスニングで意味を取れず、その後の理解を止める可能性が高い英語表現」
  (Listening Blocker Ranking、L方式)を支援価値の高い順に選ぶことが
  最優先原則。優先順位は明記されており「初回音声での処理困難、未知の
  可能性、瞬時の推測困難、本文の事実・感情・面白さへの影響、記事内
  重要度、汎用性の順」で、**汎用性(reusability)は優先順位の最後**。
- 新Trial: Standard/Advancedで別々のPromptを持ち、「汎用性・学習価値・
  自然な英語のまとまり」を最優先とし、「難しいだけ・記事固有なだけの
  語を優先しない」と明記(既存の優先順位と方向性が逆)。
- **相違点(事実)**: 既存はレベル差なし単一Prompt・難易度最優先/新
  Trialはレベル別2種類のPrompt・汎用性最優先。これはPromptの目的・
  優先順位の設計思想が異なる(どちらが正しいかの優劣判断はしない、
  事実列挙のみ)。

## 3. Topic Word概念
- 既存: 該当する概念・フィールドなし(`_ITEM_SCHEMA_PROPERTIES`に
  topic_word相当のフィールドはない)。
- 新Trial: `is_topic_word`(bool)フィールドを持ち、5個中最大1個まで
  許容する任意枠。
- **相違点**: 既存仕様には存在しない新概念。

## 4. 解説言語(Standard=日本語/Advanced=英語)
- 既存: A2/B1いずれも`ja_gloss`(日本語グロス)のみを出力し、英語での
  解説フィールドは存在しない(`er012_output/.../meta/b1b/key_phrases/
  keywords_canonicalized.json`の実例でも、B1[Advanced相当]記事の
  Key Phraseに`japanese_gloss`のみが付与されており、英語解説は無い)。
- 新Trial: Standardは`explanation_ja`(日本語)、Advancedは
  `explanation_en`(英語)と、レベルで解説言語を切り替える新仕様。
- **相違点**: 既存はレベルに関わらず解説言語が常に日本語。新Trialは
  Advancedのみ英語解説という新方針。

## 5. Phrase表記(スロット記法)
- 既存: `display_phrase`は1〜5語、完全文/節/有限助動詞を含む形は禁止。
  動詞は原則基本形へ正規化。"..."のようなプレースホルダー記号は
  **日本語グロス側では明示的に禁止**(`b1_p2_keywords_l_prompt_
  template.txt`に「『…』のようなプレースホルダー記号は使わないで
  ください」と明記)。英語表現側(display_phrase)にも"..."スロット
  記法の使用例は見当たらない。
- 新Trial: 英語Phrase側で"..."スロット記法を明示的に許容・例示
  (`put ... on hold`、`replace A with B`)。
- **相違点**: 既存は少なくとも日本語グロス側で"..."禁止と明記、英語
  Phrase側でも前例なし。新Trialは英語Phrase側で明示的に許容。

## 6. 出力構造(Pipeline段数・フィールド構成)
- 既存: 選定(selection)→正規化(canonicalization)→冗長性QA
  (redundancy QA)の3段構成。selectionのschemaは`rank/display_phrase/
  source_span/source_sentence/ja_gloss/phrase_type/normalization_type/
  normalization_note/selection_reason/listening_difficulty_reason/
  inference_transparency/topic_exposure_dependency/comprehension_
  impact/figurative_or_emotional_value/spoiler_risk/portfolio_
  category/portfolio_substitution/portfolio_substitution_reason`の
  18フィールド(1項目あたり)。canonicalization段でさらにQA項目
  (`qa.*`12項目+`qa_overall_status`+`reasoning`)が付与される。
- 新Trial: 単一段構成。1項目あたり`phrase/is_topic_word/
  example_sentence/reason_ja/explanation_ja(or _en)`の5フィールドの
  みで、正規化・冗長性QA・多観点QAは行わない。
- **相違点**: 既存は多段QA・多観点フィールドを持つ本番運用向け構造。
  新Trialは評価目的の最小構造(意図的な簡略化、Trial範囲として妥当)。

## 7. STOPすべき競合か(判定)
- 上記5点はいずれも**新Trial専用の独立したPrompt・schema・API呼び出し
  で実現でき**、既存Production関数(`run_key_phrases`/
  `run_key_phrase_selection`/`bk.*`/`kc.*`/`prod.*`/`p2g.*`)への変更や
  呼び出しを一切必要としない。`er017_key_phrase_level_spec_trial_01.py`
  はこれら既存モジュールを一切importしていない(隔離達成)。
- したがって「既存Production仕様を変更しないとTrialできない」という
  STOP条件には**該当しない**。Trialを既存仕様のまま続行する。
