# -*- coding: utf-8 -*-
"""er089 評価集計(API 0)。各stageの出力JSONから、事前固定ラベルに沿った集計 results_summary.json を作る。最終ラベルはFable。"""
import collections
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import er089_proper_noun_en_pronunciation_trial_01_lib as L  # noqa: E402
import er089_proper_noun_en_pronunciation_trial_01_run as R  # noqa: E402

OUT = L.OUT_ROOT


def jl(name):
    return R.jload(os.path.join(OUT, name))


def main():
    s2, det, reg, ident = jl("s2_free_results.json"), jl("s3_detect_results.json"), jl("s3_register_results.json"), jl("s3_identity_results.json")
    az, k3, k5 = jl("s3_azure_results.json"), jl("s3_k3asr_results.json"), jl("k5_votes.json")
    paid = L.read_jsonl(os.path.join(OUT, "paid_calls.jsonl"))
    summ = {}
    # ---- 費用
    by_kind = collections.OrderedDict()
    for p in paid:
        d = by_kind.setdefault(p["kind"], {"calls": 0, "jpy": 0.0})
        d["calls"] += 1
        d["jpy"] = round(d["jpy"] + p.get("jpy", 0.0), 4)
    summ["cost"] = {"by_kind": by_kind, "total_jpy": round(sum(p.get("jpy", 0) for p in paid), 4), "cap_jpy": R.CAP_JPY,
                    "n_paid_calls": len(paid), "planned_kinds_only": sorted(set(p["kind"] for p in paid))}
    # ---- 設計外呼出
    unexpected = []
    for name, d in (("s2", s2), ("identity", ident), ("azure", az)):
        unexpected += [{"stage": name, **u} for u in d.get("unexpected_calls", [])]
    summ["unexpected_calls"] = {"count": len(unexpected), "items": unexpected,
                                "isolated_unexpected_file_lines": len(L.read_jsonl(os.path.join(OUT, "isolated", "unexpected_calls.jsonl")))}
    # ---- 検出(D1/D2)
    d2s = {}
    for art, models in det["d2"].items():
        d2s[art] = {m: {"n_items": v["n_items"], "jpy": v["jpy"], "items": [i["surface"] for i in v["items"]],
                        "only_in_d2_vs_d1": v["only_in_d2_vs_d1"]} for m, v in models.items()}
    summ["detection"] = {"d1": {k: {"n_candidates": v["n_candidates"], "recall": v["recall"]["recall"], "per_word": v["recall"]["per_word"]}
                                for k, v in s2["d1"].items() if isinstance(v, dict) and "recall" in v},
                         "d1_notes": s2["d1"].get("_note_names_not_in_en_text"), "d2": d2s}
    # D1∪D2 再現率(語がphrase内に含まれる場合も検出済み)
    union = {}
    must_by_art = {"B": ["byUs", "LINE"], "Melos": ["Melos"], "OW": ["Framton Nuttel"]}
    for art, must in must_by_art.items():
        d1keys = {c["surface"].lower() for c in s2["d1"][art]["candidates"]}
        for model in ("gpt-6.1-sol", "gpt-6-luna"):
            d2keys = {i["surface"].lower() for i in det["d2"][art][model]["items"]}
            per = {}
            for m in must:
                ml = m.lower()
                per[m] = ("D1" if ml in d1keys else "") + ("+D2" if ml in d2keys else "") + ("+D2(in phrase)" if any(ml in k.split() or ml in k for k in d2keys) and ml not in d2keys else "")
            union.setdefault(art, {})[model] = per
    summ["detection"]["d1_union_d2"] = union
    # ---- 登録判定
    summ["registration"] = {"registered": reg["registered"], "unconfirmed_safe": [d["surface"] for d in reg["decisions"] if d["decision"] != "REGISTER"],
                            "reasons": {d["surface"]: {a: v["reasons"][:4] for a, v in d["per_arm"].items()} for d in reg["decisions"]},
                            "existing_entries_unchanged": reg["existing_entries_unchanged"], "real_ledger_unchanged": reg["watch"]["real_ledger_unchanged"],
                            "n_baseline_entries": reg["n_baseline_entries"], "n_trial_entries": reg["n_trial_entries"],
                            "trial_ledger_sha256": reg["trial_ledger_sha256"], "baseline_copy_sha256": reg["baseline_copy_sha256"]}
    # ---- 同一性(R-02)
    sm = ident["summary"]
    summ["identity"] = {"X_cases": sm["X_cases"], "X_trial_diffs": len(sm["X_trial_diffs"]), "X_hypo_diffs": len(sm["X_hypo_diffs"]),
                        "Z1_cases": sm["Z1_cases"], "Z1_trial_changes": len(sm["Z1_trial_changes"]), "Z1_hypo_changes": len(sm["Z1_hypo_changes"]),
                        "Z1_candidate_pron_set_changed_hypo": len(sm["Z1_candidate_set_hash_changed_hypo"]),
                        "errors": sm["errors"], "K3_existing_primary": ident["cases"]["B:full_story_part1:att1"]["base"]["final_status"]}
    keycases = {}
    for k in ("K2:byUs->Bias(only)", "K5ii:LINE->Lion(only)", "K5ii-short:LINE Manga->Lion Manga", "B:full_story_part1:att1", "B:full_story_part3:att2"):
        c = ident["cases"][k]
        keycases[k] = {cond: {"verified": c[cond]["verified"], "final_status": c[cond]["final_status"], "layers": c[cond]["layers"]}
                       for cond in ("base", "trial", "hypo")}
    summ["identity"]["key_cases"] = keycases
    # K6: two works -> 20 works : part3 att2 primary text contains "20 works"
    c6 = ident["cases"]["B:full_story_part3:att2"]
    summ["identity"]["K6"] = {"primary_has_20_works": "20 works" in next(x for x in R.b_attempt_cases(R.load_b()) if x["id"] == "B:full_story_part3:att2")["primary"],
                              "verified": {k: c6[k]["verified"] for k in ("base", "trial", "hypo")}}
    # ---- K3
    summ["K3"] = {"existing_primary_eval": k3["existing_text_eval"], "fresh_asr_text_head": (k3.get("fresh_primary_text") or "")[:160],
                  "fresh_eval": {k: k3.get(k) for k in ("base", "trial")}}
    # ---- K5
    summ["K5"] = {"per_attempt": [{"id": r["id"], "votes": r["votes"], "per_occurrence": r["per_occurrence"], "verdict": r["verdict"],
                                   "listening_needed": r["listening_needed"]} for r in k5["per_attempt"]]}
    # ---- Azure A/B 効果
    ev = L.read_jsonl(os.path.join(OUT, "phrase_list_evidence.jsonl"))
    pl_calls = [e for e in ev if e["phrases_expected"]]
    summ["phrase_list_evidence"] = {"n_calls": len(ev), "n_pl_calls": len(pl_calls),
                                    "pl_calls_match_all": all(e["match"] for e in pl_calls) if pl_calls else None,
                                    "examples": [{"wav": e["wav"].split("/")[-1], "phrases": e["phrases_expected"], "dgi_items": e["dgi_items"], "bias": e["bias"],
                                                  "match": e["match"]} for e in pl_calls[:3]],
                                    "no_pl_calls_have_no_dgi": all(not e["has_dgi"] for e in ev if not e["phrases_expected"])}
    eff = []
    for r in az["runs"]:
        for ps in ("pass1", "pass2"):
            d = r.get(ps) or {}
            if "baseline" in d and "armM" in d:
                b, m = d["baseline"], d["armM"]
                eff.append({"id": r["id"], "pass": ps, "baseline_accepted": b["cls"]["accepted"], "armM_accepted": m["cls"]["accepted"],
                            "baseline_variants": b["variants"], "armM_variants": m["variants"],
                            "flip": ("NG->PASS" if (not b["cls"]["accepted"] and m["cls"]["accepted"]) else
                                     "PASS->NG" if (b["cls"]["accepted"] and not m["cls"]["accepted"]) else "no_change"),
                            "multiword_removed": bool(b["variants"]["multiword"]) and not m["variants"]["multiword"],
                            "lion_to_line": ("lion" in b["variants"]["line_manga"]) and ("lion" not in m["variants"]["line_manga"])})
    summ["azure_effect"] = {"pairs": eff, "flips": collections.Counter(e["flip"] for e in eff if e["pass"] == "pass1"),
                            "multiword_removed_pass1": sum(1 for e in eff if e["pass"] == "pass1" and e["multiword_removed"]),
                            "lion_to_line_pass1": sum(1 for e in eff if e["pass"] == "pass1" and e["lion_to_line"]),
                            "pass2_targets": az["pass2_targets"],
                            "z_skipped_identical_pl": {k: v["identical_after_dedupe"] for k, v in az["z_skipped"].items()}}
    # 決定性: pass2 baseline vs pass1 baseline
    det_chk = []
    for r in az["runs"]:
        if "pass2" in r:
            for cond in r["pass2"]:
                a, b2 = r["pass1"][cond]["transcript"], r["pass2"][cond]["transcript"]
                det_chk.append({"id": r["id"], "cond": cond, "identical_transcript": a == b2,
                                "same_variants": r["pass1"][cond]["variants"] == r["pass2"][cond]["variants"]})
    summ["azure_determinism"] = det_chk
    # ---- 漏れ測定(実Trial Ledger = Vera のみ)
    summ["leak_actual_trial_ledger"] = R.leak_measure(["Vera"], R.os.path.join(OUT, "ledger_trial_copy", "ledger.json"),
                                                       {"Vera": ["the_open_window"]})
    summ["leak_hypothetical_if_registered"] = {k: {"home": v["home"], "outside": v["outside"]}
                                                for k, v in s2["leak_hypothetical"]["per_surface"].items()}
    summ["leak_hypothetical_n_unique_texts"] = s2["leak_hypothetical"]["n_unique_texts"]
    summ["leak_line_outside_examples"] = s2["leak_hypothetical"]["per_surface"]["LINE"]["outside_examples"][:3]
    # ---- 参考(J5): 既存の汚染entry(`us`=cascade_unresolved_entity, canonical='unknown')が過去EN本文で発火する件数(実Ledgerコピー)
    summ["existing_contamination_us_entry"] = R.leak_measure(["us"], os.path.join(OUT, "ledger_trial_copy", "ledger_baseline_copy.json"),
                                                              {"us": ["__none__"]})["per_surface"]["us"]
    # ---- OW Z2: PL for narration text under trial ledger
    ow = R.load_ow()
    import er006_pronunciation_ledger_01 as led
    iso_prev = led.LEDGER_PATH
    led.LEDGER_PATH = os.path.join(OUT, "ledger_trial_copy", "ledger.json")
    try:
        seed_txt = ow["seed"].get("original_summary", "")
        summ["Z2"] = {"pl_for_std_narration_text": L.get_pl_list(ow["text"]), "pl_for_seed_summary": L.get_pl_list(seed_txt)}
    finally:
        led.LEDGER_PATH = iso_prev
    # ---- J3(測定のみ・判定基準は変更しない): 多語化(Buy Us / by us)を1語(Bias)に置換した反実仮想で、Secondary許容集合式が通る件数
    import re as _re
    import er006_preprod_hardening_01_validation as val
    import er006_secondary_asr_01 as sec
    j3 = []
    for r in az["runs"]:
        t = r["pass1"]["baseline"]["transcript"]
        if not _re.search(r"\b(buy us|by us)\b", t, flags=_re.I):
            continue
        t2 = _re.sub(r"\b(buy us|by us)\b", "Bias", t, flags=_re.I)
        c0 = val.classify_asr_match(r["canonical"], t, segment_id=r["segment_id"])
        c1 = val.classify_asr_match(r["canonical"], t2, segment_id=r["segment_id"])
        j3.append({"id": r["id"], "orig_label": c0.classification, "orig_pass": bool(c0.should_pass or sec._step_alternate_pass(c0)),
                   "counterfactual_label": c1.classification, "counterfactual_pass": bool(c1.should_pass or sec._step_alternate_pass(c1)),
                   "remaining_diffs": [(d.get("canonical"), d.get("asr")) for d in c1.protected.content_word_diffs][:6]})
    summ["J3_counterfactual_multiword"] = {"cases": j3, "would_pass": sum(1 for x in j3 if x["counterfactual_pass"] and not x["orig_pass"]), "n": len(j3),
                                           "note": "測定のみ。判定関数は変更していない(転写テキスト側を置換した反実仮想)。"}
    iso_dir = os.path.join(OUT, "isolated")
    stats = {}
    if os.path.isdir(iso_dir):
        for fn in sorted(os.listdir(iso_dir)):
            fp = os.path.join(iso_dir, fn)
            stats[fn] = {"bytes": os.path.getsize(fp), "lines": sum(1 for _ in open(fp, encoding="utf-8", errors="replace"))}
    summ["isolated_dir_files"] = stats  # 隔離先に書かれた副作用(Production側の同名ファイルではなくTrial dirへ)。大きいjsonlは件数のみ保持
    # ---- Production code diff 0
    try:
        out = subprocess.run(["git", "diff", "--stat", "HEAD", "--", "*.py"], cwd=L.ROOT, capture_output=True, text=True).stdout
        prod_changed = [ln.split("|")[0].strip() for ln in out.splitlines() if "|" in ln]
        summ["production_py_diff_vs_HEAD"] = [f for f in prod_changed if not f.startswith("er089_")]
    except Exception as exc:  # noqa: BLE001
        summ["production_py_diff_vs_HEAD"] = f"error {exc}"
    R.jdump(os.path.join(OUT, "results_summary.json"), summ)
    print(json.dumps({"cost": summ["cost"]["total_jpy"], "unexpected": summ["unexpected_calls"]["count"],
                      "registered": [r["surface"] for r in reg["registered"]], "prod_diff": summ["production_py_diff_vs_HEAD"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
