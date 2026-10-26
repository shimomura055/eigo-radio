# TEST_04 委任_04(2026-10-27、API 0)
- node `selection_form_logic_test_01.js`: ALL PASS(既存41 + 新規4: 8件の7+5データがcap12/cap_by_kind7・5、kind=候補doc逐語、`reason_ja`が候補docと逐語一致(call1含む全候補)、legacy退避と非index、12件満載でも選択上限3/5/12不変)。既存2テストは7+5データに合わせて更新(旧call1理由なし検証は`data/legacy/`へ、送信文のcall1理由は逐語に、data件数10・`candidates_all`件数=データ件数)。
- py `form1_selection_form_v3_test_01.py`(run_project_regression経由): 15/15 PASS(既存12 + 新規3: `cap_info`既定12・旧doc8尊重・`shortfall_note_ja`が上限12、7+5全データのcap12/7/5・kind逐語・reason逐語・official、legacy保持)。8件の逐語照合は`test_form_data_reuses_existing_gloss_and_reason_verbatim`(7+5+legacy旧版+猿の手)で70件超。
- headless(ローカル): `browser_check_04.mjs`(新規) pass=38 fail=0、`browser_check_02.mjs` pass=19、`browser_check_03.mjs` pass=9(02/03のmelos期待値のみ新データ=8行・call1理由ありへ更新。UI不変の回帰)。出力=`browser_check_04_local_output.txt`、`browser_check_0{2,3}_local_rerun_04.txt`。
- 不整合出力を期待値とするtestなし。
