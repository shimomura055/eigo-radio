## 管理ID

OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01(委任_05b: 新仕様9/20 run E2E本実行[3プロセス並列]→merge→一次集計→commit。有料)。並行タスクなし。本委任がgit・`docs/pm/ACTIVE_TASK.md`・`docs/pm/RESULT_PACKET.md`の編集権を持つ(SSOT編集は本委任では最小限: OPEN_ITEMS本管理ID行への進捗1文のみ。REPORT/DECISION_LOGは集計・ラベル後の委任_07で更新)。

**作業方式(必須)**: ファイル書き出しは`Write`/`Edit`で小分け(1回40行以内)、Bash heredoc不使用。T-0の委任文保存はWriteを3分割して逐語保存。説明は最小限。**E2E実行中は、問題を見つけてもコード・prompt・設定を一切変更しない**(記録のみ)。

## 性質/到達上限Status/禁止事項

- 性質: Production候補経路(er052 runner、承認構成`OPEN233_APPROVED_FLOW_SWITCHES`)でのfresh E2E。KPI provenance=fresh・Production初回path含む=Yes。到達上限: 9 run完走+一次集計(ラベル無し)。**PRODUCTION_WIRED宣言禁止**(9/20時点)。
- ユーザー指示のSTOPルール(厳守): 品質問題・重大Fact見逃し・Human Review(STAGE4)・waste flag・Rewrite多発が起きても**止めない**。記録したまま同条件で9 runを完走する。止めてよいのは技術障害(API障害・実行不能・データ破損)のみ: script_02の規定どおり2回再試行後にfailed記録して次runへ。技術障害で3 run以上がfailedになった場合のみ、残runを実行せずFableへ報告(それ以外は完走)。
- 費用: 各プロセス`--budget-jpy 20`(合計¥60=Guardrail、ユーザー見積high¥50)、`--run-cap-jpy 20`(1 run¥20超は当該runをabort記録して次へ)。Fable/Sonnet判断で予算を拡大しない。プロセス累計超過は残runをskipped記録(その場合も報告で明示)。
- 禁止: runner・checker・reclassify module・テスト・promptの変更/旧E2E dir(`er052_output/open233_e2e_acceptance_01/`)への書込/残り11 runの開始/`git add -A`・`stash`・`amend`/`ACTIVE_TASK.md`・`RESULT_PACKET*.md`のadd。
- Opus独立技術レビューGate(PM_GOVERNANCE 11-3)該当判定: 非該当(承認構成での実行)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0(2026-09-13、全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ逐語で保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果をRESULT_PACKETへ1行記録する(FAILでも作業は継続)。
T-2(2026-09-25): TTSを伴う委任は`TTS_EXECUTION_MODE=STANDARD`を明示する。本委任はTTSなし(Stage 1〜出口のテキスト処理のみ)。
T-2追記(2026-09-25、PM_GOVERNANCE.md 7-5): TTS実行前4点確認。本委任はTTSなし。
T-3(2026-09-26、費用上限[Cap]を伴う全委任で常時有効): 上限¥60(Guardrail、プロセス別¥20×3)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する——**ただし本委任ではプロセス別Cap(script内)が自動で残runをskipするため、超過継続はしない(skipped記録→報告)**。暴走疑い時(想定外の大量API発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない)はSTOPし、原因・既使用額・想定追加額・残作業を報告する。ユーザー承認済みの1 run上限¥20・技術障害のみSTOPを優先し、独自に過度に厳しい停止条件を追加しない。

## ユーザー指示(原文、要点)

> 新仕様で20 runを最初からやり直す。今回はまず、新仕様 9/20 runまで実行 → 集計 → 報告で一旦区切る。残り11 runは、その9 run報告をユーザーが確認した後に進める。
> 9 run中のSTOPルール: 品質問題・重大Fact見逃し・Human Reviewが発生しても、そこでSTOPしない。9 runは最後まで走らせ、結果をまとめて報告すること。問題を見つけても、その場で勝手に仕様変更・Prompt変更・追加対策を実装しない。問題を記録したまま、同じ条件で9 runを最後まで完走する。ただし、API障害・実行不能・データ破損など、物理的に9 runを継続できない技術障害だけは例外として報告する。
> 9 run終了後は残り11 runを勝手に開始せず、報告して待つこと。

## KPI provenance欄

全KPI=fresh(新仕様、承認構成、Production初回path含むE2E=Yes)。比較用の旧9 run値はfrozen(`baseline_old9`、Evidenceではない)。事後評価ラベルは本委任では付けない(委任_06で3 worker分配)。

## Opus台帳更新

該当なし。

## 事前指定Read一覧

1. `er052_output/open233_prod_e2e_01/E2E_RUNBOOK_02.md`: 全文(実行手順・3分割・merge・集計コマンド)。
2. `docs/pm/RESULT_PACKET.md`: Grep `引継ぎ|STAGE_MAP|assert|フィールド` →委任_04の引継ぎ節のみ(STAGE_MAPへの`stage1_reclassify`追加、assert関数名、集計フィールド)。
3. `er052_output/open233_prod_e2e_01/e2e_run_02.py`: Grep `STAGE_MAP|apply_open233|assert_open233|run_instance|def main` →該当範囲(引継ぎ事項の反映箇所の確認・最小修正)。
4. `er052_output/open233_prod_e2e_01/watchlist_floor_only_gold.json`: 全文(個別追跡対象)。
5. `docs/pm/ACTIVE_TASK.md`: 全文。

## 事前指定Grep一覧+追記位置・更新位置の手順

- 事前修正(最小): `e2e_run_02.py`に(a)`STAGE_MAP`へ`stage1_reclassify`(費用のChecker関連への分類)を追加、(b)開始時に`apply_open233_approved_flow_switches()`→`assert_open233_approved_flow_switches()`の両方を呼ぶ(未済なら)。他は変更しない。修正後に`--dry-run`で3 worker再確認。
- 実行後の確認: `runs/*.json`が9件(failed/aborted/skippedを含む)、各run jsonに`stage1_reclassify.reclassify_status`があり`failed`のrunを列挙(provenance注記)。
- `OPEN_ITEMS.md`: Grep `OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01` →行末尾へ「委任_05b(2026-10-06): 新仕様9 run E2E完走(3並列、実費¥X.XX、failed/aborted/skipped各N)、一次集計(ラベル無し)完了、ラベル付け・正式集計は委任_06/07。PRODUCTION_WIRED未。」を追記(1回のEdit)。
- `docs/pm/ACTIVE_TASK.md`: 固定ヘッダで上書き(E2E 9 run完走→ラベル付け→集計・報告へ。残11 runはユーザー確認待ち)。

## 実行コマンド全文

1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-06_OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01_05b.md --json-out docs\pm\delegation_log\2026-10-06_OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01_05b.md_check.json`
2. dry-run(3 worker): `.venv\Scripts\python.exe er052_output\open233_prod_e2e_01\e2e_run_02.py --out-dir er052_output\open233_prod_e2e_02\runs --phase first9 --worker-id 1 --budget-jpy 20 --run-cap-jpy 20 --dry-run`(worker-id 2・3も同様)。
3. 本実行(3プロセス並列、PowerShell `Start-Process`でバックグラウンド起動、各workerのstdout/stderrを`er052_output\open233_prod_e2e_02\logs\worker<n>.log`へリダイレクト):
   - `.venv\Scripts\python.exe er052_output\open233_prod_e2e_01\e2e_run_02.py --out-dir er052_output\open233_prod_e2e_02\runs --phase first9 --worker-id 1 --budget-jpy 20 --run-cap-jpy 20 --yes-run-paid`
   - 同 `--worker-id 2`、`--worker-id 3`。
   - 3プロセスの完了をポーリングで待つ(`budget_state_worker<n>.json`の完了フラグまたはプロセス終了)。所要目安20〜25分。APIレート制限(429等)が連続する場合はRUNBOOKの逐次fallbackに従い、残instanceを1プロセスで続行。
4. merge: `.venv\Scripts\python.exe er052_output\open233_prod_e2e_01\e2e_merge_02.py --runs-dir er052_output\open233_prod_e2e_02\runs --out er052_output\open233_prod_e2e_02\e2e_summary_02.json`
5. 一次集計(ラベル無し): `.venv\Scripts\python.exe er052_output\open233_prod_e2e_01\aggregate_report_abcde_01.py --runs-dir er052_output\open233_prod_e2e_02\runs --out-dir er052_output\open233_prod_e2e_02\report --aggregate-json er052_output\open233_prod_e2e_02\e2e_summary_02.json` →`report/report_abcde.md`・`label_sheet.csv`(ラベル付け分配用)。
6. watch list照合: `watchlist_floor_only_gold.json`の対象(safety_A4 actor/neg3 time)について、9 run中に該当instanceがあれば(neg3)、Stage 1候補→再分類→Stage 2→S1→出口の各段階の判定を抜き出し`report/watchlist_trace.md`へ記録(¥0、run jsonから)。
7. `git status --porcelain`→明示add→commit→push。

## SSOT追記文

OPEN_ITEMS進捗1文(上記)。REPORT/DECISION_LOG/REPORT_LEDGERは委任_07で更新。

## Git

明示add対象のみ: `er052_output/open233_prod_e2e_02/`配下(runs/・logs/・e2e_summary_02.json・report/・approved_switches_dump_worker*.json・budget_state_worker*.json)、`er052_output/open233_prod_e2e_01/`配下の未commit成果物(`e2e_run_02.py`・`e2e_merge_02.py`・`E2E_RUNBOOK_02.md`・`aggregate_report_abcde_01.py`・`baseline_old9/`・`labels_old9_from_rca22.json`・`labeling_guide_01.md`・`labeling_examples_old9.md`)、`OPEN_ITEMS.md`、`docs/pm/delegation_log/2026-10-06_OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01_02.md`(+`_check.json`)、同`_05a.md`・`_05c.md`・`_05b.md`(各+`_check.json`)。`ACTIVE_TASK.md`・`RESULT_PACKET*.md`はaddしない。
コミットメッセージ: `OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01: 新仕様9/20 run E2E完走(3並列、実費¥X.XX、Human Review N件、Rewrite N件/N run、数字floor発火N件)+一次集計(ラベル前)+E2E/集計/ラベル基準ツール、PRODUCTION_WIRED未(委任_02/05a/05b/05c)`(実測値で埋める)
SSOT編集権: `OPEN_ITEMS.md`の進捗1文のみ。push前に`git status --porcelain`で混入確認。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET.md`へ(上書き): 1. T-0結果。2. 事前修正内容(STAGE_MAP・assert)とdry-run結果。3. 実行結果: 9 runのrun別(instance/worker/所要秒/費用/cycle数/Human Review有無/failed・aborted・skipped)、合計・平均費用、worker別経過秒、技術障害・再試行の有無、レート制限の有無。4. 一次集計(ラベル無し)A〜Eの表(`report_abcde.md`の要約): A Checker(AI/機械/重複/延べ/除外後、再分類前後の候補数、`reclassify_status`別run数、除外数・`changed_number`付き除外数)、B 後段AI(重大/軽微/問題なし)・数字floor(a)(c)別発火・S1 BLOCKING化、C Rewrite(件数/run数/再修正要)、D Human Review(件数、発生時は対象英文・fact_id・各段階判定・直接原因の抜粋)、E 費用(run別/合計/平均/Checker・後段判定・Rewrite関連の分離)。5. watch list追跡(neg3時期gold等)。6. 旧9 run基準値(frozen)との並記(同instance対比、n=1注記)。7. 【確認】/【推測】所見(受入観点: Checker改善が機能したか/数字のみfloorでSafety兆候/不要Rewrite減/Human Review 0、の事実のみ。結論・次工程判断はしない)。8. commit hash・push結果・raw URL。9. 一覧外Read理由。10. 委任_06(ラベル付け3 worker分配)への引継ぎ: `label_sheet.csv`のrun別件数、3分割案(W1: neg1/meta_std/hormuz_std、W2: neg7/meta_adv/hormuz_adv、W3: bgroup_B3/neg3/neg2)。

(注: 本保存文は委任文の逐語保存。一部の固定ブロック括弧内の管理ID参照・冗長な出典表記は省略)

