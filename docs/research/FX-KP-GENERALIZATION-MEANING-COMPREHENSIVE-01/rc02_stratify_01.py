# ROOT_CAUSE_02 (a)(c): er112 A3_verify 92行(現行E0 / v3 E3)の層別分析(API 0)。ラベル(gloss_class)は目視1名(Sonnet)。
import json, collections, sys
sys.stdout.reconfigure(encoding="utf-8")
R = r"C:\Users\tensh\eigo-radio\er112_output\kp_gm_trial_01\a3_verify\all_rows_judged_01.json"
d = json.load(open(R, encoding="utf-8"))
# JA参考意味(説明callに渡る日本語)の分類。N=gloss自体に記事固有条件(対象・場面)を含む / L=字義・逐語寄り(慣用義と異なる)/ O=その他
N = {"apply one's findings", "execution bell", "refueling support"}
L = {"Carry the Load", "pull someone under", "reach for someone's wallet", "take the wheel", "earn such trust"}
def cls(k): return "N_gloss_has_article_condition" if k in N else ("L_gloss_literal" if k in L else "O_other")
def sentbin(s):
    n = len(s.split()); return "short<=10" if n <= 10 else ("mid11-16" if n <= 16 else "long>=17")
def rate(rows, f):
    n = len(rows); k = sum(1 for r in rows if f(r)); return f"{k}/{n}" + (f"={100*k/n:.0f}%" if n else "")
for arm in ("a1gE0", "a1gE3"):
    print("==", arm)
    A = [r for r in d if r["arm"] == arm]
    for name, keyf in (("gloss_class", lambda r: cls(r["key"])), ("sentence_len", lambda r: sentbin(r["sent"]))):
        g = collections.defaultdict(list)
        for r in A: g[keyf(r)].append(r)
        for k, rows in sorted(g.items()):
            print(f"  {name}={k:32s} core_fail {rate(rows, lambda r: not r['core_both']):12s} sense_fail {rate(rows, lambda r: not r['sense_both']):12s} single_fail {rate(rows, lambda r: not r['single_both'])}")
    print("  ALL", "core_fail", rate(A, lambda r: not r["core_both"]), "sense_fail", rate(A, lambda r: not r["sense_both"]))
# 同一KPで E0->E3 の core_fail と sense_fail の交換(トレードオフ)
by = collections.defaultdict(lambda: collections.defaultdict(list))
for r in d: by[(r["key"], r["sent"])][r["arm"]].append(r)
trade = collections.Counter()
for k, v in by.items():
    c0 = sum(1 for r in v["a1gE0"] if not r["core_both"]); c3 = sum(1 for r in v["a1gE3"] if not r["core_both"])
    s0 = sum(1 for r in v["a1gE0"] if not r["sense_both"]); s3 = sum(1 for r in v["a1gE3"] if not r["sense_both"])
    trade["core_fail_decreased_kp" if c3 < c0 else ("core_fail_increased_kp" if c3 > c0 else "core_same_kp")] += 1
    trade["sense_fail_increased_kp" if s3 > s0 else ("sense_fail_decreased_kp" if s3 < s0 else "sense_same_kp")] += 1
    if c3 < c0 and s3 > s0: trade["BOTH(core down & sense up)=tradeoff_kp"] += 1
print(dict(trade))
