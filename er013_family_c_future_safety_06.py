# ============================================================
# er013_family_c_future_safety_06.py
# 管理ID: EDITORIAL-FUTURE-FAMILY-C-V6-CORE-PROVOCATION-REDESIGN-TRIAL-06
# ============================================================
# 目的: 新Fact Safetyレイヤー(3層)を実装する。
#   1. CURRENT FACT      : [[FACT: ref_id]]...[[/FACT]]で明示された文のみ。
#                          既存Fact Checker A'(er002_ja_web_research_r3、
#                          無改変)へそのまま渡し、Layer1 Ledger Deviation
#                          Checker(er003_v1_en_direct_vfl_01_generate、
#                          無改変)も適用する。判定は緩和しない。
#   2. PLAUSIBILITY BRIDGE: FACT/IMAGINEDのどちらにも入っていない、両者を
#                          つなぐ地の文。LLMで「完全飛躍でないか」だけを
#                          軽く判定する(事実検証はしない)。
#   3. IMAGINED FUTURE    : [[IMAGINED: timeframe]]...[[/IMAGINED]]の中身。
#                          予測精度はFact Checkしない。決定的機械チェック
#                          2点(FACTマーカー混入なし/timeframe必須)＋
#                          LLM軽判定(現在事実のように誤記していないか/
#                          明確に架空未来と分かるか)のみ。
#
# 既存er013_family_c_future_*_01〜05.pyは一切編集しない(新規ファイル、
# 抽出関数はqa_01/qa_02から無改変import再利用)。Fact Checker A'の判定
# 基準・閾値は一切緩めない。
# Status: Trial専用、未承認draft実装(`APPROVED_FOR_PRODUCTION`ではない)。
# ============================================================
from __future__ import annotations

import json
import re

import er002_ja_web_research_r3 as r3
import er003_v1_en_direct_vfl_01_generate as vfl01
import er005_cost_logger as cl
import er006_model_routing_contract_01 as routing
import er013_family_c_future_qa_01 as fcq1
import er013_family_c_future_qa_02 as fcq2
import er013_family_c_future_writer_02 as fcw2

# ------------------------------------------------------------
# レイヤー分離(FACT/IMAGINED抽出はqa_01/qa_02を無改変で再利用)
# ------------------------------------------------------------
_WHOLE_FACT_BLOCK_RE = re.compile(r"\[\[FACT:\s*[^\]]*\]\].*?\[\[/FACT\]\]", re.DOTALL)
_WHOLE_IMAGINED_BLOCK_RE = re.compile(r"\[\[IMAGINED:\s*[^\]]*\]\].*?\[\[/IMAGINED\]\]", re.DOTALL)


def extract_layers(article_text_with_markers: str) -> dict:
    text_no_meta = fcq2.strip_meta_blocks(article_text_with_markers)
    fact_blocks = fcq2.extract_fact_blocks(text_no_meta)
    imagined_blocks = fcq1.extract_imagined_blocks(text_no_meta)
    # bridge_text: FACT/IMAGINEDブロック全体(開始〜終了マーカー含む)を
    # 除去して残った、両者をつなぐ地の文。
    bridge_text = _WHOLE_FACT_BLOCK_RE.sub("", text_no_meta)
    bridge_text = _WHOLE_IMAGINED_BLOCK_RE.sub("", bridge_text)
    reader_text = fcq1.strip_markers_for_reader(text_no_meta)
    reader_text = fcq2.strip_fact_markers_keep_body(reader_text)
    return {
        "text_no_meta": text_no_meta, "fact_blocks": fact_blocks, "imagined_blocks": imagined_blocks,
        "bridge_text": bridge_text.strip(), "reader_text": reader_text.strip(),
    }


# ------------------------------------------------------------
# Layer 1: CURRENT FACT(既存Fact Checker A' + Layer1 Ledger Deviationを
# そのまま使用、緩和なし)
# ------------------------------------------------------------
_SPECULATIVE_HINT_WORDS = ["future", "imagined", "will be", "one day", "someday", "in 20"]


def _classify_issue(issue_text: str) -> str:
    lowered = (issue_text or "").lower()
    if any(w in lowered for w in _SPECULATIVE_HINT_WORDS):
        return "IMAGINED側の誤混入疑い(要目視確認)"
    return "CURRENT FACTに対する指摘"


def run_current_fact_layer(client, theme_id: str, topic_ja_placeholder: str,
                            fact_blocks: list, layer1_ledger_text: str) -> dict:
    current_fact_text = "\n".join(f"- {b['body']}" for b in fact_blocks) or "(この記事にCURRENT FACT文はありません)"
    fc_prompt = r3.build_fact_check_prompt(topic_ja_placeholder, current_fact_text, writer_sources=[])
    fc_model = routing.require_model("WRITER_FACT_CHECK", routing.WRITER_FACT_CHECK_MODEL)
    with cl.logging_context(theme_id, "safety_current_fact_check"):
        (fc_parsed, fc_final_status, fc_attempts_detail, fc_used_model, fc_response_id,
         fc_search_usage, fc_sources) = r3.run_fact_checker_with_gates(
            lambda: r3.make_fact_checker_fn(fc_prompt, client=client, model=fc_model, reasoning_effort="high"))
    if fc_final_status != "FACT_CHECK_COMPLETED":
        raise RuntimeError(f"Fact Checker A'技術的失敗: {fc_final_status}(attempts={fc_attempts_detail})")

    deviation_result = {"skipped": True, "reason": "この記事にCURRENT FACT文がないため対象外"}
    if fact_blocks:
        with cl.logging_context(theme_id, "safety_layer1_deviation_check"):
            deviation_result = vfl01.run_deviation_check(
                client, layer1_ledger_text, current_fact_text, model=vfl01.MODEL, hook_aware=False)

    issue_classification = {
        "contradictions": [{"text": t, "classification": _classify_issue(t)} for t in fc_parsed["contradictions"]],
        "unsupported_specific_claims": [{"text": t, "classification": _classify_issue(t)}
                                         for t in fc_parsed["unsupported_specific_claims"]],
    }
    return {
        "current_fact_text": current_fact_text, "fact_check": {
            "parsed": fc_parsed, "final_status": fc_final_status, "model": fc_used_model,
            "response_id": fc_response_id, "search_usage": fc_search_usage,
        },
        "issue_classification": issue_classification,
        "layer1_deviation_check": deviation_result,
        "layer_pass": fc_parsed["verdict"] != "FAIL",
    }


# ------------------------------------------------------------
# Layer 2: PLAUSIBILITY BRIDGE(LLM軽判定「完全飛躍でないか」のみ)
# ------------------------------------------------------------
BRIDGE_JSON_SCHEMA = {
    "name": "plausibility_bridge_check",
    "schema": {
        "type": "object",
        "properties": {
            "complete_leap_detected": {"type": "boolean"},
            "flagged_sentences": {"type": "array", "items": {"type": "string"}},
            "notes": {"type": "string"},
        },
        "required": ["complete_leap_detected", "flagged_sentences", "notes"],
        "additionalProperties": False,
    },
    "strict": True,
}

BRIDGE_DEVELOPER_MESSAGE = (
    "You check ONLY one thing: whether the connecting narration below makes a "
    "completely unfounded leap from today's real technology to the imagined future, "
    "with no plausible bridge at all (for example, claiming a currently nonexistent "
    "capability as if it were an easy, obvious next step with zero explanation). You do "
    "not fact-check specific numbers, and you do not judge whether the future will "
    "actually happen -- only whether the connection is not a complete, unexplained leap."
)

BRIDGE_PROMPT_TEMPLATE = """[Connecting narration text -- everything in the article that is neither a marked \
CURRENT FACT sentence nor inside a marked imagined-future scene]
{bridge_text}

Is there a complete, unexplained leap from today's real technology to the imagined
future anywhere in this text? Flag any specific sentences that make such a leap."""


def run_plausibility_bridge_layer(client, model: str, reasoning_effort: str, bridge_text: str) -> dict:
    text_for_check = bridge_text.strip() or "(この記事にbridge文はありません)"
    prompt = BRIDGE_PROMPT_TEMPLATE.format(bridge_text=text_for_check)
    response = client.responses.create(
        model=model,
        reasoning={"effort": reasoning_effort},
        text={"format": {"type": "json_schema", **BRIDGE_JSON_SCHEMA}},
        input=[
            {"role": "developer", "content": BRIDGE_DEVELOPER_MESSAGE},
            {"role": "user", "content": prompt},
        ],
    )
    parsed = json.loads(response.output_text)
    return {"parsed": parsed, "model": response.model, "response_id": response.id,
            "layer_pass": not parsed["complete_leap_detected"]}


# ------------------------------------------------------------
# Layer 3: IMAGINED FUTURE(決定的機械チェック2点 + LLM軽判定)
# ------------------------------------------------------------
IMAGINED_LIGHT_JSON_SCHEMA = {
    "name": "imagined_future_light_check",
    "schema": {
        "type": "object",
        "properties": {
            "misrepresented_as_current_fact": {"type": "boolean"},
            "clearly_imagined": {"type": "boolean"},
            "notes": {"type": "string"},
        },
        "required": ["misrepresented_as_current_fact", "clearly_imagined", "notes"],
        "additionalProperties": False,
    },
    "strict": True,
}

IMAGINED_LIGHT_DEVELOPER_MESSAGE = (
    "You check ONLY two things about the imagined-future scene(s) below: (1) is any "
    "part of it written as if it is already true today (misrepresented_as_current_fact), "
    "and (2) would a reader clearly understand this is an imagined future, not a report "
    "of something that already exists (clearly_imagined)? Do NOT judge whether the "
    "prediction is accurate or realistic -- that is out of scope."
)

IMAGINED_LIGHT_PROMPT_TEMPLATE = """[Imagined future scene(s), marker timeframes included]
{imagined_text}"""


def run_imagined_future_layer(client, model: str, reasoning_effort: str, imagined_blocks: list) -> dict:
    decisive_1_issues = fcq2.check_fact_markers_inside_imagined(imagined_blocks)
    decisive_1_pass = len(decisive_1_issues) == 0
    decisive_2_missing_timeframe = [b for b in imagined_blocks if not (b.get("timeframe") or "").strip()]
    decisive_2_pass = len(decisive_2_missing_timeframe) == 0

    if imagined_blocks:
        imagined_text = "\n\n".join(f"(timeframe: {b['timeframe']})\n{b['body']}" for b in imagined_blocks)
    else:
        imagined_text = "(この記事に[[IMAGINED]]場面がありません)"
    prompt = IMAGINED_LIGHT_PROMPT_TEMPLATE.format(imagined_text=imagined_text)
    response = client.responses.create(
        model=model,
        reasoning={"effort": reasoning_effort},
        text={"format": {"type": "json_schema", **IMAGINED_LIGHT_JSON_SCHEMA}},
        input=[
            {"role": "developer", "content": IMAGINED_LIGHT_DEVELOPER_MESSAGE},
            {"role": "user", "content": prompt},
        ],
    )
    light_parsed = json.loads(response.output_text)
    return {
        "decisive_1_no_fact_marker_inside_imagined": {"pass": decisive_1_pass, "issues": decisive_1_issues},
        "decisive_2_timeframe_present": {
            "pass": decisive_2_pass,
            "missing_count": len(decisive_2_missing_timeframe),
        },
        "llm_light_judgment": {"parsed": light_parsed, "model": response.model, "response_id": response.id},
        "layer_pass": decisive_1_pass and decisive_2_pass,
    }


# ------------------------------------------------------------
# オーケストレーション
# ------------------------------------------------------------
def run_safety_boundary_check(client, theme_id: str, topic_ja_placeholder: str, judge_model: str,
                               judge_reasoning_effort: str, layers: dict, layer1_ledger_text: str) -> dict:
    current_fact_result = run_current_fact_layer(
        client, theme_id, topic_ja_placeholder, layers["fact_blocks"], layer1_ledger_text)
    bridge_result = run_plausibility_bridge_layer(
        client, judge_model, judge_reasoning_effort, layers["bridge_text"])
    imagined_result = run_imagined_future_layer(
        client, judge_model, judge_reasoning_effort, layers["imagined_blocks"])
    overall_pass = current_fact_result["layer_pass"] and bridge_result["layer_pass"] and imagined_result["layer_pass"]
    return {
        "current_fact_layer": current_fact_result,
        "plausibility_bridge_layer": bridge_result,
        "imagined_future_layer": imagined_result,
        "overall_pass": overall_pass,
        "current_fact_verdict_note": (
            "REVIEW_REQUIREDは緩和判定に置き換えていない。CURRENT FACTに対する指摘か、"
            "IMAGINED側の誤混入疑いかをissue_classificationへ機械的に分類して記録している。"
        ),
    }
