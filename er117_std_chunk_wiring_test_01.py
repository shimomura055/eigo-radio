# -*- coding: utf-8 -*-
"""CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01 委任_01: Standard(6%減速)×Chunk分割(+0.2秒)の共通部分(er117)のtest。API 0・TTS 0。
実行: PYTHONPATH=netblock_harness_01 .venv/Scripts/python.exe -m pytest er117_std_chunk_wiring_test_01.py -q

検査:
  (1) Adv不変: 実装前HEAD(bb578265c)で凍結したgolden(既存X Adv run 2件・Y Adv run 2件のparts.jsonに対する分割計画)とバイト一致。
      attach_chunk_meta(level未指定)が従来とバイト同一。Zのplanner(levelは次委任まで撤去しない)も不変。
  (2) 合成方式 = 『chunk別減速→0.2秒無音→連結』: 減速後のポーズは正確に4800サンプル(0.2秒)の無音。連結後に減速する方式ではポーズが0.2秒を超える(採らない根拠)。
  (3) Std chunk減速証跡の検査関数(欠落・比率外・entryなし)、親集約、減速証跡なしcacheの再利用拒否。
"""
import json
import os
import shutil
import subprocess
import tempfile
import unittest

import numpy as np

import er003_v1_n3_01_assemble as asm
import er008_a2_postprocess_slowdown_01 as slow
import er117_chunk_tts_production_01 as core

ROOT = os.path.dirname(os.path.abspath(__file__))
GOLDEN = os.path.join(ROOT, "docs", "research", "CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01", "golden", "adv_plans_golden_01.json")
Y_IDS = ("y_lead", "y_intro_1", "y_voice_1", "y_intro_2", "y_voice_2", "y_intro_3", "y_voice_3", "y_closing")


def _sha(o):
    import hashlib
    return hashlib.sha256(json.dumps(o, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


class AdvUnchangedGolden(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(GOLDEN, encoding="utf-8") as f:
            cls.g = json.load(f)

    def test_golden_was_frozen_from_pre_implementation_head_and_planner_version_is_unchanged(self):
        self.assertEqual(self.g["frozen_at_head"], "bb578265c")
        self.assertEqual(self.g["planner_version"], core.CHUNK_PLANNER_VERSION)           # 規則を変えていないので版も不変(Advの旧cache/resumeを壊さない)
        self.assertEqual(self.g["extra_pause_seconds"], core.EXTRA_PAUSE_SECONDS)
        self.assertEqual(core.EXTRA_PAUSE_SECONDS, 0.2)

    def test_x_adv_plans_are_byte_identical_to_golden(self):
        for k, v in self.g["x"].items():
            plans = core.plan_x_parts(v["input_parts"])
            self.assertEqual(_sha(plans), v["plans_sha256"], k)
            self.assertEqual(json.loads(json.dumps(plans, ensure_ascii=False)), v["plans"], k)
            self.assertTrue(v["equals_saved_audit_plan"], k)                                   # 既存runの保存済みchunk_plan_b1b.jsonとも一致していた
        self.assertEqual(self.g["x"]["x_uk_train_run_chunk_01"]["plans"]["full_story_part1"]["chunked"], True)

    def test_y_adv_plans_are_byte_identical_to_golden(self):
        for k, v in self.g["y"].items():
            plans = {sid: core.plan_x_part(v["input_segments"][sid], sid) for sid in Y_IDS}
            self.assertEqual(_sha(plans), v["plans_sha256"], k)
            self.assertEqual(json.loads(json.dumps(plans, ensure_ascii=False)), v["plans"], k)
            self.assertEqual(v["chunked_segments"], [], k)                                    # 実Y記事は各Voice 1段落=不発火(正常)

    def test_attach_chunk_meta_without_level_is_byte_identical_to_legacy(self):
        chunk = {"index": 2, "words": 7, "boundary_kind": "paragraph"}
        e = core.attach_chunk_meta({}, "full_story_part1", chunk, 3)
        self.assertEqual(e, {"chunk_tts": {"planner_version": core.CHUNK_PLANNER_VERSION, "parent_id": "full_story_part1", "index": 2, "count": 3,
                                           "words": 7, "boundary_kind": "paragraph", "extra_pause_s": 0.2}})
        std = core.attach_chunk_meta({}, "full_story_part1", chunk, 3, level="a2")
        self.assertEqual(std["chunk_tts"]["level"], "a2")
        self.assertEqual(std["chunk_tts"]["std_slowdown_composition"], core.STD_SLOWDOWN_COMPOSITION)
        legacy_keys = set(e["chunk_tts"])
        self.assertTrue(legacy_keys < set(std["chunk_tts"]))                                  # Stdは追加keyのみ(既存keyは同値)

    def test_evidence_record_for_adv_chunks_has_no_std_keys(self):
        plan = core.plan_x_part("A one two.\n\nB three four.", "full_story_part1")
        seg = {c["chunk_id"]: {"status": "OK", "attempts": [{}]} for c in plan["chunks"]}
        rows = core.evidence_record(plan, seg)["chunks"]
        self.assertTrue(all("slowdown_applied" not in r for r in rows))

    def test_compose_raw_pcm_pad_is_exact_and_unchanged(self):
        a = (np.arange(1000) % 200 + 1).astype(np.int16)
        b = (np.arange(700) % 90 + 1).astype(np.int16)
        c = core.compose_raw_pcm([a, b])
        self.assertEqual(len(c), 1000 + 4800 + 700)
        self.assertTrue((c[1000:5800] == 0).all())

    def test_z_planner_level_condition_removed_std_and_adv_plans_identical(self):
        # CHUNK-TTS-STD 委任_03: Z側のStd配線(er063の減速合成・速度Gate厳格化)と同時に plan_z_clip のレベル条件を撤去済み。規則はStd/Adv同一。
        clip = {"id": "full_story_part1_c1", "voice": "narrator", "word_count": 130, "text": ("word " * 130).strip()}
        p_std = core.plan_z_clip(clip, [clip["text"]], "a2")
        p_adv = core.plan_z_clip(clip, [clip["text"]], "b1b")
        self.assertEqual(p_std, p_adv)                                                       # Advのplan出力は不変、StdもAdvと同一規則
        self.assertNotIn("level!=b1b", json.dumps(p_std, ensure_ascii=False))


class StdSlowdownCompositionPhysics(unittest.TestCase):
    """chunk別減速→0.2秒無音→連結 の採用根拠(連結後減速ではポーズが0.2秒を超える)を実ffmpegで示す。ffmpegが無い環境ではskip。"""

    def setUp(self):
        try:
            r = subprocess.run([slow.FFMPEG, "-version"], capture_output=True, text=True)
            if r.returncode != 0:
                self.skipTest("ffmpeg not runnable")
        except Exception:
            self.skipTest("ffmpeg not found")
        self.tmp = tempfile.mkdtemp(prefix="stdchunk_phys_")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def _tone(self, name, seconds, f=220):
        t = np.arange(int(core.SR24 * seconds)) / core.SR24
        pcm = (0.3 * np.sin(2 * np.pi * f * t) * 32767).astype(np.int16)
        p = f"{self.tmp}/{name}.wav"
        core.write_pcm16(p, pcm)
        return p

    def test_per_chunk_slowdown_then_pad_keeps_pause_exactly_0_2s(self):
        paths = []
        for i, sec in enumerate((2.0, 3.0, 1.5), start=1):
            src = self._tone(f"c{i}_orig", sec, 200 + 40 * i)
            dst = f"{self.tmp}/c{i}.wav"
            info = slow.apply_a2_slowdown(src, dst)                                      # 既存の減速処理そのまま(6%)
            self.assertAlmostEqual(info["slowdown_pct_actual"], 6.0, delta=0.5)
            paths.append(dst)
        pcms = [core.read_pcm16(p) for p in paths]
        raw = core.compose_raw_pcm(pcms)
        core.verify_composed_samples([len(p) for p in pcms], len(raw))
        pos = 0
        for p in pcms[:-1]:
            pos += len(p)
            self.assertTrue((raw[pos:pos + 4800] == 0).all())                            # ポーズ=減速対象外の正確な4800サンプル
            pos += 4800
        parent = f"{self.tmp}/parent.wav"
        info = core.write_raw_parent(parent, paths)
        core.verify_raw_parent(parent, paths)
        self.assertEqual(info["samples"], sum(len(p) for p in pcms) + 2 * 4800)

    def test_slowdown_after_concat_breaks_the_exact_0_2s_pause_invariant(self):
        # 比較(採らない方式): 先に0.2秒を挟んで連結してから減速すると、全体(ポーズ込み)が約6%伸び、整数サンプルの合成長検査(I8)が成立せず、
        # ポーズも『正確な4800サンプルの無音』ではなくなる(atempoの重なり窓で境界が滑る)。ユーザー承認の『追加ポーズ0.2秒』を保てないため採らない。
        a, b = self._tone("a", 2.0, 220), self._tone("b", 2.0, 330)
        pa, pb = core.read_pcm16(a), core.read_pcm16(b)
        pcm = core.compose_raw_pcm([pa, pb])
        cat, out = f"{self.tmp}/cat.wav", f"{self.tmp}/cat_slow.wav"
        core.write_pcm16(cat, pcm)
        slow.apply_a2_slowdown(cat, out)
        slowed = core.read_pcm16(out)
        with self.assertRaises(core.ChunkIntegrityError):
            core.verify_composed_samples([len(pa), len(pb)], len(slowed))               # Σchunk長+4800 と一致しない
        self.assertGreater(len(slowed) / len(pcm), 1.05)
        best = cur = 0
        for v in (np.abs(slowed.astype(np.int32)) == 0):
            cur = cur + 1 if v else 0
            best = max(best, cur)
        self.assertNotEqual(best, 4800)                                                  # 実測4569: 『正確な0.2秒』ではない


class StdChunkSlowdownEvidence(unittest.TestCase):
    PLAN = core.plan_x_part("A first para here.\n\nB second para here.\n\nC third para here.", "full_story_part1")

    def _seg(self, **over):
        segs = {}
        for c in self.PLAN["chunks"]:
            segs[c["chunk_id"]] = {"status": "OK", "slowdown_applied": True,
                                   "slowdown_info": {"src_duration_seconds": 10.0, "dst_duration_seconds": 10.6}}
        for k, v in over.items():
            if v is None:
                segs.pop(k)
            else:
                segs[k] = v
        return segs

    def test_all_chunks_slowed_is_clean_and_parent_aggregates_true(self):
        segs = self._seg()
        self.assertEqual(core.std_chunk_slowdown_violations(self.PLAN, segs), [])
        f = core.std_parent_slowdown_fields(self.PLAN, segs)
        self.assertIs(f["slowdown_applied"], True)
        self.assertEqual(f["std_chunk_slowdown_violations"], [])

    def test_missing_slowdown_on_a_later_chunk_is_detected_and_parent_is_false(self):
        segs = self._seg(full_story_part1_k3={"status": "OK", "slowdown_applied": False})
        bad = core.std_chunk_slowdown_violations(self.PLAN, segs)
        self.assertEqual([b["segment"] for b in bad], ["full_story_part1_k3"])
        self.assertIn("STD_CHUNK_MISSING_MANDATORY_A2_SLOWDOWN", bad[0]["violations"])
        self.assertIs(core.std_parent_slowdown_fields(self.PLAN, segs)["slowdown_applied"], False)

    def test_none_or_absent_slowdown_flag_is_a_violation_no_legacy_fallback(self):
        segs = self._seg(full_story_part1_k2={"status": "OK"})
        self.assertEqual([b["segment"] for b in core.std_chunk_slowdown_violations(self.PLAN, segs)], ["full_story_part1_k2"])

    def test_ratio_out_of_range_and_missing_entry(self):
        segs = self._seg(full_story_part1_k1={"status": "OK", "slowdown_applied": True,
                                              "slowdown_info": {"src_duration_seconds": 10.0, "dst_duration_seconds": 8.1}},
                         full_story_part1_k3=None)
        bad = {b["segment"]: b["violations"] for b in core.std_chunk_slowdown_violations(self.PLAN, segs)}
        self.assertTrue(bad["full_story_part1_k1"][0].startswith("STD_CHUNK_SLOWDOWN_RATIO_OUT_OF_RANGE"))
        self.assertEqual(bad["full_story_part1_k3"], ["NO_SEGMENT_RECORD"])

    def test_unchunked_plan_has_no_chunk_violations(self):
        plan = core.plan_x_part("Only one paragraph here.", "full_story_part2")
        self.assertEqual(core.std_chunk_slowdown_violations(plan, {}), [])

    def test_ratio_range_matches_the_shared_gate_constants(self):
        self.assertEqual(core.STD_SLOWDOWN_RATIO_MIN, asm._A2_SLOWDOWN_ORIGINAL_RATIO_MIN)
        self.assertEqual(core.STD_SLOWDOWN_RATIO_MAX, asm._A2_SLOWDOWN_ORIGINAL_RATIO_MAX)

    def test_drop_cached_std_chunks_without_slowdown(self):
        cached = {"segments": {"full_story_part1_k1": {"slowdown_applied": True}, "full_story_part1_k2": {"slowdown_applied": None},
                               "full_story_part1_k3": {}, "full_story_part2": {"x": 1}, "y_voice_2_k1": {"slowdown_applied": False}}}
        out = core.drop_cached_std_chunks_without_slowdown(cached)
        # 既定のchunk id判定はX/Z形式。Y形式(y_voice_2_k1)は呼出側がis_chunk_idを渡す(下)。
        self.assertEqual(sorted(out["segments"]), ["full_story_part1_k1", "full_story_part2", "y_voice_2_k1"])
        import re
        yre = re.compile(r"y_(?:lead|closing|intro_[1-3]|voice_[1-3])_k[1-9][0-9]*")
        out_y = core.drop_cached_std_chunks_without_slowdown(cached, is_chunk_id=lambda k: bool(yre.fullmatch(k)) or core.parse_chunk_id(k) is not None)
        self.assertEqual(sorted(out_y["segments"]), ["full_story_part1_k1", "full_story_part2"])
        same = {"segments": {"full_story_part1_k1": {"slowdown_applied": True}}}
        self.assertIs(core.drop_cached_std_chunks_without_slowdown(same), same)
        self.assertIsNone(core.drop_cached_std_chunks_without_slowdown(None))

    def test_evidence_record_carries_std_slowdown_fields(self):
        segs = self._seg()
        for e in segs.values():
            e["slowdown_info"]["slowdown_pct_actual"] = 5.98
            e["post_slowdown_final_classification"] = "NORMALIZED_MATCH"
        rows = core.evidence_record(self.PLAN, segs)["chunks"]
        self.assertTrue(all(r["slowdown_applied"] is True and r["slowdown_pct_actual"] == 5.98 for r in rows))
        self.assertEqual(rows[0]["post_slowdown_classification"], "NORMALIZED_MATCH")


if __name__ == "__main__":
    unittest.main()
