# -*- coding: utf-8 -*-
"""b3_annotation_check_01 / b3_annotation_merge_01 (仕様 v2) の単体テスト (LLM・API不使用)。
実行: .venv/Scripts/python.exe -X utf8 -m unittest er052_output.factlock_astra_e2e_trial_01.b3_annotation_check_01_test
(または同ディレクトリで python -m unittest b3_annotation_check_01_test)"""
import copy
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import b3_annotation_check_01 as chk  # noqa: E402
import b3_annotation_merge_01 as mrg  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
FW_DIR = os.path.join(ROOT, "er052_output", "factlock_writer_trial_01")

LEDGER = """[VERIFIED] A-001: 中央銀行は2026年9月16日、政策金利を0.25％引き下げ、4.00％にした。
  scope: 国内
  numeric_value: 0.25% (引き下げ幅)、4.00% (引き下げ後)
  date_or_period: 2026年9月16日

[VERIFIED] A-002: 次回会合は2026年10月28日に開かれる。ローンの変動金利は据え置き候補。
  date_or_period: 2026年10月28日

[VERIFIED] A-003: 条約第4条は大量破壊兵器の配備を禁止する。
  date_or_period: 1967年発効
"""
BRIEF = """# Selected Fact Brief

## Storyline
中央銀行が2026年9月に政策金利を0.25％下げた。

## Selected Facts
- 中央銀行は2026年9月16日、政策金利を0.25％引き下げ、4.00％にした。
- 次回会合は2026年10月28日に開かれる。
"""
# v2: n=4概念 -> 上限3。優先順 Storyline量(0.25) -> その他の量(4.00) -> 日付(2026年9月[16日]) の3概念が中核、2026年10月28日は周辺
ANNOT = """# Selected Fact Brief

## Storyline
中央銀行が2026年9月【中核数値】に政策金利を0.25％【中核数値】下げた。

## Selected Facts
- 【事実1】中央銀行は2026年9月16日【中核数値】、政策金利を0.25％【中核数値】引き下げ、4.00％【中核数値】にした。
- 【事実2】次回会合は2026年10月28日【周辺数値】に開かれる。
"""


def N(surface, cls, kind, concept, ids, **kw):
    d = {"surface": surface, "class": cls, "kind": kind, "concept": concept, "ledger_ids": ids}
    d.update(kw)
    return d


SIDE = {
    "annotator": "A",
    "facts": [{"n": 1, "ledger_ids": ["A-001"]}, {"n": 2, "ledger_ids": ["A-002"]}],
    "numbers": [
        N("2026年9月16日", "core", "date_time", "C_date", ["A-001"]),
        N("2026年9月", "core", "date_time", "C_date", ["A-001"]),
        N("0.25％", "core", "magnitude", "C_cut", ["A-001"]),
        N("4.00％", "core", "magnitude", "C_level", ["A-001"]),
        N("2026年10月28日", "peripheral", "date_time", "C_next", ["A-002"]),
    ],
}


def _run(brief=BRIEF, annot=ANNOT, side=SIDE, ledger=LEDGER, **kw):
    return chk.run(brief, annot, ledger, side, **kw)


def _side(**over):
    s = copy.deepcopy(SIDE)
    s.update(over)
    return s


class SyntheticTests(unittest.TestCase):
    def test_happy_path_passes(self):
        r = _run()
        self.assertEqual(r["verdict"], "PASS", json.dumps(r, ensure_ascii=False, indent=1))
        self.assertEqual(r["a_strip_equal"]["status"], "PASS")
        self.assertEqual(r["d_sequence"]["fact_numbers"], [1, 2])
        c = r["c_numbers"]
        self.assertEqual(c["core_cap"], 3)
        self.assertEqual(c["expected_core_concepts"], ["C_cut", "C_level", "C_date"])  # 優先順: Storyline量 -> 他の量 -> 日付

    def test_deletion_in_annotated_text_fails_strip_equality(self):
        r = _run(annot=ANNOT.replace("引き下げ、", "下げ、"))
        self.assertEqual(r["a_strip_equal"]["status"], "FAIL")
        self.assertEqual(r["verdict"], "FAIL")

    def test_non_sequential_tags_fail(self):
        r = _run(annot=ANNOT.replace("【事実2】", "【事実3】"))
        self.assertEqual(r["d_sequence"]["status"], "FAIL")

    def test_compound_tag_forbidden(self):
        r = _run(annot=ANNOT.replace("【事実2】", "【事実2,3】"))
        self.assertEqual(r["d_sequence"]["status"], "FAIL")
        self.assertTrue(any("複合タグ" in p for p in r["d_sequence"]["problems"]))

    def test_unclassified_number_detected(self):
        side = _side(numbers=[n for n in SIDE["numbers"] if n["surface"] != "4.00％"])
        r = _run(side=side)
        self.assertEqual(r["c_numbers"]["status"], "FAIL")
        self.assertTrue(any("分類漏れ" in p for p in r["c_numbers"]["problems"]))

    def test_core_number_not_in_ledger_fails(self):
        side = _side()
        side["numbers"][2]["ledger_ids"] = ["A-002"]   # 0.25％はA-002に無い
        r = _run(side=side)
        self.assertEqual(r["c_numbers"]["status"], "FAIL")

    def test_wrong_mark_class_detected(self):
        r = _run(annot=ANNOT.replace("4.00％【中核数値】", "4.00％【周辺数値】"))
        self.assertTrue(any("印の不一致" in p for p in r["c_numbers"]["problems"]))

    def test_missed_core_detected_when_eligible_and_within_cap(self):
        # 適格 (E1) かつ上限内なのに周辺と宣言 = 付け漏れ
        side = _side()
        side["numbers"][3]["class"] = "peripheral"
        annot = ANNOT.replace("4.00％【中核数値】", "4.00％【周辺数値】")
        r = _run(annot=annot, side=side)
        self.assertEqual(r["c_numbers"]["status"], "FAIL")
        self.assertTrue(any("付け漏れ" in p for p in r["c_numbers"]["problems"]), r["c_numbers"]["problems"])

    def test_declared_core_beyond_cap_is_wrong(self):
        side = _side()
        side["numbers"][4]["class"] = "core"           # C_next は優先順で4番目 -> 上限3の外
        annot = ANNOT.replace("2026年10月28日【周辺数値】", "2026年10月28日【中核数値】")
        r = _run(annot=annot, side=side)
        self.assertEqual(r["c_numbers"]["status"], "FAIL")
        self.assertTrue(any("上限" in p for p in r["c_numbers"]["problems"]), r["c_numbers"]["problems"])
        self.assertEqual(r["c_numbers"]["cap_dropped_concepts"], ["C_next"])
        self.assertEqual(r["c_numbers"]["cap_dropped_count"], 1)

    def test_name_embedded_number_cannot_be_core(self):
        brief = BRIEF.replace("次回会合", "COSMOS 1408の次回会合")
        annot = ANNOT.replace("次回会合", "COSMOS 1408【中核数値】の次回会合")
        side = _side()
        side["numbers"].append(N("COSMOS 1408", "core", "name_embedded", "N1", ["A-002"]))
        r = _run(brief=brief, annot=annot, side=side)
        self.assertEqual(r["c_numbers"]["status"], "FAIL")

    def test_json_side_checked(self):
        orig = {"selected_fact_brief_text": "- A。\n- B。", "x": 1}
        good = {"selected_fact_brief_text": "- 【事実1】A。\n- 【事実2】B。", "x": 1}
        self.assertEqual(chk.check_json(good, orig, "", None)["status"], "PASS")
        bad = {"selected_fact_brief_text": "- 【事実1】A!。\n- 【事実2】B。", "x": 1}
        self.assertEqual(chk.check_json(bad, orig, "", None)["status"], "FAIL")
        bad2 = {"selected_fact_brief_text": "- 【事実1】A。\n- 【事実2】B。", "x": 2}
        self.assertEqual(chk.check_json(bad2, orig, "", None)["status"], "FAIL")

    def test_core_json_is_harness_compatible(self):
        cj = chk.build_core_json(SIDE)
        lits = [l for c in cj["core"] for l in c["literals"]]
        self.assertIn("0.25％", lits)
        self.assertIn("2026年10月28日", cj["peripheral"])

    # ---- v2 新規 ----
    def test_digit_normalization(self):
        self.assertEqual(chk.digit_runs("先頭の04日と4.00％と1,500個と０．２５％"), ["4", "4", "1500", "0.25"])
        self.assertEqual(chk.main_numbers("1バレル85ドル", "magnitude"), ["85"])
        self.assertEqual(chk.main_numbers("3〜5％", "range"), ["3", "5"])
        self.assertEqual(chk.main_numbers("1,500個超", "magnitude"), ["1500"])

    def _elig(self, surface, kind, ledger_text, ids):
        led = chk.parse_ledger(ledger_text)
        sch = chk.ledger_schema(led)
        it = {"surface": surface, "kind": kind, "ledger_ids": ids}
        return chk._item_eligibility(it, led, sch)

    def test_e1_main_number_only_no_intersection(self):
        led = "[VERIFIED] X-001: Brentは1バレル85ドル。\n  numeric_value: $85/バレル超\n"
        self.assertEqual(self._elig("1バレル85ドル", "magnitude", led, ["X-001"]), "E1")
        # 単位側の数字(1)だけが台帳にあっても適格にならない (交差の緩さ廃止)
        led2 = "[VERIFIED] X-001: 1バレルあたり。\n  numeric_value: 1バレル\n"
        self.assertIsNone(self._elig("1バレル85ドル", "magnitude", led2, ["X-001"]))

    def test_e1_numeric_scope_is_excluded(self):
        led = "[VERIFIED] X-001: 率20%\n  numeric_value: 20% (numeric_scope: 7月13日の取引、85ドルの水準)\n"
        self.assertEqual(self._elig("20％", "magnitude", led, ["X-001"]), "E1")
        self.assertIsNone(self._elig("85ドル", "magnitude", led, ["X-001"]))   # scope内の数字では適格にならない
        self.assertIsNone(self._elig("7月13日", "magnitude", led, ["X-001"]))

    def test_e1_decimal_normalization(self):
        led = "[VERIFIED] X-001: 利下げ\n  numeric_value: 4.00%, 04\n"
        self.assertEqual(self._elig("4％", "magnitude", led, ["X-001"]), "E1")

    def test_e2prime_iso_and_japanese_dates(self):
        iso = "[VERIFIED] H-001: 投稿\n  date_or_period: 2026-07-13 10:16 EDT\n"
        ja = "[VERIFIED] H-001: 発言\n  date_or_period: 2026年9月14日発言、2026年9月15日公式掲載\n"
        self.assertEqual(self._elig("7月13日午前10時16分", "date_time", iso, ["H-001"]), "E2p")
        self.assertEqual(self._elig("7月13日", "date_time", iso, ["H-001"]), "E2p")
        self.assertIsNone(self._elig("7月14日", "date_time", iso, ["H-001"]))
        self.assertIsNone(self._elig("7月13日午前11時4分", "date_time", iso, ["H-001"]))
        self.assertEqual(self._elig("2026年9月14日", "date_time", ja, ["H-001"]), "E2p")
        self.assertEqual(self._elig("2026年9月", "date_time", ja, ["H-001"]), "E2p")
        self.assertIsNone(self._elig("2026年9月15日", "date_time", ja, ["H-001"]))   # 先頭の日付表現のみ
        self.assertIsNone(self._elig("2026年", "date_time", ja, ["H-001"]))           # 年のみは対象外
        self.assertIsNone(self._elig("14日", "date_time", ja, ["H-001"]))             # 月のない表記は対象外

    def test_e2prime_does_not_require_storyline(self):
        side = _side()
        side["numbers"] = [n for n in side["numbers"] if n["surface"] != "2026年9月"]
        annot = ANNOT.replace("2026年9月【中核数値】に", "2026年9月に")
        brief = BRIEF.replace("中央銀行が2026年9月に", "中央銀行が2026年9月に")
        side["numbers"].append(N("2026年9月", "core", "date_time", "C_date", ["A-001"]))
        r = _run(side=side)                                      # Storylineに出る版
        self.assertEqual(r["c_numbers"]["eligibility"]["C_date"], ["E2p"])
        # Storylineに日付が無くても日付は適格 (E2')
        brief2 = BRIEF.replace("中央銀行が2026年9月に", "中央銀行が")
        annot2 = ANNOT.replace("2026年9月【中核数値】に", "")
        side2 = _side(numbers=[n for n in SIDE["numbers"] if n["surface"] != "2026年9月"])
        r2 = chk.run(brief2, annot2, LEDGER, side2)
        self.assertEqual(r2["c_numbers"]["eligibility"]["C_date"], ["E2p"], r2["c_numbers"])

    def test_split_insertion_reverse_and_layout(self):
        brief = "# Selected Fact Brief\n\n## Storyline\nS。\n\n## Selected Facts\nA。B。\n"
        annot = "# Selected Fact Brief\n\n## Storyline\nS。\n\n## Selected Facts\n- 【事実1】A。\n- 【事実2】B。\n"
        led = "[VERIFIED] X-001: A。\n[VERIFIED] X-002: B。\n"
        side = {"annotator": "A", "facts": [{"n": 1, "ledger_ids": ["X-001"]}, {"n": 2, "ledger_ids": ["X-002"]}], "numbers": []}
        r = chk.run(brief, annot, led, side)
        self.assertEqual(r["a_strip_equal"]["status"], "PASS_LAYOUT_NORMALIZED")
        self.assertEqual(r["a_strip_equal"]["inserted_bullet_markers"], 1)
        self.assertEqual(r["a_strip_equal"]["inserted_split_breaks"], 1)
        self.assertEqual(r["verdict"], "PASS", json.dumps(r, ensure_ascii=False, indent=1))

    def test_bullet_brief_split_does_not_fail(self):
        # 箇条書きbriefでも 。 直後の \n- 挿入による分割はPASS (v1 の §1 と harness の矛盾の解消)
        brief = "# B\n\n## Storyline\nS。\n\n## Selected Facts\n- A。B。\n- C。\n"
        annot = "# B\n\n## Storyline\nS。\n\n## Selected Facts\n- 【事実1】A。\n- 【事実2】B。\n- 【事実3】C。\n"
        led = "[VERIFIED] X-001: A。\n[VERIFIED] X-002: B。\n[VERIFIED] X-003: C。\n"
        side = {"annotator": "A", "facts": [{"n": i, "ledger_ids": [f"X-00{i}"]} for i in (1, 2, 3)], "numbers": []}
        r = chk.run(brief, annot, led, side)
        self.assertEqual(r["a_strip_equal"]["status"], "PASS_LAYOUT_NORMALIZED")
        self.assertEqual(r["verdict"], "PASS", json.dumps(r["a_strip_equal"], ensure_ascii=False))

    def test_hidden_edit_inside_section_is_detected(self):
        # v1 の全空白削除比較では見逃した 'COSMOS 1408' -> 'COSMOS1408' を検出する
        brief = "# B\n\n## Storyline\nS。\n\n## Selected Facts\n- COSMOS 1408が壊れた。\n"
        annot = "# B\n\n## Storyline\nS。\n\n## Selected Facts\n- 【事実1】COSMOS1408が壊れた。\n"
        r = chk.check_a(brief, annot)
        self.assertEqual(r["status"], "FAIL")

    def test_insertion_not_after_period_is_rejected(self):
        brief = "# B\n\n## Storyline\nS。\n\n## Selected Facts\n- AはBした、そしてCした。\n"
        annot = "# B\n\n## Storyline\nS。\n\n## Selected Facts\n- 【事実1】AはBした、\n- 【事実2】そしてCした。\n"
        self.assertEqual(chk.check_a(brief, annot)["status"], "FAIL")

    def test_fake_core_declaration_detected(self):
        side = _side()
        side["numbers"].append(N("9999個", "peripheral", "magnitude", "C_fake", ["A-001"]))
        r = _run(side=side)
        self.assertTrue(any("架空" in p for p in r["c_numbers"]["problems"]), r["c_numbers"]["problems"])

    def test_concept_bundling_defect_detected(self):
        side = _side()
        for n in side["numbers"]:
            if n["surface"] == "2026年9月":
                n["concept"] = "C_date_short"      # 短い表記が長い表記に含まれ台帳IDも共通なのに別概念
        r = _run(side=side)
        self.assertTrue(any("別概念" in p for p in r["c_numbers"]["problems"]), r["c_numbers"]["problems"])

    def test_concept_kind_is_checked_on_all_members(self):
        side = _side()
        for n in side["numbers"]:
            if n["surface"] == "2026年9月":
                n["kind"] = "year"
        r = _run(side=side)
        self.assertTrue(any("kind が割れている" in p for p in r["c_numbers"]["problems"]), r["c_numbers"]["problems"])

    def test_sidecar_sha_and_annotator_checked(self):
        side = _side(spec_sha256="aaa", brief_sha256="bbb")
        ok = _run(side=side, spec_sha256="aaa", brief_sha256="bbb")
        self.assertEqual(ok["e_sidecar_meta"]["status"], "PASS")
        bad = _run(side=side, spec_sha256="zzz", brief_sha256="bbb")
        self.assertEqual(bad["e_sidecar_meta"]["status"], "FAIL")
        self.assertEqual(bad["verdict"], "FAIL")
        bad2 = _run(side=_side(annotator="C", spec_sha256="aaa", brief_sha256="bbb"), spec_sha256="aaa", brief_sha256="bbb")
        self.assertEqual(bad2["e_sidecar_meta"]["status"], "FAIL")

    def test_ledger_schema_report_and_fallback(self):
        led = ("[VERIFIED] X-001: 価格は85ドル。\n  scope: s\n  numeric_value: 85ドル\n  date_or_period: 2026-07-13\n"
               "[VERIFIED] X-002: 件数は1,500個。\n  scope: s\n"
               "[UNVERIFIED] X-003: 他。\n  date_or_period: 2026年1月\n")
        sch = chk.ledger_schema(chk.parse_ledger(led))
        self.assertEqual(sch["field_counts"]["numeric_value"], 1)
        self.assertEqual(sch["per_record"]["X-002"]["fields"], ["scope"])
        self.assertTrue(any("X-002" in w and "numeric_value" in w for w in sch["warnings"]))   # 量を示す語があるのに欄無し
        self.assertEqual(sch["non_verified_ids"], ["X-003"])
        self.assertFalse(sch["numeric_value_fallback_to_statement"])
        # numeric_value 欄が台帳全体に無い場合: statement の主数字で代替し、全数値が黙って周辺にならない
        led2 = "[VERIFIED] M-001: ELLEは2026年9月8日に紹介し、150個を扱った。\n  scope: s\n  date_or_period: 2026年9月8日\n"
        l2 = chk.parse_ledger(led2)
        sch2 = chk.ledger_schema(l2)
        self.assertTrue(sch2["numeric_value_fallback_to_statement"])
        self.assertEqual(chk._item_eligibility({"surface": "150個", "kind": "magnitude", "ledger_ids": ["M-001"]}, l2, sch2), "E1")

    def test_non_verified_ledger_id_in_facts_fails(self):
        led = LEDGER.replace("[VERIFIED] A-002", "[PENDING] A-002")
        r = _run(ledger=led)
        self.assertEqual(r["b_ledger_mapping"]["status"], "FAIL")
        for st in ("NOT_VERIFIED", "REJECTED"):
            led = LEDGER.replace("[VERIFIED] A-002", "[%s] A-002" % st)
            self.assertEqual(_run(ledger=led)["b_ledger_mapping"]["status"], "FAIL", st)

    def test_ambiguous_ledger_id_in_facts_warns_with_flag(self):
        # 委任_10 運用明確化(c)
        led = LEDGER.replace("[VERIFIED] A-002", "[AMBIGUOUS] A-002")
        b = _run(ledger=led)["b_ledger_mapping"]
        self.assertEqual(b["status"], "PASS", b)
        self.assertTrue(b["warnings"])
        self.assertEqual(b["ambiguous_fact"], {"2": ["A-002"]})

    def test_hyphenless_ledger_id_in_text_not_counted_as_digits(self):
        # 委任_11: 括弧内のハイフン無し台帳ID(F02)の数字が「分類漏れ」と誤検出されない
        led = LEDGER.replace("A-002", "F02")
        side = copy.deepcopy(SIDE)
        for f in side["facts"]:
            f["ledger_ids"] = ["F02" if x == "A-002" else x for x in f["ledger_ids"]]
        for n in side["numbers"]:
            n["ledger_ids"] = ["F02" if x == "A-002" else x for x in n["ledger_ids"]]
        brief = BRIEF.replace("開かれる。", "開かれる（F02）。")
        annot = ANNOT.replace("開かれる。", "開かれる（F02）。")
        r = chk.run(brief, annot, led, side)
        self.assertFalse([p for p in r["c_numbers"]["problems"] if "分類漏れ" in p], r["c_numbers"])
        # 比較: 台帳に無いIDなら従来どおり数字として扱われる
        led2 = LEDGER
        r2 = chk.run(brief, annot, led2, SIDE)
        self.assertTrue([p for p in r2["c_numbers"]["problems"] if "分類漏れ" in p], r2["c_numbers"])

    def test_unmapped_claims_typed(self):
        side = _side(unmapped_claims=[{"text": "x", "type": "new_fact"}])
        self.assertEqual(_run(side=side)["e_sidecar_meta"]["unmapped_claims_by_type"], {"new_fact": 1})
        bad = _side(unmapped_claims=[{"text": "x", "type": "unknown"}])
        self.assertEqual(_run(side=bad)["e_sidecar_meta"]["status"], "FAIL")

    def test_stop_candidate_number_not_in_ledger_in_storyline(self):
        brief = BRIEF.replace("下げた。", "下げた。売上は777億個に達した。")
        annot = ANNOT.replace("下げた。", "下げた。売上は777億個【周辺数値】に達した。")
        side = _side()
        side["numbers"].append(N("777億個", "peripheral", "magnitude", "C_x", ["A-001"]))
        r = chk.run(brief, annot, LEDGER, side)
        self.assertTrue(r["c_numbers"]["stop_candidates"], r["c_numbers"])


class MergeTests(unittest.TestCase):
    LED = LEDGER
    BR = """# Selected Fact Brief

## Storyline
中央銀行が2026年9月に政策金利を0.25％下げた。

## Selected Facts
- 中央銀行は2026年9月16日、政策金利を0.25％引き下げた。次回会合は2026年10月28日に開かれる。
- 条約第4条は大量破壊兵器の配備を禁止する。
"""
    A_MD = """# Selected Fact Brief

## Storyline
中央銀行が2026年9月【中核数値】に政策金利を0.25％【中核数値】下げた。

## Selected Facts
- 【事実1】中央銀行は2026年9月16日【中核数値】、政策金利を0.25％【中核数値】引き下げた。
- 【事実2】次回会合は2026年10月28日【中核数値】に開かれる。
- 【事実3】条約第4条【周辺数値】は大量破壊兵器の配備を禁止する。
"""
    B_MD = """# Selected Fact Brief

## Storyline
中央銀行が2026年9月【中核数値】に政策金利を0.25％【中核数値】下げた。

## Selected Facts
- 【事実1】中央銀行は2026年9月16日【中核数値】、政策金利を0.25％【中核数値】引き下げた。次回会合は2026年10月28日【中核数値】に開かれる。
- 【事実2】条約第4条【周辺数値】は大量破壊兵器の配備を禁止する。
"""

    def _sides(self):
        nums = [N("2026年9月16日", "core", "date_time", "D1", ["A-001"]), N("2026年9月", "core", "date_time", "D1", ["A-001"]),
                N("0.25％", "core", "magnitude", "Q1", ["A-001"]), N("2026年10月28日", "core", "date_time", "D2", ["A-002"])]
        a = {"slug": "t", "annotator": "A", "spec_sha256": "s", "brief_sha256": "b",
             "facts": [{"n": 1, "ledger_ids": ["A-001"]}, {"n": 2, "ledger_ids": ["A-002"]}, {"n": 3, "ledger_ids": ["A-003"]}],
             "numbers": nums + [N("第4条", "peripheral", "ordinal", "N1", ["A-003"])]}
        b = {"slug": "t", "annotator": "B", "spec_sha256": "s", "brief_sha256": "b",
             "facts": [{"n": 1, "ledger_ids": ["A-001", "A-002"]}, {"n": 2, "ledger_ids": ["A-003"]}],
             "numbers": copy.deepcopy(nums) + [N("第4条", "peripheral", "name_embedded", "X9", ["A-003"])]}
        return a, b

    def test_merge_picks_coarser_split_and_recomputes(self):
        a, b = self._sides()
        r = mrg.merge(self.BR, self.LED, self.A_MD, a, self.B_MD, b, "s", "b")
        self.assertEqual(r["status"], "PASS", json.dumps(r["check_result"], ensure_ascii=False, indent=1))
        self.assertEqual(len(r["merged_sidecar"]["facts"]), 2)                       # 粗い方(B)の事実数
        self.assertEqual(r["merged_sidecar"]["facts"][0]["ledger_ids"], ["A-001", "A-002"])
        kinds = {n["surface"]: n["kind"] for n in r["merged_sidecar"]["numbers"]}
        self.assertEqual(kinds["第4条"], "name_embedded")                               # 種類の食い違いは中核不可側
        rules = [x["rule"] for x in r["resolution_log"]]
        self.assertIn("分割不一致->共通の境界(粗い方)", rules)
        self.assertIn("kind食い違い->中核不可側", rules)
        self.assertIn("中核/周辺は統合入力から再計算", rules)
        self.assertEqual(r["agreement"]["split_agreement_rate"], 0.5)                  # 2項目中1項目一致
        self.assertEqual(r["agreement"]["core_jaccard"], 1.0)
        self.assertEqual(r["merged_md"].count("【事実"), 2)
        self.assertEqual(chk.strip_tags(r["merged_md"]).replace("\n- ", "\n- "), chk.prep(self.BR))

    def test_merge_recomputes_class_from_inputs_not_from_declarations(self):
        a, b = self._sides()
        # A・B がともに「周辺」と宣言していても、サイドカー単独検査(付け漏れ)で止まる=統合に入らない
        for s in (a, b):
            s["numbers"][3]["class"] = "peripheral"
        a_md = self.A_MD.replace("2026年10月28日【中核数値】", "2026年10月28日【周辺数値】")
        b_md = self.B_MD.replace("2026年10月28日【中核数値】", "2026年10月28日【周辺数値】")
        with self.assertRaises(mrg.Stop):
            mrg.merge(self.BR, self.LED, a_md, a, b_md, b, "s", "b")

    def test_merge_stops_when_ledger_ids_have_empty_intersection(self):
        a, b = self._sides()
        b["facts"][1] = {"n": 2, "ledger_ids": ["A-002"]}      # 条約の事実: A=A-003 / B=A-002
        with self.assertRaises(mrg.Stop) as cm:
            mrg.merge(self.BR, self.LED, self.A_MD, a, self.B_MD, b, "s", "b")
        self.assertIn("共通部分が空", str(cm.exception))

    def test_aggregate_excludes_zero_core_articles_from_jaccard(self):
        res = [{"split_agreement_rate": 1.0, "core_jaccard": 0.5, "core_zero_article": False},
               {"split_agreement_rate": 0.5, "core_jaccard": None, "core_zero_article": True}]
        ag = mrg.aggregate(res)
        self.assertEqual(ag["core_jaccard_mean_over_nonzero"], 0.5)
        self.assertEqual(ag["core_zero_articles"], 1)
        self.assertEqual(ag["core_jaccard_articles"], 1)


@unittest.skipUnless(os.path.exists(os.path.join(FW_DIR, "briefs", "hormuz", "b2", "selected_brief_factlock.md")),
                     "既存artifactなし")
class RealArtifactTests(unittest.TestCase):
    """過去の手付け注記版(hormuz/space)を v2 の検査にかけた実測 (仕様の主張の裏取り)。"""

    def _read(self, *p):
        with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
            return f.read()

    def test_hormuz_past_annotation_is_consistent_with_v2(self):
        brief = self._read("er052_output", "open233_b3_trial_01", "runs", "hormuz", "nb", "V0", "b2", "storyline_b3", "selected_brief.md")
        annot = self._read("er052_output", "factlock_writer_trial_01", "briefs", "hormuz", "b2", "selected_brief_factlock.md")
        led = self._read("er052_output", "factlock_writer_trial_01", "runs", "hormuz", "control", "b2__factlock__r1", "research_ledger", "verified_fact_ledger.txt")
        side = {"annotator": "A",
                "facts": [{"n": 1, "ledger_ids": ["HF-002"]}, {"n": 2, "ledger_ids": ["HF-007"]}, {"n": 3, "ledger_ids": ["HF-009"]}],
                "numbers": [
                    N("20％", "core", "magnitude", "C1", ["HF-002", "HF-007"]),
                    N("約2.6％", "core", "magnitude", "C2", ["HF-009"]),
                    N("1バレル85ドル", "core", "magnitude", "C3", ["HF-009"]),
                    N("7月13日午前10時16分", "peripheral", "date_time", "D1", ["HF-002"]),
                    N("7月13日", "peripheral", "date_time", "D1", ["HF-002"]),
                    N("7月14日午前11時4分", "peripheral", "date_time", "D2", ["HF-007"]),
                    N("14日", "peripheral", "date_time", "D2", ["HF-007"])]}
        r = chk.run(brief, annot, led, side)
        self.assertEqual(r["verdict"], "PASS", json.dumps(r, ensure_ascii=False, indent=1))
        self.assertEqual(r["c_numbers"]["cap_dropped_count"], 2)   # 日付2概念は適格だが上限3で外れる

    def test_space_past_annotation_matches_v2_with_e2prime(self):
        brief = self._read("er052_output", "open233_b3_trial_01", "runs", "space_weapons", "nb", "V0", "b2", "storyline_b3", "selected_brief.md")
        annot = self._read("er052_output", "factlock_writer_trial_01", "briefs", "space_weapons", "b2", "selected_brief_factlock.md")
        led = self._read("er052_output", "factlock_writer_trial_01", "runs", "space_weapons", "control", "b2__factlock__r1", "research_ledger", "verified_fact_ledger.txt")
        side = {"annotator": "A",
                "facts": [{"n": 1, "ledger_ids": ["F-001"]}, {"n": 2, "ledger_ids": ["F-003"]}, {"n": 3, "ledger_ids": ["F-012"]},
                          {"n": 4, "ledger_ids": ["F-015"]}, {"n": 5, "ledger_ids": ["F-016"]}],
                "numbers": [
                    N("2026年9月14日", "core", "date_time", "C1", ["F-001"]),
                    N("2026年9月", "core", "date_time", "C1", ["F-001"]),
                    N("2021年11月15日", "core", "date_time", "C2", ["F-003"]),
                    N("1,500個超", "core", "magnitude", "C3", ["F-003"]),
                    N("COSMOS 1408", "peripheral", "name_embedded", "N1", ["F-003"]),
                    N("第4条", "peripheral", "ordinal", "N2", ["F-016"])]}
        r = chk.run(brief, annot, led, side)
        self.assertEqual(r["verdict"], "PASS", json.dumps(r["c_numbers"], ensure_ascii=False, indent=1))   # E2'で過去の人手注記と一致


import re  # noqa: E402
import b3_annotator_audit_01 as aud  # noqa: E402


class AnnotatorSpecAndToolsTests(unittest.TestCase):
    SPEC = os.path.join(HERE, "B3_ANNOTATION_SPEC_v2_ANNOTATOR.md")
    TPL = os.path.join(HERE, "ANNOTATION_DELEGATION_TEMPLATE_v2.md")

    def _blocks(self):
        with open(self.SPEC, encoding="utf-8") as f:
            t = f.read()
        return {k: re.search(r"```" + k + r"\n(.*?)\n```", t, re.S).group(1) for k in ("ledger", "brief", "annotated", "sidecar")}

    def test_spec_example_passes_the_checker(self):
        b = self._blocks()
        side = json.loads(b["sidecar"])
        side["spec_sha256"], side["brief_sha256"] = "x", "y"
        r = chk.run(b["brief"] + "\n", b["annotated"] + "\n", b["ledger"] + "\n", side, spec_sha256="x", brief_sha256="y")
        self.assertEqual(r["verdict"], "PASS", json.dumps(r, ensure_ascii=False, indent=1))
        self.assertEqual(r["c_numbers"]["core_cap"], 3)
        self.assertEqual(r["c_numbers"]["expected_core_concepts"], ["C_old", "C_new", "C_drop"])
        self.assertEqual(r["c_numbers"]["cap_dropped_count"], 3)   # C_users と 適格な日付2概念(C_date, C_locker)
        self.assertEqual(r["a_strip_equal"]["inserted_split_breaks"], 1)

    def test_annotator_spec_has_no_contamination_sources(self):
        with open(self.SPEC, encoding="utf-8") as f:
            t = f.read()
        for bad in ("annotate_briefs", "ANNOTATION_LOG", "astra_revise_matrix", "prep_inputs", "selected_brief_factlock",
                    "B3_ANNOTATION_SPEC_v1", "宇宙兵器", "ホルムズ", "ミニバッグ", "META", "旧4", "COSMOS", "Fall 2026", "MUSE-HC", "F-001", "HF-0", "2026年9月", "1バレル", "Brent", "Meta"):
            self.assertNotIn(bad, t, bad)

    def test_extract_output_and_fill_template(self):
        b = self._blocks()
        reply = ("=== ANNOTATED_BRIEF_BEGIN ===\n" + b["annotated"] + "\n=== ANNOTATED_BRIEF_END ===\n"
                 "=== SIDECAR_JSON_BEGIN ===\n" + b["sidecar"] + "\n=== SIDECAR_JSON_END ===\n")
        md, side = mrg.extract_output(reply)
        self.assertEqual(md, b["annotated"] + "\n")
        self.assertEqual(side["facts"][0]["ledger_ids"], ["ZZ-001"])
        self.assertEqual(mrg.extract_output("=== STOP ===\n理由X")[0], "STOP")
        with self.assertRaises(mrg.Stop):
            mrg.extract_output("関係ない返答")
        with open(self.TPL, encoding="utf-8") as f:
            tpl = f.read()
        out = mrg.build_delegation(tpl, "A", "ex", "SPEC", "BRIEF", "LEDGER", "s" * 64, "b" * 64)
        self.assertIn("注記者は A です", out)
        self.assertNotIn("{{", out)
        with self.assertRaises(mrg.Stop):
            mrg.build_delegation(tpl + "{{EXTRA}}", "A", "ex", "S", "B", "L", "s", "b")

    def test_audit_detects_forbidden_reads_and_web(self):
        clean = json.dumps({"type": "assistant", "message": {"content": [{"type": "text", "text": "x"}]}})
        self.assertEqual(aud.audit(clean)["verdict"], "PASS_NO_TOOL_USE")
        read_ok = json.dumps({"message": {"content": [{"type": "tool_use", "name": "Read", "input": {"file_path": "C:/tmp/other.txt"}}]}})
        self.assertEqual(aud.audit(read_ok)["verdict"], "PASS_WITH_TOOL_USE_NOTE")
        bad = json.dumps({"message": {"content": [{"type": "tool_use", "name": "Read",
                                                   "input": {"file_path": "C:/x/briefs/meta/b2/selected_brief_factlock.md"}}]}})
        self.assertEqual(aud.audit(bad)["verdict"], "VIOLATION")
        grep = json.dumps({"message": {"content": [{"type": "tool_use", "name": "Grep", "input": {"pattern": "ANNOTATION_LOG", "path": "."}}]}})
        self.assertEqual(aud.audit(grep)["verdict"], "VIOLATION")
        web = json.dumps({"message": {"content": [{"type": "tool_use", "name": "WebSearch", "input": {"query": "q"}}]}})
        self.assertEqual(aud.audit(web)["verdict"], "VIOLATION")


if __name__ == "__main__":
    unittest.main()
