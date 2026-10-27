# -*- coding: utf-8 -*-
"""SLOT-23-CONSUMER-DESIGN-01 委任_04A: G3ハイライト検査(er128_kp_highlight_01.verify_highlights)のtest(API 0)。"""
import copy
import os
import unittest

import er128_kp_highlight_01 as g3
import er_learning_highlight_01 as hl
import er_learning_highlight_test_01 as base
import er_user_listening_page_common_01 as cp


def build(lv="a2", audience="public"):
    art, cands, items, units = base.load(lv)
    res = hl.resolve_highlights(art, cands, items, units)
    blocks = [cp.script_block(u["texts"][0], highlights=hl.highlights_for_text(res, u["key"], 0), audience=audience) for u in units]
    html = "<h2 id='Standard'>Standard</h2><table><tr><td>" + "".join(blocks) + "</td></tr></table>" + hl.legend_html() + hl.meaning_list_html(res["meanings"])
    exp = {"result": res, "script_texts": [u["texts"][0] for u in units], "audience": audience}
    return html, exp, res


class G3(unittest.TestCase):
    def test_pass_both_levels(self):
        for lv in ("a2", "b1b"):
            html, exp, _res = build(lv)
            v = g3.verify_highlights(html, exp)
            self.assertEqual((v["status"], v["problems"]), ("PASS", []))
            self.assertEqual(v["counts"]["candidates"], 10)

    def test_text_mismatch_detected(self):
        html, exp, _ = build()
        bad = html.replace('data-hl="p_dc8803926c">separately', 'data-hl="p_dc8803926c">separate', 1)
        self.assertIn("G3HL_TEXT_MISMATCH", [p["code"] for p in g3.verify_highlights(bad, exp)["problems"]])

    def test_missing_wrong_kind_extra(self):
        html, exp, _ = build()
        miss = html.replace('<strong class="lk1" data-hl="p_1a2370a6af">carried over</strong>', "carried over", 1)
        self.assertIn("G3HL_MISSING", [p["code"] for p in g3.verify_highlights(miss, exp)["problems"]])
        wrong = html.replace('<strong class="lk1" data-hl="p_1a2370a6af">', '<strong class="lk2" data-hl="p_1a2370a6af">', 1)
        self.assertIn("G3HL_WRONG_KIND", [p["code"] for p in g3.verify_highlights(wrong, exp)["problems"]])
        extra = html.replace("<td>", '<td><span class="lk3" data-hl="zzz">x</span>', 1)
        self.assertIn("G3HL_EXTRA", [p["code"] for p in g3.verify_highlights(extra, exp)["problems"]])

    def test_omitted_item_requires_notice(self):
        html, exp, res = build()
        e2 = copy.deepcopy(exp)
        e2["result"]["highlights"][0]["decorate"] = False          # 装飾省略と主張するが、NOTICEが無く、ページには装飾がある
        codes = [p["code"] for p in g3.verify_highlights(html, e2)["problems"]]
        self.assertIn("G3HL_NO_NOTICE_FOR_OMISSION", codes)
        self.assertIn("G3HL_UNEXPECTED_DECORATION", codes)

    def test_body_changed_and_meaning_mismatch(self):
        html, exp, _ = build()
        self.assertIn("G3HL_BODY_CHANGED", [p["code"] for p in g3.verify_highlights(html.replace("After one hour", "After two hours", 1), exp)["problems"]])
        bad = html.replace("＝ ", "＝ 違う", 1)
        self.assertIn("G3HL_MEANING_MISMATCH", [p["code"] for p in g3.verify_highlights(bad, exp)["problems"]])

    def test_public_marker_detected_and_dev_allowed(self):
        html, exp, _ = build()
        bad = html + "<span class='chunk-mark'>&#9208;</span>"
        self.assertIn("G3HL_PUBLIC_MARKER", [p["code"] for p in g3.verify_highlights(bad, exp)["problems"]])
        art, cands, items, units = base.load("a2")
        res = hl.resolve_highlights(art, cands, items, units)
        text = units[0]["texts"][0]
        first = text.index(". ") + 2
        chunks = [text[:first].strip(), text[first:].strip()]
        dev = cp.script_block(text, chunks, "dev", highlights=hl.highlights_for_text(res, units[0]["key"], 0))
        self.assertEqual(cp.count_chunk_markers(dev), 1)
        # devでも本文不変・装飾テキスト一致(マーカーは装飾の外)
        res1 = {**res, "highlights": [h for h in res["highlights"] if h["pieces"][0]["unit_key"] == units[0]["key"]], "meanings": []}
        v = g3.verify_highlights("<h2>x</h2>" + dev, {"result": res1, "script_texts": [text], "audience": "dev"})
        self.assertEqual(v["problems"], [])

    def test_kill_switch_skips_with_disabled_marker(self):
        html, exp, _ = build()
        old = os.environ.get("EIGO_KP_CONFIRMED_PROTECTION")
        os.environ["EIGO_KP_CONFIRMED_PROTECTION"] = "0"
        try:
            v = g3.verify_highlights(html.replace("After one hour", "X"), exp)
        finally:
            if old is None:
                del os.environ["EIGO_KP_CONFIRMED_PROTECTION"]
            else:
                os.environ["EIGO_KP_CONFIRMED_PROTECTION"] = old
        self.assertEqual((v["status"], v["disabled_marker"], v["problems"]), ("SKIPPED_DISABLED", True, []))


if __name__ == "__main__":
    unittest.main()
