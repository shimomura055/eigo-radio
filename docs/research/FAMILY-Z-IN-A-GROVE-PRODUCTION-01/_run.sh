#!/bin/bash
# usage: _run.sh <tag> <stages>
cd /c/Users/tensh/eigo-radio
R=docs/research/FAMILY-Z-IN-A-GROVE-PRODUCTION-01
.venv/Scripts/python.exe tools/stop_scope_check_01.py --managed-id FAMILY-Z-IN-A-GROVE-PRODUCTION-01 --run-dir er026_output/family_z_production_e2e_01/in_a_grove/run_sf_prod_01 --out $R/_stop_scope_check_$1.json || { echo STOP_RC=$?; exit 3; }
TTS_EXECUTION_MODE=STANDARD .venv/Scripts/python.exe er026_family_z_fiction_production_runner_01.py --story in_a_grove --run run_sf_prod_01 --mode real --approved-budget-jpy 70 --tts-execution-mode STANDARD --stages "$2"
echo RC=$?
