# -*- coding: utf-8 -*-
"""SLOT-23-CONSUMER-DESIGN-01 委任_04E(E班): Family Z の本文ハイライト(①二重下線/②下線/③下線+訳リスト)・Std Part 1 stage level化・Validator・page_verify G3 の配線test。
API 0(LLM・TTS・ASR・ネットワークを呼ばない。mock/合成データのみ)。実run(wav含む)に依存するtestは、無ければskipする。
実行: py -3 -m unittest er026_z_highlight_wiring_test_01 -v"""
from __future__ import annotations

import ast
import contextlib
import hashlib
import inspect
import json
import os
import re
import shutil
import tempfile
import types
import unittest
from unittest import mock

import er026_family_z_fiction_production_runner_01 as r
import er063_family_z_audio_01 as a63
import er_learning_highlight_01 as hl
import er_user_listening_page_common_01 as cp
from er119_test_support_01 import _legacy_patch  # noqa: E402  (旧マーク無し記事の再現。SLOT-23 委任_05M)

ROOT = os.path.dirname(os.path.abspath(__file__))
RUN_KCP4 = os.path.join(ROOT, "er026_output/family_z_production_e2e_01/melos/run_kcp4_ev_z_01")           # 確定レコードあり(display_specなし)の実Z run(a2/b1b)
RUN_LEGACY = os.path.join(ROOT, "er026_output/family_z_production_e2e_01/melos/run_p2_evidence_r3")       # 旧run(マーク無し)
V1 = "LEARNING_ITEMS_123_V1"
BANNED = re.compile(r"英語:|日本語:|EN:|JA:")

# 変更前(委任_04E着手前、commit 374cfc941)の build_pages 出力sha256(run_p2_evidence_r3、page_title="t"、audio_file_prefix="Melos"、public)。
GOLDEN_LEGACY = {
    "advanced.html": "9fcd37832cd238397d66d9cf65ef06487d226acf9212732780ad4b274ce7a102",
    "index.html": "c7a806771a805119d6c470e8edac92bb1beae17be1786244e152a65c40605912",
    "standard.html": "82a43fd3a74f4e30d10be9039b68b763afa06cc2570a7bfed60afd423056f06a",
}


def _sf():
    import numpy as np
    import soundfile as sf
    return np, sf


def make_run(tmp: str, level: str, clips: dict) -> str:
    """合成のZ run: <run>/<level>/assembly/timeline.json(+短いwav)と audit/tts_generation_results.json。clips={clip_id: canonical_text}(公開順)。"""
    np, sf = _sf()
    run = f"{tmp}/run"
    os.makedirs(f"{run}/{level}/assembly", exist_ok=True)
    os.makedirs(f"{run}/{level}/audit", exist_ok=True)
    wav = f"{run}/{level}/assembly/x.wav"
    sf.write(wav, np.zeros(16000 * 2, dtype="float32"), 16000)
    tl = {"wav": wav, "duration_seconds": 2.0,
          "timeline": [{"part": cid, "start_seconds": 0.1 * i, "duration_seconds": 0.1} for i, cid in enumerate(clips)]}
    with open(f"{run}/{level}/assembly/timeline.json", "w", encoding="utf-8") as f:
        json.dump(tl, f)
    with open(f"{run}/{level}/audit/tts_generation_results.json", "w", encoding="utf-8") as f:
        json.dump({"segments": {cid: {"canonical_text": t, "voice": "V"} for cid, t in clips.items()}}, f, ensure_ascii=False)
    return run


def mini(article: str, items: list):
    """合成の候補doc+items(文ID・出現を実際に計算)。items=[(cid, category, span, gloss)]"""
    import er105_kp_fulltext_selector_01 as sel
    us = hl.split_sentence_units(article)
    cands = []
    for cid, _cat, span, _gl in items:
        hits = [(i, u) for i, u in enumerate(us) if sel._phrase_pattern(span).search(u["raw_text"])]
        i0, u0 = hits[0]
        cands.append({"candidate_id": cid, "source_sentence": u0["raw_text"], "source_sentence_id": f"S{i0 + 1}",
                      "item": {"source_span": span, "occurrence_sentence_ids": [f"S{i + 1}" for i, _ in hits]}})
    doc = {"text_sha256": hl.sha256_text(article), "candidates": cands, "candidates_sha256": "c" * 64}
    its = [{"candidate_id": cid, "category": cat, "used_form": span, "japanese_gloss": gl} for cid, cat, span, gl in items]
    return doc, its


CLIP1 = "The knight rode far. He carried over the gift of kindness to a village."
CLIP2 = "A shepherd waited there. Silence fell across the valley."
CLIP3 = "At last the rain stopped."
CLIPS = {"full_story_part1_c1": CLIP1, "full_story_part1_c2": CLIP2, "full_story_part2_c1": CLIP3}
# クリップ1の末尾とクリップ2の頭にまたがる語句を作るため、別の分割も用意する
SPLIT = {"full_story_part1_c1": "The knight rode far. He carried over the gift", "full_story_part1_c2": "of kindness to a village. A shepherd waited there. Silence fell across the valley.",
         "full_story_part2_c1": CLIP3}


def article_of(clips: dict) -> str:
    return " ".join(clips.values())


def rows_of(run: str, level: str, clips: dict) -> list:
    return [{"part": cid, "clip_id": cid, "start": 0.1 * i, "dur": 0.1, "file": f"audio/{level}_{i:02d}.mp3", "voice": "V", "style": "-", "script": t, "notes": []}
            for i, (cid, t) in enumerate(clips.items())]


def user_rows(run, level, rows, out, **kw):
    os.makedirs(out, exist_ok=True)
    return a63._user_page_rows(run, level, rows, [], "audio/", out, **kw)


class TmpMixin:
    def new_tmp(self):
        t = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, t, True)
        return t


# ============================================================
# 1. er063: 表示単位・描画(合成データ、高速)
# ============================================================
class DisplayUnitsAndRowsTest(TmpMixin, unittest.TestCase):
    def test_full_story_display_units_are_part_grouped_in_order(self):
        run = make_run(self.new_tmp(), "a2", CLIPS)
        units = a63.full_story_display_units(run, "a2")
        self.assertEqual(units, [{"key": "full_story_part1", "texts": [CLIP1, CLIP2], "joiner": " "}, {"key": "full_story_part2", "texts": [CLIP3], "joiner": " "}])

    def test_no_highlights_is_byte_identical_to_plain_script_blocks(self):
        tmp = self.new_tmp()
        run = make_run(tmp, "a2", CLIPS)
        rows = rows_of(run, "a2", CLIPS)
        base = user_rows(run, "a2", rows, f"{tmp}/o1")
        same = user_rows(run, "a2", rows, f"{tmp}/o2", highlights=None)
        self.assertEqual(base, same)
        fs = [x for x in base if x["part"].startswith("Full Story Part 1")][0]
        self.assertEqual(fs["blocks"], [f"<div class='script'>{cp.esc(CLIP1)}</div>", f"<div class='script'>{cp.esc(CLIP2)}</div>"])

    def _hl(self, clips, items):
        art = article_of(clips)
        cands, its = mini(art, items)
        units = [{"key": "full_story_part1", "texts": [clips["full_story_part1_c1"], clips["full_story_part1_c2"]], "joiner": " "},
                 {"key": "full_story_part2", "texts": [clips["full_story_part2_c1"]], "joiner": " "}]
        res = hl.resolve_highlights(art, cands, its, units)
        self.assertEqual(res["issues"], [], res["issues"])
        return {"result": res, "units": units}

    def test_decorations_kinds_and_body_unchanged(self):
        tmp = self.new_tmp()
        run = make_run(tmp, "a2", CLIPS)
        h = self._hl(CLIPS, [("c1", 1, "carried over", "引き継いだ"), ("c2", 2, "shepherd", "羊飼い"), ("c3", 3, "Silence", "沈黙")])
        out = user_rows(run, "a2", rows_of(run, "a2", CLIPS), f"{tmp}/o", highlights=h)
        blocks = [b for x in out if x["part"].startswith("Full Story") for b in x["blocks"]]
        joined = "".join(blocks)
        self.assertIn('<strong class="lk1" data-hl="c1">carried over</strong>', joined)
        self.assertIn('<strong class="lk2" data-hl="c2">shepherd</strong>', joined)
        self.assertIn('<span class="lk3" data-hl="c3">Silence</span>', joined)
        self.assertNotIn("title=", joined)
        # 装飾を剥がすと元の台本(クリップ単位)に戻る
        stripped = [hl.strip_decoration(b) for b in blocks]
        self.assertEqual(stripped, [f"<div class='script'>{cp.esc(t)}</div>" for t in CLIPS.values()])

    def test_phrase_across_clip_boundary_gets_same_data_hl_on_both_pieces(self):
        tmp = self.new_tmp()
        run = make_run(tmp, "a2", SPLIT)
        h = self._hl(SPLIT, [("cx", 1, "gift of kindness", "親切の贈り物")])
        out = user_rows(run, "a2", rows_of(run, "a2", SPLIT), f"{tmp}/o", highlights=h)
        blocks = [b for x in out if x["part"].startswith("Full Story Part 1") for b in x["blocks"]]
        self.assertEqual(len(blocks), 2)
        self.assertIn('<strong class="lk1" data-hl="cx">gift</strong>', blocks[0])
        self.assertIn('<strong class="lk1" data-hl="cx">of kindness</strong>', blocks[1])
        # G3: candidate_id単位で数え、片を連結してsurfaceと一致
        import er128_kp_highlight_01 as g3
        sec = "<h2 id='std'>S</h2>" + "".join(blocks)
        with mock.patch("er128_kp_confirmed_content_01.protection_enabled", return_value=True):
            v = g3.verify_highlights(sec, {"result": h["result"], "script_texts": list(SPLIT.values())[:2], "audience": "public"})
        self.assertEqual(v["problems"], [])
        self.assertEqual(v["status"], "PASS")

    def test_display_unit_mismatch_stops(self):
        tmp = self.new_tmp()
        run = make_run(tmp, "a2", CLIPS)
        h = self._hl(CLIPS, [("c1", 1, "carried over", "x")])
        h["units"][0]["texts"][0] = CLIP1 + " "   # 解決に使った表示台本と描画する台本が1文字違う
        with self.assertRaises(a63.FamilyZAudioStop) as cm:
            user_rows(run, "a2", rows_of(run, "a2", CLIPS), f"{tmp}/o", highlights=h)
        self.assertIn("HL_DISPLAY_UNIT_MISMATCH", str(cm.exception))

    def test_chunk_marker_outside_decoration_in_every_audience(self):
        tmp = self.new_tmp()
        run = make_run(tmp, "a2", CLIPS)
        plan = {"plans": {"full_story_part1_c1": {"chunked": True, "chunks": [{"text": "The knight rode far. He carried"}, {"text": "over the gift of kindness to a village."}]}}}
        with open(f"{run}/a2/audit/chunk_plan_a2.json", "w", encoding="utf-8") as f:
            json.dump(plan, f)
        h = self._hl(CLIPS, [("c1", 1, "carried over", "x")])   # 装飾の途中(carried | over)にChunk境界が来る
        rows = rows_of(run, "a2", CLIPS)
        dev = user_rows(run, "a2", rows, f"{tmp}/od", audience="dev", highlights=h)
        pub = user_rows(run, "a2", rows, f"{tmp}/op", audience="public", highlights=h)
        dev_html = "".join(b for x in dev for b in x["blocks"])
        pub_html = "".join(b for x in pub for b in x["blocks"])
        self.assertEqual(cp.count_chunk_markers(dev_html), 1)
        self.assertEqual(cp.count_chunk_markers(pub_html), 1)       # 委任_11: 試聴ページは全audienceで実Chunk境界に⏸(旧「publicは0」を置換)
        self.assertEqual(pub_html, dev_html)
        # ⏸はハイライト要素の外(装飾タグの内側にマーカー本体がない)
        for m in re.finditer(r'<strong class="lk\d"[^>]*>(.*?)</strong>', dev_html):
            self.assertNotIn("chunk-mark", m.group(1))
        self.assertEqual(hl.strip_decoration(dev_html).count("chunk-mark"), cp.count_boundary_marker_spans(dev_html))


# ============================================================
# 2. 付随ブロック(CSS+凡例+③訳リスト)・Z lint
# ============================================================
class HighlightBlockTest(unittest.TestCase):
    def test_empty_or_none_is_empty_string(self):
        self.assertEqual(a63.highlight_block_html(None), "")
        self.assertEqual(a63.highlight_block_html({"highlights": [], "meanings": []}), "")

    def test_block_has_css_legend_meaning_outside_script_and_no_banned_words(self):
        res = {"highlights": [{"decorate": True}], "meanings": [{"used_form": "Silence", "japanese_gloss": "沈黙", "unit_key": "full_story_part1"}]}
        b = a63.highlight_block_html(res)
        self.assertIn("<style>.lk1", b)
        self.assertIn('<p class="lk-legend">', b)
        self.assertIn('<ul class="lk-meaning"><li>Silence ＝ 沈黙</li></ul>', b)
        self.assertIsNone(BANNED.search(re.sub(r"<[^>]+>", " ", b)))
        self.assertNotIn("div class='script'", b)
        self.assertNotIn("<table", b)
        self.assertNotIn("<h2", b)

    def test_meaning_only_block_has_no_legend(self):
        b = a63.highlight_block_html({"highlights": [], "meanings": [{"used_form": "exact", "japanese_gloss": "正確な", "unit_key": None}]})
        self.assertNotIn('<p class="lk-legend">', b)
        self.assertIn("exact ＝ 正確な", b)

    def test_page_lint_passes_with_block(self):
        res = {"highlights": [{"decorate": True}], "meanings": [{"used_form": "Silence", "japanese_gloss": "沈黙", "unit_key": None}]}
        page = cp.render_standard_page("t", [{"id": "std", "label": "Standard", "full_src": "a.mp3", "duration": 1.0, "rows": [], "study_html": a63.highlight_block_html(res)}])
        self.assertEqual(a63.lint_page_html(page), {"file_scheme": False, "level_label_leak": False, "kp_label_leak": False})


# ============================================================
# 3. runner: level化・display_spec判定・解決アダプタ
# ============================================================
def fake_ctx(out_dir, **kw):
    d = dict(out_dir=out_dir, pages_dir=out_dir + "/pages", regenerate_stage=None, story_key="melos", slug="melos", run="run_x", hooks={}, mode="mock", budget=None)
    d.update(kw)
    return types.SimpleNamespace(**d)


class Part1LevelizationTest(unittest.TestCase):
    PART1_FUNCS = ("_part1_items", "_part1_path", "_part1_ja_path", "_require_part1_fresh", "_require_part1_ja_fresh", "_assemble_study_rows",
                   "_stage_kp_part1", "_stage_kp_part1_ja", "_part1_stage", "_part1_ja_stage", "_part1_on", "_part1_levels", "_part2_pool")

    def test_regen_names_cover_both_levels(self):
        names = r.E2E_KP_EXTRA_REGEN_NAMES
        for n in ("kp_expl_b1b", "kp_part1_b1b", "kp_part1_ja_b1b", "kp_part1_a2", "kp_part1_ja_a2"):
            self.assertIn(n, names)

    def test_stage_names_follow_level(self):
        self.assertEqual((r._part1_stage("a2"), r._part1_ja_stage("a2")), ("kp_part1_a2", "kp_part1_ja_a2"))
        self.assertEqual((r._part1_stage(r.ADV_LEVEL), r._part1_ja_stage(r.ADV_LEVEL)), ("kp_part1_b1b", "kp_part1_ja_b1b"))

    def test_no_b1b_literal_in_part1_functions_except_default_argument(self):
        """完了基準: Part 1系関数内の"b1b"リテラルが既定引数以外で0件。"""
        with open(os.path.join(ROOT, "er026_family_z_fiction_production_runner_01.py"), encoding="utf-8") as f:
            tree = ast.parse(f.read())
        seen = set()
        for fn in [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name in self.PART1_FUNCS]:
            seen.add(fn.name)
            defaults = {id(d) for d in list(fn.args.defaults) + list(fn.args.kw_defaults) if d is not None}
            for node in ast.walk(fn):
                if isinstance(node, ast.Constant) and isinstance(node.value, str) and "b1b" in node.value and id(node) not in defaults:
                    # docstring(関数先頭の文字列式)は説明文なので除外
                    if node is fn.body[0].value if isinstance(fn.body[0], ast.Expr) else False:
                        continue
                    self.fail(f"{fn.name}:{node.lineno}: {node.value!r}")
        self.assertEqual(seen, set(self.PART1_FUNCS))

    def test_part1_on_advanced_always_standard_only_with_display_spec(self):
        ctx = fake_ctx("/nonexistent")
        with mock.patch("er128_kp_confirmed_content_01.display_spec_of", return_value=None) as m:
            self.assertTrue(r._part1_on(ctx, "b1b"))
            self.assertFalse(r._part1_on(ctx, "a2"))
            self.assertEqual(r._part1_levels(ctx), ["b1b"])
        with mock.patch("er128_kp_confirmed_content_01.display_spec_of", return_value=V1):
            self.assertTrue(r._part1_on(ctx, "a2"))
            self.assertEqual(r._part1_levels(ctx), ["b1b", "a2"])

    def test_unknown_display_spec_is_stop(self):
        with mock.patch("er128_kp_confirmed_content_01.display_spec_of", side_effect=ValueError("未知のdisplay_spec: 'X'")):
            with self.assertRaises(r.FamilyZE2EStop) as cm:
                r._display_spec(fake_ctx("/x"), "a2")
        self.assertIn("FAMILY_Z_DISPLAY_SPEC_UNKNOWN", str(cm.exception))

    def test_part2_pool_empty_when_standard_has_no_part1(self):
        with mock.patch("er128_kp_confirmed_content_01.display_spec_of", return_value=None):
            self.assertEqual(r._part2_pool(fake_ctx("/x"), "a2"), {})

    def test_paths_are_level_scoped(self):
        ctx = fake_ctx("/o")
        self.assertTrue(r._part1_path(ctx, "a2").replace("\\", "/").endswith("/o/key_phrases/a2/kp_general_explanations.json"))
        self.assertTrue(r._part1_path(ctx).replace("\\", "/").endswith("/o/key_phrases/b1b/kp_general_explanations.json"))
        self.assertTrue(r._part1_ja_path(ctx, "a2").replace("\\", "/").endswith("/o/key_phrases/a2/kp_source_sentence_ja.json"))

    def test_std_part1_missing_is_fail_closed_with_level_specific_next_command(self):
        """load_level_inputs(a2)と同じ確認入口: kp_general_explanations.jsonが無い=FamilyZE2EStop(次の一手=kp_part1_a2。Advのkp_expl_b1bは案内しない)。"""
        items = [{"rank": 1, "candidate_id": "c1", "used_form": "demand", "display_phrase": "demanding", "source_sentence": "x demanding y.", "source_sentence_id": "S1",
                  "japanese_gloss": "要求する", "fulltext_source_ref": {"sentence_id": "S1"}}]
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp, True)
        with self.assertRaises(r.FamilyZE2EStop) as cm:
            r._require_part1_fresh(fake_ctx(tmp), items, "load_level_inputs(a2)", "a2")
        msg = str(cm.exception)
        self.assertIn("kp_part1_a2", msg)
        self.assertNotIn("kp_expl_b1b", msg)

    def test_load_level_inputs_checks_part1_for_every_part1_level(self):
        src = inspect.getsource(r.load_level_inputs)
        self.assertIn("_part1_on(ctx, level)", src)
        self.assertIn("_require_part1_fresh(ctx, _p1_items", src)
        self.assertIn("_require_part1_ja_fresh(ctx, _p1_items", src)
        # Part 2の確定確認はAdvanced専用のまま(Std文法はページ専用=共有入口に付けない)
        self.assertRegex(src, r'if level == "b1b":\s+_assert_part2_final')


class ResolveAdapterTest(TmpMixin, unittest.TestCase):
    """_resolve_level_highlights: 合成run(確定レコード・候補doc・本文・クリップ台本)で、解決→audit記録/ISSUE=ページ生成前STOPを確認する。"""

    def setUp(self):
        self.tmp = self.new_tmp()
        self.out = make_run(self.tmp, "a2", CLIPS)
        title_text = "# Title\n\n" + "\n\n".join([CLIP1, CLIP2, CLIP3]) + "\n"
        os.makedirs(f"{self.out}/key_phrases/a2", exist_ok=True)
        self.text_path = f"{self.tmp}/std.md"
        with open(self.text_path, "w", encoding="utf-8") as f:
            f.write(title_text)
        self.article = r.canonical_article_text(title_text)
        self.cands, self.items = mini(self.article, [("c1", 1, "carried over", "引き継いだ"), ("c2", 2, "shepherd", "羊飼い"), ("c3", 3, "Silence", "沈黙")])
        with open(f"{self.out}/key_phrases/a2/kp_candidates.json", "w", encoding="utf-8") as f:
            json.dump(self.cands, f)
        self.rec = {"origin": {"candidates_sha256": "c" * 64}, "items": [i for i in self.items if i["category"] < 3],
                    "unconsumed": [i for i in self.items if i["category"] == 3], "display_spec": V1}
        self.ctx = fake_ctx(self.out)

    @contextlib.contextmanager
    def patched(self, spec=V1, rec=None):
        with mock.patch("er128_kp_confirmed_content_01.display_spec_of", return_value=spec), \
                mock.patch("er128_kp_confirmed_content_01.load_record", return_value=rec if rec is not None else self.rec), \
                mock.patch.object(r, "_level_text_path", return_value=self.text_path):
            yield

    def test_no_display_spec_returns_none_and_writes_nothing(self):
        with self.patched(spec=None):
            self.assertIsNone(r._resolve_level_highlights(self.ctx, "a2"))
        self.assertFalse(os.path.exists(f"{self.out}/a2/audit/highlight_resolve.json"))

    def test_ok_resolves_and_writes_audit(self):
        with self.patched():
            hr = r._resolve_level_highlights(self.ctx, "a2")
        res = hr["result"]
        self.assertEqual((res["status"], res["stats"]["decorated"]), ("OK", 3))
        self.assertEqual([u["key"] for u in hr["units"]], ["full_story_part1", "full_story_part2"])
        with open(f"{self.out}/a2/audit/highlight_resolve.json", encoding="utf-8") as fh:
            audit = json.load(fh)
        self.assertEqual((audit["status"], audit["issues"]), ("OK", []))

    def test_issue_stops_before_pages_with_cause_code(self):
        bad = dict(self.rec, items=self.rec["items"] + [{"candidate_id": "zz", "category": 1, "used_form": "ghost", "japanese_gloss": "x"}])
        with self.patched(rec=bad):
            with self.assertRaises(r.FamilyZE2EStop) as cm:
                r._resolve_level_highlights(self.ctx, "a2")
        self.assertIn("FAMILY_Z_HIGHLIGHT_ISSUE(a2)", str(cm.exception))
        self.assertIn("HL_CANDIDATE_UNKNOWN", str(cm.exception))
        with open(f"{self.out}/a2/audit/highlight_resolve.json", encoding="utf-8") as fh:
            audit = json.load(fh)
        self.assertEqual(audit["status"], "ISSUE")

    def test_phrase_missing_from_display_is_issue(self):
        """候補docの語句が、ページに表示されるクリップ台本に無い(LR等で消えた)=ISSUE。黙って装飾を落とさない。"""
        with open(f"{self.out}/a2/audit/tts_generation_results.json", encoding="utf-8") as f:
            d = json.load(f)
        d["segments"]["full_story_part1_c1"]["canonical_text"] = "The knight rode far. He brought the gift of kindness to a village."
        with open(f"{self.out}/a2/audit/tts_generation_results.json", "w", encoding="utf-8") as f:
            json.dump(d, f)
        with self.patched():
            with self.assertRaises(r.FamilyZE2EStop) as cm:
                r._resolve_level_highlights(self.ctx, "a2")
        self.assertRegex(str(cm.exception), r"HL_(SPAN_NOT_IN_SENTENCE|SENTENCE_MISMATCH|NOT_IN_DISPLAY)")

    def test_text_sha_mismatch_is_issue(self):
        with open(self.text_path, "w", encoding="utf-8") as f:
            f.write("# Title\n\n" + "\n\n".join([CLIP1 + " Extra.", CLIP2, CLIP3]) + "\n")
        with self.patched():
            with self.assertRaises(r.FamilyZE2EStop) as cm:
                r._resolve_level_highlights(self.ctx, "a2")
        self.assertIn("HL_TEXT_SHA_MISMATCH", str(cm.exception))

    def test_candidates_doc_changed_after_confirmation_is_stop(self):
        bad = dict(self.rec, origin={"candidates_sha256": "d" * 64})
        with self.patched(rec=bad):
            with self.assertRaises(r.FamilyZE2EStop) as cm:
                r._resolve_level_highlights(self.ctx, "a2")
        self.assertIn("FAMILY_Z_HIGHLIGHT_CANDIDATES_SHA_MISMATCH", str(cm.exception))


# ============================================================
# 4. stage_pages(配線): マーク無し=従来、マーク付き=Std Part 1(Part 1→Part 2)+ハイライト
# ============================================================
class StagePagesWiringTest(unittest.TestCase):
    def _run_stage_pages(self, specs: dict, p1_html: dict, hl_results: dict):
        """重い下流をmockし、build_pagesへ渡るkwargsを返す。"""
        captured = {}

        def fake_build_pages(*a, **kw):
            captured.update(kw)
            return {"ok": True}

        a63_mod = types.SimpleNamespace(build_pages=fake_build_pages)
        m = types.SimpleNamespace(a63=a63_mod)
        p1 = mock.MagicMock()
        p1.render_html_block.side_effect = lambda rows: p1_html[rows[0]["lv"]]
        p1.TRANSLATION_DECISION_RECORD = "docs/pm/decisions/part1_translation_decision.json"
        p1.KpGeneralExplanationError = type("E", (Exception,), {})
        p2w = mock.MagicMock()
        p2w.compose_page_html.side_effect = lambda part1, res: f"{part1}<P2:{res}>"
        ctx = fake_ctx("/o", pages_dir="/o/pages")
        with contextlib.ExitStack() as es:
            es.enter_context(mock.patch.object(r, "_assert_kp_review_consistent"))
            es.enter_context(mock.patch.object(r, "_display_spec", side_effect=lambda c, lv: specs.get(lv)))
            es.enter_context(mock.patch.object(r, "_resolve_level_highlights", side_effect=lambda c, lv: hl_results.get(lv)))
            es.enter_context(mock.patch.object(r, "_part1_items", side_effect=lambda c, lv="b1b": [{"lv": lv}]))
            es.enter_context(mock.patch.object(r, "_assemble_study_rows", side_effect=lambda c, items, lv="b1b": [{"lv": lv}]))
            es.enter_context(mock.patch.object(r, "_assert_part2_final", side_effect=lambda c, where, level: level.upper()))
            es.enter_context(mock.patch.object(r, "_p1", return_value=p1))
            es.enter_context(mock.patch.object(r, "_p2w", return_value=p2w))
            es.enter_context(mock.patch.object(r, "_m", return_value=m))
            r.stage_pages(ctx)
        return captured

    def test_unmarked_standard_has_no_part1_and_no_highlights_kwarg(self):
        kw = self._run_stage_pages({}, {"b1b": "<A1>"}, {})
        self.assertEqual(kw["study_html_by_level"], {"b1b": "<A1><P2:B1B>", "a2": "<P2:A2>"})   # Stdは従来どおりPart 2のみ
        self.assertNotIn("highlights_by_level", kw)

    def test_marked_standard_gets_part1_before_part2_and_highlights(self):
        res = {"result": {"status": "OK"}, "units": [{"key": "u"}], "article": "x"}
        kw = self._run_stage_pages({"a2": V1, "b1b": V1}, {"b1b": "<A1>", "a2": "<S1>"}, {"a2": res, "b1b": res})
        self.assertEqual(kw["study_html_by_level"], {"b1b": "<A1><P2:B1B>", "a2": "<S1><P2:A2>"})   # Part 1 → Part 2
        self.assertEqual(set(kw["highlights_by_level"]), {"a2", "b1b"})
        self.assertEqual(kw["highlights_by_level"]["a2"], {"result": {"status": "OK"}, "units": [{"key": "u"}]})

    def test_marked_standard_without_decision_record_is_stop_not_silent_drop(self):
        with self.assertRaises(r.FamilyZE2EStop) as cm:
            self._run_stage_pages({"a2": V1}, {"b1b": "<A1>", "a2": ""}, {})
        self.assertIn("FAMILY_Z_KP_PART1_RENDER_NOT_OK(a2)", str(cm.exception))

    def test_highlight_issue_stops_before_any_page_generation(self):
        built = []
        with mock.patch.object(r, "_assert_kp_review_consistent"), \
                mock.patch.object(r, "_resolve_level_highlights", side_effect=r.FamilyZE2EStop("FAMILY_Z_HIGHLIGHT_ISSUE(a2): HL_X")), \
                mock.patch.object(r, "_m", return_value=types.SimpleNamespace(a63=types.SimpleNamespace(build_pages=lambda *a, **k: built.append(1)))):
            with self.assertRaises(r.FamilyZE2EStop):
                r.stage_pages(fake_ctx("/o"))
        self.assertEqual(built, [])


# ============================================================
# 5. page_verify: Part 1ちょうど1個・G3
# ============================================================
class VerifyLearningItemsTest(TmpMixin, unittest.TestCase):
    P1 = "<section class='study'><h3>Vocabulary &amp; Expressions</h3><div class='study-item'>x</div></section>"

    def _index(self, tmp, std_p1: int, adv_p1: int, decorate=True, extra_std=""):
        art = article_of(CLIPS)
        cands, its = mini(art, [("c1", 1, "carried over", "引き継いだ"), ("c3", 3, "Silence", "沈黙")])
        units = [{"key": "full_story_part1", "texts": [CLIP1, CLIP2], "joiner": " "}, {"key": "full_story_part2", "texts": [CLIP3], "joiner": " "}]
        res = hl.resolve_highlights(art, cands, its, units)
        blocks = []
        for k, t in enumerate([CLIP1, CLIP2]):
            blocks.append(cp.script_block(t, highlights=hl.highlights_for_text(res, "full_story_part1", k) if decorate else None))
        study = (a63.highlight_block_html(res) if decorate else "")
        blocks2 = [cp.script_block(CLIP3, highlights=hl.highlights_for_text(res, "full_story_part2", 0) if decorate else None)]

        def lv(i, label, n):
            return {"id": i, "label": label, "full_src": "a.mp3", "duration": 1.0, "rows": [{"part": "Full Story Part 1", "start": 0.0, "dur": 1.0, "src": "a.mp3", "blocks": blocks},
                                                                         {"part": "Full Story Part 2", "start": 1.0, "dur": 1.0, "src": "a.mp3", "blocks": blocks2}],
                    "study_html": study + self.P1 * n + extra_std}
        html = cp.render_standard_page("t", [lv("std", "Standard", std_p1), lv("adv", "Advanced", adv_p1)])
        os.makedirs(f"{tmp}/pages", exist_ok=True)
        with open(f"{tmp}/pages/index.html", "w", encoding="utf-8") as f:
            f.write(html)
        return {"result": res, "units": units, "article": art}

    def _verify(self, tmp, hr, specs):
        ctx = fake_ctx(tmp, pages_dir=f"{tmp}/pages")
        with mock.patch.object(r, "_display_spec", side_effect=lambda c, lv: specs.get(lv)), \
                mock.patch.object(r, "_resolve_level_highlights", side_effect=lambda c, lv: hr if specs.get(lv) else None), \
                mock.patch("er128_kp_confirmed_content_01.protection_enabled", return_value=True):
            return r._verify_learning_items(ctx)

    def test_marked_levels_pass_with_exactly_one_part1_and_g3(self):
        tmp = self.new_tmp()
        hr = self._index(tmp, 1, 1)
        out = self._verify(tmp, hr, {"a2": V1, "b1b": V1})
        self.assertEqual((out["a2"]["part1_blocks"], out["b1b"]["part1_blocks"]), (1, 1))
        self.assertEqual((out["a2"]["g3"]["status"], out["b1b"]["g3"]["status"]), ("PASS", "PASS"))

    def test_marked_standard_with_zero_or_two_part1_is_stop(self):
        for n in (0, 2):
            tmp = self.new_tmp()
            hr = self._index(tmp, n, 1)
            with self.assertRaises(r.FamilyZE2EStop) as cm:
                self._verify(tmp, hr, {"a2": V1, "b1b": V1})
            self.assertIn("FAMILY_Z_PART1_BLOCK_COUNT(a2)", str(cm.exception))

    def test_unmarked_standard_must_not_have_part1(self):
        tmp = self.new_tmp()
        self._index(tmp, 1, 1, decorate=False)
        with self.assertRaises(r.FamilyZE2EStop):
            self._verify(tmp, None, {})
        tmp2 = self.new_tmp()
        self._index(tmp2, 0, 1, decorate=False)
        out = self._verify(tmp2, None, {})   # 旧run: StdはPart 1なし・Advはあり(判断記録が有効な現行repo)
        self.assertEqual((out["a2"]["part1_blocks"], out["b1b"]["part1_blocks"]), (0, 1))
        self.assertNotIn("g3", out["a2"])

    def test_g3_fails_when_decoration_is_missing(self):
        tmp = self.new_tmp()
        hr = self._index(tmp, 1, 1, decorate=False)   # 期待は装飾あり、ページは装飾なし
        with self.assertRaises(r.FamilyZE2EStop) as cm:
            self._verify(tmp, hr, {"a2": V1, "b1b": V1})
        self.assertIn("FAMILY_Z_HIGHLIGHT_G3_FAIL", str(cm.exception))

    def test_kill_switch_skips_g3_with_disabled_marker(self):
        tmp = self.new_tmp()
        hr = self._index(tmp, 1, 1, decorate=False)
        ctx = fake_ctx(tmp, pages_dir=f"{tmp}/pages")
        with mock.patch.object(r, "_display_spec", side_effect=lambda c, lv: V1), \
                mock.patch.object(r, "_resolve_level_highlights", return_value=hr), \
                mock.patch("er128_kp_confirmed_content_01.protection_enabled", return_value=False):
            out = r._verify_learning_items(ctx)
        self.assertEqual(out["a2"]["g3"]["status"], "SKIPPED_DISABLED")
        self.assertTrue(out["a2"]["g3"]["disabled_marker"])


# ============================================================
# 5b. mock stage_kp: Std Part 1(display_spec付き=マーク接続を模擬)のlevel通し生成・fail-closed・明示再生成(API 0)
# ============================================================
def _count_mock_calls(out_dir: str) -> dict:
    cnt: dict = {}
    p = f"{out_dir}/mock_api_calls.jsonl"
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            for line in f:
                k = json.loads(line)["kind"]
                cnt[k] = cnt.get(k, 0) + 1
    return cnt


class MockKpStageStdPart1Test(unittest.TestCase):
    @staticmethod
    def _j(p):
        with open(p, encoding="utf-8") as fh:
            return json.load(fh)

    @classmethod
    def setUpClass(cls):
        import er026_family_z_e2e_integration_test_01 as e2e
        import er128_kp_confirmed_content_slot23_test_01 as s23
        cls.e2e = e2e
        cls.forbid = e2e.forbid_real_apis()
        cls.forbid.__enter__()
        cls.tmp_plain = tempfile.mkdtemp()
        cls.tmp_marked = tempfile.mkdtemp()
        cls.plain = r.build_mock_context(cls.tmp_plain)
        with _legacy_patch():   # 旧(マーク無し)記事の再現(M14接続後はnew_reviewがマークを付けるので、plainだけマーク発行を無効化する)
            e2e.run_stages_quiet(cls.plain, e2e.PRE_STAGES)
        cls.marked = r.build_mock_context(cls.tmp_marked)
        with s23.marks_connected():   # マーク発行あり(M14接続済み。実コードのnew_reviewと同じ結果)
            cls.marked_res = e2e.run_stages_quiet(cls.marked, e2e.PRE_STAGES)

    @classmethod
    def tearDownClass(cls):
        cls.forbid.__exit__(None, None, None)
        shutil.rmtree(cls.tmp_plain, ignore_errors=True)
        shutil.rmtree(cls.tmp_marked, ignore_errors=True)

    def test_unmarked_run_has_no_standard_part1_anything(self):
        out = self.plain.out_dir
        self.assertIsNone(r._display_spec(self.plain, "a2"))
        self.assertFalse(os.path.exists(f"{out}/key_phrases/a2/kp_general_explanations.json"))
        self.assertFalse(os.path.exists(f"{out}/key_phrases/a2/kp_source_sentence_ja.json"))
        self.assertFalse(os.path.exists(f"{out}/a2/study_text/part1_vocabulary_expressions.json"))
        self.assertTrue(os.path.exists(f"{out}/key_phrases/b1b/kp_general_explanations.json"))   # Advancedは従来どおり
        self.assertEqual(r._part1_levels(self.plain), ["b1b"])

    def test_marked_run_generates_standard_part1_with_level_a2(self):
        out = self.marked.out_dir
        self.assertEqual(r._display_spec(self.marked, "a2"), V1)
        doc, adv, st, adv_st = (self._j(f"{out}/{x}") for x in ("key_phrases/a2/kp_general_explanations.json", "key_phrases/b1b/kp_general_explanations.json",
                                                              "a2/study_text/part1_vocabulary_expressions.json", "study_text/part1_vocabulary_expressions.json"))
        self.assertEqual(doc.get("level"), "a2")
        self.assertNotIn("level", adv)   # Advの保存docは従来とキー集合も同一
        self.assertTrue(os.path.exists(f"{out}/key_phrases/a2/kp_source_sentence_ja.json"))
        self.assertEqual(st["level"], "Standard")
        self.assertEqual(adv_st["level"], "Advanced")   # Stdの出力でAdvを上書きしない
        res = self.marked_res["kp"]
        for k in ("kp_part1_b1b", "kp_part1_ja_b1b", "kp_part1_a2", "kp_part1_ja_a2", "part2_b1b", "part2_a2"):
            self.assertIn(k, res)

    def test_provenance_has_part1_stage_per_level_and_no_dependents_edge(self):
        with open(f"{self.marked.out_dir}/writer/provenance.json", encoding="utf-8") as fh:
            prov = json.load(fh)
        names = set(prov["downstream_stages"])
        for n in ("kp_part1_a2", "kp_part1_ja_a2", "kp_part1_b1b", "kp_part1_ja_b1b"):
            self.assertIn(n, names)
        import er062_family_z_writer_01 as w62
        self.assertNotIn("kp_part1_a2", w62.DEPENDENTS)
        self.assertFalse(any("kp_part1" in str(v) for v in w62.DEPENDENTS.values()))

    def test_resume_is_api_zero_and_explicit_regenerate_touches_only_the_named_stage(self):
        ctx = self.marked
        before = _count_mock_calls(ctx.out_dir)
        self.e2e.run_stages_quiet(ctx, ["kp"])
        self.assertEqual(_count_mock_calls(ctx.out_dir), before)   # 再実行はAPI 0(来歴で再利用)
        ctx.regenerate_stage = "kp_part1_a2"
        try:
            self.e2e.run_stages_quiet(ctx, ["kp"])
        finally:
            ctx.regenerate_stage = None
        after = _count_mock_calls(ctx.out_dir)
        self.assertEqual(after.get("kp_part1", 0) - before.get("kp_part1", 0), 1)     # a2のPart 1だけ1 call
        self.assertEqual(after.get("kp_part1_ja", 0), before.get("kp_part1_ja", 0))   # 訳・Advは再生成しない
        self.assertEqual({k: v for k, v in after.items() if k not in ("kp_part1",)}, {k: v for k, v in before.items() if k not in ("kp_part1",)})

    def test_load_level_inputs_a2_is_fail_closed_when_standard_part1_missing_and_ok_when_present(self):
        ctx = self.marked
        p = f"{ctx.out_dir}/key_phrases/a2/kp_general_explanations.json"
        bak = f"{p}.bak"
        shutil.copy(p, bak)
        try:
            os.remove(p)
            with self.assertRaises(r.FamilyZE2EStop) as cm:
                r.load_level_inputs(ctx, "a2")
            self.assertIn("FAMILY_Z_KP_PART1_NOT_READY", str(cm.exception))
            self.assertIn("kp_part1_a2", str(cm.exception))
        finally:
            shutil.move(bak, p)
        inp = r.load_level_inputs(ctx, "a2")
        self.assertIn("plan", inp)

    def test_load_level_inputs_a2_unmarked_does_not_require_part1(self):
        inp = r.load_level_inputs(self.plain, "a2")
        self.assertIn("plan", inp)


# ============================================================
# 6. 実run(wavあり環境のみ): 旧runのバイト同一golden・マーク付き相当のend-to-end(API 0)
# ============================================================
def _has_wav(run, level):
    import glob
    return bool(glob.glob(f"{run}/{level}/assembly/*.wav")) and os.path.exists(f"{run}/{level}/assembly/timeline.json")


@unittest.skipUnless(_has_wav(RUN_LEGACY, "a2") and _has_wav(RUN_LEGACY, "b1b"), "旧run(run_p2_evidence_r3)のwavが無い環境ではgoldenをskip")
class GoldenLegacyRunTest(TmpMixin, unittest.TestCase):
    def _hashes(self, out):
        def sha(fn):
            with open(os.path.join(out, fn), "rb") as fh:
                b = fh.read()
            # 委任_11: 試聴ページは実Chunk境界に⏸を表示する(新仕様)。⏸(区切り空白+span)以外は変更前とバイト同一であることを固定する
            b = b.replace(b" <span class='chunk-mark'>&#9208;</span>", b"")
            b = re.sub(rb"<p class='rpt-legend'[^>]*>.*?</p>", b"", b)   # ⏸/赤/青があるページだけに入る凡例1行も新仕様の追加分
            return hashlib.sha256(b).hexdigest()
        return {f: sha(f) for f in sorted(os.listdir(out)) if f.endswith(".html")}

    def test_legacy_run_pages_are_byte_identical_to_pre_change(self):
        tmp = self.new_tmp()
        a63.build_pages(RUN_LEGACY, f"{tmp}/p", page_title="t", audio_file_prefix="Melos")
        self.assertEqual(self._hashes(f"{tmp}/p"), GOLDEN_LEGACY)

    def test_explicit_none_and_empty_dict_are_identical_to_omitted(self):
        tmp = self.new_tmp()
        a63.build_pages(RUN_LEGACY, f"{tmp}/p1", page_title="t", audio_file_prefix="Melos", highlights_by_level=None)
        self.assertEqual(self._hashes(f"{tmp}/p1"), GOLDEN_LEGACY)


@unittest.skipUnless(os.path.exists(f"{RUN_KCP4}/key_phrases/a2/confirmed_selection.json") and _has_wav(RUN_KCP4, "a2") and _has_wav(RUN_KCP4, "b1b"),
                     "実run(run_kcp4_ev_z_01)のwavが無い環境ではskip")
class RealRunHighlightEndToEndTest(TmpMixin, unittest.TestCase):
    """確定済みの実Z run(a2/b1b)に display_spec 付き相当の判定を与え、解決→build_pages→check_page→G3 を通す。run側のファイルは変更しない(audit記録はtmpへ退避)。"""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        cls.ctx = fake_ctx(RUN_KCP4)
        cls.written = []
        real_wj = None
        with mock.patch.object(r, "_display_spec", return_value=V1):
            m = r._m()
            real_wj = m.w62.wj
            with mock.patch.object(m.w62, "wj", side_effect=lambda p, d: cls.written.append(p)):   # audit記録(highlight_resolve.json)をrun配下へ書かない
                cls.hl = {}
                for lv in ("a2", "b1b"):
                    hr = r._resolve_level_highlights(cls.ctx, lv)
                    cls.hl[lv] = {"result": hr["result"], "units": hr["units"]}
        cls.pub = f"{cls.tmp}/pub"
        a63.build_pages(RUN_KCP4, cls.pub, page_title="t", audio_file_prefix="Melos", highlights_by_level=cls.hl)
        with open(f"{cls.pub}/index.html", encoding="utf-8") as f:
            cls.html = f.read()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_resolved_without_issue_and_audit_was_not_written_into_run(self):
        for lv in ("a2", "b1b"):
            self.assertEqual(self.hl[lv]["result"]["status"], "OK")
        self.assertTrue(all("highlight_resolve.json" in p for p in self.written))

    def test_check_page_lint_and_no_markers_titles(self):
        chk = cp.check_page(self.html, base_dir=self.pub)
        self.assertEqual(chk["overall"], "PASS", {k: v for k, v in chk["checks"].items() if not v["ok"]})
        self.assertEqual(a63.lint_page_html(self.html), {"file_scheme": False, "level_label_leak": False, "kp_label_leak": False})
        expected = 0                                                   # 委任_11: ⏸は実Chunk境界(chunk plan記録)の数だけ。それ以外の位置には出さない
        for lv in ("a2", "b1b"):
            for p in cp.load_chunk_plans(f"{RUN_KCP4}/{lv}/audit/chunk_plan_{lv}.json").values():
                expected += max(len(cp.chunk_texts_of_plan(p)) - 1, 0)
        self.assertEqual(cp.count_boundary_marker_spans(self.html), expected)
        self.assertIsNone(re.search(r"<(?:strong|span)[^>]*\btitle=", self.html))
        self.assertIsNone(BANNED.search(re.sub(r"<[^>]+>", " ", self.html)))

    def test_g3_passes_per_level_section(self):
        import er128_kp_highlight_01 as g3
        for lv, sid in (("a2", "std"), ("b1b", "adv")):
            sec = cp.level_section_html(self.html, sid)
            with mock.patch("er128_kp_confirmed_content_01.protection_enabled", return_value=True):
                v = g3.verify_highlights(sec, {"result": self.hl[lv]["result"], "script_texts": [t for u in self.hl[lv]["units"] for t in u["texts"]], "audience": "dev"})   # 委任_11: 試聴ページは⏸を持つ
            self.assertEqual((v["status"], v["problems"]), ("PASS", []), lv)

    def test_std_has_three_kinds_and_meaning_list_and_adv_has_no_meaning_list_when_no_cat3(self):
        std = cp.level_section_html(self.html, "std")
        for k in (1, 2, 3):
            self.assertIn(f'class="lk{k}" data-hl=', std)
        self.assertIn('<ul class="lk-meaning">', std)
        self.assertNotIn('<ul class="lk-meaning">', cp.level_section_html(self.html, "adv"))
        # 訳リストは台本表(table)の外
        self.assertGreater(std.index('<ul class="lk-meaning">'), std.rindex("</table>"))

    def test_standard_and_dev_detail_pages_are_untouched(self):
        for f in ("standard.html", "advanced.html"):
            with open(f"{self.pub}/{f}", encoding="utf-8") as fh:
                self.assertNotIn('class="lk', fh.read())


if __name__ == "__main__":
    unittest.main()
