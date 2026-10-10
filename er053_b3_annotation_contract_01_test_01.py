# -*- coding: utf-8 -*-
"""er053_b3_annotation_contract_01 / er053_dev_b3_fixture_adapter_01 のtest(API呼び出し0、費用¥0)。
実行: .venv/Scripts/python.exe -m pytest er053_b3_annotation_contract_01_test_01.py -q
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
import unittest

import er053_b3_annotation_contract_01 as c
import er053_dev_b3_fixture_adapter_01 as ad

HERE = os.path.dirname(os.path.abspath(__file__))


def sha(b):
    return hashlib.sha256(b).hexdigest()


class Base(unittest.TestCase):
    slug = "hormuz"

    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="b3c_test_")
        ad.build_fixture(self.slug, self.d)
        self.sd = os.path.join(self.d, "storyline_b3")

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def p(self, name):
        return os.path.join(self.sd, name)

    def rj(self, name):
        return json.load(open(self.p(name), encoding="utf-8"))

    def wj(self, name, obj):
        json.dump(obj, open(self.p(name), "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    def reseal(self, annotated=True, sidecar=True, brief=True, ledger=True):
        """ファイルを書き換えた後、manifestのshaを現状に合わせる(特定のV検査だけを単独で失敗させるため)。"""
        mf = self.rj("annotation_manifest.json")
        if annotated:
            mf["annotated_md_sha256"] = sha(open(self.p("selected_brief_annotated.md"), "rb").read())
        if sidecar:
            mf["sidecar_sha256"] = sha(open(self.p("annotation.json"), "rb").read())
        if brief:
            mf["source_selected_brief_sha256"] = sha(open(self.p("selected_brief.md"), "rb").read())
        if ledger:
            mf["ledger_sha256"] = sha(open(os.path.join(self.d, "research_ledger", "verified_fact_ledger.txt"), "rb").read())
        self.wj("annotation_manifest.json", mf)

    def edit_annotated(self, fn):
        t = open(self.p("selected_brief_annotated.md"), "rb").read().decode("utf-8")
        t2 = fn(t)
        self.assertNotEqual(t, t2)
        open(self.p("selected_brief_annotated.md"), "wb").write(t2.encode("utf-8"))
        self.reseal()

    def violation(self):
        with self.assertRaises(c.AnnotatedB3ContractViolation) as cm:
            c.validate_annotated_b3(self.d)
        return cm.exception

    def checks(self, exc):
        return {v["check"] for v in exc.violations}


class PositiveTests(unittest.TestCase):
    def test_all_nine_trial_annotations_pass(self):
        for slug in ad.SLUGS:
            d = tempfile.mkdtemp(prefix="b3c_pos_")
            try:
                ad.build_fixture(slug, d)
                r = c.validate_annotated_b3(d)
                self.assertEqual(r.producer, "trial_fixture", slug)
                self.assertEqual(r.fact_numbers, list(range(1, len(r.fact_numbers) + 1)), slug)
                self.assertTrue(r.annotated_md_text.startswith("# Selected Fact Brief"), slug)
                self.assertEqual(r.annotated_md_sha256, sha(open(r.annotated_md_path, "rb").read()), slug)
            finally:
                shutil.rmtree(d, ignore_errors=True)

    def test_nine_fixture_set_matches_trial_final_dirs(self):
        have = sorted(os.listdir(os.path.join(ad.TRIAL_ROOT, "annotation", "final")))
        self.assertEqual(sorted(x for x in have if os.path.isdir(os.path.join(ad.TRIAL_ROOT, "annotation", "final", x))), sorted(ad.SLUGS))

    def test_original_unannotated_b3_fails_all_nine(self):
        """原B3(未注記)をannotatedとして渡すと必ずFAIL(sha整合を取っても構造検査V5で落ちる)。"""
        for slug in ad.SLUGS:
            d = tempfile.mkdtemp(prefix="b3c_orig_")
            try:
                ad.build_fixture(slug, d)
                sd = os.path.join(d, "storyline_b3")
                shutil.copyfile(os.path.join(sd, "selected_brief.md"), os.path.join(sd, "selected_brief_annotated.md"))
                mf = json.load(open(os.path.join(sd, "annotation_manifest.json"), encoding="utf-8"))
                mf["annotated_md_sha256"] = sha(open(os.path.join(sd, "selected_brief_annotated.md"), "rb").read())
                json.dump(mf, open(os.path.join(sd, "annotation_manifest.json"), "w", encoding="utf-8"))
                with self.assertRaises(c.AnnotatedB3ContractViolation) as cm:
                    c.validate_annotated_b3(d)
                self.assertIn("V5", {v["check"] for v in cm.exception.violations}, slug)
            finally:
                shutil.rmtree(d, ignore_errors=True)

    def test_one_char_change_in_fact_text_fails_v10_all_nine(self):
        for slug in ad.SLUGS:
            d = tempfile.mkdtemp(prefix="b3c_1ch_")
            try:
                ad.build_fixture(slug, d)
                sd = os.path.join(d, "storyline_b3")
                p = os.path.join(sd, "selected_brief_annotated.md")
                t = open(p, "rb").read().decode("utf-8")
                i = t.index("【事実1】") + len("【事実1】") + 3        # 事実1本文の途中の1文字を書き換える
                t2 = t[:i] + ("あ" if t[i] != "あ" else "い") + t[i + 1:]
                open(p, "wb").write(t2.encode("utf-8"))
                mf = json.load(open(os.path.join(sd, "annotation_manifest.json"), encoding="utf-8"))
                mf["annotated_md_sha256"] = sha(t2.encode("utf-8"))
                json.dump(mf, open(os.path.join(sd, "annotation_manifest.json"), "w", encoding="utf-8"))
                with self.assertRaises(c.AnnotatedB3ContractViolation) as cm:
                    c.validate_annotated_b3(d)
                checks = {v["check"] for v in cm.exception.violations}
                self.assertIn("V10", checks, slug)                  # sha整合済みでもV10で落ちる
                self.assertNotIn("V3", checks, slug)
            finally:
                shutil.rmtree(d, ignore_errors=True)


class NegativeTests(Base):
    def test_v1_missing_files(self):
        for name in ("selected_brief.md", "selected_brief_annotated.md", "annotation.json", "annotation_manifest.json"):
            d = tempfile.mkdtemp()
            try:
                ad.build_fixture(self.slug, d)
                os.remove(os.path.join(d, "storyline_b3", name))
                with self.assertRaises(c.AnnotatedB3ContractViolation) as cm:
                    c.validate_annotated_b3(d)
                self.assertEqual({v["check"] for v in cm.exception.violations}, {"V1"}, name)
            finally:
                shutil.rmtree(d, ignore_errors=True)

    def test_v1_missing_ledger(self):
        os.remove(os.path.join(self.d, "research_ledger", "verified_fact_ledger.txt"))
        self.assertEqual(self.checks(self.violation()), {"V1"})

    def test_v1_invalid_json_and_schema(self):
        open(self.p("annotation.json"), "w").write("{not json")
        self.assertEqual(self.checks(self.violation()), {"V1"})
        ad.build_fixture(self.slug, self.d)
        sc = self.rj("annotation.json")
        sc["annotator"] = "Z"
        self.wj("annotation.json", sc)
        self.reseal()
        self.assertEqual(self.checks(self.violation()), {"V1"})

    def test_v2_schema_version_and_keys(self):
        mf = self.rj("annotation_manifest.json")
        mf["schema_version"] = "v0"
        self.wj("annotation_manifest.json", mf)
        self.assertEqual(self.checks(self.violation()), {"V2"})
        mf = self.rj("annotation_manifest.json")
        mf["schema_version"] = c.MANIFEST_SCHEMA_VERSION
        del mf["producer"]
        self.wj("annotation_manifest.json", mf)
        self.assertEqual(self.checks(self.violation()), {"V2"})
        mf = self.rj("annotation_manifest.json")
        mf["producer"] = "x"
        del mf["checks"]["d_tags"]
        self.wj("annotation_manifest.json", mf)
        self.assertEqual(self.checks(self.violation()), {"V2"})

    def test_v3_stale_sha_each_file(self):
        for key in ("source_selected_brief_sha256", "ledger_sha256", "annotated_md_sha256", "sidecar_sha256"):
            ad.build_fixture(self.slug, self.d)
            mf = self.rj("annotation_manifest.json")
            mf[key] = "0" * 64
            self.wj("annotation_manifest.json", mf)
            exc = self.violation()
            self.assertIn("V3", self.checks(exc), key)

    def test_v3_stale_annotation_after_brief_regeneration(self):
        """selected_brief.md が再生成されて変わった(注記が古い)場合はsha不整合で止まる。"""
        with open(self.p("selected_brief.md"), "ab") as f:
            f.write(b"\n")
        self.assertIn("V3", self.checks(self.violation()))

    def test_v4_parse_fail(self):
        self.edit_annotated(lambda t: t.replace("## Selected Facts", "## Facts"))
        self.assertIn("V4", self.checks(self.violation()))

    def test_v5_variants(self):
        self.edit_annotated(lambda t: t.replace("【事実2】", "【事実 2-3】", 1))
        self.assertIn("V5", self.checks(self.violation()))
        ad.build_fixture(self.slug, self.d)
        self.edit_annotated(lambda t: t.replace("- 【事実2】", "- 【事実3】", 1))              # 番号が連続しない/重複
        self.assertIn("V5", self.checks(self.violation()))
        ad.build_fixture(self.slug, self.d)
        self.edit_annotated(lambda t: t + "\n余計な地の文の行です。\n")                        # 全行がFACT_LINE_REに一致しない
        self.assertIn("V5", self.checks(self.violation()))
        ad.build_fixture(self.slug, self.d)
        def mid_tag(t):
            head, tail = t.split("## Selected Facts", 1)
            return head + "## Selected Facts" + tail.replace("。", "。【事実9】", 1)
        self.edit_annotated(mid_tag)                                                         # 行中タグ
        self.assertIn("V5", self.checks(self.violation()))

    def test_v6_marks(self):
        self.edit_annotated(lambda t: t.replace("【中核数値】", "【中核数値 】", 1))             # 変形印
        self.assertIn("V6", self.checks(self.violation()))
        ad.build_fixture(self.slug, self.d)
        self.edit_annotated(lambda t: t.replace("【周辺数値】", "【中核数値】", 1))             # class不一致
        self.assertIn("V6", self.checks(self.violation()))
        ad.build_fixture(self.slug, self.d)
        sc = self.rj("annotation.json")
        sc["numbers"].append({"surface": "存在しない数字999", "kind": "x", "class": "core"})   # 印の無いnumbers
        self.wj("annotation.json", sc)
        self.reseal()
        self.assertIn("V6", self.checks(self.violation()))

    def test_v7_fact_set_and_ledger_ids(self):
        sc = self.rj("annotation.json")
        sc["facts"] = sc["facts"][:-1]
        self.wj("annotation.json", sc)
        self.reseal()
        self.assertIn("V7", self.checks(self.violation()))
        ad.build_fixture(self.slug, self.d)
        sc = self.rj("annotation.json")
        sc["facts"][0]["ledger_ids"] = ["NO-SUCH-ID"]
        self.wj("annotation.json", sc)
        self.reseal()
        self.assertIn("V7", self.checks(self.violation()))

    def test_v7_ledger_structure_incomplete(self):
        with open(os.path.join(self.d, "research_ledger", "verified_fact_ledger.txt"), "ab") as f:
            f.write(b"\n[broken header without id]\n")
        self.reseal()
        self.assertIn("V7", self.checks(self.violation()))

    def test_v8_checks(self):
        for bad in ("FAIL", None, "pass"):
            ad.build_fixture(self.slug, self.d)
            mf = self.rj("annotation_manifest.json")
            mf["checks"]["b_numbers"] = bad
            self.wj("annotation_manifest.json", mf)
            self.assertEqual(self.checks(self.violation()), {"V8"}, bad)
        ad.build_fixture(self.slug, self.d)
        mf = self.rj("annotation_manifest.json")
        mf["checks"]["b_numbers"] = "PASS_LAYOUT_NORMALIZED"
        self.wj("annotation_manifest.json", mf)
        c.validate_annotated_b3(self.d)        # 許容値

    def test_v9_spec_and_brief_sha(self):
        mf = self.rj("annotation_manifest.json")
        mf["spec_sha256"] = "1" * 64
        self.wj("annotation_manifest.json", mf)
        self.assertIn("V9", self.checks(self.violation()))
        ad.build_fixture(self.slug, self.d)
        sc = self.rj("annotation.json")
        sc["brief_sha256"] = "2" * 64
        self.wj("annotation.json", sc)
        self.reseal()
        self.assertIn("V9", self.checks(self.violation()))

    def test_v10_storyline_and_whitespace_tolerance(self):
        # Storyline差し替え
        self.edit_annotated(lambda t: t.replace("## Storyline\n", "## Storyline\nX", 1).replace("## Storyline\r\n", "## Storyline\r\nX", 1))
        self.assertIn("V10", self.checks(self.violation()))
        # 空白・改行・箇条記号だけの差はPASS
        ad.build_fixture(self.slug, self.d)
        self.edit_annotated(lambda t: t.replace("\n- 【事実2】", "\n\n・【事実2】 ", 1).replace("\r\n- 【事実2】", "\r\n\r\n・【事実2】 ", 1))
        c.validate_annotated_b3(self.d)

    def test_violation_json_saved_and_message_format(self):
        mf = self.rj("annotation_manifest.json")
        mf["checks"]["a_alignment"] = "FAIL"
        self.wj("annotation_manifest.json", mf)
        exc = self.violation()
        self.assertTrue(str(exc).startswith("[STOP] ANNOTATED_B3_CONTRACT_VIOLATION: V8"))
        j = json.load(open(self.p("audit/contract_violation.json"), encoding="utf-8"))
        self.assertEqual(j["violations"][0]["check"], "V8")

    def test_producer_recorded_not_branched(self):
        mf = self.rj("annotation_manifest.json")
        for prod in ("trial_fixture", "b3_annotation_automation_v1", "anything"):
            mf["producer"] = prod
            self.wj("annotation_manifest.json", mf)
            self.assertEqual(c.validate_annotated_b3(self.d).producer, prod)


class AdapterTests(unittest.TestCase):
    def test_adapter_outputs_files_and_producer(self):
        d = tempfile.mkdtemp()
        try:
            r = ad.build_fixture("meta", d)
            for f in ("selected_brief.md", "selected_brief_annotated.md", "annotation.json", "annotation_manifest.json", "fact_selection_evidence.json"):
                self.assertTrue(os.path.exists(os.path.join(d, "storyline_b3", f)), f)
            self.assertTrue(os.path.exists(os.path.join(d, "research_ledger", "verified_fact_ledger.txt")))
            self.assertEqual(r["manifest"]["producer"], "trial_fixture")
            src = ad.fixture_paths("meta")
            self.assertIn("shared", src["brief"].replace("\\", "/"))
            self.assertIn("runs/meta/shared", src["ledger"].replace("\\", "/"))
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_adapter_uses_shared_original_not_frozen_b3_dir(self):
        src = ad.fixture_paths("hormuz")
        self.assertTrue(src["brief"].replace("\\", "/").endswith("runs/hormuz/shared/brief_original.md"))
        self.assertTrue(src["evidence"].replace("\\", "/").endswith("runs/hormuz/shared/fact_selection_evidence_original.json"))

    def test_adapter_missing_input_raises(self):
        with self.assertRaises(FileNotFoundError):
            ad.build_fixture("meta", tempfile.mkdtemp(), trial_root=os.path.join(HERE, "nonexistent_root"))

    def test_adapter_constants_match_contract(self):
        self.assertEqual(ad.SCHEMA_VERSION, c.MANIFEST_SCHEMA_VERSION)

    def test_adapter_does_not_import_production_modules(self):
        import ast
        tree = ast.parse(open(os.path.join(HERE, "er053_dev_b3_fixture_adapter_01.py"), encoding="utf-8").read())
        mods = set()
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                mods |= {a.name for a in n.names}
            elif isinstance(n, ast.ImportFrom):
                mods.add(n.module)
        self.assertEqual(mods, {"__future__", "datetime", "hashlib", "json", "os"})


if __name__ == "__main__":
    unittest.main()
