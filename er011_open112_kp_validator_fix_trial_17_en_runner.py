# ============================================================
# er011_open112_kp_validator_fix_trial_17_en_runner.py
# 管理ID: OPEN-112-TREND-THEME2-B-KEYPHRASE-VALIDATOR-FIX-TRIAL-17
# Track B: 新規fixture(a-c)+既存fixture全件回帰(d)の実行スクリプト。
# Production配線なし、新規TTS/ASR/LLM呼び出しなし(ローカル判定のみ)。
# ============================================================
from __future__ import annotations

import json
import os

import er006_preprod_hardening_01_validation as validation
import er006_preprod_hardening_01_validation_test as v_test
import er008_asr_variant_hardening_15_homophone_en_test as hp_test
import er011_no18_b1_connected_speech_trial_07 as cs_trial
import er011_open112_kp_validator_fix_trial_17_en as trial_b

results = {"new_fixtures": {}, "regression": {}}
new_fixture_failures = []

# ------------------------------------------------------------
# (a) Trial-13実ケース: 期待PASS(HOMOPHONE_MATCH系、ログ記録)
# ------------------------------------------------------------
print("=== (a) Trial-13実ケース(kp4_en) ===")
CANONICAL_A = "point to"
ASR_A = "Point two."
for approach_name, fn in (("approach1", trial_b.classify_asr_match_track_b_approach1),
                           ("approach2", trial_b.classify_asr_match_track_b_approach2)):
    r, rescues = fn(CANONICAL_A, ASR_A)
    ok = r.should_pass is True and r.classification == trial_b.HOMOPHONE_NUMBER_EXCEPTION_CLASSIFICATION
    print(f"[{'OK' if ok else 'FAIL'}] {approach_name}: canonical={CANONICAL_A!r} asr={ASR_A!r} "
          f"-> classification={r.classification} should_pass={r.should_pass} rescues={rescues}")
    results["new_fixtures"][f"a_trial13_kp4_en_{approach_name}"] = {
        "canonical": CANONICAL_A, "asr": ASR_A, "classification": r.classification,
        "should_pass": r.should_pass, "rescues": rescues, "ok": ok,
    }
    if not ok:
        new_fixture_failures.append(f"a_trial13_kp4_en_{approach_name}")

# ------------------------------------------------------------
# (b) 他の同音対
# ------------------------------------------------------------
print("\n=== (b) 他の同音対(期待PASS) ===")
# "won the game"/"one the game"は、"one"がProduction側の単独cardinal除外
# (tts_safe number変換で"one"は単独では数字化しない、_convert_cardinal_words
# 参照)によりそもそも数字ゲートへ到達せず、既存のhomophone_candidate機構
# (wait/weight等と同じ経路)が既にASR_VALIDATION_UNCERTAIN(Cascade対象、
# should_pass=Falseだがretryはしない)として捕捉済みであることを確認する
# ためのconfirmatory fixture(Track Bのgapケースではない、期待値もその通り)。
positive_pairs = [
    ("b1_for_you_four_you", "for you", "four you", True, "TRUE_CONTENT_MISMATCH"),
    ("b2_won_the_game_one_the_game", "won the game", "one the game", False, "ASR_VALIDATION_UNCERTAIN"),
]
for name, canonical_b, asr_b, expect_track_b_pass, expected_baseline_classification in positive_pairs:
    baseline = validation.classify_asr_match(canonical_b, asr_b)
    for approach_name, fn in (("approach1", trial_b.classify_asr_match_track_b_approach1),
                               ("approach2", trial_b.classify_asr_match_track_b_approach2)):
        r, rescues = fn(canonical_b, asr_b)
        if expect_track_b_pass:
            ok = r.should_pass is True
        else:
            # Track Bのgapケースではなく、既存機構が既に処理済みであることの
            # 確認(Track Bのrescueは働かない=候補ロジックの追加自体は不要)。
            ok = (baseline.classification == expected_baseline_classification
                  and r.classification == baseline.classification and not rescues)
        print(f"[{'OK' if ok else 'FAIL'}] {name}/{approach_name}: canonical={canonical_b!r} asr={asr_b!r} "
              f"baseline={baseline.classification}/{baseline.should_pass} "
              f"-> candidate={r.classification}/{r.should_pass} rescues={rescues}")
        results["new_fixtures"][f"{name}_{approach_name}"] = {
            "canonical": canonical_b, "asr": asr_b,
            "baseline_classification": baseline.classification, "baseline_should_pass": baseline.should_pass,
            "candidate_classification": r.classification, "candidate_should_pass": r.should_pass,
            "rescues": rescues, "ok": ok,
        }
        if not ok:
            new_fixture_failures.append(f"{name}_{approach_name}")

# ------------------------------------------------------------
# (c) 陰性対照(FAILのままであるべき)
# ------------------------------------------------------------
print("\n=== (c) 陰性対照(期待FAIL、should_pass=False のまま) ===")
negative_cases = [
    ("c1_point_to_point_three", "point to", "point three"),
    ("c2_two_nights_three_nights", "two nights", "three nights"),
    ("c3_canonical_has_number_asr_different_number", "The study followed 2 groups of participants.",
     "The study followed 3 groups of participants."),
    ("c4_digit_replaced_by_unrelated_nonhomophone_word", "the answer was 9", "the answer was mine"),
    ("c5_similar_but_not_homophone_numbers", "thirteen people attended", "thirty people attended"),
]
for name, canonical_c, asr_c in negative_cases:
    for approach_name, fn in (("approach1", trial_b.classify_asr_match_track_b_approach1),
                               ("approach2", trial_b.classify_asr_match_track_b_approach2)):
        r, rescues = fn(canonical_c, asr_c)
        ok = r.should_pass is False
        print(f"[{'OK' if ok else 'FAIL'}] {name}/{approach_name}: canonical={canonical_c!r} asr={asr_c!r} "
              f"-> classification={r.classification} should_pass={r.should_pass} rescues={rescues}")
        results["new_fixtures"][f"{name}_{approach_name}"] = {
            "canonical": canonical_c, "asr": asr_c, "classification": r.classification,
            "should_pass": r.should_pass, "rescues": rescues, "ok": ok,
        }
        if not ok:
            new_fixture_failures.append(f"{name}_{approach_name}")

# ------------------------------------------------------------
# Approach1 vs Approach2 差異検証用ケース: 同じテキスト内に複合基数
# ("twenty eight"->2:1圧縮)が別の場所にあると、Approach1(ローカルのみの
# index参照)はindexズレを起こし、生語の逆引きを誤る(本ケースでは
# たまたま安全側=非rescueへ倒れるが、それは設計上の保証ではなく偶然で
# あることをlocated/rawの実際の中身で示す)。Approach2(グローバルな
# alignment_safe要求)は、この種のテキスト全体では最初から機構的に
# rescueを試みない(原理的に安全)。
# ------------------------------------------------------------
print("\n=== Approach1/Approach2差異検証(複合基数を含む長文でのindexズレリスク) ===")
CANONICAL_DIFF = "The article reviewed twenty eight studies, and it was written for you."
ASR_DIFF = "The article reviewed 28 studies, and it was written four you."
canon_tokens_diff = validation.tokenize(CANONICAL_DIFF)
canon_raw_diff = trial_b._raw_tokens_no_cardinal_conversion(CANONICAL_DIFF)
asr_raw_diff = trial_b._raw_tokens_no_cardinal_conversion(ASR_DIFF)
located_diff = trial_b._locate_number_mismatch_opcodes(canon_tokens_diff, validation.tokenize(ASR_DIFF))
r1_diff, resc1_diff = trial_b.classify_asr_match_track_b_approach1(CANONICAL_DIFF, ASR_DIFF)
r2_diff, resc2_diff = trial_b.classify_asr_match_track_b_approach2(CANONICAL_DIFF, ASR_DIFF)
print(f"canonical={CANONICAL_DIFF!r}")
print(f"asr={ASR_DIFF!r}")
print(f"canon_tokens(post)={canon_tokens_diff}")
print(f"canon_raw(pre)   ={canon_raw_diff}")
print(f"located opcode index i1={located_diff[0]['i1'] if located_diff else None} "
      f"-> canon_tokens[i1]={canon_tokens_diff[located_diff[0]['i1']]!r} "
      f"だがcanon_raw[i1]={canon_raw_diff[located_diff[0]['i1']]!r}(ズレによる誤参照、本来は'for'であるべき)")
print(f"approach1: {r1_diff.classification}/{r1_diff.should_pass} rescues={resc1_diff} "
      "(たまたま非rescueだが、誤ったindexを参照した結果であり設計上の安全保証ではない)")
print(f"approach2: {r2_diff.classification}/{r2_diff.should_pass} rescues={resc2_diff} "
      "(alignment_safe=Falseにより、最初からrescueを試みない=原理的に安全)")
results["new_fixtures"]["approach_diff_index_misalignment_risk"] = {
    "canonical": CANONICAL_DIFF, "asr": ASR_DIFF,
    "canon_tokens_post": canon_tokens_diff, "canon_raw_pre": canon_raw_diff,
    "misindexed_lookup": canon_raw_diff[located_diff[0]["i1"]] if located_diff else None,
    "expected_word_at_that_position": "for",
    "approach1_classification": r1_diff.classification, "approach1_should_pass": r1_diff.should_pass,
    "approach2_classification": r2_diff.classification, "approach2_should_pass": r2_diff.should_pass,
}

# ------------------------------------------------------------
# (d) 既存EN fixtureの全件回帰
#     - er006_preprod_hardening_01_validation_test.py(POSITIVE/AMBIGUOUS/NEGATIVE)
#     - er008_asr_variant_hardening_15_homophone_en_test.py(HOMOPHONE/NON_HOMOPHONE pairs)
#     - er011_no18_b1_connected_speech_trial_07.py(CASES/NEGATIVE_CONTROL_CASES)
# ------------------------------------------------------------
print("\n=== (d) 既存EN fixture全件回帰 ===")


def run_group(group_name, fixtures, approach_name, fn):
    changed = []
    total = 0
    for fx in fixtures:
        canonical = fx["canonical"]
        asr = fx["asr"]
        baseline = validation.classify_asr_match(canonical, asr)
        candidate, rescues = fn(canonical, asr)
        total += 1
        is_changed = (baseline.classification != candidate.classification
                      or baseline.should_pass != candidate.should_pass)
        status = "SAME" if not is_changed else "CHANGED"
        print(f"[{status}] [{group_name}/{approach_name}] {fx['name']}: "
              f"baseline={baseline.classification}/{baseline.should_pass} "
              f"candidate={candidate.classification}/{candidate.should_pass} rescues={rescues}")
        if is_changed:
            changed.append({
                "name": fx["name"], "canonical": canonical, "asr": asr,
                "baseline_classification": baseline.classification, "baseline_should_pass": baseline.should_pass,
                "candidate_classification": candidate.classification, "candidate_should_pass": candidate.should_pass,
                "rescues": rescues,
            })
    return total, changed


all_groups = [
    ("POSITIVE_FIXTURES", v_test.POSITIVE_FIXTURES),
    ("AMBIGUOUS_FIXTURES", v_test.AMBIGUOUS_FIXTURES),
    ("NEGATIVE_FIXTURES", v_test.NEGATIVE_FIXTURES),
]

grand_total = 0
grand_changed = {"approach1": [], "approach2": []}
for group_name, fixtures in all_groups:
    for approach_name, fn in (("approach1", trial_b.classify_asr_match_track_b_approach1),
                               ("approach2", trial_b.classify_asr_match_track_b_approach2)):
        total, changed = run_group(group_name, fixtures, approach_name, fn)
        results["regression"].setdefault(group_name, {})[approach_name] = {
            "total": total, "changed_count": len(changed), "changed": changed}
        if approach_name == "approach1":
            grand_total += total
        grand_changed[approach_name].extend(f"{group_name}:{c['name']}" for c in changed)

# Connected Speech Trial 07 CASES/NEGATIVE_CONTROL_CASES
print("\n--- Connected Speech Validator (er011_no18_b1_connected_speech_trial_07) ---")
cs_fixtures = [{"name": k, "canonical": v["canonical"], "asr": v["asr"]} for k, v in cs_trial.CASES.items()]
cs_neg_fixtures = [{"name": k, "canonical": v["canonical"], "asr": v["asr"]}
                    for k, v in cs_trial.NEGATIVE_CONTROL_CASES.items()]
for group_name, fixtures in (("CONNECTED_SPEECH_CASES", cs_fixtures),
                              ("CONNECTED_SPEECH_NEGATIVE_CONTROL", cs_neg_fixtures)):
    for approach_name, fn in (("approach1", trial_b.classify_asr_match_track_b_approach1),
                               ("approach2", trial_b.classify_asr_match_track_b_approach2)):
        total, changed = run_group(group_name, fixtures, approach_name, fn)
        results["regression"].setdefault(group_name, {})[approach_name] = {
            "total": total, "changed_count": len(changed), "changed": changed}
        if approach_name == "approach1":
            grand_total += total
        grand_changed[approach_name].extend(f"{group_name}:{c['name']}" for c in changed)

# homophone_en_test.py自体はhomophone_arpabet_equivalent()を直接叩くだけの
# fixtureであり、classify_asr_match()を経由しないため、Track Bの2approachは
# ここへは影響しない(Production関数自体は無変更のため既存test結果はSAME)。
# 参考として、Track Bが内部で使うhomophone_arpabet_equivalent()自体の既存
# fixtureが今回のimportで壊れていないことだけ直接確認する。
print("\n--- 参考: homophone_arpabet_equivalent()自体の既存fixture(不変更の確認) ---")
homophone_fixture_failures = []
for a, b in hp_test.HOMOPHONE_PAIRS:
    result = homophone_en_result = trial_b.homophone_en.homophone_arpabet_equivalent(a, b)
    ok = result is True
    print(f"[{'OK' if ok else 'FAIL'}] {a}/{b} -> {result}")
    if not ok:
        homophone_fixture_failures.append(f"{a}/{b}")
for a, b in hp_test.NON_HOMOPHONE_PAIRS:
    result = trial_b.homophone_en.homophone_arpabet_equivalent(a, b)
    ok = result is False
    print(f"[{'OK' if ok else 'FAIL'}] {a}/{b} -> {result} (期待 False)")
    if not ok:
        homophone_fixture_failures.append(f"{a}/{b}")

print("\n=== まとめ ===")
print(f"新規fixture(a-c): {len(new_fixture_failures)}件が期待通りでなかった: {new_fixture_failures}")
for approach_name in ("approach1", "approach2"):
    print(f"既存fixture回帰({approach_name}): 全{grand_total}件中、判定が変わったもの="
          f"{len(grand_changed[approach_name])}件: {grand_changed[approach_name]}")
print(f"homophone_arpabet_equivalent()既存fixture: {len(homophone_fixture_failures)}件が期待通りでなかった: "
      f"{homophone_fixture_failures}")

results["summary"] = {
    "new_fixture_failures": new_fixture_failures,
    "regression_total": grand_total,
    "regression_changed_approach1": grand_changed["approach1"],
    "regression_changed_approach2": grand_changed["approach2"],
    "homophone_fixture_failures": homophone_fixture_failures,
}

out_dir = "er011_output/open112_kp_validator_fix_trial_17"
os.makedirs(out_dir, exist_ok=True)
out_path = f"{out_dir}/track_b_en_results.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"\nwrote {out_path}")
