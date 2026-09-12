#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
er011_tts_retry_selection_effect_reanalysis_01.py

管理ID: TTS-RETRY-TIMING-SELECTION-EFFECT-REANALYSIS-01

目的(既存データのみ・追加Trial禁止・API呼び出しなし・追加TTS生成なし):
  先行研究(TTS-RETRY-TIMING-OBSERVATION-MONITOR-01,
  TTS-RETRY-COOLDOWN-HYPOTHESIS-ANALYSIS-01)は「連続NG回数が増えるほど
  次attemptのPASS率が下がる」ことを示したが、これは「元々難しい事例だけが
  後半まで残る」選別効果(selection effect)である可能性を明示的に分離
  していなかった。本scriptは:

  1. 母集団を「最初の3回attemptが全てNGだった事例」に限定し、4回目
     attemptのPASS率を、4回目前の待ち時間(即時<150秒 / 短150秒-30分 /
     中30分-6時間 / 長6時間以上)別に比較する(主分析)。
  2. 4回目前の人的介入(原稿変更/設定変更/route変更/明示的
     approve_regenerate()呼び出し等)の有無を分離する。
  3. より緩い母集団(位置を4回目に限定しない、連続NG回数>=3の全position)
     でも同じ比較を行う(副分析、既存cooldown_pairs.jsonlを再利用)。
  4. 選別効果の可視化として、素朴な「1回NG後/2回NG後/3回以上NG後」PASS率
     テーブルを再掲する。
  5. 検出力計算(item E向け): 想定効果量別に、alpha=0.05・power=0.8で
     必要な各群Nを機械計算する。

入力(読み取り専用、書き込み・API呼び出しは一切行わない):
  - er011_output/tts_retry_timing_monitor_01/observations.jsonl
  - er011_output/tts_retry_cooldown_analysis_01/cooldown_pairs.jsonl
  - (人的介入の根拠は、本scriptの調査時に個別に特定した既存script/JSON
    ファイルへの参照として INTERVENTION_EVIDENCE 辞書に記録する。
    自動検出できるのは route/voice/model の3->4攻撃間の変化のみであり、
    それ以外[明示的approve_regenerate()呼び出し・原稿差し替えtextfix等]は
    機械的には検出できないため、個別監査結果をハードコードする。
    一般化はしない[理由: per-attempt側に汎用の介入検出フィールドが
    存在しないため、既存のDELIBERATE_INTERVENTION_OVERRIDES方式を踏襲])。

出力(このscriptが書き込むのはこの4ファイルのみ):
  - er011_output/tts_retry_selection_effect_reanalysis_01/strict_population_cases.jsonl
  - er011_output/tts_retry_selection_effect_reanalysis_01/broader_3plus_cases.jsonl
  - er011_output/tts_retry_selection_effect_reanalysis_01/summary.json
  - er011_output/tts_retry_selection_effect_reanalysis_01/summary.md

冪等性: 再実行のたびに上記4ファイルを全件再生成して上書きする(追記ではない)。

安全性:
  - Production retry/regeneration仕様は一切変更しない(観測のみ)。
  - API呼び出し・TTS生成は行わない(¥0)。
  - SSOT・docs/pm/・Production Prompt/コードは編集しない。Git操作はしない。
"""

from __future__ import annotations

import json
import math
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
OBS_PATH = REPO_ROOT / "er011_output" / "tts_retry_timing_monitor_01" / "observations.jsonl"
PAIRS_PATH = REPO_ROOT / "er011_output" / "tts_retry_cooldown_analysis_01" / "cooldown_pairs.jsonl"
OUT_DIR = REPO_ROOT / "er011_output" / "tts_retry_selection_effect_reanalysis_01"

# ---------------------------------------------------------------------------
# 間隔bucket境界(秒)。TTS-RETRY-COOLDOWN-HYPOTHESIS-ANALYSIS-01と同一定義を
# 再利用する(定義の一貫性のため、閾値は変更しない)。
# ---------------------------------------------------------------------------
GAP_IMMEDIATE = 150
GAP_SHORT = 30 * 60
GAP_MEDIUM = 6 * 60 * 60

BUCKET_LABELS = {
    "immediate": "即時<150秒",
    "short": "短時間 150秒〜30分",
    "medium": "中 30分〜6時間",
    "long": "長 6時間以上",
}


def gap_bucket(seconds: float) -> str:
    if seconds < GAP_IMMEDIATE:
        return "immediate"
    if seconds < GAP_SHORT:
        return "short"
    if seconds < GAP_MEDIUM:
        return "medium"
    return "long"


# ---------------------------------------------------------------------------
# 人的介入の個別監査結果(本タスクでの調査により特定、ハードコード)。
# 「最初の3回attemptが全てNG」母集団(8件)全てが、機械的には
# generation_path=manual_regenerate_beyond_loop_cap(attempt_number>
# max_attempts)である。これは本システムの構造上、自動retryループは
# max_attempts到達で必ず停止するため、4回目以降のattemptは常に人間が
# 何らかのscriptを明示的に再実行しない限り発生し得ないことを意味する
# (構造的制約)。加えて、下記7件は生成scriptを直接grepし、
# review_lock.approve_regenerate()の明示的呼び出しまたは原稿本文の
# 差し替えを実際に確認した。
# ---------------------------------------------------------------------------
INTERVENTION_EVIDENCE = {
    ("er003_output/n3_01/household/fact03_fix_02/b1b", "point_one"): {
        "intervention_type": "manuscript_text_change_before_regen",
        "evidence": (
            "er011_output/open138_household_fact03_b1b_minimal_fix_02/textfix.py "
            "(OPEN-138、point_one_body本文をOLD_POINT_ONE_BODY->NEW_POINT_ONE_BODY"
            "へユーザー決定に基づき差し替えたうえでの再生成)"
        ),
    },
    ("er011_output/discovery_generalization_towels_trial_11/a2", "comment_2"): {
        "intervention_type": "explicit_approve_regenerate_plus_route_change",
        "evidence": (
            "er011_discovery_generalization_towels_trial_11_audio_02_resume_human_review.py "
            "(review_lock.approve_regenerate()呼び出し、line 66)"
        ),
    },
    ("er011_output/discovery_generalization_towels_trial_11/a2", "meaning_4"): {
        "intervention_type": "explicit_approve_regenerate_plus_route_change",
        "evidence": (
            "er011_discovery_generalization_towels_trial_11_audio_02_resume_human_review.py "
            "(review_lock.approve_regenerate()呼び出し、line 81)"
        ),
    },
    ("er011_output/discovery_generalization_towels_trial_11/b1b", "full_story_part1"): {
        "intervention_type": "explicit_approve_regenerate",
        "evidence": (
            "er011_discovery_generalization_towels_trial_11_audio_04_b1b_fullstory_resume_human_review.py "
            "(review_lock.approve_regenerate()呼び出し、line 61。既存"
            "FAMILY-A-DISCOVERY-TOWELS-B1B-SECONDARY-ASR-AND-RETRY-TIMING-RECONCILE-01_REPORT.md "
            "5節で『時間経過ではなく人的介入』と既に分類済み)"
        ),
    },
    ("er011_output/discovery_generalization_towels_trial_11/b1b", "full_story_part2"): {
        "intervention_type": "explicit_approve_regenerate",
        "evidence": (
            "er011_discovery_generalization_towels_trial_11_audio_04_b1b_fullstory_resume_human_review.py "
            "(review_lock.approve_regenerate()呼び出し、line 61。full_story_part1と同一run)"
        ),
    },
    ("er011_output/family_a_completion_a2_trend_end_to_end_01/b1b", "kp5_ja_charon"): {
        "intervention_type": "explicit_approve_regenerate_plus_route_change",
        "evidence": (
            "er011_family_a_completion_a2_trend_end_to_end_01_run.py "
            "(review_lock.approve_regenerate()呼び出し、line 387)"
        ),
    },
    ("er011_output/news_stage3_new_theme_ledger_trial_09_b1b_full/b1b", "full_story_part1"): {
        "intervention_type": "explicit_approve_regenerate",
        "evidence": (
            "er011_news_stage3_new_theme_ledger_trial_09_b1b_regen01_full_story_part1.py "
            "(review_lock.approve_regenerate()呼び出し、ユーザー決定2026-09-10に基づく"
            "『既存の承認済み再生成経路で1回のみ再生成』)"
        ),
    },
    ("er011_output/tts_attempt_audio_retention_wiring_01/evidence01/a2", "kp_new_normal"): {
        "intervention_type": "deliberate_diagnostic_parameter_sweep",
        "evidence": (
            "review_lock_state.jsonのreasonに『Minimal instruction2回+English "
            "language lock2回(合計4回)を試行済み』と明記(2つの異なるroute設定を"
            "意図的に試すdiagnostic runであり、自然発生の同一設定retryではない)"
        ),
    },
}


def wilson_ci(k: int, n: int, z: float = 1.96):
    """Wilson score interval(正規近似より小標本で安定)。"""
    if n == 0:
        return (None, None)
    phat = k / n
    denom = 1 + (z ** 2) / n
    center = phat + (z ** 2) / (2 * n)
    margin = z * math.sqrt((phat * (1 - phat) / n) + (z ** 2) / (4 * n ** 2))
    lower = (center - margin) / denom
    upper = (center + margin) / denom
    return (max(0.0, lower), min(1.0, upper))


def fisher_exact_two_sided(a, b, c, d):
    """2x2表[[a,b],[c,d]]の両側Fisher正確検定p値(標準ライブラリのみ)。
    TTS-RETRY-COOLDOWN-HYPOTHESIS-ANALYSIS-01と同一アルゴリズム。"""
    n = a + b + c + d
    row1, row2 = a + b, c + d
    col1, col2 = a + c, b + d
    if n == 0:
        return None

    def hyper_prob(x):
        try:
            return (
                math.comb(row1, x) * math.comb(row2, col1 - x) / math.comb(n, col1)
            )
        except ValueError:
            return 0.0

    x_min = max(0, col1 - row2)
    x_max = min(row1, col1)
    p_obs = hyper_prob(a)
    total_p = 0.0
    eps = 1e-9
    for x in range(x_min, x_max + 1):
        p_x = hyper_prob(x)
        if p_x <= p_obs + eps:
            total_p += p_x
    return min(1.0, total_p)


def odds_ratio(a, b, c, d):
    """0セルにはHaldane-Anscombe補正(+0.5)を全セルへ適用した参考値。"""
    if 0 in (a, b, c, d):
        a2, b2, c2, d2 = a + 0.5, b + 0.5, c + 0.5, d + 0.5
        note = "0セルありのためHaldane-Anscombe補正(+0.5)適用済み(参考値)"
    else:
        a2, b2, c2, d2 = a, b, c, d
        note = "補正なし"
    if b2 == 0 or c2 == 0:
        return None, note
    return (a2 * d2) / (b2 * c2), note


def required_n_per_group(p1: float, p2: float, alpha: float = 0.05, power: float = 0.8):
    """2群比率比較の必要サンプルサイズ(正規近似、連続性補正なし、参考値)。
    z_alpha/2=1.959964(両側5%)、z_beta=0.841621(検出力80%)固定。"""
    z_alpha2 = 1.959964
    z_beta = 0.841621
    if p1 == p2:
        return None
    numerator = (z_alpha2 + z_beta) ** 2 * (p1 * (1 - p1) + p2 * (1 - p2))
    denominator = (p1 - p2) ** 2
    return math.ceil(numerator / denominator)


def load_jsonl(path: Path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    if not OBS_PATH.is_file() or not PAIRS_PATH.is_file():
        raise SystemExit(
            "入力ファイルが見つかりません。先にer011_tts_retry_timing_monitor_01.py"
            "とer011_tts_retry_cooldown_monitor_01.pyを実行してください"
            "(いずれもAPI呼び出し・TTS生成なしのローカル集計script)。"
        )

    observations = load_jsonl(OBS_PATH)
    pairs = load_jsonl(PAIRS_PATH)

    # ------------------------------------------------------------------
    # Section 1: 選別効果の可視化(素朴集計、既存と同じ定義の再掲)
    # ------------------------------------------------------------------
    def ngb(n):
        if n is None or n <= 0:
            return "0"
        if n == 1:
            return "1"
        if n == 2:
            return "2"
        return "3plus"

    naive_all = {}
    naive_b = {}
    for o in observations:
        if not o.get("is_retry_after_ng"):
            continue
        prev_cat = o.get("prev_attempt_ng_category")
        if prev_cat is None:
            continue
        key = ngb(o.get("consecutive_ng_before_this_attempt"))
        cell = naive_all.setdefault(key, {"n": 0, "pass_n": 0})
        cell["n"] += 1
        if o.get("verified") is True:
            cell["pass_n"] += 1
        if prev_cat == "B_quality_ng":
            cellb = naive_b.setdefault(key, {"n": 0, "pass_n": 0})
            cellb["n"] += 1
            if o.get("verified") is True:
                cellb["pass_n"] += 1

    def render_naive(table):
        rows = []
        for key in ("1", "2", "3plus"):
            cell = table.get(key, {"n": 0, "pass_n": 0})
            n, p = cell["n"], cell["pass_n"]
            rate = round(p / n, 4) if n else None
            lo, hi = wilson_ci(p, n) if n else (None, None)
            rows.append({
                "consecutive_ng_before": key, "n": n, "pass_n": p,
                "pass_rate": rate,
                "wilson_95ci": [round(lo, 4), round(hi, 4)] if lo is not None else None,
            })
        return rows

    naive_selection_table_all_types = render_naive(naive_all)
    naive_selection_table_type_b_only = render_naive(naive_b)

    # ------------------------------------------------------------------
    # Section 2: 主分析 — 「最初の3回が全てNG」母集団の4回目attempt
    # ------------------------------------------------------------------
    groups = {}
    for r in observations:
        key = (r["level_dir"], r["segment_id"])
        groups.setdefault(key, []).append(r)
    for k in groups:
        groups[k].sort(key=lambda r: r["sequence_index_in_group"])

    strict_cases = []
    for key, seq in groups.items():
        if len(seq) < 4:
            continue
        first3 = seq[:3]
        if not all(a.get("verified") is False for a in first3):
            continue
        a3, a4 = seq[2], seq[3]
        gap = a4.get("gap_seconds_since_prev_attempt_in_group")
        if gap is None:
            continue
        bucket = gap_bucket(gap)
        route_changed = a3.get("route") != a4.get("route")
        voice_changed = a3.get("voice") != a4.get("voice")
        model_changed = a3.get("model") != a4.get("model")
        known = INTERVENTION_EVIDENCE.get(key)
        # generation_pathは本システムの構造上、attempt_number>max_attemptsで
        # 常にmanual_regenerate_beyond_loop_capとなる(自動retryはmax_attempts
        # で必ず停止するため、4回目以降は常に人間による明示的な再実行が必要)。
        structurally_requires_manual_rerun = (a4.get("generation_path") ==
                                               "manual_regenerate_beyond_loop_cap")
        any_detected_or_known_intervention = bool(
            route_changed or voice_changed or model_changed or known
            or structurally_requires_manual_rerun
        )
        strict_cases.append({
            "level_dir": key[0],
            "segment_id": key[1],
            "n_attempts_in_group": len(seq),
            "first3_ng_subtypes": [a.get("ng_subtype") for a in first3],
            "gap_seconds_before_4th": gap,
            "gap_bucket": bucket,
            "attempt4_verified": a4.get("verified"),
            "attempt4_ng_subtype": a4.get("ng_subtype"),
            "route_changed_3to4": route_changed,
            "voice_changed_3to4": voice_changed,
            "model_changed_3to4": model_changed,
            "generation_path_attempt4": a4.get("generation_path"),
            "structurally_requires_manual_rerun_beyond_loop_cap": structurally_requires_manual_rerun,
            "known_intervention_evidence": known,
            "any_detected_or_known_intervention": any_detected_or_known_intervention,
        })

    strict_cases.sort(key=lambda c: c["gap_seconds_before_4th"])

    def two_group_stats(cases, immediate_pred, label):
        imm = [c for c in cases if immediate_pred(c)]
        non_imm = [c for c in cases if not immediate_pred(c)]
        a_pass = sum(1 for c in imm if c["attempt4_verified"] is True)
        a_n = len(imm)
        b_pass = sum(1 for c in non_imm if c["attempt4_verified"] is True)
        b_n = len(non_imm)
        a_lo, a_hi = wilson_ci(a_pass, a_n) if a_n else (None, None)
        b_lo, b_hi = wilson_ci(b_pass, b_n) if b_n else (None, None)
        fisher_p = fisher_exact_two_sided(a_pass, a_n - a_pass, b_pass, b_n - b_pass)
        orv, or_note = odds_ratio(a_pass, a_n - a_pass, b_pass, b_n - b_pass)
        return {
            "label": label,
            "immediate": {
                "n": a_n, "pass_n": a_pass,
                "pass_rate": round(a_pass / a_n, 4) if a_n else None,
                "wilson_95ci": [round(a_lo, 4), round(a_hi, 4)] if a_lo is not None else None,
            },
            "non_immediate": {
                "n": b_n, "pass_n": b_pass,
                "pass_rate": round(b_pass / b_n, 4) if b_n else None,
                "wilson_95ci": [round(b_lo, 4), round(b_hi, 4)] if b_lo is not None else None,
            },
            "pass_rate_diff_points": (
                round((b_pass / b_n - a_pass / a_n) * 100, 1)
                if a_n and b_n else None
            ),
            "fisher_exact_two_sided_p_value": round(fisher_p, 4) if fisher_p is not None else None,
            "odds_ratio_non_immediate_vs_immediate": (
                round(orv, 4) if orv is not None else None
            ),
            "odds_ratio_note": or_note,
        }

    strict_main = two_group_stats(
        strict_cases, lambda c: c["gap_bucket"] == "immediate",
        "主分析: 最初の3回全NG母集団、4回目attempt、即時 vs 非即時(全8件)",
    )
    strict_no_intervention = [c for c in strict_cases if not c["any_detected_or_known_intervention"]]
    strict_sub_no_intervention = two_group_stats(
        strict_no_intervention, lambda c: c["gap_bucket"] == "immediate",
        "副分析: 上記のうち介入なしに限定(N={})".format(len(strict_no_intervention)),
    )

    n_strict_total = len(strict_cases)
    n_strict_with_intervention = sum(1 for c in strict_cases if c["any_detected_or_known_intervention"])

    # ------------------------------------------------------------------
    # Section 3: 副分析 — 位置を限定しない「連続NG回数>=3」母集団(既存
    # cooldown_pairs.jsonlのconsecutive_ng_before_bucket=="3plus"行を再利用)
    # ------------------------------------------------------------------
    broader_cases = [
        p for p in pairs
        if p.get("consecutive_ng_before_bucket") == "3plus"
        and p.get("prev_attempt_ng_category") == "B_quality_ng"
    ]
    for p in broader_cases:
        p["is_manual_regenerate_beyond_loop_cap"] = (
            p.get("generation_path_field_raw") == "manual_regenerate_beyond_loop_cap"
        )

    broader_main = two_group_stats(
        [{"gap_bucket": p["gap_bucket"], "attempt4_verified": p["next_try_result_verified"]}
         for p in broader_cases],
        lambda c: c["gap_bucket"] == "immediate",
        "副分析: 連続NG回数>=3(位置不問、全{}件)、即時 vs 非即時".format(len(broader_cases)),
    )
    n_broader_manual = sum(1 for p in broader_cases if p["is_manual_regenerate_beyond_loop_cap"])

    # ------------------------------------------------------------------
    # Section 4: failure type別(参考値、N不足前提)
    # ------------------------------------------------------------------
    failure_type_ref = {}
    for c in strict_cases:
        # attempt3(直前のNG)のng_subtypeで分類(4回目時点でどのfailure typeを
        # 引き継いでいたか)
        ft = c["first3_ng_subtypes"][2]
        cell = failure_type_ref.setdefault(ft, {"immediate": [0, 0], "non_immediate": [0, 0]})
        grp = "immediate" if c["gap_bucket"] == "immediate" else "non_immediate"
        cell[grp][0] += 1
        if c["attempt4_verified"] is True:
            cell[grp][1] += 1

    failure_type_rows = []
    for ft, cell in failure_type_ref.items():
        failure_type_rows.append({
            "failure_type_at_3rd_ng": ft,
            "immediate_n": cell["immediate"][0], "immediate_pass": cell["immediate"][1],
            "non_immediate_n": cell["non_immediate"][0], "non_immediate_pass": cell["non_immediate"][1],
        })

    # ------------------------------------------------------------------
    # Section 5: タオルB1 full_story_part1 観測例(既存報告の再掲・引用のみ)
    # ------------------------------------------------------------------
    towel_case_key = ("er011_output/discovery_generalization_towels_trial_11/b1b", "full_story_part1")
    towel_case_detail = next((c for c in strict_cases if
                               (c["level_dir"], c["segment_id"]) == towel_case_key), None)
    towel_observation_note = {
        "segment": "discovery_generalization_towels_trial_11/b1b full_story_part1",
        "take1_to_3": "2022 survey文が丸ごと欠落するTRUE_CONTENT_MISMATCH(3回連続NG)",
        "take4_gap_seconds": towel_case_detail["gap_seconds_before_4th"] if towel_case_detail else None,
        "take4_result": towel_case_detail["attempt4_verified"] if towel_case_detail else None,
        "failure_mode_change_observed": (
            "take4以降、2022 survey文の欠落(content drop)は解消したが、"
            "take5で新たな残存差分(has→had、TRUE_CONTENT_MISMATCH、語差型)が"
            "発生し、segmentは現在もHUMAN_REVIEW_REQUIREDのまま未解決"
            "(既存FAMILY-A-DISCOVERY-TOWELS-B1B-SECONDARY-ASR-AND-RETRY-TIMING-"
            "RECONCILE-01_REPORT.md Part A/B参照)"
        ),
        "causal_attribution": (
            "既存報告(同上REPORT.md 5節)で『時間経過ではなく人的介入"
            "(review_lock.approve_regenerate()の明示的呼び出し)』と既に分類済み。"
            "時間効果単独への帰属はできない。本reanalysisはこの結論を上書きしない"
            "(1事例のみでの時間効果断定は禁止、指示7項)。"
        ),
    }

    # ------------------------------------------------------------------
    # Section 6: 検出力計算(item E向け、正規近似・参考値)
    # ------------------------------------------------------------------
    power_scenarios = []
    p_non_immediate_anchor = 0.40  # strict主分析(0.4286)・広義副分析(0.3636)の中間的丸め値
    for p_immediate in (0.10, 0.20, 0.30):
        n = required_n_per_group(p_immediate, p_non_immediate_anchor)
        power_scenarios.append({
            "assumed_immediate_pass_rate": p_immediate,
            "assumed_non_immediate_pass_rate": p_non_immediate_anchor,
            "diff_points": round((p_non_immediate_anchor - p_immediate) * 100, 1),
            "required_n_per_group_alpha05_power80": n,
        })

    # ------------------------------------------------------------------
    # 出力
    # ------------------------------------------------------------------
    strict_cases_path = OUT_DIR / "strict_population_cases.jsonl"
    with open(strict_cases_path, "w", encoding="utf-8", newline="\n") as f:
        for c in strict_cases:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    broader_cases_path = OUT_DIR / "broader_3plus_cases.jsonl"
    with open(broader_cases_path, "w", encoding="utf-8", newline="\n") as f:
        for p in broader_cases:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")

    summary = {
        "management_id": "TTS-RETRY-TIMING-SELECTION-EFFECT-REANALYSIS-01",
        "inputs": {
            "observations_jsonl": str(OBS_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
            "cooldown_pairs_jsonl": str(PAIRS_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
            "observations_count": len(observations),
            "cooldown_pairs_count": len(pairs),
        },
        "section1_naive_selection_effect": {
            "all_types": naive_selection_table_all_types,
            "type_b_only": naive_selection_table_type_b_only,
            "note": (
                "『1回NG後→69%、2回NG後→17%、3回以上NG後→24-27%』という非単調な"
                "低下は、そのまま『時間経過が悪い』と解釈すべきではない。3回以上"
                "NGバケツには複数attempt位置(4回目・5回目・6回目…)の観測が"
                "重複して含まれ、かつ元々失敗し続けている難しいsegmentほど何度も"
                "登場する(comment_2等)。主分析ではこの重複・選別を排除するため"
                "『最初の3回全NG→4回目』という一意な位置に母集団を限定する。"
            ),
        },
        "section2_main_analysis_strict_population": {
            "population_definition": (
                "level_dir+segment_id単位でグループ化し、sequence_index 1,2,3の"
                "verifiedが全てFalseで、かつ4回目attemptが存在し4回目直前の"
                "gap_secondsが既知の事例。"
            ),
            "n_total_cases": n_strict_total,
            "n_cases_with_detected_or_known_intervention": n_strict_with_intervention,
            "n_cases_without_any_detected_or_known_intervention": n_strict_total - n_strict_with_intervention,
            "structural_note": (
                "本システムのProduction retry実装は自動retryをmax_attempts到達で"
                "必ず停止する(er011_tts_retry_timing_monitor_01.pyのgeneration_path"
                "判定と同じ根拠)。したがって4回目以降のattemptは、この母集団8件"
                "全件でgeneration_path=manual_regenerate_beyond_loop_capとなり、"
                "構造上必ず人間が明示的に別scriptを再実行して発生する。加えて"
                "本タスクの個別script監査により、8件中7件でreview_lock."
                "approve_regenerate()の明示的呼び出しまたは原稿本文の差し替え"
                "(textfix.py)を直接確認した(INTERVENTION_EVIDENCE参照)。残り1件"
                "(kp_new_normal)も意図的なdiagnostic parameter sweepであり、"
                "自然発生の『同一設定のまま時間だけ空いたretry』は本母集団に"
                "0件である。"
            ),
            "main_comparison_immediate_vs_non_immediate": strict_main,
            "sub_analysis_excluding_any_intervention": strict_sub_no_intervention,
            "sub_analysis_note": (
                "介入なし副分析はN={}であり、統計的判断はできない(参考値のみ)。"
                "指示4項の『人的介入ありしか長時間群に存在しない場合は時間効果"
                "単独を推定できないと明記する』に該当する状況が、この母集団では"
                "非即時群だけでなく全群(即時群含む)に及んでいる。"
            ).format(len(strict_no_intervention)),
            "cases": strict_cases,
        },
        "section3_broader_position_unrestricted_population": {
            "population_definition": (
                "位置を4回目に限定せず、consecutive_ng_before_this_attempt>=3の"
                "全attempt(既存cooldown_pairs.jsonlの3plus行、種別Bのみ)。"
                "同一segmentが複数position(4回目・5回目・6回目…)で重複計上"
                "されうる点に注意(主分析ではないため参考位置づけ)。"
            ),
            "n_total_cases": len(broader_cases),
            "n_cases_manual_regenerate_beyond_loop_cap": n_broader_manual,
            "comparison_immediate_vs_non_immediate": broader_main,
            "note": (
                "この母集団も{}件中{}件(100%)がmanual_regenerate_beyond_loop_cap"
                "であり、主分析と同じ構造的confoundが存在する。"
            ).format(len(broader_cases), n_broader_manual),
        },
        "section4_failure_type_reference_only": {
            "note": "各セルN<5が大半のため統計化せず参考値のみ。",
            "rows": failure_type_rows,
        },
        "section5_towel_full_story_part1_observation": towel_observation_note,
        "section6_power_calculation_for_future_data_planning": {
            "method": (
                "2群比率比較の正規近似サンプルサイズ公式(連続性補正なし)、"
                "alpha=0.05(両側)、power=0.80、z_alpha/2=1.959964、"
                "z_beta=0.841621。scipy等の統計ライブラリは使用せず、既存"
                "cooldown分析と同一方針で標準ライブラリのみで計算(参考値)。"
            ),
            "anchor_non_immediate_pass_rate": p_non_immediate_anchor,
            "anchor_note": (
                "主分析(N=8)の非即時PASS率0.4286と副分析(N=15)の非即時"
                "PASS率0.3636の中間的な丸め値0.40を基準とした。即時側の想定値は"
                "3シナリオ(10%/20%/30%)を例示する(現状データの即時群はN=1-4と"
                "極small・0件PASSのため、真の即時PASS率を精度良く推定できていない)。"
            ),
            "scenarios": power_scenarios,
            "current_data_sufficiency": (
                "主分析母集団(自然発生・介入なしの4回目観測)は現状0件。副分析"
                "(位置不問)でも介入なし0件。したがって上記シナリオのいずれの"
                "必要Nに対しても、現時点の『介入なし』有効サンプルは0件であり、"
                "本テーマの検出力は実質ゼロ。"
            ),
        },
        "final_answers": {
            "A_does_time_gap_group_have_higher_4th_pass_rate_after_controlling_difficulty": (
                "主分析(N=8、最初の3回全NG母集団)では、非即時群のPASS率"
                "(42.9%, 3/7)が即時群(0%, 0/1)より高いが、即時群N=1のため"
                "この比較自体が意味のある推定ではない。副分析(N=15、位置不問)"
                "では非即時36.4%(4/11) vs 即時0%(0/4)で方向性は同じだが、"
                "こちらも即時群N=4と小さい。『選別効果を制御した後でも時間を"
                "空けた方が高い』とは言えるだけの精度のデータがない。"
            ),
            "B_is_the_difference_statistically_significant": (
                "いいえ。Fisher正確検定p値は主分析={}、副分析={}であり、"
                "N不足のため有意差ありとは判定できない(p値だけで『効果なし』"
                "と断定もしない。項目の趣旨通り、判定不能が正しい記述)。"
            ).format(
                strict_main["fisher_exact_two_sided_p_value"],
                broader_main["fisher_exact_two_sided_p_value"],
            ),
            "C_does_trend_remain_after_excluding_human_intervention": (
                "検証不能。主分析母集団8件全件(100%)が構造的または個別確認"
                "された人的介入(approve_regenerate()明示呼び出し7件、原稿"
                "差し替え1件[point_oneは差し替えと介入が重複])を伴い、"
                "介入なしの自然発生サンプルは即時・非即時いずれの群にも"
                "0件である。したがって『介入を除いても傾向が残るか』という"
                "問いには、現状データでは回答できない(YESともNOとも言えない)。"
            ),
            "D_is_there_enough_basis_to_make_time_gap_retry_a_production_spec_candidate": (
                "いいえ。理由: (1)主分析N=8は極小、(2)母集団100%が人的介入を"
                "伴い時間効果と介入効果が完全に交絡、(3)Fisher p値は有意水準に"
                "遠く及ばず、(4)本システムのアーキテクチャ上、max_attempts超の"
                "attemptは常に人間の明示的操作を要するため、現行の自動retry"
                "ループ内に『時間を空ける』仕様を追加しても、そもそも4回目以降が"
                "発生する条件(=人間の介入)自体が変わらない限り効果を検証する"
                "自然発生データが増えない構造的な問題がある。"
            ),
            "E_what_data_would_be_needed": (
                "(1) 各群{}〜{}件(想定効果量20-30ポイント差、alpha=0.05・"
                "power=0.80の場合の目安、section6参照)の『介入なし』自然発生"
                "4回目観測が必要。(2) それには自動retryのmax_attempts自体を"
                "一時的に4以上へ緩めるか、既存max_attempts=3のまま複数の異なる"
                "segmentで『人間が何もtext/設定を変えずにapprove_regenerateだけ"
                "実行する』運用を意図的に増やす必要がある(ただしこれ自体が"
                "『人工的にサンプルを増やす』ため、本タスクの『追加Trial禁止』"
                "原則とは別の、将来のPM決定が必要な運用変更)。(3) 即時retry"
                "側も同様に、3回連続NG後に即座に4回目を実行しつつ設定変更なしの"
                "ケースを増やす必要がある(現状はN=1のみ)。(4) 人工的にサンプル"
                "数を増やさない場合は、通常のProduction運用が自然に蓄積するのを"
                "待つほかなく、蓄積速度は月あたりのHUMAN_REVIEW_REQUIRED到達件数"
                "に依存するため、現在のペースでは目安件数に達するまで相当の"
                "期間を要すると見込まれる(具体的な月数の推定は本タスクの範囲外、"
                "運用側のHUMAN_REVIEW_REQUIRED到達頻度データが必要)。"
            ).format(
                power_scenarios[0]["required_n_per_group_alpha05_power80"],
                power_scenarios[2]["required_n_per_group_alpha05_power80"],
            ),
        },
        "closeout": {
            "verdict": "REJECTED",
            "verdict_scope": (
                "『時間を空けるretry』をProduction仕様候補として今回採用しない、"
                "という意味でのREJECTED。『時間経過に効果が存在しない』という"
                "主張のREJECTEDではない(N不足・交絡のため効果の有無自体が"
                "判定不能。指示のとおり有意差なし=効果なしとは結論しない)。"
            ),
            "n_insufficiency": "主分析N=8(うち介入なし0件)、副分析N=15(うち介入なし0件)。",
            "confounding": (
                "システム構造上、max_attempts超のattemptは常に人的介入を伴う。"
                "現行ログには『介入なしで時間だけ空いた自然発生の4回目retry』が"
                "存在しない。"
            ),
            "selection_effect": (
                "素朴な連続NG回数別PASS率の低下(69%→17%→24-27%)は、同一の"
                "困難segmentが複数position(4,5,6回目…)で重複計上されることに"
                "よる部分が大きい。母集団を『最初の3回全NG→4回目』に一意化"
                "すると、非即時群のPASS率(36-43%)は素朴な3+バケツの値"
                "(24-27%)よりむしろ高く、選別効果を制御すると『連続NGが"
                "即座に悪化を意味する』という単純な解釈は支持されない。"
            ),
        },
    }

    summary_path = OUT_DIR / "summary.json"
    with open(summary_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    # ---- summary.md(簡潔な人間向けサマリ) ----
    md = []
    md.append("# TTS retry timing selection-effect reanalysis — summary\n")
    md.append("(自動生成。手動編集しないこと。再実行のたびに上書きされる。)\n")
    md.append(f"- observations: {len(observations)}件 / cooldown_pairs: {len(pairs)}件\n")

    md.append("## Section1: 選別効果(素朴集計、種別Bのみ)\n")
    md.append("| 連続NG回数 | N | PASS | PASS率 | Wilson95%CI |")
    md.append("|---|---|---|---|---|")
    for row in naive_selection_table_type_b_only:
        md.append(f"| {row['consecutive_ng_before']} | {row['n']} | {row['pass_n']} | "
                   f"{row['pass_rate']} | {row['wilson_95ci']} |")

    md.append("\n## Section2: 主分析(最初の3回全NG→4回目、N=8)\n")
    md.append(f"- 即時: N={strict_main['immediate']['n']}, PASS率={strict_main['immediate']['pass_rate']}, "
               f"95%CI={strict_main['immediate']['wilson_95ci']}")
    md.append(f"- 非即時: N={strict_main['non_immediate']['n']}, PASS率={strict_main['non_immediate']['pass_rate']}, "
               f"95%CI={strict_main['non_immediate']['wilson_95ci']}")
    md.append(f"- 差: {strict_main['pass_rate_diff_points']}ポイント、"
               f"Fisher両側p={strict_main['fisher_exact_two_sided_p_value']}、"
               f"OR={strict_main['odds_ratio_non_immediate_vs_immediate']}({strict_main['odds_ratio_note']})")
    md.append(f"- 介入なし副分析: N={len(strict_no_intervention)}件(統計不能)")
    md.append(f"- **母集団8件中{n_strict_with_intervention}件が人的介入あり(100%)**\n")

    md.append("### 8件の内訳\n")
    md.append("| segment | gap | bucket | 4回目結果 | route変化 | 既知介入 |")
    md.append("|---|---|---|---|---|---|")
    for c in strict_cases:
        md.append(
            f"| {c['segment_id']} | {c['gap_seconds_before_4th']:.0f}s | {c['gap_bucket']} | "
            f"{'PASS' if c['attempt4_verified'] else 'NG'} | "
            f"{'あり' if c['route_changed_3to4'] else 'なし'} | "
            f"{c['known_intervention_evidence']['intervention_type'] if c['known_intervention_evidence'] else '(構造上manual)'} |"
        )

    md.append("\n## Section3: 副分析(連続NG>=3、位置不問、N={})\n".format(len(broader_cases)))
    md.append(f"- 即時: N={broader_main['immediate']['n']}, PASS率={broader_main['immediate']['pass_rate']}")
    md.append(f"- 非即時: N={broader_main['non_immediate']['n']}, PASS率={broader_main['non_immediate']['pass_rate']}")
    md.append(f"- Fisher両側p={broader_main['fisher_exact_two_sided_p_value']}")
    md.append(f"- manual_regenerate_beyond_loop_cap: {n_broader_manual}/{len(broader_cases)}件(100%)\n")

    md.append("## Section5: タオルB1 full_story_part1 観測例\n")
    md.append(f"- take4 gap={towel_observation_note['take4_gap_seconds']}秒, "
               f"結果={'PASS' if towel_observation_note['take4_result'] else 'NG'}")
    md.append(f"- {towel_observation_note['failure_mode_change_observed']}")
    md.append(f"- {towel_observation_note['causal_attribution']}\n")

    md.append("## Section6: 検出力計算(参考値)\n")
    md.append("| 即時PASS率(仮定) | 非即時PASS率(仮定) | 差(pt) | 必要N/群(alpha.05,power.8) |")
    md.append("|---|---|---|---|")
    for s in power_scenarios:
        md.append(f"| {s['assumed_immediate_pass_rate']} | {s['assumed_non_immediate_pass_rate']} | "
                   f"{s['diff_points']} | {s['required_n_per_group_alpha05_power80']} |")
    md.append(f"\n- 現状の『介入なし』有効サンプル: 0件(主分析・副分析とも)\n")

    md.append("## Closeout\n")
    md.append(f"- **verdict: {summary['closeout']['verdict']}**")
    md.append(f"- {summary['closeout']['verdict_scope']}")
    md.append(f"- N不足: {summary['closeout']['n_insufficiency']}")
    md.append(f"- 交絡: {summary['closeout']['confounding']}")
    md.append(f"- 選別効果: {summary['closeout']['selection_effect']}")

    md.append("\n詳細はstrict_population_cases.jsonl / broader_3plus_cases.jsonl / summary.jsonを参照。")

    summary_md_path = OUT_DIR / "summary.md"
    with open(summary_md_path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(md) + "\n")

    print(f"strict_cases_written={len(strict_cases)} -> {strict_cases_path.relative_to(REPO_ROOT)}")
    print(f"broader_cases_written={len(broader_cases)} -> {broader_cases_path.relative_to(REPO_ROOT)}")
    print(f"summary_json -> {summary_path.relative_to(REPO_ROOT)}")
    print(f"summary_md -> {summary_md_path.relative_to(REPO_ROOT)}")
    print(f"strict_main_fisher_p={strict_main['fisher_exact_two_sided_p_value']}")
    print(f"broader_main_fisher_p={broader_main['fisher_exact_two_sided_p_value']}")
    print(f"n_strict_with_intervention={n_strict_with_intervention}/{n_strict_total}")


if __name__ == "__main__":
    main()
