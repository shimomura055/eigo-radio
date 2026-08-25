# ============================================================
# er007_openai_ja_asr_quality_test_02.py
# Part E追加sample(1回目のn=6が僅少すぎたため、層化サンプルをn=14まで
# 拡大する)。canonical textは全て既存JSONから直接抽出(手入力しない)。
# ============================================================
import json
import time

import er005_cost_logger as cl
cl.install("er006_output/pool_pilot_01/evidence_density_ab_01/openai_ja_asr_quality_log.jsonl")

import er006_asr_provider_routing_01 as routing
import er007_ja_asr_validator_01 as javal

SAMPLES = [
    ("pool_n4_supermarket", "a2", "preview", "preview(長文、否定含む)"),
    ("pool_n4_supermarket", "a2", "comment_4", "comment_4(中文、否定含む)"),
    ("pool_n5_cafes", "a2", "comment_1", "comment_1(短文)"),
    ("pool_n5_cafes", "a2", "japanese_title", "japanese_title(短文)"),
    ("pool_n6_delivery", "a2", "comment_3", "comment_3(長文、否定含む)"),
    ("pool_subscriptions", "a2", "comment_4", "comment_4(中文、否定含む)"),
    ("pool_startups", "a2", "japanese_title", "japanese_title(短文)"),
    ("pool_startups", "a2", "comment_2", "comment_2(中文)"),
]


def load_canonical_and_azure(topic, level, seg_name):
    path = f"er006_output/pool_pilot_01/{topic}/{level}/audit/tts_generation_results.json"
    d = json.load(open(path, encoding="utf-8"))
    seg = d["segments"].get(seg_name)
    return seg.get("canonical_text"), seg.get("asr_text")


def run():
    results = []
    for topic, level, seg_name, label in SAMPLES:
        wav_path = f"er006_output/pool_pilot_01/{topic}/{level}/narration/{seg_name}.wav"
        canonical, azure_asr = load_canonical_and_azure(topic, level, seg_name)
        print(f"\n=== {topic}/{seg_name} - {label} ===")
        print(f"  canonical: {canonical!r}")
        t0 = time.time()
        with cl.logging_context(f"{topic}_ja_asr_quality2", "openai_mini_ja_test2"):
            openai_text, err = routing._transcribe_openai_mini(wav_path, "ja-JP", "gpt-4o-mini-transcribe")
        elapsed = round(time.time() - t0, 2)
        print(f"  OpenAI mini ({elapsed}s): {openai_text!r} (err={err})")
        print(f"  Azure(既存記録): {azure_asr!r}")

        r_openai = javal.classify_ja_asr_match(canonical, openai_text) if openai_text else None
        r_azure = javal.classify_ja_asr_match(canonical, azure_asr) if azure_asr else None
        print(f"  新Validator判定(OpenAI): {r_openai.classification if r_openai else 'N/A'} should_pass={r_openai.should_pass if r_openai else 'N/A'}")
        print(f"  新Validator判定(Azure):  {r_azure.classification if r_azure else 'N/A'} should_pass={r_azure.should_pass if r_azure else 'N/A'}")

        results.append({
            "topic": topic, "segment": seg_name, "label": label, "canonical": canonical,
            "openai_text": openai_text, "openai_elapsed_seconds": elapsed, "azure_text": azure_asr,
            "openai_classification": r_openai.classification if r_openai else None,
            "openai_should_pass": r_openai.should_pass if r_openai else None,
            "azure_classification": r_azure.classification if r_azure else None,
            "azure_should_pass": r_azure.should_pass if r_azure else None,
        })

    with open("er006_output/pool_pilot_01/evidence_density_ab_01/openai_ja_asr_quality_results_2.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("\nOPENAI_JA_ASR_QUALITY_TEST_2_DONE")


if __name__ == "__main__":
    run()
