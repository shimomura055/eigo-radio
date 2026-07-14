# ============================================================
# tts_test_azure.py (Azure AI Speech版・Neural HD音声使用)
# ============================================================
# Geminiとの一番の違い: AzureはSSML(音声合成用のXMLマークアップ)の中に
# 複数の<voice>タグを並べることで、会話全体を1回のリクエストで生成できる。
# 各セリフに声を明示的にタグ付けするので、Geminiのような
# 「話者の取り違え」が構造的に起こりようがない。

import glob
import json
import os
import sys
import html

# ============================================================
# ブロック1: レベル指定の読み取り(--level=XX)
# ============================================================
LEVEL_KEY = "A2"
for arg in sys.argv:
    if arg.startswith("--level="):
        LEVEL_KEY = arg.split("=", 1)[1].upper()

from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk

# ============================================================
# ブロック2: クライアント初期化・声の設定
# ============================================================
load_dotenv()
SPEECH_KEY = os.getenv("SPEECH_KEY")
SPEECH_REGION = os.getenv("SPEECH_REGION")

speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
# 24kHz・16bit・モノラルのWAVを直接指定(既存ファイルと音質を揃える)
speech_config.set_speech_synthesis_output_format(
    speechsdk.SpeechSynthesisOutputFormat.Riff24Khz16BitMonoPcm
)

# --- 声の割り当て(Dragon HD = Azureの最新高音質モデル) ---
# 声質はAzure AI Foundryの「Voice Gallery」で試聴してから最終決定するのが確実。
VOICE_MAYA = "en-US-Ava:DragonHDLatestNeural"       # 女性寄りの声(仮)
VOICE_LEO = "en-US-Andrew:DragonHDLatestNeural"     # 男性寄りの声(仮)
VOICE_NARRATOR = "en-US-Aria:DragonHDLatestNeural"  # 単語コーナー用。MAYA/LEOと被らない声(Emmaは未サポートだったため変更)

def esc(text):
    """SSMLはXML形式なので、&, <, > などの特殊文字をエスケープする必要がある。"""
    return html.escape(text, quote=False)

# ============================================================
# ブロック3: 最新の原稿を読み込む
# ============================================================
latest = sorted(glob.glob(f"episode_{LEVEL_KEY}_*.json"))[-1]
out_wav = latest.replace(".json", "_azure.wav")
print(f"読み込む原稿: {latest}")

with open(latest, "r", encoding="utf-8") as f:
    data = json.load(f)

turns = data["turns"]
vocab_intro = data.get("vocab_intro", "")
print(f"『{data['title']}』 全{len(turns)}ターンを1回のリクエストで音声化します")

# ============================================================
# ブロック4: SSMLを組み立てる(単語コーナー→本編を1つの文書にまとめる)
# ============================================================
voice_blocks = []

if vocab_intro:
    voice_blocks.append(
        f'<voice name="{VOICE_NARRATOR}">{esc(vocab_intro)}<break time="500ms"/></voice>'
    )
else:
    print("  ※ この原稿にはvocab_introがありません(スキップ)")

for turn in turns:
    voice_name = VOICE_MAYA if turn["speaker"] == "MAYA" else VOICE_LEO
    voice_blocks.append(
        f'<voice name="{voice_name}">{esc(turn["text"])}<break time="300ms"/></voice>'
    )

ssml = (
    '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" '
    'xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="en-US">'
    + "".join(voice_blocks)
    + "</speak>"
)

# ============================================================
# ブロック5: 音声化を実行(1リクエストで会話全体)
# ============================================================
audio_config = speechsdk.audio.AudioOutputConfig(filename=out_wav)
synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

print("音声化中(1リクエストで全体を生成)...")
result = synthesizer.speak_ssml_async(ssml).get()

if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
    print("-" * 50)
    print(f"{out_wav} を保存しました")
elif result.reason == speechsdk.ResultReason.Canceled:
    details = result.cancellation_details
    print(f"音声化が中止されました: {details.reason}")
    if details.reason == speechsdk.CancellationReason.Error:
        print(f"エラー詳細: {details.error_details}")
    sys.exit(1)