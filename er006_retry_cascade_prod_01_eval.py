# ============================================================
# er006_retry_cascade_prod_01_eval.py
# ER-006-AUDIO-RETRY-CASCADE-PROD-01: 3 Topic Cascade評価
# ============================================================
# 既存音声fixtureへ、Primary#1(既に記録済みのASR結果を再利用) ->
# Primary#2 -> Secondary#1(+Phrase List) -> Secondary#2(+Phrase List)の
# Cascadeを適用する。新規TTS生成は行わない(§16「既存音声fixtureを
# 最大限利用」)。今回検証用に明示的にfeature flagを有効化する
# (Production defaultはOFFのまま、リポジトリ上は変更しない)。

from __future__ import annotations

import json
import sys

sys.path.insert(0, '.')
from dotenv import load_dotenv
load_dotenv()

import er005_cost_logger as cl
cl.install("er006_output/pool_pilot_01/raw_usage_log.jsonl")

import er006_asr_provider_routing_01 as routing
import er006_preprod_hardening_01_validation as val
import er006_pronunciation_ledger_01 as ledger
import er006_secondary_asr_01 as secondary

secondary.FEATURE_FLAG_SECONDARY_ASR_ENABLED = True  # このスクリプト実行時のみ検証用に有効化

TARGETS = [
    {
        "topic": "pool_benches", "name": "ottoni_b1_point_one",
        "wav": "er006_output/pool_pilot_01/pool_benches_pilot_02/b1b/narration/point_one.wav",
        "canonical": "er006_output/pool_pilot_01/pool_benches_pilot_02/b1b/parts.json:point_one_body",
        "entities": ["Ottoni"],
    },
    {
        "topic": "pool_benches", "name": "malmo_triangeln_b1_point_two",
        "wav": "er006_output/pool_pilot_01/pool_benches_pilot_02/b1b/narration/point_two.wav",
        "canonical": "er006_output/pool_pilot_01/pool_benches_pilot_02/b1b/parts.json:point_two_body",
        "entities": ["Malmö", "Triangeln", "MTA"],
    },
    {
        "topic": "pool_benches", "name": "boavida_a2_full_story_part2",
        "wav": "er006_output/pool_pilot_01/pool_benches_pilot_02/a2/narration/full_story_part2.wav",
        "canonical": "er006_output/pool_pilot_01/pool_benches_pilot_02/a2/parts.json:part2",
        "entities": ["Boavida"],
    },
    {
        "topic": "pool_subscriptions", "name": "comment_2_cancelling",
        "wav": "er006_output/pool_pilot_01/pool_subscriptions/b1b/narration/comment_2.wav",
        "canonical": "er006_output/pool_pilot_01/pool_subscriptions/b1b/b1_support_texts.json:comment_2",
        "entities": [],  # 固有名詞ではない(綴りvariant)、cascadeは発動しない想定
    },
    {
        "topic": "pool_subscriptions", "name": "full_story_part2_click_to_cancel",
        "wav": "er006_output/pool_pilot_01/pool_subscriptions/a2/narration/full_story_part2.wav",
        "canonical": "er006_output/pool_pilot_01/pool_subscriptions/a2/parts.json:part2",
        "entities": [],
    },
    {
        "topic": "pool_startups", "name": "katz_shapiro_a2_full_story_part1",
        "wav": "er006_output/pool_pilot_01/pool_startups/a2/narration/full_story_part1.wav",
        "canonical": "er006_output/pool_pilot_01/pool_startups/a2/parts.json:part1",
        "entities": ["Katz", "Shapiro"],
    },
]


def load_canonical(spec: str) -> str:
    path, key = spec.split(":")
    return json.load(open(path, encoding="utf-8"))[key]


results = []
for target in TARGETS:
    canonical_text = load_canonical(target["canonical"])
    ledger_phrases = []
    for e in target["entities"]:
        hits = ledger.get_hint_for_text(e, min_confidence="low")
        ledger_phrases.extend(h["canonical_spelling"] for h in hits)

    prior_results = []
    with cl.logging_context(target["topic"], "cascade_prod_eval_primary_1"):
        primary_1_text, err = routing.transcribe(target["wav"], language="en-US")

    with cl.logging_context(target["topic"], "cascade_prod_eval"):
        detail = secondary.evaluate_attempt_with_cascade_detail(
            canonical_text, primary_1_text, prior_results, target["wav"], language="en-US",
            ledger_phrases=ledger_phrases, cascade_enabled=True)

    entry = {
        "name": target["name"], "topic": target["topic"], "entities": target["entities"],
        "ledger_phrases_used": ledger_phrases,
        "canonical_text": canonical_text,
        "verified": detail["verified"], "cascade_invoked": detail["cascade_invoked"],
        "human_review_required": detail["human_review_required"],
        "final_status": detail["final_status"],
        "steps": detail["steps"],
    }
    results.append(entry)
    print(f"[{target['name']}] verified={entry['verified']} cascade_invoked={entry['cascade_invoked']} "
          f"final={entry['final_status']} steps={[s['step'] for s in entry['steps']]}")

with open("er006_output/audio_retry_cascade_prod_01/three_topic_eval.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2, default=str)
print("CASCADE_PROD_EVAL_DONE")
