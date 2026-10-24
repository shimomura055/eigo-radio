# trial_oov_ledger_m1_01.py -- ASR-OOV-HOMOPHONE-ROOT-CAUSE-01 委任_01 Trial専用(Production無変更・どのProduction fileからもimportされない)。
# 候補E: 『Ledger読み付きCMU-OOV語を、M1の入口で entity_like 相当に扱う』ときの判定を、既存 M1 module(無変更)を呼んでオフライン再判定する。
#   - 既存 er006_m1_multi_candidate_01 の判定核(音素一致・F1 post-check・Pattern A/B/C限定)は一切変更しない。
#   - 変えるのは入口の1点のみ: base_cls が TRUE_CONTENT_MISMATCH でも、content_word_diffs の全 canonical 語が
#     『CMU未収録かつ凍結済みLedger C2候補(IPA→ARPAbet変換済)を持つ語』だけの場合に限り、その diff を entity_like 扱いに昇格して M1 に渡す。
#   - 数値/否定(protected)が通らない・C2候補が無い・ASR語がCMU未収録・音素不一致・他の内容差が残る場合は従来どおり非受理(TRUE_CONTENT_MISMATCHのまま)。
import copy, dataclasses, sys
sys.path.insert(0, ".")
import er006_preprod_hardening_01_validation as val
import er006_m1_multi_candidate_01 as m1

def _backed_words(frozen):
    return {fw.word for fw in frozen.words if any(c.source.startswith("C2_") for c in fw.candidates)}

def judge_relaxed(canonical, asr, frozen, *, segment_id=None):
    """returns dict(outcome, base, m1_reason, promoted, accepted, subs)"""
    base = val.classify_asr_match(canonical, asr, segment_id=segment_id)
    out = {"base": base.classification, "base_should_pass": base.should_pass, "promoted": False, "accepted": False, "m1_reason": None, "subs": []}
    if base.should_pass:
        out["outcome"] = "BASE_PASS"; return out
    if base.classification == "ASR_VALIDATION_UNCERTAIN":
        r = m1.m1_multi_candidate_judge(canonical, asr, frozen, base_cls=base)
        out.update(accepted=r.accepted, m1_reason=r.reason, subs=[(s["from"], s["to"], s["canonical_word"], s["source"]) for s in r.subs])
        out["outcome"] = "M1_ACCEPT(existing_gate)" if r.accepted else "UNCERTAIN_NO_M1"; return out
    if base.classification != "TRUE_CONTENT_MISMATCH" or not base.protected.passed:
        out["outcome"] = "UNCHANGED:" + base.classification; return out
    diffs = base.protected.content_word_diffs
    backed = _backed_words(frozen)
    if not diffs:
        out["outcome"] = "UNCHANGED:no_content_word_diffs"; return out
    for d in diffs:
        cw = [w for w in m1._tokens(d.get("canonical", ""))]
        if not cw or not all(w in backed for w in cw):
            out["outcome"] = "UNCHANGED:non_backed_content_diff"; return out
    promoted = copy.deepcopy(base)
    for d in promoted.protected.content_word_diffs:
        d["entity_like"] = True
    promoted = dataclasses.replace(promoted, classification="ASR_VALIDATION_UNCERTAIN")
    out["promoted"] = True
    r = m1.m1_multi_candidate_judge(canonical, asr, frozen, base_cls=promoted)
    out.update(accepted=r.accepted, m1_reason=r.reason, subs=[(s["from"], s["to"], s["canonical_word"], s["source"]) for s in r.subs])
    out["outcome"] = "M1_ACCEPT(relaxed_gate)" if r.accepted else "PROMOTED_BUT_NO_M1:" + str(r.reason)
    return out
