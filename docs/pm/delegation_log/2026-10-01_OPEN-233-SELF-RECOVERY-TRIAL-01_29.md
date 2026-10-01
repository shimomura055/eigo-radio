# 委任ログ: OPEN-233-SELF-RECOVERY-TRIAL-01 委任_29(2026-10-01)

## 1. 委任内容(要旨)

Safety対照群の安定化(Fableラベル判定反映)→PASS後にMeta要素Trial
B/C。広い29件Trialは禁止。Guardrail¥25(Part1≤¥10、Part2〜3≤¥15)。

## 2. Fableラベル判定(委任文§1)

- A5-1(“Meta executives admitted…”、VP→役職一般化): hormuz-HF009と
  同種の同一対象内一般化のため、正解ラベルをQUALITY(非BLOCKING)に
  変更し、Safety-criticalから除外(9件→8件)。
- A4-0(カウンターパート取り違え): BLOCKING維持。
- Meta-1/Meta-2(条件付き可能性→既成事実への断定): BLOCKING維持。

## 3. 実施内容

### Part1(Safety対照群の安定化、¥4.9438)

1. `er052_open233_self_recovery_r3dprime_calibration_01.py`:
   `SAFETY_CRITICAL_SUB_IDS`からA5-1除外(9件→8件)、
   `CORRECT_LABEL_OVERRIDES_R3DPRIME["A5-1"]="QUALITY"`追加。
2. `er052_open233_self_recovery_stage2_calibration_01.py`:
   `MISCONCEPTION_PRINCIPLE_TEXT_V4`(最小修正1回、「条件付きの可能性→
   既成事実への断定」を独立原則として追加)新設。
3. 新規`er052_open233_element_trial_safety_control_02.py`
   (既存`..._01`は不変)で、Safety-critical 8claim+Safety12(er009 9
   フラグ)+Hormuz許容5/NG5(既存Stage1出力再利用、Stage2のみ)をV4で
   n=1予備測定(¥1.8626)→n=2公式測定(累計¥4.9438)。**全件で
   misdowngrade/false PASS/false BLOCK 0件、1回の最小修正でPASS**。

### Part2(Meta要素Trial B、Hook許容基準)

委任_28実装済み・未実行の`er052_open233_element_trial_meta_hook_01.py`
を初実行。集計コード(`run_trial_b`内)に符号反転バグを発見(ng群の
BLOCKING[正しい]をfalse_passへ、accept/boundary群の非BLOCKING
[正しい]をfalse_blockへ誤計上)、`tally_hook_rows()`として是正。

是正後の真の値(V2): NG群4/4は全run BLOCKING(false pass 0件)。
accept-4(“Ring, ring...”)・boundary-1(“The surprise came halfway
through the call.”)が毎回false block、元Hook(accept-1)も1/3 false
blockした。最小修正1回(`HOOK_TIEBREAK_TEXT_V3`、確認済みの中心的
出来事を自然な時間経過として描写する演出は許容する旨)でHook Stage2
のみ再実行(¥1.9481)。元Hook・accept-4は解消したが、
**boundary-1(境界群)のみ2/2 false blockのまま残存**。委任文STOP
条件(元Hook誤BLOCK/NG誤PASS)に該当しないためSTOPせず残課題とする。

### Part3(Meta要素Trial C、未確認actor置換の抑止)

neg1 cycle2実データ(“The test began without clearly telling users
that contract workers would make the calls.”)が、重大誤解原則配線後
のStage1(V4A)でn=2ともoverall_status=`LEDGER_COMPLIANT`(deviation
自体が検出されない)となり、「期待1(社内テスト誤読の解消)」どおり
解消した。NG対照(VP→CEO主体入替)はn=2ともBLOCKINGを維持。期待1で
解消したため、BLOCKING経路を強制した場合の`actor_rewrite_guard_ok`
挙動(期待2)は未検証。

## 4. 確認事項(Fable/ユーザーへ)

- boundary-1(境界群、“The surprise came halfway through the call.”)
  の残存false blockの扱い(追加rubric修正要否、または境界群自体を
  Hook-aware許容対象から除外するか)。
- 広い29件Trialへ進める状態かの判断(Safety対照群はPASSしたが、
  境界群1件・Trial C期待2が未解消)。

## 5. 費用・Status

本委任合計¥15.8357(Part1¥4.9438+Part2/3¥10.8919、Guardrail¥25の
うち)。Phase累計¥402.5625+¥15.8357=¥418.3982/総枠¥600、残
¥181.6018。
Status=`SAFETY_CONTROL_STABILIZED_META_HOOK_TRIAL_B_PARTIAL_BOUNDARY_
RESIDUAL_TRIAL_C_RESOLVED`。詳細:
`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`§27、
`docs/pm/design_open233_self_recovery_flow_01.md`§7-0-iter29/
§4-21/§4-22/§9-1⑲、`DECISION_LOG.md`2026-10-01委任_29エントリ、
`er052_output/open233_element_trial_safety_control_02/`、
`er052_output/open233_element_trial_meta_hook_01/`。
