# ============================================================
# tts_style_test.py - STYLE_PREFIXの効果を検証する軽量テストハーネス
# ============================================================
# tts_test.py本体は変更せず、STYLE_PREFIXの候補を複数まとめて
# 音声化して聴き比べるための独立スクリプト。
# 固定の2行スクリプト(MAYA/LEO)を使うため、1パターンあたり
# API呼び出しは1回(1チャンク)で済む。
#
# 使い方:
#   python tts_style_test.py                … 全パターンを実行
#   python tts_style_test.py --only=H,I,J    … name(または先頭の記号)が一致するパターンだけ実行
#
# STYLE_PREFIX_CANDIDATESのリストを編集して候補を差し替える。

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
# ブロック1: 固定スクリプト(2行・MAYA/LEO)
# ============================================================
FIXED_SCRIPT = [
    {"speaker": "MAYA", "text": "Wait, why is everyone saying government bonds are suddenly going into NISA? Did something change while I was asleep? People online sound like I can buy them there today."},
    {"speaker": "LEO", "text": "No, they are not suddenly inside it. Finance Minister Satsuki Katayama invited ordinary people to think about buying more Japanese assets."},
]

# F_inline_stage_directions専用: 角括弧の演技指示をセリフ本文に埋め込んだ版。
# このパターンのときだけFIXED_SCRIPTの代わりにこちらを使う。
FIXED_SCRIPT_WITH_DIRECTIONS = [
    {"speaker": "MAYA", "text": "[surprised, half-laughing at her own confusion, rising pitch] Wait, why is everyone saying government bonds are suddenly going into NISA? Did something change while I was asleep? People online sound like I can buy them there today."},
    {"speaker": "LEO", "text": "[pause, then calm and reassuring] No, they are not suddenly inside it. Finance Minister Satsuki Katayama invited ordinary people to think about buying more Japanese assets."},
]

# ============================================================
# ブロック2: STYLE_PREFIX候補
# ============================================================
STYLE_PREFIX_CANDIDATES = [
    {
        "name": "00_current",
        "desc": "現行版(比較の基準)",
        "prefix": """TTS the following conversation between MAYA and LEO, in natural conversational English at around 125-140 words per minute.

MAYA is a woman with a warm, curious female voice, genuinely surprised when reacting - like a friendly co-host discovering something amazing.
LEO is a man with a warm, enthusiastic male voice, like a friendly science communicator sharing something he loves - never flat, curt, or lecturing.

React to each other as if this is a spontaneous conversation between two close colleagues, not a script being read aloud.

Keep each speaker's voice, gender, and tone completely consistent from their first line to their last line in this excerpt.

""",
    },
    {
        "name": "A_line_by_line_emotion",
        "desc": "セリフごとの感情の推移を直接指定",
        "prefix": """TTS the following two lines at around 125-140 words per minute.

MAYA's line carries genuine surprise and confusion - like she just read something online that doesn't add up, and she's half-laughing at her own confusion while asking. Her pitch should rise on "suddenly" and "today".

LEO's line is a warm, gentle correction - reassuring, patient, like clearing up a friend's misunderstanding without making her feel silly. Slightly slower pace than MAYA's line.

""",
    },
    {
        "name": "B_voice_actor_direction",
        "desc": "声優的な演技指導(呼吸・間・抑揚)",
        "prefix": """TTS the following conversation between MAYA and LEO, 125-140 words per minute.
Direct this like a voice actor would:
- MAYA: a short intake of breath before speaking, as if she just looked up from her phone. Let her voice climb in pitch through the questions, then land slightly deflated on the last sentence.
- LEO: a beat of silence before he starts, then a calm, downward-inflected opening ("No,") that immediately signals reassurance before the explanation.
Keep both voices' gender and identity consistent throughout.

""",
    },
    {
        "name": "C_immersive_scene",
        "desc": "情景・没入型のシーン設定",
        "prefix": """This is a recording of two podcast co-hosts, MAYA (woman) and LEO (man), in a relaxed studio. MAYA just glanced at her phone mid-conversation and reacts out loud, genuinely puzzled. LEO, sitting across from her with his coffee, looks up and immediately, warmly sets her straight. TTS their exchange at 125-140 words per minute, capturing that exact moment - not a script reading.

""",
    },
    {
        "name": "D_stress_words",
        "desc": "強調語の明示",
        "prefix": """TTS the following conversation between MAYA (woman) and LEO (man) at around 125-140 words per minute, natural and conversational, not read aloud.

For MAYA's line, stress the words "suddenly" and "today" - her confusion centers on the unexpected timing.
For LEO's line, stress the word "No" and slow slightly on "ordinary people" - his point is that this is an invitation to regular citizens, not an official change.

""",
    },
    {
        "name": "E_minimal_control",
        "desc": "対照群(最小限の指示)",
        "prefix": """TTS this conversation between MAYA (woman) and LEO (man) naturally, 125-140 wpm.

""",
    },
    {
        "name": "F_inline_stage_directions",
        "desc": "セリフ本文に演技指示を埋め込み(角括弧)",
        "prefix": """TTS the following conversation between MAYA (woman) and LEO (man) at around 125-140 words per minute. Follow the bracketed direction before each line exactly, but do not speak the bracketed text itself aloud.

""",
    },
    {
        "name": "G_current_no_wpm",
        "desc": "現行版から話速指定のみ削除(速度固定が抑揚を抑えていないか検証)",
        "prefix": """TTS the following conversation between MAYA and LEO in natural conversational English.

MAYA is a woman with a warm, curious female voice, genuinely surprised when reacting - like a friendly co-host discovering something amazing.
LEO is a man with a warm, enthusiastic male voice, like a friendly science communicator sharing something he loves - never flat, curt, or lecturing.

React to each other as if this is a spontaneous conversation between two close colleagues, not a script being read aloud.

Keep each speaker's voice, gender, and tone completely consistent from their first line to their last line in this excerpt.

""",
    },
    {
        "name": "H_AD_combo",
        "desc": "A(感情の推移)+D(強調語の明示)",
        "prefix": """TTS the following two lines at around 125-140 words per minute.

MAYA's line carries genuine surprise and confusion - like she just read something online that doesn't add up, and she's half-laughing at her own confusion while asking. Her pitch should rise on "suddenly" and "today" - stress these two words clearly.

LEO's line is a warm, gentle correction - reassuring, patient, like clearing up a friend's misunderstanding without making her feel silly. Slightly slower pace than MAYA's line. Stress the word "No" at the start, and slow slightly on "ordinary people" - his point is that this is an invitation to regular citizens, not an official change.

""",
    },
    {
        "name": "I_AB_combo",
        "desc": "A(感情の推移)+B(声優的な演技指導)",
        "prefix": """TTS the following two lines at around 125-140 words per minute.

MAYA's line: take a short intake of breath before speaking, as if she just looked up from her phone. She carries genuine surprise and confusion - like she just read something online that doesn't add up, half-laughing at her own confusion while asking. Let her pitch climb through the questions on "suddenly" and "today", then land slightly deflated on the last sentence.

LEO's line: a beat of silence before he starts, then a calm, downward-inflected opening ("No,") that immediately signals reassurance. His line is a warm, gentle correction - patient, like clearing up a friend's misunderstanding without making her feel silly. Slightly slower pace than MAYA's line.

Keep both voices' gender and identity consistent throughout.

""",
    },
    {
        "name": "J_ABD_combo",
        "desc": "A+B+D(全部乗せ)",
        "prefix": """TTS the following two lines at around 125-140 words per minute.

MAYA's line: take a short intake of breath before speaking, as if she just looked up from her phone. She carries genuine surprise and confusion - like she just read something online that doesn't add up, half-laughing at her own confusion while asking. Let her pitch climb through the questions, then land slightly deflated on the last sentence. Stress the words "suddenly" and "today" clearly - her confusion centers on the unexpected timing.

LEO's line: a beat of silence before he starts, then a calm, downward-inflected opening ("No,") that immediately signals reassurance before the explanation. His line is a warm, gentle correction - patient, like clearing up a friend's misunderstanding without making her feel silly. Slightly slower pace than MAYA's line. Stress the word "No" and slow slightly on "ordinary people" - his point is that this is an invitation to regular citizens, not an official change.

Keep both voices' gender and identity consistent throughout.

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

# Tier1の日次上限(gemini-2.5-pro-tts: 50回/日、実測値)。
TIER1_DAILY_LIMIT = 50

# ============================================================
# ブロック4-5: 本日の呼び出し回数の見立て(このスクリプト自身の記録のみ)
# ============================================================
# Google側に「消費済みクォータを問い合わせる」手段がないため、このスクリプトが
# 自分で呼び出すたびに記録するローカルログから、本日ここまでの回数を見積もる。
# あくまでこのスクリプト経由の記録に限った「見立て」であり、tts_test.py等
# 他スクリプトからの呼び出しは含まれない点に注意。
USAGE_LOG_PATH = ".tts_usage_log.jsonl"

def load_today_call_count():
    """USAGE_LOG_PATHから、今日の日付のエントリ数を数える(このスクリプトの記録分のみ)。"""
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

def record_call(pattern_name):
    """1回のAPI呼び出しが成功するたびに、ログへ1行追記する。"""
    entry = {
        "date": date.today().isoformat(),
        "timestamp": datetime.now().isoformat(),
        "script": "tts_style_test.py",
        "pattern": pattern_name,
    }
    with open(USAGE_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

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
# ブロック5: --only=での絞り込み + 事前表示(パターン数・API呼び出し回数・警告)
# ============================================================
def build_dialogue_lines(script):
    return "\n".join(f'{t["speaker"]}: {t["text"]}' for t in script)

DEFAULT_DIALOGUE_LINES = build_dialogue_lines(FIXED_SCRIPT)
DIRECTIONS_DIALOGUE_LINES = build_dialogue_lines(FIXED_SCRIPT_WITH_DIRECTIONS)

# --- --only=H,I,J のような形で、name(または先頭の記号)が一致するパターンだけに絞る ---
ONLY_FILTER = None
for arg in sys.argv:
    if arg.startswith("--only="):
        ONLY_FILTER = [tok.strip() for tok in arg.split("=", 1)[1].split(",") if tok.strip()]

def matches_only_filter(candidate_name, filter_tokens):
    if filter_tokens is None:
        return True
    prefix = candidate_name.split("_")[0]
    return candidate_name in filter_tokens or prefix in filter_tokens

selected_candidates = [c for c in STYLE_PREFIX_CANDIDATES if matches_only_filter(c["name"], ONLY_FILTER)]
if ONLY_FILTER is not None and not selected_candidates:
    raise SystemExit(f"エラー: --onlyで指定された名前に一致するパターンがありません: {', '.join(ONLY_FILTER)}")

total_patterns = len(selected_candidates)
total_calls = total_patterns  # 固定スクリプトは1チャンクなので、1パターン=API呼び出し1回

today_so_far = load_today_call_count()
projected_total = today_so_far + total_calls

if ONLY_FILTER is not None:
    print(f"--only指定: {', '.join(ONLY_FILTER)} → {total_patterns} パターンに絞って実行します")
print(f"STYLE_PREFIXパターン数: {total_patterns} 個")
print(f"本日ここまでの呼び出し回数(このスクリプトの記録に基づく見立て。他スクリプト分は含まず): {today_so_far} 回")
print(f"今回追加で必要な回数: {total_calls} 回")
print(f"実行後の見込み合計: {projected_total} 回 / Tier1日次上限(実測): {TIER1_DAILY_LIMIT} 回")
if projected_total > TIER1_DAILY_LIMIT:
    print(f"⚠ 警告: 実行後の見込み合計が日次上限を超える可能性があります。"
          f"他スクリプトでの呼び出し分も含めると、既に上限に達している可能性があります。")
elif projected_total > TIER1_DAILY_LIMIT * 0.8:
    print(f"⚠ 注意: 実行後の見込み合計が日次上限の8割を超えます。残り枠にご注意ください。")
print()

# ============================================================
# ブロック6: パターンごとに音声化して連番保存
# ============================================================
for i, candidate in enumerate(selected_candidates, 1):
    name = candidate["name"]
    desc = candidate["desc"]
    prefix = candidate["prefix"]
    out_wav = f"style_test_{name}.wav"

    # F(角括弧の演技指示埋め込み)だけは、台詞本文自体も演技指示付きの版に差し替える。
    dialogue_lines = DIRECTIONS_DIALOGUE_LINES if name == "F_inline_stage_directions" else DEFAULT_DIALOGUE_LINES

    print(f"[{i}/{total_patterns}] パターン{name}({desc})を生成中...", flush=True)
    prompt = prefix + dialogue_lines
    pcm = call_tts(prompt, build_speech_config(), label=f"pattern {name}")
    record_call(name)

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
