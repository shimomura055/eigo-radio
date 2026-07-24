# ============================================================
# er003_test_b1_p2.py
# ER-003-B1-P2: A01 B1 Key Words選定・統合Listening Preview 3案のテスト
# ============================================================
# 実API・Web検索は一切行わない。すべてモック・既存成果物の読み込みのみ。
#
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er003_test_b1_p2 -v

import json
import os
import unittest

B1_P2_OUTPUT_DIR = "er003_output/b1_p2/A01"

import er003_b1_p2_keywords as bk
import er003_b1_p2_preview as bp
import er003_key_words_production as prod


def make_selection_item(rank, phrase, gloss, sentence, span=None):
    return {
        "rank": rank, "display_phrase": phrase, "source_span": span or phrase,
        "source_sentence": sentence, "ja_gloss": gloss, "phrase_type": "technical_term",
        "normalization_type": "none", "normalization_note": "note", "selection_reason": "reason",
        "listening_difficulty_reason": "difficulty reason", "inference_transparency": "LOW",
        "topic_exposure_dependency": "HIGH", "comprehension_impact": "HIGH",
        "figurative_or_emotional_value": "LOW", "spoiler_risk": "LOW",
        "portfolio_category": "domain_expression", "portfolio_substitution": False,
        "portfolio_substitution_reason": "reason",
    }


GOOD_B1_ARTICLE = (
    "# Title\n\nEngland and Argentina met in Atlanta. Neither team had a shot on target "
    "before the break. Then stoppage time began. Messi crossed the ball to a substitute. "
    "The captain made two assists that night. England took off players to defend."
)

FIVE_ITEMS = [
    make_selection_item(1, "shot on target", "枠内シュート", "Neither team had a shot on target before the break.",
                        span="shot on target"),
    make_selection_item(2, "stoppage time", "アディショナルタイム", "Then stoppage time began.",
                        span="stoppage time"),
    make_selection_item(3, "substitute", "途中出場選手", "Messi crossed the ball to a substitute.",
                        span="substitute"),
    make_selection_item(4, "make an assist", "アシストを記録する", "The captain made two assists that night.",
                        span="made two assists"),
    make_selection_item(5, "take off a player", "選手を交代させる", "England took off players to defend.",
                        span="took off players"),
]


class KeywordsModuleReuseTests(unittest.TestCase):

    def test_reuses_p2i_production_model_and_effort(self):
        self.assertEqual(bk.SELECTOR_MODEL, prod.SELECTOR_MODEL)
        self.assertEqual(bk.SELECTOR_REASONING_EFFORT, prod.SELECTOR_REASONING_EFFORT)
        self.assertEqual(bk.SELECTOR_DEVELOPER_MESSAGE, prod.SELECTOR_DEVELOPER_MESSAGE)

    def test_reuses_p2i_schema_identity(self):
        self.assertIs(bk.SELECTOR_JSON_SCHEMA, prod.SELECTOR_JSON_SCHEMA)

    def test_reuses_p2i_runtime_metadata_and_validator(self):
        self.assertIs(bk.attach_runtime_metadata, prod.attach_runtime_metadata)
        self.assertIs(bk.validate_selection, prod.validate_production_selection)

    def test_strategy_is_l(self):
        self.assertEqual(bk.STRATEGY_ID, "L")

    def test_max_attempts_is_1_no_auto_regeneration(self):
        self.assertEqual(bk.MAX_SELECTOR_ATTEMPTS, 1)

    def test_article_id_is_a01(self):
        self.assertEqual(bk.ARTICLE_ID, "A01")

    def test_b1_article_path_points_to_p1_output_not_b2(self):
        self.assertIn("b1_p1", bk.B1_ARTICLE_PATH)
        self.assertNotIn("b2", bk.B1_ARTICLE_PATH.lower().replace("b1_p1", ""))


class KeywordsPromptTests(unittest.TestCase):

    def test_template_has_single_b1_article_placeholder(self):
        template = bk.load_prompt_template()
        self.assertIn("{approved_b1_article}", template)
        self.assertNotIn("{approved_summary}", template)
        self.assertNotIn("{approved_b2_article}", template)

    def test_build_user_message_substitutes_b1_text(self):
        msg = bk.build_user_message("B1_ARTICLE_MARKER")
        self.assertIn("B1_ARTICLE_MARKER", msg)
        self.assertNotIn("{approved_b1_article}", msg)


class KeywordsGateTests(unittest.TestCase):

    def _pass_factory(self, items=None):
        items = items if items is not None else FIVE_ITEMS

        def factory():
            def fn():
                return json.dumps({"items": items}), prod.SELECTOR_MODEL, "resp_fake_1"
            return fn
        return factory

    def _fail_factory(self):
        def factory():
            def fn():
                raise RuntimeError("simulated technical failure")
            return fn
        return factory

    def test_success_on_first_attempt(self):
        parsed, status, attempts, model_id, response_id = bk.run_selection_gate(
            self._pass_factory(), GOOD_B1_ARTICLE)
        self.assertEqual(status, "KEY_WORDS_STRUCTURE_PASS")
        self.assertEqual(len(attempts), 1)
        self.assertEqual(parsed["article_id"], "A01")
        self.assertEqual(parsed["strategy_id"], "L")

    def test_technical_failure_does_not_retry(self):
        """自動再実行なし(max_attempts=1)の直接検証。"""
        parsed, status, attempts, model_id, response_id = bk.run_selection_gate(
            self._fail_factory(), GOOD_B1_ARTICLE)
        self.assertEqual(status, "TECHNICAL_GENERATION_FAILED")
        self.assertEqual(len(attempts), 1)

    def test_structure_invalid_does_not_retry(self):
        bad_items = FIVE_ITEMS[:4]  # exactly-5違反
        parsed, status, attempts, model_id, response_id = bk.run_selection_gate(
            self._pass_factory(bad_items), GOOD_B1_ARTICLE)
        self.assertEqual(status, "KEY_WORDS_STRUCTURE_INVALID")
        self.assertEqual(len(attempts), 1)


class KeywordsExportTests(unittest.TestCase):

    def setUp(self):
        self.parsed = prod.attach_runtime_metadata({"items": FIVE_ITEMS}, "A01", "L")

    def test_selected_json_schema_matches_spec(self):
        result = bk.build_selected_keywords_json(self.parsed)
        self.assertEqual(result["article_id"], "A01")
        self.assertEqual(result["strategy_id"], "L")
        self.assertEqual(result["source_level"], "B1")
        self.assertEqual(len(result["items"]), 5)
        for item in result["items"]:
            self.assertIn("rank", item)
            self.assertIn("canonical_english", item)
            self.assertIn("japanese_gloss", item)
            self.assertIn("source_evidence", item)

    def test_selected_json_items_are_rank_ordered(self):
        result = bk.build_selected_keywords_json(self.parsed)
        ranks = [item["rank"] for item in result["items"]]
        self.assertEqual(ranks, sorted(ranks))

    def test_reading_copy_lists_all_5_items(self):
        selected = bk.build_selected_keywords_json(self.parsed)
        copy_text = bk.build_selected_keywords_reading_copy(selected)
        for item in FIVE_ITEMS:
            self.assertIn(item["display_phrase"], copy_text)
            self.assertIn(item["ja_gloss"], copy_text)


# ============================================================
# Part B: Preview
# ============================================================
SELECTED_JSON = {
    "article_id": "A01", "strategy_id": "L", "source_level": "B1",
    "items": [
        {"rank": 1, "canonical_english": "shot on target", "japanese_gloss": "枠内シュート",
         "source_evidence": "Neither team had a shot on target before the break."},
        {"rank": 2, "canonical_english": "stoppage time", "japanese_gloss": "アディショナルタイム",
         "source_evidence": "Then stoppage time began."},
        {"rank": 3, "canonical_english": "substitute", "japanese_gloss": "途中出場選手",
         "source_evidence": "Messi crossed the ball to a substitute."},
        {"rank": 4, "canonical_english": "make an assist", "japanese_gloss": "アシストを記録する",
         "source_evidence": "The captain made two assists that night."},
        {"rank": 5, "canonical_english": "take off a player", "japanese_gloss": "選手を交代させる",
         "source_evidence": "England took off players to defend."},
    ],
}


def make_used_form(rank, canonical, used, gloss):
    return {"rank": rank, "canonical_english": canonical, "used_form": used, "japanese_gloss_used": gloss}


GOOD_PATTERN_TEXT = (
    "アトランタでの一戦は前半、枠内シュート、shot on target、がゼロのまま静かに進んだ。"
    "やがてアディショナルタイム、stoppage time、に入ると空気が一変する。"
    "途中出場選手、substitute、が交代で入り、流れを変えた。"
    "主将はこの夜アシストを記録する、made an assist、動きを見せ、選手を交代させる、took off a player、判断も勝負の分かれ目になった。"
)


def make_good_pattern(pattern_id):
    return {
        "pattern_id": pattern_id,
        "text": GOOD_PATTERN_TEXT,
        "used_forms": [
            make_used_form(1, "shot on target", "shot on target", "枠内シュート"),
            make_used_form(2, "stoppage time", "stoppage time", "アディショナルタイム"),
            make_used_form(3, "substitute", "substitute", "途中出場選手"),
            make_used_form(4, "make an assist", "made an assist", "アシストを記録する"),
            make_used_form(5, "take off a player", "took off a player", "選手を交代させる"),
        ],
    }


class PreviewPromptTests(unittest.TestCase):

    def test_template_has_required_placeholders(self):
        template = bp.load_prompt_template()
        self.assertIn("{keywords_block}", template)
        self.assertIn("{approved_b1_article}", template)

    def test_template_mentions_all_three_pattern_purposes(self):
        template = bp.load_prompt_template()
        self.assertIn("Pattern A", template)
        self.assertIn("Pattern B", template)
        self.assertIn("Pattern C", template)
        self.assertIn("Story", template)
        self.assertIn("Comprehension", template)
        self.assertIn("Keyword Salience", template)

    def test_keywords_block_contains_all_5_items(self):
        block = bp.build_keywords_block(SELECTED_JSON)
        for item in SELECTED_JSON["items"]:
            self.assertIn(item["canonical_english"], block)
            self.assertIn(item["japanese_gloss"], block)

    def test_build_user_message_substitutes_both_placeholders(self):
        msg = bp.build_preview_user_message(SELECTED_JSON, "B1_TEXT_MARKER")
        self.assertIn("B1_TEXT_MARKER", msg)
        self.assertIn("shot on target", msg)
        self.assertNotIn("{keywords_block}", msg)
        self.assertNotIn("{approved_b1_article}", msg)

    def test_prompt_never_references_b2_or_natural_source(self):
        template = bp.load_prompt_template()
        self.assertNotIn("B2", template)
        self.assertNotIn("Natural English Source", template)


class PreviewFunctionTests(unittest.TestCase):

    def test_preview_fn_has_no_web_search_and_uses_structured_output(self):
        fn = bp.make_preview_fn("dummy", client=object())
        self.assertFalse(fn.uses_web_search_tool)
        self.assertTrue(fn.uses_structured_output)
        self.assertEqual(fn.model, bp.PREVIEW_MODEL)
        self.assertEqual(fn.reasoning_effort, bp.PREVIEW_REASONING_EFFORT)

    def test_module_has_no_retry_gate(self):
        for name in dir(bp):
            self.assertNotIn("gate", name.lower(), msg=name)

    def test_fake_client_success_path(self):
        class FakeResponse:
            model = bp.PREVIEW_MODEL
            output_text = json.dumps({"patterns": [make_good_pattern(p) for p in ("A", "B", "C")]})
            id = "resp_fake_preview"

        class FakeClient:
            class responses:
                @staticmethod
                def create(**kwargs):
                    return FakeResponse()

        fn = bp.make_preview_fn("dummy", client=FakeClient())
        text, model_id, response_id = fn()
        parsed = bp.parse_preview_json(text)
        self.assertEqual(len(parsed["patterns"]), 3)

    def test_fake_client_empty_response_raises(self):
        class FakeResponse:
            model = bp.PREVIEW_MODEL
            output_text = ""
            id = "resp_fake"

        class FakeClient:
            class responses:
                @staticmethod
                def create(**kwargs):
                    return FakeResponse()

        fn = bp.make_preview_fn("dummy", client=FakeClient())
        with self.assertRaises(Exception):
            fn()

    def test_parse_rejects_wrong_pattern_count(self):
        with self.assertRaises(Exception):
            bp.parse_preview_json(json.dumps({"patterns": [make_good_pattern("A")]}))


class PreviewMachineChecksTests(unittest.TestCase):

    def test_good_pattern_passes_all_checks(self):
        pattern = make_good_pattern("A")
        result = bp.check_pattern_machine(pattern, [1, 2, 3, 4, 5], GOOD_B1_ARTICLE)
        self.assertEqual(result["status"], "ALL_CHECKS_PASS")

    def test_missing_used_form_detected(self):
        pattern = make_good_pattern("A")
        pattern["text"] = pattern["text"].replace("shot on target", "an attempt at goal")
        result = bp.check_pattern_machine(pattern, [1, 2, 3, 4, 5], GOOD_B1_ARTICLE)
        self.assertFalse(result["checks"]["all_used_forms_occur_exactly_once"])
        self.assertEqual(result["status"], "SOME_CHECKS_FAILED")

    def test_duplicate_used_form_detected(self):
        pattern = make_good_pattern("A")
        pattern["text"] = pattern["text"] + " Another shot on target came later."
        result = bp.check_pattern_machine(pattern, [1, 2, 3, 4, 5], GOOD_B1_ARTICLE)
        self.assertFalse(result["checks"]["all_used_forms_occur_exactly_once"])

    def test_explicit_score_pattern_detected(self):
        pattern = make_good_pattern("A")
        pattern["text"] = pattern["text"] + " The final score was 1-2."
        result = bp.check_pattern_machine(pattern, [1, 2, 3, 4, 5], GOOD_B1_ARTICLE)
        self.assertFalse(result["checks"]["no_explicit_score_pattern"])
        self.assertEqual(result["status"], "SOME_CHECKS_FAILED")

    def test_winner_language_detected(self):
        pattern = make_good_pattern("A")
        pattern["text"] = pattern["text"] + " Argentina won in the end."
        result = bp.check_pattern_machine(pattern, [1, 2, 3, 4, 5], GOOD_B1_ARTICLE)
        self.assertFalse(result["checks"]["no_winner_language_detected"])

    def test_sentence_count_out_of_range_detected(self):
        pattern = make_good_pattern("A")
        pattern["text"] = "One sentence only with all five terms is impossible here."
        result = bp.check_pattern_machine(pattern, [1, 2, 3, 4, 5], GOOD_B1_ARTICLE)
        self.assertFalse(result["checks"]["sentence_count_in_3_to_4"])

    def test_japanese_before_english_pass_when_gloss_precedes(self):
        pattern = make_good_pattern("A")
        result = bp.check_pattern_machine(pattern, [1, 2, 3, 4, 5], GOOD_B1_ARTICLE)
        for item in result["checks"]["per_item"]:
            self.assertIn(item["japanese_before_english"], ("PASS", "UNVERIFIABLE"))

    def test_english_before_japanese_flagged_as_fail(self):
        pattern = make_good_pattern("A")
        pattern["text"] = "shot on target、枠内シュート、が印象的だった。" + pattern["text"]
        result = bp.check_pattern_machine(pattern, [1, 2, 3, 4, 5], GOOD_B1_ARTICLE)
        rank1_item = next(it for it in result["checks"]["per_item"] if it["rank"] == 1)
        self.assertEqual(rank1_item["japanese_before_english"], "FAIL")

    def test_run_preview_machine_checks_aggregates_three_patterns(self):
        parsed = {"patterns": [make_good_pattern(p) for p in ("A", "B", "C")]}
        result = bp.run_preview_machine_checks(parsed, [1, 2, 3, 4, 5], GOOD_B1_ARTICLE)
        self.assertEqual(result["status"], "ALL_CHECKS_PASS")
        self.assertEqual(result["pattern_count"], 3)
        self.assertEqual(result["pattern_ids_present"], ["A", "B", "C"])

    def test_run_preview_machine_checks_detects_one_bad_pattern(self):
        good_a = make_good_pattern("A")
        good_b = make_good_pattern("B")
        bad_c = make_good_pattern("C")
        bad_c["text"] = bad_c["text"] + " Final score 1-2."
        parsed = {"patterns": [good_a, good_b, bad_c]}
        result = bp.run_preview_machine_checks(parsed, [1, 2, 3, 4, 5], GOOD_B1_ARTICLE)
        self.assertEqual(result["status"], "SOME_CHECKS_FAILED")
        self.assertEqual(result["per_pattern"]["C"]["status"], "SOME_CHECKS_FAILED")
        self.assertEqual(result["per_pattern"]["A"]["status"], "ALL_CHECKS_PASS")


class CandidatesMarkdownTests(unittest.TestCase):

    def test_markdown_has_three_labeled_sections_in_order(self):
        parsed = {"patterns": [make_good_pattern(p) for p in ("A", "B", "C")]}
        md = bp.build_candidates_markdown(parsed)
        idx_a = md.index("Pattern A — Story / Drama")
        idx_b = md.index("Pattern B — Comprehension / Structure")
        idx_c = md.index("Pattern C — Keyword Salience")
        self.assertLess(idx_a, idx_b)
        self.assertLess(idx_b, idx_c)

    def test_markdown_contains_full_pattern_text(self):
        parsed = {"patterns": [make_good_pattern(p) for p in ("A", "B", "C")]}
        md = bp.build_candidates_markdown(parsed)
        self.assertEqual(md.count(GOOD_PATTERN_TEXT), 3)


@unittest.skipUnless(os.path.exists(f"{B1_P2_OUTPUT_DIR}/keywords_selected.json"),
                     "real API output not present in this environment")
class RealArtifactIntegrationTests(unittest.TestCase):
    """実API実行済み成果物(A01・selector1回+preview1回)の内部整合性を
    検証する(実APIは呼ばない、保存済みファイルの読み込みのみ)。"""

    @classmethod
    def setUpClass(cls):
        with open(f"{B1_P2_OUTPUT_DIR}/keywords_selected.json", encoding="utf-8") as f:
            cls.selected = json.load(f)
        with open(f"{B1_P2_OUTPUT_DIR}/keywords_runtime_metadata.json", encoding="utf-8") as f:
            cls.kw_metadata = json.load(f)
        with open(f"{B1_P2_OUTPUT_DIR}/listening_preview_metadata.json", encoding="utf-8") as f:
            cls.preview_metadata = json.load(f)

    def test_selector_api_call_count_is_1(self):
        self.assertEqual(self.kw_metadata["api_call_count"], 1)
        self.assertEqual(self.kw_metadata["auto_regeneration_count"], 0)

    def test_selector_strategy_is_l_and_source_level_is_b1(self):
        self.assertEqual(self.selected["strategy_id"], "L")
        self.assertEqual(self.selected["source_level"], "B1")
        self.assertEqual(len(self.selected["items"]), 5)

    def test_selector_used_b1_article_not_b2(self):
        self.assertIn("b1_p1", self.kw_metadata["b1_article_path"])

    def test_preview_api_call_count_is_1(self):
        self.assertEqual(self.preview_metadata["api_call_count"], 1)
        self.assertEqual(self.preview_metadata["auto_regeneration_count"], 0)

    def test_preview_no_web_search(self):
        self.assertFalse(self.preview_metadata["web_search_tool_used"])

    def test_preview_machine_checks_recorded(self):
        self.assertIn(self.preview_metadata["machine_checks"]["status"],
                      ("ALL_CHECKS_PASS", "SOME_CHECKS_FAILED"))
        self.assertEqual(self.preview_metadata["machine_checks"]["pattern_count"], 3)

    def test_record_status_prototype_not_approved(self):
        self.assertEqual(self.preview_metadata["record_status"], "PROTOTYPE")
        self.assertEqual(self.preview_metadata["approval_status"], "NOT_APPROVED")


if __name__ == "__main__":
    unittest.main()
