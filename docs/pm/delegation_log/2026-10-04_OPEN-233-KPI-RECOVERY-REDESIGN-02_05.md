## 管理ID

`OPEN-233-KPI-RECOVERY-REDESIGN-02`(委任_05)。親: `OPEN-233-SELF-RECOVERY-TRIAL-01`。並行タスクなし。¥0(API課金なし)。

## 性質/到達上限Status/禁止事項

- 性質: Step 7再ループ2回目の前半。rep27(委任_04)でSafety 0・Cost達成・**Human Review 3件**(A4 s1・A5 s1=L6とcarry-forwardの順序不整合によるladder枯渇、neg3 s1=全文Recheckの自己矛盾→再確認DEVIATIONのfail-closed)を、(a)順序不整合の技術是正(実装)、(b)neg3経路のRCA(raw応答まで)と再確認DEVIATION時の処理設計(Human Reviewへ倒さず既存cycle内で処理する案の比較)、(c)Opus批判レビュー用packet、まで行う。有料runは次委任。
- KPI(変更・緩和禁止): Primary=USER_DECISION_REQUIRED/Human Review 0件、Safety=重大Fact見逃し0件、Cost=平均追加+¥2/記事以内、Cap=+¥3/記事以内。QCD優先: 1重大見逃し0 2Human Review 0 3不要Rewriteを増やさない 4+¥2 5非決定性・追加call最小 6Production複雑化回避。「Safetyを理由にHuman Reviewへ逃がさない」。
- 到達上限Status: `IN_PROGRESS`のまま。`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`へ進まない。
- 禁止事項: Production正式path変更禁止(編集は`er052_open233_*`のみ)。Checker Prompt・Schema・判定方法・V7b不変。(b)の設計は実装しない(Opus後)。新しいretry loopを作らない(既存`MAX_CYCLES=2`/`HARD_MAX_CYCLES=3`の内側)。`git add -A`/`stash`/`amend`禁止。既存のM表示差分・untrackedに触れない。`ACTIVE_TASK.md`/`RESULT_PACKET.md`はaddしない。`PM_GOVERNANCE.md`は編集しない。
- 費用上限: ¥0。Phase累計¥641.85、上限¥900、残¥258.15。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSを伴わない。)
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`、ユーザー正式決定、費用上限[Cap]を伴う全委任で常時有効): 費用上限[Cap]は「暴走防止のためのGuardrail」であり、Cap到達=自動STOPではない。禁止事項/性質欄の費用上限記載は上記の定型文に従う。

T-0の補足: 保存先 `C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-04_OPEN-233-KPI-RECOVERY-REDESIGN-02_05.md`。**委任文は全文そのまま保存。** 一時ファイルはリポジトリ外。スクリプトはWrite/Editで作る。全体回帰は`PYTHONIOENCODING`なしのシェルで実行。

## ユーザー指示(原文、該当部分)

````
Step 7
まだ未達なら、自律的に原因分析→改善ループをもう一度回す。
合理的な改善余地が残っている限り、ユーザーへKPI緩和を提案しない。
(略)
Safetyを理由にHuman Reviewへ逃がさないこと。
Human Reviewゼロ自体がKPIです。
````

## 作業1: (a) L6とcarry-forwardの順序不整合の技術是正(実装)

- RCA確認: rep27 `safety_A4` s1・`safety_A5` s1のinstance JSONで、同一文を「引用符付き」「引用符なし」の2文字列で指摘したclaimが、1つ目のRewrite後にL6で**書き換え済みの文**を復元され、2回目のRewriteが走ってladder枯渇→STAGE4になった経路を、cycle内の順序(handoff解決→Rewrite→carry-forward判定→L6)とともに行番号付きで設計書§12-1に記録。rep24(L6 OFF)で同claimが`covered_by_earlier_rewrite_in_cycle`で合格していた事実と対比。
- 是正(決定論、追加call 0): `resolve_violation_spans`の流れで、**L6の前に**同cycleの先行Rewriteによるcarry-forward判定(委任_04の部分一致を含む)を適用する。さらにL6が復元した文が同cycleの`after_units`(置換後文)と一致する場合はcarry-forwardへ回す(二重Rewrite防止)。`sentence_restore`記録に`skipped_reason="carry_forward_precedence"`等を残す。
- テスト: A4/A5のrep27実データをfixture化し、是正後は`covered_by_earlier_rewrite_in_cycle`で解決されること/L6の他の復元(rep26・rep27の計11件)が変わらないこと/OFF不変。runner単体・er052回帰・全体回帰(基準11件以外新規なし)。
- ¥0 replay: rep27のA4 s1・A5 s1の記録済み本文・claimで、是正後のhandoff結果を決定論replayし、二重Rewriteが発生しない(carry-forwardで処理される)ことを確認。

## 作業2: (b) neg3 s1 `unconfirmed_after_reverify`のRCA(¥0、raw応答まで)

- rep27 `neg3_hormuz_prodrunner_b1b` s1のcall_log/instance JSONから、(1)Rewrite後の全文Recheckの**raw応答全文**(`LEDGER_COMPLIANT`∧`all_prior_issues_resolved=false`の自己矛盾)、(2)再確認(`recheck_confirm`)の**raw応答全文**(`LEDGER_DEVIATION`∧`all_prior_issues_resolved=true`。deviationsの具体claim・severity・issue)、(3)両callのprompt(特に`prior_issues`の内容: 委任_01の是正で現行本文が渡っているか、その文言がCheckerに「未解消」と誤読させる余地があるか)、(4)rep23 neg3 s2(同じ`unconfirmed_after_reverify`)とrep27 neg3 s2(1 cycle合格)との差、を設計書§12-2に逐語で記録。
- 再確認が返したdeviation claimを特定し、正式基準で仮ラベル(重大/軽微/問題なし)。それが「Rewrite後の文への新規指摘」「別の文への新規指摘」「空(claimなし)」のどれかを確定。
- 既存ログ全体で`unconfirmed_after_reverify`の発生件数・instance・再確認結果の型(claimあり/なし)を集計(§12-2末尾)。

## 作業3: (b)の処理設計(比較、実装しない)

設計書§12-3。現行(委任_11以来): Recheckが自己矛盾→再確認1回→再確認がDEVIATIONならSTAGE4(fail-closed)。KPI(Human Review 0)に対し、「再確認がDEVIATIONを返したら、その指摘を通常のRecheck結果として既存cycle内で処理する」案を中心に比較:
- 案N1: 再確認DEVIATIONのclaimを、cycle 2のRecheck由来claimと同じ経路(handoff→Stage 2[Tier 0/S1含む]→Rewrite→Recheck)へ流す。cycle上限(`MAX_CYCLES=2`、`HARD_MAX_CYCLES=3`)は既存のまま。claimが空のDEVIATIONは「prior issuesのrangeに対するladder次段のRewrite」として扱う。
- 案N2: 自己矛盾時の再確認を「2回」にし、2回とも同じ結論(COMPLIANT/DEVIATION)のときだけ採用、割れたらDEVIATION側(安全側)を案N1で処理。追加call 1回(¥0.27)。
- 案N3: 自己矛盾の原因がprior_issuesの文言(現行本文を渡した結果、Checkerが「指摘文がそのまま残っている=未解消」と読む)にあるなら、prior_issuesに「この文は修正済みの現行本文です。解消されているかを判定してください」の明示を加える(Checker本体Promptは不変、渡す内容の明確化=技術是正)。
- 各案: Human Reviewへの効果(既存ログの発生件数が0になるか)/Safety(DEVIATION側へ倒す=安全側か)/不要Rewrite(claimが軽微以下なら Stage 2で降格され Rewriteされない)/費用/非決定性/cycle上限との関係(cycle 3到達率)/Production配線時の整合(er003のRecheck経路)。推奨案と根拠。
- 残るSTAGE4経路の棚卸し: `violation_span_unverified`(L6で縮小)/`ladder_exhausted_without_full_rewrite`(是正(a)で縮小。他の発生条件は?)/`cycle_limit_exhausted`/`unconfirmed_after_reverify`/`ja_deviation_unresolved`(english_onlyで無効化)/その他。各経路の既存ログ発生件数と、KPI 0に向けた扱い(技術是正/設計/Production配線時)。

## 作業4: Opus packet

`docs/pm/opus_packet_open233_kpi_recovery_02_02.md`(雛形(a)〜(g)、条件A、独立レビューブロック逐語)。論点: 1.是正(a)の順序変更が他のL6復元・carry-forwardの安全性を損なわないか(書き換え済み文の復元を防ぐ判定の妥当性) 2.案N1〜N3の比較(Human Reviewへ逃げていないか、Safety側へ倒れているか、retry loopを増やさないか) 3.残るSTAGE4経路の棚卸しに漏れがないか 4.より単純な方法 5.Production配線時の整合。(b)にrep27の3件の逐語データ(raw応答含む、長ければ要点+参照)、既存ログ集計、cycle別の件数。2万字以内。

## 作業5: SSOT

- `OPEN_ITEMS.md` KPI-RECOVERY-02行Status: 「委任_05: rep27 Human Review 3件のRCA(A4/A5=L6とcarry-forward順序不整合→技術是正実装・¥0 replayで二重Rewrite解消確認、neg3=Recheck自己矛盾→再確認DEVIATIONのfail-closed→処理設計N1〜N3)、Opus#12 packet。次: Opus#12→Fable→委任_06=実装+A4/A5/neg3再確認+29件再確認」。`docs/pm/REPORT_LEDGER.md`、REPORT §55、設計書§12、`docs/pm/ACTIVE_TASK.md`(addしない)。

## 事前指定Read一覧

- rep27 instance JSON: `safety_A4` s1、`safety_A5` s1、`neg3_hormuz_prodrunner_b1b` s1/s2(Grep/Pythonで該当フィールド抽出。raw応答はcall_log)。rep23 neg3 s2、rep24 A4/A5 s1(対比)。
- runner: Grep `resolve_violation_spans|carry_forward_resolution|collect_replaced_units|covered_by_earlier_rewrite_in_cycle|vs_sentence_restore_resolve|after_units|recheck_confirm|unconfirmed_after_reverify|all_prior_issues_resolved|ladder_exhausted_without_full_rewrite|escalation_reason|STAGE4|MAX_CYCLES|HARD_MAX_CYCLES|resolve_prior_issue_text` → 該当範囲(全文Read禁止)。
- `docs/pm/design_open233_span_sentence_restore_01.md` §4(L6手順)、`docs/pm/design_open233_kpi_recovery_02.md` §10〜§11。
- 既存ログ: `er052_output/open233_self_recovery_flow_runner_01_*/`をPythonで走査(`escalation_reason`集計)。
- テンプレート: `docs/pm/templates/OPUS_CONTEXT_PACKET_TEMPLATE.md`、`OPUS_INDEPENDENT_REVIEW_BLOCK.md`。
- SSOT: Grep `KPI-RECOVERY-REDESIGN-02` → 更新位置。

## 事前指定Grep一覧+追記位置

- 上記のとおり。`git grep -n "er052_open233" -- "er003*.py" "er009*.py" "er010*.py" "er012*.py" "er019*.py"`(0件確認)。

## 実行コマンド全文

作業ディレクトリ `C:\Users\tensh\eigo-radio`。

T-0:
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-04_OPEN-233-KPI-RECOVERY-REDESIGN-02_05.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-04_OPEN-233-KPI-RECOVERY-REDESIGN-02_05.md_check.json

テスト・回帰:
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -m unittest er052_open233_self_recovery_flow_runner_01_test_01
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\run_project_regression.py --pattern "er052*_test_*.py"
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\run_project_regression.py

¥0 replay: `er052_output/open233_kpi_recovery_02_offline_01/replay_cf_l6_order_01.py`(新規)。

順序: T-0 → 作業1(テスト・replay含む) → commit/push → 作業2 → 3 → 4 → 5 → commit/push → 報告。

## Git(明示add対象・コミットメッセージ)

- SSOT編集権: `OPEN_ITEMS.md`の1行、`REPORT_LEDGER.md`の1行、REPORT。
- 1回目commit: runner、テスト、replay、設計書§12-1、委任ログ。メッセージ: `OPEN-233-KPI-RECOVERY-REDESIGN-02: rep27 Human Review 3件のうちA4/A5(L6とcarry-forwardの順序不整合による二重Rewrite→ladder枯渇)を技術是正(carry-forward優先、追加call 0)、¥0 replayで解消確認(委任_05)`
- 2回目commit: 設計書§12-2/12-3、packet、集計出力、SSOT。メッセージ: `OPEN-233-KPI-RECOVERY-REDESIGN-02: neg3 unconfirmed_after_reverifyのRCA(raw応答)と再確認DEVIATION処理の設計案N1〜N3、残STAGE4経路の棚卸し、Opus#12向けpacket(委任_05)`

## 報告(RESULT_PACKET項目)

(1)結論10行以内、(2)是正(a)の実装箇所・テスト・replay結果、(3)neg3 RCA(自己矛盾と再確認のraw要点、特定したclaimと仮ラベル、prior_issues文言の影響有無、既存ログ発生件数)、(4)案N1〜N3比較表と推奨、残STAGE4経路棚卸し表、(5)packet文字数、(6)SSOT、(7)T-0・commit・push・raw URL、一覧外Read、確認/推測の区別、(8)Fableへの論点。
