# EVIDENCE_03: Family Y E-1(宅配 redelivery_fee run_01)正式runtime証拠(委任_09、2026-10-26、新規API 0・今回の費用0円)

対象run=`er121_output/family_y_production_01/redelivery_fee/run_01`。事実のみ記録。PRODUCTION_WIRED判定語はFableが付ける(下表の『Status候補』は候補と根拠のみ)。

## 1. 完走結果(HEAD=2a66b4eb6、起動1回: `--stages gate,assemble,pages,page_verify`、2026-10-26 06:45:33〜06:45:55 JST、rc=0、`console_ypl9_launch1.log`)
- ユーザー承認(逐語=`docs/pm/delegation_log/2026-10-26_FAMILY-Y-PRODUCTION-LAUNCH-01_USER_E1_APPROVAL.md`)を反映: `er121_e1_hr_adopt_r0_01.py --apply` 3本 rc=0、`approved_by="user"`、approved_at 06:45:07/06:45:11/06:45:15頃。記録=`a2/audit/ypl7_user_approval_record_{preview,y_voice_1}.json`・`b1b/audit/ypl7_user_approval_record_y_voice_1.json`・`{a2,b1b}/audit/human_approved_segments.json`、バックアップ=`*.pre_ypl7_adopt.wav`(wav不追跡)・`*.pre_ypl7_adopt_backup.json`。
- ③ a2 `y_voice_1`: `hr_adopt_prep/y_voice_1_slowed_asr_recheck.json`(recheck_pass=true・status=OK・ASR PASS `primary_pass`)の`slowed_wav_sha256`=c3f59b0040d99d02…=採用後`a2/narration/y_voice_1.wav`のsha256(実測一致)。減速実測5.964%(目標6%)、46.465秒。
- gate: b1b=PASS・a2=PASS(`gate_summary.json`)、assemble: 両levelとも成功(`final_manifest.json` assembled)、pages・page_verify: ok=true・violations=[]・part2_verified(index_page=OK, part1_blocks=1, part2_blocks=1)・kp_selection_verified b1b ok(`page_verify_local.json`)。`final_manifest.json`生成。
- 限定公開: `<run>/pages/{index.html,audio/}`→`user_test/family_y_production_redelivery_fee_01/`(`listening/`は残置、audio=mp3 52本+index、wav 0)。`user_test_page_standard_check_01`=PASS rc=0、`y_page_notice_check_01`=ok rc=0。URL=`https://shimomura055.github.io/eigo-radio/user_test/family_y_production_redelivery_fee_01/index.html`(push後)。

## 2. Y Part 2 / KP / 文法HR の実走事実(生成は委任_06〜の前走、今回再実行0)
- Part 2(文法解説)=`study_text/part2_result.json`: status=SELECTED、Advancedのみ、選定source=`auto_top1`(candidate g1de62b0de2、tier T1、feature_class CMP[asを用いた比較]、段落P4)、生成2026-10-25 22:04、ページに『Grammar & Sentence Structure』1ブロック(page_verify part2_blocks=1)。Part 1(Vocabulary & Expressions)も同ページ(part1_blocks=1、5件)。
- Trial-08選定方式: 候補`grammar_candidates.json`(2候補、`candidates_sha256` d09c110a…)、`top_ids`・tier_table付き。
- 文法HR=`study_text/grammar_human_review.json`: status=`UNREVIEWED_AUTO_ADOPTED`(HRなし宣言`d_42edcb6d9e37`、Fable代行、user_ref=2026-10-25 USER §10-5)。KP HR=`key_phrases/b1b/kp_human_review.json`: status=`UNREVIEWED_AUTO_ADOPTED`(宣言`d_bf821f18b541`→文法用に新規宣言[`kp_review_mode.json`]、KP選定signature 23afe0b9…、`final_redundancy_qa`=REDUNDANCY_PASS)。**人間が候補を選ぶHR経路(PENDING_REVIEW→rc=4→`grammar-select`/KP確定)のY実走は無し**(『HRなし』経路のみ。`kp_review_pending.json`にPENDING_REVIEWのgrammar行が残るが、`grammar_human_review.json`はAUTO_ADOPTED=確定済み・page_verify/`_assert_study_ready`通過)。
- 費用: 今回0円。run_01 cost_log=175行、runner累計spent=52.134円(e2e_stage_log)。

## 3. 機能×Family表(Y列。X/Zは既存SSOT[CURRENT_SPEC『KP Human Review…Family別Status』]のとおり)
| 機能 | Yの事実 | Status候補と根拠 |
|---|---|---|
| ①Part 2文法解説 | SELECTED、ページに表示、page_verify part2_verified OK、gate b1b/a2 PASS | 正式経路でrunnerが生成・検証済み=`PRODUCTION_WIRED`候補(Y初run) |
| ②Trial-08選定方式 | 2候補・T1/rank1をauto_top1で確定、tier_table記録 | 同上(runnerのpart2_cand stage経由で実走) |
| ③KP HR | b1bのみ。UNREVIEWED_AUTO_ADOPTED(HRなし宣言)。HR候補を人が選ぶ経路は未実走 | 『HRなし』経路=実走済み。『HRあり』経路=Y未実走(Z R3実績のみ)=PRODUCTION_WIRED(HRなし経路)/HRあり未確認 |
| ④文法HR | UNREVIEWED_AUTO_ADOPTED(HRなし宣言)。grammar-select経路は未実走 | 同上 |
| ⑤OPEN-517 F1+F2 | r5計測付き判定あり、F1/F2発火0、READING_MATCHでfinal_gate適用された行0(`OPEN517_RUNTIME_EVIDENCE_03_Y.md`) | コード到達(r5計測)は確認。X/Z基準『適用1件以上』は未達=『runtime未確認』のまま維持が妥当(Fable判定) |
| ⑥E3/E4(OPEN-333) | 発火0、alertなし | 発火事例なし=到達の証拠は『通過(tallyで集計可能)』のみ |
