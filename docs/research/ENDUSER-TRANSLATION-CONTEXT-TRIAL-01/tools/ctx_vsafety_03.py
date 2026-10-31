# V安全試験runner(TRIAL_PLAN_02 §6)。わざと誤りを入れた対訳unitに対し、verify(Production VERIFY_HEAD)を noV / CV / DV / EV で呼ぶ。verify呼出のみ。
import json, os, sys, time, argparse
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.getcwd()
sys.path.insert(0, ROOT); sys.path.insert(0, HERE)
import ctx_methods_02 as CM
import ctx_run_03 as RUN
ap = argparse.ArgumentParser()
ap.add_argument("--set", required=True); ap.add_argument("--out", required=True); ap.add_argument("--mock", action="store_true")
a = ap.parse_args()
import er135_enduser_translate_01 as TR
if not a.mock:
    from dotenv import load_dotenv
    load_dotenv(r"C:\Users\tensh\eigo-radio\.env")
os.makedirs(a.out, exist_ok=True)
units = json.load(open(a.set, encoding="utf-8"))["units"]
res_p = os.path.join(a.out, "vsafety_results_03.jsonl"); led_p = os.path.join(a.out, "ledger_vsafety.jsonl")
done = set()
if os.path.exists(res_p):
    for ln in open(res_p, encoding="utf-8"):
        d = json.loads(ln); done.add((d["id"], d["cond"]))
llm = None if a.mock else TR.DefaultLLM()
for u in units:
    art = json.load(open(os.path.join(ROOT, "user_test", u["slug"], "enduser", "data", "article.json"), encoding="utf-8"))
    pairs = [(p["en"], p["ja"]) for p in u["pairs"]]
    base = TR.build_verify_prompt(pairs)
    for cond, method in (("noV", None), ("CV", "C"), ("DV", "D"), ("EV", "E")):
        if (u["id"], cond) in done:
            continue
        if os.path.exists(os.path.join(RUN.TRIAL_DIR, "STOP")) or os.path.exists(os.path.join(a.out, "STOP")):
            print("STOP sentinel"); sys.exit(3)
        if RUN.spent_total() >= 85.0:
            print("HARD CAP"); sys.exit(4)
        prompt = base
        ctx = []
        if method:
            ctx = [c["en"] for c in CM.build_context(method, art, u["level"], u["part"])]
            tail = "# 対訳\n"
            assert TR.VERIFY_HEAD.endswith(tail) and base.startswith(TR.VERIFY_HEAD)
            prompt = TR.VERIFY_HEAD[:-len(tail)] + RUN.VERIFY_CONTEXT_LABEL + "\n".join(f"- {c}" for c in ctx) + "\n\n" + tail + base[len(TR.VERIFY_HEAD):]
        t0 = time.time()
        if a.mock:
            text = json.dumps({"results": [{"id": i, "ok": True} for i in range(1, len(pairs) + 1)]}); cost = 0.0; usage = {}
        else:
            n0 = len(llm.calls); text = llm("verify", prompt); c = llm.calls[-1]; cost = c["cost_jpy"]; usage = c["usage"]
        dt = time.time() - t0
        try:
            v = TR.parse_verify(text, len(pairs)); err = None
        except ValueError as e:
            v = None; err = str(e)
        tix = [i for i, p in enumerate(u["pairs"], 1) if p["sid"] == u["target_sid"]][0]
        row = {"id": u["id"], "type": u["type"], "cond": cond, "ctx_n": len(ctx), "target_idx": tix, "parse_error": err,
               "caught": (None if v is None else (not v[tix][0])), "target_issue": (None if v is None else v[tix][1]),
               "false_rejects": (None if v is None else [i for i in v if i != tix and not v[i][0]]), "n_pairs": len(pairs), "cost_jpy": cost, "wall_s": round(dt, 2), "raw": text}
        open(res_p, "a", encoding="utf-8").write(json.dumps(row, ensure_ascii=False) + "\n")
        open(led_p, "a", encoding="utf-8").write(json.dumps({"t": time.strftime("%Y-%m-%dT%H:%M:%S"), "cond": cond, "unit": u["id"], "kind": "verify", "wall_s": round(dt, 2), "usage": usage, "cost_jpy": cost}, ensure_ascii=False) + "\n")
        print(u["id"], cond, "caught", row["caught"], "cost", cost, flush=True)
print("DONE")
