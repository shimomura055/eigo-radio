B=er052_output/open233_allfact_note_e2e_02
for j in "meta 2" "hormuz 1" "hormuz 2" "space_weapons 1" "space_weapons 2" "sewer 1" "sewer 2" "ai_control 1" "ai_control 2"; do set -- $j; s=$1; r=$2; R=$B/runs/$s/nb/p2/rep$r
 ( for i in $(seq 1 360); do
     if [ -f $R/ja_writer/revision2.md ] && [ -f $R/cost.json ] && grep -q '"exit_reason"' $R/nb_provenance_phase1.json; then
       python $B/tools/check_brief_transfer.py $R/storyline_b3/selected_brief.md $B/ledger/$s/research_ledger/verified_fact_ledger.txt --json-out $R/brief_transfer_check.json > /dev/null 2>&1
       bash $B/tools/launch.sh $s $r phase2 15 > $B/runs/_logs/${s}_rep${r}_p2.log 2>&1; break
     fi
     grep -q "Traceback\|SystemExit" $B/runs/_logs/${s}_rep${r}_p1.log && break
     sleep 5; done ) &
done
wait
