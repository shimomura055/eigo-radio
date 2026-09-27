# ============================================================
# er006_pronunciation_ledger_01.py
# ER-006-PRONUNCIATION-LEDGER-SECONDARY-ASR-01: Pronunciation Ledger
# ============================================================
# Perplexity発音調査の結果を、Topic横断で再利用可能な形で保存する。
# entity collisionを避けるため、spelling・entity_type・source contextで
# 識別する(単純にsurfaceの文字列だけをキーにしない: 同じ綴りでも
# 人名/地名で読みが異なりうるため)。

from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass
from typing import Optional

LEDGER_PATH = "er006_output/pronunciation_ledger_01/ledger.json"


@dataclass
class LedgerKey:
    surface: str
    entity_type: str
    source_context: str = ""  # 曖昧な場合のみ明示指定(例: 同じ綴りが複数文脈で別の読みを持つ場合)

    def ledger_id(self) -> str:
        payload = json.dumps(
            {"surface": self.surface.strip().lower(), "entity_type": self.entity_type,
             "source_context": self.source_context.strip().lower()},
            sort_keys=True)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def _load() -> dict:
    if not os.path.exists(LEDGER_PATH):
        return {}
    with open(LEDGER_PATH, encoding="utf-8") as f:
        return json.load(f)


def _save(ledger: dict) -> None:
    os.makedirs(os.path.dirname(LEDGER_PATH), exist_ok=True)
    with open(LEDGER_PATH, "w", encoding="utf-8") as f:
        json.dump(ledger, f, ensure_ascii=False, indent=2)


def lookup(key: LedgerKey) -> Optional[dict]:
    """既存Ledgerにこのentityの発音情報があれば返す(cache hit)。
    無ければNone(cache miss、新規research要)。"""
    ledger = _load()
    return ledger.get(key.ledger_id())


def upsert(key: LedgerKey, entry: dict) -> str:
    """research結果をLedgerへ登録/更新する。戻り値はledger_id。

    PRONUNCIATION-RESOLUTION-ALL-ACTIVE-FAMILIES-PRODUCTION-01(Phase 2、
    recon 3.4節): JA/EN両対応のため新規フィールドを追加する(いずれも
    既定値で後方互換、既存フィールドは無変更)。既存呼び出し元
    (upsert_research_result等、entryにこれらキーを含まない)には一切
    影響しない。"""
    ledger = _load()
    ledger_id = key.ledger_id()
    ledger[ledger_id] = {
        "surface": key.surface, "entity_type": key.entity_type, "source_context": key.source_context,
        "canonical_spelling": entry.get("canonical_spelling", key.surface),
        "language_origin": entry.get("language_origin", ""),
        "expected_pronunciation_ipa": entry.get("expected_pronunciation_ipa", ""),
        "pronunciation_hint": entry.get("pronunciation_hint", ""),
        "alternate_pronunciations": entry.get("alternate_pronunciations", []),
        "confidence": entry.get("confidence", "low"),
        "ambiguity_note": entry.get("ambiguity_note", ""),
        "sources": entry.get("sources", []),
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        # 以下、Phase 2新規フィールド(既定値で後方互換)
        "ja_reading_katakana": entry.get("ja_reading_katakana", ""),
        "ja_reading_confidence": entry.get("ja_reading_confidence", ""),
        "ja_reading_sources": entry.get("ja_reading_sources", []),
        "resolution_method": entry.get("resolution_method", ""),
        "resolved_at_stage": entry.get("resolved_at_stage", ""),
    }
    _save(ledger)
    return ledger_id


def upsert_research_result(entities: list[dict], research_items: list[dict], sources: list[str]) -> list[str]:
    """extract_proper_nouns()のitems(surface/entity_type)と、
    research_pronunciations()のitems(surface一致で対応)を突き合わせて
    Ledgerへ一括登録する。"""
    by_surface = {it["surface"]: it for it in research_items}
    ids = []
    for e in entities:
        research_item = by_surface.get(e["surface"])
        if research_item is None:
            continue
        key = LedgerKey(surface=e["surface"], entity_type=e["entity_type"])
        research_item = dict(research_item)
        research_item["sources"] = sources
        ids.append(upsert(key, research_item))
    return ids


def get_hint_for_text(text: str, min_confidence: str = "medium") -> list[dict]:
    """textの中にLedger登録済みのsurfaceが含まれていれば、そのentryを
    返す(confidence順、min_confidence未満は除外)。TTSへ渡すpronunciation
    hintの選定に使う。

    PRONUNCIATION-RESOLUTION-ALL-ACTIVE-FAMILIES-PRODUCTION-01(Phase 2):
    大文字小文字を区別しない比較へ変更する(既存はcase-sensitive、
    reactive lookup由来のentry[entity_type="cascade_unresolved_entity"]は
    surfaceが小文字で保存されるため[例: "toteme"]、本文中の実際の表記
    [例: "Toteme"]とcase-sensitiveでは一致せず、pre_tts配線後も発火しない
    実例をruntime evidenceで確認した)。大文字小文字を区別しないことで
    一致範囲は既存のcase-sensitive一致を包含する形でのみ広がる(既存の
    一致が消えることはない、fail-safe方向の変更)。"""
    conf_rank = {"high": 3, "medium": 2, "low": 1}
    min_rank = conf_rank[min_confidence]
    ledger = _load()
    text_lower = (text or "").lower()
    hits = []
    for entry in ledger.values():
        if entry["surface"].lower() in text_lower and conf_rank.get(entry["confidence"], 0) >= min_rank:
            if entry.get("pronunciation_hint"):
                hits.append(entry)
    return hits


def get_low_confidence_entries_for_text(text: str) -> list[dict]:
    """PRONUNCIATION-RESOLUTION-ALL-ACTIVE-FAMILIES-PRODUCTION-01(Phase 2):
    confidenceに関わらず、textの中にLedger登録済みのsurfaceが含まれる
    entryを全て返す(get_hint_for_textのmin_confidenceフィルタを通さない
    版)。低confidence entryへの再research要否判定に使う(呼び出し側で
    confidence=="low"のものだけを対象に絞る)。"""
    ledger = _load()
    text_lower = (text or "").lower()
    return [entry for entry in ledger.values() if entry["surface"] and entry["surface"].lower() in text_lower]


def get_ja_reading_entry(surface: str) -> Optional[dict]:
    """PRONUNCIATION-RESOLUTION-ALL-ACTIVE-FAMILIES-PRODUCTION-01(Phase 2):
    JA読み解決コア専用の単純lookup(entity_type="ja_reading_katakana"固定、
    source_contextなし)。surface小文字一致。"""
    key = LedgerKey(surface=surface, entity_type="ja_reading_katakana")
    return lookup(key)


def upsert_ja_reading_entry(surface: str, entry: dict) -> str:
    """PRONUNCIATION-RESOLUTION-ALL-ACTIVE-FAMILIES-PRODUCTION-01(Phase 2):
    JA読み解決コア専用の単純upsert(get_ja_reading_entryと対の書き込み)。"""
    key = LedgerKey(surface=surface, entity_type="ja_reading_katakana")
    return upsert(key, entry)
