# ============================================================
# er064_kp_int_01_test_01.py  (Round1 test: Production無変更・Coffee語句不在・6指標順序行逐語・sha整合・M/Pの不変条件)
# 使い方: PYTHONPATH=. .venv/Scripts/python.exe er064_kp_int_01_test_01.py
# ============================================================
import ast
import hashlib
import json
import os
import re
import subprocess
import sys
import unittest

sys.path.insert(0, os.getcwd())
import er030_key_phrase_db_hybrid_source_reference_contract_01 as contract  # noqa: E402
import er064_kp_int_01_machine as MC  # noqa: E402
import er064_kp_int_01_prompts as PR  # noqa: E402
import er064_kp_int_01_run as RUN  # noqa: E402
import er064_kp_opt_01_prompt_build as B1  # noqa: E402
import er064_kp_opt_01_phase2_run_03 as R  # noqa: E402
import er064_kp_opt_01_upstream_core as U  # noqa: E402

O = MC.OUT
BAN_PROMPT = ["pump", "fist", "wallet", "time lag", "behind", "price increase", "roast", "bean", "coffee", "barista", "latte", "show up", "come down",
              "hold on", "right away", "take time", "regular basis", "push prices", "calendar", "mark the date"]
BAN_CODE_STR = ["pump", "fist", "wallet", "time lag", "behind", "roast", "raw bean", "barista", "latte", "price increase", "push prices"]
CODE_FILES = ["er064_kp_int_01_machine.py", "er064_kp_int_01_prompts.py", "er064_kp_int_01_run.py", "er064_kp_int_01_screen.py"]


def sha_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def string_constants(path):
    tree = ast.parse(open(path, encoding="utf-8").read())
    doc_ids = set()
    for n in ast.walk(tree):
        if isinstance(n, (ast.Module, ast.FunctionDef, ast.ClassDef)) and n.body and isinstance(n.body[0], ast.Expr) and isinstance(getattr(n.body[0], "value", None), ast.Constant):
            doc_ids.add(id(n.body[0].value))
    return [n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str) and id(n) not in doc_ids]


class ProductionUnchanged(unittest.TestCase):
    def test_no_tracked_py_or_template_modified(self):
        out = subprocess.run(["git", "diff", "--name-only"], capture_output=True, text=True, encoding="utf-8").stdout.split()
        bad = [f for f in out if f.endswith(".py") or f.endswith(".txt") and "template" in f]
        self.assertEqual(bad, [], f"tracked .py/template modified: {bad}")

    def test_p0_is_production_verbatim(self):
        self.assertEqual(PR.head("P0", "std"), B1.before_static())
        self.assertEqual(PR.tail("P0"), contract._FAMILY_X_SOURCE_REFERENCE_SELECTION_GUIDANCE)

    def test_schema_is_production(self):
        # runnerはProductionのselector factory/schemaをそのまま使う(Trial独自schemaなし)
        src = open("er064_kp_opt_01_phase2_run_03.py", encoding="utf-8").read()
        self.assertIn("make_instrumented_selector_factory", src)
        self.assertIn("run_source_reference_contract_gate", src)
        self.assertEqual(B1.schema_json(False), contract.build_json_schema(["C1", "C2"]))

    def test_state_guard_if_present(self):
        p = f"{O}/state_guard_r1.json"
        if not os.path.exists(p):
            self.skipTest("state_guard_r1.json未作成")
        g = json.load(open(p, encoding="utf-8"))
        for k, v in g.items():
            if k.startswith("unchanged_"):
                self.assertTrue(v, k)


class PromptRules(unittest.TestCase):
    def test_line_a_verbatim(self):
        for pid in ("P0", "P1", "P2", "P3", "P4"):
            for lv in ("std", "adv"):
                self.assertIn(PR.LINE_A, PR.head(pid, lv), f"{pid} {lv}")
        self.assertEqual(PR.LINE_A, "優先順位は、初回音声での処理困難、未知の可能性、瞬時の推測困難、本文の事実・感情・面白さへの影響、記事内重要度、汎用性の順です。")

    def test_no_coffee_words_in_prompts(self):
        for pid in ("P1", "P2", "P3", "P4"):
            for lv in ("std", "adv"):
                t = (PR.head(pid, lv) + PR.tail(pid)).lower()
                for w in BAN_PROMPT:
                    self.assertNotIn(w, t, f"{pid} {lv}: {w}")

    def test_no_coffee_words_in_code_strings(self):
        for f in CODE_FILES:
            for s in string_constants(f):
                for w in BAN_CODE_STR:
                    self.assertNotIn(w, s.lower(), f"{f}: '{w}' in string")

    def test_anchors_only_in_eval(self):
        for f in ("er064_kp_int_01_machine.py", "er064_kp_int_01_prompts.py", "er064_kp_int_01_run.py"):
            self.assertNotIn("anchors_r1", open(f, encoding="utf-8").read(), f)
            self.assertNotIn("er064_kp_int_01_eval", open(f, encoding="utf-8").read(), f)

    # TEST-HYGIENE-02(2026-10-22): tiktokenは本体.venv非導入(隔離環境のTIKTOKEN_PATH運用)。未導入環境ではskip。
    @unittest.skipUnless(os.environ.get("TIKTOKEN_PATH") or __import__("importlib.util").util.find_spec("tiktoken"),
                         "tiktoken未導入(隔離環境のみ。TIKTOKEN_PATHを指定すれば実行)")
    def test_tokens_not_above_current(self):
        base = PR.tokens(PR.head("P0", "std")) + PR.tokens(PR.tail("P0"))
        for pid in ("P1", "P2", "P3", "P4"):
            for lv in ("std", "adv"):
                self.assertLessEqual(PR.tokens(PR.head(pid, lv)) + PR.tokens(PR.tail(pid)), base, f"{pid} {lv}")

    def test_required_contract_terms(self):
        for pid in ("P1", "P2", "P3", "P4"):
            h = PR.head(pid, "std") + PR.tail(pid)
            for term in ("ちょうど5個", 'key_phrase_role="topic"', 'key_phrase_role="important"', "1〜5語", "source_candidate_id", "surface_echo", "backup_item", "【日本語グロス】"):
                self.assertIn(term, h, f"{pid}: {term}")

    def test_annotation_labels_match_rows(self):
        for lab in (U.LABEL_CONTAINS, U.LABEL_CONTAINED, U.LABEL_FRAGMENT, MC.LABEL_MATCH):
            self.assertIn(lab, PR.ANNOT)
        self.assertEqual(PR.LABEL_MATCH, MC.LABEL_MATCH)

    def test_prompts_json_sha(self):
        pj = json.load(open(f"{O}/prompts_r1.json", encoding="utf-8"))
        for pid, e in pj["prompts"].items():
            for lv in ("std", "adv"):
                self.assertEqual(e[lv]["head_sha256"], PR.sha(PR.head(pid, lv)), f"{pid} {lv} head")
                self.assertEqual(e[lv]["tail_sha256"], PR.sha(PR.tail(pid)), f"{pid} {lv} tail")


class MachinePatterns(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sl = json.load(open(f"{O}/shortlists_r1.json", encoding="utf-8"))

    def test_sha_file(self):
        body = open(f"{O}/shortlists_r1.json", "rb").read()
        stated = open(f"{O}/shortlists_r1.sha256.txt", encoding="utf-8").read().split()[0]
        self.assertEqual(hashlib.sha256(body).hexdigest(), stated)

    def test_m0_m1_match_fixed02(self):
        fx = json.load(open("er064_output/kp_extraction_selection_opt_01/phase1_fix/shortlists_fixed_02.json", encoding="utf-8"))["articles"]
        for key in ("coffee_std", "coffee_adv", "meta_std", "meta_adv", "hormuz_std", "hormuz_adv"):
            self.assertEqual(self.sl["articles"][key]["M0"]["rows_text"], fx[key]["current"]["rows_text"], f"M0 {key}")
            self.assertEqual(self.sl["articles"][key]["M1"]["rows_text"], fx[key]["alt_precision_guarded"]["rows_text"], f"M1 {key}")

    def test_m2_superset_of_m1_and_reserved_cap(self):
        for key, ent in self.sl["articles"].items():
            m1 = {c["canonical_form"] for c in ent["M1"]["candidates"]}
            m2 = {c["canonical_form"] for c in ent["M2"]["candidates"]}
            self.assertLessEqual(len(ent["M2"]["reserved"]), MC.RESERVED_CAP, key)
            self.assertEqual(m1 - m2, set(ent["M2"]["tier_h_dropped"]), key)  # M1にあってM2に無いのはTier-Hで整理された語のみ
            self.assertTrue(set(ent["M2"]["reserved"]) <= m2, key)
            if not ent["M2"]["reserved"]:
                self.assertEqual(ent["M2"]["rows_text"], ent["M1"]["rows_text"], key)

    def test_m3_only_adds_match_label(self):
        for key, ent in self.sl["articles"].items():
            stripped = re.sub(r" \| match: \w+", "", ent["M3"]["rows_text"])
            self.assertEqual(stripped, ent["M2"]["rows_text"], key)
            self.assertNotIn("match:", ent["M2"]["rows_text"].split("【選定方針】")[0], key)

    def test_take_time_type_not_deleted(self):
        # 低優先になりうる定着表現を機械側で削除していない(M0->M2で消えるのは明示ルールの除外のみ)
        for key in ("coffee_std", "coffee_adv"):
            ent = self.sl["articles"][key]
            for pat in ("M1", "M2", "M3"):
                canon = {c["canonical_form"] for c in ent[pat]["candidates"]}
                for must in ("take time", "right away", "on a regular basis"):
                    self.assertIn(must, canon, f"{key} {pat} {must}")

    def test_reserved_evidence_kinds(self):
        for key, ent in self.sl["articles"].items():
            res = set(ent["M2"]["reserved"])
            for c in ent["M2"]["candidates"]:
                if c["canonical_form"] in res:
                    self.assertTrue(c["evidence"].startswith(("placeholder_title", "rule_poss_pattern")), c)


class RunnerRules(unittest.TestCase):
    def test_constants(self):
        # TEST-HYGIENE-02(2026-10-22): er064_kp_int_02_run/03_runはimport時にRUN.HARD_STOPを書き換える(R2/R3の上限)。
        # 同一process(全回帰)ではそれらがdiscoveryで先にimportされるため、共有module属性は95.0でない。
        # Round1定数としての95.0は、別名で独立にloadしたRound1 moduleで検証する(共有状態に依存しない)。
        import importlib.util as _ilu
        _spec = _ilu.spec_from_file_location("er064_kp_int_01_run_isolated_hygiene02", os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "er064_kp_int_01_run.py"))
        _iso = _ilu.module_from_spec(_spec)
        _spec.loader.exec_module(_iso)
        self.assertEqual(_iso.HARD_STOP, 95.0)
        self.assertEqual(RUN.N["coffee"], 3)
        self.assertEqual(RUN.N["other"], 2)
        self.assertEqual(RUN.S.MODEL, "gpt-6-luna")

    def test_m0p0_fidelity_to_production(self):
        ctx = RUN.build_ctx("coffee", ["M0P0", "M1P0"])
        fid = RUN.fidelity(ctx)
        self.assertTrue(fid and all(fid.values()), fid)

    def test_no_retry_or_loop_wrapper(self):
        src = open("er064_kp_int_01_run.py", encoding="utf-8").read()
        self.assertNotIn("subprocess", src)
        self.assertNotIn("while True", src)

    def test_cost_file_consistency_if_present(self):
        p = f"{O}/cost_r1.json"
        if not os.path.exists(p):
            self.skipTest("cost_r1.json未作成")
        c = json.load(open(p, encoding="utf-8"))
        self.assertAlmostEqual(c["cumulative_jpy"], round(sum(x["cost_jpy"] for x in c["calls"]), 4), places=3)
        self.assertTrue(all(x["model"] == "gpt-6-luna" for x in c["calls"]))
        self.assertLess(c["cumulative_jpy"], 100.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
