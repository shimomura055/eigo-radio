# OPEN-333系(しわ↔すわ=N3-07)是正案プロトタイプ。DEV/proto専用。Production fileは一切変更しない。
# 原因(open333_trace_01.out.txt): er007 protected_check_ja は『数字が左右で異なるopcode』を number_mismatches に記録して `continue` し、
#   そのopcodeに糊付けされた非数値部分(例: 'しわ8,900'->'巣は八千九百' の しわ->巣は)を content_diffs へ入れない。
#   er011 Candidate E(try_rescue_before_resolver)は content_diffs だけを見るので、その部分が未検査のまま『残差分は全て説明できた』となる。
# 本protoは try_rescue_before_resolver の戻りだけを後処理で拒否する(Production関数をimportして呼び、差分だけ上書き。PASS集合は縮む方向のみ=単調)。
#   mode:
#     E1 = 数値opcodeの残余監査: protected_checkが飛ばした『数字が異なるopcode』の非数値部分(数字・漢数字run・桁区切りcommaを除去)が
#          (一致 | 読み一致 | Candidate E候補読みの共通)のいずれかで説明できなければ拒否。
#     E3 = 数値除去後の全文再比較: 両全文から数値を除去し、その文字列をSequenceMatcherで全差分を取り直し、Productionが非数値差分へ課すのと同じ検査
#          (読み一致 | E候補共通。窓幅も同じ)で全件説明できなければ拒否(opcodeの切れ方=アラインメントに依存しない)。
#     E2 = (粗い比較案)数値不一致entryではCandidate Eを使わない。
import contextlib, difflib, re, sys
sys.path.insert(0, ".")
import er007_ja_asr_validator_01 as javal
import er011_ja_asr_variant_layer_01 as VL

_NUM_RUN = re.compile(r"[〇一二三四五六七八九十百千万]+")
_COMMA = re.compile(r"(?<=\d),(?=\d)")
_DIGITS = re.compile(r"\d+")
MODES = ("E1", "E2", "E3")


def strip_numerals(s: str) -> str:
    s = _COMMA.sub("", s or "")
    s = _DIGITS.sub("", s)
    return _NUM_RUN.sub("", s)


def explained(c: str, a: str, c_pad: str = None, a_pad: str = None) -> bool:
    """Productionが非数値差分へ課す検査と同じ2段(読み一致で許容 / Candidate E候補読みの共通)。"""
    if c == a or (not c and not a):
        return True
    if javal._reading_equal(c_pad if c_pad is not None else c, a_pad if a_pad is not None else a):
        return True
    return VL._span_pair_reading_variant_match(c, a)


def audit_e1(c_norm: str, a_norm: str) -> list:
    """未説明の(c,a)残余のlistを返す(空=全て説明済み)。"""
    bad = []
    sm = difflib.SequenceMatcher(None, c_norm, a_norm, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        cs, as_ = c_norm[i1:i2], a_norm[j1:j2]
        cn, an = javal._DIGIT_RE.findall(cs), javal._DIGIT_RE.findall(as_)
        if not (cn != an and (cn or an)):
            continue          # 数値opcodeでないものはProductionのcontent_diffsが既に検査済み
        rc, ra = strip_numerals(cs), strip_numerals(as_)
        if not explained(rc, ra):
            bad.append((rc, ra))
    return bad


def audit_e3(c_norm: str, a_norm: str) -> list:
    sc, sa = strip_numerals(c_norm), strip_numerals(a_norm)
    bad = []
    n = javal._READING_CONTEXT_CHARS
    sm = difflib.SequenceMatcher(None, sc, sa, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        cs, as_ = sc[i1:i2], sa[j1:j2]
        cp, ap = sc[max(0, i1 - n):i2 + n], sa[max(0, j1 - n):j2 + n]
        if not explained(cs, as_, cp, ap):
            bad.append((cs, as_))
    return bad


def is_e_pass(res) -> bool:
    return res is not None and "Candidate E" in (res.reason or "")


@contextlib.contextmanager
def apply_in_process(mode: str, log=None):
    assert mode in MODES
    orig = VL.try_rescue_before_resolver

    def patched(canonical_text, asr_text, c_norm, a_norm, ratio, protected):
        res = orig(canonical_text, asr_text, c_norm, a_norm, ratio, protected)
        if not is_e_pass(res) or not protected.number_mismatches:
            return res        # E以外の判定・非数値entryは無変更
        if mode == "E2":
            bad = [("*", "*")]
        elif mode == "E1":
            bad = audit_e1(c_norm, a_norm)
        else:
            bad = audit_e3(c_norm, a_norm)
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
