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

## 委任_02 本実行結果(2026-10-06、ユーザー上限¥20承認)

- 【確認】本実行(`--stage run --yes-run-paid --budget-jpy 20`、`--stage agg`)。script/promptは委任_01準備済みのまま無修正。gpt-6-luna/effort=medium/42 call(run単位1 call)、01と同一構成・同一入力。欠損run0、fail-closed0、retry0。実費¥14.3752(入力224,648tok/出力138,334tok)、較正済み見積mid¥13.8比+¥0.58(high¥16.08内、上限¥20内)。
- 【確認】候補数(件/run、和集合all/AI由来llm): 全体 Before15.93/12.52→01 8.12/4.52→02 8.57/5.00。NORMAL 24.17/19.92→9.83/5.33→**10.75/6.25**。SC 18.17/14.28→10.11/5.94→10.56/6.44。B2_hormuz 14.33/7.00→10.67/3.33→10.67/3.33。hold-out 1.0→1.0→1.0。r3(NORMAL)23.5→9.83→10.5、r5 9.0→3.42→4.17(全体 r3 8.43/r5 3.40)。決定論・coverage_gap分は不変。
- 【確認】gold 6件×3 sample: B3 3/3、B4-a 3/3、B3-same@neg5 3/3(r5のみ2/3、Beforeも2)、A2A3-0 3/3、**A4-0 3/3(01は2/3)**、A5-0 3/3。gold_pass=True。A4-0各sample: s1=決定論r3+model_r5、s2=決定論r3+model_r5、s3=model_r3+model_r5。全sampleで対象文"Through Muse, trained human contract workers made some calls and completed the exchanges with users."がCANDIDATE、4観点=actor match/counterpart **mismatch**/scope match/qualifier match、理由は「やり取りの相手を『ユーザー』とするのはLedgerの電話相手先と異なる」。01で消えたsample3もcounterpart mismatchで残存。
- 【確認】監視: hold-out 9/9残存、neg5 B3-same 3/3、K19 3/3、HF-011は候補なし(01と同じ)。いずれも01比で悪化なし。
- 【確認】verdict内訳(526 claim): CANDIDATE 190→210/NO_FACT_CLAIM 177→186/SUPPORTED 159→130。4観点mismatchは全てCANDIDATE内で発生(SUPPORTEDでのmismatchは0): qualifier 115、scope 108、actor 24、counterpart 10。組合せ上位: scope+qualifier 78、mismatchなし(他理由)69、qualifierのみ19、actor+scope+qualifier 12、scopeのみ11、actorのみ8。
- 【確認】01比のverdict変化(同一claim): 01 CANDIDATE→非CANDIDATE 29、非CANDIDATE→CANDIDATE 49(うち元NO_FACT_CLAIM 9=NORMAL 4、元SUPPORTED 40=NORMAL 21)。NORMAL新規CANDIDATE 25件。
- 【確認】NO_FACT_CLAIMからの再候補化9件(NORMAL 4): 将来予測/一般傾向/ユーザー認識の推測文が中心(例 "They will want to know if it is AI or human."、"Normally, that might have brought some relief to crude oil prices."、"People often worry that an AI phone call will produce a strange answer."×3)。純粋な効果音・比喩・つなぎ文の再候補化は9件中に見当たらない【推測】(判断はFable)。
- 【確認】「Ledger未記載のみ」境界例(CANDIDATEかつ4観点mismatchなしかつ理由が「記載/明記されていない」)7件(01は2件)。例: "A person can take over when AI alone has trouble."、"That was what people thought as they spoke."(×2)、"People who asked Muse to make a call might think AI was doing it."、"AI had not learned to speak like a human."、"Up to that point, it is AI."、"The lesson is that changing the words...does not always change the price in the same way."。
- 【確認】NORMAL新規CANDIDATE例(元SUPPORTED/NO_FACT): 見出し"# We Thought It Was AI..."(scope+qualifier、Muse一部テストの限定落ち、妥当【推測】)/"A service let people ask AI to make phone calls."(米国内企業・店舗の範囲落ち、妥当)/"In 2026 fashion, mini bags are having a big moment."(主体・季節限定の落ち、妥当)/"In 2026, the runway proudly shows this split..."(ELLE解釈のランウェイ全般化、妥当)/"Palm-sized clutches... fill runways and fashion reports."(例示の一般化、やや厳格【推測】)/"# The 20 Percent Fee Plan Is Withdrawn—But Oil Prices Quickly Return"(Brent以外へ拡大、妥当)/"A user might think the exchange was with AI..."(元NO_FACT、ユーザー認識推測、境界)/"As AI becomes able to make calls..."(元NO_FACT、将来予測、境界)/"They will want to know if it is AI or human."(同)/"A large number suddenly appeared, making the proposal the story's new lead."(元NO_FACT、数値+編集評価、境界)。
- 【推測】NORMALは01比+0.92件/記事で、Before 24.17の約44%。旧「何でも候補」水準への回帰ではないが、AI由来は+0.92(5.33→6.25)で増加。増加分の約8割は元SUPPORTED(scope/qualifier mismatch)由来。Safety上の過検出か有益な追加かの判定はFable。
- Status: Fable分類待ち(REJECTED/VALIDATED/USER_DECISION_REQUIRED)。VALIDATEDでもProduction採用ではない。詳細: `docs/pm/reclassify_open233_checker_selectivity_02.md`(結果節)、`er052_output/open233_reclassify_02/reclassify_aggregate.json`。
