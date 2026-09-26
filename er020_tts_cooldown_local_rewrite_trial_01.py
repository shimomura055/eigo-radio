# ============================================================
# er020_tts_cooldown_local_rewrite_trial_01.py
# 管理ID: TTS-COOLDOWN-LOCAL-REWRITE-TRIAL-01(Trialのみ、最大VALIDATED)
# ============================================================
# DEV/Trial path。Production正式経路(er003_v1_sing01_voice01_generate.py・
# er011_human_review_lock_01.py・er007_*・er019_*)は一切変更しない
# (read-onlyでimportし、既存の単発TTS生成関数[voice01.generate_charon_
# english]・既存ASR照合[er006_preprod_hardening_01_validation.
# classify_asr_match]を呼び出すだけ)。retry制御・10分cool-down・attempt
# 記録・Local Rewrite・局所QAはすべて本ファイル(harness側)に実装する。
#
# 目的: ユーザー正式決定のTrial仕様(ACTIVE_TASK_TC.md逐語)を実行する。
#   attempt1 -> NGなら即時attempt2 -> NGなら10分待機(固定、実際にsleep
#   する)-> attempt3 -> NGならLocal Rewrite(全文ではなく発音不能spanの
#   み)-> 局所QA PASS後のみ再TTS -> それでも不可ならHUMAN_REVIEW到達と
#   記録して停止。
#
# 安全性:
#   - Production module(er003_v1_sing01_voice01_generate.py等)は無変更。
#     Review Lockデコレータの外側(`.__wrapped__`)を呼ぶことで、harness
#     自身のattempt間retry制御と、Production側の「3回で機械的にHUMAN_
#     REVIEW_REQUIRED化する」独自のcost guardが二重に競合しないようにする
#     (この技法は既存er011_tts_cooldown_observation_harness_helpers_01.py
#     が同じ目的で既に使っている設計を踏襲したもの)。Production側の
#     review_lock_state.json(er019_output配下等)は一切読み書きしない。
#   - 出力は全てer020_output/tts_cooldown_local_rewrite_trial_01/配下の
#     新規path。Family X/Family A側の既存成果物には一切書き込まない。
#   - 人的介入(承認/テキスト手修正)は一切行わない(human_intervention
#     フィールドは常にFalse)。
#   - TTS_EXECUTION_MODE=STANDARD固定・BATCH禁止。budget-jpy 20円上限・
#     総TTS attempt上限12(dry-runで事前表示、PM_GOVERNANCE 7-5)。
#
# 実行方法:
#   .venv/Scripts/python.exe er020_tts_cooldown_local_rewrite_trial_01.py \
#       --stage dry-run|run --budget-jpy 20 --max-tts-attempts 12

from __future__ import annotations

import argparse
import difflib
import glob
import hashlib
import json
import os
import re
import time
from datetime import datetime, timezone

import er002_common as common
import er003_v1_b1_scaffold_01_generate as b1s
import er003_v1_n3_01_tts_generate as tts_gen
import er003_v1_sing01_voice01_generate as voice01
import er005_cost_logger as cl
import er006_preprod_hardening_01_validation as asr_validation
import er011_connected_speech_equivalence_layer_production_01 as cs_eq_layer
import er012_e_family_entertainment_two_level_runner_01 as e2l_runner

MANAGEMENT_ID = "TTS-COOLDOWN-LOCAL-REWRITE-TRIAL-01"
OUT_DIR = "er020_output/tts_cooldown_local_rewrite_trial_01"
ATTEMPT_LOG_PATH = f"{OUT_DIR}/attempt_log.jsonl"
COST_LOG_PATH = f"{OUT_DIR}/raw_usage_log.jsonl"

# ユーザー正式決定: 固定10分(短縮禁止、実際にtime.sleepする)。
COOLDOWN_SECONDS = 600.0

DEFAULT_BUDGET_JPY = 20.0
DEFAULT_MAX_TTS_ATTEMPTS = 12

# ============================================================
# Part A: Production raw関数(Review Lockデコレータの外側)
# ============================================================
# er011_tts_cooldown_observation_harness_helpers_01.py L45-46と同じ設計
# 意図(3回目STOPPED後もharness自身が4回目以降を制御できるようにする)。
RAW_CHARON_ENGLISH = voice01.generate_charon_english.__wrapped__


def sha256_text(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def _now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


# ============================================================
# Part B: 対象1件(Family X comment_4 canonical)
# ============================================================
FAMILY_X_B1B_DIR = "er019_output/family_x_pointless_trial_01/meta/b1b"


def load_target_family_x_comment_4() -> dict:
    with open(f"{FAMILY_X_B1B_DIR}/audit/tts_generation_results.json", encoding="utf-8") as f:
        results = json.load(f)
    entry = results["segments"]["comment_4"]
    canonical_text = entry["canonical_text"]
    return {
        "segment_id": "comment_4",
        "segment_role": "Comment(Story Recovery + Bridge to In One Line)",
        "canonical_text": canonical_text,
        "source": f"{FAMILY_X_B1B_DIR}/audit/tts_generation_results.json#segments.comment_4.canonical_text",
        "prior_real_run_note": (
            "2026-09-26の実Family X本番run(comment_4)で、attempt1-3すべてが"
            "ASR_VALIDATION_UNCERTAIN(canonical 'the main point together' を"
            "ASRが一貫して'the main points together'と聞き取る)でHUMAN_REVIEW_"
            "REQUIREDへ到達済み(review_lock_state.json参照)。本Trialはこれとは"
            "独立した、harness自身の新規TTS/ASR呼び出しで再現を試みる。"
        ),
    }


# ============================================================
# Part C: 過去のHUMAN_REVIEW_LOCKED/3回NG例の探索(attempt1がPASSして
# 再現しない場合のみ使用、追加のTTS/ASR呼び出しは行わない=read-only)。
# ============================================================
def find_historical_ng_examples(max_n: int = 2) -> list:
    found = []
    for pattern in ("er011_output/**/review_lock_state.json", "er011_output/**/tts_generation_results.json"):
        for path in glob.glob(pattern, recursive=True):
            try:
                with open(path, encoding="utf-8") as f:
                    data = json.load(f)
            except (OSError, json.JSONDecodeError):
                continue
            entries = data.get("segments", data) if isinstance(data, dict) else {}
            if not isinstance(entries, dict):
                continue
            for seg_id, entry in entries.items():
                if not isinstance(entry, dict):
                    continue
                state = entry.get("state") or entry.get("human_review_lock_status")
                final_status = entry.get("final_status") or entry.get("status")
                cumulative = entry.get("cumulative_tts_attempts")
                if state == "HUMAN_REVIEW_REQUIRED" or final_status in ("ASR_VALIDATION_UNCERTAIN", "STOPPED"):
                    canonical_text = entry.get("canonical_text")
                    last_log = entry.get("last_attempts_log") or entry.get("attempts_log") or []
                    last_asr = last_log[-1].get("asr_text") if last_log else None
                    found.append({
                        "source_path": path, "segment_id": seg_id, "canonical_text": canonical_text,
                        "asr_text": last_asr, "reason": entry.get("reason"), "final_status": final_status,
                        "cumulative_tts_attempts": cumulative,
                    })
                    if len(found) >= max_n:
                        return found
    return found


# ============================================================
# Part D: 単発TTS+ASR attempt(既存生成関数を呼び出すだけ)
# ============================================================
def run_single_tts_attempt(canonical_text: str, out_path: str, attempt_number: int,
                            style_prefix_override: str, disfluency_qa: bool,
                            input_text_override: str | None = None) -> dict:
    """RAW_CHARON_ENGLISH(=voice01.generate_charon_english.__wrapped__)を
    max_attempts=1で1回だけ呼ぶ(既存TTS+ASR経路をそのまま利用)。harness
    側では追加のretry制御・cool-down・recordのみを行い、TTS/ASR呼び出し
    ロジック自体は一切再実装しない。"""
    processed_text = input_text_override or tts_gen.tts_safe_number_words_en(tts_gen.tts_safe_en(canonical_text))
    tts_input_sha256 = sha256_text(processed_text)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    result = RAW_CHARON_ENGLISH(
        processed_text, out_path, max_attempts=1,
        style_prefix_override=style_prefix_override, disfluency_qa=disfluency_qa,
    )
    # ER-020注記(実行時に発見): generate_charon_english()は、verified=False
    # かつstop_retrying=Falseのままmax_attempts回を使い切った場合
    # (max_attempts=1では「同一signatureの連続」を判定できないため、この
    # 経路にほぼ常に落ちる)、トップレベルの戻り値に"status":"STOPPED"
    # ・"reason"のみを返し、"asr_text"/"instruction_type"/
    # "audio_classification"/"verified"を含めない(OK/ASR_VALIDATION_
    # UNCERTAIN分岐にのみ存在するキー)。実際の値は必ず
    # attempts_log[-1](このattemptのループ内で毎回appendされる、全分岐
    # 共通)に残っているため、そちらを一次情報源として使う
    # (harness側のバグ修正、Production関数自体は無変更)。
    attempts_log = result.get("attempts_log") or []
    last_attempt_entry = attempts_log[-1] if attempts_log else {}
    asr_text = result.get("asr_text", last_attempt_entry.get("asr_text"))
    instruction_type = result.get("instruction_type", last_attempt_entry.get("instruction_type"))
    cascade_audio_classification = result.get("audio_classification", last_attempt_entry.get("audio_classification"))
    # 注意: トップレベルのキー名は"asr_verified"(OK/ASR_VALIDATION_UNCERTAIN
    # 分岐のみ)、attempts_log内の粒度は"verified"(全attempt共通)。
    # キー名が異なる点を取り違えないこと(実行時に発見・修正)。
    verified = bool(result.get("asr_verified", last_attempt_entry.get("verified")))
    disfluency_checked = result.get("disfluency_checked", last_attempt_entry.get("disfluency_checked"))

    # 既存ASR照合(classify_asr_match、OPEN-121/122等価層の基盤となる
    # _classify_asr_match_core経由)を明示的に直接呼び、harness独自の
    # classificationとして記録する(呼び出すだけ、判定ロジックは無変更)。
    if asr_text is not None:
        cls = asr_validation.classify_asr_match(canonical_text, asr_text)
        classification = cls.classification
        classification_reason = cls.reason
        should_pass = cls.should_pass
    else:
        classification = result.get("status")
        classification_reason = result.get("reason")
        should_pass = False

    passed = verified and should_pass

    record = {
        "segment": "comment_4",
        "canonical_text": canonical_text,
        "attempt": attempt_number,
        "timestamp": _now_iso(),
        "model": common.MODEL_NAME,
        "voice": voice01.CHARON,
        "route": instruction_type,
        "tts_execution_mode": os.environ.get("TTS_EXECUTION_MODE"),
        "tts_input_sha256": tts_input_sha256,
        "asr_text": asr_text,
        "classification": classification,
        "classification_reason": classification_reason,
        "cascade_audio_classification": cascade_audio_classification,
        "pass": passed,
        "human_intervention": False,
        "raw_status": result.get("status"),
        "raw_reason": result.get("reason"),
        "attempt_wav_path": out_path,
        "disfluency_checked": disfluency_checked,
    }
    return record


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


# ============================================================
# Part E: attempt1 -> 即時attempt2 -> 10分待機(固定) -> attempt3
# ============================================================
def run_cooldown_retry_sequence(target: dict, out_dir: str, sleep_fn=time.sleep,
                                 cooldown_seconds: float = COOLDOWN_SECONDS,
                                 style_prefix_override: str = tts_gen.B1_PREVIEW_STYLE_PREFIX_CALM,
                                 disfluency_qa: bool = True) -> dict:
    canonical_text = target["canonical_text"]
    segment_id = target["segment_id"]
    records = []

    def _attempt(n: int) -> dict:
        wav_path = f"{out_dir}/attempt{n}/narration/{segment_id}.wav"
        rec = run_single_tts_attempt(canonical_text, wav_path, n, style_prefix_override, disfluency_qa)
        records.append(rec)
        append_attempt_records([rec])
        return rec

    r1 = _attempt(1)
    if r1["pass"]:
        return {"status": "PASS_AT_ATTEMPT_1", "attempts": _with_gap(records)}

    r2 = _attempt(2)
    if r2["pass"]:
        return {"status": "PASS_AT_ATTEMPT_2", "attempts": _with_gap(records)}

    cooldown_started_at = time.time()
    sleep_fn(cooldown_seconds)
    cooldown_ended_at = time.time()
    actual_cooldown_seconds = cooldown_ended_at - cooldown_started_at

    r3 = _attempt(3)
    r3["cooldown_requested_seconds"] = cooldown_seconds
    r3["cooldown_actual_seconds"] = round(actual_cooldown_seconds, 3)
    if r3["pass"]:
        return {"status": "PASS_AT_ATTEMPT_3", "attempts": _with_gap(records),
                "cooldown_actual_seconds": round(actual_cooldown_seconds, 3)}

    return {"status": "REPRODUCED_3_NG", "attempts": _with_gap(records),
            "cooldown_actual_seconds": round(actual_cooldown_seconds, 3)}


# ============================================================
# Part F: NG span特定(canonical vs ASRの語差分、最小限の周辺のみ)
# ============================================================
_WORD_RE = re.compile(r"[A-Za-z']+")


def identify_ng_span(canonical_text: str, asr_text: str, context_words: int = 3) -> dict:
    # 実行時に発見したバグ修正: 独自の正規表現([A-Za-z']+)はcanonical_text側の
    # 曲線アポストロフィ(’、U+2019)を単語構成文字に含めないため、
    # "let’s"(canonical)と"let's"(ASR、直線アポストロフィ)の間に見かけ上の
    # 語数差が生じ、本当のNG原因(point/points)より先に、この無関係な
    # アポストロフィ字形差が最初の非一致箇所として検出されてしまっていた。
    # 既存の本番tokenizer(asr_validation.tokenize、classify_asr_matchが
    # 内部で使う正規化と同一)をそのまま呼び出すことで、両者を同じ正規化
    # (曲線/直線アポストロフィの統一含む)にかけてから語単位でdiffする
    # (呼び出すだけ、判定ロジック自体は無変更)。
    canon_tokens = asr_validation.tokenize(canonical_text)
    asr_tokens = asr_validation.tokenize(asr_text or "")
    sm = difflib.SequenceMatcher(None, canon_tokens, asr_tokens)
    diff_ops = [op for op in sm.get_opcodes() if op[0] != "equal"]
    if not diff_ops:
        return {"found": False}
    # 最初の非一致opcodeを採用(comment_4は差分1箇所のみの実例)。
    tag, i1, i2, j1, j2 = diff_ops[0]
    ctx_start = max(0, i1 - context_words)
    ctx_end = min(len(canon_tokens), i2 + context_words)
    before_span_words = canon_tokens[ctx_start:ctx_end]
    changed_canon_words = canon_tokens[i1:i2]
    changed_asr_words = asr_tokens[j1:j2]
    # ASR側にも同じcontext windowを対応するj座標で切り出す(Connected Speech
    # Equivalence Layerの適用可否確認をspan単位[全文ではなく]で行うため。
    # 全文同士で確認すると、この差分より前に別の無関係な差(例: このTrialで
    # 実際に踏んだ曲線/直線アポストロフィの字形差)があった場合、その関数が
    # 内部で使う独自diffロジックが誤って別の箇所を指すおそれがある)。
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


# ============================================================
# Part G: Local Rewrite(Luna、全文ではなく最小限のspanのみ)
# ============================================================
LOCAL_REWRITE_SYSTEM_PROMPT = (
    "You are a careful audio-script editor for an English learning podcast. "
    "You are given a short spoken English segment and a specific word or short "
    "phrase inside it that a speech recognizer keeps mis-transcribing. Rewrite "
    "ONLY that minimal span (and, if unavoidable, a few immediately adjacent "
    "words needed for grammatical fit) so that the ambiguous word is replaced "
    "with a different, unambiguous wording that keeps exactly the same meaning. "
    "Do NOT rewrite the whole segment. Do NOT change its role, tone, or how it "
    "connects to the sentence before/after it. Do NOT add any new fact. "
    "Return STRICT JSON only, no markdown fences, no commentary, with exactly "
    "these keys: rewritten_segment (the full segment text with only the "
    "minimal span changed), changed_span_before (the exact original span you "
    "changed), changed_span_after (the exact replacement span), "
    "unchanged_ratio (your own estimate, 0.0-1.0, of the fraction of the "
    "original segment's words left completely unchanged)."
)


def _extract_json_object(raw_text: str) -> dict:
    text = raw_text.strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.MULTILINE)
    return json.loads(text)


def call_luna_local_rewrite(client, canonical_text: str, ng_span: dict) -> dict:
    prompt = (
        f"Full segment (role: Comment, bridges to the closing 'In One Line'):\n"
        f"\"{canonical_text}\"\n\n"
        f"Problem span (a speech recognizer repeatedly mis-transcribes this as "
        f"{ng_span['asr_changed_words']!r} instead of {ng_span['canonical_changed_words']!r}):\n"
        f"\"{ng_span['canonical_span_with_context']}\"\n\n"
        "Rewrite only the minimal problematic word(s) with an unambiguous "
        "alternative that keeps the same meaning and role. Return the JSON "
        "object described in the system instructions."
    )
    response = client.responses.create(
        model=b1s.MODEL,
        reasoning={"effort": b1s.REASONING_EFFORT},
        input=[
            {"role": "developer", "content": LOCAL_REWRITE_SYSTEM_PROMPT},
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


def compute_unchanged_ratio(original_text: str, rewritten_text: str) -> float:
    """LLM自己申告のunchanged_ratioを鵜呑みにせず、harness側で語単位の
    差分から独立に計算する(全文置換でないことを検証するための閾値判定に
    使う、authoritative値)。"""
    orig_words = _WORD_RE.findall(original_text.lower())
    new_words = _WORD_RE.findall(rewritten_text.lower())
    sm = difflib.SequenceMatcher(None, orig_words, new_words)
    unchanged = sum(block.size for block in sm.get_matching_blocks())
    return round(unchanged / max(1, len(orig_words)), 4)


# unchanged_ratioがこの閾値未満の場合、「全文書き換え」とみなしFAILする
# (spanのみの言い換えなら、28語中数語の変更で十分閾値を超える想定)。
LOCAL_REWRITE_MIN_UNCHANGED_RATIO = 0.7


# ============================================================
# Part H: 局所QA(Luna、意味保持・role保持・非矛盾・自然な接続)
# ============================================================
LOCAL_QA_SYSTEM_PROMPT = (
    "You are a strict QA reviewer for an English learning podcast script. You "
    "check whether a locally-rewritten segment still satisfies ALL of the "
    "following, compared to the original segment: "
    "(1) meaning is fully preserved (no new facts, no lost facts, no changed "
    "claims); "
    "(2) the segment's role/function in the episode is unchanged (a Comment "
    "that bridges to the closing 'In One Line' must still read as that role); "
    "(3) it does not contradict anything the original segment said; "
    "(4) it still connects naturally to what comes immediately before and "
    "after it. "
    "Return STRICT JSON only, no markdown fences, with exactly these keys: "
    "pass (boolean), reasons (a list of short strings explaining your "
    "judgment for each of the 4 criteria above)."
)


def call_luna_local_qa(client, original_text: str, rewritten_text: str, segment_role: str) -> dict:
    prompt = (
        f"Segment role: {segment_role}\n\n"
        f"Original segment:\n\"{original_text}\"\n\n"
        f"Locally-rewritten segment:\n\"{rewritten_text}\"\n\n"
        "Evaluate the 4 criteria and return the JSON object described in the "
        "system instructions."
    )
    response = client.responses.create(
        model=b1s.MODEL,
        reasoning={"effort": b1s.REASONING_EFFORT},
        input=[
            {"role": "developer", "content": LOCAL_QA_SYSTEM_PROMPT},
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
# Part I: Connected Speech role taxonomy(設計のみ、Production未配線)
# ============================================================
# ユーザー指示のtaxonomy例をそのまま実装する。既存の実配線は「role」では
# なく「呼び出し関数+呼び出し側フラグ」単位で決まっている実態
# (docs/pm/recon_connected_speech_scope_01.md参照、事実確認済み)。
# 本harnessは、そのギャップ自体を役割別taxonomyとして明示するための
# 設計データ構造を持つ(Production配線はしない)。
ROLE_TAXONOMY = {
    "NARRATIVE_ENGLISH": [
        "full_story_part1", "full_story_part2", "full_story_part3",
        "comment_1", "comment_2", "comment_3", "comment_4",
        "preview", "topic_intro", "in_one_line",
    ],
    "HEADING_READOUT": ["point_one_heading", "point_two_heading"],
    "KEY_PHRASE": ["kp_en_component"],
}

# role単位ではなく、実際にwireされている粒度(関数+明示フラグ)。
# docs/pm/recon_connected_speech_scope_01.md 2節の表をそのままデータ化。
CURRENT_WIRING_BY_SEGMENT = {
    "full_story_part1": True, "full_story_part2": True, "full_story_part3": True,
    "point_one": True, "point_two": True,
    "comment_1": False, "comment_2": False, "comment_3": False, "comment_4": False,
    "preview": False, "topic_intro": False, "in_one_line": False,
    "point_one_heading": False, "point_two_heading": False,
    "kp_en_component": False,
}

CURRENT_WIRING_RATIONALE = {
    "comment_4": (
        "voice01.generate_charon_english()自体にenable_connected_speech_"
        "equivalence_layer/enable_repetition_qa引数が存在しない(Full Story "
        "本文が使うnews_tail_fix.generate_news_narration_wide_marginとは別関数)。"
        "role taxonomy上はNARRATIVE_ENGLISHに属していても、現在の実装は"
        "関数単位で決まっているため適用されない。"
    ),
}


def role_of(segment_id: str) -> str | None:
    for role, members in ROLE_TAXONOMY.items():
        if segment_id in members:
            return role
    return None


def would_connected_speech_equivalence_layer_rescue(canonical_text: str, asr_text: str) -> dict:
    """OPEN-122 Equivalence Layer本体を直接呼び、comment_4のpoint/points差が
    (Production配線の有無とは独立に)そもそも救済され得る形状かを確認する
    (docs/pm/recon_connected_speech_scope_01.md 4節と同じ確認を本harness内
    で再実行し、実行時evidenceとして記録する)。"""
    result = cs_eq_layer.classify_connected_speech_equivalence(canonical_text, asr_text)
    would_rescue = result.get("layer_judgment") in ("CONNECTED_SPEECH_ACCEPT", "CONNECTED_SPEECH_RESEGMENTATION")
    return {"would_rescue": would_rescue, "layer_judgment": result.get("layer_judgment"), "raw_result": result}


def build_role_taxonomy_markdown() -> str:
    lines = [
        "# Connected Speech Role Taxonomy(設計、Production未配線)",
        "",
        f"Management-ID: {MANAGEMENT_ID}",
        "",
        "## 1. Role定義(設計)",
        "",
        "| role | segments |",
        "|---|---|",
    ]
    for role, members in ROLE_TAXONOMY.items():
        lines.append(f"| {role} | {', '.join(members)} |")
    lines += [
        "",
        "## 2. 現在の実配線(関数+明示フラグ単位、role単位ではない)",
        "",
        "| segment | role(設計) | 現在wired? | 根拠 |",
        "|---|---|---|---|",
    ]
    for seg, wired in CURRENT_WIRING_BY_SEGMENT.items():
        lines.append(f"| {seg} | {role_of(seg) or '(未分類)'} | {wired} | "
                      f"{CURRENT_WIRING_RATIONALE.get(seg, 'docs/pm/recon_connected_speech_scope_01.md 2節参照')} |")
    lines += [
        "",
        "## 3. 所見",
        "",
        "現在の適用可否はrole(NARRATIVE_ENGLISH等)単位ではなく、呼び出し関数"
        "(`voice01.generate_charon_english` vs "
        "`news_tail_fix.generate_news_narration_wide_margin`)+呼び出し側の"
        "明示フラグという、より細かい粒度で決まっている。同じNARRATIVE_ENGLISH"
        "roleに属するcomment_1-4/preview/topic_intro/in_one_lineと"
        "full_story_part1-3は、現在の実装では異なる扱いを受ける"
        "(docs/pm/recon_connected_speech_scope_01.md 3節「事実1」参照)。",
        "",
        "comment_4の`point`→`points`差は、Production未配線という理由以前に、"
        "OPEN-122 Equivalence Layer本体を直接呼んでも救済されない形状"
        "(`NOT_A_PHONEME_PREFIX_DROP`、ASR側がcanonical語の後ろに`s`を追加した"
        "形であり、この関数が想定する「phoneme drop」形状に一致しない)。"
        "本Trialのharness内で実行時に再確認した結果は本ファイル生成元の"
        "run_summary.json / attempt_summary.mdを参照。",
    ]
    return "\n".join(lines) + "\n"


# ============================================================
# Part J: dry-run(PM_GOVERNANCE 7-5)
# ============================================================
def run_dry_run(budget_jpy: float, max_tts_attempts: int) -> dict:
    target = load_target_family_x_comment_4()
    report = {
        "management_id": MANAGEMENT_ID,
        "budget_jpy": budget_jpy,
        "max_total_tts_attempts": max_tts_attempts,
        "tts_execution_mode": "STANDARD(固定、BATCH禁止)",
        "planned_target_segment": target["segment_id"],
        "planned_sequence": [
            "attempt1(即時)", "attempt2(NGなら即時)",
            f"cool-down {COOLDOWN_SECONDS:.0f}秒(NGなら固定、実sleep)",
            "attempt3(NGならLocal Rewriteへ)",
            "Local Rewrite(Luna、spanのみ)+局所QA(Luna)",
            "再TTS attempt4相当(局所QA PASS時のみ)",
        ],
        "planned_max_tts_calls_for_primary_target": 4,
        "fallback_historical_examples_max": 2,
        "fallback_note": "attempt1がPASSし再現しない場合のみ、TTSを追加せずread-onlyでer011_output/**を検索する。",
        "human_intervention": "一切行わない(常にFalse)",
        "production_modules_touched": "0件(read-onlyでimportし、Review Lockデコレータの外側[.__wrapped__]のみ呼ぶ)",
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(f"{OUT_DIR}/dry_run_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print("[TTS-COOLDOWN-TRIAL][dry-run] " + json.dumps(report, ensure_ascii=False, indent=2))
    return report


# ============================================================
# Part K: main run
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


def handle_reproduced_ng(target: dict, seq_attempts: list, target_out_dir: str, budget_jpy: float,
                          max_tts_attempts: int, tts_calls_used: int, retts_attempt_number: int = 4,
                          retts_out_subdir: str = "attempt4_rewrite") -> dict:
    """3回連続NG(再現)後のLocal Rewrite→局所QA→再TTSの一連の処理。
    run_trial()の通常経路(retts_attempt_number=4)と、実行時に発見した
    バグ(下記)の修正後にNG span特定からやり直す訂正実行の両方から呼べる
    よう分離した(cool-down 10分を再実行せずに済む)。"""
    result = {"local_rewrite": None, "local_qa": None, "retts_attempt": None, "final_status": None,
              "connected_speech_equivalence_check": None, "ng_span": None}

    last_ng = seq_attempts[-1]
    ng_span = identify_ng_span(target["canonical_text"], last_ng["asr_text"])
    result["ng_span"] = ng_span

    # span単位(全文ではなく)でEquivalence Layerの適用可否を確認する
    # (docs/pm/recon_connected_speech_scope_01.md 4節と同じ粒度。全文で
    # 呼ぶと、対象の差分より前に無関係な差があった場合に内部diffが
    # 別の箇所を指すおそれがあるため、identify_ng_span()が特定した
    # spanのみを渡す)。
    if ng_span.get("found"):
        cs_check = would_connected_speech_equivalence_layer_rescue(
            ng_span["canonical_span_with_context"], ng_span["asr_span_with_context"])
    else:
        cs_check = {"would_rescue": False, "layer_judgment": "NO_SPAN_FOUND", "raw_result": None}
    result["connected_speech_equivalence_check"] = cs_check
    with open(f"{OUT_DIR}/local_rewrite/span.json", "w", encoding="utf-8") as f:
        json.dump({"ng_span": ng_span, "connected_speech_equivalence_check": cs_check}, f,
                  ensure_ascii=False, indent=2, default=str)

    client = b1s.get_client()
    rewrite = call_luna_local_rewrite(client, target["canonical_text"], ng_span)
    e2l_runner.assert_budget_ok(OUT_DIR, budget_jpy, "after Local Rewrite LLM call")
    harness_unchanged_ratio = compute_unchanged_ratio(target["canonical_text"], rewrite["rewritten_segment"])
    rewrite["harness_computed_unchanged_ratio"] = harness_unchanged_ratio
    rewrite["is_local_not_full_rewrite"] = harness_unchanged_ratio >= LOCAL_REWRITE_MIN_UNCHANGED_RATIO
    result["local_rewrite"] = rewrite
    with open(f"{OUT_DIR}/local_rewrite/rewrite_prompt.txt", "w", encoding="utf-8") as f:
        f.write(rewrite["_prompt"])
    with open(f"{OUT_DIR}/local_rewrite/rewrite_result.json", "w", encoding="utf-8") as f:
        json.dump(rewrite, f, ensure_ascii=False, indent=2, default=str)

    if not rewrite["is_local_not_full_rewrite"]:
        result["final_status"] = "LOCAL_REWRITE_REJECTED_NOT_LOCAL"
        return result

    qa = call_luna_local_qa(client, target["canonical_text"], rewrite["rewritten_segment"], target["segment_role"])
    e2l_runner.assert_budget_ok(OUT_DIR, budget_jpy, "after Local QA LLM call")
    result["local_qa"] = qa
    with open(f"{OUT_DIR}/local_rewrite/local_qa_result.json", "w", encoding="utf-8") as f:
        json.dump(qa, f, ensure_ascii=False, indent=2, default=str)

    if not qa.get("pass"):
        result["final_status"] = "HUMAN_REVIEW_LOCKED(local QA FAILED)"
        return result
    if tts_calls_used + 1 > max_tts_attempts:
        result["final_status"] = "STOPPED(TTS attempt budget exhausted)"
        return result

    retts_out = f"{target_out_dir}/{retts_out_subdir}/narration/comment_4.wav"
    # バグ修正(実行時に発見): ここでは書き換え後のテキストを実際に発話
    # させているため、ASR照合の相手は書き換え前のtarget["canonical_text"]
    # ではなく、rewrite["rewritten_segment"](実際に話された内容)で
    # なければならない。旧canonical_textのまま比較すると、書き換えで
    # 解消済みの箇所(例: let’s->let us)が見かけ上の新規不一致として
    # 誤検出される(最初の実行で発生・確認済み)。
    retts_record = run_single_tts_attempt(
        rewrite["rewritten_segment"], retts_out, retts_attempt_number, tts_gen.B1_PREVIEW_STYLE_PREFIX_CALM, True,
        input_text_override=tts_gen.tts_safe_number_words_en(tts_gen.tts_safe_en(rewrite["rewritten_segment"])))
    retts_record["pre_rewrite_canonical_text"] = target["canonical_text"]
    append_attempt_records([retts_record])
    e2l_runner.assert_budget_ok(OUT_DIR, budget_jpy,
                                f"after re-TTS (attempt{retts_attempt_number}, rewritten segment)")
    result["retts_attempt"] = retts_record
    result["final_status"] = "RESOLVED_BY_LOCAL_REWRITE" if retts_record["pass"] else "HUMAN_REVIEW_LOCKED"
    return result


def run_trial(budget_jpy: float, max_tts_attempts: int) -> dict:
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(f"{OUT_DIR}/local_rewrite", exist_ok=True)
    os.environ["TTS_EXECUTION_MODE"] = "STANDARD"
    cl.install(COST_LOG_PATH)

    target = load_target_family_x_comment_4()
    target_out_dir = f"{OUT_DIR}/target_family_x_comment_4"

    seq = run_cooldown_retry_sequence(target, target_out_dir)
    e2l_runner.assert_budget_ok(OUT_DIR, budget_jpy, "after cooldown retry sequence (attempt1-3)")
    tts_calls_used = len(seq["attempts"])

    summary = {
        "management_id": MANAGEMENT_ID, "target": target, "cooldown_sequence_status": seq["status"],
        "attempts": seq["attempts"], "local_rewrite": None, "local_qa": None,
        "retts_attempt": None, "final_status": None,
        "connected_speech_equivalence_check": None,
        "historical_examples_used": None,
    }

    if seq["status"] in ("PASS_AT_ATTEMPT_1", "PASS_AT_ATTEMPT_2", "PASS_AT_ATTEMPT_3"):
        summary["final_status"] = "REPRODUCTION_FAILED_ATTEMPT_PASSED"
        if seq["status"] == "PASS_AT_ATTEMPT_1":
            summary["historical_examples_used"] = find_historical_ng_examples(max_n=2)
    else:
        summary.update(handle_reproduced_ng(target, seq["attempts"], target_out_dir, budget_jpy,
                                             max_tts_attempts, tts_calls_used))

    all_attempts = seq["attempts"] + ([summary["retts_attempt"]] if summary.get("retts_attempt") else [])
    with open(f"{OUT_DIR}/attempt_summary.md", "w", encoding="utf-8") as f:
        f.write(attempt_summary_markdown(all_attempts))
    with open(f"{OUT_DIR}/connected_speech_role_taxonomy.md", "w", encoding="utf-8") as f:
        f.write(build_role_taxonomy_markdown())

    final_jpy, by_provider = e2l_runner.compute_cost_jpy_so_far(COST_LOG_PATH)
    cost_summary = {"total_jpy": round(final_jpy, 4), "by_provider": by_provider, "budget_jpy": budget_jpy}
    with open(f"{OUT_DIR}/cost.json", "w", encoding="utf-8") as f:
        json.dump(cost_summary, f, ensure_ascii=False, indent=2)
    summary["cost"] = cost_summary

    with open(f"{OUT_DIR}/run_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)

    print(f"[TTS-COOLDOWN-TRIAL] 完了。final_status={summary['final_status']} cost={cost_summary}")
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
