# ============================================================
# er001b7b_point_number_compare.py
# ER-001B-7B: ポイント番号の構造比較(阪神Today's Tiger Pointsのみ)
# ============================================================
# 目的: 阪神記事の"Today's Tiger Points"セクションについて、
# 現行構造(条件B0)と、各ポイントの前に"Point One."/"Point Two."を
# 追加した構造(条件B1)を、同一話者・同一Level 2指示で比較する。
# 違いは"Point One."/"Point Two."の有無だけにする。
#
# 承認済み正本(er001b5_hanshin_script.json)は変更しない。
# ポイント番号はこの比較専用のテキスト定数としてのみ追加し、
# 正本JSONやユーザー評価前の本番仕様には反映しない。
#
# ER-001B-6の「単独話者設定」「TTS呼び出し」「音量正規化」
# 「使用量ログ」「タイムアウト・エラー処理」の仕組みをそのまま
# 流用する。ER-001B-6のスクリプト・マニフェストには一切手を加えない
# 独立スクリプト。本番パイプライン(generate_test.py等)には影響しない。
#
# ER-001B-6Aで判明した教訓(埋め込み技術検品が見出し欠落を見逃す
# 偽陰性を起こし得る)を踏まえ、この技術検品では期待テキストと
# 検出すべき語句の出現回数を明示的にプロンプトへ渡す設計にしている。
#
# 使い方:
#   python er001b7b_point_number_compare.py

import wave
import io
import os
import re
import sys
import json
import time
import array
import hashlib
from datetime import date, datetime

from dotenv import load_dotenv
from google import genai
from google.genai import types

# ============================================================
# ブロック1: B0(現行構造)・B1(ポイント番号追加)の読み上げテキスト
# ============================================================
# 承認済み正本er001b5_hanshin_script.jsonの"Today's Tiger Points"セクション
# (heading + 2つのsubsections)と内容は完全に同一。この比較のためだけに、
# タスク指定のとおり見出しの後に句点を加えた読み上げ用テキストとして定義する
# (正本JSONファイル自体は変更しない)。
B0_TEXT = """Today’s Tiger Points.

A bitter first step for young Kesamaru.

Yuki Kesamaru took the mound hoping to earn his first professional win.

Instead, he met a Chunichi lineup that refused to stay quiet.

The Dragons fought back, and Bosler’s home run became the hardest moment of his night.

It was a bitter result, but one difficult start does not tell the whole story of a young pitcher.

Games like this can become important lessons. The pressure, the mistakes and the disappointment may all help him when his next chance arrives.

Hanshin’s offense was still dangerous.

Hanshin scored five runs, and that changes how we should see this loss.

The Tigers did not lose because their bats disappeared.

They attacked.

They answered.

They made Chunichi fight until the final out.

This was not a game in which Hanshin fell behind and quietly accepted defeat. Even in the ninth inning, the Dragons could not relax.

The Tigers lost, but they still looked dangerous."""

B1_TEXT = """Today’s Tiger Points.

Point One.

A bitter first step for young Kesamaru.

Yuki Kesamaru took the mound hoping to earn his first professional win.

Instead, he met a Chunichi lineup that refused to stay quiet.

The Dragons fought back, and Bosler’s home run became the hardest moment of his night.

It was a bitter result, but one difficult start does not tell the whole story of a young pitcher.

Games like this can become important lessons. The pressure, the mistakes and the disappointment may all help him when his next chance arrives.

Point Two.

Hanshin’s offense was still dangerous.

Hanshin scored five runs, and that changes how we should see this loss.

The Tigers did not lose because their bats disappeared.

They attacked.

They answered.

They made Chunichi fight until the final out.

This was not a game in which Hanshin fell behind and quietly accepted defeat. Even in the ninth inning, the Dragons could not relax.

The Tigers lost, but they still looked dangerous."""

# 検証: B1からPoint One/Twoの行を取り除くとB0と完全一致すること(=追加差分がPoint One/Twoだけであることの機械的証拠)
_b1_without_points = B1_TEXT.replace("Point One.\n\n", "").replace("Point Two.\n\n", "")
assert _b1_without_points == B0_TEXT, "B1からPoint One/Twoを除いてもB0と一致しません(追加差分がPoint表記だけになっていません)"
print("検証: B1からPoint One/Twoを除去するとB0と完全一致(追加差分がPoint表記のみであることを確認)", flush=True)

# 承認済み正本(er001b5_hanshin_script.json)を変更していないことの確認、および
# B0の内容が正本の該当セクションと(見出し末尾の句点を除き)一致することの参考チェック。
HANSHIN_SCRIPT_PATH = "er001b5_hanshin_script.json"
with open(HANSHIN_SCRIPT_PATH, "r", encoding="utf-8") as f:
    _hanshin_script = json.load(f)
_points_section = next(
    s for s in _hanshin_script["sections"]
    if s.get("heading") == "Today’s Tiger Points"
)
_b0_lines_from_json = [_points_section["heading"]]
for sub in _points_section["subsections"]:
    _b0_lines_from_json.append(sub["heading"])
    _b0_lines_from_json.extend(sub["paragraphs"])
_b0_from_json = "\n\n".join(_b0_lines_from_json)
# B0_TEXTは各見出しの直後に句点を1つ追加した版なので、句点を取り除けば正本と一致するはず
_b0_text_headings_depunctuated = B0_TEXT.replace(
    "Today’s Tiger Points.", "Today’s Tiger Points"
).replace(
    "A bitter first step for young Kesamaru.\n\nYuki Kesamaru",
    "A bitter first step for young Kesamaru\n\nYuki Kesamaru"
).replace(
    "Hanshin’s offense was still dangerous.\n\nHanshin scored",
    "Hanshin’s offense was still dangerous\n\nHanshin scored"
)
assert _b0_text_headings_depunctuated == _b0_from_json, (
    "B0_TEXT(見出し句点を除去したもの)が正本JSONの'Today's Tiger Points'セクションと一致しません。"
    "正本の内容が変更されているか、この比較テキストに誤りがある可能性があります。"
)
print("検証: B0の内容(見出し句点を除く)が承認済み正本er001b5_hanshin_script.jsonの該当セクションと完全一致", flush=True)

def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

# ============================================================
# ブロック2: 演技指示(ER-001B-6の共通基本指示+Level 2指示 + 忠実性ルールの追加のみ)
# ============================================================
COMMON_BASE_INSTRUCTION = """TTS the following complete story in natural, engaging English.

Speak directly to one interested listener rather than announcing to a large crowd.

Create a natural emotional arc that follows the meaning already present in the script. Let the energy, weight, and pace rise or fall when the story itself changes. Do not add excitement, sadness, urgency, or drama that is not supported by the words.

Carry the meaning naturally across sentence boundaries. Do not reset your pitch, energy, or rhythm after every sentence. Group related sentences into complete thoughts, while keeping important contrasts and turning points clear.

Treat the narration as one continuous program, even when it is generated in separate sections.

Read every title, section heading, and subsection heading exactly as written. Never skip, paraphrase, shorten, or silently absorb a heading into the following text.

Clearly say "In One Line" before reading the final section.

Do not shout, sound like a movie trailer, become gloomy or sleepy, or use a distant and overly formal newsreader style.

"""

LEVEL2_INSTRUCTION = """Give the narration a noticeably animated, emotionally present, and expressive delivery.

Use a clearly wider vocal range, stronger emphasis on important words and turning points, and more distinct rises and falls in energy.

Make the listener feel that the story matters and that you genuinely want them to keep listening.

Keep the narration moving with confident momentum, including during explanatory passages. Avoid becoming passive, flat, or overly restrained.

Allow the most important moments, contrasts, and conclusions to land with clear emotional impact.

Use stronger expression than Level 1, but vary the intensity across the story. Do not stay at maximum intensity throughout.

Do not shout, force emotion, exaggerate feelings that are not present in the script, or sound like a sports commentator or movie trailer.

"""

# ER-001B-7B専用の追加(忠実性ルール)。これ以外はER-001B-6 Level 2の指示から変更しない。
POINT_LABEL_FIDELITY_RULE = """Read every heading and point label exactly as written. Clearly say "Point One" before the first point and "Point Two" before the second point. Do not skip, repeat, paraphrase, or merge a point label with its heading.

"""

STYLE_PREFIX = COMMON_BASE_INSTRUCTION + LEVEL2_INSTRUCTION + POINT_LABEL_FIDELITY_RULE

# B0とB1で演技指示が完全に同一であることを機械的に保証する(そもそも単一の変数を両方で使うため自明だが、明示的に確認する)
CONDITIONS = [
    {"name": "B0_current", "text": B0_TEXT, "out_file": "er001b7b_tiger_points_current.wav",
     "expect_point_labels": False},
    {"name": "B1_numbered", "text": B1_TEXT, "out_file": "er001b7b_tiger_points_numbered.wav",
     "expect_point_labels": True},
]
for c in CONDITIONS:
    c["style_prefix"] = STYLE_PREFIX
assert CONDITIONS[0]["style_prefix"] == CONDITIONS[1]["style_prefix"], "B0とB1で演技指示が一致していません"
print(f"検証: B0/B1の演技指示が完全一致(sha256: {sha256_text(STYLE_PREFIX)[:16]}...)", flush=True)

# 数値による話速指定を含まないことも確認する
wpm_pattern = re.compile(r"\d+\s*[-–]?\s*\d*\s*words per minute|\bwpm\b", re.IGNORECASE)
assert not wpm_pattern.search(STYLE_PREFIX), "演技指示に話速の数値指定が含まれています"

# ============================================================
# ブロック3: 道具(音量正規化・PCM→WAV変換。ER-001B-6と同一)
# ============================================================
def normalize_pcm(pcm_bytes, target_peak=0.7):
    samples = array.array('h', pcm_bytes)
    if not samples:
        return pcm_bytes
    peak = max(abs(s) for s in samples)
    if peak == 0:
        return pcm_bytes
    scale = min((target_peak * 32767) / peak, 3.0)
    normalized = array.array('h', (max(-32768, min(32767, int(s * scale))) for s in samples))
    return normalized.tobytes()

def pcm_to_wav_bytes(pcm_bytes, sample_rate):
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        w.writeframes(pcm_bytes)
    return buf.getvalue()

# ============================================================
# ブロック4: クライアント初期化・モデル設定(ER-001B-6と同一)
# ============================================================
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-2.5-pro-preview-tts"
QA_MODEL_NAME = "gemini-3-flash-preview"
LANGUAGE_CODE = "en-us"
VOICE = "Aoede"
SAMPLE_RATE = 24000
MAX_RETRY = 2
MAX_CONTENT_ATTEMPTS = 2
TTS_TIMEOUT_MS = 150_000
TIER1_DAILY_LIMIT = 50

USAGE_LOG_PATH = ".tts_usage_log.jsonl"

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
        "script": "er001b7b_point_number_compare.py",
        "pattern": label,
    }
    with open(USAGE_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def build_narrator_speech_config(voice_name):
    return types.SpeechConfig(
        language_code=LANGUAGE_CODE,
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice_name)
        ),
    )

def call_tts(prompt, speech_config, label="clip"):
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
                sys.exit(1)
            print(f"    [{label}] → エラー(試行{attempt}回目、{elapsed:.1f}秒後): {e}", flush=True)
            if attempt > MAX_RETRY:
                raise
            time.sleep(2)

# ============================================================
# ブロック5: 技術検品(期待テキスト・語句出現回数を明示するgrounded設計。
# ER-001B-6Aで判明した「見出し欠落の見逃し」を踏まえた設計)
# ============================================================
def technical_check(wav_bytes, condition, label):
    text = condition["text"]
    expect_points = condition["expect_point_labels"]
    point_requirement = (
        'This clip SHOULD contain "Point One" spoken exactly once and "Point Two" spoken exactly once.'
        if expect_points else
        'This clip should NOT contain "Point One" or "Point Two" anywhere - it must not be spoken at all.'
    )
    prompt = f"""You are doing an automated technical QA check of a TTS-generated narration, comparing it against the approved expected text below. Do NOT judge subjective voice quality or how expressive/enjoyable it sounds - only the technical criteria listed.

EXPECTED TEXT (must be read verbatim, in this exact order, not summarized/shortened/added to/reworded):
---
{text}
---

{point_requirement}

Listen to the audio and count occurrences (as literally spoken words) of each of the following, then answer:
1. heading_today_tiger_points_count: how many times is "Today's Tiger Points" spoken (expected: exactly 1)?
2. subheading1_count: how many times is "A bitter first step for young Kesamaru" spoken (expected: exactly 1)?
3. subheading2_count: how many times is "Hanshin's offense was still dangerous" spoken (expected: exactly 1)?
4. point_one_count: how many times is "Point One" spoken as its own distinct label (not merged into the following heading)?
5. point_two_count: how many times is "Point Two" spoken as its own distinct label (not merged into the following heading)?
6. dropped_content: true if any sentence or significant portion of the expected text is missing from the audio.
7. duplicated_content: true if any sentence/heading is accidentally spoken twice (beyond the counts above).
8. non_english_or_extraneous_speech: true if there is any non-English speech, or any spoken stage direction / instruction text / Markdown symbol read aloud.
9. unauthorized_wording_changes: true if the spoken words meaningfully change, add to, or remove from the expected text's wording (natural verbalization of punctuation is not a change).

Return ONLY valid JSON, no other text, in exactly this shape:
{{"heading_today_tiger_points_count": 1, "subheading1_count": 1, "subheading2_count": 1, "point_one_count": 0, "point_two_count": 0, "dropped_content": false, "duplicated_content": false, "non_english_or_extraneous_speech": false, "unauthorized_wording_changes": false, "notes": "brief explanation in English"}}"""

    for attempt in range(5):
        try:
            resp = client.models.generate_content(
                model=QA_MODEL_NAME,
                contents=[
                    types.Part.from_bytes(data=wav_bytes, mime_type="audio/wav"),
                    prompt,
                ],
                config=types.GenerateContentConfig(response_mime_type="application/json"),
            )
            text_out = resp.text.strip()
            text_out = re.sub(r"^```(json)?|```$", "", text_out.strip(), flags=re.MULTILINE).strip()
            result = json.loads(text_out)

            expected_point_one = 1 if expect_points else 0
            expected_point_two = 1 if expect_points else 0

            checks = {
                "heading_today_tiger_points_count": result.get("heading_today_tiger_points_count") == 1,
                "subheading1_count": result.get("subheading1_count") == 1,
                "subheading2_count": result.get("subheading2_count") == 1,
                "point_one_count": result.get("point_one_count") == expected_point_one,
                "point_two_count": result.get("point_two_count") == expected_point_two,
                "dropped_content": result.get("dropped_content") is False,
                "duplicated_content": result.get("duplicated_content") is False,
                "non_english_or_extraneous_speech": result.get("non_english_or_extraneous_speech") is False,
                "unauthorized_wording_changes": result.get("unauthorized_wording_changes") is False,
            }
            passed = all(checks.values())
            reasons = [k for k, v in checks.items() if not v]
            print(f"    [{label}] 技術検品: {'合格' if passed else '不合格 → ' + ', '.join(reasons)} "
                  f"(counts: heading={result.get('heading_today_tiger_points_count')}, "
                  f"sub1={result.get('subheading1_count')}, sub2={result.get('subheading2_count')}, "
                  f"point1={result.get('point_one_count')}, point2={result.get('point_two_count')}) "
                  f"(notes: {result.get('notes', '')})", flush=True)
            return passed, reasons, result
        except Exception as e:
            print(f"    [{label}] 技術検品呼び出し失敗(試行{attempt+1}回目): {str(e)[:150]}", flush=True)
            time.sleep(8)
    print(f"    [{label}] 技術検品モデルが応答不能のため、判定不能→合格扱いとします", flush=True)
    return True, ["content_check_inconclusive"], {"notes": "QA model unavailable after retries"}

# ============================================================
# ブロック6: 事前表示
# ============================================================
today_so_far = load_today_call_count()
max_calls = len(CONDITIONS) * MAX_CONTENT_ATTEMPTS

print("ER-001B-7B: ポイント番号の構造比較(Today's Tiger Pointsのみ)")
print(f"生成する音声数: {len(CONDITIONS)} 本(B0現行構造 / B1ポイント番号追加)")
print(f"最大生成試行回数: 条件あたり{MAX_CONTENT_ATTEMPTS}回(技術的失敗時のみ再生成)")
print(f"本日ここまでの呼び出し回数(全スクリプト合算の見立て): {today_so_far} 回")
print(f"実行後の見込み合計(最大): {today_so_far + max_calls} 回 / Tier1日次上限(実測): {TIER1_DAILY_LIMIT} 回")
print()

# ============================================================
# ブロック7: 条件ごとに生成 → 技術検品 → (必要なら再生成) → 保存
# ============================================================
manifest = {
    "experiment_id": "ER-001B-7B",
    "model": MODEL_NAME,
    "qa_model": QA_MODEL_NAME,
    "language_code": LANGUAGE_CODE,
    "voice": VOICE,
    "sample_rate": SAMPLE_RATE,
    "volume_normalized": True,
    "normalize_target_peak": 0.7,
    "max_content_attempts": MAX_CONTENT_ATTEMPTS,
    "style_prefix": STYLE_PREFIX,
    "style_prefix_sha256": sha256_text(STYLE_PREFIX),
    "style_prefix_identical_across_conditions": True,
    "hanshin_script_source_unchanged": HANSHIN_SCRIPT_PATH,
    "b0_matches_approved_script_section": True,
    "b1_diff_from_b0_is_point_labels_only": True,
    "clips": [],
}

speech_config = build_narrator_speech_config(VOICE)

for i, cond in enumerate(CONDITIONS, 1):
    name = cond["name"]
    text = cond["text"]
    style_prefix = cond["style_prefix"]
    out_wav = cond["out_file"]

    print(f"[{i}/{len(CONDITIONS)}] {name} を生成中(最大{MAX_CONTENT_ATTEMPTS}回試行)...", flush=True)

    attempts_log = []
    final_pcm = None
    accepted_attempt = None
    passed_final = False
    gen_seconds = None

    for attempt in range(1, MAX_CONTENT_ATTEMPTS + 1):
        call_label = f"{name}_a{attempt}"
        t0 = time.time()
        pcm = call_tts(style_prefix + text, speech_config, label=call_label)
        record_call(call_label)
        gen_seconds = time.time() - t0

        wav_bytes = pcm_to_wav_bytes(pcm, SAMPLE_RATE)
        passed, reasons, qa_result = technical_check(wav_bytes, cond, label=call_label)
        attempts_log.append({
            "attempt": attempt, "passed": passed, "reasons": reasons,
            "qa_result": qa_result, "generation_seconds": round(gen_seconds, 1),
        })

        final_pcm = pcm
        accepted_attempt = attempt
        passed_final = passed
        if passed:
            print(f"  [試行{attempt}] 技術検品合格。この生成を採用します。", flush=True)
            break
        else:
            remaining = MAX_CONTENT_ATTEMPTS - attempt
            print(f"  [試行{attempt}] 技術検品不合格({', '.join(reasons)})。"
                  f"{'再生成します' if remaining > 0 else '最大試行回数に達したため、この生成を採用します(要ユーザー確認)'}",
                  flush=True)

    with wave.open(out_wav, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        w.writeframes(final_pcm)

    seconds = len(final_pcm) / (SAMPLE_RATE * 2)
    print(f"  → {out_wav} を保存しました(約 {seconds:.1f}秒、"
          f"{'技術検品合格' if passed_final else '技術検品不合格のまま採用(要確認)'}、試行回数: {accepted_attempt})")
    print()

    manifest["clips"].append({
        "file": out_wav,
        "condition": name,
        "voice": VOICE,
        "text": text,
        "text_sha256": sha256_text(text),
        "expect_point_labels": cond["expect_point_labels"],
        "duration_seconds": round(seconds, 1),
        "word_count": len(text.split()),
        "generated_at": datetime.now().isoformat(),
        "generation_attempts": accepted_attempt,
        "attempts_log": attempts_log,
        "final_attempt_technical_check_passed": passed_final,
    })

manifest_path = "er001b7b_manifest.json"
with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)

print("-" * 50)
print(f"全{len(CONDITIONS)}音声の生成が完了しました。")
print(f"実験ID・条件・演技指示・ハッシュ・試行ログの記録を {manifest_path} に保存しました。")
