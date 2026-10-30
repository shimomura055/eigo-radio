# -*- coding: utf-8 -*-
"""SLOT-23 委任_07G(D-F1是正): public_study_htmlのPart 1をlevel+display_specで決める(API 0・全てmock)。
display_spec付きa2=Part 1(1個)→Part 2の順 / display_spec無しa2=Part 1なし(遡及なし) / b1b=従来どおり(display_specに依存しない)。
実行: PYTHONPATH=netblock_harness_01 .venv/Scripts/python.exe -m pytest er120_public_study_html_level_test_01.py -q"""
from __future__ import annotations

import test_state_isolation_01  # noqa: F401

import unittest
from unittest import mock

import er003_kp_general_explanation_01 as p1
import er120_part2_wiring_01 as p2w

ART = "# t\n\nHello world.\n"


class _CC:
    def __init__(self, spec):
        self.spec, self.calls = spec, []

    def display_spec_of(self, run, level):
        return self.spec.get(level)

    def load_verified_items(self, d, *, level, which="kp", **kw):
        self.calls.append((d, level, which))
        return [{"rank": 1}]


class PublicStudyHtmlLevelTest(unittest.TestCase):
    def _run(self, level, spec):
        cc = _CC(spec)
        order = []
        with mock.patch.object(p2w, "_cc", return_value=cc), \
             mock.patch.object(p2w, "require_final", side_effect=lambda *a, **k: order.append("p2") or {"r": 1}), \
             mock.patch.object(p1, "study_html_for_audio_dir", side_effect=lambda ad, items=None, level=None: order.append(("p1", level)) or "<P1/>"), \
             mock.patch.object(p2w, "compose_page_html", side_effect=lambda a, b: a + "|P2"), \
             mock.patch.object(p2w, "part1_ref_ja_pool", return_value={}), \
             mock.patch.object(p2w.g, "paragraphs_from_article_md", return_value=["Hello world."]), \
             mock.patch.object(p2w, "label_for", return_value="L"), \
             mock.patch.object(p2w.os.path, "exists", return_value=False):
            html = p2w.public_study_html("/run", ART, level=level)
        return html, order, cc

    def test_a2_with_display_spec_has_exactly_one_part1_before_part2(self):
        html, order, cc = self._run("a2", {"a2": "LEARNING_ITEMS_123_V1"})
        self.assertEqual(html, "<P1/>|P2")
        self.assertEqual(html.count("<P1/>"), 1)
        self.assertEqual(order, ["p2", ("p1", "a2")])         # Part 2の確定→Part 1描画(従来のb1bと同じ順)。HTML上はPart 1→Part 2
        self.assertEqual(cc.calls, [("/run/a2/key_phrases", "a2", "part1")])

    def test_a2_without_display_spec_has_no_part1(self):
        html, order, cc = self._run("a2", {})
        self.assertEqual(html, "|P2")
        self.assertEqual(order, ["p2"])
        self.assertEqual(cc.calls, [])

    def test_b1b_unchanged_regardless_of_display_spec(self):
        for spec in ({}, {"b1b": "LEARNING_ITEMS_123_V1"}):
            html, order, cc = self._run("b1b", spec)
            self.assertEqual(html, "<P1/>|P2")
            self.assertEqual(order, ["p2", ("p1", "b1b")])
            self.assertEqual(cc.calls, [("/run/b1b/key_phrases", "b1b", "part1")])


if __name__ == "__main__":
    unittest.main()
