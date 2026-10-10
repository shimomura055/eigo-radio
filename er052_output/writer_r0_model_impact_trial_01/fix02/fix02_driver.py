# -*- coding: utf-8 -*-
"""WRITER-R0-MODEL-IMPACT-TRIAL-01-FIX02: 前回R0(new腕r0.md)+今回Luna/Sol/Astra R0 の12本を同一条件でRisk Flagger(D0+D2記事モード)。Trial/DEV。
FIX01-A r0_fix01_driver.py と同じ完全台帳方式(ledger_restore_01._HDR をprocess内のみ差替え)。detectors配下は無変更。
usage: fix02_driver.py <theme> <source>   source in prev_r0|gpt-6-luna|gpt-6.1-sol|gpt-6-astra"""
import json, os, re, sys, time
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import r0_trial_driver_01 as T
from dotenv import load_dotenv
load_dotenv()
import flagger_lib as L
import run_flagger_01 as R
import ledger_restore_01 as LR

HDR = re.compile(r"^\[(?P<st>[A-Z_]+)(?:\s+-\s+[^\]]*)?\]\s+(?P<id>[^\s:]+):\s*(?P<text>.*)$")
LR._HDR = HDR
OUT = T.OUT
theme, src = sys.argv[1], sys.argv[2]
cell = "fix02_%s__%s" % (theme, src)
R.RESULTS_DIR = os.path.join(HERE, "results")
R.LOGS_DIR = os.path.join(HERE, "logs")
os.makedirs(os.path.join(HERE, "flags", theme), exist_ok=True)
L.LEDGER_PATH = os.path.join(R.LOGS_DIR, "flagger_ledger_%s.jsonl" % cell)
if src == "prev_r0":
    art = os.path.join(T.E2E, "runs", theme, "new", "new_writer", "r0.md")
else:
    art = os.path.join(OUT, "r0", theme, src + ".md")
manifest = json.load(open(os.path.join(HERE, "manifest_fix02.json"), encoding="utf-8"))
exp = manifest["cells"]["%s/%s" % (theme, src)]
assert T.sha_file(art) == exp["article_sha256"], "article sha mismatch"
lp = T.paths(theme)["ledger"]
assert T.sha_file(lp) == exp["ledger_sha256"], "ledger sha mismatch"
facts = LR.parse_ledger_file(lp)
n_head = sum(1 for ln in open(lp, encoding="utf-8").read().splitlines() if HDR.match(ln))
assert len(facts) == n_head == exp["n_headings"], (len(facts), n_head, exp["n_headings"])
sents = R._split_sentences(open(art, encoding="utf-8").read())
ss = [dict(sid="s%d" % (i + 1), text=s, before="", after="") for i, s in enumerate(sents)]
unit = dict(unit_id=cell, mode="article", facts=facts, sentences=ss, ledger_complete=True, article_path=art)
rc0 = R.run_d0([unit], cell)
t0 = time.time()
rc2 = R.run_llm([unit], "d2", T.FLAGGER_MODEL, cell, 8.0, 8.0, None, T.FLAGGER_EFFORT, None, False)
el = time.time() - t0
d0 = json.loads(open(R.result_paths("d0", "none", cell)[0], encoding="utf-8").readline())
d2 = json.loads(open(R.result_paths("d2", T.FLAGGER_MODEL, cell)[0], encoding="utf-8").readline())
union = R.union_flags([("d0", d0["flags"]), ("d2", d2["flags"])])
raw = [json.loads(x) for x in open(R.result_paths("d2", T.FLAGGER_MODEL, cell)[1], encoding="utf-8") if x.strip()]
req = raw[0].get("request", {}) if raw else {}
out = dict(theme=theme, source=src, cell=cell, fix="FIX02", flagger_model=T.FLAGGER_MODEL, flagger_effort=T.FLAGGER_EFFORT,
           article_path=os.path.relpath(art, T.REPO), article_sha256=T.sha_file(art), ledger_sha256=T.sha_file(lp), n_sentences=len(ss),
           n_facts=len(facts), n_headings=n_head, fact_ids=[f["fact_id"] for f in facts], rc_d0=rc0, rc_d2=rc2, d2_valid_json=d2["valid_json"],
           d2_attempts=d2["attempts"], d2_cost_jpy=d2["cost_jpy"], d2_elapsed_s=round(el, 2),
           d2_model_ids=sorted({r.get("model_id") for r in raw if r.get("model_id")}),
           d0_flags=d0["flags"], d2_flags=d2["flags"], union_flags=union, sentences={s["sid"]: s["text"] for s in ss},
           facts={f["fact_id"]: f["text"] for f in facts})
json.dump(out, open(os.path.join(HERE, "flags", theme, src + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(cell, "n_facts=%d d0=%d d2=%d union=%d cost=%.2f valid=%s attempts=%s" % (len(facts), len(d0["flags"]), len(d2["flags"]), len(union), d2["cost_jpy"], d2["valid_json"], d2["attempts"]))
