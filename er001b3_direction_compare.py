# ============================================================
# er001b3_direction_compare.py
# ER-001B-3: 1人ナレーターの演技指示比較(話者固定・演技指示のみ変更)
# ============================================================
# 目的: ER-001B-2のユーザー評価で相対的に良かった組み合わせ
#   (阪神記事=Aoede / 老老介護記事=Charon)に話者を固定し、
# 演技指示だけを変えて「一本調子の改善」「自然な緩急」を比較する。
#
# 条件0(現行版)は既存のER-001B-2音声(er001_hanshin_aoede.wav /
# er001_caregiving_charon.wav)を再利用し、再生成しない。
# 条件1(最小指示)・条件2(感情の起伏)の2条件のみ新規に生成する。
#
# tts_test.py / er001b2_narrator_compare.pyの「1人読み用の声設定」
# 「TTS呼び出し」「音量正規化」「使用量ログ」の仕組みをそのまま流用する。
# 本番パイプライン(generate_test.py等)には一切手を加えない、
# 独立の軽量スクリプト。
#
# 使い方:
#   python er001b3_direction_compare.py

import wave
import os
import re
import json
import time
import array
import sys
from datetime import date, datetime

from dotenv import load_dotenv
from google import genai
from google.genai import types

# ============================================================
# ブロック1: 使用英文(ER-001B-3の指示どおり、段落区切りを含めてそのまま使用。
# ER-001B-2で実際に使った本文と内容は完全に同一。修正・短縮・追加なし)
# ============================================================
HANSHIN_TEXT = (
    "One more hit. That was all Hanshin needed to turn a painful loss into a dramatic victory.\n\n"
    "The Tigers lost to the Chunichi Dragons 6-5, but they refused to go quiet. Hanshin scored first, "
    "then Chunichi turned the game around in the fourth inning.\n\n"
    "From that moment, the Dragons tried to pull away, and the Tigers kept chasing.\n\n"
    "By the ninth inning, Hanshin was only one run behind. Something could still happen."
)

CAREGIVING_TEXT = (
    "When we hear the word \"caregiving,\" we may imagine a working adult taking care of an older parent.\n\n"
    "But in many Japanese homes, the caregiver is also old. An older husband supports his older wife, "
    "or an older wife cares for her husband.\n\n"
    "In 37.1 percent of cases, both the person receiving care and the main caregiver living with them are 75 or older.\n\n"
    "The person giving support may also need support."
)

# ============================================================
# ブロック2: 演技指示(条件1=最小指示 / 条件2=感情の起伏。話速の数値指定は含めない)
# ============================================================
HANSHIN_MINIMAL_PREFIX = """TTS the following sports story in natural, engaging English.

Sound like a friendly radio host sharing an exciting close game with listeners. Keep the delivery clear and natural. Do not shout or sound like a movie trailer.

"""

HANSHIN_EMOTIONAL_ARC_PREFIX = """TTS the following sports story in natural, engaging English.

Create a clear emotional arc across the passage.

Begin with energy and curiosity, as if introducing a close and dramatic game. Settle slightly while explaining the early action. Build energy when Chunichi turns the game around. Raise the sense of expectation as Hanshin reaches the ninth inning, then soften briefly when the final hit does not come.

End with positive energy and a feeling that the Tigers will have another chance.

Give light emphasis to "one more hit," "kept chasing," and "something could still happen."

Keep the changes natural and gradual. Do not shout, stay at maximum energy throughout, or sound like a movie trailer.

"""

CAREGIVING_MINIMAL_PREFIX = """TTS the following story in natural, engaging English.

Sound warm, clear, and genuinely interested in helping the listener understand the issue. Keep the delivery calm but engaged. Do not sound gloomy, sleepy, or overly formal.

"""

CAREGIVING_EMOTIONAL_ARC_PREFIX = """TTS the following story in natural, engaging English.

Create a gentle but clear emotional arc across the passage.

Begin in a familiar, conversational way. Add a little more weight when explaining that the caregiver may also be old. Make "37.1 percent" clear and important without sounding dramatic. End with warmth and a strong sense that the caregiver also deserves support.

Give light emphasis to "both people were 75 or older" and "may also need support."

Stay calm but actively engaged with the listener. Do not sound gloomy, sleepy, distant, or overly formal.

"""

# 話者は話題ごとに固定(ER-001B-2のユーザー評価で相対的に良かった組み合わせ)
COMBOS = [
    {
        "topic": "hanshin", "voice": "Aoede", "text": HANSHIN_TEXT,
        "condition": "minimal", "style_prefix": HANSHIN_MINIMAL_PREFIX,
        "out_file": "er001b3_hanshin_aoede_minimal.wav",
    },
    {
        "topic": "hanshin", "voice": "Aoede", "text": HANSHIN_TEXT,
        "condition": "emotional_arc", "style_prefix": HANSHIN_EMOTIONAL_ARC_PREFIX,
        "out_file": "er001b3_hanshin_aoede_emotional_arc.wav",
    },
    {
        "topic": "caregiving", "voice": "Charon", "text": CAREGIVING_TEXT,
        "condition": "minimal", "style_prefix": CAREGIVING_MINIMAL_PREFIX,
        "out_file": "er001b3_caregiving_charon_minimal.wav",
    },
    {
        "topic": "caregiving", "voice": "Charon", "text": CAREGIVING_TEXT,
        "condition": "emotional_arc", "style_prefix": CAREGIVING_EMOTIONAL_ARC_PREFIX,
        "out_file": "er001b3_caregiving_charon_emotional_arc.wav",
    },
]

# 条件0(現行版)は再生成しない。ER-001B-2で生成済みの音声をそのまま参照する。
# text/style_prefixはer001b2_manifest.jsonの実際の記録値(段落区切りなしの一続きの文字列)。
CONDITION0_REUSED = [
    {
        "topic": "hanshin", "voice": "Aoede", "condition": "condition0_baseline",
        "out_file": "er001_hanshin_aoede.wav",
        "text": ("One more hit. That was all Hanshin needed to turn a painful loss into a dramatic victory. "
                  "The Tigers lost to the Chunichi Dragons 6-5, but they refused to go quiet. Hanshin scored first, "
                  "then Chunichi turned the game around in the fourth inning. "
                  "From that moment, the Dragons tried to pull away, and the Tigers kept chasing. "
                  "By the ninth inning, Hanshin was only one run behind. Something could still happen."),
        "style_prefix": ("TTS the following English text as a single narrator speaking solo (not a dialogue), "
                          "at a natural, brisk pace with the lively energy of a sports-radio broadcaster.\n\n"
                          "Convey the tension of a close, back-and-forth baseball game and a genuine sense that "
                          "\"something could still happen\" as the team claws back. Stay upbeat and energetic, "
                          "but keep every word clear and easy to follow.\n\n"
                          "Do not shout. Do not sound like an exaggerated movie-trailer voice. Do not insert "
                          "unnaturally long pauses between sentences - keep the momentum flowing naturally from "
                          "one sentence to the next.\n\n"),
        "duration_seconds": 24.9,
        "source": "er001b2_manifest.json",
        "reused": True,
    },
    {
        "topic": "caregiving", "voice": "Charon", "condition": "condition0_baseline",
        "out_file": "er001_caregiving_charon.wav",
        "text": ("When we hear the word \"caregiving,\" we may imagine a working adult taking care of an older parent. "
                  "But in many Japanese homes, the caregiver is also old. An older husband supports his older wife, "
                  "or an older wife cares for her husband. "
                  "In 37.1 percent of cases, both the person receiving care and the main caregiver living with them "
                  "are 75 or older. The person giving support may also need support."),
        "style_prefix": ("TTS the following English text as a single narrator speaking solo (not a dialogue), "
                          "in a warm, calm, measured voice.\n\n"
                          "This is a serious topic - older spouses caring for each other - so let the seriousness "
                          "come through, but do not sound dark, heavy, or clinical. Speak as if you are personally "
                          "explaining this to a friend, with genuine empathy for the people involved, not reading "
                          "a news bulletin.\n\n"
                          "Do not overact or lay the emotion on too thickly. Keep a natural, unhurried pace, but "
                          "do not slow down so much that it drags.\n\n"),
        "duration_seconds": 27.0,
        "source": "er001b2_manifest.json",
        "reused": True,
    },
]

# ============================================================
# ブロック3: 道具(tts_test.py/er001b2_narrator_compare.pyから流用: 音量正規化)
# ============================================================
def normalize_pcm(pcm_bytes, target_peak=0.7):
    """チャンクごとの音量差をならす(ピークをtarget_peakに揃える)"""
    samples = array.array('h', pcm_bytes)  # 16bit signed整数として読む
    if not samples:
        return pcm_bytes
    peak = max(abs(s) for s in samples)
    if peak == 0:
        return pcm_bytes
    scale = min((target_peak * 32767) / peak, 3.0)  # 極端な増幅は避ける
    normalized = array.array(
        'h', (max(-32768, min(32767, int(s * scale))) for s in samples)
    )
    return normalized.tobytes()

# ============================================================
# ブロック4: クライアント初期化・モデル設定(er001b2_narrator_compare.pyと同じ)
# ============================================================
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-2.5-pro-preview-tts"
LANGUAGE_CODE = "en-us"
SAMPLE_RATE = 24000
MAX_RETRY = 2
TTS_TIMEOUT_MS = 120_000
TIER1_DAILY_LIMIT = 50

USAGE_LOG_PATH = ".tts_usage_log.jsonl"  # tts_test.py/tts_style_test.py/er001b2_narrator_compare.pyと共有

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
        "script": "er001b3_direction_compare.py",
        "pattern": label,
    }
    with open(USAGE_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def build_narrator_speech_config(voice_name):
    """1人読み用の声設定(tts_test.py/er001b2_narrator_compare.pyと同じ形)。"""
    return types.SpeechConfig(
        language_code=LANGUAGE_CODE,
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice_name)
        ),
    )

def call_tts(prompt, speech_config, label="clip"):
    """Gemini-TTSを呼び出す共通の道具(tts_test.py/er001b2_narrator_compare.pyと同じ設計)。"""
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
# ブロック5: 事前表示(組み合わせ数・API呼び出し回数・クォータ警告)
# ============================================================
total_calls = len(COMBOS)  # 条件0は再生成しないため、新規呼び出しは4回のみ

today_so_far = load_today_call_count()
projected_total = today_so_far + total_calls

print("ER-001B-3: 1人ナレーターの演技指示比較(話者固定・演技指示のみ変更)")
print(f"新規生成する組み合わせ数: {total_calls} 個(条件0は既存音声を再利用・再生成なし)")
print(f"本日ここまでの呼び出し回数(全スクリプト合算の見立て): {today_so_far} 回")
print(f"今回追加で必要な回数: {total_calls} 回")
print(f"実行後の見込み合計: {projected_total} 回 / Tier1日次上限(実測): {TIER1_DAILY_LIMIT} 回")
if projected_total > TIER1_DAILY_LIMIT:
    print("⚠ 警告: 実行後の見込み合計が日次上限を超える可能性があります。")
elif projected_total > TIER1_DAILY_LIMIT * 0.8:
    print("⚠ 注意: 実行後の見込み合計が日次上限の8割を超えます。残り枠にご注意ください。")
print()

# ============================================================
# ブロック6: 条件1・条件2を生成して保存 + 条件0(再利用)を含めたマニフェスト記録
# ============================================================
manifest = {
    "task": "ER-001B-3",
    "model": MODEL_NAME,
    "language_code": LANGUAGE_CODE,
    "sample_rate": SAMPLE_RATE,
    "fixed_voice_assignment": {"hanshin": "Aoede", "caregiving": "Charon"},
    "note": (
        "条件0(condition0_baseline)はER-001B-2の既存音声を再利用しており、今回は再生成していない。"
        "条件0のtext/style_prefixはer001b2_manifest.jsonの記録値(段落区切りなしの一続きの文字列)。"
        "条件1・条件2のtextは内容は条件0と完全に同一だが、ER-001B-3の指示に従い段落区切り(空行)を含む形で保持している。"
    ),
    "clips": [],
}

# 条件0(再利用・再生成なし)をマニフェストに先に記録
for entry in CONDITION0_REUSED:
    manifest["clips"].append(entry)

for i, combo in enumerate(COMBOS, 1):
    topic = combo["topic"]
    voice = combo["voice"]
    condition = combo["condition"]
    text = combo["text"]
    style_prefix = combo["style_prefix"]
    out_wav = combo["out_file"]
    label = f"{topic}_{voice}_{condition}"

    print(f"[{i}/{total_calls}] {topic} × {voice} × {condition} を生成中...", flush=True)
    prompt = style_prefix + text
    speech_config = build_narrator_speech_config(voice)
    pcm = call_tts(prompt, speech_config, label=label)
    record_call(label)

    with wave.open(out_wav, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        w.writeframes(pcm)

    seconds = len(pcm) / (SAMPLE_RATE * 2)
    print(f"  → {out_wav} を保存しました(約 {seconds:.1f}秒)")
    print()

    manifest["clips"].append({
        "file": out_wav,
        "topic": topic,
        "voice": voice,
        "condition": condition,
        "text": text,
        "style_prefix": style_prefix,
        "duration_seconds": round(seconds, 1),
        "generated_at": datetime.now().isoformat(),
        "reused": False,
    })

manifest_path = "er001b3_manifest.json"
with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)

print("-" * 50)
print(f"新規{total_calls}組み合わせの音声化が完了しました(条件0は既存音声を再利用)。")
print(f"台本・話者・条件・演技指示の記録を {manifest_path} に保存しました。")
