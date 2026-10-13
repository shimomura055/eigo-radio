import json,sys,glob
for f in sorted(glob.glob(sys.argv[1])):
    r=json.load(open(f,encoding="utf-8"))
    print(r["tag"],r["selection_status"],r.get("merged_overall_status"),r.get("redundancy_status"),r["cost_jpy"],r["elapsed_sec"])
    for c in r.get("canonicalized",[]): print("  ",c["rank"],c["key_phrase"],"|",c["display_phrase"])
    for s in r.get("selected_items",[]): print("   sel",s["display_phrase"],"| cand:",s["candidate_surface"])
