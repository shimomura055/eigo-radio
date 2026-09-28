## 管理ID

KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-AUDIO-STYLE-TRIAL-03(ユーザー承認済みTrial、Trialのみ)。一時ファイル `docs/pm/ACTIVE_TASK_KA3.md` / `docs/pm/RESULT_PACKET_KA3.md`(commitしない)。並行: 別Sonnet 2件(Task 2 `er043_*`/`er043_output/`/`user_test/fixed_shell_champion_trial_02/`、Task 3 `er044_*`/`er044_output/`/`user_test/tts_variable_role_style_trial_02/`/`user_test/tts_all_role_style_trial_01/`)→ これらに触れない。本タスクの所有: 新規 `er042_key_phrase_advanced_english_explanation_audio_style_trial_03.py`(+`_test_01.py`)、`er042_output/key_phrase_advanced_english_explanation_audio_style_trial_03/`(Trial専用Master Store含む)、`user_test/kp_advanced_explanation_audio_trial_03/`、新規 `KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-AUDIO-STYLE-TRIAL-03_REPORT.md`、`docs/pm/design_key_phrase_advanced_english_explanation_audio_style_trial_03.md`、delegation_log。**Production code・正式Prompt・CURRENT_SPEC・Key Phrase選定ロジック・DB Hybrid・Production Master Audio Store(`er006_output/master_audio_store_01/`)は一切変更しない。SSOT 4点は編集権なし(文案のみ)。削除・移動・`rm`・`git clean`・stash/rebase/reset/amend/force push 禁止。未追跡ファイルは他Agent/ユーザーの作業物として扱う。push競合時は `git merge origin/main` のみ、conflictは中断報告。APIキー本文表示禁止。試聴リンクはGitHub Pages。**

## 性質/到達上限Status/禁止事項

- 性質: Trial(音声Styleのみ)。到達上限Status: `REJECTED` / `VALIDATED` / `USER_DECISION_REQUIRED`(ユーザー試聴前は `USER_DECISION_REQUIRED`、Production配線へ進まない)。
- 前提(ユーザー正式決定): Advanced Key Phrase 英語解説の **text 仕様は `APPROVED_FOR_PRODUCTION`**(KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-TRIAL-02 の B 候補5件)。ただし Production wiring は未実施。今回は音声 Style だけを比較する。
- 費用: 上限¥10(想定 5〜10 TTS call+ASR)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。
- **実行安全(前回インシデントの再発禁止)**: `--stage all` 相当の一括実行禁止。必要 segment だけ生成。**実行前に ACTIVE_TASK へ「対象 segment 一覧/想定 TTS call 数/retry 上限(既存 cascade の値)/想定費用/Guardrail」を記録してから実行**。既存音声を流用できる箇所は reuse。Bash timeout で background 化する前に短時間単位で分割実行。
- 禁止: Phrase・英語解説文の再生成・再選定(Hormuz 既存 5 Phrase と TRIAL-02 の B 解説文を逐語使用)、Key Phrase 選定ロジック/DB Hybrid/Production Master Store の変更、新規 Role 名の新設、Style 文言の省略表記(ページには **実際に TTS へ渡した Style Prompt 全文** を表示)。ユーザー向け表記は Standard/Advanced、TTS実行は 同期実行/バッチ実行。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない。D-1: Grep→該当行範囲Read(全文Readは `er041_*` script の構造確認時のみ可)。G-1: git出力最小化。F-1: transcript退避不要。
T-0: 本委任文を `docs/pm/delegation_log/2026-09-28_KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-AUDIO-STYLE-TRIAL-03_01.md` へ逐語保存し、`.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-28_KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-AUDIO-STYLE-TRIAL-03_01.md --json-out docs/pm/delegation_log/2026-09-28_KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-AUDIO-STYLE-TRIAL-03_01.md_check.json` を実行し結果1行記録。
T-2: `TTS_EXECUTION_MODE=STANDARD` を明示、Trial専用Store(`er042_output/.../master_store/`)、`--budget-jpy 10` 明示、Production Store 書込禁止。
T-3: 上記「性質」欄の定型文に従う。

## ユーザー指示(原文)

「Task 1 — Advanced Key Phrase 英語解説音声の再比較。前提: 英語解説テキスト仕様はユーザーが正式採用。Status: APPROVED_FOR_PRODUCTION。ただしProduction wiringはまだ行わない。今回の対象は音声Styleだけ。Hormuzの既存5 Phrase、既存英語解説文をそのまま使用し、再生成・再選定しない。比較: 同じ英語解説に対して、Before『clear, precise, explanatory』/ After『clear, precise, unhurried』で比較。ユーザー意図: 英語だけで理解する必要があるため、少し早いと理解しづらい。英語解説は『はっきり・正確に・急がず』を優先する。Phrase自体の KEY_PHRASE_EN も現行どおり、clear, precise, unhurried でよい。成果物: 試聴ページに各5 Phraseについて、Phrase/英語解説text/Before音声/After音声/実際に渡したStyle文言 を並べる。Key Phrase選定ロジック、DB Hybrid、Production Master Storeは変更しない。」

## Fable補足

- Existing Spec / Prior Trial Check(設計書に記録): `KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-TRIAL-02_REPORT.md` §2/§3(B 解説文5件、er041 の音声化で実際に渡した style 文言)、`er041_key_phrase_advanced_english_explanation_trial_02.py`(音声化経路・`trial_master_audio_store` の使い方)、`er038_tts_all_spoken_role_style_trial_01.py` の `TRIAL_ROLE_STYLE_EN["KEY_PHRASE_EXPLANATION_EN"]`/`["KEY_PHRASE_EN"]` の逐語、`er033_tts_flash_lite_family_x_styles_01.py`(6-role 既存 style、`FAMILY_X_ROLE_STYLE_EN_FALLBACK`)、`er006_master_audio_store_01.py`(Store 隔離)、OPEN-221/222/223/226(Grep)。
- **Before の reuse 判定**: er041 の B 解説音声5件が **実際に「clear, precise, explanatory」を含む style で生成されていた**なら(er041 の audit/`audio_summary.json` の style metadata で確認)、その wav をコピー再利用し新規生成しない。文言が異なる場合のみ Before を新規生成(5 call)。After「clear, precise, unhurried」は 5 call 新規。Phrase EN 音声は既存 Hormuz artifact をコピー再利用(新規生成なし)。
- 生成は Production と同じ関数(`generate_narration_snippet_verified_strict` 系)を Trial Store・Trial out-dir・style 上書きで呼び、ASR 検証は Production と同じ cascade を通す(retry 上限は既存値、独自変更なし)。**渡した style 文字列の全文**(Production 側で付与される接頭・接尾やフォールバック文を含む最終文字列)を metadata として保存し、ページに表示する。
- 試聴ページ: `user_test/kp_advanced_explanation_audio_trial_03/index.html`(5 Phrase × [Phrase EN 音声/英語解説 text/Before 音声/After 音声/実際に渡した Style 全文/duration/ASR 結果])。mp3 変換は既存 precedent(ffmpeg or `lameenc`)。
- **Pages 公開確認(7項目、全て満たすまで「試聴ページ完成」と書かない)**: (1) 対象 URL HTTP 200(`curl -sI`)、(2) 実ブラウザ相当で公開ページを開く(Windows の Edge/Chrome を headless で `--headless --dump-dom <URL>` により公開 DOM を取得。使えない場合は Pages 反映後の `curl` 本文で代替し「headless 不可」と明記)、(3) 公開 DOM に `(existing 6-role value, unchanged)` が 0 件、(4) Style Prompt 全文が公開 DOM に実表示、(5) 各 audio player(`<audio>`)が存在(件数)、(6) 各 mp3 の公開 URL が HTTP 200・content-type audio・非ゼロ長で、ダウンロードした bytes がデコード可能(ffprobe/lameenc 等)、(7) ページ表示の Style と生成音声の Style metadata(json)が一致。404/旧 cache の場合は別 URL を乱造せず、Pages の source/deploy 状態を調査して報告。
- 判定案: `USER_DECISION_REQUIRED`(ユーザー試聴待ち)。Sonnet は `VALIDATED` を自己宣言しない。

## 事前指定Read一覧

- `KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-TRIAL-02_REPORT.md`: §2-§3(50-106行)
- `er041_key_phrase_advanced_english_explanation_trial_02.py`: Grep `cmd_audio|trial_master_audio_store|TRIAL_ROLE_STYLE_EN|generate_narration_snippet|style` → 該当範囲
- `er041_output/key_phrase_advanced_english_explanation_trial_02/hormuz/audio_summary.json`(style metadata)
- `er038_tts_all_spoken_role_style_trial_01.py`: Grep `KEY_PHRASE_EXPLANATION_EN|KEY_PHRASE_EN|trial_master_audio_store`
- `OPEN_ITEMS.md`: Grep `OPEN-221|OPEN-222|OPEN-223|OPEN-226`

## 事前指定Grep一覧+追記位置・更新位置の手順

- Grep対象: 上記。SSOT は Grep のみ(編集禁止)。
- 追記位置: 設計書(新規)、REPORT(新規)。
- 更新位置: なし(既存ファイルは変更しない)。

## 実行コマンド全文

- `TTS_EXECUTION_MODE=STANDARD .venv/Scripts/python.exe er042_key_phrase_advanced_english_explanation_audio_style_trial_03.py --source-dir "er041_output/key_phrase_advanced_english_explanation_trial_02/hormuz" --out-dir "er042_output/key_phrase_advanced_english_explanation_audio_style_trial_03/hormuz" --trial-store "er042_output/key_phrase_advanced_english_explanation_audio_style_trial_03/master_store" --tts-backend speech_metadata_flash_lite --budget-jpy 10`(引数は実装に合わせ逐語記録)
- `.venv\Scripts\python.exe -m pytest C:\Users\tensh\eigo-radio\er042_key_phrase_advanced_english_explanation_audio_style_trial_03_test_01.py -q`(Phrase/解説文の逐語同一性、Before/After style 文字列の逐語、Production Store 非参照、Store 隔離復元)
- `.venv\Scripts\python.exe run_project_regression.py --pattern "er042*_test_*.py"`
- Production無変更の証拠: `git diff --stat HEAD -- "er0*.py" "er003_v1_translator_briefs/" "er006_output/master_audio_store_01/" | grep -v er042`(空。他タスク差分は列挙)
- Pages: `curl -sI https://shimomura055.github.io/eigo-radio/user_test/kp_advanced_explanation_audio_trial_03/index.html`、headless DOM 取得コマンド、mp3 200 確認コマンド(逐語記録)

## SSOT追記文

RESULT_PACKET へ文案のみ: REPORT_LEDGER 新行、DECISION_LOG(「英語解説 text 仕様=ユーザー正式採用 `APPROVED_FOR_PRODUCTION`、配線未実施」+本 Trial 記録)、OPEN-221 追記案。

## Git

- add対象(path指定のみ、`git add -A` 禁止): `er042_*`、`er042_output/.../`(json/md、wav 非commit)、`user_test/kp_advanced_explanation_audio_trial_03/`(html/mp3)、REPORT、設計書、delegation_log+`_check.json`。SSOT編集権: なし。
- メッセージ: `KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-AUDIO-STYLE-TRIAL-03: Advanced KP英語解説音声のStyle比較(explanatory vs unhurried)+試聴ページ`、trailer `Management-ID: KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-AUDIO-STYLE-TRIAL-03`。`git push origin main`。

## 報告(RESULT_PACKET_KA3 + handback、目安30行)

ユーザー指定項目: 実施内容/使用Prompt全文(Before・After の最終文字列)/Candidate(5 Phrase 表)/試聴URL/公開実ブラウザ確認結果(7項目それぞれの結果)/ASR・drift/retry/cost/regression/Production無変更証拠/Trial status/USER_DECISION_REQUIRED+STOP有無+SSOT文案+commit hash+raw URL。
