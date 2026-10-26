# -*- coding: utf-8 -*-
"""KPRW1 委任_01: 除外11件(+Human NG 3件)のtest用frozen fixtureを、DESIGN-01 inventory_01.jsonとDEV(er123)のbuild_caseから生成する(API 0・一回限り)。"""
import json, os, socket, sys
def _b(*a, **k): raise RuntimeError("net blocked")
socket.socket.connect = _b; socket.create_connection = _b
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
sys.path.insert(0, ROOT)
import er123_kp_rescue_dev_01 as m
inv = json.load(open(os.path.join(ROOT, "docs/research/KP-GATE-EXCLUSION-RESCUE-DESIGN-01/inventory_01.json"), encoding="utf-8"))
events = [e for e in inv["events"] if e["class"] != "QA_REVIEW_REQUIRED(非除外・旗)"]
out = []
for n, e in enumerate(events):
    c = m.build_case(e)
    if e["class"] == "HUMAN_NG_EXCLUDED" or c["text"]:
        out.append({"id": n, "family": e["family"], "level": e["level"], "run": e["run"], "era": e["era"], "stage": e.get("stage"),
                    "display": e["phrase"], "class": e["class"], "sub": e.get("sub"), "reason": e["reason"], "llm_key": c["llm_key"],
                    "span": c["span"], "sentence": c["sentence"], "text": c["text"]})
json.dump(out, open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(out), [(o["id"], o["display"]) for o in out if o["display"] in ("studied separately","had our eye on","rose above","held out","rang through","it can’t be helped","can’t be helped","have a say","catch their interest","redelivery fee","too soon to wave a flag")])
