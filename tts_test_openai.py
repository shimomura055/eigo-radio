# ============================================================
# tts_test_openai.py (OpenAI TTS版・gpt-4o-mini-tts使用)
# ============================================================
# Geminiとの一番の違い: OpenAIのTTSは「1リクエスト=1人分のセリフ」しか
# 生成できない(マルチスピーカー機能がない)。そのためチャンク分割は不要になり、
# ターンごとに1回ずつAPIを呼び出す、よりシンプルな構造にしている。
# 副産物として、「2人設定なのに1人分しか渡さない」ことで起きていた
# Gemini側の性別ブレ問題は、構造的に発生しようがない。

import glob
import json
import wave
import os
import time
import array
import sys

# ============================================================
# ブロック1: レベル指定の読み取り(--level=XX)
# ============================================================
LEVEL_KEY = "A2"
for arg in sys.argv:
    if arg.startswith("--level="):
        LEVEL_KEY = arg.split("=", 1)[1].upper()

from dotenv import load_dotenv
from openai import OpenAI
from levels import LEVELS

# ============================================================
# ブロック2: 道具(音量正規化)
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
# ブロック3: クライアント初期化・モデル/声の設定
# ============================================================
load_dotenv()
client = OpenAI()  # .envのOPENAI_API_KEYを自動で読む

MODEL_NAME = "gpt-4o-mini-tts"  # OpenAIの最新TTSモデル(instructionsで声の演技を指定できる)

# --- 声の割り当て ---
# 声の名前一覧(2026年7月時点): alloy, ash, ballad, cedar, coral, echo, fable,
# marin, nova, onyx, sage, shimmer, verse
# 実際の声質はOpenAI.fm(https://openai.fm)のデモで試聴して選ぶのが確実。
# ここでは一般に「女性寄り」「男性寄り」とされる声を仮に割り当てている。
VOICE_MAYA = "coral"       # 女性寄りの声(仮。合わなければ nova / shimmer / sage に差し替え可)
VOICE_LEO = "echo"         # 男性寄りの声(仮。合わなければ onyx / ash / fable に差し替え可)
VOICE_NARRATOR = "alloy"   # 単語コーナー用。MAYA/LEOと被らない声にする

# instructionsは「話し方の演技指導」。ここで性別・トーンを言葉で念押しする。
MAYA_INSTRUCTIONS = (
    "Voice: a warm, curious woman, like a friendly co-host. "
    "Tone: genuinely surprised and engaged when reacting. "
    "Pace: natural conversational speed, not rushed."
)
LEO_INSTRUCTIONS = (
    "Voice: a warm, enthusiastic man, like a friendly science communicator. "
    "Tone: never flat, curt, or lecturing - always sharing something he loves. "
    "Pace: natural conversational speed, not rushed."
)
NARRATOR_INSTRUCTIONS = (
    "Voice: a clear, friendly narrator introducing vocabulary to English learners. "
    "Tone: warm and encouraging, not robotic or school-like."
)

SAMPLE_RATE = 24000  # OpenAIのPCM出力は常に24kHz固定(公式ドキュメント記載)
PAUSE = b"\x00\x00" * int(SAMPLE_RATE * 0.2)  # ターン間0.2秒の無音
MAX_RETRY = 2

def call_tts(text, voice, instructions):
    """
    OpenAI TTSを呼び出す共通の道具。
    レート制限(429)は待っても状況が変わらないことが多いため、即座に諦めて
    分かりやすいメッセージを出す。それ以外の一時的なエラーはMAX_RETRY回まで再試行する。
    """
    for attempt in range(1, MAX_RETRY + 2):
        try:
            response = client.audio.speech.create(
                model=MODEL_NAME,
                voice=voice,
                input=text,
                instructions=instructions,
                response_format="pcm",
            )
            return normalize_pcm(response.content)
        except Exception as e:
            msg = str(e)
            if "rate_limit" in msg.lower() or "429" in msg:
                print("  → レート制限(429)に達しました。")
                print("     再試行しても変わらない可能性が高いため、ここで中止します。")
                print(f"     詳細: {msg[:200]}")
                sys.exit(1)
            print(f"    → エラー(試行{attempt}回目): {e}")
            if attempt > MAX_RETRY:
                raise
            time.sleep(2)

# ============================================================
# ブロック4: 最新の原稿を読み込む
# ============================================================
latest = sorted(glob.glob(f"episode_{LEVEL_KEY}_*.json"))[-1]
out_wav = latest.replace(".json", "_openai.wav")
print(f"読み込む原稿: {latest}")

with open(latest, "r", encoding="utf-8") as f:
    data = json.load(f)

turns = data["turns"]
print(f"『{data['title']}』 全{len(turns)}ターンを1ターンずつ音声化します(OpenAIはマルチスピーカー非対応のため)")

# ============================================================
# ブロック4-5: 単語コーナー(vocab_intro)をナレーター音声で先に生成
# ============================================================
vocab_intro = data.get("vocab_intro", "")
vocab_pcm = b""
if vocab_intro:
    print("単語コーナー(vocab_intro)を音声化中...")
    vocab_pcm = call_tts(vocab_intro, VOICE_NARRATOR, NARRATOR_INSTRUCTIONS)
else:
    print("  ※ この原稿にはvocab_introがありません(スキップ)")

# ============================================================
# ブロック5: ターンごとに生成
# ============================================================
audio = vocab_pcm + PAUSE if vocab_pcm else b""
for i, turn in enumerate(turns, 1):
    speaker = turn["speaker"]
    if speaker == "MAYA":
        voice, instructions = VOICE_MAYA, MAYA_INSTRUCTIONS
    else:
        voice, instructions = VOICE_LEO, LEO_INSTRUCTIONS

    print(f"  ターン {i}/{len(turns)} ({speaker}) を生成中...")
    pcm = call_tts(turn["text"], voice, instructions)
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