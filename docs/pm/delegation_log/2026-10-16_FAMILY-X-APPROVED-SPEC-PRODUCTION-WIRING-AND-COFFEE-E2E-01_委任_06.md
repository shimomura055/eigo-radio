# 委任文(DELEGATION_STANDARD_TEMPLATE準拠)

## 管理ID
FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01 委任_06(Coffee E2E: Mandatory STOP解除後の音声工程S6〜S11実走+費用・量産原価算出+受入条件自己照合+SSOT事実記録+commit/push)。前委任=CEC 委任_05(commit `4447cbbab`、text工程完了JPY72.64、構造的Mandatory STOP到達)。本日=2026-10-16(JST)。

## 性質/到達上限Status/禁止事項
- 性質: 正式Production経路での実走(有料: TTS/ASR/KP LLM)+証拠収集+記録。設計変更・Production code変更は想定しない。
- 到達上限Status: `AUDIO_E2E_COMPLETE_EVIDENCE_RECORDED_PENDING_FABLE`(PRODUCTION_WIRED判定はFableのみ。Sonnetは宣言しない。ユーザー試聴評価を勝手にPASS扱いしない)。
- ユーザー正式承認(下記原文§1): 既存run `er019_output/coffee_prices/run_fxpw_01` のMandatory STOP解除・音声化進行を承認。Research/Ledger/B3/Writer/英語記事は理由なく再生成しない。
- 費用上限(T-3): Coffee E2E全体の承認上限 JPY205(ユーザー承認値)。text実測72.64 → 音声工程の残り **JPY132.36 が絶対上限**。音声stage各コマンドは `--budget-jpy 100`(Guardrail。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時[想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理]のみSTOPし、原因・既使用額・想定追加額・残作業を報告する)。**ただし音声工程累計が132.36を超える見込みになった時点ではSTOP(ユーザー承認上限)**。音声見積は期待約28/最悪約67(`COFFEE_E2E_PLAN_01.md` §5)。日次1,000円: 本日累計は委任_05時点約JPY152。
- 禁止: 新しいPrompt/Style探索・K2 fallback方式改修(OPEN-399)・原価改善Trial・モデル変更・仕様変更・Family A/B/C・Family Z予防改修・Family Y・無関係Open Item棚卸し・Day5/6再開・Research/Writer再実行・旧Coffee run(run_l3_01/run_m2p0_n01_01等)の記事/KP/音声の流用(固定shell音声のStore再利用のみ正当、PLAN §1)。CLIでStyle/Prompt個別指定フラグを付けない(既定profile `fx_20261016` の自動適用を実証するため)。STOPセンチネル(`STOP`/`STOP_ALL`/`STOP_NOTICE`)の削除・迂回禁止。HR Lock・gloss HR・review_lock・M3 Style Gate・Audio Validation Gate・AUWの迂回禁止(`record_human_approval`を自分で実行しない)。有料runの再起動禁止(PM_GOVERNANCE 26節: 途中停止したstageを原因不明のまま再実行しない。rc≠0が原因不明で2回=STOP)。`git add -A/-u/-f`・amend・rebase・force push・stash・clean・reset --hard・checkout -f禁止。**Production code(er0XX_*.py)の編集禁止**: blockerでcode修正が必要と判断した場合は編集せずSTOPしFableへ報告(Family X配線はPRODUCTION_WIRED判定中であり、変更は証拠の前提を変える)。Family A互換ファイル(`er006_audio_cost_pilot_02_shared_narration.py`/`er006_master_audio_store_01.py`)に触れない。
- STOP条件(ユーザー§8): 既存Mandatory Human Review/品質Gate到達(gloss HR `EPISODE_BLOCKED_BY_GLOSS_ALIGNMENT` rc=2、review_lock 3回NG→HR、M3 `BLOCKED_STYLE_PROFILE_GATE`、Audio Validation Gate BLOCK、`STOPPED` segment)/承認済み仕様との重大な不一致(マトリクス照合FAIL)/音声・原稿・Styleの取り違え(三者sha不一致、role↔Style ID不整合)/205超過見込み/新Trial・仕様変更が不可欠/正式経路が使用できない(`assert_production_tts_backend`失敗等)/M2→Strategy L fallback発火/`CANONICALIZATION_INVALID`が既存retryで解決しない/OPEN-343(断片KP)再発。STOP時は最終成果物pathと中身要約を報告し、自動再試行しない。**非Blockingの確認事項(Review Queue候補、PASS_WITH_WARNING、K2 fallback発生)はSTOP理由にしない**(記録して続行)。
- 並行タスク: なし(本委任単独。index共有のためcommitは本委任のみ)。
- Opus独立技術レビューGate(11-3): 非該当(設計変更なし。配線設計は委任_02A前に条件Aレビュー済み=`OPUS_REVIEW_A_01_VERBATIM.md`。PRODUCTION_WIRED判定時はFableが同レビューを再利用する)。
- 時間見込み・並列化: S6 5分/S7 10〜15分/S8 20〜30分/S9 20〜30分/S10 5分/S11 15分(Pages反映待ち含む)/費用・照合・SSOT・commit 30分 ≒ 2〜2.5時間。S8とS9は直列(理由: Master Audio Store manifest/KP英語音声の共用stateとAUW telemetryの同一ファイル書込み競合、再現性)。費用集計scriptの準備はS8実行待ち中に先行してよい。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-2/T-3)
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。
T-2追記(2026-09-25、`NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02`、PM_GOVERNANCE.md 7-5、予算逸脱再発防止): TTSを伴う委任は実行前に(1)差分[変更箇所のみ]再生成が対象コード上で実際に可能か確認、(2)既存の音声再利用キャッシュの有無を確認、(3)`--budget`/`--budget-jpy`等が存在すればタスク固有の承認上限に合わせて明示、(4)想定外の全再生成と判明した場合はAPI実行前にSTOPし報告、の4点を必須とする。
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`、ユーザー正式決定、費用上限[Cap]を伴う全委任で常時有効): 費用上限[Cap]は「暴走防止のためのGuardrail」であり、Cap到達=自動STOPではない。禁止事項/性質欄の費用上限記載は次の定型文に従う。「上限¥X(Guardrail)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。」旧来の「上限¥X、超えそうなら実行前STOP」のみの記載(継続条件・STOP条件の書き分けが無いもの)は使用しない。既存7-5(4)「想定外の全再生成が判明したらAPI実行前にSTOP」は本T-3の「暴走疑い時のSTOP」に該当する条件として維持する(置き換えではない)。ユーザー承認済みの総予算・個別run上限・STOP条件を優先し、Fable/Workerが独自に過度に厳しい停止条件を追加しない(2026-10-05)。

T-0補足(本委任で厳守): (a)本委任文は**全文**を `docs/pm/delegation_log/2026-10-16_FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01_委任_06.md` へ保存する(要約・「同上」・見出しのみ保存は不可。過去委任で要約保存が逸脱として記録済み)。(b)下記「ユーザー指示(原文)」節は**一字一句そのまま**を `docs/pm/delegation_log/2026-10-16_FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01_AUDIO-RESUME_USER.md` へ保存し、文字数とsha256をRESULT_PACKETに記録する(文字数が約2,900〜3,300字の範囲外なら保存漏れを疑い再確認)。

## ユーザー指示(原文)
(原文は別ファイル `2026-10-16_FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01_AUDIO-RESUME_USER.md` に一字一句保存。本ファイルでは重複掲載を省略し参照とする。)
(Fable補足: 委任_05のReview Queue候補[b1b 2件・a2 2件、非Blocking]は上記§8末尾「非Blockingの確認事項を勝手に格上げしない」により、記事本文を変更せず記録のまま音声化する。)

## KPI provenance欄(PM_GOVERNANCE 24節)
- 全音声Section Style適用・AUW判定・K2 fallback件数・IOL文数・費用: `production_formal_path`(fresh、本委任の実走)。
- B3/R0/R1/R2 model_id・W-1契約・text費用72.64: `reuse`(委任_05で取得済み証拠 `run_fxpw_01/writer_run_summary.json`・`cost.json`、再計測しない)。
- 量産原価(Batch換算): 実測token量×正式価格記録(`er005_output/cost_baseline_01/pricing_snapshot.json`)の計算値=`manual_substitution`と明記。未測定部分を実測として扱わない。
- E2E自己確認: fresh Production初回pathを含むE2E値か = Yes(S1〜S11すべて正式runner)。

## Opus台帳更新(11-5)
`docs/pm/OPUS_FINDINGS_LEDGER.md` OF-FXPW-R-01〜R-12: 本委任でruntime evidenceが得られた指摘(特にR-03 IOL STOP、K2 2段Store key、M3/M4 role別判定、Std PD06+6%減速)を `IMPLEMENTED→EVIDENCED` へ更新(証拠path付き)。evidenceが得られないものは状態を変えず理由を記す。

## 事前指定Read一覧
1. `docs/research/FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01/COFFEE_E2E_PLAN_01.md` 全文(S6〜S11のコマンド・Gate・照合項目X12〜X31、§4受入条件対応、§5費用出典、§7、§8、§実行直前チェック(b))。
2. `docs/research/FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01/SPEC_WIRING_MATRIX_01.md` 全文(33行・⑩列の音声工程分をPASS/FAILで埋める)。
3. `docs/research/FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01/WIRING_DESIGN_01.md`: Grep `§B-2|§D|§F|fallback_used|instruction_path|KP_EN_ENGLISH_LOCK_FALLBACK_AUDIO_NOT_K2|slowdown` → 該当範囲のみRead(K2 Store key・M3 warning・Std減速の期待値)。
4. `er019_family_x_audio_production_runner_01.py`: Grep `add_argument|--stage|style_profile.json|style_profile_gate|pass_with_warning_listening_list|KP_EN_ENGLISH_LOCK_FALLBACK_AUDIO_NOT_K2|player|user_test|out_dir|cost.json` → 該当範囲のみRead(出力dir・各stageの成果物pathを特定)。
5. `er019_family_x_kp_en_k2_store_01.py` 全文(短い。Store keyのversion/instruction_pathの読み方)。
6. 直近のFamily X試聴ページ配置例: Glob `user_test/**/coffee*` と `user_test/*.html` → 直近Family X(例: `coffee_prices__run_m2p0_n01_01` 関連)の配置・index/Landing更新方法をGrep `run_m2p0_n01_01|coffee_prices` で特定し同じ方式に従う(新しい配布経路を作らない。正式Landing=`https://shimomura055.github.io/eigo-radio/user_test/articles_2026_0918.html`、PM_GOVERNANCE L336-345)。
7. `docs/pm/PM_GOVERNANCE.md`: Grep `^## 15|15-5|15-8|15-9` → 15節(費用5区分・1生成セット総原価・70円)の該当範囲Read。Grep `## 26|26-` → 26節の再起動禁止の範囲のみRead。
8. `er005_output/cost_baseline_01/pricing_snapshot.json` 全文(STANDARD/Batch単価の正式記録。Batch単価の記載がなければ「正式価格記録なし=未確認」として量産原価のBatch換算を「算出不可(出典なし)」と記す。推定値で埋めない)。
9. `er019_output/coffee_prices/run_fxpw_01/cost.json` 全文(text工程72.64の内訳、合算用)。
10. `docs/pm/RESULT_PACKET_CEC5.md` 全文(前委任の要約・Review Queue候補・既知未取得項目N1)。
11. `docs/research/PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01/dqi/DQI_PROSPECTIVE_OBS_01.md` 全文(#4行の追記書式確認)。
12. `tools/stop_scope_check_01.py`: Grep `argparse|add_argument|rc|return 3` → 使い方のみ。

## 事前指定Grep一覧+追記位置・更新位置の手順
- STOPセンチネル: Glob `er019_output/coffee_prices/run_fxpw_01/**/STOP*`、`er019_output/family_x_audio_production_wiring_01/**/STOP*`、root `STOP_ALL`/`STOP_NOTICE*`。1件でも存在=開始しない(報告)。
- 音声出力dir非存在確認: S6 `--stage plan` 前に、runnerが使う出力dir(Read 4で特定、想定 `er019_output/family_x_audio_production_wiring_01/coffee_prices__run_fxpw_01/`)が存在しないことを確認(存在すればSTOP報告。旧run stateを引き継がない)。
- `CURRENT_SPEC.md`: Grep `FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01` → 委任_02A/02B/04で追加した「Phase 2配線実装記録」の直後に「Phase 3 Coffee正式E2E runtime evidence(委任_05 text+委任_06 audio)」を追記(事実のみ。PRODUCTION_WIRED判定は書かない=「Fable判定待ち」)。
- `DECISION_LOG.md`: 直近エントリ(Grep `2026-10-16` の最終出現)の後に本委任エントリ(ユーザー承認=Mandatory STOP解除・音声化進行、原文保存path、実走結果要約)を追記。
- `OPEN_ITEMS.md`: Grep `OPEN-399` → Coffeeでの代替音声発生有無・件数・対象フレーズ・原因を追記(発生0でも「Coffee run_fxpw_01: 代替0件」を記録)。Grep `OPEN-343` → 再発有無を1行追記。新たな不具合はOPEN-401以降で登録(改修はしない)。
- `docs/pm/USER_DECISION_REGISTER_01.md`: Grep `FXUD-1|JPY205|Mandatory STOP` → 本承認(Mandatory STOP解除)を「判断済み」として追記、FXUD-1〜8の「runtime evidence待ち」を証拠pathで更新(PRODUCTION_WIRED判定はFable待ち)。
- `docs/pm/REPORT_LEDGER.md`: 本委任の行を追記。
- `docs/pm/OPUS_FINDINGS_LEDGER.md`: OF-FXPW-R-01〜12の状態更新(上記)。
- `docs/research/PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01/dqi/DQI_PROSPECTIVE_OBS_01.md`: #4行の骨格(対象=FXPW 委任_06、Validator結果)を追記。Fable判定列は空欄のまま(「Fable記入待ち」)。
- `docs/pm/ACTIVE_TASK.md`: 冒頭固定ヘッダを本委任用に上書き(PM_BRIEF書式、20〜32行)。既存の「前タスク群(保持)」節は残す。

## 実行コマンド全文
前提: `python` shimは壊れている(rc=49)。全て `.venv\Scripts\python.exe` を使う。PowerShellでは `$env:TTS_EXECUTION_MODE="STANDARD"` を各コマンド前に設定(Bashなら `TTS_EXECUTION_MODE=STANDARD` 前置)。作業dir=`C:\Users\tensh\eigo-radio`。

0. 事前(JPY0):
   - `git status --porcelain -- er019_output/coffee_prices/run_fxpw_01 er019_output/family_x_audio_production_wiring_01 user_test docs | head -50`、`git log --oneline -3`(HEAD=`4447cbbab`系を確認)。
   - `.venv\Scripts\python.exe tools/stop_scope_check_01.py --managed-id FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01 --run-dir er019_output/coffee_prices/run_fxpw_01`(rc=3なら中止)。
   - T-0保存2件+`.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-10-16_FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01_委任_06.md --json-out docs/pm/delegation_log/2026-10-16_FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01_委任_06.md_check.json`。
   - T-2追記4点の確認結果をRESULT_PACKETへ(差分再生成可否/再利用キャッシュ=Master Audio Store固定shellのみ想定/`--budget-jpy 100`明示/全再生成は新規runなので想定内=初回生成)。
1. S6 音声plan(JPY0): `TTS_EXECUTION_MODE=STANDARD .venv\Scripts\python.exe er019_family_x_audio_production_runner_01.py --slug coffee_prices --run run_fxpw_01 --level both --stage plan`(`--tts-backend`は**付けない**=既定`speech_metadata_flash_lite`の自動適用を実証。他のStyle/Prompt指定フラグも付けない)。確認: `audit/style_profile.json` の `profile_id==fx_20261016`、`style_profile_source==default_new_run_fx_20261016`、roles 6件sha(FULL_STORY 3a680861…/SUPPORT_JA 625826c1…/PREVIEW 8862317f…/KP_EXPLANATION_EN 05180006…/KP_EN 9d905cfe…/KP_JA_MEANING b12c8721…)、backend既定値。**1つでも不一致=STOP**(TTS開始しない)。
2. S7 scaffold: `TTS_EXECUTION_MODE=STANDARD .venv\Scripts\python.exe er019_family_x_audio_production_runner_01.py --slug coffee_prices --run run_fxpw_01 --level both --stage scaffold --budget-jpy 100`。CP-D自己照合(X12〜X16: `kp_supply=m2`、`m2_fallback=null`、KP5件両level、A方式、explanation形式、gloss HR未到達、OPEN-343再発なし)。KP一覧(used_form/gloss/explanation)とPreview/Comment textをRESULT_PACKET詳細へ。FAIL/HR=STOP。全PASSなら続行。
3. S8 TTS Adv: `TTS_EXECUTION_MODE=STANDARD .venv\Scripts\python.exe er019_family_x_audio_production_runner_01.py --slug coffee_prices --run run_fxpw_01 --level b1b --stage tts --budget-jpy 100`。
4. S9 TTS Std(S8完了後に直列): 同コマンドで `--level a2`。
5. CP-E自己照合: 全segment表(level/segment/role/style_instruction_id/version/prompt sha12/Store hit or new/`instruction_path`/AUW判定/WARNING ID/retry回数/ASR結果)。K2 fallback=`instruction_path=english_lock_fallback` または warning `KP_EN_ENGLISH_LOCK_FALLBACK_AUDIO_NOT_K2` の件数・対象フレーズ・原因(ログから)。Std Full Story `slowdown_info` ratio≒1.06+減速後ASR PASS。`pass_with_warning_listening_list.json`の一覧。HR queue未処理が1件でもあれば=STOP(assembleへ進まない)。
6. S10 assemble(JPY0): `TTS_EXECUTION_MODE=STANDARD .venv\Scripts\python.exe er019_family_x_audio_production_runner_01.py --slug coffee_prices --run run_fxpw_01 --level both --stage assemble`。`style_profile_gate.json status=PASS`を確認(BLOCK=STOP、人間承認を自分で記録しない)。
7. S11 player(JPY0): `... --stage player --level both`、Read 6で特定した既存方式で `user_test/` 配下へ配置・Landing更新。commit/push後、`curl.exe -s -o NUL -w "%{http_code}" <Pages URL>` でHTTP 200と音声ファイル取得可を確認(Pages反映は数分待ち、最大10分、1分間隔)。`file:///`・raw URLは試聴URLにしない。
8. 回帰(code変更なしの確認として最小限、JPY0): `.venv\Scripts\python.exe run_project_regression.py --pattern "er019_family_x_*_test_*.py"` と `--pattern "er081_*_test_*.py"`。FAILはOPEN-400既知分と区別して報告(新規FAILは修正せず報告)。
9. 費用: 音声run の `cost.json`/`raw_usage_log.jsonl` から stage別(scaffold[KP LLM/gloss/explanation/support text]/TTS Adv/TTS Std/ASR/retry/Azure等)を集計し、text 72.64と合算して「Coffee記事セット実測総費用」を出す。15節5区分(今回実測/Trial特有/異常retry・HR由来/Standard同期/Batch量産換算)で表にする。Batch換算は `pricing_snapshot.json` に正式Batch単価がある項目のみ、実測token量に適用(ASR・LLM等Batch対象外は実測のまま)。70円との差額、超過主因(Research+Ledger/B3/Full Story TTS等の寄与率)、改善余地は「候補の列挙のみ」(Trial・変更はしない)。本日累計(委任_05時点約152+本委任)と1,000円との関係を1行。
10. 受入条件12項目(ユーザー原指示§9、PLAN §4)の自己照合表(PASS/FAIL/未達と証拠path)。マトリクス33行⑩列を全て埋める。
11. secret scan: `.venv\Scripts\python.exe tools/secret_scan_01.py`(存在しなければ既存の同等scriptをGlob `tools/*secret*`で特定) hits=0 を確認してからcommit。

## SSOT追記文
- CURRENT_SPEC.md(Phase 2記録の直後):
  「### Phase 3 Coffee正式E2E runtime evidence(委任_05 text・委任_06 audio、2026-10-16)
  run=`er019_output/coffee_prices/run_fxpw_01`(text)+`<音声run dir>`(audio)。既定profile `fx_20261016` がCLI指定なしで適用(`audit/style_profile.json`)。Section別Style適用=<PASS n/n、表は RESULT_PACKET_FXPW6/REPORT参照>。AUW判定=<PASS/PASS_WITH_WARNING/NG件数>。K2代替音声=<n件、OPEN-399>。IOL=Adv 2文/Std 2文。費用=text 72.64+audio <x>=<total>(承認205内)。Status=`AUDIO_E2E_COMPLETE_EVIDENCE_RECORDED_PENDING_FABLE`(PRODUCTION_WIRED判定はFable、ユーザー試聴は未)。」(実値で埋める。STOPで未完の場合は到達stageと理由を書く)
- DECISION_LOG.md: 「2026-10-16 FXPW 委任_06: ユーザー正式判断=Coffee run_fxpw_01のMandatory STOP解除・音声化進行承認(原文=docs/pm/delegation_log/2026-10-16_..._AUDIO-RESUME_USER.md、sha256 <…>)。承認は既存記事の音声化のみで新仕様・Trial採用を含まない。実走結果=<要約>。PRODUCTION_WIRED判定はFable。」
- OPEN_ITEMS.md OPEN-399/OPEN-343: 上記Grep手順どおり。

## Git(明示add対象・コミットメッセージ・trailer)
- SSOT編集権: あり(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`/`docs/pm/REPORT_LEDGER.md`。`docs/pm/PM_GOVERNANCE.md`は編集しない)。
- 明示add(ファイル名を個別指定、`-A/-u`禁止): 音声run dirの証拠(json/log/manifest/md。音声ファイル[wav/mp3]は既存Family X runの慣例に従う=Read 6で確認し、Pages配布に必要なもののみ)、`user_test/`配下の新規ページ・更新Landing、`docs/pm/delegation_log/`2件(+_check.json)、`docs/research/FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01/`配下の更新(マトリクス・PLAN末尾の実走記録)、SSOT 3件、`docs/pm/USER_DECISION_REGISTER_01.md`、`docs/pm/REPORT_LEDGER.md`、`docs/pm/OPUS_FINDINGS_LEDGER.md`、`docs/pm/ACTIVE_TASK.md`、DQI台帳、`docs/pm/RESULT_PACKET_FXPW6.md`は**addしない**(gitignore一時ファイル)。無関係な既存差分(`er006_output/...`等のdirty)は絶対にaddしない。
- commit message: 「FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01 委任_06: ユーザー承認(Mandatory STOP解除)保存+Coffee正式E2E音声工程実走(S6〜S11: 既定profile fx_20261016自動適用・KP M2P0+A・PD06/K2/P8/P7/E1/R2 TTS・AUW・Assembly・試聴ページ)+工程別費用・量産原価試算+受入条件自己照合+SSOT事実記録(PRODUCTION_WIRED判定はFable待ち)」(STOPで途中終了した場合はその旨に差し替え)。
- push: `work/post-merge-01`でcommit → `C:\Users\tensh\eigo-radio-crbn`(main)で `git pull --ff-only origin main; git merge --ff-only work/post-merge-01; git push origin main` → 主dirで `git merge --ff-only origin/main`。conflict時は操作を止めて報告。
- 音声ファイルが大きい場合(合計>50MB目安)はcommit前に報告(過去慣例を優先)。

## 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_FXPW6.md`(要約20行程度、詳細は同ファイル末尾または `docs/research/.../COFFEE_E2E_PLAN_01.md` 末尾「§実走記録(委任_06)」へ):
1. T-0結果2行(委任文保存path/check PASS・FAIL理由/ユーザー原文保存path・文字数・sha256)。
2. 到達stage・Status(上限 `AUDIO_E2E_COMPLETE_EVIDENCE_RECORDED_PENDING_FABLE`)・STOP有無と理由。
3. S6 profile確認(profile_id/source/backend/6 role sha)。
4. KP一覧(5件: used_form/gloss(P8用)/explanation(P7用))、Preview/Comment text要約、M2 fallback=null確認。
5. 全segment Style適用表(level/segment/role/style_instruction_id/version/prompt sha12/Store hit・new/instruction_path/AUW判定/WARNING/retry/ASR)。
6. K2代替音声: 有無・件数・対象フレーズ・原因(0件なら「0件」+根拠path)。
7. AUW判定集計(PASS/PASS_WITH_WARNING/NG/HR件数)と`pass_with_warning_listening_list.json`の聞き取り対象。Std Full Story slowdown ratioと減速後ASR。
8. `style_profile_gate.json` status(両level)、assemble完了。
9. 試聴ページURL(GitHub Pages、HTTP 200確認時刻)、Adv/Std各URL、Landing更新有無。
10. 費用: 工程別実測(text再掲+audio各stage)/総額/残額(205-総額)/5区分表/Batch換算量産原価(出典と算出式、算出不可なら理由)/70円との差額/超過主因寄与率/改善余地(列挙のみ)/本日累計。
11. 受入条件12項目の自己照合表、マトリクス33行⑩列の結果(PASS数/FAIL数/未取得と理由)。
12. 回帰結果(PASS/FAIL、既知OPEN-400分の区別)。
13. 新規Open Item候補(登録したID)・Opus台帳更新内容・DQI #4骨格の記録。
14. 4行(①既存仕様整合[照合file:line] ②Production到達経路の未承認機能既定値 ③失敗終了時の最終成果物と目的適合 ④撤去・残置した規則の識別子)。
15. `判定整合: 重大NG=[ID…|なし] / 主因=[ID] / 是正対象=[ID…] / STOP理由=[ID…] / 提示=不可|証拠のみ|可|例外K`。
16. 判断候補(A既判断/B承認範囲内/C独立/D真に新しい、の別と根拠)。Open Itemにあるだけの事項・非Blocking確認事項は判断候補にしない。
17. commit hash・push結果・変更ファイルのraw URL一覧。
18. QDC材料(原因仮説・観測値・次の一手候補、STOPした場合)。

## Fable自己チェック(送信前)
- [x] Read一覧に行範囲/Grepパターンあり
- [x] 追記位置手順あり
- [x] コマンドに引数実値あり
- [x] 禁止事項・費用上限あり(T-3定型+ユーザー承認上限205/音声132.36)
- [x] 並行タスク衝突回避あり(単独)
- [x] Opus Gate判定あり(非該当・条件Aレビュー再利用)
- [x] 時間見込み・並列化判断あり(S8/S9直列理由明記)
- [x] 再委任ではない(新規継続委任。前委任QDC: 見込み高・本日費用約152/1,000・次=音声実走)
