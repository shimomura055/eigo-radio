#!/bin/bash
# 1起動分(stop確認→background起動→時刻記録)。引数: <plan> <batch> <label>
cd /c/Users/tensh/eigo-radio; T=docs/research/FAMILY-Y-VOICE1-MALE7-TRIAL-01
py tools/stop_scope_check_01.py --managed-id FAMILY-Y-VOICE1-MALE7-TRIAL-01 --run-dir er121_output/family_y_voice1_male7_trial_01 --out $T/logs/stop_check_$3.json >/dev/null || { echo "STOP rc!=0"; exit 3; }
echo "launch $3 $(date +%H:%M:%S)" >> $T/logs/launch_times.txt
(PYTHONUNBUFFERED=1 TTS_EXECUTION_MODE=STANDARD nohup .venv/Scripts/python.exe $T/tools/ym7_generate_01.py --plan $T/$1 --batch $2 --out er121_output/family_y_voice1_male7_trial_01 --budget-jpy 40 > $T/logs/gen_$3.log 2>&1 &)
