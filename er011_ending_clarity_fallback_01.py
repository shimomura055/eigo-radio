# ============================================================
# er011_ending_clarity_fallback_01.py
# ER-011-NO18-OPEN107-PRODUCTION-WIRING-AND-FINAL-AUDIO-03
# ============================================================
# OPEN-107(ER-011-NO18-OPEN108-LEDGER-REFINE-AND-OPEN107-ENDING-FALLBACK-
# TRIAL-02のTrack B)で、ユーザーがEnding-Clarity fallback(語尾・最終音素の
# 明瞭さを既存instructionへAND方式で追加する、"opened"等へのhardcodeなしの
# 一般化されたfallback)をユーザー正式承認(APPROVED_FOR_PRODUCTION)した。
# 本moduleは、これをProduction正式TTS経路(news_tail_fix.
# generate_news_narration_wide_margin、B1のFull Story/Point本文/In One
# Line生成)へ配線する。
#
# 設計方針(Trialで検証済みの手法をそのまま踏襲):
#   1. news_tail_fix.generate_news_narration_wide_margin()自体は一切
#      変更しない(既に本番実績のある関数を無変更のまま維持し、regression
#      riskを最小化する)。
#   2. 通常TTS+通常retry(review_lockを経由しない生の実装、__wrapped__
#      経由)を1回実行する。PASSすれば即座にそのまま返す(fallbackは一切
#      呼ばれない=常時適用ではない)。
#   3. NGだった場合のみ、そのsegmentの最終ASR結果に対して「語尾の屈折語尾
#      (-ed/-s/-ing等)が脱落した」パターンを検出する(既存の
#      er006_preprod_hardening_01_validation.classify_asr_matchが計算済みの
#      content_word_diffsを流用、新しい比較ロジックを重複実装しない、
#      "opened"のような特定語へのhardcodeはしない)。パターンが検出されない
#      NG(語尾脱落以外の理由の不一致)にはfallbackを一切適用しない。
#   4. 語尾脱落パターンが検出された場合のみ、Trialで検証済みのmonkeypatch
#      手法(p9a.ENGLISH_STYLE_PREFIXをこの1回の呼び出し中だけEnding-
#      Clarity版へ差し替え、呼び出し後finallyで必ず復元)で、同じ生の実装を
#      再度呼び出す(最大FALLBACK_MAX_ATTEMPTS回)。PASSすればそのsegmentだけ
#      差し替え、他の正常segmentには一切影響しない。
#   5. review_lockは、この関数全体(通常+条件付きfallback)を「1回の論理的
#      生成操作」として1回だけguardする(通常呼び出しとfallback呼び出しを
#      それぞれ別々にreview_lockへ通すと、通常NGの時点で即座にHUMAN_REVIEW_
#      REQUIREDへ遷移し、fallback自体が実行される前にブロックされてしまう
#      ため、内部の2回の呼び出しは__wrapped__[生の実装]を直接呼ぶ)。

from __future__ import annotations

import er003_b1_p9a_audio as p9a
import er003_v1_sing01_news_tail_fix as news_tail_fix
import er006_preprod_hardening_01_validation as en_validator
import er011_human_review_lock_01 as review_lock

# ユーザー提示の意図例にほぼ準拠した文言。既存instructionを全面置換せず、
# 末尾へAND方式で追加する。"opened"/"-ed"への直接的な言及は含まない。
ENDING_CLARITY_SUFFIX = (
    " Pronounce grammatical endings and final sounds clearly enough to remain audible, "
    "without exaggerating them or disrupting the natural rhythm of the sentence.")

# Trial(ER-011-NO18-OPEN108-LEDGER-REFINE-AND-OPEN107-ENDING-FALLBACK-
# TRIAL-02)のcondition 6[Production実データ相当]で検証したのと同じ回数
# (PRODUCTION_EQUIVALENT_OUTER_REPEATS=2)。新たに発明した値ではない。
FALLBACK_MAX_ATTEMPTS = 2

# 規則的な屈折語尾のみを対象にする(不規則変化・派生語形成接尾辞は対象外、
# 安全側に絞る)。canonical wordがasr wordの後ろにこの中のいずれかを
# 追加した形になっている場合のみ「語尾脱落」とみなす。
_INFLECTIONAL_SUFFIXES = ("ed", "ing", "es", "s", "en", "er", "est", "ly", "d")


def _dropped_suffix_if_ending_loss(canonical_word: str, asr_word: str) -> str | None:
    c, a = canonical_word.lower(), asr_word.lower()
    if not c or not a or c == a or not c.startswith(a):
        return None
    dropped = c[len(a):]
    if 0 < len(dropped) <= 3 and dropped in _INFLECTIONAL_SUFFIXES:
        return dropped
    return None


def detect_ending_loss_diffs(canonical_text: str, asr_text: str | None) -> list[dict]:
    """canonical_textとasr_textを比較し、「語末の屈折語尾が脱落した単語」の
    みを一般的に検出する(特定語へのhardcodeなし)。既存のclassify_asr_match
    が既に計算済みのcontent_word_diffs(単一語同士のreplace型diffのみ)を
    流用し、新しい比較ロジックは追加しない。固有名詞・同音語・複数語にまたが
    る差分・ASRの単なる表記揺れは対象外(狭く安全側に絞る)。"""
    if not asr_text:
        return []
    classification = en_validator.classify_asr_match(canonical_text, asr_text)
    findings = []
    for diff in classification.protected.content_word_diffs:
        if diff.get("type") != "replace":
            continue
        canon_words = diff.get("canonical", "").split()
        asr_words = diff.get("asr", "").split()
        if len(canon_words) != 1 or len(asr_words) != 1:
            continue
        dropped = _dropped_suffix_if_ending_loss(canon_words[0], asr_words[0])
        if dropped:
            findings.append({"canonical_word": canon_words[0], "asr_word": asr_words[0], "dropped_suffix": dropped})
    return findings


def _last_asr_text(result: dict) -> str | None:
    for log_key in ("attempts_log", "fallback_attempts_log"):
        log = result.get(log_key)
        if isinstance(log, list) and log:
            last = log[-1]
            if isinstance(last, dict) and last.get("asr_text"):
                return last["asr_text"]
    return result.get("asr_text")


@review_lock.guarded_generate("en")
def generate_news_narration_with_ending_clarity_fallback(
        text: str, out_path: str, max_attempts: int = review_lock.PRODUCTION_MAX_TTS_ATTEMPTS,
        max_extra_chars: int = 15, disfluency_qa: bool = False) -> dict:
    """news_tail_fix.generate_news_narration_wide_margin()の通常TTS+通常
    retryを未変更のまま1回実行し、それでもASRが語尾脱落パターンでNGの場合
    だけ、そのsegmentにEnding-Clarity fallbackを適用する。正常にPASSした
    segmentや、語尾脱落以外の理由でNGになったsegmentには一切影響しない
    (fallback instructionの常時適用はしない)。"""
    core = news_tail_fix.generate_news_narration_wide_margin.__wrapped__

    normal_result = core(text, out_path, max_attempts=max_attempts, max_extra_chars=max_extra_chars,
                          disfluency_qa=disfluency_qa)
    normal_result["ending_clarity_fallback_used"] = False
    if normal_result.get("status") == "OK":
        return normal_result

    last_asr = _last_asr_text(normal_result)
    ending_loss_diffs = detect_ending_loss_diffs(text, last_asr)
    normal_result["ending_clarity_trigger_check"] = {"last_asr_text": last_asr,
                                                       "ending_loss_diffs": ending_loss_diffs}
    if not ending_loss_diffs:
        # 語尾脱落パターンが検出されない通常NG(内容誤り等)には
        # fallbackを適用しない。既存のSTOP/NG処理をそのまま返す。
        return normal_result

    original_prefix = p9a.ENGLISH_STYLE_PREFIX
    p9a.ENGLISH_STYLE_PREFIX = original_prefix + ENDING_CLARITY_SUFFIX
    try:
        fallback_result = core(text, out_path, max_attempts=FALLBACK_MAX_ATTEMPTS,
                                max_extra_chars=max_extra_chars, disfluency_qa=disfluency_qa)
    finally:
        p9a.ENGLISH_STYLE_PREFIX = original_prefix  # 恒久変更を残さない

    fallback_attempts_log = fallback_result.pop("attempts_log", []) or []
    if fallback_result.get("status") == "OK":
        fallback_result["ending_clarity_fallback_used"] = True
        fallback_result["ending_clarity_trigger"] = ending_loss_diffs
        fallback_result["ending_clarity_instruction_used"] = original_prefix + ENDING_CLARITY_SUFFIX
        fallback_result["standard_attempts_log"] = normal_result.get("attempts_log")
        fallback_result["fallback_attempts_log"] = fallback_attempts_log
        fallback_result["instruction_type"] = "ending_clarity_fallback"
        return fallback_result

    # fallbackも不合格 -> 既存のSTOP/NG処理へ(通常経路のnormal_resultを
    # そのまま権威ある失敗結果として返し、fallback試行の証跡のみ付加する)。
    normal_result["ending_clarity_fallback_used"] = True
    normal_result["ending_clarity_fallback_failed"] = True
    normal_result["fallback_attempts_log"] = fallback_attempts_log
    normal_result["ending_clarity_fallback_result_status"] = fallback_result.get("status")
    return normal_result
