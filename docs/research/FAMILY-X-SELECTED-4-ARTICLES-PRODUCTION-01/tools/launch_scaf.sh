#!/bin/bash
# usage: launch_scaf.sh <slug> <HHMMSS_not_before>
cd /c/Users/tensh/eigo-radio
T=er_fx4_scratch; slug=$1
until [ "$(date +%H%M%S)" -ge "$2" ]; do sleep 3; done
O=er019_output/family_x_audio_production_wiring_01/${slug}__run_fx4_01; mkdir -p $O
PYTHONUTF8=1 .venv/Scripts/python.exe tools/stop_scope_check_01.py --managed-id FAMILY-X-SELECTED-4-ARTICLES-PRODUCTION-01 --run-dir $O --out $T/stop_s_$slug.json >/dev/null; rc=$?; echo stop_rc=$rc
[ $rc -eq 3 ] && exit 3
date +"%F %T" >> $T/launch_times.txt; echo "$slug scaffold start" >> $T/launch_times.txt
PYTHONUTF8=1 .venv/Scripts/python.exe er019_family_x_audio_production_runner_01.py --slug $slug --run run_fx4_01 --stage scaffold --level both --budget-jpy 60 > $T/scaf_$slug.log 2>&1
echo "scaffold rc=$?" >> $T/launch_times.txt
