# OPUS_REVIEW_REQUEST_02: A-1 Production配線(条件C: 重要変更のProduction採用提案前)

管理ID: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 / 2026-10-23。依頼はFableが配線実施委任の直前に行う(本ファイルは論点整理のみ。レビュー自体は未実施)。対象設計=WIRING_DESIGN_01.md。前提=OPUS_REVIEW_01(条件A)の必須5件はTrialで反映済み。A-1は既にユーザー承認済み(APPROVED_FOR_PRODUCTION)のため、レビュー対象は「承認済み仕様の実装の安全性」であり、仕様の是非ではない。

## 論点(判定を求めたい点)
1. **validator拡張の置き場所**: 閉集合`_PERSON_DEPENDENT_TO_GENERIC`を拡張せず、新関数`kc.reference_pair_ok`をer105 `is_valid_inflection_normalization`の窓判定へ`or`で足す案(WIRING K2/K5)は、gloss側`_CONCRETE_PERSON_EN`(import時固定)・`person_generalization_pairs`・`_is_valid_person_generalization`への副作用を避けられているか。表を拡張する代替案との比較。
2. **reasonゲートの集合**: `_is_valid_fulltext_normalization`(kc:502)が3 reason(lemma/generalize_person/generalize_reference_word)のどれでも同一validatorを通す設計(Trial DEV_ALLOWED_REASONSと同一)で、reasonの取り違え(this→aにlemma reasonを使う等)を許してよいか(QA自己申告値への影響: kc:512 `_qa_field_effective_verdict`、:571)。
3. **retry/INVALID増加リスク**: 規則5がLLMに新しい置換を促し、置換条件外の誤置換がvalidator却下→外側retry消費(OUTER_RETRY_EXHAUSTED=fail-closed)になる確率。Trialはreplay(選定・外側retry・音声側を通していない)であり、正式経路でのretry増加は未実測。runtime evidenceで十分か、事前に追加の合成否定が必要か。
4. **a/anのCMU判定資産の共用**: Trial独自`_cmu_dict`ではなくProductionのer108 CMU資産(cmudict 1.1.3)を使う案の妥当性、辞書外語の簡易規則のfail-closed性。
5. **旧test反転**: `er003_test_kp_fulltext_wiring_01.py:261`(`sentence someone to death`をINVALID期待)を受理期待へ反転する根拠(JRE 委任_02のZ melos事象=LLM過剰一般化→外側retry枯渇、の是正方向がA-1と矛盾しないか)。旧事象の再発防止条件(`her`所有格、`it/them`は残す)がA-1で保たれているか。
6. **音声・説明への波及**: used_form変更によるKP3V/CMU gate/Store reuse_key/説明signature再生成(WIRING §4)、`a`の弱形化によるKP英語TTSの照合安定性は無視できるか。
7. **A-3との同時配線**: A-3採用時のPROMPT_SHA256更新(B仕様変更)とA-1を同一commit/別commitのどちらで配線するのが回帰切り分けに有利か。
8. **runtime evidence十分性**: X1本(記事B KP段)+Z1本(メロス/開いた窓KP段)で「両Family発火証拠」として足りるか。自然発火しない場合の扱い。

## 参照
WIRING_DESIGN_01.md / DESIGN_02.md / OPUS_REVIEW_01.md(OF-01〜13) / TRIAL_RESULT_01.md / ITERATION_LOG_01.md / er112_kp_gm_trial_01.py(`A1_RULE5`・`_ref_pair_ok`) / OPEN-474・OPEN-476。
