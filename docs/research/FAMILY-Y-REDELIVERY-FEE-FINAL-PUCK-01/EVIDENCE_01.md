# EVIDENCE_01 — Voice 1 runtime evidence(機械可読=`evidence_01.json`)
run: ev run(BUILD_01)。結果元=`{a2,b1b}/audit/tts_generation_results.json`、`cost_log.jsonl`。
| 項目 | Std(a2) | Adv(b1b) |
|---|---|---|
| y_voice_1 `voice`/`y_tts_voice_requested` | Puck/Puck | Puck/Puck |
| model/backend | gemini-3.8-flash-lite-tts / speech_metadata_flash_lite | 同左 |
| TTS mode | STANDARD(cost_log `tts_execution_mode`) | STANDARD |
| attempt数 | 1(`attempts_log`長1) | 1 |
| ASR | PASS(`primary_pass_approved_equivalence:TIER1_NUMERIC_EQUIVALENCE`、NUMERIC_EQUIVALENCE_MATCH) | PASS(`primary_pass`、EXACT_MATCH) |
| Repetition QA | checked、flagged=False | checked、flagged=False |
| 長さ | 41.698秒(減速前39.35、比1.0597=6%減速、`slowdown_applied=True`) | 39.52秒 |
| Voice 2/3 | Zephyr/Schedar(再利用、wav sha不変) | 同左 |
| 最終wav sha(先頭) | 8432ffbc0a85 | 170d856ba5f9 |
**使用Style prefix(Voice 1、`style_prefix`欄)**: Adv=`calm, steady news narration with natural emphasis at key points and turns; not dramatic.`、Std=同文+「Speak at a slightly slower, relaxed pace…」(EVIDENCE_02)。`STYLE_PROFILE="default"`のまま=現行公開版(`_01`)と同一Style。U-15(Y Style profile疑義)は未解決のまま(別途ユーザー判断)。
**長ポーズ(-40 dBFS・>=150 ms、`yvp_measure_lib_01.measure_wav`をVoice 1最終wavに適用)**: Std y_voice_1: ge1000=1(1090 ms、`redelivery.`と`I`の間=文境界)、文中>=1.0秒=0、max 1090 ms。Adv y_voice_1: ge1000=0、max 860 ms。参考(再利用のVoice 2/3、判定外): ge1000 Std v3=1・Adv v3=2、いずれも文境界。
**再利用**: 他narration wav 67本がrun_01とsha一致、変更/新規はa2 `y_voice_1`・`y_voice_1_original`・b1b `y_voice_1`の3本のみ。
**Gate**: y_style_profile_gate a2/b1b PASS(violations []); 組立 a2 342.261秒・b1b 315.85秒 OK・clipping無し(peak 0.866/0.867); page_verify ok=True、violations []; key_phrase_source_gate PASS。
