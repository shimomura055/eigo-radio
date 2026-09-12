# ============================================================
# er012_editorial_b_voices_trial_09_audio.py
# EDITORIAL-B-FAMILY-VOICES-TRIAL-09-AUDIO-STRUCTURE-REFINEMENT-01
# ============================================================
# Lane: Lane B / Voices-Perspective。種別: Trial音声化(ユーザー判断反映版、
# 2026-09-07)。目的: Trial-07記事(一人称、5区切り: The Question/One Voice/
# Another Voice/Where the Difference Comes From/What the Seat Really Means)を、
# Voices Familyとして自然な音声構造(Narrator headingが一人称Voiceを導入し、
# Voice A/BはNarratorとは別のvoiceで読む)で再音声化し、完成候補episodeとして
# 聞けるartifactを作る。問題がなければこの仕様でProduction採用候補となるが、
# 本タスク自体はProduction採用を行わない(一人称/Voice固定/Voices Comment
# Prompt/Tension slot正式追加/新音声構造いずれもAPPROVED_FOR_PRODUCTIONに
# しない)。
#
# 設計方針(重要): 既存Production関数(er003_v1_n3_01_assemble.py [asm]・
# er003_v1_n3_01_tts_generate.py [tts_gen]・er003_v1_sing01_voice01_generate.py
# [voice01]・er003_v1_sing01_point_headings_aoede.py [point_headings]・
# er003_v1_sing01_news_tail_fix.py [news_tail_fix])は一切変更しない。
#   - Comment 1-4/Preview: b1s.run_support_text()をTrial専用ROLE promptで
#     呼ぶ(b1s.run_support_text自体は無変更、Prompt文字列だけTrial限定)。
#   - Voice A/B本文(Algieba/Erinome): news_tail_fix.generate_news_narration_
#     wide_margin()と同じロジックだが声(voice_name)だけ差し替え可能にした
#     Trial専用コピー(generate_voice_body_wide_margin)を新規実装する
#     (Production側はp9a.VOICE_NAME固定でvoice引数を持たないため、無変更の
#     まま流用できない)。
#   - Voice heading(Narrator、Aoede): point_headings.generate()をそのまま
#     無変更で呼ぶ(Aoede固定で、まさに欲しい挙動と一致)。
#   - Hook/Tension/Closing/Key Phrase: 本文・声ともTrial-07/08と同一のため、
#     Trial-08の既存音声をtext hash確認のうえコピー再利用する(重複TTSコスト
#     を避ける)。
#   - asm.load_b1_sources()/apply_b1_gain()/assemble_with_timeline()/
#     apply_headroom_safety_valve()は無変更のまま呼ぶ。11個固定segment名を
#     ハードコードしているasm.build_b1_timeline()だけはTrial専用の拡張版
#     (build_b1_voices_timeline_trial09)に差し替える。
#
# 触れないもの: docs/pm/*(ACTIVE_TASK.md/RESULT_PACKET.md以外)、SSOT、
# er011_*・er011_output/、Lane A、Productionコード/Prompt/Validator/
# Assembly本体、CURRENT_SPEC.md。
# 書き込み: 本ファイル(root)、er012_output/editorial_b_voices_trial_09_
# audio/ 配下のみ。Git操作はこのタスクの最後に1回だけ本タスクが行う。
#
# cost > 800円でSTOP。到達してよいStatus: 音声化完了(完成candidate episode)
# + USER_DECISION_REQUIRED(新音声構造・Voice固定・Voices Comment Prompt・
# Tension slot・KP canonicalizationのProduction採用判断)。
from __future__ import annotations

import json
import os
import re
import shutil
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

# PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-01: 正式リリース前はStandard同期を使う。
os.environ["TTS_EXECUTION_MODE"] = "STANDARD"

import hashlib

import er002_common as common
import er003_audio_tts_asr_safety as safety
import er003_b1_p3u_audio as p3u
import er003_b1_p4c_audio as p4c
import er003_b1_p9a_audio as p9a
import er003_v1_b1_scaffold_01_generate as b1s
import er003_v1_en_direct_ab_01_generate as ab01
import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_assemble as asm
import er003_v1_n3_01_scaffold_generate as sc
import er003_v1_n3_01_tts_generate as tts_gen
import er003_v1_repro01_main_generate as repro01
import er003_v1_sing01_news_tail_fix as news_tail_fix
import er003_v1_sing01_point_headings_aoede as point_headings
import er003_v1_sing01_voice01_generate as voice01
import er005_cost_logger as cl
import er006_audio_cost_pilot_02_shared_narration as shared_narration
import er006_batch_tts_wiring_01 as batch_wiring
import er006_asr_provider_routing_01 as asr_routing
import er006_model_routing_contract_01 as routing
import er006_pronunciation_ledger_01 as pronun_ledger
import er006_secondary_asr_01 as secondary_asr
import er008_disfluency_qa_18 as dq18
import er011_human_review_lock_01 as review_lock
import er011_tts_cooldown_observation_01 as cooldown_obs
import er011_tts_cooldown_observation_harness_helpers_01 as cooldown_helpers

TRIAL07_ARTICLE_PATH = "er012_output/editorial_b_voices_trial_07/b1b_run02_attempt2/article.md"
TRIAL07_LEDGER_PATH = "er012_output/editorial_b_voices_trial_07/research/verified_fact_ledger.txt"
TRIAL08_P1_DIR = "er012_output/editorial_b_voices_trial_08_audio/p1/b1b"

OUT_DIR = "er012_output/editorial_b_voices_trial_09_audio"
COST_LOG_PATH = f"{OUT_DIR}/audit/raw_usage_log.jsonl"
PRICING_SNAPSHOT_PATH = "er005_output/cost_baseline_01/pricing_snapshot.json"
USD_JPY = 160.0
BUDGET_JPY_CAP = 800.0

THEME = {"theme_id": "voices_trial09", "out_dir": OUT_DIR}
OUT_B1_DIR = f"{THEME['out_dir']}/b1b"
NARRATION_DIR = f"{OUT_B1_DIR}/narration"

EXTRA_SEGMENT_NAME = "tension_reflection"  # Trial-only、既存11-partに無いsegment(Trial-08由来)
REUSED_SEGMENT_NAMES = ("full_story_part1", "full_story_part2", EXTRA_SEGMENT_NAME, "in_one_line")

# 第一候補(item 1)。API呼び出しが技術的に失敗した場合のみitem 3に従い変更する。
VOICE_A_CANDIDATE = "Algieba"
VOICE_B_CANDIDATE = "Erinome"
VOICE_A_FALLBACK = "Schedar"
VOICE_B_FALLBACK = "Sulafat"
NARRATOR_VOICE = "Aoede"  # Production point_headings.generate()に既に固定されている声
COMPARISON_VOICES = ("Algieba", "Erinome", "Schedar", "Sulafat", "Aoede")


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, default=str)


def sha(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


# ============================================================
# コスト計測(Trial-08と同一ロジック、Trial-09専用ログへ適用)
# ============================================================
def _load_pricing():
    prices = load_json(PRICING_SNAPSHOT_PATH)["prices"]

    def price(provider, model, meter):
        return next(p["price"] for p in prices
                    if p["provider"] == provider and p["model"] == model and p["meter"] == meter
                    and p.get("tier", "Standard") == "Standard")
    return price


def compute_cost_jpy_so_far() -> tuple:
    if not os.path.exists(COST_LOG_PATH):
        return 0.0, {}
    price = _load_pricing()
    total_usd = 0.0
    by_provider = {}
    with open(COST_LOG_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            provider = rec.get("provider")
            model = rec.get("model_id") or rec.get("model")
            usd = 0.0
            try:
                if provider in ("gemini", "openai", "openai_asr") and model:
                    in_tok = rec.get("input_tokens") or 0
                    out_tok = rec.get("output_tokens") or 0
                    usd = in_tok * price(provider, model, "input_tokens") / 1e6 \
                        + out_tok * price(provider, model, "output_tokens") / 1e6
            except StopIteration:
                usd = 0.0
            total_usd += usd
            by_provider[provider] = by_provider.get(provider, 0.0) + usd
    jpy = total_usd * USD_JPY
    return jpy, {k: round(v * USD_JPY, 2) for k, v in by_provider.items()}


def assert_budget_ok(note: str = "") -> float:
    jpy, by_provider = compute_cost_jpy_so_far()
    print(f"[TRIAL09-AUDIO][cost] so far={jpy:.2f} JPY by_provider={by_provider} ({note})")
    if jpy > BUDGET_JPY_CAP:
        raise RuntimeError(f"[BUDGET_GUARD] cost so far {jpy:.2f} JPY > cap {BUDGET_JPY_CAP} JPY. Stopping ({note}).")
    return jpy


# ============================================================
# Step 0: 5区切り構造parser(Trial-08由来のコピー、article.md自体は無変更で
# 読み取るだけ)
# ============================================================
_HEADING_RE = re.compile(r"^(#{2,3})[ \t]+(.+?)\s*$", re.MULTILINE)
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z])")


def split_five_voice_sections(article_text: str) -> dict | None:
    title_match = re.match(r"^#[ \t]+.+?\s*\n", article_text)
    if not title_match:
        return None
    body = article_text[title_match.end():]
    matches = list(_HEADING_RE.finditer(body))
    if len(matches) != 5:
        return None
    labels = ["hook", "voice_a", "voice_b", "tension", "closing"]
    result = {}
    for i, label in enumerate(labels):
        heading_text = matches[i].group(2).strip()
        content_start = matches[i].end()
        content_end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        result[f"{label}_heading"] = heading_text
        result[f"{label}_body"] = body[content_start:content_end].strip()
    result["unexpected_preamble_before_first_heading"] = body[:matches[0].start()].strip()
    return result


def extract_title(article_text: str) -> str:
    m = re.match(r"^#\s+(.+?)\s*\n", article_text)
    if not m:
        raise RuntimeError("記事タイトル(# 見出し)が見つかりません")
    return m.group(1).strip()


def ensure_period(s: str) -> str:
    s = s.strip()
    return s if s.endswith((".", "!", "?")) else s + "."


def split_two_balanced_by_sentence(text: str) -> tuple:
    """Hook(The Question)を2つのTTS segmentへ均等に近い形で分割する
    Trial専用ヘルパー(Trial-08由来のコピー)。Assembly側では2つを小さい
    pauseで連続再生し、聞こえ方は単一のHookブロックになる(item 4: heading
    非読み上げ・単一ブロック)。"""
    sentences = [s.strip() for s in _SENTENCE_SPLIT_RE.split(text.strip()) if s.strip()]
    if len(sentences) < 2:
        raise RuntimeError(f"Hookの文数が2未満です(検出数: {len(sentences)})")
    word_counts = [len(re.findall(r"[A-Za-z']+", s)) for s in sentences]
    total = sum(word_counts)
    running = 0
    best_diff = None
    split_idx = 1
    for i in range(1, len(sentences)):
        running += word_counts[i - 1]
        diff = abs(running - (total - running))
        if best_diff is None or diff < best_diff:
            best_diff = diff
            split_idx = i
    part1 = " ".join(sentences[:split_idx])
    part2 = " ".join(sentences[split_idx:])
    return part1, part2


def first_n_sentences(text: str, n: int) -> str:
    sentences = [s.strip() for s in _SENTENCE_SPLIT_RE.split(text.strip()) if s.strip()]
    return " ".join(sentences[:n])


def build_parts(article_text: str) -> dict:
    sections = split_five_voice_sections(article_text)
    if sections is None:
        raise RuntimeError("5区切り構造の検出に失敗しました(想定と異なる見出し構成)")
    title = extract_title(article_text)
    hook_part1, hook_part2 = split_two_balanced_by_sentence(sections["hook_body"])
    # item 2: Narrator headingは記事本文の実際の見出し文言をそのまま使う
    # ("One Voice: The desk that lets work begin"は既にこの形の見出しとして
    # Trial-07記事に存在する、新規作文はしない)。TTS向けに末尾ピリオドのみ
    # 補う。
    return {
        "title": title,
        "part1": hook_part1, "part2": hook_part2,
        "point_one_heading": ensure_period(sc.clean_heading(sections["voice_a_heading"])),
        "point_one_body": sections["voice_a_body"],
        "point_two_heading": ensure_period(sc.clean_heading(sections["voice_b_heading"])),
        "point_two_body": sections["voice_b_body"],
        "in_one_line": sections["closing_body"],
        "tension_heading": sections["tension_heading"],
        "tension_body": sections["tension_body"],
        "_five_section_headings": {k: sections[k] for k in
                                    ("hook_heading", "voice_a_heading", "voice_b_heading",
                                     "tension_heading", "closing_heading")},
    }


def prepare() -> dict:
    with open(TRIAL07_ARTICLE_PATH, encoding="utf-8") as f:
        article_text = f.read()
    parts = build_parts(article_text)
    os.makedirs(f"{OUT_B1_DIR}/audit", exist_ok=True)
    with open(f"{OUT_B1_DIR}/article.md", "w", encoding="utf-8") as f:
        f.write(article_text)
    save_json(f"{OUT_B1_DIR}/parts.json", parts)
    save_json(f"{OUT_B1_DIR}/five_section_length_report.json", {
        "hook_words": len(re.findall(r"[A-Za-z']+", parts["part1"] + " " + parts["part2"])),
        "voice_a_words": ab01.compute_word_count(parts["point_one_body"]),
        "voice_b_words": ab01.compute_word_count(parts["point_two_body"]),
        "tension_words": ab01.compute_word_count(parts["tension_body"]),
        "closing_words": ab01.compute_word_count(parts["in_one_line"]),
    })
    return {"article_text": article_text, "parts": parts}


# ============================================================
# Step 1: Voice可用性確認 + 比較sample(item 1・2・3・4)
# ============================================================
def generate_voice_sample_single_take(text: str, out_path: str, voice_name: str) -> dict:
    """比較sample専用の単発生成(item 1: 'full episode不要'を受けた軽量版)。
    既存p4c.build_tts_prompt+batch_wiring.make_batch_tts_call_fn(声のみ
    差し替え)+p3u.trim_english_keyword_silenceはProductionと同じ呼び出し
    パターンを踏襲するが、ASR検証・retry cascadeは行わない(比較目的のみ、
    コスト最小化)。"""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    call_fn = batch_wiring.make_batch_tts_call_fn(p9a.ENGLISH_MODEL_NAME, voice_name, output_path=out_path)
    prompt = p4c.build_tts_prompt(text, p9a.ENGLISH_STYLE_PREFIX)
    try:
        pcm, retries, ok, err = common._call_tts_with_retry(
            call_fn, prompt, max_retry=p9a.MAX_TTS_TECHNICAL_RETRY, sleep_fn=None)
    except Exception as e:
        return {"status": "ERROR", "voice": voice_name, "text": text, "error": f"{type(e).__name__}: {e}"}
    if not ok:
        return {"status": "ERROR", "voice": voice_name, "text": text, "error": str(err)}
    samples_raw = common.pcm_bytes_to_float_mono(pcm)
    trimmed, trim_info = p3u.trim_english_keyword_silence(samples_raw, common.SAMPLE_RATE, safety_margin_seconds=0.35)
    if trimmed is None:
        return {"status": "ERROR", "voice": voice_name, "text": text, "error": "発話区間検出失敗"}
    common.write_wav_float(out_path, trimmed, common.SAMPLE_RATE, 1)
    return {"status": "OK", "voice": voice_name, "text": text, "path": out_path,
            "duration_seconds": round(len(trimmed) / common.SAMPLE_RATE, 4)}


def run_voice_availability_check(sample_text: str) -> dict:
    sample_dir = f"{OUT_DIR}/audit/voice_samples"
    results = {}
    for voice_name in COMPARISON_VOICES:
        path = f"{sample_dir}/sample_{voice_name.lower()}.wav"
        print(f"[TRIAL09-AUDIO][voice-check] {voice_name} sample生成...")
        r = generate_voice_sample_single_take(sample_text, path, voice_name)
        results[voice_name] = r
        print(f"[TRIAL09-AUDIO][voice-check] {voice_name}: status={r.get('status')}")
    save_json(f"{sample_dir}/voice_sample_results.json", {"sample_text": sample_text, "results": results})
    return results


def resolve_voice_names(sample_results: dict) -> tuple:
    reasons = {}
    voice_a = VOICE_A_CANDIDATE
    voice_b = VOICE_B_CANDIDATE
    if sample_results.get(VOICE_A_CANDIDATE, {}).get("status") != "OK":
        voice_a = VOICE_A_FALLBACK
        reasons["voice_a"] = (f"{VOICE_A_CANDIDATE}が技術的に利用不可("
                               f"{sample_results.get(VOICE_A_CANDIDATE, {}).get('error')})のため"
                               f"{VOICE_A_FALLBACK}へ変更")
    if sample_results.get(VOICE_B_CANDIDATE, {}).get("status") != "OK":
        voice_b = VOICE_B_FALLBACK
        reasons["voice_b"] = (f"{VOICE_B_CANDIDATE}が技術的に利用不可("
                               f"{sample_results.get(VOICE_B_CANDIDATE, {}).get('error')})のため"
                               f"{VOICE_B_FALLBACK}へ変更")
    return voice_a, voice_b, reasons


# ============================================================
# Step 2: Voices Family用Comment Editorial Contract(item 6、候補プロンプト。
# Production Prompt無変更、Trial限定)
# ============================================================
VOICES_COMMENT_1_ROLE = """あなたはPodcastのナビゲーターです。これから、あるテーマ・場面を短く
提示する「The Question」(冒頭の問いかけ本文)をリスナーが聞きます。その直前に流す、
Comment 1(役割: テーマ・場面への自然な導入)を書いてください。

役割: これから始まるテーマ・場面へ、リスナーの意識を自然に向けます。

以下は避けてください:
- The Questionで語られる具体的な状況・問いの先取り(内容の先出し)
- "First point"/"Second point"のようなPoint要約めいた話法
- 事実を解説するような硬い、Discovery的な説明口調

1文程度の、非常に短い導入にしてください。

【重要・出力への制約】出力する文章自体に"Part 1"・"Part 2"・"Hook"・"The Question"
のような制作内部の構造ラベルを含めないでください。リスナーは番組の内部構成を
意識しません。"""

VOICES_COMMENT_2_ROLE = """あなたはPodcastのナビゲーターです。リスナーはThe Question(冒頭の
問いかけ)をすでに聞き終わり、これから、この問いに対する異なる立場からの一人称の
語り(One Voiceの後、続けてAnother Voice)を聞きます。その間に流す、Comment 2
(役割: Hookの問いから「ここから異なるVoiceを聞く」への橋渡し)を書いてください。

役割: The Questionで示された問いを受け、「ここから、違う視点を持つ声を順番に
聞いていく」ことへリスナーを橋渡しします。

以下は避けてください:
- One Voice・Another Voiceの具体的な内容の先取り
- これから聞く見出しの文言そのものを、この時点で言うこと(見出しはこの直後に
  Narratorが読み上げます)
- "Point One"・"Point Two"のような表現

1〜2文にしてください。

【重要・出力への制約】出力する文章自体に制作内部の構造ラベルを含めないでください。"""

VOICES_COMMENT_3_ROLE = """あなたはPodcastのナビゲーターです。リスナーは、ある問いに対する
異なる立場からの一人称の語り(One Voice・Another Voice)を両方すでに聞き終わり、
これから「なぜ同じ状況を人によって違って感じるのか」という視点の深掘りを聞きます。
その間に流す、Comment 3(役割: 「どちらが正しいか」ではなく「なぜ違って感じるのか」
への視点の移動)を書いてください。

役割: 2つの声を聞き終えたリスナーの意識を、「どちらが正しいか」という判定ではなく、
「なぜ同じ状況が人によって違って感じられるのか」という問いへ移します。

以下は避けてください:
- これから聞く深掘り部分の答え(視点の違いの正体)を先に説明すること
- どちらか一方の声を「正しい」「間違っている」と評価すること

2〜3文にしてください。

【重要・出力への制約】出力する文章自体に制作内部の構造ラベルを含めないでください。"""

VOICES_COMMENT_4_ROLE = """あなたはPodcastのナビゲーターです。リスナーは「なぜ同じ状況を
人によって違って感じるのか」という視点の深掘りをすでに聞き終わり、これから結びの
まとめを聞きます。その間に流す、Comment 4(役割: 表面的な対立から一段深い問いへの
視点移動)を書いてください。

役割: 「どちらが正しいか」という表面的な対立から、一段深い問い(何がこの状況を
成り立たせているのか)へリスナーの視点を移します。

以下は避けてください:
- これから聞く結びのまとめの要約・結論の先取り
- 解決策の提案

2〜3文にしてください。

【重要・出力への制約】出力する文章自体に制作内部の構造ラベルを含めないでください。"""

VOICES_COMMENT_ROLES = {
    "comment_1": VOICES_COMMENT_1_ROLE, "comment_2": VOICES_COMMENT_2_ROLE,
    "comment_3": VOICES_COMMENT_3_ROLE, "comment_4": VOICES_COMMENT_4_ROLE,
}
VOICES_SELF_CHECK_RULES = {
    "comment_1": "Avoid leaking The Question's specific situation/content; avoid Point-style summary "
                 "language ('First point'/'Second point'); avoid a dry, explanatory Discovery-style tone.",
    "comment_2": "Avoid leaking One Voice/Another Voice content; avoid literally saying the upcoming "
                 "heading wording (e.g. 'The desk that lets work begin' / 'The freedom to move') at this "
                 "point (that wording is spoken by the Narrator right after); avoid 'Point One'/'Point Two' "
                 "phrasing.",
    "comment_3": "Avoid explaining the answer to 'why people feel differently' before that section is "
                 "heard; avoid declaring one voice right and the other wrong.",
    "comment_4": "Avoid summarizing or pre-stating the Closing's conclusion; avoid proposing a solution.",
}


def run_scaffold_voices(parts: dict, article_text: str, sections: dict, ledger_text: str) -> dict:
    client = sc.get_client()
    model = routing.require_model("B1_SUPPORT", routing.SUPPORT_MODEL)

    print("[TRIAL09-AUDIO] Comment 1(Voices Contract)生成開始...")
    c1_context = f"【これから聞く本文(The Question)】\n{sections['hook_body']}"
    c1 = b1s.run_support_text(client, VOICES_COMMENT_1_ROLE, c1_context, model=model)

    print("[TRIAL09-AUDIO] Comment 2(Voices Contract)生成開始...")
    c2_context = (f"【すでに聞いた本文(The Question)】\n{sections['hook_body']}\n\n"
                  f"【これから聞く声の見出しのみ(内容は伏せる、この時点でこの文言を言わないこと)】\n"
                  f"One Voice heading: {parts['point_one_heading']}\n"
                  f"Another Voice heading: {parts['point_two_heading']}")
    c2 = b1s.run_support_text(client, VOICES_COMMENT_2_ROLE, c2_context, model=model)

    print("[TRIAL09-AUDIO] Comment 3(Voices Contract)生成開始...")
    c3_context = (f"【One Voice(聞き終えた内容)】\n{parts['point_one_heading']}\n{parts['point_one_body']}\n\n"
                  f"【Another Voice(聞き終えた内容)】\n{parts['point_two_heading']}\n{parts['point_two_body']}\n\n"
                  f"【これから聞く内容の見出しのみ(内容は伏せる)】\n{sections['tension_heading']}")
    c3 = b1s.run_support_text(client, VOICES_COMMENT_3_ROLE, c3_context, model=model)

    print("[TRIAL09-AUDIO] Comment 4(Voices Contract)生成開始...")
    c4_context = (f"【聞き終えた内容(視点の違いの深掘り)】\n{parts['tension_body']}\n\n"
                  f"【これから聞く結びの見出しのみ(内容は伏せる)】\n{sections['closing_heading']}")
    c4 = b1s.run_support_text(client, VOICES_COMMENT_4_ROLE, c4_context, model=model)

    print("[TRIAL09-AUDIO] Preview(既存Production Prompt、無変更)生成開始...")
    preview_role = b1s.PREVIEW_ROLE.format(
        comment_1=c1.get("text") or "(生成失敗)", comment_2=c2.get("text") or "(生成失敗)")
    preview_context = f"【エピソード全文(参考、新しいFactの追加禁止)】\n{article_text}"
    preview = b1s.run_support_text(client, preview_role, preview_context, model=model)

    results = {"preview": preview, "comment_1": c1, "comment_2": c2, "comment_3": c3, "comment_4": c4}
    os.makedirs(f"{OUT_B1_DIR}/audit", exist_ok=True)
    with open(f"{OUT_B1_DIR}/b1_support_texts.json", "w", encoding="utf-8") as f:
        json.dump({k: v.get("text") for k, v in results.items()}, f, ensure_ascii=False, indent=2)
    with open(f"{OUT_B1_DIR}/audit/b1_support_generation.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)

    support_concat = "\n\n".join(t for t in (v.get("text") for v in results.values()) if t)
    print("[TRIAL09-AUDIO] Support Ledger Deviation Check(既存Production vfl01.run_deviation_check、無変更)実行...")
    deviation = vfl01.run_deviation_check(client, ledger_text, support_concat)
    save_json(f"{OUT_B1_DIR}/audit/support_ledger_deviation.json", deviation["parsed"])

    self_check = run_comment_self_check(results, parts)
    save_json(f"{OUT_B1_DIR}/audit/comment_self_check.json", self_check)

    return {"support": results, "support_status": {k: v.get("status") for k, v in results.items()},
            "deviation": deviation["parsed"], "self_check": self_check}


COMMENT_SELF_CHECK_DEVELOPER_MESSAGE = (
    "You are a strict editorial QA reviewer for a podcast segment called Comment 1-4 in a "
    "'Voices Family' episode. For each Comment, judge whether it violates its stated role and "
    "forbidden-content rules given below. If it violates a rule, quote the exact offending phrase "
    "from the Comment text in 'evidence_quote' and explain briefly in 'reasoning'. If it does not "
    "violate any rule, set compliant=true, evidence_quote to an empty string, and reasoning to a "
    "short confirmation."
)

SELF_CHECK_SCHEMA = {
    "name": "voices_comment_self_check_v1",
    "schema": {
        "type": "object",
        "properties": {
            f"comment_{i}": {
                "type": "object",
                "properties": {
                    "compliant": {"type": "boolean"},
                    "evidence_quote": {"type": "string"},
                    "reasoning": {"type": "string"},
                },
                "required": ["compliant", "evidence_quote", "reasoning"],
                "additionalProperties": False,
            } for i in (1, 2, 3, 4)
        },
        "required": [f"comment_{i}" for i in (1, 2, 3, 4)],
        "additionalProperties": False,
    },
    "strict": True,
}


def run_comment_self_check(support_results: dict, parts: dict) -> dict:
    client = vfl01.get_client()
    model = routing.require_model("B1_SUPPORT", routing.SUPPORT_MODEL)
    lines = []
    for i in (1, 2, 3, 4):
        key = f"comment_{i}"
        text = support_results[key].get("text") or ""
        lines.append(f"[{key}]\nRule: {VOICES_SELF_CHECK_RULES[key]}\nText: {text}")
    prompt = (
        "Here are Comment 1-4 for a Voices-Family episode (structure: The Question -> Comment1 -> "
        "One Voice/Another Voice (Narrator-read headings + first-person bodies) -> Comment2/3 -> "
        "'why people feel differently' section -> Comment4 -> Closing). For reference, the actual "
        "content they must not leak or pre-state is below:\n\n"
        f"[One Voice heading]\n{parts['point_one_heading']}\n[One Voice body]\n{parts['point_one_body']}\n\n"
        f"[Another Voice heading]\n{parts['point_two_heading']}\n[Another Voice body]\n{parts['point_two_body']}\n\n"
        f"[Why-people-feel-differently body]\n{parts['tension_body']}\n\n[Closing body]\n{parts['in_one_line']}\n\n"
        + "\n\n".join(lines)
    )
    resp = client.responses.create(
        model=model,
        reasoning={"effort": "low"},
        text={"format": {"type": "json_schema", **SELF_CHECK_SCHEMA}},
        input=[{"role": "developer", "content": COMMENT_SELF_CHECK_DEVELOPER_MESSAGE},
               {"role": "user", "content": prompt}],
    )
    parsed = json.loads(resp.output_text)
    return {"parsed": parsed, "model": resp.model, "response_id": resp.id, "prompt": prompt}


# ============================================================
# Step 3: Trial-08既存音声の再利用(Hook/Tension/Closing/Key Phrase、item
# 入力section参照、text hash確認のうえコピー)
# ============================================================
def copy_reused_assets_from_trial08(article_text: str) -> dict:
    os.makedirs(NARRATION_DIR, exist_ok=True)
    os.makedirs(f"{OUT_B1_DIR}/key_phrases", exist_ok=True)

    with open(f"{TRIAL08_P1_DIR}/article.md", encoding="utf-8") as f:
        trial08_article_text = f.read()
    hash_match = sha(article_text) == sha(trial08_article_text)
    if not hash_match:
        raise RuntimeError(
            "[TEXT_HASH_MISMATCH] Trial-08のarticle.mdとTrial-07記事(本タスクの入力)のtext hashが"
            "一致しないため、Hook/Tension/Closing/Key Phraseの再利用を中止します。")

    src_results = load_json(f"{TRIAL08_P1_DIR}/audit/tts_generation_results.json")
    reused_segments = {}
    for name in REUSED_SEGMENT_NAMES:
        shutil.copyfile(f"{TRIAL08_P1_DIR}/narration/{name}.wav", f"{NARRATION_DIR}/{name}.wav")
        entry = dict(src_results["segments"][name])
        entry["path"] = f"{NARRATION_DIR}/{name}.wav"
        entry["reused_from"] = f"{TRIAL08_P1_DIR}/narration/{name}.wav (EDITORIAL-B-FAMILY-VOICES-TRIAL-08-AUDIO)"
        reused_segments[name] = entry

    for name in os.listdir(f"{TRIAL08_P1_DIR}/key_phrases"):
        shutil.copyfile(f"{TRIAL08_P1_DIR}/key_phrases/{name}", f"{OUT_B1_DIR}/key_phrases/{name}")
    kp = load_json(f"{OUT_B1_DIR}/key_phrases/keywords_canonicalized.json")
    for item in kp["items"]:
        rank = item["rank"]
        for wav_name in (f"kp{rank}_en", f"kp{rank}_ja_charon"):
            shutil.copyfile(f"{TRIAL08_P1_DIR}/narration/{wav_name}.wav", f"{NARRATION_DIR}/{wav_name}.wav")

    result = {"hash_match": hash_match, "reused_segment_names": list(REUSED_SEGMENT_NAMES),
              "reused_segments": reused_segments, "reused_key_phrases": src_results.get("key_phrases", {}),
              "kp_ranks": [it["rank"] for it in kp["items"]]}
    save_json(f"{OUT_DIR}/audit/reused_from_trial08.json", result)
    print(f"[TRIAL09-AUDIO] Trial-08から再利用: hash_match={hash_match} "
          f"segments={list(REUSED_SEGMENT_NAMES)} kp_ranks={result['kp_ranks']}")
    return result


# ============================================================
# Step 4: Voice A/B本文(Algieba/Erinome想定)専用TTS(Trial専用voice差し替え
# 版、Production news_tail_fix.pyは無変更のまま)
# ============================================================
@review_lock.guarded_generate("en")
def generate_voice_body_minimal_fallback_trial(
        text: str, out_path: str, voice_name: str,
        safety_margin_seconds: float = p3u.NARRATION_BODY_TRIM_SAFETY_MARGIN_SECONDS) -> dict:
    """repro01.generate_english_component_minimal_instruction()のTrial専用
    voice差し替え版(声のみ変更、他ロジックは同一)。Production側は
    p9a.VOICE_NAME固定でvoice引数を持たないため、Voice A/B fallback専用に
    ここへ複製する。"""
    prompt = p4c.build_tts_prompt(text, repro01.MINIMAL_INSTRUCTION_PREFIX)
    call_fn = batch_wiring.make_batch_tts_call_fn(p9a.ENGLISH_MODEL_NAME, voice_name, output_path=out_path)
    pcm, retries, ok, err = common._call_tts_with_retry(
        call_fn, prompt, max_retry=p9a.MAX_TTS_TECHNICAL_RETRY, sleep_fn=None)
    if not ok:
        return {"status": "STOPPED", "reason": f"minimal instructionでもTTS失敗: {err}"}
    samples_raw = common.pcm_bytes_to_float_mono(pcm)
    trimmed, trim_info = p3u.trim_english_keyword_silence(
        samples_raw, common.SAMPLE_RATE, safety_margin_seconds=safety_margin_seconds)
    if trimmed is None:
        return {"status": "STOPPED", "reason": "発話区間を検出できませんでした"}
    anomaly = safety.detect_duration_anomaly(trim_info["raw_duration_seconds"], text, "en")
    if anomaly["is_anomaly"]:
        return {"status": "STOPPED", "reason": anomaly["reason"], "duration_anomaly": anomaly}
    common.write_wav_float(out_path, trimmed, common.SAMPLE_RATE, 1)
    metrics = common.measure_metrics(trimmed, common.SAMPLE_RATE)
    return {
        "status": "OK", "text": text, "path": out_path, "model": p9a.ENGLISH_MODEL_NAME,
        "voice": voice_name, "call_count": 1 + retries, "retry_count": retries,
        "sha256": p9a.sha256_file(out_path), "duration_seconds": round(len(trimmed) / common.SAMPLE_RATE, 4),
        "trim_info": trim_info, "clipping_detected": metrics["clipping_detected"],
        "instruction": "minimal (not ENGLISH_STYLE_PREFIX)",
    }


@review_lock.guarded_generate("en")
def generate_voice_body_wide_margin(text: str, out_path: str, voice_name: str,
                                     max_attempts: int = review_lock.PRODUCTION_MAX_TTS_ATTEMPTS,
                                     max_extra_chars: int = 15) -> dict:
    """news_tail_fix.generate_news_narration_wide_margin()のTrial専用voice
    差し替え版(声のみ変更、ASR検証・Cascade・attempt保存等の他ロジックは
    同一コピー)。Voice A/B本文専用。Production側(news_tail_fix.py)自体は
    無変更のまま。"""
    max_len = len(text) + max_extra_chars
    attempts_log = []
    classification_history = []
    for attempt in range(1, max_attempts + 1):
        call_fn = batch_wiring.make_batch_tts_call_fn(p9a.ENGLISH_MODEL_NAME, voice_name, output_path=out_path)
        prompt = p4c.build_tts_prompt(text, p9a.ENGLISH_STYLE_PREFIX)
        pcm, retries, ok, err = common._call_tts_with_retry(
            call_fn, prompt, max_retry=p9a.MAX_TTS_TECHNICAL_RETRY, sleep_fn=None)
        instruction_type = "english_style_prefix_wide_margin"
        if ok:
            samples_raw = common.pcm_bytes_to_float_mono(pcm)
            trimmed, trim_info = p3u.trim_english_keyword_silence(
                samples_raw, common.SAMPLE_RATE,
                safety_margin_seconds=news_tail_fix.LONG_FORM_TRIM_SAFETY_MARGIN_SECONDS)
            if trimmed is not None:
                anomaly = safety.detect_duration_anomaly(trim_info["raw_duration_seconds"], text, "en")
                if anomaly["is_anomaly"]:
                    trimmed = None
                    err = anomaly["reason"]
        else:
            trimmed, trim_info = None, None

        if trimmed is None:
            attempts_log.append({"attempt": attempt, "status": "STOPPED",
                                  "reason": str(err) if not ok else "発話区間検出失敗",
                                  "instruction_type": instruction_type})
            r = generate_voice_body_minimal_fallback_trial(text, out_path, voice_name)
            instruction_type = "minimal_fallback"
            if r.get("status") != "OK":
                attempts_log.append({"attempt": attempt, "status": r.get("status"), "reason": r.get("reason"),
                                      "instruction_type": instruction_type})
                continue
        else:
            common.write_wav_float(out_path, trimmed, common.SAMPLE_RATE, 1)

        asr_text, asr_err = asr_routing.transcribe(out_path, language="en-US")
        length_ok = asr_text is not None and len(asr_text) <= max_len
        ledger_phrases = [h["canonical_spelling"] for h in pronun_ledger.get_hint_for_text(text, min_confidence="low")]
        verified_content, stop_retrying, cls = secondary_asr.evaluate_attempt_with_cascade(
            text, asr_text, classification_history, out_path, language="en-US",
            ledger_phrases=ledger_phrases, cascade_enabled=secondary_asr.FEATURE_FLAG_SECONDARY_ASR_ENABLED)
        verified = verified_content and length_ok
        gate = dq18.apply_disfluency_gate(verified, out_path, language="en", enabled=False)
        verified = gate["verified"]
        attempts_log.append({"attempt": attempt, "status": "OK", "asr_text": asr_text,
                              "instruction_type": instruction_type, "audio_classification": cls.classification,
                              "connected_speech_info": getattr(cls, "connected_speech_info", None),
                              "length_ok": length_ok, "verified": verified,
                              "trim_info": trim_info, "disfluency_checked": gate["disfluency_checked"],
                              "disfluency_evidence": gate.get("disfluency_evidence")})
        _attempt_audio_path = review_lock.save_tts_attempt_audio(out_path, instruction_type, {
            "loop_attempt_index": attempt, "max_attempts": max_attempts, "language": "en",
            "model": p9a.ENGLISH_MODEL_NAME, "voice": voice_name,
            "tts_execution_mode": batch_wiring.resolve_tts_execution_mode(),
            "asr_text": asr_text, "audio_classification": cls.classification,
            "length_ok": length_ok, "verified": verified,
            "disfluency_checked": gate["disfluency_checked"],
            "disfluency_evidence": gate.get("disfluency_evidence"),
        })
        attempts_log[-1]["attempt_audio_path"] = _attempt_audio_path
        if verified:
            metrics = common.measure_metrics(common.read_wav_float(out_path)[0], common.SAMPLE_RATE)
            return {"status": "OK", "text": text, "path": out_path, "voice": voice_name, "asr_verified": True,
                    "asr_text": asr_text, "attempts_log": attempts_log, "instruction_type": instruction_type,
                    "trim_info": trim_info, "safety_margin_seconds": news_tail_fix.LONG_FORM_TRIM_SAFETY_MARGIN_SECONDS,
                    "clipping_detected": metrics["clipping_detected"], "audio_classification": cls.classification,
                    "connected_speech_info": getattr(cls, "connected_speech_info", None),
                    "disfluency_checked": gate["disfluency_checked"], "disfluency_evidence": gate.get("disfluency_evidence")}
        if stop_retrying:
            metrics = common.measure_metrics(common.read_wav_float(out_path)[0], common.SAMPLE_RATE)
            return {"status": "ASR_VALIDATION_UNCERTAIN", "text": text, "path": out_path, "voice": voice_name,
                    "asr_verified": False, "asr_text": asr_text, "attempts_log": attempts_log,
                    "instruction_type": instruction_type, "trim_info": trim_info,
                    "safety_margin_seconds": news_tail_fix.LONG_FORM_TRIM_SAFETY_MARGIN_SECONDS,
                    "clipping_detected": metrics["clipping_detected"],
                    "reason": f"同一ASR mismatch signatureが連続し、retryでの改善が見込めないため打ち切り"
                              f"(最終classification={cls.classification})"}
    return {"status": "STOPPED", "reason": f"{max_attempts}回試行してもASR検証に合格しませんでした",
            "attempts_log": attempts_log, "voice": voice_name}


# ============================================================
# Step 5: 残りの新規TTS(topic_intro/preview/comment_1-4[Charon]、
# point_one_heading/point_two_heading[Narrator=Aoede]、point_one/point_two
# [Voice A/B])
# ============================================================
def run_tts_new_segments(parts: dict, support_texts: dict, voice_a: str, voice_b: str) -> dict:
    shared_narration.ensure_all_shared_narration_b1(NARRATION_DIR)  # Production、無変更(Master Audio Store経由)

    results = {}
    topic_intro_text = f"Today's topic is {parts['title']}."
    print("[TRIAL09-AUDIO] topic_intro生成(Charon)...")
    with cl.segment_context("topic_intro"):
        results["topic_intro"] = voice01.generate_charon_english(
            tts_gen.tts_safe_number_words_en(tts_gen.tts_safe_en(topic_intro_text)), f"{NARRATION_DIR}/topic_intro.wav")
    results["topic_intro"]["canonical_text"] = topic_intro_text
    assert_budget_ok("after topic_intro TTS")

    for name in ("preview", "comment_1", "comment_2", "comment_3", "comment_4"):
        text = support_texts[name]
        print(f"[TRIAL09-AUDIO] {name}生成(Charon、Voices Contract)...")
        with cl.segment_context(name):
            results[name] = voice01.generate_charon_english(
                tts_gen.tts_safe_number_words_en(tts_gen.tts_safe_en(text)), f"{NARRATION_DIR}/{name}.wav",
                style_prefix_override=tts_gen.B1_PREVIEW_STYLE_PREFIX_CALM, disfluency_qa=True)
        results[name]["canonical_text"] = text
    assert_budget_ok("after preview/comment TTS")

    for name in ("point_one_heading", "point_two_heading"):
        text = parts[name]
        sc.assert_no_point_number_label(text, name)
        print(f"[TRIAL09-AUDIO] {name}生成(Narrator=Aoede、Production point_headings.generate、無変更)...")
        with cl.segment_context(name):
            results[name] = point_headings.generate(
                tts_gen.tts_safe_number_words_en(tts_gen.tts_safe_en(text)), f"{NARRATION_DIR}/{name}.wav")
        results[name]["canonical_text"] = text
    assert_budget_ok("after Narrator heading TTS")

    cooldown_jobs = []
    for name, text, voice_name in (
        ("point_one", parts["point_one_body"], voice_a),
        ("point_two", parts["point_two_body"], voice_b),
    ):
        sc.assert_no_point_number_label(text, name)
        print(f"[TRIAL09-AUDIO] {name}生成({voice_name}、Voice body)...")
        with cl.segment_context(name):
            results[name] = generate_voice_body_wide_margin(
                tts_gen.tts_safe_news_en(text), f"{NARRATION_DIR}/{name}.wav", voice_name)
        results[name]["canonical_text"] = text
        if results[name].get("status") == "STOPPED":
            cooldown_jobs.append(_build_voice_body_cooldown_job(name, text, voice_name))
    assert_budget_ok("after Voice A/B TTS")

    if cooldown_jobs and os.environ.get("TTS_COOLDOWN_OBSERVATION") == "1":
        cooldown_observations = cooldown_obs.run_batch_observations(cooldown_jobs)
        save_json(f"{OUT_B1_DIR}/audit/tts_cooldown_observation_stage_summary.json",
                  {"status": "RAN", "jobs": len(cooldown_jobs), "observations": cooldown_observations})
        print(f"[TRIAL09-AUDIO] TTS cooldown観測: jobs={len(cooldown_jobs)}")

    return results


# ============================================================
# TTS retry cool-down 20分観測フック用job組み立て(Trial限定、既定OFF)
# (TTS-RETRY-COOLDOWN-20MIN-OBSERVATION-TRIAL-01_REPORT.md 2.3節の配線指示)
# ============================================================
def _build_voice_body_cooldown_job(name: str, text: str, voice_name: str) -> dict:
    """`generate_voice_body_wide_margin`がSTOPPEDだったsegment用のcooldown
    観測jobを組み立てる。`three_attempt_records`は既存の
    `{NARRATION_DIR}/attempts/{name}_attempt*.json`(review_lock.
    save_tts_attempt_audio()が書き出す既存スキーマ)から読む。3件未満、
    または3件ともverified=Falseでなければ本jobはNoneを返さず、cooldown_obs
    側の`INELIGIBLE_NOT_EXACTLY_THREE_CONSECUTIVE_NG`判定に委ねる(過剰な
    事前フィルタで観測記録の透明性を落とさないため、A-Family/News harnessの
    事前フィルタとは異なる設計だが、cooldown_obs側の安全性契約は同一)。"""
    out_path = f"{NARRATION_DIR}/_cooldown_observation_01/{name}.wav"
    os.makedirs(f"{NARRATION_DIR}/_cooldown_observation_01", exist_ok=True)
    three = cooldown_helpers.load_three_attempt_records(NARRATION_DIR, name)
    if not three:
        three = []  # cooldown_obs側でINELIGIBLE判定させる(len(three)!=3)
    params = {"model": p9a.ENGLISH_MODEL_NAME, "voice": voice_name, "max_attempts": 1}

    def _capture_live_params():
        return {"model": p9a.ENGLISH_MODEL_NAME, "voice": voice_name,
                "style_prefix": p9a.ENGLISH_STYLE_PREFIX,
                "safety_margin": news_tail_fix.LONG_FORM_TRIM_SAFETY_MARGIN_SECONDS}

    return {
        "level_dir": OUT_B1_DIR, "segment_id": name, "canonical_text": text, "language": "en",
        "three_attempt_records": three, "params": params,
        "single_attempt_fn": generate_voice_body_wide_margin.__wrapped__,
        "single_attempt_args": (), "single_attempt_kwargs": {
            "text": tts_gen.tts_safe_news_en(text), "out_path": out_path, "voice_name": voice_name,
            "max_attempts": 1},
        "capture_live_params_fn": _capture_live_params,
    }


def finalize_tts_results(new_results: dict, reused: dict) -> dict:
    segments = dict(new_results)
    segments.update(reused["reused_segments"])
    data = {"segments": segments, "key_phrases": reused["reused_key_phrases"]}
    save_json(f"{OUT_B1_DIR}/audit/tts_generation_results.json", data)
    all_status = {k: v.get("status") for k, v in segments.items()}
    save_json(f"{OUT_B1_DIR}/run_summary_tts.json", {"segment_status": all_status})
    print(f"[TRIAL09-AUDIO] TTS完了。segment_status={all_status}")
    return data


# ============================================================
# Step 6: Assembly。11個固定segment名をハードコードしているasm.build_b1_
# timeline()だけをTrial専用の新timelineに差し替え、他Production primitive
# (load_b1_sources/apply_b1_gain/assemble_with_timeline/apply_headroom_
# safety_valve)は無変更のまま使う。
# ============================================================
def build_b1_voices_timeline_trial09(parts: dict, voice_a: str, voice_b: str) -> list:
    """item 5の音声構造をそのまま実装する。1点、Key Phraseの位置のみ
    Trial判断で既存B1構造どおり(Preview直後、Full story本文より前)に
    据え置いた(item 5文中の「その他既存episode必須要素…は既存B1構造
    どおり」という記述を、Key phrases intro含む周辺要素の配置を変えない
    指示と解釈した)。Key PhraseをClosing直後へ literal に移動する解釈も
    あり得るため、この解釈はREPORTで明示しUSER_DECISION_REQUIREDとして
    報告する。"""
    key_phrase_blocks = asm.build_b1_key_phrase_blocks(parts)
    b1 = parts["b1_segments"]

    seq = [
        ("Intro", parts["intro"]),
        ("Welcome (Charon)", parts["welcome"]),
        ("pause_0.5", p9a.silence_stereo(0.5)),
        ("Topic intro (Charon)", parts["topic_intro"]),
        ("pause_0.65", p9a.silence_stereo(0.65)),
        ("Notification 1", parts["notification"]),
        ("pause_0.4", p9a.silence_stereo(0.4)),
        ("Preview intro (Charon)", parts["preview_intro"]),
        ("pause_0.65", p9a.silence_stereo(0.65)),
        ("Preview (Charon)", b1["preview"]),
        ("pause_0.5", p9a.silence_stereo(0.5)),
        ("Notification 2", parts["notification"]),
        ("pause_0.4", p9a.silence_stereo(0.4)),
        ("Key phrases intro (Charon)", parts["key_phrases_intro"]),
        ("pause_0.5", p9a.silence_stereo(0.5)),
    ]
    kp_labels = tuple(f"Key Phrase {i}" for i in range(1, len(key_phrase_blocks) + 1))
    for label, block in zip(kp_labels, key_phrase_blocks):
        seq.append((label, block))

    seq += [
        ("Notification 3", parts["notification"]),
        ("pause_0.4", p9a.silence_stereo(0.4)),
        ("Full story intro (Charon)", parts["full_story_intro"]),
        ("pause_1.0", p9a.silence_stereo(asm.AOEDE_TO_CHARON_PAUSE_SECONDS)),
        ("Comment 1 (Charon)", b1["comment_1"]),
        ("pause_0.8", p9a.silence_stereo(asm.CHARON_TO_AOEDE_PAUSE_SECONDS)),
        ("Hook Part 1: The Question (Aoede, no heading)", b1["full_story_part1"]),
        ("pause_0.25_hook_internal_TRIAL_ONLY", p9a.silence_stereo(0.25)),
        ("Hook Part 2: The Question (Aoede, no heading)", b1["full_story_part2"]),
        ("pause_1.0", p9a.silence_stereo(asm.AOEDE_TO_CHARON_PAUSE_SECONDS)),
        ("Comment 2 (Charon, bridge to Voices)", b1["comment_2"]),
        ("pause_0.5_notification_entry", p9a.silence_stereo(asm.NOTIFICATION_ENTRY_PAUSE_SECONDS)),
        ("Point Notification (Voice A cue, existing SFX reuse)", parts["point_notification"]),
        ("Narrator: One Voice heading (Aoede)", b1["point_one_heading"]),
        ("pause_0.7_heading_to_body", p9a.silence_stereo(asm.HEADING_TO_BODY_PAUSE_SECONDS_B1)),
        (f"Voice A body ({voice_a})", b1["point_one"]),
        ("pause_0.5_notification_entry", p9a.silence_stereo(asm.NOTIFICATION_ENTRY_PAUSE_SECONDS)),
        ("Point Notification (Voice B cue, existing SFX reuse)", parts["point_notification"]),
        ("Narrator: Another Voice heading (Aoede)", b1["point_two_heading"]),
        ("pause_0.7_heading_to_body", p9a.silence_stereo(asm.HEADING_TO_BODY_PAUSE_SECONDS_B1)),
        (f"Voice B body ({voice_b})", b1["point_two"]),
        ("pause_1.0", p9a.silence_stereo(asm.AOEDE_TO_CHARON_PAUSE_SECONDS)),
        ("Comment 3 (Charon)", b1["comment_3"]),
        ("pause_0.8", p9a.silence_stereo(asm.CHARON_TO_AOEDE_PAUSE_SECONDS)),
        ("Tension: Where the Difference Comes From (Aoede, no heading)", b1[EXTRA_SEGMENT_NAME]),
        ("pause_1.0", p9a.silence_stereo(asm.AOEDE_TO_CHARON_PAUSE_SECONDS)),
        ("Comment 4 (Charon)", b1["comment_4"]),
        ("pause_0.8", p9a.silence_stereo(asm.CHARON_TO_AOEDE_PAUSE_SECONDS)),
        ("Closing: What the Seat Really Means (Aoede, no heading, In One Line)", b1["in_one_line"]),
        ("pause_0.8_in_one_line_to_outro", p9a.silence_stereo(asm.IN_ONE_LINE_TO_OUTRO_PAUSE_SECONDS)),
        ("Outro (Charon)", parts["outro"]),
    ]
    return seq


def preserve_gate_blocked_evidence(reason: str) -> None:
    """D4(Gate停止時はoverride・fallback追加なし、STOPして報告)。tts_
    generation_results.jsonを走査し、VALIDATED/HUMAN_APPROVED以外の
    segmentについて、最後のattempt音声をevidenceとして保全するだけ
    (Gateを回避しない、er011_open112系Trialの同名関数と同じ考え方)。"""
    data = load_json(f"{OUT_B1_DIR}/audit/tts_generation_results.json")
    evidence_dir = f"{OUT_B1_DIR}/audit/stopped_audio_evidence"
    os.makedirs(evidence_dir, exist_ok=True)
    blocked_segments = {}
    for name, entry in data.get("segments", {}).items():
        status = entry.get("status")
        if status == "OK":
            continue
        blocked_segments[name] = {"status": status, "reason": entry.get("reason")}
        attempts_log = entry.get("attempts_log") or []
        attempt_audio_path = attempts_log[-1].get("attempt_audio_path") if attempts_log else None
        if attempt_audio_path and os.path.exists(attempt_audio_path):
            shutil.copyfile(attempt_audio_path, f"{evidence_dir}/{name}_last_attempt_status_{status}.wav")
        elif os.path.exists(f"{NARRATION_DIR}/{name}.wav"):
            shutil.copyfile(f"{NARRATION_DIR}/{name}.wav", f"{evidence_dir}/{name}_last_attempt_status_{status}.wav")
        save_json(f"{evidence_dir}/{name}_result.json", entry)
    save_json(f"{evidence_dir}/gate_blocked_summary.json", {"reason": reason, "blocked_segments": blocked_segments})
    print(f"[TRIAL09-AUDIO] Gate blocked segments={list(blocked_segments)} のlast attempt音声をevidenceとして"
          "保全した(overrideはしない、record_human_approval()/approve_regenerate()はユーザーの明示指示でのみ実行可)。")


def run_voices_assembly(voice_a: str, voice_b: str) -> dict:
    os.makedirs(f"{OUT_B1_DIR}/assembled", exist_ok=True)
    os.makedirs(f"{OUT_B1_DIR}/audit", exist_ok=True)

    try:
        sources = asm.load_b1_sources(THEME)  # Production、無変更(Gate検証・shared assets copy含む)
    except RuntimeError as e:
        print(f"[TRIAL09-AUDIO] Assembly GATE_BLOCKED(override無し、報告のみ): {e}")
        preserve_gate_blocked_evidence(str(e))
        summary = {"status": "GATE_BLOCKED", "error": str(e), "voice_a": voice_a, "voice_b": voice_b}
        save_json(f"{OUT_B1_DIR}/run_summary_assemble.json", summary)
        return summary

    mono, sr, _, _ = common.read_wav_float(f"{NARRATION_DIR}/{EXTRA_SEGMENT_NAME}.wav")
    assert sr == common.SAMPLE_RATE
    sources["b1_segments"][EXTRA_SEGMENT_NAME] = mono  # apply_b1_gain()はdictをgenericにiterateする(確認済み)

    parts = asm.apply_b1_gain(sources)  # Production、無変更
    seq = build_b1_voices_timeline_trial09(parts, voice_a, voice_b)  # Trial専用
    result = asm.assemble_with_timeline(seq)  # Production、無変更
    headroom = asm.apply_headroom_safety_valve(result["assembled"], seq)  # Production、無変更
    assembled = headroom["assembled"]

    out_path = f"{OUT_B1_DIR}/assembled/Voices_Trial09_B1B_{THEME['theme_id'].upper()}.wav"
    save_json(f"{OUT_B1_DIR}/audit/gain_report.json", parts["gain_report"])
    save_json(f"{OUT_B1_DIR}/audit/timeline.json", result["timeline"])
    save_json(f"{OUT_B1_DIR}/audit/headroom_report.json", headroom["report"])
    common.write_wav_float(out_path, assembled, asm.SR, 2)
    metrics = common.measure_metrics(assembled[:, 0], asm.SR)

    summary = {
        "status": "OK", "out_path": out_path, "duration_seconds": result["total_duration_seconds"],
        "clipping_detected": metrics["clipping_detected"], "peak": round(p9a.peak(assembled), 5),
        "sample_rate": asm.SR, "channels": 2, "headroom_safety_valve": headroom["report"],
        "voice_a": voice_a, "voice_b": voice_b,
    }
    save_json(f"{OUT_B1_DIR}/run_summary_assemble.json", summary)
    print(f"[TRIAL09-AUDIO] Assembly status={summary['status']} duration={summary['duration_seconds']} "
          f"peak={summary['peak']} clipping={summary['clipping_detected']}")
    return summary


# ============================================================
# Step 7: 試聴ページ(file:///形式、音声+完全スクリプト+voiceラベル+
# pause/SFX位置+voice比較sample、item 9)
# ============================================================
# item 5の構造どおりの、narration_dir個別wavの再生順(GATE_BLOCKED時の
# fallback player、およびscript block共通で使う)。
SEGMENT_PLAY_ORDER = [
    ("preview", "Preview (Charon)", "Charon"),
    ("comment_1", "Comment 1 (Charon)", "Charon"),
    ("full_story_part1", "Hook Part 1: The Question (Aoede, no heading)", "Aoede"),
    ("full_story_part2", "Hook Part 2: The Question (Aoede, no heading)", "Aoede"),
    ("comment_2", "Comment 2 (Charon, bridge to Voices)", "Charon"),
    ("point_one_heading", "Narrator: One Voice heading (Aoede)", "Aoede (Narrator)"),
    ("point_one", "Voice A body", "voice_a"),
    ("point_two_heading", "Narrator: Another Voice heading (Aoede)", "Aoede (Narrator)"),
    ("point_two", "Voice B body", "voice_b"),
    ("comment_3", "Comment 3 (Charon)", "Charon"),
    (EXTRA_SEGMENT_NAME, "Tension: Where the Difference Comes From (Aoede, no heading)", "Aoede"),
    ("comment_4", "Comment 4 (Charon)", "Charon"),
    ("in_one_line", "Closing: What the Seat Really Means (Aoede, no heading, In One Line)", "Aoede"),
]


def build_player_html(assemble_summary: dict, parts: dict, support_texts: dict, timeline: list,
                       voice_sample_results: dict, voice_a: str, voice_b: str, resolve_reasons: dict) -> str:
    def audio_tag(path, elem_id):
        abs_path = os.path.abspath(path).replace("\\", "/")
        return f'<audio id="{elem_id}" controls preload="none" src="file:///{abs_path}"></audio>'

    def seek_button(elem_id, start_s, label):
        return f'<button onclick="seek(\'{elem_id}\', {start_s})">▶ {start_s:.1f}s</button> {label}'

    gate_blocked = assemble_summary.get("status") != "OK"

    if gate_blocked:
        gate_dict = load_json(f"{OUT_B1_DIR}/audit/tts_generation_results.json")["segments"]
        rows = []
        for i, (name, label, voice_label) in enumerate(SEGMENT_PLAY_ORDER):
            entry = gate_dict.get(name, {})
            status = entry.get("status")
            voice_display = voice_a if voice_label == "voice_a" else (voice_b if voice_label == "voice_b" else voice_label)
            wav_path = f"{NARRATION_DIR}/{name}.wav"
            if status == "OK" and os.path.exists(wav_path):
                rows.append(f"<h4>{i+1}. {label} <small style='color:#666'>[voice={voice_display}, status=OK]</small></h4>"
                            f"{audio_tag(wav_path, f'seg_{name}')}")
            else:
                evidence_path = f"{OUT_B1_DIR}/audit/stopped_audio_evidence/{name}_last_attempt_status_{status}.wav"
                if os.path.exists(evidence_path):
                    rows.append(f"<h4 style='color:#b00'>{i+1}. {label} "
                                f"<small>[voice={voice_display}, status={status}, UNVALIDATED evidence-only]</small></h4>"
                                f"{audio_tag(evidence_path, f'seg_{name}')}")
                else:
                    rows.append(f"<h4 style='color:#b00'>{i+1}. {label} "
                                f"<small>[voice={voice_display}, status={status}, 音声なし]</small></h4>")
        episode_block = ("<p style='color:#b00'><b>BLOCKED</b>: "
                          f"{assemble_summary.get('error', '')[:400]} … "
                          "完成episodeの1本化Assemblyは行われていません(override無し、human review待ち)。"
                          "以下は各segmentを構造順に個別再生するfallback player(gain調整はProduction Assembly"
                          "適用前の生の個別音量)。</p>" + "".join(rows))
        timeline_table = "<p>(Assembly未実施のためtimeline座標なし。上のfallback playerで構造順に確認してください。)</p>"
    else:
        timeline_rows = []
        for entry in timeline:
            timeline_rows.append(
                f"<tr><td>{seek_button('episode_audio', entry['start_seconds'], '')}</td>"
                f"<td>{entry['part']}</td>"
                f"<td>{entry['start_seconds']:.2f}s</td><td>{entry['duration_seconds']:.2f}s</td></tr>")
        timeline_table = "<table border='1' cellpadding='4' style='border-collapse:collapse;width:100%'>" \
                          "<tr><th>Seek</th><th>Part</th><th>Start</th><th>Duration</th></tr>" \
                          + "".join(timeline_rows) + "</table>"
        episode_block = audio_tag(assemble_summary['out_path'], 'episode_audio')

    script_rows = [
        ("Preview (Charon)", support_texts.get("preview"), "Charon"),
        ("Comment 1 (Charon)", support_texts.get("comment_1"), "Charon"),
        ("Hook: The Question (Aoede, no heading)", parts["part1"] + " " + parts["part2"], "Aoede"),
        ("Comment 2 (Charon)", support_texts.get("comment_2"), "Charon"),
        ("Narrator: One Voice heading (Aoede)", parts["point_one_heading"], "Aoede (Narrator)"),
        (f"Voice A body ({voice_a})", parts["point_one_body"], voice_a),
        ("Narrator: Another Voice heading (Aoede)", parts["point_two_heading"], "Aoede (Narrator)"),
        (f"Voice B body ({voice_b})", parts["point_two_body"], voice_b),
        ("Comment 3 (Charon)", support_texts.get("comment_3"), "Charon"),
        ("Tension: Where the Difference Comes From (Aoede, no heading)", parts["tension_body"], "Aoede"),
        ("Comment 4 (Charon)", support_texts.get("comment_4"), "Charon"),
        ("Closing: What the Seat Really Means (Aoede, no heading, In One Line)", parts["in_one_line"], "Aoede"),
    ]
    script_block = "".join(
        f"<h4>{h} <small style='color:#666'>[voice={v}]</small></h4><p>{b}</p>" for h, b, v in script_rows)

    sample_rows = []
    for voice_name, r in voice_sample_results.items():
        if r.get("status") == "OK":
            sample_rows.append(f"<div class='col'><h4>{voice_name}</h4>"
                                f"{audio_tag(r['path'], f'sample_{voice_name.lower()}')}<p>{r['text']}</p></div>")
        else:
            sample_rows.append(f"<div class='col'><h4>{voice_name} (ERROR)</h4>"
                                f"<p style='color:#b00'>{r.get('error')}</p></div>")
    sample_block = "<div class='row'>" + "".join(sample_rows) + "</div>"

    reason_block = ""
    if resolve_reasons:
        reason_block = "<p style='color:#b00'><b>Voice変更理由:</b> " + \
                        " / ".join(f"{k}: {v}" for k, v in resolve_reasons.items()) + "</p>"

    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>EDITORIAL-B-FAMILY-VOICES-TRIAL-09-AUDIO player</title>
<style>
body {{ font-family: sans-serif; max-width: 960px; margin: 2em auto; }}
h2 {{ border-bottom: 2px solid #333; }}
h4 {{ margin-bottom: 0.2em; }}
p {{ margin-top: 0.2em; color: #333; }}
audio {{ width: 100%; margin: 0.5em 0; }}
.row {{ display: flex; gap: 1.5em; flex-wrap: wrap; }}
.col {{ flex: 1; min-width: 220px; }}
table {{ font-size: 0.9em; }}
button {{ cursor: pointer; }}
</style>
<script>
function seek(id, t) {{ var a = document.getElementById(id); a.currentTime = t; a.play(); }}
</script>
</head><body>
<h1>EDITORIAL-B-FAMILY-VOICES-TRIAL-09-AUDIO-STRUCTURE-REFINEMENT-01</h1>
<p>{"完成候補episode" if not gate_blocked else "GATE_BLOCKED(1本化未実施、下のfallback player参照)"}
(Standard同期、Production採用ではない)。voice_a={voice_a} voice_b={voice_b}
duration={assemble_summary.get('duration_seconds')}s peak={assemble_summary.get('peak')}
clipping={assemble_summary.get('clipping_detected')}</p>
{reason_block}

<h2>Episode audio</h2>
{episode_block}

<h2>Timeline(seek可能)</h2>
{timeline_table}

<h2>完全スクリプト(segmentごとのvoiceラベル付き)</h2>
{script_block}

<h2>Voice比較sample(One Voiceの先頭文、同一textを5 voiceで比較)</h2>
{sample_block}

</body></html>
"""
    out_path = f"{OUT_DIR}/player.html"
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    return out_path


# ============================================================
# main
# ============================================================
def main() -> None:
    os.makedirs(f"{OUT_DIR}/audit", exist_ok=True)
    cl.install(COST_LOG_PATH)

    stage = sys.argv[1] if len(sys.argv) > 1 else "all"
    # 各stageは「直前のstageまでの成果がdiskに保存済み」であることを前提に
    # 単独実行できる(resume用)。ただし単独stage実行時、そのstageの実行に
    # 実際には不要な後続専用データまで無条件でdiskから読もうとすると、まだ
    # 存在しないファイルでFileNotFoundErrorになる。そのため、後段データの
    # 読み込みは「今回の実行で実際に使う場合のみ」に限定する。
    needs_prep = stage in ("prepare", "voice_check", "reuse", "scaffold", "tts", "all")
    needs_voice_resolution = stage in ("tts", "assemble", "player", "all")
    needs_reused = stage in ("tts", "all")

    if stage in ("prepare", "all"):
        prep = prepare()
        save_json(f"{OUT_DIR}/audit/prepare_summary.json", {"parts": prep["parts"]})
    elif needs_prep:
        prep = {"article_text": open(TRIAL07_ARTICLE_PATH, encoding="utf-8").read()}
        prep["parts"] = load_json(f"{OUT_B1_DIR}/parts.json")

    if stage in ("voice_check", "all"):
        sample_text = first_n_sentences(prep["parts"]["point_one_body"], 3)
        sample_results = run_voice_availability_check(sample_text)
        voice_a, voice_b, reasons = resolve_voice_names(sample_results)
        save_json(f"{OUT_DIR}/audit/voice_resolution.json",
                  {"voice_a": voice_a, "voice_b": voice_b, "reasons": reasons})
    elif needs_voice_resolution:
        resolution = load_json(f"{OUT_DIR}/audit/voice_resolution.json")
        voice_a, voice_b, reasons = resolution["voice_a"], resolution["voice_b"], resolution["reasons"]

    if stage in ("reuse", "all"):
        reused = copy_reused_assets_from_trial08(prep["article_text"])
    elif needs_reused:
        reused = load_json(f"{OUT_DIR}/audit/reused_from_trial08.json")

    if stage in ("scaffold", "all"):
        sections = split_five_voice_sections(prep["article_text"])
        with open(TRIAL07_LEDGER_PATH, encoding="utf-8") as f:
            ledger_text = f.read()
        scaffold_result = run_scaffold_voices(prep["parts"], prep["article_text"], sections, ledger_text)
        save_json(f"{OUT_DIR}/audit/scaffold_summary.json",
                  {"support_status": scaffold_result["support_status"],
                   "deviation_overall_status": scaffold_result["deviation"].get("overall_status")})
        assert_budget_ok("after scaffold")

    if stage in ("tts", "all"):
        support_texts = load_json(f"{OUT_B1_DIR}/b1_support_texts.json")
        new_results = run_tts_new_segments(prep["parts"], support_texts, voice_a, voice_b)
        finalize_tts_results(new_results, reused)

    if stage in ("assemble", "all"):
        assemble_summary = run_voices_assembly(voice_a, voice_b)

    if stage in ("player", "all"):
        parts = load_json(f"{OUT_B1_DIR}/parts.json")
        support_texts = load_json(f"{OUT_B1_DIR}/b1_support_texts.json")
        assemble_summary = load_json(f"{OUT_B1_DIR}/run_summary_assemble.json")
        timeline_path = f"{OUT_B1_DIR}/audit/timeline.json"
        timeline = load_json(timeline_path) if os.path.exists(timeline_path) else []
        sample_data = load_json(f"{OUT_DIR}/audit/voice_samples/voice_sample_results.json")
        player_path = build_player_html(assemble_summary, parts, support_texts, timeline,
                                         sample_data["results"], voice_a, voice_b, reasons)
        print(f"[TRIAL09-AUDIO] player.html: {os.path.abspath(player_path)}")

    jpy, by_provider = compute_cost_jpy_so_far()
    print(f"[TRIAL09-AUDIO] 完了(stage={stage})。累積cost={jpy:.2f} JPY by_provider={by_provider}")


if __name__ == "__main__":
    main()
