# er109_stored_census_01.py
# ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01 委任_01 §3: 保存済みASR記録の実測(API 0・読取専用)。
# 母集団: 全 `**/*tts_generation_results*.json`(本文segment + Key Phrase英語の attempts_log)と、各runの
#   narration/attempts/*.json の cascade_steps(Azure=Secondary転写)。Family A/B/C/X/Zを区別せず、保存分すべてを対象(読み取りのみ)。
# 各attempt行 = (canonical[TTS入力], Primary転写, 保存分類, verified, [Azure転写])。canonicalはresultsの `text`/`canonical_text`。
# 集計: 『NG(または Secondary 救済)なのに、canonicalと転写が er109 の発音同値判定で同値』になった行を、適用ルール別に数える。
#   さらに、現行コード(classify_asr_match+同音救済)で再判定して『今も不合格か』を併記し、保存分類が旧コード由来の過大計上を除く。
# 使い方: .venv\Scripts\python.exe er109_stored_census_01.py [--out <json>]
import argparse
import collections
import glob
import json
import os
import re
import sys

sys.path.insert(0, ".")
import er006_preprod_hardening_01_validation as val
import er006_secondary_asr_01 as S
import er109_asr_orthographic_equivalence_01 as e109

PASS_LABELS = {
    "EXACT_MATCH", "NORMALIZED_MATCH", "HIGH_SIMILARITY_SAFE", "NUMERIC_EQUIVALENCE_MATCH", "TRANSCRIPT_STYLE_NORMALIZED_MATCH",
    "HOMOPHONE_EQUIVALENT", "HOMOPHONE_MATCH_NUMBER_EXCEPTION", "PROPER_NOUN_ENTITY_ARPABET_CONFIRMED", "NUMERIC_VALUE_EQUIVALENT_MATCH",
    "READING_RESOLVED_MATCH", "PASS", "OK",
}
RESCUE_LABELS = {  # 旧Primaryでは不合格で、Secondary/連結音等で救済(=追加ASR費用や警告が発生した行)
    "SECONDARY_ASR_CORROBORATED_MATCH", "SECONDARY_CONFIRMED_PRIMARY_FALSE_NG", "PHONETIC_MATCH", "CONNECTED_SPEECH_ACCEPT",
    "CONNECTED_SPEECH_PASS_WITH_WARNING", "CONNECTED_SPEECH_EQUIVALENCE_ACCEPT", "CONNECTED_SPEECH_EQUIVALENCE_PASS_WITH_WARNING",
    "PASS_WITH_PRONUNCIATION_ALARM",
}
ASCII_LETTER = re.compile(r"[A-Za-z]")
CJK = re.compile(r"[぀-ヿ㐀-鿿]")


def is_english(text):
    if not text:
        return False
    return len(ASCII_LETTER.findall(text)) >= 1 and len(CJK.findall(text)) == 0


def azure_texts_by_attempt(run_dir):
    out = {}
    for f in glob.glob(os.path.join(run_dir, "narration", "attempts", "*.json")):
        try:
            d = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        seg, n = d.get("segment_id"), d.get("attempt_number")
        az = [st.get("text") for st in (d.get("cascade_steps") or []) if str(st.get("provider", "")).startswith("azure") and st.get("text")]
        if az:
            out[(seg, str(n))] = az[0]
    return out


def rows_from_results(path):
    try:
        d = json.load(open(path, encoding="utf-8"))
    except Exception:
        return []
    run_dir = os.path.dirname(os.path.dirname(path))
    azm = azure_texts_by_attempt(run_dir)
    rows = []

    def add(seg_id, v, kp):
        canon = v.get("canonical_text") or v.get("text")
        if not is_english(canon):
            return
        status = v.get("status")
        alog = list(v.get("attempts_log") or [])
        if not alog:
            # Z等: results側にattempts_logが無い場合は narration/attempts/<seg>_attempt*.json(asr_text/audio_classification/verified)で補う
            for af in sorted(glob.glob(os.path.join(run_dir, "narration", "attempts", f"{seg_id}_attempt*.json"))):
                try:
                    ad = json.load(open(af, encoding="utf-8"))
                except Exception:
                    continue
                alog.append({"attempt": ad.get("attempt_number"), "asr_text": ad.get("asr_text"),
                             "audio_classification": ad.get("audio_classification"), "verified": ad.get("verified")})
        for a in alog:
            asr = a.get("asr_text")
            if asr is None:
                continue
            rows.append({
                "src": path.replace("\\", "/"), "seg": seg_id, "kp": kp, "attempt": a.get("attempt"), "canonical": canon, "asr": asr,
                "azure": azm.get((seg_id, str(a.get("attempt")))), "stored_cls": a.get("audio_classification"),
                "verified": a.get("verified"), "final_status": status,
            })
    for seg_id, v in (d.get("segments") or {}).items():
        if isinstance(v, dict):
            add(seg_id, v, False)
    for rank, v in (d.get("key_phrases") or {}).items():
        e = (v or {}).get("english") or {}
        if isinstance(e, dict):
            add(f"kp{rank}_en", e, True)
    return rows


def current_pass(canon, asr, seg):
    cls = val.classify_asr_match(canon, asr, segment_id=seg)
    if cls.should_pass:
        return True, cls.classification
    alt = S._step_alternate_pass(cls)
    if alt:
        return True, str(alt)
    return False, cls.classification


ITN_FEATURES = {
    "digit_token": re.compile(r"\d"), "percent_symbol": re.compile(r"%"), "currency_symbol": re.compile(r"[$£€]"),
    "ampersand": re.compile(r"&"), "ordinal_suffix": re.compile(r"\d(st|nd|rd|th)"), "title_abbrev": re.compile(r"(Mr|Mrs|Ms|Dr|St|Jr|vs)\.?"),
    "okay_OK": re.compile(r"OK"), "dotted_acronym": re.compile(r"(?:[A-Z]\.){2,}"), "hyphen": re.compile(r"[A-Za-z]-[A-Za-z]"),
    "em_dash": re.compile(r"—"), "colon_time": re.compile(r"\d:\d\d"),
}


def itn_profile(pairs):
    """pairs=[(canonical, text)]: canonical側に特徴が無いのに転写側に現れた件数(=自動表記整形の傾向)。"""
    c = collections.Counter()
    for canon, text in pairs:
        if not text:
            continue
        c["n"] += 1
        for k, rx in ITN_FEATURES.items():
            if rx.search(text) and not rx.search(canon):
                c[k] += 1
    return dict(c)


def run():
    files = sorted(f for f in glob.glob("**/*tts_generation_results*.json", recursive=True) if not f.startswith(".venv"))
    rows = []
    for f in files:
        rows += rows_from_results(f)
    # 同一 (canonical, asr, seg種別) の重複(archive複製等)を除いた distinct も併記
    seen = set()
    distinct = []
    for r in rows:
        k = (r["canonical"], r["asr"])
        if k in seen:
            continue
        seen.add(k)
        distinct.append(r)
    stats = collections.Counter()
    by_rule = collections.Counter()
    ng_equiv, rescue_equiv, agreement, azure_examples = [], [], collections.Counter(), []
    for r in rows:
        cp, cl = current_pass(r["canonical"], r["asr"], r["seg"])
        r["current_pass"], r["current_cls"] = cp, cl
        agree_key = ("stored_pass" if (r["stored_cls"] in PASS_LABELS or r["verified"]) else "stored_ng_or_rescue", "now_pass" if cp else "now_ng")
        agreement[agree_key] += 1
        stored_ng = (r["stored_cls"] not in PASS_LABELS) and (not r["verified"])
        stored_rescue = r["stored_cls"] in RESCUE_LABELS
        eq = e109.evaluate(r["canonical"], r["asr"])
        r["e109_equiv"] = eq.equivalent
        r["e109_rules"] = eq.rules
        if stored_ng:
            stats["stored_ng_rows"] += 1
            if not cp:
                stats["stored_ng_and_now_ng"] += 1
            if eq.equivalent:
                stats["stored_ng_e109_equiv"] += 1
                if not cp:
                    stats["stored_ng_e109_equiv_and_now_ng"] += 1
                    for ru in (eq.rules or ["surface_equal"]):
                        by_rule[ru] += 1
                    ng_equiv.append({k: r[k] for k in ("src", "seg", "attempt", "canonical", "asr", "stored_cls", "current_cls", "final_status")}
                                    | {"rules": eq.rules, "reason": eq.reason})
        elif stored_rescue:
            stats["stored_rescue_rows"] += 1
            if eq.equivalent and not cp:
                stats["stored_rescue_e109_equiv_and_now_ng"] += 1
                rescue_equiv.append({k: r[k] for k in ("src", "seg", "attempt", "canonical", "asr", "stored_cls", "current_cls")} | {"rules": eq.rules})
        # Azure(Secondary)転写
        if r.get("azure"):
            stats["azure_text_rows"] += 1
            eqa = e109.evaluate(r["canonical"], r["azure"])
            if eqa.equivalent and eqa.rules and not current_pass(r["canonical"], r["azure"], r["seg"])[0]:
                # Azure転写が(表記差のみで)発音同値なのに現行判定では不合格(自明な完全一致は除く)
                stats["azure_text_e109_equiv_nontrivial_and_now_ng"] += 1
                azure_examples.append({"canonical": r["canonical"], "azure": r["azure"], "rules": eqa.rules, "seg": r["seg"], "src": r["src"]})
    kp_rows = [r for r in rows if r["kp"]]
    distinct_pairs = {(x["canonical"], x["asr"]) for x in ng_equiv}
    distinct_segs = {(x["src"], x["seg"]) for x in ng_equiv}
    stopped_segs = {(x["src"], x["seg"]) for x in ng_equiv if str(x["final_status"]) in ("STOPPED", "HUMAN_REVIEW_LOCKED", "HUMAN_REVIEW_REQUIRED")}
    by_top = collections.Counter(x["src"].split("/")[0] for x in ng_equiv)
    rows_by_top = collections.Counter(r["src"].split("/")[0] for r in rows)
    ng_by_top = collections.Counter(r["src"].split("/")[0] for r in rows if (r["stored_cls"] not in PASS_LABELS) and (not r["verified"]))
    kp_ng_equiv = [x for x in ng_equiv if x["seg"].startswith("kp")]
    hr_ng = [x for x in ng_equiv if str(x["final_status"]) in ("STOPPED", "HUMAN_REVIEW_LOCKED", "HUMAN_REVIEW_REQUIRED")]
    itn = {"openai_primary": itn_profile([(r["canonical"], r["asr"]) for r in rows]),
           "azure_secondary": itn_profile([(r["canonical"], r["azure"]) for r in rows if r.get("azure")])}
    try:
        t = json.load(open("docs/research/KP-QUALITY-IMPROVEMENT-2ITEMS-PRODUCTION-01/noguard_reeval_01.json", encoding="utf-8"))["table"]
        itn["kp_corpus_openai"] = itn_profile([(x["canonical"], x["p"]) for x in t])
        itn["kp_corpus_azure"] = itn_profile([(x["canonical"], x["s"]) for x in t])
        itn["kp_corpus_whisper"] = itn_profile([(x["canonical"], x.get("A_whisper")) for x in t])
    except Exception:
        pass
    summary = {
        "itn_profile_by_provider": itn,
        "results_files": len(files), "attempt_rows_en": len(rows), "distinct_canonical_asr_pairs": len(distinct), "kp_rows": len(kp_rows),
        "stats": dict(stats), "by_rule_stored_ng_e109_equiv_now_ng": dict(by_rule),
        "stored_ng_e109_equiv_now_ng_reaching_final_stop_or_hr": len(hr_ng),
        "false_ng_distinct_pairs": len(distinct_pairs), "false_ng_distinct_segments": len(distinct_segs),
        "false_ng_segments_final_stopped_or_hr": len(stopped_segs), "false_ng_kp_rows": len(kp_ng_equiv),
        "false_ng_rows_by_top_dir": dict(by_top), "all_rows_by_top_dir": dict(rows_by_top), "stored_ng_rows_by_top_dir": dict(ng_by_top),
        "stored_vs_current_agreement": {f"{a}|{b}": n for (a, b), n in agreement.items()},
    }
    summary["azure_equiv_examples"] = azure_examples[:12]
    return summary, ng_equiv, rescue_equiv


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="docs/research/ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01/stored_census_01.json")
    a = ap.parse_args()
    summ, ng_eq, resc = run()
    json.dump({"generated_by": "er109_stored_census_01.py", "api_calls": 0, "cost_jpy": 0, "summary": summ,
               "false_ng_candidates_e109_equiv_but_ng_now": ng_eq, "rescued_rows_e109_equiv_but_ng_now": resc},
              open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(summ, ensure_ascii=False, indent=1))
    for x in ng_eq[:80]:
        print(x["rules"], "|", repr(x["canonical"][:90]), "|", repr(x["asr"][:90]), "|", x["stored_cls"], x["final_status"])
