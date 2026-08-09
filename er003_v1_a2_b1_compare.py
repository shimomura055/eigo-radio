# ============================================================
# er003_v1_a2_b1_compare.py
# ER-003-A2-01: A2暫定テキストとB1確定テキストの指標比較
# ============================================================
# 既存のB1本文(er003_output/b1_p1/{topic}/b1_article_raw.md)と、
# 今回生成したA2暫定本文(er003_output/a2_p1/{topic}/a2_article_raw.md)
# を同一の計測方法(語数・文数・文長・ヒューリスティックQA)で比較する。
# 新規のTTS・音声処理は一切行わない。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_a2_b1_compare.py

from __future__ import annotations

import json

import er003_a2_article as a2
import er003_b1_article as b1

TOPIC_IDS = ("A01", "A02", "ADD03")


def compare_topic(topic_id: str) -> dict:
    with open(f"er003_output/b1_p1/{topic_id}/b1_article_raw.md", encoding="utf-8") as f:
        b1_text = f.read()
    with open(f"er003_output/a2_p1/{topic_id}/a2_article_raw.md", encoding="utf-8") as f:
        a2_text = f.read()

    b1_metrics = b1.compute_b1_sentence_metrics(b1_text)
    # B1本文にもA2用の文分割関数を適用し、「18語超過」件数だけを
    # B1/A2で同一の閾値・同一の分割ロジックで比較できるようにする
    # (avg/longestはB1側の値をそのまま使う。閾値に依存しない記述統計のため)。
    b1_sentence_level_a2_view = a2.compute_a2_sentence_metrics(b1_text)
    a2_metrics = a2.compute_a2_sentence_metrics(a2_text)

    # B1側にもA2と同じヒューリスティックQAを適用し、フェアな比較にする
    b1_heuristics = a2.compute_a2_grammar_vocab_heuristics(b1_text)
    a2_heuristics = a2.compute_a2_grammar_vocab_heuristics(a2_text)

    return {
        "topic_id": topic_id,
        "b1": {
            "total_word_count_body_only": b1_metrics["total_word_count_body_only"],
            "total_sentence_count": b1_metrics["total_sentence_count"],
            "avg_words_per_sentence": b1_metrics["avg_words_per_sentence"],
            "longest_sentence_word_count": b1_metrics["longest_sentence_word_count"],
            "sentences_over_18_word_count": b1_sentence_level_a2_view["sentences_over_18_word_count"],
        },
        "a2": {
            "total_word_count_body_only": a2_metrics["total_word_count_body_only"],
            "total_sentence_count": a2_metrics["total_sentence_count"],
            "avg_words_per_sentence": a2_metrics["avg_words_per_sentence"],
            "longest_sentence_word_count": a2_metrics["longest_sentence_word_count"],
            "sentences_over_18_word_count": a2_metrics["sentences_over_18_word_count"],
        },
        "b1_heuristics": b1_heuristics,
        "a2_heuristics": a2_heuristics,
        "b1_sentence_word_counts": b1_sentence_level_a2_view.get("sentence_word_counts"),
        "a2_sentence_word_counts": a2_metrics.get("sentence_word_counts"),
        "b1_sentences": b1_sentence_level_a2_view.get("sentences"),
        "a2_sentences": a2_metrics.get("sentences"),
    }


def run_all() -> dict:
    results = {}
    for topic_id in TOPIC_IDS:
        results[topic_id] = compare_topic(topic_id)
    with open("er003_output/a2_p1/b1_vs_a2_comparison.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    return results


if __name__ == "__main__":
    r = run_all()
    for topic_id, d in r.items():
        print(f"--- {topic_id} ---")
        print(f"  B1: words={d['b1']['total_word_count_body_only']} sentences={d['b1']['total_sentence_count']} "
              f"avg={d['b1']['avg_words_per_sentence']} longest={d['b1']['longest_sentence_word_count']}")
        print(f"  A2: words={d['a2']['total_word_count_body_only']} sentences={d['a2']['total_sentence_count']} "
              f"avg={d['a2']['avg_words_per_sentence']} longest={d['a2']['longest_sentence_word_count']} "
              f"over18={d['a2']['sentences_over_18_word_count']}")
    print("done.")
