"""Trial専用(委任_05)。A案(E2+A10 cap10)の候補のうち、現行N5出力/既存cacheに無いものへ正式N5の GEN5->VER5->CHK5(n5.generalize_verify_check、<=7件batch)を実行する。
対象集合(TRIAL_PLAN_05 §3): (A) 全rep(E2プール)のA10 cap10選定の和集合 (B) 現行B1方式A0 cap7の和集合(比較用) (X) 追加指定spans(--extra file: JSON {case:[span,...]})。
既知(gen_cache[ev02]・fixture trial_items・ev05 cache)は再実行しない。usage: python n5r_gen_05.py <proc> <case,case,...> [--dry] [--extra file]"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import n5r_lib_02 as L
n5 = L.n5
import er108_kp_cmu_lexicon_gate_01 as cmu

args = [a for a in sys.argv[1:] if not a.startswith("--")]
DRY = "--dry" in sys.argv
EXTRA = {}
if "--extra" in sys.argv:
    EXTRA = json.load(open(sys.argv[sys.argv.index("--extra") + 1], encoding="utf-8"))
    args = [a for a in args if a != sys.argv[sys.argv.index("--extra") + 1]]
PROC, CASES = args[0], args[1].split(",")
EV5 = os.path.join(L.TD, "ev05")
os.makedirs(EV5, exist_ok=True)
L.EV = EV5                                   # cost log / STOP sentinel / spent() はev05基準
if not DRY:
    L.install_log(PROC)
    n5.preflight()
fx = L.fixture()
import glob


def outcome(c):
    ck = c.get("check") or {}
    return {"outcome": "kept", "display_form": c["display_form"], "gloss_ja": c["gloss_ja"], "relation": ck.get("relation"), "verify": (c.get("verify") or {}).get("verdict"),
            "reverted": bool(c.get("reverted")), "flags": c.get("flags"), "cmu": cmu.reasons_for_phrase(c["display_form"]), "words_ok": 1 <= n5.ft.count_words(c["display_form"]) <= 5,
            "source": "ev05_run"}


for CASE in CASES:
    text = fx["cases"][CASE]["text"]
    reps = [json.load(open(f, encoding="utf-8")) for f in sorted(glob.glob(f"{os.path.join(L.TD, 'ev02')}/rep_{CASE}_*.json"))]
    cache_fn = f"{EV5}/gen_cache_05_{CASE}.json"
    cache = json.load(open(cache_fn, encoding="utf-8")) if os.path.exists(cache_fn) else {}
    known = set(cache)
    old = f"{os.path.join(L.TD, 'ev02')}/gen_cache_{CASE}.json"
    if os.path.exists(old): known |= set(json.load(open(old, encoding="utf-8")))
    known |= {L.norm_key(x["source_span"]) for x in fx["cases"][CASE]["trial_items"]}
    sent = {}
    for r in reps:
        for p in r["pools"].values():
            for c in p["judged"]:
                sent.setdefault(L.norm_key(c["span"]), c["sentence"])
    for b in fx["cases"][CASE]["base"]:
        sent.setdefault(L.norm_key(b["span"]), b.get("sentence") or "")
    A, B = {}, {}
    for r in reps:
        for c in L.pick_A10(r["pools"]["E2"]["judged"], text, 10): A.setdefault(L.norm_key(c["span"]), c["span"])
        for c in r["picks"]["A0"]: B.setdefault(L.norm_key(c["span"]), c["span"])
    pend = [s for k, s in A.items() if k not in known]
    pend += [s for k, s in B.items() if k not in known and k not in A]
    for s in EXTRA.get(CASE, []):
        if L.norm_key(s) not in known and L.norm_key(s) not in [L.norm_key(x) for x in pend]: pend.append(s)
    pend = [s for s in pend if L.norm_key(s) not in cache]
    print(CASE, "pending", len(pend), "batches", (len(pend) + 6) // 7); sys.stdout.flush()
    if DRY:
        print("   ", pend); continue
    ctx = L.make_ctx(CASE, PROC, f"n5r5_gen_{CASE}")
    blog = []
    for i in range(0, len(pend), 7):
        ch = pend[i:i + 7]
        L.guard(4.0); k0 = len(ctx.metas); t0 = time.time()
        cands = [dict(span=s, sentence=sent.get(L.norm_key(s), ""), key=L.norm_key(s), n5_origin="X") for s in ch]
        final, log = n5.generalize_verify_check(text, cands, ctx, tag=f"gen5_{i//7}")
        info = L.calls_info(ctx, k0, time.time() - t0)
        kept = {c["key"]: c for c in final}
        drops = {}
        for d in log.get("drops", []):
            drops.setdefault(d["key"], d)
        for c in cands:
            k = c["key"]
            if k in kept:
                cache[k] = dict(outcome(kept[k]), span=c["span"], sentence=c["sentence"], batch=f"{CASE}_{i//7}")
            else:
                d = drops.get(k) or {}
                cache[k] = {"outcome": "dropped", "span": c["span"], "sentence": c["sentence"], "drop_stage": d.get("stage"), "reasons": d.get("reasons"), "batch": f"{CASE}_{i//7}", "source": "ev05_run"}
        json.dump(cache, open(cache_fn, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        blog.append({"case": CASE, "batch": i // 7, "n": len(ch), **{k: info[k] for k in ("cost_jpy", "sec", "truncated", "attempts_gt1", "n_calls")}})
        print(CASE, "batch", i // 7, len(ch), "cost", info["cost_jpy"], "sec", info["sec"], "spent", round(L.spent(), 2)); sys.stdout.flush()
    if blog:
        prev = f"{EV5}/gen_batches_05_{CASE}_{PROC}.json"
        json.dump(blog, open(prev, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
