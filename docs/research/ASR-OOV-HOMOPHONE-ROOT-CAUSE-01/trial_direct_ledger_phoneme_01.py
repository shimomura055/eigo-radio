# trial_direct_ledger_phoneme_01.py -- ASR-OOV-HOMOPHONE-ROOT-CAUSE-01 委任_02 Trial専用(Production無変更・Productionからimportされない)。
# 候補E2『Ledgerの出典付き読み(M1がsegment開始前に凍結したC2候補)への直接音素一致(OF-184で需要測定待ちとされた"直接音素置換")』。
# 委任_01版からの変更(Opus OF-OOV-01/02):
#   OF-OOV-01  置換は揃えた位置の1か所のみ(全出現置換を廃止)/置換後判定=classify should_pass かつ F1残差0(’修正後)/
#              Secondary転写がある経路では矛盾(protected fail・E2/正準不一致のTRUE_CONTENT_MISMATCH・TTS_FAILURE)で不受理(OF-183同様)/
#              最終ANDゲート(値・否定)を元転写と置換後転写の両方に適用
#   OF-OOV-02  受理条件固定: Ledger confidence medium以上(low除外)/C2候補のみ・ASR語はCMU代表発音(rank0)のみ・1:1置換のみ/
#              対象role=Tier3と同じ FIVE_ROLES_APPLICABLE(KP・見出し・JA・未分類は対象外)/一致音素列は3音素以上
# 委任_03版からの変更(Opus条件Cレビュー OF-OOV-07/08):
#   OF-OOV-07  E2W(judge_e2w)を fail-closed 化: 独立エンジン(ローカルfaster-whisper)の転写が None/空 -> 不受理、
#              『矛盾しない』では受理せず『揃えた正準語の位置でWhisperが 正準語を書いた / 同じLedger読みと一致するCMU語を書いた』の正の一致のみ受理
#   OF-OOV-08  Whisperとの一致は文全体のclassify_asr_matchではなく『揃えた正準語の位置の1語範囲』だけで判定(隣接語が両側とも一致している範囲に
#              Whisper側がちょうど1語だけ入る場合のみ。隣が崩れて範囲が確定しなければ不受理=fail-closed)
#   judge_direct はE2単独(独立確認なし)のまま残す。採用候補ではなく、比較用/Azure転写の矛盾判定(OF-183)用。採用候補は judge_e2w のみ。
# 既存 er006_m1_multi_candidate_01 の凍結候補(freeze_candidates)・IPA変換・default_cmuは無変更で再利用。新規辞書・G2P・閾値は無い。
import difflib, sys
sys.path.insert(0, ".")
import er006_preprod_hardening_01_validation as val
import er006_m1_multi_candidate_01 as m1
import er011_b1_connected_speech_validator_01 as csv3

E2_REASON = "E2_LEDGER_PHONEME_ACCEPT"
MIN_CONF = ("medium", "high")
MIN_PHONEMES = 3
CONTRADICTION_CLASSES = ("TRUE_CONTENT_MISMATCH", "TTS_FAILURE")


def _role_ok(segment_id):
    import er020_tts_retry_local_rewrite_01 as rg
    import er021_en_asr_semantic_equivalence_production_01 as se
    return rg.resolve_narrative_role(segment_id) in se.FIVE_ROLES_APPLICABLE


def _align_positions(canonical, asr, c, a):
    ct, at = m1._tokens(canonical), m1._tokens(asr)
    sm = difflib.SequenceMatcher(a=ct, b=at, autojunk=False)
    return [j1 for tag, i1, i2, j1, j2 in sm.get_opcodes()
            if tag == "replace" and ct[i1:i2] == [c] and at[j1:j2] == [a]]


def _align_pairs(canonical, asr, c, a):
    ct, at = m1._tokens(canonical), m1._tokens(asr)
    sm = difflib.SequenceMatcher(a=ct, b=at, autojunk=False)
    return [(i1, j1) for tag, i1, i2, j1, j2 in sm.get_opcodes()
            if tag == "replace" and ct[i1:i2] == [c] and at[j1:j2] == [a]]


def whisper_position_check(canonical, whisper_text, canon_word, canon_index, ledger_pron, *, min_phonemes=MIN_PHONEMES):
    """OF-OOV-08: 揃えた正準語の位置(canonical token index)だけを見て、独立エンジン(Whisper)の転写との『正の一致』を判定。
    戻り値 (agree: bool, state: str, whisper_word)。fail-closed: 位置が確定しない・転写が無い・不一致は全て agree=False。"""
    if whisper_text is None or not str(whisper_text).strip():
        return False, "WHISPER_UNAVAILABLE", None
    ct, wt = m1._tokens(canonical), m1._tokens(whisper_text)
    if not wt or not (0 <= canon_index < len(ct)) or ct[canon_index] != canon_word:
        return False, "WHISPER_EMPTY_OR_INDEX_ERROR", None
    sm = difflib.SequenceMatcher(a=ct, b=wt, autojunk=False)
    eq = {}
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                eq[i1 + k] = j1 + k
    if canon_index in eq:
        return True, "AGREE_CANONICAL_SPELLING", wt[eq[canon_index]]
    i = canon_index
    if i == 0:
        lo = 0
    elif (i - 1) in eq:
        lo = eq[i - 1] + 1
    else:
        return False, "WHISPER_LEFT_NEIGHBOR_UNALIGNED", None
    if i == len(ct) - 1:
        hi = len(wt)
    elif (i + 1) in eq:
        hi = eq[i + 1]
    else:
        return False, "WHISPER_RIGHT_NEIGHBOR_UNALIGNED", None
    seg = wt[lo:hi]
    if len(seg) != 1:
        return False, "WHISPER_RANGE_NOT_1WORD:%d" % len(seg), None
    w = seg[0]
    avs = [tuple(v) for v in m1.default_cmu(w)]
    if avs and avs[0] == tuple(ledger_pron) and len(avs[0]) >= min_phonemes:
        return True, "AGREE_LEDGER_CMU_PRON", w
    return False, "WHISPER_NO_POSITIVE_AGREEMENT", w


def _core(canonical, asr, frozen, *, segment_id, min_conf, min_phonemes, role_gate, ledger):
    base = val.classify_asr_match(canonical, asr, segment_id=segment_id)
    r = {"base": base.classification, "accepted": False, "reason": None, "sub": None}
    if base.should_pass:
        r["reason"] = "BASE_PASS"; return r
    if role_gate and not _role_ok(segment_id):
        r["reason"] = "ROLE_NOT_ELIGIBLE"; return r
    if base.classification not in ("TRUE_CONTENT_MISMATCH", "ASR_VALIDATION_UNCERTAIN"):
        r["reason"] = "NOT_ELIGIBLE:" + base.classification; return r
    if not base.protected.passed:
        r["reason"] = "PROTECTED_FAIL_ORIGINAL"; return r  # 最終ANDゲート(値・否定): 元転写
    diffs = base.protected.content_word_diffs
    if len(diffs) != 1 or diffs[0].get("type") != "replace":
        r["reason"] = "NOT_SINGLE_REPLACE"; return r
    d = diffs[0]
    cw, aw = m1._tokens(d["canonical"]), m1._tokens(d["asr"])
    if len(cw) != 1 or len(aw) != 1:
        r["reason"] = "NOT_1TO1"; return r
    c, a = cw[0], aw[0]
    fw = frozen.word(c)
    if fw is None or any(x.source.startswith("C1_") for x in fw.candidates):
        r["reason"] = "CANONICAL_IN_CMU_OR_ABSENT"; return r
    allc2 = [x for x in fw.candidates if x.source.startswith("C2_")]
    if not allc2:
        r["reason"] = "NO_C2_CANDIDATE"; return r
    cands = [x for x in allc2 if x.confidence in min_conf]
    if not cands:
        r["reason"] = "CONFIDENCE_TOO_LOW"; return r
    avs = [tuple(v) for v in m1.default_cmu(a)]
    if not avs:
        r["reason"] = "ASR_WORD_NOT_IN_CMU"; return r
    hit = [x for x in cands if avs[0] == tuple(x.pron)]
    if not hit:
        r["reason"] = "NO_PHONEME_MATCH"; return r
    if len(avs[0]) < min_phonemes:
        r["reason"] = "PHONEME_RUN_TOO_SHORT"; return r
    pos = _align_positions(canonical, asr, c, a)
    if len(pos) != 1:
        r["reason"] = "ALIGN_NOT_UNIQUE:%d" % len(pos); return r
    asr2 = m1._replace_tokens(asr, {pos[0]: c})  # 揃えた位置の1か所のみ
    post = val.classify_asr_match(canonical, asr2, segment_id=segment_id)
    if not post.should_pass:
        r["reason"] = "POST_CHECK_FAIL:" + post.classification; return r
    if not post.protected.passed:
        r["reason"] = "PROTECTED_FAIL_REPLACED"; return r  # 最終ANDゲート: 置換後転写
    cs2 = csv3.classify_connected_speech(canonical, asr2)
    if cs2.get("f1_residual"):
        r["reason"] = "POST_REPLACEMENT_F1_RESIDUAL"; return r
    le = (ledger or {}).get(hit[0].ledger_key) or {}
    r.update(accepted=True, reason=E2_REASON, normalized_asr=asr2,
             sub={"canonical": c, "asr": a, "pron": list(avs[0]), "source": hit[0].source, "confidence": hit[0].confidence,
                  "ledger_key": hit[0].ledger_key, "updated_at": hit[0].updated_at, "ipa_raw": hit[0].ipa_raw,
                  "evidence_tier": le.get("evidence_tier"), "entity_type": le.get("entity_type"),
                  "candidate_set_hash": frozen.candidate_set_hash, "post": post.classification,
                  "base_classification": base.classification, "asr_index": pos[0], "canon_index": _align_pairs(canonical, asr, c, a)[0][0]})
    return r


def judge_direct(canonical, asr, frozen, *, segment_id=None, secondary_asr_text=None, min_conf=MIN_CONF,
                 min_phonemes=MIN_PHONEMES, role_gate=True, ledger=None):
    """E2判定。secondary_asr_text を渡す経路(forced-secondary・LR v1・A2 fallback)では OF-183 同様、Secondaryが矛盾すれば不受理。
    矛盾=Secondary転写がprotected fail / TRUE_CONTENT_MISMATCH・TTS_FAILURE で『E2自身でも同じ置換で受理できない』場合。
    (Secondaryが同じ同音語を書いて同じE2で受理できる、または should_pass、は agree。それ以外のUNCERTAINは M1 同様 非矛盾。)"""
    r = _core(canonical, asr, frozen, segment_id=segment_id, min_conf=min_conf, min_phonemes=min_phonemes,
              role_gate=role_gate, ledger=ledger)
    if not r["accepted"]:
        return r
    if secondary_asr_text is None:
        r["secondary_state"] = "not_provided"; return r
    sc = val.classify_asr_match(canonical, secondary_asr_text, segment_id=segment_id)
    if sc.should_pass:
        st = "native_pass"
    else:
        r2 = _core(canonical, secondary_asr_text, frozen, segment_id=segment_id, min_conf=min_conf,
                   min_phonemes=min_phonemes, role_gate=role_gate, ledger=ledger)
        if r2["accepted"]:
            st = "e2_accept"
        elif (not sc.protected.passed) or sc.classification in CONTRADICTION_CLASSES:
            st = "contradiction:" + ("protected_fail" if not sc.protected.passed else sc.classification)
        else:
            st = "uncertain_no_agreement"
    r["secondary_state"] = st
    if st.startswith("contradiction:"):
        r.update(accepted=False, reason="SECONDARY_CONTRADICTION")
    return r


def judge_e2w(canonical, asr, frozen, *, whisper_text, secondary_asr_text=None, segment_id=None, min_conf=MIN_CONF,
              min_phonemes=MIN_PHONEMES, role_gate=True, ledger=None):
    """E2W(採用候補。fail-closed)。E2を満たし、かつローカルWhisperの転写が『揃えた位置』で正の一致をした場合のみ受理。
    whisper_text が None/空(ローカルモデル失敗)なら不受理。secondary_asr_text(既にAzure転写が手元にある経路)があれば OF-183 の矛盾判定も追加で適用(不受理方向のみ)。"""
    r = judge_direct(canonical, asr, frozen, segment_id=segment_id, secondary_asr_text=secondary_asr_text, min_conf=min_conf,
                     min_phonemes=min_phonemes, role_gate=role_gate, ledger=ledger)
    if not r["accepted"]:
        r.setdefault("whisper_state", "not_evaluated")
        return r
    sub = r["sub"]
    ok, st, ww = whisper_position_check(canonical, whisper_text, sub["canonical"], sub["canon_index"], sub["pron"], min_phonemes=min_phonemes)
    r["whisper_state"] = st; r["whisper_word"] = ww
    if not ok:
        r.update(accepted=False, reason="E2W_NO_WHISPER_AGREEMENT:" + st)
    return r
