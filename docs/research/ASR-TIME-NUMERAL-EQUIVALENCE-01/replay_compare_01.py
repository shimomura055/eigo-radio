"""replay基盤: 2つの結果json(base=修正前, cand=修正後)を比較。PASS側={EQUAL,NO_VALUES,AMBIGUOUS}(value_guard)。classifyはP/N。"""
import sys, json
PASS = ("EQUAL", "NO_VALUES", "AMBIGUOUS")
b = json.load(open(sys.argv[1])); c = json.load(open(sys.argv[2])); pairs = {}
if len(sys.argv) > 3:
    for l in open(sys.argv[3], encoding="utf-8"): r = json.loads(l); pairs[r["id"]] = r
JP = ("PASS", "PASS_WITH_WARNING")
ch = {"judge_pass2ng": [], "judge_ng2pass": [], "judge_state_other": [], "vg_pass2ng": [], "vg_ng2pass": [], "vg_other": [], "cls_pass2ng": [], "cls_ng2pass": [], "tier1_change": []}
for k in b:
    x, y = b[k], c[k]
    if x["state"] != y["state"]:
        (ch["judge_pass2ng"] if x["state"] in JP and y["state"] not in JP else ch["judge_ng2pass"] if x["state"] not in JP and y["state"] in JP else ch["judge_state_other"]).append(k)
    if x["vg"] != y["vg"]:
        (ch["vg_pass2ng"] if x["vg"] in PASS and y["vg"] not in PASS else ch["vg_ng2pass"] if x["vg"] not in PASS and y["vg"] in PASS else ch["vg_other"]).append(k)
    if x["cls"][0] != y["cls"][0]: (ch["cls_pass2ng"] if x["cls"][0] == "P" else ch["cls_ng2pass"]).append(k)
    if x["tier1"] != y["tier1"]: ch["tier1_change"].append(k)
print("pairs", len(b)); [print(k, len(v)) for k, v in ch.items()]
for k, v in ch.items():
    for i in v[:15]:
        r = pairs.get(i, {}); print(f"[{k}] {b[i]['vg']}->{c[i]['vg']} judge {b[i]['state']}/{b[i]['reason'][:30]}->{c[i]['state']}/{c[i]['reason'][:30]} cls {b[i]['cls'][0]}->{c[i]['cls'][0]} | {r.get('canon','')[:110]!r} || {r.get('asr','')[:110]!r}")
