from __future__ import annotations
import er005_cost_logger as cl
import er003_v1_en_direct_ab_01_generate as ab01
import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_articles_generate as gen
import er011_open112_trend_synthesis_production_wiring_01_run as base

OUT_DIR = f"{base.OUT_DIR}/a2_run02"

def run():
    client = vfl01.get_client()
    master_full_text = ab01.load_master_full_text()
    ledger_text = gen.load_text(base.THEME2_LEDGER_PATH)
    block = gen.resolve_editorial_type_module_block("trend_synthesis")
    common_block = gen.build_common_block(master_full_text, base.TREND_TOPIC_JA, ledger_text,
                                           editorial_type_module_block=block)
    prompt = gen.build_prompt(common_block, gen.A2_KAI1_INSTRUCTION)
    with cl.logging_context(base.THEME_ID, "writer_a2_run02"):
        result = gen.run_one_pattern(client, base.THEME_ID, "A2", prompt, ledger_text,
                                      base.TREND_TOPIC_JA, OUT_DIR)
    print(f"A2 run02: status={result.get('status')} fact_verdict={result.get('fact_verdict')} "
          f"ledger_status={result.get('ledger_status')} "
          f"directional_fact_precheck_status={result.get('directional_fact_precheck_status')}")
    return result

if __name__ == "__main__":
    cl.install(f"{base.OUT_DIR}/raw_usage_log.jsonl")
    run()
