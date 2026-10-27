# COST_05 費用(委任_05、JPY。`make_real_spent_fn`/`compute_cost_jpy_so_far`によるcost_log/raw_usage_log集計。コピー前の費用は除外)
| 経路 | 内訳 | JPY |
|---|---|---|
| X Std/Adv(`part2_hr_evidence_01__run_gpg5_x_01`) | raw_usage_log: part2_cand_a2 x1, part2_expl_a2 x1, part2_cand_b1b x2, part2_expl_b1b x1(Part 1は再利用)。finalize/player追加 0 | 1.26 |
| Y Std/Adv(`run_gpg5_y_01`) | cost_log: part2_expl_b1b x3(初回のauto採用Top1生成1+退避後の再生成2)、part2_cand_a2 x1、part2_expl_a2 x2、part2_cand_b1b x1。finalize未実施 | 1.2846 |
| Z Std/Adv(`run_gpg5_z_01`) | cost_log: part2_cand_b1b x2(初回0件+再抽出1件)、part2_cand_a2 x1、part2_expl_b1b x1、kp(Redundancy QA)x1 | 0.7532 |
| **合計** | 音声/TTS 0 | **約3.30** |
上限 JPY150 比 約2.2%。案件見積300円以下かつ承認済みScope内(7-7)。guard: X --budget-jpy 10 / Y --approved-budget-jpy 10 / Z --approved-budget-jpy 20。

## 委任_05C 追記
| 経路 | 内訳 | JPY |
|---|---|---|
| Y 再開(`run_gpg5_y_01`) | stage=kp x3(final_redundancy_qa、gpt-6-luna、in 1757/1903/1694・out 714/1431/591)。part2系 0、TTS 0。runner累計 1.5892(05時点1.2846との差) | 0.3046 |
| **05+05C合計** | 音声0 | **約3.61**(上限150の2.4%、05C上限10内) |
