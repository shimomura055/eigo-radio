# -*- coding: utf-8 -*-
"""KP-OUTER-RETRY-SAME-PHRASE-FIX(OPEN-456 F1)のtest。API 0。
実行: .venv\\Scripts\\python.exe -m unittest er003_test_kp_outer_retry_exclusion_01 -v"""
from __future__ import annotations

import test_state_isolation_01  # noqa: F401

import inspect
import json
import os
import unittest
from unittest import mock

import er003_key_words_canonicalization as kc
import er003_key_words_gloss_alignment as ga
import er003_v1_n3_01_scaffold_generate as sc
import er011_key_phrase_set_redundancy_qa_01 as rq
import er105_kp_fulltext_selector_01 as ft
from er003_test_kp_fulltext_wiring_01 import (ARTICLE, _Patched, fake_canon_factory, fake_gloss_factory, fake_red_factory,
                                              selector_seq)

A = [{"phrase": "pushed prices up", "word_count": 3}, {"phrase": "time lag", "word_count": 2}]
B = [{"phrase": "took a sharp turn", "word_count": 4}, {"phrase": "time lag", "word_count": 2}]


def _canon_first_n_bad(n_bad):
    """最初のn_bad回のcanonicalizationだけrank1を本文に無い語へ変えてINVALIDにする。returns (factory, counter)。"""
    cnt = {"n": 0}
    good, bad = fake_canon_factory(), fake_canon_factory({1: ("totally different", "none")})

    def factory(um, **kw):
        cnt["n"] += 1
        return (bad if cnt["n"] <= n_bad * kc.MAX_CANONICALIZATION_RETRY_ATTEMPTS else good)(um, **kw)
    return factory, cnt


class TestOuterRetryExclusion(_Patched):
    def _run(self, seq, canon_factory, sub="kp"):
        mk, st = selector_seq(seq)
        d = os.path.join(self.tmp, sub)
        with mock.patch.object(ft, "make_selector_fn", lambda msg, **kw: mk(msg)), \
                mock.patch.object(kc, "make_canonicalization_fn", canon_factory), \
                mock.patch.object(ga, "make_alignment_fn", fake_gloss_factory()), \
                mock.patch.object(rq, "make_redundancy_qa_fn", fake_red_factory([])), \
                mock.patch("time.sleep", lambda s: None):
            res = sc.run_key_phrases(ARTICLE, d, "aid", "B1", process="B1_SUPPORT", kp_backend="fulltext_p2", stop_run_dir=self.tmp)
        return d, res, st

    def test_repeated_phrase_is_excluded_in_round2_and_different_phrase_passes(self):
        cf, cnt = _canon_first_n_bad(1)
        # 外側1周目: A -> canon INVALID(rank1=pushed prices up)。2周目のgate: attempt1でAを再選択(除外句ヒット)、attempt2でB -> PASS
        d, res, st = self._run([A, A, B], cf)
        self.assertNotIn("status", res)
        self.assertEqual(cnt["n"], kc.MAX_CANONICALIZATION_RETRY_ATTEMPTS + 1, "除外句の再選択でcanonicalization(Luna)を呼ばない: 1周目のINVALID run(内部2attempt)+2周目の成功1回のみ")
        log = res["outer_retry_log"]
        self.assertEqual(len(log), 2)
        self.assertEqual(log[1]["excluded_phrases_in"], ["pushed prices up"])
        self.assertEqual(log[0]["excluded_phrases_added"], ["pushed prices up"])
        # 2周目の最初の選定message: 本文後置のnoteに句と理由
        round2_first = st["messages"][1]
        self.assertIn("「pushed prices up」", round2_first.split(ft.BODY_DELIMITER, 1)[1])
        self.assertIn("次の語句は、これまでの検証で不適合と確定しています", round2_first)
        # 最終KP
        doc = json.load(open(f"{d}/keywords_canonicalized.json", encoding="utf-8"))
        self.assertEqual([it["display_phrase"] for it in doc["items"]], ["took a sharp turn", "time lag"])
        # outer_retry_log.json / keywords_runtime_metadata.json に除外句一覧
        olog = json.load(open(f"{d}/outer_retry_log.json", encoding="utf-8"))
        self.assertEqual([e["phrase"] for e in olog["excluded_phrases"]], ["pushed prices up"])
        self.assertTrue(olog["excluded_phrases"][0]["reasons"])
        meta = json.load(open(f"{d}/keywords_runtime_metadata.json", encoding="utf-8"))
        self.assertEqual([e["phrase"] for e in meta["outer_excluded_phrases"]], ["pushed prices up"])
        a1 = meta["attempts_detail"][0]
        self.assertEqual([h["phrase"] for h in a1["exclusion_hits"]], ["pushed prices up"])

    def test_prompt2_body_unchanged_in_every_message(self):
        cf, _ = _canon_first_n_bad(1)
        _, _, st = self._run([A, A, B], cf)
        self.assertGreaterEqual(len(st["messages"]), 3)
        for m in st["messages"]:
            self.assertTrue(m.startswith(ft.PROMPT_2_TEXT + ft.BODY_DELIMITER))
            self.assertTrue(ft.prompt_prefix_intact(m))
        self.assertEqual(ft.PROMPT_2_SHA256, "a12896f485604f32efd52cb159d2615733c0eca262725af78db0b4f1c9a3dc9a")

    def test_all_candidates_excluded_fails_closed_without_extra_canon_calls(self):
        only = [{"phrase": "pushed prices up", "word_count": 3}]
        cf, cnt = _canon_first_n_bad(99)
        d, res, st = self._run([only], cf, sub="kp_all")
        self.assertEqual(res["status"], "OUTER_RETRY_EXHAUSTED")
        self.assertEqual(cnt['n'], kc.MAX_CANONICALIZATION_RETRY_ATTEMPTS, "2周目以降は除外句の再選択を事前に弾く(canonicalization呼出は1周目のみ)")
        self.assertFalse(os.path.exists(f"{d}/keywords_canonicalized.json"))
        self.assertEqual(len(res["outer_retry_log"]), sc.KP_OUTER_RETRY_MAX)

    def test_excluded_dropped_to_shortfall_on_final_attempt(self):
        # 2周目のgate最終attemptでAのうち除外句だけ落として残り(time lag)でshortfall確定(数合わせしない)
        cf, cnt = _canon_first_n_bad(1)
        d, res, _ = self._run([A, A, A], cf, sub="kp_short")
        self.assertNotIn("status", res)
        doc = json.load(open(f"{d}/keywords_canonicalized.json", encoding="utf-8"))
        self.assertEqual([it["display_phrase"] for it in doc["items"]], ["time lag"])
        self.assertTrue(res["selection"]["shortfall"])
        meta = json.load(open(f"{d}/keywords_runtime_metadata.json", encoding="utf-8"))
        self.assertEqual([h["phrase"] for h in meta["attempts_detail"][-1]["exclusion_dropped"]], ["pushed prices up"])

    def test_outer_guard_when_select_fn_ignores_exclusion(self):
        """select_fnがexcluded_phrasesを受け取れない(=er105 gateを通らない)場合も、外側で除外句の再選択をcanon前に弾く。"""
        calls = {"canon": 0, "sel": 0}

        def sel_fn(text, kp_dir, article_id, source_level, process=None, diagnostic_note=None):
            calls["sel"] += 1
            items = [{"rank": 1, "display_phrase": "pushed prices up", "source_span": "pushed prices up", "source_sentence": "s",
                      "source_sentence_id": 1}]
            return {"status": "KEY_WORDS_STRUCTURE_PASS", "original_items": items, "parsed": {"items": items}}

        def canon_fn(text, items, kp_dir, article_id, process=None):
            calls["canon"] += 1
            with open(f"{kp_dir}/canonicalization_runtime_metadata.json", "w", encoding="utf-8") as f:
                json.dump({"attempts_detail": [{"attempt": 1, "item_reasons": [{"index": 0, "rank": 1, "reasons": ["有限助動詞が含まれている"]}]}]}, f)
            return {"status": "CANONICALIZATION_INVALID"}
        d = os.path.join(self.tmp, "kp_guard")
        res = sc.run_kp_with_outer_retry("t", d, "a", "A2", select_fn=sel_fn, canon_fn=canon_fn, redundancy_fn=lambda *a, **k: {})
        self.assertEqual(res["status"], "OUTER_RETRY_EXHAUSTED")
        self.assertEqual(calls["canon"], 1)
        self.assertEqual(calls["sel"], sc.KP_OUTER_RETRY_MAX)
        self.assertEqual(res["outer_retry_log"][1]["excluded_phrase_reselected"], ["pushed prices up"])


class TestExclusionUnits(unittest.TestCase):
    def _v(self, phrases):
        resolved = [{"index": i, "phrase": p, "reasons": []} for i, p in enumerate(phrases)]
        return {"ok": True, "reasons": [], "item_reasons": [], "resolved": resolved}

    def test_normalized_match_non_final_marks_invalid(self):
        out = ft.apply_exclusions(self._v(["Having  a big moment", "time lag"]),
                                  [{"phrase": "having a BIG moment", "reasons": ["有限助動詞が含まれている"]}], final_attempt=False)
        self.assertFalse(out["ok"])
        self.assertEqual(out["item_reasons"][0]["index"], 0)
        self.assertIn("有限助動詞", out["item_reasons"][0]["reasons"][0])

    def test_final_all_excluded_stays_invalid(self):
        out = ft.apply_exclusions(self._v(["a b"]), [{"phrase": "a b", "reasons": ["x"]}], final_attempt=True)
        self.assertFalse(out["ok"])

    def test_no_exclusion_is_identity(self):
        v = self._v(["a b"])
        out = ft.apply_exclusions(v, None, final_attempt=True)
        self.assertTrue(out["ok"])
        self.assertEqual(out["resolved"], v["resolved"])

    def test_cumulative_machine_note_includes_earlier_attempt_phrases(self):
        rec = {"status": "KEY_WORDS_STRUCTURE_INVALID", "item_reasons": [{"phrase": "p2", "reasons": ["r2"]}]}
        note = ft.build_machine_note(rec, [{"phrase": "p1", "reasons": ["r1"]}, {"phrase": "P2", "reasons": ["dup"]}])
        self.assertIn("「p2」: r2", note)
        self.assertIn("「p1」: r1", note)
        self.assertNotIn("dup", note)


class TestAbcUntouched(unittest.TestCase):
    def test_strategy_l_rejects_exclusion_and_abc_do_not_use_outer_retry(self):
        with self.assertRaises(ValueError):
            sc.run_key_phrase_selection("t", "d", "a", "A2", kp_backend="strategy_l", excluded_phrases=[{"phrase": "x"}])
        src = inspect.getsource(sc._run_key_phrases_impl)
        self.assertNotIn("run_kp_with_outer_retry", src)
        self.assertNotIn("excluded", src)


if __name__ == "__main__":
    unittest.main()
