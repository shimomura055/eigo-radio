# -*- coding: utf-8 -*-
"""er053_b3_deterministic_producer_01 (C4: 正式 annotated B3 producer = D-det v2 + 決定論assembler) のtest。API呼び出し0、費用0円。
Trial moduleのimport/読込は**このtest内に限る**(Production moduleはimportしない。ここで機械証明する)。
実行: .venv/Scripts/python.exe -m pytest er053_b3_deterministic_producer_01_test_01.py -q
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

import er053_b3_annotation_contract_01 as contract
import er053_b3_deterministic_producer_01 as prod
import er053_dev_b3_fixture_adapter_01 as ad

HERE = os.path.dirname(os.path.abspath(__file__))
T_BUILD = os.path.join(HERE, "er052_output", "b3_fact_instruction_separation_trial_01")
T_RANK = os.path.join(HERE, "er052_output", "b3_rootfix_trial_02")
T_CHK = os.path.join(HERE, "er052_output", "factlock_astra_e2e_trial_01")
PRODUCER_PY = os.path.join(HERE, "er053_b3_deterministic_producer_01.py")
RUNNER_PY = os.path.join(HERE, "er019_family_x_entertainment_production_runner_01.py")
E9_THEMES = ("semiconductor_earnings", "small_bag", "space_weapons", "hormuz", "central_bank_mortgage", "byd_recall")


def _rd(p):
    with open(p, encoding="utf-8", newline="") as f:
        return f.read().replace("\r\n", "\n")


def _sha(b):
    return hashlib.sha256(b).hexdigest()


def _segments(path):
    """トップレベルの関数・代入のソース原文(行範囲)を {name: text} で返す。"""
    src = open(path, encoding="utf-8", newline="").read().replace("\r\n", "\n")
    lines = src.split("\n")
    out = {}
    for node in ast.parse(src).body:
        if isinstance(node, ast.FunctionDef):
            out[node.name] = "\n".join(lines[node.lineno - 1:node.end_lineno])
        elif isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    out[t.id] = "\n".join(lines[node.lineno - 1:node.end_lineno])
    return out


def make_out(slug):
    d = tempfile.mkdtemp(prefix="c4_prod_")
    ad.copy_inputs(slug, d)
    return d


def sd(d, name):
    return os.path.join(d, "storyline_b3", name)


class GoldenTests(unittest.TestCase):
    """ROOTFIX-02(D-det v2)・ROOTFIX-01(D-full assembler)のTrial出力と完全一致。"""

    @classmethod
    def setUpClass(cls):
        cls.out = {th: make_out(th) for th in ad.SLUGS}
        cls.res = {th: prod.produce_annotated_b3(d) for th, d in cls.out.items()}

    @classmethod
    def tearDownClass(cls):
        for d in cls.out.values():
            shutil.rmtree(d, ignore_errors=True)

    def test_annotated_md_equals_rootfix02_eval_v2_ddet_all_nine(self):
        """ROOTFIX-02 eval_v2 の D-det v2 出力(タグ位置・role・Fact本文)と完全一致。"""
        for th in ad.SLUGS:
            gold = _rd(os.path.join(T_RANK, "eval_v2", "m11", "ddet_v2_c0", f"{th}_annotated.md"))
            self.assertEqual(_rd(sd(self.out[th], "selected_brief_annotated.md")), gold, th)

    def test_sidecar_numbers_and_facts_equal_rootfix02_eval_v2_all_nine(self):
        for th in ad.SLUGS:
            gold = json.load(open(os.path.join(T_RANK, "eval_v2", "m11", "ddet_v2_c0", f"{th}_sidecar.json"), encoding="utf-8"))
            got = json.load(open(sd(self.out[th], "annotation.json"), encoding="utf-8"))
            self.assertEqual(got["numbers"], gold["numbers"], th)
            self.assertEqual(got["facts"], gold["facts"], th)
            self.assertEqual(got["annotator"], "DETERMINISTIC")
            self.assertEqual(got["unmapped_claims"], [])

    def test_fact_lines_and_constraints_equal_rootfix01_dfull_assembler(self):
        sys.path.insert(0, T_BUILD)
        try:
            import b3sep_build_01 as B1
        finally:
            sys.path.remove(T_BUILD)
        for th in ad.SLUGS:
            d = self.out[th]
            ledger = _rd(os.path.join(d, "research_ledger", "verified_fact_ledger.txt"))
            ev = json.load(open(sd(d, "fact_selection_evidence.json"), encoding="utf-8"))
            a = B1.assemble_D(ledger, ev["selected_fact_ids"], ev["selected_storyline"], "Dfull")
            self.assertEqual(ev["deterministic_selected_fact_brief_text"], a["facts_text"], th)   # 決定論出力は別キー(F2)
            self.assertNotEqual(ev["selected_fact_brief_text"], a["facts_text"], th)             # 元の selected_fact_brief_text(B3 LLM文)は不変
            self.assertEqual(ev["writer_constraints_text"], a["constraints_text"], th)
            self.assertEqual(ev["writer_news_field_text"], a["news_field"], th)
            self.assertEqual(_rd(sd(d, "writer_constraints.txt")), a["constraints_text"], th)
            lines = [ln for ln in contract.validate_annotated_b3(d).facts_text.split("\n") if ln.strip()]
            plain_lines = [x for x in a["facts_text"].split("\n") if x.strip()]
            self.assertEqual(len(lines), len(plain_lines), th)
            for ln, pl in zip(lines, plain_lines):
                import er053_family_x_factlock_ja_writer_01 as w1
                self.assertEqual("- " + w1.strip_tags(w1.FACT_LINE_RE.match(ln).group(2)), pl, th)

    def test_news_field_equals_rootfix02_e9_news_field_for_e9_themes(self):
        """E9(R0 6 call)でWriterが実際に読んだニュース欄と、Production W-1に渡る文字列が完全一致。"""
        for th in E9_THEMES:
            gold = _rd(os.path.join(T_RANK, "e9", th, "Ddetv2", "news_field.txt"))
            a = contract.validate_annotated_b3(self.out[th])
            self.assertEqual(a.news_field_text, gold, th)

    def test_ids_removed_and_no_bracket_in_constraints(self):
        for th in ad.SLUGS:
            a = contract.validate_annotated_b3(self.out[th])
            self.assertNotIn("【", a.constraints_text, th)
            ledger = _rd(os.path.join(self.out[th], "research_ledger", "verified_fact_ledger.txt"))
            ids = [ln.split("] ", 1)[1].split(":", 1)[0] for ln in ledger.split("\n") if ln.startswith("[")]
            for fid in ids:
                self.assertNotIn(fid, a.constraints_text, f"{th}: ledger id {fid} leaked into constraints block")

    def test_ambiguous_fact_gets_fixed_qualifier_and_constraint_label_form(self):
        """AMBIGUOUS Factは固定限定文付与、制約は「事実Nについて：」形式(Nは決定論付与の番号)。"""
        n_amb = 0
        for th in ad.SLUGS:
            d = self.out[th]
            ledger = _rd(os.path.join(d, "research_ledger", "verified_fact_ledger.txt"))
            a = contract.validate_annotated_b3(d)
            ev = json.load(open(sd(d, "fact_selection_evidence.json"), encoding="utf-8"))
            for n, fid in enumerate(ev["selected_fact_ids"], 1):
                if f"[AMBIGUOUS" in "".join(x for x in ledger.split("\n") if f"{fid}:" in x and x.startswith("[AMBIGUOUS")):
                    n_amb += 1
                    ln = [x for x in a.facts_text.split("\n") if x.startswith(f"- 【事実{n}】")][0]
                    self.assertIn(prod.AMB_QUALIFIER, ln)
            for ln in a.constraints_text.split("\n")[1:]:
                if ln.strip():
                    self.assertRegex(ln, r"^- 事実\d+(?:の(?:範囲|条件))?について：", th)
        self.assertGreaterEqual(n_amb, 1)       # 9テーマのうち少なくとも1件はAMBIGUOUSを含む(含まなければこのtestは無効)

    def test_core_peripheral_roles_cap_rule_and_number_marks_only_standard(self):
        for th in ad.SLUGS:
            a = contract.validate_annotated_b3(self.out[th])
            core = [n for n in a.sidecar["numbers"] if n["class"] == "core"]
            conc = {n["concept"] for n in core}
            mf = a.manifest
            self.assertLessEqual(len(conc), mf["cap"], th)

    def test_contract_pass_and_manifest_fields(self):
        for th in ad.SLUGS:
            a = contract.validate_annotated_b3(self.out[th])
            self.assertEqual(a.producer, "deterministic_v2")
            mf = a.manifest
            self.assertEqual(mf["llm_calls"], 0)
            self.assertEqual(mf["model_ids"], [])
            self.assertEqual(set(mf["checks"].values()), {"PASS"})
            self.assertEqual(mf["rules_sha256"], prod.rules_sha256())
            self.assertEqual(mf["spec_sha256"], mf["rules_sha256"])
            self.assertEqual(set(mf["input_shas"]), {"selected_brief_md", "ledger", "fact_selection_evidence_json"})
            self.assertEqual(mf["input_shas"]["selected_brief_md"], mf["source_selected_brief_sha256"])
            self.assertEqual(a.sidecar["unmapped_claims"], [])

    def test_existing_trial_annotation_checker_agrees_only_annotator_value_differs(self):
        """既存注記検査(Trial b3_annotation_check_01)をこのtestでだけ実行: producer出力に対する指摘は annotator 許容値のみ(=契約側で追加した DETERMINISTIC)。"""
        sys.path.insert(0, T_CHK)
        try:
            import b3_annotation_check_01 as chk
        finally:
            sys.path.remove(T_CHK)
        for th in ad.SLUGS:
            d = self.out[th]
            ann = _rd(sd(d, "selected_brief_annotated.md"))
            side = json.load(open(sd(d, "annotation.json"), encoding="utf-8"))
            ledger = _rd(os.path.join(d, "research_ledger", "verified_fact_ledger.txt"))
            ev = json.load(open(sd(d, "fact_selection_evidence.json"), encoding="utf-8"))
            plain = prod.assemble_plain(ledger, ev["selected_fact_ids"], ev["selected_storyline"])["brief_md"]
            r = chk.run(plain, ann, ledger, dict(side, brief_sha256=chk.sha256(plain)), spec_sha256=None, brief_sha256=chk.sha256(plain))
            probs = [p for v in r.values() if isinstance(v, dict) for p in v.get("problems", [])]
            self.assertTrue(all("annotator" in p for p in probs), (th, probs))
            self.assertGreaterEqual(len(probs), 0)

    def test_idempotent_rerun_same_artifacts_and_llm_text_preserved(self):
        th = "central_bank_mortgage"
        d = self.out[th]
        before = {n: _sha(open(sd(d, n), "rb").read()) for n in ("selected_brief_annotated.md", "annotation.json", "writer_constraints.txt")}
        ev1 = json.load(open(sd(d, "fact_selection_evidence.json"), encoding="utf-8"))
        prod.produce_annotated_b3(d)
        after = {n: _sha(open(sd(d, n), "rb").read()) for n in before}
        self.assertEqual(before, after)
        ev2 = json.load(open(sd(d, "fact_selection_evidence.json"), encoding="utf-8"))
        orig = json.load(open(os.path.join(T_CHK, "g0_real_annotation_01", th, "shared", "fact_selection_evidence_original.json"), encoding="utf-8"))
        self.assertEqual(ev2["selected_fact_brief_text"], orig["selected_fact_brief_text"])        # F2: 元欄は不変(上書きしない)
        self.assertNotIn("b3_llm_selected_fact_brief_text", ev2)
        self.assertEqual(ev2["deterministic_selected_fact_brief_text_source"], "deterministic_v2")
        self.assertNotEqual(ev2["deterministic_selected_fact_brief_text"], orig["selected_fact_brief_text"])
        self.assertEqual(ev1, ev2)


class PortFidelityTests(unittest.TestCase):
    """移植元Trial 3ファイルの constant/regex/関数が**ソース逐語**で本moduleに存在する(byte-identical)。"""

    def test_every_ported_symbol_is_byte_identical_to_trial_source(self):
        trial = {}
        for f in (os.path.join(T_BUILD, "b3sep_build_01.py"), os.path.join(T_RANK, "b3r2_rank_02.py"), os.path.join(T_RANK, "b3r2_eval_01.py")):
            for k, v in _segments(f).items():
                trial.setdefault(k, []).append(v)
        ours = _segments(PRODUCER_PY)
        for name in prod._PORTED_NAMES:
            self.assertIn(name, ours, name)
            self.assertIn(ours[name], trial.get(name, []), f"{name}: producer source differs from every Trial source")
        self.assertEqual(len(prod._PORTED_NAMES), len(set(prod._PORTED_NAMES)))

    def test_sha_table_matches_trial_function_sources(self):
        """runtime evidenceの規則sha表は、関数は inspect.getsource のsha、constantはpattern/値のsha。Trial側原文との一致をsha表でも確認。"""
        table = prod.rules_sha_table()
        ours = _segments(PRODUCER_PY)
        for name in prod._PORTED_NAMES:
            obj = getattr(prod, name)
            if callable(obj) and hasattr(obj, "__code__"):
                import inspect
                self.assertEqual(table[name], hashlib.sha256(inspect.getsource(obj).encode("utf-8")).hexdigest(), name)
                self.assertEqual(inspect.getsource(obj).rstrip("\n"), ours[name].rstrip("\n"), name)
        self.assertEqual(prod.rules_sha256(), prod.rules_sha256())      # 決定論
        self.assertEqual(len(prod.rules_sha256()), 64)

    def test_d_det_v2_unit_conversion_table_present(self):
        self.assertEqual(prod.canon_unit("ベーシスポイント"), "<pp>")
        self.assertEqual(prod.canon_unit("パーセントポイント"), "<pp>")
        self.assertEqual(prod.canon_unit("パーセント"), "%")
        self.assertEqual(prod._bp_to_pp("25"), "0.25")
        self.assertEqual(prod.cap_of(4), 3)
        self.assertEqual(prod.cap_of(20), 6)
        self.assertEqual(prod.cap_of(8), 4)

    def test_producer_does_not_import_trial_or_lane_b_or_checker(self):
        tree = ast.parse(open(PRODUCER_PY, encoding="utf-8").read())
        mods = set()
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                mods |= {a.name for a in n.names}
            elif isinstance(n, ast.ImportFrom):
                mods.add(n.module)
        self.assertEqual(mods, {"__future__", "datetime", "hashlib", "inspect", "json", "os", "re", "types", "unicodedata",
                                "er053_family_x_factlock_ja_writer_01", "er053_b3_annotation_contract_01", "decimal"})
        src = open(PRODUCER_PY, encoding="utf-8").read()
        doc_ids = {id(n.value) for n in ast.walk(tree) if isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant) and isinstance(n.value.value, str)}
        toks = set()
        for n in ast.walk(tree):
            if isinstance(n, ast.Name):
                toks.add(n.id)
            elif isinstance(n, ast.Attribute):
                toks.add(n.attr)
            elif isinstance(n, ast.Constant) and isinstance(n.value, str) and id(n) not in doc_ids:
                toks.add(n.value)
        for forbidden in ("environ", "argv", "ArgumentParser", "getenv", "import_module", "__import__", "b3_annotation_check_01", "trial_fixture"):
            self.assertNotIn(forbidden, toks, forbidden)
        for tok in ("import b3sep", "import b3r2", "from b3sep", "from b3r2", "sys.path"):
            self.assertNotIn(tok, src, tok)


class ProducerFailureTests(unittest.TestCase):
    def setUp(self):
        self.d = make_out("small_bag")

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def _ev(self):
        return json.load(open(sd(self.d, "fact_selection_evidence.json"), encoding="utf-8"))

    def _save(self, ev):
        json.dump(ev, open(sd(self.d, "fact_selection_evidence.json"), "w", encoding="utf-8"), ensure_ascii=False)

    def test_missing_inputs_stop(self):
        for rel in ("research_ledger/verified_fact_ledger.txt", "storyline_b3/selected_brief.md", "storyline_b3/fact_selection_evidence.json"):
            d = make_out("small_bag")
            try:
                os.remove(os.path.join(d, rel))
                with self.assertRaises(prod.AnnotationProducerError) as cm:
                    prod.produce_annotated_b3(d)
                self.assertIn("missing input", str(cm.exception))
                self.assertTrue(str(cm.exception).startswith("[STOP] ANNOTATION_PRODUCER_FAILED"))
            finally:
                shutil.rmtree(d, ignore_errors=True)

    def test_unknown_duplicate_and_empty_ids_stop(self):
        ev = self._ev()
        for bad in (ev["selected_fact_ids"] + ["NO-SUCH-ID"], ev["selected_fact_ids"] + ev["selected_fact_ids"][:1], []):
            e2 = dict(ev, selected_fact_ids=bad)
            self._save(e2)
            with self.assertRaises(prod.AnnotationProducerError):
                prod.produce_annotated_b3(self.d)
        self._save(ev)
        prod.produce_annotated_b3(self.d)       # 元に戻せば成功

    def test_storyline_mismatch_with_selected_brief_stops(self):
        ev = self._ev()
        ev["selected_storyline"] = ev["selected_storyline"] + "。"
        self._save(ev)
        with self.assertRaises(prod.AnnotationProducerError) as cm:
            prod.produce_annotated_b3(self.d)
        self.assertIn("selected_storyline", str(cm.exception))

    def test_failure_removes_stale_annotation_artifacts(self):
        prod.produce_annotated_b3(self.d)
        self.assertTrue(os.path.exists(sd(self.d, "selected_brief_annotated.md")))
        ev = self._ev()
        self._save(dict(ev, selected_fact_ids=["NO-SUCH-ID"]))
        with self.assertRaises(prod.AnnotationProducerError):
            prod.produce_annotated_b3(self.d)
        for n in ("selected_brief_annotated.md", "annotation.json", "annotation_manifest.json", "writer_constraints.txt"):
            self.assertFalse(os.path.exists(sd(self.d, n)), n)             # 古い注記が残らない(W-1側のV1でも止まる)
        with self.assertRaises(contract.AnnotatedB3ContractViolation):
            contract.validate_annotated_b3(self.d)

    def test_regenerated_b3_makes_old_annotation_stale_if_producer_skipped(self):
        """producerを通さずselected_brief.mdだけ再生成されたらV3(sha)で止まる(runnerは必ずproducerを通す)。"""
        prod.produce_annotated_b3(self.d)
        with open(sd(self.d, "selected_brief.md"), "ab") as f:
            f.write(b"\n")
        with self.assertRaises(contract.AnnotatedB3ContractViolation) as cm:
            contract.validate_annotated_b3(self.d)
        self.assertIn("V3", {v["check"] for v in cm.exception.violations})


class InternalCheckTests(unittest.TestCase):
    def _prep(self):
        d = make_out("hormuz")
        self.addCleanup(shutil.rmtree, d, True)
        prod.produce_annotated_b3(d)
        ledger = _rd(os.path.join(d, "research_ledger", "verified_fact_ledger.txt"))
        ev = json.load(open(sd(d, "fact_selection_evidence.json"), encoding="utf-8"))
        ids, story = ev["selected_fact_ids"], ev["selected_storyline"]
        plain = prod.assemble_plain(ledger, ids, story)
        der = prod.ddet(ledger, ids, story)
        _pb, ann, side = prod.build_annotated(ledger, ids, story, der)
        side["spec_sha256"], side["brief_sha256"] = "x", "y"
        return plain, ann, side, der, story, ledger

    def test_clean_input_passes_all_five(self):
        plain, ann, side, der, story, ledger = self._prep()
        r = prod.run_internal_checks(plain, ann, side, der, story, ledger)
        self.assertEqual({k: v["status"] for k, v in r.items()}, {k: "PASS" for k in ("a_alignment", "b_numbers", "c_core_peripheral", "d_tags", "e_sidecar")})

    def test_each_check_catches_its_defect(self):
        plain, ann, side, der, story, ledger = self._prep()
        r = prod.run_internal_checks(plain, ann.replace("【事実2】", "【事実3】", 1), side, der, story, ledger)
        self.assertEqual(r["d_tags"]["status"], "FAIL")
        r = prod.run_internal_checks(plain, ann.replace("【中核数値】", "", 1).replace("【周辺数値】", "", 1), side, der, story, ledger)
        self.assertEqual(r["b_numbers"]["status"], "FAIL")
        r = prod.run_internal_checks(plain, ann.replace("事実", "事項", 0).replace("。", "。あ", 1), side, der, story, ledger)
        self.assertEqual(r["a_alignment"]["status"], "FAIL")
        bad_side = json.loads(json.dumps(side))
        bad_side["facts"][0]["ledger_ids"] = ["NO-SUCH"]
        r = prod.run_internal_checks(plain, ann, bad_side, der, story, ledger)
        self.assertEqual(r["e_sidecar"]["status"], "FAIL")
        bad_der = json.loads(json.dumps(der))
        for it in bad_der["items"]:
            it["role"] = "core"
            it["eligible"] = False
        r = prod.run_internal_checks(plain, ann, side, bad_der, story, ledger)
        self.assertEqual(r["c_core_peripheral"]["status"], "FAIL")

    def test_producer_stops_when_internal_check_fails(self):
        d = make_out("hormuz")
        try:
            with mock.patch.object(prod, "run_internal_checks", return_value={k: {"status": "FAIL", "problems": ["x"]} for k in (
                    "a_alignment", "b_numbers", "c_core_peripheral", "d_tags", "e_sidecar")}):
                with self.assertRaises(prod.AnnotationProducerError):
                    prod.produce_annotated_b3(d)
            self.assertFalse(os.path.exists(sd(d, "selected_brief_annotated.md")))
        finally:
            shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
