# -*- coding: utf-8 -*-
"""ASTRA-REVISE-MATRIX-02: small_bag の Fact Lock v1 R0 を新規生成(Trial/DEV)。
Production関数 jaw.run_ja_writer_o_r1_r2 の Original段(R0プロンプト+Fact Lock R0ブロック、JA Fact Check(Full Ledger)、MAJOR->must-fix 1回->STOP、記号Gate)を
そのまま通し、R1呼び出しの直前で BaseException により打ち切る(R1/R2のAPIは呼ばない)。ファイルは編集しない(実行時patchのみ)。"""
import hashlib, json, os, sys, time
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
os.chdir(ROOT); sys.path.insert(0, ROOT)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
FL = "er052_output/factlock_writer_trial_01"
B2 = f"{FL}/astra_revise_matrix_02"
OUT = f"{B2}/r0_small_bag"
E2E = "er052_output/gpt6_wiring_e2e_01/run_02"
BRIEF = f"{B2}/inputs/small_bag/selected_brief_factlock.md"
CORE = f"{B2}/inputs/small_bag/core_numbers.json"
LEDGER = f"{E2E}/research_ledger/verified_fact_ledger.txt"
PRICE_LUNA = (0.10, 0.01, 0.50)


class StopAfterR0(BaseException):
    pass


def jw(p, o):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write(json.dumps(o, ensure_ascii=False, indent=1))


def main():
    import er052_factlock_writer_trial_01_run as fl
    import er052_all6_writer_trial_01_run as all6
    import er052_open233_polysemy_nb_dev_01 as dev
    import er019_family_x_ja_writer_o_r1_r2_01 as jaw
    import er003_v1_en_direct_vfl_01_generate as vfl01
    import er005_cost_logger as cl
    if os.path.exists(f"{OUT}/original_with_tags.md"):
        print("R0 already exists"); return 0
    os.makedirs(OUT, exist_ok=True)
    brief_text = open(BRIEF, encoding="utf-8").read()
    storyline, facts = dev.parse_brief_md(brief_text)
    ledger = open(LEDGER, encoding="utf-8").read()
    cl.install(f"{OUT}/raw_usage_log.jsonl")
    saved_all6 = all6.apply_all6_patches()
    saved_fl = fl.apply_factlock_patches()
    calls, fcs = [], []
    orig_fresh = jaw.call_fresh
    orig_dev = vfl01.run_deviation_check

    def fresh(client, developer, user, effort, stage):
        r = orig_fresh(client, developer, user, effort, stage)
        calls.append({"stage": stage, "response_id": r.id, "model": r.model, "text": r.output_text.strip(), "prompt_sha": hashlib.sha256(user.encode()).hexdigest()})
        return r

    def devc(*a, **k):
        r = orig_dev(*a, **k)
        fcs.append(r)
        return r

    def stop_r1(*a, **k):
        raise StopAfterR0()

    jaw.call_fresh = fresh
    vfl01.run_deviation_check = devc
    jaw.call_with_previous_response_id = stop_r1
    t0 = time.time()
    status, err = "completed_R0_only", None
    try:
        client = vfl01.get_client()
        try:
            jaw.run_ja_writer_o_r1_r2(client, storyline, facts, full_ledger_text=ledger)
        except StopAfterR0:
            pass
        except jaw.JAFactCheckStopError as e:
            status, err = "STOP_JA_FACT_CHECK", str(e)
            jw(f"{OUT}/stop_detail.json", {"stage": e.stage, "rejected_text": e.rejected_text, "must_fix_used": e.must_fix_used,
                                             "checks": [vfl01.deviation_audit_record(c) for c in e.checks]})
    finally:
        jaw.call_fresh = orig_fresh
        vfl01.run_deviation_check = orig_dev
        fl.restore_factlock_patches(saved_fl)
        all6.restore_patches(saved_all6)
    sec = round(time.time() - t0, 1)
    fc_records = [{"parsed": r["parsed"], "model": r.get("model")} for r in fcs]
    jw(f"{OUT}/ja_fact_checks.json", fc_records)
    jw(f"{OUT}/writer_calls.json", [{k: v for k, v in c.items() if k != "text"} for c in calls])
    summary = {"status": status, "error": err, "sec": sec, "writer_calls": [c["stage"] for c in calls],
               "fc_overall": [r["parsed"].get("overall_status") for r in fcs],
               "fc_deviation_counts": [[sum(1 for d in r["parsed"].get("deviations", []) if d["severity"] == s) for s in ("MAJOR", "MINOR")] for r in fcs],
               "must_fix_applied": any(c["stage"].startswith("ja_original_must_fix") for c in calls),
               "symbol_must_fix_applied": any("symbol" in c["stage"] for c in calls),
               "brief": BRIEF, "brief_sha": hashlib.sha256(open(BRIEF, "rb").read()).hexdigest(),
               "source_b3_brief": f"{E2E}/storyline_b3/selected_brief.md", "ledger": LEDGER,
               "ledger_sha": hashlib.sha256(open(LEDGER, "rb").read()).hexdigest()}
    cost = 0.0
    for l in open(f"{OUT}/raw_usage_log.jsonl", encoding="utf-8"):
        if not l.strip():
            continue
        r = json.loads(l)
        i, c, o = r.get("input_tokens") or 0, r.get("cached_input_tokens") or 0, r.get("output_tokens") or 0
        cost += ((i - c) * PRICE_LUNA[0] + c * PRICE_LUNA[1] + o * PRICE_LUNA[2]) / 1e6 * 160
    summary["cost_jpy_luna_registered_price"] = round(cost, 4)
    if status == "completed_R0_only":
        final = calls[-1]["text"]
        open(f"{OUT}/original_with_tags.md", "w", encoding="utf-8", newline="").write(final)
        stripped = fl.strip_tags(final)
        open(f"{OUT}/original.md", "w", encoding="utf-8", newline="").write(stripped)
        r0 = stripped.strip() + "\n"
        os.makedirs(f"{B2}/inputs/small_bag", exist_ok=True)
        open(f"{B2}/inputs/small_bag/R0.md", "w", encoding="utf-8", newline="").write(r0)
        summary["R0_sha"] = hashlib.sha256(r0.encode()).hexdigest()
        # タグ照合(測定のみ、Fact Lock v1と同一 check_stage)
        fcts = fl.parse_annotated_facts(brief_text)
        core = fl.load_core_numbers(CORE)
        rec = fl.check_stage(vfl01.get_client(), all6.resolve_all6_model("WRITER_FACT_CHECK"), "r0", final, fcts, core, use_llm=True)
        jw(f"{OUT}/factlock_check_r0.json", rec)
        summary["tag_check"] = {"tagged": rec["tagged_sentences"], "total": rec["sentences_total"], "marks_echoed": rec["marks_echoed"],
                                "iii_numbers": rec["iii_numbers"]}
    jw(f"{OUT}/R0_RUN.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    return 0 if status == "completed_R0_only" else 3


if __name__ == "__main__":
    if "--yes-run-paid" not in sys.argv:
        print("DRY RUN (add --yes-run-paid)"); sys.exit(0)
    sys.exit(main())
