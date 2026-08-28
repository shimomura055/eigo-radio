# ============================================================
# er008_disfluency_qa_18.py
# ER-008-N8-QA-CONTENT-SPEED-HARDENING-18: 短いsegmentのpartial
# repetition/false start検知(disfluency QA)
# ============================================================
# 背景: No.8のA2 Key Phrase 2("uneven choice")で、TTSクリップ内に
# "uneven, uneven choice"という部分的な言い直し(partial repetition)が
# 発生していたが、Production ASR(OpenAI/Azure、素の一致判定用)は
# これを"Uneven choice."と平滑化して書き起こし、既存Validatorを
# すり抜けた(ASR smoothing問題)。
#
# 対策: 既存のProduction ASR呼び出しとは別に、無料でローカル実行できる
# faster-whisper(オープンソース、追加の有料API呼び出しではない、
# ネットワーク経由の課金無し)による word-level timestamp付き文字起こしを
# 短い高リスクsegment(Key Phrase英語/Point見出し/Preview・In One Line等)
# に限定して実行し、隣接する同一単語の繰り返しを機械的に検知する。
#
# 既知の限界: この方式は「同一単語がまるごと繰り返される」パターンの
# 検知に限られる。B1 Previewで報告された"Wh, why does..."のような
# 「単語の一部分だけの言い直し(partial word)」は、word-level ASRの
# 性質上、独立したtokenとして現れず隣接語へ吸収されるため、この方式
# では原理的に検知できない(本ファイルのdocstringで明記し、過信を防ぐ)。
#
# コスト: モデルは初回のみHugging Face Hubからダウンロード(無料、
# ローカルにキャッシュされ以降は再ダウンロードなし)。呼び出しごとの
# 追加課金は無し(ローカルCPU計算のみ)。処理時間は短いsegment(2〜30秒)
# 1件につきCPUで数秒程度。

from __future__ import annotations

import re
from typing import Optional

_MODEL_CACHE: dict = {}


def _get_model(model_size: str = "small"):
    if model_size not in _MODEL_CACHE:
        from faster_whisper import WhisperModel
        _MODEL_CACHE[model_size] = WhisperModel(model_size, device="cpu", compute_type="int8")
    return _MODEL_CACHE[model_size]


def _normalize_token(word: str) -> str:
    return re.sub(r"[.,!?\"'…]", "", word.strip().lower())


def transcribe_verbatim(wav_path: str, language: str = "en", model_size: str = "small") -> list:
    """word-level timestamp付きでverbatim寄りの文字起こしを行う(ローカル
    実行、追加API課金なし)。languageは必ず明示指定すること(auto-detectは
    日本語音声で誤検知を起こすことをNo.8データで確認済み)。"""
    model = _get_model(model_size)
    segments, _info = model.transcribe(
        wav_path, word_timestamps=True, language=language,
        condition_on_previous_text=False, vad_filter=False)
    words = []
    for seg in segments:
        for w in seg.words:
            words.append({"text": w.word, "start": w.start, "end": w.end, "probability": w.probability})
    return words


def detect_adjacent_word_repetition(words: list) -> list:
    """隣接する同一token(正規化後)の繰り返しを検知する。全文が完全一致
    する2 word以上のフレーズ反復ではなく、1 word単位の直接隣接繰り返し
    のみを対象とする(false positiveを避けるため、意図的に狭い定義)。"""
    repeats = []
    normalized = [_normalize_token(w["text"]) for w in words]
    for i in range(1, len(normalized)):
        if normalized[i] and normalized[i] == normalized[i - 1]:
            repeats.append({
                "token": normalized[i],
                "first": words[i - 1], "second": words[i],
            })
    return repeats


def check_segment_for_disfluency(wav_path: str, language: str = "en", model_size: str = "small") -> dict:
    """短いsegment 1件をverbatim再チェックし、隣接単語repetitionが
    あればflagged=Trueを返す。呼び出し側はflagged=Trueの場合、既存の
    Human Review経路へ回すこと(このモジュール自体は自動修正・自動retry
    を行わない、安全側)。"""
    words = transcribe_verbatim(wav_path, language=language, model_size=model_size)
    repeats = detect_adjacent_word_repetition(words)
    return {
        "flagged": bool(repeats),
        "repeats": repeats,
        "word_count": len(words),
        "transcript": " ".join(w["text"] for w in words).strip(),
        "method": f"faster_whisper_{model_size}_local_verbatim",
    }


# ============================================================
# ER-008-N8-PRODUCTION-WIRING-AND-FOLLOWUP-19: Production配線用ゲート
# ============================================================
# 既存のProduction ASR verified判定(内容+長さ)に、このdisfluency QAを
# 追加でANDするだけの薄いラッパー。呼び出し側(各generate系関数の
# retry loop内)は、既存のverified変数をこの関数の戻り値で置き換える
# だけでよい。enabled=Falseの場合は追加コスト・追加処理を一切発生させず
# 元のverifiedをそのまま返す(対象外segmentへの影響ゼロを保証する)。
# flag時は「TTS再生成→通常ASR+disfluency QA再判定」という既存のretry
# loopにそのまま合流させる(verified=Falseとして返すだけで、呼び出し元の
# 既存loopが次のattemptで自動的にTTSを取り直す。上限到達後の
# status="STOPPED"は、既存のer011_human_review_lock_01.guarded_generate
# デコレータがrecord_outcome()でHUMAN_REVIEW_REQUIREDへ自動遷移させるため、
# ここで新たにHuman Review経路を実装する必要はない)。
def apply_disfluency_gate(verified: bool, out_path: str, language: str = "en",
                            enabled: bool = False, model_size: str = "small") -> dict:
    if not enabled or not verified:
        return {"verified": verified, "disfluency_checked": False, "disfluency_evidence": None}
    evidence = check_segment_for_disfluency(out_path, language=language, model_size=model_size)
    return {
        "verified": verified and not evidence["flagged"],
        "disfluency_checked": True,
        "disfluency_evidence": evidence,
    }
