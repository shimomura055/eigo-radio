# ============================================================
# er007_openai_ja_asr_quality_test_01.py
# ER-007-JA-ASR-VALIDATOR-REDESIGN-AND-CASCADE-01 Part E:
# OpenAI mini日本語ASRの実効性を、既存Azure結果と比較する。
# 最小sample(6件)、新規TTSなし(既存WAVを再利用、ASRのみ新規呼び出し)。
# ============================================================
import json
import time

import er005_cost_logger as cl
cl.install("er006_output/pool_pilot_01/evidence_density_ab_01/openai_ja_asr_quality_log.jsonl")

import er006_asr_provider_routing_01 as routing
import er007_ja_asr_validator_01 as javal

SAMPLES = [
    ("comment_3(長文、やめにくくする実例)", "pool_subscriptions", "a2", "comment_3",
     ("このニュースは、定期サービスをやめにくくする仕組みと、それを変えようとした"
      "ルールが裁判で取り消された流れを伝えています。次は、解約の負担を手続きの"
      "最初から最後まで見ていきます。そして、研究者が複雑な解約の流れをどう"
      "調べたのかを聞きます。")),
    ("preview(長文)", "pool_subscriptions", "a2", "preview",
     ("定額サービスをやめたいのに、手続きの途中で迷ったことはありませんか。今回の"
      "ニュースは、解約するときに生まれる負担についてです。この問題を知ると、"
      "利用者にとって大切な視点が見えてきます。")),
    ("comment_2(中文、数字なし)", "pool_n4_supermarket", "a2", "comment_2",
     ("Part 1では、店が売り場の配置を変え、買い物客が最初に見る商品を変えたことを"
      "聞きました。では、その後、商品の売れ方はどう変わったのでしょうか。")),
    ("japanese_title(短文)", "pool_n6_delivery", "a2", "japanese_title", None),
    ("kp1_ja_charon(短文、B1 Key Phrase)", "pool_n5_cafes", "b1b", "kp1_ja_charon", None),
    ("meaning_1(短文、A2 Key Phrase)", "pool_n4_supermarket", "a2", "meaning_1", None),
]


def load_canonical(topic, level, seg_name):
    path = f"er006_output/pool_pilot_01/{topic}/{level}/audit/tts_generation_results.json"
    d = json.load(open(path, encoding="utf-8"))
    if seg_name.startswith("kp") and seg_name.endswith("_ja_charon"):
        rank = seg_name.replace("kp", "").replace("_ja_charon", "")
        return d["key_phrases"][rank]["japanese"]["canonical_text"]
    if seg_name.startswith("meaning_"):
        rank = seg_name.replace("meaning_", "")
        # meaning_{i}はrank基準ではなくindex基準、実データから逆引き
        for r, kp in d["key_phrases"].items():
            jm = kp.get("japanese_meaning")
            if jm and f"meaning_{rank}" in jm.get("path", ""):
                return jm["canonical_text"]
        return None
    seg = d["segments"].get(seg_name)
    return seg.get("canonical_text") if seg else None


def get_azure_result(topic, level, seg_name):
    path = f"er006_output/pool_pilot_01/{topic}/{level}/audit/tts_generation_results.json"
    d = json.load(open(path, encoding="utf-8"))
    if seg_name.startswith("kp") and seg_name.endswith("_ja_charon"):
        rank = seg_name.replace("kp", "").replace("_ja_charon", "")
        return d["key_phrases"][rank]["japanese"].get("asr_text")
    if seg_name.startswith("meaning_"):
        rank = seg_name.replace("meaning_", "")
        for r, kp in d["key_phrases"].items():
            jm = kp.get("japanese_meaning")
            if jm and f"meaning_{rank}" in jm.get("path", ""):
                return jm.get("asr_text")
        return None
    seg = d["segments"].get(seg_name)
    return seg.get("asr_text") if seg else None


def run():
    results = []
    for label, topic, level, seg_name, canonical_override in SAMPLES:
        wav_path = f"er006_output/pool_pilot_01/{topic}/{level}/narration/{seg_name}.wav"
        canonical = canonical_override or load_canonical(topic, level, seg_name)
        azure_asr = get_azure_result(topic, level, seg_name)

        print(f"\n=== {label} ===")
        print(f"  canonical: {canonical!r}")
        t0 = time.time()
        with cl.logging_context(f"{topic}_ja_asr_quality", "openai_mini_ja_test"):
            openai_text, err = routing._transcribe_openai_mini(wav_path, "ja-JP", "gpt-4o-mini-transcribe")
        elapsed = round(time.time() - t0, 2)
        print(f"  OpenAI mini ({elapsed}s): {openai_text!r} (err={err})")
        print(f"  Azure(既存記録): {azure_asr!r}")

        r_openai = javal.classify_ja_asr_match(canonical, openai_text) if openai_text else None
        r_azure = javal.classify_ja_asr_match(canonical, azure_asr) if azure_asr else None
        print(f"  新Validator判定(OpenAI): {r_openai.classification if r_openai else 'N/A'} "
              f"should_pass={r_openai.should_pass if r_openai else 'N/A'}")
        print(f"  新Validator判定(Azure):  {r_azure.classification if r_azure else 'N/A'} "
              f"should_pass={r_azure.should_pass if r_azure else 'N/A'}")

        results.append({
            "label": label, "canonical": canonical, "openai_text": openai_text, "openai_err": err,
            "openai_elapsed_seconds": elapsed, "azure_text": azure_asr,
            "openai_classification": r_openai.classification if r_openai else None,
            "openai_should_pass": r_openai.should_pass if r_openai else None,
            "azure_classification": r_azure.classification if r_azure else None,
            "azure_should_pass": r_azure.should_pass if r_azure else None,
        })

    with open("er006_output/pool_pilot_01/evidence_density_ab_01/openai_ja_asr_quality_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("\nOPENAI_JA_ASR_QUALITY_TEST_DONE")


if __name__ == "__main__":
    run()
