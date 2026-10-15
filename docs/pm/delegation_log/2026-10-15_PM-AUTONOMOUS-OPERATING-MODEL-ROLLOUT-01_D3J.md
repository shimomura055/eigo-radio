## 管理ID

`PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01` Day 3〜4 = 委任_J(Phase B: 盲検リプレイ本番の起動・収集。**採点はしない**=Phase CでFableがopus-consultantへ別委任)。前提: 委任_G `7997c894d`(パッケージ)、委任_H `286b71e9a`/`0121b5863`(11-4改定等)、委任_I `81714ad1a`(実動作確認: `claude -p --agent sandwich-pm`で起動・Agent委任成立、OAuth subscription Max 20x=実請求なし・定価換算表示、deny有効、並列ログ分離OK)。ユーザー正式決定①(2026-10-15): Fable自律起動を原則、被験に正解・欠陥所在・採点基準を知らせない、元Repo書込・秘密情報・外部Production影響なし、安全確認失敗時は停止。並行委任なし。Repo内で編集するのは`docs/research/PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01/day3/BLIND_REPLAY_RUN_LOG_01.md`(新規)と`docs/pm/delegation_log/`のみ。

## 性質/到達上限Status/禁止事項

- 性質: 隔離環境での被験セッション起動・結果収集(実請求なし。subscription枠を消費)。到達上限: `PHASE_B_RUNS_COLLECTED`(全17本の収集完了)または`PHASE_B_PARTIAL`(理由付き)。
- **費用Guardrail: 被験セッション合計 定価換算USD 45**(委任_I見積: 被験約USD 23、範囲14〜36)。`--max-budget-usd`は欠陥/陰性 5.0・合成 2.0(ターン完了後判定のため、1ターン分の余裕を含めた値)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量発火・同じ失敗の無意味なretry・原因不明の増加・scope外処理)のみSTOPし報告。**rate limit(429/`rate_limit`系エラー)が出たら、その時点で並列を止め、1回だけ15分待って再開。再発したら残りを未実行として`PHASE_B_PARTIAL`で報告**(ユーザー本人のMax枠を圧迫するため)。
- 禁止: 被験者へ`rubric/`・`_scorer_only/`・`runbook/NEUTRALIZATION_LOG_01.md`・Repo本体・期待値・欠陥所在を見せる一切の行為。課題文`TASK_*.md`・ACTIVE_TASK・`synthetic/inputs`の**内容変更禁止**(読むのは起動に必要な範囲のみ)。`_scorer_only/`と`rubric/`は**本委任では開かない**(採点独立性)。被験結果の採点・合否判断・論評をしない(事実の抽出のみ)。元Repo(`C:\Users\tensh\eigo-radio`)への書込は上記2 pathのみ。`~/.claude/settings.json`等のユーザー設定変更禁止。git add -A/-f、amend、rebase、force push、stash、clean、reset --hard、checkout -f。
- 時間見込み: 約2.5h(規則再同期0.3h/欠陥2+陰性1 並列2で約0.8h/合成14 並列3で約0.8h/収集・要約0.6h)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない。D-1: Grep→該当行範囲Read。G-1: git出力最小化。F-1: transcript退避不要。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果をRESULT_PACKETへ1行記録(FAILでも継続)。保存先: `docs/pm/delegation_log/2026-10-15_PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01_D3J.md`(**全文逐語保存。要旨化禁止。見出しも本文のまま**)。
T-2: TTSなし。T-3: 上記Guardrail文に従う。

## KPI provenance欄 / Opus台帳更新

該当なし。

## 事前指定Read一覧

1. `docs/research/PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01/day3/REPLAY_FEASIBILITY_01.md` §4(雛形コマンド)・§1(制約: `--max-budget-usd`はターン後判定、stdinを閉じる、`CLAUDE_CODE_*`を外す、並列2〜3)
2. `docs/research/PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01/day3/BLIND_REPLAY_RUNBOOK_01.md` §1〜§2(配置・起動手順。合成14件の起動単位・cwd・入力の与え方)
3. `C:\Users\tensh\eigo-radio-replay\runbook\RUN_SESSION.ps1`(引数)、`NEUTRALIZATION_LOG_01.md`(**置換規則のみ**を読む。被験者には見せない)
4. `docs/research/PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01/day3/DAY3_PHASE_A_APPLIED_01.md`(委任_Hが変更した規則ファイル一覧=再同期対象: `docs/pm/PM_GOVERNANCE.md`・`docs/pm/PM_BRIEF.md`。CLAUDE.md/Agent定義は`71baeb78f`から無変更か`git diff --stat 71baeb78f HEAD -- CLAUDE.md .claude/agents docs/pm/templates`で確認)

## 手順

### J-0 規則の再同期と中立化(両パッケージ `defect_case`/`negative_control`)
1. `git diff --stat 71baeb78f HEAD -- CLAUDE.md .claude/agents docs/pm/templates docs/pm/PM_GOVERNANCE.md docs/pm/PM_BRIEF.md` → 差分のあるファイルだけをHEAD版でパッケージへ上書き。
2. `NEUTRALIZATION_LOG_01.md`の置換規則を再適用し、検査式(同LOG記載)のヒットが0行であることを確認。11-7「範囲」段落の既決措置示唆文も再度除去。
3. 漏洩語検査(`欠陥|既定ON|期待値|盲検|リプレイ|OF-D3|commit hash|受入せよ|既定値を確認`)を被験者可視範囲(パッケージ全体から`rubric/`・`_scorer_only/`・`runbook/`を除く)で実行し0件を確認。**新規則文書(11-4改定等)に「盲検」「リプレイ」等の語が入った場合は、委任_Gと同じ方法で中立化し、置換をLOGへ追記**(`docs/research/PM-AUTONOMOUS-*`はパッケージから除去済みを再確認)。
4. `RUN_SESSION.ps1 -CheckOnly`を各作業dirで実行(`.git`/`.env`/APIキー/ceiling)。
5. 規則読込の確認probe(1回、`--max-budget-usd 0.6`): defect_caseのcwdで`claude -p --agent sandwich-pm --settings <subject_settings> --allowedTools Read Grep "Quote verbatim the first bullet that begins with '- **継続・再計画' under heading '### 11-4' in docs/pm/PM_GOVERNANCE.md, and the first line of CLAUDE.md. Do nothing else."` → 改定後11-4が読まれることを記録(出力json保存)。

### J-1 欠陥ケース×2・陰性対照×1
- 欠陥ケースrun1は`defect_case/`、run2は**`defect_case_run2/`へ複製**(`robocopy /E`または`Copy-Item -Recurse`。`.git`なしを再確認)。陰性対照は`negative_control/`。各run前に`-CheckOnly`。
- 起動: `RUN_SESSION.ps1 -Print`の引数(`--agent sandwich-pm --settings subject_settings.json --permission-mode default --allowedTools Read Grep Glob Agent --output-format stream-json --verbose`)+`--max-budget-usd 5.0`、課題文は`runbook/TASK_DEFECT_CASE.md`/`TASK_NEGATIVE_CONTROL.md`の本文をpromptとして渡す(runbook §2の方法どおり)。stdinを閉じ、`CLAUDE_CODE_*`環境変数を外す。並列2まで。
- 出力: `C:\Users\tensh\eigo-radio-replay\_runs\<run_id>\stdout.stream.jsonl`、`stderr.txt`、`rc.txt`、起動時刻・終了時刻・`total_cost_usd`・`num_turns`・`session_id`を`meta.json`へ。

### J-2 合成シナリオ14件
- runbook §2の起動単位に従う(1シナリオ=1セッション、cwd=`synthetic/workdir`またはシナリオ別dir。**同一cwdでの同時起動は、セッション間でファイル書込が共有されないことをrunbookで確認できた場合のみ**。確認できなければシナリオ別にcwdを複製)。`--max-budget-usd 2.0`、並列3まで。
- 出力はJ-1と同形式(`_runs/SC-xx/`)。

### J-3 収集・要約(採点しない)
- 各セッションについて`_runs/<run_id>/SESSION_SUMMARY.md`を作成: (a)起動コマンド逐語 (b)rc・`total_cost_usd`・`num_turns`・model(`modelUsage`)・subagent統計 (c)**最終報告本文を逐語**(stream-jsonの最後のassistant textまたはresult) (d)tool_use一覧(ツール名・主要引数[file_path/pattern/subagent_type]・順序) (e)Agent委任があればその子agentの最終報告逐語 (f)V0妥当性の**事実**: パッケージ外pathへのアクセス試行の有無(denyされたものも含め列挙)、ファイル書込の有無(run前後でパッケージ内sha一覧を比較)。**合否・評価語は書かない**。
- transcriptの所在(`~/.claude/projects/<cwd名>/<session_id>.jsonl`と`subagents/`)を`meta.json`へ記録し、同dirへcopy(`transcript.jsonl`、`subagents/`)。
- `_runs/INDEX.md`: 17本(+probe)の一覧(run_id/種別/cwd/rc/cost/turns/model/stdout path/transcript path/SESSION_SUMMARY path)。
- Repo内`day3/BLIND_REPLAY_RUN_LOG_01.md`: J-0の再同期・中立化・漏洩検査結果、`-CheckOnly`結果、起動一覧(時刻・並列度・rc・cost)、rate limit発生の有無、合計定価換算USD、未実行があればその理由。**被験の最終報告本文はRepo側には書かない**(`_runs/`のみ。採点前の漏洩と重複を避ける)。

## 実行コマンド全文

- T-0: `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-10-15_PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01_D3J.md --json-out docs/pm/delegation_log/2026-10-15_PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01_D3J_check.json`
- 規則差分: `git diff --stat 71baeb78f HEAD -- CLAUDE.md .claude/agents docs/pm/templates docs/pm/PM_GOVERNANCE.md docs/pm/PM_BRIEF.md`
- 安全確認: `powershell -File C:\Users\tensh\eigo-radio-replay\runbook\RUN_SESSION.ps1 -CheckOnly ...`(各cwd)
- 起動: REPLAY_FEASIBILITY_01 §4の雛形(全起動コマンドを`_runs/<run_id>/meta.json`と`BLIND_REPLAY_RUN_LOG_01.md`へ逐語記録)
- git: `git status --porcelain -- docs/research/PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01/day3/BLIND_REPLAY_RUN_LOG_01.md docs/pm/delegation_log`、`git log --oneline -3`

## SSOT追記文

なし(SSOT不編集。Phase C後にFableがまとめて委任)。

## Git(明示add対象・コミットメッセージ・trailer)

明示add: `day3/BLIND_REPLAY_RUN_LOG_01.md`、`docs/pm/delegation_log/..._D3J.md`(+`_check.json`)。`_runs/`・パッケージはRepo外でaddしない。
コミットメッセージ: 「PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01 Day3 Phase B 委任_J: 盲検リプレイ本番起動(規則再同期+中立化再適用、欠陥2・陰性1・合成14=計17セッション、隔離dirから`claude -p`自律起動、採点未実施)。実請求なし(subscription)、定価換算USD<実測>」。push to origin/main。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_ROLL3J.md`へ: (1)T-0 (2)J-0結果(再同期ファイル・中立化置換数・漏洩検査0件の証跡・probeで読まれた11-4本文の抜粋) (3)17本の一覧表(rc/cost/turns/model/subagent有無/所要時間) (4)rate limit・失敗・再起動の事実 (5)V0事実(パッケージ外アクセス試行・書込の有無) (6)transcript/summaryの所在 (7)合計定価換算USDと内訳 (8)commit hash・push・raw URL(RUN_LOG) (9)確認できなかった事項・逸脱 (10)Fable向け: Phase C採点委任で渡すべきpath一覧(SESSION_SUMMARY・transcript・INDEX)。**被験の成績に関する所感は書かない。**

Fableは(2)(3)(5)を照合する(受領≠受入)。
