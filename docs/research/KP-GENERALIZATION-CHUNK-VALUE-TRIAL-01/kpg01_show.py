import json, os, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__))
for p in sorted(glob.glob(os.path.join(HERE, "kpg01_work", "results", "*.json"))):
    n = os.path.basename(p)[:-5]
    if len(sys.argv) > 1 and not any(a in n for a in sys.argv[1:]): continue
    r = json.load(open(p, encoding="utf-8"))
    print(f"== {n}  items={len(r['items'])} ¥{r['cost_jpy']} {r['sec']}s")
    for i in r["items"]:
        v = (i.get("verify") or {}).get("verdict", "")
        print(f"  {i.get('display_form'):32s} <- {i.get('source_span'):36s} | {i.get('gloss_ja')} | {i.get('chunk_type')}/{i.get('difficulty')} {v} | {i.get('chunk_reason_ja')}")
    lg = r["log"]
    for k in ("validator_dropped", "verify_dropped", "dropped_not_in_text"):
        if lg.get(k): print("  [", k, "]", json.dumps(lg[k], ensure_ascii=False)[:400])
    if lg.get("word_candidates"): print("  words:", lg["word_candidates"])
