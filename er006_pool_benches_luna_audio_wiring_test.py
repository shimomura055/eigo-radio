# ============================================================
# er006_pool_benches_luna_audio_wiring_test.py
# ER-006-POOL-BENCHES-LUNA-AUDIO-VALIDATION-01: Audio Validation配線の確認
# ============================================================
# 実際のTTS/ASR呼び出しは行わない(新規API costゼロ)。(1) 対象ファイルが
# 新validatorをimportし、旧方式(safety.validate_asr_match/素のsubstring_ok
# のみ)へ後退していないことを静的に確認し、(2) evaluate_attempt()を
# 疑似的なASR応答列で駆動し、実際の生成ループが辿るのと同じ分岐
# (即PASS/guardrail打ち切り/retry継続)を再現できることを確認する。
from __future__ import annotations

import re

import er006_preprod_hardening_01_validation as audio_validation

WIRED_FILES = [
    "er003_v1_sing01_voice01_generate.py",
    "er003_v1_sing01_news_tail_fix.py",
    "er003_v1_sing01_point_headings_aoede.py",
    "er003_v1_repro01_main_generate.py",
    "er003_v1_crosslevel_audio_02_common.py",
]


def run():
    failures = []

    print("=== 配線確認: 対象ファイルがaudio_validationをimportしている ===")
    for filename in WIRED_FILES:
        text = open(filename, encoding="utf-8").read()
        ok = "import er006_preprod_hardening_01_validation as audio_validation" in text
        status = "OK" if ok else "FAIL"
        print(f"[{status}] {filename}")
        if not ok:
            failures.append(f"{filename}: audio_validationがimportされていない")

    print("\n=== 配線確認: evaluate_attempt()が実際に呼ばれている ===")
    for filename in WIRED_FILES:
        text = open(filename, encoding="utf-8").read()
        n_calls = len(re.findall(r"audio_validation\.evaluate_attempt\(", text))
        ok = n_calls >= 1
        status = "OK" if ok else "FAIL"
        print(f"[{status}] {filename}: evaluate_attempt呼び出し {n_calls}件")
        if not ok:
            failures.append(f"{filename}: evaluate_attempt()が呼ばれていない")

    print("\n=== 配線確認: ASR_VALIDATION_UNCERTAINという新statusを返せる ===")
    for filename in WIRED_FILES:
        text = open(filename, encoding="utf-8").read()
        ok = "ASR_VALIDATION_UNCERTAIN" in text
        status = "OK" if ok else "FAIL"
        print(f"[{status}] {filename}")
        if not ok:
            failures.append(f"{filename}: ASR_VALIDATION_UNCERTAIN分岐が無い")

    print("\n=== 動作確認: evaluate_attempt()を疑似ASR応答列で駆動(実API呼び出しなし) ===")
    # ケース1: 1回目でNORMALIZED_MATCH → 即PASS
    history = []
    verified, stop, cls = audio_validation.evaluate_attempt(
        "hostile architecture", "Hostile architecture.", history)
    ok = verified and not stop and cls.classification == "NORMALIZED_MATCH"
    print(f"[{'OK' if ok else 'FAIL'}] ケース1(即PASS): verified={verified} stop={stop} cls={cls.classification}")
    if not ok:
        failures.append("ケース1(即PASS)が期待通りでない")

    # ケース2: 同一の固有名詞差(entity_like)が3回連続 → guardrailで打ち切り
    history2 = []
    canon = "Malmö’s Triangeln station opened in 2010."
    asr_same = "Malmo's Triangle station opened in 2010."
    results = []
    for i in range(4):
        verified, stop, cls = audio_validation.evaluate_attempt(canon, asr_same, history2)
        results.append((verified, stop, cls.classification))
        if verified or stop:
            break
    ok = (not results[-1][0]) and results[-1][1] and results[-1][2] == "ASR_VALIDATION_UNCERTAIN"
    ok = ok and len(results) <= 3  # 3回目までに打ち切られること
    print(f"[{'OK' if ok else 'FAIL'}] ケース2(guardrail打ち切り): {results}")
    if not ok:
        failures.append("ケース2(guardrail打ち切り)が期待通りでない")

    # ケース3: 内容が毎回違う数字誤り → 打ち切らずretryを継続する(TRUE_CONTENT_MISMATCHは対象外)
    history3 = []
    canon3 = "The study followed 2 groups."
    asr_variants = ["The study followed 3 groups.", "The study followed 4 groups.", "The study followed 5 groups."]
    results3 = []
    for asr in asr_variants:
        verified, stop, cls = audio_validation.evaluate_attempt(canon3, asr, history3)
        results3.append((verified, stop, cls.classification))
    ok = all(not v and not s and c == "TRUE_CONTENT_MISMATCH" for v, s, c in results3)
    print(f"[{'OK' if ok else 'FAIL'}] ケース3(内容誤りはguardrailで打ち切らずretry継続): {results3}")
    if not ok:
        failures.append("ケース3(内容誤りのretry継続)が期待通りでない")

    if failures:
        raise AssertionError(f"{len(failures)}件の配線確認が失敗した:\n" + "\n".join(f"  - {f}" for f in failures))
    print(f"\nOK: 全チェックPASS(新規API呼び出しなし)")


if __name__ == "__main__":
    run()
