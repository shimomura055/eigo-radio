# ============================================================
# tts_japanese_demo.py - 日本語音声化のデモ用・軽量単発スクリプト
# ============================================================
# 本番パイプラインへの組み込みは目的ではなく、日本語での聞き比べ用の
# デモ。tts_test.pyのモデル/声/call_tts()/normalize_pcm()を流用し、
# speech_configのlanguage_codeだけを"ja-JP"に変更している。
# 動的演技指導(STYLE_PREFIXの自動生成)は今回のデモ対象外。
#
# 使い方:
#   python tts_japanese_demo.py

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
# ブロック1: 固定の対話(日本語・10ターン)
# ============================================================
DEMO_SCRIPT = [
    {"speaker": "MAYA", "text": "レオ、私のスマホが「日本が国債をNISAに入れようとしている」っていう投稿だらけなんだけど。これ、本当に起きてるの?"},
    {"speaker": "LEO", "text": "いや、まだだよ。片山さつき財務大臣が、ある変更を検討しているところなんだ。個人向け国債を、NISAの非課税口座の中で持てるようにする、ということを考えているんだよ。"},
    {"speaker": "MAYA", "text": "じゃあ、今の口座ではそれができないってこと?"},
    {"speaker": "LEO", "text": "そう、できない。これは提案であって、新しいルールじゃないんだ。ネット上の人たちは、もう始まったかのように話しているけど、まだ始まっていない。国債は今も、普段のNISAの選択肢の外にあるんだよ。"},
    {"speaker": "MAYA", "text": "つまり、見出しが「議論」を「決定済みのこと」みたいに見せてるってことだね?"},
    {"speaker": "LEO", "text": "その通り。片山氏は、普通の貯蓄者にとって、もっと魅力的なものを作ろうとしているんだ。日本の国債を直接買うことを、人々に考えてほしいと思っている。これをただのNISAの定例更新だと見てほしくないんだよ。"},
    {"speaker": "MAYA", "text": "じゃあ彼女は、普通の人たちに国債に興味を持ってほしいってこと?"},
    {"speaker": "LEO", "text": "そう。彼女はただアプリの中のリストを書き換えているわけじゃない。人々が実際に選びたくなるような商品を求めているんだ。だからこそ、NISAのルールだけじゃなく、国債そのものもこの話の一部なんだよ。"},
    {"speaker": "MAYA", "text": "ああ、じゃあ彼女は投資口座を持っている人たちだけじゃなく、もっと広く考えているんだね。"},
    {"speaker": "LEO", "text": "そうだね。彼女自身の言葉で言えば、日本は家計と年金基金の両方に、日本の投資へお金を入れる手助けをすべきだと考えている。この2つは、どちらもすごく大きな、たくさんのお金を持つグループなんだ。"},
]

# ============================================================
# ブロック2: 道具(tts_test.pyから流用: 音量正規化・安全なチャンク分割)
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
    """単独話者チャンクが出た場合は直前のチャンクに合体させる(tts_test.pyと同じ考え方)。"""
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
# ブロック3: クライアント初期化・モデル/声の設定(tts_test.pyと同じ)
# ============================================================
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-2.5-pro-preview-tts"
VOICE_MAYA = "Aoede"
VOICE_LEO = "Iapetus"

SAMPLE_RATE = 24000
CHUNK_SIZE = 2
PAUSE = b"\x00\x00" * int(SAMPLE_RATE * 0.2)
MAX_RETRY = 2
TTS_TIMEOUT_MS = 120_000

# 日本語向けの簡単な前置き(動的演技指導は今回のデモでは使わない)
STYLE_PREFIX = "以下のMAYAとLEOの会話を、自然な日本語の会話として音声化してください。\n\n"

def build_speech_config():
    """language_codeを日本語("ja-JP")にした点のみ、tts_test.pyのbuild_speech_config()と異なる。"""
    return types.SpeechConfig(
        language_code="ja-JP",
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

def call_tts(prompt, speech_config, label="chunk"):
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
# ブロック4: チャンクごとに音声化して連結・保存
# ============================================================
out_wav = "demo_ja.wav"
chunks = build_safe_chunks(DEMO_SCRIPT, CHUNK_SIZE)
print(f"日本語デモ: 全{len(DEMO_SCRIPT)}ターンを{len(chunks)}チャンクに分けて音声化します")

audio = b""
for i, chunk in enumerate(chunks, 1):
    dialogue_lines = "\n".join(f'{t["speaker"]}: {t["text"]}' for t in chunk)
    prompt = STYLE_PREFIX + dialogue_lines
    print(f"  チャンク {i}/{len(chunks)} を音声化中...", flush=True)
    pcm = call_tts(prompt, build_speech_config(), label=f"chunk {i}/{len(chunks)}")
    audio += pcm + PAUSE

with wave.open(out_wav, "wb") as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(SAMPLE_RATE)
    w.writeframes(audio)

seconds = len(audio) / (SAMPLE_RATE * 2)
print("-" * 50)
print(f"{out_wav} を保存しました(約 {seconds:.1f}秒)")
