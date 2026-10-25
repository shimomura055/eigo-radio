# Trial-05 補助オフライン分析(API 0)。合否判定には使わない(事後・探索的)。
# (1) parse補正: sentence先頭/末尾の引用符を除去して再解決(LLM出力は無編集。as-run結果は analysis_05.json)
# (2) what-if規則: 事前登録外の規則変更案を、既存標本に当てた場合の挙動(Fable向けの次案材料)
import json, os, re, sys, itertools, copy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_trial_05 as t5, run_trial_04 as t4
import analyze_05 as a5   # as-run結果をprint(副作用あり)
CORE, EITHER = a5.CORE, a5.EITHER
QS = "“”‘’\"' "
def reparse(w):
    d = t5.work_data5(w); S = a5.load(w); out = []
    for j in S:
        j2 = copy.deepcopy(j)
        for f in j2["features"]:
            if f.get("resolve_ok"): continue
            raw = f.get("sentence_llm_raw", f.get("sentence", "")); s = raw.strip().strip(QS)
            try:
                verb, pi, a, b = t4.resolve_verbatim(d, f["para"], s)
                f.update(resolve_ok=True, sentence=verb, requoted=True); f["prev"], f["next"] = t4.local_context(d, pi, a, b)
            except AssertionError as e: f["resolve_error2"] = str(e)[:80]
        seen = set()
        for f in j2["features"]:
            k = (f.get("para"), f.get("sentence"))
            f["duplicate"] = k in seen if f.get("resolve_ok") else False
            if f.get("resolve_ok"): seen.add(k)
        out.append(j2)
    return out
CLS_ORDER = ["INV", "CLEFT", "CMP", "HEAVY", "POSTMOD", "FRONT", "APPOS", "ELL", "SPEC", "OTHER"]
def elig_ab(f): return bool(f.get("resolve_ok") and not f.get("duplicate") and str(f.get("tier")).upper() in ("A", "B") and not t5._as_bool(f.get("basic_only", True)) and str(f.get("misread_ja", "")).strip())
def w1(j, k=2):  # tier A/B許容・クラス優先順
    el = sorted([f for f in j["features"] if elig_ab(f)], key=lambda f: (CLS_ORDER.index(f.get("feature_class")) if f.get("feature_class") in CLS_ORDER else 99, t5._pnum(f)))
    seen = []; 
    for f in el:
        if f["para"] not in seen: seen.append(f["para"])
    return seen[:k]
res = {}
for w in t5.WORKS5:
    S = reparse(w); allowed = CORE[w] | EITHER[w]
    sels = [[f["para"] for f in t5.select_rule(j["features"])] for j in S]
    r = dict(reparse_selections=sels, reparse_zero=[i + 1 for i, s in enumerate(sels) if not s], reparse_outside=[sorted(set(s) - allowed) for s in sels])
    r["reparse_requoted_n"] = sum(1 for j in S for f in j["features"] if f.get("requoted"))
    r["reparse_still_unresolved"] = sum(1 for j in S for f in j["features"] if not f.get("resolve_ok"))
    ws = [w1(j) for j in S]; r["W1_AB_classorder"] = dict(selections=ws, zero=[i + 1 for i, s in enumerate(ws) if not s], outside=[sorted(set(s) - allowed) for s in ws])
    # sim_B再計算(parse補正後)
    combos = list(itertools.combinations(range(len(S)), 3)); sims = []
    for c in combos:
        s = t5.sim_B([S[i] for i in c]); ps = [x[0] for x in s["selected"]]
        sims.append(ps)
    r["simB_reparse"] = dict(combos=len(sims), ok=sum(1 for ps in sims if ps and set(ps) <= allowed), zero=sum(1 for ps in sims if not ps), outside=sum(1 for ps in sims if set(ps) - allowed), sets=sorted({tuple(ps) for ps in sims}))
    res[w] = r
json.dump(res, open(os.path.join(t5.BASE, "analysis_05b.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("\n=== SUPPLEMENTARY ===")
for w, r in res.items(): print(w, json.dumps(r, ensure_ascii=False))
