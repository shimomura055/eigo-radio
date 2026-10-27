# TEST_06 (委任_02)
- node: `selection_form_logic_test_01.js` ALL PASS(出力`TEST_06_node_output.txt`、PASS行56)。新規9件: Top2提示・rank順・初期未決定/送信ブロック・ラジオ置換と2件拒否・旧状態リセット・payload(selected/none/pending)・確定KP逐語ロック・ユーザー表との完全一致(Std/Adv)・validateArticleのfail-closed(改ざん/3件/presented_ids)・index.html構造。既存testは新仕様に合わせ更新(GRAMMAR_MAX=1、grammarテスト、0/1表示、確定済み記事はv2.1選定testから除外=専用testで検証)。
- py: `run_project_regression.py --pattern form1_selection_form_v3_test_01.py` collected=17 passed=17(`TEST_06_py_output.txt`)。
- 元データ照合: `tools/verify_form_data_aif1.py` SUMMARY bad=0(`VERIFY_DATA_aif2_output.txt`)、`tools/verify_user_confirm_aif2.py` ALL MATCH。
