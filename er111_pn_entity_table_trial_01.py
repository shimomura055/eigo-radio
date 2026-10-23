# -*- coding: utf-8 -*-
"""ASR-QUALITY-2ITEMS-COMPREHENSIVE-01 PN 委任_02: Run Entity Table(RET) Trial実装 [DEV/Trial専用・Production未配線・承認前・既定OFF相当]

固有名詞の「認識」の正本を run 単位の“本文実体表”として作る。受理境界(類似度>=0.40・一般語ブロック・P-03・G3・数値/否定/脱落・KP/JA除外)は
er103_proper_noun_alarm_policy_01 のものをそのまま使う(本moduleは**証拠の供給源**を足すだけ)。

位置づけ(厳守):
  * import方向は Trial -> Production(読取のみ)。er103/er006/er019/val/runner は本moduleを import しない(AST testで固定)。
  * 11-7 flag は作らない。Production経路から暗黙参照されない(`current_table()` は本module内のprocess内状態で、er103は見ない)。
  * Opus条件Aレビュー(OPUS_REVIEW_01.md) OF-PN2-01〜10 を反映(DESIGN_02.md の差分表)。
    OF-01 証拠は「実体の出現位置」に紐づける(語集合=bagにしない)。OF-03 独立裏付けなしの entry は2回目の独立callの一致が必要。
    OF-04 CMU収録tokenに証拠を付けるカテゴリは person/place/organization/brand_product のみ(work_title/other_named はCMU未収録tokenのみ)。
    OF-05 入力は実際にTTSへ渡るsegment canonical textの和集合。逐語検証は供給前後の両textで。
    OF-06 受理に使った実体entryを保存し、再判定はそのsegment textへの逐語出現のみ確認(LLMを呼ばない)。LRでは表を減らさない。
LLM失敗時は status=LLM_UNAVAILABLE(宣言entryのみ)=現行同等へ縮退。例外を投げない。
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import time
import unicodedata
from contextlib import contextmanager
from dataclasses import dataclass, field, asdict
from typing import Callable, Iterable, Optional

import er103_proper_noun_alarm_policy_01 as pol   # 読取のみ(Production module)

TRIAL_ID = "ASR-QUALITY-2ITEMS-COMPREHENSIVE-01-PN-TRIAL"
SCHEMA_VERSION = "ret_trial_02"
MODEL = "gpt-6-luna"
PRICE_IN, PRICE_OUT, USD_JPY = 0.10, 0.50, 160.0   # per 1M tokens (er006_model_routing_pricing_coverage_test_01.py:50-52) -- NER probe と同じ出典
COST_CAP_JPY = 30.0
COST_GUARD_JPY = 29.0          # これを超える見込みで新規callを止める

CATEGORIES = ("person", "place", "organization", "work_title", "brand_product", "other_named")
# OF-PN2-04: CMU収録tokenに表証拠を付けてよいカテゴリ。work_title/other_named は CMU未収録(OOV)tokenのみ。
CMU_OK_CATEGORIES = frozenset({"person", "place", "organization", "brand_product"})
MAX_ENTITY_WORDS = 5           # 題名/長句除外
GRADE_DECLARED, GRADE_CONFIRMED, GRADE_WEAK = "declared", "confirmed", "weak"
USABLE_GRADES = frozenset({GRADE_DECLARED, GRADE_CONFIRMED})

PROMPT_A = ("You list the proper nouns (named entities) in an English radio script, for a text-to-speech pronunciation QA step. "
            "Include: people (first names, surnames, nicknames, names inside quotations or song lyrics, names that start a sentence), places, organizations/media, "
            "titles of works, brands/products, other named things. Do NOT list ordinary words just because they are capitalized at the start of a sentence or heading, "
            "months/weekdays, nationality adjectives, or generic nouns. Give each entity once, with the exact surface form (multi-word names as one entity, e.g. 'Stephen Reicher'). "
            "Category is one of: person, place, organization, work_title, brand_product, other_named.")
# 2回目の独立call用(OF-PN2-03): 文言・枠組みを変える(1回目の出力は見せない)。
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
# 隣接する実体どうしの連結(RET-3)で許す区切り: 空白/ハイフン/アポストロフィに加え、語を含まない句読点(カンマ・セミコロン)。
# 「区切り語(and/the/of等の語)が間に無い」ことを要件とする(OF-PN2-02(i)の解釈。語が挟まる場合は連結しない)。
_RUN_GAP_RE = re.compile(r"^[\s,;\-'’]*$")


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
    t = t.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').replace(" ", " ")
    return re.sub(r"\s+", " ", t)


def _gap_ok(text: str, a: W, b: W) -> bool:
    gap = text[a.end:b.start]
    if _BENIGN_GAP_RE.match(gap):
        return True
    # 単独イニシャル(L. Mimoun)のピリオドのみ許容
    return len(a.fold) == 1 and re.match(r"^\.\s*$", gap) is not None


def _is_initial_token(orig_surface_words: list, i: int, surface: str) -> bool:
    w = orig_surface_words[i]
    return len(w.fold) == 1 and w.orig[:1].isupper() and len(orig_surface_words) >= 2


# ---------------------------------------------------------------- 実体表
@dataclass
class Entry:
    surface: str
    words: list                 # fold語列
    category: str
    grade: str
    sources: list               # ["declared:<src>", "llm_a", "llm_b", "det:<label>"]
    eligible: list              # 証拠を付与してよい token(非一般語・カテゴリ規則適合・小文字形なし)
    initials: list              # 実体内部イニシャル token
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
    """run単位の実体表。`entries`のうち usable(declared/confirmed ∧ eligible token有)だけが証拠源になる。"""

    def __init__(self, entries: Optional[list] = None, *, status: str = "OK", meta: Optional[dict] = None, general_in_phrase: bool = False):
        # general_in_phrase=False: OF-PN2-01(i) 文言どおり、表が証拠を付けるのは eligible token(非一般語)と内部イニシャルのみ。
        # True: 実体出現範囲に**全体が含まれる**句で、かつ eligible token を1つ以上含む場合に限り、同じ実体内の一般語tokenにも位置紐づけで証拠を付与する
        #       (例 "Stephen Reicher" の stephen[文頭]。bagではなく位置紐づけ。ablation用、採否は評価で決める)。
        self.general_in_phrase = bool(general_in_phrase)
        self.entries: list = list(entries or [])
        self.status = status
        self.meta: dict = dict(meta or {})

    # ---- 保存/復元(OF-PN2-06: 受理に使ったentryを保存し、再判定はLLMを呼ばずに逐語出現だけ確認)
    def to_dict(self) -> dict:
        return {"schema": SCHEMA_VERSION, "status": self.status, "sha256": self.sha256(), "meta": self.meta,
                "entries": [e.to_dict() for e in self.entries]}

    @staticmethod
    def from_dict(d: dict) -> "EntityTable":
        return EntityTable([Entry.from_dict(x) for x in d.get("entries", [])], status=d.get("status", "OK"), meta=d.get("meta"))

    def sha256(self) -> str:
        body = json.dumps([[e.surface, e.words, e.category, e.grade, e.eligible, e.initials] for e in self.entries], ensure_ascii=False, sort_keys=True)
        return hashlib.sha256(body.encode("utf-8")).hexdigest()

    def usable_entries(self) -> list:
        return [e for e in self.entries if e.usable]

    def is_empty(self) -> bool:
        return not self.usable_entries()

    # ---- 出現位置(OF-PN2-01: 証拠は語集合でなく、このsegment text内の実体出現範囲に紐づける)
    def occurrences(self, text: str, ws: Optional[list] = None) -> list:
        """[(word_start_idx, word_end_idx_inclusive, entry)]。eligible/initial tokenに当たる語は大文字始まりであること(大文字一貫性)。"""
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
            if self.general_in_phrase and (set(e.eligible) & set(phrase_tokens)):
                grant |= set(e.words) & set(phrase_tokens)
        if not grant:
            return frozenset(), {"reason": "no_eligible_token_in_phrase"}
        seen, ent = set(), []
        for e in used:
            if e.surface not in seen:
                seen.add(e.surface)
                ent.append({"surface": e.surface, "words": e.words, "category": e.category, "grade": e.grade, "eligible": e.eligible, "initials": e.initials})
        return frozenset(grant), {"entities": ent, "grant": sorted(grant)}

    def entity_run_for_span(self, text: str, span_tokens: list) -> Optional[dict]:
        """RET-3(OF-PN2-02): Secondary span が「当該位置で連続する1実体出現(または区切り語なし隣接複数実体)」とtoken単位で一致するか。
        所有格 's が末尾に付くのは許容。一致しなければ None。"""
        ws = words(text)
        occs = sorted(self.occurrences(text, ws), key=lambda x: (x[0], x[1]))
        poss = self._phrase_positions(ws, list(span_tokens))
        if not poss or not occs:
            return None
        results = []
        for (a, b) in poss:
            # a..b を実体出現の隣接連結(区切り語なし)で過不足なく埋められるか
            def dfs(pos: int, chain: list):
                if pos == b + 1:
                    return chain
                for (oa, ob, e) in occs:
                    if oa == pos and ob <= b:
                        r = dfs(ob + 1, chain + [(oa, ob, e)])
                        if r is not None:
                            return r
                # 末尾の所有格 's
                if pos == b and ws[pos].fold == "s" and chain and ws[pos].start - ws[pos - 1].end <= 2:
                    return chain
                return None
            chain = dfs(a, [])
            if chain is None:
                return None          # 1出現でも不一致なら不許可(保守側)
            # 連結する隣接実体間の区切り(語無し)を確認: 隣接はgapが空白/ハイフン/アポストロフィのみ
            for (x, y) in zip(chain, chain[1:]):
                if not (_gap_ok(text, ws[x[1]], ws[y[0]]) or _RUN_GAP_RE.match(text[ws[x[1]].end:ws[y[0]].start])):
                    return None
            results.append((a, b, chain))
        grant = set()
        ents = []
        for (a, b, chain) in results:
            for (_, _, e) in chain:
                grant |= (set(e.eligible) | set(e.initials)) & set(span_tokens)
                if self.general_in_phrase and (set(e.eligible) & set(span_tokens)):
                    grant |= set(e.words) & set(span_tokens)
                ents.append({"surface": e.surface, "words": e.words, "category": e.category, "grade": e.grade})
        if not grant:
            return None
        return {"span": list(span_tokens), "positions": [(a, b) for (a, b, _) in results], "grant": frozenset(grant), "entities": ents}

    def phrase_positions(self, text: str, phrase_tokens: list) -> list:
        return self._phrase_positions(words(text), list(phrase_tokens))


# ---------------------------------------------------------------- run単位保持(process内状態。_RUN_SCOPE と同型、finallyで必ず解除)
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


# ---------------------------------------------------------------- LLM NER(gpt-6-luna、gpt-6 Responses API、strict JSON)
class CostCapExceeded(RuntimeError):
    pass


def spend_so_far(usage_log: str) -> float:
    if not usage_log or not os.path.exists(usage_log):
        return 0.0
    tot = 0.0
    with open(usage_log, encoding="utf-8") as fh:
        for l in fh:
            l = l.strip()
            if l:
                try:
                    tot += float(json.loads(l).get("jpy", 0.0))
                except Exception:
                    pass
    return tot


def llm_ner_real(text: str, prompt_id: str, *, usage_log: Optional[str] = None, tag: str = "", timeout: float = 60.0) -> dict:
    """実API(gpt-6-luna)。戻り値={"entities":[{surface,category}], "usage":{in,out,jpy,sec,model}}。失敗時は例外(呼び側がLLM_UNAVAILABLE化)。"""
    if usage_log and spend_so_far(usage_log) >= COST_GUARD_JPY:
        raise CostCapExceeded("cost guard %.2f JPY reached" % spend_so_far(usage_log))
    from dotenv import load_dotenv
    load_dotenv()
    from openai import OpenAI
    client = OpenAI(timeout=timeout)
    t0 = time.time()
    r = client.responses.create(model=MODEL, reasoning={"effort": "low"}, text={"format": {"type": "json_schema", **SCHEMA}},
                                input=[{"role": "developer", "content": PROMPTS[prompt_id]}, {"role": "user", "content": text}])
    sec = time.time() - t0
    u = r.usage
    jpy = (u.input_tokens * PRICE_IN + u.output_tokens * PRICE_OUT) / 1e6 * USD_JPY
    usage = {"model": getattr(r, "model", MODEL), "in": u.input_tokens, "out": u.output_tokens, "jpy": round(jpy, 5), "sec": round(sec, 2), "prompt": prompt_id, "tag": tag}
    if usage_log:
        with open(usage_log, "a", encoding="utf-8") as f:
            f.write(json.dumps({"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), **usage}, ensure_ascii=False) + "\n")
    data = json.loads(r.output_text)
    return {"entities": list(data.get("entities") or []), "usage": usage}


# ---------------------------------------------------------------- 構築
@dataclass
class Seg:
    text: str                       # 実際にTTSへ渡る canonical text(供給後)
    role: Optional[str] = "FULL_STORY"
    pre_text: Optional[str] = None  # 供給前text(逐語検証は両方で行う、OF-PN2-05)
    segment_id: str = ""


def _as_seg(x) -> Seg:
    return x if isinstance(x, Seg) else Seg(text=str(x))


def _token_class(tok: str, category: str, *, lowercase_seen: set, cmu_has: Callable, zipf: Callable) -> tuple:
    """token 1語が証拠付与対象か。戻り値=(eligible bool, reason)。"""
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
    """既存の決定論証拠(OOV/ALLCAPS/文中大文字。er103 proper_noun_evidence をそのまま使用)が、いずれかのsegmentで成立するか。独立裏付け(OF-PN2-03)。"""
    for sg in segs:
        ok, lab = pol.proper_noun_evidence(tok, sg.text, ledger_surfaces=frozenset(), cmu_has=cmu_has, role=sg.role)
        if ok:
            return lab
    return None


_INITIAL_ONLY_RE = re.compile(r"^[A-Z]\.?$")


def _merge_initials(items: list, texts: list) -> list:
    """LLMが「L.」と「Mimoun」を別entityに分けた場合に、本文の `L. Mimoun` を1実体として復元する(裸のイニシャルentityは捨てる)。決定論・API 0。"""
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


def build_entity_table(segments: Iterable, *, declared: Iterable = (), llm: Optional[Callable] = None, usage_log: Optional[str] = None,
                       cmu_has: Callable = pol._default_cmu_has, zipf: Callable = pol._default_zipf, tag: str = "",
                       allow_call2: bool = True) -> EntityTable:
    """実体表を構築する。例外は投げない(失敗は status に反映して縮退)。
    segments: Seg または str の列(TTSへ渡る canonical text の和集合になるよう、呼び側が対象role[KP/JA/HEADING除外]を渡す)。
    declared: [{"name","category"(任意),"source"}] (Z Seed key_roles等。R2)。llm: callable(text, prompt_id)->{"entities":[...],"usage":{...}}。"""
    segs = [_as_seg(s) for s in segments]
    meta = {"trial_id": TRIAL_ID, "model": MODEL, "wordfreq_version": _wf_version(), "n_segments": len(segs),
            "text_sha256": hashlib.sha256("\n".join(s.text for s in segs).encode("utf-8")).hexdigest(), "usage": [], "dropped": [], "tag": tag,
            "blocked_general_person_place": [], "built_at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    texts = [s.text for s in segs]
    check_texts = texts + [s.pre_text for s in segs if s.pre_text]          # 逐語検証は供給前後の両text
    union = "\n\n".join(dict.fromkeys(t.strip() for t in texts if t and t.strip()))
    lower_seen = _lowercase_forms(check_texts)
    heads = _headings(check_texts)
    status = "OK"
    entries: dict = {}                    # key=tuple(words) -> Entry

    def _mk(surface: str, category: str, grade: str, src: str) -> Optional[Entry]:
        ws = words(surface)
        toks = [w.fold for w in ws]
        if not toks:
            meta["dropped"].append({"surface": surface, "reason": "no_alpha_token"})
            return None
        elig, inits, notes = [], [], []
        for i, w in enumerate(ws):
            if len(w.fold) == 1 and w.orig[:1].isupper() and len(ws) >= 2:
                inits.append(w.fold)
                continue
            ok, why = _token_class(w.fold, category, lowercase_seen=lower_seen, cmu_has=cmu_has, zipf=zipf)
            if ok:
                elig.append(w.fold)
            else:
                notes.append("%s:%s" % (w.fold, why))
        if not elig:
            inits = []                    # 非一般語tokenが無ければ実体全体として証拠なし(イニシャルだけを証拠にしない)
        return Entry(surface=surface, words=toks, category=category, grade=grade, sources=[src], eligible=sorted(set(elig)), initials=sorted(set(inits)), notes=notes)

    # R2 宣言済み実体
    for d in declared or ():
        nm = (d.get("name") if isinstance(d, dict) else str(d)) or ""
        cat = (d.get("category") if isinstance(d, dict) else None) or "person"
        src = "declared:%s" % ((d.get("source") if isinstance(d, dict) else None) or "seed")
        if cat not in CATEGORIES:
            cat = "person"
        if not _verbatim_in(nm, check_texts):
            meta["dropped"].append({"surface": nm, "reason": "declared_not_in_text"})
            continue
        e = _mk(nm, cat, GRADE_DECLARED, src)
        if e is not None:
            entries[tuple(e.words)] = e

    # R3 LLM NER (call 1)
    llm_a: list = []
    if llm is not None and union.strip():
        try:
            r = llm(union, "A")
            llm_a = list(r.get("entities") or [])
            if r.get("usage"):
                meta["usage"].append(r["usage"])
        except Exception as ex:                                     # noqa: BLE001  -- 例外を投げない。縮退して制作を止めない
            status = "LLM_UNAVAILABLE"
            meta["llm_error"] = "%s: %s" % (type(ex).__name__, str(ex)[:200])
    elif llm is None:
        status = "LLM_NOT_CONFIGURED"

    def _verify_llm(items: list, src: str) -> list:
        out = []
        seen = set()
        for it in items:
            if not isinstance(it, dict):
                meta["dropped"].append({"surface": str(it)[:60], "reason": "bad_item"})
                continue
            sf, cat = it.get("surface"), it.get("category")
            if not isinstance(sf, str) or not sf.strip():
                meta["dropped"].append({"surface": str(sf)[:60], "reason": "bad_surface"})
                continue
            sf = sf.strip()
            if cat not in CATEGORIES:
                meta["dropped"].append({"surface": sf, "reason": "bad_category"})
                continue
            if not _verbatim_in(sf, check_texts):                  # 幻覚除去
                meta["dropped"].append({"surface": sf, "reason": "not_verbatim"})
                continue
            if len(sf.split()) > MAX_ENTITY_WORDS:
                meta["dropped"].append({"surface": sf, "reason": "long_phrase"})
                continue
            if nq(sf).strip(" *_") in heads:
                meta["dropped"].append({"surface": sf, "reason": "heading_or_title_line"})
                continue
            key = tuple(w.fold for w in words(sf))
            if not key or key in seen:
                continue
            seen.add(key)
            out.append((sf, cat, key))
        return out

    llm_a = _merge_initials(llm_a, check_texts)
    if llm is not None and status == "OK" and union.strip() and not llm_a:
        meta["llm_empty_response"] = True            # 空応答(固有名詞なしの本文の可能性もある。operator reportに明記)
    ver_a = _verify_llm(llm_a, "llm_a")
    cand: list = []
    for (sf, cat, key) in ver_a:
        if key in entries:
            entries[key].sources.append("llm_a")
            continue
        e = _mk(sf, cat, GRADE_WEAK, "llm_a")
        if e is None:
            continue
        cand.append(e)

    # 独立裏付け(OF-PN2-03): 既存決定論証拠(OOV/ALLCAPS/文中大文字)が eligible token で成立するか
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
    # 2回目の独立call(必要なentryがあるときだけ)
    b_map = {}
    if need_call2 and llm is not None and allow_call2 and status != "LLM_UNAVAILABLE":
        try:
            r2 = llm(union, "B")
            if r2.get("usage"):
                meta["usage"].append(r2["usage"])
            for (sf, cat, key) in _verify_llm(_merge_initials(list(r2.get("entities") or []), check_texts), "llm_b"):
                b_map[key] = cat
        except Exception as ex:                                     # noqa: BLE001
            meta["llm_b_error"] = "%s: %s" % (type(ex).__name__, str(ex)[:200])
            status = "PARTIAL_NO_CALL2" if status == "OK" else status
    for e in need_call2:
        agree = None
        exact = False
        if tuple(e.words) in b_map:                      # 同じ語列のentityがcall Bにもある(カテゴリも比較する)
            agree, exact = b_map[tuple(e.words)], True
        else:                                            # call Bがより長いspan(例 歌詞行 "Bertie, why do you bound?")の一部として挙げた場合は存在の一致のみ(カテゴリは比較しない)
            for key, cat_b in b_map.items():
                if any(t in key for t in e.eligible):
                    agree = cat_b
                    break
        if agree is not None:
            if exact and agree in ("work_title", "other_named") and e.category in CMU_OK_CATEGORIES:
                e.category = agree                                   # 2回の判定が割れたら厳しい側のカテゴリへ(OF-04)
                e2 = _mk(e.surface, e.category, GRADE_CONFIRMED, "llm_a")
                if e2 is not None:
                    e.eligible, e.initials, e.notes = e2.eligible, e2.initials, e2.notes + ["category_downgraded_by_call2"]
            if e.eligible:
                e.grade = GRADE_CONFIRMED
                e.sources.append("llm_b_agree")
        else:
            e.notes.append("no_independent_support")
    for e in cand:
        entries.setdefault(tuple(e.words), e)
    # 既存entryと包含関係の重複(例 "Reicher" と "Stephen Reicher")は両方残す(出現範囲ごとに独立に判定される)
    return EntityTable(list(entries.values()), status=status, meta=meta)


def merge_for_local_rewrite(base: EntityTable, changed_segments: Iterable, **build_kw) -> EntityTable:
    """OF-PN2-06(ii): Local Rewrite では表を作り直さず、変更segmentのみNERして和集合に追加する(entryは減らない)。"""
    extra = build_entity_table(list(changed_segments), **build_kw)
    have = {tuple(e.words): e for e in base.entries}
    for e in extra.entries:
        k = tuple(e.words)
        if k not in have:
            have[k] = e
    meta = dict(base.meta)
    meta.setdefault("lr_merges", []).append({"sha256": extra.sha256(), "status": extra.status, "usage": extra.meta.get("usage")})
    return EntityTable(list(have.values()), status=base.status if base.status == "OK" else extra.status, meta=meta)


def table_from_saved_entries(entries: list) -> EntityTable:
    """OF-PN2-06(i): アラームblockに保存した実体entryから表を復元(表sha一致は不要。LLMを呼ばない)。
    再判定時は occurrences()/grant_for_phrase() が当該segment textへの逐語出現のみを確認する。"""
    return EntityTable([Entry.from_dict(x) for x in entries], status="RESTORED_FROM_ALARM")


def _wf_version() -> str:
    try:
        import importlib.metadata as m
        return m.version("wordfreq")
    except Exception:
        return "unknown"


def declared_from_z_seed(seed: dict) -> list:
    """R2: Z Seed `source_essentials.key_roles[].name` を宣言済み実体にする(Bertieのような宣言外の名前は拾えない=LLM NER側の役目)。"""
    out = []
    for r in ((seed or {}).get("source_essentials") or {}).get("key_roles") or []:
        nm = (r.get("name") or "").strip() if isinstance(r, dict) else ""
        if nm:
            out.append({"name": nm, "category": "person", "source": "seed.key_roles" + (".keep_name" if r.get("keep_name") else "")})
    return out


def operator_report_lines(table: EntityTable) -> list:
    """operator report(運営者向け)の実体表サマリ行。LLM未構築/縮退は明記する(SC-6)。表の件数をカテゴリ別に出し、weak/droppedも示す。"""
    lines = []
    if table.status != "OK":
        lines.append("実体表: 未構築または縮退(status=%s)。固有名詞の認識は現行(Ledger/CMU未収録/文中大文字)のみで行われました。" % table.status)
    if table.meta.get("llm_empty_response"):
        lines.append("実体表: LLM応答が空(固有名詞なしの本文の可能性もあります。現行の証拠のみで判定)。")
    cnt: dict = {}
    for e in table.entries:
        cnt.setdefault((e.category, e.grade), 0)
        cnt[(e.category, e.grade)] += 1
    for (c, g), n in sorted(cnt.items()):
        lines.append("実体表 %s/%s: %d件" % (c, g, n))
    weak = [e.surface for e in table.entries if not e.usable]
    if weak:
        lines.append("証拠にならなかった語(weak/一般語等): %s" % ", ".join(weak[:30]))
    dr = table.meta.get("dropped") or []
    if dr:
        lines.append("除外された候補: %s" % ", ".join("%s[%s]" % (d["surface"], d["reason"]) for d in dr[:30]))
    return lines
