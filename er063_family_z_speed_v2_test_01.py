# FAMILY-Z-DIALOGUE-SPEED-PRODUCTION-WIRING-01: Family Z会話速度仕様v2(Std会話=減速撤去 / Adv会話=約6%高速化)のProduction配線test。
# API 0(TTS/ASRはmock・fake。速度処理のffmpegだけ実物=ローカル)。
import hashlib
import json
import os
import shutil
import tempfile
import unittest
from unittest import mock

import er003_v1_n3_01_tts_generate as n3
import er008_a2_postprocess_slowdown_01 as sd
import er063_family_z_audio_01 as z
import er063_family_z_audio_01_test_01 as base


def tone(path, seconds=1.0):
    base._write_tone(path, seconds)


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def _plan(level):
    plan, _, _ = base.make_plan(level)
    return plan


class SpeedProfileTableTest(unittest.TestCase):
    def test_level_kind_table(self):
        self.assertEqual(z.speed_profile_name("a2", "narrator"), "std_narrator_slow6")
        self.assertEqual(z.speed_profile_name("a2", "dialogue"), "std_dialogue_none")
        self.assertEqual(z.speed_profile_name("b1b", "narrator"), "adv_narrator_none")
        self.assertEqual(z.speed_profile_name("b1b", "dialogue"), "adv_dialogue_fast6")
        for k in ("preview", "comment", "kp_en", "kp_ja", "topic_intro", "japanese_title"):
            self.assertIsNone(z.speed_profile_name("a2", k))
            self.assertIsNone(z.speed_profile_name("b1b", k))

    def test_adv_pct_gives_tempo_1_06_same_as_trial_b(self):
        # Trial B(build_adv_01.py)と同じ引数: slowdown_pct=(1/1.06-1)*100 -> er008のtempo=1/(1+pct/100)=1.06
        self.assertAlmostEqual(z.Z_ADV_DIALOGUE_SLOWDOWN_PCT, -5.660377, places=5)
        self.assertAlmostEqual(1.0 / (1.0 + z.Z_ADV_DIALOGUE_SLOWDOWN_PCT / 100.0), 1.06, places=9)

    def test_real_ffmpeg_adv_speedup_ratio_and_std_default_unchanged(self):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        tone(f"{d}/a.wav", 3.0)
        info = sd.apply_a2_slowdown(f"{d}/a.wav", f"{d}/fast.wav", z.Z_ADV_DIALOGUE_SLOWDOWN_PCT)
        self.assertAlmostEqual(info["dst_duration_seconds"] / info["src_duration_seconds"], 1 / 1.06, delta=0.01)
        # 6%減速(Std narrator)の既定呼出はpct省略=6.0と同一バイト(共有moduleは無変更)
        sd.apply_a2_slowdown(f"{d}/a.wav", f"{d}/s1.wav")
        sd.apply_a2_slowdown(f"{d}/a.wav", f"{d}/s2.wav", z.Z_STD_NARRATOR_SLOWDOWN_PCT)
        self.assertEqual(sha(f"{d}/s1.wav"), sha(f"{d}/s2.wav"))


class ReuseKeyTest(unittest.TestCase):
    def _specs(self, level):
        return {s.clip_id: s for s in _plan(level)}

    def test_dialogue_key_has_speed_profile_others_unchanged(self):
        for level, want in (("a2", "z_speed_v2:std_dialogue_none"), ("b1b", "z_speed_v2:adv_dialogue_fast6")):
            sp = self._specs(level)
            self.assertEqual(z.build_reuse_key(sp["full_story_part1_c2"])["speed_profile"], want)
            self.assertNotIn("speed_profile", z.build_reuse_key(sp["full_story_part1_c1"]))   # narrator: key不変=既存再利用を維持
            self.assertNotIn("speed_profile", z.build_reuse_key(sp["preview"]))
            self.assertNotEqual(z.build_reuse_key(sp["full_story_part1_c2"]), z.build_legacy_reuse_key(sp["full_story_part1_c2"]))

    def test_legacy_dialogue_entry_is_not_reused_as_new_spec(self):
        for level in ("a2", "b1b"):
            spec = self._specs(level)["full_story_part1_c2"]
            wav = tempfile.mkdtemp()
            self.addCleanup(shutil.rmtree, wav, ignore_errors=True)
            p = f"{wav}/{spec.clip_id}.wav"
            tone(p, 1.0)
            legacy = {"status": "OK", "reuse_key": z.build_legacy_reuse_key(spec), "sha256": sha(p)}
            calls = []
            z.generate_or_reuse_z(legacy, spec, p, lambda: calls.append(1) or {"status": "OK", "regenerated": True})
            self.assertEqual(calls, [1], f"{level}: 旧仕様entryが新仕様として再利用された")
            cached = {"segments": {spec.clip_id: legacy}, "key_phrases": {}}
            self.assertIsNone(z._cached_entry(z.prune_cached_to_plan(cached, [spec]), spec))

    def test_same_version_entry_is_reused(self):
        spec = self._specs("b1b")["full_story_part1_c2"]
        wav = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, wav, ignore_errors=True)
        p = f"{wav}/{spec.clip_id}.wav"
        tone(p, 1.0)
        cur = {"status": "OK", "reuse_key": z.build_reuse_key(spec), "sha256": sha(p)}
        calls = []
        r = z.generate_or_reuse_z(cur, spec, p, lambda: calls.append(1) or {"status": "OK"})
        self.assertEqual(calls, [])
        self.assertTrue(r["reused_from_previous_run"])


class GeneratorWiringTest(unittest.TestCase):
    """dialogue generatorがlevel別に正しい経路を通る(Narrator/Dialogue区別・旧6%減速の撤去・二重適用なし)。"""

    def _call(self, level):
        import er012_b_family_voices_production_01 as bv
        spec = [s for s in _plan(level) if s.kind == "dialogue"][0]
        with mock.patch.object(n3, "generate_with_a2_slowdown_outer_loop", return_value={"status": "OK", "via": "outer"}) as outer, \
             mock.patch.object(bv, "generate_voice_body_wide_margin", return_value={"status": "OK", "via": "plain"}) as plain, \
             mock.patch.object(z, "_check_stop_sentinel"):
            gens = z.real_generators()
            r = gens["dialogue"](spec, f"x/{level}/narration/full_story_part1_c2.wav")
        return spec, r, outer, plain

    def test_std_dialogue_has_no_speed_postprocess(self):
        spec, r, outer, plain = self._call("a2")
        self.assertEqual(r["via"], "plain")
        outer.assert_not_called()
        self.assertEqual(plain.call_args.args[1:], ("x/a2/narration/full_story_part1_c2.wav", spec.voice))

    def test_adv_dialogue_gets_trial_b_speedup_via_outer_loop(self):
        spec, r, outer, plain = self._call("b1b")
        self.assertEqual(r["via"], "outer")
        plain.assert_not_called()
        self.assertEqual(outer.call_args.kwargs["slowdown_pct"], z.Z_ADV_DIALOGUE_SLOWDOWN_PCT)


class OuterLoopPassThroughTest(unittest.TestCase):
    def test_default_call_has_no_pct_kwarg_x_unchanged_and_pct_is_forwarded(self):
        for pct, expect in ((None, {}), (z.Z_ADV_DIALOGUE_SLOWDOWN_PCT, {"slowdown_pct": z.Z_ADV_DIALOGUE_SLOWDOWN_PCT})):
            seen = []

            def fake_post(name, nd, text, result, **kw):
                seen.append(kw)
                r = dict(result)
                r["status"] = "OK"
                return r
            d = tempfile.mkdtemp()
            self.addCleanup(shutil.rmtree, d, ignore_errors=True)
            with mock.patch.object(n3, "apply_a2_slowdown_postprocess", side_effect=fake_post), \
                 mock.patch.object(n3.review_lock, "append_attempt_history_event"):
                n3.generate_with_a2_slowdown_outer_loop("c", "t", f"{d}/c.wav", lambda m: {"status": "OK"},
                                                        **({} if pct is None else {"slowdown_pct": pct}))
            self.assertEqual({k: v for k, v in seen[0].items() if k == "slowdown_pct"}, expect)

    def test_postprocess_default_calls_ffmpeg_without_pct_and_with_pct_when_given(self):
        for pct in (None, -5.66):
            d = tempfile.mkdtemp()
            self.addCleanup(shutil.rmtree, d, ignore_errors=True)
            tone(f"{d}/n.wav", 1.0)
            fake = mock.Mock(side_effect=lambda s, o, *a: (shutil.copyfile(s, o), {"src_duration_seconds": 1.0, "dst_duration_seconds": 1.06})[1])
            with mock.patch.object(n3.a2_slowdown, "apply_a2_slowdown", fake), \
                 mock.patch.object(n3.routing, "transcribe", return_value=("some text", None)):
                n3.apply_a2_slowdown_postprocess("n", d, "some text", {"status": "OK"}, **({} if pct is None else {"slowdown_pct": pct}))
            self.assertEqual(fake.call_args.args[2:], () if pct is None else (pct,))
            self.assertTrue(os.path.exists(f"{d}/n_original.wav"))


class GateTest(unittest.TestCase):
    def _entry(self, level, kind, applied, tempo=None):
        sp = z.speed_profile_name(level, kind)
        e = {"clip_kind": kind, "status": "OK", "slowdown_applied": True if applied else None,
             "speed_profile": {"version": z.Z_SPEED_PROFILE_VERSION, "profile": sp, "applied": applied, "tempo": tempo}}
        if kind == "dialogue":
            e["reuse_key"] = {"speed_profile": f"{z.Z_SPEED_PROFILE_VERSION}:{sp}"}
        return e

    def _dir(self, cur, orig=None):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        tone(f"{d}/full_story_part1_c2.wav", cur)
        if orig:
            tone(f"{d}/full_story_part1_c2_original.wav", orig)
        return d

    def test_four_combinations_pass(self):
        z.verify_z_speed_profile("a2", {"full_story_part1_c2": self._entry("a2", "dialogue", False)}, self._dir(1.0))
        z.verify_z_speed_profile("a2", {"full_story_part1_c2": self._entry("a2", "dialogue", False)}, self._dir(1.0, 1.0))
        z.verify_z_speed_profile("b1b", {"full_story_part1_c2": self._entry("b1b", "dialogue", True, 1.06)}, self._dir(1.0, 1.06))
        z.verify_z_speed_profile("b1b", {"full_story_part1_c1": self._entry("b1b", "narrator", False)}, self._dir(1.0))
        z.verify_z_speed_profile("a2", {"full_story_part1_c1": self._entry("a2", "narrator", True, 0.943396)}, self._dir(1.0))

    def test_legacy_std_dialogue_slowed_is_detected(self):
        with self.assertRaises(z.FamilyZSlowdownGateStop):
            z.verify_z_speed_profile("a2", {"full_story_part1_c2": self._entry("a2", "dialogue", True, 0.943396)}, self._dir(1.06, 1.0))
        with self.assertRaises(z.FamilyZSlowdownGateStop):   # 記録は無処理だが実音声が減速済み(混入)
            z.verify_z_speed_profile("a2", {"full_story_part1_c2": self._entry("a2", "dialogue", False)}, self._dir(1.06, 1.0))

    def test_legacy_adv_dialogue_unprocessed_is_detected(self):
        with self.assertRaises(z.FamilyZSlowdownGateStop):
            z.verify_z_speed_profile("b1b", {"full_story_part1_c2": self._entry("b1b", "dialogue", False)}, self._dir(1.0))
        legacy_no_profile = {"clip_kind": "dialogue", "status": "OK", "slowdown_applied": None}
        with self.assertRaises(z.FamilyZSlowdownGateStop):
            z.verify_z_speed_profile("b1b", {"full_story_part1_c2": legacy_no_profile}, self._dir(1.0))
        with self.assertRaises(z.FamilyZSlowdownGateStop):   # 高速化記録はあるが実長が不整合(処理漏れ)
            z.verify_z_speed_profile("b1b", {"full_story_part1_c2": self._entry("b1b", "dialogue", True, 1.06)}, self._dir(1.0, 1.0))
        with self.assertRaises(z.FamilyZSlowdownGateStop):   # 二重適用
            z.verify_z_speed_profile("b1b", {"full_story_part1_c2": self._entry("b1b", "dialogue", True, 1.06)}, self._dir(0.9, 1.06))

    def test_adv_narrator_with_speed_is_detected(self):
        e = self._entry("b1b", "narrator", True, 1.06)
        with self.assertRaises(z.FamilyZSlowdownGateStop):
            z.verify_z_speed_profile("b1b", {"full_story_part1_c1": e}, self._dir(1.0, 1.06))

    def test_std_narrator_check_ignores_dialogue_but_still_requires_narrator_slowdown(self):
        d = self._dir(1.0)
        z.verify_std_english_slowdown("x", {"full_story_part1_c2": {"clip_kind": "dialogue", "status": "OK"}}, d)
        with self.assertRaises(z.FamilyZSlowdownGateStop):
            z.verify_std_english_slowdown("x", {"full_story_part1_c2": {"clip_kind": "narrator", "status": "OK"}}, d)


class StageIntegrationTest(unittest.TestCase):
    """run_tts_stage(Z正式経路)をfake generatorで通す: level×kind、entryのspeed_profile、resume再利用(再生成0)。"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.run = f"{self.tmp}/melos/run_01"
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def _stage(self, level, gens=None):
        plan = _plan(level)
        out = z.run_tts_stage(self.run, level, plan, generators=gens or base.fake_generators())
        return plan, out

    def test_entries_carry_speed_profile_for_all_level_kind(self):
        for level, d_prof, d_applied, n_prof, n_applied in (("a2", "std_dialogue_none", False, "std_narrator_slow6", True),
                                                             ("b1b", "adv_dialogue_fast6", True, "adv_narrator_none", False)):
            plan, out = self._stage(level)
            seg = json.load(open(out["results_path"], encoding="utf-8"))["segments"]
            d, n = seg["full_story_part1_c2"], seg["full_story_part1_c1"]
            self.assertEqual((d["speed_profile"]["profile"], d["speed_profile"]["applied"]), (d_prof, d_applied))
            self.assertEqual((n["speed_profile"]["profile"], n["speed_profile"]["applied"]), (n_prof, n_applied))
            self.assertEqual(d["reuse_key"]["speed_profile"], f"z_speed_v2:{d_prof}")
            if level == "b1b":
                self.assertAlmostEqual(d["speed_profile"]["tempo"], 1.06, places=5)
                self.assertTrue(d["speed_profile"]["original_sha256"])
            self.assertIsNone(seg["preview"].get("speed_profile"))

    def test_resume_reuses_without_regeneration(self):
        self._stage("b1b")
        calls = []
        gens = {k: (lambda spec, p, f=f: calls.append(spec.clip_id) or f(spec, p)) for k, f in base.fake_generators().items()}
        self._stage("b1b", gens=gens)
        self.assertEqual(calls, [])


class MigrationTest(unittest.TestCase):
    def setUp(self):
        self.run = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.run, ignore_errors=True)

    def _legacy(self, level):
        """速度仕様v1(旧)のrunを作る: Std=会話減速済み+_original / Adv=会話未処理。"""
        plan = _plan(level)
        narr = f"{self.run}/{level}/narration"
        os.makedirs(narr)
        os.makedirs(f"{self.run}/{level}/audit")
        segs = {}
        for s in plan:
            if s.kind != "dialogue":
                continue
            p = f"{narr}/{s.clip_id}.wav"
            if level == "a2":
                tone(f"{narr}/{s.clip_id}_original.wav", 1.0)
                tone(p, 1.06)
                applied = True
            else:
                tone(p, 1.06)
                applied = None
            segs[s.clip_id] = {"status": "OK", "reuse_key": z.build_legacy_reuse_key(s), "sha256": sha(p), "duration_seconds": 1.06,
                               "slowdown_applied": applied, "canonical_text": s.text, "text": s.text, "asr_text": s.text,
                               "clip_kind": "dialogue", "audio_text_deviation": None, "asr_judgement": {"state": "PASS", "legacy": True}}
        return plan, segs

    def test_std_migration_restores_original_without_tts_or_asr(self):
        plan, segs = self._legacy("a2")
        orig_sha = {k: sha(f"{self.run}/a2/narration/{k}_original.wav") for k in segs}
        with mock.patch.object(n3, "apply_a2_slowdown_postprocess", side_effect=AssertionError("ASR/postprocess must not run for Std")):
            cached, rep = z.migrate_legacy_dialogue_speed({"segments": segs, "key_phrases": {}}, plan, self.run, "a2")
        self.assertTrue(rep and all(r["migrated"] for r in rep))
        for k in segs:
            e = cached["segments"][k]
            self.assertEqual(sha(f"{self.run}/a2/narration/{k}.wav"), orig_sha[k])      # wav == 減速前原音 (Trial B Stdと同一)
            self.assertEqual(e["sha256"], orig_sha[k])
            self.assertFalse(e["speed_profile"]["applied"])
            self.assertIs(e["slowdown_applied"], False)
            self.assertNotIn("asr_judgement", e)                                          # 旧(減速後wav)判定recordは現行wavの判定として残さない
            self.assertTrue(os.path.exists(f"{self.run}/a2/audit/legacy_speed_backup/{k}_slowed6pct_legacy.wav"))
            spec = [s for s in plan if s.clip_id == k][0]
            self.assertEqual(e["reuse_key"], z.build_reuse_key(spec))
        cached2, rep2 = z.migrate_legacy_dialogue_speed(cached, plan, self.run, "a2")   # idempotent
        self.assertEqual(rep2, [])

    def test_adv_migration_applies_formal_postprocess_once_and_blocks_double_application(self):
        plan, segs = self._legacy("b1b")
        raw = {k: sha(f"{self.run}/b1b/narration/{k}.wav") for k in segs}
        seen = []

        def fake_post(name, nd, text, result, **kw):
            seen.append((name, kw.get("slowdown_pct")))
            p, o = f"{nd}/{name}.wav", f"{nd}/{name}_original.wav"
            shutil.copyfile(p, o)
            info = sd.apply_a2_slowdown(o, p, kw["slowdown_pct"])
            r = dict(result)
            r.update({"status": "OK", "slowdown_applied": True, "slowdown_info": info, "original_path": o,
                      "post_slowdown_asr_text": "x", "asr_judgement": {"state": "PASS"}})
            return r
        with mock.patch.object(n3, "apply_a2_slowdown_postprocess", side_effect=fake_post):
            cached, rep = z.migrate_legacy_dialogue_speed({"segments": segs, "key_phrases": {}}, plan, self.run, "b1b")
        self.assertTrue(all(r["migrated"] for r in rep))
        self.assertTrue(all(pct == z.Z_ADV_DIALOGUE_SLOWDOWN_PCT for _, pct in seen))
        nd = f"{self.run}/b1b/narration"
        for k in segs:
            e = cached["segments"][k]
            self.assertEqual(sha(f"{nd}/{k}_original.wav"), raw[k])                      # 原音=旧未処理wav
            self.assertAlmostEqual(e["speed_profile"]["tempo"], 1.06, places=5)
            self.assertAlmostEqual(z._wav_duration(f"{nd}/{k}.wav") / z._wav_duration(f"{nd}/{k}_original.wav"), 1 / 1.06, delta=0.01)
            self.assertEqual(e["asr_judgement"], {"state": "PASS"})
        n = len(seen)
        z.migrate_legacy_dialogue_speed(cached, plan, self.run, "b1b")                   # migrated entryは対象外=再適用なし
        self.assertEqual(len(seen), n)
        # 中断(entryは旧のまま、wavは高速化済み+_original残存)から再開しても原音から1回だけ適用=二重適用なし
        k0 = list(segs)[0]
        dur_fast = z._wav_duration(f"{nd}/{k0}.wav")
        with mock.patch.object(n3, "apply_a2_slowdown_postprocess", side_effect=fake_post):
            z.migrate_legacy_dialogue_speed({"segments": {k0: dict(segs[k0])}, "key_phrases": {}}, plan, self.run, "b1b")
        self.assertAlmostEqual(z._wav_duration(f"{nd}/{k0}.wav"), dur_fast, delta=0.01)

    def test_adv_asr_ng_restores_raw_and_falls_back_to_regeneration(self):
        plan, segs = self._legacy("b1b")
        k0 = list(segs)[0]
        raw = sha(f"{self.run}/b1b/narration/{k0}.wav")

        def ng_post(name, nd, text, result, **kw):
            p, o = f"{nd}/{name}.wav", f"{nd}/{name}_original.wav"
            shutil.copyfile(p, o)
            sd.apply_a2_slowdown(o, p, kw["slowdown_pct"])
            r = dict(result)
            r["status"] = "ASR_VALIDATION_FAILED"
            r["slowdown_applied"] = True
            return r
        spec = [s for s in plan if s.clip_id == k0][0]
        with mock.patch.object(n3, "apply_a2_slowdown_postprocess", side_effect=ng_post):
            cached, rep = z.migrate_legacy_dialogue_speed({"segments": {k0: segs[k0]}, "key_phrases": {}}, plan, self.run, "b1b")
        self.assertFalse(rep[0]["migrated"])
        self.assertEqual(sha(f"{self.run}/b1b/narration/{k0}.wav"), raw)
        self.assertEqual(cached["segments"][k0]["reuse_key"], z.build_legacy_reuse_key(spec))
        self.assertIsNone(z._cached_entry(z.prune_cached_to_plan(cached, plan), spec))   # 旧entryは再利用されず再生成経路へ

    def test_unconfirmed_legacy_std_entry_is_not_migrated(self):
        plan, segs = self._legacy("a2")
        k0 = list(segs)[0]
        segs[k0]["slowdown_applied"] = None    # 旧6%減速済みと確認できない
        cached, rep = z.migrate_legacy_dialogue_speed({"segments": {k0: segs[k0]}, "key_phrases": {}}, plan, self.run, "a2")
        self.assertFalse(rep[0]["migrated"])
        self.assertNotIn("speed_profile", cached["segments"][k0])

    def test_run_tts_stage_migrates_then_reuses_with_zero_generation(self):
        plan = _plan("a2")
        run = f"{self.run}/melos/run_01"
        out = z.run_tts_stage(run, "a2", plan, generators=base.fake_generators())
        res = json.load(open(out["results_path"], encoding="utf-8"))
        narr = f"{run}/a2/narration"
        dialogue_ids = [s.clip_id for s in plan if s.kind == "dialogue"]
        self.assertTrue(dialogue_ids)
        for s in plan:                                   # 会話entryだけ旧(v1)形式へ巻き戻す
            if s.kind == "dialogue":
                e = res["segments"][s.clip_id]
                tone(f"{narr}/{s.clip_id}_original.wav", 1.0)
                tone(f"{narr}/{s.clip_id}.wav", 1.06)
                e.pop("speed_profile", None)
                e["reuse_key"] = z.build_legacy_reuse_key(s)
                e["slowdown_applied"] = True
                e["sha256"] = sha(f"{narr}/{s.clip_id}.wav")
        json.dump(res, open(out["results_path"], "w", encoding="utf-8"))
        calls = []
        gens = {k: (lambda spec, p, f=f: calls.append(spec.clip_id) or f(spec, p)) for k, f in base.fake_generators().items()}
        out2 = z.run_tts_stage(run, "a2", plan, generators=gens)
        self.assertEqual(calls, [], "移行後は再生成0")
        seg = json.load(open(out2["results_path"], encoding="utf-8"))["segments"]
        for cid in dialogue_ids:
            self.assertEqual(seg[cid]["speed_profile"]["profile"], "std_dialogue_none")
            self.assertEqual(sha(f"{narr}/{cid}.wav"), sha(f"{narr}/{cid}_original.wav"))


class RunnerStagesOptionTest(unittest.TestCase):
    """runnerの--stages(既存runの後段だけを1起動で再実行)。dry-runはAPI 0・副作用なし。"""

    def _main(self, *argv):
        import contextlib
        import io
        import er026_family_z_fiction_production_runner_01 as runner
        buf, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
            rc = runner.main(list(argv))
        return rc, buf.getvalue(), err.getvalue()

    def test_stages_are_normalized_to_e2e_order(self):
        rc, out, _ = self._main("--story", "melos", "--run", "run_e2e_06", "--mode", "dry-run", "--stages", "assemble,tts_a2,gate,tts_a2")
        self.assertEqual(rc, 0)
        plan = json.loads(out[out.index("{"):])
        self.assertEqual([r["stage"] for r in plan["stages"]] if "stages" in plan else [r["stage"] for r in plan["plan"]],
                         ["tts_a2", "gate", "assemble"])

    def test_invalid_stage_or_conflict_is_rejected(self):
        rc, _, err = self._main("--mode", "real", "--stages", "writer,nope", "--approved-budget-jpy", "1")
        self.assertEqual(rc, 2)
        self.assertIn("不正なstage名", err)
        rc, _, err = self._main("--mode", "real", "--stage", "gate", "--stages", "gate", "--approved-budget-jpy", "1")
        self.assertEqual(rc, 2)


if __name__ == "__main__":
    unittest.main()
