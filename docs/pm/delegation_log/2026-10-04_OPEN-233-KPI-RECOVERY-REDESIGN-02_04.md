## 管理ID

`OPEN-233-KPI-RECOVERY-REDESIGN-02`(委任_04)。親: `OPEN-233-SELF-RECOVERY-TRIAL-01`。並行タスクなし。

## 性質/到達上限Status/禁止事項

- 性質: 委任_03のhold-out評価(目録由来の語彙拡張=流出閉鎖の上積み0・正当降格誤停止2.51%で採用条件不達/既知G_H 6語+`issue_actor`=閉鎖15/16[「and」版除き15/15]・誤停止0.19%)を受けたFable判断(下記)に基づき、Tier 0の有効語彙を確定し、Step 5(rep26、約¥5)→Step 6(rep27: Safety-critical群+既存29件、約¥22)を実行してKPI判定を行う。
- KPI(変更・緩和禁止): Primary=USER_DECISION_REQUIRED/Human Review 0件、Safety=重大Fact見逃し0件、Cost=平均追加+¥2/記事以内、Cap=+¥3/記事以内。QCD優先: 1重大見逃し0 2Human Review 0 3不要Rewriteを増やさない 4+¥2 5非決定性・追加call最小 6Production複雑化回避。
- 到達上限Status: Step 6のKPI判定まで。4つ同時達成→`VALIDATED`(Trial評価、Production採用ではない)。未達→`IN_PROGRESS`のままFableへ報告(ユーザーへKPI緩和を提案しない)。`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`へ進まない。既存の個別APPROVED項目のStatusも変更しない。
- Fable判断(SSOTへ逐語記録。変更しない):
  1. **Tier 0の有効語彙=既知G_H 6語+`issue_actor`**とする。根拠: 事前基準(誤停止≤2%かつ閉鎖15/15)を満たす唯一の構成(誤停止0.19%)。目録由来の拡張語彙は、同じ母集団で閉鎖の上積み0・誤停止+13件(`lead to`6[同一の否定文]、`as`4、`caused`3、`make`1)であり不採用。**語彙を結果を見て削る調整は行わない**(hold-outの趣旨)。拡張語彙の定数はコードに残し、`CAUSAL_FLOOR_VOCAB="known6"`(有効)/`"inventory"`(評価用、無効)で切替。
  2. **残存リスクの明示**: 6語は観測された流出クラス(`so`型)を閉じるが、未観測の接続語型の系統誤りには効かない。これはS1(偶発的な外れ)でも閉じないため、**Step 6の結果とともにユーザーへ正直に報告する**(KPI緩和の提案ではなく、Trial規模での達成状況と残存リスクの区別)。目録拡張が誤停止を生んだ事実は、「接続語の有無だけでは因果主張を判別できない(否定scope・多義語)」という知見として記録。
  3. Tier 1′ S1・Tier 2 hint・L6・prior_issues現行本文化・NORMAL群2-of-2 OFF・Q/U-2(1)は委任_03の実装のままKPI構成に含める。確認役・G_Lは無効。
  4. 「and」版(rep24 cycle 2 B3)=ACCEPTABLEのFable判断は登録済み(ユーザー未確認、否認されれば戻す)。
- 禁止事項:
  - Production正式path(`er003*`〜`er019*`)の変更禁止。編集は`er052_open233_*`のみ。Checker Prompt・Schema・判定方法・Stage 2本体rubric(V7b)は変更しない。
  - 語彙・閾値・採否基準を結果を見て変えない。Step 6の母数・nは固定(iteration 7/rep24と同じ29 instance・38 run)。再実行・n増しをしない。
  - Human Reviewへ倒す新経路を作らない。Solを使わない。
  - `git add -A`/`stash`/`amend`禁止。既存のM表示差分・untrackedに触れない。`ACTIVE_TASK.md`/`RESULT_PACKET.md`はaddしない。`PM_GOVERNANCE.md`は編集しない。
- 費用上限: 上限¥35(Guardrail。内訳の目安: rep26≈¥5[是正後の再実行1回を含めても≈¥10]、rep27≈¥22)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。Phase累計¥617.19、上限¥900、残¥282.81。有料実行前に費用概算を出し実測と並記。
- 即時STOP(有料run中): JA変更/例外2 instance以上/1 instance-run費用>¥7。重大見逃し・STAGE4は止めずに完走し、件数と原因(claim・経路・Tier発火・Rewrite失敗理由)を特定して報告。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0: 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する)。
T-2: TTSを伴う委任は`TTS_EXECUTION_MODE=STANDARD`を明示する。(本委任はTTSを伴わない。)
T-3: 費用上限[Cap]は暴走防止のGuardrailであり、Cap到達=自動STOPではない。

T-0の補足: 保存先 `C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-04_OPEN-233-KPI-RECOVERY-REDESIGN-02_04.md`。委任文は全文そのまま保存。一時ファイルはリポジトリ外(`%TEMP%`配下)。スクリプトはWrite/Editツールで作る。全体回帰は`PYTHONIOENCODING`なしのシェルで実行。10分制限で中断した場合は`skip existing`で1回だけ再開し、中断の事実を記録。

## ユーザー指示(原文、該当部分)

Step 5
B3/A2A3等の既知caseで限定確認。
Step 6
Safety-critical群＋既存29件を再確認。
ここで最低限、
- Human Review 0件
- 重大見逃し 0件
を同じ構成で同時に確認すること。
Step 7
まだ未達なら、自律的に原因分析→改善ループをもう一度回す。

## 作業1: Tier 0語彙の確定と記録(¥0)

- runner: `CAUSAL_FLOOR_VOCAB`(`"known6"`既定・有効/`"inventory"`評価用)を追加し、`causal_floor_guard`が`known6`のときG_H 6語+既存ヘッジ語で判定。`KPI_TRIAL_SWITCHES`に`CAUSAL_FLOOR: True`+`CAUSAL_FLOOR_VOCAB: "known6"`。`replay_guards_04`の結果(known6=誤停止0.19%・閉鎖15/16)を`known6`選択の根拠としてコメントに記載。テスト: known6/inventoryの切替・KPI構成の内容。
- 設計書`docs/pm/design_open233_kpi_recovery_02.md` §11「Tier 0語彙の確定(Fable判断、委任_04)」に上記判断1〜4を逐語で記録(残存リスクの明示を含む)。

## 作業2: Step 5 rep26 既知case限定確認(有料≈¥5)

`er052_open233_self_recovery_flow_runner_01_rep26_known_01.py`を`KPI_TRIAL_SWITCHES`(因果floor known6+issue_actor/S1/hint/L6/prior_issues現行本文/NORMAL群2-of-2 OFF/P-strict-closed+Q/U-2(1)/VS_MATCH_EXT/english_only/V7b/time_only floor_verify)へ更新。instance=`bgroup_B3`、`safety_A2A3`、`neg5_*`(B3同一文)、`neg3_hormuz_prodrunner_b1b`、n=2。出力`er052_output/open233_self_recovery_flow_runner_01_rep26/`。
- 確認: STAGE4 0/重大見逃し0(旧・新定義、`residual_at_pass`全件仮ラベル)/L6実flow復元(A2A3のspan不完全)/B3のcycle 2再指摘がprior_issues現行本文化で消えるか/Tier 0・S1の発火と結果(一致/割れ)/解除不可claimのRewrite解消率・cycle数/不要Rewrite(neg3・neg5)/費用(rep24・rep25同instance比)/JA 0。
- 判定: STAGE4 0∧見逃し0 → Step 6へ。1件でもあれば原因特定し、本委任内で技術是正可能(実装バグ・hint不足・照合漏れ)なら是正→同instanceだけ再実行(1回のみ)。設計変更が必要ならStep 6へ進まずFableへ報告。

## 作業3: Step 6 rep27 Safety-critical群+既存29件(有料≈¥22、1回)

`er052_open233_self_recovery_flow_runner_01_rep27_full_01.py`(rep24複製、`KPI_TRIAL_SWITCHES`)。29 instance・38 run(iteration 7/rep24と同一)。出力`er052_output/open233_self_recovery_flow_runner_01_rep27/`。
- 集計(rep24・iteration 7比): Human Review(STAGE4)件数・理由/重大見逃し(旧定義・新定義[自動導出]、`residual_at_pass`全件仮ラベル)/Safety-critical 6件(B3・B4-a・A2A3-0・A4-0・A5-0・neg5)の検出・経路(Stage 1 fresh/reuse/代替投入を明記)/Tier 0発火(理由別)・S1対象・一致・割れ・失敗/不要Rewrite(既存定義+全runのRewrite件数、rep24 24件/19 run比)/過剰Major(Stage 2 BLOCKING件数、floor単独)/L6・P・Q/U-2(1)発火と誤範囲/prior_issues現行本文化の発火/JA 0/費用(合計・1 run平均・rep24比の平均追加/記事・worst・Cap+¥3超のrunの有無)/モデル・構成(モデルID・rubric版・スイッチ全部)。
- KPI判定: Human Review 0∧重大見逃し0(新定義含む)∧平均追加≤+¥2/記事(基準=rep24同構成なし比、またはiteration 7比。両方併記)∧worst追加≤+¥3 → `VALIDATED`。1つでも未達→`IN_PROGRESS`のまま、原因分析をREPORTに書きFableへ。

## 作業4: SSOT

- `OPEN_ITEMS.md` `OPEN-233-KPI-RECOVERY-REDESIGN-02`行Status: 「委任_04: Tier 0=known6+issue_actor確定(拡張語彙は不採用、残存リスク明示)、rep26【STAGE4 a・見逃しb・¥c】、Step 6 rep27【STAGE4 d・見逃しe(旧/新)・不要Rewrite f・平均追加+¥g・worst+¥h】→【VALIDATED/未達】。次: 【Closeout(委任_05)/再ループ】」。Step進捗欄。`docs/pm/REPORT_LEDGER.md`。REPORT §54。`docs/pm/ACTIVE_TASK.md`(addしない)。`CURRENT_SPEC.md`・`DECISION_LOG.md`は編集しない(Closeoutで転記)。

## 事前指定Read一覧

- runner: Grep `causal_floor_guard|CAUSAL_CONNECTIVES_EN|HEDGE_MARKERS_EN|G_H|KPI_TRIAL_SWITCHES|apply_kpi_trial_switches|apply_stage2_second_opinion|stage2_release_guard|CORRECT_LABEL_OVERRIDES|safety_critical_dual_summary|tier0_summarize|s1_summarize` → 該当範囲(全文Read禁止)。
- `er052_output/open233_kpi_recovery_02_offline_01/replay_guards_04_causal_floor.json`(集計キー)。
- rep26スクリプト(委任_02作成)、rep24スクリプト・`rep24_agg_01.py`(複製元)、rep25スクリプト(KPI構成の渡し方)。
- `docs/pm/design_open233_kpi_recovery_02.md` §10(Fable再設計判断)。
- SSOT: Grep `KPI-RECOVERY-REDESIGN-02` → 更新位置。

## 事前指定Grep一覧+追記位置

- 上記のとおり。`git grep -n "er052_open233" -- "er003*.py" "er009*.py" "er010*.py" "er012*.py" "er019*.py"`(0件確認)。

## 実行コマンド全文

作業ディレクトリ `C:\Users\tensh\eigo-radio`。

T-0:
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-04_OPEN-233-KPI-RECOVERY-REDESIGN-02_04.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-04_OPEN-233-KPI-RECOVERY-REDESIGN-02_04.md_check.json

テスト・回帰:
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -m unittest er052_open233_self_recovery_flow_runner_01_test_01
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\run_project_regression.py --pattern "er052*_test_*.py"
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\run_project_regression.py

rep26(有料):
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_open233_self_recovery_flow_runner_01_rep26_known_01.py --stage main --n 2 --budget-jpy 8
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_open233_self_recovery_flow_runner_01_rep26_known_01.py --stage agg

rep27(有料、1回):
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_open233_self_recovery_flow_runner_01_rep27_full_01.py --stage main --budget-jpy 26
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_open233_self_recovery_flow_runner_01_rep27_full_01.py --stage agg
(引数名は実装に合わせてよい。)

順序: T-0 → 作業1(テスト含む) → 1回目commit/push → 作業2 → [判定OKなら]作業3 → 作業4 → 2回目commit/push → 報告。

## Git(明示add対象・コミットメッセージ)

- SSOT編集権: `OPEN_ITEMS.md`の1行、`REPORT_LEDGER.md`の1行、REPORT。
- 1回目commit: runner、テスト、設計書§11、委任ログ。メッセージ: `OPEN-233-KPI-RECOVERY-REDESIGN-02: Tier 0の有効語彙を既知6語+issue_actorに確定(目録拡張は閉鎖上積み0・誤停止2.51%で不採用、残存リスク明示)、KPI構成を更新(委任_04)`
- 2回目commit: rep26/rep27スクリプトと出力、SSOT。メッセージ: `OPEN-233-KPI-RECOVERY-REDESIGN-02: Step 5 rep26【…】・Step 6 rep27 29件+Safety-critical再確認【STAGE4 d・見逃しe・不要Rewrite f・平均追加+¥g・worst+¥h】→【VALIDATED/未達】(委任_04)`

## 報告(RESULT_PACKET項目)

(1)結論10行以内(KPI 4つの実測値、VALIDATED/未達)、(2)Tier 0確定の実装・テスト、(3)rep26結果表(run別、是正・再実行の有無)、(4)rep27結果表(rep24・iter7比、Safety-critical 6件の検出・Stage 1経路、Tier発火、S1一致/割れ、不要Rewrite、過剰Major、費用・平均追加・worst、モデル・構成)、`residual_at_pass`全件仮ラベル、(5)未達なら原因分析と再ループ案、(6)費用(概算/実測/Phase累計)、(7)SSOT更新箇所、(8)T-0・commit・push・raw URL、一覧外Read、確認できたことと推測の区別、(9)Fableへの論点(Closeoutへ進めるか、残存リスクの記述案)。
