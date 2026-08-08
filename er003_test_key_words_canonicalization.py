# ============================================================
# er003_test_key_words_canonicalization.py
# ER-003-KP-01: Key Phrase境界正規化のテスト
# ============================================================
# 実API・実artifactに依存する統合テストはos.path.existsでskipされる
# real-artifact integration test以外、すべてFakeClient・合成データの
# みで検証する。

import json
import os
import unittest

import er003_key_words_canonicalization as kc

GOOD_ITEMS = [
    {"rank": 1, "display_phrase": "the urge to", "source_span": "the urge to watch",
     "source_sentence": "The government hopes this small extra step will slow the urge to watch \"just one "
                         "more\" video."},
    {"rank": 2, "display_phrase": "opt out", "source_span": "opt out",
     "source_sentence": "Teenagers aged 16 and 17 could change the settings and opt out."},
]


def _good_qa():
    return {field: "PASS" for field in kc.QA_FIELDS}


class PromptBuilderTests(unittest.TestCase):
    def test_template_loads_and_contains_rules(self):
        template = kc.load_prompt_template()
        self.assertIn("{article_text}", template)
        self.assertIn("{items_json}", template)
        self.assertIn("a lot of", template)
        self.assertIn("opt out", template)

    def test_build_user_message_substitutes_article_and_items(self):
        msg = kc.build_user_message(GOOD_ITEMS, "ARTICLE_TEXT_MARKER")
        self.assertIn("ARTICLE_TEXT_MARKER", msg)
        self.assertIn("the urge to", msg)
        self.assertIn("opt out", msg)
        self.assertNotIn("{article_text}", msg)
        self.assertNotIn("{items_json}", msg)


class ValidateCanonicalizationItemTests(unittest.TestCase):
    """構造的安全性のみを検査する決定的validator(意味判断はしない)。"""

    def test_accepts_identical_phrase(self):
        result = kc.validate_canonicalization_item("opt out", "opt out")
        self.assertTrue(result["ok"], result["reasons"])

    def test_accepts_leading_article_removed(self):
        result = kc.validate_canonicalization_item("urge to", "the urge to")
        self.assertTrue(result["ok"], result["reasons"])

    def test_rejects_empty_key_phrase(self):
        result = kc.validate_canonicalization_item("", "opt out")
        self.assertFalse(result["ok"])

    def test_rejects_fabricated_phrase_not_substring(self):
        """Rule5: display_phraseに存在しない別の辞書形を勝手に生成した場合、
        構造的に不合格とする(内容判断ではなく、存在しない文字列の検出)。"""
        result = kc.validate_canonicalization_item("ask out", "opt out")
        self.assertFalse(result["ok"])
        self.assertTrue(any("連続部分文字列でない" in r for r in result["reasons"]))

    def test_rejects_too_many_words(self):
        result = kc.validate_canonicalization_item(
            "the small extra government step plan today", "the small extra government step plan today")
        self.assertFalse(result["ok"])

    def test_rejects_finite_auxiliary(self):
        result = kc.validate_canonicalization_item("is stopped", "is stopped")
        self.assertFalse(result["ok"])

    def test_case_and_whitespace_insensitive_substring_match(self):
        result = kc.validate_canonicalization_item("Urge  To", "the urge to")
        self.assertTrue(result["ok"], result["reasons"])


class ValidateCanonicalizationResponseTests(unittest.TestCase):
    def _good_response(self):
        return {
            "items": [
                {"rank": 1, "key_phrase": "urge to", "changed_from_display_phrase": True,
                 "reasoning": "先頭のtheは文脈限定のみで学習単位に不要なため除去した。", **_good_qa()},
                {"rank": 2, "key_phrase": "opt out", "changed_from_display_phrase": False,
                 "reasoning": "既に最小の自然な単位である。", **_good_qa()},
            ]
        }

    def test_good_response_passes(self):
        result = kc.validate_canonicalization_response(self._good_response(), GOOD_ITEMS)
        self.assertEqual(result["status"], "CANONICALIZATION_PASS", result)

    def test_missing_rank_fails(self):
        response = self._good_response()
        response["items"] = response["items"][:1]
        result = kc.validate_canonicalization_response(response, GOOD_ITEMS)
        self.assertEqual(result["status"], "CANONICALIZATION_INVALID")

    def test_fabricated_key_phrase_fails(self):
        response = self._good_response()
        response["items"][0]["key_phrase"] = "desire for"  # display_phraseに存在しない語
        result = kc.validate_canonicalization_response(response, GOOD_ITEMS)
        self.assertEqual(result["status"], "CANONICALIZATION_INVALID")
        self.assertTrue(any(r["reasons"] for r in result["item_reasons"]))

    def test_missing_qa_field_fails(self):
        response = self._good_response()
        del response["items"][0]["qa_standalone_natural_unit"]
        result = kc.validate_canonicalization_response(response, GOOD_ITEMS)
        self.assertEqual(result["status"], "CANONICALIZATION_INVALID")

    def test_invalid_qa_verdict_value_fails(self):
        response = self._good_response()
        response["items"][0]["qa_standalone_natural_unit"] = "MAYBE"
        result = kc.validate_canonicalization_response(response, GOOD_ITEMS)
        self.assertEqual(result["status"], "CANONICALIZATION_INVALID")

    def test_qa_fail_verdict_does_not_by_itself_invalidate(self):
        """qa_*がFAILであること自体は不合格理由にしない(自己申告として
        記録するのみ)。構造的に安全であればPASSのまま扱う。"""
        response = self._good_response()
        response["items"][0]["qa_listening_blocker_value_preserved"] = "FAIL"
        result = kc.validate_canonicalization_response(response, GOOD_ITEMS)
        self.assertEqual(result["status"], "CANONICALIZATION_PASS")


class MergeCanonicalizationResultTests(unittest.TestCase):
    def test_merge_preserves_source_span_and_sets_used_form(self):
        canon_items = [
            {"rank": 1, "key_phrase": "urge to", "changed_from_display_phrase": True,
             "reasoning": "R", **_good_qa()},
            {"rank": 2, "key_phrase": "opt out", "changed_from_display_phrase": False,
             "reasoning": "R2", **_good_qa()},
        ]
        merged = kc.merge_canonicalization_result(GOOD_ITEMS, canon_items)
        by_rank = {it["rank"]: it for it in merged["items"]}

        self.assertEqual(by_rank[1]["source_span"], "the urge to watch")
        self.assertEqual(by_rank[1]["display_phrase"], "the urge to")
        self.assertEqual(by_rank[1]["key_phrase"], "urge to")
        self.assertEqual(by_rank[1]["used_form"], "urge to")
        self.assertTrue(by_rank[1]["changed_from_display_phrase"])

        self.assertEqual(by_rank[2]["key_phrase"], "opt out")
        self.assertEqual(by_rank[2]["used_form"], "opt out")
        self.assertFalse(by_rank[2]["changed_from_display_phrase"])

    def test_used_form_always_equals_key_phrase_at_this_stage(self):
        canon_items = [{"rank": 1, "key_phrase": "urge to", "changed_from_display_phrase": True,
                        "reasoning": "R", **_good_qa()}]
        merged = kc.merge_canonicalization_result([GOOD_ITEMS[0]], canon_items)
        self.assertEqual(merged["items"][0]["used_form"], merged["items"][0]["key_phrase"])


class RunCanonicalizationGateFakeClientTests(unittest.TestCase):
    """方式L選定gate(P2/P2G)と同じFakeClientパターンで、実APIを一切
    呼ばずにgateの分岐(成功・技術的失敗・再試行)を検証する。"""

    def _good_raw_text(self):
        return json.dumps({
            "items": [
                {"rank": 1, "key_phrase": "urge to", "changed_from_display_phrase": True,
                 "reasoning": "R", **_good_qa()},
                {"rank": 2, "key_phrase": "opt out", "changed_from_display_phrase": False,
                 "reasoning": "R2", **_good_qa()},
            ]
        })

    def test_success_path_first_attempt(self):
        raw = self._good_raw_text()

        class FakeResponse:
            model = kc.SELECTOR_MODEL
            output_text = raw
            id = "resp_fake_1"

        class FakeClient:
            class responses:
                @staticmethod
                def create(**kwargs):
                    return FakeResponse()

        def make_factory():
            return kc.make_canonicalization_fn("dummy", client=FakeClient())

        parsed, status, attempts, model_id, response_id = kc.run_canonicalization_gate(make_factory, GOOD_ITEMS)
        self.assertEqual(status, "CANONICALIZATION_PASS")
        self.assertEqual(len(attempts), 1)
        self.assertEqual(model_id, kc.SELECTOR_MODEL)

    def test_technical_failure_then_success_retries_once(self):
        raw = self._good_raw_text()
        call_count = {"n": 0}

        class FakeResponse:
            model = kc.SELECTOR_MODEL
            output_text = raw
            id = "resp_fake_2"

        class FailingThenGoodClient:
            class responses:
                @staticmethod
                def create(**kwargs):
                    call_count["n"] += 1
                    if call_count["n"] == 1:
                        raise RuntimeError("simulated technical failure")
                    return FakeResponse()

        def make_factory():
            return kc.make_canonicalization_fn("dummy", client=FailingThenGoodClient())

        parsed, status, attempts, model_id, response_id = kc.run_canonicalization_gate(
            make_factory, GOOD_ITEMS, sleep_fn=lambda s: None)
        self.assertEqual(status, "CANONICALIZATION_PASS")
        self.assertEqual(len(attempts), 2)
        self.assertEqual(attempts[0]["status"], "TECHNICAL_GENERATION_FAILED")

    def test_persistent_technical_failure_stops_after_max_attempts(self):
        class AlwaysFailingClient:
            class responses:
                @staticmethod
                def create(**kwargs):
                    raise RuntimeError("always fails")

        def make_factory():
            return kc.make_canonicalization_fn("dummy", client=AlwaysFailingClient())

        parsed, status, attempts, model_id, response_id = kc.run_canonicalization_gate(
            make_factory, GOOD_ITEMS, max_attempts=2, sleep_fn=lambda s: None)
        self.assertEqual(status, "TECHNICAL_GENERATION_FAILED")
        self.assertEqual(len(attempts), 2)

    def test_model_mismatch_raises_and_counts_as_technical_failure(self):
        class FakeResponse:
            model = "some-other-model"
            output_text = "{}"
            id = "resp_fake_3"

        class FakeClient:
            class responses:
                @staticmethod
                def create(**kwargs):
                    return FakeResponse()

        def make_factory():
            return kc.make_canonicalization_fn("dummy", client=FakeClient())

        parsed, status, attempts, model_id, response_id = kc.run_canonicalization_gate(
            make_factory, GOOD_ITEMS, max_attempts=1)
        self.assertEqual(status, "TECHNICAL_GENERATION_FAILED")
        self.assertIn("CanonicalizationModelMismatchError", attempts[0]["error"])

    def test_fabricated_phrase_response_is_invalid_after_retries(self):
        bad_raw = json.dumps({
            "items": [
                {"rank": 1, "key_phrase": "desire for", "changed_from_display_phrase": True,
                 "reasoning": "R", **_good_qa()},
                {"rank": 2, "key_phrase": "opt out", "changed_from_display_phrase": False,
                 "reasoning": "R2", **_good_qa()},
            ]
        })

        class FakeResponse:
            model = kc.SELECTOR_MODEL
            output_text = bad_raw
            id = "resp_fake_4"

        class FakeClient:
            class responses:
                @staticmethod
                def create(**kwargs):
                    return FakeResponse()

        def make_factory():
            return kc.make_canonicalization_fn("dummy", client=FakeClient())

        parsed, status, attempts, model_id, response_id = kc.run_canonicalization_gate(
            make_factory, GOOD_ITEMS, max_attempts=1)
        self.assertEqual(status, "CANONICALIZATION_INVALID")


class NoBlacklistOrHardcodeImplementationTests(unittest.TestCase):
    """Rule7: 個別語句ハードコード('urge to'専用例外等)や、記事のみの
    ブラックリスト実装で解決していないことの構造的な保証。"""

    def test_module_source_has_no_hardcoded_urge_to_special_case(self):
        import inspect
        source = inspect.getsource(kc)
        # プロンプトのルール説明文中の例示としての 'urge to' はテンプレート
        # ファイル側にあり、このモジュールのPythonコード自体には出現しない。
        self.assertNotIn('"urge to"', source)
        self.assertNotIn("'urge to'", source)

    def test_validator_does_not_hardcode_article_list_for_stripping(self):
        """validate_canonicalization_itemは'the'/'a'等の冠詞リストを一切
        参照しない(構造チェックのみで、削除要否の意味判断をしない)。"""
        import inspect
        source = inspect.getsource(kc.validate_canonicalization_item)
        for article_word in ("\"the\"", "'the'", "\"a\"", "'a'", "\"an\"", "'an'"):
            self.assertNotIn(article_word, source)


class RealArtifactIntegrationTests(unittest.TestCase):
    """実API実行済み成果物の内部整合性を検証する(実APIは呼ばない、
    保存済みファイルの読み込みのみ)。"""

    @unittest.skipUnless(os.path.exists("er003_output/b1_p2/A01/keywords_canonicalized.json"),
                         "real API output not present in this environment")
    def test_a01_five_existing_items_are_unchanged_by_canonicalization(self):
        """A01は方式L選定時点で既に最小単位化済みのため、canonicalization
        工程を通しても5件とも変化しないはず(回帰確認)。"""
        with open("er003_output/b1_p2/A01/keywords_canonicalized.json", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(len(data["items"]), 5)
        for item in data["items"]:
            self.assertEqual(item["key_phrase"], item["display_phrase"],
                             f"rank {item['rank']}が意図せず変更されている: {item}")
            self.assertFalse(item["changed_from_display_phrase"])

    @unittest.skipUnless(os.path.exists("er003_output/b1_p2/A02/keywords_canonicalized.json"),
                         "real API output not present in this environment")
    def test_a02_urge_to_is_trimmed_and_others_unchanged(self):
        with open("er003_output/b1_p2/A02/keywords_canonicalized.json", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(len(data["items"]), 5)
        by_rank = {it["rank"]: it for it in data["items"]}

        urge_item = next(it for it in data["items"] if it["display_phrase"] == "the urge to")
        self.assertEqual(urge_item["key_phrase"], "urge to")
        self.assertEqual(urge_item["used_form"], "urge to")
        self.assertTrue(urge_item["changed_from_display_phrase"])

        for item in data["items"]:
            if item["display_phrase"] != "the urge to":
                self.assertEqual(item["key_phrase"], item["display_phrase"],
                                 f"rank {item['rank']}が意図せず変更されている: {item}")

    @unittest.skipUnless(os.path.exists("er003_output/kp01_negative_fixtures/keywords_canonicalized.json"),
                         "real API output not present in this environment")
    def test_negative_fixtures_fixed_expressions_are_not_broken(self):
        """Rule3: a lot of / a number of / at the same time / on the other hand /
        the same as は、canonicalization後も冠詞・限定詞を保持したまま
        (変更なし)であること。"""
        with open("er003_output/kp01_negative_fixtures/keywords_canonicalized.json", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data.get("data_kind"), "ALGORITHM_TEST_ONLY_NOT_PRODUCTION")
        fixed_expressions = {"a lot of", "a number of", "at the same time", "on the other hand", "the same as"}
        seen = set()
        for item in data["items"]:
            self.assertIn(item["display_phrase"], fixed_expressions)
            seen.add(item["display_phrase"])
            self.assertEqual(item["key_phrase"], item["display_phrase"],
                             f"固定表現が破壊されている: {item}")
        self.assertEqual(seen, fixed_expressions)


if __name__ == "__main__":
    unittest.main()
