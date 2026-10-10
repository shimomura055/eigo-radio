# -*- coding: utf-8 -*-
"""WRITER-DEV-RISK-FLAGGER-ANTENNA-TRIAL-01 1セル実行(Trial/DEV)。D2記事モードのsystem promptだけをAntenna<level>へ差し替える。
D2のFlagのみ(D0は決定論でレベル非依存・FIX02で9本とも0件)。完全台帳方式(FIX02と同一: 見出し正規表現のprocess内差し替え)。n_facts==見出し数をassert。
usage: antenna_driver.py <level 1-6> <theme> <model>"""
import json, os, re, sys, time, hashlib
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
os.chdir(REPO)
DET = os.path.join(REPO, "er052_output", "writer_dev_risk_flagger_01", "detectors")
sys.path.insert(0, DET); sys.path.insert(0, HERE)
from dotenv import load_dotenv
load_dotenv()
import flagger_lib as L
import run_flagger_01 as R
import ledger_restore_01 as LR
import prompts_flagger as P
import antenna_prompts as A

level, theme, model = int(sys.argv[1]), sys.argv[2], sys.argv[3]
FLAGGER_MODEL, EFFORT, CAP_TOTAL, MAX_CELL = "gpt-6.1-sol", "medium", 200.0, 12.0
HDR = re.compile(r"^\[(?P<st>[A-Z_]+)(?:\s+-\s+[^\]]*)?\]\s+(?P<id>[^\s:]+):\s*(?P<text>.*)$")
LR._HDR = HDR   # process内のみ(FIX01/FIX02と同一)。detectors配下のファイルは変更しない
cell = "ant%d_%s__%s" % (level, theme, model)
R.RESULTS_DIR = os.path.join(HERE, "results")
R.LOGS_DIR = os.path.join(HERE, "logs")
os.makedirs(os.path.join(HERE, "flags", "A%d" % level, theme), exist_ok=True)
L.LEDGER_PATH = os.path.join(HERE, "cost_ledger_antenna_01.jsonl")   # 全セル共有の合算台帳(累計¥200で新規呼び出し停止)
P.d2_system = lambda: A.antenna_system(level)   # process内のみ。R.plan_calls は P.d2_system() を呼ぶ
assert P.d2_system() == A.antenna_system(level)

def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()
man = json.load(open(os.path.join(REPO, "er052_output", "writer_r0_model_impact_trial_01", "fix02", "manifest_fix02.json"), encoding="utf-8"))
exp = man["cells"]["%s/%s" % (theme, model)]
art = os.path.join(REPO, exp["article_path"])
assert sha(art) == exp["article_sha256"], "article sha mismatch"
lp = os.path.join(REPO, exp["ledger_path"])
assert sha(lp) == exp["ledger_sha256"], "ledger sha mismatch"
facts = LR.parse_ledger_file(lp)
n_head = sum(1 for ln in open(lp, encoding="utf-8").read().splitlines() if HDR.match(ln))
assert len(facts) == n_head == exp["n_headings"], (len(facts), n_head, exp["n_headings"])
sents = R._split_sentences(open(art, encoding="utf-8").read())
ss = [dict(sid="s%d" % (i + 1), text=s, before="", after="") for i, s in enumerate(sents)]
unit = dict(unit_id=cell, mode="article", facts=facts, sentences=ss, ledger_complete=True, article_path=art)
sysm = A.antenna_system(level)
t0 = time.time()
rc = R.run_llm([unit], "d2", FLAGGER_MODEL, cell, MAX_CELL, CAP_TOTAL, None, EFFORT, None, False)
el = time.time() - t0
rp = R.result_paths("d2", FLAGGER_MODEL, cell)
d2 = json.loads(open(rp[0], encoding="utf-8").readline())
raw = [json.loads(x) for x in open(rp[1], encoding="utf-8") if x.strip()]
out = dict(level=level, theme=theme, model_r0=model, cell=cell, flagger_model=FLAGGER_MODEL, flagger_effort=EFFORT,
           system_prompt_sha256=A.sha(sysm), article_path=exp["article_path"], article_sha256=exp["article_sha256"], ledger_sha256=exp["ledger_sha256"],
           n_sentences=len(ss), n_facts=len(facts), n_headings=n_head, fact_ids=[f["fact_id"] for f in facts], rc=rc,
           valid_json=d2["valid_json"], attempts=d2["attempts"], cost_jpy=d2["cost_jpy"], elapsed_s=round(el, 2),
           usage=[r.get("usage") for r in raw if r.get("usage")], model_ids=sorted({r.get("model_id") for r in raw if r.get("model_id")}),
           flags=d2["flags"], sentences={s["sid"]: s["text"] for s in ss}, facts={f["fact_id"]: f["text"] for f in facts})
json.dump(out, open(os.path.join(HERE, "flags", "A%d" % level, theme, model + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(cell, "n_facts=%d flags=%d cost=%.2f valid=%s attempts=%s rc=%s" % (len(facts), len(d2["flags"]), d2["cost_jpy"], d2["valid_json"], d2["attempts"], rc))
