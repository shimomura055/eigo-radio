# 委任文(DELEGATION_STANDARD_TEMPLATE準拠)

## 管理ID
FAMILY-X-STD-JA-S3-ADOPTION-AND-WIRING-01 委任_02(Phase A成果のcommit/push・公開Pagesの到達/再生確認・SSOT記録。JPY0。Phase Bは開始しない)。本日=2026-10-17(JST)。前委任=委任_01(ローカル生成完了、git書込みなし、`docs/pm/RESULT_PACKET_S3W1.md`)。

## 性質/到達上限Status/禁止事項
- 性質: 公開・記録のみ。生成・再生成・Production変更なし。
- 到達上限Status: `PHASE_A_USER_LISTENING_PENDING`(S3 Trial評価=`VALIDATED`[機械QA全PASS・正式条件一致の意味、Production採用ではない]。正式採用判断はユーザー)。
- 禁止: 音声・ページ内容の変更/Production code・Style profile・`CURRENT_SPEC.md`の変更/Phase B着手/`git add -A/-u/-f`・amend・rebase・force push・stash・clean・reset --hard・checkout -f/無関係dirty差分のadd。**`er019_output/family_x_audio_production_wiring_01/coffee_prices__run_fxpw_01/a2/audit/key_phrase_source_gate.json` は絶対にaddしない**(委任_01で副作用により一時書換→手動復元済み。`git status`でMと出ても対象外。内容差分は `git diff --ignore-cr-at-eol` で0を確認して記録)。
- 並行タスク: なし(RLCT 委任_03はcommit `9f579283f`で完了。commitは本委任のみ)。
- Opus Gate: 非該当。
- 時間見込み: 30分(Pages反映待ち含む)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-2/T-3)
E-1: 同一task内で同一ファイルを再読しない。D-1: Grep→該当行範囲Read。G-1: git出力は最小化。F-1: transcript退避不要。
T-0: 委任文を `docs/pm/delegation_log/<管理ID>.md` へ保存し check_delegation_prompt.py を実行、結果をRESULT_PACKETへ1行記録(FAILでも継続)。
T-2: 本委任はTTSなし。T-3: 費用上限JPY0のためCap定型は該当なし。
T-0補足: 本委任文は全文を本ファイルへ保存。`python`shimは壊れている(rc=49)ので `.venv\Scripts\python.exe` を使う。

## ユーザー指示(原文)
保存済み: `docs/pm/delegation_log/2026-10-17_FAMILY-X-STD-JA-S3-ADOPTION-AND-WIRING-01_USER.md`(sha256 0a451c9d…)。§4「Phase A完了時のMandatory STOP」、§7「S3に関するTrial結果は、正式採用前にProduction仕様として記載しないこと」。

## 事前指定Read一覧
1. `docs/pm/RESULT_PACKET_S3W1.md` 全文。 2. `docs/pm/USER_DECISION_REGISTER_01.md`: Grep `#103|#104`。 3. `docs/pm/REPORT_LEDGER.md`: Grep `RLCT`。 4. `OPEN_ITEMS.md`: Grep `OPEN-404`(次=OPEN-405想定)。

## SSOT追記(要旨)
- DECISION_LOG.md末尾: 2026-10-17 S3W 委任_01/_02: ユーザー判断=Std日本語解説StyleにS3選定。Phase A: Coffee run_fxpw_01のStd Preview/Comment1〜4のみS3(sha 060c08fd…)で検証用再生成。QA 5/5 PASS、実測約JPY2.1。Production・Style profile(R2)・R2版不変。Status=PHASE_A_USER_LISTENING_PENDING。副作用記録: verify_episode_audio_validation_gateがR2のkey_phrase_source_gate.jsonのkeywords_pathを絶対パスへ書換(手動復元、Phase B留意)。
- OPEN_ITEMS.md: 新規OPEN-405(Status=PHASE_A_USER_LISTENING_PENDING、POST_USER_VALIDATION、Phase B論点(a)target_rms再計算(b)fallback未承認Style無警告経路(新fallback独断設計しない)(c)keywords_path書換副作用)。OPEN-404に「→ S3選定済み(2026-10-17)、採用判断はOPEN-405」追記。
- REPORT_LEDGER: S3W 委任_01/_02行。 USER_DECISION_REGISTER_01: #103を判断済みへ、新規#105(S3正式採用可否、UDR-blocking=Phase B開始条件、URL付き)。 ACTIVE_TASK.mdヘッダ更新。
- CURRENT_SPEC.md・PM_GOVERNANCE.mdは編集しない。

## 公開確認
push後、er019_coffee_fxpw_play_verify_06.py相当で https://shimomura055.github.io/eigo-radio/user_test/coffee_fxpw_e2e_01_s3/index.html のHTTP 200・全audio再生・console error 0を確認(最大10分待ち)→ er019_output/family_x_audio_production_wiring_01/coffee_prices__run_fxpw_01_s3_support_01/pages_play_evidence_01.json。evidenceは2つ目のcommit(直列)。引数未対応ならscratchpadに引数対応コピーを作る(scriptの定数を変更しない)。

## Git
- 明示add(commit 1): er019_coffee_s3_support_regen_01.py、er019_coffee_s3_page_01.py、...run_fxpw_01_s3_support_01/配下のjson/md/jsonl(wav除外)、user_test/coffee_fxpw_e2e_01_s3/、delegation_log 5件、DECISION_LOG.md、OPEN_ITEMS.md、docs/pm/REPORT_LEDGER.md、docs/pm/USER_DECISION_REGISTER_01.md。
- commit 1 message: 「FAMILY-X-STD-JA-S3-ADOPTION-AND-WIRING-01 委任_01/_02: Phase A Coffee限定S3差し替え(Std日本語Preview/Comment1〜4、正式条件・音量処理一致、QA 5/5 PASS、S3版試聴ページ、R2版保持、Production不変)+SSOT(ユーザー正式採用判断#105待ち、Phase B未着手)」
- commit 2 message: 「FAMILY-X-STD-JA-S3-ADOPTION-AND-WIRING-01 委任_02: 公開Pages実再生evidence」
- push: work/post-merge-01でcommit → C:\Users\tensh\eigo-radio-crbn で git pull --ff-only origin main; git merge --ff-only work/post-merge-01; git push origin main → 主dirで git merge --ff-only origin/main。conflictは停止して報告。

## 報告
docs/pm/RESULT_PACKET_S3W2.md(10行程度): T-0/公開URL・HTTP 200時刻・再生確認結果/key_phrase_source_gate.json差分0確認とadd除外/SSOT追記位置(file:line)/OPEN-405・#105/commit hash×2・push・raw URL/4行/判定整合行/判断候補(#105のみ)。
