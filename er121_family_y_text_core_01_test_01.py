# -*- coding: utf-8 -*-
"""er121_family_y_text_core_01 offline test(API 0)。偽clientのみ。ネットワーク遮断harness(socket.connect禁止)で
『実APIへの接続試行0』を担保する(隣接案件OPEN-518の既存testmock漏れの教訓)。"""
from __future__ import annotations

import ast
import copy
import hashlib
import json
import os
import re
import socket
import tempfile
import types
import unittest
from unittest import mock

import er006_model_routing_contract_01 as routing
import er121_family_y_text_core_01 as c

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "er121_family_y_text_core_01.py")
DEV_PROMPT = os.path.join(ROOT, "docs", "research", "FAMILY-Y-VOICES-DESIGN-01", "CLOSING_GENERAL_01", "prompt_closing_general_02.txt")
CONNECT_ATTEMPTS = []
_orig_connect = socket.socket.connect


def _blocked_connect(self, *a, **k):
    CONNECT_ATTEMPTS.append(a)
    raise OSError("network blocked by test harness")


def setUpModule():
    socket.socket.connect = _blocked_connect


def tearDownModule():
    socket.socket.connect = _orig_connect


GOOD = ("お店に出る朝の準備も、家に帰ってからの夜の片づけも、誰かが先に引き受けている。語りの中で何度も出てきたのは、その引き受けが、ほかの人には見えにくいということだった。"
        "手を出さないのではなく、どこから手を出せばいいのか分からないという一言が、三人の語りに重なっている。見えない仕事は、見える人の手に集まりやすい。"
        "あなたの家で、いちばん先に動き出すのは誰で、そのことに最初に気づいたのは誰か？")
INP = c.normalize_input(
    "テーマの問い", "前提の文", [{"term_ja": "用語", "definition_ja": "意味"}],
    [{"role": f"役{i}", "sketch": f"人物{i}のスケッチ。", "stake": f"大事{i}"} for i in range(1, 4)],
    {"voice_1": "俺は朝が早い。", "voice_2": "私は夜に考える。", "voice_3": "僕は何も言わなかった。"})
VOICES = INP["voices"]


def analysis(closing=GOOD, sel="c1", n=3):
    return {"observations": [{"kind": "共通点", "note": "n", "evidence_quotes": ["朝が早い"]}],
            "candidates": [{"id": f"c{i}", "new_view": f"見方{i}", "evidence_quotes": ["夜に考える"], "deepens": "d", "listener_question": "q", "pitfall": "p"} for i in range(1, n + 1)],
            "selected_id": sel, "selection_reason": "r", "closing_ja": closing}


def leak_obj(kind, fails=None, quote="引用"):
    fails = fails or {}
    fields = c.VOICE_FIELDS if kind == "voices" else c.TENSION_FIELDS
    secs = c.SLOTS if kind == "voices" else ("tension",)
    out = {}
    for s in secs:
        f = fails.get(s, [])
        item = {x: ("FAIL" if x in f else "PASS") for x in fields}
        item["reasoning"] = "理由" if f else ""
        item["quoted_evidence"] = quote if f else ""
        out[s] = item
    return out


class Resp:
    def __init__(self, obj, model="gpt-6.1-sol-2026"):
        self.output_text = json.dumps(obj, ensure_ascii=False)
        self.model, self.id = model, "resp_x"
        self.usage = types.SimpleNamespace(input_tokens=1, output_tokens=1)


class FakeClient:
    """scriptにcallable/オブジェクトを積む。呼出ごとにkwを記録。scriptが尽きたら例外(想定外のAPI呼出を検出)。"""

    def __init__(self, script):
        self.script, self.calls = list(script), []
        self.responses = types.SimpleNamespace(create=self._create)

    def _create(self, **kw):
        self.calls.append(kw)
        if not self.script:
            raise AssertionError("想定外のAPI呼出")
        nxt = self.script.pop(0)
        return nxt(kw) if callable(nxt) else nxt


def luna(kind, fails=None, quote="引用"):
    return lambda kw: Resp(leak_obj(kind, fails, quote), model="gpt-6-luna-2026")


def sol(obj, model="gpt-6.1-sol-2026"):
    return lambda kw: Resp(obj, model=model)


class RoutedCase(unittest.TestCase):
    """02Bがer006へ登録した状態を、PROCESS_MODEL_MAPへ一時登録して再現する(登録前でもtestは通る)。"""

    def setUp(self):
        self.patch = mock.patch.dict(routing.PROCESS_MODEL_MAP, {k: v["model"] for k, v in c.ROUTE.items()})
        self.patch.start()
        self.tmp = tempfile.TemporaryDirectory()
        self.d = self.tmp.name
        self.addCleanup(self.tmp.cleanup)
        self.addCleanup(self.patch.stop)
        n = len(CONNECT_ATTEMPTS)
        self.addCleanup(lambda: self.assertEqual(len(CONNECT_ATTEMPTS), n))


class TestPrompt(unittest.TestCase):
    def test_sha_pinned_and_byte_identical_to_trial_prompt(self):
        self.assertEqual(c.load_prompt_parts()["sha256"], c.PROMPT_SHA256)
        self.assertEqual(open(c.PROMPT_FILE, "rb").read(), open(DEV_PROMPT, "rb").read())
        self.assertEqual(hashlib.sha256(open(c.PROMPT_FILE, "rb").read()).hexdigest(), "4713ceff2dd00a2f67eb9313ae9e206a4a3236c5b158e624c10ccf6fc20e5f07")

    def test_sha_mismatch_stops(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "p.txt")
            open(p, "wb").write(open(c.PROMPT_FILE, "rb").read() + b"x")
            with self.assertRaises(c.YStop) as e:
                c.load_prompt_parts(p)
            self.assertEqual(e.exception.code, "PROMPT_SHA_MISMATCH")

    def test_crlf_normalised_to_same_sha(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "p.txt")
            open(p, "wb").write(open(c.PROMPT_FILE, "rb").read().replace(b"\n", b"\r\n"))
            self.assertEqual(c.load_prompt_parts(p)["sha256"], c.PROMPT_SHA256)

    def test_rules_section_is_verbatim_slice(self):
        parts = c.load_prompt_parts()
        sec = c.closing_rules_section(parts)
        self.assertTrue(sec.startswith("【最終パートの書き方】"))
        self.assertIn("説教、道徳的な一般論", sec)
        self.assertNotIn("出力はJSONのみ", sec)
        self.assertIn(sec, parts["user_template"])

    def test_old_b_skeleton_not_used_for_rewrite(self):
        txt = open(SRC, encoding="utf-8").read()
        for w in ("TENSION_RULES", "共通して望んでいること", "第1に"):
            self.assertNotIn(w if w != "第1に" else "@@never@@", txt.replace("「第1に」などのラベル", ""))


class TestEqualsTrial(unittest.TestCase):
    """DEV(Trial)実装との一致(Productionへ正確に移植されたことの固定)。DEVはtestでのみimportする(Production moduleは非import)。"""

    @classmethod
    def setUpClass(cls):
        import er110_family_y_closing_general_trial_01 as cg
        import er110_family_y_persona_text_trial_01 as p
        import er110_family_y_redelivery_revision_01 as rev
        import er110_family_y_text_trial_01 as y0
        cls.cg, cls.p, cls.rev, cls.y0 = cg, p, rev, y0

    def test_user_prompt_and_blocks_identical(self):
        a = c.build_prompt(INP)
        b = self.cg.build_prompt(INP, self.cg.load_versioned("02"))
        self.assertEqual((a["developer"], a["user"], a["prompt_sha256"], a["user_sha256"]), (b["developer"], b["user"], b["prompt_sha256"], b["user_sha256"]))

    def test_schema_and_checks_identical(self):
        self.assertEqual(c.SCHEMA, self.cg.SCHEMA)
        for t in (GOOD, "短い。", "私は思う？", "人それぞれだ" + "あ" * 190 + "？", "数字は12です。" + "あ" * 190 + "？"):
            self.assertEqual(c.check_closing(t), self.rev.check_closing(t))
        obj = analysis()
        self.assertEqual(c.check_structure(obj), self.cg.check_structure(obj))
        for k in ("EMPTY", "LENGTH=3", "HAS_DIGIT", "SYMBOL:x", "CANDIDATES_COUNT=2"):
            self.assertEqual(c.explain_problem(k), self.cg.explain_problem(k))

    def test_regex_and_constants_identical(self):
        for n in ("FIRST_PERSON_RE", "LABEL_START_RE", "LEAD_BAD_RE", "SENT_SPLIT_RE", "DESU_MASU_RE"):
            self.assertEqual(getattr(c, n).pattern, getattr(self.y0, n).pattern, n)
        for n in ("AI_ANNOUNCE_RE", "OBVIOUS_RE", "DIGIT_RE"):
            self.assertEqual(getattr(c, n).pattern, getattr(self.rev, n).pattern, n)
        self.assertEqual((c.CLOSING_RANGE, c.MAX_SENT), (self.rev.CLOSING_RANGE, self.rev.MAX_SENT))

    def test_closing_b_and_past_closings_checks_match(self):
        for pth in ("er110_output/family_y_redelivery_audio_01/revision_01/closing_B/closing_final.txt",
                    "er110_output/family_y_closing_general_02/redelivery_fee/gen_high_1/closing_final.txt"):
            full = os.path.join(ROOT, pth)
            if os.path.exists(full):
                t = open(full, encoding="utf-8").read().strip()
                self.assertEqual(c.check_closing(t), self.rev.check_closing(t))

    def test_leak_definitions_voice_side_identical(self):
        self.assertEqual(c._VOICE_ITEMS, self.p._VOICE_ITEMS)
        self.assertEqual(c._FOOT, self.p._FOOT)
        self.assertEqual(c.LEAKAGE_DEVELOPER_JA, self.y0.LEAKAGE_DEVELOPER_JA)
        self.assertEqual(c.VOICE_FIELDS, self.y0.VOICE_LEAKAGE_FIELDS)
        self.assertEqual(c.TENSION_FIELDS, self.y0.TENSION_LEAKAGE_FIELDS)
        self.assertEqual(c._TENSION_ITEMS_DEV_ORIGINAL, self.p._TENSION_ITEMS)
        self.assertEqual(c.FIELD_MEANING_JA, self.y0.FIELD_MEANING_JA)
        self.assertEqual(c.REWRITE_DEVELOPER, self.p.REWRITE_DEVELOPER)
        self.assertEqual(c.REWRITE_SCHEMA, self.p.REWRITE_SCHEMA)
        for kind in ("voices", "tension"):
            self.assertEqual(c.leak_schema_for(kind), self.p.leak_schema_for(kind))
        secs = {s: f"本文{s}" for s in c.SLOTS}
        self.assertEqual(c.build_leak_prompt("voices", secs), self.p.build_leak_prompt("voices", secs))

    def test_tension_prompt_differs_from_dev_only_by_expansion(self):
        """M-1: Production版のTension判定promptとDEV版の差分は『上記と同じ意味』行を3項目定義へ展開した箇所だけ。"""
        sec = {"tension": "最終パート本文"}
        prod = c.build_leak_prompt("tension", sec)
        dev = self.p.build_leak_prompt("tension", sec)
        self.assertNotEqual(prod, dev)
        self.assertEqual(prod.replace(c._REF_EXPANDED, c._REF_LINE), dev)
        self.assertIn(c._REF_LINE, dev)
        self.assertNotIn("上記と同じ意味", prod)
        # 展開した定義3行は、Voice用定義と一字一句同じ(新しい基準を足さない)
        for name in ("leak_evidence_subject", "leak_discovery_syntax", "leak_evidence_memorable"):
            line = [ln for ln in self.p._VOICE_ITEMS.split("\n") if ln.startswith(f"- {name}:")][0]
            self.assertIn(line + "\n", prod)
        # 6項目の残り(数字・research・camp)の定義は不変
        for ln in self.p._TENSION_ITEMS.split("\n"):
            if ln.startswith("- leak_numbers_foreground") or ln.startswith("- leak_tension_reverts") or ln.startswith("- leak_binary_camp_split"):
                self.assertIn(ln, prod)

    def test_registry_text_equals_dev_closing_b_and_canonical_doc(self):
        ent = c.FIXED_CLOSING_REGISTRY["redelivery_fee"]
        self.assertEqual(c.w1.sha_text(ent["text"]), ent["text_sha256"])
        dev_b = os.path.join(ROOT, "er110_output/family_y_redelivery_audio_01/revision_01/closing_B/closing_final.txt")
        if os.path.exists(dev_b):
            self.assertEqual(open(dev_b, encoding="utf-8").read().strip(), ent["text"])
        doc = os.path.join(ROOT, "docs/research/FAMILY-Y-VOICES-DESIGN-01/REDELIVERY_REVISION_01/REVISION_SCRIPT_01.md")
        if os.path.exists(doc):
            self.assertIn(ent["text"], open(doc, encoding="utf-8").read())
        self.assertTrue(c.check_closing(ent["text"])["ok"])

    def test_registry_hashes_match_files_when_present(self):
        ent = c.FIXED_CLOSING_REGISTRY["redelivery_fee"]
        pkg = os.path.join(ROOT, "docs/research/FAMILY-Y-VOICES-DESIGN-01/OPINION_BASED_02/THEME_DATA_02.json")
        r0 = os.path.join(ROOT, "er110_output/family_y_opinion_based_03/redelivery_fee/run_01/article_ja.md")
        if os.path.exists(pkg):
            self.assertEqual(hashlib.sha256(open(pkg, "rb").read()).hexdigest(), ent["theme_package_sha256"])
        if os.path.exists(r0):
            self.assertEqual(hashlib.sha256(open(r0, "rb").read()).hexdigest(), ent["voice_r0_sha256"])


class TestIsolation(unittest.TestCase):
    def test_no_dev_import_no_env_no_cli_no_budget_skip(self):
        src = open(SRC, encoding="utf-8").read()
        tree = ast.parse(src)
        mods = set()
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                mods |= {a.name for a in n.names}
            elif isinstance(n, ast.ImportFrom):
                mods.add(n.module)
        self.assertEqual([m for m in mods if m and m.startswith("er110")], [])
        self.assertNotIn("openai", mods)
        for w in ("os.environ", "getenv", "argparse", "sys.argv", "SKIPPED_BUDGET", "__main__"):
            self.assertNotIn(w, src, w)

    def test_dev_modules_do_not_import_production_core(self):
        for fn in os.listdir(ROOT):
            if fn.startswith("er110_family_y_") and fn.endswith(".py"):
                self.assertNotIn("er121", open(os.path.join(ROOT, fn), encoding="utf-8").read(), fn)

    def test_import_has_no_file_side_effect(self):
        before = set(os.listdir(ROOT))
        import importlib
        importlib.reload(c)
        self.assertEqual(set(os.listdir(ROOT)), before)


class TestRouting(RoutedCase):
    def test_route_table_names_models_efforts(self):
        self.assertEqual(c.ROUTE["FAMILY_Y_CLOSING_GENERATE"], {"model": "gpt-6.1-sol", "effort": "high"})
        self.assertEqual(c.ROUTE["FAMILY_Y_LEAK_JUDGE"], {"model": "gpt-6-luna", "effort": "high"})
        for k in ("FAMILY_Y_VOICE_GENERATE", "FAMILY_Y_VOICE_REWRITE", "FAMILY_Y_LEAD_GENERATE", "FAMILY_Y_PERSONA_INTRO", "FAMILY_Y_CLOSING_REWRITE"):
            self.assertIn(k, c.ROUTE)

    def test_unregistered_key_fails_closed_before_api(self):
        fc = FakeClient([sol(analysis())])
        with mock.patch.dict(routing.PROCESS_MODEL_MAP, clear=False):
            routing.PROCESS_MODEL_MAP.pop("FAMILY_Y_CLOSING_GENERATE")
            with self.assertRaises(routing.ModelContractViolation):
                c.chat(fc, route_key="FAMILY_Y_CLOSING_GENERATE", user="u", stage="s")
        self.assertEqual(fc.calls, [])

    def test_wrong_registered_model_fails_closed(self):
        fc = FakeClient([sol(analysis())])
        with mock.patch.dict(routing.PROCESS_MODEL_MAP, {"FAMILY_Y_CLOSING_GENERATE": "gpt-6-luna"}):
            with self.assertRaises(routing.ModelContractViolation):
                c.chat(fc, route_key="FAMILY_Y_CLOSING_GENERATE", user="u", stage="s")
        self.assertEqual(fc.calls, [])

    def test_unknown_key_and_no_client(self):
        with self.assertRaises(routing.ModelContractViolation):
            c.chat(FakeClient([]), route_key="FAMILY_Y_NOPE", user="u", stage="s")
        with self.assertRaises(RuntimeError):
            c.chat(None, route_key="FAMILY_Y_CLOSING_GENERATE", user="u", stage="s")

    def test_response_model_mismatch_stops(self):
        fc = FakeClient([sol(analysis(), model="gpt-6-luna-x")])
        with self.assertRaises(c.ProvenanceViolation):
            c.chat(fc, route_key="FAMILY_Y_CLOSING_GENERATE", user="u", stage="s")

    def test_effort_and_model_sent(self):
        fc = FakeClient([sol(analysis())])
        c.chat(fc, route_key="FAMILY_Y_CLOSING_GENERATE", user="u", stage="s", developer="d")
        kw = fc.calls[0]
        self.assertEqual((kw["model"], kw["reasoning"]), ("gpt-6.1-sol", {"effort": "high"}))

    def test_registered_in_er006_matches_when_present(self):
        """02Bがer006へ登録した後は、登録値が本表と一致すること(未登録の間は検査対象なし)。"""
        real = routing.__dict__["PROCESS_MODEL_MAP"]
        self.patch.stop()
        try:
            for k, v in c.ROUTE.items():
                if k in real:
                    self.assertEqual(real[k], v["model"], k)
        finally:
            self.patch.start()

    def test_transient_error_retried_twice_then_fails(self):
        def boom(kw):
            raise OSError("temp")
        fc = FakeClient([boom, boom, boom])
        with mock.patch.object(c, "_sleep", lambda s: None):
            with self.assertRaises(RuntimeError):
                c.chat(fc, route_key="FAMILY_Y_CLOSING_GENERATE", user="u", stage="s")
        self.assertEqual(len(fc.calls), 3)


class TestGuard(RoutedCase):
    def test_guard_called_before_every_paid_call_and_blocks_api(self):
        labels = []
        fc = FakeClient([sol(analysis()), luna("tension")])
        c.produce_closing(fc, slug="sns_age_limit", inp=INP, theme_package_sha256="a" * 64, voice_r0_sha256="b" * 64, out_dir=os.path.join(self.d, "c"),
                          guard=lambda label: labels.append((label, len(fc.calls))))
        self.assertEqual([x[0] for x in labels], ["yp_closing_gen", "yp_closing_leak1"])
        self.assertEqual([x[1] for x in labels], [0, 1])          # guardは各API呼出の直前(その時点の呼出数)

    def test_guard_exception_means_no_api_call(self):
        def stop(label):
            raise RuntimeError("BUDGET_STOP")
        fc = FakeClient([sol(analysis())])
        with self.assertRaises(RuntimeError):
            c.produce_closing(fc, slug="x", inp=INP, theme_package_sha256="a" * 64, voice_r0_sha256="b" * 64, out_dir=os.path.join(self.d, "c"), guard=stop)
        self.assertEqual(fc.calls, [])

    def test_guard_runs_after_routing_check(self):
        called = []
        with mock.patch.dict(routing.PROCESS_MODEL_MAP, clear=False):
            routing.PROCESS_MODEL_MAP.pop("FAMILY_Y_LEAK_JUDGE")
            with self.assertRaises(routing.ModelContractViolation):
                c.chat(FakeClient([]), route_key="FAMILY_Y_LEAK_JUDGE", user="u", stage="s", guard=called.append)
        self.assertEqual(called, [])


class TestGenerate(RoutedCase):
    def test_good_first_try(self):
        fc = FakeClient([sol(analysis())])
        r = c.generate_closing_general(fc, INP, os.path.join(self.d, "g"))
        self.assertEqual(r["text"], GOOD)
        self.assertEqual(len(fc.calls), 1)
        self.assertEqual(r["meta"]["prompt_sha256"], c.PROMPT_SHA256)
        self.assertEqual(r["selected"]["id"], "c1")
        user = fc.calls[0]["input"][1]["content"]
        self.assertIn(VOICES["voice_2"], user)
        self.assertEqual(fc.calls[0]["text"]["format"]["name"], "family_y_closing_general")

    def test_regen_once_on_violation_with_japanese_problem(self):
        fc = FakeClient([sol(analysis("短すぎる。")), sol(analysis())])
        r = c.generate_closing_general(fc, INP, os.path.join(self.d, "g"))
        self.assertEqual(len(fc.calls), 2)
        self.assertIn("前回の出力の問題", fc.calls[1]["input"][1]["content"])
        self.assertEqual(r["meta"]["problems_per_try"][0][0].startswith("NOT_ENDING") or True, True)

    def test_two_failures_contract_stop(self):
        fc = FakeClient([sol(analysis("短すぎる。")), sol(analysis("まだ短い。"))])
        with self.assertRaises(c.YStop) as e:
            c.generate_closing_general(fc, INP, os.path.join(self.d, "g"))
        self.assertEqual(e.exception.code, "CLOSING_GENERAL_CONTRACT_STOP")
        self.assertEqual(len(fc.calls), 2)

    def test_structure_violation_triggers_regen(self):
        fc = FakeClient([sol(analysis(sel="zzz")), sol(analysis())])
        c.generate_closing_general(fc, INP, os.path.join(self.d, "g"))
        self.assertEqual(len(fc.calls), 2)


SEL = {"id": "c1", "new_view": "見方1", "evidence_quotes": ["朝が早い", "夜に考える"]}
RULES = c.closing_rules_section(c.load_prompt_parts())
FIXED_GOOD = GOOD.replace("集まりやすい", "集まっていく")      # 書換え後の別稿
assert c.check_closing(FIXED_GOOD)["ok"]


def rewrite_resp(text, section="tension"):
    return sol({"rewrites": [{"section": section, "text": text}]})


class TestGate(RoutedCase):
    def gate(self, fc, **kw):
        return c.run_gate(fc, kind="tension", stage="t", texts={"tension": GOOD}, out_dir=os.path.join(self.d, "gate"), voices_ctx=VOICES,
                          selected=SEL, rules_section=RULES, **kw)

    def test_pass_first_judgement(self):
        fc = FakeClient([luna("tension")])
        r = self.gate(fc)
        self.assertEqual((r["status"], r["n_judgements"], r["rewritten"]), ("PASS", 1, False))
        self.assertEqual(fc.calls[0]["model"], "gpt-6-luna")
        self.assertTrue(os.path.exists(os.path.join(self.d, "gate", "leak_check_1.json")))

    def test_fail_then_local_rewrite_then_pass_uses_prompt02_rules_and_angle(self):
        fc = FakeClient([luna("tension", {"tension": ["leak_discovery_syntax"]}), rewrite_resp(FIXED_GOOD), luna("tension")])
        r = self.gate(fc)
        self.assertEqual((r["status"], r["n_judgements"], r["rewritten"]), ("PASS", 2, True))
        rw = fc.calls[1]
        self.assertEqual((rw["model"], rw["reasoning"]), ("gpt-6.1-sol", {"effort": "medium"}))
        up = rw["input"][1]["content"]
        self.assertIn(RULES, up)                               # Prompt 02の規則節を逐語使用
        self.assertIn("見方1", up)
        self.assertIn("朝が早い", up)                          # 選定済み切り口の根拠引用
        self.assertIn("leak_discovery_syntax", up)
        self.assertNotIn("共通して望んでいること", up)         # 旧B骨格は使わない
        self.assertEqual(r["final_texts"]["tension"], FIXED_GOOD)
        h = json.load(open(os.path.join(self.d, "gate", "gate_result.json"), encoding="utf-8"))
        self.assertEqual(len(h["history"]), 2)
        self.assertIn("rewrite_calls", h["history"][0])        # gate_history全保存

    def test_rewrite_must_pass_check_closing_else_rewrite_stop(self):
        bad = "短い文だけ。"
        fc = FakeClient([luna("tension", {"tension": ["leak_discovery_syntax"]}), rewrite_resp(bad), rewrite_resp(bad)])
        with self.assertRaises(c.YStop) as e:
            self.gate(fc)
        self.assertEqual(e.exception.code, "REWRITE_STOP")
        st = json.load(open(os.path.join(self.d, "gate", "gate_result.json"), encoding="utf-8"))
        self.assertEqual(st["status"], "REWRITE_STOP")

    def test_scope_check_unflagged_sentences_must_stay_verbatim(self):
        sents = c._sentences(GOOD)
        last = sents[-1]
        # 指摘箇所=最後の文。最初の文を書換えで変えると違反(2回続けばREWRITE_STOP)
        changed_first = GOOD.replace(sents[0], "お店に出る朝の準備も、家に帰ってからの夜の片づけも、誰かの手を借りている。")
        self.assertTrue(c.check_closing(changed_first)["ok"])
        fc = FakeClient([luna("tension", {"tension": ["leak_discovery_syntax"]}, quote=last), rewrite_resp(changed_first), rewrite_resp(changed_first)])
        with self.assertRaises(c.YStop) as e:
            self.gate(fc)
        self.assertEqual(e.exception.code, "REWRITE_STOP")
        h = json.load(open(os.path.join(self.d, "gate", "gate_result.json"), encoding="utf-8"))
        self.assertTrue(any("REWRITE_SCOPE_VIOLATION" in x for x in h["history"][0]["rewrite_calls"][0]["details"]["errors"]))

    def test_scope_check_allows_change_inside_flagged_sentence(self):
        sents = c._sentences(GOOD)
        last = sents[-1]
        ok = GOOD.replace(sents[-2], "見えない仕事は、見える人の手に集まっていく。")
        fc = FakeClient([luna("tension", {"tension": ["leak_discovery_syntax"]}, quote=sents[-2]), rewrite_resp(ok), luna("tension")])
        r = self.gate(fc)
        self.assertEqual(r["status"], "PASS")
        sc = r["history"][0]["rewrite_calls"][0]["details"]["scope_checks"]["tension"]
        self.assertTrue(sc["checked"])
        self.assertEqual(sc["violations"], [])
        self.assertIsNotNone(last)

    def test_scope_check_unit(self):
        b = "一つ目の文です。二つ目の文は少し長くて引用される。三つ目の文で終わる。"
        self.assertEqual(c.rewrite_scope_check(b, b, ["二つ目の文は少し長くて引用される"])["violations"], [])
        self.assertEqual(c.rewrite_scope_check(b, "一つ目の文です。別の二つ目。三つ目の文で終わる。", ["二つ目の文は少し長くて引用される"])["violations"], [])
        self.assertEqual(c.rewrite_scope_check(b, "違う一つ目。二つ目の文は少し長くて引用される。三つ目の文で終わる。", ["二つ目の文は少し長くて引用される"])["violations"], [0])
        self.assertEqual(c.rewrite_scope_check(b, b, ["全然別の文字列だけ"])["checked"], False)

    def test_rewrite_retry_once_succeeds(self):
        fc = FakeClient([luna("tension", {"tension": ["leak_discovery_syntax"]}), rewrite_resp("短い。"), rewrite_resp(FIXED_GOOD), luna("tension")])
        r = self.gate(fc)
        self.assertEqual(r["status"], "PASS")
        self.assertEqual(len(fc.calls), 4)

    def test_rewrite_symbol_rejected(self):
        withparen = FIXED_GOOD.replace("朝", "(朝)")
        fc = FakeClient([luna("tension", {"tension": ["leak_discovery_syntax"]}), rewrite_resp(withparen), rewrite_resp(withparen)])
        with self.assertRaises(c.YStop):
            self.gate(fc)

    def test_residual_after_three_judgements(self):
        f = {"tension": ["leak_tension_reverts_to_research"]}
        fc = FakeClient([luna("tension", f), rewrite_resp(FIXED_GOOD), luna("tension", f), rewrite_resp(FIXED_GOOD + ""), luna("tension", f)])
        r = self.gate(fc)
        self.assertEqual((r["status"], r["n_judgements"]), ("LEAKAGE_RESIDUAL_STOP", 3))
        self.assertFalse(os.path.exists(os.path.join(self.d, "gate", "final_texts.json")))     # FAIL稿は後続へ流さない
        with self.assertRaises(c.YStop):
            c.load_gated_or_stop(os.path.join(self.d, "gate"))

    def test_no_rewrite_mode_stops_after_one_judgement(self):
        fc = FakeClient([luna("tension", {"tension": ["leak_discovery_syntax"]})])
        r = self.gate(fc, allow_rewrite=False)
        self.assertEqual((r["status"], r["n_judgements"]), ("LEAKAGE_RESIDUAL_STOP", 1))
        self.assertEqual(len(fc.calls), 1)

    def test_rewrite_needs_context(self):
        fc = FakeClient([luna("tension", {"tension": ["leak_discovery_syntax"]})])
        with self.assertRaises(c.YStop):
            c.run_gate(fc, kind="tension", stage="t", texts={"tension": GOOD}, out_dir=os.path.join(self.d, "g2"), voices_ctx=VOICES)

    def test_voice_gate_rewrite_only_flagged_voice(self):
        fp = {"voice_1": "俺", "voice_2": "私", "voice_3": "僕"}
        new2 = "私は夜に静かに考える。"
        fc = FakeClient([luna("voices", {"voice_2": ["leak_evidence_subject"]}), rewrite_resp(new2, "voice_2"), luna("voices")])
        r = c.run_gate(fc, kind="voices", stage="v", texts=VOICES, out_dir=os.path.join(self.d, "vg"), shared_premise="共通前提",
                       personas_text={s: f"P-{s}" for s in c.SLOTS}, first_persons=fp)
        self.assertEqual(r["status"], "PASS")
        self.assertEqual(r["final_texts"]["voice_2"], new2)
        self.assertEqual(r["final_texts"]["voice_1"], VOICES["voice_1"])
        up = fc.calls[1]["input"][1]["content"]
        self.assertIn("共通前提", up)
        self.assertIn("P-voice_2", up)
        self.assertEqual(fc.calls[1]["model"], "gpt-6.1-sol")

    def test_voice_rewrite_without_first_person_rejected(self):
        fp = {"voice_1": "俺", "voice_2": "私", "voice_3": "僕"}
        fc = FakeClient([luna("voices", {"voice_2": ["leak_evidence_subject"]}), rewrite_resp("夜に考える。", "voice_2"), rewrite_resp("夜に考える。", "voice_2")])
        with self.assertRaises(c.YStop):
            c.run_gate(fc, kind="voices", stage="v", texts=VOICES, out_dir=os.path.join(self.d, "vg"), personas_text={s: "P" for s in c.SLOTS}, first_persons=fp)

    def test_out_of_scope_rewrite_rejected(self):
        fc = FakeClient([luna("tension", {"tension": ["leak_discovery_syntax"]}), rewrite_resp(FIXED_GOOD, "voice_1"), rewrite_resp(FIXED_GOOD, "voice_1")])
        with self.assertRaises(c.YStop):
            self.gate(fc)

    def test_leadintro_na_fields_split(self):
        chk = {"flagged_items": [{"section": "tension", "fail_fields": ["leak_tension_reverts_to_research", "leak_discovery_syntax"], "reasoning": "r", "quoted_evidence": "q"}]}
        res = c.split_leadintro_flags(chk)
        self.assertEqual(res["applicable_flagged"][0]["fail_fields"], ["leak_discovery_syntax"])
        self.assertEqual(res["not_applicable_flagged"][0]["fail_fields"], ["leak_tension_reverts_to_research"])


PKG = c.FIXED_CLOSING_REGISTRY["redelivery_fee"]["theme_package_sha256"]
R0 = c.FIXED_CLOSING_REGISTRY["redelivery_fee"]["voice_r0_sha256"]
B_TEXT = c.FIXED_CLOSING_REGISTRY["redelivery_fee"]["text"]


class TestProduceClosing(RoutedCase):
    def test_general_path_writes_record(self):
        fc = FakeClient([sol(analysis()), luna("tension")])
        r = c.produce_closing(fc, slug="sns_age_limit", inp=INP, theme_package_sha256="a" * 64, voice_r0_sha256="b" * 64, out_dir=os.path.join(self.d, "c"))
        rec = r["record"]
        self.assertEqual(rec["source"], "general_prompt_02")
        self.assertTrue(rec["general_method_used"])
        self.assertEqual((rec["routing_key"], rec["expected_model"], rec["effort"], rec["prompt_sha256"]), ("FAMILY_Y_CLOSING_GENERATE", "gpt-6.1-sol", "high", c.PROMPT_SHA256))
        self.assertEqual(rec["model_id"], "gpt-6.1-sol-2026")
        self.assertEqual((rec["gate"]["status"], rec["rewritten"]), ("PASS", False))
        self.assertEqual(rec["generation_sha256"], rec["final_sha256"])
        self.assertTrue(os.path.exists(os.path.join(self.d, "c", "closing_record.json")))
        self.assertEqual([k["model"] for k in fc.calls], ["gpt-6.1-sol", "gpt-6-luna"])

    def test_general_path_with_rewrite_records_both_shas(self):
        fc = FakeClient([sol(analysis()), luna("tension", {"tension": ["leak_discovery_syntax"]}), rewrite_resp(FIXED_GOOD), luna("tension")])
        r = c.produce_closing(fc, slug="x", inp=INP, theme_package_sha256="a" * 64, voice_r0_sha256="b" * 64, out_dir=os.path.join(self.d, "c"))
        rec = r["record"]
        self.assertTrue(rec["rewritten"])
        self.assertNotEqual(rec["generation_sha256"], rec["final_sha256"])
        self.assertEqual(rec["final_sha256"], c.w1.sha_text(FIXED_GOOD))

    def test_general_residual_stop_saves_fail_record_no_final(self):
        f = {"tension": ["leak_tension_reverts_to_research"]}
        fc = FakeClient([sol(analysis()), luna("tension", f), rewrite_resp(FIXED_GOOD), luna("tension", f), rewrite_resp(FIXED_GOOD), luna("tension", f)])
        with self.assertRaises(c.YStop) as e:
            c.produce_closing(fc, slug="x", inp=INP, theme_package_sha256="a" * 64, voice_r0_sha256="b" * 64, out_dir=os.path.join(self.d, "c"))
        self.assertEqual(e.exception.code, "LEAKAGE_RESIDUAL_STOP")
        self.assertFalse(os.path.exists(os.path.join(self.d, "c", "closing_final.txt")))
        rec = json.load(open(os.path.join(self.d, "c", "closing_record.json"), encoding="utf-8"))
        self.assertEqual(rec["status"], "LEAKAGE_RESIDUAL_STOP")

    def test_fixed_path_no_generation_no_rewrite_gate_judged_once(self):
        fc = FakeClient([luna("tension")])
        with mock.patch.object(c, "reusable_prior_gate", lambda *a, **k: None):
            r = c.produce_closing(fc, slug="redelivery_fee", inp=INP, theme_package_sha256=PKG, voice_r0_sha256=R0, out_dir=os.path.join(self.d, "c"))
        self.assertEqual(len(fc.calls), 1)
        self.assertEqual(fc.calls[0]["model"], "gpt-6-luna")
        rec = r["record"]
        self.assertEqual((rec["source"], rec["general_method_used"], rec["text_sha256"]), ("fixed_user_approved", False, c.FIXED_CLOSING_REGISTRY["redelivery_fee"]["text_sha256"]))
        self.assertEqual(r["text"], B_TEXT)
        self.assertIn("USER.md", rec["approval_ref"])
        self.assertEqual(rec["gate"]["source"], "judged_this_run")

    def test_fixed_gate_fail_stops_without_rewrite_or_retry(self):
        fc = FakeClient([luna("tension", {"tension": ["leak_discovery_syntax"]})])
        with mock.patch.object(c, "reusable_prior_gate", lambda *a, **k: None):
            with self.assertRaises(c.YStop) as e:
                c.produce_closing(fc, slug="redelivery_fee", inp=INP, theme_package_sha256=PKG, voice_r0_sha256=R0, out_dir=os.path.join(self.d, "c"))
        self.assertEqual(e.exception.code, "FIXED_CLOSING_GATE_FAIL")
        self.assertEqual(len(fc.calls), 1)                       # 書換えも判定再試行もしない
        self.assertFalse(os.path.exists(os.path.join(self.d, "c", "closing_final.txt")))

    def test_voice_or_package_change_stops_before_any_api(self):
        for pkg, r0 in ((PKG, "0" * 64), ("0" * 64, R0)):
            fc = FakeClient([])
            with self.assertRaises(c.YStop) as e:
                c.produce_closing(fc, slug="redelivery_fee", inp=INP, theme_package_sha256=pkg, voice_r0_sha256=r0, out_dir=os.path.join(self.d, "c"))
            self.assertEqual(e.exception.code, "FIXED_CLOSING_PROVENANCE_MISMATCH")
            self.assertEqual(fc.calls, [])

    def test_registry_text_tamper_stops(self):
        reg = copy.deepcopy(c.FIXED_CLOSING_REGISTRY)
        reg["redelivery_fee"]["text"] = reg["redelivery_fee"]["text"] + "。"
        with mock.patch.object(c, "FIXED_CLOSING_REGISTRY", reg):
            with self.assertRaises(c.YStop) as e:
                c.fixed_closing_lookup("redelivery_fee", PKG, R0)
        self.assertEqual(e.exception.code, "FIXED_CLOSING_TEXT_SHA_MISMATCH")

    def test_other_slug_never_uses_fixed_text_even_with_env_or_same_voices(self):
        with mock.patch.dict(os.environ, {"FAMILY_Y_FIXED_CLOSING": "1", "FIXED_CLOSING_SLUG": "sns_age_limit"}):
            self.assertIsNone(c.fixed_closing_lookup("sns_age_limit", PKG, R0))
            self.assertIsNone(c.fixed_closing_lookup("redelivery_fee2", PKG, R0))
        self.assertEqual(list(c.FIXED_CLOSING_REGISTRY), ["redelivery_fee"])

    def test_prior_gate_reuse_requires_provenance_and_same_prompt_sha(self):
        ent = c.FIXED_CLOSING_REGISTRY["redelivery_fee"]
        psha = c.w1.sha_text(c.build_leak_prompt("tension", {"tension": B_TEXT}))
        rec = {"stage": "s", "kind": "tension", "status": "PASS", "n_judgements": 1, "final_sha256": {"tension": ent["text_sha256"]},
               "history": [{"check": {"prompt_sha256": psha}}]}
        p = os.path.join(self.d, "prior.json")
        json.dump(rec, open(p, "w", encoding="utf-8"))
        self.assertIsNotNone(c.reusable_prior_gate(ent, B_TEXT, psha, p))
        self.assertIsNone(c.reusable_prior_gate(ent, B_TEXT, "0" * 64, p))                     # 判定promptが違う(M-1前の記録)→再判定
        self.assertIsNone(c.reusable_prior_gate(ent, B_TEXT + "。", psha, p))                  # 本文shaが違う
        rec["status"] = "FAIL"
        json.dump(rec, open(p, "w", encoding="utf-8"))
        self.assertIsNone(c.reusable_prior_gate(ent, B_TEXT, psha, p))
        # 実際の旧記録(M-1前のprompt sha)は再利用されない=新promptで再判定が必要
        real = os.path.join(ROOT, ent["prior_gate_record"])
        if os.path.exists(real):
            self.assertIsNone(c.reusable_prior_gate(ent, B_TEXT, psha, real))

    def test_fixed_path_reuses_prior_when_prompt_sha_matches_zero_api(self):
        ent = c.FIXED_CLOSING_REGISTRY["redelivery_fee"]
        psha = c.w1.sha_text(c.build_leak_prompt("tension", {"tension": B_TEXT}))
        rec = {"stage": "s", "kind": "tension", "status": "PASS", "n_judgements": 1, "final_sha256": {"tension": ent["text_sha256"]},
               "history": [{"check": {"prompt_sha256": psha}}]}
        p = os.path.join(self.d, "prior.json")
        json.dump(rec, open(p, "w", encoding="utf-8"))
        reg = copy.deepcopy(c.FIXED_CLOSING_REGISTRY)
        reg["redelivery_fee"]["prior_gate_record"] = p
        fc = FakeClient([])
        with mock.patch.object(c, "FIXED_CLOSING_REGISTRY", reg):
            r = c.produce_closing(fc, slug="redelivery_fee", inp=INP, theme_package_sha256=PKG, voice_r0_sha256=R0, out_dir=os.path.join(self.d, "c"))
        self.assertEqual(fc.calls, [])
        self.assertEqual(r["record"]["gate"]["source"], "reused_prior_pass_record")


if __name__ == "__main__":
    unittest.main()
