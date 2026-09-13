# ============================================================
# er013_family_c_future_spark_gate_06.py
# 管理ID: EDITORIAL-FUTURE-FAMILY-C-V6-CORE-PROVOCATION-REDESIGN-TRIAL-06
# ============================================================
# 目的: ユーザー最重要原則「QAが全部PASSでも、読んで面白くなければFAIL」
# を実装するGate。Fact/Ledger/Framing/語数より**先に**実行する
# (Story Spark Gateを最上位に置く)。
#
# 5軸(各0〜3): Future Leap / Curiosity / Emotional Pull /
# Thought-provokingness / Core Provocation clarity。
# PASS基準: 5軸すべて2以上 かつ Future Leap>=2(委任文の記載通り、
# 後者は前者に包含されるが明示チェックとして残す)。
# PASS/FAILの最終判定は、LLMの自己申告ではなく、返ってきたスコアから
# **このモジュール(コード)側で決定的に**計算する(v5構造Gate等、既存の
# 「決定的コードGate」文化を踏襲)。
#
# 3 Voices補助判定: 3方向がCore Provocationを強めているか/薄めているかを
# 併せて判定し、薄めている場合は「3 Voices希釈」に分類する。
#
# 既存er013_family_c_future_*_01〜05.pyは一切編集しない(新規ファイル)。
# Status: Trial専用、未承認draft実装(`APPROVED_FOR_PRODUCTION`ではない)。
# ============================================================
from __future__ import annotations

import json

AXES = ["future_leap", "curiosity", "emotional_pull", "thought_provoking", "core_provocation_clarity"]

SPARK_GATE_JSON_SCHEMA = {
    "name": "story_spark_gate",
    "schema": {
        "type": "object",
        "properties": {
            "future_leap": {"type": "integer"},
            "future_leap_evidence_quote": {"type": "string"},
            "curiosity": {"type": "integer"},
            "curiosity_evidence_quote": {"type": "string"},
            "emotional_pull": {"type": "integer"},
            "emotional_pull_evidence_quote": {"type": "string"},
            "thought_provoking": {"type": "integer"},
            "thought_provoking_evidence_quote": {"type": "string"},
            "core_provocation_clarity": {"type": "integer"},
            "core_provocation_clarity_evidence_quote": {"type": "string"},
            "one_sentence_why_interesting": {"type": "string"},
            "three_directions_check": {
                "type": "object",
                "properties": {
                    "directions_found": {"type": "array", "items": {"type": "string"}},
                    "reinforces_core_provocation": {"type": "boolean"},
                    "dilution_note": {"type": "string"},
                },
                "required": ["directions_found", "reinforces_core_provocation", "dilution_note"],
                "additionalProperties": False,
            },
        },
        "required": AXES + [
            "future_leap_evidence_quote", "curiosity_evidence_quote", "emotional_pull_evidence_quote",
            "thought_provoking_evidence_quote", "core_provocation_clarity_evidence_quote",
            "one_sentence_why_interesting", "three_directions_check",
        ],
        "additionalProperties": False,
    },
    "strict": True,
}

SPARK_GATE_DEVELOPER_MESSAGE = (
    "You are an independent human-reader-experience judge for a short English-learning "
    "article. You do NOT check facts, word count, or grammar here. You only judge "
    "whether a real reader would find this genuinely interesting, exciting, and "
    "thought-provoking to read -- exactly like a human reading it for pleasure, not "
    "like a QA checklist. Read the article once, as a human reader would, then score it "
    "honestly. A technically correct but boring or already-obvious article must score "
    "low on Future Leap and Curiosity, even if nothing is factually wrong with it."
)

SPARK_GATE_PROMPT_TEMPLATE = """[Core Provocation this article was supposed to deliver]
{core_provocation}

[Article -- reader-facing text, markers already removed]
{reader_text}

Score the article on each axis from 0 (not at all) to 3 (very strongly):
- future_leap: Is this genuinely a leap beyond what ordinarily already happens today,
  or does it just describe something already common in some places right now? (0 =
  basically already happening today, 3 = a genuine leap)
- curiosity: Do you want to keep reading / think about what happens next?
- emotional_pull: Is there real excitement, tension, unease, or surprise -- not just a
  flat description?
- thought_provoking: Does it leave a real question in your mind after reading, not just
  a tidy wrap-up?
- core_provocation_clarity: Could you explain in one sentence what makes this article
  interesting, based only on reading it (not based on being told the Core Provocation
  in advance)?

For each axis, quote the exact sentence(s) from the article that most support your
score.

Then write one_sentence_why_interesting: your own one-sentence answer, purely as a
reader, to 'what is interesting about this article?'.

Finally, in three_directions_check: identify which distinct angles/threads you can see
in the article (if any -- there might be one, two, three, or none clearly separable),
and judge whether they reinforce the SAME Core Provocation from different angles
(reinforces_core_provocation=true), or whether they scatter into unrelated side-stories
that weaken the Core Provocation (reinforces_core_provocation=false). Explain briefly
in dilution_note."""


def build_spark_gate_prompt(core_provocation: str, reader_text: str) -> str:
    return SPARK_GATE_PROMPT_TEMPLATE.format(core_provocation=core_provocation, reader_text=reader_text)


def run_story_spark_gate(client, model: str, reasoning_effort: str, prompt: str) -> dict:
    response = client.responses.create(
        model=model,
        reasoning={"effort": reasoning_effort},
        text={"format": {"type": "json_schema", **SPARK_GATE_JSON_SCHEMA}},
        input=[
            {"role": "developer", "content": SPARK_GATE_DEVELOPER_MESSAGE},
            {"role": "user", "content": prompt},
        ],
    )
    text = response.output_text
    if not text or not text.strip():
        raise RuntimeError("Story Spark Gate応答が空です")
    parsed = json.loads(text)
    return {"parsed": parsed, "model": response.model, "response_id": response.id}


def compute_verdict(parsed: dict) -> dict:
    """PASS/FAILをコード側で決定的に計算する(LLMの自己申告に依存しない)。"""
    scores = {axis: int(parsed[axis]) for axis in AXES}
    all_axes_ge_2 = all(v >= 2 for v in scores.values())
    future_leap_ge_2 = scores["future_leap"] >= 2
    verdict = "PASS" if (all_axes_ge_2 and future_leap_ge_2) else "FAIL"
    three = parsed.get("three_directions_check", {})
    voices_diluted = three.get("reinforces_core_provocation") is False
    return {
        "verdict": verdict, "scores": scores,
        "all_axes_ge_2": all_axes_ge_2, "future_leap_ge_2": future_leap_ge_2,
        "voices_diluted": voices_diluted,
        "one_sentence_why_interesting": parsed.get("one_sentence_why_interesting"),
        "three_directions_check": three,
    }


FAILURE_CAUSE_CATEGORIES = [
    "Core Provocation弱い", "Future Leap不足", "Evidenceに引っ張られた",
    "Writerで弱まった", "QAで削られた", "3 Voicesで希釈", "Prompt制約過多",
]


def classify_failure_cause(verdict_result: dict) -> dict:
    """委任文で指定された7分類への、単純なヒューリスティック分類
    (厳密な因果診断ではなく、次の最小改善Trialの方向を選ぶための運用分類)。"""
    scores = verdict_result["scores"]
    if scores["future_leap"] < 2:
        category = "Future Leap不足"
        reason = f"future_leap={scores['future_leap']}(<2)。冒頭または全体が現在でも起こり得る話に留まっている。"
    elif scores["core_provocation_clarity"] < 2:
        category = "Core Provocation弱い"
        reason = f"core_provocation_clarity={scores['core_provocation_clarity']}(<2)。中心の問いが記事から読み取りにくい。"
    elif verdict_result["voices_diluted"]:
        category = "3 Voicesで希釈"
        reason = "three_directions_check.reinforces_core_provocation=false。複数の角度が別々の話に分散している。"
    elif scores["emotional_pull"] < 2 or scores["curiosity"] < 2:
        category = "Writerで弱まった"
        reason = f"emotional_pull={scores['emotional_pull']}, curiosity={scores['curiosity']}のいずれかが弱い。"
    elif scores["thought_provoking"] < 2:
        category = "Writerで弱まった"
        reason = f"thought_provoking={scores['thought_provoking']}(<2)。読後に残る問いが弱い。"
    else:
        category = "Writerで弱まった"
        reason = "個別軸は2以上だが総合PASS基準を満たさない組み合わせ(要目視確認)。"
    return {"category": category, "reason": reason, "all_categories_considered": FAILURE_CAUSE_CATEGORIES}
