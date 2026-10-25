# -*- coding: utf-8 -*-
"""FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01 委任_02: 共通module er117 のunit test(API 0・TTS 0)。
実行: .venv/Scripts/python.exe -m pytest er117_chunk_tts_production_01_test_01.py -q  (repo root)
DEV/Trial moduleのimportなし(期待値はplanner_fixture_01.jsonに凍結。commit 13c640bcのallow-list方針)。"""
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
import unittest

import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import er117_chunk_tts_production_01 as core  # noqa: E402
import er020_tts_retry_local_rewrite_01 as er020  # noqa: E402

FIXTURE = os.path.join(ROOT, "docs", "research", "FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01", "planner_fixture_01.json")


def _clip(text, voice="narrator", cid="full_story_part1_c1"):
    t = core.normalize_for_tts(text)
    return {"id": cid, "voice": voice, "word_count": len(t.split()), "text": t}


def _lf(b):
    """入力ファイルのsha比較は改行正規化(Windows autocrlfのCRLF作業コピーとLFで同値にする)。"""
    return b.replace(b"\r\n", b"\n")


def _sha(b):
    return hashlib.sha256(b).hexdigest()


class TPlannerZ(unittest.TestCase):
    def test_dialogue_and_std_and_short_unchanged(self):
        p = ["word " * 130]
        self.assertFalse(core.plan_z_clip(_clip(p[0], voice="old_man"), p)["chunked"])
        self.assertFalse(core.plan_z_clip(_clip(p[0]), p, level="a2")["chunked"])      # Std対象外
        q = ["One two three. " * 20]
        self.assertFalse(core.plan_z_clip(_clip(q[0]), q)["chunked"])                   # 60語

    def test_exactly_100_not_split_101_split(self):
        s = "Alpha beta gamma delta epsilon. "
        p100, p101 = [(s * 20).strip()], [(s * 20).strip() + " Zeta."]
        self.assertFalse(core.plan_z_clip(_clip(p100[0]), p100)["chunked"])
        self.assertTrue(core.plan_z_clip(_clip(p101[0]), p101)["chunked"])

    def test_deterministic_and_k_equals_ceil(self):
        paras = [("Alpha beta gamma delta. " * 14).strip() for _ in range(3)]
        c = _clip(" ".join(paras))
        a, b = core.plan_z_clip(c, paras), core.plan_z_clip(c, paras)
        self.assertEqual(a, b)
        self.assertEqual(len(a["chunks"]), 2)

    def test_paragraph_boundary_preferred_lossless_order(self):
        paras = [("Alpha beta gamma delta. " * 11).strip(), ("Eps zeta eta theta. " * 11).strip(), ("Iota kappa lambda mu. " * 11).strip()]
        c = _clip(" ".join(paras))
        r = core.plan_z_clip(c, paras)
        self.assertTrue(r["chunked"])
        self.assertTrue(all(x["boundary_kind"] == "paragraph" for x in r["chunks"]))
        self.assertEqual(core.normalize_for_tts(" ".join(x["text"] for x in r["chunks"])), c["text"])
        self.assertEqual([x["index"] for x in r["chunks"]], list(range(1, len(r["chunks"]) + 1)))
        self.assertEqual(sum(x["words"] for x in r["chunks"]), c["word_count"])
        self.assertEqual([x["chunk_id"] for x in r["chunks"]], [f"full_story_part1_c1_k{i}" for i in range(1, len(r["chunks"]) + 1)])

    def test_never_cut_inside_quote_and_min_words(self):
        para = 'He said "Go now. Run fast. Do it." ' + ("Plain words here and there. " * 30)
        r = core.plan_z_clip(_clip(para), [para])
        self.assertTrue(r["chunked"])
        for ch in r["chunks"]:
            self.assertEqual(ch["text"].count('"') % 2, 0)
            self.assertGreaterEqual(ch["words"], core.Z_MIN_CHUNK_WORDS)

    def test_text_mismatch_fails_closed(self):
        with self.assertRaises(core.ChunkIntegrityError):
            core.plan_z_clip(_clip("word " * 130), ["different " * 130])

    def test_paragraph_info_lost_falls_back_to_sentence_only(self):
        clip = dict(_clip(("Alpha beta gamma delta. " * 30).strip()), source_paragraph_indices=[0, 1])
        texts, lost = core.paragraph_texts_for_clip(clip, ["Alpha beta gamma delta.", "unrelated paragraph"])
        self.assertTrue(lost)
        self.assertEqual(texts, [clip["text"]])
        texts, lost = core.paragraph_texts_for_clip(dict(clip, source_paragraph_indices=[0, 1, 2]), ["a"])   # index外
        self.assertTrue(lost)

    def test_plan_z_level_marks_lost_and_unchanged_clips(self):
        paras = [("Alpha beta gamma delta. " * 14).strip() for _ in range(3)]
        clips = [dict(_clip(" ".join(paras)), source_paragraph_indices=[0, 1, 2]),
                 dict(_clip("Short one. " * 3, cid="full_story_part1_c2"), source_paragraph_indices=[0])]
        r = core.plan_z_level(clips, paras)
        self.assertTrue(r["full_story_part1_c1"]["chunked"])
        self.assertFalse(r["full_story_part1_c2"]["chunked"])
        self.assertTrue(r["full_story_part1_c2"]["paragraph_info_lost"])
        self.assertEqual(core.plan_z_level(clips, paras, level="a2")["full_story_part1_c1"]["chunked"], False)


class TPlannerX(unittest.TestCase):
    def test_paragraph_chunks_lossless(self):
        t = "P one is here.\n\nP two is here now.\n\n  \nP three."
        r = core.plan_x_part(t, "full_story_part1")
        self.assertTrue(r["chunked"])
        self.assertEqual([c["chunk_id"] for c in r["chunks"]], ["full_story_part1_k1", "full_story_part1_k2", "full_story_part1_k3"])
        self.assertEqual(sum(c["words"] for c in r["chunks"]), core.wc(t))

    def test_single_paragraph_not_chunked(self):
        self.assertFalse(core.plan_x_part("Only one paragraph here.", "full_story_part2")["chunked"])

    def test_plan_x_parts_names(self):
        parts = {"part1": "A a.\n\nB b.", "part2": "C c.", "part3": "D d.\n\nE e.\n\nF f."}
        r = core.plan_x_parts(parts)
        self.assertEqual(sorted(r), ["full_story_part1", "full_story_part2", "full_story_part3"])
        self.assertEqual([len(r[k]["chunks"]) for k in sorted(r)], [2, 0, 3])


class TFrozenPlannerFixture(unittest.TestCase):
    """I3: 採用Trial planner出力(凍結)と、ディスク上の全Z run・全X parts.jsonでchunk本文(sha)・語数・boundary_kind・境界段落まで一致。"""

    @classmethod
    def setUpClass(cls):
        with open(FIXTURE, encoding="utf-8") as f:
            cls.fx = json.load(f)

    def test_z_all_runs_match_frozen_trial_planner(self):
        import er062_family_z_structure_01 as st
        checked_runs = checked_clips = split_clips = 0
        for run, v in sorted(self.fx["z_runs"].items()):
            sp, art = os.path.join(ROOT, run, "segment_plan_b1b.json"), os.path.join(ROOT, run, "writer", "r2.md")
            if not (os.path.exists(sp) and os.path.exists(art)) or "clips" not in v:
                continue
            if _sha(_lf(open(sp, "rb").read()) + _lf(open(art, "rb").read())) != v["input_sha"]:
                continue                                  # 入力が後から変わったrunは比較しない(下で最低件数を要求)
            plan = json.load(open(sp, encoding="utf-8"))
            _, body = st.split_title_body(open(art, encoding="utf-8").read())
            paras = st.clean_body_paragraphs(body)
            got = core.plan_z_level(plan["clips"], paras, "b1b")
            for cid, want in v["clips"].items():
                g = got[cid]
                gk = [[c["words"], c["boundary_kind"], core.sha256_text(c["text"]), c["first_para"], c["last_para"]] for c in g["chunks"]]
                self.assertEqual(gk, want["chunks"], f"{run}:{cid}")
                self.assertEqual(g["paragraph_info_lost"], want["paragraph_info_lost"], f"{run}:{cid}")
                checked_clips += 1
                split_clips += 1 if want["chunks"] else 0
            checked_runs += 1
        self.assertGreaterEqual(checked_runs, 10)
        self.assertGreaterEqual(split_clips, 10)
        # 実run run_sf_prod_02(承認Trial対象)の期待分割
        r2 = self.fx["z_runs"]["er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_sf_prod_02"]["clips"]
        self.assertEqual({k: [c[0] for c in v["chunks"]] for k, v in r2.items() if v["chunks"]},
                         {"full_story_part2_c1": [58, 62], "full_story_part3_c1": [65, 61]})

    def test_x_all_parts_json_match_frozen_trial_planner(self):
        checked = chunked_parts = 0
        for pj, v in sorted(self.fx["x_parts"].items()):
            path = os.path.join(ROOT, pj)
            if not os.path.exists(path) or _sha(_lf(open(path, "rb").read())) != v["input_sha"]:
                continue
            parts = json.load(open(path, encoding="utf-8"))
            plans = core.plan_x_parts(parts)
            got = []
            for n in (1, 2, 3):
                p = plans[f"full_story_part{n}"]
                for c in p["chunks"]:
                    got.append([n, c["index"], c["words"], core.sha256_text(c["text"])])
                    self.assertEqual(c["boundary_kind"], "paragraph")
                chunked_parts += 1 if p["chunked"] else 0
            # Trialは段落1つのpartも1 chunkとして扱う。er117は『段落1つ=従来の1 call(chunk化しない)』。その差だけを許容して照合する。
            want = [w for w in v["chunks"]]
            by_part = {n: [w for w in want if w[0] == n] for n in (1, 2, 3)}
            exp = []
            for n in (1, 2, 3):
                exp += by_part[n] if len(by_part[n]) >= core.X_MIN_PARAGRAPHS_FOR_CHUNKING else []
            self.assertEqual(got, [[a, b, c, d] for a, b, c, d in exp], pj)
            checked += 1
        self.assertGreaterEqual(checked, 100)
        self.assertGreater(chunked_parts, 100)


class TRoleResolution(unittest.TestCase):
    """C4/I4/R4: chunk IDがFULL_STORYに解決され、既存IDの戻り値は不変。"""

    @staticmethod
    def _legacy(seg):
        # 変更前のresolve_narrative_roleと同じ規則(FULL_STORY系のみ)。chunk追加以外の差が無いことの比較に使う。
        if not seg:
            return None
        if seg in ("full_story_part1", "full_story_part2", "full_story_part3", "point_one", "point_two"):
            return "FULL_STORY"
        if re.fullmatch(r"full_story_part[1-3]_c[0-9]+", seg):
            return "FULL_STORY"
        return "UNCHANGED"

    def test_chunk_ids_resolve_full_story_and_cs_enabled(self):
        for s in ("full_story_part1_k1", "full_story_part2_k12", "full_story_part3_c1_k2", "full_story_part1_c14_k3"):
            self.assertEqual(er020.resolve_narrative_role(s), "FULL_STORY", s)
            self.assertTrue(er020.connected_speech_enabled_for(s), s)

    def test_adjacent_ids_do_not_match(self):
        for s in ("full_story_part1_k", "full_story_part1_k0", "full_story_part1_k01", "full_story_part1_c1_k", "full_story_part4_k1",
                  "full_story_part1_k1_original", "full_story_part1_k1_heading", "full_story_part1_c1_k1x", "full_story_part1_kk1",
                  "xfull_story_part1_k1"):
            self.assertIsNone(er020.resolve_narrative_role(s), s)

    def test_existing_ids_unchanged_over_all_results_on_disk(self):
        ids = set()
        for root, dirs, files in os.walk(ROOT):
            dirs[:] = [d for d in dirs if d.endswith("_output") or root != ROOT]
            if "tts_generation_results.json" in files and os.path.basename(root) == "audit":
                try:
                    d = json.load(open(os.path.join(root, "tts_generation_results.json"), encoding="utf-8"))
                except Exception:
                    continue
                ids.update((d.get("segments") or {}).keys())
            if len(ids) > 5000:
                break
        self.assertGreater(len(ids), 20)
        for s in sorted(ids):
            if core.parse_chunk_id(s) or s.startswith("y_"):
                continue
            if self._legacy(s) == "FULL_STORY":
                self.assertEqual(er020.resolve_narrative_role(s), "FULL_STORY", s)
        # chunk形でないfull_story系IDが新たにFULL_STORYへ解決されていないこと
        # 委任_05: Family YのID(`y_lead`/`y_voice_N`等とそのchunk `_kN`)は委任_02B/05で意図的にFULL_STORYへ追加した(X/Z既存IDとは別名前空間)。
        # 『X/Z既存IDの解決が不変』の検査対象から除外する。Yの解決は er121_family_y_text_core_01_test_01.py で固定。
        for s in sorted(ids):
            if core.parse_chunk_id(s) or s.startswith("y_"):
                continue
            if er020.resolve_narrative_role(s) == "FULL_STORY":
                self.assertEqual(self._legacy(s), "FULL_STORY", s)

    def test_regex_consistency_between_er020_and_er117(self):
        for s in ("full_story_part1_k1", "full_story_part2_c3_k9", "full_story_part1_c1", "full_story_part1", "comment_1", "full_story_part1_k0",
                  "full_story_part3_c1_k10", "full_story_part1_k"):
            self.assertEqual(core.parse_chunk_id(s) is not None, bool(er020._CHUNK_TTS_SEGMENT_PATTERN.fullmatch(s)), s)
        self.assertEqual(core.parse_chunk_id("full_story_part2_c3_k9"), ("full_story_part2_c3", 9, "Z"))
        self.assertEqual(core.parse_chunk_id("full_story_part1_k2"), ("full_story_part1", 2, "X"))


class TCompose(unittest.TestCase):
    def setUp(self):
        import er003_b1_p9a_audio as p9a
        self.p9a = p9a
        rng = np.random.default_rng(0)
        self.chunks = [rng.normal(0, a, n).astype("float64") for a, n in ((0.05, 24000), (0.09, 36000), (0.03, 12000))]
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _write_chunks(self):
        paths = []
        for i, c in enumerate(self.chunks, 1):
            p = os.path.join(self.tmp, f"parent_k{i}.wav")
            core.write_pcm16(p, (np.clip(c, -1, 1) * 32767).astype(np.int16))
            paths.append(p)
        return paths

    def test_raw_parent_is_exact_pcm_concat_with_pads(self):
        paths = self._write_chunks()
        parent = os.path.join(self.tmp, "parent.wav")
        info = core.write_raw_parent(parent, paths)
        lens = [len(core.read_pcm16(p)) for p in paths]
        self.assertEqual(info["samples"], sum(lens) + 2 * core.pad_samples())
        self.assertEqual(core.pad_samples(), 4800)
        self.assertTrue(core.verify_raw_parent(parent, paths)["ok"])
        got = core.read_pcm16(parent)
        self.assertEqual(int(np.count_nonzero(got[lens[0]:lens[0] + 4800])), 0)           # 0.2秒の無音
        self.assertTrue(np.array_equal(got[:lens[0]], core.read_pcm16(paths[0])))
        self.assertEqual(info["sha256"], core.sha256_file(parent))

    def test_verify_raw_parent_detects_tamper_missing_duplicate_and_stale(self):
        paths = self._write_chunks()
        parent = os.path.join(self.tmp, "parent.wav")
        core.write_raw_parent(parent, paths)
        with self.assertRaises(core.ChunkIntegrityError):
            core.verify_raw_parent(parent, paths[:-1])                       # 1 chunk欠落(古い親wav)
        with self.assertRaises(core.ChunkIntegrityError):
            core.verify_raw_parent(parent, paths + [paths[0]])               # 重複
        with self.assertRaises(core.ChunkIntegrityError):
            core.verify_raw_parent(parent, [paths[1], paths[0], paths[2]])   # 順序
        core.write_pcm16(paths[1], core.read_pcm16(paths[1])[:-5])           # chunkだけ差し替わった(親が古い)
        with self.assertRaises(core.ChunkIntegrityError):
            core.verify_raw_parent(parent, paths)
        with self.assertRaises(core.ChunkIntegrityError):
            core.verify_raw_parent(os.path.join(self.tmp, "none.wav"), paths)

    def test_duration_check_integer_samples(self):
        lens = [24000, 36000, 12000]
        total = core.expected_raw_samples(lens)
        core.verify_composed_samples(lens, total)
        for bad in (total - 1, total + 1, total - 4800, total + 24000):
            with self.assertRaises(core.ChunkIntegrityError):
                core.verify_composed_samples(lens, bad)
        with self.assertRaises(core.ChunkIntegrityError):
            core.verify_composed_samples(lens[:-1], total)
        with self.assertRaises(core.ChunkIntegrityError):
            core.verify_composed_samples(lens + [lens[0]], total)

    def test_gained_parent_uses_p9a_gain_per_chunk_and_report(self):
        p9a = self.p9a
        mono, rep = core.compose_gained_parent(self.chunks, 0.09, gain_fn=p9a.compute_gain_for_target_rms, rms_fn=p9a.rms, peak_fn=p9a.peak)
        self.assertEqual(len(rep["gains"]), 3)
        self.assertEqual(len(rep["boundary_offsets_s"]), 2)
        for c, g in zip(self.chunks, rep["gains"]):                          # 式の同一性(I2): p9a.compute_gain_for_target_rms と一致
            self.assertAlmostEqual(g, round(float(p9a.compute_gain_for_target_rms(c, 0.09)), 4), places=4)
        for p, cap in zip(rep["post_rms"], rep["peak_capped"]):
            self.assertFalse(cap)
            self.assertAlmostEqual(p, 0.09, delta=0.0006)
        self.assertEqual(len(mono), sum(len(c) for c in self.chunks) + 2 * 4800)
        self.assertEqual(rep["boundary_offsets_s"][0], [round(len(self.chunks[0]) / 24000, 4), round(len(self.chunks[0]) / 24000 + 0.2, 4)])

    def test_peak_cap_recorded(self):
        p9a = self.p9a
        loud = [np.concatenate([np.zeros(100), np.full(10, 0.99), np.full(2000, 0.001)])]
        mono, rep = core.compose_gained_parent(loud, 0.09, gain_fn=p9a.compute_gain_for_target_rms, rms_fn=p9a.rms, peak_fn=p9a.peak)
        self.assertLessEqual(float(np.max(np.abs(mono))), 0.95 + 1e-9)
        self.assertEqual(rep["peak_capped"], [True])

    def test_padding_lowers_rms_slightly_documented(self):
        # 0.2秒無音を含む親RMSは生chunk平均RMSより小さい(仕様として明記: 約−0.06dB@X実測)。式は変えない。
        p9a = self.p9a
        raw = core.compose_raw_pcm([(c * 32767).astype(np.int16) for c in self.chunks]).astype("float64") / 32768
        self.assertLess(p9a.rms(raw), p9a.rms(np.concatenate(self.chunks)))


def _status(entry, key, approvals):
    import er003_v1_n3_01_assemble as asm
    return asm._segment_gate_status(entry, key, approvals)


class TParentAggregate(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.nd = os.path.join(self.tmp, "narration")
        os.makedirs(self.nd)
        rng = np.random.default_rng(1)
        self.plan = core.plan_x_part("Alpha one two.\n\nBeta three four five.\n\nGamma six.", "full_story_part1")
        self.segments = {}
        for c in self.plan["chunks"]:
            core.write_pcm16(f"{self.nd}/{c['chunk_id']}.wav", (rng.normal(0, 0.05, 2400) * 32767).astype(np.int16))
            self.segments[c["chunk_id"]] = core.attach_chunk_meta({"segment_id": c["chunk_id"], "status": "OK", "canonical_text": c["text"]},
                                                                   "full_story_part1", c, 3)
        self.text = "Alpha one two.\n\nBeta three four five.\n\nGamma six."

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _refresh(self, approvals=None):
        return core.refresh_parent_status(self.plan, self.segments, approvals or {}, _status, narration_dir=self.nd, parent_text=self.text,
                                          display={"voice": "Aoede", "style": {"instruction_label": "x"}})

    def test_all_ok_parent_ok_and_wav_sha(self):
        e = self._refresh()
        self.assertEqual(e["status"], "OK")
        self.assertEqual(self.segments["full_story_part1"], e)
        self.assertEqual(e["sha256"], core.sha256_file(f"{self.nd}/full_story_part1.wav"))
        self.assertEqual(e["chunk_tts"]["chunk_ids"], core.chunk_ids(self.plan))
        self.assertEqual(e["voice"], "Aoede")
        core.verify_raw_parent(f"{self.nd}/full_story_part1.wav", [f"{self.nd}/{i}.wav" for i in core.chunk_ids(self.plan)])

    def test_chunk_stopped_parent_not_validated_and_parent_approval_cannot_bypass(self):
        self.segments["full_story_part1_k2"]["status"] = "STOPPED"
        e = self._refresh()
        self.assertEqual(e["status"], core.PARENT_STATUS_NOT_ALL_VALIDATED)
        self.assertEqual(_status(e, "full_story_part1", {}), "UNVALIDATED")
        # 親idへ(親本文で)人間承認を記録しても共有Gateを迂回できない
        appr = {"full_story_part1": {"canonical_text_sha256": hashlib.sha256(self.text.encode()).hexdigest()}}
        self.assertEqual(_status(e, "full_story_part1", appr), "UNVALIDATED")
        self.assertEqual(e["chunk_tts"]["chunk_gate_statuses"]["full_story_part1_k2"], "STOPPED")

    def test_missing_chunk_entry_is_unvalidated_and_parent_still_written(self):
        del self.segments["full_story_part1_k3"]
        e = self._refresh()                                   # M2(a): 失敗・未生成でも親は常に書く
        self.assertEqual(e["status"], core.PARENT_STATUS_NOT_ALL_VALIDATED)
        self.assertEqual(e["chunk_tts"]["chunk_gate_statuses"]["full_story_part1_k3"], "UNVALIDATED")
        self.assertIn("full_story_part1", self.segments)

    def test_human_approved_chunk_makes_parent_ok_and_is_recorded(self):
        self.segments["full_story_part1_k2"]["status"] = "STOPPED"
        k2 = self.plan["chunks"][1]
        appr = {"full_story_part1_k2": {"canonical_text_sha256": hashlib.sha256(k2["text"].encode()).hexdigest()}}
        e = self._refresh(appr)
        self.assertEqual(e["status"], "OK")
        self.assertEqual(e["chunk_tts"]["human_approved_chunks"], ["full_story_part1_k2"])
        # 承認が別のtextのshaなら通らない
        bad = {"full_story_part1_k2": {"canonical_text_sha256": "0" * 64}}
        self.assertEqual(self._refresh(bad)["status"], core.PARENT_STATUS_NOT_ALL_VALIDATED)

    def test_refresh_rebuilds_stale_or_missing_parent_wav(self):
        e1 = self._refresh()
        p = f"{self.nd}/full_story_part1.wav"
        os.remove(p)                                           # 親wavが無い(承認後の再gateで必要)
        e2 = self._refresh()
        self.assertEqual(e2["sha256"], e1["sha256"])
        core.write_pcm16(f"{self.nd}/full_story_part1_k1.wav", core.read_pcm16(f"{self.nd}/full_story_part1_k1.wav")[:-100])   # chunkが更新→親は古い
        e3 = self._refresh()
        self.assertNotEqual(e3["sha256"], e1["sha256"])
        core.verify_raw_parent(p, [f"{self.nd}/{i}.wav" for i in core.chunk_ids(self.plan)])

    def test_partial_wavs_do_not_write_parent_and_sha_none(self):
        os.remove(f"{self.nd}/full_story_part1_k3.wav")
        os.remove(f"{self.nd}/full_story_part1.wav") if os.path.exists(f"{self.nd}/full_story_part1.wav") else None
        e = self._refresh()
        self.assertIsNone(e["sha256"])
        self.assertFalse(os.path.exists(f"{self.nd}/full_story_part1.wav"))

    def test_not_chunked_plan_is_noop(self):
        plan = core.plan_x_part("One paragraph only.", "full_story_part2")
        self.assertIsNone(core.refresh_parent_status(plan, {}, {}, _status, narration_dir=self.nd, parent_text="One paragraph only."))

    def test_deviation_chunks_listed(self):
        self.segments["full_story_part1_k1"]["audio_text_deviation"] = {"diff_summary": "x"}
        self.assertEqual(self._refresh()["chunk_tts"]["deviation_chunks"], ["full_story_part1_k1"])

    def test_idempotent(self):
        a = json.dumps(self._refresh(), sort_keys=True)
        b = json.dumps(self._refresh(), sort_keys=True)
        self.assertEqual(a, b)

    def test_evidence_record_has_chunk_rows(self):
        ev = core.evidence_record(self.plan, self.segments, {"gains": [1]})
        self.assertEqual(ev["chunk_count"], 3)
        self.assertEqual([r["chunk_id"] for r in ev["chunks"]], core.chunk_ids(self.plan))


class TIntegrity(unittest.TestCase):
    def _plan(self):
        paras = [("Alpha beta gamma delta. " * 11).strip(), ("Eps zeta eta theta. " * 11).strip(), ("Iota kappa lambda mu. " * 11).strip()]
        c = _clip(" ".join(paras))
        return core.plan_z_clip(c, paras), c["text"]

    def _entries(self, plan):
        return [{"segment_id": ch["chunk_id"], "canonical_text": ch["text"], "chunk_tts": {"planner_version": core.CHUNK_PLANNER_VERSION}}
                for ch in plan["chunks"]]

    def _parent(self, plan):
        return {"chunk_tts": {"chunk_ids": core.chunk_ids(plan), "words": [c["words"] for c in plan["chunks"]],
                              "planner_version": core.CHUNK_PLANNER_VERSION}}

    def test_ok(self):
        p, t = self._plan()
        self.assertTrue(core.verify_parent_integrity(p, t, self._entries(p), self._parent(p))["ok"])

    def test_missing_extra_order_text_version(self):
        p, t = self._plan()
        with self.assertRaises(core.ChunkIntegrityError):
            core.verify_parent_integrity(p, t, self._entries(p)[:-1], self._parent(p))
        e = self._entries(p)
        e.append(dict(e[0], segment_id="full_story_part1_c1_k9"))
        with self.assertRaises(core.ChunkIntegrityError):
            core.verify_parent_integrity(p, t, e, self._parent(p))
        par = self._parent(p)
        par["chunk_tts"]["chunk_ids"] = list(reversed(par["chunk_tts"]["chunk_ids"]))
        with self.assertRaises(core.ChunkIntegrityError):
            core.verify_parent_integrity(p, t, self._entries(p), par)
        e = self._entries(p)
        e[0]["canonical_text"] += " extra"
        with self.assertRaises(core.ChunkIntegrityError):
            core.verify_parent_integrity(p, t, e, self._parent(p))
        e = self._entries(p)
        e[1]["chunk_tts"]["planner_version"] = "chunk_tts_v0"
        with self.assertRaises(core.ChunkIntegrityError):
            core.verify_parent_integrity(p, t, e, self._parent(p))
        par = self._parent(p)
        par["chunk_tts"]["planner_version"] = "chunk_tts_v0"
        with self.assertRaises(core.ChunkIntegrityError):
            core.verify_parent_integrity(p, t, self._entries(p), par)

    def test_parent_marked_chunked_but_plan_not_chunked(self):
        with self.assertRaises(core.ChunkIntegrityError):
            core.verify_parent_integrity({"chunked": False, "chunks": []}, "x", [], {"chunk_tts": {"chunk_ids": ["a"]}})
        self.assertFalse(core.verify_parent_integrity({"chunked": False, "chunks": []}, "x", [], None)["chunked"])


class TReuseAndResume(unittest.TestCase):
    def test_chunk_reuse_key_fields(self):
        a = core.chunk_reuse_key_fields("p", {"index": 1}, 2)
        b = core.chunk_reuse_key_fields("p", {"index": 2}, 2)
        self.assertNotEqual(a, b)
        self.assertEqual(a["chunk_tts"]["planner_version"], core.CHUNK_PLANNER_VERSION)
        self.assertEqual(a["chunk_tts"]["extra_pause_s"], 0.2)

    def test_I1_stale_planner_version_chunks_dropped_but_non_chunks_kept(self):
        cached = {"segments": {
            "full_story_part1_k1": {"status": "OK", "chunk_tts": {"planner_version": core.CHUNK_PLANNER_VERSION}},
            "full_story_part1_k2": {"status": "OK", "chunk_tts": {"planner_version": "old"}},
            "full_story_part1_k3": {"status": "OK"},
            "full_story_part2_c1_k1": {"status": "OK", "chunk_tts": {"planner_version": "old"}},
            "full_story_part1": {"status": "OK"}, "preview": {"status": "OK"}}, "style_version": "v"}
        out = core.drop_stale_chunk_entries(cached)
        self.assertEqual(sorted(out["segments"]), ["full_story_part1", "full_story_part1_k1", "preview"])
        self.assertEqual(out["style_version"], "v")
        self.assertEqual(sorted(cached["segments"]), sorted(cached["segments"]))      # 元は変更しない
        self.assertEqual(len(cached["segments"]), 6)
        self.assertIsNone(core.drop_stale_chunk_entries(None))
        same = {"segments": {"preview": {}}}
        self.assertIs(core.drop_stale_chunk_entries(same), same)

    def test_same_inputs_same_plan_after_resume(self):
        paras = [("Alpha beta gamma delta. " * 14).strip() for _ in range(3)]
        c = _clip(" ".join(paras))
        self.assertEqual(core.plan_z_clip(c, paras), core.plan_z_clip(dict(c), list(paras)))

    def test_text_change_changes_chunk_text_sha(self):
        paras = [("Alpha beta gamma delta. " * 14).strip() for _ in range(3)]
        base = core.plan_z_clip(_clip(" ".join(paras)), paras)
        paras2 = [paras[0] + " Added sentence here today.", paras[1], paras[2]]
        new = core.plan_z_clip(_clip(" ".join(paras2)), paras2)
        self.assertNotEqual([core.sha256_text(x["text"]) for x in base["chunks"]], [core.sha256_text(x["text"]) for x in new["chunks"]])

    def test_reconcile_saved_plan_stops_on_same_text_different_split_only(self):
        tmp = tempfile.mkdtemp()
        try:
            path = os.path.join(tmp, "audit", "chunk_plan_b1b.json")
            paras = [("Alpha beta gamma delta. " * 14).strip() for _ in range(3)]
            p1 = core.plan_z_clip(_clip(" ".join(paras)), paras)
            core.reconcile_saved_plan(path, {"full_story_part1_c1": p1})
            core.reconcile_saved_plan(path, {"full_story_part1_c1": p1})                        # 同一→OK
            tampered = json.loads(json.dumps(p1))
            tampered["chunks"][0]["text"] += " zzz"
            with self.assertRaises(core.ChunkIntegrityError):
                core.reconcile_saved_plan(path, {"full_story_part1_c1": tampered})              # 同一本文sha・同一版で分割が違う
            other = dict(tampered, parent_text_sha256="deadbeef")
            core.reconcile_saved_plan(path, {"full_story_part1_c1": other})                      # 本文が変われば再計画OK
            ver = dict(p1, planner_version="chunk_tts_v0")
            core.reconcile_saved_plan(path, {"full_story_part1_c1": ver})                        # 版が変われば再計画OK
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class TLegacyCompat(unittest.TestCase):
    """本方式導入前に生成された結果(親entryのみ)は従来経路のまま扱う(gate/assemble/pagesの再実行を壊さない)。"""

    def test_legacy_detection_and_effective_plan(self):
        plan = core.plan_x_part("A a.\n\nB b.", "full_story_part1")
        legacy = {"full_story_part1": {"status": "OK"}}
        self.assertTrue(core.is_legacy_unchunked(plan, legacy))
        eff = core.effective_plan(plan, legacy)
        self.assertFalse(eff["chunked"])
        self.assertTrue(eff["legacy_unchunked"])
        self.assertFalse(core.is_legacy_unchunked(plan, {}))                                              # 親も無い=未生成(legacyではない)
        self.assertFalse(core.is_legacy_unchunked(plan, {"full_story_part1": {"status": "OK", "chunk_tts": {}}}))
        self.assertFalse(core.is_legacy_unchunked(plan, dict(legacy, full_story_part1_k1={"status": "OK"})))   # chunk entryが1件でもあれば新方式
        self.assertIs(core.effective_plan(plan, {}), plan)

    def test_integrity_accepts_dict_form_entries(self):
        paras = [("Alpha beta gamma delta. " * 11).strip(), ("Eps zeta eta theta. " * 11).strip(), ("Iota kappa lambda mu. " * 11).strip()]
        c = _clip(" ".join(paras))
        p = core.plan_z_clip(c, paras)
        ents = {ch["chunk_id"]: {"canonical_text": ch["text"], "chunk_tts": {"planner_version": core.CHUNK_PLANNER_VERSION}} for ch in p["chunks"]}
        self.assertTrue(core.verify_parent_integrity(p, c["text"], ents, None)["ok"])


if __name__ == "__main__":
    unittest.main()
