# -*- coding: utf-8 -*-
"""NUANCE-CORNER-ABOLITION-01 委任_02: ニュアンス解説コーナー廃止(2026-10-30ユーザー決定)の廃止ガードtest。全てmock・API 0。

(a) Dangling: Production(*.py/*.js/*.html)に旧生成・旧配線の識別子が残っていない(逆流防止)
(b) 旧run由来のnuance_spec.json/nuance_result.json(ADOPTED)があっても、ページ合成・期待ブロック数・検証の結果が変わらない(読まない)
(c) ページに『ニュアンス解説』ブロックがあれば構造判定でSTOP(NUANCE_CORNER_ABOLISHED)。文字列の部分一致ではなく`<h3>`見出しの構造一致
(d) 旧フォーム形式(schema_minor=2 / selection.nuance / 旧AIF2コード / 旧データ形式)は明示拒否
(e) M6 resume/逆流: 旧`rec["nuance"]`付き確定recordのload/G1/revise/rebind、`--regenerate-stage nuance_cand_*`の明示エラー
実行: .venv/Scripts/python.exe -m unittest er136_nuance_abolition_test_01
"""
from __future__ import annotations

import test_state_isolation_01  # noqa: F401

import glob
import json
import os
import re
import shutil
import subprocess
import unittest

import er120_part2_grammar_production_01 as g
import er120_part2_wiring_01 as p2w
import er128_form_readable_restore_01 as R
import er128_kp_confirmed_content_01 as cc
import er119_kp_human_review_01 as rv
from er119_test_support_01 import Env, jd, jl
from er128_kp_confirmed_content_grammar_v2_test_01 import GBase, PARAS, LABEL

ROOT = os.path.dirname(os.path.abspath(__file__))
FORM_DIR = os.path.join(ROOT, "user_test", "selection_form_v3")
BLOCK = "<section class='study'><h3>ニュアンス解説</h3><div class='study-item'><h4>at least</h4><dl><dt>ポイント</dt><dd>x</dd></dl></div></section>"
DANGLING = re.compile(r"er134_nuance|finalize_nuance|nuance_for_display|form_nuance_bundle|run_nuance_candidates|n1_stage\(|nuance_candidate\.json|nuance_spec\.json|"
                      r"nuance_result\.json|NUANCE_RESULT_FILENAME|NUANCE_ADOPTED|render_nuance_html_block|expected_nuance_blocks|nuance_is_adopted|"
                      r"cmd_nuance|_write_nuance_sidecar|_validate_form_nuance|nuance-select|nuance-issue-spec")


def _production_files():
    out = [p for p in glob.glob(os.path.join(ROOT, "er*.py")) if "test" not in os.path.basename(p)]
    out += glob.glob(os.path.join(ROOT, "enduser_page_assets", "*.py"))
    out += [os.path.join(FORM_DIR, "index.html"), os.path.join(FORM_DIR, "form_logic.js"),
            os.path.join(ROOT, "docs", "research", "KP-GATE-DROP-BACKFILL-PRODUCTION-01", "tools", "export_form_data_01.py")]
    return sorted(out)


class T1_Dangling(unittest.TestCase):
    def test_production_sources_have_no_old_nuance_generation_or_wiring_identifiers(self):
        offenders = []
        for p in _production_files():
            with open(p, encoding="utf-8") as f:
                for n, line in enumerate(f, 1):
                    if DANGLING.search(line):
                        offenders.append(f"{os.path.relpath(p, ROOT)}:{n}")
        self.assertEqual(offenders, [])

    def test_runners_and_shared_builder_do_not_import_a_nuance_module(self):
        for name in ("er019_family_x_audio_production_runner_01.py", "er121_family_y_runner_01.py", "er026_family_z_fiction_production_runner_01.py",
                     "er120_part2_wiring_01.py", "er120_part2_grammar_production_01.py", "er128_kp_confirmed_content_01.py", "er119_kp_wiring_01.py"):
            with open(os.path.join(ROOT, name), encoding="utf-8") as f:
                src = f.read()
            self.assertIsNone(re.search(r"import\s+er134|from\s+er134", src), name)

    def test_deprecated_er006_nuance_processes_have_no_callers(self):
        """M7: er006のNUANCE_EXPLANATION/NUANCE_OVERLAP_JUDGEは定義のみ残置(DEPRECATED)。呼出元は0(Dangling)。閉集合を検査するtestは参照してよい。"""
        pat = re.compile(r"NUANCE_EXPLANATION|NUANCE_OVERLAP_JUDGE")
        offenders = []
        for name in os.listdir(ROOT):
            if not name.endswith(".py") or name == "er006_model_routing_contract_01.py" or "test" in name:
                continue
            with open(os.path.join(ROOT, name), encoding="utf-8", errors="replace") as f:
                if pat.search(f.read()):
                    offenders.append(name)
        self.assertEqual(offenders, [])

    def test_removed_api_surface_is_gone(self):
        for mod, names in ((g, ("render_nuance_html_block", "nuance_is_adopted", "expected_nuance_blocks", "verify_nuance_in_section", "NUANCE_RESULT_FILENAME", "NUANCE_ADOPTED")),
                           (p2w, ("nuance_for_display", "finalize_nuance", "form_nuance_bundle")),
                           (cc, ("cmd_nuance_show", "cmd_nuance_select", "cmd_nuance_issue_spec", "nuance_state", "guard_nuance", "FILE_NUANCE", "FILE_NUANCE_SPEC"))):
            for n in names:
                self.assertFalse(hasattr(mod, n), f"{mod.__name__}.{n}")

    def test_runner_function_signatures_have_no_nuance_hooks(self):
        import inspect
        import er019_family_x_audio_production_runner_01 as x
        import er121_family_y_runner_01 as y
        import er026_family_z_fiction_production_runner_01 as z
        self.assertNotIn("nuance_enabled", inspect.signature(x.run_theme_scaffold).parameters)
        for r in (x, y, z):
            self.assertFalse(hasattr(r, "_nuance_cand_step") or hasattr(r, "_assert_nuance_final") or hasattr(r, "run_nuance_candidates_x"), r.__name__)
        self.assertNotIn("nuance", y.STAGE_EST_JPY)
        self.assertNotIn("nuance", z.E2E_STAGE_EST_JPY)


class T2_LegacyFilesAreNotRead(GBase):
    def _final(self, env):
        self.prep_grammar()
        self.form(env, self.gram(pick=(0,)))
        out = self.finalize()
        return out["result"], os.path.join(self.sd, f"{g.PART2_FILE_STEM}.md")

    def test_compose_expected_counts_and_verify_ignore_legacy_nuance_files(self):
        with Env(self.tmp) as env:
            res, md = self._final(env)
            before = p2w.compose_page_html("<section class='study'>P1</section>", res)
            counts0 = p2w.expected_block_counts(self.sd, level="b1b")
            for name, doc in (("nuance_spec.json", {"version": "nuance_v1"}),
                              ("nuance_result.json", {"schema": "nuance_result_v1", "level_key": "b1b", "status": "ADOPTED",
                                                      "candidate": {"expression": "at least", "focus": "f", "explanation_ja": "e", "quote_en": "At least.", "quote_ja": "少なくとも"}}),
                              ("nuance_candidate.json", {"status": "CANDIDATE"}), ("confirmed_nuance.json", {"decision": "adopted"})):
                jd(os.path.join(self.sd, name), doc)
            after = p2w.compose_page_html("<section class='study'>P1</section>", res)
            self.assertEqual(before, after)                                                    # 旧ファイルがあっても合成は同一
            self.assertEqual(before.count("ニュアンス解説"), 0)
            counts1 = p2w.expected_block_counts(self.sd, level="b1b")
            self.assertEqual(counts0, counts1)
            self.assertEqual(counts1["nuance_blocks"], 0)
            p2w.verify_outputs(self.sd, PARAS, LABEL, level="b1b", next_command="x", md_path=md, html_text=after)   # 旧ファイルありでもPASS

    def test_block_in_page_is_stop_by_structure_not_substring(self):
        with Env(self.tmp) as env:
            res, md = self._final(env)
            ok = p2w.compose_page_html("<section class='study'>P1</section>", res)
            for bad in (ok + BLOCK, ok + BLOCK + BLOCK):
                with self.assertRaises(g.Part2Stale) as e:
                    p2w.verify_outputs(self.sd, PARAS, LABEL, level="b1b", next_command="x", md_path=md, html_text=bad)
                self.assertIn("NUANCE_CORNER_ABOLISHED", str(e.exception))
            # 文字列の部分一致では止めない: 語としての『ニュアンス解説』や文法の必須見出しは別物
            self.assertEqual(g.count_nuance_blocks("<p>ニュアンス解説という語を含む本文</p>"), 0)
            self.assertEqual(g.count_nuance_blocks(BLOCK), 1)
            self.assertEqual(g.count_nuance_blocks("<h3>意味・ニュアンス・表現効果</h3>"), 0)         # 文法の必須見出し(維持)


class T3_FormAndPayloadRejection(GBase):
    def test_old_payload_shapes_are_explicitly_refused_and_nothing_is_recorded(self):
        with Env(self.tmp) as env:
            self.prep_grammar()
            cands = self._gen(env)
            base = self._payload(cands, cat1=[1, 2, 3], cat2=[4, 5], grammar=self.gram(pick=(0,)), level="b1b")
            for label, mod in (("schema_minor=2", lambda pl: pl.update(schema_minor=2)),
                               ("selection.nuance", lambda pl: pl["selection"].update(nuance={"decision": "adopt", "candidate_sha256": "x", "id": "n"}))):
                pl = json.loads(json.dumps(base))
                mod(pl)
                with self.assertRaises(cc.CliError) as e:
                    cc.cmd_from_form(self.run_dir, "b1b", self._write(pl, "old.json"), "human", self.uref)
                self.assertIn("NUANCE_CORNER_ABOLISHED", str(e.exception), label)
                self.assertIsNone(self.rec(), label)                                              # 黙って受理して確定しない
            out = cc.cmd_from_form(self.run_dir, "b1b", self._write(base, "new.json"), "human", self.uref)   # 新形式は従来どおり通る
            self.assertEqual(out["grammar"], 1)
            self.assertNotIn("nuance", out)
            self.assertNotIn("nuance", self.rec())

    def test_payload_guard_helper_structure(self):
        with self.assertRaises(cc.CliError):
            cc._reject_abolished_nuance_payload({"schema_minor": 2, "selection": {}})
        with self.assertRaises(cc.CliError):
            cc._reject_abolished_nuance_payload({"schema_minor": 1, "selection": {"nuance": {}}})
        cc._reject_abolished_nuance_payload({"schema_minor": 1, "selection": {"key_phrase": []}})   # 新形式は通る

    def test_readable_restore_refuses_aif2(self):
        with self.assertRaises(R.RestoreError) as e:
            R.restore("記事：x｜y\n照合コード(変更しないでください)：AIF2-slug-abcdef-12345678-12345678-1234567890-0-0-0-abcd\n")
        self.assertIn("NUANCE_CORNER_ABOLISHED", str(e.exception))
        self.assertFalse(hasattr(R, "nuance_of") or hasattr(R, "nuance_n8"))

    def test_make_code_is_aif1_only(self):
        code = R.make_code("s", {"candidates_sha256": "a" * 64, "source": {"text_sha256": "b" * 64}}, "d6d6d6", [], [], "")
        self.assertTrue(code.startswith("AIF1-"))


@unittest.skipUnless(shutil.which("node"), "node not installed")
class T4_FormJs(unittest.TestCase):
    def _node(self, js: str):
        r = subprocess.run(["node", "-e", js], capture_output=True, text=True, encoding="utf-8", cwd=ROOT, timeout=60)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout.strip()

    def test_form_logic_has_no_nuance_api(self):
        out = self._node("const FL=require('./user_test/selection_form_v3/form_logic.js');"
                         "const bad=['hasNuanceSpec','nuanceOf','nuanceDecision','chooseNuance','nuanceConflicts','nuanceBlocked','nuanceBodyText','MARK_N_BEGIN'].filter(k=>k in FL);"
                         "console.log(JSON.stringify(bad));")
        self.assertEqual(json.loads(out), [])

    def test_old_nuance_data_is_flagged_by_validate_index(self):
        # 旧nuance_spec付きのデータをindexに載せるとvalidateIndexが『旧形式データ』エラーを返す(フォームに出さず再出力を促す)
        js = ("const FL=require('./user_test/selection_form_v3/form_logic.js');const fs=require('fs');"
              "const idx=JSON.parse(fs.readFileSync('user_test/selection_form_v3/data/articles.json','utf8'));"
              "console.log(JSON.stringify(FL.validateIndex(idx).filter(x=>/旧形式/.test(x))));")
        errs = json.loads(self._node(js))
        self.assertEqual(errs, [])                                                              # 現行のindexに載るデータは再出力済み(旧形式なし)
        with open(os.path.join(FORM_DIR, "form_logic.js"), encoding="utf-8") as f:
            src = f.read()
        self.assertIn("旧形式データです", src)
        self.assertNotIn("AIF2", re.sub(r"//[^\n]*", "", src))                                  # コードとしてAIF2を生成しない(コメントの廃止注記のみ)

    def test_v3_form_html_has_no_nuance_ui(self):
        with open(os.path.join(FORM_DIR, "index.html"), encoding="utf-8") as f:
            html = f.read()
        self.assertNotIn("nuance", html)
        self.assertNotIn("ニュアンス", html)


class T5_M6_LegacyRecordAndRegenerate(GBase):
    """M6: 旧`rec["nuance"]`付き確定record(Y姓run_02と同形)のload/G1/revise/rebind。"""

    def _legacy_record(self, env):
        self.prep_grammar()
        self.form(env, self.gram(pick=(0,)))
        self.ensure(env)
        rec = self.rec()
        side_path = os.path.join(self.sd, "confirmed_nuance.json")
        jd(side_path, {"schema": "eigo_radio_confirmed_nuance_v1", "decision": "adopted", "level": "b1b", "confirmation_id": rec["confirmation_id"],
                       "candidate": {"quote_en": "A sentence that exists nowhere in the article."}})
        rec["nuance"] = {"path_rel": os.path.relpath(side_path, self.run_dir).replace(os.sep, "/"), "sidecar_sha256": "0" * 64, "decision": "adopted", "level": "b1b",
                         "schema": "eigo_radio_confirmed_nuance_v1"}
        with rv.review_lock(self.kp_dir, rv.KIND_KP, "t"):
            cc.save_record(self.kp_dir, rec)
        return side_path

    def test_legacy_record_loads_and_passes_g1_without_checking_the_nuance_sidecar(self):
        with Env(self.tmp) as env:
            side_path = self._legacy_record(env)
            self.assertIn("nuance", self.rec())
            self.assertEqual(cc._problems_self(self.rec()), [])
            self.consume()                                                                    # G1(消費者入口)。旧版は sha不一致でINTEGRITY
            os.remove(side_path)                                                              # sidecarが消えていても検査しない
            self.consume()

    def test_revise_drops_the_old_nuance_mark_and_keeps_sidecar_file_untouched(self):
        with Env(self.tmp) as env:
            side_path = self._legacy_record(env)
            cid = self.rec()["items"][0]["candidate_id"]
            cc.cmd_revise(self.run_dir, "b1b", "human", self.uref, "訳の修正", [f"{cid}=新しい訳"])
            self.assertNotIn("nuance", self.rec())                                             # 新版に引き継がない
            self.assertTrue(os.path.exists(side_path))                                         # M4: 旧sidecarは削除・移動しない(OSF Trialの参照元)
            self.ensure(env)
            self.consume()

    def test_rebind_does_not_issue_on_an_old_adopted_nuance_quote(self):
        with Env(self.tmp) as env:
            self._legacy_record(env)
            from er119_test_support_01 import ARTICLE
            cc.stale_or_rebind(self.kp_dir, ARTICLE + "\n\nAn extra closing paragraph is appended here.", "f" * 64)
            fields = []
            ip = cc.paths_of(self.kp_dir)["issue_json"]
            if os.path.exists(ip):
                fields = [d["field"] for d in jl(ip)["diffs"]]
            self.assertNotIn("nuance.quote_en", fields)                                        # 旧ニュアンス採用文の引用が本文に無くても確定をISSUEにしない

    def test_regenerate_stage_nuance_cand_is_an_explicit_argparse_error(self):
        import contextlib
        import io
        import er026_family_z_fiction_production_runner_01 as z
        import er121_family_y_runner_01 as y
        for mod in (y, z):
            err = io.StringIO()
            with contextlib.redirect_stderr(err), self.assertRaises(SystemExit) as e:
                mod.build_parser().parse_args(["--regenerate-stage", "nuance_cand_b1b"])
            self.assertEqual(e.exception.code, 2)
            self.assertIn("nuance_cand_b1b", err.getvalue())


class T6_LegacyAif2Migration(unittest.TestCase):
    """撤去前に発行・送信済みの旧AIF2回答は、撤去前の旧フォームdata(git履歴)で照合できる場合に限り受理(ニュアンス節は読み捨て)。それ以外は拒否のまま。
    実データ(雪女Std。回答原文=delegation_log、旧data=git履歴のd6=651042)を使う。"""
    STEM = "yuki_onna__a2__prod"
    D6 = "651042"
    HR = os.path.join(ROOT, "docs", "pm", "delegation_log", "2026-10-30_FAMILY-Z-YUKI-ONNA-PRODUCTION-01_USER_HR_01.md")

    @classmethod
    def setUpClass(cls):
        t = open(cls.HR, encoding="utf-8").read().split("\n")
        i = next(k for k, ln in enumerate(t) if ln.startswith("記事：雪女(Yuki-Onna)｜Standard"))
        j = next(k for k in range(i, len(t)) if t[k].startswith("照合コード") and "AIF2-" in t[k])
        cls.text = "\n".join(t[i:j + 1]) + "\n"
        cls.old = R.git_history_lookup(cls.STEM, cls.D6)

    def setUp(self):
        if self.old is None:
            self.skipTest("旧フォームdata(git履歴)が取得できない環境")

    def test_accepts_with_matching_legacy_data_and_discards_nuance(self):
        payload, notes = R.restore(self.text, legacy_form_data=self.old)
        self.assertTrue(payload["restore_meta"]["legacy"]["legacy_aif2_accepted"])
        self.assertEqual(payload["restore_meta"]["legacy"]["legacy_form_data_d6"], self.D6)
        self.assertEqual(len(payload["restore_meta"]["legacy"]["legacy_form_data_sha256"]), 64)
        self.assertEqual(payload["article"]["level"], "a2")
        self.assertNotIn("nuance", json.dumps(payload, ensure_ascii=False).lower().replace("nuance_section", ""))
        self.assertNotIn("nuance", payload["selection"])
        self.assertNotEqual(payload.get("schema_minor"), 2)
        cc._reject_abolished_nuance_payload(payload)   # 確定側のガードも通る(例外なし)
        self.assertTrue(any("移行受理" in n for n in notes))

    def test_refused_without_legacy_data(self):
        with self.assertRaises(R.RestoreError) as e:
            R.restore(self.text)
        self.assertIn("NUANCE_CORNER_ABOLISHED", str(e.exception))

    def test_refused_when_legacy_data_does_not_match_code(self):
        other = self.old.replace(b'"name"', b'"nam3"', 1)   # d6が変わる=別データ
        with self.assertRaises(R.RestoreError) as e:
            R.restore(self.text, legacy_form_data=other)
        self.assertIn("NUANCE_CORNER_ABOLISHED", str(e.exception))

    def test_refused_when_current_data_differs_beyond_nuance_keys(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            cur = json.load(open(os.path.join(R.DEFAULT_DATA_DIR, self.STEM + ".json"), encoding="utf-8"))
            cur["name"] = cur["name"] + "X"
            json.dump(cur, open(os.path.join(td, self.STEM + ".json"), "w", encoding="utf-8"), ensure_ascii=False)
            with self.assertRaises(R.RestoreError) as e:
                R.restore(self.text, data_dir=td, legacy_form_data=self.old)
            self.assertIn("NUANCE_CORNER_ABOLISHED", str(e.exception))

    def test_refused_when_nuance_decision_is_tampered(self):
        bad = self.text.replace("ニュアンス解説：不採用", "ニュアンス解説：採用", 1)
        self.assertNotEqual(bad, self.text)
        with self.assertRaises(R.RestoreError) as e:
            R.restore(bad, legacy_form_data=self.old)
        self.assertIn("n8", str(e.exception))

    def test_refused_when_selection_is_tampered(self):
        bad = self.text.replace("- mist：霧\n", "", 1)
        with self.assertRaises(R.RestoreError):
            R.restore(bad, legacy_form_data=self.old)

    def test_aif2_is_never_issued(self):
        src = open(os.path.join(ROOT, "er128_form_readable_restore_01.py"), encoding="utf-8").read()
        self.assertEqual(R.CODE_VERSION, "AIF1")
        self.assertNotIn('f"AIF2-', src)                     # make_codeはAIF1専用(AIF2の発行経路なし)
        self.assertNotIn("AIF2-", re.sub(r"#[^\n]*", "", open(os.path.join(FORM_DIR, "form_logic.js"), encoding="utf-8").read()))


if __name__ == "__main__":
    unittest.main()
