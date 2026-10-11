#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OPEN-256 是正後 (a') ¥0 replay + 固定fixture生成(API 0)。

er011_output/local_rewrite_recovery/** の記録済み候補とQA evaluationsを、本番コード経路
(build_full_candidate_records -> select_final_candidate -> _write_recovery_artifacts[一時dir])へ
通し、旧ruleとの判定差を保存する。
usage: py -3 er053_family_x_open256_replay_01.py
出力: er053_output/family_x_tts_asr_rootcause_01/OPEN256_REPLAY_01.json / open256_fixture_90records_01.json
"""
from __future__ import annotations

import glob
import json
import os
import tempfile

import er020_tts_retry_local_rewrite_01 as m

OUT = os.path.join("er053_output", "family_x_tts_asr_rootcause_01")
DERIVED = ("qa_llm", "is_full_segment_format_valid", "full_segment_check", "locality_check",
           "seven_gates", "all_seven_gates_pass")


def main() -> int:
    files = sorted(glob.glob(os.path.join("er011_output", "local_rewrite_recovery", "**",
                                          "local_rewrite_recovery_*.json"), recursive=True))
    rows, fixture, file_rows = [], [], []
    tmp = tempfile.mkdtemp(prefix="open256_replay_")
    for f in files:
        d = json.load(open(f, encoding="utf-8"))
        ng = d.get("ng_span") or {}
        canon = d["canonical_text"]
        pr = (m.find_problem_span_token_range(canon, " ".join(ng.get("canonical_changed_words") or []))
              if ng.get("found") else
              {"found": False, "start": None, "end": None, "canon_tokens": m.asr_validation.tokenize(canon)})
        cands_in = [{k: v for k, v in c.items() if k not in DERIVED} for c in d["candidates"]]
        qa_evals = []
        for c in d["candidates"]:
            if c.get("qa_llm"):
                qa_evals.append({**c["qa_llm"], "candidate_id": c["id"]})
        recs = m.build_full_candidate_records(canon, cands_in, qa_evals, pr)
        sel = m.select_final_candidate(recs)
        res = {"segment_id": d["segment_id"] + "__replay", "replay": True, "candidates": recs, "selection": sel}
        m._write_recovery_artifacts(res, os.path.join(tmp, os.path.basename(os.path.dirname(f))))
        rel = os.path.relpath(f, os.path.join("er011_output", "local_rewrite_recovery")).replace("\\", "/")
        old_sel = (d.get("selection") or {}).get("selected")
        file_rows.append({"file": rel, "old_selected_id": (old_sel or {}).get("id"),
                          "new_selected_id": (sel["selected"] or {}).get("id"),
                          "old_status": (d.get("selection") or {}).get("status"), "new_status": sel["status"]})
        for old, new in zip(d["candidates"], recs):
            old_full = (old["rewritten_segment"][:15].strip().lower() == canon[:15].strip().lower())
            rows.append({
                "file": rel, "id": new["id"], "old_prefix15_rule_pass": old_full,
                "recorded_is_full_segment": old.get("is_full_segment_format_valid"),
                "new_full_segment_ok": new["is_full_segment_format_valid"],
                "new_reason": new["full_segment_check"]["reason"],
                "recorded_all_seven": old.get("all_seven_gates_pass"), "new_all_seven": new["all_seven_gates_pass"],
                "other_gates_all_pass": all(v is True for v in new["seven_gates"].values()),
            })
            fixture.append({
                "file": rel, "id": new["id"], "canonical_text": canon,
                "rewritten_segment": new["rewritten_segment"],
                "changed_span_before": new.get("changed_span_before"),
                "changed_span_after": new.get("changed_span_after"),
                "ng_changed_tokens": pr["canon_tokens"][pr["start"]:pr["end"]] if pr["found"] else [],
                "old_prefix15_rule_pass": old_full,
            })
    old_adopted = [r for r in rows if r["old_prefix15_rule_pass"]]
    rescue = [r for r in rows if not r["old_prefix15_rule_pass"]]
    meta = [r for r in rows if r["file"].startswith("meta__run_regen_01/b1b/local_rewrite_recovery_comment_2")]
    flips_to_false = [r for r in rows if r["recorded_all_seven"] and not r["new_all_seven"]]
    rescued = [r for r in rows if (not r["recorded_all_seven"]) and r["new_all_seven"]]
    summary = {
        "n_candidates": len(rows), "n_files": len(files),
        "old_adopted_count": len(old_adopted),
        "old_adopted_still_full_ok": sum(r["new_full_segment_ok"] for r in old_adopted),
        "old_adopted_judgement_changes": [r for r in old_adopted if not r["new_full_segment_ok"]],
        "rescue_target_count": len(rescue),
        "rescue_full_ok": sum(r["new_full_segment_ok"] for r in rescue),
        "rescue_full_rejected": [r for r in rescue if not r["new_full_segment_ok"]],
        "meta_comment_2": meta,
        "all_seven_true_to_false": flips_to_false,
        "all_seven_false_to_true_rescued": rescued,
        "selection_changes": [x for x in file_rows if x["old_selected_id"] != x["new_selected_id"]],
        "tmp_artifacts_dir": tmp,
    }
    os.makedirs(OUT, exist_ok=True)
    json.dump({"summary": summary, "candidates": rows, "files": file_rows},
              open(os.path.join(OUT, "OPEN256_REPLAY_01.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    json.dump(fixture, open(os.path.join(OUT, "open256_fixture_90records_01.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(json.dumps({k: (v if not isinstance(v, list) else len(v)) for k, v in summary.items()},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
