#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
er011_tts_retry_timing_monitor_01.py

管理ID: TTS-RETRY-TIMING-OBSERVATION-MONITOR-01

目的:
  TTSリトライ間隔(retry interval)と再生成PASS率の関係を、過去ログから
  決定論的に(LLM不使用・API呼び出しなし・追加TTS生成なし)集計する観測基盤。

前提となる調査:
  TTS-REGENERATION-TIMING-DEPENDENCY-ANALYSIS-01_REPORT.md (読み取り専用調査、
  CAR-T記事 full_story_part1 の 3回連続NG→14時間21分後PASS 事例を起点とする)

入力(読み取り専用、書き込み・削除・API呼び出しは一切行わない):
  - er0*_output/**/narration/attempts/*.json (segmentごとのattempt記録、
    418〜420件規模、本スクリプトの主データ源)
  - er0*_output/**/audit/review_lock_state.json (Human Review Lock状態、
    存在する場合のみ、segment単位の最終スナップショット)
  - er0*_output/**/audit/human_approved_segments.json (事後承認・ASR再照合の
    証跡。存在する場合のみ。householdのtopic_intro型「検証ロジック変更」事例を
    識別するためのフラグ源)
  - er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl
    (Human Reviewキューへの登録記録。wav_pathで attempt の source_out_path と
    突合する)

出力(このスクリプトが書き込むのはこの3ファイルのみ):
  - er011_output/tts_retry_timing_monitor_01/observations.jsonl
  - er011_output/tts_retry_timing_monitor_01/summary.json
  - er011_output/tts_retry_timing_monitor_01/summary.md

冪等性:
  再実行のたびに上記3ファイルを「全ログの再走査結果」でまるごと上書きする
  (追記ではない)。ログが増えれば次回実行時に自動的に反映される。

安全性:
  - Production retry/regeneration仕様は一切変更しない(観測のみ)。
  - API呼び出し・TTS生成は行わない(¥0)。
  - SSOT(CURRENT_SPEC.md等)・docs/pm/・Production Prompt/コードは編集しない。
  - Git操作はしない。
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
OUT_DIR = REPO_ROOT / "er011_output" / "tts_retry_timing_monitor_01"

# 種別A(API/infra error)を疑う文字列シグナル(大文字小文字無視)。
# 現行の narration/attempts/*.json スキーマには専用の infra-error フィールドが
# 存在しないため、レコード全体のJSON文字列表現に対する保守的な文字列探索で
# 代用する(取りこぼしを許容し、誤検出よりも「検出できない」ことを正直に報告する
# 設計。詳細はREPORTの限界注記を参照)。
INFRA_ERROR_SIGNALS = [
    "429", "rate limit", "ratelimit", "timeout", "time out", "5xx",
    "500 ", "502", "503", "504", "deadline exceeded", "resourceexhausted",
    "connection reset", "network error", "service unavailable",
]

# retry間隔バケット境界(秒)。仕様の「即時〜5分/5〜30分/30分〜数時間/
# 数時間〜翌日以降」に対応する具体的な閾値(このスクリプト内でのみ有効な定義)。
GAP_BUCKET_5MIN = 5 * 60
GAP_BUCKET_30MIN = 30 * 60
GAP_BUCKET_6H = 6 * 60 * 60


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def to_posix(p: Path) -> str:
    try:
        rel = p.resolve().relative_to(REPO_ROOT)
    except ValueError:
        rel = p
    return str(rel).replace("\\", "/")


def find_attempt_files():
    files = []
    for base in sorted(REPO_ROOT.glob("er0*_output")):
        if not base.is_dir():
            continue
        for p in base.rglob("narration/attempts/*.json"):
            files.append(p)
    return sorted(set(files))


def safe_load_json(path: Path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return {"__load_error__": str(e)}


def parse_ts(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None


def classify_ng(raw: dict):
    """種別A(infra)/種別B(品質NG)の判定と、種別Bのサブタイプを返す。
    verified=True(PASS)の場合は (None, None) を返す。"""
    if raw.get("verified") is True:
        return None, None

    blob = json.dumps(raw, ensure_ascii=False).lower()
    for sig in INFRA_ERROR_SIGNALS:
        if sig in blob:
            return "A_infra_or_api_error_suspected", sig

    audio_class = raw.get("audio_classification")
    rep_qa = raw.get("repetition_qa_evidence") or {}
    rep_flagged = bool(isinstance(rep_qa, dict) and rep_qa.get("flagged"))
    length_ok = raw.get("length_ok")

    if audio_class == "TRUE_CONTENT_MISMATCH":
        subtype = "content_mismatch_or_word_omission"
    elif audio_class == "ASR_VALIDATION_UNCERTAIN":
        subtype = "asr_uncertain"
    elif audio_class == "TTS_FAILURE":
        subtype = "tts_generation_content_failure_non_infra"
    elif rep_flagged:
        subtype = "repetition_or_disfluency_flagged"
    elif length_ok is False:
        subtype = "length_mismatch"
    else:
        subtype = f"other_quality_ng:{audio_class}"

    return "B_quality_ng", subtype


def gap_bucket(seconds):
    if seconds is None:
        return None
    if seconds < GAP_BUCKET_5MIN:
        return "1_immediate_lt5min"
    if seconds < GAP_BUCKET_30MIN:
        return "2_5to30min"
    if seconds < GAP_BUCKET_6H:
        return "3_30min_to_6h"
    return "4_6h_to_next_day_or_later"


def load_level_dir_cache(level_dir: Path):
    """level_dir配下の audit/*.json を一度だけ読み込みキャッシュする。"""
    cache = {}
    audit_dir = level_dir / "audit"
    for name in ("review_lock_state.json", "human_approved_segments.json",
                 "tts_generation_results.json"):
        p = audit_dir / name
        if p.is_file():
            cache[name] = safe_load_json(p)
        else:
            cache[name] = None
    return cache


def load_human_review_queue():
    path = REPO_ROOT / "er006_output" / "audio_retry_cascade_prod_01" / "human_review_queue.jsonl"
    entries = []
    if path.is_file():
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entries.append(json.loads(line))
                except Exception:
                    continue
    return entries


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    attempt_files = find_attempt_files()
    human_review_queue = load_human_review_queue()

    # (theme_id/level/segment_idではなく) level_dir(narrationフォルダの親)を
    # グルーピングキーの一部に使う。rerunフォルダなど、theme_id/level/segment_id
    # の値自体が別ランで重複しうるため、フォルダパスで物理的に分離する。
    raw_records = []  # list of dict: parsed attempt + meta
    level_dir_cache = {}

    load_errors = []

    for f in attempt_files:
        raw = safe_load_json(f)
        if "__load_error__" in raw:
            load_errors.append({"file": to_posix(f), "error": raw["__load_error__"]})
            continue

        attempts_dir = f.parent          # .../narration/attempts
        narration_dir = attempts_dir.parent   # .../narration
        level_dir = narration_dir.parent      # .../<level>

        level_key = to_posix(level_dir)
        if level_key not in level_dir_cache:
            level_dir_cache[level_key] = load_level_dir_cache(level_dir)

        segment_id = raw.get("segment_id")
        group_key = (level_key, segment_id)

        raw_records.append({
            "file": to_posix(f),
            "level_dir": level_key,
            "group_key": group_key,
            "raw": raw,
        })

    # segment_id が取れないレコードは集計不能として除外し、missing扱いで記録する
    usable = [r for r in raw_records if r["group_key"][1]]
    unusable = [r for r in raw_records if not r["group_key"][1]]

    # グループ化
    groups = {}
    for r in usable:
        groups.setdefault(r["group_key"], []).append(r)

    observations = []
    group_pattern_rows = []  # 事例一覧生成用

    for group_key, recs in groups.items():
        level_key, segment_id = group_key
        cache = level_dir_cache.get(level_key, {})

        # timestampでソート。saved_atが欠損/不正な場合は末尾に安定的に配置。
        def sort_key(r):
            ts = parse_ts(r["raw"].get("saved_at"))
            return (ts is None, ts or datetime.max, r["file"])

        recs_sorted = sorted(recs, key=sort_key)

        theme_id_values = set(r["raw"].get("theme_id") for r in recs_sorted)
        level_values = set(r["raw"].get("level") for r in recs_sorted)

        review_lock = None
        rls = cache.get("review_lock_state.json")
        if isinstance(rls, dict) and segment_id in rls:
            entry = rls[segment_id]
            if isinstance(entry, dict):
                review_lock = {
                    "state": entry.get("state"),
                    "reason": entry.get("reason"),
                    "final_status": entry.get("final_status"),
                    "updated_at": entry.get("updated_at"),
                    "cumulative_tts_attempts": entry.get("cumulative_tts_attempts"),
                    "cumulative_asr_calls": entry.get("cumulative_asr_calls"),
                    "budget_guard_triggered": entry.get("budget_guard_triggered"),
                }

        human_approved = None
        post_hoc_verification_change_case = False
        has_json = cache.get("human_approved_segments.json")
        if isinstance(has_json, dict) and segment_id in has_json:
            entry = has_json[segment_id]
            if isinstance(entry, dict):
                human_approved = {
                    "approved_at": entry.get("approved_at"),
                    "note": entry.get("note"),
                    "management_id": entry.get("management_id"),
                    "has_asr_reverify_evidence": "asr_reverify_evidence" in entry,
                }
                if "asr_reverify_evidence" in entry or "asr_homophone_evidence" in entry:
                    post_hoc_verification_change_case = True

        canonical_text_final_state = None
        canonical_text_final_state_sha256 = None
        tgr = cache.get("tts_generation_results.json")
        if isinstance(tgr, dict):
            seg = (tgr.get("segments") or {}).get(segment_id)
            if isinstance(seg, dict) and isinstance(seg.get("text"), str):
                canonical_text_final_state = seg["text"]
                canonical_text_final_state_sha256 = sha256_text(seg["text"])

        prev_verified = None
        prev_raw = None
        prev_ts = None
        consecutive_ng_before = 0

        for idx, r in enumerate(recs_sorted, start=1):
            raw = r["raw"]
            ts = parse_ts(raw.get("saved_at"))

            gap_seconds = None
            if ts is not None and prev_ts is not None:
                gap_seconds = (ts - prev_ts).total_seconds()

            is_retry_after_ng = (prev_verified is False)
            bucket = gap_bucket(gap_seconds) if is_retry_after_ng else None

            ng_category, ng_subtype = classify_ng(raw)

            prev_ng_category, prev_ng_subtype = (None, None)
            same_ng_reason_as_prev = None
            exact_asr_text_repeat = None
            if is_retry_after_ng and prev_raw is not None:
                prev_ng_category, prev_ng_subtype = classify_ng(prev_raw)
                same_class = (prev_raw.get("audio_classification") == raw.get("audio_classification"))
                same_ng_reason_as_prev = same_class
                pa, ca = prev_raw.get("asr_text"), raw.get("asr_text")
                if isinstance(pa, str) and isinstance(ca, str):
                    exact_asr_text_repeat = (pa == ca)

            attempt_number = raw.get("attempt_number")
            max_attempts = raw.get("max_attempts")
            if attempt_number is not None and max_attempts is not None:
                generation_path = (
                    "manual_regenerate_beyond_loop_cap"
                    if attempt_number > max_attempts
                    else "automatic_retry_within_loop_cap"
                )
            else:
                generation_path = "unknown"

            has_cascade_fields = "cascade_invoked" in raw
            has_repetition_qa_fields = "repetition_qa_checked" in raw
            has_disfluency_fields = "disfluency_checked" in raw
            verification_schema_variant = (
                f"cascade_fields={has_cascade_fields}"
                f"|repetition_qa_fields={has_repetition_qa_fields}"
                f"|disfluency_fields={has_disfluency_fields}"
            )

            source_out_path = raw.get("source_out_path")
            hr_matches = []
            if source_out_path:
                norm_target = source_out_path.replace("\\", "/")
                for e in human_review_queue:
                    wp = (e.get("wav_path") or "").replace("\\", "/")
                    if wp == norm_target:
                        hr_matches.append({
                            "timestamp": e.get("timestamp"),
                            "final_status": e.get("final_status"),
                            "cost_guard_triggered": e.get("cost_guard_triggered"),
                        })

            asr_text = raw.get("asr_text")
            missing_fields = []
            for fld in ("model", "voice", "route", "saved_at", "audio_classification",
                        "verified", "length_ok"):
                if raw.get(fld) is None:
                    missing_fields.append(fld)
            missing_fields.append("per_attempt_final_tts_input_text")  # 既知の欠落(全件共通)
            missing_fields.append("actual_backend_model_revision")     # 既知の欠落(全件共通)
            if canonical_text_final_state is None:
                missing_fields.append("canonical_text_final_state")
            if not has_cascade_fields:
                missing_fields.append("cascade_invoked")
                missing_fields.append("cascade_steps")
            if not has_repetition_qa_fields:
                missing_fields.append("repetition_qa_evidence")
            if not has_disfluency_fields:
                missing_fields.append("disfluency_evidence")

            obs = {
                "file": r["file"],
                "level_dir": level_key,
                "theme_id": raw.get("theme_id"),
                "level": raw.get("level"),
                "segment_id": segment_id,
                "sequence_index_in_group": idx,
                "attempt_number_field": attempt_number,
                "max_attempts_field": max_attempts,
                "attempt_number_seq_mismatch": (attempt_number != idx) if attempt_number is not None else None,
                "loop_attempt_index": raw.get("loop_attempt_index"),
                "generation_path": generation_path,
                "model": raw.get("model"),
                "voice": raw.get("voice"),
                "route": raw.get("route"),
                "language": raw.get("language"),
                "tts_execution_mode": raw.get("tts_execution_mode"),
                "instruction_text_present": raw.get("instruction_text") is not None,
                "asr_prompt_applied": raw.get("asr_prompt_applied"),
                "saved_at": raw.get("saved_at"),
                "gap_seconds_since_prev_attempt_in_group": gap_seconds,
                "gap_bucket_if_retry_after_ng": bucket,
                "is_retry_after_ng": is_retry_after_ng,
                "consecutive_ng_before_this_attempt": consecutive_ng_before,
                "audio_classification": raw.get("audio_classification"),
                "length_ok": raw.get("length_ok"),
                "verified": raw.get("verified"),
                "asr_text": asr_text,
                "asr_text_sha256": sha256_text(asr_text) if isinstance(asr_text, str) else None,
                "sha256_audio": raw.get("sha256"),
                "disfluency_checked": raw.get("disfluency_checked"),
                "disfluency_evidence_present": raw.get("disfluency_evidence") is not None,
                "repetition_qa_checked": raw.get("repetition_qa_checked"),
                "repetition_qa_flagged": (
                    bool((raw.get("repetition_qa_evidence") or {}).get("flagged"))
                    if isinstance(raw.get("repetition_qa_evidence"), dict) else None
                ),
                "cascade_invoked": raw.get("cascade_invoked"),
                "cascade_steps": raw.get("cascade_steps"),
                "non_latin_cascade_enabled": raw.get("non_latin_cascade_enabled"),
                "non_latin_cascade_invoked": raw.get("non_latin_cascade_invoked"),
                "verification_schema_variant": verification_schema_variant,
                "ng_category": ng_category,
                "ng_subtype": ng_subtype,
                "same_ng_reason_as_prev_attempt": same_ng_reason_as_prev,
                "exact_asr_text_repeat_vs_prev_attempt": exact_asr_text_repeat,
                "prev_attempt_ng_category": prev_ng_category,
                "prev_attempt_ng_subtype": prev_ng_subtype,
                "canonical_text_final_state_caveat": (
                    "level_dir/audit/tts_generation_results.json の segments[segment_id].text は"
                    "そのsegmentの最終(=最後に成功/最新)状態を指し、この特定attempt時点で実際に"
                    "TTS APIへ渡された入力文字列そのものではない可能性がある"
                    "(先行調査TTS-REGENERATION-TIMING-DEPENDENCY-ANALYSIS-01_REPORT.md 3節の既知の欠落)。"
                ),
                "canonical_text_final_state": canonical_text_final_state,
                "canonical_text_final_state_sha256": canonical_text_final_state_sha256,
                "review_lock_state_snapshot": review_lock,
                "human_approved_segments_entry": human_approved,
                "post_hoc_verification_change_case": post_hoc_verification_change_case,
                "human_review_queue_matches": hr_matches,
                "source_out_path": source_out_path,
                "missing_fields": missing_fields,
            }
            observations.append(obs)

            if raw.get("verified") is False:
                consecutive_ng_before += 1
            else:
                consecutive_ng_before = 0

            prev_verified = raw.get("verified")
            prev_raw = raw
            prev_ts = ts if ts is not None else prev_ts

        group_pattern_rows.append({
            "level_dir": level_key,
            "segment_id": segment_id,
            "theme_id_values": sorted(x for x in theme_id_values if x),
            "n_attempts": len(recs_sorted),
            "verified_sequence": [r["raw"].get("verified") for r in recs_sorted],
            "post_hoc_verification_change_case": post_hoc_verification_change_case,
        })

    observations.sort(key=lambda o: (o["level_dir"], o["segment_id"], o["sequence_index_in_group"]))

    # ---- observations.jsonl 書き出し ----
    obs_path = OUT_DIR / "observations.jsonl"
    with open(obs_path, "w", encoding="utf-8", newline="\n") as f:
        for o in observations:
            f.write(json.dumps(o, ensure_ascii=False) + "\n")

    # ---- 集計: 種別Bのみを主対象に P(next PASS | consecutive_ng_before, gap_bucket) ----
    table_b = {}  # (ng_before_bucket, gap_bucket) -> {"n":..,"pass":..}
    table_a = {}
    excluded_post_hoc_rows = []

    def ng_before_bucket(n):
        if n <= 0:
            return "0"
        if n == 1:
            return "1"
        if n == 2:
            return "2"
        return "3plus"

    for o in observations:
        if not o["is_retry_after_ng"]:
            continue
        if o["gap_bucket_if_retry_after_ng"] is None:
            continue
        prev_cat = o["prev_attempt_ng_category"]
        if prev_cat is None:
            continue

        if o["post_hoc_verification_change_case"]:
            excluded_post_hoc_rows.append(o["file"])

        key = (ng_before_bucket(o["consecutive_ng_before_this_attempt"]), o["gap_bucket_if_retry_after_ng"])
        target = table_b if prev_cat == "B_quality_ng" else table_a
        cell = target.setdefault(key, {"n": 0, "pass_n": 0})
        cell["n"] += 1
        if o["verified"] is True:
            cell["pass_n"] += 1

    def render_table(t):
        rows = []
        for (ngb, gb), cell in sorted(t.items()):
            n = cell["n"]
            p = cell["pass_n"]
            rate = round(p / n, 4) if n else None
            rows.append({
                "consecutive_ng_before_bucket": ngb,
                "gap_bucket": gb,
                "n": n,
                "pass_n": p,
                "pass_rate": rate,
            })
        return rows

    table_b_rows = render_table(table_b)
    table_a_rows = render_table(table_a)

    # ---- 類似事例一覧(パターン分類、決定論的ルール) ----
    def classify_pattern(row):
        seq = row["verified_sequence"]
        n = len(seq)
        if n < 2:
            return "single_attempt_only"
        if all(v is True for v in seq):
            return "all_pass_no_retry_needed"
        if all(v is False for v in seq):
            return "never_resolved_all_ng_in_log"
        # 末尾がPASSで、直前に連続NGがあるか
        last_pass = (seq[-1] is True)
        # 連続NG数(先頭からの塊、複数塊がありうるので最大塊長を見る)
        max_run = 0
        cur = 0
        for v in seq:
            if v is False:
                cur += 1
                max_run = max(max_run, cur)
            else:
                cur = 0
        if last_pass and max_run >= 3:
            return "ng_x3plus_then_eventually_pass"
        if last_pass and max_run == 2:
            return "ng_x2_then_eventually_pass"
        if last_pass and max_run == 1:
            return "ng_x1_then_pass_simple_retry"
        if not last_pass:
            return "ends_in_ng_unresolved_in_log"
        return "other_pattern"

    pattern_counts = {}
    pattern_examples = {}
    for row in group_pattern_rows:
        pat = classify_pattern(row)
        pattern_counts[pat] = pattern_counts.get(pat, 0) + 1
        pattern_examples.setdefault(pat, [])
        if len(pattern_examples[pat]) < 5:
            pattern_examples[pat].append({
                "level_dir": row["level_dir"],
                "segment_id": row["segment_id"],
                "n_attempts": row["n_attempts"],
                "verified_sequence": row["verified_sequence"],
                "post_hoc_verification_change_case": row["post_hoc_verification_change_case"],
            })

    n_groups = len(group_pattern_rows)
    n_groups_multi = sum(1 for r in group_pattern_rows if r["n_attempts"] >= 2)

    summary = {
        "management_id": "TTS-RETRY-TIMING-OBSERVATION-MONITOR-01",
        "generated_at_note": "スクリプト実行のたびに全ログを再走査し上書き生成(冪等)。実行日時はrun_evidence側で別途記録。",
        "input_counts": {
            "attempt_files_scanned": len(attempt_files),
            "attempt_files_load_errors": len(load_errors),
            "records_with_segment_id": len(usable),
            "records_without_segment_id_excluded": len(unusable),
            "distinct_segments_groups": n_groups,
            "groups_with_2plus_attempts": n_groups_multi,
            "human_review_queue_entries": len(human_review_queue),
        },
        "load_errors": load_errors,
        "gap_bucket_definition_seconds": {
            "1_immediate_lt5min": "<300",
            "2_5to30min": "300-1800",
            "3_30min_to_6h": "1800-21600",
            "4_6h_to_next_day_or_later": ">=21600",
        },
        "table_type_b_quality_ng_next_pass_rate": table_b_rows,
        "table_type_a_infra_suspected_next_pass_rate": table_a_rows,
        "type_a_note": (
            "現行の narration/attempts/*.json スキーマには429/5xx/timeout等を示す専用フィールドが"
            "存在しないため、種別Aはレコード文字列中の保守的キーワード検索でのみ検出している。"
            "検出0件の場合は『infra errorが存在しなかった』ではなく『このログ形式からは検出できな"
            "かった』という意味であることに注意。"
        ),
        "post_hoc_verification_change_case_rows_excluded_from_causal_reading": excluded_post_hoc_rows,
        "pattern_counts": pattern_counts,
        "pattern_examples": pattern_examples,
    }

    summary_path = OUT_DIR / "summary.json"
    with open(summary_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    # ---- summary.md ----
    md = []
    md.append("# TTS retry timing monitor — summary\n")
    md.append("(自動生成。手動編集しないこと。再実行のたびに上書きされる。)\n")
    md.append(f"- attempt files scanned: {len(attempt_files)} (load errors: {len(load_errors)})")
    md.append(f"- usable records (segment_id あり): {len(usable)}")
    md.append(f"- distinct segment groups: {n_groups} (2+ attempts: {n_groups_multi})")
    md.append(f"- human_review_queue.jsonl entries: {len(human_review_queue)}\n")

    md.append("## 表1: 種別B(品質NG)のみ — P(次attemptがPASS | 直前連続NG回数, retry間隔bucket)\n")
    md.append("| 直前連続NG回数 | 間隔bucket | N | PASS数 | PASS率 |")
    md.append("|---|---|---|---|---|")
    for row in table_b_rows:
        md.append(f"| {row['consecutive_ng_before_bucket']} | {row['gap_bucket']} | {row['n']} | {row['pass_n']} | {row['pass_rate']} |")
    if not table_b_rows:
        md.append("| (該当行なし) | | | | |")

    md.append("\n## 表2: 種別A(API/infra error疑い)— 同形式\n")
    md.append("| 直前連続NG回数 | 間隔bucket | N | PASS数 | PASS率 |")
    md.append("|---|---|---|---|---|")
    for row in table_a_rows:
        md.append(f"| {row['consecutive_ng_before_bucket']} | {row['gap_bucket']} | {row['n']} | {row['pass_n']} | {row['pass_rate']} |")
    if not table_a_rows:
        md.append("| (該当行なし。0件=『infra errorなし』ではなく『このログ形式からは検出不能』の意味) | | | | |")

    md.append("\n## 検証ロジック変更(post-hoc)により表1から除外すべき行(household topic_intro型)\n")
    if excluded_post_hoc_rows:
        for x in excluded_post_hoc_rows:
            md.append(f"- {x}")
    else:
        md.append("- (該当なし)")

    md.append("\n## パターン別件数(segment単位、group_pattern分類)\n")
    md.append("| パターン | 件数 |")
    md.append("|---|---|")
    for k, v in sorted(pattern_counts.items(), key=lambda x: -x[1]):
        md.append(f"| {k} | {v} |")

    md.append("\n詳細は observations.jsonl / summary.json を参照。")

    summary_md_path = OUT_DIR / "summary.md"
    with open(summary_md_path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(md) + "\n")

    print(f"attempt_files_scanned={len(attempt_files)}")
    print(f"usable_records={len(usable)} unusable_records={len(unusable)}")
    print(f"distinct_segments_groups={n_groups} groups_with_2plus_attempts={n_groups_multi}")
    print(f"observations_written={len(observations)} -> {to_posix(obs_path)}")
    print(f"summary_json -> {to_posix(summary_path)}")
    print(f"summary_md -> {to_posix(summary_md_path)}")


if __name__ == "__main__":
    main()
