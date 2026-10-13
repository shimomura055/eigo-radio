# -*- coding: utf-8 -*-
"""er006_m1_multi_candidate_01 の unit test(API 0 / 有料呼出なし / Ledger は読取のみ)。
委任_01 の合成24+F1反例19 + OF-178(F1 explained 必須)+ OF-179(凍結・注入)+ OF-180(ASR 非依存契約)+ OF-181(C2 除外)
+ OF-183(矛盾拒否)+ OF-187(audit/集計)。"""
import ast
import dataclasses
import hashlib
import inspect
import json
import os
import sys

import pytest

sys.path.insert(0, os.getcwd())
import er006_m1_multi_candidate_01 as M  # noqa: E402
import er006_preprod_hardening_01_validation as val  # noqa: E402
import er006_secondary_asr_01 as sec  # noqa: E402

LEDGER_PATH = "er006_output/pronunciation_ledger_01/ledger.json"
LED = json.load(open(LEDGER_PATH, encoding="utf-8"))
T0 = "2099-01-01T00:00:00"  # 現Ledgerの全エントリより後=全て『segment 開始前』扱い


def final(canonical, asr, led=None, secondary_text=None, m1_enabled=True):
    """Production 相当の最終判定(Primary 分類 → alternate pass → M1)。戻り値 (pass, basis, M1Result|None)。"""
    led = LED if led is None else led
    cls = val.classify_asr_match(canonical, asr)
    if cls.should_pass:
        return True, "prod:" + cls.classification, None
    if sec._step_alternate_pass(cls):
        return True, "alt", None
    fz = M.freeze_candidates(canonical, ledger_snapshot=led, segment_started_at=T0)
    r = M.m1_multi_candidate_judge(canonical, asr, fz, base_cls=cls, secondary_asr_text=secondary_text, m1_enabled=m1_enabled)
    return r.accepted, ("m1:" + r.reason), r


# ----------------------------------------------------------------- IPA
def test_ipa_table():
    assert M.ipa_to_arpa("/ˈmɛloʊs/") == ("M", "EH", "L", "OW", "S")
    assert M.ipa_to_arpa("/ˈmiː.lɑːs/") == ("M", "IY", "L", "AA", "S")
    assert M.ipa_to_arpa("/ˈmɪlɒs/") == ("M", "IH", "L", "AA", "S")
    assert M.ipa_to_arpa("/otˈtoːni/") is None and M.ipa_to_arpa("oh-TOH-nee") is None and M.ipa_to_arpa("") is None


# ----------------------------------------------------------------- 凍結(OF-179)
def test_freeze_has_no_asr_argument_and_is_deterministic():
    params = inspect.signature(M.freeze_candidates).parameters
    assert not any("asr" in p for p in params)
    a = M.freeze_candidates("Melos said.", ledger_snapshot=LED, segment_started_at=T0)
    b = M.freeze_candidates("Melos said.", ledger_snapshot=LED, segment_started_at=T0)
    assert a.candidate_set_hash == b.candidate_set_hash


def test_frozen_object_is_immutable():
    fz = M.freeze_candidates("Melos said.", ledger_snapshot=LED, segment_started_at=T0)
    with pytest.raises(dataclasses.FrozenInstanceError):
        fz.candidate_set_hash = "x"
    with pytest.raises(dataclasses.FrozenInstanceError):
        fz.words[0].candidates[0].pron = ()  # type: ignore
    assert isinstance(fz.words, tuple) and isinstance(fz.words[0].candidates, tuple)


def test_judge_does_not_recompute_candidates_from_ledger_or_cmu_for_canonical():
    """Ledger を凍結後に書き換えても(Tier3 が segment 内で書込んだ想定)、凍結物を渡す限り判定は不変。"""
    led = json.loads(json.dumps(LED))
    fz = M.freeze_candidates("Melos said.", ledger_snapshot=led, segment_started_at=T0)
    cls = val.classify_asr_match("Melos said.", "Mello said.")
    r1 = M.m1_multi_candidate_judge("Melos said.", "Mello said.", fz, base_cls=cls)
    for e in led.values():  # 全 Ledger を破壊的に変更
        e["alternate_pronunciations"] = []
        e["expected_pronunciation_ipa"] = ""
    r2 = M.m1_multi_candidate_judge("Melos said.", "Mello said.", fz, base_cls=cls)
    assert r1.accepted and r2.accepted and r1.audit["candidate_set_hash"] == r2.audit["candidate_set_hash"] == fz.candidate_set_hash
    # 新しく凍結し直すと(=別 segment)候補は消える。これは意図どおり(再凍結は segment 境界のみ)
    fz2 = M.freeze_candidates("Melos said.", ledger_snapshot=led, segment_started_at=T0)
    assert fz2.candidate_set_hash != fz.candidate_set_hash
    assert not M.m1_multi_candidate_judge("Melos said.", "Mello said.", fz2, base_cls=cls).accepted


def test_judge_signature_takes_frozen_and_no_ledger_param():
    p = inspect.signature(M.m1_multi_candidate_judge).parameters
    assert "frozen" in p and "ledger_snapshot" not in p and "ledger" not in p


def test_entries_updated_at_or_after_segment_start_are_not_candidates():
    led = {"k": {"surface": "zzqx", "entity_type": "cascade_unresolved_entity", "canonical_spelling": "zzqx", "confidence": "low",
                 "expected_pronunciation_ipa": "/ˈkæt/", "alternate_pronunciations": [], "sources": ["https://x"],
                 "updated_at": "2026-10-13T12:00:00"}}
    before = M.freeze_candidates("zzqx", ledger_snapshot=led, segment_started_at="2026-10-13T13:00:00")
    after = M.freeze_candidates("zzqx", ledger_snapshot=led, segment_started_at="2026-10-13T11:00:00")
    assert len(before.word("zzqx").candidates) == 1
    assert len(after.word("zzqx").candidates) == 0
    assert any("updated_at_not_before_segment_start" in x for x in after.word("zzqx").excluded)


def test_cap_enforced_and_overflow_recorded():
    led = {"x": {"surface": "zzqx", "entity_type": "cascade_unresolved_entity", "canonical_spelling": "zzqx", "confidence": "low",
                 "sources": ["s"], "expected_pronunciation_ipa": "/ˈkæt/",
                 "alternate_pronunciations": ["/ˈkɪt/", "/ˈkʊt/", "/ˈkɛt/", "/ˈkʌt/", "/ˈkɑt/", "/ˈkɔt/", "/ˈkæp/"]}}
    fw = M.freeze_candidates("zzqx", ledger_snapshot=led, segment_started_at=T0).word("zzqx")
    assert len(fw.candidates) == M.DEFAULT_MAX_PER_WORD and fw.overflow_dropped == 2 and fw.n_before_cap == 8


# ----------------------------------------------------------------- C2 除外(OF-181)
def _led(surface, canon, ipa, sources=("s",), alt=(), etype="cascade_unresolved_entity"):
    return {"k": {"surface": surface, "entity_type": etype, "canonical_spelling": canon, "confidence": "low", "sources": list(sources),
                  "expected_pronunciation_ipa": ipa, "alternate_pronunciations": list(alt)}}


def test_c2_only_for_cmu_oov_words():
    fw = M.freeze_candidates("us", ledger_snapshot=_led("us", "us", "/ʌnˈnoʊn/"), segment_started_at=T0).word("us")
    assert all(c.source == "C1_cmu_variant" for c in fw.candidates)


def test_c2_excludes_canonical_spelling_mismatch():
    fw = M.freeze_candidates("zzqx", ledger_snapshot=_led("zzqx", "unknown", "/ʌnˈnoʊn/"), segment_started_at=T0).word("zzqx")
    assert not fw.candidates and any("canonical_spelling_differs_from_surface" in x for x in fw.excluded)


def test_c2_excludes_empty_sources():
    fw = M.freeze_candidates("zzqx", ledger_snapshot=_led("zzqx", "zzqx", "/ˈkæt/", sources=()), segment_started_at=T0).word("zzqx")
    assert not fw.candidates and any("sources_empty" in x for x in fw.excluded)


def test_c2_excludes_ja_reading_and_non_english_label():
    assert not M.freeze_candidates("zzqx", ledger_snapshot=_led("zzqx", "zzqx", "/ˈkæt/", etype="ja_reading_katakana"),
                                   segment_started_at=T0).word("zzqx").candidates
    fw = M.freeze_candidates("zzqx", ledger_snapshot=_led("zzqx", "zzqx", "native Swedish /ˈkæt/"), segment_started_at=T0).word("zzqx")
    assert not fw.candidates


def test_low_confidence_preserved_not_upgraded():
    fw = M.freeze_candidates("Melos said.", ledger_snapshot=LED, segment_started_at=T0).word("melos")
    assert fw.candidates and all(c.confidence == "low" and c.source.startswith("C2") for c in fw.candidates)
    prons = [c.pron for c in fw.candidates]
    assert ("M", "EH", "L", "OW", "S") in prons and ("M", "IY", "L", "AA", "S") in prons


# ----------------------------------------------------------------- ASR 非依存契約(OF-180)
def test_research_input_is_canonical_side_only():
    import er006_pronunciation_research_01 as R
    assert list(inspect.signature(R.build_user_message).parameters) == ["entities"]
    msg = R.build_user_message([{"surface": "Melos", "entity_type": "unknown", "risk_reason": "fixed text"}])
    assert "Melos" in msg
    for fn in ("er006_secondary_asr_01.py", "er025_entity_pronunciation_resolver_core_01.py"):
        tree = ast.parse(open(fn, encoding="utf-8").read())
        found = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.Dict):
                keys = {k.value for k in node.keys if isinstance(k, ast.Constant) and isinstance(k.value, str)}
                if "risk_reason" in keys:
                    found += 1
                    assert keys <= {"surface", "entity_type", "risk_reason"}, (fn, keys)
                    for k, v in zip(node.keys, node.values):
                        if isinstance(k, ast.Constant) and k.value == "risk_reason":
                            assert isinstance(v, ast.Constant), (fn, "risk_reason must be a constant string, not ASR-derived")
        assert found >= 1, fn


# ----------------------------------------------------------------- OF-178 F1 explained 必須
def test_of178_single_melos_left_nonpass():
    ok, basis, r = final("Melos left.", "Mellow left.")
    assert not ok and r.reason == M.R_NOT_EXPLAINED


def test_of178_repeated_word_t8_nonpass():
    ok, basis, r = final("Melos said Melos left.", "Mello said Mellow left.")
    assert not ok and r.reason == M.R_NOT_EXPLAINED


def test_of178_sibilant_next_word_pass():
    ok, basis, r = final("Melos said.", "Mello said.")
    assert ok and r.reason == M.ACCEPT_REASON and r.pass_with_warning
    assert r.subs[0]["rule"] == "drop_final_S_or_Z" and r.audit["f1_explained"]


def test_of178_add_s_type():
    led = _led("soen", "soen", "/ˈsoʊn/")
    ok, basis, r = final("Soen spoke.", "Sones spoke.", led)
    assert ok and r.subs[0]["rule"] == "add_s", (basis, r and r.audit)
    ok2, basis2, r2 = final("Soen left.", "Sones left.", led)  # 次語が歯擦音でない=Pattern C 不発
    assert not ok2 and r2.reason == M.R_NOT_EXPLAINED


def test_of178_add_s_repeated_word_second_position_unexplained():
    led = _led("soen", "soen", "/ˈsoʊn/")
    ok, _, r = final("Soen spoke. Soen left.", "Sones spoke. Sones left.", led)
    assert not ok


# ----------------------------------------------------------------- 委任_01 合成24(OF-178 反映後の期待)
import er077_m1_oov_multi_pronunciation_01_eval as E  # noqa: E402  (SYNTH データのみ使用)

CHANGED_BY_OF178 = {("Melos said Melos left.", "Mello said Mellow left."): "NONPASS"}


@pytest.mark.parametrize("kind,c,a,exp,note,fake", E.SYNTH)
def test_synthetic_cases(kind, c, a, exp, note, fake):
    led = dict(LED)
    if fake:
        led["_fake_" + fake["surface"]] = dict(fake, canonical_spelling=fake["surface"], sources=["fake-test-source"])
    expected = CHANGED_BY_OF178.get((c, a), exp)
    ok, basis, r = final(c, a, led)
    assert ok == expected.startswith("PASS"), (kind, c, a, basis)


COUNTER_CASES = __import__("er075_m1_f1_production_wiring_01_census").COUNTER


@pytest.mark.parametrize("c,a,exp", COUNTER_CASES)
def test_f1_counterexamples_unchanged(c, a, exp):
    ok, basis, r = final(c, a)
    if exp == "nonpass":
        assert not ok, (c, a, basis)
    elif exp == "pass":
        assert ok, (c, a, basis)
    assert r is None or not r.accepted  # M1 はこれらの新規受理に関与しない


# ----------------------------------------------------------------- 入口条件
def test_not_applicable_paths():
    fz = M.freeze_candidates("Melos said.", ledger_snapshot=LED, segment_started_at=T0)
    assert M.m1_multi_candidate_judge("Melos said.", "Mello said.", fz, m1_enabled=False).reason == M.R_DISABLED
    assert M.m1_multi_candidate_judge("Melos said.", "Mello said.", fz, lang="ja-JP").reason == M.R_LANG
    empty = M.freeze_candidates("The cat sat.", ledger_snapshot={}, segment_started_at=T0)
    assert M.m1_multi_candidate_judge("The cat sat.", "The cat sit.", dataclasses.replace(empty, words=()) ).reason == M.R_NO_FROZEN


def test_protected_fail_blocks_m1():
    ok, _, r = final("Melos said he did not go.", "Mello said he did go.")
    assert not ok and r.reason in (M.R_NOT_UNCERTAIN, M.R_PROTECTED_FAIL)
    ok, _, r = final("Melos said 5 cats sleep.", "Mello said 6 cats sleep.")
    assert not ok


def test_no_match_reason_telemetry():
    ok, _, r = final("Melos said.", "Milo said.")
    assert not ok and r.no_match_reason == M.NM_NO_PHONEME_MATCH
    ok, _, r = final("Melos said.", "Melas said.")
    assert not ok and r.no_match_reason == M.NM_ASR_NOT_IN_CMU
    ok, _, r = final("Cleos said.", "Clio said.", {})
    assert not ok and r.no_match_reason == M.NM_NO_CANDIDATES


# ----------------------------------------------------------------- 矛盾拒否(OF-183)
def test_secondary_contradiction_rejects():
    c = "Melos said he did not go."
    ok, _, r = final("Melos said.", "Mello said.", secondary_text="Melos did not say.")
    assert not ok and r.reason == M.R_SECONDARY_CONTRADICTION and r.audit["no_match_reason"].startswith("contradiction:")
    ok, _, r = final("Melos said cats.", "Mello said cats.", secondary_text="Mello said dogs.")
    assert not ok and r.reason == M.R_SECONDARY_CONTRADICTION


def test_secondary_agree_is_telemetry_not_required():
    ok, _, r = final("Melos said.", "Mello said.", secondary_text="Mellow said.")
    assert ok and r.secondary_agree is True and r.audit["secondary_state"] == "m1_accept"
    ok, _, r = final("Melos said.", "Mello said.", secondary_text="Milo said.")  # 同意しない=矛盾ではない
    assert ok and r.secondary_agree is False
    ok, _, r = final("Melos said.", "Mello said.", secondary_text=None)
    assert ok and r.audit["secondary_state"] == "not_provided"
    ok, _, r = final("Melos said.", "Mello said.", secondary_text="Melos said.")
    assert ok and r.audit["secondary_state"] == "native_pass" and r.secondary_agree is True


# ----------------------------------------------------------------- audit / 集計(OF-187)
def test_audit_fields_and_aggregate():
    ok, _, r = final("Melos said.", "Mello said.", secondary_text="Mellow said.")
    a = r.audit
    for k in ("candidate_set_hash", "original_asr", "normalized_asr", "acceptance_reason", "subs", "ledger_keys", "secondary_agree",
              "candidates_frozen", "m1_version"):
        assert k in a, k
    s = a["subs"][0]
    for k in ("ledger_key", "updated_at", "ipa_raw", "source", "confidence", "rule", "pron", "all_matching_candidates"):
        assert k in s, k
    assert s["ledger_key"] and s["confidence"] == "low" and s["source"] == "C2_ledger_alt"
    agg = M.aggregate_by_ledger_key([a, a])
    assert agg[s["ledger_key"]]["accept_count"] == 2 and agg[s["ledger_key"]]["confidences"] == ["low"]


# ----------------------------------------------------------------- Ledger 非破壊
def test_module_never_writes_ledger():
    src = open("er006_m1_multi_candidate_01.py", encoding="utf-8").read()
    assert "upsert" not in src and "open(" not in src and "requests" not in src
    md5 = hashlib.md5(open(LEDGER_PATH, "rb").read()).hexdigest()
    final("Melos said.", "Mello said.")
    assert hashlib.md5(open(LEDGER_PATH, "rb").read()).hexdigest() == md5
