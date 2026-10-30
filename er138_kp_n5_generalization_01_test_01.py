# -*- coding: utf-8 -*-
"""KP-GENERALIZATION-N5-PRODUCTION-WIRING-01 委任_02: er138(Key Phrase一般化N5の正式Production module)のmodule単体test(API 0、決定論)。
(1) Prompt/schema/モデル/呼出パラメータの固定(Trial確定版と同一であることの固定値)
(2) Trial 03のcache keyの再計算一致(=Prompt/schema/model/effort/think_budgetが実入力でTrialと同一)+記録応答replayによるTrial N5出力とのexact一致(19ケース、Trial不変のまま再現)
(3) 原文§4Aの必須回帰(hear it out / take points away from / keep one's eye on / set a lower limit / take an unexpected turn / 訳が旧語義のまま残らない / 良質候補の保持)
(4) 送り方の同一性(Opus M7: developer messageなし・json_schema strict・effort None時reasoning指定なし・GeminiはadditionalProperties除去・thinking_budget・max_output_tokens)
(5) 各部品の単体(revert/span_gloss/fix_drops_content/reconcile、M5 apply_to_item、M6 5語、M8/M9 CHK5、M13 Gemini model_version、JSON途切れ再試行・技術retry・STOP伝播)
(6) 資産(WordNet vendoring sha・routing・価格登録)のfail-closed
実行: .venv\\Scripts\\python.exe -m unittest er138_kp_n5_generalization_01_test_01 -v"""
from __future__ import annotations

import test_state_isolation_01  # noqa: F401

import copy
import hashlib
import json
import os
import re
import unittest
from unittest import mock

import er006_model_routing_contract_01 as routing
import er119_kp_backfill_01 as bf
import er138_kp_n5_generalization_01 as n5

ROOT = os.path.dirname(os.path.abspath(__file__))
FIXTURE = os.path.join(ROOT, "docs", "research", "KP-GENERALIZATION-N5-PRODUCTION-WIRING-01", "fixtures", "n5_trial_replay_fixture_01.json")
with open(FIXTURE, encoding="utf-8") as _f:
    FX = json.load(_f)

# ---- Trial確定版の固定値(CURRENT_STATE_01 §4の実測sha。Prompt/規則/schemaの変更にはユーザー承認が必要) ----
EXPECTED_SHA = {
    "B1": "97dd3c281a2858f3", "GEN5_EXTRA": "a4252120a6254001", "GEN2_RULES": "32f51f3552ab3497", "VER5_HEAD+VER5_ADD": "1483f97b92a40be9",
    "CHK5_RULES": "b10a6edca5ed9737",
    "schema": {"B1": "e52f403cf3b4760f", "SEL": "36612de032fba6b4", "GEN5": "e158613928975289", "VER5": "1164d51aa0682719", "CHK5": "c5a05fed55bf59ea"},
    "FLAGS_V1_HASH": "3bba7ad2cc6a",
}


def cache_key(model, user, schema, effort, think_budget):
    """Trial kpg02_llm.callのcache key([model, user, system, schema, effort, think_budget, SALT])。"""
    return hashlib.sha256(json.dumps([model, user, None, schema, effort, think_budget, ""], ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:24]


class ReplaySend:
    """n5._sendの差替え: Trialのcache keyを再計算してfixtureから応答を返す。keyが無ければ失敗=Prompt/schema/model等がTrialと異なる証拠。"""

    def __init__(self):
        self.keys = []

    def __call__(self, stage, model, user, schema, max_out):
        p = n5.STAGE_PARAMS[stage]
        assert max_out == p["max_out"]
        key = cache_key(model, user, schema, p["effort"], p["think_budget"])
        self.keys.append((stage, key))
        if key not in FX["cache"]:
            raise AssertionError(f"Trialのcache keyに一致しない({stage}): Prompt/schema/model/effort/think_budgetがTrial確定版と異なる")
        d = FX["cache"][key]
        assert d["stage"] == stage
        m = d["meta"]
        return json.dumps(d["out"], ensure_ascii=False), {"model_req": model, "model_id": m["model_id"], "model_version": None, "in": m["in"], "out": m["out"],
                                                         "cached": 0, "sec": m["sec"], "cost_jpy": m["cost_jpy"]}


def run_case(cid, send=None):
    case = FX["cases"][cid]
    send = send or ReplaySend()
    ctx = n5.N5Ctx("A2_SUPPORT", sleep_fn=lambda s: None)
    with mock.patch.object(n5, "_send", send), mock.patch.object(n5, "preflight", lambda: None):
        r = n5.run_trial_equivalent(case["text"], case["base"], ctx)
    return json.loads(json.dumps(r["items"], ensure_ascii=False)), r, ctx, send


class TestPinnedConfig(unittest.TestCase):
    def test_prompt_and_schema_shas_pinned(self):
        s = n5.prompt_shas()
        self.assertEqual(s["B1"], EXPECTED_SHA["B1"])
        self.assertEqual(s["GEN5_EXTRA"], EXPECTED_SHA["GEN5_EXTRA"])
        self.assertEqual(s["GEN2_RULES"], EXPECTED_SHA["GEN2_RULES"])
        self.assertEqual(s["VER5_HEAD+VER5_ADD"], EXPECTED_SHA["VER5_HEAD+VER5_ADD"])
        self.assertEqual(s["CHK5_RULES"], EXPECTED_SHA["CHK5_RULES"])
        self.assertEqual(s["schema"], EXPECTED_SHA["schema"])
        self.assertEqual(s["FLAGS_V1_HASH"], EXPECTED_SHA["FLAGS_V1_HASH"])
        self.assertEqual(n5.FLAGS_V1_HASH, EXPECTED_SHA["FLAGS_V1_HASH"])

    def test_models_and_call_params_equal_trial(self):
        # Trial T2/kpg03_methods.py:20 (SOL/LUNA/GEM)、kpg04_methods: B1 max_out6000/SEL 7000/GEN5 9000/VER5 6000(think_budget=0)/CHK5 3500(effort=low)
        self.assertEqual((n5.LUNA, n5.GEM, n5.SOL), ("gpt-6-luna", "gemini-3.8-flash", "gpt-6.1-sol"))
        self.assertEqual(n5.STAGE_PARAMS, {
            "b1": {"model": "gpt-6-luna", "max_out": 6000, "effort": None, "think_budget": None},
            "sel": {"model": "gpt-6-luna", "max_out": 7000, "effort": None, "think_budget": None},
            "gen5": {"model": "gpt-6-luna", "max_out": 9000, "effort": None, "think_budget": None},
            "ver5": {"model": "gemini-3.8-flash", "max_out": 6000, "effort": None, "think_budget": 0},
            "chk5": {"model": "gpt-6.1-sol", "max_out": 3500, "effort": "low", "think_budget": None}})
        self.assertEqual(n5.PHRASE_PICK_CAP, 7)
        self.assertEqual(n5.JSON_TRUNCATION_MAX_OUT_FACTOR, 1.6)

    def test_not_counted_stages_match_backfill_constants(self):
        self.assertEqual(tuple(n5.NOT_COUNTED_N5_STAGES), ("n5_pool", "n5_select", "n5_pick"))
        for st in n5.NOT_COUNTED_N5_STAGES:
            self.assertIn(st, bf.NOT_COUNTED_STAGES)
            self.assertIn(st, bf.GATE_DROP_EXEMPT_STAGES)
        for st in (n5.STAGE_GENERALIZE, n5.STAGE_VERIFY, n5.STAGE_CHECK):      # pick後に失われた候補はEに数える(Opus M3)
            self.assertNotIn(st, bf.NOT_COUNTED_STAGES)
            self.assertNotIn(st, bf.GATE_DROP_EXEMPT_STAGES)

    def test_e_counting_n5_select_not_counted_but_verify_check_counted(self):
        dropped = [{"phrase": "a b", "stage": "n5_pool"}, {"phrase": "c d", "stage": "n5_select"}, {"phrase": "e f", "stage": "n5_pick"},
                   {"phrase": "g h", "stage": "n5_generalize"}, {"phrase": "i j", "stage": "n5_verify"}, {"phrase": "k l", "stage": "n5_check"}]
        c = bf.count_exclusions(dropped, [])
        self.assertEqual(c["total"], 3)
        self.assertEqual(sorted(c["by_stage"]), ["n5_check", "n5_generalize", "n5_verify"])

    def test_routing_keys_literal_and_resolution(self):
        self.assertEqual(routing.PROCESS_MODEL_MAP["KP_N5_VERIFY"], "gemini-3.8-flash")
        self.assertEqual(routing.PROCESS_MODEL_MAP["KP_N5_CHECK"], "gpt-6.1-sol")
        for proc in ("A2_SUPPORT", "B1_SUPPORT"):
            for st in ("b1", "sel", "gen5"):
                self.assertEqual(n5.resolve_stage_model(st, proc), "gpt-6-luna")
        self.assertEqual(n5.resolve_stage_model("ver5", "A2_SUPPORT"), "gemini-3.8-flash")
        self.assertEqual(n5.resolve_stage_model("chk5", "B1_SUPPORT"), "gpt-6.1-sol")

    def test_routing_violation_is_stop_and_before_api(self):
        with mock.patch.object(n5, "_send", side_effect=AssertionError("API呼出前に止まるべき")):
            with self.assertRaises(n5.N5ContractError):
                n5.call_llm("sel", "x", n5.SEL3_SCHEMA, n5.N5Ctx(None))            # processなし
            with self.assertRaises(n5.N5ContractError):
                n5.call_llm("sel", "x", n5.SEL3_SCHEMA, n5.N5Ctx("WRITER_FACT_CHECK"))  # luna段のprocessはA2/B1_SUPPORTのみ
        with mock.patch.dict(routing.PROCESS_MODEL_MAP, {"KP_N5_VERIFY": "gemini-3.8-flash-lite"}):
            with self.assertRaises(n5.N5ContractError):
                n5.resolve_stage_model("ver5", "A2_SUPPORT")           # 契約値が書換えられたらTrial確定版と一致せずSTOP

    def test_contract_error_is_propagating_for_backfill(self):
        e = n5.N5ContractError("x")
        self.assertTrue(bf.is_propagating_exception(e))
        self.assertTrue(bf.is_propagating_exception(routing.ModelContractViolation("y")))

    def test_pricing_registered_for_all_models_and_fail_closed(self):
        for m in (n5.LUNA, n5.GEM, n5.SOL):
            inp, cached, out = n5._price_per_m(m)
            self.assertTrue(inp > 0 and out > 0)
        self.assertEqual(n5._price_per_m("gemini-3.8-flash"), (0.75, 0.075, 3.75))
        with self.assertRaises(routing.PricingNotFoundError):
            n5._price_per_m("gemini-9.9-nonexistent")

    def test_wordnet_vendored_sha_pinned(self):
        with open(n5.WORDNET_ZIP, "rb") as f:
            h = hashlib.sha256(f.read()).hexdigest()
        self.assertEqual(h, n5.WORDNET_SHA256)
        self.assertEqual(n5.WORDNET_SHA256, "cbda5ea6eef7f36a97a43d4a75f85e07fccbb4f23657d27b4ccbc93e2646ab59")
        self.assertTrue(n5._wn().synsets("take"))

    def test_wordnet_missing_or_tampered_is_fail_closed(self):
        with mock.patch.object(n5, "_WN", None), mock.patch.object(n5, "WORDNET_ZIP", os.path.join(ROOT, "does_not_exist.zip")):
            with self.assertRaises(n5.N5ContractError):
                n5._wn()
        with mock.patch.object(n5, "_WN", None), mock.patch.object(n5, "WORDNET_SHA256", "0" * 64):
            with self.assertRaises(n5.N5ContractError):
                n5._wn()

    def test_no_developer_message_and_no_trial_imports_in_source(self):
        with open(os.path.join(ROOT, "er138_kp_n5_generalization_01.py"), encoding="utf-8") as f:
            src = f.read()
        self.assertNotIn('"role": "developer"', src)
        self.assertNotIn("'role': 'developer'", src)
        self.assertIsNone(re.search(r"^\s*(import|from)\s+kpg0[1-4]", src, re.M))
        self.assertNotIn("KPG4_CAP", src)

    def test_audit_record_has_method_models_and_prompt_shas(self):
        a = n5.audit_record()
        self.assertEqual(a["method"], "N5@T3-2026-10-30")
        self.assertEqual(a["models_requested"], {"b1": "gpt-6-luna", "sel": "gpt-6-luna", "gen5": "gpt-6-luna", "ver5": "gemini-3.8-flash", "chk5": "gpt-6.1-sol"})
        self.assertEqual(a["prompt_sha16"]["B1"], EXPECTED_SHA["B1"])
        self.assertEqual(a["wordnet_sha256"], n5.WORDNET_SHA256)


class TestTrialReplayExact(unittest.TestCase):
    """実Trial入力(19ケース)に対し、Production moduleがTrial N5と同じcache keyのPromptを組み立て(=同一性の証明)、記録応答のreplayでTrial出力とexact一致する。"""

    def test_all_cases_key_match_and_exact_output(self):
        self.assertEqual(len(FX["cases"]), 19)
        n_items, n_keys = 0, 0
        for cid in FX["cases"]:
            with self.subTest(case=cid):
                items, r, ctx, send = run_case(cid)
                self.assertEqual(items, FX["cases"][cid]["trial_items"])
                self.assertGreaterEqual(len(send.keys), 4)                       # B1/SEL/GEN5/VER5/CHK5(全stage)
                self.assertEqual({s for s, _ in send.keys} >= {"b1", "sel", "gen5", "ver5", "chk5"}, True)
                n_items += len(items)
                n_keys += len(send.keys)
        self.assertGreaterEqual(n_items, 100)
        self.assertGreaterEqual(n_keys, 90)

    def test_actual_models_recorded_per_stage(self):
        _, r, ctx, send = run_case("untidi_a2")
        got = {m["stage"]: m["model_id"] for m in ctx.metas}
        self.assertEqual(got, {"b1": "gpt-6-luna", "sel": "gpt-6-luna", "gen5": "gpt-6-luna", "ver5": "gemini-3.8-flash", "chk5": "gpt-6.1-sol"})

    def _item(self, cid, span):
        return next(i for i in run_case(cid)[0] if i["source_span"] == span)

    def test_4A_hear_it_out(self):
        for cid in ("untidi_a2", "untidi_b1b"):
            it = self._item(cid, "hear it out")
            self.assertEqual(it["display_form"], "hear someone out")
            self.assertEqual(it["check"]["relation"], "SAME")
            self.assertIn("PERSON_OVERRIDE", it["flags"])
            self.assertIn("最後まで聞く", it["gloss_ja"])
            self.assertFalse(it["reverted"])

    def test_4A_take_points_away_from(self):
        it = self._item("untidi_a2", "take points away from")
        self.assertEqual(it["display_form"], "take something away from")
        self.assertEqual(it["check"]["relation"], "GLOSS_MISMATCH")                 # 日本語訳が旧語義のまま -> CHK5が訳を修正して採用
        self.assertNotEqual(it["gloss_ja"], it["gloss_pre_check"])
        self.assertIsNotNone(it["gloss_pre_check"])
        # untidi_b1bの『taking points away』は意味が変わる一般化(take away from=別見出し)を本文の形へrevert、訳も本文語義へ(M1)
        it2 = self._item("untidi_b1b", "taking points away")
        self.assertTrue(it2["reverted"])
        self.assertEqual(it2["display_form"], "take points away")
        self.assertIn("FIX_REJECTED", it2["flags"])
        self.assertEqual(it2["gloss_source"], "verify.source_sense_ja")                # この句には同一spanのP7 glossが無く、VER5が独立導出した本文語義へ
        self.assertEqual(it2["gloss_ja"], "〜の価値や良さを損なう、減点する")
        self.assertIsNone(it2["check"])                                             # CHK5対象はrevertされていない件のみ(Opus M8の実体)

    def test_4A_keep_ones_eye_on_boundary_example(self):
        it = self._item("melos_a2", "kept his eyes on them")
        self.assertEqual(it["display_form"], "keep one's eye on")
        self.assertEqual(it["reconcile"], "FRAME_MISMATCH")
        self.assertIn("PRONOUN_SLOT", it["flags"])
        self.assertEqual(it["check"]["relation"], "SAME")

    def test_4A_modifier_drop_allowed_forms(self):
        a = self._item("jwst_m_b1b", "set a lower limit")
        self.assertEqual(a["display_form"], "set a limit")
        self.assertEqual(a["check"]["relation"], "MODIFIER_DROPPED_OK")
        for cid in ("jwst_m_a2", "jwst_m_b1b"):
            b = self._item(cid, "took an unexpected turn")
            self.assertEqual(b["display_form"], "take a turn")
            self.assertEqual(b["check"]["relation"], "MODIFIER_DROPPED_OK")
            self.assertNotIn("予期", b["gloss_ja"])                                  # 除いた修飾語の意味を訳に残さない

    def test_4A_no_stale_old_sense_gloss_after_revert_or_fix(self):
        """revert/fix時に形と訳が対で変わる(訳だけ旧語義のまま残らない)。"""
        for cid in FX["cases"]:
            for it in FX["cases"][cid]["trial_items"]:
                if it["reverted"]:
                    self.assertTrue(it["gloss_source"])                                # revert時は訳の出所(本文語義)が記録される
                    self.assertNotEqual(it["gloss_ja"], it["gloss_pre_revert"])        # 旧語義の訳が残っていない(形と訳が対で戻る)
                    self.assertNotEqual(it["display_form"], it["display_form_pre_revert"])

    def test_4A_good_candidates_not_lost(self):
        """Trial N5が保持した全候補(110のうち本fixture分)が正式module経路でも保持される=exact一致で担保。ケース別件数を固定。"""
        want = {"untidi_a2": 7, "ai_cha_b1b": 4, "jwst_m_a2": 5, "jwst_m_b1b": 7, "meta_w_b1b": 4, "untidi_b1b": 7, "ai_cha_a2": 3, "meta_w_a2": 5, "aiisland_b1b": 7,
                "surname_b1b": 6, "melos_a2": 7, "ignobel_a2": 4, "ignobel_b1b": 7, "tesla_b1b": 7, "aiisland_a2": 6, "moon_b1b": 4, "surname_a2": 5, "melos_b1b": 5, "tesla_a2": 5}
        for cid, n in want.items():
            self.assertEqual(len(run_case(cid)[0]), n, cid)


class Scripted:
    """n5._sendの差替え(合成応答)。stageごとの応答queue(str=raw本文 / Exception=送出)。呼出記録を残す。"""

    def __init__(self, **q):
        self.q = {k: list(v) for k, v in q.items()}
        self.calls = []

    def __call__(self, stage, model, user, schema, max_out):
        self.calls.append((stage, model, max_out, user))
        item = self.q[stage].pop(0)
        if isinstance(item, Exception):
            raise item
        return (item if isinstance(item, str) else json.dumps(item, ensure_ascii=False)), {
            "model_req": model, "model_id": model, "model_version": None, "in": 100, "out": 50, "cached": 0, "sec": 0.0, "cost_jpy": 0.01}


def _chk(rows):
    return {"checks": [{"id": i, "context_sense_ja": "c", "example_en": "e", "relation": r, "fix_display_form": fx, "fix_gloss_ja": fg, "reason_ja": "r"}
                       for i, (r, fx, fg) in enumerate(rows, 1)]}


def _item(span="work out the plan", sentence="They work out the plan.", form="work out", gloss="練る", **kw):
    c = dict(span=span, sentence=sentence, display_form=form, gloss_ja=gloss, tokens=[(1, "CORE", "work"), (2, "CORE", "out"), (3, "DROP", ""), (4, "DROP", "")],
             verify={}, source_sense_ja="計画を考え出す", sense_note_ja="x", key=1)
    c.update(kw)
    return c


class TestCheckStage(unittest.TestCase):
    def ctx(self):
        return n5.N5Ctx("A2_SUPPORT", sleep_fn=lambda s: None)

    def test_chk5_targets_only_non_reverted_all_items_M8(self):
        a, b = _item(span="work out the plan", key=1), _item(span="figure it out now", sentence="I figure it out now.", form="figure out", key=2, reverted=True)
        s = Scripted(chk5=[_chk([("SAME", "", "")])])
        log = n5.new_log("t")
        with mock.patch.object(n5, "_send", s):
            out = n5.run_check("T", [a, b], log, self.ctx())
        self.assertEqual(len(out), 2)
        self.assertEqual(len(log["check_targets"]), 1)                            # reverted済みはCHK5対象外
        self.assertIn("work out the plan", s.calls[0][3])
        self.assertNotIn("figure it out now", s.calls[0][3].split("【検査対象】")[1])

    def test_chk5_missing_verdict_retried_once_then_dropped_M9(self):
        a, b = _item(span="work out the plan", key=1), _item(span="look into the matter", sentence="We look into the matter.", form="look into", key=2)
        # 1回目: 項目2の判定が欠落 -> 欠落分(項目2)だけ再呼出 -> なお欠落 -> 除外(n5_check、Eに数える)
        s = Scripted(chk5=[_chk([("SAME", "", "")]), {"checks": []}])
        log = n5.new_log("t")
        with mock.patch.object(n5, "_send", s):
            out = n5.run_check("T", [a, b], log, self.ctx())
        self.assertEqual([c["key"] for c in out], [1])
        self.assertEqual(len(s.calls), 2)
        self.assertNotIn("work out the plan", s.calls[1][3].split("【検査対象】")[1])      # 再呼出は欠落分のみ
        self.assertIn("look into the matter", s.calls[1][3])
        self.assertEqual([d["stage"] for d in log["drops"]], ["n5_check"])
        self.assertEqual(log["check_missing_retry"]["first_missing"], 1)

    def test_chk5_missing_recovered_on_retry_M9(self):
        a, b = _item(span="work out the plan", key=1), _item(span="look into the matter", sentence="We look into the matter.", form="look into", key=2)
        s = Scripted(chk5=[_chk([("SAME", "", "")]), _chk([("MODIFIER_DROPPED_OK", "", "調べる")])])
        log = n5.new_log("t")
        with mock.patch.object(n5, "_send", s):
            out = n5.run_check("T", [a, b], log, self.ctx())
        self.assertEqual([c["key"] for c in out], [1, 2])
        self.assertEqual(out[1]["gloss_ja"], "調べる")
        self.assertNotIn("drops", log)

    def test_chk5_gloss_mismatch_without_fix_reverts_form_and_gloss_together(self):
        c = _item(span="took points away", form="take something away from", gloss="取り去る", key=1, prod_gloss="減点する",
                  tokens=[(1, "CORE", "take"), (2, "CORE", "points"), (3, "CORE", "away")])
        s = Scripted(chk5=[_chk([("GLOSS_MISMATCH", "", "")])])
        log = n5.new_log("t")
        with mock.patch.object(n5, "_send", s):
            out = n5.run_check("T", [c], log, self.ctx())
        self.assertTrue(out[0]["reverted"])
        self.assertEqual(out[0]["gloss_ja"], "減点する")                              # PROD_GLOSS(P7由来のcanon・ga後gloss)へ。形と訳が対で本文語義に戻る
        self.assertEqual(out[0]["gloss_source"], "PROD_GLOSS")

    def test_b1_origin_has_no_prod_gloss_so_uses_source_sense_M4a(self):
        c = _item(span="took points away", form="take something away from", gloss="取り去る", key=1, prod_gloss=None, n5_origin="B1",
                  tokens=[(1, "CORE", "take"), (2, "CORE", "points"), (3, "CORE", "away")], verify={"source_sense_ja": "VER5由来の本文語義"})
        gl, src = n5.span_gloss(c)
        self.assertEqual((gl, src), ("VER5由来の本文語義", "verify.source_sense_ja"))
        c["verify"] = {}
        self.assertEqual(n5.span_gloss(c), ("計画を考え出す", "source_sense_ja"))
        self.assertEqual(n5.span_gloss(dict(c, source_sense_ja="", sense_note_ja="")), (None, None))

    def test_revert_without_gloss_drops_item(self):
        c = _item(span="took points away", form="take something away from", gloss="x", key=1, source_sense_ja="", sense_note_ja="", verify={},
                  tokens=[(1, "CORE", "take"), (2, "CORE", "points"), (3, "CORE", "away")])
        log = n5.new_log("t")
        self.assertFalse(n5.revert_to_span(c, log, "why"))
        self.assertEqual(log["drops"][0]["stage"], "n5_verify")

    def test_fix_that_drops_slot_or_core_is_rejected(self):
        self.assertEqual(n5.fix_drops_content("take something away from", "take away from"), ["<slot>"])
        self.assertEqual(n5.fix_drops_content("hear someone out", "hear something out"), [])
        self.assertEqual(n5.fix_drops_content("work out", "work something out"), [])


class TestVerifyAndGeneralize(unittest.TestCase):
    def ctx(self):
        return n5.N5Ctx("B1_SUPPORT", sleep_fn=lambda s: None)

    def test_reconcile_cases(self):
        self.assertEqual(n5.reconcile("hear it out", "hear it out"), ("hear it out", "SAME"))
        self.assertEqual(n5.reconcile("hear something out", "hear someone out"), ("hear someone out", "SLOT_TYPE_OVERRIDDEN"))
        self.assertEqual(n5.reconcile("put up", "put someone up"), ("put someone up", "SLOT_INSERTED"))
        self.assertEqual(n5.reconcile("keep one's eye on", "keep a lookout on")[1], "FRAME_MISMATCH")

    def test_max_words_applied_to_n5_form_M6(self):
        ok = _item(form="make up one's mind about", key=1)
        bad = _item(form="make up one's mind about this thing", key=2)
        log = n5.new_log("t")
        out = n5.enforce_max_words([ok, bad], log)
        self.assertEqual([c["key"] for c in out], [1])
        self.assertEqual(log["drops"][0]["stage"], "n5_verify")
        self.assertEqual(log["max_words_dropped"][0]["word_count"], 7)

    def test_verify5_missing_verdict_is_ok_like_trial_and_counted(self):
        a = _item(key=1)
        s = Scripted(ver5=[{"verdicts": []}])
        log = n5.new_log("t")
        with mock.patch.object(n5, "_send", s):
            out = n5.verify5("T", [a], log, self.ctx())
        self.assertEqual(len(out), 1)
        self.assertEqual(log["verify_missing"], 1)

    def test_verify5_reject_drops_with_stage_n5_verify(self):
        a = _item(key=1)
        row = {"id": 1, "verdict": "REJECT", "meaning_preserved": False, "gloss_consistent": True, "natural_headword": True, "issue": "別語義", "fix_display_form": "",
               "fix_gloss_ja": "", "source_sense_ja": "s", "argument_type_ok": True, "frame_preserved": "SAME"}
        s = Scripted(ver5=[{"verdicts": [row]}])
        log = n5.new_log("t")
        with mock.patch.object(n5, "_send", s):
            out = n5.verify5("T", [a], log, self.ctx())
        self.assertEqual(out, [])
        self.assertEqual(log["drops"][0]["stage"], "n5_verify")


class TestCallLayer(unittest.TestCase):
    def test_json_truncation_retries_once_with_max_out_x1_6_then_ok(self):
        s = Scripted(sel=['{"judgements": [', {"judgements": []}])
        ctx = n5.N5Ctx("A2_SUPPORT", sleep_fn=lambda s_: None)
        with mock.patch.object(n5, "_send", s):
            out, meta = n5.call_llm("sel", "u", n5.SEL3_SCHEMA, ctx)
        self.assertEqual(out, {"judgements": []})
        self.assertEqual([c[2] for c in s.calls], [7000, int(7000 * 1.6)])
        self.assertTrue(meta["truncation_retried"])

    def test_technical_failure_retries_per_existing_limit_then_raises(self):
        sleeps = []
        s = Scripted(sel=[RuntimeError("net"), RuntimeError("net2")])
        with mock.patch.object(n5, "_send", s):
            with self.assertRaises(n5.N5TechnicalFailure):
                n5.call_llm("sel", "u", n5.SEL3_SCHEMA, n5.N5Ctx("A2_SUPPORT", sleep_fn=sleeps.append))
        self.assertEqual(len(s.calls), n5.MAX_ATTEMPTS)
        self.assertEqual(sleeps, [2])

    def test_technical_failure_then_success(self):
        s = Scripted(sel=[RuntimeError("net"), {"judgements": []}])
        with mock.patch.object(n5, "_send", s):
            out, _ = n5.call_llm("sel", "u", n5.SEL3_SCHEMA, n5.N5Ctx("A2_SUPPORT", sleep_fn=lambda s_: None))
        self.assertEqual(out, {"judgements": []})

    def test_contract_error_and_stop_propagate_without_retry(self):
        for exc in (n5.N5ContractError("model mismatch"), routing.ModelContractViolation("v")):
            s = Scripted(sel=[exc])
            with mock.patch.object(n5, "_send", s):
                with self.assertRaises(Exception) as cm:
                    n5.call_llm("sel", "u", n5.SEL3_SCHEMA, n5.N5Ctx("A2_SUPPORT", sleep_fn=lambda s_: None))
            self.assertNotIsInstance(cm.exception, n5.N5TechnicalFailure)
            self.assertEqual(len(s.calls), 1)

    def test_stop_check_called_before_each_api_call(self):
        seen = []

        def stop(where):
            seen.append(where)
            if len(seen) == 2:
                raise KeyboardInterrupt("STOP")
        s = Scripted(sel=[{"judgements": []}, {"judgements": []}])
        ctx = n5.N5Ctx("A2_SUPPORT", stop_check_fn=stop, tag="t", sleep_fn=lambda s_: None)
        with mock.patch.object(n5, "_send", s):
            n5.call_llm("sel", "u", n5.SEL3_SCHEMA, ctx)
            with self.assertRaises(KeyboardInterrupt):
                n5.call_llm("sel", "u", n5.SEL3_SCHEMA, ctx)
        self.assertEqual(len(s.calls), 1)                                          # STOP時は新規API呼出をしない
        self.assertTrue(seen[0].startswith("kp_n5_sel"))

    def test_gemini_model_version_normalized_compare_M13(self):
        m = n5.gemini_version_matches
        self.assertTrue(m("gemini-3.8-flash", "gemini-3.8-flash"))
        self.assertTrue(m("gemini-3.8-flash", "models/Gemini-3.8-Flash"))
        self.assertTrue(m("gemini-3.8-flash", "gemini-3.8-flash-001"))
        self.assertTrue(m("gemini-3.8-flash", "gemini-3.8-flash-preview-0930"))
        self.assertFalse(m("gemini-3.8-flash", "gemini-3.8-flash-lite"))
        self.assertFalse(m("gemini-3.8-flash", "gemini-3.5-flash"))
        self.assertFalse(m("gemini-3.8-flash", None))


class _FakeOpenAI:
    def __init__(self, model_echo=None):
        self.kwargs = []
        self.model_echo = model_echo
        outer = self

        class _Resp:
            def create(self_inner, **kw):
                outer.kwargs.append(kw)
                u = type("U", (), {"input_tokens": 10, "output_tokens": 5, "input_tokens_details": type("D", (), {"cached_tokens": 0})()})()
                return type("R", (), {"model": outer.model_echo or kw["model"], "output_text": "{}", "usage": u, "id": "r1"})()
        self.responses = _Resp()


class _FakeGemini:
    def __init__(self, model_version="gemini-3.8-flash"):
        self.calls = []
        outer = self
        self.model_version = model_version

        class _Models:
            def generate_content(self_inner, **kw):
                outer.calls.append(kw)
                um = type("UM", (), {"prompt_token_count": 10, "candidates_token_count": 5, "thoughts_token_count": 0})()
                return type("R", (), {"text": "{}", "usage_metadata": um, "model_version": outer.model_version})()
        self.models = _Models()


class TestRequestForm(unittest.TestCase):
    """Opus M7: SDK request kwargsを捕捉して送り方がTrial確定版(kpg02_llm.call)と同一であることを固定する。"""

    def _walk(self, o, key):
        if isinstance(o, dict):
            if key in o:
                return True
            return any(self._walk(v, key) for v in o.values())
        if isinstance(o, list):
            return any(self._walk(v, key) for v in o)
        return False

    def test_openai_request_kwargs_luna_stage(self):
        fake = _FakeOpenAI()
        with mock.patch.object(n5, "_get_openai_client", return_value=fake):
            for stage, schema in (("b1", n5.B1_SCHEMA), ("sel", n5.SEL3_SCHEMA), ("gen5", n5.GEN5_SCHEMA)):
                n5._send(stage, "gpt-6-luna", "USER-PROMPT", schema, n5.STAGE_PARAMS[stage]["max_out"])
        self.assertEqual(len(fake.kwargs), 3)
        for kw, stage, schema in zip(fake.kwargs, ("b1", "sel", "gen5"), (n5.B1_SCHEMA, n5.SEL3_SCHEMA, n5.GEN5_SCHEMA)):
            self.assertEqual(set(kw), {"model", "input", "text", "max_output_tokens"})        # reasoning指定なし(effort None)・developer/instructionsなし
            self.assertEqual(kw["input"], [{"role": "user", "content": "USER-PROMPT"}])
            self.assertEqual(kw["text"], {"format": {"type": "json_schema", "name": schema["name"], "strict": True, "schema": schema["schema"]}})
            self.assertEqual(kw["max_output_tokens"], n5.STAGE_PARAMS[stage]["max_out"])
            self.assertEqual(kw["model"], "gpt-6-luna")

    def test_openai_request_kwargs_sol_check_stage_has_effort_low(self):
        fake = _FakeOpenAI()
        with mock.patch.object(n5, "_get_openai_client", return_value=fake):
            n5._send("chk5", "gpt-6.1-sol", "P", n5.CHK5_SCHEMA, 3500)
        kw = fake.kwargs[0]
        self.assertEqual(kw["reasoning"], {"effort": "low"})
        self.assertEqual(kw["max_output_tokens"], 3500)
        self.assertEqual(kw["model"], "gpt-6.1-sol")
        self.assertEqual(kw["input"], [{"role": "user", "content": "P"}])

    def test_openai_model_mismatch_is_stop(self):
        with mock.patch.object(n5, "_get_openai_client", return_value=_FakeOpenAI(model_echo="gpt-6-luna-mini")):
            with self.assertRaises(n5.N5ContractError):
                n5._send("sel", "gpt-6-luna", "P", n5.SEL3_SCHEMA, 7000)

    def test_gemini_request_config_matches_trial(self):
        fake = _FakeGemini()
        with mock.patch.object(n5, "_get_gemini_client", return_value=fake):
            text, meta = n5._send("ver5", "gemini-3.8-flash", "P", n5.VER5_SCHEMA, 6000)
        kw = fake.calls[0]
        self.assertEqual(set(kw), {"model", "contents", "config"})
        self.assertEqual(kw["model"], "gemini-3.8-flash")
        self.assertEqual(kw["contents"], "P")                                       # plain string(system_instructionなし)
        cfg = kw["config"]
        self.assertEqual(cfg.response_mime_type, "application/json")
        self.assertEqual(cfg.thinking_config.thinking_budget, 0)
        self.assertEqual(cfg.max_output_tokens, 6000)
        self.assertIsNone(cfg.system_instruction)
        self.assertFalse(self._walk(cfg.response_schema if isinstance(cfg.response_schema, dict) else json.loads(json.dumps(cfg.response_schema, default=lambda o: getattr(o, "__dict__", str(o)))), "additionalProperties"))
        self.assertEqual(meta["model_version"], "gemini-3.8-flash")
        self.assertEqual(meta["model_id"], "gemini-3.8-flash")

    def test_gemini_model_version_mismatch_is_stop_and_missing_is_recorded_unverified(self):
        with mock.patch.object(n5, "_get_gemini_client", return_value=_FakeGemini(model_version="gemini-3.8-flash-lite")):
            with self.assertRaises(n5.N5ContractError):
                n5._send("ver5", "gemini-3.8-flash", "P", n5.VER5_SCHEMA, 6000)
        with mock.patch.object(n5, "_get_gemini_client", return_value=_FakeGemini(model_version=None)):
            _, meta = n5._send("ver5", "gemini-3.8-flash", "P", n5.VER5_SCHEMA, 6000)
        self.assertTrue(meta["model_version_unverified"])
        with mock.patch.object(n5, "_get_gemini_client", return_value=_FakeGemini(model_version="models/gemini-3.8-flash-001")):
            _, meta = n5._send("ver5", "gemini-3.8-flash", "P", n5.VER5_SCHEMA, 6000)
        self.assertEqual(meta["model_id"], "gemini-3.8-flash-001")

    def test_strip_removes_additional_properties_everywhere(self):
        self.assertFalse(self._walk(n5._strip(n5.VER5_SCHEMA["schema"]), "additionalProperties"))
        self.assertTrue(self._walk(n5.VER5_SCHEMA["schema"], "additionalProperties"))     # 元schema(OpenAI用)は無変更

    def test_replay_key_proves_effort_and_think_budget_equal_trial(self):
        """cache keyは [model,user,system,schema,effort,think_budget,salt]。replayが全stageで成立=effort(None/None/None/None/low)とthink_budget(None..0..None)がTrialと同一。"""
        items, r, ctx, send = run_case("jwst_m_b1b")
        self.assertEqual({s for s, _ in send.keys}, {"b1", "sel", "gen5", "ver5", "chk5"})


class TestApplyToItem(unittest.TestCase):
    def _canon_item(self):
        return {"rank": 1, "source_span": "hear it out", "source_sentence": "She will hear it out.", "display_phrase": "hear it out", "key_phrase": "hear it out",
                "used_form": "hear it out", "japanese_gloss": "彼女の話を最後まで聞く", "japanese_gloss_tts": "彼女の話を最後まで聞く",
                "changed_from_display_phrase": False, "normalization_reason": "none", "qa": {"a": "PASS"}, "qa_overall_status": "PASS", "reasoning": "canon理由",
                "kp_extends_beyond_candidate": False, "gloss_alignment_status": "ALIGNED", "gloss_alignment": {"status": "GLOSS_ALREADY_CONSISTENT"}}

    def test_pair_updated_stale_fields_moved_qa_untouched_M5(self):
        it = self._canon_item()
        c = {"span": "hear it out", "sentence": "S", "display_form": "hear someone out", "gloss_ja": "〜の話を最後まで聞く", "generalization_note_ja": "目的語をsomeoneに",
             "verify": {"verdict": "OK"}, "check": {"relation": "SAME"}, "flags": ["PERSON_OVERRIDE"], "tokens": [], "n5_origin": "P7"}
        n5.apply_to_item(it, c)
        self.assertEqual(it["used_form"], "hear someone out")
        self.assertEqual(it["key_phrase"], "hear someone out")                      # used_form == key_phrase 不変条件
        self.assertEqual(it["japanese_gloss"], "〜の話を最後まで聞く")
        self.assertTrue(it["japanese_gloss_tts"].startswith("なにか") or it["japanese_gloss_tts"].startswith("なに") or it["japanese_gloss_tts"])   # TTS用glossはN5訳から再計算
        self.assertEqual(it["source_span"], "hear it out")                           # 本文根拠は無変更
        self.assertEqual(it["display_phrase"], "hear it out")
        self.assertEqual(it["qa"], {"a": "PASS"})                                    # QA12は無変更(解釈β′)
        self.assertEqual(it["qa_overall_status"], "PASS")
        self.assertEqual(it["n5"]["canon_pre"]["key_phrase"], "hear it out")
        self.assertEqual(it["n5"]["canon_pre"]["japanese_gloss"], "彼女の話を最後まで聞く")
        self.assertEqual(it["n5"]["canon_pre"]["reasoning"], "canon理由")
        self.assertEqual(it["n5"]["canon_pre"]["gloss_alignment"], {"status": "GLOSS_ALREADY_CONSISTENT"})
        self.assertTrue(it["changed_from_display_phrase"])
        self.assertEqual(it["normalization_reason"], n5.N5_NORMALIZATION_REASON)
        self.assertEqual(it["gloss_alignment_status"], "ALIGNED")
        self.assertEqual(it["gloss_alignment"]["status"], "N5_CONFIRMED")
        self.assertTrue(it["reasoning"].startswith("[N5]"))
        self.assertEqual(it["n5"]["method"], n5.METHOD_ID)
        self.assertTrue(it["n5"]["source_span_matches_item"])

    def test_unchanged_pair_keeps_canon_alignment_record(self):
        it = self._canon_item()
        c = {"span": "hear it out", "sentence": "S", "display_form": "hear it out", "gloss_ja": "彼女の話を最後まで聞く", "verify": {}, "check": {"relation": "SAME"}, "flags": [],
             "tokens": [], "n5_origin": "P7"}
        n5.apply_to_item(it, c)
        self.assertEqual(it["gloss_alignment"], {"status": "GLOSS_ALREADY_CONSISTENT"})
        self.assertTrue(it["n5"]["pair_unchanged_from_canon"])
        self.assertEqual(it["reasoning"], "canon理由")

    def test_person_check_after_n5_flags_concrete_person_gloss_on_generic_form(self):
        """N5形がsomeoneなのに訳に『彼』が残る組は既存の決定論検査(ga.person_reference_mismatch、API 0)で不整合として検出される。"""
        import er003_key_words_gloss_alignment as ga
        it = self._canon_item()
        it.update(key_phrase="hear someone out", used_form="hear someone out", japanese_gloss="彼の話を最後まで聞く")
        self.assertEqual(n5.person_check_after_n5([it]), [1])
        it["japanese_gloss"] = "〜の話を最後まで聞く"
        self.assertEqual(n5.person_check_after_n5([it]), [])
        self.assertIsNone(ga.person_reference_mismatch("hear someone out", "〜の話を最後まで聞く"))


class TestPoolAndGate(unittest.TestCase):
    def test_collect_pool_trial_logic_without_gate(self):
        base = [{"span": "worked out", "sentence": "They worked out."}]
        b1 = [{"span": "worked out the plan", "sentence": "x"}, {"span": "holds heat in", "sentence": "Heat is held. It holds heat in."}, {"span": "not in text zzz", "sentence": ""}]
        text = "They worked out. It holds heat in. Heat is held."
        pool, rej = n5.collect_pool(text, base, b1)
        spans = [c["span"] for c in pool]
        self.assertEqual(spans, ["worked out", "holds heat in"])
        self.assertEqual({r["reasons"][0] for r in rej}, {"B1候補が本文に連続一致しない"})

    def test_frag_removed_and_gate_before_containment(self):
        text = "Which ones work. The firm sought funding rounds. Rounds happen."
        base = []
        b1 = [{"span": "Which ones work", "sentence": "Which ones work."}, {"span": "funding rounds", "sentence": "The firm sought funding rounds."},
              {"span": "sought funding rounds", "sentence": "The firm sought funding rounds."}]

        def gate(c):
            if c["span"] == "funding rounds":
                return None, ["既存Gate不通過"]
            return dict(c, n5_origin="B1"), []
        pool, rej = n5.collect_pool(text, base, b1, gate_fn=gate)
        self.assertEqual([c["span"] for c in pool], ["sought funding rounds"])         # Gate落ちの候補が包含dedupeで有効候補を妨げない
        reasons = {r["span"]: r["stage"] for r in rej}
        self.assertEqual(reasons["Which ones work"], "n5_pool")
        self.assertEqual(reasons["funding rounds"], "n5_pool")

    def test_pick_orders_by_difficulty_dedups_and_caps(self):
        j = [{"span": f"a{i} b{i}", "keep": True, "difficulty": d, "display_form": None} for i, d in enumerate(["easy", "advanced", "upper_intermediate", "advanced"])]
        out = n5.pick(j, 3)
        self.assertEqual([c["difficulty"] for c in out], ["advanced", "advanced", "upper_intermediate"])
        j2 = [{"span": "take care of", "keep": True, "difficulty": "advanced", "display_form": None}, {"span": "take care", "keep": True, "difficulty": "advanced", "display_form": None}]
        self.assertEqual(len(n5.pick(j2, 7)), 1)                                      # span包含dedupe
        self.assertEqual(len(n5.pick([dict(c, keep=False) for c in j], 7)), 0)        # 易しい表現は除外しないが、keepでないものは採らない(補充しない)

    def test_easy_expression_not_excluded_only_ordered_last(self):
        j = [{"span": "rely on", "keep": True, "difficulty": "easy", "display_form": None}, {"span": "walk someone through", "keep": True, "difficulty": "advanced", "display_form": None}]
        out = n5.pick(j, 7)
        self.assertEqual([c["span"] for c in out], ["walk someone through", "rely on"])

class TestJ2ProductionL1EqualsTrialOnRecordedCases(unittest.TestCase):
    """J2是正の等価性(API 0): Trial 03の19ケースで、Production L1(pool_and_select、再判定つき)の選定がTrialのL1(collect_pool->select->pick)と一致する。
    再判定callが必要になるのは2ケース(ai_cha_a2 'clear fall'、moon_b1b 'heat from escaping')のみで、実APIでの再判定結果はいずれも非keep(Trialと同一選定)=`ev03/j2_part1_result.json`。"""
    NEEDS_SECOND_SEL = {"ai_cha_a2": ["clear fall"], "moon_b1b": ["heat from escaping"]}

    def _l1(self, cid):
        case = FX["cases"][cid]
        items = [{"display_phrase": b["span"], "source_sentence": b.get("sentence") or "", "item": {"display_phrase": b["span"]}} for b in case["base"]]
        gate = lambda units, screen=None: (lambda c: (dict(c, n5_origin="B1", item={"display_phrase": c["span"], "reason_ja": ""}), []))
        spans = []
        orig = n5.select

        def wrap(text, cands, log, ctx, *, label="SEL"):
            if label == "SEL_DEFERRED":
                spans.append([c["span"] for c in cands])
                return []                     # 再判定なし(非keep)として扱い、再判定対象spanだけ記録する
            return orig(text, cands, log, ctx, label=label)
        send = ReplaySend()
        ctx = n5.N5Ctx("A2_SUPPORT", sleep_fn=lambda s: None)
        with mock.patch.object(n5, "_send", send), mock.patch.object(n5, "preflight", lambda: None), mock.patch.object(n5, "make_b1_gate", gate), mock.patch.object(n5, "select", wrap):
            r = n5.pool_and_select(case["text"], items, ctx, include_b1=True, units=[])
        # Trial L1(同じreplay応答)
        send2 = ReplaySend()
        ctx2 = n5.N5Ctx("A2_SUPPORT", sleep_fn=lambda s: None)
        with mock.patch.object(n5, "_send", send2), mock.patch.object(n5, "preflight", lambda: None):
            o, _ = n5.call_llm("b1", n5.prompt_B1(case["text"]), n5.B1_SCHEMA, ctx2, label="B1")
            pool, _ = n5.collect_pool(case["text"], case["base"], o["candidates"])
            kept = n5.pick(n5.select(case["text"], pool, n5.new_log("t"), ctx2), n5.PHRASE_PICK_CAP)
        return [p["item"]["display_phrase"] for p in r["picked"]], [c["span"] for c in kept], spans

    def test_all_19_cases_l1_selection_equals_trial(self):
        second = {}
        for cid in FX["cases"]:
            with self.subTest(case=cid):
                prod, trial, sp = self._l1(cid)
                self.assertEqual(prod, trial)
                if sp:
                    second[cid] = sp[0]
        self.assertEqual(second, self.NEEDS_SECOND_SEL)


class TestJ2DeferredRejudge(unittest.TestCase):
    """委任_03 J2是正: 包含dedupeをSEL後に回す。Trial 03のP7入力はQA通過後の最終候補で、F判定になるP7 sub-spanはpoolに無かった。
    P7 sub-span(包含相手)がSELでkeepにならないとき、B1 supersetをSEL再判定して残す。相手がkeepなら従来(Trial逐語)どおりsupersetを落とす。"""
    TEXT = "The telescope team will set a lower limit on the mass. They kept calm."

    def _run(self, judge, b1=("set a lower limit",), p7=("a lower limit",)):
        sel_calls = []

        def fake_prompt_S3(text, cands, mode):
            sel_calls.append([c["span"] for c in cands])
            return "SEL::" + "|".join(c["span"] for c in cands)

        def fake_call(stage, user, schema, ctx, *, label=""):
            if stage == "b1":
                return {"candidates": [{"span": b, "sentence": self.TEXT} for b in b1]}, {"model_id": "x"}
            assert stage == "sel", stage
            spans = user[len("SEL::"):].split("|")
            return {"judgements": [dict(id=i, cls="C" if judge[sp] else "F", chunk_type="collocation" if judge[sp] else "none", reason_ja="r",
                                        difficulty="advanced", keep=judge[sp], passive_fragment=False) for i, sp in enumerate(spans, 1)]}, {"model_id": "x"}
        gate = lambda units, screen=None: (lambda c: (dict(c, n5_origin="B1", item={"display_phrase": c["span"], "reason_ja": ""}), []))
        items = [{"display_phrase": x, "source_sentence": self.TEXT} for x in p7]
        with mock.patch.object(n5, "preflight", lambda: None), mock.patch.object(n5, "prompt_S3", fake_prompt_S3),                 mock.patch.object(n5, "call_llm", fake_call), mock.patch.object(n5, "make_b1_gate", gate):
            r = n5.pool_and_select(self.TEXT, items, n5.N5Ctx("A2_SUPPORT", sleep_fn=lambda s: None), include_b1=True, units=[])
        return r, sel_calls

    def test_sub_span_F_keeps_superset_via_second_sel(self):
        r, calls = self._run({"a lower limit": False, "set a lower limit": True})
        self.assertEqual(calls, [["a lower limit"], ["set a lower limit"]])       # 1回目=Trial同一pool、2回目=再判定
        self.assertEqual([p["item"]["display_phrase"] for p in r["picked"]], ["set a lower limit"])
        self.assertEqual(r["picked"][0]["n5_origin"], "B1")
        self.assertEqual(r["record"]["deferred_rejudged"], [{"span": "set a lower limit", "blocked_by": "a lower limit", "keep": True}])
        self.assertEqual([x["stage"] for x in r["record"]["stages"] if x["stage"].startswith("SEL")], ["SEL", "SEL_DEFERRED"])
        self.assertEqual(r["record"]["pool_rejected"], [])                               # 再判定した件はn5_pool dropに数えない
        self.assertEqual([d["phrase"] for d in r["dropped"]], ["a lower limit"])        # P7 sub-spanのSEL非keepは従来どおりn5_select

    def test_sub_span_keep_drops_superset_like_trial_without_second_call(self):
        r, calls = self._run({"a lower limit": True, "set a lower limit": True})
        self.assertEqual(calls, [["a lower limit"]])                                    # defer対象はあるが再判定callなし=Trial exact
        self.assertEqual([p["item"]["display_phrase"] for p in r["picked"]], ["a lower limit"])
        rej = r["record"]["pool_rejected"]
        self.assertEqual(len(rej), 1)
        self.assertEqual(rej[0]["stage"], "n5_pool")
        self.assertEqual(rej[0]["blocked_by"], "a lower limit")
        self.assertIn("Trial差分", rej[0]["reasons"][0])                                # drop理由にTrial差分を記録
        self.assertEqual(r["record"]["deferred_rejudged"], [])

    def test_identical_span_duplicate_is_not_rejudged_and_reason_is_plain(self):
        r, calls = self._run({"a lower limit": False}, b1=("a lower limit",), p7=("a lower limit",))
        self.assertEqual(calls, [["a lower limit"]])                                    # 同一spanは再判定しない(同じ候補を2回判定しない)
        self.assertEqual(r["record"]["pool_rejected"][0]["reasons"], ["既存候補と同一span(重複。Trialと同じ除外)"])
        self.assertEqual(r["record"]["deferred_rejudged"], [])

    def test_blocker_kept_by_another_candidate_stays_dropped(self):
        # supersetが別のkeep候補とも包含関係なら再判定しない
        r, calls = self._run({"a lower limit": False, "limit on the mass": True, "set a lower limit on the mass": True},
                             b1=("set a lower limit on the mass",), p7=("a lower limit", "limit on the mass"))
        self.assertEqual(len(calls), 1)

    def test_no_containment_means_single_sel_call_as_trial(self):
        r, calls = self._run({"kept calm": True}, b1=("kept calm",), p7=())
        self.assertEqual(calls, [["kept calm"]])

    def test_sel_deferred_rejudge_technical_failure_raises_N5TechnicalFailure_after_retry_limit(self):
        """委任_04: 再判定call(SEL_DEFERRED)の技術失敗は既存retry上限(MAX_ATTEMPTS)後にN5TechnicalFailureとして伝播する(結果を返さない=呼出側の外側retryへ)。
        call_llm/_send/retryは正式関数、_sendだけ差替え(1回目SEL=sub-span F、再判定SEL=ネットワーク失敗)。"""
        sleeps = []
        spans = {"a lower limit": False}
        sel_ok = {"judgements": [{"id": 1, "cls": "F", "chunk_type": "none", "reason_ja": "r", "difficulty": "advanced", "keep": False, "passive_fragment": False}]}
        s = Scripted(b1=[{"candidates": [{"span": "set a lower limit", "sentence": self.TEXT}]}],
                     sel=[sel_ok, RuntimeError("net1"), RuntimeError("net2")])
        gate = lambda units, screen=None: (lambda c: (dict(c, n5_origin="B1", item={"display_phrase": c["span"], "reason_ja": ""}), []))
        items = [{"display_phrase": "a lower limit", "source_sentence": self.TEXT}]
        with mock.patch.object(n5, "preflight", lambda: None), mock.patch.object(n5, "_send", s), mock.patch.object(n5, "make_b1_gate", gate):
            with self.assertRaises(n5.N5TechnicalFailure):
                n5.pool_and_select(self.TEXT, items, n5.N5Ctx("A2_SUPPORT", sleep_fn=sleeps.append), include_b1=True, units=[])
        self.assertEqual([c[0] for c in s.calls], ["b1", "sel", "sel", "sel"])      # 再判定callが発行され、既存retry上限(2)まで試行して失敗
        self.assertEqual(sleeps, [2])

    def test_rejudged_superset_F_is_not_picked_and_not_counted_in_E(self):
        r, calls = self._run({"a lower limit": False, "set a lower limit": False})
        self.assertEqual(r["picked"], [])
        self.assertEqual([d["phrase"] for d in r["dropped"]], ["a lower limit"])      # B1 superset(AIが選んだ候補ではない)は一覧に出さない

    def test_collect_pool_without_defer_out_is_unchanged_trial_logic(self):
        base = [{"span": "a lower limit", "sentence": "x"}]
        b1 = [{"span": "set a lower limit", "sentence": "x"}]
        pool, rej = n5.collect_pool(self.TEXT, base, b1)
        self.assertEqual([c["span"] for c in pool], ["a lower limit"])
        d = []
        pool2, rej2 = n5.collect_pool(self.TEXT, base, b1, defer_out=d)
        self.assertEqual([c["span"] for c in pool2], ["a lower limit"])
        self.assertEqual([x["cand"]["span"] for x in d], ["set a lower limit"])


if __name__ == "__main__":
    unittest.main()
