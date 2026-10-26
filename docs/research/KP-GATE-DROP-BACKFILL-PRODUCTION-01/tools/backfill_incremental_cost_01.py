# -*- coding: utf-8 -*-
"""補完1発動あたりの追加費用(実測)を、補完に属するLLM call(2-V補完call・補完分canonicalization・補完分gloss整合)のresponse_idで特定して集計する。読取りのみ・API 0。
実行: .venv\\Scripts\\python.exe docs\\research\\KP-GATE-DROP-BACKFILL-PRODUCTION-01\\tools\\backfill_incremental_cost_01.py <kp_candidates.json> <usage.jsonl>
(response_idの出典: doc.backfill.response_id / <work>/backfill_1/canonicalization_runtime_metadata.json / gloss_alignment_runtime_metadata.json)
"""
from __future__ import annotations

import json
import os
import re
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, ROOT)
os.chdir(ROOT)


def ids_for(cand_path: str) -> dict:
    d = json.load(open(cand_path, encoding="utf-8"))
    bf = d.get("backfill") or {}
    out = {}
    if not bf.get("triggered"):
        return out
    if bf.get("response_id"):
        out[bf["response_id"]] = "backfill_2V"
    work = os.path.join(os.path.dirname(cand_path), "kp_candidates", "round_1", "work", "backfill_1")
    for fn, lab in (("canonicalization_runtime_metadata.json", "backfill_canonicalization"), ("gloss_alignment_runtime_metadata.json", "backfill_gloss_alignment")):
        p = os.path.join(work, fn)
        if os.path.exists(p):
            for rid in set(re.findall(r'"response_id": "([^"]+)"', open(p, encoding="utf-8").read())):
                out[rid] = lab
    return out


def main(cand_path: str, usage_path: str) -> dict:
    import er019_family_x_audio_production_runner_01 as x
    ids = ids_for(cand_path)
    lines = {}
    for line in open(usage_path, encoding="utf-8"):
        if not line.strip():
            continue
        r = json.loads(line)
        if r.get("response_id") in ids:
            lines.setdefault(ids[r["response_id"]], []).append(line)
    res = {"cand": cand_path, "by_call": {}, "total_jpy": 0.0}
    for lab, ls in lines.items():
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8") as t:
            t.writelines(ls)
        jpy, _ = x.compute_cost_jpy_so_far(t.name)
        os.unlink(t.name)
        res["by_call"][lab] = {"calls": len(ls), "jpy": round(jpy, 4)}
        res["total_jpy"] += jpy
    res["total_jpy"] = round(res["total_jpy"], 4)
    res["missing_ids"] = [i for i in ids if not any(i in l for ls in lines.values() for l in ls)]
    return res


if __name__ == "__main__":
    print(json.dumps(main(sys.argv[1], sys.argv[2]), ensure_ascii=False))
