# -*- coding: utf-8 -*-
"""er124_kp_phrase_word_trial_01 のtest(API 0。ネットワーク遮断harness下で実行する)。"""
import json
import os
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

import er105_kp_fulltext_selector_01 as ft          # noqa: E402
import er119_kp_candidates_01 as kcand               # noqa: E402
import er119_kp_prompt_2v_01 as p2v                  # noqa: E402
import er124_kp_phrase_word_trial_01 as t            # noqa: E402

TEXT = ("The island was reset every hour. The AI kept notes in a work area. Those that had taken a detour were now one step ahead. "
        "A cathedral stood on the hill. One tip was worth paying attention to.")


class PromptTests(unittest.TestCase):
    def test_production_prompts_untouched(self):
        self.assertEqual(p2v.PROMPT_2V_SHA256, p2v.PROMPT_2V_SHA256_PINNED)

    def test_p7_differs_from_prompt2_only_in_head_and_cond6(self):
        base_lines = ft.PROMPT_2_TEXT.split("\n")
        p7_lines = t.P7_TEXT.split("\n")
        diff = [(a, b) for a, b in zip(base_lines, p7_lines) if a != b]
        self.assertEqual(len(base_lines), len(p7_lines))
        self.assertEqual(len(diff), 2)   # 冒頭の件数文と条件6のみ
        self.assertIn("最大7", t.P7_TEXT)
        for cond in ("1. **本文一致（絶対条件）**", "2. **5語以内（絶対条件）**", "3. **学習ポイントの明確化と最小化（必須）**",
                     "4. **上級者向けの学習価値**", "5. **易しい表現の除外**"):
            self.assertIn(cond, t.P7_TEXT)
        self.assertEqual(ft.PROMPT_2_TEXT.split("\n")[-1], t.P7_TEXT.split("\n")[-1])   # 最終確認文は同一

    def test_w3_is_single_word_prompt(self):
        self.assertIn("単語単体(1語)", t.W3_TEXT)
        self.assertIn("最大3つ", t.W3_TEXT)
        self.assertIn("数合わせはしない", t.W3_TEXT)
        self.assertIn("簡単すぎる語や不自然な語で3件に揃えない", t.W3_TEXT)

    def test_messages(self):
        m7 = t.build_p7_message(TEXT)
        self.assertTrue(m7.startswith(t.P7_TEXT + ft.BODY_DELIMITER))
        w = t.build_w3_message(TEXT, ["take a detour", "one step ahead"])
        self.assertEqual(t.parse_already(w), ["take a detour", "one step ahead"])


class KindTests(unittest.TestCase):
    def test_kind(self):
        self.assertEqual(t.classify_kind("cathedral"), "word")
        self.assertEqual(t.classify_kind("well-known"), "word")
        self.assertEqual(t.classify_kind("carry over"), "phrase")
        self.assertEqual(t.classify_kind("one step ahead"), "phrase")


class GateTests(unittest.TestCase):
    def setUp(self):
        import er030_key_phrase_db_hybrid_core_01 as core
        self.units = core.build_sentence_units(TEXT)

    def _sel(self, phrases):
        return [{"phrase": p, "reason_ja": "r", "declared_word_count": len(p.split())} for p in phrases]

    def test_validate_and_containment_and_overflow(self):
        g = t.selection_gate(self._sel(["taken a detour", "not in text", "one step ahead", "worth paying attention to"]), self.units, [], {}, 2, "p7")
        stages = {d["phrase"]: d["stage"] for d in g["dropped"]}
        self.assertEqual(stages["not in text"], "validate")
        self.assertEqual(len(g["kept"]), 2)
        self.assertEqual(stages["worth paying attention to"], "overflow")
        # 単語がP7句に包含される場合はProductionと同じくduplicate_of_top3
        g2 = t.selection_gate(self._sel(["detour", "cathedral"]), self.units, [ft.phrase_key("a detour"), ft.phrase_key("one step ahead")], {}, 3, "w3")
        d2 = {d["phrase"]: d["stage"] for d in g2["dropped"]}
        self.assertEqual(d2.get("detour"), "duplicate_of_top3")
        self.assertEqual([k["resolved"]["phrase"] for k in g2["kept"]], ["cathedral"])

    def test_gate_matches_production_run_vocab_selection(self):
        """selection_gateは、Productionのrun_vocab_selection(cap=5)と同一入力で同一のkept/droppedを返す。"""
        sel = ["taken a detour", "not in text", "cathedral", "one step ahead", "detour"]
        raw = json.dumps({"items": [{"phrase": p, "reason_ja": "r", "word_count": len(p.split())} for p in sel]})
        already_items = [{"display_phrase": "a detour"}]
        prod = kcand.run_vocab_selection(TEXT, self.units, already_items, [], make_call_fn=lambda msg: (lambda: (raw, "m", "r")), sleep_fn=lambda s: None)
        mine = t.selection_gate(p2v.parse_selection(raw), self.units, [ft.phrase_key("a detour")], {}, 5, "call2")
        self.assertEqual([k["resolved"]["phrase"] for k in prod["kept"]], [k["resolved"]["phrase"] for k in mine["kept"]])
        self.assertEqual([(d["phrase"], d["stage"]) for d in prod["dropped"]], [(d["phrase"], d["stage"]) for d in mine["dropped"]])


class FlowTests(unittest.TestCase):
    def test_select_fn_and_w3_fn_with_mock_calls(self):
        import er030_key_phrase_db_hybrid_core_01 as core
        units = core.build_sentence_units(TEXT)
        state = t.TrialState()
        seen = {}

        def factory(msg, model):
            def fn():
                if msg.startswith(t.P7_TEXT):
                    seen["p7"] = msg
                    items = [{"phrase": "one step ahead", "reason_ja": "a", "word_count": 3}, {"phrase": "no such", "reason_ja": "b", "word_count": 2},
                             {"phrase": "worth paying attention to", "reason_ja": "c", "word_count": 4}]
                else:
                    seen["w3"] = msg
                    items = [{"phrase": "cathedral", "reason_ja": "d", "word_count": 1}] * 1 + [
                        {"phrase": "notes", "reason_ja": "e", "word_count": 1}, {"phrase": "island", "reason_ja": "f", "word_count": 1},
                        {"phrase": "hill", "reason_ja": "g", "word_count": 1}]
                return json.dumps({"items": items}), model, "resp"
            return fn
        sel = t.make_p7_select_fn(TEXT, state, units, call_factory=factory)
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            res = sel(TEXT, d, "a", "A2", process="A2_SUPPORT", diagnostic_note=None, kp_backend="fulltext_p2")
        self.assertEqual(res["status"], ft.STATUS_PASS)
        self.assertEqual([i["display_phrase"] for i in res["original_items"]], ["one step ahead", "worth paying attention to"])
        self.assertEqual(state.p7_returned, 3)
        self.assertEqual([x["stage"] for x in state.p7_dropped], ["validate"])
        w3 = t.make_w3_call_fn(TEXT, state, "A2_SUPPORT", call_factory=factory)
        prod_msg = p2v.build_user_message(TEXT, ["one step ahead", "worth paying attention to"])
        raw, mid, rid = w3(prod_msg)()
        self.assertEqual(state.w3_returned, 4)
        self.assertEqual(state.w3_over_request, 1)
        self.assertEqual(len(json.loads(raw)["items"]), 3)
        self.assertIn("- one step ahead", seen["w3"])


class IsolationTests(unittest.TestCase):
    PROD = ["er119_kp_candidates_01.py", "er119_kp_human_review_01.py", "er119_kp_human_review_cli_01.py", "er105_kp_fulltext_selector_01.py",
            "er003_key_words_canonicalization.py", "er003_key_words_min_unit.py", "er119_kp_prompt_2v_01.py", "er119_kp_wiring_01.py"]

    def test_production_modules_do_not_import_trial_module(self):
        for f in self.PROD + ["er019_family_x_audio_production_runner_01.py", "er026_family_z_fiction_production_runner_01.py",
                              "er003_v1_n3_01_scaffold_generate.py"]:
            with open(os.path.join(ROOT, f), encoding="utf-8") as fh:
                self.assertNotIn("er124_kp_phrase_word_trial", fh.read(), f)

    def test_production_files_not_modified_vs_head(self):
        r = subprocess.run(["git", "diff", "--stat", "--"] + self.PROD, cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(r.stdout.strip(), "")


if __name__ == "__main__":
    unittest.main()
