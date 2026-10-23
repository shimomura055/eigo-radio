#!/bin/bash
# 全検証の再実行(cache経由=API 0、cache missのみ実API)。順序: 表構築→検出→HR replay→追補→同値→負例→失敗注入→安定性→4clip→集計
cd "$(dirname "$0")/../../../../.."
PY=.venv/Scripts/python.exe
T=docs/research/ASR-QUALITY-2ITEMS-COMPREHENSIVE-01/PN/TRIAL_01
for s in sc1_equivalence_01 ner_d3_run_01 sc2_sc3_detection_01 sc4_hr_replay_01 sc4b_followups_01 sc5_variants_01 sc6_failsafe_01 sc9_stability_01 bertie_stability_01 openwindow_4clip_01 sc7_sc8_summary_01; do
  echo "=== $s"; $PY $T/$s.py > $T/_log_$s.txt 2>&1; echo "rc=$?"; tail -2 $T/_log_$s.txt
done
