# -*- coding: utf-8 -*-
"""POST-EN-TRIAL-01 1セル実行(Trial/DEV)。usage: post_en_driver.py <level 3|4> <unit>   (--dry でAPI非呼び出し)
A3/A4 promptは antenna_prompts.antenna_system(level) をそのまま使う(英語注記なし。COMMON_HEADが既に『記事の文は英語や日本語のことがあります』を含むため差分ゼロ)。"""
import json, os, sys, time
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import post_en_common as C
from post_en_common import *
os.chdir(REPO)
from dotenv import load_dotenv
load_dotenv()
level, uid = int(sys.argv[1]), sys.argv[2]
DRY = "--dry" in sys.argv
assert level in (3, 4)
CAP_TOTAL = float(os.environ.get("POST_EN_CAP", "76.25")); MAX_CELL = 8.0
man = load_manifest()
u = next(x for x in man["units"] if x["unit"] == uid)
unit, facts, ss = build_unit(u, man)
cell = "pe_A%d_%s_%s" % (level, uid, u["theme"])
R.RESULTS_DIR = os.path.join(HERE, "results"); R.LOGS_DIR = os.path.join(HERE, "logs")
os.makedirs(os.path.join(HERE, "flags", "A%d" % level), exist_ok=True)
L.LEDGER_PATH = os.path.join(HERE, "cost_ledger_post_en_01.jsonl")
P.d2_system = lambda: A.antenna_system(level)
assert P.d2_system() == A.antenna_system(level)
sysm = A.antenna_system(level)
if DRY:
    print(cell, "n_facts", len(facts), "n_sents", len(ss), "est_in_tok", L.estimate_tokens(sysm) + L.estimate_tokens(P.build_user(unit))); sys.exit(0)
t0 = time.time()
rc = R.run_llm([unit], "d2", FLAGGER_MODEL, cell, MAX_CELL, CAP_TOTAL, None, EFFORT, None, False)
el = time.time() - t0
rp = R.result_paths("d2", FLAGGER_MODEL, cell)
d2 = json.loads(open(rp[0], encoding="utf-8").readline())
raw = [json.loads(x) for x in open(rp[1], encoding="utf-8") if x.strip()]
out = dict(level=level, unit=uid, theme=u["theme"], cell=cell, flagger_model=FLAGGER_MODEL, flagger_effort=EFFORT,
           system_prompt_sha256=A.sha(sysm), input_path=u["input_path"], input_sha256=u["input_sha256"], status=u["status"],
           ledger_sha256=man["ledgers"][u["ledger"]]["sha256"], n_sentences=len(ss), n_facts=len(facts), fact_ids=[f["fact_id"] for f in facts], rc=rc,
           valid_json=d2["valid_json"], attempts=d2["attempts"], cost_jpy=d2["cost_jpy"], elapsed_s=round(el, 2),
           usage=[r.get("usage") for r in raw if r.get("usage")], model_ids=sorted({r.get("model_id") for r in raw if r.get("model_id")}),
           flags=d2["flags"], sentences={s["sid"]: s["text"] for s in ss}, facts={f["fact_id"]: f["text"] for f in facts})
json.dump(out, open(os.path.join(HERE, "flags", "A%d" % level, uid + "_" + u["theme"] + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(cell, "n_facts=%d n_sents=%d flags=%d cost=%.2f valid=%s attempts=%s rc=%s models=%s" % (len(facts), len(ss), len(d2["flags"]), d2["cost_jpy"], d2["valid_json"], d2["attempts"], rc, out["model_ids"]))
