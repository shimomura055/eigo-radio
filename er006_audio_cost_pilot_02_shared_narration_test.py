# ============================================================
# er006_audio_cost_pilot_02_shared_narration_test.py
# ============================================================
# 実行方法: .venv/Scripts/python.exe er006_audio_cost_pilot_02_shared_narration_test.py
from __future__ import annotations

import os
import shutil
import wave

import er003_v1_sing01_voice01_generate as voice01
import er006_audio_cost_pilot_02_shared_narration as shared
import er006_master_audio_store_01 as store


def _write_dummy_wav(path: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(24000)
        wf.writeframes(b"\x00\x00" * 2400)


def test_b1_and_a2_share_master_no_double_tts():
    tmp_dir = "er006_output/_test_shared_narration_tmp"
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    orig_store_dir, orig_audio_dir = store.STORE_DIR, store.AUDIO_DIR
    orig_manifest, orig_telemetry = store.MANIFEST_PATH, store.TELEMETRY_PATH
    store.STORE_DIR = f"{tmp_dir}/store"
    store.AUDIO_DIR = f"{tmp_dir}/store/audio"
    store.MANIFEST_PATH = f"{tmp_dir}/store/manifest.json"
    store.TELEMETRY_PATH = f"{tmp_dir}/store/reuse_telemetry.jsonl"

    calls = {"en": 0, "ja": 0}
    orig_en = voice01.generate_charon_english
    orig_ja = voice01.generate_charon_japanese

    def fake_en(text, out_path, **kwargs):
        calls["en"] += 1
        _write_dummy_wav(out_path)
        return {"status": "OK"}

    def fake_ja(text, out_path, expected_substring, max_attempts=6, **kwargs):
        calls["ja"] += 1
        _write_dummy_wav(out_path)
        return {"status": "OK"}

    voice01.generate_charon_english = fake_en
    voice01.generate_charon_japanese = fake_ja
    try:
        b1_dir = f"{tmp_dir}/b1b/narration"
        a2_dir = f"{tmp_dir}/a2/narration"
        r_b1 = shared.ensure_all_shared_narration_b1(b1_dir)
        r_a2 = shared.ensure_all_shared_narration_a2(a2_dir)

        assert calls["en"] == 9, f"welcome/preview_intro/key_phrases_intro/full_story_intro/num_one〜five = 9種、B1で生成後はA2で全てreuseされ、TTSはB1側の9回のみのはず。実際={calls['en']}"
        assert calls["ja"] == 1, "point_explanationはA2のみ、1回だけ生成されるはず"
        for name in shared.FIXED_ENGLISH_TEXTS:
            assert r_a2[name]["reused"] is True, f"{name}はA2側で必ずreuseされるはず"
            assert os.path.exists(f"{a2_dir}/{name}.wav")
        assert r_a2["point_explanation"]["reused"] is False  # A2で初生成
    finally:
        voice01.generate_charon_english = orig_en
        voice01.generate_charon_japanese = orig_ja
        store.STORE_DIR, store.AUDIO_DIR = orig_store_dir, orig_audio_dir
        store.MANIFEST_PATH, store.TELEMETRY_PATH = orig_manifest, orig_telemetry
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)
    print("PASS: test_b1_and_a2_share_master_no_double_tts")


def test_flash_lite_backend_uses_separate_master_key_and_does_not_touch_legacy_assets():
    """TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-02(C、
    2026-09-28): tts_backend="speech_metadata_flash_lite"のとき、
    MasterAudioKey.tts_model_idがFlash-Lite専用値になり、既存Structured
    Separation資産(tts_backend既定)とは別のmaster_audio_id(=別キー)に
    なることを確認する。既存資産の再利用可否には触れない(生成しない)。"""
    # FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(W2、2026-09-29):
    # _make_english_keyの引数にname(phrase名)を追加(Champion style map
    # がphraseごとに異なる文言を持つため)。welcomeを使う限り本テストの
    # 意図(legacy/flash-lite backendで別master_audio_idになる)は無変更。
    key_legacy_en = shared._make_english_key("welcome", "Welcome to English Your Way.")
    key_flash_en = shared._make_english_key(
        "welcome", "Welcome to English Your Way.", "speech_metadata_flash_lite")
    assert key_legacy_en.tts_model_id == shared.TTS_MODEL_EN
    assert key_flash_en.tts_model_id == shared.TTS_MODEL_FLASH_LITE
    assert key_legacy_en.master_audio_id() != key_flash_en.master_audio_id()

    key_legacy_ja = shared._make_japanese_key("ポイント解説")
    key_flash_ja = shared._make_japanese_key("ポイント解説", "speech_metadata_flash_lite")
    assert key_legacy_ja.tts_model_id == shared.TTS_MODEL_JA
    assert key_flash_ja.tts_model_id == shared.TTS_MODEL_FLASH_LITE
    assert key_legacy_ja.master_audio_id() != key_flash_ja.master_audio_id()
    print("PASS: test_flash_lite_backend_uses_separate_master_key_and_does_not_touch_legacy_assets")


def test_ensure_functions_thread_tts_backend_to_generators():
    """ensure_fixed_english_segment/ensure_fixed_japanese_segment/
    ensure_key_phrase_english_componentが、受け取ったtts_backendを
    そのまま下位のgenerate_*関数へ転送することを確認する(実TTS呼び出し
    はmockする)。"""
    tmp_dir = "er006_output/_test_shared_narration_backend_tmp"
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    orig_store_dir, orig_audio_dir = store.STORE_DIR, store.AUDIO_DIR
    orig_manifest, orig_telemetry = store.MANIFEST_PATH, store.TELEMETRY_PATH
    store.STORE_DIR = f"{tmp_dir}/store"
    store.AUDIO_DIR = f"{tmp_dir}/store/audio"
    store.MANIFEST_PATH = f"{tmp_dir}/store/manifest.json"
    store.TELEMETRY_PATH = f"{tmp_dir}/store/reuse_telemetry.jsonl"

    captured = {}
    orig_en = voice01.generate_charon_english
    orig_ja = voice01.generate_charon_japanese
    import er003_v1_repro01_main_generate as repro01
    orig_kp = repro01.generate_key_phrase_component_verified

    def fake_en(text, out_path, **kwargs):
        captured["en_tts_backend"] = kwargs.get("tts_backend")
        _write_dummy_wav(out_path)
        return {"status": "OK"}

    def fake_ja(text, out_path, expected_substring, max_attempts=6, **kwargs):
        captured["ja_tts_backend"] = kwargs.get("tts_backend")
        _write_dummy_wav(out_path)
        return {"status": "OK"}

    def fake_kp(text, out_path, disfluency_qa=True, tts_backend="structured_separation"):
        captured["kp_tts_backend"] = tts_backend
        _write_dummy_wav(out_path)
        return {"status": "OK"}

    voice01.generate_charon_english = fake_en
    voice01.generate_charon_japanese = fake_ja
    repro01.generate_key_phrase_component_verified = fake_kp
    try:
        narration_dir = f"{tmp_dir}/b1b/narration"
        shared.ensure_fixed_english_segment("welcome", narration_dir, tts_backend="speech_metadata_flash_lite")
        shared.ensure_fixed_japanese_segment("point_explanation", narration_dir,
                                              tts_backend="speech_metadata_flash_lite")
        shared.ensure_key_phrase_english_component("test phrase", f"{narration_dir}/kp1_en.wav",
                                                     tts_backend="speech_metadata_flash_lite")
        assert captured["en_tts_backend"] == "speech_metadata_flash_lite"
        assert captured["ja_tts_backend"] == "speech_metadata_flash_lite"
        assert captured["kp_tts_backend"] == "speech_metadata_flash_lite"
    finally:
        voice01.generate_charon_english = orig_en
        voice01.generate_charon_japanese = orig_ja
        repro01.generate_key_phrase_component_verified = orig_kp
        store.STORE_DIR, store.AUDIO_DIR = orig_store_dir, orig_audio_dir
        store.MANIFEST_PATH, store.TELEMETRY_PATH = orig_manifest, orig_telemetry
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)
    print("PASS: test_ensure_functions_thread_tts_backend_to_generators")


def test_bl1_flash_lite_shell_uses_short_style_override_default_backend_unchanged():
    """TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-02(BL-1、
    修正3回目、2026-09-28、Opus L2所見): ensure_fixed_english_segment()が
    tts_backend="speech_metadata_flash_lite"の場合のみ、voice01.
    generate_charon_englishへstyle_prefix_override=
    FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]を渡すことを確認する(既定backendは
    style_prefix_override=None=既存挙動のまま、byte-identical)。"""
    import er033_tts_flash_lite_family_x_styles_01 as fl_styles
    tmp_dir = "er006_output/_test_shared_narration_bl1_tmp"
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    orig_store_dir, orig_audio_dir = store.STORE_DIR, store.AUDIO_DIR
    orig_manifest, orig_telemetry = store.MANIFEST_PATH, store.TELEMETRY_PATH
    store.STORE_DIR = f"{tmp_dir}/store"
    store.AUDIO_DIR = f"{tmp_dir}/store/audio"
    store.MANIFEST_PATH = f"{tmp_dir}/store/manifest.json"
    store.TELEMETRY_PATH = f"{tmp_dir}/store/reuse_telemetry.jsonl"

    captured = {}
    orig_en = voice01.generate_charon_english

    def fake_en(text, out_path, **kwargs):
        captured["style_prefix_override"] = kwargs.get("style_prefix_override")
        _write_dummy_wav(out_path)
        return {"status": "OK"}

    voice01.generate_charon_english = fake_en
    try:
        narration_dir = f"{tmp_dir}/b1b/narration"
        shared.ensure_fixed_english_segment("num_two", narration_dir, filename_suffix="_charon")
        assert captured["style_prefix_override"] is None, \
            f"既定backendはstyle_prefix_override=Noneのままのはず。実際={captured['style_prefix_override']!r}"
        captured.clear()
        # FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(W2、2026-09-29):
        # num_twoはChampion(candidate B)へ切り替わったため、
        # FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]ではなく
        # SHELL_CHAMPION_STYLE_BY_PHRASE_EN["num_two"]が渡されるはず。
        shared.ensure_fixed_english_segment(
            "num_two", narration_dir, filename_suffix="_charon", tts_backend="speech_metadata_flash_lite")
        assert captured["style_prefix_override"] == shared.SHELL_CHAMPION_STYLE_BY_PHRASE_EN["num_two"], \
            f"Flash-Lite backendはChampion styleを渡すはず。実際={captured['style_prefix_override']!r}"
        captured.clear()
        # welcomeは引き続きFAMILY_X_ROLE_STYLE_EN_FALLBACK[0](現行Master
        # 継続、Champion決定「welcome=A」)。
        shared.ensure_fixed_english_segment(
            "welcome", narration_dir, filename_suffix="_charon", tts_backend="speech_metadata_flash_lite")
        assert captured["style_prefix_override"] == fl_styles.FAMILY_X_ROLE_STYLE_EN_FALLBACK[0], \
            f"welcomeはFAMILY_X_ROLE_STYLE_EN_FALLBACK[0]のまま不変のはず。実際={captured['style_prefix_override']!r}"
    finally:
        voice01.generate_charon_english = orig_en
        store.STORE_DIR, store.AUDIO_DIR = orig_store_dir, orig_audio_dir
        store.MANIFEST_PATH, store.TELEMETRY_PATH = orig_manifest, orig_telemetry
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)
    print("PASS: test_bl1_flash_lite_shell_uses_short_style_override_default_backend_unchanged")


def test_bl1_style_instruction_version_bump_only_for_flash_lite_key():
    """BL-1是正: style override変更に伴い、Flash-Lite backend時のみ
    style_instruction_versionをbumpする(既定backendのkeyは"v1"のまま
    無変更=既存Structured Separation資産のcache維持)。JA keyは今回
    style自体を変更していないためversionもv1のまま(意図的、RESULT_PACKET
    参照)。"""
    # FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(W2、2026-09-29)によって
    # num_twoはChampion(candidate B)へ切り替わったため、_make_english_key
    # の引数にname="num_two"が必要になった(以前はtextのみでtts_backendの
    # 分岐のみ判定していた)。Championのversionは
    # SHELL_CHAMPION_STYLE_INSTRUCTION_VERSIONへ変わる(旧
    # SHELL_ENGLISH_FLASH_LITE_STYLE_INSTRUCTION_VERSIONはwelcome専用に
    # 縮小)。JA側point_explanationもChampion(candidate B)登録に伴い
    # versionをbumpするため、下のJA assertも合わせて更新する(BL-1時点の
    # 「JAはスコープ外」判断は本タスクでversion面のみ解消、style本体の
    # 実runtime適用は引き続きスコープ外=SHELL_CHAMPION_STYLE_JA_
    # POINT_EXPLANATION_Bのコメント参照)。
    key_legacy_en = shared._make_english_key("num_two", "Two.")
    key_flash_en = shared._make_english_key("num_two", "Two.", "speech_metadata_flash_lite")
    assert key_legacy_en.style_instruction_version == "v1"
    assert key_flash_en.style_instruction_version == shared.SHELL_CHAMPION_STYLE_INSTRUCTION_VERSION
    assert key_legacy_en.style_instruction_version != key_flash_en.style_instruction_version
    # welcomeは引き続き旧v2 versionのまま(Champion決定「welcome=A」=現行
    # Master継続、新規登録なし)。
    key_flash_welcome = shared._make_english_key(
        "welcome", "Welcome to English Your Way.", "speech_metadata_flash_lite")
    assert key_flash_welcome.style_instruction_version == shared.SHELL_ENGLISH_FLASH_LITE_STYLE_INSTRUCTION_VERSION
    # 既存Flash-Lite資産(旧style時代に生成済みのmaster、例:
    # master_audio_id=586a1ecd053b563c856dad20相当のnum_two等)はversion差分により
    # cache missとなり、新styleで再生成される(意図どおり)。
    key_flash_ja = shared._make_japanese_key("ポイント解説", "speech_metadata_flash_lite")
    assert key_flash_ja.style_instruction_version == shared.SHELL_CHAMPION_STYLE_INSTRUCTION_VERSION, \
        "point_explanationはChampion(candidate B)としてW2で新規登録するためversionをbumpする"
    print("PASS: test_bl1_style_instruction_version_bump_only_for_flash_lite_key")


def test_w2_champion_style_map_matches_all_shell_phrases_except_welcome():
    """FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(W2、2026-09-29):
    SHELL_CHAMPION_STYLE_BY_PHRASE_ENが、welcome以外のFIXED_ENGLISH_TEXTS
    全phraseをカバーし、welcomeは含まないことを確認する(er048登録
    スクリプトのkey計算とここのmapが常に一致しているという前提の
    regression guard)。"""
    non_welcome_names = set(shared.FIXED_ENGLISH_TEXTS) - {"welcome"}
    assert set(shared.SHELL_CHAMPION_STYLE_BY_PHRASE_EN) == non_welcome_names, (
        f"Champion style mapがFIXED_ENGLISH_TEXTS(welcome除く)と一致しない。"
        f"map={sorted(shared.SHELL_CHAMPION_STYLE_BY_PHRASE_EN)} "
        f"expected={sorted(non_welcome_names)}")
    assert "welcome" not in shared.SHELL_CHAMPION_STYLE_BY_PHRASE_EN
    for name in non_welcome_names:
        override = shared._resolve_shell_english_style_prefix_override(name, "speech_metadata_flash_lite")
        assert override == shared.SHELL_CHAMPION_STYLE_BY_PHRASE_EN[name]
        key = shared._make_english_key(name, shared.FIXED_ENGLISH_TEXTS[name], "speech_metadata_flash_lite")
        assert key.style_instruction_version == shared.SHELL_CHAMPION_STYLE_INSTRUCTION_VERSION
    # welcomeだけはFALLBACK[0]・旧versionのまま。
    assert shared._resolve_shell_english_style_prefix_override(
        "welcome", "speech_metadata_flash_lite") == "natural, clear, conversational"
    print("PASS: test_w2_champion_style_map_matches_all_shell_phrases_except_welcome")


if __name__ == "__main__":
    test_b1_and_a2_share_master_no_double_tts()
    test_flash_lite_backend_uses_separate_master_key_and_does_not_touch_legacy_assets()
    test_ensure_functions_thread_tts_backend_to_generators()
    test_bl1_flash_lite_shell_uses_short_style_override_default_backend_unchanged()
    test_bl1_style_instruction_version_bump_only_for_flash_lite_key()
    test_w2_champion_style_map_matches_all_shell_phrases_except_welcome()
    print("ALL TESTS PASSED")
