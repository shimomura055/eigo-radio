# ============================================================
# er015_standard_a2_6000_generation_first_trial_01_test_01.py
# STANDARD-A2-6000-GENERATION-FIRST-TRIAL-01のオフラインテスト
# (API呼び出しなし)。
# ============================================================
from __future__ import annotations

import hashlib

import er015_standard_a2_6000_generation_first_trial_01 as trial


def test_gen_first_prompt_differs_only_in_vocab_block():
    a = trial.std_gen.STANDARD_A2_PROMPT_V5
    b = trial.GEN_FIRST_PROMPT_V1
    assert a != b
    # A/Bとも語彙段落を除いた前後の文字列が完全一致することを確認する
    a_prefix, _, a_suffix = a.partition(trial._OLD_VOCAB_BLOCK)
    b_prefix, _, b_suffix = b.partition(trial._NEW_VOCAB_BLOCK_GEN_FIRST)
    assert a_prefix == b_prefix
    assert a_suffix == b_suffix
    assert a_prefix != ""
    assert a_suffix != ""


def test_gen_first_prompt_sha256_matches_constant():
    actual = hashlib.sha256(trial.GEN_FIRST_PROMPT_V1.encode("utf-8")).hexdigest()
    assert actual == trial.GEN_FIRST_PROMPT_SHA256


def test_gen_first_prompt_has_article_template_placeholder():
    assert "{advanced_article}" in trial.GEN_FIRST_PROMPT_V1


def test_gen_first_prompt_keeps_structure_contract_line():
    structure_line = (
        "Keep the same Markdown structure (the \"# \" title, the two "
        "\"### \" sections, and the final \"## In one line\" section); "
        "do not add or remove sections."
    )
    assert structure_line in trial.GEN_FIRST_PROMPT_V1
    assert structure_line in trial.std_gen.STANDARD_A2_PROMPT_V5


def test_gen_first_prompt_does_not_ask_for_abcd_classification_output():
    lowered = trial.GEN_FIRST_PROMPT_V1.lower()
    assert "decision" not in lowered
    assert "keep -- " not in lowered
    assert "candidate word" not in lowered or "do not" in lowered


def test_gen_first_prompt_contains_required_elements():
    text = trial.GEN_FIRST_PROMPT_V1
    assert "top 6,000" in text
    assert "flush" in text and "use" in text
    assert "storytelling" in text.lower()
    assert "proper noun" in text.lower()
    assert "exception categories" in text.lower()


def test_lemma_and_rank_functions_are_reused_from_v2mod():
    assert trial.lemma_candidates_v2 is trial.v2mod.lemma_candidates_v2
    assert trial.rank_of_word_v2 is trial.v2mod.rank_of_word_v2
    assert trial.fact_tokens_check is trial.v2mod.fact_tokens_check


def test_fact_tokens_check_offline_no_change():
    before = "Meta said the plan cost $100.\n\nSam Ortiz confirmed it."
    after = "Meta said the plan cost $100.\n\nSam Ortiz confirmed it."
    result = trial.fact_tokens_check(before, after)
    assert result["overall_fact_tokens_match"] is True
    assert result["numbers_match"] is True
    assert result["proper_noun_words_match"] is True


def test_fact_tokens_check_offline_detects_number_change():
    before = "The device cost $100 last year."
    after = "The device cost $150 last year."
    result = trial.fact_tokens_check(before, after)
    assert result["overall_fact_tokens_match"] is False
    assert result["numbers_match"] is False


def test_residual_words_offline_filters_by_threshold():
    import wordfreq
    top20000 = wordfreq.top_n_list("en", 20000)
    rank_of = trial._rank_of_map(top20000)
    text = (
        "Title Line\n\n"
        "The sewer system carries wastewater through an ancient artery "
        "under the town. Septic tanks are a simple alternative.\n"
    )
    residual = trial._residual_words(text, rank_of)
    words = {e["word"] for e in residual}
    assert all(e["rank"] is None or e["rank"] > trial.RANK_THRESHOLD
               for e in residual)
    # "the", "system", "under" 等の高頻度語は残存語に含まれないはず
    assert "the" not in words
    assert "system" not in words


def test_paragraph_count_offline():
    text = "Title\n\nPara one sentence.\n\nPara two sentence.\n\nPara three."
    assert trial._paragraph_count(text) == 3


def test_process_label_registered_in_routing_contract():
    assert "STANDARD_A2_ADAPTATION" in trial.routing.PROCESS_MODEL_MAP
    assert (trial.routing.PROCESS_MODEL_MAP["STANDARD_A2_ADAPTATION"]
            == trial.routing.WRITER_MODEL)


def test_ja_source_paths_exist_and_are_approved_evidence_dir():
    import os
    for path in trial.JA_SOURCE_PATHS.values():
        assert os.path.exists(path), path
        assert "docs" + os.sep + "evidence" in path


def test_generate_standard_a2_gen_first_rejects_wrong_effort():
    try:
        trial.generate_standard_a2_gen_first("dummy", effort="low")
        raise AssertionError("expected ValueError for mismatched effort")
    except ValueError:
        pass


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
