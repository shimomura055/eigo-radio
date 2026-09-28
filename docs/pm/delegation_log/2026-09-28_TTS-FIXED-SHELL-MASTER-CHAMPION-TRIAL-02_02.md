## 管理ID

TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-02(修正1回目、委任 _02)。一時ファイル `docs/pm/ACTIVE_TASK_CH2B.md` / `docs/pm/RESULT_PACKET_CH2B.md`(commitしない)。並行: 別Sonnet 1件(Task 3 `er044_*`/`er044_output/`/`user_test/tts_variable_role_style_trial_02/`/`user_test/tts_all_role_style_trial_01/`)→ 触れない。本タスクの所有: `er043_tts_fixed_shell_master_champion_trial_02_page_01.py`、`er043_output/tts_fixed_shell_master_champion_trial_02/`(読み取り+ページ用 json 追記)、`user_test/fixed_shell_champion_trial_02/`、`TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-02_REPORT.md`(§9 追記)、delegation_log。**API 支出 上限¥0(TTS/ASR/LLM 呼び出し禁止。必要なら実行前STOP)**。Production code・Prompt・SSOT・Production Master Store は変更しない。**削除・移動・`rm`・`git clean`・stash/rebase/reset/amend/force push 禁止**(既存ファイルの同名上書きは可)。未追跡ファイルは他Agent/ユーザーの作業物として扱う。push競合時は `git merge origin/main` のみ。APIキー本文表示禁止。

## 性質/到達上限Status/禁止事項

- 性質: 試聴ページの情報補完(既存生成物のみ使用)。Status は `USER_DECISION_REQUIRED` のまま。
- 背景: One〜Five で B(num_one/num_three/num_four)・C(num_three)が既存 ASR cascade で3 attempt とも不合格(STOPPED)となり、ユーザーが「5個セットとして」B/C を A と比較できない。Trial-01 では num_three の ASR text が "Free" になる等、**音声自体は正しく発話されている可能性**があり、単語1語の極短音声に対する ASR 厳格一致の限界が疑われる(OPEN-222)。Production 登録には ASR verified が必要だが、既存の Human Review Lock には人間承認の経路があるため、ユーザーが聴いて判断できる材料を出す価値がある。
- 禁止: 新規生成、Gate/Lock 状態の変更、STOPPED 音声を「合格」と表示すること(必ず「ASR 未合格・人間確認待ち」と明示)、Style の省略表記。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-2/T-3)

E-1/D-1/G-1/F-1 標準。
T-0: 本委任文を `docs/pm/delegation_log/2026-09-28_TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-02_02.md` へ逐語保存し、`.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-28_TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-02_02.md --json-out docs/pm/delegation_log/2026-09-28_TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-02_02.md_check.json` を実行し結果1行記録。
T-2: TTSなし。T-3: API支出なし。

## 手順

1. `er043_output/.../champion_trial_results.json` と attempts 配下から、STOPPED となった candidate×phrase(B: num_one/num_three/num_four、C: num_three)の **全 attempt の wav**(存在するもの)と各 attempt の ASR text・失敗分類(TTS_FAILURE/TRUE_CONTENT_MISMATCH 等)を収集。wav が保存されていない attempt は「音声未保存」と記録(生成しない)。
2. 既存の mp3 変換経路(lameenc)で attempt wav を mp3 化し、ページに新 section「ASR 未合格 attempt(人間確認用・Production 登録不可のまま)」を追加: candidate×phrase×attempt ごとに 音声/ASR text/失敗分類/Style 全文/duration。
3. One→Five 連続再生について、B と C それぞれ「OK 音声+未合格 attempt のうち最初の attempt」で構成した **参考連結 mp3** を追加(明確に「未検証 attempt を含む参考」と表示)。A の連結は既存のまま。
4. 既存 section(A/B/C の OK 音声、6 Style 文言)は変更しない。
5. Pages 公開確認 7項目を再実施(HTTP 200 / headless Edge DOM / `(existing 6-role value, unchanged)` 0件 / Style 全文表示 / `<audio>` 件数=集計一致 / mp3 全件 200・audio・非ゼロ長・代表デコード / 表示 Style と metadata 一致)。反映まで待って確認。
6. REPORT §9 に「修正1回目(未合格 attempt の可視化、¥0)」を追記: 追加内容、attempt ごとの ASR text 一覧表、One〜Five の A/B/C 揃い指標(既存 F0 proxy を未合格 attempt にも適用できれば追加)、Production 無変更、API 0 件(`raw_usage_log` 行数不変)。

## 事前指定Read一覧

- `er043_output/tts_fixed_shell_master_champion_trial_02/champion_trial_results.json`(Grep `STOPPED|attempts_log|asr_text|wav`)
- `er043_tts_fixed_shell_master_champion_trial_02_page_01.py`(全文、構造変更のため)
- `TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-02_REPORT.md`: §3-§5(Grep `## `)

## 事前指定Grep一覧+追記位置・更新位置の手順

- Grep対象: 上記。
- 更新位置: `_page_01.py`(section 追加)、`user_test/fixed_shell_champion_trial_02/index.html`+新 mp3、REPORT 末尾 §9。

## 実行コマンド全文

- `.venv\Scripts\python.exe er043_tts_fixed_shell_master_champion_trial_02_page_01.py <既存引数 逐語記録>`
- `.venv\Scripts\python.exe run_project_regression.py --pattern "er043*_test_*.py"`(17件 PASS 維持)
- `curl -sI https://shimomura055.github.io/eigo-radio/user_test/fixed_shell_champion_trial_02/index.html`、headless DOM 取得、mp3 200 確認(逐語記録)
- `git diff --stat HEAD -- "er0*.py" "er003_v1_translator_briefs/" "er006_output/master_audio_store_01/" | grep -v er043`

## SSOT追記文

不要(SSOT反映は別委任)。

## Git

- add対象(path指定のみ): `_page_01.py`、`user_test/fixed_shell_champion_trial_02/`(html/新 mp3)、REPORT、ページ用 json、delegation_log+`_check.json`。SSOT編集権なし。
- メッセージ: `TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-02: One〜FiveのASR未合格attempt音声を人間確認用sectionとして試聴ページへ追加(新規生成なし、¥0)`、trailer `Management-ID: TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-02`。`git push origin main`。

## 報告(RESULT_PACKET_CH2B + handback、目安20行)

追加した attempt 一覧(candidate/phrase/attempt/ASR text/分類/音声有無)/参考連結の構成/Pages 7項目結果/API 0件の実測/Regression/commit hash・raw URL/STOP有無。
