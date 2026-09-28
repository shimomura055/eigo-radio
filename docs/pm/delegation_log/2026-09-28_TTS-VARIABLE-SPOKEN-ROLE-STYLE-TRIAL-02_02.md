## 管理ID

TTS-VARIABLE-SPOKEN-ROLE-STYLE-TRIAL-02(修正1回目、委任 _02)。一時ファイル `docs/pm/ACTIVE_TASK_VR2B.md` / `docs/pm/RESULT_PACKET_VR2B.md`(commitしない)。並行Agentなし。本タスクの所有: `er044_tts_variable_spoken_role_style_trial_02.py`(ページ生成部のみ)、`er044_output/tts_variable_spoken_role_style_trial_02/`、`user_test/tts_variable_role_style_trial_02/`、`TTS-VARIABLE-SPOKEN-ROLE-STYLE-TRIAL-02_REPORT.md`(§14 追記)、delegation_log。**API 支出 上限¥0(TTS/ASR/LLM 呼び出し禁止。必要なら実行前STOP)**。Production code・Prompt・SSOT・Production Master Store は変更しない。`er038_*` は読み取りのみ。**削除・移動・`rm`・`git clean`・stash/rebase/reset/amend/force push 禁止**(同名上書きは可)。未追跡ファイルは他Agent/ユーザーの作業物として扱う。push競合時は `git merge origin/main` のみ。APIキー本文表示禁止。

## 性質/到達上限Status/禁止事項

- 性質: 試聴ページの情報補完(既存音声の reuse のみ)。Status `USER_DECISION_REQUIRED` のまま。
- 背景: ユーザーが「現状=『落ち着いた、自然な話し言葉で』は抑揚不足」と述べた基準点は、Task B(`TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01`)の試聴ページで聴いた Trial 限定 style の音声である。本 Trial は J0 を真の Production 現状(`p9a.JAPANESE_STYLE_PREFIX` 長文)に訂正したため、ユーザーの基準点音声がページに無い。比較の連続性のため、Task B Trial 値の音声を **参考列** として追加する。
- 禁止: 新規生成(er038 の既存 wav が該当 segment・該当 style で存在しない場合は「参考音声なし」と表示し生成しない)、J0〜J3 の変更、Style の省略表記。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-2/T-3)

E-1/D-1/G-1/F-1 標準。
T-0: 本委任文を `docs/pm/delegation_log/2026-09-28_TTS-VARIABLE-SPOKEN-ROLE-STYLE-TRIAL-02_02.md` へ逐語保存し、`.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-28_TTS-VARIABLE-SPOKEN-ROLE-STYLE-TRIAL-02_02.md --json-out docs/pm/delegation_log/2026-09-28_TTS-VARIABLE-SPOKEN-ROLE-STYLE-TRIAL-02_02.md_check.json` を実行し結果1行記録。
T-2: TTSなし。T-3: API支出なし。

## 手順

1. `er038_output/tts_all_spoken_role_style_trial_01/hormuz/a2/`(Standard)配下の JA segment(preview/comment_1〜4)の wav と `audit/tts_generation_results.json` の style metadata を確認し、**実際に渡された style 文字列が「落ち着いた、自然な話し言葉で」(またはそれを含む Task B の JA style 文言)であること**を確認。該当 wav を `er044_output/.../reference_taskb/` へコピー(read-only)、既存経路で mp3 化。
2. ページ A(日本語)の各 segment 行に「参考: Task B Trial 値(Production 未配線)」列を追加し、音声/**Style 全文**/duration/ASR 結果を表示。J0 のラベルを「J0=現行 Production(長文 instruction)」と明確化し、ページ冒頭に「ユーザーが以前に聴いた『落ち着いた、自然な話し言葉で』は Task B の Trial 値であり Production 未配線。本ページの J0 は真の Production 現状」という説明を1段落で記載。
3. Pages 公開確認 7項目を再実施(HTTP 200 / headless Edge DOM / `(existing 6-role value, unchanged)` 0件 / Style 全文表示 / `<audio>` 件数=集計一致 / mp3 全件 200・audio・非ゼロ長・代表デコード / 表示 Style と metadata 一致)。反映まで待って確認。
4. REPORT §14「修正1回目(Task B Trial 値の参考列追加、¥0)」を追記(追加内容、reuse 元パス・style 一致確認、API 0 件=`raw_usage_log` 行数不変、Regression、Production 無変更)。
5. `.venv\Scripts\python.exe run_project_regression.py --pattern "er044*_test_*.py"`(11件 PASS 維持)。

## 事前指定Read一覧

- `er038_output/tts_all_spoken_role_style_trial_01/hormuz/a2/audit/tts_generation_results.json`(Grep `preview|comment_|style`)
- `er044_tts_variable_spoken_role_style_trial_02.py`: ページ生成部(Grep `def build_page|html|<audio>`)
- `TTS-VARIABLE-SPOKEN-ROLE-STYLE-TRIAL-02_REPORT.md`: §2-§4(15-66行)

## 事前指定Grep一覧+追記位置・更新位置の手順

- Grep対象: 上記。
- 更新位置: `er044_*.py` ページ生成部、`user_test/tts_variable_role_style_trial_02/index.html`+参考 mp3、REPORT 末尾 §14。

## 実行コマンド全文

- `.venv\Scripts\python.exe er044_tts_variable_spoken_role_style_trial_02.py <ページ再生成の引数 逐語記録>`
- `.venv\Scripts\python.exe run_project_regression.py --pattern "er044*_test_*.py"`
- `curl -sI https://shimomura055.github.io/eigo-radio/user_test/tts_variable_role_style_trial_02/index.html`、headless DOM 取得、mp3 200 確認(逐語記録)
- `git diff --stat HEAD -- "er0*.py" "er003_v1_translator_briefs/" "er006_output/master_audio_store_01/" | grep -v er044`

## SSOT追記文

不要(SSOT反映は別委任)。

## Git

- add対象(path指定のみ): `er044_*.py`、`user_test/tts_variable_role_style_trial_02/`(html/参考 mp3)、`er044_output/.../reference_taskb/*.json`(wav 非commit)、REPORT、delegation_log+`_check.json`。SSOT編集権なし。
- メッセージ: `TTS-VARIABLE-SPOKEN-ROLE-STYLE-TRIAL-02: Task B Trial値(落ち着いた、自然な話し言葉で)のJA参考列を試聴ページへ追加(reuseのみ、¥0)`、trailer `Management-ID: TTS-VARIABLE-SPOKEN-ROLE-STYLE-TRIAL-02`。`git push origin main`。

## 報告(RESULT_PACKET_VR2B + handback、目安15行)

追加した参考音声一覧(segment/reuse 元/style 全文/ASR)/参考なし segment があればその理由/Pages 7項目結果/API 0件実測/Regression/commit hash・raw URL/STOP有無。
