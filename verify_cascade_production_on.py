# -*- coding: utf-8 -*-
# ER-006-GATE-EVIDENCE-REVIEW-CASCADE-ON-MATH-ADOPT-01 Part C-3検証
# FEATURE_FLAG_SECONDARY_ASR_ENABLED=Trueへ変更後、Production call siteと
# 全く同じ呼び出し方(cascade_enabled=secondary_asr.FEATURE_FLAG_SECONDARY_ASR_ENABLED、
# 明示的なTrue上書きはしない)で、既存No.6 Sweeny audio fixtureに対し
# Primary#1->Primary#2->Secondary#1->Secondary#2->Human Reviewの流れになり、
# TTS再生成が発生しないことを確認する。新規TTSは一切生成しない。
import sys, json
sys.path.insert(0, '.')
import er005_cost_logger as cl
cl.install("er006_output/pool_pilot_01/coverage_gate_01/cascade_production_on_verify_log.jsonl")

import er006_asr_provider_routing_01 as routing
import er006_preprod_hardening_01_validation as val
import er006_secondary_asr_01 as secondary_asr

print(f"FEATURE_FLAG_SECONDARY_ASR_ENABLED = {secondary_asr.FEATURE_FLAG_SECONDARY_ASR_ENABLED}")
assert secondary_asr.FEATURE_FLAG_SECONDARY_ASR_ENABLED is True, "flag not enabled"

CASES = [
    ("B1 full_story_part1", "er006_output/pool_pilot_01/pool_n6_delivery/b1b/narration/full_story_part1.wav",
     ("A package is on its way, but its next step is unclear.\n\nSo we open the tracking page. Then, a few "
      "minutes later, we check it again. Nothing may have changed. Still, the update button pulls us back.\n\n"
      "What looks like simple impatience may be part of a wider response to uncertain waiting.\n\nA 2025 "
      "longitudinal study by Howell and Sweeny, published in *Emotion*, followed three groups over periods "
      "ranging from several weeks to several months. They included voters waiting for the 2020 United States "
      "presidential election result, people waiting for their California bar exam results, and academic job "
      "applicants waiting for hiring decisions.\n\nThe pattern was clear: as people became more worried, they "
      "searched more often for news and updates.")),
    ("A2 full_story_part1", "er006_output/pool_pilot_01/pool_n6_delivery/a2/narration/full_story_part1.wav",
     ("Why do we open a delivery page again and again?\n\nThe answer may begin with the waiting, not the "
      "package.\n\nWhen the result is unknown, checking for new information can feel like taking a small "
      "action in a situation we cannot control.\n\nIn 2025, Howell and Sweeny reported a long-term study in "
      "*Emotion*. They followed three groups for several weeks or months: people waiting for the result of "
      "the 2020 U.S. presidential election, people waiting for California bar exam results, and people "
      "waiting for academic job decisions.\n\nThey found a clear pattern. As people’s worry grew, they "
      "checked the news and searched for updates more often.")),
]

for label, wav_path, canonical_text in CASES:
    print(f"\n=== {label} ===")
    asr_text, err = routing.transcribe(wav_path, language="en-US", timeout_seconds=300.0)
    print(f"Primary#1 ASR text: {asr_text!r}")
    base_cls = val.classify_asr_match(canonical_text, asr_text)
    print(f"base classification: {base_cls.classification}")
    print(f"content_word_diffs: {base_cls.protected.content_word_diffs}")
    print(f"is_entity_like_mismatch: {secondary_asr.is_entity_like_mismatch(base_cls)}")

    # Production call siteと同じ呼び出し方(cascade_enabledは明示的に上書きしない、
    # モジュール既定値をそのまま使う)
    detail = secondary_asr.evaluate_attempt_with_cascade_detail(
        canonical_text, asr_text, [], wav_path, language="en-US",
        ledger_phrases=[], cascade_enabled=secondary_asr.FEATURE_FLAG_SECONDARY_ASR_ENABLED)
    print(f"cascade_invoked: {detail['cascade_invoked']}")
    print(f"final verified: {detail['verified']} stop_retrying: {detail['stop_retrying']} "
          f"final_status: {detail['final_status']} human_review_required: {detail['human_review_required']}")
    tts_regenerations = 0  # このscriptはTTSを一切呼んでいない(既存音声を再利用するのみ)
    for step in detail["steps"]:
        print(f"  step={step['step']} provider={step['provider']} classification={step['classification']} "
              f"text={step.get('text','')!r}")
    print(f"TTS regenerations in this verification: {tts_regenerations}")
