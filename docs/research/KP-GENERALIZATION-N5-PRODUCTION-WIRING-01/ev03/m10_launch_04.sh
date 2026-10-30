#!/bin/bash
cd "$(dirname "$0")/../../../.."
EV3=docs/research/KP-GENERALIZATION-N5-PRODUCTION-WIRING-01/ev03
PY=/c/Users/tensh/eigo-radio/.venv/Scripts/python.exe
c=untidi_b1b
py -3 tools/stop_scope_check_01.py --managed-id KP-GENERALIZATION-N5-PRODUCTION-WIRING-01 --run-dir $EV3 --out $EV3/stop_check_m10_$c.json > /dev/null; rc=$?
if [ $rc -eq 3 ]; then echo "STOP rc=3"; exit 3; fi
py -3 $EV3/launch_gate.py "m10_$c"
M10_CAP=31 PYTHONIOENCODING=utf-8 $PY $EV3/m10_run.py $c > $EV3/m10_$c.log 2>&1
echo "$c exit rc=$? $(date +%H:%M:%S)" >> $EV3/launches.txt
