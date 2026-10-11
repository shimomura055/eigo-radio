# FAMILY-Z-STORY-POOL-SCREENING-TRIAL-01 委任_03(2026-10-11、課金上限JPY30、実測約3.67円)
## 実施
- Step1(無料): 権利screeningを work_rights/edition_rights 分離(rights_screen script、決定論)。L04=ロシア語原作(ru.wikisource Пари、sources/L04_ru/)取得、REVIEW->PASS。L06=NG維持。SCREENING_TABLE_02_original_language.md。commit b3e9c9ee。
- Step2(有料): gpt-6-luna、L01先行(品質0.30+権利0.11円、問題なし)の後、残り権利9+品質8を並列4で実行。全19call、actual model_id=gpt-6-luna、合計3.67円。driver変更: 従来/新基準の両判定、L04ロシア語入力、usage_full/elapsed/user_prompt_full記録、権利Promptをwork/edition分離。commit 4d92619e。
- Step3: Phase D比較(新評価commit後に封印ファイル開封)。PHASE_D_COMPARISON_01.md。
- Step4: Phase E pool/story_pool_01.json + STORY_POOL_01.md(全件未選定)。
- Step5: RESULT_01.md。
## 変更ファイル
er054_*_rights_screen/rights_interpret/quality_eval driver, trial_02_test(L04の据え置き検証を合成screeningへ変更、11 test OK)、er054_output/family_z_story_pool_trial_01/ 配下。Production・CURRENT_SPEC・Routing keyは未変更。
## 注意
- sources/の大きいaux_*.html(約280KB)等は委任_01方針でstageしていない(L04_ruは小ファイルのみstage)。
- Status案: USER_DECISION_REQUIRED(詳細 RESULT_01.md)。
