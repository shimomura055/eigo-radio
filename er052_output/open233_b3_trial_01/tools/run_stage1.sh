#!/bin/bash
# 段階1: B3 brief生成 V0/V1/V2/V3/V6 x 3テーマ x 2回 (V5は実行しない)
cd "$(dirname "$0")/../../.."
job() { v=$1; s=$2; i=$3
  .venv/Scripts/python.exe er052_output/open233_b3_trial_01/tools/run_b3_variant.py --variant $v --slug $s \
   --out-dir er052_output/open233_b3_trial_01/runs/$s/nb/$v/b$i --budget-jpy 5 --yes-run-paid \
   > er052_output/open233_b3_trial_01/logs/${s}_${v}_b$i.log 2>&1; echo "$s $v b$i rc=$?"; }
export -f job
for v in V0 V1 V2 V3 V6; do for s in meta hormuz space_weapons; do for i in 1 2; do echo "$v $s $i"; done; done; done | xargs -P 5 -L 1 bash -c 'job $0 $1 $2'
