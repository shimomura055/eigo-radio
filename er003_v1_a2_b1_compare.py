# ============================================================
# er003_v1_a2_b1_compare.py
# ER-003-A2-01/A2-02: A2テキストとB1確定テキストの指標比較
# ============================================================
# 既存のB1本文(er003_output/b1_p1/{topic}/b1_article_raw.md)と、
# A2-01(er003_output/a2_p1/{topic}/a2_article_raw.md)、
# A2-02(er003_output/a2_p1_r2/{topic}/a2_article_raw.md)を同一の計測方法
# (語数・文数・文長・セクション別語数・ヒューリスティックQA)で比較する。
# 新規のTTS・音声処理は一切行わない。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_a2_b1_compare.py

from __future__ import annotations

import json

import er003_a2_article as a2
import er003_b1_article as b1

TOPIC_IDS = ("A01", "A02", "ADD03")


def _load(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def compare_topic(topic_id: str) -> dict:
    b1_text = _load(f"er003_output/b1_p1/{topic_id}/b1_article_raw.md")
    a2r1_text = _load(f"er003_output/a2_p1/{topic_id}/a2_article_raw.md")
    a2r2_text = _load(f"er003_output/a2_p1_r2/{topic_id}/a2_article_raw.md")

    b1_metrics = b1.compute_b1_sentence_metrics(b1_text)
    b1_a2view = a2.compute_a2_sentence_metrics(b1_text)
    a2r1_metrics = a2.compute_a2_sentence_metrics(a2r1_text)
    a2r2_metrics = a2.compute_a2_sentence_metrics(a2r2_text)

    b1_sections = a2.compute_section_word_counts(b1_text)
    a2r1_sections = a2.compute_section_word_counts(a2r1_text)
    a2r2_sections = a2.compute_section_word_counts(a2r2_text)

    def summarize(label, text, metrics, sections):
        return {
            "label": label,
            "total_word_count_body_only": metrics["total_word_count_body_only"],
            "total_sentence_count": metrics["total_sentence_count"],
            "avg_words_per_sentence": metrics["avg_words_per_sentence"],
            "longest_sentence_word_count": metrics["longest_sentence_word_count"],
            "sentences_over_18_word_count": metrics.get(
                "sentences_over_18_word_count", b1_a2view["sentences_over_18_word_count"]),
            "full_story_word_count": sections["full_story_word_count"],
            "points_word_count": sections["points_word_count"],
            "in_one_line_word_count": sections["in_one_line_word_count"],
            "full_story_to_points_ratio": sections["full_story_to_points_ratio"],
            "full_story_share_of_total": sections["full_story_share_of_total"],
        }

    return {
        "topic_id": topic_id,
        "b1": summarize("B1", b1_text, b1_a2view, b1_sections) | {
            "avg_words_per_sentence": b1_metrics["avg_words_per_sentence"],
            "longest_sentence_word_count": b1_metrics["longest_sentence_word_count"],
        },
        "a2_r1": summarize("A2-01", a2r1_text, a2r1_metrics, a2r1_sections),
        "a2_r2": summarize("A2-02", a2r2_text, a2r2_metrics, a2r2_sections),
    }


def run_all() -> dict:
    results = {}
    for topic_id in TOPIC_IDS:
        results[topic_id] = compare_topic(topic_id)
    with open("er003_output/a2_p1_r2/b1_vs_a2r1_vs_a2r2_comparison.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    return results


if __name__ == "__main__":
    r = run_all()
    for topic_id, d in r.items():
        print(f"--- {topic_id} ---")
        for key in ("b1", "a2_r1", "a2_r2"):
            v = d[key]
            print(f"  {v['label']}: words={v['total_word_count_body_only']} "
                  f"avg={v['avg_words_per_sentence']} longest={v['longest_sentence_word_count']} "
                  f"FS={v['full_story_word_count']} Pts={v['points_word_count']} "
                  f"FS_share={v['full_story_share_of_total']}")
    print("done.")
