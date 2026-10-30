#!/bin/bash
# M10 4level launcher(各caseを1回だけ起動。再試行なし)。起動前に stop_scope_check(rc=3なら即中止)+ launch_gate(>=150秒間隔・300秒窓<=2回)
cd "$(dirname "$0")/../../../.."
EV3=docs/research/KP-GENERALIZATION-N5-PRODUCTION-WIRING-01/ev03
PY=/c/Users/tensh/eigo-radio/.venv/Scripts/python.exe
for c in jwst_m_b1b untidi_a2 melos_a2 untidi_b1b; do
  py -3 tools/stop_scope_check_01.py --managed-id KP-GENERALIZATION-N5-PRODUCTION-WIRING-01 --run-dir $EV3 --out $EV3/stop_check_m10_$c.json > /dev/null; rc=$?
  if [ $rc -eq 3 ]; then echo "STOP rc=3 before $c"; exit 3; fi
  py -3 $EV3/launch_gate.py "m10_$c"
  PYTHONIOENCODING=utf-8 $PY $EV3/m10_run.py $c > $EV3/m10_$c.log 2>&1 &
  echo "$c PID=$! $(date +%H:%M:%S)" >> $EV3/launches.txt
done
wait
echo done >> $EV3/launches.txt
