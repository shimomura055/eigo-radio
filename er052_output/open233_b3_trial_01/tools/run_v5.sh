#!/bin/bash
cd "$(dirname "$0")/../../.."
job() { s=$1; i=$2; v=V5
  .venv/Scripts/python.exe er052_output/open233_b3_trial_01/tools/run_b3_variant.py --variant $v --slug $s \
   --out-dir er052_output/open233_b3_trial_01/runs/$s/nb/$v/b$i --budget-jpy 5 --yes-run-paid \
   > er052_output/open233_b3_trial_01/logs/${s}_${v}_b$i.log 2>&1; echo "$s $v b$i rc=$?"; }
export -f job
for s in meta hormuz space_weapons; do for i in 1 2 3 4; do echo "$s $i"; done; done | xargs -P 6 -L 1 bash -c 'job $0 $1'
