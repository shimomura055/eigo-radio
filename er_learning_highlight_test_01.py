# -*- coding: utf-8 -*-
"""SLOT-23-CONSUMER-DESIGN-01 委任_04A: 本文ハイライト共通解決器・描画のtest(API 0)。fixtures=AI島a2/b1b(docs/research/SLOT-23-CONSUMER-DESIGN-01/fixtures)。"""
import json
import os
import unittest

import er_learning_highlight_01 as hl
import er_user_listening_page_common_01 as cp

ROOT = os.path.dirname(os.path.abspath(__file__))
FX = os.path.join(ROOT, "docs", "research", "SLOT-23-CONSUMER-DESIGN-01", "fixtures")


def load(lv):
    d = os.path.join(FX, f"ai_island_{lv}")

    def rj(n):
        with open(os.path.join(d, n), encoding="utf-8") as f:
            return json.load(f)
    with open(os.path.join(d, "article.md"), encoding="utf-8") as f:
        art = f.read()
    p = rj("parts.json")
    units = [{"key": f"full_story_part{i}", "texts": [p[f"part{i}"]], "joiner": " "} for i in (1, 2, 3)]
    return art, rj("kp_candidates.json"), hl.items_from_record(rj("confirmed_selection.json")), units


def U(*texts, key="u"):
    return [{"key": key, "texts": list(texts), "joiner": " "}]


def mini(article, items):
    """合成データ: articleから候補docを作る(sha・文ID・出現を実際に計算)。items=[(cid,cat,span,gloss)]"""
    import er105_kp_fulltext_selector_01 as sel
    us = hl.split_sentence_units(article)
    cands = []
    for cid, cat, span, gl in items:
        hits = [(i, u) for i, u in enumerate(us) if sel._phrase_pattern(span).search(u["raw_text"])]
        i0, u0 = hits[0]
        cands.append({"candidate_id": cid, "source_sentence": u0["raw_text"], "source_sentence_id": f"S{i0 + 1}",
                      "item": {"source_span": span, "occurrence_sentence_ids": [f"S{i + 1}" for i, _ in hits]}})
    doc = {"text_sha256": hl.sha256_text(article), "candidates": cands}
    its = [{"candidate_id": cid, "category": cat, "used_form": span, "japanese_gloss": gl} for cid, cat, span, gl in items]
    return doc, its


class AiIsland(unittest.TestCase):
    def test_a2_all_resolved_no_issue(self):
        art, cands, items, units = load("a2")
        r = hl.resolve_highlights(art, cands, items, units)
        self.assertEqual(r["issues"], [])
        self.assertEqual(r["stats"]["decorated"], 10)
        self.assertEqual(sorted(h["kind"] for h in r["highlights"]), [1, 1, 1, 2, 2, 3, 3, 3, 3, 3])
        by = {h["used_form"]: h for h in r["highlights"]}
        # 活用形: 候補のsource_span(本文表層形)を使う
        self.assertEqual(by["carry over"]["surface"], "carried over")
        self.assertEqual(by["take a detour"]["surface"], "taken a detour")
        # Std Strategy: タイトル由来S2は表示範囲外→本文内最初の出現へ再配置(NOTICE)
        self.assertEqual((by["Strategy"]["relocated_from"], by["Strategy"]["sentence_id"]), ("S2", "S8"))
        self.assertEqual([n["code"] for n in r["notices"]], ["HL_OCCURRENCE_RELOCATED"])
        self.assertEqual(len(r["meanings"]), 5)

    def test_b1b_inflections_and_technique(self):
        art, cands, items, units = load("b1b")
        r = hl.resolve_highlights(art, cands, items, units)
        self.assertEqual(r["issues"], [])
        surf = {h["used_form"]: h["surface"] for h in r["highlights"]}
        self.assertEqual((surf["look at separately"], surf["erase"], surf["technique"]), ("looked at separately", "erased", "technique"))
        self.assertEqual({h["used_form"]: h["sentence_id"] for h in r["highlights"]}["technique"], "S25")

    def test_surface_equals_display_slice_and_render_roundtrip(self):
        for lv in ("a2", "b1b"):
            art, cands, items, units = load(lv)
            r = hl.resolve_highlights(art, cands, items, units)
            n = 0
            for u in units:
                text = u["texts"][0]
                hs = hl.highlights_for_text(r, u["key"], 0)
                n += len(hs)
                for h in hs:
                    self.assertEqual(text[h["start"]:h["end"]], h["surface"])
                html = cp.script_block(text, highlights=hs)
                self.assertEqual(hl.strip_decoration(html), "<div class='script'>" + cp.esc(text) + "</div>")   # 本文不変
                self.assertNotIn("⏸", html)
            self.assertEqual(n, 10)

    def test_text_sha_mismatch_is_issue(self):
        art, cands, items, units = load("a2")
        r = hl.resolve_highlights(art + " x", cands, items, units)
        self.assertEqual([i["code"] for i in r["issues"]], ["HL_TEXT_SHA_MISMATCH"])
        self.assertEqual(r["highlights"], [])

    def test_split_matches_candidate_source_sentence(self):
        # 文分割(wordfreq無し環境のコピー)が候補docの記録と全件一致=候補生成時の分割と同一
        for lv in ("a2", "b1b"):
            art, cands, _i, _u = load(lv)
            us = hl._local_build_sentence_units(art)
            for c in cands["candidates"]:
                self.assertEqual(hl.norm_ws(us[int(c["source_sentence_id"][1:]) - 1]["raw_text"]), hl.norm_ws(c["source_sentence"]))


class Rules(unittest.TestCase):
    def test_normalization_curly_quotes_and_whitespace(self):
        art = "# T\n\nHe said it's a \"good plan\" for us. Then they left.\n"
        units = U("He said it’s a “good plan”  for us.   Then they left.")
        doc, its = mini(art, [("c1", 1, "good plan", "良い計画")])
        r = hl.resolve_highlights(art, doc, its, units)
        self.assertEqual(r["issues"], [])
        self.assertEqual(r["highlights"][0]["surface"], "good plan")

    def test_monotonic_alignment_uses_specified_occurrence(self):
        art = "# T\n\nOne price rose. The price fell again. A third sentence here.\n"
        units = U("One price rose. The price fell again. A third sentence here.")
        doc, its = mini(art, [("c1", 3, "price", "値段")])
        doc["candidates"][0]["source_sentence_id"] = "S3"      # 特定出現=2つ目のprice(本文の文S3 = タイトル行がS1)
        doc["candidates"][0]["source_sentence"] = hl.split_sentence_units(art)[2]["raw_text"]
        r = hl.resolve_highlights(art, doc, its, units)
        h = r["highlights"][0]
        self.assertEqual((h["sentence_id"], h["pieces"][0]["start"]), ("S3", 20))

    def test_relocation_when_title_sentence_not_displayed(self):
        art = "# Big Strategy Day\n\nWe made a strategy for the day. The strategy worked.\n"
        units = U("We made a strategy for the day. The strategy worked.")
        doc, its = mini(art, [("c1", 3, "strategy", "戦略")])
        r = hl.resolve_highlights(art, doc, its, units)
        self.assertEqual(r["issues"], [])
        self.assertEqual(r["highlights"][0]["relocated_from"], "S1")
        self.assertEqual([n["code"] for n in r["notices"]], ["HL_OCCURRENCE_RELOCATED"])

    def test_not_in_display(self):
        art = "# T\n\nThe visible sentence is here. Hidden words appear elsewhere.\n"
        units = U("The visible sentence is here.")
        doc, its = mini(art, [("c1", 3, "hidden words", "隠れた語"), ("c2", 1, "hidden words appear", "x")])
        r = hl.resolve_highlights(art, doc, its, units)
        self.assertEqual([n["code"] for n in r["notices"]], ["HL_NOT_IN_DISPLAY_MEANING_ONLY"])      # ③は訳リストのみ
        self.assertEqual([i["code"] for i in r["issues"]], ["HL_NOT_IN_DISPLAY"])                       # ①はISSUE
        self.assertEqual([m["candidate_id"] for m in r["meanings"]], ["c1"])

    def test_sentence_mismatch_and_unknown_id(self):
        art = "# T\n\nAlpha beta gamma. Delta epsilon.\n"
        units = U("Alpha beta gamma. Delta epsilon.")
        doc, its = mini(art, [("c1", 1, "alpha beta", "x"), ("c2", 1, "delta", "y")])
        doc["candidates"][0]["source_sentence"] = "Different sentence"
        doc["candidates"][1]["source_sentence_id"] = "S99"
        r = hl.resolve_highlights(art, doc, its, units)
        self.assertEqual(sorted(i["code"] for i in r["issues"]), ["HL_SENTENCE_ID_UNKNOWN", "HL_SENTENCE_MISMATCH"])

    def test_containment_lower_priority_omitted_with_notice(self):
        art = "# T\n\nIt is worth paying attention to details.\n"
        units = U("It is worth paying attention to details.")
        doc, its = mini(art, [("c1", 1, "worth paying attention to", "注目に値する"), ("c2", 2, "attention", "注意"), ("c3", 3, "paying attention", "注意を払う")])
        r = hl.resolve_highlights(art, doc, its, units)
        self.assertEqual(r["issues"], [])
        dec = {h["candidate_id"]: h["decorate"] for h in r["highlights"]}
        self.assertEqual(dec, {"c1": True, "c2": False, "c3": False})
        self.assertEqual(sorted(n["candidate_id"] for n in r["notices"] if n["code"] == "HL_CONTAINED"), ["c2", "c3"])
        self.assertEqual([m["candidate_id"] for m in r["meanings"]], ["c3"])   # 訳リストには残る

    def test_contained_higher_inside_lower(self):
        art = "# T\n\nWe pay attention to the details here.\n"
        units = U("We pay attention to the details here.")
        doc, its = mini(art, [("c1", 1, "attention", "注意"), ("c2", 3, "pay attention to", "注意を払う")])
        r = hl.resolve_highlights(art, doc, its, units)
        dec = {h["candidate_id"]: h["decorate"] for h in r["highlights"]}
        self.assertEqual(dec, {"c1": True, "c2": False})

    def test_partial_overlap_rules(self):
        art = "# T\n\nWe took a long detour home today.\n"
        units = U("We took a long detour home today.")
        doc, its = mini(art, [("c1", 3, "took a long", "x"), ("c2", 3, "long detour home", "y")])
        r = hl.resolve_highlights(art, doc, its, units)
        self.assertEqual(r["issues"], [])
        self.assertEqual([n["code"] for n in r["notices"]], ["HL_PARTIAL_OVERLAP_3"])
        self.assertEqual(len(r["meanings"]), 2)
        doc, its = mini(art, [("c1", 1, "took a long", "x"), ("c2", 3, "long detour home", "y")])
        r = hl.resolve_highlights(art, doc, its, units)
        self.assertEqual([i["code"] for i in r["issues"]], ["HL_PARTIAL_OVERLAP"])

    def test_adjacent_items_are_separate_elements(self):
        art = "# T\n\nWe took detours daily.\n"
        units = U("We took detours daily.")
        doc, its = mini(art, [("c1", 3, "took", "a"), ("c2", 3, "detours", "b")])
        r = hl.resolve_highlights(art, doc, its, units)
        self.assertEqual(r["issues"], [])
        self.assertTrue(all(h["decorate"] for h in r["highlights"]))

    def test_sentence_across_clips_resolves_in_owning_clip(self):
        art = "# T\n\nMelos called across the hall, \"You kill men from fear.\"\n"
        units = U("Melos called across the hall,", "\"You kill men from fear.\"")
        doc, its = mini(art, [("c1", 3, "kill men", "y")])
        r = hl.resolve_highlights(art, doc, its, units)
        self.assertEqual(r["issues"], [])
        self.assertEqual(r["highlights"][0]["pieces"][0]["text_index"], 1)

    def test_lr_rebound_notice(self):
        art = "# T\n\nFirst line here. The old sentence had a cool trick. Last line there.\n"
        units = U("First line here. The rewritten sentence has a cool trick now. Last line there.")
        doc, its = mini(art, [("c1", 1, "cool trick", "x")])
        r0 = hl.resolve_highlights(art, doc, its, units)
        self.assertEqual([i["code"] for i in r0["issues"]], ["HL_NOT_IN_DISPLAY"])     # LR後・文が変わった: 既定は特定不能=ISSUE
        r1 = hl.resolve_highlights(art, doc, its, units, lr_rebound=True)
        self.assertEqual(r1["issues"], [])
        self.assertEqual([n["code"] for n in r1["notices"]], ["HL_LR_REBOUND"])


class Render(unittest.TestCase):
    def test_script_block_none_is_byte_identical(self):
        for t, ch, au in (("A b c.", None, "public"), ("A b. C d.", ["A b.", "C d."], "dev"), ("", None, "public")):
            a = cp.script_block(t, ch, au)
            self.assertEqual(cp.script_block(t, ch, au, highlights=None), a)
            self.assertEqual(cp.script_block(t, ch, au, highlights=[]), a)

    def test_css_constants_and_tags(self):
        css = hl.HIGHLIGHT_CSS
        for need in ("text-decoration-style:double", "-webkit-text-decoration-style:double", "-webkit-text-decoration-line:underline",
                     ".lk3{font-weight:inherit", "font-size:inherit", "color:inherit", "background:none"):
            self.assertIn(need, css)
        for bad in ("::before", "::after", "content:"):
            self.assertNotIn(bad, css)
        self.assertIs(cp.HIGHLIGHT_CSS, hl.HIGHLIGHT_CSS)
        self.assertNotIn(".lk1", cp.CSS)          # 本体CSSへは連結しない(既存ページのバイト不変。配線班が連結)
        h = cp.script_block("alpha beta gamma", highlights=[{"kind": 1, "start": 0, "end": 5, "candidate_id": "a"}, {"kind": 2, "start": 6, "end": 10, "candidate_id": "b"},
                                                          {"kind": 3, "start": 11, "end": 16, "candidate_id": "c", "surface": "gamma"}])
        self.assertEqual(h, "<div class='script'><strong class=\"lk1\" data-hl=\"a\">alpha</strong> <strong class=\"lk2\" data-hl=\"b\">beta</strong> "
                            "<span class=\"lk3\" data-hl=\"c\">gamma</span></div>")
        self.assertNotIn("title=", h)

    def test_surface_assert(self):
        with self.assertRaises(AssertionError):
            cp.script_block("alpha beta", highlights=[{"kind": 1, "start": 0, "end": 5, "candidate_id": "a", "surface": "WRONG"}])
        with self.assertRaises(AssertionError):
            cp.script_block("alpha beta", highlights=[{"kind": 1, "start": 0, "end": 6, "candidate_id": "a"}, {"kind": 3, "start": 5, "end": 8, "candidate_id": "b"}])

    def test_marker_outside_decoration_in_every_audience(self):
        text = "First paragraph here.\n\nSecond paragraph here."
        chunks = ["First paragraph here.", "Second paragraph here."]
        s, e = text.index("here."), text.index("Second") + len("Second")      # ハイライトがChunk境界を跨ぐ
        hs = [{"kind": 2, "start": s, "end": e, "candidate_id": "x", "surface": text[s:e]}]
        dev = cp.script_block(text, chunks, "dev", highlights=hs)
        self.assertEqual(cp.count_chunk_markers(dev), 1)
        self.assertIn("</strong> <span class='chunk-mark'>&#9208;</span><strong class=\"lk2\" data-hl=\"x\">", dev)   # マーカーは装飾の外
        self.assertEqual(hl.strip_decoration(dev), cp.script_block(text, chunks, "dev"))
        pub = cp.script_block(text, chunks, "public", highlights=hs)
        self.assertEqual(pub, dev)                                    # 委任_11(ユーザー原文_02 §4): 試聴ページは全audienceで実Chunk境界に⏸(旧「publicはマーカーなし」を置換)
        self.assertEqual(cp.script_block(text, None, "public", highlights=hs).count("chunk-mark"), 0)   # chunk記録がなければ表示なし

    def test_meaning_and_legend(self):
        m = hl.meaning_list_html([{"used_form": "make a difference", "japanese_gloss": "影響を与える"}])
        self.assertEqual(m, '<ul class="lk-meaning"><li>make a difference ＝ 影響を与える</li></ul>')
        self.assertEqual(hl.meaning_list_html([]), "")
        lg = hl.legend_html()
        for bad in ("英語:", "日本語:", "EN:", "JA:", "(A2)", "data-hl", "title="):
            self.assertNotIn(bad, lg + m)
        self.assertIn('class="lk1"', lg)


class Contract(unittest.TestCase):
    def test_contract_view(self):
        art, cands, items, units = load("a2")
        v = hl.contract_view(hl.resolve_highlights(art, cands, items, units))
        self.assertEqual(sum(len(x) for x in v["highlights"].values()), 10)
        self.assertEqual([n["code"] for n in v["notices"]], ["HL_OCCURRENCE_RELOCATED"])
        self.assertEqual(sum(len(x) for x in v["meanings"].values()), 5)


if __name__ == "__main__":
    unittest.main()
