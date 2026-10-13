# -*- coding: utf-8 -*-
"""ASR-PHONETIC-EQUIVALENCE-M1-F1-PRODUCTION-WIRING-01 委任_02: F1(連結発音Validatorの『最初の食い違いだけ見て全文PASS』)是正案の
影響事前集計。既存データのみ read-only / API 0 / JPY0。Production code は import するだけ(F1案は本ファイル内のプロトタイプで
csv3.classify_connected_speech をプロセス内だけ差し替えて評価。ファイルは無変更)。共有 telemetry へは書かない(er068 import で no-op 化)。"""
import argparse, collections, difflib, json, os, re, sys
sys.path.insert(0, os.getcwd())
import er068_asr_phonetic_equivalence_generalization_01_offline as O  # noqa: F401 (telemetry no-op化)
import er006_preprod_hardening_01_validation as val
import er011_b1_connected_speech_validator_01 as csv3

OK_J = ("CONNECTED_SPEECH_ACCEPT", "CONNECTED_SPEECH_RESEGMENTATION")
UNCL = "UNCLASSIFIED_FALLS_THROUGH_TO_EXISTING"


_OLD = csv3._classify_first_diff  # F1前の挙動(Pattern判定本体・無変更)
_NEW = csv3.classify_connected_speech  # Production F1版


def f1_classify(canonical: str, asr: str) -> dict:
    return _NEW(canonical, asr)


def judge(c, a, seg="full_story_part1", patched=False):
    """patched=False: F1前(_classify_first_diff差替)/ True: Production F1版を直接呼ぶ。seg=None でdialogue相当(segment_id=None)。"""
    csv3.classify_connected_speech = _NEW if patched else _OLD
    try:
        r = val.classify_asr_match(c, a, segment_id=seg)
    finally:
        csv3.classify_connected_speech = _NEW
    return r


def load_pairs():
    pairs = {}

    def add(c, a, src):
        if c and a and c.strip() != a.strip():
            pairs.setdefault((c, a), src)
    for l in open("er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl", encoding="utf-8"):
        try:
            d = json.loads(l)
        except Exception:
            continue
        for s in d.get("steps", []):
            add(d.get("canonical_text"), s.get("text"), "human_review_queue")
    excl = set(range(7155, 9153)) | set(range(9177, 9180)) | set(range(9195, 9200))  # 1-based 7156-9153 / 9178-9180 除外
    for n, l in enumerate(open("er021_output/en_asr_semantic_equivalence_production_wiring_01/telemetry.jsonl", encoding="utf-8")):
        if n in excl:
            continue
        try:
            d = json.loads(l)
        except Exception:
            continue
        add(d.get("canonical"), d.get("asr"), "er021_telemetry")
    ah_keys, ah_text = collections.Counter(), 0
    for l in open("er011_output/attempt_history.jsonl", encoding="utf-8"):
        try:
            d = json.loads(l)
        except Exception:
            continue
        ah_keys.update(d.keys())
        if d.get("canonical_text") or d.get("canonical") or d.get("asr_text"):
            ah_text += 1
    r = json.load(open("er069_output/attribution_clip_split_trial_01/results_02.json", encoding="utf-8"))["rows"]
    for x in r:
        for eng in ("openai", "azure"):
            add(x["text"], x[eng].get("text"), "er069_results_02")
    kp_n = 0
    import glob
    for pth in glob.glob("er019_output/**/tts_generation_results.json", recursive=True) + glob.glob("er026_output/**/tts_generation_results.json", recursive=True):
        try:
            d = json.load(open(pth, encoding="utf-8"))
        except Exception:
            continue
        for name, seg in (d.get("segments") or {}).items():
            if not isinstance(seg, dict) or not any(k in name.lower() for k in ("key_phrase", "kp_")):
                continue
            before = len(pairs)
            add(seg.get("text"), seg.get("asr_text"), "kp_tts_generation_results")
            for at in seg.get("attempts_log") or []:
                add(seg.get("text"), at.get("asr_text"), "kp_tts_generation_results")
            kp_n += len(pairs) - before
    return pairs, {"kp_pairs_added": kp_n, "attempt_history_has_text_records": ah_text, "attempt_history_keys": dict(ah_keys.most_common(12))}


COUNTER = [  # (canonical, asr, 期待: nonpass=非PASSであるべき / pass=PASSのまま)
    ("The studies suggest cats today.", "The study suggests dogs today.", "nonpass"),
    ("The studies suggest cats today.", "The study suggests cats today.", "pass"),
    ("The studies suggest cats today.", "The study suggest cats today.", "pass"),
    ("The studies suggest that cats sleep.", "The study suggests that cats sleep.", "pass"),
    ("The studies suggest that cats sleep.", "The study suggests that dogs sleep.", "nonpass"),
    ("The studies suggest that cats sleep.", "The study suggests that cats sleep more.", "nonpass"),
    ("The studies suggest that cats sleep.", "The study suggests cats sleep.", "nonpass"),
    ("The studies suggest that cats sleep.", "The study suggests that cats did not sleep.", "nonpass"),
    ("The studies suggest that cats sleep.", "The study suggests that cats slept.", "nonpass"),
    ("The studies suggest that 5 cats sleep.", "The study suggests that 6 cats sleep.", "nonpass"),
    ("The studies suggest that Rex sleeps.", "The study suggests that Max sleeps.", "nonpass"),
    ("The studies suggest that cats sleep.", "The study suggests that cats.", "nonpass"),
    ("The company opened today and it closed to the public.", "The company open today and it closed to the public.", "pass"),
    ("The company opened today and it closed to the public.", "The company open today and it closes to the public.", "nonpass"),
    ("The company opened today and it closed to the public.", "The company open today and it closed to the people.", "nonpass"),
    ("The survey suggests that cats sleep.", "The surveys suggest that cats sleep.", "pass?"),
    ("The survey suggests that cats sleep.", "The surveys suggest that dogs sleep.", "nonpass"),
    ("Their studies suggest cats and their survey suggests cats.", "Their study suggests cats and their surveys suggest cats.", "pass"),
    ("Their studies suggest cats and their survey suggests cats.", "Their study suggests cats and their surveys suggest dogs.", "nonpass"),
]


def labeled_sets():
    """既存の真値付きデータ(er068 の読取専用ローダ)で、F1案の『欠陥→PASS(誤PASS)』『正常→非PASS(誤NG)』を算出する。"""
    recs = []
    for fn in ("ds_cs_audit_sweeps", "ds_text_sets", "ds_general_windows", "ds_real_diff_instances"):
        try:
            recs += getattr(O, fn)()
        except Exception as e:  # pragma: no cover
            recs.append({"ds": "LOAD_ERROR_" + fn, "canonical": "", "asr": "", "truth": "?", "err": str(e)[:80]})
    agg = collections.defaultdict(lambda: collections.Counter())
    changed = []
    for r in recs:
        if not r.get("canonical") or not r.get("asr"):
            continue
        o = judge(r["canonical"], r["asr"])
        n = judge(r["canonical"], r["asr"], patched=True)
        key = (r["ds"].split("_")[0] + "_" + r["ds"].split("_")[1] if "_" in r["ds"] else r["ds"], r["truth"])
        agg[key]["n"] += 1
        agg[key]["old_pass"] += int(o.should_pass)
        agg[key]["new_pass"] += int(n.should_pass)
        if o.should_pass != n.should_pass:
            changed.append({"ds": r["ds"], "truth": r["truth"], "canonical": r["canonical"], "asr": r["asr"], "old": o.classification, "new": n.classification})
    return {f"{k[0]}|{k[1]}": dict(v) for k, v in agg.items()}, changed


def _acronym(text):
    return bool(re.search(r"[A-Z]{2,}", text or ""))


def run_pairs(pairs, seg):
    rows, trans = [], collections.Counter()
    for (c, asr), src in pairs.items():
        try:
            o = judge(c, asr, seg=seg)
            n = judge(c, asr, seg=seg, patched=True)
        except Exception as e:  # pragma: no cover
            rows.append({"src": src, "error": str(e)[:100]})
            continue
        trans[(o.classification, n.classification, o.should_pass, n.should_pass)] += 1
        if (o.classification, o.should_pass) != (n.classification, n.should_pass):
            ci = n.connected_speech_info or {}
            rows.append({"src": src, "canonical": c, "asr": asr, "old": o.classification, "new": n.classification,
                         "old_pass": o.should_pass, "new_pass": n.should_pass,
                         "old_rule": (o.connected_speech_info or {}).get("rule"),
                         "residual": ci.get("f1_residual"), "residual_kind": ci.get("f1_residual_kind"),
                         "acronym_in_canonical": _acronym(c)})
    changed = [r for r in rows if "error" not in r]
    return {"segment_id": seg, "errors": sum(1 for r in rows if "error" in r),
            "old_pass_via_connected_speech": sum(v for k, v in trans.items() if k[0].startswith("CONNECTED_SPEECH") and k[2]),
            "pass_to_nonpass": sum(1 for r in changed if r["old_pass"] and not r["new_pass"]),
            "nonpass_to_pass": sum(1 for r in changed if (not r["old_pass"]) and r["new_pass"]),
            "nonpass_to_nonpass_class_change": sum(1 for r in changed if (not r["old_pass"]) and (not r["new_pass"])),
            "transitions": {f"{k[0]}->{k[1]}|{k[2]}->{k[3]}": v for k, v in trans.items() if k[0] != k[1] or k[2] != k[3]}}, changed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["production"], required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    pairs, meta = load_pairs()
    out = {"n_pairs": len(pairs), "by_src": dict(collections.Counter(pairs.values())), "meta": meta, "api_calls": 0, "mode": a.mode}
    changed_all = {}
    for seg in ("full_story_part1", None):
        summ, ch = run_pairs(pairs, seg)
        out["seg_" + str(seg)] = summ
        changed_all[str(seg)] = ch
    ctr = []
    for seg in ("full_story_part1", None):
        for ce, ae, exp in COUNTER:
            o = judge(ce, ae, seg=seg)
            n = judge(ce, ae, seg=seg, patched=True)
            ctr.append({"segment_id": seg, "canonical": ce, "asr": ae, "expect": exp, "old": [o.classification, o.should_pass],
                        "new": [n.classification, n.should_pass]})
    lab, lab_changed = labeled_sets()
    out["labeled_sets"] = lab
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    json.dump({"summary": out, "changed": changed_all, "labeled_changed": lab_changed, "counterexamples": ctr},
              open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(out, ensure_ascii=False, indent=1))
    for k, ch in changed_all.items():
        for r in ch:
            print("CHG", k, r["src"], r["old"], "->", r["new"], "|", r["canonical"][:200], "|", r["asr"][:200], "|", r["residual"], r["residual_kind"], "ACR" if r["acronym_in_canonical"] else "")
    for r in lab_changed:
        print("LAB", r["truth"], r["old"], "->", r["new"], "|", r["canonical"][:160], "|", r["asr"][:160])
    for c in ctr:
        print("CTR", c["segment_id"], c["expect"], c["old"], c["new"], "|", c["canonical"], "|", c["asr"])


if __name__ == "__main__":
    main()
