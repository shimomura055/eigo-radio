# -*- coding: utf-8 -*-
"""固有名詞発音取得改善 Stage 1 の純関数群(未配線module。Production .pyは本fileをimportしない)。

管理: PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02 委任_03 [E-1]。設計=docs/research/PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02/
STAGE1_IMPLEMENTATION_DESIGN_01.md。ユーザー承認(2026-10-22)=Stage 1実施。**PASS/NG判定・自動PASS条件は変えない**:
本moduleは「最終slotのHuman Review用 発音情報取得」(`er006_secondary_asr_01._resolve_unresolved_entity_for_review`)の
前後だけを対象とし、judge/M1/Case A/L1の入出力には触れない(importしない)。

機能(純関数。I/Oは引数注入。実HTTP・実API・実Ledger書込は本moduleでは行わない):
  1. 否定記録  : classify_research_outcome / build_negative_record / negative_status / NegativeCacheStore(sidecar file)
  2. 統一lookup : unified_lookup (entity_type非依存。ja_reading_katakana=日本語読みは英語発音の根拠でないため除外)
  3. 一般語除外 : is_general_word_span (CMU収録 かつ 全token wordfreq zipf>=閾値)。除外は「調査を呼ばない」だけ。
  4. HR階層表示: evidence_tier / hr_display (表示専用の追加キー)
  5. 引用実在確認(V1'): verify_citations (取得関数を注入。安全条件: http/https・SSRF遮断・サイズ/時間上限・テキスト抽出のみ)
  6. 統合判断   : decide_span_action (USE_LEDGER / SKIP_ISOLATED_ENTRY / SKIP_GENERAL_WORD / SKIP_NEGATIVE_CACHE / RESEARCH)
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import html as _html
import ipaddress
import json
import os
import re
import socket
import unicodedata
import uuid
from typing import Callable, Optional
from urllib.parse import urlparse

# ---- 定数(rollbackはProduction側の単一定数で行う。本moduleは値を持つだけ) ----
NEGATIVE_TTL_DAYS = 60              # 暫定(ユーザー承認=計画上60日。Stage 2 Trial再取得データで見直し)
GENERAL_WORD_MIN_ZIPF = 4.0         # 全tokenのwordfreq zipf下限(実測: 一般語6語は4.44以上、固有名詞系は3.59以下)
FETCH_MAX_BYTES = 512 * 1024
FETCH_TIMEOUT_SEC = 5.0
FETCH_MAX_URLS = 3
EXCLUDED_ENTITY_TYPES = frozenset({"ja_reading_katakana"})   # 日本語読みは英語発音の根拠にしない(M1も除外)
RESEARCH_ENTITY_TYPE = "cascade_unresolved_entity"           # 調査用type(旧lookupが見ていた唯一のtype)。このtypeのentryは従来どおり最優先で処理する(S1-04)
PRON_SUPPLY_STAGE1_ENABLED = True   # 全体ON/OFFの単一定数(S1-08)。サポート組合せは「全ON/全OFF」のみ。OFF時はresolve_span_for_reviewが
                                    # action=DISABLED_USE_LEGACYを返し、副作用ゼロ(呼出側が従来関数へ戻す)。項目別定数は持たない。
MIN_PRON_FORM_LEN = 5               # 発音表記の照合に使う最小長(正規化後、空白除く。S1-07)

OUTCOME_FOUND = "FOUND"
OUTCOME_NOT_FOUND = "NOT_FOUND"
OUTCOME_TRANSIENT = "TRANSIENT"

ACTION_USE_LEDGER = "USE_LEDGER"
ACTION_SKIP_ISOLATED = "SKIP_ISOLATED_ENTRY"
ACTION_SKIP_GENERAL = "SKIP_GENERAL_WORD"
ACTION_SKIP_NEGATIVE = "SKIP_NEGATIVE_CACHE"
ACTION_RESEARCH = "RESEARCH"
ACTION_DISABLED = "DISABLED_USE_LEGACY"

TIER_QUOTE_VERIFIED = "QUOTE_VERIFIED"            # 出典ページに引用文が実在(Stage 2のresearch形式で付与。Stage 1は表示のみ)
TIER_PRON_IN_PAGE = "PRON_IN_CITED_PAGE"          # 出典ページ本文に名称と発音表記(IPA/ヒント)が実在(出典ページ照合V1'=弱い確認。引用実在確認ではない)
TIER_NAME_IN_PAGE = "NAME_IN_CITED_PAGE"          # 出典ページ本文に名称のみ実在(発音表記は未確認)
TIER_UNVERIFIED = "UNVERIFIED_AI_OUTPUT"          # 出典はあるが取得失敗/不一致=AI出力のまま(拒否ではない)
TIER_NO_SOURCE = "NO_SOURCE"                      # 出典なし
TIER_HUMAN = "HUMAN_APPROVED"
TIER_NEGATIVE = "NEGATIVE_SEARCHED_NOT_FOUND"
TIER_GENERAL = "GENERAL_WORD_NOT_SEARCHED"
TIER_LABELS_JA = {
    TIER_QUOTE_VERIFIED: "引用確認済み(出典ページに引用文が実在)",
    TIER_PRON_IN_PAGE: "出典ページに発音表記あり(公式/実使用の区別は未判定)",
    TIER_NAME_IN_PAGE: "出典ページに名称のみ(発音表記は未確認)",
    TIER_UNVERIFIED: "AI出力・出典未検証",
    TIER_NO_SOURCE: "出典なし",
    TIER_HUMAN: "人間承認済み",
    TIER_NEGATIVE: "調査済み・未取得",
    TIER_GENERAL: "通常の英語語彙のため調査省略",
}
_CONF_RANK = {"high": 3, "medium": 2, "low": 1}


# ---------------------------------------------------------------- 共通
def fold(s: str) -> str:
    """アクセント除去+小文字化+空白正規化(er006_pronunciation_ledger_01._foldと同義)。"""
    t = unicodedata.normalize("NFKD", s or "")
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", t.strip().lower())


def norm_surface(s: str) -> str:
    """鍵用の正規化: fold + 前後の句読点除去。entity_typeを含まない。"""
    return re.sub(r"^[^\w]+|[^\w]+$", "", fold(s))


def _parse_ts(ts) -> Optional[_dt.datetime]:
    if not ts:
        return None
    try:
        return _dt.datetime.strptime(str(ts)[:19], "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        return None


def _fmt(dt: _dt.datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%S")


def _has_usable_info(e: dict) -> bool:
    return bool((e.get("expected_pronunciation_ipa") or "").strip() or (e.get("pronunciation_hint") or "").strip())


# ---------------------------------------------------------------- 1. 否定記録
def classify_research_outcome(research: Optional[dict], exception: Optional[BaseException] = None) -> str:
    """research_pronunciations()の結果を分類する。
    TRANSIENT=一時失敗(例外/CREDENTIAL_REQUIRED/HTTP失敗/items欠落[応答不正]) -> 否定記録を**保存しない**。
    NOT_FOUND=status OKで応答は正常だが、調査結果itemが1件も無い(現行実装ではLedgerに何も残らず、次回も再調査になる唯一のケース)
              -> 否定記録の対象。
    FOUND=itemが1件以上ある(IPA/hintが空でも現行どおりLedgerへupsertされ、次回は命中扱い=再調査されない。品質の高低は階層表示で区別)。"""
    if exception is not None or not isinstance(research, dict):
        return OUTCOME_TRANSIENT
    if research.get("status") != "OK":
        return OUTCOME_TRANSIENT
    items = research.get("items")
    if not isinstance(items, list):
        return OUTCOME_TRANSIENT
    return OUTCOME_FOUND if items else OUTCOME_NOT_FOUND


def build_negative_record(surface: str, outcome: str, *, now: _dt.datetime, ttl_days: int = NEGATIVE_TTL_DAYS,
                          reason: str = "research_ok_no_pronunciation_info") -> Optional[dict]:
    """NOT_FOUNDのときだけ否定記録dictを返す。TRANSIENT/FOUNDはNone(保存しない)。"""
    if outcome != OUTCOME_NOT_FOUND:
        return None
    key = norm_surface(surface)
    if not key:
        return None
    return {"key": key, "surface": surface, "searched_at": _fmt(now),
            "negative_until": _fmt(now + _dt.timedelta(days=ttl_days)), "ttl_days": ttl_days, "reason": reason}


NEG_ACTIVE, NEG_EXPIRED, NEG_INVALIDATED, NEG_ABSENT = "ACTIVE", "EXPIRED", "INVALIDATED", "ABSENT"


def negative_status(rec: Optional[dict], *, now: _dt.datetime, ledger_entries: Optional[list] = None) -> str:
    """ACTIVE=再調査しない / EXPIRED=期間後 / INVALIDATED=人間承認または新登録で即無効 / ABSENT=記録なし。
    INVALIDATED条件: 同綴りの(除外type以外の)有効entryが記録時刻より後に発音情報つきで作成・更新された、またはhuman_approvedなentryがある。"""
    if not rec:
        return NEG_ABSENT
    searched = _parse_ts(rec.get("searched_at"))
    for e in ledger_entries or []:
        if e.get("ledger_disabled") or e.get("entity_type") in EXCLUDED_ENTITY_TYPES:
            continue
        if e.get("human_approved"):
            return NEG_INVALIDATED
        upd = _parse_ts(e.get("updated_at"))
        if searched and upd and upd > searched and _has_usable_info(e):
            return NEG_INVALIDATED
    until = _parse_ts(rec.get("negative_until"))
    if until is None:
        return NEG_EXPIRED
    return NEG_ACTIVE if now < until else NEG_EXPIRED


class NegativeCacheStore:
    """否定記録のsidecar store(JSON。Ledger本体 ledger.json は読み書きしない)。
    sidecarにする理由: 「見つからなかった語」にはLedger entryが存在せず、擬似entryを作るとM1 C2/Phrase List/
    get_low_confidence_entries等の全readerに混入する(設計書 1-1)。pathは呼出側が与える(本moduleは既定pathを持たない)。"""

    def __init__(self, path: str):
        self.path = path

    def _load(self) -> dict:
        if not os.path.exists(self.path):
            return {}
        try:
            with open(self.path, encoding="utf-8") as f:
                d = json.load(f)
            return d if isinstance(d, dict) else {}
        except Exception:   # noqa: BLE001  破損・権限・文字コード等すべて「記録なし」扱い(=従来どおり調査する。安全側, S1-03)
            return {}

    def get(self, surface: str) -> Optional[dict]:
        rec = self._load().get(norm_surface(surface))
        return rec if isinstance(rec, dict) else None

    def put(self, rec: Optional[dict]) -> bool:
        if not rec:
            return False
        d = self._load()
        d[rec["key"]] = rec
        self._atomic_write(d)
        return True

    def invalidate(self, surface: str) -> bool:
        d = self._load()
        k = norm_surface(surface)
        if k in d:
            del d[k]
            self._atomic_write(d)
            return True
        return False

    def _atomic_write(self, d: dict) -> None:
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        tmp = f"{self.path}.{os.getpid()}.{uuid.uuid4().hex[:8]}.tmp"   # 並列run同士で一時fileを共有しない(S1-03)
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(d, f, ensure_ascii=False, indent=2, sort_keys=True)
            os.replace(tmp, self.path)
        finally:
            if os.path.exists(tmp):
                try:
                    os.remove(tmp)
                except OSError:
                    pass


# ---------------------------------------------------------------- 2. 統一lookup
def _canonical_ok(surface_key: str, e: dict) -> bool:
    """OF-181(a)相当: canonical_spellingがsurfaceと無関係な混入entry("us"->"unknown")は採用しない。"""
    c = norm_surface(e.get("canonical_spelling") or "")
    if not c:
        return True
    return surface_key in c or c in surface_key


def unified_lookup(ledger: dict, surface: str) -> tuple:
    """同綴り(norm_surface一致)のentryを、entity_typeに依存せず最上位1件返す(読取専用)。
    除外: ledger_disabled / ja_reading_katakana(日本語読み) / canonical_spellingがsurfaceと無関係。
    順位: human_approved > confidence(high>medium>low) > 発音情報あり > 出典あり > updated_at新しい。
    戻り値=(entry|None, meta)。metaはcandidates(件数)・picked_entity_type・picked_ledger_id・excluded(理由別件数)。"""
    key = norm_surface(surface)
    excluded: dict = {}
    cands = []
    for lid, e in (ledger or {}).items():
        if norm_surface(e.get("surface", "")) != key:
            continue
        if e.get("entity_type") in EXCLUDED_ENTITY_TYPES:
            excluded["ja_reading_katakana"] = excluded.get("ja_reading_katakana", 0) + 1
            continue
        if e.get("ledger_disabled"):
            excluded["ledger_disabled"] = excluded.get("ledger_disabled", 0) + 1
            continue
        if not _canonical_ok(key, e):
            excluded["canonical_unrelated"] = excluded.get("canonical_unrelated", 0) + 1
            continue
        rank = (1 if e.get("human_approved") else 0, _CONF_RANK.get(e.get("confidence", ""), 0),
                1 if _has_usable_info(e) else 0, 1 if e.get("sources") else 0, str(e.get("updated_at") or ""))
        cands.append((rank, lid, e))
    cands.sort(key=lambda x: x[0], reverse=True)
    meta = {"candidates": len(cands), "excluded": excluded,
            "picked_entity_type": cands[0][2].get("entity_type") if cands else None,
            "picked_ledger_id": cands[0][1] if cands else None}
    return (cands[0][2] if cands else None), meta


# ---------------------------------------------------------------- 3. 一般語除外
def _default_cmu_has(token: str) -> bool:
    import pronouncing
    return bool(pronouncing.phones_for_word(token.lower().strip("'")))


def _default_zipf(token: str) -> float:
    from wordfreq import zipf_frequency
    return zipf_frequency(token, "en")


def is_general_word_span(span: str, *, cmu_has: Callable = _default_cmu_has, zipf: Callable = _default_zipf,
                         min_zipf: float = GENERAL_WORD_MIN_ZIPF) -> bool:
    """spanの全tokenが(a)CMU収録 かつ (b)通常の英語語彙(wordfreq zipf>=min_zipf)なら一般語/一般句。
    「調査を呼ぶか」の判定専用。PASS/NGには影響しない。CMU収録語はM1のC2(CMU未収録語のみ対象)でも
    使われないため、除外によってM1候補集合は変わらない。"""
    toks = re.findall(r"[a-z0-9']+", fold(span))
    if not toks:
        return False
    return all(cmu_has(t) and zipf(t) >= min_zipf for t in toks)


# ---------------------------------------------------------------- 5. 引用実在確認(V1')
def is_safe_url(url: str, *, resolver: Optional[Callable] = None) -> bool:
    """http/httpsのみ。loopback/private/link-local/reserved宛は遮断(SSRF)。解決不能はFalse。"""
    try:
        p = urlparse(url)
        if p.scheme not in ("http", "https") or not p.hostname:
            return False
        addrs = resolver(p.hostname) if resolver else [ai[4][0] for ai in socket.getaddrinfo(p.hostname, None)]
    except Exception:   # noqa: BLE001  名前解決・URL解析のどの失敗も「安全と確認できない」=False(S1-03)
        return False
    if not addrs:
        return False
    for a in addrs:
        try:
            ip = ipaddress.ip_address(a)
        except ValueError:
            return False
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast or ip.is_unspecified:
            return False
    return True


def html_to_text(raw: str) -> str:
    """HTML->テキスト(script/style除去、タグ除去、実体参照復号)。実行・外部読込はしない。"""
    t = re.sub(r"(?is)<(script|style|noscript)\b.*?</\1\s*>", " ", raw or "")
    t = re.sub(r"(?s)<!--.*?-->", " ", t)
    t = re.sub(r"(?s)<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", _html.unescape(t)).strip()


_KEEP = "0-9a-zæœøðþßɐ-ʯθŋ"          # 照合に使う文字(英数字+æ等+IPA主要範囲)。それ以外は空白に置換(S1-07)
_IPA_MARKS_RE = re.compile(r"[ˈˌːˑ.‿/\[\]()]")


def _words(s: str, *, ipa: bool = False) -> str:
    """空白を残した正規化テキスト(語境界つき照合用)。ipa=Trueは強勢・長音・括弧等を削除してから正規化する。"""
    t = fold(s)
    if ipa:
        t = _IPA_MARKS_RE.sub("", t)
    return re.sub(r"\s+", " ", re.sub(f"[^{_KEEP}]+", " ", t)).strip()


def _has_phrase(hay: str, needle: str) -> bool:
    """語境界つき部分一致(hay/needleは_wordsの出力)。'ottoni'は'bottonix'にはマッチしない。"""
    return bool(needle) and f" {needle} " in f" {hay} "


def _pron_forms(entry: dict) -> list:
    """[(kind, form)]。kind='ipa'|'words'。正規化後(空白除く)がMIN_PRON_FORM_LEN未満の表記は照合に使わない(偶然一致防止)。"""
    forms = []
    ipa = (entry.get("expected_pronunciation_ipa") or "").strip()
    if ipa:
        forms.append(("ipa", ipa))
    hint = (entry.get("pronunciation_hint") or "").strip()
    if hint:
        forms.append(("words", hint))
    for a in entry.get("alternate_pronunciations") or []:
        if isinstance(a, str) and a.strip():
            forms.append(("ipa" if (not a.isascii() or a.strip().startswith(("/", "["))) else "words", a.strip()))
    out = []
    for kind, f in forms:
        w = _words(f, ipa=(kind == "ipa"))
        if len(w.replace(" ", "")) >= MIN_PRON_FORM_LEN:
            out.append((kind, w))
    return out


def verify_citations(entry: dict, fetch: Callable, *, max_urls: int = FETCH_MAX_URLS, timeout: float = FETCH_TIMEOUT_SEC,
                     max_bytes: int = FETCH_MAX_BYTES, url_ok: Callable = is_safe_url) -> dict:
    """【出典ページ照合V1'=名称・発音表記の出現確認(弱い確認)。承認された「引用実在確認」そのものではない。保存キーevidence_check/tier名は互換のため維持、
    報告上の名称は`source_page_check_v1`】出典URLを取得し、(1)evidence[].quoteがあれば本文への実在、(2)なければ名称+発音表記(IPA/hint)の実在を語境界つきで確認する。
    fetch(url, timeout, max_bytes) -> 本文(str, HTML可)またはNone(失敗)。**失敗は拒否ではなく`UNVERIFIED_AI_OUTPUT`**。
    読取専用: Ledgerを書換えない。戻り値は表示/記録用のdict(tier, checked, details)。"""
    urls = [u for u in (entry.get("sources") or []) if isinstance(u, str)]
    ev = [x for x in (entry.get("evidence") or []) if isinstance(x, dict) and x.get("url") and x.get("quote")]
    if not urls and not ev:
        return {"tier": TIER_NO_SOURCE, "checked": 0, "details": []}
    ev_urls = {x["url"] for x in ev}
    targets = [(x["url"], x["quote"]) for x in ev] + [(u, None) for u in urls if u not in ev_urls]
    name = _words(entry.get("canonical_spelling") or entry.get("surface") or "")
    forms = _pron_forms(entry)
    best, details, n = TIER_UNVERIFIED, [], 0
    order = {TIER_UNVERIFIED: 0, TIER_NAME_IN_PAGE: 1, TIER_PRON_IN_PAGE: 2, TIER_QUOTE_VERIFIED: 3}
    for url, quote in targets[:max_urls]:
        n += 1
        if not url_ok(url):
            details.append({"url": url, "result": "BLOCKED_UNSAFE_URL"})
            continue
        try:
            raw = fetch(url, timeout, max_bytes)
        except Exception as ex:   # 取得失敗は検証失敗(=未検証)であり例外を伝播させない
            details.append({"url": url, "result": "FETCH_ERROR", "error": type(ex).__name__})
            continue
        if raw is None:
            details.append({"url": url, "result": "FETCH_FAILED"})
            continue
        text = html_to_text(raw[:max_bytes])
        sq = _words(text)
        sq_ipa = _words(text, ipa=True)
        q = _words(quote) if quote else ""
        if q and _has_phrase(sq, q):
            tier = TIER_QUOTE_VERIFIED
        elif forms and _has_phrase(sq, name) and any(_has_phrase(sq_ipa if k == "ipa" else sq, f) for k, f in forms):
            tier = TIER_PRON_IN_PAGE
        elif _has_phrase(sq, name):
            tier = TIER_NAME_IN_PAGE
        else:
            tier = TIER_UNVERIFIED
        details.append({"url": url, "result": tier, "text_len": len(text)})
        if order[tier] > order[best]:
            best = tier
    return {"tier": best, "checked": n, "details": details}


# ---------------------------------------------------------------- 4. HR階層表示(表示専用)
def evidence_tier(entry: Optional[dict], verification: Optional[dict] = None) -> str:
    """entryの根拠階層ラベル。verification(V1'の結果)があればそれを、無ければentry保存済みの`evidence_tier`、
    それも無ければ出典の有無から保守的に決める(未検証=UNVERIFIED_AI_OUTPUT)。**PASS根拠には使わない(Stage 1は表示のみ)**。"""
    if not entry:
        return TIER_NO_SOURCE
    if entry.get("human_approved"):
        return TIER_HUMAN
    if verification and verification.get("tier"):
        return verification["tier"]
    if entry.get("evidence_tier"):
        return entry["evidence_tier"]
    return TIER_UNVERIFIED if entry.get("sources") else TIER_NO_SOURCE


def hr_display(info: Optional[dict], *, action: str, lookup_meta: Optional[dict] = None, negative: Optional[dict] = None,
               verification: Optional[dict] = None, general_word: bool = False) -> dict:
    """pronunciation_lookups[span]へ**追加**するキー群を返す(既存キーは上書きしない)。
    keys: same_spelling_other_type(別type採用時のみ) / evidence_tier / evidence_tier_label_ja / lookup_action / lookup_entity_type / source_urls /
    negative_searched_at / negative_until / citation_check / display_lines_ja。"""
    if action == ACTION_SKIP_GENERAL or (action == ACTION_SKIP_ISOLATED and general_word):
        tier = TIER_GENERAL
    elif action == ACTION_SKIP_NEGATIVE:
        tier = TIER_NEGATIVE
    else:
        tier = evidence_tier(info, verification)
    urls = [u for u in ((info or {}).get("sources") or []) if isinstance(u, str)][:3]
    lines = [f"根拠階層: {TIER_LABELS_JA[tier]}"]
    other_type = None
    if action == ACTION_USE_LEDGER and info and info.get("entity_type") not in (None, RESEARCH_ENTITY_TYPE):
        other_type = info.get("entity_type")      # S1-05: 調査用type以外のentryを採用した場合は同一対象かの未確認を明示
        lines.append(f"同綴りの別entry(type={other_type})の情報。同一対象かは未確認")
    if action == ACTION_SKIP_NEGATIVE and negative:
        lines.append(f"調査済み・未取得({str(negative.get('searched_at',''))[:10]}調査、"
                     f"{str(negative.get('negative_until',''))[:10]}まで再調査しない)")
    if urls:
        lines.append("出典: " + " / ".join(urls))
    if (info or {}).get("confidence"):
        lines.append(f"AI報告の確信度(参考): {info['confidence']}")
    extra = {"evidence_tier": tier, "evidence_tier_label_ja": TIER_LABELS_JA[tier], "lookup_action": action,
             "lookup_entity_type": (lookup_meta or {}).get("picked_entity_type"), "source_urls": urls,
             "display_lines_ja": lines}
    if other_type:
        extra["same_spelling_other_type"] = other_type
    if negative:
        extra["negative_searched_at"] = negative.get("searched_at")
        extra["negative_until"] = negative.get("negative_until")
    if verification:
        extra["citation_check"] = {"tier": verification.get("tier"), "checked": verification.get("checked")}
    return extra


# ---------------------------------------------------------------- 6. 統合判断
def decide_span_action(span: str, ledger: dict, neg_store: Optional[NegativeCacheStore], *, now: _dt.datetime,
                       cmu_has: Callable = _default_cmu_has, zipf: Callable = _default_zipf) -> dict:
    """最終slotのentity-like不一致spanについて、調査(有料)を呼ぶかを決める。優先順(上で確定すれば下は評価しない):
      0. 調査用type(RESEARCH_ENTITY_TYPE)のentryが同綴りにある -> 従来のlookupと同じ扱いを**最優先**(S1-04):
           有効entry -> USE_LEDGER(発音情報の有無を問わない) / ledger_disabled -> SKIP_ISOLATED_ENTRY(HR情報なし・再調査なし)
      1. USE_LEDGER         : 別typeの有効entryで発音情報つき(unified_lookup。旧lookupの取りこぼし解消)。発音情報の無い別typeのentryは調査を止めない
      2. SKIP_GENERAL_WORD  : 一般語/一般句
      3. SKIP_NEGATIVE_CACHE: 否定記録がACTIVE(記録の取得・評価で例外が出た場合は「記録なし」扱い=調査する)
      4. RESEARCH           : 上記すべて非該当(従来どおり1回調査)
    互換性不変条件: 旧lookupが命中していた(同surfaceのcascade_unresolved_entity entryがある)場合は決してRESEARCHにならない。"""
    key = norm_surface(span)
    same = [e for e in (ledger or {}).values() if norm_surface(e.get("surface", "")) == key]
    own = [e for e in same if e.get("entity_type") == RESEARCH_ENTITY_TYPE]
    if own:
        live = [e for e in own if not e.get("ledger_disabled")]
        if live:
            best = sorted(live, key=lambda e: (1 if _has_usable_info(e) else 0, str(e.get("updated_at") or "")), reverse=True)[0]
            return {"action": ACTION_USE_LEDGER, "entry": best, "meta": {"candidates": len(live), "excluded": {},
                    "picked_entity_type": RESEARCH_ENTITY_TYPE, "picked_ledger_id": None}}
        return {"action": ACTION_SKIP_ISOLATED, "entry": None, "meta": {"candidates": 0, "excluded": {"ledger_disabled": len(own)},
                "picked_entity_type": None, "picked_ledger_id": None}, "general_word": _safe_general(span, cmu_has, zipf)}
    entry, meta = unified_lookup(ledger, span)
    if entry is not None and _has_usable_info(entry):
        return {"action": ACTION_USE_LEDGER, "entry": entry, "meta": meta}
    if _safe_general(span, cmu_has, zipf):
        return {"action": ACTION_SKIP_GENERAL, "entry": None, "meta": meta}
    rec, st = None, NEG_ABSENT
    try:
        rec = neg_store.get(span) if neg_store is not None else None
        st = negative_status(rec, now=now, ledger_entries=same)
    except Exception:   # noqa: BLE001  否定記録の取得・評価失敗は従来動作(=調査する)へ(S1-03)
        rec, st = None, NEG_ABSENT
    if st == NEG_ACTIVE:
        return {"action": ACTION_SKIP_NEGATIVE, "entry": None, "meta": meta, "negative": rec}
    return {"action": ACTION_RESEARCH, "entry": None, "meta": meta, "negative_status": st}


def _safe_general(span: str, cmu_has: Callable, zipf: Callable) -> bool:
    """一般語判定。辞書(pronouncing/wordfreq)のimport失敗等はFalse=従来どおり調査する側(S1-03)。"""
    try:
        return is_general_word_span(span, cmu_has=cmu_has, zipf=zipf)
    except Exception:   # noqa: BLE001
        return False


# ---------------------------------------------------------------- 5b. 既定の取得関数(読取専用GET。testではhttp_getを注入)
def default_fetch(url: str, timeout: float = FETCH_TIMEOUT_SEC, max_bytes: int = FETCH_MAX_BYTES, *,
                  http_get: Optional[Callable] = None, url_ok: Callable = is_safe_url, max_redirects: int = 3) -> Optional[str]:
    """GETのみ・redirectは手動で最大3回(各hopでurl_okを再検査)・応答はmax_bytesで打切り・text/html系のみ・
    取得物はメモリ上でテキスト化するだけ(ファイル保存・実行・外部resource読込なし)。失敗はNone。
    http_get(url, timeout) -> response(status_code, headers, iter_content(chunk_size)) 。既定はrequests.get(stream=True, allow_redirects=False)。"""
    if http_get is None:
        def http_get(u, t):   # pragma: no cover - 実HTTPはE-2のruntime evidenceでのみ使う
            rq = __import__("requests")
            return rq.get(u, timeout=t, stream=True, allow_redirects=False,
                          headers={"User-Agent": "eigo-radio-citation-check/1.0 (read-only)"})
    cur = url
    for _ in range(max_redirects + 1):
        if not url_ok(cur):
            return None
        resp = http_get(cur, timeout)
        code = getattr(resp, "status_code", 0)
        if code in (301, 302, 303, 307, 308):
            loc = (getattr(resp, "headers", {}) or {}).get("Location")
            if not loc:
                return None
            from urllib.parse import urljoin
            cur = urljoin(cur, loc)
            continue
        if code != 200:
            return None
        ctype = str((getattr(resp, "headers", {}) or {}).get("Content-Type", "")).lower()
        if ctype and not any(k in ctype for k in ("text/", "html", "xml", "json")):
            return None
        buf, total = [], 0
        for chunk in resp.iter_content(8192):
            if not chunk:
                continue
            total += len(chunk)
            buf.append(chunk[: max(0, max_bytes - (total - len(chunk)))])
            if total >= max_bytes:
                break
        return b"".join(buf).decode("utf-8", errors="replace")
    return None


# ---------------------------------------------------------------- 7. Human Review用の発音情報取得(旧 _resolve_unresolved_entity_for_review の置換版)
def resolve_span_for_review(span: str, *, ledger_loader: Callable, research_fn: Callable, upsert_fn: Callable,
                            neg_store: Optional[NegativeCacheStore], now: _dt.datetime,
                            fetch: Optional[Callable] = None, url_ok: Callable = is_safe_url, transient_exceptions: tuple = (OSError,),
                            cmu_has: Callable = _default_cmu_has, zipf: Callable = _default_zipf,
                            enabled: Optional[bool] = None) -> dict:
    """副作用(Ledger読込・調査API・Ledger登録)は全て引数で注入する。戻り値:
      info            : HR packageへ載せる既存形式のdict(従来の`_resolve_unresolved_entity_for_review`の戻り値と同じ形)またはNone
      extra           : hr_display(...)の追加キー(表示専用。呼出側が info(またはstub)へ重ねる)
      action/outcome  : 判断の記録(監査用)  research_called/negative_written : bool
    **PASS/NGに関与する値は返さない**。research_fn(span)->research dict、upsert_fn(span, item)->saved entry(dict)。
    enabled: None=module定数PRON_SUPPLY_STAGE1_ENABLED。Falseなら副作用ゼロでaction=DISABLED_USE_LEGACYを返す(呼出側が従来関数へ戻す, S1-08)。
    例外の扱い(S1-03): 否定記録のget/put・出典ページ照合V1'・HR表示キー生成の例外は捕捉して従来動作へ(照合/表示なしで続行)。
    research_fn(調査API)のtransient_exceptions以外(cost logger未初期化等)・ledger_loader・upsert_fnの例外は従来どおり伝播させる(揉み消さない)。"""
    if not (PRON_SUPPLY_STAGE1_ENABLED if enabled is None else enabled):
        return {"info": None, "extra": {}, "action": ACTION_DISABLED, "outcome": None, "research_called": False, "negative_written": False}
    ledger = ledger_loader()
    d = decide_span_action(span, ledger, neg_store, now=now, cmu_has=cmu_has, zipf=zipf)
    act = d["action"]
    out = {"info": None, "extra": {}, "action": act, "outcome": None, "research_called": False, "negative_written": False}

    def _disp(*a, **k) -> dict:
        try:
            return hr_display(*a, **k)
        except Exception:   # noqa: BLE001  表示専用キーの生成失敗は表示なし(従来表示)へ
            return {}

    if act == ACTION_USE_LEDGER:
        out["info"] = dict(d["entry"])
        out["extra"] = _disp(out["info"], action=act, lookup_meta=d["meta"])
        return out
    if act == ACTION_SKIP_ISOLATED:
        out["extra"] = _disp(None, action=act, lookup_meta=d["meta"], general_word=bool(d.get("general_word")))
        return out
    if act == ACTION_SKIP_GENERAL:
        out["extra"] = _disp(None, action=act, lookup_meta=d["meta"])
        return out
    if act == ACTION_SKIP_NEGATIVE:
        out["extra"] = _disp(None, action=act, lookup_meta=d["meta"], negative=d.get("negative"))
        return out
    # RESEARCH(従来どおり1回だけ)
    exc, research = None, None
    out["research_called"] = True
    try:
        research = research_fn(span)
    except transient_exceptions as ex:
        exc = ex
    outcome = classify_research_outcome(research, exc)
    out["outcome"] = outcome
    if outcome == OUTCOME_TRANSIENT:
        out["extra"] = _disp(None, action=act)
        return out                       # 何も保存しない(一時失敗を否定記録にしない)
    if outcome == OUTCOME_NOT_FOUND:
        rec = build_negative_record(span, outcome, now=now)
        try:
            if neg_store is not None and neg_store.put(rec):
                out["negative_written"] = True
        except Exception:   # noqa: BLE001  否定記録の保存失敗=記録なし(次回また調査するだけ。従来動作)
            out["negative_written"] = False
        out["extra"] = _disp(None, action=act, negative=rec if out["negative_written"] else None)
        return out
    item = dict(research["items"][0])
    item["sources"] = research.get("citations", [])
    verification = None
    if fetch is not None:
        try:
            verification = verify_citations(item, fetch, url_ok=url_ok)
            item["evidence_tier"] = verification["tier"]
            item["evidence_check"] = {"tier": verification["tier"], "checked": verification["checked"], "at": _fmt(now)}
        except Exception:   # noqa: BLE001  照合の失敗は照合なしで従来どおり登録
            verification = None
            item.pop("evidence_tier", None)
            item.pop("evidence_check", None)
    saved = upsert_fn(span, item)
    if (saved or {}).get("ledger_disabled"):
        out["extra"] = _disp(None, action=act)      # 隔離entryは従来どおりHRへ誤情報を載せない
        return out
    out["info"] = dict(saved) if saved else None
    out["extra"] = _disp(out["info"], action=act, verification=verification)
    return out


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(65536), b""):
            h.update(b)
    return h.hexdigest()
