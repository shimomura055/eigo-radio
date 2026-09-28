## 管理ID

FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-02 の Trial記録+PM-RECOVER-DELETED-UNTRACKED-FILES-01 の事後開示の SSOT 反映(¥0、コード変更なし)。一時ファイル `docs/pm/ACTIVE_TASK_SSOT7.md` / `docs/pm/RESULT_PACKET_SSOT7.md`(commitしない)。**SSOT編集権: 本タスクのみ**(他の並行Sonnet 3件[er040/er041/er038系Trial]はSSOT編集権なし)。開始時・commit直前に `git status --porcelain CURRENT_SPEC.md DECISION_LOG.md OPEN_ITEMS.md docs/pm/REPORT_LEDGER.md docs/pm/PM_GOVERNANCE.md` で他差分なしを確認。**削除・移動・`rm`・`git clean`・stash/rebase/reset/amend/force push 禁止**(push競合時は `git merge origin/main` のみ、conflictは中断報告)。`git add -A` 禁止。E-1/D-1/G-1: 再読なし、Grep→範囲Read、git出力最小化。F-1: 退避不要。T-0: 本委任文を `docs/pm/delegation_log/2026-09-28_FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-02_03.md` へ保存し `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-28_FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-02_03.md --json-out docs/pm/delegation_log/2026-09-28_FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-02_03.md_check.json`、結果1行記録。T-2: TTSなし。T-3: ¥0。

## 事前指定Read一覧

- `docs/pm/RESULT_PACKET_CC2.md`:58-82(USER_DECISION事項・SSOT文案)
- `docs/pm/RESULT_PACKET_REC1.md`(復元結果の詳細、Grep `復元|byte|不可` → 範囲)
- `OPEN_ITEMS.md`: 最終番号(Grep `OPEN-22`)、OPEN-217/218/220 行
- `docs/pm/PM_GOVERNANCE.md` 8節「SSOT編集の直列化ルール」末尾(Grep `push競合`)

## 適用内容

1. `docs/pm/REPORT_LEDGER.md`: Trial-02 新行(RESULT_PACKET_CC2 文案、Status `USER_DECISION_REQUIRED`[Fable判定]、commit `42f63319`、Opus発火なし)。
2. `DECISION_LOG.md` 末尾: (a) Trial-02 エントリ(2×2 Matrix結果要約[T0全セルCOMPLIANT、T1はHormuz AN3-T1/Meta AN2-T1でMAJOR各1、AN3は数字削減優位、固有名詞削減は同水準]、固有名詞9→19の原因[改良カウンタでJA=EN=7、英語化による新規追加0、アーティファクト]、費用¥16.9、Fable判定 `USER_DECISION_REQUIRED`、ユーザー判断待ち論点3点[AN3/AN2の優先、T1の保留/不採用、OPEN-220の優先度]、Production無変更)。(b) `PM-RECOVER-DELETED-UNTRACKED-FILES-01`(2026-09-28): Trial-02 初回AgentがスコープN外の未追跡ファイル2件を `rm -f` で誤削除(`a2_jt_debug.json` 1,117 bytes/2026-09-27作成=復元不可、`docs/pm/b1b_naming_investigation.md` 9,213 bytes=transcriptのWrite内容からbyte一致で完全復元)。再発防止: 全委任文の固定ブロックへ「削除・移動・`rm`・`git clean` 禁止、自タスクout-dir外に触れない」を明記(適用済み)。
3. `OPEN_ITEMS.md`: 新規「T1(英語化Trial限定抑制追記)は Hormuz/Meta 各1セルでMAJOR Deviation、採用検討には再現性確認が必要(ユーザー判断待ち)」、新規「`a2_jt_debug.json` 誤削除・復元不可(用途不明、必要なら再生成要否をユーザー確認)」Status OPEN。OPEN-220 へ RESULT_PACKET_CC2 の追記案を追加。OPEN-217/218 へ「Trial-02 でも Deviation Check 主判定+rubric併用で評価(rubric誤判定は未観測)」を追記。
4. `docs/pm/PM_GOVERNANCE.md` 8節「SSOT編集の直列化ルール」の push競合手順の直後へ、運用補足として「委任Agentは自タスクの所有ファイル以外を削除・移動しない(`rm`/`git clean` 禁止)。未追跡ファイルは他Agent/ユーザーの作業物として扱う」を1項追記(2026-09-28、`PM-RECOVER-DELETED-UNTRACKED-FILES-01`、Fable運用補足。正式ルール化はユーザー判断待ちと明記)。

## Git

add対象: SSOT 4点+PM_GOVERNANCE+delegation_log+`_check.json`。コミット: `FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-02: Trial記録をSSOTへ反映(USER_DECISION_REQUIRED)+PM-RECOVER-DELETED-UNTRACKED-FILES-01 事後開示`、trailer `Management-ID: FAMILY-XY-CONCRETENESS-CONTROL-TRIAL-02`。`git push origin main`。

## 報告

適用箇所/新規OPEN番号/差分所有者確認/commit hash/raw URL(4 SSOT+PM_GOVERNANCE)。
