k=$1
export OPEN233_RUNS_ROOT=er052_output/open233_meta_rollback_minimal_note_01/runs OPEN233_B3_VARIANT=nb PYTHONIOENCODING=utf-8
B=er052_output/open233_meta_rollback_minimal_note_01
.venv/Scripts/python.exe er052_open233_polysemy_nb_dev_01.py --phase phase1 --slug meta --theme "Meta Muse AI電話代行「人間コンシェルジュ」実験" --ledger-txt $B/ledger/nb/research_ledger/verified_fact_ledger.txt --out-dir $B/runs/meta/nb/rep$k --budget-jpy 8 --yes-run-paid
