# ============================================================
# er006_pool_pilot_01_audio.py
# ER-006-POOL-PILOT-01: TTS + ASR/Audio QA + Assembly
# ============================================================
# er003_v1_n3_01_tts_generate.py / er003_v1_n3_01_assemble.py の本番
# generate_b1_segments/generate_a2_segments/stage_assemble_b1/
# stage_assemble_a2をそのまま呼び出す(ER-005-AUDIO-*系で確立済みの
# Structured Separation・phonetic validation・trim safety・duration
# anomaly検知・Point Notification仕様は全て無変更で適用される)。
# B1/A2それぞれ個別にcl.logging_context()で囲み、Level別costを維持する。

from __future__ import annotations

import json
import time

import er005_cost_logger as cl
import er003_v1_n3_01_tts_generate as tts_gen
import er003_v1_n3_01_assemble as asm

# generate_a2_segments()は本番のJAPANESE_TITLES辞書(hanshin/health/household用)を
# 参照する設計になっている。ER-006の新規3テーマ分をここへ追加する(production側の
# er003_v1_n3_01_tts_generate.pyファイル自体は変更しない、実行時にdictへ追記するのみ)。
tts_gen.JAPANESE_TITLES.update({
    "pool_benches": "公共のベンチ、なぜ今見直されているのか",
    "pool_subscriptions": "なぜ契約は簡単で、解約は難しいのか",
    "pool_startups": "なぜ一部のスタートアップは利益より成長を優先するのか",
})


def run_audio_for_theme(theme: dict) -> dict:
    theme_id = theme["theme_id"]
    timing = {}

    t0 = time.time()
    with cl.logging_context(theme_id, "tts_b1"):
        b1_tts_summary = tts_gen.generate_b1_segments(theme)
    timing["tts_b1"] = round(time.time() - t0, 2)

    t1 = time.time()
    with cl.logging_context(theme_id, "tts_a2"):
        a2_tts_summary = tts_gen.generate_a2_segments(theme)
    timing["tts_a2"] = round(time.time() - t1, 2)

    t2 = time.time()
    with cl.logging_context(theme_id, "assemble_b1"):
        b1_assemble_summary = asm.stage_assemble_b1(theme)
    timing["assemble_b1"] = round(time.time() - t2, 2)

    t3 = time.time()
    with cl.logging_context(theme_id, "assemble_a2"):
        a2_assemble_summary = asm.stage_assemble_a2(theme)
    timing["assemble_a2"] = round(time.time() - t3, 2)

    with open(f"{theme['out_dir']}/audio_timing.json", "w", encoding="utf-8") as f:
        json.dump(timing, f, ensure_ascii=False, indent=2)

    print(f"[{theme_id}] Audio完了。timing={timing}")
    print(f"  B1 TTS: {b1_tts_summary['segment_status']}")
    print(f"  A2 TTS: {a2_tts_summary['segment_status']}")
    print(f"  B1 Assemble: {b1_assemble_summary}")
    print(f"  A2 Assemble: {a2_assemble_summary}")
    return {
        "b1_tts": b1_tts_summary, "a2_tts": a2_tts_summary,
        "b1_assemble": b1_assemble_summary, "a2_assemble": a2_assemble_summary,
        "timing": timing,
    }


if __name__ == "__main__":
    print("This module is imported by er006_pool_pilot_01_run.py; not run directly.")
