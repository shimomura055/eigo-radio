# OPEN-333系(しわ↔すわ=N3-07)是正案 proto v3 = E3(P-1なし)。DEV/proto専用。Production fileは一切変更しない。
# (注: 委任_12は『proto_open333_fix_03.py』と指定したが、同名は委任_11でE4 protoとして事前登録・凍結済み[sha 444bbe24…]のため、
#  凍結物を上書きしない目的で v3 を fix_04、E3v3+E4 を fix_05 とした。)
# v2(proto_open333_fix_02.py、凍結)からの差分 = Opus独立レビュー(OPUS_REVIEW_01_OPEN333.md)の反映:
#   P-1(助詞免除、explained_p)を除去(R-3/Fable判断: 未承認のB-light v2規則を不具合是正に混ぜない)。
#   R-2: 数値の剥がし方を、値ガード(er078 extract_atoms_ja)が数値と認識したspan(num/frac/approx/unparsed)に限定し、
#        削除ではなく両側を同じplaceholderへ置換してアラインメントする。語中の漢数字(一緒・千葉・九州)は剥がさない。
#        差分spanの説明検査ではplaceholderを除いた残り(非数値部分)だけを見る(値そのものの一致は値ガードが担当)。
#   M-5相当: helper内の例外は『説明できない=拒否』(fail-closed)。
#   R-6: 数値entry(protected.number_mismatches)のE-PASSは、値ガード(final gateと同じ F2付き value_guard_kana_unified)が
#        EQUAL/NO_VALUES/AMBIGUOUS のときだけ許す(DIFF/UNKNOWN=拒否)。判定を広げない方向のみ(多層防御)。
#   mode: E3 = 非数値差の全件再検査のみ(P-1なし) / E3V = E3 + 値ガード要求(R-6)。
import contextlib, difflib, sys, unicodedata
sys.path.insert(0, ".")
import er007_ja_asr_validator_01 as javal
import er011_ja_asr_variant_layer_01 as VL
import er078_asr_value_guard_01 as vg

MODES = ("E3", "E3V")
PH = ""
_MASK_KINDS = ("num", "frac", "approx", "unparsed")


def mask_values(norm_text: str) -> str:
    t = unicodedata.normalize("NFKC", norm_text or "")
    atoms = [a for a in vg.extract_atoms_ja(t) if a.kind in _MASK_KINDS]
    atoms.sort(key=lambda a: a.start)
    out, pos = [], 0
    for a in atoms:
        if a.start < pos:
            continue
        out.append(t[pos:a.start]); out.append(PH); pos = a.end
    out.append(t[pos:])
    return "".join(out)


def explained(c: str, a: str, c_pad: str, a_pad: str) -> bool:
    """Productionが非数値差分へ課す検査と同じ2段(読み一致 / Candidate E候補読みの共通)。P-1なし。"""
    if c == a or (not c and not a):
        return True
    if javal._reading_equal(c_pad, a_pad):
        return True
    return VL._span_pair_reading_variant_match(c, a)


def audit_e3(c_norm: str, a_norm: str) -> list:
    """未説明の(c,a)のlist(空=全て説明済み)。例外は拒否(fail-closed)。"""
    try:
        sc, sa = mask_values(c_norm), mask_values(a_norm)
        bad = []
        n = javal._READING_CONTEXT_CHARS
        sm = difflib.SequenceMatcher(None, sc, sa, autojunk=False)
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == "equal":
                continue
            cs, as_ = sc[i1:i2].replace(PH, ""), sa[j1:j2].replace(PH, "")
            if not cs and not as_:
                continue          # 値spanのみの差(値の一致は値ガードの担当)
            cp = sc[max(0, i1 - n):i2 + n].replace(PH, "")
            ap = sa[max(0, j1 - n):j2 + n].replace(PH, "")
            if not explained(cs, as_, cp, ap):
                bad.append((cs, as_))
        return bad
    except Exception as exc:  # noqa: BLE001 fail-closed
        return [("<error>", type(exc).__name__)]


def value_veto(canonical_text: str, asr_text: str):
    try:
        g = vg.value_guard_kana_unified(canonical_text, asr_text, "ja")
    except Exception as exc:  # noqa: BLE001 fail-closed
        return ("<value_guard_error>", type(exc).__name__)
    if g.kind in (vg.EQUAL, vg.NO_VALUES, vg.AMBIGUOUS):
        return None
    return ("<value_guard>", g.kind)


def is_e_pass(res) -> bool:
    return res is not None and "Candidate E" in (res.reason or "")


def rejections(mode, canonical_text, asr_text, c_norm, a_norm):
    bad = list(audit_e3(c_norm, a_norm))
    if mode == "E3V":
        v = value_veto(canonical_text, asr_text)
        if v:
            bad.append(v)
    return bad


@contextlib.contextmanager
def apply_in_process(mode, log=None):
    assert mode in MODES
    orig = VL.try_rescue_before_resolver

    def patched(canonical_text, asr_text, c_norm, a_norm, ratio, protected):
        res = orig(canonical_text, asr_text, c_norm, a_norm, ratio, protected)
        if not is_e_pass(res) or not protected.number_mismatches:
            return res
        bad = rejections(mode, canonical_text, asr_text, c_norm, a_norm)
        if bad:
            if log is not None:
                log.append((canonical_text, asr_text, mode, bad))
            return None
        return res
    VL.try_rescue_before_resolver = patched
    try:
        yield
    finally:
        VL.try_rescue_before_resolver = orig
