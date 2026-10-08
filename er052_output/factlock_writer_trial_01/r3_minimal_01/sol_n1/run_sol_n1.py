# -*- coding: utf-8 -*-
"""FACTLOCK 委任_07: R3-fresh を gpt-6-sol で N=1 (Trial/DEV)。run_r3_minimal.pyは編集せずimportのみ。"""
import argparse, json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
R3DIR = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, R3DIR)
import run_r3_minimal as m   # ROOTへchdir済み
sys.path.insert(0, "er052_output/factlock_writer_trial_01/sweep_01/tools")
import style_metrics as sm
import er003_audio_tts_asr_safety as safety

OUT = "er052_output/factlock_writer_trial_01/r3_minimal_01/sol_n1"
SOL = (2.00, 0.20, 10.00)
JUDGE = "gpt-6-luna"


def cost(u, price):
    i, c, o = u.get("input_tokens") or 0, u.get("cached_input_tokens") or 0, u.get("output_tokens") or 0
    return ((i - c) * price[0] + c * price[1] + o * price[2]) / 1e6 * m.USD_JPY


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", default="meta"); ap.add_argument("--brief", default="b2")
    ap.add_argument("--model", default="gpt-6-sol"); ap.add_argument("--budget-jpy", type=float, default=15)
    ap.add_argument("--yes-run-paid", action="store_true")
    a = ap.parse_args()
    import er006_model_routing_contract_01 as routing
    import er019_family_x_ja_writer_o_r1_r2_01 as jaw
    import er003_v1_en_direct_vfl_01_generate as vfl01
    routing.require_model_or_override("B1_WRITER", a.model, override_reason="FACTLOCK R3 SOL N=1")
    routing.require_model_or_override("WRITER_FACT_CHECK", JUDGE, override_reason="FACTLOCK R3 SOL N=1 FC/judge")
    it = [x for x in m.select_sources() if x["slug"] == a.slug and f"b{x['b']}" == a.brief][0]
    r2 = m.read(it["r2_path"]).strip()
    if not a.yes_run_paid:
        print("dry", it["key"], len(r2)); return 2
    client = vfl01.get_client()
    log = []
    total = 0.0

    def rec(stage, resp, price, sec, **kw):
        nonlocal total
        u = m.usage_of(resp); c = cost(u, price); total += c
        log.append({"stage": stage, "model": resp.model, "sec": round(sec, 1), "cost_jpy": round(c, 4), **u, **kw})
        m.jwrite(f"{OUT}/usage_log.json", log)
        return c

    # (1) sol R3 fresh
    user = m.build_fresh_input(r2, jaw.SYMBOL_PREVENTION_BLOCK_JA)
    msgs = [{"role": "developer", "content": jaw.DEVELOPER_MESSAGE}, {"role": "user", "content": user}]
    eff, note = jaw.WRITER_EFFORT, "high"
    t0 = time.time()
    try:
        resp = client.responses.create(model=a.model, reasoning={"effort": eff}, input=msgs)
    except Exception as e:
        print("high failed:", repr(e)[:300]); eff = "medium"; note = f"high失敗({repr(e)[:200]})->medium"
        t0 = time.time(); resp = client.responses.create(model=a.model, reasoning={"effort": eff}, input=msgs)
    sec = time.time() - t0
    rec("r3_sol", resp, SOL, sec, effort=eff, note=note)
    text = (resp.output_text or "").strip()
    m.write(f"{OUT}/r3_sol.md", text)
    print(f"[gen] {sec:.0f}s effort={eff} cum=¥{total:.2f}", flush=True)

    # (2) JA FC (luna)
    t0 = time.time()
    res = vfl01.run_deviation_check(client, m.read(it["ledger_path"]), text, model=JUDGE, hook_aware=False, include_related_fact_id=True)
    sec = time.time() - t0
    c = cost(res["usage"], m.PRICE); total += c
    log.append({"stage": "fc_sol", "model": res["model"], "sec": round(sec, 1), "cost_jpy": round(c, 4), **res["usage"]})
    m.jwrite(f"{OUT}/fc_sol.json", {"parsed": res["parsed"], "model": res["model"], "sec": round(sec, 1)})
    print("[fc]", res["parsed"].get("overall_status"), f"cum=¥{total:.2f}", flush=True)

    # (3) pairwise
    luna_r3 = m.read(f"{R3DIR}/runs/{a.slug}/{a.brief}/r3_fresh.md").strip()
    for tag, other in (("vs_r2", r2), ("vs_luna", luna_r3)):
        for order in (0, 1):
            x, y = (text, other) if order == 0 else (other, text)
            t0 = time.time()
            r = client.responses.create(model=JUDGE, reasoning={"effort": "medium"},
                text={"format": {"type": "json_schema", **m.PW_SCHEMA}},
                input=[{"role": "developer", "content": m.PW_DEV},
                       {"role": "user", "content": f"{m.PW_INSTR}\n\n# 記事A\n{x}\n\n# 記事B\n{y}\n"}])
            sec = time.time() - t0
            c = cost(m.usage_of(r), m.PRICE); total += c
            log.append({"stage": f"pw_{tag}_o{order}", "model": r.model, "sec": round(sec, 1), "cost_jpy": round(c, 4), **m.usage_of(r)})
            p = json.loads(r.output_text); lab = p["winner"]
            w = "sol" if (lab == "A" and order == 0) or (lab == "B" and order == 1) else ("other" if lab != "tie" else "tie")
            m.jwrite(f"{OUT}/pairwise_{tag}_o{order}.json", {"A": "sol" if order == 0 else "other", "B": "other" if order == 0 else "sol",
                     "winner_label": lab, "winner": w, "reason": p["reason"], "model": r.model})
            print(f"[pw] {tag} o{order} -> {w} cum=¥{total:.2f}", flush=True)

    # (4) metrics / symbol gate
    met = {n: sm.metrics(t) for n, t in (("r2", r2), ("luna_r3", luna_r3), ("sol_r3", text))}
    sym = {n: [str(s) for s in safety.detect_prohibited_symbols(t, language="ja")] for n, t in (("r2", r2), ("luna_r3", luna_r3), ("sol_r3", text))}
    m.jwrite(f"{OUT}/metrics.json", {"metrics": met, "symbols": sym})
    m.jwrite(f"{OUT}/usage_log.json", log)
    m.jwrite(f"{OUT}/MANIFEST.json", {"total_cost_jpy": round(total, 3), "effort": eff, "note": note, "model": a.model})
    print("done total ¥", round(total, 3))

main()
