# ============================================================
# er011_b1_connected_speech_validator_01_f1_test_01.py
# ASR-PHONETIC-EQUIVALENCE-M1-F1-PRODUCTION-WIRING-01 委任_03
# ============================================================
# F1(連結発音Validatorの「最初の食い違い1か所だけでACCEPT」欠陥の是正)のunit/replay test。
# 実行: .venv\Scripts\python.exe er011_b1_connected_speech_validator_01_f1_test_01.py
#       または .venv\Scripts\python.exe -m pytest er011_b1_connected_speech_validator_01_f1_test_01.py -q
# 共有telemetryへ追記しない(append_telemetry_logをno-op化)。API呼出なし(Secondary/localはmock)。
from __future__ import annotations

import er006_preprod_hardening_01_validation as val
import er006_secondary_asr_01 as secondary
import er008_disfluency_qa_18 as disfluency_qa
import er011_b1_connected_speech_validator_01 as csv3
import er011_connected_speech_equivalence_layer_production_01 as cs_equiv
import er021_en_asr_semantic_equivalence_production_01 as _se

_se.append_telemetry_log = lambda *a, **k: None  # telemetry保護

SEGS = ["full_story_part1", None]  # None=dialogue相当(role gate非適用)

USER_EXAMPLE = ("The studies suggest cats today.", "The study suggests dogs today.")

# 正常連結6件(委任_02反例セット: PASS維持が必須)
NORMAL6 = [
    ("The studies suggest cats today.", "The study suggests cats today."),
    ("The studies suggest cats today.", "The study suggest cats today."),
    ("The studies suggest that cats sleep.", "The study suggests that cats sleep."),
    ("The company opened today and it closed to the public.", "The company open today and it closed to the public."),
    ("The survey suggests that cats sleep.", "The surveys suggest that cats sleep."),
    ("Their studies suggest cats and their survey suggests cats.", "Their study suggests cats and their surveys suggest cats."),
]

# 反例(非PASS必須)。最初のPATTERN説明差分+後続の説明不能差分(11件=旧版でCONNECTED_SPEECH系PASSだったもの)
COUNTER11 = [
    USER_EXAMPLE,
    ("The studies suggest that cats sleep.", "The study suggests that dogs sleep."),
    ("The studies suggest that cats sleep.", "The study suggests that cats sleep more."),
    ("The studies suggest that cats sleep.", "The study suggests cats sleep."),
    ("The studies suggest that cats sleep.", "The study suggests that cats slept."),
    ("The studies suggest that cats sleep.", "The study suggests that cats."),
    ("The company opened today and it closed to the public.", "The company open today and it closes to the public."),
    ("The company opened today and it closed to the public.", "The company open today and it closed to the people."),
    ("The survey suggests that cats sleep.", "The surveys suggest that dogs sleep."),
    ("Their studies suggest cats and their survey suggests cats.", "Their study suggests cats and their surveys suggest dogs."),
    ("The studies suggest that Rex sleeps.", "The study suggests that Max sleeps."),
]
# もともと非PASS(F1前から)の反例
COUNTER_ALREADY_NONPASS = [
    ("The studies suggest that cats sleep.", "The study suggests that cats did not sleep."),
    ("The studies suggest that 5 cats sleep.", "The study suggests that 6 cats sleep."),
]


def _cls(c, a, seg):
    return val.classify_asr_match(c, a, segment_id=seg)


# ------------------------------------------------------------
# csv3.classify_connected_speech(F1本体)
# ------------------------------------------------------------
def test_user_example_is_not_accepted_and_residual_is_first_unexplained_diff():
    r = csv3.classify_connected_speech(*USER_EXAMPLE)
    assert r["new_judgment"] == "UNCLASSIFIED_FALLS_THROUGH_TO_EXISTING"
    assert len(r["f1_residual"]) == 1 and r["f1_residual"][0]["canonical"] == ["cats"]
    assert r["f1_residual"][0]["asr"] == ["dogs"]
    # OF-159(a): diffは「説明済み差分(studies)」ではなく最初の残差(cats)
    assert r["diff"]["canonical_word"] == "cats" and r["diff"]["asr_word"] == "dogs"
    assert r["f1_residual_kind"] == "content"
    assert [e["canonical"] for e in r["f1_explained"]] == ["studies"]
    # F1前の旧挙動は誤ACCEPTだった(このtestが欠陥再現を保証する)
    assert csv3._classify_first_diff(*USER_EXAMPLE)["new_judgment"] == "CONNECTED_SPEECH_ACCEPT"


def test_normal_connected_speech_still_accepted_with_observability_keys():
    for c, a in NORMAL6:
        r = csv3.classify_connected_speech(c, a)
        assert r["new_judgment"] in ("CONNECTED_SPEECH_ACCEPT", "CONNECTED_SPEECH_RESEGMENTATION"), (c, a, r["new_judgment"])
        assert r["f1_residual"] == [] and r["f1_explained"], (c, a)
        for k in ("f1_version", "f1_all_diffs", "f1_explained", "f1_residual", "f1_residual_kind"):
            assert k in r, k
        assert r["f1_residual_kind"] == "none"
        # 旧キーは後方互換
        for k in ("diff", "rule", "expected_phoneme_boundary", "new_judgment", "false_accept_risk"):
            assert k in r, k


def test_no_diff_and_unclassified_unchanged():
    r = csv3.classify_connected_speech("The cat sat.", "The cat sat.")
    assert r["new_judgment"] == "NO_DIFF" and r["f1_residual"] == []
    c, a = "The report shows a clear increase in visits.", "The report shows a clear decrease in visits."
    assert csv3.classify_connected_speech(c, a)["new_judgment"] == csv3._classify_first_diff(c, a)["new_judgment"]


def test_benign_is_limited_to_articles_and_regular_plurals():
    base_c = "The studies suggest that cats are asleep."
    # 冠詞のみの差は許容(Pattern A説明差分+後続の冠詞欠落。最初の差分がPattern非該当の場合はF1前同様に対象外=緩和なし)
    assert csv3.classify_connected_speech("The studies suggest the cats today.", "The study suggests cats today.")["new_judgment"] \
        == "CONNECTED_SPEECH_ACCEPT"
    # 時制/前置詞/接続詞は残差(OF-160)
    for c, a in [(base_c, "The study suggests that cats were asleep."),
                 ("The studies suggest cats in homes.", "The study suggests cats on homes."),
                 ("The studies suggest cats and dogs.", "The study suggests cats or dogs.")]:
        r = csv3.classify_connected_speech(c, a)
        assert r["new_judgment"] == "UNCLASSIFIED_FALLS_THROUGH_TO_EXISTING", (c, a)
        assert r["f1_residual"], (c, a)
    # 規則単複の1:1差(results/result、_is_benign_plural_pair準拠。cats/catは長さ条件で非benign=従来のprotected_checkと同じ)は許容
    r = csv3.classify_connected_speech("The studies suggest results today.", "The study suggests result today.")
    assert r["new_judgment"] == "CONNECTED_SPEECH_ACCEPT" and r["f1_residual"] == []


def test_number_difference_is_residual():
    r = csv3.classify_connected_speech(*COUNTER_ALREADY_NONPASS[1])
    assert r["new_judgment"] != "CONNECTED_SPEECH_ACCEPT"
    r2 = csv3.classify_connected_speech("The studies suggest 5 cats.", "The study suggests 6 cats.")
    assert r2["new_judgment"] == "UNCLASSIFIED_FALLS_THROUGH_TO_EXISTING"
    assert any(x["op"] == "number" for x in r2["f1_residual"])


# ------------------------------------------------------------
# classify_asr_match(Production経路、segment_id有/無=dialogue相当)
# ------------------------------------------------------------
def test_counter_examples_are_non_pass_in_production_path():
    for seg in SEGS:
        for c, a in COUNTER11 + COUNTER_ALREADY_NONPASS:
            r = _cls(c, a, seg)
            assert r.should_pass is False, (seg, c, a, r.classification)
        # 旧版(F1前)では11件がCONNECTED_SPEECH系でPASSしていたことを確認(testの意味づけ)
        for c, a in COUNTER11:
            assert csv3._classify_first_diff(c, a)["new_judgment"] in (
                "CONNECTED_SPEECH_ACCEPT", "CONNECTED_SPEECH_RESEGMENTATION"), (c, a)


def test_normal_connected_speech_still_passes_in_production_path():
    for seg in SEGS:
        for c, a in NORMAL6:
            r = _cls(c, a, seg)
            assert r.should_pass is True, (seg, c, a, r.classification)


def test_residual_kind_routes_entity_only_residual_to_uncertain_not_true_mismatch():
    for seg in SEGS:
        r = _cls("The studies suggest that Rex sleeps.", "The study suggests that Max sleeps.", seg)
        assert r.classification == "ASR_VALIDATION_UNCERTAIN" and r.should_retry is False, r.classification
        assert r.connected_speech_info["f1_residual_kind"] == "entity_or_homophone_only"
        r2 = _cls(*USER_EXAMPLE, seg)
        assert r2.classification == "TRUE_CONTENT_MISMATCH" and r2.should_retry is True
        assert r2.connected_speech_info["f1_residual_kind"] == "content"


def test_accepted_result_records_f1_observability_in_connected_speech_info():
    r = _cls(*NORMAL6[0], "full_story_part1")
    info = r.connected_speech_info
    assert info["f1_version"] and info["f1_residual"] == [] and info["f1_explained"] and info["f1_all_diffs"]


# ------------------------------------------------------------
# Equivalence Layerガード(OF-159(b)) + cascade replay
# ------------------------------------------------------------
def test_equivalence_layer_refuses_when_residual_is_not_exactly_one():
    canonical = "Young travelers still showed strong interest in the results."
    primary = "Young travelers still show strong interest in the outcomes."
    existing = csv3.classify_connected_speech(canonical, primary)
    assert len(existing["f1_residual"]) >= 2
    r = cs_equiv.classify_connected_speech_equivalence(canonical, primary, canonical, canonical)
    assert r["layer_judgment"] == "NO_DELETION_SHAPED_DIFF"
    assert r["ineligible_reason"] == "F1_RESIDUAL_NOT_EXACTLY_ONE_AT_DIFF"
    # 既存の単一残差ケース(OPEN-122 accept例)は従来どおり評価される
    one = cs_equiv.classify_connected_speech_equivalence(
        canonical, "Young travelers still show strong interest in the results.", canonical, canonical)
    assert one["layer_judgment"].startswith("EQUIVALENCE_LAYER_")


def _replay(canonical, primary, secondary_text, seg):
    orig_sec = secondary.get_full_text_via_azure_stt_with_phrase_list
    orig_local = disfluency_qa.transcribe_verbatim
    calls = {"secondary": 0, "local": 0}

    def sec(*a, **k):
        calls["secondary"] += 1
        return secondary_text, None

    def loc(*a, **k):
        calls["local"] += 1
        return [{"text": w} for w in secondary_text.split()]
    secondary.get_full_text_via_azure_stt_with_phrase_list = sec
    disfluency_qa.transcribe_verbatim = loc
    try:
        r = secondary.evaluate_attempt_with_cascade_detail(
            canonical, primary, [], "dummy.wav", cascade_enabled=True,
            enable_connected_speech_equivalence_layer=True, segment_id=seg)
    finally:
        secondary.get_full_text_via_azure_stt_with_phrase_list = orig_sec
        disfluency_qa.transcribe_verbatim = orig_local
    return r, calls


def test_cascade_replay_user_example_stays_non_pass_with_supporting_secondary():
    c, a = USER_EXAMPLE
    for seg in SEGS:
        # Secondary/localが「最初の差分位置でcanonicalを支持する」転写(=canonical全文)を返す設定
        r, calls = _replay(c, a, c, seg)
        assert r["verified"] is False, (seg, r["classification"].classification)
        assert r["classification"].should_pass is False
        assert r["classification"].classification in ("TRUE_CONTENT_MISMATCH", "ASR_VALIDATION_UNCERTAIN")


def test_cascade_replay_multi_residual_after_first_eq_eligible_diff_stays_non_pass():
    canonical = "Young travelers still showed strong interest in the results."
    primary = "Young travelers still show strong interest in the outcomes."
    for seg in SEGS:
        r, calls = _replay(canonical, primary, canonical, seg)
        assert r["verified"] is False
        assert r["connected_speech_equivalence_layer_invoked"] is False
        assert calls == {"secondary": 0, "local": 0}


def test_cascade_replay_normal_connected_speech_still_passes():
    for seg in SEGS:
        for c, a in NORMAL6:
            r, _ = _replay(c, a, c, seg)
            assert r["verified"] is True, (seg, c, a, r["classification"].classification)


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print("PASS:", name)
    print("ALL PASS")


# run_project_regression.py(unittest discovery)から収集できるようにするためのwrapper
import unittest  # noqa: E402


class F1RegressionWrapper(unittest.TestCase):
    pass


for _n, _f in list(globals().items()):
    if _n.startswith("test_") and callable(_f):
        setattr(F1RegressionWrapper, _n, (lambda f: (lambda self: f()))(_f))
