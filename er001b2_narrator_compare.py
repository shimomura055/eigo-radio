# ============================================================
# er001b2_narrator_compare.py
# ER-001B-2: 1人ナレーター短尺比較(Aoede vs Charon)
# ============================================================
# 目的: 阪神記事/老老介護記事の2つの英文を、Aoede/Charonの2話者で
# 同一条件(同じ台本・同じTTSモデル・同じ演技指示・同じ音声設定・
# 同じ後処理)で音声化し、声質と題材への適応力を比較する。
#
# tts_test.pyのbuild_narrator_speech_config()(1人読み用の声設定)と、
# call_tts()・normalize_pcm()・使用量ログの仕組みをそのまま流用する。
# 本番パイプライン(generate_test.py等)には一切手を加えない、
# 独立の軽量スクリプト。
#
# 使い方:
#   python er001b2_narrator_compare.py

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
# ブロック1: 比較対象の英文(ER-001B-2指定の比較用英文)
# ============================================================
HANSHIN_TEXT = (
    "One more hit. That was all Hanshin needed to turn a painful loss into a dramatic victory. "
    "The Tigers lost to the Chunichi Dragons 6-5, but they refused to go quiet. Hanshin scored first, "
    "then Chunichi turned the game around in the fourth inning. "
    "From that moment, the Dragons tried to pull away, and the Tigers kept chasing. "
    "By the ninth inning, Hanshin was only one run behind. Something could still happen."
)

CAREGIVING_TEXT = (
    "When we hear the word \"caregiving,\" we may imagine a working adult taking care of an older parent. "
    "But in many Japanese homes, the caregiver is also old. An older husband supports his older wife, "
    "or an older wife cares for her husband. "
    "In 37.1 percent of cases, both the person receiving care and the main caregiver living with them are 75 or older. "
    "The person giving support may also need support."
)

# ============================================================
# ブロック2: 演技指示(題材ごとに固定。Aoede/Charon間で完全に同一の文面を使う)
# ============================================================
HANSHIN_STYLE_PREFIX = """TTS the following English text as a single narrator speaking solo (not a dialogue), at a natural, brisk pace with the lively energy of a sports-radio broadcaster.

Convey the tension of a close, back-and-forth baseball game and a genuine sense that "something could still happen" as the team claws back. Stay upbeat and energetic, but keep every word clear and easy to follow.

Do not shout. Do not sound like an exaggerated movie-trailer voice. Do not insert unnaturally long pauses between sentences - keep the momentum flowing naturally from one sentence to the next.

"""

CAREGIVING_STYLE_PREFIX = """TTS the following English text as a single narrator speaking solo (not a dialogue), in a warm, calm, measured voice.

This is a serious topic - older spouses caring for each other - so let the seriousness come through, but do not sound dark, heavy, or clinical. Speak as if you are personally explaining this to a friend, with genuine empathy for the people involved, not reading a news bulletin.

Do not overact or lay the emotion on too thickly. Keep a natural, unhurried pace, but do not slow down so much that it drags.

"""

TOPICS = [
    {"key": "hanshin", "text": HANSHIN_TEXT, "style_prefix": HANSHIN_STYLE_PREFIX},
    {"key": "caregiving", "text": CAREGIVING_TEXT, "style_prefix": CAREGIVING_STYLE_PREFIX},
]

VOICES = ["Aoede", "Charon"]

# ============================================================
# ブロック3: 道具(tts_test.pyから流用: 音量正規化)
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
# ブロック4: クライアント初期化・モデル設定(tts_test.pyと同じモデル)
# ============================================================
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-2.5-pro-preview-tts"
SAMPLE_RATE = 24000
MAX_RETRY = 2
TTS_TIMEOUT_MS = 120_000
TIER1_DAILY_LIMIT = 50

USAGE_LOG_PATH = ".tts_usage_log.jsonl"  # tts_test.py/tts_style_test.pyと共有

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
        "script": "er001b2_narrator_compare.py",
        "pattern": label,
    }
    with open(USAGE_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def build_narrator_speech_config(voice_name):
    """1人読み用の声設定(tts_test.pyのbuild_narrator_speech_config()と同じ形。声名だけ引数化)。"""
    return types.SpeechConfig(
        language_code="en-us",
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice_name)
        ),
    )

def call_tts(prompt, speech_config, label="clip"):
    """Gemini-TTSを呼び出す共通の道具(tts_test.pyのcall_tts()と同じ設計)。"""
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
combos = [(topic, voice) for topic in TOPICS for voice in VOICES]
total_calls = len(combos)

today_so_far = load_today_call_count()
projected_total = today_so_far + total_calls

print(f"ER-001B-2: 1人ナレーター短尺比較(Aoede vs Charon)")
print(f"組み合わせ数: {total_calls} 個(題材{len(TOPICS)} × 話者{len(VOICES)})")
print(f"本日ここまでの呼び出し回数(全スクリプト合算の見立て): {today_so_far} 回")
print(f"今回追加で必要な回数: {total_calls} 回")
print(f"実行後の見込み合計: {projected_total} 回 / Tier1日次上限(実測): {TIER1_DAILY_LIMIT} 回")
if projected_total > TIER1_DAILY_LIMIT:
    print("⚠ 警告: 実行後の見込み合計が日次上限を超える可能性があります。")
elif projected_total > TIER1_DAILY_LIMIT * 0.8:
    print("⚠ 注意: 実行後の見込み合計が日次上限の8割を超えます。残り枠にご注意ください。")
print()

# ============================================================
# ブロック6: 題材×話者ごとに音声化して保存 + 台本・設定の記録
# ============================================================
manifest = {
    "task": "ER-001B-2",
    "model": MODEL_NAME,
    "sample_rate": SAMPLE_RATE,
    "voices_compared": VOICES,
    "clips": [],
}

for i, (topic, voice) in enumerate(combos, 1):
    key = topic["key"]
    text = topic["text"]
    style_prefix = topic["style_prefix"]
    out_wav = f"er001_{key}_{voice.lower()}.wav"
    label = f"{key}_{voice}"

    print(f"[{i}/{total_calls}] {key} × {voice} を生成中...", flush=True)
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
        "topic": key,
        "voice": voice,
        "text": text,
        "style_prefix": style_prefix,
        "duration_seconds": round(seconds, 1),
    })

manifest_path = "er001b2_manifest.json"
with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)

print("-" * 50)
print(f"全{total_calls}組み合わせの音声化が完了しました。")
print(f"台本・話者・演技指示の記録を {manifest_path} に保存しました。")
