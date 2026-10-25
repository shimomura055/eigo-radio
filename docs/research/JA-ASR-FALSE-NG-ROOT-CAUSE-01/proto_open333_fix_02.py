# OPEN-333系(しわ↔すわ=N3-07)是正案プロトタイプ v2。DEV/proto専用。Production fileは一切変更しない。
# v1(proto_open333_fix_01.py、凍結・変更なし)からの差分 = 事前登録§5の改訂1点のみ:
#   P-1: 『助詞の発音等価』の免除。糊付け残余の説明検査(explained)に、v1の2段(一致|読み一致|E候補共通)に加えて
#        『助詞は→わ・へ→え だけを発音形にした読みが一致』(proto_reading_compare_02.pron_hira)を許す。
#   動機: v1評価で、月題(MOON attempt3_minimalfallback#1: 原稿`しわ`/転写`詩は`=助詞はをwaと読めば同音)が糊付け未検査のため
#         現行Productionでたまたまcorrect PASSになっていて、v1(E1/E3)がこれをNG化した(正常音声の誤NG化=K3違反)。
#         免除は『現行PASSを保つ』方向のみ(PASS集合は現行の部分集合のまま。新規受理なし)。新しい合格条件ではなく、E1/E3が壊す既存の
#         正しいPASSを壊さないための例外。非糊付けの`詩は`↔`しわ`が現行Productionで別途NGになる既存不整合(B-light領域)は触らない。
#   mode: E1P=E1+P-1 / E3P=E3+P-1 / E1,E2,E3=v1と同一(比較用に再エクスポート)。
import contextlib, difflib, sys
sys.path.insert(0, ".")
import er007_ja_asr_validator_01 as javal
import er011_ja_asr_variant_layer_01 as VL
import proto_open333_fix_01 as B
import proto_reading_compare_02 as RC

MODES = ("E1", "E2", "E3", "E1P", "E3P")
strip_numerals = B.strip_numerals
is_e_pass = B.is_e_pass


def explained_p(c, a, c_pad=None, a_pad=None):
    if B.explained(c, a, c_pad, a_pad):
        return True
    try:
        return bool(c) and bool(a) and RC.pron_hira(c) == RC.pron_hira(a)
    except Exception:
        return False


def audit_e1(c_norm, a_norm, exp=B.explained):
    bad = []
    sm = difflib.SequenceMatcher(None, c_norm, a_norm, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        cs, as_ = c_norm[i1:i2], a_norm[j1:j2]
        cn, an = javal._DIGIT_RE.findall(cs), javal._DIGIT_RE.findall(as_)
        if not (cn != an and (cn or an)):
            continue
        rc, ra = strip_numerals(cs), strip_numerals(as_)
        if not exp(rc, ra):
            bad.append((rc, ra))
    return bad


def audit_e3(c_norm, a_norm, exp=B.explained):
    sc, sa = strip_numerals(c_norm), strip_numerals(a_norm)
    bad = []
    n = javal._READING_CONTEXT_CHARS
    sm = difflib.SequenceMatcher(None, sc, sa, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        cs, as_ = sc[i1:i2], sa[j1:j2]
        cp, ap = sc[max(0, i1 - n):i2 + n], sa[max(0, j1 - n):j2 + n]
        if not exp(cs, as_, cp, ap):
            bad.append((cs, as_))
    return bad


@contextlib.contextmanager
def apply_in_process(mode, log=None):
    assert mode in MODES
    orig = VL.try_rescue_before_resolver

    def patched(canonical_text, asr_text, c_norm, a_norm, ratio, protected):
        res = orig(canonical_text, asr_text, c_norm, a_norm, ratio, protected)
        if not is_e_pass(res) or not protected.number_mismatches:
            return res
        if mode == "E2":
            bad = [("*", "*")]
        elif mode == "E1":
            bad = audit_e1(c_norm, a_norm)
        elif mode == "E3":
            bad = audit_e3(c_norm, a_norm)
        elif mode == "E1P":
            bad = audit_e1(c_norm, a_norm, explained_p)
        else:
            bad = audit_e3(c_norm, a_norm, explained_p)
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
