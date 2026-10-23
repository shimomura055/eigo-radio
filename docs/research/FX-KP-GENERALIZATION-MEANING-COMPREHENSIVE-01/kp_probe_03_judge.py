# probe-03 E行をSonnet 1系統でE2(sense_ok/core/single)判定(既存er112 Judge基盤を再利用)。費用台帳はprobe-03のLEDGERへ合算。
import json, sys, os
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:\Users\tensh\eigo-radio"); os.chdir(ROOT); sys.path.insert(0, str(ROOT))
D = ROOT / "docs/research/FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01"
import er112_kp_gm_trial_01 as tr
import er112_kp_gm_judge_01 as jd
tr.LEDGER = D / "kp_probe_03_paid_calls.jsonl"
rows = {}
for l in (D / "kp_probe_03_results.jsonl").read_text(encoding="utf-8").splitlines():
    r = json.loads(l)
    if r["kind"] != "E": continue
    row = dict(id=jd.rid("E2", r["key"], r["sent"], r["text"]), kind="E2", key_phrase=r["key"], source_sentence=r["sent"], explanation=r["text"])
    rows[row["id"]] = row
c = jd.load_cache("sonnet")
todo = sorted([x for x in rows.values() if x["id"] not in c], key=lambda x: x["id"])
print("unique", len(rows), "todo", len(todo))
if len(sys.argv) > 1 and sys.argv[1] == "dry": sys.exit(0)
for i in range(0, len(todo), jd.BATCH):
    print(jd.run_batch("sonnet", "E2", todo[i:i + jd.BATCH], 14.9), "cum", round(tr.ledger_total_jpy(), 3), flush=True)
