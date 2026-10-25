# OPEN-333系 第2の漏れ(E4=cascade-eligible差分の便乗PASS)評価用proto v2 = E3v3(proto_open333_fix_04、P-1なし)+E4。DEV/proto専用。Production fileは一切変更しない。
# (proto_open333_fix_03.py=委任_11のE3P+E4 protoは凍結物のため変更せず、E3v3ベースで作り直した。)
# E4: Candidate Eが non-cascade 差分を救済したとき、cascade_eligible差分(entity_like=カタカナ/略語同士、phonetic_uncertain=濁点/半濁点のみの差)が
#     protected.content_diffs に1つでも残るなら、E-PASSにせず ASR_VALIDATION_UNCERTAIN(Cascade=Azure再確認)を返す。元来Cascadeへ回る差分の復元であり、PASS集合は縮む方向のみ。
# mode:
#   E3V       = proto_open333_fix_04のE3V(比較用の再エクスポート)
#   E3V_E4    = E3V + E4(cascade_eligible全般: entity_like と phonetic_uncertain)
#   E3V_E4E   = E3V + E4(entity_likeのみ。濁点のみ差は従来どおり便乗を許す、E4の狭い版)
import contextlib, sys
sys.path.insert(0, ".")
import er007_ja_asr_validator_01 as javal
import er011_ja_asr_variant_layer_01 as VL
import proto_open333_fix_04 as B4

MODES = ("E3V", "E3V_E4", "E3V_E4E")
is_e_pass = B4.is_e_pass


def e4_hits(mode, protected):
    ds = protected.content_diffs or []
    if mode == "E3V_E4":
        return [d for d in ds if d.get("cascade_eligible")]
    if mode == "E3V_E4E":
        return [d for d in ds if d.get("entity_like")]
    return []


@contextlib.contextmanager
def apply_in_process(mode, log=None):
    assert mode in MODES
    orig = VL.try_rescue_before_resolver

    def patched(canonical_text, asr_text, c_norm, a_norm, ratio, protected):
        res = orig(canonical_text, asr_text, c_norm, a_norm, ratio, protected)
        if not is_e_pass(res):
            return res
        if protected.number_mismatches:
            bad = B4.rejections("E3V", canonical_text, asr_text, c_norm, a_norm)
            if bad:
                if log is not None:
                    log.append((canonical_text, asr_text, mode, "e3", bad))
                return None
        hits = e4_hits(mode, protected)
        if hits:
            if log is not None:
                log.append((canonical_text, asr_text, mode, "e4", [(d["canonical"], d["asr"]) for d in hits]))
            return javal.ClassificationResultJA(
                "ASR_VALIDATION_UNCERTAIN", ratio, protected, should_pass=False, should_retry=False,
                reason="(proto E4)Candidate Eは救済したが、cascade_eligible差分(カタカナ/略語・濁点のみ差)が未検査で残るためCascade対象")
        return res
    VL.try_rescue_before_resolver = patched
    try:
        yield
    finally:
        VL.try_rescue_before_resolver = orig
