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
    {
        # ER-006-ASR-VALIDATION-RESIDUAL-02(2026-08-22)、Pool Benches Pilot-02実測。
        # tts_safe_number_words_en()がTTS入力側だけ"two"→"2"へ変換しているため、
        # canonical(=TTS入力後のtext)は"2"だが、OpenAI gpt-4o-mini-transcribeは
        # 綴りのまま"two"と書き起こした。値は変わっていないので吸収してよい。
        "name": "spelled/digit small number (benches/b1/comment_3, OpenAI ASR spells out '2' as 'two')",
        "canonical": "Next, we will look at this issue from 2 more angles.",
        "asr": "Next, we will look at this issue from two more angles.",
    },
    {
        # ER-006-VALIDATOR-NUMERIC-COST-RECONCILE-01(2026-08-22)、実際にPublic
        # Benches Boavida segmentでAzure Secondary ASR(Phrase List付き)が
        # 固有名詞自体は正しく認識したにもかかわらず、"28"を"twenty-eight"と
        # 綴ったためsegment全体がFAILしていた実例。数値正規化の一般化により解消。
        "name": "cardinal number 28 <-> twenty-eight (benches Boavida segment, real Azure Secondary ASR output)",
        "canonical": "A separate review by Boavida and colleagues in 2023 examined 28 articles published from 2020 to 2023.",
        "asr": "A separate review by Boavida and colleagues in 2023 examined twenty-eight articles published from 2020 to 2023.",
    },
    {"name": "larger cardinal 125 <-> one hundred twenty-five",
     "canonical": "The survey collected 125 responses.",
     "asr": "The survey collected one hundred twenty-five responses."},
    {"name": "year 2023 <-> two thousand twenty-three (standard cardinal reading)",
     "canonical": "The report was published in 2023.",
     "asr": "The report was published in two thousand twenty-three."},
    {"name": "comma thousands separator 1,000 <-> 1000",
     "canonical": "The venue holds 1,000 people.",
     "asr": "The venue holds 1000 people."},
    {"name": "percent 28% <-> twenty-eight percent",
     "canonical": "Prices rose by 28% last year.",
     "asr": "Prices rose by twenty-eight percent last year."},
    {"name": "currency $5 <-> five dollars",
     "canonical": "The ticket costs $5.",
     "asr": "The ticket costs five dollars."},
    {"name": "decimal 2.5 <-> two point five",
     "canonical": "The average score was 2.5.",
     "asr": "The average score was two point five."},
    {"name": "ordinal word <-> digit ordinal (third <-> 3rd, not cardinal)",
     "canonical": "This is the third time we've seen this pattern.",
     "asr": "This is the 3rd time we've seen this pattern."},
    # ER-006-GATE-CALIBRATION-ASR-CASCADE-MATH-VALIDATOR-01 Part B: 規則的な
    # 単数形/複数形の揺れ(No.6 delivery topic A2 full_story_part1の実例。
    # "Sweeny"/"Sweeney"というASR固有名詞差と同時に発生し、is_entity_like_mismatch
    # の判定を無関係にブロックしていた)。
    {"name": "singular/plural noun variance (result/results, real No.6 A2 ASR pattern)",
     "canonical": "the result of the 2020 U.S. presidential election",
     "asr": "the results of the 2020 U.S. presidential election"},
    {"name": "singular/plural noun variance, -es ending (box/boxes)",
     "canonical": "They opened the box on the porch.",
     "asr": "They opened the boxes on the porch."},
    # ER-006-GATE-CALIBRATION-ASR-CASCADE-MATH-VALIDATOR-01 Part C: 数式表記
    # (markdown italics、"="、"×"、小数、負/上付き指数)の一般正規化。
    {"name": "markdown italics + equals + decimal (b coefficient, No.6 real pattern)",
     "canonical": "*b* = 0.90",
     "asr": "b equals 0.90"},
    {"name": "equals spoken as 'is equal to'",
     "canonical": "*b* = 0.90",
     "asr": "b is equal to 0.90"},
    {"name": "negative superscript exponent <-> spoken 'to the minus N'",
     "canonical": "a probability of 2 × 10⁻¹⁶",
     "asr": "a probability of 2 times 10 to the minus 16"},
    {"name": "negative superscript exponent with ordinal-style ASR reading ('16th')",
     "canonical": "a probability of 2 × 10⁻¹⁶",
     "asr": "a probability of 2 times 10 to the minus 16th"},
    {"name": "positive superscript exponent <-> spoken 'to the N'",
     "canonical": "roughly 10¹⁶ combinations",
     "asr": "roughly 10 to the 16th combinations"},
    {"name": "exponent word 'negative' (real No.6 B1 ASR wording) <-> Unicode superscript",
     "canonical": "b = 0.90, P < 2 × 10⁻¹⁶",
     "asr": "b equals 0.90, p less than 2 times 10 to the negative 16th"},
    {"name": "ASCII caret exponent notation (real ASR output '10^-16') <-> Unicode superscript",
     "canonical": "P < 2 × 10⁻¹⁶",
     "asr": "P < 2 × 10^-16"},
    {"name": "'x' as multiplication between digits, no spaces (real ASR output '2x10^-16')",
     "canonical": "p below 2 × 10⁻¹⁶",
     "asr": "p below 2x10^-16"},
    {"name": "less-than symbol <-> spoken 'less than' (real No.6 B1 pattern)",
     "canonical": "P < 2 × 10⁻¹⁶",
     "asr": "P less than 2 times 10 to the minus 16"},
    {"name": "greater-than symbol <-> spoken 'greater than'",
     "canonical": "a rate above p > 0.05",
     "asr": "a rate above p greater than 0.05"},
]

# ER-006-ASR-VALIDATION-RESIDUAL-02(2026-08-22)で方針変更: "St."略記
# artifact(street→St.)は、当初(ER-006-POOL-PREPROD-HARDENING-01時点)は
# "st"が"saint"の略記である可能性を排除できないとしてTRUE_CONTENT_MISMATCH
# のまま残していたが、実際にはこの曖昧さはcanonical側テキストを基準に
# 判定すれば解消できる: normalize_text()の略語展開はcanonical側が明示的に
# "street"(一般名詞)である場合の"st"のみを対象にしており(_STREET_SUFFIX_
# EXPANSIONS参照)、canonical側が"Saint"(固有名詞、例: "St. Louis")の
# ケースでは"saint"という語自体が展開対象に含まれないため発火しない。
# つまりStreet/Saintの曖昧性はcanonical textが常に正解を握っており、
# 機械的にも安全に判定できる。個別記事のwhitelistではなく、USPS通り
# 種別略語という閉じた既知集合への一般対策として実装した
# (詳細はER-006-AUDIO-COST-PILOT-02完了報告参照)。
AMBIGUOUS_FIXTURES = [
    {
        "name": "St. abbreviation ASR punctuation artifact (benches/a2/full_story_part2, excerpt)",
        "canonical": "So, the bench debate is not only about street furniture.",
        "asr": "So the bench debate is not only about St. furniture.",
        "expected": "NORMALIZED_MATCH",
    },
    {
        "name": "St. as Saint abbreviation must NOT be absorbed (canonical says saint, not street)",
        "canonical": "The event took place near Saint Louis, not far from the river.",
        "asr": "The event took place near St. Louis, not far from the river.",
        "expected": "ASR_VALIDATION_UNCERTAIN",
    },
]

NEGATIVE_FIXTURES = [
    {"name": "number changed 2->3", "canonical": "The study followed 2 groups of participants.",
     "asr": "The study followed 3 groups of participants."},
    {"name": "number changed two->three, spelled form (must not be masked by digit/word equivalence)",
     "canonical": "The study followed two groups of participants.",
     "asr": "The study followed three groups of participants."},
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
    # ER-006-VALIDATOR-NUMERIC-COST-RECONCILE-01(2026-08-22): 数値正規化の
    # 一般化で絶対に吸収してはいけない安全fixture(タスク仕様§4に対応)。
    {"name": "three != 3:00 (time-format artifact, digit value differs)",
     "canonical": "They looked at three nearby neighborhoods.",
     "asr": "They looked at 3:00 nearby neighborhoods."},
    {"name": "28 != 28th (cardinal vs ordinal, real bug found and fixed this task)",
     "canonical": "The study included 28 articles.",
     "asr": "The study included 28th articles."},
    {"name": "5 != $5 (currency marker must not be dropped)",
     "canonical": "The fee is 5.",
     "asr": "The fee is $5."},
    {"name": "5 != 5% (percent marker must not be dropped)",
     "canonical": "The rate is 5.",
     "asr": "The rate is 5%."},
    {"name": "1.5 != 15 (decimal point must not be silently removed)",
     "canonical": "The score was 1.5.",
     "asr": "The score was 15."},
    {"name": "year 2023 != 2024 (cardinal normalization must not blur distinct years)",
     "canonical": "It happened in 2023.",
     "asr": "It happened in 2024."},
    {"name": "28 != 2,016 people (comma-number normalization must not mask an inserted/different quantity)",
     "canonical": "It happened in 2016.",
     "asr": "It happened in 2,016 people."},
    {"name": "percent value changed (28% != 30%, must not be masked by percent-marker normalization)",
     "canonical": "Prices rose by 28% last year.",
     "asr": "Prices rose by 30% last year."},
    {"name": "unit dropped (5 dollars != 5, currency word absence must be caught)",
     "canonical": "The ticket costs five dollars.",
     "asr": "The ticket costs five."},
    # ER-006-GATE-CALIBRATION-ASR-CASCADE-MATH-VALIDATOR-01 Part C-4: 数式表記の
    # 意味が異なる場合は、正規化後も絶対にPASSしてはいけない安全fixture。
    {"name": "exponent sign flipped (10^-16 != 10^16, must not collapse)",
     "canonical": "a probability of 2 × 10⁻¹⁶",
     "asr": "a probability of 2 times 10 to the 16th"},
    {"name": "exponent digits differ (10^-16 != 10^-6)",
     "canonical": "a probability of 2 × 10⁻¹⁶",
     "asr": "a probability of 2 times 10 to the minus 6"},
    {"name": "decimal value differs (0.90 != 0.09, digit transposition)",
     "canonical": "*b* = 0.90",
     "asr": "b equals 0.09"},
    {"name": "decimal value differs (0.90 != 9.0, decimal point shifted)",
     "canonical": "*b* = 0.90",
     "asr": "b equals 9.0"},
    {"name": "coefficient differs (2 × 10^-16 != 2 × 10^-15, exponent off by one)",
     "canonical": "a probability of 2 × 10⁻¹⁶",
     "asr": "a probability of 2 times 10 to the minus 15"},
    {"name": "multiplier coefficient differs (2 × != 20 ×)",
     "canonical": "a probability of 2 × 10⁻¹⁶",
     "asr": "a probability of 20 times 10 to the minus 16"},
    {"name": "negative sign missing entirely (10^-16 != 10, exponent dropped)",
     "canonical": "a probability of 2 × 10⁻¹⁶",
     "asr": "a probability of 2 times 10"},
    {"name": "exponent value missing (spoken form omits the digit)",
     "canonical": "roughly 10¹⁶ combinations",
     "asr": "roughly 10 combinations"},
    {"name": "caret exponent sign flipped (10^-16 != 10^16, ASCII form)",
     "canonical": "P < 2 × 10⁻¹⁶",
     "asr": "P < 2 × 10^16"},
    {"name": "less-than vs greater-than must not collapse (P < X != P > X)",
     "canonical": "P < 2 × 10⁻¹⁶",
     "asr": "P greater than 2 times 10 to the minus 16"},
    {"name": "unrelated plural nouns must not be absorbed as a plural pair (cats != dogs)",
     "canonical": "They were chasing the cats around the yard.",
     "asr": "They were chasing the dogs around the yard."},
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

    print("\n=== AMBIGUOUS fixtures (吸収してよいものと、してはいけないものを区別できることを確認) ===")
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
