# -*- coding: utf-8 -*-
"""ASR-M1-OOV-MULTI-PRONUNCIATION-PRODUCTION-01 委任_02: M1 複数発音候補方式の Production module(新規)。

状態: MODULE_IMPLEMENTED_PENDING_WIRING(配線は委任_03。本 module は既存 Production file から未 import)。
承認: 2026-10-13 ユーザー承認(複数の合理的発音候補のいずれか 1 つで音韻整合すれば PASS 可)。Opus 条件A レビュー OF-178〜187 反映。

設計の要点
  * 候補集合は canonical 側のみから segment の最初の試行前に 1 回だけ freeze_candidates() で作り、
    以降の判定関数へ「凍結オブジェクトを引数注入」する(OF-179)。判定側は Ledger/CMU の canonical 側候補を再計算しない。
  * 候補クラス: C1(CMU 全異読) / C2(Pronunciation Ledger の IPA、CMU 未収録語のみ・除外条件あり OF-181)。
    C3(綴りからの規則推定)・ASR 転写からの後付け候補は存在しない。
  * M1 は F1(er011_b1_connected_speech_validator_01.classify_connected_speech)の内側で動く:
    置換後の文で F1 を再実行し、残差 0 かつ、exact 以外の規則で置換した全位置が f1_explained(Pattern A/B/C)に含まれること
    (F1 の benign[規則単複]で吸収された置換は不受理、OF-178)。
  * 受理理由は M1_MULTI_CANDIDATE_ACCEPT(PASS_WITH_WARNING)。audit に ledger_key/updated_at/ipa_raw/candidate_set_hash/
    一致候補[出典クラス・confidence]/secondary_agree/no_match_reason を残し、ledger_key 別に事後集計できる(OF-187)。
本 module は Ledger を書かない(読取スナップショットのみ)。API 呼出なし。
"""
from __future__ import annotations

import collections
import copy
import datetime as _dt
import difflib
import hashlib
import itertools
import json
import re
from dataclasses import dataclass, field

M1_VERSION = "M1-MULTI-2026-10-13"
ACCEPT_REASON = "M1_MULTI_CANDIDATE_ACCEPT"
DEFAULT_MAX_PER_WORD = 6

# 不受理/不発理由(telemetry の列挙値)
R_DISABLED = "M1_DISABLED"
R_LANG = "LANG_NOT_EN_US"
R_NOT_UNCERTAIN = "BASE_CLASSIFICATION_NOT_UNCERTAIN"
R_PROTECTED_FAIL = "PROTECTED_CHECK_FAILED"
R_F1_CONTENT = "F1_RESIDUAL_CONTENT"
R_NO_FROZEN = "NO_FROZEN_CANDIDATES"
R_NO_FLAGGED = "NO_FLAGGED_DIFF"
R_NO_MATCH = "MULTI_CANDIDATE_NO_MATCH"
R_POST_RESIDUAL = "POST_REPLACEMENT_F1_RESIDUAL"
R_NOT_EXPLAINED = "SUBSTITUTION_NOT_F1_EXPLAINED"
R_SECONDARY_CONTRADICTION = "SECONDARY_CONTRADICTION"
R_SECONDARY_UNAVAILABLE = "SECONDARY_UNAVAILABLE"  # 予約(必須化しない=OF-183)

# no_match 理由別(OF-184: 直接音素置換の需要測定用 telemetry)
NM_NO_CANDIDATES = "no_candidates_for_canonical_word"
NM_ASR_NOT_IN_CMU = "asr_word_not_in_cmu"
NM_NO_PHONEME_MATCH = "no_phoneme_match_with_any_candidate"

_TOK = re.compile(r"[a-z0-9']+")
_SIB = ("S", "Z")
_OK_JUDGMENTS = ("CONNECTED_SPEECH_ACCEPT", "CONNECTED_SPEECH_RESEGMENTATION")


def _tokens(text: str) -> list:
    return _TOK.findall((text or "").lower().replace("’", "'"))


def _strip_stress(ph: str) -> str:
    return "".join(c for c in ph if not c.isdigit())


def default_cmu(word: str) -> list:
    """CMU 辞書(pronouncing)の全異読。ストレス除去済み音素列の tuple のリスト。未収録は []。"""
    import pronouncing
    return [tuple(_strip_stress(x) for x in e.split()) for e in pronouncing.phones_for_word(word.lower().strip("'"))]


# ---------------------------------------------------------------------------
# IPA -> ARPAbet 決定論表(委任_01 eval から移設)。変換不能な記号を含む発音は『候補不成立』。
# ---------------------------------------------------------------------------
IPA_TABLE = [
    ("tʃ", "CH"), ("t͡ʃ", "CH"), ("ʧ", "CH"), ("dʒ", "JH"), ("d͡ʒ", "JH"), ("ʤ", "JH"), ("t͡s", "T S"), ("ts", "T S"),
    ("aɪ", "AY"), ("aʊ", "AW"), ("eɪ", "EY"), ("oʊ", "OW"), ("əʊ", "OW"), ("ɔɪ", "OY"),
    ("ɜːr", "ER"), ("ɜr", "ER"), ("ɜː", "ER"), ("ɝ", "ER"), ("ɚ", "ER"), ("ər", "ER"),
    ("iː", "IY"), ("uː", "UW"), ("ɑː", "AA"), ("ɔː", "AO"), ("ɒ", "AA"), ("ɛ", "EH"), ("æ", "AE"), ("ɪ", "IH"), ("ʊ", "UH"),
    ("ʌ", "AH"), ("ə", "AH"), ("ɔ", "AO"), ("ɑ", "AA"), ("i", "IY"), ("u", "UW"),
    ("θ", "TH"), ("ð", "DH"), ("ʃ", "SH"), ("ʒ", "ZH"), ("ŋ", "NG"), ("j", "Y"), ("ɹ", "R"), ("r", "R"), ("l", "L"), ("m", "M"),
    ("n", "N"), ("p", "P"), ("b", "B"), ("t", "T"), ("d", "D"), ("k", "K"), ("ɡ", "G"), ("g", "G"), ("f", "F"), ("v", "V"),
    ("s", "S"), ("z", "Z"), ("h", "HH"), ("w", "W"),
]
_IPA_STRIP = re.compile(r"[ˈˌ.\s/\[\]²]")
_IPA_CHARS = re.compile(r"[ˈˌːɑɒæɛəɜɪʊʌɔθðʃʒŋɹɡɝɚ͡]")
_NON_ENGLISH_LABEL = re.compile(r"native|Swedish|Italian|French|German|Spanish|Japanese|Chinese|Korean|Russian|Greek", re.I)


def ipa_to_arpa(ipa: str):
    """決定論的 IPA→ARPAbet(ストレス除去)。未知記号があれば None(=候補不成立)。"""
    s = _IPA_STRIP.sub("", ipa or "")
    out, i = [], 0
    while i < len(s):
        for k, v in IPA_TABLE:
            if s.startswith(k, i):
                out.extend(v.split())
                i += len(k)
                break
        else:
            return None
    return tuple(out) if out else None


def _ipa_segments(raw: str):
    """Ledger 文字列から IPA らしき断片を (断片, 除外理由|None) で返す(綴り読みは IPA ではないので候補にしない=G2P 非新設)。"""
    raw = raw or ""
    segs = []
    for m in re.finditer(r"/([^/]+)/", raw):
        ctx = raw[max(0, m.start() - 24):m.start()]
        segs.append((m.group(1), "non_english_label" if _NON_ENGLISH_LABEL.search(ctx) else None))
    if not segs:
        m = re.search(r"\[([^\]]+)\]", raw)
        body = m.group(1) if m else raw.split("（")[0].split("(")[0]
        if _IPA_CHARS.search(body):
            segs.append((body.strip(), None))
    return segs


# ---------------------------------------------------------------------------
# 凍結候補集合(OF-179)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class FrozenCandidate:
    pron: tuple
    source: str  # C1_cmu_variant / C2_ledger_expected / C2_ledger_alt
    confidence: str  # dictionary / low / medium / high
    rank: int  # C1 のとき CMU 異読の順位(0=代表)。C2 は 0
    ledger_key: str | None = None
    updated_at: str | None = None
    ipa_raw: str | None = None
    also_from: tuple = ()


@dataclass(frozen=True)
class FrozenWord:
    word: str
    candidates: tuple  # tuple[FrozenCandidate]
    spell_prons: tuple  # ((expected_spelling, (pron_variants...)), ...)  canonical 語が許す Pattern 期待綴りの CMU 発音
    overflow_dropped: int
    n_before_cap: int
    excluded: tuple  # (dict as sorted tuple of items) 除外理由の記録
    unconvertible: tuple


@dataclass(frozen=True)
class FrozenCandidateSet:
    words: tuple  # tuple[FrozenWord]
    candidate_set_hash: str
    segment_started_at: str | None
    max_per_word: int
    m1_version: str = M1_VERSION

    def word(self, w: str):
        w = (w or "").lower().strip("'")
        for fw in self.words:
            if fw.word == w:
                return fw
        return None

    def to_dict(self) -> dict:
        return {"candidate_set_hash": self.candidate_set_hash, "segment_started_at": self.segment_started_at,
                "max_per_word": self.max_per_word,
                "words": {fw.word: [{"pron": list(c.pron), "source": c.source, "confidence": c.confidence, "rank": c.rank,
                                      "ledger_key": c.ledger_key, "updated_at": c.updated_at, "ipa_raw": c.ipa_raw,
                                      "also_from": list(c.also_from)} for c in fw.candidates] for fw in self.words}}


def expected_spellings(c: str) -> set:
    """canonical 語 c に対し、承認済み Pattern A/B/C と厳密一致が『受理側』として期待する ASR 綴りの集合。"""
    c = c.lower().strip("'")
    e = {c}
    if c.endswith("ies") and len(c) > 4:
        e.add(c[:-3] + "y")
    if c.endswith("es") and len(c) > 3:
        e.add(c[:-2])
    if c.endswith("s") and len(c) > 2:
        e.add(c[:-1])
    if c.endswith("ed") and len(c) > 3:
        e.add(c[:-2])
    e.add(c + "s")
    e.add(c + "es")
    if c.endswith("y") and len(c) > 2:
        e.add(c[:-1] + "ies")
    return e


def _parse_ts(v):
    """ISO 文字列/epoch/datetime を datetime へ。解釈不能は None。"""
    if v is None or v == "":
        return None
    if isinstance(v, _dt.datetime):
        return v
    if isinstance(v, (int, float)):
        return _dt.datetime.fromtimestamp(v)
    try:
        d = _dt.datetime.fromisoformat(str(v))
        return d.replace(tzinfo=None) if d.tzinfo else d
    except ValueError:
        return None


def _norm_surface(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def _c2_candidates(w: str, ledger: dict, started):
    """Ledger から語 w の C2 候補を (採用リスト, 除外記録, 変換不能記録) で返す。除外条件(OF-181)と時刻条件(OF-179)を適用。"""
    got, excluded, unconv = [], [], []
    for key, e in (ledger or {}).items():
        surf = _norm_surface(e.get("surface", ""))
        if surf != w:
            continue
        if " " in surf:
            continue
        if e.get("entity_type") == "ja_reading_katakana":
            excluded.append({"ledger_key": key, "reason": "ja_reading_katakana"})
            continue
        if e.get("ledger_disabled"):  # PRONUNCIATION-LEDGER-INVALID-ENTRY-REMEDIATION-01: 不正entryの隔離フラグ
            excluded.append({"ledger_key": key, "reason": "ledger_disabled", "detail": e.get("ledger_disabled_reason", "")})
            continue
        canon_sp = _norm_surface(e.get("canonical_spelling", ""))
        if canon_sp and canon_sp != surf:  # OF-181(a): us→unknown / plus→cascade 型
            excluded.append({"ledger_key": key, "reason": "canonical_spelling_differs_from_surface", "canonical_spelling": canon_sp})
            continue
        if not (e.get("sources") or []):  # OF-181(b)
            excluded.append({"ledger_key": key, "reason": "sources_empty"})
            continue
        upd = e.get("updated_at")
        upd_dt = _parse_ts(upd)
        if started is not None and upd_dt is not None and upd_dt >= started:  # OF-179: segment 開始以降の作成・更新は候補にしない
            excluded.append({"ledger_key": key, "reason": "updated_at_not_before_segment_start", "updated_at": upd})
            continue
        conf = e.get("confidence", "") or ""
        raws = [("C2_ledger_expected", e.get("expected_pronunciation_ipa") or "")] + \
               [("C2_ledger_alt", a) for a in (e.get("alternate_pronunciations") or [])]
        for src, raw in raws:
            for seg, why in _ipa_segments(raw):
                if why:
                    excluded.append({"ledger_key": key, "reason": why, "ipa": seg})
                    continue
                p = ipa_to_arpa(seg)
                if p is None:
                    unconv.append({"ledger_key": key, "ipa": seg, "reason": "unconvertible_symbol"})
                    continue
                got.append((p, src, conf, key, upd, seg))
    return got, excluded, unconv


def freeze_candidates(canonical_text: str, *, cmu=None, ledger_snapshot=None, segment_started_at=None,
                      max_per_word: int = DEFAULT_MAX_PER_WORD) -> FrozenCandidateSet:
    """canonical 文の全トークンの候補集合を、segment の最初の試行前に 1 回だけ作り凍結する。
    入力に ASR 転写は存在しない(ASR 非依存)。ledger_snapshot は呼出側が segment 開始時に取った読取専用 dict。
    retry/fallback/regen/減速後の同一 segment 内では、返された凍結物を判定関数へ渡し続けること(再生成しない)。"""
    cmu = cmu or default_cmu
    started = _parse_ts(segment_started_at)
    words = []
    for w in dict.fromkeys(_tokens(canonical_text)):
        cands, seen = [], {}

        def add(pron, src, conf, rank, key=None, upd=None, raw=None):
            if pron in seen:
                i = seen[pron]
                c = cands[i]
                cands[i] = FrozenCandidate(c.pron, c.source, c.confidence, c.rank, c.ledger_key, c.updated_at, c.ipa_raw,
                                           tuple(c.also_from) + (src,))
                return
            seen[pron] = len(cands)
            cands.append(FrozenCandidate(pron, src, conf, rank, key, upd, raw))

        vs = cmu(w)
        for i, v in enumerate(vs):
            add(tuple(v), "C1_cmu_variant", "dictionary", i)
        excluded, unconv = [], []
        if not vs:  # C2 は CMU 未収録語のみ
            got, excluded, unconv = _c2_candidates(w, ledger_snapshot, started)
            for p, src, conf, key, upd, seg in got:
                add(p, src, conf, 0, key, upd, seg)
        overflow = max(0, len(cands) - max_per_word)
        spell = tuple((s, tuple(tuple(v) for v in cmu(s))) for s in sorted(expected_spellings(w)))
        words.append(FrozenWord(w, tuple(cands[:max_per_word]), spell, overflow, len(cands),
                                tuple(json.dumps(x, sort_keys=True, ensure_ascii=False) for x in excluded),
                                tuple(json.dumps(x, sort_keys=True, ensure_ascii=False) for x in unconv)))
    payload = {"v": M1_VERSION, "cap": max_per_word, "started": str(segment_started_at),
               "words": [[fw.word, [[list(c.pron), c.source, c.confidence, c.rank, c.ledger_key, c.updated_at, c.ipa_raw, list(c.also_from)]
                                    for c in fw.candidates],
                          [[s, [list(v) for v in vs]] for s, vs in fw.spell_prons], fw.overflow_dropped] for fw in words]}
    h = hashlib.sha1(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()[:16]
    return FrozenCandidateSet(tuple(words), h, str(segment_started_at) if segment_started_at is not None else None, max_per_word)


# ---------------------------------------------------------------------------
# 判定
# ---------------------------------------------------------------------------
def forms_from(c: str, cands) -> dict:
    """候補ごとに Pattern(厳密/A/B/C)が受理側として期待する音素列を導く。{音素列: [(rule, candidate)]}"""
    out = collections.defaultdict(list)
    cl = c.lower().strip("'")
    for cd in cands:
        v = tuple(cd.pron)
        out[v].append(("exact", cd))
        if v and v[-1] in _SIB:
            out[v[:-1]].append(("drop_final_S_or_Z", cd))
        if cl.endswith("ed"):
            if v and v[-1] in ("T", "D"):
                out[v[:-1]].append(("drop_ed", cd))
            if len(v) >= 2 and v[-2:] == ("IH", "D"):
                out[v[:-2]].append(("drop_ed", cd))
        out[v + ("S",)].append(("add_s", cd))
        out[v + ("Z",)].append(("add_s", cd))
        out[v + ("IH", "Z")].append(("add_s", cd))
    return out


@dataclass
class M1Result:
    accepted: bool
    reason: str  # ACCEPT_REASON か不受理/不発理由
    applicable: bool  # M1 を試行した(入口条件を満たした)か
    classification: str | None = None
    pass_with_warning: bool = False
    normalized_asr: str | None = None
    subs: list = field(default_factory=list)
    audit: dict = field(default_factory=dict)
    no_match_reason: str | None = None
    secondary_agree: bool | None = None


def _replace_tokens(asr: str, repl: dict) -> str:
    text = (asr or "").replace("’", "'")
    pieces, last, j = [], 0, 0
    for m in re.finditer(r"[A-Za-z0-9']+", text):
        tok = m.group(0)
        pieces.append(text[last:m.start()])
        new = repl.get(j)
        pieces.append(tok if new is None else (new.capitalize() if tok[:1].isupper() else new))
        last = m.end()
        j += 1
    pieces.append(text[last:])
    return "".join(pieces)


def _variants(cmu, word: str, primary_only: bool) -> list:
    vs = [tuple(v) for v in cmu(word.strip("'"))]
    return vs[:1] if primary_only else vs


def _lazy_val():
    import er006_preprod_hardening_01_validation as val
    return val


def _lazy_csv3():
    import er011_b1_connected_speech_validator_01 as csv3
    return csv3


def _enumerate_subs(canonical, asr, flagged, frozen, cmu):
    """フラグされた差分 ASR トークンごとの置換案と、一致しなかった理由を返す。(by_idx, no_match_reasons)"""
    cw, aw = _tokens(canonical), _tokens(asr)
    sm = difflib.SequenceMatcher(a=cw, b=aw, autojunk=False)
    by_idx, reasons = {}, []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal" or j1 == j2 or i1 == i2:
            continue
        for j in range(j1, j2):
            tok = aw[j]
            if tok not in flagged:
                continue
            ent = flagged[tok]
            avs = _variants(cmu, tok, ent)
            if not avs:
                reasons.append(NM_ASR_NOT_IN_CMU)
                continue
            opts, had_cands = [], False
            for c in cw[i1:i2]:
                fw = frozen.word(c)
                if fw is None:
                    continue
                cands = [x for x in fw.candidates if not (ent and x.source == "C1_cmu_variant" and x.rank > 0)]
                if not cands:
                    continue
                had_cands = True
                forms = forms_from(c, cands)
                for s, svs_all in fw.spell_prons:
                    if s == tok:
                        continue
                    svs = list(svs_all[:1]) if ent else list(svs_all)
                    if not svs or not (set(svs) & set(avs)):
                        continue
                    hits = [(rule, cd) for v in svs for rule, cd in forms.get(tuple(v), [])]
                    if hits:
                        hits.sort(key=lambda h: (h[0] != "exact", h[1].source != "C1_cmu_variant", h[1].pron))
                        opts.append({"asr_index": j, "from": tok, "to": s, "canonical_word": c, "entity_like": ent,
                                     "rule": hits[0][0], "hits": hits})
            if opts:
                opts.sort(key=lambda o: (o["rule"] != "exact", o["to"]))
                by_idx[j] = opts
            else:
                reasons.append(NM_NO_PHONEME_MATCH if had_cands else NM_NO_CANDIDATES)
    return by_idx, reasons


def _hit_dict(rule, cd):
    return {"rule": rule, "source": cd.source, "confidence": cd.confidence, "pron": list(cd.pron),
            "ledger_key": cd.ledger_key, "updated_at": cd.updated_at, "ipa_raw": cd.ipa_raw, "also_from": list(cd.also_from)}


def _post_check(canonical, asr2, subs):
    """置換後の文で F1 を再実行。(ok, reason, cs2)。残差 0、かつ exact 以外の置換は全て f1_explained に含まれること(OF-178)。"""
    csv3 = _lazy_csv3()
    cs2 = csv3.classify_connected_speech(canonical, asr2)
    if cs2.get("f1_residual"):
        return False, R_POST_RESIDUAL, cs2
    need = collections.Counter((s["canonical_word"].lower(), s["to"].lower()) for s in subs if s["rule"] != "exact")
    if need:
        if cs2.get("new_judgment") not in _OK_JUDGMENTS:
            return False, R_NOT_EXPLAINED, cs2
        have = collections.Counter(((e.get("canonical") or "").lower().strip("'"), (e.get("asr") or "").lower().strip("'"))
                                   for e in cs2.get("f1_explained") or [])
        for k, n in need.items():
            if have.get(k, 0) < n:
                return False, R_NOT_EXPLAINED, cs2  # F1 の benign(規則単複)等で吸収された置換は不受理
    return True, None, cs2


def _entry_gate(canonical, asr_text, base_cls, f1_result, classify_fn):
    """入口条件: Production 分類が ASR_VALIDATION_UNCERTAIN、protected 通過、F1 残差が entity_or_homophone_only/none。
    戻り値 (ok, reason, base_cls, f1_kind)"""
    val = _lazy_val()
    csv3 = _lazy_csv3()
    if base_cls is None:
        base_cls = (classify_fn or val.classify_asr_match)(canonical, asr_text)
    if base_cls is None or base_cls.classification != "ASR_VALIDATION_UNCERTAIN":
        return False, R_NOT_UNCERTAIN, base_cls, None
    if not base_cls.protected.passed:
        return False, R_PROTECTED_FAIL, base_cls, None
    cs = copy.deepcopy(f1_result) if f1_result is not None else csv3.classify_connected_speech(canonical, asr_text)
    kind = val._f1_refine_residual_kind(cs, base_cls.protected)
    if kind == "content":
        return False, R_F1_CONTENT, base_cls, kind
    return True, None, base_cls, kind


def _judge_core(canonical, asr_text, frozen, base_cls, f1_result, cmu, classify_fn, max_combo=64):
    ok, why, base_cls, kind = _entry_gate(canonical, asr_text, base_cls, f1_result, classify_fn)
    audit = {"m1_version": M1_VERSION, "original_asr": asr_text, "candidate_set_hash": frozen.candidate_set_hash,
             "candidates_frozen": True, "f1_residual_kind": kind}
    if not ok:
        return M1Result(False, why, False, audit=audit)
    flagged = {}
    for d in base_cls.protected.content_word_diffs:
        for t in _tokens(d.get("asr", "")):
            flagged[t] = flagged.get(t, False) or bool(d.get("entity_like"))
    if not flagged:
        return M1Result(False, R_NO_FLAGGED, True, audit=audit)
    by_idx, reasons = _enumerate_subs(canonical, asr_text, flagged, frozen, cmu)
    if not by_idx:
        nm = reasons[0] if reasons else NM_NO_PHONEME_MATCH
        audit["no_match_reason"] = nm
        audit["no_match_reasons"] = sorted(set(reasons))
        return M1Result(False, R_NO_MATCH, True, audit=audit, no_match_reason=nm)
    idxs = sorted(by_idx)
    last_fail = R_NO_MATCH
    for combo in itertools.islice(itertools.product(*[by_idx[i] for i in idxs]), max_combo):
        asr2 = _replace_tokens(asr_text, {o["asr_index"]: o["to"] for o in combo})
        ok2, why2, cs2 = _post_check(canonical, asr2, combo)
        if not ok2:
            last_fail = why2
            continue
        subs = []
        for o in combo:
            h0 = o["hits"][0]
            d = _hit_dict(*h0)
            d.update({"from": o["from"], "to": o["to"], "canonical_word": o["canonical_word"], "entity_like": o["entity_like"],
                      "rule": o["rule"], "all_matching_candidates": [_hit_dict(r, c) for r, c in o["hits"]]})
            subs.append(d)
        audit.update({"normalized_asr": asr2, "acceptance_reason": ACCEPT_REASON, "subs": subs,
                      "ledger_keys": sorted({s["ledger_key"] for s in subs if s["ledger_key"]}),
                      "f1_explained": cs2.get("f1_explained"), "f1_version": cs2.get("f1_version")})
        return M1Result(True, ACCEPT_REASON, True, classification=ACCEPT_REASON, pass_with_warning=True,
                        normalized_asr=asr2, subs=subs, audit=audit)
    audit["no_match_reason"] = last_fail
    return M1Result(False, last_fail, True, audit=audit, no_match_reason=last_fail)


def m1_multi_candidate_judge(canonical: str, asr_text: str, frozen: FrozenCandidateSet, *, f1_result=None,
                             secondary_asr_text=None, m1_enabled: bool = True, lang: str = "en-US",
                             base_cls=None, cmu=None, classify_fn=None) -> M1Result:
    """M1 複数候補判定。frozen は freeze_candidates() の戻り値(凍結物の注入。この関数内で canonical 側候補を再計算しない)。
    base_cls: Production の ClassificationResult(省略時は classify_asr_match を呼ぶ)。f1_result: classify_connected_speech の戻り値(任意)。
    secondary_asr_text: 両転写が手元にある場合のみ渡す(必須化しない)。他方が protected fail/内容誤りなら矛盾として非PASS(OF-183)。"""
    if not m1_enabled:
        return M1Result(False, R_DISABLED, False)
    if lang != "en-US":
        return M1Result(False, R_LANG, False)
    if frozen is None or not any(fw.candidates for fw in frozen.words):
        return M1Result(False, R_NO_FROZEN, False)
    cmu = cmu or default_cmu
    val = _lazy_val()
    classify = classify_fn or val.classify_asr_match
    r = _judge_core(canonical, asr_text, frozen, base_cls, f1_result, cmu, classify)
    sec_state, sec_agree = None, None
    if r.accepted and secondary_asr_text is not None:
        sc = classify(canonical, secondary_asr_text)
        if sc is None:
            sec_state = "unavailable"
        elif sc.should_pass:
            sec_state, sec_agree = "native_pass", True
        elif (not sc.protected.passed) or sc.classification in ("TRUE_CONTENT_MISMATCH", "TTS_FAILURE"):
            sec_state = "contradiction:" + ("protected_fail" if not sc.protected.passed else sc.classification)
        else:
            r2 = _judge_core(canonical, secondary_asr_text, frozen, sc, None, cmu, classify)
            if r2.accepted:
                mine = {(s["canonical_word"], tuple(h["pron"])) for s in r.subs for h in s["all_matching_candidates"]}
                theirs = {(s["canonical_word"], tuple(h["pron"])) for s in r2.subs for h in s["all_matching_candidates"]}
                sec_state, sec_agree = "m1_accept", bool(mine & theirs)
            else:
                sec_state, sec_agree = "uncertain_no_agreement", False
        r.audit["secondary_state"] = sec_state
        r.audit["secondary_agree"] = sec_agree
        r.secondary_agree = sec_agree
        if sec_state and sec_state.startswith("contradiction:"):
            r.accepted, r.reason, r.classification, r.pass_with_warning = False, R_SECONDARY_CONTRADICTION, None, False
            r.audit["no_match_reason"] = sec_state
    elif r.accepted:
        r.audit["secondary_state"], r.audit["secondary_agree"] = "not_provided", None
    return r


# ---------------------------------------------------------------------------
# 事後集計(OF-187)
# ---------------------------------------------------------------------------
def aggregate_by_ledger_key(audits) -> dict:
    """M1_MULTI_CANDIDATE_ACCEPT の audit 列を ledger_key 別に集計する(自己強化ループの事後検出用)。"""
    out = {}
    for a in audits:
        if a.get("acceptance_reason") != ACCEPT_REASON:
            continue
        for s in a.get("subs", []):
            k = s.get("ledger_key") or "(C1_cmu)"
            e = out.setdefault(k, {"accept_count": 0, "canonical_words": set(), "confidences": set(), "sources": set(),
                                   "updated_at": set(), "candidate_set_hashes": set(), "secondary_agree_true": 0})
            e["accept_count"] += 1
            e["canonical_words"].add(s["canonical_word"])
            e["confidences"].add(s["confidence"])
            e["sources"].add(s["source"])
            e["updated_at"].add(s["updated_at"])
            e["candidate_set_hashes"].add(a.get("candidate_set_hash"))
            if a.get("secondary_agree"):
                e["secondary_agree_true"] += 1
    return {k: {kk: (sorted(vv, key=str) if isinstance(vv, set) else vv) for kk, vv in v.items()} for k, v in out.items()}
