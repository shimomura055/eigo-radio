# ============================================================
# er006_pool_pilot_01_attempt_ledger.py
# ER-006-POOL-PILOT-COST-ROOTFIX-01: segment/attempt単位のAttempt Ledger再構築
# ============================================================
# 既存の audit/tts_generation_results.json (segment単位のASR attempt記録) と
# raw_usage_log.jsonl (call単位の実費用) を、実行順序に基づき突き合わせて、
# segment/attempt単位のCost Ledgerを再構築する。
#
# 突き合わせ方法: audit側はsegment名・attempt番号・ASR文字列・verdictは持つが
# 費用が無い。raw_usage_log側は費用があるがsegment名が無い。両方とも同一プロセス
# 内で生成順どおりに記録されているため、audit側から求めたsegmentごとの
# 「物理attempt数(standard+fallback合計)」の順に raw_usage_log の
# (gemini,azure)ペアを先頭から消費して割り当てる。突合が合わない場合は
# 例外を出し、UNKNOWNとして扱う(過大な精度を主張しない)。
from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime

LUNA_IN, LUNA_CACHED, LUNA_OUT = 0.20, 0.02, 1.20
GEMINI_IN, GEMINI_OUT = 1.00, 20.00
AZURE_HOUR = 1.00
USD_JPY = 160.0

THEMES = ["pool_benches", "pool_subscriptions", "pool_startups"]
LEVELS = [("b1b", "b1"), ("a2", "a2")]


def gemini_cost_jpy(r):
    it, ot = r.get("input_tokens") or 0, r.get("output_tokens") or 0
    return ((it / 1e6) * GEMINI_IN + (ot / 1e6) * GEMINI_OUT) * USD_JPY


def azure_cost_jpy(r):
    sec = r.get("audio_duration_submitted_seconds") or 0
    return (sec / 3600) * AZURE_HOUR * USD_JPY


def flatten_segment(name, seg, kp_id=None, component=None):
    """audit JSON内の1コンポーネント分を(segment記述, attemptリスト)へ正規化する。"""
    records = []
    if "standard_attempts_log" in seg:
        for a in seg.get("standard_attempts_log", []):
            records.append({"path": "standard", **a})
        for a in seg.get("fallback_attempts_log", []):
            records.append({"path": "fallback_minimal_instruction", **a})
    elif "attempts_log" in seg:
        for a in seg.get("attempts_log", []):
            records.append({"path": "single", **a})
    else:
        pass  # UNKNOWN構造(このsegmentは復元不能)
    return records


def iter_components(audit):
    """audit全体を(segment_label, component_dict)の列へ展開する。"""
    for name, seg in audit.get("segments", {}).items():
        yield name, seg
    for kp_id, kp in audit.get("key_phrases", {}).items():
        for comp_key in ("english", "japanese", "japanese_meaning"):
            if comp_key in kp:
                yield f"kp{kp_id}_{comp_key}", kp[comp_key]


def build_ledger_for_episode(theme, level_dir, level_key):
    audit_path = f"er006_output/pool_pilot_01/{theme}/{level_dir}/audit/tts_generation_results.json"
    audit = json.load(open(audit_path, encoding="utf-8"))

    component_attempts = []  # [(comp_label, [attempt_dicts...]), ...] 実行順
    for name, seg in iter_components(audit):
        atts = flatten_segment(name, seg)
        component_attempts.append((name, seg.get("status"), atts))

    expected_pairs = sum(len(atts) for _, _, atts in component_attempts)
    return component_attempts, expected_pairs


# pool_benches/a2は、JAPANESE_TITLES KeyErrorによるクラッシュ→再実行(同一連続runの中で
# 発生、gapベースのsubrun分割では検知できない)により、topic_introが2回生成された
# (1回目6.531秒・2回目6.331秒、共に08:20:56/08:21:54とほぼ連続するタイムスタンプで、
# 内容・長さがほぼ同一)。audit(tts_generation_results.json)は最終run(2回目)の結果のみを
# 保持するため、raw_usage_log側の先頭1ペア(1回目のtopic_intro生成)だけが対応segmentを
# 持たない「孤立ペア」として残る。これを個別に特定し、Operator-error Wasteとして計上する
# (件数が1件・理由が明確なため、UNKNOWN扱いにはしない)。
KNOWN_OPERATOR_ERROR_DUPLICATES = {
    ("pool_benches", "a2"): {"drop_pair_index": 0, "reason": "JAPANESE_TITLES KeyErrorクラッシュ後の再実行によるtopic_intro二重生成(1回目、破棄)"},
}


def build_full_ledger():
    with open("er006_output/pool_pilot_01/raw_usage_log.jsonl", encoding="utf-8") as f:
        RECORDS = [json.loads(l) for l in f]

    ledger_rows = []
    operator_error_rows = []
    reconciliation = {}

    for theme in THEMES:
        for level_dir, level_key in LEVELS:
            stage = f"tts_{level_key}"
            component_attempts, expected_pairs = build_ledger_for_episode(theme, level_dir, level_key)

            log_idxs = sorted(
                [i for i, r in enumerate(RECORDS) if r["theme"] == theme and r["stage"] == stage],
                key=lambda i: RECORDS[i]["timestamp"],
            )
            gemini_idxs = [i for i in log_idxs if RECORDS[i]["provider"] == "gemini"]
            azure_idxs = [i for i in log_idxs if RECORDS[i]["provider"] == "azure"]

            dup = KNOWN_OPERATOR_ERROR_DUPLICATES.get((theme, level_key))
            if dup is not None:
                di = dup["drop_pair_index"]
                g_rec, az_rec = RECORDS[gemini_idxs[di]], RECORDS[azure_idxs[di]]
                operator_error_rows.append({
                    "theme": theme, "level": level_key, "reason": dup["reason"],
                    "tts_cost_jpy": round(gemini_cost_jpy(g_rec), 3),
                    "asr_cost_jpy": round(azure_cost_jpy(az_rec), 3),
                    "timestamp": g_rec.get("timestamp"),
                })
                del gemini_idxs[di]
                del azure_idxs[di]

            actual_pairs = min(len(gemini_idxs), len(azure_idxs))

            reconciliation[f"{theme}/{level_key}"] = {
                "expected_pairs_from_audit": expected_pairs,
                "actual_pairs_in_log": actual_pairs,
                "gemini_calls": len(gemini_idxs), "azure_calls": len(azure_idxs),
                "MATCH": expected_pairs == actual_pairs,
            }

            if expected_pairs != actual_pairs:
                # 突合不一致: このepisodeはUNKNOWNとして記録し、按分等の推定は行わない
                for comp_name, comp_status, atts in component_attempts:
                    for i, a in enumerate(atts):
                        ledger_rows.append({
                            "theme": theme, "level": level_key, "segment": comp_name,
                            "attempt": a.get("attempt"), "path": a.get("path"),
                            "asr_text": a.get("asr_text"), "verified": a.get("verified"),
                            "duration_seconds": a.get("duration_seconds"),
                            "tts_cost_jpy": "UNKNOWN", "asr_cost_jpy": "UNKNOWN",
                            "reconciliation": "MISMATCH_UNKNOWN_COST",
                        })
                continue

            ptr = 0
            for comp_name, comp_status, atts in component_attempts:
                for a in atts:
                    g_rec = RECORDS[gemini_idxs[ptr]]
                    az_rec = RECORDS[azure_idxs[ptr]]
                    ledger_rows.append({
                        "theme": theme, "level": level_key, "segment": comp_name,
                        "attempt": a.get("attempt"), "path": a.get("path"),
                        "status": a.get("status"), "asr_text": a.get("asr_text"),
                        "asr_text_length": a.get("asr_text_length"), "max_len": a.get("max_len"),
                        "substring_ok": a.get("substring_ok"), "length_ok": a.get("length_ok"),
                        "phonetic_verdict": a.get("phonetic_verdict"),
                        "verified": a.get("verified"),
                        "duration_seconds": a.get("duration_seconds") or g_rec.get("output_audio_seconds_computed_from_pcm"),
                        "tts_model": g_rec.get("model_id"), "tts_input_tokens": g_rec.get("input_tokens"),
                        "tts_output_tokens": g_rec.get("output_tokens"),
                        "tts_cost_jpy": round(gemini_cost_jpy(g_rec), 3),
                        "asr_audio_seconds": az_rec.get("audio_duration_submitted_seconds"),
                        "asr_cost_jpy": round(azure_cost_jpy(az_rec), 3),
                        "segment_final_status": comp_status,
                        "timestamp_tts": g_rec.get("timestamp"), "timestamp_asr": az_rec.get("timestamp"),
                    })
                    ptr += 1

    return ledger_rows, reconciliation, operator_error_rows


if __name__ == "__main__":
    rows, recon, op_err_rows = build_full_ledger()
    print(json.dumps(recon, ensure_ascii=False, indent=2))
    mismatches = [k for k, v in recon.items() if not v["MATCH"]]
    print("MISMATCHES (UNKNOWN扱い):", mismatches)
    print("TOTAL ROWS:", len(rows))
    print("OPERATOR ERROR ROWS:", json.dumps(op_err_rows, ensure_ascii=False, indent=2))
    with open("er006_output/pool_pilot_01/attempt_ledger.json", "w", encoding="utf-8") as f:
        json.dump({"attempts": rows, "operator_error": op_err_rows, "reconciliation": recon}, f, ensure_ascii=False, indent=2)
