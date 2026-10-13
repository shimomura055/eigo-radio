# -*- coding: utf-8 -*-
"""FAMILY-XZ-M2P0-N01-PRODUCTION-COMPLETION-01 是正①: 候補ID方式itemの末尾機能語spanを原文内で拡張する
(Rule7は緩和しない)ことのRegression。API呼出なし。"""
import copy
import unittest

import er003_key_words_canonicalization as kc

SENT = 'However, "about nine months" is an estimate based on interviews'


def _item(span, sentence, contract="candidate_id_v1", rank=5, **extra):
    it = {"rank": rank, "display_phrase": span, "source_span": span, "source_sentence": sentence}
    if contract:
        it["source_reference_contract"] = contract
    it.update(extra)
    return it


def _llm_item(rank, key_phrase, reason="restore_semantic_complement", changed=True):
    d = {"rank": rank, "key_phrase": key_phrase, "changed_from_display_phrase": changed,
         "normalization_reason": reason, "reasoning": "x"}
    for f in kc.QA_FIELDS:
        d[f] = "PASS"
    return d


class DanglingSpanExpansionTest(unittest.TestCase):
    def test_based_on_expands_to_interviews(self):
        self.assertEqual(kc.expand_dangling_source_span(_item("based on", SENT)), "based on interviews")

    def test_similar_dangling_tails(self):
        self.assertEqual(kc.expand_dangling_source_span(
            _item("urge to", "I feel the urge to watch another video, again.")), "urge to watch")
        self.assertEqual(kc.expand_dangling_source_span(
            _item("look at", "We look at the data again")), "look at the data")
        self.assertEqual(kc.expand_dangling_source_span(
            _item("rely on", "Firms rely on, say, data.")), "rely on")


    def test_complete_spans_untouched(self):
        for span, sent in [("right away", "But a shop's price may not change right away"),
                           ("prices up", "A person said three costs had pushed prices up"),
                           ("raw-bean", "The raw-bean price fell")]:
            self.assertEqual(kc.expand_dangling_source_span(_item(span, sent)), span)

    def test_punctuation_stops_expansion(self):
        self.assertEqual(kc.expand_dangling_source_span(_item("based on", "It was based on.")), "based on")
        self.assertEqual(kc.expand_dangling_source_span(_item("based on", "It was based on, however, data.")), "based on")

    def test_span_not_in_sentence_untouched(self):
        self.assertEqual(kc.expand_dangling_source_span(_item("based on", "Nothing relevant here")), "based on")

    def test_strategy_l_items_untouched(self):
        # source_reference_contractを持たない(Strategy L等)itemは入力がバイト同一
        it = _item("based on", SENT, contract=None)
        self.assertEqual(kc.expand_dangling_source_span(it), "based on")
        before = copy.deepcopy([it])
        self.assertEqual(kc.canonicalization_view_items([it]), before)

    def test_view_does_not_mutate_original(self):
        it = _item("based on", SENT)
        orig = copy.deepcopy(it)
        view = kc.canonicalization_view_items([it])
        self.assertEqual(it, orig)
        self.assertEqual(view[0]["source_span"], "based on interviews")
        self.assertEqual(view[0]["source_span_original"], "based on")


class Rule7StillStrictTest(unittest.TestCase):
    def test_incident_case_now_valid_and_rule7_not_relaxed(self):
        items = [_item("based on", SENT)]
        resp = {"items": [_llm_item(5, "based on interviews")]}
        # 拡張span経由で実際に不整合が解消する
        self.assertNotEqual(kc.validate_canonicalization_response(resp, items)["status"], "CANONICALIZATION_INVALID")
        # 同じ応答が、拡張前spanの検証(従来)ではINVALIDだったこと(再現確認)
        old = kc.validate_canonicalization_item("based on interviews", "based on", "based on",
                                                normalization_reason="restore_semantic_complement")
        self.assertFalse(old["ok"])

    def test_phrase_outside_expanded_span_still_invalid(self):
        items = [_item("based on", SENT)]
        for bad in ("based on the interviews", "based on interviews with experts", "relying on interviews"):
            resp = {"items": [_llm_item(5, bad)]}
            self.assertEqual(kc.validate_canonicalization_response(resp, items)["status"],
                             "CANONICALIZATION_INVALID", bad)

    def test_strategy_l_item_still_strict(self):
        items = [_item("based on", SENT, contract=None)]
        resp = {"items": [_llm_item(5, "based on interviews")]}
        self.assertEqual(kc.validate_canonicalization_response(resp, items)["status"], "CANONICALIZATION_INVALID")

    def test_prompt_message_carries_expanded_span_only_for_candidate_id_items(self):
        tmpl = "{article_text}\n{items_json}"
        msg = kc.build_user_message([_item("based on", SENT)], SENT, template=tmpl)
        self.assertIn('"source_span": "based on interviews"', msg)
        msg2 = kc.build_user_message([_item("based on", SENT, contract=None)], SENT, template=tmpl)
        self.assertIn('"source_span": "based on"', msg2)

    def test_merge_keeps_original_source_span_and_records_expanded(self):
        items = [_item("based on", SENT)]
        merged = kc.merge_canonicalization_result(items, [_llm_item(5, "based on interviews")])
        m = merged["items"][0]
        self.assertEqual(m["source_span"], "based on")
        self.assertEqual(m["canonicalization_source_span"], "based on interviews")
        self.assertEqual(m["key_phrase"], "based on interviews")
        merged2 = kc.merge_canonicalization_result([_item("right away", "x right away")],
                                                   [_llm_item(5, "right away", reason="none", changed=False)])
        self.assertNotIn("canonicalization_source_span", merged2["items"][0])


class CompletionO2LeftEndGuardTest(unittest.TestCase):
    """委任_02 OF-X1/X2: 左端ガード・語境界・追加test。"""

    def _status(self, span, sentence, key_phrase, **extra):
        it = _item(span, sentence)
        it.update(extra)
        return kc.validate_canonicalization_response({"items": [_llm_item(5, key_phrase)]}, [it])["status"]

    def test_of_x1_complement_only_is_invalid(self):
        for bad in ("interviews", "on interviews"):
            self.assertEqual(self._status("based on", SENT, bad), "CANONICALIZATION_INVALID", bad)

    def test_of_x1_right_completion_still_valid(self):
        self.assertNotEqual(self._status("based on", SENT, "based on interviews"), "CANONICALIZATION_INVALID")
        self.assertNotEqual(self._status("the urge to", "I feel the urge to watch another video.", "urge to watch"),
                            "CANONICALIZATION_INVALID")
        self.assertNotEqual(self._status("urge to", "I feel the urge to watch another video.", "urge to watch"),
                            "CANONICALIZATION_INVALID")

    def test_of_x1_within_original_span_unchanged_behaviour(self):
        # 原span内に収まるkey_phraseは従来どおり受理(拡張の有無に影響されない)
        self.assertNotEqual(self._status("based on", SENT, "based on"), "CANONICALIZATION_INVALID")

    def test_of_x2_word_boundary(self):
        it = _item("in the", "The firm said within the report that it is in the market now")
        self.assertEqual(kc.expand_dangling_source_span(it), "in the market")
        it2 = _item("in the", "It is within the report only")
        self.assertEqual(kc.expand_dangling_source_span(it2), "in the")  # 'within the'へ誤一致しない

    def test_of_x2_repeated_occurrence(self):
        same = _item("based on", "It is based on data, and also based on data.")
        self.assertEqual(kc.expand_dangling_source_span(same), "based on data")
        amb = _item("based on", "It is based on data, and also based on experts.")
        self.assertEqual(kc.expand_dangling_source_span(amb), "based on")  # 曖昧なら拡張しない(fail-safe)

    def test_three_function_words_stop_at_three(self):
        it = _item("rely on", "We rely on the of in data here")
        self.assertEqual(kc.expand_dangling_source_span(it), "rely on the of in")

    def test_span_corrected_in_restore_item(self):
        it = _item("based on", SENT, source_span_corrected_in_restore=True)
        out = kc.canonicalization_view_items([it])[0]
        self.assertEqual(out["source_span"], "based on interviews")
        self.assertTrue(out["source_span_corrected_in_restore"])
        merged = kc.merge_canonicalization_result([it], [_llm_item(5, "based on interviews")])
        self.assertEqual(merged["items"][0]["source_span"], "based on")

    def test_topic_role_item(self):
        it = _item("based on", SENT, key_phrase_role="topic")
        merged = kc.merge_canonicalization_result([it], [_llm_item(5, "based on interviews")])
        self.assertEqual(merged["items"][0]["key_phrase_role"], "topic")
        self.assertEqual(merged["items"][0]["canonicalization_source_span"], "based on interviews")
        self.assertEqual(self._status("based on", SENT, "on interviews", key_phrase_role="topic"),
                         "CANONICALIZATION_INVALID")


if __name__ == "__main__":
    unittest.main()
