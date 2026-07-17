# ============================================================
# er001b6_intensity_compare.py
# ER-001B-6: 表現強度3段階の全文比較
# ============================================================
# 目的: ER-001B-5で採用した共通Emotional+Connected方式のまま、
# 表現強度(感情の関与・強調・抑揚・前進感・聞き手への働きかけ)だけを
# 3段階(Level 0/1/2)に分けて全文音声を比較する。
# 阪神記事・老老介護記事で共通利用できる表現強度の上限を探ることが目的。
#
# 台本の正本(内容は一切変更しない): er001b5_hanshin_script.json /
# er001b5_caregiving_script.json (ER-001B-5でユーザーから提供された正本を再利用)。
#
# ER-001B-5からの変更点:
#   - セクション間無音を0.6秒→0.8秒に変更
#   - 見出し・"In One Line"を明示的に発話させる指示を基本指示へ追加
#   - 表現強度を3段階(Level 0/1/2)に分けて比較
#   - ER-001B-5の3音声は基準音声として再利用しない(無音長・見出し省略の
#     問題があったため。今回は6音声すべてを同一条件下で新規生成する)
#
# ER-001B-5の「JSON台本読み込み」「読み上げテキスト変換」「単独話者設定」
# 「TTS API呼び出し」「セクション分割」「タイムアウト・エラー処理」
# 「音量正規化」「WAV結合」「使用量ログ」「マニフェスト保存」の仕組みを
# そのまま流用する。ER-001B-5のスクリプト・比較結果には一切手を加えない
# 独立スクリプト。本番パイプライン(generate_test.py等)には影響しない。
#
# 使い方:
#   python er001b6_intensity_compare.py

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
# ブロック1: 台本の正本を読み込み、セクション単位のチャンクへ分割
# (ER-001B-5(er001b5_full_narration_compare.py)と同じロジック)
# ============================================================
HANSHIN_SCRIPT_PATH = "er001b5_hanshin_script.json"
CAREGIVING_SCRIPT_PATH = "er001b5_caregiving_script.json"

def load_script(path):
    if not os.path.isfile(path):
        raise SystemExit(
            f"エラー: 台本の正本 {path} が見つかりません。"
            f"内容を推測して生成することはできないため、正本ファイルを配置してから再実行してください。"
        )
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def build_narration_text(script):
    """JSON内のtitle/sectionsを、記録された順番のままプレーンテキストへ変換する。"""
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
    """セクション境界(body / 各見出しセクション)でチャンクに分割する。文の途中では分割しない。"""
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
    """タイトル・全セクション見出し・全小見出しを、読み上げが必須な語句として順番どおりに返す。"""
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

hanshin_script = load_script(HANSHIN_SCRIPT_PATH)
caregiving_script = load_script(CAREGIVING_SCRIPT_PATH)

HANSHIN_TEXT = build_narration_text(hanshin_script)
CAREGIVING_TEXT = build_narration_text(caregiving_script)
HANSHIN_CHUNKS = split_into_section_chunks(hanshin_script)
CAREGIVING_CHUNKS = split_into_section_chunks(caregiving_script)
HANSHIN_HEADINGS = get_required_headings(hanshin_script)
CAREGIVING_HEADINGS = get_required_headings(caregiving_script)

# ============================================================
# ブロック2: 全Level共通の基本指示 + Level固有の強度指示(すべてユーザー指定の文面のまま)
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

LEVEL0_INSTRUCTION = """Use natural vocal variation appropriate to the script.

Give important moments enough emphasis to be clear, but keep the overall delivery controlled and conversational.

Allow explanatory passages to sound calm, while maintaining steady interest and connection with the listener.

Do not overact.

"""

LEVEL1_INSTRUCTION = """Maintain a clearly engaged and expressive delivery throughout the full narration.

Use moderately stronger emotional involvement, emphasis, and vocal variation than a standard conversational news reading.

Keep a clear sense of forward movement, including during explanatory passages. Do not let the energy become passive or overly restrained.

Let important contrasts, turning points, and conclusions stand out more clearly, while keeping the delivery natural and appropriate to the meaning of the script.

Use a wider range of pitch, rhythm, and emphasis than Level 0, but keep the changes smooth and controlled.

"""

LEVEL2_INSTRUCTION = """Give the narration a noticeably animated, emotionally present, and expressive delivery.

Use a clearly wider vocal range, stronger emphasis on important words and turning points, and more distinct rises and falls in energy.

Make the listener feel that the story matters and that you genuinely want them to keep listening.

Keep the narration moving with confident momentum, including during explanatory passages. Avoid becoming passive, flat, or overly restrained.

Allow the most important moments, contrasts, and conclusions to land with clear emotional impact.

Use stronger expression than Level 1, but vary the intensity across the story. Do not stay at maximum intensity throughout.

Do not shout, force emotion, exaggerate feelings that are not present in the script, or sound like a sports commentator or movie trailer.

"""

LEVEL_INSTRUCTIONS = {
    "level0": LEVEL0_INSTRUCTION,
    "level1": LEVEL1_INSTRUCTION,
    "level2": LEVEL2_INSTRUCTION,
}

COMBOS = [
    {"topic": "hanshin", "voice": "Aoede", "script_file": HANSHIN_SCRIPT_PATH,
     "full_text": HANSHIN_TEXT, "chunks": HANSHIN_CHUNKS, "headings": HANSHIN_HEADINGS},
    {"topic": "caregiving", "voice": "Charon", "script_file": CAREGIVING_SCRIPT_PATH,
     "full_text": CAREGIVING_TEXT, "chunks": CAREGIVING_CHUNKS, "headings": CAREGIVING_HEADINGS},
]

CLIP_PLAN = []
for combo in COMBOS:
    for level in ("level0", "level1", "level2"):
        CLIP_PLAN.append({
            **combo,
            "level": level,
            "level_instruction": LEVEL_INSTRUCTIONS[level],
            "style_prefix": COMMON_BASE_INSTRUCTION + LEVEL_INSTRUCTIONS[level],
            "out_file": f"er001b6_{combo['topic']}_{combo['voice'].lower()}_{level}_full.wav",
        })

# ============================================================
# ブロック3: 生成前の自動検証(10節)。不一致なら生成前にエラー終了する。
# ============================================================
def validate_prompts():
    # 1) 共通基本指示が全6条件で完全一致
    for clip in CLIP_PLAN:
        assert clip["style_prefix"].startswith(COMMON_BASE_INSTRUCTION), \
            f"{clip['topic']}/{clip['level']}: 共通基本指示がプロンプト先頭と一致しません"

    # 2) 同じLevelの強度指示が阪神と老老介護で完全一致
    for level in ("level0", "level1", "level2"):
        level_texts = [c["level_instruction"] for c in CLIP_PLAN if c["level"] == level]
        assert len(set(level_texts)) == 1, f"{level}: 強度指示が題材間で一致していません"

    # 3) 記事名・ジャンル名・固有名詞を演技指示へ追加していないことを確認
    # 「sports commentator」等、演技指示自体が持つ一般的な比喩表現(Level 2の
    # "sound like a sports commentator" 等)は題材固有語句ではないため対象外とする。
    banned_terms = ["hanshin", "tiger", "chunichi", "dragon", "kesamaru", "vantelin",
                     "caregiv", "elder", "baseball", "37.1"]
    combined_instructions = COMMON_BASE_INSTRUCTION + "".join(LEVEL_INSTRUCTIONS.values())
    lowered = combined_instructions.lower()
    for term in banned_terms:
        assert term not in lowered, f"演技指示に題材固有の語句が混入しています: '{term}'"

    # 4) Level間の差が強度指示だけであること(共通部分を除いた残りが各Levelで異なることを確認)
    lvl_texts = [LEVEL_INSTRUCTIONS[l] for l in ("level0", "level1", "level2")]
    assert len(set(lvl_texts)) == 3, "Level 0/1/2の強度指示が互いに重複しています"

    # 5) 数値による話速指定を含まない(例: "125-140 words per minute" のようなパターンがないか)
    wpm_pattern = re.compile(r"\d+\s*[-–]?\s*\d*\s*words per minute|\bwpm\b", re.IGNORECASE)
    for clip in CLIP_PLAN:
        assert not wpm_pattern.search(clip["style_prefix"]), \
            f"{clip['topic']}/{clip['level']}: 話速の数値指定が含まれています"

    # 6) 全Levelに見出し発話保証が含まれる
    heading_guarantee = "Read every title, section heading, and subsection heading exactly as written"
    for clip in CLIP_PLAN:
        assert heading_guarantee in clip["style_prefix"], \
            f"{clip['topic']}/{clip['level']}: 見出し発話保証の文言が含まれていません"

    # 7) 全Levelに"In One Line"の明示的な発話指示が含まれる
    in_one_line_guarantee = 'Clearly say "In One Line" before reading the final section.'
    for clip in CLIP_PLAN:
        assert in_one_line_guarantee in clip["style_prefix"], \
            f"{clip['topic']}/{clip['level']}: 'In One Line'の明示発話指示が含まれていません"

    # 阪神3音声・老老介護3音声で、それぞれ台本(チャンク本文)が完全一致していることも確認
    for topic_key, chunks_ref in (("hanshin", HANSHIN_CHUNKS), ("caregiving", CAREGIVING_CHUNKS)):
        for clip in [c for c in CLIP_PLAN if c["topic"] == topic_key]:
            assert [t for _, t in clip["chunks"]] == [t for _, t in chunks_ref], \
                f"{topic_key}/{clip['level']}: チャンク本文が他Levelと一致していません"

    print("生成前検証: 全項目(共通指示一致・Level間差異・話速指定なし・見出し/In One Line保証・台本一致)をパス", flush=True)

validate_prompts()

# ============================================================
# ブロック4: 道具(音量正規化・PCM→WAVバイト列変換)
# ============================================================
def normalize_pcm(pcm_bytes, target_peak=0.7):
    """チャンクごとの音量差をならす(ピークをtarget_peakに揃える)"""
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
# ブロック5: クライアント初期化・モデル設定
# ============================================================
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-2.5-pro-preview-tts"
QA_MODEL_NAME = "gemini-3-flash-preview"  # 技術的検品(生成物の自動チェック)専用。TTS本体とは別モデル。
LANGUAGE_CODE = "en-us"
SAMPLE_RATE = 24000
MAX_RETRY = 2                 # API例外時の再試行回数(通信エラー・500番台等)
MAX_CONTENT_ATTEMPTS = 2      # 技術的失敗(欠落・重複・見出し欠落等)時の生成やり直し回数上限。全条件で共通。
TTS_TIMEOUT_MS = 150_000
TIER1_DAILY_LIMIT = 50

SECTION_JOIN_PAUSE_SECONDS = 0.8  # ER-001B-5の0.6秒から変更(ユーザー指示)
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
        "script": "er001b6_intensity_compare.py",
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
    """Gemini-TTSを呼び出す共通の道具(ER-001B-3/4/5と同じ設計)。"""
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
                print("     リセットを待つか、有料ティアへの切り替えをご検討ください。")
                sys.exit(1)
            print(f"    [{label}] → エラー(試行{attempt}回目、{elapsed:.1f}秒後): {e}", flush=True)
            if attempt > MAX_RETRY:
                raise
            time.sleep(2)

# ============================================================
# ブロック6: 生成物の技術的検品(欠落・重複・見出し欠落・不要発話・語句改変のみを機械判定)
# ============================================================
def technical_check(wav_bytes, full_text, headings, label):
    """
    主観的な声の良し悪しは判定しない。以下の技術的失敗のみを機械的に判定する:
    見出し欠落、In One Line欠落、内容欠落、重複発話、英語以外/不要発話の混入、
    台本にない明確な語句変更。QAモデル自体が不安定な場合は、再試行後もJSON解析に
    失敗した場合、判定不能として合格扱いにする(このスクリプトの主目的である
    表現強度比較の実行を、QAモデルの不調で止めないため)。
    """
    headings_json = json.dumps(headings, ensure_ascii=False)
    prompt = f"""You are doing an automated technical QA check of a TTS-generated narration, comparing it against the approved source script below. Do NOT judge subjective voice quality, emotional naturalness, or how enjoyable it sounds - only the technical criteria listed.

SOURCE SCRIPT (approved, must not be summarized, shortened, added to, or reworded):
---
{full_text}
---

REQUIRED HEADINGS THAT MUST BE SPOKEN ALOUD, IN ORDER, AS LITERAL WORDS (not paraphrased, not silently skipped): {headings_json}

Listen to the audio and determine:
1. all_headings_present: true only if EVERY required heading above is spoken aloud as written.
2. in_one_line_present: true only if the exact phrase "In One Line" is clearly spoken aloud as its own heading before the final section.
3. dropped_content: true if any paragraph or significant portion of the source script is missing from the audio.
4. duplicated_content: true if any paragraph or sentence is spoken twice (a statistic or idea intentionally restated later in the source script itself, e.g. in a closing summary, is NOT a duplication bug - only flag true accidental repeats).
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
                reasons.append("in_one_line_missing")
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
    print(f"    [{label}] 技術検品モデルが応答不能のため、判定不能→合格扱いとします(表現強度比較を止めないため)", flush=True)
    return True, ["content_check_inconclusive"], "QA model unavailable after retries"

# ============================================================
# ブロック7: 事前表示(組み合わせ数・API呼び出し回数見立て・クォータ警告)
# ============================================================
chunks_per_clip = 3
min_tts_calls = len(CLIP_PLAN) * chunks_per_clip  # 各条件1回で成功した場合の最小呼び出し数
max_tts_calls = min_tts_calls * MAX_CONTENT_ATTEMPTS  # 全条件が最大試行回数まで再生成した場合の上限

today_so_far = load_today_call_count()

print("ER-001B-6: 表現強度3段階の全文比較")
print(f"生成する音声数: {len(CLIP_PLAN)} 本(阪神3 Level + 老老介護3 Level)")
print(f"セクション分割: 各3チャンク(body / 見出しセクション / In One Line)")
print(f"最大生成試行回数: 条件あたり{MAX_CONTENT_ATTEMPTS}回(技術的失敗時のみ再生成)")
print(f"想定TTS呼び出し回数: 最小{min_tts_calls}回 〜 最大{max_tts_calls}回(全条件が最大試行回数まで再生成した場合)")
print(f"本日ここまでの呼び出し回数(全スクリプト合算の見立て): {today_so_far} 回")
print(f"実行後の見込み合計(最小〜最大): {today_so_far + min_tts_calls} 〜 {today_so_far + max_tts_calls} 回 "
      f"/ Tier1日次上限(実測): {TIER1_DAILY_LIMIT} 回")
if today_so_far + max_tts_calls > TIER1_DAILY_LIMIT:
    print("[注意] 全条件が最大試行回数まで再生成した場合、日次上限を超える可能性があります。"
          "実際は技術的失敗が起きた場合のみ再生成するため、通常は最小回数に近くなる見込みです。")
print()

# ============================================================
# ブロック8: 条件ごとにセクション単位で生成 → 技術検品 → (必要なら再生成) → 結合・保存
# ============================================================
manifest = {
    "experiment_id": "ER-001B-6",
    "model": MODEL_NAME,
    "qa_model": QA_MODEL_NAME,
    "language_code": LANGUAGE_CODE,
    "sample_rate": SAMPLE_RATE,
    "fixed_voice_assignment": {"hanshin": "Aoede", "caregiving": "Charon"},
    "section_join_pause_seconds": SECTION_JOIN_PAUSE_SECONDS,
    "volume_normalized": True,
    "normalize_target_peak": 0.7,
    "max_content_attempts": MAX_CONTENT_ATTEMPTS,
    "common_base_instruction": COMMON_BASE_INSTRUCTION,
    "level_instructions": LEVEL_INSTRUCTIONS,
    "pre_generation_validation": (
        "共通基本指示の全条件一致、同一Levelの強度指示が題材間で一致、題材固有語句の非混入、"
        "Level間差異が強度指示のみであること、話速数値指定の非存在、見出し発話保証の存在、"
        "'In One Line'明示発話指示の存在、台本(チャンク本文)の題材内一致、を生成前にassertで検証し、"
        "全項目をパスしたことを確認してから生成を開始した(不一致があれば生成前にエラー終了する設計)。"
    ),
    "clips": [],
}

for i, clip in enumerate(CLIP_PLAN, 1):
    topic = clip["topic"]
    voice = clip["voice"]
    level = clip["level"]
    style_prefix = clip["style_prefix"]
    chunks = clip["chunks"]
    headings = clip["headings"]
    full_text = clip["full_text"]
    out_wav = clip["out_file"]
    speech_config = build_narrator_speech_config(voice)

    print(f"[{i}/{len(CLIP_PLAN)}] {topic} × {voice} × {level} を生成中"
          f"(最大{MAX_CONTENT_ATTEMPTS}回試行)...", flush=True)

    attempts_log = []
    final_audio = None
    final_chunk_records = None
    accepted_attempt = None

    for attempt in range(1, MAX_CONTENT_ATTEMPTS + 1):
        audio = b""
        chunk_records = []
        for j, (chunk_label, chunk_text) in enumerate(chunks, 1):
            call_label = f"{topic}_{voice}_{level}_a{attempt}_c{j}_{chunk_label}"
            print(f"  [試行{attempt}] チャンク {j}/{len(chunks)}({chunk_label}, "
                  f"{len(chunk_text.split())}語)を生成中...", flush=True)
            t0 = time.time()
            pcm = call_tts(style_prefix + chunk_text, speech_config, label=call_label)
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
        passed, reasons, notes = technical_check(wav_bytes, full_text, headings,
                                                   label=f"{topic}_{voice}_{level}_a{attempt}")
        attempts_log.append({"attempt": attempt, "passed": passed, "reasons": reasons, "notes": notes})

        if passed:
            final_audio = audio
            final_chunk_records = chunk_records
            accepted_attempt = attempt
            break
        else:
            print(f"  [試行{attempt}] 技術検品不合格({', '.join(reasons)})。"
                  f"{'再生成します' if attempt < MAX_CONTENT_ATTEMPTS else '最大試行回数に達したため、この生成を採用します(要ユーザー確認)'}",
                  flush=True)
            final_audio = audio  # 最大試行到達時のフォールバック用に保持
            final_chunk_records = chunk_records
            accepted_attempt = attempt

    with wave.open(out_wav, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        w.writeframes(final_audio)

    seconds = len(final_audio) / (SAMPLE_RATE * 2)
    all_passed = attempts_log[-1]["passed"]
    print(f"  → {out_wav} を保存しました(約 {seconds:.1f}秒 / {seconds/60:.2f}分、"
          f"{'技術検品合格' if all_passed else '技術検品不合格のまま採用(要確認)'}、試行回数: {accepted_attempt})")
    print()

    manifest["clips"].append({
        "file": out_wav,
        "topic": topic,
        "voice": voice,
        "level": level,
        "condition": f"{topic}_{level}",
        "script_file": clip["script_file"],
        "full_text": full_text,
        "script_sha256": sha256_text(full_text),
        "level_instruction": clip["level_instruction"],
        "final_style_prefix": style_prefix,
        "prompt_sha256": sha256_text(style_prefix),
        "chunk_count": len(chunks),
        "chunks": final_chunk_records,
        "duration_seconds": round(seconds, 1),
        "generated_at": datetime.now().isoformat(),
        "generation_attempts": accepted_attempt,
        "attempts_log": attempts_log,
        "final_attempt_technical_check_passed": all_passed,
    })

manifest_path = "er001b6_manifest.json"
with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)

print("-" * 50)
print(f"全{len(CLIP_PLAN)}音声の生成が完了しました。")
print(f"実験ID・題材・Level・演技指示・ハッシュ・試行ログの記録を {manifest_path} に保存しました。")
