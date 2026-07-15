# ============================================================
# tts_style_test.py - STYLE_PREFIXの効果を検証する軽量テストハーネス
# ============================================================
# tts_test.py本体は変更せず、STYLE_PREFIXの候補を複数まとめて
# 音声化して聴き比べるための独立スクリプト。
# 固定の2行スクリプト(MAYA/LEO)を使うため、1パターンあたり
# API呼び出しは1回(1チャンク)で済む。
#
# 使い方:
#   python tts_style_test.py
#
# STYLE_PREFIX_CANDIDATESのリストを編集して候補を差し替える。

import wave
import os
import re
import time
import array
import sys

from dotenv import load_dotenv
from google import genai
from google.genai import types

# ============================================================
# ブロック1: 固定スクリプト(2行・MAYA/LEO)
# ============================================================
FIXED_SCRIPT = [
    {"speaker": "MAYA", "text": "Wait, why is everyone saying government bonds are suddenly going into NISA? Did something change while I was asleep? People online sound like I can buy them there today."},
    {"speaker": "LEO", "text": "No, they are not suddenly inside it. Finance Minister Satsuki Katayama invited ordinary people to think about buying more Japanese assets."},
]

# ============================================================
# ブロック2: STYLE_PREFIX候補(プレースホルダー。中身は後で差し替える)
# ============================================================
STYLE_PREFIX_CANDIDATES = [
    {
        "id": "01",
        "label": "ダミー候補1(プレースホルダー)",
        "prefix": """TTS the following conversation between MAYA and LEO, in natural conversational English.

MAYA is a woman with a warm, curious female voice.
LEO is a man with a warm, enthusiastic male voice.

""",
    },
    {
        "id": "02",
        "label": "ダミー候補2(プレースホルダー)",
        "prefix": """TTS the following conversation between MAYA and LEO, in natural conversational English at a slightly faster pace.

MAYA is a woman with a warm, curious female voice, genuinely surprised when reacting.
LEO is a man with a warm, enthusiastic male voice, like a friendly science communicator.

Keep each speaker's voice, gender, and tone completely consistent from their first line to their last line in this excerpt.

""",
    },
    {
        "id": "03",
        "label": "ダミー候補3(プレースホルダー)",
        "prefix": """TTS the following conversation between MAYA and LEO.

React to each other as if this is a spontaneous conversation between two close colleagues, not a script being read aloud.

""",
    },
]

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
# ブロック4: クライアント初期化・モデル/声の設定(tts_test.pyと同じ)
# ============================================================
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-2.5-pro-preview-tts"
VOICE_MAYA = "Aoede"
VOICE_LEO = "Iapetus"

SAMPLE_RATE = 24000
MAX_RETRY = 2             # 500エラー(既知の不具合)対策の再試行回数
TTS_TIMEOUT_MS = 120_000  # 1回のAPI呼び出しの上限(ミリ秒)。無応答ハング対策。

# Tier1の日次上限(gemini-2.5-pro-tts: 50回/日、実測値)を踏まえた警告しきい値。
# このスクリプト単体でこの回数を超えるパターン数を指定した場合、警告のみ出して続行する。
TIER1_DAILY_WARNING_THRESHOLD = 30

def build_speech_config():
    return types.SpeechConfig(
        language_code="en-us",
        multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
            speaker_voice_configs=[
                types.SpeakerVoiceConfig(
                    speaker="MAYA",
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=VOICE_MAYA)),
                ),
                types.SpeakerVoiceConfig(
                    speaker="LEO",
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=VOICE_LEO)),
                ),
            ]
        ),
    )

def call_tts(prompt, speech_config, label="pattern"):
    """
    Gemini-TTSを呼び出す共通の道具(tts_test.pyのcall_tts()と同じ設計)。
    429(1日のクォータ切れ)は、待っても状況が変わらないため即座に諦めて
    分かりやすいメッセージを出す。それ以外のエラー(一時的な500番台など)は
    MAX_RETRY回まで再試行する。
    """
    for attempt in range(1, MAX_RETRY + 2):
        start = time.time()
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],  # ← 2.5系モデルは明示指定が必須
                    speech_config=speech_config,
                    http_options=types.HttpOptions(timeout=TTS_TIMEOUT_MS),  # 無応答ハング対策
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
                # モデルごとに1日の上限リクエスト数は異なるため、固定の数字は埋め込まず、
                # エラーメッセージ本体からquotaValue/quotaMetric/modelを都度抜き出して表示する。
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
# ブロック5: 事前表示(パターン数・API呼び出し回数・警告)
# ============================================================
dialogue_lines = "\n".join(f'{t["speaker"]}: {t["text"]}' for t in FIXED_SCRIPT)

total_patterns = len(STYLE_PREFIX_CANDIDATES)
total_calls = total_patterns  # 固定スクリプトは1チャンクなので、1パターン=API呼び出し1回

print(f"STYLE_PREFIXパターン数: {total_patterns} 個")
print(f"必要なAPI呼び出し回数: {total_calls} 回(1パターン=1回、固定スクリプトが1チャンクのため)")
if total_calls > TIER1_DAILY_WARNING_THRESHOLD:
    print(f"⚠ 警告: Tier1の日次上限(gemini-2.5-pro-tts、実測50回/日)に対して、"
          f"このスクリプト単体で{total_calls}回消費します。他の作業分の枠が残らない可能性があります。")
print()

# ============================================================
# ブロック6: パターンごとに音声化して連番保存
# ============================================================
for i, candidate in enumerate(STYLE_PREFIX_CANDIDATES, 1):
    pattern_id = candidate["id"]
    label = candidate["label"]
    prefix = candidate["prefix"]
    out_wav = f"style_test_{pattern_id}.wav"

    print(f"[{i}/{total_patterns}] パターン{pattern_id}({label})を生成中...", flush=True)
    prompt = prefix + dialogue_lines
    pcm = call_tts(prompt, build_speech_config(), label=f"pattern {pattern_id}")

    with wave.open(out_wav, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        w.writeframes(pcm)

    seconds = len(pcm) / (SAMPLE_RATE * 2)
    print(f"  → {out_wav} を保存しました(約 {seconds:.1f}秒)")
    print()

print("-" * 50)
print(f"全{total_patterns}パターンの音声化が完了しました。")
