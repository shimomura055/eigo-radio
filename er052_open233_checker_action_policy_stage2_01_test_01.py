# -*- coding: utf-8 -*-
# OPEN-233-CHECKER-ACTION-POLICY-STAGE2-01 委任_02: ①構造要素Rewrite規則(OPEN233_STRUCTURAL_REWRITE_RULES)・②読者信念テスト
# (OPEN233_STAGE2_READER_BELIEF)の単体テスト。ネットワークなし(¥0)。全新規挙動は環境変数スイッチ既定OFF。
from __future__ import annotations

import inspect
import json
import os
import pathlib
import unittest
from unittest import mock

import er052_open233_checker_action_policy_stage2_01 as cap2
import er052_open233_self_recovery_flow_runner_01 as runner

FX = pathlib.Path(__file__).parent / "er052_output" / "open233_stage2_01" / "precheck" / "fixtures"
BEFORE = (FX / "qvqc_rep2_before.md").read_text(encoding="utf-8")
TITLE = "# I Followed an AI Phone Agent and Found a Human"
SWB, SWS = cap2.SW_READER_BELIEF, cap2.SW_STRUCT_RULES
LEDGER = ("[VERIFIED] MUSE-HC-006: Metaは訓練を受けた人間の契約スタッフを使った\n"
          "[VERIFIED] MUSE-HC-012: 利用者への説明なしにテストが始まった\n")


def _env(**kw):
    return mock.patch.dict(os.environ, kw, clear=False)


def _state():
    return {"cumulative_jpy": 0.0, "cumulative_calls": 0, "cumulative_errors": 0, "history": []}


def _bj(idx, mat, belief=None, belief_text="", cfids=None, kind="none", hint=""):
    d = {"claim_index": idx, "materiality": mat, "basis": "none", "rewrite_kind": kind, "rewrite_hint": hint}
    if belief is not None:
        d.update({"reader_belief": belief_text, "belief_vs_ledger": belief, "contradicting_fact_ids": cfids or []})
    return d


def _res(judgments):
    return {"prompt_sha256": "p", "parsed": {"judgments": judgments}, "model": "m", "response_id": "r", "usage": {},
            "cost_jpy": 0.01, "elapsed_seconds": 0.01}


class TestSwitchesDefaultOff(unittest.TestCase):
    def test_default_off(self):
        env = {k: v for k, v in os.environ.items() if k not in (SWB, SWS, cap2.SW_SAVE_R3)}
        with mock.patch.dict(os.environ, env, clear=True):
            self.assertFalse(cap2.switch_on(SWB))
            self.assertFalse(cap2.switch_on(SWS))
            self.assertFalse(cap2.switch_on(cap2.SW_SAVE_R3))

    def test_not_in_approved_flow_switches(self):
        self.assertNotIn(SWB, json.dumps(runner.OPEN233_APPROVED_FLOW_SWITCHES))
        self.assertNotIn(SWS, json.dumps(runner.OPEN233_APPROVED_FLOW_SWITCHES))


class TestGuardTarget(unittest.TestCase):
    def test_negation_absence(self):
        g = cap2.guard_target("They did not know a human was on the line.", {}, "")
        self.assertTrue(g["target"])
        self.assertIn("negation_absence_or_polarity", g["types"])

    def test_universal_and_number(self):
        self.assertIn("universal", cap2.guard_target("Every call was handled by a person.", {}, "")["types"])
        self.assertIn("number", cap2.guard_target("It happened in 3 cities.", {}, "")["types"])

    def test_dev_flags(self):
        self.assertIn("direction", cap2.guard_target("Prices moved.", {"changed_comparison": True}, "")["types"])
        self.assertIn("negation_absence_or_polarity", cap2.guard_target("Prices moved.", {"changed_negation": True}, "")["types"])
        self.assertIn("subject_flag", cap2.guard_target("Prices moved.", {"changed_actor": True}, "")["types"])

    def test_new_proper_noun_not_in_ledger(self):
        g = cap2.guard_target("The call was placed by Google staff.", {}, LEDGER)
        self.assertIn("subject_new_proper_noun", g["types"])
        g2 = cap2.guard_target("The call was placed by Meta staff.", {}, LEDGER)
        self.assertNotIn("subject_new_proper_noun", g2["types"])

    def test_plain_sentence_is_not_target(self):
        g = cap2.guard_target("Muse can call businesses and make a haircut appointment.", {}, "")
        self.assertFalse(g["target"])
        self.assertEqual(g["types"], [])

    def test_direction_words_not_used(self):
        # DIRWORD(方向語彙)は設計§4-3で不採用。語彙だけでは対象にしない(Stage1のchanged_comparisonフラグがあるときだけ)。
        self.assertFalse(cap2.guard_target("Prices went up sharply.", {}, "")["target"])


class TestHelperBranches(unittest.TestCase):
    def test_consistency_invalid(self):  # (c)
        self.assertTrue(cap2.consistency_invalid(True, "contradicts", "QUALITY"))
        self.assertTrue(cap2.consistency_invalid(True, "contradicts", "ACCEPTABLE"))
        self.assertFalse(cap2.consistency_invalid(True, "contradicts", "BLOCKING"))
        self.assertFalse(cap2.consistency_invalid(False, "contradicts", "QUALITY"))
        self.assertFalse(cap2.consistency_invalid(True, "consistent", "QUALITY"))

    def test_downgrade_conditions(self):  # (d)
        self.assertTrue(cap2.downgrade_established_first_call(False, None))
        self.assertTrue(cap2.downgrade_established_first_call(True, "consistent"))
        for b in ("unclear", "unsupported_new_claim", "contradicts", None, "not_applicable"):
            self.assertFalse(cap2.downgrade_established_first_call(True, b))
        self.assertTrue(cap2.downgrade_confirmed_by_second("consistent", "consistent"))
        self.assertFalse(cap2.downgrade_confirmed_by_second("consistent", "unclear"))
        self.assertFalse(cap2.downgrade_confirmed_by_second("consistent", "contradicts"))
        self.assertFalse(cap2.downgrade_confirmed_by_second("unclear", "consistent"))

    def test_reuse_forbidden(self):  # (e)
        self.assertTrue(cap2.reuse_forbidden(True))
        self.assertFalse(cap2.reuse_forbidden(False))

    def test_run_instance_wires_reuse_ban(self):  # (e)の配線(run_instance全体は重いためソース配線を確認。cycle2は実run未再現=限界)
        src = inspect.getsource(runner.run_instance)
        self.assertEqual(src.count("cap2.reuse_forbidden"), 2)
        self.assertIn("SW_READER_BELIEF", src)

    def test_schema_has_belief_fields(self):
        for sch in (cap2.BODY_BELIEF_SCHEMA, cap2.HOOK_BELIEF_SCHEMA):
            item = sch["schema"]["properties"]["judgments"]["items"]
            for k in ("reader_belief", "belief_vs_ledger", "contradicting_fact_ids"):
                self.assertIn(k, item["properties"])
                self.assertIn(k, item["required"])
        self.assertEqual(set(cap2.BODY_BELIEF_SCHEMA["schema"]["properties"]["judgments"]["items"]["properties"]
                             ["belief_vs_ledger"]["enum"]),
                         {"contradicts", "unsupported_new_claim", "consistent", "unclear", "not_applicable"})

    def test_addendum_contains_m2_frame_clause_and_guard_note(self):
        a = cap2.belief_addendum()
        self.assertIn("語り手の枠", a)
        self.assertIn("guard_targetは私(システム)が決めて渡します", a)


FIXTURE = {"article_text": "# T\n\nIntro hook. It has two sentences.\n\nMiddle paragraph here. It also has two.\n\nThey did not know that a human was on the other end.\n\n## In one line\nS.\n",
           "ledger_text": LEDGER, "source_article_text": None}
CLAIM_TEXT = "They did not know that a human was on the other end."


def _claims(text=CLAIM_TEXT, dev=None):
    return [{"claim_text": text, "origin": "translation", "related_fact_id": "MUSE-HC-012",
             "dev": dev or {"severity": "MAJOR"}, "detected_by": "stage1_llm"}]


def _run_stage2(fake_body, claims=None, fixture=None):
    claims = claims or _claims()
    with mock.patch.object(runner, "record_call", lambda *a, **k: None), \
            mock.patch.object(cap2, "run_belief_batch_body", fake_body), \
            mock.patch.object(cap2, "run_belief_batch_hook", fake_body):
        call_log = []
        out = runner.run_stage2(None, _state(), [0], call_log, "t", fixture or FIXTURE, claims)
    return out, call_log


class TestReaderBeliefStage2(unittest.TestCase):
    def test_off_uses_legacy_call_and_adds_no_keys(self):
        legacy = mock.MagicMock(return_value=_res([_bj(0, "QUALITY")]))
        new = mock.MagicMock()
        with _env(**{SWB: "0"}), mock.patch.object(runner, "record_call", lambda *a, **k: None), \
                mock.patch.object(runner.s2c, "run_stage2_batch_variant", legacy), \
                mock.patch.object(cap2, "run_belief_batch_body", new):
            out = runner.run_stage2(None, _state(), [0], [], "t", FIXTURE, _claims())
        legacy.assert_called_once()
        new.assert_not_called()
        for k in ("guard_target", "guard_types", "reader_belief"):
            self.assertNotIn(k, out[0])
        self.assertEqual(out[0]["materiality"], "QUALITY")

    def test_on_consistent_quality_stays_quality(self):
        calls = []

        def fake(client, ledger, source, cl, rubric, model=None, *a, **k):
            calls.append(cl)
            return _res([_bj(0, "QUALITY", "consistent", "人間の存在は説明されていない", [])])
        with _env(**{SWB: "1"}):
            out, _ = _run_stage2(fake)
        self.assertEqual(len(calls), 1)
        self.assertTrue(calls[0][0]["guard_target"])
        self.assertEqual(out[0]["materiality"], "QUALITY")
        self.assertTrue(out[0]["guard_target"])
        self.assertEqual(out[0]["reader_belief"]["belief_vs_ledger"], "consistent")
        self.assertNotIn("forced_blocking", out[0]["reader_belief"])

    def test_c_reask_once_then_consistent_is_accepted(self):
        seq = [_res([_bj(0, "QUALITY", "contradicts", "x", ["MUSE-HC-012"])]),
               _res([_bj(0, "QUALITY", "consistent", "x", [])])]
        calls = []

        def fake(client, ledger, source, cl, rubric, model=None, *a, **k):
            calls.append(cl)
            return seq[len(calls) - 1]
        with _env(**{SWB: "1"}):
            out, _ = _run_stage2(fake)
        self.assertEqual(len(calls), 2)  # 再判定は1回
        self.assertEqual(out[0]["materiality"], "QUALITY")
        self.assertTrue(out[0]["reader_belief"]["reasked"])
        self.assertEqual(out[0]["reader_belief"]["first_belief"], "contradicts")

    def test_c_reask_still_contradicts_nonblocking_becomes_blocking_rewrite_increase(self):
        calls = []

        def fake(client, ledger, source, cl, rubric, model=None, *a, **k):
            calls.append(cl)
            return _res([_bj(0, "QUALITY", "contradicts", "x", ["MUSE-HC-012"])])
        with _env(**{SWB: "1"}):
            out, _ = _run_stage2(fake)
        self.assertEqual(len(calls), 2)  # 無限再判定しない(1回)
        self.assertEqual(out[0]["materiality"], "BLOCKING")
        rb = out[0]["reader_belief"]
        self.assertTrue(rb["forced_blocking"])
        self.assertTrue(rb["rewrite_increase_side"])
        self.assertEqual(rb["forced_reason"], "contradicts_but_nonblocking_after_reask")
        self.assertTrue(out[0]["floor_reason"].startswith("reader_belief_downgrade_not_established"))

    def test_c_contradicts_with_blocking_has_no_reask(self):
        calls = []

        def fake(client, ledger, source, cl, rubric, model=None, *a, **k):
            calls.append(cl)
            return _res([_bj(0, "BLOCKING", "contradicts", "x", ["MUSE-HC-012"], kind="replace_with_ledger_value", hint="h")])
        with _env(**{SWB: "1"}):
            out, _ = _run_stage2(fake)
        self.assertEqual(len(calls), 1)
        self.assertEqual(out[0]["materiality"], "BLOCKING")
        self.assertNotIn("forced_blocking", out[0]["reader_belief"])

    def test_d_first_call_unclear_or_unsupported_nonblocking_becomes_blocking(self):
        for b in ("unclear", "unsupported_new_claim"):
            def fake(client, ledger, source, cl, rubric, model=None, *a, _b=b, **k):
                return _res([_bj(0, "QUALITY", _b, "x", [])])
            with _env(**{SWB: "1"}):
                out, _ = _run_stage2(fake)
            self.assertEqual(out[0]["materiality"], "BLOCKING", b)
            self.assertEqual(out[0]["reader_belief"]["forced_reason"], "belief_" + b)

    def test_non_guard_claim_unaffected(self):
        text = "Muse can call businesses and make a haircut appointment."
        fx = dict(FIXTURE, article_text="# T\n\nIntro hook.\n\n" + text + "\n\n## In one line\nS.\n")
        calls = []

        def fake(client, ledger, source, cl, rubric, model=None, *a, **k):
            calls.append(cl)
            return _res([_bj(0, "QUALITY", "not_applicable", "", [])])
        with _env(**{SWB: "1"}):
            out, _ = _run_stage2(fake, _claims(text), fx)
        self.assertFalse(out[0]["guard_target"])
        self.assertEqual(out[0]["materiality"], "QUALITY")
        self.assertEqual(len(calls), 1)
        self.assertNotIn("reader_belief", out[0])

    def test_m2_first_person_frame_prompt_and_not_forced(self):
        """M2: 一人称の枠(`I followed ...`)を含むタイトル型の入力。promptに「語り手の枠は世界主張として扱わない」項が入り、
        モデルがconsistent+非BLOCKINGと返したときCheckerはBLOCKINGへ倒さない(forced無し)。(モデル自体の判断はreplayで実測)"""
        title_claim = "I Followed an AI Phone Agent and Found a Human"
        fx = dict(FIXTURE, article_text=BEFORE, ledger_text=LEDGER)
        prompts = []

        class _C:
            responses = None

        def fake_call(client, ledger, source, cl, rubric, model=None, *a, **k):
            prompts.append((cl, rubric))
            return _res([_bj(0, "ACCEPTABLE", "consistent", "人間がAIの裏にいたという事実", [])])
        with _env(**{SWB: "1"}), mock.patch.object(runner, "FLOOR_MODE", runner.FLOOR_MODE_NUMBER_ONLY):
            out, _ = _run_stage2(fake_call, _claims(title_claim, {"severity": "MAJOR", "changed_actor": True}), fx)
        self.assertEqual(out[0]["materiality"], "ACCEPTABLE")
        self.assertTrue(out[0]["guard_target"])
        self.assertNotIn("forced_blocking", out[0]["reader_belief"])
        self.assertIn("語り手の枠", cap2.belief_addendum())
        # 実際に組み立てられるpromptへ追記が入ることを、未モックのprompt組立関数で確認
        captured = {}

        class _Resp:
            output_text = json.dumps({"judgments": [_bj(0, "ACCEPTABLE", "consistent", "x", [])]})
            model, id, usage = "m", "r", None

        class _Cl:
            class responses:  # noqa: N801
                @staticmethod
                def create(**kw):
                    captured["prompt"] = kw["input"][1]["content"]
                    captured["schema"] = kw["text"]["format"]["name"]
                    return _Resp()
        cap2.run_belief_batch_body(_Cl, LEDGER, None, [dict(_claims(title_claim)[0], local_context="ctx", guard_target=True)],
                                   "RUBRIC", "m")
        self.assertIn("語り手の枠(I/we/youによる語りかけ", captured["prompt"])
        self.assertIn("guard_target: true", captured["prompt"])
        self.assertEqual(captured["schema"], "open233_stage2_belief_body_v1")


class TestReaderBeliefHookRoute(unittest.TestCase):
    def test_hook_route_uses_hook_belief_call_and_reask(self):
        hook_text = "They did not know that a human was on the other end."
        fx = dict(FIXTURE, article_text="# T\n\n" + hook_text + "\n\nBody paragraph. It has two.\n\n## In one line\nS.\n")
        seq = [_res([_bj(0, "ACCEPTABLE", "contradicts", "x", ["MUSE-HC-012"])]), _res([_bj(0, "ACCEPTABLE", "consistent", "x", [])])]
        calls = []

        def fake_hook(client, ledger, source, title_hook_text, cl, hook_rubric, model=None, *a, **k):
            calls.append((title_hook_text, cl))
            return seq[len(calls) - 1]
        body = mock.MagicMock()
        with _env(**{SWB: "1"}), mock.patch.object(runner, "record_call", lambda *a, **k: None), \
                mock.patch.object(cap2, "run_belief_batch_hook", fake_hook), \
                mock.patch.object(cap2, "run_belief_batch_body", body):
            out = runner.run_stage2(None, _state(), [0], [], "t", fx, _claims(hook_text))
        body.assert_not_called()
        self.assertEqual(len(calls), 2)
        self.assertEqual(out[0]["stage2_route"], "hook")
        self.assertEqual(out[0]["materiality"], "ACCEPTABLE")
        self.assertTrue(out[0]["reader_belief"]["reasked"])


def _so_result(guard=True, belief="consistent", mat="QUALITY"):
    return {"claim_text": CLAIM_TEXT, "origin": "translation", "related_fact_id": "MUSE-HC-012",
            "dev": {"severity": "MAJOR", "related_fact_id": "MUSE-HC-012"}, "detected_by": "stage1_llm",
            "materiality": mat, "llm_materiality": mat, "basis": "none", "rewrite_kind": "replace_with_ledger_value",
            "rewrite_hint": "", "floor_reason": None, "stage2_route": "body", "guard_target": guard,
            "reader_belief": {"reader_belief": "人間が裏にいたことは説明されなかった", "belief_vs_ledger": belief}}


class TestBeliefSecondOpinion(unittest.TestCase):
    def _run(self, results, only_fn=None, second_run_stage2=None):
        with _env(**{SWB: "1"}), mock.patch.object(runner, "record_call", lambda *a, **k: None), \
                mock.patch.object(cap2, "run_belief_only", only_fn or mock.MagicMock()), \
                mock.patch.object(runner, "run_stage2", second_run_stage2 or mock.MagicMock()):
            return runner.apply_stage2_second_opinion(None, _state(), [0], [], "c1", FIXTURE, results, "inst", 1)

    def test_both_consistent_confirms_downgrade_and_second_call_hides_sentence(self):
        seen = {}

        def only(client, ledger, beliefs, model):
            seen["ledger"], seen["beliefs"] = ledger, beliefs
            return {"prompt_sha256": "x", "parsed": {"judgments": [
                {"item_index": 0, "belief_vs_ledger": "consistent", "contradicting_fact_ids": []}]},
                    "model": "m", "response_id": "r", "usage": {}, "cost_jpy": 0.01, "elapsed_seconds": 0.0}
        out, log = self._run([_so_result()], only)
        self.assertEqual(out[0]["materiality"], "QUALITY")
        self.assertTrue(out[0]["second_opinion"]["confirmed_downgrade"])
        self.assertTrue(out[0]["second_opinion"]["belief_only"])
        self.assertEqual(seen["beliefs"], ["人間が裏にいたことは説明されなかった"])
        self.assertEqual(seen["ledger"], LEDGER)
        self.assertEqual(len(log), 1)

    def test_o1_prompt_does_not_contain_the_sentence(self):
        captured = {}

        class _Resp:
            output_text = json.dumps({"judgments": [{"item_index": 0, "belief_vs_ledger": "consistent",
                                                     "contradicting_fact_ids": []}]})
            model, id, usage = "m", "r", None

        class _Cl:
            class responses:  # noqa: N801
                @staticmethod
                def create(**kw):
                    captured["prompt"] = kw["input"][1]["content"]
                    return _Resp()
        cap2.run_belief_only(_Cl, LEDGER, ["人間が裏にいた"], "m")
        self.assertIn("人間が裏にいた", captured["prompt"])
        self.assertIn("MUSE-HC-012", captured["prompt"])
        self.assertNotIn(CLAIM_TEXT, captured["prompt"])
        self.assertNotIn("claim_index", captured["prompt"])

    def test_second_not_consistent_becomes_blocking(self):
        for b in ("contradicts", "unclear", "unsupported_new_claim"):
            def only(client, ledger, beliefs, model, _b=b):
                return {"prompt_sha256": "x", "parsed": {"judgments": [
                    {"item_index": 0, "belief_vs_ledger": _b, "contradicting_fact_ids": ["MUSE-HC-012"]}]},
                        "model": "m", "response_id": "r", "usage": {}, "cost_jpy": 0.01, "elapsed_seconds": 0.0}
            out, log = self._run([_so_result()], only)
            self.assertEqual(out[0]["materiality"], "BLOCKING", b)
            self.assertEqual(out[0]["floor_reason"], "s1_second_opinion_belief_not_consistent")
            self.assertTrue(log[0]["split"])

    def test_second_api_failure_is_failclosed(self):
        def only(client, ledger, beliefs, model):
            raise RuntimeError("boom")
        with mock.patch.object(runner.time, "sleep", lambda *_: None):
            out, log = self._run([_so_result()], only)
        self.assertEqual(out[0]["materiality"], "BLOCKING")
        self.assertEqual(out[0]["floor_reason"], "s1_second_opinion_failclosed:api_failure")

    def test_non_guard_claim_goes_to_regular_second_opinion(self):
        only = mock.MagicMock()
        second = mock.MagicMock(return_value=[{"materiality": "QUALITY", "floor_reason": None, "basis": "none"}])
        out, log = self._run([_so_result(guard=False)], only, second)
        only.assert_not_called()
        second.assert_called_once()
        self.assertTrue(out[0]["second_opinion"]["confirmed_downgrade"])
        self.assertNotIn("belief_only", out[0]["second_opinion"])

    def test_off_guard_flag_is_ignored(self):
        only = mock.MagicMock()
        second = mock.MagicMock(return_value=[{"materiality": "QUALITY", "floor_reason": None, "basis": "none"}])
        with _env(**{SWB: "0"}), mock.patch.object(runner, "record_call", lambda *a, **k: None), \
                mock.patch.object(cap2, "run_belief_only", only), mock.patch.object(runner, "run_stage2", second):
            out, log = runner.apply_stage2_second_opinion(None, _state(), [0], [], "c1", FIXTURE, [_so_result()], "i", 1)
        only.assert_not_called()
        second.assert_called_once()
        self.assertNotIn("belief_only", out[0]["second_opinion"])


# ---------------------------------------------------------------------------------------------------------------
# B. 構造要素の4照合
# ---------------------------------------------------------------------------------------------------------------
class TestFourChecks(unittest.TestCase):
    VOCAB = cap2.proper_noun_vocab(LEDGER, BEFORE)

    def test_vocab_contains_proper_nouns_not_title_words(self):
        for w in ("meta", "muse"):
            self.assertIn(w, self.VOCAB)
        self.assertNotIn("followed", self.VOCAB)

    def test_common_words_capitalized_by_position_are_not_proper_nouns(self):
        body = "Intro here.\n\nHe said: By then it was over. The test began later, by design. They said Meta ran it."
        v = cap2.proper_noun_vocab("", body)
        self.assertNotIn("by", v)
        self.assertIn("meta", v)
        r = cap2.four_checks("hook", "Meta ran the test.", "Meta ran the test by area.", v, body)
        self.assertTrue(r["ok"], r)

    def test_proper_nouns_in_ledger_urls_do_not_hide_names(self):
        # Ledgerのmeta.com等の小文字URLがあっても、本文に小文字形が無い固有名詞(Meta/Muse/AI)は語彙に残る(replay dev実測のバグの再発防止)
        ledger = "[VERIFIED] X: https://about.meta.com/ai/muse が説明した\n"
        body = "# T\n\nIf you ask AI to call, it does.\n\nMeta’s agent, Muse, can call stores."
        v = cap2.proper_noun_vocab(ledger, body)
        for w in ("ai", "meta", "muse"):
            self.assertIn(w, v)
        r = cap2.four_checks("hook", "If you ask AI to call, it does.", "If you ask Muse to call, it does.", v, body)
        self.assertIn("subject", r["violations"])

    def test_sentence_initial_proper_noun_without_lowercase_form_is_recognized(self):
        body = "# T\n\nHook sentence one. Another here.\n\nMatsuyama City will choose shared sewers. Japan is large."
        v = cap2.proper_noun_vocab("", body)
        self.assertIn("matsuyama", v)
        r = cap2.four_checks("hook", "A move is planned for the city.", "A move is planned for Matsuyama.", v, body)
        self.assertIn("subject", r["violations"])

    def test_unknown_capitalized_token_introduced_is_a_new_subject(self):
        # 本文にもLedger(英語)にも無い固有名詞の持込(例: Japan→Matsuyama)。語彙に無くても、文頭以外の大文字語は主体集合に入る
        body = "# T\n\nHook sentence one. Another here.\n\nJapan plans a move for sewers."
        v = cap2.proper_noun_vocab("", body)
        r = cap2.four_checks("hook", "A move is planned for Japan’s sewer systems.", "A move is planned for Matsuyama’s sewer systems.", v, body)
        self.assertIn("subject", r["violations"])
        self.assertIn("matsuyama", r["new_subjects"])
        r2 = cap2.four_checks("hook", "A move is planned for Japan’s sewer systems.",
                              "A move is planned for Japan’s sewer systems in some areas.", v, body)
        self.assertTrue(r2["ok"], r2)

    def test_title_case_does_not_flag_every_capitalized_word(self):
        body = "# T\n\nHook sentence one. Another here.\n\nMeta ran a test."
        v = cap2.proper_noun_vocab("", body)
        r = cap2.four_checks("title", "# I Followed an AI Phone Agent", "# I Followed an AI Phone Agent and Found a Human", v, body)
        self.assertTrue(r["ok"], r)

    def test_m1_subject_replacement_rejected(self):  # qvqc: I -> Meta
        r = cap2.four_checks("title", TITLE, "Meta Tested an AI Phone Agent and Found a Human", self.VOCAB, BEFORE)
        self.assertFalse(r["ok"])
        self.assertIn("subject", r["violations"])
        self.assertIn("meta", r["new_subjects"])

    def test_m1_one_word_added_allowed(self):
        r = cap2.four_checks("title", TITLE, "# I Followed an AI Phone Agent and Found a Human Behind It", self.VOCAB, BEFORE)
        self.assertTrue(r["ok"], r)
        r2 = cap2.four_checks("title", "# Meta Tested an AI Agent", "# Meta Tested an AI Agent Briefly", self.VOCAB, BEFORE)
        self.assertTrue(r2["ok"], r2)

    def test_subject_removal_is_subset_and_allowed(self):
        r = cap2.four_checks("title", TITLE, "# Following an AI Phone Agent and Finding a Human", self.VOCAB, BEFORE)
        self.assertTrue(r["ok"], r)

    def test_pronoun_swap_rejected(self):
        r = cap2.four_checks("title", TITLE, "# We Followed an AI Phone Agent and Found a Human", self.VOCAB, BEFORE)
        self.assertIn("subject", r["violations"])

    def test_polarity_change_rejected(self):
        r = cap2.four_checks("hook", "The AI makes the call.", "The AI does not make the call.", self.VOCAB, BEFORE)
        self.assertIn("polarity", r["violations"])

    def test_number_not_in_body_rejected_and_in_body_allowed(self):
        body = BEFORE + "\nIt happened 3 times."
        r = cap2.four_checks("hook", "The AI makes the call.", "The AI makes the call 7 times.", self.VOCAB, body)
        self.assertIn("number", r["violations"])
        r2 = cap2.four_checks("hook", "The AI makes the call.", "The AI makes the call 3 times.", self.VOCAB, body)
        self.assertNotIn("number", r2["violations"])

    def test_format_title_markup_and_length(self):
        r = cap2.four_checks("title", TITLE, "I Followed an AI Phone Agent and Found a Human", self.VOCAB, BEFORE)
        self.assertIn("format:markup_changed", r["violations"])
        r2 = cap2.four_checks("title", TITLE, "# " + "I Followed an AI Phone Agent " * 8, self.VOCAB, BEFORE)
        self.assertIn("format:too_long", r2["violations"])
        r3 = cap2.four_checks("heading", "## In one line", "In one line", self.VOCAB, BEFORE)
        self.assertIn("format:markup_changed", r3["violations"])

    def test_actor_class_new_subject_rejected(self):
        r = cap2.four_checks("hook", "The AI makes the call.", "The employees make the call.", self.VOCAB, BEFORE)
        self.assertIn("subject", r["violations"])


class TestStructuralKind(unittest.TestCase):
    def test_kinds(self):
        self.assertEqual(runner.structural_kind_of(BEFORE, TITLE), "title")
        self.assertEqual(runner.structural_kind_of(BEFORE, "The user asks it to handle a task."), "hook")
        self.assertIsNone(runner.structural_kind_of(BEFORE, "The human concierge feature was temporarily rolled back."))
        self.assertEqual(runner.structural_kind_of("# T\n\nHook.\n\n## In one line\nShort summary here.\n",
                                                   "Short summary here."), "in_one_line")


# ---------------------------------------------------------------------------------------------------------------
# B. ladderへの配線(分岐)
# ---------------------------------------------------------------------------------------------------------------
def _ladder(responses, claim_text, kind="delete", fixture_text=BEFORE, patch_l6=False):
    claim_rec = {"claim_text": claim_text, "rewrite_kind": kind, "materiality": "BLOCKING", "basis": "ledger_claim",
                 "rewrite_hint": "h", "dev": {"issue": "x"}}
    fixture = {"ledger_text": LEDGER, "article_text": fixture_text}
    seq = list(responses)
    seen = []

    def fake_llm(*a, **k):
        seen.append(a[4])  # label
        r = seq.pop(0) if len(seq) > 1 else seq[0]
        return json.dumps({"revised_ranges": [r]}) if r is not None else None
    ctx = [mock.patch.object(runner, "STRUCTURAL_ELEMENT_REWRITE", True),
           mock.patch.object(runner, "simple_llm_call", side_effect=fake_llm),
           mock.patch.object(runner, "record_call", lambda *a, **k: None)]
    if patch_l6:
        ctx.append(mock.patch.object(runner, "ENABLE_LADDER_LEVEL_6_FULL_REWRITE", False))
    for c in ctx:
        c.start()
    try:
        res = runner.rewrite_ranges_ladder(None, _state(), [0], [], "t", fixture, "article_text", claim_rec)
    finally:
        mock.patch.stopall()
    return res, seen


SWAP = "# Meta Tested an AI Phone Agent and Found a Human"
GOOD = "# I Followed an AI Phone Agent and Found a Human Behind It"


class TestStructuralRulesLadder(unittest.TestCase):
    def test_off_accepts_subject_swap_as_today(self):
        with _env(**{SWS: "0", "OPEN233_FIX_W1_TITLE_MARKUP": "1"}):
            res, seen = _ladder([SWAP], TITLE)
        self.assertTrue(res["guard_ok"])
        self.assertNotIn("structural_rules", res["handoff"])
        self.assertEqual(len(seen), 1)

    def test_on_m1_one_word_added_passes_without_regen(self):
        with _env(**{SWS: "1", "OPEN233_FIX_W1_TITLE_MARKUP": "1"}):
            res, seen = _ladder([GOOD], TITLE)
        self.assertTrue(res["guard_ok"])
        self.assertEqual(runner._en_title_line(res["updated_text"]), GOOD)
        sr = res["handoff"]["structural_rules"]
        self.assertEqual(sr["regen_calls"], 0)
        self.assertTrue(sr["checks"][0]["ok"])
        self.assertTrue(res["handoff"].get("structural_pair"))  # (d) W2経由でRecheckへ渡す前後対
        self.assertEqual(len(seen), 1)

    def test_on_subject_swap_regenerates_once_then_passes(self):
        with _env(**{SWS: "1", "OPEN233_FIX_W1_TITLE_MARKUP": "1"}):
            res, seen = _ladder([SWAP, GOOD], TITLE)
        self.assertTrue(res["guard_ok"])
        sr = res["handoff"]["structural_rules"]
        self.assertEqual(sr["regen_calls"], 1)
        self.assertEqual([c["ok"] for c in sr["checks"]], [False, True])
        self.assertIn("subject", sr["checks"][0]["violations"])
        self.assertEqual(seen[1], seen[0] + "_regen")

    def test_on_subject_swap_twice_rejects_level_and_exhausts_ladder_keeping_original(self):
        with _env(**{SWS: "1", "OPEN233_FIX_W1_TITLE_MARKUP": "1"}):
            res, seen = _ladder([SWAP], TITLE, patch_l6=True)
        self.assertFalse(res["guard_ok"])
        self.assertTrue(res["ladder_exhausted_without_full_rewrite"])
        self.assertEqual(res["updated_text"], BEFORE)  # 元のまま
        sr = res["handoff"]["structural_rules"]
        self.assertTrue(sr["rejected_levels"])
        self.assertTrue(sr["kept_original_quality_record"])
        self.assertLessEqual(sr["regen_calls"], len(sr["rejected_levels"]))  # 再生成は1levelにつき1回
        self.assertTrue(res["handoff"]["structural_element_rewrite"])  # 既存のladder枯渇分類(構造要素由来STOP)へ

    def test_on_markup_dropped_without_w1_is_violation(self):
        with _env(**{SWS: "1", "OPEN233_FIX_W1_TITLE_MARKUP": "0"}):
            res, _ = _ladder(["I Followed an AI Phone Agent and Found a Human Behind It"], TITLE, patch_l6=True)
        self.assertFalse(res["guard_ok"])
        self.assertIn("format:markup_changed", res["handoff"]["structural_rules"]["checks"][0]["violations"])

    def test_hook_delete_is_deferred_then_last_resort(self):
        sent = "The user asks it to handle a task."
        with _env(**{SWS: "1", "OPEN233_FIX_W1_TITLE_MARKUP": "1"}):
            res, seen = _ladder(["Meta asks it to handle a task."], sent, kind="delete", patch_l6=True)
        self.assertTrue(res["guard_ok"], res["method"])
        self.assertTrue(res["handoff"].get("hook_last_resort_delete"))
        self.assertEqual(res["ladder_level_used"], "0_delete_hook_last_resort")
        self.assertNotIn(sent, res["updated_text"])
        self.assertGreaterEqual(len(seen), 2)  # 削除の前に書換え(+再生成)を試している

    def test_hook_delete_rewrite_success_means_no_delete(self):
        sent = "The user asks it to handle a task."
        with _env(**{SWS: "1"}):
            res, seen = _ladder(["The user asks it to handle a small task."], sent, kind="delete")
        self.assertTrue(res["guard_ok"])
        self.assertFalse(res["handoff"].get("hook_last_resort_delete"))
        self.assertIn("small task", res["updated_text"])

    def test_hook_delete_off_deletes_deterministically_as_today(self):
        sent = "The user asks it to handle a task."
        with _env(**{SWS: "0"}):
            res, seen = _ladder(["x"], sent, kind="delete")
        self.assertTrue(res["guard_ok"])
        self.assertEqual(seen, [])  # LLMを呼ばず決定論削除(現行)
        self.assertNotIn(sent, res["updated_text"])

    def test_body_sentence_is_not_structural_and_unchecked(self):
        sent = "The human concierge feature was temporarily rolled back."
        with _env(**{SWS: "1"}):
            res, seen = _ladder(["Meta rolled back the human concierge feature."], sent, kind="replace_with_ledger_value")
        self.assertTrue(res["guard_ok"])
        self.assertNotIn("structural_rules", res["handoff"])

    def test_level6_article_check_rejects_title_subject_swap(self):
        after = BEFORE.replace(TITLE, SWAP)
        r = runner.structural_article_check(BEFORE, after, LEDGER)
        self.assertFalse(r["ok"])
        self.assertEqual(r["checks"][0]["kind"], "title")
        self.assertTrue(runner.structural_article_check(BEFORE, BEFORE, LEDGER)["ok"])


class TestRubricVersions(unittest.TestCase):
    def test_v1_default_and_v2_switch(self):
        env = {k: v for k, v in os.environ.items() if k != cap2.RUBRIC_VERSION_ENV}
        with mock.patch.dict(os.environ, env, clear=True):
            self.assertIs(cap2.belief_addendum(), cap2.READER_BELIEF_ADDENDUM_V1)
        with _env(**{cap2.RUBRIC_VERSION_ENV: "v2"}):
            self.assertIs(cap2.belief_addendum(), cap2.READER_BELIEF_ADDENDUM_V2)
        self.assertNotEqual(cap2.READER_BELIEF_ADDENDUM_V1, cap2.READER_BELIEF_ADDENDUM_V2)

    def test_v2_keeps_m2_frame_clause_contradicts_rule_and_guard_note(self):
        a = cap2.READER_BELIEF_ADDENDUM_V2
        self.assertIn("語り手の枠", a)
        self.assertIn("contradictsなら、materialityはBLOCKING", a)
        self.assertIn("guard_targetは私(システム)が決めて渡します", a)

    def test_belief_only_template_v2_selected_and_still_hides_sentence(self):
        captured = {}

        class _Resp:
            output_text = json.dumps({"judgments": [{"item_index": 0, "belief_vs_ledger": "consistent",
                                                     "contradicting_fact_ids": []}]})
            model, id, usage = "m", "r", None

        class _Cl:
            class responses:  # noqa: N801
                @staticmethod
                def create(**kw):
                    captured["prompt"] = kw["input"][1]["content"]
                    return _Resp()
        with _env(**{cap2.RUBRIC_VERSION_ENV: "v2"}):
            cap2.run_belief_only(_Cl, LEDGER, ["人間が裏にいた"], "m")
        self.assertIn("言い換えた・要約した・組み合わせたもの", captured["prompt"])
        self.assertNotIn(CLAIM_TEXT, captured["prompt"])


class TestR3SaveSwitchName(unittest.TestCase):
    def test_switch_constant_matches_checker(self):
        import er052_open233_stage1_coverage_checker_01 as cov
        with _env(**{cap2.SW_SAVE_R3: "1"}):
            self.assertTrue(cov.save_r3_support_ids_enabled())
        with _env(**{cap2.SW_SAVE_R3: "0"}):
            self.assertFalse(cov.save_r3_support_ids_enabled())


if __name__ == "__main__":
    unittest.main()
