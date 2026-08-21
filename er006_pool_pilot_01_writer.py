# ============================================================
# er006_pool_pilot_01_writer.py
# ER-006-POOL-PILOT-01: Writer(B1/A2)+FactCheck+LedgerDeviation
# ============================================================
# er003_v1_n3_01_articles_generate.py の本番run_one_pattern()をそのまま
# 呼び出す(prompt/instruction/Fact Checker/Deviation Checkは無変更)。
# B1/A2それぞれを個別にcl.logging_context()で囲むことで、共有のrun_theme()
# 一括呼び出しでは失われるLevel別costの区別を維持する。

from __future__ import annotations

import json
import os
import time

import er005_cost_logger as cl
import er003_v1_n3_01_articles_generate as gen
import er003_v1_en_direct_ab_01_generate as ab01
import er003_v1_en_direct_vfl_01_generate as vfl01


def load_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def run_writer_for_theme(client, master_full_text: str, theme_id: str, topic: str,
                          ledger_path: str, out_dir: str) -> dict:
    verified_ledger_text = load_text(ledger_path)
    common_block = gen.build_common_block(master_full_text, topic, verified_ledger_text)

    results = {}
    timing = {}
    for label, instruction, level_out_dir, stage_tag in [
        ("B1B", gen.B1_B_DIRECT_INSTRUCTION, f"{out_dir}/b1b", "writer_b1"),
        ("A2", gen.A2_KAI1_INSTRUCTION, f"{out_dir}/a2", "writer_a2"),
    ]:
        prompt = gen.build_prompt(common_block, instruction)
        t0 = time.time()
        with cl.logging_context(theme_id, stage_tag):
            result = gen.run_one_pattern(client, theme_id, label, prompt, verified_ledger_text,
                                          topic, level_out_dir)
        timing[stage_tag] = round(time.time() - t0, 2)
        results[label] = result

    with open(f"{out_dir}/articles_run_summary.json", "w", encoding="utf-8") as f:
        json.dump({k: {kk: vv for kk, vv in v.items() if kk != "article_text"} for k, v in results.items()},
                   f, ensure_ascii=False, indent=2, default=str)
    with open(f"{out_dir}/writer_timing.json", "w", encoding="utf-8") as f:
        json.dump(timing, f, ensure_ascii=False, indent=2)
    print(f"[{theme_id}] Writer完了。timing={timing}")
    for label, r in results.items():
        print(f"  {label}: status={r.get('status')} fact_verdict={r.get('fact_verdict')} "
              f"ledger_status={r.get('ledger_status')}")
    return {"results": results, "timing": timing}


if __name__ == "__main__":
    print("This module is imported by er006_pool_pilot_01_run.py; not run directly.")
