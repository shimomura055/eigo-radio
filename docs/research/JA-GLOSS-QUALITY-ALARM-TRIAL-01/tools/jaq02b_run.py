# -*- coding: utf-8 -*-
"""JA-GLOSS-QUALITY-ALARM-TRIAL-01 委任_02B runner(Trial専用・Production非接続)。モデル=gpt-6-luna固定。
使い方: jaq02b_run.py --run NAME --method {M1,M2,M3,R6,M6,M5} --effort {low,medium,high} --phase {dev,final} [--rep N] [--ref] [--base RUN] [--workers 6]
ledger=trial/ledger_02b.json(呼出ごと)。Cap=60円: 止め線48円で警告出力、HARD=55円到達見込みで停止(rc=3)。再実行は完了済みjobをskip(二重課金なし)。
検査失敗(API error/JSON破損/idの抜け)は『警告なし』に数えず `unchecked` として別掲(R-10)。"""
import json, os, re, sys, time, random, argparse, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jaq02b_prompts as P

MODEL = "gpt-6-luna"
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.path.dirname(HERE); TRIAL = os.path.join(BASE, "trial")
ENV = r"C:\Users\tensh\eigo-radio\.env"
P_IN, P_CACHED, P_OUT, FX = 0.10, 0.01, 0.50, 160.0
CAP, LINE, HARD = 60.0, 48.0, 55.0
LEDGER = os.path.join(TRIAL, "ledger_02b.json")
LOCK = threading.Lock()
J = lambda p: json.load(open(p, encoding="utf-8"))


def norm(s):
    return re.sub(r"\s+", " ", s.replace("’", "'").replace("‘", "'")).strip().lower()


def cost_jpy(u):
    inp = u.get("input_tokens") or 0; c = u.get("cached_input_tokens") or 0; out = u.get("output_tokens") or 0
    return ((inp - c) * P_IN + c * P_CACHED + out * P_OUT) / 1e6 * FX


def ledger_load():
    if os.path.exists(LEDGER): return J(LEDGER)
    return {"model": MODEL, "cap_jpy": CAP, "stop_line_jpy": LINE, "hard_stop_jpy": HARD, "calls": [], "total_jpy": 0.0, "line_crossed": False}


def ledger_add(rec):
    with LOCK:
        L = ledger_load(); L["calls"].append(rec); L["total_jpy"] = round(L["total_jpy"] + rec["cost_jpy"], 4)
        if L["total_jpy"] >= LINE and not L["line_crossed"]:
            L["line_crossed"] = True; print("!!! 止め線48円到達 total", L["total_jpy"], flush=True)
        json.dump(L, open(LEDGER, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        return L["total_jpy"]


def ledger_total():
    with LOCK: return ledger_load()["total_jpy"]


def throttle():
    """runner規則: 300秒窓で起動<=2、起動間隔>=150秒。"""
    p = os.path.join(TRIAL, "launches_02b.jsonl")
    ts = []
    if os.path.exists(p): ts = [json.loads(l)["t"] for l in open(p, encoding="utf-8") if l.strip()]
    while True:
        now = time.time()
        recent = [t for t in ts if now - t < 300]
        wait = 0
        if ts and now - max(ts) < 150: wait = 150 - (now - max(ts))
        if len(recent) >= 2: wait = max(wait, 300 - (now - min(recent)))
        if wait <= 0: break
        print(f"throttle wait {wait:.0f}s", flush=True); time.sleep(min(wait, 60) + 1)
    with open(p, "a", encoding="utf-8") as f: f.write(json.dumps({"t": time.time(), "argv": sys.argv[1:]}) + "\n")


def m8_check():
    """M-8: eval items.json(131) とプール261の expression / current_ja がPrompt本文・schemaに含まれないことを機械照合。"""
    items = J(os.path.join(BASE, "eval_set/items.json")); pool = J(os.path.join(BASE, "adjudication/pool.json"))
    texts = dict(P.all_prompt_texts())
    texts["SCHEMAS"] = json.dumps(P.SCHEMAS, ensure_ascii=False)
    blob = "\n".join(texts.values())
    lblob = blob.lower()
    hits = []; seen = set()
    for src, rows in (("eval", items), ("pool", pool)):
        for r in rows:
            ex = r["expression"].strip().lower(); cj = r["current_ja"].strip()
            if ex and (ex, "e") not in seen:
                seen.add((ex, "e"))
                if re.search(r"(?<![a-z])" + re.escape(ex) + r"(?![a-z])", lblob): hits.append((src, "expression", r["expression"]))
            if len(cj) >= 2 and (cj, "j") not in seen:
                seen.add((cj, "j"))
                if cj in blob: hits.append((src, "current_ja", cj))
    return {"pass": not hits, "hits": hits, "prompt_sha256": P.prompt_sha(), "n_eval": len(items), "n_pool": len(pool), "n_distinct_checked": len(seen)}


def load_all():
    return J(os.path.join(TRIAL, "units.json"))


def slug_of(u, slugs):
    if u["kind"] == "pool": return u["slug"]
    return next((s for s in slugs if s in u["article_key"]), None)


def build_ref(U):
    slugs = sorted({u["slug"] for u in U.values() if u["kind"] == "pool"})
    d = {}
    for u in U.values():
        if u["kind"] == "pool":
            d.setdefault((u["slug"], norm(u["expression"])), {})[u["level"]] = u["current_ja"]
    return d, slugs


def other_level(u, d, slugs):
    """同じ記事の他levelで同じ表現に付いている訳(R-9(a))。合成項目も同じ表現なので同じ参照になる。"""
    sl = slug_of(u, slugs)
    if not sl: return None
    m = d.get((sl, norm(u["expression"])), {})
    for lv, ja in m.items():
        if lv != u["level"]: return ja
    return None


def item_line(u, cid, ref_ja=None):
    o = {"id": cid, "expression": u["expression"], "current_ja": u["current_ja"], "sentence_en": u["sentence_en"],
         "context_before": u["context_before"], "context_after": u["context_after"]}
    if ref_ja: o["other_level_ja"] = ref_ja
    return json.dumps(o, ensure_ascii=False)


def user_msg(article_text, level, lines):
    return "\n".join(["【記事全文(英語)】", article_text, "", "【レベル】" + level, "", "【検査対象】"] + lines)


_client = None


def client():
    global _client
    if _client is None:
        from dotenv import load_dotenv
        load_dotenv(ENV)
        from openai import OpenAI
        _client = OpenAI(timeout=240.0, max_retries=0)
    return _client


def llm(developer, user, schema_key, effort, tag):
    if ledger_total() + 0.45 > HARD:
        raise RuntimeError("HARD_STOP_BUDGET")
    t0 = time.time()
    r = client().responses.create(model=MODEL, reasoning={"effort": effort}, text={"format": {"type": "json_schema", **P.SCHEMAS[schema_key]}},
                                  input=[{"role": "developer", "content": developer}, {"role": "user", "content": user}])
    el = round(time.time() - t0, 1)
    u = r.usage
    usage = {"input_tokens": u.input_tokens, "output_tokens": u.output_tokens, "cached_input_tokens": getattr(getattr(u, "input_tokens_details", None), "cached_tokens", 0) or 0}
    c = cost_jpy(usage)
    ledger_add({"tag": tag, "model": r.model, "response_id": r.id, "usage": usage, "cost_jpy": round(c, 4), "elapsed_s": el, "t": time.strftime("%Y-%m-%d %H:%M:%S")})
    if r.model != MODEL and not str(r.model).startswith(MODEL):
        raise RuntimeError("MODEL_MISMATCH " + str(r.model))
    return json.loads(r.output_text), usage, c, el, r.model, r.id


def call_retry(developer, user, schema_key, effort, tag, expect_ids):
    """1回再試行。id集合照合に失敗/例外は再試行→それでも失敗なら ok=False(R-10: 警告なしに数えない)。"""
    last = None; partial = None; agg = {"usage": [], "cost": 0.0, "elapsed": 0.0, "attempts": 0}
    for att in range(2):
        try:
            out, usage, c, el, model, rid = llm(developer, user, schema_key, effort, tag + f"|a{att}")
            agg["attempts"] += 1; agg["cost"] += c; agg["elapsed"] += el; agg["usage"].append(usage)
            got = [x.get("id") for x in out.get("results", [])]
            if sorted(got) == sorted(expect_ids) and len(set(got)) == len(got):
                return {"ok": True, "output": out, "model": model, "response_id": rid, **agg}
            last = f"id mismatch: missing={sorted(set(expect_ids) - set(got))} extra={sorted(set(got) - set(expect_ids))}"
            partial = out
        except RuntimeError as e:
            if "HARD_STOP" in str(e) or "MODEL_MISMATCH" in str(e): raise
            last = "exc:" + repr(e)[:200]
        except Exception as e:
            last = "exc:" + repr(e)[:200]
    return {"ok": False, "error": last, "partial": partial, **agg}


def make_order(bid, rep):
    return random.Random(f"{bid}|{rep}|20261101")


def run_batch(U, b, method, effort, rep, ref, refd, slugs, outdir, base_dir=None):
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", b["bid"])
    fn = os.path.join(outdir, safe + ".json")
    if os.path.exists(fn):
        prev = J(fn)
        if prev["stages"] and all(s.get("ok") for s in prev["stages"].values()): return prev
    uids = list(b["uids"])
    if method == "M1": uids = list(b["scored"])
    if method == "M5":
        uids = list(b["uids"])
    make_order(b["bid"], rep).shuffle(uids)
    idmap = {f"c{k+1:02d}": uid for k, uid in enumerate(uids)}
    rev = {v: k for k, v in idmap.items()}
    rec = {"bid": b["bid"], "method": method, "effort": effort, "rep": rep, "ref": ref, "idmap": idmap, "scored": b["scored"], "stages": {}, "model": MODEL}
    text = b["article_text"]; lv = b["level"]
    tag = f"{os.path.basename(outdir)}|{b['bid']}"
    lines = [item_line(U[uid], rev[uid], other_level(U[uid], refd, slugs) if ref else None) for uid in uids]
    if method in ("M2", "M3", "R6", "M3v2", "R6v2"):
        dev = P.developer_text(method, ref, True)
        sk = {"M2": "base", "M3": "m3", "R6": "r6", "M3v2": "m3", "R6v2": "r6"}[method]
        rec["stages"]["s1"] = call_retry(dev, user_msg(text, lv, lines), sk, effort, tag + "|s1", list(idmap))
    elif method == "M1":
        res = {"ok": True, "outputs": {}, "cost": 0.0, "elapsed": 0.0}
        dev = P.developer_text("M1", ref, False)
        for cid, uid in idmap.items():
            one = [item_line(U[uid], cid, other_level(U[uid], refd, slugs) if ref else None)]
            r = call_retry(dev, user_msg(text, lv, one), "base", effort, tag + "|" + cid, [cid])
            res["cost"] += r["cost"]; res["elapsed"] += r["elapsed"]
            if r["ok"]: res["outputs"][cid] = r["output"]["results"][0]
            else:
                res["ok"] = False; res.setdefault("errors", {})[cid] = r["error"]
        res["output"] = {"results": list(res["outputs"].values())}
        rec["stages"]["s1"] = res
    elif method == "M6":
        l1 = [json.dumps({"id": k, "expression": U[u]["expression"], "sentence_en": U[u]["sentence_en"], "context_before": U[u]["context_before"], "context_after": U[u]["context_after"]}, ensure_ascii=False) for k, u in idmap.items()]
        r1 = call_retry(P.M6S1, user_msg(text, lv, l1), "m6s1", effort, tag + "|s1", list(idmap))
        rec["stages"]["s1"] = r1
        if r1["ok"]:
            bests = {x["id"]: x for x in r1["output"]["results"]}
            need = []; skipped = []
            for cid, uid in idmap.items():
                cur = norm(U[uid]["current_ja"]); bj = bests[cid]
                if cur == norm(bj["best_ja"]) or cur in [norm(x) for x in bj["acceptable_alternatives"]]: skipped.append(cid)
                else: need.append(cid)
            rec["m6_skipped_equal"] = sorted(skipped)
            if need:
                l2 = []
                for cid in need:
                    u = U[idmap[cid]]
                    l2.append(json.dumps({"id": cid, "expression": u["expression"], "current_ja": u["current_ja"], "best_ja": bests[cid]["best_ja"],
                                          "acceptable_alternatives": bests[cid]["acceptable_alternatives"], "sentence_en": u["sentence_en"],
                                          "context_before": u["context_before"], "context_after": u["context_after"]}, ensure_ascii=False))
                rec["stages"]["s2"] = call_retry(P.M6S2, user_msg(text, lv, l2), "m6s2", effort, tag + "|s2", need)
    elif method == "M5":
        bfn = os.path.join(base_dir, safe + ".json")
        if not os.path.exists(bfn): return rec
        bs = J(bfn)
        s1 = bs["stages"]["s1"]
        rec["idmap"] = bs["idmap"]
        if not s1.get("ok"): return rec
        cand = [x for x in s1["output"]["results"] if x["warn"] and x["suggestion"].strip()]
        rec["m5_candidates"] = [x["id"] for x in cand]
        if cand:
            rr = make_order(b["bid"], "m5")
            l2 = []; ab = {}
            for x in cand:
                u = U[bs["idmap"][x["id"]]]
                cur_is_A = rr.random() < 0.5
                ab[x["id"]] = "A" if cur_is_A else "B"
                A, B_ = (u["current_ja"], x["suggestion"]) if cur_is_A else (x["suggestion"], u["current_ja"])
                l2.append(json.dumps({"id": x["id"], "expression": u["expression"], "A": A, "B": B_, "sentence_en": u["sentence_en"],
                                      "context_before": u["context_before"], "context_after": u["context_after"]}, ensure_ascii=False))
            rec["m5_current_side"] = ab
            rec["stages"]["s2"] = call_retry(P.M5S2, user_msg(text, lv, l2), "m5s2", effort, tag + "|s2", [x["id"] for x in cand])
        else:
            rec["stages"]["s2"] = {"ok": True, "output": {"results": []}, "cost": 0.0, "elapsed": 0.0}
    os.makedirs(outdir, exist_ok=True)
    json.dump(rec, open(fn, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return rec


def main_multi(specs, workers):
    """1回の起動で複数runを同時実行(起動間隔規則の遵守と待機短縮)。spec=name:method:effort:phase:rep:ref(0/1):base"""
    chk = m8_check()
    json.dump(chk, open(os.path.join(TRIAL, f"m8_check_{chk['prompt_sha256'][:12]}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if not chk["pass"]:
        print("M-8 FAIL", chk["hits"]); sys.exit(5)
    print("M-8 PASS prompt_sha", chk["prompt_sha256"][:16])
    U = load_all(); refd, slugs = build_ref(U)
    throttle()
    tasks = []
    for sp in specs:
        name, method, effort, phase, rep, ref, base = (sp.split(":") + [""] * 7)[:7]
        B = J(os.path.join(TRIAL, f"batches_{phase}.json"))
        outdir = os.path.join(TRIAL, "out", name); os.makedirs(outdir, exist_ok=True)
        json.dump({"run": name, "spec": sp, "prompt_sha256": chk["prompt_sha256"], "model": MODEL, "t": time.strftime("%Y-%m-%d %H:%M:%S"), "n_batches": len(B)},
                  open(os.path.join(outdir, "_run.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        base_dir = os.path.join(TRIAL, "out", base) if base else None
        for b in B: tasks.append((name, b, method, effort, int(rep or 1), ref == "1", outdir, base_dir))
    t0 = time.time(); rc = 0; done = 0
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(run_batch, U, b, m, e, r, rf, refd, slugs, od, bd): (n, b["bid"]) for (n, b, m, e, r, rf, od, bd) in tasks}
        for f in as_completed(futs):
            try:
                f.result(); done += 1
            except RuntimeError as e:
                print("STOP:", e); rc = 3
            except Exception as e:
                print("ERR", futs[f], repr(e)[:200]); rc = 1
    print(f"multi done {done}/{len(tasks)} elapsed {time.time()-t0:.0f}s ledger_total {ledger_total():.3f}")
    sys.exit(rc)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--multi":
        w = 8
        specs = [x for x in sys.argv[2:] if not x.startswith("--workers=")]
        for x in sys.argv[2:]:
            if x.startswith("--workers="): w = int(x.split("=")[1])
        return main_multi(specs, w)
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True); ap.add_argument("--method", required=True); ap.add_argument("--effort", default="medium")
    ap.add_argument("--phase", default="dev"); ap.add_argument("--rep", type=int, default=1); ap.add_argument("--ref", action="store_true")
    ap.add_argument("--base"); ap.add_argument("--workers", type=int, default=6); ap.add_argument("--only"); ap.add_argument("--dry", action="store_true")
    ap.add_argument("--no-throttle", action="store_true")
    a = ap.parse_args()
    chk = m8_check()
    json.dump(chk, open(os.path.join(TRIAL, f"m8_check_{chk['prompt_sha256'][:12]}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if not chk["pass"]:
        print("M-8 FAIL", chk["hits"]); sys.exit(5)
    print("M-8 PASS prompt_sha", chk["prompt_sha256"][:16], "distinct checked", chk["n_distinct_checked"])
    U = load_all()
    B = J(os.path.join(TRIAL, f"batches_{a.phase}.json"))
    if a.only: B = [b for b in B if re.search(a.only, b["bid"])]
    refd, slugs = build_ref(U)
    outdir = os.path.join(TRIAL, "out", a.run)
    base_dir = os.path.join(TRIAL, "out", a.base) if a.base else None
    if a.dry:
        print("DRY batches", len(B)); return
    os.makedirs(outdir, exist_ok=True)
    if not a.no_throttle: throttle()
    json.dump({"run": a.run, "args": vars(a), "prompt_sha256": chk["prompt_sha256"], "model": MODEL, "t": time.strftime("%Y-%m-%d %H:%M:%S"), "n_batches": len(B)},
              open(os.path.join(outdir, "_run.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    t0 = time.time(); done = 0; rc = 0
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = {ex.submit(run_batch, U, b, a.method, a.effort, a.rep, a.ref, refd, slugs, outdir, base_dir): b for b in B}
        for f in as_completed(futs):
            try:
                f.result(); done += 1
            except RuntimeError as e:
                print("STOP:", e); rc = 3
            except Exception as e:
                print("ERR", futs[f]["bid"], repr(e)[:200]); rc = 1
    print(f"run {a.run} done {done}/{len(B)} elapsed {time.time()-t0:.0f}s ledger_total {ledger_total():.3f}")
    sys.exit(rc)


if __name__ == "__main__":
    main()
