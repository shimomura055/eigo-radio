# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01 委任_08(Phase 3続き: Fable許可によるStd `full_story_part3_c1`の`--only-clips`再実行(1回)→OKなら残工程(provision_shell→gate→assemble→pages→page_verify)→evidence補完→標準フォーマット試聴ページ更新→SSOT。**有料、本件枠JPY80の残33.86内**)。日付: 2026-10-19(JST)。

## 性質・到達上限Status・禁止事項
- 性質: 委任_07の継続。runner設計上の正規手段(`FamilyZTtsClipFailedStop`メッセージ記載「承認または --only-clips で当該clipのみ再実行」)による当該clipのみの再実行をFableが1回許可。
- 到達上限Status: `PHASE3_E2E_COMPLETE_EVIDENCE_RECORDED_PENDING_FABLE`。PRODUCTION_WIREDはFable判定、聴感PASSはユーザー試聴前に扱わない。
- 禁止: `--only-clips`再実行は**1回のみ**(再度NG/STOPPEDなら再試行せずSTOP報告=HR人手判断はユーザー)/HR Lock・review_lock・ASR判定・Gateの迂回・手動承認(`human_approved_segments`への書込み禁止)/累計JPY80超過見込みでの続行/他clipの再生成/run_e2e_01〜03の起動/Production code・Prompt・Style・Voice変更/本文再生成/`ledger.json`のcommit/`user_test/family_z_melos_01`の変更。
- 固定ブロック: **E-1**(委任_07のPHASE3_RUN_E2E_04_RECORD_01・RESULT_PACKET_FZQI7、OPUS_REVIEW_E F6-2、ユーザー試聴ページ標準フォーマット)/**D-1**(不適用)/**G-1**(変更ファイルのみ明示add、`git add -A/-u/-f`・amend・rebase・force push・stash・clean・reset --hard・checkout -f禁止、secret_scan hits=0後commit、push=`C:\Users\tensh\eigo-radio-crbn`で`git pull --ff-only; git merge --ff-only work/post-merge-01; git push origin main`、戻って`git merge --ff-only origin/main`。SSOTは自分の変更行のみstaged blob)/**F-1**(`run_e2e_04/cost_log.jsonl`実測、`cost_by_stage_04.json`を更新。本件枠80に対する累計(委任_07 46.14+本委任))/**T-0**(本委任文を全文そのまま`C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01_委任_08.md`へ保存し`check_delegation_prompt.py --file <path> --json-out <path>_check.json`実行)/**T-2・T-3**(報告=`C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_FZQI8.md`、ACTIVE_TASK.md先頭へ自分のブロックのみEdit追記)。

## Fable決定(記録用)
- Std `full_story_part3_c1`(「Melos drank」固有名の誤読でNG_BOTH→HR Lock)について、runnerが設計上提供する正規手段`--only-clips full_story_part3_c1`での再実行を**1回**許可(26節の禁止対象=実行層の自動再起動・ループではなく、Fable明示許可の単発再実行。HR Lockの迂回ではなく、同一ASR/AUW経路で再判定させるもの)。再実行でもOKにならなければSTOPし、ユーザーへHR判断(当該clipの音声・ASR結果・候補)を提示する。
- 固有名「Melos」誤読は確率的(attempt間で読みが変化)=OPEN-318/M1 Ledger(`ec716e185835dba3`)の既知領域。今回は新規の仕様変更・Ledger編集は行わない(観測を記録)。

## 事前指定Read一覧
- `C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_FZQI7.md`・`docs\research\FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01\PHASE3_RUN_E2E_04_RECORD_01.md`
- `C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_e2e_04\a2\audit\{tts_generation_results.json(segments.full_story_part3_c1), review_lock_state.json}`
- `C:\Users\tensh\eigo-radio\er026_family_z_fiction_production_runner_01.py` L1517-1533(stage_tts/only_clips)・stage_provision_shell以降・stage_pages/page_verify
- `C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_FZ19.md`(標準フォーマットページ生成・check・公開検証の手順)

## 事前指定Grep一覧+追記位置・更新位置の手順
- `CURRENT_SPEC.md`: Grep `OPEN-419|2026-10-19`(Family Z節①〜④)→「runtime evidence取得済み(run_e2e_04、commit)・Fable判定待ち」を追記。共通Status表にKP日本語意味(人称整合)行がなければ「X/Z共通module: Z=runtime evidence済み/X=コード配線(STOPのみ)・runtime待ち」を追加。
- `OPEN_ITEMS.md`: Grep `OPEN-419`→Phase 3結果・費用・HR Lock経緯(1回再実行)・試聴URL。Grep `OPEN-318`→「run_e2e_04 part3_c1 Melos誤読(確率的)」観測を1行。
- `DECISION_LOG.md`: 末尾に委任_08エントリ(Fable許可の根拠含む)。
- `docs/pm/USER_DECISION_REGISTER_01.md`: Grep `#23`→「改善版(run_e2e_04)提示、試聴待ち」。
- `docs/pm/REPORT_LEDGER.md`: 末尾1行。
- `PHASE3_RUN_E2E_04_RECORD_01.md`: 続き(再実行結果・残工程・evidence補完・費用更新)。

## 作業(順序)
A. T-0。stop_scope_check(run_e2e_04)rc=0確認。当日費用照合。
B. 再実行(1回、foreground、`TTS_EXECUTION_MODE=STANDARD`): `--stage tts_a2 --only-clips full_story_part3_c1`。結果OKなら C へ。STOPPED/NGなら: 当該clipの全attemptのASR結果・採用候補・音声path(attempts配下)・M1判定内訳をまとめ、残工程を実行せずSTOP報告(判断候補[D]=HR人手判断)。
C. 残工程: `--stage provision_shell`→`gate`→`assemble`→`pages`→`page_verify`(runnerの`--stage all`が完了済みstageをreuseして続行できるなら`--stage all`1回でも可。いずれも起動は必要最小限、各起動前にdry-run不要)。HR Lock等で停止したら迂回せずSTOP報告。
D. evidence補完(JPY0): ②新旧対照表(Preview/Comment1〜3全文、run_e2e_03 vs 04)+F3-2照合材料(Comment1「メロスが友人に何を約束し、そのあとどう行動するのか」に対応するPart1該当文の抜粋、Comment2/3も同様)/③Dialogue clipへのPD06適用0の明示確認(style tableでDialogue 21 clipのstyle sha≠PD06 sha)/④語数WARN 0(gate/validatorログ)と新prompt.txtに「400」含有/Style表(`segment_style_table_04.json`: exp_match true/false、Dialogue=Adv同一sha)/`style_record.json` NEW_RUN/Voice 21/21/AUW・6%減速23 clip比率/PASS_WITH_WARNING一覧/HR Lock最終状態(RESOLVED)。
E. 試聴ページ: `user_test/family_z_melos_02/`を標準フォーマットで更新(pages stage出力)→標準適合check→commit/push→公開URL実再生(通し再生・シーク・audio数・console error 0)→`pages_play_evidence_04.json`。
F. 費用更新(`cost_by_stage_04.json`再生成、合計/80)。Regression再実行(er062/er026/er063/er003 gloss系)。SSOT→commit→push。

## 実行コマンド全文(作業dir=`C:\Users\tensh\eigo-radio`)
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01_委任_08.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01_委任_08.md_check.json`
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\tools\stop_scope_check_01.py --managed-id FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01 --managed-id FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01 --run-dir C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_e2e_04 --out C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_e2e_04\stop_scope_check_fzqi8.json`
- 再実行(PowerShell): `$env:TTS_EXECUTION_MODE="STANDARD"; C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er026_family_z_fiction_production_runner_01.py --run run_e2e_04 --mode real --stage tts_a2 --only-clips full_story_part3_c1 --approved-budget-jpy 80 --tts-execution-mode STANDARD 2>&1 | Tee-Object -FilePath C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_e2e_04\run_08_onlyclip_console.log`
- 残工程(PowerShell): `$env:TTS_EXECUTION_MODE="STANDARD"; C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe C:\Users\tensh\eigo-radio\er026_family_z_fiction_production_runner_01.py --run run_e2e_04 --mode real --stage all --approved-budget-jpy 80 --tts-execution-mode STANDARD 2>&1 | Tee-Object -FilePath C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_e2e_04\run_08_rest_console.log`(`--stage all`が既完了stageをreuseしない実装なら、`--stage provision_shell`/`gate`/`assemble`/`pages`/`page_verify`を個別に順次実行し、各consoleを`run_08_<stage>_console.log`へ)
- 費用: `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\er026_fz_cost_17.py --run-dir C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_e2e_04 --out C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_e2e_04\audit\cost_by_stage_04.json`
- Style表: `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\er026_fz_style_table_17.py --run-dir C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_e2e_04 --out C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_e2e_04\audit\segment_style_table_04.json`
- 標準適合check: `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\tools\user_test_page_standard_check_01.py --page C:\Users\tensh\eigo-radio\user_test\family_z_melos_02\index.html --out C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_e2e_04\audit\page_standard_check_04.json`
- Pages実再生: `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\er026_fz_play_verify_19.py --url https://shimomura055.github.io/eigo-radio/user_test/family_z_melos_02/index.html --out C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_e2e_04\audit\pages_play_evidence_04.json`
- 回帰: `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I -m pytest C:\Users\tensh\eigo-radio\er062_family_z_writer_01_test_01.py C:\Users\tensh\eigo-radio\er026_family_z_fiction_production_runner_01_test.py C:\Users\tensh\eigo-radio\er026_family_z_e2e_integration_test_01.py C:\Users\tensh\eigo-radio\er003_test_kp_gloss_person_alignment.py C:\Users\tensh\eigo-radio\er063_family_z_audio_01_test_01.py -q`
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\tools\secret_scan_01.py --staged`(実在script名に置換)

## SSOT追記文(要点)
- CURRENT_SPEC(①〜④): runtime evidence(run_e2e_04)取得・Fable判定待ち。
- OPEN-419: Phase 3完了事実(費用x/80、HR Lock→Fable許可の1回再実行→結果、evidence path、試聴URL)。OPEN-318: 観測1行。REGISTER #23: 改善版提示・試聴待ち。

## Git(明示add対象・コミットメッセージ・trailer)
- commit 1: delegation_log 委任_08+_check.json、run_e2e_04追跡対象(更新分)、`user_test/family_z_melos_02/**`、audit json、PHASE3記録。msg: `FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01 委任_08: run_e2e_04 Std part3_c1 --only-clips再実行(Fable許可1回)→残工程(gate/assemble/pages)完走+evidence補完(①〜④)+標準フォーマット試聴ページ更新(JPY x/80)`
- commit 2: SSOT。msg: `FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01 委任_08: SSOT(runtime evidence・費用・#23試聴待ち、PRODUCTION_WIRED未宣言)`

## 報告(RESULT_PACKET項目: `C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_FZQI8.md`)
ユーザー§6の順で事実のみ: (1)4項目の到達状態(2)①修復結果(3)②前後対照全文+F3-2照合材料(4)③Dialogue sha/比率/長さ/PD06適用0(5)④reuse・WARN 0・prompt 400(6)費用(stage別・累計/80・所要時間)(7)Git/SSOT/evidence path(8)試聴URL・未解決(part3_c1再実行の結果とHR状態を明記)。4行+`判定整合:`+`判断候補:`。T-0 check。自己チェック: 再実行1回のみ/手動承認なし/Gate迂回なし/累計≤80/本文再生成なし/PRODUCTION_WIRED・聴感PASS未記載。
