# ============================================================
# er001b6a_regenerate_caregiving_level1.py
# ER-001B-6A: 老老介護Level 1の技術的不合格音声を再生成
# ============================================================
# 背景: ER-001B-6で生成したer001b6_caregiving_charon_level1_full.wavは、
# 最大試行回数(2回)まで自動再生成しても技術検品に合格せず
# ("In One Line"の二重発話)、不合格のまま採用されていた。
# これは受入条件を満たさないため、この1音声だけを同一条件で再生成する。
#
# 台本・話者・モデル・言語設定・共通基本指示・Level 1固有指示・
# チャンク分割位置・チャンク結合方法・セクション間無音(0.8秒)・
# 音量正規化・タイムアウト条件・後処理は、er001b6_intensity_compare.py
# から一切変更していない(定数・関数を同一の文面のままこのファイルへ
# コピーして再利用している。er001b6_intensity_compare.py自体は変更しない)。
#
# 変更点は「技術検品に合格するまで試行を続ける(上限あり)」という
# 再試行方針のみ。主観的な声の良し悪しでは選別しない。
#
# 使い方:
#   python er001b6a_regenerate_caregiving_level1.py

import wave
import io
import os
import re
import sys
import json
import time
import array
import hashlib
from datetime import date, datetime

from dotenv import load_dotenv
from google import genai
from google.genai import types

# ============================================================
# ブロック1: 台本読み込み・チャンク分割(er001b6_intensity_compare.pyと同一)
# ============================================================
CAREGIVING_SCRIPT_PATH = "er001b5_caregiving_script.json"

def load_script(path):
    if not os.path.isfile(path):
        raise SystemExit(f"エラー: 台本の正本 {path} が見つかりません。")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def build_narration_text(script):
    lines = [script["title"]]
    for section in script["sections"]:
        if section["type"] == "body":
            lines.extend(section["paragraphs"])
        elif section["type"] == "section":
            lines.append(section["heading"])
            if "paragraphs" in section:
                lines.extend(section["paragraphs"])
            if "subsections" in section:
                for sub in section["subsections"]:
                    lines.append(sub["heading"])
                    lines.extend(sub["paragraphs"])
    return "\n\n".join(lines)

def split_into_section_chunks(script):
    chunks = []
    body_section = next(s for s in script["sections"] if s["type"] == "body")
    chunks.append(("body", "\n\n".join([script["title"]] + body_section["paragraphs"])))
    for section in script["sections"]:
        if section["type"] != "section":
            continue
        lines = [section["heading"]]
        if "paragraphs" in section:
            lines.extend(section["paragraphs"])
        if "subsections" in section:
            for sub in section["subsections"]:
                lines.append(sub["heading"])
                lines.extend(sub["paragraphs"])
        chunks.append((section["heading"], "\n\n".join(lines)))
    return chunks

def get_required_headings(script):
    headings = [script["title"]]
    for section in script["sections"]:
        if section["type"] == "section":
            headings.append(section["heading"])
            if "subsections" in section:
                for sub in section["subsections"]:
                    headings.append(sub["heading"])
    return headings

def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

caregiving_script = load_script(CAREGIVING_SCRIPT_PATH)
CAREGIVING_TEXT = build_narration_text(caregiving_script)
CAREGIVING_CHUNKS = split_into_section_chunks(caregiving_script)
CAREGIVING_HEADINGS = get_required_headings(caregiving_script)

# ============================================================
# ブロック2: 共通基本指示 + Level 1指示(er001b6_intensity_compare.pyと一字一句同一)
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

LEVEL1_INSTRUCTION = """Maintain a clearly engaged and expressive delivery throughout the full narration.

Use moderately stronger emotional involvement, emphasis, and vocal variation than a standard conversational news reading.

Keep a clear sense of forward movement, including during explanatory passages. Do not let the energy become passive or overly restrained.

Let important contrasts, turning points, and conclusions stand out more clearly, while keeping the delivery natural and appropriate to the meaning of the script.

Use a wider range of pitch, rhythm, and emphasis than Level 0, but keep the changes smooth and controlled.

"""

STYLE_PREFIX = COMMON_BASE_INSTRUCTION + LEVEL1_INSTRUCTION

# ER-001B-6のマニフェストに記録済みのprompt_sha256と一致することを起動時に検証する
# (演技指示を一切変更していないことの機械的な証拠)。
EXPECTED_PROMPT_SHA256_PREFIX = None
if os.path.isfile("er001b6_manifest.json"):
    with open("er001b6_manifest.json", "r", encoding="utf-8") as f:
        _prev_manifest = json.load(f)
    for _clip in _prev_manifest["clips"]:
        if _clip["condition"] == "caregiving_level1":
            EXPECTED_PROMPT_SHA256_PREFIX = _clip["prompt_sha256"]
            break

_actual_prompt_sha256 = sha256_text(STYLE_PREFIX)
if EXPECTED_PROMPT_SHA256_PREFIX is not None:
    assert _actual_prompt_sha256 == EXPECTED_PROMPT_SHA256_PREFIX, (
        "演技指示のハッシュがER-001B-6時点の記録と一致しません。"
        "共通基本指示・Level 1指示を変更していないか確認してください。"
    )
    print(f"検証: 演技指示のsha256がER-001B-6時点の記録と完全一致({_actual_prompt_sha256[:16]}...)", flush=True)

_actual_script_sha256 = sha256_text(CAREGIVING_TEXT)
EXPECTED_SCRIPT_SHA256 = None
if EXPECTED_PROMPT_SHA256_PREFIX is not None:
    for _clip in _prev_manifest["clips"]:
        if _clip["condition"] == "caregiving_level1":
            EXPECTED_SCRIPT_SHA256 = _clip["script_sha256"]
            break
    assert _actual_script_sha256 == EXPECTED_SCRIPT_SHA256, (
        "台本のハッシュがER-001B-6時点の記録と一致しません。台本を変更していないか確認してください。"
    )
    print(f"検証: 台本のsha256がER-001B-6時点の記録と完全一致({_actual_script_sha256[:16]}...)", flush=True)

# ============================================================
# ブロック3: 道具(音量正規化・PCM→WAV変換。er001b6_intensity_compare.pyと同一)
# ============================================================
def normalize_pcm(pcm_bytes, target_peak=0.7):
    samples = array.array('h', pcm_bytes)
    if not samples:
        return pcm_bytes
    peak = max(abs(s) for s in samples)
    if peak == 0:
        return pcm_bytes
    scale = min((target_peak * 32767) / peak, 3.0)
    normalized = array.array(
        'h', (max(-32768, min(32767, int(s * scale))) for s in samples)
    )
    return normalized.tobytes()

def pcm_to_wav_bytes(pcm_bytes, sample_rate):
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        w.writeframes(pcm_bytes)
    return buf.getvalue()

# ============================================================
# ブロック4: クライアント初期化・モデル設定(er001b6_intensity_compare.pyと同一)
# ============================================================
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-2.5-pro-preview-tts"
QA_MODEL_NAME = "gemini-3-flash-preview"
LANGUAGE_CODE = "en-us"
VOICE = "Charon"
SAMPLE_RATE = 24000
MAX_RETRY = 2
TTS_TIMEOUT_MS = 150_000
TIER1_DAILY_LIMIT = 50

SECTION_JOIN_PAUSE_SECONDS = 0.8  # ER-001B-6から変更しない
SECTION_JOIN_PAUSE = b"\x00\x00" * int(SAMPLE_RATE * SECTION_JOIN_PAUSE_SECONDS)

# 元のER-001B-6では条件あたり最大2回だった。既に2回とも技術的に不合格だったため、
# ここでは合格するまで追加で試行する(主観的な選別はしない)が、無限ループを避けるため
# 追加試行の上限を設ける。試行番号は元の2回に続けて3から数える。
ADDITIONAL_MAX_ATTEMPTS = 4  # attempt 3,4,5,6 まで試す
START_ATTEMPT_NUMBER = 3

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
        "script": "er001b6a_regenerate_caregiving_level1.py",
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
            return normalize_pcm(pcm)
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
# ブロック5: 技術検品(er001b6_intensity_compare.pyのtechnical_check()と同一)
# ============================================================
def technical_check(wav_bytes, full_text, headings, label):
    headings_json = json.dumps(headings, ensure_ascii=False)
    prompt = f"""You are doing an automated technical QA check of a TTS-generated narration, comparing it against the approved source script below. Do NOT judge subjective voice quality, emotional naturalness, or how enjoyable it sounds - only the technical criteria listed.

SOURCE SCRIPT (approved, must not be summarized, shortened, added to, or reworded):
---
{full_text}
---

REQUIRED HEADINGS THAT MUST BE SPOKEN ALOUD, IN ORDER, AS LITERAL WORDS (not paraphrased, not silently skipped): {headings_json}

Listen to the audio and determine:
1. all_headings_present: true only if EVERY required heading above is spoken aloud as written.
2. in_one_line_present: true only if the exact phrase "In One Line" is clearly spoken aloud exactly ONCE as its own heading before the final section (if it is spoken more than once, this must be false).
3. dropped_content: true if any paragraph or significant portion of the source script is missing from the audio.
4. duplicated_content: true if any paragraph, sentence, or heading is spoken twice (a statistic or idea intentionally restated later in the source script itself, e.g. in a closing summary, is NOT a duplication bug - only flag true accidental repeats of the same words/audio).
5. non_english_or_extraneous_speech: true if there is any non-English speech, or any spoken stage direction / instruction text / JSON key name / Markdown symbol read aloud.
6. unauthorized_wording_changes: true if the spoken words meaningfully change, add to, or remove from the source script's wording (natural verbalization of numbers/punctuation, e.g. "6-5" spoken as "six to five", is NOT a wording change).

Return ONLY valid JSON, no other text, in exactly this shape:
{{"all_headings_present": true, "in_one_line_present": true, "dropped_content": false, "duplicated_content": false, "non_english_or_extraneous_speech": false, "unauthorized_wording_changes": false, "notes": "brief explanation in English"}}"""

    for attempt in range(5):
        try:
            resp = client.models.generate_content(
                model=QA_MODEL_NAME,
                contents=[
                    types.Part.from_bytes(data=wav_bytes, mime_type="audio/wav"),
                    prompt,
                ],
                config=types.GenerateContentConfig(response_mime_type="application/json"),
            )
            text = resp.text.strip()
            text = re.sub(r"^```(json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
            result = json.loads(text)
            passed = (
                result.get("all_headings_present") is True
                and result.get("in_one_line_present") is True
                and result.get("dropped_content") is False
                and result.get("duplicated_content") is False
                and result.get("non_english_or_extraneous_speech") is False
                and result.get("unauthorized_wording_changes") is False
            )
            reasons = []
            if result.get("all_headings_present") is not True:
                reasons.append("heading_missing")
            if result.get("in_one_line_present") is not True:
                reasons.append("in_one_line_missing_or_duplicated")
            if result.get("dropped_content") is True:
                reasons.append("dropped_content")
            if result.get("duplicated_content") is True:
                reasons.append("duplicated_content")
            if result.get("non_english_or_extraneous_speech") is True:
                reasons.append("non_english_or_extraneous_speech")
            if result.get("unauthorized_wording_changes") is True:
                reasons.append("unauthorized_wording_changes")
            print(f"    [{label}] 技術検品: {'合格' if passed else '不合格 → ' + ', '.join(reasons)} "
                  f"(notes: {result.get('notes', '')})", flush=True)
            return passed, reasons, result.get("notes", "")
        except Exception as e:
            print(f"    [{label}] 技術検品呼び出し失敗(試行{attempt+1}回目): {str(e)[:150]}", flush=True)
            time.sleep(8)
    print(f"    [{label}] 技術検品モデルが応答不能のため、判定不能→合格扱いとします", flush=True)
    return True, ["content_check_inconclusive"], "QA model unavailable after retries"

# ============================================================
# ブロック6: 事前表示
# ============================================================
today_so_far = load_today_call_count()
max_new_tts_calls = ADDITIONAL_MAX_ATTEMPTS * 3

print("ER-001B-6A: 老老介護Level 1の技術的不合格音声を再生成")
print(f"対象: caregiving × {VOICE} × level1 の1音声のみ")
print(f"追加試行番号: attempt {START_ATTEMPT_NUMBER} 〜 {START_ATTEMPT_NUMBER + ADDITIONAL_MAX_ATTEMPTS - 1}"
      f"(最大{ADDITIONAL_MAX_ATTEMPTS}回、技術検品に合格した時点で終了)")
print(f"本日ここまでの呼び出し回数(全スクリプト合算の見立て): {today_so_far} 回")
print(f"今回の想定追加呼び出し回数: 最大 {max_new_tts_calls} 回(3チャンク×最大{ADDITIONAL_MAX_ATTEMPTS}回試行)")
print(f"実行後の見込み合計(最大): {today_so_far + max_new_tts_calls} 回 / Tier1日次上限(実測): {TIER1_DAILY_LIMIT} 回")
print()

# ============================================================
# ブロック7: 技術検品に合格するまで再生成(主観選別はしない)
# ============================================================
speech_config = build_narrator_speech_config(VOICE)
out_wav = "er001b6_caregiving_charon_level1_full.wav"

new_attempts_log = []
final_audio = None
final_chunk_records = None
accepted_attempt = None
passed_final = False

for offset in range(ADDITIONAL_MAX_ATTEMPTS):
    attempt = START_ATTEMPT_NUMBER + offset
    audio = b""
    chunk_records = []
    print(f"[試行{attempt}] caregiving × {VOICE} × level1 を生成中...", flush=True)
    for j, (chunk_label, chunk_text) in enumerate(CAREGIVING_CHUNKS, 1):
        call_label = f"caregiving_{VOICE}_level1_a{attempt}_c{j}_{chunk_label}"
        print(f"  [試行{attempt}] チャンク {j}/{len(CAREGIVING_CHUNKS)}({chunk_label}, "
              f"{len(chunk_text.split())}語)を生成中...", flush=True)
        t0 = time.time()
        pcm = call_tts(STYLE_PREFIX + chunk_text, speech_config, label=call_label)
        record_call(call_label)
        gen_seconds = time.time() - t0
        if j > 1:
            audio += SECTION_JOIN_PAUSE
        audio += pcm
        chunk_duration = len(pcm) / (SAMPLE_RATE * 2)
        chunk_records.append({
            "index": j,
            "label": chunk_label,
            "text": chunk_text,
            "word_count": len(chunk_text.split()),
            "generation_seconds": round(gen_seconds, 1),
            "audio_duration_seconds": round(chunk_duration, 1),
        })

    wav_bytes = pcm_to_wav_bytes(audio, SAMPLE_RATE)
    passed, reasons, notes = technical_check(wav_bytes, CAREGIVING_TEXT, CAREGIVING_HEADINGS,
                                               label=f"caregiving_{VOICE}_level1_a{attempt}")
    new_attempts_log.append({"attempt": attempt, "passed": passed, "reasons": reasons, "notes": notes})

    final_audio = audio
    final_chunk_records = chunk_records
    accepted_attempt = attempt
    passed_final = passed

    if passed:
        print(f"  [試行{attempt}] 技術検品合格。この生成を採用します。", flush=True)
        break
    else:
        remaining = ADDITIONAL_MAX_ATTEMPTS - offset - 1
        print(f"  [試行{attempt}] 技術検品不合格({', '.join(reasons)})。"
              f"{'再生成します' if remaining > 0 else '追加試行の上限に達しました(要ユーザー確認)'}", flush=True)

with wave.open(out_wav, "wb") as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(SAMPLE_RATE)
    w.writeframes(final_audio)

seconds = len(final_audio) / (SAMPLE_RATE * 2)
print()
print(f"→ {out_wav} を保存しました(約 {seconds:.1f}秒 / {seconds/60:.2f}分、"
      f"{'技術検品合格' if passed_final else '技術検品不合格のまま(要確認)'}、"
      f"今回の試行回数: {accepted_attempt - START_ATTEMPT_NUMBER + 1}、累計試行回数: {accepted_attempt})")

# ============================================================
# ブロック8: er001b6_manifest.jsonを更新
# ============================================================
manifest_path = "er001b6_manifest.json"
with open(manifest_path, "r", encoding="utf-8") as f:
    manifest = json.load(f)

for clip in manifest["clips"]:
    if clip["condition"] == "caregiving_level1":
        original_attempts_log = clip["attempts_log"]
        original_attempt_count = clip["generation_attempts"]
        clip["er001b6a_regeneration"] = {
            "reason": "ER-001B-6の最大試行回数(2回)まで再生成しても技術検品に不合格"
                      "(in_one_line_missing_or_duplicated: 'In One Line'の二重発話)であったため、"
                      "ER-001B-6Aとして同一条件のまま追加再生成を実施した。",
            "original_er001b6_attempts_log": original_attempts_log,
            "original_er001b6_attempt_count": original_attempt_count,
            "rejected_file_archived_as": "er001b6_caregiving_charon_level1_full_REJECTED_duplicated_in_one_line.wav",
            "additional_attempts_log": new_attempts_log,
            "cumulative_attempt_count": accepted_attempt,
            "prompt_sha256_unchanged": _actual_prompt_sha256 == EXPECTED_PROMPT_SHA256_PREFIX,
            "script_sha256_unchanged": _actual_script_sha256 == EXPECTED_SCRIPT_SHA256,
            "regenerated_at": datetime.now().isoformat(),
        }
        clip["chunks"] = final_chunk_records
        clip["duration_seconds"] = round(seconds, 1)
        clip["generation_attempts"] = accepted_attempt
        clip["attempts_log"] = original_attempts_log + new_attempts_log
        clip["final_attempt_technical_check_passed"] = passed_final
        clip["generated_at"] = datetime.now().isoformat()
        break
else:
    raise SystemExit("エラー: er001b6_manifest.json内にcaregiving_level1の記録が見つかりません")

with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)

print(f"er001b6_manifest.jsonのcaregiving_level1エントリを更新しました。")
print("-" * 50)
print("ER-001B-6A: 完了")
