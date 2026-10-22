# ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01 (AUW) 委任_06c (OF-AUW-C-03、DESIGN_02_ADDENDUM_01 §3-1)
# 既存音声の再利用点(同一out_dirの前回results・Master Audio Store・Z generate_or_reuse_z・C resumable_reuse・
# Family X validation inheritance)で、再利用前に**保存転写のみ**(API 0・Secondary新規呼出0)を現行の統一judgeへ通し、
# 値ガードDIFF/否定差(最終ANDゲートの保護差)が検出された場合は再利用せず再生成へ回す。
#
# 方針(fail-open は「判定できない」場合のみ):
#   - 保存転写/canonical textが無い、または再判定が例外 -> 従来どおり再利用(blocked=False、reasonへ記録)。旧資産を全再生成しない。
#   - 再判定のreason_codeが保護差(値DIFF/否定差/protected_diff)の場合のみ blocked=True。それ以外のNG(許容集合外等)は再利用を止めない
#     (元の正式Validationで受理済み。F1等の判定器差分で動く領域を再生成コストに転嫁しない)。
#   - 一括再判定scriptが付けた `reuse_blocked` mark(削除ではなく再利用禁止の印)を持つ資産は常に blocked。
# Productionの判定ロジック・閾値・Prompt・HR Lockは変更しない(再利用可否の前段ガードの追加のみ)。
from __future__ import annotations

import re

_JA_CHAR_RE = re.compile(r"[぀-ヿ㐀-䶿一-鿿]")

PROTECTED_REASON_PREFIXES = (
    "final_gate_value_diff", "final_gate_negation_diff", "p1_value_diff", "p1_negation_diff", "p1_protected_diff",
    "secondary_value_diff", "secondary_negation_diff",
)


def has_ja_chars(text) -> bool:
    return bool(text and _JA_CHAR_RE.search(str(text)))


def is_protected_reason(reason_code: str) -> bool:
    return bool(reason_code) and any(str(reason_code).startswith(p) for p in PROTECTED_REASON_PREFIXES)


def guard_entry(entry, *, label: str = "", canonical_text: str | None = None, level: str | None = None,
                kp_vote_gate_follows: bool = False) -> dict:
    """再利用しようとしているentry(results entry / Master Store qa_evidence+key / .ok meta 相当のdict)を保存転写で再判定する。
    戻り値: {blocked, applicable, reason, unified_state, reason_code, api_calls(=0)}。例外を投げない。

    kp_vote_gate_follows(2026-10-22 KP-QUALITY-2ITEMS、OF-KPQ-P-01): True = このentryはKP英語で、**呼出元が直後にKP 3-ASR vote gate
    (`kp_vote_reuse_ok`/`KpVoteReuseGate`)を必ず通す**。KP英語は数値・否定の保護を解除した(ユーザー承認2026-10-22)ため、vote gateの手前の
    保存転写・保護差再判定をskipする(`reuse_blocked`明示markとPNAP範囲外判定は従来どおり)。labelでは判定しない(A/B/Cの
    `key_phrase_english_component`はvote gateが後続しないため保護を維持する。vote無効=rollback時も呼出元がFalseを渡す)。既定False=従来どおり。"""
    out = {"blocked": False, "applicable": False, "reason": "", "unified_state": None, "reason_code": None,
           "api_calls": 0, "secondary_new_calls": 0}
    if not isinstance(entry, dict):
        out["reason"] = "NO_ENTRY"
        return out
    mark = entry.get("reuse_blocked")
    if mark:
        out.update(blocked=True, applicable=True, reason="REUSE_BLOCKED_MARK", reuse_blocked_mark=mark)
        return out
    # PNAP 委任_02(OF-PNAP-P-05(ii)): 固有名詞アラーム受理音声(state=PASS_WITH_PRONUNCIATION_ALARM)は、承認範囲(Family X/Z run scope内∧flag有効)の
    # 外では再利用しない(Master Audio StoreはA/B/Cとも共有のため、X/Zで受理した音声がA/B/CやDefault OFF時に流入しないようにする)。再生成へ回す。
    _aj0 = entry.get("asr_judgement") or entry.get("asr_judgement_inherited")
    if isinstance(_aj0, dict) and _aj0.get("state") == "PASS_WITH_PRONUNCIATION_ALARM":
        import er103_proper_noun_alarm_policy_01 as _pnap
        if not _pnap.is_active_for_run():
            out.update(blocked=True, applicable=True, reason="PRONUNCIATION_ALARM_AUDIO_OUT_OF_SCOPE")
            return out
    if kp_vote_gate_follows:
        out.update(applicable=False, reason="KP_EN_VOTE_GATE_DECIDES")
        return out
    asr_text = entry.get("asr_text")
    if not asr_text:  # C `.ok.meta.json`等、asr_textを持たず統一judge recordだけを保存している資産
        _aj = entry.get("asr_judgement") or entry.get("asr_judgement_inherited") or {}
        asr_text = (_aj.get("primary") or {}).get("text") if isinstance(_aj, dict) else None
    base = canonical_text or entry.get("text") or entry.get("canonical_text")
    if not asr_text or not base:
        out["reason"] = "NO_TRANSCRIPT_NOT_JUDGEABLE"
        return out
    probe = dict(entry)
    probe["text"] = base
    probe["asr_text"] = asr_text
    try:
        import er019_family_x_validation_inheritance_01 as vi
        lang = "ja" if has_ja_chars(base) else "en"
        rj = vi.rejudge_with_current_judge(probe, level or ("a2" if lang == "ja" else "b1b"), label or "reuse", force_lang=lang)
    except Exception as exc:  # noqa: BLE001  判定不能=従来どおり(再利用を止めない)。記録のみ。
        out["reason"] = f"REJUDGE_ERROR:{type(exc).__name__}"
        return out
    out.update(applicable=True, unified_state=rj.get("unified_state"), reason_code=rj.get("unified_reason_code"),
               secondary_new_calls=int(rj.get("secondary_new_calls", 0)))
    if rj.get("ok"):
        out["reason"] = "REJUDGE_OK"
        return out
    if is_protected_reason(rj.get("unified_reason_code") or ""):
        out.update(blocked=True, reason=f"PROTECTED_DIFF:{rj.get('unified_reason_code')}")
        return out
    out["reason"] = f"REJUDGE_NG_NOT_PROTECTED:{rj.get('reason')}"
    return out
