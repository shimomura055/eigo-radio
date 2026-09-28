## 管理ID

TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01(Fableからの修正1回目=ユーザー指示反映: "Two."/"Three." を再生成せず、既存合格MasterをTrial内でreuseしてAdvanced全体試聴を成立させる)。一時ファイル `docs/pm/ACTIVE_TASK_RS2.md` / `docs/pm/RESULT_PACKET_RS2.md`(commitしない)。並行: 別Sonnet 3件(Trial-02 `er039_*`、Task C `er040_*`/`user_test/fixed_shell_champion_trial_01/`、Task D `er041_*`/`user_test/kp_advanced_explanation_trial_02/`[Task Dは `er038_*.py` をimportのみ])→ これらに触れない。本タスクの所有: `er038_tts_all_spoken_role_style_trial_01.py`(reuse経路の追加のみ、最小変更)、`er038_output/tts_all_spoken_role_style_trial_01/`、`user_test/tts_all_role_style_trial_01/`、`TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01_REPORT.md`(§追記)、delegation_log。**Production code・正式Prompt・CURRENT_SPEC・routing・Production Master Audio Store は一切変更しない(Production Masterの置換禁止)**。SSOT 4点は編集権なし。**削除・移動・`rm`・`git clean`・stash/rebase/reset/amend/force push 禁止**(push競合時は `git merge origin/main` のみ、conflictは中断報告)。

## 性質/到達上限Status/禁止事項

- 性質: Trial追補。到達上限Status: `USER_DECISION_REQUIRED`(試聴待ち)のまま。
- 費用: 上限¥5(Guardrail。原則¥0=reuseのみ。reuse不能で再生成が必要と判明した場合は実行せずSTOPして報告)。
- 禁止(ユーザー明示): "Two."/"Three." のためだけの再生成(毎回再生成する方向へ寄せない)、Production Masterの置換、Task CのChampion選定前の固定shell変更、記事再生成、Key Phrase再選定。APIキー本文表示禁止。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない。D-1: Grep→該当行範囲Read。G-1: git出力最小化。F-1: 退避不要。T-0: 本委任文を `docs/pm/delegation_log/2026-09-28_TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01_03.md` へ保存し `.venv\Scripts\python.exe docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-09-28_TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01_03.md --json-out docs/pm/delegation_log/2026-09-28_TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01_03.md_check.json`、結果1行記録。T-2: TTS再生成なし(reuseのみ。Assembly/mp3変換はAPI不要)。T-3: 上記「性質」欄のとおり。

## ユーザー指示(原文)

「Task Bとの関係: 現在進行中の TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01 については、Two. / Three. のためだけに毎回再生成する方向へ寄せない。固定shellはTask Cの思想『合格済み固定音声をMaster化してreuse』と整合させること。ただしTask CのChampion選定前に、Production Masterを勝手に置換しない。Advanced全体試聴を成立させるために既存合格MasterをTrial内でreuseできるなら、それを優先する。」

## 手順

1. 既存合格Masterの特定(read-only): Production Master Audio Store `er006_output/master_audio_store_01/manifest.json` から、canonical text "Two." / "Three."(および他の固定shell)の **ASR verified・status OK** entry(修正3回目 commit `ee280e76` 後の Flash-Lite+`FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]` style master、voice同一)を特定(`master_audio_id`、wav path、style_instruction_version、tts_model_id を記録)。
2. Trial内reuse: `er038_output/tts_all_spoken_role_style_trial_01/hormuz/b1b/` の `num_two`/`num_three` について、上記Masterのwavを **コピーして**(Production Storeは読み取りのみ、書き込み・置換なし)Trial側segmentとして配置し、`tts_generation_results.json`/`shared_narration` 記録に `reused_from_production_master=true`、`master_audio_id`、`style=FALLBACK[0](Trial NUMBER_LABEL styleではない)` を明記。Trial側のHuman Review Lock状態は「Trial内reuseで代替(Lock解除ではない)」として記録(共有Lockファイルは変更しない。OPEN-223参照)。
3. Advanced Assembly(既存結合関数、¥0)→ `episode.wav` → mp3変換(`imageio_ffmpeg` 同梱バイナリ)→ `user_test/tts_all_role_style_trial_01/` へ `hormuz_advanced_trial.mp3` を追加し、index.html を更新(Advanced全体の再生、num_two/num_three 行に「Production合格Masterをreuse(Trial NUMBER_LABEL styleは言語ドリフト)」と表示)。push後 `curl -sI https://shimomura055.github.io/eigo-radio/user_test/tts_all_role_style_trial_01/index.html` で200確認。
4. REPORT §追記「修正1回目: 既存合格Master reuseによるAdvanced結合」(reuse元、Assembly結果[duration]、Task C思想との整合、Production Master無変更の証拠 `git diff --stat HEAD -- "er006_output/master_audio_store_01/"` 空)。
5. reuse可能なMasterが存在しない場合(例: voice/modelが一致しない)は、再生成せずSTOPして報告(選択肢のみ列挙)。

## 実行コマンド全文

- Assembly: `TTS_EXECUTION_MODE=STANDARD .venv/Scripts/python.exe er038_tts_all_spoken_role_style_trial_01.py --assemble-only --level b1b --out-dir "er038_output/tts_all_spoken_role_style_trial_01/hormuz" --reuse-production-master num_two,num_three`(引数は実装に合わせ最小追加、逐語記録)
- `.venv\Scripts\python.exe -m pytest er038_tts_all_spoken_role_style_trial_01_test_01.py -q`(既存13件+reuse経路がProduction Storeへ書き込まないassert 1件)
- `.venv\Scripts\python.exe run_project_regression.py --pattern "er038*_test_*.py"`

## Git

- add対象: `er038_tts_all_spoken_role_style_trial_01.py`(+test)、`er038_output/.../hormuz/b1b/` のjson、`user_test/tts_all_role_style_trial_01/`(mp3/html)、REPORT、delegation_log+`_check.json`。SSOT編集権: なし。
- メッセージ: `TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01 修正1回目: Two./Three.を再生成せず既存合格Production MasterをTrial内reuseしてAdvanced全体を結合(Production Master無変更)`、trailer `Management-ID: TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01`。`git push origin main`。

## 報告(RESULT_PACKET項目)

T-0結果/reuse元Master表/Assembly結果(duration)/試聴URL/Production Master無変更の証拠/test・regression/cost(¥0想定)/STOP有無/commit hash/raw URL。ユーザー向け表記はStandard/Advanced。
