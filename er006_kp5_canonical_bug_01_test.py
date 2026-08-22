# ============================================================
# er006_kp5_canonical_bug_01_test.py
# ER-006-KP5-CANONICAL-BUG-01: canonical placeholder混入バグの
# regression test。
# ============================================================
# 実行方法: .venv/Scripts/python.exe er006_kp5_canonical_bug_01_test.py

from __future__ import annotations

import er003_audio_tts_asr_safety as safety
import er003_v1_n3_01_tts_generate as tts_gen
import er003_v1_sing01_voice01_generate as voice01


def test_detect_finds_mid_string_ellipsis_and_wave_dash():
    # 実際にPublic Benches B1 kp5_jaで発生した値そのもの。
    r = safety.detect_gloss_placeholder_notation("〜を…と結びつける")
    assert r["has_placeholder"] is True
    assert "〜" in r["found_chars"]
    assert "…" in r["found_chars"]
    print("PASS: test_detect_finds_mid_string_ellipsis_and_wave_dash")


def test_detect_finds_fullwidth_tilde_variant():
    # U+FF5E(全角チルダ)とU+301C(波ダッシュ)は別のUnicode文字だが、
    # どちらも同じ問題を起こしうるため両方検出できること。
    r = safety.detect_gloss_placeholder_notation("～によって説明される")
    assert r["has_placeholder"] is True
    assert "～" in r["found_chars"]
    print("PASS: test_detect_finds_fullwidth_tilde_variant")


def test_detect_passes_normal_gloss():
    # 実際にPublic Benches B1 kp1-4で使われている、placeholderを含まない
    # 自然なgloss。誤検出しないこと。
    for gloss in ("人を排除する都市設計", "大規模な実証研究",
                  "玄関先のような交流の場になる", "発注された仕様より傾斜が急で",
                  "その場を立ち去る"):
        r = safety.detect_gloss_placeholder_notation(gloss)
        assert r["has_placeholder"] is False, f"誤検出: {gloss!r}"
    print("PASS: test_detect_passes_normal_gloss")


def test_tts_safe_ja_strips_both_tilde_variants_when_leading():
    # 先頭位置のtilde placeholderは、どちらの文字種でも安全にlstrip
    # できる(文法が壊れない、ER-003-B1-REDESIGN-AUDIO-01で確立済みの
    # 「先頭のみ」という前提はそのまま維持する)。
    assert tts_gen.tts_safe_ja("～によって説明される") == "によって説明される"
    assert tts_gen.tts_safe_ja("〜によって説明される") == "によって説明される"
    # 先頭以外の「〜」「…」はlstrip対象外(mid-stringは機械的に消さない)。
    stripped = tts_gen.tts_safe_ja("〜を…と結びつける")
    assert stripped == "を…と結びつける", stripped
    print("PASS: test_tts_safe_ja_strips_both_tilde_variants_when_leading")


def test_generate_charon_japanese_gate_blocks_before_tts_call():
    # B1経路: placeholderが残ったままgenerate_charon_japaneseへ渡らない
    # ことを、実際にmonkeypatchしてTTS呼び出しがゼロ回であることで確認する。
    calls = {"n": 0}
    orig = voice01.generate_charon_japanese

    def fake_generate_charon_japanese(*args, **kwargs):
        calls["n"] += 1
        return {"status": "OK"}

    voice01.generate_charon_japanese = fake_generate_charon_japanese
    try:
        r = tts_gen.generate_charon_japanese_with_reading_safety(
            "〜を…と結びつける", "dummy_out.wav", "結びつける")
        assert r["status"] == "STOPPED", r
        assert calls["n"] == 0, f"TTSが{calls['n']}回呼ばれた(0回であるべき)"
        assert r["canonical_text"] == "〜を…と結びつける"
    finally:
        voice01.generate_charon_japanese = orig
    print("PASS: test_generate_charon_japanese_gate_blocks_before_tts_call")


def test_generate_charon_japanese_gate_allows_normal_gloss_through():
    # 正常なglossはゲートを通過し、通常通りTTS呼び出しに到達すること
    # (実発話textと一致する: ゲートを通った場合のtts_input/canonical_text
    # は互いに矛盾しない)。
    calls = {"n": 0, "text": None}
    orig = voice01.generate_charon_japanese

    def fake_generate_charon_japanese(text, out_path, expected_substring, max_attempts=6):
        calls["n"] += 1
        calls["text"] = text
        return {"status": "OK"}

    voice01.generate_charon_japanese = fake_generate_charon_japanese
    try:
        r = tts_gen.generate_charon_japanese_with_reading_safety(
            "その場を立ち去る", "dummy_out.wav", "立ち去る")
        assert r["status"] == "OK", r
        assert calls["n"] == 1
        assert calls["text"] == "その場を立ち去る"
        assert r["canonical_text"] == "その場を立ち去る"
    finally:
        voice01.generate_charon_japanese = orig
    print("PASS: test_generate_charon_japanese_gate_allows_normal_gloss_through")


def test_generate_charon_japanese_gate_allows_leading_tilde_after_strip():
    # 先頭のみのplaceholder("〜によって"型)は、strip後にplaceholderが
    # 残らないため、ゲートで止めずに正常にTTS呼び出しへ到達すること。
    calls = {"n": 0, "text": None}
    orig = voice01.generate_charon_japanese

    def fake_generate_charon_japanese(text, out_path, expected_substring, max_attempts=6):
        calls["n"] += 1
        calls["text"] = text
        return {"status": "OK"}

    voice01.generate_charon_japanese = fake_generate_charon_japanese
    try:
        r = tts_gen.generate_charon_japanese_with_reading_safety(
            "〜によって説明される", "dummy_out.wav", "説明される")
        assert r["status"] == "OK", r
        assert calls["n"] == 1
        assert calls["text"] == "によって説明される"
    finally:
        voice01.generate_charon_japanese = orig
    print("PASS: test_generate_charon_japanese_gate_allows_leading_tilde_after_strip")


if __name__ == "__main__":
    test_detect_finds_mid_string_ellipsis_and_wave_dash()
    test_detect_finds_fullwidth_tilde_variant()
    test_detect_passes_normal_gloss()
    test_tts_safe_ja_strips_both_tilde_variants_when_leading()
    test_generate_charon_japanese_gate_blocks_before_tts_call()
    test_generate_charon_japanese_gate_allows_normal_gloss_through()
    test_generate_charon_japanese_gate_allows_leading_tilde_after_strip()
    print("ALL TESTS PASSED")
