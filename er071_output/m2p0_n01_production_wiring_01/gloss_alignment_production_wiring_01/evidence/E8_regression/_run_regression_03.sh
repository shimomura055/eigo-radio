#!/bin/bash
# KGCPW 委任_03 E8 Regression(直列・単独)。OPENAI_API_KEY空、有料API 0。委任_02と同条件(er003/er019/er026のみ)。
cd /c/Users/tensh/eigo-radio
export OPENAI_API_KEY=""
export PYTHONUTF8=1
D=er071_output/m2p0_n01_production_wiring_01/gloss_alignment_production_wiring_01/evidence/E8_regression
for pat in "er003*_test_*.py" "er019*_test_*.py" "er026*_test_*.py"; do
  name=$(echo "$pat" | sed 's/[*.]//g; s/_test_py//')
  .venv/Scripts/python.exe run_project_regression.py --pattern "$pat" --json-summary $D/summary_${name}.json > $D/${name}.log 2>&1
  echo "rc=$? $pat" >> $D/_rc.txt
done
echo DONE >> $D/_rc.txt
