# -*- coding: utf-8 -*-
"""A-3 v3 追加検証 Judge段。E2(sense_ok/core/single)を新規25KP分の説明に対し実行。キャッシュ=er112既存judge cacheを共有(同一行hashは再利用)。台帳=a3_verify/paid_calls.jsonl"""
import json, sys, glob, collections
from pathlib import Path
ROOT = Path(r"C:\Users\tensh\eigo-radio"); sys.path.insert(0, str(ROOT))
import er112_kp_gm_trial_01 as tr
import er112_kp_gm_judge_01 as jd
from concurrent.futures import ThreadPoolExecutor, as_completed
V = ROOT / "er112_output/kp_gm_trial_01/a3_verify"
tr.LEDGER = V / "paid_calls.jsonl"
def rows(kind):
    out = {}
    for f in glob.glob(str(V / "runs" / "*" / "*" / "*.json")):
        d = json.load(open(f, encoding="utf-8"))
        for it in d["items"]:
            e = (d["expl"] or {}).get(str(it["rank"]))
            if not e: continue
            r = dict(id=jd.rid(kind, it["key_phrase"], it["source_sentence"], e["text"]), kind=kind, key_phrase=it["key_phrase"], source_sentence=it["source_sentence"], explanation=e["text"])
            out[r["id"]] = r
    return out
if __name__ == "__main__":
    kinds = sys.argv[1].split(","); judges = sys.argv[2].split(","); cap = float(sys.argv[3]); dry = len(sys.argv) > 4
    jobs = []
    for k in kinds:
        rs = rows(k)
        for j in judges:
            c = jd.load_cache(j)
            todo = sorted([r for r in rs.values() if r["id"] not in c], key=lambda x: x["id"])
            print(k, j, "unique rows", len(rs), "todo", len(todo))
            for i in range(0, len(todo), jd.BATCH): jobs.append((j, k, todo[i:i + jd.BATCH]))
    if dry: sys.exit(0)
    with ThreadPoolExecutor(4) as ex:
        for f in as_completed([ex.submit(jd.run_batch, j, k, b, cap) for j, k, b in jobs]): print(f.result(), tr.ledger_total_jpy())
