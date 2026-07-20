# ============================================================
# er003_v1_p2a_finalize.py
# ER-003-P2A: 再計測結果を正式記録として確定する(API呼び出しなし)
# ============================================================
# sentence_metrics_recalculated.json (ER-003-P2Aで文分割ロジックを修正して
# 再計測した正式指標)を、各記事のrun_summary.jsonおよび
# natural_source_vs_b2_metrics.jsonのsentence_metrics欄に反映する。
#
# 旧sentence_metrics.json自体は監査記録としてそのまま残し、上書きしない。
# 代わりにP2A_metrics_supersession_manifest.jsonへ、どの値がどの理由で
# supersededになったかを記録する。
#
# B2本文(b2_version_raw.md等)、Natural English Sourceは一切変更しない。
# APIは一切呼ばない。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_p2a_finalize.py

from __future__ import annotations

import json
import os

P2_OUTPUT_ROOT = "er003_output/p2"
TOPIC_IDS = ("A01", "A02", "ADD03")

SUPERSESSION_REASON = (
    "ER-003-P2A: split_sentences()が段落境界(空行)とカーリークォートを"
    "正しく扱えず、実在しない長文(A02=59語, ADD03=37語)を計測していた。"
    "段落認識型のsentence splitterへ修正し、保存済みB2本文をAPI再実行なし"
    "で再計測した。B2本文自体は無変更(sha256で確認済み)。"
)


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def finalize_run_summary(topic_id: str) -> dict:
    out_dir = os.path.join(P2_OUTPUT_ROOT, topic_id)
    run_summary_path = os.path.join(P2_OUTPUT_ROOT, f"{topic_id}_run_summary.json")
    run_summary = load_json(run_summary_path)

    pre_p2a_metrics = run_summary["sentence_metrics"]
    recalculated_metrics = load_json(os.path.join(out_dir, "sentence_metrics_recalculated.json"))

    run_summary["sentence_metrics"] = recalculated_metrics
    run_summary["sentence_metrics_pre_p2a_superseded"] = pre_p2a_metrics
    run_summary["sentence_metrics_correction"] = {
        "corrected_by": "ER-003-P2A",
        "reason": SUPERSESSION_REASON,
        "official_metrics_source": "sentence_metrics_recalculated.json",
        "superseded_metrics_source": "sentence_metrics.json (audit record, unmodified)",
    }
    save_json(run_summary_path, run_summary)
    return {
        "topic_id": topic_id,
        "pre_p2a_overall_status": pre_p2a_metrics["overall_status"],
        "official_overall_status": recalculated_metrics["overall_status"],
    }


def finalize_natural_source_vs_b2_metrics() -> None:
    path = os.path.join(P2_OUTPUT_ROOT, "natural_source_vs_b2_metrics.json")
    combined = load_json(path)
    for topic_id in TOPIC_IDS:
        recalculated = load_json(
            os.path.join(P2_OUTPUT_ROOT, topic_id, "sentence_metrics_recalculated.json")
        )
        b2_entry = combined[topic_id]["b2"]
        b2_entry["pre_p2a_superseded"] = {
            "avg_words_per_sentence": b2_entry["avg_words_per_sentence"],
            "longest_sentence_word_count": b2_entry["longest_sentence_word_count"],
            "sentences_over_32_word_count": b2_entry["sentences_over_32_word_count"],
            "sentence_metrics_status": b2_entry["sentence_metrics_status"],
        }
        b2_entry["avg_words_per_sentence"] = recalculated["avg_words_per_sentence"]
        b2_entry["longest_sentence_word_count"] = recalculated["longest_sentence_word_count"]
        b2_entry["sentences_over_32_word_count"] = recalculated["sentences_over_32_word_count"]
        b2_entry["sentence_metrics_status"] = recalculated["overall_status"]
    save_json(path, combined)


def build_supersession_manifest(results: list) -> None:
    manifest = {
        "corrected_by": "ER-003-P2A",
        "reason": SUPERSESSION_REASON,
        "splitter_fix_commit": "b9d701a",
        "api_calls_made": 0,
        "b2_body_text_modified": False,
        "natural_english_source_modified": False,
        "official_metrics_field": "sentence_metrics_recalculated.json (per-article) / sentence_metrics (in *_run_summary.json, post-P2A)",
        "superseded_metrics_field": "sentence_metrics.json (per-article, kept unmodified as audit record) / sentence_metrics_pre_p2a_superseded (in *_run_summary.json)",
        "per_article_verdict_change": results,
    }
    save_json(os.path.join(P2_OUTPUT_ROOT, "P2A_metrics_supersession_manifest.json"), manifest)


if __name__ == "__main__":
    results = [finalize_run_summary(topic_id) for topic_id in TOPIC_IDS]
    finalize_natural_source_vs_b2_metrics()
    build_supersession_manifest(results)
    print("done. P2 final verdicts corrected via P2A recalculated metrics.")
