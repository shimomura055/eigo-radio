# -*- coding: utf-8 -*-
"""FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01 委任_01 test雛形(Production未編集。API 0・TTS 0)。
実行: py -m pytest docs/research/FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01/tests_draft_01.py -q  (repo root で)
実装委任では、本ファイルの T* をProduction module(er117_chunk_tts_production_01, 仮称)向けに移し、
下の「実装委任で追加するtest(skip雛形)」をProduction配線(er019/er063/er020)に対して実装する。"""
import os
import sys
import unittest

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)
import chunk_tts_core_draft_01 as core  # noqa: E402

TTH2 = "er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_sf_prod_02"
UK_PARTS = "er019_output/family_x_audio_production_wiring_01/uk_train_speaker_playback__run_nws_02/b1b/parts.json"


def _clip(text, voice="narrator", cid="full_story_part1_c1"):
    t = core.normalize_for_tts(text)
    return {"id": cid, "voice": voice, "word_count": len(t.split()), "text": t}


class TPlannerZ(unittest.TestCase):
    def test_dialogue_and_std_and_short_unchanged(self):
        p = ["word " * 130]
        self.assertFalse(core.plan_z_clip(_clip(p[0], voice="old_man"), p)["chunked"])
        self.assertFalse(core.plan_z_clip(_clip(p[0]), p, level="a2")["chunked"])      # Std対象外
        q = ["One two three. " * 20]
        self.assertFalse(core.plan_z_clip(_clip(q[0]), q)["chunked"])                   # 60語

    def test_exactly_100_not_split_101_split(self):
        s = "Alpha beta gamma delta epsilon. "                                          # 5語/文
        p100 = [(s * 20).strip()]
        p101 = [(s * 20).strip() + " Zeta."]
        self.assertFalse(core.plan_z_clip(_clip(p100[0]), p100)["chunked"])
        self.assertTrue(core.plan_z_clip(_clip(p101[0]), p101)["chunked"])

    def test_deterministic_and_k_equals_ceil(self):
        paras = [("Alpha beta gamma delta. " * 14).strip() for _ in range(3)]          # 168語
        c = _clip(" ".join(paras))
        a, b = core.plan_z_clip(c, paras), core.plan_z_clip(c, paras)
        self.assertEqual(a, b)
        self.assertEqual(len(a["chunks"]), 2)                                           # ceil(168/100)

    def test_paragraph_boundary_preferred_lossless_order(self):
        paras = [("Alpha beta gamma delta. " * 11).strip(), ("Eps zeta eta theta. " * 11).strip(), ("Iota kappa lambda mu. " * 11).strip()]
        c = _clip(" ".join(paras))
        r = core.plan_z_clip(c, paras)
        self.assertTrue(r["chunked"])
        self.assertTrue(all(x["boundary_kind"] == "paragraph" for x in r["chunks"]))
        self.assertEqual(core.normalize_for_tts(" ".join(x["text"] for x in r["chunks"])), c["text"])
        self.assertEqual([x["index"] for x in r["chunks"]], list(range(1, len(r["chunks"]) + 1)))
        self.assertEqual(sum(x["words"] for x in r["chunks"]), c["word_count"])

    def test_never_cut_inside_quote_and_min_words(self):
        para = 'He said "Go now. Run fast. Do it." ' + ("Plain words here and there. " * 30)
        r = core.plan_z_clip(_clip(para), [para])
        for ch in r.get("chunks", []):
            self.assertEqual(ch["text"].count('"') % 2, 0)
            self.assertGreaterEqual(ch["words"], core.Z_MIN_CHUNK_WORDS)

    def test_text_mismatch_fails_closed(self):
        with self.assertRaises(core.ChunkIntegrityError):
            core.plan_z_clip(_clip("word " * 130), ["different " * 130])

    @unittest.skipUnless(os.path.exists(os.path.join(ROOT, TTH2, "segment_plan_b1b.json")), "run_sf_prod_02 missing")
    def test_equals_adopted_trial_planner_on_real_run(self):
        """採用Trial方式(er114 plan_clip_chunks)と実runで出力一致(分割位置・語数)。"""
        import er114_fz_narration_chunk_trial_01 as trial
        r_trial = trial.plan_run(TTH2, "b1b", "writer/r2.md")
        import json
        import er062_family_z_structure_01 as st
        plan = json.load(open(os.path.join(ROOT, TTH2, "segment_plan_b1b.json"), encoding="utf-8"))
        _, body = st.split_title_body(open(os.path.join(ROOT, TTH2, "writer/r2.md"), encoding="utf-8").read())
        paras = st.clean_body_paragraphs(body)
        got = {}
        for c in plan["clips"]:
            pt = [paras[i] for i in c["source_paragraph_indices"]]
            if core.normalize_for_tts(" ".join(pt)) != core.normalize_for_tts(c["text"]):
                pt = [c["text"]]
            r = core.plan_z_clip(c, pt)
            got[c["id"]] = [x["words"] for x in r["chunks"]]
        want = {c["clip_id"]: [x["words"] for x in c["chunks"]] for c in r_trial["clips"]}
        self.assertEqual(got, want)
        self.assertEqual({k: v for k, v in got.items() if v}, {"full_story_part2_c1": [58, 62], "full_story_part3_c1": [65, 61]})


class TPlannerX(unittest.TestCase):
    def test_paragraph_chunks_lossless(self):
        t = "P one is here.\n\nP two is here now.\n\n  \nP three."
        r = core.plan_x_part(t, "full_story_part1")
        self.assertTrue(r["chunked"])
        self.assertEqual([c["chunk_id"] for c in r["chunks"]], ["full_story_part1_k1", "full_story_part1_k2", "full_story_part1_k3"])
        self.assertEqual(sum(c["words"] for c in r["chunks"]), core.wc(t))

    def test_single_paragraph_not_chunked(self):
        self.assertFalse(core.plan_x_part("Only one paragraph here.", "full_story_part2")["chunked"])

    @unittest.skipUnless(os.path.exists(os.path.join(ROOT, UK_PARTS)), "uk_train parts.json missing")
    def test_uk_train_matches_trial_10_chunks(self):
        import json
        parts = json.load(open(os.path.join(ROOT, UK_PARTS), encoding="utf-8"))
        n = [len(core.plan_x_part(parts[f"part{i}"], f"full_story_part{i}")["chunks"]) for i in (1, 2, 3)]
        self.assertEqual(n, [4, 3, 3])
        import er113_fx_paragraph_chunk_trial_01 as trial
        want = [(c["chunk_id"], c["text"]) for c in trial.build_chunk_plan(parts)]
        got = [(c["text"]) for i in (1, 2, 3) for c in core.plan_x_part(parts[f"part{i}"], f"full_story_part{i}")["chunks"]]
        self.assertEqual([w[1] for w in want], got)


class TCompose(unittest.TestCase):
    def setUp(self):
        # p9a.rms/peak と同一定義(sqrt(mean(x^2)) / max|x|)。p9a自体はgoogle.genai依存のimport連鎖があり、軽量testでは使わない
        self.rms = lambda x: float(np.sqrt(np.mean(np.square(x.astype("float64")))))
        self.peak = lambda x: float(np.max(np.abs(x)))
        rng = np.random.default_rng(0)
        self.chunks = [rng.normal(0, a, n).astype("float32") for a, n in ((0.05, 24000), (0.09, 36000), (0.03, 12000))]

    def test_raw_parent_length_equals_sum_plus_pads(self):
        raw = core.compose_raw_parent(self.chunks)
        self.assertEqual(len(raw), sum(len(c) for c in self.chunks) + 2 * core.pad_samples())
        core.verify_composed_duration([len(c) / core.SR24 for c in self.chunks], len(raw) / core.SR24)

    def test_gain_per_chunk_not_per_parent(self):
        mono, gains, post, bounds = core.compose_gained_parent(self.chunks, 0.09, self.rms, self.peak)
        self.assertEqual(len(gains), 3)
        self.assertEqual(len(bounds), 2)
        for p in post:
            self.assertAlmostEqual(p, 0.09, delta=0.0006)                                # 各chunkがtargetへ(peak頭打ち無し前提)
        self.assertLess(bounds[0], bounds[1])

    def test_peak_cap(self):
        loud = [np.concatenate([np.zeros(100), np.full(10, 0.99, dtype="float32"), np.full(2000, 0.001, dtype="float32")])]
        _, _, _, _ = core.compose_gained_parent(loud, 0.09, self.rms, self.peak)
        mono, gains, _, _ = core.compose_gained_parent(loud, 0.09, self.rms, self.peak)
        self.assertLessEqual(float(np.max(np.abs(mono))), 0.95 + 1e-6)

    def test_duration_check_detects_missing_or_duplicate(self):
        raw = core.compose_raw_parent(self.chunks)
        durs = [len(c) / core.SR24 for c in self.chunks]
        with self.assertRaises(core.ChunkIntegrityError):
            core.verify_composed_duration(durs[:-1], len(raw) / core.SR24)                  # 1 chunk欠落
        with self.assertRaises(core.ChunkIntegrityError):
            core.verify_composed_duration(durs + [durs[0]], len(raw) / core.SR24)           # 重複


class TIntegrity(unittest.TestCase):
    def _plan(self):
        paras = [("Alpha beta gamma delta. " * 11).strip(), ("Eps zeta eta theta. " * 11).strip(), ("Iota kappa lambda mu. " * 11).strip()]
        c = _clip(" ".join(paras))
        return core.plan_z_clip(c, paras), c["text"]

    def _entries(self, plan):
        return [{"segment_id": ch["chunk_id"], "canonical_text": ch["text"],
                 "chunk_tts": {"planner_version": core.CHUNK_PLANNER_VERSION}} for ch in plan["chunks"]]

    def _parent(self, plan):
        return {"chunk_tts": {"chunk_ids": [c["chunk_id"] for c in plan["chunks"]], "words": [c["words"] for c in plan["chunks"]]}}

    def test_ok(self):
        p, t = self._plan()
        self.assertTrue(core.verify_parent_integrity(p, t, self._entries(p), self._parent(p))["ok"])

    def test_missing_chunk(self):
        p, t = self._plan()
        with self.assertRaises(core.ChunkIntegrityError):
            core.verify_parent_integrity(p, t, self._entries(p)[:-1], self._parent(p))

    def test_duplicate_or_extra_chunk(self):
        p, t = self._plan()
        e = self._entries(p)
        e.append(dict(e[0], segment_id="full_story_part1_c1_k9"))
        with self.assertRaises(core.ChunkIntegrityError):
            core.verify_parent_integrity(p, t, e, self._parent(p))

    def test_order_changed(self):
        p, t = self._plan()
        par = self._parent(p)
        par["chunk_tts"]["chunk_ids"] = list(reversed(par["chunk_tts"]["chunk_ids"]))
        with self.assertRaises(core.ChunkIntegrityError):
            core.verify_parent_integrity(p, t, self._entries(p), par)

    def test_text_changed_after_generation(self):
        p, t = self._plan()
        e = self._entries(p)
        e[0]["canonical_text"] = e[0]["canonical_text"] + " extra"
        with self.assertRaises(core.ChunkIntegrityError):
            core.verify_parent_integrity(p, t, e, self._parent(p))

    def test_old_planner_version_not_reused(self):
        p, t = self._plan()
        e = self._entries(p)
        e[1]["chunk_tts"]["planner_version"] = "chunk_tts_v0"
        with self.assertRaises(core.ChunkIntegrityError):
            core.verify_parent_integrity(p, t, e, self._parent(p))

    def test_parent_marked_chunked_but_plan_not_chunked(self):
        plan = {"chunked": False, "chunks": []}
        with self.assertRaises(core.ChunkIntegrityError):
            core.verify_parent_integrity(plan, "x", [], {"chunk_tts": {"chunk_ids": ["a"]}})


class TReuseKey(unittest.TestCase):
    def test_chunk_fields_change_with_planner_version_and_index(self):
        ch = {"index": 1}
        a = core.chunk_reuse_key_fields("p", ch, 2)
        b = core.chunk_reuse_key_fields("p", {"index": 2}, 2)
        self.assertNotEqual(a, b)
        self.assertEqual(a["chunk_tts"]["planner_version"], core.CHUNK_PLANNER_VERSION)
        self.assertEqual(a["chunk_tts"]["extra_pause_s"], 0.2)


class TResumeReconstruct(unittest.TestCase):
    def test_same_inputs_same_plan_after_resume(self):
        paras = [("Alpha beta gamma delta. " * 14).strip() for _ in range(3)]
        c = _clip(" ".join(paras))
        first = core.plan_z_clip(c, paras)
        after_resume = core.plan_z_clip(dict(c), list(paras))                                # 保存済みplanを使わず再構成しても同一(決定論)
        self.assertEqual(first, after_resume)

    def test_text_change_changes_chunk_text_sha(self):
        paras = [("Alpha beta gamma delta. " * 14).strip() for _ in range(3)]
        c = _clip(" ".join(paras))
        base = core.plan_z_clip(c, paras)
        paras2 = [paras[0] + " Added sentence here today.", paras[1], paras[2]]
        c2 = _clip(" ".join(paras2))
        new = core.plan_z_clip(c2, paras2)
        self.assertNotEqual([core.sha256_text(x["text"]) for x in base["chunks"]], [core.sha256_text(x["text"]) for x in new["chunks"]])


# ---------------------------------------------------------------------------------------------------------
# 実装委任で追加するtest(skip雛形。Production配線ができてから実装。ここでは識別子と検証内容だけ固定する)
# ---------------------------------------------------------------------------------------------------------
@unittest.skip("実装委任: resolve_narrative_role が full_story_part{n}(_c{k})?_k{j} をFULL_STORYへ解決(chunk wavにCS層/Repetition QA/発音resolverが掛かる)")
class TImpl_RoleResolution(unittest.TestCase):
    def test_x_chunk_id_resolves_full_story(self): ...
    def test_z_chunk_id_resolves_full_story(self): ...
    def test_non_chunk_ids_unchanged(self): ...


@unittest.skip("実装委任: X runner generate_family_x_b1_segments の本文3 partがchunk経路を通り、各chunkで news_tail_fix.generate_news_narration_wide_margin が同一引数(style/tts_backend/enable_*)で呼ばれる(mock)")
class TImpl_XWiring(unittest.TestCase):
    def test_body_parts_call_generator_per_chunk_with_same_kwargs(self): ...
    def test_a2_standard_path_unchanged_no_chunk(self): ...
    def test_gate_failure_in_chunk_k_retries_only_that_chunk_and_resume_reuses_ok_chunks(self): ...
    def test_parent_wav_is_raw_concat_with_0p2_and_sha_recorded(self): ...
    def test_assemble_applies_per_chunk_gain_then_pad_then_stereo(self): ...
    def test_old_unchunked_cache_entry_not_reused(self): ...


@unittest.skip("実装委任: Z build_level_plan がAdvのnarrator>100語clipをchunk ClipSpecへ展開、a2/dialogue/短narratorは不変")
class TImpl_ZWiring(unittest.TestCase):
    def test_plan_expands_only_adv_long_narrator(self): ...
    def test_build_reuse_key_adds_chunk_tts_only_for_chunks(self): ...
    def test_run_assembly_sequence_has_0p2_between_chunks_and_0p5_after_last(self): ...
    def test_only_clips_parent_id_expands_to_its_chunks(self): ...
    def test_verify_z_speed_profile_covers_chunk_ids_adv_narrator_none(self): ...
    def test_pages_row_uses_parent_clip_id(self): ...


if __name__ == "__main__":
    unittest.main()
