# -*- coding: utf-8 -*-
"""er053_family_x_factlock_ja_writer_01 (W-1 Production module) のtest(API呼び出し0、費用¥0。client はstub)。
Trial moduleのimportはこのtest内に限る(Production moduleはimportしない)。
実行: .venv/Scripts/python.exe -m pytest er053_family_x_factlock_ja_writer_01_test_01.py -q
"""
from __future__ import annotations

import ast
import glob
import hashlib
import inspect
import json
import os
import re
import shutil
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

import er003_audio_tts_asr_safety as safety
import er006_model_routing_contract_01 as routing
import er019_family_x_ja_writer_o_r1_r2_01 as jaw
import er053_b3_annotation_contract_01 as contract
import er053_dev_b3_fixture_adapter_01 as adapter
import er053_family_x_factlock_ja_writer_01 as w1

HERE = os.path.dirname(os.path.abspath(__file__))
T = os.path.join(HERE, "er052_output", "factlock_astra_e2e_trial_01")
GOLDEN = os.path.join(HERE, "er053_output", "risk_flagger_production_wiring_01", "golden", "w1_golden_prompts_01.json")


def sh(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


# DESIGN_03 2-2 の sha256 表(30項目。HEAD 4c303184 で実測された値)。
PINNED = {
    "P1": "313120e94232497290e7efac2df1210dc628a8a1b497bb04e7174b5a98442f7f", "P2": "e72822deeabf4d395b02e5f03b7a6a177203b123d9a41613a0347cb53e9377fc",
    "P3": "4ff7844384e20534ae45e1e6a19a79970cfe88cfac6d05822723d605f8396d5f", "P4": "3f4c6f3a4a54a934b5824a4b2cb2ba6e5eef07b56d5879f3b7109a154c0155ed",
    "P5": "74b948719e14fd7184ff3719d36639ede7905e45cef95b97c1cca1a5638b2bf1",
    "X1": "e741d7b52c3cb0e6d13d175cd07fa0ca9dc9214a897eadefd81a42e1ce582c70", "X2": "3040b63717495c49b7155dc33ed23edfb4968b1bdd37276d649d9f06d92f653d",
    "X3": "b1a952f90bcd82bac0938bc02fc41e524a51216ff469ef3b69fb119598ec9cf4", "X4": "2521939572da8d300ced77b6035a424afe10624c55c2487bec0ecf06834a4ed8",
    "X5": "fcce9077a398c39b9c67b76bc150474d9d9421c16d2d06a7ce9df2b5b4efa0d5",
    "F1": "fbc1f553adc5a73f33b7c9986a5e98e1eaf0b6a4f6b7f0c79ff5f6888e6ecc62", "F2": "67515a1efef63c7a1999bf89e83d94fb193d2a6587c5ed67b5b73b1b7c64c8b4",
    "F3": "15cd9bc7753dbbd79713efb3aea1094a19f082d74303f6bbd55e00194a88a856", "F4": "1809af1445c2fb1a96ac9985194831f0418cc57c1b3b29c4ba4de4352691bbaf",
    "F5": "0dab13bf26c73673d9e20923dd7bc20e20b98d90c038357f4472c7687f7f229d", "F6": "c98fd66a945bef782c501112bea27204a0c1e367ca660d49705a99a988e40bd1",
    "F7": "4590a0650be08f7e453174806dcbcfe6e43e62c6fff6c25d3a02c408b8419391", "F8": "9919d5fef338e7184e217ca4f2bfb45ed7e5a4ec30cfd4a46354e97f1df1d95b",
    "F9": "b360e7517b949959508c6a156d68a7ba7e501509ff79b8c64b240a6d8e4a0b48", "F10": "2778bee0f53db2ee3d87af4f07ac256268ed8c2fd43e1de54f338e7f3b52fd34",
    "F11": "d8ef033a8f9c29d5cb973e85996d02962dd326f29ef23feadcd9a5f05270c460",
    "E1": "6108a7cddaa9eaf31262354ba32d33e4683ccaf810d861f27e3dcc8972028366", "E2": "d1fbb04224d346e79c588b8e69da4dcfe26e758ceefc71aa83d13ff7f216ed8d",
    "E3": "0629ab47a18ccb986844d8cff4ea087a9690eb8a7b8aefb28039496eec603b73", "E4": "067030ff53ecb76a4d1477a3deace07b3e1fac438a33cb873edbe045cf6927fe",
    "E5": "eaf0592f1936cb360e8ec0ef4b547c269ca105e8f9692691a11d25ff310455dd", "E6": "57dfde90933115dcbb4952e280c09843ba44d47162a51cda7eb49e04cfa40a94",
    "E7": "c0bfcc90a8d287a375f91784349d6b8bb478b0533bafd2dbe7776ba6f1b93722", "E8": "18b80d6e6a170176a496b7adc3030b72e77cba86d02b6ad08aee260f90377eef",
    "E9": "d5c976c3135df5872d591484c4783944c65f2cc72170fab30f9117c9bfe9272e",
}


class Identity(unittest.TestCase):
    """Trial版との同一性(Trial moduleはここでだけimport)。"""

    @classmethod
    def setUpClass(cls):
        import er052_factlock_astra_e2e_runner_01 as e2e
        import er052_factlock_writer_trial_01_run as fl
        import er003_v1_n3_01_advanced_adaptation_generate as adv
        cls.e2e, cls.fl, cls.adv = e2e, fl, adv

    def test_pinned_table_has_30_items(self):
        self.assertEqual(len(PINNED), 30)

    def test_trial_values_equal_pinned_design_table(self):
        e2e, fl, adv = self.e2e, self.fl, self.adv
        live = {
            "P1": sh(e2e.USER_TMPL), "P2": sh(fl.FACTLOCK_R0_BLOCK_HEAD), "P3": sh(fl.FACTLOCK_R0_BLOCK_TAIL), "P4": sh(fl.MUSTFIX_PRIORITY),
            "P5": sh(fl.build_r0_block(jaw.CONCRETENESS_CONTROL_AN3_BLOCK)),
            "X1": sh(fl.TAG_RE.pattern), "X2": sh(fl.BROAD_TAG_RE.pattern), "X3": sh(fl.MARK_RE.pattern), "X4": sh(e2e.TAG_LEAK_RE.pattern),
            "X5": sh(e2e.ECHO_RE.pattern),
            "F1": sh(inspect.getsource(fl.strip_tags)), "F2": sh(inspect.getsource(fl.parse_annotated_facts)),
            "F3": sh(inspect.getsource(fl.build_r0_block)), "F4": sh(inspect.getsource(e2e.strip_markdown)),
            "F5": sh(inspect.getsource(e2e.dash_to_comma)), "F6": sh(inspect.getsource(e2e.postprocess_ja)),
            "F7": sh(inspect.getsource(e2e.assert_no_tag_leak)), "F8": sh(inspect.getsource(e2e.clean_ja_for_next)),
            "F9": sh(inspect.getsource(e2e.detect_r0_echo)), "F10": sh(inspect.getsource(e2e.parse_brief_md)),
            "F11": sh(inspect.getsource(e2e.call_astra)),
            "E1": sh(jaw.R0_PROMPT), "E2": sh(jaw.DEVELOPER_MESSAGE), "E3": sh(jaw.SYMBOL_PREVENTION_BLOCK_JA),
            "E4": sh(jaw.CONCRETENESS_CONTROL_AN3_BLOCK), "E6": sh(inspect.getsource(safety.normalize_ellipsis_pause_ja)),
            "E7": sh(adv.FAMILY_X_IN_ONE_LINE_INSTRUCTION_TEMPLATE_M1), "E8": sh(adv.FAMILY_X_IN_ONE_LINE_M1_REQUIREMENT_LINE),
            "E9": sh(inspect.getsource(adv.build_family_x_in_one_line_prompt)),
        }
        for k, v in live.items():
            self.assertEqual(v, PINNED[k], k)

    def test_E5_build_original_prompt_source_pre_c2_only(self):
        """E5(jaw.build_original_prompt のソースsha)は C2(must_fix/full_ledger_text引数の削除)で変わる。
        C2では本testをgolden出力比較(test_golden_r0_prompts)へ置換すること。C1(現HEAD)ではまだ不変。"""
        self.assertEqual(sh(inspect.getsource(jaw.build_original_prompt)), PINNED["E5"])

    def test_production_constants_equal_trial(self):
        e2e, fl = self.e2e, self.fl
        self.assertEqual(w1.USER_TMPL, e2e.USER_TMPL)
        for n in ("FACTLOCK_R0_BLOCK_HEAD", "FACTLOCK_R0_BLOCK_TAIL", "MUSTFIX_PRIORITY"):
            self.assertEqual(getattr(w1, n), getattr(fl, n), n)
        for n in ("TAG_RE", "BROAD_TAG_RE", "MARK_RE", "FACT_LINE_RE"):
            self.assertEqual(getattr(w1, n).pattern, getattr(fl, n).pattern, n)
        self.assertEqual(w1.TAG_LEAK_RE.pattern, e2e.TAG_LEAK_RE.pattern)
        self.assertEqual(w1.ECHO_RE.pattern, e2e.ECHO_RE.pattern)
        self.assertEqual(sh(w1.USER_TMPL), PINNED["P1"])
        self.assertEqual(sh(w1.FACTLOCK_R0_BLOCK_HEAD), PINNED["P2"])
        self.assertEqual(sh(w1.FACTLOCK_R0_BLOCK_TAIL), PINNED["P3"])
        self.assertEqual(sh(w1.MUSTFIX_PRIORITY), PINNED["P4"])
        self.assertEqual(sh(w1.build_r0_block(jaw.CONCRETENESS_CONTROL_AN3_BLOCK)), PINNED["P5"])
        for n, k in (("TAG_RE", "X1"), ("BROAD_TAG_RE", "X2"), ("MARK_RE", "X3"), ("TAG_LEAK_RE", "X4"), ("ECHO_RE", "X5")):
            self.assertEqual(sh(getattr(w1, n).pattern), PINNED[k], n)

    def test_production_functions_byte_identical(self):
        for name, key in (("strip_tags", "F1"), ("parse_annotated_facts", "F2"), ("build_r0_block", "F3"), ("strip_markdown", "F4"),
                          ("dash_to_comma", "F5"), ("postprocess_ja", "F6"), ("assert_no_tag_leak", "F7"),
                          ("detect_r0_echo", "F9"), ("parse_brief_md", "F10")):
            self.assertEqual(sh(inspect.getsource(getattr(w1, name))), PINNED[key], name)

    def test_F8_tolerance_only_fl_prefix_and_import(self):
        trial = inspect.getsource(self.e2e.clean_ja_for_next)
        norm = trial.replace("    import er052_factlock_writer_trial_01_run as fl\n", "").replace("fl.strip_tags(text)", "strip_tags(text)")
        self.assertEqual(inspect.getsource(w1.clean_ja_for_next), norm)

    def test_F11_tolerance_exactly_three_points(self):
        trial = inspect.getsource(self.e2e.call_astra)
        norm = trial.replace("cl.logging_context(TRIAL_ID, stage)", "cl.logging_context(THEME_TAG, stage)")
        norm = norm.replace('time.sleep(0 if os.environ.get("E2E_STUB") else 3 * (i + 1))', "time.sleep(3 * (i + 1))")
        head = "def call_astra(client, user: str, stage: str, retries: int = 2):\n"
        self.assertTrue(norm.startswith(head))
        norm = head + ('    routing.require_model("FAMILY_X_FACTLOCK_REVISE", ASTRA_MODEL)   '
                       '# 許容差(2): API call前のfail-closed(Trialは require_model_or_override)\n') + norm[len(head):]
        self.assertEqual(inspect.getsource(w1.call_astra), norm)
        self.assertNotIn("E2E_STUB", inspect.getsource(w1.call_astra))

    def test_E_assets_unchanged_and_used_not_copied(self):
        self.assertEqual(sh(jaw.R0_PROMPT), PINNED["E1"])
        self.assertEqual(sh(jaw.DEVELOPER_MESSAGE), PINNED["E2"])
        self.assertEqual(w1.verbatim_shas()["R0_PROMPT"], PINNED["E1"])
        self.assertEqual(w1.verbatim_shas()["DEVELOPER_MESSAGE"], PINNED["E2"])
        self.assertEqual(w1.verbatim_shas()["SYMBOL_PREVENTION_BLOCK_JA"], PINNED["E3"])
        self.assertEqual(w1.verbatim_shas()["CONCRETENESS_CONTROL_AN3_BLOCK"], PINNED["E4"])
        self.assertEqual(w1.verbatim_shas()["R0_BLOCK"], PINNED["P5"])

    def test_model_literals_equal_current_jaw_settings(self):
        self.assertEqual(w1.R0_MODEL, jaw.WRITER_MODEL)
        self.assertEqual(w1.R0_EFFORT, jaw.WRITER_EFFORT)
        self.assertEqual(routing.PROCESS_MODEL_MAP["FAMILY_X_FACTLOCK_R0"], w1.R0_MODEL)
        self.assertEqual(routing.PROCESS_MODEL_MAP["FAMILY_X_FACTLOCK_REVISE"], w1.ASTRA_MODEL)
        self.assertEqual(self.e2e.ASTRA_MODEL, w1.ASTRA_MODEL)


class GoldenPrompts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.g = json.load(open(GOLDEN, encoding="utf-8"))

    def _check(self, group):
        findings = safety.detect_prohibited_symbols(self.g["sample_text_for_regen"], language="ja")
        n = 0
        for slug, e in self.g[group].items():
            text = open(os.path.join(HERE, e["md_path"]), encoding="utf-8").read()
            self.assertEqual(sh(text), e["md_sha256"], slug)                       # 入力md自体が変わっていない
            storyline, facts = w1.parse_brief_md(text)
            self.assertEqual(storyline, e["storyline"])
            self.assertEqual(w1.build_r0_prompt(storyline, facts), e["r0_prompt"], slug)
            self.assertEqual(w1.build_r0_symbol_regen_prompt(storyline, facts, findings), e["regen_prompt"], slug)
            n += 1
        return n

    def test_golden_r0_prompts_annotation_final_9(self):
        self.assertEqual(self._check("annotation_final"), 9)

    def test_golden_r0_prompts_new_arm_runs_8(self):
        self.assertEqual(self._check("new_arm_runs"), 8)


class TrialArtifactCrossCheck(unittest.TestCase):
    """new腕8本の実Trial成果物(Astra user文sha・後処理結果・最終文)と一致する。"""

    SLUGS = ["byd_recall", "hormuz", "meta", "openai_copyright", "semiconductor_earnings", "small_bag", "space_weapons", "streaming_price"]

    def _rdt(self, p):
        return open(p, encoding="utf-8").read()

    def test_astra_user_sha_postprocess_and_final_match_trial_runs(self):
        for s in self.SLUGS:
            nw = os.path.join(T, "runs", s, "new", "new_writer")
            r0 = self._rdt(os.path.join(nw, "r0.md"))
            user1 = w1.USER_TMPL.format(body=r0.strip())
            self.assertEqual(sh(user1), json.load(open(os.path.join(nw, "r1.response.json"), encoding="utf-8"))["user_message_sha256"], s)
            raw1 = self._rdt(os.path.join(nw, "r1.raw.md"))
            self.assertEqual(w1.postprocess_ja(raw1.strip()), self._rdt(os.path.join(nw, "r1.p1.md")), s)
            user2 = w1.USER_TMPL.format(body=raw1.strip())
            self.assertEqual(sh(user2), json.load(open(os.path.join(nw, "r2.response.json"), encoding="utf-8"))["user_message_sha256"], s)
            raw2 = self._rdt(os.path.join(nw, "r2.raw.md"))
            final = w1.clean_ja_for_next(w1.postprocess_ja(raw2.strip()))
            self.assertEqual(final, self._rdt(os.path.join(T, "runs", s, "new", "ja_writer", "revision2.md")), s)

    def test_r0_factlock_block_sha_recorded_in_trial_meta(self):
        for s in self.SLUGS:
            m = json.load(open(os.path.join(T, "runs", s, "new", "new_writer", "r0_meta.json"), encoding="utf-8"))
            self.assertEqual(m["factlock_r0_block_sha256"], PINNED["P5"], s)
            self.assertFalse(m["must_fix_applied"], s)


# ---------------------------------------------------------------- 実行フロー(stub client)
class FakeResp:
    def __init__(self, text, model, rid):
        self.output_text, self.model, self.id = text, model, rid
        self.usage = SimpleNamespace(input_tokens=100, output_tokens=50)


class FakeClient:
    """responses.create の呼出順に scripts を返す。scripts: [(text, model) or Exception]"""

    def __init__(self, scripts):
        self.scripts = list(scripts)
        self.calls = []
        self.responses = self

    def create(self, **kw):
        self.calls.append(kw)
        item = self.scripts.pop(0)
        if isinstance(item, Exception):
            raise item
        text, model = item
        return FakeResp(text, model, f"resp_{len(self.calls)}")


R0_OK = "メタの話\n人間が電話をしたというテストがありました。【事実1】\nこれは面白いですね。\n"
R1_RAW = "# タイトル\r\n\r\n**太字**の本文です。\r\n\r\n---\r\n続きです。"
R2_RAW = "# 新タイトル\n\n本文その2です。続きの文です。"


def make_out(slug="meta"):
    d = tempfile.mkdtemp(prefix="w1_test_")
    adapter.build_fixture(slug, d)
    return d


class FlowTests(unittest.TestCase):
    def setUp(self):
        self.out = make_out()
        self.sleep = mock.patch.object(w1.time, "sleep", lambda s: None)
        self.sleep.start()

    def tearDown(self):
        self.sleep.stop()
        shutil.rmtree(self.out, ignore_errors=True)

    def run_w1(self, scripts, **kw):
        c = FakeClient(scripts)
        return c, w1.run_w1_writer(self.out, client=c, **kw)

    def test_happy_path_calls_shape_and_outputs(self):
        c, r = self.run_w1([(R0_OK, "gpt-6-luna-2026"), (R1_RAW, "gpt-6-astra-2026"), (R2_RAW, "gpt-6-astra-2026")])
        self.assertEqual(len(c.calls), 3)
        k0, k1, k2 = c.calls
        # R0: developer + user, effort high, 単発(previous_response_id無し)
        self.assertEqual(k0["model"], "gpt-6-luna")
        self.assertEqual(k0["reasoning"], {"effort": "high"})
        self.assertEqual([m["role"] for m in k0["input"]], ["developer", "user"])
        self.assertEqual(k0["input"][0]["content"], jaw.DEVELOPER_MESSAGE)
        self.assertNotIn("previous_response_id", k0)
        # R1/R2: Astra, effort high, userのみ、previous_response_id/service_tier/developerなし
        for k in (k1, k2):
            self.assertEqual(k["model"], "gpt-6-astra")
            self.assertEqual(k["reasoning"], {"effort": "high"})
            self.assertEqual([m["role"] for m in k["input"]], ["user"])
            self.assertEqual(set(k), {"model", "reasoning", "input"})
        # R1 user = USER_TMPL(R0のタグ除去後本文)
        r0_clean = w1.clean_ja_for_next(R0_OK).strip() + "\n"
        self.assertEqual(k1["input"][0]["content"], w1.USER_TMPL.format(body=r0_clean.strip()))
        self.assertNotIn("【事実", k1["input"][0]["content"])
        # R2 user = R1の生出力(strip + CRLF->LF。Markdown記号は後処理前のまま)
        body2 = k2["input"][0]["content"]
        self.assertIn("**太字**", body2)
        self.assertNotIn("\r", body2)
        self.assertEqual(body2, w1.USER_TMPL.format(body=R1_RAW.replace("\r\n", "\n").strip()))
        # 出力ファイル
        d = os.path.join(self.out, "ja_writer")
        for f in ("original.md", "revision1.md", "revision2.md", "runtime_evidence.json", "factlock/r0_with_tags.md", "factlock/r1.raw.md",
                  "factlock/r2.raw.md", "factlock/r1.response.json", "factlock/r2.response.json", "factlock/r0_meta.json"):
            self.assertTrue(os.path.exists(os.path.join(d, f)), f)
        self.assertEqual(open(os.path.join(d, "revision2.md"), encoding="utf-8").read(), w1.clean_ja_for_next(w1.postprocess_ja(R2_RAW)))
        self.assertIn("【事実1】", open(os.path.join(d, "factlock", "r0_with_tags.md"), encoding="utf-8").read())
        self.assertNotIn("【", open(os.path.join(d, "original.md"), encoding="utf-8").read())
        ev = json.load(open(os.path.join(d, "runtime_evidence.json"), encoding="utf-8"))
        self.assertEqual(ev["chain_method"], "W-1")
        self.assertEqual(ev["annotated_md_sha256"], contract.validate_annotated_b3(self.out).annotated_md_sha256)
        self.assertEqual(ev["annotation_manifest_producer"], "trial_fixture")
        self.assertEqual(ev["title"], "新タイトル")
        self.assertEqual(ev["r1"]["model"], "gpt-6-astra-2026")
        self.assertEqual(ev["original"]["model"], "gpt-6-luna-2026")
        self.assertEqual(ev["r2"]["response_id"], "resp_3")
        self.assertEqual(ev["verbatim_shas"]["R0_BLOCK"], PINNED["P5"])
        self.assertEqual(r["title"], "新タイトル")
        # derive_japanese_title(audio runner)が読めるキー
        self.assertTrue(ev["title"])

    def test_r0_prompt_is_built_from_parsed_annotated_md_only(self):
        c, _ = self.run_w1([(R0_OK, "gpt-6-luna"), (R1_RAW, "gpt-6-astra"), (R2_RAW, "gpt-6-astra")])
        ann = open(os.path.join(self.out, "storyline_b3", "selected_brief_annotated.md"), encoding="utf-8").read()
        storyline, facts = w1.parse_brief_md(ann)
        self.assertEqual(c.calls[0]["input"][1]["content"], w1.build_r0_prompt(storyline, facts))
        self.assertIn("【事実1】", c.calls[0]["input"][1]["content"])      # 注記済み(タグ付き)factsが入る
        self.assertIn("[ニュース]", c.calls[0]["input"][1]["content"])

    def test_budget_check_called_between_r1_and_r2_and_before_each(self):
        order = []
        c = FakeClient([(R0_OK, "gpt-6-luna"), (R1_RAW, "gpt-6-astra"), (R2_RAW, "gpt-6-astra")])
        orig = c.create

        def create(**kw):
            order.append("call")
            return orig(**kw)
        c.create = create
        w1.run_w1_writer(self.out, client=c, budget_check=lambda: order.append("budget"))
        self.assertEqual(order, ["budget", "call", "budget", "call", "budget", "call"])   # R0前・R1前・R1/R2間

    def test_budget_check_exception_stops_before_api(self):
        def bc():
            raise RuntimeError("[STOP] budget")
        c = FakeClient([])
        with self.assertRaises(RuntimeError):
            w1.run_w1_writer(self.out, client=c, budget_check=bc)
        self.assertEqual(c.calls, [])

    def test_r0_symbol_qa_regenerates_once_with_note_and_before_tag_strip(self):
        bad = "メタ（括弧）の話\n人間が電話をしました。【事実1】\n"
        c, r = self.run_w1([(bad, "gpt-6-luna"), (R0_OK, "gpt-6-luna"), (R1_RAW, "gpt-6-astra"), (R2_RAW, "gpt-6-astra")])
        self.assertEqual(len(c.calls), 4)
        ann = open(os.path.join(self.out, "storyline_b3", "selected_brief_annotated.md"), encoding="utf-8").read()
        storyline, facts = w1.parse_brief_md(ann)
        findings = safety.detect_prohibited_symbols(bad, language="ja")          # タグ付き本文に対する判定
        self.assertEqual(c.calls[1]["input"][1]["content"], w1.build_r0_prompt(storyline, facts) + "\n\n" + safety.build_symbol_violation_prompt_note(findings))
        self.assertTrue(r["runtime_evidence"]["symbol_qa"]["r0"]["regenerated"])

    def test_r0_symbol_qa_stop_if_remains_and_no_astra_call(self):
        bad = "メタ（括弧）の話\n人間が電話。【事実1】\n"
        c = FakeClient([(bad, "gpt-6-luna"), (bad, "gpt-6-luna")])
        with self.assertRaises(w1.JASymbolCheckStopError) as cm:
            w1.run_w1_writer(self.out, client=c)
        self.assertEqual(cm.exception.stage, "r0_symbol")
        self.assertEqual(len(c.calls), 2)                    # 上限=1回再生成(既存T-01と同じ)。Astraは呼ばれない

    def test_astra_symbol_qa_case_a_reruns_r2_only_same_input(self):
        r2_bad = "# 題\n\n本文（括弧つき）です。"
        c, r = self.run_w1([(R0_OK, "gpt-6-luna"), (R1_RAW, "gpt-6-astra"), (r2_bad, "gpt-6-astra"), (R2_RAW, "gpt-6-astra")])
        self.assertEqual(len(c.calls), 4)
        self.assertEqual(c.calls[2]["input"], c.calls[3]["input"])             # 同一userでR2のみ再実行(Prompt変更なし)
        self.assertNotEqual(c.calls[1]["input"], c.calls[3]["input"])
        q = r["runtime_evidence"]["symbol_qa"]["r2"]
        self.assertTrue(q["rerun"])
        self.assertEqual(q["response_ids"], ["resp_3", "resp_4"])             # 両response_id記録
        self.assertEqual(r["runtime_evidence"]["r2"]["response_id"], "resp_4")
        self.assertEqual(open(os.path.join(self.out, "ja_writer", "revision2.md"), encoding="utf-8").read(), w1.clean_ja_for_next(w1.postprocess_ja(R2_RAW)))

    def test_astra_symbol_qa_stop_if_remains(self):
        r2_bad = "# 題\n\n本文（括弧つき）です。"
        c = FakeClient([(R0_OK, "gpt-6-luna"), (R1_RAW, "gpt-6-astra"), (r2_bad, "gpt-6-astra"), (r2_bad, "gpt-6-astra")])
        with self.assertRaises(w1.JASymbolCheckStopError) as cm:
            w1.run_w1_writer(self.out, client=c)
        self.assertEqual(cm.exception.stage, "r2_symbol")
        self.assertEqual(len(c.calls), 4)                    # R2のやり直しは1回のみ。R1は再実行しない

    def test_astra_rerun_budget_checks_before_and_after(self):
        r2_bad = "# 題\n\n本文（括弧つき）です。"
        order = []
        c = FakeClient([(R0_OK, "gpt-6-luna"), (R1_RAW, "gpt-6-astra"), (r2_bad, "gpt-6-astra"), (R2_RAW, "gpt-6-astra")])
        orig = c.create
        c.create = lambda **kw: (order.append("call"), orig(**kw))[1]
        w1.run_w1_writer(self.out, client=c, budget_check=lambda: order.append("budget"))
        self.assertEqual(order, ["budget", "call", "budget", "call", "budget", "call", "budget", "call", "budget"])

    def test_astra_model_mismatch_is_stop(self):
        c = FakeClient([(R0_OK, "gpt-6-luna"), (R1_RAW, "gpt-6.1-sol")])
        with self.assertRaises(w1.ProvenanceViolation):
            w1.run_w1_writer(self.out, client=c)
        self.assertEqual(len(c.calls), 2)

    def test_call_astra_transient_retry_two_then_success_and_exhaust(self):
        c = FakeClient([RuntimeError("a"), RuntimeError("b"), ("ok", "gpt-6-astra")])
        self.assertEqual(w1.call_astra(c, "u", "s").output_text, "ok")
        c2 = FakeClient([RuntimeError("a"), RuntimeError("b"), RuntimeError("c")])
        with self.assertRaises(RuntimeError):
            w1.call_astra(c2, "u", "s")
        self.assertEqual(len(c2.calls), 3)

    def test_tag_leak_stop(self):
        leaked = "題\n本文です。【 中核数値 】\n"
        c = FakeClient([(leaked, "gpt-6-luna")])
        with self.assertRaises(w1.TagLeak):
            w1.run_w1_writer(self.out, client=c)

    def test_routing_drift_stops_before_api(self):
        c = FakeClient([])
        with mock.patch.dict(routing.PROCESS_MODEL_MAP, {"FAMILY_X_FACTLOCK_R0": "gpt-9"}):
            with self.assertRaises(routing.ModelContractViolation):
                w1.run_w1_writer(self.out, client=c)
        self.assertEqual(c.calls, [])
        with mock.patch.dict(routing.PROCESS_MODEL_MAP, {"FAMILY_X_FACTLOCK_REVISE": "gpt-6-other"}):
            with self.assertRaises(routing.ModelContractViolation):
                w1.run_w1_writer(self.out, client=c)
        self.assertEqual(c.calls, [])

    def test_r0_echo_recorded_not_fixed(self):
        echo = "題\nこれ、ちょっと面白くない？と聞かれた話です。\n"
        c, r = self.run_w1([(echo + "【事実1】\n", "gpt-6-luna"), (R1_RAW, "gpt-6-astra"), (R2_RAW, "gpt-6-astra")])
        meta = json.load(open(os.path.join(self.out, "ja_writer", "factlock", "r0_meta.json"), encoding="utf-8"))
        self.assertTrue(meta["r0_echo"]["echo_anywhere"])
        self.assertEqual(len(c.calls), 3)                    # 復唱は記録のみ。再生成しない


class ContractGate(unittest.TestCase):
    def test_unannotated_b3_stops_before_any_api_call(self):
        d = make_out()
        try:
            os.remove(os.path.join(d, "storyline_b3", "selected_brief_annotated.md"))
            os.remove(os.path.join(d, "storyline_b3", "annotation.json"))
            os.remove(os.path.join(d, "storyline_b3", "annotation_manifest.json"))
            c = FakeClient([])
            with self.assertRaises(contract.AnnotatedB3ContractViolation):
                w1.run_w1_writer(d, client=c)
            self.assertEqual(c.calls, [])
            self.assertTrue(os.path.exists(os.path.join(d, "storyline_b3", "audit", "contract_violation.json")))
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_original_b3_passed_as_annotated_fails(self):
        d = make_out()
        try:
            sd = os.path.join(d, "storyline_b3")
            shutil.copyfile(os.path.join(sd, "selected_brief.md"), os.path.join(sd, "selected_brief_annotated.md"))
            mf = json.load(open(os.path.join(sd, "annotation_manifest.json"), encoding="utf-8"))
            mf["annotated_md_sha256"] = hashlib.sha256(open(os.path.join(sd, "selected_brief_annotated.md"), "rb").read()).hexdigest()
            json.dump(mf, open(os.path.join(sd, "annotation_manifest.json"), "w", encoding="utf-8"))
            sc = open(os.path.join(sd, "annotation.json"), "rb").read()
            mf["sidecar_sha256"] = hashlib.sha256(sc).hexdigest()
            json.dump(mf, open(os.path.join(sd, "annotation_manifest.json"), "w", encoding="utf-8"))
            c = FakeClient([])
            with self.assertRaises(contract.AnnotatedB3ContractViolation) as cm:
                w1.run_w1_writer(d, client=c)
            self.assertIn("V5", str(cm.exception))
            self.assertEqual(c.calls, [])
        finally:
            shutil.rmtree(d, ignore_errors=True)


class StaticTests(unittest.TestCase):
    MODS = ["er053_family_x_factlock_ja_writer_01.py", "er053_b3_annotation_contract_01.py"]

    def _tree(self, f):
        return ast.parse(open(os.path.join(HERE, f), encoding="utf-8").read())

    def test_no_trial_imports(self):
        for f in self.MODS + ["er053_risk_flagger_production_01.py", "er053_review_queue_01.py", "er053_en_sentence_splitter_01.py"]:
            for n in ast.walk(self._tree(f)):
                names = []
                if isinstance(n, ast.Import):
                    names = [a.name for a in n.names]
                elif isinstance(n, ast.ImportFrom):
                    names = [n.module]
                for m in names:
                    self.assertFalse(m.startswith(("er050", "er051", "er052", "b3_annotation", "annot_driver")), f"{f}: {m}")

    def test_T13_no_switch_cli_env_fallback(self):
        for f in self.MODS:
            src = open(os.path.join(HERE, f), encoding="utf-8").read()
            tree = ast.parse(src)
            for n in ast.walk(tree):
                if isinstance(n, (ast.Import, ast.ImportFrom)):
                    mods = [a.name for a in n.names] if isinstance(n, ast.Import) else [n.module]
                    for m in mods:
                        self.assertNotIn(m, ("argparse", "getopt", "click", "typer"), f)
                if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name):
                    self.assertFalse(n.value.id == "sys" and n.attr == "argv", f)
                    self.assertFalse(n.value.id == "os" and n.attr in ("environ", "getenv"), f)
                if isinstance(n, ast.FunctionDef):
                    for a in n.args.args + n.args.kwonlyargs:
                        self.assertIsNone(re.search(r"(allow|skip|bypass|disable|legacy|unannotated|fallback|no_annot|without_annot|force)", a.arg, re.I),
                                          f"{f}:{n.name}({a.arg})")
            for bad in ("E2E_STUB", "OPEN243", "OPEN233", "fact_check_mode", "legacy_checker"):
                self.assertNotIn(bad, re.sub(r"#.*", "", src) if bad != "E2E_STUB" else self._code_only(src), f"{f}: {bad}")

    @staticmethod
    def _code_only(src):
        """docstring/コメントを除いたコード部分(ASTのConstant以外)。E2E_STUBがコード上の識別子/文字列として残っていないことの確認用。"""
        tree = ast.parse(src)
        out = []
        for n in ast.walk(tree):
            if isinstance(n, ast.Name):
                out.append(n.id)
            elif isinstance(n, ast.Attribute):
                out.append(n.attr)
        consts = [n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str)
                  and not (len(n.value) > 60)]
        return "\n".join(out + consts)

    def test_contract_signature_has_only_out_dir(self):
        self.assertEqual(list(inspect.signature(contract.validate_annotated_b3).parameters), ["out_dir"])

    def test_w1_main_entry_params(self):
        self.assertEqual(list(inspect.signature(w1.run_w1_writer).parameters), ["out_dir", "client", "budget_check"])

    def _root_py_files(self):
        out = []
        for f in glob.glob(os.path.join(HERE, "*.py")):
            b = os.path.basename(f)
            if b.startswith("er053_") or b.endswith(("_test_01.py", "_test.py")) or b.startswith("test_"):
                continue
            out.append(f)
        return out

    def test_T14_dev_adapter_not_referenced_by_production(self):
        er053 = [f for f in glob.glob(os.path.join(HERE, "er053_*.py"))
                 if not f.endswith("_test_01.py") and os.path.basename(f) != "er053_dev_b3_fixture_adapter_01.py"]
        for f in self._root_py_files() + er053:
            self.assertNotIn("er053_dev_b3_fixture_adapter", open(f, encoding="utf-8", errors="replace").read(), os.path.basename(f))

    def test_w1_and_rf_not_called_from_any_production_runner_in_c1(self):
        for f in self._root_py_files():
            src = open(f, encoding="utf-8", errors="replace").read()
            for m in ("er053_family_x_factlock_ja_writer_01", "er053_risk_flagger_production_01", "er053_review_queue_01",
                      "er053_b3_annotation_contract_01"):
                self.assertNotIn(m, src, f"{os.path.basename(f)} references {m} (C1 is additive only; wiring is C2)")


if __name__ == "__main__":
    unittest.main()
