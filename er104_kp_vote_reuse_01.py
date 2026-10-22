# ============================================================
# er104_kp_vote_reuse_01.py
# KP-THREE-ASR-MAJORITY-PRODUCTION-01 委任_02 (ユーザー承認 APPROVED_FOR_PRODUCTION、2026-10-22)
#
# KP英語phrase「3-ASR多数決(OpenAI・Azure・Whisper、2/3)」のFamily X/Z配線側の共通部品(旧 er096_kp_dual_pass_01 の後継。
# er096は履歴scriptとして残置し、Productionからimportしない: AST testで固定)。
#   - 判定本体は er078_asr_unified_judge_01 の `vote_required` モード + er104_kp_three_asr_vote_01.tally()。本moduleは配線側の部品だけ。
#   - 再利用6点(X: 前回results/inheritance/Store key A,B/X default `+vote1` key、Z: kp_en)はすべて `kp_vote_reuse_ok` を通る。
#     **再判定は本番adapter経由**(P-01): 保存Primary転写+保存Secondary転写(cache)+保存Whisper転写(同sha、無ければローカルWhisper)を
#     `evaluate_attempt_with_cascade_detail(vote_required=True)` に渡す。手書きの再判定(旧rejudge_stored)は置かない。
#   - 保存容器名は維持(P-05): entry field `kp_dual_check`、telemetry名`reuse_blocked_by_kp_dual_gate`・`kp_dual_gate`等は変更しない(共有Store無編集)。
#     version="kp_vote_check_v1" で新旧を区別する。旧`kp_dual_check_v1`と旧`asr_judgement.dual`は **読取専用**(中の転写でAPI 0再判定)。
#   - Azure障害(例外/空転写/circuit open)・Whisper障害(例外/import失敗/timeout/circuit open) = 技術STOP(再利用も再生成もしない)。
#     NG(通常) のときだけ再生成。HR Lock済みKPを新判定で自動解除しない(本moduleはLockを一切操作しない)。
# ============================================================
from __future__ import annotations

import os

import er006_master_audio_store_01 as store
import er006_secondary_asr_01 as secondary_asr
import er078_asr_unified_judge_01 as uj
import er104_kp_three_asr_vote_01 as kp3v

# ---- 単一flag読取(P-05: 全呼出点はこの関数だけを見る。実体はkp3vの定数) ----
CHECK_VERSION = kp3v.CHECK_VERSION
LEGACY_CHECK_VERSION = "kp_dual_check_v1"     # 読取専用(旧両方PASS必須時代の証跡)
VOTE_KEY_VERSION_SUFFIX = "+vote1"            # X default profileの専用Store key(旧共有keyのentryは上書きしない)

ACTION_REUSE = "reuse"
ACTION_REGENERATE = "regenerate"
ACTION_TECHNICAL_STOP = "technical_stop"
TECHNICAL_STOP_STATUS_SECONDARY = "TECHNICAL_STOP_SECONDARY_UNAVAILABLE"
TECHNICAL_STOP_STATUS_WHISPER = "TECHNICAL_STOP_WHISPER_UNAVAILABLE"
TECHNICAL_STOP_STATUS = TECHNICAL_STOP_STATUS_SECONDARY   # 互換(旧名の参照用)


def vote_enabled() -> bool:
    """単一のflag読取関数。呼出点はすべてこの戻り値を `vote_pass_required` に渡す(他から直接Trueを渡さない)。"""
    return kp3v.vote_enabled()


# ============================================================
# 証跡(kp_dual_check容器に kp_vote_check_v1 を保存)
# ============================================================
def kp_vote_check_from_result(r: dict, wav_path: str, canonical_text: str) -> dict | None:
    """生成結果dict(strict/Store/Zの戻り値)の`asr_judgement.vote`から証跡を作る。vote未実施(rollback等)はNone。"""
    if not isinstance(r, dict) or r.get("status") != "OK":
        return None
    aj = r.get("asr_judgement") or {}
    v = aj.get("vote")
    if not isinstance(v, dict):
        return None
    return kp3v.vote_check_from_audit(v, wav_path, canonical_text, source="generation", judge_state=aj.get("state"),
                                      verified=bool(aj.get("state") in uj.PASSING_STATES and v.get("state") in kp3v.PASSING))


def attach_kp_vote_check(r: dict, wav_path: str, canonical_text: str) -> dict:
    """Z等、Storeを経由しない生成結果にも証跡を付ける(additive)。容器名は`kp_dual_check`を維持(P-05)。"""
    chk = kp_vote_check_from_result(r, wav_path, canonical_text)
    if chk is not None:
        r["kp_dual_check"] = chk
    return r


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
    """保存済み証跡(新vote_v1または旧dual_v1[読取専用])。"""
    chk = entry.get("kp_dual_check")
    if isinstance(chk, dict) and chk.get("version") in (CHECK_VERSION, LEGACY_CHECK_VERSION):
        return chk
    return None


def _derive_check_from_asr_judgement(entry: dict, wav_path: str, canonical_text: str) -> dict | None:
    """前回resultsのentry等、`kp_dual_check`が無くasr_judgement(.vote新 / .dual旧[読取専用])だけある場合の導出。"""
    for k in ("asr_judgement", "asr_judgement_inherited"):
        aj = entry.get(k)
        if not isinstance(aj, dict):
            continue
        v = aj.get("vote")
        if isinstance(v, dict):
            return kp3v.vote_check_from_audit(v, wav_path, canonical_text, source="derived_from_asr_judgement",
                                              judge_state=aj.get("state"))
        d = aj.get("dual")
        if isinstance(d, dict):   # 旧dual(読取専用): 転写だけを使い、判定は現行(vote)で再実施する
            return {"version": LEGACY_CHECK_VERSION, "ok": False, "source": "derived_from_legacy_dual", "canonical_text": canonical_text,
                    "wav_sha256": kp3v.sha256_file(wav_path),
                    "primary": {"provider": "openai", "text": d.get("primary_text")},
                    "secondary": {"provider": "azure", "text": d.get("secondary_text")}}
    return None


# ============================================================
# 判定の再実行(同一の統一judge adapterを通す。vote_required=True)  P-01: 本番adapter経路
# ============================================================
def evaluate_vote(canonical_text: str, primary_text: str, wav_path: str, *, secondary_text: str | None = None,
                  whisper_text: str | None = None, max_extra_chars: int = 10) -> dict:
    """保存済みPrimary転写を現行分類器で再判定。Secondary転写が与えられればAPI 0、無ければAzureを1回呼ぶ(S1)。Whisper転写が与えられ
    (同sha)れば再転写せず、無ければ割れたときだけローカルWhisper(API 0)。戻り値: {verified, state, technical_stop, azure_real_calls, vote(audit), ...}。"""
    import er003_v1_repro01_main_generate as repro01
    ledger_phrases = [h["canonical_spelling"] for h in repro01.pronun_ledger.get_hint_for_text(canonical_text, min_confidence="low")]
    sha = secondary_asr._wav_sha256(wav_path)
    cache = uj.SecondaryCache()
    if secondary_text is not None and str(secondary_text).strip() and sha:
        cache._store[(sha, "azure", "en", secondary_asr._phrase_hash(ledger_phrases))] = uj.SecondaryOutcome(secondary_text)
    max_len = len(canonical_text) + max_extra_chars
    actx = {"slot": 1, "is_last_slot": False, "script_version": "v0", "cache": cache, "max_len": max_len, "vote_required": True}
    if whisper_text is not None and str(whisper_text).strip():
        actx["vote_whisper_fn"] = lambda: kp3v.whisper_vote(canonical_text, wav_path, sha=sha, max_len=max_len, stored_text=whisper_text)
    detail = secondary_asr.evaluate_attempt_with_cascade_detail(
        canonical_text, primary_text, [], wav_path, language="en-US", ledger_phrases=ledger_phrases,
        cascade_enabled=secondary_asr.FEATURE_FLAG_SECONDARY_ASR_ENABLED, enable_non_latin_cascade=True, attempt_ctx=actx)
    aj = detail.get("asr_judgement") or {}
    length_ok = primary_text is not None and len(primary_text) <= max_len
    final_len_ok = uj.final_length_ok(length_ok, detail)
    verified = bool(detail.get("verified")) and final_len_ok
    state = aj.get("state")
    v = aj.get("vote") or {}
    return {
        "verified": verified, "state": state, "technical_stop": state in uj.TECHNICAL_STOP_STATES,
        "azure_real_calls": (aj.get("adapter") or {}).get("azure_real_calls", 0),
        "vote": v, "asr_judgement": aj, "primary_text": primary_text, "secondary_text": (v.get("secondary") or {}).get("text"),
        "whisper_called": bool(v.get("whisper_called")), "row": v.get("row"), "final_length_ok": final_len_ok,
    }


def _check_from_eval(ev: dict, wav_path: str, canonical_text: str, source: str) -> dict | None:
    if not ev.get("vote"):
        return None
    return kp3v.vote_check_from_audit(ev["vote"], wav_path, canonical_text, source=source, judge_state=ev["state"], verified=ev["verified"])


def _stop_reason(ev: dict) -> str:
    return "whisper_unavailable" if ev["state"] == uj.NG_WHISPER_UNAVAILABLE else "secondary_unavailable"


def kp_vote_reuse_ok(entry: dict, *, wav_path: str, canonical_text: str, allow_s1: bool, label: str = "") -> dict:
    """KP英語phrase再利用6点の共通helper(fail-closed)。entry = Store entry / 前回results entry。戻り値: {action, ok, reason, kp_dual_check,
    azure_real_calls, source}。
      1. wav実在・sha256を計算できる。
      2. 保存済み証跡(`kp_dual_check`[version vote_v1または旧dual_v1]、または`asr_judgement.vote`/旧`.dual`)があれば: canonical一致・wav sha256一致・
         Primary/Secondary転写あり -> **本番adapter(vote_required)** でAPI 0(Azure再呼出なし)に再判定。割れればWhisper(保存転写[同sha]
         またはローカル)。PASSなら再利用、NGなら再生成。Whisper/Azure障害は技術STOP。
      3. 証跡が無ければ allow_s1=True のときだけ S1: 保存Primary転写でAzureを1回だけ呼びvoteを確認する。Primary転写が無ければ regenerate。
      4. allow_s1=False(API 0の文脈)で証跡が無ければ不可(regenerate扱い)。"""
    if not wav_path or not os.path.exists(wav_path):
        return {"action": ACTION_REGENERATE, "ok": False, "reason": "wav_missing", "kp_dual_check": None, "azure_real_calls": 0}
    sha = kp3v.sha256_file(wav_path)
    chk = _stored_check(entry or {})
    if chk is None and isinstance(entry, dict):
        chk = _derive_check_from_asr_judgement(entry, wav_path, canonical_text)
    if chk is not None:
        sec_t = (chk.get("secondary") or {}).get("text")
        pri_t = (chk.get("primary") or {}).get("text")
        if (chk.get("canonical_text") != canonical_text or chk.get("wav_sha256") != sha or not pri_t
                or not (sec_t and str(sec_t).strip())):
            chk = None   # 証跡が現物と対応しない/不完全 -> 無いものとして扱う(S1か再生成)
        else:
            w_t = (chk.get("whisper") or {}).get("text") if chk.get("version") == CHECK_VERSION else None
            ev = evaluate_vote(canonical_text, pri_t, wav_path, secondary_text=sec_t, whisper_text=w_t)
            if ev["technical_stop"]:
                return {"action": ACTION_TECHNICAL_STOP, "ok": False, "reason": _stop_reason(ev), "kp_dual_check": None,
                        "azure_real_calls": ev["azure_real_calls"], "source": "stored_evidence_rejudged"}
            new_chk = _check_from_eval(ev, wav_path, canonical_text, "stored_evidence_rejudged")
            ok = bool(ev["verified"] and new_chk and new_chk["ok"])
            return {"action": ACTION_REUSE if ok else ACTION_REGENERATE, "ok": ok,
                    "reason": "stored_vote_evidence_ok" if ok else f"stored_vote_evidence_rejudge_ng:{ev['state']}",
                    "kp_dual_check": new_chk if ok else (new_chk or chk), "azure_real_calls": ev["azure_real_calls"],
                    "source": "stored_evidence_rejudged"}
    if not allow_s1:
        return {"action": ACTION_REGENERATE, "ok": False, "reason": "no_vote_evidence_api0_context", "kp_dual_check": None,
                "azure_real_calls": 0}
    pri_t = _entry_primary_text(entry or {})
    if not pri_t:
        return {"action": ACTION_REGENERATE, "ok": False, "reason": "no_primary_transcript", "kp_dual_check": None, "azure_real_calls": 0}
    rs = getattr(secondary_asr, "_RUN_STATE", None)
    if rs is not None and getattr(rs, "circuit_open", False):
        return {"action": ACTION_TECHNICAL_STOP, "ok": False, "reason": "secondary_circuit_open", "kp_dual_check": None, "azure_real_calls": 0}
    ev = evaluate_vote(canonical_text, pri_t, wav_path)
    if ev["technical_stop"]:
        return {"action": ACTION_TECHNICAL_STOP, "ok": False, "reason": _stop_reason(ev), "kp_dual_check": None,
                "azure_real_calls": ev["azure_real_calls"]}
    new_chk = _check_from_eval(ev, wav_path, canonical_text, "s1_confirm")
    ok = bool(ev["verified"] and new_chk and new_chk["ok"])
    return {"action": ACTION_REUSE if ok else ACTION_REGENERATE, "ok": ok,
            "reason": "s1_vote_ok" if ok else f"s1_vote_ng:{ev['state']}", "kp_dual_check": new_chk,
            "azure_real_calls": ev["azure_real_calls"], "source": "s1_confirm"}


def technical_stop_entry(label: str, decision: dict) -> dict:
    whisper = "whisper" in str(decision.get("reason") or "")
    return {"status": TECHNICAL_STOP_STATUS_WHISPER if whisper else TECHNICAL_STOP_STATUS_SECONDARY, "label": label, "technical_stop": True,
            "restartable": True, "approval_required": False, "human_review_required": False, "asr_verified": False,
            "reason": ("KP vote reuse gate: Whisper(ローカルASR)障害のため再利用判定不能(再利用も再生成もしない。再実行で再開可)" if whisper else
                       "KP vote reuse gate: Secondary(Azure)障害のため再利用判定不能(再利用も再生成もしない。再実行で再開可)"),
            "kp_dual_reuse_gate": {k: decision.get(k) for k in ("action", "reason")}}   # 容器名は維持(P-05)


# ============================================================
# Whisper事前確認とcircuit guard(P-08): KP stage(生成)の最初のTTSの前に1回だけモデルロード可否を確認し、失敗/circuit open中は
# TTSを回さず技術STOP(再実行で再開可・HRに入れない)にする。再利用だけで済む経路(割れが無い)はWhisperを必要としない。
# ============================================================
_PREFLIGHT: dict = {}


def preflight_once(*, force: bool = False) -> dict:
    """プロセス内で1回だけWhisper事前確認を行い記録を返す(モデルcache有無・load時間・model/compute type。runtime evidence用)。"""
    if force or not _PREFLIGHT:
        rec = kp3v.whisper_preflight()
        _PREFLIGHT.clear()
        _PREFLIGHT.update(rec)
        print(f"[KP-VOTE] whisper preflight: ok={rec.get('ok')} model={rec.get('model')}/{rec.get('compute_type')} "
              f"cache_present={rec.get('model_cache_present')} load_sec={rec.get('load_sec')} error={rec.get('error')}")
    return dict(_PREFLIGHT)


def reset_preflight() -> None:
    _PREFLIGHT.clear()


def whisper_technical_stop_entry(label: str, preflight: dict | None = None) -> dict:
    return {"status": TECHNICAL_STOP_STATUS_WHISPER, "label": label, "technical_stop": True, "restartable": True,
            "approval_required": False, "human_review_required": False, "asr_verified": False,
            "reason": "Whisper(ローカルASR)が利用できない(事前確認失敗またはcircuit open)ため、KP英語phraseのTTS生成を開始しない(再実行で再開可・承認不要)",
            "whisper_preflight": preflight, "events": list(kp3v.WHISPER_STATE.events[-3:])}


def guard_whisper(generate_fn, label: str = ""):
    """KP英語phraseの生成関数をwrapする: vote有効かつWhisper事前確認失敗/circuit open中はTTS/ASRを呼ばず技術STOP entryを返す。
    secondary_run_scope.guard_generate(Azure circuit)と同型。vote無効(rollback)ならgenerate_fnそのまま。"""
    import functools

    @functools.wraps(generate_fn)
    def _g(*a, **k):
        if vote_enabled():
            pf = preflight_once()
            if kp3v.whisper_circuit_open():
                return whisper_technical_stop_entry(label, pf)
        return generate_fn(*a, **k)
    return _g


# ============================================================
# Store reuse_gate(X K2 key A/B・X default `+vote1` key)
# ============================================================
class KpVoteReuseGate:
    """store.get_or_generate(..., reuse_gate=KpVoteReuseGate())。entryは qa_evidence/asr_judgement/kp_dual_check(容器名維持)を持つ。"""

    def __call__(self, entry: dict, key, master_id: str) -> dict:
        probe = dict(entry)
        probe.update(entry.get("qa_evidence") or {})        # asr_text
        probe["asr_judgement"] = entry.get("asr_judgement")
        d = kp_vote_reuse_ok(probe, wav_path=entry["audio_path"], canonical_text=key.canonical_text, allow_s1=True,
                             label="master:" + str(key.style_instruction_id))
        return {"action": d["action"], "reason": d["reason"], "kp_dual_check": d.get("kp_dual_check"),
                "azure_real_calls": d.get("azure_real_calls", 0)}

    def on_generated(self, r: dict, stored_path: str, key) -> dict | None:
        return kp_vote_check_from_result(r, stored_path, key.canonical_text)


# ============================================================
# X default profile: 共有モジュールを編集せず、同一構造のkey(+vote1)でStore経由取得
# ============================================================
def vote_store_key(used_form_tts_safe: str, tts_backend: str = "structured_separation"):
    import er006_audio_cost_pilot_02_shared_narration as shared
    version = shared.KEY_PHRASE_TRIM_POLICY_VERSION + (VOTE_KEY_VERSION_SUFFIX if vote_enabled() else "")
    return store.MasterAudioKey(
        language="en", speaker_voice="Aoede", tts_model_id=shared._resolve_shared_narration_model("en", tts_backend),
        canonical_text=used_form_tts_safe, level=None, style_instruction_id="key_phrase_english_component",
        style_instruction_version=version)


def ensure_key_phrase_english_component_x_vote(used_form_tts_safe: str, out_path: str,
                                               tts_backend: str = "structured_separation") -> dict:
    """X runner `_kp_english_generate_fn` の default 分岐から呼ぶ。rollback(KP_THREE_ASR_VOTE_ENABLED=False)時は共有関数へそのまま委譲
    (旧key・旧挙動とバイト同一)。True時は `+vote1` 専用keyで、再利用gate付き・`vote_pass_required=True` の生成を行う。"""
    import er003_v1_repro01_main_generate as repro01
    import er006_audio_cost_pilot_02_shared_narration as shared
    if not vote_enabled():
        return shared.ensure_key_phrase_english_component(used_form_tts_safe, out_path, tts_backend=tts_backend)
    key = vote_store_key(used_form_tts_safe, tts_backend)
    return store.get_or_generate(
        key, out_path,
        lambda p: repro01.generate_key_phrase_component_verified(
            used_form_tts_safe, p, tts_backend=tts_backend, vote_pass_required=vote_enabled()),
        reuse_gate=KpVoteReuseGate())


# ============================================================
# 組立時の非blocking監査(blockingゲート化はユーザー判断=範囲外): KP英語phraseのvote証跡欠落を警告ログ+summaryに記録する
# ============================================================
def _entry_has_vote_pass(e: dict) -> bool:
    chk = e.get("kp_dual_check")
    if isinstance(chk, dict) and chk.get("version") in (CHECK_VERSION, LEGACY_CHECK_VERSION) and chk.get("ok") is True:
        return True
    for k in ("asr_judgement", "asr_judgement_inherited"):
        aj = e.get(k)
        if not isinstance(aj, dict):
            continue
        v = aj.get("vote")
        if isinstance(v, dict) and v.get("state") in kp3v.PASSING and aj.get("state") in uj.PASSING_STATES:
            return True
    return False


def assembly_audit(results: dict, level: str = "") -> dict:
    """tts_generation_results相当dictのKP英語phrase(status=OK)について3-ASR多数決PASSの証跡有無を数える。常に非blocking
    (戻り値と警告printのみ)。vote無効(rollback)時は {"enabled": False}。"""
    if not vote_enabled():
        return {"enabled": False}
    ok_ranks, missing = [], []
    for rank, subs in sorted(((results or {}).get("key_phrases") or {}).items(), key=lambda kv: str(kv[0])):
        e = (subs or {}).get("english") or {}
        if e.get("status") != "OK":
            continue
        (ok_ranks if _entry_has_vote_pass(e) else missing).append(str(rank))
    for r in missing:
        print(f"[WARN][KP-VOTE] {level} kp{r}_english: 3-ASR多数決PASSの証跡(kp_dual_check[kp_vote_check_v1])がありません(非blocking監査。OPEN-451)。")
    return {"enabled": True, "checked": len(ok_ranks) + len(missing), "with_vote_evidence": ok_ranks, "missing_vote_evidence": missing,
            "blocking": False}
