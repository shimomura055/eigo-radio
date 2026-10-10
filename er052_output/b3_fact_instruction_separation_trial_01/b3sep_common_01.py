# -*- coding: utf-8 -*-
import os, sys, json, re, hashlib
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, REPO); sys.path.insert(0, HERE)
G0 = os.path.join(REPO, "er052_output", "factlock_astra_e2e_trial_01", "g0_real_annotation_01")
THEMES = ["semiconductor_earnings", "small_bag", "space_weapons", "hormuz", "central_bank_mortgage", "meta", "byd_recall", "openai_copyright", "streaming_price"]
PROBLEM5 = THEMES[:5]
E9_THEMES = PROBLEM5 + ["byd_recall"]
MODEL = "gpt-6-luna"
def rd(p): return open(p, encoding="utf-8", newline="").read().replace("\r\n", "\n")
def rj(p): return json.load(open(p, encoding="utf-8"))
def wj(p, o):
    os.makedirs(os.path.dirname(p), exist_ok=True); open(p, "w", encoding="utf-8", newline="\n").write(json.dumps(o, ensure_ascii=False, indent=1))
def wt(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True); open(p, "w", encoding="utf-8", newline="\n").write(t)
def sha(t): return hashlib.sha256(t.encode("utf-8") if isinstance(t, str) else t).hexdigest()
def theme_inputs(th):
    d = f"{G0}/{th}/shared"
    ev = rj(f"{d}/fact_selection_evidence_original.json")
    return {"theme": th, "dir": d, "topic": rd(f"{d}/topic.txt"), "ledger": open(f"{d}/ledger.txt", encoding="utf-8", newline="").read(),
            "ledger_path": f"{d}/ledger.txt", "ev": ev, "brief": rd(f"{d}/brief_original.md")}
