#!/bin/bash
cd /c/Users/tensh/eigo-radio
for c in R2_X_uk_a2 R5_Z_monkeys_paw_b1b; do
  PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/tools/replay_backfill_01.py $c docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/replay_results
done
