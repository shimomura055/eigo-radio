# ============================================================
# er002_editorial_runner.py
# ER-002-v1.1A: 編集工程オーケストレーション
# ============================================================
# アングル生成→アングル評価→Editorial Brief構築→Brief検品→台本生成
# (編集品質検品ゲート込み)、という一連の流れを1つの記事について実行する。
#
# 実API・実TTS・実QA・新規トピック取得は行わない(ER-002-v1.1A-I1の
# 非対象範囲)。すべての呼び出し関数(*_fn)は引数として注入され、
# このファイル自体は具体的なAPIクライアントを一切importしない。
#
# API通信障害時のリトライ(call_with_retry)と、コンテンツ試行
# (アングル生成・台本生成)・評価試行(アングル評価・編集品質検品)の
# 回数は、それぞれ別のフィールドに記録する。

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Optional

import er002_common as common
import er002_editorial_common as ec

MAX_ANGLE_CONTENT_ATTEMPTS = 2
MAX_ANGLE_GENERATION_API_RETRY = common.MAX_TTS_API_RETRY
MAX_ANGLE_EVALUATION_API_RETRY = common.MAX_QA_API_RETRY
MAX_SCRIPT_CONTENT_ATTEMPTS = common.MAX_SCRIPT_ATTEMPTS  # 既存条件(2)を維持


# ============================================================
# ステージ1: アングル生成→評価(最大2コンテンツ試行)
# ============================================================
@dataclass
class AngleStageAttemptRecord:
    attempt_number: int
    outcome: str  # "selected" / "all_disqualified" / "diversity_failed" / "inconclusive"
    reasons: list = field(default_factory=list)
    generation_api_retry_count: int = 0
    evaluation_api_retry_count: int = 0
    selection_result: Any = None


@dataclass
class AngleStageOutcome:
    status: str  # "selected" / "failed"
    selected_candidate: Optional[dict] = None
    attempts: list = field(default_factory=list)


def run_angle_stage(
    angle_generation_fn: Callable[[dict], list],
    angle_eval_call_fn: Callable[[str], str],
    angle_eval_prompt_builder: Callable[[list], str],
    valid_fact_ids: set,
    max_content_attempts: int = MAX_ANGLE_CONTENT_ATTEMPTS,
    max_gen_api_retry: int = MAX_ANGLE_GENERATION_API_RETRY,
    max_eval_api_retry: int = MAX_ANGLE_EVALUATION_API_RETRY,
    sleep_fn: Optional[Callable[[float], None]] = None,
) -> AngleStageOutcome:
    """アングル生成(OpenAI)とアングル評価(Gemini QA)は必ず別呼び出しで行う
    (angle_generation_fnとangle_eval_call_fnは別のコーラブル)。"""
    attempts: list[AngleStageAttemptRecord] = []

    for attempt in range(1, max_content_attempts + 1):
        candidates, gen_retries, gen_ok, gen_err = ec.call_with_retry(
            lambda: angle_generation_fn({}), max_gen_api_retry, sleep_fn)
        if not gen_ok:
            attempts.append(AngleStageAttemptRecord(
                attempt_number=attempt, outcome="inconclusive",
                reasons=[f"generation_api_failed: {gen_err}"], generation_api_retry_count=gen_retries,
            ))
            continue

        eval_prompt = angle_eval_prompt_builder(candidates)
        eval_outcome = common.call_qa_with_retry(
            lambda p, _wav: angle_eval_call_fn(p), eval_prompt, b"",
            max_retry=max_eval_api_retry, sleep_fn=sleep_fn,
        )
        if eval_outcome.parse_failed or eval_outcome.raw_result is None:
            attempts.append(AngleStageAttemptRecord(
                attempt_number=attempt, outcome="inconclusive",
                reasons=["evaluation_unavailable_or_unparseable"],
                generation_api_retry_count=gen_retries,
                evaluation_api_retry_count=eval_outcome.api_retry_count,
            ))
            continue

        try:
            result = ec.classify_angle_evaluation(eval_outcome.raw_result, candidates, valid_fact_ids)
        except ec.AngleEvaluationInconclusive as e:
            attempts.append(AngleStageAttemptRecord(
                attempt_number=attempt, outcome="inconclusive", reasons=[str(e)],
                generation_api_retry_count=gen_retries,
                evaluation_api_retry_count=eval_outcome.api_retry_count,
            ))
            continue

        attempts.append(AngleStageAttemptRecord(
            attempt_number=attempt, outcome=result.status,
            reasons=[result.reason] if result.reason else [],
            generation_api_retry_count=gen_retries,
            evaluation_api_retry_count=eval_outcome.api_retry_count,
            selection_result=result,
        ))
        if result.status == "selected":
            selected = next(c for c in candidates if c["angle_id"] == result.selected_angle_id)
            return AngleStageOutcome(status="selected", selected_candidate=selected, attempts=attempts)

    return AngleStageOutcome(status="failed", attempts=attempts)


# ============================================================
# ステージ2: 台本生成(編集品質検品ゲート込み、最大2コンテンツ試行)
# ============================================================
@dataclass
class ScriptStageAttemptRecord:
    attempt_number: int
    structural_valid: bool
    structural_errors: list = field(default_factory=list)
    word_count: Optional[int] = None
    word_count_status: Optional[str] = None
    script_generation_api_retry_count: int = 0
    editorial_quality_outcome: Optional[str] = None  # "passed"/"conclusive_fail"/"inconclusive"/None
    editorial_quality_reasons: list = field(default_factory=list)
    editorial_quality_api_retry_count: int = 0


@dataclass
class ScriptStageOutcome:
    status: str  # "OK" / "FAILED"
    script: Optional[dict] = None
    plan: Optional[Any] = None
    attempts: list = field(default_factory=list)


def run_script_stage_with_quality_gate(
    script_write_fn: Callable[[dict], dict],
    brief: dict,
    quality_prompt_builder: Callable[[dict, dict], str],
    quality_call_fn: Callable[[str], str],
    max_script_attempts: int = MAX_SCRIPT_CONTENT_ATTEMPTS,
    max_gen_api_retry: int = common.MAX_TTS_API_RETRY,
    sleep_fn: Optional[Callable[[float], None]] = None,
) -> ScriptStageOutcome:
    """確定的な編集品質不合格(conclusive_fail)の場合は再評価せず次の台本
    生成試行へ進む。編集品質評価が解析不能なままmax_eval_attempts回続いた
    場合(inconclusive)も、同様に次の台本生成試行へ進む(台本自体を
    作り直す。同じ不完全な評価を繰り返さない)。"""
    attempts: list[ScriptStageAttemptRecord] = []

    for attempt in range(1, max_script_attempts + 1):
        script, gen_retries, gen_ok, gen_err = ec.call_with_retry(
            lambda: script_write_fn({}), max_gen_api_retry, sleep_fn)
        if not gen_ok:
            attempts.append(ScriptStageAttemptRecord(
                attempt_number=attempt, structural_valid=False,
                structural_errors=[f"script_generation_api_failed: {gen_err}"],
                script_generation_api_retry_count=gen_retries,
            ))
            continue

        structure = common.validate_script_structure(script)
        if not structure.valid:
            attempts.append(ScriptStageAttemptRecord(
                attempt_number=attempt, structural_valid=False, structural_errors=structure.errors,
                script_generation_api_retry_count=gen_retries,
            ))
            continue

        plan = common.build_narration_plan(script)
        wc = common.word_count(plan.full_text)
        wc_eval = common.evaluate_word_count(wc)
        if wc_eval["status"] != "within_acceptable_range":
            attempts.append(ScriptStageAttemptRecord(
                attempt_number=attempt, structural_valid=True, word_count=wc,
                word_count_status=wc_eval["status"], script_generation_api_retry_count=gen_retries,
            ))
            continue

        quality_prompt = quality_prompt_builder(script, brief)
        quality_outcome = ec.evaluate_editorial_quality(quality_prompt, quality_call_fn, sleep_fn=sleep_fn)

        record = ScriptStageAttemptRecord(
            attempt_number=attempt, structural_valid=True, word_count=wc,
            word_count_status=wc_eval["status"], script_generation_api_retry_count=gen_retries,
            editorial_quality_outcome=quality_outcome.final_outcome,
            editorial_quality_reasons=quality_outcome.reasons,
            editorial_quality_api_retry_count=quality_outcome.total_api_retry_count,
        )
        attempts.append(record)

        if quality_outcome.final_outcome == "passed":
            return ScriptStageOutcome(status="OK", script=script, plan=plan, attempts=attempts)
        # "conclusive_fail" / "inconclusive"(評価自身の再試行を使い切った後)は
        # いずれも次の台本生成試行(新しい台本)へ進む。

    return ScriptStageOutcome(status="FAILED", attempts=attempts)


# ============================================================
# ステージ3: Editorial Brief検品(独立呼び出し)
# ============================================================
@dataclass
class BriefInspectionStageOutcome:
    status: str  # "OK" / "FAILED"
    result: Optional[dict] = None
    api_retry_count: int = 0


def run_brief_inspection_stage(
    brief: dict,
    brief_inspection_call_fn: Callable[[str], str],
    brief_inspection_prompt_builder: Callable[[dict, set], str],
    valid_fact_ids: set,
    max_api_retry: int = common.MAX_QA_API_RETRY,
    sleep_fn: Optional[Callable[[float], None]] = None,
) -> BriefInspectionStageOutcome:
    prompt = brief_inspection_prompt_builder(brief, valid_fact_ids)
    outcome = common.call_qa_with_retry(
        lambda p, _wav: brief_inspection_call_fn(p), prompt, b"", max_retry=max_api_retry, sleep_fn=sleep_fn)
    if outcome.parse_failed or outcome.raw_result is None:
        return BriefInspectionStageOutcome(status="FAILED", api_retry_count=outcome.api_retry_count)
    try:
        result = ec.classify_brief_inspection(outcome.raw_result, brief, valid_fact_ids)
    except ec.BriefInspectionInconclusive:
        return BriefInspectionStageOutcome(status="FAILED", api_retry_count=outcome.api_retry_count)
    return BriefInspectionStageOutcome(
        status=("OK" if result["passed"] else "FAILED"), result=result, api_retry_count=outcome.api_retry_count,
    )


# ============================================================
# 全体オーケストレーション(TTSはこの工程では呼び出さない。呼び出し関数を
# 渡した場合のみ、台本確定後に呼ぶ設計は用意するが、ER-002-v1.1A-I1では
# tts_call_fnを渡さずに使う)
# ============================================================
@dataclass
class EditorialArticlePipelineOutcome:
    status: str  # "OK" / "FAILED_ANGLE_STAGE" / "FAILED_BRIEF_INSPECTION" / "FAILED_SCRIPT_STAGE"
    article_id: str
    brief: Optional[dict] = None
    script: Optional[dict] = None
    angle_stage: Optional[AngleStageOutcome] = None
    brief_inspection: Optional[BriefInspectionStageOutcome] = None
    script_stage: Optional[ScriptStageOutcome] = None
    tts_called: bool = False


def run_editorial_article_pipeline(
    article_id: str,
    angle_generation_fn: Callable[[dict], list],
    angle_eval_call_fn: Callable[[str], str],
    angle_eval_prompt_builder: Callable[[list], str],
    brief_inspection_call_fn: Callable[[str], str],
    brief_inspection_prompt_builder: Callable[[dict, set], str],
    script_write_fn_factory: Callable[[dict], Callable],  # (brief) -> script_write_fn
    quality_prompt_builder: Callable[[dict, dict], str],
    quality_call_fn: Callable[[str], str],
    valid_fact_ids: set,
    tts_call_fn: Optional[Callable[[dict], Any]] = None,
    sleep_fn: Optional[Callable[[float], None]] = None,
) -> EditorialArticlePipelineOutcome:
    angle_stage = run_angle_stage(
        angle_generation_fn, angle_eval_call_fn, angle_eval_prompt_builder, valid_fact_ids, sleep_fn=sleep_fn)
    if angle_stage.status != "selected":
        return EditorialArticlePipelineOutcome(
            status="FAILED_ANGLE_STAGE", article_id=article_id, angle_stage=angle_stage)

    brief = ec.build_editorial_brief(angle_stage.selected_candidate)

    brief_inspection = run_brief_inspection_stage(
        brief, brief_inspection_call_fn, brief_inspection_prompt_builder, valid_fact_ids, sleep_fn=sleep_fn)
    if brief_inspection.status != "OK":
        return EditorialArticlePipelineOutcome(
            status="FAILED_BRIEF_INSPECTION", article_id=article_id,
            angle_stage=angle_stage, brief=brief, brief_inspection=brief_inspection)

    script_write_fn = script_write_fn_factory(brief)
    script_stage = run_script_stage_with_quality_gate(
        script_write_fn, brief, quality_prompt_builder, quality_call_fn, sleep_fn=sleep_fn)
    if script_stage.status != "OK":
        return EditorialArticlePipelineOutcome(
            status="FAILED_SCRIPT_STAGE", article_id=article_id, angle_stage=angle_stage,
            brief=brief, brief_inspection=brief_inspection, script_stage=script_stage)

    tts_called = False
    if tts_call_fn is not None:
        tts_call_fn(script_stage.script)
        tts_called = True

    return EditorialArticlePipelineOutcome(
        status="OK", article_id=article_id, brief=brief, script=script_stage.script,
        angle_stage=angle_stage, brief_inspection=brief_inspection, script_stage=script_stage,
        tts_called=tts_called,
    )
