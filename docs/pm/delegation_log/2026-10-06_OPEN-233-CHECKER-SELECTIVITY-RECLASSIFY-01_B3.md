## 管理ID

OPEN-233-CHECKER-SELECTIVITY-RECLASSIFY-01(委任_B3: 委任_B2[STOP、未実装]の残作業をFable判断で再開+委任_A/A2成果物の統合・SSOT反映・ACTIVE_TASK更新。本管理IDの最終Sonnet委任)。並行タスクなし(委任_A2・Opusレビューは完了済み)。本委任がgit・SSOT・`docs/pm/ACTIVE_TASK.md`・`docs/pm/RESULT_PACKET.md`の編集権を持つ。

## 性質/到達上限Status/禁止事項

- 性質: (B)実装不具合修正の是正(既存仕様内、Trial runner、Production正式path不変)+(A)Trial結果の正式記録・STOP処理。最終Status: 再分類Trial=**VALIDATED未達でSTOP**(gold A4-0 1 sample消失)、管理ID全体=**USER_DECISION_REQUIRED**。`APPROVED_FOR_PRODUCTION`ではない。
- 禁止: Stage 1/2構成・prompt・gold・Safety-critical定義・floor語彙・**STAGE4許可リスト(`STAGE4_ALLOWED_REASONS` L8159-8160の4種)の変更禁止**(新ラベル・新遷移先・新Status不可)/有料API禁止(¥0)/E2E再開禁止/Human Review基準緩和禁止(本文に残る未解消BLOCKINGはfail-closed)/`git add -A`・`stash`・`amend`禁止/`ACTIVE_TASK.md`・`RESULT_PACKET.md`・`RESULT_PACKET_A.md`のadd禁止/Checker本体・再分類scriptの変更禁止。
- 費用: ¥0。
- Opus独立技術レビューGate(PM_GOVERNANCE 11-3)該当判定: 任意レビュー実施済み(本日1回目、委任_B成果)。本委任はその指摘反映で追加レビュー不要。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ逐語で保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。本委任はTTSなし。
T-2追記(2026-09-25、`NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02`、PM_GOVERNANCE.md 7-5): TTSを伴う委任は実行前に(1)差分再生成可否、(2)音声再利用キャッシュ、(3)`--budget`明示、(4)想定外の全再生成判明時はAPI実行前STOP、の4点を必須とする。本委任はTTSなし。
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`): 本委任は¥0のためCap定型文は適用対象外。

## ユーザー指示(原文)

> 期待動作：同一cycleでRewrite成功済みの対象を、最終削除処理で再対象化しない／Human Reviewへ送る前に、本当に構造上修正不能なのかを確認する／非構造的な位置特定失敗を「構造上修正不能」と誤分類しない／regression testを追加する／retry / fallback / regenerationでも同種不具合が起きないことを確認する。
> 見込みが外れた場合は、そのまま実装へ進まずSTOPして報告すること。KPIは変更しない。Safety基準をTrial都合で緩和しないこと。到達してよいStatusは最大で VALIDATED。Production正式Checker仕様の変更は、今回の再分類結果をユーザーが確認するまで行わない。

## KPI provenance欄

(A)再分類Trial: Before=reuse(段階A 42 run保存候補)、After=fresh(分類call 42回、¥10.46)、E2E自己確認=No。詳細は`docs/pm/reclassify_open233_checker_selectivity_01.md`に記載済み(本委任はそれを正式記録へ転記)。(B)該当なし(コード修正+テスト)。

## Opus台帳更新

`docs/pm/OPUS_FINDINGS_LEDGER.md`: (1)OF-027(Opus#17、保存候補の分類proxy)→TRIALED→EVIDENCED(結果: NORMAL候補24.2→9.8件/記事、gold 5/6[A4-0 2/3]、¥10.46、VALIDATED未達)。(2)本日のOpus任意レビュー(委任_B成果)の指摘を新規ID(最大番号+1〜+5)で登録: R5-(a) classify/select判定不一致→FABLE_DECIDED→IMPLEMENTED(本委任)/R2 carry経路は費用増のみ→FABLE_DECIDED(許可リスト内`blocking_confirmed_unlocatable_after_cap`+sub_reason記録で即fail-closed)→IMPLEMENTED/R1 covered条件強化→IMPLEMENTED/R5-(b) 構造検証結果記録→IMPLEMENTED/R4 regen内の新規枯渇未判定(既存挙動・安全側)→RAISED(観察)。既存書式に従う(Grep `^\| OF-` で最終行確認)。

## Fable判断(委任_B2のSTOP事項への回答=本委任の実装指示)

- **R2の行き先(確定)**: 許可リストは変更しない。`unlocatable_not_covered`は、SPAN_FALLBACK_CHAINの有効/無効にかかわらず、H-1 carryせず、その場で`stage4_reason="blocking_confirmed_unlocatable_after_cap"`(許可リスト内、`stage4_allowlist_decision`でallowed=True)でfail-closed停止(STAGE4)する。あわせて`cycle_record["stage4_sub_reason"]="t_target_unlocatable_nonstructural"`と、`structural_verified=False`・分類結果(`last_resort_failure_classification`)を記録する(記録のみ、挙動・許可リスト不変)。委任_Bが無効時に使っていた許可リスト外ラベル(`violation_span_unverified`/`target_not_locatable`)でのSTAGE4停止は廃止(legacy funnel経路を残さない)。
- **R5-(a)【必須】**: `classify_last_resort_failures`で`method`が`covered_by_earlier_rewrite`で始まるT recordを`covered_by_earlier_rewrite`として扱い、`select_last_resort_targets`(L6003)と判定を揃える。統合テスト「同じ文を指す枯渇claim 2件を同時にT→2件目はcarry-forward→STAGE4へ行かない」を先に書き、FAIL(再現)確認→修正→PASS。
- **R1**: covered判定(L7007付近 `r in b`)に「範囲rが現在(置換後)の本文に存在しない」を追加条件。テスト: 同文2回出現・片方のみ書き換え→coveredにならない。
- **R5-(b)**: `blocking_structural_after_ladder`の全発生箇所(L8869, L9065, L9101, L9246)で`structural_verified`(bool+理由)を`cycle_record`へ記録(記録のみ)。
- **R4**: REPORT §76の「regenはTを再実行しない」を訂正(T対象はL9083の`last_resort_delete=True`によりregen内L6123で再実行される。正しくは「regen内で新たに起きた枯渇・位置特定不能は判定されずRecheckへ流れる(安全側)」)。
- R2テスト: SPAN_FALLBACK_CHAIN=True/Falseの両方で`unlocatable_not_covered`が`blocking_confirmed_unlocatable_after_cap`+sub_reasonでSTAGE4、carryされない。

## Fable確認(A側、Trial記録へ追記する事実)

A4-0 goldの正式な違反内容は、Sonnet推測(限定語"some")ではなく**「やり取りの相手(カウンターパート)の取り違え」**: Ledger MUSE-HC-006は電話の相手先=企業・店舗、記事は"completed the exchanges with users"(Museのユーザー)。根拠: `er052_open233_self_recovery_stage2_calibration_01.py` L363-368(Ledgerのissue逐語)。新しい問いは主体の取り違えを「Ledger一致」と誤読して候補から外した=Safety上の本物の見逃し(主体/固有名のFactリスク)。A4-0は過去にもV2 false downgrade・r5-V 0/3と脆弱。

## 事前指定Read一覧

1. `docs/pm/delegation_log/2026-10-06_OPEN-233-CHECKER-SELECTIVITY-RECLASSIFY-01_B2.md`: 全文(B2の詳細指示。本委任の「Fable判断」が優先)。
2. `er052_open233_self_recovery_flow_runner_01.py`: L5980-L6045、L7000-L7035、L7150-L7162、L8155-L8175(許可リストと`stage4_allowlist_decision`)、L8860-L8876、L9048-L9134、L9240-L9250。
3. `er052_open233_self_recovery_flow_runner_01_test_01.py`: Grep `class TestLastResortDeleteDoesNotRetargetRewrittenClaims` →クラス全体。
4. `docs/pm/RESULT_PACKET_A.md`: 全文(A2の報告・SSOT追記文案)。
5. `docs/pm/reclassify_open233_checker_selectivity_01.md`: 全文(Trial記録。§2/§8へ上記Fable確認を追記)。
6. `OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`: Grep `^## §76|§76` →§76全体。
7. `docs/pm/OPUS_FINDINGS_LEDGER.md`: Grep `OF-027|^\| OF-` →OF-027行と最終5行。
8. `docs/pm/ACTIVE_TASK.md`: 全文。`docs/pm/PM_BRIEF.md`: L233-L248(固定ヘッダ書式)。

## 事前指定Grep一覧+追記位置・更新位置の手順

- `OPEN_ITEMS.md`: Grep `OPEN-233-CHECKER-SELECTIVITY-RECLASSIFY-01 委任_B` →直後へ委任_A/A2・委任_B3の進捗を追記(下記SSOT追記文)。
- `docs/pm/REPORT_LEDGER.md`: Grep `OPEN-233-CHECKER-SELECTIVITY-RECLASSIFY-01 委任_B` →直後へ2行(委任_A/A2、委任_B3)。
- REPORT: §76末尾へ「§76-2 Opus任意レビュー指摘の反映(委任_B3)」+R4訂正、§76の後ろに「§77 Checker選択性再分類Trial(委任_A/A2)」(RESULT_PACKET_Aの文案+Trial記録を基に、候補数Before→After表・gold 6件×sample表・監視項目・2方向・実費・例文・Fable確認[A4-0の違反内容]・判定=VALIDATED未達でSTOP)。
- `DECISION_LOG.md`: Grep `OPEN-233-CHECKER-SELECTIVITY-RECLASSIFY-01` →既存エントリ末尾へ追記: (1)Fable判断: 再分類Cap¥10超(見積mid¥13.7)に対しT-3継続条件充足で既存r3構成のまま¥17で実行(実費¥10.46)、(2)結果: NORMAL候補24.2→9.8、gold 5/6(A4-0 sample3消失=カウンターパート取り違えの見逃し)、hold-out 9/9、K19 3/3、HF-011候補なし→VALIDATED未達・ユーザー指示によりSTOP、(3)Opus任意レビュー後のFable判断(R5-a/R2/R1/R5-b採用、R2は許可リスト内ラベル+sub_reason、R4観察)、(4)ユーザー判断事項へ: 次Trial可否(問いの精緻化案: 主体・相手先・範囲・限定語の一致確認を明示/1方向CANDIDATEなら残す等)、STAGE4理由ラベル新設の要否(低優先)。
- `docs/pm/ACTIVE_TASK.md`: 固定ヘッダで上書き。Status=**USER_DECISION_REQUIRED**。UDR-blocking: (U1)再分類Trial VALIDATED未達→次Trial(問い精緻化・再分類¥10前後)へ進めるか/この設計方向を止めるか、(U2)E2E再開(SC 11 run)可否(バグ修正済み・設計問題②未解決のまま)、(U3)STAGE4理由ラベル新設(低優先)。KPI不変・Production未変更を明記。

## 実行コマンド全文

1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-06_OPEN-233-CHECKER-SELECTIVITY-RECLASSIFY-01_B3.md --json-out docs\pm\delegation_log\2026-10-06_OPEN-233-CHECKER-SELECTIVITY-RECLASSIFY-01_B3.md_check.json`
2. 単体: `.venv\Scripts\python.exe -m pytest er052_open233_self_recovery_flow_runner_01_test_01.py -k "LastResort" -q`(R5-(a)テストは修正前FAIL→修正後PASSの両方を記録)
3. 回帰: `.venv\Scripts\python.exe run_project_regression.py --pattern "er052*_test_*.py"`(基準857件PASS、増分=追加テスト数)
4. `git status --porcelain`→明示add→commit→push(2 commitに分けてよい: ①B3コード+テスト+REPORT §76-2、②A/A2成果物+SSOT+REPORT §77。1 commitでも可)。

## SSOT追記文

- OPEN_ITEMS.md(委任_B進捗の直後): 「委任_A/A2(2026-10-06): 段階A 42 run保存候補を新しい問い(Ledger食い違い/Ledger外の具体的新事実)で再分類(gpt-6-luna medium、¥10.46): NORMAL候補24.2→9.8件/記事(llm分19.9→5.3)、全体15.9→8.1、r3 15.6→8.1・r5 5.6→3.2、hold-out 9/9・K19 3/3残存、**gold 5/6(A4-0 sample3が全経路でSUPPORTED化=カウンターパート取り違えの見逃し)→VALIDATED未達、ユーザー指示によりSTOP**。KPI不変・Checker本体不変。委任_B3: Opus任意レビュー指摘反映(classify/select判定統一・carry廃止→許可リスト内ラベル+sub_reasonで即fail-closed・covered条件強化・構造検証記録)、テスト+N件、回帰X件PASS、¥0。Status=USER_DECISION_REQUIRED。」
- REPORT_LEDGER.md: 「- 2026-10-06 | OPEN-233-CHECKER-SELECTIVITY-RECLASSIFY-01 委任_A/A2 | 再分類Trial(¥10.46): NORMAL候補24.2→9.8、gold 5/6(A4-0 1 sample消失)、VALIDATED未達でSTOP。REPORT §77。」「- 2026-10-06 | OPEN-233-CHECKER-SELECTIVITY-RECLASSIFY-01 委任_B3 | Opus任意レビュー反映(R1/R2/R5-a/R5-b)、テスト+N件、回帰X件PASS、¥0。REPORT §76-2。」
- OPUS_FINDINGS_LEDGER.md・DECISION_LOG.md: 上記。
- `docs/pm/reclassify_open233_checker_selectivity_01.md`: §2・§8へ「Fable確認: A4-0の違反内容=カウンターパート取り違え(根拠L363-368)」を追記。

## Git

明示add対象のみ: `er052_open233_self_recovery_flow_runner_01.py`、`er052_open233_self_recovery_flow_runner_01_test_01.py`、`OPEN_ITEMS.md`、`DECISION_LOG.md`、`docs/pm/REPORT_LEDGER.md`、`docs/pm/OPUS_FINDINGS_LEDGER.md`、`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`、`docs/pm/reclassify_open233_checker_selectivity_01.md`、`er052_output/open233_reclassify_01/`配下の全ファイル(script・cost_estimate.json・budget_state.json・reclassify_aggregate.json・runs/)、`docs/pm/delegation_log/2026-10-06_OPEN-233-CHECKER-SELECTIVITY-RECLASSIFY-01_A.md`(+`_check.json`)、同`_A2.md`(+`_check.json`)、同`_B2.md`(+`_check.json`)、同`_B3.md`(+`_check.json`)。`ACTIVE_TASK.md`・`RESULT_PACKET.md`・`RESULT_PACKET_A.md`はaddしない。
コミットメッセージ例: ①`OPEN-233-CHECKER-SELECTIVITY-RECLASSIFY-01: T経路修正にOpus任意レビュー指摘を反映(classify/select判定統一・carry廃止→許可リスト内ラベル+sub_reasonで即fail-closed・covered条件強化・構造検証記録)+test N件、回帰X件PASS(委任_B3、¥0)` ②`OPEN-233-CHECKER-SELECTIVITY-RECLASSIFY-01: 再分類Trial結果【NORMAL候補24.2→9.8、gold 5/6(A4-0消失)、VALIDATED未達・STOP】を記録、REPORT §77、USER_DECISION_REQUIRED(委任_A/A2、¥10.46)`
SSOT編集権: あり(`OPEN_ITEMS.md`/`DECISION_LOG.md`/`docs/pm/REPORT_LEDGER.md`/`docs/pm/OPUS_FINDINGS_LEDGER.md`/REPORT)。`CURRENT_SPEC.md`・`docs/pm/PM_GOVERNANCE.md`は編集しない。push前に`git status --porcelain`で混入確認。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET.md`へ: 1. T-0結果。2. R5-(a)再現FAIL証跡→PASS。3. R2実装後の遷移(行番号、許可リスト内であることの確認、sub_reason記録)。4. R1・R5-(b)変更箇所。5. 追加テスト一覧・回帰件数。6. R4訂正。7. Safety・Human Review基準不緩和の説明。8. A側統合: REPORT §77・SSOT・Opus台帳・Trial記録追記の完了確認。9. commit hash(①②)・push結果・raw.githubusercontent.com URL(変更ファイル分)。10. 一覧外Read理由。11. 残課題(設計問題②、R4観察、ラベル新設要否)。
