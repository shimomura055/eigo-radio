# -*- coding: utf-8 -*-
"""FY-SPEAKER-INTRO-BE-PRODUCTION-WIRING-01(2026-10-29): Family Y人物紹介 B+E方式の正式配線test。
Trial確定成果物(er121_output/family_y_intro_trial_01/*)を正本とし、(1) Prompt sha・B+E節 (2) person_blockの『話題との関わり』行 (3) 3類型golden
(4) 時期語の決定論検査が無いこと (5) retry/regeneration/cacheで同じPromptが使われること (6) X/Zへ未適用 を固定する。"""
import json, os, re, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.chdir(HERE)
import er121_family_y_text_core_01 as tc

TRIAL = "er121_output/family_y_intro_trial_01"
PKG = {
    "surname": "docs/research/FAMILY-Y-SURNAME-CHOICE-PRODUCTION-01/theme_packages/surname_choice_package_01.json",
    "sns_age_limit": "docs/research/FAMILY-Y-PRODUCTION-LAUNCH-01/theme_packages/sns_age_limit_package_01.json",
}
RED_DATA = "docs/research/FAMILY-Y-VOICES-DESIGN-01/OPINION_BASED_02/THEME_DATA_02.json"
RED_MAN = "docs/research/FAMILY-Y-PRODUCTION-LAUNCH-01/theme_packages/redelivery_fee_reuse_01.json"
RUN = {"surname": "er121_output/family_y_production_01/surname_choice/run_02", "redelivery_fee": "er121_output/family_y_production_01/redelivery_fee/run_voice_puck_ev_01",
       "sns_age_limit": "er121_output/family_y_production_01/sns_age_limit/run_01"}
NEW_SHA = "a5da099a2d7b44392f118f61a97f3538933cf2e3354d0024b3bbcf697a12fbe5"
OLD_SHA = "787794d635587053d20a411aa98da70b00dc7a45bc182f1483c1ae6a7267afc4"
PRINCIPLE_HEAD = "- 【人物紹介の一般化原則】"
CLAUSE_E_HEAD = "- 【属性がそのまま立場のとき】"
ARTS = [f"{r}/text/article_assembled.md" for r in RUN.values()]


def have(*ps):
    return all(os.path.exists(p) for p in ps)


def red_checks():
    return json.load(open(RED_MAN, encoding="utf-8"))["intro_checks"]


def load_theme(slug):
    if slug == "redelivery_fee":
        raw = json.load(open(RED_DATA, encoding="utf-8"))
        man = json.load(open(RED_MAN, encoding="utf-8"))
        raw["intro_checks"] = man["intro_checks"]
        for k in ("lead_premise_ja", "lead_scope_lines"):
            if k in man:
                raw[k] = man[k]
        return tc.load_theme_package(raw)["theme"]
    return tc.load_theme_package(PKG[slug])["theme"]


def spec_of(slug, theme):
    return tc.intro_spec(theme, red_checks()) if slug == "redelivery_fee" else tc.intro_spec(theme)


def voices_of(slug):
    art = open(f"{RUN[slug]}/text/article_assembled.md", encoding="utf-8").read()
    blocks = [b.strip() for b in re.split(r"\n\s*\n", art.strip())]
    return {s: blocks[2 + i].split("\n", 1)[1].strip() for i, s in enumerate(tc.SLOTS)}


def cands(slug, name):
    return json.load(open(f"{TRIAL}/{slug}/ja_candidates_{name}.json", encoding="utf-8"))


class PromptShaAndClauses(unittest.TestCase):
    def test_sha_pinned_new_and_old_removed(self):
        self.assertEqual(tc.ARTICLE_PROMPTS["intro"][1], NEW_SHA)
        self.assertEqual(tc.load_article_prompt("intro")["sha256"], NEW_SHA)
        self.assertNotEqual(NEW_SHA, OLD_SHA)

    def test_be_clauses_present_once_right_after_header(self):
        t = tc.load_article_prompt("intro")["user_template"]
        self.assertEqual(t.count(PRINCIPLE_HEAD), 1)
        self.assertEqual(t.count(CLAUSE_E_HEAD), 1)
        body = t.split("【書き方】\n", 1)[1].split("\n")
        self.assertTrue(body[0].startswith(PRINCIPLE_HEAD))
        self.assertTrue(body[1].startswith(CLAUSE_E_HEAD))
        self.assertIn("宅配ドライバー", body[1])                       # 属性がそのまま立場のときは属性名を省かない(E節)
        self.assertIn("属性を削るだけで終わらせず", body[0])             # A方式(過剰抽象化)へ戻らない
        self.assertIn("機械的に使わず", body[0])                          # 機械的転記の禁止
        for tag in ("@@PREMISE@@", "@@PERSONS@@", "@@CLAIM_WORDS@@", "@@OBJECT_EXAMPLES@@"):
            self.assertIn(tag, t)

    def test_no_trial_label_left_in_production_prompt(self):
        t = open("er121_prompts/persona_intro_01.txt", encoding="utf-8").read()
        self.assertNotIn("(Trial", t)
        self.assertNotIn("Trial追加", t)

    @unittest.skipUnless(have(PKG["surname"], f"{TRIAL}/surname/ja_candidates_AB.json", *ARTS), "artifact無し")
    def test_no_timing_word_deterministic_check_added(self):
        # 『元情報にない時期語』を形式的にNGにする検査は追加しない(ユーザー決定)。Trial A1(『結婚して』を含む)がcheck_introを通ることで固定
        spec = tc.intro_spec(load_theme("surname"))
        a1 = cands("surname", "AB")["A1"]["intros"]["voice_1"]
        self.assertIn("結婚して", a1)
        self.assertEqual(tc.check_intro(a1, "voice_1", voices_of("surname")["voice_1"], spec), {"ok": True, "violations": []})
        seg = open("er121_family_y_text_core_01.py", encoding="utf-8").read().split("def check_intro", 1)[1].split("def person_block", 1)[0]
        self.assertNotIn("TIMING", seg)
        self.assertNotIn("結婚を機に", seg)

    def test_check_intro_thresholds_unchanged(self):
        self.assertEqual(tc.INTRO_RANGE, (32, 62))


@unittest.skipUnless(have(*PKG.values(), RED_DATA, RED_MAN, *ARTS), "Trial/Run artifact無し")
class PersonBlockAndPrompt(unittest.TestCase):
    def test_person_block_has_contact_line_for_three_types(self):
        for slug in ("surname", "redelivery_fee", "sns_age_limit"):
            theme, voices = load_theme(slug), voices_of(slug)
            for i, s in enumerate(tc.SLOTS):
                pb = tc.person_block(s, theme["sheets"], voices)
                cp = theme["sheets"][s]["contact_point_ja"].strip()
                self.assertTrue(cp)
                lines = pb.split("\n")
                self.assertTrue(lines[0].startswith(f"【人物{i + 1}】"))
                self.assertEqual(lines[1], f"  話題との関わり: {cp}", (slug, s))
                self.assertTrue(lines[2].startswith("  暮らしの様子:"))
                self.assertIn(voices[s], pb)                                # 本人の語りは読取専用のまま

    @staticmethod
    def _norm(p):
        return p.replace("(Trial)", "").replace("(Trial追加)", "").replace(CLAUSE_E_HEAD, CLAUSE_E_HEAD[2:])

    def test_production_prompt_equals_trial_confirmed_prompts(self):
        """Trial確定Prompt(prompt_E=redelivery/sns、surnameはprompt_B+E節)と、ラベル除去・箇条書き記号を除き一致(A方式へ戻っていない)。"""
        parts = tc.load_article_prompt("intro")
        for slug in ("redelivery_fee", "sns_age_limit", "surname"):
            theme, voices = load_theme(slug), voices_of(slug)
            premise, _s, _src = tc.lead_inputs(theme)
            prod = tc.build_intro_prompt(theme, premise, voices, parts, spec_of(slug, theme))
            tf = f"{TRIAL}/{slug}/prompt_E.txt" if slug != "surname" else f"{TRIAL}/surname/prompt_B.txt"
            trial = open(tf, encoding="utf-8").read()
            if slug == "surname":      # surnameのTrialはE節の前=B(原則+話題との関わり行)にE節を足したものが正本
                clause = [ln for ln in prod.split("\n") if ln.startswith(CLAUSE_E_HEAD)][0]
                lines = trial.split("\n")
                k = [i for i, ln in enumerate(lines) if ln.startswith("- 【人物紹介の一般化原則(Trial)】")][0]
                lines.insert(k + 1, clause)
                trial = "\n".join(lines)
            self.assertEqual(self._norm(prod).strip(), self._norm(trial).strip(), slug)


@unittest.skipUnless(have(*[f"{TRIAL}/{s}/ja_candidates_{n}.json" for s, n in (("surname", "AB"), ("redelivery_fee", "E"), ("redelivery_fee", "AB"), ("sns_age_limit", "E"))],
                          *PKG.values(), RED_DATA, RED_MAN, *ARTS), "Trial artifact無し")
class ThreeTypeGolden(unittest.TestCase):
    """Trial出力(B+E)を期待値の範囲として、乖離型・一致型・中間型の期待動作と既存check_introの通過を固定する。"""

    def test_surname_divergent_type_does_not_return_to_father(self):
        theme, voices = load_theme("surname"), voices_of("surname")
        spec = spec_of("surname", theme)
        for key in ("B1", "B2"):
            iv = cands("surname", "AB")[key]["intros"]
            self.assertNotIn("父親", iv["voice_1"], key)               # 属性『父親』を主名詞にしない
            self.assertIn("姓", iv["voice_1"])                          # 妻の姓に関する立場が中心
            for s in tc.SLOTS:
                self.assertTrue(tc.check_intro(iv[s], s, voices[s], spec)["ok"], (key, s))
        rec = "最初に話すのは、妻の姓を名乗り、妻の実家で家族と暮らしている男性だ。"       # 別承認の固定V1文(B+Eで再生成しない)の形も既存検査を通る
        self.assertTrue(tc.check_intro(rec, "voice_1", voices["voice_1"], spec)["ok"])

    def test_redelivery_match_type_keeps_driver_attribute(self):
        theme, voices = load_theme("redelivery_fee"), voices_of("redelivery_fee")
        spec = spec_of("redelivery_fee", theme)
        for key, c in cands("redelivery_fee", "E").items():
            self.assertIn("宅配ドライバー", c["intros"]["voice_1"], key)
            for s in tc.SLOTS:
                self.assertTrue(tc.check_intro(c["intros"][s], s, voices[s], spec)["ok"], (key, s))
        # 属性を削りすぎるA方式のTrial出力は『宅配ドライバー』を欠く=この期待値でA方式への後退を検出できる
        self.assertNotIn("宅配ドライバー", cands("redelivery_fee", "AB")["A1"]["intros"]["voice_1"])

    def test_sns_middle_type_combines_attribute_and_involvement(self):
        theme, voices = load_theme("sns_age_limit"), voices_of("sns_age_limit")
        spec = spec_of("sns_age_limit", theme)
        for key, c in cands("sns_age_limit", "E").items():
            iv = c["intros"]
            self.assertIn("親", iv["voice_1"])
            self.assertRegex(iv["voice_1"], "(見守|決める|使い方)")
            self.assertIn("高校生", iv["voice_2"])
            self.assertIn("制限", iv["voice_2"])
            self.assertIn("親", iv["voice_3"])
            self.assertIn("中学生", iv["voice_3"])
            for s in tc.SLOTS:
                self.assertTrue(tc.check_intro(iv[s], s, voices[s], spec)["ok"], (key, s))


class RetryRegenResume(unittest.TestCase):
    """retry(契約違反時の内部再生成)・--regenerate-stage text・cache/resumeが同じB+E Promptを使うこと。"""

    class _Resp:
        def __init__(self, text):
            self.output_text, self.id, self.model, self.usage = text, "r", "gpt-6.1-sol", None

    @unittest.skipUnless(have(PKG["sns_age_limit"], f"{TRIAL}/sns_age_limit/ja_candidates_E.json", *ARTS), "artifact無し")
    def test_internal_retry_reuses_be_prompt_and_adds_only_problem_list(self):
        theme, voices = load_theme("sns_age_limit"), voices_of("sns_age_limit")
        spec, parts = tc.intro_spec(theme), tc.load_article_prompt("intro")
        good = cands("sns_age_limit", "E")["E2"]["intros"]
        bad = dict(good)
        bad["voice_1"] = "私が最初に話す。"
        seen = []
        outs = [json.dumps(bad, ensure_ascii=False), json.dumps(good, ensure_ascii=False)]

        def fake_chat(client, *, route_key, user, stage, developer=None, schema=None, retries=2, guard=None):
            seen.append((route_key, stage, user))
            return self._Resp(outs[len(seen) - 1])
        orig = tc.chat
        tc.chat = fake_chat
        try:
            with tempfile.TemporaryDirectory() as d:
                r = tc.generate_intros(None, theme, voices, d, parts, spec)
        finally:
            tc.chat = orig
        self.assertEqual([x[0] for x in seen], ["FAMILY_Y_PERSONA_INTRO"] * 2)
        self.assertEqual([x[1] for x in seen], ["yp_intro", "yp_intro_regen"])
        for _rk, _st, user in seen:
            self.assertIn(PRINCIPLE_HEAD, user)
            self.assertIn(CLAUSE_E_HEAD, user)
            self.assertIn("  話題との関わり: ", user)
        self.assertTrue(seen[1][2].startswith(seen[0][2]))
        self.assertEqual(r["intros"]["voice_2"], good["voice_2"])

    def test_text_stage_cache_key_and_single_path(self):
        src = open("er121_family_y_text_core_01.py", encoding="utf-8").read()
        pa = src.split("def _produce_article", 1)[1].split("# ---- 3. Closing", 1)[0]
        self.assertIn('parts_i = load_article_prompt("intro") if not intros_reused else None', pa)   # 新規生成時は常にpin済みB+E Prompt(shaが違えばPROMPT_SHA_MISMATCHでSTOP)
        self.assertIn('intro=(parts_i or {}).get("sha256")', pa)                                       # Prompt shaがcache keyに入る=旧Prompt生成物はresumeで再利用されない
        self.assertIn("**common", pa)                                                                  # common=module sha(person_block変更も無効化)
        self.assertIn("generate_intros(client, theme, voices", pa)
        rn = open("er121_family_y_runner_01.py", encoding="utf-8").read()
        self.assertIn('fn = getattr(tc, "produce_article", None)', rn)                                 # runner text stage=produce_article単一経路(--regenerate-stage textも同関数)
        with tempfile.TemporaryDirectory() as d:                                                       # Prompt改変はSTOP
            p = os.path.join(d, "x.txt")
            raw = open("er121_prompts/persona_intro_01.txt", "rb").read()
            open(p, "wb").write(raw.replace(PRINCIPLE_HEAD.encode("utf-8"), b"- X"))
            with self.assertRaises(tc.YStop):
                tc.load_article_prompt("intro", path=p)


class XZUnaffected(unittest.TestCase):
    def test_intro_prompt_and_person_block_used_only_by_family_y(self):
        allowed_prefix = ("er121_family_y_", "er110_family_y_redelivery_revision")
        for fn in os.listdir(HERE):
            if not fn.endswith(".py") or fn == os.path.basename(__file__):
                continue
            t = open(fn, encoding="utf-8", errors="ignore").read()
            if "persona_intro_01" in t:
                self.assertTrue(fn.startswith(allowed_prefix), fn)
            if re.match(r"er12[2-9]_|er13\d_", fn) and not fn.startswith("er121_family_y_"):
                self.assertNotIn("generate_intros", t, fn)


if __name__ == "__main__":
    unittest.main()
