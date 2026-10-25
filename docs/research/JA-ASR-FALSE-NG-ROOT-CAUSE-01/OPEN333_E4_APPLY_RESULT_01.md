# OPEN333_E4_APPLY_RESULT_01(JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_14、2026-10-26、API 0・実費0円)
区分=承認済み不具合是正(11-8。新仕様・新しい受理クラスなし)。Opus短縮レビュー=`OPUS_REVIEW_02_OPEN333_E4.md`(条件付き同意、M-1〜M-4反映)。計画=`OPEN333_E4_APPLY_PLAN_01.md`。E4-Nは見送り(A4に触れる)。

## 1. 変更
- `er011_ja_asr_variant_layer_01.py`: 定数`CANDIDATE_E_CASCADE_DIFF_RETURN=True`(env/flag/引数で切替不可)。Candidate E分岐で`_rej`判定の後・`_pass`の前に、`content_diffs`のcascade_eligible差分(キー欠落=cascade扱い)が残れば`protected.candidate_e_cascade_diffs`を記録して既存`_cascade()`を返す。**M-1: try/exceptはcascade_diffsの計算・記録だけを囲む**(例外時はPASSにせずCascade)。E3の`_rej`判定は囲まない(E3 helper例外は従来どおりNone=TCM)。
- `er007_ja_secondary_asr_01.py`: adapterが`candidate_e_cascade_diffs`を`asr_judgement.candidate_e_cascade_return`へ読取専用複写(発火時のみ、判定不変)。
- `er007_ja_asr_validator_01.py`: コメント+`is_entity_like_mismatch_ja`のdocstring注記(混在diffsでFalse、統一judge経路では未使用)。
- test: `er011_ja_asr_variant_layer_candidate_e_cascade_return_test_01.py` 14件(既定/ON-OFF/ctrl/env非依存/例外fail-closed/M-1/M-3/M-4/監視field)。
## 2. 一致検証(`open333_e4_prod_parity_01.py`、出力`.out.txt/.json`)
4230キー(Primary段2956[adapter state/reason/label+key集合]+Secondary対1274): **off≡head 差0(asr_judgementのkey集合2,956行を含む)・on≡proto 差0**(protoの説明文reasonのみ正規化)。on vs head変化152キー=PASS→非PASS 148+Secondary label変化4(受理acc/orth変化0)。**非PASS→PASS 0**。新field発火行はON 148キー、head/offは0。
## 3. runtime発火確認(`open333_e4_runtime_fire_01.py`、API 0)
1,514 attempt: 発火ON=74(実データ4+合成70)、OFF=0。HEAD(OFF)比遷移=PASS→NG_SECONDARY_UNAVAILABLE(Azure stub不在)74のみ、非PASS→PASS 0。Azure応答注入: 原稿どおり→PASS_WITH_WARNING 74/74、Primaryと同じ誤り→NG_BOTH 74/74。実データ4行=Meta/Muse2行・ヴェラ→ベラ・走れメロス→走レメラス。
## 4. 回帰
遮断harness下43 file: **1,104 passed / 8 failed**。8件は委任_12の既知失敗と同一(er007_ja_secondary 2・er109 5・static audit inventory 1)。api.openai.com遮断試行12件は委任_12と同数(既存失敗test由来、新規test・評価scriptは0)。
## 5. 監視・報告条件(`open333_first_run_tally_01.py <run_dir>`、M-2)
`e4_fired`/`e4_pairs`/`e4_outcomes`(PASS_WITH_WARNING・REGEN_THEN_PASS・HR・STOP・OTHER_NONPASS)。1runで3件超→Fable報告。**E4発火行がHRに到達したら1件でも報告**(`alert_e4_hr`)。対処はE4 rollbackではなく表記正規化(ユーザー承認が必要な別件)の検討。rollback=定数False または適用commitのrevert。
## 6. 残課題
Candidate E本体は同形異音(今日→こんにち等)でもPASSし得る(承認済み挙動。分類=実害なし、別件観察)。E4-N再検討は『A4見直し』としてユーザー判断D。
