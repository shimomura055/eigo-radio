# OPEN-333系 第2の漏れ(『cascade-eligible差分の便乗PASS』)の評価用proto。DEV/proto専用。Production fileは一切変更しない。
# 事実(open333_api0_eval_02.out.txt の棚卸し + scratch確認): Candidate Eの条件 `remaining_diffs and all(...)` の remaining_diffs は non-cascade 差分のみ。
#   entity_like(カタカナ/略語同士: ロ→ラ・ヴェ→ベ・muse→ミューズ)と phonetic_uncertain(濁点/半濁点のみ差)の cascade_eligible 差分は検査されず、
#   他の差分がEで救済されると便乗してPASSになる(現行Production、P4 3件+未知1件)。これは元来 ASR_VALIDATION_UNCERTAIN(Cascade=Azure再確認)へ回る差分。
# mode:
#   E4   = Candidate E救済時に cascade_eligible 差分が1つでも残るなら、E-PASSにせず ASR_VALIDATION_UNCERTAIN(Cascade対象)を返す(両entry)。
#   E3P4 = E3P(proto_open333_fix_02、しわ↔すわの是正案)+ E4。
import contextlib, sys
sys.path.insert(0, ".")
import er007_ja_asr_validator_01 as javal
import er011_ja_asr_variant_layer_01 as VL
import proto_open333_fix_02 as B2

MODES = ("E3P", "E4", "E3P4")
audit_e1, audit_e3, explained_p = B2.audit_e1, B2.audit_e3, B2.explained_p


@contextlib.contextmanager
def apply_in_process(mode, log=None):
    assert mode in MODES
    orig = VL.try_rescue_before_resolver

    def patched(canonical_text, asr_text, c_norm, a_norm, ratio, protected):
        res = orig(canonical_text, asr_text, c_norm, a_norm, ratio, protected)
        if not B2.is_e_pass(res):
            return res
        if mode in ("E3P", "E3P4") and protected.number_mismatches:
            if B2.audit_e3(c_norm, a_norm, B2.explained_p):
                if log is not None:
                    log.append((canonical_text, asr_text, mode, "e3p"))
                return None
        if mode in ("E4", "E3P4") and any(d["cascade_eligible"] for d in protected.content_diffs):
            if log is not None:
                log.append((canonical_text, asr_text, mode, "e4"))
            return javal.ClassificationResultJA(
                "ASR_VALIDATION_UNCERTAIN", ratio, protected, should_pass=False, should_retry=False,
                reason="(proto E4)Candidate Eは救済したが、cascade_eligible差分(カタカナ/略語・濁点のみ差)が未検査で残るためCascade対象")
        return res
    VL.try_rescue_before_resolver = patched
    try:
        yield
    finally:
        VL.try_rescue_before_resolver = orig
