# ============================================================
# er006_pronunciation_ledger_01_test.py
# ============================================================
# 実行方法: .venv/Scripts/python.exe er006_pronunciation_ledger_01_test.py
from __future__ import annotations

import os
import shutil

import er006_pronunciation_ledger_01 as ledger


def _use_temp_ledger(test_fn):
    orig_path = ledger.LEDGER_PATH
    tmp_path = "er006_output/_test_pronunciation_ledger_tmp/ledger.json"
    if os.path.exists(os.path.dirname(tmp_path)):
        shutil.rmtree(os.path.dirname(tmp_path))
    ledger.LEDGER_PATH = tmp_path
    try:
        test_fn()
    finally:
        ledger.LEDGER_PATH = orig_path
        if os.path.exists(os.path.dirname(tmp_path)):
            shutil.rmtree(os.path.dirname(tmp_path))


def test_cache_miss_then_hit():
    def run():
        key = ledger.LedgerKey(surface="Ottoni", entity_type="person")
        assert ledger.lookup(key) is None
        ledger.upsert(key, {"pronunciation_hint": "oh-TOH-nee", "confidence": "medium"})
        hit = ledger.lookup(key)
        assert hit is not None
        assert hit["pronunciation_hint"] == "oh-TOH-nee"
    _use_temp_ledger(run)
    print("PASS: test_cache_miss_then_hit")


def test_entity_type_avoids_collision():
    # 同じ綴りでも entity_type が違えば別entryとして扱われること
    # (人名の"Jordan"と地名の"Jordan"を混同しない)。
    def run():
        key_person = ledger.LedgerKey(surface="Jordan", entity_type="person")
        key_place = ledger.LedgerKey(surface="Jordan", entity_type="place")
        assert key_person.ledger_id() != key_place.ledger_id()
        ledger.upsert(key_person, {"pronunciation_hint": "JOR-dan (name)", "confidence": "high"})
        ledger.upsert(key_place, {"pronunciation_hint": "jor-DAHN (country, Arabic origin)", "confidence": "high"})
        assert ledger.lookup(key_person)["pronunciation_hint"] != ledger.lookup(key_place)["pronunciation_hint"]
    _use_temp_ledger(run)
    print("PASS: test_entity_type_avoids_collision")


def test_get_hint_for_text_respects_min_confidence():
    def run():
        key_low = ledger.LedgerKey(surface="Foo", entity_type="person")
        key_high = ledger.LedgerKey(surface="Bar", entity_type="person")
        ledger.upsert(key_low, {"pronunciation_hint": "foo-hint", "confidence": "low"})
        ledger.upsert(key_high, {"pronunciation_hint": "bar-hint", "confidence": "high"})
        text = "This mentions Foo and Bar together."
        hits_medium = ledger.get_hint_for_text(text, min_confidence="medium")
        surfaces = {h["surface"] for h in hits_medium}
        assert "Bar" in surfaces
        assert "Foo" not in surfaces, "low confidenceはmin_confidence=mediumで除外されるはず"
        hits_low = ledger.get_hint_for_text(text, min_confidence="low")
        surfaces_low = {h["surface"] for h in hits_low}
        assert {"Foo", "Bar"} == surfaces_low
    _use_temp_ledger(run)
    print("PASS: test_get_hint_for_text_respects_min_confidence")


def test_get_hint_for_text_no_false_match():
    def run():
        key = ledger.LedgerKey(surface="Ottoni", entity_type="person")
        ledger.upsert(key, {"pronunciation_hint": "oh-TOH-nee", "confidence": "high"})
        text_without = "This text does not mention that surname at all."
        hits = ledger.get_hint_for_text(text_without, min_confidence="low")
        assert hits == []
    _use_temp_ledger(run)
    print("PASS: test_get_hint_for_text_no_false_match")


def test_upsert_research_result_matches_by_surface():
    def run():
        entities = [{"surface": "Ottoni", "entity_type": "person", "risk_reason": "x"}]
        research_items = [{"surface": "Ottoni", "canonical_spelling": "Ottoni",
                            "pronunciation_hint": "oh-TOH-nee", "confidence": "medium",
                            "alternate_pronunciations": [], "ambiguity_note": "", "language_origin": "Italian",
                            "expected_pronunciation_ipa": ""}]
        ids = ledger.upsert_research_result(entities, research_items, sources=["https://example.com"])
        assert len(ids) == 1
        key = ledger.LedgerKey(surface="Ottoni", entity_type="person")
        entry = ledger.lookup(key)
        assert entry["sources"] == ["https://example.com"]
    _use_temp_ledger(run)
    print("PASS: test_upsert_research_result_matches_by_surface")


if __name__ == "__main__":
    test_cache_miss_then_hit()
    test_entity_type_avoids_collision()
    test_get_hint_for_text_respects_min_confidence()
    test_get_hint_for_text_no_false_match()
    test_upsert_research_result_matches_by_surface()
    print("ALL TESTS PASSED")
