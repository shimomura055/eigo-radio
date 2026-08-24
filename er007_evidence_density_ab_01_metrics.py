# ============================================================
# er007_evidence_density_ab_01_metrics.py
# ER-007-SPOKEN-EVIDENCE-DENSITY-AB-01 Part A-10: A/B定量比較
# (spoken word count / 数字出現数 / 年号出現数 / 固有名詞数 /
#  research attribution表現数)。「短ければ良い」ではなく、Evidence
# Densityがどの程度下がったかを見るための補助指標。
# ============================================================
from __future__ import annotations

import json
import re

from er007_evidence_density_ab_01_scripts import B_SCRIPTS

THEME_CONFIG = {
    "n4_supermarket": "er006_output/pool_pilot_01/pool_n4_supermarket",
    "n5_cafes": "er006_output/pool_pilot_01/pool_n5_cafes",
    "n6_delivery": "er006_output/pool_pilot_01/pool_n6_delivery",
}

SEGMENTS = ("part1", "part2", "point_one_body", "point_two_body")

_YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")
_NUMBER_RE = re.compile(r"\b\d[\d,.]*\b|\b(?:one|two|three|four|five|six|seven|eight|nine|ten|"
                         r"eleven|twelve|dozens?|hundred|thousand|percent)\b", re.IGNORECASE)
_ATTRIBUTION_RE = re.compile(
    r"\b(study|studies|research(?:ers)?|report(?:ed)?|survey|paper|review|"
    r"published|journal|according to|source)\b", re.IGNORECASE)
_PROPER_NOUN_RE = re.compile(r"\b[A-Z][a-zA-Z']+\b")
_STOPWORD_CAPS = {"The", "A", "An", "In", "But", "So", "This", "It", "They", "When", "After",
                   "At", "There", "Some", "Its", "For", "On", "That", "Two", "Three", "Four",
                   "Twenty", "London", "England", "UK", "Berlin"}  # 地名は別途手動集計、除外


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def word_count(text: str) -> int:
    return len(re.findall(r"\S+", text))


def count_metrics(text: str) -> dict:
    return {
        "word_count": word_count(text),
        "numbers": len(_NUMBER_RE.findall(text)),
        "years": len(_YEAR_RE.findall(text)),
        "attribution_phrases": len(_ATTRIBUTION_RE.findall(text)),
        "capitalized_proper_noun_candidates": len(
            [w for w in _PROPER_NOUN_RE.findall(text) if w not in _STOPWORD_CAPS]),
    }


def compare_segment(short_key: str, level_dir: str, seg_name: str, original: str, override: str | None) -> dict:
    b_text = override or original
    a_m = count_metrics(original)
    b_m = count_metrics(b_text)
    changed = override is not None
    return {"segment": seg_name, "changed": changed, "A": a_m, "B": b_m}


def run(short_key: str) -> dict:
    out_dir = THEME_CONFIG[short_key]
    results = {}
    for level_dir in ("b1b", "a2"):
        parts = load_json(f"{out_dir}/{level_dir}/parts.json")
        overrides = B_SCRIPTS[short_key][level_dir]
        seg_results = []
        for seg_name, key in (("part1", "part1"), ("part2", "part2"),
                               ("point_one_body", "point_one_body"), ("point_two_body", "point_two_body")):
            seg_results.append(compare_segment(short_key, level_dir, seg_name, parts[key], overrides.get(key)))
        totals_a = {k: sum(s["A"][k] for s in seg_results) for k in seg_results[0]["A"]}
        totals_b = {k: sum(s["B"][k] for s in seg_results) for k in seg_results[0]["B"]}
        results[level_dir] = {"segments": seg_results, "totals_A": totals_a, "totals_B": totals_b}
    return results


if __name__ == "__main__":
    all_results = {}
    for short_key in THEME_CONFIG:
        r = run(short_key)
        all_results[short_key] = r
        print(f"=== {short_key} ===")
        for level_dir, d in r.items():
            ta, tb = d["totals_A"], d["totals_B"]
            print(f"  {level_dir}: word_count A={ta['word_count']} B={tb['word_count']} "
                  f"({tb['word_count']-ta['word_count']:+d}, {100*(tb['word_count']-ta['word_count'])/ta['word_count']:.1f}%)")
            print(f"           numbers A={ta['numbers']} B={tb['numbers']} "
                  f"years A={ta['years']} B={tb['years']} "
                  f"attribution A={ta['attribution_phrases']} B={tb['attribution_phrases']} "
                  f"proper_noun_candidates A={ta['capitalized_proper_noun_candidates']} B={tb['capitalized_proper_noun_candidates']}")
    with open("er006_output/pool_pilot_01/evidence_density_ab_01/ab_quantitative_metrics.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print("METRICS_DONE")
