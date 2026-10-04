## 管理ID

`OPEN-233-SELF-RECOVERY-TRIAL-01`(委任_62)。並行タスクなし。

## 性質/到達上限Status/禁止事項

- 性質: ユーザー決定[5回目](2026-10-04、選択肢3)の手順4「単体確認PASS後のみ、少数の実flow確認」を実施する(有料、目安¥12〜30)。単体確認(委任_61、`er052_output/open233_floor_verify_unit_check_02/`)と V7b再較正(`open233_safety_control_04/`)はPASSをFableが照合済み(重大期待の非抽出版も確認callのラベルが10/10 BLOCKING、解放0)。**29件横断(手順5)は本委任では行わない**(少数flowの結果をFableが照合してから委任_63で実施)。次Trial(10本)は開始しない。
- 到達上限Status: Trial評価(`VALIDATED`相当の記録)まで。Production採用判断・`PRODUCTION_WIRED`はしない。自己修復機構本体はProduction未接続。
- 禁止事項:
  - Production正式path(`er003*`〜`er019*`)の変更禁止。編集は`er052_open233_*`のみ。コード変更は、少数flowを回すための実行スクリプト(`*_rep23_limited_01.py`)と集計のみ。runner本体のロジック変更は禁止(不具合を見つけたら修正せず報告。集計の表示だけの修正は可)。
  - 新しい仕様候補・新しい対策を勝手に追加しない。新しいProduct判断が必要になったら`USER_DECISION_REQUIRED`としてSTOPし報告。
  - 日本語本文・日本語タイトルへの修正が発生しないこと(`JA_MODE=english_only`)。発生したら即STOPし報告。
  - 解放ログで重大と思われる解放が1件でもあれば(下記の判定基準)、追加runをせずSTOPし報告。
  - 不要な再測定・全文Recheck・惰性的retryをしない。n=2固定。
  - `git add -A`/`stash`/`amend`禁止。既存のM表示差分・untrackedに触れない。`ACTIVE_TASK.md`/`RESULT_PACKET.md`はaddしない。
- 費用上限: 上限¥35(Guardrail。目安¥12〜30はユーザー承認済み)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。Phase累計¥548.214、上限¥900。1 instance-runの費用上限(runner既存Guardrail)は¥7のまま。
- Opus独立技術レビューGate: 本委任は新構造なし(確認のみ)。該当なし。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSを伴わない。)
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`、ユーザー正式決定、費用上限[Cap]を伴う全委任で常時有効): 費用上限[Cap]は「暴走防止のためのGuardrail」であり、Cap到達=自動STOPではない。禁止事項/性質欄の費用上限記載は上記の定型文に従う。

T-0の補足: 保存先 `C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-04_OPEN-233-SELF-RECOVERY-TRIAL-01_62.md`。**委任文は全文そのまま保存(要旨化・要約保存は不可)。** 一時ファイルはリポジトリ外(`%TEMP%`配下)。

## ユーザー指示(原文、該当部分。全文は`DECISION_LOG.md`末尾の2026-10-04ユーザー決定[5回目]を参照)

````
4. 単体確認PASS後のみ、少数の実flow確認を実施。
   - 説明文混入対策
   - 句読点差対策
   - 英語だけ修正
   - 時期だけの追加確認
   - retry / recheck整合
     を確認。
   - 費用目安 ¥12〜30。
5. 少数flowが問題なければ、29件横断を1回だけ実施。
   (略)
今回の作業中に新しいProduct判断が必要になった場合は、追加Trialや仕様拡張へ進まず USER_DECISION_REQUIRED でSTOPしてください。
````

ユーザー決定[4回目](2026-10-04、判断D)§6の確認項目も適用する: 真の重大見逃し 0 / 解放した重大ケース 0 / 過剰Majorが減っている / 不要Rewriteが減っている / Human Reviewが増えていない / 説明文混入対策が誤範囲を選ばない / 句読点差対策が機能する / 英語だけ修正する方針が維持される / retry / recheckで仕様が崩れない。「問題が出たら29件へ進まずSTOPしてください。」

## 作業1: 実行構成(rep23 limited)

- 実行スクリプト: `er052_open233_self_recovery_flow_runner_01_rep23_limited_01.py`(既存の`..._rep22_representative_01.py`を複製して構成を変える)。出力`er052_output/open233_self_recovery_flow_runner_01_rep23/`。
- スイッチ(全て有効化。これが「承認済み対策を全部入れた構成」): `HANDOFF_MODE=violation_span`、`VS_MATCH_EXT=True`、`VS_EXPLAIN_SPLIT=True`(P-strict-closed)、`JA_MODE=english_only`、Stage 2 rubric=V7b(`BODY_RUBRIC_DEFAULT`がV7bであることをGrepで確認)、`FLOOR_VERIFY_MODE=time_only`。その他は既定(⑥OFF、`MAX_CYCLES=2`、`HARD_MAX_CYCLES=3`)。実際に有効になったことをinstance JSONの`switches`で確認し、集計に載せる。
- instance選定: 6 instance × n=2 = 12 instance-run。設計書`docs/pm/design_open233_floor_alignment_01.md` §5「限定flow計画」の選定に従う。§5に具体名がなければ次の基準で選ぶ(選定理由を記録): (i)`hormuz_run03_standard`(実記事・Escalation履歴)、(ii)`meta_run03_standard`(実記事)、(iii)`bgroup_B3`(Safety-critical、J-1ラダー)、(iv)`safety_A2A3`または`safety_A5`(Safety-critical)、(v)rep22で説明文混入(`vs_explain_split`相当の未解決)が発生したinstance 1件(`er052_output/open233_explanatory_mixed_offline_check_01/`の集計から)、(vi)rep22で`changed_time`のfloor-onlyがあったinstance 1件(`er052_output/open233_floor_alignment_offline_01/K_rows.csv`から)。(v)(vi)が同じinstanceなら、句読点差(`VS_MATCH_EXT` L5)が発火したinstanceを1件追加。
- 比較基準: 同じinstanceのrep22結果(`er052_output/open233_self_recovery_flow_runner_01_rep22/`)。rep22に無いinstanceは、直近の同instance結果(rep20〜21等)を基準にし、どれを使ったか記録。

## 作業2: 実行(有料)

- 先に1 instance × n=1で単価を確認(rep22実測は1 instance-run ¥1〜4)。12 runの見込みが¥30を超えるなら、(i)〜(iv)を優先して本数を減らし報告。
- 実行中、instanceごとに完了後に次の即時STOP条件を確認: (a)日本語本文・タイトルに変更が発生、(b)`floor_verify`で解放されたclaimのうち、Fable/人間が見て重大(台帳と矛盾する時期の取り違え・順序反転・継続中の出来事の消滅/復活)と思われるものがある、(c)Safety-critical登録5件(B3、B4-a、A2A3-0、A4-0、A5-0)のいずれかが`residual_at_pass`に残る(=検出されずに合格)、(d)例外・クラッシュ。該当したら追加runを止めて報告。

## 作業3: 集計(`er052_output/open233_self_recovery_flow_runner_01_rep23/summary_01.json` + `summary_01.md`)

ユーザー確認項目ごとに、rep23とrep22(基準)の実測を並べる。

1. 真の重大見逃し: Safety-critical 5件の検出状況、`residual_at_pass`に重大候補が残っていないか(残った文は全件列挙し、正式基準[重大=事実関係の重大な誤解]で仮ラベル付け。Fableが最終判定)。
2. 解放した重大ケース: `floor_verify`の解放ログ全件(claim文/Ledger該当fact逐語/`issue`/確認2回の`materiality`・`basis`・`ledger_citation`/最終値)を`release_log_01.md`に列挙し、各件に仮ラベル(重大/軽微/問題なし)を付ける。対象判定件数・CONFIRMED件数・確認call件数・解放件数・BLOCKING固定理由別件数・費用。
3. 過剰Major: Stage 2でBLOCKINGになった件数(rep22比)、floor-onlyでBLOCKINGになった件数(フラグ別)、そのうち正式基準で軽微以下と思われる件数(仮ラベル)。
4. 不要Rewrite: Rewrite実行件数・不要Rewrite率(既存の定義・計算方法を踏襲し、定義を1行で明記)、rep22比。
5. Human Review: STAGE4_ESCALATION件数とその理由(`escalation_reason`)、rep22比。
6. 説明文混入対策: `vs_explain_split_resolve`の発火件数、採用された範囲(`level="P:<n>"`)全件を列挙し、Checkerの`claim_in_article`と採用範囲・`dropped_remainders`を並べ、誤範囲(本文にない語/説明文の混入/別文の選択)がないか目視相当で確認(全件列挙、仮判定)。
7. 句読点差対策: `VS_MATCH_EXT`のL5(edge punctuation)/`label_only`の発火件数・成功件数、失敗(unresolvable)件数。
8. 英語だけ修正: `current_ja_text=None`で全run通過、JA Rewrite 0件、`en_title_rewritten`の件数、`english_only_ja_source_requires_full_recheck`の発火と全文Recheck実施の対応(発火=Recheck実施が1対1か)。
9. retry/recheck整合: cycle 2・3に入ったrun数、`carry_forward_comparison`/`severity_wobble`の件数、Recheck由来の指摘が同じ経路(handoff・floor・floor_verify・2-of-2)を通っているか(instance JSONの該当フィールドで確認)、解放状態がcycle間で引き継がれていないこと(cycle 2で同じclaimが再評価されているか)。
10. 費用: instance-run別・合計、rep22同instance比、worst instance cost。

各項目に「PASS/注意/FAIL」の仮判定と根拠(件数)を付ける。FAILの定義: 1・2は1件でもFAIL、3・4は「減っていない(増えている)」、5は「増えている」、6は誤範囲1件でもFAIL、7は機能していない(発火0かつ対象があった、または誤解決)、8はJA変更1件でもFAIL、9は仕様崩れ1件でもFAIL。

## 作業4: SSOT・記録

- `OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md` §44「少数実flow確認 rep23(委任_62)」(構成・結果表・仮判定・解放ログ要約・費用)。
- `OPEN_ITEMS.md` OPEN-233行Status: 「少数実flow確認rep23実施(2026-10-04、委任_62、6 instance×n=2、¥X): 項目別【PASS/注意/FAIL】。29件横断(1回)はFable照合後の委任_63。次Trial禁止。Production未接続」(旧Statusは「旧Status参考(委任_61)」で残す)。次Action欄末尾に「(委任_62)Fable照合→問題なければ委任_63=29件横断1回(¥35〜70)→STOP報告(次TrialはユーザーGO待ち)」を追記。
- `docs/pm/REPORT_LEDGER.md` OPEN-233行の備考。`docs/pm/ACTIVE_TASK.md` Status=「IN_PROGRESS(rep23少数flow完了、Fable照合待ち)」(addしない)。`CURRENT_SPEC.md`・`DECISION_LOG.md`は本委任では編集しない(Trial結果はREPORT/OPEN_ITEMSに記録)。

## 事前指定Read一覧

- `er052_open233_self_recovery_flow_runner_01_rep22_representative_01.py`: 全文(複製元)。
- `er052_open233_self_recovery_flow_runner_01.py`: Grep `switches`、`BODY_RUBRIC_DEFAULT`、`FLOOR_VERIFY_MODE`、`floor_verify_summarize`、`residual_at_pass`、`escalation_reason`、`vs_explain_split`、`en_title_rewritten`、`english_only_ja_source_requires_full_recheck`、`severity_wobble`、`carry_forward_comparison`、`unnecessary_rewrite` → 該当範囲(全文Read禁止)。
- `docs/pm/design_open233_floor_alignment_01.md`: §5のみ。`er052_output/open233_floor_alignment_offline_01/K_rows.csv`。`er052_output/open233_explanatory_mixed_offline_check_01/`のresults(集計キーのみ)。
- `er052_output/open233_self_recovery_flow_runner_01_rep22/`: summary系ファイルと、選定した6 instanceのJSON(該当フィールドのみGrep)。
- 既存の不要Rewrite率・Human Review集計の定義: `OPEN-233-SELF-RECOVERY-TRIAL-01_REPORT.md`をGrep `不要Rewrite率`で定義行だけ。
- `OPEN_ITEMS.md`/`REPORT_LEDGER.md`/REPORT: Grep `委任_61` → 更新位置だけ。

## 事前指定Grep一覧+追記位置

- 上記のとおり。`git grep -n "er052_open233" -- "er003*.py" "er009*.py" "er010*.py" "er012*.py" "er019*.py"`(0件を確認)。

## 実行コマンド全文

作業ディレクトリ `C:\Users\tensh\eigo-radio`。PowerShellなら先に `$env:PYTHONIOENCODING="utf-8"`。

T-0:
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-04_OPEN-233-SELF-RECOVERY-TRIAL-01_62.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-04_OPEN-233-SELF-RECOVERY-TRIAL-01_62.md_check.json

単価確認(有料):
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_open233_self_recovery_flow_runner_01_rep23_limited_01.py --stage probe --instances hormuz_run03_standard --n 1 --budget-jpy 5

本実行(有料):
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_open233_self_recovery_flow_runner_01_rep23_limited_01.py --stage main --n 2 --budget-jpy 30

集計:
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er052_open233_self_recovery_flow_runner_01_rep23_limited_01.py --stage agg
(引数名は複製元の実装に合わせてよい。probeの1 runは本実行のn=2に含めてよい[同一構成なら]。)

テスト(コード変更がスクリプト追加のみでも実行):
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -m unittest er052_open233_self_recovery_flow_runner_01_test_01
C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\run_project_regression.py --pattern "er052*_test_*.py"
(全体回帰はrunner本体を変更しないため不要。`budget_state_*.json`等の書き換えは`git checkout`で戻す。)

順序: T-0 → 作業1 → 単価確認 → 本実行(即時STOP条件を確認しながら) → 集計 → テスト → 作業4 → commit/push → 報告。

## Git(明示add対象・コミットメッセージ)

- SSOT編集権: `OPEN_ITEMS.md`の1行、`REPORT_LEDGER.md`の1行、REPORTの追記。`CURRENT_SPEC.md`/`DECISION_LOG.md`/`PM_GOVERNANCE.md`は編集しない。
- commit対象: 実行スクリプト、`er052_output/open233_self_recovery_flow_runner_01_rep23/`配下(instance JSON・summary・release_log)、REPORT、`OPEN_ITEMS.md`、`REPORT_LEDGER.md`、委任ログ`_62.md`・`_check.json`。メッセージ: `OPEN-233-SELF-RECOVERY-TRIAL-01: 承認済み対策を全て有効にした少数実flow確認rep23(6 instance×n=2、¥X)を実施し項目別に集計【結果】、29件横断はFable照合後(次Trial未開始、Production未変更)(委任_62)`
- commit前に`git status --porcelain`で混入なしを確認。競合・失敗は自動解決せず報告。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET.md`と最終メッセージに: (1)結論10行以内(29件横断へ進める状態か、STOP該当か)、(2)構成とinstance選定理由、有効スイッチの実測、(3)項目1〜10の結果表(rep22比・仮判定・根拠件数)、(4)解放ログ全件(件数が多ければ重大候補と判断に迷うものを全件、残りは件数)、(5)説明文混入対策の採用範囲全件、(6)即時STOP条件の該当有無、(7)費用(instance-run別・合計・Phase累計)、(8)テスト、(9)SSOT更新箇所、(10)T-0・commit・push・raw URL、一覧外Read、確認できたことと推測の区別、(11)Fableへの論点。
