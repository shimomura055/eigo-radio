## 管理ID

TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01(修正2回目、委任 _04)。一時ファイル `docs/pm/ACTIVE_TASK_RS3.md` / `docs/pm/RESULT_PACKET_RS3.md`(commitしない)。並行: 別Sonnet 2件(Task C `er040_*`/`user_test/fixed_shell_champion_trial_01/`、SSOT反映Agent[REPORT_LEDGER/DECISION_LOG/OPEN_ITEMS 編集中])→ これらに触れない。本タスクの所有: `er038_tts_all_spoken_role_style_trial_01*.py`、`er038_output/tts_all_spoken_role_style_trial_01/`、`user_test/tts_all_role_style_trial_01/`、`TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01_REPORT.md`、delegation_log。**削除・移動・`rm`・`git clean`・stash/rebase/reset/amend/force push 禁止**。未追跡ファイルは他Agent/ユーザーの作業物として扱う。push競合時は `git merge origin/main` のみ、conflictは中断報告。SSOT 4点+PM_GOVERNANCE は編集権なし。Production code・正式Prompt・CURRENT_SPEC・Production Master Audio Store(`er006_output/master_audio_store_01/`)・Human Review Lock 共有ログは一切変更しない(読み取りのみ)。

## 背景(前回 _03 のインシデント、REPORT §13 参照)

前回Agentが `--stage all` を実行した結果、Advanced(B1B)の Key Phrase 10 segment と主記事 9 segment(topic_intro/preview/comment_1-4/full_story_part1/in_one_line/full_story_part2_heading)が意図せず再生成された(¥30.80、Guardrail ¥5 超過)。再生成時にASR検証は実行されたが値の保存前にprocessが強制終了されたため、`b1b/audit/tts_generation_results.json` の `segments`/`key_phrases` は再生成前の実測値のままで、既存Gate `asm.verify_episode_audio_validation_gate`(ASSET_HASH_MISMATCH)が Advanced full assembly を正しくブロックしている。full_story_part2 本文/full_story_part3_heading/full_story_part3 本文の3 segmentは旧音声+旧evidenceのまま整合。pre-incident の wav は復元不可(git管理外)。shared narration(shell)は `--reuse-production-master num_two,num_three` で全て OK。Standard(A2)と `user_test/tts_all_role_style_trial_01/` の既存ファイルは無影響。

## 目的(Option A)

再生成後の Advanced 19 segment(KP 10+主記事 9)について、**新規TTSを一切発生させずに**、実際の音声byteと検証evidenceを再紐付けし、Advanced full assembly → `hormuz_advanced_trial.mp3` → `index.html` 更新までを完了する。

## 性質/到達上限Status/禁止事項

- 性質: Trial成果物の復旧(記録整合)。到達上限Status: 変わらず `USER_DECISION_REQUIRED`(ユーザー試聴待ち)。
- 費用: **上限¥10**(ASR再検証のみ想定、19 segment × 約¥0.3)。**Gemini TTS 呼び出しは 0 件が必須条件**。作業前後で `raw_usage_log.jsonl` の gemini 行数が不変であることを実測記録する。実行計画上 TTS 再生成が不可避と判明した場合は **API実行前にSTOP**して報告(Option B=Advanced full 見送り、へ切替判断はFable/ユーザー)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。
- **`--stage all` および `run_tts_stage` 全体の再実行は禁止**。実行するコマンドは、対象 segment を明示した部分実行(evidence再検証・assemble・mp3変換)に限る。実行前に「そのコマンドがTTSを呼ばない」ことをコード上で確認し、確認根拠(関数名・行)を記録する。Bashのtimeout超過でbackground実行へ移る前に、必ず短時間で終わる単位に分割して実行する。
- 禁止: Gate(`verify_episode_audio_validation_gate`等)の回避・無効化・evidence改竄。evidence は実際に音声byteに対してASR検証(既存Production関数、例 `generate_narration_snippet_verified_strict` 系の検証部のみ、または `er006_preprod_hardening_01_validation` 系の既存検証関数)を再実行して得た値のみ記録する。旧evidenceの hash だけを書き換える操作は禁止。Standard(A2)側・shell 側は触らない。Production Master Store 汚染禁止。APIキー本文表示禁止。試聴リンクは GitHub Pages。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない。
D-1: Grep→該当行範囲Read。全文Readは `er038_tts_all_spoken_role_style_trial_01.py` の構造確認時のみ可。
G-1: git出力は `--porcelain`/`--stat`/`--short` で最小化。
F-1: transcript退避不要。
T-0: 本委任文を `docs/pm/delegation_log/2026-09-28_TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01_04.md` へ逐語保存し、`.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-28_TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01_04.md --json-out docs/pm/delegation_log/2026-09-28_TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01_04.md_check.json` を実行し結果1行記録(FAILでも内容改変してPASSさせない)。
T-2: TTS実行なし(0件が必須)。ASR再検証を行う場合も `TTS_EXECUTION_MODE=STANDARD` を環境に明示し、実行コマンドを逐語記録。
T-3: 上記「性質」欄の定型文に従う。

## 手順

1. 現状把握(¥0): `b1b/` 配下の対象19 segmentの wav の sha256、`b1b/audit/tts_generation_results.json` の該当 evidence、`raw_usage_log.jsonl` の gemini/openai 行数を記録。前回の再生成でASR結果がどこかに残っていないか(`raw_usage_log.jsonl` の openai_asr 行の payload、`audit/` 配下の中間ファイル)を確認し、**残っていれば再呼び出しせず ¥0 で再紐付け**する。
2. 残っていない segment のみ、既存Production検証関数で ASR 再検証(新規TTSなし)。post-process(Advanced に 6% slowdown 等の必須処理があるかを Task B 設計書/`er019_family_x_audio_production_runner_01.py` で確認し、必要なら適用済み音声に対して検証)。
3. `tts_generation_results.json` の `segments`/`key_phrases` を実測値で更新(`reconciliation_note` に本修正の経緯を追記)。
4. `run_assemble_stage`(または同等の部分実行)で Advanced full assembly → Gate PASS を確認 → `hormuz_advanced_trial.mp3` 変換(前回と同じ ffmpeg 経路)→ `index.html` に Advanced full を追加。Standard 側の既存要素は無変更。
5. `.venv\Scripts\python.exe run_project_regression.py --pattern "er038*_test_*.py"`(16件 PASS 維持。evidence再紐付けの検証テストを追加する場合は所有ファイル内のみ)。
6. Production 無変更の証拠: `er006_output/master_audio_store_01/manifest.json`・`reuse_telemetry.jsonl` の sha256 作業前後不変、`git diff --stat HEAD -- "er0*.py" "er003_v1_translator_briefs/" | grep -v er038` が空。
7. push後 `curl -sI https://shimomura055.github.io/eigo-radio/user_test/tts_all_role_style_trial_01/index.html` と Advanced mp3 の 200 確認。
8. REPORT §14 として「修正2回目(evidence再紐付け)」を追記: 何が問題だったか/何を変更したか/何が改善されるか/リスク、実行コマンド全文、gemini 呼び出し 0 件の実測、費用実測、Regression、Production無変更の証拠、STOP有無。

## Git

- add対象(path指定のみ、`git add -A` 禁止): `er038_tts_all_spoken_role_style_trial_01*.py`(変更した場合)、`er038_output/tts_all_spoken_role_style_trial_01/hormuz/b1b/audit/*.json`・`run_summary_*.json`(wav非commit)、`user_test/tts_all_role_style_trial_01/`(index.html+新規mp3)、REPORT、delegation_log+`_check.json`。他Agentの差分(er040系・SSOT・他delegation_log)は add しない。SSOT編集権: なし。
- メッセージ: `TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01: Advanced 19 segmentのevidence再紐付け(新規TTSなし)+Advanced full assembly/試聴ページ更新`、trailer `Management-ID: TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01`。`git push origin main`。

## 報告(RESULT_PACKET_RS3 + handback、目安25行)

1 何が問題だったか 2 何を変更したか 3 何が改善されるか 4 リスク・注意点/gemini呼び出し0件の実測(行数before/after)/費用実測(上限¥10)/Gate PASS の証拠/Regression/Production無変更の証拠/Pages 200/commit hash・raw URL/STOP有無/Advanced full が完成しなかった場合はその時点の状態と残作業。ユーザー向け表記は Standard/Advanced、TTS実行は同期実行/バッチ実行。
