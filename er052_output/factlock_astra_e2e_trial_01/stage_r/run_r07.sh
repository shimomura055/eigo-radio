#!/bin/bash
# usage: run_r07.sh slug topickey budget
cd /c/Users/tensh/eigo-radio
export PYTHONUTF8=1
D=er052_output/factlock_astra_e2e_trial_01/stage_r
slug=$1; key=$2; bud=$3
topic=$(.venv/Scripts/python.exe -c "import json;print(json.load(open('$D/topics.json',encoding='utf-8'))['$key'])")
mkdir -p $D/$slug
.venv/Scripts/python.exe er019_family_x_entertainment_production_runner_01.py --theme "$topic" --slug "$slug" --out-dir $D/$slug --budget-jpy $bud --stage storyline_b3 --stop-after storyline_b3 >> $D/$slug/stdout.log 2>&1
echo "exit=$?" >> $D/$slug/stdout.log
