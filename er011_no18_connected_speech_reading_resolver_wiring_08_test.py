# ============================================================
# er011_no18_connected_speech_reading_resolver_wiring_08_test.py
# ER-011-NO18-CONNECTED-SPEECH-READING-RESOLVER-PRODUCTION-WIRING-08
# Regression Tests (§10, 最低15項目)
# ============================================================
# B1 Connected Speech Validator: 1-8
# A2 Reading Resolver: 9-15
from __future__ import annotations

import er003_v1_n3_01_tts_generate as n3_tts
import er006_preprod_hardening_01_validation as en_validator
import er007_ja_asr_validator_01 as javal
import er011_a2_reading_resolver_01 as reading_resolver

failures = []


def check(name, condition, detail=""):
    status = "OK" if condition else "FAIL"
    print(f"[{status}] {name}" + (f" ({detail})" if detail and not condition else ""))
    if not condition:
        failures.append(name)


# ------------------------------------------------------------
# B1 Connected Speech Validator
# ------------------------------------------------------------
print("=== B1 Connected Speech Validator ===")

# 1. studies suggest型 -> ACCEPT
r1 = en_validator.classify_asr_match(
    "The studies suggest that a phone can affect attention even when you do not check it.",
    "The study suggests that a phone can affect attention even when you do not check it.")
check("1. studies suggest型 -> CONNECTED_SPEECH_ACCEPT",
      r1.classification == "CONNECTED_SPEECH_ACCEPT" and r1.should_pass is True, r1.classification)

# 2. opened to型 -> ACCEPT
r2 = en_validator.classify_asr_match(
    "Your phone does not have to be opened to become part of the task.",
    "Your phone does not have to be open to become part of the task.")
check("2. opened to型 -> CONNECTED_SPEECH_ACCEPT",
      r2.classification == "CONNECTED_SPEECH_ACCEPT" and r2.should_pass is True, r2.classification)

# 3. survey suggest型 -> PASS_WITH_WARNING
r3 = en_validator.classify_asr_match(
    "The studies and the survey suggest that a phone can affect people even when they do not check it.",
    "The studies and the surveys suggest that a phone can affect people even when they do not check it.")
check("3. survey suggest型 -> CONNECTED_SPEECH_PASS_WITH_WARNING",
      r3.classification == "CONNECTED_SPEECH_PASS_WITH_WARNING" and r3.should_pass is True, r3.classification)

# 4. 無関係なword change -> NG
r4 = en_validator.classify_asr_match(
    "The report shows a clear increase in visits.", "The report shows a clear decrease in visits.")
check("4. 無関係なword change(increase/decrease) -> TRUE_CONTENT_MISMATCH",
      r4.classification == "TRUE_CONTENT_MISMATCH" and r4.should_pass is False, r4.classification)

# 5. unrelated insertion -> NG
r5 = en_validator.classify_asr_match(
    "The report shows clear evidence about the trend.",
    "The report shows clear evidence about the trend today.")
check("5. unrelated insertion -> TRUE_CONTENT_MISMATCH",
      r5.classification == "TRUE_CONTENT_MISMATCH" and r5.should_pass is False, r5.classification)

# 6. 子音条件不成立(次語頭が歯擦音でない、shはdigraphのため対象外) -> 誤って許容しない
r6 = en_validator.classify_asr_match(
    "The survey shows useful results for parents.", "The surveys show useful results for parents.")
check("6. 子音条件不成立(survey/shows、次語頭がshで歯擦音対象外) -> CONNECTED_SPEECHとして誤って許容しない",
      r6.should_pass is False
      and r6.classification not in ("CONNECTED_SPEECH_ACCEPT", "CONNECTED_SPEECH_PASS_WITH_WARNING"),
      r6.classification)

# 7. warning対象とno-warning対象を区別
check("7. ACCEPT(警告なし)とPASS_WITH_WARNINGは異なるclassificationである",
      r1.classification != r3.classification
      and r1.connected_speech_info["rule"] == "Pattern_A_sibilant_sequence"
      and r3.connected_speech_info["rule"] == "Pattern_C_resegmentation_added_consonant")

# 8. OPEN-107 fallback(Ending-Clarity)がProduction経路から呼ばれない
with open("er003_v1_n3_01_tts_generate.py", encoding="utf-8") as f:
    orchestrator_src = f.read()
check("8. er003_v1_n3_01_tts_generate.pyがer011_ending_clarity_fallback_01をimportしていない",
      "import er011_ending_clarity_fallback_01" not in orchestrator_src)

# ------------------------------------------------------------
# A2 Reading Resolver
# ------------------------------------------------------------
print("\n=== A2 Reading Resolver ===")

# 9. 後->あと解決(実データOPEN-111相当の文脈、実際にLLM呼び出しを発火させる)
r9 = javal.classify_ja_asr_match(
    "スマートフォンの通知音のあとに作業へ戻ることについて話します。",
    "スマートフォンの通知音の後に作業へ戻ることについて話します。")
check("9. 後->あと(comment_1相当) -> READING_RESOLVED_MATCH",
      r9.classification == "READING_RESOLVED_MATCH" and r9.should_pass is True, r9.classification)

# 10. 正常segment -> Resolver未発火(機械変換の時点で既に一致)
r10 = javal.classify_ja_asr_match("今日は天気がいいですね。", "今日は天気がいいですね。")
check("10. 完全一致segment -> Resolver未発火(EXACT_MATCH)",
      r10.classification == "EXACT_MATCH" and r10.reading_resolver_info is None, r10.classification)

# 11. 候補外応答 -> NG(fail-safe): call_resolverが候補外を返した場合、
#     resolve_reading_diffはresolved_match=Falseで返すこと。
_orig_call_resolver = reading_resolver.call_resolver
try:
    def _fake_call_resolver_out_of_candidates(full_text_context, target_word, candidates):
        return {"selected_reading": "でたらめ", "response_id": "fake", "model": "fake"}
    reading_resolver.call_resolver = _fake_call_resolver_out_of_candidates
    result11 = reading_resolver.resolve_reading_diff(
        "スマートフォンの通知音のあとに作業へ戻る。", "スマートフォンの通知音の後に作業へ戻る。")
    check("11. 候補外応答 -> resolved_match=False(fail-safe)",
          result11["resolved_match"] is False, str(result11.get("error")))
finally:
    reading_resolver.call_resolver = _orig_call_resolver

# 12. 候補なし -> NG/STOP: 辞書候補が空の場合、そのchunkは未解決のまま
_orig_candidates = reading_resolver.single_char_candidates
try:
    reading_resolver.single_char_candidates = lambda ch: []
    result12 = reading_resolver.resolve_reading_diff(
        "スマートフォンの通知音のあとに作業へ戻る。", "スマートフォンの通知音の後に作業へ戻る。")
    check("12. 候補なし -> resolved_match=False(fail-safe)、resolver_calls=0",
          result12["resolved_match"] is False and result12["resolver_calls"] == 0, str(result12))
finally:
    reading_resolver.single_char_candidates = _orig_candidates

# 13. LLM不正応答(例外) -> NG/STOP
try:
    def _raise(*args, **kwargs):
        raise RuntimeError("simulated malformed LLM response")
    reading_resolver.call_resolver = _raise
    result13 = reading_resolver.resolve_reading_diff(
        "スマートフォンの通知音のあとに作業へ戻る。", "スマートフォンの通知音の後に作業へ戻る。")
    check("13. LLM不正応答(例外) -> resolved_match=False(fail-safe)、errorが記録される",
          result13["resolved_match"] is False and result13["error"] is not None, str(result13.get("error")))
finally:
    reading_resolver.call_resolver = _orig_call_resolver

# 14. 読み問題でない差分(真の内容誤り) -> PASSさせない
r14 = javal.classify_ja_asr_match("今日は増加傾向にあります。", "今日は減少傾向にあります。")
check("14. 読み問題でない真の内容誤り(増加/減少) -> TRUE_CONTENT_MISMATCH(READING_RESOLVED_MATCHにならない)",
      r14.classification == "TRUE_CONTENT_MISMATCH" and r14.should_pass is False, r14.classification)

# 15. B1(英語Validator)にはReading Resolverが一切importされない
with open("er006_preprod_hardening_01_validation.py", encoding="utf-8") as f:
    en_validator_src = f.read()
check("15. er006_preprod_hardening_01_validation.pyがer011_a2_reading_resolver_01をimportしていない",
      "er011_a2_reading_resolver_01" not in en_validator_src)


print()
if failures:
    raise AssertionError(f"{len(failures)}件のregression testが失敗した: {failures}")
print(f"OK: 全15項目のregression testがPASSした")
