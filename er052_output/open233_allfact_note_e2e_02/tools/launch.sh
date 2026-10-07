# usage: launch.sh <slug> <rep> <phase> <budget>
slug=$1; rep=$2; ph=$3; bud=$4
export OPEN233_RUNS_ROOT=er052_output/open233_allfact_note_e2e_02/runs OPEN233_B3_VARIANT=nb OPEN233_NOTE_PREFIX="注意:" PYTHONIOENCODING=utf-8 PYTHONUTF8=1
B=er052_output/open233_allfact_note_e2e_02
.venv/Scripts/python.exe er052_open233_polysemy_nb_dev_01.py --phase $ph --slug $slug --theme "er052_output/open233_polysemy_trial_02/ledgers/$slug/topic.txt" --ledger-txt $B/ledger/$slug/research_ledger/verified_fact_ledger.txt --out-dir $B/runs/$slug/nb/p2/rep$rep --budget-jpy $bud --yes-run-paid
