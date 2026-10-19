# 委任_01(FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01): Melos/Mellows/Mello/Melo の音素比較 + 既存各機構の判定を既存転写に対しoffline再実行
# (API 0 / Production module はimportして呼ぶだけ、無変更 / telemetry追記は no-op 化 / ledger.jsonはread-only)。
# 付録: 「修正案プロトタイプ」(G-1: CMU語幹+規則屈折でASR OOV語の音素を導出、G-2: 語末歯擦音の有声性差を許容)は
#   本scriptの中だけに存在する検討用で、Productionには一切接続しない(仕様変更候補。採用判断なし)。
# 実行: .venv\Scripts\python.exe -X utf8 <this file> --out <json>   (cwd=repo root。-Iだとcwdがimport pathに入らずProduction moduleをimportできないため-Iなし)
import sys, os, json, argparse, difflib, re, hashlib, collections
sys.path.insert(0, os.getcwd())
import er021_en_asr_semantic_equivalence_production_01 as se
se.append_telemetry_log = lambda *a, **k: None
import pronouncing
import er006_m1_multi_candidate_01 as m1
import er011_b1_connected_speech_validator_01 as csv3
import er011_connected_speech_equivalence_layer_production_01 as eq
import er006_preprod_hardening_01_validation as val
import er006_secondary_asr_01 as sec
import er006_pronunciation_ledger_01 as pl

LEDGER = "er006_output/pronunciation_ledger_01/ledger.json"
ASRJ = "docs/research/FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01/asr_consistency_part3c1_01_result.json"
E21 = "er021_output/en_asr_semantic_equivalence_production_wiring_01/telemetry.jsonl"
CANON = ("He remembered the hands held out for the chains. His friend trusted him without asking for another promise. "
         "Water came slowly through a crack in the rock. Melos drank, got onto his knees, and stood up. He managed one step, "
         "then took another. At the city gates, the bell rang for his friend's death. He raced to the square, where the sword "
         "was already raised above his friend.")
SEG = "full_story_part3_c1"
SIB = ("S", "Z")
FEAT = eq.CONSONANT_FEATURES


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def cmu_all(w):
    return [tuple(m1._strip_stress(x) for x in e.split()) for e in pronouncing.phones_for_word(w.lower())]


# ---- 分析専用: CMU語幹 + 規則屈折(S/Z/IH Z)で OOV語の音素を導出(既存機構ではない。G-1候補) ----
def derive_inflected(word):
    w = word.lower()
    for suf in ("es", "s"):
        if w.endswith(suf) and len(w) > len(suf) + 2:
            stem = w[:-len(suf)]
            sp = cmu_all(stem)
            if sp:
                out = []
                for p in sp:
                    last = p[-1]
                    if last in ("S", "Z", "SH", "ZH", "CH", "JH"):
                        out.append(p + ("IH", "Z"))
                    elif last in FEAT and not FEAT[last][2]:
                        out.append(p + ("S",))
                    else:
                        out.append(p + ("Z",))
                return out, "derived: CMU stem '%s' + regular -%s allomorph (analysis only)" % (stem, suf)
    return [], None


def pron_of(word, frozen):
    """(prons, source) 既存経路の優先順: CMU -> M1凍結C2(Ledger) -> 導出(分析専用)。"""
    c = cmu_all(word)
    if c:
        return c, "CMU(pronouncing)"
    fw = frozen.word(word) if frozen else None
    if fw and fw.candidates:
        return [tuple(x.pron) for x in fw.candidates], "Ledger C2 candidates (IPA->ARPAbet, er006_m1 ipa_to_arpa)"
    d, why = derive_inflected(word)
    return d, why or "NONE (CMU OOV, no existing G2P)"


def align(a, b):
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    ops = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        ops.append({"op": tag, "a": list(a[i1:i2]), "b": list(b[j1:j2]), "a_idx": [i1, i2], "b_idx": [j1, j2]})
    return ops


def classify_diff(a, b):
    ops = align(a, b)
    if not ops:
        return "identical", ops
    if len(a) == len(b) and len(ops) == 1 and len(ops[0]["a"]) == 1:
        x, y = ops[0]["a"][0], ops[0]["b"][0]
        fx, fy = FEAT.get(x), FEAT.get(y)
        if fx and fy and fx[0] == fy[0] and fx[1] == fy[1] and fx[2] != fy[2]:
            return "consonant VOICING-ONLY difference (%s vs %s: same manner/place, voicing differs)" % (x, y), ops
        if fx is None or fy is None:
            return "vowel substitution", ops
        return "consonant substitution (manner/place differs)", ops
    if len(a) == len(b) + 1 and len(ops) == 1 and ops[0]["op"] == "delete" and ops[0]["a_idx"][1] == len(a):
        return "final phoneme DELETION (%s)" % ops[0]["a"][0], ops
    return "other", ops


def voicing_neutral_equiv(p, q):
    p, q = tuple(p), tuple(q)
    return len(p) == len(q) and len(p) >= 2 and p[:-1] == q[:-1] and p[-1] in SIB and q[-1] in SIB


def name_window(t):
    m = re.search(r"rock\.\s*(.{0,30})", t or "")
    return m.group(1) if m else None


def cls_summary(cls):
    d = cls.protected.content_word_diffs
    return {"classification": cls.classification, "should_pass": cls.should_pass,
            "diffs": [{"canonical": x.get("canonical"), "asr": x.get("asr"), "entity_like": x.get("entity_like"),
                       "homophone_candidate": x.get("homophone_candidate")} for x in d]}


def mech_matrix(label, asr_text, other_text, frozen):
    cls = val.classify_asr_match(CANON, asr_text, segment_id=SEG)
    r = {"label": label, "asr_name_window": name_window(asr_text), "classify_asr_match": cls_summary(cls)}
    r["step_alternate_pass(Case A/homophone)"] = sec._step_alternate_pass(cls)
    cs = csv3.classify_connected_speech(CANON, asr_text)
    r["F1_classify_connected_speech"] = {"new_judgment": cs.get("new_judgment"), "rule": cs.get("rule"),
                                         "f1_residual": cs.get("f1_residual"), "f1_explained": cs.get("f1_explained")}
    m = m1.m1_multi_candidate_judge(CANON, asr_text, frozen, base_cls=cls)
    r["M1"] = {"accepted": m.accepted, "reason": m.reason, "applicable": m.applicable,
               "no_match_reason": m.no_match_reason, "f1_residual_kind": m.audit.get("f1_residual_kind")}
    ct, at = val.tokenize(CANON), val.tokenize(asr_text)
    sub, loc = se.determine_sub_reason(classification=cls.classification, should_pass=cls.should_pass,
                                       content_word_diffs=cls.protected.content_word_diffs,
                                       number_mismatches=cls.protected.number_mismatches,
                                       negation_mismatches=cls.protected.negation_mismatches,
                                       canon_tokens=ct, asr_tokens=at)
    r["Tier3"] = {"sub_reason": sub, "diff_loc": loc}
    if other_text is not None and loc:
        ot = val.tokenize(other_text)
        r["Tier3"]["corroboration_supports(other_engine_text)"] = se.corroboration_supports(ct, loc["index"], ot)
        r["Tier3"]["other_engine_token_at_idx"] = ot[loc["index"]] if loc["index"] < len(ot) else None
    for d in cls.protected.content_word_diffs:
        c, a = (d.get("canonical") or "").lower(), (d.get("asr") or "").lower()
        r.setdefault("EqLayer_helpers", []).append({
            "canonical": c, "asr": a, "word_phones(c)": eq.word_phones(c), "word_phones(a)": eq.word_phones(a),
            "phoneme_prefix_drop": eq.phoneme_prefix_drop(c, a),
            "phoneme_final_place_substitution": eq.phoneme_final_place_substitution(c, a),
            "note": "Layer入口はTRUE_CONTENT_MISMATCH限定。本件はUNCERTAINのため不呼出"})
    return r


# ---- 分析専用プロトタイプ(G-1+G-2): Productionへ接続しない ----
def whatif_voicing(asr_text, frozen):
    cls = val.classify_asr_match(CANON, asr_text, segment_id=SEG)
    if cls.classification != "ASR_VALIDATION_UNCERTAIN":
        return {"applicable": False, "why": "base not UNCERTAIN (%s)" % cls.classification}
    repl, trace = {}, []
    for d in cls.protected.content_word_diffs:
        if not d.get("entity_like"):
            return {"applicable": False, "why": "non-entity diff present"}
        a = (d.get("asr") or "").lower()
        c = (d.get("canonical") or "").lower()
        fw = frozen.word(c)
        if not fw or not fw.candidates or any(x.source == "C1_cmu_variant" for x in fw.candidates):
            trace.append({"asr": a, "canonical": c, "result": "skip: canonical not OOV/Ledger-C2"})
            continue
        ap, src = pron_of(a, None)
        hit = [(cp.pron, q) for cp in fw.candidates for q in ap if voicing_neutral_equiv(cp.pron, q)]
        trace.append({"asr": a, "asr_prons": [list(x) for x in ap], "asr_pron_source": src, "canonical": c,
                      "candidates": [list(x.pron) for x in fw.candidates], "voicing_neutral_hit": bool(hit)})
        if hit:
            repl[a] = c
    if not repl:
        return {"applicable": True, "accepted": False, "trace": trace}
    new = asr_text
    for a, c in repl.items():
        new = re.sub(r"\b%s\b" % re.escape(a), c.capitalize(), new, flags=re.I)
    c2 = val.classify_asr_match(CANON, new, segment_id=SEG)
    return {"applicable": True, "accepted": bool(c2.should_pass), "normalized_asr_name_window": name_window(new),
            "post_classification": c2.classification, "trace": trace}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    led_sha0 = sha(LEDGER)
    snap = pl._load()
    frozen = m1.freeze_candidates(CANON, ledger_snapshot=snap, segment_started_at="2026-10-19T12:00:00")
    out = {"ledger_sha256_before": led_sha0, "m1_candidate_set_hash": frozen.candidate_set_hash}
    words = ["melos", "mellows", "mello", "melo", "mellow", "mellos"]
    tab = {}
    for w in words:
        prons, src = pron_of(w, frozen)
        tab[w] = {"prons": [list(p) for p in prons], "source": src}
    out["pronunciations"] = tab
    ref = [tuple(x.pron) for x in frozen.word("melos").candidates]
    rows = []
    for w in ["mellows", "mello", "melo", "mellow", "mellos"]:
        for q in [tuple(x) for x in tab[w]["prons"]]:
            for p in ref:
                kind, ops = classify_diff(p, q)
                rows.append({"melos_ledger_candidate": list(p), "other_word": w, "other_pron": list(q), "diff_kind": kind, "ops": ops,
                             "voicing_neutral_equiv": voicing_neutral_equiv(p, q),
                             "vowel_count_equal": sum(1 for x in p if x not in FEAT) == sum(1 for x in q if x not in FEAT)})
    out["phoneme_diff_table"] = rows
    out["sibilant_features"] = {"S": FEAT["S"], "Z": FEAT["Z"], "src": "er011_connected_speech_equivalence_layer_production_01.py:46-62 (manner, place, voiced)"}
    aj = json.load(open(ASRJ, encoding="utf8"))
    e21 = [json.loads(l) for l in open(E21, encoding="utf8")]
    prod_primary_att2 = e21[9612]["asr"]
    R = aj["runs"]
    r2, r3, r03 = R["run04_att2"], R["run04_att3"], R["run03_att1_PASS_pre_slowdown"]
    cases = [("att2_primary_PRODUCTION(E21行9613)", prod_primary_att2, r2["azure_with_phraselist"]["text"]),
             ("att2_secondary_azure_PL(再現)", r2["azure_with_phraselist"]["text"], prod_primary_att2),
             ("att2_secondary_azure_noPL(再現)", r2["azure_no_phraselist"]["text"], prod_primary_att2),
             ("att2_primary_openai_rerun", r2["primary_openai"]["text"], r2["azure_with_phraselist"]["text"]),
             ("att3_primary_openai_rerun", r3["primary_openai"]["text"], r3["azure_with_phraselist"]["text"]),
             ("att3_secondary_azure_PL", r3["azure_with_phraselist"]["text"], r3["primary_openai"]["text"]),
             ("run03_PASS_primary_openai", r03["primary_openai"]["text"], r03["azure_with_phraselist"]["text"]),
             ("run03_PASS_secondary_azure_PL", r03["azure_with_phraselist"]["text"], r03["primary_openai"]["text"])]
    out["mechanism_matrix"] = [mech_matrix(l, t, o, frozen) for l, t, o in cases]
    out["whatif_G1_G2_prototype"] = {l: whatif_voicing(t, frozen) for l, t, o in cases}
    fx = []

    def fixture(name, cand, asrp, expect):
        got = voicing_neutral_equiv(cand.split(), asrp.split())
        fx.append({"name": name, "canonical_cand": cand, "asr_pron": asrp, "expect_equiv": expect, "got": got, "ok": got == expect})
    fixture("positive: final S vs Z (same stem)", "M EH L OW S", "M EH L OW Z", True)
    fixture("negative: vowel differs", "M EH L OW S", "M IH L OW Z", False)
    fixture("negative: final deleted", "M EH L OW S", "M EH L OW", False)
    fixture("negative: place differs S vs SH", "M EH L OW S", "M EH L OW SH", False)
    fixture("negative: non-final S/Z swap", "S EH L OW M", "Z EH L OW M", False)
    fixture("negative: extra syllable (IH Z)", "M EH L OW S", "M EH L OW IH Z", False)
    fixture("negative: different stem consonant", "M EH L OW S", "M EH R OW Z", False)
    out["fixtures_function_level"] = fx
    pairs = collections.OrderedDict()
    for r in e21:
        d = r.get("diff_span") or {}
        c, aw = (d.get("canonical_word") or "").lower(), (d.get("asr_word") or "").lower()
        if c and aw and c != aw:
            pairs[(c, aw)] = pairs.get((c, aw), 0) + 1
    fcache, hits, n_oov = {}, [], 0
    for (c, aw), n in pairs.items():
        if c not in fcache:
            fcache[c] = m1.freeze_candidates(c, ledger_snapshot=snap, segment_started_at="2026-10-19T12:00:00")
        fw = fcache[c].word(c)
        if not fw or not fw.candidates or any(x.source == "C1_cmu_variant" for x in fw.candidates):
            continue
        n_oov += 1
        ap_, src = pron_of(aw, None)
        if any(voicing_neutral_equiv(x.pron, q) for x in fw.candidates for q in ap_):
            hits.append({"canonical": c, "asr": aw, "occurrences": n, "asr_pron_source": src})
    out["corpus_exposure_census"] = {"source": E21, "rows": len(e21), "unique_diff_pairs": len(pairs),
                                     "pairs_with_OOV_canonical_and_ledger_C2": n_oov,
                                     "pairs_newly_accepted_by_G1G2_prototype": hits}
    out["ledger_sha256_after"] = sha(LEDGER)
    json.dump(out, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("pron:", {k: v["prons"] for k, v in tab.items()})
    for m in out["mechanism_matrix"]:
        print(m["label"], "| cls:", m["classify_asr_match"]["classification"], "| caseA:", m["step_alternate_pass(Case A/homophone)"],
              "| F1:", m["F1_classify_connected_speech"]["new_judgment"], "| M1:", m["M1"]["reason"], m["M1"]["no_match_reason"],
              "| T3:", m["Tier3"].get("corroboration_supports(other_engine_text)"))
    for l, w in out["whatif_G1_G2_prototype"].items():
        print("whatif", l, w.get("accepted"), w.get("why"))
    print("fixtures ok:", all(f["ok"] for f in fx), "| census pairs/oov/hits:", len(pairs), n_oov, hits)
    print("ledger unchanged:", out["ledger_sha256_before"] == out["ledger_sha256_after"])


main()
