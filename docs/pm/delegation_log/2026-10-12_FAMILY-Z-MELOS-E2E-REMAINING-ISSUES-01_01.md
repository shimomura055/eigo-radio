# FAMILY-Z-MELOS-E2E-REMAINING-ISSUES-01 委任_01 (2026-10-12)
範囲: 項目2 Comment3仕様検証 / 項目4 STOP機構test不安定性 / 項目5 `He drank`文脈。固有名詞ASR(項目3)は対象外。有料API 0(費用JPY0、Melos累計JPY169.2のまま)。
結果: 
- 項目2: Melos Comment3(Std再生成版/Adv)ネタバレなし。25%規則は汎用性に問題あり(OPEN-323, USER_DECISION_REQUIRED)。Trial(LLM)=NOT_RUN。
- 項目4: 原因=同test複数プロセス同時実行による共有dir/STOP_ALL競合+tool/testのdecode脆弱性。test排他lock+UTF-8固定、tools/stop_all_family_z.py UTF-8明示decode。10連続16/16、同時2本も両方PASS。
- 項目5: 既存Rewrite採用・再生成不要。
証跡: er026_output/family_z_production_e2e_01/melos/remaining_issues_01/{COMMENT3_REVIEW_01.md,STOP_TEST_FLAKE_01.md,HE_DRANK_CONTEXT_01.md}
SSOT: DECISION_LOG.md追記、OPEN_ITEMS.md OPEN-323/324。CURRENT_SPEC.md無変更。
