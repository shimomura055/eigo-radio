# -*- coding: utf-8 -*-
"""ASR-QUALITY-2ITEMS-COMPREHENSIVE-01 PN 委任_04: Run Entity Table(RET) Production実装 [APPROVED_FOR_PRODUCTION: ユーザー正式採用2026-10-23 UDR #168。PRODUCTION_WIREDはFable受入後]

固有名詞の「認識」の正本を run 単位の“本文実体表”として作り、`er103_proper_noun_alarm_policy_01.evaluate_alarm_eligibility` へ **証拠の供給源**として渡す
(RET-2=G5の位置紐づけ証拠、RET-3=G3のSecondary span)。受理境界(類似度>=0.40・一般語ブロック・P-03・G3・数値/否定/脱落・KP/JA除外・slot・HR Lock)は無変更。

有効条件は単一読取関数 `is_active_for_run()` = `RUN_ENTITY_TABLE_ENABLED is True ∧ pnap.is_active_for_run()`(PNAPのX/Z run scope内)。
env/引数/設定dictから変えられない。rollback=`RUN_ENTITY_TABLE_ENABLED=False`の1行(RET由来の受理音声はStore guard/継承で再生成へ回る)。
Trial実装(DEV用の旧module)は参照用に残置し、本moduleはTrial moduleをimportしない(AST testで固定)。

Opus条件Cレビュー(OPUS_REVIEW_02_COND_C.md)反映:
  W-03 保存はLLM生候補(raw)+coverage(text sha)のみ。判定用の表は構築点ごとに「今のprovider textの和集合」に対し決定論(API 0)で再導出する
       (今のtextに逐語出現しない旧entryは外す)。NER失敗textはcoverageに入れず再試行(W-09)。
  W-10 builder_version=build_version(prompt/model/検証規則/導出)、rules_version=eligible規則(継承の復元可否)に分離し、明示定数+関連source hashで凍結。
  W-11 並行書込はlockfile(O_EXCL)+再読込和集合+atomic replace。
  W-12 逐語検証は供給前script textに加えtts_safe変換後textでも行う(provider側でalt_textsを付与)。
"""
from __future__ import annotations

import hashlib
import inspect
import json
import os
import re
import time
import unicodedata
from contextlib import contextmanager
from dataclasses import dataclass, field, asdict
from typing import Callable, Iterable, Optional

import er006_model_routing_contract_01 as routing
import er103_proper_noun_alarm_policy_01 as pol

# ---- 単一flag(読取は is_enabled()/is_active_for_run() のみ。env/引数/設定dictから変えない) ----
RUN_ENTITY_TABLE_ENABLED = True
FLAG_NOTE = "ユーザー正式採用(APPROVED_FOR_PRODUCTION 2026-10-23, UDR #168)により既定ON。X/Z run scope(PNAP scope)外では不活性。rollback=Falseへ1行"


def is_enabled() -> bool:
    return RUN_ENTITY_TABLE_ENABLED is True


def is_active_for_run() -> bool:
    """RETの唯一の有効判定: RET flag有効 ∧ PNAP有効かつX/Z run scope内。A/B/C・単体呼出・dry_runは常にFalse。"""
    return is_enabled() and pol.is_active_for_run()


SCHEMA_VERSION = "ret_prod_01"
MODEL = routing.RUN_ENTITY_TABLE_MODEL
PRICE_IN, PRICE_OUT, USD_JPY = 0.10, 0.50, 160.0     # per 1M tokens(gpt-6-luna。er006_model_routing_pricing_coverage_test_01.py:50-52。報告用の概算。実費はcost loggerが記録)
MAX_NER_CALLS_PER_BUILD = 2
MAX_INPUT_CHARS = 80000
LOCK_WAIT_SEC = 5.0
LOCK_STALE_SEC = 30.0

CATEGORIES = ("person", "place", "organization", "work_title", "brand_product", "other_named")
CMU_OK_CATEGORIES = frozenset({"person", "place", "organization", "brand_product"})   # OF-PN2-04
MAX_ENTITY_WORDS = 5
GRADE_DECLARED, GRADE_CONFIRMED, GRADE_WEAK = "declared", "confirmed", "weak"
USABLE_GRADES = frozenset({GRADE_DECLARED, GRADE_CONFIRMED})

PROMPT_A = ("You list the proper nouns (named entities) in an English radio script, for a text-to-speech pronunciation QA step. "
            "Include: people (first names, surnames, nicknames, names inside quotations or song lyrics, names that start a sentence), places, organizations/media, "
            "titles of works, brands/products, other named things. Do NOT list ordinary words just because they are capitalized at the start of a sentence or heading, "
            "months/weekdays, nationality adjectives, or generic nouns. Give each entity once, with the exact surface form (multi-word names as one entity, e.g. 'Stephen Reicher'). "
            "Category is one of: person, place, organization, work_title, brand_product, other_named.")
PROMPT_B = ("Task: quality control for speech synthesis. Read the English text and extract every capitalized NAME that refers to one specific real or fictional "
            "person (including characters, nicknames and names that appear only in dialogue, lyrics or as a vocative), place, organization, product/brand or work. "
            "A name starts with a capital letter because it is a name, not because it begins a sentence. Skip ordinary words, headings, job titles, "
            "nationalities, days, months, and common nouns. Return each name once, copied exactly as written (keep multi-word names together). "
            "Category must be one of: person, place, organization, work_title, brand_product, other_named.")
PROMPTS = {"A": PROMPT_A, "B": PROMPT_B}
SCHEMA = {"name": "entities", "strict": True, "schema": {"type": "object", "additionalProperties": False, "required": ["entities"], "properties": {"entities": {"type": "array", "items": {
    "type": "object", "additionalProperties": False, "required": ["surface", "category"],
    "properties": {"surface": {"type": "string"}, "category": {"type": "string", "enum": list(CATEGORIES)}}}}}}}

_WORD_RE = re.compile(r"[^\W\d_]+", re.UNICODE)
_BENIGN_GAP_RE = re.compile(r"^[\s\-'’]*$")
_RUN_GAP_RE = re.compile(r"^[\s,;\-'’]*$")        # RET-3: 隣接実体どうしの連結で許す区切り(語を含まない句読点)
R_RET3_SUPPLIED = "supplied_token_in_span"          # W-05


# ---------------------------------------------------------------- 語分割・正規化
@dataclass(frozen=True)
class W:
    fold: str
    start: int
    end: int
    orig: str


def words(text: str) -> list:
    return [W(pol._fold(m.group(0)), m.start(), m.end(), m.group(0)) for m in _WORD_RE.finditer(text or "")]


def nq(text: str) -> str:
    """引用符向き・空白の正規化(逐語検証用。大文字小文字は保持)。"""
    t = unicodedata.normalize("NFC", text or "")
    t = t.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').replace(" ", " ")
    return re.sub(r"\s+", " ", t)


def _gap_ok(text: str, a: W, b: W) -> bool:
    gap = text[a.end:b.start]
    if _BENIGN_GAP_RE.match(gap):
        return True
    return len(a.fold) == 1 and re.match(r"^\.\s*$", gap) is not None


def text_sha(text: str) -> str:
    return hashlib.sha256((text or "").strip().encode("utf-8")).hexdigest()


# ---------------------------------------------------------------- 実体表
@dataclass
class Entry:
    surface: str
    words: list
    category: str
    grade: str
    sources: list
    eligible: list
    initials: list
    notes: list = field(default_factory=list)

    @property
    def usable(self) -> bool:
        return self.grade in USABLE_GRADES and bool(self.eligible)

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "Entry":
        return Entry(surface=d["surface"], words=list(d["words"]), category=d["category"], grade=d["grade"], sources=list(d.get("sources") or []),
                     eligible=list(d.get("eligible") or []), initials=list(d.get("initials") or []), notes=list(d.get("notes") or []))


class EntityTable:
    """run単位の実体表。`entries`のうち usable(declared/confirmed ∧ eligible token有)だけが証拠源になる。判定時に全処理がAPI 0。"""

    def __init__(self, entries: Optional[list] = None, *, status: str = "OK", meta: Optional[dict] = None):
        self.entries: list = list(entries or [])
        self.status = status
        self.meta: dict = dict(meta or {})

    def sha256(self) -> str:
        body = json.dumps([[e.surface, e.words, e.category, e.grade, e.eligible, e.initials] for e in self.entries], ensure_ascii=False, sort_keys=True)
        return hashlib.sha256(body.encode("utf-8")).hexdigest()

    def usable_entries(self) -> list:
        return [e for e in self.entries if e.usable]

    def is_empty(self) -> bool:
        return not self.usable_entries()

    # ---- 出現位置(OF-PN2-01: 証拠は語集合でなく、このsegment text内の実体出現範囲に紐づける)
    def occurrences(self, text: str, ws: Optional[list] = None) -> list:
        ws = ws if ws is not None else words(text)
        out = []
        for e in self.usable_entries():
            n = len(e.words)
            if n == 0:
                continue
            need_cap = set(e.eligible) | set(e.initials)
            for i in range(0, len(ws) - n + 1):
                if all(ws[i + k].fold == e.words[k] for k in range(n)):
                    if not all(_gap_ok(text, ws[i + k], ws[i + k + 1]) for k in range(n - 1)):
                        continue
                    if not all(ws[i + k].orig[:1].isupper() for k in range(n) if e.words[k] in need_cap):
                        continue
                    out.append((i, i + n - 1, e))
        return out

    @staticmethod
    def _phrase_positions(ws: list, phrase: list) -> list:
        n = len(phrase)
        return [(i, i + n - 1) for i in range(0, len(ws) - n + 1) if all(ws[i + k].fold == phrase[k] for k in range(n))] if n else []

    def grant_for_phrase(self, text: str, phrase_tokens: list) -> tuple:
        """Primary diff の canonical 句が、この text 内の実体出現範囲に**全出現が**連続して含まれる場合のみ、その実体の eligible token / 内部イニシャルを返す。
        戻り値=(grant frozenset, info dict)。含まれない/出現なし/一部出現が範囲外 -> 空(fail-closed)。"""
        ws = words(text)
        occs = self.occurrences(text, ws)
        poss = self._phrase_positions(ws, list(phrase_tokens))
        if not occs or not poss:
            return frozenset(), {"reason": "no_entity_occurrence" if not occs else "phrase_not_found"}
        grant, used = set(), []
        for (a, b) in poss:
            cover = [(oa, ob, e) for (oa, ob, e) in occs if oa <= a and b <= ob + (1 if (ob + 1 < len(ws) and ws[ob + 1].fold == "s") else 0)]
            if not cover:
                return frozenset(), {"reason": "phrase_occurrence_outside_entity", "at": [a, b]}
            for (oa, ob, e) in cover:
                used.append(e)
        for e in used:
            for t in list(e.eligible) + list(e.initials):
                if t in phrase_tokens:
                    grant.add(t)
        if not grant:
            return frozenset(), {"reason": "no_eligible_token_in_phrase"}
        seen, ent = set(), []
        for e in used:
            if e.surface not in seen:
                seen.add(e.surface)
                ent.append({"surface": e.surface, "words": e.words, "category": e.category, "grade": e.grade, "eligible": e.eligible, "initials": e.initials})
        return frozenset(grant), {"entities": ent, "grant": sorted(grant)}

    def entity_run_for_span(self, text: str, span_tokens: list) -> Optional[dict]:
        """RET-3(OF-PN2-02): Secondary span が「当該位置で連続する1実体出現(または区切り語なし隣接複数実体)」とtoken単位で一致するか。"""
        ws = words(text)
        occs = sorted(self.occurrences(text, ws), key=lambda x: (x[0], x[1]))
        poss = self._phrase_positions(ws, list(span_tokens))
        if not poss or not occs:
            return None
        results = []
        for (a, b) in poss:
            def dfs(pos: int, chain: list):
                if pos == b + 1:
                    return chain
                for (oa, ob, e) in occs:
                    if oa == pos and ob <= b:
                        r = dfs(ob + 1, chain + [(oa, ob, e)])
                        if r is not None:
                            return r
                if pos == b and ws[pos].fold == "s" and chain and ws[pos].start - ws[pos - 1].end <= 2:
                    return chain
                return None
            chain = dfs(a, [])
            if chain is None:
                return None
            for (x, y) in zip(chain, chain[1:]):
                if not (_gap_ok(text, ws[x[1]], ws[y[0]]) or _RUN_GAP_RE.match(text[ws[x[1]].end:ws[y[0]].start])):
                    return None
            results.append((a, b, chain))
        grant = set()
        ents = []
        for (a, b, chain) in results:
            for (_, _, e) in chain:
                grant |= (set(e.eligible) | set(e.initials)) & set(span_tokens)
                ents.append({"surface": e.surface, "words": e.words, "category": e.category, "grade": e.grade})
        if not grant:
            return None
        return {"span": list(span_tokens), "positions": [(a, b) for (a, b, _) in results], "grant": frozenset(grant), "entities": ents}

    def phrase_positions(self, text: str, phrase_tokens: list) -> list:
        return self._phrase_positions(words(text), list(phrase_tokens))

    # ---- RET-3(er103.G3の不受理分岐でのみ呼ばれる)
    def ret3_check(self, d_sec: dict, dp: list, canonical_text: str, *, ledger_surfaces, cmu_has, zipf, max_asr_per_canon, min_similarity,
                   role, supply_map=None) -> tuple:
        """戻り値=(True, record, True) | (False, reason, touched)。touched=表のentityが当該spanに関与した(不受理理由を`ret3_rejected`として残してよい)か。
        表と無関係のspanは touched=False(=現行の不受理detailとバイト一致、W-02(c))。"""
        span_tokens = d_sec["canonical"].split()
        run = self.entity_run_for_span(canonical_text, span_tokens)
        if run is None:
            return False, "span_not_one_entity_run", False
        if any(t in (supply_map or {}) for t in span_tokens):           # W-05: 供給で綴り置換した語を含むspanはRET-3の対象外
            return False, R_RET3_SUPPLIED, True
        contained = []
        for p in dp:
            for (a, b) in self.phrase_positions(canonical_text, p["canonical"].split()):
                for (sa, sb) in run["positions"]:
                    overlap = not (b < sa or sb < a)
                    if overlap and not (sa <= a and b <= sb):
                        return False, "primary_diff_straddles_span_boundary", True
                    if sa <= a and b <= sb:
                        contained.append(p)
        if not contained:
            return False, "no_primary_diff_inside_span", True
        ls = frozenset(ledger_surfaces) | run["grant"]
        bad, info, sim = pol._noun_checks(d_sec["canonical"], d_sec["asr"], canonical_text, ledger_surfaces=ls, cmu_has=cmu_has, zipf=zipf,
                                          max_asr_per_canon=max_asr_per_canon, min_similarity=min_similarity, supply_map=None, role=role)
        if bad:
            return False, "noun_checks:%s" % bad, True
        p_asr = " ".join(p["asr"] for p in contained)
        if pol.asr_all_general(p_asr, cmu_has=cmu_has, zipf=zipf) and pol.asr_all_general(d_sec["asr"], cmu_has=cmu_has, zipf=zipf):
            return False, "p03_both_asr_general", True
        label = self.relabel(d_sec["canonical"], info, frozenset(ledger_surfaces), run["grant"], {"entities": run["entities"]}, canonical_text, cmu_has, role)
        return True, {"span": d_sec["canonical"], "asr_secondary": d_sec["asr"], "similarity": sim, "entities": run["entities"], "evidence": label}, True

    @staticmethod
    def relabel(canon: str, info, base_ledger, grant, ginfo, canonical_text, cmu_has, role):
        """grant に依存して通った token の証拠ラベルを `entity_table:<grade>:<category>` へ置換する。"""
        if not grant or not isinstance(info, str) or info == "supplied_respelling":
            return info
        ents = {w: (e["grade"], e["category"]) for e in (ginfo or {}).get("entities", []) for w in e["words"]}
        evs = []
        for t in canon.split():
            ok, ev = pol.proper_noun_evidence(t, canonical_text, ledger_surfaces=base_ledger, cmu_has=cmu_has, role=role)
            if ok:
                evs.append(ev)
            else:
                g, c = ents.get(t, ("confirmed", "?"))
                evs.append("entity_table:%s:%s" % (g, c))
        return "+".join(sorted(set(evs)))

    @staticmethod
    def alarm_labels(diffs: list, *, zipf: Callable = pol._default_zipf) -> list:
        """OF-PN2-08: 区別は関門でなく、アラームのラベル(試聴優先度)。受理境界は変えない。"""
        res = []
        for diff in diffs:
            sp = diff.similarity_primary
            band = "high(>=0.70)" if sp >= 0.70 else ("mid(0.50-0.70)" if sp >= 0.50 else "low(0.40-0.50)")
            same_other = bool(diff.asr_secondary) and pol._despaced(diff.asr_primary) == pol._despaced(diff.asr_secondary)
            border = False
            for tk in re.findall(r"[a-z0-9']+", pol._fold(diff.asr_primary + " " + (diff.asr_secondary or ""))):
                z = zipf(tk)
                if 3.5 <= z < 4.0:
                    border = True
            res.append({"similarity_band": band, "both_asr_same_other_word": same_other, "asr_zipf_near_general_boundary": border})
        return res

    def audit_block(self, table_used: list, ret3_records: list) -> dict:
        """受理に実際に寄与したentry(W-01)を保存形にする(再判定=LLM 0 callの復元元)。"""
        names = []
        for rec in table_used:
            names += [e["surface"] for e in rec.get("entities", [])]
        for rec in ret3_records:
            names += [e["surface"] for e in rec.get("entities", [])]
        seen, used = set(), []
        for e in self.entries:
            if e.surface in names and e.surface not in seen:
                seen.add(e.surface)
                used.append(e.to_dict())
        return {"sha256": self.sha256(), "status": self.status, "builder_version": builder_version(), "rules_version": rules_version(),
                "per_diff": table_used, "ret3": ret3_records, "entries_used": used}


def table_from_saved_entries(entries: list, *, rules_ver: Optional[str] = None) -> Optional[EntityTable]:
    """OF-PN2-06(i)/W-04: アラームblockに保存した実体entryから表を復元(表sha一致は不要。LLM 0 call。当該segment textへの逐語出現のみ確認される)。
    rules_ver(保存時の rules_version)が現行と一致しないときは復元しない(None=呼出元は再判定NGまたは表なし)。"""
    if rules_ver is not None and rules_ver != rules_version():
        return None
    return EntityTable([Entry.from_dict(x) for x in entries or []], status="RESTORED_FROM_ALARM")


def restore_from_audit_block(block: Optional[dict]) -> Optional[EntityTable]:
    """pronunciation_alarmブロックの`entity_table`から復元表を作る。復元不可(無し/rules_version不一致/RET不活性)はNone。"""
    et = (block or {}).get("entity_table") if isinstance(block, dict) else None
    if not et or not is_active_for_run():
        return None
    return table_from_saved_entries(et.get("entries_used") or [], rules_ver=et.get("rules_version"))


def entity_contributed(aj) -> bool:
    """asr_judgement(継承record含む)の受理にRETが寄与したか(`pronunciation_alarm.entity_table`あり)。ortho_contributedと同形(W-06)。"""
    if not isinstance(aj, dict):
        return False
    pa = aj.get("pronunciation_alarm")
    return isinstance(pa, dict) and bool(pa.get("entity_table"))


def restorable(aj) -> bool:
    if not isinstance(aj, dict):
        return False
    et = (aj.get("pronunciation_alarm") or {}).get("entity_table") or {}
    return bool(et.get("entries_used")) and et.get("rules_version") == rules_version()


# ---------------------------------------------------------------- run単位保持(process内状態。pnap._RUN_SCOPE と同型、finallyで必ず解除)
_RUN_TABLE: Optional[EntityTable] = None


def current_table() -> Optional[EntityTable]:
    return _RUN_TABLE


@contextmanager
def run_table(table: Optional[EntityTable]):
    global _RUN_TABLE
    prev = _RUN_TABLE
    _RUN_TABLE = table
    try:
        yield table
    finally:
        _RUN_TABLE = prev


def adapter_table() -> Optional[EntityTable]:
    """W-04: **adapter経路(er006_secondary_asr_01._pnap_try_accept)だけ**が呼ぶ。継承・Store再判定は呼ばない(復元表かNoneを明示で渡す)。"""
    return _RUN_TABLE if is_active_for_run() else None


# ---------------------------------------------------------------- 構築入力
@dataclass
class Seg:
    text: str                                    # 供給前script text(NER入力・coverage単位)
    role: Optional[str] = "FULL_STORY"
    segment_id: str = ""
    alt_texts: tuple = ()                        # tts_safe変換後等の別形(W-12。逐語検証のみに使い、NERには渡さない)


def _check_texts(segs: list) -> list:
    out = []
    for s in segs:
        out.append(s.text)
        out += [a for a in (s.alt_texts or ()) if a]
    return out


# ---------------------------------------------------------------- 決定論の導出(API 0)
def _token_class(tok: str, category: str, *, lowercase_seen: set, cmu_has: Callable, zipf: Callable) -> tuple:
    if tok in lowercase_seen:
        return False, "lowercase_form_in_text"
    if pol.is_general_word(tok, cmu_has=cmu_has, zipf=zipf):
        return False, "general_word"
    oov = not cmu_has(tok)
    if oov or category in CMU_OK_CATEGORIES:
        return True, "oov" if oov else "cmu_in_nongeneral"
    return False, "category_%s_requires_oov" % category


def _lowercase_forms(texts: Iterable[str]) -> set:
    s = set()
    for t in texts:
        for m in _WORD_RE.finditer(t or ""):
            w = m.group(0)
            if w[:1].islower():
                s.add(pol._fold(w))
    return s


def _headings(texts: Iterable[str]) -> set:
    h = set()
    for t in texts:
        for line in (t or "").splitlines():
            ln = line.strip()
            if ln.startswith("#") or (ln and len(ln.split()) <= 10 and not re.search(r"[.!?\"”’']$", ln)):
                h.add(nq(re.sub(r"^#+\s*", "", ln)).strip(" *_"))
    return h


def _verbatim_in(surface: str, texts: Iterable[str]) -> bool:
    s = nq(surface).strip()
    if not s:
        return False
    pat = re.compile(r"(?<![^\W\d_])" + re.escape(s) + r"(?![^\W\d_])")
    return any(pat.search(nq(t)) for t in texts if t)


def _det_support(tok: str, segs: list, cmu_has: Callable) -> Optional[str]:
    for sg in segs:
        ok, lab = pol.proper_noun_evidence(tok, sg.text, ledger_surfaces=frozenset(), cmu_has=cmu_has, role=sg.role)
        if ok:
            return lab
    return None


_INITIAL_ONLY_RE = re.compile(r"^[A-Z]\.?$")


def _merge_initials(items: list, texts: list) -> list:
    """LLMが「L.」と「Mimoun」を別entityに分けた場合に、本文の `L. Mimoun` を1実体として復元する。決定論・API 0。"""
    out, bare = [], []
    for it in items:
        sf = it.get("surface") if isinstance(it, dict) else None
        if isinstance(sf, str) and _INITIAL_ONLY_RE.match(sf.strip()):
            bare.append(it)
            continue
        out.append(it)
    if not bare:
        return items
    merged = []
    for it in out:
        sf = it.get("surface") if isinstance(it, dict) else None
        if not isinstance(sf, str):
            continue
        for t in texts:
            for m in re.finditer(r"(?<![^\W\d_])([A-Z])\.\s+" + re.escape(sf.strip()) + r"(?![^\W\d_])", nq(t or "")):
                merged.append({"surface": "%s. %s" % (m.group(1), sf.strip()), "category": it.get("category")})
    seen, res = set(), []
    for it in out + merged:
        k = (it.get("surface") if isinstance(it, dict) else str(it))
        if k not in seen:
            seen.add(k)
            res.append(it)
    return res


def _verify_items(items: list, check_texts: list, heads: set, dropped: list) -> list:
    """LLM/保存候補の検証(幻覚除去・長句・見出し・カテゴリ)。戻り値=[(surface, category, key)]。"""
    out, seen = [], set()
    for it in items:
        if not isinstance(it, dict):
            dropped.append({"surface": str(it)[:60], "reason": "bad_item"})
            continue
        sf, cat = it.get("surface"), it.get("category")
        if not isinstance(sf, str) or not sf.strip():
            dropped.append({"surface": str(sf)[:60], "reason": "bad_surface"})
            continue
        sf = sf.strip()
        if cat not in CATEGORIES:
            dropped.append({"surface": sf, "reason": "bad_category"})
            continue
        if not _verbatim_in(sf, check_texts):
            dropped.append({"surface": sf, "reason": "not_verbatim"})
            continue
        if len(sf.split()) > MAX_ENTITY_WORDS:
            dropped.append({"surface": sf, "reason": "long_phrase"})
            continue
        if nq(sf).strip(" *_") in heads:
            dropped.append({"surface": sf, "reason": "heading_or_title_line"})
            continue
        key = tuple(w.fold for w in words(sf))
        if not key or key in seen:
            continue
        seen.add(key)
        out.append((sf, cat, key))
    return out


def _mk_entry(surface: str, category: str, grade: str, src: str, *, lower_seen: set, dropped: list, cmu_has: Callable, zipf: Callable) -> Optional[Entry]:
    ws = words(surface)
    toks = [w.fold for w in ws]
    if not toks:
        dropped.append({"surface": surface, "reason": "no_alpha_token"})
        return None
    elig, inits, notes = [], [], []
    for w in ws:
        if len(w.fold) == 1 and w.orig[:1].isupper() and len(ws) >= 2:
            inits.append(w.fold)
            continue
        ok, why = _token_class(w.fold, category, lowercase_seen=lower_seen, cmu_has=cmu_has, zipf=zipf)
        if ok:
            elig.append(w.fold)
        else:
            notes.append("%s:%s" % (w.fold, why))
    if not elig:
        inits = []
    return Entry(surface=surface, words=toks, category=category, grade=grade, sources=[src], eligible=sorted(set(elig)), initials=sorted(set(inits)), notes=notes)


def empty_raw() -> dict:
    return {"declared": [], "llm_a": [], "llm_b": []}


def derive_entries(raw: dict, segs: list, *, cmu_has: Callable = pol._default_cmu_has, zipf: Callable = pol._default_zipf) -> tuple:
    """W-03: 保存したLLM生候補(raw)+宣言を、**今のprovider textの和集合**に対して決定論で実体entryへ導出する(API 0)。
    今のtextに逐語出現しない候補は外す。戻り値=(entries, meta, pending_b)。pending_b=独立裏付け(決定論証拠 or call B一致)待ちのentry数。"""
    meta = {"dropped": [], "blocked_general_person_place": []}
    dropped = meta["dropped"]
    check_texts = _check_texts(segs)
    lower_seen = _lowercase_forms(check_texts)
    heads = _headings(check_texts)
    entries: dict = {}

    for d in raw.get("declared") or ():
        nm = (d.get("name") if isinstance(d, dict) else str(d)) or ""
        cat = (d.get("category") if isinstance(d, dict) else None) or "person"
        src = "declared:%s" % ((d.get("source") if isinstance(d, dict) else None) or "seed")
        if cat not in CATEGORIES:
            cat = "person"
        if not _verbatim_in(nm, check_texts):
            dropped.append({"surface": nm, "reason": "declared_not_in_text"})
            continue
        e = _mk_entry(nm, cat, GRADE_DECLARED, src, lower_seen=lower_seen, dropped=dropped, cmu_has=cmu_has, zipf=zipf)
        if e is not None:
            entries[tuple(e.words)] = e

    ver_a = _verify_items(list(raw.get("llm_a") or []), check_texts, heads, dropped)
    cand: list = []
    for (sf, cat, key) in ver_a:
        if key in entries:
            entries[key].sources.append("llm_a")
            continue
        e = _mk_entry(sf, cat, GRADE_WEAK, "llm_a", lower_seen=lower_seen, dropped=dropped, cmu_has=cmu_has, zipf=zipf)
        if e is not None:
            cand.append(e)

    need_call2 = []
    for e in cand:
        if not e.eligible:
            meta["blocked_general_person_place"].append({"surface": e.surface, "category": e.category, "notes": e.notes})
            e.notes.append("no_eligible_token")
            continue
        det = None
        for t in e.eligible:
            det = _det_support(t, segs, cmu_has)
            if det:
                break
        if det:
            e.grade = GRADE_CONFIRMED
            e.sources.append("det:%s" % det)
        else:
            need_call2.append(e)

    b_map = {}
    for (sf, cat, key) in _verify_items(list(raw.get("llm_b") or []), check_texts, heads, []):
        b_map[key] = cat
    pending = 0
    for e in need_call2:
        agree, exact = None, False
        if tuple(e.words) in b_map:
            agree, exact = b_map[tuple(e.words)], True
        else:
            for key, cat_b in b_map.items():
                if any(t in key for t in e.eligible):
                    agree = cat_b
                    break
        if agree is not None:
            if exact and agree in ("work_title", "other_named") and e.category in CMU_OK_CATEGORIES:
                e.category = agree
                e2 = _mk_entry(e.surface, e.category, GRADE_CONFIRMED, "llm_a", lower_seen=lower_seen, dropped=[], cmu_has=cmu_has, zipf=zipf)
                if e2 is not None:
                    e.eligible, e.initials, e.notes = e2.eligible, e2.initials, e2.notes + ["category_downgraded_by_call2"]
            if e.eligible:
                e.grade = GRADE_CONFIRMED
                e.sources.append("llm_b_agree")
        else:
            e.notes.append("no_independent_support")
            pending += 1
    for e in cand:
        entries.setdefault(tuple(e.words), e)
    return list(entries.values()), meta, pending


# ---------------------------------------------------------------- builder_version(W-10)
BUILDER_RULES_CONSTANT = "ret_rules_2026-10-23_v1"      # eligible規則(継承の復元可否)を変えたら必ず更新する
BUILDER_BUILD_CONSTANT = "ret_build_2026-10-23_v1"      # prompt/検証/導出を変えたら必ず更新する


def _src(*fns) -> str:
    h = hashlib.sha256()
    for fn in fns:
        h.update(inspect.getsource(fn).replace("\r\n", "\n").encode("utf-8"))
    return h.hexdigest()


def _lib_version(name: str) -> str:
    try:
        import importlib.metadata as m
        return m.version(name)
    except Exception:
        return "unknown"


def rules_inputs() -> dict:
    """eligible規則(表のentryが証拠を付与してよいtokenを決める規則)の入力。継承時に保存entryを復元してよいかの判定に使う。"""
    return {"const": BUILDER_RULES_CONSTANT, "GENERAL_WORD_MIN_ZIPF": pol.GENERAL_WORD_MIN_ZIPF, "CMU_OK_CATEGORIES": sorted(CMU_OK_CATEGORIES),
            "USABLE_GRADES": sorted(USABLE_GRADES), "MAX_ENTITY_WORDS": MAX_ENTITY_WORDS, "wordfreq": _lib_version("wordfreq"),
            "pronouncing": _lib_version("pronouncing"), "src": _src(_token_class, pol.is_general_word, pol.proper_noun_evidence)}


def rules_version() -> str:
    return hashlib.sha256(json.dumps(rules_inputs(), sort_keys=True).encode("utf-8")).hexdigest()[:16]


def build_inputs() -> dict:
    """保存した生候補(raw)を再利用してよいかの判定(resume)に使う入力。prompt/model/検証・導出規則を含む。"""
    return {"const": BUILDER_BUILD_CONSTANT, "rules": rules_version(), "model": MODEL, "prompts": {k: hashlib.sha256(v.encode()).hexdigest()[:12] for k, v in PROMPTS.items()},
            "CATEGORIES": list(CATEGORIES), "src": _src(_verify_items, _merge_initials, _headings, _lowercase_forms, _verbatim_in, _det_support,
                                                       _mk_entry, derive_entries)}


def builder_version() -> str:
    return hashlib.sha256(json.dumps(build_inputs(), sort_keys=True).encode("utf-8")).hexdigest()[:16]


# ---------------------------------------------------------------- 保存・並行書込(W-11)
@contextmanager
def _file_lock(path: str):
    """lockfile(O_EXCL)。取得できなければ(LOCK_WAIT_SEC後)Falseで続行=書込をskip(runは止めない)。stale lockは回収。"""
    lock = path + ".lock"
    os.makedirs(os.path.dirname(lock) or ".", exist_ok=True)
    got = False
    t0 = time.time()
    while True:
        try:
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode())
            os.close(fd)
            got = True
            break
        except FileExistsError:
            try:
                if time.time() - os.path.getmtime(lock) > LOCK_STALE_SEC:
                    os.remove(lock)
                    continue
            except OSError:
                pass
            if time.time() - t0 > LOCK_WAIT_SEC:
                break
            time.sleep(0.1)
        except OSError:
            break
    try:
        yield got
    finally:
        if got:
            try:
                os.remove(lock)
            except OSError:
                pass


def load_saved(path: str) -> Optional[dict]:
    try:
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
    except (OSError, ValueError):
        return None
    if not isinstance(d, dict) or d.get("schema") != SCHEMA_VERSION or not isinstance(d.get("raw"), dict):
        return None
    return d


def _union_raw(a: dict, b: dict) -> dict:
    out = empty_raw()
    for k in ("declared", "llm_a", "llm_b"):
        seen, lst = set(), []
        for it in list(a.get(k) or []) + list(b.get(k) or []):
            kk = json.dumps(it, sort_keys=True, ensure_ascii=False)
            if kk not in seen:
                seen.add(kk)
                lst.append(it)
        out[k] = lst
    return out


def _save(path: str, doc: dict) -> bool:
    """再読込→和集合→atomic replace。lock未取得なら書かない(False)。"""
    with _file_lock(path) as got:
        if not got:
            return False
        disk = load_saved(path)
        if disk and disk.get("builder_version") == doc["builder_version"]:
            doc["raw"] = _union_raw(disk["raw"], doc["raw"])
            doc["covered_text_sha256"] = sorted(set(disk.get("covered_text_sha256") or []) | set(doc["covered_text_sha256"]))
            doc["covered_b_text_sha256"] = sorted(set(disk.get("covered_b_text_sha256") or []) | set(doc["covered_b_text_sha256"]))
            doc["builds"] = list(disk.get("builds") or []) + [b for b in doc["builds"] if b not in (disk.get("builds") or [])]
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        tmp = f"{path}.{os.getpid()}.tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=2, sort_keys=True, default=str)
        os.replace(tmp, path)
        return True


# ---------------------------------------------------------------- NER(gpt-6-luna、Responses API、strict JSON)
def _stop_hit(run_dir: Optional[str]):
    """A-18: NER(新規API呼出)の前にSTOPセンチネル(<run>/STOP・STOP_ALL・restart-storm marker)を確認する。ある場合はNERせず縮退(表なし=現行)。"""
    try:
        import er062_family_z_structure_01 as zst
        return zst.stop_sentinel_hit(run_dir)
    except Exception:  # noqa: BLE001
        return None


def default_llm(*, timeout: float = 60.0) -> Optional[Callable]:
    """本番NER callable(text, prompt_id)->{"entities":[...],"usage":{...}}。cost logger未init・API key無しならNone(=縮退、API 0)。
    設定不備[cost logger未init/単価未登録]は呼出時にRuntimeErrorとして伝播する(握りつぶさない、A-2)。"""
    import er005_cost_logger as cl
    if cl._LOG_PATH is None:
        return None
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:  # noqa: BLE001
        pass

    def call(text: str, prompt_id: str) -> dict:
        from openai import OpenAI
        client = OpenAI(timeout=timeout)
        t0 = time.time()
        with cl.segment_context("ret_entity_ner_%s" % prompt_id):
            r = client.responses.create(model=MODEL, reasoning={"effort": "low"}, text={"format": {"type": "json_schema", **SCHEMA}},
                                        input=[{"role": "developer", "content": PROMPTS[prompt_id]}, {"role": "user", "content": text}])
        u = r.usage
        jpy = (u.input_tokens * PRICE_IN + u.output_tokens * PRICE_OUT) / 1e6 * USD_JPY
        data = json.loads(r.output_text)
        return {"entities": list(data.get("entities") or []),
                "usage": {"model": getattr(r, "model", MODEL), "in": u.input_tokens, "out": u.output_tokens, "jpy_est": round(jpy, 5), "sec": round(time.time() - t0, 2), "prompt": prompt_id}}
    return call


def _is_config_stop(exc: BaseException) -> bool:
    import er078_asr_unified_judge_01 as uj
    return uj.is_config_stop_error(exc)


# ---------------------------------------------------------------- 構築(hookから1回)
def ensure_table(provider, *, llm: Optional[Callable] = None, cmu_has: Callable = pol._default_cmu_has, zipf: Callable = pol._default_zipf,
                 use_default_llm: bool = True) -> EntityTable:
    """provider(collect()->(segs, declared)・table_path・run_dir)から、このrunの実体表を返す。例外は投げない(設定不備[cost logger/単価]とBaseException[STOP]を除く)。
    保存済みrawの再利用: builder_version一致のとき、未カバーtext(coverage=text sha)のみNERしrawへ和集合(entryは減らない)。全text既カバー=NER 0 call(W-03/W-09)。
    判定用のentryは毎回「今のsegs」の和集合に対し決定論(API 0)で導出し直す。"""
    status = "OK"
    meta = {"model": MODEL, "builder_version": builder_version(), "rules_version": rules_version(), "built_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "usage": [], "calls": 0, "table_path": getattr(provider, "table_path", None)}
    try:
        segs, declared = provider.collect()
    except Exception as exc:  # noqa: BLE001
        t = EntityTable([], status="PROVIDER_ERROR", meta={**meta, "error": "%s: %s" % (type(exc).__name__, str(exc)[:200])})
        return t
    segs = [s for s in segs if s.text and s.text.strip()]
    path = getattr(provider, "table_path", None)
    saved = load_saved(path) if path else None
    bv = builder_version()
    if saved and saved.get("builder_version") != bv:
        meta["discarded_saved_builder_version"] = saved.get("builder_version")
        saved = None
    raw = _union_raw(saved["raw"], empty_raw()) if saved else empty_raw()
    covered = set(saved.get("covered_text_sha256") or []) if saved else set()
    covered_b = set(saved.get("covered_b_text_sha256") or []) if saved else set()
    builds = list(saved.get("builds") or []) if saved else []
    changed = False
    if declared:
        before = len(raw["declared"])
        raw = _union_raw(raw, {"declared": list(declared)})
        changed = changed or len(raw["declared"]) != before

    by_sha = {}
    for s in segs:
        by_sha.setdefault(text_sha(s.text), s)
    uncovered = [s for sha, s in by_sha.items() if sha not in covered]
    run_dir = getattr(provider, "run_dir", None)
    calls = 0

    def _llm():
        nonlocal llm
        if llm is None and use_default_llm:
            llm = default_llm()
        return llm

    ner_ok_shas: list = []
    ner_dropped: list = []          # NER時の検証で捨てた候補(幻覚/長句/見出し/カテゴリ不正)。operator報告用(rawには入れない)
    if uncovered:
        hit = _stop_hit(run_dir)
        if hit:
            status = "STOP_SENTINEL_NER_SKIPPED"
            meta["stop_sentinel"] = str(hit)
        elif _llm() is None:
            status = "LLM_NOT_CONFIGURED"
        else:
            union = "\n\n".join(s.text.strip() for s in uncovered)[:MAX_INPUT_CHARS]
            try:
                r = _llm()(union, "A")
                calls += 1
                if r.get("usage"):
                    meta["usage"].append(r["usage"])
                items = _merge_initials(list(r.get("entities") or []), _check_texts(uncovered))
                good = _verify_items(items, _check_texts(uncovered), _headings(_check_texts(uncovered)), ner_dropped)
                raw = _union_raw(raw, {"llm_a": [{"surface": sf, "category": cat} for (sf, cat, _k) in good]})
                ner_ok_shas = [text_sha(s.text) for s in uncovered]
                covered |= set(ner_ok_shas)
                changed = True
                if not items:
                    meta["llm_empty_response"] = True
            except Exception as ex:  # noqa: BLE001  設定不備のみ伝播。それ以外は縮退(coverageに入れず次回再試行、W-09)
                if _is_config_stop(ex):
                    raise
                status = "LLM_UNAVAILABLE"
                meta["llm_error"] = "%s: %s" % (type(ex).__name__, str(ex)[:200])

    entries, dmeta, pending = derive_entries(raw, segs, cmu_has=cmu_has, zipf=zipf)
    cur_shas = set(by_sha)
    if pending and status in ("OK",) and calls < MAX_NER_CALLS_PER_BUILD and not cur_shas <= covered_b and _llm() is not None and not _stop_hit(run_dir):
        union_all = "\n\n".join(s.text.strip() for s in by_sha.values())[:MAX_INPUT_CHARS]
        try:
            r2 = _llm()(union_all, "B")
            calls += 1
            if r2.get("usage"):
                meta["usage"].append(r2["usage"])
            items2 = _merge_initials(list(r2.get("entities") or []), _check_texts(segs))
            good2 = _verify_items(items2, _check_texts(segs), _headings(_check_texts(segs)), ner_dropped)
            raw = _union_raw(raw, {"llm_b": [{"surface": sf, "category": cat} for (sf, cat, _k) in good2]})
            covered_b |= cur_shas
            changed = True
            entries, dmeta, pending = derive_entries(raw, segs, cmu_has=cmu_has, zipf=zipf)
        except Exception as ex:  # noqa: BLE001
            if _is_config_stop(ex):
                raise
            meta["llm_b_error"] = "%s: %s" % (type(ex).__name__, str(ex)[:200])
            status = "PARTIAL_NO_CALL2"
    meta.update(dmeta)
    meta["dropped"] = ner_dropped + list(dmeta.get("dropped") or [])
    meta["calls"] = calls
    meta["n_segments"] = len(segs)
    meta["n_uncovered_before"] = len(uncovered)
    meta["pending_independent_support"] = pending
    meta["covered_all_current"] = cur_shas <= covered
    table = EntityTable(entries, status=status, meta=meta)
    meta = table.meta               # EntityTableはmetaをcopyするため、以降の追記は表側のmetaへ

    if path and changed:
        builds.append({"at": meta["built_at"], "status": status, "calls": calls, "uncovered": len(uncovered), "usage": meta["usage"]})
        doc = {"schema": SCHEMA_VERSION, "builder_version": bv, "rules_version": rules_version(), "status": status, "model": MODEL, "raw": raw,
               "covered_text_sha256": sorted(covered), "covered_b_text_sha256": sorted(covered_b), "builds": builds,
               "derived_snapshot": {"note": "監査用。判定には使わない(毎回rawから導出)", "sha256": table.sha256(), "entries": [e.to_dict() for e in entries]}}
        try:
            meta["saved"] = _save(path, doc)
        except Exception as ex:  # noqa: BLE001
            meta["saved"] = False
            meta["save_error"] = "%s: %s" % (type(ex).__name__, str(ex)[:200])
    return table


def ensure_table_safe(provider, **kw) -> Optional[EntityTable]:
    """hook用: 構築失敗でrunを止めない(設定不備RuntimeError・BaseExceptionは伝播)。失敗=None(表なし=現行)。"""
    try:
        return ensure_table(provider, **kw)
    except RuntimeError as ex:
        if _is_config_stop(ex):
            raise
        return None
    except Exception:  # noqa: BLE001
        return None


# ---------------------------------------------------------------- providers(X/Z)
class XProvider:
    """Family X: `<theme_out_dir>/{b1b,a2}/parts.json`+support textsから、TTSへ渡るEN script(topic_intro/preview/comment_1-4/full_story_part1-3/in_one_line)を集める。
    両levelの入力が存在すれば1回のNERにまとめる(Std/Adv統合、OF-PN2-10)。Std(a2)のpreview/commentは日本語のため除外。KP/japanese_titleは対象外。"""

    def __init__(self, theme_out_dir: str):
        self.run_dir = theme_out_dir
        self.table_path = f"{theme_out_dir}/audit/entity_table.json"

    def collect(self) -> tuple:
        import er003_v1_n3_01_tts_generate as n3
        segs: list = []

        def rj(p):
            with open(p, encoding="utf-8") as f:
                return json.load(f)
        for lvl, support_name in (("b1b", "b1_support_texts.json"), ("a2", "a2_support_texts.json")):
            pj = f"{self.run_dir}/{lvl}/parts.json"
            if not os.path.exists(pj):
                continue
            parts = rj(pj)
            topics = []
            if parts.get("title"):
                topics.append(f"Today's topic is {parts['title']}.")
            if lvl == "a2" and parts.get("title_tts") and parts.get("title_tts") != parts.get("title"):
                topics.append(f"Today's topic is {parts['title_tts']}.")
            for txt in topics:
                segs.append(Seg(text=txt, role="TOPIC_INTRO", segment_id=f"{lvl}:topic_intro", alt_texts=(n3.tts_safe_number_words_en(n3.tts_safe_en(txt)),)))
            sp = f"{self.run_dir}/{lvl}/{support_name}"
            if lvl == "b1b" and os.path.exists(sp):
                support = rj(sp)
                for name in ("preview", "comment_1", "comment_2", "comment_3", "comment_4"):
                    txt = support.get(name)
                    if txt:
                        role = "PREVIEW" if name == "preview" else "COMMENT"
                        segs.append(Seg(text=txt, role=role, segment_id=f"{lvl}:{name}", alt_texts=(n3.tts_safe_number_words_en(n3.tts_safe_en(txt)),)))
            for name in ("part1", "part2", "part3", "in_one_line"):
                txt = parts.get(name)
                if txt:
                    sid = {"part1": "full_story_part1", "part2": "full_story_part2", "part3": "full_story_part3"}.get(name, name)
                    role = "IN_ONE_LINE" if name == "in_one_line" else "FULL_STORY"
                    segs.append(Seg(text=txt, role=role, segment_id=f"{lvl}:{sid}", alt_texts=(n3.tts_safe_news_en(txt),)))
        return segs, []


class ZProvider:
    """Family Z: `plan`(ClipSpec列)の英語script(narrator/dialogue/preview/comment/topic_intro、KP/japanese_title除外)。
    他levelの脚本(`segment_plan_<level>.json`と`support/<level>_support.json`の英語分)が揃っていれば和集合に加える(W-03、best effort)。"""

    _EN_KINDS = ("narrator", "dialogue", "preview", "comment", "topic_intro")

    def __init__(self, run_dir: str, level: str, plan: list):
        self.run_dir = run_dir
        self.level = level
        self.plan = plan
        self.table_path = f"{run_dir}/audit/entity_table.json"

    def collect(self) -> tuple:
        import er003_v1_n3_01_tts_generate as n3
        import er020_tts_retry_local_rewrite_01 as rw
        segs: list = []
        ja = re.compile(r"[぀-ヿ㐀-䶿一-鿿]")
        for sp in self.plan:
            if getattr(sp, "kind", None) not in self._EN_KINDS or getattr(sp, "language", "en") != "en" or ja.search(sp.text or ""):
                continue
            role = rw.resolve_narrative_role(sp.clip_id)
            if sp.kind in ("narrator", "dialogue"):
                alt = n3.tts_safe_news_en(sp.text)
            else:
                alt = n3.tts_safe_number_words_en(n3.tts_safe_en(sp.text))
            segs.append(Seg(text=sp.text, role=role, segment_id=f"{self.level}:{sp.clip_id}", alt_texts=(alt,)))
        other = "a2" if self.level == "b1b" else "b1b"
        try:
            pj = f"{self.run_dir}/segment_plan_{other}.json"
            if os.path.exists(pj):
                with open(pj, encoding="utf-8") as f:
                    for c in (json.load(f).get("clips") or []):
                        t = c.get("text")
                        if t and not ja.search(t):
                            segs.append(Seg(text=t, role="FULL_STORY", segment_id=f"{other}:{c.get('id')}", alt_texts=(n3.tts_safe_news_en(t),)))
            sj = f"{self.run_dir}/support/{other}_support.json"
            if os.path.exists(sj):
                with open(sj, encoding="utf-8") as f:
                    sup = json.load(f)
                if isinstance(sup.get("preview"), str) and not ja.search(sup["preview"]):
                    segs.append(Seg(text=sup["preview"], role="PREVIEW", segment_id=f"{other}:preview"))
                for k, t in (sup.get("comments") or {}).items():
                    if isinstance(t, str) and not ja.search(t):
                        segs.append(Seg(text=t, role="COMMENT", segment_id=f"{other}:comment_{k}"))
        except Exception:  # noqa: BLE001  他level脚本は補助(読めなくても当該levelだけで構築)
            pass
        return segs, []


# ---------------------------------------------------------------- operator report(A-16)
def operator_report_lines(table: Optional[EntityTable]) -> list:
    """運営者向けの実体表サマリ。未構築/縮退は明記する(SC-6)。表の根拠とPerplexity根拠(発音の根拠)は別欄(W-13)。"""
    if table is None:
        return ["実体表: 未構築または縮退(表なし)。固有名詞の認識は現行(Ledger/CMU未収録/文中大文字)のみで行われました。"]
    lines = []
    if table.status != "OK":
        lines.append("実体表: 未構築または縮退(status=%s)。固有名詞の認識は現行(Ledger/CMU未収録/文中大文字)のみで行われた部分があります。" % table.status)
    if table.meta.get("llm_empty_response"):
        lines.append("実体表: LLM応答が空(固有名詞なしの本文の可能性もあります。現行の証拠のみで判定)。")
    cnt: dict = {}
    for e in table.entries:
        cnt.setdefault((e.category, e.grade), 0)
        cnt[(e.category, e.grade)] += 1
    lines.append("実体表: %d件(うち証拠として使用可 %d件) / NER call=%s / model=%s / table_sha256=%s" % (
        len(table.entries), len(table.usable_entries()), table.meta.get("calls"), table.meta.get("model"), table.sha256()[:12]))
    for (c, g), n in sorted(cnt.items()):
        lines.append("実体表 %s/%s: %d件" % (c, g, n))
    weak = [e.surface for e in table.entries if not e.usable]
    if weak:
        lines.append("証拠にならなかった語(weak/一般語等): %s" % ", ".join(weak[:30]))
    dr = table.meta.get("dropped") or []
    if dr:
        lines.append("除外された候補: %s" % ", ".join("%s[%s]" % (d["surface"], d["reason"]) for d in dr[:30]))
    return lines
