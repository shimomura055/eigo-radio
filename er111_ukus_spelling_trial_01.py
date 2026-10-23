# ============================================================
# er111_ukus_spelling_trial_01.py
# ASR-QUALITY-2ITEMS-COMPREHENSIVE-01 ②英米綴り UKUS 委任_02 (2026-10-23) DEV/Trial専用。Production未配線・承認前。
# Status: TRIAL(VALIDATEDではない)。正式経路(er006/er020/er078/er104/runner/er109/er109_xz_scope)から参照されない(AST testで固定: er111_ukus_spelling_trial_01_test_01.py)。
#         11-7の限定例外(flag)も使わない=flagが無い=Production経路からONにできない。採用はユーザー承認+別委任(Opus条件C)。
#
# 目的: 『正当な英米綴り差(speciality/specialty, colour/color, organise/organize ...)』だけが原因のNGを、er109と同じ判定(整列→差span→同値判定)の中で
#       位置ごとに同値化する『Trial用evaluate』。er109の関数・module globalは変更しない(import方向は Trial -> er109 のみ)。
# Opus独立レビュー(OPUS_REVIEW_01.md)の反映:
#   OF-01: key正規化をせず元keyで整列。同数・語unit・1:1の'replace'spanを位置ごとに見て、既存判定(音素)が不合格になる位置だけ固定対表を参照する。
#          対が一致した位置は SpanRecord(rule="ukus_spelling_variant", equivalent=True)。残りの位置は既存の bad チェック/_judge_span。
#          さらに『既存er109.evaluateがPASSなら、その結果をそのまま返す』=PASS->NGは構造上起こらない(単調性)。長さ違い・欠落・付加は従来どおり非同値。
#   OF-02: canonical側/ASR側を明示的に区別(対の向きはcanonical->ASR)。偽の発音を注入しない(対一致位置は『bad』検査の対象外にするだけ)。
#          canonical側の固有名詞らしさ(語中の大文字・全大文字・文頭大文字+次が大文字語・非ASCII外来語)は対象外=fail-closed(Rockefeller Center->Centre)。
#   OF-05: Tier-2(level71-99)は非同値。UKUS情報はwarningsに入れない(PASS_WITH_WARNING化しない)。別fieldの res.ukus_pairs に記録。
#   OF-06: 対ごとのpron_differs(CMU両側登録で音素が交わらない=TTSが米式に読んでも通る残存リスク)を記録して件数を数える。
#   OF-08/11: 規則は固定表へ展開済み(runtimeに規則・wordfreq依存なし)。breame不採用。
# ============================================================
from __future__ import annotations

import difflib
import functools
import json
import os
import re
import unicodedata

import er109_asr_orthographic_equivalence_01 as e109

_BASE_EVALUATE = e109.evaluate    # import時点の原本を束縛(評価harnessがe109.evaluateを一時差替えしても再帰しない)
TRIAL_LAYER_VERSION = "er111_ukus_spelling_trial_v1"
RULE_NAME = "ukus_spelling_variant"
PAIRS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "er111_ukus_pairs_v1.json")

_SENT_END = set(".!?:;\"“”(‘’'")


# ---------------------------------------------------------------- 固定対表
class PairTable:
    def __init__(self, path: str = PAIRS_FILE):
        d = json.load(open(path, encoding="utf-8"))
        self.meta = d["meta"]
        self.path = path
        self.p: dict = {}
        for e in d["pairs"]:
            if e.get("active"):
                self.p[(e["uk"], e["us"])] = e
        self.size = len(self.p)

    def direct(self, c: str, a: str):
        """canonical語c -> ASR語a が許可された直接対(推移しない)か。UK形->US形は全対、US形->UK形は双方向対のみ(AMBは一方向)。"""
        e = self.p.get((c, a))
        if e is not None:
            return e
        e2 = self.p.get((a, c))
        if e2 is not None and e2["dir"] == "both":
            return e2
        return None

    def word_pair(self, c: str, a: str):
        """list[entry] | None。語幹対 + 同一接尾('s / s') + ハイフン複合(各部が同じか対)。1つ以上の対が必要。"""
        if c == a:
            return []
        e = self.direct(c, a)
        if e is not None:
            return [e]
        if c.endswith("'s") and a.endswith("'s"):
            return self.word_pair(c[:-2], a[:-2]) or None
        if c.endswith("s'") and a.endswith("s'"):
            return self.word_pair(c[:-1], a[:-1]) or None
        if "-" in c and "-" in a:
            cp, ap = [x for x in c.split("-") if x], [x for x in a.split("-") if x]
            if len(cp) != len(ap) or len(cp) < 2:
                return None
            out = []
            for x, y in zip(cp, ap):
                r = self.word_pair(x, y)
                if r is None:
                    return None
                out += r
            return out or None
        return None


@functools.lru_cache(maxsize=1)
def table() -> PairTable:
    return PairTable()


# ---------------------------------------------------------------- canonical側の固有名詞らしさ(OF-02)
def _canon_entity_flags(canonical: str) -> list:
    """e109._unitsと1:1対応する canonical unit ごとの『固有名詞らしさ』flag。fail-closed側(迷ったらTrue)。"""
    t = unicodedata.normalize("NFKC", canonical or "").replace("’", "'").replace("‘", "'")
    t = t.replace("—", " ").replace("–", " ").replace("−", "-")
    ms = list(e109._TOKEN_RE.finditer(t))
    flags = []
    for i, m in enumerate(ms):
        s = m.group(0)
        if m.lastgroup != "word":
            flags.append(False)
            continue
        core = s.rstrip(".")
        letters = re.sub(r"[^A-Za-z]", "", core)
        ent = False
        if any(ord(ch) > 127 for ch in core):
            ent = True                                                  # 非ASCII(外来語)
        elif len(letters) >= 2 and letters.isupper():
            ent = True                                                  # 全大文字(頭字語・固有名)
        elif letters[1:] != letters[1:].lower():
            ent = True                                                  # 語中の大文字(McDonald/iPhone)
        elif letters[:1].isupper():
            pre = t[: m.start()].rstrip()
            sent_initial = (not pre) or pre[-1] in _SENT_END
            if not sent_initial:
                ent = True                                              # 文中の大文字始まり=固有名詞らしい
            else:
                nxt = ms[i + 1].group(0) if i + 1 < len(ms) and ms[i + 1].lastgroup == "word" else ""
                if nxt[:1].isupper():
                    ent = True                                          # 文頭だが次も大文字語(Centre Street / Grey Gardens)
        flags.append(ent)
    return flags


# ---------------------------------------------------------------- Trial用evaluate
def _position_existing(cu_: e109.Unit, au_: e109.Unit, representative_only: bool, entity_tokens: set):
    """1位置(1:1語)を既存er109の基準で判定。(SpanRecord|None, incomparable_why)。None=この位置は既存基準で判定不能(bad)。"""
    if not cu_.prons or not au_.prons:
        return None, ",".join(sorted({u.why or u.kind for u in (cu_, au_) if not u.prons}))
    return e109._judge_span([cu_], [au_], representative_only, entity_tokens), ""


def evaluate_trial(canonical: str, asr: str, *, representative_only: bool = False, tbl: PairTable | None = None) -> e109.EquivalenceResult:
    """canonical(期待文)とasr(転写)が『発音同値 もしくは 英米綴り差のみ』か。er109.evaluateの拡張版(Trial)。
    res.ukus_pairs: 本層で同値化した位置の記録(list[dict])。res.trial_layer: TRIAL_LAYER_VERSION。"""
    base = _BASE_EVALUATE(canonical, asr, representative_only=representative_only)
    base.ukus_pairs = []
    base.trial_layer = TRIAL_LAYER_VERSION
    if base.equivalent:
        return base                                    # OF-01: 既存PASSは完全にそのまま(PASS->NGは構造上起こらない)
    if asr is None or canonical is None:
        return base
    tbl = tbl or table()
    import er006_preprod_hardening_01_validation as val
    entity_tokens = set()
    try:
        entity_tokens = set(val.capitalized_flags(canonical)) | set(val.loanword_flags(canonical))
    except Exception:
        pass
    # NG結果は整列に使ったunit列を保持している(EquivalenceResult.canon_units/asr_units)。再計算せず再利用する(unit化がコストの大半)。
    cu, au = list(base.canon_units or []), list(base.asr_units or [])
    if not cu or not au:
        return base
    ent_flags = _canon_entity_flags(canonical)
    if len(ent_flags) != len(cu):
        return base                                    # 対応が取れない=fail-closed
    ck = [u.key or u.surface for u in cu]
    ak = [u.key or u.surface for u in au]
    sm = difflib.SequenceMatcher(None, ck, ak, autojunk=False)
    res = e109.EquivalenceResult(False, "", canon_units=cu, asr_units=au)
    res.ukus_pairs = []
    res.trial_layer = TRIAL_LAYER_VERSION
    n_diff = 0
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        n_diff += 1
        c_span, a_span = cu[i1:i2], au[j1:j2]
        cs, as_ = [u.surface for u in c_span], [u.surface for u in a_span]
        if not c_span or not a_span:
            res.spans.append(e109.SpanRecord(cs, as_, False, "insert_or_delete", "one_side_empty"))
            res.reason = "one_side_empty(欠落・付加は同値にしない)"
            return res
        if len(c_span) > e109.MAX_UNITS_PER_SIDE or len(a_span) > e109.MAX_UNITS_PER_SIDE:
            res.spans.append(e109.SpanRecord(cs, as_, False, "too_long", "span_too_long"))
            res.reason = "span_too_long"
            return res
        positional = (len(c_span) == len(a_span) and all(u.kind == "word" for u in c_span + a_span))
        if not positional:
            # 長さ違い・数/記号/略語を含むspan: 従来どおり(本層は関与しない)
            bad = [u for u in c_span + a_span if not u.prons]
            if bad:
                res.spans.append(e109.SpanRecord(cs, as_, False, "incomparable", ",".join(sorted({u.why or u.kind for u in bad}))))
                res.reason = "incomparable(CMU未登録/解析不能/曖昧略語のため同値化しない)"
                return res
            rec = e109._judge_span(c_span, a_span, representative_only, entity_tokens)
            res.spans.append(rec)
            if not rec.equivalent:
                res.reason = rec.why
                return res
            if rec.rule not in res.rules:
                res.rules.append(rec.rule)
            for w in rec.warnings:
                if w not in res.warnings:
                    res.warnings.append(w)
            continue
        # 同数の語span: 位置ごと(OF-01)
        for k, (cu_, au_) in enumerate(zip(c_span, a_span)):
            ci = i1 + k
            rec, why_bad = _position_existing(cu_, au_, representative_only, entity_tokens)
            if rec is not None and rec.equivalent:
                res.spans.append(rec)
                if rec.rule not in res.rules:
                    res.rules.append(rec.rule)
                for w in rec.warnings:
                    if w not in res.warnings:
                        res.warnings.append(w)
                continue
            # 既存基準で不合格(または判定不能)の位置だけ、固定対表を参照
            hit = None
            if not ent_flags[ci]:
                hit = tbl.word_pair(cu_.surface.lower().rstrip("."), au_.surface.lower().rstrip("."))
            if hit:
                srec = e109.SpanRecord([cu_.surface], [au_.surface], True, RULE_NAME, "ukus_pair:" + "+".join(h["tier"] + ":" + h["uk"] + "/" + h["us"] for h in hit))
                res.spans.append(srec)
                if RULE_NAME not in res.rules:
                    res.rules.append(RULE_NAME)
                for h in hit:
                    res.ukus_pairs.append({"canon": cu_.surface, "asr": au_.surface, "uk": h["uk"], "us": h["us"], "tier": h["tier"], "src": h["src"],
                                           "dir": h["dir"], "pron_differs": h.get("pron_differs")})
                continue
            if rec is None:
                res.spans.append(e109.SpanRecord([cu_.surface], [au_.surface], False, "incomparable", why_bad))
                res.reason = "incomparable(CMU未登録/解析不能/曖昧略語のため同値化しない)"
                return res
            res.spans.append(rec)
            res.reason = rec.why
            return res
    if n_diff == 0:
        res.equivalent, res.reason = True, "surface_equal_after_normalization"
        return res
    res.equivalent = True
    res.reason = "all_diff_spans_phoneme_equal_or_ukus_variant" if res.ukus_pairs else "all_diff_spans_phoneme_equal"
    return res


@functools.lru_cache(maxsize=8192)
def evaluate_trial_cached(canonical: str, asr: str):
    """V6専用(test processでのhook差し替え用)。純関数のメモ化。"""
    return evaluate_trial(canonical, asr)


def audit_ukus(res) -> dict:
    """監査記録: ukus_pairs(別field。warningsには入れない)とpron_differs件数。"""
    pairs = list(getattr(res, "ukus_pairs", []) or [])
    return {"trial_layer": TRIAL_LAYER_VERSION, "ukus_pairs": pairs, "ukus_pairs_n": len(pairs),
            "pron_differs_n": sum(1 for p in pairs if p.get("pron_differs"))}
