## 管理ID

TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01(修正3回目=本管理IDのSonnet最終回、委任 _05)。一時ファイル `docs/pm/ACTIVE_TASK_RS4.md` / `docs/pm/RESULT_PACKET_RS4.md`(commitしない)。並行Agentなし(本タスクのみ稼働)。本タスクの所有: `er038_output/tts_all_spoken_role_style_trial_01/`、`user_test/tts_all_role_style_trial_01/`、`TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01_REPORT.md`、delegation_log。`er038_*.py` は変更しない(読み取りのみ)。**削除・移動・`rm`・`git clean`・stash/rebase/reset/amend/force push 禁止**(既存mp3の上書き=同名ファイルへの再書き込みは可、削除は不可)。未追跡ファイルは他Agent/ユーザーの作業物として扱う。push競合時は `git merge origin/main` のみ、conflictは中断報告。SSOT 4点+PM_GOVERNANCE 編集権なし。Production code・正式Prompt・CURRENT_SPEC・Production Master Audio Store・Human Review Lock 共有ログは一切変更しない。

## 性質/到達上限Status/禁止事項

- 性質: 試聴ページの表示整合(ローカル変換のみ)。到達上限Status: 変わらず `USER_DECISION_REQUIRED`(ユーザー試聴待ち)。
- 費用: **上限¥0。API呼び出し(TTS/ASR/LLM)は一切禁止**。必要と判明したら実行前にSTOPして報告。`raw_usage_log.jsonl` の総行数が作業前後で不変であることを実測記録する。
- 禁止: Gate回避・evidence改変、Standard(A2)側の変更、`hormuz_advanced_trial.mp3`/`hormuz_standard_trial.mp3` の再生成(既に整合済み)。APIキー本文表示禁止。試聴リンクはGitHub Pages。

## 背景(REPORT §13/§14 参照)

修正2回目で Advanced(B1B)full(`hormuz_advanced_trial.mp3`)は現音声byte+再検証evidenceで整合済み。しかし試聴ページ セクション4(Advanced Role別segmentテーブル)の個別プレビュー mp3(`b1b_*.mp3` 19件、および `b1b_shared_num_two.mp3`/`b1b_shared_num_three.mp3`)はインシデント前(16:26台)の旧音声のままで、full音声と一致しない。またテーブル上 num_two/num_three が `HUMAN_REVIEW_LOCKED` 表示のままで、実態(Production既存合格Master の reuse で OK)と食い違っている。

## 目的

ユーザーが「個別 segment」と「full」で同じ音声を聴ける状態にし、テーブル表示を実態に合わせる。

## 手順

1. 現状記録(¥0): `raw_usage_log.jsonl` 総行数、対象 mp3 21件の mtime/sha256、`b1b/audit/tts_generation_results.json` の各 segment の現 wav パス・status。
2. 現在の wav(full assembly に使われたものと同一。`tts_generation_results.json`/`run_summary_assemble.json` の参照パスで確認)から、修正1回目/2回目と同じ ffmpeg 経路・同ビットレート(128kbps)で個別プレビュー mp3 を同名で再変換(Advanced 19件+shared num_two/num_three 2件)。変換元 wav の sha256 が full assembly 入力と一致することを記録。Standard 側 mp3 は触らない。
3. `index.html` セクション4 のテーブルを `tts_generation_results.json` の現状に合わせて更新(num_two/num_three=OK、備考に「Production既存合格Master reuse、TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-02 由来」、その他 19 segment に「2026-09-28 再生成後の音声、evidence 再検証済み」の注記)。セクション2の経緯説明と矛盾がないことを確認。ユーザー向け表記は Standard/Advanced、TTS実行は 同期実行/バッチ実行。
4. `.venv\Scripts\python.exe run_project_regression.py --pattern "er038*_test_*.py"`(16/16 PASS 維持)。
5. Production無変更の証拠: `er006_output/master_audio_store_01/manifest.json`・`reuse_telemetry.jsonl` の mtime 不変、`git diff --stat HEAD -- "er0*.py" "er003_v1_translator_briefs/" | grep -v er038` が空、`er038_*.py` 無変更。
6. push後 `curl -sI` で `index.html` と再変換した mp3 数件(例 `b1b_shared_num_two.mp3`、`b1b_comment_1.mp3`)の 200 確認(反映に数分要する場合は待って再確認)。
7. REPORT §15 として「修正3回目(試聴ページ個別プレビュー整合、¥0)」を追記(何が問題だったか/何を変更したか/何が改善されるか/リスク、API 0件の実測、Regression、Production無変更の証拠、STOP有無)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない。
D-1: Grep→該当行範囲Read。`index.html` は構造変更のため全文Read可。
G-1: git出力は `--porcelain`/`--stat`/`--short` で最小化。
F-1: transcript退避不要。
T-0: 本委任文を `docs/pm/delegation_log/2026-09-28_TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01_05.md` へ逐語保存し、`.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-28_TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01_05.md --json-out docs/pm/delegation_log/2026-09-28_TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01_05.md_check.json` を実行し結果1行記録(FAILでも内容改変してPASSさせない)。
T-2: TTS実行なし。
T-3: API支出なし(上限¥0)。

## 事前指定Read一覧

- `TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01_REPORT.md` §14(Grep `### 14` → 該当範囲)
- `er038_output/tts_all_spoken_role_style_trial_01/hormuz/b1b/audit/tts_generation_results.json`(Grep `wav|status|num_two|num_three`)
- `er038_output/tts_all_spoken_role_style_trial_01/hormuz/b1b/run_summary_assemble.json`
- `user_test/tts_all_role_style_trial_01/index.html`(全文)

## 事前指定Grep一覧+追記位置・更新位置の手順

- Grep対象: `tts_generation_results.json`(`"path"|"wav"|"status"`)、`index.html`(`HUMAN_REVIEW_LOCKED|b1b_shared_num|b1b_comment_1`)、REPORT(`### 14|ffmpeg`)。
- 更新位置: `user_test/tts_all_role_style_trial_01/index.html` セクション4テーブル(既存行の status/備考のみ更新、構造は維持)、同ディレクトリの対象 mp3 21件(同名上書き)、REPORT 末尾に §15 追記。

## 実行コマンド全文

- ffmpeg 変換は修正1回目/2回目で使用したコマンドと同一形式(`ffmpeg -y -i <wav> -b:a 128k <mp3>` 相当。実際に使う引数を逐語記録)。
- `.venv\Scripts\python.exe run_project_regression.py --pattern "er038*_test_*.py"`
- `git diff --stat HEAD -- "er0*.py" "er003_v1_translator_briefs/" | grep -v er038`
- `curl -sI https://shimomura055.github.io/eigo-radio/user_test/tts_all_role_style_trial_01/index.html`

## SSOT追記文

不要(SSOT反映は別委任)。

## Git

- add対象(path指定のみ、`git add -A` 禁止): `user_test/tts_all_role_style_trial_01/index.html`、同ディレクトリの再変換 mp3 21件、`TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01_REPORT.md`、delegation_log+`_check.json`。他Agent差分・SSOT・`er038_*.py`・wav は add しない。SSOT編集権: なし。
- メッセージ: `TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01: 試聴ページのAdvanced個別プレビューmp3を現音声へ再変換+テーブル表示を実態(num_two/num_three reuse OK)へ整合(API 0件)`、trailer `Management-ID: TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01`。`git push origin main`。

## 報告(RESULT_PACKET_RS4 + handback、目安15行)

1 何が問題だったか 2 何を変更したか 3 何が改善されるか 4 リスク/API 0件の実測(総行数before/after)/変換元wavとfull入力の一致/Regression/Production無変更/Pages 200/commit hash・raw URL/STOP有無。
