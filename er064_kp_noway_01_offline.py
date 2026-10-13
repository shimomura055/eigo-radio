# ============================================================
# er064_kp_noway_01_offline.py  (FAMILY-X-KP-NO-WAY-MINIMAL-FIX-TRIAL-01 委任_01、Trial専用・Production非接続・JPY0)
# LLM/TTS/ASR呼出なし(FakeClientのみ)。既存成果物(Round1/2のM2P0 run、shortlists_r1.json、Phase2 run)を読み、
#  (1) P0X(P0+1段落)の差分・sha・token、候補ブロックがP0と同一であること(=M2P0対照を再利用できること)
#  (2) 構文断片の発生段階の再確認(candidate/containment/fragment_risk/canon)
#  (3) 案B表示形の既存Validator(選定gate・Rule7・語数・有限助動詞)への通過可否(実関数・FakeClientで実gate経路)
#  (4) hardcode禁止の静的検査 (5) 費用見積用の実績集計
# を行い er064_output/kp_no_way_fix_01/offline_check_01.json を出力する。
# 使い方: PYTHONPATH=. PYTHONUTF8=1 .venv/Scripts/python.exe er064_kp_noway_01_offline.py
# ============================================================
from __future__ import annotations

import difflib
import glob
import json
import os
import re
import statistics
import sys

sys.path.insert(0, os.getcwd())
import er003_key_words_canonicalization as kc  # noqa: E402
import er030_key_phrase_db_hybrid_selector_01 as selector01  # noqa: E402
import er064_kp_idiom_trial_01_select as S  # noqa: E402
import er064_kp_int_01_machine as MC  # noqa: E402
import er064_kp_int_01_prompts as PR  # noqa: E402
import er064_kp_noway_01_prompts as NP  # noqa: E402
import er064_kp_opt_01_phase2_run_03 as R  # noqa: E402
import er064_kp_opt_01_upstream_core as U  # noqa: E402

OUT = "er064_output/kp_no_way_fix_01"
R1 = "er064_output/kp_integrated_opt_01/round1"
R2 = "er064_output/kp_integrated_opt_01/round2"
CELLS = [("coffee", "std"), ("coffee", "adv"), ("meta", "std"), ("meta", "adv"), ("hormuz", "std"), ("hormuz", "adv")]
BAN_WORDS = ["no way", "know", "meta", "coffee", "hormuz", "pump", "fist", "wallet", "time lag", "show up", "come down", "behind", "price", "roast",
             "bean", "concierge", "contract", "scenes", "strait"]


def jload(p):
    return json.load(open(p, encoding="utf-8"))


def sha_text(s):
    return NP.sha(s)


# ---------- 1. Prompt差分 ----------
def prompt_section():
    res = {"added_paragraph": NP.ADDED_PARAGRAPH, "cells": {}}
    h0, hx = NP.B1.before_static(), NP.head_p0x()
    res["head_unified_diff"] = list(difflib.unified_diff(h0.splitlines(), hx.splitlines(), "P0_head", "P0X_head", lineterm="", n=1))
    res["head_chars"] = {"P0": len(h0), "P0X": len(hx), "added": len(hx) - len(h0)}
    res["approx_tokens_added"] = MC.tok_count(NP.ADDED_PARAGRAPH)
    res["tokens_method"] = "tiktoken(o200k_base)" if "tiktoken" in sys.modules else "UTF-8 bytes/4近似(tiktoken未導入)"
    all_same = True
    for art, lv in CELLS:
        key = f"{art}_{lv}"
        b = MC.build_pattern(key, "M2")
        cb = R.cand_block(b["rows_text"])
        m0 = PR.render("P0", lv, cb)
        mx = NP.render_p0x(cb)
        stripped = mx.replace("\n\n" + NP.ADDED_PARAGRAPH, "", 1)
        fs = sorted(glob.glob(f"{R1}/runs/{art}_{lv}_M2P0_run*/job_result.json"))
        jr = [jload(f) for f in fs]
        ctl = {"n_existing_M2P0_runs": len(jr),
               "msg_sha256_set_match_current_P0": ({j["msg_sha256"] for j in jr} == {sha_text(m0)}) if jr else None,
               "rows_sha256_set_match": ({j["rows_sha256"] for j in jr} == {sha_text(b["rows_text"])}) if jr else None}
        res["cells"][key] = {"P0_msg_sha256": sha_text(m0), "P0X_msg_sha256": sha_text(mx), "rows_sha256": sha_text(b["rows_text"]),
                             "P0X_minus_added_paragraph_equals_P0": stripped == m0, "n_candidates": len(b["shortlist"]),
                             "chars_P0": len(m0), "chars_P0X": len(mx), "control": ctl}
        all_same &= (stripped == m0) and (ctl["msg_sha256_set_match_current_P0"] in (True, None))
    res["all_cells_only_added_paragraph_differs_and_control_reusable"] = all_same
    return res


# ---------- 2. 発生段階の再確認(meta_adv M2P0) ----------
def stage_section():
    d = jload(f"{R1}/shortlists_r1.json")["articles"]["meta_adv"]
    res = {}
    for pat in ("M0", "M2"):
        cs = d[pat]["candidates"]
        c7 = [c for c in cs if c["surface_form"].lower() == "no way"]
        res[pat] = {"candidate_entry": c7, "n_candidates": len(cs), "tier_h_dropped": d[pat]["tier_h_dropped"], "reserved": d[pat]["reserved"],
                    "longer_variants_in_shortlist": [c["surface_form"] for c in cs if "no way" in c["surface_form"].lower() and c["surface_form"].lower() != "no way"]}
    snap = jload(U.SNAPSHOT_PATH)
    res["wiktionary_snapshot_lookups"] = {k: snap["multiword"][k]["hit"] for k in snap["multiword"]
                                          if k.lower() in ("no way", "had no way", "have no way", "no way to", "way to know", "way to")}
    res["fragment_risk_rule"] = {"FRAG_START_contains_first_token": "no" in U.FRAG_START, "registered_exempts": True,
                                 "fragment_risk(registered=True)": U.fragment_risk("no way", True, no_aux=True),
                                 "fragment_risk(registered=False)": U.fragment_risk("no way", False, no_aux=True)}
    runs = []
    for f in sorted(glob.glob(f"{R1}/runs/meta_adv_*/job_result.json") + glob.glob(f"{R2}/runs/meta_adv_*/job_result.json")):
        j = jload(f)
        for it in j.get("raw_selected_items", []):
            if it["source_candidate_id"] == "C7":
                cz = [c for c in j.get("canonicalized", []) if c["rank"] == it["rank"]]
                runs.append({"tag": j["tag"], "rank": it["rank"], "display_phrase": it["display_phrase"], "surface_echo": it["surface_echo"],
                             "normalization_type": it["normalization_type"], "normalization_note": it["normalization_note"],
                             "selection_reason": it["selection_reason"],
                             "gate": [j["selection_status"], j.get("canonicalization_status"), j.get("redundancy_status"), j.get("merged_overall_status")],
                             "canonicalized": cz})
    res["c7_selections"] = runs
    inv = []
    for f in sorted(glob.glob("er064_output/kp_extraction_selection_opt_01/phase2/runs/meta_adv_*/job_result.json")):
        j = jload(f)
        inv.append({"tag": j.get("tag"), "canon": j.get("canonicalization_status"), "canon_reasons": j.get("canonicalization_item_reasons")})
    res["phase2_meta_adv_canon_not_pass"] = [x for x in inv if x["canon"] != "CANONICALIZATION_PASS"]
    return res


# ---------- 3. 案B表示形のValidator通過可否 ----------
class _Resp:
    def __init__(self, text):
        self.model = S.MODEL
        self.id = "fake_offline"
        self.output_text = text
        self.usage = None


class FakeClient:
    """LLMを呼ばない。事前に用意したJSONテキストを返す(実gate経路の検証用)。"""

    def __init__(self, text):
        self.calls = 0
        outer = self

        class _R:
            def create(self, **kw):
                outer.calls += 1
                return _Resp(text)
        self.responses = _R()


def gate_variants():
    import er064_kp_int_01_run as RUN
    base = jload(f"{R1}/runs/meta_adv_M2P0_run1/job_result.json")
    raw = base["usage"]["selection"][0]["output_text"]
    ctx = RUN.build_ctx("meta", ["M2P0"], levels=("adv",))[("meta", "adv", "M2P0")]
    art = ctx["article_text"]
    sent = ctx["sentence_reference"]["S14"]
    variants = ["no way", "no way to know", "have no way to know", "had no way to know", "no way to", "no way to know whether",
                "have no way", "no way to know whether they", "no way to tell"]
    out = []
    os.makedirs(f"{OUT}/offline_gate", exist_ok=True)
    for v in variants:
        p = json.loads(raw)
        for it in p["items"]:
            if it["source_candidate_id"] == "C7":
                it["display_phrase"] = v
                it["surface_echo"] = v if len(v.split()) <= 6 else "no way to know"
        fc = FakeClient(json.dumps(p, ensure_ascii=False))
        gate, viol = R.run_gate(ctx["msg"], art, ctx["id2c"], ctx["cids"], ctx["sentence_reference"], fc, f"{OUT}/offline_gate", f"variant_{len(out)}")
        lit = v.lower() in sent.lower()
        rec = {"display_phrase": v, "n_words": len(v.split()), "fake_calls": fc.calls, "selection_status": gate["status"],
               "validation_reasons": gate.get("validation_reasons"),
               "item_reasons": [r for r in (gate.get("item_reasons") or []) if r.get("reasons")],
               "contract_violation": viol, "literal_in_source_sentence": lit,
               "verbatim_note": "本文に逐語で存在" if lit else "本文に逐語では存在しない(時制の基本形化または追加語)"}
        if gate["status"] == "KEY_WORDS_STRUCTURE_PASS":
            items = gate["parsed"]["items"]
            it = [i for i in items if i["source_candidate_id"] == "C7"][0]
            rec["candidate_mismatch_suspected"] = it.get("candidate_mismatch_suspected")
            rec["source_span_missing"] = selector01._verify_source_spans_against_raw_article(items, art)
            rec["rule7_unchanged_key_phrase"] = kc.validate_canonicalization_item(v, v, it["source_span"], "none")
        else:
            rec["rule7_unchanged_key_phrase"] = kc.validate_canonicalization_item(v, v, "no way", "none")
        out.append(rec)
    return out


def canon_rule_checks():
    V = kc.validate_canonicalization_item
    cases = [
        ("A. selection=bare / canon LLMがsource_span超えへ拡張(Phase2 C0 run1で観測された型)", V("no way to know", "no way", "no way", "idiom_core")),
        ("B. selection=extended display / canon unchanged", V("no way to know", "no way to know", "no way", "none")),
        ("C. 有限助動詞(have)を含む表示形はunchangedでも不可", V("have no way to know", "have no way to know", "no way", "none")),
        ("D. one's一般化(display 'pump its fist' -> key \"pump one's fist\"、1対1置換)は許可", V("pump one's fist", "pump its fist", "pumps its fist", "generalize_person_dependent_reference")),
        ("D2. 動詞活用を同時に変える置換(pumps its fist -> pump one's fist)は一般化に該当せず不可(canon LLMはdisplayを先に基本形へ整える必要)", V("pump one's fist", "pumps its fist", "pumps its fist", "generalize_person_dependent_reference")),
        ("E. 既存で通る拡張例(push prices up、span 'prices up')はunchangedなら通る", V("push prices up", "push prices up", "prices up", "none")),
        ("F. 6語は不可", V("no way to know whether they were", "no way to know whether they were", "no way", "none")),
    ]
    return [{"case": c, "ok": r["ok"], "reasons": r["reasons"]} for c, r in cases]


# ---------- 4. hardcode禁止の静的検査 ----------
def hardcode_check():
    t = NP.ADDED_PARAGRAPH.lower()
    ban_hits = [w for w in BAN_WORDS if w in t]
    anchors = jload(f"{R1}/anchors_r1.json")["anchors"]
    anchor_hits = [a["label"] for a in anchors if a["label"].lower() in t or re.search(a["full"], t)]
    phrases = set()
    for _k, v in jload(f"{R1}/shortlists_r1.json")["articles"].items():
        for c in v["M2"]["candidates"]:
            if len(c["surface_form"].split()) >= 2:
                phrases.add(c["surface_form"].lower())
    cand_hits = sorted(p for p in phrases if p in t)
    src = open("er064_kp_noway_01_prompts.py", encoding="utf-8").read()
    code_lines = [l for l in src.splitlines() if not l.strip().startswith("#")]
    code_hits = [w for w in BAN_WORDS if any(w in l.lower() for l in code_lines)]
    return {"added_paragraph_ban_word_hits": ban_hits, "added_paragraph_anchor_hits": anchor_hits,
            "added_paragraph_candidate_phrase_hits": cand_hits, "prompts_module_code_ban_word_hits": code_hits,
            "n_candidate_phrases_checked": len(phrases), "ban_words": BAN_WORDS, "pass": not (ban_hits or anchor_hits or cand_hits or code_hits)}


# ---------- 5. 費用実績集計 ----------
def cost_section():
    rows = {}
    for src, pat in ((R1, "M2P0"), (R2, "M2P5")):
        for f in glob.glob(f"{src}/runs/*_{pat}_run*/job_result.json"):
            j = jload(f)
            rows.setdefault((j["article"], j["level"], pat), []).append(j["cost_jpy"])
    tab = {f"{a}_{lv}_{p}": {"n": len(v), "mean": round(statistics.mean(v), 4), "max": max(v), "min": min(v)} for (a, lv, p), v in sorted(rows.items())}
    ctl = [x for (a, lv, p), v in rows.items() if p == "M2P0" for x in v]
    allj = [x for v in rows.values() for x in v]
    return {"per_cell_actual_jpy": tab, "M2P0_all_n": len(ctl), "M2P0_mean": round(statistics.mean(ctl), 4), "M2P0_max": max(ctl),
            "M2P0_M2P5_all_n": len(allj), "all_mean": round(statistics.mean(allj), 4), "all_max": max(allj)}


def main():
    os.makedirs(OUT, exist_ok=True)
    res = {"purpose": "FAMILY-X-KP-NO-WAY-MINIMAL-FIX-TRIAL-01 委任_01 offline check (JPY0, LLM呼出なし)", "llm_calls": 0}
    res["prompt"] = prompt_section()
    res["origin_stage"] = stage_section()
    res["case_b_validator_check"] = gate_variants()
    res["canonicalization_rule_checks"] = canon_rule_checks()
    res["hardcode_check"] = hardcode_check()
    res["cost_actuals"] = cost_section()
    json.dump(res, open(f"{OUT}/offline_check_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({"prompt_ok": res["prompt"]["all_cells_only_added_paragraph_differs_and_control_reusable"], "hardcode_pass": res["hardcode_check"]["pass"],
                      "variants": [(v["display_phrase"], v["selection_status"], v["rule7_unchanged_key_phrase"]["ok"]) for v in res["case_b_validator_check"]]},
                     ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
