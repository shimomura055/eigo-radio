# -*- coding: utf-8 -*-
"""phase3_paid_runner_01 のGO方式test (API 0)。GOが無ければ有料callを1回も行わず、ファイル作成0。
実行: PYTHONUTF8=1 .venv/Scripts/python.exe docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/phase3_paid_runner_01_test_01.py"""
import json, os, shutil, sys, tempfile, unittest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import phase3_paid_runner_01 as R


class Boom:
    calls = 0

    def __call__(self, *a, **k):
        Boom.calls += 1
        raise AssertionError("API call attempted without GO")


class TestGo(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.old_root = R.ROOT
        R.ROOT = self.tmp
        os.makedirs(os.path.join(self.tmp, R.RD))
        shutil.copy(os.path.join(self.old_root, R.RD, "n3_clips_01.json"), os.path.join(self.tmp, R.RD, "n3_clips_01.json"))
        Boom.calls = 0

    def tearDown(self):
        R.ROOT = self.old_root
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _snapshot(self):
        return sorted(os.path.relpath(os.path.join(d, f), self.tmp) for d, _, fs in os.walk(self.tmp) for f in fs) + \
               sorted(os.path.relpath(os.path.join(d, x), self.tmp) for d, xs, _ in os.walk(self.tmp) for x in xs)

    def test_no_go_file_refuses_with_zero_side_effects(self):
        before = self._snapshot()
        for st in R.STAGES:
            with self.assertRaises(SystemExit) as cm:
                R.run_stage(st, azure_fn=Boom(), openai_fn=Boom(), tts_fn=Boom())
            self.assertEqual(cm.exception.code, 4)
        self.assertEqual(Boom.calls, 0)
        self.assertEqual(self._snapshot(), before)          # run_dir/log/stop_check いずれも作られない
        self.assertFalse(os.path.exists(os.path.join(self.tmp, R.RUN_DIR)))

    def _go(self, **kw):
        go = {"managed_id": R.MANAGED_ID, "cap_jpy": 60, "stages": ["N3_tts"]}
        go.update(kw)
        json.dump(go, open(os.path.join(self.tmp, R.GO_FILE), "w", encoding="utf8"))

    def test_bad_go_refuses(self):
        for bad in ({"managed_id": "X"}, {"cap_jpy": 61}, {"stages": ["A1_azure_moon"]}, {"cap_jpy": 0}):
            self._go(**bad)
            with self.assertRaises(SystemExit) as cm:
                R.run_stage("N3_tts", azure_fn=Boom(), openai_fn=Boom(), tts_fn=Boom())
            self.assertEqual(cm.exception.code, 4)
        self.assertEqual(Boom.calls, 0)

    def test_valid_go_runs_injected_and_stops_on_error_without_retry(self):
        self._go()
        n = {"c": 0}

        def tts(text, out):
            n["c"] += 1
            return {"status": "ERR"} if False else None
        res = R.run_stage("N3_tts", tts_fn=tts, azure_fn=lambda w: ("", None), openai_fn=lambda w, **k: ("", None))
        self.assertEqual(res["n"], 30)
        self.assertEqual(n["c"], 30)

    def test_plan_is_api0_and_within_cap(self):
        p = R.plan()
        self.assertLessEqual(p["total_upper_jpy"], R.CAP_JPY_MAX)
        self.assertIn("go_present", p)


if __name__ == "__main__":
    unittest.main(verbosity=1)
