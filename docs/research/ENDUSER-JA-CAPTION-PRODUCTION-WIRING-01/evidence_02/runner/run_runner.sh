#!/bin/bash
# usage: run_runner.sh x|y|z -- stop check -> launch gate -> 正式runner(code=wt_cap, cwd=rr mirror, API 0 shim)
S=/c/Users/tensh/AppData/Local/Temp/claude/C--Users-tensh-eigo-radio/7eda59a9-ca6c-4f6c-9eb5-2b973c0ca046/scratchpad
PY=/c/Users/tensh/eigo-radio/.venv/Scripts/python.exe
WT=$S/wt_cap; RR=/c/Users/tensh/eigo-radio; MAIN=/c/Users/tensh/eigo-radio; RW=$S/capw/rw
cd $S/capw
k=$1
case $k in
  x) runs=$MAIN/er019_output/family_x_audio_production_wiring_01/ai_chat_sponsored_persuasion__run_fx4_01; mod=er019_family_x_listening_page_01; args="--slug ai_chat_sponsored_persuasion --run-name run_fx4_01 --web $RW/xweb_ai_chat_sponsored_persuasion";;
  y) runs=$MAIN/er121_output/family_y_production_01/surname_choice/run_02; mod=er121_family_y_runner_01; args="--slug surname_choice --run run_02 --mode real --approved-budget-jpy 1 --stages pages,page_verify --theme-package $MAIN/docs/research/FAMILY-Y-SURNAME-CHOICE-PRODUCTION-01/theme_packages/surname_choice_package_01.json";;
  z) runs=$MAIN/er026_output/family_z_production_e2e_01/yuki_onna/run_yo_prod_01; mod=er026_family_z_fiction_production_runner_01; args="--story yuki_onna --run run_yo_prod_01 --mode real --approved-budget-jpy 1 --stages pages,page_verify --pages-dir $RW/zpages";;
esac
(cd $WT && PYTHONUTF8=1 $PY tools/stop_scope_check_01.py --managed-id ENDUSER-JA-CAPTION-PRODUCTION-WIRING-01 --run-dir $runs --out $S/capw/stop_runner_${k}.json >/dev/null)
rc=$?
if [ $rc -ne 0 ]; then echo "runner_$k STOP_CHECK_rc=$rc ABORT" >> status_runner.txt; exit 3; fi
$PY launch_gate.py "runner_${k}" >> job.out 2>&1
echo "CMD: $mod $args" > runner_${k}.log
echo "runner_$k start $(date +%T)" >> status_runner.txt
ECH_KEEP_CWD=1 PYTHONUTF8=1 $PY runner_shim.py $WT $RR $mod $args >> runner_${k}.log 2>&1
echo "runner_$k rc=$? $(date +%T)" >> status_runner.txt
