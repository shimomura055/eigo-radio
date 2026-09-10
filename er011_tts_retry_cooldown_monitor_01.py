#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
er011_tts_retry_cooldown_monitor_01.py

管理ID: TTS-RETRY-COOLDOWN-HYPOTHESIS-ANALYSIS-01

目的(cool-down仮説の検証、読み取り専用・API呼び出しなし・追加TTS生成なし):
  先行調査(TTS-RETRY-TIMING-OBSERVATION-MONITOR-01、
  TTS-REGENERATION-TIMING-DEPENDENCY-ANALYSIS-01)は「4回目だから通るか」
  (attempt番号依存)を検証し「時間依存性なし」と結論した。本scriptはユーザーが
  再定義した論点、すなわち「連続NG後、時間を空けたretryの方が、即時retryより
  PASS率が高いか」(cool-down仮説)を、自然発生retryのみを対象に集計する。
  人工的にTTS生成回数を増やすことは一切行わない。

入力(読み取り専用):
  - er011_output/tts_retry_timing_monitor_01/observations.jsonl
    (er011_tts_retry_timing_monitor_01.py の出力。本scriptを実行する前に
    そちらを先に実行し最新化しておくことを推奨するが、本script自体は
    observations.jsonlが存在すればそれを読むだけで新規スキャンはしない)

出力(このscriptが書き込むのはこの3ファイルのみ):
  - er011_output/tts_retry_cooldown_analysis_01/cooldown_pairs.jsonl
  - er011_output/tts_retry_cooldown_analysis_01/summary.json
  - er011_output/tts_retry_cooldown_analysis_01/summary.md

冪等性:
  再実行のたびに上記3ファイルを全件再生成して上書きする(追記ではない)。

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
INPUT_PATH = REPO_ROOT / "er011_output" / "tts_retry_timing_monitor_01" / "observations.jsonl"
OUT_DIR = REPO_ROOT / "er011_output" / "tts_retry_cooldown_analysis_01"

# ---------------------------------------------------------------------------
# 間隔bucket境界(秒)。データ分布に基づき決定(根拠は summary.md にも転記)。
#
# 2026-09-11時点の53件(is_retry_after_ng=True かつ gap_seconds既知)の実測分布で、
# 94秒(discovery_generalization_towels_trial_11 comment_2)と282秒
# (kp5_ja_charon attempt6→7)の間に、データ点が一切存在しない自然な間隙
# (約3倍のギャップ)がある。この間隙のどこに閾値を置いても分類結果は変わらない
# ため、閾値は150秒(2.5分、同一runの自動retryループが取りうる時間としての
# 目安)とする。同様に、567秒(household point_one)と2350秒(kp5_ja_charon
# 39分)の間にも間隙があり、30分(1800秒)境界はこの間隙の外側(2350秒側)に
# 位置するため実測分布と矛盾しない。6時間(21600秒)境界は、8357秒(2時間19分、
# point_two_heading)と51635秒(14時間21分、CAR-T)の間の大きな間隙(約6倍)の
# 中間にあり、これも実測分布と矛盾しない。
# ---------------------------------------------------------------------------
GAP_BUCKET_IMMEDIATE = 150          # <150秒 = 即時(同一run内自動retry相当)
GAP_BUCKET_SHORT = 30 * 60          # 150秒〜30分 = 短時間
GAP_BUCKET_MEDIUM = 6 * 60 * 60     # 30分〜6時間 = 中
# 6時間以上 = 長(別日相当)

BUCKET_LABELS = {
    "immediate": "即時<150秒(同一run内自動retry相当)",
    "short": "短時間 150秒〜30分",
    "medium": "中 30分〜6時間",
    "long": "長 6時間以上(別日相当)",
}

# ---------------------------------------------------------------------------
# 既知の手動介入補正(deliberate intervention override)
#
# er011_tts_retry_timing_monitor_01.py の generation_path 判定は
# 「attempt_number > max_attempts なら manual_regenerate_beyond_loop_cap、
# それ以外は automatic_retry_within_loop_cap」という機械的ルールのみに
# 基づく。しかし個別に監査した結果、下記1件は attempt_number(2) <=
# max_attempts(3) のため automatic 判定されるが、実際には
# `er012_output/editorial_b_voices_trial_09_audio/b1b/audit/
# heading_regen_03_result.json`(management_id=
# "EDITORIAL-B-FAMILY-VOICES-TRIAL-09-HEADING-REGEN-AND-FULL-EPISODE-03")
# という別名の管理IDで、2時間19分後に明示的に再実行(regen)されたことが
# 確認できる(同一run内の受動的retryではない)。この既知の1件のみ、
# 手動でオーバーライドする(自動検出ルールへの一般化はしない。理由:
# per-attempt側に「同一run内か別run再実行か」を機械的に判定できる
# フィールドが存在しないため、これ以上の自動化は誤判定リスクがある)。
# ---------------------------------------------------------------------------
DELIBERATE_INTERVENTION_OVERRIDES = {
    (
        "er012_output/editorial_b_voices_trial_09_audio/b1b",
        "point_two_heading",
        8357.0,
    ): {
        "corrected_intervention_type": "deliberate_separate_regen_run_mislabeled_as_automatic",
        "evidence_file": (
            "er012_output/editorial_b_voices_trial_09_audio/b1b/audit/"
            "heading_regen_03_result.json"
        ),
        "note": (
            "management_id=EDITORIAL-B-FAMILY-VOICES-TRIAL-09-HEADING-REGEN-AND-"
            "FULL-EPISODE-03。attempt_number<=max_attemptsのためgeneration_path"
            "フィールドはautomatic_retry_within_loop_capと機械判定されるが、"
            "実際は別名の管理IDで2時間19分後に明示的に再実行されたdeliberate regen。"
        ),
    }
}


def gap_bucket(seconds: float) -> str:
    if seconds < GAP_BUCKET_IMMEDIATE:
        return "immediate"
    if seconds < GAP_BUCKET_SHORT:
        return "short"
    if seconds < GAP_BUCKET_MEDIUM:
        return "medium"
    return "long"


def ng_before_bucket(n):
    if n is None:
        return "unknown"
    if n <= 1:
        return "1"
    if n == 2:
        return "2"
    return "3plus"


def fisher_exact_two_sided(a, b, c, d):
    """2x2表 [[a,b],[c,d]] の両側Fisher正確検定のp値(標準ライブラリのみ、
    scipy不使用)。行1=[a,b], 行2=[c,d]。周辺合計固定のもとでの超幾何分布。
    件数が小さい前提の集計のため、全探索で計算する(高速性は不要)。"""
    n = a + b + c + d
    row1 = a + b
    row2 = c + d
    col1 = a + c
    col2 = b + d
    if n == 0:
        return None

    def hyper_prob(x):
        # P(a=x | 周辺固定)
        try:
            return (
                math.comb(row1, x)
                * math.comb(row2, col1 - x)
                / math.comb(n, col1)
            )
        except ValueError:
            return 0.0

    x_min = max(0, col1 - row2)
    x_max = min(row1, col1)
    p_obs = hyper_prob(a)
    total_p = 0.0
    # 浮動小数点誤差対策の微小許容
    eps = 1e-9
    for x in range(x_min, x_max + 1):
        p_x = hyper_prob(x)
        if p_x <= p_obs + eps:
            total_p += p_x
    return min(1.0, total_p)


def load_observations():
    rows = []
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    if not INPUT_PATH.is_file():
        raise SystemExit(
            f"入力ファイルが見つかりません: {INPUT_PATH}\n"
            "先に er011_tts_retry_timing_monitor_01.py を実行してください "
            "(API呼び出し・TTS生成は一切行わないローカル集計scriptです)。"
        )

    observations = load_observations()

    pairs = []
    for o in observations:
        if not o.get("is_retry_after_ng"):
            continue
        gap = o.get("gap_seconds_since_prev_attempt_in_group")
        if gap is None:
            continue
        prev_cat = o.get("prev_attempt_ng_category")
        if prev_cat is None:
            continue

        bucket = gap_bucket(gap)
        override_key = (o.get("level_dir"), o.get("segment_id"), gap)
        override = DELIBERATE_INTERVENTION_OVERRIDES.get(override_key)

        pair = {
            "level_dir": o.get("level_dir"),
            "segment_id": o.get("segment_id"),
            "file": o.get("file"),
            "gap_seconds": gap,
            "gap_bucket": bucket,
            "gap_bucket_label": BUCKET_LABELS[bucket],
            "consecutive_ng_before_this_attempt": o.get("consecutive_ng_before_this_attempt"),
            "consecutive_ng_before_bucket": ng_before_bucket(
                o.get("consecutive_ng_before_this_attempt")
            ),
            "prev_attempt_ng_category": prev_cat,
            "prev_attempt_ng_subtype": o.get("prev_attempt_ng_subtype"),
            "generation_path_field_raw": o.get("generation_path"),
            "post_hoc_verification_change_case": o.get(
                "post_hoc_verification_change_case"
            ),
            "next_try_result_verified": o.get("verified"),
            # 交絡注記: per-attempt単位の実TTS入力テキストは保存されておらず
            # (missing_fieldsに常時含まれるper_attempt_final_tts_input_text)、
            # canonical_text_final_state_sha256はgroup単位(=このsegmentの最終
            # 状態)で1回だけ取得された値であり、attempt間でテキストが変化した
            # かどうかを直接検証する材料にはならない(既知の限界、先行調査でも
            # 指摘済み)。generation_path_field_rawのみが機械的に得られる
            # manual/automaticの代理指標であり、それも下記overrideの通り
            # 取りこぼしがあることが個別監査で判明している。
            "deliberate_intervention_override": override,
        }
        pairs.append(pair)

    pairs.sort(key=lambda p: p["gap_seconds"])

    # ---- 集計: 種別B(品質NG)のみを主対象 ----
    def build_table(rows, key_fn):
        table = {}
        for p in rows:
            key = key_fn(p)
            cell = table.setdefault(key, {"n": 0, "pass_n": 0, "examples": []})
            cell["n"] += 1
            if p["next_try_result_verified"] is True:
                cell["pass_n"] += 1
            if len(cell["examples"]) < 8:
                cell["examples"].append(
                    f"{p['segment_id']}@{p['gap_seconds']:.0f}s"
                    f"({'PASS' if p['next_try_result_verified'] else 'NG'})"
                )
        rows_out = []
        for key, cell in table.items():
            n = cell["n"]
            pr = round(cell["pass_n"] / n, 4) if n else None
            rows_out.append({"key": key, "n": n, "pass_n": cell["pass_n"],
                              "pass_rate": pr, "examples": cell["examples"]})
        return rows_out

    b_rows = [p for p in pairs if p["prev_attempt_ng_category"] == "B_quality_ng"]
    a_rows = [p for p in pairs if p["prev_attempt_ng_category"] == "A_infra_or_api_error_suspected"]

    table_bucket_only = build_table(b_rows, lambda p: p["gap_bucket"])
    table_bucket_x_ngbefore = build_table(
        b_rows, lambda p: (p["consecutive_ng_before_bucket"], p["gap_bucket"])
    )
    table_bucket_x_genpath = build_table(
        b_rows,
        lambda p: (
            p["generation_path_field_raw"],
            "deliberate_override" if p["deliberate_intervention_override"] else "no_override",
            p["gap_bucket"],
        ),
    )
    table_a_bucket_only = build_table(a_rows, lambda p: p["gap_bucket"])

    # ---- Fisher正確検定: 即時(immediate) vs 非即時(short+medium+long統合) ----
    imm = [p for p in b_rows if p["gap_bucket"] == "immediate"]
    non_imm = [p for p in b_rows if p["gap_bucket"] != "immediate"]
    a_pass = sum(1 for p in imm if p["next_try_result_verified"] is True)
    a_fail = len(imm) - a_pass
    b_pass = sum(1 for p in non_imm if p["next_try_result_verified"] is True)
    b_fail = len(non_imm) - b_pass
    fisher_p = fisher_exact_two_sided(a_pass, a_fail, b_pass, b_fail)

    fisher_result = {
        "comparison": "immediate(<150s) vs non_immediate(>=150s, short+medium+long統合)",
        "note": "種別Bのみ。参考値(件数が小さいため解釈に注意、下記sufficiency_criteria参照)。",
        "table_2x2": {
            "immediate": {"pass": a_pass, "fail": a_fail, "n": a_pass + a_fail},
            "non_immediate": {"pass": b_pass, "fail": b_fail, "n": b_pass + b_fail},
        },
        "immediate_pass_rate": round(a_pass / (a_pass + a_fail), 4) if (a_pass + a_fail) else None,
        "non_immediate_pass_rate": round(b_pass / (b_pass + b_fail), 4) if (b_pass + b_fail) else None,
        "fisher_exact_two_sided_p_value": round(fisher_p, 4) if fisher_p is not None else None,
    }

    # ---- 事前定義した「傾向が十分出た」判定基準(sufficiency criteria) ----
    # 決定はユーザー。ここでは基準の定義と、現時点での到達可否の機械判定のみ行う。
    SUFFICIENCY_CRITERIA = {
        "description": (
            "各binでN>=20 かつ、即時binと非即時bin(いずれか)のPASS率の差が"
            "20ポイント以上、かつ全ての非即時binに『deliberate_intervention'"
            "(手動介入・別run再実行)を伴わない自然発生の長間隔retryサンプル』が"
            "最低5件以上含まれること(手動介入100%のサンプルでは時間経過そのものの"
            "効果と介入効果を分離できないため)。"
        ),
        "min_n_per_bin": 20,
        "min_pass_rate_diff_points": 20,
        "min_non_intervention_long_gap_samples": 5,
    }

    non_imm_non_intervention = [
        p for p in non_imm
        if p["generation_path_field_raw"] == "automatic_retry_within_loop_cap"
        and not p["deliberate_intervention_override"]
    ]

    bucket_n = {row["key"]: row["n"] for row in table_bucket_only}
    min_bucket_n = min(bucket_n.values()) if bucket_n else 0
    max_bucket_n = max(bucket_n.values()) if bucket_n else 0
    pass_rate_diff_points = None
    if fisher_result["immediate_pass_rate"] is not None and fisher_result["non_immediate_pass_rate"] is not None:
        pass_rate_diff_points = round(
            abs(fisher_result["immediate_pass_rate"] - fisher_result["non_immediate_pass_rate"]) * 100, 1
        )

    sufficiency_check = {
        "criteria": SUFFICIENCY_CRITERIA,
        "current_state": {
            "bucket_n": bucket_n,
            "min_bucket_n_across_4_buckets": min_bucket_n,
            "pass_rate_diff_points_immediate_vs_non_immediate": pass_rate_diff_points,
            "non_immediate_samples_without_deliberate_intervention": len(non_imm_non_intervention),
            "non_immediate_samples_without_deliberate_intervention_list": [
                f"{p['segment_id']}@{p['gap_seconds']:.0f}s({p['gap_bucket']})"
                for p in non_imm_non_intervention
            ],
        },
        "criteria_met": (
            min_bucket_n >= SUFFICIENCY_CRITERIA["min_n_per_bin"]
            and (pass_rate_diff_points or 0) >= SUFFICIENCY_CRITERIA["min_pass_rate_diff_points"]
            and len(non_imm_non_intervention) >= SUFFICIENCY_CRITERIA["min_non_intervention_long_gap_samples"]
        ),
    }

    # ---- 個別ケース監査: 非即時5件全件の介入有無を明示(隠蔽なし) ----
    non_immediate_case_audit = []
    for p in sorted(non_imm, key=lambda x: x["gap_seconds"]):
        non_immediate_case_audit.append({
            "segment_id": p["segment_id"],
            "level_dir": p["level_dir"],
            "gap_seconds": p["gap_seconds"],
            "gap_bucket": p["gap_bucket"],
            "consecutive_ng_before_this_attempt": p["consecutive_ng_before_this_attempt"],
            "next_try_result_verified": p["next_try_result_verified"],
            "generation_path_field_raw": p["generation_path_field_raw"],
            "deliberate_intervention_override": p["deliberate_intervention_override"],
            "is_confounded_by_deliberate_intervention": (
                p["generation_path_field_raw"] == "manual_regenerate_beyond_loop_cap"
                or p["deliberate_intervention_override"] is not None
            ),
        })

    summary = {
        "management_id": "TTS-RETRY-COOLDOWN-HYPOTHESIS-ANALYSIS-01",
        "input_file": str(INPUT_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
        "total_retry_after_ng_pairs": len(pairs),
        "type_b_quality_ng_pairs": len(b_rows),
        "type_a_infra_suspected_pairs": len(a_rows),
        "gap_bucket_definition_seconds": {
            "immediate": f"<{GAP_BUCKET_IMMEDIATE}",
            "short": f"{GAP_BUCKET_IMMEDIATE}-{GAP_BUCKET_SHORT}",
            "medium": f"{GAP_BUCKET_SHORT}-{GAP_BUCKET_MEDIUM}",
            "long": f">={GAP_BUCKET_MEDIUM}",
        },
        "table_type_b_by_gap_bucket_only": table_bucket_only,
        "table_type_b_by_ngbefore_x_gapbucket": table_bucket_x_ngbefore,
        "table_type_b_by_generation_path_x_gapbucket": table_bucket_x_genpath,
        "table_type_a_by_gap_bucket_only_reference_only": table_a_bucket_only,
        "fisher_exact_test_immediate_vs_non_immediate": fisher_result,
        "sufficiency_check": sufficiency_check,
        "non_immediate_case_audit_all_5_or_fewer": non_immediate_case_audit,
    }

    summary_path = OUT_DIR / "summary.json"
    with open(summary_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    pairs_path = OUT_DIR / "cooldown_pairs.jsonl"
    with open(pairs_path, "w", encoding="utf-8", newline="\n") as f:
        for p in pairs:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")

    # ---- summary.md ----
    md = []
    md.append("# TTS retry cool-down hypothesis analysis — summary\n")
    md.append("(自動生成。手動編集しないこと。再実行のたびに上書きされる。)\n")
    md.append(f"- 入力: {summary['input_file']}")
    md.append(f"- retry-after-NGペア総数: {len(pairs)} (種別B: {len(b_rows)}, 種別A参考値: {len(a_rows)})\n")

    md.append("## 表1: 種別B(品質NG)— 間隔bucketのみ\n")
    md.append("| bucket | N | PASS | PASS率 |")
    md.append("|---|---|---|---|")
    for row in sorted(table_bucket_only, key=lambda r: r["key"]):
        md.append(f"| {BUCKET_LABELS[row['key']]} | {row['n']} | {row['pass_n']} | {row['pass_rate']} |")

    md.append("\n## 表2: 種別B — 連続NG回数 × 間隔bucket\n")
    md.append("| 連続NG回数 | bucket | N | PASS | PASS率 | 例 |")
    md.append("|---|---|---|---|---|---|")
    for row in sorted(table_bucket_x_ngbefore, key=lambda r: r["key"]):
        ngb, gb = row["key"]
        md.append(
            f"| {ngb} | {BUCKET_LABELS[gb]} | {row['n']} | {row['pass_n']} | "
            f"{row['pass_rate']} | {'; '.join(row['examples'])} |"
        )

    md.append("\n## 表3: 種別B — generation_path × 手動介入補正 × 間隔bucket\n")
    md.append("| generation_path(機械判定) | 介入補正 | bucket | N | PASS | PASS率 |")
    md.append("|---|---|---|---|---|---|")
    for row in sorted(table_bucket_x_genpath, key=lambda r: str(r["key"])):
        gp, ov, gb = row["key"]
        md.append(f"| {gp} | {ov} | {BUCKET_LABELS[gb]} | {row['n']} | {row['pass_n']} | {row['pass_rate']} |")

    md.append("\n## Fisher正確検定(参考値、種別Bのみ、即時 vs 非即時統合)\n")
    md.append(f"- 即時: N={fisher_result['table_2x2']['immediate']['n']}, "
              f"PASS率={fisher_result['immediate_pass_rate']}")
    md.append(f"- 非即時(短+中+長統合): N={fisher_result['table_2x2']['non_immediate']['n']}, "
              f"PASS率={fisher_result['non_immediate_pass_rate']}")
    md.append(f"- 両側Fisher正確検定 p値 = {fisher_result['fisher_exact_two_sided_p_value']}"
              f"(参考値。件数が小さいため解釈注意)")

    md.append("\n## 「傾向が十分出た」の事前定義基準と現時点の判定\n")
    md.append(f"- 基準: {SUFFICIENCY_CRITERIA['description']}")
    md.append(f"- 現状: 4bucket中の最小N = {sufficiency_check['current_state']['min_bucket_n_across_4_buckets']}"
              f"(基準N>=20)")
    md.append(f"- 現状: 即時 vs 非即時のPASS率差 = "
              f"{sufficiency_check['current_state']['pass_rate_diff_points_immediate_vs_non_immediate']}"
              f"ポイント(基準20ポイント以上)")
    md.append(f"- 現状: 手動介入を伴わない非即時サンプル数 = "
              f"{sufficiency_check['current_state']['non_immediate_samples_without_deliberate_intervention']}"
              f"件(基準5件以上、内訳: "
              f"{sufficiency_check['current_state']['non_immediate_samples_without_deliberate_intervention_list']})")
    md.append(f"- **基準到達: {sufficiency_check['criteria_met']}**")

    md.append("\n## 非即時(>=150秒)全件の個別監査(隠蔽なし、全件記載)\n")
    md.append("| segment | 間隔 | bucket | 連続NG | 結果 | generation_path | 介入補正 | 介入confound疑い |")
    md.append("|---|---|---|---|---|---|---|---|")
    for c in non_immediate_case_audit:
        md.append(
            f"| {c['segment_id']} | {c['gap_seconds']:.0f}s | {c['gap_bucket']} | "
            f"{c['consecutive_ng_before_this_attempt']} | "
            f"{'PASS' if c['next_try_result_verified'] else 'NG'} | "
            f"{c['generation_path_field_raw']} | "
            f"{'あり' if c['deliberate_intervention_override'] else 'なし'} | "
            f"{'YES' if c['is_confounded_by_deliberate_intervention'] else 'no'} |"
        )

    md.append("\n詳細は cooldown_pairs.jsonl / summary.json を参照。")

    summary_md_path = OUT_DIR / "summary.md"
    with open(summary_md_path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(md) + "\n")

    print(f"pairs_written={len(pairs)} -> {pairs_path.relative_to(REPO_ROOT)}")
    print(f"summary_json -> {summary_path.relative_to(REPO_ROOT)}")
    print(f"summary_md -> {summary_md_path.relative_to(REPO_ROOT)}")
    print(f"sufficiency_criteria_met={sufficiency_check['criteria_met']}")


if __name__ == "__main__":
    main()
