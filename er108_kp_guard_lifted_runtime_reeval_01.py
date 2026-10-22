# ============================================================
# er108_kp_guard_lifted_runtime_reeval_01.py  (API 0 / 費用0 / 研究・runtime evidence用script。Productionからimportされない)
# KP-QUALITY-IMPROVEMENT-2ITEMS-PRODUCTION-01 委任_02 ①-(a): 保存音声(coffee `pump one's fist` 8本 + KP3V保存84件)を、
# **配線後の本番adapter経路をmonkeypatchなしで**再判定する(er104_kp_vote_reuse_01.evaluate_vote -> er006 evaluate_attempt_with_cascade_detail,
# vote_required=True)。Whisperは保存音声へのlocalな実転写(faster-whisper small int8、API 0)。Azureは保存転写の再生(新規呼出0)。
# 比較対象 = 委任_01の noguard_reeval_01.json の `base`(保護解除前の現行Production判定。保存済み結果)。
# 使い方: .venv\Scripts\python.exe er108_kp_guard_lifted_runtime_reeval_01.py --out <json>
# ============================================================
from __future__ import annotations

import argparse
import importlib
import json
import os
import sys

sys.path.insert(0, ".")
import er006_secondary_asr_01 as sec

kp3v = importlib.import_module("er104_kp_three_asr_vote_01")
r2 = importlib.import_module("er104_stored_audio_reeval_02")

EVID = "docs/research/FAMILY-X-KP-AUDIO-NG3-EVIDENCE-01/evidence_data_01.json"
PREV = "docs/research/KP-QUALITY-IMPROVEMENT-2ITEMS-PRODUCTION-01/noguard_reeval_01.json"


def coffee_rows():
    d = json.load(open(EVID, encoding="utf-8"))
    out = []
    for c in d["cases"]:
        for r in c["rows"]:
            out.append((c["id"], c["kp"], f"{c['id']}#{r['attempt']}", r["wav"].replace("\\", "/"), r["primary_text"], r["azure_text"]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    sec.get_full_text_via_azure_stt_with_phrase_list = r2._no_azure
    sec.semantic_equivalence.append_telemetry_log = lambda *x, **k: None
    kp3v.reset_whisper_state()
    rows = []
    for corpus, fn in (("er091_kp39", r2.corpus_er091), ("byus_survey7", r2.corpus_survey), ("take_part", r2.corpus_take_part),
                       ("er096_stats24", r2.corpus_stats_attempts)):
        rows += fn()
    for cid, kp, rid, wav, p, s in coffee_rows():
        rows.append(r2.evaluate("ng3_" + cid, rid, kp, "ng3_case", wav, p, s, note="NG3 evidence"))
    prev = {(t["corpus"], t["id"]): t for t in json.load(open(PREV, encoding="utf-8"))["table"]}
    table = []
    for r in rows:
        k = (r["corpus"], r["id"])
        pv = prev.get(k)
        ad = r["adapter"]
        table.append({"corpus": r["corpus"], "id": r["id"], "canonical": r["canonical"], "p": r["primary"]["text"], "s": r["secondary"]["text"],
                      "old_verified": (pv or {}).get("base"), "old_state": (pv or {}).get("base_state"),
                      "new_verified": ad["verified"], "new_state": ad["vote_state"], "new_row": ad["row"], "whisper_text": ad["whisper_text"],
                      "azure_real_calls": ad["azure_real_calls"]})
    changed = [t for t in table if t["old_verified"] is not None and t["old_verified"] != t["new_verified"]]
    false_pass = [t for t in changed if t["new_verified"] and not t["old_verified"] and t["corpus"] != "ng3_case" and not t["corpus"].startswith("ng3_")]
    out = {"generated_by": "er108_kp_guard_lifted_runtime_reeval_01.py", "api_calls": 0, "cost_jpy": 0, "n_rows": len(table),
           "azure_real_calls_total": sum(t["azure_real_calls"] for t in table),
           "changed": changed, "n_changed": len(changed), "non_ng3_new_pass_count": len(false_pass), "table": table}
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    json.dump(out, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("rows", len(table), "changed", len(changed), "non-ng3 new pass", len(false_pass), "azure real", out["azure_real_calls_total"])
    for t in changed:
        print(t["id"], t["p"], "|", t["s"], t["old_state"], "->", t["new_state"], t["new_row"], t["whisper_text"])


if __name__ == "__main__":
    main()
