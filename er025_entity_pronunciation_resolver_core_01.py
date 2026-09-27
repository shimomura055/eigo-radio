# ============================================================
# er025_entity_pronunciation_resolver_core_01.py
# PRONUNCIATION-RESOLUTION-ALL-ACTIVE-FAMILIES-PRODUCTION-01 (Phase 2)
# ============================================================
# 固有名詞/外来語の読み解決を、日本語TTS(Latin表記の日本語読み)・
# 英語TTS(固有名詞の英語発音)の両方について共通のパイプラインで扱う
# coreモジュール(docs/pm/recon_pronunciation_resolution_01.md 3.1節)。
#
# 依存方向(Gate 4 Dangling Reference Check観点、逆依存を作らない):
#   このモジュール -> er003_audio_tts_asr_safety(読み取りのみ)
#                  -> er006_pronunciation_ledger_01(store、読み書き)
#                  -> er006_pronunciation_research_01(EN web lookup)
#                  -> er006_pronunciation_tts_injection_01(EN style_prefix注入)
#                  -> er002_ja_web_research_r3(JA web lookup、遅延import)
# 既存2機構(Foreign Token Gate辞書 / Pronunciation Ledger)は本モジュール
# を一切importしない(既存Production・既存17件+αのtestへの影響ゼロ)。
#
# Detect -> known dictionary/cache -> web lookup(必要時のみ) ->
# confidence判定 -> 高confidence自動使用 -> store保存 -> (ASR裏付け) ->
# それでも不能ならHUMAN_REVIEW、という共通フローをJA/ENそれぞれで実装する
# (ユーザー決定の要約、recon 0節)。
#
# fail-safe方針: web lookup失敗・API未設定・応答解析失敗はいずれも
# 「解決できなかった」として扱い、既存の安全側動作(JAはHUMAN_REVIEW、
# ENは発音ヒント注入なしの通常TTS+既存ASR Cascade)を一切変更しない。

from __future__ import annotations

import re
import time
from typing import Optional

import er003_audio_tts_asr_safety as safety
import er006_pronunciation_ledger_01 as ledger
import er006_pronunciation_research_01 as en_research
import er006_pronunciation_tts_injection_01 as en_injection

# ------------------------------------------------------------
# confidence判定(recon 3.4節のFable設計判断§3準拠)
# ------------------------------------------------------------
CONFIDENCE_TO_GATE = {"high": "AUTO_USE", "medium": "ASR_BACKED", "low": "HUMAN_REVIEW"}


def confidence_gate(confidence: Optional[str]) -> str:
    return CONFIDENCE_TO_GATE.get((confidence or "").strip().lower(), "HUMAN_REVIEW")


# ------------------------------------------------------------
# run内(同一プロセス内)の重複解決回避用in-memory cache。
# 記事をまたいでプロセスが再起動されればLedger(永続store)がcacheとして
# 機能するため、ここはあくまで「同一記事内でのAPI呼び出し削減」用。
# ------------------------------------------------------------
_JA_RUN_CACHE: dict[str, dict] = {}
_EN_LOW_CONFIDENCE_RETRY_DONE: set[str] = set()


def reset_run_caches() -> None:
    """test/新しい記事runの開始時にin-memory cacheをクリアする(既定では
    呼ばれない。プロセスが記事ごとに再起動される現行運用では通常不要だが、
    同一プロセス内で複数記事を扱うテスト・将来のバッチ実行向けに用意する)。"""
    _JA_RUN_CACHE.clear()
    _EN_LOW_CONFIDENCE_RETRY_DONE.clear()


# ============================================================
# JA側: 未知のLatin外来語トークンのreading_dictionaryへの動的追加
# ============================================================
JA_READING_LINE_RE = re.compile(
    r"READING:\s*(?P<surface>.+?)\s*=\s*(?P<reading>.+?)\s*\|\s*CONFIDENCE:\s*(?P<confidence>high|medium|low)"
    r"\s*\|\s*SOURCE:\s*(?P<source>.+?)\s*$", re.MULTILINE)

JA_READING_RESEARCH_PROMPT_TEMPLATE = """あなたは日本語メディアでの固有名詞の読み方(カタカナ表記)調査担当です。
以下の固有名詞それぞれについて、日本のニュース・メディアで実際に使われている
一般的なカタカナ読みを、Web検索で確認してください。

信頼できる情報源の優先順位:
(a) 当該固有名詞の公式サイト日本語版・日本法人のプレスリリース
(b) 日本語版Wikipedia
(c) 主要日本語報道(共同通信・時事通信・NHK等)
(d) 上記が見つからない場合のみ、英語の発音からの機械的なカタカナ近似

対象一覧:
{entity_list}

文脈(記事からの抜粋、参考情報):
{context}

出力形式(厳守、他の説明文は書かない): 対象1件につき1行、以下の形式のみで
出力してください。

READING: <固有名詞> = <カタカナ読み> | CONFIDENCE: <high|medium|low> | SOURCE: <確認したURLまたは根拠>

CONFIDENCEの判定基準:
- high: 公式サイト日本語版・日本法人プレスリリースに読みの記載がある、
  または独立した信頼ソース2件以上(日本語版Wikipedia・主要報道)で表記が一致する
- medium: 信頼できるソースが1件のみ見つかった
- low: ソース間で表記が割れている、または(d)の機械的近似のみ
"""


def build_ja_reading_research_prompt(surfaces: list[str], context: str = "") -> str:
    entity_list = "\n".join(f"- {s}" for s in surfaces)
    return JA_READING_RESEARCH_PROMPT_TEMPLATE.format(entity_list=entity_list, context=(context or "")[:400])


def parse_ja_reading_research_output(raw_text: str) -> list[dict]:
    results = []
    for m in JA_READING_LINE_RE.finditer(raw_text or ""):
        results.append({
            "surface": m.group("surface").strip(),
            "reading": m.group("reading").strip(),
            "confidence": m.group("confidence").strip().lower(),
            "source": m.group("source").strip(),
        })
    return results


def research_ja_readings(surfaces: list[str], context: str = "", client=None) -> dict:
    """既存er002_ja_web_research_r3.make_writer_research_fn(OpenAI
    web_search、OPEN-146と同一関数)を無改変で再利用し、1回のAPI実行内で
    surfaces全件のJA読みをWeb検索で確認する(1記事につき未知語をまとめて
    1回、recon 3.7節)。surfacesが空の場合はAPI呼び出し自体を行わない
    (OPEN-146 run_canonical_spelling_research()と同型の非発火設計)。"""
    if not surfaces:
        return {"raw_text": None, "model": None, "response_id": None,
                "search_usage": None, "sources": [], "parsed": [], "skipped": True}
    try:
        import er002_ja_web_research_r3 as r3
    except Exception as exc:
        return {"raw_text": None, "model": None, "response_id": None,
                "search_usage": None, "sources": [], "parsed": [], "skipped": True,
                "error": f"{type(exc).__name__}: {exc}"}
    try:
        user_message = build_ja_reading_research_prompt(surfaces, context)
        research_fn = r3.make_writer_research_fn(user_message, client=client, reasoning_effort="medium")
        text, model, response_id, search_usage, sources = research_fn()
        parsed = parse_ja_reading_research_output(text)
        return {"raw_text": text, "model": model, "response_id": response_id,
                "search_usage": search_usage, "sources": sources, "parsed": parsed, "skipped": False}
    except Exception as exc:
        # fail-safe: web lookup失敗は「解決できなかった」として扱う
        # (既存Reading ResolverのFail-safe設計を踏襲、TTSは止めない設計
        # のため呼び出し側でHUMAN_REVIEWへ自然にfall backする)。
        return {"raw_text": None, "model": None, "response_id": None,
                "search_usage": None, "sources": [], "parsed": [], "skipped": False,
                "error": f"{type(exc).__name__}: {exc}"}


def resolve_unknown_ja_tokens(text: str, known_key_phrase_terms=None,
                               extra_dictionary: Optional[dict] = None,
                               context: str = "", client=None) -> dict:
    """日本語canonical text中の未知Latin外来語トークンを検出し、
    cache -> Ledger -> web lookup -> confidence判定 -> 高/中confidenceの
    読みをreading_dictionaryへ動的追加する(recon 3.2節)。

    戻り値:
      reading_dictionary: 呼び出し側がsafety.classify_foreign_tokens_in_
        japanese_text()へそのまま渡せる、既存extra_dictionaryに新規解決分
        をマージした辞書(既存キーは上書きしない)。
      resolved: 今回自動使用(AUTO_USE/ASR_BACKED)した項目のリスト。
      unresolved_human_review: 解決できずHUMAN_REVIEW対象のまま残る
        surfaceのリスト(fail-safe、既存Gateの安全側動作は変更しない)。
      web_lookup_called: 今回web lookup(有料API)を実際に呼んだか。
      research_meta: research_ja_readings()の戻り値そのもの(呼んだ場合のみ)。
    """
    base_dictionary = dict(extra_dictionary or {})
    # まず既存Gateのdetectロジックをそのまま再利用し、現時点でHUMAN_REVIEW
    # 相当と判定される未知トークンだけを洗い出す(Gate自体は無改変)。
    findings = safety.classify_foreign_tokens_in_japanese_text(
        text, known_key_phrase_terms=known_key_phrase_terms, reading_dictionary=base_dictionary)
    unknown_tokens = sorted({
        f["token"] for f in findings if f.get("category") == safety.FOREIGN_TOKEN_HUMAN_REVIEW
    }, key=str.lower)

    resolved = []
    still_unresolved = []
    web_lookup_called = False
    research_meta = None

    need_lookup = []
    for token in unknown_tokens:
        key = token.lower()
        cached = _JA_RUN_CACHE.get(key)
        if cached is None:
            stored = ledger.get_ja_reading_entry(key)
            if stored and stored.get("ja_reading_katakana"):
                cached = stored
                _JA_RUN_CACHE[key] = cached
        if cached is not None:
            gate = confidence_gate(cached.get("ja_reading_confidence") or cached.get("confidence"))
            if gate in ("AUTO_USE", "ASR_BACKED"):
                base_dictionary.setdefault(key, cached["ja_reading_katakana"])
                resolved.append({"surface": token, "reading": cached["ja_reading_katakana"],
                                  "confidence": cached.get("ja_reading_confidence") or cached.get("confidence"),
                                  "source": "cache_or_ledger"})
            else:
                still_unresolved.append(token)
        else:
            need_lookup.append(token)

    if need_lookup:
        research_meta = research_ja_readings(need_lookup, context=context, client=client)
        web_lookup_called = not research_meta.get("skipped", True)
        parsed_by_surface = {p["surface"].lower(): p for p in research_meta.get("parsed", [])}
        for token in need_lookup:
            key = token.lower()
            parsed = parsed_by_surface.get(key)
            if parsed is None:
                still_unresolved.append(token)
                continue
            gate = confidence_gate(parsed["confidence"])
            entry = {
                "ja_reading_katakana": parsed["reading"], "ja_reading_confidence": parsed["confidence"],
                "ja_reading_sources": [parsed["source"]], "resolution_method": "web_search",
                "resolved_at_stage": "pre_tts",
                # 旧(EN専用)confidenceフィールドにも同じ値を鏡写しし、
                # EN側get_low_confidence_entries_for_text()がJA読みentryを
                # 誤ってEN低confidence候補として拾わないようにする
                # (entity_type="ja_reading_katakana"での除外と二重の安全策)。
                "confidence": parsed["confidence"],
            }
            ledger.upsert_ja_reading_entry(key, entry)
            _JA_RUN_CACHE[key] = entry
            if gate in ("AUTO_USE", "ASR_BACKED"):
                base_dictionary.setdefault(key, parsed["reading"])
                resolved.append({"surface": token, "reading": parsed["reading"],
                                  "confidence": parsed["confidence"], "source": parsed["source"]})
            else:
                still_unresolved.append(token)

    return {
        "reading_dictionary": base_dictionary, "resolved": resolved,
        "unresolved_human_review": still_unresolved, "web_lookup_called": web_lookup_called,
        "research_meta": research_meta,
    }


# ============================================================
# EN側: TTS生成前の発音ヒントstyle_prefix注入(recon 3.3節)
# ============================================================
def resolve_and_augment_en_style_prefix(style_prefix: str, text: str, context: str = "",
                                         client=None) -> tuple:
    """既存Pronunciation Ledger(cache)登録済みの固有名詞があれば
    style_prefixへ発音ヒントを注入する(既存augment_style_prefix_with_
    pronunciation()、初めてTTS生成前の経路へ実配線)。

    加えて、Ledgerにconfidence="low"で登録済み(reactive lookupや過去の
    web lookupで確信度が上がらなかった)の固有名詞がtext中にある場合、
    プロセス内で未再試行のものに限り1回だけ追加research_pronunciations()
    を試み、confidenceが改善すればLedgerを更新しヒントを注入する
    (recon 3.8節のEN既存low-confidence実例向け、in-processで重複再研究
    しないようdedupする)。

    戻り値: (augmented_style_prefix, info)。infoはtelemetry用の辞書。"""
    augmented, hits = en_injection.augment_style_prefix_with_pronunciation(
        style_prefix, text, min_confidence="medium")
    info = {
        "hints_applied": bool(hits), "cache_hits": hits, "low_confidence_retry_attempted": False,
        "low_confidence_retry_improved": False, "research_meta": None,
    }
    if hits:
        return augmented, info

    low_conf_candidates = [
        e for e in ledger.get_low_confidence_entries_for_text(text)
        if (e.get("confidence") == "low") and (e.get("entity_type") != "ja_reading_katakana")
        and (e["surface"].lower() not in _EN_LOW_CONFIDENCE_RETRY_DONE)
    ]
    if not low_conf_candidates:
        return augmented, info

    info["low_confidence_retry_attempted"] = True
    entities = [{"surface": e["surface"], "entity_type": e.get("entity_type", "unknown"),
                 "risk_reason": "既存Ledgerでconfidence=lowのため、pre_tts配線時に再research"}
                for e in low_conf_candidates]
    for e in low_conf_candidates:
        _EN_LOW_CONFIDENCE_RETRY_DONE.add(e["surface"].lower())
    research_result = en_research.research_pronunciations(entities)
    info["research_meta"] = research_result
    if research_result.get("status") != "OK":
        return augmented, info

    from er006_pronunciation_ledger_01 import LedgerKey
    improved = False
    for item in research_result.get("items", []):
        matching = next((e for e in low_conf_candidates if e["surface"] == item.get("surface")), None)
        if matching is None:
            continue
        key = LedgerKey(surface=matching["surface"], entity_type=matching.get("entity_type", "unknown"))
        item_with_sources = dict(item)
        item_with_sources["sources"] = research_result.get("citations", [])
        ledger.upsert(key, item_with_sources)
        if confidence_gate(item.get("confidence")) != "HUMAN_REVIEW":
            improved = True
    info["low_confidence_retry_improved"] = improved
    if improved:
        augmented2, hits2 = en_injection.augment_style_prefix_with_pronunciation(
            style_prefix, text, min_confidence="medium")
        info["cache_hits"] = hits2
        info["hints_applied"] = bool(hits2)
        return augmented2, info
    return augmented, info
