# -*- coding: utf-8 -*-
"""er113_fx_paragraph_chunk_trial_01 の unit test (API 0、TTSを呼ばない)。
実行: PYTHONUTF8=1 .venv/Scripts/python.exe -m unittest er113_fx_paragraph_chunk_trial_01_test_01 -v
"""
import json
import os
import tempfile
import unittest

import numpy as np

import er113_fx_paragraph_chunk_trial_01 as t


class SplitTests(unittest.TestCase):
    def test_split_lossless_and_counts_on_real_parts(self):
        parts = t.load_json(f"{t.A_LEVEL_DIR}/parts.json")
        plan = t.build_chunk_plan(parts)
        self.assertEqual([c["chunk_id"] for c in plan],
                         ["p1_1", "p1_2", "p1_3", "p1_4", "p2_1", "p2_2", "p2_3", "p3_1", "p3_2", "p3_3"])
        for n in t.PARTS:
            paras = [c["text"] for c in plan if c["part"] == n]
            self.assertTrue(t.verify_split_lossless(parts[f"part{n}"], paras))
        self.assertEqual(sum(c["words"] for c in plan if c["part"] == 1) > 0, True)

    def test_tts_safe_news_en_is_paragraph_local(self):
        """A側は tts_safe_news_en(part全体) をTTSへ渡す。その出力には改行が無く(段落境界は半角空白へ畳まれる=Aの入力は『段落区切り情報なしの1続き文』)、
        段落ごとに掛けた結果を' 'で連結すると全体適用と完全一致する(=B各chunkの入力テキストはAの入力の単なる分割で、整形差なし)。"""
        import er003_v1_n3_01_tts_generate as n3_tts
        parts = t.load_json(f"{t.A_LEVEL_DIR}/parts.json")
        for n in t.PARTS:
            whole = n3_tts.tts_safe_news_en(parts[f"part{n}"])
            per = [n3_tts.tts_safe_news_en(p) for p in t.split_paragraphs(parts[f"part{n}"])]
            self.assertNotIn(chr(10), whole)
            self.assertEqual(whole, " ".join(per), f"part{n}: 整形が段落単位と全体で異なる")


class JoinTests(unittest.TestCase):
    def _tone(self, amp, sec=1.0):
        x = np.sin(2 * np.pi * 220 * np.arange(int(sec * t.SR24)) / t.SR24) * amp
        pad = np.zeros(int(0.3 * t.SR24))
        return np.concatenate([pad, x, pad]).astype(np.float64)

    def test_per_chunk_gain_equalizes_rms(self):
        import er003_b1_p9a_audio as p9a
        chunks = [self._tone(0.05), self._tone(0.2)]
        target = 0.08
        r = t.join_chunks(chunks, target, pause_seconds=0.0, per_chunk_gain=True)
        # 各chunkのpost RMSは target に近い(peak上限0.95に当たらない範囲)
        for post in r["rms_after"]:
            self.assertAlmostEqual(post, target, delta=0.002)
        self.assertEqual(len(r["mono24"]), sum(len(c) for c in chunks))  # pause 0 = 純粋連結(crossfade/重ね合わせなし)

    def test_pause_inserted_only_between(self):
        chunks = [self._tone(0.1), self._tone(0.1), self._tone(0.1)]
        r = t.join_chunks(chunks, 0.08, pause_seconds=0.5)
        self.assertEqual(len(r["mono24"]), sum(len(c) for c in chunks) + 2 * int(0.5 * t.SR24))

    def test_segment_gain_mode_single_gain(self):
        r = t.join_chunks([self._tone(0.05), self._tone(0.2)], 0.08, per_chunk_gain=False)
        self.assertEqual(len(r["gains"]), 1)

    def test_boundary_jump_db_detects_volume_step(self):
        a, b = self._tone(0.05), self._tone(0.2)
        j = t.boundary_jump_db([a, b])
        self.assertAlmostEqual(j[0], 20 * np.log10(4), delta=0.3)

    def test_peak_cap_respected(self):
        import er003_b1_p9a_audio as p9a
        quiet_peaky = self._tone(0.9)
        g, _ = t.normalize_chunk_to_target(quiet_peaky, 5.0)[0], 0
        self.assertLessEqual(p9a.peak(g), 0.95 + 1e-6)


class MeasureTests(unittest.TestCase):
    def test_articulation_separates_pause_from_speed(self):
        """同じ発話に長いポーズを足すと total_wpm は下がるが articulation_wpm_500 は(ほぼ)変わらない。"""
        sp = np.sin(2 * np.pi * 200 * np.arange(int(2 * t.SR24)) / t.SR24) * 0.3
        base = np.concatenate([sp, sp])
        paused = np.concatenate([sp, np.zeros(int(1.0 * t.SR24)), sp])
        m0, m1 = t.measure_wav(base, t.SR24, 10), t.measure_wav(paused, t.SR24, 10)
        self.assertLess(m1["total_wpm"], m0["total_wpm"] * 0.85)
        self.assertAlmostEqual(m1["articulation_wpm_500"], m0["articulation_wpm_500"], delta=m0["articulation_wpm_500"] * 0.03)
        self.assertEqual(m1["pause_500"]["n_mid"], 1)


class IsolationTests(unittest.TestCase):
    def test_gen_refuses_without_go_file(self):
        if os.path.exists(os.path.join(t.ROOT, t.PHASE2_GO_FILE)):
            self.skipTest("GOあり")
        with self.assertRaises(SystemExit):
            t._require_go()

    def test_sink_redirect_and_restore(self):
        import importlib
        orig = {}
        for m, a in t.SINK_CONSTANTS:
            orig[(m, a)] = getattr(importlib.import_module(m), a)
        m21 = importlib.import_module("er021_en_asr_semantic_equivalence_production_01")
        orig_fn = m21.append_telemetry_log
        with tempfile.TemporaryDirectory() as td:
            rel = os.path.relpath(td, t.ROOT) if td.startswith(t.ROOT) else td
            with t.redirect_production_sinks(rel):
                for m, a in t.SINK_CONSTANTS:
                    self.assertNotEqual(getattr(importlib.import_module(m), a), orig[(m, a)])
                self.assertIsNot(m21.append_telemetry_log, orig_fn)
            for m, a in t.SINK_CONSTANTS:
                self.assertEqual(getattr(importlib.import_module(m), a), orig[(m, a)])
            self.assertIs(m21.append_telemetry_log, orig_fn)

    def test_dry_run_with_fake_tts_writes_nothing_to_production(self):
        """injectしたfake生成関数でgenerate_chunks_phase2を通し、Production storeが不変であることを確認(API 0)。"""
        before = t.snapshot_protected()
        plan = t.build_chunk_plan(t.load_json(f"{t.A_LEVEL_DIR}/parts.json"))[:2]
        calls = []

        def fake(text, out_path, **kw):
            calls.append((out_path, kw.get("enable_repetition_qa"), kw.get("tts_backend")))
            import soundfile as sf
            sf.write(out_path, np.zeros(2400, dtype="float32"), t.SR24)
            return {"status": "OK", "attempts_log": [{}], "audio_classification": "FAKE", "trim_info": None}
        import shutil
        real_out = t.OUT_DIR
        tmp_out = "er113_output/_dryrun_tmp_test"   # 本番OUT_DIR(Phase 2実成果物)を絶対に触らないため専用tmpへ向ける
        t.OUT_DIR = tmp_out
        self.addCleanup(lambda: (setattr(t, "OUT_DIR", real_out), shutil.rmtree(os.path.join(t.ROOT, tmp_out), ignore_errors=True)))
        with t.redirect_production_sinks(f"{tmp_out}/sinks_dryrun"):
            res = t.generate_chunks_phase2(plan, tts_generate_fn=fake)
        self.assertEqual(len(calls), 2)
        self.assertTrue(all(c[1] is True and c[2] == "speech_metadata_flash_lite" for c in calls))
        self.assertTrue(all("/gen/p1_" in c[0].replace("\\", "/") for c in calls))
        self.assertEqual(t.diff_snapshots(before, t.snapshot_protected()), [])


class CostTests(unittest.TestCase):
    def test_tts_cost_matches_recorded_a_call(self):
        # A実測: part1 attempt1 output_tokens=1308 input_tokens=189 -> 約1.27円
        jpy = (1308 * t.TTS_STD_OUT_USD_PER_M / 1e6 + 189 * t.TTS_STD_IN_USD_PER_M / 1e6) * t.USD_JPY
        self.assertAlmostEqual(jpy, 1.27, delta=0.02)


class MeasureDefsMatchOriginal(unittest.TestCase):
    def test_measure_defs_match_original_source(self):
        """転記元(measure_wpm_01.py)の関数をastで抜き出して(importせず=main()を走らせず)実行し、転記版と数値一致を確認。"""
        import ast
        import re as _re
        src_path = os.path.join(t.ROOT, "er057_output/coffee_final_listening_tone_trial_01/wpm_measurement_01/measure_wpm_01.py")
        src = open(src_path, encoding="utf-8").read()
        tree = ast.parse(src)
        keep = [n for n in tree.body if (isinstance(n, ast.FunctionDef) and n.name in ("count_primary", "frame_rms_db", "find_pauses"))
                or (isinstance(n, ast.Assign) and getattr(n.targets[0], "id", None) in ("FRAME_MS", "THRESH_DB"))
                or (isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Tuple))]
        ns = {"np": np, "re": _re}
        exec(compile(ast.Module(body=keep, type_ignores=[]), "orig", "exec"), ns)
        self.assertEqual((ns["FRAME_MS"], ns["HOP_MS"], ns["THRESH_DB"]), (t._MW.FRAME_MS, t._MW.HOP_MS, t._MW.THRESH_DB))
        rng = np.random.default_rng(0)
        x = np.concatenate([rng.normal(0, 0.1, 24000), np.zeros(12000), rng.normal(0, 0.1, 24000)])
        mine = t._mw()
        self.assertTrue(np.allclose(ns["frame_rms_db"](x, 24000), mine.frame_rms_db(x, 24000)))
        dur = len(x) / 24000
        self.assertEqual(ns["find_pauses"](ns["frame_rms_db"](x, 24000), 300, dur), mine.find_pauses(mine.frame_rms_db(x, 24000), 300, dur))
        self.assertEqual(ns["count_primary"]("It's 2026 — a well-known 1,000 fine."), mine.count_primary("It's 2026 — a well-known 1,000 fine."))


class ArmPlanTests(unittest.TestCase):
    def test_arm_plans(self):
        parts = t.load_json(f"{t.A_LEVEL_DIR}/parts.json")
        b = t.arm_plan("B_r1", parts)
        self.assertEqual(len(b), 10)
        self.assertTrue(all(c["chunk_id"].startswith("B_r1_p") for c in b))
        a = t.arm_plan("A_r2", parts)
        self.assertEqual([c["text"] for c in a], [parts["part1"], parts["part2"], parts["part3"]])
        with self.assertRaises(SystemExit):
            t.arm_plan("X", parts)


if __name__ == "__main__":
    unittest.main()
