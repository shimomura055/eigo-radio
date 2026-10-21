# ============================================================
# er091_asr_three_way_trial_01_tts_construct.py
# ASR-THREE-WAY-COMPARISON-TRIAL-01: 意図的誤発音音声の新規TTS(上限8本、Trial専用dir、量産集計と区別)。
# 正解ラベルは「構成ラベル」: canonical(本来の台本)と異なる文面をTTSに読ませた=音声は台本どおりではない(問題)。
# TTSがcanonicalへ「自動補正」した場合はラベルが成立しない -> 後段でASR転写との照合結果を併記(要人間試聴フラグ)。
# Production TTS関数(単発・ASR検証なし)を呼ぶだけでProductionは改変しない。1回のみ実行(再生成しない)。
# ============================================================
from __future__ import annotations
import json
import os
import shutil
import time

OUT = "er091_output/asr_three_way_trial_01"
DST = os.path.join(OUT, "audio", "tts_construct")
os.makedirs(DST, exist_ok=True)
import er005_cost_logger as cl  # noqa: E402
cl.install(os.path.join(OUT, "tts_raw_usage_log.jsonl"))
import er003_v1_repro01_main_generate as gen  # noqa: E402

# (id, kind, canonical台本, TTSに読ませた文面, 誤りの種類)
ITEMS = [
    ("tts_kp_takepart_as_tart", "kp", "take part", "take tart", "consonant_swap(p->t)"),
    ("tts_kp_weaken_as_weekend", "kp", "weaken", "weekend", "vowel/consonant_confusion(real_store_suspect)"),
    ("tts_kp_turnon_as_turnoff", "kp", "turn on", "turn off", "meaning_change_word_swap"),
    ("tts_kp_makerewardsmaller_omit_a", "kp", "make a reward smaller", "make reward smaller", "function_word_omission"),
    ("tts_kp_farbank_as_furbank", "kp", "far bank", "fur bank", "vowel_swap"),
    ("tts_body_threedays_as_thirteen", "body", "\"Give me three days to see my sister's wedding,\"",
     "\"Give me thirteen days to see my sister's wedding,\"", "number_error"),
    ("tts_body_return_negation_added", "body", "\"Then I will return to you.\"", "\"Then I will not return to you.\"",
     "negation_added"),
    ("tts_body_melos_as_milos", "body", "Melos said.", "Milos said.", "proper_noun_misreading"),
]
assert len(ITEMS) <= 8


def main():
    log = []
    for rid, kind, canon, spoken, etype in ITEMS:
        out = os.path.join(DST, rid + ".wav")
        t = time.time()
        margin = gen.KEY_PHRASE_TRIM_SAFETY_MARGIN_SECONDS if kind == "kp" else gen.p3u.NARRATION_BODY_TRIM_SAFETY_MARGIN_SECONDS
        r = gen.generate_english_component_minimal_instruction(
            spoken, out, safety_margin_seconds=margin, tts_backend="speech_metadata_flash_lite")
        rec = {"id": rid, "kind": kind, "canonical": canon, "spoken_text_requested": spoken, "error_type": etype,
               "status": r.get("status"), "path": out.replace("\\", "/"), "sha256": r.get("sha256"),
               "duration_s": r.get("duration_seconds"), "model": r.get("model"), "voice": r.get("voice"),
               "call_count": r.get("call_count"), "wall_s": round(time.time() - t, 2), "reason": r.get("reason")}
        log.append(rec)
        print(rec, flush=True)
    json.dump(log, open(os.path.join(OUT, "tts_construct_log.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
