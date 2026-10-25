# OPEN-333系 第2の漏れ(E4=cascade-eligible差分の便乗PASS)と、E3の副作用(E4-N)の評価用proto v3 = E3v3+E4+E4-N。DEV/proto専用。Production fileは変更しない。
# (proto_open333_fix_05.py=E3v3+E4 は凍結物のため変更しない。本ファイルはHEAD[E3適用済み]の上に重ねる。)
# E4  : Candidate Eが救済(PASS)する直前、protected.content_diffs に cascade_eligible 差分(entity_like=カタカナ/略語同士、phonetic_uncertain=濁点のみ差)が
#       1つでも残るなら、PASSにせず既存の `_cascade` と同じ ASR_VALIDATION_UNCERTAIN(Cascade=Azure再確認)を返す。
# E4-N: 数値entryでE3(全差分再検査)が『説明できない非数値差』を理由にEを拒否する(return None -> TRUE_CONTENT_MISMATCH)とき、
#       説明できない差が【全て】cascade_eligible(protected_check_jaと同じ述語: replace かつ entity_like[両側カタカナ/略語] または 濁点のみ差)で、
#       かつ値ガードが EQUAL/NO_VALUES/AMBIGUOUS なら、拒否ではなく既存 `_cascade` を返す。非数値entryなら元来Cascade行きの差の整合化。PASSは増えない。
#       1つでも非cascade差(しわ->すわ等)・値ガードDIFF/UNKNOWN・helper例外があれば従来どおり拒否(return None)。
# mode: E4 = E4のみ(fix_05の E3V_E4 と同義) / E4N = E4-Nのみ / E4_E4N = 両方
import contextlib, difflib, sys
sys.path.insert(0, ".")
import er007_ja_asr_validator_01 as javal
import er011_ja_asr_variant_layer_01 as VL
import proto_open333_fix_04 as B4
import proto_open333_fix_05 as B5

MODES = ("E4", "E4N", "E4_E4N")
is_e_pass = B4.is_e_pass


def audit_e3_classified(c_norm: str, a_norm: str) -> list:
    """B4.audit_e3 と同じ検査(未説明の差のlist)に、各差のcascade_eligible判定を付ける。例外は『説明できない・cascade不可』(fail-closed)。"""
    try:
        sc, sa = B4.mask_values(c_norm), B4.mask_values(a_norm)
        bad = []
        n = javal._READING_CONTEXT_CHARS
        sm = difflib.SequenceMatcher(None, sc, sa, autojunk=False)
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == "equal":
                continue
            cs, as_ = sc[i1:i2].replace(B4.PH, ""), sa[j1:j2].replace(B4.PH, "")
            if not cs and not as_:
                continue
            cp = sc[max(0, i1 - n):i2 + n].replace(B4.PH, "")
            ap = sa[max(0, j1 - n):j2 + n].replace(B4.PH, "")
            if B4.explained(cs, as_, cp, ap):
                continue
            both = tag == "replace" and bool(cs) and bool(as_)
            ent = both and javal._is_katakana_or_acronym(cs) and javal._is_katakana_or_acronym(as_)
            ph = both and javal._reading_equal_allowing_voicing(cp, ap)
            bad.append({"canonical": cs, "asr": as_, "kind": "unexplained_non_numeric_diff",
                        "entity_like": bool(ent), "phonetic_uncertain": bool(ph), "cascade_eligible": bool(ent or ph)})
        return bad
    except Exception as exc:  # noqa: BLE001 fail-closed
        return [{"canonical": "", "asr": "", "kind": f"helper_error:{type(exc).__name__}", "cascade_eligible": False}]


def e4n_decision(canonical_text, asr_text, c_norm, a_norm):
    """(cascade可否, 拒否理由list)。cascade可 = 説明できない差が1件以上あり全てcascade_eligible かつ 値ガードOK。"""
    items = audit_e3_classified(c_norm, a_norm)
    veto = B4.value_veto(canonical_text, asr_text)
    ok = bool(items) and all(i["cascade_eligible"] for i in items) and veto is None
    return ok, items, veto


def _cascade(protected, ratio, reason):
    return javal.ClassificationResultJA("ASR_VALIDATION_UNCERTAIN", ratio, protected, should_pass=False, should_retry=False, reason=reason)


@contextlib.contextmanager
def apply_in_process(mode, log=None):
    assert mode in MODES
    use_e4 = mode in ("E4", "E4_E4N")
    use_n = mode in ("E4N", "E4_E4N")
    orig = VL.try_rescue_before_resolver

    def patched(canonical_text, asr_text, c_norm, a_norm, ratio, protected):
        res = orig(canonical_text, asr_text, c_norm, a_norm, ratio, protected)
        num = bool(protected.number_mismatches)
        if res is None and use_n and num and getattr(protected, "candidate_e_rejections", None):
            ok, items, veto = e4n_decision(canonical_text, asr_text, c_norm, a_norm)
            if ok:
                if log is not None:
                    log.append((canonical_text, asr_text, mode, "e4n", [(i["canonical"], i["asr"]) for i in items]))
                return _cascade(protected, ratio, "(proto E4-N)Candidate Eは数値entryの未説明差を理由に拒否したが、その差が全てcascade_eligible(カタカナ/略語・濁点のみ差)のため既存のCascade対象へ")
            return res
        if not is_e_pass(res):
            return res
        if num:                                    # HEADにE3が無い構成(rollback)でも同じ結論になるようにする(HEADがE3 ONなら到達しない)
            ok, items, veto = e4n_decision(canonical_text, asr_text, c_norm, a_norm)
            bad = B4.rejections("E3V", canonical_text, asr_text, c_norm, a_norm)
            if bad:
                if use_n and ok:
                    return _cascade(protected, ratio, "(proto E4-N)")
                return None
        if use_e4:
            hits = B5.e4_hits("E3V_E4", protected)
            if hits:
                if log is not None:
                    log.append((canonical_text, asr_text, mode, "e4", [(d["canonical"], d["asr"]) for d in hits]))
                return _cascade(protected, ratio, "(proto E4)Candidate Eは救済したが、cascade_eligible差分(カタカナ/略語・濁点のみ差)が未検査で残るためCascade対象")
        return res
    VL.try_rescue_before_resolver = patched
    try:
        yield
    finally:
        VL.try_rescue_before_resolver = orig
