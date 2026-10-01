# 委任ログ: OPEN-233-SELF-RECOVERY-TRIAL-01 委任_28(2026-10-01)

## 1. 委任内容(要旨)

Meta要素Trial B/C(Hook許容基準・未確認actor置換の抑止)、重大誤解原則の
Stage1・Hook rubric実配線、Safety対照群の全量確認、hormuz HF-009の
ラベル整合。広い29件Trialは禁止。Guardrail¥25。

## 2. 実施内容

### Part0(¥0、配線・ラベル是正)
1. `er052_open233_self_recovery_flow_runner_01.py`へ
   `stage1_fresh_with_misconception_principle()`新設(既存
   `stage1_fresh()`は無変更)。
2. `er052_open233_self_recovery_r3dprime_calibration_01.SAFETY_
   CRITICAL_SUB_IDS`からhormuz-HF009を除外(10件→9件、§7-0-iter27との
   ラベル整合)。
3. `er052_open233_self_recovery_stage2_hook_01.run_stage2_hook_batch`
   へ`hook_rubric_text`引数追加(既定値`HOOK_RUBRIC`で無変更)+
   `HOOK_RUBRIC_WITH_MISCONCEPTION_PRINCIPLE_V2`(tie-break明文化)新設。
4. unittest新規7件、discoverで既存338件+7件=345件全PASS。

### Part1(Safety対照群の全量確認、Stage2 body rubric)
新規`er052_open233_element_trial_safety_control_01.py`で、
Safety-critical 9claim+Safety12(er009 9フラグ)を実測した。

- n=1予備測定(V2、¥2.7022): A4-0(counterparty取り違え)・A5-1
  (VP→役職一般化)の2件がfalse downgrade。
- 最小修正1回(V3、当事者関係取り違えと役職一般化を区別): A4-0は解消
  したが、n=2公式測定(¥4.3851)で**A5-1がACCEPTABLEへさらに悪化、
  新規にMeta-1/Meta-2(certainty強化型)がQUALITYへfalse downgrade**。
- Safety12(er009 9フラグ、Stage2直接判定)は9/9とも2/2 BLOCKING維持。
- Safety12のうち4フラグのStage1(V4A)新配線fresh実行は8 run中7 runで
  完全一致(1 runはflag名のみ別名へ振れたがBLOCKING自体は維持)。

**STOP判定**: 委任文STOP条件「Safety対照群のいずれかが小修正1回後も
BLOCKINGに戻らない」に該当。Stage2 body rubricへの重大誤解原則配線を
ここで停止し、**Part2(Meta Hook Trial B)・Part3(Actor Trial C)は
未実施のまま本委任を終えた**(コードは実装済み、
`er052_open233_element_trial_meta_hook_01.py`、未実行)。

### 事故と復旧(開示)
Part1予備測定の実装中、Stage1 fresh呼び出しを誤って`runner.stage1_
fresh_with_misconception_principle`経由で直接実行し、同関数内部の
`record_call`→`save_budget_state`が呼び出し元のstate dictに関わらず
runner自身の固定`BUDGET_STATE_PATH`(委任_24の既存証跡`.../flow_
runner_01_rep15/budget_state_c233ab_24_rep15.json`)へ書き込む副作用
により、同ファイルを一時的に上書きする事故が発生した。検出直後に
`git checkout`で当該1ファイルのみ即座に復元し(`git diff`で差分なしを
確認)、以後は本委任専用の自己完結ラッパーへ是正した。この復元操作に
より、予備測定のStage1 fresh呼び出し4件分の詳細出力json自体は失われた
(既存証跡への実害はない、既知のsunk cost¥2.7022として計上)。

## 3. 費用・Git・Status

- 本委任費用: ¥7.0873(Part1予備測定¥2.7022+V3公式測定¥4.3851、
  Guardrail¥25のうち、Part2/3は未実施のため¥0)。
- Phase累計: ¥395.4752+¥7.0873=**¥402.5625**/総枠¥600、残**¥197.4375**。
- USER_DECISION_REQUIRED 7条件(design書§12)はいずれも非該当
  (Production非接続・KPI不変・Cap/予算¥600内・新Product原則の設定なし)。
- `git diff --stat`でProduction(er003/er006/er009/er010/er012/er019)・
  既存rep/iteration証跡(rep15の一時汚染は復元済み)への差分なしを確認。
- Status=`SAFETY_CONTROL_AUDIT_STOPPED_AFTER_ONE_MINOR_FIX_STILL_
  FAILING`。

## 4. 次のPMアクション

- A5-1・Meta-1/Meta-2の扱い(Safety-criticalリストからの除外候補[既存
  §7-0-iter5でA2A3-1/A4-2が同様に是正された前例あり]か、rubricの
  さらなる改善が必要かの判断)をFable/ユーザーが判断する。
- 上記判断後、Meta要素Trial B(Hook)・Trial C(Actor)を再開するか、
  Stage2 body rubricへの重大誤解原則配線自体を見直すかを決定する。
- 広い29件Trialは引き続き未着手(禁止どおり)。

## 5. 詳細

`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`§26、
`docs/pm/design_open233_self_recovery_flow_01.md`§7-0-iter27続き/
§9-1⑱、`DECISION_LOG.md`(本委任エントリ)、
`er052_output/open233_element_trial_safety_control_01/`。
