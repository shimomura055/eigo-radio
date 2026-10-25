# BUDGET_LOG_01(委任_04 実費ログ。2026-10-25 JST)

管理ID: KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01 委任_04 兼 PART2-GRAMMAR-PRODUCTION-WIRING-01 委任_04 / Cap 150円 / 日次1,500円(委任文)
算出元: X=`compute_cost_jpy_so_far(raw_usage_log.jsonl)`、Z=`e2e_stage_log.jsonl` `spent_jpy_cumulative`。

| run | 内容 | 実費(円) | 備考 |
|---|---|---|---|
| R0 | Z the_tell_tale_heart 旧run複製 `--stage kp`(Step A''=0件、Part 1再生成) | 0.37 | KP HRが発動しない対象と判明 |
| R1 | X・HRあり 完走(scaffold 4.09[support/KP候補/Part 1/Part 2]+TTS/ASR/Azure 14.04) | 18.13 | openai 4.25 / gemini_batch 6.33 / openai_asr 3.67 / azure 3.87 |
| R2 | X・HRなし scaffold+TTS(comment_4 HR Lockで停止) | 18.32 | openai 4.45 / gemini_batch 6.26 / openai_asr 3.40 / azure 4.20 |
| R3 | Z melos・HRあり(KP候補/文法候補+再抽出/finalize/解説/Part 1) | 2.90 | 完成段未実施(STOP) |
| R4 | Z melos・HRなし 完走(差分TTS含む) | 5.72 | |
| **合計** | | **45.44** | Cap 150円の30.3%(80%=120円未満) |

- seed不一致で起動前STOPした3回(gift_of_the_magi/monkeys_paw、A=API 0)と`melos` R3の1回目試行: 費用0。
- 日次: `daily_dev_cost_01.py` の `adopted_jpy` は 23:15時点 1,232.5円(他agent・他案件を含む全体値。着手前は1,059.4円)。本委任分の増加は上表45.44円以内。日次1,500円を超過していない。
- 委任文の「Cap 150円[委任_02のmock漏れ推定≤25円を含む]」の25円は本表に含めていない(委任_02の別枠。未確認)。
