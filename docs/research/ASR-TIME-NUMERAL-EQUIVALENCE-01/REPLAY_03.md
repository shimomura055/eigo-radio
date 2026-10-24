# REPLAY_03(ASR-TIME-NUMERAL-EQUIVALENCE-01 委任_04、API 0・読み取り専用)

基盤 `replay_extract_pairs_01.py`/`replay_judge_01.py`/`replay_compare_01.py`/`replay_family_02.py`(README_REPLAY_01.md)。対象=`pairs_01.jsonl`(全リポジトリ47,132 json/jsonlから抽出した(canonical, asr)対 **5,330対**、A/B/C Legacy・X・Z・Y・共通fixtureを含む)。

## OPEN-489修正(er021+er006の2ブロック)
修正前=`base_HEAD03`(着手時HEADの複製、`replay03_base.json`)、修正後=working tree(`replay03_after.json`)。比較=`replay03_compare.txt`、Family別=`replay03_family.txt`。

| 指標 | 件数 |
|---|---|
| judge(統一Judge Primary 1本) PASS→NG | **0** |
| judge NG→PASS / その他state変化 | 0 / 0 |
| value_guard PASS→NG / NG→PASS | 0 / 0 |
| 分類層 PASS→NG / NG→PASS | 0 / 0 |
| Tier1 変化 | 0 |

Family別(A/B Legacy 407 / C 28 / X 203 / Y 18 / Z 35 / 共通・fixture 4,639): 全て変化0。**保存corpusに『scale語を伴わない `数詞語 and 数詞語`』が存在せず、修正が効く対がそもそも0件**(実害未観測と整合。効果はTEST_MATRIX_03の合成case 28件とruntime evidence variantで確認)。ベースラインstate内訳(Primary 1本・Secondary不可): NG_SECONDARY_UNAVAILABLE 3,076 / PASS 1,235 / NG_PROTECTED 1,019。

## OPEN-487候補(参考、Production未反映)
- 案A(`despaced()`の数字境界保持、`proto_487A/`): vs 修正後 judge PASS→NG **0**、分類層 PASS→NG 21(うち20=共通・fixture、1=A/B Legacy。全て最終judgeではTier1経路でPASS維持、または元から最終Gate NGの対)。`replay03_487A.json`/`replay03_487A_compare.txt`/`replay03_487A_family.txt`。
- 案B(value_guardのnum↔time kind_mismatchをDIFF化、`proto_487B/`): judge PASS→NG 0、状態変化33(全て元からNG)だが、TEST_MATRIX_487で24時間表記`nineteen thirty`↔`19:30`等の現行PASSを3件NG化する退行(案Bは不採用候補)。`replay03_487B.json`/`replay03_487B_compare.txt`。
