# ============================================================
# er006_master_audio_store_01_test.py
# ER-006-MASTER-AUDIO-STORE-01: regression test
# ============================================================
# 実行方法: .venv/Scripts/python.exe er006_master_audio_store_01_test.py
# テスト用に一時的なStoreディレクトリへ切り替えて実行し、実行後に
# 元へ戻す(本番Storeを汚さない)。

from __future__ import annotations

import os
import shutil
import wave

import er006_master_audio_store_01 as store


def _write_dummy_wav(path: str, n_samples: int = 2400) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(24000)
        wf.writeframes(b"\x00\x00" * n_samples)


def _use_temp_store(test_fn):
    orig_store_dir = store.STORE_DIR
    orig_audio_dir = store.AUDIO_DIR
    orig_manifest = store.MANIFEST_PATH
    orig_telemetry = store.TELEMETRY_PATH
    tmp_dir = "er006_output/_test_master_audio_store_tmp"
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    store.STORE_DIR = tmp_dir
    store.AUDIO_DIR = f"{tmp_dir}/audio"
    store.MANIFEST_PATH = f"{tmp_dir}/manifest.json"
    store.TELEMETRY_PATH = f"{tmp_dir}/reuse_telemetry.jsonl"
    try:
        test_fn()
    finally:
        store.STORE_DIR = orig_store_dir
        store.AUDIO_DIR = orig_audio_dir
        store.MANIFEST_PATH = orig_manifest
        store.TELEMETRY_PATH = orig_telemetry
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)


def test_first_call_generates_second_call_reuses():
    def run():
        calls = {"n": 0}

        def fake_generate(out_path):
            calls["n"] += 1
            _write_dummy_wav(out_path)
            return {"status": "OK"}

        key = store.MasterAudioKey(
            language="en", speaker_voice="Charon", tts_model_id="gemini-2.5-pro-preview-tts",
            canonical_text="Welcome to English Your Way.")

        r1 = store.get_or_generate(key, "er006_output/_test_master_audio_store_tmp/out1.wav", fake_generate)
        assert r1["reused"] is False
        assert calls["n"] == 1

        r2 = store.get_or_generate(key, "er006_output/_test_master_audio_store_tmp/out2.wav", fake_generate)
        assert r2["reused"] is True
        assert calls["n"] == 1, "2回目はTTSを呼ばずreuseするはず"
        assert os.path.exists("er006_output/_test_master_audio_store_tmp/out2.wav")
        assert r1["master_audio_id"] == r2["master_audio_id"]
    _use_temp_store(run)
    print("PASS: test_first_call_generates_second_call_reuses")


def test_welcome_drift_resolved_across_b1_and_a2():
    # B1向け・A2向けで別々にWelcomeを生成しようとしても、level=Noneで
    # 同一Keyになるため、2回目はreuseされ、常に同一音声になる(drift
    # が起きようがない)。
    def run():
        calls = {"n": 0}

        def fake_generate(out_path):
            calls["n"] += 1
            _write_dummy_wav(out_path, n_samples=1000 + calls["n"])  # 呼ぶたびに違う長さになるTTSを模擬
            return {"status": "OK"}

        key_for_b1 = store.MasterAudioKey(
            language="en", speaker_voice="Charon", tts_model_id="gemini-2.5-pro-preview-tts",
            canonical_text="Welcome to English Your Way.", level=None)
        key_for_a2 = store.MasterAudioKey(
            language="en", speaker_voice="Charon", tts_model_id="gemini-2.5-pro-preview-tts",
            canonical_text="Welcome to English Your Way.", level=None)

        r_b1 = store.get_or_generate(key_for_b1, "er006_output/_test_master_audio_store_tmp/b1_welcome.wav", fake_generate)
        r_a2 = store.get_or_generate(key_for_a2, "er006_output/_test_master_audio_store_tmp/a2_welcome.wav", fake_generate)

        assert calls["n"] == 1, "B1/A2どちらもlevel=Noneの同一Keyなので、TTSは1回しか呼ばれないはず"
        assert r_a2["reused"] is True
        with wave.open("er006_output/_test_master_audio_store_tmp/b1_welcome.wav") as f1, \
             wave.open("er006_output/_test_master_audio_store_tmp/a2_welcome.wav") as f2:
            assert f1.getnframes() == f2.getnframes(), "B1/A2で同じ音声(同じ長さ)になっているはず(drift解消)"
    _use_temp_store(run)
    print("PASS: test_welcome_drift_resolved_across_b1_and_a2")


def test_key_phrase_duplicate_reuse_across_levels():
    # B1/A2で同一Key Phrase(voice/model/style全て同一)は再利用される。
    def run():
        calls = {"n": 0}

        def fake_generate(out_path):
            calls["n"] += 1
            _write_dummy_wav(out_path)
            return {"status": "OK"}

        key_b1 = store.MasterAudioKey(
            language="en", speaker_voice="Aoede", tts_model_id="gemini-2.5-pro-preview-tts",
            canonical_text="hostile architecture", level=None)
        key_a2 = store.MasterAudioKey(
            language="en", speaker_voice="Aoede", tts_model_id="gemini-2.5-pro-preview-tts",
            canonical_text="hostile architecture", level=None)

        store.get_or_generate(key_b1, "er006_output/_test_master_audio_store_tmp/kp_b1.wav", fake_generate)
        r2 = store.get_or_generate(key_a2, "er006_output/_test_master_audio_store_tmp/kp_a2.wav", fake_generate)
        assert calls["n"] == 1
        assert r2["reused"] is True
    _use_temp_store(run)
    print("PASS: test_key_phrase_duplicate_reuse_across_levels")


def test_different_text_does_not_reuse():
    def run():
        calls = {"n": 0}

        def fake_generate(out_path):
            calls["n"] += 1
            _write_dummy_wav(out_path)
            return {"status": "OK"}

        key1 = store.MasterAudioKey(
            language="en", speaker_voice="Aoede", tts_model_id="gemini-2.5-pro-preview-tts",
            canonical_text="hostile architecture")
        key2 = store.MasterAudioKey(
            language="en", speaker_voice="Aoede", tts_model_id="gemini-2.5-pro-preview-tts",
            canonical_text="blitzscaling")

        store.get_or_generate(key1, "er006_output/_test_master_audio_store_tmp/a.wav", fake_generate)
        store.get_or_generate(key2, "er006_output/_test_master_audio_store_tmp/b.wav", fake_generate)
        assert calls["n"] == 2, "テキストが違えばmaster_audio_idも変わり、reuseされないはず"
    _use_temp_store(run)
    print("PASS: test_different_text_does_not_reuse")


def test_voice_change_invalidates_master():
    def run():
        calls = {"n": 0}

        def fake_generate(out_path):
            calls["n"] += 1
            _write_dummy_wav(out_path)
            return {"status": "OK"}

        key_charon = store.MasterAudioKey(
            language="en", speaker_voice="Charon", tts_model_id="gemini-2.5-pro-preview-tts",
            canonical_text="Welcome to English Your Way.")
        key_aoede = store.MasterAudioKey(
            language="en", speaker_voice="Aoede", tts_model_id="gemini-2.5-pro-preview-tts",
            canonical_text="Welcome to English Your Way.")

        store.get_or_generate(key_charon, "er006_output/_test_master_audio_store_tmp/c.wav", fake_generate)
        r2 = store.get_or_generate(key_aoede, "er006_output/_test_master_audio_store_tmp/d.wav", fake_generate)
        assert calls["n"] == 2, "voiceが変わればmasterは無効化され、再生成されるはず"
        assert r2["reused"] is False
    _use_temp_store(run)
    print("PASS: test_voice_change_invalidates_master")


def test_failed_generation_not_cached():
    def run():
        def failing_generate(out_path):
            return {"status": "STOPPED", "reason": "simulated failure"}

        key = store.MasterAudioKey(
            language="en", speaker_voice="Charon", tts_model_id="gemini-2.5-pro-preview-tts",
            canonical_text="This will fail.")
        r = store.get_or_generate(key, "er006_output/_test_master_audio_store_tmp/fail.wav", failing_generate)
        assert r["status"] == "STOPPED"
        assert r["reused"] is False
        manifest = store._load_manifest()
        assert r["master_audio_id"] not in manifest, "失敗した生成はManifestへ登録されないはず"
    _use_temp_store(run)
    print("PASS: test_failed_generation_not_cached")


if __name__ == "__main__":
    test_first_call_generates_second_call_reuses()
    test_welcome_drift_resolved_across_b1_and_a2()
    test_key_phrase_duplicate_reuse_across_levels()
    test_different_text_does_not_reuse()
    test_voice_change_invalidates_master()
    test_failed_generation_not_cached()
    print("ALL TESTS PASSED")
