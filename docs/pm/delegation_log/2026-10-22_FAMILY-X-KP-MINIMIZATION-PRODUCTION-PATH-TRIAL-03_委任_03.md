FABLE-DELEGATION-MARKER: KPMP-B1-FIX-AND-TEST-TRIAGE-委任_03-20261022

# 委任(FAMILY-X-KP-MINIMIZATION-PRODUCTION-PATH-TRIAL-03 委任_03: (A)Family X runnerのKP stage fail-closed修正[FOLLOWUPS_01.md B1 選択肢2=Zと対称: kp_statusがPASS系以外ならstageを停止し、後段TTS/assemblyが旧attemptの`keywords_canonicalized.json`を読まないようにする]。(B)本日検出された既存失敗test(er011 DefaultByteParity 3件、er007 azure import 3件)の既存/新規切り分け。API 0・JPY0)

## 管理ID
FAMILY-X-KP-MINIMIZATION-PRODUCTION-PATH-TRIAL-03 委任_03(OPEN-448/新規OPEN。並行: PNAP設計(er103)、KP3V設計(er104)が作業中。両者はProduction .pyを編集しないが、`er019_family_x_audio_production_runner_01.py`を読んでいる。本委任はこのファイルの**KP stage部分(約:400-434)のみ**を編集。共有SSOTは`git status`→該当行再Grep→自分の行だけ→即add+commit、`index.lock`は30秒待ち)。

## 性質/到達上限Status/禁止事項
- 性質: 既存仕様内の不具合是正(fail-closed化、Family Zと同じ挙動へ)。Opus Gate: 非該当(新構造なし。Zに既存の停止条件をXへ揃える最小修正)。到達Status: 新規OPEN「FAMILY-X-KP-STAGE-FAIL-CLOSED-FIX-01」=`FIXED_RECORDED`。
- 修正範囲(11-8): 範囲内=`er019_family_x_audio_production_runner_01.py`のKP stage後処理(kp_statusの判定で停止・明確なエラー/Status記録・resume時に同stageから再実行できること)、unit/wiring test追加、Regression。範囲外=`er003_v1_n3_01_scaffold_generate.py`の設計(:818-827のHR報告のための旧artifact保持)変更、Z側変更、Prompt変更、KP判定方式変更。
- 費用/日次: JPY0。
- 禁止: `git add -A/-u/-f`、amend、rebase、force push、stash、clean、reset --hard、checkout -f。secret_scan hits=0。push=`git push origin HEAD:main`。ACTIVE_TASK/RESULT_PACKETはgitignore。SSOT全文読込禁止。他agentの未commit差分を混ぜない。有料run禁止。

## Fable判断(根拠)
- B1の経路(`FOLLOWUPS_01.md`): X runner `er019:424`はkp_statusを記録するだけで停止せず、TTS(`:890`,`:1295`)・assembly(`:1955`)はファイルの有無だけで分岐→Redundancy NG済み旧KPが使われ得る。Zは`er026:1486-1494`で停止。**承認済み仕様の意図(Redundancy QA NGのKPは使わない)と実装の乖離=是正対象**(11-8の範囲内)。方式変更ではない。
- 停止の形: 既存のZと同じ扱い(stage失敗としてrc≠0・Status `KP_STAGE_FAILED(<kp_status>)`を`entry_point.json`/stage statusへ記録。HR Lockへは送らない=技術STOP(OPEN-371の扱いに従い、HR Lockへ誤転送しない)。resume: `--stage kp --regenerate-stage kp_*`で再実行可能なことをtestで確認)。

## 実行内容
(A)
1. `er019_family_x_audio_production_runner_01.py:395-440`と`er026_family_z_fiction_production_runner_01.py:1480-1500`を読み、Zの停止条件をXへ移植(PASS系statusの集合はZと同じ定義を共有関数化できるなら共有、できなければ同一リテラル+コメントで相互参照)。
2. test: `er019_family_x_kp_stage_fail_closed_01_test_01.py`(kp_status=CANONICALIZATION_INVALID/SELECTION_FAILED/REDUNDANCY_NGでstage停止・後段未実行・旧ファイルが存在しても読まれない/PASS系で従来どおり続行/resume再実行)。Regression: `.venv\Scripts\python.exe run_project_regression.py --pattern "er019*_test*.py"`、`"er003_test_kp*"`該当、`"er026*_test*.py"`(無影響確認)。
3. runtime evidence(API 0): 既存run dir(例`er019_output/paycheck_personality/run_pp_02`のコピーをtmpへ)でkp_statusを人工的にINVALIDにし、runnerをdry/mockで起動して停止を確認(有料呼出なし。mock範囲を記録)。
(B)
4. 失敗testの切り分け(0円): `er011_open112_trend_synthesis_mode_production_wiring_01_test_01`(DefaultByteParity 3件)と`er007_ja_scg_test_01`(azure import 3件)を、本日の変更前commit(`git worktree add <tmp> 7e17a8338` 等、本日早朝のcommitを選ぶ。worktreeは作業後`git worktree remove`)で実行し、既存失敗か本日の変更由来かを確定。本日由来なら原因commitと修正(軽微なら実施)。既存失敗なら原因(Prompt本文変更に伴うparity期待値の未更新/環境依存import)を1行で記録し、Prompt parity期待値の更新が必要な場合は**実施せず報告**(Prompt関連の期待値は承認済み内容との照合が必要)。
5. SSOT: `OPEN_ITEMS.md`新規行「FAMILY-X-KP-STAGE-FAIL-CLOSED-FIX-01」`FIXED_RECORDED`(経路・是正・test・resume確認。(B)の結果も1文)。`FOLLOWUPS_01.md`B1に「選択肢2を実施(委任_03)」追記。`docs/pm/REPORT_LEDGER.md`1行。CURRENT_SPECのKP節に1行追記が妥当なら文案をRESULT_PACKETへ(編集は不可)。T-0: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-22_FAMILY-X-KP-MINIMIZATION-PRODUCTION-PATH-TRIAL-03_委任_03.md`(Nは`FABLE-DELEGATION-MARKER: KPMP-B1-FIX-AND-TEST-TRIAGE-委任_03-20261022`を含むAgent tool_useの通番、281前後。先頭行で一致確認)。
6. commit→push→到達確認。`RESULT_PACKET_KPMP3.md`。

## Git
- 明示add: `er019_family_x_audio_production_runner_01.py`、新test、`FOLLOWUPS_01.md`、`OPEN_ITEMS.md`、`docs/pm/REPORT_LEDGER.md`、delegation_log(+(B)で修正した場合そのファイル)。
- commit: `FX-KP-FAILCLOSED 委任_03: Family X runnerのKP stageをkp_status非PASSで停止(Zと対称、旧attemptのKP残骸を後段が読まない)+test、既存失敗testの切り分け、¥0`。

## 報告(RESULT_PACKET_KPMP3.md)
(A)差分要約(file:行)・test結果・resume確認・mock evidence/(B)切り分け結果(既存/本日由来、原因、処置)/RESULT_PACKET 4行/raw URL。