"""PNMH-PLAN-01 (計画段階・API 0・Production無変更): 提案方式(A) "span限定の音韻列連結比較" の
**オフライン試作**。Productionコードは一切編集しない。protected_checkのソースをメモリ上でpatchして
(1:1 homophone判定の直後に本関数を追加呼出)、保存済みペアへ before/after を再適用する。
本ファイルは計画の根拠測定用であり、Production経路・DEV経路のいずれにも配線されない。"""
import re, sys, os, json, inspect, itertools
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
os.chdir(ROOT); sys.path.insert(0, ROOT)
import pronouncing
import er006_preprod_hardening_01_validation as val
import er008_asr_variant_hardening_15_homophone_en as hp

MAX_SIDE = 3          # 片側の最大token数
MAX_JOINT = 64        # 発音variant直積の上限(超過は判定不能=安全側で非救済)

def _strip(ph): return re.sub(r"\d", "", ph)

def _variants_nostress(tok, representative_only=False):
    ps = pronouncing.phones_for_word(tok)
    if not ps: return None
    if representative_only: ps = ps[:1]   # v3: 固有名詞らしい語(entity_like)は代表発音(CMU先頭variant)のみ。measure_v2_01.py の rep と同一
    return sorted({tuple(_strip(p).split()) for p in ps})

def joint_variants(tokens, representative_only=False):
    vs = []
    for t in tokens:
        v = _variants_nostress(t, representative_only)
        if v is None: return None
        vs.append(v)
    n = 1
    for v in vs: n *= len(v)
    if n > MAX_JOINT: return None
    return {tuple(x for part in combo for x in part) for combo in itertools.product(*vs)}

_TOK_OK = re.compile(r"^[a-z][a-z']*$")

GUARDS = ({"single_letter": False, "short_canon": False} if os.environ.get("PNMH_NO_GUARDS") == "1" else {"single_letter": True, "short_canon": True})   # ablation用(既定は全ON)
MIN_CANON_TOKEN_LEN = 3   # canonical側tokenの最小文字数(AI/US/AM等の短い略語様tokenを除外。CMUはam/us/aiに文字読みvariant、aiはAY1[eye]を持つため)

def multiword_span_equivalent(canon_span, asr_span, *, detail=None):
    """1語<->連続n語(n=2..3)の置換spanで、連結した音素列(ストレス無視、CMU辞書、全variant)が一致するか。
    ガード: 片側は単語1つ(1:n / n:1に限定)、全tokenが英字のみ、複数語側に1文字token禁止(文字読み a m / u s / a i 対策)、
    数値/否定語は対象外、辞書外(OOV)は判定不能=非救済、span内に脱落/追加が含まれる場合は音素列が一致せず非救済。"""
    d = detail if detail is not None else {}
    c, a = list(canon_span), list(asr_span)
    if not c or not a: d["why"] = "empty_side"; return False
    if len(c) == 1 and len(a) == 1: d["why"] = "one_to_one(existing)"; return False
    if not (len(c) == 1 or len(a) == 1): d["why"] = "both_multi(out_of_scope_v1)"; return False
    if max(len(c), len(a)) > MAX_SIDE: d["why"] = "too_long"; return False
    toks = c + a
    if any(not _TOK_OK.match(t) for t in toks): d["why"] = "non_alpha_token"; return False
    if any(t in val._NEGATION_WORDS or val._is_number(t) for t in toks): d["why"] = "number_or_negation"; return False
    multi = c if len(c) > 1 else a
    if GUARDS["single_letter"] and any(len(t) < 2 for t in multi): d["why"] = "single_letter_token(letter_reading_guard)"; return False
    if GUARDS["short_canon"] and any(len(t) < MIN_CANON_TOKEN_LEN for t in c): d["why"] = "short_canonical_token(acronym_guard)"; return False
    vc, va = joint_variants(c), joint_variants(a)
    if vc is None or va is None: d["why"] = "OOV_or_too_many_variants"; return False
    ok = bool(vc & va)
    d["why"] = "phoneme_equal" if ok else "phoneme_differs"
    return ok

# --- v3 Fix(2026-10-22ユーザー判断反映): V8(2字tokenは閉じた機能語集合のみ=`Bi-us`型NG維持) + entity_like代表発音限定 ---
# 既定のv2挙動(multiword_span_equivalent)は変更しない(再現性)。v3方針は下記のwrapper経由のみ(Trial専用・Production未配線)。
FW2 = {"us", "on", "to", "in", "of", "by", "at", "it", "is", "as", "or", "an", "my", "me", "he", "we", "be", "do", "go", "up", "so", "no", "if", "am", "ok"}

def multiword_span_equivalent_v3(canon_span, asr_span, entity_like=False, *, detail=None):
    d = detail if detail is not None else {}
    c, a = list(canon_span), list(asr_span)
    multi = c if len(c) > 1 else a
    if len(multi) > 1 and any(len(t) == 2 and t not in FW2 for t in multi):
        d["why"] = "two_letter_non_function_word(V8_bius_guard)"; return False
    if entity_like:
        # 代表発音のみで比較(multiword_span_equivalent と同じガード列を通した後、代表発音で再判定)
        if not multiword_span_equivalent(c, a, detail=d): return False
        vc, va = joint_variants(c, True), joint_variants(a, True)
        if vc is None or va is None: d["why"] = "OOV_or_too_many_variants"; return False
        ok = bool(vc & va); d["why"] = "phoneme_equal_representative" if ok else "differs_in_representative_only"; return ok
    return multiword_span_equivalent(c, a, detail=d)

_src = inspect.getsource(val.protected_check)
_OLD = "                    homophone_candidate = bool(result_h)\n"
assert _OLD in _src
_NEW = _OLD + ("                if not homophone_candidate and PROTO_MULTIWORD(canon_span, asr_span):\n"
               "                    homophone_candidate = True\n")
def install_proto():
    ns = val.__dict__
    ns["PROTO_MULTIWORD"] = multiword_span_equivalent
    exec(compile(_src.replace(_OLD, _NEW), "<proto_protected_check>", "exec"), ns)

if __name__ == "__main__":
    for c, a in [(["byus"], ["buy", "us"]), (["byus"], ["by", "us"]), (["us"], ["u", "s"]), (["am"], ["a", "m"]),
                 (["onto"], ["on", "to"]), (["byus"], ["bios"]), (["melos"], ["mellow", "s"]), (["byus"], ["buy"]), (["byus"], ["buy", "us", "an"])]:
        dd = {}; print(c, a, multiword_span_equivalent(c, a, detail=dd), dd)
