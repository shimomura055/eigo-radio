# -*- coding: utf-8 -*-
"""ASR-PHONETIC-EQUIVALENCE-M1-F1-PRODUCTION-WIRING-01 委任_02: F1(連結発音Validatorの『最初の食い違いだけ見て全文PASS』)是正案の
影響事前集計。既存データのみ read-only / API 0 / JPY0。Production code は import するだけ(F1案は本ファイル内のプロトタイプで
csv3.classify_connected_speech をプロセス内だけ差し替えて評価。ファイルは無変更)。共有 telemetry へは書かない(er068 import で no-op 化)。"""
import argparse, collections, difflib, json, os, sys
sys.path.insert(0, os.getcwd())
import er068_asr_phonetic_equivalence_generalization_01_offline as O  # noqa: F401 (telemetry no-op化)
import er006_preprod_hardening_01_validation as val
import er011_b1_connected_speech_validator_01 as csv3

_ORIG = csv3.classify_connected_speech
OK_J = ("CONNECTED_SPEECH_ACCEPT", "CONNECTED_SPEECH_RESEGMENTATION")
UNCL = "UNCLASSIFIED_FALLS_THROUGH_TO_EXISTING"


def f1_classify(canonical: str, asr: str) -> dict:
    """F1案: 全位置の食い違いを列挙し、各食い違いを既存 Pattern A/B/C(変更なし)で個別判定。説明不能が1つでも残れば UNCLASSIFIED。"""
    cw, aw = csv3.tokenize(canonical), csv3.tokenize(asr)
    sm = difflib.SequenceMatcher(a=[w.lower() for w in cw], b=[w.lower() for w in aw], autojunk=False)
    diffs = [(t, i1, i2, j1, j2) for t, i1, i2, j1, j2 in sm.get_opcodes() if t != "equal"]
    if not diffs:
        return _ORIG(canonical, asr)
    first = _ORIG(canonical, asr)  # 既存の戻り値形式(diff 等)を維持
    results, residual = [], []

    def benign(cspan, aspan):
        """連結発音で説明できない差分を『既存の通常Validator(protected_check)』で判定: 内容語差・数字・否定の不一致が無ければ(機能語のみの差/
        規則的な単複の揺れ=既存が元々吸収する差)残差としない。"""
        pc = val.protected_check([w.lower() for w in cspan], [w.lower() for w in aspan])
        return pc.passed and not pc.content_word_diffs

    for t, i1, i2, j1, j2 in diffs:
        if (i2 - i1) == (j2 - j1) and i2 > i1:
            for k in range(i2 - i1):
                r = _ORIG(" ".join(cw[i1 + k:]), " ".join(aw[j1 + k:]))
                if r["new_judgment"] in OK_J and (r.get("diff") or {}).get("index") == 0:
                    results.append(r)
                elif not benign(cw[i1 + k:i1 + k + 1], aw[j1 + k:j1 + k + 1]):
                    residual.append({"op": "replace", "canonical": [cw[i1 + k]], "asr": [aw[j1 + k]]})
        elif not benign(cw[i1:i2], aw[j1:j2]):
            residual.append({"op": t, "canonical": cw[i1:i2], "asr": aw[j1:j2]})
    out = dict(first)
    out["f1_all_diffs"] = len(diffs)
    out["f1_residual"] = residual
    if residual or not results:
        out["new_judgment"] = UNCL
        out["rule"] = None
        return out
    out["new_judgment"] = "CONNECTED_SPEECH_RESEGMENTATION" if any(r["new_judgment"] == "CONNECTED_SPEECH_RESEGMENTATION" for r in results) else "CONNECTED_SPEECH_ACCEPT"
    out["rule"] = "+".join(sorted({r["rule"] for r in results}))
    out["expected_phoneme_boundary"] = " | ".join(r["expected_phoneme_boundary"] for r in results)
    return out


def judge(c, a, seg="full_story_part1", patched=False):
    csv3.classify_connected_speech = f1_classify if patched else _ORIG
    try:
        r = val.classify_asr_match(c, a, segment_id=seg)
    finally:
        csv3.classify_connected_speech = _ORIG
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
    excl = set(range(7155, 9153)) | set(range(9177, 9180))  # 1-based 7156-9153 / 9178-9180 除外
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
    return pairs, {"attempt_history_has_text_records": ah_text, "attempt_history_keys": dict(ah_keys.most_common(12))}


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--no-telemetry", action="store_true", required=True)
    a = ap.parse_args()
    pairs, meta = load_pairs()
    rows, trans = [], collections.Counter()
    for (c, asr), src in pairs.items():
        try:
            o = judge(c, asr)
            n = judge(c, asr, patched=True)
        except Exception as e:  # pragma: no cover
            rows.append({"src": src, "error": str(e)[:100]})
            continue
        trans[(o.classification, n.classification, o.should_pass, n.should_pass)] += 1
        if (o.classification, o.should_pass) != (n.classification, n.should_pass):
            fr = f1_classify(c, asr)
            rows.append({"src": src, "canonical": c, "asr": asr, "old": o.classification, "new": n.classification,
                         "old_pass": o.should_pass, "new_pass": n.should_pass,
                         "old_rule": (o.connected_speech_info or {}).get("rule"), "residual": fr.get("f1_residual")})
    changed = [r for r in rows if "error" not in r]
    ctr = []
    for ce, ae, exp in COUNTER:
        o = judge(ce, ae)
        n = judge(ce, ae, patched=True)
        ctr.append({"canonical": ce, "asr": ae, "expect": exp, "old": [o.classification, o.should_pass], "new": [n.classification, n.should_pass],
                    "old_rule": (o.connected_speech_info or {}).get("rule")})
    lab, lab_changed = labeled_sets()
    old_cs = sum(v for k, v in trans.items() if k[0].startswith("CONNECTED_SPEECH") and k[2])
    summ = {"n_pairs": len(pairs), "by_src": dict(collections.Counter(pairs.values())), "meta": meta,
            "errors": sum(1 for r in rows if "error" in r),
            "old_pass_via_connected_speech": old_cs, "pass_to_nonpass": sum(1 for r in changed if r["old_pass"] and not r["new_pass"]),
            "nonpass_to_pass": sum(1 for r in changed if (not r["old_pass"]) and r["new_pass"]),
            "other_class_change_same_pass": sum(1 for r in changed if r["old_pass"] == r["new_pass"]),
            "transitions": {f"{k[0]}->{k[1]}|{k[2]}->{k[3]}": v for k, v in trans.items() if k[0] != k[1] or k[2] != k[3]},
            "labeled_sets": lab, "api_calls": 0}
    os.makedirs(a.out_dir, exist_ok=True)
    json.dump({"summary": summ, "changed": changed, "labeled_changed": lab_changed, "counterexamples": ctr}, open(os.path.join(a.out_dir, "f1_census_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(summ, ensure_ascii=False, indent=1))
    for r in changed:
        print("CHG", r["src"], r["old"], "->", r["new"], "|", r["canonical"][:200], "|", r["asr"][:200], "|", r["residual"])
    for r in lab_changed:
        print("LAB", r["truth"], r["old"], "->", r["new"], "|", r["canonical"][:160], "|", r["asr"][:160])
    for c in ctr:
        print("CTR", c["expect"], c["old"], c["new"], c["old_rule"], "|", c["canonical"], "|", c["asr"])


if __name__ == "__main__":
    main()
