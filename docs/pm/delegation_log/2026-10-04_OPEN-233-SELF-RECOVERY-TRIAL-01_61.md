## 管理ID

`OPEN-233-SELF-RECOVERY-TRIAL-01`(委任_61)。並行タスクなし。

## 性質/到達上限Status/禁止事項

- 性質: ユーザー決定(2026-10-04、5回目: 選択肢3=「時期だけ解放対象」)の逐語記録、委任_60で実装した追加確認(`FLOOR_VERIFY_MODE`)の対象を`changed_time`のみに縮小する修正、時期の重大ケースでの単体安全確認(有料¥5〜10)、V7b再較正(有料¥8〜10)、SSOT反映。**少数flow確認・29件横断は本委任では行わない**(単体確認・再較正のPASSをFableが照合してから次の委任_62で実施)。次Trial(10本)は開始しない。
- 到達上限Status: 「時期だけ解放」=ユーザー正式判断済み(`APPROVED_FOR_PRODUCTION`として追跡)。自己修復機構本体がProduction未接続のため**`PRODUCTION_WIRED`ではない**(明確に区別して記録)。
- 禁止事項:
  - Production正式path(`er003*`〜`er019*`)の変更禁止。編集は`er052_open233_*`のみ。
  - **比較・方向(`changed_comparison`)・主体・数値・否定は従来どおり決定論でBLOCKING維持。** これらが1つでもtrueなら追加確認の対象外。追加確認で解放できるのは、trueのfloorフラグが`changed_time`だけの指摘に限る。
  - 自動解放(文字一致・台帳中の時期語の有無だけを根拠にした解放)を実装しない。解放は「追加確認2回とも非BLOCKING、かつ引用が逐語」のときだけ(委任_60の解放条件・BLOCKING固定条件・`dev`不変・2-of-2除外・cycleごと再評価は維持)。
  - 既存より厳しくする変更を追加しない。新しい仕様候補を勝手に追加しない。新しいProduct判断が必要になったら、追加Trialや仕様拡張へ進まず`USER_DECISION_REQUIRED`としてSTOPし報告。
  - スイッチは既定OFF維持。`comparison_time`モードはCLI・定数の選択肢から外す(残す場合もCLIから選べず、テストで「選べない」ことを固定する)。
  - 単体確認で**重大期待ケースを1件でも軽微以下へ解放したら、その時点で測定を止めて報告**(修正を重ねない)。
  - `git add -A`/`stash`/`amend`禁止。既存のM表示差分・untrackedに触れない。`ACTIVE_TASK.md`/`RESULT_PACKET.md`はaddしない。
- 費用上限: 上限¥25(Guardrail。内訳の目安: 単体安全確認¥5〜10、V7b再較正¥8〜10[いずれもユーザー承認済み])。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。Phase累計¥538.829、上限¥900。
- Opus独立技術レビューGate(PM_GOVERNANCE 11-3): 本件はOpus#8でレビュー済みの構造(F5)をユーザー判断で対象縮小するもので、新構造ではない。レビュー済みの形と異なる変更が必要になったら実装せず報告。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSを伴わない。)
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`、ユーザー正式決定、費用上限[Cap]を伴う全委任で常時有効): 費用上限[Cap]は「暴走防止のためのGuardrail」であり、Cap到達=自動STOPではない。禁止事項/性質欄の費用上限記載は上記の定型文に従う。

T-0の補足: 保存先 `C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-04_OPEN-233-SELF-RECOVERY-TRIAL-01_61.md`。**委任文は全文そのまま保存(要旨化・要約保存は不可。委任_60修正1では要約保存でFAILになった)。** 一時ファイルはリポジトリ外(`%TEMP%`配下)。

## ユーザー指示(原文)

次の全文を`DECISION_LOG.md`末尾へ一字一句そのまま引用する(作業1)。

````
選択肢3を正式採用します。
AIの追加確認で軽微へ戻せる対象は、「時期」だけに縮小してください。
つまり、
- 時期 → AI追加確認の対象
- 比較・方向 → 従来どおり機械判定で重大維持
- 主体 → 従来どおり機械判定で重大維持
- 数値 → 従来どおり機械判定で重大維持
- 否定 → 従来どおり機械判定で重大維持
とします。
prices began to fall 型の過剰Majorは、現時点では受容します。
今回の安全確認で危険な解放が出た「方向反転」は、追加確認対象から外してください。
そのうえで、次の順で進めてください。
1. 「時期だけ解放対象」に実装を修正。
2. 時期の重大ケースで単体安全確認を実施。
   - 重大期待ケースを1件でも軽微以下へ解放したらSTOP。
   - 追加費用目安 ¥5〜10。
3. V7b再較正を実施。
   - 新しい重大/軽微基準と今回の対象縮小後の挙動が整合することを確認。
   - 費用目安 ¥8〜10。
4. 単体確認PASS後のみ、少数の実flow確認を実施。
   - 説明文混入対策
   - 句読点差対策
   - 英語だけ修正
   - 時期だけの追加確認
   - retry / recheck整合
     を確認。
   - 費用目安 ¥12〜30。
5. 少数flowが問題なければ、29件横断を1回だけ実施。
   - 真の重大見逃し 0
   - 重大ケースの誤解放 0
   - 過剰Majorの状況
   - 不要Rewrite
   - Human Review増加有無
     を確認。
   - 費用目安 ¥35〜70。
6. そこでSTOPして報告。
   - 5記事 × Standard/Advanced = 10本の次Trialはまだ開始しない。
   - 次TrialはユーザーGO待ち。
今回の「時期だけ解放」は、ユーザー正式判断済みなので APPROVED_FOR_PRODUCTION として追跡してください。
ただし、Production正式pathへの実装・runtime evidence・retry/fallback整合・必要test・CURRENT_SPEC / DECISION_LOG / OPEN_ITEMS / Git反映まで完了するまでは PRODUCTION_WIRED にしないでください。
また、既に承認済みの以下もProduction接続時に漏れなく一体で追跡してください。
- 新しい重大 / 軽微 / 問題なし基準
- 説明文混入の後段分離
- 句読点差対策
- 英語だけ修正する方針
今回の作業中に新しいProduct判断が必要になった場合は、追加Trialや仕様拡張へ進まず USER_DECISION_REQUIRED でSTOPしてください。
````

## 作業1: ユーザー決定の記録

`DECISION_LOG.md`末尾に「OPEN-233-SELF-RECOVERY-TRIAL-01(2026-10-04、ユーザー決定[5回目]: 選択肢3=追加確認による解放対象を「時期」だけに縮小[比較・方向・主体・数値・否定は決定論でBLOCKING維持、`prices began to fall`型の過剰Majorは受容]/手順1〜6/`APPROVED_FOR_PRODUCTION`として追跡・`PRODUCTION_WIRED`は配線完了まで不可/承認済み4項目の一体追跡/新Product判断はUSER_DECISION_REQUIRED)」を追記し、原文を全文逐語で引用。続けて「Fableの受け止めと分担」(委任_61=記録・時期のみへ縮小・単体確認・再較正・SSOT、委任_62=少数flow確認→29件横断1回、委任_63=Closeout確認・STOP報告。ユーザーの手順4・5はFableが単体確認・再較正のPASSを照合してから着手)。`docs/pm/ACTIVE_TASK.md` Status=「IN_PROGRESS(選択肢3=時期のみの実装・単体確認・再較正中、少数flow・29件横断・次Trialは未着手)」(addしない)。

## 作業2: 「時期だけ解放対象」への実装修正(runner)

- `FLOOR_VERIFY_MODE`の選択肢を`"off"`(既定)/`"time_only"`に変更。`"comparison_time"`はCLI(`--floor-verify-mode`)の`choices`と定数一覧から外し、指定されたら`ValueError`または起動時エラー(テストで固定)。
- 対象判定: Stage 2のLLM判定(`llm_materiality`)が非BLOCKINGで、`apply_floor`だけがBLOCKINGにした指摘のうち、**trueのfloorフラグが`changed_time`のみ**のもの。`changed_comparison`/`changed_actor`/`changed_number`/`changed_negation`のいずれかがtrueなら対象外(理由コード`out_of_scope_flag:<flag名>`を`floor_verify`に記録)。precheck floorも対象外。
- 比較用のCONFIRMED規則(`floor_verify_comparison_numbers`)は呼ばれなくなるが、関数は残してよい(未使用である旨をdocstringに記載)。時期のCONFIRMED規則(`floor_verify_time_tokens`)は変更しない。
- 確認promptの軽微例: 委任_60のpromptに含めていたK19(`prices began to fall`)等の**比較・方向の例があれば外す**(時期の対象縮小に伴う整合。時期に関する例が必要な場合は、既存のcriteria doc・設計書に記載済みの正解ラベル付き例だけを使い、新しい例を作らない)。rubric本体(V7b)は変更しない。
- summary(`floor_verify_summarize`)に理由別件数として`out_of_scope_flag`を追加。
- その他の解放条件・BLOCKING固定条件・2-of-2除外・cycleごと再評価・`dev`不変は委任_60のまま。

## 作業3: 単体安全確認(有料¥5〜10)

`er052_open233_floor_verify_unit_check_01.py`を時期ケースへ更新(または`_02.py`として追加)。出力`er052_output/open233_floor_verify_unit_check_02/`(生応答、`results_01.json`、`cases_01.csv`)。既存の`_01`出力は削除しない。想定シナリオは委任_60と同じ「LLM=QUALITYなのにfloorがBLOCKINGへ昇格、trueフラグは`changed_time`のみ」。

- **重大期待ケース(解放したらSTOP)**。各ケースで、決定論CONFIRMEDが発火する版と、**発火しない版(確認callが実際に動く版)**の両方を用意する(CONFIRMEDが発火する版だけだと確認経路が未検証のまま合格してしまうため)。発火しない版は、月日・年・時刻・期間・翌日等の抽出トークンを含まない相対表現(例: "a few days later" / "by the weekend" / "before the announcement" / "later that month" / "soon after"←順序・前後関係の取り違え)で作る。
  - T1: 日付の取り違え(HF-003系、7/13 vs 7/14。CONFIRMED版 + 「the day before the announcement」のような前後関係反転版)
  - T2: K16型「継続中の出来事を一度消えて戻った」とする(HF-009/HF-003、"The fee plan left the stage, but the events driving oil prices…"型を時期の取り違えとして)
  - T3: 順序の反転(台帳で「Aの後にB」のものを「Bの後にA」にする。Safety12のうち時期フラグのfixtureがあればそれを使い、無ければHF系の合成)
  - T4: A5-0(時期・経過の創作、Safety-critical)
  - T5: 期間の付け替え(台帳の「数時間」を「数日」等。CONFIRMED版 + 「for a long time」のような非抽出版)
- **解放期待(参考値、0でも不合格ではない)**: B2「Trump’s proposed Hormuz fee vanished overnight.」(`changed_time`のみ、実run記録LLM=ACCEPTABLE)、他に設計書・criteria docに正解ラベル(軽微/問題なし)付きで記載されている時期系の過剰判定例があれば1〜2件(新しい例を作らない)。
- 回数: 重大期待はn=5(確認2回=10 call/ケース版)、解放期待はn=3。最初に1ケース×1回で単価(委任_60実測¥0.1219/call)を再確認し、全体が¥10を超える見込みならnを減らして報告(重大期待を優先)。
- 受入条件: **重大期待ケース(どの版でも)が1件でも解放(2回とも非BLOCKING、かつ引用逐語)されたら測定を止めて報告。**
- 集計: ケース版別の対象判定/CONFIRMED/確認結果の分布/解放数/BLOCKING固定理由/費用、引用の逐語一致。

## 作業4: V7b再較正(有料¥8〜10)

- 委任_55の`er052_open233_element_trial_safety_control_05.py`(引数名は実装に合わせる。rubric指定が無ければ`_06.py`として追加)をV7bで実行。較正セット(a)Safety-critical 5件 (b)Safety12 (c)Hormuz NG5 (d)例3件[例1=QUALITY、例2=ACCEPTABLE、K19=QUALITY] (e)K16・K20 (f)false BLOCK対照、n=2。出力`er052_output/open233_safety_control_04/`。
- 合格: (a)誤降格0、(b)0/18、(c)V6/V7と同じ、(d)期待どおり、(e)BLOCKING、(f)false BLOCK 0。外れたら修正を重ねず報告。
- 「対象縮小後の挙動との整合」: 再較正はStage 2 rubricの確認であり追加確認は含まれないので、作業3の結果と合わせて「時期以外のfloorはLLM判定に関係なくBLOCKING維持」「時期は2回確認で解放可能、重大は解放されない」が両立していることを`results`の集計に1節で明記。

## 作業5: テスト・回帰

- 新規・更新テスト: `comparison_time`が選べない/`changed_comparison`trueが対象外になる/`changed_time`のみが対象になる/CONFIRMED時期規則/2回確認の解放条件/失敗時BLOCKING固定/2-of-2除外/cycleごと再評価/OFFで無変更/legacy無影響/確認promptに比較・方向の例が含まれない。
- runner単体・er052回帰・全体回帰(基準11件以外に新規なし。`budget_state_c233an_42_rep22.json`等の書き換えは`git checkout`で戻す)。

## 作業6: SSOT

- `CURRENT_SPEC.md` OPEN-233節の「案1」記述を更新: 「追加確認による解放対象は時期(`changed_time`)のみ(2026-10-04ユーザー決定[5回目]、`APPROVED_FOR_PRODUCTION`)。比較・方向・主体・数値・否定は決定論でBLOCKING維持。`prices began to fall`型の過剰Majorは受容。委任_60の単体確認で方向反転S1が解放されたため対象から除外。自己修復機構本体がProduction未接続のため`PRODUCTION_WIRED`ではない」+単体確認・再較正の結果。
- `OPEN_ITEMS.md` OPEN-233行: Status「ユーザー決定[5回目]反映(2026-10-04、委任_61): 時期のみへ縮小実装(既定OFF)【単体確認PASS/STOP】、V7b再較正【結果】。少数flow・29件横断(1回)は次工程(委任_62)。次Trial禁止。Production未接続」(旧Statusは「旧Status参考(委任_60)」で残す)。次Action欄末尾に「(委任_61)…→委任_62=少数flow(¥12〜30)→29件横断1回(¥35〜70)→委任_63=Closeout確認・STOP報告」を追記(既存文は削除しない)。`OPEN-233-A1-PROD`行: 「案1の追加確認」を「時期のみの追加確認(選択肢3)」へ更新。
- `docs/pm/REPORT_LEDGER.md` OPEN-233行の備考、`OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md` §43、`docs/pm/design_open233_floor_alignment_01.md` §9「対象縮小(時期のみ)・単体確認・再較正(委任_61)」。

## 事前指定Read一覧

- `er052_open233_self_recovery_flow_runner_01.py`: Grep `FLOOR_VERIFY_MODE`、`floor_verify`、`run_floor_verify_call`、`floor_verify_time_tokens`、`floor_verify_comparison_numbers`、`floor_verify_summarize`、`--floor-verify-mode` → 該当範囲(委任_60で追加した範囲)。
- `er052_open233_floor_verify_unit_check_01.py`: 全文(自作の再利用)。`er052_output/open233_floor_verify_unit_check_01/cases_01.csv`。
- `er052_open233_element_trial_safety_control_05.py`: 引数・rubric指定部をGrep(`argparse`、`rubric`、`V7`)。
- `docs/pm/design_open233_floor_alignment_01.md`: §8(委任_60)のみ。`docs/pm/design_open233_self_recovery_flow_01.md`: Grep `A5-0`、`K16`、`B2`、`Safety12`、`changed_time` → 該当範囲(全文Read禁止)。
- Ledger: HF-003・HF-009・A5-0関連のfactブロック(Grep)。
- `CURRENT_SPEC.md`/`OPEN_ITEMS.md`/`DECISION_LOG.md`/`REPORT_LEDGER.md`/REPORT: Grep `委任_60` → 更新・追記位置だけ。

## 事前指定Grep一覧+追記位置

- 上記のとおり。`git grep -n "er052_open233" -- "er003*.py" "er009*.py" "er010*.py" "er012*.py" "er019*.py"`(0件を確認)。

## 実行コマンド全文

作業ディレクトリ `C:\Users\tensh\eigo-radio`。PowerShellなら先に `$env:PYTHONIOENCODING="utf-8"`。

T-0:
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-04_OPEN-233-SELF-RECOVERY-TRIAL-01_61.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-04_OPEN-233-SELF-RECOVERY-TRIAL-01_61.md_check.json

テスト・回帰:
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -m unittest er052_open233_self_recovery_flow_runner_01_test_01
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\run_project_regression.py --pattern "er052*_test_*.py"
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\run_project_regression.py

単体安全確認(有料):
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_open233_floor_verify_unit_check_01.py --suite time_only --stage probe --out-dir C:\Users\tensh\eigo-radio\er052_output\open233_floor_verify_unit_check_02
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_open233_floor_verify_unit_check_01.py --suite time_only --stage main --n-serious 5 --n-release 3 --budget-jpy 10 --out-dir C:\Users\tensh\eigo-radio\er052_output\open233_floor_verify_unit_check_02
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_open233_floor_verify_unit_check_01.py --suite time_only --stage agg --out-dir C:\Users\tensh\eigo-radio\er052_output\open233_floor_verify_unit_check_02
(引数名は実装に合わせてよい。`_02.py`として分ける場合も同じ出力先。)

再較正(有料):
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_open233_element_trial_safety_control_05.py --rubric v7b --out-dir C:\Users\tensh\eigo-radio\er052_output\open233_safety_control_04 --n 2 --budget-jpy 12
(引数名は実装に合わせる。無ければ`_06.py`として追加。)

順序: 作業1 → 2 → 5(テスト・回帰) → 1回目commit/push → 3(単体確認) → [STOPでなければ] 4(再較正) → 6(SSOT) → 2回目commit/push。単体確認でSTOP条件に当たったら、再較正へ進まず、その時点で2回目commit(結果とSSOT[STOPの記録、Status=`USER_DECISION_REQUIRED`])を行い報告。

## SSOT追記文

作業1・6のとおり。

## Git(明示add対象・コミットメッセージ)

- SSOT編集権: あり(`DECISION_LOG.md`末尾、`OPEN_ITEMS.md`の2行、`REPORT_LEDGER.md`の1行、`CURRENT_SPEC.md`のOPEN-233節)。`PM_GOVERNANCE.md`は編集しない。
- 1回目commit: `DECISION_LOG.md`、runner、runnerテスト、委任ログ`_61.md`・`_check.json`。メッセージ: `OPEN-233-SELF-RECOVERY-TRIAL-01: ユーザー決定(選択肢3=追加確認による解放対象を時期のみに縮小、比較・方向・主体・数値・否定は決定論維持)を逐語記録し検証用runnerを修正(既定OFF、Production未変更)(委任_61)`
- 2回目commit: 単体確認スクリプトと結果、再較正結果、`CURRENT_SPEC.md`、`OPEN_ITEMS.md`、`REPORT_LEDGER.md`、REPORT、設計doc。メッセージ: `OPEN-233-SELF-RECOVERY-TRIAL-01: 時期のみ追加確認の単体安全確認【PASS/STOP】とV7b再較正【結果】を実施、CURRENT_SPEC等へ反映(自己修復機構本体はProduction未接続)(委任_61)`
- 各commit前に`git status --porcelain`で確認。競合・新規テスト失敗・再較正不合格は自動解決せず報告。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET.md`と最終メッセージに: (1)結論10行以内、(2)実装修正の要点(対象判定の変更・`comparison_time`の無効化・prompt例の整理)、(3)単体確認のケース版別結果表(対象判定/CONFIRMED/確認2回の結果/解放/期待との一致/引用逐語)、費用、STOP該当有無、(4)再較正の集計と合否、整合の1節、(5)テスト件数・回帰、(6)SSOT更新箇所、(7)T-0・commit・push・raw URL、一覧外Read、確認できたことと推測の区別、(8)Fableへの論点(あれば)。
