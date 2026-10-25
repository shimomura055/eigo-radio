# -*- coding: utf-8 -*-
"""KP Human Review: 隔離・既定動作のtest(API 0、決定論)。
(1) 共有関数 sc.run_key_phrases / run_key_phrase_redundancy_qa が無変更(A/B/C・Y Trialは従来の3件経路のまま)
(2) er119 moduleをimportするProductionファイルはX/Zのrunnerだけ(他Family・共有moduleへ混入しない)
(3) 自動確定の読取点は宣言ファイルのみ(環境変数・hooks・設定dictから読まない)
(4) 宣言なし=待機(rc=4)が既定であることのGrep確認
実行: .venv\\Scripts\\python.exe -m unittest er119_isolation_test_01 -v"""
from __future__ import annotations

import test_state_isolation_01  # noqa: F401

import glob
import hashlib
import inspect
import os
import re
import unittest

import er003_v1_n3_01_scaffold_generate as sc
import er119_kp_human_review_01 as rv

ROOT = os.path.dirname(os.path.abspath(__file__))
RUN_KEY_PHRASES_SHA256 = "f0d65c78b834d6c86c84ed2669bcd17700a2cee051c32f4f27dd147c3c789e6e"   # KP Human Review導入時点(HEADと同一)の関数source
REDUNDANCY_QA_SHA256 = "8fae6027180787861be401ef4d091789a15b6d53bedfdf5fef56f89d95e1f374"


def _sha(fn) -> str:
    return hashlib.sha256(inspect.getsource(fn).encode("utf-8")).hexdigest()


class TestSharedFunctionsUnchanged(unittest.TestCase):
    def test_run_key_phrases_is_unchanged(self):
        self.assertEqual(_sha(sc.run_key_phrases), RUN_KEY_PHRASES_SHA256,
                         "共有関数 sc.run_key_phrases が変更されました(A/B/C・Y Trialの3件経路を変えない。KP Human Reviewはer119側で完結する)")

    def test_run_key_phrase_redundancy_qa_is_unchanged(self):
        self.assertEqual(_sha(sc.run_key_phrase_redundancy_qa), REDUNDANCY_QA_SHA256)


class TestImportersAreOnlyXZRunners(unittest.TestCase):
    ALLOWED = {"er019_family_x_audio_production_runner_01.py", "er026_family_z_fiction_production_runner_01.py"}

    def test_only_x_z_runners_import_er119(self):
        offenders = []
        for p in glob.glob(os.path.join(ROOT, "*.py")):
            b = os.path.basename(p)
            if b.startswith("er119_") or "test" in b:
                continue
            with open(p, encoding="utf-8", errors="ignore") as f:
                if re.search(r"^\s*(import|from)\s+er119_", f.read(), re.M) and b not in self.ALLOWED:
                    offenders.append(b)
        self.assertEqual(offenders, [])

    def test_grammar_kind_not_referenced_by_production(self):
        for b in self.ALLOWED:
            with open(os.path.join(ROOT, b), encoding="utf-8", errors="ignore") as f:
                self.assertNotIn("KIND_GRAMMAR", f.read(), b)


class TestSingleReadPointAndDefaultWait(unittest.TestCase):
    def _src(self, name):
        with open(os.path.join(ROOT, name), encoding="utf-8", errors="ignore") as f:
            return f.read()

    def test_auto_mode_is_read_only_in_read_mode_declaration(self):
        core = self._src("er119_kp_human_review_01.py")
        self.assertEqual(len(re.findall(r"def read_mode_declaration\(", core)), 1)
        self.assertNotIn("os.environ", core)
        self.assertNotIn("getenv", core)
        for name in ("er119_kp_candidates_01.py", "er119_kp_wiring_01.py", "er119_kp_prompt_2v_01.py"):
            s = self._src(name)
            self.assertNotIn("os.environ", s, name)
            self.assertNotIn("getenv", s, name)

    def test_runner_defaults_are_wait(self):
        x, z = self._src("er019_family_x_audio_production_runner_01.py"), self._src("er026_family_z_fiction_production_runner_01.py")
        for s in (x, z):
            self.assertRegex(s, r'add_argument\("--kp-review", default=None, choices=\("wait", "auto"\)')
            self.assertIn('if args.kp_review == "auto"', s)   # 宣言を書くのは明示引数のときだけ
        # 起動script・.envで暗黙にONにしない
        for p in glob.glob(os.path.join(ROOT, "*.bat")) + glob.glob(os.path.join(ROOT, "*.sh")) + [os.path.join(ROOT, ".env")]:
            if os.path.exists(p):
                with open(p, encoding="utf-8", errors="ignore") as f:
                    self.assertNotIn("--kp-review auto", f.read(), p)

    def test_exit_code_and_marker_constants(self):
        self.assertEqual(rv.EXIT_CODE_PENDING, 4)
        self.assertEqual(rv.PENDING_MARKER, "[KP_REVIEW_PENDING]")


if __name__ == "__main__":
    unittest.main()
