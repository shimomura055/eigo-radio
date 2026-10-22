# er109_gate_exposure_01.py
# ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01 委任_01: 『分類(classify_asr_match)は承認済み規則でPASSなのに、非KPの最終ANDゲート(値DIFF/否定差)が
# 同一発音の表記差を保護差と誤判定してNG_PROTECTEDにする』件数を、機械生成の正例(発音同一の異表記)で測る。API 0・ローカル。
# 非KP本文のみ対象(KPは2026-10-22に保護解除済み)。承認済みequivalence_basis(Tier1/数字ゲート例外)は本物のjudgeと同じくゲートをskip。
import argparse
import collections
import json
import sys

sys.path.insert(0, ".")
import er006_preprod_hardening_01_validation as val
import er006_secondary_asr_01 as S
import er078_asr_unified_judge_01 as uj
import er109_machine_pairs_eval_01 as mp


def run(n_body=700):
    body = mp.load_body_sentences(n_body)
    blocked, tot, pass_cls = [], 0, 0
    by_cat = collections.Counter()
    for c in body:
        for g in mp.POS_GENS:
            r = g(c)
            if not r:
                continue
            a, cat = r
            tot += 1
            cls = val.classify_asr_match(c, a, segment_id="full_story_part1")
            alt = None if cls.should_pass else S._step_alternate_pass(cls)
            if not (cls.should_pass or alt):
                continue
            pass_cls += 1
            basis = S._equivalence_basis_of(cls) if cls.should_pass else None
            if basis in uj.APPROVED_EQUIVALENCE_BASES:
                continue
            vgr, neg = uj._protected(c, a, "en")
            if vgr.kind == uj.vg.DIFF or neg:
                by_cat[cat] += 1
                blocked.append({"canonical": c, "asr": a, "cat": cat, "label": cls.classification if cls.should_pass else alt,
                                "value_guard": vgr.kind, "reasons": list(vgr.reasons)[:2], "negation_diff": bool(neg)})
    return {"positives_generated": tot, "classify_or_homophone_pass": pass_cls, "blocked_by_final_gate": len(blocked),
            "blocked_by_category": dict(by_cat)}, blocked


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="docs/research/ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01/gate_exposure_01.json")
    a = ap.parse_args()
    s, b = run()
    json.dump({"generated_by": "er109_gate_exposure_01.py", "api_calls": 0, "cost_jpy": 0, "summary": s, "blocked": b},
              open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(s, ensure_ascii=False, indent=1))
    for x in b[:25]:
        print(x["cat"], "|", repr(x["canonical"][:80]), "|", repr(x["asr"][:80]), "|", x["label"], x["reasons"])
