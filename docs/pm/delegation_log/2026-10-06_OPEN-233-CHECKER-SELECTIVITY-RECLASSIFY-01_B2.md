## 管理ID

OPEN-233-CHECKER-SELECTIVITY-RECLASSIFY-01(委任_B2: 委任_B[commit `dea81a92`]のT経路修正に対するOpus独立レビュー指摘の反映、Fable修正指示1回目)。並行タスク: 委任_A2(再分類Trial、`er052_output/open233_reclassify_01/`・`docs/pm/RESULT_PACKET_A.md`・`docs/pm/reclassify_open233_checker_selectivity_01.md`、git操作なし)が進行中。**本委任は委任_A2のファイルを読まない・addしない。** 本委任がgit・SSOT・`docs/pm/ACTIVE_TASK.md`・`docs/pm/RESULT_PACKET.md`の編集権を持つ。

## 性質/到達上限Status/禁止事項

- 性質: 実装不具合修正の是正(既存仕様への整合修正)。Trial runnerの修正であり、Production正式pathは不変。`APPROVED_FOR_PRODUCTION`ではない。
- 禁止: Stage 1/Stage 2構成・prompt・gold・Safety-critical定義・floor語彙・STAGE4許可リスト(理由ラベル一覧)の変更禁止(新ラベル・新遷移先・新Statusを作らない)/有料API禁止(¥0)/E2E再開禁止/Human Review基準の緩和禁止(本文に残る未解消BLOCKINGはfail-closed)/`git add -A`・`stash`・`amend`禁止/`ACTIVE_TASK.md`・`RESULT_PACKET.md`のadd禁止。
- 費用: ¥0。
- Opus独立技術レビューGate(PM_GOVERNANCE 11-3)該当判定: 任意レビュー実施済み(本日1回目)。本委任はその指摘反映であり、追加レビュー不要(内容が同じ論点の是正のため)。R2でcarry経路を廃止することで、Human Review遷移の変更(条件A境界)は解消される。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0: 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する)。**本委任では受領文を要約せず逐語で保存すること(委任_BはT-0 FAIL=要約保存だった)。**
T-2: TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。(本委任はTTSなし)
T-3: 本委任は¥0のためCap定型文は適用対象外。

## ユーザー指示(原文)

> 期待動作：同一cycleでRewrite成功済みの対象を、最終削除処理で再対象化しない／Human Reviewへ送る前に、本当に構造上修正不能なのかを確認する／非構造的な位置特定失敗を「構造上修正不能」と誤分類しない／regression testを追加する／retry / fallback / regenerationでも同種不具合が起きないことを確認する。この種の明確な実装バグは、今後もまず修正・testしてから報告すること。Safety基準をTrial都合で緩和しないこと。

## KPI provenance欄

該当なし(コード修正+テストのみ)。

## Opus台帳更新

本レビュー(Opus、2026-10-06、委任_B成果の任意レビュー)の指摘をFableが採用した旨を`docs/pm/OPUS_FINDINGS_LEDGER.md`へ新規ID(既存の最大番号+1〜+3)で登録: (1)R5-(a) classify/selectの判定不一致→FABLE_DECIDED→本委任でIMPLEMENTED、(2)R2 carry経路は費用増のみでHuman Review削減なし→FABLE_DECIDED(即fail-closed停止へ統一)→IMPLEMENTED、(3)R1 covered条件強化→IMPLEMENTED、(4)R5-(b) 構造検証結果の記録→IMPLEMENTED(記録のみ)、(5)R4 regen内の新規枯渇が判定されない(既存挙動、安全側)→RAISED(観察、未対応)。台帳の既存書式に従う(Grep `^\| OF-` で最終行を確認)。

## Fable判断(Opus指摘の採否、実装指示)

Opusレビュー要旨(行番号は`dea81a92`時点):
- **R5-(a)【必須】**: `classify_last_resort_failures`(L6009-6038)が、T内部のcarry-forwardで`method="covered_by_earlier_rewrite_in_cycle"`, `guard_ok=False`, `target_not_locatable=False`となったrecord(L7157-7159)を`located_guard_failed`(L6025, L6034-6035)として`blocking_structural_after_ladder`STAGE4(L9101)へ送る。一方`select_last_resort_targets`(L6003)は同methodを解消済み扱い。→**修正**: classifyでも`method`が`covered_by_earlier_rewrite`で始まるrecordを`covered_by_earlier_rewrite`として扱い、両関数の判定を揃える。統合テスト追加: 「同じ文を指す枯渇claim 2件を同時にT」(1件目のT削除の置換単位で2件目がcarry-forwardになる)→STAGE4へ行かない。
- **R2(採用=Opus代替案)**: `unlocatable_not_covered`→H-1 carry(SPAN_FALLBACK_CHAIN=True時)は、次cycleでStage 2を通さずBLOCKING注入(L8593-8606, L8684)+`t_used=True`→L8739で必ず`post_T_new_blocking`STAGE4に落ちる=1 cycle分の費用増と理由名不一致だけでHuman Reviewを減らさない。→**修正**: carry分岐を廃止し、SPAN_FALLBACK_CHAINの有効/無効にかかわらず、`unlocatable_not_covered`は既存の非構造ラベル(`violation_span_unverified`/`target_not_locatable`、委任_Bで無効時に使ったもの)でその場でfail-closed停止(STAGE4)に統一する。新ラベルは作らない。既存の許可リストに当該ラベルが無い場合は実装せずSTOPして報告(許可リスト変更はFable/ユーザー判断)。
- **R1(採用)**: covered判定(L7007 `r in b`)に「範囲rが現在(置換後)の本文に存在しない」を追加条件とする(同文複数出現で片方だけ書き換えられた場合の抜け道を塞ぐ、安全側)。
- **R5-(b)(採用、記録のみ)**: `blocking_structural_after_ladder`の全発生箇所(L8869, L9065, L9101, L9246)で`structural_verified`(構造検証結果bool+理由)を`cycle_record`へ記録する。挙動・ラベルは変えない。
- **R4(観察のみ、未対応)**: 委任_Bの観察「regenはTを再実行しない」はT対象については不正確(L9083の`last_resort_delete=True`がregen内L6123で再実行される)。正しくは「regen内で新たに起きた枯渇・位置特定不能は判定されずRecheckへ流れる」(安全側)。REPORT §76の該当記述を訂正する。
- **R3**: 問題なし(確認済み)。変更不要。

## 事前指定Read一覧

1. `er052_open233_self_recovery_flow_runner_01.py`: L5980-L6045(新2関数)、L6115-L6135(regen内T再実行)、L7000-L7035(covered判定・部分一致)、L7150-L7162(carry-forward record)、L8585-L8610・L8680-L8690・L8735-L8745(carry注入とpost_T_new_blocking)、L8860-L8876、L9048-L9134(適用箇所・carry分岐)、L9240-L9250。Grep `ALLOWED.*REASON|allowed_reasons|blocking_confirmed_unlocatable_after_cap|violation_span_unverified|target_not_locatable` →許可リスト定義の範囲のみRead。
2. `er052_open233_self_recovery_flow_runner_01_test_01.py`: Grep `class TestLastResortDeleteDoesNotRetargetRewrittenClaims` →クラス全体(L9096-L9246付近)。
3. `OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`: Grep `^## §76|§76` →§76全体(訂正・追記用)。
4. `docs/pm/OPUS_FINDINGS_LEDGER.md`: Grep `^\| OF-` →最終5行(書式・最大ID確認)。
5. `docs/pm/ACTIVE_TASK.md`: 全文(更新用)。

## 事前指定Grep一覧+追記位置・更新位置の手順

- `OPEN_ITEMS.md`: Grep `OPEN-233-CHECKER-SELECTIVITY-RECLASSIFY-01 委任_B` →その直後へ委任_B2の進捗1文を追記。
- `docs/pm/REPORT_LEDGER.md`: Grep `委任_B |` (本管理ID) →その直後へ1行追加。
- REPORT §76: 末尾に「§76-2 Opus任意レビュー指摘の反映(委任_B2)」を追加し、R4の記述を訂正(訂正箇所を明示、旧記述は取り消し線でなく「訂正: 」と併記)。
- `DECISION_LOG.md`: Grep `OPEN-233-CHECKER-SELECTIVITY-RECLASSIFY-01` →既存エントリ末尾へ「Fable判断(Opus任意レビュー後、2026-10-06): R5-(a)必須修正採用/R2 Opus代替案採用(carry廃止・即fail-closed)/R1・R5-(b)採用/R4観察のみ/条件A境界は解消」を追記。
- `docs/pm/ACTIVE_TASK.md`: 固定ヘッダを更新(Status: 委任_B2完了・委任_A2進行中、Opus任意レビュー1回使用)。

## 実行コマンド全文

1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-06_OPEN-233-CHECKER-SELECTIVITY-RECLASSIFY-01_B2.md --json-out docs\pm\delegation_log\2026-10-06_OPEN-233-CHECKER-SELECTIVITY-RECLASSIFY-01_B2.md_check.json`
2. 修正前に、R5-(a)の統合テスト(同一文を指す枯渇claim 2件同時T)を先に書き、**FAIL(再現)を確認**してから修正→PASS。R2の分岐統一テスト(SPAN_FALLBACK_CHAIN=True/Falseの両方で`unlocatable_not_covered`が同じ既存ラベルでSTAGE4、carryされない)、R1のテスト(同文2回出現・片方のみ書き換え→coveredにならない)を追加。
3. 単体: `.venv\Scripts\python.exe -m pytest er052_open233_self_recovery_flow_runner_01_test_01.py -k "LastResort" -q`
4. 回帰: `.venv\Scripts\python.exe run_project_regression.py --pattern "er052*_test_*.py"`(基準: 委任_B時点857件PASS。増分=追加テスト数)。
5. `git status --porcelain`で混入確認→明示add→commit→push。

## SSOT追記文

- OPEN_ITEMS.md(委任_B進捗の直後): 「委任_B2(2026-10-06): Opus任意レビュー指摘を反映: classify/selectの判定不一致(T内carry-forwardの誤STAGE4)修正、unlocatable_not_coveredのcarry経路を廃止し既存非構造ラベルで即fail-closed(Human Review遷移変更を解消)、covered条件に現本文不在を追加、構造検証結果の記録、テスト+N件(再現FAIL→PASS)、回帰X件PASS、¥0。」
- REPORT_LEDGER.md: 「- 2026-10-06 | OPEN-233-CHECKER-SELECTIVITY-RECLASSIFY-01 委任_B2 | Opus任意レビュー(R1/R2/R5-a/R5-b採用、R4観察)反映、テスト+N件、回帰X件PASS、¥0。REPORT §76-2。」
- OPUS_FINDINGS_LEDGER.md: 上記5件。
- DECISION_LOG.md: 上記Fable判断追記。

## Git

明示add対象のみ: `er052_open233_self_recovery_flow_runner_01.py`、`er052_open233_self_recovery_flow_runner_01_test_01.py`、`OPEN_ITEMS.md`、`DECISION_LOG.md`、`docs/pm/REPORT_LEDGER.md`、`docs/pm/OPUS_FINDINGS_LEDGER.md`、`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`、`docs/pm/delegation_log/2026-10-06_OPEN-233-CHECKER-SELECTIVITY-RECLASSIFY-01_B2.md`(+`_check.json`)。`ACTIVE_TASK.md`・`RESULT_PACKET.md`・委任_A/A2のファイルはaddしない。
コミットメッセージ: `OPEN-233-CHECKER-SELECTIVITY-RECLASSIFY-01: T経路修正にOpus任意レビュー指摘を反映(classify/select判定統一・carry経路廃止→既存ラベルで即fail-closed・covered条件強化・構造検証記録)+test N件、回帰X件PASS(委任_B2、¥0)`
SSOT編集権: あり(`OPEN_ITEMS.md`/`DECISION_LOG.md`/`docs/pm/REPORT_LEDGER.md`/`docs/pm/OPUS_FINDINGS_LEDGER.md`/REPORT)。`CURRENT_SPEC.md`・`docs/pm/PM_GOVERNANCE.md`は編集しない。index.lock競合時は数秒待って1回だけ再試行、再発時はcommit保留で報告。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET.md`へ(委任_Bの内容は「委任_B経緯」として要約保持): 1. T-0結果。2. R5-(a)再現FAIL証跡→修正後PASS。3. R2: carry分岐廃止後の遷移(ラベル名・許可リスト内であることの確認、行番号)。4. R1・R5-(b)の変更箇所。5. 追加テスト一覧・回帰件数。6. R4訂正内容。7. Safety・Human Review基準を緩和していないことの説明。8. commit hash・push結果・raw URL。9. 一覧外Read理由。10. 残課題(設計問題②・R4観察)。
