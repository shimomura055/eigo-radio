# ============================================================
# er094_multiword_homophone_01.py
# 多語同音救済(L1判定層)の純関数module。PNMH-01 Trial v3(VALIDATED、2026-10-22ユーザー正式採用
# =APPROVED_FOR_PRODUCTION)の `multiword_span_equivalent_v3` を移植したもの。出典:
#   docs/research/PROPER-NOUN-PRONUNCIATION-MULTIWORD-HOMOPHONE-PLAN-01/proto_multiword_span_01.py
# 仕様: 隣接span内の「1語 <-> 連続2〜3語」で、CMU辞書の音素列(ストレス記号無視・全variant連結)が一致する場合のみ
# 「同音候補(homophone_candidate)」とする。ByUs <-> buy us / by us 型。承認済み安全条件(Trial v3のまま。拡張禁止):
#   - 片側は1語のみ(1:n / n:1)、最大3語、全tokenが英字のみ(小文字)
#   - 数値token・否定語は対象外(呼出側val.protected_checkの数値/否定ガードが先行し、ここでも拒否)
#   - 複数語側に1文字tokenを禁止(文字読み a m / u s 対策)、canonical側3字未満tokenを禁止(G5: AI/US/AM等の略語様)
#   - V8: 複数語側に2字tokenがある場合は閉じた機能語集合FW2のみ許容(`Bi-us`型の誤発音をNG維持)
#   - entity_like(固有名詞らしい語)は代表発音(CMU先頭variant)のみで比較
#   - CMU辞書外(OOV)・variant直積>64は判定不能=非救済
# 状態: 未配線(A-1)。Production既存ファイルから参照されない。配線(A-2)は val.protected_check の
#   1:1 homophone判定直後の1箇所のみ(Primary/Secondary転写とも classify_asr_match 経由で同一関数を通る)。
# rollback: 下記 MULTIWORD_HOMOPHONE_ENABLED を False にするだけ(env/flag/設定dictではない。承認済みのため既定True)。
# 循環import回避: val(er006_preprod_hardening_01_validation)は関数内で遅延importする。
# ============================================================
from __future__ import annotations

import itertools
import re

import er008_asr_variant_hardening_15_homophone_en as _hp

MULTIWORD_HOMOPHONE_ENABLED = True   # rollback用module定数(承認済み仕様のため既定ON)

MAX_SIDE = 3          # 片側の最大token数
MAX_JOINT = 64        # 発音variant直積の上限(超過は判定不能=安全側で非救済)
MIN_CANON_TOKEN_LEN = 3   # G5: canonical側tokenの最小文字数
# V8: 複数語側の2字tokenは下記の閉じた機能語集合のみ許容
FW2 = frozenset({"us", "on", "to", "in", "of", "by", "at", "it", "is", "as", "or", "an", "my", "me",
                 "he", "we", "be", "do", "go", "up", "so", "no", "if", "am", "ok"})

_TOK_OK = re.compile(r"^[a-z][a-z']*$")


def _strip(ph: str) -> str:
    return re.sub(r"\d", "", ph)


def _variants_nostress(tok: str, representative_only: bool = False):
    ps = _hp._phone_variants(tok)           # 既存CMU取得手段を再利用(辞書外=None)
    if not ps:
        return None
    if representative_only:
        ps = ps[:1]   # entity_like: 代表発音(CMU先頭variant)のみ
    return sorted({tuple(_strip(p).split()) for p in ps})


def joint_variants(tokens, representative_only: bool = False):
    vs = []
    for t in tokens:
        v = _variants_nostress(t, representative_only)
        if v is None:
            return None
        vs.append(v)
    n = 1
    for v in vs:
        n *= len(v)
    if n > MAX_JOINT:
        return None
    return {tuple(x for part in combo for x in part) for combo in itertools.product(*vs)}


def _is_number_or_negation(tok: str) -> bool:
    import er006_preprod_hardening_01_validation as val   # 遅延import(循環回避)
    return tok in val._NEGATION_WORDS or val._is_number(tok)


def multiword_span_equivalent(canon_span, asr_span, *, detail=None) -> bool:
    """全variant比較版(Trial v2相当)。通常は multiword_span_equivalent_v3 を使う。"""
    d = detail if detail is not None else {}
    c, a = list(canon_span), list(asr_span)
    if not c or not a:
        d["why"] = "empty_side"; return False
    if len(c) == 1 and len(a) == 1:
        d["why"] = "one_to_one(existing)"; return False
    if not (len(c) == 1 or len(a) == 1):
        d["why"] = "both_multi(out_of_scope)"; return False
    if max(len(c), len(a)) > MAX_SIDE:
        d["why"] = "too_long"; return False
    toks = c + a
    if any(not _TOK_OK.match(t) for t in toks):
        d["why"] = "non_alpha_token"; return False
    if any(_is_number_or_negation(t) for t in toks):
        d["why"] = "number_or_negation"; return False
    multi = c if len(c) > 1 else a
    if any(len(t) < 2 for t in multi):
        d["why"] = "single_letter_token(letter_reading_guard)"; return False
    if any(len(t) < MIN_CANON_TOKEN_LEN for t in c):
        d["why"] = "short_canonical_token(G5_acronym_guard)"; return False
    vc, va = joint_variants(c), joint_variants(a)
    if vc is None or va is None:
        d["why"] = "OOV_or_too_many_variants"; return False
    ok = bool(vc & va)
    d["why"] = "phoneme_equal" if ok else "phoneme_differs"
    return ok


def multiword_span_equivalent_v3(canon_span, asr_span, entity_like: bool = False, *, detail=None) -> bool:
    """承認済み判定(Trial v3): V8 + entity_like代表発音限定 + 上記ガード。純関数(副作用なし)。"""
    d = detail if detail is not None else {}
    c, a = list(canon_span), list(asr_span)
    multi = c if len(c) > 1 else a
    if len(multi) > 1 and any(len(t) == 2 and t not in FW2 for t in multi):
        d["why"] = "two_letter_non_function_word(V8_bius_guard)"; return False
    if entity_like:
        if not multiword_span_equivalent(c, a, detail=d):
            return False
        vc, va = joint_variants(c, True), joint_variants(a, True)
        if vc is None or va is None:
            d["why"] = "OOV_or_too_many_variants"; return False
        ok = bool(vc & va)
        d["why"] = "phoneme_equal_representative" if ok else "differs_in_representative_only"
        return ok
    return multiword_span_equivalent(c, a, detail=d)


def multiword_homophone_candidate(canon_span, asr_span, entity_like: bool = False) -> bool:
    """配線用の入口(A-2で val.protected_check から呼ぶ唯一の関数)。MULTIWORD_HOMOPHONE_ENABLED=Falseなら常にFalse
    (=現行挙動とバイト一致)。例外は握りつぶして非救済(fail-closed: 救済しない側)。"""
    if not MULTIWORD_HOMOPHONE_ENABLED:
        return False
    try:
        return bool(multiword_span_equivalent_v3(canon_span, asr_span, entity_like))
    except Exception:
        return False
