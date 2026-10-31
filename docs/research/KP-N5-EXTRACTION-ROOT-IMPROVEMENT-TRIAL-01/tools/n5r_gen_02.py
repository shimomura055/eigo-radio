"""Trial専用。pick済み最終候補へ GEN5->VER5->CHK5(n5.generalize_verify_check、7件以下のbatch)を実行(TRIAL_PLAN_02 §2-8/9)。
同一(記事,span)はcache(ev02/gen_cache_<case>.json)共有。usage: python n5r_gen_02.py <proc_label> <case> <arm,arm,...|ALL> [confirm=<arm>:<rep>]
A0は常に含める。ALL=picksにある全アーム。"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import n5r_lib_02 as L
n5 = L.n5
import er108_kp_cmu_lexicon_gate_01 as cmu

PROC, CASE, ARMS = sys.argv[1], sys.argv[2], sys.argv[3]
CONFIRM = [a for a in sys.argv[4:] if a.startswith("confirm=")]
L.install_log(PROC)
n5.preflight()
fx = L.fixture(); text = fx["cases"][CASE]["text"]
reps = sorted(int(f.split("_")[-1].split(".")[0]) for f in os.listdir(L.EV) if f.startswith(f"rep_{CASE}_") and f.endswith(".json"))
R = {r: json.load(open(f"{L.EV}/rep_{CASE}_{r}.json", encoding="utf-8")) for r in reps}
cache_fn = f"{L.EV}/gen_cache_{CASE}.json"
cache = json.load(open(cache_fn, encoding="utf-8")) if os.path.exists(cache_fn) else {}
sent = {}
for r in R.values():
    for p in r["pools"].values():
        for c in p["judged"]:
            sent.setdefault(L.norm_key(c["span"]), c["sentence"])
arms = sorted({a for r in R.values() for a in r["picks"]}) if ARMS == "ALL" else ARMS.split(",")
if "A0" not in arms: arms = ["A0"] + arms
ctx = L.make_ctx(CASE, PROC, f"n5r2_gen_{CASE}")


def outcome(c):
    ck = c.get("check") or {}
    return {"outcome": "kept", "display_form": c["display_form"], "gloss_ja": c["gloss_ja"], "relation": ck.get("relation"), "verify": (c.get("verify") or {}).get("verdict"),
            "reverted": bool(c.get("reverted")), "flags": c.get("flags"), "cmu": cmu.reasons_for_phrase(c["display_form"]), "words_ok": 1 <= n5.ft.count_words(c["display_form"]) <= 5}


def run_batches(spans, tag):
    for i in range(0, len(spans), 7):
        ch = spans[i:i + 7]
        L.guard(4.0); k0 = len(ctx.metas); t0 = time.time()
        cands = [dict(span=s, sentence=sent.get(L.norm_key(s), ""), key=L.norm_key(s), n5_origin="X") for s in ch]
        final, log = n5.generalize_verify_check(text, cands, ctx, tag=f"{tag}_{i//7}")
        info = L.calls_info(ctx, k0, time.time() - t0)
        kept = {c["key"]: c for c in final}
        drops = {}
        for d in log.get("drops", []):
            drops.setdefault(d["key"], d)
        for c in cands:
            k = c["key"]
            if k in kept:
                cache[k] = dict(outcome(kept[k]), span=c["span"], sentence=c["sentence"], batch=f"{tag}_{i//7}")
            else:
                d = drops.get(k) or {}
                cache[k] = {"outcome": "dropped", "span": c["span"], "sentence": c["sentence"], "drop_stage": d.get("stage"), "reasons": d.get("reasons"), "batch": f"{tag}_{i//7}"}
        json.dump(cache, open(cache_fn, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(CASE, tag, "batch", i // 7, len(ch), "cost", info["cost_jpy"], "sec", info["sec"], "spent", round(L.spent(), 2)); sys.stdout.flush()
        batch_log.append({"tag": f"{tag}_{i//7}", "n": len(ch), **{k: info[k] for k in ("cost_jpy", "sec", "truncated", "attempts_gt1", "n_calls")}})


batch_log = []
if not CONFIRM:
    pend = []
    for r in reps:
        for a in arms:
            for c in R[r]["picks"].get(a, []):
                k = L.norm_key(c["span"])
                if k not in cache and c["span"] not in pend and k not in [L.norm_key(x) for x in pend]:
                    pend.append(c["span"])
    print(CASE, "arms", arms, "pending", len(pend), "cached", len(cache)); sys.stdout.flush()
    run_batches(pend, "gen")
    json.dump(batch_log, open(f"{L.EV}/gen_batches_{CASE}_{PROC}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
else:
    arm, rep = CONFIRM[0].split("=")[1].split(":"); rep = int(rep)
    spans = [c["span"] for c in R[rep]["picks"][arm]]
    old = {k: dict(v) for k, v in cache.items()}
    tmp = {}
    cands = [dict(span=s, sentence=sent.get(L.norm_key(s), ""), key=L.norm_key(s), n5_origin="X") for s in spans]
    L.guard(4.0)
    final, log = n5.generalize_verify_check(text, cands, ctx, tag=f"confirm_{arm}_{rep}")
    kept = {c["key"]: c for c in final}
    res = []
    for c in cands:
        new = outcome(kept[c["key"]]) if c["key"] in kept else {"outcome": "dropped"}
        o = old.get(c["key"], {})
        res.append({"span": c["span"], "cache_outcome": o.get("outcome"), "cache_relation": o.get("relation"), "cache_form": o.get("display_form"), "confirm": new.get("outcome"), "confirm_relation": new.get("relation"),
                    "confirm_form": new.get("display_form"), "confirm_gloss": new.get("gloss_ja"), "same": o.get("outcome") == new.get("outcome") and o.get("relation") == new.get("relation")})
    json.dump({"arm": arm, "rep": rep, "items": res, "cost_jpy": round(sum(m.get("cost_jpy") or 0 for m in ctx.metas), 3)}, open(f"{L.EV}/confirm_{CASE}_{arm}_{rep}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(res, ensure_ascii=False, indent=1)); print("spent", round(L.spent(), 2))
