## 管理ID

OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01(委任_04: 承認済み2点の実装+test+runtime evidence。E2Eは本委任ではしない[委任_05])。並行タスク: 委任_02(集計script、`er052_output/open233_prod_e2e_01/`・`docs/pm/RESULT_PACKET_AGG.md`のみ書込、git操作なし)。**本委任は委任_02のファイルを読まない・addしない。** 本委任がgit・SSOT・`docs/pm/ACTIVE_TASK.md`・`docs/pm/RESULT_PACKET.md`の編集権を持つ。

**作業方式(必須)**: ファイル書き出しは`Write`/`Edit`で小分け(1回40行以内)、Bash heredoc不使用。T-0の委任文保存はWriteを3〜4分割して逐語保存。説明は最小限。コード変更は関数単位の小さなEditを積み上げる。

## 性質/到達上限Status/禁止事項

- 性質: Production候補経路(er052 runner)への配線実装。Status: 本管理ID=APPROVED_FOR_PRODUCTION(ユーザー承認済み2点)、**PRODUCTION_WIRED未**(E2E・runtime evidence・SSOT確認後にFable/ユーザー判定。本委任完了時点でもPRODUCTION_WIRED宣言禁止)。
- 承認済み仕様(ユーザー決定2026-10-06、変更禁止): (1)Checker=「Ledgerに書いていない」だけでは候補にしない/Ledger食い違い・具体的新事実の追加を候補/主体・相手先(対象)・範囲・限定条件も照合(RECLASSIFY-02でVALIDATEDの再分類処理を同一内容で正式化)。(2)後段機械判定=数字のみ残し、主体・否定・比較・時期・因果等の「AI判定を強制的に重大へ上書きする機械判定」は廃止(追加確認トリガーとしても残さない)。
- 禁止: 仕様の独自変更/r3・r5 promptの変更/Stage 2(後段AI)rubric・S1の変更/gold・Safety-critical定義変更/有料API(**本委任は¥0**。テストはmock/fixture)/E2E開始/`git add -A`・`stash`・`amend`/`ACTIVE_TASK.md`・`RESULT_PACKET.md`・`RESULT_PACKET_AGG.md`のadd/`docs/pm/PM_GOVERNANCE.md`編集。
- Opus独立技術レビューGate(PM_GOVERNANCE 11-3)該当判定: 条件A該当・レビュー実施済み(2026-10-06)。本委任はその必須修正M1〜M5を反映した実装。内容が同じ限り再レビュー不要。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要。
T-1: 事前指定Read/Grep一覧に従う。一覧外の追加Readはその理由をRESULT_PACKETに1行記録。
T-0: 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ逐語保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行、結果をRESULT_PACKETへ1行記録(FAILでも継続)。
T-2: TTSなし。T-3: 本委任は¥0のためCap定型文は適用対象外。

## ユーザー指示(原文、要点)

> Production Wiring確認: 今回承認された仕様について、初回Production経路だけでなく、Rewrite後Recheck/retry/fallback/regeneration/最終出口確認でも矛盾がないことを確認する。旧仕様の「数字以外の機械的強制重大化」が後段経路に残っていないことも確認する。必要なRegression / integration testを実施し、runtime evidenceを残す。CURRENT_SPEC / DECISION_LOG / OPEN_ITEMS等は実態に合わせて更新する。ただし、9/20 run時点では全E2E未完了なので、PRODUCTION_WIRED完了扱いにはしない。

(注: 本ファイルは委任文の保存版。付録Opusレビュー要旨は別ファイル docs/pm/opus_l2_review_open233_checker_floor_production_e2e_01.md に転記。)

## Fable判断(Opus条件Aレビューの採否、実装指示)

計画doc `docs/pm/plan_open233_checker_floor_production_e2e_01.md` の方向を維持しつつ、Opus必須修正を以下のとおり反映する:

- **M1(採用)**: 再分類はr3/r5候補を`union_candidates`(coverage_checker L725-747)で合流する**前**に、経路別entryへ1箇所で適用する。coverage module側に任意引数`candidate_filter`(既定None=挙動不変)を追加し、`run_stage1_coverage`/`run_recheck_scope`/`run_exit_full_r3`の3箇所で`union_candidates`直前に適用。runner側の3関数は同じfilterを渡すだけにする。再分類の対象はmodel由来候補のみ、決定論由来・coverage_gapは対象外(Trialと同一)。同文グループ一貫性処理で広がった兄弟候補の扱いはTrialと同じ。
- **M2(採用)**: Recheckの`prior_issues_resolved`は再分類後の候補で計算される位置にする。前回指摘と文面が一致する候補(`prior_issue_resolution`の`same_text`条件)は再分類の対象外(fail-closedで候補に残しStage 2が再判定)。出口チェックにも同じ保護を適用。fact_id単位の未解消規則(`same_fact`)は変更しない(残存リスクとして記録)。
- **M3(採用)**: 再分類call用のcall_fnを新設し、model=gpt-6-luna・effort=medium(Trial02と同一)を明示固定。`DEVELOPER_MESSAGE`・prompt本文・schema(v2、`actor_match`等4項目)を逐語移植し、Trial scriptの該当文字列とsha256一致を検証するテストを追加。
- **M4(採用、必須同時実施)**: `precheck_floor`の数字以外4種(date/actor/negation/comparison marker)を廃止しnumber_mismatchのみ残す。絞り込みは`build_precheck_floor_claims`とF3の記録の両方が使う1つの関数で行う。
- **floor縮小**: `apply_floor`の発火集合を新定数`MECHANICAL_FLOOR_FLAGS=("changed_number",)`に限定(`FLOOR_MODE`スイッチ、既定=旧挙動で既存テスト維持)。`FLOOR_FLAGS`自体は不変。`DISCLOSURE_GAP_DISQUALIFYING_FLAGS`は維持するが`FLOOR_FLAGS`参照ではなく明示リストに切り離す(挙動不変)。`apply_floor_cited`は記録のみなので維持。
- **M5(採用)**: 承認済み構成をrunner側の名前付き定数`OPEN233_APPROVED_FLOW_SWITCHES`+適用関数`apply_open233_approved_flow_switches()`として新設(`FLOOR_MODE=number_only`、`FLOOR_VERIFY_MODE=off`、`CAUSAL_FLOOR=False`、`STAGE2_DOWNGRADE_VERIFY=False`、`TIER0_G_L_ENABLED=False`、`STAGE1_RECLASSIFY=on`、precheck=number_only、S1=旧E2Eと同じ値、その他は旧E2E `KPI_TRIAL_SWITCHES`から引き継ぐ値を明示)。E2E scriptと将来のProduction配線はこれをassertする。`KPI_TRIAL_SWITCHES`は旧仕様として残すがdocstring/コメントで「SUPERSEDED by OPEN233_APPROVED_FLOW_SWITCHES(2026-10-06)」と明記。globalの既定は旧挙動のまま。
- **数字floorの定義(明記)**: 残す機械判定は(a)LLM付与`changed_number`→`apply_floor`、(c)precheck `number_mismatch`→Stage 2スキップBLOCKING。(b)Stage 1決定論`number_not_in_fact`は候補化のみ(現状維持、floor不発火)。run jsonに(a)/(c)を区別できる`floor_reason`を残す。(c)は`llm_materiality=None`なので集計では「AI未判定」枠。
- **再分類失敗時**: fail-closed(未返却・schema不一致・例外は全件CANDIDATEのまま)。run jsonに`reclassify_status`(`ok`/`no_target`/`failed`)と除外数・`changed_number`付きで除外された件数を記録。
- **S1**: 旧E2Eと同じ設定を維持。S1によるBLOCKING化はrun jsonで区別可能にする(既存フィールドで足りるか確認、不足なら追加)。
- **¥0事前replay(採用)**: 保存済みrun(段階A 42 run・旧E2E 9 run)からSC gold全件と旧分析の「正当」floor 6件の`llm_materiality`を集計し、「floorだけで重大にしていたgold」のwatch list(`er052_output/open233_prod_e2e_01/watchlist_floor_only_gold.json`)を作る。

## KPI provenance欄

本委任: テスト・replayのみ(frozen/reuse、¥0)。E2E(fresh)は委任_05。

## Opus台帳更新

`docs/pm/OPUS_FINDINGS_LEDGER.md`へ新規ID(最大番号+1〜+7、1行ずつEdit): M1合流前filter/M2 Recheck同文除外/M3 effort・逐語一致/M4 precheck同時廃止/M5承認構成の定数化/E2E assert追加(STAGE2_DOWNGRADE_VERIFY・TIER0_G_L_ENABLED)/数字floor3系統の定義明記、各=FABLE_DECIDED→IMPLEMENTED(本委任)。Opusレビュー全文は`docs/pm/opus_l2_review_open233_checker_floor_production_e2e_01.md`へ保存。

## 事前指定Read一覧

1. `docs/pm/plan_open233_checker_floor_production_e2e_01.md`: 全文。
2. `er052_output/open233_reclassify_02/reclassify_candidates_02.py`: L22-L78、L101-L129、L178-L205、L262-L279。
3. `er052_open233_stage1_coverage_checker_01.py`: L538-L561、L612-L648、L725-L747、L835-L927、L998-L1057。
4. `er052_open233_self_recovery_flow_runner_01.py`: L403-L483、L1765-L1852、L2432-L2502、L2709-L2717、L3361-L3380、L3790-L3936、L4026-L4088、L8027-L8051、L8597-L8713。Grep `def stage1_coverage_fresh|def run_recheck_coverage|def run_exit_check_coverage` →各±40行。
5. 既存テスト `er052_open233_self_recovery_flow_runner_01_test_01.py`: Grep `apply_floor|precheck|FLOOR_VERIFY|KPI_TRIAL_SWITCHES`。coverage checkerテスト: Grep `union_candidates|run_stage1_coverage|run_recheck_scope`。
6. `docs/pm/ACTIVE_TASK.md`: 全文。

## 事前指定Grep一覧+追記位置・更新位置の手順

- 「数字以外の機械的強制重大化」の残存確認: runner Grep `changed_actor|changed_negation|changed_comparison|changed_time|changed_causality|tier0|precheck_floor|floor_verify|CAUSAL_FLOOR|STAGE2_DOWNGRADE_VERIFY|TIER0_G_L_ENABLED` →全ヒットを「上書き/記録/降格禁止/理由選択/休眠」に分類し、承認構成適用時に上書きが数字以外で起きないことをテストで証明(integration test)。
- 後続経路の整合テスト: Recheck/retry/fallback/regeneration/出口/T・STAGE4理由選択。
- runtime evidence: `er052_output/open233_prod_e2e_01/runtime_evidence_tests_01.txt`、`approved_switches_dump.json`、replay結果。
- SSOT: `OPEN_ITEMS.md` Grep `OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01` →行末尾へ委任_04の進捗追記。`DECISION_LOG.md` 同ID→エントリ末尾へ「Opus条件Aレビュー要旨+Fable判断」追記。`CURRENT_SPEC.md`: 注記(L2372付近)に「実装完了・E2E未(委任_04)」追記のみ。`docs/pm/REPORT_LEDGER.md`末尾1行。REPORT §80を`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`末尾に追加。
- `docs/pm/ACTIVE_TASK.md`: 固定ヘッダで上書き(実装完了→委任_05 E2Eへ)。

## 実行コマンド全文

1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-06_OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01_04.md --json-out docs\pm\delegation_log\2026-10-06_OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01_04.md_check.json`
2. 実装。新規module: `er052_open233_stage1_reclassify_01.py`(prompt/schema/DEVELOPER_MESSAGE逐語+call_fn+filter関数)。
3. テスト追加(新規 `er052_open233_checker_floor_prod_wiring_test_01.py`): (a)sha256逐語一致、(b)filterが合流前に効く、(c)Recheck同文除外、(d)fail-closed、(e)承認構成で数字以外floor不発火・数字floor発火、(f)precheck number_mismatchのみ、(g)retry/fallback/regen/出口の整合、(h)既定で既存テスト不変、(i)`OPEN233_APPROVED_FLOW_SWITCHES`のassert関数。
4. 単体: `.venv\Scripts\python.exe -m unittest er052_open233_checker_floor_prod_wiring_test_01 -v` → `er052_output\open233_prod_e2e_01\runtime_evidence_tests_01.txt`
5. 回帰: `.venv\Scripts\python.exe run_project_regression.py --pattern "er052*_test_*.py"`(基準863件+新規N件)。
6. replay(¥0): `.venv\Scripts\python.exe er052_output\open233_prod_e2e_01\build_watchlist_floor_only_gold_01.py --stagea-dir er052_output\open233_stage1_stageA_01 --e2e-dir er052_output\open233_e2e_acceptance_01\runs --out er052_output\open233_prod_e2e_01\watchlist_floor_only_gold.json`(script新規作成)。
7. SSOT・REPORT・ACTIVE_TASK・RESULT_PACKET更新。
8. `git status --porcelain`→明示add→commit→push(委任_02のファイルはaddしない)。

## Git

明示add対象のみ(runner, coverage checker, reclassify module新規, テスト, build_watchlist script/json, runtime_evidence, approved_switches_dump, opus review md, OPEN_ITEMS, DECISION_LOG, CURRENT_SPEC, REPORT_LEDGER, OPUS_FINDINGS_LEDGER, REPORT, delegation_log _04(+_check.json))。委任_02のファイル・ACTIVE_TASK・RESULT_PACKETはaddしない。
コミットメッセージ: `OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01: Checker再分類(4観点)を合流前filterとして初回/Recheck/出口へ配線、floorをchanged_numberのみに縮小、precheck数字以外廃止、承認構成を名前付き定数化(Opus M1〜M5反映)+test N件・回帰X件PASS・runtime evidence、PRODUCTION_WIRED未(委任_04、¥0)`

## 報告(RESULT_PACKET項目)

1. T-0結果。2. 変更一覧(M1〜M5対応表)。3. 数字以外の機械的強制重大化 残存確認表。4. テスト。5. 後続経路整合確認表。6. 承認構成定数dump。7. replay watch list。8. 残存リスク。9. Status(実装完了・E2E未・PRODUCTION_WIRED未)。10. commit hash・push結果・raw URL。11. 一覧外Read理由。12. 委任_05(E2E)への引継ぎ。

(付録Opusレビュー要旨は docs/pm/opus_l2_review_open233_checker_floor_production_e2e_01.md を参照。)
