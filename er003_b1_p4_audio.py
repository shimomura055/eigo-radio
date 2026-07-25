# ============================================================
# er003_b1_p4_audio.py
# ER-003-B1-P4: Pattern A全文＋B1本文・通し試聴版生成
# ============================================================
# 短尺検証(P3W〜P3Z)で確定した方式を、ER-003-B1-P2でユーザーが採用した
# Pattern A(Story/Drama)全文と、ER-003-B1-P1でACCEPT済みのA01 B1本文へ
# 適用する。Pattern A・B1本文のsource(語句・順序・日本語訳・英語表現)
# は一切変更しない。5つの英語used formをTTS用一時カタカナマーカーへ
# 置換し、MFAで区間を特定し、対応する英語音声へ置換する。
#
# 再利用するもの(再実装しない):
#   - er002_common.build_style_prefix/build_narration_plan/assemble_audio/
#     _call_tts_with_retry/pcm_to_wav_bytes/pcm_bytes_to_float_mono/
#     write_wav_float/read_wav_float/measure_metrics/apply_dynamics3_once/
#     SAMPLE_RATE/SECTION_JOIN_PAUSE_SECONDS/DYNAMICS3_PARAMS
#   - er002_gemini_client.make_tts_call_fn(voice_name)
#   - er003_b1_p3r_audio.VOICE_NAME/load_pattern_a_text/load_b1_article_text/
#     parse_b1_markdown_to_script/PATTERN_A_SOURCE_PATH/B1_ARTICLE_SOURCE_PATH
#   - er003_b1_p3u_audio.find_speech_bounds/trim_english_keyword_silence
#   - er003_b1_p3w_audio.MFA_*/mfa_environment_available/run_mfa_align/
#     parse_textgrid_words_tier
#   - er003_b1_p3y_audio.build_japanese_style_prefix
#   - er003_b1_p3z_audio.adjust_trailing_silence/adjust_leading_silence
#
# 新規に追加するのは、(1) 5マーカーのカタカナ対応表とPattern Aへの一括
# 置換、(2) 1発話内で複数マーカーを順序どおりに探すfind_all_marker_spans
# 、(3) マーカー区間ごとの日本語segment抽出、(4) 複数文にまたがる長尺
# 音声向けのAzure STT連続認識ラッパー、の4つのみ。
#
# (4)について: p3u.get_word_timestamps_via_azure_sttは
# recognize_once()を使うため、単一の短い発話(P3T/P3U/P3W/P3Y)では
# 問題なかったが、本ステージのPreview全文(複数文・40秒超)では最初の
# 1文しか認識されないことが実機で判明した。この問題を修正するための
# 連続認識版を、p3u側は変更せず本モジュールへ新規追加する。

from __future__ import annotations

import json
import os
import re
import time

import er002_common as common
import er003_b1_p3r_audio as p3r
import er003_b1_p3u_audio as p3u
import er003_b1_p3w_audio as p3w
import er003_b1_p3y_audio as p3y
import er003_b1_p3z_audio as p3z

ARTICLE_ID = "A01"
VOICE_NAME = p3r.VOICE_NAME  # "Aoede"

PATTERN_A_SOURCE_PATH = p3r.PATTERN_A_SOURCE_PATH
B1_ARTICLE_SOURCE_PATH = p3r.B1_ARTICLE_SOURCE_PATH
KEYWORDS_SOURCE_PATH = "er003_output/b1_p2/A01/keywords_selected.json"

load_pattern_a_text = p3r.load_pattern_a_text
load_b1_article_text = p3r.load_b1_article_text
parse_b1_markdown_to_script = p3r.parse_b1_markdown_to_script

MAX_TTS_TECHNICAL_RETRY = 1

# 日本語Preview用instruction(P3Yで日本語生成に成功した言語指定へ差替済み)。
JAPANESE_STYLE_PREFIX = p3y.build_japanese_style_prefix()
# 英語Key Phrase・B1本文用instruction(B2までに採用済み、無変更)。
ENGLISH_STYLE_PREFIX = common.build_style_prefix()

# 採用済みの実効間隔(P3Zの検証を踏まえてユーザーが確定)。
GAP_BEFORE_TARGET_SECONDS = 0.40
GAP_AFTER_TARGET_SECONDS = 0.30
GAP_TOLERANCE_SECONDS = 0.03

# 英語Key Phrase音声のtrim安全余白(P3Uで確立済みの値、そのまま踏襲)。
EN_TRIM_SAFETY_MARGIN_SECONDS = p3u.EN_TRIM_SAFETY_MARGIN_SECONDS  # 0.08

EXISTING_SHOT_ON_TARGET_PATH = "er003_output/b1_p3u/A01/components/en_shot_on_target_trimmed.wav"


def build_japanese_style_prefix() -> str:
    return JAPANESE_STYLE_PREFIX


def build_english_style_prefix() -> str:
    return ENGLISH_STYLE_PREFIX


def build_tts_prompt(text: str, style_prefix: str) -> str:
    return style_prefix + text


# ============================================================
# マーカーmap: Pattern A内の5 used formを、出現順にカタカナマーカーへ
# 対応付ける。カタカナは各used formの実際の語形(canonical formではない)
# に基づいて作成する(例: "take players off"の複数形、"a narrow lead"の
# 冠詞、"close the door to the final"の全文)。
# ============================================================
# 実機のMFA(japanese_mfa)tokenizerで、上記カタカナマーカーがどう分割
# 認識されるかを事前確認済み(mfa_tool経由のtokenizer実行結果)。
# find_all_marker_spansへ渡すtoken列はこの実測結果を使う。
_TOKEN_SEQUENCE_BY_USED_FORM = {
    "shot on target": ("ショット", "オン", "ターゲット"),
    "take players off": ("テイク", "プレイヤーズ", "オフ"),
    "a narrow lead": ("ア", "ナロー", "リード"),
    "close the door to the final": ("クローズ", "ザ", "ドア", "トゥ", "ザ", "ファイナル"),
    "stoppage time": ("ストッページ", "タイム"),
}


def marker_specs_from_marker_map(marker_map: list[dict]) -> list[dict]:
    """marker_map(出現順)から、find_all_marker_spansへ渡すmarker_specs
    (marker_id・token_sequence)を組み立てる。"""
    specs = []
    for e in marker_map:
        seq = _TOKEN_SEQUENCE_BY_USED_FORM.get(e["used_form"])
        if seq is None:
            raise ValueError(f"used_form{e['used_form']!r}に対応するtoken列が未定義です")
        specs.append({
            "marker_id": f"rank{e['rank']}_{e['canonical_english'].replace(' ', '_')}",
            "used_form": e["used_form"],
            "token_sequence": seq,
        })
    return specs


_KATAKANA_BY_USED_FORM = {
    "shot on target": "ショット・オン・ターゲット",
    "take players off": "テイク・プレイヤーズ・オフ",
    "a narrow lead": "ア・ナロー・リード",
    "close the door to the final": "クローズ・ザ・ドア・トゥ・ザ・ファイナル",
    "stoppage time": "ストッページ・タイム",
}


def load_keywords_selected(path: str = KEYWORDS_SOURCE_PATH) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build_marker_map(pattern_a_text: str, used_forms: list[dict]) -> list[dict]:
    """Pattern A本文内でのused_formの出現位置(文字インデックス)順に
    マーカーmapを構築する。各used_formがPattern A内にちょうど1回だけ
    現れることを確認する(0回・複数回は例外)。"""
    entries = []
    for uf in used_forms:
        used_form = uf["used_form"]
        count = pattern_a_text.count(used_form)
        if count != 1:
            raise ValueError(f"used_form{used_form!r}がPattern A内に{count}回出現します(1回である必要があります)")
        katakana = _KATAKANA_BY_USED_FORM.get(used_form)
        if katakana is None:
            raise ValueError(f"used_form{used_form!r}に対応するカタカナマーカーが未定義です")
        index = pattern_a_text.index(used_form)
        entries.append({
            "rank": uf["rank"],
            "canonical_english": uf["canonical_english"],
            "used_form": used_form,
            "japanese_gloss_used": uf["japanese_gloss_used"],
            "katakana_marker": katakana,
            "text_index": index,
        })
    entries.sort(key=lambda e: e["text_index"])
    for order, e in enumerate(entries, start=1):
        e["appearance_order"] = order
    return entries


def build_tts_script_with_markers(pattern_a_text: str, marker_map: list[dict]) -> str:
    """marker_map(出現順)の各used_formを、対応するカタカナマーカーへ
    1回ずつ置換する。それ以外の日本語・助詞・句読点は一切変更しない。
    置換後にmarkerを元のused_formへ戻すと、元のPattern Aテキストへ
    完全に一致することを確認する(安全性チェック)。"""
    script = pattern_a_text
    for e in marker_map:
        if e["used_form"] not in script:
            raise ValueError(f"used_form{e['used_form']!r}が置換時点のscript内に見つかりません")
        script = script.replace(e["used_form"], e["katakana_marker"], 1)

    reconstructed = script
    for e in marker_map:
        reconstructed = reconstructed.replace(e["katakana_marker"], e["used_form"], 1)
    if reconstructed != pattern_a_text:
        raise ValueError("マーカー置換の可逆性チェックに失敗しました(元のPattern Aへ復元できません)")

    return script


def get_full_text_via_azure_stt_continuous(
    wav_path: str, language: str = "ja-JP", timeout_seconds: float = 90.0,
) -> tuple[str | None, str | None]:
    """複数文・長尺の音声全体を、Azureの連続認識(start_continuous_
    recognition)で最初から最後まで認識し、認識された全セグメントを
    結合したテキストを返す。recognize_once()は最初の1文しか認識しない
    ため、本ステージのPreview全文確認には使えない(実機で確認済み)。
    境界決定には使わず、内容(日本語かどうか・マーカーが揃っているか)
    の診断用途のみに使う。"""
    if not os.path.exists(wav_path):
        return None, f"音声ファイルが見つかりません: {wav_path}"

    try:
        from dotenv import load_dotenv
        import azure.cognitiveservices.speech as speechsdk
    except ImportError as exc:
        return None, f"Azure Speech SDKの読み込みに失敗しました: {exc}"

    load_dotenv()
    speech_key = os.getenv("SPEECH_KEY")
    speech_region = os.getenv("SPEECH_REGION")
    if not speech_key or not speech_region:
        return None, "SPEECH_KEY/SPEECH_REGIONが.envに設定されていません"

    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
    speech_config.speech_recognition_language = language
    audio_config = speechsdk.audio.AudioConfig(filename=wav_path)
    recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    segments = []
    done = {"flag": False, "reason": None}

    def on_recognized(evt):
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            segments.append(evt.result.text)

    def on_stopped(evt):
        done["flag"] = True
        done["reason"] = str(evt)

    recognizer.recognized.connect(on_recognized)
    recognizer.session_stopped.connect(on_stopped)
    recognizer.canceled.connect(on_stopped)

    recognizer.start_continuous_recognition()
    start = time.time()
    while not done["flag"] and (time.time() - start) < timeout_seconds:
        time.sleep(0.5)
    recognizer.stop_continuous_recognition()

    if not done["flag"]:
        return None, f"連続認識がtimeout({timeout_seconds}秒)内に完了しませんでした"

    return "".join(segments), None


# ============================================================
# 生成直後の日本語内容確認(MFAへ進む前のゲート、P3Yのcheck_ja_content
# を5マーカー向けに一般化)
# ============================================================
_PUNCTUATION_TO_STRIP = "・、。,.!?！？　 \n\t"


def _strip_punctuation(text: str) -> str:
    return "".join(ch for ch in text if ch not in _PUNCTUATION_TO_STRIP)


def check_ja_content(recognized_text_ja: str, marker_map: list[dict]) -> dict:
    ja_char_count = sum(
        1 for ch in recognized_text_ja
        if ("぀" <= ch <= "ゟ") or ("゠" <= ch <= "ヿ") or ("一" <= ch <= "鿿")
    )
    ja_char_ratio = ja_char_count / len(recognized_text_ja) if recognized_text_ja else 0.0
    is_japanese = ja_char_ratio >= 0.5

    # ASRの句読点復元(punctuation restoration)により、マーカー内部にも
    # 読点が挿入されることがある(実機で確認済み: 「ショット、オンター
    # ゲット」)。境界決定には使わないため、句読点・中黒を除去した文字列
    # 同士で照合する(緩い一致判定でよい)。
    stripped_text = _strip_punctuation(recognized_text_ja)

    marker_checks = []
    all_markers_present_once = True
    for e in marker_map:
        marker_stripped = _strip_punctuation(e["katakana_marker"])
        count = stripped_text.count(marker_stripped)
        present_once = count == 1
        if not present_once:
            all_markers_present_once = False
        marker_checks.append({
            "katakana_marker": e["katakana_marker"],
            "count_in_stripped_text": count,
            "present_once": present_once,
        })

    return {
        "ja_char_count": ja_char_count,
        "ja_char_ratio": round(ja_char_ratio, 4),
        "is_japanese": is_japanese,
        "marker_checks": marker_checks,
        "all_markers_present_once": all_markers_present_once,
    }


# ============================================================
# MFA: 1発話内の複数マーカーを、出現順・重複なしで探す
# ============================================================
def find_all_marker_spans(words: list[dict], marker_specs: list[dict]) -> tuple[list[dict], list[str]]:
    """marker_specs: [{'marker_id', 'token_sequence'}, ...](期待される
    出現順)。各マーカーについて、直前に見つかったマーカーの終了位置
    より後ろだけを探索することで、順序維持・重複なしを保証する。
    無音長は一切使わず、token列の一致のみを根拠にする。"""
    non_empty = [(i, w["text"]) for i, w in enumerate(words) if w["text"] != ""]
    texts = [t for _, t in non_empty]

    results = []
    errors = []
    search_start = 0

    for spec in marker_specs:
        seq = tuple(spec["token_sequence"])
        n = len(seq)
        matches = [
            i for i in range(search_start, len(texts) - n + 1)
            if tuple(texts[i:i + n]) == seq
        ]
        if not matches:
            errors.append(f"{spec['marker_id']}: token列{seq}が(search_start={search_start}以降で)見つかりません")
            results.append(None)
            continue

        ne_first = matches[0]
        ne_last = ne_first + n - 1
        if ne_first == 0 or ne_last == len(non_empty) - 1:
            errors.append(f"{spec['marker_id']}: 前後に単語が存在せず直前・直後token順を確認できません")
            results.append(None)
            continue

        prev_idx = non_empty[ne_first - 1][0]
        next_idx = non_empty[ne_last + 1][0]
        first_idx = non_empty[ne_first][0]
        last_idx = non_empty[ne_last][0]

        results.append({
            "marker_id": spec["marker_id"],
            "token_sequence": list(seq),
            "start_seconds": words[first_idx]["xmin"],
            "end_seconds": words[last_idx]["xmax"],
            "duration_seconds": round(words[last_idx]["xmax"] - words[first_idx]["xmin"], 4),
            "preceding_token": words[prev_idx]["text"],
            "preceding_start_seconds": words[prev_idx]["xmin"],
            "preceding_end_seconds": words[prev_idx]["xmax"],
            "following_token": words[next_idx]["text"],
            "following_start_seconds": words[next_idx]["xmin"],
            "following_end_seconds": words[next_idx]["xmax"],
        })
        search_start = ne_last + 1

    return results, errors


def spans_are_monotonic_non_overlapping(spans: list[dict]) -> bool:
    for i in range(1, len(spans)):
        if spans[i]["start_seconds"] < spans[i - 1]["end_seconds"]:
            return False
    return all(s["end_seconds"] > s["start_seconds"] for s in spans)
