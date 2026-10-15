# AUW(ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01) 委任_05: leaf -> 統一judge adapter へ渡す attempt_ctx の組立て(純関数)。
#
# 目的: HR queue投入を「最終slotのNGのみ」へ統一する(DESIGN_01 §4-7 / 原文「3回とも不合格の場合、既存の安全条件に従いLocal Rewrite
#       またはHuman Reviewへ進む」)。adapter(er006/er007)は attempt_ctx["is_last_slot"] が True かつ NG のときだけ
#       human_review_required=True を返し、wrapperがHR queueへ(重複排除付きで)追記する。leaf側のHR Lock
#       (er011_human_review_lock_01: guarded_generate/record_outcome)は無変更で、最終STOPPEDで従来どおり動く。
#
# 規約(slotは segment通算のTTS生成番号。標準経路/fallback経路/KP 4回構成の入れ子をまたいで通算する):
#   slot        = slot_offset + attempt
#   is_last_slot = slot >= total_slots        (total_slots 省略時は slot_offset + max_attempts)
# 標準経路ループ(後段にfallbackがある)は total_slots を通算上限に揃えて渡す。これにより「後続のslotが残っているNG」では
# HR queueへ投入されない。Local Rewrite後のv1再TTSは script_version="v1" で渡す(LR_REWRITTENがPASS_WITH_WARNING扱い)。
# 値の変更・閾値・Prompt・回数は一切含まない(組立てのみ)。
from __future__ import annotations

from typing import Optional


def build_attempt_ctx(attempt: int, max_attempts: int, *, slot_offset: int = 0, total_slots: Optional[int] = None,
                      script_version: str = "v0", length_ok: Optional[bool] = None,
                      segment_key: Optional[str] = None) -> dict:
    slot = int(slot_offset) + int(attempt)
    total = int(total_slots) if total_slots is not None else int(slot_offset) + int(max_attempts)
    ctx = {"slot": slot, "is_last_slot": slot >= total, "script_version": script_version}
    if length_ok is not None:
        ctx["length_ok"] = bool(length_ok)
    if segment_key:
        ctx["segment_key"] = segment_key
    return ctx
