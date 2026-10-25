# OPEN517_RUNTIME_EVIDENCE_03_Y: Family Y E-1(宅配 redelivery_fee run_01)のOPEN-517 F1+F2 / OPEN-333 E3・E4 runtime証拠(FAMILY-Y-PRODUCTION-LAUNCH-01 委任_09、2026-10-26、API 0)

**種別=事実記録(PRODUCTION_WIRED判定語はFableが付ける)。** 対象=`er121_output/family_y_production_01/redelivery_fee/run_01`。新規API呼出0(今回の起動は gate,assemble,pages,page_verify のみ)。

## 1. tally(`open517_first_run_tally_01.py` / `open333_first_run_tally_01.py`、出力=run_01/tally517_ypl9.json・tally333_ypl9.json)
| 項目 | 値 |
|---|---|
| attempts_scanned | 58 |
| reading_match_attempts(Primary equivalence_basis=READING_MATCH) | 2(= a2 `comment_2` attempt1 とそのpre_ypl7_adopt_backup複製。実質1判定) |
| a_final_gate_diff(F1でNG化) / b_demote_p3 | 0 / 0 |
| d_f2_fired(F2) / e_part_of_larger / e_weak_diff | 0 / 0 / 0 |
| r5_present | 2(tally集計。tally対象はattempts_log。review_lock_state等のr5付き判定は下記2) |
| r5_measurement_errors | 0 |
| r5_secondary_provenance_incomplete | 0 |
| head_evidence.READING_MATCH_FINAL_GATE | true |
| alert_rollback_review / alert_demote_review | false / false |
| OPEN-333: phonetic_match_pass / e3_fired / alert | 2 / 0 / false |
| OPEN-333: e4_fired / e4_outcomes(HR・STOP含む) / alert_e4_count / alert_e4_hr | 0 / 全0 / false / false |

## 2. 判定の世代区別(F1+F2適用commit 5e50613f5=2026-10-25T21:56:35+09:00、R-5 7261b9fff=22:45:49[計測コードは58cbf7786 22:36:33])
- **READING_MATCH経路の判定は1件のみ**: a2 `comment_2` attempt1(ファイル時刻 2026-10-25 21:15:10=F1適用commit**より前**、`asr_judgement`に`r5`なし、`final_gate={"applied": false, "skipped": "approved_equivalence:READING_MATCH"}`、`reason_code=primary_pass_approved_equivalence:READING_MATCH`、`reused_from_previous_run`系キーあり)。**よって F1+F2適用後に生成された、READING_MATCHで`final_gate`が適用された行は0件**(委任文基準『READING_MATCH経路でfinal_gate適用1件以上』は**未達**)。
- **F1/F2/R-5コードが評価した(rベクトル`r5`付き)判定**: a2 `preview` attempt4・5・6(attempt jsonの時刻 2026-10-25 22:19:58〜22:20:20=F1適用commit**以降**、R-5 commit[22:45:49]**より前**だがR-5計測コードは作業ツリーで有効=`r5`が付与されている)。a2 `y_voice_1`(attempts_log[0..1]=PASS/primary_pass、final_gate applied=true・value_guard EQUAL、fallback=NG_BOTH、post_slowdown_cascade=PASS_WITH_WARNING secondary_confirmed)。各`r5.f1`=`{rollback_const_READING_MATCH_FINAL_GATE: true, reading_match_primary_pass: false, final_gate_rejected: false, demoted_p3: false}`、`r5.f2.enabled=false`(かな数詞なし)。
- `secondary.provenance_complete`=True・`secondary.model_id`=`azure-speech-stt`(preview 3行、Primary=`gpt-4o-mini-transcribe`)。`canonical_text`あり。
- 減速後再検証(`a2/hr_adopt_prep/y_voice_1_slowed_asr_recheck.json`、2026-10-25 23:22、sha c3f59b00…): 英語ASR。`asr_judgement.state=PASS`・`reason_code=primary_pass`・`final_gate={applied:true, value_guard:EQUAL, negation_diff:false}`。英語のスキーマは不変なので`r5`・`canonical_text`なし(仕様どおり)。

## 3. 事実の要点
1. Y経路でF1(READING_MATCH最終ゲート)・F2(かな数詞統一)の**コードは実行され**、`r5`計測が付いた(preview・y_voice_1)。ただし**READING_MATCH Primary PASSで最終ゲートが評価された事例はこのrunに無く**、F1/F2とも発火0。X/Zと同一の受入基準(READING_MATCH経路で適用された行1件以上)は**本runでは満たされていない**(Y=runtime証拠は『r5計測のみ』)。
2. a2 `preview`はF1+F2適用後(attempt4〜6)もNG_BOTH(Primary・Azureとも『思い通りに』転写で正本『思いどおりに』と表記差、`primary.equivalence_basis`なし)。**F1/F2では救えない型**(E1_HUMAN_REVIEW_01 §4/OPEN-515の根本原因側)。ユーザー試聴承認で採用した(`approved_by=user`、2026-10-26)。
3. E3/E4はこのrunで発火0、alertなし。
4. 追加の正式runtime証拠を取るなら、READING_MATCHに当たる日本語segmentを含む次のY正式run(E-3 SNS等)での再tallyが必要(API追加支出が出る場合は別判断)。
