#!/bin/bash
# usage: run_theme.sh slug  (reads topic from topics.json)
cd /c/Users/tensh/eigo-radio
export PYTHONUTF8=1
D=er052_output/factlock_astra_e2e_trial_01/stage_r
slug=$1
topic=$(python -c "import json,sys;print(json.load(open('$D/topics.json',encoding='utf-8'))['$slug'])")
mkdir -p $D/$slug
.venv/Scripts/python.exe er019_family_x_entertainment_production_runner_01.py --theme "$topic" --slug "$slug" --out-dir $D/$slug --budget-jpy 30 --stage storyline_b3 --stop-after storyline_b3 > $D/$slug/stdout.log 2>&1
echo "exit=$?" >> $D/$slug/stdout.log
