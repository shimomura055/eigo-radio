# trial_direct_ledger_phoneme_02_test_01.py -- E2 Trial module(委任_02)の単体test。API 0・共有state書込0。
# 実行: .venv\Scripts\python.exe -m pytest docs/research/ASR-OOV-HOMOPHONE-ROOT-CAUSE-01/trial_direct_ledger_phoneme_02_test_01.py -q
import copy, glob, importlib, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE); sys.path.insert(0, ROOT)
import trial_direct_ledger_phoneme_01 as T
import er006_m1_multi_candidate_01 as m1

SEG = "full_story_part1"
T0 = "2099-01-01T00:00:00"
OLD = "2026-01-01T00:00:00"


def entry(surface, ipa, conf="medium", alt=None, sources=("https://example.org/x",), canon=None, upd=OLD, disabled=False,
          etype="cascade_unresolved_entity"):
    e = {"surface": surface, "entity_type": etype, "canonical_spelling": canon if canon is not None else surface,
         "expected_pronunciation_ipa": ipa, "alternate_pronunciations": alt or [], "confidence": conf,
         "sources": list(sources), "updated_at": upd}
    if disabled:
        e["ledger_disabled"] = True
    return e


LEDGER = {
    "k_gacha": entry("gacha", "/ˈɡɑː.tʃə/ (US English); /ˈɡætʃ.ə/ (UK English)",
                     alt=["UK English: /ˈɡætʃ.ə/", "US English: /ˈɡɑː.tʃə/"]),
    "k_lyft": entry("Lyft", "/lɪft/", etype="organization"),
    "k_skool": entry("skool", "/skuːl/"),
    "k_thicc": entry("thicc", "/θɪk/"),
    "k_boi": entry("boi", "/bɔɪ/"),
    "k_low": entry("kewl", "/kuːl/", conf="low"),
    "k_nosrc": entry("fyre", "/faɪ.ɚ/", sources=()),
    "k_disabled": entry("luv", "/lʌv/", disabled=True),
    "k_canon_differs": entry("phat", "/fæt/", canon="fat"),
    "k_future": entry("grindr", "/ˈɡrɪn.dɚ/", upd="2099-12-31T00:00:00"),
}


def run(canonical, asr, secondary=None, seg=SEG, ledger=LEDGER, **kw):
    fz = m1.freeze_candidates(canonical, ledger_snapshot=ledger, segment_started_at=T0)
    return T.judge_direct(canonical, asr, fz, segment_id=seg, secondary_asr_text=secondary, ledger=ledger, **kw)


G = "It's unexpected to find a gacha at the entrance, though."
GOT = "It's unexpected to find a gotcha at the entrance, though."


# ---- 正例 ----
def test_positive_gacha_gotcha():
    r = run(G, GOT)
    assert r["accepted"] and r["reason"] == T.E2_REASON
    assert r["sub"]["canonical"] == "gacha" and r["sub"]["asr"] == "gotcha" and r["sub"]["ledger_key"] == "k_gacha"
    assert r["normalized_asr"].count("gacha") == 1 and "gotcha" not in r["normalized_asr"]
    assert r["sub"]["candidate_set_hash"]


def test_positive_entity_capitalized_lyft_lift():
    r = run("We took a Lyft home after the party.", "We took a lift home after the party.")
    assert r["accepted"], r


def test_positive_skool_school_and_thicc_thick():
    assert run("Back to skool this fall.", "Back to school this fall.")["accepted"]
    assert run("That sandwich is so thicc today.", "That sandwich is so thick today.")["accepted"]


# ---- 負例(文字列レベル14件。精度の証拠ではなくロジック防御の確認) ----
NEG = {
    "gutter": GOT.replace("gotcha", "gutter"), "gadget": GOT.replace("gotcha", "gadget"), "gotta": GOT.replace("gotcha", "gotta"),
    "catcher": GOT.replace("gotcha", "catcher"), "gatcha_not_cmu": GOT.replace("gotcha", "gatcha"),
    "gaycha_not_cmu": GOT.replace("gotcha", "gaycha"),
    "dropped": GOT.replace("a gotcha at", "a at"), "two_words": GOT.replace("a gotcha at", "a got you at"),
    "plus_other_content_diff": GOT.replace("entrance", "entry"),
    "plus_number": GOT.replace("unexpected", "2 unexpected"),
    "plus_negation": GOT.replace("It's unexpected", "It's not unexpected"),
    "plus_dropped_function_word": GOT.replace(" at the", " the"),
    "double_gotcha": GOT.replace("gotcha", "gotcha gotcha"),
    "plus_tense": GOT.replace("find", "found"),
}


def test_negatives_not_accepted():
    assert len(NEG) == 14
    for k, a in NEG.items():
        r = run(G, a)
        assert not r["accepted"], (k, r["reason"])


# ---- 境界(OF-OOV-01/02) ----
def test_three_phoneme_minimum_boi_boy_rejected():
    r = run("He is a good boi today.", "He is a good boy today.")
    assert not r["accepted"] and r["reason"] == "PHONEME_RUN_TOO_SHORT"
    r2 = run("He is a good boi today.", "He is a good boy today.", min_phonemes=2)
    assert r2["accepted"]  # 閾値だけの差であること(境界の確認)


def test_confidence_low_excluded_and_high_accepted():
    r = run("That is so kewl today.", "That is so cool today.")
    assert not r["accepted"] and r["reason"] == "CONFIDENCE_TOO_LOW"
    L2 = dict(LEDGER)
    L2["k_low"] = entry("kewl", "/kuːl/", conf="high")
    assert run("That is so kewl today.", "That is so cool today.", ledger=L2)["accepted"]


def test_ledger_exclusion_contract_OF181_OF179():
    assert not run("I luv it today.", "I love it today.")["accepted"]                        # ledger_disabled
    assert not run("I saw a phat cat today.", "I saw a fat cat today.")["accepted"]          # canonical_spelling != surface
    assert not run("Open the fyre door today.", "Open the fire door today.")["accepted"]     # sources empty
    assert not run("I use grindr every day.", "I use grinder every day.")["accepted"]        # updated_at >= segment start


def test_multiple_occurrences_not_accepted_current_rule():
    r = run("A gacha is a gacha today.", "A gotcha is a gotcha today.")
    assert not r["accepted"] and r["reason"] in ("NOT_SINGLE_REPLACE", "NOT_1TO1") or r["reason"].startswith("ALIGN_NOT_UNIQUE")


def test_only_aligned_position_replaced_when_gotcha_elsewhere_is_genuine():
    c = "Gotcha, said the gacha seller today."
    a = "Gotcha, said the gotcha seller today."
    r = run(c, a)
    assert r["accepted"], r
    assert r["normalized_asr"].lower().startswith("gotcha, said the gacha seller")  # 先頭の gotcha は置換されない


def test_two_word_difference_not_accepted():
    r = run("We took a Lyft to skool today.", "We took a lift to school today.")
    assert not r["accepted"] and r["reason"] == "NOT_SINGLE_REPLACE"


def test_role_gating_keyphrase_heading_unclassified_excluded():
    for seg in ("kp1_en", "point_one_heading", None):
        r = run(G, GOT, seg=seg)
        assert not r["accepted"] and r["reason"] == "ROLE_NOT_ELIGIBLE", (seg, r["reason"])
    for seg in ("full_story_part3", "comment_1", "preview", "topic_intro", "in_one_line"):
        assert run(G, GOT, seg=seg)["accepted"], seg


def test_candidates_are_c2_only_and_no_c1():
    fz = m1.freeze_candidates("We took a Lyft home.", ledger_snapshot=LEDGER, segment_started_at=T0)
    cs = fz.word("lyft").candidates
    assert cs and all(c.source.startswith("C2_") for c in cs)


def test_canonical_in_cmu_not_eligible():
    r = run("We took a lift home today.", "We took a lyft home today.")
    assert not r["accepted"]


# ---- Secondary(OF-183相当) ----
def test_secondary_contradiction_rejected():
    r = run(G, GOT, secondary="It's unexpected to find a gutter at the entrance, though.")
    assert not r["accepted"] and r["reason"] == "SECONDARY_CONTRADICTION"
    r = run(G, GOT, secondary="It's unexpected to find 5 gotcha at the entrance, though.")
    assert not r["accepted"]


def test_secondary_agreement_accepted():
    r0 = run(G, GOT, secondary=G)
    assert r0["accepted"] and r0["secondary_state"] == "native_pass"
    r = run(G, GOT, secondary=GOT)  # Secondaryも同じ同音語 -> 同じE2で受理できる = 矛盾でない
    assert r["accepted"] and r["secondary_state"] == "e2_accept"
    assert run(G, GOT)["secondary_state"] == "not_provided"


# ---- 最終ANDゲート(値・否定) ----
def test_final_gate_values_negation():
    assert not run("There is no gacha prize today.", "There is gotcha prize today.")["accepted"]
    assert not run("There are 3 gacha prizes today.", "There are 4 gotcha prizes today.")["accepted"]


# ---- 凍結契約・隔離 ----
def test_frozen_candidates_independent_of_asr_text_and_ledger_not_mutated():
    a = m1.freeze_candidates(G, ledger_snapshot=LEDGER, segment_started_at=T0)
    b = m1.freeze_candidates(G, ledger_snapshot=LEDGER, segment_started_at=T0)
    assert a.candidate_set_hash == b.candidate_set_hash
    assert "gotcha" not in {fw.word for fw in a.words}  # ASR語は候補集合の入力にならない
    L = copy.deepcopy(LEDGER)
    run(G, GOT, ledger=L)
    assert L == LEDGER


def test_not_imported_from_production_modules():
    offenders = []
    for f in glob.glob(os.path.join(ROOT, "*.py")):
        txt = open(f, encoding="utf-8", errors="ignore").read()
        if "trial_direct_ledger_phoneme" in txt:
            offenders.append(os.path.basename(f))
    assert offenders == [], offenders


def test_default_off_isolation_no_production_behavior_change():
    import er006_preprod_hardening_01_validation as val
    before = val.classify_asr_match(G, GOT, segment_id=SEG).classification
    importlib.reload(T)
    assert val.classify_asr_match(G, GOT, segment_id=SEG).classification == before == "TRUE_CONTENT_MISMATCH"
