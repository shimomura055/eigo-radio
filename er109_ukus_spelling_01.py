# ============================================================
# er109_ukus_spelling_01.py
# ASR-QUALITY-2ITEMS-COMPREHENSIVE-01 ②英米綴り(UKUS) 委任_04 (2026-10-23)
# Production: Family X / Z の run scope 内でのみ有効(er109_xz_scope_01.is_ukus_active_for_run())。A/B/C・単体呼出は従来どおり(evaluate(ukus=False)既定)。
# 承認: APPROVED_FOR_PRODUCTION(ユーザー正式採用2026-10-23、UDR #168)。PRODUCTION_WIRED表記はFable受入後。
#
# 目的: 『正当な英米綴り差(speciality/specialty, colour/color, organise/organize ...)だけ』が原因のNGを、er109の判定(整列→差span→同値判定)の
#       内側で位置ごとに同値化する。統合点は er109_asr_orthographic_equivalence_01.evaluate の opcode ループ1か所。
#       既存判定が合格するspanには一切触れない(whole-span判定が先、救済は不合格spanのみ)=PASS->NG 0は構造保証。
#       救済に失敗した場合は、呼出元は元の(ukus=False と同一の)NG記録をそのまま使う。
# 仕様(Trial判定ロジック・承認済み、DESIGN_02/OPUS_REVIEW_01 OF-01〜11、OPUS_REVIEW_02_COND_C W-01):
#   - 救済の対象は『同数・全unitがword』のspan(Trial positional条件)だけ。位置ごとに既存の位置別判定(単一語unit同士)を行い、
#     不合格(または判定不能=CMU未登録)の位置だけ固定対表を参照する。1位置以上が対表で同値化され、かつ他の全位置が合格のときだけ救済成立。
#   - canonical側の固有名詞らしさ(全大文字/語中大文字/非ASCII/文中の大文字始まり/文頭大文字+次が大文字語)の位置は対象外(fail-closed)。
#     ①RET(PNAP)の表は参照しない(純関数性維持)。
#   - 対は直接対のみ(推移しない)。AMB対(mum/mom型)は canonical=UK形 -> ASR=US形 の一方向。語幹+同一接尾('s / s')とハイフン複合(各部が同形か対)対応。
#   - 音素は注入しない(対一致位置は『bad(CMU未登録)』検査の対象外にするだけ)。warningsには入れない(PASS_WITH_WARNING化しない)。
#     pron_differs(52対: TTSが米式に読んでもPASSし得る残存リスク)は ukus_pairs[] に記録し、audit()が pron_differs_n を集計する。
#   - Tier-2(level71-99, 8,718対)は active=False で保持するだけ(有効化は仕様変更=ユーザー承認+Opus)。
# 固定対表: er109_ukus_pairs_v1.json (VarCon/SCOWL 2020.12.07 派生。meta.license に著作権・許諾文)。ロード時に pairs の正規化JSONの sha256 を
#   PAIRS_CANONICAL_SHA256 と照合し、不一致なら RuntimeError(失敗状態をcache=毎回1.5MB再ロードしない)。呼出元(decision())はfail-closed(従来判定+sinkへ記録)。
# 辞書更新手順(開発ツール、Productionからimportされない): er109_ukus_pairs_build_01.py --write → 差分対を人手確認 → PAIRS_CANONICAL_SHA256更新 →
#   er109 LAYER_VERSION のsuffix更新(ukus02…)+X/Z golden再作成 → Opus/Fable確認(対表の追加・Tier昇格は仕様変更=ユーザー承認)。
# ============================================================
from __future__ import annotations

import functools
import hashlib
import json
import os
import re
import unicodedata

import er109_asr_orthographic_equivalence_01 as e109

RULE_NAME = "ukus_spelling_variant"
PAIRS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "er109_ukus_pairs_v1.json")
PAIRS_CANONICAL_SHA256 = "c5598eb6e603ee4cf5af2b8664f8ead9495eafd839ed8abbefda6bbe2bbb2dee"
REASON_WITH_UKUS = "all_diff_spans_phoneme_equal_or_ukus_variant"

_SENT_END = set(".!?:;\"“”(‘’'")


def pairs_canonical_sha256(pairs) -> str:
    return hashlib.sha256(json.dumps(pairs, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).hexdigest()


# ---------------------------------------------------------------- 固定対表
class PairTable:
    def __init__(self, path: str = PAIRS_FILE, expected_sha: str | None = PAIRS_CANONICAL_SHA256):
        d = json.load(open(path, encoding="utf-8"))
        got = pairs_canonical_sha256(d["pairs"])
        if expected_sha is not None and got != expected_sha:
            raise RuntimeError(f"ukus_pairs_sha256_mismatch: expected={expected_sha} got={got}")
        self.meta = d["meta"]
        self.path = path
        self.sha256 = got
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


_TABLE_STATE: dict = {}


def table() -> PairTable:
    """1 process 1回ロード。sha不一致等の失敗は『失敗状態』をcacheし、毎回再ロードしない(lru_cacheは例外をcacheしないため自前)。"""
    st = _TABLE_STATE.get("v")
    if st is None:
        try:
            st = (True, PairTable())
        except Exception as exc:  # noqa: BLE001
            st = (False, exc)
        _TABLE_STATE["v"] = st
    if st[0]:
        return st[1]
    raise RuntimeError(f"ukus_table_unavailable(cached): {type(st[1]).__name__}: {st[1]}")


def reset_table_cache_for_test() -> None:
    _TABLE_STATE.clear()
    canon_entity_flags.cache_clear()


# ---------------------------------------------------------------- canonical側の固有名詞らしさ(OF-02)
@functools.lru_cache(maxsize=2048)
def canon_entity_flags(canonical: str) -> tuple:
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
    return tuple(flags)


# ---------------------------------------------------------------- 救済(evaluate の opcode ループから ukus=True のときだけ呼ばれる)
def rescue_span(canonical: str, n_canon_units: int, i1: int, c_span: list, a_span: list, representative_only: bool, entity_tokens: set):
    """既存判定が不合格(bad または _judge_span NG)になった『同数・全unitがword』のspanを、位置別に救済できるか。
    戻り値: (records: list[SpanRecord], ukus_pairs: list[dict], warnings: list[str]) | None(救済不可=呼出元は元のNG記録を使う)。
    位置ごと: 既存の位置別判定(単一語unit同士)で合格 -> そのまま / 不合格または判定不能(CMU未登録)かつ canonical側が固有名詞らしくなく
    直接対が表にある -> SpanRecord(rule=ukus_spelling_variant) / それ以外 -> 救済不可。他位置が全て合格し、かつ1位置以上が対表で同値化された場合のみ成立。"""
    if not (len(c_span) == len(a_span) and c_span and all(u.kind == "word" for u in c_span + a_span)):
        return None
    flags = canon_entity_flags(canonical)
    if len(flags) != n_canon_units:
        return None                                    # 対応が取れない=fail-closed
    tbl = table()
    records, pairs, warns = [], [], []
    for k, (cu_, au_) in enumerate(zip(c_span, a_span)):
        rec = None
        if cu_.prons and au_.prons:
            rec = e109._judge_span([cu_], [au_], representative_only, entity_tokens)
        if rec is not None and rec.equivalent:
            records.append(rec)
            for w in rec.warnings:
                if w not in warns:
                    warns.append(w)
            continue
        if flags[i1 + k]:
            return None
        hit = tbl.word_pair(cu_.surface.lower().rstrip("."), au_.surface.lower().rstrip("."))
        if not hit:
            return None
        records.append(e109.SpanRecord([cu_.surface], [au_.surface], True, RULE_NAME,
                                       "ukus_pair:" + "+".join(h["tier"] + ":" + h["uk"] + "/" + h["us"] for h in hit)))
        for h in hit:
            pairs.append({"canon": cu_.surface, "asr": au_.surface, "uk": h["uk"], "us": h["us"], "tier": h["tier"], "src": h["src"],
                          "dir": h["dir"], "pron_differs": h.get("pron_differs")})
    if not pairs:
        return None                                    # 対表による同値化が1つも無い=本層の寄与なし(既存NGのまま)
    return records, pairs, warns


def audit_fields(pairs: list) -> dict:
    return {"ukus_pairs": list(pairs), "ukus_pairs_n": len(pairs), "pron_differs_n": sum(1 for p in pairs if p.get("pron_differs"))}
