# ============================================================
# er007_evidence_density_ab_01_factcheck.py
# ER-007-SPOKEN-EVIDENCE-DENSITY-AB-01 Part A-7:
# B版spoken scriptを、既存Ledgerに対しWriter Fact Check + Ledger
# Deviation Checkで再検証する(新規Researchは行わない)。
# ============================================================
from __future__ import annotations

import json
import sys

import er005_cost_logger as cl
cl.install("er006_output/pool_pilot_01/evidence_density_ab_01/factcheck_usage_log.jsonl")

import er002_ja_web_research_r3 as r3
import er003_v1_en_direct_vfl_01_generate as vfl01
import er006_model_routing_contract_01 as routing
import er006_pool_pilot_01_topics as topics
from er007_evidence_density_ab_01_scripts import B_SCRIPTS

THEME_CONFIG = {
    "n4_supermarket": {"theme_id": "pool_n4_supermarket", "out_dir": "er006_output/pool_pilot_01/pool_n4_supermarket"},
    "n5_cafes": {"theme_id": "pool_n5_cafes", "out_dir": "er006_output/pool_pilot_01/pool_n5_cafes"},
    "n6_delivery": {"theme_id": "pool_n6_delivery", "out_dir": "er006_output/pool_pilot_01/pool_n6_delivery"},
}


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build_b_article_text(parts: dict, overrides: dict) -> str:
    part1 = overrides.get("part1") or parts["part1"]
    part2 = overrides.get("part2") or parts["part2"]
    p1_body = overrides.get("point_one_body") or parts["point_one_body"]
    p2_body = overrides.get("point_two_body") or parts["point_two_body"]
    return (
        f"# {parts['title']}\n\n"
        f"{part1}\n\n"
        f"{part2}\n\n"
        f"### {parts['point_one_heading']}\n\n"
        f"{p1_body}\n\n"
        f"### {parts['point_two_heading']}\n\n"
        f"{p2_body}\n\n"
        f"## In one line…\n\n"
        f"{parts['in_one_line']}"
    )


def run_check(short_key: str, level: str) -> dict:
    cfg = THEME_CONFIG[short_key]
    theme_id = cfg["theme_id"]
    out_dir = cfg["out_dir"]
    level_dir = "b1b" if level == "b1b" else "a2"
    parts = load_json(f"{out_dir}/{level_dir}/parts.json")
    overrides = B_SCRIPTS[short_key][level_dir]
    b_article_text = build_b_article_text(parts, overrides)

    ledger_path = f"{out_dir}/research/verified_fact_ledger.txt"
    verified_ledger_text = open(ledger_path, encoding="utf-8").read()
    topic = topics.TOPIC_JA[theme_id]

    client = vfl01.get_client()

    label = f"{short_key}_{level_dir}_B"
    print(f"[{label}] Fact Checker呼び出し開始...")
    fc_prompt = r3.build_fact_check_prompt(topic, b_article_text, [])

    def make_fc_fn():
        return r3.make_fact_checker_fn(
            fc_prompt, client=client,
            model=routing.require_model("WRITER_FACT_CHECK", routing.WRITER_FACT_CHECK_MODEL))

    with cl.logging_context(f"{theme_id}_evidence_density_ab", f"factcheck_B_{level_dir}"):
        fc_result, fc_status, fc_attempts, fc_model, fc_response_id, fc_search_usage, fc_sources = \
            r3.run_fact_checker_with_gates(make_fc_fn, sleep_fn=None)
    verdict = fc_result.get("verdict") if fc_result else None
    print(f"[{label}] fact_check status={fc_status} verdict={verdict}")

    print(f"[{label}] Ledger Deviation Check呼び出し開始...")
    writer_process = "B1_WRITER" if level_dir == "b1b" else "A2_WRITER"
    with cl.logging_context(f"{theme_id}_evidence_density_ab", f"deviation_B_{level_dir}"):
        deviation_result = vfl01.run_deviation_check(
            client, verified_ledger_text, b_article_text,
            model=routing.require_model(writer_process, routing.WRITER_MODEL))
    dev_status = deviation_result["parsed"]["overall_status"]
    dev_count = len(deviation_result["parsed"]["deviations"])
    print(f"[{label}] deviation overall_status={dev_status} deviations={dev_count}")

    record = {
        "label": label, "b_article_text": b_article_text,
        "fact_status": fc_status, "fact_verdict": verdict, "fact_result": fc_result,
        "ledger_status": dev_status, "ledger_deviation_count": dev_count,
        "ledger_deviations": deviation_result["parsed"]["deviations"],
    }
    out_path = f"er006_output/pool_pilot_01/evidence_density_ab_01/{short_key}_{level_dir}_B_factcheck.json"
    import os
    os.makedirs("er006_output/pool_pilot_01/evidence_density_ab_01", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=2, default=str)
    return record


if __name__ == "__main__":
    targets = sys.argv[1:] or [f"{k}:{lvl}" for k in THEME_CONFIG for lvl in ("b1b", "a2")]
    for t in targets:
        k, lvl = t.split(":")
        run_check(k, lvl)
    print("ALL_FACTCHECK_DONE")
