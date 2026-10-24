# trial_direct_ledger_phoneme_01.py -- ASR-OOV-HOMOPHONE-ROOT-CAUSE-01 委任_01 Trial専用(Production無変更・Productionからimportされない)。
# 候補E2『Ledger読みへの直接音素一致(OF-184で需要測定待ちとされた"直接音素置換")』のオフライン実装。
# 受理条件(すべて):
#   (1) Production分類がTRUE_CONTENT_MISMATCH/ASR_VALIDATION_UNCERTAINで protected(数値・否定)通過、should_passでない
#   (2) 内容語差が『canonical 1語 -> ASR 1語』のreplaceだけ(複数語・脱落・挿入は対象外)
#   (3) canonical語は CMU未収録 かつ 凍結済みLedger C2候補(sources非空・ledger_disabled無・canonical_spelling==surface・IPA変換可・segment開始前)を持つ
#   (4) ASR語は CMU収録語で、その代表発音(rank0)のストレス除去済み音素列が C2候補のいずれかと完全一致
#   (5) ASR語をcanonical語へ置換した転写を Production classify_asr_match に再投入して should_pass(=他に差が1つも残らない)
# 既存 er006_m1_multi_candidate_01 の凍結候補(freeze_candidates)・IPA変換(ipa_to_arpa)は無変更で再利用する。新規辞書・G2P・閾値は無い。
import copy, sys, re
sys.path.insert(0, ".")
import er006_preprod_hardening_01_validation as val
import er006_m1_multi_candidate_01 as m1

def judge_direct(canonical, asr, frozen, *, segment_id=None, min_conf=("low", "medium", "high")):
    base = val.classify_asr_match(canonical, asr, segment_id=segment_id)
    r = {"base": base.classification, "accepted": False, "reason": None, "sub": None}
    if base.should_pass:
        r["reason"] = "BASE_PASS"; return r
    if base.classification not in ("TRUE_CONTENT_MISMATCH", "ASR_VALIDATION_UNCERTAIN") or not base.protected.passed:
        r["reason"] = "NOT_ELIGIBLE:" + base.classification; return r
    diffs = base.protected.content_word_diffs
    if len(diffs) != 1 or diffs[0].get("type") != "replace":
        r["reason"] = "NOT_SINGLE_REPLACE"; return r
    d = diffs[0]
    cw, aw = m1._tokens(d["canonical"]), m1._tokens(d["asr"])
    if len(cw) != 1 or len(aw) != 1:
        r["reason"] = "NOT_1TO1"; return r
    c, a = cw[0], aw[0]
    fw = frozen.word(c)
    cands = [x for x in (fw.candidates if fw else ()) if x.source.startswith("C2_") and x.confidence in min_conf]
    if not cands:
        r["reason"] = "NO_C2_CANDIDATE"; return r
    avs = [tuple(v) for v in m1.default_cmu(a)]
    if not avs:
        r["reason"] = "ASR_WORD_NOT_IN_CMU"; return r
    hit = [x for x in cands if avs[0] == tuple(x.pron)]
    if not hit:
        r["reason"] = "NO_PHONEME_MATCH"; return r
    asr2 = m1._replace_tokens(asr, {i: c for i, t in enumerate(m1._tokens(asr)) if t == a and True})
    # 置換は差分位置のみ: 同一語が他所にある場合は全置換になるが、その場合も再判定でshould_passを要求するため安全側
    post = val.classify_asr_match(canonical, asr2, segment_id=segment_id)
    if not post.should_pass:
        r["reason"] = "POST_CHECK_FAIL:" + post.classification; return r
    r.update(accepted=True, reason="E2_LEDGER_PHONEME_ACCEPT", sub={"canonical": c, "asr": a, "pron": list(avs[0]), "source": hit[0].source,
             "confidence": hit[0].confidence, "ledger_key": hit[0].ledger_key, "ipa_raw": hit[0].ipa_raw, "post": post.classification})
    return r
