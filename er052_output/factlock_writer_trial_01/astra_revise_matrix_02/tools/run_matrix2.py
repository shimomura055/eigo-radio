# -*- coding: utf-8 -*-
"""FACTLOCK-WRITER-REDESIGN-TRIAL-01 delegation 16 ASTRA-REVISE-MATRIX-02 (Trial/DEV, not a Production path).
hormuz / small_bag: Fact Lock R0 -> gpt-6-astra R1 -> R2, two series (A = user prompt only [X] / B = expert-editor developer [Y]). Then evaluation.
Reuses matrix_01 conventions (read-only import of er052_step2_astra_r3_01_run). Usage: --phase gen --articles hormuz[,small_bag] | --phase eval ; dry run without --yes-run-paid."""
import argparse, hashlib, json, os, sys, threading, time
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, ROOT)
import er052_step2_astra_r3_01_run as H   # chdir(ROOT) at import
m = H.m

FL = "er052_output/factlock_writer_trial_01"
BASE = f"{FL}/astra_revise_matrix_02"
E2E = "er052_output/gpt6_wiring_e2e_01/run_02"
HZ = f"{FL}/runs/hormuz/control/b2__factlock__r1"
ART = {
    "hormuz": {"r0": f"{BASE}/inputs/hormuz/R0.md", "d_src": HZ, "ledger": f"{HZ}/research_ledger/verified_fact_ledger.txt",
               "brief": f"{FL}/briefs/hormuz/b2/selected_brief_factlock.md"},
    "small_bag": {"r0": f"{BASE}/inputs/small_bag/R0.md", "d_src": E2E, "ledger": f"{E2E}/research_ledger/verified_fact_ledger.txt",
                  "brief": f"{BASE}/inputs/small_bag/selected_brief_factlock.md"},
}
MODEL = "gpt-6-astra"
EFFORT = "high"
PRICE_ASTRA = H.PRICE_ASTRA
USER_TMPL = "以下の記事:\n\n{body}\n\n事実は変えずにエンターテイメント性をもっと上げた記事にReviseください。長さは800〜1000字程度でお願いします。"
_L = threading.Lock()
LOG = f"{BASE}/usage_log.jsonl"
R0LOG = f"{BASE}/r0_small_bag/raw_usage_log.jsonl"
ROUNDS = (1, 2)


def f2_developer():
    return json.load(open(f"{FL}/step1_chat_repro_01/conditions.json", encoding="utf-8"))["conditions"]["F2"]["developer"]


DEV = {"A": None, "B": f2_developer()}


def r0_cost():
    if not os.path.exists(R0LOG):
        return 0.0
    t = 0.0
    for l in open(R0LOG, encoding="utf-8"):
        if l.strip():
            r = json.loads(l)
            t += H.jpy(H.PRICE_LUNA, r.get("input_tokens") or 0, r.get("cached_input_tokens") or 0, r.get("output_tokens") or 0)
    return t


def total_cost():
    t = r0_cost()
    if os.path.exists(LOG):
        t += sum(json.loads(l).get("cost_jpy", 0) for l in open(LOG, encoding="utf-8") if l.strip())
    return t


def rec(r):
    with _L:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def gen_series(client, art, series, budget):
    prev_path = ART[art]["r0"]
    for n in ROUNDS:
        out = f"{BASE}/runs/{art}/{series}/r{n}.md"
        if os.path.exists(out):
            prev_path = out
            continue
        if total_cost() > budget:
            print(f"[STOP] cost {total_cost():.1f} > budget {budget}", flush=True)
            return False
        body = m.read(prev_path).strip()
        user = USER_TMPL.format(body=body)
        msgs = ([{"role": "developer", "content": DEV[series]}] if DEV[series] else []) + [{"role": "user", "content": user}]
        t0 = time.time()
        try:
            resp = client.responses.create(model=MODEL, reasoning={"effort": EFFORT}, input=msgs)
        except Exception as e:  # noqa: BLE001  no retry for generation
            m.jwrite(f"{BASE}/runs/{art}/{series}/r{n}_ERROR.json", {"error": repr(e)[:800]})
            print("[gen-ERR]", art, series, n, repr(e)[:200], flush=True)
            return False
        sec = time.time() - t0
        us = m.usage_of(resp)
        c = H.jpy(PRICE_ASTRA, us.get("input_tokens") or 0, us.get("cached_input_tokens") or 0, us.get("output_tokens") or 0)
        raw = (resp.output_text or "").strip()
        rec({"stage": "gen", "article": art, "series": series, "round": n, "model": resp.model, "sec": round(sec, 1), "cost_jpy": round(c, 4),
             "price_estimated": True, **us})
        m.write(out, raw)
        m.write(f"{BASE}/runs/{art}/{series}/r{n}.p1.md", H.strip_markdown(raw))
        m.jwrite(f"{BASE}/runs/{art}/{series}/r{n}.response.json", {
            "article": art, "series": series, "round": n, "requested_model": MODEL, "model": resp.model, "reasoning": {"effort": EFFORT},
            "developer_message": DEV[series], "user_message_sha256": hashlib.sha256(user.encode("utf-8")).hexdigest(),
            "input_source": prev_path, "input_chars": len(body), "output_chars": len(raw), "response_id": resp.id,
            "sec": round(sec, 1), "usage": us, "cost_jpy_estimated": round(c, 4),
            "price_note": "astra price unregistered; estimate = gpt-6-sol (2.00/0.20/10.00 USD/1M) x2.5, USD/JPY=160",
            "previous_response_id_used": False, "status": getattr(resp, "status", None)})
        print(f"[gen] {art} {series} r{n} {sec:.0f}s cost={c:.2f} chars={len(raw)} cum={total_cost():.1f}", flush=True)
        prev_path = out
    return True


def targets(art):
    t = [(f"{art}_R0", ART[art]["r0"])]
    for s in ("A", "B"):
        for n in ROUNDS:
            t.append((f"{art}_{s}_r{n}", f"{BASE}/runs/{art}/{s}/r{n}.p1.md"))
    return t


def art_of(tid):
    return "small_bag" if tid.startswith("small_bag") else "hormuz"


def do_fc(client, vfl01, tid, path, budget):
    out = f"{BASE}/eval/fc/{tid}.json"
    if os.path.exists(out) or not os.path.exists(path) or total_cost() > budget:
        return
    led = m.read(ART[art_of(tid)]["ledger"])
    t0 = time.time()
    res = m.retry(lambda: vfl01.run_deviation_check(client, led, m.read(path).strip(), model=H.MODEL_JUDGE,
                                                    hook_aware=False, include_related_fact_id=True), 2)
    u = res["usage"]
    c = H.jpy(H.PRICE_LUNA, u.get("input_tokens") or 0, u.get("cached_input_tokens") or 0, u.get("output_tokens") or 0)
    rec({"stage": "fc", "id": tid, "model": res["model"], "sec": round(time.time() - t0, 1), "cost_jpy": round(c, 4), **u})
    m.jwrite(out, {"parsed": res["parsed"], "model": res["model"], "response_id": res["response_id"]})
    print(f"[fc] {tid} {res['parsed'].get('overall_status')}", flush=True)


def do_ii(client, fl, tid, path, budget):
    out = f"{BASE}/eval/ii/{tid}.json"
    if os.path.exists(out) or not os.path.exists(path) or total_cost() > budget:
        return
    t0 = time.time()
    facts = fl.parse_annotated_facts(m.read(ART[art_of(tid)]["brief"]))
    r = fl.untagged_check(client, H.MODEL_JUDGE, f"matrix2_{tid}", fl.split_sentences(m.read(path)), facts)
    rec({"stage": "ii", "id": tid, "sec": round(time.time() - t0, 1), "cost_jpy": 0.2, "cost_is_estimate": True})
    m.jwrite(out, r)
    print(f"[ii] {tid} new={r['counts'].get('new_specific_claim')}", flush=True)


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", default="gen")
    ap.add_argument("--articles", default="hormuz,small_bag")
    ap.add_argument("--budget-jpy", type=float, default=80)
    ap.add_argument("--yes-run-paid", action="store_true")
    a = ap.parse_args()
    arts = a.articles.split(",")
    if not a.yes_run_paid:
        print("DRY RUN. model", MODEL, "effort", EFFORT)
        for x in arts:
            p = ART[x]["r0"]
            print(x, "R0", p, "exists", os.path.exists(p), "chars", len(m.read(p)) if os.path.exists(p) else None)
        for s in ("A", "B"):
            print(s, "developer:", DEV[s])
        print("user:", repr(USER_TMPL.format(body="...")))
        print("budget", a.budget_jpy, "cost so far", total_cost())
        return 0
    import er006_model_routing_contract_01 as routing
    import er003_v1_en_direct_vfl_01_generate as vfl01
    import er052_factlock_writer_trial_01_run as fl
    client = vfl01.get_client()
    if a.phase == "gen":
        routing.require_model_or_override("B1_WRITER", MODEL, override_reason="FACTLOCK ASTRA-REVISE-MATRIX-02 (Trial; price unregistered, estimated)")
        jobs = [(x, s) for x in arts for s in ("A", "B")]
        with ThreadPoolExecutor(max_workers=4) as ex:
            res = list(ex.map(lambda j: gen_series(client, j[0], j[1], a.budget_jpy), jobs))
        return 0 if all(res) else 1
    if a.phase == "eval":
        routing.require_model_or_override("WRITER_FACT_CHECK", H.MODEL_JUDGE, override_reason="FACTLOCK ASTRA-REVISE-MATRIX-02")
        t0 = time.time()
        with ThreadPoolExecutor(max_workers=4) as ex:
            jobs = [j for x in arts for j in targets(x)]
            list(ex.map(lambda j: do_ii(client, fl, j[0], j[1], a.budget_jpy), jobs))
            list(ex.map(lambda j: do_fc(client, vfl01, j[0], j[1], a.budget_jpy), jobs))
        print("eval done sec", round(time.time() - t0, 1), "cum", round(total_cost(), 2))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
