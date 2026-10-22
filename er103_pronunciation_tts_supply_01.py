# -*- coding: utf-8 -*-
"""固有名詞の発音情報をTTS入力へ供給する(綴り置換)純関数群(未配線module。Production .pyは本fileをimportしない)。

管理: PROPER-NOUN-PRONUNCIATION-ALARM-POLICY-PRODUCTION-01 委任_01。ユーザー承認(2026-10-22 `APPROVED_FOR_PRODUCTION`)①:
  Stage 2 Trialで検証した「綴り置換(Reicher->Riker方式)」を、Pronunciation Ledgerの根拠階層から供給する。
    A階層(公式・信頼できる出典で引用実在確認済み)=自動供給 / B階層(媒体由来)=人間承認済み(Ledger `human_approved`=True)の語のみ供給 /
    ESTIMATED(AI推定のみ・出典未検証・取得なし)=**供給しない**。
  既存機構の活用: 置換はer003_v1_n3_01_tts_generate._EN_NAME_PRONUNCIATION_OVERRIDES(静的辞書{"Reicher":"Riker"})と同じ思想。
  Family A/B/C共有のer003_v1_n3_01_tts_generate.pyは**編集しない**(27-7)。X/Zのtext整形点(`tts_safe_news_en`の直後)に本moduleの
  `apply_supply`を1回挟む(配線はIMPLEMENTATION_DESIGN_01 §5)。静的辞書の語(Reicher)は二重適用しない。

重要な限界(Stage 2 Trial実測): 誤った発音を供給するとASR比較対象(置換後テキスト)も誤りで固定され、誤りを検出できない
(Meink->Minkで実証)。安全性は供給元の正しさに全面依存するため、A/B階層ゲート・respelling機械検査・複数entry衝突時の不供給を課す。
置換が効かない語(Meink/Altuzarra型)も存在する。供給して不一致が残る場合はアラームの`tts_supply_result`に記録される。
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Callable, Optional
from urllib.parse import urlparse

POLICY_ID = "PROPER-NOUN-PRONUNCIATION-ALARM-POLICY-PRODUCTION-01"

# er097_pronunciation_supply_stage1_01の階層ラベルと同値(文字列で参照、importしない=未配線moduleを独立に保つ)
TIER_QUOTE_VERIFIED = "QUOTE_VERIFIED"
TIER_PRON_IN_PAGE = "PRON_IN_CITED_PAGE"

# A階層(公式・信頼できる根拠)と認める出典ホストの規則。**暫定値**(Opusレビュー対象): 参照辞書・百科、または出典ホストが固有名詞の
# surfaceを含む(ブランド/本人の公式サイト)。媒体(nylon.com等)はここに含めない=B階層。
REFERENCE_HOST_SUFFIXES = ("wikipedia.org", "wikimedia.org", "merriam-webster.com", "oxfordlearnersdictionaries.com",
                           "dictionary.cambridge.org", "collinsdictionary.com", "britannica.com", "ldoceonline.com")
MAX_RESPELLING_WORDS = 3

SUPPLY_OK = "SUPPLIED"
R_NO_ENTRY = "NO_LEDGER_ENTRY"
R_DISABLED = "LEDGER_OR_TTS_INJECTION_DISABLED"
R_EXCLUDED_TYPE = "EXCLUDED_ENTITY_TYPE"
R_UNVERIFIED = "EVIDENCE_NOT_VERIFIED_ESTIMATED"
R_B_NOT_APPROVED = "B_TIER_NOT_HUMAN_APPROVED"
R_NO_RESPELLING = "NO_USABLE_RESPELLING"
R_CONFLICT = "CONFLICTING_ENTRIES"
R_ALREADY_STATIC = "HANDLED_BY_STATIC_OVERRIDE"
R_DISABLED_FLAG = "SUPPLY_DISABLED"

# 単独フラグ(ユーザー承認により委任_02で既定True。run scope外は恒等)。読取は is_enabled() のみ
TTS_SUPPLY_ENABLED = True


def is_enabled() -> bool:
    return TTS_SUPPLY_ENABLED is True


def _fold(s: str) -> str:
    t = unicodedata.normalize("NFKD", s or "")
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", t.strip().lower())


def _default_cmu_has(token: str) -> bool:
    import pronouncing
    return bool(pronouncing.phones_for_word(token.lower().strip("'")))


def source_hosts(entry: dict) -> list:
    out = []
    for u in entry.get("sources") or []:
        if isinstance(u, str):
            h = (urlparse(u).hostname or "").lower()
            if h:
                out.append(h)
    return out


def _is_official_host(host: str, surface: str) -> bool:
    """参照辞書/百科のホスト、またはホストの**ラベル単位**がsurface名と一致する公式ホスト(OF-PNAP-P-07: 部分文字列一致は不可。
    例 khaite.com / www.khaite.com / shop.khaite.com は可、khaite-fan-blog.example / notkhaite.com は不可)。"""
    if any(host == suf or host.endswith("." + suf) for suf in REFERENCE_HOST_SUFFIXES):
        return True
    slug = re.sub(r"[^a-z0-9]", "", _fold(surface))
    return len(slug) >= 4 and any(re.sub(r"[^a-z0-9]", "", lab) == slug for lab in host.split("."))


def _word_in(text: str, phrase: str) -> bool:
    t, ph = _fold(text), _fold(phrase)
    return bool(ph) and re.search(r"(?<![a-z0-9])" + re.escape(ph) + r"(?![a-z0-9])", t) is not None


def respelling_consistent_with_verified_quote(entry: dict, respelling: Optional[str]) -> bool:
    """OF-PNAP-P-07: A階層の自動供給は『人が登録したtts_respelling』または『hint由来のrespellingが、出典ホスト条件を満たす引用
    (evidence[].quote)の中に語として現れる(=検証済み引用のIPA/respellingと整合)』場合に限る。引用の無い・整合しないhintは自動供給しない。"""
    if (entry.get("tts_respelling") or "").strip():
        return True
    if not respelling:
        return False
    surface = entry.get("surface", "")
    for ev in entry.get("evidence") or []:
        if not isinstance(ev, dict) or not ev.get("quote") or not ev.get("url"):
            continue
        host = (urlparse(ev["url"]).hostname or "").lower()
        if host and _is_official_host(host, surface) and _word_in(ev["quote"], respelling):
            return True
    return False


def classify_supply_tier(entry: dict, *, cmu_has: Callable = _default_cmu_has) -> tuple:
    """Ledger entry -> (tier|None, reason)。tier: "A"|"B"。
      A: evidence_tier==QUOTE_VERIFIED(出典ページに引用文が実在) ∧ 出典ホストの1つが参照辞書/百科またはsurface名を含む公式ホスト
      B: evidence_tier∈{QUOTE_VERIFIED, PRON_IN_CITED_PAGE}(媒体由来) または human_approved=True
         -> **human_approved=Trueの場合のみ供給**(plan_supplyで検査)
      None(供給しない=ESTIMATED): UNVERIFIED_AI_OUTPUT / NAME_IN_CITED_PAGE / NO_SOURCE / 出典なし / evidence_tier未保存"""
    et = entry.get("evidence_tier")
    approved = bool(entry.get("human_approved"))
    if et == TIER_QUOTE_VERIFIED and any(_is_official_host(h, entry.get("surface", "")) for h in source_hosts(entry)):
        if respelling_consistent_with_verified_quote(entry, derive_respelling(entry, cmu_has=cmu_has)):
            return "A", "official_or_reference_host_quote_verified_consistent"
        if not approved:
            return "B", "official_host_but_respelling_not_consistent_with_quote"
    if approved:
        return "B", "human_approved"
    if et in (TIER_QUOTE_VERIFIED, TIER_PRON_IN_PAGE):
        return "B", f"media_{et}_not_approved"
    return None, R_UNVERIFIED


def derive_respelling(entry: dict, *, cmu_has: Callable = _default_cmu_has) -> Optional[str]:
    """TTSが綴りに追従して正しく読める『一般語の綴り』を返す。無ければNone(供給しない)。
    1) 人が承認・登録した`tts_respelling`(Ledger追加キー、配線時に追加)を最優先。
    2) 無ければ`pronunciation_hint`の機械変換: 小文字化し、全tokenがCMU収録語(空白区切り、ハイフン音節表記は不可)かつ
       <=MAX_RESPELLING_WORDS語・数字なしの場合のみ採用(例 'kate'->'Kate')。音節表記('al-tuh-ZAIR-ah')や非語('KAYT')は不採用
       =Stage 2 Trialでも音節表記は制御不能だった。
    surface自身と同一のときは不採用(置換の意味がない)。"""
    surface = entry.get("surface", "")
    rs = (entry.get("tts_respelling") or "").strip()
    if rs:
        cand = rs
    else:
        hint = (entry.get("pronunciation_hint") or "").strip()
        if not hint or "-" in hint or re.search(r"\d", hint):
            return None
        toks = hint.lower().split()
        if not toks or len(toks) > MAX_RESPELLING_WORDS or not all(re.fullmatch(r"[a-z]+", t) and cmu_has(t) for t in toks):
            return None
        cand = " ".join(toks)
    cand = " ".join(w[:1].upper() + w[1:] for w in cand.split())
    if _fold(cand) == _fold(surface):
        return None
    if len(cand.split()) > MAX_RESPELLING_WORDS or re.search(r"[^A-Za-z' ]", cand):
        return None
    return cand


@dataclass
class SupplyDecision:
    surface: str
    supplied: bool
    reason: str
    tier: Optional[str] = None
    respelling: Optional[str] = None
    ledger_id: Optional[str] = None
    evidence_tier: Optional[str] = None
    source_urls: list = field(default_factory=list)
    human_approved: bool = False

    def to_audit(self) -> dict:
        return {"supplied": self.supplied, "reason": self.reason, "tier": self.tier, "original": self.surface,
                "respelling": self.respelling, "ledger_id": self.ledger_id, "evidence_tier": self.evidence_tier,
                "human_approved": self.human_approved, "source_urls": self.source_urls[:3], "policy_id": POLICY_ID}


def _surface_pattern(surface: str):
    """OF-PNAP-P-06: 置換は**大文字小文字を区別**する。Ledger surfaceが全小文字なら(固有名詞の小文字登録)大文字小文字無視、
    それ以外(Khaite等)は登録どおりの綴りのみ。"""
    flags = re.IGNORECASE if surface == surface.lower() else 0
    return re.compile(r"(?<![A-Za-z0-9])" + re.escape(surface) + r"(?![A-Za-z0-9])", flags=flags)


def _is_general_lower(surface: str, *, cmu_has: Callable = _default_cmu_has, zipf: Optional[Callable] = None) -> bool:
    """surfaceの小文字形が通常語彙(CMU収録∧zipf>=4.0)か(Nice/Muse/Gap等)。"""
    if zipf is None:
        from wordfreq import zipf_frequency
        zipf = lambda w: zipf_frequency(w, "en")   # noqa: E731
    toks = [t for t in re.findall(r"[a-z']+", _fold(surface))]
    return bool(toks) and all(cmu_has(t) and zipf(t) >= 4.0 for t in toks)


def _sentence_initial(text: str, start: int) -> bool:
    before = text[:start].rstrip()
    if before == "":
        return True
    if re.search(r"[:;\"'\u201c\u2018(\[\u2014]$", before):
        return True
    return bool(re.search(r"[.!?]['\")\]]*$", before) and not re.search(r"(?<![A-Za-z])[A-Z]\.$", before))


def plan_supply(text: str, ledger: dict, *, static_overrides: Optional[dict] = None, enabled: Optional[bool] = None,
                cmu_has: Callable = _default_cmu_has, excluded_entity_types=frozenset({"ja_reading_katakana"})) -> list:
    """textに現れるLedger登録surfaceごとの供給判断を返す(監査用に非供給の理由も全て返す)。純関数、API 0、Ledgerは引数で受ける。
    同一surface(fold一致)に複数entryがあり、供給可能なrespellingが食い違う場合は不供給(R_CONFLICT)。"""
    if enabled is None:
        enabled = is_enabled()
    static_overrides = static_overrides or {}
    by_surface: dict = {}
    for lid, e in (ledger or {}).items():
        sf = e.get("surface") or ""
        if not sf.strip() or not _surface_pattern(sf).search(text):
            continue
        by_surface.setdefault(_fold(sf), []).append((lid, e))
    out = []
    for key, items in by_surface.items():
        surface = items[0][1]["surface"]
        if not enabled:
            out.append(SupplyDecision(surface, False, R_DISABLED_FLAG))
            continue
        if any(_fold(k) == key for k in static_overrides):
            out.append(SupplyDecision(surface, False, R_ALREADY_STATIC))
            continue
        cands = []
        last_reason = R_NO_ENTRY
        for lid, e in items:
            if e.get("entity_type") in excluded_entity_types:
                last_reason = R_EXCLUDED_TYPE
                continue
            if e.get("ledger_disabled") or e.get("tts_injection_disabled"):
                last_reason = R_DISABLED
                continue
            tier, why = classify_supply_tier(e, cmu_has=cmu_has)
            if tier is None:
                last_reason = why
                continue
            if tier == "B" and not e.get("human_approved"):
                last_reason = R_B_NOT_APPROVED
                continue
            rs = derive_respelling(e, cmu_has=cmu_has)
            if rs is None:
                last_reason = R_NO_RESPELLING
                continue
            cands.append(SupplyDecision(e.get("surface", surface), True, SUPPLY_OK, tier=tier, respelling=rs, ledger_id=lid,
                                        evidence_tier=e.get("evidence_tier"),
                                        source_urls=[u for u in (e.get("sources") or []) if isinstance(u, str)],
                                        human_approved=bool(e.get("human_approved"))))
        if not cands:
            out.append(SupplyDecision(surface, False, last_reason))
        elif len({_fold(c.respelling) for c in cands}) > 1:
            out.append(SupplyDecision(surface, False, R_CONFLICT))
        else:
            out.append(sorted(cands, key=lambda c: (c.tier != "A", c.ledger_id or ""))[0])
    return out


def apply_supply(text: str, decisions: list) -> tuple:
    """供給すると決まった語だけ、surfaceをrespellingへ置換する(語境界・大文字小文字無視。所有格's等はそのまま残る)。
    戻り値=(置換後text, supply_map{置換後token小文字: 元surface小文字})。supply_mapはevaluate_alarm_eligibilityへ渡す。"""
    out = text
    smap: dict = {}
    for d in decisions:
        if not d.supplied:
            continue
        pat = _surface_pattern(d.surface)
        if _is_general_lower(d.surface) and d.surface[:1].isupper():
            # OF-PNAP-P-06: 小文字形が一般語(Nice/Muse/Gap)の場合、大文字始まりの**文中**出現のみ置換(文頭・引用直後は一般語の可能性が高い)
            out = pat.sub(lambda m, _r=d.respelling, _t=out: m.group(0) if _sentence_initial(_t, m.start()) else _r, out)
        else:
            out = pat.sub(d.respelling, out)
        for t in d.respelling.split():
            smap[t.lower()] = d.surface.lower()
    return out, smap


# ---------------------------------------------------------------- 供給結果の受け渡し(runner -> adapter)
# adapter(er006 evaluate_attempt_with_cascade_detail)はleaf関数が組み立てたattempt_ctxしか受け取れず、runnerが決めた供給情報を直接渡せない。
# そこでrunnerが`apply_supply`直後に「置換後text(=ASR比較のcanonical_text)」をキーにprocess内registryへ登録し、adapterがcanonical_textで引く。
# 局所書換え(LR)等でtextが変わった場合は一致しない=supply情報なし(fail-closed: 供給語はアラーム受理されずHR側へ)。
_REGISTRY: dict = {}


def register_supply(tts_text: str, decisions: list, supply_map: dict, *, pre_supply_text: Optional[str] = None, error: Optional[str] = None) -> None:
    _REGISTRY[tts_text] = {"supply_map": dict(supply_map or {}), "decisions": [d.to_audit() for d in decisions],
                           "tts_input_text": tts_text, "pre_supply_text": pre_supply_text, "error": error}


def lookup_supply(canonical_text: str) -> dict:
    return _REGISTRY.get(canonical_text) or {"supply_map": {}, "decisions": []}


def clear_registry() -> None:
    _REGISTRY.clear()


def applied_supplies() -> list:
    """このprocess(=run)で登録された供給判断のうち、実際に供給した語(静的辞書含む)を重複なしで返す。完成報告の『発音供給の適用一覧』用。"""
    seen, out = set(), []
    for v in _REGISTRY.values():
        for d in v.get("decisions") or []:
            if d.get("supplied"):
                k = (d.get("original"), d.get("respelling"), d.get("tier"))
                if k not in seen:
                    seen.add(k)
                    out.append(d)
    return out


def supply_info_for(noun_surface: str, lookup: dict) -> dict:
    """アラームrecordの`tts_supply_result`: 当該固有名詞に対するTTS発音改善の試行結果(供給した/しなかった+理由)。"""
    key = _fold(noun_surface)
    for d in lookup.get("decisions") or []:
        if _fold(d.get("original", "")) == key:
            return d
    return {"supplied": False, "reason": "no_ledger_entry_or_not_planned", "original": noun_surface}


def supply_list_from_lookup(lookup: dict) -> list:
    """完成報告の『発音供給の適用一覧』用: 供給した語(静的辞書含む)のみ。"""
    return [d for d in (lookup.get("decisions") or []) if d.get("supplied")]


# ---------------------------------------------------------------- X/Z共通の入口(配線点5-4)。共有er003 TTS生成関数は編集しない
def static_decisions(original_text: str, static_overrides: Optional[dict]) -> list:
    """既存の静的辞書(例 Reicher->Riker)で**既に**置換済みの語を、供給記録(SupplyDecision tier="S")として登録する(OF-PNAP-P-11)。
    置換自体は共有`tts_safe_*`が済ませているので本moduleは再適用しない(二重適用防止)。ここでは監査・supply_map(アラーム判定の固有名詞扱い)用。"""
    out = []
    for k, v in (static_overrides or {}).items():
        if re.search(r"(?<![A-Za-z0-9])" + re.escape(k) + r"(?![A-Za-z0-9])", original_text or "", flags=re.IGNORECASE):
            out.append(SupplyDecision(k, True, "STATIC_OVERRIDE", tier="S", respelling=v, ledger_id="static:er003_EN_NAME_PRONUNCIATION_OVERRIDES",
                                      evidence_tier="STATIC_DICT"))
    return out


def supply_for_tts(original_text: str, shaped_text: str, *, ledger: Optional[dict] = None, static_overrides: Optional[dict] = None,
                   enabled: Optional[bool] = None, cmu_has: Callable = _default_cmu_has) -> str:
    """X/Zのtext整形点(`tts_safe_news_en`等)の**直後**に1回呼ぶ。戻り値=TTS入力text(供給なし/無効時は`shaped_text`をそのまま返す=恒等)。
    有効条件: TTS_SUPPLY_ENABLED ∧ run scope∈{X,Z}(アラーム方針moduleのscope。A/B/C・単体は恒等)。
    ASR比較のcanonical(=戻り値)と供給判断を`register_supply`で登録し、adapterがcanonical_textで引く。例外は呼出側へ伝播させない
    (供給は補助機能: 失敗時は恒等+registryへ失敗理由を残す)。"""
    if enabled is None:
        try:
            import er103_proper_noun_alarm_policy_01 as _pol
            enabled = is_enabled() and _pol.current_scope() in _pol.APPROVED_SCOPES
        except Exception:
            enabled = False
    if not enabled:
        return shaped_text
    try:
        if ledger is None:
            import er006_pronunciation_ledger_01 as _pl
            ledger = _pl._load()
        decs = plan_supply(shaped_text, ledger, static_overrides=static_overrides, enabled=True, cmu_has=cmu_has)
        out, smap = apply_supply(shaped_text, decs)
        sdec = static_decisions(original_text, static_overrides)
        for d in sdec:
            smap[d.respelling.lower()] = d.surface.lower()
        register_supply(out, [*sdec, *decs], smap, pre_supply_text=shaped_text)
        return out
    except Exception as exc:  # noqa: BLE001  供給は補助。失敗は恒等(従来動作)
        register_supply(shaped_text, [], {}, error=f"{type(exc).__name__}: {exc}")
        return shaped_text
