#!/bin/bash
# 6件のフォームJSONを生成(API 0)。入力のcandidate docは各fresh run / replayの出力(読み取りのみ)。
cd /c/Users/tensh/eigo-radio
export PYTHONIOENCODING=utf-8
D=docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01
FD=user_test/selection_form_v3/data
PY=".venv/Scripts/python.exe $D/tools/export_form_data_01.py"
X=er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_kpbf_ev_01
Y=er121_output/family_y_production_01/redelivery_fee/run_kpbf_ev_01/key_phrases
M=er026_output/family_z_production_e2e_01/melos/run_kpbf_ev_01/key_phrases
NOTE_P="Production正式経路(KP stage・補完機能ON)で生成した候補です。選定フォームのテスト表示で、Production未連携。"
$PY --cand $X/a2/key_phrases/kp_candidates.json --slug ai_island_temple_prod --level a2 --name "AIの仮想の島｜Production候補・補完evidence" --family X --run ai_island_temple__run_kpbf_ev_01 --note-ja "$NOTE_P" --out $FD/ai_island_temple__a2__prod.json
$PY --cand $X/b1b/key_phrases/kp_candidates.json --slug ai_island_temple_prod --level b1b --name "AIの仮想の島｜Production候補・補完evidence" --family X --run ai_island_temple__run_kpbf_ev_01 --note-ja "$NOTE_P" --out $FD/ai_island_temple__b1b__prod.json
$PY --cand $Y/a2/kp_candidates.json --slug redelivery_fee_prod --level a2 --name "再配達手数料｜Production候補・補完evidence" --family Y --run redelivery_fee/run_kpbf_ev_01 --note-ja "$NOTE_P" --out $FD/redelivery_fee__a2__prod.json
$PY --cand $Y/b1b/kp_candidates.json --slug redelivery_fee_prod --level b1b --name "再配達手数料｜Production候補・補完evidence" --family Y --run redelivery_fee/run_kpbf_ev_01 --note-ja "$NOTE_P" --out $FD/redelivery_fee__b1b__prod.json
$PY --cand $M/a2/kp_candidates.json --slug melos_prod --level a2 --name "走れメロス｜Production候補・補完evidence" --family Z --run melos/run_kpbf_ev_01 --note-ja "$NOTE_P" --out $FD/melos__a2__prod.json
$PY --cand $D/replay_results/R5a_Z_monkeys_paw_b1b_frozen_only/kp_candidates_doc.json --slug monkeys_paw_prod --level b1b --name "猿の手｜Production候補・補完evidence" --family Z --run replay:R5a_Z_monkeys_paw_b1b_frozen_only --source-kind REPLAY_FROZEN_INITIAL_REAL_BACKFILL --note-ja "Production候補生成関数(補完機能ON)に、過去run(現行方式)の初回出力を凍結して通した候補です(猿の手はseed更新によりrunner経由の再生成が止まるため)。Gate除外が起きなかったため補完は未発動。Production未連携。" --text-sha256 8388280adba421ba866222a9ee43f9af2411fb3cb88e012b02b5cfc7548f42d7 --out $FD/monkeys_paw__b1b__prod.json
