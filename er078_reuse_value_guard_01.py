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


# JA-ASR-V2-BETA-PRODUCTION-WIRING-01 委任_02A(Opus M-4): v2読み規則+B-light β(新方式)が合否に寄与した音声の再利用規則。
# 新方式の印(`ja_v2beta`/`judge_rule_version`/`rescue_basis`/JA_NEWLAYER_*警告)が**無い**entryでは新moduleをimportしない(A/B/C・旧資産は従来どおり)。
_JA_V2B_MARK_KEYS = ("ja_v2beta", "judge_rule_version", "rescue_basis")


def _ja_v2b_marked(aj) -> bool:
    if not isinstance(aj, dict):
        return False
    if any(k in aj for k in _JA_V2B_MARK_KEYS):
        return True
    return any(str(w).startswith("JA_NEWLAYER_") for w in (aj.get("warnings") or []))


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
    # ASR-QUALITY PN 委任_04(RET、OPEN-472 / Opus W-06): Run Entity Table(RET)が受理に寄与したアラーム音声(`pronunciation_alarm.entity_table`あり)は、
    # RETが有効でない間(X/Z scope内でRET flag=Falseのrollback)、または保存entryを現行のeligible規則で復元できない間(rules_version不一致)は再利用しない
    # (再判定NGが保護理由でなければ下の再判定は止めないため、ここで先に止める)。`asr_judgement`と`asr_judgement_inherited`の**両方**を見る。
    # RET由来の受理だけが対象=既存のLedger受理entry・印のないentryには作用しない。再判定自体がNGになった場合のブロックは下の再判定後(REJUDGE_NG_ENTITY_TABLE)。
    import er103_run_entity_table_01 as _ret
    _aj_ret = [a for a in (entry.get("asr_judgement"), entry.get("asr_judgement_inherited")) if _ret.entity_contributed(a)]
    if _aj_ret and (not _ret.is_active_for_run() or not all(_ret.restorable(a) for a in _aj_ret)):
        out.update(blocked=True, applicable=True, reason="ENTITY_TABLE_ALARM_AUDIO_RET_INACTIVE_OR_UNRESTORABLE")
        return out
    # ASR-HOMOPHONE 委任_04(E-2、Opus M1): er109(表記違い同音)が合否に寄与した音声(層・印の種類ごと: orthographic_equivalence.applied / primary・secondary・vote票のlabel /
    # ORTHO_*警告)は、X/Z run scope(∧flag有効)の外では再利用しない(Master Audio StoreはA/B/Cとも共有。scope外の判定では多くの場合secondary_not_acceptedになり
    # 下の再判定が止めないため、ここで先に止める)。`asr_judgement`と`asr_judgement_inherited`の**両方**を見る。KP vote gate後続のskip(下)より前。
    # er109で生まれたentryだけが対象=既存のentry・印のないentryには作用しない。flag Falseのrollback時はX/Z内のortho entryもここで再生成へ回る(再生成費用が出る)。
    import er109_xz_scope_01 as _xz
    if (_xz.ortho_contributed(entry.get("asr_judgement")) or _xz.ortho_contributed(entry.get("asr_judgement_inherited"))) and not _xz.is_active_for_run():
        out.update(blocked=True, applicable=True, reason=_xz.OUT_OF_SCOPE_BLOCK_REASON)
        return out
    # ASR-FLAP-T-PRODUCTION-WIRING-01: Flap-T(米音の弾音化)救済が合否に寄与した音声は、X/Y/Z run scope外・親/子flag OFF・Voice表sha(またはCMU辞書sha)が
    # 保存時と異なる・当該(voice,model)が現表で未確認、のいずれかでは再利用しない(再判定NGが保護理由でなければ下の再判定は止めないため、ここで先に止める)。
    # 保存audit(sites[*].er109.flapt)が読めない場合もfail-closed(再生成)。Flap-Tを使っていないentryには作用しない。
    _ajs_flap = [a for a in (entry.get("asr_judgement"), entry.get("asr_judgement_inherited")) if _xz.flapt_contributed(a)]
    if _ajs_flap:
        import er139_flapt_equivalence_01 as _flapt_fe
        if (not _xz.is_active_for_run()) or not all(_flapt_fe.reuse_still_valid(a)[0] for a in _ajs_flap):
            out.update(blocked=True, applicable=True, reason=_flapt_fe.REUSE_BLOCK_REASON)
            return out
    # ASR-QUALITY-2ITEMS ②UKUS 委任_04(OF-UKUS-W-03): ②英米綴り層(UKUS)が合否に寄与した音声は、UKUS層が有効でない間(UKUS flagだけOFFのrollback等。親ortho/scopeは上で処理済み)は再利用しない。
    # UKUS flagだけOFFだと再判定NG(非保護差)はblockされない(下の保護差のみblock)ため、ここが唯一の防壁。asr_judgement/asr_judgement_inherited両方・全site(primary/secondary/KP票)を見る。
    # 検出は fail-closed(ortho適用・version=*_ukus*でsite auditが無い/壊れていればUKUS寄与あり)。配置はkp_vote_gate_follows早期returnより前。
    if (_xz.ukus_contributed(entry.get("asr_judgement")) or _xz.ukus_contributed(entry.get("asr_judgement_inherited"))) and not _xz.is_ukus_active_for_run():
        out.update(blocked=True, applicable=True, reason=_xz.UKUS_OUT_OF_SCOPE_BLOCK_REASON)
        return out
    # JA-ASR-V2-BETA-PRODUCTION-WIRING-01 委任_02A(Opus M-4): 日本語ASR v2+β(新方式)が合否に寄与した音声。配置はkp_vote_gate_follows早期returnより前(ortho/UKUSと同じ)。
    #  (1) X/Y/Z run scope外・flag OFFでは再利用しない(Master Audio StoreはA/B/Cとも共有。scope外の判定では新方式の受理を再現できない)→再生成。
    #  (2) scope内で判定規則の版(judge_rule_version)が現行と同じなら保存判定を信頼する(J11と同じ方針。Reading Resolver=LLMで分類が揺れて正しい資産が再生成されるのを避ける)。
    #  (3) 版が異なる/欠落する寄与recordは**API 0**(Resolverなし・Secondary新規呼出なし)で現行規則により再判定し、不成立なら再生成。判定不能(保存データ欠落)はfail-closed(再生成)。
    #  `asr_judgement`と`asr_judgement_inherited`の**両方**を見る。印のないentryには作用しない。
    _ajs_v2b = [a for a in (entry.get("asr_judgement"), entry.get("asr_judgement_inherited")) if _ja_v2b_marked(a)]
    if _ajs_v2b:
        import er078_ja_v2beta_01 as _v2b
        _contrib = [a for a in _ajs_v2b if _v2b.contributed(a)]
        if _contrib:
            if not _v2b.is_active_for_run():
                out.update(blocked=True, applicable=True, reason=_v2b.OUT_OF_SCOPE_BLOCK_REASON)
                return out
            for _a in _contrib:
                if _a.get("judge_rule_version") != _v2b.JUDGE_RULE_VERSION:
                    _ok, _why = _v2b.rejudge_contributed(_a)
                    if not _ok:
                        out.update(blocked=True, applicable=True, reason=f"JA_V2BETA_REJUDGE_NG:{_why}")
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
    if _aj_ret:   # RET由来の受理音声は、現行境界での再判定がNGなら(保護理由でなくても)再利用しない=境界を厳しくした後に古い受理を黙って通さない(W-06)
        out.update(blocked=True, reason=f"REJUDGE_NG_ENTITY_TABLE:{rj.get('reason')}")
        return out
    out["reason"] = f"REJUDGE_NG_NOT_PROTECTED:{rj.get('reason')}"
    return out
