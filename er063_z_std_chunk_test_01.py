# -*- coding: utf-8 -*-
"""CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01 委任_03: Z Standard(a2) narrator 100語超のB_r1 chunk分割+0.2秒 の配線test(API 0、mock generator)。
Opus M2(速度Gate厳格化)・M3(レベル条件撤去/親aggregate/cache位置)・R6(ctx経路不変)・R7(Local Rewrite経由の減速)・Adv golden一致を固定する。"""
import importlib.util
import json
import os
import shutil
import tempfile
import unittest
from unittest import mock

import er063_family_z_audio_01 as z
import er117_chunk_tts_production_01 as core
import er122_fz_ctx_notes_01 as notes
import er117_z_chunk_wiring_test_01 as zt

REPO = os.path.dirname(os.path.abspath(__file__))
GOLDEN = f"{REPO}/docs/research/CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01/measure_z/z_adv_golden_01.json"
FREEZE = f"{REPO}/docs/research/CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01/measure_z/freeze_z_adv_golden_01.py"
K1, K2 = "full_story_part2_c1_k1", "full_story_part2_c1_k2"


class StripGens(zt.Gens):
    """指定chunkの結果から減速記録を落とす/壊す(減速が掛からなかった・記録されなかったStd chunkの再現)。"""

    def __init__(self, strip_slowdown=(), drop_info=(), bad_ratio=(), **kw):
        super().__init__(**kw)
        self.strip_slowdown, self.drop_info, self.bad_ratio = set(strip_slowdown), set(drop_info), set(bad_ratio)

    def make(self, kind):
        base = super().make(kind)

        def fn(spec, out_path):
            r = base(spec, out_path)
            if spec.clip_id in self.strip_slowdown:
                r["slowdown_applied"] = False
                r.pop("slowdown_info", None)
                r.pop("original_path", None)
            if spec.clip_id in self.drop_info:
                r["slowdown_info"] = {"slowdown_pct_target": 6.0}
            if spec.clip_id in self.bad_ratio:
                r["slowdown_info"] = {"src_duration_seconds": 1.0, "dst_duration_seconds": 1.2, "slowdown_pct_target": 6.0}
            return r
        return fn


class _Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.run = f"{self.tmp}/melos/run_01"
        import er003_v1_n3_01_assemble as asm
        shared = f"{self.tmp}/shared_narration"
        for src_name in list(z.SHELL_ASSET_SOURCES.values()) + list(z.NUMBER_ASSET_SOURCES.values()):
            zt._tone(f"{shared}/{src_name}", 0.4)
        self._p1 = mock.patch.object(asm, "B1_SHARED_SOURCE_DIR", shared)
        self._p1.start()
        self._p2 = mock.patch.object(asm, "verify_key_phrase_source_gate")
        self._p2.start()

    def tearDown(self):
        self._p2.stop()
        self._p1.stop()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def tts(self, level="a2", gens=None, **kw):
        plan, kp = zt.make_plan(level)
        g = gens or zt.Gens()
        out = z.run_tts_stage(self.run, level, plan, generators=g.gens(), **kw)
        return plan, kp, g, out

    def res(self, level="a2"):
        return zt._res(self.run, level)

    def write_res(self, d, level="a2"):
        json.dump(d, open(f"{self.run}/{level}/audit/tts_generation_results.json", "w", encoding="utf-8"))


class StdTtsTests(_Base):
    def test_std_chunk_entries_carry_slowdown_record_and_parent_aggregates(self):
        plan, kp, g, out = self.tts()
        seg = self.res()["segments"]
        for cid in (K1, K2):
            e = seg[cid]
            self.assertTrue(e["slowdown_applied"])                                           # chunk単位で6%減速
            self.assertEqual(e["slowdown_info"]["src_duration_seconds"], 1.0)
            self.assertEqual(e["slowdown_info"]["dst_duration_seconds"], 1.06)
            self.assertEqual(e["chunk_tts"]["level"], "a2")
            self.assertEqual(e["chunk_tts"]["std_slowdown_composition"], core.STD_SLOWDOWN_COMPOSITION)
            self.assertEqual(e["speed_profile"]["profile"], "std_narrator_slow6")
        par = seg["full_story_part2_c1"]
        self.assertIs(par["slowdown_applied"], True)                                         # 親=全chunk減速済みの集約(明示True)
        self.assertEqual(par["std_chunk_slowdown_violations"], [])
        self.assertEqual(par["std_slowdown_composition"], core.STD_SLOWDOWN_COMPOSITION)
        self.assertEqual([c for c in g.calls if "part2_c1" in c], [K1, K2])                  # 親はTTSしない
        nd = f"{self.run}/a2/narration"
        core.verify_raw_parent(f"{nd}/full_story_part2_c1.wav", [f"{nd}/{K1}.wav", f"{nd}/{K2}.wav"])   # 親wav=減速後chunk wav+0.2秒の生連結

    def test_adv_entries_and_parent_display_unchanged(self):
        """M3: b1bの親はslowdown_applied=None・追加キーなし、chunk entryにlevel/slowdown_infoは付かない(Adv不変)。"""
        plan, kp, g, out = self.tts("b1b")
        seg = self.res("b1b")["segments"]
        par = seg["full_story_part2_c1"]
        self.assertIsNone(par["slowdown_applied"])
        for k in ("std_slowdown_composition", "std_chunk_slowdown_violations", "slowdown_basis"):
            self.assertNotIn(k, par)
        for cid in (K1, K2):
            self.assertNotIn("level", seg[cid]["chunk_tts"])
            self.assertNotIn("std_slowdown_composition", seg[cid]["chunk_tts"])
            self.assertNotIn("slowdown_info", seg[cid])

    def test_parent_false_when_one_chunk_lacks_slowdown(self):
        plan, kp, g, out = self.tts(gens=StripGens(strip_slowdown={K2}))
        par = self.res()["segments"]["full_story_part2_c1"]
        self.assertIs(par["slowdown_applied"], False)
        self.assertEqual(par["std_chunk_slowdown_violations"], [K2])

    def test_resume_does_not_reuse_std_chunk_without_slowdown_evidence_even_when_not_selected(self):
        """M3: drop_cached_std_chunks_without_slowdown は load_results直後。--only-clipsで選ばれなかったclipの再利用経路でも
        減速証跡のないchunkを使わない。"""
        plan, kp, g, out = self.tts()
        d = self.res()
        d["segments"][K1].pop("slowdown_applied")
        d["segments"][K1].pop("slowdown_info")
        self.write_res(d)
        g2 = zt.Gens()
        z.run_tts_stage(self.run, "a2", plan, generators=g2.gens(), only_clips={"full_story_part1_c1"})
        seg = self.res()["segments"]
        self.assertNotIn(K1, seg)                                                            # 選択外でも旧(証跡なし)chunkはcarry-overされない
        self.assertIn(K2, seg)                                                               # 証跡のあるchunkは再利用
        self.assertEqual(g2.calls, [])                                                       # 選択外ではTTSしない
        g3 = zt.Gens()
        z.run_tts_stage(self.run, "a2", plan, generators=g3.gens(), only_clips={"full_story_part2_c1"})
        self.assertEqual(g3.calls, [K1])                                                     # 選択すれば当該chunkだけ再生成
        self.assertTrue(self.res()["segments"][K1]["slowdown_applied"])

    def test_resume_reuses_slowed_chunks_zero_tts(self):
        plan, kp, g, out = self.tts()
        g2 = zt.Gens()
        z.run_tts_stage(self.run, "a2", plan, generators=g2.gens())
        self.assertEqual(g2.calls, [])                                                       # 再起動でTTS 0回(chunk再利用)
        g3 = zt.Gens()
        z.run_tts_stage(self.run, "a2", plan, generators=g3.gens(), only_clips={"full_story_part2_c1"})
        self.assertEqual(g3.calls, [])

    def test_local_rewrite_chunk_output_is_slowed_and_passes_strict_gate_R7(self):
        """R7: Std chunkでLocal Rewrite(generate_a2_segment_with_slowdown内でLR後に減速)を経た出力に減速記録があり、厳格Gateを通る。
        減速が漏れたLR出力は厳格Gateが止める。"""
        plan, kp, g, out = self.tts(gens=zt.Gens(lr={K2}))
        e = self.res()["segments"][K2]
        self.assertIsNotNone(e["audio_text_deviation"])                                      # LR採用(provenance)
        self.assertTrue(e["slowdown_applied"])
        self.assertEqual(e["slowdown_info"]["dst_duration_seconds"], 1.06)
        z.provision_shell_assets(self.run, "a2", kp_count=1)
        # 委任_11(B-wire): このtestの対象はM1(Std減速Gate)。mockのLR結果は実leaf形(final_adoption・文単位で一意な書換え位置)を持たないため、
        # UD-3の採用take分類核(LR/Fallbackイベントclip)は台帳を作れない扱い(旧判定のまま)にして減速Gateだけを検証する。分類核は別test(er130/er132/er063 style gate)で検証。
        with mock.patch("er003_v1_n3_01_assemble.verify_episode_audio_validation_gate"),                 mock.patch("er130_adopted_take_classifier_01.event_ledger_clips", return_value=None):
            res = z.run_audio_gate(self.run, "a2", plan, zt.SHELL, article_text="a")
        self.assertTrue(res["m1_slowdown"][K2]["ok"])
        shutil.rmtree(self.run)                                                              # LR出力に減速が掛かっていない場合
        plan, kp, g, out = self.tts(gens=StripGens(strip_slowdown={K2}, lr={K2}))
        z.provision_shell_assets(self.run, "a2", kp_count=1)
        with mock.patch("er003_v1_n3_01_assemble.verify_episode_audio_validation_gate"),                 mock.patch("er130_adopted_take_classifier_01.event_ledger_clips", return_value=None):
            with self.assertRaises(z.FamilyZSlowdownGateStop):
                z.run_audio_gate(self.run, "a2", plan, zt.SHELL, article_text="a")

    def test_dialogue_not_chunked_not_slowed_and_zero_tts_on_chunk_resume_R6(self):
        """R6: Stdでchunk展開してもdialogueはchunk化されず減速されない。旧(非chunk)planで生成済みのdialogueは、chunk planで
        --only-clips <親>を指定してもTTS 0回(reuse_key不変=再利用)。"""
        legacy, kp = zt.make_plan("a2", chunked=False)
        plan, _ = zt.make_plan("a2", chunked=True)
        dlg = [s for s in plan if s.kind == "dialogue"]
        self.assertTrue(dlg)
        self.assertEqual({s.clip_id: z.build_reuse_key(s) for s in dlg},                     # run前(ctx付与前)のdialogue reuse_keyは非chunk planと同一
                         {s.clip_id: z.build_reuse_key(s) for s in legacy if s.kind == "dialogue"})
        z.run_tts_stage(self.run, "a2", legacy, generators=zt.Gens().gens())
        g = zt.Gens()
        z.run_tts_stage(self.run, "a2", plan, generators=g.gens(), only_clips={"full_story_part2_c1"})
        self.assertEqual(g.calls, [K1, K2])                                                  # narrator chunkのみ。dialogue・他clipは0回
        seg = self.res()["segments"]
        self.assertNotEqual(seg["full_story_part1_c2"].get("slowdown_applied"), True)       # dialogueに減速なし
        self.assertEqual(seg["full_story_part1_c2"]["speed_profile"]["profile"], "std_dialogue_none")

    def test_story_clips_from_plan_identical_for_std_chunked_and_unchunked_R6(self):
        a, _ = zt.make_plan("a2", chunked=True)
        b, _ = zt.make_plan("a2", chunked=False)
        sa, sb = notes.story_clips_from_plan(a), notes.story_clips_from_plan(b)
        self.assertEqual(sa, sb)                                                             # 文脈抽出の入力(畳み戻し)は非chunk時と同一
        n_ctx = 0
        for c in sa:
            if str(c.get("voice_role", "")).startswith("dialogue:"):
                disp = {c["speaker"]: c["speaker"]}
                self.assertEqual(notes.extract_context(sa, c["id"], disp), notes.extract_context(sb, c["id"], disp))
                n_ctx += 1
        self.assertGreater(n_ctx, 0)


class StdGateTests(_Base):
    def prep(self, gens=None):
        plan, kp, g, out = self.tts(gens=gens)
        z.provision_shell_assets(self.run, "a2", kp_count=1)
        return plan

    def gate(self, plan):
        with mock.patch("er003_v1_n3_01_assemble.verify_episode_audio_validation_gate"):
            return z.run_audio_gate(self.run, "a2", plan, zt.SHELL, article_text="a")

    def test_gate_checks_chunk_ids_strictly_pass(self):
        plan = self.prep()
        res = self.gate(plan)
        for cid in (K1, K2):
            self.assertTrue(res["m1_slowdown"][cid]["ok"])
            self.assertEqual(res["m1_slowdown"][cid]["strict"], "chunk")

    def test_gate_stops_std_chunk_without_slowdown_no_original_wav_rescue_M2(self):
        plan = self.prep(StripGens(strip_slowdown={K1}))
        nd = f"{self.run}/a2/narration"
        zt._tone(f"{nd}/{K1}_original.wav", 1.0)                                             # 弱い証拠(長さ比1.06)を用意しても救済されない
        zt._tone(f"{nd}/{K1}.wav", 1.06)
        with self.assertRaises(z.FamilyZSlowdownGateStop) as cm:
            self.gate(plan)
        self.assertIn(K1, str(cm.exception))
        self.assertIn("STD_CHUNK_MISSING_MANDATORY_A2_SLOWDOWN", str(cm.exception))

    def test_gate_stops_when_duration_record_missing_or_ratio_out_of_range_M2_R2(self):
        plan = self.prep(StripGens(drop_info={K1}))
        with self.assertRaises(z.FamilyZSlowdownGateStop) as cm:
            self.gate(plan)
        self.assertIn("STD_CHUNK_SLOWDOWN_DURATION_RECORD_MISSING", str(cm.exception))
        shutil.rmtree(self.run)
        plan = self.prep(StripGens(bad_ratio={K2}))
        with self.assertRaises(z.FamilyZSlowdownGateStop) as cm:
            self.gate(plan)
        self.assertIn("RATIO_OUT_OF_RANGE", str(cm.exception))

    def test_direct_verify_covers_chunk_id_even_without_plan(self):
        with self.assertRaises(z.FamilyZSlowdownGateStop):
            z.verify_std_english_slowdown("x", {K1: {"clip_kind": "narrator", "slowdown_applied": False}})
        ok = {"clip_kind": "narrator", "slowdown_applied": True, "slowdown_info": {"src_duration_seconds": 10.0, "dst_duration_seconds": 10.6}}
        self.assertTrue(z.verify_std_english_slowdown("x", {K1: ok})[K1]["ok"])
        pl = {"full_story_part2_c1": {"chunked": True, "chunks": [{"chunk_id": K1}, {"chunk_id": K2}]}}
        with self.assertRaises(z.FamilyZSlowdownGateStop):                                   # planにあるchunkのentry欠落はNG
            z.verify_std_english_slowdown("x", {K1: ok}, chunk_plans=pl)
        # 非chunkのStd narrator(従来経路)は従来どおり
        legacy = {"full_story_part1_c1": {"clip_kind": "narrator", "slowdown_applied": True}}
        self.assertTrue(z.verify_std_english_slowdown("x", legacy)["full_story_part1_c1"]["ok"])

    def test_real_shared_gate_and_assembly_std(self):
        import er003_v1_n3_01_assemble as asm
        plan = self.prep()
        z.run_audio_gate(self.run, "a2", plan, zt.SHELL, article_text="a", skip_shared_gate=True)
        asm.verify_episode_audio_validation_gate(f"{self.run}/a2", z.GATE_LEVEL_STRING["a2"])   # 実Gate: 親(集約True)+chunk+他entry
        tl = z.run_assembly(self.run, "a2", zt.story(), zt.make_plan("a2")[1], chunk_plans=z.chunk_plans_from_specs(plan), kp_third="japanese")
        ct = tl["chunk_tts"]["parents"]["full_story_part2_c1"]
        self.assertEqual(ct["chunk_ids"], [K1, K2])
        a, b = ct["gap_offsets_in_part_s"][0]
        self.assertAlmostEqual(b - a, 0.2, places=3)                                        # 追加ポーズ0.2秒(減速対象外)
        nd = f"{self.run}/a2/narration"
        lens = [len(core.read_pcm16(f"{nd}/{c}.wav")) for c in (K1, K2)]
        part = [e for e in tl["timeline"] if e["part"] == "full_story_part2_c1"][0]
        self.assertAlmostEqual(part["duration_seconds"], (sum(lens) + 4800) / 24000, places=2)

    def test_non_chunk_std_result_still_gates(self):
        """本方式導入前の公開済みStd結果(親entryのみ)は従来経路。非chunk planのgateは従来どおり通る(後方互換)。"""
        plan, kp = zt.make_plan("a2", chunked=False)
        z.run_tts_stage(self.run, "a2", plan, generators=zt.Gens().gens())
        z.provision_shell_assets(self.run, "a2", kp_count=1)
        res = self.gate(plan)
        self.assertTrue(res["m1_slowdown"]["full_story_part2_c1"]["ok"])


class AdvInvarianceGoldenTests(unittest.TestCase):
    @unittest.skipUnless(os.path.exists(GOLDEN), "golden無し")
    def test_adv_plan_specs_reuse_keys_match_frozen_head_golden_and_std_changes_only_chunked_parents(self):
        if not os.path.exists(f"{REPO}/er026_output/family_z_production_e2e_01/melos/run_fzcw_e1_01/segment_plan_b1b.json"):
            self.skipTest("実run dir無し")
        sp = importlib.util.spec_from_file_location("fz_z_adv", FREEZE)
        m = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(m)
        got = m.compute()
        gold = json.load(open(GOLDEN, encoding="utf-8"))
        for run, rec in gold["runs"].items():
            g_b, n_b = rec["b1b"], got["runs"][run]["b1b"]
            self.assertEqual(n_b["chunk_plans_sha256"], g_b["chunk_plans_sha256"], run)      # Adv chunk plan: バイト一致
            if "specs_sha256" in g_b:
                self.assertEqual(n_b["specs_sha256"], g_b["specs_sha256"], run)               # Adv ClipSpec列: バイト一致
                self.assertEqual(n_b["parent_display"], g_b["parent_display"], run)           # b1bの親display(slowdown_applied=None)一致
                self.assertEqual(n_b["attach_chunk_meta"], g_b["attach_chunk_meta"], run)     # chunk_tts meta(level指定なし)一致
                self.assertEqual(n_b["reuse_keys"], g_b["reuse_keys"], run)
            # Std: 変わるのは100語超narratorの親だけ。他specのreuse_key(dialogue含む)は凍結値と一致
            g_a, n_a = rec["a2"], got["runs"][run]["a2"]
            chunked = [p for p, v in n_a["chunk_plans"].items() if v["chunked"]]
            self.assertTrue(chunked, run)
            for p in chunked:
                clip = [c for c in n_a["story_clips"] if c["id"] == p][0]
                self.assertGreater(len(clip["text"].split()), 100)
            for cid, key in g_a["reuse_keys"].items():
                if cid not in chunked:
                    got_key = dict(n_a["reuse_keys"][cid])
                    # FZ-TELL-TALE-HEART-NARRATOR-VOICE-01: 凍結golden(2026-10-24頃)以後に告げ口心臓のNarrator VoiceがAoede->Fenrirへ正式変更された。
                    # narratorのvoiceだけは現行 narrator_voice_for(story) と一致することを確認し、それ以外のkey成分は凍結値と一致させる。
                    if "tell_tale" in run and got_key.get("voice") == "Fenrir" and key.get("voice") == "Aoede":
                        import er062_family_z_structure_01 as _s62
                        self.assertEqual(_s62.narrator_voice_for("the_tell_tale_heart"), "Fenrir")
                        got_key["voice"] = key["voice"]
                    self.assertEqual(got_key, key, f"{run} {cid}")
            self.assertEqual(n_a["story_clips"], g_a["story_clips"])


if __name__ == "__main__":
    unittest.main()
