## 管理ID

PM-CLOSEOUT-CONSOLIDATION-124
並行タスク衝突確認: 並行タスクなし(S2配線タスク・Family C v5タスクとも完了済み)。Git操作は本タスクのみ。

## 性質/到達上限Status/禁止事項

- 性質: Closeout統合(¥0、API呼び出しなし)。到達Status: 完了(commit/push成功)または失敗内容の報告。
- 内容: (A) Family C Trial-05成果物のGit記録+SSOT反映、(B) S2配線タスクで発生した安全インシデントのSSOT記録、(C) 再発防止の恒久修正2点(委任文標準テンプレートの回帰コマンド規定+`run_project_regression.py`の非テストファイル拒否ガード)、(D) transcript退避2件、(E) ACTIVE_TASK固定ヘッダ更新。
- 禁止: 記事生成・API呼び出し一切禁止/`run_project_regression.py --pattern`に`_test`を含まないglobを渡すこと厳禁(本インシデントの原因)/`git add -A`・`git add .`・`stash`・`clean`・`amend`・`rebase`・`force push`禁止/er013_*・er003_*・er011_*のProduction/Trialコードの機能変更禁止(`run_project_regression.py`のガード追加のみ可)/`APPROVED_FOR_PRODUCTION`・`PRODUCTION_WIRED`をFamily Cに付与しない(Family CはTrial VALIDATED止まり)。
- STOP条件: `run_project_regression.py`ガード追加で既定回帰の収集件数(2588)が変わる場合はガードを入れずに報告(実装案のみ記載)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

---
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
---

## ユーザー指示(原文)

> (Family C) Trial終了時は REJECTED/VALIDATED/USER_DECISION_REQUIRED のいずれかに分類し、VALIDATEDでもProductionへは進まずSTOPしてください。
> (Discovery S2) 1項目でも未確認ならPRODUCTION_WIREDとしないでください。
(本CONSOLIDATIONはFableの自律実施範囲[¥0・低リスク・整合性修正]。恒久ルールの文言追加はFableが事後報告する。)

## 事前指定Read一覧

1. `docs/pm/RESULT_PACKET_FC5.md` 全文(短い)。
2. `EDITORIAL-FUTURE-FAMILY-C-V5-EMOTION-RECOVERY-AND-CONSTRAINT-STABILITY-TRIAL-05_REPORT.md` L351-380(Artifact・commit対象候補一覧)とL401-450(SSOT追記文案・DECISION_LOG案)。
3. `docs/pm/RESULT_PACKET_S2W.md` 全文(短い)。
4. `FAMILY-A-DISCOVERY-S2-PRODUCTION-WIRING-01_REPORT.md` L6-33(安全インシデント0節)。
5. `run_project_regression.py` 全文(ガード追加対象、構造変更のため全文可)。
6. `docs/pm/templates/DELEGATION_STANDARD_TEMPLATE.md` L43-49(実行コマンド全文セクション)。
7. `docs/pm/tools/README.md`: Grep `collect_subagent_transcripts` → 使用法の該当範囲のみRead。
8. `docs/pm/PM_BRIEF.md` L133-157(ACTIVE_TASK固定ヘッダ書式)。

## 事前指定Grep一覧+追記位置・更新位置の手順

- `OPEN_ITEMS.md`: Grep `^\| OPEN-147 ` → 行末尾へ追記(下記SSOT追記文①)。Grep `^\| OPEN-135 ` → 行末尾へ追記(下記②)。既存内容は削除しない。
- `DECISION_LOG.md`: Grep `FAMILY-A-DISCOVERY-S2-PRODUCTION-WIRING-01` で直近エントリ位置と索引行書式を確認 → その直後に新エントリ「PM-CLOSEOUT-CONSOLIDATION-124」(下記③)を追加し、索引に1行追加。
- `docs/pm/MODEL_ROUTING_TRIAL_LOG.md`: Grep `family_c_future_trial_04|Trial-04` → 直近Family C行の直後にTrial-05行(gpt-5.6-luna等の実使用モデルはTrial-05 REPORT 12節/`er013_output/family_c_future_trial_05/cost_summary.json`に従う、実費¥22.88)を追記。
- `docs/pm/PM_GOVERNANCE.md`: Grep `D-2` → 11節D-2の末尾へ1項追加(下記④)。
- `docs/pm/templates/DELEGATION_STANDARD_TEMPLATE.md`: L43-49「実行コマンド全文」の説明文末尾に下記⑤を追加。
- `run_project_regression.py`: `--pattern`引数で受け取ったglobがテストファイル限定でない場合(パターン文字列に`_test`を含まない場合)、収集前に「非テストファイルをimport実行する危険があるため拒否」というメッセージを出して終了コード2で終了するガードを追加する(`--allow-non-test-pattern`フラグを明示した場合のみ従来動作)。既定(pattern未指定)の動作・収集件数は変えない。変更後、`.venv\Scripts\python.exe run_project_regression.py --pattern "er013*"`が拒否されること、`--pattern "er013*_test_*.py"`が従来どおり実行されること、既定実行の収集件数が2588であることを確認する。
- transcript退避: README記載の使用法に従い、session `294958fe-da6e-491c-8a02-4f864d8195c8`のtaskId `afddb6ad831a29246`(S2配線)と`a5f1da0e03c3eacdb`(Family C v5)の2件を`docs/pm/transcripts/`へ退避(0バイト時はREADMEのJSONL復旧手順で復旧)。
- `docs/pm/ACTIVE_TASK.md`: 固定ヘッダ付きで上書き(管理ID=本タスク、Status、UDR-blocking=なし[Fableがユーザー報告で提示する判断事項はFable側で扱う]、UDR-deferred=OPEN-134/121(d)等既存、APPROVED未配線=OPEN-83/145/146(+OPEN-120 3Vゲートruntime evidence待ち)、STOP条件=なし、次アクション=ユーザー報告、未回答報告=なし、報告単位Status: Discovery S2=PRODUCTION_WIRED / Family C=Trial VALIDATED(Production未採用))。
- RESULT_PACKETは`docs/pm/RESULT_PACKET.md`へ上書き。

## 実行コマンド全文

(すべて `C:\Users\tensh\eigo-radio` で実行)
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\PM-CLOSEOUT-CONSOLIDATION-124.md --json-out docs\pm\delegation_log\PM-CLOSEOUT-CONSOLIDATION-124_check.json`
2. ガード確認(拒否されることの確認): `.venv\Scripts\python.exe run_project_regression.py --pattern "er013*"`(期待: 終了コード2、収集・実行なし)
3. ガード確認(テスト限定は通る): `.venv\Scripts\python.exe run_project_regression.py --pattern "er013*_test_*.py"`(期待: 従来どおり実行、Trial-05新規テスト込みで全PASS)
4. 既定回帰(件数不変確認、1回): `.venv\Scripts\python.exe run_project_regression.py`(期待: 2588 collected/2585 passed/3 failed[既知`er003_test_p2j_investigate`]/0 errors)
5. transcript退避: `.venv\Scripts\python.exe docs\pm\tools\collect_subagent_transcripts.py --apply`にREADME記載の引数(session id `294958fe-da6e-491c-8a02-4f864d8195c8`、task id `afddb6ad831a29246` と `a5f1da0e03c3eacdb`)を付けて実行。実際に使った全文コマンドをRESULT_PACKETへ記録。
6. `git status --porcelain` / `git diff --stat` で対象確認 → 明示add → commit → `git push origin main`。

## SSOT追記文

① OPEN-147末尾: 「(EDITORIAL-FUTURE-FAMILY-C-V5-EMOTION-RECOVERY-AND-CONSTRAINT-STABILITY-TRIAL-05、2026-09-13) 同一テーマ・同一Ledgerでv5契約(感情起伏1+選択1+出来事目安+見出し3固定による統合示唆配置+枠外will禁止)を検証。A2 434語/B1 520語(目安内)、感情・没入感A2=3/B1=3(Trial-04の1から回復)、研究解説感0、Ledger Deviation COMPLIANT、Future Framing QA v2 A2/B1 PASS(Trial-04 B1のREVIEW_REQUIRED解消)、A2×3サンプルで制約追加による不安定化なし(gate_attempts=1)。分類: VALIDATED(Trial、Production未採用、STOP)。実費¥22.88、Family C残額(¥105.01+追加¥100)→¥182.13。Fable照合所見: (i)2場面が『順調→停止→苛立ち→人が介入』の同一感情アークを反復(A2/B1・安定性3本で同型、テンプレ化として残存問題)、(ii)Fact Checker A' REVIEW_REQUIRED(Trial-03から不変)の原因を特定: Fact Checker入力は[[IMAGINED]]枠外の統合示唆段落のみ(全文could/might hedged予測)で、News用Fact Checker A'がこれを裏付けなしの具体的主張と判定(contradictions=0、A2/B1とも)。事実誤りではなくFuture記事への判定基準未適合という構造問題。扱い(Future-aware判定ルール/枠外段落の除外/現状維持)はユーザー判断待ち。」
② OPEN-135末尾: 「(PM-CLOSEOUT-CONSOLIDATION-124、2026-09-13) Fable照合: Gate 3 14項目の証跡確認によりPRODUCTION_WIRED承認。残存注記: runtime evidenceは分岐(b)fail-closedで発火確認済みだが、Production版`run_one_pattern_staged_discovery_focus()`で記事が正常完走した実データ証跡は未取得(Trial版で完走済み、Production版はモック24件のみ)。正常完走証跡Trial(¥40-60、Discovery残額¥88.31内)の実施可否はユーザー判断待ち。」
③ DECISION_LOG新エントリ「2026-09-13: PM-CLOSEOUT-CONSOLIDATION-124。(A) Family C Trial-05をGit記録・OPEN-147反映(VALIDATED、Production未採用)。(B) 安全インシデント記録: FAMILY-A-DISCOVERY-S2-PRODUCTION-WIRING-01でFableの委任文が指定した回帰コマンド`run_project_regression.py --pattern "er003*"`/`"er011*"`がテスト以外のrunnerスクリプトをimport実行し、無関係のProduction記事(pool_n18_notifications_specfix_v2)への実API呼び出し(¥15-20相当)とファイル上書きが発生。Sonnetが即時kill+`git checkout --`で復元、以後`_test_*.py`限定で再実行。原因はFable委任文の欠陥(コマンド指定の安全性未確認)。(C) 再発防止(¥0・整合性修正、Fable自律実施・事後報告): 委任文標準に『回帰patternは必ず`_test`を含む』を明記、`run_project_regression.py`に非テストpattern拒否ガード追加(既定動作・収集件数2588不変)。(D) transcript退避2件。詳細: 各REPORT参照。」
④ PM_GOVERNANCE 11節D-2末尾: 「D-2-補足(2026-09-13、PM-CLOSEOUT-CONSOLIDATION-124): 委任文の実行コマンドで`run_project_regression.py --pattern`を指定する場合、patternは必ず`_test`を含むテストファイル限定glob(例`er003*_test_*.py`)とする。テスト以外の`.py`をimport実行すると一回限りrunnerが実行されProduction記事への実API呼び出し・上書きが起こる(同日インシデント)。ハーネス側にも非テストpattern拒否ガードを追加済み。」
⑤ テンプレート「実行コマンド全文」説明文末尾: 「`run_project_regression.py --pattern`のglobは必ず`_test`を含める(例`er003*_test_*.py`)。テスト以外のスクリプトがimport実行される事故防止(CONSOLIDATION-124)。」
- 上記①②の数値は各RESULT_PACKET/REPORTと照合し、差異があれば実値を優先して記載しRESULT_PACKETに差異を報告。

## Git(明示add対象・コミットメッセージ・trailer)

- 明示add対象: `er013_family_c_future_writer_05.py`、`er013_family_c_future_qa_05.py`、`er013_family_c_future_qa_test_05.py`、`er013_family_c_future_trial_05_run.py`、`EDITORIAL-FUTURE-FAMILY-C-V5-EMOTION-RECOVERY-AND-CONSTRAINT-STABILITY-TRIAL-05_REPORT.md`、`er013_output/family_c_future_trial_05/`配下(記事txt・json・md・html・stability/配下。音声等大容量は無し想定、あれば除外)、`docs/pm/delegation_log/EDITORIAL-FUTURE-FAMILY-C-V5-EMOTION-RECOVERY-AND-CONSTRAINT-STABILITY-TRIAL-05.md`+`_check.json`、`docs/pm/delegation_log/PM-CLOSEOUT-CONSOLIDATION-124.md`+`_check.json`、`docs/pm/RESULT_PACKET_FC5.md`、`docs/pm/RESULT_PACKET_S2W.md`、`OPEN_ITEMS.md`、`DECISION_LOG.md`、`docs/pm/PM_GOVERNANCE.md`、`docs/pm/templates/DELEGATION_STANDARD_TEMPLATE.md`、`run_project_regression.py`、`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`、`docs/pm/transcripts/`配下の新規退避2件。
- 本タスク開始前から存在する無関係の既存差分(er006_output/*・er011_output/attempt_history.jsonl・er012_*等の`M`、多数の`??`)はaddしない。
- コミットメッセージ: `PM-CLOSEOUT-CONSOLIDATION-124: Family C Trial-05(VALIDATED)のGit記録+S2配線時の安全インシデント記録+回帰pattern再発防止(委任文標準+ハーネスガード)` の後に空行、末尾に
  `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`
  `Claude-Session: https://claude.ai/code/session_01THnbjj6FiMbJtrKdFteoE4`
- `git push origin main`。失敗時はforceせず報告。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET.md`へ: 1) commit hash・push結果、2) add対象ファイル数と内訳、3) ガード動作確認3コマンドの結果(拒否/通過/既定件数)、4) 既定回帰件数・PASS・FAIL内訳、5) transcript退避結果(2件、サイズ、0バイト復旧の有無)、6) SSOT追記の実施位置(ファイル・行)、7) ①②の数値照合で差異があれば内容、8) T-0結果1行、事前指定外Read(理由付き)、9) ACTIVE_TASK固定ヘッダ更新済み、10) STOP該当の有無。

## Fable自己チェック(送信前)

- [x] Read一覧に行範囲/Grepパターンあり
- [x] 追記位置手順あり
- [x] コマンドに引数実値あり
- [x] 禁止事項・費用上限あり(¥0、非テストpattern禁止)
- [x] 並行タスク衝突回避あり(並行なし)
