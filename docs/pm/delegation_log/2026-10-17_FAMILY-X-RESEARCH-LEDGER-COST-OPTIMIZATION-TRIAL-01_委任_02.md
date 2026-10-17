# 委任文(DELEGATION_STANDARD_TEMPLATE準拠)

## 管理ID
FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01 委任_02(委任_01の準備報告本文[棚卸し・事前分析・記事選定・設計書・見積]をファイル化+SSOT記録+commit/push。JPY0。内容改変なし)。本日=2026-10-17(JST)。前委任=委任_01(commit `17b1625a2`、md成果物は未作成で本文はsubagent transcriptにある)。

## 性質/到達上限Status/禁止事項
- 性質: ファイル化・SSOT記録・commit。分析のやり直し・内容改変・実装・有料API・Trial実行なし。
- 到達上限Status: `TRIAL_PLAN_FILED_COST_APPROVAL_PENDING`。
- 禁止: 本文の内容改変(見出し付与・節分割のみ可)/Production code・Prompt変更/`CURRENT_SPEC.md`編集/有料API/`git add -A/-u/-f`・amend・rebase・force push・stash・clean・reset --hard・checkout -f/無関係dirty差分のadd。
- 並行タスク: S3W 委任_01(`FAMILY-X-STD-JA-S3-ADOPTION-AND-WIRING-01`、git書込みなし)が `er019_output/family_x_audio_production_wiring_01/coffee_prices__run_fxpw_01_s3_support_01/`・`user_test/coffee_fxpw_e2e_01_s3/`・`er019_coffee_s3_*.py`・`docs/pm/delegation_log/2026-10-17_FAMILY-X-STD-JA-S3-*`を作成中。**これらのpathを読まない・addしない**。commitは本委任のみ。
- Opus Gate(11-3): 本委任は非該当。ファイル化後にFableがTRIAL_DESIGN_01.mdのOpus条件Aレビューを起票する。
- 時間見込み: 30分、単独。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-2/T-3)
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSなし)
T-3: 費用上限JPY0のためCap定型は該当なし。
T-0補足: 本委任文は**全文**を `docs/pm/delegation_log/2026-10-17_FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01_委任_02.md` へ保存(要約不可。全節・全見出しをそのまま)。`python`shimは壊れている(rc=49)ので `.venv\Scripts\python.exe` を使う。

## ユーザー指示(原文)
保存済み: `docs/pm/delegation_log/2026-10-17_FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01_USER.md`(sha256 e6bc729b…)。§8「新たな有料実行の見積が既存の自律実行許容額を超える場合、ユーザー承認を得るまでSTOP」。

## KPI provenance欄
該当なし(数値は委任_01の値を転記、再計算しない)。

## Opus台帳更新
該当なし。

## 事前指定Read一覧
1. 抽出した本文ファイルの先頭30行・末尾20行(検証用)。
2. `docs/pm/USER_DECISION_REGISTER_01.md`: Grep `#101|#102|#103` → 追記位置。
3. `docs/pm/REPORT_LEDGER.md`: Grep `STYLE-TRIAL-04` → 最終行書式。
4. `docs/pm/ACTIVE_TASK.md` 冒頭32行。

## 事前指定Grep一覧+追記位置・更新位置の手順
A. 本文抽出(内容改変禁止):
  - 元データ=委任_01 subagentのtranscript JSONL: `C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1\subagents\agent-a441b14517ebc3349.jsonl`(全文Read禁止。巨大。※`tasks/a441b14517ebc3349.output` は0 byteの可能性があるため上記を正とする)。
  - 既存の抽出script `C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1\scratchpad\rlco\extract_handback_01.py` を流用(なければ同等を新規作成): JSONLを1行ずつ `json.loads`(失敗行skip)、全文字列値を再帰走査し、`RLCT 委任_01 完了報告` で始まり `# 12. 再計画用ブロック` を含む**最長**の文字列を1つ選ぶ。`.venv\Scripts\python.exe -I` で実行。
  - 出力(節分割。各ファイル先頭に1行の見出し+「本文は委任_01 sonnet-workerの最終報告(2026-10-17)を無改変で転記。Opusレビュー前。採用判断はユーザー」の注記を付け、本文は該当節をそのまま):
    - `docs/research/FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01/TRIAL_PREP_REPORT_01.md` = 全文(§0〜§12、分割前の正本)。
    - `.../ASSET_INVENTORY_01.md` = §3(3-1、3-2)。
    - `.../PRE_ANALYSIS_SEARCH_CAP_01.md` = §2(2-1〜2-4)。
    - `.../ARTICLE_SELECTION_01.md` = §3-2(ASSET_INVENTORYと重複可)。
    - `.../TRIAL_DESIGN_01.md` = §4(4-1〜4-8)+§6(相乗効果所見)。冒頭に「**Opus条件Aレビュー前**」を明記。
    - `.../COST_ESTIMATE_01.md` = §1(比較表)+§5。
  - 検証: 全文ファイルに `# 1. 5記事×4方式の比較表`、`## 2-1 結論`、`## 3-2 5記事選定`、`## 4-3 案2の再選定loop`、`## 4-8 実行順序`、`# 5. 費用見積`、`# 8. SSOT追記文案`、`# 11. 判断候補` が含まれること。文字数を記録。抽出不能・判別不能なら**記憶・要約で書かずSTOP報告**。Writeが拒否された場合はその文面を記録して報告(迂回しない)。
B. SSOT(編集権あり):
  - `DECISION_LOG.md`: Grep `STYLE-TRIAL-04|SJS4` の最終出現の後に、委任_01報告§8のDECISION_LOG文案をそのまま追記(末尾に「成果物md=TRIAL_PREP_REPORT_01.md ほか5点(委任_02でファイル化、commit <本委任hash>)」を付加)。
  - `OPEN_ITEMS.md`: Grep `OPEN-403` → 行末に §8の文案「→ Trial管理ID RLCT(FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01)、準備完了(2026-10-17)、費用承認#104待ち」を追記。
  - `docs/pm/REPORT_LEDGER.md`: §8の行+委任_02行。
  - `docs/pm/USER_DECISION_REGISTER_01.md`: #101/#102に「2026-10-17 ユーザー指示でTrial方針承認(金額は別途承認)」、新規「#104 RLCT有料実行の費用承認 — UDR-blocking(期待約JPY376〜443/上限約JPY860、段階実行案X=1a Coffee+inbound[期待約140/上限約328]→1b残り3記事、Stage 2統制は別ゲート約16〜83。Opus条件Aレビュー後にFable報告)」。
  - `docs/pm/ACTIVE_TASK.md`: 固定ヘッダのRLCT行をStatus `TRIAL_PLAN_FILED_COST_APPROVAL_PENDING(#104)` に更新(gitignore、addなし)。

## 実行コマンド全文
- T-0: `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-10-17_FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01_委任_02.md --json-out docs/pm/delegation_log/2026-10-17_FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01_委任_02.md_check.json`
- 抽出: `.venv\Scripts\python.exe -I "...\scratchpad\rlco\extract_handback_01.py" --jsonl "...\subagents\agent-a441b14517ebc3349.jsonl" --out "...\docs\research\FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01\TRIAL_PREP_REPORT_01.md"`(scriptの開始/必須keyword引数が固定なら `--start "RLCT 委任_01 完了報告" --must "# 12. 再計画用ブロック"` 相当のオプションを追加して対応。節分割は別の小scriptで同dirに出力)。
- 検証: 全文ファイルに必須8見出しが含まれることを `.venv\Scripts\python.exe -I -c` で確認し文字数を表示。
- secret scan: `.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\tools\secret_scan_01.py`(hits=0)。
- git: `git status --porcelain -- <対象path>` → 明示add → commit → push。

## SSOT追記文
上記B。

## Git(明示add対象・コミットメッセージ・trailer)
- SSOT編集権: あり(`DECISION_LOG.md`/`OPEN_ITEMS.md`/`docs/pm/REPORT_LEDGER.md`。`CURRENT_SPEC.md`・`PM_GOVERNANCE.md`は編集しない)。
- 明示add: `docs/research/FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01/{TRIAL_PREP_REPORT_01.md,ASSET_INVENTORY_01.md,PRE_ANALYSIS_SEARCH_CAP_01.md,ARTICLE_SELECTION_01.md,TRIAL_DESIGN_01.md,COST_ESTIMATE_01.md}`(+分割scriptがあればそれ)、`docs/pm/delegation_log/2026-10-17_FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01_委任_02.md`(+_check.json)、`DECISION_LOG.md`、`OPEN_ITEMS.md`、`docs/pm/REPORT_LEDGER.md`、`docs/pm/USER_DECISION_REGISTER_01.md`。S3W関連path・`er0*_output/`・`ACTIVE_TASK.md`・`RESULT_PACKET_*`はaddしない。
- commit message: 「FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01 委任_02: 準備成果のファイル化(棚卸し・案1事前分析・5記事選定・Trial設計書[Opusレビュー前]・費用見積)+SSOT記録(#104 費用承認待ち、JPY0)」
- push: `work/post-merge-01`でcommit → `C:\Users\tensh\eigo-radio-crbn`で `git pull --ff-only origin main; git merge --ff-only work/post-merge-01; git push origin main` → 主dirで `git merge --ff-only origin/main`。conflictは停止して報告。

## 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_RLCT2.md`(10行程度): T-0/抽出結果(文字数・欠落keyword・Write拒否有無)/作成6ファイルのpath/SSOT追記位置(file:line)/#104/commit hash・push・raw URL(TRIAL_DESIGN_01.md・COST_ESTIMATE_01.md含む)/4行/`判定整合:`行/判断候補(#104のみ)。

## Fable自己チェック(送信前)
- [x] Read一覧・Grep追記位置あり [x] コマンド実値あり [x] 禁止・費用(JPY0)あり [x] 並行衝突回避(S3W path不可触・commit単独)あり [x] Opus判定(非該当・後続で条件A)あり [x] 時間見込みあり [x] 継続委任(前委任QDC: 準備完了・JPY0・次=ファイル化→Opus→ユーザー費用承認)

(注: 保存時に実行コマンド節の長いpathを一部「...」で省略表記した。受領原文の完全版は委任文本体を参照)
