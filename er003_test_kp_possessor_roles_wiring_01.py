# -*- coding: utf-8 -*-
"""FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_20: 課題②(見出し語の所有格一般化=possessor_roles + role条件付き受理 + revertのみ後処理)と
A-1(参照語の不定化)のX/Z Production配線test(API 0・オフライン)。WIRING_DESIGN_05.md §8 WC-07のtest計画を実装する。
正常/境界/revert/role不明時無変更/its維持/A-1同居/legacy(A/B/C)非適用/reason保持/merge passthrough/QA実効値/hook呼出。
実行: .venv\\Scripts\\python.exe -W error -m unittest er003_test_kp_possessor_roles_wiring_01 -v"""
from __future__ import annotations

import test_state_isolation_01  # noqa: F401  (Production監査ログ・telemetryへの追記を隔離)

import hashlib
import json
import os
import re
import tempfile
import unittest
from unittest import mock

import er003_key_words_canonicalization as kc
import er003_key_words_gloss_alignment as ga
import er003_v1_n3_01_scaffold_generate as sc
import er105_kp_fulltext_selector_01 as ft

ROOT = os.path.dirname(os.path.abspath(__file__))


def _orig(rank, display, fulltext=True, **kw):
    it = {"rank": rank, "display_phrase": display, "source_span": display, "source_sentence": f"They {display} today.",
          "ja_gloss": None, "japanese_gloss": None}
    if fulltext:
        it.update({"fulltext_source_ref": ft.FULLTEXT_SOURCE_REF_ID, "source_sentence_id": f"S{rank}",
                   "selection_resolution_method": "fulltext_exact_unique", "occurrence_count": 1,
                   "occurrence_sentence_ids": [f"S{rank}"], "declared_word_count_mismatch": False})
    it.update(kw)
    return it


def _row(rank, key, reason="generalize_person_dependent_reference", roles=None, **qa):
    row = {"rank": rank, "possessor_roles": roles if roles is not None else [], "key_phrase": key,
           "changed_from_display_phrase": True, "normalization_reason": reason, "reasoning": "r"}
    for f in kc.QA_FIELDS:
        row[f] = qa.get(f, "PASS")
    return row


def _read(path, mode="r"):
    with open(path, mode, **({} if "b" in mode else {"encoding": "utf-8", "errors": "ignore"})) as f:
        return f.read()


def _R(*pairs):
    return [{"token": t, "role": r} for t, r in pairs]


def _post(orig_items, rows):
    return ft.postprocess_possessor_roles({"items": rows}, orig_items)


def _status(post, i=0):
    return post["items"][i]["person_role_repair"]["status"]


def _validate(orig_items, post):
    return kc.validate_canonicalization_response(post, orig_items)["status"]


# ==================================================================
# A-1: validator真理値表(WIRING_DESIGN_01 付録A)
# ==================================================================
class TestA1ReferenceWord(unittest.TestCase):
    POS = [("draw a line", "draw that line", "generalize_reference_word"), ("float an idea", "float that idea", "generalize_reference_word"),
           ("take a step", "take that step", "generalize_reference_word"), ("make a call", "make that call", "generalize_reference_word"),
           ("pull someone under", "pulled him under", "generalize_person_dependent_reference"),
           ("sentence someone to death", "sentenced him to death", "generalize_person_dependent_reference"),
           ("tell someone the truth", "told her the truth", "generalize_person_dependent_reference"),
           ("give someone a hand", "gave him a hand", "generalize_person_dependent_reference"),
           ("close around someone", "close around me", "generalize_person_dependent_reference"),
           ("lose someone's job", "lose her job", "generalize_person_dependent_reference"),
           ("push prices up", "pushed prices up", "lemma_normalization")]
    NEG = [("draw the line", "draw that line"), ("float a idea", "float that idea"), ("take an advice", "take that advice"),
           ("cost a much", "cost that much"), ("so a nobody noticed", "so that nobody noticed"), ("a time", "that time"),
           ("lose someone job", "lose her job"), ("bind to the protein", "bound to the protein")]   # 最後はOPEN-476=DEFERRED(拒否のまま)

    def test_positive_table(self):
        for key, disp, reason in self.POS:
            with self.subTest(key=key):
                self.assertTrue(kc._is_valid_fulltext_normalization(key, disp, reason))
                self.assertTrue(ft.is_valid_inflection_normalization(key, disp))

    def test_negative_table(self):
        for key, disp in self.NEG:
            with self.subTest(key=key):
                self.assertFalse(ft.is_valid_inflection_normalization(key, disp))

    def test_reason_gate_other_none_rejected(self):
        for reason in ("none", "other", "remove_contextual_determiner"):
            self.assertFalse(kc._is_valid_fulltext_normalization("draw a line", "draw that line", reason))
        for reason in ("generalize_reference_word", "lemma_normalization", "generalize_person_dependent_reference"):
            self.assertTrue(kc._is_valid_fulltext_normalization("draw a line", "draw that line", reason))

    def test_fixed_expressions_not_replaced(self):
        for disp, key in [("that said", "a said"), ("at that point", "at a point"), ("this time", "a time"), ("like that", "like a"),
                          ("all that", "all a")]:
            with self.subTest(disp=disp):
                self.assertFalse(ft.is_valid_inflection_normalization(key, disp))

    def test_a_an_by_cmu(self):
        for w in ("idea", "hour", "umbrella", "honest"):
            self.assertTrue(ft.starts_with_vowel_sound(w), w)
        for w in ("line", "university", "one", "step"):
            self.assertFalse(ft.starts_with_vowel_sound(w), w)

    def test_her_possessive_vs_object(self):
        self.assertTrue(ft.is_valid_inflection_normalization("tell someone the truth", "told her the truth"))
        self.assertFalse(ft.is_valid_inflection_normalization("lose someone job", "lose her job"))

    def test_full_response_pass_for_a1(self):
        o = [_orig(1, "draw that line")]
        post = _post(o, [_row(1, "draw a line", "generalize_reference_word")])
        self.assertEqual(_validate(o, post), "CANONICALIZATION_PASS")
        o2 = [_orig(1, "pulled him under")]
        post2 = _post(o2, [_row(1, "pull someone under", "generalize_person_dependent_reference", qa_traceable_contiguous_span="FAIL")])
        self.assertEqual(_validate(o2, post2), "CANONICALIZATION_PASS")   # qa_traceable FAILはvalidator合格の変換なので実効PASS

    def test_gloss_person_generalization_pairs_g1(self):
        pairs = ga.person_generalization_pairs({"display_phrase": "pulled him under", "key_phrase": "pull someone under"})
        self.assertEqual(pairs, [{"from": "him", "to": "someone"}])   # pulled->pull(lemma)は人称組ではない。him->someoneのみ
        pairs = ga.person_generalization_pairs({"display_phrase": "close around me", "key_phrase": "close around someone"})
        self.assertEqual(pairs, [{"from": "me", "to": "someone"}])
        pairs = ga.person_generalization_pairs({"display_phrase": "pull him under", "key_phrase": "pull someone under"})
        self.assertEqual(pairs, [{"from": "him", "to": "someone"}])
        self.assertIsNotNone(ga.person_reference_mismatch("pull someone under", "彼を引きずり込む"))

    def test_gloss_pairs_g1_prime_only_with_role_ok(self):
        item = {"display_phrase": "lose my job", "key_phrase": "lose someone's job"}
        self.assertEqual(ga.person_generalization_pairs(item), [])                     # 表は拡張しない(roleの記録が無ければ組を返さない)
        item["person_role_repair"] = {"role_ok_poss": [1]}
        self.assertEqual(ga.person_generalization_pairs(item), [{"from": "my", "to": "someone's"}])
        self.assertNotIn("someone's", kc._PERSON_DEPENDENT_TO_GENERIC["my"])           # 共有許可表は不変


# ==================================================================
# 課題②: possessor_roles検証・role条件付き受理・revertのみ
# ==================================================================
class TestA1ValidatorTighteningW03W02(unittest.TestCase):
    """委任_27: Opus条件C必須修正W-03(置換しない条件のvalidator決定論却下)とW-02(辞書に無い語は不許可・複数発音は保守的)。
    template(5(a)(b)の『置換しない』列挙)はvalidatorより広くない: validatorはtemplate列挙+時間名詞・same/other/very・me系固定表現・不可算の後方語を追加で却下する(受理範囲を狭めるのみ)。"""
    NEG = [("not a bad", "not that bad"), ("between someone and someone", "between you and me"), ("between you and someone", "between you and me"),
           ("a year", "this year"), ("a week", "this week"), ("a weekend", "this weekend"), ("a month", "that month"), ("a morning", "this morning"),
           ("a same team", "that same team"), ("an other idea", "that other idea"), ("a very day", "that very day"),
           ("take a good advice", "take that good advice"), ("take a good information", "take that good information"),
           ("excuse someone", "excuse me"), ("beats someone", "beats me"), ("trust someone", "trust me"), ("lucky someone", "lucky me"),
           ("isn't a bad", "isn't that bad"), ("all a idea", "all that idea"), ("just a step", "just that step"), ("at a step", "at that step"),
           ("with a idea", "with that idea"), ("like a line", "like that line"), ("quite a step", "quite that step")]
    POS = [("draw a line", "draw that line"), ("float an idea", "float that idea"), ("take a step", "take that step"), ("make a call", "make that call"),
           ("pull someone under", "pulled him under"), ("tell someone the truth", "told her the truth"), ("close around someone", "close around me"),
           ("give someone a hand", "gave him a hand")]

    def test_negative_cases_rejected(self):
        for key, disp in self.NEG:
            with self.subTest(key=key, disp=disp):
                self.assertFalse(ft.is_valid_inflection_normalization(key, disp))
                for reason in ("generalize_reference_word", "generalize_person_dependent_reference", "lemma_normalization"):
                    self.assertFalse(kc._is_valid_fulltext_normalization(key, disp, reason))

    def test_positive_cases_kept(self):
        for key, disp in self.POS:
            with self.subTest(key=key):
                self.assertTrue(ft.is_valid_inflection_normalization(key, disp))

    def test_context_before_window_is_used(self):
        # 窓の外の直前語でも除外が効く(窓がthatから始まる場合)
        self.assertFalse(ft.is_valid_inflection_normalization("a bad", "not that bad day"))
        self.assertTrue(ft.is_valid_inflection_normalization("draw a line", "they draw that line now"))

    def test_w02_unknown_word_is_not_allowed(self):
        self.assertFalse(ft.starts_with_vowel_sound("zzqxv"))
        self.assertFalse(ft.starts_with_consonant_sound("zzqxv"))
        self.assertFalse(ft.is_valid_inflection_normalization("draw a zzqxv", "draw that zzqxv"))
        self.assertFalse(ft.is_valid_inflection_normalization("draw an zzqxv", "draw that zzqxv"))

    def test_w02_dictionary_exception_is_safe(self):
        import pronouncing
        with mock.patch.object(pronouncing, "phones_for_word", side_effect=RuntimeError("boom")):
            self.assertFalse(ft.starts_with_vowel_sound("idea"))
            self.assertFalse(ft.starts_with_consonant_sound("line"))
            self.assertFalse(ft.is_valid_inflection_normalization("draw a line", "draw that line"))

    def test_w02_multiple_pronunciations_must_all_match(self):
        import pronouncing
        with mock.patch.object(pronouncing, "phones_for_word", return_value=["AH0 B", "B AH0"]):
            self.assertFalse(ft.starts_with_vowel_sound("x"))
            self.assertFalse(ft.starts_with_consonant_sound("x"))
        with mock.patch.object(pronouncing, "phones_for_word", return_value=["AH0 B", "EY1 B"]):
            self.assertTrue(ft.starts_with_vowel_sound("x"))
        with mock.patch.object(pronouncing, "phones_for_word", return_value=["B AH0", "K AH0"]):
            self.assertTrue(ft.starts_with_consonant_sound("x"))


class TestPossessorRolesPostprocess(unittest.TestCase):
    def test_self_one_s_unchanged(self):
        o = [_orig(1, "lost his temper")]
        post = _post(o, [_row(1, "lose one's temper", "generalize_person_dependent_reference", roles=_R(("his", "self")))])
        self.assertEqual(_status(post), "NO_CHANGE")
        self.assertEqual(post["items"][0]["key_phrase"], "lose one's temper")
        self.assertEqual(_validate(o, post), "CANONICALIZATION_PASS")

    def test_other_person_someone_s_unchanged(self):
        o = [_orig(1, "praised their effort")]
        post = _post(o, [_row(1, "praise someone's effort", roles=_R(("their", "other_person")))])
        self.assertEqual(_status(post), "NO_CHANGE")
        self.assertEqual(_validate(o, post), "CANONICALIZATION_PASS")

    def test_wrong_other_person_to_one_s_is_reverted(self):
        o = [_orig(1, "praised their effort")]
        post = _post(o, [_row(1, "praise one's effort", roles=_R(("their", "other_person")))])
        self.assertEqual(_status(post), "REPAIRED")
        self.assertEqual(post["items"][0]["key_phrase"], "praise their effort")     # displayの語へ戻す(someone'sへ書換えない)
        self.assertEqual(post["items"][0]["person_role_repair"]["repairs"][0]["rule"], "revert_other_person")
        self.assertEqual(_validate(o, post), "CANONICALIZATION_PASS")

    def test_wrong_self_to_someone_s_is_reverted(self):
        o = [_orig(1, "reach for your wallet")]
        post = _post(o, [_row(1, "reach for someone's wallet", roles=_R(("your", "self")))])
        self.assertEqual(_status(post), "REPAIRED")
        self.assertEqual(post["items"][0]["key_phrase"], "reach for your wallet")
        self.assertEqual(post["items"][0]["normalization_reason"], "none")
        self.assertFalse(post["items"][0]["changed_from_display_phrase"])
        self.assertEqual(_validate(o, post), "CANONICALIZATION_PASS")

    def test_non_person_its_kept_and_generalized_is_reverted(self):
        o = [_orig(1, "run its course")]
        self.assertEqual(_status(_post(o, [_row(1, "run its course", "none", roles=_R(("its", "non_person")))])), "NO_CHANGE")
        post = _post(o, [_row(1, "run one's course", roles=_R(("its", "non_person")))])
        self.assertEqual(_status(post), "REPAIRED")
        self.assertEqual(post["items"][0]["key_phrase"], "run its course")          # 物が動作主のitsは現状維持
        self.assertEqual(_validate(o, post), "CANONICALIZATION_PASS")

    def test_role_none_object_her_untouched_a1_someone_not_reverted(self):
        o = [_orig(1, "told her the truth")]
        post = _post(o, [_row(1, "tell someone the truth", roles=_R(("her", "none")))])
        self.assertEqual(_status(post), "NO_CHANGE")                                 # A-1のsomeone(目的格)は所有格revertの対象外
        self.assertEqual(post["items"][0]["key_phrase"], "tell someone the truth")
        self.assertEqual(_validate(o, post), "CANONICALIZATION_PASS")

    def test_role_none_possessive_generic_is_reverted(self):
        o = [_orig(1, "lose her job")]
        post = _post(o, [_row(1, "lose someone's job", roles=_R(("her", "none")))])
        self.assertEqual(_status(post), "REPAIRED")
        self.assertEqual(post["items"][0]["key_phrase"], "lose her job")

    def test_a1_and_possessive_coexist(self):
        o = [_orig(1, "gave him his word")]
        post = _post(o, [_row(1, "give someone one's word", roles=_R(("his", "self")))])
        self.assertEqual(_status(post), "NO_CHANGE")
        self.assertEqual(_validate(o, post), "CANONICALIZATION_PASS")
        # A-1側のsomeoneは残し、所有格だけをrevertする
        post2 = _post(o, [_row(1, "give someone someone's word", roles=_R(("his", "self")))])
        self.assertEqual(_status(post2), "REPAIRED")
        self.assertEqual(post2["items"][0]["key_phrase"], "give someone his word")
        self.assertEqual(_validate(o, post2), "CANONICALIZATION_PASS")

    def test_reflexive_and_double_possessive(self):
        o = [_orig(1, "put herself in their shoes")]
        post = _post(o, [_row(1, "put oneself in someone's shoes", roles=_R(("their", "other_person")))])
        self.assertEqual(_status(post), "NO_CHANGE")                                 # 再帰代名詞はroleを問わず決定論(許可表のoneselfのみ)
        self.assertEqual(_validate(o, post), "CANONICALIZATION_PASS")

    def test_unverified_roles_leave_key_untouched(self):
        o = [_orig(1, "reach for your wallet")]
        for roles in (None, [], _R(("your", "self"), ("his", "self")), _R(("his", "self")), _R(("your", "bogus"))):
            with self.subTest(roles=roles):
                row = _row(1, "reach for someone's wallet")
                if roles is None:
                    row.pop("possessor_roles")
                else:
                    row["possessor_roles"] = roles
                post = _post(o, [row])
                self.assertEqual(_status(post), "UNVERIFIED_ROLES")
                self.assertEqual(post["items"][0]["key_phrase"], "reach for someone's wallet")   # 迷えば触らない=現行どおり

    def test_no_possessive_item_untouched(self):
        o = [_orig(1, "pushed prices up")]
        post = _post(o, [_row(1, "push prices up", "lemma_normalization", roles=[])])
        self.assertEqual(_status(post), "NO_POSSESSIVE")
        self.assertEqual(post["items"][0]["key_phrase"], "push prices up")

    def test_input_not_mutated(self):
        o = [_orig(1, "reach for your wallet")]
        parsed = {"items": [_row(1, "reach for someone's wallet", roles=_R(("your", "self")))]}
        before = json.dumps(parsed, sort_keys=True)
        ft.postprocess_possessor_roles(parsed, o)
        self.assertEqual(json.dumps(parsed, sort_keys=True), before)

    def test_reason_generalize_reference_word_preserved_after_revert(self):
        o = [_orig(1, "draw that line their way")]
        post = _post(o, [_row(1, "draw a line one's way", "generalize_reference_word", roles=_R(("their", "other_person")))])
        self.assertEqual(_status(post), "REPAIRED")
        self.assertEqual(post["items"][0]["key_phrase"], "draw a line their way")
        self.assertEqual(post["items"][0]["normalization_reason"], "generalize_reference_word")   # A-1の記録を消さない
        self.assertTrue(post["items"][0]["changed_from_display_phrase"])
        self.assertEqual(_validate(o, post), "CANONICALIZATION_PASS")

    def test_reason_recomputed_when_person_reason_no_longer_fits(self):
        o = [_orig(1, "pumps its fist")]
        post = _post(o, [_row(1, "pump one's fist", "generalize_person_dependent_reference", roles=_R(("its", "non_person")))])
        self.assertEqual(post["items"][0]["key_phrase"], "pump its fist")
        self.assertEqual(post["items"][0]["normalization_reason"], "lemma_normalization")
        self.assertEqual(_validate(o, post), "CANONICALIZATION_PASS")

    def test_revert_skipped_when_validator_would_fail(self):
        o = [_orig(1, "praised their effort")]
        with mock.patch.object(kc, "validate_canonicalization_item", return_value={"ok": False, "reasons": ["x"]}):
            post = _post(o, [_row(1, "praise one's effort", roles=_R(("their", "other_person")))])
        self.assertEqual(_status(post), "REVERT_SKIPPED")
        self.assertEqual(post["items"][0]["key_phrase"], "praise one's effort")   # key無変更(新しいINVALID/retry消費を作らない)

    def test_no_window_leaves_key_untouched(self):
        o = [_orig(1, "reach for your wallet")]
        post = _post(o, [_row(1, "grab for someone's wallet", roles=_R(("your", "self")))])
        self.assertEqual(_status(post), "NO_WINDOW")
        self.assertEqual(post["items"][0]["key_phrase"], "grab for someone's wallet")

    def test_qa_person_flag_not_overwritten_without_repair(self):
        o = [_orig(1, "lost his temper")]
        post = _post(o, [_row(1, "lose one's temper", roles=_R(("his", "self")), qa_person_reference_generalized="FAIL")])
        self.assertEqual(post["items"][0]["qa_person_reference_generalized"], "FAIL")   # 無条件PASS上書きはしない
        post2 = _post([_orig(1, "reach for your wallet")], [_row(1, "reach for someone's wallet", roles=_R(("your", "self")),
                                                                  qa_person_reference_generalized="FAIL")])
        self.assertEqual(post2["items"][0]["qa_person_reference_generalized"], "PASS")   # revert後はroleと整合

    def test_traceable_fail_with_unchanged_key_becomes_pass(self):
        o = [_orig(1, "reach for your wallet")]
        post = _post(o, [_row(1, "reach for someone's wallet", roles=_R(("your", "self")), qa_traceable_contiguous_span="FAIL")])
        self.assertEqual(post["items"][0]["qa_traceable_contiguous_span"], "PASS")        # QA定義(a): key==display

    def test_postprocess_is_deterministic_and_idempotent(self):
        o = [_orig(1, "reach for your wallet")]
        rows = [_row(1, "reach for someone's wallet", roles=_R(("your", "self")))]
        p1 = _post(o, rows)
        p2 = ft.postprocess_possessor_roles(p1, o)
        self.assertEqual(p2["items"][0]["key_phrase"], p1["items"][0]["key_phrase"])


# ==================================================================
# role条件付き受理(my/our -> someone's): 共有許可表は不変・A/B/C非適用
# ==================================================================
class TestRoleConditionalAcceptance(unittest.TestCase):
    def test_my_to_someone_s_accepted_only_for_verified_other_person(self):
        o = [_orig(1, "lose my job")]
        ok = _post(o, [_row(1, "lose someone's job", roles=_R(("my", "other_person")))])
        self.assertEqual(_status(ok), "NO_CHANGE")
        self.assertEqual(ok["items"][0]["person_role_repair"]["role_ok_poss"], [1])
        self.assertEqual(_validate(o, ok), "CANONICALIZATION_PASS")

    def test_my_to_someone_s_with_role_self_is_reverted(self):
        o = [_orig(1, "lose my job")]
        post = _post(o, [_row(1, "lose someone's job", roles=_R(("my", "self")))])
        self.assertEqual(_status(post), "REPAIRED")
        self.assertEqual(post["items"][0]["key_phrase"], "lose my job")
        self.assertEqual(_validate(o, post), "CANONICALIZATION_PASS")

    def test_my_to_someone_s_with_unverified_roles_rejected_as_today(self):
        o = [_orig(1, "lose my job")]
        row = _row(1, "lose someone's job")
        row.pop("possessor_roles")
        post = _post(o, [row])
        self.assertEqual(_status(post), "UNVERIFIED_ROLES")
        self.assertEqual(_validate(o, post), "CANONICALIZATION_INVALID")                # 従来どおり外側retryへ

    def test_llm_cannot_self_declare_role_ok(self):
        o = [_orig(1, "lose my job")]
        row = _row(1, "lose someone's job", roles=_R(("my", "self")))
        row["person_role_repair"] = {"role_ok_poss": [1]}                               # LLMが偽装しても後処理が上書きする
        post = _post(o, [row])
        self.assertEqual(post["items"][0]["person_role_repair"]["role_ok_poss"], [])
        self.assertEqual(post["items"][0]["key_phrase"], "lose my job")

    def test_shared_table_and_find_window_default_unchanged(self):
        self.assertEqual(kc._PERSON_DEPENDENT_TO_GENERIC["my"], {"one's"})
        self.assertEqual(kc._PERSON_DEPENDENT_TO_GENERIC["our"], {"one's"})
        self.assertFalse(ft.is_valid_inflection_normalization("lose someone's job", "lose my job"))
        self.assertFalse(kc._is_valid_person_generalization("pull someone's leg", "pull my leg"))            # er064:55-56と同じ固定
        self.assertTrue(ft.is_valid_inflection_normalization("lose someone's job", "lose my job", frozenset({1})))

    def test_legacy_abc_item_does_not_get_role_acceptance(self):
        # A/B/C itemは(fulltext_source_refなし)=role_ok_possを渡さない。canon行にperson_role_repairがあっても受理範囲は広がらない。
        o = [_orig(1, "lose my job", fulltext=False)]
        row = _row(1, "lose someone's job")
        row["person_role_repair"] = {"role_ok_poss": [1]}
        for k in ("possessor_roles", "person_role_repair"):
            pass
        row_abc = {k: v for k, v in row.items() if k != "possessor_roles"}
        self.assertEqual(kc.validate_canonicalization_response({"items": [row_abc]}, o)["status"], "CANONICALIZATION_INVALID")
        self.assertEqual(kc.validate_canonicalization_item("pull someone's leg", "pull my leg", "pull my leg",
                                                           normalization_reason="generalize_person_dependent_reference")["ok"], False)

    def test_legacy_abc_template_and_enum_unchanged(self):
        old = open(os.path.join(ROOT, kc.PROMPT_TEMPLATE_PATH), "rb").read().replace(b"\r\n", b"\n")
        self.assertEqual(hashlib.sha1(b"blob %d\0" % len(old) + old).hexdigest(), "6e19a90557b8512a0f3727cfa4547663df873ea4")
        self.assertNotIn("possessor_roles", kc.CANONICALIZATION_JSON_SCHEMA["schema"]["properties"]["items"]["items"]["properties"])
        self.assertNotIn("generalize_reference_word", kc.NORMALIZATION_REASONS)


# ==================================================================
# hook(run_canonicalization_gate postprocess) / merge passthrough / scaffold配線
# ==================================================================
class TestGateHookAndMerge(unittest.TestCase):
    def _factory(self, rows):
        raw = json.dumps({"items": rows}, ensure_ascii=False)

        def make_factory():
            return lambda: (raw, "gpt-6-luna", "resp_x")
        return make_factory, raw

    def test_gate_without_postprocess_is_unchanged(self):
        o = [_orig(1, "reach for your wallet")]
        rows = [_row(1, "reach for someone's wallet", roles=_R(("your", "self")))]
        mk, raw = self._factory(rows)
        parsed, status, attempts, _, _ = kc.run_canonicalization_gate(mk, o)
        self.assertEqual(parsed["items"][0]["key_phrase"], "reach for someone's wallet")   # hook無し=従来どおり(何も書換えない)
        self.assertNotIn("person_role_repair", parsed["items"][0])

    def test_gate_with_postprocess_reverts_and_keeps_raw_text(self):
        o = [_orig(1, "reach for your wallet")]
        rows = [_row(1, "reach for someone's wallet", roles=_R(("your", "self")))]
        mk, raw = self._factory(rows)
        parsed, status, attempts, _, _ = kc.run_canonicalization_gate(mk, o, postprocess=ft.postprocess_possessor_roles)
        self.assertEqual(status, "CANONICALIZATION_PASS")
        self.assertEqual(parsed["items"][0]["key_phrase"], "reach for your wallet")
        self.assertEqual(attempts[0]["raw_text"], raw)                                   # 生応答は書換えず保持
        self.assertEqual(len(attempts), 1)                                               # retryを消費しない

    def test_gate_postprocess_exception_falls_back_to_raw(self):
        o = [_orig(1, "lost his temper")]
        rows = [_row(1, "lose one's temper", roles=_R(("his", "self")))]
        mk, raw = self._factory(rows)

        def boom(parsed, items):
            raise ValueError("x")
        parsed, status, attempts, _, _ = kc.run_canonicalization_gate(mk, o, postprocess=boom)
        self.assertEqual(status, "CANONICALIZATION_PASS")
        self.assertIn("ValueError", attempts[0]["postprocess_error"])

    def test_merge_passes_roles_for_fulltext_only(self):
        o = [_orig(1, "reach for your wallet")]
        post = _post(o, [_row(1, "reach for someone's wallet", roles=_R(("your", "self")))])
        merged = kc.merge_canonicalization_result(o, post["items"])["items"][0]
        self.assertEqual(merged["key_phrase"], "reach for your wallet")
        self.assertEqual(merged["possessor_roles"], _R(("your", "self")))
        self.assertEqual(merged["person_role_repair"]["status"], "REPAIRED")
        self.assertEqual(merged["used_form"], "reach for your wallet")
        # A/B/C itemにはcanon側に欄があっても複写しない(出力バイト同一)
        oa = [_orig(1, "pushed prices up", fulltext=False)]
        row = _row(1, "pushed prices up", "none", roles=[])
        row["person_role_repair"] = {"status": "X"}
        row["changed_from_display_phrase"] = False
        mm = kc.merge_canonicalization_result(oa, [row])["items"][0]
        self.assertNotIn("possessor_roles", mm)
        self.assertNotIn("person_role_repair", mm)

    def test_merge_effective_qa_uses_role_ok(self):
        o = [_orig(1, "lose my job")]
        post = _post(o, [_row(1, "lose someone's job", roles=_R(("my", "other_person")), qa_traceable_contiguous_span="FAIL")])
        merged = kc.merge_canonicalization_result(o, post["items"])["items"][0]
        self.assertEqual(merged["qa"]["qa_traceable_contiguous_span"], "PASS")
        self.assertEqual(merged["qa_overall_status"], "PASS")

    def test_scaffold_passes_hook_only_for_fulltext(self):
        captured = {}

        def fake_gate(make_factory, original_items, **kw):
            captured["kw"] = kw
            return None, "TECHNICAL_GENERATION_FAILED", [], None, None
        for fulltext in (True, False):
            captured.clear()
            with tempfile.TemporaryDirectory() as d, mock.patch.object(kc, "run_canonicalization_gate", side_effect=fake_gate):
                items = [_orig(1, "reach for your wallet", fulltext=fulltext)]
                sc.run_key_phrase_canonicalization("ART text", items, d, "art1")
            if fulltext:
                self.assertIs(captured["kw"]["postprocess"], ft.postprocess_possessor_roles)
            else:
                self.assertIsNone(captured["kw"]["postprocess"])

    def test_only_fulltext_scaffold_passes_postprocess_in_source(self):
        hits = []
        for fn in os.listdir(ROOT):
            if fn.endswith(".py") and "_test" not in fn and not fn.startswith("er112_") and fn != "er003_key_words_canonicalization.py":
                src = _read(os.path.join(ROOT, fn))
                if re.search(r"run_canonicalization_gate\([^)]*postprocess\s*=", src, re.S) or "postprocess=_postprocess" in src:
                    hits.append(fn)
        self.assertEqual(hits, ["er003_v1_n3_01_scaffold_generate.py"])                   # A/B/Cの約10呼出点はhookを渡さない

    def test_xz_share_single_canonicalization_path(self):
        # X: er019 run_theme_scaffold / Z: er026 run_kp_stage は共に sc.run_key_phrases -> run_key_phrase_canonicalization(1箇所)を通る
        src = _read(os.path.join(ROOT, "er003_v1_n3_01_scaffold_generate.py"))
        self.assertEqual(src.count("kc.run_canonicalization_gate("), 1)


# ==================================================================
# template / schema / Dangling Reference
# ==================================================================
class TestTemplateAndSchema(unittest.TestCase):
    def setUp(self):
        self.t = kc.load_prompt_template(kc.FULLTEXT_PROMPT_TEMPLATE_PATH)

    def test_template_has_role_block_rule5_and_pt2(self):
        for needle in ("possessor_roles", "role=self", "role=other_person", "role=non_person", "5. 参照語の不定化", "generalize_reference_word",
                       "置換せずdisplay_phraseの語のまま残してください", "lose one's temper", "challenge its conclusions"):
            self.assertIn(needle, self.t, needle)

    def test_old_rules_removed(self):
        for old in ("より自然だと判断する側を選んでください", "him/her(目的格)/them/me/us/it等の目的格・その他の代名詞は",
                    "\"pumps its fist\"→\"pump its fist\"(人称の一般化と併用する場合は\"pump one's fist\")", "a/an/the"):
            self.assertNotIn(old, self.t, old)

    def test_the_not_allowed_consistent(self):
        self.assertIn("theは使いません", self.t)
        self.assertFalse(ft.is_valid_inflection_normalization("draw the line", "draw that line"))

    def test_schema_possessor_roles_before_key_phrase(self):
        props = list(kc.CANONICALIZATION_JSON_SCHEMA_FULLTEXT["schema"]["properties"]["items"]["items"]["properties"])
        self.assertLess(props.index("possessor_roles"), props.index("key_phrase"))

    def test_no_dangling_reference_to_dev_or_unapproved(self):
        for fn in ("er003_key_words_canonicalization.py", "er105_kp_fulltext_selector_01.py", "er003_v1_n3_01_scaffold_generate.py",
                   "er003_key_words_gloss_alignment.py"):
            src = _read(os.path.join(ROOT, fn))
            self.assertIsNone(re.search(r"^\s*(import|from)\s+er112_", src, re.M), fn)
            self.assertNotIn("EIGO_KP_POSS", src, fn)       # 実験flagに依存しない(flagによるON/OFFは設けない)
        self.assertNotIn("er112", self.t)


# ==================================================================
# Family Y(Trial専用経路)が同じ共通KP moduleを呼ぶこと(事実の固定)。Yの正式Production経路は存在しない=PRODUCTION_WIREDとは呼ばない。
# ==================================================================
class TestFamilyYSharedKpPath(unittest.TestCase):
    def test_y_trial_scaffolds_call_shared_fulltext_kp_path(self):
        for fn in ("er110_family_y_text_trial_01_run.py", "er110_family_y_persona_text_trial_01_run.py"):
            src = _read(os.path.join(ROOT, fn))
            self.assertRegex(src, r"sc\.run_key_phrases\([^)]*kp_backend=\"fulltext_p2\"", fn)      # X/Zと同じ共通KP module(er003_v1_n3_01_scaffold_generate)
            self.assertIn("import er003_v1_n3_01_scaffold_generate as sc", src, fn)

    def test_y_has_no_production_entry_flag_in_audio_trials(self):
        for fn in ("er110_family_y_audio_trial_01.py", "er110_family_y_persona_audio_trial_01.py"):
            self.assertIn('"production_reachable": False', _read(os.path.join(ROOT, fn)), fn)

    def test_shared_path_gives_y_trial_the_same_hook(self):
        # Y trial = sc.run_key_phrases(kp_backend="fulltext_p2") -> run_kp_with_outer_retry -> run_key_phrase_canonicalization(is_fulltext) -> hook
        src = _read(os.path.join(ROOT, "er003_v1_n3_01_scaffold_generate.py"))
        self.assertIn("kp_backend == FULLTEXT_BACKEND_ID", src)
        self.assertIn("postprocess=_postprocess", src)


if __name__ == "__main__":
    unittest.main()
