# ============================================================
# er003_audio_tts_asr_safety.py
# ER-003-AUDIO-HARDENING-01: TTS入力正規化・ASR検証正規化 共通ユーティリティ
# ============================================================
# ER-003-B1-SCAFFOLD-AUDIO-01で個別記事(A02)向けに発見・その場しのぎで
# 修正した4件のTTS/ASR技術的問題を、A2/B1/B2の今後の音声制作で再利用
# できる形に一般化したモジュール。
#
# 重要な原則(このモジュール全体で守ること):
#   1. TTS入力正規化とASR検証正規化は「目的が異なる別々の処理」であり、
#      1つの万能normalizerに統合しない(このファイル内でも関数を分離する)。
#      - TTS入力正規化: TTSモデルにテキストを安全に渡すためだけの処理。
#        カノニカルな記事本文・表示用テキスト・Fact-QA用テキストは
#        一切変更しない(TTS呼び出し直前でのみ適用する使い捨てコピー)。
#      - ASR検証正規化: 実際には正しく読み上げられた音声を、表記揺れ
#        (綴り・大文字小文字・句読点)だけを理由に誤ってFAILさせない
#        ための処理。ただし数字・固有名詞・否定・欠落語句・無関係な
#        内容の違いは絶対に見逃さない(過剰正規化の禁止)。
#   2. カノニカルテキスト(記事本文)は、TTSの都合で書き換えない。
#   3. ASR未取得(空文字列/Noneまたは認証・API的なエラー)は、
#      絶対にPASS扱いにしない。
#
# このモジュールはProduction本体のTTS/ASR呼び出し関数
# (er003_b1_p9a_audio.py, er003_v1_repro01_main_generate.py 等)を
# import・変更しない。呼び出し側が実際のTTS/ASR関数をcallableとして
# 渡すオーケストレーション方式にすることで、Productionパイプラインへの
# 大規模改修を避けている(ER-003-AUDIO-HARDENING-01の非スコープ:
# 大規模Production refactor)。
#
# 出自: ER-003-B1-SCAFFOLD-AUDIO-01/02で発見された以下の問題への対策を
# 一般化したもの(元の実装は er003_v1_b1_scaffold_audio_01_generate.py):
#   - Markdown強調記号(**)・カーブ引用符によるTTS 400エラー
#   - 自己言及的な一文("The word X matters."型)によるTTS 400エラー
#   - text[:N]文字列包含によるASR検証の偽陰性
#     (改行混入・単語途中切断・ハイフン複合語・コンマ有無)
#   - 英国綴り/米国綴り差(personalised/personalized)による偽陰性

from __future__ import annotations

import re

# ============================================================
# A. TTS入力正規化(TTS呼び出し直前のみに適用する)
# ============================================================

def strip_markdown_for_tts(text: str) -> str:
    """TTSモデルへ渡す直前だけに使う。Markdown強調記号(**)とカーブ引用符
    (“ ”)を除去する。単語そのものは変更しない。カノニカル本文・表示用
    テキスト・Fact-QA用テキストにはこの関数を通さない(呼び出し側で
    使い捨てコピーに対してのみ適用すること)。"""
    text = text.replace("**", "")
    text = text.replace("“", "").replace("”", "")
    return text


# 自己言及的・指示文的に見えるためTTSモデルが「これはナレーション対象の
# 台本ではなく自分への指示文だ」と誤解しやすいパターン。厳密な検出は
# 困難なため、簡易ヒューリスティックとしてのみ提供する(判定を過信せず、
# 実際の判断はTTS呼び出しの成否そのもので行うこと。下記
# generate_and_verify_segmentのfallback機構が本体)。
_SELF_REFERENTIAL_HINT_RE = re.compile(
    r"\bthe word[s]?\b.{0,40}\bmatters?\b", re.IGNORECASE)


def looks_self_referential(text: str) -> bool:
    """自己言及的な一文(例: "The word default matters.")の疑いがあるか
    どうかの簡易ヒント。Trueでも実際にTTSが失敗するとは限らず、Falseでも
    未知パターンで失敗する可能性がある。ログ・優先度判断の補助情報に
    とどめ、これ単体でTTS方式を確定的に分岐させない。"""
    return bool(_SELF_REFERENTIAL_HINT_RE.search(text or ""))


# ============================================================
# B. TTS生成のfallbackオーケストレーション
# ============================================================

def generate_tts_with_fallback(text: str, out_path: str, primary_fn, fallback_fn,
                                max_attempts: int = 6) -> dict:
    """primary_fn(text, out_path)->dict{status,...}を試み、失敗した場合の
    みfallback_fn(text, out_path)へ切り替える。両方とも既存Production
    関数をそのままcallableとして渡す想定で、このモジュール自身は具体的な
    TTS API呼び出しを持たない(呼び出し側のProduction機構を再利用する
    ことで、TTS instruction文言自体は新規作成しない)。

    戻り値には試行ログ(attempts_log)とinstruction_type
    ("primary"/"fallback")を含める。max_attempts回試しても両方失敗した
    場合はstatus="STOPPED"を返す。呼び出し側はこれを自動リトライで
    ごまかさず、HUMAN_REVIEW/SPECIAL_TTS_HANDLINGとして扱うこと
    (無理に汎用解決しようとしない、というのがハードニング仕様の方針)。
    """
    attempts_log = []
    for attempt in range(1, max_attempts + 1):
        r = primary_fn(text, out_path)
        instruction_type = "primary"
        if r.get("status") != "OK":
            attempts_log.append({"attempt": attempt, "status": r.get("status"),
                                  "reason": r.get("reason"), "instruction_type": instruction_type})
            r = fallback_fn(text, out_path)
            instruction_type = "fallback"
            if r.get("status") != "OK":
                attempts_log.append({"attempt": attempt, "status": r.get("status"),
                                      "reason": r.get("reason"), "instruction_type": instruction_type})
                continue
        r = dict(r)
        r["instruction_type"] = instruction_type
        r["attempts_log"] = attempts_log
        return r
    return {"status": "STOPPED", "reason": f"{max_attempts}回試行してもTTS生成に成功しませんでした",
            "instruction_type": "human_review_required", "attempts_log": attempts_log}


# ============================================================
# C. ASR検証正規化
# ============================================================

def _extract_words(text: str) -> list:
    return re.findall(r"[A-Za-z0-9']+", (text or "").lower())


# 英国綴り/米国綴りの体系的な差異のみを対象にする(語彙単位の大規模辞書は
# 作らない=過剰正規化の防止)。個別の非体系的な綴り差(grey/gray等)が
# 今後実務で問題になった場合は、ここへ明示的なペアを追加すること。
_BRITISH_AMERICAN_SUFFIX_RULES = [
    ("ise", "ize"),
    ("ised", "ized"),
    ("ising", "izing"),
    ("isation", "ization"),
    ("our", "or"),
]


def _words_equivalent(a: str, b: str) -> bool:
    if a == b:
        return True
    for uk_suffix, us_suffix in _BRITISH_AMERICAN_SUFFIX_RULES:
        if a.endswith(uk_suffix) and b.endswith(us_suffix) and a[:-len(uk_suffix)] == b[:-len(us_suffix)]:
            return True
        if a.endswith(us_suffix) and b.endswith(uk_suffix) and a[:-len(us_suffix)] == b[:-len(uk_suffix)]:
            return True
    return False


def _subsequence_match(expected_words: list, actual_words: list, equivalent) -> bool:
    span = len(expected_words)
    if span == 0:
        return False
    for i in range(len(actual_words) - span + 1):
        if all(equivalent(expected_words[j], actual_words[i + j]) for j in range(span)):
            return True
    return False


def expected_words_present(expected_text: str, asr_text: str, n: int = 6) -> bool:
    """後方互換のための単純判定(旧er003_v1_b1_scaffold_audio_01_generate.
    expected_words_presentと同じ挙動: 単語完全一致の連続部分列判定、
    綴り差は吸収しない)。新規コードはvalidate_asr_matchの利用を推奨する。"""
    expected_words = _extract_words(expected_text)[:n]
    if not expected_words:
        return False
    actual_words = _extract_words(asr_text)
    return _subsequence_match(expected_words, actual_words, equivalent=lambda a, b: a == b)


EXACT_MATCH = "EXACT_MATCH"
NORMALIZED_MATCH = "NORMALIZED_MATCH"
FAIL = "FAIL"


def validate_asr_match(expected_text: str, asr_text, n: int = 6, asr_error: str = None) -> dict:
    """expected_textの先頭n語と、ASR書き起こしテキストを比較し、監査
    可能な判定結果を返す。

    判定基準(過剰正規化の禁止を優先する):
      - asr_error指定あり、またはasr_textが空/None
        → FAIL(ASR未取得・API/認証エラーは絶対にPASS扱いにしない)
      - 単語完全一致(大文字小文字・句読点・改行・ハイフンは無視)の
        連続部分列として一致 → EXACT_MATCH
      - 英国綴り/米国綴りの体系的な差異のみを吸収した上で一致
        → NORMALIZED_MATCH
      - それ以外(語句の欠落・追加・数字違い・否定の有無・無関係な
        内容を含む) → FAIL

    戻り値は監査trail(expected_text/normalized_expected/asr_text/
    normalized_actual/verdict/passed/reason)を含む。
    """
    normalized_expected = _extract_words(expected_text)[:n]
    normalized_actual = _extract_words(asr_text) if asr_text else []

    result = {
        "expected_text": expected_text,
        "normalized_expected_words": normalized_expected,
        "asr_text": asr_text,
        "normalized_actual_words": normalized_actual,
    }

    if asr_error:
        result.update(verdict=FAIL, passed=False,
                       reason=f"ASR/API error — treated as FAIL, PASS forbidden: {asr_error}")
        return result
    if not asr_text:
        result.update(verdict=FAIL, passed=False,
                       reason="ASR text is empty/None — treated as FAIL, PASS forbidden")
        return result
    if not normalized_expected:
        result.update(verdict=FAIL, passed=False, reason="expected_text produced no words")
        return result

    if _subsequence_match(normalized_expected, normalized_actual, equivalent=lambda a, b: a == b):
        result.update(verdict=EXACT_MATCH, passed=True, reason="word-for-word subsequence match")
        return result

    if _subsequence_match(normalized_expected, normalized_actual, equivalent=_words_equivalent):
        result.update(verdict=NORMALIZED_MATCH, passed=True,
                       reason="matched after British/American spelling normalization only")
        return result

    result.update(verdict=FAIL, passed=False,
                   reason="no matching subsequence found even after spelling normalization "
                          "(word omission, addition, number/negation difference, or unrelated content)")
    return result
