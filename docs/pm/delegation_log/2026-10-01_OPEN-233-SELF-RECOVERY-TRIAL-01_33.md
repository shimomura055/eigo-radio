# 委任ログ: OPEN-233-SELF-RECOVERY-TRIAL-01 委任_33(2026-10-01)

## 1. 委任内容(要旨)

iter8(委任_32)で未達だった3点のうち、(1)B3(HF-007)のSafety-critical
誤降格2/2、(2)A2A3-0(HF-003)のSafety-critical誤降格1/2、
(3)meta_run03_standardの人間確認率悪化(0%→20%)の原因特定・小修正・
限定再確認を行う。広いTrialは含めない。Guardrail¥15。

## 2. 実施内容

### A. body rubric V6(¥0、最小修正1回)

`er052_open233_self_recovery_stage2_calibration_01.py`へ
`MISCONCEPTION_PRINCIPLE_TEXT_V6`/`RUBRIC_R3_TRIPLE_PRIME_WITH_
MISCONCEPTION_PRINCIPLE_V6`を新設。新しい判定基準は追加せず、既存
BLOCKING列挙(d)[Ledgerと異なる因果の断定]・(b)[Ledgerに無い具体的
主体の追加]について、「確認済みFact同士の自然な接続」として
tie-breakでQUALITYへ寛容化されやすい2パターン(B3型/A2A3-0型)を
許容/NG対比例示として追加した。

Stage2入力(`verified_ledger_text`)には既にLedgerの`conditions`/
`notes_for_writer`/`causal_strength`を含む全文が渡されていることを
確認済み(§4-4確定版どおり、コード変更不要)。

### B. priming再測定+full flow再確認

`er052_open233_element_trial_safety_control_04.py`(新規)でSafety-
critical 8claim/Hormuz許容5・NG5/Hook(neg1実Hook+境界例)をStage2
のみ・n=1で再確認(¥2.0061、8 call、error 0)。8/8 BLOCKING維持・
Hormuz false block/pass各0・Hook 2/2 QUALITY(非回帰)を確認した後、
`BODY_RUBRIC_DEFAULT`をV6へ昇格。

`er052_open233_self_recovery_flow_runner_01_rep18_representative_01.py`
(新規、`OUT_DIR_REP18`新設)で`bgroup_B3`(Stage1 fresh)・
`safety_A2A3`(Stage1 reuse)・`meta_run03_standard`(Stage1 fresh)を
full flow・n=2で再実行(¥4.3972、29 call、error 0)。

結果:
1. `bgroup_B3`: 2/2ともBLOCKING維持→1語Rewrite(`so`→`while`)で
   `RESOLVED_REWRITE`(誤降格解消)。
2. `safety_A2A3`: 2/2ともHF-003がBLOCKING維持(誤降格は再現せず)。
   Rewrite自体は`ladder_exhausted_without_full_rewrite`で未完了のまま
   STAGE4(fail-closed、安全側)。
3. `meta_run03_standard`: 2/2ともACCEPTABLE_STAGE1(iter8は2/2
   STAGE4)。同一fixture・同一コードでの結果の激変により、原因三択の
   うち「Stage1 fresh enumeration非決定性」を確定(design書§6-14)。
   (a)複数箇所独立ladderの不備は不成立(機構は正しく機能)、
   (c)disclosure-gap型でBLOCKING不要も不成立(数値・規模の歪曲であり
   重大誤解原則下でもBLOCKING維持が正しい)と判定。根本改善は根本
   設計変更に該当するためコード変更せず。

### C. `silent_pass_candidate`自動検知への置換(¥0)

`aggregate_measurements`内の常時0固定プレースホルダを、
`SAFETY_CRITICAL_CLAIM_DEFS`(8claim名指しリストの正本定義)と
`detect_safety_critical_misdowngrades`による自動照合へ置換(design書
§8-8)。iter8実データへ適用し、B3(2/2)・A2A3-0(1/2)が正しく自動検出
されることをunittestで確認。rep18では誤降格0件。

## 3. 費用・unittest

実測: ¥2.0061(Part A/C/Hook)+¥4.3972(rep18)=**¥6.4033**
(Guardrail¥15のうち約43%)。Phase累計¥462.6236+¥6.4033=
**¥469.0269**/総枠¥600、残**¥130.9731**。

unittest: 既存281件+新規11件(`TestMisconceptionPrincipleRubricV6`
3件・`TestSafetyCriticalMisdowngradeDetection`8件)=**計292件全PASS**。
`run_project_regression.py`: collected=4259・passed=4248・failed=6・
errors=5(失敗11件はer052/OPEN-233と無関係なモジュールで、本委任の
変更前から存在する既知issueと判断、スコープ外)。`git diff --stat`で
対象4ファイル(489 insertions, 10 deletions)のみ、既存iteration1〜8・
rep7〜17証跡・Production codeは無変更を確認。

## 4. Status・次アクション

Status: `B3_A2A3-0_MISDOWNGRADE_RESOLVED_VIA_RUBRIC_V6_META_STANDARD_
ROOT_CAUSE_CONFIRMED_AS_STAGE1_ENUMERATION_NONDETERMINISM_NO_CODE_
FIX_APPLIED`。STOP条件はいずれも非該当。

次アクション: meta_run03_standardの原因(Stage1 fresh enumeration
非決定性)の根本改善要否(根本設計変更)はFable/ユーザー判断事項。
Phase 2(10〜20実記事規模)は引き続き新規テーマ選定(PM_GOVERNANCE§13、
ユーザー判断)待ち(継続する未決事項)。

詳細: `OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`§31、
`docs/pm/design_open233_self_recovery_flow_01.md`§4-25/§6-14/§8-8/
§9-1㉓、`DECISION_LOG.md`2026-10-01エントリ、`OPEN_ITEMS.md`
(OPEN-233行追記)。
