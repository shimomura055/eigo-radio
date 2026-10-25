# -*- coding: utf-8 -*-
"""FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01 委任_02: Family X(Advanced本文=段落単位chunk+0.2秒)配線のtest(API 0・TTS 0。TTS関数はmock)。
実行: .venv/Scripts/python.exe -m pytest er117_x_chunk_wiring_test_01.py -q  (repo root)"""
import hashlib
import json
import os
import shutil
import tempfile
import unittest
from unittest import mock

import numpy as np

import er003_v1_n3_01_assemble as asm
import er019_family_x_audio_production_runner_01 as runner
import er019_family_x_style_profile_01 as sp
import er117_chunk_tts_production_01 as core

FL = "speech_metadata_flash_lite"
P1 = "Para one is short here.\n\nPara two has some more words in it.\n\nPara three ends the first part."
P2 = "Only one paragraph in the second part, so it is not split at all."
P3 = "Third part first paragraph here.\n\nThird part second paragraph here."
PARTS = {"title": "Sample Title", "title_tts": "Sample Title", "part1": P1, "part2": P2, "part3": P3, "in_one_line": "One line."}
SUPPORT = {"preview": "Preview text.", "comment_1": "Comment one.", "comment_2": "Comment two.", "comment_3": "Comment three.",
           "comment_4": "Comment four."}


def _wav(path, seed, n=2400):
    rng = np.random.default_rng(seed)
    core.write_pcm16(path, (rng.normal(0, 0.05, n) * 32767).astype(np.int16))


def _make_theme(tmp, parts=None):
    d = os.path.join(tmp, "b1b")
    os.makedirs(os.path.join(d, "narration"), exist_ok=True)
    json.dump(parts or PARTS, open(os.path.join(d, "parts.json"), "w", encoding="utf-8"), ensure_ascii=False)
    json.dump(SUPPORT, open(os.path.join(d, "b1_support_texts.json"), "w", encoding="utf-8"))
    return d


class Rig:
    """generate_family_x_b1_segments をmockで回す。wide(news_tail_fix)の呼出を記録し、失敗chunkを指定できる。"""

    def __init__(self, fail=None, minimal_fallback=()):
        self.calls, self.fail, self.minimal_fallback = [], set(fail or ()), set(minimal_fallback)

    def wide(self, text, out, **k):
        name = os.path.basename(out)[:-4]
        self.calls.append({"name": name, "text": text, "kw": k})
        _wav(out, abs(hash(name)) % 1000)
        status = "STOPPED" if name in self.fail else "OK"
        return {"status": status, "text": text, "path": out, "asr_verified": status == "OK", "voice": "Aoede",
                "tts_model_id": "m", "model": "m", "tts_backend": k.get("tts_backend"), "style_prefix": k.get("style_prefix_override") or "",
                "instruction_type": "minimal_fallback" if name in self.minimal_fallback else "english_style_prefix_wide_margin",
                "sha256": hashlib.sha256(open(out, "rb").read()).hexdigest(), "disfluency_checked": True}

    def charon(self, text, out, **k):
        self.calls.append({"name": os.path.basename(out)[:-4], "text": text, "kw": k})
        _wav(out, 7)
        return {"status": "OK", "canonical_text": text, "disfluency_checked": True, "text": text}

    def run(self, tmp, **kw):
        with mock.patch.object(runner.shared_narration, "ensure_all_shared_narration_b1", return_value={}), \
             mock.patch.object(runner.voice01, "generate_charon_english", side_effect=self.charon), \
             mock.patch.object(runner.news_tail_fix, "generate_news_narration_wide_margin", side_effect=self.wide):
            return runner.generate_family_x_b1_segments(tmp, tts_backend=FL, **kw)

    def names(self):
        return [c["name"] for c in self.calls]


def _results(tmp):
    return json.load(open(f"{tmp}/b1b/audit/tts_generation_results.json", encoding="utf-8"))


class XGenerateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="xchunk_")
        _make_theme(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_body_parts_generate_per_chunk_with_same_kwargs_and_single_paragraph_unchanged(self):
        r = Rig()
        r.run(self.tmp)
        names = [n for n in r.names() if n.startswith("full_story") or n == "in_one_line"]
        self.assertEqual(names, ["full_story_part1_k1", "full_story_part1_k2", "full_story_part1_k3", "full_story_part2",
                                 "full_story_part3_k1", "full_story_part3_k2", "in_one_line"])          # 直列(chunk順)。1段落partは従来の1 call
        by = {c["name"]: c for c in r.calls}
        ref = by["full_story_part2"]["kw"]                                                             # 従来経路(1段落part)のkwargs
        for n in ("full_story_part1_k1", "full_story_part1_k3", "full_story_part3_k2"):
            kw = by[n]["kw"]
            self.assertEqual(kw["enable_repetition_qa"], ref["enable_repetition_qa"])
            self.assertEqual(kw["style_prefix_override"], ref["style_prefix_override"])
            self.assertEqual(kw["tts_backend"], ref["tts_backend"])
            self.assertEqual(kw["enable_pronunciation_resolver"], ref["enable_pronunciation_resolver"])
            self.assertEqual(kw["enable_connected_speech_equivalence_layer"], True)                    # chunk idもFULL_STORYのCS層対象(C4)
            self.assertEqual(kw["disfluency_qa"], False)
        self.assertEqual(by["full_story_part1_k2"]["text"], runner.n3_tts.tts_safe_news_en("Para two has some more words in it."))   # TTS入力整形はchunk本文だけに掛かる
        self.assertEqual(by["in_one_line"]["kw"]["enable_repetition_qa"], False)

    def test_results_have_chunk_entries_parent_aggregate_and_exact_parent_wav(self):
        Rig().run(self.tmp)
        res = _results(self.tmp)
        seg = res["segments"]
        for cid in ("full_story_part1_k1", "full_story_part1_k2", "full_story_part1_k3", "full_story_part3_k1", "full_story_part3_k2"):
            self.assertEqual(seg[cid]["status"], "OK")
            self.assertEqual(seg[cid]["chunk_tts"]["planner_version"], core.CHUNK_PLANNER_VERSION)
            self.assertEqual(seg[cid]["style_profile"] if "style_profile" in seg[cid] else None, None)   # default profileは記録なし
        self.assertEqual(seg["full_story_part1"]["status"], "OK")
        self.assertEqual(seg["full_story_part1"]["chunk_tts"]["chunk_ids"], ["full_story_part1_k1", "full_story_part1_k2", "full_story_part1_k3"])
        nd = f"{self.tmp}/b1b/narration"
        core.verify_raw_parent(f"{nd}/full_story_part1.wav", [f"{nd}/full_story_part1_k{i}.wav" for i in (1, 2, 3)])
        self.assertEqual(seg["full_story_part1"]["sha256"], core.sha256_file(f"{nd}/full_story_part1.wav"))
        self.assertNotIn("chunk_tts", seg["full_story_part2"])                                         # 1段落part=従来entry
        self.assertEqual(seg["full_story_part2"]["canonical_text"], P2)
        self.assertEqual(seg["full_story_part1"]["voice"], "Aoede")                                    # I7
        self.assertTrue(os.path.exists(f"{self.tmp}/b1b/audit/chunk_plan_b1b.json"))
        ev = json.load(open(f"{self.tmp}/b1b/audit/chunk_tts_evidence_b1b.json", encoding="utf-8"))
        self.assertEqual(sorted(ev["parents"]), ["full_story_part1", "full_story_part3"])
        self.assertEqual(ev["parents"]["full_story_part1"]["chunk_count"], 3)
        # 共有Gateが親+chunkを全て通す
        asm.verify_episode_audio_validation_gate(f"{self.tmp}/b1b", "B1")

    def test_chunk_failure_does_not_stop_later_chunks_and_parent_is_written_not_validated(self):
        r = Rig(fail={"full_story_part1_k2"})
        r.run(self.tmp)
        self.assertIn("full_story_part1_k3", r.names())                                                # R1: 失敗後も後続chunkを生成
        seg = _results(self.tmp)["segments"]
        self.assertEqual(seg["full_story_part1_k2"]["status"], "STOPPED")
        self.assertEqual(seg["full_story_part1"]["status"], core.PARENT_STATUS_NOT_ALL_VALIDATED)      # M2(a): 失敗時も親を書く
        with self.assertRaises(RuntimeError) as cm:
            asm.verify_episode_audio_validation_gate(f"{self.tmp}/b1b", "B1")
        self.assertIn("full_story_part1_k2=STOPPED", str(cm.exception))
        self.assertIn("full_story_part1=UNVALIDATED", str(cm.exception))

    def test_resume_reuses_ok_chunks_and_regenerates_only_failed(self):
        Rig(fail={"full_story_part1_k2"}).run(self.tmp)
        r2 = Rig()
        r2.run(self.tmp)
        gen = [n for n in r2.names() if n.startswith("full_story")]
        self.assertIn("full_story_part1_k2", gen)
        self.assertNotIn("full_story_part1_k1", gen)
        self.assertNotIn("full_story_part1_k3", gen)
        self.assertNotIn("full_story_part3_k1", gen)
        self.assertEqual(_results(self.tmp)["segments"]["full_story_part1"]["status"], "OK")

    def test_I1_old_planner_version_chunk_is_not_reused(self):
        Rig().run(self.tmp)
        p = f"{self.tmp}/b1b/audit/tts_generation_results.json"
        d = json.load(open(p, encoding="utf-8"))
        d["segments"]["full_story_part1_k2"]["chunk_tts"]["planner_version"] = "chunk_tts_v0"
        json.dump(d, open(p, "w", encoding="utf-8"))
        r2 = Rig()
        r2.run(self.tmp)
        gen = [n for n in r2.names() if n.startswith("full_story_part1")]
        self.assertEqual(gen, ["full_story_part1_k2"])                                                 # 版が違うchunkだけ再生成

    def test_text_change_regenerates_only_changed_chunk(self):
        Rig().run(self.tmp)
        parts = dict(PARTS, part1=P1.replace("Para two has some more words in it.", "Para two was edited a little."))
        _make_theme(self.tmp, parts)
        r2 = Rig()
        r2.run(self.tmp)
        self.assertEqual([n for n in r2.names() if n.startswith("full_story_part1")], ["full_story_part1_k2"])

    def test_old_unchunked_cache_entry_is_not_reused_for_chunked_part(self):
        # 本方式導入前のresults(full_story_part1が単独entry)を引き継いだout_dir: 旧part音声は再利用されず、chunkが新規生成される
        d = _make_theme(self.tmp)
        nd = f"{d}/narration"
        _wav(f"{nd}/full_story_part1.wav", 3)
        os.makedirs(f"{d}/audit")
        json.dump({"segments": {"full_story_part1": {"status": "OK", "canonical_text": P1, "path": f"{nd}/full_story_part1.wav",
                                                       "sha256": core.sha256_file(f"{nd}/full_story_part1.wav"), "asr_verified": True}},
                   "style_version": runner.FAMILY_X_VARIABLE_ROLE_STYLE_VERSION}, open(f"{d}/audit/tts_generation_results.json", "w"))
        r = Rig()
        r.run(self.tmp)
        self.assertEqual([n for n in r.names() if n.startswith("full_story_part1")],
                         ["full_story_part1_k1", "full_story_part1_k2", "full_story_part1_k3"])
        self.assertTrue(_results(self.tmp)["segments"]["full_story_part1"]["chunk_tts"])               # 親は新方式の集約entryに置換

    def test_resume_replan_prohibition_stops_before_any_call(self):
        Rig().run(self.tmp)
        p = f"{self.tmp}/b1b/audit/chunk_plan_b1b.json"
        d = json.load(open(p, encoding="utf-8"))
        d["plans"]["full_story_part1"]["chunks"][0]["text"] += " tampered"
        json.dump(d, open(p, "w", encoding="utf-8"))
        r = Rig()
        with self.assertRaises(core.ChunkIntegrityError):
            r.run(self.tmp)
        self.assertEqual(r.calls, [])                                                                  # 課金前にSTOP

    def test_std_a2_path_untouched_no_chunk_ids(self):
        # a2(Std)本文はchunk化しない: a2関数のソースにchunk経路が入っていない
        import inspect
        src = inspect.getsource(runner.generate_family_x_a2_segments)
        self.assertNotIn("chunk_tts", src)
        self.assertNotIn("_generate_x_body_part_chunked", src)
        self.assertNotIn("chunk_tts", inspect.getsource(runner.apply_family_x_a2_gain))
        self.assertNotIn("chunk_tts", inspect.getsource(runner.load_family_x_a2_sources))
        self.assertNotIn("chunk_tts", inspect.getsource(runner.stage_assemble_family_x_a2))


class XOnlySegmentsTests(unittest.TestCase):
    def test_validate_only_segments_chunk_forms(self):
        v = runner.validate_only_segments_args
        sel, err = v("tts", False, "b1b", "full_story_part2,full_story_part1_k2")
        self.assertIsNone(err)
        self.assertEqual(sel, {"full_story_part2", "full_story_part1_k2"})
        _, err = v("tts", False, "a2", "full_story_part1_k1")                                          # I5: Stdは_k指定を拒否
        self.assertIn("_k", err)
        _, err = v("tts", False, "a2", "full_story_part1")                                             # 親名はa2でも従来どおり可
        self.assertIsNone(err)
        for bad in ("full_story_part1_k", "full_story_part1_k0", "full_story_part1_c1_k1", "comment_1_k1", "in_one_line_k1"):
            _, err = v("tts", False, "b1b", bad)
            self.assertIsNotNone(err, bad)

    def test_parent_name_selects_all_its_chunks_and_k_selects_only_that_chunk(self):
        tmp = tempfile.mkdtemp(prefix="xchunk_only_")
        try:
            _make_theme(tmp)
            Rig().run(tmp)
            old = runner._ONLY_SEGMENTS
            try:
                runner._ONLY_SEGMENTS = {"full_story_part1_k2"}
                r = Rig()
                r.run(tmp)
                gen = [n for n in r.names() if n.startswith("full_story")]
                self.assertEqual(gen, [])                                                              # 全て検証済みentryを引き継ぎ(非選択)・k2は再利用
                runner._ONLY_SEGMENTS = {"full_story_part3"}
                self.assertTrue(runner._chunk_parent_selected("full_story_part3_k2"))
                self.assertFalse(runner._chunk_parent_selected("full_story_part1_k2"))
                self.assertIsNone(runner._only_segments_skip("full_story_part3_k1"))
                self.assertEqual(runner._only_segments_skip("full_story_part1_k1")["status"], "SKIPPED_NOT_SELECTED")
            finally:
                runner._ONLY_SEGMENTS = old
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class XStyleProfileGateTests(unittest.TestCase):
    """M1(Opus条件A最重要): Style profile M3 Gateはchunk entryを検査する(親は対象外)。"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="xchunk_m3_")
        _make_theme(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _gen(self, **rigkw):
        r = Rig(**rigkw)
        r.run(self.tmp, style_profile="coffee_p8")
        return _results(self.tmp)

    def test_pass_checks_chunk_ids_not_parent(self):
        res = self._gen()
        gate = sp.m3_assembly_gate("coffee_p8", "b1b", res, {})
        self.assertEqual(gate["status"], "PASS", gate)
        for cid in ("full_story_part1_k1", "full_story_part1_k2", "full_story_part1_k3", "full_story_part3_k1", "full_story_part3_k2", "full_story_part2"):
            self.assertIn(cid, gate["checked"])
        self.assertNotIn("full_story_part1", gate["checked"])                                         # 親は対象外
        self.assertNotIn("full_story_part3", gate["checked"])
        for cid in ("full_story_part1_k2",):
            self.assertIn("style_profile", res["segments"][cid])                                      # chunkごとにprofile記録
        self.assertNotIn("style_profile", res["segments"]["full_story_part1"])                        # 親へはコピーしない

    def test_only_k2_minimal_fallback_blocks_even_if_other_chunks_ok(self):
        res = self._gen(minimal_fallback={"full_story_part1_k2"})
        gate = sp.m3_assembly_gate("coffee_p8", "b1b", res, {})
        self.assertEqual(gate["status"], "BLOCK")
        self.assertEqual([b["segment"] for b in gate["blocked"]], ["full_story_part1_k2"])
        self.assertIn("ADV_MINIMAL_FALLBACK", gate["blocked"][0]["violations"])
        # 人間承認(chunk id・chunk本文sha)があれば通る / 親idへの承認では通らない
        ctext = res["segments"]["full_story_part1_k2"]["canonical_text"]
        ok = {"full_story_part1_k2": {"canonical_text_sha256": hashlib.sha256(ctext.encode()).hexdigest()}}
        self.assertEqual(sp.m3_assembly_gate("coffee_p8", "b1b", res, ok)["status"], "PASS")
        parent_only = {"full_story_part1": {"canonical_text_sha256": hashlib.sha256(P1.encode()).hexdigest()}}
        self.assertEqual(sp.m3_assembly_gate("coffee_p8", "b1b", res, parent_only)["status"], "BLOCK")

    def test_missing_chunk_entry_blocks_and_copying_chunk1_to_parent_does_not_help(self):
        res = self._gen()
        del res["segments"]["full_story_part1_k3"]
        res["segments"]["full_story_part1"]["style_profile"] = dict(res["segments"]["full_story_part1_k1"]["style_profile"])
        res["segments"]["full_story_part1"]["style_prefix"] = res["segments"]["full_story_part1_k1"]["style_prefix"]
        gate = sp.m3_assembly_gate("coffee_p8", "b1b", res, {})
        self.assertEqual(gate["status"], "BLOCK")
        self.assertEqual([b["segment"] for b in gate["blocked"]], ["full_story_part1_k3"])
        self.assertIn("NO_SEGMENT_RECORD", gate["blocked"][0]["violations"])

    def test_legacy_unchunked_parent_still_checked_as_before(self):
        res = {"segments": {"full_story_part1": {"status": "OK", "canonical_text": "x"}}}
        gate = sp.m3_assembly_gate("coffee_p8", "b1b", res, {})
        self.assertIn("full_story_part1", gate["checked"])
        self.assertNotIn("full_story_part1_k1", gate["checked"])


class XGainAndAssemblyTests(unittest.TestCase):
    def _sources(self):
        rng = np.random.default_rng(5)
        mono = lambda a, n=24000: rng.normal(0, a, n)
        chunks = [mono(0.05, 24000), mono(0.09, 30000), mono(0.03, 12000)]
        raw = core.compose_raw_pcm([(c * 32767).astype(np.int16) for c in chunks]).astype("float64") / 32768
        st = lambda n=48000: rng.normal(0, 0.05, (n, 2))
        return {
            "intro": {"samples": st()}, "notification": {"samples": st()}, "outro": {"samples": st()},
            "narration": {"welcome": mono(0.05), "topic_intro": mono(0.05)},
            "b1_segments": {"preview": mono(0.05), "full_story_part1": raw, "full_story_part2": mono(0.05, 20000), "comment_1": mono(0.05),
                            "in_one_line": mono(0.05)},
            "key_phrase_components": {}, "key_phrase_meanings": {}, "kp_items": [],
            "body_chunks": {"full_story_part1": chunks},
            "chunk_plans": {}}, chunks

    def test_apply_gain_composes_chunks_with_per_chunk_gain_and_pad_and_leaves_others(self):
        src, chunks = self._sources()
        out = runner.apply_family_x_b1_gain(src)
        gr = out["gain_report"]
        rep = gr["chunk_tts"]["full_story_part1"]
        self.assertEqual(len(rep["gains"]), 3)
        self.assertEqual(gr["b1_full_story_part1"]["chunked"], True)
        self.assertNotIn("gain", gr["b1_full_story_part1"])                                           # I7: 親keyに掛けていないgainを書かない
        self.assertIn("gain", gr["b1_full_story_part2"])                                              # 非chunk partは従来のまま
        st = out["b1_segments"]["full_story_part1"]
        self.assertEqual(st.shape[1], 2)
        self.assertEqual(st.shape[0], 2 * (sum(len(c) for c in chunks) + 2 * 4800))                    # 24k→48k=2倍、0.2秒×2含む
        # 同じtarget_rmsへ揃っている(peak cap未発動なら)
        for p, cap in zip(rep["post_rms"], rep["peak_capped"]):
            self.assertTrue(cap or abs(p - gr["target_rms"]) < 0.0006)

    def test_apply_gain_without_chunks_is_byte_identical_to_legacy_formula(self):
        src, _ = self._sources()
        src["body_chunks"] = {}
        out = runner.apply_family_x_b1_gain(src)
        import er003_b1_p9a_audio as p9a
        mono = src["b1_segments"]["full_story_part2"]
        tgt = (p9a.rms(src["b1_segments"]["preview"]) + p9a.rms(src["b1_segments"]["full_story_part1"])) / 2     # 式は無変更
        want = p9a.mono_24k_to_stereo_target(mono * p9a.compute_gain_for_target_rms(mono, tgt))
        self.assertTrue(np.array_equal(out["b1_segments"]["full_story_part2"], want))
        self.assertNotIn("chunk_tts", out["gain_report"])

    def test_assembly_summary_records_absolute_gap_offsets(self):
        plans = {"full_story_part1": core.plan_x_part(P1, "full_story_part1")}
        rep = {"full_story_part1": {"boundary_offsets_s": [[1.0, 1.2], [3.0, 3.2]], "gains": [1, 1, 1], "pre_rms": [], "post_rms": [],
                                    "peak_after": [], "peak_capped": [False] * 3, "chunk_samples": []}}
        tl = [{"part": "Intro", "start_seconds": 0.0}, {"part": "Full Story Part 1 (Aoede)", "start_seconds": 10.0}]
        s = runner._chunk_assembly_summary_x(plans, rep, tl)
        self.assertEqual(s["parents"]["full_story_part1"]["gap_offsets_in_episode_s"], [[11.0, 11.2], [13.0, 13.2]])
        self.assertEqual(s["extra_pause_seconds"], 0.2)


class XRefreshAndLegacyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="xchunk_ref_")
        _make_theme(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_human_approval_then_refresh_makes_parent_ok_and_records_it(self):
        Rig(fail={"full_story_part1_k2"}).run(self.tmp)
        out_dir = f"{self.tmp}/b1b"
        res = _results(self.tmp)
        k2 = res["segments"]["full_story_part1_k2"]["canonical_text"]
        asm.record_human_approval(out_dir, "full_story_part1_k2", k2)
        os.remove(f"{out_dir}/narration/full_story_part1.wav")                                         # 承認後に親wavが無い状態
        runner._chunk_parent_refresh_x(out_dir)                                                       # assembleの入口(M2(c))
        seg = _results(self.tmp)["segments"]
        self.assertEqual(seg["full_story_part1"]["status"], "OK")
        self.assertEqual(seg["full_story_part1"]["chunk_tts"]["human_approved_chunks"], ["full_story_part1_k2"])
        self.assertTrue(os.path.exists(f"{out_dir}/narration/full_story_part1.wav"))
        asm.verify_episode_audio_validation_gate(out_dir, "B1")

    def test_legacy_results_keep_legacy_path(self):
        d = _make_theme(self.tmp)
        nd = f"{d}/narration"
        os.makedirs(f"{d}/audit", exist_ok=True)
        _wav(f"{nd}/full_story_part1.wav", 3)
        json.dump({"segments": {f"full_story_part{i}": {"status": "OK", "canonical_text": PARTS[f"part{i}"]} for i in (1, 2, 3)}},
                  open(f"{d}/audit/tts_generation_results.json", "w"))
        plans = runner._x_effective_chunk_plans(d, PARTS)
        self.assertFalse(plans["full_story_part1"]["chunked"])
        self.assertTrue(plans["full_story_part1"]["legacy_unchunked"])
        before = open(f"{d}/audit/tts_generation_results.json", "rb").read()
        runner._chunk_parent_refresh_x(d)                                                              # legacy結果ではファイルに触れない
        self.assertEqual(open(f"{d}/audit/tts_generation_results.json", "rb").read(), before)

    def test_integrity_stops_before_audio_when_parent_wav_not_raw_concat(self):
        Rig().run(self.tmp)
        out_dir = f"{self.tmp}/b1b"
        nd = f"{out_dir}/narration"
        core.write_pcm16(f"{nd}/full_story_part1.wav", core.read_pcm16(f"{nd}/full_story_part1.wav")[:-50])
        plans = runner._x_effective_chunk_plans(out_dir, PARTS)
        segs = _results(self.tmp)["segments"]
        ids = core.chunk_ids(plans["full_story_part1"])
        core.verify_parent_integrity(plans["full_story_part1"], P1, {i: segs[i] for i in ids}, segs["full_story_part1"])   # 構造は整合
        with self.assertRaises(core.ChunkIntegrityError):
            core.verify_raw_parent(f"{nd}/full_story_part1.wav", [f"{nd}/{i}.wav" for i in ids])                       # 親wavだけ古い→検知


class XImportGuardTests(unittest.TestCase):
    def test_import_time_self_check_present_for_chunk_ids(self):
        src = open("er019_family_x_audio_production_runner_01.py", encoding="utf-8").read()
        self.assertIn('"full_story_part1_k1"', src)
        self.assertIn("er020のchunk ID正規表現が外れています", src)


if __name__ == "__main__":
    unittest.main()


class XFullAssembleOfflineTests(unittest.TestCase):
    """generate(mock TTS)→assemble の通し(本物のGate・組立・headroom・summary。KP 0件、素材mp3は実ファイル)。"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="xchunk_asm_")
        self.d = _make_theme(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _prepare(self, **rigkw):
        Rig(**rigkw).run(self.tmp)
        nd = f"{self.d}/narration"
        for i, n in enumerate(("welcome", "preview_intro", "key_phrases_intro", "full_story_intro", "num_one", "num_two", "num_three",
                               "num_four", "num_five")):
            _wav(f"{nd}/{n}_charon.wav", 100 + i)
        os.makedirs(f"{self.d}/key_phrases", exist_ok=True)
        json.dump({"items": []}, open(f"{self.d}/key_phrases/keywords_canonicalized.json", "w"))

    def _assemble(self):
        with mock.patch.object(asm, "verify_key_phrase_source_gate"), \
             mock.patch.object(runner, "_assert_no_gloss_alignment_hr"), \
             mock.patch.object(runner, "_shared_narration_gate_blocked_summary", return_value=None), \
             mock.patch.object(asm, "build_b1_key_phrase_blocks", return_value=[]):
            return runner.stage_assemble_family_x_b1(self.tmp, "sample_theme")

    def test_assemble_ok_with_chunk_gain_gap_and_summary(self):
        self._prepare()
        s = self._assemble()
        self.assertEqual(s["status"], "OK", s)
        ct = s["chunk_tts"]["parents"]
        self.assertEqual(sorted(ct), ["full_story_part1", "full_story_part3"])
        self.assertEqual(len(ct["full_story_part1"]["gap_offsets_in_episode_s"]), 2)
        a, b = ct["full_story_part1"]["gap_offsets_in_episode_s"][0]
        self.assertAlmostEqual(b - a, 0.2, places=3)
        tl = json.load(open(f"{self.d}/audit/timeline.json", encoding="utf-8"))
        self.assertIn("Full Story Part 1 (Aoede)", [x["part"] for x in tl])                          # timelineは親1エントリ(ページ行不変)
        self.assertFalse(any("_k" in x["part"] for x in tl))
        gr = json.load(open(f"{self.d}/audit/gain_report.json", encoding="utf-8"))
        self.assertEqual(len(gr["chunk_tts"]["full_story_part1"]["gains"]), 3)

    def test_assemble_blocked_when_chunk_stopped_and_unblocked_after_human_approval(self):
        self._prepare(fail={"full_story_part1_k2"})
        with self.assertRaises(RuntimeError):
            self._assemble()
        k2 = _results(self.tmp)["segments"]["full_story_part1_k2"]["canonical_text"]
        asm.record_human_approval(self.d, "full_story_part1_k2", k2)
        os.remove(f"{self.d}/narration/full_story_part1.wav")
        s = self._assemble()                                                                          # M2(b)(c): 承認後に親wav・親entryが再構築されて通る
        self.assertEqual(s["status"], "OK", s)
        self.assertEqual(_results(self.tmp)["segments"]["full_story_part1"]["chunk_tts"]["human_approved_chunks"], ["full_story_part1_k2"])

    def test_stale_chunk_wav_blocked_by_shared_gate_and_stale_parent_wav_rebuilt(self):
        self._prepare()
        nd = f"{self.d}/narration"
        k1 = f"{nd}/full_story_part1_k1.wav"
        good = open(k1, "rb").read()
        core.write_pcm16(k1, core.read_pcm16(k1)[:-77])                                               # chunk wavだけ差し替わった→共有Gateのsha stale検知(chunk単位)
        with self.assertRaises(RuntimeError) as cm:
            self._assemble()
        self.assertIn("full_story_part1_k1=VALIDATED(ASSET_HASH_MISMATCH)", str(cm.exception))
        open(k1, "wb").write(good)
        p = f"{nd}/full_story_part1.wav"
        core.write_pcm16(p, core.read_pcm16(p)[:-123])                                                # 親wavが古い/壊れている→入口のrefreshが再合成してsha更新
        s = self._assemble()
        self.assertEqual(s["status"], "OK")
        core.verify_raw_parent(p, [f"{nd}/full_story_part1_k{i}.wav" for i in (1, 2, 3)])
