# -*- coding: utf-8 -*-
"""FACTLOCK-WRITER-REDESIGN-TRIAL-01 delegation 15 ASTRA-REVISE-MATRIX-01 (Trial/DEV, not a Production path).
Fact Lock v1 meta b2 R0 -> gpt-6-astra R1->R2->R3, two series (A = user prompt only / B = expert-editor developer message), then evaluation.
Existing harness (er052_step2_astra_r3_01_run / run_r3_minimal / Production modules) is import-only; never edited.
Usage: --phase gen --series A|B | --phase eval ; without --yes-run-paid it is a dry run."""
import argparse, hashlib, json, os, sys, threading, time
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, ROOT)
import er052_step2_astra_r3_01_run as H   # chdir(ROOT) done at import; main() not called
m = H.m

FL = "er052_output/factlock_writer_trial_01"
BASE = f"{FL}/astra_revise_matrix_01"
R0_PATH = f"{FL}/step2_astra_r3_01/inputs/FL_R0/meta/b2/source.md"
RUN_DIR = f"{FL}/runs/meta/control/b2__factlock__r1"     # ledger / d_src
LEDGER = f"{RUN_DIR}/research_ledger/verified_fact_ledger.txt"
BRIEF = f"{FL}/briefs/meta/b2/selected_brief_factlock.md"
MODEL = "gpt-6-astra"
EFFORT = "high"          # same as Step 1 (conditions.json reasoning / run_step1.py)
PRICE_ASTRA = H.PRICE_ASTRA
USER_TMPL = "以下の記事:\n\n{body}\n\n事実は変えずにエンターテイメント性をもっと上げた記事にReviseください。長さは800〜1000字程度でお願いします。"
_L = threading.Lock()


def f2_developer():
    return json.load(open(f"{FL}/step1_chat_repro_01/conditions.json", encoding="utf-8"))["conditions"]["F2"]["developer"]


DEV = {"A": None, "B": f2_developer()}
LOG = f"{BASE}/usage_log.jsonl"


def total_cost():
    if not os.path.exists(LOG):
        return 0.0
    return sum(json.loads(l).get("cost_jpy", 0) for l in open(LOG, encoding="utf-8") if l.strip())


def rec(r):
    with _L:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def gen_series(client, series, budget):
    prev_path = R0_PATH
    for n in (1, 2, 3):
        out = f"{BASE}/runs/{series}/r{n}.md"
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
        except Exception as e:  # noqa: BLE001  no retry for generation; record error only
            m.jwrite(f"{BASE}/runs/{series}/r{n}_ERROR.json", {"error": repr(e)[:800]})
            print("[gen-ERR]", series, n, repr(e)[:200], flush=True)
            return False
        sec = time.time() - t0
        us = m.usage_of(resp)
        c = H.jpy(PRICE_ASTRA, us.get("input_tokens") or 0, us.get("cached_input_tokens") or 0, us.get("output_tokens") or 0)
        raw = (resp.output_text or "").strip()
        rec({"stage": "gen", "series": series, "round": n, "model": resp.model, "sec": round(sec, 1), "cost_jpy": round(c, 4),
             "price_estimated": True, **us})
        m.write(out, raw)
        m.write(f"{BASE}/runs/{series}/r{n}.p1.md", H.strip_markdown(raw))
        m.jwrite(f"{BASE}/runs/{series}/r{n}.response.json", {
            "series": series, "round": n, "requested_model": MODEL, "model": resp.model, "reasoning": {"effort": EFFORT},
            "developer_message": DEV[series], "user_message_sha256": hashlib.sha256(user.encode("utf-8")).hexdigest(),
            "input_source": prev_path, "input_chars": len(body), "output_chars": len(raw), "response_id": resp.id,
            "sec": round(sec, 1), "usage": us, "cost_jpy_estimated": round(c, 4),
            "price_note": "astra price unregistered; estimate = gpt-6-sol (2.00/0.20/10.00 USD/1M) x2.5, USD/JPY=160",
            "previous_response_id_used": False, "status": getattr(resp, "status", None)})
        print(f"[gen] {series} r{n} {sec:.0f}s cost={c:.2f} chars={len(raw)} cum={total_cost():.1f}", flush=True)
        prev_path = out
    return True


def targets():
    t = [("R0", R0_PATH)]
    for s in ("A", "B"):
        for n in (1, 2, 3):
            t.append((f"{s}_r{n}", f"{BASE}/runs/{s}/r{n}.p1.md"))
    return t


def do_fc(client, vfl01, tid, path, budget):
    out = f"{BASE}/eval/fc/{tid}.json"
    if os.path.exists(out) or not os.path.exists(path) or total_cost() > budget:
        return
    t0 = time.time()
    res = m.retry(lambda: vfl01.run_deviation_check(client, m.read(LEDGER), m.read(path).strip(), model=H.MODEL_JUDGE,
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
    facts = fl.parse_annotated_facts(m.read(BRIEF))
    r = fl.untagged_check(client, H.MODEL_JUDGE, f"matrix_{tid}", fl.split_sentences(m.read(path)), facts)
    rec({"stage": "ii", "id": tid, "sec": round(time.time() - t0, 1), "cost_jpy": 0.2, "cost_is_estimate": True})
    m.jwrite(out, r)
    print(f"[ii] {tid} new={r['counts'].get('new_specific_claim')}", flush=True)


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", default="gen")
    ap.add_argument("--series", default="A")
    ap.add_argument("--budget-jpy", type=float, default=60)
    ap.add_argument("--yes-run-paid", action="store_true")
    a = ap.parse_args()
    r0 = m.read(R0_PATH).strip()
    if not a.yes_run_paid:
        print("DRY RUN. model", MODEL, "effort", EFFORT, "R0 chars", len(r0))
        for s in ("A", "B"):
            print(s, "developer:", DEV[s])
        print("user:", repr(USER_TMPL.format(body=r0[:30] + "...")))
        print("budget", a.budget_jpy, "log cost so far", total_cost())
        return 0
    import er006_model_routing_contract_01 as routing
    import er003_v1_en_direct_vfl_01_generate as vfl01
    import er052_factlock_writer_trial_01_run as fl
    client = vfl01.get_client()
    if a.phase == "gen":
        routing.require_model_or_override("B1_WRITER", MODEL, override_reason="FACTLOCK ASTRA-REVISE-MATRIX-01 (Trial; price unregistered, estimated)")
        return 0 if gen_series(client, a.series, a.budget_jpy) else 1
    if a.phase == "eval":
        routing.require_model_or_override("WRITER_FACT_CHECK", H.MODEL_JUDGE, override_reason="FACTLOCK ASTRA-REVISE-MATRIX-01")
        t0 = time.time()
        with ThreadPoolExecutor(max_workers=4) as ex:
            jobs = targets()
            list(ex.map(lambda j: do_ii(client, fl, j[0], j[1], a.budget_jpy), jobs))
            list(ex.map(lambda j: do_fc(client, vfl01, j[0], j[1], a.budget_jpy), jobs))
        print("eval done sec", round(time.time() - t0, 1), "cum", round(total_cost(), 2))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
