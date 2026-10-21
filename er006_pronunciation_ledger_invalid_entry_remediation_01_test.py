# ============================================================
# PRONUNCIATION-LEDGER-INVALID-ENTRY-REMEDIATION-01 test
# 実行: .venv/Scripts/python.exe -m pytest -q er006_pronunciation_ledger_invalid_entry_remediation_01_test.py
# 不正entry(canonical="unknown"等)がPhrase List/M1/TTS/再researchへ供給されないこと、正当entry(Melos等)は維持されること。
# ============================================================
from __future__ import annotations

import os
import shutil

import pytest

import er006_m1_multi_candidate_01 as M
import er006_pronunciation_ledger_01 as L
import er006_secondary_asr_01 as sec

CAS = L.CASCADE_UNRESOLVED_ENTITY_TYPE


@pytest.fixture()
def tmp_ledger():
    orig = L.LEDGER_PATH
    d = "er006_output/_test_plir1_tmp"
    if os.path.exists(d):
        shutil.rmtree(d)
    L.LEDGER_PATH = d + "/ledger.json"
    yield
    L.LEDGER_PATH = orig
    shutil.rmtree(d, ignore_errors=True)


def _reg(surface, canonical, hint="X-hint", conf="low", et=CAS, **kw):
    return L.upsert(L.LedgerKey(surface=surface, entity_type=et),
                    {"canonical_spelling": canonical, "pronunciation_hint": hint, "confidence": conf,
                     "expected_pronunciation_ipa": "/ʌnˈnoʊn/", "sources": ["https://x"], **kw})


@pytest.mark.parametrize("surface,canon", [("us", "unknown"), ("plus", "cascade"), ("main story", "cascade"),
                                           ("another voice", "ASR Cascade"), ("one voice", "one voice unknown")])
def test_known_bad_registrations_are_invalid(surface, canon):
    assert L.entry_invalid_reason(surface, CAS, {"canonical_spelling": canon})


@pytest.mark.parametrize("surface,canon", [("melos", "Melos"), ("canele", "canelé"), ("kristie tse", "Kristie Tse"),
                                           ("toteme", "TOTEME"), ("familymart", "FamilyMart"), ("muse", "muse")])
def test_legit_registrations_stay_valid(surface, canon):
    assert L.entry_invalid_reason(surface, CAS, {"canonical_spelling": canon}) is None


def test_non_cascade_placeholder_canonical_is_invalid():
    assert L.entry_invalid_reason("Foo", "person", {"canonical_spelling": "unknown"})
    assert L.entry_invalid_reason("Foo", "person", {"canonical_spelling": "Foo"}) is None


def test_upsert_auto_disables_invalid_and_never_supplied(tmp_ledger):
    lid = _reg("us", "unknown", hint="uhn-NOHN", conf="medium")
    e = L.lookup(L.LedgerKey(surface="us", entity_type=CAS))
    assert e["ledger_disabled"] is True and e["ledger_disabled_reason"].startswith("auto:")
    assert e["surface"] == "us"  # 履歴は残す(削除しない)
    text = "trade between Gulf states and the US. Tell us about it."
    assert L.get_hint_for_text(text, min_confidence="low") == []
    assert L.get_hint_for_text(text, min_confidence="low", exclude_entity_types=set(), apply_tts_injection_filter=True) == []
    assert L.get_low_confidence_entries_for_text(text) == []
    assert lid in L._load()


def test_valid_cascade_entry_still_supplied_and_hint_cleaned(tmp_ledger):
    _reg("melos", "Melos", hint="MEE-lahs（英国寄りなら MEE-loss）")
    e = L.lookup(L.LedgerKey(surface="melos", entity_type=CAS))
    assert e["pronunciation_hint"] == "MEE-lahs" and not e["ledger_disabled"]
    assert "MEE-loss" in e["ambiguity_note"]  # 原文は注記に保存
    hits = L.get_hint_for_text("Melos ran to the city.", min_confidence="low")
    assert [h["canonical_spelling"] for h in hits] == ["Melos"]


def test_disabled_flag_survives_reupsert(tmp_ledger):
    _reg("zzqx", "Zzqx")
    lid = L.LedgerKey(surface="zzqx", entity_type=CAS).ledger_id()
    L.set_ledger_disabled(lid, "manual")
    _reg("zzqx", "Zzqx", conf="high")  # 低confidence再research相当の後続upsert
    e = L.lookup(L.LedgerKey(surface="zzqx", entity_type=CAS))
    assert e["ledger_disabled"] is True and e["ledger_disabled_reason"] == "manual"
    assert L.get_hint_for_text("zzqx here", min_confidence="low") == []


def test_unconfirmed_confidence_never_supplied(tmp_ledger):
    _reg("zzqy", "Zzqy", conf="unconfirmed")
    assert L.get_hint_for_text("zzqy here", min_confidence="low") == []


def test_m1_c2_excludes_ledger_disabled():
    led = {"k1": {"surface": "zzqx", "entity_type": CAS, "canonical_spelling": "zzqx", "expected_pronunciation_ipa": "/ˈkæt/",
                  "sources": ["u"], "confidence": "medium", "updated_at": "2026-01-01T00:00:00", "ledger_disabled": True,
                  "ledger_disabled_reason": "t"}}
    got, excluded, _ = M._c2_candidates("zzqx", led, None)
    assert got == [] and excluded[0]["reason"] == "ledger_disabled"
    led["k1"]["ledger_disabled"] = False
    got, _, _ = M._c2_candidates("zzqx", led, None)
    assert got


def test_review_lookup_does_not_return_or_research_disabled_entry(tmp_ledger, monkeypatch):
    _reg("us", "unknown", hint="uhn-NOHN")

    def boom(*a, **k):
        raise AssertionError("research must not be called for an existing (disabled) entry")
    monkeypatch.setattr(sec.pronun_research, "research_pronunciations", boom)
    assert sec._resolve_unresolved_entity_for_review("us") is None


def test_research_failure_registers_nothing_supplyable(tmp_ledger, monkeypatch):
    monkeypatch.setattr(sec.pronun_research, "research_pronunciations", lambda *a, **k: {"status": "FAILED", "http_status": 401})
    assert sec._resolve_unresolved_entity_for_review("Zzqz") is None
    assert L.get_hint_for_text("Zzqz here", min_confidence="low") == []


def test_research_returning_unknown_is_registered_disabled(tmp_ledger, monkeypatch):
    item = {"surface": "us", "entity_type": "unknown", "canonical_spelling": "unknown", "pronunciation_hint": "uhn-NOHN",
            "expected_pronunciation_ipa": "/ʌnˈnoʊn/", "alternate_pronunciations": [], "confidence": "low", "ambiguity_note": ""}
    monkeypatch.setattr(sec.pronun_research, "research_pronunciations",
                        lambda *a, **k: {"status": "OK", "items": [item], "citations": ["https://d"]})
    info = sec._resolve_unresolved_entity_for_review("us")  # Human Reviewへ誤情報を載せない(None)
    assert info is None
    assert L.lookup(L.LedgerKey(surface="us", entity_type=CAS))["ledger_disabled"] is True  # 記録は残る
    assert L.get_hint_for_text("the US and us", min_confidence="low") == []


# ---- 本番Ledger(現行ledger.json)の健全性ガード ----
def test_real_ledger_has_no_active_invalid_entry():
    hc = L.ledger_health_check()
    assert hc["invalid_but_still_active"] == []


def test_real_ledger_supply_clean_and_melos_kept():
    us = "Trump said trade between Gulf states and the US could grow. Tell us more, plus a main story and one voice."
    phrases = [h["canonical_spelling"].lower() for h in L.get_hint_for_text(us, min_confidence="low")]
    assert not ({"unknown", "cascade", "asr cascade", "one voice unknown"} & set(phrases))
    mel = [h["canonical_spelling"] for h in L.get_hint_for_text("Melos was angry. Melos ran.", min_confidence="low")]
    assert "Melos" in mel
    for h in L.get_hint_for_text("Melos ran.", min_confidence="low"):
        assert "（" not in h["pronunciation_hint"] and "(" not in h["pronunciation_hint"]
