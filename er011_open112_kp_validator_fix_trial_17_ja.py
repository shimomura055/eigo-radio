# ============================================================
# er011_open112_kp_validator_fix_trial_17_ja.py
# 管理ID: OPEN-112-TREND-THEME2-B-KEYPHRASE-VALIDATOR-FIX-TRIAL-17
# Track A: JA数字ゲート一般化(隔離Trial、Production配線禁止)
# ============================================================
# 背景(Opus診断 OPEN-112-...-STOP-DIAGNOSTIC-15の結論):
# er007_ja_asr_validator_01.normalize_ja()が呼ぶ
# er003_audio_tts_asr_safety.normalize_kanji_counter_numerals_ja()は、
# 助数詞「つ」の直前の単独漢数字(一〜九)のみを算用数字へ揃える
# (_KANJI_COUNTER_RE = r"[一二三四五六七八九](?=つ)")。このため
# kp3_ja_charon(canonical「中央値は約2泊」/ASR「中央値は約二泊。」)の
# ような「泊」等、「つ」以外の助数詞直前の漢数字は変換されず、
# protected_check_ja()の数字保護ゲートが「canonicalに無い数字」として
# 誤ってTRUE_CONTENT_MISMATCH(即retry対象)に分類していた。
#
# 本Trialの候補ロジック(案A、ユーザー正式決定に基づく):
# 「泊/日/人/回/件/年/時間/か月/週/歳」という**閉じた助数詞リスト**の
# 直前に来る単独漢数字(一〜九)だけを追加で算用数字へ正規化する
# (一般の漢数字変換[案A']は採らない、既存の「つ」限定方針と同じ設計
# 思想の単純な拡張)。
#
# 実装方針: Production関数(er007_ja_asr_validator_01.classify_ja_asr_match、
# er003_audio_tts_asr_safety.normalize_kanji_counter_numerals_ja等)は
# 一切変更しない。本モジュールは、閉じた助数詞リストによる追加正規化を
# **入力テキストの前処理**として適用したうえで、既存の
# er007.classify_ja_asr_match()/er003.validate_japanese_short_segment_match()
# へそのまま委譲する(ラップするだけで内部ロジックは複製しない)。
# ============================================================
from __future__ import annotations

import re

import er003_audio_tts_asr_safety as safety
import er007_ja_asr_validator_01 as ja_validator

# 閉じた助数詞リスト(ユーザー指示、案A)。「回」の重複は削除済み。
CLOSED_COUNTERS_JA: tuple[str, ...] = (
    "泊", "日", "人", "回", "件", "年", "時間", "か月", "週", "歳",
)

_KANJI_DIGIT_MAP = {
    "一": "1", "二": "2", "三": "3", "四": "4", "五": "5",
    "六": "6", "七": "7", "八": "8", "九": "9",
}

# 単独漢数字(一〜九)の直前文字が、上記閉じた助数詞リストのいずれかと
# 完全一致する場合のみ変換する(既存の「つ」限定パターンと同じ設計、
# 一般の漢数字[十/百/二十/二回のような複合語]は対象外のまま)。
_CLOSED_COUNTER_KANJI_RE = re.compile(
    r"[一二三四五六七八九](?=(?:" + "|".join(CLOSED_COUNTERS_JA) + r"))"
)


def normalize_closed_counter_kanji_ja(text: str) -> str:
    """助数詞「つ」の既存正規化(Production、変更なし)に加えて、
    CLOSED_COUNTERS_JAの直前に来る単独漢数字だけを算用数字へ変換する。
    "二十"のような複合漢数字、"京三"/"二宮"のような単独漢数字が閉じた
    助数詞リストの語を直後に伴わない固有名詞は対象外のまま変更しない。"""
    if not text:
        return text
    # 既存Production関数(「つ」限定)をそのまま再利用(重複実装しない)。
    text = safety.normalize_kanji_counter_numerals_ja(text)
    return _CLOSED_COUNTER_KANJI_RE.sub(lambda m: _KANJI_DIGIT_MAP[m.group(0)], text)


def classify_ja_asr_match_track_a(canonical_text: str, asr_text: str | None,
                                   tts_failure_threshold: float = 0.4):
    """Track A候補ロジック。入力テキストへ閉じた助数詞リストの追加正規化
    を前処理として適用したうえで、Production関数
    er007_ja_asr_validator_01.classify_ja_asr_match()へそのまま委譲する
    (Production関数自体は無変更・無改造)。"""
    c_pre = normalize_closed_counter_kanji_ja(canonical_text) if canonical_text else canonical_text
    a_pre = normalize_closed_counter_kanji_ja(asr_text) if asr_text else asr_text
    return ja_validator.classify_ja_asr_match(c_pre, a_pre, tts_failure_threshold=tts_failure_threshold)


def validate_japanese_short_segment_match_track_a(canonical_text: str, asr_text, asr_error: str = None) -> dict:
    """同じ前処理を、短いsegment専用のProduction関数
    er003_audio_tts_asr_safety.validate_japanese_short_segment_match()
    へも適用する版(そちらもClosed counter listの恩恵を受けられるかを
    確認するため、instructions(d)の回帰対象に含める)。"""
    c_pre = normalize_closed_counter_kanji_ja(canonical_text) if canonical_text else canonical_text
    a_pre = normalize_closed_counter_kanji_ja(asr_text) if asr_text else asr_text
    return safety.validate_japanese_short_segment_match(c_pre, a_pre, asr_error=asr_error)


if __name__ == "__main__":
    import json
    import os

    results = {"new_fixtures": {}, "regression": {}}
    failures = []

    # ------------------------------------------------------------
    # (a) Trial-13実ケース: 期待PASS(NORMALIZED_MATCH等)
    # ------------------------------------------------------------
    print("=== (a) Trial-13実ケース(kp3_ja_charon) ===")
    canonical_a = "中央値は約2泊"
    asr_a = "中央値は約二泊。"
    r_a = classify_ja_asr_match_track_a(canonical_a, asr_a)
    ok_a = r_a.should_pass is True
    print(f"[{'OK' if ok_a else 'FAIL'}] canonical={canonical_a!r} asr={asr_a!r} "
          f"-> classification={r_a.classification} should_pass={r_a.should_pass} reason={r_a.reason}")
    results["new_fixtures"]["a_trial13_kp3_ja"] = {
        "canonical": canonical_a, "asr": asr_a, "classification": r_a.classification,
        "should_pass": r_a.should_pass, "expected_pass": True, "ok": ok_a,
    }
    if not ok_a:
        failures.append("a_trial13_kp3_ja")

    # ------------------------------------------------------------
    # (b) 既存「2つ/二つ」パターンが引き続きPASSすること
    # ------------------------------------------------------------
    print("\n=== (b) 既存「つ」パターン回帰 ===")
    canonical_b = "では、この二つの動きについて、英語のまとめを聞いてみましょう。"
    asr_b = "では、この2つの動きについて、英語のまとめを聞いてみましょう。"
    r_b = classify_ja_asr_match_track_a(canonical_b, asr_b)
    ok_b = r_b.should_pass is True
    print(f"[{'OK' if ok_b else 'FAIL'}] -> classification={r_b.classification} should_pass={r_b.should_pass}")
    results["new_fixtures"]["b_existing_tsu_pattern"] = {
        "canonical": canonical_b, "asr": asr_b, "classification": r_b.classification,
        "should_pass": r_b.should_pass, "expected_pass": True, "ok": ok_b,
    }
    if not ok_b:
        failures.append("b_existing_tsu_pattern")

    # ------------------------------------------------------------
    # (c) 陰性対照
    # ------------------------------------------------------------
    print("\n=== (c) 陰性対照(FAILのままであるべき) ===")
    negative_cases = [
        ("c1_different_quantity", "中央値は約2泊", "中央値は約三泊。"),
        ("c2_digit_dropped", "2泊", "泊"),
        ("c3_proper_noun_kyouzou", "京三さんに聞いた話です", "京三さんに聞いた話です"),  # positive control (unaffected)
        ("c4_proper_noun_ninomiya_not_miscoverted", "二宮さんに聞いた話です。", "二宮さんに聞いた話です"),
        ("c5_different_counter_kai_vs_tsu", "この点については二回説明しました。", "この点については2つ説明しました。"),
        ("c6_nijuu_not_affected", "参加者は二十人ほど集まりました。", "参加者は2人ほど集まりました。"),
    ]
    for name, canonical_c, asr_c in negative_cases:
        r_c = classify_ja_asr_match_track_a(canonical_c, asr_c)
        if name in ("c3_proper_noun_kyouzou", "c4_proper_noun_ninomiya_not_miscoverted"):
            # 「二宮」の「二」は直後が助数詞ではない("宮")ため無変換のまま
            # (positive control: 句読点差のみで意味は完全一致、誤って
            # 数字が書き換わっていないことの確認、PASSが正しい期待値)。
            # 完全一致のpositive control(誤って書き換わっていないことの確認)
            expected_pass = True
            ok_c = r_c.should_pass is True
        else:
            expected_pass = False
            ok_c = r_c.should_pass is False
        print(f"[{'OK' if ok_c else 'FAIL'}] {name}: canonical={canonical_c!r} asr={asr_c!r} "
              f"-> classification={r_c.classification} should_pass={r_c.should_pass}")
        results["new_fixtures"][name] = {
            "canonical": canonical_c, "asr": asr_c, "classification": r_c.classification,
            "should_pass": r_c.should_pass, "expected_pass": expected_pass, "ok": ok_c,
        }
        if not ok_c:
            failures.append(name)

    # 固有名詞の変換自体が起きていないことを、正規化関数レベルでも直接確認
    print("\n--- 固有名詞の閉じた助数詞誤変換防止(正規化関数レベル) ---")
    entity_checks = [
        ("京三", "京三"),   # 「三」の直後に助数詞が続かない -> 無変換
        ("二宮", "二宮"),   # 「二」の直後が「宮」(助数詞ではない) -> 無変換
    ]
    for raw, expected in entity_checks:
        got = normalize_closed_counter_kanji_ja(raw)
        ok = got == expected
        print(f"[{'OK' if ok else 'FAIL'}] normalize_closed_counter_kanji_ja({raw!r}) = {got!r} (期待 {expected!r})")
        results["new_fixtures"][f"entity_norm_{raw}"] = {"input": raw, "output": got, "expected": expected, "ok": ok}
        if not ok:
            failures.append(f"entity_norm_{raw}")

    # 既知の生産リスク: 「日」を閉じたリストに含めるため、"四日市"/"五日市"の
    # ような実在地名(漢数字+日)も対称的に変換される。symmetricに適用され
    # る限り数字集合の比較自体は崩れないことを確認しつつ、Production採用時の
    # 既知リスクとして記録する(FAILにはしない、記録目的)。
    print("\n--- 既知リスク記録: 地名『四日市』(漢数字+『日』) ---")
    risk_input = "四日市に住んでいます。"
    risk_output = normalize_closed_counter_kanji_ja(risk_input)
    print(f"normalize_closed_counter_kanji_ja({risk_input!r}) = {risk_output!r} "
          f"(地名の一部が数字として変換される既知のリスク、Production採用時は要検討)")
    results["new_fixtures"]["known_risk_yokkaichi"] = {"input": risk_input, "output": risk_output}

    # 実際に回帰で見つかったkakasi依存の構造的リスク(下記(d)の全件回帰で
    # 判明): 「日」をClosed counter listへ含めると、"三日坊主"(慣用句、
    # 正しい読みは不規則な"mikkabouzu")のようなcanonicalが、"3日坊主"へ
    # 変換されてしまい、kakasiが数字文字"3"を読み上げず文字のまま扱う
    # ため(_kakasi_reading("3")は"mikka"にならず"3"のまま)、ASRの全文
    # ひらがな書き起こし"みっかぼうず"との読み一致(whole_text_reading_
    # equal機構)が壊れる。これは実際に(d)の全件回帰で検出された。
    print("\n--- 判明したリスク: 「日」のkakasi不規則読み(三日坊主) ---")
    r_risk = classify_ja_asr_match_track_a("三日坊主", "みっかぼうず")
    baseline_risk = ja_validator.classify_ja_asr_match("三日坊主", "みっかぼうず")
    print(f"baseline(Production, 無変更)={baseline_risk.classification}/{baseline_risk.should_pass}")
    print(f"candidate(Track A, 日を含む閉じたリスト)={r_risk.classification}/{r_risk.should_pass}")
    results["new_fixtures"]["known_regression_mikkabouzu"] = {
        "canonical": "三日坊主", "asr": "みっかぼうず",
        "baseline_classification": baseline_risk.classification, "baseline_should_pass": baseline_risk.should_pass,
        "candidate_classification": r_risk.classification, "candidate_should_pass": r_risk.should_pass,
        "note": "「日」をClosed counter listに含めることで発生する実regression(詳細はREPORT参照)",
    }

    # ------------------------------------------------------------
    # (d) 既存JA fixtureの全件回帰(er007_ja_asr_validator_01_test.py +
    #     er003_test_audio_tts_asr_safety.py)
    # ------------------------------------------------------------
    print("\n=== (d) 既存fixture全件回帰 ===")
    import er007_ja_asr_validator_01_test as er007_test

    # コスト安全: Reading Resolver(LLM呼び出し)は本Trialでは一切呼ばない
    # (絶対禁止: 追加の音声/LLM課金なし)。既存comment(モジュール定数として
    # 公開されている、ER-011-NO18-...-WIRING-08)の通り、test目的での明示的
    # 無効化として使う。baseline/candidate双方に同じ設定を適用するため、
    # Track Aロジックの差だけを見た比較になる。
    ja_validator.FEATURE_FLAG_A2_READING_RESOLVER_ENABLED = False

    all_fixture_groups = [
        ("POSITIVE_FIXTURES", er007_test.POSITIVE_FIXTURES),
        ("NEGATIVE_FIXTURES", er007_test.NEGATIVE_FIXTURES),
        ("ENTITY_LIKE_FIXTURES", er007_test.ENTITY_LIKE_FIXTURES),
        ("PHONETIC_UNCERTAIN_FIXTURES", er007_test.PHONETIC_UNCERTAIN_FIXTURES),
        ("WHOLE_TEXT_SCRIPT_MISMATCH_FIXTURES", er007_test.WHOLE_TEXT_SCRIPT_MISMATCH_FIXTURES),
        ("WHOLE_TEXT_SCRIPT_MISMATCH_NEGATIVE_FIXTURES", er007_test.WHOLE_TEXT_SCRIPT_MISMATCH_NEGATIVE_FIXTURES),
        ("KNOWN_TRADEOFF_FIXTURES", er007_test.KNOWN_TRADEOFF_FIXTURES),
        ("READING_RESOLVER_CORRECTLY_RESOLVES_FIXTURES", er007_test.READING_RESOLVER_CORRECTLY_RESOLVES_FIXTURES),
    ]
    regression_diff_count = 0
    regression_total = 0
    for group_name, fixtures in all_fixture_groups:
        group_results = []
        for fx in fixtures:
            baseline = ja_validator.classify_ja_asr_match(fx["canonical"], fx["asr"])
            candidate = classify_ja_asr_match_track_a(fx["canonical"], fx["asr"])
            regression_total += 1
            changed = (baseline.classification != candidate.classification
                       or baseline.should_pass != candidate.should_pass)
            if changed:
                regression_diff_count += 1
            status = "SAME" if not changed else "CHANGED"
            print(f"[{status}] [{group_name}] {fx['name']}: "
                  f"baseline={baseline.classification}/{baseline.should_pass} "
                  f"candidate={candidate.classification}/{candidate.should_pass}")
            group_results.append({
                "name": fx["name"], "baseline_classification": baseline.classification,
                "baseline_should_pass": baseline.should_pass,
                "candidate_classification": candidate.classification,
                "candidate_should_pass": candidate.should_pass, "changed": changed,
            })
        results["regression"][group_name] = group_results

    # er003_test_audio_tts_asr_safety.pyのJA短seg fixture(kanji counter系のみ抜粋、
    # クラス内定義のためテキストのみここへ直接記載)も同じロジック経由で回帰する。
    print("\n--- er003 短seg fixture(validate_japanese_short_segment_match経由) ---")
    er003_short_seg_fixtures = [
        {"name": "kanji_counter_matches_digit_counter(つ)", "canonical": "二つの動き", "asr": "2つの動き"},
        {"name": "kanji_counter_quantity_difference_still_fails(つ)", "canonical": "二つの動き", "asr": "3つの動き"},
        {"name": "naikouka_vs_naikouka_homophone_kanji", "canonical": "内向化問題", "asr": "内効果問題"},
        {"name": "exact_orthographic_match_still_works", "canonical": "外在化問題", "asr": "外在化問題"},
    ]
    for fx in er003_short_seg_fixtures:
        baseline = safety.validate_japanese_short_segment_match(fx["canonical"], fx["asr"])
        candidate = validate_japanese_short_segment_match_track_a(fx["canonical"], fx["asr"])
        regression_total += 1
        changed = baseline["verdict"] != candidate["verdict"] or baseline["passed"] != candidate["passed"]
        if changed:
            regression_diff_count += 1
        status = "SAME" if not changed else "CHANGED"
        print(f"[{status}] [er003_short_seg] {fx['name']}: "
              f"baseline={baseline['verdict']}/{baseline['passed']} candidate={candidate['verdict']}/{candidate['passed']}")
        results["regression"].setdefault("er003_short_seg_fixtures", []).append({
            "name": fx["name"], "baseline_verdict": baseline["verdict"], "baseline_passed": baseline["passed"],
            "candidate_verdict": candidate["verdict"], "candidate_passed": candidate["passed"], "changed": changed,
        })

    print(f"\n=== まとめ ===")
    print(f"新規fixture(a-d一部): {len(failures)}件が期待通りでなかった: {failures}")
    print(f"既存fixture回帰: 全{regression_total}件中、判定が変わったもの={regression_diff_count}件")

    results["summary"] = {
        "new_fixture_failures": failures,
        "regression_total": regression_total,
        "regression_changed_count": regression_diff_count,
    }

    out_dir = "er011_output/open112_kp_validator_fix_trial_17"
    os.makedirs(out_dir, exist_ok=True)
    out_path = f"{out_dir}/track_a_ja_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nwrote {out_path}")
