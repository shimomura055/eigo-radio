# ============================================================
# er108_kp_noguard_reeval_01.py  (API 0 / 費用0 / 研究用script。Production参照なし=import先を読むだけで編集しない)
# KP-QUALITY-IMPROVEMENT-2ITEMS-PRODUCTION-01 委任_01 成果物4: 保存音声84件+coffee/small_bag 12本を、本番adapter経路
# (er104_kp_vote_reuse_01.evaluate_vote -> er006 evaluate_attempt_with_cascade_detail, vote_required=True)で再判定する。
# 『数値・否定保護の解除』は、このprocess内でのみ er078 `_protected` を差し替えて模擬する(ファイルは編集しない)。
#   baseline = 現行(保護あり)   A = 値DIFF/否定差を解除(AMBIGUOUSは維持)   B = 値ガード・否定ガードを全て解除(AMBIGUOUSも解除)
# 使い方: .venv\Scripts\python.exe er108_kp_noguard_reeval_01.py --out <json>
# ============================================================
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, ".")
import er006_secondary_asr_01 as sec
import er078_asr_unified_judge_01 as uj
import importlib

kp3v = importlib.import_module("er104_kp_three_asr_vote_01")   # `import er104_`字面を避ける理由はer108_kp_vote_noguard_01.py参照
kv = importlib.import_module("er104_kp_vote_reuse_01")
r2 = importlib.import_module("er104_stored_audio_reeval_02")

EVID = "docs/research/FAMILY-X-KP-AUDIO-NG3-EVIDENCE-01/evidence_data_01.json"
_ORIG = uj._protected
_NO = uj.vg.ValueGuardResult(uj.vg.NO_VALUES)


def _patched(variant):
    def f(canonical, text, lang):
        vgr, neg = _ORIG(canonical, text, lang)
        if variant == "baseline":
            return vgr, neg
        if variant == "A":
            if vgr.kind == uj.vg.DIFF:
                return uj.vg.ValueGuardResult(uj.vg.NO_VALUES, warnings=vgr.warnings), False
            return vgr, False
        return _NO, False        # B
    return f


def coffee_rows():
    d = json.load(open(EVID, encoding="utf-8"))
    out = []
    for c in d["cases"]:
        for r in c["rows"]:
            out.append((c["id"], c["kp"], f"{c['id']}#{r['attempt']}", r["wav"].replace("\\", "/"), r["primary_text"], r["azure_text"]))
    return out


def run(variant):
    uj._protected = _patched(variant)
    rows = []
    for corpus, fn in (("er091_kp39", r2.corpus_er091), ("byus_survey7", r2.corpus_survey), ("take_part", r2.corpus_take_part),
                       ("er096_stats24", r2.corpus_stats_attempts)):
        rows += fn()
    for cid, kp, rid, wav, p, s in coffee_rows():
        rows.append(r2.evaluate("ng3_" + cid, rid, kp, "ng3_case", wav, p, s, note="NG3 evidence"))
    uj._protected = _ORIG
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    sec.get_full_text_via_azure_stt_with_phrase_list = r2._no_azure
    sec.semantic_equivalence.append_telemetry_log = lambda *x, **k: None
    kp3v.reset_whisper_state()
    res = {v: run(v) for v in ("baseline", "A", "B")}
    keyf = lambda r: (r["corpus"], r["id"])
    base = {keyf(r): r for r in res["baseline"]}
    table = []
    for r in res["baseline"]:
        k = keyf(r)
        a_ = {keyf(x): x for x in res["A"]}[k]
        b_ = {keyf(x): x for x in res["B"]}[k]
        table.append({"corpus": r["corpus"], "id": r["id"], "canonical": r["canonical"], "label": r["label"], "note": r["note"],
                      "p": r["primary"]["text"], "s": r["secondary"]["text"],
                      "base": r["adapter"]["verified"], "base_state": r["adapter"]["vote_state"], "base_row": r["adapter"]["row"],
                      "A": a_["adapter"]["verified"], "A_state": a_["adapter"]["vote_state"], "A_row": a_["adapter"]["row"],
                      "A_whisper": a_["adapter"]["whisper_text"], "B": b_["adapter"]["verified"], "B_state": b_["adapter"]["vote_state"],
                      "B_row": b_["adapter"]["row"], "B_whisper": b_["adapter"]["whisper_text"]})
    out = {"generated_by": "er108_kp_noguard_reeval_01.py", "api_calls": 0, "cost_jpy": 0,
           "azure_real_calls_total": sum(r["adapter"]["azure_real_calls"] for v in res.values() for r in v),
           "n_rows": len(table),
           "changed_A": [t for t in table if t["base"] != t["A"]], "changed_B": [t for t in table if t["base"] != t["B"]],
           "table": table}
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(out, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("rows", len(table), "changed A", len(out["changed_A"]), "changed B", len(out["changed_B"]), "azure real", out["azure_real_calls_total"])


if __name__ == "__main__":
    main()
