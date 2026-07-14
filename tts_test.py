# ============================================================
# tts_test.py (Gemini-TTS版・チャンク分割対応 + 声の性別ブレ対策)
# ============================================================

import glob
import json
import wave
import os
import re
import time
import array
import sys

# ============================================================
# ブロック1: レベル指定の読み取り(--level=XX)
# 実行例: python tts_test.py --level=B1
# デフォルト値は持たない(generate_test.pyとデフォルトが食い違い、指定漏れ事故につながるため指定必須)
# ============================================================
LEVEL_KEY = None
for arg in sys.argv:
    if arg.startswith("--level="):
        LEVEL_KEY = arg.split("=", 1)[1].upper()
if LEVEL_KEY is None:
    raise SystemExit("エラー: --level=A2/B1/B2 のいずれかを指定してください(例: python tts_test.py --level=B1)")

from dotenv import load_dotenv
from google import genai
from google.genai import types
from levels import LEVELS

# ============================================================
# ブロック2: 道具(音量正規化・安全なチャンク分割)
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

def build_safe_chunks(turns, chunk_size):
    """
    通常はCHUNK_SIZEごとに区切るが、単独話者(MAYA/LEOのどちらか片方だけ)
    になってしまうチャンクがあれば、直前のチャンクに合体させる。
    これにより「2人設定のリクエストなのに1人分しか話さない」状態を防ぎ、
    声の入れ替わりバグの引き金を断つ狙い。
    (旧版は最後のチャンクだけをチェックしていたが、全チャンクを対象にする版に修正)
    """
    chunks = [turns[i:i + chunk_size] for i in range(0, len(turns), chunk_size)]
    merged = []
    for chunk in chunks:
        speakers = {t["speaker"] for t in chunk}
        if len(speakers) < 2 and merged:
            merged[-1] = merged[-1] + chunk
        else:
            merged.append(chunk)
    return merged

# ============================================================
# ブロック3: クライアント初期化・モデル/声の設定
# ============================================================
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-2.5-pro-preview-tts"  # proを試す
VOICE_MAYA = "Aoede"       # ← AI Studioで確認した名前(差し替え済)
VOICE_LEO = "Iapetus"      # ← ぶっきらぼう対策の候補(差し替え済)
VOICE_NARRATOR = "Charon"  # ← ①概要・②キーワードコーナー専用。1人読みなのでMAYA/LEOとは別の声にする

target_wpm = LEVELS[LEVEL_KEY]["wpm_range"]

# --- 声の性別ブレ対策: 男女を明示し、一貫性を保つよう念押し ---
STYLE_PREFIX = f"""TTS the following conversation between MAYA and LEO, in natural conversational English at around {target_wpm} words per minute.

MAYA is a woman with a warm, curious female voice, genuinely surprised when reacting - like a friendly co-host discovering something amazing.
LEO is a man with a warm, enthusiastic male voice, like a friendly science communicator sharing something he loves - never flat, curt, or lecturing.

React to each other as if this is a spontaneous conversation between two close colleagues, not a script being read aloud.

Keep each speaker's voice, gender, and tone completely consistent from their first line to their last line in this excerpt.

"""

SAMPLE_RATE = 24000
CHUNK_SIZE = 2           # 1チャンクあたりのターン数(交互台本なら2以上で単独話者は発生しない)
PAUSE = b"\x00\x00" * int(SAMPLE_RATE * 0.2)  # チャンク間0.2秒の無音
MAX_RETRY = 2            # 500エラー(既知の不具合)対策の再試行回数
TTS_TIMEOUT_MS = 120_000  # 1回のAPI呼び出しの上限(ミリ秒)。無応答ハング対策。通常は10〜42秒で完了する

# ============================================================
# ブロック4: 最新の原稿を読み込み、ターンを安全にチャンク分割
# ============================================================
latest = sorted(glob.glob(f"episode_{LEVEL_KEY}_*.json"))[-1]
out_wav = latest.replace(".json", "_gemini.wav")
print(f"読み込む原稿: {latest}")

with open(latest, "r", encoding="utf-8") as f:
    data = json.load(f)

turns = data["turns"]
chunks = build_safe_chunks(turns, CHUNK_SIZE)  # ← 単独話者チャンク防止版に変更
print(f"『{data['title']}』 全{len(turns)}ターンを{len(chunks)}チャンクに分けて音声化します")

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

def build_narrator_speech_config():
    """①概要(overview_intro)・②キーワードコーナー(keywords_intro)用。話者は1人だけなのでmulti_speaker設定は使わない。"""
    return types.SpeechConfig(
        language_code="en-us",
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=VOICE_NARRATOR)
        ),
    )

def call_tts(prompt, speech_config, label="chunk"):
    """
    Gemini-TTSを呼び出す共通の道具(単語コーナー・本編チャンクの両方から使う)。
    429(1日のクォータ切れ)は、待っても状況が変わらないため即座に諦めて
    分かりやすいメッセージを出す。それ以外のエラー(一時的な500番台など)は
    これまで通りMAX_RETRY回まで再試行する。
    labelはログ表示用の識別子(例: "overview", "keywords", "chunk 3/10")。
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
                # 抜き出せなかった場合は生のメッセージをそのまま出す(フォールバック)。
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
# ブロック4-5: ①概要(overview_intro)・②キーワードコーナー(keywords_intro)を
#              それぞれ別々にナレーター単独音声で先に生成
# ============================================================
overview_intro = data.get("overview_intro", "")
overview_pcm = b""
if overview_intro:
    print("①概要(overview_intro)を音声化中...", flush=True)
    overview_pcm = call_tts(overview_intro, build_narrator_speech_config(), label="overview")
else:
    print("  ※ この原稿にはoverview_introがありません(スキップ)")

keywords_intro = data.get("keywords_intro", "")
keywords_pcm = b""
if keywords_intro:
    print("②キーワードコーナー(keywords_intro)を音声化中...", flush=True)
    keywords_pcm = call_tts(keywords_intro, build_narrator_speech_config(), label="keywords")
else:
    print("  ※ この原稿にはkeywords_introがありません(スキップ)")

# ============================================================
# ブロック5: チャンクごとに生成(500エラー時は再試行)
# ============================================================
audio = b""
if overview_pcm:
    audio += overview_pcm + PAUSE
if keywords_pcm:
    audio += keywords_pcm + PAUSE
for i, chunk in enumerate(chunks, 1):
    dialogue_lines = "\n".join(f'{t["speaker"]}: {t["text"]}' for t in chunk)
    prompt = STYLE_PREFIX + dialogue_lines
    print(f"  チャンク {i}/{len(chunks)} を生成中...", flush=True)
    pcm = call_tts(prompt, build_speech_config(), label=f"chunk {i}/{len(chunks)}")
    audio += pcm + PAUSE

# ============================================================
# ブロック6: WAVファイルとして保存
# ============================================================
with wave.open(out_wav, "wb") as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(SAMPLE_RATE)
    w.writeframes(audio)

seconds = len(audio) / (SAMPLE_RATE * 2)
print("-" * 50)
print(f"{out_wav} を保存しました(約 {seconds/60:.1f} 分)")

# test