# -*- coding: utf-8 -*-
"""ASR-PHONETIC-EQUIVALENCE-GENERALIZATION-01 委任_01 回帰/特性test(ASR/TTS/LLM呼出なし、既存転写・既存wav入力のみ、費用JPY0)。

目的:
 (1) Trial隔離プロトタイプ(er068 offline.py)の判定が『Melos専用hardcodeでない』ことを固定する(設計上の担保)。
 (2) 安全条件(否定・数・時制・別名・語欠落・複数差分)を許容にしないことを固定する。
 (3) 『ASRテキストのみ(V1)では末尾切詰を区別できず増分誤PASSになる』という既知の限界(REJECTED理由)を特性として固定し、
     末尾完全性の独立確認(V2)が有る場合のみACCEPTとなることを固定する。
 (4) 減速前後で判定関数が同一入力に同一出力を返す(判定思想が変わらない)ことを固定する。
 (5) Production state保護(telemetry追記なし)・Production経路への未接続(静的)を固定する。

実行: .venv\\Scripts\\python.exe er068_asr_phonetic_equivalence_generalization_01_test_01.py
"""
import glob
import inspect
import os
import re
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import er068_asr_phonetic_equivalence_generalization_01_offline as O  # noqa: E402
import er068_asr_phonetic_equivalence_generalization_01_stateguard as G  # noqa: E402

ROOT = os.path.dirname(os.path.abspath(__file__))


def jd(c, a):
    return O.design_judge(c, a)["verdict"]


class ProductionCharacterization(unittest.TestCase):
    """既存Productionの現行挙動(変更していないことの固定)。Melo/Mello非対称の現状(OPEN-327/330)を記録する。"""

    def test_melo_accepted_mello_not_by_production(self):
        self.assertTrue(O.prod_judge("Melos said.", "Melo said.")["pass"])
        self.assertFalse(O.prod_judge("Melos said.", "Mello said.")["pass"])
        self.assertFalse(O.prod_judge("Melos said.", "Mellow said.")["pass"])

    def test_existing_pattern_a_first_diff_only_hole_is_recorded(self):
        # 既存Pattern Aは最初の食い違い語しか見ない: 後続の無関係な語の置換(cats->dogs)を見逃す。本委任では修正しない(報告のみ)。
        c, a = "The studies suggest cats today.", "The study suggests dogs today."
        # TEST-HYGIENE-02(2026-10-22): この穴はユーザー承認のF1是正(ASR-PHONETIC-EQUIVALENCE-M1-F1-PRODUCTION-WIRING-01
        # 委任_03、2026-10-13: 全差分を点検し、cats->dogsは非PASS必須)でProductionが塞いだ。現行Productionは非PASS。
        self.assertFalse(O.prod_judge(c, a)["pass"])
        self.assertNotIn(jd(c, a), ("PROD_PASS_UNCHANGED", "ACCEPT_M1"))  # 設計判定も受理側へ変えない


class M1Behavior(unittest.TestCase):
    def test_homophone_spellings_get_same_decision_as_pattern_a(self):
        for asr in ("Melo said.", "Mello said.", "Mellow said.", "Mellos said.", "Mellows said."):
            v = jd("Melos said.", asr)
            self.assertIn(v, ("PROD_PASS_UNCHANGED", "ACCEPT_M1"), (asr, v))

    def test_m1_reuses_existing_pattern_a(self):
        r = O.design_judge("Melos said.", "Mello said.")
        self.assertEqual(r["verdict"], "ACCEPT_M1")
        self.assertEqual(r["m1"]["variant_classification"], "CONNECTED_SPEECH_ACCEPT")
        self.assertEqual(r["m1"]["cs_rule"], "Pattern_A_sibilant_sequence")  # 新しい受理基準を作らず既存規則に帰着

    def test_phonetically_different_not_accepted(self):
        for asr in ("Melon said.", "Marcus said.", "Melody said.", "Mellis said.", "Milo said.", "Mel said.", "Melos aid."):
            self.assertNotIn(jd("Melos said.", asr), ("ACCEPT_M1",), asr)

    def test_not_melos_specific_other_names_follow_same_rule(self):
        # Melos以外(CMU収録stemを持つ名前)にも同じ機構で効く。綴りの個別登録はしていない。
        self.assertEqual(jd("Carlos said.", "Karlow said."), "ACCEPT_M1")
        # 委任_02(Opus必須1): Giles/Guile は語頭子音が違う(JH vs G)=音素基準で受理しない(委任_01の綴り基準では受理面にあった)
        self.assertNotEqual(jd("Giles said.", "Guile said."), "ACCEPT_M1")
        self.assertEqual(jd("Lucas said.", "Luka said."), "ACCEPT_M1")

    def test_stem_not_in_cmu_is_not_guessed(self):
        # stemがCMU未収録なら音素を推定せず(G2P未導入)、M1は発火しない(=既存判定のまま)。
        for asr in ("Marcu said.", "Marku said."):
            v = jd("Marcus said.", asr)
            self.assertIn(v, ("PROD_PASS_UNCHANGED", "DEFER_NOT_EXPLAINED", "HR_CANDIDATE_EXPLAINED", "HR_CANDIDATE_RISK_FLAGGED"))

    def test_entity_uses_primary_pronunciation_only(self):
        # 固有名詞は代表発音一致のみ(Tseの実例に基づくProductionの保守基準)。'Tse'/'C'(第2変種のみ一致)をM1で通さない。
        self.assertNotEqual(jd("Kristie Tse links it.", "Christy C links it."), "ACCEPT_M1")
        cls, _ = O.homophone_class("tse", primary_only=True)
        self.assertNotIn("c", cls)

    def test_m1_only_for_uncertain_not_true_content_mismatch(self):
        # 内容語の差(TRUE_CONTENT_MISMATCH)はM1で覆い隠さない
        self.assertNotEqual(jd("The studies suggest a link.", "The studio suggests a link."), "ACCEPT_M1")

    def test_multi_diff_one_homophone_not_masking(self):
        self.assertNotEqual(jd("Melos said hello to Marcus.", "Mello said hello to Mark."), "ACCEPT_M1")
        self.assertNotEqual(jd("Melos said hello to Marcus.", "Mello said hello to Marcos."), "ACCEPT_M1")


class SafetyConditions(unittest.TestCase):
    def test_negation_number_tense_not_accepted(self):
        cases = [("He can't talk to them.", "He can talk to them."), ("They did not stop soon.", "They did stop soon."),
                 ("Sales rose by three percent.", "Sales rose by tree percent."), ("There are six sets.", "There are sick sets."),
                 ("Sales increased slowly.", "Sales decreased slowly.")]
        for c, a in cases:
            self.assertNotEqual(jd(c, a), "ACCEPT_M1", (c, a))
        # 否定の不一致はprotected_check不通過 -> 本機構は適用せず既存判定へ委譲
        self.assertEqual(jd("They did not stop soon.", "They did stop soon."), "DEFER_PROTECTED_FAIL")

    def test_word_dropped_and_wrong_word_not_accepted(self):
        for c, a in (("Melos said hello.", "Melos hello."), ("The bosses said so.", "The said so."),
                     ("The bosses said so.", "The bonus said so."), ("Melos said that he would return.", "Melos said that he would return home.")):
            self.assertNotEqual(jd(c, a), "ACCEPT_M1", (c, a))

    def test_explained_but_not_auto_accepted_goes_to_hr_candidate(self):
        # 音素水準で説明できても自動受理しない(説明付きHR候補)。例: 破裂音/同一子音の連結
        v = jd("last time", "lass time")
        self.assertNotEqual(v, "ACCEPT_M1")


class TailIntegrity(unittest.TestCase):
    TRUNC = "er065_output/short_clip_asr_context_trial_01/synthetic_audio/syn_B1_trunc140.wav"
    INTACT = "er065_output/short_clip_asr_context_trial_01/audio_src/a2_narration/attempts/full_story_part1_c5_attempt1_customadfcf33f.wav"

    def test_v1_text_only_cannot_tell_truncation_known_limit(self):
        # 特性固定(REJECTED理由): 末尾切詰wavでもASR転写はintactと同一('mello said')で、V1(テキストのみ)はACCEPT_M1にする。
        self.assertEqual(jd("Melos said.", "mello said"), "ACCEPT_M1")

    def test_v2_requires_tail_ok(self):
        d = O.design_judge("Melos said.", "mello said")
        self.assertEqual(O.v2_verdict(d, None), "HR_CANDIDATE_TAIL_UNCONFIRMED")
        self.assertEqual(O.v2_verdict(d, {"tail_ok": False}), "HR_CANDIDATE_TAIL_SUSPECT")
        self.assertEqual(O.v2_verdict(d, {"tail_ok": True}), "ACCEPT_M1")
        # ACCEPT_M1以外はV2で何も変わらない
        d2 = O.design_judge("Melos said.", "Melon said.")
        self.assertEqual(O.v2_verdict(d2, {"tail_ok": True}), d2["verdict"])

    @unittest.skipUnless(os.path.exists(os.path.join(ROOT, TRUNC)) and os.path.exists(os.path.join(ROOT, INTACT)), "er065 wav not on disk")
    def test_tail_check_on_existing_wavs(self):
        t = O.tail_integrity(os.path.join(ROOT, self.TRUNC))
        i = O.tail_integrity(os.path.join(ROOT, self.INTACT))
        self.assertIsNotNone(t)
        self.assertIsNotNone(i)
        self.assertFalse(t["tail_ok"])
        self.assertTrue(i["tail_ok"])

    def test_missing_wav_is_unconfirmed(self):
        self.assertIsNone(O.tail_integrity("no/such/file.wav"))
        self.assertIsNone(O.tail_integrity(None))


class SlowdownAndRouteInvariance(unittest.TestCase):
    def test_judgement_is_pure_function_of_text_not_of_route_or_slowdown(self):
        sig = inspect.signature(O.design_judge)
        self.assertEqual(list(sig.parameters), ["canonical", "asr"])  # route/slowdown/role/engine を入力に持たない
        a = O.design_judge("Melos said.", "Mello said.")
        b = O.design_judge("Melos said.", "Mello said.")
        self.assertEqual(a["verdict"], b["verdict"])

    def test_pre_and_post_slowdown_same_transcript_same_verdict(self):
        for asr in ("Mello said", "Mello said.", "Mellow said.", "Melo said."):
            self.assertEqual(jd("Melos said.", asr), jd("Melos said.", asr))
        # ピリオドの有無で判定が変わらない(実データ: 減速後 attempt1 は 'Mello said' ピリオド無し)
        self.assertEqual(jd("Melos said.", "Mello said"), jd("Melos said.", "Mello said."))


class NoHardcodeAndIsolation(unittest.TestCase):
    def test_no_melos_literals_in_mechanism_source(self):
        for fn in (O.homophone_class, O.expected_spellings, O.m1_candidates, O.m1_try, O.design_judge, O.v2_verdict, O.tail_integrity,
                   O._replace_tokens, O.phoneme_ok, O.derived_phone_forms, O.normalize_possessive, O._f1_guard_ok):
            src = inspect.getsource(fn).lower()
            code = "\n".join(l for l in src.splitlines() if not l.strip().startswith("#"))
            code = re.sub(r'""".*?"""', "", code, flags=re.S)
            for w in ("melos", "mello", "mellow", "melo "):
                self.assertNotIn(w, code, f"{fn.__name__} contains literal {w!r}")

    # TEST-HYGIENE-02(2026-10-22): 旧testは「er068_」の部分文字列で全er0*.pyを走査したため、後続taskの研究script
    # (ASR-PHONETIC-EQUIVALENCE-M1-F1の census/benefit/oov_options/eval。Production非接続・27-7の研究script扱い)
    # とtest fileを誤検出していた。禁止したいのはProduction fileによるimportなので、実際のimport文のみを対象にし、
    # test fileと下記の研究scriptを対象外として明示する(新しいProduction側のimportは従来どおり検出される)。
    _RESEARCH_SCRIPTS_ALLOWED_TO_IMPORT = {
        "er075_m1_f1_production_wiring_01_census.py", "er075_m1_f1_production_wiring_01_m1_benefit.py",
        "er075_m1_f1_production_wiring_01_oov_options.py", "er077_m1_oov_multi_pronunciation_01_eval.py",
    }
    _IMPORT_RE = re.compile(r"^\s*(?:import|from)\s+er068_", re.M)

    def test_not_imported_by_production_files(self):
        prod = [p for p in glob.glob(os.path.join(ROOT, "er0*.py"))
                if not os.path.basename(p).startswith(("er068", "er069"))
                and not re.search(r"_test_\d+\.py$", os.path.basename(p))
                and os.path.basename(p) not in self._RESEARCH_SCRIPTS_ALLOWED_TO_IMPORT]
        offenders = []
        for p in prod:
            try:
                with open(p, encoding="utf-8", errors="replace") as fh:
                    txt = fh.read()
            except Exception:
                continue
            if self._IMPORT_RE.search(txt):
                offenders.append(os.path.basename(p))
        self.assertEqual(offenders, [], offenders)

    def test_no_shared_telemetry_append(self):
        before = G.snapshot(ROOT)
        O.design_judge("Melos said.", "Mello said.")
        O.design_judge("The studies suggest a link.", "The study suggests a link.")
        after = G.snapshot(ROOT)
        key = "er021_output/en_asr_semantic_equivalence_production_wiring_01/telemetry.jsonl"
        self.assertEqual(before[key], after[key])

    def test_surface_probe_is_data_driven_not_name_list_of_one(self):
        r = O.surface_expansion_probe()
        self.assertGreaterEqual(r["n_names"], 50)
        names_with_extra = [x["name"] for x in r["rows"] if x["m1_extra_spellings"]]
        self.assertGreater(len(names_with_extra), 5)  # Melos以外にも効く(=Melos専用ではない)
        self.assertTrue(any(n != "Melos" for n in names_with_extra))


class Delegation02PhonemeBasis(unittest.TestCase):
    """委任_02: Opus条件A必須修正1(音素基準)・必須2(受理理由の限定)・推奨(所有格)・F1の回帰test。"""

    def test_opus_examples_not_accepted_phonemes_differ(self):
        # 必須1: Moses/moss(母音・音節)、Hades/haid、Torres/tore、Giles/guile(語頭子音)は音素が異なるため受理しない
        for c, a in (("Moses", "moss"), ("Hades", "haid"), ("Torres", "tore"), ("Giles", "guile")):
            ok, basis, _ = O.phoneme_ok(c.lower(), a.lower(), True)
            self.assertFalse(ok, (c, a))
            self.assertEqual(basis, "phoneme")
            self.assertNotEqual(jd(c + " said.", a.capitalize() + " said."), "ACCEPT_M1", (c, a))

    def test_opus_true_same_phoneme_examples_remain(self):
        # Jones<-Joan / Hayes<-Hey は音素列が真に同一(語末 /Z/ を除いた列)なので残る(Pattern A の本質的帰結。受理面として明示済み)
        for c, a in (("Jones", "joan"), ("Hayes", "hey")):
            ok, basis, rule = O.phoneme_ok(c.lower(), a, True)
            self.assertTrue(ok)
            self.assertEqual(rule, "drop_final_S_or_Z")
        self.assertEqual(jd("Jones said.", "Joan said."), "ACCEPT_M1")
        self.assertEqual(jd("Hayes said.", "Hey said."), "ACCEPT_M1")

    def test_only_one_final_sibilant_is_dropped(self):
        forms = O.derived_phone_forms("moses", True)
        self.assertNotIn(("M", "OW", "Z"), forms)  # 語末 AH S から S を 1 つ除いた形(M OW Z AH)までで、母音まで削る形は作らない
        self.assertNotIn(("M", "AO", "S"), forms)  # moss の音素列は導出されない

    def test_oov_canonical_falls_back_to_spelling_basis_and_is_marked(self):
        ok, basis, _ = O.phoneme_ok("melos", "melo", True)
        self.assertTrue(ok)
        self.assertEqual(basis, "oov_spelling_fallback")  # USER_DECISION_REQUIRED(4): OOV 名のみ綴り基準へ戻す
        r = O.design_judge("Melos said.", "Mello said.")
        self.assertEqual(r["verdict"], "ACCEPT_M1")
        self.assertEqual(r["m1"]["subs"][0]["basis"], "oov_spelling_fallback")

    def test_reason_restriction_excludes_high_similarity_and_numeric(self):
        # 必須2: 歯擦音が続かない文脈(Mello called)の /z/ 欠落を HIGH_SIMILARITY_SAFE 理由で受理しない
        for a in ("Mello called across the hall.", "Mellow called across the hall."):
            self.assertNotEqual(jd("Melos called across the hall.", a), "ACCEPT_M1", a)
        self.assertEqual(jd("Melos said across the hall.", "Mello said across the hall."), "ACCEPT_M1")  # Pattern A(歯擦音が続く)は受理
        self.assertIn("HIGH_SIMILARITY_SAFE", {"HIGH_SIMILARITY_SAFE"} - O.ALLOWED_VARIANT_CLASSES)
        self.assertIn("NUMERIC_EQUIVALENCE_MATCH", {"NUMERIC_EQUIVALENCE_MATCH"} - O.ALLOWED_VARIANT_CLASSES)
        self.assertEqual(O.ALLOWED_VARIANT_CLASSES, {"EXACT_MATCH", "NORMALIZED_MATCH", "CONNECTED_SPEECH_ACCEPT",
                                                     "CONNECTED_SPEECH_PASS_WITH_WARNING", "CONNECTED_SPEECH_RESEGMENTATION"})

    def test_possessive_normalized_and_audit_trail(self):
        self.assertEqual(O.normalize_possessive("Mello's said."), "Mellos said.")
        r = O.design_judge("Melos said.", "Mello's said.")
        self.assertEqual(r["verdict"], "ACCEPT_M1")
        self.assertTrue(r["m1"]["pass_with_warning"])
        self.assertTrue(r["m1"]["possessive_normalized"])
        at = r["m1"]["audit_trail"]
        self.assertEqual(at["original_asr"], "Mello's said.")
        self.assertIn("normalized_asr", at)
        self.assertIn("acceptance_reason", at)

    def test_accept_always_has_audit_trail_and_warning(self):
        r = O.design_judge("Melos said.", "Mello said.")
        self.assertTrue(r["m1"]["pass_with_warning"])
        self.assertEqual(r["m1"]["audit_trail"]["acceptance_reason"], r["m1"]["variant_classification"])

    def test_replaced_sentence_does_not_pass_via_f1_first_diff_only(self):
        # F1(最初の差だけ見る)経由で置換後の文がPASSしない: 置換と無関係な後続差分が残る文は M1 で受理しない
        for c, a in (("Melos said cats today.", "Mello said dogs today."), ("Melos said the studies suggest cats.", "Mello said the study suggests dogs."),
                     ("Melos said hello to Marcus.", "Mello said hello to Mark.")):
            self.assertNotEqual(jd(c, a), "ACCEPT_M1", (c, a))
        self.assertFalse(O._f1_guard_ok("Melos said cats today.", "Melo said dogs today.", {0}))
        self.assertTrue(O._f1_guard_ok("Melos said cats today.", "Melo said cats today.", {0}))

    def test_cmu_known_words_never_use_spelling_basis(self):
        # CMU 収録 canonical(Moses 等)では綴り基準へ戻らない(戻るのは OOV のみ)
        self.assertTrue(O.derived_phone_forms("moses", True))
        self.assertFalse(O.derived_phone_forms("melos", True))


if __name__ == "__main__":
    unittest.main(verbosity=2)
