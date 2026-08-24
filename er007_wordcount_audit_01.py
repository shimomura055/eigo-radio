# ============================================================
# er007_wordcount_audit_01.py
# ER-007-EVIDENCE-WORDCOUNT-JA-ASR-EFFECTIVENESS-AUDIT-01 Part A:
# No.4-6 B版(Evidence Compression)の語数を、Production Writerが
# 実際に使っている計測関数(ab01.compute_word_count / gen.compute_metrics)
# でそのまま再計測する。新しい計測方法は作らない。
# ============================================================
import json
import sys

sys.path.insert(0, ".")
import er003_v1_en_direct_ab_01_generate as ab01
import er003_v1_n3_01_articles_generate as gen
from er007_evidence_density_ab_01_scripts import B_SCRIPTS
from er007_evidence_density_ab_01_factcheck import build_b_article_text, THEME_CONFIG

# Production Writerの実測diagnostic定数(er003_v1_n3_01_articles_generate.py)
POINT_TARGET_LOWER = gen.POINT_TARGET_LOWER
POINT_TARGET_UPPER = gen.POINT_TARGET_UPPER
POINT_TOLERANCE_LOWER = gen.POINT_TOLERANCE_LOWER
POINT_TOLERANCE_UPPER = gen.POINT_TOLERANCE_UPPER
TOTAL_SOFT_LOWER = gen.TOTAL_SOFT_LOWER
TOTAL_SOFT_UPPER = gen.TOTAL_SOFT_UPPER


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def verdict(value, lower, upper):
    if value < lower:
        return "BELOW"
    if value > upper:
        return "ABOVE"
    return "PASS"


def audit_topic_level(short_key, level_dir):
    cfg = THEME_CONFIG[short_key]
    out_dir = cfg["out_dir"]
    parts = load_json(f"{out_dir}/{level_dir}/parts.json")
    overrides = B_SCRIPTS[short_key][level_dir]

    a_article_text = open(f"{out_dir}/{level_dir}/article.md", encoding="utf-8").read()
    b_article_text = build_b_article_text(parts, overrides)

    a_total = gen.compute_metrics(a_article_text)["word_count"]
    b_total = gen.compute_metrics(b_article_text)["word_count"]

    p1_body_a = parts["point_one_body"]
    p2_body_a = parts["point_two_body"]
    p1_body_b = overrides.get("point_one_body") or p1_body_a
    p2_body_b = overrides.get("point_two_body") or p2_body_a

    a_p1 = ab01.compute_word_count(p1_body_a)
    a_p2 = ab01.compute_word_count(p2_body_a)
    b_p1 = ab01.compute_word_count(p1_body_b)
    b_p2 = ab01.compute_word_count(p2_body_b)

    return {
        "topic": short_key, "level": level_dir,
        "total": {"A": a_total, "B": b_total,
                  "target_range": [TOTAL_SOFT_LOWER, TOTAL_SOFT_UPPER],
                  "verdict_B": verdict(b_total, TOTAL_SOFT_LOWER, TOTAL_SOFT_UPPER),
                  "verdict_A": verdict(a_total, TOTAL_SOFT_LOWER, TOTAL_SOFT_UPPER)},
        "point_one": {"A": a_p1, "B": b_p1,
                      "target_range": [POINT_TARGET_LOWER, POINT_TARGET_UPPER],
                      "tolerance_range": [POINT_TOLERANCE_LOWER, POINT_TOLERANCE_UPPER],
                      "verdict_B_target": verdict(b_p1, POINT_TARGET_LOWER, POINT_TARGET_UPPER),
                      "verdict_B_tolerance": verdict(b_p1, POINT_TOLERANCE_LOWER, POINT_TOLERANCE_UPPER)},
        "point_two": {"A": a_p2, "B": b_p2,
                      "target_range": [POINT_TARGET_LOWER, POINT_TARGET_UPPER],
                      "tolerance_range": [POINT_TOLERANCE_LOWER, POINT_TOLERANCE_UPPER],
                      "verdict_B_target": verdict(b_p2, POINT_TARGET_LOWER, POINT_TARGET_UPPER),
                      "verdict_B_tolerance": verdict(b_p2, POINT_TOLERANCE_LOWER, POINT_TOLERANCE_UPPER)},
    }


if __name__ == "__main__":
    results = []
    for short_key in THEME_CONFIG:
        for level_dir in ("b1b", "a2"):
            r = audit_topic_level(short_key, level_dir)
            results.append(r)
            print(f"=== {short_key} / {level_dir} ===")
            print(f"  TOTAL: A={r['total']['A']} B={r['total']['B']} "
                  f"target=[{TOTAL_SOFT_LOWER},{TOTAL_SOFT_UPPER}] "
                  f"verdict_B={r['total']['verdict_B']} (verdict_A={r['total']['verdict_A']})")
            print(f"  POINT_ONE: A={r['point_one']['A']} B={r['point_one']['B']} "
                  f"target=[{POINT_TARGET_LOWER},{POINT_TARGET_UPPER}] tol=[{POINT_TOLERANCE_LOWER},{POINT_TOLERANCE_UPPER}] "
                  f"verdict_B_target={r['point_one']['verdict_B_target']} verdict_B_tolerance={r['point_one']['verdict_B_tolerance']}")
            print(f"  POINT_TWO: A={r['point_two']['A']} B={r['point_two']['B']} "
                  f"target=[{POINT_TARGET_LOWER},{POINT_TARGET_UPPER}] tol=[{POINT_TOLERANCE_LOWER},{POINT_TOLERANCE_UPPER}] "
                  f"verdict_B_target={r['point_two']['verdict_B_target']} verdict_B_tolerance={r['point_two']['verdict_B_tolerance']}")
    with open("er006_output/pool_pilot_01/evidence_density_ab_01/wordcount_audit.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("WORDCOUNT_AUDIT_DONE")
