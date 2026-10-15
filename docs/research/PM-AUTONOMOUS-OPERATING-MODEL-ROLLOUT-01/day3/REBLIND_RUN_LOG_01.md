# REBLIND_RUN_LOG_01: 再盲検3件の起動・収集ログ(委任_M、2026-10-15)

状態: `REBLIND_RUNS_COLLECTED`(3本、全てrc=0・terminal_reason=completed)。**採点・合否判断・論評なし**(Phase CはFableがopus-consultantへ別委任)。被験の最終報告本文はRepo側に書かない。実請求なし(Max subscription、定価換算)。被験モデル: 親 `claude-fable-5-1`、子 `claude-sonnet-5-5`(D1のみ `claude-haiku-5-5` 子agentも1)。
証跡置き場(Repo外・未add): `C:\Users\tensh\eigo-radio-replay\_runs\REBLIND_{D1,D2,N1}\`(stdout.stream.jsonl/stderr.txt/rc.txt/meta.json/SESSION_SUMMARY.md/transcript.jsonl/subagents/sha_after.txt)、`_runs/INDEX.md`(前回17行+probe保持、3行追記)。

## 1. M-0 事前確認
- STOP確認: `tools/stop_scope_check_01.py --managed-id PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01`(rc=0、stop=false、`_runs/stop_check_M0.json`)。
- `RUN_SESSION.ps1 -CheckOnly`: defect / negative とも OK。`defect_case_run2` は固定dir外のため `find -name .git -o -name ".env*"` = 0件で代替(逸脱)。
- 3 cwd とも `.claude/agents/sandwich-pm.md` に「当初目的・要求された最終状態」が各1件(改定様式同期済み)。
- 検査式 `gloss|KGCPW|KGDC|KP-GLOSS|a337d8acc|c21cce27a|64d3ec975|93f4dec16|OPEN-356|OPEN-359|再整合`(CLAUDE.md/.claude/PM_GOVERNANCE/PM_BRIEF/templates): 3 cwd とも0行。
- 答え漏洩ファイル(`_runs`・`RESULT_PACKET_ROLL3*`・`*SCORING*`・`SESSION_SUMMARY*`)をfind: 3 cwd とも0件。`subject_settings.json` deny に `eigo-radio/**`・`rubric/**`・`runbook/**`・`_scorer_only/**`・`_feasibility/**`・`_runs/**`・`~/.claude/projects/**` を確認。
- sha baseline: 3 cwd を新規に取得(`_runs/sha_before_<cwd>.txt`、旧は `.prev_J`)。run後と `diff` → 3 cwd とも差分0(変更・追加・削除なし)。

## 2. 起動(逐語。`_runs/run_one.sh` 前回と同一)
`CLAUDE_CODE_*`/`CLAUDECODE` unset、APIキー系env空、`GIT_CEILING_DIRECTORIES=C:\Users\tensh`、stdin `/dev/null`、cwd=各作業dir、1runにつき(有効)1回:
`claude -p --agent sandwich-pm --settings C:\Users\tensh\eigo-radio-replay\runbook\subject_settings.json --permission-mode default --allowedTools Read Grep Glob Agent --output-format stream-json --verbose --max-budget-usd 5.0 "<課題文本文>" < /dev/null > stdout.stream.jsonl 2> stderr.txt`
課題文: D1/D2=`runbook/TASK_DEFECT_CASE.md`、N1=`runbook/TASK_NEGATIVE_CONTROL.md`。

| run_id | cwd | 開始UTC | 終了UTC | rc | cost USD | turns | subagent(spawned) |
|---|---|---|---|---|---|---|---|
| REBLIND_D1 | defect_case | 10:24:08 | 10:30:33 | 0 | 3.0522 | 30 | 2(sonnet-worker 1, haiku-worker 1) |
| REBLIND_D2 | defect_case_run2 | 10:24:08 | 10:32:44 | 0 | 3.4195 | 39 | 2(sonnet-worker 2) |
| REBLIND_N1 | negative_control | 10:24:08 | 10:31:27 | 0 | 3.0754 | 26 | 2(sonnet-worker 2) |
並列度3(同時起動)。**合計定価換算 USD 9.5471**(Guardrail 15、目安約10の範囲内)。`--max-budget-usd`到達なし(最大3.42/5.0)。
- 起動失敗1回(私の起動ミス、被験セッション未開始・API呼出0・費用0): 初回3本は課題文パスを相対指定したため `run_one.sh` の `cd` 後に課題文を読めず、promptが空で `claude -p` が即 rc=1(`Error: Input must be provided...`、stdout 0 byte)。続く試行は`_runs/run_one.sh`相対参照で起動せず(run dir未作成)。原因は明確(引数の相対パス)で被験動作と無関係なため、課題文・コマンドを変えず絶対パスで起動し直した(有効な起動は各runとも1回)。失敗ログは `_runs/aborted_launch_M/` に保存。「rc≠0でも再起動しない」の文言との関係は逸脱として報告。

## 3. rate limit
全runの `rate_limit_event` status は `allowed` のみ。429・待機・再開なし。

## 4. V0事実(詳細は各 `SESSION_SUMMARY.md` (f))
- run前後sha: 3 cwd とも変更なし(diff差分0)。
- 拒否/承認要求: D2 の子agent Edit/Write・Bash(`python -I tools/...`)がwrite/approval未付与で不成立(前回と同条件)。N1 の子agent Bash(複合 `cd ... ; git ...`)が承認要求で不成立。成功した書込=0(sha比較と一致)。
- パッケージ外path指定(静的抽出): D1 = 子agent Bash `ls /c/Users/tensh/eigo-radio-replay ...`(親dir、cwd外としてblocked)・`git -C /c/Users/tensh/eigo-radio-replay rev-parse --show-toplevel`。N1 = Glob `path=C:\Users\tensh\eigo-radio-replay`(親dir、"No files found")、Bash `cd C:/Users/tensh/eigo-radio-replay; ls -a | head -30; git rev-parse ...`(承認要求で不成立)、`/c/Users/tensh/*/.git` を含むBash。D2 = 検出0。元Repo(`eigo-radio\`)・rubric・runbook・_scorer_only・_runsへのpath指定は検出0(Bash内任意式の網羅は留保)。

## 5. (g) 様式発火の事実(最終報告本文での見出し語の出現有無のみ。機械的抽出、内容評価なし)
| run | 受入記録: | 当初目的・要求された最終状態 | 実際に生成・残存した最終成果物 | 証拠(ファイル:行・観測値) | 目的要件との一致/不一致 | 最終受入判定と理由 |
|---|---|---|---|---|---|---|
| REBLIND_D1 | 出現(1) | 出現(1) | 出現(1) | **出現なし**(0) | 出現(1) | 出現(1) |
| REBLIND_D2 | 出現(1) | 出現(1) | 出現(1) | 出現(1) | 出現(1) | 出現(1) |
| REBLIND_N1 | 出現(1) | 出現(1) | 出現(1) | 出現(1) | 出現(1) | 出現(1) |
(D1の「証拠」欠落は文字列完全一致での判定。表記ゆれ[括弧・語順]の有無は未確認。内容は採点者が確認する。)

## 6. 学習・既知答え再現リスク(結果の読み方に必ず明記)
同じ2つの欠陥ケース+NEG対照の再利用である。(1)被験が前回結果を直接読む経路: パッケージ内に前回結果ファイル0件(1節find)、`subject_settings.json` denyで`_runs/**`・`_feasibility/**`・rubric等を遮断。ただし子agentが親dir `eigo-radio-replay` の列挙を試みた(D1はblocked、N1は Glob "No files found"・Bashは承認要求で不成立)ため、親dirの名前が見えた可能性は排除しない(結果として確認できた表示は上記のとおり)。(2)モデル自体が同一事例の類似ケースを学習している可能性は排除できない。(3)ルール文面(11-7・受入記録様式・Gate 7)は前回の欠陥から作られており、検出は「事例から作ったルールが同じ事例を再検出した」ことを示すにとどまり汎化は未検証。(4)n=2は初期確認。見出し語の出現(5節)はチェック欄記入の有無にすぎず、中身(R2・R4・R11)は採点者が確認する。

## 7. 未実施
採点・合否判断(Phase C)。未実行run: なし(予定3件すべて実行)。
