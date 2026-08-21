# ============================================================
# er006_preprod_hardening_01_validation_test.py
# ER-006-POOL-PREPROD-HARDENING-01: Regression fixture
# ============================================================
# Positive fixture: ER-006-POOL-PILOT-COST-ROOTFIX-01で実際に観測した9件の
# STOPPED segment(の代表的attempt)。いずれも不要retryを起こさないこと
# (should_pass=True または should_retry=False)を確認する。
# Negative fixture: 人工的に作った内容誤り。全てshould_pass=Falseかつ
# classification="TRUE_CONTENT_MISMATCH"(=retry対象のまま)であることを
# 確認する。
from __future__ import annotations

from er006_preprod_hardening_01_validation import classify_asr_match

POSITIVE_FIXTURES = [
    {
        "name": "Malmö/Malmo + Triangeln/Triangle + ordinal + dash (benches/b1/point_two)",
        "canonical": "Malmö’s Triangeln station opened in December 2010, and a formal complaint about its tilted bench was reported on March 4, 2011. Yet officials said it was steeper than ordered and later corrected. In 2021, an NYC Transit post linked bench removals to homeless people sleeping. It was deleted, and the MTA called it an error—not a confirmed policy.",
        "asr": "Malmo's Triangle station opened in December 2010, and a formal complaint about its tilted bench was reported on March 4th, 2011. Yet officials said it was steeper than ordered and later corrected. In 2021, an NYC Transit post linked bench removals to homeless people sleeping. It was deleted and the MTA called it an error, not a confirmed policy.",
    },
    {
        "name": "hyphen (benches/b1/kp2 wide-scale empirical study)",
        "canonical": "a wide-scale empirical study",
        "asr": "Wide-scale empirical study.",
    },
    {
        "name": "hyphen no-change (benches/b1/kp2, dehyphenated variant)",
        "canonical": "a wide-scale empirical study",
        "asr": "Widescale empirical study.",
    },
    {
        "name": "cancelling/canceling (subscriptions/b1/comment_2)",
        "canonical": "Part 1 showed that cancelling a subscription can involve extra steps, a kind of friction called sludge. Now, listen for how US regulators tried to address this problem, and what later happened to their rule.",
        "asr": "Part 1 showed that canceling a subscription can involve extra steps, a kind of friction called sludge. Now listen for how US regulators tried to address this problem and what later happened to their rule.",
    },
    {
        "name": "Click-to-Cancel/Click to cancel hyphen (subscriptions/a2/full_story_part2, excerpt)",
        "canonical": "On October 16, 2024, it finalized its Click-to-Cancel rule.",
        "asr": "On October 16, 2024, it finalized its Click to cancel rule.",
    },
    {
        "name": "blitzscaling compound word boundary (startups kp3)",
        "canonical": "blitzscaling",
        "asr": "Blitz scaling.",
    },
]

# "St." abbreviation artifact(street→St.、ASRの表記揺れ)は、canonical側の
# "street"が固有名詞ではない(小文字・一般名詞)ため、本Validatorの設計上は
# 意図的にTRUE_CONTENT_MISMATCH(retry対象)のまま残す。"st"は"saint"の略記
# である可能性もあり、機械的に安全とは断定できないため。これは
# ASR_VALIDATION_UNCERTAIN Guardrail(3回連続で改善しなければretry停止)で
# 別途吸収する設計とし、Validator単体では過度に許容しない。
AMBIGUOUS_FIXTURES = [
    {
        "name": "St. abbreviation ASR punctuation artifact (benches/a2/full_story_part2, excerpt)",
        "canonical": "So, the bench debate is not only about street furniture.",
        "asr": "So the bench debate is not only about St. furniture.",
        "expected": "TRUE_CONTENT_MISMATCH",
    },
]

NEGATIVE_FIXTURES = [
    {"name": "number changed 2->3", "canonical": "The study followed 2 groups of participants.",
     "asr": "The study followed 3 groups of participants."},
    {"name": "year changed 2025->2024", "canonical": "The rule was vacated in 2025.",
     "asr": "The rule was vacated in 2024."},
    {"name": "negation flipped can->cannot", "canonical": "Users can cancel the plan at any time.",
     "asr": "Users cannot cancel the plan at any time."},
    {"name": "antonym increase->decrease", "canonical": "Prices tend to increase after the trial period.",
     "asr": "Prices tend to decrease after the trial period."},
    {"name": "important content word dropped", "canonical": "The company reported a significant loss last quarter.",
     "asr": "The company reported a loss last quarter."},
    {"name": "unrelated sentence appended", "canonical": "The park closes at nine.",
     "asr": "The park closes at nine. Also, remember to buy milk tomorrow."},
    {"name": "may misheard as May 1st (startups full_story_part1)",
     "canonical": "a company with a true network effect may first run at a loss",
     "asr": "a company with a true network effect May 1st run at a loss"},
]


def run():
    failures = []

    print("=== POSITIVE fixtures (should NOT trigger unnecessary retry) ===")
    for fx in POSITIVE_FIXTURES:
        r = classify_asr_match(fx["canonical"], fx["asr"])
        ok = r.should_pass or not r.should_retry
        status = "OK" if ok else "FAIL"
        print(f"[{status}] {fx['name']}: classification={r.classification} ratio={r.normalized_ratio:.3f} should_pass={r.should_pass} should_retry={r.should_retry}")
        if not ok:
            failures.append(fx["name"])

    print("\n=== AMBIGUOUS fixtures (意図的にretry対象/Review対象のまま残すことを確認) ===")
    for fx in AMBIGUOUS_FIXTURES:
        r = classify_asr_match(fx["canonical"], fx["asr"])
        ok = r.classification == fx["expected"]
        status = "OK" if ok else "FAIL"
        print(f"[{status}] {fx['name']}: classification={r.classification} (expected {fx['expected']}) ratio={r.normalized_ratio:.3f}")
        if not ok:
            failures.append(fx["name"])

    print("\n=== NEGATIVE fixtures (MUST stay retry-eligible, must NOT auto-pass) ===")
    for fx in NEGATIVE_FIXTURES:
        r = classify_asr_match(fx["canonical"], fx["asr"])
        ok = (not r.should_pass) and r.classification in ("TRUE_CONTENT_MISMATCH", "TTS_FAILURE")
        status = "OK" if ok else "FAIL"
        print(f"[{status}] {fx['name']}: classification={r.classification} ratio={r.normalized_ratio:.3f} should_pass={r.should_pass} reason={r.reason}")
        if not ok:
            failures.append(fx["name"])

    if failures:
        raise AssertionError(f"{len(failures)}件のfixtureが期待通りに分類されなかった: {failures}")
    print(f"\nOK: 全{len(POSITIVE_FIXTURES)+len(NEGATIVE_FIXTURES)}件のfixtureが期待通りに分類された")


if __name__ == "__main__":
    run()
