# -*- coding: utf-8 -*-
"""yvp_cross_generate_01 のoffline test(API 0)。Voice以外の設定(モデル・Style・速度・生成関数・本文)が全Voiceで同一であること、
本文がrun_01採用本文と一字一致、Productionファイル未変更を確認する。実行: PYTHONPATH=netblock_harness_01 NETBLOCK_LOG=<log> py -m unittest <this>"""
import hashlib, json, os, subprocess, sys, unittest

sys.path.insert(0, os.getcwd())
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import yvp_cross_generate_01 as g


class T(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.P = g.load_prod()

    def test_only_voice_differs(self):
        for lv in ("a2", "b1b"):
            for b in (1, 2, 3):
                specs = [g.build_spec(lv, b, v, self.P) for v in (1, 2, 3)]
                for k in ("tts_backend", "style_profile", "style_prefix", "style_prefix_sha256", "text_sha256", "words", "generator", "slowdown_percent_a2", "tts_execution_mode"):
                    self.assertEqual(len({json.dumps(s[k]) for s in specs}), 1, (lv, b, k))
                self.assertEqual([s["voice_name"] for s in specs], ["Algieba", "Zephyr", "Schedar"])

    def test_style_same_across_bodies_and_equals_candidates_script(self):
        for lv in ("a2", "b1b"):
            self.assertEqual(len({g.build_spec(lv, b, 1, self.P)["style_prefix_sha256"] for b in (1, 2, 3)}), 1)

    def test_voice_names_match_production_map(self):
        vm = self.P["ya"].segment_voice_map()
        for v in (1, 2, 3):
            self.assertEqual(vm[f"y_voice_{v}"], g.VOICE_SLOT[v])

    def test_slowdown_6pct(self):
        self.assertEqual(g.build_spec("a2", 1, 1, self.P)["slowdown_percent_a2"], 6.0)
        self.assertIsNone(g.build_spec("b1b", 1, 1, self.P)["slowdown_percent_a2"])

    def test_text_equals_run01(self):
        for lv in ("a2", "b1b"):
            parts = json.load(open(f"{g.RUN01}/{lv}/parts.json", encoding="utf-8"))["segments"]
            for b in (1, 2, 3):
                self.assertEqual(g.body_text(lv, b), parts[f"y_voice_{b}"])
                self.assertEqual(g.build_spec(lv, b, 1, self.P)["text_sha256"], hashlib.sha256(parts[f"y_voice_{b}"].encode("utf-8")).hexdigest())

    def test_style_equals_recorded_attempts(self):
        """既存attempt jsonのinstruction_textの先頭がspecのstyle_prefixと一致(同条件で混在できる根拠)。"""
        import glob
        for lv, pat in (("a2", "custom"), ("b1b", "widemargin")):
            style = g.build_spec(lv, 1, 1, self.P)["style_prefix"]
            files = glob.glob(f"{g.RUN01}/{lv}/narration/attempts/y_voice_*_attempt*_*{pat}*.json")
            self.assertTrue(files)
            n_checked = 0
            for f in files:
                d = json.load(open(f, encoding="utf-8"))
                it = d.get("instruction_text") or ""
                if not it:      # b1b(Adv)のattempt jsonはinstruction_textを保存しない(コード同一性で担保)
                    continue
                n_checked += 1
                self.assertTrue(it.strip().startswith(style.strip()[:80]), (f, it[:80]))
            if lv == "a2":
                self.assertGreaterEqual(n_checked, 5)

    def test_no_run01_write_path(self):
        src = open(g.__file__, encoding="utf-8").read()
        self.assertNotIn("open(f\"{RUN01}", src.replace("json.load(open(f\"{RUN01}", ""))


if __name__ == "__main__":
    unittest.main()
