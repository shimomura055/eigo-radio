# ============================================================
# er108_kp_quality_runtime_aggregate_01.py  (read-only / API 0 / 研究・runtime evidence用。Productionからimportされない)
# KP-QUALITY-IMPROVEMENT-2ITEMS-PRODUCTION-01 委任_02: 正式runの出力dirから
#   (P-08a) 全KP vote記録(kp_dual_check / asr_judgement.vote)の `guard_lifted` と、全選定metadata(keywords_runtime_metadata.json)の `cmu_gate` を集計し、
#   ①(自然発火: 保護差を伴う票でWhisperが呼ばれたか) ②(CMU除外・再選定・M2の記録)を抜き出す。
# 使い方: .venv\Scripts\python.exe er108_kp_quality_runtime_aggregate_01.py --out <json> --x-run-dir <dir> ... --z-run-dir <dir> ...
# ============================================================
from __future__ import annotations

import argparse
import glob
import json
import os


def _load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def vote_records_x(run_dir):
    out = []
    for p in sorted(glob.glob(os.path.join(run_dir, "*", "audit", "tts_generation_results.json"))):
        d = _load(p)
        for rank, v in (d.get("key_phrases") or {}).items():
            e = (v or {}).get("english")
            if not isinstance(e, dict):
                continue
            aj = e.get("asr_judgement") or {}
            vt = aj.get("vote") or {}
            chk = e.get("kp_dual_check") or {}
            out.append({"file": p.replace("\\", "/"), "kp": rank, "canonical": e.get("canonical_text"), "status": e.get("status"),
                        "reused": bool(e.get("reused") or e.get("reused_from_previous_run")),
                        "vote_state": vt.get("state"), "row": vt.get("row"), "whisper_called": vt.get("whisper_called"),
                        "guard_lifted_vote": vt.get("guard_lifted"), "observed_protected_diff": vt.get("observed_protected_diff"),
                        "primary": (vt.get("primary") or {}).get("text"), "secondary": (vt.get("secondary") or {}).get("text"),
                        "whisper": (vt.get("whisper") or {}).get("text"),
                        "check_version": chk.get("version"), "check_guard_lifted": chk.get("guard_lifted"), "check_source": chk.get("source")})
    return out


def vote_records_z(run_dir):
    """Zもkey_phrases/<rank>/english構造はXと同じ(<level>/audit/tts_generation_results.json)。"""
    return vote_records_x(run_dir)


def cmu_records(run_dir):
    out = []
    for p in sorted(glob.glob(os.path.join(run_dir, "**", "keywords_runtime_metadata.json"), recursive=True)):
        if "outer_retry" in p.replace("\\", "/"):
            continue
        m = _load(p)
        g = m.get("cmu_gate")
        out.append({"file": p.replace("\\", "/"), "has_cmu_gate": g is not None, "version": (g or {}).get("version"),
                    "cmudict": ((g or {}).get("lexicon") or {}).get("package_cmudict"),
                    "entries": ((g or {}).get("lexicon") or {}).get("entries"),
                    "attempts_with_cmu_reason": (g or {}).get("attempts_with_cmu_reason"), "excluded": (g or {}).get("excluded"),
                    "selection_attempts": m.get("attempts"), "final_status": m.get("final_status"), "shortfall": m.get("shortfall"),
                    "cmu_item_reasons": [{"attempt": a.get("attempt"), "reasons": a.get("item_reasons")} for a in (m.get("attempts_detail") or [])
                                         if any("CMU" in r for ir in (a.get("item_reasons") or []) for r in ir.get("reasons", []))]})
    return out


def outer_retry_records(run_dir):
    out = []
    for p in sorted(glob.glob(os.path.join(run_dir, "**", "outer_retry_log.json"), recursive=True)):
        l = _load(p)
        out.append({"file": p.replace("\\", "/"), "attempts": [
            {"outer_attempt": a.get("outer_attempt"), "selection_phrases": a.get("selection_phrases"),
             "canonicalization_status": a.get("canonicalization_status"), "cmu_post_canon": a.get("cmu_post_canon")} for a in l.get("attempts", [])]})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--x-run-dir", action="append", default=[])
    ap.add_argument("--z-run-dir", action="append", default=[])
    a = ap.parse_args()
    res = {"x": {}, "z": {}}
    for d in a.x_run_dir:
        res["x"][d] = {"vote": vote_records_x(d), "cmu": cmu_records(d), "outer_retry": outer_retry_records(d)}
    for d in a.z_run_dir:
        res["z"][d] = {"vote": vote_records_z(d), "cmu": cmu_records(d), "outer_retry": outer_retry_records(d)}
    allv = [r for fam in res.values() for v in fam.values() for r in v["vote"]]
    allc = [r for fam in res.values() for v in fam.values() for r in v["cmu"]]
    gen = [r for r in allv if r.get("vote_state")]          # 生成時のvote記録(再利用entryはvote_stateなし)
    res["summary"] = {
        "vote_records_with_vote": len(gen), "vote_records_all": len(allv),
        "all_generated_vote_guard_lifted": all(bool(r.get("guard_lifted_vote")) for r in gen) if gen else None,
        "all_checks_guard_lifted": all(bool(r.get("check_guard_lifted")) for r in allv if r.get("check_version") or r.get("check_guard_lifted") is not None),
        "selection_metadata_n": len(allc), "all_selection_metadata_have_cmu_gate": all(r["has_cmu_gate"] for r in allc) if allc else None,
        "whisper_called_with_observed_protected_diff": [r for r in gen if r.get("whisper_called") and any((r.get("observed_protected_diff") or {}).values())],
        "cmu_fired_selection_retries": [r for r in allc if r["attempts_with_cmu_reason"]],
    }
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    json.dump(res, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    s = res["summary"]
    print({k: (v if not isinstance(v, list) else len(v)) for k, v in s.items()})


if __name__ == "__main__":
    main()
