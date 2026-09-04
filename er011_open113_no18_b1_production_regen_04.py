# ============================================================
# er011_open113_no18_b1_production_regen_04.py
# OPEN-113-POINT-CONTEXT-PRODUCTION-WIRING-AND-NO18-B1-REGEN-04
# ============================================================
# No.18 B1を、正式Production経路(er006_pool_pilot_01_writer.run_writer_for_theme
# が内部で呼ぶgen.run_one_pattern、B1_B_DIRECT_INSTRUCTION・
# build_common_block・build_prompt)を使って再生成する。4層Prompt
# (er011_open112_a_family_4layer_prompt_trial_05.py)は一切使用しない
# (このscriptはimportもしない)。
#
# Topic/Verified Fact Ledgerは、現行承認済みのpool_n18_notifications_
# specfix_v2のものをそのまま再利用する(新しいWeb researchは行わない、
# 記事固有の書き換えも行わない)。A2は再生成しない(gen.run_one_patternを
# B1B 1件のみ呼ぶ)。出力先は新しいtheme_id/out_dirとし、既存承認済み
# pool_n18_notifications_specfix_v2は変更・上書きしない。
from __future__ import annotations

import json
import os
import time

if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

import er003_v1_en_direct_ab_01_generate as ab01
import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_articles_generate as gen
import er011_no18_discovery_why_full_production_run_01 as no18_orig

EXISTING_THEME_ID = "pool_n18_notifications_specfix_v2"
EXISTING_OUT_DIR = f"er006_output/pool_pilot_01/{EXISTING_THEME_ID}"
LEDGER_PATH = f"{EXISTING_OUT_DIR}/research/verified_fact_ledger.txt"

THEME_ID = "pool_n18_notifications_open113_04_b1_regen"
OUT_DIR = f"er006_output/pool_pilot_01/{THEME_ID}"
B1_OUT_DIR = f"{OUT_DIR}/b1b"

TOPIC_JA = no18_orig.TOPIC_JA


def main() -> dict:
    os.makedirs(B1_OUT_DIR, exist_ok=True)
    os.makedirs(f"{B1_OUT_DIR}/audit", exist_ok=True)

    client = vfl01.get_client()
    master_full_text = ab01.load_master_full_text()
    verified_ledger_text = gen.load_text(LEDGER_PATH) if hasattr(gen, "load_text") else open(
        LEDGER_PATH, encoding="utf-8").read()

    common_block = gen.build_common_block(master_full_text, TOPIC_JA, verified_ledger_text,
                                           shared_point_blueprint_block="")
    prompt = gen.build_prompt(common_block, gen.B1_B_DIRECT_INSTRUCTION)

    with open(f"{B1_OUT_DIR}/audit/prompt.txt", "w", encoding="utf-8") as f:
        f.write(prompt)

    t0 = time.time()
    result = gen.run_one_pattern(client, THEME_ID, "B1B", prompt, verified_ledger_text, TOPIC_JA,
                                  B1_OUT_DIR, apply_evidence_compression=True)
    elapsed = round(time.time() - t0, 1)
    result["elapsed_seconds"] = elapsed
    result["theme_id"] = THEME_ID
    result["model_id_used_for_ledger"] = gen.routing.require_model(
        gen._writer_process("B1B"), gen.routing.WRITER_MODEL)

    print(f"[{THEME_ID}] B1B再生成完了。status={result.get('status')} "
          f"ledger_status={result.get('ledger_status')} "
          f"local_rewrite_fired={bool(result.get('local_rewrite_results'))} elapsed={elapsed}s")

    with open(f"{B1_OUT_DIR}/run_summary_open113_04.json", "w", encoding="utf-8") as f:
        json.dump({k: v for k, v in result.items() if k != "article_text"}, f, ensure_ascii=False,
                   indent=2, default=str)
    with open(f"{B1_OUT_DIR}/article.md", "w", encoding="utf-8") as f:
        f.write(result["article_text"])

    return result


if __name__ == "__main__":
    main()
