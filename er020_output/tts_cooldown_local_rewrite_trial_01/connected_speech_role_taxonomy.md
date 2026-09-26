# Connected Speech Role Taxonomy(設計、Production未配線)

Management-ID: TTS-COOLDOWN-LOCAL-REWRITE-TRIAL-01

## 1. Role定義(設計)

| role | segments |
|---|---|
| NARRATIVE_ENGLISH | full_story_part1, full_story_part2, full_story_part3, comment_1, comment_2, comment_3, comment_4, preview, topic_intro, in_one_line |
| HEADING_READOUT | point_one_heading, point_two_heading |
| KEY_PHRASE | kp_en_component |

## 2. 現在の実配線(関数+明示フラグ単位、role単位ではない)

| segment | role(設計) | 現在wired? | 根拠 |
|---|---|---|---|
| full_story_part1 | NARRATIVE_ENGLISH | True | docs/pm/recon_connected_speech_scope_01.md 2節参照 |
| full_story_part2 | NARRATIVE_ENGLISH | True | docs/pm/recon_connected_speech_scope_01.md 2節参照 |
| full_story_part3 | NARRATIVE_ENGLISH | True | docs/pm/recon_connected_speech_scope_01.md 2節参照 |
| point_one | (未分類) | True | docs/pm/recon_connected_speech_scope_01.md 2節参照 |
| point_two | (未分類) | True | docs/pm/recon_connected_speech_scope_01.md 2節参照 |
| comment_1 | NARRATIVE_ENGLISH | False | docs/pm/recon_connected_speech_scope_01.md 2節参照 |
| comment_2 | NARRATIVE_ENGLISH | False | docs/pm/recon_connected_speech_scope_01.md 2節参照 |
| comment_3 | NARRATIVE_ENGLISH | False | docs/pm/recon_connected_speech_scope_01.md 2節参照 |
| comment_4 | NARRATIVE_ENGLISH | False | voice01.generate_charon_english()自体にenable_connected_speech_equivalence_layer/enable_repetition_qa引数が存在しない(Full Story 本文が使うnews_tail_fix.generate_news_narration_wide_marginとは別関数)。role taxonomy上はNARRATIVE_ENGLISHに属していても、現在の実装は関数単位で決まっているため適用されない。 |
| preview | NARRATIVE_ENGLISH | False | docs/pm/recon_connected_speech_scope_01.md 2節参照 |
| topic_intro | NARRATIVE_ENGLISH | False | docs/pm/recon_connected_speech_scope_01.md 2節参照 |
| in_one_line | NARRATIVE_ENGLISH | False | docs/pm/recon_connected_speech_scope_01.md 2節参照 |
| point_one_heading | HEADING_READOUT | False | docs/pm/recon_connected_speech_scope_01.md 2節参照 |
| point_two_heading | HEADING_READOUT | False | docs/pm/recon_connected_speech_scope_01.md 2節参照 |
| kp_en_component | KEY_PHRASE | False | docs/pm/recon_connected_speech_scope_01.md 2節参照 |

## 3. 所見

現在の適用可否はrole(NARRATIVE_ENGLISH等)単位ではなく、呼び出し関数(`voice01.generate_charon_english` vs `news_tail_fix.generate_news_narration_wide_margin`)+呼び出し側の明示フラグという、より細かい粒度で決まっている。同じNARRATIVE_ENGLISHroleに属するcomment_1-4/preview/topic_intro/in_one_lineとfull_story_part1-3は、現在の実装では異なる扱いを受ける(docs/pm/recon_connected_speech_scope_01.md 3節「事実1」参照)。

comment_4の`point`→`points`差は、Production未配線という理由以前に、OPEN-122 Equivalence Layer本体を直接呼んでも救済されない形状(`NOT_A_PHONEME_PREFIX_DROP`、ASR側がcanonical語の後ろに`s`を追加した形であり、この関数が想定する「phoneme drop」形状に一致しない)。本Trialのharness内で実行時に再確認した結果は本ファイル生成元のrun_summary.json / attempt_summary.mdを参照。
