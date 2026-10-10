# -*- coding: utf-8 -*-
"""Trial driver (DEV/Trial only; not Production).
  b3  --arm C1|Aprime --themes a,b --reps 1,2     B3 regeneration (paid). C1 = Production module imported unmodified, Aprime = Trial copy
  e9  --variant Dmin|Dfull                        Writer R0 only (paid). 6 themes x {D, C0}
  frozen                                          record sha256 of frozen inputs (free)
Cost: cl.install(raw log) + run.row_cost_usd. Cap is judged on the sum of cost_ledger_b3sep_01.jsonl."""
import sys, os, time, json, argparse, importlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from b3sep_common_01 import *
import b3sep_build_01 as B

CAP = 60.0
EST_B3 = 0.75
EST_R0 = 1.6
LEDGER = f"{HERE}/cost_ledger_b3sep_01.jsonl"


class Stop(RuntimeError):
    pass


def spent():
    if not os.path.exists(LEDGER):
        return 0.0
    return sum(json.loads(l)["jpy"] for l in open(LEDGER, encoding="utf-8") if l.strip())


def guard(est):
    s = spent()
    if s + est > CAP:
        raise Stop(f"[STOP] cap: spent={s:.2f} + est={est} > {CAP}")
    return s


def cost_of_log(path, start):
    import er052_factlock_astra_e2e_runner_01 as run
    rows = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()][start:]
    jpy = sum(run.row_cost_usd(r) * 160.0 for r in rows)
    return jpy, rows, start + len(rows)


def frozen():
    out = {}
    for th in THEMES:
        ti = theme_inputs(th)
        out[th] = {"ledger_sha256": sha(ti["ledger"]), "topic_sha256": sha(ti["topic"]), "c0_selected_fact_ids": ti["ev"]["selected_fact_ids"]}
    out["_prereg_sha256"] = sha(open(f"{HERE}/PREREGISTRATION_02.md", encoding="utf-8", newline="").read())
    wj(f"{HERE}/frozen_inputs_02.json", out)
    print(json.dumps(out, ensure_ascii=False)[:300])


def cmd_b3(a):
    import er003_v1_en_direct_vfl_01_generate as vfl01
    import er005_cost_logger as cl
    import er019_family_x_storyline_b3_fact_selection_01 as b3prod
    mod = b3prod if a.arm == "C1" else importlib.import_module("b3sep_b3_aprime_01")
    assert vfl01.MODEL == MODEL, vfl01.MODEL
    fz = rj(f"{HERE}/frozen_inputs_02.json")
    tag = f"{a.arm}_{os.getpid()}"
    rawp = f"{HERE}/runs/_raw_usage/{tag}.jsonl"
    os.makedirs(os.path.dirname(rawp), exist_ok=True)
    cl.install(rawp)
    client = vfl01.get_client()
    cur = 0
    for th in a.themes.split(","):
        ti = theme_inputs(th)
        if sha(ti["ledger"]) != fz[th]["ledger_sha256"] or sha(ti["topic"]) != fz[th]["topic_sha256"]:
            raise Stop(f"[STOP] frozen input sha mismatch {th}")
        for rep in [int(x) for x in a.reps.split(",")]:
            od = f"{HERE}/runs/{a.arm}/{th}/rep{rep}"
            if os.path.exists(f"{od}/selection.json"):
                print("skip(existing)", od)
                continue
            s0 = guard(EST_B3)
            sel = mod.run_storyline_b3_selection(client, ti["topic"], ti["ledger"], model=vfl01.MODEL, effort=vfl01.REASONING_EFFORT)
            jpy, rows, cur = cost_of_log(rawp, cur)
            if not str(sel["model"]).startswith(MODEL):
                raise Stop(f"[STOP] model mismatch {sel['model']}")
            p = sel["parsed"]
            wj(f"{od}/selection.json", {"arm": a.arm, "theme": th, "rep": rep, "parsed": p, "model": sel["model"], "response_id": sel["response_id"],
                                        "latency_seconds": sel["latency_seconds"], "attempts": sel["attempts"], "retried": sel["retried"],
                                        "soft_warnings": sel["soft_warnings"], "prompt_shas": sel["prompt_shas"], "ledger_sha256": sha(ti["ledger"]),
                                        "attempts_log": sel["attempts_log"]})
            brief_md = mod.build_selected_brief_markdown(sel)
            wt(f"{od}/selected_brief_raw.md", brief_md)
            rec = {"arm": a.arm, "theme": th, "rep": rep, "kind": "b3", "jpy": round(jpy, 4), "n_api_rows": len(rows), "attempts": sel["attempts"],
                   "latency_seconds": round(sel["latency_seconds"], 1), "model": sel["model"], "ts": time.strftime("%Y-%m-%dT%H:%M:%S")}
            with open(LEDGER, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            print("done", a.arm, th, rep, rec["jpy"], "total", round(s0 + jpy, 2), flush=True)


def cmd_e9(a):
    import er003_v1_en_direct_vfl_01_generate as vfl01
    import er005_cost_logger as cl
    import er019_family_x_ja_writer_o_r1_r2_01 as jaw
    import er052_factlock_writer_trial_01_run as fl
    import er052_factlock_astra_e2e_runner_01 as run
    assert vfl01.MODEL == MODEL
    rawp = f"{HERE}/runs/_raw_usage/e9_{os.getpid()}.jsonl"
    os.makedirs(os.path.dirname(rawp), exist_ok=True)
    cl.install(rawp)
    client = vfl01.get_client()
    cur = 0
    for th in (a.themes.split(",") if a.themes else E9_THEMES):
        ti = theme_inputs(th)
        ev = ti["ev"]
        d = B.assemble_D(ti["ledger"], ev["selected_fact_ids"], ev["selected_storyline"], a.variant)
        arms = {"D": (ev["selected_storyline"], d["brief_md"], d["constraints_text"]),
                "C0": (ev["selected_storyline"], ti["brief"], "")}
        for arm in a.arms.split(","):
            od = f"{HERE}/runs/E9/{th}/{arm}"
            if os.path.exists(f"{od}/r0_meta.json"):
                print("skip(existing)", od)
                continue
            story, brief_md, cons = arms[arm]
            ann = run.dryrun_annotate(brief_md)
            _, facts_ann = run.parse_brief_md(ann)
            news = B.compose_news_field(facts_ann, cons)       # the single composing function
            wt(f"{od}/news_field.txt", news)
            wt(f"{od}/brief_annotated.md", ann)
            s0 = guard(EST_R0)
            saved, calls = fl.apply_factlock_patches(), []
            o_fresh, o_prev = jaw.call_fresh, jaw.call_with_previous_response_id

            def fresh(c, developer, user, effort, stage, _o=o_fresh):
                r = _o(c, developer, user, effort, stage)
                calls.append({"stage": stage, "response_id": r.id, "model": r.model, "text": r.output_text.strip(), "user": user})
                return r

            def stop_r1(*x, **k):
                raise run.StopAfterR0()
            jaw.call_fresh, jaw.call_with_previous_response_id = fresh, stop_r1
            t0 = time.time()
            try:
                try:
                    jaw.run_ja_writer_o_r1_r2(client, story, news, full_ledger_text=None)
                except run.StopAfterR0:
                    pass
            finally:
                jaw.call_fresh, jaw.call_with_previous_response_id = o_fresh, o_prev
                fl.restore_factlock_patches(saved)
            lat = time.time() - t0
            jpy, rows, cur = cost_of_log(rawp, cur)
            if not calls:
                raise Stop("[STOP] no R0 call captured")
            if not str(calls[-1]["model"]).startswith(MODEL):
                raise Stop(f"[STOP] model mismatch {calls[-1]['model']}")
            final = calls[-1]["text"]
            wt(f"{od}/r0_with_tags.md", final)
            wt(f"{od}/r0_prompt.txt", calls[0]["user"])
            wj(f"{od}/r0_meta.json", {"theme": th, "arm": arm, "variant": a.variant,
                                       "calls": [{k: v for k, v in c.items() if k not in ("text", "user")} for c in calls],
                                       "prompt_sha256": sha(calls[0]["user"]), "latency_seconds": round(lat, 1), "n_api_rows": len(rows)})
            rec = {"arm": f"E9_{arm}", "theme": th, "rep": 1, "kind": "r0", "jpy": round(jpy, 4), "n_api_rows": len(rows), "latency_seconds": round(lat, 1),
                   "model": calls[-1]["model"], "ts": time.strftime("%Y-%m-%dT%H:%M:%S")}
            with open(LEDGER, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            print("done E9", arm, th, rec["jpy"], "total", round(s0 + jpy, 2), flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd")
    sp.add_parser("frozen")
    b = sp.add_parser("b3")
    b.add_argument("--arm", required=True, choices=["C1", "Aprime"])
    b.add_argument("--themes", required=True)
    b.add_argument("--reps", default="1,2")
    e = sp.add_parser("e9")
    e.add_argument("--variant", required=True, choices=["Dmin", "Dfull"])
    e.add_argument("--themes", default="")
    e.add_argument("--arms", default="D,C0")
    a = ap.parse_args()
    try:
        {"frozen": lambda a: frozen(), "b3": cmd_b3, "e9": cmd_e9}[a.cmd](a)
    except Stop as ex:
        print(ex)
        sys.exit(46)
