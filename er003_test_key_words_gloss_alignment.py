# KP-GLOSS-ALIGNMENT-01 テスト(API不要、mock)
import json
import os
import tempfile
import unittest

import er003_key_words_canonicalization as kc
import er003_key_words_gloss_alignment as ga


def _merged(items):
    return {"items": items, "overall_status": "PASS"}


def _item(rank, disp, kp, gloss, beyond=False, sentence="x"):
    return {"rank": rank, "display_phrase": disp, "key_phrase": kp, "used_form": kp, "japanese_gloss": gloss,
            "japanese_gloss_tts": kc.convert_display_gloss_to_tts_text(gloss),
            "kp_extends_beyond_candidate": beyond, "gloss_review_hint": beyond,
            "changed_from_display_phrase": disp != kp, "source_sentence": sentence}


class FakeFn:
    def __init__(self, payloads, model="gpt-6-luna"):
        self.payloads = list(payloads)
        self.calls = 0
        self.model = model

    def __call__(self):
        self.calls += 1
        p = self.payloads.pop(0)
        if isinstance(p, Exception):
            raise p
        return (p if isinstance(p, str) else json.dumps(p, ensure_ascii=False)), self.model, "resp_x"


def _resp(items):
    return {"items": [{"rank": r, "current_gloss_consistent": c, "japanese_gloss": g,
                       "qa_reflects_all_key_phrase_words": q, "reasoning": "r"} for r, c, g, q in items]}


class TargetSelection(unittest.TestCase):
    def test_extended_kp_is_target(self):
        self.assertTrue(ga.kp_adds_words_beyond_display("based on", "based on interviews"))

    def test_unchanged_not_target(self):
        self.assertFalse(ga.kp_adds_words_beyond_display("right away", "right away"))

    def test_inflection_not_target(self):
        self.assertFalse(ga.kp_adds_words_beyond_display("give back", "gave back"))

    def test_person_generalization_not_target(self):
        self.assertFalse(ga.kp_adds_words_beyond_display("catch their breath", "catch one's breath"))
        self.assertFalse(ga.kp_adds_words_beyond_display("give my word", "give one's word"))

    def test_article_removal_not_target(self):
        self.assertFalse(ga.kp_adds_words_beyond_display("the Strait", "Strait"))

    def test_flag_makes_target(self):
        m = _merged([_item(1, "x y", "x y", "g", beyond=True)])
        self.assertEqual(len(ga.select_alignment_targets(m["items"])), 1)

    def test_no_targets_no_api(self):
        m = _merged([_item(1, "right away", "right away", "すぐに")])
        called = []
        r = ga.align_glosses(m, "art", lambda msg: called.append(1))
        self.assertEqual(r["status"], "NO_TARGETS")
        self.assertIs(r["merged"], m)
        self.assertFalse(called)


class Alignment(unittest.TestCase):
    def setUp(self):
        self.m = _merged([_item(1, "right away", "right away", "すぐに"),
                          _item(2, "based on", "based on interviews", "～をもとにした", beyond=True)])

    def test_realign(self):
        fn = FakeFn([_resp([(2, False, "インタビューをもとにした", "PASS")])])
        r = ga.align_glosses(self.m, "art", lambda msg: fn)
        it = r["merged"]["items"][1]
        self.assertEqual(r["status"], "ALIGN_PASS")
        self.assertEqual(it["japanese_gloss"], "インタビューをもとにした")
        self.assertEqual(it["japanese_gloss_tts"], "インタビューをもとにした")
        self.assertEqual(it["gloss_alignment"]["status"], "GLOSS_REALIGNED")
        self.assertEqual(it["gloss_alignment"]["original_japanese_gloss"], "～をもとにした")
        self.assertEqual(it["key_phrase"], "based on interviews")
        # 対象外itemは無変更
        self.assertEqual(r["merged"]["items"][0], self.m["items"][0])
        # 元mergedは変更しない
        self.assertEqual(self.m["items"][1]["japanese_gloss"], "～をもとにした")
        self.assertEqual(fn.calls, 1)

    def test_already_consistent(self):
        fn = FakeFn([_resp([(2, True, "～をもとにした", "PASS")])])
        r = ga.align_glosses(self.m, "art", lambda msg: fn)
        self.assertEqual(r["merged"]["items"][1]["gloss_alignment"]["status"], "GLOSS_ALREADY_CONSISTENT")

    def test_retry_then_pass(self):
        fn = FakeFn([_resp([(2, False, "インタビュー（取材）をもとにした", "PASS")]),
                     _resp([(2, False, "インタビューをもとにした", "PASS")])])
        r = ga.align_glosses(self.m, "art", lambda msg: fn)
        self.assertEqual(fn.calls, 2)
        self.assertEqual(r["status"], "ALIGN_PASS")
        self.assertEqual(r["merged"]["items"][1]["japanese_gloss"], "インタビューをもとにした")

    def test_fallback_reverts_kp_after_two_failures(self):
        fn = FakeFn([_resp([(2, False, "x", "FAIL")]), RuntimeError("boom")])
        r = ga.align_glosses(self.m, "art", lambda msg: fn)
        self.assertEqual(fn.calls, ga.MAX_GLOSS_ALIGNMENT_ATTEMPTS)
        self.assertEqual(r["status"], "ALIGN_FAILED")
        it = r["merged"]["items"][1]
        self.assertEqual(it["key_phrase"], "based on")
        self.assertEqual(it["used_form"], "based on")
        self.assertEqual(it["japanese_gloss"], "～をもとにした")
        self.assertFalse(it["kp_extends_beyond_candidate"])
        self.assertEqual(it["gloss_alignment"]["status"], "FALLBACK_KP_REVERTED_TO_DISPLAY_PHRASE")
        self.assertEqual(it["gloss_alignment"]["key_phrase_before_revert"], "based on interviews")

    def test_rank_mismatch_invalid(self):
        fn = FakeFn([_resp([(9, False, "a", "PASS")]), _resp([(9, False, "a", "PASS")])])
        r = ga.align_glosses(self.m, "art", lambda msg: fn)
        self.assertEqual(r["status"], "ALIGN_FAILED")

    def test_digit_and_paren_rejected(self):
        for bad in ("2つの", "インタビュー(取材)をもとにした", "インタビュー…をもとにした"):
            v = ga.validate_alignment_response(_resp([(2, False, bad, "PASS")]), [self.m["items"][1]])
            self.assertFalse(v["ok"], bad)

    def test_slot_tilde_allowed_and_tts_converted(self):
        v = ga.validate_alignment_response(_resp([(2, False, "～をもとにした", "PASS")]), [self.m["items"][1]])
        self.assertTrue(v["ok"])

    def test_writes_audit_files(self):
        fn = FakeFn([_resp([(2, False, "インタビューをもとにした", "PASS")])])
        with tempfile.TemporaryDirectory() as d:
            ga.align_glosses(self.m, "art", lambda msg: fn, out_dir=d, article_id="A")
            meta = json.load(open(os.path.join(d, "gloss_alignment_runtime_metadata.json"), encoding="utf-8"))
            self.assertEqual(meta["final_status"], "ALIGN_PASS")
            self.assertTrue(os.path.exists(os.path.join(d, "gloss_alignment_prompt.txt")))


class PromptReuse(unittest.TestCase):
    def test_rules_extracted_from_approved_template(self):
        rules = ga.load_approved_gloss_rules()
        self.assertIn("括弧", rules)
        self.assertIn("漢数字", rules)
        msg = ga.build_user_message([_item(2, "based on", "based on interviews", "～をもとにした", True)], "ART")
        self.assertIn(rules, msg)
        self.assertIn("based on interviews", msg)

    def test_model_required(self):
        with self.assertRaises(ValueError):
            ga.make_alignment_fn("m", client=object())

    def test_model_mismatch_raises(self):
        class R:
            model = "other"; output_text = "{}"; id = "i"

        class C:
            class responses:
                @staticmethod
                def create(**k): return R()
        fn = ga.make_alignment_fn("m", client=C(), model="gpt-6-luna")
        with self.assertRaises(ga.GlossAlignmentModelMismatchError):
            fn()


class ScaffoldWiring(unittest.TestCase):
    def test_scaffold_calls_alignment_in_canonicalization_path(self):
        import inspect
        import er003_v1_n3_01_scaffold_generate as sc
        src = inspect.getsource(sc.run_key_phrase_canonicalization)
        self.assertIn("gloss_align.align_glosses", src)


class ScaffoldIntegration(unittest.TestCase):
    """sc.run_key_phrase_canonicalization(Production関数)を通して、gloss再整合が初回経路で効く/対象0件ならAPI呼出なし。"""

    def _run(self, kp_for_rank4, fake):
        import unittest.mock as mock
        import er003_v1_n3_01_scaffold_generate as sc
        originals = [
            {"rank": 1, "display_phrase": "right away", "source_span": "right away", "source_sentence": "Do it right away.",
             "ja_gloss": "すぐに", "source_reference_contract": "X"},
            {"rank": 2, "display_phrase": "based on", "source_span": "based on",
             "source_sentence": "It is an estimate based on interviews with sellers.", "ja_gloss": "～をもとにした",
             "source_reference_contract": "X"},
        ]
        qa = {f: "PASS" for f in kc.QA_FIELDS}
        parsed = {"items": [
            {"rank": 1, "key_phrase": "right away", "changed_from_display_phrase": False, "normalization_reason": "none",
             "reasoning": "r", **qa},
            {"rank": 2, "key_phrase": kp_for_rank4, "changed_from_display_phrase": kp_for_rank4 != "based on",
             "normalization_reason": "restore_semantic_complement" if kp_for_rank4 != "based on" else "none",
             "reasoning": "r", **qa},
        ]}
        with tempfile.TemporaryDirectory() as d,                 mock.patch.object(sc.kc, "run_canonicalization_gate",
                                  return_value=(parsed, "CANONICALIZATION_PASS", [], "gpt-6-luna", "resp")),                 mock.patch.object(sc.gloss_align, "make_alignment_fn", return_value=fake):
            res = sc.run_key_phrase_canonicalization("ART", originals, d, "A", process="A2_SUPPORT")
            saved = json.load(open(os.path.join(d, "keywords_canonicalized.json"), encoding="utf-8"))
        return res, saved

    def test_extended_kp_gets_realigned_gloss_in_saved_record(self):
        fake = FakeFn([_resp([(2, False, "インタビューをもとにした", "PASS")])])
        res, saved = self._run("based on interviews", fake)
        it = saved["items"][1]
        self.assertEqual(res["gloss_alignment_status"], "ALIGN_PASS")
        self.assertEqual(it["key_phrase"], "based on interviews")
        self.assertEqual(it["japanese_gloss"], "インタビューをもとにした")
        self.assertEqual(it["japanese_gloss_tts"], "インタビューをもとにした")
        self.assertEqual(saved["items"][0]["japanese_gloss"], "すぐに")

    def test_unextended_kp_makes_no_api_call(self):
        fake = FakeFn([])
        res, saved = self._run("based on", fake)
        self.assertEqual(res["gloss_alignment_status"], "NO_TARGETS")
        self.assertEqual(fake.calls, 0)
        self.assertEqual(saved["items"][1]["japanese_gloss"], "～をもとにした")

    def test_failed_alignment_reverts_kp_automatically_not_human_review(self):
        fake = FakeFn([_resp([(2, False, "x", "FAIL")]), _resp([(2, False, "x", "FAIL")])])
        res, saved = self._run("based on interviews", fake)
        self.assertEqual(res["status"], "CANONICALIZATION_PASS")
        self.assertEqual(saved["items"][1]["key_phrase"], "based on")
        self.assertEqual(saved["items"][1]["japanese_gloss"], "～をもとにした")
        self.assertEqual(res["gloss_alignment_status"], "ALIGN_FAILED")


if __name__ == "__main__":
    unittest.main()
