# -*- coding: utf-8 -*-
"""er121_family_y_text_core_01 の記事全体(委任_02C: produce_article = Voice生成+Voice Gate+Lead+人物紹介+補助Gate+Closing+組立)の offline test(API 0)。
偽clientのみ。ネットワーク遮断harness(socket.connect禁止)で『実APIへの接続試行0』を担保する。
DEV(er110_*)との一致は、Productionが『展開移植のみ』であることの固定(DEVはtestでのみimport。Production moduleはDEVを一切importしない)。"""
from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import shutil
import socket
import tempfile
import types
import unittest
from unittest import mock

import er006_model_routing_contract_01 as routing
import er121_family_y_text_core_01 as c
from er121_family_y_text_core_01_test_01 import GOOD, Resp, analysis, leak_obj

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "er121_family_y_text_core_01.py")
PK_DIR = os.path.join(ROOT, "docs", "research", "FAMILY-Y-PRODUCTION-LAUNCH-01", "theme_packages")
SNS_PKG = os.path.join(PK_DIR, "sns_age_limit_package_01.json")
RED_PKG = os.path.join(ROOT, "docs", "research", "FAMILY-Y-VOICES-DESIGN-01", "OPINION_BASED_02", "THEME_DATA_02.json")
RED_REUSE = os.path.join(PK_DIR, "redelivery_fee_reuse_01.json")
CONNECT_ATTEMPTS = []
_orig_connect = socket.socket.connect


def _blocked_connect(self, *a, **k):
    CONNECT_ATTEMPTS.append(a)
    raise OSError("network blocked by test harness")


def setUpModule():
    socket.socket.connect = _blocked_connect


def tearDownModule():
    socket.socket.connect = _orig_connect


def have(*paths):
    return all(os.path.exists(os.path.join(ROOT, p)) for p in paths)


# ------------------------------------------------------------
# 偽client(スキーマ名・developerで応答を振り分ける。呼出ごとにkwを記録。overridesで個別に差し替え)
# ------------------------------------------------------------
VOICES_OK = {
    "私": "私は小さい子どもと毎日一緒にいるから、画面の中身が気になって仕方ない。静かにしてほしい時は助けられる自分もいて、割り切れない。年齢に合わせた決まりがあれば少し楽になる気がする。",
    "僕": "僕は友達との連絡にいつも使っているから、年齢だけで切られるのは困る。自分で決めたい気持ちはあるけど、本当に危ない時は大人に頼りたい。",
    "わたし": "わたしは中学生の子どもを持つ親として、少しずつ使える範囲を広げたいと考えている。準備のないまま急に触れさせるのが心配だと思う。",
}
LEAD_OK = ("子どものSNSに、年齢の決まりを設けるとしたら、どこまでが守りで、どこからが締めつけなのだろう。便利さと危うさが同じ画面に並ぶ今、"
           "この問いは誰にとっても他人事ではない。ここに、立場も暮らしも違う三人の声を並べてみよう。")
LEAD_OK = LEAD_OK.replace("便利さと危うさが同じ画面に並ぶ今、", "便利さと危うさが同じ画面に並ぶ今の暮らしの中では、")
INTROS_OK = {"voice_1": "最初に話すのは、幼い子どもを見守りながら暮らしている、子育て真っ最中の親だ。",
             "voice_2": "次に話すのは、友達とのやり取りが毎日の中心にある、ごく普通の高校生だ。",
             "voice_3": "最後に話すのは、中学生の子どもを育てながら、使い方を一緒に考えている親だ。"}
SENT_LINE_RE = re.compile(r"^(\d+): (.*)$", re.M)


class Smart:
    def __init__(self, overrides=None, voices=None, lead=LEAD_OK, intros=None, closing=GOOD, tags=None):
        self.calls, self.overrides = [], list(overrides or [])
        self.responses = types.SimpleNamespace(create=self._create)
        self.voices, self.lead, self.intros, self.closing = voices or VOICES_OK, lead, intros or INTROS_OK, closing
        self.tags = tags

    def resp(self, kw, obj):
        text = obj if isinstance(obj, str) else json.dumps(obj, ensure_ascii=False)
        r = Resp({}, model=kw["model"] + "-2026")
        r.output_text = text
        return r

    def schema_name(self, kw):
        return (kw.get("text") or {}).get("format", {}).get("name")

    def _create(self, **kw):
        self.calls.append(kw)
        for i, (pred, fn) in enumerate(self.overrides):
            if pred(kw):
                self.overrides.pop(i)
                return fn(kw) if callable(fn) else fn
        return self.resp(kw, self.default(kw))

    def default(self, kw):
        name = self.schema_name(kw)
        user = kw["input"][-1]["content"]
        dev = kw["input"][0]["content"] if len(kw["input"]) > 1 else ""
        if name is None:
            if "これから三人の声を聞く人に向けて" in dev:
                return self.lead
            m = re.search(r"一人称は「(.+?)」", user)
            return self.voices[m.group(1)]
        if name == "yob_provenance_map":
            sents = SENT_LINE_RE.findall(user)
            exp = re.findall(r"- \[(\w+)\]", user)
            return {"items": [{"idx": int(i), "source_ids": exp[:1], "supplement_kinds": ["なし"], "is_event_claim": False, "note_ja": "n"} for i, _ in sents]}
        if name == "yp_structure_tags":
            ty = self.tags or [("自分の状況・立場の描写から", "主張から具体例へ", "迷いを残して締める"), ("感情・本音の吐露から", "感情から具体例へ", "問いを残して締める"),
                               ("主張・意見の表明から", "経験の時系列", "主張を言い切って締める")]
            return {"voices": [{"voice": s, "opening_type": o, "development_type": d, "closing_type": cl, "evidence_ja": "e"} for s, (o, d, cl) in zip(c.SLOTS, ty)]}
        if name == "family_y_persona_leakage_voices":
            return leak_obj("voices")
        if name == "family_y_persona_leakage_tension":
            return leak_obj("tension")
        if name == "family_y_voice_intros":
            return self.intros
        if name == "family_y_closing_general":
            return analysis(self.closing)
        raise AssertionError(f"想定外のcall: {name} / {dev[:30]}")

    def by(self, model=None, name=None):
        return [k for k in self.calls if (model is None or k["model"] == model) and (name is None or self.schema_name(k) == name)]


def when(**cond):
    def pred(kw):
        name = (kw.get("text") or {}).get("format", {}).get("name")
        if "name" in cond and name != cond["name"]:
            return False
        if "model" in cond and kw["model"] != cond["model"]:
            return False
        if "dev" in cond and cond["dev"] not in (kw["input"][0]["content"] if len(kw["input"]) > 1 else ""):
            return False
        if "user_has" in cond and cond["user_has"] not in kw["input"][-1]["content"]:
            return False
        return True
    return pred


def leak_fail(kind, fails, quote="引用"):
    return lambda kw: Resp(leak_obj(kind, fails, quote), model="gpt-6-luna-2026")


class Routed(unittest.TestCase):
    def setUp(self):
        reg = {k: v["model"] for k, v in {**c.ROUTE, **c.ROUTE_AUX}.items()}
        self.patch = mock.patch.dict(routing.PROCESS_MODEL_MAP, reg)
        self.patch.start()
        self.addCleanup(self.patch.stop)
        self.tmp = tempfile.TemporaryDirectory()
        self.d = self.tmp.name
        self.addCleanup(self.tmp.cleanup)
        n = len(CONNECT_ATTEMPTS)
        self.addCleanup(lambda: self.assertEqual(len(CONNECT_ATTEMPTS), n))

    def run_sns(self, client, **kw):
        return c.produce_article(client, slug="sns_age_limit", theme_package=SNS_PKG, out_dir=os.path.join(self.d, "text"), **kw)

    def rj(self, *p):
        with open(os.path.join(self.d, *p), encoding="utf-8") as f:
            return json.load(f)


# ============================================================
# Prompt / 定義文のsha固定とDEV一致
# ============================================================
class TestPromptFiles(unittest.TestCase):
    def test_sha_pinned_and_files_present(self):
        for k, (fn, sha) in c.ARTICLE_PROMPTS.items():
            raw = open(os.path.join(c.PROMPT_DIR, fn), "rb").read()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), sha, k)
            self.assertEqual(c.load_article_prompt(k)["sha256"], sha)

    def test_literal_sha_values(self):
        self.assertEqual(c.ARTICLE_PROMPTS["voice"][1], "48645f1de5fcf6efd3a9d758a0120aa97b37f656a074c9ea0c31d95c51ffcd5e")
        self.assertEqual(c.ARTICLE_PROMPTS["lead"][1], "76282235c4f089c56318a635c4af1e45001795e7c8b956480bcfacb307edef21")
        self.assertEqual(c.ARTICLE_PROMPTS["intro"][1], "a5da099a2d7b44392f118f61a97f3538933cf2e3354d0024b3bbcf697a12fbe5")   # B+E(FY-SPEAKER-INTRO-BE-PRODUCTION-WIRING-01、2026-10-29。旧787794d6…)

    def test_mismatch_stops_and_crlf_is_normalised(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "x.txt")
            raw = open(os.path.join(c.PROMPT_DIR, c.ARTICLE_PROMPTS["lead"][0]), "rb").read()
            open(p, "wb").write(raw + b"x")
            with self.assertRaises(c.YStop) as e:
                c.load_article_prompt("lead", p)
            self.assertEqual(e.exception.code, "PROMPT_SHA_MISMATCH")
            open(p, "wb").write(raw.replace(b"\n", b"\r\n"))
            self.assertEqual(c.load_article_prompt("lead", p)["sha256"], c.ARTICLE_PROMPTS["lead"][1])

    def test_new_section_has_no_theme_specific_words(self):
        src = open(SRC, encoding="utf-8").read()
        new = src[src.index("# 委任_02C: 記事全体"):]
        for w in ("宅配", "再配達", "ドライバー", "置き配", "ロッカー", "SNS", "年齢", "高校生", "中学生", "不在票", "redelivery", "sns_age"):
            self.assertNotIn(w, new, w)

    def test_prompt_files_carry_no_theme_placeholders_beyond_known(self):
        self.assertEqual(sorted(set(re.findall(r"@@[A-Z_]+@@", c.load_article_prompt("voice")["user_template"]))),
                         ["@@CUE@@", "@@DISTINCTIONS@@", "@@FACT@@", "@@OPENING@@", "@@PREMISE@@", "@@QUESTION@@", "@@SHEET@@"])
        self.assertEqual(sorted(set(re.findall(r"@@[A-Z_]+@@", c.load_article_prompt("lead")["user_template"]))), ["@@PREMISE@@", "@@SCOPE@@"])
        self.assertEqual(sorted(set(re.findall(r"@@[A-Z_]+@@", c.load_article_prompt("intro")["user_template"]))),
                         ["@@CLAIM_WORDS@@", "@@OBJECT_EXAMPLES@@", "@@PERSONS@@", "@@PREMISE@@"])


@unittest.skipUnless(have("docs/research/FAMILY-Y-VOICES-DESIGN-01/OPINION_BASED_02/THEME_DATA_02.json"), "DEV theme data absent")
class TestEqualsDev(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import er110_family_y_opinion_based_01 as ob
        import er110_family_y_opinion_based_02 as ob2
        import er110_family_y_opinion_based_03 as ob3
        import er110_family_y_persona_pipeline_01 as pl
        import er110_family_y_persona_text_trial_01 as p
        import er110_family_y_redelivery_audio_01 as rr
        import er110_family_y_redelivery_revision_01 as rev
        cls.ob, cls.ob2, cls.ob3, cls.pl, cls.p, cls.rr, cls.rev = ob, ob2, ob3, pl, p, rr, rev
        cls.red = c.load_theme_package(RED_PKG)["theme"]
        cls.sns = c.load_theme_package(SNS_PKG)["theme"]
        cls.parts = c.load_article_prompt("voice")

    # ---- Voice ----
    def test_voice_template_and_developer_equal_dev(self):
        self.assertEqual(self.parts["user_template"], self.ob2.VOICE_PROMPT_OB2)
        self.assertEqual(self.parts["developer"], self.p.VOICE_DEVELOPER)
        self.assertEqual(c.OPENING_GUIDE, self.ob2.OPENING_GUIDE_02)

    def test_voice_prompt_equals_dev_redelivery_via_ob3(self):
        theme = self.ob3.load_theme(RED_PKG)
        for slot in c.SLOTS:
            for emph in (False, True):
                with self.ob3.patched_ob_03(10.0, theme):
                    dev = self.ob.build_voice_prompt_ob(theme["world_frame"], slot, emph)
                mine = c.build_voice_prompt(self.red["world_frame"], self.red["sheets"][slot], self.red["who_ja"][slot], self.parts, emph)
                self.assertEqual(mine, dev, (slot, emph))

    def test_voice_prompt_equals_dev_sns_via_ob2_and_ob3(self):
        for slot in c.SLOTS:
            with self.ob2.patched_ob(10.0):
                dev = self.ob.build_voice_prompt_ob(self.ob2.WORLD_FRAME_02, slot, False)
            mine = c.build_voice_prompt(self.sns["world_frame"], self.sns["sheets"][slot], self.sns["who_ja"][slot], self.parts, False)
            self.assertEqual(mine, dev, slot)
        theme3 = self.ob3.load_theme(SNS_PKG)
        for slot in c.SLOTS:
            with self.ob3.patched_ob_03(10.0, theme3):
                dev = self.ob.build_voice_prompt_ob(theme3["world_frame"], slot, True)
            self.assertEqual(c.build_voice_prompt(self.sns["world_frame"], self.sns["sheets"][slot], self.sns["who_ja"][slot], self.parts, True), dev)

    def test_render_persona_equals_dev(self):
        for slot in c.SLOTS:
            self.assertEqual(c.render_persona(self.sns["sheets"][slot], self.sns["who_ja"][slot]), self.ob2.render_persona_ob2(self.ob2.SHEETS_02[slot], self.ob2.WHO_JA_02[slot]))

    def test_voice_checks_and_monitors_equal_dev(self):
        samples = [("私は朝が早い。", "私"), ("", "私"), ("一行目\n二行目私", "私"), ("【見出し】私は", "私"), ("僕は何も言わなかった。", "私"), ("私は3回来た。多くの人が来る！？", "私")]
        for t, fp in samples:
            self.assertEqual(c.check_voice(t, fp), self.pl.check_voice_pl(t, fp))
            self.assertEqual(c.voice_monitors(t, fp), self.pl.voice_monitors_pl(t, fp))

    def test_regexes_equal_dev(self):
        for n in ("NUM_RE", "ROLE_WORD_RE", "INTERVIEW_RE"):
            self.assertEqual(getattr(c, n).pattern, getattr(self.p, n).pattern, n)
        for n in ("EVENT_WORD_RE", "PAST_END_RE", "PAST_EXCLUDE_RE", "HYPO_RE"):
            self.assertEqual(getattr(c, n).pattern, getattr(self.ob, n).pattern, n)
        self.assertEqual(c.SUPP_KINDS, self.ob.SUPP_KINDS)
        self.assertEqual(c.REQUIRED_SHEET_KEYS, tuple(k for k in self.ob3.REQUIRED_SHEET_KEYS))

    def test_mapping_equals_dev(self):
        self.assertEqual(c.SCHEMA_MAP, self.ob.SCHEMA_MAP)
        self.assertEqual(c.MAP_DEVELOPER, self.ob.MAP_DEVELOPER)
        sents = ["私は朝が早い。", "この前、先生に言われた。", "もし来るなら嬉しい。", "知らない話だ。"]
        with self.ob3.patched_ob_03(10.0, self.ob3.load_theme(RED_PKG)):
            for slot in c.SLOTS:
                sh = self.red["sheets"][slot]
                self.assertEqual(c.build_map_prompt(sh, sents), self.ob.build_map_prompt(slot, sents))
                parsed = {"items": [{"idx": 0, "source_ids": [sh["experiences"][0]["id"]], "supplement_kinds": ["なし"], "is_event_claim": False, "note_ja": ""},
                                    {"idx": 1, "source_ids": [], "supplement_kinds": ["なし"], "is_event_claim": True, "note_ja": ""},
                                    {"idx": 2, "source_ids": ["ZZZ"], "supplement_kinds": ["口調・言い回し"], "is_event_claim": False, "note_ja": ""}]}
                mine, dev = c.check_mapping(slot, sh, sents, parsed), self.ob.check_mapping(slot, sents, parsed)
                dev = {**{k: v for k, v in dev.items() if k != "tbs_only_idx"}, "r2plus_only_idx": dev["tbs_only_idx"]}
                self.assertEqual(mine, dev)
                self.assertEqual(c.unmapped_extra(mine), self.ob.unmapped_extra(dev))

    def test_structure_equals_dev(self):
        self.assertEqual(c.SCHEMA_STRUCTURE, self.pl.SCHEMA_STRUCTURE)
        self.assertEqual(c.STRUCTURE_DEVELOPER, self.pl.STRUCTURE_DEVELOPER)
        t = {s: f"本文{s}" for s in c.SLOTS}
        self.assertEqual(c.build_structure_prompt(t), self.pl.build_structure_prompt(t))
        same = {s: {"opening_type": "問いかけから", "development_type": "経験の時系列", "closing_type": "その他"} for s in c.SLOTS}
        diff = copy.deepcopy(same)
        diff["voice_2"]["development_type"] = "主張から具体例へ"
        other = copy.deepcopy(same)
        for s in c.SLOTS:
            other[s]["development_type"] = "その他"
        for tags in (same, diff, other):
            self.assertEqual(c.structure_fire(tags), self.pl.structure_fire(tags))
        self.assertTrue(c.structure_fire(same)["fired"])
        self.assertEqual(c.structure_fire(same)["regenerate_slot"], "voice_2")

    def test_repetition_report_equals_dev(self):
        for t in ("私は朝が早い。朝が早いのは私の習慣だ。でも夜は遅い。", "短い。", "A。B。"):
            self.assertEqual(c.repetition_report(t), self.ob2.repetition_report(t))

    # ---- Lead ----
    def test_lead_template_and_prompt_equal_dev(self):
        parts = c.load_article_prompt("lead")
        self.assertEqual(parts["user_template"], self.rev.LEAD_TMPL)
        self.assertEqual(parts["developer"], self.rr.LEAD_DEVELOPER)
        self.assertEqual(c.build_lead_prompt(self.rr.PREMISE_JA, list(self.rev.SCOPE_LINES), parts), self.rev.build_lead_prompt())
        self.assertEqual((c.LEAD_RANGE, c.INTRO_RANGE), (self.rev.LEAD_RANGE, self.rev.INTRO_RANGE))
        self.assertEqual(c.PREVIEW_RE.pattern, self.rev.PREVIEW_RE.pattern)
        self.assertEqual(c.IOL_RE.pattern, self.rev.IOL_RE.pattern)

    def test_check_lead_equals_dev(self):
        for t in (LEAD_OK, "短い。", "私は思う。三人の声。", "取材した三人です。" + "あ" * 120, "数字は12個。" + "あ" * 120 + "三人", LEAD_OK + "\n二段落目", "AIが組み立てた三人の声。" + "あ" * 120):
            self.assertEqual(c.check_lead(t), self.rev.check_lead(t), t[:12])

    # ---- 人物紹介 ----
    def explicit_checks(self):
        return {"role_patterns": {s: self.rev.INTRO_ROLE_RE[s].pattern for s in c.SLOTS}, "object_words": list(self.rev.INTRO_OBJECT_WORDS),
                "claim_pattern": self.rev.CLAIM_WORDS_RE.pattern, "claim_words_prompt": "「有料」「料金」「賛成」「反対」「払う」「請求」",
                "object_examples_prompt": "宅配ボックス・置き配・ロッカー・営業所・時間指定・不在票"}

    def test_intro_template_and_prompt_equal_dev(self):
        parts = c.load_article_prompt("intro")
        # B+E(2026-10-29): 追加2箇条(一般化原則・E節)と人物ブロックの『話題との関わり』行を除いた残りがDEV(旧委任_28)と一致=旧部分は不変
        parts = dict(parts, user_template="\n".join(ln for ln in parts["user_template"].split("\n") if not ln.startswith(("- 【人物紹介の一般化原則】", "- 【属性がそのまま立場のとき】"))))
        self.assertEqual(parts["developer"], self.rev.INTRO_DEVELOPER)
        self.assertEqual(c.INTRO_SCHEMA, self.rev.INTRO_SCHEMA)
        spec = c.intro_spec(self.red, self.explicit_checks())
        self.assertEqual(parts["user_template"].replace("@@CLAIM_WORDS@@", spec["claim_prompt"]).replace("(@@OBJECT_EXAMPLES@@など)", "(" + spec["object_prompt"] + "など)"),
                         self.rev.INTRO_TMPL)
        if have("er110_output/family_y_opinion_based_03/redelivery_fee/run_01/article_ja.md"):
            r0 = self.rr.load_r0()
            voices = {s: r0[s] for s in c.SLOTS}
            self.assertEqual(re.sub(r"  話題との関わり: .*\n", "", c.build_intro_prompt(self.red, self.rr.PREMISE_JA, voices, parts, spec)), self.rev.build_intro_prompt(self.rev.load_theme_sheets(), voices))

    def test_check_intro_equals_dev_with_explicit_spec(self):
        spec = c.intro_spec(self.red, self.explicit_checks())
        body = "宅配ボックスを使う。置き配も試した。ロッカーまで歩く日もある。それだけの話だ。"
        cases = [("最初に話すのは、日々の配達で家々を回り、荷物を届けている宅配ドライバーだ。", "voice_1"), ("", "voice_1"), ("私が話す。", "voice_2"),
                 ("次は、有料化に賛成の、共働きで家を空けがちな人だ。", "voice_2"), ("最後は、ロッカーでの受け取りなどを選び、再配達にならないよう工夫している人だ。", "voice_3"),
                 ("最後は、置き配やコンビニ受け取りを選ぶ、再配達を避けたい人だ。", "voice_3"), ("宅配ボックスを使う。置き配も試した。ロッカーまで歩く、受け取る人だ。", "voice_3"),
                 ("short", "voice_1"), ("あ" * 80, "voice_2")]
        for t, slot in cases:
            self.assertEqual(c.check_intro(t, slot, body, spec), self.rev.check_intro(t, slot, body), (slot, t[:10]))

    def test_shingle_and_norm_equal_dev(self):
        for t in ("私は「朝」が早い、と思う。", "ABC ｱｲｳ 123"):
            self.assertEqual(c._norm_ja(t), self.rr._norm_ja(t))
            self.assertEqual(c._shingles(t, 3), self.rev._shingles(t, 3))
        srcs = {"a.txt": "朝が早いと思うのは私だけではないはずだと誰もが言うのだった"}
        self.assertEqual(c.shingle_hits_ja("朝が早いと思うのは私だけではないはずだ", srcs, 12), self.rr.shingle_hits_ja("朝が早いと思うのは私だけではないはずだ", srcs, 12))

    # ---- Theme Package ----
    def test_validate_matches_dev_on_both_packages(self):
        for pk in (RED_PKG, SNS_PKG):
            self.assertEqual(c.validate_theme_package(json.load(open(pk, encoding="utf-8"))), [])
            self.ob3.load_theme(pk)                          # DEV検証も通る

    def test_sns_package_is_mechanical_transcription_of_dev_constants(self):
        d = json.load(open(SNS_PKG, encoding="utf-8"))
        self.assertEqual(d["world_frame"], self.ob2.WORLD_FRAME_02)
        self.assertEqual(d["who_ja"], self.ob2.WHO_JA_02)
        want = copy.deepcopy(self.ob2.SHEETS_02)
        for sh in want.values():
            for x in sh["experiences"]:
                x.pop("tbs_only")
        self.assertEqual(d["sheets"], want)
        self.assertEqual(d["restricted_voice_ids"], ["TBS-07"])
        for s in c.SLOTS:
            for x, y in zip(c.load_theme_package(SNS_PKG)["theme"]["sheets"][s]["experiences"], self.ob2.SHEETS_02[s]["experiences"]):
                self.assertEqual(x["r2plus_only"], y["tbs_only"])

    @unittest.skipUnless(have("er110_output/family_y_opinion_based_03/redelivery_fee/run_01/article_ja.md"), "R0 absent")
    def test_closing_input_equals_dev_load_input(self):
        import er110_family_y_closing_general_trial_01 as cg
        dev = cg.load_input("redelivery_fee")
        mine = c.closing_input_from_theme(self.red, dev["voices"])
        self.assertEqual(mine, dev)

    def test_closing_input_sns_equals_dev(self):
        import er110_family_y_closing_general_trial_01 as cg
        if not (have("er110_output/family_y_opinion_based_02/sns_age_limit/run_03/voices_final.json")):
            self.skipTest("SNS voices absent")
        dev = cg.load_input("sns_age_limit")
        self.assertEqual(c.closing_input_from_theme(self.sns, dev["voices"]), dev)


class TestThemePackage(unittest.TestCase):
    def base(self):
        return json.load(open(SNS_PKG, encoding="utf-8"))

    def test_invalid_variants_rejected(self):
        for mut, code in ((lambda d: d["sheets"].pop("voice_3"), "THEME_SLOTS_MISMATCH"), (lambda d: d["sheets"]["voice_1"].pop("arc_ja"), "SHEET_MISSING_KEYS"),
                          (lambda d: d["sheets"]["voice_1"].__setitem__("opening_type", "謎"), "UNKNOWN_OPENING_TYPE"),
                          (lambda d: d["sheets"]["voice_2"].__setitem__("relevant_terms", ["未定義"]), "RELEVANT_TERM_NOT_DEFINED"),
                          (lambda d: d["sheets"]["voice_2"]["experiences"][0].__setitem__("source_ids", []), "EXPERIENCE_FIELDS"),
                          (lambda d: d["world_frame"].pop("title_ja"), "WORLD_FRAME_MISSING"), (lambda d: d.pop("who_ja"), "PACKAGE_MISSING")):
            d = self.base()
            mut(d)
            errs = c.validate_theme_package(d)
            self.assertTrue(any(code in e for e in errs), (code, errs))
            with self.assertRaises(c.YStop) as e:
                c.load_theme_package(d)
            self.assertEqual(e.exception.code, "THEME_PACKAGE_INVALID")

    def test_sha_is_file_bytes_like_registry(self):
        r = c.load_theme_package(RED_PKG)
        self.assertEqual(r["sha256"], c.FIXED_CLOSING_REGISTRY["redelivery_fee"]["theme_package_sha256"])
        self.assertEqual(r["sha_method"], "file_bytes")
        d = json.load(open(RED_PKG, encoding="utf-8"))
        r2 = c.load_theme_package(d)
        self.assertEqual(r2["sha_method"], "canonical_json")
        self.assertNotEqual(r2["sha256"], r["sha256"])                     # dictのみ=案Bは注入されない(fail-closed)
        r3 = c.load_theme_package(d, path=RED_PKG)
        self.assertEqual(r3["sha256"], r["sha256"])
        d["theme_id"] = "other"
        with self.assertRaises(c.YStop):
            c.load_theme_package(d, path=RED_PKG)


# ============================================================
# 生成経路(新規生成: SNS Theme Package)
# ============================================================
class TestGeneratedPath(Routed):
    def test_happy_path_call_counts_models_and_files(self):
        fc = Smart()
        labels = []
        res = self.run_sns(fc, guard=labels.append)
        self.assertEqual(set(res), {"title", "lead", "intros", "voices", "closing", "closing_record", "records"})
        self.assertEqual(res["voices"], {"voice_1": VOICES_OK["私"], "voice_2": VOICES_OK["僕"], "voice_3": VOICES_OK["わたし"]})
        self.assertEqual((res["lead"], res["intros"], res["closing"]), (LEAD_OK, INTROS_OK, GOOD))
        sols, lunas = fc.by("gpt-6.1-sol"), fc.by("gpt-6-luna")
        # sol: Voice3 + Lead1 + Intro1 + Closing生成1 = 6 / luna: 付番3+構造1+Voice Gate1+最終付番3+Lead紹介判定1+Closing判定1 = 10
        self.assertEqual((len(sols), len(lunas), len(fc.calls)), (6, 10, 16))
        self.assertEqual(len(labels), 16)
        self.assertEqual([k["reasoning"]["effort"] for k in sols], ["high"] * 6)
        self.assertEqual({k["reasoning"]["effort"] for k in fc.by("gpt-6-luna", "yob_provenance_map")}, {"medium"})
        self.assertEqual({k["reasoning"]["effort"] for k in fc.by("gpt-6-luna", "family_y_persona_leakage_voices")}, {"high"})
        # 呼出順(guardラベル): 生成→付番→構造→Gate→最終付番→Lead→紹介→補助Gate→Closing
        self.assertEqual(labels[:3], ["yp_voice_voice_1", "yp_voice_voice_2", "yp_voice_voice_3"])
        self.assertEqual(labels[3:6], ["yp_vmap_voice_1_m1", "yp_vmap_voice_2_m1", "yp_vmap_voice_3_m1"])
        self.assertEqual(labels[6:8], ["yp_vstruct1", "yp_voices_gate_leak1"])
        self.assertEqual(labels[-5:], ["yp_lead", "yp_intro", "yp_leadintro_leak", "yp_closing_gen", "yp_closing_leak1"])
        self.assertEqual(labels[8:11], ["yp_vmap_voice_1_final", "yp_vmap_voice_2_final", "yp_vmap_voice_3_final"])
        for f in ("article_record.json", "article_status.json", "article_assembled.md"):
            self.assertTrue(os.path.exists(os.path.join(self.d, "text", f)), f)
        for f in ("voices/voices_final.json", "voices/voices_record.json", "voices/gate_voices/gate_result.json", "voices/gate_voices/leak_check_1.json",
                  "lead_intro/gate/applicable_result.json", "closing/closing_record.json", "closing/closing_final.txt", "closing/gate/gate_result.json"):
            self.assertTrue(os.path.exists(os.path.join(self.d, "text", f)), f)

    def test_article_record_has_model_routing_prompt_sha_and_gate_history(self):
        fc = Smart()
        res = self.run_sns(fc)
        rec = self.rj("text", "article_record.json")
        self.assertEqual((rec["status"], rec["mode"], rec["slug"]), ("FAMILY_Y_PRODUCTION", "generated", "sns_age_limit"))
        v = rec["voices"]
        self.assertEqual((v["routing_key"], v["expected_model"], v["effort"]), ("FAMILY_Y_VOICE_GENERATE", "gpt-6.1-sol", "high"))
        self.assertEqual(v["model_ids"], ["gpt-6.1-sol-2026"])
        self.assertEqual(v["prompt_sha256"], c.ARTICLE_PROMPTS["voice"][1])
        self.assertEqual(v["gate"]["status"], "PASS")
        self.assertEqual(v["final_sha256"], {s: c.w1.sha_text(res["voices"][s]) for s in c.SLOTS})
        self.assertEqual(rec["lead"]["routing_key"], "FAMILY_Y_LEAD_GENERATE")
        self.assertEqual(rec["lead"]["prompt_sha256"], c.ARTICLE_PROMPTS["lead"][1])
        self.assertEqual(rec["intros"]["routing_key"], "FAMILY_Y_PERSONA_INTRO")
        self.assertEqual(rec["leadintro_gate"]["status"], "PASS")
        self.assertEqual(rec["closing"]["source"], "general_prompt_02")
        self.assertEqual(rec["closing"]["prompt_sha256"], c.PROMPT_SHA256)
        self.assertEqual(rec["closing"]["model_id"], "gpt-6.1-sol-2026")
        self.assertEqual(rec["theme_package_sha_method"], "file_bytes")
        self.assertEqual(rec["theme_package_sha256"], hashlib.sha256(open(SNS_PKG, "rb").read()).hexdigest())
        self.assertEqual(rec["module"]["sha256"], hashlib.sha256(open(SRC, "rb").read()).hexdigest())
        self.assertEqual(sorted(rec["part_sha256"]), sorted(["lead", "closing"] + [f"intro_{s}" for s in c.SLOTS] + [f"voice_{s}" for s in c.SLOTS]))
        self.assertEqual(res["closing_record"], rec["closing"])
        self.assertFalse(rec["verbatim"]["n_hits"])

    def test_article_has_five_parts_no_in_one_line_no_ai_notice(self):
        res = self.run_sns(Smart())
        text = c.render_article_text(res["title"], res["lead"], res["intros"], res["voices"], res["closing"])
        self.assertEqual(open(os.path.join(self.d, "text", "article_assembled.md"), encoding="utf-8").read(), text)
        body = text.split("\n\n", 1)[1]
        paras = [p for p in re.split(r"\n\s*\n", body.strip()) if p.strip()]
        self.assertEqual(len(paras), 5)
        for i in (1, 2, 3):
            self.assertEqual(len(paras[i].split("\n")), 2)
        self.assertFalse(c.IOL_RE.search(text))
        self.assertFalse(c.AI_ANNOUNCE_RE.search("\n".join([res["lead"], res["closing"]] + list(res["intros"].values()))))
        self.assertTrue(text.startswith("# 子どものSNS、それぞれの声"))

    def test_voice_prompt_sent_matches_builder_and_uses_voice_route(self):
        fc = Smart()
        self.run_sns(fc)
        th = c.load_theme_package(SNS_PKG)["theme"]
        parts = c.load_article_prompt("voice")
        sent = [k for k in fc.by("gpt-6.1-sol") if k["input"][0]["content"] == parts["developer"]]
        self.assertEqual([k["input"][1]["content"] for k in sent], [c.build_voice_prompt(th["world_frame"], th["sheets"][s], th["who_ja"][s], parts) for s in c.SLOTS])

    def test_unmapped_voice_regenerated_once_and_recorded(self):
        calls = {"n": 0}

        def map_bad(kw):
            calls["n"] += 1
            sents = SENT_LINE_RE.findall(kw["input"][-1]["content"])
            items = [{"idx": int(i), "source_ids": [], "supplement_kinds": ["なし"], "is_event_claim": True, "note_ja": ""} for i, _ in sents]
            return Resp({"items": items}, model="gpt-6-luna-2026")
        fc = Smart(overrides=[(when(name="yob_provenance_map"), map_bad)])
        self.run_sns(fc)
        rec = self.rj("text", "voices", "voices_record.json")
        self.assertEqual(list(rec["unmapped_regen"]), ["voice_1"])                   # 最初の付番(voice_1)だけ不良=1本だけ再生成
        self.assertEqual(rec["unmapped_regen"]["voice_1"]["n_unmapped_after"], 0)
        extra = [k for k in fc.by("gpt-6.1-sol") if "前回の出力の問題" in k["input"][-1]["content"]]
        self.assertEqual(len(extra), 1)
        self.assertEqual(len(fc.calls), 16 + 2)                                       # 再生成1 + 再付番1

    def test_structure_fire_regenerates_one_voice_and_records_tag2(self):
        same = [("問いかけから", "経験の時系列", "その他")] * 3
        fc = Smart(overrides=[(when(name="yp_structure_tags"), lambda kw: fc.resp(kw, {"voices": [{"voice": s, "opening_type": o, "development_type": d, "closing_type": cl, "evidence_ja": "e"}
                                                                                                    for s, (o, d, cl) in zip(c.SLOTS, same)]}))])
        self.run_sns(fc)
        rec = self.rj("text", "voices", "voices_record.json")
        self.assertTrue(rec["structure"]["tags_before"]["fire"]["fired"])
        self.assertEqual(rec["structure"]["regen"]["slot"], "voice_2")
        self.assertIsNotNone(rec["structure"]["tags_after"])
        emph = [k for k in fc.by("gpt-6.1-sol") if "今回の追加指示" in k["input"][-1]["content"]]
        self.assertEqual(len(emph), 1)

    def test_voice_contract_violation_regenerates_then_stops(self):
        fc = Smart()
        bad = lambda kw: fc.resp(kw, "一人称のない語り。")
        fc.overrides = [(when(dev="書き手"), bad), (when(dev="書き手"), bad)]
        with self.assertRaises(c.YStop) as e:
            self.run_sns(fc)
        self.assertEqual(e.exception.code, "VOICE_CONTRACT_STOP")
        self.assertEqual(len(fc.calls), 2)                                           # 初回+再生成1回で停止(それ以上API 0)
        st = self.rj("text", "article_status.json")
        self.assertEqual((st["status"], st["code"]), ("STOP", "VOICE_CONTRACT_STOP"))
        self.assertTrue(os.path.exists(os.path.join(self.d, "text", "voices", "voices_partial.json")))
        self.assertFalse(os.path.exists(os.path.join(self.d, "text", "voices", "voices_final.json")))
        self.assertFalse(os.path.exists(os.path.join(self.d, "text", "article_record.json")))

    def test_voice_gate_fail_rewrites_only_flagged_voice(self):
        new2 = "僕は友達との連絡にいつも使っているから、年齢だけで切られるのは困る。でも、自分で決めたい気持ちと、危ない時は大人に頼りたい気持ちが、僕の中で両方ある。"
        fc = Smart()
        fc.overrides = [(when(name="family_y_persona_leakage_voices"), leak_fail("voices", {"voice_2": ["leak_evidence_subject"]})),
                        (when(name="family_y_persona_rewrite"), lambda kw: fc.resp(kw, {"rewrites": [{"section": "voice_2", "text": new2}]}))]
        res = self.run_sns(fc)
        self.assertEqual(res["voices"]["voice_2"], new2)
        self.assertEqual(res["voices"]["voice_1"], VOICES_OK["私"])
        rec = self.rj("text", "voices", "voices_record.json")
        self.assertEqual((rec["gate"]["status"], rec["gate"]["n_judgements"], rec["gate"]["rewritten"]), ("PASS", 2, True))
        rw = [k for k in fc.calls if k["model"] == "gpt-6.1-sol" and self.is_rewrite(k)]
        self.assertEqual(len(rw), 1)
        self.assertEqual(rw[0]["reasoning"], {"effort": "medium"})
        gr = self.rj("text", "voices", "gate_voices", "gate_result.json")
        self.assertEqual(len(gr["history"]), 2)
        self.assertIn("rewrite_calls", gr["history"][0])
        th = c.load_theme_package(SNS_PKG)["theme"]
        up = rw[0]["input"][-1]["content"]
        self.assertIn(th["world_frame"]["shared_premise_ja"], up)                       # 題材非依存の書換えprompt: 共通前提・Personaは入力から
        self.assertIn(c.render_persona(th["sheets"]["voice_2"], th["who_ja"]["voice_2"]), up)
        self.assertIn(VOICES_OK["私"], up)                                              # 他のVoiceは読み取り専用の文脈

    @staticmethod
    def is_rewrite(kw):
        return (kw.get("text") or {}).get("format", {}).get("name") == "family_y_persona_rewrite"

    def test_voice_residual_after_three_judgements_stops_without_closing_or_final(self):
        f = leak_fail("voices", {"voice_2": ["leak_evidence_subject"]})
        fc = Smart()
        newv = lambda kw: fc.resp(kw, {"rewrites": [{"section": "voice_2", "text": VOICES_OK["僕"].replace("困る", "困ってしまう")}]})
        fc.overrides = [(when(name="family_y_persona_leakage_voices"), f), (when(name="family_y_persona_rewrite"), newv),
                        (when(name="family_y_persona_leakage_voices"), f), (when(name="family_y_persona_rewrite"), newv),
                        (when(name="family_y_persona_leakage_voices"), f)]
        with self.assertRaises(c.YStop) as e:
            self.run_sns(fc)
        self.assertEqual(e.exception.code, "VOICE_RESIDUAL_STOP")
        self.assertEqual(self.rj("text", "voices", "gate_voices", "gate_result.json")["n_judgements"], 3)
        self.assertFalse(os.path.exists(os.path.join(self.d, "text", "voices", "gate_voices", "final_texts.json")))
        self.assertFalse(os.path.exists(os.path.join(self.d, "text", "closing")))
        self.assertEqual(self.rj("text", "article_status.json")["code"], "VOICE_RESIDUAL_STOP")
        self.assertEqual([k for k in fc.calls if (k.get("text") or {}).get("format", {}).get("name") == "family_y_closing_general"], [])

    def test_rewrite_deterministic_failure_is_rewrite_stop(self):
        fc = Smart()
        bad = lambda kw: fc.resp(kw, {"rewrites": [{"section": "voice_2", "text": "一人称がない書換え。"}]})
        fc.overrides = [(when(name="family_y_persona_leakage_voices"), leak_fail("voices", {"voice_2": ["leak_evidence_subject"]})),
                        (when(name="family_y_persona_rewrite"), bad), (when(name="family_y_persona_rewrite"), bad)]
        with self.assertRaises(c.YStop) as e:
            self.run_sns(fc)
        self.assertEqual(e.exception.code, "REWRITE_STOP")

    def test_leadintro_gate_applies_only_to_narrator_relevant_items(self):
        """OT-28: leak_evidence_memorable / Tension専用2項目はLead・紹介に非適用。出所系(evidence_subject等)は適用。"""
        na = {"tension": ["leak_evidence_memorable", "leak_tension_reverts_to_research", "leak_binary_camp_split"]}
        fc = Smart(overrides=[(when(name="family_y_persona_leakage_tension"), leak_fail("tension", na))])
        self.run_sns(fc)                                                              # 非適用項目のFAILだけ=PASS(記録は残る)
        rec = self.rj("text", "lead_intro", "gate", "applicable_result.json")
        self.assertEqual(rec["status"], "PASS")
        self.assertEqual(sorted(rec["not_applicable_flagged"][0]["fail_fields"]), sorted(na["tension"]))
        self.assertEqual(rec["applicable_flagged"], [])

    def test_leadintro_gate_fail_on_applicable_item_stops(self):
        for fld in ("leak_evidence_subject", "leak_discovery_syntax", "leak_numbers_foreground"):
            with tempfile.TemporaryDirectory() as d:
                fc = Smart(overrides=[(when(name="family_y_persona_leakage_tension"), leak_fail("tension", {"tension": [fld]}))])
                with self.assertRaises(c.YStop) as e:
                    c.produce_article(fc, slug="sns_age_limit", theme_package=SNS_PKG, out_dir=os.path.join(d, "t"))
                self.assertEqual(e.exception.code, "LEADINTRO_LEAKAGE_FLAGGED", fld)
                self.assertEqual([k for k in fc.calls if (k.get("text") or {}).get("format", {}).get("name") == "family_y_closing_general"], [])   # Closingへ進まない

    def test_lead_and_intro_contract_stops(self):
        fc = Smart(lead="短い。")
        with self.assertRaises(c.YStop) as e:
            self.run_sns(fc)
        self.assertEqual(e.exception.code, "LEAD_CONTRACT_STOP")
        self.assertEqual(len(fc.by("gpt-6.1-sol")), 3 + 2)                           # Voice3 + Lead(初回+再生成)
        with tempfile.TemporaryDirectory() as d:
            bad = dict(INTROS_OK, voice_1="私が最初に話す。")
            fc2 = Smart(intros=bad)
            with self.assertRaises(c.YStop) as e2:
                c.produce_article(fc2, slug="sns_age_limit", theme_package=SNS_PKG, out_dir=os.path.join(d, "t"))
            self.assertEqual(e2.exception.code, "INTRO_CONTRACT_STOP")

    def test_intro_foreshadow_and_copy_detected(self):
        th = c.load_theme_package(SNS_PKG)["theme"]
        spec = c.intro_spec(th)
        body = VOICES_OK["私"]
        self.assertIn("FORESHADOWS_CLAIM_WORD", c.check_intro("最初に話すのは、禁止に反対している、幼い子どもを育てる親だ。", "voice_1", body, spec)["violations"])
        self.assertIn("COPIES_VOICE_BODY_10CHARS", c.check_intro("最初に話すのは、静かにしてほしい時は助けられる自分もいて、割り切れない親だ。", "voice_1", body, spec)["violations"])
        self.assertIn("INTRO_OBJECT_NOT_IN_OWN_VOICE:年齢確認", c.check_intro("最初に話すのは、年齢確認が気になっている、幼い子どもを育てる親だ。", "voice_1", body, spec)["violations"])
        self.assertTrue(c.check_intro(INTROS_OK["voice_1"], "voice_1", body, spec)["ok"])

    def test_closing_contract_stop_propagates_with_artifacts(self):
        fc = Smart(closing="短い。")
        with self.assertRaises(c.YStop) as e:
            self.run_sns(fc)
        self.assertEqual(e.exception.code, "CLOSING_GENERAL_CONTRACT_STOP")
        self.assertTrue(os.path.exists(os.path.join(self.d, "text", "voices", "voices_final.json")))            # Voice/Lead/紹介は保存済み
        self.assertTrue(os.path.exists(os.path.join(self.d, "text", "lead_intro", "stage_lead_intro.json")))
        self.assertFalse(os.path.exists(os.path.join(self.d, "text", "closing", "closing_final.txt")))

    def test_resume_after_closing_stop_does_not_pay_for_voices_again(self):
        fc = Smart(closing="短い。")
        with self.assertRaises(c.YStop):
            self.run_sns(fc)
        fc2 = Smart()
        res = self.run_sns(fc2)
        self.assertEqual(len(fc2.calls), 2)                                          # Closing生成1 + Closing判定1のみ
        self.assertEqual(res["closing"], GOOD)
        self.assertEqual(res["records"]["stages_done"], ["voices(cached)", "lead_intro(cached)", "closing"])
        fc3 = Smart()
        self.run_sns(fc3)
        self.assertEqual(fc3.calls, [])                                              # 全段完了後はAPI 0

    def test_cache_invalidated_when_package_changes(self):
        fc = Smart()
        self.run_sns(fc)
        d = json.load(open(SNS_PKG, encoding="utf-8"))
        d["sheets"]["voice_1"]["claim_core_ja"] += "。"
        p2 = os.path.join(self.d, "pkg2.json")
        json.dump(d, open(p2, "w", encoding="utf-8"), ensure_ascii=False)
        fc2 = Smart()
        c.produce_article(fc2, slug="sns_age_limit", theme_package=p2, out_dir=os.path.join(self.d, "text"))
        self.assertEqual(len(fc2.calls), 16)

    def test_registry_slug_without_reuse_stops_before_any_api(self):
        fc = Smart()
        with self.assertRaises(c.YStop) as e:
            c.produce_article(fc, slug="redelivery_fee", theme_package=RED_PKG, out_dir=os.path.join(self.d, "t"))
        self.assertEqual(e.exception.code, "FIXED_CLOSING_REQUIRES_R0_REUSE")
        self.assertEqual(fc.calls, [])


class TestGuardsAndRouting(Routed):
    def test_guard_exception_stops_before_first_api_call(self):
        fc = Smart()

        def stop(label):
            raise RuntimeError("BUDGET_STOP")
        with self.assertRaises(RuntimeError):
            self.run_sns(fc, guard=stop)
        self.assertEqual(fc.calls, [])

    def test_error_status_replaces_stale_done_status(self):
        self.run_sns(Smart())
        self.assertEqual(self.rj("text", "article_status.json")["status"], "DONE")
        shutil.rmtree(os.path.join(self.d, "text", "closing"))                       # Closingだけやり直し→予算guardで異常終了させる

        def stop(label):
            raise RuntimeError("BUDGET_STOP")
        with self.assertRaises(RuntimeError):
            self.run_sns(Smart(), guard=stop)
        st = self.rj("text", "article_status.json")
        self.assertEqual((st["status"], st["error_type"]), ("ERROR", "RuntimeError"))     # 古いDONEが残らない
        self.assertIn("BUDGET_STOP", st["message"])

    def test_guard_exception_midway_blocks_following_calls(self):
        fc = Smart()
        seen = []

        def stop_at_gate(label):
            seen.append(label)
            if label == "yp_voices_gate_leak1":
                raise RuntimeError("BUDGET_STOP")
        with self.assertRaises(RuntimeError):
            self.run_sns(fc, guard=stop_at_gate)
        self.assertEqual(len(fc.calls), 7)                                           # 生成3+付番3+構造1。Gate判定は呼ばれない
        self.assertEqual(seen[-1], "yp_voices_gate_leak1")

    def test_aux_route_unregistered_stops_before_first_api_call(self):
        fc = Smart()
        with mock.patch.dict(routing.PROCESS_MODEL_MAP, clear=False):
            routing.PROCESS_MODEL_MAP.pop("FAMILY_Y_VOICE_PROVENANCE_MAP")
            with self.assertRaises(routing.ModelContractViolation):
                self.run_sns(fc)
        self.assertEqual(fc.calls, [])                                               # Voice生成(高額)の前に停止=費用0

    def test_any_core_route_unregistered_stops_before_first_api_call(self):
        for key in ("FAMILY_Y_VOICE_GENERATE", "FAMILY_Y_LEAK_JUDGE", "FAMILY_Y_CLOSING_REWRITE", "FAMILY_Y_PERSONA_INTRO", "FAMILY_Y_LEAD_GENERATE"):
            fc = Smart()
            with mock.patch.dict(routing.PROCESS_MODEL_MAP, clear=False):
                routing.PROCESS_MODEL_MAP.pop(key)
                with self.assertRaises(routing.ModelContractViolation):
                    c.produce_article(fc, slug="sns_age_limit", theme_package=SNS_PKG, out_dir=os.path.join(self.d, key))
            self.assertEqual(fc.calls, [], key)

    def test_response_model_mismatch_stops(self):
        fc = Smart(overrides=[(when(dev="書き手"), lambda kw: Resp({}, model="gpt-6-luna-x"))])
        with self.assertRaises(c.ProvenanceViolation):
            self.run_sns(fc)

    def test_no_client_raises_without_side_effects_beyond_status(self):
        with self.assertRaises(RuntimeError):
            self.run_sns(None)

    def test_aux_routes_match_er006_when_registered(self):
        self.patch.stop()
        try:
            for k, v in c.ROUTE_AUX.items():
                if k in routing.PROCESS_MODEL_MAP:
                    self.assertEqual(routing.PROCESS_MODEL_MAP[k], v["model"], k)
        finally:
            self.patch.start()

    def test_preflight_lists_every_key_with_model(self):
        r = c.preflight_routes(["FAMILY_Y_LEAK_JUDGE", "FAMILY_Y_VOICE_STRUCTURE_TAG"])
        self.assertEqual([x["model"] for x in r], ["gpt-6-luna", "gpt-6-luna"])


# ============================================================
# 宅配の既存R0を再利用する経路(E-1)
# ============================================================
@unittest.skipUnless(have("er110_output/family_y_opinion_based_03/redelivery_fee/run_01/article_ja.md", "er110_output/family_y_redelivery_audio_01/revision_01/lead/lead.txt",
                          "er110_output/family_y_redelivery_audio_01/revision_01/intro/intros.json"), "redelivery R0 absent")
class TestReusePath(Routed):
    def run_red(self, fc, reuse=RED_REUSE, **kw):
        return c.produce_article(fc, slug="redelivery_fee", theme_package=RED_PKG, out_dir=os.path.join(self.d, "text"), reuse=reuse, **kw)

    def manifest(self):
        return json.load(open(RED_REUSE, encoding="utf-8"))

    def test_reuse_adopts_r0_byte_identical_and_injects_plan_b(self):
        fc = Smart()
        res = self.run_red(fc)
        import er110_family_y_redelivery_audio_01 as rr
        r0 = rr.load_r0()
        self.assertEqual(res["voices"], {s: r0[s].strip() for s in c.SLOTS})                       # byte一致
        self.assertEqual(res["lead"], open(os.path.join(ROOT, self.manifest()["lead_file"]), encoding="utf-8").read().strip())
        self.assertEqual(res["intros"], json.load(open(os.path.join(ROOT, self.manifest()["intros_file"]), encoding="utf-8")))
        self.assertEqual(res["closing"], c.FIXED_CLOSING_REGISTRY["redelivery_fee"]["text"])        # 案B(誤って案A/Cや一般化案にならない)
        # API: Lead+紹介の補助判定1 + 案B判定1 のみ(Voice生成0・Voice Gateは来歴検査付きの既存PASS記録を再利用)
        self.assertEqual(len(fc.calls), 2)
        self.assertEqual([k["model"] for k in fc.calls], ["gpt-6-luna", "gpt-6-luna"])
        self.assertEqual(fc.by("gpt-6.1-sol"), [])
        rec = self.rj("text", "article_record.json")
        self.assertEqual(rec["mode"], "reused_r0")
        self.assertEqual(rec["voices"]["source"], "reused_r0")
        self.assertFalse(rec["voices"]["voice_generation_used"])
        self.assertEqual(rec["voices"]["gate"]["source"], "reused_prior_pass_record")
        self.assertEqual(rec["lead"]["source"], "reused")
        self.assertEqual(rec["intros"]["source"], "reused")
        self.assertEqual(rec["closing"]["source"], "fixed_user_approved")
        self.assertFalse(rec["closing"]["general_method_used"])
        self.assertEqual(rec["closing"]["voice_r0_sha256"], c.FIXED_CLOSING_REGISTRY["redelivery_fee"]["voice_r0_sha256"])
        self.assertEqual(rec["theme_package_sha256"], c.FIXED_CLOSING_REGISTRY["redelivery_fee"]["theme_package_sha256"])
        self.assertIn("Production runtime evidenceではない", rec["voices"]["note"])

    def test_plan_b_gate_fail_rejudges_three_times_without_rewrite_then_stops_and_no_closing_final(self):
        """OT-27改訂(委任_04, USER_02 ②): 案Bは既存の再判定機構(判定<=3回)を使うが承認本文は書換えない。3回判定後もFAILなら公開せずSTOP(ユーザー承認本文とGateの衝突としてユーザー判断へ)。"""
        # 委任_05: leak_evidence_memorable単独のFAILは個別Human承認(USER_03 §1)で救済されるため、STOP側の検証には承認対象外の別項目を使う
        fail = leak_fail("tension", {"tension": ["leak_discovery_syntax"]})
        fc = Smart(overrides=[(when(name="family_y_persona_leakage_tension"), lambda kw: Resp(leak_obj("tension"), model="gpt-6-luna-2026")),      # Lead/紹介判定=PASS
                              (when(name="family_y_persona_leakage_tension"), fail), (when(name="family_y_persona_leakage_tension"), fail),
                              (when(name="family_y_persona_leakage_tension"), fail)])                                                              # 案B判定=3回ともFAIL
        with self.assertRaises(c.YStop) as e:
            self.run_red(fc)
        self.assertEqual(e.exception.code, "FIXED_CLOSING_RESIDUAL_FAIL")
        self.assertEqual(len(fc.calls), 4)                                                            # Lead/紹介1+案B判定3。それ以上は呼ばない
        self.assertEqual([k for k in fc.calls if self.is_rewrite(k)], [])
        self.assertFalse(os.path.exists(os.path.join(self.d, "text", "closing", "closing_final.txt")))
        rec = self.rj("text", "closing", "closing_record.json")
        self.assertEqual((rec["status"], rec["n_judgements"], rec["rewritten"]), ("FIXED_CLOSING_RESIDUAL_FAIL", 3, False))
        st = self.rj("text", "article_status.json")
        self.assertEqual((st["status"], st["code"]), ("STOP", "FIXED_CLOSING_RESIDUAL_FAIL"))
        self.assertTrue(os.path.exists(os.path.join(self.d, "text", "lead_intro", "stage_lead_intro.json")))      # 再開時にLead/紹介は再課金しない

    def _mem_fail_overrides(self):
        mem = leak_fail("tension", {"tension": ["leak_evidence_memorable"]})
        nm = "family_y_persona_leakage_tension"
        return [(when(name=nm), lambda kw: Resp(leak_obj("tension"), model="gpt-6-luna-2026")),      # Lead/紹介判定=PASS
                (when(name=nm), mem), (when(name=nm), mem), (when(name=nm), mem)]                  # 案B判定=3回ともleak_evidence_memorableのみFAIL

    def test_plan_b_memorable_only_fail_is_accepted_by_human_approval_end_to_end_and_cached_resume_reverifies(self):
        """委任_05 ①(USER_03 §1): 案Bが3判定ともleak_evidence_memorableのみFAIL→PASS_BY_HUMAN_APPROVALで記事組立まで進む。再実行(cache)でも来歴を再検査する。"""
        fc = Smart(overrides=self._mem_fail_overrides())
        res = self.run_red(fc)
        self.assertEqual(res["closing"], c.FIXED_CLOSING_REGISTRY["redelivery_fee"]["text"])
        self.assertEqual(len(fc.calls), 4)                                                            # Lead/紹介1+案B判定3。書換え0
        self.assertEqual([k for k in fc.calls if self.is_rewrite(k)], [])
        rec = self.rj("text", "article_record.json")
        self.assertEqual(rec["closing"]["status"], c.PASS_BY_HUMAN_APPROVAL)
        self.assertIn("USER_03.md", rec["closing"]["human_approval_ref"])
        self.assertEqual(self.rj("text", "closing", "gate", "gate_result.json")["status"], "LEAKAGE_RESIDUAL_STOP")      # 元のGate結果は保持
        self.assertTrue(os.path.exists(os.path.join(self.d, "text", "closing", c.HUMAN_APPROVED_CLOSING_FILE)))
        # cache再利用(API 0)。承認記録の来歴が現在の案Bと一致する限り同じ結果
        fc2 = Smart()
        res2 = self.run_red(fc2)
        self.assertEqual(fc2.calls, [])
        self.assertEqual(res2["closing_record"]["status"], c.PASS_BY_HUMAN_APPROVAL)
        # 承認記録の元判定snapshotが改変されていたら、cacheがあっても承認を使い回さず停止
        ha_path = os.path.join(self.d, "text", "closing", c.HUMAN_APPROVED_CLOSING_FILE)
        snap = json.load(open(ha_path, encoding="utf-8"))["closing"]["judgements"][0]["snapshot_path"]
        open(snap, "ab").write(b" ")
        with self.assertRaises(c.YStop) as e:
            self.run_red(Smart())
        self.assertEqual(e.exception.code, "HUMAN_APPROVAL_PROVENANCE_MISMATCH")

    @staticmethod
    def is_rewrite(kw):
        return (kw.get("text") or {}).get("format", {}).get("name") == "family_y_persona_rewrite"

    def tmp_manifest(self, **over):
        man = self.manifest()
        man.update(over)
        p = os.path.join(self.d, "man.json")
        json.dump(man, open(p, "w", encoding="utf-8"), ensure_ascii=False)
        return p

    def copy_r0(self):
        src = os.path.join(ROOT, "er110_output/family_y_opinion_based_03/redelivery_fee/run_01")
        dst = os.path.join(self.d, "r0")
        shutil.copytree(src, dst, ignore=shutil.ignore_patterns("*.jsonl"))
        return dst

    def test_reuse_mismatch_between_article_and_gate_final_stops_with_zero_api(self):
        r0 = self.copy_r0()
        ft = os.path.join(r0, "gate_voices", "final_texts.json")
        d = json.load(open(ft, encoding="utf-8"))
        d["voice_1"] += "。"
        json.dump(d, open(ft, "w", encoding="utf-8"), ensure_ascii=False)
        fc = Smart()
        with self.assertRaises(c.YStop) as e:
            self.run_red(fc, reuse=self.tmp_manifest(voice_r0_article=os.path.join(r0, "article_ja.md"), voice_gate_dir=os.path.join(r0, "gate_voices")))
        self.assertEqual(e.exception.code, "REUSE_MISMATCH")
        self.assertEqual(fc.calls, [])

    def test_modified_r0_changes_sha_and_registry_refuses_plan_b(self):
        r0 = self.copy_r0()
        art = os.path.join(r0, "article_ja.md")
        open(art, "ab").write(b"\n")
        fc = Smart()
        with self.assertRaises(c.YStop) as e:
            self.run_red(fc, reuse=self.tmp_manifest(voice_r0_article=art, voice_gate_dir=os.path.join(r0, "gate_voices")))
        self.assertEqual(e.exception.code, "FIXED_CLOSING_PROVENANCE_MISMATCH")
        self.assertEqual(fc.calls, [])

    def test_slug_mismatch_and_bad_schema(self):
        with self.assertRaises(c.YStop) as e:
            c.produce_article(Smart(), slug="sns_age_limit", theme_package=SNS_PKG, out_dir=os.path.join(self.d, "t"), reuse=RED_REUSE)
        self.assertEqual(e.exception.code, "REUSE_MISMATCH")
        with self.assertRaises(c.YStop) as e2:
            self.run_red(Smart(), reuse=self.tmp_manifest(schema="nope"))
        self.assertEqual(e2.exception.code, "REUSE_MISMATCH")

    def test_reused_lead_failing_checks_stops(self):
        bad = os.path.join(self.d, "lead.txt")
        open(bad, "w", encoding="utf-8").write("三人の声。数字は12。")
        fc = Smart()
        with self.assertRaises(c.YStop) as e:
            self.run_red(fc, reuse=self.tmp_manifest(lead_file=bad))
        self.assertEqual(e.exception.code, "REUSED_TEXT_CHECK_FAILED")
        self.assertEqual(fc.calls, [])

    def test_reused_intro_foreshadowing_stops(self):
        intros = json.load(open(os.path.join(ROOT, self.manifest()["intros_file"]), encoding="utf-8"))
        intros["voice_2"] = "次は、有料化に反対の、共働きで家を空けがちな人だ。"
        p = os.path.join(self.d, "intros.json")
        json.dump(intros, open(p, "w", encoding="utf-8"), ensure_ascii=False)
        with self.assertRaises(c.YStop) as e:
            self.run_red(Smart(), reuse=self.tmp_manifest(intros_file=p))
        self.assertEqual(e.exception.code, "REUSED_TEXT_CHECK_FAILED")

    def test_prior_gate_not_reusable_when_prompt_sha_differs_is_rejudged_without_rewrite(self):
        r0 = self.copy_r0()
        gp = os.path.join(r0, "gate_voices", "gate_result.json")
        g = json.load(open(gp, encoding="utf-8"))
        g["history"][-1]["check"]["prompt_sha256"] = "0" * 64
        json.dump(g, open(gp, "w", encoding="utf-8"), ensure_ascii=False)
        fc = Smart()
        res = self.run_red(fc, reuse=self.tmp_manifest(voice_r0_article=os.path.join(r0, "article_ja.md"), voice_gate_dir=os.path.join(r0, "gate_voices")))
        self.assertEqual(len(fc.by(name="family_y_persona_leakage_voices")), 1)                       # 判定1回(書換えなし)
        self.assertEqual(self.rj("text", "article_record.json")["voices"]["gate"]["source"], "judged_this_run")
        self.assertEqual(res["closing"], c.FIXED_CLOSING_REGISTRY["redelivery_fee"]["text"])

    def test_reused_voice_judged_fail_stops_and_never_rewrites(self):
        r0 = self.copy_r0()
        gp = os.path.join(r0, "gate_voices", "gate_result.json")
        g = json.load(open(gp, encoding="utf-8"))
        g["history"][-1]["check"]["prompt_sha256"] = "0" * 64
        json.dump(g, open(gp, "w", encoding="utf-8"), ensure_ascii=False)
        fc = Smart(overrides=[(when(name="family_y_persona_leakage_voices"), leak_fail("voices", {"voice_1": ["leak_evidence_subject"]}))])
        with self.assertRaises(c.YStop) as e:
            self.run_red(fc, reuse=self.tmp_manifest(voice_r0_article=os.path.join(r0, "article_ja.md"), voice_gate_dir=os.path.join(r0, "gate_voices")))
        self.assertEqual(e.exception.code, "REUSED_VOICE_GATE_FAIL")
        self.assertEqual(len(fc.calls), 1)


class TestVerbatim(Routed):
    def test_verbatim_stop_when_part_copies_source(self):
        src = os.path.join(self.d, "src")
        os.makedirs(src)
        copied = "静かにしてほしい時は助けられる自分もいて割り切れない年齢に合わせた決まりがあれば少し楽になる気がする"
        open(os.path.join(src, "a.txt"), "w", encoding="utf-8").write("前置き。" + copied + "。後書き。")
        d = json.load(open(SNS_PKG, encoding="utf-8"))
        d["source_dir"] = src
        p = os.path.join(self.d, "pkg.json")
        json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False)
        with self.assertRaises(c.YStop) as e:
            c.produce_article(Smart(), slug="sns_age_limit", theme_package=p, out_dir=os.path.join(self.d, "t"))
        self.assertEqual(e.exception.code, "SOURCE_VERBATIM_STOP")
        self.assertTrue(os.path.exists(os.path.join(self.d, "t", "verbatim_hits.json")))
        self.assertFalse(os.path.exists(os.path.join(self.d, "t", "article_record.json")))

    def test_no_source_dir_is_recorded_as_not_checked(self):
        d = json.load(open(SNS_PKG, encoding="utf-8"))
        d.pop("source_dir")
        p = os.path.join(self.d, "pkg.json")
        json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False)
        c.produce_article(Smart(), slug="sns_age_limit", theme_package=p, out_dir=os.path.join(self.d, "t"))
        rec = self.rj("t", "article_record.json")
        self.assertFalse(rec["verbatim"]["checked"])
        self.assertIn("未確認", rec["verbatim"]["reason"])

    def test_sns_package_source_dir_exists_and_clean_run_checks_it(self):
        if not have("docs/research/FAMILY-Y-VOICES-DESIGN-01/OPINION_BASED_01/sources"):
            self.skipTest("sources absent")
        self.run_sns_clean()

    def run_sns_clean(self):
        c.produce_article(Smart(), slug="sns_age_limit", theme_package=SNS_PKG, out_dir=os.path.join(self.d, "t"))
        rec = self.rj("t", "article_record.json")
        self.assertTrue(rec["verbatim"]["checked"])
        self.assertEqual(rec["verbatim"]["n_hits"], 0)


class TestAssembly(unittest.TestCase):
    def parts(self):
        return dict(lead=LEAD_OK, intros=dict(INTROS_OK), voices={"voice_1": VOICES_OK["私"], "voice_2": VOICES_OK["僕"], "voice_3": VOICES_OK["わたし"]}, closing=GOOD)

    def fps(self):
        return {"voice_1": "私", "voice_2": "僕", "voice_3": "わたし"}

    def test_clean_parts_pass(self):
        p = self.parts()
        self.assertEqual(c.check_article_parts(p["lead"], p["intros"], p["voices"], p["closing"], self.fps(), p["voices"]), [])

    def test_violations_detected(self):
        p = self.parts()
        chk = lambda **kw: c.check_article_parts(kw.get("lead", p["lead"]), kw.get("intros", p["intros"]), kw.get("voices", p["voices"]), kw.get("closing", p["closing"]), self.fps(),
                                                  kw.get("expected", p["voices"]))
        self.assertTrue(any("IN_ONE_LINE_PRESENT" in x for x in chk(closing=GOOD + "\nIn one line")))
        self.assertTrue(any("HAS_AI_EDIT_ANNOUNCEMENT:lead" in x for x in chk(lead="AIが組み立てた三人の声。")))
        self.assertTrue(any("NARRATOR_STARTS_WITH_FIRST_PERSON:closing" in x for x in chk(closing="私は思う。" + GOOD)))
        self.assertTrue(any("VOICE_CHANGED_AFTER_GATE:voice_1" in x for x in chk(expected=dict(p["voices"], voice_1="別の本文"))))
        self.assertTrue(any("VOICE_NO_OWN_FIRST_PERSON:voice_2" in x for x in chk(voices=dict(p["voices"], voice_2="一人称なし"), expected=dict(p["voices"], voice_2="一人称なし"))))
        self.assertTrue(any("INTRO_HAS_FIRST_PERSON:voice_3" in x for x in chk(intros=dict(p["intros"], voice_3="私が最後に話す。"))))

    def test_render_has_title_and_five_paragraphs(self):
        p = self.parts()
        t = c.render_article_text("タイトル", p["lead"], p["intros"], p["voices"], p["closing"])
        self.assertTrue(t.startswith("# タイトル\n\n"))
        self.assertEqual(len([x for x in re.split(r"\n\s*\n", t.split("\n\n", 1)[1].strip()) if x]), 5)

    def test_page_notice_is_not_in_article_text_and_is_the_approved_wording(self):
        # 委任_08(ユーザー正式決定2026-10-27 USER_04 §1-B): 承認文言(逐語)。旧文言(「実在する人々の意見を参考に…」)は撤去
        notice = "Voice 1〜3は実在人物の発言をそのまま再現したものではなく、実際に投稿された意見をもとに、AIが編集・再構成したものです。"
        p = self.parts()
        t = c.render_article_text("タイトル", p["lead"], p["intros"], p["voices"], p["closing"])
        self.assertNotIn(notice, t)                                  # 注意書きはページ側(本文外)。音声にアナウンスを入れない
        self.assertNotIn("AIが編集", t)
        try:
            import er121_family_y_structure_01 as ys
            self.assertEqual(ys.PAGE_NOTICE_JA, notice)
            self.assertTrue(ys.check_y_article(t, lang="ja")["ok"])
            sp = ys.split_y_article(t)
            self.assertEqual(sp["lead"], p["lead"])
        except ImportError:
            pass


class TestIsolation02C(unittest.TestCase):
    def test_import_does_no_io_and_exposes_no_flag(self):
        src = open(SRC, encoding="utf-8").read()
        for w in ("os.environ", "getenv", "argparse", "sys.argv", "SKIPPED_BUDGET", "__main__", "TENSION_RULES"):
            self.assertNotIn(w, src, w)
        self.assertNotRegex(src, r"(?m)^\s*(import|from)\s+er110")
        self.assertNotIn("openai", src.replace("openai client", ""))

    def test_dev_modules_do_not_import_er121(self):
        for fn in os.listdir(ROOT):
            if fn.startswith("er110_family_y_") and fn.endswith(".py"):
                self.assertNotIn("er121", open(os.path.join(ROOT, fn), encoding="utf-8").read(), fn)

    def test_produce_article_signature_matches_runner_call(self):
        import inspect
        sig = inspect.signature(c.produce_article)
        for k in ("slug", "theme_package", "out_dir", "guard"):
            self.assertIn(k, sig.parameters)
        self.assertIs(sig.parameters["guard"].default, None)
        self.assertIs(sig.parameters["reuse"].default, None)

    def test_sleep_and_budget_hooks_default_off(self):
        self.assertIsNone(c._sleep)


if __name__ == "__main__":
    unittest.main()
