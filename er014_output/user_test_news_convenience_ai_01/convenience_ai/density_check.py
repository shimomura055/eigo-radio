# ============================================================
# er014_output/user_test_news_convenience_ai_01/convenience_ai/density_check.py
# 管理ID: USER-TEST-NEWS-CONVENIENCE-AI-01
#
# read-only情報密度チェック(委任文「編集判断の実装手段(c)」)。
# 新Gate・新Validatorではない。既存 er003_v1_n3_01_articles_generate.
# compute_metrics() をそのまま使い、追加で数字出現数・避けるべき難語・
# 論点数(見出し###の数、既存構成上は常に2)を数えるだけの補助スクリプト。
# 判定結果はGateとして記事完成をブロックしない(報告用)。
# ============================================================
from __future__ import annotations
import json
import re
import sys

sys.path.insert(0, ".")
import er003_v1_n3_01_articles_generate as prod_gen

AVOID_WORDS = [
    "product development process", "consumer behavior", "predictive analytics",
    "optimization", "generative model", "market segmentation", "algorithm",
    "machine learning", "artificial intelligence model", "neural network",
    "digital transformation", "data-driven", "leverage", "utilize",
]

NUMBER_RE = re.compile(r"\b\d[\d,.]*\b")


def check(article_path: str, level: str) -> dict:
    text = open(article_path, encoding="utf-8").read()
    flat = " ".join(line.strip() for line in text.splitlines()
                     if line.strip() and not line.strip().startswith("#"))
    metrics = prod_gen.compute_metrics(text)
    numbers = NUMBER_RE.findall(flat)
    lower = flat.lower()
    avoided_hits = [w for w in AVOID_WORDS if w in lower]
    point_count = len(re.findall(r"^###\s", text, flags=re.MULTILINE))
    avg_limit = 11 if level == "a2" else 15
    max_limit = 18 if level == "a2" else 24
    return {
        "level": level,
        "word_count": metrics["word_count"],
        "sentence_count": metrics["sentence_count"],
        "avg_sentence_length": metrics["avg_sentence_length"],
        "max_sentence_length": metrics["max_sentence_length"],
        "avg_limit_diagnostic": avg_limit,
        "max_limit_diagnostic": max_limit,
        "avg_within_limit": metrics["avg_sentence_length"] <= avg_limit,
        "max_within_limit": metrics["max_sentence_length"] <= max_limit,
        "number_occurrences": len(numbers),
        "numbers_found": numbers,
        "avoided_word_hits": avoided_hits,
        "point_heading_count": point_count,
    }


if __name__ == "__main__":
    base = "er014_output/user_test_news_convenience_ai_01/convenience_ai"
    out = {}
    for level, sub in (("a2", "a2"), ("b1", "b1b")):
        r = check(f"{base}/{sub}/article.md", level)
        out[level] = r
        print(f"[{level}] word_count={r['word_count']} avg={r['avg_sentence_length']}"
              f"(limit{r['avg_limit_diagnostic']}) max={r['max_sentence_length']}"
              f"(limit{r['max_limit_diagnostic']}) numbers={r['number_occurrences']} "
              f"avoided_words={r['avoided_word_hits']} points={r['point_heading_count']}")
    with open(f"{base}/audit/density_check_result.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
