# -*- coding: utf-8 -*-
"""ITEM1 委任_05 G: run_e2e_03(a2)の永続化済みartifactに対し、決定論の人称語突合がオフライン(API 0)で不整合を検出することを示す。
read-onlyで、run_e2e_03の成果物は一切書き換えない(読取前後のshaを記録して不変を確認)。"""
import hashlib, json, os, sys
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, REPO)
import er003_key_words_gloss_alignment as ga

RUN = os.path.join(REPO, "er026_output", "family_z_production_e2e_01", "melos", "run_e2e_03")
files = [os.path.join(RUN, "key_phrases", "a2", "keywords_canonicalized.json"),
         os.path.join(RUN, "a2", "key_phrases", "keywords_canonicalized.json"),
         os.path.join(RUN, "key_phrases", "b1b", "keywords_canonicalized.json"),
         os.path.join(RUN, "key_phrases", "a2_result.json")]
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
before = {p: sha(p) for p in files}
out = {"run": RUN, "files": {}}
for p in files[:3]:
    doc = json.load(open(p, encoding="utf-8"))
    items = doc.get("items") or []
    mism = ga.select_person_mismatches(items)
    out["files"][os.path.relpath(p, REPO)] = {
        "consumer_unevaluated_ranks": [x["rank"] for x in ga.collect_unevaluated(doc)],
        "person_mismatches": [{"rank": x["rank"], "key_phrase": x["key_phrase"], "japanese_gloss": x["japanese_gloss"],
                               "reason": ga.person_reference_mismatch(x["key_phrase"], x["japanese_gloss"])} for x in mism],
        "generation_targets_ranks": [x["rank"] for x in ga.select_generation_targets(items)],
        "person_generalized_ranks": [x["rank"] for x in items if ga.is_person_generalized(x)]}
after = {p: sha(p) for p in files}
out["artifacts_unchanged"] = before == after
out["sha256_before"] = {os.path.relpath(p, REPO): v for p, v in before.items()}
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "item1_melos_offline_detect_05_result.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print(json.dumps(out, ensure_ascii=False, indent=1))
