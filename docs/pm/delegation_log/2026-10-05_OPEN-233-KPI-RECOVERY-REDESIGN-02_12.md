## 管理ID

`OPEN-233-KPI-RECOVERY-REDESIGN-02`(委任_12)。親: `OPEN-233-SELF-RECOVERY-TRIAL-01`。並行タスクなし。

## 性質/到達上限Status/禁止事項

- 性質: 委任_11実装(I-2許可リスト/I-1最小/B′/A2/D+H-1/G/T/BLOCKING固定、commit a9958828)に対するFable照合で見つかった是正1件(¥0)→限定確認rep30a(有料≈¥5)→Step 6再確認rep30(有料≈¥28、1回)→KPI判定。
- KPI(変更・緩和禁止): Primary=USER_DECISION_REQUIRED/Human Review 0件、Safety=重大Fact見逃し0件、Cost=平均追加+¥2/記事以内、Cap=worst追加+¥3/記事以内(基準は従来どおりrep24比。iter7比も併記)。追加事前基準(Opus#14、Fable採用): 許可リスト外STAGE4 0件/G(判定だけのcycle)経路の降格は全件S1通過/書き換えられていないBLOCKINGによるPASS 0件。参考指標(採否基準ではなく記録): NORMAL群不要Rewriteがrep29の5/14から増えたか(兄弟列挙スイッチの不採用候補判定に使う)。
- 到達上限Status: 4 KPI+追加3基準を同時達成→`VALIDATED`(Trial評価)。未達→`IN_PROGRESS`のまま原因分析をFableへ。`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`へ進まない。既存の個別APPROVED項目のStatusも変更しない。
- **Fable照合結果(委任_11に対する是正・判断、SSOTへ逐語記録)**:
  1. **是正(必須、¥0)**: `degenerate`(Rewrite結果が空・同一等の退化)を`blocking_structural_after_ladder`へ写像しているのは、許可リスト外の理由を許可名で包む「名前の洗い替え」であり、I-2の趣旨に反する。是正: degenerateは「そのlevelの試行失敗」として扱い、同cycle内で上位levelへ昇段→ladder枯渇ならT(構造要素以外)→T不可(構造要素)の場合のみ`blocking_structural_after_ladder`。すなわち`blocking_structural_after_ladder`は「構造要素であること(`structural_element_reasons`で判定)∧ladder④まで実試行済み」を関数内で検証したときだけ返す。fixture追加(非構造degenerate→昇段→T、構造degenerate→STAGE4)。
  2. **rep28の構造要素3件が反実仮想replayでHuman Reviewのまま残る件**: replayはrep28記録時のLLM出力(構造要素書き換えfallback実装前)に基づくためで、同3 instanceはrep29実行時には構造要素書き換えで解消済み(委任_09報告: 「rep28の3件(ladder_exhausted系)は消えた」)。設計上の未解決ではなく、`blocking_structural_after_ladder`は正当な残余経路(H-3③)。rep30で実測する。
  3. **`issue_focus_absent_recheck_only`(L6既存承認経路)**: Stage 2 BLOCKINGの引用語句が現行本文全体に存在しない(Checkerの引用が記事に無い)場合にRecheckのみで解消する経路。H-1(位置特定済みBLOCKINGを書き換えずにPASS)とは「書き換える対象文が本文に存在しない」点で異なり、materiality降格ではなく引用の非存在の決定論確認+全文Recheck。**本委任では変更しない**(Opus#9/#12で承認済み)。ただし(a)非存在判定が「該当文」ではなく「現行本文全体」に対して行われていることをコードで確認し(違えば本文全体へ是正)、(b)rep30で発火件数・結果を記録、(c)Closeoutのユーザー確認事項へ追加。
  4. **スイッチ**: `STAGE2_VERDICT_REUSE_NONBLOCKING`=ON、`STAGE2_SIBLING_LOCATIONS_CYCLE1`=ON(事前基準どおり: 再利用replay抑制8・ラベル重大0・flip0、第二段階①=20%>0)。rep30で兄弟列挙によりNORMAL群不要Rewriteがrep29(5/14)より増えた場合は「不採用候補」として記録(rep30の採否判定自体は変えない)。
  5. 委任_11の実装判断(T後のBLOCKINGは追わず`post_T_new_blocking`、carry未再取得は次cycleで`..._unlocatable_after_cap`)は採用。
- 禁止事項: Production正式path(`er003*`/`er009*`/`er010*`/`er012*`/`er019*`)変更禁止、編集は`er052_open233_*`と文書のみ。Checker本体Prompt・Schema・判定規則・V7b・同義語表不変。KPI緩和・Human Review温存を結論にしない。新retry loop・Human Reviewへ倒す新経路を作らない。母数・n固定(29 instance・38 run)、再実行・n増しなし。採否基準を結果を見て変えない。`git add -A`/`stash`/`amend`禁止。既存のM表示差分・untrackedに触れない。`ACTIVE_TASK.md`/`RESULT_PACKET.md`はaddしない。`PM_GOVERNANCE.md`・`CURRENT_SPEC.md`・`DECISION_LOG.md`は編集しない。
- 費用上限: ¥38(Guardrail。内訳の目安: rep30a≈¥5、rep30≈¥28〜30)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。Phase累計¥695.39、上限¥900、残¥204.61。有料実行前に費用概算を出し実測と並記。rep30は`--budget-jpy 30`で起動(委任_09で¥24見積→¥24.67実測の経緯を踏まえる)。Guardrail TrialAbortで中断した場合は`skip existing`で1回だけ再開(残run数・残費用を記録)。
- 即時STOP(有料run中): JA変更/例外2 instance以上/1 instance-run費用>¥7。重大見逃し・STAGE4・許可リスト外STAGE4は止めずに完走し、件数と原因を特定して報告。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0: 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する。
T-2: TTSを伴う委任は`TTS_EXECUTION_MODE=STANDARD`を明示(本委任はTTSを伴わない)。
T-3: 費用上限[Cap]はGuardrailであり、Cap到達=自動STOPではない。

T-0補足: 保存先 `C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-05_OPEN-233-KPI-RECOVERY-REDESIGN-02_12.md`。委任文は全文そのまま保存。一時ファイルはリポジトリ外。スクリプトはWrite/Editで作る。全体回帰は`PYTHONIOENCODING`なしのシェルで実行。

## ユーザー指示(原文、該当部分)

Step 6
Safety-critical群＋既存29件を再確認。
ここで最低限、
- Human Review 0件
- 重大見逃し 0件
を同じ構成で同時に確認すること。
Step 7
まだ未達なら、自律的に原因分析→改善ループをもう一度回す。
合理的な改善余地が残っている限り、ユーザーへKPI緩和を提案しない。

## 作業1: 是正(¥0)

- Fable照合1(degenerate)をrunnerに実装、fixture・単体テスト追加。Fable照合3(a)をコードで確認(違えば是正)。設計書§18-Bに「Fable照合(委任_12)」小節として照合結果1〜5を逐語記録。
- テスト: runner単体・er052回帰・全体回帰(基準11件以外新規なし)。`git grep -n "er052_open233" -- "er003*.py" "er009*.py" "er010*.py" "er012*.py" "er019*.py"` 0件。
- 反実仮想replay(`replay_counterfactual_rep27_29_01.py`)を再実行し、degenerate是正後の終端を更新(許可リスト外STAGE4 0件維持を確認)。
- 1回目commit/push。

## 作業2: 限定確認 rep30a(有料≈¥5)

`er052_open233_self_recovery_flow_runner_01_rep30a_limited_01.py`(`meta_run03_advanced` s1/s2、`safety_A4` s1、`--budget-jpy 7`)。確認: STAGE4件数・理由(許可リスト内外)/重大見逃し/各新経路の発火逐語(B′昇段level列、A2却下、D引用分割の確定、carry list、判定だけのcycle[S1通過]、T、BLOCKING固定、再利用、兄弟列挙)/Rewrite案がLedgerに沿うか(目視相当)/費用(instance別)/JA 0。**STAGE4が1件でも出た場合、または許可リスト外STAGE4・未書換BLOCKING PASS・S1非通過降格が1件でも出た場合はrep30へ進まず**、原因を特定しFableへ報告(是正は次委任)。

## 作業3: Step 6再確認 rep30(有料≈¥28〜30、1回)

`er052_open233_self_recovery_flow_runner_01_rep30_full_01.py --budget-jpy 30`→`_rep30_agg_01.py`。29 instance・38 run、KPI構成+新スイッチ(委任_11既定: ON 7+再利用ON+兄弟列挙ON)。
- 集計(rep29・rep28・rep24・iter7比): Human Review(統一定義)件数・理由(許可リスト内外別)/重大見逃し(旧・新定義・`text_pattern`版、`residual_at_pass`全件仮ラベル)/Safety-critical 6件の検出・経路/各機構の発火(Tier 0・S1・L6[focus_absent含む]・N1′・actor_guard[basis別]・構造要素・件数一致・B′・A2・D・carry・G・T・BLOCKING固定・再利用・兄弟列挙)/G経路降格のS1通過率/未書換BLOCKING PASS件数/Recheck自己矛盾率・再確認call数/不要Rewrite(NORMAL群、rep29 5/14比)/過剰Major/cycle分布(判定だけのcycle含む)/JA 0/費用(合計・平均追加/記事[rep24比・iter7比]・worst[instance名]・Cap超)/モデル・構成。
- **KPI判定**: Human Review 0∧重大見逃し0∧平均追加≤+¥2(rep24比)∧worst追加≤+¥3(rep24比)∧許可リスト外STAGE4 0∧G降格S1通過100%∧未書換BLOCKING PASS 0 → `VALIDATED`。未達→原因分析(どの判定が、どの入力で、なぜ)をREPORTに書きFableへ。

## 作業4: SSOT

- `OPEN_ITEMS.md` KPI-RECOVERY-02行Status: 「委任_12: degenerate是正、rep30a【STAGE4 a/許可外 b】、rep30【Human Review d(許可外 e)・見逃しf・不要Rewrite g/14・平均追加+¥h・worst+¥i(instance)・G S1通過j%・未書換PASS k】→【VALIDATED/未達】。次: 【Closeout(委任_13)/再ループ】」。`docs/pm/REPORT_LEDGER.md`1行、REPORT §62、`docs/pm/ACTIVE_TASK.md`(addしない)。

## 事前指定Read一覧

- runner: Grep `stage4_allowlist_decision|degenerate|blocking_structural_after_ladder|structural_element_reasons|issue_focus_absent|vs_l6_focus_absent|vs_l6_focus_guard|LAST_RESORT_DELETE` → 該当範囲(全文Read禁止)。
- 設計書§18/§18-B(追記位置)。rep30a/rep30/aggスクリプト(作成済み、引数名確認)。`replay_counterfactual_rep27_29_01.py`。
- rep30a/rep30出力(実行後)。

## 事前指定Grep一覧+追記位置・更新位置の手順

- SSOT: Grep `KPI-RECOVERY-REDESIGN-02` in `OPEN_ITEMS.md`(該当1行のStatus欄のみ更新)、`docs/pm/REPORT_LEDGER.md`(末尾1行追加)、`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`(§61の直後に§62追加)。
- 設計書: Grep `§18-B` → 小節末尾に「Fable照合(委任_12)」追記。
- `git grep -n "er052_open233" -- "er003*.py" "er009*.py" "er010*.py" "er012*.py" "er019*.py"`(0件確認)。

## 実行コマンド全文

作業ディレクトリ `C:\Users\tensh\eigo-radio`。
T-0: C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-05_OPEN-233-KPI-RECOVERY-REDESIGN-02_12.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-05_OPEN-233-KPI-RECOVERY-REDESIGN-02_12.md_check.json
テスト: C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -m unittest er052_open233_self_recovery_flow_runner_01_test_01
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\run_project_regression.py --pattern "er052*_test_*.py"
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\run_project_regression.py
replay: C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_output\open233_kpi_recovery_02_offline_01\replay_counterfactual_rep27_29_01.py
rep30a(有料): C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_open233_self_recovery_flow_runner_01_rep30a_limited_01.py --stage main --budget-jpy 7 → `--stage agg`
rep30(有料、1回): C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_open233_self_recovery_flow_runner_01_rep30_full_01.py --stage main --budget-jpy 30 → C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_open233_self_recovery_flow_runner_01_rep30_agg_01.py
(引数名は実装に合わせてよい。)
順序: T-0 → 作業1 → 1回目commit/push → 作業2 → [STAGE4 0∧許可外0∧未書換PASS 0∧S1非通過0なら]作業3 → 作業4 → 2回目commit/push → 報告。

## Git(明示add対象・コミットメッセージ)

- 1回目: runner、テスト、設計書§18-B、replay出力、委任ログ+check.json。メッセージ: `OPEN-233-KPI-RECOVERY-REDESIGN-02: degenerateを許可名へ写像せずladder昇段→Tへ是正(I-2整合)、focus_absent経路の本文全体判定確認、反実仮想replay更新(委任_12、¥0)`
- 2回目: rep30a・rep30出力、SSOT。メッセージ: `OPEN-233-KPI-RECOVERY-REDESIGN-02: 限定確認rep30a【STAGE4 a】・Step 6再確認rep30 29件+Safety-critical【Human Review d・見逃しf・不要Rewrite g/14・平均追加+¥h・worst+¥i】→【VALIDATED/未達】(委任_12)`

## 報告(RESULT_PACKET項目)

(1)結論10行以内(KPI 4つ+追加3基準の実測値、VALIDATED/未達)、(2)是正・テスト・replay更新、(3)rep30a結果(新経路発火の逐語)、(4)rep30結果表(rep29/28/24/iter7比、Safety-critical 6件、機構発火、S1通過率、未書換PASS、不要Rewrite、自己矛盾率、費用、モデル・構成)、`residual_at_pass`全件仮ラベル、focus_absent発火件数、(5)未達なら原因分析(判定・入力・理由)と再ループ案、(6)費用(概算/実測/Phase累計)、(7)SSOT、(8)T-0・commit・push・raw URL、一覧外Read、確認/推測の区別、(9)Fableへの論点(Closeoutへ進めるか、ユーザー確認事項の一覧)。
