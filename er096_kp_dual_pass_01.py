# ============================================================
# er096_kp_dual_pass_01.py
# FAMILY-XZ-ASR-PASS-CONDITION-SPEC-AUDIT-01 委任_03 [D-2](2026-10-22、UDR #139 APPROVED_FOR_PRODUCTION)
#
# KP英語phrase「Primary(OpenAI)・Secondary(Azure)の両方PASS必須」のFamily X/Z Production配線の共通部品。
#   - 判定本体は er078_asr_unified_judge_01 の `dual_required` モード(KP英語phrase専用)。本moduleは配線側の部品だけを持つ。
#   - 6呼出点(X default: generate_key_phrase_component_verified 内のMinimal 2+English Lock 2 / X K2: _styled_two_stage の primary・lock /
#     Z: _kp_en_two_stage の primary・lock)だけが `dual_pass_required=dual_enabled()` を渡す。KP英語解説・phrase_repeat・KP日本語・
#     その他全音声・Family A/B/Cは渡さない(静的test = er096_kp_dual_pass_01_test_01 の AST test で固定)。
#   - rollback = module定数 KP_EN_PHRASE_DUAL_REQUIRED(env/flagではない)。False = 6呼出点が従来どおり(dual_pass_required=False)。
#   - 共有モジュール er006_audio_cost_pilot_02_shared_narration.py は編集しない(Family A/B/C隔離)。X default profileは本module
#     の X専用関数 ensure_key_phrase_english_component_x_dual から、同一構造のMasterAudioKey(version末尾に `+dual1`)を組み立てる。
#     旧共有key(legacy)のentryは上書きしない。
#   - 再利用点6箇所はすべて共通helper `kp_dual_reuse_ok`(fail-closed)を呼ぶ。
#       X: (1)同一out_dirの前回results(runner `_generate_or_reuse_kp` role=english) (2)`try_inherit_from_cached`(validation inheritance、API 0)
#          (3)Store key A (4)Store key B [(3)(4)=K2 profile、get_or_generate(reuse_gate=)] (5)X default profileの`+dual1` key [get_or_generate(reuse_gate=)]
#       Z: (6)`generate_or_reuse_z` の kp_en
#   - gateが判定できなければ不合格(fail-closed): Primary転写なし / sha256不一致 / Azure例外・空転写・circuit open は再利用しない。
#     Azure**障害**=技術STOP(再利用も再生成もしない)、Azure**NG**のときだけ再生成。
# ============================================================
from __future__ import annotations

import hashlib
import os
import time

import er006_master_audio_store_01 as store
import er006_secondary_asr_01 as secondary_asr
import er078_asr_unified_judge_01 as uj

# ---- rollback(module定数。env/flagではない) ----
KP_EN_PHRASE_DUAL_REQUIRED = True
CHECK_VERSION = "kp_dual_check_v1"
DUAL_KEY_VERSION_SUFFIX = "+dual1"   # X default profileの専用Store key(旧共有keyのentryは上書きしない)

ACTION_REUSE = "reuse"
ACTION_REGENERATE = "regenerate"
ACTION_TECHNICAL_STOP = "technical_stop"
TECHNICAL_STOP_STATUS = "TECHNICAL_STOP_SECONDARY_UNAVAILABLE"


def dual_enabled() -> bool:
    """単一のflag読取関数。6呼出点はすべてこの関数の戻り値を `dual_pass_required` に渡す(他から直接Trueを渡さない)。"""
    return bool(KP_EN_PHRASE_DUAL_REQUIRED)


def _sha256_file(path: str) -> str | None:
    try:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError:
        return None


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S")


# ============================================================
# 証跡(kp_dual_check): 生成時・S1確認時に作り、Store entry / results entry に保存する
# ============================================================
def _check_from_dual_audit(aj: dict, wav_path: str, canonical_text: str, *, source: str) -> dict | None:
    d = (aj or {}).get("dual")
    if not isinstance(d, dict):
        return None
    ok = bool(aj.get("state") in uj.PASSING_STATES and d.get("required") and d.get("primary_pass") and d.get("secondary_pass")
              and not d.get("primary_rescued_by_secondary"))
    return {
        "version": CHECK_VERSION, "ok": ok, "source": source, "canonical_text": canonical_text,
        "wav_sha256": _sha256_file(wav_path),
        "primary": {"provider": "openai", "text": d.get("primary_text"), "pass": bool(d.get("primary_pass")),
                    "rescued_by_secondary": bool(d.get("primary_rescued_by_secondary")),
                    "rescue_layers": list(d.get("primary_rescue_layers") or [])},
        "secondary": {"provider": "azure", "text": d.get("secondary_text"), "pass": bool(d.get("secondary_pass")),
                      "called": bool(d.get("secondary_called"))},
        "judge_state": aj.get("state"), "reason_code": aj.get("reason_code"), "checked_at": _now(),
    }


def kp_dual_check_from_result(r: dict, wav_path: str, canonical_text: str) -> dict | None:
    """生成結果dict(strict/Store/Zの戻り値)の`asr_judgement.dual`から証跡を作る。dual未実施(rollback等)はNone。"""
    if not isinstance(r, dict) or r.get("status") != "OK":
        return None
    return _check_from_dual_audit(r.get("asr_judgement") or {}, wav_path, canonical_text, source="generation")


def attach_kp_dual_check(r: dict, wav_path: str, canonical_text: str) -> dict:
    """Z等、Storeを経由しない生成結果にも証跡を付ける(additive)。"""
    chk = kp_dual_check_from_result(r, wav_path, canonical_text)
    if chk is not None:
        r["kp_dual_check"] = chk
    return r


# ============================================================
# 判定の再実行(同一の統一judge adapterを通す。dual_required=True)
# ============================================================
def evaluate_dual(canonical_text: str, primary_text: str, wav_path: str, *, secondary_text: str | None = None,
                  max_extra_chars: int = 10) -> dict:
    """保存済みPrimary転写を現行分類器で再判定し、Secondary転写が与えられればAPI 0、無ければAzureを1回呼ぶ(S1)。
    戻り値: {verified, state, technical_stop, azure_real_calls, dual(audit), asr_judgement, primary_text, secondary_text}。"""
    import er003_v1_repro01_main_generate as repro01
    ledger_phrases = [h["canonical_spelling"] for h in repro01.pronun_ledger.get_hint_for_text(canonical_text, min_confidence="low")]
    sha = secondary_asr._wav_sha256(wav_path)
    cache = uj.SecondaryCache()
    if secondary_text is not None and str(secondary_text).strip() and sha:
        cache._store[(sha, "azure", "en", secondary_asr._phrase_hash(ledger_phrases))] = uj.SecondaryOutcome(secondary_text)
    max_len = len(canonical_text) + max_extra_chars
    detail = secondary_asr.evaluate_attempt_with_cascade_detail(
        canonical_text, primary_text, [], wav_path, language="en-US", ledger_phrases=ledger_phrases,
        cascade_enabled=secondary_asr.FEATURE_FLAG_SECONDARY_ASR_ENABLED, enable_non_latin_cascade=True,
        attempt_ctx={"slot": 1, "is_last_slot": False, "script_version": "v0", "cache": cache, "max_len": max_len, "dual_required": True})
    aj = detail.get("asr_judgement") or {}
    length_ok = primary_text is not None and len(primary_text) <= max_len
    final_len_ok = uj.final_length_ok(length_ok, detail)
    verified = bool(detail.get("verified")) and final_len_ok
    state = aj.get("state")
    d = aj.get("dual") or {}
    return {
        "verified": verified, "state": state, "technical_stop": state == uj.NG_SECONDARY_UNAVAILABLE,
        "azure_real_calls": (aj.get("adapter") or {}).get("azure_real_calls", 0),
        "dual": d, "asr_judgement": aj, "primary_text": primary_text, "secondary_text": d.get("secondary_text"),
        "final_length_ok": final_len_ok,
    }


def _entry_primary_text(entry: dict) -> str | None:
    for src in (entry.get("asr_text"), (entry.get("qa_evidence") or {}).get("asr_text")):
        if src:
            return src
    for k in ("asr_judgement", "asr_judgement_inherited"):
        aj = entry.get(k)
        if isinstance(aj, dict):
            t = (aj.get("primary") or {}).get("text")
            if t:
                return t
    return None


def _stored_check(entry: dict) -> dict | None:
    chk = entry.get("kp_dual_check")
    if isinstance(chk, dict) and chk.get("version") == CHECK_VERSION:
        return chk
    return None


def kp_dual_reuse_ok(entry: dict, *, wav_path: str, canonical_text: str, allow_s1: bool, label: str = "") -> dict:
    """KP英語phrase再利用6点の共通helper(fail-closed)。entry = Store entry / 前回results entry(qa_evidence・asr_judgement・
    kp_dual_check・asr_textを含みうるdict)。戻り値: {action, ok, reason, kp_dual_check, azure_real_calls, source}。
      1. wav実在・sha256を計算できる。
      2. 保存済みdual証跡(`kp_dual_check`)があれば: canonical一致・wav sha256一致・両Provider転写あり -> 現行分類器でAPI 0で再判定し
         `NG_DUAL_PRIMARY_NOT_PASS`/救済依存/Secondary不受理なら再利用しない(regenerate)。
      3. 証跡が無ければ allow_s1=True のときだけ S1: 保存済みPrimary転写を使い、Azureを1回だけ呼んで両方PASSを確認する(PASSなら証跡を保存)。
         Primary転写が無ければ regenerate。Azure障害(例外/空転写/circuit open)= technical_stop(再利用も再生成もしない)。
      4. allow_s1=False(API 0の文脈)で証跡が無ければ不可(action=regenerate扱い、呼出側はSKIPPED/再生成)。"""
    if not wav_path or not os.path.exists(wav_path):
        return {"action": ACTION_REGENERATE, "ok": False, "reason": "wav_missing", "kp_dual_check": None, "azure_real_calls": 0}
    sha = _sha256_file(wav_path)
    chk = _stored_check(entry or {})
    if chk is None and isinstance(entry, dict):
        # 生成時のasr_judgement.dual(または継承)から導出できる証跡(例: 前回resultsのentry)
        for k in ("asr_judgement", "asr_judgement_inherited"):
            aj = entry.get(k)
            if isinstance(aj, dict) and isinstance(aj.get("dual"), dict):
                chk = _check_from_dual_audit(aj, wav_path, canonical_text, source="derived_from_asr_judgement")
                if chk is not None:
                    break
    if chk is not None:
        sec_t = (chk.get("secondary") or {}).get("text")
        pri_t = (chk.get("primary") or {}).get("text")
        if (chk.get("canonical_text") != canonical_text or chk.get("wav_sha256") != sha or not pri_t
                or not (sec_t and str(sec_t).strip())):
            chk = None   # 証跡が現物と対応しない/不完全 -> 無いものとして扱う(S1か再生成)
        else:
            ev = evaluate_dual(canonical_text, pri_t, wav_path, secondary_text=sec_t)
            new_chk = _check_from_dual_audit(ev["asr_judgement"], wav_path, canonical_text, source="stored_evidence_rejudged")
            ok = bool(ev["verified"] and new_chk and new_chk["ok"])
            return {"action": ACTION_REUSE if ok else ACTION_REGENERATE, "ok": ok,
                    "reason": "stored_dual_evidence_ok" if ok else f"stored_dual_evidence_rejudge_ng:{ev['state']}",
                    "kp_dual_check": new_chk if ok else (new_chk or chk), "azure_real_calls": ev["azure_real_calls"],
                    "source": "stored_evidence_rejudged"}
    if not allow_s1:
        return {"action": ACTION_REGENERATE, "ok": False, "reason": "no_dual_evidence_api0_context", "kp_dual_check": None,
                "azure_real_calls": 0}
    pri_t = _entry_primary_text(entry or {})
    if not pri_t:
        return {"action": ACTION_REGENERATE, "ok": False, "reason": "no_primary_transcript", "kp_dual_check": None, "azure_real_calls": 0}
    rs = getattr(secondary_asr, "_RUN_STATE", None)
    if rs is not None and getattr(rs, "circuit_open", False):
        return {"action": ACTION_TECHNICAL_STOP, "ok": False, "reason": "secondary_circuit_open", "kp_dual_check": None,
                "azure_real_calls": 0}
    ev = evaluate_dual(canonical_text, pri_t, wav_path)
    if ev["technical_stop"]:
        return {"action": ACTION_TECHNICAL_STOP, "ok": False, "reason": "secondary_unavailable", "kp_dual_check": None,
                "azure_real_calls": ev["azure_real_calls"]}
    new_chk = _check_from_dual_audit(ev["asr_judgement"], wav_path, canonical_text, source="s1_confirm")
    ok = bool(ev["verified"] and new_chk and new_chk["ok"])
    return {"action": ACTION_REUSE if ok else ACTION_REGENERATE, "ok": ok,
            "reason": "s1_dual_ok" if ok else f"s1_dual_ng:{ev['state']}", "kp_dual_check": new_chk,
            "azure_real_calls": ev["azure_real_calls"], "source": "s1_confirm"}


def technical_stop_entry(label: str, decision: dict) -> dict:
    return {"status": TECHNICAL_STOP_STATUS, "label": label, "technical_stop": True, "restartable": True,
            "approval_required": False, "human_review_required": False, "asr_verified": False,
            "reason": "KP dual reuse gate: Secondary(Azure)障害のため再利用判定不能(再利用も再生成もしない。再実行で再開可)",
            "kp_dual_reuse_gate": {k: decision.get(k) for k in ("action", "reason")}}


# ============================================================
# Store reuse_gate(X K2 key A/B・X default `+dual1` key)
# ============================================================
class KpDualReuseGate:
    """store.get_or_generate(..., reuse_gate=KpDualReuseGate())。entryは qa_evidence/asr_judgement/kp_dual_check を持つ。"""

    def __call__(self, entry: dict, key, master_id: str) -> dict:
        probe = dict(entry)
        probe.update(entry.get("qa_evidence") or {})        # asr_text
        probe["asr_judgement"] = entry.get("asr_judgement")
        d = kp_dual_reuse_ok(probe, wav_path=entry["audio_path"], canonical_text=key.canonical_text, allow_s1=True,
                             label="master:" + str(key.style_instruction_id))
        return {"action": d["action"], "reason": d["reason"], "kp_dual_check": d.get("kp_dual_check"),
                "azure_real_calls": d.get("azure_real_calls", 0)}

    def on_generated(self, r: dict, stored_path: str, key) -> dict | None:
        return kp_dual_check_from_result(r, stored_path, key.canonical_text)


# ============================================================
# X default profile: 共有モジュールを編集せず、同一構造のkey(+dual1)でStore経由取得
# ============================================================
def dual_store_key(used_form_tts_safe: str, tts_backend: str = "structured_separation"):
    import er006_audio_cost_pilot_02_shared_narration as shared
    version = shared.KEY_PHRASE_TRIM_POLICY_VERSION + (DUAL_KEY_VERSION_SUFFIX if dual_enabled() else "")
    return store.MasterAudioKey(
        language="en", speaker_voice="Aoede", tts_model_id=shared._resolve_shared_narration_model("en", tts_backend),
        canonical_text=used_form_tts_safe, level=None, style_instruction_id="key_phrase_english_component",
        style_instruction_version=version)


def ensure_key_phrase_english_component_x_dual(used_form_tts_safe: str, out_path: str,
                                               tts_backend: str = "structured_separation") -> dict:
    """X runner `_kp_english_generate_fn` の default 分岐から呼ぶ。rollback(KP_EN_PHRASE_DUAL_REQUIRED=False)時は共有関数へそのまま委譲
    (旧key・旧挙動とバイト同一)。True時は `+dual1` 専用keyで、再利用gate付き・`dual_pass_required=True` の生成を行う。"""
    import er003_v1_repro01_main_generate as repro01
    import er006_audio_cost_pilot_02_shared_narration as shared
    if not dual_enabled():
        return shared.ensure_key_phrase_english_component(used_form_tts_safe, out_path, tts_backend=tts_backend)
    key = dual_store_key(used_form_tts_safe, tts_backend)
    return store.get_or_generate(
        key, out_path,
        lambda p: repro01.generate_key_phrase_component_verified(
            used_form_tts_safe, p, tts_backend=tts_backend, dual_pass_required=dual_enabled()),
        reuse_gate=KpDualReuseGate())


# ============================================================
# 組立時の非blocking監査(Fable判断で採用。blockingゲート化はユーザー判断=範囲外): KP英語phraseのdual証跡欠落を警告ログ+summaryに記録する
# ============================================================
def _entry_has_dual_pass(e: dict) -> bool:
    chk = e.get("kp_dual_check")
    if isinstance(chk, dict) and chk.get("ok") is True:
        return True
    for k in ("asr_judgement", "asr_judgement_inherited"):
        aj = e.get(k)
        d = aj.get("dual") if isinstance(aj, dict) else None
        if isinstance(d, dict) and d.get("required") and d.get("primary_pass") and d.get("secondary_pass") \
                and aj.get("state") in uj.PASSING_STATES:
            return True
    return False


def assembly_audit(results: dict, level: str = "") -> dict:
    """tts_generation_results相当dictのKP英語phrase(status=OK)について両Provider PASSの証跡有無を数える。常に非blocking
    (戻り値と警告printのみ。Gate/assemblyの判定には使わない)。dual無効(rollback)時は {"enabled": False}。"""
    if not dual_enabled():
        return {"enabled": False}
    ok_ranks, missing = [], []
    for rank, subs in sorted(((results or {}).get("key_phrases") or {}).items(), key=lambda kv: str(kv[0])):
        e = (subs or {}).get("english") or {}
        if e.get("status") != "OK":
            continue
        (ok_ranks if _entry_has_dual_pass(e) else missing).append(str(rank))
    for r in missing:
        print(f"[WARN][KP-DUAL] {level} kp{r}_english: 両Provider PASSの証跡(kp_dual_check)がありません(非blocking監査。OPEN-440)。")
    return {"enabled": True, "checked": len(ok_ranks) + len(missing), "with_dual_evidence": ok_ranks, "missing_dual_evidence": missing,
            "blocking": False}
