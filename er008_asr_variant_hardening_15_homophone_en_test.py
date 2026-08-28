# ============================================================
# er008_asr_variant_hardening_15_homophone_en_test.py
# ER-008-ASR-VARIANT-HARDENING-AND-RETRY-15 Part J-2: 必須fixture
# ============================================================
from __future__ import annotations

import er008_asr_variant_hardening_15_homophone_en as hp

HOMOPHONE_PAIRS = [
    ("wait", "weight"),
    ("their", "there"),
    ("hear", "here"),
    ("week", "weak"),
]

NON_HOMOPHONE_PAIRS = [
    ("wait", "wet"),
    ("weight", "white"),
    ("hear", "hair"),
    ("there", "three"),
]


def test_required_homophone_pairs_pass():
    for a, b in HOMOPHONE_PAIRS:
        result = hp.homophone_arpabet_equivalent(a, b)
        assert result is True, f"{a}/{b}はhomophoneと判定されるべき(結果={result})"
    print("PASS: test_required_homophone_pairs_pass")


def test_required_non_homophone_pairs_fail():
    for a, b in NON_HOMOPHONE_PAIRS:
        result = hp.homophone_arpabet_equivalent(a, b)
        assert result is False, f"{a}/{b}はhomophoneと判定されてはならない(結果={result})"
    print("PASS: test_required_non_homophone_pairs_fail")


def test_entity_word_primary_match_kristie_christie():
    # 固有名詞Case A: 代表発音同士の完全一致(D-1で先頭音グループを
    # 修正した効果込み)。
    assert hp.entity_word_arpabet_primary_match("kristie", "christie") is True
    assert hp.entity_word_arpabet_primary_match("kristie", "christy") is True
    print("PASS: test_entity_word_primary_match_kristie_christie")


def test_entity_word_primary_match_tse_rejects_coincidental_overlap():
    # "tse"はCMU辞書に存在するが(無関係な理由で)、代表(先頭)発音は
    # "T S IY1"。ASR候補"tay"(T EY1)/"say"(S EY1)とは代表発音が
    # 一致しないため、Case Aでは解決しない(D-2'(B)、Ledgerへ回すべき
    # ケース)。
    assert hp.entity_word_arpabet_primary_match("tse", "tay") is False
    assert hp.entity_word_arpabet_primary_match("tse", "say") is False
    print("PASS: test_entity_word_primary_match_tse_rejects_coincidental_overlap")


def test_entity_span_match_requires_all_words_resolved():
    # "Kristie Tse"全体としては、"Tse"側が解決しないため span 全体は
    # matched=Falseのまま(resolved=Trueだが一致しない、または一部OOV)。
    result = hp.entity_span_arpabet_match("Kristie Tse", "Christy Tay")
    assert result.matched is False
    print("PASS: test_entity_span_match_requires_all_words_resolved")


def test_unresolvable_word_returns_none_not_false():
    # CMU辞書に存在しない語同士は「不一致」ではなく「判定不能」(None)を
    # 返す(呼び出し側が安全にCase Bへ回せるようにするため)。
    result = hp.homophone_arpabet_equivalent("zzzznotarealword", "wait")
    assert result is None
    print("PASS: test_unresolvable_word_returns_none_not_false")


if __name__ == "__main__":
    test_required_homophone_pairs_pass()
    test_required_non_homophone_pairs_fail()
    test_entity_word_primary_match_kristie_christie()
    test_entity_word_primary_match_tse_rejects_coincidental_overlap()
    test_entity_span_match_requires_all_words_resolved()
    test_unresolvable_word_returns_none_not_false()
    print("ALL TESTS PASSED")
