#!/bin/bash
S=/c/Users/tensh/AppData/Local/Temp/claude/C--Users-tensh-eigo-radio/7eda59a9-ca6c-4f6c-9eb5-2b973c0ca046/scratchpad/ech_out
PY=/c/Users/tensh/eigo-radio/.venv/Scripts/python.exe
cd $S
for k in "$@"; do
  runs=$($PY -c "import sys;sys.path.insert(0,'.');from ejh_dirs import DIRS;print(DIRS['$k']['run'])")
  (cd /c/Users/tensh/ech02 && PYTHONUTF8=1 $PY tools/stop_scope_check_01.py --managed-id ENDUSER-CLICK-HIGHLIGHT-NO-SEEK-01 --run-dir $runs --out $S/stop_${k}.json >/dev/null)
  rc=$?
  if [ $rc -ne 0 ]; then echo "$k STOP_CHECK_rc=$rc ABORT" >> status.txt; exit 3; fi
  $PY launch_gate.py "prod_${k}" >> job.out 2>&1
  PYTHONUTF8=1 $PY ech_produce.py $k > produce_${k}.log 2>&1
  echo "$k rc=$? $(date +%H:%M:%S)" >> status.txt
done
echo JOBDONE >> status.txt
