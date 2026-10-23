# -*- coding: utf-8 -*-
"""er112_kp_gm_poss_04 の決定論部分(API 0)と、DefaultOffIsolation(import/未install時にProductionのattributeが変わらないこと)のtest。"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import er003_key_words_canonicalization as kc          # noqa: E402
import er112_kp_gm_poss_04 as P                        # noqa: E402

R = lambda tok, role: {"token": tok, "role": role}     # noqa: E731


def test_default_off_isolation_before_install():
    assert kc._PERSON_DEPENDENT_TO_GENERIC["my"] == {"one's"}
    assert kc._PERSON_DEPENDENT_TO_GENERIC["our"] == {"one's"}
    assert not P._INSTALLED


def test_repair_self_someone_to_one():
    r = P.repair_item("reach for your wallet", "reach for someone's wallet", [R("your", "self")], "role")
    assert r["status"] == "REPAIRED" and r["key_after"] == "reach for one's wallet"
    assert r["repairs"][0]["rule"] == "role_self"


def test_repair_other_one_to_someone():
    r = P.repair_item("he will die in your place", "die in one's place", [R("your", "other_person")], "role")
    assert r["key_after"] == "die in someone's place"


def test_non_person_generalized_reverts_to_display_word():
    for mode in ("role", "revert"):
        r = P.repair_item("apply its findings", "apply one's findings", [R("its", "non_person")], mode)
        assert r["status"] == "REPAIRED" and r["key_after"] == "apply its findings"
        assert r["repairs"][0]["rule"] == "revert_non_person"


def test_none_role_with_replacement_reverts():
    r = P.repair_item("told her the truth", "tell her the truth", [R("her", "none")], "role")
    assert r["status"] == "NO_CHANGE"
    r = P.repair_item("pumps its fist", "pump one's fist", [R("its", "none")], "role")
    assert r["key_after"] == "pump its fist"
    # 許可表に無い置換(its -> someone's)はwindowに合わず、修復せずProductionの既存validatorに任せる(NO_WINDOW)
    r = P.repair_item("pumps its fist", "pump someone's fist", [R("its", "none")], "role")
    assert r["status"] == "NO_WINDOW" and r["key_after"] == "pump someone's fist"


def test_not_replacing_is_always_allowed():
    for role in P.ROLES:
        r = P.repair_item("reach for your wallet", "reach for your wallet", [R("your", role)], "role")
        assert r["status"] == "NO_CHANGE" and r["key_after"] == "reach for your wallet"


def test_revert_mode_vs_role_mode():
    r_role = P.repair_item("lose her job", "lose someone's job", [R("her", "self")], "role")
    r_rev = P.repair_item("lose her job", "lose someone's job", [R("her", "self")], "revert")
    assert r_role["key_after"] == "lose one's job" and r_rev["key_after"] == "lose her job"


def test_unverified_roles_do_not_touch_key():
    # 要素数不一致 / token不一致 / enum外
    for roles in ([], [R("her", "self"), R("her", "self")], [R("his", "self")], [R("her", "robot")], None):
        r = P.repair_item("lose her job", "lose someone's job", roles, "role")
        assert r["status"] == "UNVERIFIED_ROLES" and r["key_after"] == "lose someone's job"


def test_multiple_possessives_token_level():
    # 二重所有: 出現順の配列で項目内の複数語を別々に判定
    r = P.repair_item("keep their hands off our property", "keep their hands off someone's property", [R("their", "self"), R("our", "other_person")], "role")
    assert r["status"] == "NO_CHANGE"       # theirは置換していない(常に許可)、our->someone's(other_person)は許可表(拡張)に合致
    r = P.repair_item("keep their hands off our property", "keep one's hands off one's property", [R("their", "self"), R("our", "other_person")], "role")
    assert r["key_after"] == "keep one's hands off someone's property"


def test_window_subphrase_alignment():
    # keyがdisplayの部分窓(語順そのまま・語形のみ変更)の場合も、窓内の所有格にroleを対応づける
    r = P.repair_item("when she pumps her fist at them", "pump someone's fist", [R("her", "self")], "role")
    assert r["key_after"] == "pump one's fist" and r["window_start"] == 2


def test_recompute_fields_after_revert():
    item = {"key_phrase": "apply one's findings", "normalization_reason": "generalize_person_dependent_reference", "changed_from_display_phrase": True,
            "qa_person_reference_generalized": "FAIL", "qa_traceable_contiguous_span": "FAIL"}
    chg = P.recompute_fields(item, "apply its findings", "apply its findings")
    assert chg["changed_from_display_phrase"] is False and chg["normalization_reason"] == "none"
    assert chg["qa_person_reference_generalized"] == "PASS" and chg["qa_traceable_contiguous_span"] == "PASS"


def test_recompute_fields_lemma_only_after_revert():
    item = {"key_phrase": "pump one's fist", "normalization_reason": "generalize_person_dependent_reference", "qa_traceable_contiguous_span": "PASS"}
    chg = P.recompute_fields(item, "pumps its fist", "pump its fist")
    assert chg["changed_from_display_phrase"] is True and chg["normalization_reason"] == "lemma_normalization"


def test_process_response_text_strips_roles_and_applies():
    text = json.dumps({"items": [{"rank": 1, "possessor_roles": [R("your", "self")], "key_phrase": "reach for someone's wallet", "changed_from_display_phrase": True,
                                  "normalization_reason": "generalize_person_dependent_reference", "qa_person_reference_generalized": "PASS",
                                  "qa_traceable_contiguous_span": "PASS"}]})
    out, log = P.process_response_text(text, {1: "reach for your wallet"}, "role")
    parsed = json.loads(out)
    assert "possessor_roles" not in parsed["items"][0]
    assert parsed["items"][0]["key_phrase"] == "reach for one's wallet"
    assert log[0]["applied"]["before"]["key_phrase"] == "reach for someone's wallet"
    out2, _ = P.process_response_text(text, {1: "reach for your wallet"}, "none")
    assert json.loads(out2)["items"][0]["key_phrase"] == "reach for someone's wallet"


def test_score_headword():
    assert P.score_headword("reach for your wallet", "reach for someone's wallet", ["self"]) == "WRONG"
    assert P.score_headword("reach for your wallet", "reach for one's wallet", ["self"]) == "CORRECT_GENERALIZED"
    assert P.score_headword("apply its findings", "apply its findings", ["non_person"]) == "KEPT"
    assert P.score_headword("apply its findings", "apply one's findings", ["non_person"]) == "WRONG"


def test_dev_poss_builders_fail_closed_after_wiring():
    """委任_20: 課題②+A-1がProductionへ配線済みのため、DEVのtemplate builderは(二重適用せず)drift guardでfail-closedし、
    Production templateは既にpossessor_roles規則を持つ。"""
    import er112_kp_gm_trial_01 as t1
    base = (ROOT / kc.FULLTEXT_PROMPT_TEMPLATE_PATH).read_text(encoding="utf-8")
    assert "possessor_roles" in base and "5. 参照語の不定化" in base
    with pytest.raises(RuntimeError):
        P.build_poss_template(t1.build_a1_template(base))
    props = list(kc.CANONICALIZATION_JSON_SCHEMA_FULLTEXT["schema"]["properties"]["items"]["items"]["properties"])
    assert props[:3] == ["rank", "possessor_roles", "key_phrase"]
    assert "possessor_roles" not in json.dumps(kc.CANONICALIZATION_JSON_SCHEMA)       # A/B/C共有schemaは不変
    assert (ROOT / kc.FULLTEXT_PROMPT_TEMPLATE_PATH).read_text(encoding="utf-8") == base


def test_dev_installer_fails_closed_without_partial_patch():
    orig_make, orig_load, orig_table = kc.make_canonicalization_fn, kc.load_prompt_template, {k: set(v) for k, v in kc._PERSON_DEPENDENT_TO_GENERIC.items()}
    with pytest.raises(RuntimeError):
        P.install_poss_patches()
    assert kc.make_canonicalization_fn is orig_make and kc.load_prompt_template is orig_load
    assert {k: set(v) for k, v in kc._PERSON_DEPENDENT_TO_GENERIC.items()} == orig_table   # 共有許可表は不変(my/ourへ足されていない)
    assert not P._INSTALLED
