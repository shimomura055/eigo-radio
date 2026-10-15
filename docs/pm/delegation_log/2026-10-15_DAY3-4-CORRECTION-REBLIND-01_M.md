# 委任_M 委任文(逐語保存、2026-10-15)

## 管理ID

`PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01／DAY3-4-CORRECTION-REBLIND-01`(CRB)委任_M(再盲検3件の起動・収集。**採点はしない**=Phase CはFableがopus-consultantへ別委任)。前提: 委任_L(`e9ee8dbbb`/`069654cdb`)で規則・様式反映済み、パッケージ18dir再同期済み、`subject_settings.json`に`_runs/**`・`_feasibility/**`のdeny追加済み。ユーザー承認: 「欠陥ケース2件・正常な陰性対照1件・合計3件」「定価換算費用の目安は約USD 10」「予定した3件を超える追加Trialが必要→STOP」「不合格時に自律的に追加Trialを繰り返さない」。並行: `ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01`委任_01(Repo内`er058_output/`のみ)。本委任のRepo内書込は`docs/research/PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01/day3/REBLIND_RUN_LOG_01.md`(新規)と`docs/pm/delegation_log/`のみ。git `index.lock`衝突時は30秒待ち最大3回再試行。

## 性質/禁止

- 性質: 隔離環境での被験セッション起動・結果収集(実請求なし、subscription枠消費)。到達上限: `REBLIND_RUNS_COLLECTED`または`REBLIND_PARTIAL`(理由付き)。
- **Guardrail: 被験3本の定価換算合計USD 15**(`--max-budget-usd 5.0`/本)。rate limit(429等)が出たら並列を止め1回だけ15分待って再開、再発なら残りを未実行で`REBLIND_PARTIAL`。**各run1回起動・再試行なし**(rc≠0でも再起動しない。事実を記録)。
- 禁止: 被験者へ`rubric/`(v1・v2)・`_scorer_only/`・`_runs/`・`runbook/NEUTRALIZATION_LOG_01.md`・Repo本体・期待値・前回結果を見せる一切の行為。課題文`TASK_*.md`・ACTIVE_TASK・パッケージ内容の変更。`rubric/`・`_scorer_only/`を**本委任では開かない**。被験結果の採点・合否判断・論評(事実抽出のみ)。元Repoへの書込は上記2 path以外禁止。`~/.claude/settings.json`等の変更。git add -A/-f、amend、rebase、force push、stash、clean、reset --hard、checkout -f。
- T-0(恒久運用): 本委任文を`docs/pm/delegation_log/2026-10-15_DAY3-4-CORRECTION-REBLIND-01_M.md`へ全文逐語保存し`.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`(FAILでも継続)。E-1/D-1/G-1/F-1従来どおり。T-2: TTSなし。T-3: 上記Guardrail文。
- 時間見込み: 約1.0h(起動3本並列 約10分+収集・要約 約30分)。

## 事前指定Read一覧

1. `day3/BLIND_REPLAY_RUN_LOG_01.md` §2〜§3(前回の起動コマンド逐語・stdin閉鎖・`CLAUDE_CODE_*`除去・並列度)、`day3/REPLAY_FEASIBILITY_01.md` §4(雛形)
2. `day3/CRB_PHASE1_APPLIED_01.md`(L-5再同期の結果・deny追加・注意点)
3. `C:\Users\tensh\eigo-radio-replay\runbook\RUN_SESSION.ps1`(`-CheckOnly`/`-Print`)、`subject_settings.json`(deny一覧の確認のみ)
4. 前回の`_runs/DEFECT_R1/SESSION_SUMMARY.md`の**見出し構成のみ**(同形式で作るため。本文は読まない)

## 手順

### M-0 事前確認
1. 3 cwd(`defect_case`/`defect_case_run2`/`negative_control`)で`RUN_SESSION.ps1 -CheckOnly`(run2は固定dir外なら`.git`/`.env*`不在をfindで代替)。
2. 3 cwdの`.claude/agents/sandwich-pm.md`に「当初目的・要求された最終状態」が含まれる(=改定様式が同期済み)ことをGrepで確認し、`docs/pm/PM_GOVERNANCE.md`の検査式(`gloss|KGCPW|再整合`等、NEUTRALIZATION_LOGの式)ヒット0を再確認。
3. 3 cwdに`_runs`・`RESULT_PACKET_ROLL3*`・`*SCORING*`・`SESSION_SUMMARY*`が無いことをfindで確認(答え漏洩防止)。
4. 新run_id: `REBLIND_D1`(cwd=defect_case)/`REBLIND_D2`(cwd=defect_case_run2)/`REBLIND_N1`(cwd=negative_control)。出力先`C:\Users\tensh\eigo-radio-replay\_runs\<run_id>\`(新規)。

### M-1 起動(並列3まで)
- `claude -p --agent sandwich-pm --settings <runbook\subject_settings.json> --permission-mode default --allowedTools Read Grep Glob Agent --output-format stream-json --verbose --max-budget-usd 5.0`、課題文は`runbook\TASK_DEFECT_CASE.md`/`TASK_NEGATIVE_CONTROL.md`の本文をpromptとして(前回と同じ方法)。stdinを閉じ、`CLAUDE_CODE_*`環境変数を外す。被験側sonnet-workerのBash(複合)・Edit・Writeが承認待ちで不成立になる制約は**前回と同条件のまま許容**(比較条件を揃える。Fable判断)。
- 保存: `stdout.stream.jsonl`、`stderr.txt`、`rc.txt`、`meta.json`(起動コマンド逐語・開始/終了時刻・`total_cost_usd`・`num_turns`・`session_id`・model・subagent統計)。

### M-2 収集・要約(採点しない)
- 各runに`SESSION_SUMMARY.md`(前回と同じ見出し: (a)起動コマンド (b)rc/cost/turns/model/subagent統計 (c)**最終報告本文を逐語** (d)tool_use一覧(ツール名・主要引数・順序) (e)子agentの最終報告逐語 (f)V0事実: パッケージ外pathアクセス試行[denyされたものも列挙]、ファイル書込の有無[run前後のsha一覧比較])。**合否・評価語は書かない。**
- 加えて(g)**様式発火の事実**(採点ではなく機械的抽出): 最終報告本文に見出し語「受入記録:」「当初目的・要求された最終状態」「実際に生成・残存した最終成果物」「証拠(ファイル:行・観測値)」「目的要件との一致/不一致」「最終受入判定と理由」の各々が出現するか(出現有無のみ。中身の評価はしない)。
- transcript(`~/.claude/projects/<cwd名>/<session_id>.jsonl`と`subagents/`)を各run dirへcopy。`_runs/INDEX.md`に3行追記(前回17行は保持)。
- `day3/REBLIND_RUN_LOG_01.md`: M-0の確認結果、起動一覧(時刻・並列度・rc・cost・turns)、rate limit有無、合計定価換算USD、(g)の出現表(run×6見出し語)、**同一ケース再利用による学習・既知答え再現リスクの明記**(被験者が読める範囲に前回結果が無いことの確認結果とともに)、未実行があればその理由。被験の最終報告本文はRepo側に書かない。

## 実行コマンド全文

- T-0: `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-10-15_DAY3-4-CORRECTION-REBLIND-01_M.md --json-out docs/pm/delegation_log/2026-10-15_DAY3-4-CORRECTION-REBLIND-01_M_check.json`
- 安全確認: `powershell -File C:\Users\tensh\eigo-radio-replay\runbook\RUN_SESSION.ps1 -CheckOnly ...`(各cwd)
- 起動: 上記M-1(全コマンドを`meta.json`と`REBLIND_RUN_LOG_01.md`へ逐語)
- git: `git status --porcelain -- docs/research/PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01/day3/REBLIND_RUN_LOG_01.md docs/pm/delegation_log`、`git log --oneline -3`

## SSOT追記文

なし(Phase C後にFableがまとめて委任)。

## Git

明示add: `day3/REBLIND_RUN_LOG_01.md`、delegation_log(+`_check.json`)。コミットメッセージ: 「DAY3-4-CORRECTION-REBLIND-01 委任_M: 再盲検3件(欠陥2・陰性1)を改定規則同期済みパッケージから`claude -p`自律起動・収集(採点未実施、様式見出し出現の機械抽出のみ)。実請求なし、定価換算USD<実測>」。push origin/main。

## 報告(`docs/pm/RESULT_PACKET_CRBM.md`)

(1)T-0 (2)M-0結果(様式同期確認・検査式0・答え漏洩ファイル0) (3)3本の表(rc/cost/turns/model/subagent/所要) (4)rate limit・失敗 (5)V0事実 (6)(g)様式見出し出現表 (7)所在(SESSION_SUMMARY・transcript) (8)合計定価換算USD (9)commit hash・raw URL (10)逸脱・未確認 (11)Fable向け: Phase C採点委任で渡すpath。**成績に関する所感は書かない。**

Fableは(2)(5)(6)を照合する(受領≠受入)。
