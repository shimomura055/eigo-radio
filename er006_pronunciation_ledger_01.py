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
import re
import time
from dataclasses import dataclass
from typing import Optional

LEDGER_PATH = "er006_output/pronunciation_ledger_01/ledger.json"

# PRONUNCIATION-RESOLUTION-ALL-ACTIVE-FAMILIES-PRODUCTION-01(Sonnet修正1回目、
# Opus L2 BLOCKER-1是正): Stage 2(ASR Cascade Human Review packaging)専用の
# entity_type。この種のentryは「解決できなかった固有名詞をHuman Review
# パッケージに補足情報として載せる」ためだけに作られ(er006_secondary_asr_01.
# _resolve_unresolved_entity_for_review参照)、TTS発音ヒント注入の裏付けとして
# 設計されたものではない。Phase 2でget_hint_for_text()がTTS注入経路へ初めて
# 接続された際、この設計意図に反してTTS注入対象に混入した(実データで
# surface="plus"/"mini"/"main story"/"one voice"/"ganis"の誤entryが本番Ledger
# へ実際に混入し、"surplus"/"minister"等を含む無関係な英文で誤発音指示が
# 付与される実害を確認)。
CASCADE_UNRESOLVED_ENTITY_TYPE = "cascade_unresolved_entity"

# surfaceが英数字・空白・一部記号のみで構成される場合(Latin表記)は語境界
# 付き一致を使う。非Latin(漢字・キリル文字・アクセント付きラテン文字等)を
# 含む場合は、語境界の概念が単純な正規表現では安全に定義できないため、
# 既存どおりの部分一致(substring match)にfall backする(fail-safe: 既存の
# 一致範囲を狭める方向にのみ変更し、非Latin側の挙動は変えない)。
_ASCII_SURFACE_RE = re.compile(r"^[A-Za-z0-9 '\-.,&]+$")


def _surface_matches_text(surface: str, text_lower: str) -> bool:
    """PRONUNCIATION-RESOLUTION-ALL-ACTIVE-FAMILIES-PRODUCTION-01(Sonnet修正
    1回目、Opus L2 BLOCKER-1是正(i)): 語境界なしの`surface in text`部分一致
    (旧実装)は、"plus"が"surplus"に、"mini"が"minister"に、"ganis"が
    "organisation"に、それぞれ誤って一致してしまう(実データで確認済みの
    実害)。surfaceが完全にASCII(英数字+一部記号)の場合のみ、前後が
    英数字でない位置での一致(語境界相当)を要求する。"""
    s = (surface or "").strip().lower()
    if not s:
        return False
    if _ASCII_SURFACE_RE.match(s):
        pattern = r"(?<![A-Za-z0-9])" + re.escape(s) + r"(?![A-Za-z0-9])"
        return re.search(pattern, text_lower) is not None
    return s in text_lower


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
    existing = ledger.get(ledger_id, {})
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
        # Sonnet修正1回目(Opus L2 BLOCKER-1是正(iii)): 誤entryの隔離フラグ。
        # entryが明示的に指定しない限り、既存storeの値をそのまま引き継ぐ
        # (set_tts_injection_disabled()で立てたフラグが、無関係な後続の
        # upsert[例: 低confidence再research]で黙って消えないようにする)。
        "tts_injection_disabled": entry.get("tts_injection_disabled", existing.get("tts_injection_disabled", False)),
        "tts_injection_disabled_reason": entry.get(
            "tts_injection_disabled_reason", existing.get("tts_injection_disabled_reason", "")),
    }
    _save(ledger)
    return ledger_id


def set_tts_injection_disabled(ledger_id: str, reason: str) -> None:
    """PRONUNCIATION-RESOLUTION-ALL-ACTIVE-FAMILIES-PRODUCTION-01(Sonnet修正
    1回目、Opus L2 BLOCKER-1是正(iii)): 本番Ledgerの特定entryを削除せず
    隔離する(entity_typeはそのまま維持、ASR Phrase List用途は維持し、
    TTS注入対象からのみ除外する)。upsert()を経由せず該当entryの2
    フィールドだけを直接更新することで、entry内の既存フィールド(sources
    等)を一切変更しない。"""
    ledger = _load()
    if ledger_id not in ledger:
        raise KeyError(f"ledger_id not found in ledger: {ledger_id}")
    ledger[ledger_id]["tts_injection_disabled"] = True
    ledger[ledger_id]["tts_injection_disabled_reason"] = reason
    _save(ledger)


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


def get_hint_for_text(text: str, min_confidence: str = "medium",
                       exclude_entity_types: Optional[set] = None,
                       apply_tts_injection_filter: bool = False) -> list[dict]:
    """textの中にLedger登録済みのsurfaceが含まれていれば、そのentryを
    返す(confidence順、min_confidence未満は除外)。TTSへ渡すpronunciation
    hintの選定と、ASR Secondary Cascade用Phrase Listの選定の両方で使われる
    共有関数(呼び出し元ごとに用途が異なるため、以下の2引数は既定値では
    従来どおり無効=ASR Phrase List用途を維持する)。

    PRONUNCIATION-RESOLUTION-ALL-ACTIVE-FAMILIES-PRODUCTION-01(Phase 2):
    大文字小文字を区別しない比較へ変更する(既存はcase-sensitive、
    reactive lookup由来のentry[entity_type="cascade_unresolved_entity"]は
    surfaceが小文字で保存されるため[例: "toteme"]、本文中の実際の表記
    [例: "Toteme"]とcase-sensitiveでは一致せず、pre_tts配線後も発火しない
    実例をruntime evidenceで確認した)。大文字小文字を区別しないことで
    一致範囲は既存のcase-sensitive一致を包含する形でのみ広がる(既存の
    一致が消えることはない、fail-safe方向の変更)。

    Sonnet修正1回目(Opus L2 BLOCKER-1是正)追加引数:
      exclude_entity_types: このentity_typeのentryは対象から除外する
        (TTS注入呼び出し元は`{CASCADE_UNRESOLVED_ENTITY_TYPE}`を渡す。
        ASR Phrase List呼び出し元[er003_v1_repro01_main_generate.py]は
        既定Noneのまま=従来どおり除外しない、既存のASR Phrase List用途を
        維持する)。
      apply_tts_injection_filter: Trueの場合、`tts_injection_disabled`が
        真のentryも対象から除外する(本番Ledger内の既知の誤entry隔離用、
        4節参照)。ASR Phrase List用途では既定Falseのまま除外しない
        (誤entryでも代替spellingとしてASR認識には有用なため)。"""
    conf_rank = {"high": 3, "medium": 2, "low": 1}
    min_rank = conf_rank[min_confidence]
    exclude_entity_types = exclude_entity_types or set()
    ledger = _load()
    text_lower = (text or "").lower()
    hits = []
    for entry in ledger.values():
        if entry.get("entity_type") in exclude_entity_types:
            continue
        if apply_tts_injection_filter and entry.get("tts_injection_disabled"):
            continue
        if _surface_matches_text(entry["surface"], text_lower) and conf_rank.get(entry["confidence"], 0) >= min_rank:
            if entry.get("pronunciation_hint"):
                hits.append(entry)
    return hits


def get_low_confidence_entries_for_text(text: str, exclude_entity_types: Optional[set] = None) -> list[dict]:
    """PRONUNCIATION-RESOLUTION-ALL-ACTIVE-FAMILIES-PRODUCTION-01(Phase 2):
    confidenceに関わらず、textの中にLedger登録済みのsurfaceが含まれる
    entryを全て返す(get_hint_for_textのmin_confidenceフィルタを通さない
    版)。低confidence entryへの再research要否判定に使う(呼び出し側で
    confidence=="low"のものだけを対象に絞る)。

    Sonnet修正1回目(Opus L2 BLOCKER-1是正): 語境界付き一致へ変更
    (`_surface_matches_text`、"ganis"が"organisation"に部分一致し無関係な
    記事で毎回Perplexity再researchが発火していた実害への対応)。
    exclude_entity_types(既定None)を渡すと、そのentity_typeのentryは
    再research対象から除外できる(呼び出し側`resolve_and_augment_en_style_
    prefix`が`{CASCADE_UNRESOLVED_ENTITY_TYPE}`を渡す)。"""
    exclude_entity_types = exclude_entity_types or set()
    ledger = _load()
    text_lower = (text or "").lower()
    return [entry for entry in ledger.values()
            if entry.get("entity_type") not in exclude_entity_types
            and entry["surface"] and _surface_matches_text(entry["surface"], text_lower)]


JA_READING_ENTITY_TYPE = "ja_reading_katakana"


def get_ja_reading_entry(surface: str, source_context: str = "") -> Optional[dict]:
    """PRONUNCIATION-RESOLUTION-ALL-ACTIVE-FAMILIES-PRODUCTION-01(Phase 2、
    Sonnet修正1回目でsource_context引数を追加、Opus L2 BLOCKER-2是正):
    JA読み解決コア専用の単純lookup(entity_type="ja_reading_katakana"固定)。
    surface小文字一致。source_context既定""は既存呼び出し元と完全後方互換
    (同じ綴りは全記事で1読みのみ、という旧挙動のまま)。作品固有の読み
    (例: 太宰治『走れメロス』の"ディオニス")のように、同じ綴りが文脈により
    異なる読みを持つ場合のみ、呼び出し側が非空のsource_contextを渡す。"""
    key = LedgerKey(surface=surface, entity_type=JA_READING_ENTITY_TYPE, source_context=source_context)
    return lookup(key)


def upsert_ja_reading_entry(surface: str, entry: dict, source_context: str = "") -> str:
    """PRONUNCIATION-RESOLUTION-ALL-ACTIVE-FAMILIES-PRODUCTION-01(Phase 2、
    Sonnet修正1回目でsource_context引数を追加): JA読み解決コア専用の単純
    upsert(get_ja_reading_entryと対の書き込み)。"""
    key = LedgerKey(surface=surface, entity_type=JA_READING_ENTITY_TYPE, source_context=source_context)
    return upsert(key, entry)


def ledger_health_check() -> dict:
    """PRONUNCIATION-RESOLUTION-ALL-ACTIVE-FAMILIES-PRODUCTION-01(Sonnet修正
    1回目、Opus L2所見「QCD」フォローアップ): 本番Ledgerの健全性を読み取り
    専用でチェックし、報告用の所見リストを返す(何も書き換えない)。
    - `cascade_unresolved_entity`型で、canonical_spellingがsurfaceと
      文字列として無関係(互いに部分文字列関係にない)なentry
      (BLOCKER-1のような取り違え混入の兆候)。
    - `ja_reading_katakana`型で、`confidence`と`ja_reading_confidence`が
      不一致なentry(Figma鏡写し不整合と同種の問題)。
    - `pronunciation_hint`が空のまま(TTS注入に使えない)entry。
    - `tts_injection_disabled`が真のentry(隔離済み一覧、参考情報)。"""
    ledger = _load()
    canonical_mismatch, confidence_mismatch, empty_hint, disabled = [], [], [], []
    for ledger_id, entry in ledger.items():
        surface = (entry.get("surface") or "").strip().lower()
        canonical = (entry.get("canonical_spelling") or "").strip().lower()
        if entry.get("entity_type") == CASCADE_UNRESOLVED_ENTITY_TYPE and surface and canonical:
            if surface not in canonical and canonical not in surface:
                canonical_mismatch.append({"ledger_id": ledger_id, "surface": entry.get("surface"),
                                            "canonical_spelling": entry.get("canonical_spelling")})
        if entry.get("entity_type") == JA_READING_ENTITY_TYPE:
            ja_conf = entry.get("ja_reading_confidence")
            top_conf = entry.get("confidence")
            if ja_conf and top_conf and ja_conf != top_conf:
                confidence_mismatch.append({"ledger_id": ledger_id, "surface": entry.get("surface"),
                                             "confidence": top_conf, "ja_reading_confidence": ja_conf})
        if not entry.get("pronunciation_hint") and entry.get("entity_type") != JA_READING_ENTITY_TYPE:
            empty_hint.append({"ledger_id": ledger_id, "surface": entry.get("surface"),
                                "entity_type": entry.get("entity_type")})
        if entry.get("tts_injection_disabled"):
            disabled.append({"ledger_id": ledger_id, "surface": entry.get("surface"),
                              "reason": entry.get("tts_injection_disabled_reason")})
    return {
        "total_entries": len(ledger),
        "canonical_spelling_mismatch": canonical_mismatch,
        "confidence_mirror_mismatch": confidence_mismatch,
        "empty_pronunciation_hint": empty_hint,
        "tts_injection_disabled": disabled,
    }
