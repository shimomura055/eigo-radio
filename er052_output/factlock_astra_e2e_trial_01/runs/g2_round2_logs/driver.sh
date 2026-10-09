cd /c/Users/tensh/eigo-radio
R=er052_output/factlock_astra_e2e_trial_01/runs
L=$R/g2_round2_logs
C="--cap-jpy 1000 --alert-jpy 850 --allow-script-change"
run(){ # wid themes arms tag
  /c/Users/tensh/eigo-radio/.venv/Scripts/python.exe -X utf8 er052_factlock_astra_e2e_runner_01.py run --root $R --themes $2 --arms $3 --worker-id $1 $C > $L/worker$1_$4.stdout.log 2> $L/worker$1_$4.stderr.log; echo "rc=$?" >> $L/worker$1_$4.stdout.log; }
( run 3 space_weapons new,old resume_space_weapons; run 6 openai_copyright,semiconductor_earnings new,old r2_openai_semi ) &
( run 4 small_bag new,old resume_small_bag; run 7 streaming_price new,old r2_streaming ) &
( run 5 byd_recall,central_bank_mortgage new,old r2_byd_cbm ) &
wait
