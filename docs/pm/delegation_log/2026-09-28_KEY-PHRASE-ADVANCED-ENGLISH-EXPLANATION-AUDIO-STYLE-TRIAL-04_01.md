## 管理ID

KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-AUDIO-STYLE-TRIAL-04(ユーザー承認済みTrial、音声Styleのみ)。一時ファイル `docs/pm/ACTIVE_TASK_KA4.md` / `docs/pm/RESULT_PACKET_KA4.md`(commitしない)。並行: 別Sonnet 4件(Task 1 `er045_*`/`user_test/no_heading_trial_01/`、Task 3 `er047_*`/`user_test/fixed_shell_three_five_retrial_01/`、Task 4 設計書、SSOT反映Agent)→ 触れない。SSOT 4点は編集権なし(文案のみ)。本タスクの所有: 新規 `er046_key_phrase_advanced_english_explanation_audio_style_trial_04.py`(+`_test_01.py`)、`er046_output/key_phrase_advanced_english_explanation_audio_style_trial_04/`(Trial専用Store含む)、`user_test/kp_advanced_explanation_audio_trial_04/`、新規 `KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-AUDIO-STYLE-TRIAL-04_REPORT.md`、`docs/pm/design_key_phrase_advanced_english_explanation_audio_style_trial_04.md`、delegation_log。**Production code・Master Store・Key Phrase selector・DB Hybrid・正式Prompt・CURRENT_SPEC は変更禁止。削除・移動・`rm`・`git clean`・stash/rebase/reset/amend/force push 禁止。未追跡ファイルは他Agent/ユーザーの作業物として扱う。push競合時は `git merge origin/main` のみ。APIキー本文表示禁止。試聴リンクはGitHub Pages。**

## 性質/到達上限Status/禁止事項

- 性質: Trial。到達上限Status: `REJECTED` / `VALIDATED` / `USER_DECISION_REQUIRED`(ユーザー試聴前は `USER_DECISION_REQUIRED`)。
- 前提(ユーザー決定): 英語解説 text 仕様は `APPROVED_FOR_PRODUCTION`(未配線)。TRIAL-03 の「clear, precise, unhurried」は **遅すぎた**(不採用)。前回の「clear, precise, explanatory」との中間の自然な速度感を探す。
- 費用: 上限¥10(想定 15 TTS call+ASR)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし報告。
- **実行安全**: `--stage all` 禁止。必要 segment のみ。実行前に ACTIVE_TASK へ「対象 segment 一覧/想定 TTS call 数/retry 上限(既存 cascade)/想定費用/Guardrail」を記録。既存音声(TRIAL-03 の Before/After、Phrase EN)は reuse。
- 禁止: Phrase・解説文の再生成・再選定(Hormuz 既存5 Phrase+TRIAL-02 の B 解説文を逐語 reuse)、新規 Role 名、Style 省略表記(ページに TTS へ渡した Style 全文)。ユーザー向け表記は Standard/Advanced、TTS実行は 同期実行/バッチ実行。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-2/T-3)

E-1/D-1/G-1/F-1 標準(全文Readは `er042_*` script のみ可、流用推奨)。
T-0: 本委任文を `docs/pm/delegation_log/2026-09-28_KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-AUDIO-STYLE-TRIAL-04_01.md` へ逐語保存し、`.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-28_KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-AUDIO-STYLE-TRIAL-04_01.md --json-out docs/pm/delegation_log/2026-09-28_KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-AUDIO-STYLE-TRIAL-04_01.md_check.json` を実行し結果1行記録。
T-2: `TTS_EXECUTION_MODE=STANDARD` 明示、Trial専用Store(`er046_output/.../master_store/`)、`--budget-jpy 10`、Production Store 書込禁止。
T-3: 上記「性質」欄の定型文に従う。

## ユーザー指示(原文)

「前回: clear, precise, explanatory。今回: clear, precise, unhurried だったが、unhurried は遅すぎた。目的: その中間の自然な速度感を探す。実施: 既存 Hormuz 5 Phrase と既存英語解説 text を逐語 reuse。Phrase 選定・英語解説生成はやり直さない。3パターン程度作成する。方向性: clear/precise/説明として少し余裕/ただし unhurried ほど遅くしない/間延びさせない。例として、A: 少しだけ落ち着かせる、B: 中間、C: やや丁寧 程度に差をつける。実際の Style Prompt 全文を試聴ページに表示。Production code/Master Store/selector は変更禁止。」

## Fable補足

- Existing Spec / Prior Trial: `KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-AUDIO-STYLE-TRIAL-03_REPORT.md`(Before/After の生成条件・model・voice・reuse 元)、`er042_*` script(経路をそのまま流用し style 3案に拡張)、OPEN-221。
- **Style 3案(短く、設計書に逐語。「clear, precise」を必ず含め、速度は数値指定しない=`assert_no_wpm_specification` 相当)**: 例 A「clear, precise, at a slightly relaxed pace」/ B「clear, precise, at a measured pace, without dragging」/ C「clear, precise, carefully paced for understanding, without slowing down」。実装側で文言を確定し、Before/After と並べて差が分かるようにする。model/voice は TRIAL-03 と同一(Flash-Lite、同 voice)。
- 生成: 5 Phrase × 3 案=15 call(Production 同一関数、Trial Store、ASR cascade 既存上限)。**参考列**として TRIAL-03 の Before(explanatory)/After(unhurried)の既存 mp3 を reuse 表示(¥0)、Phrase EN 音声も reuse。
- ページ `user_test/kp_advanced_explanation_audio_trial_04/index.html`: 5 Phrase × [Phrase EN/解説 text/Before(参考)/A/B/C/After(参考)/各 Style 全文/duration/ASR]。duration 比較表(Before/A/B/C/After の秒数・語/秒)を掲載し「速度感」の客観指標を添える。
- **Pages 公開確認 7項目**(HTTP 200/headless Edge・Chrome DOM/省略表記 0件/Style 全文表示/`<audio>` 件数/mp3 全件 200・audio・非ゼロ長・代表デコード/表示 Style と metadata 一致)。全て満たすまで「完成」と書かない。404/旧 cache は原因調査。
- 判定案: `USER_DECISION_REQUIRED`。

## 事前指定Read一覧

- `KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-AUDIO-STYLE-TRIAL-03_REPORT.md`(全文、短い)
- `er042_key_phrase_advanced_english_explanation_audio_style_trial_03.py`(全文)
- `er042_output/key_phrase_advanced_english_explanation_audio_style_trial_03/hormuz/after_audio_summary.json`(model/voice/style metadata)

## 事前指定Grep一覧+追記位置・更新位置の手順

- Grep対象: `OPEN_ITEMS.md`(`OPEN-221`)。SSOT は Grep のみ。
- 追記位置: 設計書(新規)、REPORT(新規)。更新位置: なし。

## 実行コマンド全文

- `TTS_EXECUTION_MODE=STANDARD .venv/Scripts/python.exe er046_key_phrase_advanced_english_explanation_audio_style_trial_04.py --source-dir "er042_output/key_phrase_advanced_english_explanation_audio_style_trial_03/hormuz" --out-dir "er046_output/key_phrase_advanced_english_explanation_audio_style_trial_04/hormuz" --trial-store "er046_output/key_phrase_advanced_english_explanation_audio_style_trial_04/master_store" --tts-backend speech_metadata_flash_lite --budget-jpy 10`(逐語記録)
- `.venv\Scripts\python.exe -m unittest er046_key_phrase_advanced_english_explanation_audio_style_trial_04_test_01 -v`
- `.venv\Scripts\python.exe run_project_regression.py --pattern "er046*_test_*.py"`
- `git diff --stat HEAD -- "er0*.py" "er003_v1_translator_briefs/" "er006_output/master_audio_store_01/" | grep -v er046`
- `curl -sI https://shimomura055.github.io/eigo-radio/user_test/kp_advanced_explanation_audio_trial_04/index.html`、headless DOM、mp3 200(逐語記録)

## SSOT追記文

RESULT_PACKET へ文案のみ(REPORT_LEDGER 新行、DECISION_LOG、OPEN-221 追記案)。

## Git

- add対象(path指定のみ): `er046_*`、`er046_output/.../`(json/md)、`user_test/kp_advanced_explanation_audio_trial_04/`、REPORT、設計書、delegation_log+`_check.json`。SSOT編集権なし。
- メッセージ: `KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-AUDIO-STYLE-TRIAL-04: 英語解説音声のStyle中間3案(explanatory/unhurriedの間)+duration比較+試聴ページ`、trailer `Management-ID: KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-AUDIO-STYLE-TRIAL-04`。`git push origin main`。

## 報告(RESULT_PACKET_KA4 + handback、目安25行)

管理ID/実施内容/既存Spec確認結果/使用Prompt全文(A/B/C+参考)/model・voice/retry/ASR・drift/cost/Regression/公開試聴URL/公開確認結果(7項目)/Production変更有無/Trial status/USER_DECISION_REQUIRED事項/未配線 APPROVED 項目(text 仕様)+duration 表+commit hash+raw URL+STOP有無。
