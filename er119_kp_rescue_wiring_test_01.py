# -*- coding: utf-8 -*-
"""KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01 委任_02: 救済フロー配線後の統合test(API 0・全LLM関数をmock)。

固定する性質(Opus OPUS_REVIEW_03 M1〜M4 / R1〜R6 と配線4箇所):
  W1 救済発火: 選定段[D1再アンカー・慣用句の核]とcanonicalization段[M1窓内再導出]が、正式経路 generate_candidates を通って候補に反映される
  W2 resume読み戻し: 保存済み候補は再計算せず(LLM 0)、候補ファイルはバイト不変
  W3 kill switch: EIGO_KP_RESCUE=0 は従来動作(救済なし)。環境変数はEnvで明示固定(シェルの値に依存しない)
  W4 M2: generate_candidates の外(旧経路)では環境変数ONでも発火しない
  W5 M1: 救済後の句が他の句と重複するなら救済しない(承認済みblocking条件「重複」を迂回しない)
  W6 M3: 救済済みでauto不可の候補があれば外側retry(F1累積除外には入れない)
  W7 R1/R2/R4/R6
実行: .venv\\Scripts\\python.exe run_project_regression.py --pattern "er119*_test_*.py"
"""
from __future__ import annotations

import test_state_isolation_01  # noqa: F401

import functools
import json
import os
import sys
import unittest
from unittest import mock

from er119_test_support_01 import ARTICLE, Env, KpTestCase, rd  # noqa: F401

import er003_v1_n3_01_scaffold_generate as sc
import er030_key_phrase_db_hybrid_core_01 as core
import er105_kp_fulltext_selector_01 as ft
import er119_kp_candidates_01 as kcand
import er119_kp_human_review_01 as rv
import er125_kp_rescue_production_01 as r

ART = ("# Wiring test\n\nThe owner pushed prices up in May. They let people try whatever catches their interest. "
       "The cafe keeps raw beans in stock. Her laughter rose above the other voices. Nobody knew the plan, and I guess it can’t be helped. "
       "In the end, the band took a sharp turn.\n")
# KP-PHRASE7-WORD5-PRODUCTION-01: フレーズは全てcall1(P7・最大7)。call2(W5')は単語のみなので空(適切な単語が無い=件数不足を許容)
CALL1 = [{"phrase": "catch their interest", "word_count": 3}, {"phrase": "pushed prices up", "word_count": 3}, {"phrase": "in stock", "word_count": 2},
         {"phrase": "rose above", "reason_ja": "M1", "word_count": 2}, {"phrase": "it can’t be helped", "reason_ja": "idiom", "word_count": 4},
         {"phrase": "took a sharp turn", "reason_ja": "plain", "word_count": 4}]
CALL2 = []
CANON_KEYS = {"rose above": "rise above the other voices"}      # LLMが長い原形key(窓外tailつき)を返す -> M1で'rise above'


def _cand(doc, phrase):
    return next(c for c in doc["candidates"] if c["selection_phrase"] == phrase)


class TestWiredFlow(KpTestCase):
    def _gen(self, **kw):
        env_kw = dict(call1=CALL1, call2=CALL2, canon_keys=CANON_KEYS)
        env_kw.update(kw)
        env = Env(self.tmp, **env_kw)
        return env

    def test_w1_all_rescue_paths_flow_into_candidates(self):
        with self._gen() as env:
            out = self.ensure(env, text=ART)
        self.assertEqual(out["state"], "PENDING", out)
        doc = rv.load_candidates(self.kp_dir)
        self.assertEqual(rv.candidates_sha256(doc), doc["candidates_sha256"])
        self.assertEqual(doc["dropped"], [])
        self.assertEqual(len(doc["candidates"]), 6)
        # 選定段D1: 'catch their interest' -> 本文表層 'catches their interest'
        d1 = _cand(doc, "catches their interest")
        self.assertTrue(d1["flags"]["rescued"])
        self.assertEqual(d1["rescue"]["selection"]["code"], r.R_D1)
        self.assertEqual(d1["rescue"]["selection"]["original_phrase"], "catch their interest")
        self.assertIn("catch their interest", d1["rescue_note"])
        self.assertTrue(d1["auto_eligible"])                               # 選定段のみの救済は後続の通常canonicalizationを通る=追加条件なし
        # 選定段 慣用句の核: 'it can't be helped' -> 'can't be helped'
        idi = next(c for c in doc["candidates"] if r._hw_norm(c["selection_phrase"]) == "can't be helped")
        self.assertEqual(idi["rescue"]["selection"]["code"], r.R_IDIOM_CORE)
        self.assertIsNotNone(idi["rescue"]["selection"]["headword"])
        # canonicalization段M1: LLMのkey 'rise above the other voices' -> 窓内再導出 'rise above'
        m1 = _cand(doc, "rose above")
        self.assertEqual(m1["used_form"], "rise above")
        self.assertEqual(m1["rescue"]["canonicalization"]["code"], r.R_M1)
        self.assertEqual(m1["rescue"]["gloss"]["status"], r.GLOSS_REALIGNED)
        self.assertEqual(m1["rescue"]["qa"]["status"], r.QA_REJUDGED_PASS)
        self.assertEqual(m1["gates"]["canonicalization"], "RESCUED_QA_REJUDGED_PASS")
        self.assertTrue(m1["auto_eligible"])
        self.assertTrue(r.verify_persisted_rescue(m1))
        rr = r.reverify_persisted_rescue(m1)
        self.assertTrue(rr["checked"] and rr["ok"], rr)
        # 通常候補は無変更(rescueなし)
        plain = _cand(doc, "pushed prices up")
        self.assertNotIn("rescue", plain)
        self.assertFalse(plain["flags"].get("rescued", False))
        # doc単位provenance(R2)
        prov = doc["rescue_provenance"]
        self.assertEqual(prov["lexicon_sha256"], r.LEXICON_SHA256)
        self.assertEqual(prov["lexicon_status"], "ok")
        self.assertTrue(prov["rescue_enabled"])
        self.assertEqual(prov["schema"], r.SCHEMA)
        # HR依頼書に救済旗が出る
        md = rd(f"{self.kp_dir}/kp_human_review_request.md")
        self.assertIn("修正済み(元: catch their interest", md)

    def test_w1b_candidates_sha_covers_rescue_meta(self):
        with self._gen() as env:
            self.ensure(env, text=ART)
        doc = rv.load_candidates(self.kp_dir)
        sha = rv.candidates_sha256(doc)
        _cand(doc, "rose above")["rescue"]["canonicalization"]["rescued_key"] = "tampered"
        self.assertNotEqual(rv.candidates_sha256(doc), sha)
        doc2 = rv.load_candidates(self.kp_dir)
        _cand(doc2, "rose above")["rescue"]["canonicalization"]["validator_args"]["key"] = "tampered"
        self.assertFalse(r.verify_persisted_rescue(_cand(doc2, "rose above")))        # R4: 3者一致の確認

    def test_w2_resume_reads_back_without_any_llm_call(self):
        with self._gen() as env:
            self.ensure(env, text=ART)
            calls = env.total_llm_calls()
            before = rd(f"{self.kp_dir}/kp_candidates.json")
            out = self.ensure(env, text=ART)                                         # 同引数で再起動
            self.assertEqual(out["state"], "PENDING")
            self.assertEqual(env.total_llm_calls(), calls)                           # 再計算なし(API 0)
            self.assertEqual(rd(f"{self.kp_dir}/kp_candidates.json"), before)

    def test_w2b_resume_logs_provenance_drift_without_stopping(self):
        with self._gen() as env:
            self.ensure(env, text=ART)
            drift = dict(r.provenance(), lexicon_sha256="0" * 64)
            with mock.patch.object(r, "provenance", lambda: drift):
                with self.assertLogs("kp_review", level="WARNING") as cm:
                    out = self.ensure(env, text=ART)
            self.assertEqual(out["state"], "PENDING")                                # 停止しない
            self.assertTrue(any("provenance drift" in m for m in cm.output), cm.output)

    def test_w3_kill_switch_off_is_pre_rescue_behavior(self):
        with self._gen(rescue_env="0") as env:
            out = self.ensure(env, text=ART)
        # 『catch their interest』は本文に連続一致しない -> call1が3回INVALID -> 外側retry尽きて失敗(従来どおり。救済で拾われない)
        self.assertEqual(out["state"], "FAILED", out)
        self.assertEqual(env.n["gloss"], 0)

    def test_w3b_kill_switch_off_candidates_unrescued_when_phrases_valid(self):
        call1 = [{"phrase": "pushed prices up", "word_count": 3}, {"phrase": "in stock", "word_count": 2}, {"phrase": "took a sharp turn", "word_count": 4},
                 {"phrase": "rose above", "reason_ja": "x", "word_count": 2}]
        with self._gen(rescue_env="0", call1=call1, call2=[]) as env:
            self.ensure(env, text=ART)
        doc = rv.load_candidates(self.kp_dir)
        self.assertTrue(all("rescue" not in c for c in doc["candidates"]))
        # 救済なし: LLMの不適切なkey('rise above the other voices')は従来どおりGate除外(M1で拾われない)
        self.assertEqual([d["phrase"] for d in doc["dropped"] if d["stage"] == "canonicalization"], ["rose above"])
        self.assertEqual(doc["rescue_provenance"]["rescue_enabled"], False)

    def test_w4_old_routes_do_not_rescue_even_when_env_on(self):
        self.assertTrue(r.rescue_enabled())
        self.assertFalse(r._rescue_ctx.get())
        units = core.build_sentence_units(ART)

        def make_call_fn(msg):
            def fn():
                return json.dumps({"items": [{"phrase": "catch their interest", "word_count": 3}, {"phrase": "in stock", "word_count": 2}]}), "gpt-6-luna", "x"
            return fn
        with mock.patch("time.sleep", lambda s: None):
            g = ft.run_selection_gate(ART, make_call_fn, units=units, max_attempts=2)
        self.assertEqual(g["status"], ft.STATUS_INVALID)                              # 旧経路(Z旧kp_fn/Y旧アダプタ/run_selection_gate他呼出元)は従来どおり除外
        self.assertIsNone(g["items"])
        v = ft.validate_and_resolve([{"phrase": "catch their interest", "declared_word_count": None}], units)
        self.assertFalse(v["ok"])
        self.assertNotIn("selection_rescue", v["resolved"][0])
        self.assertTrue(ft.contains_finite_aux_role_based("might as well"))
        # canonicalization側: rescue引数の既定はFalse(A/B/C・旧候補なし経路・test注入は影響を受けない)
        import inspect
        self.assertIs(inspect.signature(sc.run_key_phrase_canonicalization).parameters["rescue"].default, False)

    def test_w4b_context_is_reset_after_generate_candidates_even_on_error(self):
        self.assertFalse(r._rescue_ctx.get())
        with self.assertRaises(Exception):
            kcand.generate_candidates("t", "/nonexistent/\0bad", "a", "A2", "a2", 1, [], select_fn=lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")))
        self.assertFalse(r._rescue_ctx.get())

    def test_w5_m1_rescued_phrase_duplicate_is_not_bypassed(self):
        units = core.build_sentence_units(ART)
        with r.rescue_context():
            # 連続一致する句が先 -> 後の『catch their interest』は救済すると重複になるので救済せず、元のreason(本文に連続一致しない)を維持
            v = ft.validate_and_resolve([{"phrase": "catches their interest", "declared_word_count": None},
                                         {"phrase": "catch their interest", "declared_word_count": None}], units)
            self.assertFalse(v["ok"])
            self.assertNotIn("selection_rescue", v["resolved"][1])
            self.assertTrue(any("本文に連続一致しない" in x for x in v["item_reasons"][0]["reasons"]), v["item_reasons"])
            # 救済対象が先 -> 救済は成立するが、後ろの『catches their interest』は『重複』(承認済みblocking条件)で止まる
            v2 = ft.validate_and_resolve([{"phrase": "catch their interest", "declared_word_count": None},
                                          {"phrase": "catches their interest", "declared_word_count": None}], units)
            self.assertFalse(v2["ok"])
            self.assertEqual(v2["resolved"][0]["phrase"], "catches their interest")
            self.assertTrue(any("重複" in x for ir in v2["item_reasons"] for x in ir["reasons"]), v2["item_reasons"])
            # 救済単独: wc/span/rec欄は救済後の句で再計算
            v3 = ft.validate_and_resolve([{"phrase": "catch their interest", "declared_word_count": 3}], units)
            self.assertTrue(v3["ok"])
            rec = v3["resolved"][0]
            self.assertEqual((rec["phrase"], rec["word_count"], rec["source_span"]), ("catches their interest", 3, "catches their interest"))
            self.assertEqual(rec["selection_rescue"]["code"], r.R_D1)
            item = ft.build_original_items(v3["resolved"])[0]
            self.assertEqual(item["selection_rescue"]["original_phrase"], "catch their interest")
            self.assertEqual(item["display_phrase"], "catches their interest")
        # 救済なしの項目はキー自体を持たない(従来とバイト同一)
        v4 = ft.validate_and_resolve([{"phrase": "in stock", "declared_word_count": None}], units)
        self.assertNotIn("selection_rescue", ft.build_original_items(v4["resolved"])[0])

    def test_w5b_call2_vocab_selection_duplicate_with_top3_after_rescue_is_dropped(self):
        units = core.build_sentence_units(ART)
        top3 = [{"display_phrase": "catches their interest"}]
        with r.rescue_context():
            out = kcand.run_vocab_selection(ART, units, top3, [], make_call_fn=lambda m: (lambda: (json.dumps({"items": [
                {"phrase": "catch their interest", "reason_ja": "dup", "word_count": 3}]}), "gpt-6-luna", "x")), sleep_fn=lambda s: None)
        self.assertEqual(out["status"], "OK")
        self.assertEqual(out["kept"], [])
        self.assertEqual(out["dropped"][0]["stage"], "duplicate_of_top3")

    def test_w6_m3_rescued_but_not_auto_triggers_outer_retry_without_f1_exclusion(self):
        call1 = [{"phrase": "pushed prices up", "word_count": 3}, {"phrase": "in stock", "word_count": 2}, {"phrase": "took a sharp turn", "word_count": 4}]
        # 'pushed prices up'のLLM keyが不適切 -> revertで救済、QA再判定のkeyが不一致(NOT_REJUDGED)=auto不可。n_auto=2<3かつGate除外0件
        # 『rescued_not_auto脚』は補完OFF(EIGO_KP_BACKFILL=0)の現行条件。補完ON(既定)では撤去(Opus M-3、初回合格候補を入れ替えない。er119_kp_backfill_test_01 TBF18)
        with Env(self.tmp, call1=call1, call2=[], canon_keys={"pushed prices up": "totally different"}, qa_mismatch={"pushed prices up"}) as env,                 mock.patch.dict(os.environ, {"EIGO_KP_BACKFILL": "0"}):
            self.ensure(env, text=ART)
        doc = rv.load_candidates(self.kp_dir)
        c = _cand(doc, "pushed prices up")
        self.assertEqual(c["rescue"]["canonicalization"]["code"], r.R_REVERT)
        self.assertEqual(c["rescue"]["qa"]["status"], r.QA_NOT_REJUDGED)
        self.assertFalse(c["auto_eligible"])
        self.assertEqual(c["gates"]["canonicalization"], "RESCUED_QA_NOT_REJUDGED")
        self.assertEqual(env.n["call1"], sc.KP_OUTER_RETRY_MAX)                        # 外側retryが発動(上限まで)。承認済みmax_outer内
        for m in env.messages1[1:]:
            self.assertNotIn("「pushed prices up」", m)     # F1累積除外へ入れない(再選定でHR候補として残り得る)=除外指定noteに現れない
        self.assertEqual(doc["outer_retry_log"][0]["rescued_not_auto"], [c["candidate_id"]])
        self.assertTrue(c["flags"]["rescued"])

    def test_w6b_rescued_and_auto_ok_does_not_retry(self):
        call1 = [{"phrase": "pushed prices up", "word_count": 3}, {"phrase": "in stock", "word_count": 2}, {"phrase": "took a sharp turn", "word_count": 4}]
        with Env(self.tmp, call1=call1, call2=[], canon_keys={"pushed prices up": "totally different"}) as env:
            self.ensure(env, text=ART)
        doc = rv.load_candidates(self.kp_dir)
        self.assertTrue(_cand(doc, "pushed prices up")["auto_eligible"])
        self.assertEqual(env.n["call1"], 1)                                            # 救済成功で候補が足りれば再選定しない

    def test_w7_human_ng_original_phrase_blocks_rescued_candidate(self):
        ng = [rv.make_ng_entry({"candidate_id": rv.candidate_id_for("catch their interest"), "selection_phrase": "catch their interest",
                                "used_form": "catch their interest"}, "NG", "tester")]
        cand = {"selection_phrase": "catches their interest", "used_form": "catches their interest",
                "rescue": {"selection": {"original_phrase": "catch their interest", "code": r.R_D1}}}
        self.assertTrue(r.ng_blocked(cand, ng, rv.match_ng, rv.candidate_id_for))
        self.assertEqual(r.ng_match_originals(cand, ng, rv.match_ng, rv.candidate_id_for), "exact")
        # R6: 選定段(apply_exclusions)で救済前の元句も照合する
        units = core.build_sentence_units(ART)
        with r.rescue_context():
            v = ft.validate_and_resolve([{"phrase": "catch their interest", "declared_word_count": None}], units)
        out = ft.apply_exclusions(v, [{"phrase": "catch their interest", "reasons": ["Humanが不適切(NG)と指定"]}], final_attempt=False)
        self.assertFalse(out["ok"])
        self.assertEqual(len(out["exclusion_hits"]), 1)

    def test_w7b_idiom_flag_only_for_phrases_the_guard_would_reject(self):
        have_say = {"selection_phrase": "have a say", "item": {}}
        r.annotate_candidate(have_say)
        self.assertNotIn("idiom_exception", have_say.get("flags", {}))                # R1: 既存guardが拒否しない句には付けない
        might = {"selection_phrase": "might as well", "item": {}}
        r.annotate_candidate(might)
        self.assertIn("idiom_exception", might["flags"])
        for hw in ("have one's shit together", "have someone by the balls", "have the hots for", "have several seats"):
            self.assertIsNone(r.idiom_exception(hw), hw)                              # R1: 卑語・俗語はdenylist

    def test_w8_provenance_drift_helper(self):
        self.assertEqual(r.provenance_drift(None), [])
        self.assertEqual(r.provenance_drift(r.provenance()), [])
        self.assertTrue(r.provenance_drift(dict(r.provenance(), lexicon_status="sha_mismatch_code")))


if __name__ == "__main__":
    unittest.main()
