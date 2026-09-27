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

import contextlib
import json
import os
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
# Sonnet修正1回目(Opus L2所見「テスト時web lookup禁止スイッチ」是正):
# 既定(未設定)は既存Production挙動を一切変えない(=許可)。テスト側が
# 明示的に`ALLOW_PRONUNCIATION_WEB_LOOKUP=0`を設定した場合のみ、有料API
# (JA web_search / EN Perplexity)呼び出しをその場でfail-safe(既存の
# 「解決できなかった」扱い、skipped=True)にする。無mockのままproduction
# 関数を直接呼ぶ既存/将来のtestで、fixture文に外来語が含まれていても
# 実API呼び出し・本番Ledger書き込みが発生しないことを恒久的に保証する
# ためのスイッチ(disable_web_lookup_for_test()参照)。
# ------------------------------------------------------------
ALLOW_PRONUNCIATION_WEB_LOOKUP_ENV = "ALLOW_PRONUNCIATION_WEB_LOOKUP"


def _web_lookup_allowed() -> bool:
    return os.environ.get(ALLOW_PRONUNCIATION_WEB_LOOKUP_ENV, "1") != "0"


@contextlib.contextmanager
def disable_web_lookup_for_test():
    """test側から使う恒久的なweb lookup禁止スイッチ。with文の間、
    `research_ja_readings`/`resolve_and_augment_en_style_prefix`の低
    confidence再researchが実API呼び出しを行わずfail-safe結果を返す。"""
    orig = os.environ.get(ALLOW_PRONUNCIATION_WEB_LOOKUP_ENV)
    os.environ[ALLOW_PRONUNCIATION_WEB_LOOKUP_ENV] = "0"
    try:
        yield
    finally:
        if orig is None:
            os.environ.pop(ALLOW_PRONUNCIATION_WEB_LOOKUP_ENV, None)
        else:
            os.environ[ALLOW_PRONUNCIATION_WEB_LOOKUP_ENV] = orig


# ------------------------------------------------------------
# Sonnet修正1回目(Opus L2所見「negative cache無し」「run単位lookup上限・
# telemetry」是正): 1プロセス(記事1本の生成に相当)あたりのJA web
# lookup実行回数(research_ja_readings()の実API呼び出し回数、tokenの
# 個数ではない)に上限を設ける。上限超過時はfail-safeで「解決できな
# かった」扱いにし、既存HUMAN_REVIEWへ自然に倒す(既存Gateを緩めない)。
# ------------------------------------------------------------
MAX_JA_WEB_LOOKUP_CALLS_PER_RUN = 5
_JA_WEB_LOOKUP_CALL_COUNT = 0

# ------------------------------------------------------------
# Sonnet修正2回目(Opus L2所見S4(a)是正、JA同型): EN側
# (resolve_and_augment_en_style_prefixのlow-confidence再research、
# en_research.research_pronunciations経由のPerplexity呼び出し)にも
# 1プロセスあたりの上限を設ける。既定値・仕組みはJA側と同一
# (超過時はfail-safeで既存の「解決できなかった」扱いへ倒す)。
# ------------------------------------------------------------
MAX_EN_WEB_LOOKUP_CALLS_PER_RUN = 5
_EN_WEB_LOOKUP_CALL_COUNT = 0

TELEMETRY_PATH = "er025_output/pronunciation_resolution_core_telemetry_01/telemetry.jsonl"


def _log_telemetry(event: dict) -> None:
    try:
        os.makedirs(os.path.dirname(TELEMETRY_PATH), exist_ok=True)
        with open(TELEMETRY_PATH, "a", encoding="utf-8") as f:
            record = dict(event)
            record["logged_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError:
        pass  # telemetryはbest-effort。書き込み失敗でも本処理は継続する。


# ------------------------------------------------------------
# run内(同一プロセス内)の重複解決回避用in-memory cache。
# 記事をまたいでプロセスが再起動されればLedger(永続store)がcacheとして
# 機能するため、ここはあくまで「同一記事内でのAPI呼び出し削減」用。
# Sonnet修正1回目(Opus L2 BLOCKER-2是正): JA run cacheのkeyへ
# source_contextを含める(同じsurfaceでも文脈が異なれば別cache行にする)。
# ------------------------------------------------------------
_JA_RUN_CACHE: dict[str, dict] = {}
_EN_LOW_CONFIDENCE_RETRY_DONE: set[str] = set()


def _ja_run_cache_key(surface_lower: str, source_context: str) -> str:
    return f"{(source_context or '').strip().lower()}\x00{surface_lower}"


def reset_run_caches() -> None:
    """test/新しい記事runの開始時にin-memory cacheをクリアする(既定では
    呼ばれない。プロセスが記事ごとに再起動される現行運用では通常不要だが、
    同一プロセス内で複数記事を扱うテスト・将来のバッチ実行向けに用意する)。"""
    global _JA_WEB_LOOKUP_CALL_COUNT, _EN_WEB_LOOKUP_CALL_COUNT
    _JA_RUN_CACHE.clear()
    _EN_LOW_CONFIDENCE_RETRY_DONE.clear()
    _JA_WEB_LOOKUP_CALL_COUNT = 0
    _EN_WEB_LOOKUP_CALL_COUNT = 0


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


_SOURCE_URL_RE = re.compile(r"https?://[^\s,;、]+")


def split_ja_reading_sources(raw_source: str) -> list[str]:
    """PRONUNCIATION-RESOLUTION-ALL-ACTIVE-FAMILIES-PRODUCTION-01(Sonnet修正
    1回目、Opus L2所見「ja_reading_sourcesが1件しか保存されない」フォロー
    アップ): SOURCE行の生文字列にURLが複数含まれる場合、それぞれを個別の
    リスト要素として保存する(1件も見つからない場合は既存どおり生文字列
    1件のまま、fail-safe: 情報が失われる方向の変更はしない)。"""
    raw_source = (raw_source or "").strip()
    urls = _SOURCE_URL_RE.findall(raw_source)
    if len(urls) >= 2:
        return urls
    return [raw_source] if raw_source else []


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
    (OPEN-146 run_canonical_spelling_research()と同型の非発火設計)。

    Sonnet修正1回目(Opus L2所見「テスト時web lookup禁止スイッチ」是正):
    `disable_web_lookup_for_test()`使用中(または`ALLOW_PRONUNCIATION_WEB_
    LOOKUP=0`)はAPI呼び出し自体を行わずfail-safe(skipped=True)を返す。"""
    if not surfaces:
        return {"raw_text": None, "model": None, "response_id": None,
                "search_usage": None, "sources": [], "parsed": [], "skipped": True}
    if not _web_lookup_allowed():
        return {"raw_text": None, "model": None, "response_id": None,
                "search_usage": None, "sources": [], "parsed": [], "skipped": True,
                "web_lookup_disabled_for_test": True}
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


NEGATIVE_CACHE_RESOLUTION_METHOD = "negative_cache_unresolved"
JA_NEGATIVE_CACHE_COOLDOWN_SECONDS = 6 * 60 * 60  # 6時間(Opus L2所見「negative cache無し」是正)


def _within_negative_cache_cooldown(updated_at: Optional[str]) -> bool:
    if not updated_at:
        return False
    try:
        ts = time.mktime(time.strptime(updated_at, "%Y-%m-%dT%H:%M:%S"))
    except (ValueError, TypeError):
        return False
    return (time.time() - ts) < JA_NEGATIVE_CACHE_COOLDOWN_SECONDS


def resolve_unknown_ja_tokens(text: str, known_key_phrase_terms=None,
                               extra_dictionary: Optional[dict] = None,
                               context: str = "", client=None, source_context: str = "") -> dict:
    """日本語canonical text中の未知Latin外来語トークンを検出し、
    cache -> Ledger -> web lookup -> confidence判定 -> 高/中confidenceの
    読みをreading_dictionaryへ動的追加する(recon 3.2節)。

    source_context(既定""、Sonnet修正1回目、Opus L2 BLOCKER-2是正):
    同じ綴りが作品ごとに異なる読みを持つ場合(例: 太宰治『走れメロス』の
    「ディオニス」 vs 史実の「ディオニュシオス」)、呼び出し側が作品固有の
    文脈識別子(例: "family_z_melos")を渡すことで、Ledger上で別entryとして
    扱われる(`seed_work_canon_reading()`で事前seedしたentryをそのまま
    cache hitとして使う)。既定""は既存呼び出し元と完全後方互換。

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
    global _JA_WEB_LOOKUP_CALL_COUNT
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
        cache_key = _ja_run_cache_key(key, source_context)
        cached = _JA_RUN_CACHE.get(cache_key)
        negative_cache_active = False
        if cached is None:
            stored = ledger.get_ja_reading_entry(key, source_context=source_context)
            if stored and stored.get("ja_reading_katakana"):
                cached = stored
                _JA_RUN_CACHE[cache_key] = cached
            elif (stored and stored.get("resolution_method") == NEGATIVE_CACHE_RESOLUTION_METHOD
                    and _within_negative_cache_cooldown(stored.get("updated_at"))):
                # Sonnet修正1回目(Opus L2所見「negative cache無し」是正):
                # 直近のcooldown内で既にresearch済み・解決不能だった未知語は
                # 再lookupせず、そのままHUMAN_REVIEW対象として扱う
                # (無関係記事での毎回の有料再lookupを防ぐ、fail-safe側)。
                negative_cache_active = True
        if cached is not None:
            ja_conf = cached.get("ja_reading_confidence") or cached.get("confidence")
            # Sonnet修正1回目(Opus L2所見「Figma confidence不整合」是正):
            # cache hit時に鏡写しフィールドの不整合を検出したら、その場で
            # 再upsertして自己修復する(従来はcache hitではupsertされず
            # 不整合が永続していた)。
            if cached.get("ja_reading_confidence") and cached.get("confidence") != cached.get("ja_reading_confidence"):
                fixed_entry = dict(cached)
                fixed_entry["confidence"] = cached["ja_reading_confidence"]
                ledger.upsert_ja_reading_entry(key, fixed_entry, source_context=source_context)
                cached = fixed_entry
                _JA_RUN_CACHE[cache_key] = cached
            gate = confidence_gate(ja_conf)
            if gate in ("AUTO_USE", "ASR_BACKED"):
                base_dictionary.setdefault(key, cached["ja_reading_katakana"])
                resolved.append({"surface": token, "reading": cached["ja_reading_katakana"],
                                  "confidence": ja_conf, "source": "cache_or_ledger"})
            else:
                still_unresolved.append(token)
        elif negative_cache_active:
            still_unresolved.append(token)
            _log_telemetry({"event": "ja_negative_cache_hit_skip_lookup", "surface": token,
                             "source_context": source_context})
        else:
            need_lookup.append(token)

    if need_lookup:
        if _JA_WEB_LOOKUP_CALL_COUNT >= MAX_JA_WEB_LOOKUP_CALLS_PER_RUN:
            # Sonnet修正1回目(Opus L2所見「run単位lookup上限」是正): 1
            # プロセスあたりのJA web lookup API呼び出し回数に上限を設け、
            # 超過時はfail-safeで既存HUMAN_REVIEWへ倒す(既存Gateは緩めない)。
            still_unresolved.extend(need_lookup)
            _log_telemetry({"event": "ja_run_lookup_cap_reached", "tokens": need_lookup,
                             "cap": MAX_JA_WEB_LOOKUP_CALLS_PER_RUN, "source_context": source_context})
        else:
            _JA_WEB_LOOKUP_CALL_COUNT += 1
            research_meta = research_ja_readings(need_lookup, context=context, client=client)
            web_lookup_called = not research_meta.get("skipped", True)
            _log_telemetry({"event": "ja_web_lookup_call", "tokens": need_lookup,
                             "web_lookup_called": web_lookup_called, "source_context": source_context,
                             "model": research_meta.get("model"), "run_call_count": _JA_WEB_LOOKUP_CALL_COUNT})
            parsed_by_surface = {p["surface"].lower(): p for p in research_meta.get("parsed", [])}
            for token in need_lookup:
                key = token.lower()
                parsed = parsed_by_surface.get(key)
                if parsed is None:
                    still_unresolved.append(token)
                    if web_lookup_called:
                        # 実際にlookupを試みたが対象語の結果が得られなかった
                        # 場合のみnegative cacheを保存する(API未設定・disabled
                        # 等でskipされた場合は保存しない、fail-safe)。
                        neg_entry = {
                            "ja_reading_katakana": "", "ja_reading_confidence": "",
                            "resolution_method": NEGATIVE_CACHE_RESOLUTION_METHOD,
                            "resolved_at_stage": "pre_tts", "confidence": "",
                        }
                        ledger.upsert_ja_reading_entry(key, neg_entry, source_context=source_context)
                    continue
                gate = confidence_gate(parsed["confidence"])
                entry = {
                    "ja_reading_katakana": parsed["reading"], "ja_reading_confidence": parsed["confidence"],
                    "ja_reading_sources": split_ja_reading_sources(parsed["source"]), "resolution_method": "web_search",
                    "resolved_at_stage": "pre_tts",
                    # 旧(EN専用)confidenceフィールドにも同じ値を鏡写しし、
                    # EN側get_low_confidence_entries_for_text()がJA読みentryを
                    # 誤ってEN低confidence候補として拾わないようにする
                    # (entity_type="ja_reading_katakana"での除外と二重の安全策)。
                    "confidence": parsed["confidence"],
                }
                ledger.upsert_ja_reading_entry(key, entry, source_context=source_context)
                _JA_RUN_CACHE[_ja_run_cache_key(key, source_context)] = entry
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


def seed_work_canon_reading(surface: str, ja_katakana: str, en_hint: str = "",
                             source_context: str = "", sources: Optional[list] = None) -> str:
    """PRONUNCIATION-RESOLUTION-ALL-ACTIVE-FAMILIES-PRODUCTION-01(Sonnet
    修正1回目、Opus L2 BLOCKER-2是正): 作品固有の確定読みを、web lookupを
    介さず事前にLedgerへseedする(`resolution_method="work_canon"`、
    `confidence="high"`)。以後、同じ`(surface, source_context)`の組み合わせで
    `resolve_unknown_ja_tokens(..., source_context=source_context)`を呼ぶと、
    web lookupなしのcache hitとしてこの読みが使われる。

    一般機構(このcore全体で使われるsource_context分岐)のAPIであり、
    特定作品のためだけの専用コードパス・ハードコードされたif分岐では
    ない(呼び出し側がsource_context文字列を選ぶだけ)。

    en_hint(既定""): 英語発音のガイドが必要な場合(将来、EN側で同一
    entityの発音を揃えたい場合)にpronunciation_hintフィールドへ保存する。
    ただし本entry自体はentity_type="ja_reading_katakana"固定のため、EN側
    `get_hint_for_text()`(entity_type非フィルタ時)の検索対象には含まれる
    が、TTS注入呼び出し元は`exclude_entity_types`を指定していないため
    通常の高confidence entryとして扱われる(2026-09-27時点の実装、EN側の
    正式な作品固有発音供給は別途の配線判断)。"""
    entry = {
        "ja_reading_katakana": ja_katakana, "ja_reading_confidence": "high",
        "ja_reading_sources": sources or [], "resolution_method": "work_canon",
        "resolved_at_stage": "seed", "confidence": "high", "pronunciation_hint": en_hint,
    }
    return ledger.upsert_ja_reading_entry(surface, entry, source_context=source_context)


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

    Sonnet修正1回目(Opus L2 BLOCKER-1是正): `entity_type=="cascade_
    unresolved_entity"`(ASR Cascade Human Review packaging専用)のentryは
    低confidence再research対象からも除外する(BLOCKER-1の"ganis"→
    "organisation"のような語境界外一致は`_surface_matches_text`側で既に
    防げているが、この経路自体もStage 2専用entryを対象にしない設計へ
    揃える)。あわせて`disable_web_lookup_for_test()`使用中は有料API
    (Perplexity)を呼ばずfail-safeで戻る。

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
        e for e in ledger.get_low_confidence_entries_for_text(
            text, exclude_entity_types={ledger.CASCADE_UNRESOLVED_ENTITY_TYPE})
        if (e.get("confidence") == "low") and (e.get("entity_type") != ledger.JA_READING_ENTITY_TYPE)
        and (e["surface"].lower() not in _EN_LOW_CONFIDENCE_RETRY_DONE)
    ]
    if not low_conf_candidates:
        return augmented, info

    if not _web_lookup_allowed():
        return augmented, info

    global _EN_WEB_LOOKUP_CALL_COUNT
    if _EN_WEB_LOOKUP_CALL_COUNT >= MAX_EN_WEB_LOOKUP_CALLS_PER_RUN:
        # Sonnet修正2回目(Opus L2所見S4(a)是正): JA側と同じ「1プロセス
        # あたりの上限」。超過時はfail-safeでlow_confidence_retry_
        # attempted=Falseのまま(=このrunでは再research不能だった)扱いに
        # する。`_EN_LOW_CONFIDENCE_RETRY_DONE`へは追加しない(このrun内で
        # 恒久的にブロックするのではなく、単に今回分のweb lookup予算切れ
        # であることを示すため。次のプロセス[記事]では上限がリセットされ、
        # 通常どおり再試行できる)。
        _log_telemetry({"event": "en_run_lookup_cap_reached",
                         "surfaces": [e["surface"] for e in low_conf_candidates],
                         "cap": MAX_EN_WEB_LOOKUP_CALLS_PER_RUN})
        return augmented, info

    info["low_confidence_retry_attempted"] = True
    entities = [{"surface": e["surface"], "entity_type": e.get("entity_type", "unknown"),
                 "risk_reason": "既存Ledgerでconfidence=lowのため、pre_tts配線時に再research"}
                for e in low_conf_candidates]
    for e in low_conf_candidates:
        _EN_LOW_CONFIDENCE_RETRY_DONE.add(e["surface"].lower())
    _EN_WEB_LOOKUP_CALL_COUNT += 1
    research_result = en_research.research_pronunciations(entities)
    info["research_meta"] = research_result
    _log_telemetry({"event": "en_web_lookup_call",
                     "surfaces": [e["surface"] for e in low_conf_candidates],
                     "run_call_count": _EN_WEB_LOOKUP_CALL_COUNT,
                     "status": research_result.get("status")})
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


def augment_style_prefix_with_cached_hits(style_prefix: str, hits: list) -> str:
    """Sonnet修正2回目(Opus L2所見S3是正、非対称解消): `generate_charon_
    english`等が既にresolve_and_augment_en_style_prefix()で算出済みの
    `cache_hits`を、Ledgerへ再アクセスせずそのまま別のbase style_prefix
    (技術的fallbackのMINIMAL_INSTRUCTION_PREFIX等)へ適用するための薄い
    wrapper。新規web lookup・新規Ledger読み取りは一切発生しない(純粋な
    文字列整形のみ、`en_injection.apply_precomputed_hints_to_style_
    prefix`をそのまま呼ぶ)。hitsが空ならstyle_prefixをそのまま返す。"""
    return en_injection.apply_precomputed_hints_to_style_prefix(style_prefix, hits)
