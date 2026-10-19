# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01 委任_09(HR Lock中のStd `full_story_part3_c1`について、ユーザーのHuman Review用ページ(3 attemptの音声+本文+ASR結果)をGitHub Pagesへ公開し、USER_DECISION_REQUIRED(#116)を記録。**JPY0、有料実行0、Lock操作なし**)。日付: 2026-10-19(JST)。

## 性質・到達上限Status・禁止事項
- 性質: HR判断材料の提示ページ生成・公開+SSOT記録。
- 到達上限Status: `PHASE3_HR_LOCK_USER_DECISION_REQUIRED(#116)`。
- 禁止: `review_lock_state`・`human_approved_segments`への書込み(Lock解除・承認は人間のみ)/TTS・ASR・LLM呼出/run_e2e_04の成果物変更(読み取りとmp3変換コピーのみ)/`user_test/family_z_melos_02`・`melos_01`の変更/Production code変更。
- 固定ブロック: E-1(既存ツール`tools/build_family_z_hr_review_page.py`を優先使用。出力先既定はmelos_02に一本化済みのため、本件は`--out`等で別dir `user_test/family_z_melos_hr_run04/`へ。無ければ最小のHTMLを生成)/D-1(不適用)/G-1(変更ファイルのみ明示add、禁止操作同前、secret_scan hits=0後commit、push=`C:\Users\tensh\eigo-radio-crbn`で`git pull --ff-only; git merge --ff-only work/post-merge-01; git push origin main`、戻って`git merge --ff-only origin/main`)/F-1(JPY0)/T-0(本委任文を全文そのまま`C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01_委任_09.md`へ保存し`check_delegation_prompt.py --file <path> --json-out <path>_check.json`実行)/T-2・T-3(報告=`C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_FZQI9.md`、ACTIVE_TASK.md先頭へ自分のブロックのみEdit追記)。

## 事前指定Read一覧
- `C:\Users\tensh\eigo-radio\tools\build_family_z_hr_review_page.py`(usage)
- `C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_e2e_04\a2\audit\review_lock_state.json`、`tts_generation_results.json`(segments.full_story_part3_c1: 各attemptのASR primary/secondary、判定、path)
- `C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_e2e_04\a2\narration\attempts\full_story_part3_c1_attempt{1,2,3}_*.wav`、`.../a2/narration/full_story_part3_c1.wav`
- 参考: run_e2e_03の同clip(`run_e2e_03/a2/narration/full_story_part3_c1.wav`とそのASR結果)=前回版との比較用に併記

## 事前指定Grep一覧+追記位置・更新位置の手順
- `docs/pm/USER_DECISION_REGISTER_01.md`: Grep `#115`→直後に`#116(UDR-blocking 2026-10-19) run_e2e_04 Std part3_c1 HR判断: (a)attempt1/2/3のいずれかを承認 (b)全却下→再生成をFable許可で最大2回(見込みJPY2〜5) (c)保留`を追加。
- `OPEN_ITEMS.md`: Grep `OPEN-419`→HR Lock・#116・HRページURLを追記。
- `DECISION_LOG.md`: 末尾1行。`docs/pm/REPORT_LEDGER.md`: 末尾1行。

## 作業
1. T-0。2. 3 attempt+採用候補+run_e2e_03版をmp3へ変換(ffmpeg、ローカル無料)し`user_test/family_z_melos_hr_run04/audio/`へ。3. HRページ`user_test/family_z_melos_hr_run04/index.html`: 対象文(本文該当文を明示、「Melos drank …」)、各attemptの再生ボタン+primary/secondary ASRテキスト+判定、run_e2e_03版の再生ボタン、判断の選択肢(a)(b)(c)の説明(ページ上では選択操作なし=回答はチャットで)。内部ID等は最小限。4. commit/push→公開URL HTTP 200・audio再生確認(Playwright既存scriptを流用可)。5. SSOT→commit→push。

## 実行コマンド全文(作業dir=`C:\Users\tensh\eigo-radio`)
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01_委任_09.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01_委任_09.md_check.json`
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\tools\build_family_z_hr_review_page.py --run-dir C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_e2e_04 --level a2 --clip full_story_part3_c1 --out C:\Users\tensh\eigo-radio\user_test\family_z_melos_hr_run04`(引数は実装usageに合わせて置換。非対応なら最小HTMLを自作)
- `ffmpeg -y -i <wav> -codec:a libmp3lame -q:a 4 <mp3>`(各ファイル)
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\er026_fz_play_verify_19.py --url https://shimomura055.github.io/eigo-radio/user_test/family_z_melos_hr_run04/index.html --out C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_e2e_04\audit\hr_page_play_evidence_09.json`(scriptが標準フォーマット前提で失敗する場合はHTTP 200+audio要素数の簡易確認で可)
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\tools\secret_scan_01.py --staged`(実在script名に置換)

## SSOT追記文(要点)
- REGISTER #116(UDR-blocking)、OPEN-419(HR Lock・URL)、DECISION_LOG(STOP理由=HR Lock、Lock操作なし)。

## Git(明示add対象・コミットメッセージ・trailer)
- commit: delegation_log 委任_09+_check.json、`user_test/family_z_melos_hr_run04/**`、evidence json、REGISTER、OPEN_ITEMS、DECISION_LOG、REPORT_LEDGER。msg: `FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01 委任_09: run_e2e_04 Std part3_c1 HR Lock用のユーザーReviewページ公開(3 attempt+前回版、ASR結果)+#116 USER_DECISION_REQUIRED記録(JPY0、Lock操作なし)`

## 報告(RESULT_PACKET項目: `C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_FZQI9.md`)
4行(整合/到達経路=変更なし/成果物: HRページURL・attempt別ASR表・commit sha/撤去残置)。`判定整合:`・`判断候補:`・T-0 check・自己チェック(Lock未操作/有料0/melos_02不変)。
