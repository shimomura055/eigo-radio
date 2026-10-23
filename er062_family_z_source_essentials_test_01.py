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
    def test_production_seed_equals_t2_trial_seed(self):
        self.assertEqual(_rd(f"{OW_SEED}/seed.json"), _rd(T2_SEED))
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

    def test_r0_byte_identical_to_t2_and_t3_dumps(self):
        prompt, _ = w.build_r0_prompt(self.seed, essentials=self.ess)
        got = w.WRITER_DEVELOPER_MESSAGE + "\n\n---\n\n" + prompt
        self.assertEqual(got, _rd(T2_R0))
        for d in T3:
            self.assertEqual(got, _rd(f"{d}/r0_prompt.txt"), d)

    def _revise_expect(self, dump):
        self.assertIn(self.TRIAL_REV_NAME, dump)
        return dump.replace(self.TRIAL_REV_NAME, self.PROD_REV_NAME)

    def test_r1_r2_match_t3_dumps_except_intended_name_diff(self):
        for d in T3:
            for stage in ("r1", "r2"):
                dump = _rd(f"{d}/{stage}_prompt.txt")
                m = re.match(r"Here is a short story:\n\n(.*)\n\nWithout changing", dump, re.S)
                self.assertTrue(m, (d, stage))
                got = w.build_revise_prompt(m.group(1), "the_open_window", essentials=self.ess)
                self.assertEqual(got, self._revise_expect(dump), (d, stage))
                self.assertNotIn("Nuttel", got.split("Without changing")[1])   # フルネームは指示文に無い

    def test_std_byte_identical_to_t3_dumps(self):
        for d in T3:
            dump = _rd(f"{d}/std_adjust_prompt.txt")
            adv = dump.split("[Story]\n", 1)[1]
            got = w.std_developer() + "\n\n---\n\n" + w.build_std_prompt(adv, essentials=self.ess)
            self.assertEqual(got, dump, d)

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
                                             "support_b1b", "support_a2", "kp_b1b", "kp_a2"))
        self.assertEqual(set(w.STAGE_KEY.values()), {"FAMILY_Z_WRITER_ADV_R0", "FAMILY_Z_WRITER_ADV_R1",
                                                      "FAMILY_Z_WRITER_ADV_R2", "FAMILY_Z_STD_ADJUST"})


class CpChecklistAndPatchTest(unittest.TestCase):
    def test_checklist_generated_from_essentials(self):
        seed = _rj(f"{OW_SEED}/seed.json")
        texts = {"r2": "# T\n\nA.\n\nExtra line here.\n\nRomance at short notice was Vera's speciality.\n",
                 "std_adjust": "# T\n\nA.\n\nVera was good at stories.\n"}
        md = w.build_cp_checklist(seed, "the_open_window", texts)
        for needle in ("ending_reveal", "withhold_until_end", "setup と payoff", "keep_name=Framton", "keep_name=Vera",
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


if __name__ == "__main__":
    unittest.main()
