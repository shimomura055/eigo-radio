# ============================================================
# er005_avr02_run.py
# ER-005-AUDIO-VALIDATION-ROBUSTNESS-02: Controlled A/B test 実行
# ============================================================
from __future__ import annotations

import json

import er002_common as common
import er003_b1_p3y_audio as p3y
import er005_avr02_instruction_separation as avr02

OUT_DIR = "er005_output/audio_validation_robustness_02"

EN_STYLE_PREFIX = common.build_style_prefix()
JA_STYLE_PREFIX = p3y.build_japanese_style_prefix()

TOPIC_INTRO_TEXT = "Today's topic is When Family Tension Meets Screen Time: A Study of Young Children."
POINT_ONE_TEXT = ("A closer parent-child relationship was linked with fewer behavior problems. "
                   "But closeness did not significantly predict later screen time. So, feeling close "
                   "and having conflict were not simply two opposite roads to the same result.")
FULL_STORY_PART1_TEXT = (
    "A quiet question at home may become an important research question: What happens when a young "
    "child often has conflict with a parent? A 2026 study looked at this question through family "
    "relationships, screen time, and children's behavior. The study followed children aged 3 to 6 in "
    "Fuyang, Anhui, China. The final analysis included 532 children. Their mothers answered questions "
    "about the children and their family relationships. The researchers collected information 3 times. "
    "Each check was 4 months apart. They asked about 2 parts of the parent-child relationship: closeness "
    "and conflict. They also asked about the children's daily screen time and behavior problems. The "
    "main result was clear in its direction."
)
KP5_EN_TEXT = "association"
KP5_JA_TEXT = "関連・相関"

PLAN = [
    dict(segment_name="a2_topic_intro", text=TOPIC_INTRO_TEXT, style_prefix=EN_STYLE_PREFIX,
         voice="Aoede", language="en", n_trials=3),
    dict(segment_name="a2_point_one", text=POINT_ONE_TEXT, style_prefix=EN_STYLE_PREFIX,
         voice="Aoede", language="en", n_trials=3),
    dict(segment_name="a2_full_story_part1", text=FULL_STORY_PART1_TEXT, style_prefix=EN_STYLE_PREFIX,
         voice="Aoede", language="en", n_trials=2),
    dict(segment_name="kp5_en_association", text=KP5_EN_TEXT, style_prefix=EN_STYLE_PREFIX,
         voice="Aoede", language="en", n_trials=5),
    dict(segment_name="kp5_ja_association", text=KP5_JA_TEXT, style_prefix=JA_STYLE_PREFIX,
         voice="Charon", language="ja", n_trials=5),
]

if __name__ == "__main__":
    all_results = []
    for spec in PLAN:
        r = avr02.run_segment_trials(**spec)
        all_results.append(r)
        with open(f"{OUT_DIR}/avr02_trial_results.json", "w", encoding="utf-8") as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2, default=str)
    print("ALL DONE")
