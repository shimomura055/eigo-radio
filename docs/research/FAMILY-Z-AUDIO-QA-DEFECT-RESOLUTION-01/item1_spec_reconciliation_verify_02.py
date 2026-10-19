# 委任_05: ①Melos/Mellows 判定順序の各段を実関数で再実測する(read-only・API 0・Production module無変更)
# 実行: .venv\Scripts\python.exe -X utf8 <this> --out <json>   (cwd=repo root)
import sys, os, json, argparse, hashlib
sys.path.insert(0, os.getcwd())
import er021_en_asr_semantic_equivalence_production_01 as se
se.append_telemetry_log = lambda *a, **k: None
import er006_m1_multi_candidate_01 as m1
import er011_b1_connected_speech_validator_01 as csv3
import er006_preprod_hardening_01_validation as val
import er006_secondary_asr_01 as sec
import er006_pronunciation_ledger_01 as pl

LEDGER = "er006_output/pronunciation_ledger_01/ledger.json"
LONG = ("He remembered the hands held out for the chains. His friend trusted him without asking for another promise. "
        "Water came slowly through a crack in the rock. Melos drank, got onto his knees, and stood up. He managed one step, "
        "then took another. At the city gates, the bell rang for his friend's death. He raced to the square, where the sword "
        "was already raised above his friend.")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def trace(canon, asr, frozen, secondary_text=None):
    cls = val.classify_asr_match(canon, asr)
    d = {"asr": asr[:80], "classification": cls.classification, "ratio": round(cls.normalized_ratio, 4),
         "should_pass": cls.should_pass,
         "content_word_diffs": [{k: v[k] for k in ("canonical", "asr", "entity_like", "homophone_candidate")} for v in cls.protected.content_word_diffs]}
    d["caseA_or_homophone_label"] = sec._step_alternate_pass(cls)
    cs = csv3.classify_connected_speech(canon, asr)
    d["F1"] = {"new_judgment": cs.get("new_judgment"), "rule": cs.get("rule"), "f1_residual": cs.get("f1_residual"),
               "f1_explained": cs.get("f1_explained")}
    r = m1.m1_multi_candidate_judge(canon, asr, frozen, base_cls=cls)
    d["M1"] = {"accepted": r.accepted, "reason": r.reason, "applicable": r.applicable, "no_match_reason": r.no_match_reason,
               "subs": [{k: s.get(k) for k in ("from", "to", "canonical_word", "rule")} for s in (r.subs or [])]}
    # 受理面を見るため、M1の入口を通る場合の置換案を列挙
    try:
        flagged = {}
        for e in cls.protected.content_word_diffs:
            for t in e["asr"].split():
                flagged[t] = bool(e["entity_like"])
        by_idx, reasons = m1._enumerate_subs(canon, asr, flagged, frozen, m1.default_cmu)
        d["M1_enumerate_subs"] = {"options": {str(k): [{"to": o["to"], "rule": o["rule"]} for o in v] for k, v in by_idx.items()},
                                  "no_match_reasons": reasons}
        if by_idx:
            subs = [v[0] for v in by_idx.values()]
            repl = {k: v[0]["to"] for k, v in by_idx.items()}
            asr2 = m1._replace_tokens(asr, repl)
            ok, why, cs2 = m1._post_check(canon, asr2, subs)
            d["M1_post_check"] = {"asr2": asr2[:60], "ok": ok, "reason": why, "cs2_new_judgment": cs2.get("new_judgment"),
                                  "cs2_rule": cs2.get("rule"), "cs2_f1_explained": cs2.get("f1_explained")}
    except Exception as ex:
        d["M1_enumerate_subs"] = "ERR %r" % (ex,)
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    s0 = sha(LEDGER)
    snap = pl._load()
    out = {"ledger_sha_before": s0}
    cmu = m1.default_cmu
    out["cmu"] = {w: cmu(w) for w in ("melos", "melo", "mello", "mellow", "mellows", "mellos", "drank", "said")}
    out["F1_helpers"] = {"final_s_sound(Melos)": csv3.final_s_sound("Melos"), "initial_sound(drank)": csv3.initial_sound("drank"),
                         "initial_sound(said)": csv3.initial_sound("said"), "initial_sound(left)": csv3.initial_sound("left"),
                         "s_suffix_label_if_match(Melos,Melo)": csv3.s_suffix_label_if_match("Melos", "Melo"),
                         "s_suffix_label_if_match(Melos,Mello)": csv3.s_suffix_label_if_match("Melos", "Mello"),
                         "s_suffix_label_if_match(Melos,Mellows)": csv3.s_suffix_label_if_match("Melos", "Mellows")}
    out["benign"] = {"_singularize_simple(melos)": val._singularize_simple("melos"),
                     "_is_benign_plural_pair(melos,melo)": val._is_benign_plural_pair("melos", "melo"),
                     "_is_benign_plural_pair(melos,mello)": val._is_benign_plural_pair("melos", "mello"),
                     "_is_benign_plural_pair(melos,mellow)": val._is_benign_plural_pair("melos", "mellow"),
                     "_is_benign_plural_pair(melos,mellows)": val._is_benign_plural_pair("melos", "mellows"),
                     "_singularize_simple(mellows)": val._singularize_simple("mellows")}
    contexts = {"LONG(part3_c1全文, Melos drank)": LONG,
                "SHORT 'Melos drank.'": "Melos drank.",
                "SHORT 'Melos said.'": "Melos said."}
    for cname, canon in contexts.items():
        frozen = m1.freeze_candidates(canon, ledger_snapshot=snap, segment_started_at="2026-10-19T12:00:00")
        out.setdefault("traces", {})[cname] = {}
        for w in ("Melos", "Melo", "Mello", "Mellow", "Mellows", "Mellos"):
            if cname.startswith("LONG"):
                asr = canon.replace("Melos", w)
            else:
                asr = canon.replace("Melos", w)
            out["traces"][cname][w] = trace(canon, asr, frozen)
    # Tier3 corroboration (Primary Mello vs Azure X)
    ct = val.tokenize(LONG) if hasattr(val, "tokenize") else None
    out["tier3"] = {}
    if ct:
        pt = val.tokenize(LONG.replace("Melos", "Mello"))
        loc = se.locate_single_token_diff(ct, pt)
        out["tier3"]["locate_single_token_diff(Primary=Mello)"] = loc
        for az in ("Mellows", "Melos", "Mellow", "Mellos"):
            at = val.tokenize(LONG.replace("Melos", az))
            out["tier3"]["corroboration_supports(Azure=%s)" % az] = se.corroboration_supports(ct, loc["index"], at) if loc else None
    out["ledger_sha_after"] = sha(LEDGER)
    out["ledger_unchanged"] = out["ledger_sha_after"] == s0
    json.dump(out, open(a.out, "w", encoding="utf8"), ensure_ascii=False, indent=1, default=str)
    print("ok", a.out, "ledger_unchanged=", out["ledger_unchanged"])


main()
