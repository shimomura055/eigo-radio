# ============================================================
# er003_v1_p2a_recalculate.py
# ER-003-P2A: 保存済みB2本文の再計測(API呼び出しなし)
# ============================================================
# ER-003-P2で保存済みのB2本文3記事を、修正後のsplit_sentences/
# compute_b2_sentence_metricsで再計測する。本文は一切変更しない。
# APIは一切呼ばない。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_p2a_recalculate.py

from __future__ import annotations

import json
import os

import er003_b2_adapter as b2
import er003_ja_to_en_translation as er003

P2_OUTPUT_ROOT = "er003_output/p2"

# ER-003-P2で実際に記録された修正前の指標(このスクリプト自身では
# 再現しない。比較レビュー作成のためだけに記録として保持する)。
PRE_FIX_METRICS = {
    "A01": {"total_sentence_count": 26, "avg_words_per_sentence": 11.46, "longest_sentence_word_count": 24,
            "sentences_over_32_word_count": 0, "overall_status": "B2_SENTENCE_METRICS_PASS"},
    "A02": {"total_sentence_count": 30, "avg_words_per_sentence": 13.2, "longest_sentence_word_count": 59,
            "sentences_over_32_word_count": 2, "overall_status": "B2_SENTENCE_METRICS_FAIL"},
    "ADD03": {"total_sentence_count": 31, "avg_words_per_sentence": 12.55, "longest_sentence_word_count": 37,
              "sentences_over_32_word_count": 2, "overall_status": "B2_SENTENCE_METRICS_FAIL"},
}


def recalculate_article(topic_id: str) -> dict:
    article_path = os.path.join(P2_OUTPUT_ROOT, topic_id, "b2_version_raw.md")
    with open(article_path, encoding="utf-8") as f:
        raw_text = f.read()
    source_sha256 = er003.sha256_text(raw_text)

    body_only_raw = b2.strip_heading_lines(raw_text)
    plain_body_only = er003.article_gen.strip_markdown_symbols(body_only_raw)
    sentences = er003.split_sentences(plain_body_only)

    segments = []
    paragraph_index = 0
    for paragraph in er003.split_into_paragraphs(plain_body_only):
        paragraph_index += 1
        for sentence in (er003.split_paragraph_into_sentences(paragraph) or [paragraph]):
            segments.append({
                "index": len(segments) + 1,
                "paragraph_index": paragraph_index,
                "text": sentence,
                "word_count": er003.compute_word_count(sentence),
                "over_32_words": er003.compute_word_count(sentence) > 32,
            })

    metrics = b2.compute_b2_sentence_metrics(raw_text)

    sentence_segments = {
        "article_id": topic_id,
        "source_sha256": source_sha256,
        "sentences": segments,
        "sentence_count": len(segments),
        "average_sentence_words": metrics["avg_words_per_sentence"],
        "max_sentence_words": metrics["longest_sentence_word_count"],
        "over_32_count": metrics["sentences_over_32_word_count"],
        "gate": "PASS" if metrics["overall_status"] == "B2_SENTENCE_METRICS_PASS" else "FAIL",
    }

    out_dir = os.path.join(P2_OUTPUT_ROOT, topic_id)
    with open(os.path.join(out_dir, "sentence_segments.json"), "w", encoding="utf-8") as f:
        json.dump(sentence_segments, f, ensure_ascii=False, indent=2)

    md_lines = [f"# {topic_id} sentence segments (recalculated)", "", f"source_sha256: `{source_sha256}`", ""]
    for seg in segments:
        marker = " **[OVER 32 WORDS]**" if seg["over_32_words"] else ""
        md_lines.append(f"{seg['index']}. ({seg['word_count']}w){marker} {seg['text']}")
    md_lines.append("")
    with open(os.path.join(out_dir, "sentence_segments.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    with open(os.path.join(out_dir, "sentence_metrics_recalculated.json"), "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

    return {
        "topic_id": topic_id, "source_sha256": source_sha256,
        "pre_fix": PRE_FIX_METRICS[topic_id],
        "post_fix": {
            "total_sentence_count": metrics["total_sentence_count"],
            "avg_words_per_sentence": metrics["avg_words_per_sentence"],
            "longest_sentence_word_count": metrics["longest_sentence_word_count"],
            "sentences_over_32_word_count": metrics["sentences_over_32_word_count"],
            "overall_status": metrics["overall_status"],
        },
        "over_32_sentences_after_fix": [s for s in segments if s["over_32_words"]],
    }


def build_comparison_review(results: dict) -> str:
    lines = [
        "# ER-002-v1.2M-JA / ER-003-P2 sentence metrics review (ER-003-P2A)",
        "",
        "B2文長計測ロジックの根本原因修正前後の比較。APIは一切呼んでいない。B2本文は一切変更していない。",
        "",
    ]
    for topic_id, r in results.items():
        lines.append(f"## {topic_id}")
        lines.append("")
        lines.append(f"- 入力sha256: `{r['source_sha256']}`(P2実行時と不変)")
        lines.append("")
        lines.append("| 指標 | 修正前 | 修正後 |")
        lines.append("|---|---|---|")
        lines.append(f"| 文数 | {r['pre_fix']['total_sentence_count']} | {r['post_fix']['total_sentence_count']} |")
        lines.append(f"| 平均文長 | {r['pre_fix']['avg_words_per_sentence']} | {r['post_fix']['avg_words_per_sentence']} |")
        lines.append(f"| 最長文 | {r['pre_fix']['longest_sentence_word_count']} | {r['post_fix']['longest_sentence_word_count']} |")
        lines.append(f"| 32語超の文数 | {r['pre_fix']['sentences_over_32_word_count']} | {r['post_fix']['sentences_over_32_word_count']} |")
        lines.append(f"| B2_SENTENCE_METRICS判定 | {r['pre_fix']['overall_status']} | {r['post_fix']['overall_status']} |")
        lines.append("")
        if r["over_32_sentences_after_fix"]:
            lines.append("### 修正後も32語を超える文")
            for s in r["over_32_sentences_after_fix"]:
                lines.append(f"- ({s['word_count']}w) {s['text']}")
        else:
            lines.append("修正後、32語を超える文は存在しない。")
        lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    all_results = {}
    for topic_id in ["A01", "A02", "ADD03"]:
        all_results[topic_id] = recalculate_article(topic_id)

    review_md = build_comparison_review(all_results)
    with open(os.path.join(P2_OUTPUT_ROOT, "ER-003-P2_sentence_metrics_review.md"), "w", encoding="utf-8") as f:
        f.write(review_md)

    with open(os.path.join(P2_OUTPUT_ROOT, "sentence_metrics_recalculation_summary.json"), "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    print("done. recalculation complete for A01, A02, ADD03.")
