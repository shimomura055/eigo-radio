# -*- coding: utf-8 -*-
"""META-ROLLBACK-CHECK-01: 既存稿1本 x A3/A4 (post_en_trialと同一経路・同一prompt)。usage: rb_driver.py <3|4|pre> [--dry]"""
import json, os, sys, time, re
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
PE = os.path.join(HERE, "..", "post_en_trial_01"); sys.path.insert(0, PE)
import post_en_common as C
from post_en_common import *
os.chdir(REPO)
from dotenv import load_dotenv
load_dotenv()
ART = "er019_output/meta/run_03/b1b/article.md"; LED = "er019_output/meta/run_03/ledger/verified_fact_ledger.txt"
TARGET = "The company also restored the human concierge feature to the way it had been before, at least for now."
def build():
    ap = os.path.join(REPO, ART); lp = os.path.join(REPO, LED)
    art = open(ap, encoding="utf-8").read(); txt = open(lp, encoding="utf-8").read()
    lines = txt.splitlines()
    n_broad = sum(1 for l in lines if l.startswith("[")); n_hdr = sum(1 for l in lines if HDR.match(l))
    facts = LR.parse_ledger_text(txt)
    ids = [f["fact_id"] for f in facts]
    ss = [dict(sid="s%d" % (i + 1), text=s, before="", after="") for i, s in enumerate(R._split_sentences(art))]
    unit = dict(unit_id="RB01", mode="article", facts=facts, sentences=ss, ledger_complete=True, article_path=ap)
    info = dict(article=ART, article_sha256=sha_b(open(ap, "rb").read()), ledger=LED, ledger_sha256=sha_b(txt.encode("utf-8")),
                expected_headers_broad=n_broad, expected_headers_strict=n_hdr, parsed=len(facts), ids=ids, n_sentences=len(ss),
                target_in_article=TARGET in art, target_sids=[s["sid"] for s in ss if "restored the human concierge" in s["text"]])
    assert n_broad == n_hdr == len(facts) == 15 and TARGET in art and info["target_sids"], info
    return unit, facts, ss, info
HERE = os.path.dirname(os.path.abspath(__file__))  # post_en_commonのHEREを上書きしない(実行後修正: 初回実行時は出力がpost_en_trial_01/へ出たため手動でmv)
arg = sys.argv[1]; DRY = "--dry" in sys.argv
unit, facts, ss, info = build()
if arg == "pre":
    out = dict(info); out["sha_A3"] = A.sha(A.antenna_system(3)); out["sha_A4"] = A.sha(A.antenna_system(4))
    prices = L.load_prices(FLAGGER_MODEL); out["prices"] = prices
    OUT = {3: 174, 4: 320}; est = {}
    for lv in (3, 4):
        it = L.estimate_tokens(A.antenna_system(lv)) + L.estimate_tokens(P.build_user(unit))
        est[lv] = dict(est_in_tok=it, central_jpy=round(L.cost_yen(prices, it, OUT[lv]), 3), high_jpy=round(L.cost_yen(prices, int(it * 1.25), OUT[lv] * 3), 3))
    out["estimate"] = est
    json.dump(out, open(os.path.join(HERE, "precheck_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(json.dumps(out, ensure_ascii=False, indent=1)[:2500]); sys.exit(0)
level = int(arg); assert level in (3, 4)
cell = "rb_A%d_meta_run03_b1b" % level
R.RESULTS_DIR = os.path.join(HERE, "runs"); R.LOGS_DIR = os.path.join(HERE, "runs")
L.LEDGER_PATH = os.path.join(HERE, "cost_ledger_rb_01.jsonl")
P.d2_system = lambda: A.antenna_system(level)
sysm = A.antenna_system(level)
t0 = time.time(); ts = time.strftime("%Y-%m-%dT%H:%M:%S%z")
rc = R.run_llm([unit], "d2", FLAGGER_MODEL, cell, 8.0, 20.0, None, EFFORT, None, False)
el = time.time() - t0
rp = R.result_paths("d2", FLAGGER_MODEL, cell)
d2 = json.loads(open(rp[0], encoding="utf-8").readline())
raw = [json.loads(x) for x in open(rp[1], encoding="utf-8") if x.strip()]
out = dict(level=level, cell=cell, started=ts, flagger_model=FLAGGER_MODEL, flagger_effort=EFFORT, system_prompt_sha256=A.sha(sysm), **info,
           rc=rc, valid_json=d2["valid_json"], attempts=d2["attempts"], cost_jpy=d2["cost_jpy"], elapsed_s=round(el, 2),
           usage=[r.get("usage") for r in raw if r.get("usage")], model_ids=sorted({r.get("model_id") for r in raw if r.get("model_id")}),
           flags=d2["flags"], sentences={s["sid"]: s["text"] for s in ss}, facts={f["fact_id"]: f["text"] for f in facts})
json.dump(out, open(os.path.join(HERE, "runs", "A%d_result.json" % level), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(cell, "flags=%d cost=%.3f valid=%s attempts=%s rc=%s models=%s" % (len(d2["flags"]), d2["cost_jpy"], d2["valid_json"], d2["attempts"], rc, out["model_ids"]))
