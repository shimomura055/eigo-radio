# OFFLINE_RESOLVE_01 既存確定済みX/Y/Z run全件のハイライト解決(API 0、read-only)

生成: `py -3 docs/research/SLOT-23-CONSUMER-DESIGN-01/tools/offline_resolve_01.py --md <本ファイル>`(JSON=`OFFLINE_RESOLVE_01.json`)。
表示範囲=Full Story本文(X=parts.json part1-3 / Y=parts.json segments全件 / Z=segment_plan clips(Part別))。

| Family | level | run | 判定 | 項目数 | 装飾 | ③訳 | NOTICE | ISSUE |
|---|---|---|---|---|---|---|---|---|
| X | a2 | ai_island_temple__run_form_prod_01 | OK | 10 | 10 | 5 | HL_OCCURRENCE_RELOCATED:p_31e10e6357 | 0 |
| X | b1b | ai_island_temple__run_form_prod_01 | OK | 10 | 10 | 5 | 0 | 0 |
| X | a2 | part2_hr_evidence_01__run_gpg5_x_01 | OK | 3 | 3 | 0 | 0 | 0 |
| X | b1b | part2_hr_evidence_01__run_gpg5_x_01 | ISSUE | 5 | 4 | 0 | HL_OCCURRENCE_RELOCATED:p_b4c590d854 | HL_NOT_IN_DISPLAY:p_bbe6b2b09a |
| Z | b1b | run_gpg5_z_01 | OK | 3 | 3 | 0 | 0 | 0 |
| Z | a2 | run_kcp4_ev_z_01 | OK | 7 | 7 | 2 | 0 | 0 |
| Z | b1b | run_kcp4_ev_z_01 | OK | 3 | 3 | 0 | 0 | 0 |
| Y | a2 | run_gpg5_y_01 | OK | 3 | 3 | 0 | 0 | 0 |
| Y | b1b | run_gpg5_y_01 | OK | 5 | 5 | 0 | 0 | 0 |

合計: 9 run-level、ISSUE=1件、TOOL_ERROR=0。

- ISSUE X/b1b/part2_hr_evidence_01__run_gpg5_x_01: `HL_NOT_IN_DISPLAY` p_bbe6b2b09a: ['S41'] のいずれも表示範囲(Full Story本文)に無い
  - 変種(表示範囲に In one line を加える): OK、NOTICE=['HL_OCCURRENCE_RELOCATED']

## AI島(`ai_island_temple__run_form_prod_01`)の全項目

### a2
| 区分 | 本文表層形 | used_form | 文 | 単位 | 再配置 | 装飾 |
|---|---|---|---|---|---|---|
| 1 | carried over | carry over | S20 | full_story_part2 | - | True |
| 1 | taken a detour | take a detour | S29 | full_story_part2 | - | True |
| 1 | card to play | card to play | S40 | full_story_part3 | - | True |
| 3 | made a difference | make a difference | S38 | full_story_part3 | - | True |
| 3 | separately | separately | S37 | full_story_part3 | - | True |
| 3 | feature | feature | S17 | full_story_part1 | - | True |
| 3 | strategy | Strategy | S8 | full_story_part1 | S2 | True |
| 3 | setup | setup | S24 | full_story_part2 | - | True |
| 2 | worth paying attention to | worth paying attention to | S34 | full_story_part3 | - | True |
| 2 | obstacle | obstacle | S12 | full_story_part1 | - | True |

### b1b
| 区分 | 本文表層形 | used_form | 文 | 単位 | 再配置 | 装飾 |
|---|---|---|---|---|---|---|
| 1 | carried over | carry over | S18 | full_story_part2 | - | True |
| 1 | called on | call on | S20 | full_story_part2 | - | True |
| 1 | taken a detour | take a detour | S24 | full_story_part2 | - | True |
| 2 | card to play | card to play | S34 | full_story_part3 | - | True |
| 2 | obstacle | obstacle | S12 | full_story_part1 | - | True |
| 3 | looked at separately | look at separately | S31 | full_story_part3 | - | True |
| 3 | exploration | exploration | S11 | full_story_part1 | - | True |
| 3 | technique | technique | S25 | full_story_part3 | - | True |
| 3 | overlook | overlook | S29 | full_story_part3 | - | True |
| 3 | erased | erase | S19 | full_story_part2 | - | True |


## 所見
- 9 run-levelのうち8がISSUE 0。残る1件(X `part2_hr_evidence_01__run_gpg5_x_01` b1b ①`year over year`=S41)は**データ起因**: 当該語句は本文の「In one line」節(parts.json `in_one_line`、Full Story part1-3の外)にしか出現しない(`occurrence_sentence_ids=['S41']`)。規則の誤りではなく、候補生成が`article.md`全体(In one line節を含む)を対象にしたため。変種(表示範囲に`in_one_line`を加える)ではISSUE 0。判断は配線班/Fable(表示範囲の定義=Full Storyのみ か In one lineを含むか。既定の表示範囲は変更していない)。
- 文分割は`er030.build_sentence_units`と同一実装のコピーを使用(この環境は`wordfreq`未導入でer030をimportできないため。import可能な環境では本物を使う)。同一性は全run・全候補の`source_sentence`と文IDが一致すること(`HL_SENTENCE_MISMATCH`/`HL_SENTENCE_ID_UNKNOWN`が0件)で実証済み。
- Zの表示単位はsegment_plan clips(Part別)で代用(実ページのscriptと同文であることは配線班が確認)。
