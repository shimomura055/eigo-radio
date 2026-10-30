#!/bin/bash
cd /c/Users/tensh/eigo-radio
slug=$1; name=$2
O=er019_output/family_x_audio_production_wiring_01/${slug}__run_fx4_01
for lv in a2 b1b; do
  PYTHONUTF8=1 .venv/Scripts/python.exe docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/tools/export_form_data_01.py --cand $O/$lv/key_phrases/kp_candidates.json --slug $slug --level $lv --name "$name" --family X --out user_test/selection_form_v3/data/${slug}__${lv}__prod.json --run er019_output/$slug/run_fx4_01 --grammar-study-dir $O/$lv/study_text --note-ja "FAMILY-X-SELECTED-4-ARTICLES-PRODUCTION-01 正式Production経路(fulltext_p2)" 
  echo "$slug $lv rc=$?"
done
