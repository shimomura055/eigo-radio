# OPEN-233 CHECKER-SELECTIVITY-RECLASSIFY-02 Trial記録(委任_01、2026-10-06)

性質: Trial(Production採用ではない)。**結果: 有料run未実行(較正済み見積mid¥13.8 > 上限¥12のSTOP条件)、実費¥0**。gold/A4-0/候補数/hold-outは未測定。
provenance: Before=reuse(01 frozen)。After=未実行。

## 実装(【確認】)
`er052_output/open233_reclassify_02/reclassify_candidates_02.py`(01のコピー)。変更は(a)PROMPT_TEMPLATE: 規則4(SUPPORTED前に主体/相手先・対象/範囲/限定条件の4点照合、1つでもmismatchならCANDIDATE、Ledger未記載だけではmismatchにしない、NO_FACT_CLAIMは4点n_a)を追加し旧4,5を5,6へ繰下げ、(b)SCHEMA: `actor_match/counterpart_match/scope_match/qualifier_match`(match/mismatch/n_a)追加・name v2、(c)見積器較正のみ。モデルgpt-6-luna/effort=medium/入力構成は01と同一。instance固有語(Muse/users等)・A4-0名指しはpromptに無し(抽象例「AがBに対して→AがCに対して」1つ)。

## 見積較正(【確認】01実測、増分は【推測】)
01: 42 call、入力206,966tok(0.417tok/字、01見積器は0.66で過大)、出力91,916tok=reasoning 61,961(1,475/call)+可視29,955(57/claim)、¥10.46(01見積mid¥13.7の過大要因は入力過大+reasoning仮定)。
02: 入力0.42tok/字、reasoning=1,475x(1.0/1.2/1.5)、可視=(85/105/125)/claim+30 → **low¥12.00/mid¥13.80/high¥16.08**(入力約9%増を含む)。01条件のまま(増分なし)でもmatch項目分で約¥12.3。→ mid>¥12につきSTOP。
出力: `er052_output/open233_reclassify_02/cost_estimate.json`。

## 回帰(¥0)
runner不変。`run_project_regression.py --pattern "er052*_test_*.py"`: 863件PASS(基準一致)。flow_runner testの`LastResort`系ok行は15行(委任文の「19件」とは数え方が異なる可能性、全件PASS)。

## 判断事項
予算枠拡大(例¥14〜16)の承認、または出力簡素化(match項目の削減・短縮)は仕様/予算判断のためSonnetは実施せず、Fable/ユーザー判断。
