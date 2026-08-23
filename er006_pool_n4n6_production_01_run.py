# ============================================================
# er006_pool_n4n6_production_01_run.py
# ER-006-POOL-N4-N6-PRODUCTION-01: No.4-6 現行Production仕様での通し生成
# ============================================================
# POOL_TOPIC_MASTER.mdでユーザー承認済みの20 Topic MasterのNo.4-6を、
# 現行FIX済みProduction仕様(Luna Writer/Support/FactCheck、Gemini Batch
# TTS、OpenAI English Primary ASR、現行Validator、Master Audio Store)で
# 通し生成する。Topic Selectionは実行しない(ユーザーがPOOL_TOPIC_MASTER
# から直接指定したため、USER_DECIDED_FROM_POOL_MASTERとして扱う)。
#
# 実行方法: .venv/Scripts/python.exe er006_pool_n4n6_production_01_run.py <theme_key>
# theme_key: pool_n4_supermarket / pool_n5_cafes / pool_n6_delivery
from __future__ import annotations

import json
import sys
import time

sys.path.insert(0, '.')
import er005_cost_logger as cl
cl.install("er006_output/pool_pilot_01/raw_usage_log.jsonl")

import er003_v1_en_direct_ab_01_generate as ab01
import er003_v1_en_direct_vfl_01_generate as vfl01
import er006_pool_pilot_01_research as research_mod
import er006_pool_pilot_01_ledger as ledger_mod
import er006_pool_pilot_01_writer as writer_mod
import er006_pool_pilot_01_support as support_mod
import er006_pool_pilot_01_audio as audio_mod
import er006_pool_pilot_01_topics as topics

THEME_CONFIG = {
    "pool_n4_supermarket": {
        "title": "The Supermarket Shuffle: Why Shelves Keep Moving",
        "out_dir": "er006_output/pool_pilot_01/pool_n4_supermarket",
    },
    "pool_n5_cafes": {
        "title": "Cafes Are Rethinking the All-Day Customer",
        "out_dir": "er006_output/pool_pilot_01/pool_n5_cafes",
    },
    "pool_n6_delivery": {
        "title": "The Strange Pull of Delivery Tracking",
        "out_dir": "er006_output/pool_pilot_01/pool_n6_delivery",
    },
}


def run_research_stage(theme_id: str) -> dict:
    cfg = THEME_CONFIG[theme_id]
    out_dir = cfg["out_dir"]
    sources = json.load(open(f"{out_dir}/research/raw_sources.json", encoding="utf-8"))["sources"]
    t0 = time.time()
    result = research_mod.run_research_for_theme(theme_id, f"{out_dir}/research", cfg["title"], sources)
    ledger_text = ledger_mod.build_ledger_text_from_vfl(
        result["vfl"]["parsed"], result["evidence_pack"]["parsed"], cfg["title"])
    ledger_path = f"{out_dir}/research/verified_fact_ledger.txt"
    with open(ledger_path, "w", encoding="utf-8") as f:
        f.write(ledger_text)
    elapsed = round(time.time() - t0, 1)
    print(f"[{theme_id}] Research+Ledger完了。elapsed={elapsed}s ledger_path={ledger_path}")
    return {"ledger_path": ledger_path, "elapsed": elapsed, "research_result": result}


def run_writer_support_stage(theme_id: str) -> dict:
    cfg = THEME_CONFIG[theme_id]
    out_dir = cfg["out_dir"]
    ledger_path = f"{out_dir}/research/verified_fact_ledger.txt"
    client = vfl01.get_client()
    master_full_text = ab01.load_master_full_text()

    t0 = time.time()
    writer_result = writer_mod.run_writer_for_theme(
        client, master_full_text, theme_id, topics.TOPIC_JA[theme_id], ledger_path, out_dir)
    t1 = time.time()
    ledger_text = open(ledger_path, encoding="utf-8").read()
    support_result = support_mod.run_support_for_theme(client, theme_id, out_dir, ledger_text)
    t2 = time.time()
    print(f"[{theme_id}] Writer完了 elapsed={round(t1-t0,1)}s / Support完了 elapsed={round(t2-t1,1)}s")
    return {"writer_result": writer_result, "support_result": support_result,
            "writer_elapsed": round(t1 - t0, 1), "support_elapsed": round(t2 - t1, 1)}


def run_audio_stage(theme_id: str) -> dict:
    cfg = THEME_CONFIG[theme_id]
    theme = {"theme_id": theme_id, "out_dir": cfg["out_dir"]}
    t0 = time.time()
    audio_result = audio_mod.run_audio_for_theme(theme)
    elapsed = round(time.time() - t0, 1)
    print(f"[{theme_id}] Audio完了。elapsed={elapsed}s")
    return {"audio_result": audio_result, "elapsed": elapsed}


if __name__ == "__main__":
    theme_id = sys.argv[1]
    stage = sys.argv[2] if len(sys.argv) > 2 else "all"
    t_start = time.time()

    timing = {"theme_id": theme_id, "start_timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")}
    if stage in ("all", "research"):
        r1 = run_research_stage(theme_id)
        timing["research_elapsed_seconds"] = r1["elapsed"]
    if stage in ("all", "writer_support"):
        r2 = run_writer_support_stage(theme_id)
        timing["writer_elapsed_seconds"] = r2["writer_elapsed"]
        timing["support_elapsed_seconds"] = r2["support_elapsed"]
    if stage in ("all", "audio"):
        r3 = run_audio_stage(theme_id)
        timing["audio_elapsed_seconds"] = r3["elapsed"]

    timing["total_elapsed_seconds"] = round(time.time() - t_start, 1)
    timing["end_timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    cfg = THEME_CONFIG[theme_id]
    with open(f"{cfg['out_dir']}/throughput_timing_{stage}.json", "w", encoding="utf-8") as f:
        json.dump(timing, f, ensure_ascii=False, indent=2)
    print(f"TOTAL_ELAPSED_SECONDS={timing['total_elapsed_seconds']}")
    print(f"[{theme_id}][{stage}] RUN_DONE")
