# -*- coding: utf-8 -*-
# ER-007-JA-ASR-VALIDATOR-REDESIGN-AND-CASCADE-01: Production配線後の
# 実音声smoke test。ASR_ROUTING["ja"]=openai_asr、FEATURE_FLAG_JA_PRIMARY_
# OPENAI=True配線後、Production call siteと全く同じ呼び出し方
# (routing.transcribe -> ja_secondary.evaluate_attempt_ja_with_cascade_detail、
# cascade_enabledは明示的に上書きしない)で、既存No.6 Delivery B1/A2の
# 実音声fixtureに対し意図通りOpenAI Primaryが呼ばれ、分類が破綻しないことを
# 確認する。新規TTSは一切生成しない。
import sys, json
sys.path.insert(0, '.')
import er005_cost_logger as cl
cl.install("er006_output/pool_pilot_01/coverage_gate_01/ja_cascade_production_on_verify_log.jsonl")

import er006_asr_provider_routing_01 as routing
import er007_ja_asr_validator_01 as javal
import er007_ja_secondary_asr_01 as ja_secondary

print(f"ASR_ROUTING['ja'] = {routing.ASR_ROUTING['ja']}")
assert routing.ASR_ROUTING["ja"]["provider"] == "openai_asr", "ja routing not on openai_asr"
print(f"FEATURE_FLAG_JA_PRIMARY_OPENAI = {ja_secondary.FEATURE_FLAG_JA_PRIMARY_OPENAI}")
assert ja_secondary.FEATURE_FLAG_JA_PRIMARY_OPENAI is True, "flag not enabled"

with open('er006_output/pool_pilot_01/pool_n6_delivery/b1b/audit/tts_generation_results.json', encoding='utf-8') as f:
    b1_data = json.load(f)
with open('er006_output/pool_pilot_01/pool_n6_delivery/a2/audit/tts_generation_results.json', encoding='utf-8') as f:
    a2_data = json.load(f)

CASES = []
for rank, kp in b1_data.get("key_phrases", {}).items():
    ja = kp.get("japanese", {})
    if ja.get("canonical_text"):
        CASES.append((f"B1 kp{rank}_ja_charon",
                      f"er006_output/pool_pilot_01/pool_n6_delivery/b1b/narration/kp{rank}_ja_charon.wav",
                      ja["canonical_text"]))
for name in ("preview", "comment_1", "comment_2"):
    seg = a2_data.get("segments", {}).get(name)
    if seg and seg.get("canonical_text"):
        CASES.append((f"A2 {name}",
                      f"er006_output/pool_pilot_01/pool_n6_delivery/a2/narration/{name}.wav",
                      seg["canonical_text"]))

for label, wav_path, canonical_text in CASES:
    print(f"\n=== {label} ===")
    print(f"canonical: {canonical_text!r}")
    asr_text, err = routing.transcribe(wav_path, language="ja-JP", timeout_seconds=90.0)
    print(f"Primary(OpenAI mini) ASR text: {asr_text!r} err={err}")

    base_cls = javal.classify_ja_asr_match(canonical_text, asr_text)
    print(f"base classification: {base_cls.classification} ratio={base_cls.similarity_ratio:.3f}")
    print(f"content_diffs: {base_cls.protected.content_diffs}")
    print(f"is_entity_like_mismatch_ja: {ja_secondary.is_entity_like_mismatch_ja(base_cls)}")

    # Production call siteと同じ呼び出し方(cascade_enabledは明示的に上書きしない、
    # モジュール既定値をそのまま使う)
    detail = ja_secondary.evaluate_attempt_ja_with_cascade_detail(
        canonical_text, asr_text, wav_path, cascade_enabled=ja_secondary.FEATURE_FLAG_JA_PRIMARY_OPENAI)
    print(f"cascade_invoked: {detail['cascade_invoked']}")
    print(f"final verified: {detail['verified']} stop_retrying: {detail['stop_retrying']} "
          f"final_status: {detail['final_status']} human_review_required: {detail['human_review_required']}")
    for step in detail["steps"]:
        print(f"  step={step['step']} provider={step['provider']} classification={step['classification']} "
              f"text={step.get('text','')!r}")
    print("TTS regenerations in this verification: 0 (既存音声を再利用するのみ)")
