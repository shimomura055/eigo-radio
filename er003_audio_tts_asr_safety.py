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


# ER-003-AUDIO-JP-READING-SAFETY-01: 日本語分数表現「N分のM」の「分」読み対策
# ------------------------------------------------------------
# 「分」は「ふん(時間)」「ぶん(割合)」等の複数の読みを持つ多音字。
# 「N分のM」という分数パターンでは「ぶん」と読むべきだが、ER-003-IRAN-
# A2-B1-01で、文脈のない短いTTS入力("5分の1"のみ)に対しTTSモデルが
# より頻度の高い「ふん」読みを選んでしまう事例が発覚した("ごふんのいち"、
# 正しくは"ごぶんのいち")。
#
# 重要な構造的限界: この読み間違いはASRによる自動検証だけでは検出でき
# ない。正しい"ごぶんのいち"でも誤った"ごふんのいち"でも、Azure STTは
# 分数として認識すると同じ"1/5"等の数字表記へ正規化してしまうため、
# ASR書き起こしテキストの一致だけを根拠にPASS判定してはならない
# (validate_asr_matchはこの種の読み違いを原理的に検出できない)。
# 機械的に保証できるのは「TTS入力へ'ぶん'という読みを明示したこと」
# までであり、それ以上(実際にその通り発音されたか)はASRでは確認
# できない。本関数はTTS入力正規化(セクションA)としてのみ提供する。
#
# 対象は「N分のM」という分数パターンに厳密に限定する。「5分待つ」
# 「10分後」「3分間」等、"分"の後に"の"+数字が続かない時間表現は
# 一切変換しない(過剰な多音字辞書は作らない、というモジュール全体の
# 方針を踏襲)。カノニカル/表示用テキスト自体は変更せず、TTS呼び出し
# 直前に渡すコピーにのみ適用すること。

_JP_FRACTION_RE = re.compile(r"([0-9０-９]+)分の([0-9０-９]+)")


def to_tts_safe_japanese_fraction_reading(text: str) -> str:
    """カノニカルテキストはそのまま、TTS入力用にのみ「N分のM」の「分」を
    「ぶん」へ明示的に読み替えたコピーを返す。分数パターン以外の「分」
    (時間表現等)には一切触れない。呼び出し側は、この関数の戻り値のみを
    TTS呼び出しへ渡し、記事本文・Key Phrase japanese_gloss等の表示用
    フィールドは元のまま保持すること。"""
    return _JP_FRACTION_RE.sub(lambda m: f"{m.group(1)}ぶんの{m.group(2)}", text or "")


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
# B1. 異常長音声(hallucination)の早期検知
# ============================================================
# ER-005-AUDIO-WASTE-REDUCTION-01(2026-08-21)で発見: TTSモデルが与えた
# テキストを読み上げず、無関係な内容(多くの場合、渡したstyle instruction
# 自体のパラフレーズ・翻訳)を生成する"instruction leakage"型hallucination
# が発生すると、音声長が本来の想定を大きく超える(実例: 数秒で読める
# はずの短いKey Phraseが100秒超になった)。この種の異常は、ASRを実行する
# 前に音声長だけで機械的に検知できる。
#
# 閾値は、今回のE2E実測ログにおける「正常に生成された(hallucinationで
# ない)attempt」の実測sec/word(英語)・sec/character(日本語)の最大値
# (英語 約1.10 sec/word、日本語 約0.55 sec/char、いずれも短いKey Phrase
# で固定オーバーヘッドの影響が大きい場合の値)に、十分な安全マージンを
# 掛けたもの。実測hallucination(kp5_en 17.33秒=17.3 sec/word、kp5_ja
# 136.96秒/127.96秒=27.4/25.6 sec/char)とは10倍以上の差があり、閾値の
# 微調整だけで正常な生成を誤って弾くリスクは低いと判断した。
EN_MAX_SEC_PER_WORD = 1.5
JA_MAX_SEC_PER_CHAR = 1.2
EN_FIXED_OVERHEAD_SECONDS = 4.0
JA_FIXED_OVERHEAD_SECONDS = 3.0


def estimate_max_reasonable_duration_seconds(text: str, language: str) -> float:
    """テキストの語数(英語)・文字数(日本語)から、正常な発話であれば
    まず超えないはずの音声長の上限を見積もる。閾値は意図的に緩く
    (かなり遅い発話でも正常判定されるように)設定しており、正常な発話
    速度のばらつきを誤検知しないことを優先する。"""
    text = text or ""
    if language == "ja":
        return len(text) * JA_MAX_SEC_PER_CHAR + JA_FIXED_OVERHEAD_SECONDS
    word_count = max(1, len(text.split()))
    return word_count * EN_MAX_SEC_PER_WORD + EN_FIXED_OVERHEAD_SECONDS


def detect_duration_anomaly(raw_duration_seconds: float, text: str, language: str) -> dict:
    """生成直後(ASR実行前)に呼び出す。異常に長い音声(hallucinationの
    疑い)を検知した場合、ASRへ送らずこの時点で当該attemptを破棄できる
    ようにするための判定結果を返す。"""
    max_reasonable = estimate_max_reasonable_duration_seconds(text, language)
    is_anomaly = raw_duration_seconds > max_reasonable
    return {
        "is_anomaly": is_anomaly,
        "raw_duration_seconds": raw_duration_seconds,
        "max_reasonable_seconds": round(max_reasonable, 2),
        "reason": (f"生成音声長({raw_duration_seconds:.2f}秒)が、テキスト量から見積もった"
                   f"妥当な上限({max_reasonable:.2f}秒)を超えています。TTSモデルが指示文の"
                   f"パラフレーズ等、無関係な内容を生成した疑いがあるため、ASRへ送らずこの"
                   f"attemptを破棄します。") if is_anomaly else "正常範囲内",
    }


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

# ER-005-AUDIO-WASTE-REDUCTION-01(2026-08-21)で発見: TTS入力側の
# tts_safe_number_words_en()は綴り数字(two〜twelve)を算用数字(2〜12)へ
# 変換してからTTSへ渡すが、この変換はTTSモデルの発音を安定させるためだけの
# ものであり、canonical_textやASR検証用の期待テキストには適用されない
# 場合がある。一方、Azure STTは口頭で発話された小さな数字を綴りのまま
# ("two")書き起こすことが多い。結果、TTS入力側の期待テキストに変換後の
# "2"が残っていると、正しく読み上げられた音声でも常に不一致になる
# (B1 full_story_part2で実際に6回連続で発生し、全て無意味な再生成に
# つながっていたことを確認済み)。これは「数字そのものの違い」を見逃す
# 過剰正規化ではなく、「同じ数字の異なる表記」を吸収する処理である
# (値が異なる数字同士は一致させない=数字の欠落・置換は引き続き検知する)。
_NUMBER_WORD_TO_DIGIT = {
    "one": "1", "two": "2", "three": "3", "four": "4", "five": "5", "six": "6",
    "seven": "7", "eight": "8", "nine": "9", "ten": "10", "eleven": "11", "twelve": "12",
}


def _numeric_form(w: str) -> str:
    return _NUMBER_WORD_TO_DIGIT.get(w, w)


def _words_equivalent(a: str, b: str) -> bool:
    if a == b:
        return True
    if _numeric_form(a) == _numeric_form(b) and (a in _NUMBER_WORD_TO_DIGIT or b in _NUMBER_WORD_TO_DIGIT
                                                   or a.isdigit() or b.isdigit()):
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


# ============================================================
# D. Production Telemetry(統一Attempt Ledgerスキーマ、提案・オプトイン)
# ============================================================
# ER-005-AUDIO-WASTE-REDUCTION-01(2026-08-21)で発見: 現行の各生成関数
# (p9a.generate_narration_snippet/voice01.generate_charon_*/repro01.
# generate_key_phrase_component_verified 等)は、それぞれ独自のattempt
# 辞書形式でログを書いており(attempts_log/standard_attempts_log+
# fallback_attempts_log/call_count+retry_countの3variant)、
# segment単位のCost・音声秒数を完全には復元できない箇所があった
# (B1のpoint_one_heading/point_two_headingは音声長が一切保存されて
# いなかった)。
#
# ここでは、今後の生成関数が「追加」で使える統一スキーマを提案する
# (既存の各生成関数のattempts_log自体を置き換える大規模改修は今回の
# スコープ外。呼び出し側が任意でnew_attempt_record()を使い、既存の
# attempts_logへ1件追記する形で段階的に導入できる)。
def new_attempt_record(
    *, episode_id: str, level: str, segment_name: str, attempt_number: int,
    path: str,  # "standard" | "fallback" | "minimal_instruction" 等
    tts_model: str = None, tts_input_tokens: int = None, tts_output_tokens: int = None,
    generated_audio_seconds: float = None, tts_cost_jpy: float = None,
    asr_audio_seconds: float = None, asr_cost_jpy: float = None, asr_transcript: str = None,
    validation_result: str = None,  # "PASS" | "FAIL" | "DURATION_ANOMALY" | "TTS_ERROR" 等
    failure_reason: str = None,
    retry_decision: str = None,  # "retry_tts" | "no_retry_minor_diff" | "retry_asr_only" | "stop_human_review" 等
) -> dict:
    """1回のTTS(+ASR)試行を表す統一レコードを1件生成する。値が不明な
    フィールドはNoneのまま残し(推測で埋めない)、既存のattempts_log
    エントリへ追記する形で使うことを想定する。"""
    return {
        "episode_id": episode_id, "level": level, "segment_name": segment_name,
        "attempt_number": attempt_number, "path": path,
        "tts_model": tts_model, "tts_input_tokens": tts_input_tokens,
        "tts_output_tokens": tts_output_tokens, "generated_audio_seconds": generated_audio_seconds,
        "tts_cost_jpy": tts_cost_jpy, "asr_audio_seconds": asr_audio_seconds,
        "asr_cost_jpy": asr_cost_jpy, "asr_transcript": asr_transcript,
        "validation_result": validation_result, "failure_reason": failure_reason,
        "retry_decision": retry_decision,
    }
