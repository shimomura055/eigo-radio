# -*- coding: utf-8 -*-
"""LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01 委任_06(B1): 採用take記録`final_adoption`(最小)+resume時LR根拠保存(M-4)のoffline test。
API 0・実sleep 0。記録追記のみ=Gate判定・retry回数・待機・Fallback Style・LR範囲・TTS呼出が不変であること(既存test群PASSと併せて)を確認する。

(a) finishで`final_adoption`がBlockProgress `verified`(depth,ordinal)と整合 (b) Z ctx採用時の記録 (c) Store key B hit時の`source=store_reuse`
(d) Z `build_entry`透過 (e) resume後にLR根拠が読める (f) 旧entry(記録なし)で例外が出ない。
"""
from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from unittest import mock

import er127_test_fakes_01 as F
import er127_tts_block_policy_01 as blk
import er127_tts_block_policy_01_test_01 as T

SLOTS = {1: "①", 2: "②", 3: "③"}


def progress_state(w):
    level_dir = os.path.dirname(os.path.dirname(w.out_path))
    p = f"{level_dir}/audit/tts_block_progress/{w.seg}.json"
    with open(p, encoding="utf-8") as f:
        return json.load(f)


class FinalAdoptionRecordTests(T.Base):
    KEYS = {"depth", "ordinal", "slot", "style_mode", "sent_style_sha", "attempt_audio_sha", "source"}

    def _consistent(self, fa, st):
        self.assertEqual(fa["source"], "tts_attempt")
        a = st["blocks"][str(fa["depth"])]["attempts"][str(fa["ordinal"])]
        self.assertTrue(a["verified"])                                   # BlockProgress verified(depth,ordinal)と整合
        others = [(d, o) for d, b in st["blocks"].items() for o, x in b["attempts"].items() if x.get("verified")]
        self.assertEqual(others, [(str(fa["depth"]), str(fa["ordinal"]))])   # 採用は一意

    def test_a_first_attempt_adopted_matches_progress_verified(self):
        for leaf in ("L1", "L2", "L3", "L4"):
            with self.subTest(leaf=leaf):
                s = self.go(leaf, [F.PASS])
                fa = s.r["final_adoption"]
                self.assertEqual(set(fa), self.KEYS)                     # 最小キーのみ(lr_applied/human_approval_superseded/LR本文を持たない)
                self.assertEqual((fa["depth"], fa["ordinal"], fa["slot"], fa["style_mode"]), (0, 1, "①", "PRIMARY"))
                self._consistent(fa, progress_state(s.w))
                self.assertEqual(progress_state(s.w)["final_adoption"], fa)
                self.assertEqual(s.status, "OK")

    def test_a_third_attempt_fallback_recorded_as_fallback_style(self):
        for leaf in ("L1", "L3"):
            with self.subTest(leaf=leaf):
                s = self.go(leaf, [F.NG, F.NG, F.PASS])
                fa = s.r["final_adoption"]
                self.assertEqual((fa["depth"], fa["ordinal"], fa["slot"], fa["style_mode"]), (0, 3, "③", "FALLBACK"))
                self._consistent(fa, progress_state(s.w))

    def test_a_lr_adopted_take_is_lr_block_and_survives_to_depth0_result(self):
        for leaf in ("L1", "L3"):
            with self.subTest(leaf=leaf):
                s = self.go(leaf, [F.NG, F.NG, F.NG, F.PASS])            # 元①②③NG -> LR後①'で合格
                self.assertEqual(s.status, "OK")
                fa = s.r["final_adoption"]
                self.assertEqual((fa["depth"], fa["ordinal"], fa["slot"], fa["style_mode"]), (1, 1, "①'", "PRIMARY"))
                st = progress_state(s.w)
                self._consistent(fa, st)
                self.assertFalse(st["blocks"]["0"]["attempts"]["3"]["verified"])   # 未採用の③(Fallback)は採用扱いにならない
                self.assertEqual(st["final_adoption"], fa)
                self.assertNotIn("lr_applied", fa)
                self.assertNotIn("human_approval_superseded", fa)

    def test_a_failed_block_has_no_final_adoption(self):
        s = self.go("L1", [F.NG] * 12)
        self.assertNotEqual(s.status, "OK")
        self.assertNotIn("final_adoption", s.r)
        self.assertNotIn("final_adoption", progress_state(s.w))

    def test_a_scope_out_leaf_unchanged_no_record(self):
        s = T.run("L1", [F.PASS], scope=None)
        try:
            self.assertEqual(s.status, "OK")
            self.assertNotIn("final_adoption", s.r)
        finally:
            s.close()

    def test_slot_label(self):
        self.assertEqual([blk._slot_label(i, 0) for i in (1, 2, 3)], ["①", "②", "③"])
        self.assertEqual([blk._slot_label(i, 1) for i in (1, 2, 3)], ["①'", "②'", "③'"])

    def test_sent_style_sha_from_result_or_log(self):
        import hashlib
        sha = hashlib.sha256(b"abc").hexdigest()
        self.assertEqual(blk._sent_style_sha({"style_prefix": {"sha256": sha}}), sha)
        self.assertEqual(blk._sent_style_sha({"style_prefix": "abc"}), sha)
        self.assertEqual(blk._sent_style_sha({"attempts_log": [{"verified": True, "style_prefix": {"sha256": sha}}]}), sha)
        self.assertIsNone(blk._sent_style_sha({"attempts_log": [{"verified": False}]}))


class ZCtxFinalAdoptionTests(unittest.TestCase):
    def setUp(self):
        import er122_fz_ctx_policy_01 as pol
        self.pol = pol
        self.tmp = tempfile.mkdtemp(prefix="b1z_")
        self.level_dir = os.path.join(self.tmp, "theme", "b1b")
        os.makedirs(os.path.join(self.level_dir, "narration"), exist_ok=True)
        self.wav = os.path.join(self.level_dir, "narration", "full_story_part1_c3.wav")
        with open(self.wav, "wb") as f:
            f.write(b"RIFFfake")
        self.p = mock.patch.object(pol.RUNTIME, "clock", F.FakeClock().clock)
        self.p.start()

    def tearDown(self):
        self.p.stop()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _open(self):
        return self.pol.DialogueAttemptPolicy(self.level_dir, "full_story_part1_c3", "Hello.", "CTX", "c" * 64, out_path=self.wav,
                                              stop_check=lambda where: None)

    def test_b_ctx_adoption_recorded(self):
        p = self._open()
        p.before_attempt(1, 1, self.wav)
        p.after_attempt(1, [{"instruction_type": "styled"}], True, "styled")
        r = p.finish({"status": "OK"})
        fa = r["final_adoption"]
        self.assertEqual((fa["depth"], fa["ordinal"], fa["slot"], fa["style_mode"], fa["sent_style_sha"], fa["source"]),
                         (0, 1, "①", "PRIMARY", "c" * 64, "tts_attempt"))
        self.assertEqual(p.st["done"]["result"]["final_adoption"], fa)          # 保存結果(adopt_saved_done_ok)にも残る
        self.assertEqual(p.saved_result() if p._saved_result else fa, fa)

    def test_b_legacy_dialogue_style_adoption_is_fallback(self):
        p = self._open()
        for n in (1, 2):
            p.before_attempt(n, 3, self.wav)
            p.after_attempt(n, [{"instruction_type": "styled"}], False, "styled")
        with mock.patch.object(p, "_cooldown_before_fallback"):
            p.before_attempt(3, 3, self.wav)
        p.after_attempt(3, [{"instruction_type": "styled"}], True, "styled")
        fa = p.finish({"status": "OK"})["final_adoption"]
        self.assertEqual((fa["ordinal"], fa["slot"], fa["style_mode"], fa["sent_style_sha"]), (3, "③", "FALLBACK", None))

    def test_b_ng_result_has_no_record(self):
        p = self._open()
        p.before_attempt(1, 1, self.wav)
        p.after_attempt(1, [{"instruction_type": "styled"}], False, "styled")
        self.assertNotIn("final_adoption", p.finish({"status": "STOPPED"}))


class StoreReuseTests(unittest.TestCase):
    def test_c_key_b_hit_is_store_reuse_with_english_lock_style(self):
        import hashlib
        import er003_v1_repro01_main_generate as repro01
        import er019_family_x_kp_en_k2_store_01 as k2
        d = tempfile.mkdtemp(prefix="b1k_")
        try:
            wav = os.path.join(d, "kp1_en.wav")
            with open(wav, "wb") as f:
                f.write(b"RIFFx")
            res = {"status": "OK", "reused": True, "fallback_used": True, "path": wav, "final_adoption": {"stale": True}}
            k2._note_store_reuse_adoption(res, style_text="K2 STYLE")
            fa = res["final_adoption"]
            self.assertEqual(fa["source"], "store_reuse")
            self.assertEqual(fa["style_mode"], "FALLBACK")
            self.assertEqual(fa["style_name"], "ENGLISH_LOCK")
            self.assertIsNone(fa["ordinal"])
            self.assertEqual(fa["sent_style_sha"], hashlib.sha256(repro01.KEY_PHRASE_ENGLISH_LOCK_INSTRUCTION.encode("utf-8")).hexdigest())
            # key A hit = K2 Style(PRIMARY)
            ra = {"status": "OK", "reused": True, "fallback_used": False, "path": wav}
            k2._note_store_reuse_adoption(ra, style_text="K2 STYLE")
            self.assertEqual((ra["final_adoption"]["style_mode"], ra["final_adoption"]["source"]), ("PRIMARY", "store_reuse"))
            self.assertEqual(ra["final_adoption"]["sent_style_sha"], hashlib.sha256(b"K2 STYLE").hexdigest())
            # TTS生成(reused False)には触れない
            rg = {"status": "OK", "reused": False, "final_adoption": {"source": "tts_attempt"}}
            k2._note_store_reuse_adoption(rg, style_text="K2 STYLE")
            self.assertEqual(rg["final_adoption"], {"source": "tts_attempt"})
            k2._note_store_reuse_adoption(None, style_text="x")        # 例外を出さない
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_c_blockrun_reused_result_gets_store_reuse_source(self):
        s = None
        try:
            tmp = tempfile.mkdtemp(prefix="b1r_")
            out = os.path.join(tmp, "theme", "a2", "narration", "kp1_en.wav").replace("\\", "/")
            os.makedirs(os.path.dirname(out), exist_ok=True)
            import er109_xz_scope_01 as xz
            c = F.FakeClock()
            with mock.patch.object(blk.RUNTIME, "clock", c.clock), mock.patch.object(blk.RUNTIME, "sleep", c.sleep), \
                    mock.patch.object(blk, "_STOP_CHECK", None), xz.run_scope("X"):
                b = blk.open_block("L6", out, "hello", fingerprint={"s": 1})
                b.step(1)
                b.step(2)
                res = {"status": "OK", "reused": True, "fallback_used": True}
                b.finish(res)
            self.assertEqual((res["final_adoption"]["source"], res["final_adoption"]["ordinal"]), ("store_reuse", None))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class EntryCopyTests(unittest.TestCase):
    def test_d_z_build_entry_copies_final_adoption_and_old_entry_unchanged(self):
        import er063_family_z_audio_01 as z
        import er063_family_z_audio_01_test_01 as zt
        d = tempfile.mkdtemp(prefix="b1e_")
        try:
            plan, _, _ = zt.make_plan("b1b")
            spec = plan[0]
            wav = os.path.join(d, spec.wav_name())
            zt._write_tone(wav)
            fa = {"depth": 0, "ordinal": 1, "slot": "①", "style_mode": "PRIMARY", "sent_style_sha": None, "attempt_audio_sha": "x",
                  "source": "tts_attempt"}
            e = z.build_entry(spec, wav, {"status": "OK", "final_adoption": fa})
            self.assertEqual(e["final_adoption"], fa)
            old = z.build_entry(spec, wav, {"status": "OK"})              # (f) 旧entry(記録なし): 例外なし・キーなし(従来と同形)
            self.assertNotIn("final_adoption", old)
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_d_x_generate_or_reuse_keeps_final_adoption_on_reuse(self):
        import er019_family_x_audio_production_runner_01 as x
        d = tempfile.mkdtemp(prefix="b1x_")
        try:
            wav = os.path.join(d, "comment_1.wav")
            with open(wav, "wb") as f:
                f.write(b"RIFFx")
            fa = {"depth": 0, "ordinal": 2, "slot": "②", "style_mode": "PRIMARY", "sent_style_sha": "s", "attempt_audio_sha": "a", "source": "tts_attempt"}
            cached = {"style_version": x.FAMILY_X_VARIABLE_ROLE_STYLE_VERSION,
                      "segments": {"comment_1": {"status": "OK", "canonical_text": "Hi.", "final_adoption": fa}}}
            with mock.patch.object(x, "_reuse_guard_blocks", return_value=None):
                r = x._generate_or_reuse(cached, "comment_1", wav, lambda: self.fail("must reuse"), expected_text="Hi.")
            self.assertEqual(r["final_adoption"], fa)
            self.assertTrue(r["reused_from_previous_run"])
            # 旧entry(記録なし)の再利用で例外が出ない
            cached["segments"]["comment_1"].pop("final_adoption")
            with mock.patch.object(x, "_reuse_guard_blocks", return_value=None):
                r2 = x._generate_or_reuse(cached, "comment_1", wav, lambda: self.fail("must reuse"), expected_text="Hi.")
            self.assertNotIn("final_adoption", r2)
        finally:
            shutil.rmtree(d, ignore_errors=True)


class ResumeLrAuditTests(T.Base):
    def test_e_pre_retts_audit_saved_and_restored_on_resume(self):
        """M-4: LR選定根拠(候補・7 Gate結果・理由・変更範囲)が再TTS前に保存され、LR block内でkill後のresumeで読める(LR LLMは再実行しない)。"""
        w = T.make_world("L1", judge=[F.NG] * 12)
        self.addCleanup(w.cleanup)
        import er020_tts_retry_local_rewrite_01 as er020
        orig_lr_run = w.lr_run
        gates = {k: True for k in ("1_meaning_preserved", "2_role_preserved", "3_fact_non_contradiction", "4_context_connection",
                                   "5_natural_english_gate", "6_localized_minimal_change", "7_not_full_rewrite")}

        def lr_run_with_audit(**kw):
            # 本物のrun_local_rewrite_recoveryと同じ順序: 選定→再TTS前の監査コピー(hook)→再TTS。選定結果はfake(LLMは呼ばない)
            real_retts = kw["retts_fn"]

            def retts(text):
                res = {"management_id": "fake", "segment_id": kw["segment_id"], "canonical_text": kw["canonical_text"], "ng_span": {"found": True},
                       "selection": {"selected": {"id": "1", "rewritten_segment": text, "changed_span_before": "dog", "changed_span_after": "dog today",
                                                  "seven_gates": gates, "all_seven_gates_pass": True, "adoptable": True,
                                                  "qa_llm": {"natural_english": {"pass": True, "reason": "natural"}}},
                                     "selection_rationale": "r"},
                       "candidates": []}
                er020._write_pre_retts_audit(res, None, real_retts)
                return real_retts(text)
            retts.pre_retts_audit_hook = getattr(real_retts, "pre_retts_audit_hook", None)
            kw["retts_fn"] = retts
            return orig_lr_run(**kw)
        w.lr_run = lr_run_with_audit
        w.stop_after_sleeps = 40                       # 第1待機後、LR block ③'直前の第2待機の途中でkill(既存StopResumeTestsと同条件)
        with w.patched(scope="X"):
            with self.assertRaises(blk.TtsBlockStopError):
                T.call_leaf("L1", w)
        st = progress_state(w)
        audit = st["lr"].get("audit")
        self.assertIsNotNone(audit)                    # 再TTS後の書込みを待たず、killされてもBlockProgressに残る
        self.assertEqual(audit["schema"], "lr_selection_audit_v1")
        self.assertEqual(audit["canonical_text"], F.TEXT)
        sel = audit["selected"]
        self.assertEqual(sel["rewritten_segment"], st["lr"]["text"])
        self.assertTrue(sel["all_seven_gates_pass"])
        self.assertEqual(len(sel["seven_gates"]), 7)
        self.assertTrue(all(v is True for v in sel["seven_gates"].values()))
        self.assertIn("changed_span_before", sel)
        w.stop_after_sleeps = None
        w.judge_script, w.judge_i, w.tts_i = [F.PASS], 0, 0
        w.clock.t += 10.0
        n_llm = len(w.lr_calls)
        with w.patched(scope="X"):
            r = T.call_leaf("L1", w)
        self.assertEqual(len(w.lr_calls), n_llm)       # LR LLM再実行なし(不変)
        rec = r["local_rewrite_recovery"]
        self.assertTrue(rec.get("resumed_without_llm"))
        self.assertEqual(rec["lr_selection_audit_restored"], audit)    # resume後にLR根拠が読める
        self.assertEqual(r["status"], "OK")
        self.assertEqual(r["final_adoption"]["depth"], 1)

    def test_e_er020_writes_separate_pre_retts_audit_file_and_keeps_post_file(self):
        import er020_tts_retry_local_rewrite_01 as m
        res = {"management_id": "M", "segment_id": "seg", "canonical_text": "A b c.", "ng_span": {"found": True},
               "selection": {"selected": {"id": "1", "rewritten_segment": "A b d.", "changed_span_before": "c", "changed_span_after": "d",
                                           "seven_gates": {"1_meaning_preserved": True}, "all_seven_gates_pass": True, "adoptable": True,
                                           "qa_llm": {"meaning_preserved": {"pass": True, "reason": "ok"}}},
                             "selection_rationale": "r"},
               "candidates": []}
        d = tempfile.mkdtemp(prefix="b1a_")
        seen = []

        def retts(t):
            seen.append(t)
            return {"status": "OK"}
        retts.pre_retts_audit_hook = lambda a: seen.append(("hook", a["selected"]["id"]))
        try:
            m._write_pre_retts_audit(res, d, retts)
            self.assertEqual(seen, [("hook", "1")])                       # hookは再TTS(retts)より前に呼ばれる前提の純記録
            p = os.path.join(d, "lr_selection_audit_seg.json")
            self.assertTrue(os.path.exists(p))
            self.assertFalse(os.path.exists(os.path.join(d, "local_rewrite_recovery_seg.json")))   # 既存の再TTS後fileとは別名
            a = json.load(open(p, encoding="utf-8"))
            self.assertEqual(a["selected"]["qa_reasons"]["meaning_preserved"], "ok")
            # hook例外・out_dirなしでもLRを止めない
            retts.pre_retts_audit_hook = lambda a: 1 / 0
            m._write_pre_retts_audit(res, None, retts)
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_f_old_progress_without_records_does_not_raise(self):
        s = self.go("L1", [F.PASS])
        st = progress_state(s.w)
        st.pop("final_adoption", None)                                   # 旧BlockProgress(記録なし)
        level_dir = os.path.dirname(os.path.dirname(s.w.out_path))
        p = f"{level_dir}/audit/tts_block_progress/{s.w.seg}.json"
        json.dump(st, open(p, "w", encoding="utf-8"))
        bp = blk.BlockProgress(s.w.out_path, s.w.seg, F.TEXT, {"policy": "x"})
        self.assertIsNone(bp.final_adoption())


class RealRecoveryOrderTests(unittest.TestCase):
    def test_e_real_run_local_rewrite_recovery_writes_audit_before_retts(self):
        """本物のrun_local_rewrite_recovery(LLMのみfake): 再TTS(retts_fn)より前にhookと監査fileが出来、再TTS後の既存fileも従来どおり残る。
        候補選定・採否・戻り値statusは不変。"""
        import er020_tts_retry_local_rewrite_01 as m
        import er020_tts_retry_local_rewrite_01_test_01 as t20
        d = tempfile.mkdtemp(prefix="b1o_")
        try:
            canonical = "let's bring the main point together before we close."
            asr = "let's bring the main points together before we close."
            cg = {"candidates": [t20._candidate("c1", "let's bring the main idea together before we close.")]}
            qa = {"evaluations": [{"candidate_id": "c1", "meaning_preserved": t20._gate(True), "role_preserved": t20._gate(True),
                                   "fact_non_contradiction": t20._gate(True), "context_connection": t20._gate(True),
                                   "natural_english": t20._gate(True, "natural")}]}
            client = t20.RunLocalRewriteRecoveryTest._fake_client(None, cg, qa)
            order = []

            def retts(text):
                order.append(("retts", os.path.exists(f"{d}/lr_selection_audit_comment_4.json"),
                              os.path.exists(f"{d}/local_rewrite_recovery_comment_4.json")))
                return {"status": "OK"}
            retts.pre_retts_audit_hook = lambda audit: order.append(("hook", audit["selected"]["id"], len(audit["selected"]["seven_gates"])))
            rec = m.run_local_rewrite_recovery(segment_id="comment_4", canonical_text=canonical, last_asr_text=asr, retts_fn=retts,
                                               out_dir=d, client=client)
            self.assertEqual(rec["status"], "RESOLVED_BY_LOCAL_REWRITE")
            self.assertEqual(order[0], ("hook", "c1", 7))
            self.assertEqual(order[1], ("retts", True, False))          # 監査copyは再TTS前に在り、既存の再TTS後fileはまだ無い
            self.assertTrue(os.path.exists(f"{d}/local_rewrite_recovery_comment_4.json"))     # 既存の再TTS後の書込みは残る
        finally:
            shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
