# ============================================================
# er006_pronunciation_tts_injection_01_test.py
# ============================================================
# 実行方法: .venv/Scripts/python.exe er006_pronunciation_tts_injection_01_test.py
from __future__ import annotations

import os
import shutil

import er006_pronunciation_ledger_01 as ledger
import er006_pronunciation_tts_injection_01 as inject


def _use_temp_ledger(test_fn):
    orig_path = ledger.LEDGER_PATH
    tmp_path = "er006_output/_test_pronunciation_injection_tmp/ledger.json"
    if os.path.exists(os.path.dirname(tmp_path)):
        shutil.rmtree(os.path.dirname(tmp_path))
    ledger.LEDGER_PATH = tmp_path
    try:
        test_fn()
    finally:
        ledger.LEDGER_PATH = orig_path
        if os.path.exists(os.path.dirname(tmp_path)):
            shutil.rmtree(os.path.dirname(tmp_path))


def test_no_hint_when_no_entity_present():
    def run():
        key = ledger.LedgerKey(surface="Ottoni", entity_type="person")
        ledger.upsert(key, {"pronunciation_hint": "oh-TOH-nee", "confidence": "high"})
        style_prefix = "Speak naturally."
        text = "This sentence has no proper nouns of interest."
        augmented, hits = inject.augment_style_prefix_with_pronunciation(style_prefix, text)
        assert augmented == style_prefix, "無関係なtextではstyle_prefixを変更してはならない"
        assert hits == []
    _use_temp_ledger(run)
    print("PASS: test_no_hint_when_no_entity_present")


def test_hint_added_when_entity_present():
    def run():
        key = ledger.LedgerKey(surface="Ottoni", entity_type="person")
        ledger.upsert(key, {"pronunciation_hint": "oh-TOH-nee", "confidence": "high"})
        style_prefix = "Speak naturally."
        text = "Ottoni and colleagues published a study in 2016."
        augmented, hits = inject.augment_style_prefix_with_pronunciation(style_prefix, text)
        assert "oh-TOH-nee" in augmented
        assert style_prefix in augmented
        assert len(hits) == 1
    _use_temp_ledger(run)
    print("PASS: test_hint_added_when_entity_present")


def test_spoken_text_never_modified():
    # この関数はstyle_prefixだけを返す設計であり、textを一切返さない
    # (呼び出し側がtext自体を書き換える余地がない、という設計の裏付け)。
    def run():
        key = ledger.LedgerKey(surface="Ottoni", entity_type="person")
        ledger.upsert(key, {"pronunciation_hint": "oh-TOH-nee", "confidence": "high"})
        text = "Ottoni and colleagues published a study in 2016."
        original_text = text
        inject.augment_style_prefix_with_pronunciation("Speak naturally.", text)
        assert text == original_text, "text引数自体が変更されてはならない"
    _use_temp_ledger(run)
    print("PASS: test_spoken_text_never_modified")


def test_low_confidence_excluded_by_default():
    def run():
        key = ledger.LedgerKey(surface="Foo", entity_type="person")
        ledger.upsert(key, {"pronunciation_hint": "foo-hint", "confidence": "low"})
        text = "Foo appears in this sentence."
        augmented, hits = inject.augment_style_prefix_with_pronunciation("Speak naturally.", text)
        assert hits == [], "既定のmin_confidence=mediumでlow confidenceは注入しないはず"
    _use_temp_ledger(run)
    print("PASS: test_low_confidence_excluded_by_default")


def test_multiple_entities_all_included():
    def run():
        ledger.upsert(ledger.LedgerKey(surface="Malmö", entity_type="place"),
                       {"pronunciation_hint": "MAL-moh", "confidence": "high"})
        ledger.upsert(ledger.LedgerKey(surface="Triangeln", entity_type="place"),
                       {"pronunciation_hint": "tree-AHNG-eln", "confidence": "medium"})
        text = "At Malmö's Triangeln station, a bench was tilted."
        augmented, hits = inject.augment_style_prefix_with_pronunciation("Speak naturally.", text)
        assert "MAL-moh" in augmented
        assert "tree-AHNG-eln" in augmented
        assert len(hits) == 2
    _use_temp_ledger(run)
    print("PASS: test_multiple_entities_all_included")


if __name__ == "__main__":
    test_no_hint_when_no_entity_present()
    test_hint_added_when_entity_present()
    test_spoken_text_never_modified()
    test_low_confidence_excluded_by_default()
    test_multiple_entities_all_included()
    print("ALL TESTS PASSED")
