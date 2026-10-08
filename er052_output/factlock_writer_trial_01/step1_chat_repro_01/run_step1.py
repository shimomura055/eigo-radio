# -*- coding: utf-8 -*-
"""FACTLOCK 委任_10 Step1 ChatGPT再現度の要因分解 (Trial/DEV。Production経路ではない)。既存harnessはimportのみ。"""
import argparse, json, os, sys, time, threading
from concurrent.futures import ThreadPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "r3_minimal_01"))
import run_r3_minimal as m   # ROOTへchdir済み
BASE = "er052_output/factlock_writer_trial_01/step1_chat_repro_01"
R2 = "er052_output/all6_writer_redesign_necessity_01/runs/meta/control/b2__all6__r1/ja_writer/revision2.md"
LEDGER = "er052_output/open233_b3_trial_01/runs/meta/nb/V0/b2/research_ledger/verified_fact_ledger.txt"
FC_MODEL = "gpt-6-luna"
PRICES = {"gpt-6-luna": (0.10, 0.01, 0.50), "gpt-6-sol": (2.00, 0.20, 10.00)}
ASTRA_MULT = 2.5   # 単価未登録: sol単価x2.5の推定概算
PRICES["gpt-6-astra"] = tuple(x * ASTRA_MULT for x in PRICES["gpt-6-sol"])
DEV0 = "あなたは日本語のニュースを分かりやすく面白く伝える書き手です。"
DEV2 = ("あなたは熟練の編集者です。元記事の事実はそのままに、読者が思わず続きを聞きたくなる記事に書き直してください。"
        "構成の組み替え、段落の分け方、語りかけ、問いかけ、余韻のある結びなど、必要だと思う手段は自由に使ってください。")
LEN_FREE = "長さは自由です。元より長くなってもかまいません。"
_L = threading.Lock(); _S = {"cost": 0.0}


def build(cond, r2, sym):
    dev = DEV0 if cond == "F0" or cond == "F1" else DEV2
    u = f"以下の記事:\n\n{r2}\n\n{m.R3_SENTENCE}"
    if cond == "F0": u += sym
    if cond in ("F3", "F4"): u += LEN_FREE
    return dev, u


# (id, cond, model)
JOBS = [(f"{c}_{mo.split('-')[-1]}", c, mo) for c in ("F0", "F1", "F2", "F3") for mo in ("gpt-6-luna", "gpt-6-sol")]
JOBS += [("F3_astra", "F3", "gpt-6-astra"), ("F2_astra", "F2", "gpt-6-astra")]


def cost(u, model):
    p = PRICES[model]
    i, c, o = u.get("input_tokens") or 0, u.get("cached_input_tokens") or 0, u.get("output_tokens") or 0
    return ((i - c) * p[0] + c * p[1] + o * p[2]) / 1e6 * m.USD_JPY


def rec(rec_):
    with _L:
        _S["cost"] += rec_["cost_jpy"]
        with open(f"{BASE}/usage_log.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(rec_, ensure_ascii=False) + "\n")


def gen(client, jaw, r2, jid, cond, model, budget):
    out = f"{BASE}/runs/{jid}.md"
    if os.path.exists(out): return
    m.check_budget(budget)
    dev, u = build(cond, r2, jaw.SYMBOL_PREVENTION_BLOCK_JA)
    t0 = time.time()
    try:
        resp = client.responses.create(model=model, reasoning={"effort": "high"},
                                       input=[{"role": "developer", "content": dev}, {"role": "user", "content": u}])
    except Exception as e:  # noqa
        m.jwrite(f"{BASE}/runs/{jid}_ERROR.json", {"error": repr(e)[:800], "model": model, "cond": cond})
        print(f"[gen-ERR] {jid} {repr(e)[:200]}", flush=True); return
    sec = time.time() - t0
    us = m.usage_of(resp); c = cost(us, model)
    rec({"stage": "gen", "id": jid, "model": resp.model, "sec": round(sec, 1), "cost_jpy": round(c, 4),
         "price_estimated": model == "gpt-6-astra", **us})
    m.write(out, (resp.output_text or "").strip())
    m.jwrite(f"{BASE}/runs/{jid}_meta.json", {"id": jid, "cond": cond, "model": resp.model, "sec": round(sec, 1), "cost_jpy": round(c, 4), **us})
    print(f"[gen] {jid} {sec:.0f}s ¥{c:.2f} cum=¥{_S['cost']:.1f}", flush=True)


def fc(client, vfl01, name, path, budget):
    out = f"{BASE}/fc/{name}.json"
    if os.path.exists(out): return
    m.check_budget(budget)
    t0 = time.time()
    res = m.retry(lambda: vfl01.run_deviation_check(client, m.read(LEDGER), m.read(path).strip(), model=FC_MODEL,
                                                    hook_aware=False, include_related_fact_id=True), 2)
    sec = time.time() - t0; c = cost(res["usage"], FC_MODEL)
    rec({"stage": "fc", "id": name, "model": res["model"], "sec": round(sec, 1), "cost_jpy": round(c, 4), **res["usage"]})
    m.jwrite(out, {"parsed": res["parsed"], "model": res["model"], "sec": round(sec, 1), "cost_jpy": round(c, 4)})
    print(f"[fc] {name} {res['parsed'].get('overall_status')} cum=¥{_S['cost']:.1f}", flush=True)


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget-jpy", type=float, default=60); ap.add_argument("--parallel", type=int, default=10)
    ap.add_argument("--yes-run-paid", action="store_true"); ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    import er006_model_routing_contract_01 as routing
    import er019_family_x_ja_writer_o_r1_r2_01 as jaw
    import er003_v1_en_direct_vfl_01_generate as vfl01
    for mo in ("gpt-6-luna", "gpt-6-sol"):
        routing.require_model_or_override("B1_WRITER", mo, override_reason="FACTLOCK STEP1")
    routing.require_model_or_override("B1_WRITER", "gpt-6-astra", override_reason="FACTLOCK STEP1 F4")
    routing.require_model_or_override("WRITER_FACT_CHECK", FC_MODEL, override_reason="FACTLOCK STEP1")
    r2 = m.read(R2).strip()
    conds = {c: dict(zip(("developer", "user"), build(c, "{R2}", "<SYMBOL_BLOCK>"))) for c in ("F0", "F1", "F2", "F3", "F4")}
    m.jwrite(f"{BASE}/conditions.json", {"conditions": conds, "jobs": JOBS, "reasoning": "high", "astra_price_note": f"sol x{ASTRA_MULT} estimated"})
    if a.dry_run or not a.yes_run_paid:
        for c, v in conds.items(): print(c, "| dev:", v["developer"][:40], "| user tail:", repr(v["user"][-60:]))
        print("jobs", [j[0] for j in JOBS], "r2len", len(r2)); return 0
    client = vfl01.get_client(); t_all = time.time()
    with ThreadPoolExecutor(max_workers=a.parallel) as ex:
        list(ex.map(lambda j: gen(client, jaw, r2, j[0], j[1], j[2], a.budget_jpy), JOBS))
        names = [(j[0], f"{BASE}/runs/{j[0]}.md") for j in JOBS if os.path.exists(f"{BASE}/runs/{j[0]}.md")]
        names += [("chatgpt_logout", f"{BASE}/chatgpt_logout.txt"), ("orig_r2", R2)]
        list(ex.map(lambda n: fc(client, vfl01, n[0], n[1], a.budget_jpy), names))
    m.jwrite(f"{BASE}/MANIFEST.json", {"total_cost_jpy": round(_S["cost"], 3), "wall_sec": round(time.time() - t_all, 1)})
    print("done", round(_S["cost"], 2)); return 0

sys.exit(main())
