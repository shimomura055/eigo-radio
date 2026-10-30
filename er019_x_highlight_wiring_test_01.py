# -*- coding: utf-8 -*-
"""SLOT-23-CONSUMER-DESIGN-01 委任_04C: Family X配線のtest(API 0、mockのみ)。

- 本文ハイライト(player): display_spec付きrunだけ装飾+③訳リスト+凡例+CSS、無いrun=従来とバイト同一(実run `boredom_aggression__run_bape_01` のgolden sha)
- 表示範囲に「In one line」を含む(Full Story外の語句もISSUEにしない)、解決不能はHighlightStop(ページ生成前STOP)
- Std Part 1: level引数化(b1b/a2相互独立)、part1_enabled(Adv常に/Stdはdisplay_spec付きのみ)、Part 1ブロックちょうど1個(0・2個=STOP)、判断記録なし=STOP
- 標準公開builder: 検査PASSでのみ出力、AI島固有文言なし、display_specなし=ハイライト無し
- 旧per-article scriptのguard(display_spec付きrunでSTOP、旧runは素通し)
- 旧経路撤去: Part 1系関数内に"b1b"リテラルが既定引数以外で0件(AST)
実行: .venv\\Scripts\\python.exe -m unittest er019_x_highlight_wiring_test_01"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import er019_family_x_audio_production_runner_01 as R
import er019_family_x_listening_page_01 as B
import er_learning_highlight_01 as hl
import er_user_listening_page_common_01 as uc
from er_learning_highlight_test_01 import mini

ROOT = os.path.dirname(os.path.abspath(__file__))
FX = os.path.join(ROOT, "docs", "research", "SLOT-23-CONSUMER-DESIGN-01", "fixtures")
SPEC = "LEARNING_ITEMS_123_V1"
# 旧(変更前)runner/playerで生成した実run(boredom_aggression__run_bape_01)のplayer.html(正規化後)sha256。変更前後でバイト同一であること。
GOLDEN_BAPE_PLAYER_SHA = "6a60daf08482a2e7794ef7b09d03e7408b12ca793f87defc2a714067158a4151"
BAPE_RUN = os.path.join(ROOT, "er019_output", "family_x_audio_production_wiring_01", "boredom_aggression__run_bape_01")


def _rj(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def _wj(p, obj):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)


def make_run(tmp: str, *, spec: bool, assembled: bool = True, wav: bool = False):
    """AI島fixtures(a2/b1b)から、player/builderが読むXのrun dirとsource_dirを作る。specならdisplay_spec付きレコード。"""
    out = os.path.join(tmp, "runs", "ai_island_temple__run_t")
    src = os.path.join(tmp, "src", "ai_island_temple", "run_t")
    _wj(os.path.join(out, "entry_point.json"), {"source_dir": src})
    for lv in ("a2", "b1b"):
        fx = os.path.join(FX, f"ai_island_{lv}")
        os.makedirs(os.path.join(src, lv), exist_ok=True)
        shutil.copy(os.path.join(fx, "article.md"), os.path.join(src, lv, "article.md"))
        parts = _rj(os.path.join(fx, "parts.json"))
        _wj(os.path.join(out, lv, "parts.json"), parts)
        kp = os.path.join(out, lv, "key_phrases")
        os.makedirs(kp, exist_ok=True)
        shutil.copy(os.path.join(fx, "kp_candidates.json"), os.path.join(kp, "kp_candidates.json"))
        rec = _rj(os.path.join(fx, "confirmed_selection.json"))
        if spec:
            rec["display_spec"] = SPEC
        _wj(os.path.join(kp, "confirmed_selection.json"), rec)
        kp_items = [{"rank": 1, "used_form": "carry over", "japanese_gloss": "引き継ぐ", "display_phrase": "carried over"}]
        _wj(os.path.join(kp, "keywords_canonicalized.json"), {"items": kp_items})
        _wj(os.path.join(out, lv, "b1_support_texts.json" if lv == "b1b" else "a2_support_texts.json"),
            {"preview": "Preview text here.", "comment_1": "Comment one.", "comment_2": "c2", "comment_3": "c3", "comment_4": "c4"})
        if lv == "b1b":
            _wj(os.path.join(out, lv, "audit", "tts_generation_results.json"), {"key_phrases": {"1": {"explanation": {"explanation_text": "explain carry over"}}}})
        timeline = []
        t = 0.0
        for label in ("Topic intro", "Preview", "Key Phrase 1", "Full Story Part 1 (Voice)", "Full Story Part 2 (Voice)", "Full Story Part 3 (Voice)", "Comment 1", "In One Line"):
            timeline.append({"part": label, "start_seconds": t, "duration_seconds": 1.0})
            t += 1.0
        _wj(os.path.join(out, lv, "audit", "timeline.json"), timeline)
        wavp = os.path.join(out, lv, "assembled", "episode.wav")
        if wav:
            import numpy as np
            import soundfile as sf
            os.makedirs(os.path.dirname(wavp), exist_ok=True)
            sf.write(wavp, np.zeros(int(24000 * t), dtype="float32"), 24000)
        _wj(os.path.join(out, lv, "run_summary_assemble.json"),
            {"status": "OK" if assembled else "NG", "out_path": wavp, "duration_seconds": t, "peak": 0.5, "clipping_detected": False})
    return out, src


class _Tmp(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="x_hl_wiring_")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)


class PlayerHighlight(_Tmp):
    def test_spec_run_decorates_and_lists_meanings(self):
        out, src = make_run(self.tmp, spec=True)
        self.assertTrue(R.x_display_spec(out, "a2"))
        res = {lv: R.resolve_x_highlights(out, lv) for lv in ("b1b", "a2")}
        for lv in res:
            self.assertEqual(res[lv]["issues"], [])
        p = R.build_player_html(out, "t", None)
        t = open(p, encoding="utf-8").read()
        self.assertIn('class="lk1"', t)
        self.assertIn('class="lk2"', t)
        self.assertIn('class="lk3"', t)
        self.assertIn(hl.HIGHLIGHT_CSS, t)                      # PLAYER_STANDARD_CSS_WITH_HIGHLIGHT
        self.assertIn('class="lk-legend"', t)                   # 凡例は台本表の外
        self.assertIn('<ul class="lk-meaning">', t)             # ③訳リスト
        self.assertNotIn("title=", re.sub(r"<title>.*?</title>", "", t))   # ③のtitle属性なし
        self.assertEqual(uc.count_chunk_markers(t), 0)          # public: ⏸ 0
        # G3(装飾・③訳・本文不変・public混入)が両levelでPASS、Part 1検査はこのmockでは別
        for lv in ("b1b", "a2"):
            sec = R.player_level_section(t, lv)
            import er128_kp_highlight_01 as g3
            g = g3.verify_highlights(sec, {"result": res[lv], "audience": "public"})
            self.assertEqual(g["status"], "PASS", g["problems"])

    def test_body_text_unchanged_after_stripping_decoration(self):
        out, _src = make_run(self.tmp, spec=True)
        res = R.resolve_x_highlights(out, "b1b")
        parts = _rj(os.path.join(out, "b1b", "parts.json"))
        cell = R.x_script_cell_html(parts["part2"], "full_story_part2", res)
        import html
        body = cell.split('<ul class="lk-meaning">')[0]          # 本文部分(③訳リストは本文の外)
        plain = re.sub(r"<[^>]+>", "", hl.strip_decoration(body))
        self.assertEqual(html.unescape(plain), parts["part2"])
        self.assertIn("lk1", cell)

    def test_no_display_spec_is_conventional_and_byte_identical(self):
        out, _src = make_run(self.tmp, spec=False)
        self.assertIsNone(R.x_display_spec(out, "a2"))
        self.assertIsNone(R.resolve_x_highlights(out, "b1b"))
        auto = open(R.build_player_html(out, "t", None), encoding="utf-8").read()
        explicit = open(R.build_player_html(out, "t", None, highlights_by_level={"b1b": None, "a2": None}), encoding="utf-8").read()
        self.assertEqual(auto, explicit)
        self.assertNotIn("lk1", auto)
        self.assertNotIn("lk-meaning", auto)
        self.assertNotIn(hl.HIGHLIGHT_CSS, auto)
        self.assertIn(R.player_common.PLAYER_STANDARD_CSS, auto)

    @unittest.skipUnless(os.path.isdir(BAPE_RUN), "実run(bape)が無い環境")
    def test_golden_existing_run_player_byte_identical_to_before_change(self):
        tmp = os.path.join(self.tmp, "bape")
        for dp, _dn, fn in os.walk(BAPE_RUN):
            for f in fn:
                if f.endswith((".json", ".md", ".jsonl")) and os.path.getsize(os.path.join(dp, f)) < 5_000_000:
                    rel = os.path.relpath(os.path.join(dp, f), BAPE_RUN)
                    os.makedirs(os.path.dirname(os.path.join(tmp, rel)), exist_ok=True)
                    shutil.copy(os.path.join(dp, f), os.path.join(tmp, rel))
        p = R.build_player_html(tmp, "boredom_aggression", None, study_html="", study_html_a2="", audience="public")
        t = open(p, encoding="utf-8").read().replace(R.player_common.abs_file_url(tmp), "<RUN>")
        self.assertEqual(hashlib.sha256(t.encode("utf-8")).hexdigest(), GOLDEN_BAPE_PLAYER_SHA)

    def test_unresolvable_stops_before_player(self):
        out, src = make_run(self.tmp, spec=True)
        with open(os.path.join(src, "b1b", "article.md"), "a", encoding="utf-8") as f:
            f.write("\nA changed sentence.\n")        # 候補生成後に本文が変わった(text_sha256不一致)
        with self.assertRaises(R.HighlightStop) as cm:
            R.resolve_x_highlights(out, "b1b")
        self.assertIn("HL_TEXT_SHA_MISMATCH", str(cm.exception))
        self.assertIn("X_HIGHLIGHT_UNRESOLVED", str(cm.exception))
        with self.assertRaises(R.HighlightStop):
            R.build_player_html(out, "t", None)
        self.assertFalse(os.path.exists(os.path.join(out, "player.html")))

    def test_dev_marker_outside_decoration(self):
        out, _src = make_run(self.tmp, spec=True)
        res = R.resolve_x_highlights(out, "b1b")
        parts = _rj(os.path.join(out, "b1b", "parts.json"))
        text = parts["part2"]
        mid = text.index(". ") + 2
        chunks = [text[:mid], text[mid:]]
        cell = R.x_script_cell_html(text, "full_story_part2", res, chunk_texts=chunks, audience="dev")
        self.assertEqual(cell.count(uc.CHUNK_MARKER_ENTITY), 1)
        pub = R.x_script_cell_html(text, "full_story_part2", res, chunk_texts=chunks, audience="public")
        self.assertEqual(pub.count(uc.CHUNK_MARKER_ENTITY), 0)
        self.assertNotIn("chunk-mark", pub)

    def test_unit_keys_include_in_one_line(self):
        parts = _rj(os.path.join(FX, "ai_island_b1b", "parts.json"))
        keys = [u["key"] for u in R.x_display_units(parts)]
        self.assertEqual(keys, ["full_story_part1", "full_story_part2", "full_story_part3", "in_one_line"])

    def test_in_one_line_only_phrase_resolves_with_in_one_line_unit_but_not_without(self):
        article = ("# Title\n\nFirst para sentence one. First para sentence two.\n\nSecond para sentence one. Second para sentence two.\n\n"
                   "Third para sentence one. Third para sentence two.\n\n## In one line\nCosts rose year over year in the sector.\n")
        doc, items = mini(article, [("c1", 1, "year over year", "前年比で")])
        parts = {"part1": "First para sentence one. First para sentence two.", "part2": "Second para sentence one. Second para sentence two.",
                 "part3": "Third para sentence one. Third para sentence two.", "in_one_line": "Costs rose year over year in the sector."}
        units = R.x_display_units(parts)
        ok = hl.resolve_highlights(article, doc, items, units)
        self.assertEqual(ok["status"], "OK", ok["issues"])
        self.assertEqual([p["unit_key"] for p in ok["highlights"][0]["pieces"]], ["in_one_line"])
        ng = hl.resolve_highlights(article, doc, items, units[:3])   # 旧(Full Storyのみ)の表示範囲
        self.assertEqual(ng["status"], "ISSUE")
        cell = R.x_script_cell_html(parts["in_one_line"], "in_one_line", ok)
        self.assertIn('<strong class="lk1" data-hl="c1">year over year</strong>', cell)


class PlayerVerify(_Tmp):
    """player生成後の検査(verify_x_player): 表示有効(display_spec付き)levelだけ G3 + Part 1ちょうど1個。マーク無し=何もしない。"""

    def _player(self, spec, p1_count):
        out, _src = make_run(self.tmp, spec=spec)
        blk = f"<section class='study'>{R.PART1_HEADING_MARK}<div>x</div></section>" * p1_count
        hres = R.resolve_x_highlights_for_levels(out, ["a2", "b1b"], source_dir=_src)
        path = R.build_player_html(out, "t", None, study_html=blk, study_html_a2=blk, highlights_by_level=hres)
        return out, path, hres

    def test_pass_when_part1_exactly_one_and_g3_ok(self):
        out, path, hres = self._player(True, 1)
        R.verify_x_player(out, path, ["a2", "b1b"], hres)      # 例外なし

    def test_part1_zero_or_two_is_stop(self):
        for n in (0, 2):
            tmp = tempfile.mkdtemp(prefix="x_hl_pv_")
            self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
            out, _src = make_run(tmp, spec=True)
            hres = R.resolve_x_highlights_for_levels(out, ["a2", "b1b"], source_dir=_src)
            blk = f"<section class='study'>{R.PART1_HEADING_MARK}</section>" * n
            path = R.build_player_html(out, "t", None, study_html=blk, study_html_a2=blk, highlights_by_level=hres)
            with self.assertRaises(RuntimeError) as cm:
                R.verify_x_player(out, path, ["a2", "b1b"], hres)
            self.assertIn("X_PART1_BLOCK_COUNT", str(cm.exception))

    def test_missing_decoration_fails_g3(self):
        out, path, hres = self._player(True, 1)
        t = open(path, encoding="utf-8").read()
        t2 = t.replace('<strong class="lk1" data-hl=', '<strong class="zz" data-hl=', 1)     # 装飾が1つ壊れた
        with open(path, "w", encoding="utf-8") as f:
            f.write(t2)
        with self.assertRaises(RuntimeError) as cm:
            R.verify_x_player(out, path, ["a2", "b1b"], hres)
        self.assertIn("X_HIGHLIGHT_G3_FAIL", str(cm.exception))

    def test_unmarked_run_is_noop_even_without_part1(self):
        out, path, hres = self._player(False, 0)
        self.assertEqual(hres, {"b1b": None, "a2": None})
        R.verify_x_player(out, path, ["a2", "b1b"], hres)      # マーク無し旧run=従来どおり(Part 1ゼロでも止めない)


class Part1Level(_Tmp):
    def test_part1_enabled_adv_always_std_only_with_display_spec(self):
        out_spec, _ = make_run(os.path.join(self.tmp, "a"), spec=True)
        out_old, _ = make_run(os.path.join(self.tmp, "b"), spec=False)
        self.assertEqual(R.part1_levels(out_spec, ["b1b", "a2"]), ["b1b", "a2"])
        self.assertEqual(R.part1_levels(out_old, ["b1b", "a2"]), ["b1b"])      # マーク無し旧run=Stdは従来どおりPart 1なし
        self.assertTrue(R.part1_enabled(out_old, "b1b"))
        self.assertFalse(R.part1_enabled(out_old, "a2"))

    def test_generate_part1_all_passes_level_and_uses_level_dirs(self):
        out, src = make_run(self.tmp, spec=True)
        calls = []

        class FakeP1:
            KpGeneralExplanationError = type("E1", (Exception,), {})
            KpGeneralExplanationInputError = type("E2", (Exception,), {})
            EXPLANATIONS_FILENAME = "kp_general_explanations.json"

            @staticmethod
            def resolve_general_explanations(items, cached, *, call_fn=None, client=None, level="b1b"):
                calls.append(("expl", level))
                return {"level": level, "reused_from_previous_run": False, "audit": {"total_cost_jpy": 0.1}}

        class FakeJa:
            KpSourceSentenceJaError = type("E3", (Exception,), {})
            KpSourceSentenceJaInputError = type("E4", (Exception,), {})
            TRANSLATIONS_FILENAME = "kp_source_sentence_ja.json"

            @staticmethod
            def resolve_translations(items, cached, *, call_fn=None, client=None, article_text=""):
                calls.append(("ja", len(article_text)))
                return {"reused_from_previous_run": False, "audit": {"total_cost_jpy": 0.03}}

        with mock.patch.object(R, "_part1_gen", return_value=FakeP1), mock.patch.object(R, "_part1_ja_gen", return_value=FakeJa), \
                mock.patch.object(R, "_part1_kp_items", return_value=[{"rank": 1}]):
            r = R.generate_part1_all(None, src, out, level="a2")
            self.assertEqual(r["status"], "OK")
            self.assertEqual(calls[0], ("expl", "a2"))
            self.assertTrue(os.path.exists(os.path.join(out, "a2", "key_phrases", "kp_general_explanations.json")))
            self.assertTrue(os.path.exists(os.path.join(out, "a2", "key_phrases", "kp_source_sentence_ja.json")))
            self.assertFalse(os.path.exists(os.path.join(out, "b1b", "key_phrases", "kp_general_explanations.json")))   # level相互独立
            # 訳の本文は {source_dir}/a2/article.md(b1bの本文ではない)
            self.assertEqual(calls[1][1], len(open(os.path.join(src, "a2", "article.md"), encoding="utf-8").read()))

    def test_failure_marker_and_next_command_are_level_specific(self):
        out, src = make_run(self.tmp, spec=True)

        class FakeP1:
            class KpGeneralExplanationError(Exception):
                pass
            KpGeneralExplanationInputError = type("E2", (Exception,), {})
            EXPLANATIONS_FILENAME = "kp_general_explanations.json"

            @staticmethod
            def resolve_general_explanations(*a, **k):
                raise FakeP1.KpGeneralExplanationError("boom")

        with mock.patch.object(R, "_part1_gen", return_value=FakeP1), mock.patch.object(R, "_part1_kp_items", return_value=[{"rank": 1}]):
            r = R.generate_part1(None, src, out, level="a2")
        self.assertTrue(r["status"].startswith("KP_PART1_FAILED"))
        mk = R._part1_failed_markers(out, ["b1b", "a2"])
        self.assertEqual(len(mk), 1)
        self.assertIn("/a2/", mk[0].replace("\\", "/"))
        d = _rj(mk[0])
        self.assertIn("--level a2", d["next_command"])
        self.assertIn("--level a2", R.part1_next_command(src, "a2"))
        self.assertIn("--level b1b", R.part1_next_command(src))

    def test_part1_block_count_exactly_one(self):
        one = f"<div>{R.PART1_HEADING_MARK}</div>"
        self.assertEqual(R.validate_part1_block_count(one, "b1b"), 1)
        for bad in ("<div></div>", one + one):
            with self.assertRaises(RuntimeError) as cm:
                R.validate_part1_block_count(bad, "a2")
            self.assertIn("X_PART1_BLOCK_COUNT", str(cm.exception))

    def test_no_b1b_literal_in_part1_functions_except_defaults(self):
        tree = ast.parse(open(os.path.join(ROOT, "er019_family_x_audio_production_runner_01.py"), encoding="utf-8").read())
        names = {"_part1_explanations_path", "_part1_failed_markers", "part1_next_command", "_part1_kp_items", "_part1_ja_path", "generate_part1_ja",
                 "_require_part1_ja_fresh_x", "generate_part1", "generate_part1_all", "assemble_part1_x", "_require_part1_fresh_x",
                 "run_study_text_stage", "part1_study_html_for_player", "part1_enabled", "part1_levels", "x_display_spec"}
        found = set()
        for fn in [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name in names]:
            found.add(fn.name)
            default_ids = {id(d) for d in fn.args.defaults + fn.args.kw_defaults if d is not None}
            for node in ast.walk(fn):
                if isinstance(node, ast.Constant) and node.value == "b1b" and id(node) not in default_ids:
                    self.fail(f"{fn.name}: 既定引数以外に \"b1b\" リテラル (line {node.lineno})")
        self.assertEqual(found, names)
        src = open(os.path.join(ROOT, "er019_family_x_audio_production_runner_01.py"), encoding="utf-8").read()
        for old in ("generate_part1_for_b1b", "generate_part1_ja_for_b1b", "generate_part1_all_for_b1b", "assemble_part1_for_b1b"):
            self.assertNotIn(old, src)                       # 互換別名なし

    def test_player_main_flow_uses_level_helpers(self):
        src = open(os.path.join(ROOT, "er019_family_x_audio_production_runner_01.py"), encoding="utf-8").read()
        self.assertIn("for _lv1 in part1_levels(out_dir, levels):", src)
        self.assertIn("compose_page_html(_part1_htmls.get(\"a2\", \"\")", src)


class StandardBuilder(_Tmp):
    def _study(self, with_part1_for, count=1):
        def fake(run, article_text, *, level, next_command="--stage study_text"):
            blk = (f"<section class='study'>{R.PART1_HEADING_MARK}<div>x</div></section>" * count) if level in with_part1_for else ""
            return blk + "<section class='study'><h3>Grammar &amp; Sentence Structure</h3><div>g</div></section>"
        return fake

    def _build(self, out_tmp, *, spec, part1_levels, count=1, p1_vocab=None):
        out, src = make_run(out_tmp, spec=spec, wav=True)
        web = os.path.join(out_tmp, "web")
        runs = os.path.dirname(out)
        slug_run = os.path.basename(out).split("__")
        with mock.patch("er120_part2_wiring_01.public_study_html", self._study(part1_levels, count)), \
                mock.patch("er120_part2_wiring_01.verify_outputs", return_value=None):
            return web, B.build_page(slug_run[0], slug_run[1], web, run_root=runs,
                                     source_root=os.path.join(out_tmp, "src"), ja_title="AI島の発見")

    def test_spec_run_builds_page_with_highlights_part1_once_per_vocab_level(self):
        web, s = self._build(self.tmp, spec=True, part1_levels=("a2", "b1b"))
        page = open(os.path.join(web, "index.html"), encoding="utf-8").read()
        self.assertEqual(s["marked_levels"], ["a2", "b1b"])
        self.assertEqual(s["vocab_levels"], ["a2", "b1b"])
        for lid in ("std", "adv"):
            sec = uc.level_section_html(page, lid)
            self.assertEqual(sec.count(R.PART1_HEADING_MARK), 1)
            self.assertIn("lk1", sec)
            self.assertIn("lk-meaning", sec)
            _pos = [sec.index(m) for m in (R.PART1_HEADING_MARK, "Grammar &amp; Sentence Structure") if m in sec]
            self.assertEqual(_pos, sorted(_pos))   # Part 1 → Part 2(存在するブロック同士の相対順。文法0件でもValueErrorにならない。M-5)
        self.assertIn(hl.HIGHLIGHT_CSS, page)
        self.assertEqual(uc.check_page(page, base_dir=web)["overall"], "PASS")
        self.assertNotIn("後続反映予定", page)                        # AI島固有文言なし
        self.assertTrue(os.path.exists(os.path.join(web, "audio", "ai_island_temple_standard.mp3")))

    def test_part1_zero_or_two_blocks_stop_and_no_index(self):
        for count, levels in ((0, ("a2", "b1b")), (2, ("a2", "b1b"))):
            tmp = tempfile.mkdtemp(prefix="x_hl_b_")
            self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
            with self.assertRaises(B.PageStop) as cm:
                self._build(tmp, spec=True, part1_levels=levels, count=count)
            self.assertIn("X_PART1_BLOCK_COUNT", str(cm.exception))
            self.assertFalse(os.path.exists(os.path.join(tmp, "web", "index.html")))

    def test_unmarked_run_has_no_highlight_and_no_std_part1(self):
        web, s = self._build(self.tmp, spec=False, part1_levels=("b1b",))
        page = open(os.path.join(web, "index.html"), encoding="utf-8").read()
        self.assertEqual(s["marked_levels"], [])
        self.assertEqual(s["vocab_levels"], ["b1b"])
        self.assertNotIn("lk1", page)
        self.assertNotIn(hl.HIGHLIGHT_CSS, page)
        self.assertNotIn("lk-legend", page)
        self.assertEqual(uc.level_section_html(page, "std").count(R.PART1_HEADING_MARK), 0)
        self.assertEqual(uc.level_section_html(page, "adv").count(R.PART1_HEADING_MARK), 1)

    def test_unmarked_std_with_part1_block_is_stop(self):
        tmp = tempfile.mkdtemp(prefix="x_hl_b_")
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        with self.assertRaises(B.PageStop) as cm:
            self._build(tmp, spec=False, part1_levels=("a2", "b1b"))
        self.assertIn("X_PAGE_PART1_UNEXPECTED", str(cm.exception))
        self.assertFalse(os.path.exists(os.path.join(tmp, "web", "index.html")))

    def test_unresolvable_highlight_stops_before_any_output(self):
        out, src = make_run(self.tmp, spec=True, wav=True)
        with open(os.path.join(src, "a2", "article.md"), "a", encoding="utf-8") as f:
            f.write("\nChanged.\n")
        web = os.path.join(self.tmp, "web")
        with mock.patch("er120_part2_wiring_01.public_study_html", self._study(("a2", "b1b"))), \
                mock.patch("er120_part2_wiring_01.verify_outputs", return_value=None):
            with self.assertRaises(B.PageStop) as cm:
                B.build_page("ai_island_temple", "run_t", web, run_root=os.path.dirname(out), source_root=os.path.join(self.tmp, "src"), ja_title="x")
        self.assertIn("HL_TEXT_SHA_MISMATCH", str(cm.exception))
        self.assertFalse(os.path.exists(os.path.join(web, "index.html")))
        self.assertFalse(os.path.exists(web) and os.listdir(web))      # 音声も書かない

    def test_wrapper_delegates_to_standard_builder(self):
        src = open(os.path.join(ROOT, "tools", "build_aif3_listening_page_01.py"), encoding="utf-8").read()
        self.assertIn("er019_family_x_listening_page_01", src)
        self.assertNotIn("後続反映予定", src)
        self.assertNotIn("後続反映予定", open(os.path.join(ROOT, "er019_family_x_listening_page_01.py"), encoding="utf-8").read().split('"""', 2)[2])


class Guard(_Tmp):
    def _run_py(self, code: str):
        return subprocess.run([sys.executable, "-I", "-c", "import sys; sys.path.insert(0, %r); " % ROOT + code], capture_output=True, text=True,
                              encoding="utf-8", errors="replace", cwd=self.tmp)

    def test_display_spec_run_is_stopped_when_old_script_reads_inputs(self):
        out, _src = make_run(self.tmp, spec=True)
        r = self._run_py(f"import er019_x_page_guard_01; open({os.path.join(out, 'b1b', 'parts.json')!r}).read()")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("X_PAGE_GUARD_DISPLAY_SPEC_RUN", r.stderr)

    def test_legacy_run_passes_through(self):
        out, _src = make_run(self.tmp, spec=False)
        r = self._run_py(f"import er019_x_page_guard_01; open({os.path.join(out, 'b1b', 'parts.json')!r}, encoding='utf-8').read(); print('PASSED')")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("PASSED", r.stdout)

    def test_all_old_scripts_import_guard_once_and_standard_builder_does_not(self):
        olds = [f for f in os.listdir(ROOT) if re.fullmatch(r"er019_.*page.*\.py", f) and f not in ("er019_x_page_guard_01.py", "er019_family_x_listening_page_01.py")]
        self.assertEqual(len(olds), 14)
        for f in olds:
            self.assertEqual(open(os.path.join(ROOT, f), encoding="utf-8").read().count("import er019_x_page_guard_01"), 1, f)
        self.assertNotIn("er019_x_page_guard_01", open(os.path.join(ROOT, "er019_family_x_listening_page_01.py"), encoding="utf-8").read().split('"""', 2)[2])

    def test_nws2_script_stops_for_display_spec_run(self):
        out, _src = make_run(self.tmp, spec=True)
        r = subprocess.run([sys.executable, os.path.join(ROOT, "er019_nws2_final_page_01.py"), "--audio-dir", out, "--out", os.path.join(self.tmp, "o"),
                            "--tag", "t", "--title-ja", "t"], capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=ROOT)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("X_PAGE_GUARD_DISPLAY_SPEC_RUN", r.stderr)
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "o", "index.html")))

    def test_nws2_calls_study_html_with_explicit_level(self):
        src = open(os.path.join(ROOT, "er019_nws2_final_page_01.py"), encoding="utf-8").read()
        self.assertIn('study_html_for_audio_dir(pp.RUN, level="b1b")', src)


class DefaultOffIsolation(unittest.TestCase):
    def test_no_flag_or_env_path_to_enable_display(self):
        src = open(os.path.join(ROOT, "er019_family_x_audio_production_runner_01.py"), encoding="utf-8").read()
        a = src.index("# SLOT-23 委任_04C: 学習項目①②③の本文ハイライト")
        blk = src[a:a + 9000]
        self.assertNotIn("os.environ", blk)
        self.assertNotIn("getenv", blk)
        self.assertNotIn("EIGO_", blk)
        g = open(os.path.join(ROOT, "er019_x_page_guard_01.py"), encoding="utf-8").read()
        self.assertNotIn("os.environ", g)
        self.assertNotIn("getenv", g)
        # マーク発行(new_review接続)はしない: runner/builder/guardに display_spec を書き込むコードがない
        for name in ("er019_family_x_audio_production_runner_01.py", "er019_family_x_listening_page_01.py", "er019_x_page_guard_01.py"):
            s = open(os.path.join(ROOT, name), encoding="utf-8").read()
            self.assertIsNone(re.search(r"\[[\"']display_spec[\"']\]\s*=", s), name)
            self.assertNotIn("issue_std_part1_mark", s)


if __name__ == "__main__":
    unittest.main()
