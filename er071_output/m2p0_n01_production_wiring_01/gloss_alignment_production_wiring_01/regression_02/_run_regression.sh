#!/bin/bash
# KGCPW 委任_02 Regression(直列・単独)。OPENAI_API_KEY空。有料API 0。
cd /c/Users/tensh/eigo-radio
export OPENAI_API_KEY=""
export PYTHONUTF8=1
D=er071_output/m2p0_n01_production_wiring_01/gloss_alignment_production_wiring_01/regression_02
for pat in "er003*_test_*.py" "er019*_test_*.py" "er026*_test_*.py" "er062*_test_*.py" "er063*_test_*.py" "er030*_test_*.py"; do
  name=$(echo "$pat" | sed 's/[*.]//g; s/_test_py//')
  echo "=== $pat" 
  .venv/Scripts/python.exe run_project_regression.py --pattern "$pat" --json-summary $D/summary_${name}.json > $D/${name}.log 2>&1
  echo "rc=$? $pat" | tee -a $D/_rc.txt
done
.venv/Scripts/python.exe -m pytest er008_audio_validation_gate_05_test.py -q > $D/er008_gate.log 2>&1
echo "rc=$? er008" | tee -a $D/_rc.txt
echo DONE >> $D/_rc.txt
