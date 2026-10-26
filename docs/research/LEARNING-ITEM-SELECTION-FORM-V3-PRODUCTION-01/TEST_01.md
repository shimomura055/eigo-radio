# TEST_01 テスト結果(2026-10-26、接続0・API 0)
1. node単体: `node docs/research/LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01/selection_form_logic_test_01.js` → `ALL PASS 25`(上限3/5/12、同一候補1区分、解除常時可、古い選択の非計上、文法独立最大2、9記事状態分離、出力書式、構造化JSON、URL<=6000と長文フォールバック、**参照HTMLの`counts/allowed`との乱数20000件の同値**、猿の手に仮文法なし)。
2. Python回帰: `.venv\Scripts\python.exe run_project_regression.py --pattern "form1_selection_form_v3_test_01.py"` → `collected=6 passed=6 failed=0 errors=0`(参照HTML sha256保全、node suite、猿の手データとRESULT_02の一致、仮文法非流用、Production非接続=er119_/er105_/er003_/er125_/APIキー文字列なし)。
3. 実ブラウザDOM: headless Chrome(CDP)`browser_check_01.mjs` → `pass=32 fail=0`(出力=`browser_check_01_output.txt`)。上限挙動・記事切替・リロード保持・文法2件・送信URL・コピーのフォールバック・Console error 0。
JS関数↔参照の対応: `counts()`→`FormLogic.counts(choices,terms)`、`allowed(term,cat)`→`FormLogic.allowed(choices,terms,term,cat)`、`payload()`→`buildText`。
