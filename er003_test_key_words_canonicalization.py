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
    """構造的安全性のみを検査する決定的validator(意味判断はしない)。
    2026-08-08(ER-003-KP-02): 第3引数source_spanを追加。key_phraseが
    display_phraseと無変更ならsource_spanを問わず安全、変更する場合は
    source_span内の連続部分文字列であることを要求する。"""

    def test_accepts_identical_phrase(self):
        result = kc.validate_canonicalization_item("opt out", "opt out", "opt out")
        self.assertTrue(result["ok"], result["reasons"])

    def test_accepts_leading_article_removed(self):
        result = kc.validate_canonicalization_item("urge to", "the urge to", "the urge to")
        self.assertTrue(result["ok"], result["reasons"])

    def test_accepts_word_restored_from_source_span(self):
        """KP-02の主眼: display_phraseにはない"watch"を、より広いsource_span
        から復元したkey_phraseを構造的に受理する。"""
        result = kc.validate_canonicalization_item("urge to watch", "the urge to", "the urge to watch")
        self.assertTrue(result["ok"], result["reasons"])

    def test_unchanged_item_accepted_even_if_display_phrase_not_in_source_span(self):
        """A01の"take a player off"(display_phrase)は元のsource_span
        "took off players"と文字列として一致しない(語順・活用が異なる、
        方式L選定時点の正規化)。無変更であれば、source_spanとの関係を
        問わず安全とみなす。"""
        result = kc.validate_canonicalization_item("take a player off", "take a player off", "took off players")
        self.assertTrue(result["ok"], result["reasons"])

    def test_rejects_empty_key_phrase(self):
        result = kc.validate_canonicalization_item("", "opt out", "opt out")
        self.assertFalse(result["ok"])

    def test_rejects_fabricated_phrase_not_substring(self):
        """Rule7: source_spanにもdisplay_phraseにも存在しない別の辞書形を
        勝手に生成した場合、構造的に不合格とする(内容判断ではなく、
        存在しない文字列の検出)。"""
        result = kc.validate_canonicalization_item("ask out", "opt out", "opt out")
        self.assertFalse(result["ok"])
        self.assertTrue(any("連続部分文字列でもない" in r for r in result["reasons"]))

    def test_rejects_word_not_present_in_source_span_even_if_changed(self):
        """display_phraseから変更する場合、source_spanの範囲を超えて
        新しい語を生成することは許されない。"""
        result = kc.validate_canonicalization_item(
            "urge to watch videos", "the urge to", "the urge to watch")
        self.assertFalse(result["ok"])

    def test_rejects_too_many_words(self):
        result = kc.validate_canonicalization_item(
            "the small extra government step plan today",
            "the small extra government step plan today",
            "the small extra government step plan today")
        self.assertFalse(result["ok"])

    def test_rejects_finite_auxiliary(self):
        result = kc.validate_canonicalization_item("is stopped", "is stopped", "is stopped")
        self.assertFalse(result["ok"])

    def test_case_and_whitespace_insensitive_substring_match(self):
        result = kc.validate_canonicalization_item("Urge  To", "the urge to", "the urge to")
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

    def test_qa_fail_verdict_yields_review_required_not_invalid(self):
        """qa_*が1件でもFAILの場合、構造validatorが合格していても自動
        PASSにはせず、REVIEW_REQUIREDとして扱う(2026-08-08ユーザー受入
        時の修正、自動再試行は不要・人間確認後に採用可能とする)。"""
        response = self._good_response()
        response["items"][0]["qa_listening_blocker_value_preserved"] = "FAIL"
        result = kc.validate_canonicalization_response(response, GOOD_ITEMS)
        self.assertEqual(result["status"], "CANONICALIZATION_REVIEW_REQUIRED")
        self.assertEqual(result["items_requiring_review"], [1])

    def test_qa_all_pass_across_all_items_yields_pass(self):
        result = kc.validate_canonicalization_response(self._good_response(), GOOD_ITEMS)
        self.assertEqual(result["items_requiring_review"], [])

    def test_structural_failure_takes_precedence_over_qa_fail(self):
        """同じ項目で構造違反とQA FAILが両方あっても、ステータスは
        INVALID(構造不合格が優先)。"""
        response = self._good_response()
        response["items"][0]["key_phrase"] = "desire for"  # Rule5違反
        response["items"][0]["qa_listening_blocker_value_preserved"] = "FAIL"
        result = kc.validate_canonicalization_response(response, GOOD_ITEMS)
        self.assertEqual(result["status"], "CANONICALIZATION_INVALID")


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

    def test_all_pass_qa_yields_pass_overall_status(self):
        canon_items = [
            {"rank": 1, "key_phrase": "urge to", "changed_from_display_phrase": True,
             "reasoning": "R", **_good_qa()},
            {"rank": 2, "key_phrase": "opt out", "changed_from_display_phrase": False,
             "reasoning": "R2", **_good_qa()},
        ]
        merged = kc.merge_canonicalization_result(GOOD_ITEMS, canon_items)
        self.assertEqual(merged["overall_status"], "PASS")
        for item in merged["items"]:
            self.assertEqual(item["qa_overall_status"], "PASS")

    def test_one_qa_fail_yields_review_required_overall_and_item_status(self):
        qa_with_fail = _good_qa()
        qa_with_fail["qa_listening_blocker_value_preserved"] = "FAIL"
        canon_items = [
            {"rank": 1, "key_phrase": "urge to", "changed_from_display_phrase": True,
             "reasoning": "R", **qa_with_fail},
            {"rank": 2, "key_phrase": "opt out", "changed_from_display_phrase": False,
             "reasoning": "R2", **_good_qa()},
        ]
        merged = kc.merge_canonicalization_result(GOOD_ITEMS, canon_items)
        by_rank = {it["rank"]: it for it in merged["items"]}
        self.assertEqual(merged["overall_status"], "REVIEW_REQUIRED")
        self.assertEqual(by_rank[1]["qa_overall_status"], "REVIEW_REQUIRED")
        self.assertEqual(by_rank[2]["qa_overall_status"], "PASS")


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


    def test_qa_fail_response_returns_review_required_without_retry(self):
        """QA FAILを含む応答は、構造的には合格のためREVIEW_REQUIREDで
        即座に確定し、自動再試行はしない(再試行しても解決しないため)。"""
        qa_with_fail = _good_qa()
        qa_with_fail["qa_listening_blocker_value_preserved"] = "FAIL"
        raw = json.dumps({
            "items": [
                {"rank": 1, "key_phrase": "urge to", "changed_from_display_phrase": True,
                 "reasoning": "R", **qa_with_fail},
                {"rank": 2, "key_phrase": "opt out", "changed_from_display_phrase": False,
                 "reasoning": "R2", **_good_qa()},
            ]
        })
        call_count = {"n": 0}

        class FakeResponse:
            model = kc.SELECTOR_MODEL
            output_text = raw
            id = "resp_fake_review"

        class CountingClient:
            class responses:
                @staticmethod
                def create(**kwargs):
                    call_count["n"] += 1
                    return FakeResponse()

        def make_factory():
            return kc.make_canonicalization_fn("dummy", client=CountingClient())

        parsed, status, attempts, model_id, response_id = kc.run_canonicalization_gate(
            make_factory, GOOD_ITEMS, max_attempts=2)
        self.assertEqual(status, "CANONICALIZATION_REVIEW_REQUIRED")
        self.assertEqual(call_count["n"], 1, "REVIEW_REQUIREDは自動再試行してはならない")
        self.assertEqual(len(attempts), 1)


class NoBlacklistOrHardcodeImplementationTests(unittest.TestCase):
    """Rule7: 個別語句ハードコード('urge to'専用例外等)や、記事のみの
    ブラックリスト実装で解決していないことの構造的な保証。"""

    def test_decision_logic_has_no_hardcoded_urge_to_special_case(self):
        """判定ロジック本体(validate_canonicalization_item/_response、
        merge_canonicalization_result)に'urge to'専用の分岐がないことを
        確認する。モジュール冒頭のコメント(KP-02修正の経緯説明としての
        具体例)はここでは対象外とする(コードの条件分岐ではなく、人間
        向けの説明文であるため)。"""
        import inspect
        for fn in (kc.validate_canonicalization_item, kc.validate_canonicalization_response,
                  kc.merge_canonicalization_result):
            source = inspect.getsource(fn)
            self.assertNotIn('"urge to"', source, msg=f"{fn.__name__}にハードコードあり")
            self.assertNotIn("'urge to'", source, msg=f"{fn.__name__}にハードコードあり")

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
    def test_a01_five_existing_items_have_unchanged_values(self):
        """A01は方式L選定時点で既に最小単位化済みのため、canonicalization
        工程を通しても5件とも「値」は変化しないはず(回帰確認)。KP-02時点
        では、rank2("take a player off")がsource_spanとの文字列不一致
        (時制正規化のため)を理由にqa_traceable_contiguous_spanがFAILと
        自己申告され、REVIEW_REQUIREDとなることを許容する(値自体は
        正しく無変更)。"""
        with open("er003_output/b1_p2/A01/keywords_canonicalized.json", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(len(data["items"]), 5)
        for item in data["items"]:
            self.assertEqual(item["key_phrase"], item["display_phrase"],
                             f"rank {item['rank']}が意図せず変更されている: {item}")
            self.assertFalse(item["changed_from_display_phrase"])
        self.assertIn(data["overall_status"], ("PASS", "REVIEW_REQUIRED"))

    @unittest.skipUnless(os.path.exists("er003_output/b1_p2/A02/keywords_canonicalized.json"),
                         "real API output not present in this environment")
    def test_a02_urge_to_restores_watch_and_others_unchanged(self):
        """KP-02の期待結果: "the urge to"は"urge to watch"へ(source_spanから
        "watch"を復元)、他4件("personalized feed"含む)は無変更。"""
        with open("er003_output/b1_p2/A02/keywords_canonicalized.json", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(len(data["items"]), 5)
        self.assertEqual(data["overall_status"], "PASS")

        urge_item = next(it for it in data["items"] if it["display_phrase"] == "the urge to")
        self.assertEqual(urge_item["key_phrase"], "urge to watch")
        self.assertEqual(urge_item["used_form"], "urge to watch")
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

    @unittest.skipUnless(os.path.exists("er003_output/kp02_over_minimization_fixtures/keywords_canonicalized.json"),
                         "real API output not present in this environment")
    def test_over_minimization_fixtures_keep_necessary_context(self):
        """ER-003-KP-02: source_spanから語を削りすぎて意味を欠いた断片に
        しないことの実LLM検証。"the urge to watch"→"urge to watch"、
        "the risk of losing jobs"→"risk of losing jobs"のように、
        意味理解に必要な語(動詞・目的語)は保持されるはず。"struggle to
        pay"・"pressure to resign"は元々十分な形なので無変更のはず。"""
        with open("er003_output/kp02_over_minimization_fixtures/keywords_canonicalized.json",
                 encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data.get("data_kind"), "ALGORITHM_TEST_ONLY_NOT_PRODUCTION")
        by_display = {it["display_phrase"]: it for it in data["items"]}

        # 過剰短縮していないこと("struggle to"/"risk of"/"pressure to"
        # のような、目的語・補語を欠いた断片まで削られていないか)
        for item in data["items"]:
            self.assertGreaterEqual(len(item["key_phrase"].split()), 2,
                                    f"{item['display_phrase']!r}が単独では意味の薄い1語まで削られている: {item}")

        # "the risk of losing jobs" は先頭のtheが除去されても"losing jobs"
        # まで保持されるはず("risk of"だけへの過剰短縮は不可)
        risk_item = by_display["the risk of losing jobs"]
        self.assertIn("losing", risk_item["key_phrase"].lower())
        self.assertIn("jobs", risk_item["key_phrase"].lower())

        # 既に必要十分な形は無変更のはず
        pressure_item = by_display["pressure to resign"]
        self.assertEqual(pressure_item["key_phrase"], "pressure to resign")


if __name__ == "__main__":
    unittest.main()
