# ============================================================
# er014_output/four_type_observation_01/trend/run_trend_audio_completion_3.py
# 管理ID: USER-TEST-AUDIO-HUMAN-REVIEW-FIX-02-TREND
# ============================================================
# 目的: Trend A2の最後の残りsegment `point_two`(「Alexa+」表記揺れにより
# Human Review Cost Guardでロック中)について、ユーザー承認(2026-09-15)に
# 基づき、`er011_human_review_lock_01.approve_regenerate()`を**1回だけ**
# 呼び、CONT1(run_trend_audio_completion_2.py)が使ったのと**完全に同一の
# canonical text・同一のProduction関数・同一引数**で1回だけ再生成する。
# 目的は完成だけでなく、同一テキストでのrun-to-run varianceの観測も兼ねる。
#
# 通れば(status=="OK"): A2 Assembly以降(Gate/consistency/player/cost集計)
# まで完了させる。通らなければ、追加retryは一切行わず、lockはHUMAN_REVIEW_
# REQUIREDのまま残しSTOPする(本ファイル内でも上限回数を独自判断で
# 引き上げない)。
#
# 既存Production関数(er003_v1_n3_01_tts_generate.py等)は無変更で直接呼ぶ。
# 本ファイルはCONT1(run_trend_audio_completion_2.py)をモジュールとして
# importし、読み整形関数・Assembly以降の関数をそのまま再利用する。
#
# 実行方法(root直下から):
#   .venv/Scripts/python.exe er014_output/four_type_observation_01/trend/run_trend_audio_completion_3.py --level a2 --approve-point-two-once
from __future__ import annotations

import argparse
import os
import sys
import time
from datetime import datetime, timezone

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)
_TREND_DIR_FOR_IMPORT = os.path.dirname(os.path.abspath(__file__))
if _TREND_DIR_FOR_IMPORT not in sys.path:
    sys.path.insert(0, _TREND_DIR_FOR_IMPORT)

import run_trend_audio_completion as base  # 前回driver(Production関数を無変更で直接呼ぶ既存呼び出しをそのまま再利用)
import run_trend_audio_completion_2 as cont1  # CONT1(読み整形・Assembly以降のヘルパーを再利用)
import er011_human_review_lock_01 as review_lock

sc = base.sc
tts_gen = base.tts_gen
asm = base.asm
cl = base.cl
arp = base.arp
load_json = base.load_json
save_json = base.save_json

OUT_DIR = base.OUT_DIR
THEME_ID = base.THEME_ID
TREND_DIR = base.TREND_DIR

DELEGATION_ID = "USER-TEST-AUDIO-HUMAN-REVIEW-FIX-02-TREND"
APPROVED_BY = (
    f"user (2026-09-15, delegation={DELEGATION_ID}, "
    "ユーザー承認原文: 「Trend A2 残り: point_twoのAlexa+。ユーザー承認: 同一テキストで"
    "追加再生成を1回だけ許可。目的は単純N増しだけでなく、時間差/run-to-run varianceの観測も"
    "兼ねる。同一canonical text/同一Production path/1回のみ/Human Review Lock承認付き/"
    "結果を時間差runとして記録。通れば完成。通らなければ自動retry継続禁止。その時点でOPEN-153へ"
    "再発例として記録。」)"
)

TASK_BUDGET_JPY = 40.0  # 委任文: point_two 1回+Assembly以降


def task_baseline_cost_jpy() -> float:
    return base.cost_so_far_jpy()


def task_check_budget(baseline: float, note: str) -> float:
    so_far = base.cost_so_far_jpy()
    delta = round(so_far - baseline, 4)
    print(f"[FIX02-BUDGET] this_task_delta={delta:.2f} JPY / budget={TASK_BUDGET_JPY} JPY (次段階: {note})")
    if delta >= TASK_BUDGET_JPY:
        raise RuntimeError(
            f"[FIX02] 本タスク費用上限到達のためSTOP: delta={delta:.2f} JPY >= "
            f"budget={TASK_BUDGET_JPY} JPY (次段階「{note}」を実行せず停止)")
    return delta


# ============================================================
# 本タスクで発見: base.cost_breakdown_by_stage()はTrendの共有
# raw_usage_log_audio_completion.jsonlを毎回全件re-readし、stage名に
# level(_a2/_b1b)が含まれているにもかかわらずlevelでの絞り込みを一切
# 行わない。そのためbase.update_shared_outputs(level, ...)を複数levelで
# 呼ぶと、後から呼んだlevelのcost_summary_audio.json["levels"][level]に
# 「その時点までにログされた全level分の合計」がまるごと入ってしまう
# (実際にCONT1がlevel="b1b"のみで1回呼んだ時点で、
# cost_summary_audio.json["levels"]["b1b"]=¥160.16 は実際には
# a2初回パス¥64.40+a2 reading fix¥26.22(合計¥90.62)まで
# 混入した値だった。本タスクでlevel="a2"を素朴に追加呼び出しすると
# 二重計上でさらに悪化するため、ここではbase側ファイルを無変更のまま、
# stage名に"_{level}"というトークンを含む行だけを対象にした正しい
# level別集計を本ファイル内でのみ提供し、a2/b1b両方のcost_summary_audio.
# json/production_set_cost.jsonエントリを正しい値へ補正する
# (CONT1がbuild_consistency_check()のB1Bキー構造バグ・comment_4非冪等
# バグをローカル修正版で対応したのと同じ手法)。
# ============================================================
def cost_breakdown_by_stage_for_level(level: str) -> dict:
    full = base.cost_breakdown_by_stage()
    token = f"_{level}"
    return {stage: v for stage, v in full.items() if token in stage}


def _cat_totals_from_breakdown(breakdown: dict) -> dict:
    category_map = {"scaffold": "preview_comment_llm_jpy", "keyphrase": "key_phrase_llm_jpy",
                     "tts": "tts_jpy", "assemble": "other_jpy"}
    cat_totals = {"preview_comment_llm_jpy": 0.0, "key_phrase_llm_jpy": 0.0, "tts_jpy": 0.0, "other_jpy": 0.0}
    for stage, jpy in breakdown.items():
        prefix = stage.rsplit("_", 1)[0]
        cat = category_map.get(prefix, "other_jpy")
        cat_totals[cat] += jpy
    cat_totals = {k: round(v, 2) for k, v in cat_totals.items()}
    cat_totals["total_jpy"] = round(sum(cat_totals.values()), 2)
    cat_totals["raw_stage_breakdown_jpy"] = breakdown
    return cat_totals


def fix_cost_summary_and_production_set_cost() -> dict:
    """base.update_shared_outputs()呼び出し後に、cost_summary_audio.jsonの
    levels.a2/levels.b1bエントリとproduction_set_cost.jsonのaudio_completion
    関連フィールドを、level別に正しく絞り込んだ値へ補正する。"""
    cost_path = f"{OUT_DIR}/cost_summary_audio.json"
    cost_doc = load_json(cost_path)
    before_snapshot = {lvl: v.get("total_jpy") for lvl, v in cost_doc.get("levels", {}).items()}

    for lvl in ("a2", "b1b"):
        breakdown = cost_breakdown_by_stage_for_level(lvl)
        cost_doc["levels"][lvl] = _cat_totals_from_breakdown(breakdown)
    cost_doc["combined_total_jpy"] = round(sum(v["total_jpy"] for v in cost_doc["levels"].values()), 2)
    cost_doc["level_cost_aggregation_bug_fix_note"] = (
        "[FIX02-COST-AGGREGATION-DISCOVERY] base.cost_breakdown_by_stage()はlevelで絞り込まず"
        "共有ログ全件を返すため、base.update_shared_outputs()を複数levelで呼ぶとlevelごとの"
        "total_jpyが二重・混入計上される(本タスクで発見)。本ファイルはstage名の\"_a2\"/\"_b1b\""
        "トークンで絞り込んだ正しいlevel別集計へ補正済み。補正前(base.update_shared_outputs()"
        f"直後、誤った値)の levels totals={before_snapshot}"
    )
    cost_doc["updated_at"] = datetime.now(timezone.utc).isoformat()
    save_json(cost_path, cost_doc)

    ps_path = f"{TREND_DIR}/production_set_cost.json"
    ps_doc = load_json(ps_path)
    ps_doc["audio_completion_cost_jpy"] = cost_doc["combined_total_jpy"]
    ps_doc["audio_completion_cost_by_level_jpy"] = {
        lvl: v["total_jpy"] for lvl, v in cost_doc["levels"].items()
    }
    ps_doc["production_set_total_cost_including_audio_jpy"] = round(174.03 + cost_doc["combined_total_jpy"], 2)
    ps_doc["audio_completion_note"] = (
        "USER-TEST-AUDIO-COMPLETION-01-TREND / USER-TEST-AUDIO-HUMAN-REVIEW-FIX-02-TREND: "
        "既存正式audio completion経路(er003_v1_n3_01_scaffold_generate/tts_generate/assemble、無変更)で"
        "A2/B1B完成episode+Web試聴playerまで仕上げた追加費用。本文Writer/Fact Checker/QA(¥174.03)には"
        "50:50配賦しない。[FIX02] level別集計はcost_aggregation_bug_fix_note参照(補正済み、正しい値)。"
    )
    save_json(ps_path, ps_doc)
    return {"cost_doc_levels": cost_doc["levels"], "combined_total_jpy": cost_doc["combined_total_jpy"],
            "production_set_total_cost_including_audio_jpy": ps_doc["production_set_total_cost_including_audio_jpy"],
            "before_snapshot_totals": before_snapshot}


def append_progress_log_fixed(level: str, level_result: dict, corrected_level_total_jpy: float) -> None:
    log_path = "er014_output/four_type_observation_01/progress_log.md"
    now = datetime.now(timezone.utc).isoformat()
    duration = level_result["assemble_result"].get("duration_seconds")
    gate_on = level_result["gate_opt_in_result"].get("gate_on_result")
    all_pass = level_result["consistency"].get("all_pass")
    line = (f"- Trend audio completion ({level}): {now} 完了(point_two Human Review承認付き再生成1回込み), "
            f"gate_off=PASS, gate_on={gate_on}, duration={duration}s, "
            f"article_audio_consistency_all_pass={all_pass}, "
            f"level_cost_jpy(corrected, level別絞り込み後)={corrected_level_total_jpy:.2f} "
            f"(管理ID: {DELEGATION_ID})\n")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(line)


def _lock_entry_snapshot(level_out_dir: str, segment_id: str) -> dict | None:
    lock_path = f"{level_out_dir}/audit/review_lock_state.json"
    if not os.path.exists(lock_path):
        return None
    lock = load_json(lock_path)
    return lock.get(segment_id)


def run_point_two_regen_once() -> dict:
    level_out_dir = f"{OUT_DIR}/a2"
    narration_dir = f"{level_out_dir}/narration"
    parts = load_json(f"{level_out_dir}/parts.json")
    results_path = f"{level_out_dir}/audit/tts_generation_results.json"
    results = load_json(results_path)

    original_text = parts["point_two_body"]
    transformed_text = cont1.apply_reading_transforms(original_text)
    tts_input = tts_gen.tts_safe_news_en(transformed_text)
    out_path = f"{narration_dir}/point_two.wav"

    # (1) 事前状態の記録
    pre_lock_entry = _lock_entry_snapshot(level_out_dir, "point_two")
    if pre_lock_entry is None:
        raise RuntimeError("[FIX02] point_twoの既存lockエントリが見つかりません(前提不一致)。STOP。")
    if pre_lock_entry.get("state") != "HUMAN_REVIEW_REQUIRED":
        raise RuntimeError(
            f"[FIX02] point_twoの現在stateがHUMAN_REVIEW_REQUIREDではありません"
            f"(state={pre_lock_entry.get('state')})。想定外の前提のためSTOP。")
    prior_text_hash = pre_lock_entry.get("canonical_text_sha256")
    current_text_hash = review_lock._text_hash(tts_input)
    if prior_text_hash != current_text_hash:
        raise RuntimeError(
            "[FIX02] 再構成したcanonical text(読み整形適用後、tts_safe_news_en適用後)のsha256が"
            f"前回lockのcanonical_text_sha256と一致しません(prior={prior_text_hash}, "
            f"current={current_text_hash})。禁止事項「テキスト変更」に抵触する可能性があるためSTOP。")
    print(f"[FIX02] point_two: 前回lockとcanonical text sha256一致を確認 ({current_text_hash[:16]}...)。")

    # (2) approve_regenerate()を1回だけ呼ぶ(ユーザー承認2026-09-15に基づく)
    approval_call_time = datetime.now(timezone.utc).isoformat()
    approval_result = review_lock.approve_regenerate(out_path, tts_input, approved_by=APPROVED_BY)
    print(f"[FIX02] approve_regenerate() 呼び出し完了: time={approval_call_time}, "
          f"out_path={out_path}, state={approval_result.get('state')}")

    # (3) 前回と同一のProduction関数・同一引数で1回だけ再生成
    run_start = time.time()
    with cl.logging_context(THEME_ID, "tts_a2_point_two_time_variance"):
        with cl.segment_context("point_two"):
            r = tts_gen.generate_a2_segment_with_slowdown(
                tts_input, out_path, tts_gen.first_words(transformed_text),
                style_prefix_override=tts_gen.A2_ENGLISH_STYLE_PREFIX_SLOWER,
                disfluency_qa=False,
                enable_connected_speech_equivalence_layer=True,
                enable_repetition_qa=True)
    run_elapsed = round(time.time() - run_start, 3)
    r["canonical_text"] = transformed_text
    r["reading_transform_applied"] = True
    r["reading_transform_original_text"] = original_text
    r["human_review_regenerate_approved"] = True
    r["human_review_regenerate_approved_by"] = APPROVED_BY
    r["human_review_regenerate_approved_at"] = approval_call_time
    results["segments"]["point_two"] = r
    save_json(results_path, results)
    print(f"[FIX02] point_two: 再生成完了 status={r.get('status')} elapsed={run_elapsed}s")

    # (4) 時間差run結果の記録
    post_lock_entry = _lock_entry_snapshot(level_out_dir, "point_two")
    prev_attempt = (pre_lock_entry.get("last_attempts_log") or [{}])[0]
    curr_attempt = (post_lock_entry.get("last_attempts_log") or [{}])[-1] if post_lock_entry else {}

    def _parse_ts(s):
        if not s:
            return None
        try:
            return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            return None

    prev_ts = _parse_ts(pre_lock_entry.get("updated_at"))
    curr_ts = _parse_ts(post_lock_entry.get("updated_at")) if post_lock_entry else None
    elapsed_between_runs_seconds = None
    if prev_ts is not None and curr_ts is not None:
        elapsed_between_runs_seconds = (curr_ts - prev_ts).total_seconds()

    variance_record = {
        "delegation_id": DELEGATION_ID,
        "segment_id": "point_two",
        "level": "a2",
        "purpose": "ユーザー承認に基づく1回限りの追加再生成。時間差/run-to-run varianceの観測を兼ねる。",
        "approval": {
            "called_at": approval_call_time,
            "out_path": out_path,
            "approved_by": APPROVED_BY,
            "approve_regenerate_return_state": approval_result.get("state"),
        },
        "canonical_text_sha256": current_text_hash,
        "canonical_text_sha256_identical_to_previous_run": True,
        "previous_run": {
            "updated_at": pre_lock_entry.get("updated_at"),
            "final_status": pre_lock_entry.get("final_status"),
            "lock_state_after": pre_lock_entry.get("state"),
            "attempt_asr_text": prev_attempt.get("asr_text"),
            "attempt_audio_classification": prev_attempt.get("audio_classification"),
            "attempt_verified": prev_attempt.get("verified"),
        },
        "current_run": {
            "updated_at": post_lock_entry.get("updated_at") if post_lock_entry else None,
            "final_status": post_lock_entry.get("final_status") if post_lock_entry else r.get("status"),
            "lock_state_after": post_lock_entry.get("state") if post_lock_entry else None,
            "attempt_asr_text": curr_attempt.get("asr_text"),
            "attempt_audio_classification": curr_attempt.get("audio_classification"),
            "attempt_verified": curr_attempt.get("verified"),
            "run_wall_clock_seconds": run_elapsed,
        },
        "elapsed_seconds_between_previous_and_current_run": elapsed_between_runs_seconds,
        "passed": r.get("status") == "OK",
    }
    save_json(f"{level_out_dir}/point_two_time_variance_run.json", variance_record)
    return {"regen_result": r, "variance_record": variance_record, "transformed_text": transformed_text,
             "original_text": original_text}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--level", choices=["a2"], required=True)
    parser.add_argument("--approve-point-two-once", action="store_true", required=True)
    args = parser.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)
    cl.install(base.LOG_PATH)

    baseline = task_baseline_cost_jpy()
    print(f"[FIX02-BUDGET] baseline(累積, 前回runまで込み)={baseline:.2f} JPY, 本タスク上限={TASK_BUDGET_JPY} JPY")

    task_check_budget(baseline, "tts_a2_point_two_time_variance")
    regen = run_point_two_regen_once()
    task_check_budget(baseline, "assemble_a2 (after point_two regen)")

    if not regen["variance_record"]["passed"]:
        print("[FIX02] STOP: point_twoの1回限り承認付き再生成が通りませんでした"
              f"(status={regen['regen_result'].get('status')})。追加retryは行わず、lockはHUMAN_REVIEW_"
              "REQUIREDのまま残します。ユーザー判断が必要(OPEN-153追記対象)。")
        return

    print("[FIX02] point_two: PASS。A2 Assembly以降へ進みます。")
    final_results = load_json(f"{OUT_DIR}/a2/audit/tts_generation_results.json")
    transform_log = cont1._fill_missing_transform_log_from_results({}, cont1.A2_FIX_SEGMENTS, final_results)
    cont1.save_tts_reading_transforms_doc("a2", transform_log, None)

    assemble_result = base.run_assembly("a2")
    if assemble_result.get("gate_off_result") != "PASS":
        raise RuntimeError(f"[FIX02][a2] Assembly(Gate OFF経路)がPASSしませんでした、STOP: {assemble_result}")

    gate_on = base.run_gate_opt_in_check("a2")
    consistency = cont1.build_consistency_check_fixed("a2")
    cont1.augment_consistency_with_transforms("a2", transform_log, None)
    consistency = load_json(f"{OUT_DIR}/a2/article_audio_consistency.json")
    web = base.build_player_and_web_delivery("a2", assemble_result)

    level_result = {
        "level": "a2", "transform_log": transform_log, "comment_4_result": None,
        "assemble_result": assemble_result, "gate_opt_in_result": gate_on,
        "consistency": consistency, "web": web,
        "cost_breakdown_jpy": base.cost_breakdown_by_stage(),  # base実装との互換のため保持(未補正値)
    }
    base.update_shared_outputs("a2", level_result)
    cost_fix = fix_cost_summary_and_production_set_cost()
    append_progress_log_fixed("a2", level_result, cost_fix["cost_doc_levels"]["a2"]["total_jpy"])

    this_task_delta_jpy = round(base.cost_so_far_jpy() - baseline, 4)
    save_json(f"{OUT_DIR}/a2/run_result_audio_completion_fix02.json", {
        "delegation_id": DELEGATION_ID, "level": "a2",
        "gate_off_result": assemble_result.get("gate_off_result"),
        "gate_on_result": gate_on.get("gate_on_result"),
        "duration_seconds": assemble_result.get("duration_seconds"),
        "consistency_all_pass": consistency.get("all_pass"),
        "this_task_delta_jpy": this_task_delta_jpy,
        "cost_fix_summary": cost_fix,
        "point_two_time_variance_run": regen["variance_record"],
    })
    print(f"===== [FIX02] level=a2 完了(this_task_delta_jpy={this_task_delta_jpy:.2f}, "
          f"trend_total_including_audio_jpy={cost_fix['production_set_total_cost_including_audio_jpy']:.2f}) =====")


if __name__ == "__main__":
    main()
