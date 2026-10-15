| run | clip | role | lang | status | has asr_judgement | state | reason | slot/ver | Secondary called | azure calls | value_guard | slowdown | tts used |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| zep2/run/a2 | topic_intro_en | topic_intro | en | OK | True | PASS | primary_pass | 1/v0 | False | 0 | NO_VALUES | None | None |
| zep2/run/a2 | japanese_title | japanese_title | ja | OK | True | PASS | primary_pass | 1/v0 | False | 0 | NO_VALUES | None | None |
| zep2/run/a2 | preview | PREVIEW | ja | OK | True | PASS | primary_pass_approved_equivalence:READING_MATCH | 1/v0 | False | 0 | None | None | None |
| zep2/run/a2 | comment_1 | COMMENT | ja | OK | True | PASS_WITH_WARNING | secondary_exact_resolves_ambiguous | 1/v0 | True | 1 | None | None | None |
| zep2/run/a2 | comment_2 | COMMENT | ja | OK | True | PASS | primary_pass | 1/v0 | False | 0 | EQUAL | None | None |
| zep2/run/a2 | comment_3 | COMMENT | ja | OK | True | PASS | primary_pass_approved_equivalence:READING_MATCH | 1/v0 | False | 0 | None | None | None |
| zep2/run/a2 | full_story_part1_c1 | FULL_STORY | en | OK | True | PASS_WITH_WARNING | secondary_confirmed | 1/v0 | True | 1 | NO_VALUES | True | 1 |
| zep2/run/a2 | full_story_part1_c2 | FULL_STORY | en | OK | True | PASS | primary_pass | 1/v0 | False | 0 | NO_VALUES | True | None |
| zep2/run/a2 | full_story_part2_c1 | FULL_STORY | en | OK | True | PASS | primary_pass_approved_equivalence:TIER1_NUMERIC_EQUIVALENCE | 1/v0 | False | 0 | None | True | 1 |
| zep2/run/a2 | full_story_part3_c1 | FULL_STORY | en | OK | True | PASS | primary_pass_approved_equivalence:TIER1_NUMERIC_EQUIVALENCE | 1/v0 | False | 0 | None | True | 1 |
| zep2/run/a2 | kp1_english | KEY_PHRASE | en | OK | True | PASS | primary_pass | 1/v0 | False | 0 | NO_VALUES | None | None |
| zep2/run/a2 | kp1_japanese_meaning | KEY_PHRASE | ja | OK | True | PASS | primary_pass | 1/v0 | False | 0 | NO_VALUES | None | None |
| zep2/run/b1b | topic_intro_en | topic_intro | en | OK | True | PASS | primary_pass | 1/v0 | False | 0 | NO_VALUES | None | None |
| zep2/run/b1b | preview | PREVIEW | en | OK | True | PASS | primary_pass | 1/v0 | False | 0 | NO_VALUES | None | None |
| zep2/run/b1b | comment_1 | COMMENT | en | OK | True | PASS_WITH_WARNING | primary_pass | 1/v0 | False | 0 | NO_VALUES | None | None |
| zep2/run/b1b | comment_2 | COMMENT | en | OK | True | PASS | primary_pass_approved_equivalence:TIER1_NUMERIC_EQUIVALENCE | 1/v0 | False | 0 | None | None | None |
| zep2/run/b1b | comment_3 | COMMENT | en | OK | True | PASS | primary_pass_approved_equivalence:TIER1_NUMERIC_EQUIVALENCE | 1/v0 | False | 0 | None | None | None |
| zep2/run/b1b | full_story_part1_c1 | FULL_STORY | en | OK | True | PASS_WITH_WARNING | primary_pass | 1/v0 | False | 0 | NO_VALUES | None | None |
| zep2/run/b1b | full_story_part1_c2 | FULL_STORY | en | OK | True | PASS | primary_pass | 1/v0 | False | 0 | NO_VALUES | None | None |
| zep2/run/b1b | full_story_part2_c1 | FULL_STORY | en | OK | True | PASS | primary_pass_approved_equivalence:TIER1_NUMERIC_EQUIVALENCE | 1/v0 | False | 0 | None | None | None |
| zep2/run/b1b | full_story_part3_c1 | FULL_STORY | en | OK | True | PASS | primary_pass_approved_equivalence:TIER1_NUMERIC_EQUIVALENCE | 1/v0 | False | 0 | None | None | None |
| zep2/run/b1b | kp1_english | KEY_PHRASE | en | OK | True | PASS | primary_pass | 1/v0 | False | 0 | NO_VALUES | None | None |
| zep2/run/b1b | kp1_explanation | kp_expl_en | en | OK | True | PASS | primary_pass | 1/v0 | False | 0 | NO_VALUES | None | None |

```json
{
 "n_clips": 23,
 "n_ok": 23,
 "n_with_asr_judgement": 23,
 "ok_without_asr_judgement": [],
 "false_accepts_value_or_negation": [],
 "n_pww": 4,
 "sec_called_clips": 2
}
```
