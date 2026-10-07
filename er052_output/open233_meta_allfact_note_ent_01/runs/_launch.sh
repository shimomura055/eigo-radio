# usage: _launch.sh <p1|p2> <prefix> <phase> <budget>
m=$1; pre=$2; ph=$3; bud=$4
export OPEN233_RUNS_ROOT=er052_output/open233_meta_allfact_note_ent_01/runs OPEN233_B3_VARIANT=nb OPEN233_NOTE_PREFIX="$pre" PYTHONIOENCODING=utf-8 PYTHONUTF8=1
B=er052_output/open233_meta_allfact_note_ent_01
.venv/Scripts/python.exe er052_open233_polysemy_nb_dev_01.py --phase $ph --slug meta --theme "Meta Muse AI電話代行「人間コンシェルジュ」実験" --ledger-txt $B/ledger/$m/research_ledger/verified_fact_ledger.txt --out-dir $B/runs/meta/nb/$m/rep1 --budget-jpy $bud --yes-run-paid
