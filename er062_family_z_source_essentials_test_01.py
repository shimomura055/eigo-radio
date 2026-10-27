# -*- coding: utf-8 -*-
"""FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01 委任_05: 原作忠実性包括対策v1(修正版B全体)のProduction配線test。課金0(mock/ファイルのみ)。

検証: (1)Melos Promptは現行とbyte一致(essentials無し) (2)『開いた窓』R0/R1/R2/StdがTrial dump(T2/T3)とbyte一致
(意図した差分のみ許容) (3)全段・全経路(通常/regenerate/resume)がSeedからessentialsを引数で渡す (4)essentials shaが入力指紋/provenanceに入る
(5)fail-closed(新規Z作品essentials必須、Melos例外) (6)keep_name上書き・STORY_MAIN_CHARACTER・forbidden_names (7)CPチェックリスト機械生成と削除パッチ
(8)新Validator/LLM検査を追加していない(chain stage集合・routing key集合が不変)。
"""
import copy
import hashlib
import json
import os
import re
import shutil
import tempfile
import unittest

import er062_family_z_structure_01 as st
import er062_family_z_writer_01 as w

RUN = "er026_output/family_z_production_e2e_01"
MELOS_SEED = f"{RUN}/melos/seed"
OW_SEED = f"{RUN}/the_open_window/seed"
T2_SEED = "docs/research/FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01/sftrial_seeds/t2/seed.json"
T2_R0 = f"{RUN}/the_open_window/run_sftrial_t2_01/writer/r0_prompt.txt"
T3 = [f"{RUN}/the_open_window/run_sftrial_t3_0{i}/writer" for i in (1, 2)]
# 案A(2026-10-25)込みで実際にLLMへ送られたTrial Phase 2のPrompt dump(Production Promptと完全byte一致する根拠)
P2_DUMP = "er026_output/family_z_dev_trials/fz_essence_01/{story}/{run}/writer/{stage}_prompt.txt"
P2_RUN = {"the_gift_of_the_magi": "p2_s1", "the_open_window": "p2_s1", "the_monkeys_paw": "p2_s1", "the_tell_tale_heart": "1b_s1"}

S = lambda x: hashlib.sha256(x.encode("utf-8")).hexdigest()


def _rj(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def _rd(p):
    with open(p, encoding="utf-8", newline="") as f:
        return f.read().replace("\r\n", "\n")


def _story(n, words):
    return "# T\n\n" + "\n\n".join(" ".join([f"word{i}"] * words) for i in range(n)) + "\n"


class MelosUnchangedTest(unittest.TestCase):
    """Melos(essentials無し)のPromptは、本変更前のProduction現行とbyte一致(HEAD da316da5d時点で算出したsha256を固定)。"""
    GOLD = {"r0": "e97fe88a5644bca909e20349973585881ce6f4feb3e13df92c3367cdadace762",
            "revise": "34fa8fb1f8eacd8d79213293017cd96f782a6a8600270dffd7523be2f04965bd",
            "std": "4571da377c32fd8fb0d9d1ee1b3eaa9c11da27854110be4163dba26f263cc009"}

    def test_melos_seed_has_no_essentials(self):
        seed = _rj(f"{MELOS_SEED}/seed.json")
        self.assertNotIn("source_essentials", seed)
        self.assertIsNone(w.build_essentials(seed))
        self.assertEqual(w.validate_source_essentials(seed, "melos", MELOS_SEED), {"present": False, "exempt": True})

    def test_melos_prompts_byte_identical_to_current_production(self):
        seed = _rj(f"{MELOS_SEED}/seed.json")
        self.assertEqual(S(w.build_r0_prompt(seed)[0]), self.GOLD["r0"])
        self.assertEqual(S(w.build_r0_prompt(seed, essentials=w.build_essentials(seed))[0]), self.GOLD["r0"])
        self.assertEqual(S(w.build_revise_prompt("BODY")), self.GOLD["revise"])
        self.assertEqual(S(w.build_revise_prompt("BODY", "melos", essentials=None)), self.GOLD["revise"])
        self.assertEqual(S(w.build_std_prompt(_story(8, 60))), self.GOLD["std"])
        self.assertEqual(S(w.build_std_prompt(_story(8, 60), essentials=None)), self.GOLD["std"])

    def test_melos_main_character_and_lint_unchanged(self):
        self.assertEqual(w.STORY_MAIN_CHARACTER["melos"], "Melos")
        self.assertIn("セリヌンティウス", st.STORY_LINT_CONFIG["melos"]["forbidden_names"])

    def test_melos_chain_fingerprint_unchanged(self):
        """essentials無し(Melos): 入力指紋・provenanceは従来と同一(追加キー無し)。"""
        with tempfile.TemporaryDirectory() as d:
            w.run_writer_chain(w.LLM(w.MockClient(None), w.Budget(1e9)), d, MELOS_SEED, stages=("r0", "r1", "r2", "std_adjust"))
            prov = _rj(f"{d}/writer/provenance.json")
            ch = {e["stage"]: e for e in prov["chain"]}
            self.assertEqual(ch["r0"]["input_sha256"], prov["seed_sha256"])
            self.assertEqual(ch["r1"]["input_sha256"], ch["r0"]["output_sha256"])
            self.assertNotIn("source_essentials_sha256", prov)
            for e in ch.values():
                self.assertNotIn("essentials_sha256", e)
            self.assertIsNone(w.write_cp_checklist(d, _rj(f"{MELOS_SEED}/seed.json"), "melos"))
            self.assertFalse(os.path.exists(f"{d}/writer/cp_checklist.md"))


class ProductionSeedTest(unittest.TestCase):
    def test_production_seed_equals_t2_trial_seed_plus_narration_voice(self):
        """案A導入後: Production Seed = T2 Trial Seed + source_essentials.narration_voice 1キーのみ(旧: byte一致)。"""
        prod, t2 = _rj(f"{OW_SEED}/seed.json"), _rj(T2_SEED)
        nv = prod["source_essentials"].pop("narration_voice")
        self.assertTrue(nv.startswith("The story is told in the third person by an outside narrator"))
        self.assertEqual(prod, t2)
        prov = _rj(f"{OW_SEED}/SEED_PROVENANCE.json")
        with open(f"{OW_SEED}/seed.json", "rb") as f:
            self.assertEqual(prov["files"]["seed.json"]["sha256"], hashlib.sha256(f.read()).hexdigest())
        self.assertTrue(os.path.exists(f"{OW_SEED}/seed_STALE_20261023.json"))

    def test_seed_validates_and_quote_matches_last_paragraph(self):
        seed = _rj(f"{OW_SEED}/seed.json")
        r = w.validate_source_essentials(seed, "the_open_window", OW_SEED)
        self.assertTrue(r["present"] and r["source_quote_checked_vs_last_paragraph"])
        self.assertEqual(r["keep_names"], ["Framton", "Vera"])
        self.assertLessEqual(r["items"], w.ESSENTIALS_MAX_ITEMS)
        # 旧矛盾の除去: conversion_planは原作最終文を「説明禁止」の対象外と明記、少女の名前省略はdiscardedに無い
        cp = seed["conversion_plan"]
        self.assertIn("is not such an explanation", cp)
        self.assertNotIn("the girl's name", " ".join(seed["discarded_elements"]))

    def test_new_zfiction_story_without_essentials_is_rejected_fail_closed(self):
        seed = copy.deepcopy(_rj(f"{OW_SEED}/seed.json"))
        del seed["source_essentials"]
        with self.assertRaises(w.FamilyZSeedEssentialsStop):
            w.validate_source_essentials(seed, "the_open_window", OW_SEED)
        with self.assertRaises(w.FamilyZSeedEssentialsStop):
            w.validate_source_essentials(seed, "some_new_story", None)
        # run_writer_chainも同じ(Seed承認を通らない=LLMを呼ぶ前にSTOP)
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as sd:
            self._copy_seed(sd, seed)
            llm = w.LLM(w.MockClient(None), w.Budget(1e9))
            with self.assertRaises(w.FamilyZSeedEssentialsStop):
                w.run_writer_chain(llm, d, sd, stages=("r0",), story_key="the_open_window")
            self.assertEqual(len(llm.client.responses.calls), 0)

    @staticmethod
    def _copy_seed(sd, seed):
        shutil.copy(f"{OW_SEED}/primary_text_excerpt.md", f"{sd}/primary_text_excerpt.md")
        with open(f"{sd}/seed.json", "w", encoding="utf-8") as f:
            json.dump(seed, f, ensure_ascii=False, indent=1)
        sha = hashlib.sha256(open(f"{sd}/seed.json", "rb").read()).hexdigest()
        with open(f"{sd}/SEED_PROVENANCE.json", "w", encoding="utf-8") as f:
            json.dump({"files": {"seed.json": {"sha256": sha}}}, f)

    def test_schema_violations_rejected(self):
        base = _rj(f"{OW_SEED}/seed.json")
        cases = {}
        c = copy.deepcopy(base); c["source_essentials"]["ending_reveal"]["source_quote"] = "Not in the last paragraph at all."
        cases["quote_not_in_last_paragraph"] = c
        c = copy.deepcopy(base); del c["source_essentials"]["ending_reveal"]["withhold_until_end"]
        cases["withhold_missing"] = c
        c = copy.deepcopy(base); c["source_essentials"]["free_to_cut"] = []
        cases["free_to_cut_missing"] = c
        c = copy.deepcopy(base); c["source_essentials"]["key_causality"] = ["a", "b", "c", "d"]
        cases["over_5_items"] = c
        c = copy.deepcopy(base); c["source_essentials"]["key_roles"][0].pop("name")
        cases["keep_name_without_name"] = c
        for k, seed in cases.items():
            with self.subTest(k), self.assertRaises(w.FamilyZSeedEssentialsStop):
                w.validate_source_essentials(seed, "the_open_window", OW_SEED)


class TrialPromptMatchTest(unittest.TestCase):
    """配線後の『開いた窓』R0/R1/R2/StdがT2/T3のdumpとbyte一致(意図した差分のみ許容)。"""
    # 意図した差分(列挙): (1)REVISE side: "Framton Nuttel"->"Framton"(STORY_MAIN_CHARACTER修正、Opus論点4 must-fix)
    #                    (2)REVISE side: 一方の名前のみ節の追加(Opus should-fix)。R0とStdはdumpとbyte一致(差分0)。
    TRIAL_REV_NAME = ('and only Framton Nuttel and the people marked "keep the name" in the Must-keep section below may have a '
                      'personal name (keep those names as they are; use no other personal names).')
    PROD_REV_NAME = ('and only Framton and the people marked "keep the name" in the Must-keep section below may have a '
                     'personal name (keep those names as they are; use no other personal names; use only one of the two names '
                     '(first or last) of a person, consistently).')

    def setUp(self):
        self.seed = _rj(f"{OW_SEED}/seed.json")
        self.ess = w.build_essentials(self.seed)

    # 案A導入後の意図した差分(2点のみ): (1)導入2行の直後にNarration行が1行入る (2)REVISEの"in third person, "が欄参照句に置換される
    INTRO = ("These are the points that make this story work. Keep their meaning (your own words are fine); "
             "everything not listed here may be shortened or reshaped.\n")

    def _narr_expect(self, dump, revise=False):
        self.assertIn(self.INTRO, dump)
        out = dump.replace(self.INTRO, self.INTRO + w._NARR_LINE.format(voice=self.ess.ess["narration_voice"].strip()) + "\n", 1)
        if revise:
            self.assertIn(w._REVISE_THIRD, out)
            out = out.replace(w._REVISE_THIRD, w._REVISE_NARR, 1)
        return out

    def test_r0_matches_t2_and_t3_dumps_except_narration_line(self):
        prompt, _ = w.build_r0_prompt(self.seed, essentials=self.ess)
        got = w.WRITER_DEVELOPER_MESSAGE + "\n\n---\n\n" + prompt
        self.assertEqual(got, self._narr_expect(_rd(T2_R0)))
        for d in T3:
            self.assertEqual(got, self._narr_expect(_rd(f"{d}/r0_prompt.txt")), d)

    def _revise_expect(self, dump):
        self.assertIn(self.TRIAL_REV_NAME, dump)
        return self._narr_expect(dump.replace(self.TRIAL_REV_NAME, self.PROD_REV_NAME), revise=True)

    def test_r1_r2_match_t3_dumps_except_intended_name_diff(self):
        for d in T3:
            for stage in ("r1", "r2"):
                dump = _rd(f"{d}/{stage}_prompt.txt")
                m = re.match(r"Here is a short story:\n\n(.*)\n\nWithout changing", dump, re.S)
                self.assertTrue(m, (d, stage))
                got = w.build_revise_prompt(m.group(1), "the_open_window", essentials=self.ess)
                self.assertEqual(got, self._revise_expect(dump), (d, stage))
                self.assertNotIn("Nuttel", got.split("Without changing")[1])   # フルネームは指示文に無い

    def test_std_matches_t3_dumps_except_narration_line(self):
        for d in T3:
            dump = _rd(f"{d}/std_adjust_prompt.txt")
            adv = dump.split("[Story]\n", 1)[1]
            got = w.std_developer() + "\n\n---\n\n" + w.build_std_prompt(adv, essentials=self.ess)
            self.assertEqual(got, self._narr_expect(dump), d)

    def test_std_prompt_states_final_reveal_is_not_a_closing_summary(self):
        p = w.build_std_prompt(_story(8, 60), essentials=self.ess)
        self.assertIn("so the rules against summaries and new explanations do not apply to it", p)
        self.assertIn("Romance at short notice was her speciality.", p)
        self.assertNotIn("Not before the ending", p)      # Stdは結末前の示唆禁止行を持たない(Trial文面どおり)

    def test_keep_name_overrides_all_three_name_constraints(self):
        r0, _ = w.build_r0_prompt(self.seed, essentials=self.ess)
        self.assertNotIn(w._R0_NAME_SENT, r0)
        self.assertNotIn(w._R0_PRES_LAST, r0)
        self.assertIn('marked "keep the name"', r0)
        rev = w.build_revise_prompt("BODY", "the_open_window", essentials=self.ess)
        self.assertNotIn("and only Framton may have a personal name.", rev)
        # 作品名は共通Prompt定数に無い
        for blk in (w.R0_BLOCK_COMMON, w.R0_BLOCK_PRESERVATION, w.REVISE_USER_TMPL, w.STD_PROMPT_TAIL, w._R0_NAME_SENT_KEEP,
                    w._REVISE_NAME_SENT_KEEP):
            self.assertNotIn("Vera", blk)
            self.assertNotIn("Framton", blk)

    def test_essentials_without_keep_name_leaves_name_sentences_unchanged(self):
        seed = copy.deepcopy(self.seed)
        for r in seed["source_essentials"]["key_roles"]:
            r["keep_name"] = False
        ess = w.build_essentials(seed)
        r0, _ = w.build_r0_prompt(seed, essentials=ess)
        self.assertIn(w._R0_NAME_SENT, r0)
        self.assertIn(w._R0_PRES_LAST, r0)
        self.assertIn("and only Framton may have a personal name.", w.build_revise_prompt("B", "the_open_window", essentials=ess))


class NamesTest(unittest.TestCase):
    def test_main_character_is_framton_only(self):
        self.assertEqual(w.STORY_MAIN_CHARACTER["the_open_window"], "Framton")

    def test_keep_name_people_not_in_forbidden_names(self):
        seed = _rj(f"{OW_SEED}/seed.json")
        forb = st.STORY_LINT_CONFIG["the_open_window"]["forbidden_names"]
        keeps = [r["name"] for r in seed["source_essentials"]["key_roles"] if r.get("keep_name")]
        kana = {"Vera": ["ヴェラ", "ベラ", "ヴィラ"], "Framton": ["フラムトン", "フレイムトン", "フラントン"]}
        for n in keeps:
            for f in forb:
                self.assertNotIn(n.lower(), f.lower())
                for k in kana.get(n, []):
                    self.assertNotIn(k, f)
        # 他の非keep人名は引き続き禁止(Preview/Commentに出さない)
        for nm in ("Sappleton", "Ronnie", "サプルトン", "ロニー"):
            self.assertIn(nm, forb)
        # lint: 日本語Preview/Commentで「ヴェラ」が出ても名前禁止でblockingしない
        self.assertEqual(st.lint_support_text("ヴェラは落ち着いて話します。", "ja", "the_open_window"), [])
        self.assertTrue(any(c.startswith("FORBIDDEN_NAME") for c in
                            st.lint_support_text("サプルトン夫人は話します。", "ja", "the_open_window")))


class PropagationAndFingerprintTest(unittest.TestCase):
    """全段・全経路(通常/regenerate/resume)がSeedからessentialsを引数で渡し、shaを入力指紋・provenanceへ組込む。"""

    def _chain(self, d, sd=OW_SEED, **kw):
        llm = w.LLM(w.MockClient(None), w.Budget(1e9))
        return w.run_writer_chain(llm, d, sd, story_key="the_open_window", **kw), llm

    def _spy(self):
        calls = []
        o = (w.build_r0_prompt, w.build_revise_prompt, w.build_std_prompt)

        def r0(seed, story_type="literature", essentials=None):
            calls.append(("r0", essentials)); return o[0](seed, story_type, essentials)

        def rv(body, story_key="melos", essentials=None):
            calls.append(("rv", essentials)); return o[1](body, story_key, essentials)

        def sd(adv, essentials=None):
            calls.append(("std", essentials)); return o[2](adv, essentials)
        w.build_r0_prompt, w.build_revise_prompt, w.build_std_prompt = r0, rv, sd
        self.addCleanup(lambda: (setattr(w, "build_r0_prompt", o[0]), setattr(w, "build_revise_prompt", o[1]),
                                 setattr(w, "build_std_prompt", o[2])))
        return calls

    def test_every_stage_receives_essentials_incl_regenerate_and_partial_runs(self):
        calls = self._spy()
        ess_sha = w.build_essentials(_rj(f"{OW_SEED}/seed.json")).sha256
        with tempfile.TemporaryDirectory() as d:
            self._chain(d, stages=("r0", "r1", "r2", "std_adjust"))
            self.assertEqual([c[0] for c in calls], ["r0", "rv", "rv", "std"])
            self.assertTrue(all(c[1] is not None and c[1].sha256 == ess_sha for c in calls))
            calls.clear()
            self._chain(d, stages=("r1",), regenerate_stage="r1")                # regenerate経路(子孫はstale化=明示再生成のみ)
            self.assertEqual([c[0] for c in calls], ["rv"])
            self.assertIsNotNone(calls[0][1])
            calls.clear()
            self._chain(d, stages=("r2",), regenerate_stage="r2")
            self.assertEqual([c[0] for c in calls], ["rv"])
            self.assertIsNotNone(calls[0][1])
            calls.clear()
            self._chain(d, stages=("std_adjust",), regenerate_stage="std_adjust")  # std単独regenerate(runnerのstage_std_adjust相当)
            self.assertEqual([c[0] for c in calls], ["std"])
            self.assertIsNotNone(calls[0][1])

    def test_essentials_sha_in_input_fingerprint_and_provenance(self):
        with tempfile.TemporaryDirectory() as d:
            self._chain(d, stages=("r0", "r1", "r2", "std_adjust"))
            prov = _rj(f"{d}/writer/provenance.json")
            ess = w.build_essentials(_rj(f"{OW_SEED}/seed.json"))
            self.assertEqual(prov["source_essentials_sha256"], ess.sha256)
            ch = {e["stage"]: e for e in prov["chain"]}
            prev = prov["seed_sha256"]
            for s in w.CHAIN_STAGES:
                self.assertEqual(ch[s]["essentials_sha256"], ess.sha256, s)
                self.assertEqual(ch[s]["input_sha256"], w.sha(prev + "\n##ESSENTIALS##" + ess.sha256), s)
                prev = ch[s]["output_sha256"]
            for s in ("r0", "r1", "r2", "std_adjust"):                          # prompt_sha256はPrompt dumpと一致
                dump = _rd(f"{d}/writer/{s}_prompt.txt")
                full = ("\n\n---\n\n" + dump) if s in ("r1", "r2") else dump   # devの無い段のprompt_sha256 = "" + sep + user
                self.assertEqual(ch[s]["prompt_sha256"], w.sha(full), s)

    def test_resume_reuses_with_zero_calls_and_changed_essentials_stops(self):
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as sd:
            self._chain(d, stages=("r0", "r1", "r2"))
            _res, llm = self._chain(d, stages=("r0", "r1", "r2"))               # resume: 再生成0
            self.assertEqual(len(llm.client.responses.calls), 0)
            self.assertTrue(all(v["status"] == "reused" for v in _res["stages"].values()))
            # essentialsだけ変えたSeed(別seed sha)で同じrun dirを再開 -> 旧本文を黙って再利用しない(Seed sha不一致でSTOP)
            seed = copy.deepcopy(_rj(f"{OW_SEED}/seed.json"))
            seed["source_essentials"]["free_to_cut"].append("an extra item")
            ProductionSeedTest._copy_seed(sd, seed)
            with self.assertRaises(w.FamilyZProvenanceMismatchStop):
                w.run_writer_chain(w.LLM(w.MockClient(None), w.Budget(1e9)), d, sd, stages=("r0",), story_key="the_open_window")

    def test_essentials_fingerprint_differs_from_plain_seed_chain(self):
        """essentials sha自体が指紋に入る(Seed shaが同一でもessentials shaが違えばinput_sha256が変わる)。"""
        seed = _rj(f"{OW_SEED}/seed.json")
        a = w.build_essentials(seed).sha256
        seed2 = copy.deepcopy(seed)
        seed2["source_essentials"]["free_to_cut"].append("x")
        b = w.build_essentials(seed2).sha256
        self.assertNotEqual(w.sha("P\n##ESSENTIALS##" + a), w.sha("P\n##ESSENTIALS##" + b))
        self.assertNotEqual(a, b)

    def test_default_builders_do_not_read_essentials_implicitly(self):
        """未承認機能の隠れON無し: essentials引数を渡さなければ従来出力(flag/環境変数/グローバルでONにできない)。"""
        seed = _rj(f"{OW_SEED}/seed.json")
        p, _ = w.build_r0_prompt(seed)
        self.assertNotIn("Must-keep", p)
        self.assertNotIn("Must-keep", w.build_revise_prompt("B", "the_open_window"))
        self.assertNotIn("Must-keep", w.build_std_prompt(_story(8, 60)))

    def test_no_new_stage_or_validator_added(self):
        self.assertEqual(w.CHAIN_STAGES, ("r0", "r1", "r2", "std_adjust"))
        self.assertEqual(w.ALL_STAGE_NAMES, ("r0", "r1", "r2", "std_adjust", "plan_b1b", "plan_a2",
                                             "support_b1b", "support_a2", "kp_b1b", "kp_a2",
                                             "part2_cand_b1b", "part2_b1b", "part2_cand_a2", "part2_a2"))   # Part 2(文法)のstageを両level分(PART2-GRAMMAR委任_03 / GRAMMAR-PREGEN-ALL-LEVELS-01 委任_03)。CHAIN_STAGES/STAGE_KEYは不変
        self.assertEqual(set(w.STAGE_KEY.values()), {"FAMILY_Z_WRITER_ADV_R0", "FAMILY_Z_WRITER_ADV_R1",
                                                      "FAMILY_Z_WRITER_ADV_R2", "FAMILY_Z_STD_ADJUST"})


class CpChecklistAndPatchTest(unittest.TestCase):
    def test_checklist_generated_from_essentials(self):
        seed = _rj(f"{OW_SEED}/seed.json")
        texts = {"r2": "# T\n\nA.\n\nExtra line here.\n\nRomance at short notice was Vera's speciality.\n",
                 "std_adjust": "# T\n\nA.\n\nVera was good at stories.\n"}
        md = w.build_cp_checklist(seed, "the_open_window", texts)
        for needle in ("narration", "ending_reveal", "withhold_until_end", "setup と payoff", "keep_name=Framton", "keep_name=Vera",
                       "key_causality", "本文の該当引用(r2)", "本文の該当引用(std_adjust)", "処置規則", "重大", "軽微",
                       "Romance at short notice was her speciality.", "Extra line here."):
            self.assertIn(needle, md, needle)
        self.assertEqual(w.build_cp_checklist(_rj(f"{MELOS_SEED}/seed.json"), "melos", texts), "")

    def test_deletion_patch_exact_and_recorded(self):
        with tempfile.TemporaryDirectory() as d:
            uniq = lambda kw: "# T\n\nAlpha one two three.\n\nBeta four five six.\n\nGamma seven eight nine.\n"
            llm = w.LLM(w.MockClient(uniq), w.Budget(1e9))
            w.run_writer_chain(llm, d, OW_SEED, stages=("r0", "r1", "r2"), story_key="the_open_window")
            para = "Beta four five six."
            with self.assertRaises(st.FamilyZStop):
                w.apply_cp_deletion_patch(d, "r2", "no such text zzz", "t")
            res = w.apply_cp_deletion_patch(d, "r2", para.strip(), "結末直前の付加文(テスト)")
            self.assertNotEqual(res["old_sha256"], res["new_sha256"])
            prov = _rj(f"{d}/writer/provenance.json")
            e = {x["stage"]: x for x in prov["chain"]}["r2"]
            self.assertEqual(e["output_sha256"], res["new_sha256"])
            self.assertEqual(e["cp_patches"][0]["removed_text"], para.strip())
            self.assertEqual(w.file_sha(f"{d}/writer/r2.md"), res["new_sha256"])
            # パッチ後もresumeで再生成0(親sha整合)
            llm2 = w.LLM(w.MockClient(None), w.Budget(1e9))
            out = w.run_writer_chain(llm2, d, OW_SEED, stages=("r0", "r1", "r2"), story_key="the_open_window")
            self.assertEqual(len(llm2.client.responses.calls), 0)
            self.assertTrue(all(v["status"] == "reused" for v in out["stages"].values()))


def _prompt_for(story, stage, body=None):
    """Production経路のbuilderで『stage dumpと同じ形式』のPromptを組む(dev + 区切り + user)。"""
    d = f"{RUN}/{story}/seed"
    seed = _rj(f"{d}/seed.json")
    ess = w.build_essentials(seed)
    if stage == "r0":
        return w.WRITER_DEVELOPER_MESSAGE + "\n\n---\n\n" + w.build_r0_prompt(seed, essentials=ess)[0]
    if stage in ("r1", "r2"):
        return w.build_revise_prompt(body, story, essentials=ess)
    return w.std_developer() + "\n\n---\n\n" + w.build_std_prompt(body, essentials=ess)


class NarrationVoiceWiringTest(unittest.TestCase):
    """案A(2026-10-25 APPROVED_FOR_PRODUCTION): narration_voiceの配線。課金0。"""
    STORIES = ("the_tell_tale_heart", "the_gift_of_the_magi", "the_open_window", "the_monkeys_paw", "after_twenty_years")

    def _seed(self, story):
        return _rj(f"{RUN}/{story}/seed/seed.json")

    def test_narration_line_position_once_before_ending_and_key_people(self):
        for story in self.STORIES:
            ess = w.build_essentials(self._seed(story))
            for blk in (ess.block_full, ess.block_std):
                lines = blk.split("\n")
                idx = [i for i, l in enumerate(lines) if l.startswith("- Narration: ")]
                self.assertEqual(idx, [2], story)                       # 導入2行(見出し+説明)の直後
                self.assertTrue(lines[3].startswith("- Ending (required)"), story)
                self.assertLess(idx[0], next(i for i, l in enumerate(lines) if l.startswith("- Key people:")))

    def test_std_prompt_carries_narration_line(self):
        for story in self.STORIES:
            ess = w.build_essentials(self._seed(story))
            p = w.build_std_prompt(_story(8, 60), essentials=ess)
            self.assertEqual(p.count("- Narration: "), 1, story)

    def test_revise_replaces_third_person_when_essentials_exist(self):
        for story in self.STORIES:
            ess = w.build_essentials(self._seed(story))
            p = w.build_revise_prompt("BODY", story, essentials=ess)
            self.assertNotIn("in third person", p, story)
            self.assertEqual(p.count("in the narration described in the Must-keep section below,"), 1, story)
            self.assertEqual(p.count("- Narration: "), 1, story)
        # essentials無し(Melos専用経路)は従来の文言のまま
        self.assertIn("in third person, ", w.build_revise_prompt("BODY", "melos", essentials=None))

    def test_r0_prompts_have_narration_for_essentials_works(self):
        for story in self.STORIES:
            seed = self._seed(story)
            p = w.build_r0_prompt(seed, essentials=w.build_essentials(seed))[0]
            self.assertEqual(p.count("- Narration: "), 1, story)

    def test_narration_voice_required_fail_closed(self):
        base = self._seed("the_tell_tale_heart")
        for bad in (None, "", "   ", 123, ["x"]):
            seed = copy.deepcopy(base)
            if bad is None:
                del seed["source_essentials"]["narration_voice"]
            else:
                seed["source_essentials"]["narration_voice"] = bad
            with self.subTest(bad=bad):
                with self.assertRaises(w.FamilyZSeedEssentialsStop) as cm:
                    w.validate_source_essentials(seed, "the_tell_tale_heart", f"{RUN}/the_tell_tale_heart/seed")
                self.assertIn("narration_voice", str(cm.exception))
                with self.assertRaises(w.FamilyZSeedEssentialsStop) as cm2:
                    w.Essentials(seed["source_essentials"])
                self.assertIn("narration_voice", str(cm2.exception))
                with self.assertRaises(w.FamilyZSeedEssentialsStop):
                    w.build_essentials(seed)
        self.assertEqual(w.validate_source_essentials(_rj(f"{MELOS_SEED}/seed.json"), "melos", MELOS_SEED), {"present": False, "exempt": True})

    def test_validate_returns_narration_voice_for_stage_log(self):
        r = w.validate_source_essentials(self._seed("the_tell_tale_heart"), "the_tell_tale_heart", f"{RUN}/the_tell_tale_heart/seed")
        self.assertTrue(r["narration_voice"].startswith("The narrator speaks as 'I'"))
        self.assertLessEqual(r["items"], w.ESSENTIALS_MAX_ITEMS)             # narration_voiceは5件上限に数えない

    def test_all_stage_prompts_dumped_with_narration_incl_regenerate_and_partial(self):
        """通常/regenerate/部分runのいずれでも、各stage Prompt dumpに Narration行(R1/R2は置換句)が入る。"""
        story = "the_tell_tale_heart"
        sd = f"{RUN}/{story}/seed"
        with tempfile.TemporaryDirectory() as d:
            def chain(**kw):
                return w.run_writer_chain(w.LLM(w.MockClient(None), w.Budget(1e9)), d, sd, story_key=story, **kw)
            chain(stages=("r0", "r1", "r2", "std_adjust"))
            for stage in ("r0", "r1", "r2", "std_adjust"):
                self.assertEqual(_rd(f"{d}/writer/{stage}_prompt.txt").count("- Narration: "), 1, stage)
            for stage in ("r1", "r2"):
                t = _rd(f"{d}/writer/{stage}_prompt.txt")
                self.assertIn("in the narration described in the Must-keep section below,", t)
                self.assertNotIn("in third person", t)
            chain(stages=("r1",), regenerate_stage="r1")
            self.assertEqual(_rd(f"{d}/writer/r1_prompt.txt").count("- Narration: "), 1)
            chain(stages=("r2",), regenerate_stage="r2")
            self.assertEqual(_rd(f"{d}/writer/r2_prompt.txt").count("- Narration: "), 1)
            chain(stages=("std_adjust",), regenerate_stage="std_adjust")
            self.assertEqual(_rd(f"{d}/writer/std_adjust_prompt.txt").count("- Narration: "), 1)

    def test_narration_voice_change_stops_resume(self):
        story = "the_tell_tale_heart"
        sd0 = f"{RUN}/{story}/seed"
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as sd:
            w.run_writer_chain(w.LLM(w.MockClient(None), w.Budget(1e9)), d, sd0, stages=("r0",), story_key=story)
            seed = copy.deepcopy(self._seed(story))
            seed["source_essentials"]["narration_voice"] += " Changed."
            shutil.copy(f"{sd0}/primary_text_excerpt.md", f"{sd}/primary_text_excerpt.md")
            with open(f"{sd}/seed.json", "w", encoding="utf-8") as f:
                json.dump(seed, f, ensure_ascii=False, indent=1)
            sha = hashlib.sha256(open(f"{sd}/seed.json", "rb").read()).hexdigest()
            with open(f"{sd}/SEED_PROVENANCE.json", "w", encoding="utf-8") as f:
                json.dump({"files": {"seed.json": {"sha256": sha}}}, f)
            with self.assertRaises(w.FamilyZProvenanceMismatchStop):
                w.run_writer_chain(w.LLM(w.MockClient(None), w.Budget(1e9)), d, sd, stages=("r0",), story_key=story)

    def test_in_third_person_remains_only_in_revise_base_template(self):
        """旧固定文言の撤去確認: 『in third person』はREVISE_USER_TMPLのベース文言1か所(essentials無し=Melos専用経路)と置換元定数のみ。"""
        src = _rd("er062_family_z_writer_01.py")
        self.assertEqual(w.REVISE_USER_TMPL.count("in third person"), 1)
        self.assertEqual(w.ESSENTIALS_EXEMPT_STORIES, ("melos",))          # 推奨1: Melos以外へ広がらないことを固定
        self.assertIn("assert _REVISE_THIRD in tmpl", src)
        hits = [l.strip() for l in src.split("\n") if "in third person" in l]
        self.assertTrue(all(("_REVISE_THIRD" in h or "Keep it at a natural upper-intermediate" in h or h.startswith("#")) for h in hits), hits)

    def test_seed_narration_rules_structure(self):
        """記入規則の軽い構造検査(本文Validatorではない): 非空・第1文に自称・free_to_cutに丸ごと入っていない。"""
        for story in self.STORIES:
            e = self._seed(story)["source_essentials"]
            nv = e["narration_voice"]
            self.assertTrue(nv.strip(), story)
            self.assertTrue(("told in the third person by an outside narrator" in nv.split(".")[0]) or ("speaks as 'I'" in nv.split(";")[0]), story)
            self.assertFalse(any(nv in f or f in nv for f in e["free_to_cut"]), story)

    def test_cp_checklist_has_narration_row_severe_and_treatment_rule(self):
        seed = self._seed("the_tell_tale_heart")
        md = w.build_cp_checklist(seed, "the_tell_tale_heart", {"r2": "# T\n\nI am calm.\n\nYou see.\n"})
        row = [l for l in md.split("\n") if "narration(人称・語り手の立場が各stageで保たれている)" in l]
        self.assertEqual(len(row), 1)
        self.assertIn("| 重大 |", row[0])
        self.assertIn(seed["source_essentials"]["narration_voice"].replace("|", "/"), row[0])
        self.assertIn("narration(人称・視点・語り手の立場の変更)", w.CP_TREATMENT_RULE)    # (A)重大の列挙とW6の整合(Opus必須修正4)

    def test_no_dev_runner_reference_from_production(self):
        """Production本体はDEV/Trial runnerを参照しない(Opus確認事項: 本番→DEV参照0件)。"""
        for f in ("er062_family_z_writer_01.py", "er026_family_z_fiction_production_runner_01.py", "er062_family_z_structure_01.py"):
            self.assertNotIn("fz_essence_dev_runner", _rd(f), f)

    def test_historical_dev_runner_fail_fast_guard(self):
        """DEV runnerは案A昇格後はimport時に停止する(二重注入防止、Opus必須修正5)。"""
        import subprocess, sys
        r = subprocess.run([sys.executable, "-c",
                            "import sys; sys.path.insert(0,'docs/research/FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01'); import fz_essence_dev_runner_01"],
                           capture_output=True, encoding="utf-8", errors="replace", env={**os.environ, "PYTHONIOENCODING": "utf-8"})
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("HISTORICAL_RUNNER", (r.stderr or "") + (r.stdout or ""))

    def test_four_works_prompts_match_trial_dumps_byte_for_byte(self):
        """Production builder(実Seed)のR0/R1/R2/Std PromptがTrialが実際に送信したPrompt dumpとbyte一致(Trial結果再利用の根拠)。
        賢者/開いた窓/猿の手=p2_s1、告げ口心臓=1b_s1。二十年後はTrial dumpが無く構造検査のみ(上のtest)。"""
        for story, run in P2_RUN.items():
            dumps = {s_: _rd(P2_DUMP.format(story=story, run=run, stage=s_)) for s_ in ("r0", "r1", "r2", "std_adjust")}
            self.assertEqual(_prompt_for(story, "r0"), dumps["r0"], (story, "r0"))
            for stage in ("r1", "r2"):
                m = re.match(r"Here is a short story:\n\n(.*)\n\nWithout changing", dumps[stage], re.S)
                self.assertTrue(m, (story, stage))
                self.assertEqual(_prompt_for(story, stage, m.group(1)), dumps[stage], (story, stage))
            adv = dumps["std_adjust"].split("[Story]\n", 1)[1]
            self.assertEqual(_prompt_for(story, "std_adjust", adv), dumps["std_adjust"], (story, "std_adjust"))


if __name__ == "__main__":
    unittest.main()
