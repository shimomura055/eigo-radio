# ============================================================
# er020_tts_local_rewrite_natural_english_qa_trial_02.py
# 管理ID: TTS-LOCAL-REWRITE-NATURAL-ENGLISH-QA-TRIAL-02(Trialのみ、最大
# VALIDATED、Production未配線)
# ============================================================
# DEV/Trial path。Production正式経路(er003_v1_sing01_voice01_generate.py・
# er011_human_review_lock_01.py・er007_*・er019_*)は一切変更しない
# (read-onlyでimportし、既存の単発TTS生成関数[voice01.generate_charon_
# english]・既存ASR照合[er006_preprod_hardening_01_validation.
# classify_asr_match]を呼び出すだけ)。前回harness
# (er020_tts_cooldown_local_rewrite_trial_01.py)もread-onlyでimportし、
# 純粋関数(compute_unchanged_ratio/LOCAL_REWRITE_MIN_UNCHANGED_RATIO/
# run_single_tts_attempt/identify_ng_span/_extract_json_object)のみ再利用
# する(そのモジュール自身のOUT_DIR/ATTEMPT_LOG_PATHは一切触らない)。
#
# 目的: 前回Trial(TTS-COOLDOWN-LOCAL-REWRITE-TRIAL-01)で「TTSが通った」
# 1語置換("main point"->"main idea")について、「TTSが通ること」と「英語
# として自然であること」は別問題だという指摘に基づき、Local Rewrite後・
# TTS前に独立したNatural English Gateを含む7項目QAを課し、複数候補を比較
# したうえで最終候補を選定し、選定候補のみを実際にTTS+ASRで検証する。
#
# 7 QA項目(ユーザー正式決定、ACTIVE_TASK_TC2.md/このファイルのdocstring
# に逐語転記):
#   1. 元の意味を保持 2. segment roleを保持 3. 記事Factと矛盾しない
#   4. 前後文脈と自然につながる
#   5. 英語として自然で一般的な言い回し(Natural English Gate)
#   6. 発音問題を起こしたword/span周辺だけを必要最小限変更
#   7. 不要な全文Rewriteをしない
# 1-5はLuna(LLM)判定、6-7はharness側の機械判定(token位置の局所性・
# unchanged_ratio閾値)。全7項目PASSの候補のみがTTSへ進める(FAIL候補は
# 一切TTSしない)。
#
# 安全性:
#   - Production module無変更(read-onlyでimportし、Review Lockデコレータ
#     の外側[.__wrapped__]のみ呼ぶ、前回Trialと同じ設計)。
#   - 出力は全てer020_output/tts_local_rewrite_natural_english_qa_trial_02/
#     配下の新規path。Family X/前回Trialの既存成果物には一切書き込まない
#     (前回Trialのartifactはread-onlyで参照するのみ)。
#   - 人的介入は一切行わない(human_interventionフィールドは常にFalse)。
#   - TTS_EXECUTION_MODE=STANDARD固定・BATCH禁止。budget-jpy 15円上限・
#     TTS attempt上限4(dry-runで事前表示、PM_GOVERNANCE 7-5)。予算超過時は
#     暴走(単発callで異常な跳ね上がり)の場合のみSTOPし、それ以外は
#     超過を記録して継続する(ACTIVE_TASK_TC2.md Guardrail節)。
#
# 実行方法:
#   .venv/Scripts/python.exe er020_tts_local_rewrite_natural_english_qa_trial_02.py \
#       --stage dry-run|run --budget-jpy 15 --max-tts-attempts 4

from __future__ import annotations

import argparse
import difflib
import json
import os
import time
from datetime import datetime, timezone

import er003_v1_b1_scaffold_01_generate as b1s
import er003_v1_n3_01_tts_generate as tts_gen
import er003_v1_sing01_voice01_generate as voice01
import er005_cost_logger as cl
import er006_preprod_hardening_01_validation as asr_validation
import er012_e_family_entertainment_two_level_runner_01 as e2l_runner
import er020_tts_cooldown_local_rewrite_trial_01 as prior_trial

MANAGEMENT_ID = "TTS-LOCAL-REWRITE-NATURAL-ENGLISH-QA-TRIAL-02"
OUT_DIR = "er020_output/tts_local_rewrite_natural_english_qa_trial_02"
ATTEMPT_LOG_PATH = f"{OUT_DIR}/attempt_log.jsonl"
COST_LOG_PATH = f"{OUT_DIR}/raw_usage_log.jsonl"

PRIOR_TRIAL_OUT_DIR = "er020_output/tts_cooldown_local_rewrite_trial_01"
FAMILY_X_B1B_DIR = "er019_output/family_x_pointless_trial_01/meta/b1b"

DEFAULT_BUDGET_JPY = 15.0
DEFAULT_MAX_TTS_ATTEMPTS = 4
LOCAL_TTS_ATTEMPT_CAP = 2  # 採用候補のみ、cool-downなしで最大2回

# 前回harnessの.__wrapped__技法をそのまま再利用(Review Lockデコレータの
# 外側を呼ぶことで、harness自身のattempt間retry制御とProduction側の
# 独自cost guardが二重に競合しないようにする)。
RAW_CHARON_ENGLISH = prior_trial.RAW_CHARON_ENGLISH


def _now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


# ============================================================
# Part A: 対象1件(Family X comment_4 canonical) + 前後文脈
# ============================================================
PROBLEM_SPAN_TEXT = "bring the main point together"


def load_target_and_context() -> dict:
    with open(f"{FAMILY_X_B1B_DIR}/audit/tts_generation_results.json", encoding="utf-8") as f:
        results = json.load(f)
    segs = results["segments"]
    return {
        "segment_id": "comment_4",
        "segment_role": "Comment(Story Recovery + Bridge to In One Line)",
        "canonical_text": segs["comment_4"]["canonical_text"],
        "context_before_segment_id": "full_story_part3",
        "context_before_text": segs["full_story_part3"]["canonical_text"],
        "context_after_segment_id": "in_one_line",
        "context_after_text": segs["in_one_line"]["canonical_text"],
        "problem_span_text": PROBLEM_SPAN_TEXT,
        "problem_span_ng_evidence": (
            "前回Trial(TTS-COOLDOWN-LOCAL-REWRITE-TRIAL-01)でattempt1-3すべてが"
            "ASR_VALIDATION_UNCERTAIN(ASRが一貫して'point'を'points'と聞き取る)"
            "で終わったことをharness自身のTTS/ASR呼び出しで再現済み"
            "(er020_output/tts_cooldown_local_rewrite_trial_01/run_summary.json)。"
        ),
        "source": (
            f"{FAMILY_X_B1B_DIR}/audit/tts_generation_results.json#segments."
            "{comment_4,full_story_part3,in_one_line}.canonical_text"
        ),
    }


def load_prior_main_idea_candidate() -> dict:
    """前回Trialで採用された1語置換(point->idea)をread-onlyで取得し、比較
    対象の候補として今回も同一の7 QAにかける(前回はNatural English Gateを
    独立Gateとして課していなかった)。"""
    with open(f"{PRIOR_TRIAL_OUT_DIR}/local_rewrite/rewrite_result.json", encoding="utf-8") as f:
        prior = json.load(f)
    with open(f"{PRIOR_TRIAL_OUT_DIR}/run_summary.json", encoding="utf-8") as f:
        prior_summary = json.load(f)
    return {
        "id": "candidate_main_idea_previous",
        "rewrite_type": "single_word_swap",
        "source": "TTS-COOLDOWN-LOCAL-REWRITE-TRIAL-01(read-only参照、変更なし)",
        "rewritten_segment": prior["rewritten_segment"],
        "changed_span_before": prior["changed_span_before"],
        "changed_span_after": prior["changed_span_after"],
        "rationale": (
            "前回Trialで採用された1語置換(point->idea)。当時のQAは意味保持/"
            "role/Fact非矛盾/前後接続の4項目のみで、Natural English Gateは"
            "独立Gateとして課されていなかった。今回は比較対象として同一の7 QA"
            "を適用する。"
        ),
        "prior_tts_result": {
            "final_status": prior_summary.get("final_status"),
            "classification": (prior_summary.get("retts_attempt") or {}).get("classification"),
            "asr_text": (prior_summary.get("retts_attempt") or {}).get("asr_text"),
        },
    }


# ============================================================
# Part B: Local Rewrite候補生成(Luna、json_schema strict、1 call)
# ============================================================
N_NEW_CANDIDATES = 5  # + 前回"main idea"版(read-only流用)= 合計6件(4〜6件の範囲内)

CANDIDATE_GEN_SYSTEM_PROMPT = (
    "You are a careful audio-script editor for an English learning podcast. "
    "You are given a short spoken English 'Comment' segment and a specific "
    "short phrase inside it that a speech recognizer keeps mis-transcribing: "
    "it repeatedly hears the word 'point' (singular) as its plural 'points', "
    "which causes repeated TTS/ASR validation failures. "
    f"Propose exactly {N_NEW_CANDIDATES} different LOCAL rewrite candidates "
    "for the minimal problematic phrase only ('bring the main point "
    "together'), NOT a rewrite of the whole segment. Each candidate must: "
    "(a) completely avoid the word 'point' in singular OR plural form in "
    "that phrase, to remove the ambiguity that keeps causing the ASR "
    "mismatch; "
    "(b) preserve the exact original meaning (this sentence sums up the "
    "story's key takeaway and bridges to the closing 'In One Line' "
    "summary); "
    "(c) preserve the segment's role (a narrator's Comment that recaps the "
    "story and leads into the closing one-line summary); "
    "(d) sound like natural, idiomatic spoken English that a native speaker "
    "would actually say in this exact context, not merely a grammatically "
    "valid paraphrase (note: the original phrase 'bring the main point "
    "together' is itself somewhat awkward English; you may restructure the "
    "short phrase, not just swap one word, if that is what natural English "
    "requires); "
    "(e) change only the minimal span needed (a single word if that is "
    "enough, or a short phrase of a few words if a single-word swap cannot "
    "fix the awkwardness); "
    "(f) introduce no new fact and drop no existing fact. "
    "Vary the style across the candidates: include at least one "
    "single-word-swap candidate and at least one short-phrase-rewrite "
    "candidate. "
    "CRITICAL FORMAT REQUIREMENT: the 'rewritten_segment' field for EACH "
    "candidate MUST be the ENTIRE original segment text given to you in the "
    "user message, reproduced VERBATIM character-for-character, with ONLY "
    "the problem phrase replaced by your candidate wording. Do NOT return "
    "just the replacement phrase by itself in 'rewritten_segment' -- it "
    "must be the full sentence(s) of the segment, unchanged outside the "
    "replaced span. 'changed_span_before' is the exact original phrase you "
    "replaced (a substring of the full segment); 'changed_span_after' is "
    "the exact replacement wording you inserted in its place. "
    "Return STRICT JSON only via the provided schema, no markdown fences, "
    "no commentary."
)


def build_candidate_gen_schema(n: int) -> dict:
    return {
        "name": "local_rewrite_candidates_natural_english_qa_trial_02",
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


def build_candidate_gen_prompt(target: dict) -> str:
    return (
        f"Segment role: {target['segment_role']}\n\n"
        f"Context immediately BEFORE this segment ({target['context_before_segment_id']}):\n"
        f"\"{target['context_before_text']}\"\n\n"
        f"Full segment ({target['segment_id']}, contains the problem phrase):\n"
        f"\"{target['canonical_text']}\"\n\n"
        f"Context immediately AFTER this segment ({target['context_after_segment_id']}):\n"
        f"\"{target['context_after_text']}\"\n\n"
        f"Problem phrase (ASR keeps mis-hearing 'point' as 'points' here):\n"
        f"\"{target['problem_span_text']}\"\n\n"
        f"Propose exactly {N_NEW_CANDIDATES} candidates as described in the "
        "system instructions. Return the JSON object described in the "
        "system instructions."
    )


def call_luna_candidate_gen(client, target: dict) -> dict:
    schema = build_candidate_gen_schema(N_NEW_CANDIDATES)
    prompt = build_candidate_gen_prompt(target)
    response = client.responses.create(
        model=b1s.MODEL,
        reasoning={"effort": b1s.REASONING_EFFORT},
        text={"format": {"type": "json_schema", **schema}},
        input=[
            {"role": "developer", "content": CANDIDATE_GEN_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )
    raw_text = (response.output_text or "").strip()
    parsed = prior_trial._extract_json_object(raw_text)
    parsed["_raw_model_response_text"] = raw_text
    parsed["_model_id"] = response.model
    parsed["_response_id"] = response.id
    parsed["_prompt"] = prompt
    return parsed


# ============================================================
# Part C: harness側の機械判定(criterion 6: 局所性 / criterion 7: 非全文)
# ============================================================
LOCALITY_WINDOW_TOKENS = 3  # 前回harnessのidentify_ng_span()と同じcontext_words


def find_problem_span_token_range(canonical_text: str, problem_span_text: str) -> dict:
    canon_tokens = asr_validation.tokenize(canonical_text)
    span_tokens = asr_validation.tokenize(problem_span_text)
    n = len(span_tokens)
    for i in range(len(canon_tokens) - n + 1):
        if canon_tokens[i:i + n] == span_tokens:
            return {"found": True, "start": i, "end": i + n, "canon_tokens": canon_tokens}
    return {"found": False, "start": None, "end": None, "canon_tokens": canon_tokens}


def check_locality(canonical_text: str, rewritten_segment: str, problem_span_range: dict) -> dict:
    """criterion 6(問題span周辺だけの必要最小限変更)とcriterion 7(不要な
    全文Rewriteをしない)をharness側で機械的に判定する。"""
    canon_tokens = problem_span_range["canon_tokens"]
    new_tokens = asr_validation.tokenize(rewritten_segment)
    sm = difflib.SequenceMatcher(None, canon_tokens, new_tokens, autojunk=False)
    diff_ops = [op for op in sm.get_opcodes() if op[0] != "equal"]

    unchanged_ratio = prior_trial.compute_unchanged_ratio(canonical_text, rewritten_segment)
    criterion7_not_full_rewrite = unchanged_ratio >= prior_trial.LOCAL_REWRITE_MIN_UNCHANGED_RATIO

    if not diff_ops:
        return {
            "criterion6_localized_to_problem_span": False,
            "criterion6_reason": "no diff detected vs. canonical text (problem span left unmodified)",
            "criterion7_not_full_rewrite": criterion7_not_full_rewrite,
            "unchanged_ratio": unchanged_ratio,
        }

    lo = min(op[1] for op in diff_ops)
    hi = max(op[2] for op in diff_ops)
    if problem_span_range["found"]:
        window_lo = max(0, problem_span_range["start"] - LOCALITY_WINDOW_TOKENS)
        window_hi = min(len(canon_tokens), problem_span_range["end"] + LOCALITY_WINDOW_TOKENS)
        localized = (lo >= window_lo) and (hi <= window_hi)
    else:
        window_lo, window_hi, localized = None, None, False

    return {
        "criterion6_localized_to_problem_span": localized,
        "criterion6_diff_token_range": [lo, hi],
        "criterion6_allowed_window": [window_lo, window_hi],
        "criterion7_not_full_rewrite": criterion7_not_full_rewrite,
        "unchanged_ratio": unchanged_ratio,
    }


# ============================================================
# Part D: TTS安定性の事前見立て(harness側、機械的な注記のみ。実TTS/ASRの
# 代わりにはならない)
# ============================================================
def tts_stability_heuristic(changed_span_after: str) -> dict:
    words = asr_validation.tokenize(changed_span_after)
    content_words = [w for w in words if w not in asr_validation._STOPWORDS]
    plural_s_risk_words = []
    word_final_plosive_words = []
    benign_pair_if_pluralized = {}
    for w in content_words:
        plus_s = w + "s"
        if asr_validation._singularize_simple(plus_s) == w:
            plural_s_risk_words.append(w)
            benign_pair_if_pluralized[w] = asr_validation._is_benign_plural_pair(w, plus_s)
        if w[-1:] in {"t", "d", "k", "p", "b", "g"}:
            word_final_plosive_words.append(w)
    return {
        "content_words_checked": content_words,
        "plural_s_risk_words": plural_s_risk_words,
        "word_final_plosive_consonant_words": word_final_plosive_words,
        "would_be_classified_benign_plural_pair_if_asr_added_s": benign_pair_if_pluralized,
        "caveat_diagnostic_evidence": (
            "本Trialで実行時に直接確認した事実: 'point'/'points'はer006_"
            "preprod_hardening_01_validation.protected_check()内では既に"
            "_is_benign_plural_pair()によりbenignな複数形ゆれと判定される"
            "(content_word_diffsに計上されない)。しかしclassify_asr_match()"
            "全体の結果は依然ASR_VALIDATION_UNCERTAINだった(正規化後の"
            "一致率0.96が合格閾値に届かないため)。よって「benign plural "
            "pairに該当する」ことは合格を保証しない。この見立ては機械的な"
            "ヒューリスティックの注記であり、最終判断は必ず実TTS/ASR結果"
            "(Part Fで採用候補のみに対して実行)で行う。"
        ),
    }


# ============================================================
# Part D-2: 安全網(実行時に発見したバグの再発防止)
# ============================================================
FULL_SEGMENT_PREFIX_CHECK_CHARS = 15


def validate_candidate_is_full_segment(canonical_text: str, rewritten_segment: str) -> bool:
    """実行時に発見したバグの再発防止用の安全網: 初回実行でLuna候補生成が
    'rewritten_segment'に全文ではなく置換phraseのみを返す不具合が起きた
    (プロンプトの指示不足が原因、プロンプト修正済み)。プロンプト修正後も
    将来的なモデル出力のゆれに備え、rewritten_segmentがcanonical_textと
    同じ書き出しを持つ(=全文である)ことを機械的に検証する。Falseの場合は
    その候補をformat不正としてall_seven_gates_pass判定から除外する
    (TTSへは絶対に渡さない)。"""
    return (rewritten_segment[:FULL_SEGMENT_PREFIX_CHECK_CHARS].strip().lower()
            == canonical_text[:FULL_SEGMENT_PREFIX_CHECK_CHARS].strip().lower())


# ============================================================
# Part E: 局所QA(Luna、7項目のうち1-5、候補まとめて1 call)
# ============================================================
LOCAL_QA_SYSTEM_PROMPT = (
    "You are a strict QA reviewer for an English learning podcast script. "
    "You are given the original segment, its immediate context before/after, "
    "and several candidate local rewrites of one short phrase inside it. For "
    "EACH candidate, independently judge ALL of the following 5 gates "
    "compared to the ORIGINAL segment (not to other candidates): "
    "(1) meaning_preserved: meaning is fully preserved (no new facts, no "
    "lost facts, no changed claims); "
    "(2) role_preserved: the segment's role/function in the episode is "
    "unchanged (a Comment that recaps the story and bridges to the closing "
    "'In One Line' must still read as that role); "
    "(3) fact_non_contradiction: it does not contradict anything the "
    "original segment or its surrounding context said; "
    "(4) context_connection: it still connects naturally to what comes "
    "immediately before and after it; "
    "(5) natural_english: this is an INDEPENDENT gate from mere grammatical "
    "correctness. PASS only if the phrase is something a native speaker "
    "would actually and commonly say in this exact spoken narration context. "
    "FAIL if it is grammatically possible but not something people usually "
    "say, if it is understandable but sounds unnatural or stilted, if it is "
    "acceptable to an LLM but not idiomatic, if it awkwardly preserves the "
    "original sentence structure just to minimize the edit, or if the "
    "wording looks chosen only to pass a speech-recognition check rather "
    "than because it is genuinely natural English. In your natural_english "
    "reason, explicitly say whether this candidate sounds more natural, "
    "equally natural, or less natural than a plain word-for-word swap of "
    "'point' -> 'idea' in the same sentence, and why. "
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
        "name": "local_rewrite_qa_five_llm_gates_trial_02",
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


def build_qa_prompt(target: dict, candidates: list) -> str:
    lines = [
        f"Segment role: {target['segment_role']}",
        "",
        f"Context immediately BEFORE ({target['context_before_segment_id']}):",
        f"\"{target['context_before_text']}\"",
        "",
        f"ORIGINAL segment ({target['segment_id']}):",
        f"\"{target['canonical_text']}\"",
        "",
        f"Context immediately AFTER ({target['context_after_segment_id']}):",
        f"\"{target['context_after_text']}\"",
        "",
        "Candidates to evaluate:",
    ]
    for c in candidates:
        lines.append(f"- candidate_id={c['id']!r}: \"{c['rewritten_segment']}\"")
    lines.append("")
    lines.append("Evaluate all 5 gates for every candidate and return the JSON object "
                  "described in the system instructions.")
    return "\n".join(lines)


def call_luna_local_qa(client, target: dict, candidates: list) -> dict:
    schema = build_qa_schema(len(candidates))
    prompt = build_qa_prompt(target, candidates)
    response = client.responses.create(
        model=b1s.MODEL,
        reasoning={"effort": b1s.REASONING_EFFORT},
        text={"format": {"type": "json_schema", **schema}},
        input=[
            {"role": "developer", "content": LOCAL_QA_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )
    raw_text = (response.output_text or "").strip()
    parsed = prior_trial._extract_json_object(raw_text)
    parsed["_raw_model_response_text"] = raw_text
    parsed["_model_id"] = response.model
    parsed["_response_id"] = response.id
    parsed["_prompt"] = prompt
    return parsed


# ============================================================
# Part F: 7 QA統合 + 最終候補選定
# ============================================================
def build_full_candidate_records(target: dict, candidates: list, qa_evaluations: list,
                                  problem_span_range: dict) -> list:
    qa_by_id = {e["candidate_id"]: e for e in qa_evaluations}
    records = []
    for c in candidates:
        qa = qa_by_id.get(c["id"])
        is_full_segment = validate_candidate_is_full_segment(target["canonical_text"], c["rewritten_segment"])
        locality = check_locality(target["canonical_text"], c["rewritten_segment"], problem_span_range)
        stability = tts_stability_heuristic(c["changed_span_after"])
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
        record["tts_stability_heuristic"] = stability
        record["seven_gates"] = gates
        record["all_seven_gates_pass"] = all_pass
        records.append(record)
    return records


def select_final_candidate(records: list) -> dict:
    """全7 GateをPASSした候補の中から最終採用候補を1件選ぶ。決定的な規則:
    (1) TTS安定性ヒューリスティックのrisk flag数が少ない方を優先(word-final
    plosive consonant/plural_s_risk、'point'型の失敗と同種の懸念が少ない
    候補を優先)、(2) 同点ならunchanged_ratioが高い方(より最小限の変更)、
    (3) それでも同点ならid昇順(再現性のための最終tie-break)。"""
    passing = [r for r in records if r["all_seven_gates_pass"]]
    if not passing:
        return {"selected": None, "status": "NO_CANDIDATE_PASSED_ALL_SEVEN_GATES",
                "selection_rationale": "全候補が7 Gateのいずれかで不合格だったため、採用候補なし。"}

    def risk_count(r):
        h = r["tts_stability_heuristic"]
        return len(h["plural_s_risk_words"]) + len(h["word_final_plosive_consonant_words"])

    ranked = sorted(
        passing,
        key=lambda r: (risk_count(r), -r["locality_check"]["unchanged_ratio"], r["id"]),
    )
    winner = ranked[0]
    rationale = (
        f"全7 Gate PASSの候補は{len(passing)}件({[r['id'] for r in passing]})。"
        f"その中でTTS安定性ヒューリスティックのrisk flag数が最少"
        f"(plural_s_risk={winner['tts_stability_heuristic']['plural_s_risk_words']}, "
        f"word_final_plosive={winner['tts_stability_heuristic']['word_final_plosive_consonant_words']})"
        f"かつunchanged_ratio={winner['locality_check']['unchanged_ratio']}(より最小限の変更)"
        f"である'{winner['id']}'を採用。Natural English Gateの理由: "
        f"{winner['qa_llm']['natural_english']['reason']}"
    )
    return {"selected": winner, "status": "SELECTED", "selection_rationale": rationale,
            "all_passing_candidate_ids": [r["id"] for r in passing]}


# ============================================================
# Part G: 採用候補のみTTS(STANDARD、attempt上限2、cool-downなし)
# ============================================================
def run_single_tts_attempt(canonical_text: str, out_path: str, attempt_number: int) -> dict:
    """前回harnessのrun_single_tts_attempt()と同一ロジック(そのまま再利用)。
    採用候補の実発話テキストをcanonical_text/ASR照合対象の両方として渡す。"""
    return prior_trial.run_single_tts_attempt(
        canonical_text, out_path, attempt_number, tts_gen.B1_PREVIEW_STYLE_PREFIX_CALM, True,
        input_text_override=tts_gen.tts_safe_number_words_en(tts_gen.tts_safe_en(canonical_text)),
    )


def append_attempt_records(records: list) -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(ATTEMPT_LOG_PATH, "a", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False, default=str) + "\n")


def _with_gap(records: list) -> list:
    prev_ts = None
    for r in records:
        ts = datetime.fromisoformat(r["timestamp"])
        r["gap_seconds_from_previous_attempt"] = (
            None if prev_ts is None else round((ts - prev_ts).total_seconds(), 3))
        prev_ts = ts
    return records


def run_selected_tts(selected: dict, target_out_dir: str, max_attempts: int = LOCAL_TTS_ATTEMPT_CAP) -> dict:
    rewritten_segment = selected["rewritten_segment"]
    records = []

    def _attempt(n: int) -> dict:
        wav_path = f"{target_out_dir}/attempt{n}/narration/comment_4.wav"
        rec = run_single_tts_attempt(rewritten_segment, wav_path, n)
        rec["candidate_id"] = selected["id"]
        rec["pre_rewrite_canonical_text"] = None  # 前回のような書き換え前canonicalは別文脈(本Trialでは候補=採用文そのもの)
        records.append(rec)
        append_attempt_records([rec])
        return rec

    r1 = _attempt(1)
    if r1["pass"]:
        return {"status": "PASS_AT_ATTEMPT_1", "attempts": _with_gap(records)}

    if max_attempts >= 2:
        r2 = _attempt(2)
        if r2["pass"]:
            return {"status": "PASS_AT_ATTEMPT_2", "attempts": _with_gap(records)}
        return {"status": "NG_AFTER_2_ATTEMPTS(HUMAN_REVIEW_LOCKED)", "attempts": _with_gap(records)}

    return {"status": "NG_AFTER_1_ATTEMPT(HUMAN_REVIEW_LOCKED)", "attempts": _with_gap(records)}


# ============================================================
# Part H: 予算Guardrail(超過時は原則継続、暴走疑いのみSTOP)
# ============================================================
def soft_budget_check(budget_jpy: float, note: str, prior_jpy: float) -> tuple:
    jpy, by_provider = e2l_runner.compute_cost_jpy_so_far(COST_LOG_PATH)
    delta = jpy - prior_jpy
    status = "OK"
    message = None
    if jpy > budget_jpy:
        if delta > budget_jpy * 2:
            status = "STOP_RUNAWAY_SUSPECTED"
            message = (f"[BUDGET][RUNAWAY_SUSPECTED] cost so far={jpy:.2f} JPY (cap {budget_jpy} JPY), "
                       f"single-step delta={delta:.2f} JPY looks anomalous. Stopping ({note}).")
        else:
            status = "OVER_BUDGET_CONTINUING"
            message = (f"[BUDGET][OVER_BUDGET_CONTINUING] cost so far={jpy:.2f} JPY exceeds cap "
                       f"{budget_jpy} JPY at step '{note}', but no runaway signal detected; "
                       "recording overage and continuing per Guardrail policy (not a hard stop).")
    print(f"[TTS-LOCAL-REWRITE-NATURAL-ENGLISH-QA-TRIAL-02][cost] so far={jpy:.2f} JPY "
          f"by_provider={by_provider} ({note}) status={status}")
    if message:
        print(message)
    if status == "STOP_RUNAWAY_SUSPECTED":
        raise RuntimeError(message)
    return jpy, status, message


# ============================================================
# Part I: dry-run(PM_GOVERNANCE 7-5)
# ============================================================
def run_dry_run(budget_jpy: float, max_tts_attempts: int) -> dict:
    target = load_target_and_context()
    report = {
        "management_id": MANAGEMENT_ID,
        "budget_jpy": budget_jpy,
        "max_total_tts_attempts": max_tts_attempts,
        "tts_execution_mode": "STANDARD(固定、BATCH禁止)",
        "planned_target_segment": target["segment_id"],
        "planned_sequence": [
            "候補生成(Luna 1 call、json_schema strict、新規5件)",
            "前回'main idea'版(read-only流用)を候補6件目として追加",
            "局所QA(Luna 1 call、6候補まとめて5 LLM Gate判定)",
            "harness側でcriterion6(局所性)・criterion7(非全文)を機械判定",
            "TTS安定性ヒューリスティックを機械的に注記",
            "全7 Gate PASSの候補から最終候補を1件選定",
            f"採用候補のみTTS(cool-downなし、attempt上限{LOCAL_TTS_ATTEMPT_CAP})+ASR",
        ],
        "planned_luna_calls": 2,
        "planned_max_tts_calls_for_selected_candidate": LOCAL_TTS_ATTEMPT_CAP,
        "human_intervention": "一切行わない(常にFalse)",
        "production_modules_touched": "0件(read-onlyでimportし、Review Lockデコレータの外側[.__wrapped__]のみ呼ぶ)",
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(f"{OUT_DIR}/dry_run_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print("[TTS-LOCAL-REWRITE-NATURAL-ENGLISH-QA-TRIAL-02][dry-run] " + json.dumps(report, ensure_ascii=False, indent=2))
    return report


# ============================================================
# Part J: main run
# ============================================================
def attempt_summary_markdown(attempts: list) -> str:
    lines = ["# Attempt Summary", "",
             "| attempt | timestamp | gap(s) | route | classification | pass | asr_text |",
             "|---|---|---|---|---|---|---|"]
    for r in attempts:
        gap = r.get("gap_seconds_from_previous_attempt")
        gap_disp = "-" if gap is None else f"{gap:.1f}"
        asr_disp = (r.get("asr_text") or "").replace("|", "/")
        lines.append(f"| {r['attempt']} | {r['timestamp']} | {gap_disp} | {r.get('route')} | "
                      f"{r.get('classification')} | {r.get('pass')} | {asr_disp} |")
    return "\n".join(lines) + "\n"


def qa_results_markdown(records: list, selection: dict) -> str:
    lines = ["# QA Results (7 Gates per candidate)", "",
             f"Management-ID: {MANAGEMENT_ID}", "",
             "| id | type | rewritten_segment | 1.meaning | 2.role | 3.fact | 4.context | "
             "5.natural_english | 6.localized | 7.not_full_rewrite | ALL PASS |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in records:
        g = r["seven_gates"]
        lines.append(
            f"| {r['id']} | {r['rewrite_type']} | {r['rewritten_segment']} | "
            f"{g['1_meaning_preserved']} | {g['2_role_preserved']} | {g['3_fact_non_contradiction']} | "
            f"{g['4_context_connection']} | {g['5_natural_english_gate']} | {g['6_localized_minimal_change']} | "
            f"{g['7_not_full_rewrite']} | {r['all_seven_gates_pass']} |"
        )
    lines.append("")
    lines.append("## Natural English Gate 理由(候補ごと)")
    lines.append("")
    for r in records:
        reason = r["qa_llm"]["natural_english"]["reason"] if r["qa_llm"] else "(QA未取得)"
        lines.append(f"- **{r['id']}** (`{r['rewritten_segment']}`): {reason}")
    lines.append("")
    lines.append("## 選定結果")
    lines.append("")
    lines.append(f"- status: {selection['status']}")
    lines.append(f"- rationale: {selection['selection_rationale']}")
    return "\n".join(lines) + "\n"


def run_trial(budget_jpy: float, max_tts_attempts: int) -> dict:
    os.makedirs(OUT_DIR, exist_ok=True)
    os.environ["TTS_EXECUTION_MODE"] = "STANDARD"
    cl.install(COST_LOG_PATH)

    target = load_target_and_context()
    client = b1s.get_client()

    prior_jpy = 0.0

    # --- Part B: 候補生成 ---
    gen_result = call_luna_candidate_gen(client, target)
    with open(f"{OUT_DIR}/candidate_gen_raw.json", "w", encoding="utf-8") as f:
        json.dump(gen_result, f, ensure_ascii=False, indent=2, default=str)
    prior_jpy, budget_status_1, _ = soft_budget_check(budget_jpy, "after candidate generation LLM call", prior_jpy)

    new_candidates = gen_result["candidates"]
    historical_candidate = load_prior_main_idea_candidate()
    all_candidates = new_candidates + [historical_candidate]

    problem_span_range = find_problem_span_token_range(target["canonical_text"], target["problem_span_text"])

    # --- Part E: 局所QA(6候補まとめて1 call) ---
    qa_result = call_luna_local_qa(client, target, all_candidates)
    with open(f"{OUT_DIR}/qa_raw.json", "w", encoding="utf-8") as f:
        json.dump(qa_result, f, ensure_ascii=False, indent=2, default=str)
    prior_jpy, budget_status_2, _ = soft_budget_check(budget_jpy, "after local QA LLM call", prior_jpy)

    records = build_full_candidate_records(target, all_candidates, qa_result["evaluations"], problem_span_range)
    with open(f"{OUT_DIR}/candidates.json", "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2, default=str)

    # --- Part F: 選定 ---
    selection = select_final_candidate(records)
    with open(f"{OUT_DIR}/selected.json", "w", encoding="utf-8") as f:
        json.dump(selection, f, ensure_ascii=False, indent=2, default=str)
    with open(f"{OUT_DIR}/qa_results.md", "w", encoding="utf-8") as f:
        f.write(qa_results_markdown(records, selection))

    summary = {
        "management_id": MANAGEMENT_ID,
        "target": target,
        "candidates": records,
        "selection": selection,
        "tts_sequence_status": None,
        "attempts": [],
        "budget_status_after_candidate_gen": budget_status_1,
        "budget_status_after_qa": budget_status_2,
    }

    # --- Part G: 採用候補のみTTS+ASR ---
    if selection["selected"] is not None:
        target_out_dir = f"{OUT_DIR}/target_family_x_comment_4"
        tts_seq = run_selected_tts(selection["selected"], target_out_dir, max_attempts=min(LOCAL_TTS_ATTEMPT_CAP, max_tts_attempts))
        summary["tts_sequence_status"] = tts_seq["status"]
        summary["attempts"] = tts_seq["attempts"]
        prior_jpy, budget_status_3, _ = soft_budget_check(budget_jpy, "after selected-candidate TTS+ASR", prior_jpy)
        summary["budget_status_after_tts"] = budget_status_3
        with open(f"{OUT_DIR}/attempt_summary.md", "w", encoding="utf-8") as f:
            f.write(attempt_summary_markdown(tts_seq["attempts"]))
    else:
        summary["tts_sequence_status"] = "SKIPPED_NO_CANDIDATE_SELECTED"
        with open(f"{OUT_DIR}/attempt_summary.md", "w", encoding="utf-8") as f:
            f.write("# Attempt Summary\n\n(No candidate passed all 7 gates; no TTS attempt was made.)\n")

    final_jpy, by_provider = e2l_runner.compute_cost_jpy_so_far(COST_LOG_PATH)
    cost_summary = {"total_jpy": round(final_jpy, 4), "by_provider": by_provider, "budget_jpy": budget_jpy}
    with open(f"{OUT_DIR}/cost.json", "w", encoding="utf-8") as f:
        json.dump(cost_summary, f, ensure_ascii=False, indent=2)
    summary["cost"] = cost_summary

    with open(f"{OUT_DIR}/run_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)

    print(f"[TTS-LOCAL-REWRITE-NATURAL-ENGLISH-QA-TRIAL-02] 完了。"
          f"selection_status={selection['status']} tts_status={summary['tts_sequence_status']} "
          f"cost={cost_summary}")
    return summary


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", default="dry-run", choices=("dry-run", "run"))
    parser.add_argument("--budget-jpy", type=float, default=DEFAULT_BUDGET_JPY)
    parser.add_argument("--max-tts-attempts", type=int, default=DEFAULT_MAX_TTS_ATTEMPTS)
    return parser


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()
    if args.stage == "dry-run":
        run_dry_run(args.budget_jpy, args.max_tts_attempts)
        return
    run_trial(args.budget_jpy, args.max_tts_attempts)


if __name__ == "__main__":
    main()
