# -*- coding: utf-8 -*-
# OPEN-233-CHECKER-ACTION-POLICY-STAGE2-01 委任_03: ①v3(`OPEN233_STRUCTURAL_REWRITE_RULES=2`、役割クラス比較+語り枠保持)の単体テスト。
# ネットワークなし(¥0)。盲点2種(一般名詞の主体入替・一人称枠消失)の再現fixtureを含む。v2(=1)・OFF(=0)の分岐も確認する。
from __future__ import annotations

import json
import os
import pathlib
import tempfile
import unittest
from unittest import mock

import er052_open233_checker_action_policy_stage2_01 as cap2
import er052_open233_self_recovery_flow_runner_01 as runner

FX = pathlib.Path(__file__).parent / "er052_output" / "open233_stage2_01" / "precheck" / "fixtures"
BEFORE = (FX / "qvqc_rep2_before.md").read_text(encoding="utf-8")
TITLE = "# I Followed an AI Phone Agent and Found a Human"
LEDGER = ("[VERIFIED] MUSE-HC-006: Metaは訓練を受けた人間の契約スタッフを使った\n"
          "[VERIFIED] MUSE-HC-012: 利用者への説明なしにテストが始まった\n")
SWS = cap2.SW_STRUCT_RULES
VOCAB = cap2.proper_noun_vocab(LEDGER, BEFORE)
CTX = {"classes": {"meta": "org", "muse": "ai", "reuters": "org"}}


def _env(**kw):
    return mock.patch.dict(os.environ, kw, clear=False)


def _state():
    return {"cumulative_jpy": 0.0, "cumulative_calls": 0, "cumulative_errors": 0, "history": []}


def v3(kind, b, a, ctx=CTX):
    return cap2.four_checks(kind, b, a, VOCAB, BEFORE, ctx)


class TestSwitchLevel(unittest.TestCase):
    def test_levels(self):
        for val, lv in (("0", 0), ("", 0), ("1", 1), ("ON", 1), ("2", 2), ("3", 0)):
            with _env(**{SWS: val}):
                self.assertEqual(cap2.struct_rules_level(), lv, val)
        env = {k: v for k, v in os.environ.items() if k != SWS}
        with mock.patch.dict(os.environ, env, clear=True):
            self.assertEqual(cap2.struct_rules_level(), 0)  # 既定OFF

    def test_v2_four_checks_unchanged_when_no_ctx(self):
        r = cap2.four_checks("hook", "The AI makes the call.", "The human makes the call.", VOCAB, BEFORE)
        self.assertNotIn("v3", r)
        self.assertTrue(r["ok"], r)  # v2(段階2)の盲点がそのまま残る(v2は変更しない)


class TestBlindSpots(unittest.TestCase):
    def test_blindspot1_ai_to_human_rejected(self):
        r = v3("hook", "The AI makes the call.", "The human makes the call.")
        self.assertFalse(r["ok"], r)
        self.assertIn("subject", r["violations"])
        self.assertTrue(any(x.startswith("class_cross:human") for x in r["v3"]["role_reasons"]), r)

    def test_blindspot1_other_cross_class_rejected(self):
        for after in ("The employees make the call.", "The users make the call.", "The company makes the call."):
            r = v3("hook", "The AI makes the call.", after)
            self.assertIn("subject", r["violations"], after)

    def test_blindspot1_unknown_general_noun_rejected(self):
        r = v3("hook", "The AI makes the call.", "The crowd makes the call.")
        self.assertIn("subject", r["violations"], r)
        self.assertTrue(any(x.startswith("unknown_subject_noun:crowd") for x in r["v3"]["role_reasons"]))

    def test_blindspot2_first_person_frame_lost_rejected(self):
        r = v3("title", TITLE, "# AI Phone Agent Test Put Humans on the Line")
        self.assertFalse(r["ok"], r)
        self.assertIn("frame", r["violations"])
        self.assertIn("i", r["v3"]["frame_lost"])

    def test_blindspot2_second_person_and_question_lost_rejected(self):
        r = v3("hook", "If you ask AI to make a call, does it do it?", "If asked, AI makes the call.")
        self.assertIn("frame", r["violations"])
        self.assertEqual(sorted(r["v3"]["frame_lost"]), ["?", "you"])

    def test_frame_not_required_for_in_one_line(self):
        r = v3("in_one_line", "You can ask AI to call.", "AI can make calls.")
        self.assertNotIn("frame", r["violations"])


class TestAllowed(unittest.TestCase):
    def test_ai_to_muse_concretization_allowed(self):  # 正しい具体化(Muse=台帳登録のAI)
        r = v3("hook", "If you ask AI to make a phone call, it talks to the other person.",
               "If you ask Muse to make a phone call, it talks to the other person.")
        self.assertTrue(r["ok"], r)
        r2 = v3("hook", "The AI makes the call.", "Muse makes the call.")
        self.assertTrue(r2["ok"], r2)

    def test_one_word_added_allowed(self):
        self.assertTrue(v3("title", TITLE, "# I Followed an AI Phone Agent and Found a Human Behind It")["ok"])
        self.assertTrue(v3("title", "# Meta Tested an AI Agent", "# Meta Tested an AI Agent Briefly")["ok"])
        self.assertTrue(v3("in_one_line", "Meta tested human workers on some calls.",
                           "Meta tested human workers on some calls without clearly telling users.".replace("without clearly telling users", "briefly"))["ok"])

    def test_narrator_frame_kept_with_edit_allowed(self):
        r = v3("title", TITLE, "# I Followed an AI Phone Agent and Found a Human on the Line")
        self.assertTrue(r["ok"], r)

    def test_class_subset_removal_allowed(self):
        r = v3("title", "# Meta Tested an AI Agent and Contract Workers", "# Meta Tested an AI Agent")
        self.assertTrue(r["ok"], r)


class TestStillRejected(unittest.TestCase):
    def test_hyphen_compound_cross_class_rejected(self):
        r = v3("hook", "The AI makes the call.", "The AI-Employee makes the call.")
        self.assertIn("subject", r["violations"], r)

    def test_i_to_meta_rejected(self):
        r = v3("title", TITLE, "# Meta Tested an AI Phone Agent and Found a Human")
        self.assertIn("subject", r["violations"])
        self.assertIn("frame", r["violations"])

    def test_unregistered_entity_rejected(self):
        r = v3("hook", "The AI makes the call.", "Zorblax makes the call.")
        self.assertIn("subject", r["violations"], r)
        r2 = v3("hook", "The AI makes the call.", "Meta makes the call.", {"classes": {}})
        self.assertTrue(any(x.startswith("unregistered_entity:meta") for x in r2["v3"]["role_reasons"]), r2)

    def test_org_entity_replacing_ai_rejected(self):
        r = v3("hook", "The AI makes the call.", "Reuters makes the call.")  # Reuters=org、元のクラスにorgなし
        self.assertIn("subject", r["violations"], r)

    def test_polarity_number_format_unchanged_in_v3(self):
        self.assertIn("polarity", v3("hook", "The AI makes the call.", "The AI does not make the call.")["violations"])
        self.assertIn("number", v3("hook", "The AI makes the call.", "The AI makes the call 7 times.")["violations"])
        self.assertIn("format:markup_changed", v3("title", TITLE, "I Followed an AI Phone Agent and Found a Human")["violations"])

    def test_new_pronoun_rejected(self):
        r = v3("title", TITLE, "# We Followed an AI Phone Agent and Found a Human")
        self.assertIn("subject", r["violations"])


class TestEntityTypingCache(unittest.TestCase):
    def test_cache_hit_makes_no_api_call_and_fail_closed_without_client(self):
        with tempfile.TemporaryDirectory() as d, _env(**{cap2.ENTITY_CACHE_DIR_ENV: d}):
            sha = cap2._ledger_sha(LEDGER)
            pathlib.Path(d, sha + ".json").write_text(json.dumps({"classes": {n: "org" for n in VOCAB}}), encoding="utf-8")
            client = mock.Mock()
            ctx = cap2.build_v3_ctx(LEDGER, VOCAB, client, "m", [])
            client.responses.create.assert_not_called()
            self.assertEqual(ctx["classes"]["meta"], "org")
        with tempfile.TemporaryDirectory() as d, _env(**{cap2.ENTITY_CACHE_DIR_ENV: d}):
            ctx = cap2.build_v3_ctx(LEDGER, VOCAB, None, "m", [])  # client無し=辞書のみ(未登録の固有名詞は却下される)
            self.assertEqual(ctx["classes"], {})

    def test_typing_call_once_then_cached(self):
        fake_resp = mock.Mock(output_text=json.dumps({"entities": [{"name": "Meta", "role_class": "org"}, {"name": "muse", "role_class": "ai"}]}),
                              model="m", id="r")
        with tempfile.TemporaryDirectory() as d, _env(**{cap2.ENTITY_CACHE_DIR_ENV: d}), \
                mock.patch.object(cap2.s2p, "_extract_usage", return_value={}), \
                mock.patch.object(cap2.s2p, "official_cost_jpy", return_value=0.3):
            client = mock.Mock()
            client.responses.create.return_value = fake_resp
            sink: list = []
            vocab = {"meta", "muse"}
            c1 = cap2.build_v3_ctx(LEDGER, vocab, client, "m", sink)
            self.assertEqual(c1["classes"], {"meta": "org", "muse": "ai"})
            self.assertEqual(sink, [0.3])
            c2 = cap2.build_v3_ctx(LEDGER, vocab, client, "m", sink)
            self.assertEqual(client.responses.create.call_count, 1)  # 台帳ごとに1回だけ
            self.assertEqual(c2["classes"], c1["classes"])

    def test_typing_failure_is_fail_closed(self):
        with tempfile.TemporaryDirectory() as d, _env(**{cap2.ENTITY_CACHE_DIR_ENV: d}):
            client = mock.Mock()
            client.responses.create.side_effect = RuntimeError("boom")
            ctx = cap2.build_v3_ctx(LEDGER, {"meta"}, client, "m", [])
            self.assertEqual(ctx["classes"], {})
            self.assertIn("boom", ctx["error"])


def _ladder(responses, claim_text, kind="replace_with_ledger_value", fixture_text=BEFORE):
    claim_rec = {"claim_text": claim_text, "rewrite_kind": kind, "materiality": "BLOCKING", "basis": "ledger_claim",
                 "rewrite_hint": "h", "dev": {"issue": "x"}}
    fixture = {"ledger_text": LEDGER, "article_text": fixture_text}
    seq = list(responses)
    prompts = []

    def fake_llm(*a, **k):
        prompts.append(a[6])
        r = seq.pop(0) if len(seq) > 1 else seq[0]
        return json.dumps({"revised_ranges": [r]})
    ctx = [mock.patch.object(runner, "STRUCTURAL_ELEMENT_REWRITE", True),
           mock.patch.object(runner, "simple_llm_call", side_effect=fake_llm),
           mock.patch.object(runner, "record_call", lambda *a, **k: None),
           mock.patch.object(runner, "ENABLE_LADDER_LEVEL_6_FULL_REWRITE", False)]
    for c in ctx:
        c.start()
    try:
        res = runner.rewrite_ranges_ladder(None, _state(), [0], [], "t", fixture, "article_text", claim_rec)
    finally:
        mock.patch.stopall()
    return res, prompts


BAD_FRAME = "# AI Phone Agent Test Put Humans on the Line"
GOOD = "# I Followed an AI Phone Agent and Found a Human Behind It"


class TestLadderBranches(unittest.TestCase):
    def setUp(self):
        self._d = tempfile.TemporaryDirectory()
        self.addCleanup(self._d.cleanup)
        sha = cap2._ledger_sha(LEDGER)
        pathlib.Path(self._d.name, sha + ".json").write_text(json.dumps({"classes": {"meta": "org", "muse": "ai"}}), encoding="utf-8")

    def _e(self, level):
        return _env(**{SWS: level, "OPEN233_FIX_W1_TITLE_MARKUP": "1", cap2.ENTITY_CACHE_DIR_ENV: self._d.name})

    def test_off_accepts_frame_loss(self):
        with self._e("0"):
            res, prompts = _ladder([BAD_FRAME], TITLE)
        self.assertTrue(res["guard_ok"])
        self.assertNotIn("structural_rules", res["handoff"])
        self.assertEqual(len(prompts), 1)

    def test_v2_accepts_frame_loss_as_in_stage2(self):
        with self._e("1"):
            res, prompts = _ladder([BAD_FRAME], TITLE)
        self.assertTrue(res["guard_ok"], res["method"])  # v2の盲点(一人称枠消失)は残す=v3との差の再現
        self.assertEqual(res["handoff"]["structural_rules"]["regen_calls"], 0)

    def test_v3_rejects_frame_loss_regenerates_once_with_v3_note_then_passes(self):
        with self._e("2"):
            res, prompts = _ladder([BAD_FRAME, GOOD], TITLE)
        self.assertTrue(res["guard_ok"], res["method"])
        sr = res["handoff"]["structural_rules"]
        self.assertEqual(sr["regen_calls"], 1)
        self.assertEqual([c["ok"] for c in sr["checks"]], [False, True])
        self.assertIn("frame", sr["checks"][0]["violations"])
        self.assertIn("I / you / we", prompts[1])  # v3の再生成指示
        self.assertEqual(runner._en_title_line(res["updated_text"]), GOOD)

    def test_v3_twice_rejected_keeps_original_and_exhausts_via_existing_route(self):
        with self._e("2"):
            res, prompts = _ladder([BAD_FRAME], TITLE)
        self.assertFalse(res["guard_ok"])
        self.assertTrue(res["ladder_exhausted_without_full_rewrite"])
        self.assertEqual(res["updated_text"], BEFORE)  # 元のまま。BLOCKING未修正の新しい出口は作らない
        sr = res["handoff"]["structural_rules"]
        self.assertTrue(sr["kept_original_quality_record"])
        self.assertTrue(res["handoff"]["structural_element_rewrite"])

    def test_v3_hook_ai_to_human_rejected_ai_to_muse_passes(self):
        hook = "The AI makes the call."
        with self._e("2"):
            res, _ = _ladder(["Muse makes the call."], hook)
        self.assertTrue(res["guard_ok"], res["method"])
        with self._e("2"):
            res2, _ = _ladder(["The human makes the call."], hook)
        self.assertFalse(res2["guard_ok"])
        with self._e("1"):
            res3, _ = _ladder(["The human makes the call."], hook)
        self.assertTrue(res3["guard_ok"])  # v2は盲点のまま通す

    def test_v3_body_sentence_unchecked(self):
        sent = "The human concierge feature was temporarily rolled back."
        with self._e("2"):
            res, _ = _ladder(["Meta rolled back the human concierge feature."], sent)
        self.assertTrue(res["guard_ok"])
        self.assertNotIn("structural_rules", res["handoff"])


class TestLevel6(unittest.TestCase):
    def test_article_check_passes_ctx(self):
        after = BEFORE.replace(TITLE, BAD_FRAME)
        self.assertTrue(runner.structural_article_check(BEFORE, after, LEDGER)["ok"])  # v2
        r = runner.structural_article_check(BEFORE, after, LEDGER, CTX)
        self.assertFalse(r["ok"])
        self.assertIn("frame", r["checks"][0]["violations"])


class TestReaderBeliefStaysOff(unittest.TestCase):
    def test_default_off(self):
        env = {k: v for k, v in os.environ.items() if k != cap2.SW_READER_BELIEF}
        with mock.patch.dict(os.environ, env, clear=True):
            self.assertFalse(cap2.switch_on(cap2.SW_READER_BELIEF))


if __name__ == "__main__":
    unittest.main()
