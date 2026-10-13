# -*- coding: utf-8 -*-
"""er077 M1 OOV 複数発音候補方式の unit test(API 0、Production 無変更、Ledger は読取のみ)。"""
import hashlib
import inspect
import os
import sys

sys.path.insert(0, os.getcwd())
import er077_m1_oov_multi_pronunciation_01_eval as E  # noqa: E402

LED = E.load_ledger()


def test_ipa_to_arpa_table():
    assert E.ipa_to_arpa("/ˈmɛloʊs/") == ("M", "EH", "L", "OW", "S")
    assert E.ipa_to_arpa("/ˈmiː.lɑːs/") == ("M", "IY", "L", "AA", "S")
    assert E.ipa_to_arpa("/ˈmɪlɒs/") == ("M", "IH", "L", "AA", "S")
    assert E.ipa_to_arpa("/kæts/") == ("K", "AE", "T", "S")
    assert E.ipa_to_arpa("/vænˈkuː.vɚ/")[-1] == "ER"


def test_ipa_unconvertible_is_none():
    assert E.ipa_to_arpa("/otˈtoːni/") is None  # 'o' / 'oː' は表に無い=候補不成立
    assert E.ipa_to_arpa("oh-TOH-nee") is None  # 綴り読みは IPA ではない
    assert E.ipa_to_arpa("") is None


def test_candidates_depend_only_on_word_not_asr():
    params = inspect.signature(E.candidates_for).parameters
    assert "asr" not in params
    a = E.candidates_for("melos", LED)
    b = E.candidates_for("melos", LED)
    assert E.cset_hash(a) == E.cset_hash(b)
    fx = E.fix_candidates("Melos said.", LED)
    assert "melos" in fx and "said" in fx


def test_melos_candidates_sources_and_confidence_preserved():
    cs = E.candidates_for("melos", LED)
    srcs = {c["source"] for c in cs["candidates"]}
    assert srcs <= {"C2_ledger_expected", "C2_ledger_alt"}
    assert all(c["confidence"] == "low" for c in cs["candidates"])  # 低信頼を高信頼へ書き換えない
    prons = [tuple(c["pron"]) for c in cs["candidates"]]
    assert ("M", "EH", "L", "OW", "S") in prons and ("M", "IY", "L", "AA", "S") in prons
    assert len(prons) == len(set(prons))


def test_cap_enforced_and_overflow_recorded():
    led = {"x": {"surface": "zzqx", "entity_type": "cascade_unresolved_entity", "confidence": "low",
                 "expected_pronunciation_ipa": "/ˈkæt/", "alternate_pronunciations": ["/ˈkɪt/", "/ˈkʊt/", "/ˈkɛt/", "/ˈkʌt/", "/ˈkɑt/", "/ˈkɔt/", "/ˈkæp/"]}}
    cs = E.candidates_for("zzqx", led)
    assert len(cs["candidates"]) == E.CAP and cs["overflow_dropped"] == 2 and cs["n_before_cap"] == 8


def test_ledger_only_for_cmu_oov_words():
    led = {"u": {"surface": "us", "entity_type": "cascade_unresolved_entity", "confidence": "low",
                 "expected_pronunciation_ipa": "/ʌnˈnoʊn/", "alternate_pronunciations": []}}
    cs = E.candidates_for("us", led)
    assert all(c["source"] == "C1_cmu_variant" for c in cs["candidates"])  # CMU 収録語は Ledger を使わない


def test_non_english_label_and_katakana_excluded():
    cs = E.candidates_for("malmo", {"m": {"surface": "malmo", "entity_type": "place", "confidence": "high",
                                            "expected_pronunciation_ipa": "/ˈmæl.məʊ/ (English); Swedish native: /²malmøː/", "alternate_pronunciations": []}})
    assert [tuple(c["pron"]) for c in cs["candidates"]] == [("M", "AE", "L", "M", "OW")]
    assert any(x["reason"] == "non_english_label" for x in cs["excluded"])
    kata = {"k": {"surface": "figma", "entity_type": "ja_reading_katakana", "confidence": "high", "expected_pronunciation_ipa": "/fɪɡmə/", "alternate_pronunciations": []}}
    assert E.candidates_for("figma", kata)["candidates"] == []


def test_melos_pass_and_non_matching_nonpass():
    assert E.judge_multi("Melos said.", "Mello said.", LED)["new_m1"]
    assert E.judge_multi("Melos said.", "Mellow said.", LED)["new_m1"]
    for bad in ("Milo said.", "Mellon said.", "Melas said.", "Sad."):
        assert not E.judge_multi("Melos said.", bad, LED)["pass"], bad


def test_no_candidates_means_no_pass_even_if_spelling_close():
    r = E.judge_multi("Cleos said.", "Clio said.", LED)
    assert not r["pass"]  # C3 不採用: 綴り近似の救済なし


def test_pronunciation_mismatch_with_ledger_candidate_nonpass():
    led = dict(LED)
    led["f"] = {"surface": "cleos", "entity_type": "cascade_unresolved_entity", "confidence": "low",
                "expected_pronunciation_ipa": "/ˈkliːəs/", "alternate_pronunciations": []}
    assert not E.judge_multi("Cleos said.", "Clio said.", led)["pass"]


def test_f1_other_diffs_block_pass():
    for c, a in (("Melos said cats sleep.", "Mello said dogs sleep."), ("Melos said he did not go.", "Mello said he did go."),
                 ("Melos said 5 cats sleep.", "Mello said 6 cats sleep."), ("Melos said cats slept.", "Mello said cats sleep."),
                 ("Melos said he left.", "Mello said.")):
        assert not E.judge_multi(c, a, LED)["pass"], (c, a)
    assert E.judge_multi("Melos said cats sleep.", "Mello said cats sleep.", LED)["pass"]


def test_secondary_agree_requires_same_candidate():
    a = E.judge_multi("Melos said.", "Mello said.", LED)
    b = E.judge_multi("Melos said.", "Mellow said.", LED)
    c = E.judge_multi("Melos said.", "Mella said.", LED)
    assert E.secondary_agree(a, b, LED)
    assert not E.secondary_agree(a, c, LED)


def test_candidates_fixed_before_asr_flag_and_ledger_untouched():
    p = E.LEDGER_PATH
    h0 = hashlib.md5(open(p, "rb").read()).hexdigest()
    r = E.judge_multi("Melos said.", "Mello said.", LED)
    assert r["candidates_fixed_before_asr"] is True
    assert hashlib.md5(open(p, "rb").read()).hexdigest() == h0


def test_phoneme_ok_restored_after_context():
    orig = E.O.phoneme_ok
    E.judge_multi("Melos said.", "Mello said.", LED)
    assert E.O.phoneme_ok is orig
