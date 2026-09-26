# ============================================================
# er020_tts_retry_local_rewrite_01.py
# 管理ID: TTS-LOCAL-REWRITE-CONNECTED-SPEECH-PRODUCTION-WIRING-01
# ============================================================
# Production module(Trial格ではない、Production TTS retry primitiveの
# 共有実装)。ユーザー承認済み仕様(APPROVED_FOR_PRODUCTION):
#   A. cool-down(10分固定) + Local Rewrite(問題spanのみ) + Natural
#      English QA(Luna 1 call)を、attempt1/2 NG後の最終attempt前・
#      Human Review Lock到達前の回復経路として実装する。
#   B. attempt1 NG -> 即時attempt2 -> NG -> 10分cool-down -> attempt3
#      -> NGならLocal Rewrite(既存のPRODUCTION_MAX_TTS_ATTEMPTS=3
#      ループにそのまま乗せる、新規retry上限は追加しない)。
#   C. Connected Speech適用範囲(既決定、5 role適用/2 role非適用)。
#   D. Human Review Lock(er011_human_review_lock_01)の手前に本回復
#      経路を挟む(回復成功時はstatus="OK"を返しRESOLVEDのまま、回復
#      失敗時のみ既存のHUMAN_REVIEW_REQUIREDへ進む)。
#
# 設計方針(本ファイルが「role→適用判定を一箇所に集約」する単一の場所):
#   - connected_speech_enabled_for(segment_id)が、Full Story/Comment/
#     Preview/Topic intro/In One Line(5 role)についてのみTrueを返す
#     単一のSSOT関数。各Production呼び出し元は、経路ごとに個別の
#     ハードコードされた条件式を書く代わりに、必ずこの関数を参照する。
#   - cool-down・Local Rewrite回復も、同じ「enable_connected_speech_
#     equivalence_layer」引数値(=上記関数の戻り値)でゲートする(5 role
#     以外[Heading readout/Key Phrase/日本語segment]には一切影響しない、
#     既存の他の呼び出し元[約50ファイルの過去個別記事script等]は本引数
#     を渡さないため既定Falseのまま=挙動無変更)。
#
# Trial系譜(ロジックの移設元、read-onlyで参照するのみ・変更しない):
#   er020_tts_cooldown_local_rewrite_trial_01.py(cool-down設計、
#   identify_ng_span、Local Rewrite/局所QA原型、VALIDATED)
#   er020_tts_local_rewrite_natural_english_qa_trial_02.py(7 Gate QA
#   [Natural English Gateを含む]、複数候補比較、VALIDATED)
# 本ファイルはこれら2 Trialの検証済みロジックを、特定segment
# (Family X comment_4の"point/points")に限定しない汎用形へ一般化して
# Production module化したものである(Trialファイル自体は無変更のまま
# 併存させる、歴史的再現性のため)。

from __future__ import annotations

import difflib
import json
import re
import time
from datetime import datetime, timezone

import er003_v1_b1_scaffold_01_generate as b1s
import er006_preprod_hardening_01_validation as asr_validation
import er011_human_review_lock_01 as review_lock

MANAGEMENT_ID = "TTS-LOCAL-REWRITE-CONNECTED-SPEECH-PRODUCTION-WIRING-01"

# ============================================================
# Part A: cool-down(ユーザー正式決定、固定10分・短縮禁止)
# ============================================================
COOLDOWN_SECONDS = 600.0


def _now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def maybe_cooldown_before_attempt(attempt: int, max_attempts: int, cooldown_gate_enabled: bool,
                                   sleep_fn=time.sleep, cooldown_seconds: float = COOLDOWN_SECONDS) -> dict | None:
    """既存retryループの各attempt開始直前(TTS呼び出し前)に呼ぶ。
    cooldown_gate_enabled(=connected_speech_enabled_for(segment_id)の
    戻り値をそのまま渡す想定)がTrueかつ、これが合計3回以上のbudgetの
    最終attemptである場合のみ、実際に10分sleepする(attempt1->即時
    attempt2->NG->10分cool-down->attempt3、というユーザー承認済み順序)。
    それ以外(cooldown_gate_enabled=False、または最終attemptではない)は
    何もせずNoneを返す(既存の全呼び出し元の挙動を変えない)。"""
    if not cooldown_gate_enabled:
        return None
    if not (max_attempts >= 3 and attempt == max_attempts):
        return None
    cooldown_started_at = time.time()
    started_iso = _now_iso()
    sleep_fn(cooldown_seconds)
    cooldown_ended_at = time.time()
    return {
        "cooldown_requested_seconds": cooldown_seconds,
        "cooldown_actual_seconds": round(cooldown_ended_at - cooldown_started_at, 3),
        "cooldown_started_at": started_iso,
        "cooldown_ended_at": _now_iso(),
        "attempt_before_cooldown": attempt - 1,
        "attempt_after_cooldown": attempt,
    }


# ============================================================
# Part B: Connected Speech role taxonomy(単一のSSOT、role→適用判定を
# 一箇所に集約)
# ============================================================
# ユーザー承認済み範囲(2026-09-26): 適用する5 role。
CONNECTED_SPEECH_SEGMENT_IDS = frozenset({
    # Full Story(本文、3分割対応。point_one/two本文は既存OPEN-121/122
    # Production wiringで既にFull Story本文と同じ関数[news_tail_fix.
    # generate_news_narration_wide_margin]経由でTrueが適用済みのため、
    # 本タスクでは回帰させず同じFULL_STORY roleへ含める[既存動作維持、
    # 新規追加ではない])。
    "full_story_part1", "full_story_part2", "full_story_part3",
    "point_one", "point_two",
    # Comment
    "comment_1", "comment_2", "comment_3", "comment_4",
    # Preview
    "preview",
    # Topic intro
    "topic_intro",
    # In One Line
    "in_one_line",
})

# 非適用(ユーザー承認済み、明示的除外): Heading readout / Key Phrase。
NON_APPLICABLE_SEGMENT_IDS = frozenset({
    "point_one_heading", "point_two_heading",
})
_KEY_PHRASE_PATTERN = re.compile(r"^kp\d+_(en|ja)")


def resolve_narrative_role(segment_id: str | None) -> str | None:
    """segment_id -> role名(NARRATIVE_ENGLISH系5 role/HEADING_READOUT/
    KEY_PHRASE/None[未分類])を返す単一の判定関数。"""
    if not segment_id:
        return None
    if segment_id in ("full_story_part1", "full_story_part2", "full_story_part3",
                       "point_one", "point_two"):
        return "FULL_STORY"
    if segment_id in ("comment_1", "comment_2", "comment_3", "comment_4"):
        return "COMMENT"
    if segment_id == "preview":
        return "PREVIEW"
    if segment_id == "topic_intro":
        return "TOPIC_INTRO"
    if segment_id == "in_one_line":
        return "IN_ONE_LINE"
    if segment_id in NON_APPLICABLE_SEGMENT_IDS:
        return "HEADING_READOUT"
    if _KEY_PHRASE_PATTERN.match(segment_id or ""):
        return "KEY_PHRASE"
    return None


NARRATIVE_ENGLISH_ROLE_LABELS = {
    "FULL_STORY": "Full Story narration (the article's main narrated body, incl. Point body text)",
    "COMMENT": "Comment (a short narrator remark that recaps the story and bridges to the closing "
               "'In One Line' summary)",
    "PREVIEW": "Preview (a short teaser spoken before the full story)",
    "TOPIC_INTRO": "Topic intro (a short line announcing today's topic)",
    "IN_ONE_LINE": "In One Line (the closing one-line summary of the episode)",
}


def connected_speech_enabled_for(segment_id: str | None) -> bool:
    """呼び出し元は、経路ごとに個別のハードコード条件式("name in (...)"
    等)を書く代わりに、必ずこの1関数を参照すること(要件3、経路ごとの
    個別フラグ禁止)。"""
    return resolve_narrative_role(segment_id) in (
        "FULL_STORY", "COMMENT", "PREVIEW", "TOPIC_INTRO", "IN_ONE_LINE")


def role_label_for(segment_id: str | None) -> str:
    role = resolve_narrative_role(segment_id)
    return NARRATIVE_ENGLISH_ROLE_LABELS.get(role, f"segment '{segment_id}'")


# ============================================================
# Part C: NG span特定(canonical vs ASRの語差分、最小限の周辺のみ)
# ============================================================
# er020_tts_cooldown_local_rewrite_trial_01.identify_ng_span()と同一
# ロジック(VALIDATED、そのまま移設)。
def identify_ng_span(canonical_text: str, asr_text: str, context_words: int = 3) -> dict:
    canon_tokens = asr_validation.tokenize(canonical_text)
    asr_tokens = asr_validation.tokenize(asr_text or "")
    sm = difflib.SequenceMatcher(None, canon_tokens, asr_tokens)
    diff_ops = [op for op in sm.get_opcodes() if op[0] != "equal"]
    if not diff_ops:
        return {"found": False}
    tag, i1, i2, j1, j2 = diff_ops[0]
    ctx_start = max(0, i1 - context_words)
    ctx_end = min(len(canon_tokens), i2 + context_words)
    before_span_words = canon_tokens[ctx_start:ctx_end]
    changed_canon_words = canon_tokens[i1:i2]
    changed_asr_words = asr_tokens[j1:j2]
    asr_ctx_start = max(0, j1 - context_words)
    asr_ctx_end = min(len(asr_tokens), j2 + context_words)
    asr_span_with_context = " ".join(asr_tokens[asr_ctx_start:asr_ctx_end])
    return {
        "found": True,
        "diff_tag": tag,
        "canonical_span_with_context": " ".join(before_span_words),
        "asr_span_with_context": asr_span_with_context,
        "canonical_changed_words": changed_canon_words,
        "asr_changed_words": changed_asr_words,
        "context_window_word_indices": [ctx_start, ctx_end],
    }


_WORD_RE = re.compile(r"[A-Za-z']+")


def compute_unchanged_ratio(original_text: str, rewritten_text: str) -> float:
    orig_words = _WORD_RE.findall(original_text.lower())
    new_words = _WORD_RE.findall(rewritten_text.lower())
    sm = difflib.SequenceMatcher(None, orig_words, new_words)
    unchanged = sum(block.size for block in sm.get_matching_blocks())
    return round(unchanged / max(1, len(orig_words)), 4)


LOCAL_REWRITE_MIN_UNCHANGED_RATIO = 0.7
FULL_SEGMENT_PREFIX_CHECK_CHARS = 15


def validate_candidate_is_full_segment(canonical_text: str, rewritten_segment: str) -> bool:
    return (rewritten_segment[:FULL_SEGMENT_PREFIX_CHECK_CHARS].strip().lower()
            == canonical_text[:FULL_SEGMENT_PREFIX_CHECK_CHARS].strip().lower())


def _extract_json_object(raw_text: str) -> dict:
    text = raw_text.strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.MULTILINE)
    return json.loads(text)


# ============================================================
# Part D: 候補生成(Luna、json_schema strict、1 call、汎用spanベース)
# ============================================================
N_NEW_CANDIDATES_DEFAULT = 5

CANDIDATE_GEN_SYSTEM_PROMPT = (
    "You are a careful audio-script editor for an English learning podcast. "
    "You are given a short spoken English segment and a specific short span "
    "inside it that a speech recognizer keeps mis-transcribing (canonical vs. "
    "what the recognizer actually heard are both given to you). "
    "Propose exactly {n} different LOCAL rewrite candidates for the minimal "
    "problematic span only, NOT a rewrite of the whole segment. Each "
    "candidate must: "
    "(a) avoid the exact wording that keeps causing the ASR mismatch; "
    "(b) preserve the exact original meaning of the segment; "
    "(c) preserve the segment's role: {role_label}; "
    "(d) sound like natural, idiomatic spoken English that a native speaker "
    "would actually say in this exact context, not merely a grammatically "
    "valid paraphrase (you may restructure the short span, not just swap "
    "one word, if that is what natural English requires); "
    "(e) change only the minimal span needed (a single word if that is "
    "enough, or a short phrase of a few words if a single-word swap cannot "
    "fix the awkwardness); "
    "(f) introduce no new fact and drop no existing fact. "
    "Vary the style across the candidates: include at least one "
    "single-word-swap candidate and at least one short-phrase-rewrite "
    "candidate if plausible. "
    "CRITICAL FORMAT REQUIREMENT: the 'rewritten_segment' field for EACH "
    "candidate MUST be the ENTIRE original segment text given to you in the "
    "user message, reproduced VERBATIM character-for-character, with ONLY "
    "the problem span replaced by your candidate wording. Do NOT return "
    "just the replacement phrase by itself in 'rewritten_segment'. "
    "'changed_span_before' is the exact original phrase you replaced (a "
    "substring of the full segment); 'changed_span_after' is the exact "
    "replacement wording you inserted in its place. "
    "Return STRICT JSON only via the provided schema, no markdown fences, "
    "no commentary."
)


def build_candidate_gen_schema(n: int) -> dict:
    return {
        "name": "local_rewrite_candidates_production_01",
        "schema": {
            "type": "object",
            "properties": {
                "candidates": {
                    "type": "array",
                    "minItems": n,
                    "maxItems": n,
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "rewrite_type": {
                                "type": "string",
                                "enum": ["single_word_swap", "short_phrase_rewrite"],
                            },
                            "rewritten_segment": {"type": "string"},
                            "changed_span_before": {"type": "string"},
                            "changed_span_after": {"type": "string"},
                            "rationale": {"type": "string"},
                        },
                        "required": ["id", "rewrite_type", "rewritten_segment",
                                     "changed_span_before", "changed_span_after", "rationale"],
                        "additionalProperties": False,
                    },
                },
            },
            "required": ["candidates"],
            "additionalProperties": False,
        },
        "strict": True,
    }


def build_candidate_gen_prompt(segment_role_label: str, canonical_text: str, ng_span: dict,
                                context_before_text: str | None, context_after_text: str | None) -> str:
    lines = [f"Segment role: {segment_role_label}", ""]
    if context_before_text:
        lines += [f"Context immediately BEFORE this segment:\n\"{context_before_text}\"", ""]
    lines += [f"Full segment (contains the problem span):\n\"{canonical_text}\"", ""]
    if context_after_text:
        lines += [f"Context immediately AFTER this segment:\n\"{context_after_text}\"", ""]
    lines += [
        f"Problem span (a speech recognizer repeatedly mis-transcribes this as "
        f"{ng_span.get('asr_changed_words')!r} instead of {ng_span.get('canonical_changed_words')!r}):",
        f"\"{ng_span.get('canonical_span_with_context')}\"",
        "",
        "Propose the candidates as described in the system instructions. Return the JSON object.",
    ]
    return "\n".join(lines)


def call_luna_candidate_gen(client, segment_role_label: str, canonical_text: str, ng_span: dict,
                             context_before_text: str | None, context_after_text: str | None,
                             n: int = N_NEW_CANDIDATES_DEFAULT) -> dict:
    schema = build_candidate_gen_schema(n)
    prompt = build_candidate_gen_prompt(segment_role_label, canonical_text, ng_span,
                                        context_before_text, context_after_text)
    response = client.responses.create(
        model=b1s.MODEL,
        reasoning={"effort": b1s.REASONING_EFFORT},
        text={"format": {"type": "json_schema", **schema}},
        input=[
            {"role": "developer", "content": CANDIDATE_GEN_SYSTEM_PROMPT.format(
                n=n, role_label=segment_role_label)},
            {"role": "user", "content": prompt},
        ],
    )
    raw_text = (response.output_text or "").strip()
    parsed = _extract_json_object(raw_text)
    parsed["_raw_model_response_text"] = raw_text
    parsed["_model_id"] = response.model
    parsed["_response_id"] = response.id
    parsed["_prompt"] = prompt
    return parsed


# ============================================================
# Part E: 局所性チェック(harness側の機械判定、criterion 6/7)
# ============================================================
LOCALITY_WINDOW_TOKENS = 3


def find_problem_span_token_range(canonical_text: str, problem_span_text: str) -> dict:
    canon_tokens = asr_validation.tokenize(canonical_text)
    span_tokens = asr_validation.tokenize(problem_span_text)
    n = len(span_tokens)
    for i in range(len(canon_tokens) - n + 1):
        if canon_tokens[i:i + n] == span_tokens:
            return {"found": True, "start": i, "end": i + n, "canon_tokens": canon_tokens}
    return {"found": False, "start": None, "end": None, "canon_tokens": canon_tokens}


def check_locality(canonical_text: str, rewritten_segment: str, problem_span_range: dict) -> dict:
    canon_tokens = problem_span_range["canon_tokens"]
    new_tokens = asr_validation.tokenize(rewritten_segment)
    sm = difflib.SequenceMatcher(None, canon_tokens, new_tokens, autojunk=False)
    diff_ops = [op for op in sm.get_opcodes() if op[0] != "equal"]
    unchanged_ratio = compute_unchanged_ratio(canonical_text, rewritten_segment)
    criterion7_not_full_rewrite = unchanged_ratio >= LOCAL_REWRITE_MIN_UNCHANGED_RATIO
    if not diff_ops:
        return {"criterion6_localized_to_problem_span": False,
                "criterion6_reason": "no diff detected vs. canonical text (problem span left unmodified)",
                "criterion7_not_full_rewrite": criterion7_not_full_rewrite, "unchanged_ratio": unchanged_ratio}
    lo = min(op[1] for op in diff_ops)
    hi = max(op[2] for op in diff_ops)
    if problem_span_range["found"]:
        window_lo = max(0, problem_span_range["start"] - LOCALITY_WINDOW_TOKENS)
        window_hi = min(len(canon_tokens), problem_span_range["end"] + LOCALITY_WINDOW_TOKENS)
        localized = (lo >= window_lo) and (hi <= window_hi)
    else:
        window_lo, window_hi, localized = None, None, False
    return {"criterion6_localized_to_problem_span": localized,
            "criterion6_diff_token_range": [lo, hi], "criterion6_allowed_window": [window_lo, window_hi],
            "criterion7_not_full_rewrite": criterion7_not_full_rewrite, "unchanged_ratio": unchanged_ratio}


# ============================================================
# Part F: 局所QA(Luna、7項目のうち1-5、候補まとめて1 call)
# ============================================================
LOCAL_QA_SYSTEM_PROMPT = (
    "You are a strict QA reviewer for an English learning podcast script. "
    "You are given the original segment, its immediate context before/after "
    "(if provided), and several candidate local rewrites of one short span "
    "inside it. For EACH candidate, independently judge ALL of the following "
    "5 gates compared to the ORIGINAL segment (not to other candidates): "
    "(1) meaning_preserved: meaning is fully preserved (no new facts, no "
    "lost facts, no changed claims); "
    "(2) role_preserved: the segment's role/function in the episode is "
    "unchanged (given role: {role_label}); "
    "(3) fact_non_contradiction: it does not contradict anything the "
    "original segment or its surrounding context said; "
    "(4) context_connection: it still connects naturally to what comes "
    "immediately before and after it (if context was provided); "
    "(5) natural_english: this is an INDEPENDENT gate from mere grammatical "
    "correctness. PASS only if the phrase is something a native speaker "
    "would actually and commonly say in this exact spoken narration context. "
    "FAIL if it is grammatically possible but not something people usually "
    "say, if it is understandable but sounds unnatural or stilted, if it is "
    "acceptable to an LLM but not idiomatic, or if the wording looks chosen "
    "only to pass a speech-recognition check rather than because it is "
    "genuinely natural English. "
    "Return STRICT JSON only via the provided schema, no markdown fences, "
    "no commentary."
)


def build_qa_schema(n_total: int) -> dict:
    gate_item = {
        "type": "object",
        "properties": {"pass": {"type": "boolean"}, "reason": {"type": "string"}},
        "required": ["pass", "reason"],
        "additionalProperties": False,
    }
    return {
        "name": "local_rewrite_qa_five_llm_gates_production_01",
        "schema": {
            "type": "object",
            "properties": {
                "evaluations": {
                    "type": "array",
                    "minItems": n_total,
                    "maxItems": n_total,
                    "items": {
                        "type": "object",
                        "properties": {
                            "candidate_id": {"type": "string"},
                            "meaning_preserved": gate_item,
                            "role_preserved": gate_item,
                            "fact_non_contradiction": gate_item,
                            "context_connection": gate_item,
                            "natural_english": gate_item,
                        },
                        "required": ["candidate_id", "meaning_preserved", "role_preserved",
                                     "fact_non_contradiction", "context_connection", "natural_english"],
                        "additionalProperties": False,
                    },
                },
            },
            "required": ["evaluations"],
            "additionalProperties": False,
        },
        "strict": True,
    }


def build_qa_prompt(segment_role_label: str, canonical_text: str, candidates: list,
                     context_before_text: str | None, context_after_text: str | None) -> str:
    lines = [f"Segment role: {segment_role_label}", ""]
    if context_before_text:
        lines += [f"Context immediately BEFORE:\n\"{context_before_text}\"", ""]
    lines += [f"ORIGINAL segment:\n\"{canonical_text}\"", ""]
    if context_after_text:
        lines += [f"Context immediately AFTER:\n\"{context_after_text}\"", ""]
    lines.append("Candidates to evaluate:")
    for c in candidates:
        lines.append(f"- candidate_id={c['id']!r}: \"{c['rewritten_segment']}\"")
    lines += ["", "Evaluate all 5 gates for every candidate and return the JSON object "
                   "described in the system instructions."]
    return "\n".join(lines)


def call_luna_local_qa(client, segment_role_label: str, canonical_text: str, candidates: list,
                        context_before_text: str | None, context_after_text: str | None) -> dict:
    schema = build_qa_schema(len(candidates))
    prompt = build_qa_prompt(segment_role_label, canonical_text, candidates,
                              context_before_text, context_after_text)
    response = client.responses.create(
        model=b1s.MODEL,
        reasoning={"effort": b1s.REASONING_EFFORT},
        text={"format": {"type": "json_schema", **schema}},
        input=[
            {"role": "developer", "content": LOCAL_QA_SYSTEM_PROMPT.format(role_label=segment_role_label)},
            {"role": "user", "content": prompt},
        ],
    )
    raw_text = (response.output_text or "").strip()
    parsed = _extract_json_object(raw_text)
    parsed["_raw_model_response_text"] = raw_text
    parsed["_model_id"] = response.model
    parsed["_response_id"] = response.id
    parsed["_prompt"] = prompt
    return parsed


def build_full_candidate_records(canonical_text: str, candidates: list, qa_evaluations: list,
                                  problem_span_range: dict) -> list:
    qa_by_id = {e["candidate_id"]: e for e in qa_evaluations}
    records = []
    for c in candidates:
        qa = qa_by_id.get(c["id"])
        is_full_segment = validate_candidate_is_full_segment(canonical_text, c["rewritten_segment"])
        locality = check_locality(canonical_text, c["rewritten_segment"], problem_span_range)
        gates = {
            "1_meaning_preserved": qa["meaning_preserved"]["pass"] if qa else None,
            "2_role_preserved": qa["role_preserved"]["pass"] if qa else None,
            "3_fact_non_contradiction": qa["fact_non_contradiction"]["pass"] if qa else None,
            "4_context_connection": qa["context_connection"]["pass"] if qa else None,
            "5_natural_english_gate": qa["natural_english"]["pass"] if qa else None,
            "6_localized_minimal_change": locality["criterion6_localized_to_problem_span"],
            "7_not_full_rewrite": locality["criterion7_not_full_rewrite"],
        }
        all_pass = qa is not None and is_full_segment and all(v is True for v in gates.values())
        record = dict(c)
        record["qa_llm"] = qa
        record["is_full_segment_format_valid"] = is_full_segment
        record["locality_check"] = locality
        record["seven_gates"] = gates
        record["all_seven_gates_pass"] = all_pass
        records.append(record)
    return records


def select_final_candidate(records: list) -> dict:
    passing = [r for r in records if r["all_seven_gates_pass"]]
    if not passing:
        return {"selected": None, "status": "NO_CANDIDATE_PASSED_ALL_SEVEN_GATES",
                "selection_rationale": "全候補が7 Gateのいずれかで不合格だったため、採用候補なし。"}

    def _key(r):
        return (-r["locality_check"]["unchanged_ratio"], r["id"])

    ranked = sorted(passing, key=_key)
    winner = ranked[0]
    rationale = (f"全7 Gate PASSの候補は{len(passing)}件({[r['id'] for r in passing]})。"
                 f"unchanged_ratio={winner['locality_check']['unchanged_ratio']}(最小限の変更)が最大の"
                 f"'{winner['id']}'を採用。Natural English Gate理由: "
                 f"{winner['qa_llm']['natural_english']['reason']}")
    return {"selected": winner, "status": "SELECTED", "selection_rationale": rationale,
            "all_passing_candidate_ids": [r["id"] for r in passing]}


# ============================================================
# Part G: 統合エントリポイント(Production呼び出し元から呼ぶ唯一の関数)
# ============================================================
def run_local_rewrite_recovery(*, segment_id: str, canonical_text: str, last_asr_text: str | None,
                                retts_fn, out_dir: str | None = None,
                                context_before_text: str | None = None,
                                context_after_text: str | None = None,
                                n_new_candidates: int = N_NEW_CANDIDATES_DEFAULT,
                                client=None) -> dict:
    """Human Review Lockへ到達する直前に、Production呼び出し元(generate_
    charon_english/generate_news_narration_wide_margin)から呼ぶ唯一の
    回復経路。retts_fn(rewritten_text:str)->dict は、呼び出し元が既に
    持つTTS+ASR生成ロジック(その関数自身の`.__wrapped__`をmax_attempts=1
    で呼ぶ、というProduction既存の設計パターン)をそのまま使う想定。

    戻り値のstatus:
      RESOLVED_BY_LOCAL_REWRITE  -> retts_fnがstatus=="OK"を返した
      HUMAN_REVIEW_LOCKED_NO_CANDIDATE_PASSED_QA -> 7 Gate全PASSの候補なし
      HUMAN_REVIEW_LOCKED_RETTS_FAILED -> 採用候補で再TTSしたが不合格
      HUMAN_REVIEW_LOCKED_NO_NG_SPAN -> canonical/ASR間に差分が見つからない
        (Local Rewriteの対象spanを機械的に特定できない)
    """
    role_label = role_label_for(segment_id)
    result: dict = {
        "management_id": MANAGEMENT_ID, "segment_id": segment_id, "segment_role_label": role_label,
        "canonical_text": canonical_text, "last_asr_text": last_asr_text,
        "ng_span": None, "candidate_gen": None, "qa": None, "candidates": None,
        "selection": None, "retts_result": None, "status": None,
    }
    ng_span = identify_ng_span(canonical_text, last_asr_text or "")
    result["ng_span"] = ng_span
    if not ng_span.get("found"):
        result["status"] = "HUMAN_REVIEW_LOCKED_NO_NG_SPAN"
        _append_recovery_history(result, out_dir)
        return result

    client = client or b1s.get_client()
    gen = call_luna_candidate_gen(client, role_label, canonical_text, ng_span,
                                   context_before_text, context_after_text, n=n_new_candidates)
    result["candidate_gen"] = gen
    candidates = gen["candidates"]

    problem_span_range = find_problem_span_token_range(
        canonical_text, " ".join(ng_span["canonical_changed_words"]))

    qa = call_luna_local_qa(client, role_label, canonical_text, candidates,
                             context_before_text, context_after_text)
    result["qa"] = qa

    records = build_full_candidate_records(canonical_text, candidates, qa["evaluations"], problem_span_range)
    result["candidates"] = records

    selection = select_final_candidate(records)
    result["selection"] = selection

    if selection["selected"] is None:
        result["status"] = "HUMAN_REVIEW_LOCKED_NO_CANDIDATE_PASSED_QA"
        _write_recovery_artifacts(result, out_dir)
        _append_recovery_history(result, out_dir)
        return result

    retts_result = retts_fn(selection["selected"]["rewritten_segment"])
    result["retts_result"] = retts_result
    if retts_result.get("status") == "OK":
        result["status"] = "RESOLVED_BY_LOCAL_REWRITE"
    else:
        result["status"] = "HUMAN_REVIEW_LOCKED_RETTS_FAILED"
    _write_recovery_artifacts(result, out_dir)
    _append_recovery_history(result, out_dir)
    return result


def _write_recovery_artifacts(result: dict, out_dir: str | None) -> None:
    if not out_dir:
        return
    import os
    os.makedirs(out_dir, exist_ok=True)
    with open(f"{out_dir}/local_rewrite_recovery_{result['segment_id']}.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)


def _append_recovery_history(result: dict, out_dir: str | None) -> None:
    """既存attempt履歴(er011_output/attempt_history.jsonl)へ、Local
    Rewrite回復イベントを追記型で記録する(既存フォーマットは変更せず、
    action="LOCAL_REWRITE_RECOVERY"の新規行として追加するのみ)。"""
    record = {
        "action": "LOCAL_REWRITE_RECOVERY",
        "timestamp": _now_iso(),
        "management_id": MANAGEMENT_ID,
        "segment_id": result.get("segment_id"),
        "segment_role_label": result.get("segment_role_label"),
        "ng_span_found": (result.get("ng_span") or {}).get("found"),
        "selection_status": (result.get("selection") or {}).get("status"),
        "selected_candidate_id": ((result.get("selection") or {}).get("selected") or {}).get("id"),
        "changed_span_before": ((result.get("selection") or {}).get("selected") or {}).get("changed_span_before"),
        "changed_span_after": ((result.get("selection") or {}).get("selected") or {}).get("changed_span_after"),
        "final_status": result.get("status"),
        "luna_model_id": (result.get("candidate_gen") or {}).get("_model_id"),
    }
    review_lock._append_attempt_history(record)
