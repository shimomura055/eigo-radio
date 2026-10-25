# RUNTIME_EVIDENCE_01(FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01 委任_02 Step C)

Status候補: X=WIRED_PENDING_FABLE / Z=WIRED_PENDING_FABLE(PRODUCTION_WIREDはFable判定)。事実のみ。公開ページの差替えなし(候補は`user_test/`)。
使用モデル: TTS=speech_metadata_flash_lite(Production承認backend、評価用の新旧モデル比較なし)。承認方式はX=B0.2 / Z=B_r1(追加Trial・方式変更なし)。

## 1. X(『英国の電車マナー』 uk_train_speaker_playback)
- 入力: `er019_output/family_x_audio_production_wiring_01/uk_train_speaker_playback__run_nws_02`をraw_usage_log.jsonlを除いて丸ごとcopy → `..._run_chunk_01`(旧結果は親entryのみ=chunk化前)。記録Style profile=`fx_20261017`=現行既定`DEFAULT_NEW_RUN_PROFILE`(`er019_family_x_style_profile_01.py:188`)と一致(課金前確認)。`b1b/assembled/*.wav`は削除して再組立。
- 実行(正式runner CLI): `--stage study_text`(Part 1未生成のため必須、0.13円)→`--stage tts --level b1b`(2.51円、wall 13:27:02〜13:45:54=約18.9分)→`--stage assemble`→`--stage player`。`--budget-jpy 20`。STOP helper rc=0(`stop_check_chunk_x_tts*.json`)。
- Chunk計画(親の語数→chunk): Part1 150語=[63,14,30,43] / Part2 152語=[58,52,42] / Part3 126語=[34,53,39]、全て`boundary_kind=paragraph`。凍結Trial planner fixture(`planner_fixture_01.json` x_parts)と語数・本文shaまで一致。
- 結果: chunk entry 10件すべてstatus=OK、ASR=primary_pass、attempt 1回(`er011_output/attempt_history.jsonl` theme=`uk_train_speaker_playback__run_chunk_01` 10行・最大1回)、Local Rewrite 0・audio_text_deviation 0・HR(human_review_queue)新規行 0・fallback 0。
- 親aggregate entry: 3件とも`status=OK`、`chunk_gate_statuses`全VALIDATED。親wav = raw chunk PCMの0.2秒(4800 sample@24kHz)無音連結が**整数sample一致**(`runtime_evidence_chunk_x.json` parent_concat_check 3件 equal=True)。
- M1(Style profile M3 Gate): `b1b/audit/style_profile_gate.json` status=PASS、checkedは**chunk entry 10件**(`full_story_part{1,2,3}_k*`)+kp/preview、親は対象外、blocked=[]。
- 組立: chunk別scalar gain(target_rms共通)、post_rms全chunk同値、peak_capped全てfalse(`audit/chunk_tts_assembly_b1b.json`)。通し音声内の0.2秒gap 7箇所を実測(`assembled_gap_check`): 長さ0.200秒、gap内max|x|≤0.0012(≒-58.7dBFS以下、48kHz変換のring程度)。Advanced通し 290.44秒(旧nws_02 280.84秒。Full Story Part 1/2/3 = 55.44/50.49/43.59秒、旧 53.48/47.48/38.96秒)。
- 既存headroom機構: peak_before=0.987(Full Story Part 2)>0.98のため既存の全体scalar 0.9929(-0.06dB)が適用された(旧nws_02は未適用)。既存仕様どおりの動作であり変更なし。
- 候補ページ: `user_test/uk_train_speaker_playback_chunk_01/index.html`(`er019_nws2_final_page_01.py`でStd=旧runのa2 copy、Adv=chunk版)、標準適合check overall=PASS(17項目、`page_standard_check.json`)。公開ページ差替えなし。
- 実費: 合計2.64円(openai 0.13=Part 1、gemini_batch 1.80、openai_asr 0.71)。Cap 60円内。

## 2. Z(『告げ口心臓』 the_tell_tale_heart)
- 入力: `run_sf_prod_02`から`copy_reusable_run_assets`(許可リスト、ALLOW 73/DENY 157、計画=`run_chunk_01/run_chunk_01_copy_plan.json`)で`run_chunk_01`を新規作成。writer/segment_plan/KP/supportを再利用。
- 実行(1起動、`run_launch_log.jsonl`): `--mode real --approved-budget-jpy 60 --tts-execution-mode STANDARD --stages kp,tts_b1b,tts_a2,provision_shell,gate,assemble`(provision_shell含む。pages/page_verifyは公開ページ上書きを避け実行せず、下記候補ページのみAPI 0で別途構築)。STOP helper rc=0、STOP_ALL・RUN STOPなし、他agentのZ TTSなし。rc=0(再起動0)。
- 所要: kp 17.4秒 / tts_b1b 178.7秒 / tts_a2 201.0秒 / provision_shell 0.2秒 / gate 1.3秒 / assemble 5.5秒。
- Chunk計画: Advanced narratorの100語超2 clip。`full_story_part2_c1`=[58,62]・`full_story_part3_c1`=[65,61]、いずれも段落境界(`boundary_kind=paragraph`)。凍結Trial plannerの`run_sf_prod_02`期待値(委任文の承認Trial対象)と完全一致。引用内切断なし。
- 結果: Advanced 22 entry全てOK(chunk 4件含む、ASR=primary_pass)、Standard 19 entry全てOK。Local Rewrite 0・audio_text_deviation 0・新規HR行 0。retry: Adv `full_story_part1_c3`(会話)と Std 5 clipが各2回目で通過(非chunk clip・既存retry上限内)。chunk clipは全て1回。
- 親aggregate entry: 2件`status=OK`、chunk_gate_statuses全VALIDATED、parent_sha256==raw_parent_sha256、親wav=chunk PCM+0.2秒の整数sample一致(`runtime_evidence_chunk_z.json`)。
- 共有Gate: `gate_result_04C.json` shared_gate=PASS(a2/b1b)、m2_complete=true。速度Gate(z_speed_v2)はchunk id(`full_story_part2_c1_k1`等)を対象に`adv_narrator_none` ok。
- 組立: `b1b/assembly/timeline.json`の`chunk_tts`にchunk別gain(part2_c1: 1.1303/0.9690、part3_c1: 1.2536/0.8462)・peak_capped false・0.2秒gap(episode内188.516〜188.716秒/249.376〜249.576秒、実測max|x|≤0.0004)。Advanced 280.6秒、headroom適用なし。
- 候補ページ: `user_test/family_z_tell_tale_heart_chunk_01/`(`stage_pages`をpages_dir上書きのctxで実行、API 0)、標準適合check overall=PASS。公開ページ(`user_test/family_z_tell_tale_heart_01`)は未変更。
- 実費: 16.67円(kp 0.14 + tts_b1b 6.85 + tts_a2 9.68)。Cap 60円内。
- 候補ページpage_verify(委任_04、2026-10-25 14:43〜14:45 JST、API 0): er026 runnerへ`--pages-dir`(未指定=従来の公開dir)を追加し、`--story the_tell_tale_heart --run run_chunk_01 --mode real --approved-budget-jpy 1 --stages pages,page_verify --pages-dir user_test/family_z_tell_tale_heart_chunk_01`を1起動で実行(rc=0、cost_log追記0・spent 16.6657円のまま)。pages再生成後も候補ページはgit差分0・audio_standard/audio_advanced 55ファイルのsha256が実行前と同一。公開ページ`user_test/family_z_tell_tale_heart_01`はgit status差分0(実行前後)。page_verify(Playwright --local、`run_chunk_01/page_verify_local.json`、控え=`page_verify_local_z_chunk_01.json`): index(audio 34・plays_ok 34)/standard(audio 26・plays_ok 26)/advanced(audio 24・plays_ok 24)すべてhttp 200・plays_failed 0・console_errors 0・http_ge400 0、標準適合check overall=PASS。seek_ok_all=Falseはhttp.serverがRange非対応による既知の偽陰性(合否に含めない、evaluate_page_verify仕様)。

## 3. 費用・日次
- 起動前の日次(JST 2026-10-25、`daily_dev_cost_01.py`): X前 838.7円 → Z前 845.35円(他agent分含む)。本委任の実費合計=約19.3円(X 2.64+Z 16.67)。日次1,000円内。
