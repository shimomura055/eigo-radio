B=er052_output/open233_allfact_note_e2e_02; s=sewer; r=2; R=$B/runs/$s/nb/p2/rep$r
bash $B/tools/launch.sh $s $r phase1 8 > $B/runs/_logs/${s}_rep${r}_p1.log 2>&1
if [ -f $R/ja_writer/revision2.md ]; then
 python $B/tools/check_brief_transfer.py $R/storyline_b3/selected_brief.md $B/ledger/$s/research_ledger/verified_fact_ledger.txt --json-out $R/brief_transfer_check.json >/dev/null 2>&1
 bash $B/tools/launch.sh $s $r phase2 15 > $B/runs/_logs/${s}_rep${r}_p2.log 2>&1
fi
