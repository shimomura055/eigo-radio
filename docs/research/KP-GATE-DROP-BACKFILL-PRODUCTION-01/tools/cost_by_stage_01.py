# -*- coding: utf-8 -*-
"""usage log(jsonl)のstage別費用(JPY、token x 単価。`compute_cost_jpy_so_far`)。読取りのみ・API 0。
実行: .venv\\Scripts\\python.exe docs\\research\\KP-GATE-DROP-BACKFILL-PRODUCTION-01\\tools\\cost_by_stage_01.py <usage.jsonl> [...]
"""
from __future__ import annotations

import json
import os
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, ROOT)
os.chdir(ROOT)


def cost_by_stage(path: str) -> dict:
    import er019_family_x_audio_production_runner_01 as x
    by = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                d = json.loads(line)
                by.setdefault(d.get("stage"), []).append(line)
    out = {}
    for st, lines in by.items():
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8") as t:
            t.writelines(lines)
        jpy, _ = x.compute_cost_jpy_so_far(t.name)
        os.unlink(t.name)
        out[st] = {"calls": len(lines), "cost_jpy": round(jpy, 4)}
    total, _ = x.compute_cost_jpy_so_far(path)
    models = sorted({json.loads(line).get("model_id") for line in open(path, encoding="utf-8") if line.strip()})
    return {"path": path, "by_stage": out, "total_cost_jpy": round(total, 4), "models": models, "n_calls": sum(v["calls"] for v in out.values())}


if __name__ == "__main__":
    for p in sys.argv[1:]:
        print(json.dumps(cost_by_stage(p), ensure_ascii=False))
