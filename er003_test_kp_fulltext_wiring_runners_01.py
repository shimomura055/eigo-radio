# -*- coding: utf-8 -*-
"""KP-FULLTEXT-SELECTION-3KP-PRODUCTION-01 委任_02: Family X runnerへの配線test(API 0・オフライン)。
X runner(er019)はgoogle-genai(外部SDK)をimportし、`-W error`ではSDK内のDeprecationWarningで落ちるため、
X runnerをimportするtestだけをこのfileへ分離した(本体は er003_test_kp_fulltext_wiring_01.py、`-W error`で実行)。
実行: .venv\\Scripts\\python.exe -m unittest er003_test_kp_fulltext_wiring_runners_01 -v"""
from __future__ import annotations

import test_state_isolation_01  # noqa: F401

import inspect
import json
import os
import tempfile
import unittest
from unittest import mock

import er003_v1_n3_01_scaffold_generate as sc

KP_ITEM = {"rank": 1, "display_phrase": "pushed prices up", "used_form": "push prices up", "key_phrase": "push prices up",
           "fulltext_source_ref": "fulltext_exact_v1", "source_sentence": "s", "japanese_gloss": "g"}


class TestExplanationPhraseX(unittest.TestCase):
    def test_x_signature_and_input_use_explanation_phrase(self):
        import er019_family_x_audio_production_runner_01 as x
        seen = {}

        def fake_gen(items, **kw):
            seen["items"] = items
            return {"items": {}, "audit": {}}
        with mock.patch.object(x.kp_explanation_gen, "generate_kp_explanations", fake_gen):
            r = x._resolve_kp_explanations_text([KP_ITEM], None)
        self.assertEqual(seen["items"][0]["display_phrase"], "push prices up")   # P-03: 解説の対象=音声で使う形
        self.assertEqual(r["phrases_signature"], ["push prices up"])
        self.assertEqual(r["gloss_signature"][0][0], "push prices up")

    def test_x_reuse_of_old_signature_is_unchanged_for_pre_kpft_items(self):
        import er019_family_x_audio_production_runner_01 as x
        old = {"rank": 1, "display_phrase": "take a player off", "used_form": "take a player off", "key_phrase": "take a player off",
               "source_sentence": "s", "japanese_gloss": "g"}
        cached = {"key_phrase_explanations_text": {"phrases_signature": ["take a player off"], "items": {}, "audit": {}}}
        r = x._resolve_kp_explanations_text([old], cached)
        self.assertTrue(r["reused_from_previous_run"])   # 旧artifact(マーカー無し)のsigは従来どおりdisplay_phrase


class TestFamilyXWiring(unittest.TestCase):
    def test_run_theme_scaffold_default_backend_is_fulltext(self):
        import er019_family_x_audio_production_runner_01 as x
        self.assertEqual(inspect.signature(x.run_theme_scaffold).parameters["kp_backend"].default, "fulltext_p2")

    def test_kp_already_generated_counts_stale_artifacts(self):
        import er019_family_x_audio_production_runner_01 as x
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(x._kp_already_generated(d), [])
            open(f"{d}/keywords_canonicalized.STALE_attempt3.json", "w").write("{}")
            self.assertEqual(len(x._kp_already_generated(d)), 1)   # 最終失敗でも1レベル1回の制約(引き直さない)

    def test_kp_stage_failure_status_for_one_two_three_items(self):
        import er019_family_x_audio_production_runner_01 as x
        kp = {"canonicalization": {"status": "CANONICALIZATION_PASS"}, "selection": {"status": "KEY_WORDS_STRUCTURE_PASS"}}
        self.assertIsNone(x.kp_stage_failure_status(kp))
        self.assertEqual(x.kp_stage_failure_status({"status": "OUTER_RETRY_EXHAUSTED", "canonicalization": None,
                                                    "selection": {"status": "KEY_WORDS_STRUCTURE_INVALID"}}),
                         "KP_STAGE_FAILED(OUTER_RETRY_EXHAUSTED)")

    def test_scaffold_only_kp_passes_fulltext_backend_and_run_dir_to_sc(self):
        import er019_family_x_audio_production_runner_01 as x
        article = "# T\n\n" + "\n\n".join(f"Paragraph {i}. Owners pushed prices up in May. Cafes keep raw beans in stock." for i in range(1, 5)) + "\n"
        captured = {}

        def fake_run_key_phrases(**kw):   # KP Human Review: X Productionはsc.run_key_phrasesではなくer119の確認付きKP経路を通る
            captured.update(kw)
            kp_dir = kw["kp_dir"]
            captured["kp_backend"] = "fulltext_p2"
            os.makedirs(kp_dir, exist_ok=True)
            return {"selection": {"status": "KEY_WORDS_STRUCTURE_PASS", "kp_backend_used": "fulltext_p2"},
                    "canonicalization": {"status": "CANONICALIZATION_PASS"}, "status": None}
        with tempfile.TemporaryDirectory() as src, tempfile.TemporaryDirectory() as out:
            os.makedirs(f"{src}/a2")
            open(f"{src}/a2/article.md", "w", encoding="utf-8").write(article)
            os.makedirs(f"{out}/a2")
            json.dump({}, open(f"{out}/a2/a2_support_texts.json", "w"))
            with mock.patch.object(__import__("er119_kp_wiring_01"), "run_kp_with_review", fake_run_key_phrases),                     mock.patch.object(x.plan, "split_family_x_article_text_v2", lambda t: {"status": "OK", "part1": "a", "part2": "b", "part3": "c"}):
                res = x.run_theme_scaffold(None, src, out, ["a2"], scaffold_only="kp")
        self.assertEqual(captured["kp_backend"], "fulltext_p2")
        self.assertEqual(captured["stop_run_dir"], out)
        self.assertEqual(res["a2"]["kp_backend_used"], "fulltext_p2")   # P-14: 完成報告・entry_pointで旧5件KPと区別


if __name__ == "__main__":
    unittest.main()
