# COST_ESTIMATE_01 (FAMILY-X-STD-JA-S3-ADOPTION-AND-WIRING-01 委任_03 Phase B, 2026-10-17, API 0)

## 結論: 想定外の「Std全再生成」が判明 → T-2追記(4)に従い有料API実行前にSTOP(Fable判断待ち)

委任文の前提「Full Story/KP/IOL/固定shellはMaster Audio Storeのsha一致で再利用され新規生成0」は成立しない。コード上の事実:
- Master Audio Store(`er006_master_audio_store_01.py`)で再利用されるのは (1) 固定shell/共通narration (`shared_narration.ensure_all_shared_narration_a2`) と (2) KP英語(K2、`er019_family_x_kp_en_k2_store_01.py`、同一KP文面のときのみ)だけ。
- `topic_intro` / `japanese_title` / `preview` / `comment_1〜4` / `full_story_part1〜3` / `in_one_line` / `kp*_japanese_meaning` は `_generate_or_reuse`(er019_family_x_audio_production_runner_01.py:626-666)で **同一out_dirの前回results(`audit/tts_generation_results.json`)のみ**を再利用する。新out_dirには前回resultsが無いので全て再生成になる。R2版のStore entryはmanifestにこれらのkeyを持たない(R2 run `tts_generation_results.json`のsegmentsに`master_audio_key`無し)。
- SUPPORT_JA(preview/comment_1〜4)はMaster Storeのkey対象外(Style sha/versionがkeyに含まれるかを問う以前に、Store非経由)。R2音声がS3として再利用される経路は無い(per-run cacheは同一out_dir+現在profile記録でのみ有効)。

## 費用見積(実測ベース: R2版 coffee_prices__run_fxpw_01/raw_usage_log.jsonl を `compute_cost_jpy_so_far` で集計、a2+b1b両level)
- R2版 run全体(scaffold+tts、a2+b1b): JPY21.38(openai 2.38 / gemini TTS 13.06 / openai_asr 3.62 / azure 2.32)。うちscaffold(KP選定等) JPY2.36。
- Std(a2)のみの新規フル生成(scaffold + tts + ASR)の想定: 上記のうちa2分 = 期待 約JPY10〜14、最悪(技術失敗retry込み) 上限 JPY21.4(=R2版両levelの実測合計)。Adv(b1b)は実行しない。
- 委任上限(Guardrail) JPY40 / 7-7の100円閾値 / 日次soft budget JPY1,000(本日使用済み約JPY44)のいずれも超過しない見込み。
- 本日累計見込み: 約JPY44 + 約JPY10〜14 = 約JPY54〜58(最悪 約JPY66)。

## 実行しなかった理由
委任文T-2追記(4)「想定外の全再生成と判明した場合はAPI実行前にSTOPし報告」を優先した。費用面は上記のとおりGuardrail内(Fable判断で実行承認されれば即実行可)。

## 実施済み(API 0)
- `--stage plan`(`TTS_EXECUTION_MODE=STANDARD`、Style/backend CLI指定なし、`--out-dir`のみ指定): `entry_point.json` style_profile=fx_20261017 / style_profile_source=default_new_run_fx_20261017 / `audit/style_profile.json` SUPPORT_JA sha=060c08fd…(199字)。
- 実行コマンド: `TTS_EXECUTION_MODE=STANDARD .venv\Scripts\python.exe er019_family_x_audio_production_runner_01.py --slug coffee_prices --run run_fxpw_01 --out-dir er019_output/family_x_audio_production_wiring_01/coffee_prices__run_fxpw_01_s3prod --level a2 --stage plan`
- R2 run dir 207ファイルのsha256 before/after一致(`audit/r2_run_integrity_before_after_01.json`)。

## Fable承認後の実行コマンド(同一out_dir、順に実行。全て `--budget-jpy 40` `TTS_EXECUTION_MODE=STANDARD`)
1. `... --slug coffee_prices --run run_fxpw_01 --out-dir <上記OUT> --level a2 --stage scaffold --budget-jpy 40`
2. `... --stage tts --budget-jpy 40`
3. `... --stage assemble`
4. `... --stage player`
