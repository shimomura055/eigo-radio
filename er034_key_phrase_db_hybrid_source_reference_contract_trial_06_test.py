# ============================================================
# er034_key_phrase_db_hybrid_source_reference_contract_trial_06_test.py
# KEY-PHRASE-DB-HYBRID-SOURCE-REFERENCE-CONTRACT-TRIAL-06 (Phase B)
# ============================================================
# API呼び出しを一切行わない構造unit test。
# 実行: .venv/Scripts/python.exe -m unittest
#   er034_key_phrase_db_hybrid_source_reference_contract_trial_06_test -v
# ============================================================

from __future__ import annotations

import os
import unittest

import er003_key_words_min_unit as p2g
import er023_key_phrase_db_ingest as ing
import er028_key_phrase_db_hybrid_trial_03_run as base
import er030_key_phrase_db_hybrid_selector_01 as selector01
import er032_key_phrase_db_hybrid_core_v2_trial_05_run as run5
import er034_key_phrase_db_hybrid_source_reference_contract_trial_06_contract as contract
import er034_key_phrase_db_hybrid_source_reference_contract_trial_06_run as runner

TWINS_A2_PATH = "er013_output/family_c_episode_trial_12/twins_a2/article_normalized.txt"
MELOS_A2_PATH = "er026_output/family_z_production_e2e_01/melos/run_01/article.md"


def _fixture_shortlist():
    return [
        {"surface_form": "digital twin", "canonical_form": "digital twin", "unit_type": "noun_phrase",
         "important_noun_phrase_candidate": True, "source_span": "digital twin",
         "context_sentence_id": "S3", "occurrence_count_in_article": 2,
         "matched_dbs": ["wiktionary"], "db_categories": ["multiword_term"]},
        {"surface_form": "take over", "canonical_form": "take over", "unit_type": "phrasal_verb",
         "important_noun_phrase_candidate": False, "source_span": "take over",
         "context_sentence_id": "S7", "occurrence_count_in_article": 1,
         "matched_dbs": ["ngsl"], "db_categories": []},
        {"surface_form": "audition", "canonical_form": "audition", "unit_type": "word",
         "important_noun_phrase_candidate": False, "source_span": "audition",
         "context_sentence_id": None, "occurrence_count_in_article": 3,
         "matched_dbs": ["cefr_j"], "db_categories": []},
    ]


def _fixture_sentence_reference():
    return {
        "S3": "Her digital twin appeared in the mirror",
        "S7": "The twin began to take over small tasks",
    }


class CandidateIdAssignmentTests(unittest.TestCase):
    def test_ids_are_sequential_and_unique(self):
        shortlist = _fixture_shortlist()
        result = contract.assign_candidate_ids(shortlist)
        self.assertEqual(result["candidate_ids"], ["C1", "C2", "C3"])
        self.assertEqual(len(result["id_to_candidate"]), 3)
        self.assertEqual(result["id_to_candidate"]["C1"]["surface_form"], "digital twin")
        self.assertEqual(result["id_to_candidate"]["C2"]["surface_form"], "take over")

    def test_original_shortlist_not_mutated(self):
        shortlist = _fixture_shortlist()
        contract.assign_candidate_ids(shortlist)
        self.assertNotIn("candidate_id", shortlist[0])


class SchemaConstructionTests(unittest.TestCase):
    """新schemaがsource_sentence/source_spanをLLMへ一切書かせない構造に
    なっていること、既存のenum/フィールド数はほぼ据え置きであること。"""

    def test_source_span_and_source_sentence_removed_from_llm_schema(self):
        props = contract.build_item_schema_properties(["C1", "C2", "C3"])
        self.assertNotIn("source_span", props)
        self.assertNotIn("source_sentence", props)
        self.assertIn("source_candidate_id", props)
        self.assertIn("surface_echo", props)
        self.assertEqual(props["source_candidate_id"]["enum"], ["C1", "C2", "C3"])

    def test_required_fields_match_properties_keys_exactly(self):
        # OpenAI Structured Outputs strict modeはrequired==properties鍵集合を要求する。
        candidate_ids = ["C1", "C2"]
        schema = contract.build_json_schema(candidate_ids)
        item_schema = schema["schema"]["properties"]["items"]["items"]
        self.assertEqual(set(item_schema["required"]), set(item_schema["properties"].keys()))
        self.assertTrue(item_schema["additionalProperties"] is False)

    def test_item_count_fixed_at_5(self):
        schema = contract.build_json_schema(["C1"])
        items_schema = schema["schema"]["properties"]["items"]
        self.assertEqual(items_schema["minItems"], 5)
        self.assertEqual(items_schema["maxItems"], 5)

    def test_enum_values_change_per_call_shortlist(self):
        schema_a = contract.build_json_schema(["C1", "C2"])
        schema_b = contract.build_json_schema(["C1", "C2", "C3", "C4", "C5"])
        enum_a = schema_a["schema"]["properties"]["items"]["items"]["properties"]["source_candidate_id"]["enum"]
        enum_b = schema_b["schema"]["properties"]["items"]["items"]["properties"]["source_candidate_id"]["enum"]
        self.assertEqual(enum_a, ["C1", "C2"])
        self.assertEqual(enum_b, ["C1", "C2", "C3", "C4", "C5"])


class RestoreSourceFieldsTests(unittest.TestCase):
    """候補ID -> source_sentence/source_span復元の決定論性・複数出現候補の
    復元規則(context_sentence_idが指す1個の文に固定)・enum外/防御的
    unresolvedケース。"""

    def setUp(self):
        ids = contract.assign_candidate_ids(_fixture_shortlist())
        self.id_to_candidate = ids["id_to_candidate"]
        self.sentence_reference = _fixture_sentence_reference()

    def test_deterministic_restoration_same_input_same_output(self):
        items = [{"rank": 1, "source_candidate_id": "C1", "surface_echo": "digital twin"}]
        r1 = contract.restore_source_fields(items, self.id_to_candidate, self.sentence_reference)
        r2 = contract.restore_source_fields(items, self.id_to_candidate, self.sentence_reference)
        self.assertEqual(r1["items"][0]["source_span"], r2["items"][0]["source_span"])
        self.assertEqual(r1["items"][0]["source_sentence"], r2["items"][0]["source_sentence"])

    def test_source_sentence_restored_from_context_sentence_id(self):
        items = [{"rank": 1, "source_candidate_id": "C1", "surface_echo": "digital twin"}]
        restored = contract.restore_source_fields(items, self.id_to_candidate, self.sentence_reference)
        item = restored["items"][0]
        self.assertEqual(item["source_span"], "digital twin")
        self.assertEqual(item["source_sentence"], "Her digital twin appeared in the mirror")

    def test_candidate_without_context_sentence_id_falls_back_to_source_span(self):
        # C3(audition)はcontext_sentence_id=None(attach_compact_contextが
        # 出現文を見つけられなかった稀なケースの防御的fallback)。
        items = [{"rank": 1, "source_candidate_id": "C3", "surface_echo": "audition"}]
        restored = contract.restore_source_fields(items, self.id_to_candidate, self.sentence_reference)
        item = restored["items"][0]
        self.assertEqual(item["source_span"], "audition")
        self.assertEqual(item["source_sentence"], "audition")

    def test_unresolved_candidate_id_is_defensively_recorded(self):
        # schemaのenum制約により通常は発生しないはずだが、防御的に検知できること。
        items = [{"rank": 1, "source_candidate_id": "C999", "surface_echo": "x"}]
        restored = contract.restore_source_fields(items, self.id_to_candidate, self.sentence_reference)
        self.assertEqual(len(restored["unresolved"]), 1)
        self.assertEqual(restored["unresolved"][0]["source_candidate_id"], "C999")

    def test_surface_echo_matching_candidate_not_flagged_as_mismatch(self):
        items = [{"rank": 1, "source_candidate_id": "C1", "surface_echo": "Digital Twin"}]
        restored = contract.restore_source_fields(items, self.id_to_candidate, self.sentence_reference)
        self.assertFalse(restored["items"][0]["candidate_mismatch_suspected"])
        self.assertEqual(restored["mismatch_count"], 0)

    def test_surface_echo_mismatching_candidate_flagged_non_blocking(self):
        items = [{"rank": 1, "source_candidate_id": "C1", "surface_echo": "take over"}]
        restored = contract.restore_source_fields(items, self.id_to_candidate, self.sentence_reference)
        self.assertTrue(restored["items"][0]["candidate_mismatch_suspected"])
        self.assertEqual(restored["mismatch_count"], 1)
        # 非ブロッキング: source_span/source_sentenceは選ばれたcandidate(C1)の
        # ものがそのまま入る(取り違え検知はSTOPさせない)。
        self.assertEqual(restored["items"][0]["source_span"], "digital twin")

    def test_empty_surface_echo_not_flagged(self):
        items = [{"rank": 1, "source_candidate_id": "C1", "surface_echo": ""}]
        restored = contract.restore_source_fields(items, self.id_to_candidate, self.sentence_reference)
        self.assertFalse(restored["items"][0]["candidate_mismatch_suspected"])

    def test_multiple_items_selecting_same_candidate_restore_independently(self):
        items = [
            {"rank": 1, "source_candidate_id": "C1", "surface_echo": "digital twin"},
            {"rank": 2, "source_candidate_id": "C1", "surface_echo": "digital twin"},
        ]
        restored = contract.restore_source_fields(items, self.id_to_candidate, self.sentence_reference)
        self.assertEqual(restored["items"][0]["source_sentence"], restored["items"][1]["source_sentence"])


class ProductionValidatorUnchangedIntegrationTests(unittest.TestCase):
    """復元後の辞書が既存p2g.validate_min_unit_selection(無変更)をそのまま
    通せる形になっていること(必須フィールド・文字列型の要件を満たす)。"""

    def test_restored_item_has_all_required_fields_for_existing_validator(self):
        ids = contract.assign_candidate_ids(_fixture_shortlist())
        item = {
            "rank": 1, "source_candidate_id": "C1", "surface_echo": "digital twin",
            "display_phrase": "digital twin", "ja_gloss": "デジタルツイン",
            "phrase_type": "noun_phrase", "normalization_type": "none", "normalization_note": "",
            "selection_reason": "reason", "listening_difficulty_reason": "reason",
            "inference_transparency": "MEDIUM", "topic_exposure_dependency": "MEDIUM",
            "comprehension_impact": "HIGH", "figurative_or_emotional_value": "LOW",
            "spoiler_risk": "LOW", "portfolio_category": "domain_expression",
            "portfolio_substitution": False, "portfolio_substitution_reason": "",
        }
        restored = contract.restore_source_fields(
            [item], ids["id_to_candidate"], _fixture_sentence_reference())
        restored_item = restored["items"][0]
        for field in p2g._ITEM_REQUIRED_FIELDS:
            self.assertIn(field, restored_item, f"missing field: {field}")
            self.assertIsInstance(restored_item[field], (str, int, bool))


class WrapV1V2StructuralTests(unittest.TestCase):
    """v1(er029 stage1)/v2(er032 stage1)いずれをラップしても、shortlistの
    各候補がcandidate ID付与に必要な既存フィールド(surface_form/
    source_span/context_sentence_id)を持つこと(API呼び出しなし)。"""

    @classmethod
    def setUpClass(cls):
        cls.dbs = ing.load_all_group1_dbs()

    def test_v1_wrap_shortlist_has_required_fields(self):
        if not os.path.exists(TWINS_A2_PATH):
            self.skipTest("article fixture not present")
        article_text = open(TWINS_A2_PATH, encoding="utf-8").read()
        s1r = runner.run_stage1_and_shortlist_v1_wrap(article_text, self.dbs, "Digital Twins")
        shortlist = s1r["shortlist_info"]["shortlist"]
        self.assertGreater(len(shortlist), 0)
        for c in shortlist:
            self.assertIn("surface_form", c)
            self.assertIn("source_span", c)
            self.assertIn("context_sentence_id", c)

    def test_v2_wrap_shortlist_has_required_fields(self):
        if not os.path.exists(TWINS_A2_PATH):
            self.skipTest("article fixture not present")
        article_text = open(TWINS_A2_PATH, encoding="utf-8").read()
        s1r = runner.run_stage1_and_shortlist_v2_wrap(article_text, self.dbs, "Digital Twins")
        shortlist = s1r["shortlist_info"]["shortlist"]
        self.assertGreater(len(shortlist), 0)
        for c in shortlist:
            self.assertIn("surface_form", c)
            self.assertIn("source_span", c)
            self.assertIn("context_sentence_id", c)

    def test_candidate_id_assignment_covers_full_v2_shortlist(self):
        if not os.path.exists(MELOS_A2_PATH):
            self.skipTest("article fixture not present")
        article_text = open(MELOS_A2_PATH, encoding="utf-8").read()
        s1r = runner.run_stage1_and_shortlist_v2_wrap(article_text, self.dbs, "The Three-Day Promise")
        shortlist = s1r["shortlist_info"]["shortlist"]
        id_result = contract.assign_candidate_ids(shortlist)
        self.assertEqual(len(id_result["candidate_ids"]), len(shortlist))
        self.assertEqual(len(set(id_result["candidate_ids"])), len(shortlist))


class NoFullArticleBodyInPromptTests(unittest.TestCase):
    """候補ID方式のprompt(SENTENCE REFERENCE表を含む)もarticle全文を
    含まないこと(既存assert_no_full_article_bodyを流用)。"""

    @classmethod
    def setUpClass(cls):
        cls.dbs = ing.load_all_group1_dbs()

    def test_v2_wrap_prompt_does_not_contain_full_article_body(self):
        if not os.path.exists(TWINS_A2_PATH):
            self.skipTest("article fixture not present")
        article_text = open(TWINS_A2_PATH, encoding="utf-8").read()
        s1r = runner.run_stage1_and_shortlist_v2_wrap(article_text, self.dbs, "Digital Twins")
        shortlist_info = s1r["shortlist_info"]
        id_result = contract.assign_candidate_ids(shortlist_info["shortlist"])
        static_instructions = base.extract_static_instructions(
            __import__("er003_b1_p2_keywords").load_prompt_template())
        message = contract.build_lightweight_user_message(
            "Digital Twins", id_result["shortlist_with_ids"], shortlist_info["sentence_reference"],
            static_instructions, display_type_fn=run5._display_type_v2,
            evidence_fn=run5._compact_evidence_string_v2)
        base.assert_no_full_article_body(message, article_text)

    def test_prompt_contains_candidate_ids_and_no_old_copy_instruction(self):
        if not os.path.exists(TWINS_A2_PATH):
            self.skipTest("article fixture not present")
        article_text = open(TWINS_A2_PATH, encoding="utf-8").read()
        s1r = runner.run_stage1_and_shortlist_v2_wrap(article_text, self.dbs, "Digital Twins")
        shortlist_info = s1r["shortlist_info"]
        id_result = contract.assign_candidate_ids(shortlist_info["shortlist"])
        static_instructions = base.extract_static_instructions(
            __import__("er003_b1_p2_keywords").load_prompt_template())
        message = contract.build_lightweight_user_message(
            "Digital Twins", id_result["shortlist_with_ids"], shortlist_info["sentence_reference"],
            static_instructions, display_type_fn=run5._display_type_v2,
            evidence_fn=run5._compact_evidence_string_v2)
        self.assertIn("id: C1", message)
        self.assertIn("source_candidate_id", message)
        self.assertNotIn("そのまま(一字一句、改変せず)使用", message)


class PrepareArticleIntegrationTests(unittest.TestCase):
    """prepare_article(API呼び出しなしの前半部分)が候補ID/promptを正しく
    組み立てること。"""

    @classmethod
    def setUpClass(cls):
        cls.dbs = ing.load_all_group1_dbs()

    def test_prepare_article_v2_twins_a2(self):
        if not os.path.exists(TWINS_A2_PATH):
            self.skipTest("article fixture not present")
        path, process, title_override = runner.X_ADDITIONAL_6_RAW["twins_a2"]
        prepared = runner.prepare_article("twins_a2", path, process, title_override, self.dbs, "v2")
        self.assertEqual(prepared["wrap_version"], "v2")
        self.assertGreater(len(prepared["id_result"]["candidate_ids"]), 0)
        self.assertIn("id: C1", prepared["lightweight_message"])


if __name__ == "__main__":
    unittest.main()
