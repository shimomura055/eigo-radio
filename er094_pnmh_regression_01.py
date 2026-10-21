"""PNMH-01 A-2: 4,032ペア(pairs_02、golden_mdjf 191+runtime fixture等を含む)のshould_pass/classification before/after差分表。API 0。
mode=head: git HEAD版(配線前)のval/secを一時dirから読み込む(env PNMH_HEAD_DIR) / off: 配線後コード+MULTIWORD_HOMOPHONE_ENABLED=False / on: 既定。
出力JSON=各ペアの (classification, should_pass, final(alternate_pass込み), content_word_diffs repr, steps相当)。
実行: PNMH_HEAD_DIR=<dir> .venv/Scripts/python.exe er094_pnmh_regression_01.py --mode head|off|on --out <json>"""
import argparse, json, os, sys
ROOT = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser(); ap.add_argument("--mode", required=True); ap.add_argument("--out", required=True)
a = ap.parse_args()
if a.mode == "head":
    sys.path.insert(0, os.environ["PNMH_HEAD_DIR"])
sys.path.insert(1 if a.mode == "head" else 0, ROOT)
import er006_preprod_hardening_01_validation as val
import er006_secondary_asr_01 as sec
import er021_en_asr_semantic_equivalence_production_01 as se
se.append_telemetry_log = lambda *x, **k: None
if a.mode == "head":
    assert "multiword" not in open(val.__file__, encoding="utf-8").read().lower(), val.__file__
else:
    import er094_multiword_homophone_01 as mw
    mw.MULTIWORD_HOMOPHONE_ENABLED = (a.mode == "on")
PAIRS = os.path.join(ROOT, "docs", "research", "PROPER-NOUN-PRONUNCIATION-MULTIWORD-HOMOPHONE-PLAN-01", "pairs_02.jsonl")
rows = []
for l in open(PAIRS, encoding="utf-8"):
    p = json.loads(l)
    try:
        r = val.classify_asr_match(p["canonical"], p["asr"])
    except Exception as e:
        rows.append({"err": repr(e)}); continue
    final = "PASS" if r.should_pass else None
    if final is None and (sec.is_entity_like_mismatch(r) or sec.is_homophone_candidate_mismatch(r)):
        lab = sec._step_alternate_pass(r)
        if lab:
            final = "PASS:" + lab
    rows.append({"classification": r.classification, "should_pass": bool(r.should_pass), "final": final or "NOT_PASS",
                 "diffs": json.dumps(r.protected.content_word_diffs, ensure_ascii=False, sort_keys=True)})
json.dump(rows, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=0, sort_keys=True)
print(a.mode, len(rows), "errors:", sum(1 for r in rows if "err" in r))
