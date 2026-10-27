# TEST_05(委任_05、2026-10-27、API 0)

- node `selection_form_logic_test_01.js`: ALL PASS 41(PASS行47。前回45→+2)。追加: 理由なし候補はai_reference/candidates_allの理由項目に含まれず「AI理由なし」文言なし / index.htmlは`ro.has`条件でdetails描画・`ro.note`/「（なし）」なし。旧「call1理由なし」検査は「理由欄非表示(行ごと出さない)」検査へ置換。ダミー(理由なし)のai_reference件数は0、7+5/旧docの件数は理由あり選択数と一致。
- py `form1_selection_form_v3_test_01.py`: 17/17 PASS(前回15→+2: `test_reason_missing_warning_only_for_p7w5_docs`、`test_form_html_hides_reason_pane_without_reason`)。
- py `er119_kp_backfill_test_01.py`: 65/65 PASS(エクスポータ変更の回帰)。
