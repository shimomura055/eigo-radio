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


def test_get_hint_for_text_word_boundary_no_substring_false_match():
    # PRONUNCIATION-RESOLUTION-ALL-ACTIVE-FAMILIES-PRODUCTION-01(Sonnet
    # 修正1回目、Opus L2 BLOCKER-1是正(i)+(iv)): 実データで確認された
    # 誤entry(surface="plus"/"mini"、entity_type=cascade_unresolved_entity)
    # と同型の再現。"surplus"/"minister"を含む英文でhits=0であること。
    def run():
        ledger.upsert(ledger.LedgerKey(surface="plus", entity_type="cascade_unresolved_entity"),
                       {"pronunciation_hint": "kass-KAYD", "confidence": "medium",
                        "canonical_spelling": "cascade"})
        ledger.upsert(ledger.LedgerKey(surface="mini", entity_type="cascade_unresolved_entity"),
                       {"pronunciation_hint": "MIN-ee", "confidence": "medium",
                        "canonical_spelling": "mini"})
        text = "The government reported a budget surplus and the minister spoke about it."
        hits = ledger.get_hint_for_text(text, min_confidence="low")
        assert hits == [], f"語境界なし部分一致が復活している: {hits}"
    _use_temp_ledger(run)
    print("PASS: test_get_hint_for_text_word_boundary_no_substring_false_match")


def test_get_hint_for_text_excludes_cascade_unresolved_entity_type():
    # BLOCKER-1是正(ii): TTS注入呼び出し元と同じ引数(exclude_entity_types)
    # を渡した場合、語境界内で一致していてもcascade_unresolved_entity型は
    # 除外されること。
    def run():
        ledger.upsert(ledger.LedgerKey(surface="plus", entity_type="cascade_unresolved_entity"),
                       {"pronunciation_hint": "kass-KAYD", "confidence": "medium"})
        text = "We saw a plus sign on the board."
        hits_default = ledger.get_hint_for_text(text, min_confidence="low")
        assert len(hits_default) == 1, "既定(exclude無し)ではASR Phrase List用途どおり一致するはず"
        hits_excluded = ledger.get_hint_for_text(
            text, min_confidence="low", exclude_entity_types={"cascade_unresolved_entity"})
        assert hits_excluded == [], "TTS注入呼び出し元相当の引数ではcascade_unresolved_entity型を除外するはず"
    _use_temp_ledger(run)
    print("PASS: test_get_hint_for_text_excludes_cascade_unresolved_entity_type")


def test_set_tts_injection_disabled_isolates_entry_without_deleting():
    # BLOCKER-1是正(iii): 本番Ledgerの誤entry隔離手段。削除せず
    # tts_injection_disabledフラグのみを立て、他フィールドは無変更。
    def run():
        key = ledger.LedgerKey(surface="ganis", entity_type="cascade_unresolved_entity")
        ledger_id = ledger.upsert(key, {"pronunciation_hint": "GANN-iss", "confidence": "low",
                                          "sources": ["https://example.com/ganis"]})
        ledger.set_tts_injection_disabled(ledger_id, "BLOCKER-1: 部分一致で無関係語へ誤発火した実例")
        entry = ledger.lookup(key)
        assert entry["tts_injection_disabled"] is True
        assert entry["sources"] == ["https://example.com/ganis"], "隔離フラグ以外のフィールドは無変更のはず"

        hits_phrase_list = ledger.get_hint_for_text("The ganis interview aired today.", min_confidence="low")
        assert len(hits_phrase_list) == 1, "ASR Phrase List用途(apply_tts_injection_filter無指定)は維持されるはず"
        hits_tts = ledger.get_hint_for_text(
            "The ganis interview aired today.", min_confidence="low", apply_tts_injection_filter=True)
        assert hits_tts == [], "隔離済みentryはTTS注入フィルタ有効時には除外されるはず"
    _use_temp_ledger(run)
    print("PASS: test_set_tts_injection_disabled_isolates_entry_without_deleting")


def test_ja_reading_entry_source_context_no_collision():
    # BLOCKER-2是正: 同じsurfaceでもsource_contextが異なれば別entryとして
    # 保存・参照できること(作品固有読みの分離)。
    def run():
        ledger.upsert_ja_reading_entry("dionysius", {"ja_reading_katakana": "ディオニュシオス",
                                                        "ja_reading_confidence": "high", "confidence": "high"},
                                        source_context="")
        ledger.upsert_ja_reading_entry("dionysius", {"ja_reading_katakana": "ディオニス",
                                                        "ja_reading_confidence": "high", "confidence": "high"},
                                        source_context="family_z_melos")
        default_entry = ledger.get_ja_reading_entry("dionysius")
        melos_entry = ledger.get_ja_reading_entry("dionysius", source_context="family_z_melos")
        assert default_entry["ja_reading_katakana"] == "ディオニュシオス"
        assert melos_entry["ja_reading_katakana"] == "ディオニス"
    _use_temp_ledger(run)
    print("PASS: test_ja_reading_entry_source_context_no_collision")


def test_ledger_health_check_detects_confidence_mirror_mismatch():
    def run():
        ledger.upsert_ja_reading_entry("figma", {"ja_reading_katakana": "フィグマ",
                                                    "ja_reading_confidence": "high", "confidence": "low"})
        report = ledger.ledger_health_check()
        surfaces = {e["surface"] for e in report["confidence_mirror_mismatch"]}
        assert "figma" in surfaces
    _use_temp_ledger(run)
    print("PASS: test_ledger_health_check_detects_confidence_mirror_mismatch")


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
    test_get_hint_for_text_word_boundary_no_substring_false_match()
    test_get_hint_for_text_excludes_cascade_unresolved_entity_type()
    test_set_tts_injection_disabled_isolates_entry_without_deleting()
    test_ja_reading_entry_source_context_no_collision()
    test_ledger_health_check_detects_confidence_mirror_mismatch()
    test_upsert_research_result_matches_by_surface()
    print("ALL TESTS PASSED")
