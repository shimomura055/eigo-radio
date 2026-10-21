# 無patchの現行Validatorで pairs_02 を判定しダンプ(O1(2)の『提案無効時の出力不変』比較の基準側。別processで実行)。
import sys, os, json
ROOT = os.path.dirname(os.path.abspath(__file__)); os.chdir(ROOT); sys.path.insert(0, ROOT)
import er006_preprod_hardening_01_validation as val
import er006_secondary_asr_01 as sec
import er021_en_asr_semantic_equivalence_production_01 as se
se.append_telemetry_log = lambda *a, **k: None
PAIRS = "docs/research/PROPER-NOUN-PRONUNCIATION-MULTIWORD-HOMOPHONE-PLAN-01/pairs_02.jsonl"
def ser(c, a):
    r = val.classify_asr_match(c, a)
    final = "PASS" if r.should_pass else None
    if final is None and (sec.is_entity_like_mismatch(r) or sec.is_homophone_candidate_mismatch(r)):
        lab = sec._step_alternate_pass(r)
        if lab: final = "PASS:" + lab
    return [r.classification, final or "NOT_PASS", r.should_pass, r.protected.content_word_diffs]
out = [ser(p["canonical"], p["asr"]) for p in map(json.loads, open(PAIRS, encoding="utf8"))]
json.dump(out, open("er093_output/pnmh_trial_01/o1_baseline_unpatched.json", "w", encoding="utf8"), ensure_ascii=False, sort_keys=True)
print(len(out))
