# ============================================================
# er001b5_full_narration_compare.py
# ER-001B-5: 3分版による共通ナレーション方針の検証
# ============================================================
# 目的: ER-001B-3/4の短尺比較で局所的に良かった条件
#   (阪神=Minimal+Connected / 老老介護=Emotional+Connected)を踏まえ、
# ジャンル非依存の「共通Emotional+Connected」指示が、約3分の全文でも
# 自然に機能するかを検証する。阪神ではMinimal+Connectedとの全文比較も行う。
#
# 台本の正本は、ユーザーから提供された以下の入力ファイル(このスクリプトが
# 内容を推測・生成することはない):
#   - er001b5_hanshin_script.json
#   - er001b5_caregiving_script.json
# タイトル・見出し・小見出し・本文を、JSON内に記録された順番のまま
# 読み上げ用テキストへ変換する。要約・短縮・加筆・言い換え・句読点の
# 変更は一切行わない。
#
# 長文TTSへの対応: 全文(阪神468語/老老介護329語)を1回のAPI呼び出しで
# 生成する事前検証を行ったところ、280秒のタイムアウトでも完了せず、
# 安定しないことを確認した(255語のセクション単体では79秒で成功)。
# そのため、9節で許可されている「セクション単位の分割生成」を採用する。
# 分割は必ずセクション境界(body / 見出しセクション / In One Line)で行い、
# 文の途中では分割しない。分割位置は同一台本を使う条件間で完全に同じにする
# (阪神の2条件は同じJSONから生成するため自動的に同じ分割位置になる)。
#
# er001b3/er001b4の「単独話者設定」「TTS呼び出し」「音量正規化」
# 「使用量ログ」「タイムアウト・エラー処理」の仕組みをそのまま流用する。
# 本番パイプライン(generate_test.py等)には一切手を加えない、
# 独立の軽量スクリプト。
#
# 使い方:
#   python er001b5_full_narration_compare.py

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
# ブロック1: 台本の正本を読み込み、セクション単位のチャンクへ分割
# ============================================================
HANSHIN_SCRIPT_PATH = "er001b5_hanshin_script.json"
CAREGIVING_SCRIPT_PATH = "er001b5_caregiving_script.json"

def load_script(path):
    if not os.path.isfile(path):
        raise SystemExit(
            f"エラー: 台本の正本 {path} が見つかりません。"
            f"内容を推測して生成することはできないため、正本ファイルを配置してから再実行してください。"
        )
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def build_narration_text(script):
    """
    JSON内のtitle/sections(body・section・subsections)を、記録された順番のまま
    プレーンテキストへ変換する(Markdown記号・JSONキー名は一切含めない)。
    段落間は空行(\n\n)で区切る。全文の記録・語数カウント用。
    """
    lines = [script["title"]]
    for section in script["sections"]:
        if section["type"] == "body":
            lines.extend(section["paragraphs"])
        elif section["type"] == "section":
            lines.append(section["heading"])
            if "paragraphs" in section:
                lines.extend(section["paragraphs"])
            if "subsections" in section:
                for sub in section["subsections"]:
                    lines.append(sub["heading"])
                    lines.extend(sub["paragraphs"])
    return "\n\n".join(lines)

def split_into_section_chunks(script):
    """
    セクション境界(body / 各見出しセクション)でチャンクに分割する。
    文の途中では絶対に分割しない。bodyチャンクにはタイトルを含める。
    戻り値: [(label, text), ...] のリスト(台本内の順番どおり)。
    """
    chunks = []
    body_section = next(s for s in script["sections"] if s["type"] == "body")
    chunks.append(("body", "\n\n".join([script["title"]] + body_section["paragraphs"])))

    for section in script["sections"]:
        if section["type"] != "section":
            continue
        lines = [section["heading"]]
        if "paragraphs" in section:
            lines.extend(section["paragraphs"])
        if "subsections" in section:
            for sub in section["subsections"]:
                lines.append(sub["heading"])
                lines.extend(sub["paragraphs"])
        chunks.append((section["heading"], "\n\n".join(lines)))
    return chunks

hanshin_script = load_script(HANSHIN_SCRIPT_PATH)
caregiving_script = load_script(CAREGIVING_SCRIPT_PATH)

HANSHIN_TEXT = build_narration_text(hanshin_script)
CAREGIVING_TEXT = build_narration_text(caregiving_script)

HANSHIN_CHUNKS = split_into_section_chunks(hanshin_script)
CAREGIVING_CHUNKS = split_into_section_chunks(caregiving_script)

# 阪神の2条件が同一の読み上げ本文・同一の分割位置を使うことを起動時に検証する。
_hanshin_chunks_check_a = split_into_section_chunks(hanshin_script)
_hanshin_chunks_check_b = split_into_section_chunks(hanshin_script)
assert [t for _, t in _hanshin_chunks_check_a] == [t for _, t in _hanshin_chunks_check_b], \
    "阪神の分割チャンクが再現できません(同一JSONからの生成で差異が発生しています)"
assert [l for l, _ in HANSHIN_CHUNKS] == ["body", "Today’s Tiger Points", "In One Line"], \
    "阪神の分割ラベルが想定と異なります"
assert [l for l, _ in CAREGIVING_CHUNKS] == ["body", "Today’s Care Points", "In One Line"], \
    "老老介護の分割ラベルが想定と異なります"

# ============================================================
# ブロック2: 演技指示
# ============================================================
HANSHIN_MINIMAL_CONNECTED_PREFIX = """TTS the following complete sports story in natural, engaging English.

Sound like a friendly radio host sharing an exciting close game with one interested listener. Keep the delivery clear, lively, and natural. Do not shout or sound like a movie trailer.

Carry the meaning naturally across sentence boundaries. Do not reset your pitch, energy, or rhythm after every sentence. Group related sentences into complete thoughts, and use noticeable pauses only when the story or section truly changes direction.

Keep enough variation for a full-length narration. Do not stay at maximum energy throughout. Save the strongest energy for the most important moments, and allow calmer explanatory passages to breathe.

Treat section headings as natural transitions within one continuous story, not as separate announcements.

"""

# 阪神・老老介護で完全に同一の文面を使う(ジャンル名・題材名は一切追加しない)。
COMMON_EMOTIONAL_CONNECTED_PREFIX = """TTS the following complete story in natural, engaging English.

Speak directly to one interested listener rather than announcing to a large crowd.

Create a natural emotional arc that follows the meaning already present in the script. Let the energy, weight, and pace rise or fall when the story itself changes. Do not add excitement, sadness, urgency, or drama that is not supported by the words.

Carry the meaning naturally across sentence boundaries. Do not reset your pitch, energy, or rhythm after every sentence. Group related sentences into complete thoughts, while keeping important contrasts and turning points clear.

Keep enough vocal variation for a full-length narration, but do not overact. Save stronger emphasis for genuinely important moments, and let explanatory passages sound calmer and more conversational.

Treat section headings as natural transitions within one continuous story, not as separate announcements.

Do not shout, sound like a movie trailer, become gloomy or sleepy, or read in a distant and overly formal newsreader style.

"""

COMBOS = [
    {
        "topic": "hanshin", "voice": "Aoede", "condition": "minimal_connected",
        "script_source_file": HANSHIN_SCRIPT_PATH,
        "full_text": HANSHIN_TEXT, "chunks": HANSHIN_CHUNKS,
        "style_prefix": HANSHIN_MINIMAL_CONNECTED_PREFIX,
        "out_file": "er001b5_hanshin_aoede_minimal_connected_full.wav",
    },
    {
        "topic": "hanshin", "voice": "Aoede", "condition": "emotional_connected",
        "script_source_file": HANSHIN_SCRIPT_PATH,
        "full_text": HANSHIN_TEXT, "chunks": HANSHIN_CHUNKS,
        "style_prefix": COMMON_EMOTIONAL_CONNECTED_PREFIX,
        "out_file": "er001b5_hanshin_aoede_emotional_connected_full.wav",
    },
    {
        "topic": "caregiving", "voice": "Charon", "condition": "emotional_connected",
        "script_source_file": CAREGIVING_SCRIPT_PATH,
        "full_text": CAREGIVING_TEXT, "chunks": CAREGIVING_CHUNKS,
        "style_prefix": COMMON_EMOTIONAL_CONNECTED_PREFIX,
        "out_file": "er001b5_caregiving_charon_emotional_connected_full.wav",
    },
]

# 阪神2条件で読み上げ本文が完全に同一であることを起動時に検証する(受入条件4・5)。
assert COMBOS[0]["full_text"] == COMBOS[1]["full_text"], \
    "阪神の2条件で読み上げ本文が一致していません"
assert [t for _, t in COMBOS[0]["chunks"]] == [t for _, t in COMBOS[1]["chunks"]], \
    "阪神の2条件で分割チャンクの本文が一致していません"

# 共通Emotional+Connected指示が阪神と老老介護で完全に同一であることを起動時に検証する(受入条件6)。
assert COMBOS[1]["style_prefix"] == COMBOS[2]["style_prefix"], \
    "共通Emotional+Connected指示が阪神と老老介護で一致していません"

# ============================================================
# ブロック3: 道具(er001b4_connected_narration.pyから流用: 音量正規化)
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
# ブロック4: クライアント初期化・モデル設定
# ============================================================
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-2.5-pro-preview-tts"
LANGUAGE_CODE = "en-us"
SAMPLE_RATE = 24000
MAX_RETRY = 2
TTS_TIMEOUT_MS = 150_000  # セクション単体(最大255語)は実測79秒で完了。余裕を持たせた値。
TIER1_DAILY_LIMIT = 50

# セクション境界(チャンク間)の無音。全クリップ・全チャンク間で同一の長さ・同一の生成方法を使う
# (音量差や不自然な無音を作らないため、後加工のフェード等は行わず、単純な無音のみ)。
SECTION_JOIN_PAUSE_SECONDS = 0.6
SECTION_JOIN_PAUSE = b"\x00\x00" * int(SAMPLE_RATE * SECTION_JOIN_PAUSE_SECONDS)

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
        "script": "er001b5_full_narration_compare.py",
        "pattern": label,
    }
    with open(USAGE_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def build_narrator_speech_config(voice_name):
    """1人読み用の声設定(er001b3/b4と同じ形)。"""
    return types.SpeechConfig(
        language_code=LANGUAGE_CODE,
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice_name)
        ),
    )

def call_tts(prompt, speech_config, label="clip"):
    """Gemini-TTSを呼び出す共通の道具(er001b3/b4と同じ設計)。"""
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
total_calls = sum(len(combo["chunks"]) for combo in COMBOS)

today_so_far = load_today_call_count()
projected_total = today_so_far + total_calls

print("ER-001B-5: 3分版による共通ナレーション方針の検証")
print(f"生成する音声数: {len(COMBOS)} 本(セクション分割のため合計API呼び出し回数: {total_calls} 回)")
for combo in COMBOS:
    labels = [l for l, _ in combo["chunks"]]
    print(f"  - {combo['topic']} × {combo['voice']} × {combo['condition']}: "
          f"{len(combo['chunks'])}チャンク({', '.join(labels)})")
print(f"本日ここまでの呼び出し回数(全スクリプト合算の見立て): {today_so_far} 回")
print(f"今回追加で必要な回数: {total_calls} 回")
print(f"実行後の見込み合計: {projected_total} 回 / Tier1日次上限(実測): {TIER1_DAILY_LIMIT} 回")
if projected_total > TIER1_DAILY_LIMIT:
    print("⚠ 警告: 実行後の見込み合計が日次上限を超える可能性があります。")
elif projected_total > TIER1_DAILY_LIMIT * 0.8:
    print("⚠ 注意: 実行後の見込み合計が日次上限の8割を超えます。残り枠にご注意ください。")
print()

# ============================================================
# ブロック6: 条件ごとにセクション単位で生成 → 結合 → 保存 + マニフェスト記録
# ============================================================
manifest = {
    "experiment_id": "ER-001B-5",
    "model": MODEL_NAME,
    "language_code": LANGUAGE_CODE,
    "sample_rate": SAMPLE_RATE,
    "fixed_voice_assignment": {"hanshin": "Aoede", "caregiving": "Charon"},
    "volume_normalized": True,
    "normalize_target_peak": 0.7,
    "long_text_handling": {
        "single_call_attempted": True,
        "single_call_result": (
            "阪神全文(468語/2686文字)を1回のAPI呼び出しで生成する事前検証を実施したが、"
            "タイムアウト280秒でも完了せず不安定だった(255語のセクション単体は79秒で成功)。"
            "そのため9節の規定に従い、セクション単位の分割生成を採用した。"
        ),
        "split_strategy": "文の途中では分割せず、セクション境界(body / 見出しセクション / In One Line)でのみ分割する。",
        "join_method": f"チャンクごとに音量正規化(target_peak=0.7)した後、チャンク間に{SECTION_JOIN_PAUSE_SECONDS}秒の無音のみを挿入して結合する。フェード等の後加工は行わない。",
        "join_pause_seconds": SECTION_JOIN_PAUSE_SECONDS,
        "consistency": "分割位置・結合方法・無音の長さ・音量正規化方式は、全3音声で完全に同一。阪神の2条件は同一JSONから生成しているため分割位置も自動的に一致する。",
    },
    "note": (
        "台本の正本はer001b5_hanshin_script.json / er001b5_caregiving_script.jsonで、"
        "ユーザーから提供された内容をそのまま保存したもの(要約・短縮・加筆・言い換え・句読点変更なし)。"
        "阪神の2条件は読み上げ本文が完全に同一(起動時assertで検証)。"
        "共通Emotional+Connected指示は阪神と老老介護で完全に同一(起動時assertで検証)。"
    ),
    "clips": [],
}

for i, combo in enumerate(COMBOS, 1):
    topic = combo["topic"]
    voice = combo["voice"]
    condition = combo["condition"]
    style_prefix = combo["style_prefix"]
    out_wav = combo["out_file"]
    chunks = combo["chunks"]
    speech_config = build_narrator_speech_config(voice)

    print(f"[{i}/{len(COMBOS)}] {topic} × {voice} × {condition} を生成中"
          f"({len(chunks)}チャンクに分割)...", flush=True)

    audio = b""
    chunk_records = []
    for j, (chunk_label, chunk_text) in enumerate(chunks, 1):
        label = f"{topic}_{voice}_{condition}_chunk{j}_{chunk_label}"
        print(f"  チャンク {j}/{len(chunks)}({chunk_label}, {len(chunk_text.split())}語)を生成中...", flush=True)
        prompt = style_prefix + chunk_text
        pcm = call_tts(prompt, speech_config, label=label)
        record_call(label)
        if j > 1:
            audio += SECTION_JOIN_PAUSE
        audio += pcm
        chunk_records.append({
            "index": j,
            "label": chunk_label,
            "word_count": len(chunk_text.split()),
            "char_count": len(chunk_text),
        })

    with wave.open(out_wav, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        w.writeframes(audio)

    seconds = len(audio) / (SAMPLE_RATE * 2)
    print(f"  → {out_wav} を保存しました(約 {seconds:.1f}秒 / {seconds/60:.2f}分)")
    print()

    full_text = combo["full_text"]
    manifest["clips"].append({
        "file": out_wav,
        "topic": topic,
        "voice": voice,
        "condition": condition,
        "script_source_file": combo["script_source_file"],
        "full_text": full_text,
        "style_prefix": style_prefix,
        "input_char_count": len(full_text),
        "word_count": len(full_text.split()),
        "duration_seconds": round(seconds, 1),
        "generated_at": datetime.now().isoformat(),
        "split_into_chunks": True,
        "chunk_count": len(chunks),
        "chunks": chunk_records,
        "join_pause_seconds": SECTION_JOIN_PAUSE_SECONDS,
    })

manifest_path = "er001b5_manifest.json"
with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)

print("-" * 50)
print(f"全{len(COMBOS)}音声の生成が完了しました(合計{total_calls}回のTTS呼び出し)。")
print(f"実験ID・題材・条件・演技指示・分割情報の記録を {manifest_path} に保存しました。")
