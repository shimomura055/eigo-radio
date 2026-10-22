# ============================================================
# er019_family_x_kp_en_k2_store_01.py
# FAMILY-X-APPROVED-SPEC-PRODUCTION-WIRING-AND-COFFEE-E2E-01 委任_02A(2026-10-16、Opus条件A R-01採用)
#
# KP英語(承認済みStyle K2)のMaster Audio Store「2段key」経路。Family X専用の新module(共有module
# `er006_audio_cost_pilot_02_shared_narration.py`[Family A/B/C/Zと共有・working tree差分0が機械的に強制されている]、
# `er006_master_audio_store_01.py`、`er003_v1_repro01_main_generate.py`は一切変更しない。Family A/B/Cのkey・送信Promptは
# バイト同一)。runner(er019_family_x_audio_production_runner_01.py)がprofileにKP_EN overrideがある(fx_20261016)ときだけ呼ぶ。
#
#   key A: instruction_path="primary"               / style_instruction_id=KP_EN_STORE_STYLE_ID / version="{trim}+k2.{K2 sha12}"
#          -> K2 primary 2回のみ(`KEY_PHRASE_MINIMAL_MAX_ATTEMPTS`)。通ればkey Aに保存・再利用される。
#   key B: instruction_path="english_lock_fallback" / 同id / version="{trim}+lock.{ENGLISH_LOCK sha12}"
#          -> K2 primaryが2回とも非OKのときだけ、ENGLISH_LOCK 2回(承認済み4回構成の後半)。通った音声はkey Bに保存する。
#          (key Aには保存しない=ENGLISH_LOCK音声が「K2音声」として別記事へ誤再利用されない。)
# 事実(報告対象): K2が通らないときは従来のMINIMAL+ENGLISH_LOCK(旧style)で代替生成される。この音声はkey Bで識別され、
# runnerのM3 Gate(er019_family_x_style_profile_01.kp_en_store_key_check)が非ブロッキングwarningとして列挙する。
# review_lockの会計は`_styled_two_stage`(@guarded_generate 1回、slot_offset 0/2、total 4)で従来の
# `generate_key_phrase_component_verified`・Family Zの`_kp_en_two_stage`と同一(Store reuse時は従来どおりLockを触らない)。
# ============================================================
from __future__ import annotations

import hashlib

import er003_v1_repro01_main_generate as repro01
import er006_audio_cost_pilot_02_shared_narration as shared
import er006_master_audio_store_01 as store
import er096_kp_dual_pass_01 as kp_dual  # KPDUAL-PROD-D2(2026-10-22、UDR #139): KP英語phrase Primary・Secondary両方PASS必須

KEY_PHRASE_STYLED_PATH_PRIMARY = "primary"
KEY_PHRASE_STYLED_PATH_FALLBACK = "english_lock_fallback"


def _sha12(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def key_phrase_styled_keys(used_form_tts_safe: str, style_text: str, style_id: str, style_tag: str,
                           tts_backend: str) -> tuple:
    """(key A[primary], key B[english_lock_fallback])を返す。keyの構成はここだけで決める(runner/testから共通利用)。"""
    model = shared._resolve_shared_narration_model("en", tts_backend)
    lock_text = repro01.KEY_PHRASE_ENGLISH_LOCK_INSTRUCTION

    def _mk(tag: str, text: str, path: str) -> "store.MasterAudioKey":
        return store.MasterAudioKey(
            language="en", speaker_voice="Aoede", tts_model_id=model, canonical_text=used_form_tts_safe, level=None,
            style_instruction_id=style_id,
            style_instruction_version=f"{shared.KEY_PHRASE_TRIM_POLICY_VERSION}+{tag}.{_sha12(text)}",
            instruction_path=path)

    return (_mk(style_tag, style_text, KEY_PHRASE_STYLED_PATH_PRIMARY),
            _mk("lock", lock_text, KEY_PHRASE_STYLED_PATH_FALLBACK))


@repro01.review_lock.guarded_generate("en")
def _styled_two_stage(text: str, out_path: str, *, style_text: str, key_b, tts_backend: str) -> dict:
    primary = repro01.generate_narration_snippet_verified_strict(
        text, "en", out_path, text, max_extra_chars=10, max_attempts=repro01.KEY_PHRASE_MINIMAL_MAX_ATTEMPTS,
        safety_margin_seconds=repro01.KEY_PHRASE_TRIM_SAFETY_MARGIN_SECONDS, disfluency_qa=True,
        style_prefix_override=style_text, asr_prompt=repro01.KEY_PHRASE_EN_ASR_NO_TRANSLATE_PROMPT,
        enable_non_latin_cascade=True, tts_backend=tts_backend,
        slot_offset=0, total_slots=repro01.KEY_PHRASE_TOTAL_MAX_ATTEMPTS,  # 4回構成の前半(HR queue対象外)
        dual_pass_required=kp_dual.dual_enabled())  # KPDUAL-PROD-D2: KP英語phrase=Primary・Secondary両方PASS必須
    if primary.get("status") == "OK":
        primary["fallback_used"] = False
        primary["primary_instruction_type"] = "STYLED"
        return primary
    if kp_dual.dual_enabled() and repro01._dual_circuit_open():
        # KPDUAL-PROD-D2(OF-KPD-P-02の最小緩和): Azure circuit breaker open中はENGLISH_LOCK段のTTSを回さない(技術STOP、最大試行・HR Lockの意味は不変)。
        primary["fallback_used"] = False
        primary["primary_instruction_type"] = "STYLED_ONLY_SECONDARY_CIRCUIT_OPEN"
        primary["english_lock_skipped_secondary_circuit_open"] = True
        return primary

    def _gen_lock(p: str) -> dict:
        return repro01.generate_narration_snippet_verified_strict(
            text, "en", p, text, max_extra_chars=10, max_attempts=repro01.KEY_PHRASE_ENGLISH_LOCK_MAX_ATTEMPTS,
            safety_margin_seconds=repro01.KEY_PHRASE_TRIM_SAFETY_MARGIN_SECONDS, disfluency_qa=True,
            style_prefix_override=repro01.KEY_PHRASE_ENGLISH_LOCK_INSTRUCTION,
            asr_prompt=repro01.KEY_PHRASE_EN_ASR_NO_TRANSLATE_PROMPT, enable_non_latin_cascade=True,
            tts_backend=tts_backend,
            slot_offset=repro01.KEY_PHRASE_MINIMAL_MAX_ATTEMPTS,
            total_slots=repro01.KEY_PHRASE_TOTAL_MAX_ATTEMPTS,  # 4回構成の後半(最終slot)
            dual_pass_required=kp_dual.dual_enabled())  # KPDUAL-PROD-D2

    fb = store.get_or_generate(key_b, out_path, _gen_lock,
                               reuse_gate=(kp_dual.KpDualReuseGate() if kp_dual.dual_enabled() else None))
    fb["fallback_used"] = True
    fb["primary_instruction_type"] = "ENGLISH_LOCK" if fb.get("status") == "OK" else "STYLED_AND_ENGLISH_LOCK_BOTH_FAILED"
    # legacy `generate_key_phrase_component_verified`と同じ会計(record_outcomeの実TTS試行数=4)。
    fb["fallback_attempts_log"] = primary.get("attempts_log")
    fb["minimal_attempts_log"] = primary.get("attempts_log")
    fb["english_lock_attempts_log"] = fb.get("attempts_log")
    return fb


def ensure_key_phrase_english_component_styled(used_form_tts_safe: str, out_path: str, *, style_text: str,
                                               style_id: str, style_tag: str = "k2",
                                               tts_backend: str = "speech_metadata_flash_lite") -> dict:
    """KP英語Component(Aoede)を、承認済みStyle(style_text=K2)で2段keyのMaster Audio Store経由で取得する。
    戻り値は常に`master_audio_key`(実際に使われたkey=AまたはB)を持つ。key Aのhit=TTS 0回、Aがmissでprimary OK=A保存、
    primary NG->key B(hitならLock段TTS 0回、missならENGLISH_LOCK 2回)。fallback音声はkey Aへ保存しない。
    注意: get_or_generate(key A)のgenerate_fn内でkey Bのget_or_generateが走る(manifestを更新する)が、その場合key Aは
    非OKのstand-inを返すためkey A側はmanifestを保存しない(stale manifestでkey Bを上書きしない)。"""
    key_a, key_b = key_phrase_styled_keys(used_form_tts_safe, style_text, style_id, style_tag, tts_backend)
    holder: dict = {}

    def _gen_a(p: str) -> dict:
        r = _styled_two_stage(used_form_tts_safe, p, style_text=style_text, key_b=key_b, tts_backend=tts_backend)
        if r.get("fallback_used") is True:
            # fallback経路(key Bで保存済み/または失敗)の結果。key Aへ保存させない(非OKのstand-inを返す)。
            holder["fb"] = r
            return {"status": "STYLED_PRIMARY_NOT_OK_FALLBACK_HANDLED_UNDER_KEY_B", "path": p}
        return r

    ra = store.get_or_generate(key_a, out_path, _gen_a,
                               reuse_gate=(kp_dual.KpDualReuseGate() if kp_dual.dual_enabled() else None))
    return holder["fb"] if "fb" in holder else ra
