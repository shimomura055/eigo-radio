# comment_1の「後に」解決という、OPEN-111本体の判定について、
# 同一入力に対するReading Resolverの選択がどれだけ安定しているかを
# 追加測定する(5回反復)。新規TTS/ASR呼び出しはなし、LLM呼び出しのみ。
from __future__ import annotations

import json
import os

import er011_no18_a2_reading_resolver_trial_07 as t07

OUT_DIR = t07.OUT_DIR

A2_AUDIT_PATH = "er006_output/pool_pilot_01/pool_n18_notifications_specfix_v2/a2/audit/tts_generation_results.json"
audit = json.load(open(A2_AUDIT_PATH, encoding="utf-8"))
c1_asr_text = audit["segments"]["comment_1"]["standard_attempts_log"][-1]["asr_text"]

candidates = t07.single_char_candidates("後")
N = 5
selections = []
for i in range(N):
    result = t07.call_resolver(c1_asr_text, "後に", candidates)
    selections.append(result["selected_reading"])
    print(i + 1, result["selected_reading"])

from collections import Counter
counts = Counter(selections)

out = {
    "target": "comment_1 ASR text, target_word=後に",
    "candidates": candidates,
    "n_trials": N,
    "selections": selections,
    "counts": dict(counts),
    "majority": counts.most_common(1)[0][0],
    "correct_answer": "あと",
    "majority_correct": counts.most_common(1)[0][0] == "あと",
    "agreement_rate_with_correct": selections.count("あと") / N,
}
with open(f"{OUT_DIR}/consistency_check_comment1.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print(json.dumps(out, ensure_ascii=False, indent=2))
