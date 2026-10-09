# -*- coding: utf-8 -*-
"""WRITER-R0-MODEL-IMPACT-TRIAL-01-FIX01-A: Disney+(streaming_price)を完全台帳(F01-F07)でFlagger再実行。Trial/DEV。
detectors配下は無変更。ledger_restore_01._HDR(見出し正規表現)をこのprocess内だけで差替え、[AMBIGUOUS - ...]見出しも読む。
他5件と同じ扱い(見出し接頭辞[...] ID: を除去しFact本文+後続行をtextにする)。Flagger Prompt/model/effort/記事/文分割は前回と同一。R0は再生成しない。
"""
import json, os, re, sys, time
sys.dont_write_bytecode = True
import r0_trial_driver_01 as T   # REPO/DET sys.path/chdir設定、paths(), sha_file()
from dotenv import load_dotenv
load_dotenv()
import flagger_lib as L
import run_flagger_01 as R
import ledger_restore_01 as LR

LR._HDR = re.compile(r"^\[(?P<st>[A-Z_]+)(?:\s+-\s+[^\]]*)?\]\s+(?P<id>[^\s:]+):\s*(?P<text>.*)$")
OUT = T.OUT
theme = "streaming_price"
model = sys.argv[1]
cell = "fix01_%s__%s" % (theme, model)
R.RESULTS_DIR = os.path.join(OUT, "results_fix01")
R.LOGS_DIR = os.path.join(OUT, "logs_fix01")
os.makedirs(R.RESULTS_DIR, exist_ok=True); os.makedirs(R.LOGS_DIR, exist_ok=True)
os.makedirs(os.path.join(OUT, "flags_fix01", theme), exist_ok=True)
L.LEDGER_PATH = os.path.join(R.LOGS_DIR, "flagger_ledger_%s.jsonl" % cell)
art = os.path.join(OUT, "r0", theme, model + ".md")
facts = LR.parse_ledger_file(T.paths(theme)["ledger"])
assert [f["fact_id"] for f in facts] == ["F0%d" % i for i in range(1, 8)], [f["fact_id"] for f in facts]
sents = R._split_sentences(open(art, encoding="utf-8").read())
ss = [dict(sid="s%d" % (i + 1), text=s, before="", after="") for i, s in enumerate(sents)]
unit = dict(unit_id=cell, mode="article", facts=facts, sentences=ss, ledger_complete=True, article_path=art)
rc0 = R.run_d0([unit], cell)
t0 = time.time()
rc2 = R.run_llm([unit], "d2", T.FLAGGER_MODEL, cell, 20.0, 20.0, None, T.FLAGGER_EFFORT, None, False)
el = time.time() - t0
d0 = json.loads(open(R.result_paths("d0", "none", cell)[0], encoding="utf-8").readline())
d2 = json.loads(open(R.result_paths("d2", T.FLAGGER_MODEL, cell)[0], encoding="utf-8").readline())
union = R.union_flags([("d0", d0["flags"]), ("d2", d2["flags"])])
raw = [json.loads(x) for x in open(R.result_paths("d2", T.FLAGGER_MODEL, cell)[1], encoding="utf-8") if x.strip()]
out = dict(theme=theme, r0_model=model, cell=cell, fix="FIX01-A", flagger_model=T.FLAGGER_MODEL, flagger_effort=T.FLAGGER_EFFORT,
           article_sha256=T.sha_file(art), ledger_sha256=T.sha_file(T.paths(theme)["ledger"]), n_sentences=len(ss), n_facts=len(facts),
           fact_ids=[f["fact_id"] for f in facts], rc_d0=rc0, rc_d2=rc2, d2_valid_json=d2["valid_json"], d2_attempts=d2["attempts"],
           d2_cost_jpy=d2["cost_jpy"], d2_elapsed_s=round(el, 2), d2_model_ids=sorted({r.get("model_id") for r in raw if r.get("model_id")}),
           d0_flags=d0["flags"], d2_flags=d2["flags"], union_flags=union, sentences={s["sid"]: s["text"] for s in ss},
           facts={f["fact_id"]: f["text"] for f in facts})
json.dump(out, open(os.path.join(OUT, "flags_fix01", theme, model + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(cell, "n_facts=%d d0=%d d2=%d union=%d cost=%.2f valid=%s" % (len(facts), len(d0["flags"]), len(d2["flags"]), len(union), d2["cost_jpy"], d2["valid_json"]))
