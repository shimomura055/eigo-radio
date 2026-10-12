# BUILD_PLAN_V4 (FAMILY-X-COFFEE-P8-FINAL-AUDIO-AND-PRODUCTION-WIRING-01 委任_01A、2026-10-12、Trial隔離、Production配線ではない)
- 変更: Full Story Part1〜3 x Std/Adv の6本のみ P8 で全編再生成。Std は生成後 apply_a2_slowdown(6%)。他role(Intro/Preview/Comment/KP/In One Line/固定音源)は v3 と同一wav(sha照合: provenance_diff_v4_{std,adv}.json、不変 27/26 role)。
- 原稿: v3 canonical tts_input と sha256一致(assert)。Prompt: prompts_aoede_style_03.md のP8逐語(assert)。
- 経路: er057_coffee_final_v4_gen_01.py (v3 gen流用、Primary ASR -> 非verified時Secondary cascade、最大3 attempt、HR到達は不採択)、er057_coffee_final_v4_build_01.py (v3 build流用、assembler無改変)。
- 結果: 6本とも attempt1 でPrimary ASR採択(Secondary/HR未発生)。実費 JPY9.48 / 上限JPY30。
- 出力: final_v4/Coffee_{Standard,Advanced}_final_v4.{wav,mp3}、試聴 user_test/coffee_final_v4/。
