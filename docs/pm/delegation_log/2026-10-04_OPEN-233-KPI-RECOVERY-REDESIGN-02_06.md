## 管理ID

`OPEN-233-KPI-RECOVERY-REDESIGN-02`(委任_06)。親: `OPEN-233-SELF-RECOVERY-TRIAL-01`。並行タスクなし。

## 性質/到達上限Status/禁止事項

- 性質: Opus批判レビュー#12(本委任文末尾に全文)に対するFableの評価(下記)に基づき、Step 7再ループ2回目の後半を実行する: N1′(再確認結果の合流)とN3′(Recheckへ書き換え前後の対を渡す)の実装→¥0分類→neg3/neg2の限定A/B(有料≈¥8)→構成確定→Step 6再確認(rep28: Safety-critical群+29件、同一構成、有料≈¥20)→KPI判定(`VALIDATED`/未達ならFableへ)。
- KPI(変更・緩和禁止): Primary=USER_DECISION_REQUIRED/Human Review 0件、Safety=重大Fact見逃し0件、Cost=平均追加+¥2/記事以内、Cap=+¥3/記事以内。QCD優先: 1重大見逃し0 2Human Review 0 3不要Rewriteを増やさない 4+¥2 5非決定性・追加call最小 6Production複雑化回避。
- 到達上限Status: Step 6のKPI判定まで。4つ同時達成→`VALIDATED`(Trial評価、Production採用ではない)。未達→`IN_PROGRESS`のままFableへ報告(ユーザーへKPI緩和を提案しない)。`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`へ進まない。既存の個別APPROVED項目のStatusも変更しない。
- Fableの評価(Opus#12の採否。SSOTへ逐語記録。変更しない):
  1. **是正(a)(carry-forward優先)は維持**(Opus: 妥当)。規則(2)も維持。
  2. **N1′を採用**(N1-aは不採用): 再確認が「COMPLIANT∧all_prior=True」以外を返したら、(i)再確認deviationsのMAJOR ∪ (ii)再確認`prior_issues_resolved`でresolved=falseの元blocking claim(dev)を、fact_idで重複除去して次cycleのstage1_deviationsとし、既存Stage 2(Tier 0/S1含む)→Rewriteへ流す。(ii)は既存`find_matching_prior_record`でladderに乗る。(i)(ii)とも空なら既存`not blocking_claims`経路でRESOLVED_REWRITE_THEN_DOWNGRADE(監査用`reverify_deviation_without_major=True`を記録)。`unconfirmed_after_reverify`のSTAGE4経路は廃止。追加call 0、既存cycle上限の内側。
  3. **通常経路の潜在ギャップも同時に是正**: 通常のRecheckが`DEVIATION∧all_prior=False`で、未解消のprior issueがdeviationsに無い場合も、(ii)と同じく元claimを次cycleへ合流させる(Opus論点1・2の指摘。構造を1規則に統一: 「未解消のprior issueは必ず次cycleのStage 2を通る」)。
  4. **N3′を技術是正として採用(スイッチ付き、A/Bで効果測定)**: 通常のRecheckにも、再確認が既に使っている「書き換え前後の対」ブロック(cite-or-release指示は除く)を同じ形式で渡す。根拠: ユーザー指示(KPI-RECOVERY-02)は「Promptや入力設計の改善余地がある」をUSER_DECISION_REQUIREDではないと明記し、「Rewrite前の古い文章をCheckerへ渡していた問題」を技術是正としている。N3′はその完結(`issue`が指す元の文を入力に揃える)。Checker本体のPrompt文・Schema・判定規則・`issue`文言は変えない(Trial側で渡す情報ブロックの追加のみ)。境界事例である点はユーザーへ報告する。採用判定はA/B(下記)で、Safety側の悪化(prior issue未解消の取りこぼし)がなく自己矛盾率が下がる場合のみ29件構成に含める。
  5. **L6はONのまま維持・観測継続**(Opus論点4)。
  6. **停止経路の定義**: 例外終了(API失敗・連続エラー・予算上限)で`stage4_reason`を持たないrunも「Human Review相当」としてKPIに数える(rep27は0件)。N1′導入後の移動先(`same_claim_fact_id_reblocked`/`cycle_limit_exhausted`)を監視対象に加える。
  7. **旧構成の`ladder_exhausted` 10件の¥0分類**(同cycle同一文の重複claim型か否か)を実施し、L6以外の原因が残るかを確認。
  8. **N2・再確認callの廃止は不採用**。Production配線は「再検査結果を正規化する純関数(PASS/NEXT_CYCLE/STOP)をTrial/Productionで共有、Productionが自己回復flowを持たない間はNEXT_CYCLE→STOP」の方向を`OPEN-233-A1-PROD`に記録(実装は配線時)。
- 禁止事項: Production正式path変更禁止(編集は`er052_open233_*`のみ)。Checker本体Prompt文・Schema・判定規則・V7b不変。新しいretry loopを作らない(`MAX_CYCLES=2`/`HARD_MAX_CYCLES=3`不変)。Human Reviewへ倒す新経路を作らない。Step 6の母数・nは固定(29 instance・38 run)、再実行・n増しなし。採否基準を結果を見て変えない。`git add -A`/`stash`/`amend`禁止。既存のM表示差分・untrackedに触れない。`ACTIVE_TASK.md`/`RESULT_PACKET.md`はaddしない。`PM_GOVERNANCE.md`は編集しない。
- 費用上限: 上限¥35(Guardrail。内訳の目安: A/B[neg3・neg2×n=2×2構成=8 run]≈¥8、rep28≈¥20)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。Phase累計¥641.85、上限¥900、残¥258.15。有料実行前に費用概算を出し実測と並記。
- 即時STOP(有料run中): JA変更/例外2 instance以上/1 instance-run費用>¥7。重大見逃し・STAGE4は止めずに完走し、件数と原因を特定して報告。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSを伴わない。)
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`、ユーザー正式決定、費用上限[Cap]を伴う全委任で常時有効): 費用上限[Cap]は「暴走防止のためのGuardrail」であり、Cap到達=自動STOPではない。禁止事項/性質欄の費用上限記載は上記の定型文に従う。

T-0の補足: 保存先 `C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-04_OPEN-233-KPI-RECOVERY-REDESIGN-02_06.md`。委任文は全文そのまま保存(末尾のOpus#12全文を含む)。一時ファイルはリポジトリ外。スクリプトはWrite/Editで作る。全体回帰は`PYTHONIOENCODING`なしのシェルで実行。10分制限で中断した場合は`skip existing`で1回だけ再開し記録。

## ユーザー指示(原文、該当部分。全文は`DECISION_LOG.md`末尾の`OPEN-233-KPI-RECOVERY-REDESIGN-02`)

````
以下はUSER_DECISION_REQUIREDではありません。
- 実装バグ
- 古い本文を渡していた
- Trial補助が評価を歪めていた
- Promptや入力設計の改善余地がある
- 後段の判定ロジックにSafety holeがある
- Opusが改善案を出した
(略)
Step 6
Safety-critical群＋既存29件を再確認。
ここで最低限、
- Human Review 0件
- 重大見逃し 0件
を同じ構成で同時に確認すること。
````

## 作業1: Opus#12の保存とFable評価(¥0)

`docs/pm/opus_l2_review_open233_kpi_recovery_02_12.md`(依頼文[本委任文末尾の要旨]、Opus#12全文、Fable評価1〜8逐語、11-3の8項目照合、STOP条件非該当の根拠)。設計書`docs/pm/design_open233_kpi_recovery_02.md` §13「Opus#12後の採否と実装仕様(N1′/潜在ギャップ是正/N3′/停止経路定義)」。

## 作業2: 実装(runner、KPI構成でON、既定OFF)

- 2-1 N1′: `normalize_recheck_outcome(recheck, confirm, prior_blocking_claims)`(純関数)→`PASS`/`NEXT_CYCLE(deviations)`/`STOP`(STOPは例外終了のみ)。再確認結果の合流(Fable評価2)。`unconfirmed_after_reverify`経路を廃止(スイッチ`RECHECK_MERGE_UNRESOLVED`、既定OFFで旧挙動)。
- 2-2 潜在ギャップ是正: 通常Recheckの`DEVIATION∧all_prior=False`でも未解消prior claimを合流(同スイッチ)。
- 2-3 N3′: `RECHECK_BEFORE_AFTER_PAIRS`(既定OFF)。ONのとき通常Recheckのpromptに、再確認で使っている前後の対ブロックを同形式で追加(cite-or-release指示は除く)。Checker本体template(er003)はバイト不変(sha固定テスト)。prompt sha256・ブロック長を記録。
- 2-4 記録: `reverify_deviation_without_major`、`recheck_prior_issues_resolved`(委任_05追加済み)の逐語、`merged_from`(reverify_major/unresolved_prior/normal_gap)、停止経路の統一集計(`stage4_reason`+例外終了)。
- 2-5 `KPI_TRIAL_SWITCHES`に`RECHECK_MERGE_UNRESOLVED: True`を追加。`RECHECK_BEFORE_AFTER_PAIRS`はA/B後に確定(作業4)。
- テスト: N1′(reverify MAJOR合流/unresolved prior合流/重複除去/空→RESOLVED_REWRITE_THEN_DOWNGRADE+監査flag)/潜在ギャップ/N3′(prompt差分・template不変・OFF不変)/純関数の全分岐/KPI構成。runner単体・er052回帰・全体回帰(基準11件以外新規なし)。

## 作業3: ¥0分類(Fable評価7)

旧構成の`ladder_exhausted_without_full_rewrite` 10件(rep16・rep18・rep20・iter8)を「同cycle同一文の重複claim型/その他」に分類し、その他があれば原因を1行で(設計書§13-4)。

## 作業4: 限定A/B(有料≈¥8): neg3・neg2

`er052_open233_self_recovery_flow_runner_01_rep28a_ab_01.py`。instance=`neg3_hormuz_prodrunner_b1b`、`neg2_meta_refresh_a2`、n=2、構成A=KPI構成+N1′(N3′ OFF)、構成B=KPI構成+N1′+N3′ ON。計8 run。出力`er052_output/open233_self_recovery_flow_runner_01_rep28a/`。
- 測定: Recheck自己矛盾率(A/B)、再確認call回数、`recheck_prior_issues_resolved`の逐語(resolved=falseの理由文→自己矛盾の機序を確認)、再確認deviationsの逐語と仮ラベル、N1′の合流件数とStage 2結果(降格/BLOCKING)、cycle数、STAGE4(統一定義)、不要Rewrite、費用。
- **N3′採否基準(事前設定)**: Bで自己矛盾率がAより下がり、かつ(ア)prior issueのresolved=true判定のうち本文が実際に書き換わっていないもの(形だけの解消)が0件、(イ)STAGE4・見逃しが増えない → N3′ ONを29件構成に採用。満たさない→N3′ OFF(N1′のみ)で29件。

## 作業5: Step 6再確認 rep28(有料≈¥20、1回)

`er052_open233_self_recovery_flow_runner_01_rep28_full_01.py`(rep27複製、確定構成)。29 instance・38 run。出力`er052_output/open233_self_recovery_flow_runner_01_rep28/`。
- 集計(rep27・rep24・iter7比): Human Review(統一定義: `stage4_reason`全種+例外終了)件数・理由/重大見逃し(旧・新定義、`residual_at_pass`全件仮ラベル)/Safety-critical 6件の検出・経路/Tier 0・S1・L6・N1′合流・N3′の発火/不要Rewrite(既存定義+全run件数)/過剰Major/cycle分布(`same_claim_fact_id_reblocked`・`cycle_limit_exhausted`の移動監視)/JA 0/費用(合計・平均追加/記事[rep24比・iter7比]・worst・Cap超)/モデル・構成(モデルIDはrunner定数から記録)。
- **KPI判定**: Human Review 0∧重大見逃し0∧平均追加≤+¥2∧worst追加≤+¥3 → `VALIDATED`。未達→原因分析をREPORTに書きFableへ。

## 作業6: SSOT

- `OPEN_ITEMS.md` KPI-RECOVERY-02行Status: 「委任_06: Opus#12→Fable評価(N1′採用・潜在ギャップ是正・N3′技術是正[境界事例]・L6維持)、実装、A/B【自己矛盾A x%/B y%、N3′採否】、rep28【Human Review d・見逃しe・不要Rewrite f・平均追加+¥g・worst+¥h】→【VALIDATED/未達】。次: 【Closeout(委任_07)/再ループ】」。`OPEN-233-A1-PROD`行に「再検査結果の正規化純関数(PASS/NEXT_CYCLE/STOP)をTrial/Production共有、未配線時はNEXT_CYCLE→STOP」を追加。`docs/pm/REPORT_LEDGER.md`、REPORT §56、`docs/pm/ACTIVE_TASK.md`(addしない)。`CURRENT_SPEC.md`・`DECISION_LOG.md`は編集しない(Closeoutで転記)。

## 事前指定Read一覧

- runner: Grep `recheck_confirm|unconfirmed_after_reverify|all_prior_issues_resolved|prior_issues_resolved|find_matching_prior_record|same_claim_fact_id_reblocked|not blocking_claims|RESOLVED_REWRITE_THEN_DOWNGRADE|before_after_pairs|cite_or_release|build_prior_issues_instruction|stage4_reason|KPI_TRIAL_SWITCHES|run_recheck|full_recheck` → 該当範囲(全文Read禁止。Opus#12が示した行: 8180〜8319、7690〜7839、8140〜8164、7466〜7495)。
- `docs/pm/design_open233_kpi_recovery_02.md` §12。`er052_output/open233_kpi_recovery_02_offline_01/agg_stage4_reasons_01.md`、`rca_neg3_prompt_reconstruct_01.md`。
- rep27スクリプト・`rep27_agg_01.py`(複製元)。旧ログ: `ladder_exhausted`10件のinstance JSON(Pythonで走査)。
- `er003_v1_en_direct_vfl_01_generate.py` Grep `build_prior_issues_instruction`(read-only、sha固定用)。
- SSOT: Grep `KPI-RECOVERY-REDESIGN-02`、`OPEN-233-A1-PROD` → 更新位置。

## 事前指定Grep一覧+追記位置

- 上記のとおり。`git grep -n "er052_open233" -- "er003*.py" "er009*.py" "er010*.py" "er012*.py" "er019*.py"`(0件確認)。

## 実行コマンド全文

作業ディレクトリ `C:\Users\tensh\eigo-radio`。

T-0:
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-04_OPEN-233-KPI-RECOVERY-REDESIGN-02_06.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-04_OPEN-233-KPI-RECOVERY-REDESIGN-02_06.md_check.json

テスト・回帰:
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -m unittest er052_open233_self_recovery_flow_runner_01_test_01
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\run_project_regression.py --pattern "er052*_test_*.py"
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\run_project_regression.py

A/B(有料):
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_open233_self_recovery_flow_runner_01_rep28a_ab_01.py --stage main --n 2 --budget-jpy 10
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_open233_self_recovery_flow_runner_01_rep28a_ab_01.py --stage agg

rep28(有料、1回):
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_open233_self_recovery_flow_runner_01_rep28_full_01.py --stage main --budget-jpy 24
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_open233_self_recovery_flow_runner_01_rep28_full_01.py --stage agg
(引数名は実装に合わせてよい。)

順序: T-0 → 作業1 → 2(テスト含む) → 3 → 1回目commit/push → 4 → 構成確定 → 5 → 6 → 2回目commit/push → 報告。

## Git(明示add対象・コミットメッセージ)

- SSOT編集権: `OPEN_ITEMS.md`の2行、`REPORT_LEDGER.md`の1行、REPORT。
- 1回目commit: Opus#12保存、設計書§13、runner、テスト、¥0分類。メッセージ: `OPEN-233-KPI-RECOVERY-REDESIGN-02: Opus批判レビュー#12を保存しFable評価、再確認結果の合流N1′(unconfirmed_after_reverify廃止・未解消prior必ずStage 2へ)・通常経路の潜在ギャップ是正・Recheckへ前後対N3′(スイッチ)を実装、旧ladder_exhausted 10件分類(委任_06)`
- 2回目commit: A/B・rep28スクリプトと出力、SSOT。メッセージ: `OPEN-233-KPI-RECOVERY-REDESIGN-02: neg3/neg2 A/B【自己矛盾A x%/B y%、N3′採否】、Step 6再確認rep28 29件+Safety-critical【Human Review d・見逃しe・不要Rewrite f・平均追加+¥g・worst+¥h】→【VALIDATED/未達】(委任_06)`

## 報告(RESULT_PACKET項目)

(1)結論10行以内(KPI 4つの実測値、VALIDATED/未達)、(2)実装箇所・テスト、(3)¥0分類結果、(4)A/B結果表(自己矛盾率・resolved=false理由文の要点・再確認deviationの逐語と仮ラベル・N3′採否)、(5)rep28結果表(rep27/24/iter7比、Safety-critical 6件、各機構の発火、STAGE4統一定義、移動監視、費用、モデル・構成)、`residual_at_pass`全件仮ラベル、(6)未達なら原因分析と再ループ案、(7)費用(概算/実測/Phase累計)、(8)SSOT、(9)T-0・commit・push・raw URL、一覧外Read、確認/推測の区別、(10)Fableへの論点(Closeoutへ進めるか、N3′の境界事例の報告文案)。

---

## 参考(逐語): Opusへの依頼(レビュー#12)

[Fableがopus-consultantへ送った依頼。論点1〜7: 1.是正(a)の安全性 2.案N1-aの評価(空DEVIATIONの扱い) 3.neg3/neg2の自己矛盾の根本原因(prior_issues入力の不整合、N3具体化、技術是正か設計変更か) 4.L6の位置づけ 5.残STAGE4経路の棚卸し 6.より単純な方法 7.Production配線。packet: `docs/pm/opus_packet_open233_kpi_recovery_02_02.md`、設計書§12。]

## 参考(逐語): Opus独立レビュー#12 全文

# Opus独立レビュー#12: OPEN-233-KPI-RECOVERY-REDESIGN-02(rep27のHuman Review残3件の是正)

## 結論
- **是正(a)(carry-forwardをL6より先に適用)**: 妥当です。維持してよいです。
- **案N1-a**: 方向は正しいものの、このままでは不十分です。修正版のN1′を推奨します。
  - 欠陥1: N1-aは再確認(Recheck結果が自己矛盾したときに追加で1回呼ぶ確認call)のdeviations(Checkerが返す逸脱指摘)のうちMAJORだけを次cycleへ渡します。このため、再確認が「元指摘は未解消」と答えたのに、その指摘がdeviationsに無い場合、元指摘が消えてしまいます。現行の再確認が防いでいる「静かな降格」を作り直すことになります。
  - 欠陥2: 空のDEVIATIONだけをSTAGE4に残すのは、通常経路より厳しい特別扱いです。根拠が無く、Human Reviewの経路を1本残してしまいます。
- **neg3/neg2の自己矛盾の根本原因**: 設計書§12-2は「入力の不整合は主因でない」としていますが、この推論には誤りがあります。既存データは逆に、「Recheckに書き換え前後の対が無いこと」が主因だという説を強く支持しています(論点3)。
- **条件Bの判定**: neg3の再発(iter5〜rep27で5回)は個別バグの連続ではありません。原因は2つの設計上の問題です。(1)再確認の結果を捨てて、Stage 2(materiality判定)を通さずSTAGE4へ直行させている。(2)Recheckの入力に、`issue`が指している元の文が含まれていない。

## 12観点(要点のみ)
1. 必要か: 是正(a)は必要です(実害2件を確認済み)。N1系も必要です。STAGE4へ直行する現行の扱いは、通常経路と矛盾しています。
2. 単純化: N1′は、`stage1_deviations`を作る規則を1か所変えるだけで済みます。
3. 既存の再利用:
   - 再確認が使っている書き換え前後の対(`before_after_pairs`)を、通常のRecheckにも渡す案があります(N3′、論点3)。
   - 次cycleへ渡す経路・Stage 2・cycle上限は既存のものをそのまま使えます。
4. 情報の喪失: 現行は再確認のdeviationsとprior_issues_resolved(項目別の解消判定)を捨てています。これが今回の穴の正体です。
5. LLM callの追加: N1′・N3′とも追加callは0です。N3′は再確認の発生そのものを減らす見込みです。
6. 非決定性: N1′は増やしません。N2(再確認2回)は増やします。
7. Human Review: N1′で`unconfirmed_after_reverify`の経路自体がなくなります。ただし後述のとおり、別の経路へ移る可能性があります。
8. 不要Rewrite: N1′で、再確認の指摘がBLOCKINGになった場合だけcycle 2のRewriteが増えます。中身は未測定です。
9. コスト: 増えません。
10. retry / fallback / regenerationとの整合: 既存のcycle上限(MAX_CYCLES=2、HARD_MAX_CYCLES=3)の内側に収まります。新しいloopは作りません。
11. 失敗時に安全側へ倒れるか: N1′の条件を守れば倒れます(論点2)。
12. 再発防止: N1′とN3′を組み合わせれば、個別パッチではなく構造的な是正になります。

## 論点1: 是正(a)の安全性
- **他のL6復元への影響**: 新しい判定は「同じcycleに先行Rewriteがある」場合だけ動きます。L6の本来の救済例であるrep24のA2A3 s2 c2とB3 s2 c2は、どちらもcycle 2の事例です(span restore設計書§5-2)。これらは今回の是正の対象外で、引き続きL6が働きます。
- **同じ文を指す2つのclaimが別の問題を指す場合**: 実害は出にくい構造です。runner 8148〜8158行で確認しました。
  - covered扱いになったclaimも`blocking_claims`に含まれたまま、自分の`issue`付きでRecheckの`prior_issues`に入ります。つまり、もう一方の問題は「解消したか」を項目として明示的に検査されます。
  - ただし未解消と判定された後、それがどう流れるかは論点2の欠陥1と同じ穴を通ります。再確認経由だとN1-aでは消えます。通常経路でも、DEVIATIONかつ`all_prior=False`で、その問題がdeviationsに入っていなければ消えます(既存の潜在ギャップ)。
  - したがって、是正(a)の安全性はN1′の「未解消のprior issueを次cycleへ合流させる」とセットで成り立ちます。
- **規則(2)(`restored_equals_after_unit`)**: 同じcycle内のclaimはcycle開始時点の本文に基づいて作られます。先行Rewriteが新しく持ち込んだ問題を指すことはありえないので、誤って適用される余地は小さいです。単独で効いた実例は0件で、合成テストのみです。害は小さいので維持でよいです。

## 論点2: N1-aの評価と代替案
- **N1′(推奨)**: 再確認がCOMPLIANTかつ`all_prior=True`以外の結果を返したら、次の2つを合わせて次cycleのstage1とし、既存のStage 2へ流します(重複はfact_idで除く)。
  - (i) 再確認deviationsのMAJOR
  - (ii) 再確認の`prior_issues_resolved`でresolved=falseになった元のblocking claimのdev
- **(ii)が既存のladder機構に乗ること**: (ii)は元claimそのものなので、既存の`find_matching_prior_record`で一致します。結果は次のどちらかになり、既存のladderに自然に乗ります。
  - まだ段落水準まで試していなければ段落水準へ昇段してRewrite
  - 試行済みなら`same_claim_fact_id_reblocked`
- **空のDEVIATIONの扱い**: (i)(ii)とも空になった場合は、既存の`not blocking_claims`経路でRESOLVED_REWRITE_THEN_DOWNGRADEになります。これは通常経路で「DEVIATIONだがMAJORは0件」のときと同じ扱いです。
  - 安全性の根拠: 全文検査2回(Recheck=COMPLIANT、再確認=MAJORなし)と、cite-or-release(根拠の引用ができない未解消を解除する仕組み)を経た「元指摘は解消」が揃っています。元指摘が静かに消えることはありません。
  - 監査用に`reverify_deviation_without_major=True`を記録するよう追加を推奨します。
- **3条件の判定**:
  - Human Reviewへ逃げない: 満たします。
  - Safety側へ倒れる: 満たします。未解消は必ずStage 2を通り、降格を防ぐ既存のガード(Tier 0・S1)も維持されます。
  - 新しいretry loopを作らない: 満たします。既存の`cycle`を使います。
- **他案との比較**:
  - N1-a: 空のDEVIATIONでHuman Reviewが残り、KPI(Human Review 0)と整合しません。
  - 「もう1回再確認」: N2と同じで、費用と非決定性が増えるだけです。
  - N1-b(ladder次段のRewrite): 問題が指定されていない文を書き換えることになり、不要Rewriteが増えます。
  - 以上により、いずれもN1′より劣ります。
- **残るリスク**:
  - 再確認の指摘がBLOCKINGと判定されれば、cycle 2のRewriteが走ります。ACCEPTABLE記事での不要Rewriteになりえます。
  - Human Reviewが`cycle_limit_exhausted`や`same_claim_fact_id_reblocked`へ移るだけの可能性があります。
  - どちらも次runで、記録専用で追加した逐語ログから測る必要があります。

## 論点3: 自己矛盾が恒常的になる根本原因
- **§12-2の推論の誤り**: §12-2は「現行本文化の後も4/4で自己矛盾した。だから主因ではない」としています。しかし、委任_01の現行本文化こそが「`claim_in_article`=書き換え後、`issue`=書き換え前の欠陥」という不整合を生んでいます(是正前は`claim_in_article`が本文に存在しない、という別の不整合でした)。両方とも不整合なので、この推論で否定できるのは「本文の取り違え」説だけです。
- **より強い証拠(§12-2の対比表6行)**:
  - 6件すべてで、Recheck(前後の対なし)は`all_prior=False`でした。
  - 6件すべてで、再確認(前後の対あり)は`all_prior=True`でした。
  - 自己矛盾は「出来事の継続を残す」正しい書き換え(rep26 s1、rep27 s2)でも出ています。
  - `released_count=0`なので、cite-or-releaseが機械的に解除した結果でもありません。Checker自身が判断を変えています。
  - つまり、解消判定を変えている要因は文面の良し悪しではなく、「`issue`が指す元の文が入力にあるかどうか」だと推定されます(強い推定)。
- **再確認のDEVIATIONが約24%で出る理由**: 解消判定とは別に、全文検査そのものが揺れていることによると考えられます(N1′で扱います)。
- **N3′(具体化)**: Checker本体のPrompt・Schema・判定規則は変えずに、通常のRecheckにも、再確認で既に使っている書き換え前後の対の部分(cite-or-release指示は除く)を同じ形式で渡します(Trial側のみ)。
  - 効けば、neg3/neg2の再確認callの大半(neg3は82%)が不要になります。費用・非決定性とも下がり、再確認の揺れに当たる機会も減ります。
  - リスク: 全instanceのRecheck入力が変わります。前後の対を見て、形だけの書き換えでも「解消」と甘く判定する方向へ動く可能性があります。¥0では検証できないため、次runで382件の自己矛盾率と見逃しを測る必要があります。
- **技術的見解(是正か、設計変更か)**:
  - 「`issue`が参照する元の文を入力に揃える」こと自体は、ユーザーが技術是正とした「Rewrite前の古い文章をCheckerへ渡していた問題」の自然な完結にあたり、不具合是正の延長と言えます。
  - 一方で、Recheckのプロンプトに新しい情報ブロックを足す点は、「Checker Prompt不変」という制約の解釈次第です。
  - 判定の基準や`issue`の文言そのものを書き換える(LLMで書き直す等)のは、Checkerの入力設計の変更にあたり、ユーザー判断事項です。
  - Fableは、N3′がどちらに当たるかを境界事例としてユーザーに確認するのが安全です。
- **先に取れる材料**: 次runで`recheck_prior_issues_resolved`の逐語が取れれば、resolved=falseの理由文から原因を直接確認できます。その確認をN3′より先に行うことを推奨します。

## 論点4: L6をONのまま維持するか
ONのまま維持し、観測を続けることを推奨します。外すべきではありません。
- L6が対象とする失敗の実例(rep24でHuman Review 2件、どちらもcycle 2)をreplayで救済しています。
- 合成ストレス712件で誤復元0件、決定論で追加callも0です。
- rep26・27で救済例が0件だったのは、`violation_span_unverified`が出なかったため(発生率は0.02〜0.05件/run程度)と考えられ、無価値の証拠にはなりません。
- 外すと、`violation_span_unverified`の経路(rep24で2/38)が再び開きます。
- 有害だった相互作用は、是正(a)で除去済みです。

## 論点5: 残STAGE4経路の棚卸し
`stage4_reason`の代入箇所はGrepで全列挙して照合しました(7738・7791・7834・7951・7970・8055・8276・8309行)。棚卸し表と一致しており、漏れはありません。その上で、次の補足があります。
- **(a) 表にない停止経路**: 例外終了(API失敗、連続エラー、予算上限=budget_state)は`stage4_reason`を持ちません。KPI上の「Human Review相当」に数えるのかどうかを定義しておく必要があります。rep27は0件です。
- **(b) N1′導入後の移動先**: N1′を入れると、`unconfirmed_after_reverify`の分が`same_claim_fact_id_reblocked`、`cycle_limit_exhausted(_after_recheck)`へ移る可能性があります。「KPI構成で0件」という評価は、N1′導入後に測り直してください。
- **(c) `ladder_exhausted`の他の原因**: 旧構成の10件(rep16・rep18・rep20・iter8)について、「同じcycleで同じ文を指すclaimが重複していた」型かどうかを、既存ログから¥0で分類できます。L6以外の原因が残っているかを、run前に安く確認できます。
- **`cycle_limit_exhausted`**: 上限は触れないでよいです。ただし(b)のとおり、発生件数は監視対象にしてください。
- **仕分けの妥当性**: 次の仕分けは妥当です。
  - 技術是正で潰せるもの: `unconfirmed_after_reverify`(N1′)、`ladder_exhausted`(是正(a)+分類)
  - 継続観察: `violation_span_unverified`(L6)
  - 旧構成でのみ発生: その他

## 論点6: より単純な方法・既存Evidenceの再利用
- **再確認callの廃止**: 推奨しません。廃止して自己矛盾を直接Stage 2へ流すと、neg3の82%で毎回cycle 2に入り、不要Rewriteが増えます。再確認は、安い判定役として機能しています。
- **最小の組み合わせ**: N1′(追加call 0)を必須とし、N3′は測定付きの任意とします。N3′が効けば、再確認はほとんど呼ばれなくなります。
- **N2**: 不採用でよいです。
- **既存Evidenceの再利用**: 次runは、記録専用で追加した逐語ログを取ることを主目的にすれば、追加費用はほぼ0です。

## 論点7: Production配線時の整合
- Production(`er012`、410〜430行)には、Stage 2・cycle・ladderがそもそもありません(再生成→再検査→不成立ならSTOP)。N1′だけを移植しても成立しません。
- 推奨する方向: 再検査の結果を正規化する純関数を1つ設け、TrialとProductionで共有します。
  - 入力: `(recheck, confirm)`
  - 出力: `PASS` / `NEXT_CYCLE(MAJOR ∪ 未解消prior)` / `STOP`
- Productionが自己回復flowを持たない間は、`NEXT_CYCLE`を`STOP`へ写像します(現行のSTOP相当で、安全側)。
- 自己回復flow全体をProductionへ配線するときに、この関数をそのまま使えば、TrialとProductionで仕様が分岐しません。
- N3′を入れる場合は、Production共通の`build_prior_issues_instruction`(`er003` 678行)をどう扱うかを、この配線と同時に決めてください。
- 採用可否は宣言しません(人間ユーザーのみが決めます)。

## 十分に答えられなかった論点
- 再確認deviationsの中身と、Recheckでresolved=falseになった理由文は未保存です。このため、N1′で不要Rewriteがどれだけ増えるか、N3′がどれだけ効くかは推定にとどまります。
- 通常経路の潜在ギャップ(DEVIATIONかつ`all_prior=False`で、未解消の元指摘がdeviationsに無い場合に脱落する)の実際の発生件数は、未集計です。次runの`recheck_prior_issues_resolved`から¥0で集計できます。

## 追加で読んだファイルと概算文字数
- `docs\pm\design_open233_kpi_recovery_02.md` §12(302〜407行): 約1.6万字
- `er052_open233_self_recovery_flow_runner_01.py`: 8180〜8319行、7690〜7839行、8140〜8164行、7466〜7495行(約1.6万字)。加えて`stage4_reason`と`prior_issues`のGrep
- `docs\pm\design_open233_span_sentence_restore_01.md`: Grepで約30行(約3千字)
- 合計: packetを含め約4.8万字
