# -*- coding: utf-8 -*-
import re
import subprocess
import unittest

import er086_writer_detective_avoidance_trial_01_lib as lib

PROD_FILES = ["er003_v1_en_direct_vfl_01_generate.py", "er019_family_x_entertainment_production_runner_01.py",
              "er053_family_x_factlock_ja_writer_01.py", "er003_v1_n3_01_advanced_adaptation_generate.py",
              "er003_v1_n3_01_standard_a2_generate.py", "er012_e_family_entertainment_two_level_runner_01.py"]


class T(unittest.TestCase):
    def test_pattern_text_byte_match_user_original(self):
        txt = lib.read_text(lib.USER_MD)
        quotes = re.findall(r"^> (.+)$", txt, re.M)
        self.assertEqual(len(quotes), 3)
        for k, q in zip("ABC", quotes):
            self.assertEqual(lib.PATTERN_TEXT[k].encode("utf-8"), q.encode("utf-8"), k)

    def _prompts(self):
        import er003_v1_n3_01_advanced_adaptation_generate as adv
        import er003_v1_n3_01_standard_a2_generate as std
        import er053_family_x_factlock_ja_writer_01 as w1
        return {
            "r0": w1.build_r0_prompt("t", "f"),
            "r1r2": w1.USER_TMPL.format(body="BODY"),
            "tr": adv.build_family_x_faithful_translation_prompt("JAARTICLE"),
            "iol": adv.build_family_x_in_one_line_prompt("T", "B", ja_text="JA", ledger_text="LED"),
            "std": std.build_family_x_no_heading_prompt("ADVART"),
        }

    def test_injection_in_all_stages_and_restored(self):
        import er053_family_x_factlock_ja_writer_01 as w1
        base = self._prompts()
        f_before = (w1.build_r0_prompt, w1.call_astra, w1.call_luna_r0, w1.USER_TMPL)
        for pat, add in lib.PATTERN_TEXT.items():
            with lib.injected(pat):
                p = self._prompts()
            for k, v in p.items():
                self.assertEqual(v.count(add), 1, (pat, k))
                self.assertEqual(v.replace("\n\n" + add, "", 1), base[k], (pat, k, "追加以外の差分なし"))
            # 位置: 翻訳/IOL/Standardは記事本文より前
            self.assertLess(p["tr"].index(add), p["tr"].index("[Japanese article]"))
            self.assertLess(p["std"].index(add), p["std"].index("[Article]"))
            self.assertLess(p["iol"].index(add), p["iol"].index("[Japanese source article]"))
            self.assertTrue(p["r0"].endswith(add))
            self.assertTrue(p["r1r2"].endswith(add))
        self.assertEqual(f_before, (w1.build_r0_prompt, w1.call_astra, w1.call_luna_r0, w1.USER_TMPL))
        self.assertEqual(self._prompts(), base)

    def test_production_files_unchanged_vs_head(self):
        r = subprocess.run(["git", "status", "--porcelain"] + PROD_FILES, capture_output=True, text=True, cwd=lib.ROOT)
        self.assertEqual(r.stdout.strip(), "", r.stdout)

    def test_grep_counts(self):
        c = lib.count_detective("A detective and Detectives. 探偵. DETECTIVE-like")
        self.assertEqual(c["substring_ci"], 3)
        self.assertEqual(c["word_ci"], 2)       # "detective", "DETECTIVE"-like (word boundary at '-')
        self.assertEqual(c["derivatives_ci"], 1)
        self.assertEqual(c["ja_tantei"], 1)
        self.assertEqual(lib.count_detective("no such word")["substring_ci"], 0)


if __name__ == "__main__":
    unittest.main()
