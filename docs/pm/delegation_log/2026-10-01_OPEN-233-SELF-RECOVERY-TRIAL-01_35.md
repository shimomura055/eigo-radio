# 委任ログ: OPEN-233-SELF-RECOVERY-TRIAL-01 委任_35(2026-10-01)

## 1. 委任内容(要旨)

委任_34で特定した追加原因(d)(deterministic floorのfact_id単位
broadcast+same_fact_id_locations enumeration複合によるcycle内非収束)
の小修正を実装し、frozen fixture(rep19と同一)で再検証する。広い
Trialは含めない。Guardrail¥10。

## 2. 実施内容

### A. 実装(¥0)

4点の小修正を実装した(design書§6-16参照)。

1. `apply_floor`/`apply_floor_cited`
   (`er052_open233_self_recovery_flow_runner_01.py`): 複製claim
   (`dev.detected_by_enumeration=True`)に対してはdeterministic floor
   を適用しない。違反を体現する当該claim文自体(`detected_by_
   enumeration`が立っていない)は従来どおりfloorでBLOCKING維持。
2. `run_recheck`: 新規引数`enable_fact_id_enumeration`(既定`False`)。
   `False`時は`SAME_FACT_ID_ENUMERATION_INSTRUCTION`をpromptへ追加
   せず、`expand_same_fact_id_locations`も呼ばない。既存呼び出し側
   (`run_instance`内のEN/JA recheck計2箇所)は既定値をそのまま使う。
3. `measure_section_role_violation`: `iol_degenerate`(「## In one
   line」見出し自体の削除・消失)を追加し、既存の`title_degenerate`/
   `hook_degenerate`と同じhard block条件(`run_instance`、
   `degenerate_rewrite_output`)へ合流。
4. `classify_problem_kind`自体への追加修正は、rep20実測(下記B)で
   該当claimがそもそもBLOCKINGへ至らなくなったことを確認した上で、
   不要と判断し実装しなかった(経過観察)。

unittest: 開始前チェック(既存292件、API呼び出し前に再確認、全PASS)
→新規12件追加(`TestFloorFactIdBroadcastFix35`5件・`TestRecheckFactIdEnumerationOnceOnly35`
3件・`TestInOneLineHeadingDegenerateGuard35`4件、rep19実データ[dev
dict・claim文]を使用)→計304件、全PASS(¥0、API呼び出し前)。

### B. rep20(¥6.0782、Guardrail¥9のうちのsub-budget)

rep19と同一のfrozen fixture(`er052_output/open233_self_recovery_
flow_runner_01_rep19/stage1_fixtures/meta_run03_standard_iter8_
cycle1_frozen.json`、再freezeせず読み込むのみ)を、(d)是正後のコードで
2 run実行した(`er052_open233_self_recovery_flow_runner_01_rep20_
representative_01.py`新規、`OUT_DIR_REP20`新設)。

結果:
1. sample1: 3cycleで`RESOLVED_REWRITE_THEN_DOWNGRADE`(¥2.0186)。
   cycle1のblocking_claimsが2(rep19)→1件に減少(複製4件が強制
   BLOCKINGから解放)。Rewriteは単語置換("calls"→"one call"等)のみ。
   cycle2で新規claim("Some calls needed user information to
   continue.")がLLM独立判定でBLOCKING、cycle3で解消。
2. sample2: 2cycleで`STAGE4_ESCALATION`
   (`stage4_reason=ladder_exhausted_without_full_rewrite`、
   ¥1.8301)。cycle1は同様に1件のみBLOCKING、単語置換で解消。cycle2の
   新規claim("They could not tell if it was AI or a person"等)が
   ladder上限(⑥全文Rewrite不使用)に達しfail-closedでSTAGE4(安全側、
   false PASSではない)。

rep19で観測された検出対象増加連鎖(cycle1:2件→cycle2:12件→cycle3:
5件)、「別文へ丸ごと置換」、「## In one line」見出し削除は、いずれも
再発しなかった(見出しは全cycle・両runで保持を確認)。

false PASS: 0件。`detect_safety_critical_misdowngrades`(meta群は対象外)
: 該当行なし。

### C. Safety対照(regression確認)

対照A(Safety12のうち`safety_er009_changed_number`/`safety_er009_
changed_actor`、full flow n=1×2、¥0.8986): いずれも違反文自体が
`deterministic_floor:changed_number`/`changed_actor`でBLOCKING→
Rewrite→`RESOLVED_REWRITE`(floorが引き続き正しく発火、誤って
弱まっていない)。

対照B(`SAFETY_CRITICAL_CLAIM_DEFS`登録6 instance・8claim、Stage1
[reuse]+Stage2のみ[cycle=1相当、Rewrite/Recheckは回さない]、
¥1.3309): この簡易harnessで検出できた6claim(A2A3-0/A4-0/A4-1/
A5-0/Meta-1/B4-a)は全てBLOCKING維持(0件downgrade)。残り2claim
(B3/Meta-2)は「検出できなかった」(downgradeされたのではない):
B3は既知のStage1 recall miss(`KNOWN_RECALL_MISS_INSTANCE_IDS`、
§10/§14既知の限界、本委任のfloor修正とは無関係)。Meta-2は、この
instance用stage1_sourceの実データ(2 deviationのfact_id/文字列)が
`SAFETY_CRITICAL_CLAIM_DEFS`のMeta-2定義と一致しない既存データ特性
(個別に照合確認済み、本委任のfloor修正の影響ではない)。8claimの
うち、検出された上でBLOCKINGから他状態へdowngradeした事例は0件。

## 3. 結果・Status

`D_FIX_IMPLEMENTED_REP20_VALIDATED_CYCLE1_BLOCKING_2_TO_1_NO_
SAFETY_DOWNGRADE`。

design書§6-16(修正内容・rep20実測・Safety対照)を新設。(d)の小修正は
実装・検証とも完了し、rep19で観測された非収束連鎖は再現せず、Safety
側の誤降格も0件。

## 4. 費用

分析・実装(Part A)¥0+rep20(Part B本体¥3.8487+Safety対照A¥0.8986+
Safety対照B¥1.3309)=**¥6.0782**(Guardrail¥10のうち約61%)。Phase
累計¥476.2883+¥6.0782=**¥482.3665**/総枠¥600、残**¥117.6335**。

## 5. unittest・Git

unittest304件(既存292+新規12)を実行前に再確認し全PASS
(`.venv/Scripts/python.exe -m unittest er052_open233_self_recovery_
flow_runner_01_test_01`、¥0)。project-wide regression
(`run_project_regression.py`)も実行し、collected=4271(既存4259+新規
12)・本委任由来の新規failureなし(既存20件前後の無関係failure[er003_
test_bad/er003_test_p2j_investigate/er011_open112/er015/er025/
er040/er043等、いずれもer052_open233対象外の既存issue]のみ、詳細は
`docs/pm/ACTIVE_TASK.md`一時ファイル参照)を確認した。

**変更ファイル**: `er052_open233_self_recovery_flow_runner_01.py`
(`apply_floor`/`apply_floor_cited`/`run_recheck`/`measure_section_
role_violation`/`run_instance`のhard block条件、`OUT_DIR_REP20`/
`BUDGET_STATE_PATH`/`TOTAL_BUDGET_JPY`新設、既存`OUT_DIR_REP19`等は
無変更)。`er052_open233_self_recovery_flow_runner_01_test_01.py`
(新規unittest12件)。新規`er052_open233_self_recovery_flow_runner_01_
rep20_representative_01.py`、`er052_output/open233_self_recovery_
flow_runner_01_rep20/`(新規)、`docs/pm/design_open233_self_recovery_
flow_01.md`(§6-16/§9-1㉕追記)、`OPEN-233-SELF-RECOVERY-TRIAL-01_
REPORT.md`(§33追記)、`DECISION_LOG.md`(新規エントリ)、
`OPEN_ITEMS.md`(OPEN-233行追記)、`docs/pm/delegation_log/2026-10-01_
OPEN-233-SELF-RECOVERY-TRIAL-01_35.md`(本ファイル)。**Production
code(er003/er006/er009/er010/er012/er019)・既存iteration1〜8・
rep7〜19・rep19 frozen fixtureは無変更。**

## 6. STOP条件該当確認

¥10超え見込み(該当せず、累計¥6.0782/¥10)/API error 3連続(該当せず、
0 error)/Production・既存証跡変更(該当せず)/USER_DECISION_REQUIRED
5条件(該当せず)/開始前チェック未反映(0件)/Safety12の違反文または
Safety-critical 8がBLOCKINGでなくなる(該当せず、2-C参照、downgrade
0件)/false PASS 1件以上(該当せず、0件)/小修正1回後もFAIL(該当せず、
1回の小修正でrep20が成功)。STOP条件はいずれも非該当。

次アクション: meta_run03_standardの(b)Stage1 fresh enumeration非
決定性そのものの改善要否(委任_33から継続する未決事項)、Phase 2新規
テーマ選定(PM_GOVERNANCE§13、ユーザー判断)はFable/ユーザー判断事項
として継続。
