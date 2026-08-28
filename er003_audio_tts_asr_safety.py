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

import json
import os
import re
import time

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


# ============================================================
# A1. Key Phrase日本語glossの辞書的項変数記法(placeholder)検出
# ============================================================
# ER-006-KP5-CANONICAL-BUG-01(2026-08-22)で発見: 2つの目的語を取る
# 英語Key Phrase(例: "associate with")のjapanese_glossを生成する際、
# LLMが辞書の見出し語定義でよく使われる項変数記法(例:
# 「〜を…と結びつける」)をそのまま出力することがある。「〜」「…」は
# いずれも実際には発話されない記号であり、この記法のままcanonical_text
# としてTTS/ASR比較へ渡すと、実際にどう発話させても原理的に一致し
# ようがない不良segmentになる(該当例: Public Benches B1 kp5_ja、
# 全12回のattemptがTRUE_CONTENT_MISMATCH/ASR_VALIDATION_UNCERTAIN)。
#
# 「〜」は先頭位置であれば(例:「～によって」のような接続パターン)
# 除去しても文法的に成立する場合があり、tts_safe_ja()側で既に対応
# 済み。一方、この関数が対象とするのは「文中に残った」項変数記法で
# あり、機械的な削除では文法が壊れる(例:「〜を…と結びつける」から
# 記号だけ削ると「をと結びつける」という非文になる)。そのため、この
# 関数は「削除して当座を凌ぐ」のではなく、TTS呼び出し自体を行う前に
# 検出してブロックする(呼び出し側でSTOPPED扱いとし、gloss自体の
# 再生成・手動修正を促す)ためのゲートとして使う。
#
# スコープは意図的にKey Phrase日本語gloss呼び出し経路に限定する
# (Full Story等の長尺ナレーションで「…」が正当な間・余韻として使われる
# 可能性まで一律に禁止しない)。「短く自然な日本語グロス」という既存の
# プロンプト指示自体がこの記法を想定しておらず、実例でも他の4件の
# gloss(例:「その場を立ち去る」)はいずれも項変数記法を使っていない
# ため、gloss文脈でこれらの記号が現れるケースは事実上すべて不良出力と
# みなしてよい。
_GLOSS_PLACEHOLDER_CHARS = ("〜", "～", "…")  # U+301C WAVE DASH / U+FF5E FULLWIDTH TILDE / U+2026 HORIZONTAL ELLIPSIS


def detect_gloss_placeholder_notation(text: str) -> dict:
    """Key Phrase日本語glossに、辞書的な項変数記法(「〜を…と結びつける」型)が
    残っていないかを検出する。文字列中のどの位置であっても対象記号が
    1つでも含まれていればhas_placeholder=Trueを返す(mid-string分は
    安全に自動削除できないため、呼び出し側でTTS呼び出し前にブロックする
    こと)。"""
    text = text or ""
    found = [ch for ch in _GLOSS_PLACEHOLDER_CHARS if ch in text]
    return {"has_placeholder": bool(found), "found_chars": found, "text": text}


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


# ============================================================
# E. 日本語短語segmentの発音ベース検証(ER-005-AUDIO-VALIDATION-ROBUSTNESS-02)
# ============================================================
# ER-005-AUDIO-WASTE-REDUCTION-01で発見した「内向化問題→内効果問題」
# 「行動上→公道上」等は、TTSの発音ミスではなく、短く文脈のない日本語
# 専門用語をAzure STTが同音の一般語へ書き起こしたものである可能性が
# 高いことを確認済み。これらは漢字表記こそ違うが、発音(読み)は同一
# であることをpykakasi(かな/ローマ字変換)で裏付けた上で、Key Phrase・
# glossのような「非常に短い」日本語segmentに限定してPHONETIC_MATCHを
# 導入する。長文Narration全体には適用しない(過剰な一般化を避ける)。
#
# 個別専門用語のwhitelist(「内向化→内効果ならPASS」のような1対1登録)
# は主方式にしない。一般的な読み変換で吸収できない特殊ケースは
# ASR_UNCERTAINへ分類し、既存audioを保持したままレビューへ回す
# (即TTS再生成しない)。

EXACT_MATCH_JA = "EXACT_MATCH"
NORMALIZED_MATCH_JA = "NORMALIZED_MATCH"
PHONETIC_MATCH_JA = "PHONETIC_MATCH"
TRUE_CONTENT_MISMATCH_JA = "TRUE_CONTENT_MISMATCH"
ASR_UNCERTAIN_JA = "ASR_UNCERTAIN"

# 発音一致とみなす下限(かな読み列のSequenceMatcher ratio)。1.0未満を
# 許容する余地は用意するが、今回はまず「完全一致のみPHONETIC_MATCH」
# という厳格な既定値から始める(過剰許容の禁止を優先)。中間の値は
# ASR_UNCERTAINとして人手レビューへ回す。
_PHONETIC_EXACT_THRESHOLD = 1.0
_PHONETIC_UNCERTAIN_THRESHOLD = 0.85

# 日本語のごく短いsegment(Key Phrase・gloss等)にのみ適用する上限文字数。
# 長文Narrationへの誤適用を防ぐガード。
JAPANESE_SHORT_SEGMENT_MAX_CHARS = 30

_JP_PUNCTUATION_RE = re.compile(r"[、。・「」『』\s]")
_NEGATION_MARKERS_JA = ("ない", "じゃない", "ではない", "でない", "せず", "未", "非", "無", "なく")


def _kakasi_reading(text: str) -> str:
    """日本語テキストをローマ字読みへ変換する(pykakasi、遅延import)。
    数字はアラビア数字のまま残るため、数字違いは読み比較でも検知できる。"""
    import pykakasi
    kks = pykakasi.kakasi()
    return "".join(item["hepburn"] for item in kks.convert(text))


_KANJI_COUNTER_DIGIT_MAP = {
    "一": "1", "二": "2", "三": "3", "四": "4", "五": "5",
    "六": "6", "七": "7", "八": "8", "九": "9",
}
# 助数詞「つ」の直前に来る単独漢数字(一〜九)だけを対象にした限定的な
# 同値正規化(ER-008-B1-POINT2-FACT-FIX-AND-JA-NUMERAL-NORMALIZATION-07)。
# 「一つ/二つ/…/九つ」は常に「かず+つ」の形で数量そのものを表し、
# _extract_numbers_ja()が単独漢数字を対象外にした理由(固有名詞的な語
# 内での偶然の一致、例:"京三")とは性質が異なる——「つ」という助数詞の
# 直前という文脈があるため、意味・読み・数量が完全に同じ表記ゆれとして
# 安全に判別できる。「二十」「二回」「二人」等、「つ」が続かない漢数字は
# 一切変換しない(それらは従来通り数字保護の対象外のまま=一般化しない)。
_KANJI_COUNTER_RE = re.compile(r"[一二三四五六七八九](?=つ)")


def normalize_kanji_counter_numerals_ja(text: str) -> str:
    """助数詞「つ」の直前の単独漢数字だけを算用数字へ変換する
    (例:"二つ"->"2つ"、"二十"や"二回"は対象外のまま変更しない)。"""
    if not text:
        return text
    return _KANJI_COUNTER_RE.sub(lambda m: _KANJI_COUNTER_DIGIT_MAP[m.group(0)], text)


def _extract_numbers_ja(text: str) -> set:
    """算用数字のみを抽出する。漢数字の単独文字(一〜九)は、短い固有名詞
    的な語(例: ASRの誤認識"京三"の"三")に偶然含まれることがあり、実際
    に数字を意味しない場合との判別が難しいため、今回の対象(Key Phrase・
    glossのような短いsegment、大きな漢数字表記の出現頻度が低い)では
    誤検知リスクの方が高いと判断し対象外とする(過剰な一般化を避ける、
    指示section11の方針)。canonical側が算用数字で数を表す場合(本
    プロジェクトのTTS入力正規化との整合)を主対象とする。ただし
    「一つ〜九つ」のような助数詞「つ」直前の漢数字だけは、文脈から
    数量であることが確実なため、normalize_kanji_counter_numerals_ja()で
    事前に算用数字へ揃えてから抽出する(ER-008-B1-POINT2-FACT-FIX-AND-
    JA-NUMERAL-NORMALIZATION-07)。"""
    text = normalize_kanji_counter_numerals_ja(text)
    return set(re.findall(r"\d+", text))


def _has_negation_ja(text: str) -> bool:
    return any(marker in text for marker in _NEGATION_MARKERS_JA)


def validate_japanese_short_segment_match(canonical_text: str, asr_text, asr_error: str = None) -> dict:
    """非常に短い日本語segment(Key Phrase・gloss等)専用の検証。長文
    Narrationには使わないこと(JAPANESE_SHORT_SEGMENT_MAX_CHARSを超える
    場合はNotImplementedErrorではなくASR_UNCERTAINへフォールバックし、
    呼び出し側が誤用に気付けるようreasonへ明記する)。

    判定順序(過剰正規化の禁止を優先、Bチームの既存方針を踏襲):
      1. asr_error/空文字 -> TRUE_CONTENT_MISMATCH(PASSにしない)
      2. 数字集合が異なる -> TRUE_CONTENT_MISMATCH(発音が近くても不採用)
      3. 否定語の有無が異なる -> TRUE_CONTENT_MISMATCH
      4. 文字列完全一致(句読点等の記号のみ除去) -> EXACT_MATCH
      5. 上記が同じでも表記だけ違う(将来の既存正規化拡張余地) -> NORMALIZED_MATCH
      6. 読み(ローマ字)が完全一致 -> PHONETIC_MATCH
      7. 読みの類似度が中間(0.85以上1.0未満) -> ASR_UNCERTAIN
      8. それ以外 -> TRUE_CONTENT_MISMATCH
    """
    result = {
        "canonical_text": canonical_text, "asr_text": asr_text,
    }
    if len(canonical_text or "") > JAPANESE_SHORT_SEGMENT_MAX_CHARS:
        result.update(verdict=ASR_UNCERTAIN_JA, passed=False,
                       reason=f"canonical_textが{JAPANESE_SHORT_SEGMENT_MAX_CHARS}文字を超えており、"
                              "この関数の対象(非常に短いsegment)外です。誤用の可能性があります。")
        return result
    if asr_error:
        result.update(verdict=TRUE_CONTENT_MISMATCH_JA, passed=False,
                       reason=f"ASR/API error — PASS禁止: {asr_error}")
        return result
    if not asr_text:
        result.update(verdict=TRUE_CONTENT_MISMATCH_JA, passed=False,
                       reason="ASR text is empty/None — PASS禁止")
        return result

    c_norm = _JP_PUNCTUATION_RE.sub("", canonical_text)
    a_norm = _JP_PUNCTUATION_RE.sub("", asr_text)
    # 助数詞「つ」直前の漢数字(一〜九)だけを算用数字へ揃える。kakasiは
    # "2つ"を"futatsu"ではなく"2tsu"と読むため、数字セット比較だけでなく
    # ここで文字列自体を揃えておかないと、後段の完全一致判定・読み比較の
    # 両方を素通りしてしまう(ER-008-B1-POINT2-FACT-FIX-AND-JA-NUMERAL-
    # NORMALIZATION-07)。
    c_norm = normalize_kanji_counter_numerals_ja(c_norm)
    a_norm = normalize_kanji_counter_numerals_ja(a_norm)

    c_numbers = _extract_numbers_ja(c_norm)
    a_numbers = _extract_numbers_ja(a_norm)
    if c_numbers != a_numbers:
        result.update(verdict=TRUE_CONTENT_MISMATCH_JA, passed=False,
                       reason=f"数字が一致しません(canonical={c_numbers or 'なし'}, asr={a_numbers or 'なし'})")
        return result

    if _has_negation_ja(c_norm) != _has_negation_ja(a_norm):
        result.update(verdict=TRUE_CONTENT_MISMATCH_JA, passed=False,
                       reason="否定表現の有無が一致しません")
        return result

    if c_norm == a_norm:
        result.update(verdict=EXACT_MATCH_JA, passed=True, reason="記号除去後に完全一致")
        return result

    c_reading = _kakasi_reading(c_norm)
    a_reading = _kakasi_reading(a_norm)
    result["canonical_reading"] = c_reading
    result["asr_reading"] = a_reading

    if c_reading == a_reading:
        result.update(verdict=PHONETIC_MATCH_JA, passed=True,
                       reason="漢字表記は異なるが、読み(発音)が完全一致")
        return result

    import difflib
    ratio = difflib.SequenceMatcher(None, c_reading, a_reading).ratio()
    result["reading_similarity_ratio"] = round(ratio, 3)
    if ratio >= _PHONETIC_UNCERTAIN_THRESHOLD:
        result.update(verdict=ASR_UNCERTAIN_JA, passed=False,
                       reason=f"読みが近い(類似度{ratio:.2f})が完全一致ではないため、機械的にはPASSと"
                              "断定しない。既存audioを保持したままレビュー対象とすることを推奨します。")
        return result

    result.update(verdict=TRUE_CONTENT_MISMATCH_JA, passed=False,
                   reason=f"読みが大きく異なります(類似度{ratio:.2f})")
    return result


# ============================================================
# F. 日本語canonical textに残る外来語・制作内部ラベルの検出
# ============================================================
# ER-009-JA-FOREIGN-TOKEN-GATE-01(2026-08-26)で発見: No.4(pool_n4_
# supermarket)のA2 comment_2のJapanese canonical textに、制作内部の
# 章番号ラベル「Part 1」がリスナー向け日本語のまま残っていた
# ("Part 1では、店が売り場の配置を変え…")。TTS自体は正しく「パート1」と
# 発話していたが、Japanese ASRは文中の英字表記をローマ字のまま書き
# 起こすことがほぼ無いため、canonical text側の「Part 1」とASR書き起こし
# 「パート1」が構造的に一致し得ず、14回の試行(旧STOPPED時12回+今回2回)
# 全てでHuman Review待ち(ASR_VALIDATION_UNCERTAIN)へ回っていた。
#
# 根本原因はASR/TTS側の技術的不具合ではなく、「制作都合の内部ラベルを
# リスナー向け日本語にそのまま残した」という編集上の問題である。本節は、
# 日本語canonical textに残る英字・数字混じりのトークンを、TTSへ渡す前に
# 検出し、以下4分類のいずれかへ振り分ける(OPEN-72/ER-008-DIRECTIONAL-
# FACT-PRECHECK-08と同じ「rule-based・軽量・確信が持てない場合は無理に
# 自動判定しない」思想を踏襲する。新規LLM呼び出しは使わない):
#
#   1. NEEDS_JAPANESE_PARAPHRASE: 「Part 1」「Point 2」等、制作内部の
#      segment名・章番号ラベルがそのまま残っているもの。自然な日本語
#      (例:「物語の前半」)へ言い換えるべき
#   2. READING_DICTIONARY: 定着した略語・固有名詞で、カタカナ読みが
#      既に辞書(DEFAULT_JA_READING_DICTIONARY)に登録されているもの
#      (機械的に対応可)
#   3. ENGLISH_PRONUNCIATION: その記事のKey Phrase英語表現(used_form)
#      そのものが含まれており、意図的に英語のまま発話させるべき箇所
#      (呼び出し側がknown_key_phrase_termsを渡した場合のみ判定できる)
#   4. HUMAN_REVIEW: 上記いずれにも機械的な確信を持って分類できない
#      もの。既存のASR Cascade(human_review_queue.jsonl)と同じ思想で、
#      無理に自動判定せず明示的にレビュー待ちとして記録する
#
# 過検知でProduction全体を止めないため、TTS呼び出し自体をブロックする
# のはカテゴリ4(HUMAN_REVIEW)のみに限定する(既存のdetect_gloss_
# placeholder_notation()と同じ「ブロック対象は確信が持てるケースに限定
# する」設計)。カテゴリ1〜3は検出・記録に留め、生成そのものは止めない。
FOREIGN_TOKEN_NEEDS_PARAPHRASE = "NEEDS_JAPANESE_PARAPHRASE"
FOREIGN_TOKEN_READING_DICTIONARY = "READING_DICTIONARY"
FOREIGN_TOKEN_ENGLISH_PRONUNCIATION = "ENGLISH_PRONUNCIATION"
FOREIGN_TOKEN_HUMAN_REVIEW = "HUMAN_REVIEW"

# 「英単語+数字/ローマ数字」の形をした制作内部ラベル。ASCII英数字の
# 前後だけを見るnegative lookaround(Unicode \bは漢字/かなも「単語文字」
# とみなすため使えない、というPython re の既知の落とし穴を回避する)。
_INTERNAL_LABEL_WORDS = ("Part", "Point", "Comment", "Section", "Step", "Chapter")
# ER-008-N8-QA-CONTENT-SPEED-HARDENING-18: 数字/ローマ数字だけでなく、
# "Part One"/"Point Two"のような英単語表記の序数もラベルとして検出する
# (元々は"Part 1"等の数字表記のみを対象にしていたが、CURRENT_SPECの
# 見出し命名規則自体が"Point One"等の英単語表記も禁止していることと
# 平仄を合わせる。日本語版・英語版の両方でこの拡張が有効になる)。
_INTERNAL_LABEL_ORDINAL_WORDS = ("One", "Two", "Three", "Four", "Five",
                                  "First", "Second", "Third", "Fourth", "Fifth")
_INTERNAL_LABEL_RE = re.compile(
    r"(?<![A-Za-z0-9])(?:" + "|".join(_INTERNAL_LABEL_WORDS) + r")\s*(?:[0-9]+|[IVXivx]+|"
    + "|".join(_INTERNAL_LABEL_ORDINAL_WORDS) + r")(?![A-Za-z0-9])")

# 日本語文中に残るLatin文字トークン(英単語・略語)を検出する。数字単独
# ("2026"等、既存のtts_safe_number_words_en等で扱う体系)は対象外とし、
# 英字を含むトークンのみを対象にする(過検知を避ける、モジュール全体の
# 「過剰な一般化を避ける」方針を踏襲)。
_LATIN_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9\-\.']*")

# 定着した略語・固有名詞の小規模な読み方辞書(機械的に対応可能なものだけ。
# 大規模語彙辞書は作らない=過剰な一般化を避ける)。キーは小文字で比較する。
DEFAULT_JA_READING_DICTIONARY = {
    "cm": "センチ", "kg": "キログラム", "km": "キロメートル", "kcal": "キロカロリー",
    "ceo": "シーイーオー", "wi-fi": "ワイファイ", "cafe": "カフェ",
}


def _spans_overlap(span: tuple, other_spans: list) -> bool:
    s, e = span
    return any(s < e2 and s2 < e for s2, e2 in other_spans)


def classify_foreign_tokens_in_japanese_text(text: str, known_key_phrase_terms=None,
                                              reading_dictionary: dict = None) -> list:
    """日本語canonical text(TTSへ渡す直前のもの)に残る英字・数字混じりの
    トークンを検出し、上記4分類のいずれかへ振り分ける。

    known_key_phrase_terms(既定None): その記事のKey Phrase英語表現
    (used_form)のiterableを渡すと、canonical text中にその表現がそのまま
    含まれる箇所を、意図的な英語発話(ENGLISH_PRONUNCIATION)として扱う。
    渡さない場合はこの分類は行われない(該当箇所は他の分類・HUMAN_REVIEW
    のいずれかへ回る)。

    reading_dictionary(既定None): DEFAULT_JA_READING_DICTIONARYへ追加/
    上書きする呼び出し側固有の読み方辞書(小文字キー)。

    戻り値: 検出0件ならば空list。各検出は
    {"token": str, "category": str, "reason": str} の形の辞書。
    判定順序(重複検出を避けるため、先に確定した範囲は後段の判定から除外
    する): 1) 制作内部ラベル -> 2) Key Phrase英語表現 -> 3) 読み方辞書/
    HUMAN_REVIEW(残りのLatin文字トークン)。
    """
    text = text or ""
    dictionary = dict(DEFAULT_JA_READING_DICTIONARY)
    if reading_dictionary:
        dictionary.update({k.lower(): v for k, v in reading_dictionary.items()})
    kp_terms = sorted({t for t in (known_key_phrase_terms or []) if t}, key=len, reverse=True)

    findings = []
    claimed_spans = []

    # 1) 制作内部ラベル(Part 1等)を最優先で検出する
    for m in _INTERNAL_LABEL_RE.finditer(text):
        findings.append({
            "token": m.group(0), "category": FOREIGN_TOKEN_NEEDS_PARAPHRASE,
            "reason": f"制作内部のsegment名/章番号ラベルがリスナー向け日本語に残っています: {m.group(0)!r}。"
                      "リスナーが単独で理解できる自然な日本語(例:「物語の前半」)へ言い換えてください。",
        })
        claimed_spans.append(m.span())

    # 2) その記事のKey Phrase英語表現がそのまま含まれる場合は意図的な英語発話
    lower_text = text.lower()
    for term in kp_terms:
        term_lower = term.lower()
        start = 0
        while True:
            idx = lower_text.find(term_lower, start)
            if idx == -1:
                break
            span = (idx, idx + len(term_lower))
            if not _spans_overlap(span, claimed_spans):
                findings.append({
                    "token": text[idx:idx + len(term_lower)], "category": FOREIGN_TOKEN_ENGLISH_PRONUNCIATION,
                    "reason": f"この記事のKey Phrase英語表現そのものであり、意図的に英語で発話させる箇所です: "
                              f"{text[idx:idx + len(term_lower)]!r}",
                })
                claimed_spans.append(span)
            start = idx + 1

    # 3) 残りのLatin文字トークンを、読み方辞書 or HUMAN_REVIEWへ振り分ける
    for m in _LATIN_TOKEN_RE.finditer(text):
        span = m.span()
        if _spans_overlap(span, claimed_spans):
            continue
        token = m.group(0)
        if token.lower() in dictionary:
            findings.append({
                "token": token, "category": FOREIGN_TOKEN_READING_DICTIONARY,
                "reason": f"読み方辞書に登録済みの表記です(読み: {dictionary[token.lower()]})",
            })
        else:
            findings.append({
                "token": token, "category": FOREIGN_TOKEN_HUMAN_REVIEW,
                "reason": f"日本語canonical text中の未対応の英字/記号表記です: {token!r}。"
                          "機械的に「言い換え」「辞書対応」「意図的な英語発話」のいずれとも判定できないため、"
                          "人による確認が必要です。",
            })
        claimed_spans.append(span)

    return findings


def foreign_token_gate_requires_stop(findings: list) -> bool:
    """カテゴリ4(HUMAN_REVIEW)が1件でもあれば、TTS呼び出し自体を
    ブロックすべきと判定する。カテゴリ1〜3だけでは生成をブロックしない。"""
    return any(f.get("category") == FOREIGN_TOKEN_HUMAN_REVIEW for f in (findings or []))


FOREIGN_TOKEN_HUMAN_REVIEW_LOG_PATH = "er009_output/ja_foreign_token_gate_01/human_review_queue.jsonl"


# ============================================================
# ER-008-N8-QA-CONTENT-SPEED-HARDENING-18: 英語canonical textの
# 制作内部ラベル検出(日本語版[上記]の英語ミラー)
# ============================================================
# No.8のB1 Comment 2で、"In Part 2, what is American Airlines doing..."
# という制作内部の構造ラベルがリスナー向け英語にそのまま出力される事故が
# 発生した。上記の日本語版ガード(classify_foreign_tokens_in_japanese_
# text)は日本語canonical text専用で、英語canonical textは対象外だった
# ため検知できなかった。根本原因(Comment生成promptのcontextにPart 1/
# Part 2という内部ラベルがそのまま含まれていたこと)はprompt側で別途
# 修正済み(er003_v1_n3_01_scaffold_generate.py)だが、再発を防ぐ第二の
# 防御線として、英語版の同種ガードを新設する。日本語版と同じ
# _INTERNAL_LABEL_RE(Part/Point/Comment/Section/Step/Chapter + 数字/
# ローマ数字)をそのまま再利用する(新しい正規表現・新規LLM呼び出しは
# 追加しない、追加コスト0円)。日本語版と異なり、英語canonical textには
# 「意図的な英語発話」のような救済分類が無いため、1件でも検出されれば
# 無条件でブロックする(過検知リスクより、内部ラベル露出の実害の方が
# 重いと判断)。
def detect_internal_production_labels_in_english_text(text: str) -> list:
    """英語canonical text(TTSへ渡す直前のもの)に、制作内部のsegment名/
    章番号ラベル(Part 1・Point 2・Comment 3・Section 1等)がそのまま
    残っていないかを検出する。戻り値: 検出0件ならば空list、各検出は
    {"token": str, "reason": str} の形の辞書。"""
    text = text or ""
    findings = []
    for m in _INTERNAL_LABEL_RE.finditer(text):
        findings.append({
            "token": m.group(0),
            "reason": f"制作内部のsegment名/章番号ラベルがリスナー向け英語に残っています: {m.group(0)!r}。"
                      "リスナーが単独で理解できる表現(例:\"the first half\"/\"what we just heard\")へ"
                      "言い換えてください。",
        })
    return findings


def english_internal_label_gate_requires_stop(findings: list) -> bool:
    """1件でも検出されればTTS呼び出し自体をブロックすべきと判定する
    (英語版には日本語版のような救済分類[ENGLISH_PRONUNCIATION等]が
    無いため、日本語版より単純な全件ブロック設計)。"""
    return bool(findings)


def log_foreign_token_human_review(canonical_text: str, wav_path: str, findings: list) -> None:
    """既存のASR Cascade human_review_queue.jsonl(er007_ja_secondary_
    asr_01.py::_log_human_review)と同じ思想・形式で、HUMAN_REVIEW判定を
    記録する(TTS呼び出し自体は行わない)。"""
    os.makedirs(os.path.dirname(FOREIGN_TOKEN_HUMAN_REVIEW_LOG_PATH), exist_ok=True)
    record = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "canonical_text": canonical_text, "wav_path": wav_path, "findings": findings,
    }
    with open(FOREIGN_TOKEN_HUMAN_REVIEW_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
