# ============================================================
# er015_vocab_band_6000_10000_14000_trial_01_test_01.py
# NEWS-VOCAB-BAND-6000-10000-14000-TRIAL-01のオフラインテスト
# (API呼び出しなし)。
# ============================================================
from __future__ import annotations

import hashlib

import er015_vocab_band_6000_10000_14000_trial_01 as trial


def test_prompt_template_differs_only_in_band_number():
    a = trial.render_prompt(6000, "[SAMPLE]")
    b = trial.render_prompt(10000, "[SAMPLE]")
    c = trial.render_prompt(14000, "[SAMPLE]")
    a_norm = a.replace("6,000", "<BAND>")
    b_norm = b.replace("10,000", "<BAND>")
    c_norm = c.replace("14,000", "<BAND>")
    assert a_norm == b_norm == c_norm
    assert "6,000" in a and "10,000" in b and "14,000" in c


def test_prompt_sha256_by_band_all_differ():
    shas = list(trial.PROMPT_SHA256_BY_BAND.values())
    assert len(shas) == len(set(shas)) == 3


def test_prompt_sha256_matches_recomputation():
    for band in trial.BANDS:
        text = trial.PROMPT_TEMPLATE_VB.format(
            band=band, advanced_article="{advanced_article}")
        expected = hashlib.sha256(text.encode("utf-8")).hexdigest()
        assert expected == trial.PROMPT_SHA256_BY_BAND[band]


def test_prompt_template_has_article_placeholder():
    assert "{advanced_article}" in trial.PROMPT_TEMPLATE_VB
    assert "{band:,}" in trial.PROMPT_TEMPLATE_VB


def test_prompt_keeps_structure_contract_line():
    structure_line = (
        "Keep the same Markdown structure (the \"# \" title, the two "
        "\"### \" sections, and the final \"## In one line\" section); "
        "do not add or remove sections."
    )
    assert structure_line in trial.PROMPT_TEMPLATE_VB


def test_prompt_only_uses_approved_example_words():
    text = trial.PROMPT_TEMPLATE_VB
    approved = ["wastewater", "surprisingly", "piano", "curtain", "Meta",
                "Muse", "Reuters"]
    for w in approved:
        assert w in text
    # Trial対象本文固有の語を個別に例示していないことを確認する
    forbidden = ["septic", "sewer", "artery", "flush", "concierge"]
    lowered = text.lower()
    for w in forbidden:
        assert w not in lowered


def test_prompt_does_not_ask_for_abcd_classification_output():
    lowered = trial.PROMPT_TEMPLATE_VB.lower()
    assert "category a" not in lowered
    assert "keep -- " not in lowered
    assert "do not list or output any candidate words" in lowered


def test_prompt_states_three_exclusion_kinds_only():
    text = trial.PROMPT_TEMPLATE_VB
    assert "(1) A true proper noun" in text
    assert "(2) A derived or compound word" in text
    assert "(3) A word that is a common loanword" in text
    assert "(4)" not in text


def test_lemma_and_rank_functions_are_reused_from_v2mod():
    assert trial.lemma_candidates_v2 is trial.v2mod.lemma_candidates_v2
    assert trial.rank_of_word_v2 is trial.v2mod.rank_of_word_v2
    assert trial.fact_tokens_check is trial.v2mod.fact_tokens_check


def test_fact_tokens_check_offline_no_change():
    before = "Meta said the plan cost $100.\n\nSam Ortiz confirmed it."
    after = "Meta said the plan cost $100.\n\nSam Ortiz confirmed it."
    result = trial.fact_tokens_check(before, after)
    assert result["overall_fact_tokens_match"] is True


def test_fact_tokens_check_offline_detects_number_change():
    before = "The device cost $100 last year."
    after = "The device cost $150 last year."
    result = trial.fact_tokens_check(before, after)
    assert result["overall_fact_tokens_match"] is False
    assert result["numbers_match"] is False


def test_residual_words_offline_filters_by_threshold_per_band():
    import wordfreq
    top20000 = wordfreq.top_n_list("en", 20000)
    rank_of = trial._rank_of_map(top20000)
    text = (
        "Title Line\n\n"
        "The sewer system carries wastewater through an ancient artery "
        "under the town. Septic tanks are a simple alternative.\n"
    )
    residual_6000 = trial._residual_words(text, rank_of, 6000)
    residual_14000 = trial._residual_words(text, rank_of, 14000)
    words_6000 = {e["word"] for e in residual_6000}
    words_14000 = {e["word"] for e in residual_14000}
    assert all(e["rank"] is None or e["rank"] > 6000 for e in residual_6000)
    assert all(e["rank"] is None or e["rank"] > 14000 for e in residual_14000)
    # 高い閾値ほど残存語数は減るか同数(単調性)
    assert len(words_14000) <= len(words_6000)
    assert "the" not in words_6000
    assert "system" not in words_6000


def test_residual_words_proper_noun_candidate_flagged():
    import wordfreq
    top20000 = wordfreq.top_n_list("en", 20000)
    rank_of = trial._rank_of_map(top20000)
    text = "Title\n\nReuters reported that Muse was paused by Meta.\n"
    residual = trial._residual_words(text, rank_of, 6000)
    proper = {e["word"] for e in residual if e["proper_noun_candidate"]}
    assert "reuters" in proper or "muse" in proper or "meta" in proper or proper


def test_paragraph_count_offline():
    text = "Title\n\nPara one sentence.\n\nPara two sentence.\n\nPara three."
    assert trial._paragraph_count(text) == 3


def test_process_label_registered_in_routing_contract():
    assert "STANDARD_A2_ADAPTATION" in trial.routing.PROCESS_MODEL_MAP
    assert (trial.routing.PROCESS_MODEL_MAP["STANDARD_A2_ADAPTATION"]
            == trial.routing.WRITER_MODEL)


def test_input_paths_exist_and_are_prior_trial_outputs():
    import os
    for path in trial.INPUT_PATHS.values():
        assert os.path.exists(path), path
        assert "standard_a2_6000_generation_first_trial_01" in path


def test_generate_band_article_rejects_wrong_effort():
    try:
        trial.generate_band_article(6000, "dummy", effort="low")
        raise AssertionError("expected ValueError for mismatched effort")
    except ValueError:
        pass


def test_structure_contract_check_offline_pass_and_fail():
    restore_r2 = trial.vfl01.restore_r2
    good = (
        "# Title\n\n"
        "Some intro text.\n\n"
        "### First section\n\n"
        "Body one.\n\n"
        "### Second section\n\n"
        "Body two.\n\n"
        "## In one line\n\n"
        "Summary line."
    )
    bad_one_heading = (
        "# Title\n\n### Only one section\n\nBody.\n\n## In one line\n\nX."
    )
    good_result = restore_r2.validate_point_structure(good)
    bad_result = restore_r2.validate_point_structure(bad_one_heading)
    assert good_result.status == "STRUCTURE_PASS"
    assert good_result.h3_count == 2
    assert bad_result.status != "STRUCTURE_PASS"
    assert bad_result.h3_count == 1


def test_bands_are_the_three_committed_conditions():
    assert trial.BANDS == [6000, 10000, 14000]


def test_budget_guardrail_cap_and_ceiling():
    assert trial.BUDGET_JPY_CAP == 30.0
    assert trial.PER_CALL_CEILING_JPY <= trial.BUDGET_JPY_CAP


if __name__ == "__main__":
    import sys

    failures = 0
    tests = [obj for name, obj in list(globals().items())
             if name.startswith("test_") and callable(obj)]
    for t in tests:
        try:
            t()
            print(f"[PASS] {t.__name__}")
        except Exception as e:  # noqa: BLE001
            failures += 1
            print(f"[FAIL] {t.__name__}: {type(e).__name__}: {e}")
    print(f"\n{len(tests) - failures}/{len(tests)} passed")
    sys.exit(1 if failures else 0)
