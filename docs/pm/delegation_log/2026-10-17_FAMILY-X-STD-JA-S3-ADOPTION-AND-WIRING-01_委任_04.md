# 委任文(DELEGATION_STANDARD_TEMPLATE準拠)

## 管理ID
FAMILY-X-STD-JA-S3-ADOPTION-AND-WIRING-01 委任_04(Phase B続き: 正式Production経路でのS3 runtime evidence取得=新out_dirでCoffee Standard[a2]をscaffold→tts→assemble→playerまで実走、公開、SSOT、commit)。本日=2026-10-17(JST)。前委任=委任_03(commit `11024c0e5`、配線・test完了、T-2(4)で有料実行前にSTOP)。

## Fable判断(委任_03のSTOPに対して)
- 委任_03の判断候補「案1: 新out_dirでStandardを全再生成(約JPY10〜14、上限21.4)」を採用(Fable権限内: 7-7の100円未満、Guardrail 40内。Store再利用前提は私の委任文の誤りで、正式初回経路の証拠として全再生成が正当)。案2(R2 resultsのseed)は不採用。
- 本日累計約JPY44 → 実行後約54〜58見込み(日次1,000内)。

## 性質/到達上限Status/禁止事項
- 性質: 正式Production runnerの実走(有料: Gemini TTS Std一式+ASR+KP scaffold LLM)+公開+記録。コード変更なし。
- 到達上限Status: `S3_WIRED_EVIDENCE_RECORDED_PENDING_FABLE`(PRODUCTION_WIRED判定はFable)。
- 費用上限(T-3): 上限JPY40(Guardrail)。見積=委任_03 `COST_ESTIMATE_01.md`(期待10〜14/上限21.4)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。
- 禁止: Production code・Prompt・Style profile変更/CLIでのStyle・backend個別指定(既定profile自動適用の実証)/R2 run(`coffee_prices__run_fxpw_01`)・Phase A dir・Master Store R2 keyへの書込み/Advanced(b1b)の実行(S3非対象、費用節約)/HR Lock・M3・Audio Validation Gateの迂回(`record_human_approval`を自分で実行しない)/有料runの原因不明再起動(26節: rc≠0原因不明2回でSTOP)/Family A互換ファイル変更/`git add -A/-u/-f`・amend・rebase・force push・stash・clean・reset --hard・checkout -f/無関係dirty差分のadd(特に `coffee_prices__run_fxpw_01/a2/audit/key_phrase_source_gate.json`、Master Store `manifest.json`)。
- STOP条件: M3 `BLOCKED_STYLE_PROFILE_GATE`(特に `JA_FALLBACK_USED_OR_UNKNOWN`=S3非適用)/gloss HR到達/AUW NG→HR/`STOPPED` segment/承認内容と実送信Style shaの不一致/R2 run配下の変更検知/費用Guardrail超過の暴走疑い。STOP時は最終成果物pathと状態を報告し迂回しない。
- 並行タスク: RLCT 委任_04(harness実装、git書込みなし、`er082_*`・`er082_output/`・`docs/research/FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01/`・同delegation_logを作成中)。これらに触れない・addしない。commitは本委任のみ。
- Opus Gate: 非該当(委任_03で判定済み。③は既存M3 BLOCKで担保、ロジック変更なし)。
- 時間見込み: 実走30〜40分/公開・確認15分/SSOT・commit 20分 ≒ 1.5時間。単独。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-2/T-3)
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、恒久運用): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続、記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ。
T-2追記(2026-09-25、`NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02`、PM_GOVERNANCE.md 7-5): TTSを伴う委任は実行前に(1)差分再生成が可能か確認、(2)既存の音声再利用キャッシュの有無を確認、(3)`--budget`/`--budget-jpy`等をタスク固有の承認上限に合わせて明示、(4)想定外の全再生成と判明した場合はAPI実行前にSTOPし報告、の4点を必須とする。(本委任: (1)(2)は委任_03で確認済み=新out_dirは全再生成が仕様、(3)`--budget-jpy 40`、(4)全再生成はFableが承認済み=想定内。これを記録して実行してよい。)
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`): 費用上限[Cap]は暴走防止のGuardrailであり、Cap到達=自動STOPではない(上記「費用上限(T-3)」の定型文に従う)。既存7-5(4)は「暴走疑い時のSTOP」に該当する条件として維持。ユーザー承認済みの総予算・個別run上限・STOP条件を優先し、Fable/Workerが独自に過度に厳しい停止条件を追加しない(2026-10-05)。
T-0補足(厳守): 本委任文は全文を `docs/pm/delegation_log/2026-10-17_FAMILY-X-STD-JA-S3-ADOPTION-AND-WIRING-01_委任_04.md` へ保存。`python`shimは壊れている(rc=49)ので `.venv\Scripts\python.exe` を使う。

## ユーザー指示(原文)
保存済み: `docs/pm/delegation_log/2026-10-17_FAMILY-X-STD-JA-S3-ADOPTION-AND-WIRING-01_PHASE-B_USER.md`(sha256 2d79e61f…)。§5「正式Production経路でS3が実際に発火したことを確認する」、§6、§9。

## KPI provenance欄(24節)
全evidence=`production_formal_path`(fresh)。E2E自己確認: Yes(Std側、既定profile、CLI個別指定なし)。

## Opus台帳更新
該当なし。

## 事前指定Read一覧
1. `er019_output/family_x_audio_production_wiring_01/coffee_prices__run_fxpw_01_s3prod/COST_ESTIMATE_01.md` 全文。同dir `entry_point.json`・`audit/style_profile.json`(plan済み状態の確認)。
2. `docs/pm/RESULT_PACKET_S3W3.md` 全文。
3. `er019_coffee_fxpw_page_06.py`(Grep `def |argparse|add_argument`)と `er019_coffee_fxpw_play_verify_06.py`(引数)。

## 事前指定Grep一覧+追記位置・更新位置の手順
- 実走前: R2 run integrityのbefore再取得(`audit/r2_run_integrity_before_02.json`、委任_03と同手順207ファイル)、Master Store `manifest.json` sha記録、STOPセンチネル確認。
- 実走(同一out_dir、`--level a2`、CLIでStyle/backend指定なし、`TTS_EXECUTION_MODE=STANDARD`): scaffold → tts → assemble → player(COST_ESTIMATE_01.mdのコマンド全文どおり)。各stage rc=0を確認、stage logを `run_fxpw_01_s3prod_stage_*.log` へ保存。
- evidence(`audit/` 配下): `e2e_segment_style_table_s3prod.json`(SUPPORT_JA 5行=style_instruction_id/version/expected_base_sha=`060c08fd…`/style_base_sha/instruction_path/fallback_used=false/AUW判定/retry)、`tts_generation_results.json`、`gain_report`(Preview無加工・Comment RMS方式=R2 runと同方式であることを確認し `gain_method_compare_01.json`)、`style_profile_gate.json`(PASS必須、`JA_FALLBACK_USED_OR_UNKNOWN`なし)、AUW/ASR結果集計、`cost.json`/`raw_usage_log.jsonl`→`cost_by_stage_s3prod_01.json`、`reuse_telemetry`(固定shell・K2のStore再利用件数)、実送信Style全文sha(runnerの記録、無ければ`style_profile.json`のsha+segment tableの一致で代替し「送信全文の直接記録なし」と明記)、`response.model`/voice。
- 実走後: R2 run integrity after(一致必須。不一致=即STOP報告)、Master Store manifestのR2 key不変+新規書込み内容(あれば列挙; S3はStore対象外のはず)。
- ページ: `user_test/coffee_fxpw_e2e_01_s3prod/index.html`(「Coffee Standard 正式Production版(S3配線後の正式経路で生成、2026-10-17)」、Std通し+各section再生、Advは `../coffee_fxpw_e2e_01/index.html#adv` へリンク、QA結果・profile・Style sha表示)。commit/push後にPages HTTP 200・全audio再生・console error 0(最大10分待ち)→ `audit/pages_play_evidence_s3prod_01.json`(2つ目のcommit)。
- SSOT(編集権あり): `CURRENT_SPEC.md`(委任_03で追加したS3記載のStatus行を `S3_WIRED_EVIDENCE_RECORDED_PENDING_FABLE`+evidence pathへ更新。PRODUCTION_WIREDとは書かない)、`DECISION_LOG.md`(委任_04記録)、`OPEN_ITEMS.md`(OPEN-405: ②gain方式一致の確認結果を追記)、`docs/pm/REPORT_LEDGER.md` 行、`docs/pm/ACTIVE_TASK.md`(addなし)。

## 実行コマンド全文
- 事前: `git status --porcelain | head -40`、`git log --oneline -1`(HEAD=`11024c0e5`)、`.venv\Scripts\python.exe tools/stop_scope_check_01.py --managed-id FAMILY-X-STD-JA-S3-ADOPTION-AND-WIRING-01 --run-dir er019_output/family_x_audio_production_wiring_01/coffee_prices__run_fxpw_01_s3prod`(rc=3なら中止)。
- T-0: `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-10-17_FAMILY-X-STD-JA-S3-ADOPTION-AND-WIRING-01_委任_04.md --json-out docs/pm/delegation_log/2026-10-17_FAMILY-X-STD-JA-S3-ADOPTION-AND-WIRING-01_委任_04.md_check.json`
- 実走(`TTS_EXECUTION_MODE=STANDARD`):
  - `.venv\Scripts\python.exe er019_family_x_audio_production_runner_01.py --slug coffee_prices --run run_fxpw_01 --out-dir er019_output/family_x_audio_production_wiring_01/coffee_prices__run_fxpw_01_s3prod --level a2 --stage scaffold --budget-jpy 40`
  - 同 `--stage tts --budget-jpy 40`
  - 同 `--stage assemble`
  - 同 `--stage player`
- secret scan: `.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\tools\secret_scan_01.py`(hits=0)
- Pages確認: `.venv\Scripts\python.exe er019_coffee_fxpw_play_verify_06.py --url https://shimomura055.github.io/eigo-radio/user_test/coffee_fxpw_e2e_01_s3prod/index.html --out er019_output/family_x_audio_production_wiring_01/coffee_prices__run_fxpw_01_s3prod/audit/pages_play_evidence_s3prod_01.json`(引数非対応ならscratchpadに引数対応コピーを作成、原scriptは不変)

## SSOT追記文
上記のとおり(実値で埋める)。

## Git(明示add対象・コミットメッセージ・trailer)
- SSOT編集権: あり(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`/`docs/pm/REPORT_LEDGER.md`)。
- 明示add(commit 1): 新run dirの記録(json/md/jsonl/log、wav除外)、`user_test/coffee_fxpw_e2e_01_s3prod/`(index.html+mp3)、本delegation_log(+_check.json)、SSOT 3件、`docs/pm/REPORT_LEDGER.md`。commit 2: pages evidence。RLCT関連・R2 run・Master Store manifest・`RESULT_PACKET_*`・`ACTIVE_TASK.md`はaddしない。
- commit 1 message: 「FAMILY-X-STD-JA-S3-ADOPTION-AND-WIRING-01 委任_04: 正式Production経路でのS3 runtime evidence(Coffee Std 新run、既定profile fx_20261017自動適用、SUPPORT_JA 5 segment S3発火、AUW/ASR、M3 PASS、R2 run保全)+正式版Stdページ+SSOT(Fable PRODUCTION_WIRED判定待ち)」
- push: `work/post-merge-01`でcommit → `C:\Users\tensh\eigo-radio-crbn`で `git pull --ff-only origin main; git merge --ff-only work/post-merge-01; git push origin main` → 主dirで `git merge --ff-only origin/main`。conflictは停止して報告。

## 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_S3W4.md`(20行程度): T-0/各stage rc・retry・fallback・HR有無/profile選択証拠/SUPPORT_JA 5行の表/`style_profile_gate.json` status/gain方式一致/Store再利用件数・新規生成件数/R2 run integrity一致・Master Store保全/費用/公開URL・HTTP 200時刻・再生確認/SSOT位置/commit hash×2・push・raw URL/4行/`判定整合:`行/判断候補/使用モデル。

## Fable自己チェック(送信前)
全項目チェック済み(Read一覧・コマンド実値・禁止・費用上限JPY40・並行衝突回避・Opus Gate非該当・時間見込み・継続委任)。
