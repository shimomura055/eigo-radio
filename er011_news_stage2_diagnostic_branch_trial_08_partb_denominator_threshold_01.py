# ============================================================
# er011_news_stage2_diagnostic_branch_trial_08_partb_denominator_threshold_01.py
# FAMILY-A-NEWS-STAGE2-DIAGNOSTIC-BRANCH-TRIAL-08 Part B (N-2、¥0)
# ============================================================
# 目的(ユーザー決定2026-09-09、N-2=(a)): 閾値0.40・分母は変更せず、既存
# 240件(Trial-04/05/06/07の全attemptのP1/P2)のoverlap分布を用いて、
# 「分母の語数正規化案」と「閾値再校正の必要性」を数値で示す(判断材料
# のみ、¥0、Production/Prompt/共有module/SSOT編集なし、新規API呼び出し
# なし)。
#
# 再利用(import・無変更、読み取り専用): er011_point_quality_stage1_
# recomputation_01.RUNS(既存の50 run・240 Point観測の読み込み結果、
# enumerate_runs/load_run_data、Trial-04/05/06/07の
# point_overlap_article_retry_log.jsonを読むだけ)。新規の集計ロジックの
# みここに追加する(再改変ではなく別ファイルからの追加集計)。
# ============================================================
from __future__ import annotations

import json
import statistics
from pathlib import Path

import er011_point_quality_stage1_recomputation_01 as stage1

OUT_DIR = Path("er011_output/news_stage2_diagnostic_branch_trial_08/partb")
OUT_DIR.mkdir(parents=True, exist_ok=True)

THRESHOLD = 0.40
ONE_WORD_DELTA = 0.037  # Opus引用値、stage1 (a)で再確認済み(1語≈0.0333〜0.037)


def collect_rows():
    rows = []
    for run in stage1.RUNS:
        for att in run["retry_log"]:
            report = att.get("report") or {}
            for point_key in ("point_one", "point_two"):
                pdata = report.get(point_key, {}).get("before_overlap")
                if not pdata:
                    continue
                wc = pdata.get("point_word_count")
                ratio = pdata.get("overlap_ratio")
                shared = pdata.get("shared_words")
                flagged = pdata.get("flagged")
                if wc is None or ratio is None or shared is None:
                    continue
                rows.append({
                    "trial": run["trial"], "theme": run["theme"], "condition": run["condition"],
                    "run": run["run"], "attempt": att.get("attempt"), "point": point_key,
                    "point_word_count": wc, "shared_word_count": len(shared),
                    "overlap_ratio": ratio, "flagged": bool(flagged),
                })
    return rows


def percentile(sorted_vals, value):
    """valueが分布の何パーセンタイルに位置するか(<=valueの割合)。"""
    n = len(sorted_vals)
    if n == 0:
        return None
    count_le = sum(1 for v in sorted_vals if v <= value)
    return round(100 * count_le / n, 2)


def analyze_threshold_position(rows):
    ratios = sorted(r["overlap_ratio"] for r in rows)
    n = len(ratios)
    pct = percentile(ratios, THRESHOLD)
    quartiles = statistics.quantiles(ratios, n=4) if n >= 4 else None
    boundary_lo, boundary_hi = THRESHOLD - ONE_WORD_DELTA, THRESHOLD + ONE_WORD_DELTA
    in_boundary = [r for r in rows if boundary_lo <= r["overlap_ratio"] <= boundary_hi]
    return {
        "n": n,
        "threshold": THRESHOLD,
        "threshold_percentile_of_observed_distribution": pct,
        "mean_ratio": round(statistics.mean(ratios), 4),
        "median_ratio": round(statistics.median(ratios), 4),
        "stdev_ratio": round(statistics.stdev(ratios), 4),
        "quartiles(Q1,Q2,Q3)": [round(q, 4) for q in quartiles] if quartiles else None,
        "one_word_delta_used": ONE_WORD_DELTA,
        "boundary_band": [round(boundary_lo, 4), round(boundary_hi, 4)],
        "n_observations_in_boundary_band(within_1_word_of_threshold)": len(in_boundary),
        "pct_observations_in_boundary_band": round(100 * len(in_boundary) / n, 2),
        "note": "閾値0.40が観測分布のどの位置にあるか(percentile)。境界帯は"
                "『あと1語shared word数が変わればflag判定が反転する』観測の数"
                "(stage1(a)で確認済みの1語あたり変化量≈0.037を使用)。",
    }


# ============================================================
# 分母正規化案(数式提示、採用しない・判断材料のみ):
#   ratio_norm = shared_word_count / D_fixed
#   D_fixed = 観測分布の中央値point_word_count(30語、stage1(a)の中央値と
#   同一)を固定分母として採用する案。現行 ratio = shared / point_word_count
#   (Point自身の語数で正規化)から、固定語数で正規化する方式へ変更した
#   場合の影響を、同じ閾値0.40のまま試算する。
# ============================================================
D_FIXED = 30  # stage1 (a) 中央値30語(FAMILY-A-POINT-QUALITY-STAGE1-RECOMPUTATION-01_REPORT.md 44行)


def analyze_denominator_normalization(rows):
    n = len(rows)
    changed = []
    for r in rows:
        ratio_norm = round(r["shared_word_count"] / D_FIXED, 4)
        flagged_norm = ratio_norm >= THRESHOLD
        r2 = dict(r)
        r2["ratio_norm_fixed_denominator"] = ratio_norm
        r2["flagged_norm"] = flagged_norm
        r2["flag_changed"] = flagged_norm != r["flagged"]
        changed.append(r2)

    n_flagged_current = sum(1 for r in changed if r["flagged"])
    n_flagged_norm = sum(1 for r in changed if r["flagged_norm"])
    newly_flagged = [r for r in changed if r["flagged_norm"] and not r["flagged"]]
    no_longer_flagged = [r for r in changed if r["flagged"] and not r["flagged_norm"]]

    # newly/no-longer flagged の word count 傾向(短いPointが新たにflagされる
    # か、長いPointがflag解除されるかの方向性確認)
    def wc_mean(lst):
        return round(statistics.mean(r["point_word_count"] for r in lst), 2) if lst else None

    # NG率への影響試算(run単位、point_one/point_twoいずれかがflagged=True
    # ならそのattemptはlexical_flagged相当とみなす簡易試算。実際のstill_
    # flagged判定[value QAとのOR]やretry後の実際のNG rateは再現していない
    # ため、あくまで「lexical flag発生頻度」への影響の粗い試算)。
    by_attempt = {}
    for r in changed:
        key = (r["trial"], r["theme"], r["condition"], r["run"], r["attempt"])
        by_attempt.setdefault(key, {"flagged": False, "flagged_norm": False})
        by_attempt[key]["flagged"] = by_attempt[key]["flagged"] or r["flagged"]
        by_attempt[key]["flagged_norm"] = by_attempt[key]["flagged_norm"] or r["flagged_norm"]
    n_attempts = len(by_attempt)
    attempt_flagged_current = sum(1 for v in by_attempt.values() if v["flagged"])
    attempt_flagged_norm = sum(1 for v in by_attempt.values() if v["flagged_norm"])

    return {
        "formula": "ratio_norm = shared_word_count / D_fixed, D_fixed=30(観測分布の中央値point_word_count、"
                   "stage1(a)と同一値)。現行: ratio = shared_word_count / point_word_count"
                   "(Point自身の異なり内容語数)。閾値0.40は据え置き、分子(shared_word_count)は不変。",
        "n_point_observations": n,
        "n_flagged_current_denominator": n_flagged_current,
        "current_flagged_rate": round(100 * n_flagged_current / n, 2),
        "n_flagged_fixed_denominator_30": n_flagged_norm,
        "fixed_denom_flagged_rate": round(100 * n_flagged_norm / n, 2),
        "n_point_observations_flag_status_changed": len(newly_flagged) + len(no_longer_flagged),
        "newly_flagged_under_fixed_denominator": {
            "count": len(newly_flagged), "mean_point_word_count": wc_mean(newly_flagged),
            "note": "現行分母では未flagだが固定分母30なら新たにflagされる観測(=元のpoint_word_countが"
                    "30語より小さいため、固定分母だと相対的にoverlapが強く出るケース)。",
        },
        "no_longer_flagged_under_fixed_denominator": {
            "count": len(no_longer_flagged), "mean_point_word_count": wc_mean(no_longer_flagged),
            "note": "現行分母ではflag済みだが固定分母30なら未flagとなる観測(=元のpoint_word_countが"
                    "30語より大きいため、固定分母だと相対的にoverlapが弱く出るケース)。",
        },
        "attempt_level_lexical_flag_rate_impact(rough_estimate)": {
            "note": "run×attempt単位で、point_one/two いずれかがflaggedならそのattemptを"
                    "『lexical flag相当』とみなす粗い試算(still_flaggedのOR判定・retry後の"
                    "実際のNG rateは再現していない。分母変更だけを孤立させた試算値)。",
            "n_attempts": n_attempts,
            "attempt_lexical_flag_rate_current": round(100 * attempt_flagged_current / n_attempts, 2),
            "attempt_lexical_flag_rate_fixed_denominator_30": round(100 * attempt_flagged_norm / n_attempts, 2),
        },
        "caution": "本試算は判断材料の提示のみ(採用しない)。閾値0.40は据え置き、分母のみを仮に"
                   "固定した場合の機械的な再計算であり、Fact Safety・実運用適合性の検討は含まない"
                   "(A-UDR-7観測Exit条件・OPEN-134との整合確認はUDR対象、"
                   "FAMILY-A-POINT-QUALITY-STAGE1-RECOMPUTATION-01_REPORT.md UDR候補(ii)参照)。",
    }


# ============================================================
# Focus系施策の改善が境界効果(閾値付近)に依存する割合
# ============================================================
CONDITION_PAIRS = {
    "trial_06:focus_hint": ("trial_06", "baseline", "focus_hint"),
    "trial_06:hint_only": ("trial_06", "baseline", "hint_only"),
    "trial_04:focus": ("trial_04", "baseline", "focus"),
    "trial_05:gapfix": ("trial_05", "baseline", "gapfix"),
    "trial_07:discovery_focus": ("trial_07", "baseline", "discovery_focus"),
}


def analyze_boundary_dependency(rows):
    boundary_lo, boundary_hi = THRESHOLD - ONE_WORD_DELTA, THRESHOLD  # 「僅差で未flag」帯(境界のすぐ下)
    results = {}
    for label, (trial, control_cond, treat_cond) in CONDITION_PAIRS.items():
        control_rows = [r for r in rows if r["trial"] == trial and r["condition"] == control_cond]
        treat_rows = [r for r in rows if r["trial"] == trial and r["condition"] == treat_cond]
        if not control_rows or not treat_rows:
            continue
        control_flagged = sum(1 for r in control_rows if r["flagged"])
        treat_flagged = sum(1 for r in treat_rows if r["flagged"])
        control_flagged_rate = control_flagged / len(control_rows)
        treat_flagged_rate = treat_flagged / len(treat_rows)
        reduction_rate = control_flagged_rate - treat_flagged_rate

        treat_non_flagged = [r for r in treat_rows if not r["flagged"]]
        treat_boundary_adjacent = [r for r in treat_non_flagged if boundary_lo <= r["overlap_ratio"] < boundary_hi]

        # 「改善が境界効果に依存する割合」の定義:
        # treatment条件の非flag観測のうち、閾値のすぐ下(1語分)に位置する
        # ものの比率。この比率が高いほど、施策条件の『flagされていない』
        # という結果は僅差(あと1語shared wordが増えればflagされていた)
        # に依存していることを意味する。
        dependency_pct = (round(100 * len(treat_boundary_adjacent) / len(treat_non_flagged), 2)
                           if treat_non_flagged else None)
        results[label] = {
            "n_control": len(control_rows), "n_treat": len(treat_rows),
            "control_flagged_rate_pct": round(100 * control_flagged_rate, 2),
            "treat_flagged_rate_pct": round(100 * treat_flagged_rate, 2),
            "flagged_rate_reduction_pct_points": round(100 * reduction_rate, 2),
            "n_treat_non_flagged": len(treat_non_flagged),
            "n_treat_non_flagged_within_1_word_of_threshold": len(treat_boundary_adjacent),
            "pct_of_treat_non_flagged_observations_that_are_boundary_adjacent": dependency_pct,
        }
    return results


def main():
    rows = collect_rows()
    threshold_position = analyze_threshold_position(rows)
    denom_normalization = analyze_denominator_normalization(rows)
    boundary_dependency = analyze_boundary_dependency(rows)

    result = {
        "meta": {
            "management_id": "FAMILY-A-NEWS-STAGE2-DIAGNOSTIC-BRANCH-TRIAL-08",
            "part": "Part B (N-2=(a)、¥0)",
            "n_point_observations": len(rows),
            "source": "er011_point_quality_stage1_recomputation_01.RUNS (Trial-04/05/06/07、全50 run、"
                       "全attemptのpoint_overlap_article_retry_log.json、既存JSON読み取りのみ、新規"
                       "API呼び出しなし)。",
            "threshold_unchanged": THRESHOLD,
            "denominator_unchanged_in_production": "現行分母(Point自身の異なり内容語数)は変更していない"
                                                     "(本Partは判断材料の提示のみ)。",
        },
        "threshold_position_in_observed_distribution": threshold_position,
        "denominator_normalization_proposal": denom_normalization,
        "boundary_effect_dependency_of_focus_family_improvements": boundary_dependency,
    }

    with open(OUT_DIR / "partb_results.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


if __name__ == "__main__":
    main()
