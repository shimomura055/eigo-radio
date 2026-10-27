# -*- coding: utf-8 -*-
"""FAMILY-Y-STYLE-PROFILE-FIX-01 委任_08: 開発用Chunk境界マーカー(audience=dev|public、X/Y/Z共通の表示機構)のtest。API 0・表示専用。
ユーザー正式決定2026-10-27(USER_04 §1-C): 実TTS Chunk分割境界のみ⏸、ASR/音声解析ポーズは表示しない、公開物にはマーカーを出さない。"""
import glob
import json
import os
import re
import tempfile
import unittest

import er_user_listening_page_common_01 as cp

ROOT = os.path.dirname(os.path.abspath(__file__))
SCRIPT = "First paragraph here.\n\nSecond paragraph here.\n\nThird paragraph here."
CHUNKS3 = ["First paragraph here.", "Second paragraph here.", "Third paragraph here."]


class MarkerCore(unittest.TestCase):
    def test_default_is_public_and_byte_identical_to_legacy(self):
        legacy = "<div class='script'>" + cp.esc(SCRIPT) + "</div>"
        self.assertEqual(cp.script_block(SCRIPT), legacy)
        self.assertEqual(cp.script_block(SCRIPT, CHUNKS3), legacy)                     # chunk情報を渡されても既定publicはマーカーなし
        self.assertEqual(cp.script_block(SCRIPT, CHUNKS3, "public"), legacy)
        self.assertEqual(cp.AUDIENCE_PUBLIC, "public")

    def test_dev_marker_count_equals_real_chunk_boundaries(self):
        for chunks, expect in ((CHUNKS3, 2), (CHUNKS3[:2], 1)):
            text = "\n\n".join(chunks)
            h = cp.script_block(text, chunks, "dev")
            self.assertEqual(cp.count_chunk_markers(h), expect)
            for t in chunks:
                self.assertIn(cp.esc(t), h)                                            # 本文は不変(マーカーを足すだけ)
        self.assertIn("First paragraph here. <span class='chunk-mark'>&#9208;</span>\n\nSecond", cp.script_block(SCRIPT, CHUNKS3, "dev"))
        self.assertNotRegex(cp.script_block(SCRIPT, CHUNKS3, "dev"), r"title=|\d+(\.\d+)?\s*s\b")     # 秒数・title属性・説明なし

    def test_no_boundary_no_marker(self):
        for chunks in (None, [], ["only one"]):
            self.assertEqual(cp.count_chunk_markers(cp.script_block("only one", chunks, "dev")), 0)
        self.assertEqual(cp.chunk_texts_of_plan({"chunked": False, "chunks": []}), [])
        self.assertEqual(cp.chunk_texts_of_plan(None), [])
        self.assertEqual(cp.chunk_texts_of_plan({"chunked": True, "chunks": [{"text": "a"}]}), [])
        self.assertEqual(cp.chunk_texts_of_plan({"chunked": True, "chunks": [{"text": "a"}, {"text": "b"}]}), ["a", "b"])

    def test_chunk_text_not_found_is_not_guessed(self):
        warn = []
        h = cp.script_block(SCRIPT, ["First paragraph here.", "NOT IN SCRIPT", "Third paragraph here."], "dev", warn)
        self.assertEqual(cp.count_chunk_markers(h), 1)                                 # 位置不明の境界は出さない(推定位置なし)
        self.assertEqual(len(warn), 1)
        self.assertIn("CHUNK_TEXT_NOT_FOUND_IN_SCRIPT", warn[0])

    def test_whitespace_difference_tolerated(self):
        h = cp.script_block("A  b\nc.\n\nD e.", ["A b c.", "D e."], "dev")
        self.assertEqual(cp.count_chunk_markers(h), 1)

    def test_html_is_escaped(self):
        h = cp.script_block("<b>x</b>\n\ny & z", ["<b>x</b>", "y & z"], "dev")
        self.assertIn("&lt;b&gt;x&lt;/b&gt;", h)
        self.assertNotIn("<b>x", h)

    def test_audience_validation_is_fail_closed(self):
        for bad in (None, "", "DEV", "Dev", "both", True):
            with self.assertRaises(ValueError):
                cp.normalize_audience(bad)
            with self.assertRaises(ValueError):
                cp.script_block("x", None, bad)

    def test_count_detects_both_forms(self):
        self.assertEqual(cp.count_chunk_markers("a⏸b &#9208; &#x23F8;"), 3)
        self.assertEqual(cp.count_chunk_markers("clean"), 0)

    def test_load_chunk_plans_missing_file_is_empty(self):
        self.assertEqual(cp.load_chunk_plans(os.path.join(tempfile.gettempdir(), "no_such_plan_xyz.json")), {})


class PublicGuard(unittest.TestCase):
    def _page(self, block):
        lv = [{"id": "standard", "label": "Standard", "full_src": "a.mp3", "duration": 1.0,
               "rows": [{"part": "Full Story Part 1", "start": 0.0, "dur": 1.0, "src": "a.mp3", "blocks": [block]}]}]
        return cp.render_standard_page("T", lv)

    def test_check_page_fails_public_page_with_marker_but_not_dev(self):
        dev_block = cp.script_block(SCRIPT, CHUNKS3, "dev")
        pub = cp.check_page(self._page(dev_block), levels=("Standard",))                # 既定=public
        self.assertFalse(pub["checks"]["no_chunk_marker_in_public"]["ok"])
        self.assertEqual(pub["overall"], "FAIL")
        dev = cp.check_page(self._page(dev_block), levels=("Standard",), audience="dev")
        self.assertNotIn("no_chunk_marker_in_public", dev["checks"])
        clean = cp.check_page(self._page(cp.script_block(SCRIPT, CHUNKS3)), levels=("Standard",))
        self.assertTrue(clean["checks"]["no_chunk_marker_in_public"]["ok"])

    def test_published_artifacts_have_no_marker(self):
        """量産スクリプト(parts.json/study_text/article)にマーカー0件(表示専用機構がデータ側に漏れない)。新builderの公開用pagesは FullMockRun.test_page_rows_... と dev/public比較testで検査。旧run出力のpages/index.htmlは旧builder生成物(旧実測ポーズ表示)で対象外。
        除外: user_test/family_y_production_redelivery_fee_0N の静的ページ(委任_07が出力済みの静的物。`_03`の凡例1行に記号⏸が残る件は VERIFY_06.md に記録=次委任で是正。
        旧版`_01`/`_02`は履歴)。"""
        pats = ["er121_output/family_y_production_01/**/parts.json", "er121_output/family_y_production_01/**/study_text/*",
                "er121_output/family_y_production_01/**/article*.md"]
        n = 0
        for pat in pats:
            for p in glob.glob(os.path.join(ROOT, pat), recursive=True):
                if not os.path.isfile(p):
                    continue
                n += 1
                with open(p, encoding="utf-8", errors="ignore") as f:
                    self.assertEqual(cp.count_chunk_markers(f.read()), 0, p)
        self.assertGreaterEqual(n, 1)


class NoLegacyPauseDisplay(unittest.TestCase):
    def test_legacy_identifiers_are_gone_from_production_sources(self):
        legacy = re.compile(r"_script_with_pauses|PAUSE_MARK_MIN_MS|_PZ_STYLE|&#9208;\d")
        for fn in ("er121_family_y_audio_01.py", "er121_family_y_runner_01.py", "er121_family_y_structure_01.py", "er063_family_z_audio_01.py",
                   "er019_family_x_audio_production_runner_01.py", "er_user_listening_page_common_01.py"):
            src = open(os.path.join(ROOT, fn), encoding="utf-8").read()
            self.assertIsNone(legacy.search(src), fn)

    def test_runners_default_to_public_and_do_not_read_env_for_audience(self):
        import inspect
        import er063_family_z_audio_01 as z
        import er019_family_x_audio_production_runner_01 as x
        import er121_family_y_runner_01 as yr
        import er121_family_y_audio_01 as ya
        for fn in (z.build_pages, z._user_page_rows, x.build_player_html, x._build_level_table, ya.build_page_rows, ya.render_y_page, ya.page_legend_html):
            self.assertEqual(inspect.signature(fn).parameters["audience"].default, "public", fn.__name__)
        self.assertEqual(yr.YContext().page_audience, "public")
        for fn in ("er_user_listening_page_common_01.py", "er121_family_y_runner_01.py"):
            src = open(os.path.join(ROOT, fn), encoding="utf-8").read()
            self.assertNotRegex(src, r"os\.environ[^\n]*(AUDIENCE|CHUNK_MARKER)", fn)       # env/設定での暗黙ONなし


class ZWiring(unittest.TestCase):
    def test_z_user_page_rows_dev_marks_only_real_chunk_boundaries(self):
        import numpy as np
        import soundfile as sf
        import er063_family_z_audio_01 as z
        with tempfile.TemporaryDirectory() as run:
            os.makedirs(f"{run}/b1b/assembly")
            os.makedirs(f"{run}/b1b/audit")
            wav = os.path.join(run, "unused.wav")
            sf.write(wav, np.zeros(48000, dtype="float32"), 24000)
            json.dump({"wav": wav}, open(f"{run}/b1b/assembly/timeline.json", "w", encoding="utf-8"))
            json.dump({"key_phrases": {}}, open(f"{run}/b1b/audit/tts_generation_results.json", "w", encoding="utf-8"))
            plan = {"chunked": True, "chunks": [{"text": c} for c in CHUNKS3]}
            json.dump({"plans": {"full_story_part1_c1": plan, "full_story_part1_c2": {"chunked": False, "chunks": []}}},
                      open(f"{run}/b1b/audit/chunk_plan_b1b.json", "w", encoding="utf-8"))
            outdir = os.path.join(run, "out")
            os.makedirs(outdir)
            rows = [{"part": "full_story_part1_c1", "clip_id": "full_story_part1_c1", "start": 0.0, "dur": 1.0, "file": "a.mp3", "voice": "Charon", "script": SCRIPT},
                    {"part": "full_story_part1_c2", "clip_id": "full_story_part1_c2", "start": 1.0, "dur": 1.0, "file": "b.mp3", "voice": "Charon", "script": "Single para."}]
            pub = z._user_page_rows(run, "b1b", rows, [], "a/", outdir)
            dev = z._user_page_rows(run, "b1b", rows, [], "a/", outdir, "dev")
            self.assertEqual(cp.count_chunk_markers("".join(b for r in pub for b in r["blocks"])), 0)
            self.assertEqual(cp.count_chunk_markers("".join(b for r in dev for b in r["blocks"])), 2)     # 3 chunk=境界2。単一段落clipは0


if __name__ == "__main__":
    unittest.main()
