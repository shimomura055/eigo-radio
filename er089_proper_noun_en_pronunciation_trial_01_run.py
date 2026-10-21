# -*- coding: utf-8 -*-
"""FAMILY-XZ-PROPER-NOUN-EN-PRONUNCIATION-SUPPLY-TRIAL-01 runner(Trial専用)。

Production経路へは配線しない。Production関数は import・呼出のみ。副作用は TrialIsolation で Trial dir へ隔離。
使い方: .venv\\Scripts\\python.exe er089_proper_noun_en_pronunciation_trial_01_run.py <stage>
stage: s2_free | s3_detect | s3_research | s3_register | s3_identity | s3_azure | s3_k3asr
"""
import argparse
import glob
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import er089_proper_noun_en_pronunciation_trial_01_lib as L  # noqa: E402
import er006_pronunciation_ledger_01 as led  # noqa: E402
import er006_secondary_asr_01 as sec  # noqa: E402

OUT = L.OUT_ROOT
CAP_JPY = 200.0
PAID_PATH = os.path.join(OUT, "paid_calls.jsonl")
B_DIR = "er019_output/family_x_audio_production_wiring_01/manga_ai_chat_byus__run_byus_01"
B_RES = f"{B_DIR}/b1b/audit/tts_generation_results.json"
FACT_LEDGER = "er019_output/manga_ai_chat_byus/run_byus_01/research_ledger/verified_fact_ledger.txt"
Z_MELOS = "er026_output/family_z_production_e2e_01/melos/run_e2e_06"
OW_STD = "er026_output/family_z_production_e2e_01/the_open_window/run_e2e_01/writer/std.md"
OW_SEED = "er026_output/family_z_production_e2e_01/the_open_window/seed/seed.json"
JA_TELEMETRY = "er025_output/pronunciation_resolution_core_telemetry_01/telemetry.jsonl"
MUST = {"B": ["byUs", "LINE"], "Melos": ["Melos"], "OW": ["Framton Nuttel"], "OW_seed": ["Framton Nuttel", "Sappleton", "Vera"]}
# 設計の必須名のうちDionysius/Selinuntiusは run_e2e_06 のEN narration本文に出現しない(speaker IDとJA側のみ。S2で実測)。
# Sappleton/VeraもOWのEN narration(std.md)に出現せず seed.json にのみ出現 -> seed要約文を別入力(OW_seed)として検出を測る。
_JA_RE = re.compile(r"[぀-ヿ㐀-鿿]")


def rp(p):
    return os.path.join(L.ROOT, p)


def jdump(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)


def jload(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ------------------------------------------------------------------ inventory
def load_b():
    d = jload(rp(B_RES))
    segs = {k: v["canonical_text"] for k, v in d["segments"].items() if v.get("canonical_text") and not _JA_RE.search(v["canonical_text"])}
    return {"segments": segs, "text": "\n\n".join(segs.values()), "raw": d["segments"]}


def load_z_melos():
    segs, raw = {}, {}
    for lvl in ("a2", "b1b"):
        d = jload(rp(f"{Z_MELOS}/{lvl}/audit/tts_generation_results.json"))
        for k, v in d["segments"].items():
            if isinstance(v, dict) and v.get("canonical_text") and not _JA_RE.search(v["canonical_text"]):
                segs[f"{lvl}/{k}"] = v["canonical_text"]
                raw[f"{lvl}/{k}"] = v
    return {"segments": segs, "text": "\n\n".join(dict.fromkeys(segs.values())), "raw": raw}


def load_ow():
    t = open(rp(OW_STD), encoding="utf-8").read()
    seed = jload(rp(OW_SEED))
    return {"segments": {"std": t}, "text": t, "seed": seed}


def fact_terms_b():
    t = open(rp(FACT_LEDGER), encoding="utf-8").read()
    terms = set()
    for m in re.finditer(r"[A-Za-z][A-Za-z0-9]*(?: [A-Z][A-Za-z0-9]*)*", t):
        s = m.group(0).strip()
        if len(s) >= 3 and (any(c.isupper() for c in s[1:]) or s[0].isupper()):
            terms.add(s)
    return sorted(terms)


def fact_terms_ow(seed):
    s = json.dumps(seed, ensure_ascii=False)
    return sorted(set(re.findall(r"\b[A-Z][a-z]+(?: [A-Z][a-z]+)?\b", s)))


def attempt_wav_b(seg, n):
    for p in glob.glob(rp(f"{B_DIR}/b1b/narration/attempts/{seg}_attempt{n}_*.wav")):
        return p
    return None


def attempt_wav_z(lvl, seg, n):
    for p in glob.glob(rp(f"{Z_MELOS}/{lvl}/narration/attempts/{seg}_attempt{n}_*.wav")):
        return p
    return None


def b_attempt_cases(b):
    """記事Bの実attempt(part1 x3, part3 x3, part2 x1)。Primary/Azure既存転写つき。"""
    cases = []
    for seg in ("full_story_part1", "full_story_part3", "full_story_part2"):
        s = b["raw"][seg]
        for a in s.get("attempts_log") or []:
            aj = a.get("asr_judgement") or {}
            n = a.get("attempt")
            wav = attempt_wav_b(seg, n)
            if wav is None:
                continue
            cases.append({"id": f"B:{seg}:att{n}", "family": "X", "segment_id": seg, "canonical": s["canonical_text"],
                          "primary": (aj.get("primary") or {}).get("text") or a.get("asr_text"),
                          "azure": (aj.get("secondary") or {}).get("text"), "wav": wav, "cs_layer": True,
                          "orig_state": aj.get("state")})
    return cases


def z_cases(z):
    cases = []
    pat = re.compile(r"melos|dionysi|selinunt", re.I)
    for key, s in z["raw"].items():
        if not pat.search(s["canonical_text"]):
            continue
        lvl, seg = key.split("/", 1)
        for a in (s.get("attempts") or [])[:1]:
            if not a.get("asr_text"):
                continue
            wav = attempt_wav_z(lvl, seg, a.get("attempt", 1))
            if wav is None:
                continue
            aj = s.get("asr_judgement") or {}
            cases.append({"id": f"Z:{key}:att{a.get('attempt', 1)}", "family": "Z", "segment_id": seg, "canonical": s["canonical_text"],
                          "primary": a["asr_text"], "azure": ((aj.get("secondary") or {}).get("text") if aj.get("slot") == 1 else None),
                          "wav": wav, "cs_layer": True, "orig_state": aj.get("state")})
    return cases


def synthetic_cases(b):
    p1 = b["segments"]["full_story_part1"]
    wav = attempt_wav_b("full_story_part1", 1)
    k2 = p1.replace("byUs", "Bias")  # byUs->Bias の単独差分のみ
    k5 = p1.replace("LINE Manga", "Lion Manga")  # LINE->Lion の単独差分のみ(実音声が違う想定のASR転写)
    return [
        {"id": "K2:byUs->Bias(only)", "family": "X", "segment_id": "full_story_part1", "canonical": p1, "primary": k2, "azure": None,
         "wav": wav, "cs_layer": False, "expect": "PASS"},
        {"id": "K5ii:LINE->Lion(only)", "family": "X", "segment_id": "full_story_part1", "canonical": p1, "primary": k5, "azure": None,
         "wav": wav, "cs_layer": False, "expect": "NOT_PASS"},
        {"id": "K5ii-short:LINE Manga->Lion Manga", "family": "X", "segment_id": "comment_1",
         "canonical": "LINE Manga already has character chat.", "primary": "Lion Manga already has character chat.", "azure": None,
         "wav": wav, "cs_layer": False, "expect": "NOT_PASS"},
    ]


def eval_case(iso, case, ledger_path, extra_phrases=None):
    """evaluate_attempt_with_cascade(M1有効)を既存転写注入で実行(R-02)。条件切替ごとにM1 cache reset+LEDGER_PATH切替。"""
    iso.set_ledger(ledger_path)
    iso.injected_azure.pop(os.path.abspath(case["wav"]), None)
    if case.get("azure"):
        iso.injected_azure[os.path.abspath(case["wav"])] = case["azure"]
    pl = L.get_pl_list(case["canonical"])
    detail = {}
    try:
        v, stop, cls = sec.evaluate_attempt_with_cascade(
            case["canonical"], case["primary"], [], case["wav"], language="en-US", ledger_phrases=pl, cascade_enabled=True,
            enable_connected_speech_equivalence_layer=bool(case.get("cs_layer")), detail_out=detail, segment_id=case["segment_id"])
    except Exception as exc:  # noqa: BLE001
        return {"id": case["id"], "error": f"{type(exc).__name__}: {str(exc)[:200]}", "pl": pl}
    aj = detail.get("asr_judgement") or {}
    m1 = detail.get("m1_multi_candidate") or {}
    m1rej = detail.get("m1_multi_candidate_rejected") or []
    return {"id": case["id"], "verified": bool(v), "final_status": detail.get("final_status"),
            "classification": getattr(cls, "classification", None), "judge_state": aj.get("state"),
            "layers": (aj.get("adapter") or {}).get("layers"), "pl": pl,
            "m1_candidate_set_hash": m1.get("candidate_set_hash") or (m1rej[0].get("candidate_set_hash") if m1rej else None),
            "m1_accepted": bool(m1), "m1_reject_reasons": [r.get("no_match_reason") or r.get("reason") for r in m1rej],
            "secondary_called": bool((aj.get("secondary") or {}).get("called")),
            "azure_stub_used": bool(case.get("azure"))}


def compare(base, tr):
    keys = ("verified", "final_status", "classification", "judge_state", "layers")
    diff = {k: (base.get(k), tr.get(k)) for k in keys if base.get(k) != tr.get(k)}
    return diff


# ------------------------------------------------------------------ leak (R-05)
def corpus_texts():
    """過去run全EN segment本文(dedupe)。{text_sha: (text, [source files])}。"""
    out = {}
    for f in glob.glob(rp("**/tts_generation_results*.json"), recursive=True):
        if os.sep + ".venv" + os.sep in f or "er089_output" in f:
            continue
        try:
            d = jload(f)
        except Exception:  # noqa: BLE001
            continue
        for _k, v in (d.get("segments") or {}).items() if isinstance(d, dict) else []:
            if isinstance(v, dict):
                t = v.get("canonical_text") or v.get("text")
                if isinstance(t, str) and t and not _JA_RE.search(t):
                    h = L.sha256_text(t)
                    out.setdefault(h, (t, set()))[1].add(os.path.relpath(f, L.ROOT).replace("\\", "/"))
    return out


def leak_measure(new_surfaces, trial_ledger_path, home_markers):
    """新規entryごとの発火件数を、(a)ホーム記事 (b)ホーム以外に分けて集計。get_hint_for_text(min_confidence='low')を実関数で再計算。"""
    corp = corpus_texts()
    res = {s: {"home": 0, "outside": 0, "outside_examples": []} for s in new_surfaces}
    base_led = L.ledger_snapshot(rp(L.REAL_LEDGER_PATH))
    prev = led.LEDGER_PATH
    try:
        led.LEDGER_PATH = trial_ledger_path
        for h, (t, srcs) in corp.items():
            hits = {e["surface"].lower() for e in led.get_hint_for_text(t, min_confidence="low")}
            for s in new_surfaces:
                if s.lower() in hits:
                    is_home = any(m in src for src in srcs for m in home_markers.get(s, []))
                    if is_home:
                        res[s]["home"] += 1
                    else:
                        res[s]["outside"] += 1
                        if len(res[s]["outside_examples"]) < 5:
                            res[s]["outside_examples"].append({"text": t[:140], "src": sorted(srcs)[:2]})
    finally:
        led.LEDGER_PATH = prev
    return {"n_unique_texts": len(corp), "per_surface": res, "real_ledger_entries": len(base_led)}


# ------------------------------------------------------------------ S2 (free)
def stage_s2():
    t0 = time.time()
    b, z, ow = load_b(), load_z_melos(), load_ow()
    results = {"started": time.strftime("%Y-%m-%dT%H:%M:%S")}
    with L.TrialIsolation() as iso:
        base = L.ledger_snapshot(iso.base_ledger)
        ja_b = L.load_ja_gate_tokens(rp(JA_TELEMETRY), "2026-10-21T13:00:00", "2026-10-21T13:30:00")
        ja_z = []  # Zの対象JA記事のtelemetry窓が特定できず、任意窓ではtest由来のダミートークン(Uniqxxx等)が混入したため未使用(R-12のJA Gate規則はX記事Bで検証)
        d1 = {}
        for name, art, facts, gate in (("B", b, fact_terms_b(), ja_b), ("Melos", z, [], ja_z), ("OW", ow, fact_terms_ow(ow["seed"]), [])):
            r = L.detect_d1(art["text"], ledger=base, fact_terms=facts, ja_gate_tokens=gate)
            rec = L.recall_against(r["candidates"], MUST[name])
            d1[name] = {"n_candidates": len(r["candidates"]), "n_excluded": len(r["excluded"]), "recall": rec,
                        "must": MUST[name], "ja_gate_tokens_used": gate, "n_fact_terms": len(facts),
                        "candidates": [{"surface": c["surface"], "rules": c["rules"], "evidence_only": c["evidence_only"]} for c in r["candidates"]],
                        "excluded": [{"surface": c["surface"], "reason": c["excluded_reason"]} for c in r["excluded"]]}
        seed_txt = ow["seed"].get("original_summary", "")
        r = L.detect_d1(seed_txt, ledger=base, fact_terms=fact_terms_ow(ow["seed"]))
        d1["OW_seed"] = {"n_candidates": len(r["candidates"]), "n_excluded": len(r["excluded"]),
                         "recall": L.recall_against(r["candidates"], MUST["OW_seed"]), "must": MUST["OW_seed"],
                         "candidates": [{"surface": c["surface"], "rules": c["rules"], "evidence_only": c["evidence_only"]} for c in r["candidates"]],
                         "excluded": [], "ja_gate_tokens_used": [], "n_fact_terms": 0}
        d1["_note_names_not_in_en_text"] = {"Dionysius": "not in run_e2e_06 EN narration (speaker id / JA only)",
                                            "Selinuntius": "not in run_e2e_06 EN narration (speaker id / JA only)",
                                            "Sappleton,Vera": "not in OW std.md narration; present only in seed.json original_summary"}
        results["d1"] = d1
        # R-12 negative-ish set(件数のみ): 非候補セット
        neg = ["story-making", "Manga", "AI"]
        results["d1_nonmust_flagged_note"] = {n: [c["surface"] for c in d1["B"]["candidates"] if c["surface"].lower() == n.lower()] for n in neg}
        # 漏れ測定(R-05): 仮想entry(発火は surface のみで決まる)
        hypo = os.path.join(OUT, "ledger_trial_copy", "ledger_hypothetical_for_leak.json")
        hl = dict(base)
        for s in ("byUs", "LINE", "Melos", "Dionysius", "Selinuntius", "Framton Nuttel", "Nuttel", "Framton", "Sappleton", "Vera"):
            hl[f"hypo_{s}"] = {"surface": s, "entity_type": "proper_noun", "canonical_spelling": s, "pronunciation_hint": "x-y",
                               "confidence": "medium", "sources": ["https://x"], "expected_pronunciation_ipa": "", "alternate_pronunciations": []}
        jdump(hypo, hl)
        results["leak_hypothetical"] = leak_measure(
            ["byUs", "LINE", "Melos", "Dionysius", "Selinuntius", "Framton Nuttel", "Nuttel", "Framton", "Sappleton", "Vera"], hypo,
            {"byUs": ["manga_ai_chat_byus"], "LINE": ["manga_ai_chat_byus"], "Melos": ["family_z_production_e2e_01/melos"],
             "Dionysius": ["family_z_production_e2e_01/melos"], "Selinuntius": ["family_z_production_e2e_01/melos"],
             "Framton Nuttel": ["the_open_window"], "Nuttel": ["the_open_window"], "Framton": ["the_open_window"],
             "Sappleton": ["the_open_window"], "Vera": ["the_open_window"]})
        # baseline(Ledger無=現行Production相当)の同一性検証入力
        cases = b_attempt_cases(b) + synthetic_cases(b) + z_cases(z)
        base_eval = {}
        for c in cases:
            base_eval[c["id"]] = eval_case(iso, c, iso.base_ledger)
        results["identity_baseline"] = base_eval
        results["n_cases"] = len(cases)
        jdump(os.path.join(OUT, "inputs", "cases.json"), [{k: v for k, v in c.items()} for c in cases])
        results["unexpected_calls"] = iso.unexpected_calls()
        results["watch"] = iso.watch_report()
    results["elapsed_s"] = round(time.time() - t0, 1)
    jdump(os.path.join(OUT, "s2_free_results.json"), results)
    print(json.dumps({"n_cases": results["n_cases"], "unexpected": len(results["unexpected_calls"]),
                      "d1": {k: (v["n_candidates"], v["recall"]["recall"]) for k, v in d1.items() if isinstance(v, dict) and "recall" in v},
                      "elapsed_s": results["elapsed_s"]}, ensure_ascii=False))


# ------------------------------------------------------------------ K5 voters (free, local whisper)
def stage_k5vote():
    """K5(R-09): 投票者=Primary(既存転写)/Azure PL無(既存転写)/faster-whisper medium(ローカル、費用0)。Azure PL有は投票から除外。"""
    import er008_disfluency_qa_18 as dq
    b = load_b()
    out = {"voters": ["primary_existing", "azure_no_pl_existing", "whisper_medium_local"],
           "excluded_voters": ["azure_with_pl (same engine family, not independent)"], "per_attempt": []}
    for case in b_attempt_cases(b):
        if case["segment_id"] != "full_story_part1":
            continue
        words = dq.transcribe_verbatim(case["wav"], language="en", model_size="medium")
        wtext = " ".join(w["text"].strip() for w in words).strip()
        rec = {"id": case["id"], "wav": os.path.relpath(case["wav"], L.ROOT).replace("\\", "/"),
               "primary": case["primary"], "azure_no_pl": case["azure"], "whisper_medium": wtext}

        def toks(t):
            return [m.group(1).lower() for m in re.finditer(r"\b(line|lion|lyon|lyin|lying|lined)\b\s+manga", (t or ""), flags=re.I)]
        votes = {"primary": toks(case["primary"]), "azure_no_pl": toks(case["azure"]) if case["azure"] else None,
                 "whisper_medium": toks(wtext)}
        rec["votes"] = votes
        per_occ = []
        for i in range(2):  # 本文中の "LINE Manga" 2か所を位置ごとに投票
            cast = [v[i] for v in votes.values() if v and len(v) > i]
            n_line = sum(1 for x in cast if x == "line")
            n_other = len(cast) - n_line
            if len(cast) < 2:
                verdict = "AMBIGUOUS(votes<2)"
            elif n_line > n_other:
                verdict = "AUDIO_LIKELY_CORRECT"
            elif n_other > n_line:
                verdict = "AUDIO_LIKELY_MISPRONOUNCED"
            else:
                verdict = "AMBIGUOUS"
            per_occ.append({"occurrence": i + 1, "cast": cast, "verdict": verdict})
        rec["per_occurrence"] = per_occ
        rec["verdict"] = ("AUDIO_LIKELY_CORRECT" if all(o["verdict"] == "AUDIO_LIKELY_CORRECT" for o in per_occ)
                          else ("AUDIO_LIKELY_MISPRONOUNCED" if any(o["verdict"] == "AUDIO_LIKELY_MISPRONOUNCED" for o in per_occ) else "AMBIGUOUS"))
        rec["listening_needed"] = rec["verdict"] != "AUDIO_LIKELY_CORRECT"
        out["per_attempt"].append(rec)
    jdump(os.path.join(OUT, "k5_votes.json"), out)
    print(json.dumps([(r["id"], r["votes"], [o["verdict"] for o in r["per_occurrence"]], r["verdict"]) for r in out["per_attempt"]], ensure_ascii=False))


# ------------------------------------------------------------------ S3: 検出(D2)
ARTICLES = {
    "B": {"title": "byUs: an AI story chat service launched on LINE Manga (Japanese manga app)"},
    "Melos": {"title": "Run, Melos! (Osamu Dazai's story retold in English)"},
    "OW": {"title": "The Open Window (Saki's short story)"},
}


def stage_s3_detect():
    paid = L.PaidCallLedger(PAID_PATH, CAP_JPY)
    b, z, ow = load_b(), load_z_melos(), load_ow()
    base = L.ledger_snapshot(rp("er089_output/proper_noun_en_pronunciation_trial_01/ledger_trial_copy/ledger_baseline_copy.json"))
    arts = {"B": (b["text"], fact_terms_b()[:40]), "Melos": (z["text"], []), "OW": (ow["text"], [])}
    out = {"d2": {}}
    client = L.openai_client()
    for name, (text, facts) in arts.items():
        d1 = L.detect_d1(text, ledger=base, fact_terms=facts if name == "B" else None)
        d1keys = {c["key"] for c in d1["candidates"]}
        out["d2"][name] = {}
        for model in ("gpt-6.1-sol", "gpt-6-luna"):
            r = L.detect_d2(paid, text, ARTICLES[name]["title"], facts, model, {"article": name}, client=client)
            keys = {i["surface"].lower() for i in r["items"]}
            must = MUST.get(name, [])
            out["d2"][name][model] = {
                "n_items": len(r["items"]), "items": r["items"], "parse_ok": r["paid"]["parse_ok"], "jpy": r["paid"]["jpy"],
                "must_recall": L.recall_against([{"key": k} for k in keys], must) if must else None,
                "only_in_d2_vs_d1": sorted(keys - d1keys), "only_in_d1_vs_d2": len(d1keys - keys),
                "usage": r["paid"]["usage"], "resp_model": r["paid"]["resp_model"]}
    out["total_jpy"] = paid.total_jpy()
    jdump(os.path.join(OUT, "s3_detect_results.json"), out)
    print(json.dumps({"total_jpy": out["total_jpy"],
                      "recall": {n: {m: (v["must_recall"] or {}).get("recall") for m, v in d.items()} for n, d in out["d2"].items()}},
                     ensure_ascii=False))


# ------------------------------------------------------------------ S3: 研究(腕A/B)
RESEARCH_TARGETS = [
    {"surface": "byUs", "type": "product", "context": "an AI story chat service name appearing in an English article about a Japanese manga app"},
    {"surface": "LINE", "type": "brand", "context": "brand name in 'LINE Manga' (Japanese messaging/manga app)"},
    {"surface": "Melos", "type": "person", "context": "name of the hero in a retelling of Osamu Dazai's 'Run, Melos!'"},
    {"surface": "Framton Nuttel", "type": "person", "context": "character name in Saki's short story 'The Open Window'"},
    {"surface": "Sappleton", "type": "person", "context": "surname (Mrs. Sappleton) in Saki's short story 'The Open Window'"},
    {"surface": "Vera", "type": "person", "context": "girl's name in Saki's short story 'The Open Window'"},
    {"surface": "Zorbleflux", "type": "brand", "context": "product name appearing in an English article"},
]


def stage_s3_research():
    paid = L.PaidCallLedger(PAID_PATH, CAP_JPY)
    out = {"targets": RESEARCH_TARGETS, "arms": {}}
    a = L.research_arm_a(paid, RESEARCH_TARGETS)
    b = L.research_arm_b(paid, RESEARCH_TARGETS)
    for arm, r in (("A", a), ("B", b)):
        out["arms"][arm] = {"items": r["items"], "error": r.get("error"), "paid": r.get("paid"), "model": r.get("model"),
                            "response_id": r.get("response_id"), "prompt_sha256": r.get("prompt_sha256"),
                            "sources": r.get("sources") or r.get("citations"), "raw_text": r.get("raw_text")}
    out["total_jpy"] = paid.total_jpy()
    out["retrieved_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    jdump(os.path.join(OUT, "s3_research_raw.json"), out)
    print(json.dumps({"total_jpy": out["total_jpy"], "A_items": len(a["items"]), "B_items": len(b["items"]),
                      "B_err": b.get("error")}, ensure_ascii=False))


EXTRA_FOCUS = ("Search specifically for ENGLISH-language sources: NAVER WEBTOON / WEBTOON Entertainment global press releases, LINE Digital Frontier "
               "or LINE Manga English pages, English-language news about the service named byUs, and official English trailers or videos. "
               "State what those English sources say about how the name is pronounced (even if only that they never state it). "
               "For LINE also check whether the company has stated an official English pronunciation of the brand name.")


def stage_s3_research_extra():
    """追加調査(腕A2): byUs/LINEの英語情報源の有無に絞った1呼出(J7の証拠収集。K1がUNCONFIRMED_SAFEの場合の委任文指示)。"""
    paid = L.PaidCallLedger(PAID_PATH, CAP_JPY)
    targets = [t for t in RESEARCH_TARGETS if t["surface"] in ("byUs", "LINE")]
    a = L.research_arm_a(paid, targets, extra=EXTRA_FOCUS, planned_jpy=30.0)
    out = {"arm": "A2", "targets": targets, "items": a["items"], "paid": a["paid"], "model": a.get("model"),
           "response_id": a.get("response_id"), "prompt_sha256": a.get("prompt_sha256"), "sources": a.get("sources"),
           "raw_text": a.get("raw_text"), "retrieved_at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    jdump(os.path.join(OUT, "s3_research_extra_raw.json"), out)
    print(json.dumps({"total_jpy": paid.total_jpy(), "items": len(a["items"])}, ensure_ascii=False))


def stage_j7_evidence():
    """J7証拠(費用0): PR TIMES原文のbyUs読み該当箇所をHTTP取得で確認(V1'と同じ関数)。"""
    url = "https://prtimes.jp/main/html/rd/p/000000536.000063705.html"
    r = L.verify_quote_in_source(url, "byUs（バイアス）")
    page = None
    try:
        page = L.default_fetch(url)
    except Exception as exc:  # noqa: BLE001
        r["fetch_error"] = str(exc)[:120]
    ctx = []
    if page:
        for m in re.finditer(r"byUs", page):
            ctx.append(page[max(0, m.start() - 40):m.end() + 60])
            if len(ctx) >= 3:
                break
    out = {"url": url, "verify": r, "contexts": ctx, "english_pronunciation_in_page": bool(page and re.search(r"pronounc", page, re.I))}
    jdump(os.path.join(OUT, "j7_evidence.json"), out)
    print(json.dumps({"quote_found": r.get("quote_found"), "n_ctx": len(ctx)}, ensure_ascii=False))


def stage_s3_register():
    """validator(V1〜V6+V1')を適用し、通過分のみTrial Ledgerへ登録。通過しないものは UNCONFIRMED_SAFE(登録0)。"""
    raw = jload(os.path.join(OUT, "s3_research_raw.json"))
    ex_path = os.path.join(OUT, "s3_research_extra_raw.json")
    if os.path.exists(ex_path):
        ex = jload(ex_path)
        raw["arms"]["A2"] = {"items": ex["items"], "model": ex.get("model"), "prompt_sha256": ex.get("prompt_sha256"),
                             "response_id": ex.get("response_id")}
    decisions, registered = [], []
    with L.TrialIsolation() as iso:
        iso.set_ledger(iso.trial_ledger)
        for t in RESEARCH_TARGETS:
            s = t["surface"]
            per_arm = {}
            for arm in [x for x in ("A", "A2", "B") if x in raw["arms"]]:
                a = raw["arms"][arm]
                item = next((i for i in a["items"] if (i.get("surface") or "").lower() == s.lower()), None)
                if item is None:
                    per_arm[arm] = {"decision": "UNCONFIRMED_SAFE", "reasons": ["no_item_returned"], "checks": {}, "entry": None, "arm": arm}
                    continue
                meta = {"retrieved_at": raw["retrieved_at"], "model": a.get("model"), "prompt_sha256": a.get("prompt_sha256"),
                        "response_id": a.get("response_id")}
                item = dict(item)
                item.setdefault("canonical_spelling", s)
                if (item.get("canonical_spelling") or "").lower() != s.lower():
                    item["canonical_spelling"] = item.get("canonical_spelling") or s
                per_arm[arm] = L.validate_item(item, s, L.ledger_snapshot(iso.trial_ledger), arm=arm, meta=meta)
                per_arm[arm]["raw_item"] = item
            chosen = next((per_arm[a] for a in ("A", "A2", "B") if a in per_arm and per_arm[a]["decision"] == "REGISTER"), None)
            rec = {"surface": s, "per_arm": {k: {kk: vv for kk, vv in v.items() if kk != "entry"} for k, v in per_arm.items()},
                   "decision": "REGISTER" if chosen else "UNCONFIRMED_SAFE", "chosen_arm": chosen["arm"] if chosen else None}
            if chosen:
                hints = {k: (v.get("raw_item") or {}).get("pronunciation_hint") for k, v in per_arm.items() if v["decision"] == "REGISTER"}
                rec["cross_arm_hints_among_registrable"] = hints
                lid = L.register_entry(iso.trial_ledger, s, chosen["entry"])
                registered.append({"surface": s, "ledger_id": lid, "arm": chosen["arm"], "hint": chosen["entry"]["pronunciation_hint"],
                                   "confidence": chosen["entry"]["confidence"], "sources": chosen["entry"]["sources"]})
            decisions.append(rec)
        before = L.ledger_snapshot(iso.base_ledger)
        after = L.ledger_snapshot(iso.trial_ledger)
        diff = L.ledger_diff(before, after)
        existing_unchanged = diff["changed"] == [] and diff["removed"] == []
        res = {"decisions": decisions, "registered": registered, "ledger_diff": diff, "existing_entries_unchanged": existing_unchanged,
               "n_baseline_entries": len(before), "n_trial_entries": len(after),
               "trial_ledger_sha256": L.sha256_file(iso.trial_ledger), "baseline_copy_sha256": L.sha256_file(iso.base_ledger),
               "watch": iso.watch_report(), "unexpected_calls": iso.unexpected_calls()}
    jdump(os.path.join(OUT, "s3_register_results.json"), res)
    print(json.dumps({"registered": [r["surface"] for r in registered],
                      "unconfirmed": [d["surface"] for d in decisions if d["decision"] != "REGISTER"],
                      "existing_unchanged": res["existing_entries_unchanged"], "real_unchanged": res["watch"]["real_ledger_unchanged"]},
                     ensure_ascii=False))



# ------------------------------------------------------------------ S3: 同一性検証(R-02) base / trial / hypo
HYPO_FIXTURES = {
    # 注意: これは『登録された場合の判定への影響』を測る**テスト用フィクスチャ**であり、事実主張ではない(証拠ベースでは未登録)。
    "byUs": {"entity_type": "product", "ipa": "/ˈbaɪəs/", "hint": "BY-us"},
    "LINE": {"entity_type": "brand", "ipa": "/laɪn/", "hint": "LYNE"},
    "Melos": {"entity_type": "person", "ipa": "/ˈmiːlɒs/", "hint": "MEE-los"},
    "Framton": {"entity_type": "person", "ipa": "/ˈfræmtən/", "hint": "FRAM-tun"},
    "Nuttel": {"entity_type": "person", "ipa": "/ˈnʌtəl/", "hint": "NUT-ul"},
    "Sappleton": {"entity_type": "person", "ipa": "/ˈsæpəltən/", "hint": "SAP-ul-tun"},
}


def build_hypo_ledger(iso):
    """Trial Ledger(実登録分)+テスト用フィクスチャentry(sources非空=M1のC2条件を満たす最大限のケース)。別fileで保持。"""
    path = os.path.join(OUT, "ledger_trial_copy", "ledger_hypothetical_registered_fixture.json")
    led_d = L.ledger_snapshot(iso.trial_ledger)
    for s, f in HYPO_FIXTURES.items():
        key = led.LedgerKey(surface=s, entity_type=f["entity_type"], source_context="")
        led_d[f"hypo_{key.ledger_id()}"] = {
            "surface": s, "entity_type": f["entity_type"], "source_context": "", "canonical_spelling": s,
            "language_origin": "", "expected_pronunciation_ipa": f["ipa"], "pronunciation_hint": f["hint"],
            "alternate_pronunciations": [], "confidence": "medium", "ambiguity_note": "TEST FIXTURE (not evidence)",
            "sources": ["https://fixture.invalid/test-only"], "updated_at": "2026-10-01T00:00:00",
            "ja_reading_katakana": "", "ja_reading_confidence": "", "ja_reading_sources": [],
            "resolution_method": "test_fixture", "resolved_at_stage": "trial_pre_tts",
            "tts_injection_disabled": True, "tts_injection_disabled_reason": "fixture"}
    jdump(path, led_d)
    return path


def stage_s3_identity():
    b, z = load_b(), load_z_melos()
    cases = b_attempt_cases(b) + synthetic_cases(b) + z_cases(z)
    res = {"conditions": {"base": "real Ledger copy (=現行Production相当)", "trial": "Trial Ledger(実際に登録できた分のみ)",
                          "hypo": "Trial Ledger + テスト用フィクスチャ(byUs/LINE/Melos/Framton/Nuttel/Sappleton が登録された場合の安全性測定。事実主張ではない)"},
           "cases": {}}
    with L.TrialIsolation() as iso:
        hypo = build_hypo_ledger(iso)
        paths = {"base": iso.base_ledger, "trial": iso.trial_ledger, "hypo": hypo}
        for c in cases:
            rec = {}
            for cond, pth in paths.items():
                r = eval_case(iso, c, pth)
                iso.set_ledger(pth)
                r["frozen_candidate_set"] = L.m1_candidate_set(c["canonical"], pth)
                rec[cond] = r
            rec["diff_trial_vs_base"] = compare(rec["base"], rec["trial"])
            rec["diff_hypo_vs_base"] = compare(rec["base"], rec["hypo"])
            rec["candidate_set_hash_changed_hypo"] = rec["base"]["frozen_candidate_set"]["stable_candidates_hash"] != rec["hypo"]["frozen_candidate_set"]["stable_candidates_hash"]
            rec["candidate_set_hash_changed_trial"] = rec["base"]["frozen_candidate_set"]["stable_candidates_hash"] != rec["trial"]["frozen_candidate_set"]["stable_candidates_hash"]
            rec["family"] = c["family"]
            rec["expect"] = c.get("expect")
            res["cases"][c["id"]] = rec
        res["unexpected_calls"] = iso.unexpected_calls()
        res["stub_azure_calls"] = L.read_jsonl(iso.azure_stub_path)[-3:]
        res["watch"] = iso.watch_report()
    # 集計
    def grp(ids):
        return {i: res["cases"][i] for i in ids if i in res["cases"]}
    same_group = [i for i, r in res["cases"].items() if r["family"] == "X"]
    z_group = [i for i, r in res["cases"].items() if r["family"] == "Z"]
    res["summary"] = {
        "X_cases": len(same_group),
        "X_trial_diffs": {i: res["cases"][i]["diff_trial_vs_base"] for i in same_group if res["cases"][i]["diff_trial_vs_base"]},
        "X_hypo_diffs": {i: res["cases"][i]["diff_hypo_vs_base"] for i in same_group if res["cases"][i]["diff_hypo_vs_base"]},
        "Z1_cases": len(z_group),
        "Z1_trial_changes": {i: res["cases"][i]["diff_trial_vs_base"] for i in z_group if res["cases"][i]["diff_trial_vs_base"]},
        "Z1_hypo_changes": {i: res["cases"][i]["diff_hypo_vs_base"] for i in z_group if res["cases"][i]["diff_hypo_vs_base"]},
        "Z1_candidate_set_hash_changed_hypo": [i for i in z_group if res["cases"][i]["candidate_set_hash_changed_hypo"]],
        "candidate_set_hash_changed_trial": [i for i, r in res["cases"].items() if r["candidate_set_hash_changed_trial"]],
        "K3": res["cases"].get("B:full_story_part1:att1"),
        "errors": [i for i, r in res["cases"].items() if any("error" in r[c] for c in ("base", "trial", "hypo"))],
    }
    jdump(os.path.join(OUT, "s3_identity_results.json"), res)
    sm = res["summary"]
    print(json.dumps({"X_cases": sm["X_cases"], "X_trial_diffs": len(sm["X_trial_diffs"]), "X_hypo_diffs": len(sm["X_hypo_diffs"]),
                      "Z1_cases": sm["Z1_cases"], "Z1_trial_changes": len(sm["Z1_trial_changes"]),
                      "Z1_hypo_changes": len(sm["Z1_hypo_changes"]), "errors": sm["errors"],
                      "unexpected": len(res["unexpected_calls"])}, ensure_ascii=False))



# ------------------------------------------------------------------ S3: Azure A/B(R-10 圧縮版)+K3 実ASR
def classify_azure_text(canonical, text, segment_id):
    """Azure転写をSecondary許容集合と同じ式(should_pass or CMU Case A/homophone)で分類。M1はX(byUs/LINEともCMU収録語)では対象外。"""
    import er006_preprod_hardening_01_validation as val
    cls = val.classify_asr_match(canonical, text, segment_id=segment_id)
    alt = sec._step_alternate_pass(cls)
    return {"classification": cls.classification, "should_pass": bool(cls.should_pass), "alt_label": alt,
            "accepted": bool(cls.should_pass or alt),
            "content_word_diffs": [{"canonical": d.get("canonical"), "asr": d.get("asr")} for d in cls.protected.content_word_diffs][:12]}


def byus_variants(canonical, text):
    """canonical中のbyUs/LINE位置に対応するAzure側の表記(多語化の検出: Buy Us/by us)。"""
    t = (text or "")
    multi = re.findall(r"\b(buy us|by us|bye us|buyers)\b", t, flags=re.I)
    single = re.findall(r"\b(byus|bias|baias|bayas|fayas|bios|buyas|bayus|biass)\b", t, flags=re.I)
    line = re.findall(r"\b(line|lion)\s+manga\b", t, flags=re.I)
    return {"multiword": [m.lower() for m in multi], "single": [m.lower() for m in single], "line_manga": [m.lower() for m in line]}


def stage_s3_azure():
    """腕M(綴りのみ供給)対 baseline(PL無)。Production関数 get_full_text_via_azure_stt_with_phrase_list を実呼出し(SDK診断ログでspeech.context取得)。
    R-10: 各条件1回+差異があったwav・決定性確認2本のみ2回目。Z(Melos)はbaseline PL==trial PL(実Ledgerのcascade entryで既にPL=['Melos'])のため呼ばない。"""
    paid = L.PaidCallLedger(PAID_PATH, CAP_JPY)
    ev_path = os.path.join(OUT, "phrase_list_evidence.jsonl")
    b = load_b()
    cases = [c for c in b_attempt_cases(b) if c["segment_id"] in ("full_story_part1", "full_story_part3")]
    out = {"runs": [], "z_skipped": {}, "label_note": "arm M = 綴りのみ直接供給(Ledger登録を介さない、Production関数経由ではなくphrases引数へ直接投入)。K1がUNCONFIRMED_SAFEのため"
           "byUs/LINEはLedger経由では供給されない=機構・効果の測定であって登録の代替ではない"}
    sdk_dir = os.path.join(OUT, "sdk_tmp")
    with L.TrialIsolation() as iso:
        iso.set_ledger(iso.base_ledger)
        hypo = build_hypo_ledger(iso)
        for c in cases:
            iso.set_ledger(iso.base_ledger)
            pl_base = L.get_pl_list(c["canonical"])
            iso.set_ledger(hypo)
            pl_m = [p for p in L.get_pl_list(c["canonical"]) if p in ("byUs", "LINE")]
            iso.set_ledger(iso.base_ledger)
            out["runs"].append({"id": c["id"], "wav": c["wav"], "pl_base": pl_base, "pl_m": pl_m, "canonical": c["canonical"],
                                "segment_id": c["segment_id"]})
        # 1周目(各条件1回)
        for r in out["runs"]:
            for cond, pl in (("baseline", r["pl_base"]), ("armM", r["pl_m"])):
                rec = L.azure_production_call(iso, paid, r["wav"], pl, {"id": r["id"], "cond": cond, "pass": 1}, sdk_dir, ev_path)
                r.setdefault("pass1", {})[cond] = rec
                r["pass1"][cond]["cls"] = classify_azure_text(r["canonical"], rec["transcript"], r["segment_id"]) if rec["transcript"] else None
                r["pass1"][cond]["variants"] = byus_variants(r["canonical"], rec["transcript"])
        # 2周目: 差異があったwav(両条件) + 決定性確認2本(差異無しのwavのbaselineを再実行)
        def norm(t):
            return re.sub(r"[^a-z0-9]+", " ", (t or "").lower()).strip()
        diff_ids = [r["id"] for r in out["runs"] if norm(r["pass1"]["baseline"]["transcript"]) != norm(r["pass1"]["armM"]["transcript"])]
        same_ids = [r["id"] for r in out["runs"] if r["id"] not in diff_ids][:2]
        out["pass2_targets"] = {"differing": diff_ids, "determinism_baseline_only": same_ids}
        for r in out["runs"]:
            conds = []
            if r["id"] in diff_ids:
                conds = [("baseline", r["pl_base"]), ("armM", r["pl_m"])]
            elif r["id"] in same_ids:
                conds = [("baseline", r["pl_base"])]
            for cond, pl in conds:
                rec = L.azure_production_call(iso, paid, r["wav"], pl, {"id": r["id"], "cond": cond, "pass": 2}, sdk_dir, ev_path)
                rec["cls"] = classify_azure_text(r["canonical"], rec["transcript"], r["segment_id"]) if rec["transcript"] else None
                rec["variants"] = byus_variants(r["canonical"], rec["transcript"])
                r.setdefault("pass2", {})[cond] = rec
        # Z: baseline PL == trial PL かを記録(呼出なし)
        z = load_z_melos()
        for zc in z_cases(z)[:6]:
            iso.set_ledger(iso.base_ledger)
            pb = L.get_pl_list(zc["canonical"])
            iso.set_ledger(iso.trial_ledger)
            pt = L.get_pl_list(zc["canonical"])
            out["z_skipped"][zc["id"]] = {"pl_baseline": pb, "pl_trial": pt, "identical_after_dedupe": sorted(set(p.lower() for p in pb)) == sorted(set(p.lower() for p in pt))}
        out["unexpected_calls"] = iso.unexpected_calls()
        out["watch"] = iso.watch_report()
    import shutil as _sh
    _sh.rmtree(sdk_dir, ignore_errors=True)  # SDK生ログ(認証情報を含み得る)は抽出後に削除。repoに残さない
    out["total_azure_jpy_this_stage"] = round(sum(x["jpy"] for x in L.read_jsonl(PAID_PATH) if x.get("kind") == "azure_stt"), 4)
    out["cumulative_jpy"] = paid.total_jpy()
    jdump(os.path.join(OUT, "s3_azure_results.json"), out)
    print(json.dumps({"cumulative_jpy": out["cumulative_jpy"], "azure_jpy": out["total_azure_jpy_this_stage"],
                      "pass2": out["pass2_targets"], "evidence_match": [e["match"] for e in L.read_jsonl(ev_path) if e["phrases_expected"]]},
                     ensure_ascii=False))


def stage_s3_k3asr():
    """K3(byUs->Bias + story-making->storymaking): part1 att1 wav をProduction Primary ASRで実転写1回し、①反映後の判定関数で判定。"""
    import er006_asr_provider_routing_01 as routing
    paid = L.PaidCallLedger(PAID_PATH, CAP_JPY)
    b = load_b()
    c = [x for x in b_attempt_cases(b) if x["id"] == "B:full_story_part1:att1"][0]
    dur = L.wav_seconds(c["wav"])
    est = dur / 60.0 * 0.003 * L.JPY_PER_USD  # gpt-4o-mini-transcribe 公称$0.003/min(上限見積)
    paid.check_cap(est)
    with L.TrialIsolation() as iso:
        t0 = time.time()
        text, err = routing.transcribe(c["wav"], language="en-US")
        paid.record({"kind": "primary_asr_k3", "model": "gpt-4o-mini-transcribe", "wav": os.path.relpath(c["wav"], L.ROOT), "jpy": round(est, 4),
                     "cost_source": "estimated(official $0.003/min x duration)", "elapsed_s": round(time.time() - t0, 2), "err": err})
        res = {"wav": os.path.relpath(c["wav"], L.ROOT).replace("\\", "/"), "fresh_primary_text": text, "err": err,
               "existing_primary_text": c["primary"]}
        if text:
            for cond, pth in (("base", iso.base_ledger), ("trial", iso.trial_ledger)):
                cc = dict(c)
                cc["primary"] = text
                res[cond] = eval_case(iso, cc, pth)
        res["existing_text_eval"] = {cond: eval_case(iso, c, pth) for cond, pth in (("base", iso.base_ledger), ("trial", iso.trial_ledger))}
        res["unexpected_calls"] = iso.unexpected_calls()
    jdump(os.path.join(OUT, "s3_k3asr_results.json"), res)
    print(json.dumps({"err": err, "base": (res.get("base") or {}).get("final_status"), "existing": res["existing_text_eval"]["base"]["final_status"]}, ensure_ascii=False))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("stage")
    a = ap.parse_args()
    {"s2_free": stage_s2, "k5vote": stage_k5vote, "s3_detect": stage_s3_detect, "s3_research": stage_s3_research,
     "s3_register": stage_s3_register, "s3_research_extra": stage_s3_research_extra, "j7": stage_j7_evidence, "s3_identity": stage_s3_identity, "s3_azure": stage_s3_azure, "s3_k3asr": stage_s3_k3asr}[a.stage]()
