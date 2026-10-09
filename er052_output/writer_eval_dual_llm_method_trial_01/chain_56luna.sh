PY=/c/Users/tensh/eigo-radio/.venv/Scripts/python.exe
$PY -X utf8 run_eval_01.py --model gpt-5.6-luna --rep 1 --max-yen 9 > logs/stdout_56luna_rep1.txt 2>&1
$PY -X utf8 run_eval_01.py --model gpt-5.6-luna --rep 2 --max-yen 9 > logs/stdout_56luna_rep2.txt 2>&1
