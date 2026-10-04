# -*- coding: utf-8 -*-
# OPEN-233-KPI-RECOVERY-REDESIGN-02 委任_05 作業1: L6とcarry-forwardの順序是正の決定論replay(API call 0、JPY0)。
# rep26/rep27の記録済みrewrite_records(各cycle)について、cycle開始時点の本文(fixture article_text)・記録済みclaim・
# 先行Rewriteの成功置換(記録済みbefore_after)から、是正後の`run_stage3_for_claim_spans`の「Rewriteを試みるか(core呼び出し)/
# carry-forwardで処理するか」を再現する。coreはスタブ(呼ばれた=Rewriteが発生する)。
# 使い方: python er052_output/open233_kpi_recovery_02_offline_01/replay_cf_l6_order_01.py
import glob
import json
import os
import sys

sys.path.insert(0, os.getcwd())
import er052_open233_self_recovery_flow_runner_01 as runner  # noqa: E402

OUT = "er052_output/open233_kpi_recovery_02_offline_01/replay_cf_l6_order_01.json"


def replay_cycle(inst_fixture, cyc, order_fix: bool):
    en0 = inst_fixture["article_text"]
    ja0 = inst_fixture.get("source_article_text")
    blocking = [c for c in cyc["stage2_results"] if c.get("materiality") == "BLOCKING"]
    recs = cyc.get("rewrite_records") or []
    en_now = en0
    units, info = [], {}
    rows = []
    called = {"n": 0}

    def stub_core(*a, **k):
        called["n"] += 1
        return {"handoff": {}, "en_text": a[6], "ja_text": a[7], "guard_ok": False, "method": "STUB_REWRITE_ATTEMPTED",
                "mechanism": "stub", "ladder_level_used": None, "target_not_locatable": False}

    orig_core = runner._run_stage3_spans_core
    orig_fn = runner.l6_carry_forward_precedence
    if not order_fix:
        runner.l6_carry_forward_precedence = lambda *a, **k: None  # 是正前(旧順序)
    runner._run_stage3_spans_core = stub_core
    try:
        for i, rec in enumerate(recs):
            h = rec.get("handoff") or {}
            claim_text = h.get("checker_claim_text")
            cl = next((c for c in blocking if c["claim_text"] == claim_text), None)
            if cl is None:
                rows.append({"i": i, "skip": "claim_not_found"})
                continue
            dev = cl["dev"]
            claim_rec = {"claim_text": claim_text, "dev": dev, "cycle_start_en_text": en0, "cycle_start_ja_text": ja0,
                         "cycle_replaced_units": list(units), "cycle_claim_info": dict(info),
                         "claim_identity": rec["claim_identity"]}
            before = called["n"]
            r = runner.run_stage3_for_claim_spans(None, None, None, [], "x", {"article_text": en0}, en_now, ja0, claim_rec, False)
            attempted = called["n"] > before
            orig_res = (h.get("resolution") or {})
            hh = r.get("handoff") or {}
            rows.append({"i": i, "claim_identity": rec["claim_identity"], "orig_method": rec["method"][:60],
                         "orig_level": orig_res.get("level"), "orig_guard_ok": rec["guard_ok"],
                         "replay_method": r["method"], "replay_rewrite_attempted": attempted,
                         "replay_resolution_status": (hh.get("resolution") or {}).get("status"),
                         "replay_l6_skipped": (hh.get("resolution") or {}).get("l6_skipped", {}).get("skipped_reason"),
                         "replay_l6_rule": (hh.get("resolution") or {}).get("l6_skipped", {}).get("rule")})
            # 次のclaimの状態を更新: 元の記録が成功Rewriteなら置換を反映する。
            if rec.get("guard_ok") and not (r["method"] == "covered_by_earlier_rewrite_in_cycle"):
                for u in runner.collect_replaced_units(rec, rec["claim_identity"]):
                    units.append(u)
                    if u["lang"] == "EN":
                        for b, a in zip(u["before_units"], u["after_units"]):
                            if en_now.count(b) == 1:
                                en_now = en_now.replace(b, a)
            info[rec["claim_identity"]] = {"issue": dev.get("issue") or "", "related_fact_id": dev.get("related_fact_id") or "",
                                           "true_flags": runner._dev_true_flags(dev)}
    finally:
        runner._run_stage3_spans_core = orig_core
        runner.l6_carry_forward_precedence = orig_fn
    return rows


def main():
    runner.apply_kpi_trial_switches()
    insts = {i["instance_id"]: i for i in runner.build_target_instances()}
    out = {"cases": []}
    for rep in (26, 27):
        for f in sorted(glob.glob(f"er052_output/open233_self_recovery_flow_runner_01_rep{rep}/instances_s*/*.json")):
            d = json.load(open(f, encoding="utf-8"))
            iid = d["instance_id"]
            if iid not in insts:
                continue
            fx = insts[iid]["fixture"]
            for cyc in d["cycles"]:
                if not any("L6" in str((r.get("handoff") or {}).get("resolution", {}).get("level")) or
                           "L6" in str((r.get("handoff") or {}).get("resolution", {}).get("cycle_start_level"))
                           for r in (cyc.get("rewrite_records") or [])):
                    continue
                new = replay_cycle(fx, cyc, True)
                old = replay_cycle(fx, cyc, False)
                out["cases"].append({"rep": rep, "file": f.replace("\\", "/").split("rep")[-1], "cycle": cyc["cycle"],
                                     "old_order": old, "new_order": new})
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for c in out["cases"]:
        print("==", c["rep"], c["file"], "cycle", c["cycle"])
        for o, n in zip(c["old_order"], c["new_order"]):
            tag = "CHANGED" if (o.get("replay_method") != n.get("replay_method")) else "same"
            print(f"  rec{n.get('i')} {n.get('claim_identity')} orig={n.get('orig_method')} | old->{o.get('replay_method')} "
                  f"rewrite={o.get('replay_rewrite_attempted')} | new->{n.get('replay_method')} rewrite={n.get('replay_rewrite_attempted')} "
                  f"skip={n.get('replay_l6_skipped')}/{n.get('replay_l6_rule')} [{tag}]")


if __name__ == "__main__":
    main()
