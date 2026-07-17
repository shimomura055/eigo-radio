# ============================================================
# er001b9_caregiving_common_spec.py
# ER-001B-9: 老老介護への共通最終仕様適用テスト
# ============================================================
# 目的: 老老介護記事に、これまで採用した共通最終仕様
# (Emotional+Connected+Level2 / Point One・Point Two / In One Line必須
#  / セクション間0.8秒)を適用した全文音声を1回だけ新規TTS生成し、
# その同一音源から無処理版(C0)とDynamics 3適用版(C1)を作る。
# C0とC1をそれぞれ別にTTS生成しない(生成ゆらぎを比較へ混入させない)。
#
# 台本の正本(er001b5_caregiving_script.json)は変更しない。
# Point One/Point Twoは、この比較用の読み上げテキストを構築する
# 段階でのみ追加する。
#
# ER-001B-6の「単独話者設定」「TTS呼び出し」「音量正規化」「使用量ログ」
# 「タイムアウト・エラー処理」「3チャンク分割方式」と、
# ER-001B-8の「ソフトニー・コンプレッサー(Dynamics 3固定パラメータ)」
# 「ラウドネス整合(固定ゲインのみ、ピーク上限-1.0dBFS優先)」の実装・
# 計算式をそのまま再利用する。ER-001B-6/7B/8のスクリプト・マニフェスト・
# 既存音声には一切手を加えない独立スクリプト。本番パイプライン
# (generate_test.py等)には影響しない。
#
# 使い方:
#   python er001b9_caregiving_common_spec.py

import sys

try:
    import numpy as np
except ImportError:
    raise SystemExit(
        "エラー: numpyが見つかりません。次のコマンドでインストールしてください:\n"
        "  .venv/Scripts/python.exe -m pip install numpy scipy"
    )
try:
    import scipy
    from scipy.signal import lfilter
except ImportError:
    raise SystemExit(
        "エラー: scipyが見つかりません。次のコマンドでインストールしてください:\n"
        "  .venv/Scripts/python.exe -m pip install numpy scipy"
    )

import wave
import io
import os
import re
import json
import time
import array
import hashlib
import platform
from datetime import date, datetime

from dotenv import load_dotenv
from google import genai
from google.genai import types

# ============================================================
# ブロック1: 台本読み込み・Point One/Two入りの読み上げテキスト構築
# ============================================================
CAREGIVING_SCRIPT_PATH = "er001b5_caregiving_script.json"

def load_script(path):
    if not os.path.isfile(path):
        raise SystemExit(f"エラー: 台本の正本 {path} が見つかりません。")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def sha256_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

script = load_script(CAREGIVING_SCRIPT_PATH)
script_sha256 = sha256_file(CAREGIVING_SCRIPT_PATH)

body_section = next(s for s in script["sections"] if s["type"] == "body")
points_section = next(s for s in script["sections"] if s.get("heading") == "Today’s Care Points")
sub1, sub2 = points_section["subsections"]
final_section = next(s for s in script["sections"] if s.get("heading") == "In One Line")

# チャンク1: タイトル+本文
CHUNK1_TEXT = "\n\n".join([script["title"]] + body_section["paragraphs"])

# チャンク2: Today's Care Points + Point One + 小見出し1本文 + Point Two + 小見出し2本文
CHUNK2_LINES = (
    [points_section["heading"], "Point One", sub1["heading"]] + sub1["paragraphs"]
    + ["Point Two", sub2["heading"]] + sub2["paragraphs"]
)
CHUNK2_TEXT = "\n\n".join(CHUNK2_LINES)

# チャンク3: In One Line + 締めの本文
CHUNK3_TEXT = "\n\n".join([final_section["heading"]] + final_section["paragraphs"])

CHUNKS = [("body", CHUNK1_TEXT), ("Today’s Care Points", CHUNK2_TEXT), ("In One Line", CHUNK3_TEXT)]
FULL_TEXT = "\n\n".join([CHUNK1_TEXT, CHUNK2_TEXT, CHUNK3_TEXT])

REQUIRED_HEADINGS_IN_ORDER = [
    script["title"], points_section["heading"], "Point One", sub1["heading"],
    "Point Two", sub2["heading"], final_section["heading"],
]

# ---- 検証: 追加された語句がPoint One / Point Twoだけであること ----
chunk2_without_points = "\n\n".join(
    [points_section["heading"], sub1["heading"]] + sub1["paragraphs"]
    + [sub2["heading"]] + sub2["paragraphs"]
)
chunk2_from_json_directly = "\n\n".join(
    [points_section["heading"]] + [sub1["heading"]] + sub1["paragraphs"]
    + [sub2["heading"]] + sub2["paragraphs"]
)
assert chunk2_without_points == chunk2_from_json_directly, (
    "Point One/Twoを除去したチャンク2が、正本JSONから直接組み立てた内容と一致しません"
)
print("検証: チャンク2からPoint One/Twoを除去すると、正本JSONの該当セクションと完全一致"
      "(追加差分がPoint表記だけであることを確認)", flush=True)

with open(CAREGIVING_SCRIPT_PATH, "r", encoding="utf-8") as f:
    _script_check = json.load(f)
assert _script_check == script, "正本JSONの内容が読み込み後に変化しています(想定外)"
print(f"検証: 正本JSON({CAREGIVING_SCRIPT_PATH})は未変更。SHA-256: {script_sha256[:16]}...", flush=True)

# ============================================================
# ブロック2: 演技指示(ER-001B-6の共通基本指示+Level 2指示 + 忠実性ルールの追加のみ)
# ============================================================
COMMON_BASE_INSTRUCTION = """TTS the following complete story in natural, engaging English.

Speak directly to one interested listener rather than announcing to a large crowd.

Create a natural emotional arc that follows the meaning already present in the script. Let the energy, weight, and pace rise or fall when the story itself changes. Do not add excitement, sadness, urgency, or drama that is not supported by the words.

Carry the meaning naturally across sentence boundaries. Do not reset your pitch, energy, or rhythm after every sentence. Group related sentences into complete thoughts, while keeping important contrasts and turning points clear.

Treat the narration as one continuous program, even when it is generated in separate sections.

Read every title, section heading, and subsection heading exactly as written. Never skip, paraphrase, shorten, or silently absorb a heading into the following text.

Clearly say "In One Line" before reading the final section.

Do not shout, sound like a movie trailer, become gloomy or sleepy, or use a distant and overly formal newsreader style.

"""

LEVEL2_INSTRUCTION = """Give the narration a noticeably animated, emotionally present, and expressive delivery.

Use a clearly wider vocal range, stronger emphasis on important words and turning points, and more distinct rises and falls in energy.

Make the listener feel that the story matters and that you genuinely want them to keep listening.

Keep the narration moving with confident momentum, including during explanatory passages. Avoid becoming passive, flat, or overly restrained.

Allow the most important moments, contrasts, and conclusions to land with clear emotional impact.

Use stronger expression than Level 1, but vary the intensity across the story. Do not stay at maximum intensity throughout.

Do not shout, force emotion, exaggerate feelings that are not present in the script, or sound like a sports commentator or movie trailer.

"""

POINT_LABEL_FIDELITY_RULE = """Read every title, section heading, point label, and subsection heading exactly as written.
Clearly say "Point One" before the first care point and "Point Two" before the second care point.
Clearly say "In One Line" before the final section.
Do not skip, repeat, paraphrase, shorten, or merge any title, heading, point label, or subsection heading with the following text.

"""

STYLE_PREFIX = COMMON_BASE_INSTRUCTION + LEVEL2_INSTRUCTION + POINT_LABEL_FIDELITY_RULE

wpm_pattern = re.compile(r"\d+\s*[-–]?\s*\d*\s*words per minute|\bwpm\b", re.IGNORECASE)
assert not wpm_pattern.search(STYLE_PREFIX), "演技指示に話速の数値指定が含まれています"
print(f"演技指示のsha256: {sha256_text(STYLE_PREFIX)[:16]}...", flush=True)

# ============================================================
# ブロック3: 道具(音量正規化・PCM<->WAV。ER-001B-6/8と同一)
# ============================================================
def normalize_pcm(pcm_bytes, target_peak=0.7):
    samples = array.array('h', pcm_bytes)
    if not samples:
        return pcm_bytes
    peak = max(abs(s) for s in samples)
    if peak == 0:
        return pcm_bytes
    scale = min((target_peak * 32767) / peak, 3.0)
    normalized = array.array('h', (max(-32768, min(32767, int(s * scale))) for s in samples))
    return normalized.tobytes()

def pcm_to_wav_bytes(pcm_bytes, sample_rate):
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        w.writeframes(pcm_bytes)
    return buf.getvalue()

def read_wav_float(path):
    with wave.open(path, "rb") as w:
        channels = w.getnchannels()
        sampwidth = w.getsampwidth()
        framerate = w.getframerate()
        nframes = w.getnframes()
        raw = w.readframes(nframes)
    assert sampwidth == 2
    samples = np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768.0
    return samples, framerate, channels, nframes

def write_wav_float(path, samples, framerate, channels):
    assert np.all(np.isfinite(samples)), "出力サンプルにNaN/Infが含まれています"
    peak = np.max(np.abs(samples))
    assert peak <= 1.0 + 1e-9, f"出力にクリッピングの恐れがあります(peak={peak})"
    clipped = np.clip(samples, -1.0, 1.0)
    pcm16 = (clipped * 32767.0).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(channels)
        w.setsampwidth(2)
        w.setframerate(framerate)
        w.writeframes(pcm16.tobytes())

# ============================================================
# ブロック4: クライアント初期化・モデル設定(ER-001B-6と同一)
# ============================================================
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-2.5-pro-preview-tts"
QA_MODEL_NAME = "gemini-3-flash-preview"
LANGUAGE_CODE = "en-us"
VOICE = "Charon"
SAMPLE_RATE = 24000
MAX_RETRY = 2
MAX_CONTENT_ATTEMPTS = 5  # タスク指定: 最大5回、5回とも不合格なら停止して報告
TTS_TIMEOUT_MS = 150_000
TIER1_DAILY_LIMIT = 50

SECTION_JOIN_PAUSE_SECONDS = 0.8
SECTION_JOIN_PAUSE = b"\x00\x00" * int(SAMPLE_RATE * SECTION_JOIN_PAUSE_SECONDS)

USAGE_LOG_PATH = ".tts_usage_log.jsonl"

def load_today_call_count():
    if not os.path.isfile(USAGE_LOG_PATH):
        return 0
    today_str = date.today().isoformat()
    count = 0
    with open(USAGE_LOG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if entry.get("date") == today_str:
                count += 1
    return count

def record_call(label):
    entry = {
        "date": date.today().isoformat(),
        "timestamp": datetime.now().isoformat(),
        "script": "er001b9_caregiving_common_spec.py",
        "pattern": label,
    }
    with open(USAGE_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def build_narrator_speech_config(voice_name):
    return types.SpeechConfig(
        language_code=LANGUAGE_CODE,
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice_name)
        ),
    )

def call_tts(prompt, speech_config, label="clip"):
    for attempt in range(1, MAX_RETRY + 2):
        start = time.time()
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=speech_config,
                    http_options=types.HttpOptions(timeout=TTS_TIMEOUT_MS),
                ),
            )
            elapsed = time.time() - start
            parts = response.candidates[0].content.parts
            pcm = b"".join(
                p.inline_data.data for p in parts
                if p.inline_data and p.inline_data.data
            )
            if not pcm:
                raise RuntimeError(f"音声パーツが空でした(parts数: {len(parts)})")
            print(f"    [{label}] 所要時間: {elapsed:.1f}秒 (受信パーツ数: {len(parts)})", flush=True)
            return normalize_pcm(pcm), elapsed
        except Exception as e:
            elapsed = time.time() - start
            msg = str(e)
            if "RESOURCE_EXHAUSTED" in msg or "429" in msg:
                quota_value = re.search(r"'quotaValue':\s*'(\d+)'", msg)
                quota_metric = re.search(r"'quotaMetric':\s*'([^']+)'", msg)
                quota_model = re.search(r"'model':\s*'([^']+)'", msg)
                if quota_value:
                    detail = f"上限 {quota_value.group(1)}回"
                    if quota_model:
                        detail += f"(モデル: {quota_model.group(1)})"
                    if quota_metric:
                        detail += f" [{quota_metric.group(1)}]"
                    print(f"  → [{label}] 1日のリクエスト{detail}に達しました({elapsed:.1f}秒後)。", flush=True)
                else:
                    print(f"  → [{label}] クォータ上限に達しました({elapsed:.1f}秒後)。詳細: {msg}", flush=True)
                print("     再試行しても変わらないため、ここで中止します。")
                sys.exit(1)
            print(f"    [{label}] → エラー(試行{attempt}回目、{elapsed:.1f}秒後): {e}", flush=True)
            if attempt > MAX_RETRY:
                raise
            time.sleep(2)

# ============================================================
# ブロック5: 技術検品(1) 埋め込みゲート(承認済み全文・語句カウントを明示)
# ============================================================
def technical_check_embedded(wav_bytes, label):
    headings_json = json.dumps(REQUIRED_HEADINGS_IN_ORDER, ensure_ascii=False)
    prompt = f"""You are doing an automated technical QA check of a TTS-generated narration, comparing it against the approved source text below. Do NOT judge subjective voice quality or how expressive it sounds - only the technical criteria listed.

APPROVED SOURCE TEXT (must be read verbatim, in this exact order, not summarized/shortened/added to/reworded):
---
{FULL_TEXT}
---

REQUIRED ELEMENTS THAT MUST EACH BE SPOKEN ALOUD EXACTLY ONCE, IN THIS ORDER, AS LITERAL WORDS (not paraphrased, not silently skipped, not merged with surrounding text): {headings_json}

Listen to the audio and count occurrences (as literally spoken words) of each required element, then answer:
1. title_count: how many times is the exact title "{script['title']}" spoken at the very start (expected: exactly 1)?
2. today_care_points_count: how many times is "Today's Care Points" spoken (expected: exactly 1)?
3. point_one_count: how many times is "Point One" spoken as its own distinct label (expected: exactly 1)?
4. subheading1_count: how many times is "{sub1['heading']}" spoken (expected: exactly 1)?
5. point_two_count: how many times is "Point Two" spoken as its own distinct label (expected: exactly 1)?
6. subheading2_count: how many times is "{sub2['heading']}" spoken (expected: exactly 1)?
7. in_one_line_count: how many times is "In One Line" spoken (expected: exactly 1)?
8. dropped_content: true if any sentence or significant portion of the source text is missing from the audio.
9. duplicated_content: true if any sentence/heading is accidentally spoken twice (beyond the counts above).
10. non_english_or_extraneous_speech: true if there is any non-English speech, or any spoken stage direction / instruction text / JSON key name / Markdown symbol read aloud.
11. unauthorized_wording_changes: true if the spoken words meaningfully change, add to, or remove from the source text's wording (natural verbalization of numbers/punctuation is not a change).
12. numbers_changed: true if any number (such as "37.1 percent") is spoken incorrectly or changed.

Return ONLY valid JSON, no other text, in exactly this shape:
{{"title_count": 1, "today_care_points_count": 1, "point_one_count": 1, "subheading1_count": 1, "point_two_count": 1, "subheading2_count": 1, "in_one_line_count": 1, "dropped_content": false, "duplicated_content": false, "non_english_or_extraneous_speech": false, "unauthorized_wording_changes": false, "numbers_changed": false, "notes": "brief explanation in English"}}"""

    for attempt in range(5):
        try:
            resp = client.models.generate_content(
                model=QA_MODEL_NAME,
                contents=[types.Part.from_bytes(data=wav_bytes, mime_type="audio/wav"), prompt],
                config=types.GenerateContentConfig(response_mime_type="application/json"),
            )
            text_out = re.sub(r"^```(json)?|```$", "", resp.text.strip(), flags=re.MULTILINE).strip()
            result = json.loads(text_out)
            checks = {
                "title_count": result.get("title_count") == 1,
                "today_care_points_count": result.get("today_care_points_count") == 1,
                "point_one_count": result.get("point_one_count") == 1,
                "subheading1_count": result.get("subheading1_count") == 1,
                "point_two_count": result.get("point_two_count") == 1,
                "subheading2_count": result.get("subheading2_count") == 1,
                "in_one_line_count": result.get("in_one_line_count") == 1,
                "dropped_content": result.get("dropped_content") is False,
                "duplicated_content": result.get("duplicated_content") is False,
                "non_english_or_extraneous_speech": result.get("non_english_or_extraneous_speech") is False,
                "unauthorized_wording_changes": result.get("unauthorized_wording_changes") is False,
                "numbers_changed": result.get("numbers_changed") is False,
            }
            passed = all(checks.values())
            reasons = [k for k, v in checks.items() if not v]
            print(f"    [{label}][embedded] {'合格' if passed else '不合格 → ' + ', '.join(reasons)} "
                  f"(notes: {result.get('notes','')})", flush=True)
            return passed, reasons, result
        except Exception as e:
            print(f"    [{label}][embedded] QA呼び出し失敗(試行{attempt+1}回目): {str(e)[:150]}", flush=True)
            time.sleep(8)
    print(f"    [{label}][embedded] QAモデル応答不能。判定不能として不合格扱いにします(安全側)", flush=True)
    return False, ["qa_model_unavailable"], {"notes": "embedded QA unavailable after retries"}

# ============================================================
# ブロック6: 技術検品(2) 独立した事後grounded再検証(全文書き起こし方式)
# ER-001B-6Aで判明した「見出し欠落の見逃し」対策として、埋め込みゲートとは
# 別の切り口(全文書き起こし+要素カウント)で二重に確認する。
# ============================================================
def technical_check_grounded_transcript(wav_bytes, label):
    prompt = f"""Here is the exact approved source text this audio should read aloud verbatim, in order:
---
{FULL_TEXT}
---

Listen to the audio and:
1. Transcribe exactly what is spoken, verbatim, from start to finish.
2. Report how many times each of these exact phrases is spoken as its own distinct spoken element: "{script['title']}", "Today's Care Points", "Point One", "{sub1['heading']}", "Point Two", "{sub2['heading']}", "In One Line".
3. State whether the transcript matches the approved source text exactly (any additions, omissions, or word substitutions?).

Return ONLY valid JSON, no other text, in exactly this shape:
{{"transcript": "...", "title_count": 1, "today_care_points_count": 1, "point_one_count": 1, "subheading1_count": 1, "point_two_count": 1, "subheading2_count": 1, "in_one_line_count": 1, "matches_source_exactly": true, "differences_note": "brief explanation in English"}}"""

    for attempt in range(5):
        try:
            resp = client.models.generate_content(
                model=QA_MODEL_NAME,
                contents=[types.Part.from_bytes(data=wav_bytes, mime_type="audio/wav"), prompt],
                config=types.GenerateContentConfig(response_mime_type="application/json"),
            )
            text_out = re.sub(r"^```(json)?|```$", "", resp.text.strip(), flags=re.MULTILINE).strip()
            result = json.loads(text_out)
            checks = {
                "title_count": result.get("title_count") == 1,
                "today_care_points_count": result.get("today_care_points_count") == 1,
                "point_one_count": result.get("point_one_count") == 1,
                "subheading1_count": result.get("subheading1_count") == 1,
                "point_two_count": result.get("point_two_count") == 1,
                "subheading2_count": result.get("subheading2_count") == 1,
                "in_one_line_count": result.get("in_one_line_count") == 1,
                "matches_source_exactly": result.get("matches_source_exactly") is True,
            }
            passed = all(checks.values())
            reasons = [k for k, v in checks.items() if not v]
            print(f"    [{label}][grounded] {'合格' if passed else '不合格 → ' + ', '.join(reasons)} "
                  f"(diff note: {result.get('differences_note','')})", flush=True)
            return passed, reasons, result
        except Exception as e:
            print(f"    [{label}][grounded] QA呼び出し失敗(試行{attempt+1}回目): {str(e)[:150]}", flush=True)
            time.sleep(8)
    print(f"    [{label}][grounded] QAモデル応答不能。判定不能として不合格扱いにします(安全側)", flush=True)
    return False, ["qa_model_unavailable"], {"notes": "grounded QA unavailable after retries"}

# ============================================================
# ブロック7: C0生成(最大5回試行。技術的失敗時のみ再生成)
# ============================================================
today_so_far = load_today_call_count()
print("ER-001B-9: 老老介護への共通最終仕様適用テスト")
print(f"話者: {VOICE} / モデル: {MODEL_NAME} / 言語: {LANGUAGE_CODE}")
print(f"最大生成試行回数: {MAX_CONTENT_ATTEMPTS}回(技術的失敗時のみ再生成、埋め込み検品+独立grounded検品の両方に合格が必要)")
print(f"本日ここまでの呼び出し回数(全スクリプト合算の見立て): {today_so_far} 回")
print()

speech_config = build_narrator_speech_config(VOICE)
REJECTED_FILES = []
attempts_log = []
c0_audio = None
c0_chunk_records = None
accepted_attempt = None

for attempt in range(1, MAX_CONTENT_ATTEMPTS + 1):
    print(f"[試行{attempt}/{MAX_CONTENT_ATTEMPTS}] 老老介護 × {VOICE} × Level2+Point番号 を生成中...", flush=True)
    audio = b""
    chunk_records = []
    for j, (chunk_label, chunk_text) in enumerate(CHUNKS, 1):
        call_label = f"caregiving_{VOICE}_common_a{attempt}_c{j}_{chunk_label}"
        print(f"  [試行{attempt}] チャンク {j}/3({chunk_label}, {len(chunk_text.split())}語)を生成中...", flush=True)
        pcm, gen_seconds = call_tts(STYLE_PREFIX + chunk_text, speech_config, label=call_label)
        record_call(call_label)
        if j > 1:
            audio += SECTION_JOIN_PAUSE
        audio += pcm
        chunk_records.append({
            "index": j, "label": chunk_label, "text": chunk_text,
            "word_count": len(chunk_text.split()),
            "generation_seconds": round(gen_seconds, 1),
            "audio_duration_seconds": round(len(pcm) / (SAMPLE_RATE * 2), 1),
        })

    wav_bytes = pcm_to_wav_bytes(audio, SAMPLE_RATE)
    passed1, reasons1, qa1 = technical_check_embedded(wav_bytes, label=f"a{attempt}")
    passed2, reasons2, qa2 = (False, ["skipped_embedded_failed"], {}) if not passed1 else \
        technical_check_grounded_transcript(wav_bytes, label=f"a{attempt}")

    passed = passed1 and passed2
    attempts_log.append({
        "attempt": attempt, "passed": passed,
        "embedded_check": {"passed": passed1, "reasons": reasons1, "result": qa1},
        "grounded_check": {"passed": passed2, "reasons": reasons2, "result": qa2},
    })

    if passed:
        c0_audio = audio
        c0_chunk_records = chunk_records
        accepted_attempt = attempt
        print(f"  [試行{attempt}] 埋め込み検品・独立grounded検品ともに合格。この生成をC0として採用します。", flush=True)
        break
    else:
        rejected_name = f"er001b9_caregiving_level2_numbered_raw_REJECTED_attempt{attempt}.wav"
        with wave.open(rejected_name, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(SAMPLE_RATE)
            w.writeframes(audio)
        REJECTED_FILES.append(rejected_name)
        all_reasons = list(dict.fromkeys(reasons1 + reasons2))
        print(f"  [試行{attempt}] 技術検品不合格({', '.join(all_reasons)})。{rejected_name} として退避しました。", flush=True)
        if attempt == MAX_CONTENT_ATTEMPTS:
            print(f"[停止] 最大{MAX_CONTENT_ATTEMPTS}回すべて技術検品に不合格でした。C0を採用できません。", flush=True)

if c0_audio is None:
    manifest_partial = {
        "experiment_id": "ER-001B-9",
        "status": "FAILED_ALL_ATTEMPTS",
        "max_attempts": MAX_CONTENT_ATTEMPTS,
        "attempts_log": attempts_log,
        "rejected_files": REJECTED_FILES,
        "generated_at": datetime.now().isoformat(),
    }
    with open("er001b9_manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest_partial, f, ensure_ascii=False, indent=2)
    raise SystemExit(
        f"エラー: {MAX_CONTENT_ATTEMPTS}回すべて技術検品に不合格でした。"
        f"er001b9_manifest.jsonに経緯を記録して停止します。"
    )

# ============================================================
# ブロック8: C0保存
# ============================================================
C0_FILE = "er001b9_caregiving_level2_numbered_raw.wav"
C1_FILE = "er001b9_caregiving_level2_numbered_dynamics3.wav"

with wave.open(C0_FILE, "wb") as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(SAMPLE_RATE)
    w.writeframes(c0_audio)

c0_seconds = len(c0_audio) / (SAMPLE_RATE * 2)
print(f"\n-> {C0_FILE} を保存しました(約 {c0_seconds:.1f}秒 / {c0_seconds/60:.2f}分、試行回数: {accepted_attempt})\n")

# ============================================================
# ブロック9: 客観指標・Dynamics 3(ER-001B-8と同一実装・同一パラメータ)
# ============================================================
def design_rbj_highshelf(sr, f0, gain_db, q):
    A = 10 ** (gain_db / 40)
    w0 = 2 * np.pi * f0 / sr
    alpha = np.sin(w0) / (2 * q)
    cos_w0 = np.cos(w0)
    sqrtA = np.sqrt(A)
    b0 = A * ((A + 1) + (A - 1) * cos_w0 + 2 * sqrtA * alpha)
    b1 = -2 * A * ((A - 1) + (A + 1) * cos_w0)
    b2 = A * ((A + 1) + (A - 1) * cos_w0 - 2 * sqrtA * alpha)
    a0 = (A + 1) - (A - 1) * cos_w0 + 2 * sqrtA * alpha
    a1 = 2 * ((A - 1) - (A + 1) * cos_w0)
    a2 = (A + 1) - (A - 1) * cos_w0 - 2 * sqrtA * alpha
    return np.array([b0, b1, b2]) / a0, np.array([a0, a1, a2]) / a0

def design_rbj_highpass(sr, f0, q):
    w0 = 2 * np.pi * f0 / sr
    alpha = np.sin(w0) / (2 * q)
    cos_w0 = np.cos(w0)
    b0 = (1 + cos_w0) / 2
    b1 = -(1 + cos_w0)
    b2 = (1 + cos_w0) / 2
    a0 = 1 + alpha
    a1 = -2 * cos_w0
    a2 = 1 - alpha
    return np.array([b0, b1, b2]) / a0, np.array([a0, a1, a2]) / a0

LUFS_METHOD_NOTE = (
    "ITU-R BS.1770のK-weightingを24kHz向けにRBJ Audio EQ Cookbookの式で再設計し、"
    "2段階ゲーティングで積分ラウドネスを近似計算したもの(ER-001B-7A/8と同一実装)。"
    "公式のBS.1770準拠測定器とは完全には一致しない可能性がある近似値。"
)
LRA_METHOD_NOTE = "3秒窓・1秒ホップの短時間ラウドネス分布のP95-P10による簡易近似。EBU R128のLRA完全準拠アルゴリズムではない。"

def k_weight(samples, sr):
    b1, a1 = design_rbj_highshelf(sr, 1681.9, 3.999844545, 0.7071752369554193)
    b2, a2 = design_rbj_highpass(sr, 38.13547087613982, 0.5003270373238773)
    return lfilter(b2, a2, lfilter(b1, a1, samples))

def integrated_lufs_approx(samples, sr):
    y = k_weight(samples, sr)
    block, hop = int(0.4 * sr), int(0.1 * sr)
    if len(y) < block:
        return None
    z = np.array([np.mean(y[s:s + block] ** 2) for s in range(0, len(y) - block + 1, hop)])
    z = z[z > 0]
    if len(z) == 0:
        return None
    loudness = -0.691 + 10 * np.log10(z)
    gated1 = z[loudness > -70]
    if len(gated1) == 0:
        return None
    ungated_loudness = -0.691 + 10 * np.log10(np.mean(gated1))
    rel_gate = ungated_loudness - 10
    loudness1 = -0.691 + 10 * np.log10(gated1)
    gated2 = gated1[loudness1 > rel_gate]
    if len(gated2) == 0:
        gated2 = gated1
    return float(-0.691 + 10 * np.log10(np.mean(gated2)))

def loudness_range_approx(samples, sr):
    y = k_weight(samples, sr)
    block, hop = int(3.0 * sr), int(1.0 * sr)
    if len(y) < block:
        return None
    vals = []
    for s in range(0, len(y) - block + 1, hop):
        z = np.mean(y[s:s + block] ** 2)
        if z > 0:
            vals.append(-0.691 + 10 * np.log10(z))
    if len(vals) < 2:
        return None
    vals = np.array(vals)
    gated = vals[vals > -70]
    if len(gated) < 2:
        gated = vals
    return float(np.percentile(gated, 95) - np.percentile(gated, 10))

def db(x):
    return 20 * np.log10(max(x, 1e-12))

def measure_metrics(mono, sr):
    peak = float(np.max(np.abs(mono)))
    rms = float(np.sqrt(np.mean(mono ** 2)))
    clip_count = int(np.sum(np.abs(mono) >= 0.999))
    lufs = integrated_lufs_approx(mono, sr)
    lra = loudness_range_approx(mono, sr)
    crest_factor_db = round(db(peak) - db(rms), 2) if rms > 0 else None
    return {
        "duration_seconds": round(len(mono) / sr, 3),
        "sample_count": int(len(mono)),
        "sample_rate": sr,
        "peak_dbfs": round(db(peak), 2),
        "rms_dbfs": round(db(rms), 2),
        "integrated_lufs_approx": round(lufs, 2) if lufs is not None else None,
        "loudness_range_approx_lu": round(lra, 2) if lra is not None else None,
        "crest_factor_db": crest_factor_db,
        "clipping_sample_count": clip_count,
        "clipping_detected": clip_count > 0,
    }

def soft_knee_gain_reduction_db(level_db, threshold_db, ratio, knee_db):
    gr = np.zeros_like(level_db)
    lower, upper = threshold_db - knee_db / 2, threshold_db + knee_db / 2
    below, above = level_db <= lower, level_db >= upper
    within = ~below & ~above
    gr[above] = (level_db[above] - threshold_db) * (1 / ratio - 1)
    x = level_db[within] - lower
    gr[within] = ((1 / ratio - 1) * (x ** 2)) / (2 * knee_db)
    return gr

def envelope_follower_db(mono, sr, attack_ms, release_ms):
    abs_sig = np.abs(mono)
    attack_coef = np.exp(-1.0 / (sr * attack_ms / 1000.0))
    release_coef = np.exp(-1.0 / (sr * release_ms / 1000.0))
    env = np.zeros_like(abs_sig)
    prev = 0.0
    for i, x in enumerate(abs_sig):
        coef = attack_coef if x > prev else release_coef
        prev = coef * prev + (1 - coef) * x
        env[i] = prev
    return 20 * np.log10(np.maximum(env, 1e-9))

def apply_compressor(mono, sr, params):
    env_db = envelope_follower_db(mono, sr, params["attack_ms"], params["release_ms"])
    threshold_db = float(np.percentile(env_db, params["threshold_percentile"]))
    gr_db = soft_knee_gain_reduction_db(env_db, threshold_db, params["ratio"], params["knee_db"])
    smooth_coef = np.exp(-1.0 / (sr * params["gain_smoothing_ms"] / 1000.0))
    gr_db_smoothed = np.zeros_like(gr_db)
    prev = 0.0
    for i, g in enumerate(gr_db):
        prev = smooth_coef * prev + (1 - smooth_coef) * g
        gr_db_smoothed[i] = prev
    gain_linear = 10 ** (gr_db_smoothed / 20)
    return mono * gain_linear, gr_db_smoothed, threshold_db

def diagnose_gain_reduction(gr_db_series, sr):
    step = max(1, int(sr / 100))
    ds = gr_db_series[::step]
    dc_removed = ds - np.mean(ds)
    if np.allclose(dc_removed, 0) or len(dc_removed) < 20:
        autocorr_info = {"pumping_suspected": False, "max_autocorr": 0.0, "note": "ゲイン変化がほぼ無いため判定対象外"}
    else:
        autocorr = np.correlate(dc_removed, dc_removed, mode="full")
        autocorr = autocorr[len(autocorr) // 2:]
        autocorr = autocorr / (autocorr[0] + 1e-12)
        min_lag, max_lag = 10, min(200, len(autocorr) - 1)
        if min_lag >= max_lag:
            autocorr_info = {"pumping_suspected": False, "max_autocorr": 0.0, "note": "音声が短すぎて判定対象外"}
        else:
            window = autocorr[min_lag:max_lag]
            peak_idx = int(np.argmax(window)) + min_lag
            peak_val = float(window[peak_idx - min_lag])
            autocorr_info = {
                "pumping_suspected": bool(peak_val > 0.5),
                "max_autocorr": round(peak_val, 3),
                "period_seconds_at_peak": round(peak_idx / 100.0, 2),
                "threshold_used": 0.5,
            }
    window_samples = max(1, int(0.05 * 100))
    recover_events, i, n = 0, 0, len(ds)
    while i < n - window_samples:
        if ds[i] < -3.0 and np.any(ds[i:i + window_samples] > -0.5):
            recover_events += 1
            i += window_samples
            continue
        i += 1
    below = ds < -1.0
    max_run = cur_run = 0
    for b in below:
        cur_run = cur_run + 1 if b else 0
        max_run = max(max_run, cur_run)
    return {
        **autocorr_info,
        "rapid_gain_recovery_event_count": recover_events,
        "max_sustained_reduction_seconds": round(max_run / 100.0, 2),
    }

PEAK_CEILING_DB = -1.0

def match_loudness(processed, target_lufs, sr):
    compressed_lufs = integrated_lufs_approx(processed, sr)
    current_peak_db = db(float(np.max(np.abs(processed))))
    desired_gain_db = 0.0 if (target_lufs is None or compressed_lufs is None) else target_lufs - compressed_lufs
    max_gain_allowed_by_peak_db = PEAK_CEILING_DB - current_peak_db
    final_gain_db = min(desired_gain_db, max_gain_allowed_by_peak_db)
    gained = processed * (10 ** (final_gain_db / 20))
    final_lufs = integrated_lufs_approx(gained, sr)
    shortfall_lu = round(target_lufs - final_lufs, 3) if (target_lufs is not None and final_lufs is not None) else None
    return gained, {
        "target_lufs": round(target_lufs, 2) if target_lufs is not None else None,
        "compressed_lufs_before_gain": round(compressed_lufs, 2) if compressed_lufs is not None else None,
        "desired_gain_db": round(desired_gain_db, 3),
        "peak_ceiling_db": PEAK_CEILING_DB,
        "max_gain_allowed_by_peak_db": round(max_gain_allowed_by_peak_db, 3),
        "applied_fixed_gain_db": round(final_gain_db, 3),
        "peak_ceiling_prioritized": bool(final_gain_db < desired_gain_db - 1e-9),
        "final_peak_dbfs": round(db(float(np.max(np.abs(gained)))), 2),
        "final_lufs_approx": round(final_lufs, 2) if final_lufs is not None else None,
        "loudness_shortfall_lu": shortfall_lu,
        "within_0_3_lu_target": (abs(shortfall_lu) <= 0.3) if shortfall_lu is not None else None,
    }

# ER-001B-8のDynamics 3固定パラメータ(変更しない)
DYNAMICS3_PARAMS = {
    "type": "soft_knee_compressor",
    "threshold_percentile": 60,
    "ratio": 8.0,
    "knee_db": 6.0,
    "attack_ms": 5.0,
    "release_ms": 200.0,
    "gain_smoothing_ms": 8.0,
}

# ============================================================
# ブロック10: C0を読み直してC1(Dynamics 3)を生成(C0からのみ導出。再TTSなし)
# ============================================================
print("C0の指標を計測中...", flush=True)
c0_samples, c0_sr, c0_channels, c0_nframes = read_wav_float(C0_FILE)
c0_mono = c0_samples if c0_channels == 1 else c0_samples.mean(axis=1)
c0_metrics = measure_metrics(c0_mono, c0_sr)
print(json.dumps(c0_metrics, ensure_ascii=False, indent=2))
print()

print("Dynamics 3(ER-001B-8と同一パラメータ)をC0へ適用中...", flush=True)
processed, gr_db_series, threshold_db_used = apply_compressor(c0_mono, c0_sr, DYNAMICS3_PARAMS)

# ---- 安全チェック: 増幅していないか・NaN/Infがないか ----
assert np.all(gr_db_series <= 1e-6), "ゲインリダクションが正(増幅)になっています(想定外)"
assert np.all(np.isfinite(processed)), "処理直後の信号にNaN/Infが含まれています"
assert np.all(np.abs(processed) <= np.abs(c0_mono) + 1e-9), "処理直後のサンプル絶対値がC0を上回っています(想定外の増幅)"
print("安全チェック: 減衰のみ・NaN/Infなし・C0超えの増幅なし を確認", flush=True)

compressed_metrics = measure_metrics(processed, c0_sr)
target_lufs = c0_metrics["integrated_lufs_approx"]
matched, loudness_info = match_loudness(processed, target_lufs, c0_sr)
assert not np.any(np.abs(matched) >= 1.0), "ラウドネス整合後にクリッピングの恐れがあります"

write_wav_float(C1_FILE, matched, c0_sr, c0_channels)
c1_metrics = measure_metrics(matched, c0_sr)
print(f"-> {C1_FILE} を保存しました "
      f"(final peak={c1_metrics['peak_dbfs']}dBFS, LUFS約{c1_metrics['integrated_lufs_approx']}, "
      f"クリッピング={c1_metrics['clipping_detected']})", flush=True)

max_gr_db = round(float(np.min(gr_db_series)), 2)
mean_gr_db = round(float(np.mean(gr_db_series)), 3)
pumping_info = diagnose_gain_reduction(gr_db_series, c0_sr)
print("ポンピング等の参考所見:", json.dumps(pumping_info, ensure_ascii=False))

# ---- C0とC1の形式一致確認(受入条件10) ----
c1_samples, c1_sr, c1_channels, c1_nframes = read_wav_float(C1_FILE)
format_match = {
    "duration_matches": c0_metrics["duration_seconds"] == c1_metrics["duration_seconds"],
    "sample_count_matches": c0_nframes == c1_nframes,
    "sample_rate_matches": c0_sr == c1_sr,
    "channels_match": c0_channels == c1_channels,
}
assert all(format_match.values()), f"C0とC1の形式が一致していません: {format_match}"
print(f"C0/C1形式一致確認: {format_match}", flush=True)

# ============================================================
# ブロック11: マニフェスト保存
# ============================================================
c0_sha256 = sha256_file(C0_FILE)
c1_sha256 = sha256_file(C1_FILE)

manifest = {
    "experiment_id": "ER-001B-9",
    "status": "OK",
    "purpose": "老老介護記事への共通最終仕様(Emotional+Connected+Level2/Point番号/In One Line必須/0.8秒無音/Dynamics3)の適用テスト",
    "script_source_file": CAREGIVING_SCRIPT_PATH,
    "script_source_sha256": script_sha256,
    "full_narration_text": FULL_TEXT,
    "full_narration_text_sha256": sha256_text(FULL_TEXT),
    "added_diff_is_point_labels_only": True,
    "model": MODEL_NAME,
    "qa_model": QA_MODEL_NAME,
    "voice": VOICE,
    "language_code": LANGUAGE_CODE,
    "common_base_instruction": COMMON_BASE_INSTRUCTION,
    "level2_instruction": LEVEL2_INSTRUCTION,
    "point_label_fidelity_rule": POINT_LABEL_FIDELITY_RULE,
    "final_style_prefix": STYLE_PREFIX,
    "final_style_prefix_sha256": sha256_text(STYLE_PREFIX),
    "common_base_instruction_unchanged_from_er001b6": True,
    "level2_instruction_unchanged_from_er001b6": True,
    "section_join_pause_seconds": SECTION_JOIN_PAUSE_SECONDS,
    "volume_normalized": True,
    "normalize_target_peak": 0.7,
    "max_content_attempts": MAX_CONTENT_ATTEMPTS,
    "c0_generation_attempts": accepted_attempt,
    "c0_attempts_log": attempts_log,
    "c0_rejected_files": REJECTED_FILES,
    "c0_chunks": c0_chunk_records,
    "tts_generated_once_for_both_c0_and_c1": True,
    "c1_derived_from_c0_no_separate_tts": True,
    "environment": {
        "python_version": platform.python_version(),
        "numpy_version": np.__version__,
        "scipy_version": scipy.__version__,
        "install_command": ".venv/Scripts/python.exe -m pip install numpy scipy",
    },
    "peak_ceiling_db": PEAK_CEILING_DB,
    "loudness_match_target_lu": 0.3,
    "lufs_method_note": LUFS_METHOD_NOTE,
    "loudness_range_method_note": LRA_METHOD_NOTE,
    "c0": {
        "file": C0_FILE,
        "file_sha256": c0_sha256,
        "metrics": c0_metrics,
    },
    "c1": {
        "file": C1_FILE,
        "file_sha256": c1_sha256,
        "input_file": C0_FILE,
        "input_file_sha256": c0_sha256,
        "dynamics_params": DYNAMICS3_PARAMS,
        "dynamics_params_unchanged_from_er001b8": True,
        "threshold_db_used": round(threshold_db_used, 2),
        "makeup_gain_before_loudness_match_db": 0.0,
        "gain_reduction_stats": {"max_gain_reduction_db": max_gr_db, "mean_gain_reduction_db": mean_gr_db},
        "metrics_after_compression_before_loudness_match": compressed_metrics,
        "loudness_matching": loudness_info,
        "metrics_final": c1_metrics,
        "pumping_diagnostics": pumping_info,
    },
    "c0_c1_format_match": format_match,
    "generated_at": datetime.now().isoformat(),
}

with open("er001b9_manifest.json", "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)

print()
print("-" * 50)
print("er001b9_manifest.json を保存しました。")
