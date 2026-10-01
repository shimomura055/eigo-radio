# 委任ログ: OPEN-233-SELF-RECOVERY-TRIAL-01 委任_34(2026-10-01)

## 1. 委任内容(要旨)

meta_run03_standardの人間確認(STAGE4到達)を「Stage1の揺れ」から
切り離して検証する。iter8(委任_32)でmeta_run03_standardが2/2 STAGE4に
なったStage1出力(fresh、同一事実の多箇所列挙)をそのままreuse入力と
して固定し、現行既定構成(body rubric V6・actorガード常時評価・局所
QA・JA fail-open封鎖・escalate_to_paragraph OFF・⑥OFF)の流路が、この
Stage1検出集合を人間確認なしに解消できるかを確認する。Stage1自体の
揺れは本委任の責任範囲外。広いTrialは含めない。Guardrail¥8。

## 2. 実施内容

### A. 分析(¥0)

iter8のinstances_s1/s2のmeta_run03_standard.jsonを精査。s1/s2の
cycle1 Stage1検出内容(原本2件: MUSE-HC-012/MUSE-HC-011)が完全同一
であることを確認した(`stage1_cache`共有、fresh instanceの既存仕様
どおり)。原本2件は`same_fact_id_locations`フィールドを持ち、既存
`expand_same_fact_id_locations`で各4件・計6件へ展開される。

iter8のcycle別`stage2_results`を精査し、各claimの判定文(materiality/
llm_materiality/floor_reason)を逐語照合した結果、`News reports also
cited one employee's report.`(「one」=単数、正確な記述、llm_
materiality=ACCEPTABLE)が`deterministic_floor:changed_number`で
BLOCKINGへ強制されているなど、文面自体は正確なのに同一`related_
fact_id`を共有する他claimのfloorへ巻き込まれる誤分類を複数件確認した
(詳細はREPORT§32-1)。

### B. rep19(¥7.2614、Guardrail¥8)

iter8のcycle1原本2件(`same_fact_id_locations`付き)のみを抽出し、
frozen fixture(`er052_output/open233_self_recovery_flow_runner_01_
rep19/stage1_fixtures/meta_run03_standard_iter8_cycle1_frozen.json`)
を作成。meta_run03_standard instanceの`stage1_mode`を`reuse`へ上書き
し、現行既定構成で2 run試行した
(`er052_open233_self_recovery_flow_runner_01_rep19_representative_
01.py`新規、`OUT_DIR_REP19`新設)。

結果:
1. sample1: 3cycle・32 call(¥6.2845)を費やしても収束せず
   `STAGE4_ESCALATION`(`stage4_reason=cycle_limit_exhausted_after_
   recheck`)。cycle1の2claim→cycle2の12claim(blocking6+
   non_blocking6)→cycle3の5claim(全てBLOCKING、non_blocking0)と
   検出対象が増加し続けた。
2. sample2: cycle1完了後、累計¥7.2614がGuardrail¥8へ到達し
   `TrialAbort`で自己停止(¥0.9769消費、結果は未保存)。

false PASS: 0件。Safety-critical誤降格: 0件(meta群はSAFETY_
CRITICAL_SUB_IDS対象外)。

### C. 発見(追加原因(d))

cycle1入力を完全固定しても非収束が再現したことは、委任_33(design書
§6-14)が確定した「原因は(b)Stage1 fresh enumeration非決定性のみ」
では説明できない。claim単位の逐語照合により、`deterministic_floor:
changed_number`/`changed_actor`が、違反を体現する当該claim文だけで
なく同一`related_fact_id`を共有する他の全claim(llm_materialityが
独立にACCEPTABLE/QUALITYと判定していても)へBLOCKINGを強制的に波及
させていること、`same_fact_id_locations`enumerationが毎cycle新しい
候補文を再列挙し続けることと複合して、cycle上限に達するまで収束
しなかったことを特定した(追加原因(d)、design書§6-15)。

(d)は委任文の分類では「Stage2許容例示の適用範囲」(floorの対象範囲を
当該claim文のみへ狭める)に近い小修正候補だが、Guardrail¥8を
sample1完走+sample2 cycle1部分実行で使い切ったため、修正の実装・
再検証(見込み≤¥2)およびSafety-critical priming再確認(見込み≤¥1)を
行う予算がなく、**未検証のままコード変更は行っていない**。

## 3. 結果・Status

`META_STANDARD_STAGE1_INPUT_FROZEN_STILL_STAGE4_ADDITIONAL_ROOT_
CAUSE_D_DETERMINISTIC_FLOOR_FACT_ID_BROADCAST_IDENTIFIED_FIX_
UNTESTED_BUDGET_GUARDRAIL_STOP`。

design書§6-14の結論を「(b)は少なくとも部分的要因」へ修正し、(d)
deterministic floorのfact_id単位broadcast+same_fact_id_locations
enumeration複合によるcycle内非収束を、既知の残存原因候補として追加
した(design書§6-15)。

## 4. 費用

分析(Part A)¥0+rep19(Part B)¥7.2614=**¥7.2614**
(Guardrail¥8のうち約91%)。Phase累計¥469.0269+¥7.2614=
**¥476.2883**/総枠¥600、残**¥123.7117**。

## 5. unittest・Git

unittest292件(既存281+委任_33新規11)をAPI呼び出し前に再実行し全
PASS(`.venv/Scripts/python.exe -m unittest er052_open233_self_
recovery_flow_runner_01_test_01`、¥0)。`run_project_regression.py`
実行結果・`git diff --stat`は本commit後に別途記録する。

**変更ファイル**: `er052_open233_self_recovery_flow_runner_01.py`
(`OUT_DIR_REP19`/`BUDGET_STATE_PATH`/`TOTAL_BUDGET_JPY`新設、既存
`OUT_DIR_REP18`等は無変更)。新規`er052_open233_self_recovery_flow_
runner_01_rep19_representative_01.py`、`er052_output/open233_self_
recovery_flow_runner_01_rep19/`(新規)、`docs/pm/design_open233_
self_recovery_flow_01.md`(§6-15/§9-1㉔追記)、
`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`(§32追記)、
`DECISION_LOG.md`(新規エントリ)、`OPEN_ITEMS.md`(OPEN-233行追記)、
`docs/pm/delegation_log/2026-10-01_OPEN-233-SELF-RECOVERY-TRIAL-01_
34.md`(本ファイル)。**Production code(er003/er006/er009/er010/
er012/er019)・既存iteration1〜8・rep7〜18は無変更。**

## 6. STOP条件該当確認

¥8超え見込み(**該当**: 累計¥7.2614/¥8[残¥0.7386]に到達し、計画の
残作業[sample2完走・小修正1回・Safety-critical priming再確認]の
いずれも≤¥2〜¥3の見込み費用を賄えないため、これ以上API呼び出しを
伴う作業を行うとGuardrailを超える見込み)/API error 3連続(該当せず、
0 error)/Production・既存証跡変更(該当せず)/USER_DECISION_REQUIRED
5条件(該当せず)/開始前チェック未反映(0件)/Safety-critical誤降格
(該当せず、meta群は対象外・0件)/false PASS 1件以上(該当せず、0件)/
小修正1回後もFAIL(未実施: 修正を試す前に予算到達)。**STOP(budget
guardrail)**。

次アクション: (d)修正(floorの対象範囲を当該claim文へ限定)の実装・
検証の要否、および追加予算(目安¥3程度)の承認をFable/ユーザーへ
依頼する。
