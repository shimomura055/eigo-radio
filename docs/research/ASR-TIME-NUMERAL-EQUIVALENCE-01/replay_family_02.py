"""replay結果(修正前/後)をpairのsrc pathでFamily別に集計する(API 0)。 py replay_family_02.py base.json cand.json pairs.jsonl
Family判定はsrc pathの文字列によるヒューリスティック(X: family_x/er019/er053/ig_nobel等、Z: family_z/er026/er063、Y: family_y/er110、C: family_c/er013、
それ以外=A/B/Legacy/共通/docs=other)。判定の変化(PASS<->NG)の件数をFamily別に出す。"""
import sys, json, re, collections
b = json.load(open(sys.argv[1], encoding="utf-8")); c = json.load(open(sys.argv[2], encoding="utf-8")); pairs = {}
for l in open(sys.argv[3], encoding="utf-8"):
    r = json.loads(l); pairs[r["id"]] = r
JP = ("PASS", "PASS_WITH_WARNING"); VP = ("EQUAL", "NO_VALUES", "AMBIGUOUS")
def fam(src):
    s = src.lower().replace("\\", "/")
    if re.search(r"family_z|er026_|er063|/er062", s): return "Z"
    if re.search(r"family_y|er110_|er112", s): return "Y"
    if re.search(r"family_x|er019_|er053|er052_|ig_nobel|coffee_prices|hormuz", s): return "X"
    if re.search(r"family_c|er013", s): return "C"
    if re.search(r"er003|er006|er008|er010|er011|er012|er014|er015|er016", s): return "A/B legacy"
    return "other(共通/docs/fixture)"
cnt = collections.defaultdict(lambda: collections.Counter())
for k in b:
    f = fam(pairs[k]["src"]); x, y = b[k], c[k]; cnt[f]["pairs"] += 1
    xp, yp = x["state"] in JP, y["state"] in JP
    if xp and not yp: cnt[f]["judge_PASS->NG"] += 1
    if (not xp) and yp: cnt[f]["judge_NG->PASS"] += 1
    if x["state"] != y["state"] and xp == yp: cnt[f]["judge_state_other"] += 1
    if x["vg"] in VP and y["vg"] not in VP: cnt[f]["vg_PASS->NG"] += 1
    if x["vg"] not in VP and y["vg"] in VP: cnt[f]["vg_NG->PASS"] += 1
    if x["cls"][0] == "P" and y["cls"][0] != "P": cnt[f]["cls_PASS->NG"] += 1
    if x["cls"][0] != "P" and y["cls"][0] == "P": cnt[f]["cls_NG->PASS"] += 1
keys = ["pairs", "judge_PASS->NG", "judge_NG->PASS", "judge_state_other", "vg_PASS->NG", "vg_NG->PASS", "cls_PASS->NG", "cls_NG->PASS"]
print("family".ljust(26) + "".join(k.rjust(18) for k in keys))
tot = collections.Counter()
for f in sorted(cnt):
    print(f.ljust(26) + "".join(str(cnt[f][k]).rjust(18) for k in keys)); tot.update(cnt[f])
print("TOTAL".ljust(26) + "".join(str(tot[k]).rjust(18) for k in keys))
