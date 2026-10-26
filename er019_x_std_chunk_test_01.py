# -*- coding: utf-8 -*-
"""CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01 委任_01: Family X Standard(a2)本文のChunk分割(+0.2秒)×6%減速のProduction配線test(API 0・TTS 0。TTS関数はmock)。
ユーザー正式承認2026-10-26(APPROVED_FOR_PRODUCTION: Std/Adv双方、Standard除外は認めない)。
実行: PYTHONPATH=netblock_harness_01 .venv/Scripts/python.exe -m pytest er019_x_std_chunk_test_01.py -q

検査: chunk別に既存の減速関数(generate_a2_segment_with_slowdown)を同一kwargsで呼ぶ / 1段落partは従来の1 call / 親集約entry(減速集約・親wav生連結) /
      共有Gate通過 / chunkの減速欠落・失敗はGateでブロック / resume(再課金なし・減速証跡なしcache拒否) / 再計画禁止 / chunk別gain+0.2秒の組立 / Adv(b1b)不変。
"""
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
import er117_chunk_tts_production_01 as core

FL = "speech_metadata_flash_lite"
P1 = "Para one is short here.\n\nPara two has some more words in it.\n\nPara three ends the first part."
P2 = "Only one paragraph in the second part, so it is not split at all."
P3 = "Third part first paragraph here.\n\nThird part second paragraph here."
PARTS = {"title": "Sample Title", "title_tts": "Sample Title", "part1": P1, "part2": P2, "part3": P3, "in_one_line": "One line."}
SUPPORT = {"preview": "予告です。", "comment_1": "コメント一。", "comment_2": "コメント二。", "comment_3": "コメント三。", "comment_4": "コメント四。"}


def _wav(path, seed, n):
    rng = np.random.default_rng(seed)
    core.write_pcm16(path, (rng.normal(0, 0.05, n) * 32767).astype(np.int16))


def _make_theme(tmp, parts=None):
    d = os.path.join(tmp, "a2")
    os.makedirs(os.path.join(d, "narration"), exist_ok=True)
    json.dump(parts or PARTS, open(os.path.join(d, "parts.json"), "w", encoding="utf-8"), ensure_ascii=False)
    json.dump(SUPPORT, open(os.path.join(d, "a2_support_texts.json"), "w", encoding="utf-8"), ensure_ascii=False)
    return d


def _results(tmp):
    return json.load(open(f"{tmp}/a2/audit/tts_generation_results.json", encoding="utf-8"))


class Rig:
    """generate_family_x_a2_segments をmockで回す。減速関数(generate_a2_segment_with_slowdown)の呼出を記録。
    fail=失敗chunk名 / no_slowdown=減速証跡を付けないchunk名(配線漏れの再現)。"""

    def __init__(self, fail=None, no_slowdown=()):
        self.calls, self.fail, self.no_slowdown = [], set(fail or ()), set(no_slowdown)

    def slow(self, tts_input, out, sub, **k):
        name = os.path.basename(out)[:-4]
        self.calls.append({"name": name, "text": tts_input, "sub": sub, "kw": k})
        n = 2400 + 100 * (abs(hash(name)) % 7)
        orig = out[:-4] + "_original.wav"
        _wav(orig, 3, n)
        _wav(out, 4, int(n * 1.06))
        ok = name not in self.fail
        e = {"status": "OK" if ok else "STOPPED", "text": tts_input, "path": out, "asr_verified": ok, "voice": "Aoede", "tts_model_id": "m",
             "model": "m", "tts_backend": k.get("tts_backend"), "style_prefix": k.get("style_prefix_override") or "", "fallback_used": False,
             "instruction_type": "english_style_prefix_wide_margin", "disfluency_checked": True,
             "sha256": hashlib.sha256(open(out, "rb").read()).hexdigest()}
        if name not in self.no_slowdown:
            e["slowdown_applied"] = True
            e["slowdown_info"] = {"slowdown_pct_target": 6.0, "slowdown_pct_actual": 6.0, "src_duration_seconds": n / 24000,
                                  "dst_duration_seconds": int(n * 1.06) / 24000}
        return e

    def fallback_en(self, text, out, sub, **k):
        self.calls.append({"name": os.path.basename(out)[:-4], "text": text, "kw": k})
        _wav(out, 5, 2400)
        return {"status": "OK", "text": text, "path": out, "asr_verified": True, "fallback_used": False, "disfluency_checked": True,
                "sha256": hashlib.sha256(open(out, "rb").read()).hexdigest()}

    def ja(self, text, out, sub, **k):
        self.calls.append({"name": os.path.basename(out)[:-4], "text": text, "kw": k})
        _wav(out, 6, 2400)
        return {"status": "OK", "text": text, "path": out, "asr_verified": True, "fallback_used": False, "disfluency_checked": True,
                "sha256": hashlib.sha256(open(out, "rb").read()).hexdigest()}

    def run(self, tmp, **kw):
        # PNAP(固有名詞アラーム)が他testの状態でONのまま残っていると、run_with_alarm_hookが実体表構築(OpenAI NER)を試みる。
        # 本testは外部接続0を保証するため、PNAPを明示的にOFFにして回す(Adv/Stdのchunk経路とは無関係)。
        with mock.patch.object(runner.pnap_hooks.pnap, "is_enabled", return_value=False), \
             mock.patch.object(runner.shared_narration, "ensure_all_shared_narration_a2", return_value={}), \
             mock.patch.object(runner.n3_tts, "generate_a2_segment_with_slowdown", side_effect=self.slow), \
             mock.patch.object(runner.crosslevel_common, "generate_english_segment_with_fallback", side_effect=self.fallback_en), \
             mock.patch.object(runner.n3_tts, "generate_a2_japanese_with_reading_safety", side_effect=self.ja):
            return runner.generate_family_x_a2_segments(tmp, "日本語タイトル", tts_backend=FL, **kw)

    def body_names(self):
        return [c["name"] for c in self.calls if c["name"].startswith("full_story") or c["name"] == "in_one_line"]


class XStdGenerateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="xstd_")
        _make_theme(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_each_chunk_goes_through_the_existing_slowdown_function_with_same_kwargs(self):
        r = Rig()
        r.run(self.tmp)
        self.assertEqual(r.body_names(), ["full_story_part1_k1", "full_story_part1_k2", "full_story_part1_k3", "full_story_part2",
                                          "full_story_part3_k1", "full_story_part3_k2", "in_one_line"])   # 直列(chunk順)。1段落partは従来の1 call
        by = {c["name"]: c for c in r.calls}
        ref = by["full_story_part2"]["kw"]                                                                # 従来経路(1段落part)のkwargs
        for n in ("full_story_part1_k1", "full_story_part1_k3", "full_story_part3_k2"):
            kw = by[n]["kw"]
            for key in ("style_prefix_override", "enable_repetition_qa", "tts_backend", "disfluency_qa"):
                self.assertEqual(kw[key], ref[key], (n, key))
            self.assertEqual(kw["enable_connected_speech_equivalence_layer"], True)                       # chunk idもFULL_STORYのCS層対象
        self.assertIn("slow", by["full_story_part1_k1"]["kw"]["style_prefix_override"].lower())            # 減速instruction込みのStd style(承認済み組合せ)
        self.assertEqual(by["full_story_part1_k2"]["sub"], runner.n3_tts.first_words("Para two has some more words in it."))   # 期待先頭語もchunk本文から
        self.assertEqual(by["in_one_line"]["kw"]["disfluency_qa"], True)

    def test_chunk_entries_carry_slowdown_and_std_meta_and_parent_aggregates_slowdown(self):
        Rig().run(self.tmp)
        seg = _results(self.tmp)["segments"]
        for cid in ("full_story_part1_k1", "full_story_part1_k2", "full_story_part1_k3", "full_story_part3_k1", "full_story_part3_k2"):
            self.assertIs(seg[cid]["slowdown_applied"], True)
            ct = seg[cid]["chunk_tts"]
            self.assertEqual((ct["level"], ct["std_slowdown_composition"], ct["extra_pause_s"]), ("a2", "per_chunk_slowdown_then_pad_0.2s", 0.2))
        p1 = seg["full_story_part1"]
        self.assertEqual(p1["status"], "OK")
        self.assertIs(p1["slowdown_applied"], True)
        self.assertEqual(p1["slowdown_basis"].split("(")[0], "all_chunks_slowdown_applied")
        self.assertEqual(p1["chunk_tts"]["chunk_ids"], ["full_story_part1_k1", "full_story_part1_k2", "full_story_part1_k3"])
        self.assertNotIn("chunk_tts", seg["full_story_part2"])                                            # 1段落part=従来entry
        self.assertIs(seg["full_story_part2"]["slowdown_applied"], True)

    def test_parent_wav_is_post_slowdown_chunks_plus_exact_0_2s_silence(self):
        Rig().run(self.tmp)
        nd = f"{self.tmp}/a2/narration"
        ids = [f"full_story_part1_k{i}" for i in (1, 2, 3)]
        core.verify_raw_parent(f"{nd}/full_story_part1.wav", [f"{nd}/{i}.wav" for i in ids])
        pcms = [core.read_pcm16(f"{nd}/{i}.wav") for i in ids]                                            # chunk wav = 減速後(_original.wavの1.06倍)
        origs = [core.read_pcm16(f"{nd}/{i}_original.wav") for i in ids]
        for p, o in zip(pcms, origs):
            self.assertAlmostEqual(len(p) / len(o), 1.06, places=2)
        parent = core.read_pcm16(f"{nd}/full_story_part1.wav")
        self.assertEqual(len(parent), sum(len(p) for p in pcms) + 2 * 4800)                               # ポーズは減速されない: ちょうど0.2秒×2
        self.assertTrue((parent[len(pcms[0]):len(pcms[0]) + 4800] == 0).all())
        seg = _results(self.tmp)["segments"]
        self.assertEqual(seg["full_story_part1"]["sha256"], core.sha256_file(f"{nd}/full_story_part1.wav"))

    def test_shared_gate_passes_parent_and_chunks_and_evidence_is_written(self):
        Rig().run(self.tmp)
        asm.verify_episode_audio_validation_gate(f"{self.tmp}/a2", "A2")
        self.assertIsNone(runner._x_std_chunk_slowdown_blocked(f"{self.tmp}/a2"))
        ev = json.load(open(f"{self.tmp}/a2/audit/chunk_tts_evidence_a2.json", encoding="utf-8"))
        self.assertEqual((ev["level"], ev["composition"]), ("a2", "per_chunk_slowdown_then_pad_0.2s"))
        rows = ev["parents"]["full_story_part1"]["chunks"]
        self.assertEqual(len(rows), 3)
        self.assertTrue(all(r["slowdown_applied"] is True and r["slowdown_pct_actual"] == 6.0 for r in rows))
        self.assertTrue(os.path.exists(f"{self.tmp}/a2/audit/chunk_plan_a2.json"))
        self.assertFalse(os.path.exists(f"{self.tmp}/a2/audit/chunk_plan_b1b.json"))                      # Advのファイルを作らない

    def test_chunk_without_slowdown_evidence_blocks_parent_and_assembly_gate(self):
        r = Rig(no_slowdown={"full_story_part1_k3"})
        r.run(self.tmp)
        seg = _results(self.tmp)["segments"]
        self.assertIs(seg["full_story_part1"]["slowdown_applied"], False)                                 # 親は集約False
        with self.assertRaises(RuntimeError) as cm:
            asm.verify_episode_audio_validation_gate(f"{self.tmp}/a2", "A2")                              # 共有Gate: 親のMISSING_MANDATORY_A2_SLOWDOWN
        self.assertIn("full_story_part1=", str(cm.exception))
        self.assertIn("MISSING_MANDATORY_A2_SLOWDOWN", str(cm.exception))
        blocked = runner._x_std_chunk_slowdown_blocked(f"{self.tmp}/a2")                                  # X追加Gate: どのchunkかを特定
        self.assertEqual(blocked["status"], "BLOCKED_STD_CHUNK_SLOWDOWN_GATE")
        self.assertEqual([b["segment"] for b in blocked["blocked"]], ["full_story_part1_k3"])

    def test_human_approval_cannot_bypass_missing_chunk_slowdown(self):
        Rig(no_slowdown={"full_story_part3_k2"}).run(self.tmp)
        out_dir = f"{self.tmp}/a2"
        seg = _results(self.tmp)["segments"]
        ap = asm.human_approval_path(out_dir)
        json.dump({"full_story_part3_k2": {"canonical_text_sha256": hashlib.sha256(seg["full_story_part3_k2"]["canonical_text"].encode()).hexdigest(),
                                           "approved_by": "t"}}, open(ap, "w", encoding="utf-8"))
        self.assertIsNotNone(runner._x_std_chunk_slowdown_blocked(out_dir))

    def test_chunk_failure_does_not_stop_later_chunks_and_parent_is_written_not_validated(self):
        r = Rig(fail={"full_story_part1_k2"})
        r.run(self.tmp)
        self.assertIn("full_story_part1_k3", r.body_names())                                              # R1: 失敗後も後続chunkを生成
        seg = _results(self.tmp)["segments"]
        self.assertEqual(seg["full_story_part1_k2"]["status"], "STOPPED")
        self.assertEqual(seg["full_story_part1"]["status"], core.PARENT_STATUS_NOT_ALL_VALIDATED)
        with self.assertRaises(RuntimeError):
            asm.verify_episode_audio_validation_gate(f"{self.tmp}/a2", "A2")

    def test_resume_reuses_ok_chunks_without_new_tts_and_regenerates_chunks_without_slowdown_evidence(self):
        Rig().run(self.tmp)
        r2 = Rig()
        r2.run(self.tmp)
        self.assertEqual(r2.body_names(), [])                                                              # OK chunk/partは全て再利用(再課金なし)
        res = _results(self.tmp)
        del res["segments"]["full_story_part1_k2"]["slowdown_applied"]                                    # 減速証跡のない旧cache
        json.dump(res, open(f"{self.tmp}/a2/audit/tts_generation_results.json", "w", encoding="utf-8"))
        r3 = Rig()
        r3.run(self.tmp)
        self.assertEqual(r3.body_names(), ["full_story_part1_k2"])                                        # 証跡なしchunkだけ再生成
        self.assertIs(_results(self.tmp)["segments"]["full_story_part1_k2"]["slowdown_applied"], True)

    def test_replan_with_same_text_and_version_stops_before_any_tts(self):
        Rig().run(self.tmp)
        p = f"{self.tmp}/a2/audit/chunk_plan_a2.json"
        d = json.load(open(p, encoding="utf-8"))
        d["plans"]["full_story_part1"]["chunks"][0]["text"] += " tampered"
        json.dump(d, open(p, "w", encoding="utf-8"))
        r = Rig()
        with self.assertRaises(core.ChunkIntegrityError):
            r.run(self.tmp)
        self.assertEqual(r.calls, [])

    def test_changed_text_regenerates_only_changed_chunk(self):
        Rig().run(self.tmp)
        parts = dict(PARTS)
        parts["part1"] = P1.replace("Para two has some more words in it.", "Para two now says something else entirely.")
        json.dump(parts, open(f"{self.tmp}/a2/parts.json", "w", encoding="utf-8"))
        r = Rig()
        r.run(self.tmp)
        self.assertEqual(r.body_names(), ["full_story_part1_k2"])

    def test_only_segments_parent_name_expands_to_all_its_chunks_for_std(self):
        sel, err = runner.validate_only_segments_args("tts", False, "a2", "full_story_part1")
        self.assertIsNone(err)
        old = runner._ONLY_SEGMENTS
        try:
            runner._ONLY_SEGMENTS = sel
            r = Rig()
            r.run(self.tmp)
        finally:
            runner._ONLY_SEGMENTS = old
        self.assertEqual(r.body_names(), ["full_story_part1_k1", "full_story_part1_k2", "full_story_part1_k3"])

    def test_single_paragraph_parts_only_means_no_chunking_and_legacy_files(self):
        parts = {**PARTS, "part1": P2, "part3": P2.replace("second", "third")}
        json.dump(parts, open(f"{self.tmp}/a2/parts.json", "w", encoding="utf-8"))
        r = Rig()
        r.run(self.tmp)
        self.assertEqual(r.body_names(), ["full_story_part1", "full_story_part2", "full_story_part3", "in_one_line"])
        self.assertFalse(os.path.exists(f"{self.tmp}/a2/audit/chunk_tts_evidence_a2.json"))                # 不発火=証跡ファイルなし(不発火と配線漏れを区別するのはplan記録)
        plan = json.load(open(f"{self.tmp}/a2/audit/chunk_plan_a2.json", encoding="utf-8"))["plans"]
        self.assertTrue(all(p["chunked"] is False for p in plan.values()))


class XStdLegacyAndAdvTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="xstd_leg_")
        _make_theme(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_legacy_unchunked_std_results_are_still_assembled_by_the_legacy_path(self):
        # 本方式導入前に生成されたStd結果(親entryのみ・chunk entryなし)は従来経路のまま(既存runの再組立を壊さない)
        os.makedirs(f"{self.tmp}/a2/audit", exist_ok=True)
        res = {"segments": {n: {"status": "OK", "canonical_text": PARTS[k], "slowdown_applied": True}
                            for n, k in (("full_story_part1", "part1"), ("full_story_part2", "part2"), ("full_story_part3", "part3"))}}
        json.dump(res, open(f"{self.tmp}/a2/audit/tts_generation_results.json", "w", encoding="utf-8"))
        plans = runner._x_effective_chunk_plans(f"{self.tmp}/a2", PARTS)
        for pid in ("full_story_part1", "full_story_part3"):
            self.assertFalse(plans[pid]["chunked"], pid)
            self.assertTrue(plans[pid].get("legacy_unchunked"), pid)
        self.assertIsNone(runner._x_std_chunk_slowdown_blocked(f"{self.tmp}/a2"))

    def test_adv_generate_source_is_unchanged_in_structure(self):
        import inspect
        src = inspect.getsource(runner.generate_family_x_b1_segments)
        self.assertIn("_generate_x_body_part_chunked(", src)
        self.assertNotIn("_generate_x_body_part_chunked_a2", src)
        self.assertNotIn("chunk_plan_a2", src)
        self.assertNotIn("drop_cached_std_chunks_without_slowdown", src)

    def test_refresh_parents_default_level_is_adv_and_adds_no_std_keys(self):
        # Adv(b1b)の親集約entryに減速集約keyが付かない
        os.makedirs(f"{self.tmp}/b1b/narration", exist_ok=True)
        parts = PARTS
        plan = core.plan_x_part(parts["part1"], "full_story_part1")
        segs = {}
        for c in plan["chunks"]:
            _wav(f"{self.tmp}/b1b/narration/{c['chunk_id']}.wav", 1, 2400)
            segs[c["chunk_id"]] = {"status": "OK", "canonical_text": c["text"], "asr_verified": True, "disfluency_checked": True,
                                   "fallback_used": False, "voice": "Aoede", "text": c["text"]}
        out = runner._refresh_x_chunk_parents(f"{self.tmp}/b1b", parts, segs, {"full_story_part1": plan})
        self.assertNotIn("slowdown_applied", out["full_story_part1"])
        self.assertNotIn("std_slowdown_composition", out["full_story_part1"])


class XStdGainAndAssemblyTests(unittest.TestCase):
    def _sources(self):
        rng = np.random.default_rng(9)
        mono = lambda a, n=24000: rng.normal(0, a, n)
        chunks = [mono(0.05, 24000), mono(0.09, 30000), mono(0.03, 12000)]
        raw = core.compose_raw_pcm([(c * 32767).astype(np.int16) for c in chunks]).astype("float64") / 32768
        st = lambda n=48000: rng.normal(0, 0.05, (n, 2))
        return {"intro": {"samples": st()}, "notification": {"samples": st()}, "outro": {"samples": st()},
                "preview_mono": mono(0.05), "narration": {"welcome": mono(0.05)},
                "a2_segments": {"full_story_part1": raw, "full_story_part2": mono(0.05, 20000), "comment_1": mono(0.05), "in_one_line": mono(0.05)},
                "key_phrase_components": {}, "kp_items": [], "body_chunks": {"full_story_part1": chunks}, "chunk_plans": {}}, chunks

    def test_std_gain_composes_chunks_with_per_chunk_gain_and_0_2s_pad(self):
        src, chunks = self._sources()
        out = runner.apply_family_x_a2_gain(src)
        gr = out["gain_report"]
        rep = gr["chunk_tts"]["full_story_part1"]
        self.assertEqual(len(rep["gains"]), 3)
        self.assertEqual(gr["a2_full_story_part1"]["chunked"], True)
        self.assertNotIn("gain", gr["a2_full_story_part1"])
        self.assertIn("gain", gr["a2_full_story_part2"])
        st = out["a2_segments"]["full_story_part1"]
        self.assertEqual(st.shape[0], 2 * (sum(len(c) for c in chunks) + 2 * 4800))                         # 24k→48k、0.2秒×2含む
        for a, b in rep["boundary_offsets_s"]:
            self.assertAlmostEqual(b - a, 0.2, places=4)

    def test_std_gain_without_chunks_is_byte_identical_to_legacy_formula(self):
        src, _ = self._sources()
        src["body_chunks"] = {}
        out = runner.apply_family_x_a2_gain(src)
        import er003_b1_p9a_audio as p9a
        mono = src["a2_segments"]["full_story_part2"]
        tgt = (p9a.rms(src["preview_mono"]) + p9a.rms(src["a2_segments"]["full_story_part1"])) / 2
        want = p9a.mono_24k_to_stereo_target(mono * p9a.compute_gain_for_target_rms(mono, tgt))
        self.assertTrue(np.array_equal(out["a2_segments"]["full_story_part2"], want))
        self.assertNotIn("chunk_tts", out["gain_report"])

    def test_stage_assemble_blocks_before_loading_audio_when_a_chunk_lacks_slowdown(self):
        tmp = tempfile.mkdtemp(prefix="xstd_asm_")
        try:
            _make_theme(tmp)
            Rig(no_slowdown={"full_story_part1_k1"}).run(tmp)
            os.makedirs(f"{tmp}/a2/key_phrases", exist_ok=True)
            json.dump({"items": []}, open(f"{tmp}/a2/key_phrases/keywords_canonicalized.json", "w", encoding="utf-8"))
            s = runner.stage_assemble_family_x_a2(tmp, "t")
            self.assertEqual(s["status"], "BLOCKED_STD_CHUNK_SLOWDOWN_GATE")
            self.assertEqual([b["segment"] for b in s["blocked"]], ["full_story_part1_k1"])
            wavs = [f for f in os.listdir(f"{tmp}/a2/assembled")] if os.path.isdir(f"{tmp}/a2/assembled") else []
            self.assertEqual(wavs, [], "BLOCK時に未完成のassembled音声を残さない")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
