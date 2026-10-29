# -*- coding: utf-8 -*-
"""D8(HR-SELECTION-FLOW-QA-FIRST-AND-REDUNDANCY-NONBLOCKING-01 委任_04): 重複アラームの表示(完了報告ブロック/事後確認節)。API 0。"""
import json
import os
import re
import tempfile
import unittest

import er119_kp_human_review_01 as rv

ROOT = os.path.dirname(os.path.abspath(__file__))


def _w(p, d):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False)


PAIR = {"candidate_id_a": "p1", "candidate_id_b": "p2", "used_form_a": "let go of", "used_form_b": "give <up>", "slot_label_a": "Key Phrase(①)",
        "slot_label_b": "本文意味(③)", "aspects": {"meaning_overlap": "FAIL", "usage_context_overlap": "PASS"}, "reasoning": "どちらも手放す感覚"}


class TestRender(unittest.TestCase):
    def test_zero_alarms_shows_zero(self):
        with tempfile.TemporaryDirectory() as d:
            _w(f"{d}/a2/key_phrases/redundancy_alarm.json", {"candidate_qa_alarms": [], "final_set_alarms": []})     # X配置
            t, h = rv.render_redundancy_alarms(d, "a2")
            self.assertIn("重複アラーム 0件", t)
            self.assertIn("重複アラーム 0件", h)

    def test_multiple_alarms_dedup_and_escape_yz_layout(self):
        with tempfile.TemporaryDirectory() as d:
            fin = dict(PAIR, candidate_id_a="p2", candidate_id_b="p1", used_form_a="give <up>", used_form_b="let go of")     # 同一ペア(逆順)=1件
            other = dict(PAIR, used_form_b="hold back", candidate_id_b="p3")
            _w(f"{d}/key_phrases/b1b/redundancy_alarm.json", {"candidate_qa_alarms": [PAIR, other], "final_set_alarms": [fin]})     # Y/Z配置
            _w(f"{d}/study_text/nuance_redundancy_alarm.json", {"alarms": [{"kind": "nuance_vs_kp_word", "item": "never stir", "note": "焦点が重複"}]})
            t, h = rv.render_redundancy_alarms(d, "b1b")
            self.assertIn("Advanced: 重複アラーム 3件", t)
            self.assertIn("give &lt;up&gt;", h)
            self.assertNotIn("give <up>", h)
            self.assertIn("ニュアンス解説", t)
            self.assertEqual(rv.render_redundancy_alarms(d, "a2"), ("", ""))     # 別levelの記録なし

    def test_missing_or_broken_file_is_empty_and_nonblocking(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(rv.render_redundancy_alarms(d, "a2"), ("", ""))
            self.assertEqual(rv.render_redundancy_alarms_all(d), ("", ""))     # 全記録なし=従来ページとバイト同一
            os.makedirs(f"{d}/a2/key_phrases")
            with open(f"{d}/a2/key_phrases/redundancy_alarm.json", "w") as f:
                f.write("{broken")
            self.assertEqual(rv.render_redundancy_alarms(d, "a2"), ("", ""))

    def test_all_section_is_outside_body_and_has_no_forbidden_labels(self):
        with tempfile.TemporaryDirectory() as d:
            _w(f"{d}/a2/key_phrases/redundancy_alarm.json", {"candidate_qa_alarms": [PAIR], "final_set_alarms": []})
            t, h = rv.render_redundancy_alarms_all(d)
            self.assertTrue(h.startswith("<section id='post-check'>") and h.endswith("</section>"))
            self.assertNotRegex(re.sub(r"<[^>]+>", " ", h), r"English:|英語:|EN:|日本語:|JA:|\bA2\b|\bB1\b")     # Z lint / level label


class TestRunnerCalls(unittest.TestCase):
    def _src(self, n):
        with open(os.path.join(ROOT, n), encoding="utf-8") as f:
            return f.read()

    def test_x_y_z_call_the_common_render_function(self):
        for n in ("er019_family_x_listening_page_01.py", "er121_family_y_runner_01.py", "er026_family_z_fiction_production_runner_01.py"):
            self.assertIn("render_redundancy_alarms_all(", self._src(n), n)
        self.assertIn("post_check_html", self._src("er063_family_z_audio_01.py"))

    def test_z_index_appends_post_check_after_aux_and_default_is_byte_identical(self):
        import er063_family_z_audio_01 as z
        base = z.build_index_html([], [], page_title="t")
        sec = "<section id='post-check'>X</section>"
        withp = z.build_index_html([], [], page_title="t", post_check_html=sec)
        self.assertEqual(withp.replace(sec, "", 1), base)     # 空(既定)=従来とバイト同一 / 追記は補助情報の直後(本文領域外)
        self.assertIn("</details>" + sec, withp)

    def test_only_one_render_definition(self):
        defs = [n for n in os.listdir(ROOT) if n.endswith(".py") and "test" not in n and re.search(r"def render_redundancy_alarms\(", self._src(n))]
        self.assertEqual(defs, ["er119_kp_human_review_01.py"])


if __name__ == "__main__":
    unittest.main()
