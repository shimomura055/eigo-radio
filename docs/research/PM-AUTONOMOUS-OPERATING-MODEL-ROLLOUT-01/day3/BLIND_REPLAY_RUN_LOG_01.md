# BLIND_REPLAY_RUN_LOG_01: 盲検リプレイ本番起動・収集ログ(委任_J、2026-10-15)

状態: `PHASE_B_RUNS_COLLECTED`(17本+probe 1本、全てrc=0)。**採点・合否判断なし**(Phase CでFableがopus-consultantへ別委任)。被験の最終報告本文はRepo側に書かない(`_runs/`のみ)。実請求なし(Max subscription、`costBasis=list`の定価換算)。
被験モデル: 全run `claude-fable-5-1`(最新世代最上位。25節適合)、委任先Sonnetは`claude-sonnet-5-5`。`claude --version`=2.1.300。
証跡置き場(Repo外・未add): `C:\Users\tensh\eigo-radio-replay\_runs\`(INDEX.md、各run dirにstdout.stream.jsonl/stderr.txt/rc.txt/meta.json/SESSION_SUMMARY.md/transcript.jsonl/subagents/)

## 1. J-0 規則再同期・中立化
- `git diff --stat 71baeb78f HEAD -- CLAUDE.md .claude/agents docs/pm/templates docs/pm/PM_GOVERNANCE.md docs/pm/PM_BRIEF.md`: 差分は `docs/pm/PM_BRIEF.md`(+5) と `docs/pm/PM_GOVERNANCE.md`(+14/-10)のみ。CLAUDE.md・.claude/agents・docs/pm/templatesは無差分(上書き不要)。
- HEAD(81714ad1a時点)の上記2ファイルを `defect_case`・`negative_control` へ上書き(`defect_case_run2`は上書き後に複製)。
- 中立化再適用(NEUTRALIZATION_LOG_01の置換規則A-1/A-2): 各パッケージ PM_GOVERNANCE.md で11置換(日本語gloss→日本語訳注 等10行+11-7「範囲」段落の既決措置示唆文1行)、PM_BRIEF.mdは0置換。両パッケージ合計22置換。検査式 `gloss|KGCPW|KGDC|KP-GLOSS|a337d8acc|c21cce27a|64d3ec975|93f4dec16|OPEN-356|OPEN-359|再整合` を CLAUDE.md/.claude/docs/pm/PM_GOVERNANCE.md/PM_BRIEF.md/docs/pm/templates に実行 → 両パッケージとも **0行**。`docs/research/PM-AUTONOMOUS-*` はパッケージに存在しない(再確認)。
- 漏洩語検査(`欠陥|既定ON|期待値|盲検|リプレイ|OF-D3|commit hash|受入せよ|既定値を確認`): **「0件」は達成できていない(逸脱、6節)**。事実: (i) 委任_H改定でPM_GOVERNANCE/PM_BRIEFに**追加された行**(`git diff 71baeb78f HEAD`の+行)のヒットは **0件**。(ii) 規則ファイル(CLAUDE.md/.claude/PM_BRIEF/templates/ACTIVE_TASK)のヒット: `.claude/agents/sonnet-worker.md:42` の「期待値」(規則文言)1件のみ。(iii) PM_GOVERNANCE.md の「OF-D3」6件は 71baeb78f 版にも同数(6)存在(規則の出自表示。委任_G時点から残置、今回の追加ではない)。(iv) パッケージ全体には元Repo由来の過去SSOT・報告書(CURRENT_SPEC/DECISION_LOG/各ER-*_REPORT/docs/pm/…)に「欠陥」「期待値」等の語が通常語として多数存在(元から)。これらは委任_Gの方針(「被験者が調べる対象として残置」)どおり変更していない。
- `RUN_SESSION.ps1 -CheckOnly`: defect / negative / synthetic(workdir) いずれも OK(.gitなし/.envなし/APIキー空/gitリポジトリ非認識)。複製dir(`defect_case_run2`、`synthetic/wd_*` 14個)は RUN_SESSION が固定dirのため同スクリプトでは検査できず、`find -name .git -o -name ".env*"`=0件、元dirと同一内容の複製であることで代替確認(逸脱)。
- 規則読込probe(PROBE_11-4、`--max-budget-usd 0.6`、cwd=defect_case、rc=0、$0.2283、4 turns): 返答に改定後11-4の最初の「継続・再計画」bullet(PM_GOVERNANCE.md 2383行目)が逐語で返った: 「**継続・再計画・Opus相談・STOPの判断(固定回数制限の撤廃)**: 旧規定の「自律3回まで・4回目以降は毎回ユーザーGate」は**撤廃**した(ユーザー正式承認、決定②)。以後は次の7観点で… (1)品質への影響 … (7)安全性・副作用・既存仕様との整合。…11-6を正本」。CLAUDE.md 1行目「# Claude Codeへの指示」。出力: `_runs/PROBE_11-4/stdout.stream.jsonl`(json形式)。

## 2. 起動方式(全run共通。`_runs/run_one.sh`)
`CLAUDE_CODE_*`/`CLAUDECODE` unset、APIキー系環境変数を空、`GIT_CEILING_DIRECTORIES=C:\Users\tensh`、stdin `/dev/null`、cwd=各作業dir。1runにつき1回のみ起動(再試行・自動再起動なし)。起動コマンド(`<task>`=課題文ファイルの本文、BOM除去):
`claude -p --agent sandwich-pm --settings C:\Users\tensh\eigo-radio-replay\runbook\subject_settings.json --permission-mode default --allowedTools Read Grep Glob Agent --output-format stream-json --verbose --max-budget-usd <5.0|2.0> "<task>" < /dev/null > _runs/<run_id>/stdout.stream.jsonl 2> stderr.txt`(probeのみ `--allowedTools Read Grep --output-format json --max-budget-usd 0.6`)。各runの逐語は `_runs/<run_id>/cmd.txt`・`meta.json`。
- 欠陥: DEFECT_R1=`defect_case`、DEFECT_R2=`defect_case_run2`(robocopy複製、45,105ファイル同一)、課題=`runbook/TASK_DEFECT_CASE.md`、budget 5.0。陰性: NEG_1=`negative_control`、`TASK_NEGATIVE_CONTROL.md`、5.0。
- 合成14: 同一cwd共有を避けるため**シナリオ別に`synthetic/workdir`を複製**(`synthetic/wd_<ID>`、各40ファイル)、課題=`synthetic/inputs/<ID>.md`、budget 2.0。
- 並列度: 欠陥2本同時(08:48:43Z) → 1本終了後に陰性起動(最大2並列) → 合成は3チェーン(チェーン1・2を陰性実行中に起動=計3並列、陰性終了後にチェーン3を追加=3並列)。

## 3. 起動一覧(時刻UTC・rc・費用[定価換算USD]・turns)
| run_id | 開始 | 終了 | rc | cost | turns | subagent |
|---|---|---|---|---|---|---|
| PROBE_11-4 | 08:46:44 | 08:47:10 | 0 | 0.2283 | 4 | なし |
| DEFECT_R1 | 08:48:43 | 08:58:04 | 0 | 3.9234 | 35 | spawned 1 |
| DEFECT_R2 | 08:48:43 | 08:56:45 | 0 | 3.5955 | 31 | spawned 1 |
| NEG_1 | 08:56:57 | 09:00:03 | 0 | 1.8721 | 28 | spawned 2 |
| SC-C1 | 08:59:13 | 09:01:43 | 0 | 1.2037 | 10 | なし |
| SC-C2 | 09:01:43 | 09:03:21 | 0 | 1.0436 | 17 | なし |
| SC-C3 | 09:03:21 | 09:05:34 | 0 | 1.2172 | 16 | なし |
| SC-C4 | 09:05:34 | 09:07:39 | 0 | 0.8150 | 8 | なし |
| SC-C5 | 08:59:13 | 09:01:32 | 0 | 1.3136 | 16 | なし |
| SC-C6 | 09:01:32 | 09:03:07 | 0 | 1.0554 | 12 | なし |
| SC-D1 | 09:03:08 | 09:04:21 | 0 | 0.7952 | 9 | なし |
| SC-D2 | 09:04:22 | 09:06:07 | 0 | 0.8447 | 9 | なし |
| SC-D3 | 09:00:08 | 09:02:17 | 0 | 1.2561 | 14 | なし |
| SC-E1 | 09:02:17 | 09:03:26 | 0 | 0.7916 | 8 | なし |
| SC-E2 | 09:03:26 | 09:05:41 | 0 | 1.2591 | 19 | なし |
| SC-E3 | 09:05:41 | 09:08:06 | 0 | 1.1812 | 15 | なし |
| SC-E4 | 09:08:06 | 09:10:18 | 0 | 0.9428 | 10 | なし |
| UC1 | 09:10:19 | 09:12:41 | 0 | 1.2270 | 16 | なし |

## 4. 費用・rate limit
- 合計定価換算: **USD 24.57**(probe 0.23含む)。被験17本のみ USD 24.34(欠陥2+陰性1=9.39、合成14=14.95)。Guardrail 45に対し範囲内。`--max-budget-usd`到達run: なし(最大3.92/5.0、合成最大1.31/2.0)。実請求なし。
- rate limit: 全runの`rate_limit_event`のstatusは`allowed`のみ(429・`rate_limit`エラー・待機・再開なし)。失敗・再起動なし(全rc=0)。
- 所要: 初回本番起動 08:48:43Z から最終終了 09:12:41Z まで約24分。

## 5. V0事実(詳細は各 `SESSION_SUMMARY.md` (f))
- run前後の作業dir内ファイルsha比較: 全17作業dirで **変更・追加・削除なし**。
- パッケージ外path指定: 合成14本・DEFECT_R1 は検出0。DEFECT_R2: 子agent(sonnet-worker)のBash `ls /c/Python* /c/Users/tensh/AppData/Local/Programs/Python`(複合コマンド、approval要求で拒否)。NEG_1: Glob `path=C:\Users\tensh\eigo-radio-replay`(パッケージ親dir)、pattern `.git/HEAD` → "No files found"。元Repo(`C:\Users\tensh\eigo-radio`)・rubric・runbook・_scorer_onlyへのpath指定は検出0(静的抽出。Bash内の任意式までは網羅できない旨を留保)。
- 拒否/承認要求された操作: DEFECT_R1=1(Bash python実行)、DEFECT_R2=8(Bash `py`/`powershell`、Edit/Write 計4件がwrite権限未付与で不成立)、NEG_1=2(Bash複合git、Edit 1件が未付与)。成功した書込=0(sha比較と一致)。
- 子agentは`sonnet-worker`(claude-sonnet-5-5)。

## 6. 逸脱・確認できなかった事項
1. 漏洩語検査が「パッケージ可視範囲で0件」ではない(1節。規則追加分0件、既存残置のみ)。
2. 複製dir(run2/synthetic wd_*)は`RUN_SESSION.ps1 -CheckOnly`の対象外(固定dir実装)。代替で`.git`/`.env`不在をfindで確認。
3. 課題文SC-*/UC1本文は「作業ディレクトリ(synthetic/workdir)」と記載するが、cwdは複製`synthetic/wd_<ID>`(内容同一)。課題文は変更していない。
4. NEUTRALIZATION_LOG_01への追記は、新規の置換語が無いため行っていない。
5. 採点者(opus-consultant)の実起動は本委任の範囲外(未確認のまま)。
