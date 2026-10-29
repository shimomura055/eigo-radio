# FY-FZ-FEMALE-VOICE-RANK-01 委任_01 EVIDENCE_01(2026-10-29)

## 結論
女性Voice候補順位(Leda/Erinome/Sulafat/Kore/Zephyr)をY・Zの正式Production経路へ反映(コード・test・API 0確認完了)。実TTS送信の動作証拠は **Z Std/Adv=取得済み(Leda実送信)**、**Y Std/Adv=取得済み(委任_02、2026-10-29 18:16/18:20 JST、Leda実送信)**。委任_01では自起動3回でRESTART_STORMのSTOP(API 0)となったがFableが`--clear-stop`許可、委任_02で2起動(間隔約4分)で取得。全4組合せ揃う。

## 4組合せ表
| 組合せ | 順位反映(正式経路) | 実送信 voice_id (cost_log `tts_voice_sent`) | model_id | Style/routing | 費用 | 状態 |
|---|---|---|---|---|---|---|
| Z Std(a2) | `er062` 新規(pin無し)作品 `derive_dialogue_voice_tts_names`→`er063.resolve_dialogue_voice`=Leda(女性1位) / 男性Algieba不変 | **Leda** (`evidence/z/cost_log.jsonl` stage tts_a2 fvr_ev_a2_heroine、ASR一致) | gemini-2.5-pro-preview-tts | `er063.real_generators()["dialogue"]` Std=`bvoices.generate_voice_body_wide_margin`(既定Dialogue Style、速度後処理なし)、TTS_EXECUTION_MODE=STANDARD | 約¥0.5 | 取得済み |
| Z Adv(b1b) | 同上 | **Leda** (tts_b1b fvr_ev_b1b_heroine、ASR一致、最終成功1回) | gemini-2.5-pro-preview-tts | Adv=`generate_with_a2_slowdown_outer_loop`+slowdown 6%(Z_ADV_DIALOGUE_SLOWDOWN_PCT) | 約¥2(driver不具合の再実行2回分含む。Z合計 gemini TTS 4回・in1822/out500 tokens ≒¥2〜3) | 取得済み |
| Y Std(a2) | `er121_family_y_structure_01` 既定 `FIXED_VOICE_SLOTS`=Puck/**Leda**/Schedar。正式runnerが新規run dirで`voice_assignment.json`に`voice_2=Leda`を書出し(`evidence/y/voice_assignment.json`)、stage入力shaがVoice込みで変わりprovenance不一致STOP(再生成を要求=Voice変更が正式経路に届く証拠、API 0) | **Leda** (`evidence/y/cost_log.jsonl` 1行目 stage tts_a2 y_voice_2、ASR 2回目で一致[1回目不一致→attempt2成功]、y_voice_2 status OK) | gemini-3.8-flash-lite-tts | tts_backend=speech_metadata_flash_lite、TTS_EXECUTION_MODE=STANDARD | 約¥1.56 | 取得済み |
| Y Adv(b1b) | 同上 | **Leda** (stage tts_b1b y_voice_2 attempt1 成功、ASR 1回で一致、status OK) | gemini-3.8-flash-lite-tts | tts_backend=speech_metadata_flash_lite、STANDARD(b1bはY runnerの同backend) | 約¥1.39(累計¥2.94) | 取得済み |

Y実送信の再開手順(Fable): `python er121_family_y_runner_01.py --clear-stop --reason "..." --slug redelivery_fee --run run_fvr_ev_01`後、`--stages tts_a2 --regenerate-stage tts_a2 --only-segments y_voice_2`を1起動、150秒以上空けて`--stages tts_b1b --regenerate-stage tts_b1b --only-segments y_voice_2`を1起動(共通引数は`evidence/y/console_launch3.log`の履歴と同じ、`--approved-budget-jpy 15`、cost_logは複製元の過去行を空にしてある[`cost_log_inherited_from_style_fix_01.jsonl.bak`に退避])。

## 既存記事不変(API 0、`evidence/api0_unchanged_check_01.json`、tools/api0_unchanged_check_01.py)
- Y 16 run: 記録済み女性Voice(Zephyr 14件/Leda 2件[新規evidence run等])を`segment_voice_map(run_dir, level)`が返す(a2/b1b)。runner再起動時の`voice_assignment_record`も既存記録を上書きしない。fail=0。
- Z 46 run(全story): 記録済み話者Voice == 現行`derive_dialogue_voice_tts_names`(open_window/gift/monkeys_paw/in_a_grove の女性は`STORY_VOICE_PINS`で旧Zephyr/Kore維持)。diff=0。
- 男性: Y Puck/Schedar/Fenrir/Orus/Iapetus、Z Algieba/Schedar/Fenrir/Orus/Puck 不変(test固定)。旧記録にvoice_1=Algieba(除外済み)があるrunは従来どおり現行既定Puckに解決(記録値で上書きしない)。

## FIXED_VOICE_SLOTS判定
**(a)**: Yの`FIXED_VOICE_SLOTS`は候補表からの導出結果であり(`verify_voice_assignment`が`assign_dialogue_voices(ROSTER, pool=Y_DIALOGUE_VOICE_POOL)`との一致を強制、`er121_family_y_structure_01.py`)、特定Voiceを明示指定する配役仕様ではない(CURRENT_SPEC 3145『固定割当 Voice 1=Puck…Voice 2=Zephyr』は同時点の表からの導出結果)。よって新規制作は新順位(Voice 2=Leda)。既存記事は run dirの記録で保持。Zの明示pin(メロス Algieba/Erinome/Charon、告げ口心臓 Narrator=Fenrir)は不変。

## test
`er_female_voice_rank_test_01.py`(新規9件)+更新(er062 voice_assignment、er121 voice_table/audio_chunk/hr_approval_guard/runner/structure_match、er026 registry gift/monkeys/in_a_grove)。関連294 PASS。既知の他要因失敗3件(本変更と無関係): `er121_family_y_voice_table_test_01::test_existing_run_01_and_public_pages_not_modified`(他Workerが2026-10-29 16:45にrun_01/run_style_fix_01へ追記した`run_launch_log.jsonl`差分)、`er121_family_y_structure_match_test_01::test_a2_common_calls_not_dropped`(X共通呼出`RuntimeError`の追従、他Workerのer003等未commit差分)、er063系2件(`_narrator_inner`/`kwargs`、他Workerのer063未commit差分)。
