# -*- coding: utf-8 -*-
"""FAMILY-Z-IN-A-GROVE-PRODUCTION-01 委任_13 (OPEN-596): 閉じ引用符の無い発言(段落跨ぎ発言の慣習 ※段落末は閉じず次段落を“で再開)が
地の文(narrator)へ倒れ、発言者Voiceでなくナレーターで読まれる不具合の回帰test。API呼出0・ファイル書込0(run実物は読取のみ)。
(a)quote_spans/extract_quotes/build_flat_chunks: 末尾の閉じ無し引用を1引用として拾う (b)全て閉じた段落・引用なし段落は従来と同一
(c)藪の中 Std/Adv実本文: narrator clipに引用符(“)が1つも残らない・全dialogue textが話者Voiceで分かれる (d)clip連結が元段落に復元できる(欠落・重複なし)"""
import json
import os
import re
import unittest

import er013_family_c_production_01 as fam_c
import er062_family_z_structure_01 as st

RUN = "er026_output/family_z_production_e2e_01/in_a_grove/run_sf_prod_01"

# 段落index→話者(藪の中。7証言の順序固定、Std/Adv共通: 全14段落)
GROVE_PARA_SPEAKER = {0: "woodcutter", 1: "monk", 2: "constable", 3: "old_woman", 4: "tajomaru", 5: "tajomaru",
                      6: "masago", 7: "masago", 8: "masago", 9: "takehiro", 10: "takehiro", 11: "takehiro", 12: "takehiro", 13: "takehiro"}


def _speakers_by_paragraph(paras):
    out = {}
    for q in st.extract_quotes(paras):
        out[q["quote_id"]] = GROVE_PARA_SPEAKER[q["paragraph_index"]]
    return out


class QuoteSpansUnitTest(unittest.TestCase):
    def test_closed_only_unchanged_vs_regex(self):
        for para in ['“A,” he said. “B.”', 'no quote here.', '“Only one.”', '“A,” said X. “B,” said Y.']:
            self.assertEqual(st.quote_spans(para), [(m.start(), m.end()) for m in st.QUOTE_RE.finditer(para)])

    def test_trailing_unclosed_opening_quote_is_one_quote_to_paragraph_end(self):
        para = '“I killed him,” Tajomaru said. “The wind lifted her veil. She fought with her dagger.'
        sp = st.quote_spans(para)
        self.assertEqual(len(sp), 2)
        self.assertEqual(para[sp[0][0]:sp[0][1]], '“I killed him,”')
        self.assertEqual(para[sp[1][0]:sp[1][1]], '“The wind lifted her veil. She fought with her dagger.')

    def test_paragraph_that_is_entirely_an_unclosed_continuation(self):
        para = '“He moved his lips. ‘Kill me,’ he said, so I stabbed him.'
        sp = st.quote_spans(para)
        self.assertEqual(sp, [(0, len(para))])      # 単一引用符(‘’)は引用境界にしない

    def test_trailing_whitespace_and_empty_open_quote_are_ignored(self):
        para = '“A,” said X. “  '
        self.assertEqual(st.quote_spans(para), [(m.start(), m.end()) for m in st.QUOTE_RE.finditer(para)])

    def test_extract_quotes_ids_stable_and_text_is_raw_slice(self):
        paras = ['“A,” X said. “B and C.', '“D.”']
        qs = st.extract_quotes(paras)
        self.assertEqual([q["quote_id"] for q in qs], ["q0_1", "q0_2", "q1_1"])
        for q in qs:
            self.assertEqual(paras[q["paragraph_index"]][q["start"]:q["end"]], q["text"])

    def test_build_flat_chunks_routes_unclosed_to_speaker_not_narrator(self):
        paras = ['“A,” X said. “B and C.']
        flat = st.build_flat_chunks(paras, {"q0_1": "x", "q0_2": "x"})
        self.assertEqual([(v, t) for (_p, v, t) in flat], [("x", "“A,”"), ("narrator", " X said. "), ("x", "“B and C.")])
        self.assertEqual("".join(t for (_p, _v, t) in flat), paras[0])      # 欠落・重複なし


@unittest.skipUnless(os.path.exists(f"{RUN}/writer/std.md"), "run実物が無い環境ではskip")
class InAGroveRealTextTest(unittest.TestCase):
    def _paras(self, rel):
        text = open(f"{RUN}/{rel}", encoding="utf-8").read()
        _t, body = st.split_title_body(text)
        return st.clean_body_paragraphs(body)

    def _plan(self, rel, level):
        paras = self._paras(rel)
        old = json.load(open(f"{RUN}/segment_plan_{level}.json", encoding="utf-8"))
        b1, b2 = old["boundaries"]
        clips = st.plan_clips(paras, _speakers_by_paragraph(paras), b1, b2, level, f"{RUN}/{level}/narration")
        return paras, clips

    def _check(self, rel, level):
        paras, clips = self._plan(rel, level)
        # (1) narrator clipには引用符が残らない(=引用の本文が地の文へ倒れない)
        for c in clips:
            if c["speaker"] == "narrator":
                self.assertNotIn('"', c["text"], f"{c['id']} narratorに引用符が残存: {c['text'][:60]}")      # clip textはnormalize_for_tts後(直線引用符)
        # (2) 7証言者それぞれの発言本文が、その証言者のclipに全て入る(段落→話者の固定表と一致)
        for c in clips:
            if c["speaker"] != "narrator":
                for pi in c["source_paragraph_indices"]:
                    self.assertEqual(GROVE_PARA_SPEAKER[pi], c["speaker"], f"{c['id']} para{pi}")
        # (3) 欠落・重複なし: 全clip textの連結が元段落の連結(空白除く)と一致
        joined = re.sub(r"\s+", "", "".join(c["text"] for c in clips))
        self.assertEqual(joined, re.sub(r"\s+", "", fam_c.normalize_for_tts("".join(paras))))
        # (4) 多襄丸の発言(段落4・5)は全てtajomaru。ナレーターは短い発言タグのみ
        taj = [c for c in clips if c["speaker"] == "tajomaru"]
        self.assertTrue(any("wind lifted" in c["text"] or "breeze lifted" in c["text"] for c in taj))
        self.assertTrue(any("She held my arm" in c["text"] or "Then she seized my arm" in c["text"] for c in taj))
        for c in clips:
            if c["speaker"] == "narrator":
                self.assertLessEqual(c["word_count"], 8, f"{c['id']} narratorが長い(=発言が混入): {c['text']}")
        return clips

    def test_standard_real_text(self):
        self._check("writer/std.md", "a2")

    def test_advanced_real_text(self):
        self._check("writer/r2.md", "b1b")

    def test_old_behaviour_would_fail_this_check(self):
        """修正前の挙動(閉じ引用のみ)ではnarrator clipに発言が混入する=testが不具合を検出できる証拠。"""
        paras = self._paras("writer/std.md")
        old_flat = []
        for p_idx, para in enumerate(paras):
            pos = 0
            for m in st.QUOTE_RE.finditer(para):
                if m.start() > pos and para[pos:m.start()].strip():
                    old_flat.append(("narrator", para[pos:m.start()]))
                old_flat.append(("q", m.group(0)))
                pos = m.end()
            if pos < len(para) and para[pos:].strip():
                old_flat.append(("narrator", para[pos:]))
        leaked = [t for (v, t) in old_flat if v == "narrator" and "“" in t]
        self.assertGreaterEqual(len(leaked), 3)      # Tajomaru / Masago / Takehiro


if __name__ == "__main__":
    unittest.main()
