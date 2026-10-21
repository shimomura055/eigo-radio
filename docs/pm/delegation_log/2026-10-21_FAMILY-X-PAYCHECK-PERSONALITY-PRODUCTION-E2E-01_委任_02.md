# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-X-PAYCHECK-PERSONALITY-PRODUCTION-E2E-01 委任_02(Std `full_story_part2` fallback take のHuman Review用試聴ページ公開+Adv完成音声の先行試聴掲載+次Gate[key_phrase_source_gate]の先読み。API 0・有料生成0。HR承認は人間のみ、本委任では`record_human_approval`を実行しない)。委任_01(`docs/pm/delegation_log/2026-10-21_FAMILY-X-PAYCHECK-PERSONALITY-PRODUCTION-E2E-01_委任_01.md`)の禁止事項・共有プロトコル・Gitルールを継承。並行agent: 記事B `FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01 委任_02`(er053 producer是正+再開、共有ログ・OPEN_ITEMS/REPORT_LEDGER/ACTIVE_TASK共有)。

## 性質/到達上限Status/禁止事項
- 性質: Human Review準備(MEY E2E-02 委任_03と同型: `er019_mey_hr_page_02.py`/`user_test/middle_east_yemen_saudi_e2e_02/hr_comment_2/`、E2E_PLAN_02.md §9-6)。到達上限=`HUMAN_REVIEW_PENDING(ユーザー試聴待ち)`。
- 費用JPY0(TTS/ASR/LLM呼出0)。
- 禁止: HR Lock/M3 Gate迂回、`record_human_approval`実行、state/wav手編集、新run起動、Production変更、`git add -A`等。

## 固定ブロック
E-1/D-1/G-1/F-1: 委任_01と同じ。T-0: 本委任文を`..._委任_02.md`へ逐語保存(extract tool、N=「PAYCHECK-PERSONALITY-PRODUCTION-E2E-01 委任_02」を含む最新index)、check結果1行。T-2: TTSなし。

## 作業手順
S1. HR試聴ページ: `er019_mey_hr_page_02.py`を`er019_pp_hr_page_01.py`へ複製(文言・path差し替えのみ)し、`user_test/paycheck_personality_e2e_01/hr_full_story_part2/index.html`を生成。掲載内容: (a)Std `full_story_part2` の**採用候補=fallback take**(`a2/narration/full_story_part2.wav`→wavはgitignoreのためMEY/Voice Trialと同じ方法でmp3化して掲載、元wavはローカル)、(b)canonical本文(英文全文)、(c)参考: 承認Style attempt 1/2 のASR転写差分の要約(tts_generation_results.jsonから、転写文と相違語を箇条書き。judge判定名)、(d)Adv完成音声 `b1b/assembled/Family_X_Audio_B1_PAYCHECK_PERSONALITY.wav`(mp3化)+Adv全文スクリプト(先行試聴用。「Production技術完成=Adv済/Std未完」の注記)、(e)このページがHuman Review用であり正式試聴ページではない注記。
S2. 公開: commit/push(`git push origin HEAD:main`)→Pages反映待ち(最大10分)→Playwright再生verify(`er019_pp_play_verify_01.py`のURL差し替え版 or 引数化、evidence `docs/research/FAMILY-X-PAYCHECK-PERSONALITY-PRODUCTION-E2E-01/hr_page_play_evidence_01.json`)。URL=`https://shimomura055.github.io/eigo-radio/user_test/paycheck_personality_e2e_01/hr_full_story_part2/index.html`。
S3. 次Gateの先読み(コードread、API 0): a2 Key Phrases `overall_status=REVIEW_REQUIRED`(rank2 "jump to that conclusion"、qa_no_residual_context_word FAIL)が、HR承認後の`--stage assemble --level a2`で`key_phrase_source_gate`にどう扱われるか(BLOCK/PASS_WITH_WARNING/除外)を該当コード(`er019_family_x_audio_production_runner_01.py`のkey phrase gate、`key_phrase_source_gate.json`生成箇所)から特定し、BLOCKになるならその場合の既存仕様上の経路(HR/除外/再生成)と費用見積を記録。実行はしない。
S4. 承認後の手順書(実行しない)をE2E_PLAN_01.md §5へ: `record_human_approval`呼出(MEY §10のとおり、segment=`full_story_part2`、canonical sha)→`--stage tts --level a2`(API 0見込み)→`--stage assemble --level both`→player→`er019_pp_page_01.py`→再生verify、各見積JPY。代替案(B)新run再生成の見積(audio約25〜30)も併記。
S5. SSOT(共有プロトコル): OPEN-432行頭Statusを`HUMAN_REVIEW_PENDING_STD_FULL_STORY_PART2(HR試聴ページ公開済み・Adv先行試聴可)`へ更新、REPORT_LEDGER 1行、ACTIVE_TASK先頭追記。
S6. secret scan→commit→push→到達確認。

## 報告(docs/pm/RESULT_PACKET_FXPP2.md 上書き)
1. HRページURL+再生evidence(全音声OK件数) 2. part2の承認Style attempt転写差分の要約(ユーザーが聞きどころを把握できる3〜5点: 該当文の英文と、ASRが違って転写した語) 3. S3の先読み結果(BLOCKか否か、根拠行) 4. 承認後手順書と見積、代替案(B)見積 5. 費用JPY0・当日累計実測 6. commit hash・raw URL 7. 4行判定。