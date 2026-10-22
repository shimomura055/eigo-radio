# -*- coding: utf-8 -*-
"""FAMILY-XZ-M2P0-N01-PRODUCTION-COMPLETION-01 是正②: 再利用segmentの「検証済み状態」の証拠つき引継ぎ(API呼出なし)。

背景(OPEN-346②): `--only-segments`のtts実行が非選択segmentのresults entryを`SKIPPED_NOT_SELECTED`で上書きする、
また他runから音声wavだけをseed(copy)したsegmentにはAdv側のresults entry自体が無い、の2点により、元の正式Validation
(ASR検証OK)が済んだsegmentでもAudio Validation Gateが`UNVALIDATED`としてassemblyをBLOCKしていた。

方針(Gateは無変更・緩和しない): 次の証拠がすべて揃うsegmentに限り、元の検証済みentryを(status=OK、元のASR/QA証拠を保持
したまま)引き継ぎ、`validation_inheritance`(label=REUSED_VALIDATED、元記録へのポインタ・sha256)を付与する。
  1. 元entryが status=="OK" かつ asr_verified is True (元の正式Validation結果)
  2. 現在のwavが存在し、wavのsha256が同一性の証拠と一致する:
       (a) 元entryが`sha256`を持つ場合: 現在のwav sha256 == entry.sha256
       (b) 持たない場合: 呼び出し側が渡すwitness(seed provenanceに記録されたcopy時sha256 かつ 元runに残る元wavの
           現在sha256)の両方が現在のwav sha256と一致 + (OF-X7)entry.trim_info.trimmed_duration_secondsが
           現在wav長と±20ms以内で一致
     どちらも無ければ引継ぎしない(NO_IDENTITY_EVIDENCE、fail-closed)。
  3. expected_textが渡された場合、元entryのcanonical_text(または原文text)が完全一致(古い文面の音声を引き継がない)。
証拠が揃わないsegmentは従来どおりUNVALIDATEDのまま(Gate BLOCK維持)。
引き継いだentryには現在のwav sha256を`sha256`として記録するため、Gateの`ASSET_HASH_MISMATCH`(stale検知)も有効になる。

委任_02(Opusレビュー反映、2026-10-13)の追加:
  - OF-X4: CLI `--apply`はexpected_text必須(`--expected-texts-auto`でparts.json/support_texts/titleから自動導出)。
  - OF-X5: 元runのstyle_versionが現行と異なる場合は`cross_version_accepted_by`(Fable判断記録ポインタ)を必須とし、
    `validation_inheritance.source_style_version`/`cross_version_accepted_by`を記録する(無ければ引継ぎしない)。
    runner自動引継ぎでも元の記録を保持する。
  - OF-X6: 元entryの保存済み`asr_text`を現行(F1後)判定関数で再判定(offline)し、NGは引継ぎ不可。f1_versionを記録。
  - OF-X11: `--only-segments`非選択labelは、sha一致時に状態を問わず前回entryを持ち越す(statusはGateが判定。緩和ではない)。
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import shutil
import time
import wave
from typing import Optional

REUSED_VALIDATED = "REUSED_VALIDATED"
DURATION_WITNESS_TOLERANCE_SECONDS = 0.020
_OVERWRITABLE_STATUSES = (None, "SKIPPED_NOT_SELECTED", "INVALIDATED_FOR_REGENERATION",
                          "TECHNICAL_STOP_SECONDARY_UNAVAILABLE",  # 委任_06c: Secondary障害の技術STOP(再実行で再生成)
                          "TECHNICAL_STOP_WHISPER_UNAVAILABLE")    # KP3V(P-08): Whisper(ローカルASR)障害の技術STOP(再実行で再生成)


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def entry_fingerprint(entry: dict) -> str:
    return hashlib.sha256(json.dumps(entry, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")).hexdigest()


def wav_duration_seconds(path: str) -> Optional[float]:
    try:
        with wave.open(path, "rb") as w:
            return w.getnframes() / float(w.getframerate())
    except Exception:
        return None


def _duration_witness(entry: dict, wav_path: str) -> dict:
    """OF-X7: entry.trim_info.trimmed_duration_secondsと現在wav長が±20ms以内で一致するか。"""
    recorded = (entry.get("trim_info") or {}).get("trimmed_duration_seconds")
    actual = wav_duration_seconds(wav_path)
    if recorded is None or actual is None:
        return {"ok": False, "recorded": recorded, "actual": actual}
    return {"ok": abs(float(recorded) - actual) <= DURATION_WITNESS_TOLERANCE_SECONDS,
            "recorded": recorded, "actual": round(actual, 4)}


def _text_matches(entry: dict, expected_text: str) -> bool:
    # 旧runner版のentryはcanonical_textにTTS入力(数字語化済み)、textに原文を持つ。どちらかが一致すればよい。
    return expected_text in (entry.get("canonical_text"), entry.get("text"))


def evaluate_inheritance(entry: Optional[dict], wav_path: str, expected_text: Optional[str] = None,
                         witness_sha256s: Optional[list] = None, require_duration_witness: bool = False) -> dict:
    """戻り値: {ok, reason, current_sha256, evidence}。reasonは不許可理由(ok時は"OK")。"""
    if not isinstance(entry, dict):
        return {"ok": False, "reason": "NO_SOURCE_ENTRY", "current_sha256": None, "evidence": None}
    if entry.get("status") != "OK":
        return {"ok": False, "reason": f"SOURCE_STATUS_NOT_OK({entry.get('status')})", "current_sha256": None, "evidence": None}
    if entry.get("asr_verified") is not True:
        return {"ok": False, "reason": "SOURCE_ASR_NOT_VERIFIED", "current_sha256": None, "evidence": None}
    if not wav_path or not os.path.exists(wav_path):
        return {"ok": False, "reason": "WAV_MISSING", "current_sha256": None, "evidence": None}
    current = sha256_file(wav_path)
    if expected_text is not None and not _text_matches(entry, expected_text):
        return {"ok": False, "reason": "CANONICAL_TEXT_MISMATCH", "current_sha256": current, "evidence": None}
    recorded = entry.get("sha256")
    if recorded:
        if recorded != current:
            return {"ok": False, "reason": "ENTRY_SHA256_MISMATCH", "current_sha256": current, "evidence": None}
        return {"ok": True, "reason": "OK", "current_sha256": current, "evidence": "entry_sha256"}
    if witness_sha256s:
        if all(w == current for w in witness_sha256s):
            if require_duration_witness:
                dw = _duration_witness(entry, wav_path)
                if not dw["ok"]:
                    return {"ok": False, "reason": "DURATION_WITNESS_MISMATCH", "current_sha256": current,
                            "evidence": None, "duration_witness": dw}
                return {"ok": True, "reason": "OK", "current_sha256": current,
                        "evidence": "witness_sha256_and_trimmed_duration", "duration_witness": dw}
            return {"ok": True, "reason": "OK", "current_sha256": current,
                    "evidence": "seed_provenance_and_source_wav_sha256"}
        return {"ok": False, "reason": "WITNESS_SHA256_MISMATCH", "current_sha256": current, "evidence": None}
    return {"ok": False, "reason": "NO_IDENTITY_EVIDENCE", "current_sha256": current, "evidence": None}


def build_inherited_entry(entry: dict, wav_path: str, evaluation: dict, source_ref: dict,
                          source_style_version: Optional[str] = None, cross_version_accepted_by: Optional[str] = None,
                          f1_rejudge: Optional[dict] = None, expected_text: Optional[str] = None) -> dict:
    """元entryを深いcopyし、status=OKと元の検証証拠を保ったまま、現在wavのpath/sha256と引継ぎ記録を付ける。
    style_profile等の元の記録は書き換えない(呼び出し側で現行profileを上書き付与しない)。
    元entryが既に`validation_inheritance`を持つ(CLIで引継ぎ済みの次回runner自動引継ぎ)場合は、元の記録
    (source_style_version / cross_version_accepted_by / f1_rejudge / source_ref)を失わず保持し、持ち越し履歴だけ足す。"""
    new_entry = copy.deepcopy(entry)
    new_entry["path"] = wav_path
    new_entry["sha256"] = evaluation["current_sha256"]
    new_entry["reused_from_previous_run"] = True
    # AUW 委任_04(J11、additive): 継承再判定の統一judge record。元の`asr_judgement`は`asr_judgement_inherited`へ移し、
    # 事後試聴リストが元のWARNINGを継承して表示できるようにする(OF-AUW-15)。f1_rejudgeにはrecord本体を二重に入れない。
    if f1_rejudge is not None and f1_rejudge.get("asr_judgement_inherited") is not None:
        new_entry.pop("asr_judgement", None)
        new_entry["asr_judgement_inherited"] = f1_rejudge["asr_judgement_inherited"]
        f1_rejudge = {k: v for k, v in f1_rejudge.items() if k != "asr_judgement_inherited"}
    elif "asr_judgement" in new_entry:
        new_entry["asr_judgement_inherited"] = new_entry.pop("asr_judgement")
    prior = entry.get("validation_inheritance")
    if isinstance(prior, dict) and prior.get("label") == REUSED_VALIDATED:
        vi = copy.deepcopy(prior)
        vi["wav_sha256"] = evaluation["current_sha256"]
        vi["carried_over_count"] = int(vi.get("carried_over_count", 0)) + 1
        vi["last_carried_over_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        new_entry["validation_inheritance"] = vi
        return new_entry
    vi = {
        "label": REUSED_VALIDATED,
        "evidence": evaluation["evidence"],
        "wav_sha256": evaluation["current_sha256"],
        "source_entry_fingerprint_sha256": entry_fingerprint(entry),
        "source_ref": source_ref,
        "source_style_version": source_style_version,
        "inherited_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    if evaluation.get("duration_witness") is not None:
        vi["duration_witness"] = evaluation["duration_witness"]
    if cross_version_accepted_by:
        vi["cross_version_accepted_by"] = cross_version_accepted_by
    if f1_rejudge is not None:
        vi["f1_rejudge"] = f1_rejudge
    new_entry["validation_inheritance"] = vi
    if expected_text is not None:
        new_entry["canonical_text"] = expected_text
    return new_entry


def carry_over_unchanged(cached_entry: Optional[dict], wav_path: str, expected_text: Optional[str],
                         cached_style_version: Optional[str], current_style_version: str) -> Optional[dict]:
    """OF-X11: `--only-segments`の非選択labelで、前回entryがsha256を持ち現在wavとsha一致(かつtext一致、
    style_version一致)のとき、statusを問わず(STOPPED+HUMAN_APPROVEDの前提entry等を含む)そのまま持ち越す。
    status判定はGate/review_lockに任せる(検証済み扱いにはしない: validation_inheritanceは付けない)。"""
    if cached_style_version != current_style_version or not isinstance(cached_entry, dict):
        return None
    if cached_entry.get("status") in _OVERWRITABLE_STATUSES:
        return None
    recorded = cached_entry.get("sha256")
    if not recorded or not wav_path or not os.path.exists(wav_path) or sha256_file(wav_path) != recorded:
        return None
    if expected_text is not None and not _text_matches(cached_entry, expected_text):
        return None
    out = copy.deepcopy(cached_entry)
    out["carried_over_unchanged"] = True
    return out


def is_untouched_entry(entry: dict) -> bool:
    """runnerが現行style_profile等を再付与してはいけないentry(未選択skip / 引継ぎ / 持ち越し)か。"""
    return bool(entry.get("status") == "SKIPPED_NOT_SELECTED" or entry.get("validation_inheritance")
                or entry.get("carried_over_unchanged"))


def try_inherit_from_cached(cached_entry: Optional[dict], wav_path: str, expected_text: Optional[str],
                            cached_style_version: Optional[str], current_style_version: str,
                            source_ref: dict, *, kp_vote_required: bool = False,
                            kp_vote_canonical: Optional[str] = None) -> Optional[dict]:
    """runner(`--only-segments`で非選択のsegment)用: 同一out_dirの前回results entryを、上記証拠が揃う場合に限り
    引き継ぐ。style_version不一致の旧cacheは通常のreuseと同様に引き継がない。引き継げなければNone。
    OF-X11: OK+asr_verifiedの検証済みentryは`REUSED_VALIDATED`として、それ以外のstatus(STOPPED等)はsha一致時に
    そのまま持ち越す(statusはGateが判定)。"""
    if cached_style_version != current_style_version:
        return None
    ev = evaluate_inheritance(cached_entry, wav_path, expected_text=expected_text)
    if ev["ok"] and ev["evidence"] == "entry_sha256":
        # AUW 委任_06c(OF-AUW-C-03): 引継ぎ前に保存転写のみ(API 0)を現行の統一judgeへ通す。値ガードDIFF/否定差(`reuse_blocked` mark含む)
        # なら引継ぎず(None)、呼出側は再生成/SKIPPED(=Gate BLOCK維持)へ回す。carry_over_unchanged(検証済み扱いにしない持越し)は対象外。
        import er078_reuse_value_guard_01 as _rvg
        if _rvg.guard_entry(cached_entry, label=str((source_ref or {}).get("label") or "")).get("blocked"):
            return None
        if kp_vote_required:
            # KP3V(OF-KPD-P-03、再利用点2): KP英語phraseの引継ぎ(--only-segments非選択)は、両Provider PASSの保存証跡を現行分類器で
            # API 0再判定して成立する場合に限る(Azureは呼ばない=allow_s1=False)。証跡が無い/不成立/判定不能は引き継がない(None=SKIPPED)。
            import er104_kp_vote_reuse_01 as _kd
            if not kp_vote_canonical:
                return None
            _d = _kd.kp_vote_reuse_ok(cached_entry, wav_path=wav_path, canonical_text=kp_vote_canonical, allow_s1=False,
                                      label=str((source_ref or {}).get("label") or ""))
            if not _d["ok"]:
                return None
        return build_inherited_entry(cached_entry, wav_path, ev, source_ref, source_style_version=cached_style_version)
    return carry_over_unchanged(cached_entry, wav_path, expected_text, cached_style_version, current_style_version)


# ------------------------------------------------------------
# OF-X6: F1後の判定関数による再判定(offline、API呼出なし)
# ------------------------------------------------------------
def is_japanese_label(level: str, label: str) -> bool:
    if level == "a2":
        return (label == "japanese_title" or label == "preview" or label.startswith("comment_")
                or label.endswith("_japanese_meaning"))
    return False


def _j11_adopted_judgement(entry: dict):
    """元entryが統一judgeのrecord(`asr_judgement`/`asr_judgement_inherited`)を持つ場合、(record, 採用転写text)を返す。
    Primary PASSならPrimary転写、Secondary確認で採用ならSecondary転写(=実際に最終ANDゲートで確認すべき転写)。"""
    aj = entry.get("asr_judgement") or entry.get("asr_judgement_inherited")
    if not isinstance(aj, dict):
        return None, None
    if aj.get("state") == "PASS_WITH_PRONUNCIATION_ALARM":
        # PNAP 委任_02(OF-PNAP-P-05(i)): アラーム受理音声のPrimary自身はNG(固有名詞の発音不一致)。採用転写=Primary転写
        # (Secondary転写は固有名詞不一致を含む別judge対象)。最終ANDゲートはPrimary転写へ適用する。
        return aj, (aj.get("primary") or {}).get("text")
    if aj.get("state") not in ("PASS", "PASS_WITH_WARNING"):
        return aj, None
    prim, sec = aj.get("primary") or {}, aj.get("secondary") or {}
    if prim.get("passed"):
        return aj, prim.get("text")
    return aj, sec.get("text")


def _norm(x) -> str:
    return " ".join(str(x or "").lower().split())


def rejudge_with_current_judge(entry: dict, level: str, label: str, force_lang: Optional[str] = None) -> dict:
    """J11(AUW 委任_04、DESIGN_02_ADDENDUM_01 §3-1): 既存音声の継承時に、保存済み転写を**統一judgeの入口
    (er078_asr_unified_judge_01.unified_judge)**でAPI 0のまま再判定する(旧: 英語のclassify_asr_matchのみ・日本語は対象外)。
    - Secondary(Azure)は**新規に呼ばない**(secondary_fnは元entryに保存済みのSecondary転写を返すだけ。無ければ取得不能=NG)。
    - EN: 保存済み`asr_text`を現行(F1後)の`classify_asr_match`でPrimary再判定(従来どおり。NGでも保存済みSecondary転写が
      許容集合PASSならPASS_WITH_WARNING)し、最終ANDゲート(値ガードDIFF/否定差)を適用する。
    - JA(a2のjapanese_title/preview/comment/KP日本語意味): 日本語Primaryを再導出せず(Resolver=LLM呼出を避けAPI 0を守る)、
      元の正式Validation結果(status=OK/asr_verified、inheritanceの前提)を維持したまま、**最終ANDゲートだけ**を採用転写に再適用する
      (値ガードDIFF/否定差なら引継ぎ不可=fail-closed)。
    - 元entryが`asr_judgement`(PASS_WITH_WARNING等)を持つ場合は`asr_judgement_inherited`として継承する(元のWARNINGを失わない、OF-AUW-15)。
    戻り値: {applicable, ok, reason, unified_state, secondary_new_calls(=0), asr_judgement_inherited, ...(EN: classification/f1_version/tts_input)}。"""
    import er078_asr_unified_judge_01 as uj
    # 委任_06c(additive): force_lang("ja"|"en")を渡す呼出元(再利用経路の値ガード等、levelを持たない)は言語を明示できる。
    ja = (force_lang == "ja") if force_lang in ("ja", "en") else is_japanese_label(level, label)
    asr_text = entry.get("asr_text")
    base_text = entry.get("text") or entry.get("canonical_text")
    if base_text:
        # FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01 委任_02(不具合③、OPEN-283修正): Local Rewrite(LR)採用済みentryの保存転写は
        # 書換え後の文で生成された音声の転写。再利用/継承の再判定も、書換え前の原稿ではなく書換え後の実送信文と照合する
        # (単一参照点=er020.resolve_expected_text_after_local_rewrite。LR記録の無いentryは従来どおり)。
        import er020_tts_retry_local_rewrite_01 as _lr
        base_text, _ = _lr.resolve_expected_text_after_local_rewrite(entry, base_text)
    aj, adopted = _j11_adopted_judgement(entry)
    if not asr_text or not base_text:
        return {"applicable": True, "ok": False, "reason": "NO_ASR_TEXT_OR_TEXT", "secondary_new_calls": 0}
    out: dict = {"applicable": True, "secondary_new_calls": 0}
    stored_secondary = ((aj or {}).get("secondary") or {}).get("text") or ((entry.get("scg_info") or {}).get("secondary_transcript"))
    calls = {"n": 0}

    def _no_new_secondary(_ctx):
        """新規Secondary呼出は行わない(J11)。保存済みSecondary転写があればそれを返す。無ければ取得不能(PASS不可)。"""
        calls["n"] += 1
        if stored_secondary:
            return uj.SecondaryOutcome(stored_secondary)
        return uj.SecondaryOutcome(None, error="j11_no_new_secondary_call")

    lang = "ja" if ja else "en"
    if ja:
        primary = uj.PrimaryResult(passed=True, text=adopted or asr_text, label=str(entry.get("audio_classification") or "ORIGINAL_VERIFIED_STATUS_OK"),
                                   equivalence_basis=None)
        accept_fn = None
        tts_input = base_text
    else:
        import er003_v1_n3_01_tts_generate as n3_tts
        import er006_preprod_hardening_01_validation as en_validator
        import er006_secondary_asr_01 as en_adapter
        import er011_b1_connected_speech_validator_01 as cs
        if label.startswith("full_story") or label == "in_one_line":
            tts_input = n3_tts.tts_safe_news_en(base_text)
        else:
            tts_input = n3_tts.tts_safe_number_words_en(n3_tts.tts_safe_en(base_text))
        res = en_validator.classify_asr_match(tts_input, asr_text)
        cs_info = getattr(res, "connected_speech_info", None) or {}
        out.update(classification=res.classification,
                   f1_version=cs_info.get("f1_version") or cs.F1_VERSION, judge_module_f1_version=cs.F1_VERSION, tts_input=tts_input)
        primary = uj.PrimaryResult(passed=bool(res.should_pass), text=asr_text, label=res.classification,
                                   equivalence_basis=en_adapter._equivalence_basis_of(res) if res.should_pass else None)
        # 委任_06c(OF-AUW-C-01): 元がKP非ラテン救済(adapter.layersにnon_latin)でAzure転写(保存済みSecondary)が採用根拠のとき、
        # Primary(非ラテン)転写ではなく採用転写を根拠としてPrimary相当にする(Primary非ラテン転写に英語否定語・数値を照合しない)。
        _layers = ((aj or {}).get("adapter") or {}).get("layers") or []
        if (not res.should_pass and "non_latin" in _layers and stored_secondary
                and (aj or {}).get("state") in ("PASS", "PASS_WITH_WARNING")):
            res_nl = en_validator.classify_asr_match(tts_input, stored_secondary)
            if res_nl.should_pass:
                primary = uj.PrimaryResult(passed=True, text=asr_text, label=res_nl.classification,
                                           equivalence_basis=en_adapter._equivalence_basis_of(res_nl),
                                           warning_labels=(uj.W_SECONDARY_CONFIRMED,), adopted_text=stored_secondary)

        def accept_fn(canon, stext):
            r2 = en_validator.classify_asr_match(canon, stext)
            return bool(r2.should_pass), r2.classification
    sha = entry.get("sha256") or ""
    ctx = uj.AttemptCtx(canonical_text=tts_input, wav_sha256=sha or f"j11:{label}", segment_key=label, engine="azure",
                        length_ok=True, script_version=(aj or {}).get("script_version", "v0"))
    jr = uj.unified_judge(ctx, primary, _no_new_secondary, lang=lang, role=None, secondary_accept_fn=accept_fn)
    # PNAP 委任_02(OF-PNAP-P-05(i)/(iii)): 元がアラーム受理(state=PASS_WITH_PRONUNCIATION_ALARM)の英語音声は、保存転写でNG_BOTHに戻る。
    # 現行定数・現行Ledgerで`evaluate_alarm_eligibility`を**再評価**し(API 0)、受理できる場合のみ継承する(境界を厳しくした後に古い受理を
    # 黙って通さない/承認範囲外[scope未設定・flag OFF]では継承しない=再判定NG)。供給後のTTS入力textは保存blockから使う(元綴りと不一致を避ける)。
    if (not ja) and isinstance(aj, dict) and aj.get("state") == "PASS_WITH_PRONUNCIATION_ALARM" and not jr.verified:
        import er103_proper_noun_alarm_policy_01 as pnap
        ab = aj.get("pronunciation_alarm") or {}
        if pnap.is_active_for_run() and jr.state == "NG_BOTH" and jr.reason_code == pnap.JUDGE_REASON_ELIGIBLE and stored_secondary:
            canon = tts_input
            lookup = {"supply_map": {}, "decisions": []}
            if ab.get("tts_input_text") and ab.get("pre_supply_text") == tts_input:
                canon = ab["tts_input_text"]
                lookup = {"supply_map": ab.get("supply_map") or {}, "decisions": ab.get("supply_decisions") or [],
                          "pre_supply_text": ab.get("pre_supply_text")}
            import er020_tts_retry_local_rewrite_01 as _rg
            cls_p = en_validator.classify_asr_match(canon, asr_text)
            cls_s = en_validator.classify_asr_match(canon, stored_secondary)
            dec = pnap.evaluate_for_adapter(
                canonical_text=canon, primary_cls=cls_p, secondary_cls=cls_s, primary_text=asr_text, secondary_text=stored_secondary,
                judge_state=jr.state, judge_reason_code=jr.reason_code, p3_entry=jr.audit_record.get("p3_entry"),
                role=_rg.resolve_narrative_role(label), lang="en", vote_required=False, lookup=lookup)
            out["alarm_rejudge"] = {"accepted": dec.accept, "reason": dec.reason}
            if dec.accept:
                rec = copy.deepcopy(aj)
                old = rec.get("pronunciation_alarm_records") or []
                smap = lookup.get("supply_map") or {}
                new_recs = []
                for d in dec.diffs:
                    noun = " ".join(smap.get(t, t) for t in d.canonical.split())
                    base = next((r for r in old if _norm(r.get("proper_noun")) == _norm(noun)), {})
                    new_recs += pnap.build_alarm_records(
                        pnap.AlarmDecision(True, dec.reason, diffs=[d], detail=dec.detail), canonical_text=canon,
                        segment_id=label, wav_path=str(entry.get("path") or entry.get("wav_path") or ""), wav_sha256=sha,
                        family=base.get("family") or pnap.current_scope() or "", article_id=base.get("article_id") or "", level=level,
                        role=base.get("role") or "", primary_text=asr_text, secondary_text=stored_secondary,
                        supply_info=base.get("tts_supply_result"),
                        ledger_info=({**(base.get("pronunciation_basis") or {}), "expected_pronunciation_ipa": (base.get("pronunciation_basis") or {}).get("ipa")} if base else None),
                        slot=base.get("slot"), models=base.get("models"), supply_map=smap)
                rec["pronunciation_alarm_records"] = new_recs
                rec["inherited"] = {"via": "J11_rejudge_with_current_judge", "api_calls": 0, "secondary_new_calls": 0,
                                    "rejudged_state": pnap.STATE_ALARM, "rejudged_reason_code": "pronunciation_alarm_reevaluated", "lang": lang,
                                    "had_original_asr_judgement": True, "stored_secondary_used": True,
                                    "rejudged_at": time.strftime("%Y-%m-%dT%H:%M:%S")}
                out.update(ok=True, unified_state=pnap.STATE_ALARM, unified_reason_code="pronunciation_alarm_reevaluated",
                           reason="OK", asr_judgement_inherited=rec)
                return out
    rec = copy.deepcopy(aj) if isinstance(aj, dict) else jr.audit_record
    if isinstance(aj, dict):
        # 元のWARNING(元のSecondary確認等)を失わない: 再導出したWARNINGを合成し、最終ANDゲートの結果でstateを更新する。
        rec["warnings"] = list(dict.fromkeys(list(aj.get("warnings") or []) + list(jr.warning_labels)))
        rec["state"] = jr.state if not jr.verified else (aj.get("state") if aj.get("state") in ("PASS", "PASS_WITH_WARNING") else jr.state)
        if jr.verified and rec["warnings"] and rec["state"] == "PASS":
            rec["state"] = "PASS_WITH_WARNING"
    rec["inherited"] = {"via": "J11_rejudge_with_current_judge", "api_calls": 0, "secondary_new_calls": 0,
                        "rejudged_state": jr.state, "rejudged_reason_code": jr.reason_code, "lang": lang,
                        "had_original_asr_judgement": isinstance(aj, dict), "stored_secondary_used": bool(stored_secondary and calls["n"]),
                        "rejudged_at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    out.update(ok=bool(jr.verified), unified_state=jr.state, unified_reason_code=jr.reason_code,
               reason="OK" if jr.verified else f"REJUDGE_NG({out.get('classification') or jr.state}:{jr.reason_code})",
               asr_judgement_inherited=rec)
    return out


# ------------------------------------------------------------
# 別run由来のseed segment(音声wavだけをcopyし、results entryが無い)用の再構築(明示CLI、既定dry-run)
# ------------------------------------------------------------
def rebuild_state(level_dir: str, source_results_path: str, source_root: str, provenance_path: Optional[str],
                  labels: list, expected_texts: Optional[dict] = None, *, level: str = "b1b",
                  rejudge_f1: bool = False, cross_version_accepted_by: Optional[str] = None,
                  current_style_version: Optional[str] = None, seed_wav: bool = False,
                  require_duration_witness: bool = True) -> dict:
    """level_dir=<theme>/<level>(例 .../b1b)。source_results_path=元runのaudit/tts_generation_results.json。
    source_root=元runの相対pathを解決するroot。provenance_path=seed provenance(roles[label].sha256=copy時sha256、
    無い/`roles`キー無しでも可: entry自身のsha256経路で通る)。
    seed_wav=True: 元runのwavをlevel_dir/narration/{label}.wavへ置く(適用時)前提で、元wavを候補として評価する
    (現在wavが無い/元wavと異なる場合のみ。既存wavはapply時に`_replaced_02/`へ退避してから置換する)。
    現在のresults(level_dir/audit/tts_generation_results.json)は変更しない。戻り値=判定結果(merged_segments案を含む)。"""
    cur_path = f"{level_dir}/audit/tts_generation_results.json"
    cur = json.load(open(cur_path, encoding="utf-8")) if os.path.exists(cur_path) else {"segments": {}}
    src = json.load(open(source_results_path, encoding="utf-8"))
    roles = {}
    if provenance_path and os.path.exists(provenance_path):
        prov = json.load(open(provenance_path, encoding="utf-8"))
        roles = prov.get("roles") or {}
    cur_ver = current_style_version if current_style_version is not None else cur.get("style_version")
    report = {"level_dir": level_dir, "level": level, "source_results_path": source_results_path,
              "provenance_path": provenance_path, "labels": {}, "merged_segments": {}, "seed_copies": {}}
    for label in labels:
        wav = f"{level_dir}/narration/{label}.wav"
        existing = (cur.get("segments") or {}).get(label)
        if existing and existing.get("status") not in _OVERWRITABLE_STATUSES:
            report["labels"][label] = {"ok": False,
                                       "reason": f"EXISTING_ENTRY_PRESENT({existing.get('status')})_NOT_OVERWRITTEN"}
            continue
        src_entry = (src.get("segments") or {}).get(label)
        witnesses, notes = [], {}
        role = roles.get(label)
        if role and role.get("sha256"):
            witnesses.append(role["sha256"])
            notes["seed_provenance_sha256"] = role["sha256"]
            notes["seed_src"] = role.get("src")
        else:
            notes["seed_provenance_sha256"] = None
            if not seed_wav:
                witnesses.append("NO_SEED_PROVENANCE")
        src_wav = None
        if isinstance(src_entry, dict) and src_entry.get("path"):
            src_wav = (src_entry["path"] if os.path.isabs(src_entry["path"])
                       else os.path.join(source_root, src_entry["path"]))
        if src_wav and os.path.exists(src_wav):
            notes["source_wav_current_sha256"] = sha256_file(src_wav)
            witnesses.append(notes["source_wav_current_sha256"])
        else:
            notes["source_wav_current_sha256"] = None
            witnesses.append("SOURCE_WAV_MISSING")
        eval_wav = wav
        if seed_wav and src_wav and os.path.exists(src_wav):
            cur_sha = sha256_file(wav) if os.path.exists(wav) else None
            if cur_sha != notes["source_wav_current_sha256"]:
                eval_wav = src_wav
                report["seed_copies"][label] = {"from": src_wav, "to": wav, "replaces_existing_sha256": cur_sha}
                # 置換される現行wav(Trial raw等)についてのprovenance(copy時sha256)は新wavの証拠にならない。
                # 元wavのsha256自体 + trimmed_duration witness(後述、必須)で同一性を確認する。
                witnesses = [w for w in witnesses if w != notes.get("seed_provenance_sha256")] or []
                notes["seed_provenance_ignored_because_wav_replaced"] = True
        ev = evaluate_inheritance(src_entry, eval_wav, expected_text=(expected_texts or {}).get(label),
                                  witness_sha256s=witnesses, require_duration_witness=require_duration_witness)
        src_ver = src.get("style_version")
        rec = {"ok": ev["ok"], "reason": ev["reason"], "current_wav_sha256": ev["current_sha256"], **notes,
               "source_style_version": src_ver, "current_style_version_in_results": cur_ver}
        if ev["ok"] and src_ver != cur_ver and not cross_version_accepted_by:
            rec["ok"], rec["reason"] = False, "STYLE_VERSION_MISMATCH_NO_ACCEPTANCE_POINTER"
        f1 = None
        if rec["ok"] and rejudge_f1:
            f1 = rejudge_with_current_judge(src_entry, level, label)
            rec["f1_rejudge"] = f1
            if not f1["ok"]:
                rec["ok"], rec["reason"] = False, f"F1_REJUDGE_NG:{f1.get('reason')}"
        report["labels"][label] = rec
        if rec["ok"]:
            report["merged_segments"][label] = build_inherited_entry(
                src_entry, wav, ev, {"kind": "other_run_results_with_seed_provenance" if not seed_wav
                                     else "other_run_results_seeded_wav",
                                     "source_results_path": source_results_path, "provenance_path": provenance_path},
                source_style_version=src_ver, cross_version_accepted_by=cross_version_accepted_by if src_ver != cur_ver else None,
                f1_rejudge=f1, expected_text=(expected_texts or {}).get(label))
        else:
            report["seed_copies"].pop(label, None)
    report["inherited"] = sorted(report["merged_segments"])
    report["not_inherited"] = sorted(l for l, r in report["labels"].items() if not r["ok"])
    return report


def rebuild_state_multi(level_dir: str, specs: list, expected_texts: Optional[dict], **kw) -> dict:
    """specs=[{labels:[..], source_results_path, source_root, provenance_path}]。各sourceのreportを1つへ統合する。"""
    merged = None
    for sp in specs:
        rep = rebuild_state(level_dir, sp["source_results_path"], sp["source_root"], sp.get("provenance_path"),
                            sp["labels"], expected_texts, **kw)
        if merged is None:
            merged = rep
            merged["sources"] = [sp["source_results_path"]]
            continue
        for k in ("labels", "merged_segments", "seed_copies"):
            merged[k].update(rep[k])
        merged["sources"].append(sp["source_results_path"])
    merged["inherited"] = sorted(merged["merged_segments"])
    merged["not_inherited"] = sorted(l for l, r in merged["labels"].items() if not r["ok"])
    return merged


def apply_state(level_dir: str, report: dict, expected_texts: Optional[dict] = None) -> str:
    """rebuild_stateの結果(inheritedのみ)を、level_dir/audit/tts_generation_results.jsonへ書き込む。
    OF-X4: expected_text(inheritedの全label分)が揃っていなければ書き込まず中止する。
    実行前に元のresultsを同ディレクトリへ`.pre_inherit_<ts>.json`としてcopy保全する。非OK entryは上書きしない。
    seed_copiesがあるlabelは、既存wavを`narration/_replaced_02/`へ退避(削除しない)してから元wavをcopyする。
    戻り値=バックアップpath。"""
    missing = [l for l in report["merged_segments"] if not (expected_texts or {}).get(l)]
    if missing:
        raise SystemExit(f"[ABORT][OF-X4] --apply にはexpected_textが必須です(不足label: {missing})")
    path = f"{level_dir}/audit/tts_generation_results.json"
    cur = json.load(open(path, encoding="utf-8"))
    ts = time.strftime('%Y%m%dT%H%M%S')
    backup = f"{level_dir}/audit/tts_generation_results.pre_inherit_{ts}.json"
    shutil.copyfile(path, backup)
    for label, entry in report["merged_segments"].items():
        existing = cur["segments"].get(label)
        assert not existing or existing.get("status") in _OVERWRITABLE_STATUSES, label
        seed = (report.get("seed_copies") or {}).get(label)
        if seed:
            dst = seed["to"]
            if os.path.exists(dst):
                rdir = os.path.join(os.path.dirname(dst), "_replaced_02")
                os.makedirs(rdir, exist_ok=True)
                shutil.move(dst, os.path.join(rdir, f"{os.path.basename(dst)[:-4]}.{(seed.get('replaces_existing_sha256') or 'x')[:8]}.wav"))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copyfile(seed["from"], dst)
            if sha256_file(dst) != entry["sha256"]:
                raise SystemExit(f"[ABORT] seed copy後のsha256が一致しません: {label}")
            entry["validation_inheritance"]["seeded_wav"] = {"from": seed["from"], "to": dst,
                                                              "replaced_existing_sha256": seed.get("replaces_existing_sha256")}
        cur["segments"][label] = entry
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cur, f, ensure_ascii=False, indent=2)
    return backup


def derive_expected_texts(level_dir: str, level: str, labels: list) -> dict:
    """OF-X4: 現行parts.json / support_texts / title(topic_intro文)から期待textを導出する(runnerと同じ式)。"""
    out = {}
    parts = json.load(open(f"{level_dir}/parts.json", encoding="utf-8"))
    sup_name = "a2_support_texts.json" if level == "a2" else "b1_support_texts.json"
    sup_path = f"{level_dir}/{sup_name}"
    support = json.load(open(sup_path, encoding="utf-8")) if os.path.exists(sup_path) else {}
    ep_path = os.path.join(os.path.dirname(level_dir.rstrip("/\\")), "entry_point.json")
    ep = json.load(open(ep_path, encoding="utf-8")) if os.path.exists(ep_path) else {}
    for l in labels:
        if l == "topic_intro":
            out[l] = f"Today's topic is {parts['title']}."
        elif l == "in_one_line":
            out[l] = parts["in_one_line"]
        elif l == "japanese_title" and ep.get("japanese_title"):
            out[l] = ep["japanese_title"]
        elif l in support:
            out[l] = support[l]
        elif l.startswith("full_story_part") and l.replace("full_story_", "") in parts:
            out[l] = parts[l.replace("full_story_", "")]
    return out


def main():
    ap = argparse.ArgumentParser(description="seed segmentの検証済み状態の証拠つき引継ぎ(既定dry-run: 新規ファイルへ出力のみ)")
    ap.add_argument("--level-dir", required=True)
    ap.add_argument("--level", required=True, choices=["a2", "b1b"])
    ap.add_argument("--source", action="append", required=True,
                    help="'label1,label2|source_results.json|source_root[|provenance.json]' (複数指定可)")
    ap.add_argument("--expected-texts-json", default=None, help="label->期待textのjson")
    ap.add_argument("--expected-texts-auto", action="store_true", help="現行parts.json/support_texts/titleから導出(OF-X4)")
    ap.add_argument("--rejudge-f1", action="store_true", help="保存済みasr_textを現行(F1後)判定で再判定(OF-X6)")
    ap.add_argument("--cross-version-accepted-by", default=None, help="style_version不一致の受入れ記録ポインタ(OF-X5)")
    ap.add_argument("--seed-wav", action="store_true", help="元runのwavを現在のnarrationへ置く(apply時、既存wavは_replaced_02へ退避)")
    ap.add_argument("--output", required=True, help="判定結果の出力先(新規ファイル。既存なら中止)")
    ap.add_argument("--apply", action="store_true", help="resultsへ実際に書込む(バックアップ後)。既定はdry-run。expected_text必須")
    a = ap.parse_args()
    if os.path.exists(a.output):
        raise SystemExit(f"出力先が既に存在します(上書き禁止): {a.output}")
    specs = []
    all_labels = []
    for s in a.source:
        parts = s.split("|")
        labels = [x.strip() for x in parts[0].split(",") if x.strip()]
        specs.append({"labels": labels, "source_results_path": parts[1], "source_root": parts[2],
                      "provenance_path": parts[3] if len(parts) > 3 and parts[3] else None})
        all_labels += labels
    exp = {}
    if a.expected_texts_json:
        exp.update(json.load(open(a.expected_texts_json, encoding="utf-8")))
    if a.expected_texts_auto:
        for k, v in derive_expected_texts(a.level_dir, a.level, all_labels).items():
            exp.setdefault(k, v)
    if a.apply:
        missing = [l for l in all_labels if not exp.get(l)]
        if missing:
            raise SystemExit(f"[ABORT][OF-X4] --apply にはexpected_textが必須です(不足label: {missing})。"
                             "--expected-texts-auto または --expected-texts-json を指定してください。")
    rep = rebuild_state_multi(a.level_dir, specs, exp or None, level=a.level, rejudge_f1=a.rejudge_f1,
                              cross_version_accepted_by=a.cross_version_accepted_by, seed_wav=a.seed_wav)
    rep["expected_texts_used"] = exp
    if a.apply:
        rep["applied_backup"] = apply_state(a.level_dir, rep, exp)
    os.makedirs(os.path.dirname(a.output) or ".", exist_ok=True)
    with open(a.output, "w", encoding="utf-8") as f:
        json.dump(rep, f, ensure_ascii=False, indent=2)
    print(json.dumps({"inherited": rep["inherited"], "not_inherited": rep["not_inherited"],
                      "reasons": {l: r["reason"] for l, r in rep["labels"].items()}}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
