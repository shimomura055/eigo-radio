## 管理ID

PM-SSOT-SYNC-13(OPEN-527 Closeout反映+OPEN-540 DESIGN_READY+OPEN-537/539のユーザー緊急指示反映+ACTIVE_TASK更新。API 0・JPY0)。並行Agent: FAMILY-Y-STYLE-PROFILE-FIX-01 委任_01(read-only設計)、FAMILY-Y-HR-APPROVAL-VOICE-GUARD-01(er121_family_y_audio_01.py編集)、opus-consultant(TTS統一レビュー、read-only)。**SSOT編集権は本委任のみ**(8-Y直列化)。所有=`OPEN_ITEMS.md`・`CURRENT_SPEC.md`・`DECISION_LOG.md`・`docs/pm/USER_DECISION_REGISTER_01.md`・`docs/pm/ACTIVE_TASK.md`・`docs/pm/delegation_log/2026-10-26_PM-SSOT-SYNC-13_DELEGATION_01.md`(+check.json)・`docs/pm/RESULT_PACKET_SSOT13.md`。pathspec付きcommit。git index.lock競合は10秒待って再実行(最大3回)。

## 性質/到達上限Status/禁止事項

- 性質: SSOT同期(Fable判定の転記)。到達上限=SYNCED。
- 禁止: SSOT全文読込(Grep→該当行Read→Editのみ)、他ファイル編集、判定語の格上げ、`git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・`git checkout -- <file>`。
- worktree SSOTがHEADより古い場合: `git show HEAD:<path>`で確認し、HEAD内容を書き戻してから自分のhunkのみ追加(他Agentのstage混入回避)。
- 時間見込み: 約40分。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`): 本委任はTTSなし。
T-3: 費用なし。

T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-26_PM-SSOT-SYNC-13_DELEGATION_01.md` をN=674から順に試し、先頭が「## 管理ID」+「PM-SSOT-SYNC-13」のものを採用(`--index -1`不可)。

## Fable判定(転記内容。文案の正本=`docs/research/FAMILY-Y-CHUNK-OPEN527-CLOSEOUT-01/CLOSEOUT_01.md`、`docs/pm/RESULT_PACKET_TRU1.md` (9)。両方を読み、下記Fable判定と矛盾する箇所はFable判定を優先)

### A. OPEN-527 → CLOSED(Fable判定、2026-10-26。ユーザー指示§3「独立Open Itemを維持しない」)
OPEN_ITEMS.md L1042の行末に追記(本体は履歴として保持、Status語を`CLOSED`へ):
「**2026-10-26 Fable Closeout(PM-SSOT-SYNC-13、ユーザー指示=緊急指示§3 `docs/pm/delegation_log/2026-10-26_FAMILY-Y-STYLE-PROFILE-FIX-01_USER.md`): CLOSED。複合項目の帰結: ①Comment 2削除=PRODUCTION_WIRED(限定: 初回生成stage[導入文3 call]の確認は次のY新規記事で実施、確認先=OPEN-532 Y欄に移管)。②Voice 1ポーズ対策=OPEN-531(Puck採用、PRODUCTION_WIRED)で解決済み・CLOSED。③Y段落分割=独立管理を終了しOPEN-532(Chunk案件)へ一本化。Y本文契約(段落5固定・Voice本文1行)は承認済みで変更しない。Chunkは配線済み(`er121_family_y_audio_01.py:267,288,731`)、複数段落入力のオフライン回帰=`er121_family_y_std_chunk_test_01.py`(14件)+`er121_family_y_audio_chunk_test_01.py`+`er121_family_y_multiparagraph_regression_test_01.py`(新規7件、計330件PASS・接続0)、dev入力evidence=`CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01/EVIDENCE_01.md` §3。実記事では不発火のためPRODUCTION_WIREDとは判定しない(ユーザー決定2026-10-26)。複数段落のY記事が正式CLIで生成された時点で`docs/research/FAMILY-Y-CHUNK-OPEN527-CLOSEOUT-01/PRODUCTION_CHECK_PROCEDURE_01.md`に従いruntime evidenceを取得してFableが判定する。UDR-YFB-1(分割方式)は新規判断を立てず、本文契約変更は未承認のまま据置(ユーザー指示「検証のためだけに本文を改変しない・有料Trialをしない」)。証跡=`docs/research/FAMILY-Y-CHUNK-OPEN527-CLOSEOUT-01/{STATE_01,CLOSEOUT_01,PRODUCTION_CHECK_PROCEDURE_01}.md`、commit 47db4accf。**」
- OPEN-532(L1047)へ追記: 「2026-10-26追記(SYNC-13): OPEN-527のY分割管理を本項へ一本化。Y=WIRED_NOT_FIRING継続、複数段落回帰test(上記)で定常確認、Production確認手順書=PRODUCTION_CHECK_PROCEDURE_01.md。Comment 2削除の初回生成stage確認も次のY新規記事で本項にて記録。」
- L1035(OPEN-520内参照)の「OPEN-527」参照に「(CLOSED→OPEN-532)」を付す。
- CURRENT_SPEC.md: CLOSEOUT_01.mdのL2972 1行修正案を適用(「OPEN-527参照」→「OPEN-532参照、手順書path」)。L2981/L3096は参照だけなら「(OPEN-527はCLOSED、→OPEN-532)」を付す。
- UDR: `docs/pm/USER_DECISION_REGISTER_01.md` L411/L424/L451/L456の該当=UDR-YFB-1を「据置(新規判断を立てない。ユーザー指示2026-10-26§3)・OPEN-527 CLOSED・管理先OPEN-532」へ。UDR-YFB-2は既にOPEN-531で解決済みであることを確認(未反映なら反映)。
- DECISION_LOG.md: 1エントリ「2026-10-26 OPEN-527 Closeout(Fable判定、ユーザー指示§3)。Y Chunk=WIRED_NOT_FIRING継続、本文契約不変、管理先OPEN-532」。

### B. OPEN-540 Status更新(TTS統一)
RESULT_PACKET_TRU1.md (9)の更新案を適用: 「DESIGN_READY(委任_01完了、commit 6669925cf、Opus条件Aレビュー進行中[2026-10-26 Fable発注、論点O-1〜O-8+F-1〜F-3])。次=Opus→委任_02実装→委任_03 evidence(Lean 46case 保守約200円/天井約298円、Fable自律枠)→委任_04 Fable受入」。統合先(OPEN-376/312/536/538/528/274/389)の文案は「解消予定」表現のまま転記(解消済みと書かない)。CURRENT_SPEC新節・DECISION_LOGの本採用記述は**実装後**とし、今回は転記しない。

### C. OPEN-537(Y Style不整合)Status更新
「2026-10-26 ユーザー緊急指示(原文=`docs/pm/delegation_log/2026-10-26_FAMILY-Y-STYLE-PROFILE-FIX-01_USER.md` §1): **最優先是正**。『適用時期ユーザー判断』の分類を撤回し、Fable主導で原因究明→正しい部位別Style確定→runner是正+fail-closed Gate+受入検証への再発防止→再配達記事の影響音声再生成・再提出へ進む(FAMILY-Y-STYLE-PROFILE-FIX-01 委任_01=原因究明・設計、進行中)。Fableの反省事実: 統合調査でU-15(B・高)を把握しながら、現行runner(`default`)で完成版`_02`を制作・提出し適用時期を判断に回した。これはPM Gate上の誤り(ユーザー指摘)。」UDRの該当項(OPEN-537関連)を「ユーザー判断待ち」から「ユーザー指示により是正実施中」へ。

### D. OPEN-539(再配達試聴)更新
「2026-10-26 ユーザー緊急指示§1-C: 公開版`_02`(default Style)への試聴承認は**旧版に対する承認として記録**する。新Style反映版(`_03`予定)はユーザーの再試聴・再承認待ちとし、承認を先取りしない。」UDRの試聴承認項も同様に更新。

### E. ACTIVE_TASK.md(全面上書き)
管理ID: FAMILY-Y-STYLE-PROFILE-FIX-01(OPEN-537最優先、委任_01設計中)/ 並行: FAMILY-Y-HR-APPROVAL-VOICE-GUARD-01(OPEN-535)、TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01(Opus条件Aレビュー中)
Status: 進行中3件。OPEN-527 CLOSED(SYNC-13)
次: 537設計→Opus任意レビュー要否判断→委任_02(是正実装+再生成、見積要)→`_03`公開→ユーザー再試聴; 535 FIXED→Fable受入; 540 Opus→委任_02
STOP条件: 猿の手 run_fzcw_e1_01 のSTOP/RESTART_STORM_LOCK残置(当該run不使用)。他なし
UDR-blocking: OPEN-526・534・539(旧版承認扱い、新版待ち)。537はユーザー指示で実施中
QDC: 当日約563円/1,000(KP救済含む)。537再生成見積は委任_01で算出
報告単位Status: 537/535/540の結果待ち

## 実行コマンド全文

- `py docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-26_PM-SSOT-SYNC-13_DELEGATION_01.md --json-out docs\pm\delegation_log\2026-10-26_PM-SSOT-SYNC-13_DELEGATION_01.md_check.json`
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## Git

- add対象: `OPEN_ITEMS.md`、`CURRENT_SPEC.md`、`DECISION_LOG.md`、`docs/pm/USER_DECISION_REGISTER_01.md`、`docs/pm/delegation_log/2026-10-26_PM-SSOT-SYNC-13_DELEGATION_01.md`(+check.json)。ACTIVE_TASK/RESULT_PACKETはgitignore。pathspec付きcommit。
- commit message: `PM-SSOT-SYNC-13: OPEN-527 Closeout(Y分割→OPEN-532一本化、Comment2 WIRED限定、本文契約不変)、OPEN-540 DESIGN_READY、OPEN-537最優先是正へ、OPEN-539旧版承認扱い(API 0)`
- trailer: `Delegation: PM-SSOT-SYNC-13/01`
- push: `git push origin HEAD:main`(non-ffなら fetch→merge --no-edit→push。競合はSTOP報告)。

## 報告

`docs/pm/RESULT_PACKET_SSOT13.md`: (0)T-0、(1)編集箇所一覧(ファイル:行、追記/置換)、(2)Fable判定との差異(あれば)、(3)必須4行+「判定整合: 重大NG=<なし|あり>」、(4)commit hash・raw URL。末尾5行要約。