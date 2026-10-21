# -*- coding: utf-8 -*-
"""委任_05 C-1: S5(`【概数表記】`タグ漏れ検知)のTrial環境検証(API 0、Production file無変更)。
修正後の検知regex(S5版 TAG_LEAK_RE / MARK_RE)を本ファイルに複製し、ProductionのWriter関数(strip_tags/assert_no_tag_leak/clean_ja_for_next)の
module globalをmonkeypatchして挙動を実測する(Production sourceは編集しない)。
  (i)  `【概数表記】`残留を含むWriter出力fixture -> 現行Productionは未検知(Before)、S5版は検知+除去(After)
  (ii) 誤発火0: Trial2の12arm出力 + 記事A/B等の既存Production本文(正常文)で、S5版の検知結果が現行と完全一致(新たな検知0)
実行: .venv/Scripts/python.exe er090_b3_core_number_rounding_trial_03_s5.py   (証跡: er090_output/.../evidence/s5_trial_result_01.json)
      .venv/Scripts/python.exe -m pytest er090_b3_core_number_rounding_trial_03_s5.py -q
"""
from __future__ import annotations

import glob
import json
import os
import re
import unittest

import er053_family_x_factlock_ja_writer_01 as w1

HERE = os.path.dirname(os.path.abspath(__file__))
EVID = os.path.join(HERE, "er090_output", "b3_core_number_rounding_trial_02", "evidence", "s5_trial_result_01.json")

# ---- S5版(C-2でProductionへ入れる予定の2行。現行 w1.TAG_LEAK_RE:102 / w1.MARK_RE:98 に `概数表記` を追加するのみ)----
S5_TAG_LEAK_RE = re.compile(r"【\s*(?:事実|[FＦ]|中核数値|周辺数値|概数表記)[^】\n]{0,30}】")
S5_MARK_RE = re.compile(r"【(?:中核数値|周辺数値|\s*概数表記\s*)】")   # 概数表記のみ前後空白を許容(空白入り漏れでSTOPを増やさない)


class patched:
    """w1のmodule globalをS5版へ一時差替え(with内のみ)。Production sourceは無改変。"""
    def __enter__(self):
        self.old = (w1.TAG_LEAK_RE, w1.MARK_RE)
        w1.TAG_LEAK_RE, w1.MARK_RE = S5_TAG_LEAK_RE, S5_MARK_RE
        return self

    def __exit__(self, *a):
        w1.TAG_LEAK_RE, w1.MARK_RE = self.old


# 漏れfixture(Writer出力で起こりうる形。タグの位置・複数・全角空白入り・事実タグ併存)
LEAK_FIXTURES = [
    ("sentence_head", "【概数表記】約13万5千人が参加しました【事実2】。"),
    ("after_number", "最大約13万5千人【概数表記】が対象でした【事実2】。"),
    ("multi", "約13万人【概数表記】と、約5千人【概数表記】です【事実2】。"),
    ("with_space", "約13万5千人【 概数表記 】でした【事実2】。"),
    ("alone_line", "給料の話です【事実1】。\n【概数表記】\n約13万5千人でした【事実2】。"),
]
# 正常文(タグ語を含まない/含んでも無関係な【】: 【速報】等は残す)
CLEAN_SAMPLES = [
    "約13万5千人が参加しました。",
    "【速報】最大約13万5千人が対象になりました。",
    "概数表記という言葉自体は、タグではなくただの語句です。",
    "「概数表記」の説明をしました。",          # 鉤括弧(【】ではない)
    "【注目】数字の話です【事実3】。",           # 事実タグは従来どおり検知(S5と無関係)
]


def corpus_files():
    pats = [os.path.join(HERE, "er090_output", "b3_core_number_rounding_trial_02", "phase2", "*", "*", "**", "*.md"),
            os.path.join(HERE, "er019_output", "**", "ja_writer", "revision2.md"),
            os.path.join(HERE, "er019_output", "**", "ja_writer", "original.md"),
            os.path.join(HERE, "er019_output", "**", "ja_writer", "factlock", "r0_with_tags.md"),
            os.path.join(HERE, "er019_output", "**", "b1b", "article.md"),
            os.path.join(HERE, "er019_output", "**", "a2", "article.md")]
    out = set()
    for p in pats:
        out.update(glob.glob(p, recursive=True))
    return sorted(out)


def run_checks() -> dict:
    res = {"leak_fixtures": [], "clean_samples": [], "corpus": {}}
    for name, text in LEAK_FIXTURES:
        before_detect = bool(w1.TAG_LEAK_RE.search(text) and "概数表記" in "".join(w1.TAG_LEAK_RE.findall(text)))
        try:
            w1.assert_no_tag_leak(text.replace("【事実2】", "").replace("【事実1】", ""))
            before_assert = "PASS(未検知)"
        except w1.TagLeak:
            before_assert = "TagLeak"
        with patched():
            raw_flag = "概数表記" in "".join(w1.TAG_LEAK_RE.findall(text))
            try:
                w1.assert_no_tag_leak(text.replace("【事実2】", "").replace("【事実1】", ""))
                after_assert = "PASS(未検知)"
            except w1.TagLeak:
                after_assert = "TagLeak(検出)"
            cleaned = w1.clean_ja_for_next(text)
            echoed = len(w1.MARK_RE.findall(text))
        res["leak_fixtures"].append({"name": name, "before_regex_detects_概数表記": before_detect, "before_assert_on_raw_without_fact_tags": before_assert,
                                     "after_regex_detects_概数表記": raw_flag, "after_assert_on_raw_without_fact_tags": after_assert,
                                     "after_clean_residue_概数表記": "概数表記" in cleaned, "marks_echoed_counted": echoed})
    for text in CLEAN_SAMPLES:
        old = w1.TAG_LEAK_RE.findall(text)
        with patched():
            new = w1.TAG_LEAK_RE.findall(text)
        res["clean_samples"].append({"text": text, "old_matches": old, "new_matches": new, "same": old == new})
    n_files = n_diff = n_contains_marker = 0
    diffs = []
    for p in corpus_files():
        t = open(p, encoding="utf-8", errors="replace").read()
        old = w1.TAG_LEAK_RE.findall(t)
        old_m = w1.MARK_RE.findall(t)
        with patched():
            new = w1.TAG_LEAK_RE.findall(t)
            new_m = w1.MARK_RE.findall(t)
        n_files += 1
        n_contains_marker += int("概数表記" in t)
        if old != new or old_m != new_m:
            n_diff += 1
            diffs.append(os.path.relpath(p, HERE))
    res["corpus"] = {"n_files": n_files, "n_files_with_概数表記_substring": n_contains_marker,
                     "n_files_where_S5_changes_detection": n_diff, "changed_files": diffs[:20]}
    res["PASS"] = (all(f["before_regex_detects_概数表記"] is False and f["after_regex_detects_概数表記"] is True and f["after_clean_residue_概数表記"] is False
                       and f["after_assert_on_raw_without_fact_tags"] == "TagLeak(検出)" for f in res["leak_fixtures"])
                   and all(c["same"] for c in res["clean_samples"]) and n_diff == 0 and n_files > 0)
    return res


class S5Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = run_checks()

    def test_current_production_does_not_detect(self):
        self.assertTrue(all(f["before_regex_detects_概数表記"] is False for f in self.r["leak_fixtures"]))

    def test_s5_detects_and_cleans_leaks(self):
        for f in self.r["leak_fixtures"]:
            self.assertTrue(f["after_regex_detects_概数表記"], f["name"])
            self.assertEqual(f["after_assert_on_raw_without_fact_tags"], "TagLeak(検出)", f["name"])
            self.assertFalse(f["after_clean_residue_概数表記"], f["name"])
            self.assertGreaterEqual(f["marks_echoed_counted"], 1, f["name"])

    def test_no_false_positive_on_clean_samples(self):
        self.assertTrue(all(c["same"] for c in self.r["clean_samples"]))

    def test_no_false_positive_on_corpus(self):
        self.assertGreater(self.r["corpus"]["n_files"], 100)
        self.assertEqual(self.r["corpus"]["n_files_where_S5_changes_detection"], 0, self.r["corpus"]["changed_files"])

    def test_production_source_unchanged(self):
        self.assertNotIn("概数表記", w1.TAG_LEAK_RE.pattern)       # C-1ではProduction無変更(C-2で+2行)
        self.assertNotIn("概数表記", w1.MARK_RE.pattern)

    def test_overall_pass(self):
        self.assertTrue(self.r["PASS"])


if __name__ == "__main__":
    r = run_checks()
    json.dump(r, open(EVID, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in r.items() if k != "leak_fixtures"}, ensure_ascii=False)[:1500])
    print("PASS" if r["PASS"] else "FAIL")
