# -*- coding: utf-8 -*-
"""CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01 委任_02: Opus条件Aレビュー(M1・R1〜R3)反映のtest(API 0・TTS 0。TTS関数はmock)。
実行: PYTHONPATH=netblock_harness_01 .venv/Scripts/python.exe -m pytest er019_x_std_chunk_opus_test_01.py -q

M1  旧方式(親entryのみ)のStd/Adv結果へ『本文以外』の--only-segments retry → 本文のTTS 0回・親が上書きされず従来経路で残る。本文を含む通常のresumeはchunk化して再生成。
R1  load_family_x_a2_sourcesにもchunk単位の減速証跡検査(親の集約値を偽装しても通らない)。
R2  slowdown_infoの減速前後長が欠けたchunkは違反。
R3  (a)集約値Falseの親は古い親_original.wavの弱い証拠で救済されない (b)減速後NG→人間承認chunkで親OK・集約True・Gate PASS (c)planに無いchunk idの指定は拒否。
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
import er019_x_std_chunk_test_01 as stdt
import er117_chunk_tts_production_01 as core
import er117_x_chunk_wiring_test_01 as advt

P1 = stdt.P1


def _results_a2(tmp):
    return stdt._results(tmp)


def _make_legacy_std(tmp):
    """本方式導入前のStd結果(本文part1が複数段落でも1 callで生成=親entryのみ)を、planを一時的に『全て非chunk』にして再現する。"""
    legacy = lambda parts: {pid: {**core.plan_x_part(parts["part" + pid[-1]], pid), "chunked": False, "chunks": []}
                            for pid in ("full_story_part1", "full_story_part2", "full_story_part3")}
    with mock.patch.object(runner, "_x_chunk_plans", side_effect=legacy):
        r = stdt.Rig()
        r.run(tmp)
    os.remove(f"{tmp}/a2/audit/chunk_plan_a2.json")      # 本方式導入前の生成=chunk planファイルは存在しない
    return r


class M1LegacyStdPartialRetryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="m1std_")
        stdt._make_theme(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _only(self, names, rig):
        sel, err = runner.validate_only_segments_args("tts", False, "a2", names)
        self.assertIsNone(err)
        old = runner._ONLY_SEGMENTS
        try:
            runner._ONLY_SEGMENTS = sel
            rig.run(self.tmp)
        finally:
            runner._ONLY_SEGMENTS = old

    def test_legacy_std_result_plus_non_body_only_segments_does_not_touch_body(self):
        first = _make_legacy_std(self.tmp)
        self.assertEqual([c["name"] for c in first.calls if c["name"].startswith("full_story")],
                         ["full_story_part1", "full_story_part2", "full_story_part3"])      # 旧方式=本文partは各1 call
        before = json.dumps(_results_a2(self.tmp)["segments"]["full_story_part1"], sort_keys=True)
        r = stdt.Rig()
        self._only("comment_2", r)
        self.assertEqual(r.body_names(), [])                                                 # 本文のTTSは0回(chunkも親も)
        seg = _results_a2(self.tmp)["segments"]
        self.assertNotIn("chunk_tts", seg["full_story_part1"])                              # 親が chunk集約entry(CHUNKS_NOT_ALL_VALIDATED)で上書きされない
        self.assertNotEqual(seg["full_story_part1"]["status"], core.PARENT_STATUS_NOT_ALL_VALIDATED)
        self.assertNotIn("full_story_part1_k1", seg)                                         # 未生成chunkの空entryも作らない
        self.assertEqual(seg["full_story_part1"]["canonical_text"], json.loads(before)["canonical_text"])
        # 検証済み本文は共有Gate上も有効のまま(引継ぎ=従来経路)
        for pid in ("full_story_part1", "full_story_part3"):
            self.assertEqual(asm._segment_gate_status(seg[pid], pid, {}), "VALIDATED", pid)
        # 組立側も旧方式経路: effective planは非chunk・Std chunk追加Gateは対象なし
        plans = runner._x_effective_chunk_plans(f"{self.tmp}/a2", stdt.PARTS)
        self.assertTrue(all(not p["chunked"] for p in plans.values()))
        self.assertIsNone(runner._x_std_chunk_slowdown_blocked(f"{self.tmp}/a2"))

    def test_legacy_std_result_with_body_in_only_segments_is_rechunked_as_before(self):
        # 本文を含む通常のresume=承認文の『resumeへ一貫』どおりchunk化して再生成する(現行維持。SSOT既知事項)
        _make_legacy_std(self.tmp)
        r = stdt.Rig()
        self._only("full_story_part1", r)
        self.assertEqual(r.body_names(), ["full_story_part1_k1", "full_story_part1_k2", "full_story_part1_k3"])
        self.assertIn("chunk_tts", _results_a2(self.tmp)["segments"]["full_story_part1"])

    def test_chunk_id_directly_selected_on_legacy_result_goes_chunk_path(self):
        _make_legacy_std(self.tmp)
        r = stdt.Rig()
        self._only("full_story_part1_k2", r)
        self.assertEqual(r.body_names(), ["full_story_part1_k2"])

    def test_already_chunked_result_is_not_treated_as_legacy(self):
        stdt.Rig().run(self.tmp)                                                              # 新方式の結果(chunk entryあり)
        plans = core.plan_x_parts(stdt.PARTS)
        cached = {"segments": _results_a2(self.tmp)["segments"]}
        self.assertEqual(core.legacy_partial_retry_parents(plans, cached, {"comment_2"}), set())

    def test_helper_only_none_or_empty_cache_is_noop(self):
        plans = core.plan_x_parts(stdt.PARTS)
        self.assertEqual(core.legacy_partial_retry_parents(plans, {"segments": {"full_story_part1": {"status": "OK"}}}, None), set())
        self.assertEqual(core.legacy_partial_retry_parents(plans, None, {"comment_2"}), set())
        self.assertIs(core.apply_legacy_partial_retry(plans, None, {"comment_2"}), plans)


class M1LegacyAdvPartialRetryTests(unittest.TestCase):
    """同じ潜在不具合は10-25配線のX Advにもあった(Opus M1)。"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="m1adv_")
        advt._make_theme(self.tmp)
        # 他testが残したPNAP=ONの状態で固有名詞アラームの実体表構築(OpenAI NER)に入らないよう明示的にOFF(接続試行0を保証)
        p = mock.patch.object(runner.pnap_hooks.pnap, "is_enabled", return_value=False)
        p.start()
        self.addCleanup(p.stop)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_legacy_adv_result_plus_non_body_only_segments_does_not_touch_body(self):
        legacy = lambda parts: {pid: {**core.plan_x_part(parts["part" + pid[-1]], pid), "chunked": False, "chunks": []}
                                for pid in ("full_story_part1", "full_story_part2", "full_story_part3")}
        with mock.patch.object(runner, "_x_chunk_plans", side_effect=legacy):
            first = advt.Rig()
            first.run(self.tmp)
        os.remove(f"{self.tmp}/b1b/audit/chunk_plan_b1b.json")      # 本方式導入前の生成=chunk planファイルは存在しない
        self.assertIn("full_story_part1", first.names())
        sel, err = runner.validate_only_segments_args("tts", False, "b1b", "comment_2")
        self.assertIsNone(err)
        old = runner._ONLY_SEGMENTS
        try:
            runner._ONLY_SEGMENTS = sel
            r = advt.Rig()
            r.run(self.tmp)
        finally:
            runner._ONLY_SEGMENTS = old
        self.assertEqual([n for n in r.names() if n.startswith("full_story") or n == "in_one_line"], [])
        seg = advt._results(self.tmp)["segments"]
        self.assertNotIn("chunk_tts", seg["full_story_part1"])
        self.assertEqual(asm._segment_gate_status(seg["full_story_part1"], "full_story_part1", {}), "VALIDATED")


class R2MissingDurationRecordTests(unittest.TestCase):
    def _plan(self):
        return core.plan_x_part(stdt.P1, "full_story_part1")

    def _segs(self, info):
        plan = self._plan()
        return plan, {c["chunk_id"]: {"slowdown_applied": True, "slowdown_info": dict(info)} for c in plan["chunks"]}

    def test_missing_src_or_dst_is_a_violation(self):
        for info in ({}, {"src_duration_seconds": 1.0}, {"dst_duration_seconds": 1.06}, {"src_duration_seconds": 0, "dst_duration_seconds": 0}):
            plan, segs = self._segs(info)
            bad = core.std_chunk_slowdown_violations(plan, segs)
            self.assertEqual(len(bad), 3, info)
            self.assertIn("STD_CHUNK_SLOWDOWN_DURATION_RECORD_MISSING", bad[0]["violations"])

    def test_complete_record_in_range_passes_and_out_of_range_fails(self):
        plan, segs = self._segs({"src_duration_seconds": 1.0, "dst_duration_seconds": 1.06})
        self.assertEqual(core.std_chunk_slowdown_violations(plan, segs), [])
        plan, segs = self._segs({"src_duration_seconds": 1.0, "dst_duration_seconds": 1.3})
        self.assertTrue(core.std_chunk_slowdown_violations(plan, segs)[0]["violations"][0].startswith("STD_CHUNK_SLOWDOWN_RATIO_OUT_OF_RANGE"))

    def test_real_generation_records_both_durations_so_no_false_block(self):
        tmp = tempfile.mkdtemp(prefix="r2_")
        try:
            stdt._make_theme(tmp)
            stdt.Rig().run(tmp)
            self.assertIsNone(runner._x_std_chunk_slowdown_blocked(f"{tmp}/a2"))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class R3Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="r3_")
        stdt._make_theme(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_a_aggregate_false_parent_is_not_rescued_by_stale_parent_original_wav(self):
        stdt.Rig(no_slowdown={"full_story_part1_k3"}).run(self.tmp)
        nd = f"{self.tmp}/a2/narration"
        seg = _results_a2(self.tmp)["segments"]
        self.assertIs(seg["full_story_part1"]["slowdown_applied"], False)
        # 古い親_original.wav(現在の親wavとの長さ比が6%に整合する弱い証拠)を置いても救済されない
        n_parent = len(core.read_pcm16(f"{nd}/full_story_part1.wav"))
        stdt._wav(f"{nd}/full_story_part1_original.wav", 1, int(n_parent / 1.06))
        self.assertTrue(asm._segment_missing_mandatory_a2_slowdown("full_story_part1", seg["full_story_part1"], nd))
        with self.assertRaises(RuntimeError) as cm:
            asm.verify_episode_audio_validation_gate(f"{self.tmp}/a2", "A2")
        self.assertIn("MISSING_MANDATORY_A2_SLOWDOWN", str(cm.exception))

    def test_b_post_slowdown_ng_then_human_approved_chunk_gives_ok_parent_true_aggregate_and_gate_pass(self):
        stdt.Rig(fail={"full_story_part1_k2"}).run(self.tmp)
        out_dir = f"{self.tmp}/a2"
        seg = _results_a2(self.tmp)["segments"]
        self.assertIs(seg["full_story_part1_k2"]["slowdown_applied"], True)                  # 減速は適用済み(減速後ASRだけNG=STOPPED)
        self.assertEqual(seg["full_story_part1"]["status"], core.PARENT_STATUS_NOT_ALL_VALIDATED)
        with self.assertRaises(RuntimeError):
            asm.verify_episode_audio_validation_gate(out_dir, "A2")
        asm.record_human_approval(out_dir, "full_story_part1_k2", seg["full_story_part1_k2"]["canonical_text"])
        runner._chunk_parent_refresh_x(out_dir, "a2")                                         # assemble入口の親再構築
        seg = _results_a2(self.tmp)["segments"]
        self.assertEqual(seg["full_story_part1"]["status"], "OK")
        self.assertIs(seg["full_story_part1"]["slowdown_applied"], True)
        self.assertEqual(seg["full_story_part1"]["chunk_tts"]["human_approved_chunks"], ["full_story_part1_k2"])
        asm.verify_episode_audio_validation_gate(out_dir, "A2")                               # 共有Gate PASS
        self.assertIsNone(runner._x_std_chunk_slowdown_blocked(out_dir))                      # 追加Gateも減速証跡あり=PASS

    def test_c_unknown_chunk_id_in_only_segments_is_rejected_before_any_tts(self):
        for bad in ("full_story_part1_k9", "full_story_part2_k1"):                           # k9=範囲外 / part2は1段落=chunkなし
            sel, err = runner.validate_only_segments_args("tts", False, "a2", bad)
            self.assertIsNone(err)                                                           # 形式は妥当(validate_only_segments_argsはplanを知らない)
            old = runner._ONLY_SEGMENTS
            r = stdt.Rig()
            try:
                runner._ONLY_SEGMENTS = sel
                with self.assertRaises(core.ChunkIntegrityError) as cm:
                    r.run(self.tmp)
            finally:
                runner._ONLY_SEGMENTS = old
            self.assertIn(bad, str(cm.exception))
            self.assertEqual(r.calls, [], bad)                                               # 課金前=TTS 0回

    def test_c_helper_accepts_known_chunk_ids_and_non_chunk_names(self):
        plans = core.plan_x_parts(stdt.PARTS)
        self.assertEqual(core.unknown_chunk_ids_in_selection(plans, {"full_story_part1_k2", "comment_2", "full_story_part1"}), [])
        self.assertEqual(core.unknown_chunk_ids_in_selection(plans, {"full_story_part1_k4"}), ["full_story_part1_k4"])
        self.assertEqual(core.unknown_chunk_ids_in_selection(plans, None), [])


class R1LoadFunctionHasSlowdownCheckTests(unittest.TestCase):
    """load_family_x_a2_sourcesを『stage関数を通さず』直接呼んでも、chunk単位の減速証跡検査を通る(共有Gateがload関数の中にある構造と揃える)。"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="r1_")
        stdt._make_theme(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _forge_parent_true(self):
        # 抜け道の試み: chunkの減速証跡を欠いたまま、親の集約値だけTrueに書き換える(共有Gateはこれを通す)
        p = f"{self.tmp}/a2/audit/tts_generation_results.json"
        doc = json.load(open(p, encoding="utf-8"))
        doc["segments"]["full_story_part1"]["slowdown_applied"] = True
        json.dump(doc, open(p, "w", encoding="utf-8"))
        os.makedirs(f"{self.tmp}/a2/key_phrases", exist_ok=True)
        json.dump({"items": []}, open(f"{self.tmp}/a2/key_phrases/keywords_canonicalized.json", "w"))

    def _load(self):
        z = np.zeros(2400)
        with mock.patch.object(runner.asm, "verify_episode_audio_validation_gate", return_value=None), \
             mock.patch.object(runner.p9a, "load_and_resample_to_target", return_value=z), \
             mock.patch.object(runner.common, "read_wav_float", return_value=(z, runner.common.SAMPLE_RATE, None, None)):
            return runner.load_family_x_a2_sources(self.tmp)

    def test_forged_parent_aggregate_is_still_blocked_by_chunk_check_in_load(self):
        stdt.Rig(no_slowdown={"full_story_part1_k2"}).run(self.tmp)
        self._forge_parent_true()
        with self.assertRaises(core.ChunkIntegrityError) as cm:
            self._load()
        self.assertIn("BLOCKED_STD_CHUNK_SLOWDOWN_GATE", str(cm.exception))
        self.assertIn("full_story_part1_k2", str(cm.exception))

    def test_missing_duration_record_is_blocked_in_load_too(self):
        stdt.Rig().run(self.tmp)
        p = f"{self.tmp}/a2/audit/tts_generation_results.json"
        doc = json.load(open(p, encoding="utf-8"))
        del doc["segments"]["full_story_part1_k1"]["slowdown_info"]["dst_duration_seconds"]
        json.dump(doc, open(p, "w", encoding="utf-8"))
        os.makedirs(f"{self.tmp}/a2/key_phrases", exist_ok=True)
        json.dump({"items": []}, open(f"{self.tmp}/a2/key_phrases/keywords_canonicalized.json", "w"))
        with self.assertRaises(core.ChunkIntegrityError) as cm:
            self._load()
        self.assertIn("DURATION_RECORD_MISSING", str(cm.exception))

    def test_properly_slowed_chunks_pass_the_load_check(self):
        stdt.Rig().run(self.tmp)
        os.makedirs(f"{self.tmp}/a2/key_phrases", exist_ok=True)
        json.dump({"items": []}, open(f"{self.tmp}/a2/key_phrases/keywords_canonicalized.json", "w"))
        out = self._load()
        self.assertEqual(sorted(out["body_chunks"]), ["full_story_part1", "full_story_part3"])


class R4HunkClassifierTest(unittest.TestCase):
    def test_every_diff_vs_pre_implementation_head_is_a2_only_new_helper_default_adv_or_reviewed(self):
        """Opus R4(a): git diff bb578265c の各差分箇所が、a2専用/新設helper/既定値Advのhelper/Std専用ガード内/人手レビュー済み のいずれかであること(UNCLASSIFIED=0)。"""
        import subprocess
        import sys
        tool = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs", "research", "CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01", "tools", "adv_hunk_classifier_01.py")
        out = os.path.join(tempfile.mkdtemp(prefix="hunk_"), "r.json")
        try:
            cp = subprocess.run([sys.executable, tool, "--base", "bb578265c", "--out", out], capture_output=True, cwd=os.path.dirname(os.path.abspath(__file__)), env={**os.environ, "PYTHONUTF8": "1"})
        except OSError:
            self.skipTest("git/python起動不可")
        if b"unknown revision" in cp.stderr or b"bad object" in cp.stderr:
            self.skipTest("基準commit bb578265c が無い環境")
        self.assertEqual(cp.returncode, 0, cp.stdout.decode("utf-8", "replace")[-2000:] + cp.stderr.decode("utf-8", "replace")[-1000:])
        self.assertEqual(json.load(open(out, encoding="utf-8"))["unclassified"], [])


if __name__ == "__main__":
    unittest.main()
