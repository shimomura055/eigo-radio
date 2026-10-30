#!/bin/bash
# usage: launch_one.sh <label> <stop-run-dir> <est_jpy> <inflight_jpy> -- <command...>   (1回だけ起動。再試行なし)
# 順序: stop_scope_check(rc=3で中止) -> 費用台帳guard(rc=3で中止) -> launch_gate(>=150秒・300秒窓<=2) -> 起動(バックグラウンド、PID記録)
cd "$(dirname "$0")/../../../.."
EV3=docs/research/KP-GENERALIZATION-N5-PRODUCTION-WIRING-01/ev03
PY=/c/Users/tensh/eigo-radio/.venv/Scripts/python.exe
label=$1; rundir=$2; est=$3; infl=$4; shift 5
py -3 tools/stop_scope_check_01.py --managed-id KP-GENERALIZATION-N5-PRODUCTION-WIRING-01 --run-dir "$rundir" --out $EV3/stop_check_$label.json > /dev/null; rc=$?
if [ $rc -eq 3 ]; then echo "STOP rc=3 before $label" | tee -a $EV3/launches.txt; exit 3; fi
$PY $EV3/ledger.py --check $est --inflight $infl >> $EV3/ledger_log.txt; rc=$?
if [ $rc -eq 3 ]; then echo "LEDGER GUARD stop before $label" | tee -a $EV3/launches.txt; exit 3; fi
py -3 $EV3/launch_gate.py "$label"
PYTHONIOENCODING=utf-8 PYTHONUTF8=1 "$@" > $EV3/console_$label.log 2>&1 &
echo "$label PID=$! $(date +%H:%M:%S) cmd: $*" >> $EV3/launches.txt
wait $!
echo "$label exit rc=$? $(date +%H:%M:%S)" >> $EV3/launches.txt
