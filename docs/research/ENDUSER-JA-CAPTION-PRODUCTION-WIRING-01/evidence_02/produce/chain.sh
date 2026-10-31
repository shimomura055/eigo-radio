#!/bin/bash
# usage: chain.sh label key1 key2 ...  (API 0 produce chain; stop check before each)
S=/c/Users/tensh/AppData/Local/Temp/claude/C--Users-tensh-eigo-radio/7eda59a9-ca6c-4f6c-9eb5-2b973c0ca046/scratchpad
PY=/c/Users/tensh/eigo-radio/.venv/Scripts/python.exe
label=$1; shift
cd $S/capw
for k in "$@"; do
  run=$($PY -c "import sys;sys.path.insert(0,'.');from ejh_dirs import DIRS;print(DIRS['$k']['run'])")
  (cd $S/wt_cap && PYTHONUTF8=1 $PY tools/stop_scope_check_01.py --managed-id ENDUSER-JA-CAPTION-PRODUCTION-WIRING-01 --run-dir "$run" --out $S/capw/stop_$k.json >/dev/null)
  rc=$?
  if [ $rc -ne 0 ]; then echo "$k STOP_CHECK_rc=$rc ABORT $(date +%T)" >> status_$label.txt; exit 3; fi
  echo "$k start $(date +%T)" >> status_$label.txt
  PYTHONUTF8=1 $PY produce_one.py $k > produce_$k.log 2>&1
  echo "$k rc=$? $(date +%T)" >> status_$label.txt
done
echo CHAINDONE >> status_$label.txt
