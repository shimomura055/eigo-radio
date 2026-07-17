# ============================================================
# er001b4_connected_narration.py
# ER-001B-4: つながった語りの比較(話者・比較基準固定)
# ============================================================
# 目的: ER-001B-3のユーザー評価で最も良かった条件
#   (阪神=最小指示 / 老老介護=感情の起伏)を基準に、
# 「一文ずつ独立したアナウンスのように読む」傾向を減らし、
# 関連する複数文を一つの考えとしてつなげる指示を追加した版を比較する。
#
# 比較基準の2音声(ER-001B-3で生成済み)は再生成せず、
# er001b3_manifest.jsonの記録値をそのまま参照する。
# 新規に生成するのは「つながった語り」を追加した2音声のみ。
#
# er001b3_direction_compare.pyの「英文(改行含め完全に同一)」
# 「単独話者設定」「TTS呼び出し」「音量正規化」「使用量ログ」
# 「タイムアウト・エラー処理」「マニフェスト保存」の仕組みを
# そのまま流用する。ER-001B-3の比較結果に影響を与えないよう、
# er001b3_direction_compare.py自体は変更しない独立スクリプト。
# 本番パイプライン(generate_test.py等)には一切手を加えない。
#
# 使い方:
#   python er001b4_connected_narration.py

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
# ブロック1: 使用英文(ER-001B-3と完全同一。改行・内容とも変更しない)
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

# ER-001B-3のテキストと完全一致することを起動時に確認する(比較条件の前提)。
assert HANSHIN_TEXT == (
    "One more hit. That was all Hanshin needed to turn a painful loss into a dramatic victory.\n\n"
    "The Tigers lost to the Chunichi Dragons 6-5, but they refused to go quiet. Hanshin scored first, "
    "then Chunichi turned the game around in the fourth inning.\n\n"
    "From that moment, the Dragons tried to pull away, and the Tigers kept chasing.\n\n"
    "By the ninth inning, Hanshin was only one run behind. Something could still happen."
), "阪神記事の英文がER-001B-3と一致していません"

# ============================================================
# ブロック2: 演技指示(ER-001B-3の基準指示 + つながった語りの追加のみ。話速の数値指定なし)
# ============================================================
HANSHIN_CONNECTED_PREFIX = """TTS the following sports story in natural, engaging English.

Sound like a friendly radio host sharing an exciting close game with listeners. Keep the delivery clear and natural. Do not shout or sound like a movie trailer.

Speak to one interested listener rather than announcing to a large crowd.

Carry the meaning naturally across sentence boundaries. Do not reset your pitch, energy, or rhythm after every sentence. Group related sentences into complete thoughts, and use noticeable pauses only when the story truly changes direction.

Keep the delivery lively, but save the strongest energy for the most important moments.

"""

CAREGIVING_CONNECTED_PREFIX = """TTS the following story in natural, engaging English.

Create a gentle but clear emotional arc across the passage.

Begin in a familiar, conversational way. Add a little more weight when explaining that the caregiver may also be old. Make "37.1 percent" clear and important without sounding dramatic. End with warmth and a strong sense that the caregiver also deserves support.

Give light emphasis to "both people were 75 or older" and "may also need support."

Stay calm but actively engaged with the listener. Do not sound gloomy, sleepy, distant, or overly formal.

Speak directly to one interested listener in a warm and natural way.

Carry the meaning naturally across sentence boundaries. Do not treat every short sentence as a separate announcement. Group related sentences into complete thoughts, while keeping the important contrasts clear.

Use noticeable pauses only when the topic or point changes.

"""

COMBOS = [
    {
        "topic": "hanshin", "voice": "Aoede", "text": HANSHIN_TEXT,
        "condition": "connected", "style_prefix": HANSHIN_CONNECTED_PREFIX,
        "out_file": "er001b4_hanshin_aoede_connected.wav",
        "baseline_file": "er001b3_hanshin_aoede_minimal.wav",
        "baseline_condition": "minimal(ER-001B-3)",
    },
    {
        "topic": "caregiving", "voice": "Charon", "text": CAREGIVING_TEXT,
        "condition": "connected", "style_prefix": CAREGIVING_CONNECTED_PREFIX,
        "out_file": "er001b4_caregiving_charon_connected.wav",
        "baseline_file": "er001b3_caregiving_charon_emotional_arc.wav",
        "baseline_condition": "emotional_arc(ER-001B-3)",
    },
]

# 比較基準の2音声は再生成しない。er001b3_manifest.jsonの記録値をそのまま参照する。
BASELINE_REUSED = [
    {
        "topic": "hanshin", "voice": "Aoede", "condition": "minimal(ER-001B-3)",
        "out_file": "er001b3_hanshin_aoede_minimal.wav",
        "text": HANSHIN_TEXT,
        "style_prefix": ("TTS the following sports story in natural, engaging English.\n\n"
                          "Sound like a friendly radio host sharing an exciting close game with listeners. "
                          "Keep the delivery clear and natural. Do not shout or sound like a movie trailer.\n\n"),
        "duration_seconds": 26.5,
        "source": "er001b3_manifest.json",
        "reused": True,
    },
    {
        "topic": "caregiving", "voice": "Charon", "condition": "emotional_arc(ER-001B-3)",
        "out_file": "er001b3_caregiving_charon_emotional_arc.wav",
        "text": CAREGIVING_TEXT,
        "style_prefix": ("TTS the following story in natural, engaging English.\n\n"
                          "Create a gentle but clear emotional arc across the passage.\n\n"
                          "Begin in a familiar, conversational way. Add a little more weight when explaining "
                          "that the caregiver may also be old. Make \"37.1 percent\" clear and important without "
                          "sounding dramatic. End with warmth and a strong sense that the caregiver also deserves "
                          "support.\n\n"
                          "Give light emphasis to \"both people were 75 or older\" and \"may also need support.\"\n\n"
                          "Stay calm but actively engaged with the listener. Do not sound gloomy, sleepy, distant, "
                          "or overly formal.\n\n"),
        "duration_seconds": 32.5,
        "source": "er001b3_manifest.json",
        "reused": True,
    },
]

# ============================================================
# ブロック3: 道具(er001b3_direction_compare.pyから流用: 音量正規化)
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
# ブロック4: クライアント初期化・モデル設定(er001b3_direction_compare.pyと同じ)
# ============================================================
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-2.5-pro-preview-tts"
LANGUAGE_CODE = "en-us"
SAMPLE_RATE = 24000
MAX_RETRY = 2
TTS_TIMEOUT_MS = 120_000
TIER1_DAILY_LIMIT = 50

USAGE_LOG_PATH = ".tts_usage_log.jsonl"  # tts_test.py以降の全スクリプトと共有

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
        "script": "er001b4_connected_narration.py",
        "pattern": label,
    }
    with open(USAGE_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def build_narrator_speech_config(voice_name):
    """1人読み用の声設定(er001b3_direction_compare.pyと同じ形)。"""
    return types.SpeechConfig(
        language_code=LANGUAGE_CODE,
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice_name)
        ),
    )

def call_tts(prompt, speech_config, label="clip"):
    """Gemini-TTSを呼び出す共通の道具(er001b3_direction_compare.pyと同じ設計)。"""
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
total_calls = len(COMBOS)  # 比較基準は再生成しないため、新規呼び出しは2回のみ

today_so_far = load_today_call_count()
projected_total = today_so_far + total_calls

print("ER-001B-4: つながった語りの比較(話者・比較基準固定)")
print(f"新規生成する組み合わせ数: {total_calls} 個(比較基準2音声は既存を再利用・再生成なし)")
print(f"本日ここまでの呼び出し回数(全スクリプト合算の見立て): {today_so_far} 回")
print(f"今回追加で必要な回数: {total_calls} 回")
print(f"実行後の見込み合計: {projected_total} 回 / Tier1日次上限(実測): {TIER1_DAILY_LIMIT} 回")
if projected_total > TIER1_DAILY_LIMIT:
    print("⚠ 警告: 実行後の見込み合計が日次上限を超える可能性があります。")
elif projected_total > TIER1_DAILY_LIMIT * 0.8:
    print("⚠ 注意: 実行後の見込み合計が日次上限の8割を超えます。残り枠にご注意ください。")
print()

# ============================================================
# ブロック6: 「つながった語り」条件を生成 + 比較基準(再利用)を含めたマニフェスト記録
# ============================================================
manifest = {
    "experiment_id": "ER-001B-4",
    "model": MODEL_NAME,
    "language_code": LANGUAGE_CODE,
    "sample_rate": SAMPLE_RATE,
    "fixed_voice_assignment": {"hanshin": "Aoede", "caregiving": "Charon"},
    "note": (
        "比較基準(baseline_reused)はER-001B-3の既存音声を再利用しており、今回は再生成していない。"
        "比較基準のtext/style_prefixはer001b3_manifest.jsonの記録値。"
        "connected条件のtextは比較基準と改行を含め完全に同一(HANSHIN_TEXT/CAREGIVING_TEXTのassertで起動時に検証済み)。"
        "connected条件の演技指示は、比較基準の指示文に「つながった語り」の指示を追加したのみで、"
        "既存の指示文自体は変更していない。"
    ),
    "clips": [],
}

for entry in BASELINE_REUSED:
    manifest["clips"].append(entry)

for i, combo in enumerate(COMBOS, 1):
    topic = combo["topic"]
    voice = combo["voice"]
    condition = combo["condition"]
    text = combo["text"]
    style_prefix = combo["style_prefix"]
    out_wav = combo["out_file"]
    label = f"{topic}_{voice}_{condition}"

    print(f"[{i}/{total_calls}] {topic} × {voice} × {condition} を生成中"
          f"(比較基準: {combo['baseline_file']} / {combo['baseline_condition']})...", flush=True)
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
        "baseline_file": combo["baseline_file"],
        "baseline_condition": combo["baseline_condition"],
        "duration_seconds": round(seconds, 1),
        "generated_at": datetime.now().isoformat(),
        "reused": False,
    })

manifest_path = "er001b4_manifest.json"
with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)

print("-" * 50)
print(f"新規{total_calls}音声の生成が完了しました(比較基準2音声は既存を再利用)。")
print(f"実験ID・題材・話者・条件・演技指示・比較基準の記録を {manifest_path} に保存しました。")
