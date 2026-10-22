# er109_stored_onoff_compare_01.py
# ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01 委任_02 D: 保存ASR記録(A/B/C/X/Z全件)に対する er109 の flag ON/OFF 比較(オフライン・API 0)。
# **Productionへは未配線**。ONは『現行Production判定(B修正後)に、er109の同値を追加で許す』というモデル(配線設計 DESIGN_ADDENDUM_02 §P-06):
#   OFF(現行) = classify_asr_match + _step_alternate_pass +(非KPのみ)最終ANDゲート(値DIFF/否定差)
#   ON(案)    = OFF が合格 -> そのまま(変更なし) / OFF が不合格 かつ er109.equivalent -> 合格。ただし非KPは最終ゲートを丸ごとskipせず、
#               値DIFF・否定差が残る場合は『その差が er109 の同値span内で説明できる場合のみ』解除(P-06)。KPは票(値/否定は監査のみ=2026-10-22解除)。
# 出力: PASS->NG 件数(要件0)、NG->PASS 全件(Family別・A/B/C分離)、保存wav(あれば)のパス。--whisper でローカルWhisper再転写(API 0)。
# 使い方: python er109_stored_onoff_compare_01.py --out <json> [--whisper]
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
import er078_asr_unified_judge_01 as uj
import er109_asr_orthographic_equivalence_01 as e109
import er109_stored_census_01 as census


def family_of(src: str) -> str:
    s = src.replace("\\", "/").lower()
    if "family_z" in s or "er026_output" in s or "/z_s" in s or "kp3v_runtime_evidence" in s and "/z" in s:
        return "Z"
    if "family_x" in s or "er019_output" in s or "er104_output" in s or "er103" in s or "er106" in s or "x_b1b" in s or "m2p0" in s:
        return "X"
    if "er063" in s:
        return "Z"
    return "A/B/C(旧世代・共有Validator)"


def judge_off(c, a, seg, kp):
    cls = val.classify_asr_match(c, a, segment_id=(None if kp else seg))
    alt = None if cls.should_pass else S._step_alternate_pass(cls)
    cls_pass = bool(cls.should_pass or alt)
    gate = None
    final_ok = cls_pass
    basis_ok = False
    vgr = None
    neg = False
    if cls_pass and not kp:
        basis = S._equivalence_basis_of(cls) if cls.should_pass else None
        basis_ok = basis in uj.APPROVED_EQUIVALENCE_BASES
        if not basis_ok:
            vgr, neg = uj._protected(c, a, "en")
            if vgr.kind == uj.vg.DIFF or neg:
                final_ok = False
                gate = "value_diff" if vgr.kind == uj.vg.DIFF else "negation_diff"
    return {"cls_pass": cls_pass, "final_ok": final_ok, "label": cls.classification if cls.should_pass else (str(alt) if alt else cls.classification), "gate": gate}


def _neg_counter(text):
    t = val.expand_standard_contractions(text or "").lower().replace("’", "'")
    t = re.sub(r"\bcan\s+not\b", "cannot", t)
    return collections.Counter(w.replace("'", "") for w in re.findall(r"[a-z']+", t) if w.replace("'", "") in val._NEGATION_WORDS)


def explained_by_spans(c, a, eq, vgr, neg_diff):
    """P-06: 値DIFF/否定差の各々が er109 の同値span(canon_span/asr_span)内で説明できるか。"""
    spans = [s for s in eq.spans if s.equivalent]
    ctext = [" ".join(s.canon_span).lower() for s in spans]
    atext = [" ".join(s.asr_span).lower() for s in spans]
    if vgr is not None and vgr.kind == uj.vg.DIFF:
        for p in vgr.pairs:
            if p.verdict != uj.vg.DIFF:
                continue
            ok = False
            for ct, at in zip(ctext, atext):
                src_ok = (p.src is None) or (str(p.src).lower() in ct)
                hyp_ok = (p.hyp is None) or (str(p.hyp).lower() in at)
                if src_ok and hyp_ok:
                    ok = True
                    break
            if not ok:
                return False
    if neg_diff:
        nc, na = _neg_counter(c), _neg_counter(a)
        in_c = _neg_counter(" ".join(" ".join(s.canon_span) for s in spans))
        in_a = _neg_counter(" ".join(" ".join(s.asr_span) for s in spans))
        if (nc - in_c) != (na - in_a):
            return False
    return True


def judge_on(c, a, seg, kp, off):
    if off["final_ok"]:
        return {"final_ok": True, "by": "off_pass", "warnings": []}
    eq = e109.evaluate(c, a)
    if not eq.equivalent:
        return {"final_ok": False, "by": "ng", "warnings": []}
    if kp:
        return {"final_ok": True, "by": "er109", "warnings": eq.warnings, "rules": eq.rules, "verdict": eq.verdict}
    vgr, neg = uj._protected(c, a, "en")
    if vgr.kind == uj.vg.DIFF or neg:
        if not explained_by_spans(c, a, eq, vgr, neg):
            return {"final_ok": False, "by": "er109_blocked_by_final_gate_unexplained", "warnings": eq.warnings}
    if vgr.kind == uj.vg.AMBIGUOUS:
        return {"final_ok": False, "by": "er109_blocked_ambiguous_value", "warnings": eq.warnings}
    return {"final_ok": True, "by": "er109", "warnings": eq.warnings, "rules": eq.rules, "verdict": eq.verdict}


def find_wav(src, seg, attempt):
    run_dir = os.path.dirname(os.path.dirname(src))
    pats = [f"{run_dir}/narration/attempts/{seg}_attempt{attempt}_*.wav", f"{run_dir}/narration/attempts/{seg}_attempt{attempt}.wav",
            f"{run_dir}/narration/attempts/{seg}_a{attempt}*.wav"]
    for p in pats:
        hits = sorted(glob.glob(p))
        if hits:
            return hits[0].replace("\\", "/")
    return None


def build_rows():
    files = sorted(f for f in glob.glob("**/*tts_generation_results*.json", recursive=True) if not f.startswith(".venv"))
    rows = []
    for f in files:
        rows += census.rows_from_results(f)
    return rows


def run(args):
    rows = build_rows()
    items = []
    for r in rows:
        items.append({"kind": "primary", "c": r["canonical"], "a": r["asr"], "seg": r["seg"], "kp": bool(r["kp"]), "src": r["src"],
                      "attempt": r.get("attempt"), "stored_cls": r.get("stored_cls"), "final_status": r.get("final_status")})
        if r.get("azure"):
            items.append({"kind": "azure", "c": r["canonical"], "a": r["azure"], "seg": r["seg"], "kp": bool(r["kp"]), "src": r["src"],
                          "attempt": r.get("attempt"), "stored_cls": r.get("stored_cls"), "final_status": r.get("final_status")})
    cache = {}
    pass_to_ng, ng_to_pass, blocked = [], [], []
    stats = collections.Counter()
    for it in items:
        key = (it["c"], it["a"], it["seg"], it["kp"])
        if key not in cache:
            off = judge_off(it["c"], it["a"], it["seg"], it["kp"])
            on = judge_on(it["c"], it["a"], it["seg"], it["kp"], off)
            cache[key] = (off, on)
        off, on = cache[key]
        it["off"], it["on"] = off, on
        stats["items"] += 1
        stats["off_pass"] += int(off["final_ok"])
        stats["on_pass"] += int(on["final_ok"])
        if off["final_ok"] and not on["final_ok"]:
            pass_to_ng.append(it)
        if (not off["final_ok"]) and on["final_ok"]:
            it["family"] = family_of(it["src"])
            it["wav"] = find_wav(it["src"], it["seg"], it["attempt"])
            ng_to_pass.append(it)
        if (not off["final_ok"]) and (not on["final_ok"]) and on["by"].startswith("er109_blocked"):
            blocked.append(it)
    # 重複(同一canonical/asr/seg)を除いた distinct
    distinct = {}
    for it in ng_to_pass:
        distinct.setdefault((it["c"], it["a"], it["seg"]), it)
    by_family = collections.Counter(x["family"] for x in ng_to_pass)
    by_family_distinct = collections.Counter(x["family"] for x in distinct.values())
    segs = {(x["src"], x["seg"]) for x in ng_to_pass}
    hr = {(x["src"], x["seg"]) for x in ng_to_pass if str(x.get("final_status")) in ("STOPPED", "HUMAN_REVIEW_LOCKED", "HUMAN_REVIEW_REQUIRED")}
    out = {"generated_by": "er109_stored_onoff_compare_01.py", "api_calls": 0, "cost_jpy": 0, "layer_version": e109.LAYER_VERSION,
           "flag": "er109 ORTHOGRAPHIC_EQUIVALENCE_ENABLED は未配線・既定OFF。ONは本harnessが直接er109を呼ぶオフラインモデル",
           "summary": {"rows_primary": sum(1 for i in items if i["kind"] == "primary"), "items_total(primary+azure)": stats["items"],
                       "distinct_judgments": len(cache), "off_pass": stats["off_pass"], "on_pass": stats["on_pass"],
                       "PASS_to_NG": len(pass_to_ng), "NG_to_PASS_items": len(ng_to_pass), "NG_to_PASS_distinct_pairs": len(distinct),
                       "NG_to_PASS_distinct_segments": len(segs), "NG_to_PASS_segments_final_stopped_or_hr": len(hr),
                       "NG_to_PASS_by_family(items)": dict(by_family), "NG_to_PASS_by_family(distinct pairs)": dict(by_family_distinct),
                       "er109_equiv_but_blocked_by_final_gate(P-06)": len(blocked)},
           "PASS_to_NG_items": pass_to_ng, "NG_to_PASS": ng_to_pass, "blocked_by_final_gate": blocked}
    json.dump(out, open(args.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(out["summary"], ensure_ascii=False, indent=1))
    for x in list(distinct.values())[:60]:
        print(x["family"], "|", x["kind"], x["seg"], "|", repr(x["c"][:70]), "|", repr(x["a"][:70]), "|", x["on"].get("rules"), x["on"].get("warnings"), "| wav" if x["wav"] else "| no-wav")
    if args.whisper:
        whisper_pass(out, args.out)


def whisper_pass(out, path):
    import er104_kp_three_asr_vote_01 as k3
    res = []
    seen = set()
    for x in out["NG_to_PASS"]:
        w = x.get("wav")
        if not w or (w, x["c"]) in seen:
            continue
        seen.add((w, x["c"]))
        try:
            t = k3.whisper_transcribe(w)
        except Exception as e:
            res.append({"wav": w, "canonical": x["c"], "error": f"{type(e).__name__}: {e}"})
            continue
        eq = e109.evaluate(x["c"], t)
        cls = val.classify_asr_match(x["c"], t, segment_id=(None if x["kp"] else x["seg"]))
        alt = None if cls.should_pass else S._step_alternate_pass(cls)
        res.append({"wav": w, "canonical": x["c"], "stored_asr": x["a"], "whisper": t, "family": x["family"],
                    "whisper_off_pass": bool(cls.should_pass or alt), "whisper_e109_equiv": eq.equivalent, "verdict": eq.verdict,
                    "rules": eq.rules, "warnings": eq.warnings})
    out["whisper_recheck"] = res
    out["whisper_recheck_summary"] = {"wavs": len(res), "whisper_e109_equiv_or_off_pass": sum(1 for r in res if r.get("whisper_e109_equiv") or r.get("whisper_off_pass")),
                                      "whisper_not_supported": [r for r in res if "whisper_e109_equiv" in r and not (r["whisper_e109_equiv"] or r["whisper_off_pass"])][:50]}
    json.dump(out, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in out["whisper_recheck_summary"].items() if k != "whisper_not_supported"}, ensure_ascii=False))
    for r in res:
        print("WHISPER", r.get("family"), repr(r["canonical"][:60]), "|", repr((r.get("whisper") or "")[:60]), "| off", r.get("whisper_off_pass"), "e109", r.get("whisper_e109_equiv"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="docs/research/ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01/stored_onoff_compare_02.json")
    ap.add_argument("--whisper", action="store_true")
    run(ap.parse_args())
