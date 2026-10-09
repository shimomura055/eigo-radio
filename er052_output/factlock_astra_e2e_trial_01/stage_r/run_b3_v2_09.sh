#!/bin/bash
# 委任_09: B3再生成(各テーマ1回)。ledger凍結物を一時out-dirへコピーして再利用、storyline_b3のみ実行(research非実行)。v1は無改変。
# usage: run_b3_v2_09.sh slug budget
cd /c/Users/tensh/eigo-radio
export PYTHONUTF8=1
D=er052_output/factlock_astra_e2e_trial_01/stage_r
slug=$1; bud=$2
T=$D/_tmp_v2_$slug
rm -rf $T; mkdir -p $T
cp -r $D/$slug/research_ledger $T/research_ledger
topic=$(.venv/Scripts/python.exe -c "import json;print(json.load(open('$D/$slug/entry_point.json',encoding='utf-8'))['args']['theme'])")
.venv/Scripts/python.exe er019_family_x_entertainment_production_runner_01.py --theme "$topic" --slug "$slug" --out-dir $T --budget-jpy $bud --stage storyline_b3 --stop-after storyline_b3 > $T/stdout.log 2>&1
echo "exit=$?" >> $T/stdout.log
