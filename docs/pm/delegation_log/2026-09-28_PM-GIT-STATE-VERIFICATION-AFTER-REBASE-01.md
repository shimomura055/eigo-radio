## 管理ID

(1) PM-GIT-STATE-VERIFICATION-AFTER-REBASE-01(新規、Git状態の検証と事後開示、¥0)/(2) KEY-PHRASE-4PLUS1-TOPIC-PHRASE-PRODUCTION-01 の Fable Gate 3判定同期/(3) FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-01 の Trial記録。一時ファイル `docs/pm/ACTIVE_TASK_SSOT5.md` / `docs/pm/RESULT_PACKET_SSOT5.md`(commitしない)。**SSOT編集権: 本タスクのみ**。並行: 別Sonnet(`TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01`、`er038_*`/`er038_output/`/`user_test/tts_all_role_style_trial_01/`/`TTS-ALL-*`)が実行中で未commit差分を持つ → **その差分に一切触れない(stash/checkout/reset/rebase/clean 禁止)**。

## 性質/到達上限Status/禁止事項

¥0、コード変更なし。禁止: `git stash`/`rebase`/`reset`/`amend`/`force push`/`git add -A`/`git checkout -- <他人のファイル>`。他Agentの未commit差分をcommitしない。E-1/D-1/G-1: 再読なし、Grep→範囲Read、git出力最小化。F-1: 退避不要。T-0: 本委任文を `docs/pm/delegation_log/2026-09-28_PM-GIT-STATE-VERIFICATION-AFTER-REBASE-01.md` へ保存し `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-28_PM-GIT-STATE-VERIFICATION-AFTER-REBASE-01.md --json-out docs/pm/delegation_log/2026-09-28_PM-GIT-STATE-VERIFICATION-AFTER-REBASE-01.md_check.json`、結果1行記録。T-2: TTSなし。T-3: ¥0。

## 背景(事実)

- Task A Agent(FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-01)はローカル commit `44cf1c0662dd8de231fa1ffb0f6e7a7742986d5f` を作成したが、origin/main が先行していたため push できず、merge を安全に中断して終了した。
- その後 KP 4+1 Agent は commit `0cb59383acb67d38a5aaedc775fc501885e8a934` を作成し、push 時にリモート先行のため「無関係差分を `git stash` → `git rebase origin/main` → push → `stash pop`」を実施したと報告(**PM_GOVERNANCE/CLAUDE.md で禁止された操作。事後開示対象**)。この結果、Task A の commit がrebaseで別hashになって origin へ含まれた可能性がある。

## 手順

1. **Git状態の検証(read-only)**: `git log --oneline -15 origin/main`、`git log --oneline -15`、`git status --porcelain`、`git stash list`、`git reflog -20`(要約)。確認事項: (a) `44cf1c06` の内容(`er037_*`、`FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-01_REPORT.md`、`docs/pm/design_family_xy_concreteness_control_trial_01.md`、`er037_output/`)が origin/main に含まれているか(`git log origin/main --oneline -- er037_family_xy_concreteness_control_trial_01.py` と `git show --stat <hash>`)。含まれていれば新hashを記録。含まれていなければ、ローカルに `44cf1c06` が残っているか(`git branch --contains 44cf1c06`、`git cat-file -t 44cf1c06`)を確認し、残っていれば `git merge origin/main`(fast-forward/通常merge、conflictが出たら中断して報告)→`git push origin main`。残っていなければ working tree の `er037_*`/REPORT/設計書/`er037_output/` の存在を確認し、存在すればそれらのみpath指定addで再commit(メッセージ `FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-01: 数字・時刻・固有名詞の前景化抑制Trial(再commit、rebase後の復元)`、trailer `Management-ID: FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-01`)→push。存在しなければSTOPして報告(reflogからの復元は行わず、Fable判断)。(b) `git stash list` が空か(残っていれば触らず報告)。(c) Task B(`er038_*` 等)の未commit差分が working tree に存在するか(存在すれば「stash popで復元されている」ことの傍証として記録。判断はしない)。(d) HEAD == origin/main か。
2. **KP 4+1 判定同期**(Fable Gate 3判定、2026-09-28): `KEY-PHRASE-4PLUS1-TOPIC-PHRASE-PRODUCTION-01` を `PRODUCTION_WIRED`。スコープ: 共通Key Phrase経路(Strategy L/DB Hybrid両経路・全Family)の4+1構成、DB Hybrid backup補完、Strategy L retry 2回+2回目報告、runner-up DEFERRED(OPEN-211)。根拠: commit `0e6744e0`/`0cb59383`、Opus L2(BLOCKER 0、S1〜S7/N1/N7反映)、evidence 9記事+差分evidence_02、test 27件+regression baseline一致、SSOT反映済み。適用: `CURRENT_SPEC.md` 4+1行のStatus文言(Grep `KEY-PHRASE-4PLUS1` `判定待ち`)→「Fable Gate 3判定: `PRODUCTION_WIRED`(2026-09-28、スコープ…)」、`docs/pm/REPORT_LEDGER.md` 行Status、REPORT Gate 3表の判定行、`DECISION_LOG.md` 判定エントリ。
3. **Task A Trial記録**: `FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-01_REPORT.md` 末尾のSSOT追記文案(Grep `SSOT追記` → 範囲)を逐語適用: REPORT_LEDGER新行(Trial、`USER_DECISION_REQUIRED`[Fable判定、Task B cleanup は Fable判定 `REJECTED`]、commit hash は手順1で確定したもの)、DECISION_LOG新エントリ(文案+Fable判定+ユーザー判断待ち論点[Trial-02再現性/Advanced化Prompt側の固有名詞検証/Task B cleanup REJECTED確定])、OPEN_ITEMS候補1件登録。加えて OPEN-217/OPEN-218(Family Y由来)へ「FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-01 に統合(ユーザー決定2026-09-28)。Task C(R1→R2改善C1)は両記事でDeviation MAJOR 0、評価はDeviation Check主判定+rubric併用で実施」を追記(Statusは OPEN のまま、Task Aの結論確定時にclose)。
4. **事後開示の記録**: `DECISION_LOG.md` 末尾に「PM-GIT-STATE-VERIFICATION-AFTER-REBASE-01(2026-09-28): KP 4+1修正1回目AgentがPM_GOVERNANCE/CLAUDE.md禁止の `git stash`+`git rebase origin/main` を実施(push競合回避目的)。検証結果[手順1の事実]。履歴書き換えはユーザー確認必須事項であり、Fableが事後開示。再発防止: 委任文の固定ブロックに『push競合時は `git merge origin/main` のみ可、stash/rebase/reset禁止、conflict時は中断報告』を明記(次の委任から適用)」を追記。`docs/pm/PM_GOVERNANCE.md` 8節「SSOT編集の直列化ルール」末尾へ同趣旨の1項(push競合時の手順)を追記(ユーザー正式採用済みルールの運用補足として。新ルールの新設が必要と判断される場合は追記せず文案のみ報告)。

## Git

add対象: SSOT 4点+PM_GOVERNANCE+KP 4+1 REPORT+delegation_log+`_check.json`(+手順1で必要になった Task A ファイル群)。コミットは (i) 手順1のTask A復旧(必要時)、(ii) `KEY-PHRASE-4PLUS1-TOPIC-PHRASE-PRODUCTION-01: Fable Gate 3判定 PRODUCTION_WIRED をSSOT/REPORTへ同期`(trailer `Management-ID: KEY-PHRASE-4PLUS1-TOPIC-PHRASE-PRODUCTION-01`)、(iii) `FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-01: Trial記録をSSOTへ反映(USER_DECISION_REQUIRED)+PM-GIT-STATE-VERIFICATION-AFTER-REBASE-01 事後開示`(trailer `Management-ID: FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-01`)。各commit直前に `git status --porcelain CURRENT_SPEC.md DECISION_LOG.md OPEN_ITEMS.md docs/pm/REPORT_LEDGER.md docs/pm/PM_GOVERNANCE.md` で自分以外の差分がないことを確認。push は `git push origin main`(競合時は `git merge origin/main` のみ、conflictなら中断報告)。

## 報告

手順1の検証結果(Task A commitの所在・新hash・stash list・Task B差分の有無・HEAD==origin)/適用箇所/新規OPEN番号/commit hash/raw URL(4 SSOT+Task A REPORT+設計書+`er037_family_xy_concreteness_control_trial_01.py`)。
