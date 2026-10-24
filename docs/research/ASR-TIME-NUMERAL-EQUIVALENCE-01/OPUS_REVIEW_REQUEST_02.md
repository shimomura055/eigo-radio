# OPUS_REVIEW_REQUEST_02(ASR-TIME-NUMERAL-EQUIVALENCE-01 委任_04、OPEN-487、Fableが起動)

起動条件の根拠: 11-3条件A(判定構造に触れる設計)に準じる確認。**ただし**案Aは新しい処理フロー・受理面の追加ではなく、既存の一次分類規則(despace一致)の『数字-数字境界の過剰受理』を是正する縮小変更(約12行・1モジュール)であり、Fable判断で『11-3不要例(既存規則の不具合是正)』と整理して委任_05へ進むことも可能。判断はFable。

## レビュー依頼内容(観点)
1. 根本原因の妥当性: OPEN-487の誤PASSは `despaced()`一致(er006:1150)が一次要因で、value_guard UNKNOWN(kind_mismatch)は二次要因という整理で良いか(OPEN487_DESIGN_01.md §2、TEST_MATRIX_487_01.md)。
2. 案A(`proto_487A/er006_preprod_hardening_01_validation.py`の `_join_keep_digit_boundary`)の正当性: 数字-数字境界を残す連結が、複合語分かち書き(story making/covid 19/blitz-scaling)・冠詞除外despace(`a wide-scale empirical study`↔`Widescale empirical study`)・年号・桁区切りを壊さないか。見落としている数字-文字境界・全角数字・序数(`3rd`)・小数(`3.5`→`3 5`)・通貨(`$5`)等の経路はないか。
3. 副作用の許容: `At 1030`↔`At 10:30`/`At 130`↔`At 1:30`/`At 345`↔`At 3:45` が Primary分類でPASS→NGになる(X/Zはer109承認済み同音規則が救済、A/B/C Legacyは非救済=Secondary次第)。この非対称を『過剰受理の是正』として許容してよいか、それともA/B/Cにも同等の救済(新規受理面の追加=仕様候補)が必要か。
4. 案B(value_guard UNKNOWN→DIFF)の不採用理由(24時間表記の退行3件、er109承認規則の最終Gate阻止)の妥当性。案C(atom由来)を併用する価値はあるか。
5. 影響分析gateの十分性: replay 5,330対(最終judge PASS→NG 0)、TEST_MATRIX 56+152件、全回帰。追加すべき負例・正例。
6. OPEN-489修正(各層1ブロック、反映済み・commit予定)との干渉: `_consume_number_word_run`のand分割とdespace変更の組合せ(`between nine and eleven`↔`between 9 and 11`等)に問題がないか。

## 添付
OPEN487_DESIGN_01.md / TEST_MATRIX_487_01.md / `test_matrix_487_01.py` / `proto_487A/` / `proto_487B/` / REPLAY_03.md(§OPEN-487候補)/ `replay03_487A_compare.txt` / `replay03_487B_compare.txt` / `matrix03_487A.txt`。
