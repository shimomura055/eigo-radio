# ============================================================
# er025_phase4_s1_offline_reclassification_01.py
# PRONUNCIATION-RESOLUTION-PHASE-4-A2-FALLBACK-WIRING-AND-ASR-ENTITY-
# LIKE-01 修正1回目(ユーザー判断 2026-09-28、S1)
# ============================================================
# 目的: 既存の実運用telemetry/human_review_queueに蓄積済みの「NG記録」
# (canonical/ASR文字列を保持している行)を、現行コード(Ledger surface
# 条件はOFF=DEFERRED/NOT_ADOPTED、A-1(b)loanword_flagsのみ有効)で
# **read-onlyでオフライン再判定**し、
#   - 母数(再判定対象件数)
#   - entity_like反転件数(記録当時TRUE_CONTENT_MISMATCH -> 現行コードで
#     再判定するとASR_VALIDATION_UNCERTAINへ変わる件数)
#   - そのうち_case_a_entity_pass(CMU辞書ARPAbet完全一致)でPASS化しうる
#     件数
#   - 一般語誤りが隠れる可能性がある件数(ヒューリスティック、下記参照)
# を集計する。
#
# 安全設計(read-only、API呼び出し0、¥0):
#   - 入力ファイル(er021_output/.../telemetry.jsonl、er006_output/.../
#     human_review_queue.jsonl)は**一切書き込まない**(openは"r"のみ)。
#   - 実TTS/ASR/LLM呼び出しは一切行わない(既存記録済みのcanonical/ASR
#     文字列同士をval.classify_asr_match()で再計算するのみ)。
#   - 出力は本ファイル専用の新設ディレクトリ er025_output/
#     phase4_s1_offline_01/ のみ(既存artifactを上書きしない)。
#
# 「一般語誤りが隠れる件数」の定義(ヒューリスティック、保守的な注意
# フラグであり確定判定ではない): 反転した記録のうち、entity_like_source
# が{"loanword"}のみ(={"capitalized"}を含まない、すなわち大文字始まりの
# 裏付けが無く非ASCII文字の有無だけでentity_like判定された)diffを含む
# もの。capitalized_flags由来の救済は「本文中で大文字始まりだった」という
# 従来から使われてきた強い手がかりを伴うが、loanword_flags由来の救済は
# 非ASCII文字の有無のみに依存するため、真に一般語の内容誤り(まれに
# 借用語の綴りを含む一般語、例: café/naïve等)を誤ってentity_like扱いに
# する可能性がcapitalized判定より広い。件数が0でも「発生していない」を
# 意味するだけで「発生しえない」設計上の保証ではない(REPORT §7 Opus
# 申し送り事項1と同種の限定に留意)。
#
# 実行方法:
#   .venv/Scripts/python.exe er025_phase4_s1_offline_reclassification_01.py
from __future__ import annotations

import json
import os

import er006_preprod_hardening_01_validation as val
import er006_secondary_asr_01 as secondary_asr

TELEMETRY_PATH = "er021_output/en_asr_semantic_equivalence_production_wiring_01/telemetry.jsonl"
HUMAN_REVIEW_PATH = "er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl"
OUT_DIR = "er025_output/phase4_s1_offline_01"


def _iter_telemetry_records(path: str):
    """telemetry.jsonlの各行は {canonical, asr, role, classification,
    sub_reason, diff_span, ...} 形式(既存の観測性ログ、role_gate_
    applicableかつshould_pass=Falseの場合のみ追記される)。canonical/asr
    どちらかが欠けている行はスキップする(既存の古い形式混入への
    fail-safe)。"""
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            canonical = rec.get("canonical")
            asr = rec.get("asr")
            old_classification = rec.get("classification")
            if not canonical or asr is None or not old_classification:
                continue
            yield {
                "source_file": path, "source_line": line_no, "source_step": None,
                "canonical": canonical, "asr": asr, "old_classification": old_classification,
            }


def _iter_human_review_records(path: str):
    """human_review_queue.jsonlの各行は{canonical_text, wav_path, steps:[...],
    final_status, ...}形式。steps[*]のうち"text"(ASR書き起こし)と
    "classification"の両方を持つstepを、個別のNG記録として扱う(primary_1/
    primary_2/secondary_1/secondary_2/non_latin_secondary/secondary_forced等、
    いずれもval.classify_asr_match()の結果をそのまま記録したもの)。"""
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            canonical = rec.get("canonical_text")
            if not canonical:
                continue
            for step in rec.get("steps") or []:
                asr = step.get("text")
                old_classification = step.get("classification")
                if asr is None or not old_classification:
                    continue
                yield {
                    "source_file": path, "source_line": line_no, "source_step": step.get("step"),
                    "canonical": canonical, "asr": asr, "old_classification": old_classification,
                }


def reclassify_all() -> dict:
    denominator = 0
    per_source_denominator: dict[str, int] = {}
    flips: list[dict] = []

    for rec in list(_iter_telemetry_records(TELEMETRY_PATH)) + list(_iter_human_review_records(HUMAN_REVIEW_PATH)):
        denominator += 1
        per_source_denominator[rec["source_file"]] = per_source_denominator.get(rec["source_file"], 0) + 1

        new_result = val.classify_asr_match(rec["canonical"], rec["asr"])
        new_classification = new_result.classification

        if rec["old_classification"] == "TRUE_CONTENT_MISMATCH" and new_classification == "ASR_VALIDATION_UNCERTAIN":
            entity_like_sources = val.aggregate_entity_like_sources(new_result.protected.content_word_diffs)
            case_a_pass = secondary_asr._case_a_entity_pass(new_result)
            loanword_only = entity_like_sources == ["loanword"]
            flips.append({
                "source_file": rec["source_file"], "source_line": rec["source_line"],
                "source_step": rec["source_step"],
                "canonical": rec["canonical"], "asr": rec["asr"],
                "old_classification": rec["old_classification"], "new_classification": new_classification,
                "entity_like_source": entity_like_sources,
                "case_a_entity_pass": case_a_pass,
                "loanword_only_flip_candidate": loanword_only,
                "content_word_diffs": new_result.protected.content_word_diffs,
            })

    case_a_pass_count = sum(1 for f in flips if f["case_a_entity_pass"])
    loanword_only_count = sum(1 for f in flips if f["loanword_only_flip_candidate"])

    summary = {
        "management_id": "PRONUNCIATION-RESOLUTION-PHASE-4-A2-FALLBACK-WIRING-AND-ASR-ENTITY-LIKE-01",
        "phase": "S1(修正1回目、read-only offline reclassification)",
        "ledger_entity_flags_enabled_for_classification": val.LEDGER_ENTITY_FLAGS_ENABLED_FOR_CLASSIFICATION,
        "input_files": [TELEMETRY_PATH, HUMAN_REVIEW_PATH],
        "denominator_total": denominator,
        "denominator_by_source_file": per_source_denominator,
        "entity_like_flip_count_true_content_mismatch_to_uncertain": len(flips),
        "of_which_case_a_entity_pass_could_auto_pass": case_a_pass_count,
        "of_which_loanword_only_flip_candidate_hidden_general_word_risk": loanword_only_count,
        "methodology_note": (
            "現行コード(classify_asr_match、Ledger surface条件OFF)で、"
            "canonical/ASR文字列を保持している既存NG記録を再判定した。"
            "実TTS/ASR呼び出しは一切行っていない(記録済み文字列の再比較のみ)。"
            "「一般語誤りが隠れる件数」はloanword_flagsのみを根拠とする反転の"
            "件数であり、保守的な注意フラグ(確定判定ではない)。"),
    }
    return {"summary": summary, "flips": flips}


def run() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    result = reclassify_all()
    with open(os.path.join(OUT_DIR, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(result["summary"], f, ensure_ascii=False, indent=2, default=str)
    with open(os.path.join(OUT_DIR, "flips_detail.jsonl"), "w", encoding="utf-8") as f:
        for flip in result["flips"]:
            f.write(json.dumps(flip, ensure_ascii=False, default=str) + "\n")
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    run()
