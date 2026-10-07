#!/bin/bash
# A4: 並列度2に固定(クラッシュ対策、brief既存はskip)。
# 段階2 step1: 追加B3 V0/V1/V3/V6 x 3テーマ x b3,b4 = 24本
cd "$(dirname "$0")/../../.."
job() { v=$1; s=$2; i=$3
  [ -f er052_output/open233_b3_trial_01/runs/$s/nb/$v/b$i/storyline_b3/selected_brief.md ] && { echo "$s $v b$i skip(existing)"; return 0; }
  .venv/Scripts/python.exe er052_output/open233_b3_trial_01/tools/run_b3_variant.py --variant $v --slug $s \
   --out-dir er052_output/open233_b3_trial_01/runs/$s/nb/$v/b$i --budget-jpy 5 --yes-run-paid \
   > er052_output/open233_b3_trial_01/logs/${s}_${v}_b$i.log 2>&1; echo "$s $v b$i rc=$?"; }
export -f job
for v in V0 V1 V3 V6; do for s in meta hormuz space_weapons; do for i in 3 4; do echo "$v $s $i"; done; done; done | xargs -P 2 -L 1 bash -c 'job $0 $1 $2'
