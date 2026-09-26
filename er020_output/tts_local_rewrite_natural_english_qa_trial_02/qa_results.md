# QA Results (7 Gates per candidate)

Management-ID: TTS-LOCAL-REWRITE-NATURAL-ENGLISH-QA-TRIAL-02

| id | type | rewritten_segment | 1.meaning | 2.role | 3.fact | 4.context | 5.natural_english | 6.localized | 7.not_full_rewrite | ALL PASS |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | single_word_swap | The service looked like AI, but the work behind it was not always done by AI alone. Now, let’s bring the main threads together. | True | True | True | True | True | True | True | True |
| 2 | short_phrase_rewrite | The service looked like AI, but the work behind it was not always done by AI alone. Now, let’s sum up the story’s main takeaway. | True | True | True | True | True | True | True | True |
| 3 | short_phrase_rewrite | The service looked like AI, but the work behind it was not always done by AI alone. Now, let’s bring the central message into focus. | True | True | True | True | True | True | True | True |
| 4 | short_phrase_rewrite | The service looked like AI, but the work behind it was not always done by AI alone. Now, let’s bring the main lesson home. | True | True | True | True | True | True | True | True |
| 5 | short_phrase_rewrite | The service looked like AI, but the work behind it was not always done by AI alone. Now, let’s sum up the key lesson. | True | True | True | True | True | True | True | True |
| candidate_main_idea_previous | single_word_swap | The service looked like AI, but the work behind it was not always done by AI alone. Now, let’s bring the main idea together. | True | True | True | True | False | True | True | False |

## Natural English Gate 理由(候補ごと)

- **1** (`The service looked like AI, but the work behind it was not always done by AI alone. Now, let’s bring the main threads together.`): This sounds more natural than a plain point-to-idea swap because 'bring the main threads together' is an established way to describe synthesizing a story in narration.
- **2** (`The service looked like AI, but the work behind it was not always done by AI alone. Now, let’s sum up the story’s main takeaway.`): This sounds more natural than a plain point-to-idea swap because 'sum up' is a common spoken transition and 'main takeaway' is idiomatic in explanatory narration.
- **3** (`The service looked like AI, but the work behind it was not always done by AI alone. Now, let’s bring the central message into focus.`): This sounds more natural than a plain point-to-idea swap because 'bring the central message into focus' is a standard, idiomatic collocation for a concluding narration.
- **4** (`The service looked like AI, but the work behind it was not always done by AI alone. Now, let’s bring the main lesson home.`): This sounds more natural than a plain point-to-idea swap because 'bring the main lesson home' uses an idiomatic emphasis expression, whereas 'bring the main idea together' is awkward.
- **5** (`The service looked like AI, but the work behind it was not always done by AI alone. Now, let’s sum up the key lesson.`): This sounds more natural than a plain point-to-idea swap because 'sum up the key lesson' is a normal concluding phrase in spoken explanatory English.
- **candidate_main_idea_previous** (`The service looked like AI, but the work behind it was not always done by AI alone. Now, let’s bring the main idea together.`): It is equally natural as the plain point-to-idea swap because it is exactly that swap, but both versions sound unnatural and stilted. A native speaker would more likely say 'sum up the main idea' or 'bring the main idea into focus.' 

## 選定結果

- status: SELECTED
- rationale: 全7 Gate PASSの候補は5件(['1', '2', '3', '4', '5'])。その中でTTS安定性ヒューリスティックのrisk flag数が最少(plural_s_risk=['lesson'], word_final_plosive=['up'])かつunchanged_ratio=0.84(より最小限の変更)である'5'を採用。Natural English Gateの理由: This sounds more natural than a plain point-to-idea swap because 'sum up the key lesson' is a normal concluding phrase in spoken explanatory English.
