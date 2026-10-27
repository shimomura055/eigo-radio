# -*- coding: utf-8 -*-
"""KP-CONFIRMED-CONTENT-PROTECTION-01 委任_03: G2のKP復唱(phrase_repeat)検査の単体test。API 0。
委任_03 evidence(X Adv実測)で、TTS recordの `phrase_repeat`(KP英語の復唱)を改変してもG2が止めない漏れを発見 → 同一委任内で是正。
実行: .venv/Scripts/python.exe -m unittest er128_kp_confirmed_content_03_test_01 -v"""
from __future__ import annotations

import test_state_isolation_01  # noqa: F401

import os
import unittest

import er119_kp_human_review_01 as rv
import er128_kp_confirmed_content_01 as cc
from er119_test_support_01 import Env, jd, jl
from er128_kp_confirmed_content_02b_test_01 import CCBase


class TestG2PhraseRepeat(CCBase):
    def _tts(self, kp_dir, **repeat_over):
        items = jl(f"{kp_dir}/keywords_canonicalized.json")["items"]
        kps = {}
        for it in items:
            e = {"english": {"canonical_text": it["used_form"]}, "phrase_repeat": {"canonical_text": it["used_form"]}}
            kps[str(it["rank"])] = e
        for r, v in repeat_over.items():
            kps[r]["phrase_repeat"] = v
        p = os.path.join(self.tmp, "tts_pr.json")
        jd(p, {"key_phrases": kps})
        return p, items

    def test_phrase_repeat_must_match_confirmed_english(self):
        with Env(self.tmp) as env:
            self.confirm_user(env)
        ok, items = self._tts(self.kp_dir)
        cc.verify_outputs(self.kp_dir, "b1b", tts_results_path=ok)   # 復唱=確定英語 → 止まらない
        bad, _ = self._tts(self.kp_dir, **{"1": {"canonical_text": items[0]["used_form"] + " XX"}})
        with self.assertRaises(rv.ConfirmedContentIntegrityViolation):
            cc.verify_outputs(self.kp_dir, "b1b", tts_results_path=bad)
        self.assertIn("phrase_repeat", str(jl(cc.paths_of(self.kp_dir)["issue_json"])["diffs"]))

    def test_missing_phrase_repeat_or_text_is_not_blocked(self):
        """復唱を持たない(Std/Y/Z)record・Master Store再利用で本文を持たないrecordは比較不能として扱い、誤BLOCKしない。"""
        with Env(self.tmp) as env:
            self.confirm_user(env)
        items = jl(f"{self.kp_dir}/keywords_canonicalized.json")["items"]
        p = os.path.join(self.tmp, "tts_nopr.json")
        jd(p, {"key_phrases": {str(it["rank"]): {"english": {"canonical_text": it["used_form"]}} for it in items}})
        cc.verify_outputs(self.kp_dir, "b1b", tts_results_path=p)
        p2 = os.path.join(self.tmp, "tts_notext.json")
        jd(p2, {"key_phrases": {str(it["rank"]): {"english": {"canonical_text": it["used_form"]}, "phrase_repeat": {"reused_from_master_store": True}} for it in items}})
        cc.verify_outputs(self.kp_dir, "b1b", tts_results_path=p2)


if __name__ == "__main__":
    unittest.main()
