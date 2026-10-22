# -*- coding: utf-8 -*-
"""固有名詞ASR発音不一致の「アラーム受理」判定とアラーム記録(未配線module。Production .pyは本fileをimportしない)。

管理: PROPER-NOUN-PRONUNCIATION-ALARM-POLICY-PRODUCTION-01 委任_01。ユーザー承認(2026-10-22 `APPROVED_FOR_PRODUCTION`):
  固有名詞の発音不一致**だけ**が原因のNG/Human Reviewを、アラーム記録のみで受理(制作を止めない・HRに回さない)。
設計=docs/research/PROPER-NOUN-PRONUNCIATION-ALARM-POLICY-PRODUCTION-01/IMPLEMENTATION_DESIGN_01.md。

位置づけ(設計§3): 統一judge(er078)が NG_BOTH / secondary_not_accepted で返した**後**、adapter
(er006_secondary_asr_01.evaluate_attempt_with_cascade_detail)から呼ぶ最終救済。Tier3/CMU Case A/homophone/M1/CS Equivalence/
Secondary許容集合の**全て**を通ってもNGだった場合のみ到達する(既存救済が先、解決すればそちら優先)。追加API呼出は0。

承認範囲(厳守): 緩和するのは「固有名詞の発音不一致だけ」。次は従来どおり(本moduleは受理しない=fail-closed):
  KPフレーズ(dual_required/KEY_PHRASE role)、HEADING_READOUT、日本語、一般語・内容語の差、数値/否定の差、語の脱落/追加、
  音声欠落(TTS_FAILURE)、Secondary障害(NG_SECONDARY_UNAVAILABLE=技術STOP)、除外表(NG_EXCLUDED)。

純関数のみ(I/Oは`append_alarm_log`/`write_run_alarms`の引数pathに限る)。依存はProduction判定器のimport(読取のみ)。
"""
from __future__ import annotations

import difflib
import hashlib
import json
import os
import re
import time
import unicodedata
from dataclasses import dataclass, field
from typing import Callable, Optional

POLICY_ID = "PROPER-NOUN-PRONUNCIATION-ALARM-POLICY-PRODUCTION-01"

# ---- 単一flag(読取は is_enabled() のみ)。未配線の間は False。配線委任でTrue(ユーザー承認済み仕様のため)。 ----
PROPER_NOUN_ALARM_POLICY_ENABLED = False


def is_enabled() -> bool:
    return PROPER_NOUN_ALARM_POLICY_ENABLED is True


# ---- run scope(承認範囲=Family X/Z。A/B/C・単体呼出は scope 未設定のため完全に従来どおり) ----
# X runner / Z runner の main 冒頭で enter_scope("X"|"Z") を1回呼ぶ(既存 secondary_run_scope と同型のprocess内状態)。
APPROVED_SCOPES = frozenset({"X", "Z"})
_RUN_SCOPE: Optional[str] = None


def enter_scope(family: str) -> None:
    global _RUN_SCOPE
    if family not in APPROVED_SCOPES:
        raise ValueError(f"unsupported scope: {family!r} (approved: {sorted(APPROVED_SCOPES)})")
    _RUN_SCOPE = family


def leave_scope() -> None:
    global _RUN_SCOPE
    _RUN_SCOPE = None


def current_scope() -> Optional[str]:
    return _RUN_SCOPE


def is_active_for_run() -> bool:
    """adapterが参照する唯一の読取関数: flag有効 かつ X/Z runner scope内。"""
    return is_enabled() and _RUN_SCOPE in APPROVED_SCOPES


# ---- 状態名・理由コード ----
STATE_ALARM = "PASS_WITH_PRONUNCIATION_ALARM"      # asr_judgement.state の新区分(PASS_WITH_WARNINGとは別。事後試聴リストに載せない)
FINAL_STATE_JA = "アラーム付き完成"
JUDGE_REASON_ELIGIBLE = "secondary_not_accepted"   # 統一judgeが NG_BOTH で返す理由のうち、アラーム受理の入口になるもの(唯一)
JUDGE_STATE_ELIGIBLE = "NG_BOTH"

# 適用するrole(= Tier3/EN意味等価と同じ「英語ナレーション5 role」。Zの対話clipはFULL_STORYに解決される)。
APPLICABLE_ROLES = frozenset({"FULL_STORY", "COMMENT", "PREVIEW", "TOPIC_INTRO", "IN_ONE_LINE"})

# ---- 受理境界のパラメータ(校正値は IMPLEMENTATION_DESIGN_01 §2-4。変更はFable/Opusレビュー対象) ----
MAX_DIFFS_PER_SEGMENT = 3          # 1 segmentで受理する固有名詞差分の最大数(超過は「文が大きく違う」疑いとしてfail-closed)
MAX_ASR_TOKENS_PER_CANON_TOKEN = 2  # canonical固有名詞1語に対し、ASR側に出てよい語数(Alta Zara=2は可、Mellow Strength型は類似度で除外)
MIN_SPAN_SIMILARITY = 0.40         # despaced綴りの類似度(difflib ratio)下限。Melos->"Mellow Strength"型(別語句の聞き取り)を除く
GENERAL_WORD_MIN_ZIPF = 4.0        # er097.GENERAL_WORD_MIN_ZIPFと同値。CMU収録かつzipf>=これの語は「一般語」扱い=受理しない
_ENTITY_SOURCES_OK = frozenset({"capitalized", "loanword", "ledger"})
_SENT_END_RE = re.compile(r"[.!?]['\")\]]*\s+")

# 不受理理由コード(監査・test用)
R_DISABLED = "DISABLED"
R_LANG = "NOT_EN"
R_ROLE = "ROLE_NOT_APPLICABLE"
R_DUAL = "DUAL_REQUIRED_KP"
R_JUDGE_STATE = "JUDGE_STATE_NOT_ELIGIBLE"
R_PRIMARY_NOT_ENTITY_ONLY = "PRIMARY_NOT_ENTITY_ONLY"
R_SECONDARY_MISSING = "SECONDARY_TEXT_MISSING"
R_SECONDARY_NOT_ENTITY_ONLY = "SECONDARY_NOT_ENTITY_ONLY"
R_NO_DIFF = "NO_ENTITY_DIFF"
R_TOO_MANY_DIFFS = "TOO_MANY_DIFFS"
R_DELETION = "WORD_DELETION_OR_NO_ASR_TOKEN"
R_GENERAL_WORD = "CANONICAL_TOKEN_IS_GENERAL_WORD"
R_NOT_PROPER_EVIDENCE = "NO_PROPER_NOUN_EVIDENCE"
R_ASR_TOO_LONG = "ASR_SPAN_TOO_LONG"
R_LOW_SIMILARITY = "LOW_SPAN_SIMILARITY"
R_ASR_HAS_NUMBER_OR_NEG = "ASR_SPAN_HAS_NUMBER_OR_NEGATION"


# ---------------------------------------------------------------- 小道具
def _fold(s: str) -> str:
    t = unicodedata.normalize("NFKD", s or "")
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", t.strip().lower())


def _despaced(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", _fold(s))


def span_similarity(canonical_span: str, asr_span: str) -> float:
    return round(difflib.SequenceMatcher(None, _despaced(canonical_span), _despaced(asr_span)).ratio(), 4)


def _default_cmu_has(token: str) -> bool:
    import pronouncing
    return bool(pronouncing.phones_for_word(token.lower().strip("'")))


def _default_zipf(token: str) -> float:
    from wordfreq import zipf_frequency
    return zipf_frequency(token, "en")


def is_general_word(token: str, *, cmu_has: Callable = _default_cmu_has, zipf: Callable = _default_zipf,
                    min_zipf: float = GENERAL_WORD_MIN_ZIPF) -> bool:
    """CMU収録かつzipf>=min_zipf = 通常の英語語彙(er097.is_general_word_spanと同定義)。"""
    t = _fold(token).strip("'")
    return bool(t) and cmu_has(t) and zipf(t) >= min_zipf


def proper_noun_evidence(token: str, canonical_text: str, *, ledger_surfaces: frozenset = frozenset(),
                         cmu_has: Callable = _default_cmu_has) -> tuple[bool, str]:
    """canonical側tokenが「固有名詞らしい」根拠を持つか。戻り値=(bool, 根拠ラベル)。
    根拠(いずれか): (1) Ledger登録surface(語単位) (2) CMU未収録語(造語・外来語・ブランド名) (3) 文中(文頭でない位置)の大文字始まり
    (4) 周囲がALLCAPSでない単独のALLCAPS語(ELLE等)。
    文頭の大文字だけ(CMU収録語)は根拠にしない("Retail sales fell"のRetailを固有名詞扱いしない)。"""
    t = _fold(token)
    if t in ledger_surfaces:
        return True, "ledger"
    if not cmu_has(t):
        return True, "cmu_oov"
    words = [m for m in re.finditer(r"[^\W\d_]+", canonical_text, flags=re.UNICODE)]
    for k, m in enumerate(words):
        w = m.group(0)
        if _fold(w) != t or not w[:1].isupper():
            continue
        if len(w) >= 2 and w.isupper():
            # ALLCAPS語(ELLE/MTA等)。周囲の語がALLCAPSでなければ(見出し全体の大文字化でなければ)ブランド/略語として根拠にする
            nb = [words[j].group(0) for j in (k - 1, k + 1) if 0 <= j < len(words)]
            if not any(x.isupper() and len(x) >= 2 for x in nb):
                return True, "allcaps"
        before = canonical_text[:m.start()].rstrip()
        if before == "" or (re.search(r"[.!?]['\")\]]*$", before) and not re.search(r"(?<![A-Za-z])[A-Z]\.$", before)):
            continue  # 文頭(「L. Mimoun」のイニシャル+ピリオドは文末とみなさない)
        return True, "capitalized_midsentence"
    return False, "none"


# ---------------------------------------------------------------- 判定結果
@dataclass
class AlarmDiff:
    canonical: str
    asr_primary: str
    asr_secondary: str
    evidence: str
    similarity_primary: float
    similarity_secondary: float


@dataclass
class AlarmDecision:
    accept: bool
    reason: str                       # 受理: "ENTITY_ONLY_ACCEPT" / 不受理: R_*
    diffs: list = field(default_factory=list)
    detail: dict = field(default_factory=dict)


def _span_has_number_or_negation(span: str) -> bool:
    import er006_preprod_hardening_01_validation as val
    return any(val._is_number(t) or t in val._NEGATION_WORDS for t in val.tokenize(span))


def _same_or_plural(a: str, b: str) -> bool:
    a, b = a.lower(), b.lower()
    return a == b or a + "s" == b or b + "s" == a or a + "es" == b or b + "es" == a


def _noun_checks(canon: str, asr: str, canonical_text: str, *, ledger_surfaces, cmu_has, zipf, max_asr_per_canon, min_similarity,
                 supply_map=None):
    """1つのPrimary diff(canonical語句 -> ASR語句)がアラーム受理境界内か。戻り値=(None, evidence_label, similarity) | (不受理理由, detail, None)。"""
    if not canon or not asr:
        return R_DELETION, {"canonical": canon, "asr": asr}, None
    c_tokens = canon.split()
    evs = []
    supply_map = supply_map or {}
    supplied = [t for t in c_tokens if t in supply_map]
    if supplied:
        # TTS発音供給で綴り置換済みの語(例 Khaite->Kate)。置換後の語(Kate)は一般語に見えるが、元は固有名詞(供給根拠はLedger階層で別途監査済み)。
        # 固有名詞根拠=supplied_respelling。類似度は置換後綴り/元綴りのうち近い方で見る(ASRは原綴りを書くことがある)。
        if _span_has_number_or_negation(asr):
            return R_ASR_HAS_NUMBER_OR_NEG, {"asr": asr}, None
        if len(asr.split()) > len(c_tokens) * max_asr_per_canon:
            return R_ASR_TOO_LONG, {"canonical": canon, "asr": asr}, None
        orig = " ".join(supply_map.get(t, t) for t in c_tokens)
        sim = max(span_similarity(canon, asr), span_similarity(orig, asr))
        if sim < min_similarity:
            return R_LOW_SIMILARITY, {"canonical": canon, "asr": asr, "similarity": sim}, None
        return None, "supplied_respelling", sim
    if all(is_general_word(tk, cmu_has=cmu_has, zipf=zipf) for tk in c_tokens):
        # 句の全tokenが通常の英語語彙(例: "mini")なら一般語の誤読とみなし受理しない。"Stephen Reicher"のように一部が人名でも
        # 他のtokenが語彙外(Reicher)なら固有名詞句として扱う(er097.is_general_word_spanと同じ「全token」基準)。
        return R_GENERAL_WORD, {"tokens": c_tokens}, None
    for tk in c_tokens:
        ok, ev = proper_noun_evidence(tk, canonical_text, ledger_surfaces=ledger_surfaces, cmu_has=cmu_has)
        if not ok:
            return R_NOT_PROPER_EVIDENCE, {"token": tk}, None
        evs.append(ev)
    if _span_has_number_or_negation(asr):
        return R_ASR_HAS_NUMBER_OR_NEG, {"asr": asr}, None
    if len(asr.split()) > len(c_tokens) * max_asr_per_canon:
        return R_ASR_TOO_LONG, {"canonical": canon, "asr": asr}, None
    sim = span_similarity(canon, asr)
    if sim < min_similarity:
        return R_LOW_SIMILARITY, {"canonical": canon, "asr": asr, "similarity": sim}, None
    return None, "+".join(sorted(set(evs))), sim


def evaluate_alarm_eligibility(
        *, canonical_text: str, primary_cls, secondary_cls, primary_text: Optional[str], secondary_text: Optional[str],
        judge_state: str, judge_reason_code: str, role: Optional[str], lang: str = "en", dual_required: bool = False,
        enabled: Optional[bool] = None, ledger_surfaces: frozenset = frozenset(),
        cmu_has: Callable = _default_cmu_has, zipf: Callable = _default_zipf,
        max_diffs: int = MAX_DIFFS_PER_SEGMENT, max_asr_per_canon: int = MAX_ASR_TOKENS_PER_CANON_TOKEN,
        min_similarity: float = MIN_SPAN_SIMILARITY, supply_map: Optional[dict] = None) -> AlarmDecision:
    """固有名詞の発音不一致**だけ**が原因でNGになったかを機械判定する(純関数、API 0、fail-closed)。

    受理条件(全て満たす場合のみ accept=True):
      G0  flag有効 / 言語=en / role∈APPLICABLE_ROLES / dual_required=False(KP英語phrase両方PASS条件は維持)
      G1  統一judgeが NG_BOTH ∧ reason=secondary_not_accepted(既存の全救済層を通過後。この時点で両転写の値ガード/否定ガードはPASS済み)
      G2  Primary(OpenAI ASR=production authority)分類=ASR_VALIDATION_UNCERTAIN ∧ 全diffがentity_like
          (= 数値/否定差なし・非固有名詞の内容語差なし・TTS_FAILUREでない・語の追加のみの差なし)
      G3  Secondary(Azure)転写あり。Secondary側のdiffは次のとおり扱う:
            - Primaryも同じcanonical語句で差がある位置 -> その語句がentity_like(または同じ固有名詞+所有格's)であること(=両engineが同じ固有名詞で不一致)
            - Primaryがcanonicalと一致している位置のSecondary-only diff(Azure固有の表記揺れ/聞き落とし) -> 受理判断から除外し`secondary_only_noise`として記録
              (Primary PASSの音声でSecondaryは参照されない既存設計と整合。Secondaryのみの内容語差で止めない)
      G4  Primaryのdiff総数 <= max_diffs
      G5  各Primary diffについて: 置換(canonical語・ASR語とも非空=語の脱落でない) ∧ canonical全tokenが固有名詞根拠あり(proper_noun_evidence)
          ∧ 一般語(CMU∧zipf>=4.0)でない ∧ ASR語数<=canonical語数*max_asr_per_canon ∧ ASR側に数値/否定語なし
          ∧ despaced綴り類似度>=min_similarity(別語句への聞き取り替わり["Melos"->"Mellow Strength"]を除く)
    アラーム対象の固有名詞 = G5を満たしたPrimary diffのcanonical語句。
    supply_map: TTS発音供給で綴り置換した語の {置換後token(小文字): 元の固有名詞surface}。置換後tokenを固有名詞として扱う(G5の一般語/根拠検査を置換)。
    """
    if enabled is None:
        enabled = is_active_for_run()
    if not enabled:
        return AlarmDecision(False, R_DISABLED)
    if str(lang).lower() not in ("en", "en-us"):
        return AlarmDecision(False, R_LANG)
    if dual_required:
        return AlarmDecision(False, R_DUAL)
    if role not in APPLICABLE_ROLES:
        return AlarmDecision(False, R_ROLE, detail={"role": role})
    if judge_state != JUDGE_STATE_ELIGIBLE or judge_reason_code != JUDGE_REASON_ELIGIBLE:
        return AlarmDecision(False, R_JUDGE_STATE, detail={"judge_state": judge_state, "reason_code": judge_reason_code})
    if not secondary_text or secondary_cls is None:
        return AlarmDecision(False, R_SECONDARY_MISSING)
    if primary_cls is None or primary_cls.classification != "ASR_VALIDATION_UNCERTAIN":
        return AlarmDecision(False, R_PRIMARY_NOT_ENTITY_ONLY, detail={"classification": getattr(primary_cls, "classification", None)})
    dp = list(primary_cls.protected.content_word_diffs or [])
    if not dp:
        return AlarmDecision(False, R_NO_DIFF)
    if not all(d.get("entity_like") for d in dp):
        return AlarmDecision(False, R_PRIMARY_NOT_ENTITY_ONLY, detail={"diffs": [(d["canonical"], d["asr"]) for d in dp if not d.get("entity_like")]})
    if len(dp) > max_diffs:
        return AlarmDecision(False, R_TOO_MANY_DIFFS, detail={"primary": len(dp)})

    ds = list(secondary_cls.protected.content_word_diffs or [])
    noun_tokens = {t for d in dp for t in d["canonical"].split()}
    p_canons = {d["canonical"] for d in dp}
    noise = []
    by_canon_s = {}
    for d in ds:
        c_set = set(d["canonical"].split())
        if d["canonical"] in p_canons:
            if not (d.get("entity_like") or c_set <= (noun_tokens | {"s"})):
                return AlarmDecision(False, R_SECONDARY_NOT_ENTITY_ONLY, detail={"canonical": d["canonical"], "asr_secondary": d["asr"]})
            by_canon_s[d["canonical"]] = d
        elif c_set & noun_tokens:
            # Secondaryのspanが固有名詞tokenに隣接する語まで巻き込んでいる("melos drank"->"mellow strength")。固有名詞と所有格's以外の
            # canonical語は、ASR側に同語(または規則的な単複違い)が残っていなければ「隣接語まで聞き取り違い」=受理しない。
            rest = [t for t in d["canonical"].split() if t not in noun_tokens and t != "s"]
            asr_toks = d["asr"].split()
            if not all(any(_same_or_plural(t, a) for a in asr_toks) for t in rest):
                return AlarmDecision(False, R_SECONDARY_NOT_ENTITY_ONLY,
                                     detail={"canonical": d["canonical"], "asr_secondary": d["asr"], "why": "adjacent_word_changed"})
            noise.append({"canonical": d["canonical"], "asr_secondary": d["asr"], "entity_like": bool(d.get("entity_like")), "merged_with_noun": True})
        else:
            # Primaryが一致している位置、または所有格's等でspanが合成された位置(例 'khaite s'->'kites')のSecondary-only差
            noise.append({"canonical": d["canonical"], "asr_secondary": d["asr"], "entity_like": bool(d.get("entity_like"))})
    out = []
    for d in dp:
        bad, info, sim_p = _noun_checks(d["canonical"], d["asr"], canonical_text, ledger_surfaces=ledger_surfaces, cmu_has=cmu_has,
                                        zipf=zipf, max_asr_per_canon=max_asr_per_canon, min_similarity=min_similarity, supply_map=supply_map)
        if bad:
            return AlarmDecision(False, bad, detail=info)
        sh = by_canon_s.get(d["canonical"])
        asr_s, sim_s = "", None
        if sh is not None:
            bad_s, info_s, sim_s = _noun_checks(d["canonical"], sh["asr"], canonical_text, ledger_surfaces=ledger_surfaces,
                                                cmu_has=cmu_has, zipf=zipf, max_asr_per_canon=max_asr_per_canon, min_similarity=min_similarity, supply_map=supply_map)
            if bad_s:
                return AlarmDecision(False, bad_s, detail={"side": "secondary", **(info_s if isinstance(info_s, dict) else {})})
            asr_s = sh["asr"]
        out.append(AlarmDiff(d["canonical"], d["asr"], asr_s, info, sim_p, sim_s if sim_s is not None else 1.0))
    return AlarmDecision(True, "ENTITY_ONLY_ACCEPT", diffs=out, detail={"secondary_only_noise": noise})


# ---------------------------------------------------------------- アラーム記録
def _approx_position(canonical_text: str, token: str, audio_seconds: Optional[float]) -> dict:
    """該当音声箇所(近似)。ASR語タイムスタンプは無いので、canonical内の語位置/文字位置を音声長で按分した目安を併記する。"""
    low = canonical_text.lower()
    i = low.find(token.lower())
    toks = re.findall(r"\S+", canonical_text)
    n = max(len(toks), 1)
    char_ratio = (i / max(len(canonical_text), 1)) if i >= 0 else None
    left = canonical_text[max(0, i - 40):i] if i >= 0 else ""
    right = canonical_text[i + len(token):i + len(token) + 40] if i >= 0 else ""
    return {"char_index": i, "context": f"...{left}[[{token}]]{right}...",
            "approx_seconds": (round(char_ratio * audio_seconds, 1) if (char_ratio is not None and audio_seconds) else None),
            "approx_note": "文字位置を音声長で按分した目安(±数秒)。正確な時刻ではありません" if audio_seconds else "音声長不明のため時刻目安なし"}


def build_alarm_records(decision: AlarmDecision, *, canonical_text: str, display_text: Optional[str] = None,
                        segment_id: str = "", wav_path: str = "", wav_sha256: str = "", family: str = "", article_id: str = "",
                        level: str = "", role: str = "", audio_seconds: Optional[float] = None,
                        primary_text: Optional[str] = None, secondary_text: Optional[str] = None,
                        supply_info: Optional[dict] = None, ledger_info: Optional[dict] = None,
                        slot: Optional[int] = None, models: Optional[dict] = None, now: Optional[str] = None,
                        supply_map: Optional[dict] = None) -> list:
    """AlarmDecision(accept=True)から、固有名詞ごとのアラームrecord(ユーザー承認③の必須項目)を作る。
    supply_info: TTS発音供給の結果(er103_pronunciation_tts_supply_01.SupplyDecision.to_audit()。供給なしは{"supplied":False,"reason":...})。
    ledger_info: Ledger側の根拠(evidence_tier/confidence/sources/hint)。無ければ「根拠なし」と記録する。"""
    if not decision.accept:
        return []
    ts = now or time.strftime("%Y-%m-%dT%H:%M:%S")
    recs = []
    for d in decision.diffs:
        key = f"{family}|{article_id}|{level}|{segment_id}|{wav_sha256 or wav_path}|{_fold(d.canonical)}"
        alarm_id = "pnal_" + hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]
        li = ledger_info or {}
        sup = supply_info or {"supplied": False, "reason": "no_supply_info"}
        orig = " ".join((supply_map or {}).get(t, t) for t in d.canonical.split())
        recs.append({
            "alarm_id": alarm_id, "policy_id": POLICY_ID, "created_at": ts,
            "final_state": STATE_ALARM, "final_state_ja": FINAL_STATE_JA,
            "family": family, "article_id": article_id, "level": level, "segment_id": segment_id, "role": role, "slot": slot,
            "proper_noun": orig, "tts_input_token": d.canonical if orig != d.canonical else None,
            "location": {"wav_path": wav_path, "wav_sha256": wav_sha256, "canonical_sentence": display_text or canonical_text,
                         "tts_input_text": canonical_text, **_approx_position(canonical_text, d.canonical.split()[0], audio_seconds)},
            "mismatch": {"canonical": d.canonical, "asr_primary": d.asr_primary, "asr_secondary": d.asr_secondary,
                         "similarity_primary": d.similarity_primary, "similarity_secondary": d.similarity_secondary,
                         "proper_noun_evidence": d.evidence, "primary_text": primary_text, "secondary_text": secondary_text},
            "pronunciation_basis": {"has_basis": bool(li.get("expected_pronunciation_ipa") or li.get("pronunciation_hint")),
                                    "evidence_tier": li.get("evidence_tier"), "confidence": li.get("confidence"),
                                    "pronunciation_hint": li.get("pronunciation_hint"), "ipa": li.get("expected_pronunciation_ipa"),
                                    "sources": list(li.get("sources") or [])[:3],
                                    "note": ("AI調査結果。出典未検証の場合あり" if li and not li.get("evidence_tier") else "")},
            "tts_supply_result": sup,
            "models": models or {},
            "reason": "固有名詞の発音不一致のみ(Primary/Secondary両ASRとも他の差なし)。承認済み方針によりHuman Review・再生成なしで完成扱い。",
            "operator_only": True,
        })
    return recs


def alarm_audit_block(decision: AlarmDecision, records: list) -> dict:
    """asr_judgement(統一judge監査record)へ追記する`pronunciation_alarm`ブロック(additive)。"""
    return {"policy_id": POLICY_ID, "accepted": decision.accept, "reason": decision.reason,
            "alarm_ids": [r["alarm_id"] for r in records],
            "nouns": [r["proper_noun"] for r in records]}


# ---------------------------------------------------------------- 永続(path引数のみ。既定pathは配線側が渡す)
SHARED_LOG_PATH = "er006_output/audio_retry_cascade_prod_01/pronunciation_alarms.jsonl"   # 配線側が渡す想定の既定(本moduleは使わない)


def append_alarm_log(path: str, records: list) -> int:
    """共有ログ(append-only、alarm_idで冪等)。戻り値=新規追記件数。"""
    if not records:
        return 0
    seen = set()
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                try:
                    seen.add(json.loads(line).get("alarm_id"))
                except Exception:
                    continue
    new = [r for r in records if r["alarm_id"] not in seen]
    if new:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            for r in new:
                f.write(json.dumps(r, ensure_ascii=False, default=str) + "\n")
    return len(new)


_SKIP_KEYS = ("attempts_log", "standard_attempts_log", "fallback_attempts_log", "attempts", "cascade_steps",
              "post_slowdown_cascade", "local_rewrite_recovery", "asr_judgement", "asr_judgement_inherited")


def _walk(node, path):
    if isinstance(node, dict):
        if "asr_judgement" in node or "asr_judgement_inherited" in node:
            yield path, node
        for k, v in node.items():
            if k in _SKIP_KEYS:
                continue
            if isinstance(v, (dict, list)):
                yield from _walk(v, path + [str(k)])
    elif isinstance(node, list):
        for i, v in enumerate(node):
            if isinstance(v, (dict, list)):
                yield from _walk(v, path + [str(i)])


def derive_run_alarms(tts_generation_results: dict) -> list:
    """tts_generation_results.json(採用音声のみ)から、state=PASS_WITH_PRONUNCIATION_ALARMのasr_judgement(継承含む)を列挙し、
    各`pronunciation_alarm_records`を重複排除して返す。PASS_WITH_WARNING registry(er078_pass_with_warning_registry_01)と同じ
    「再導出・冪等・別store無し」方式。STOPPED/未採用segmentは含めない。"""
    out, seen = [], set()
    for path, node in _walk(tts_generation_results or {}, []):
        if node.get("status") not in (None, "OK"):
            continue
        for key, inherited in (("asr_judgement", False), ("asr_judgement_inherited", True)):
            j = node.get(key)
            if not isinstance(j, dict) or j.get("state") != STATE_ALARM:
                continue
            for r in (j.get("pronunciation_alarm_records") or []):
                if r["alarm_id"] in seen:
                    continue
                seen.add(r["alarm_id"])
                out.append({**r, "inherited": inherited, "entry_key": "/".join(path)})
    return out


def write_run_alarms(run_dir: str) -> dict:
    """<run_dir>/audit/tts_generation_results.json -> <run_dir>/audit/pronunciation_alarms.json と operator_alarm_report.md(冪等)。
    一般リスナー向けページ(pages_dir/index.html等)へは**一切書かない**(出力先はaudit/のみ)。"""
    audit_dir = os.path.join(run_dir, "audit")
    src = os.path.join(audit_dir, "tts_generation_results.json")
    results = {}
    if os.path.exists(src):
        with open(src, encoding="utf-8") as f:
            results = json.load(f)
    alarms = derive_run_alarms(results)
    payload = {"policy_id": POLICY_ID, "source": "audit/tts_generation_results.json", "count": len(alarms), "operator_only": True,
               "alarms": alarms}
    os.makedirs(audit_dir, exist_ok=True)
    jp = os.path.join(audit_dir, "pronunciation_alarms.json")
    with open(jp + ".tmp", "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, sort_keys=True)
    os.replace(jp + ".tmp", jp)
    mp = os.path.join(audit_dir, "operator_alarm_report.md")
    with open(mp, "w", encoding="utf-8") as f:
        f.write(render_operator_report(alarms))
    return {"json": jp, "md": mp, "count": len(alarms)}


def render_operator_report(alarms: list) -> str:
    """記事完成報告へ貼る運営責任者向けアラーム節(Markdown)。0件でも節を出す。"""
    lines = ["## 固有名詞発音アラーム(運営責任者向け・一般リスナー非表示)"]
    if not alarms:
        lines.append("0件(固有名詞の発音不一致アラームなし)")
        return "\n".join(lines) + "\n"
    lines.append(f"{len(alarms)}件。最終状態=**{FINAL_STATE_JA}**。制作は停止せずHuman Reviewにも回していません。確認・承認操作は完成の条件ではありません。")
    for a in alarms:
        m, loc, b, s = a["mismatch"], a["location"], a["pronunciation_basis"], a["tts_supply_result"]
        lines += [
            f"- **{a['proper_noun']}** ({a['family']}/{a['level']}/{a['segment_id']}{' [継承]' if a.get('inherited') else ''})",
            f"  - 音声箇所: {loc.get('wav_path')} / 文脈 `{loc.get('context')}`" + (f" / 目安{loc['approx_seconds']}秒" if loc.get("approx_seconds") is not None else ""),
            f"  - 検出した不一致: 原稿 `{m['canonical']}` -> Primary `{m['asr_primary'] or '(原稿どおり)'}` / Secondary `{m['asr_secondary'] or '(原稿どおり)'}`",
            f"  - 発音の根拠: " + (f"階層={b.get('evidence_tier') or '未検証'} / 確信度={b.get('confidence')} / hint={b.get('pronunciation_hint')}" if b.get("has_basis") else "根拠なし(調査で発音情報を取得できていません)"),
            f"  - TTS発音改善: " + (f"供給あり({s.get('tier')}階層, `{s.get('original')}`->`{s.get('respelling')}`)でも不一致" if s.get("supplied") else f"供給なし({s.get('reason')})"),
            f"  - 最終状態: {FINAL_STATE_JA}",
        ]
    return "\n".join(lines) + "\n"


def write_run_alarms_safe(run_dir: str) -> dict:
    """生成完了hook用の非ブロッキング版(例外を投げない。PWW registryの`write_listening_list_safe`と同じ契約)。"""
    rep = {"run_dir": run_dir, "json": None, "md": None, "count": None, "error": None}
    try:
        r = write_run_alarms(run_dir)
        rep.update(json=r["json"], md=r["md"], count=r["count"])
    except Exception as exc:  # noqa: BLE001
        rep["error"] = f"{type(exc).__name__}: {exc}"
        import sys
        print(f"[WARN][pronunciation_alarms] 出力に失敗(生成は継続): {run_dir}: {rep['error']}", file=sys.stderr)
    return rep
