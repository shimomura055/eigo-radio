"""Trial専用(非Production)。委任_01: 抽出変種(L3等)の候補をP7候補と合流させ、既存SEL(無変更)で判定し、pick規則の変種(R0現行/R1型枠/R2出現回数昇格)で最終7件を比較する。
SEL判定は1 pool 1回(ledger記録)。pick規則はAPI 0の再計算。usage: python pool_pick_probe_01.py <repo_root> <case> <result_json> <variant> <sample_idx(1-based)>"""
import sys, os, json, glob, re
ROOT = os.path.abspath(sys.argv[1]); sys.path.insert(0, ROOT)
CASE, RES, VAR, SIDX = sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5])
from dotenv import load_dotenv
load_dotenv("C:/Users/tensh/eigo-radio/.env")
TD = os.path.join(ROOT, "docs/research/KP-N5-EXTRACTION-ROOT-IMPROVEMENT-TRIAL-01"); EV = os.path.join(TD, "ev01")
CAP_STOP = float(os.environ.get("N5R_CAP_STOP", "20.0"))
import er005_cost_logger as cl, er053_cost_aggregate_01 as agg
import er138_kp_n5_generalization_01 as n5, er062_family_z_structure_01 as st
def spent():
    return sum(agg.compute_stage_cost_breakdown_multi(p)["total_jpy"] for p in glob.glob(f"{EV}/cost_log*.jsonl"))
cl.install(f"{EV}/cost_log_poolpick.jsonl")
fx = json.load(open(f"{ROOT}/docs/research/KP-GENERALIZATION-N5-PRODUCTION-WIRING-01/fixtures/n5_trial_replay_fixture_01.json", encoding="utf-8"))
case = fx["cases"][CASE]; text = case["text"]
spans = json.load(open(RES, encoding="utf-8"))["runs"][VAR][SIDX - 1]["spans"]
base = [dict(c, n5_origin="P7", p7_rank=i + 1) for i, c in enumerate(case["base"])]
b1 = [{"span": s, "sentence": ""} for s in spans]
pool, rejected = n5.collect_pool(text, base, b1)
if spent() + 1.0 > CAP_STOP: raise SystemExit("cost guard")
ctx = n5.N5Ctx("B1_SUPPORT", tag=f"poolpick_{CASE}_{VAR}_{SIDX}", stop_check_fn=lambda w: st.check_stop_sentinel(w, EV), article_id="N5R_" + CASE)
log = n5.new_log("N5R")
with cl.logging_context("N5R_probe", "poolpick_sel"):
    judged = n5.select(text, pool, log, ctx)
sents = [s for s in re.split(r"(?<=[.!?])\s+", text.replace("\n", " ")) if s.strip()]
def occ(span):
    """出現回数(探索的特徴): spanの内容語lemmaが順序どおり、窓(語数+2)内で現れる文の数。"""
    ts = [t for t in n5.toks(span) if t not in n5.PLACE and t not in ("a", "an", "the", "it", "that", "this", "something", "someone")] if hasattr(n5, "PLACE") else n5.toks(span)
    if not ts: return 0
    L = [n5.lemmas(t) for t in ts]; c = 0
    for s in sents:
        tk = n5.toks(s); ok = False
        for i in range(len(tk)):
            if not (L[0] & n5.lemmas(tk[i])): continue
            j = i + 1; k = 1
            while k < len(L) and j < len(tk) and j <= i + len(ts) + 2:
                if L[k] & n5.lemmas(tk[j]): k += 1
                j += 1
            if k == len(L): ok = True; break
        c += ok
    return c
for c in judged: c["occ"] = occ(c["span"])
def pick_with(judged, cap, keyfn):
    ks = [c for c in judged if c["keep"]]; ks.sort(key=keyfn); out = []
    for c in ks:
        dfl = (c.get("display_form") or "").lower()
        if any(n5._contains(c["span"], o["span"]) for o in out): continue
        out.append(c)
    return out[:cap]
RK = n5.RANK
R = {
 "R0_current": lambda c: RK.get(c["difficulty"], 1),
 "R1_chunktype_tier": lambda c: RK.get(c["difficulty"], 1) - (1 if (c["difficulty"] == "easy" and c["chunk_type"] in ("phrasal_verb", "idiom")) else 0),
 "R2_occ_promote": lambda c: RK.get(c["difficulty"], 1) - (1 if (c["difficulty"] == "easy" and c["occ"] >= 3) else 0),
}
res = {"case": CASE, "variant": f"{VAR}#{SIDX}", "n_pool": len(pool), "n_rejected_pool": len(rejected), "n_keep": sum(1 for c in judged if c["keep"]),
       "judged": [{k: c.get(k) for k in ("span", "n5_origin", "cls", "chunk_type", "difficulty", "keep", "passive_fragment", "occ")} for c in judged], "picks": {}}
for name, kf in R.items():
    res["picks"][name] = [c["span"] for c in pick_with(judged, n5.PHRASE_PICK_CAP, kf)]
res["sel_cost_jpy"] = sum(m.get("cost_jpy") or 0 for m in ctx.metas)
fn = f"{EV}/poolpick_{CASE}_{VAR}_{SIDX}.json"
json.dump(res, open(fn, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({k: res[k] for k in ("n_pool", "n_keep", "sel_cost_jpy", "picks")}, ensure_ascii=False, indent=1)); print("spent", round(spent(), 3))
