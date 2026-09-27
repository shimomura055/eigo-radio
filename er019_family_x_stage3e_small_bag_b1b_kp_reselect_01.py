# ============================================================
# er019_family_x_stage3e_small_bag_b1b_kp_reselect_01.py
# NEWS-FAMILY-X-AUDIO-PRODUCTION-WIRING-01 Stage 3e
# ============================================================
# ユーザー既決(2026-09-27): small_bag B1B Key Phrase再選定を、既存
# Strategy L(既定`kp_backend="strategy_l"`、DB Hybridは使わない)で1 call
# だけ承認。既存Production関数(er003_v1_n3_01_scaffold_generate.
# run_key_phrases、無変更)をそのまま呼ぶだけで、新しいGate/retry仕様は
# 追加しない。選定→canonicalization→Key Phrase Set Redundancy QAの
# 構造Gateを通過した場合のみ、以降のKP TTS(`--stage tts --level b1b`
# 再実行)へ進む(既存run_key_phrases自体の仕様どおり、Gateに自動retry
# は無い)。
#
# 実行方法(root直下から、実LLM呼び出し1回、既存Production費用計測込み):
#   .venv/Scripts/python.exe er019_family_x_stage3e_small_bag_b1b_kp_reselect_01.py
from __future__ import annotations

import json

import er003_v1_n3_01_scaffold_generate as sc
import er005_cost_logger as cl

SOURCE_ARTICLE_PATH = "er019_output/family_x_b3_diversity_trial_01/small_bag/run_02/b1b/article.md"
OUT_DIR = "er019_output/family_x_audio_production_wiring_01/family_x_b3_diversity_trial_01/small_bag__run_02"
KP_DIR = f"{OUT_DIR}/b1b/key_phrases"
ARTICLE_ID = f"FAMILY_X_AUDIO_{OUT_DIR.rsplit('/', 1)[1]}_b1b"


def main() -> None:
    # NEWS-FAMILY-X-AUDIO-PRODUCTION-WIRING-01のrunner(main()内`cl.install(
    # f"{out_dir}/raw_usage_log.jsonl")`)と同じcost log先へ記録する(この
    # 呼び出し自体は既存run_theme_scaffold()と同じsc.run_key_phrasesを
    # 直接呼ぶだけで、scaffold全体[本文生成等]は再実行しない)。
    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")
    with open(SOURCE_ARTICLE_PATH, encoding="utf-8") as f:
        article_text = f.read()

    with cl.logging_context("family_x_b3_diversity_trial_01/small_bag", "kp_reselect_stage3e"):
        kp = sc.run_key_phrases(article_text, KP_DIR, ARTICLE_ID, "b1b", process="B1_SUPPORT")

    sel_status = kp["selection"]["status"]
    canon_status = (kp["canonicalization"] or {}).get("status") if kp["canonicalization"] else None
    redundancy_status = (kp["redundancy_qa"] or {}).get("status") if kp["redundancy_qa"] else None
    overall = kp.get("status")
    print(json.dumps({
        "selection_status": sel_status,
        "canonicalization_status": canon_status,
        "redundancy_status": redundancy_status,
        "overall_status_field": overall,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
