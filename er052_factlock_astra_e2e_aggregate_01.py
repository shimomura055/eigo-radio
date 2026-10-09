# -*- coding: utf-8 -*-
"""FACTLOCK-ASTRA-E2E-TRIAL-01 委任_05 (i): 集計script(API 0、読取専用)。

er052_factlock_astra_e2e_runner_01.py が作った <root>/<theme>/{old,new}/ を読み、DESIGN_E2E_01.md 1-2節の行立て
(REPORT §81と同じ A〜E に、F〜N の追加指標)で 新腕/旧腕/差 を集計する。分母は予定run数(各腕 2 x テーマ数)に固定し、
STOP(JA STOP・影STOP・EN STOP)は独立カテゴリとして分母に残す。盲検ラベルが必要な欄(真に重大/不要など)は None(要ラベル)。
使い方: .venv/Scripts/python.exe -X utf8 er052_factlock_astra_e2e_aggregate_01.py --root <root> [--out-dir <dir>]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

import er052_factlock_astra_e2e_runner_01 as R

LEVELS = (("advanced", "b1b", "adv"), ("standard", "a2", "std"))


def _safe(p, default=None):
    try:
        return R.rj(p) if os.path.exists(p) else default
    except (OSError, ValueError):
        return default


def ja_stats(arm_dir: str) -> dict:
    p = f"{arm_dir}/ja_writer/revision2.md"
    if not os.path.exists(p):
        return {}
    t = R.rdt(p)
    body = [l for l in t.split("\n") if l.strip()][1:]
    flat = "".join(body).replace(" ", "")
    d = {"chars": len(flat), "paragraphs": len(body), "questions": flat.count("？") + flat.count("?"),
         "r2_echo": R.detect_r0_echo(t)}
    o = f"{arm_dir}/ja_writer/original.md"
    if os.path.exists(o):
        d["r0_echo"] = R.detect_r0_echo(R.rdt(o))
    try:
        import er003_audio_tts_asr_safety as safety
        d["symbol_gate_findings"] = len(safety.detect_prohibited_symbols(t, "ja"))
    except Exception:  # noqa: BLE001  集計はsafety importに依存させない
        d["symbol_gate_findings"] = None
    return d


def ja_fc(arm: str, arm_dir: str) -> dict:
    if arm == "new":
        r2 = _safe(f"{arm_dir}/new_writer/r2_fc.json") or {}
        return {"source": "new_r2_fc", "n_major": r2.get("n_major"), "n_minor": r2.get("n_minor")}
    p = _safe(f"{arm_dir}/ja_writer/audit/deviation_checks/ja_r2_attempt1.json") or {}
    devs = (p.get("parsed") or {}).get("deviations", [])
    return {"source": "ja_r2_attempt1", "n_major": sum(1 for d in devs if d.get("severity") == "MAJOR"),
            "n_minor": sum(1 for d in devs if d.get("severity") == "MINOR")}


def en_dev(arm_dir: str, dname: str, key: str) -> dict:
    a1 = _safe(f"{arm_dir}/{dname}/audit/deviation_checks/{key}_attempt1.json")
    if a1 is None:
        return {}
    devs = (a1.get("parsed") or {}).get("deviations", [])
    ma = [d for d in devs if d.get("severity") == "MAJOR"]
    return {"n_major": len(ma), "n_translation": sum(1 for d in ma if d.get("origin") == "translation"),
            "n_ja_source": sum(1 for d in ma if d.get("origin") == "ja_source"), "n_minor": sum(1 for d in devs if d.get("severity") == "MINOR"),
            "m1_fired": os.path.exists(f"{arm_dir}/{dname}/audit/deviation_checks/{key}_attempt2.json") and arm_dir.endswith("new")}


def arm_record(root: str, theme: str, arm: str) -> dict:
    ad = f"{root}/{theme}/{arm}"
    st = R.ArmState(ad)
    evs = st.events()
    rec = {"theme": theme, "arm": arm, "stages": {}, "ja": ja_stats(ad), "ja_fc": ja_fc(arm, ad)}
    for e in evs:
        if e["ev"] in ("stage_done", "stage_stop", "stage_failed"):
            rec["stages"][e["stage"]] = e["ev"][6:]
        elif e["ev"] == "reset":
            for s in e["stages"]:
                rec["stages"].pop(s, None)
    rec["ja_recheck_events"] = R.read_jsonl(f"{ad}/telemetry/ja_recheck_events.jsonl")
    rec["first_ja_recheck"] = bool(rec["ja_recheck_events"])
    rec["b1_recovery"] = st.count("b1_recovery")
    rec["b1_denied"] = [e for e in evs if e["ev"] == "b1_denied"]
    rec["shadow_stop_initial"] = any(e["ev"] == "shadow_stop" and not e.get("final") for e in evs)
    rec["shadow_stop_final"] = any(e["ev"] == "shadow_stop" and e.get("final") for e in evs)
    ja_stage = "old_ja" if arm == "old" else "new_r0"
    rec["ja_stop"] = rec["stages"].get(ja_stage) == "stop"
    rec["en"] = {}
    rec["checker"] = {}
    for lvl, dname, short in LEVELS:
        stage = f"new_en_{short}" if arm == "new" else f"old_{short}"
        rec["en"][lvl] = {"status": rec["stages"].get(stage), "article": R.stage_ok(f"{ad}/{dname}/article.md"), **en_dev(ad, dname, lvl)}
        cj = _safe(f"{ad}/checker/{lvl}.json")
        if cj:
            cyc = cj.get("cycles") or []
            cov = (cj.get("stage1_coverage") or {})
            cf = cov.get("candidate_filter") or {}
            rec["checker"][lvl] = {
                "final_state": cj.get("final_state"), "aborted": bool(cj.get("aborted")), "human_review": cj.get("final_state") == "STAGE4_ESCALATION",
                "rewrite": any(c.get("rewrite_records") for c in cyc), "cost_jpy": cj.get("total_cost_jpy"),
                "n_union_candidates": cov.get("n_union_candidates"), "n_excluded_claims": cf.get("n_excluded_claims"),
                "n_protected_keys": cf.get("n_protected_keys"), "stage2_cycle1": len((cyc[0].get("stage2_results") or [])) if cyc else None,
                "waste_flags": cj.get("waste_flags"), "provenance_violations": cj.get("provenance_violations"), "stub": cj.get("stub", False)}
    ii = _safe(f"{ad}/telemetry/ii.json") or {}
    rec["ii_new_specific_final"] = (ii.get("final") or {}).get("new_specific_claim")
    rec["ii_delta_vs_r0"] = ii.get("delta_new_specific_final_minus_r0")
    sh = _safe(f"{ad}/telemetry/shadow.json") or {}
    rec["shadow"] = {k: sh.get(k) for k in ("m1a", "m1b", "standard_attempt1_major")}
    g3 = R.read_jsonl(f"{ad}/telemetry/g3_telemetry.jsonl")      # 観測のみ(API 0): EN translation起源MINOR / 再分類で除外されたフラグ付き候補
    rec["g3"] = {"translation_minor": sum(1 for x in g3 if x.get("kind") == "en_deviation_translation_minor"),
                 "reclassify_excluded_flagged": sum(1 for x in g3 if x.get("kind") == "reclassify_excluded_flagged"),
                 "m3_would_protect_changed_actor": sum(1 for x in g3 if x.get("kind") == "reclassify_excluded_flagged" and "changed_actor" in (x.get("flags") or []))}
    return rec


def cost_by_arm(root: str) -> dict:
    out = {}
    for fn in sorted(os.listdir(root)) if os.path.isdir(root) else []:
        if fn.startswith("ledger_costs_worker"):
            for e in R.read_jsonl(f"{root}/{fn}"):
                if e["kind"] == "settle":
                    d = out.setdefault(e["arm"], {"raw_jpy": 0.0, "guard_jpy": 0.0, "by_stage": {}})
                    d["raw_jpy"] += e["jpy_raw"]
                    d["guard_jpy"] += e["jpy_guard"]
                    d["by_stage"][e["stage"]] = round(d["by_stage"].get(e["stage"], 0.0) + e["jpy_raw"], 4)
    for d in out.values():
        d["raw_jpy"], d["guard_jpy"] = round(d["raw_jpy"], 4), round(d["guard_jpy"], 4)
    return out


def human_intervention(recs: list) -> dict:
    """人手介入必要率(定義案、DESIGN 1-3): 記事単位STOP(JA STOP・影STOP)=2 run、EN STOP=該当レベル1 run、Human Review=run単位。同一runは最大1回。"""
    counted, parts = set(), {"ja_stop": 0, "shadow_stop": 0, "en_stop": 0, "human_review": 0}
    for r in recs:
        for kind, flag in (("ja_stop", r["ja_stop"]), ("shadow_stop", r["shadow_stop_final"])):
            if flag:
                for lvl, _, _ in LEVELS:
                    if (r["theme"], lvl) not in counted:
                        counted.add((r["theme"], lvl))
                        parts[kind] += 1
        for lvl, _, _ in LEVELS:
            if r["en"][lvl]["status"] == "stop" and (r["theme"], lvl) not in counted:
                counted.add((r["theme"], lvl))
                parts["en_stop"] += 1
        for lvl, c in r["checker"].items():
            if c["human_review"] and (r["theme"], lvl) not in counted:
                counted.add((r["theme"], lvl))
                parts["human_review"] += 1
    return parts


def aggregate(root: str, only_themes=None) -> dict:
    themes = sorted(d for d in os.listdir(root) if os.path.isdir(f"{root}/{d}/shared")) if os.path.isdir(root) else []
    if only_themes is not None:      # 委任_13追加: 層別集計(旧4/新5)用。費用(cost)は全体のまま
        themes = [t for t in themes if t in only_themes]
    out = {"root": root, "themes": themes, "planned_runs_per_arm": 2 * len(themes), "arms": {}, "per_theme": [], "cost": cost_by_arm(root),
           "b1_global": R.read_jsonl(f"{root}/b1_counter.jsonl"), "note": "分母は予定run数(各腕2 x テーマ数)。STOPは独立カテゴリ。None=要ラベル/未計測"}
    for arm in ("new", "old"):
        recs = [arm_record(root, t, arm) for t in themes if os.path.isdir(f"{root}/{t}/{arm}")]
        n, planned = len(recs), 2 * len(recs)
        runs = [(r["theme"], lvl, c) for r in recs for lvl, c in r["checker"].items()]
        hi = human_intervention(recs)
        out["arms"][arm] = {
            "n_articles": n, "planned_runs": planned, "checker_runs_done": len(runs),
            "A_checker_candidates": {"union_candidates_total": sum((c["n_union_candidates"] or 0) for _, _, c in runs),
                                     "excluded_claims_total": sum((c["n_excluded_claims"] or 0) for _, _, c in runs),
                                     "protected_keys_total": sum((c["n_protected_keys"] or 0) for _, _, c in runs),
                                     "true_problem_Y_N": None},
            "B_stage2": {"mean_cycle1_candidates": (sum((c["stage2_cycle1"] or 0) for _, _, c in runs) / len(runs)) if runs else None,
                         "truly_serious_labels": None},
            "C_rewrite": {"rewrite_runs": sum(1 for _, _, c in runs if c["rewrite"]), "rate_over_planned": (sum(1 for _, _, c in runs if c["rewrite"]) / planned) if planned else None},
            "D_human_review": {"runs": sum(1 for _, _, c in runs if c["human_review"]), "rate_over_planned": (sum(1 for _, _, c in runs if c["human_review"]) / planned) if planned else None},
            "E_cost": out["cost"].get(arm), "E_serious_miss": None,
            "F_final_serious_minor": None,
            "G_ja": {"fc_major_total": sum((r["ja_fc"].get("n_major") or 0) for r in recs), "fc_minor_total": sum((r["ja_fc"].get("n_minor") or 0) for r in recs),
                     "mean_chars": (sum(r["ja"].get("chars", 0) for r in recs) / n) if n else None, "symbol_gate_findings_total": sum((r["ja"].get("symbol_gate_findings") or 0) for r in recs)},
            "H_en": {lvl: {"stop": sum(1 for r in recs if r["en"][lvl]["status"] == "stop"),
                           "attempt1_major_total": sum((r["en"][lvl].get("n_major") or 0) for r in recs),
                           "translation_major_total": sum((r["en"][lvl].get("n_translation") or 0) for r in recs),
                           "ja_source_major_total": sum((r["en"][lvl].get("n_ja_source") or 0) for r in recs),
                           "m1_fired": sum(1 for r in recs if r["en"][lvl].get("m1_fired"))} for lvl, _, _ in LEVELS},
            "I_m3": {"protected_keys_total": sum((c["n_protected_keys"] or 0) for _, _, c in runs),
                     "reclassify_excluded_flagged_total": sum(r["g3"]["reclassify_excluded_flagged"] for r in recs),
                     "m3_would_protect_changed_actor_total(旧腕での影の対照)": sum(r["g3"]["m3_would_protect_changed_actor"] for r in recs),
                     "en_translation_minor_total": sum(r["g3"]["translation_minor"] for r in recs)},
            "K_first_ja_recheck": {"n": sum(1 for r in recs if r["first_ja_recheck"]), "rate_over_articles": (sum(1 for r in recs if r["first_ja_recheck"]) / n) if n else None},
            "L_human_intervention": {**hi, "total": sum(hi.values()), "rate_over_planned": (sum(hi.values()) / planned) if planned else None},
            "M_new_specific_claim": {"final_total": sum((r["ii_new_specific_final"] or 0) for r in recs), "delta_vs_r0_total": sum((r["ii_delta_vs_r0"] or 0) for r in recs)},
            "N_shadow_stop_b1": {"shadow_stop_initial": sum(1 for r in recs if r["shadow_stop_initial"]), "shadow_stop_final": sum(1 for r in recs if r["shadow_stop_final"]),
                                 "b1_recoveries": sum(r["b1_recovery"] for r in recs), "b1_denied": sum(len(r["b1_denied"]) for r in recs)},
            "R0_echo_remaining_in_final": sum(1 for r in recs if (r["ja"].get("r2_echo") or {}).get("echo_anywhere")),
            "stub_values": any(c["stub"] for _, _, c in runs)}
        out["per_theme"] += recs
    return out


def to_markdown(agg: dict) -> str:
    n, o = agg["arms"].get("new"), agg["arms"].get("old")
    rows = [("予定run数", "planned_runs"), ("Checker run完了", "checker_runs_done")]
    L = ["# E2E集計(自動生成。stubの場合は値が実測ではない)", "", f"root: `{agg['root']}` / テーマ: {', '.join(agg['themes'])}", "",
         "| 指標 | 新腕 | 旧腕 | 差(新-旧) |", "|---|---|---|---|"]

    def row(label, fn):
        a, b = (fn(n) if n else None), (fn(o) if o else None)
        a, b = (round(a, 3) if isinstance(a, float) else a), (round(b, 3) if isinstance(b, float) else b)
        d = round(a - b, 4) if isinstance(a, (int, float)) and isinstance(b, (int, float)) else ""
        L.append(f"| {label} | {a} | {b} | {d} |")
    for lab, k in rows:
        row(lab, lambda x, k=k: x[k])
    row("A 初回候補(延べ)", lambda x: x["A_checker_candidates"]["union_candidates_total"])
    row("A 再分類で除外されたclaim", lambda x: x["A_checker_candidates"]["excluded_claims_total"])
    row("I M3保護claim", lambda x: x["I_m3"]["protected_keys_total"])
    row("I M3: changed_actor保護されたはずの除外claim(影)", lambda x: x["I_m3"]["m3_would_protect_changed_actor_total(旧腕での影の対照)"])
    row("C Rewrite発生run数", lambda x: x["C_rewrite"]["rewrite_runs"])
    row("C Rewrite率(予定run分母)", lambda x: x["C_rewrite"]["rate_over_planned"])
    row("D Human Review run数", lambda x: x["D_human_review"]["runs"])
    row("E 費用 raw円", lambda x: (x["E_cost"] or {}).get("raw_jpy"))
    row("G JA FC MAJOR(R2)", lambda x: x["G_ja"]["fc_major_total"])
    row("G JA 記号Gate指摘", lambda x: x["G_ja"]["symbol_gate_findings_total"])
    for lvl, _, _ in LEVELS:
        row(f"H EN {lvl} STOP", lambda x, lvl=lvl: x["H_en"][lvl]["stop"])
        row(f"H EN {lvl} 初回MAJOR", lambda x, lvl=lvl: x["H_en"][lvl]["attempt1_major_total"])
        row(f"H EN {lvl} 初回MAJOR(translation由来)", lambda x, lvl=lvl: x["H_en"][lvl]["translation_major_total"])
    row("K 初回JA_RECHECK(記事数)", lambda x: x["K_first_ja_recheck"]["n"])
    row("L 人手介入(件)", lambda x: x["L_human_intervention"]["total"])
    row("L 人手介入率(予定run分母)", lambda x: x["L_human_intervention"]["rate_over_planned"])
    row("M 新規具体主張(ii)最終JA", lambda x: x["M_new_specific_claim"]["final_total"])
    row("N 影STOP(最終)", lambda x: x["N_shadow_stop_b1"]["shadow_stop_final"])
    row("N B1回復発動", lambda x: x["N_shadow_stop_b1"]["b1_recoveries"])
    L += ["", "盲検ラベル・Fable突合が必要な欄(真に重大/不要/F重大軽微)は aggregate.json 上 None。"]
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--out-dir", default=None)
    a = ap.parse_args(argv)
    os.chdir(R.HERE)
    agg = aggregate(a.root)
    od = a.out_dir or f"{a.root}/aggregate"
    R.wj(f"{od}/aggregate.json", agg)
    R.wt(f"{od}/AGGREGATE.md", to_markdown(agg))
    print(f"aggregate written: {od}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
