# FAMILY-X-COFFEE-NEW-TONE-PRODUCTION-E2E-01 委任_05(案b: 承認済み品質マスター受入の実装・test・乾式検証)
- 範囲: ユーザー正式決定①(案b APPROVED_FOR_PRODUCTION)+Opus条件Aレビュー(GO with required fixes)の実装。API課金0。
- 変更: er019_family_x_entertainment_production_runner_01.py(opt-in `--approved-quality-master`、事前検証、pinned registry、acceptance.jsonl追記、ja_source可視化)、新test er053_u1_approved_master_acceptance_test_01.py(46件)、新helper er053_approved_master_rundir_builder_01.py、設計書8節追記、er053_c4_wiring_test_01.py(CLI許可リストに新オプション1要素追加のみ)。
- 乾式検証: er053_output/coffee_new_tone_e2e_01/U1_DRY_RUN_VERIFICATION_01.md(受理PASS916文字、evidence不変、acceptance 1行、opt-in無しSTOP)。
- 回帰: 5446/5308/17/75/38、FAIL/ERROR集合はbaseline 02と完全一致(新規fail 0)。
- run dir er019_output/coffee_prices/run_e_tone_01/ は非commit(autocrlf対策、builderで再構成)。
- SSOT・er003_v1_*・er019 audio runner・er033_*は不変。Production実run(API課金)は未実施。
