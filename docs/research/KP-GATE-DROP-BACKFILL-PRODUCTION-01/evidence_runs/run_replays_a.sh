#!/bin/bash
cd /c/Users/tensh/eigo-radio
for c in R1_X_ai_island_a2 R3_Y_redelivery_a2 R4_Y_sns_b1b R6_Z_melos_b1b; do
  PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/tools/replay_backfill_01.py $c docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/replay_results
done
