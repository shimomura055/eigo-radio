# Trial-05 オフライン分析(API 0)。事前登録 PREREGISTERED_CRITERIA_05.md の§1許容集合・§3安定・§5(B)模擬を機械的に当てはめる。
import json, glob, os, re, itertools, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_trial_05 as t5
BASE = t5.BASE
CORE = {"open_window": {"P21"}, "ig_nobel": {"P4", "P5", "P8", "P9"}, "gift": {"P4", "P22", "P30"}, "paw": {"P24"}}
EITHER = {"open_window": {"P29"}, "ig_nobel": {"P2", "P3", "P11"}, "gift": {"P12", "P29"}, "paw": {"P2", "P8", "P19", "P22", "P32"}}
def load(w):
    return [json.load(open(os.path.join(BASE, f"OUTPUT_05_{w}_r{i}_STEPA_DEV.json"), encoding="utf-8")) for i in range(1, t5.NSAMP[w] + 1)]
def sel_paras(j): return [f["para"] for f in t5.select_rule(j["features"])]
def stable_for(w, selections):
    allowed = CORE[w] | EITHER[w]
    v1 = all(set(s) <= allowed for s in selections); v2 = all(len(s) > 0 for s in selections)
    return dict(sel_subset_allowed=v1, no_zero=v2, strict_core=all(set(s) <= CORE[w] for s in selections))
out = {}
for w in t5.WORKS5:
    S = load(w); sels = [sel_paras(j) for j in S]
    allowed = CORE[w] | EITHER[w]
    r = dict(selections=sels, outside_allowed=[sorted(set(s) - allowed) for s in sels], zero_samples=[i + 1 for i, s in enumerate(sels) if not s])
    r["stable"] = stable_for(w, sels)
    r["stable"]["all"] = r["stable"]["sel_subset_allowed"] and r["stable"]["no_zero"]   # 基礎のみ=0はSonnet目視(別記)
    # 拾い漏れ: 中核の候補化率(features収載)と層A率
    feat_rate = {}; tierA_rate = {}; elig_rate = {}
    for p in sorted(CORE[w] | EITHER[w], key=lambda x: int(x[1:])):
        feat_rate[p] = sum(any(f["para"] == p and f.get("resolve_ok") for f in j["features"]) for j in S)
        tierA_rate[p] = sum(any(f["para"] == p and str(f.get("tier")).upper() == "A" for f in j["features"]) for j in S)
        elig_rate[p] = sum(any(f["para"] == p and t5.is_eligible(f) for f in j["features"]) for j in S)
    r["n"] = len(S); r["feature_listed"] = feat_rate; r["tierA"] = tierA_rate; r["eligible"] = elig_rate
    # 文ごとの層分布(全標本のtier=A/B/Cを集計)
    dist = {}
    for j in S:
        for f in j["features"]:
            if not f.get("resolve_ok"): continue
            k = f"{f['para']}|{f['sentence'][:50]}"
            d = dist.setdefault(k, dict(A=0, B=0, C=0, other=0, basic_true=0, elig=0))
            t = str(f.get("tier")).upper(); d[t if t in "ABC" and len(t) == 1 else "other"] += 1
            d["basic_true"] += int(t5._as_bool(f.get("basic_only", True))); d["elig"] += int(t5.is_eligible(f))
    r["tier_dist"] = dict(sorted(dist.items(), key=lambda kv: int(re.match(r"P(\d+)", kv[0]).group(1))))
    r["uncovered"] = [j["uncovered_paras"] for j in S]
    r["misread_quote_in_sentence"] = sum(1 for j in S for f in j["features"] if f.get("resolve_ok") and t5.is_eligible(f) and f.get("misread_quote_in_sentence"))
    r["eligible_total"] = sum(1 for j in S for f in j["features"] if t5.is_eligible(f))
    r["resolve_fail"] = sum(1 for j in S for f in j["features"] if not f.get("resolve_ok"))
    r["replaced_by_body"] = sum(1 for j in S for f in j["features"] if f.get("sentence_replaced_by_body"))
    r["cost"] = [j["usage"]["cost_jpy_at_160"] for j in S]; r["sec"] = [j["usage"]["elapsed_sec"] for j in S]
    # (B)模擬: n=3の全組合せ
    combos = list(itertools.combinations(range(len(S)), 3)); sims = []
    for c in combos:
        s = t5.sim_B([S[i] for i in c]); ps = [x[0] for x in s["selected"]]
        sims.append(dict(combo=[i + 1 for i in c], selected=ps, ok=bool(ps) and set(ps) <= allowed, tierB_report=[x[0] for x in s["fable_report_tierB"]]))
    r["sim_B_n3"] = dict(combos=len(sims), ok=sum(s["ok"] for s in sims), zero=sum(1 for s in sims if not s["selected"]),
                         outside=sum(1 for s in sims if set(s["selected"]) - allowed), sets=sorted({tuple(s["selected"]) for s in sims}), tierB_flag=sum(1 for s in sims if s["tierB_report"]))
    full = t5.sim_B(S, frac=2 / 3); r["consensus_all"] = [x[0] for x in full["selected"]]
    out[w] = r
json.dump(out, open(os.path.join(BASE, "analysis_05.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for w, r in out.items():
    print("==", w, "n", r["n"], "sel", r["selections"], "outside", r["outside_allowed"], "zero", r["zero_samples"], "stable", r["stable"])
    print("  listed", r["feature_listed"], "tierA", r["tierA"], "elig", r["eligible"])
    print("  simB", r["sim_B_n3"], "consensus_all", r["consensus_all"], "uncov", r["uncovered"], "mq", r["misread_quote_in_sentence"], "/", r["eligible_total"], "resfail", r["resolve_fail"], "repl", r["replaced_by_body"])
    print("  cost", r["cost"], "sec", r["sec"])
