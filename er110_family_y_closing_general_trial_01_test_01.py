# -*- coding: utf-8 -*-
"""er110_family_y_closing_general_trial_01 offline test(API 0)。--paid付きの実run入口を実APIで呼ぶtestは書かない(偽clientのみ)。"""
from __future__ import annotations

import argparse
import glob
import json
import os
import tempfile
import types
import unittest

import er110_family_y_closing_general_trial_01 as g

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "er110_family_y_closing_general_trial_01.py")
# 記事固有語(両テーマの題材語+委任_28の切り口語)。Prompt本文・developer・schemaに含めない
TOPIC_WORDS = ["宅配", "再配達", "不在", "ロッカー", "ドライバー", "配達", "置き配", "営業所", "送料", "SNS", "ＳＮＳ", "年齢", "子ども", "子供", "動画", "禁止",
               "有料", "料金", "高校生", "中学生", "保護者", "アプリ", "スマホ", "ネット", "悪者", "歩み寄り", "切り口A", "案A", "案B", "案C"]


class TestPrompt(unittest.TestCase):
    def setUp(self):
        self.parts = g.load_prompt_parts()

    def test_sha_pinned(self):
        g.check_prompt_sha(self.parts)

    def test_sha_mismatch_detected(self):
        bad = dict(self.parts, sha256="0" * 64)
        with self.assertRaises(RuntimeError):
            g.check_prompt_sha(bad)

    def test_no_topic_words_in_prompt_developer_schema(self):
        blob = self.parts["developer"] + self.parts["user_template"] + json.dumps(g.SCHEMA, ensure_ascii=False)
        self.assertEqual([w for w in TOPIC_WORDS if w in blob], [])

    def test_no_fixed_angle_categories_in_prompt(self):
        """案A/B/C相当の固定分類(型の選択式)・抽象化した例示をPromptに持たない。"""
        blob = self.parts["user_template"]
        for w in ("パターン", "次のいずれか", "3つの型", "型から選", "問い直す", "変えられる", "変えられない", "歩み寄"):
            self.assertNotIn(w, blob)

    def test_same_prompt_across_themes_only_input_differs(self):
        base = None
        for t in g.THEMES:
            inp = g.load_input(t)
            pr = g.build_prompt(inp, self.parts)
            u = pr["user"]
            for blk in g.render_blocks(inp).values():
                u = u.replace(blk, "@@BLOCK@@")
            self.assertNotIn("@@THEME", u)
            if base is None:
                base = u
            self.assertEqual(base, u)            # 入力ブロック以外は完全に同一
            self.assertEqual(pr["developer"], self.parts["developer"])

    def test_input_isolation_no_existing_closing_or_angle(self):
        """入力に既存Closing(案A/B/C)・切り口データ・Gate結果を入れない。"""
        import er110_family_y_redelivery_revision_01 as rv
        shingles = set()
        for aid in ("A", "B", "C"):
            pth = f"{rv.REV}/closing_{aid}/closing_final.txt"
            if os.path.exists(pth):
                t = open(pth, encoding="utf-8").read().strip()
                shingles |= {t[i:i + 14] for i in range(0, len(t) - 14, 3)}
        self.assertTrue(shingles)
        for t in g.THEMES:
            u = g.build_prompt(g.load_input(t), self.parts)["user"]
            self.assertEqual([s for s in shingles if s in u], [])
            for w in ("ANGLES", "切り口の名前", "closing_A", "gate_result"):
                self.assertNotIn(w, u)
        inp = g.load_input("redelivery_fee")
        self.assertEqual(set(inp.keys()), {"question", "premise", "distinctions", "personas", "voices"})
        self.assertEqual(set(inp["personas"][0].keys()), {"role", "sketch", "stake"})

    def test_voices_are_r0_bytes(self):
        import er110_family_y_redelivery_audio_01 as rr
        r0 = rr.load_r0()
        inp = g.load_input("redelivery_fee")
        for s in g.SLOTS:
            self.assertEqual(inp["voices"][s], r0[s].strip())

    def test_sns_voices_have_gate_pass_input(self):
        inp = g.load_input("sns_age_limit")
        self.assertEqual(len(inp["voices"]), 3)
        self.assertTrue(all(len(v) > 150 for v in inp["voices"].values()))


class TestPromptRevision02(unittest.TestCase):
    """委任_30: Opusレビュー反映(M1〜M4, R1〜R5, O1)がPromptに入っていること、旧表現が残っていないこと。"""

    def setUp(self):
        self.u = g.load_prompt_parts()["user_template"]

    def test_required_present(self):
        for s in ("人物像の欄は人物を理解するための参考", "「人物1」などの番号や順番で呼ばない", "一人でも当てはまらない面があるなら、全員にまとめない",
                  "中心にしないとされている話題を、見方の中心にしません", "並べた順番は選び方に関係しません", "多くの人が思いつきそうな見方は選ばない",
                  "最後の問いは1つにする", "唯一の正しい見方として言い切らない", "哲学的な一般化", "selection_reason には",
                  "evidence_quotes で裏づけられる範囲", "もとにした観察か、焦点を当てる語りの箇所が違う", "算用数字を使わない"):
            self.assertIn(s, self.u)

    def test_old_expressions_removed(self):
        for s in ("最初に思いついた候補を、そのまま選ばないでください", "互いに言い換えにならないように", "漢数字", "いつ、どこで、誰と、何をしたとき"):
            self.assertNotIn(s, self.u)

    def test_old_prompt_kept_and_differs(self):
        old = os.path.join(ROOT, "docs/research/FAMILY-Y-VOICES-DESIGN-01/CLOSING_GENERAL_01/prompt_closing_general_00.txt")
        self.assertTrue(os.path.exists(old))
        self.assertNotEqual(g.load_prompt_parts(old)["sha256"], g.PROMPT_SHA256)

    def test_explain_problem_japanese(self):
        for c in ("HAS_DIGIT", "NOT_ENDING_WITH_QUESTION", "LENGTH=300", "SENTENCE_TOO_LONG", "DESU_MASU", "SYMBOL:x", "UNKNOWN_X"):
            e = g.explain_problem(c)
            self.assertTrue(any("぀" <= ch <= "ヿ" for ch in e), c)
        self.assertNotIn("HAS_DIGIT", g.explain_problem("HAS_DIGIT"))

    def test_regen_feedback_uses_japanese(self):
        users = []

        def fake_chat(client, **kw):
            users.append(kw["user"])
            return FakeResp(fake_obj("短すぎる。" if len(users) == 1 else GOOD))
        with tempfile.TemporaryDirectory() as d:
            g.generate_one(None, theme="redelivery_fee", gen_idx=1, inp=g.load_input("redelivery_fee"), theme_cap=40.0, out_dir=os.path.join(d, "t", "gen_1"),
                           chat=fake_chat, spent_fn=lambda _d: 0.0, leak=lambda *a, **k: {"any_flagged": False, "flagged_items": []})
        self.assertEqual(len(users), 2)
        self.assertIn("約190〜230字", users[1])
        self.assertNotIn("LENGTH=", users[1])


class TestIsolation(unittest.TestCase):
    def test_no_production_reference(self):
        bad = []
        for f in glob.glob(os.path.join(ROOT, "*.py")):
            b = os.path.basename(f)
            if b.startswith("er110_family_y_"):
                continue
            try:
                t = open(f, encoding="utf-8", errors="ignore").read()
            except OSError:
                continue
            if "er110_family_y_closing_general" in t:
                bad.append(b)
        self.assertEqual(bad, [])

    def test_no_env_flag(self):
        s = open(SRC, encoding="utf-8").read()
        self.assertNotIn("os.environ", s)
        self.assertNotIn("getenv", s)

    def test_no_paid_flag_raises_without_side_effect(self):
        before = set(glob.glob(os.path.join(ROOT, g.ROOT, "**", "*"), recursive=True))
        with self.assertRaises(RuntimeError):
            g.cmd_gen(argparse.Namespace(paid=False, theme="redelivery_fee", gens=1))
        self.assertEqual(before, set(glob.glob(os.path.join(ROOT, g.ROOT, "**", "*"), recursive=True)))

    def test_paid_without_approval_raises(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(RuntimeError):
                g.require_paid(True, os.path.join(d, "none.json"))

    def test_production_gate_untouched(self):
        s = open(os.path.join(ROOT, "er110_family_y_persona_text_trial_01.py"), encoding="utf-8").read()
        self.assertIn("leak_tension_reverts_to_research: 最終パートの中心が、3人がなぜ違う答えに至るのかの掘り下げになっており", s)
        self.assertNotIn("closing_general", s)


class FakeResp:
    def __init__(self, obj):
        self.output_text = json.dumps(obj, ensure_ascii=False)
        self.id = "fake"
        self.model = "gpt-6.1-sol-fake"
        self.usage = types.SimpleNamespace(input_tokens=1, output_tokens=1)


GOOD = ("朝に届くと言われた荷物を待つ人も、次の家へ急ぐ人も、同じ一軒の玄関を見ている。そのとき玄関の外と中で、何が見えていないのか。"
        "見えない時間が積もると、誰も悪くないのに、少しずつ苦い気持ちになる。待つ側にも急ぐ側にも、言えないまま残る小さな我慢があるはずだ。"
        "あなたが最近、誰かを待たせた場面を一つ思い出すと、そのとき相手には何が見えていなかっただろうか？")


def fake_obj(closing=GOOD):
    q = ["次の家へ向かう"]
    return {"observations": [{"kind": "共通点", "note": "n", "evidence_quotes": q}],
            "candidates": [{"id": f"c{i}", "new_view": "v", "evidence_quotes": q, "deepens": "d", "listener_question": "q", "pitfall": "p"} for i in range(1, 4)],
            "selected_id": "c2", "selection_reason": "r", "closing_ja": closing}


class TestPipelineOffline(unittest.TestCase):
    def _run(self, closings, spent=0.0, cap=40.0):
        calls = {"chat": 0, "leak": 0}
        seq = list(closings)

        def fake_chat(client, **kw):
            calls["chat"] += 1
            return FakeResp(fake_obj(seq.pop(0)))

        def fake_leak(client, kind, sections, **kw):
            calls["leak"] += 1
            return {"any_flagged": False, "flagged_items": [], "kind": kind}
        with tempfile.TemporaryDirectory() as d:
            od = os.path.join(d, "t", "gen_1")
            inp = g.load_input("redelivery_fee")
            try:
                r = g.generate_one(None, theme="redelivery_fee", gen_idx=1, inp=inp, theme_cap=cap, out_dir=od, chat=fake_chat,
                                   spent_fn=lambda _d: spent, leak=fake_leak)
            except Exception as e:  # noqa: BLE001
                return calls, e, None
            return calls, None, r

    def test_good_path_one_chat_one_leak(self):
        calls, err, _ = self._run([GOOD])
        self.assertIsNone(err, err)
        self.assertEqual((calls["chat"], calls["leak"]), (1, 1))

    def test_contract_violation_regens_once_then_stops(self):
        bad = "短すぎる。"
        calls, err, _ = self._run([bad, bad])
        self.assertIsNotNone(err)
        self.assertEqual(calls["chat"], 2)       # 再生成は1回だけ
        self.assertEqual(calls["leak"], 0)       # 契約違反本文はGateへ流さない

    def test_reserve_blocks_before_any_call(self):
        calls, err, _ = self._run([GOOD], spent=39.0, cap=40.0)
        self.assertIsInstance(err, RuntimeError)
        self.assertIn("BUDGET_RESERVE_STOP", str(err))
        self.assertEqual((calls["chat"], calls["leak"]), (0, 0))

    def test_check_structure(self):
        o = fake_obj()
        self.assertEqual(g.check_structure(o), [])
        o["selected_id"] = "zzz"
        self.assertIn("SELECTED_ID_NOT_IN_CANDIDATES", g.check_structure(o))

    def test_grounding_report_records_only(self):
        inp = g.load_input("redelivery_fee")
        o = fake_obj()
        o["candidates"][0]["evidence_quotes"] = ["本文にない一節"]
        r = g.grounding_report(o, inp["voices"])
        self.assertGreaterEqual(r["n_quotes"], 4)
        self.assertIn("本文にない一節", r["missing"])


if __name__ == "__main__":
    unittest.main()
