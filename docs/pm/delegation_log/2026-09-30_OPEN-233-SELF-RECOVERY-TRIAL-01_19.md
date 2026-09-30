# 委任ログ: OPEN-233-SELF-RECOVERY-TRIAL-01 委任_19(2026-09-30)

## 1. 委任内容(要旨)

委任_18の残課題4点(局所QA基本形が未達/`hormuz_run03_standard`新規
STAGE4/`neg3`両論併記が必要/`safety_A2A3`・`safety_A5`のsample2未実行)
の是正+限定再試行rep10。広いTrialは含めない。Guardrail¥16(A≤¥0.5/
B≤¥13)。

## 2. 実施内容

### A(¥0.3096)

- **A-1(全文Recheck条件narrowingの検討→実施しない決定)**: 委任文の
  「paired J-1は①〜③なら`full_recheck_required`条件(c)から外す」を
  検討した結果、rep9新規観測(`hormuz_run03_standard`sample1、
  `cycle_limit_exhausted_after_recheck`)を根拠に**実施しない**と決定。
  条件(c)を維持しつつ、新設条件(f)(`same_fact_id_reappeared_across_
  cycles`)+`find_sentence_context`のlocateバグ是正
  (SequenceMatcher近似fallback、閾値0.85)を実装。
- **A-2(escalate_to_paragraph)**: 同一fact_idが過去cycleで既に
  BLOCKINGだった場合、①③を飛ばし④段落水準から試す機構を実装
  (`single_text_rewrite`/`paired_rewrite`両方に追加、cycle数上限自体は
  無変更)。
- **A-3(neg3両論併記+sample2原因特定)**: `er052_open233_self_
  recovery_neg3_stage2_n3_01.py`(新規)で既存Stage1出力を再利用し
  Stage2のみn=3測定(¥0.3096)。sample2の`unconfirmed_after_reverify`の
  confirm call出力を分析。
- unittest新規14件(`TestFullRecheckRequiredRepeatFactId`/
  `TestFindSentenceContextFuzzyFallback`/`TestEscalateToParagraph
  LadderSkip`/`TestRepeatFactIdWiring`)+既存214件=計224件全PASS。
  design書§6-6新設。`docs/pm/ACTIVE_TASK_C233W.md`で開始前チェック表
  (指示1・6・7・8・9・10、未反映0件)を作成。

### B(¥12.3479、Guardrail¥13)

`er052_open233_self_recovery_flow_runner_01_rep10_representative_01.py`
(新規、OUT_DIR=`er052_output/open233_self_recovery_flow_runner_01_
rep10`、TOTAL_BUDGET_JPY=13.0)で限定7 instance
(`hormuz_run03_standard`/`neg3_hormuz_prodrunner_b1b`/`bgroup_B3`/
`hormuz_run02_advanced`/`safety_er009_changed_number`/`safety_A2A3`/
`safety_A5`)をn=2実行。**14/14 instance-run完走、STAGE4_ESCALATION
0件**(Guardrail到達なし)。

### C(報告)

REPORT§19、DECISION_LOG新規エントリ、OPEN_ITEMS.md OPEN-233行更新、
本ファイル。

## 3. 得られた結論(要約)

- A-1: 委任文どおりのnarrowingは**実施しなかった**(新規反証により
  安全側判断)。理由・捕捉表はdesign書§6-6/REPORT§19-1に記録。
- A-2: `hormuz_run03_standard`が2/2 sample(rep9はsample1がSTAGE4)とも
  RESOLVEDへ改善。ただし別セクション分散[見出し/one-line]への根本対応
  ではない既知の限界は残存(正直に記録)。
- A-3: n=3測定で3/3 BLOCKING(非flaky)。claim解釈の両論を提示し決定は
  しない。sample2原因はconfirm callのfail-closed正常動作と判明、rep10
  実測で同一claimのconfirm callに非決定性があることも確認。
- rep10: 14/14完走・STAGE4 0件(rep9の2件から改善)、Safety側の全文
  Recheck維持能力(`safety_fixture`条件)を保持。局所QA fastpath発火は
  0/14(選定7 instanceが全て複雑ケースだったため、locateバグ是正の実run
  効果測定機会は今回も得られなかった)。
- **事故と復旧**: A-3測定スクリプトが既存rep9の`budget_state_c233v_18.
  json`を一時的に上書きしたが`git checkout --`で即座に復旧、`git
  status`で他の意図しない変更がないことも確認済み(正直に報告)。

29 instance全量ではないため広いTrialのGateは判定保留。Status=
`REP10_ALL_7_INSTANCES_COMPLETE_STAGE4_ZERO`。

## 4. USER_DECISION_REQUIRED該当有無

該当なし(6条件いずれも非該当)。既存の安全装置(deterministic floor・
safety_fixture条件・cycle上限3・cite-or-release)はいずれも変更・回避
していない。A-1のnarrowing非実施判断・A-3の両論併記はFable/ユーザーへの
判断材料として提示する。予算は¥12.6575/Guardrail¥16内(A=¥0.3096/
B=¥12.3479)、Phase累計¥330.499/総枠¥500内。

## 5. Git

commit予定(本ファイル含む、対象: `docs/pm/design_open233_self_
recovery_flow_01.md`/`er052_open233_self_recovery_flow_runner_01.py`
[+test]/`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`/`DECISION_LOG.md`/
`OPEN_ITEMS.md`/新規`er052_open233_self_recovery_neg3_stage2_n3_01.py`/
新規`er052_open233_self_recovery_flow_runner_01_rep10_representative_
01.py`/`er052_output/open233_self_recovery_flow_runner_01_rep10/`/
`er052_output/open233_self_recovery_neg3_stage2_n3_01/`/本ファイル)。
パス指定`git add`(`-A`不使用)。`docs/pm/ACTIVE_TASK*`/
`docs/pm/RESULT_PACKET*`は一時ファイルのため対象外。

## 6. 報告(handback)

SubagentHandbackで報告(REPORT§19と同内容の要約)。
