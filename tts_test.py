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
from datetime import date, datetime

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
from openai import OpenAI
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
openai_client = OpenAI()

MODEL_NAME = "gemini-2.5-pro-preview-tts"  # proを試す
MODEL_DIRECTOR = "gpt-5.6-luna"  # 演技指導(STYLE_PREFIX)の動的生成用(generate_test.pyのMODEL_PLANと同じ格)
VOICE_MAYA = "Aoede"       # ← AI Studioで確認した名前(差し替え済)
VOICE_LEO = "Iapetus"      # ← ぶっきらぼう対策の候補(差し替え済)
VOICE_NARRATOR = "Charon"  # ← ①概要・②キーワードコーナー専用。1人読みなのでMAYA/LEOとは別の声にする

target_wpm = LEVELS[LEVEL_KEY]["wpm_range"]

SAMPLE_RATE = 24000
CHUNK_SIZE = 2           # 1チャンクあたりのターン数(交互台本なら2以上で単独話者は発生しない)
PAUSE = b"\x00\x00" * int(SAMPLE_RATE * 0.2)  # チャンク間0.2秒の無音
MAX_RETRY = 2            # 500エラー(既知の不具合)対策の再試行回数
TTS_TIMEOUT_MS = 120_000  # 1回のAPI呼び出しの上限(ミリ秒)。無応答ハング対策。通常は10〜42秒で完了する

# ============================================================
# ブロック3-5: 演技指導(STYLE_PREFIX)をチャンクのセリフ内容から動的生成
# ============================================================
# tts_style_test.pyでの検証の結果、"I_AB_combo"方式(呼吸・間の演技指導 +
# セリフ内の具体的な単語を指定した感情の推移)が最も評価が高かったため、
# その構造をテンプレートとして、毎回のセリフ内容に応じてOpenAIに
# 演技指導を1行ずつ書かせ、STYLE_PREFIXを動的に組み立てる。
DIRECTION_PROMPT = """You are directing text-to-speech voice actors for a podcast dialogue between MAYA (a woman) and LEO (a man). Below is one chunk of their dialogue, in order.

For EACH line, write ONE direction paragraph that combines, in this order:
1. A breath/pause/gesture cue right before the line starts - but ONLY if it fits naturally. If the line continues directly from the flow of conversation with no natural beat before it, skip this part entirely rather than forcing one.
2. The emotional arc across the line, grounded STRICTLY in what this line's own words and context actually convey - never invent an emotion the text does not support.
3. 1-2 specific words copied from this line's own text that carry the emotional or informational weight, explicitly named as words to stress.
4. If relevant, this line's pace relative to the adjacent line from the other speaker (e.g. "slightly slower than LEO's line here").

Style reference (match only the shape/format of this example, not its content):
"take a short intake of breath before speaking, as if she just looked up from her phone. She carries genuine surprise and confusion - like she just read something online that doesn't add up, half-laughing at her own confusion while asking. Let her pitch climb through the questions on \"suddenly\" and \"today\", then land slightly deflated on the last sentence."

Dialogue lines (in order):
{lines_json}

Return ONLY valid JSON, with exactly one entry per line above, in the same order:
{{"directions": ["direction paragraph for line 1", "direction paragraph for line 2", "..."]}}"""

MAX_DIRECTION_RETRY = 2  # 演技指導生成(OpenAI呼び出し)の再試行回数

def generate_style_prefix(chunk, target_wpm):
    """
    チャンクの実際のセリフ内容をDIRECTION_PROMPTに渡し、行ごとの演技指導を
    生成した上で、I_AB_comboのテンプレート構造に当てはめてSTYLE_PREFIXを
    組み立てる。戻り値は (style_prefix文字列, 行ごとの演技指導リスト)。
    """
    lines_for_prompt = [{"speaker": t["speaker"], "text": t["text"]} for t in chunk]
    prompt = DIRECTION_PROMPT.format(
        lines_json=json.dumps(lines_for_prompt, ensure_ascii=False, indent=2))

    directions = None
    for attempt in range(1, MAX_DIRECTION_RETRY + 2):
        start = time.time()
        try:
            res = openai_client.chat.completions.create(
                model=MODEL_DIRECTOR,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
            )
            elapsed = time.time() - start
            out = json.loads(res.choices[0].message.content)
            directions = out["directions"]
            if len(directions) != len(chunk):
                raise RuntimeError(
                    f"演技指導の行数({len(directions)})がチャンクの行数({len(chunk)})と一致しません")
            print(f"    [演技指導生成] 所要時間: {elapsed:.1f}秒", flush=True)
            break
        except Exception as e:
            elapsed = time.time() - start
            print(f"    [演技指導生成] → エラー(試行{attempt}回目、{elapsed:.1f}秒後): {e}", flush=True)
            if attempt > MAX_DIRECTION_RETRY:
                raise
            time.sleep(2)

    lines = [f"TTS the following conversation between MAYA and LEO, at around {target_wpm} words per minute.", ""]
    for t, d in zip(chunk, directions):
        lines.append(f"{t['speaker']}'s line: {d}")
        lines.append("")
    lines.append("Keep each speaker's voice, gender, and tone completely consistent from their first line to their last line in this excerpt.")
    lines.append("")
    style_prefix = "\n".join(lines)
    return style_prefix, directions

# ============================================================
# ブロック3-6: 本日の呼び出し回数の見立て(Gemini TTS呼び出し用ログ)
# tts_style_test.pyと同じログファイルを共有し、両スクリプト合算で見立てる。
# ============================================================
TIER1_DAILY_LIMIT = 50  # gemini-2.5-pro-tts の日次上限(実測値)
USAGE_LOG_PATH = ".tts_usage_log.jsonl"

def load_today_call_count():
    """USAGE_LOG_PATHから、今日の日付のエントリ数を数える(tts_test.py・tts_style_test.py合算)。"""
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
    """Gemini TTS呼び出しが成功するたびに、ログへ1行追記する。"""
    entry = {
        "date": date.today().isoformat(),
        "timestamp": datetime.now().isoformat(),
        "script": "tts_test.py",
        "pattern": label,
    }
    with open(USAGE_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

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

overview_intro = data.get("overview_intro", "")
keywords_intro = data.get("keywords_intro", "")

# --- 事前表示: 本日の呼び出し回数の見立て(tts_style_test.pyと同じログを共有) ---
total_calls_needed = len(chunks) + (1 if overview_intro else 0) + (1 if keywords_intro else 0)
today_so_far = load_today_call_count()
projected_total = today_so_far + total_calls_needed

print(f"必要なGemini TTS呼び出し回数: {total_calls_needed} 回(概要{'1' if overview_intro else '0'} + "
      f"キーワード{'1' if keywords_intro else '0'} + 本編{len(chunks)}チャンク)")
print(f"本日ここまでの呼び出し回数(tts_test.py・tts_style_test.py合算の見立て): {today_so_far} 回")
print(f"実行後の見込み合計: {projected_total} 回 / Tier1日次上限(実測): {TIER1_DAILY_LIMIT} 回")
if projected_total > TIER1_DAILY_LIMIT:
    print("⚠ 警告: 実行後の見込み合計が日次上限を超える可能性があります。")
elif projected_total > TIER1_DAILY_LIMIT * 0.8:
    print("⚠ 注意: 実行後の見込み合計が日次上限の8割を超えます。残り枠にご注意ください。")

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
overview_pcm = b""
if overview_intro:
    print("①概要(overview_intro)を音声化中...", flush=True)
    overview_pcm = call_tts(overview_intro, build_narrator_speech_config(), label="overview")
    record_call("overview")
else:
    print("  ※ この原稿にはoverview_introがありません(スキップ)")

keywords_pcm = b""
if keywords_intro:
    print("②キーワードコーナー(keywords_intro)を音声化中...", flush=True)
    keywords_pcm = call_tts(keywords_intro, build_narrator_speech_config(), label="keywords")
    record_call("keywords")
else:
    print("  ※ この原稿にはkeywords_introがありません(スキップ)")

# ============================================================
# ブロック5: チャンクごとに演技指導を動的生成→音声化(500エラー時は再試行)
# ============================================================
audio = b""
if overview_pcm:
    audio += overview_pcm + PAUSE
if keywords_pcm:
    audio += keywords_pcm + PAUSE

direction_log = []  # 人間が後から確認できるよう、チャンクごとの演技指導を記録する
for i, chunk in enumerate(chunks, 1):
    dialogue_lines = "\n".join(f'{t["speaker"]}: {t["text"]}' for t in chunk)
    print(f"  チャンク {i}/{len(chunks)}: 演技指導を生成中...", flush=True)
    style_prefix, directions = generate_style_prefix(chunk, target_wpm)
    direction_log.append({
        "chunk": i,
        "turns": [{"speaker": t["speaker"], "text": t["text"], "direction": d}
                  for t, d in zip(chunk, directions)],
    })

    prompt = style_prefix + dialogue_lines
    print(f"  チャンク {i}/{len(chunks)} を音声化中...", flush=True)
    pcm = call_tts(prompt, build_speech_config(), label=f"chunk {i}/{len(chunks)}")
    record_call(f"chunk_{i}")
    audio += pcm + PAUSE

directions_path = latest.replace(".json", "_directions.json")
with open(directions_path, "w", encoding="utf-8") as f:
    json.dump(direction_log, f, ensure_ascii=False, indent=2)
print(f"演技指導の記録を {directions_path} に保存しました(内容確認用)。")

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