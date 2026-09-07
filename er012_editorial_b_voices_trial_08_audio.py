# ============================================================
# er012_editorial_b_voices_trial_08_audio.py
# EDITORIAL-B-FAMILY-VOICES-TRIAL-08-AUDIO-FIRST-PERSON-CHECK-01
# ============================================================
# Lane: Lane B / Voices-Perspective。種別: Trial音声化(ユーザー承認
# 2026-09-07)。目的: Trial-07記事(一人称Voice、5区切り: The Question/
# One Voice/Another Voice/Where the Difference Comes From/What the Seat
# Really Means)を音声化し、一人称Voiceが音声でどう聞こえるかを確認する。
# Production採用ではない(5区切り骨格・Contract・一人称・Editor例外・
# Leakage基準はAPPROVED_FOR_PRODUCTIONにしない)。
#
# 設計方針(重要): 既存Production関数(er003_v1_n3_01_scaffold_generate.py
# [sc]・_tts_generate.py [tts_gen]・_assemble.py [asm])は一切変更しない。
# 5区切り→11-part構造の対応が効かない箇所(Tension段落に相当するslotが
# 既存Assemblyに無い)は、Production関数を無変更のままimportし、Trial
# 専用のローカル関数で「入力データを拡張する」形で対応する(Production
# コード自体へフックや分岐を追加しない)。具体的には:
#   - asm.load_b1_sources()はProduction無変更のまま呼び、返ってきた
#     sources["b1_segments"]辞書へTrial側でtension segmentを追加する。
#   - asm.apply_b1_gain()はsources["b1_segments"]の辞書をgenericに
#     iterateするだけの実装なので、無変更のまま呼んでもtension segment
#     を含めてgain処理される(実装を確認済み)。
#   - asm.build_b1_timeline()だけは11個の固定segment名をハードコードして
#     おり、拡張できないため、Trial専用のbuild_b1_voices_timeline()を
#     ここへ新規実装する(asm.build_b1_timeline()自体はコピー元として
#     参照するのみで、無変更のまま残す)。
#
# 触れないもの: docs/pm/*(ACTIVE_TASK.md以外)、SSOT、er011_*・
# er011_output/、Productionコード/Prompt/Validator/Assembly本体。
# 書き込み: 本ファイル(root)、er012_output/editorial_b_voices_trial_08_
# audio/ 配下のみ。Git操作は行わない(Fableが後で統合commit)。
#
# cost > ¥500でSTOP。到達してよいStatus: 音声化完了 + USER_DECISION_
# REQUIRED(一人称/5区切り骨格/11-part拡張のProduction採用判断)。
from __future__ import annotations

import difflib
import hashlib
import json
import os
import re
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

# PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-01: 正式リリース前はStandard同期を使う。
os.environ["TTS_EXECUTION_MODE"] = "STANDARD"

import numpy as np

import er002_common as common
import er003_b1_p9a_audio as p9a
import er003_v1_en_direct_ab_01_generate as ab01
import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_articles_generate as gen
import er003_v1_n3_01_assemble as asm
import er003_v1_n3_01_scaffold_generate as sc
import er003_v1_n3_01_tts_generate as tts_gen
import er003_v1_sing01_news_tail_fix as news_tail_fix
import er005_cost_logger as cl
import er006_model_routing_contract_01 as routing
import er008_disfluency_qa_18 as dq18
import er011_open121_tts_repetition_general_qa_trial_01 as rep_qa

TRIAL07_ARTICLE_PATH = "er012_output/editorial_b_voices_trial_07/b1b_run02_attempt2/article.md"
TRIAL07_LEDGER_PATH = "er012_output/editorial_b_voices_trial_07/research/verified_fact_ledger.txt"

OUT_DIR = "er012_output/editorial_b_voices_trial_08_audio"
COST_LOG_PATH = f"{OUT_DIR}/audit/raw_usage_log.jsonl"
PRICING_SNAPSHOT_PATH = "er005_output/cost_baseline_01/pricing_snapshot.json"
USD_JPY = 160.0
BUDGET_JPY_CAP = 500.0

THEME_P1 = {"theme_id": "voices_trial08_p1", "out_dir": f"{OUT_DIR}/p1"}
THEME_P3 = {"theme_id": "voices_trial08_p3", "out_dir": f"{OUT_DIR}/p3"}

EXTRA_SEGMENT_NAME = "tension_reflection"  # Trial-only、既存11-partに無いsegment

# 版1(P1)の narration segment(記事本文に依存する、単体品質monitoring対象)
P1_MONITOR_SEGMENTS = [
    "topic_intro", "preview", "comment_1", "comment_2", "comment_3", "comment_4",
    "point_one_heading", "point_two_heading", "full_story_part1", "full_story_part2",
    "point_one", "point_two", "in_one_line", EXTRA_SEGMENT_NAME,
]
P3_REGENERATED_SEGMENTS = ["point_one", "point_two"]


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
# コスト計測(er011_open121_tts_repetition_general_qa_trial_01.py の
# compute_cost_jpy_so_far()と同じロジックをTrial専用ログへ適用する)
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
    print(f"[TRIAL08-AUDIO][cost] so far={jpy:.2f} JPY by_provider={by_provider} ({note})")
    if jpy > BUDGET_JPY_CAP:
        raise RuntimeError(f"[BUDGET_GUARD] cost so far {jpy:.2f} JPY > cap {BUDGET_JPY_CAP} JPY. Stopping ({note}).")
    return jpy


# ============================================================
# Step 0: 5区切り構造parser(Trial-04〜07由来、article.md自体は無変更で
# 読み取るだけ。本ファイル内にTrial専用のコピーを持つ、既存の慣例どおり)
# ============================================================
_HEADING_RE = re.compile(r"^(#{2,3})[ \t]+(.+?)\s*$", re.MULTILINE)


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


_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z])")


def split_two_balanced_by_sentence(text: str) -> tuple:
    """Hook(The Question)を、既存split_article_text()のMain Story段落分割と
    同じ「累積語数がなるべく均等になる境界を選ぶ」考え方を、段落ではなく
    文単位に適用したTrial専用ヘルパー。Hookは1段落のみで改行による段落分割が
    効かないため(sc.split_article_text()のロジックをそのまま流用できない)、
    ここだけ文分割版を新規実装する。Production側のsc.split_article_text()
    自体は変更しない。"""
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


def build_parts(article_text: str) -> dict:
    sections = split_five_voice_sections(article_text)
    if sections is None:
        raise RuntimeError("5区切り構造の検出に失敗しました(想定と異なる見出し構成)")
    title = extract_title(article_text)
    hook_part1, hook_part2 = split_two_balanced_by_sentence(sections["hook_body"])
    return {
        "title": title,
        "part1": hook_part1, "part2": hook_part2,
        "point_one_heading": sc.clean_heading(sections["voice_a_heading"]),
        "point_one_body": sections["voice_a_body"],
        "point_two_heading": sc.clean_heading(sections["voice_b_heading"]),
        "point_two_body": sections["voice_b_body"],
        "in_one_line": sections["closing_body"],
        # Trial-only extra(Production側のparts.jsonスキーマには存在しない
        # キー。generate_b1_segments()/run_b1_scaffold()はdict内の未知キーを
        # 無視して動作するため、追加してもProduction経路には影響しない)。
        "tension_heading": sections["tension_heading"],
        "tension_body": sections["tension_body"],
        "_five_section_headings": {k: sections[k] for k in
                                    ("hook_heading", "voice_a_heading", "voice_b_heading",
                                     "tension_heading", "closing_heading")},
    }


# ============================================================
# Step 1 (P1): article.md/parts.json準備
# ============================================================
def prepare_p1() -> dict:
    with open(TRIAL07_ARTICLE_PATH, encoding="utf-8") as f:
        article_text = f.read()
    parts = build_parts(article_text)
    out_dir = f"{THEME_P1['out_dir']}/b1b"
    os.makedirs(f"{out_dir}/audit", exist_ok=True)
    with open(f"{out_dir}/article.md", "w", encoding="utf-8") as f:
        f.write(article_text)
    save_json(f"{out_dir}/parts.json", parts)
    save_json(f"{out_dir}/five_section_length_report.json", {
        "hook_words": len(re.findall(r"[A-Za-z']+", parts["part1"] + " " + parts["part2"])),
        "voice_a_words": ab01.compute_word_count(parts["point_one_body"]),
        "voice_b_words": ab01.compute_word_count(parts["point_two_body"]),
        "tension_words": ab01.compute_word_count(parts["tension_body"]),
        "closing_words": ab01.compute_word_count(parts["in_one_line"]),
    })
    return {"article_text": article_text, "parts": parts}


# ============================================================
# Step 2 (P1): Preview/Comment(Production run_b1_scaffold、無変更)+
# Key Phrase(Production run_key_phrases、無変更)
# ============================================================
def run_scaffold_p1(parts: dict, article_text: str) -> dict:
    out_dir = f"{THEME_P1['out_dir']}/b1b"
    client = sc.get_client()
    print("[TRIAL08-AUDIO][P1] B1 Support(Preview/Comment1-4)生成開始(Production run_b1_scaffold、無変更)...")
    support = sc.run_b1_scaffold(client, parts, out_dir, article_text)
    assert_budget_ok("after P1 support texts")

    kp_dir = f"{out_dir}/key_phrases"
    article_id = "TRIAL08_VOICES_B1B_P1"
    print("[TRIAL08-AUDIO][P1] Key Phrase選定+Canonicalization+Redundancy QA(Production run_key_phrases、無変更)...")
    kp = sc.run_key_phrases(article_text, kp_dir, article_id, "B1-B(EDITORIAL-B-VOICES-TRIAL-08-AUDIO adapter)",
                             process="B1_SUPPORT")
    assert_budget_ok("after P1 key phrases")
    return {"support": {k: v.get("status") for k, v in support.items()}, "support_raw": support, "kp": kp}


# ============================================================
# Step 3 (P1): TTS(Production tts_gen.generate_b1_segments、無変更)+
# Trial専用のtension_reflection segment TTS(既存関数呼び出しパターンを
# そのまま踏襲、新しいTTS instructionは設計しない)
# ============================================================
def generate_tension_segment(out_dir: str, parts: dict) -> dict:
    narration_dir = f"{out_dir}/narration"
    text = parts["tension_body"]
    print(f"[TRIAL08-AUDIO][P1] {EXTRA_SEGMENT_NAME}生成(Aoede、News本文と同じ呼び出しパターン、"
          "Trial専用の追加segment)...")
    with cl.segment_context(EXTRA_SEGMENT_NAME):
        result = news_tail_fix.generate_news_narration_wide_margin(
            tts_gen.tts_safe_news_en(text), f"{narration_dir}/{EXTRA_SEGMENT_NAME}.wav", disfluency_qa=False)
    result["canonical_text"] = text
    return result


def merge_segment_into_results(out_dir: str, name: str, result: dict) -> None:
    """既存tts_generation_results.json(Production tts_gen.generate_b1_segments()が
    書いたもの)へ、Trial専用segmentの結果を追記する。既存segmentのエントリは
    一切書き換えない(追記のみ)。verify_episode_audio_validation_gate()は
    segments辞書をgenericにiterateするため、この追記だけでGate対象に入る。"""
    path = f"{out_dir}/audit/tts_generation_results.json"
    data = load_json(path)
    data["segments"][name] = result
    save_json(path, data)


def run_tts_p1(parts: dict) -> dict:
    out_dir = f"{THEME_P1['out_dir']}/b1b"
    print("[TRIAL08-AUDIO][P1] 標準13/14 segment + Key Phrase TTS生成(Production tts_gen.generate_b1_segments、無変更)...")
    with cl.logging_context(THEME_P1["theme_id"], "tts_b1b_standard"):
        standard_result = tts_gen.generate_b1_segments(THEME_P1)
    assert_budget_ok("after P1 standard TTS")

    with cl.logging_context(THEME_P1["theme_id"], "tts_b1b_tension_extra"):
        tension_result = generate_tension_segment(out_dir, parts)
    merge_segment_into_results(out_dir, EXTRA_SEGMENT_NAME, tension_result)
    assert_budget_ok("after P1 tension segment TTS")
    return {"standard_result": standard_result, "tension_status": tension_result.get("status")}


# ============================================================
# Step 4 (P1): Assembly。asm.stage_assemble_b1()と同じProduction primitive
# (load_b1_sources / apply_b1_gain / assemble_with_timeline /
# apply_headroom_safety_valve、いずれも無変更)を使うが、11個固定segmentの
# build_b1_timeline()だけはTrial専用の拡張版に差し替える。
# ============================================================
def build_b1_voices_timeline(parts: dict) -> list:
    """asm.build_b1_timeline()のコピー(Production側は無変更のまま)。
    Point Two本文の直後、Comment 4(Charon)へ入る前に、5区切り構造の
    'Where the Difference Comes From'(既存11-partに対応slotが無い第4の
    content beat)をAoedeの地の文として1つ追加する。この挿入位置・pauseは
    Trial限定の設計判断であり、Production側のB1構造には存在しない
    Aoede→Aoede連続遷移である(REPORT参照、Production採用には正式な
    構造設計判断が必要)。"""
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
        ("Full Story Part 1 (Aoede)", b1["full_story_part1"]),
        ("pause_1.0", p9a.silence_stereo(asm.AOEDE_TO_CHARON_PAUSE_SECONDS)),
        ("Comment 2 (Charon)", b1["comment_2"]),
        ("pause_0.8", p9a.silence_stereo(asm.CHARON_TO_AOEDE_PAUSE_SECONDS)),
        ("Full Story Part 2 (Aoede)", b1["full_story_part2"]),
        ("pause_1.0", p9a.silence_stereo(asm.AOEDE_TO_CHARON_PAUSE_SECONDS)),
        ("Comment 3 (Charon, Bridge)", b1["comment_3"]),
        ("pause_0.5_notification_entry", p9a.silence_stereo(asm.NOTIFICATION_ENTRY_PAUSE_SECONDS)),
        ("Point Notification (Point One cue)", parts["point_notification"]),
        ("Point One semantic heading (Aoede)", b1["point_one_heading"]),
        ("pause_0.7_heading_to_body", p9a.silence_stereo(asm.HEADING_TO_BODY_PAUSE_SECONDS_B1)),
        ("Point One (Aoede)", b1["point_one"]),
        ("pause_0.5_notification_entry", p9a.silence_stereo(asm.NOTIFICATION_ENTRY_PAUSE_SECONDS)),
        ("Point Notification (Point Two cue)", parts["point_notification"]),
        ("Point Two semantic heading (Aoede)", b1["point_two_heading"]),
        ("pause_0.7_heading_to_body", p9a.silence_stereo(asm.HEADING_TO_BODY_PAUSE_SECONDS_B1)),
        ("Point Two (Aoede)", b1["point_two"]),
        # --- Trial-only追加beat(既存11-partに対応slotが無い、REPORT参照) ---
        ("pause_0.7_point_to_tension_TRIAL_ONLY", p9a.silence_stereo(asm.HEADING_TO_BODY_PAUSE_SECONDS_B1)),
        ("Where the Difference Comes From (Aoede, TRIAL-ONLY EXTRA BEAT)", b1[EXTRA_SEGMENT_NAME]),
        # --- Trial-only追加beatここまで ---
        ("pause_1.0", p9a.silence_stereo(asm.AOEDE_TO_CHARON_PAUSE_SECONDS)),
        ("Comment 4 (Charon)", b1["comment_4"]),
        ("pause_0.8", p9a.silence_stereo(asm.CHARON_TO_AOEDE_PAUSE_SECONDS)),
        ("In One Line (Aoede)", b1["in_one_line"]),
        ("pause_0.8_in_one_line_to_outro", p9a.silence_stereo(asm.IN_ONE_LINE_TO_OUTRO_PAUSE_SECONDS)),
        ("Outro (Charon)", parts["outro"]),
    ]
    return seq


def run_voices_assembly(theme: dict) -> dict:
    out_dir = f"{theme['out_dir']}/b1b"
    os.makedirs(f"{out_dir}/assembled", exist_ok=True)
    os.makedirs(f"{out_dir}/audit", exist_ok=True)
    narration_dir = f"{out_dir}/narration"

    sources = asm.load_b1_sources(theme)  # Production、無変更(Gate検証・shared assets copy含む)
    mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/{EXTRA_SEGMENT_NAME}.wav")
    assert sr == common.SAMPLE_RATE
    sources["b1_segments"][EXTRA_SEGMENT_NAME] = mono  # apply_b1_gain()はdictをgenericにiterateする(確認済み)

    parts = asm.apply_b1_gain(sources)  # Production、無変更
    seq = build_b1_voices_timeline(parts)  # Trial専用(11-part拡張)
    result = asm.assemble_with_timeline(seq)  # Production、無変更
    headroom = asm.apply_headroom_safety_valve(result["assembled"], seq)  # Production、無変更
    assembled = headroom["assembled"]

    out_path = f"{out_dir}/assembled/Voices_Trial08_B1B_{theme['theme_id'].upper()}.wav"
    save_json(f"{out_dir}/audit/gain_report.json", parts["gain_report"])
    save_json(f"{out_dir}/audit/timeline.json", result["timeline"])
    save_json(f"{out_dir}/audit/headroom_report.json", headroom["report"])
    common.write_wav_float(out_path, assembled, asm.SR, 2)
    metrics = common.measure_metrics(assembled[:, 0], asm.SR)

    summary = {
        "status": "OK", "out_path": out_path, "duration_seconds": result["total_duration_seconds"],
        "clipping_detected": metrics["clipping_detected"], "peak": round(p9a.peak(assembled), 5),
        "sample_rate": asm.SR, "channels": 2, "headroom_safety_valve": headroom["report"],
    }
    save_json(f"{out_dir}/run_summary_assemble.json", summary)
    print(f"[TRIAL08-AUDIO][{theme['theme_id']}] Assembly status={summary['status']} "
          f"duration={summary['duration_seconds']} peak={summary['peak']} clipping={summary['clipping_detected']}")
    return summary


# ============================================================
# Step 5 (P3): Voice A/Bのみ機械的に三人称へ変換(内容・文順・情報量は
# 変えない、LLM 1回呼び出し、変換前後の差分を記録)。Production Writer
# Promptは一切使わない、Trial限定の単発テキスト変換タスク。
# ============================================================
THIRD_PERSON_DEVELOPER_MESSAGE = (
    "You are a precise, mechanical text editor. You will be given two short first-person "
    "narrative passages. For each passage, rewrite it in third person ONLY by changing the "
    "personal pronouns and the verb forms that grammatically depend on them (I/my/me/mine -> "
    "'the employee' for the first mention, then a consistent singular 'they/their/them' for "
    "every subsequent reference within that same passage). Do not add, remove, reorder, or "
    "merge any sentence. Do not change any fact, number, noun, adjective, or word choice beyond "
    "what is grammatically required by the pronoun change. Keep paragraph structure identical "
    "(same single paragraph, same sentence count and order). Do not add any new sentence, "
    "clarification, or explanation."
)

THIRD_PERSON_SCHEMA = {
    "name": "voice_third_person_conversion_v1",
    "schema": {
        "type": "object",
        "properties": {
            "voice_a_third_person": {"type": "string"},
            "voice_b_third_person": {"type": "string"},
        },
        "required": ["voice_a_third_person", "voice_b_third_person"],
        "additionalProperties": False,
    },
    "strict": True,
}


def convert_voices_to_third_person(sections: dict) -> dict:
    client = vfl01.get_client()
    model = routing.require_model("B1_WRITER", routing.WRITER_MODEL)
    prompt = (
        f"[Voice A, first person]\n{sections['voice_a_body']}\n\n"
        f"[Voice B, first person]\n{sections['voice_b_body']}\n\n"
        "Convert both passages to third person per the instructions above. Return both "
        "converted passages."
    )
    resp = client.responses.create(
        model=model,
        reasoning={"effort": "low"},
        text={"format": {"type": "json_schema", **THIRD_PERSON_SCHEMA}},
        input=[{"role": "developer", "content": THIRD_PERSON_DEVELOPER_MESSAGE},
               {"role": "user", "content": prompt}],
    )
    parsed = json.loads(resp.output_text)
    return {
        "prompt": prompt, "raw_text": resp.output_text, "parsed": parsed,
        "model": resp.model, "response_id": resp.id,
    }


def word_diff(label_a: str, text_a: str, label_b: str, text_b: str) -> list:
    words_a = text_a.split()
    words_b = text_b.split()
    diff = difflib.unified_diff(words_a, words_b, lineterm="", n=3)
    return list(diff)


# ============================================================
# Step 6 (P3): article/parts/support/kp/narrationをP1からコピー再利用し、
# point_one/point_two(Voice A/B本文)のみ三人称テキストで再生成する
# (er011_open112_trend_theme2_b_final_audio_rerun_02.pyのreuse patternを
# 踏襲、Production関数自体は無変更)。
# ============================================================
def prepare_p3(parts_p1: dict, third_person: dict) -> dict:
    src_dir = f"{THEME_P1['out_dir']}/b1b"
    dst_dir = f"{THEME_P3['out_dir']}/b1b"
    os.makedirs(f"{dst_dir}/audit", exist_ok=True)
    os.makedirs(f"{dst_dir}/narration", exist_ok=True)
    os.makedirs(f"{dst_dir}/key_phrases", exist_ok=True)

    import shutil
    shutil.copyfile(f"{src_dir}/article.md", f"{dst_dir}/article.md")
    for name in os.listdir(f"{src_dir}/key_phrases"):
        shutil.copyfile(f"{src_dir}/key_phrases/{name}", f"{dst_dir}/key_phrases/{name}")
    shutil.copyfile(f"{src_dir}/b1_support_texts.json", f"{dst_dir}/b1_support_texts.json")

    reused_names = [n for n in P1_MONITOR_SEGMENTS if n not in P3_REGENERATED_SEGMENTS]
    kp = load_json(f"{src_dir}/key_phrases/keywords_canonicalized.json")
    kp_wav_names = []
    for item in kp["items"]:
        rank = item["rank"]
        kp_wav_names += [f"kp{rank}_en", f"kp{rank}_ja_charon"]
    for name in reused_names + kp_wav_names:
        shutil.copyfile(f"{src_dir}/narration/{name}.wav", f"{dst_dir}/narration/{name}.wav")
    # Master Audio Store由来のshared narration(welcome等)もそのままコピー
    # (Production ensure_all_shared_narration_b1()は毎回Store参照で再生成
    # コストゼロだが、P3でも同じ経路を素直に呼ぶだけにする)。

    parts_p3 = dict(parts_p1)
    parts_p3["point_one_body"] = third_person["parsed"]["voice_a_third_person"]
    parts_p3["point_two_body"] = third_person["parsed"]["voice_b_third_person"]
    save_json(f"{dst_dir}/parts.json", parts_p3)

    src_results = load_json(f"{src_dir}/audit/tts_generation_results.json")
    dst_results = {"segments": {}, "key_phrases": src_results.get("key_phrases", {})}
    for name in reused_names:
        dst_results["segments"][name] = src_results["segments"][name]
    save_json(f"{dst_dir}/audit/tts_generation_results.json_partial_reused", dst_results)
    return {"parts": parts_p3, "reused_names": reused_names}


STOPPED_EVIDENCE_STATUSES = ("STOPPED", "ASR_VALIDATION_UNCERTAIN", "HUMAN_REVIEW_LOCKED")


def preserve_stopped_audio_evidence(out_dir: str, label: str, result: dict, wav_path: str) -> None:
    """D4(Gate停止時はoverride・fallback追加なし、STOPして報告)。
    er011_open112_trend_theme2_b_final_audio_rerun_02.pyの同名関数と同じ考え方
    (最後のattempt音声をevidenceとして保全するだけ、Gateを回避しない)。"""
    status = result.get("status")
    if status == "OK" or status not in STOPPED_EVIDENCE_STATUSES:
        return
    evidence_dir = f"{out_dir}/audit/stopped_audio_evidence"
    os.makedirs(evidence_dir, exist_ok=True)
    import shutil
    if os.path.exists(wav_path):
        shutil.copyfile(wav_path, f"{evidence_dir}/{label}_last_attempt_status_{status}.wav")
    save_json(f"{evidence_dir}/{label}_result.json", result)
    print(f"[TRIAL08-AUDIO][P3] {label}: status={status} のためlast attempt音声をevidenceとして保全"
          "(overrideはしない)。")


def run_tts_p3(parts_p3: dict) -> dict:
    out_dir = f"{THEME_P3['out_dir']}/b1b"
    narration_dir = f"{out_dir}/narration"
    results = {}
    for name, text in (("point_one", parts_p3["point_one_body"]), ("point_two", parts_p3["point_two_body"])):
        sc.assert_no_point_number_label(text, name)
        print(f"[TRIAL08-AUDIO][P3] {name}(三人称)生成(Aoede、News本文と同じ呼び出しパターン)...")
        wav_path = f"{narration_dir}/{name}.wav"
        with cl.segment_context(name):
            r = news_tail_fix.generate_news_narration_wide_margin(
                tts_gen.tts_safe_news_en(text), wav_path, disfluency_qa=False)
        r["canonical_text"] = text
        results[name] = r
        preserve_stopped_audio_evidence(out_dir, name, r, wav_path)
    assert_budget_ok("after P3 point_one/point_two TTS")

    # partial_reusedへ新規2件をmergeしてtts_generation_results.jsonを完成させる
    partial_path = f"{out_dir}/audit/tts_generation_results.json_partial_reused"
    data = load_json(partial_path)
    data["segments"]["point_one"] = results["point_one"]
    data["segments"]["point_two"] = results["point_two"]
    save_json(f"{out_dir}/audit/tts_generation_results.json", data)
    os.remove(partial_path)
    return {k: v.get("status") for k, v in results.items()}


# ============================================================
# Step 7: Ledger Deviation Checker(Production
# er003_v1_en_direct_vfl_01_generate.run_deviation_check、無変更)を、
# P3再構成後の記事全文(Voice A/Bのみ三人称、他は原文のまま)へ適用する。
# ============================================================
def build_reconstructed_p3_article(article_text: str, sections: dict, third_person: dict) -> str:
    title_match = re.match(r"^#\s+.+?\s*\n", article_text)
    title_line = title_match.group(0)
    return (
        f"{title_line}\n"
        f"## {sections['hook_heading']}\n\n{sections['hook_body']}\n\n"
        f"### {sections['voice_a_heading']}\n\n{third_person['parsed']['voice_a_third_person']}\n\n"
        f"### {sections['voice_b_heading']}\n\n{third_person['parsed']['voice_b_third_person']}\n\n"
        f"## {sections['tension_heading']}\n\n{sections['tension_body']}\n\n"
        f"## {sections['closing_heading']}\n\n{sections['closing_body']}\n"
    )


def run_ledger_deviation_check(reconstructed_article_text: str) -> dict:
    with open(TRIAL07_LEDGER_PATH, encoding="utf-8") as f:
        ledger_text = f.read()
    client = vfl01.get_client()
    print("[TRIAL08-AUDIO][P3] Ledger Deviation Checker(Production vfl01.run_deviation_check、無変更)実行...")
    result = vfl01.run_deviation_check(client, ledger_text, reconstructed_article_text)
    assert_budget_ok("after ledger deviation check")
    return result


# ============================================================
# Step 8: OPEN-121 Trial方式A(n-gram反復検知)+方式D(自己相関)による
# monitoring(gateにはしない、既存er011_open121_tts_repetition_general_qa_
# trial_01.pyの関数をそのまま呼ぶだけ)。segment単体wav + episode該当区間
# (assembled wavから該当秒数を切り出したクリップ)の両方に適用する。
# ============================================================
def run_repetition_monitoring_on_wav(wav_path: str, canonical_text: str | None, item_id: str) -> dict:
    method_d = rep_qa.spectral_self_similarity(wav_path)
    best_run = max((m.get("run_length_seconds_at_thresh_0.85", 0.0) for m in method_d["top_matches"]), default=0.0)
    words = dq18.transcribe_verbatim(wav_path, language="en", model_size="small")
    method_a = rep_qa.detect_ngram_repetition(words, canonical_text=canonical_text, min_words=3)
    return {
        "item_id": item_id, "wav_path": wav_path,
        "method_d_best_run_length_seconds": best_run,
        "method_d_top_matches": method_d["top_matches"],
        "method_a_flagged": method_a["flagged"],
        "method_a_flagged_matches": method_a["flagged_matches"],
        "word_count": len(words),
    }


def extract_clip(assembled_path: str, start_s: float, duration_s: float, out_path: str) -> None:
    import soundfile as sf
    data, sr = sf.read(assembled_path, always_2d=True)
    i0 = int(round(start_s * sr))
    i1 = int(round((start_s + duration_s) * sr))
    clip = data[i0:i1]
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    sf.write(out_path, clip, sr)


def run_monitoring_for_theme(theme: dict, segment_names: list, canonical_text_by_name: dict) -> dict:
    out_dir = f"{theme['out_dir']}/b1b"
    narration_dir = f"{out_dir}/narration"
    # Assembly未完了(Gate停止等)の場合、episode該当区間は取得できないため
    # segment単体monitoringのみ実行する(monitoring自体はgateではないので、
    # STOPPED音声も「参考情報」として単体monitoringにかけることは許容する)。
    assemble_summary_path = f"{out_dir}/run_summary_assemble.json"
    timeline_by_label_substr = {}
    if os.path.exists(assemble_summary_path):
        assembled_path = load_json(assemble_summary_path)["out_path"]
        timeline = load_json(f"{out_dir}/audit/timeline.json")
        for entry in timeline:
            timeline_by_label_substr[entry["part"]] = entry
    else:
        assembled_path = None
        print(f"[TRIAL08-AUDIO][monitoring][{theme['theme_id']}] run_summary_assemble.jsonが無いため"
              "(Assembly未完了)、episode該当区間monitoringはskipし、segment単体monitoringのみ実行する。")

    name_to_label = {
        "topic_intro": "Topic intro (Charon)", "preview": "Preview (Charon)",
        "comment_1": "Comment 1 (Charon)", "comment_2": "Comment 2 (Charon)",
        "comment_3": "Comment 3 (Charon, Bridge)", "comment_4": "Comment 4 (Charon)",
        "point_one_heading": "Point One semantic heading (Aoede)",
        "point_two_heading": "Point Two semantic heading (Aoede)",
        "full_story_part1": "Full Story Part 1 (Aoede)", "full_story_part2": "Full Story Part 2 (Aoede)",
        "point_one": "Point One (Aoede)", "point_two": "Point Two (Aoede)",
        "in_one_line": "In One Line (Aoede)",
        EXTRA_SEGMENT_NAME: "Where the Difference Comes From (Aoede, TRIAL-ONLY EXTRA BEAT)",
    }

    results = {}
    clip_dir = f"{out_dir}/audit/monitoring_clips"
    for name in segment_names:
        wav_path = f"{narration_dir}/{name}.wav"
        canon = canonical_text_by_name.get(name)
        print(f"[TRIAL08-AUDIO][monitoring][{theme['theme_id']}] segment単体 {name} ...")
        standalone = run_repetition_monitoring_on_wav(wav_path, canon, f"{name}_standalone")

        label = name_to_label.get(name)
        episode_clip = None
        if label and label in timeline_by_label_substr:
            entry = timeline_by_label_substr[label]
            clip_path = f"{clip_dir}/{name}_episode_clip.wav"
            extract_clip(assembled_path, entry["start_seconds"], entry["duration_seconds"], clip_path)
            print(f"[TRIAL08-AUDIO][monitoring][{theme['theme_id']}] episode該当区間 {name} "
                  f"(start={entry['start_seconds']}s dur={entry['duration_seconds']}s) ...")
            episode_clip = run_repetition_monitoring_on_wav(clip_path, canon, f"{name}_episode_clip")
        results[name] = {"standalone": standalone, "episode_clip": episode_clip}
    return results


# ============================================================
# Step 9: 試聴ページ(file:///形式、音声+完全スクリプト同一ページ)
# ============================================================
def build_player_html(p1_summary: dict, p3_summary: dict, parts_p1: dict, parts_p3: dict) -> str:
    def audio_tag(path, elem_id):
        abs_path = os.path.abspath(path).replace("\\", "/")
        return f'<audio id="{elem_id}" controls preload="none" src="file:///{abs_path}"></audio>'

    def script_block(parts):
        rows = [
            ("Hook: The Question", parts["part1"] + " " + parts["part2"]),
            ("Voice A: " + parts["point_one_heading"], parts["point_one_body"]),
            ("Voice B: " + parts["point_two_heading"], parts["point_two_body"]),
            ("Where the Difference Comes From (Trial-only extra beat)", parts["tension_body"]),
            ("What the Seat Really Means (In One Line)", parts["in_one_line"]),
        ]
        return "".join(f"<h4>{h}</h4><p>{b}</p>" for h, b in rows)

    p3_ok = p3_summary is not None and p3_summary.get("status") == "OK"
    if p3_ok:
        episode2_block = f"""{audio_tag(p3_summary['out_path'], 'p3_audio')}
{script_block(parts_p3)}"""
        duration_line = (f"duration: P1={p1_summary.get('duration_seconds')}s peak={p1_summary.get('peak')} / "
                          f"P3={p3_summary.get('duration_seconds')}s peak={p3_summary.get('peak')}")
    else:
        episode2_block = ("<p style='color:#b00'><b>BLOCKED</b>: point_two(Voice B, 三人称)がAudio Validation "
                           "Gateで3回ともTRUE_CONTENT_MISMATCH(STOPPED)となり、完成episodeのAssemblyは行われて"
                           "いません(override無し、human review待ち)。下のVoice B(3P)行はGate未検証の"
                           "最終attempt音声(参考用)です。</p>")
        duration_line = f"duration: P1={p1_summary.get('duration_seconds')}s peak={p1_summary.get('peak')} / P3=BLOCKED"

    voice_b_3p_path = f"{THEME_P3['out_dir']}/b1b/narration/point_two.wav"
    voice_b_3p_label = "Voice B (3P, UNVALIDATED/STOPPED)" if not p3_ok else "Voice B (3P)"

    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>EDITORIAL-B-FAMILY-VOICES-TRIAL-08-AUDIO player</title>
<style>
body {{ font-family: sans-serif; max-width: 900px; margin: 2em auto; }}
h2 {{ border-bottom: 2px solid #333; }}
h4 {{ margin-bottom: 0.2em; }}
p {{ margin-top: 0.2em; color: #333; }}
audio {{ width: 100%; margin: 0.5em 0; }}
.row {{ display: flex; gap: 2em; }}
.col {{ flex: 1; }}
</style></head><body>
<h1>EDITORIAL-B-FAMILY-VOICES-TRIAL-08-AUDIO-FIRST-PERSON-CHECK-01</h1>
<p>版1=一人称そのまま(P1) / 版2=Voice A・Bのみ三人称変換、他は版1の音声を再利用(P3)。
{duration_line}</p>

<h2>Episode 1: One Voice / Another Voice (First Person, P1)</h2>
{audio_tag(p1_summary['out_path'], 'p1_audio')}
{script_block(parts_p1)}

<h2>Episode 2: One Voice / Another Voice (Third Person, P3)</h2>
{episode2_block}

<h2>Voice A / Voice B: 1P vs 3P 並べて聞き比べ</h2>
<div class="row">
<div class="col"><h4>Voice A (1P)</h4>{audio_tag(f"{THEME_P1['out_dir']}/b1b/narration/point_one.wav", 'p1_voice_a')}
<p>{parts_p1['point_one_body']}</p></div>
<div class="col"><h4>Voice A (3P)</h4>{audio_tag(f"{THEME_P3['out_dir']}/b1b/narration/point_one.wav", 'p3_voice_a')}
<p>{parts_p3['point_one_body']}</p></div>
</div>
<div class="row">
<div class="col"><h4>Voice B (1P)</h4>{audio_tag(f"{THEME_P1['out_dir']}/b1b/narration/point_two.wav", 'p1_voice_b')}
<p>{parts_p1['point_two_body']}</p></div>
<div class="col"><h4>{voice_b_3p_label}</h4>{audio_tag(voice_b_3p_path, 'p3_voice_b')}
<p>{parts_p3['point_two_body']}</p></div>
</div>

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

    if stage in ("p1_parts", "all"):
        p1_inputs = prepare_p1()
        save_json(f"{OUT_DIR}/audit/p1_inputs_summary.json",
                  {"parts": p1_inputs["parts"]})
    else:
        p1_inputs = {"article_text": open(TRIAL07_ARTICLE_PATH, encoding="utf-8").read()}
        p1_inputs["parts"] = load_json(f"{THEME_P1['out_dir']}/b1b/parts.json")

    if stage in ("p1_scaffold", "all"):
        scaffold_result = run_scaffold_p1(p1_inputs["parts"], p1_inputs["article_text"])
        save_json(f"{OUT_DIR}/audit/p1_scaffold_summary.json",
                  {"support_status": scaffold_result["support"],
                   "kp_status": scaffold_result["kp"].get("status")})

    if stage in ("p1_tts", "all"):
        tts_result = run_tts_p1(p1_inputs["parts"])
        save_json(f"{OUT_DIR}/audit/p1_tts_summary.json", tts_result)

    if stage in ("p1_assemble", "all"):
        p1_assemble = run_voices_assembly(THEME_P1)
        save_json(f"{OUT_DIR}/audit/p1_assemble_summary.json", p1_assemble)

    if stage in ("p3", "all"):
        sections = split_five_voice_sections(p1_inputs["article_text"])
        third_person = convert_voices_to_third_person(sections)
        save_json(f"{OUT_DIR}/audit/third_person_conversion_raw.json", third_person)
        diff_a = word_diff("voice_a_1p", sections["voice_a_body"],
                            "voice_a_3p", third_person["parsed"]["voice_a_third_person"])
        diff_b = word_diff("voice_b_1p", sections["voice_b_body"],
                            "voice_b_3p", third_person["parsed"]["voice_b_third_person"])
        with open(f"{OUT_DIR}/audit/third_person_diff.txt", "w", encoding="utf-8") as f:
            f.write("=== Voice A diff ===\n" + "\n".join(diff_a) + "\n\n=== Voice B diff ===\n" + "\n".join(diff_b))
        assert_budget_ok("after third person conversion")

        p3_prep = prepare_p3(p1_inputs["parts"], third_person)
        p3_tts = run_tts_p3(p3_prep["parts"])
        save_json(f"{OUT_DIR}/audit/p3_tts_summary.json", p3_tts)
        try:
            p3_assemble = run_voices_assembly(THEME_P3)
        except RuntimeError as e:
            p3_assemble = {"status": "GATE_BLOCKED", "error": str(e)}
            print(f"[TRIAL08-AUDIO][P3] Assembly GATE_BLOCKED(override無し、報告のみ): {e}")
        save_json(f"{OUT_DIR}/audit/p3_assemble_summary.json", p3_assemble)

        reconstructed = build_reconstructed_p3_article(p1_inputs["article_text"], sections, third_person)
        with open(f"{OUT_DIR}/audit/p3_reconstructed_article.md", "w", encoding="utf-8") as f:
            f.write(reconstructed)
        deviation = run_ledger_deviation_check(reconstructed)
        save_json(f"{OUT_DIR}/audit/p3_ledger_deviation.json", deviation["parsed"])

    if stage == "p3_resume_after_gate_block":
        # third_person conversion・prepare_p3・run_tts_p3は既に完了済み
        # (point_two=STOPPED、costを二重に発生させないため再実行しない)。
        # assembly retry(同じ入力で、override無しにGateへ再度掛けるだけ)+
        # ledger deviation checkのみ再開する。
        sections = split_five_voice_sections(p1_inputs["article_text"])
        third_person = load_json(f"{OUT_DIR}/audit/third_person_conversion_raw.json")
        try:
            p3_assemble = run_voices_assembly(THEME_P3)
        except RuntimeError as e:
            # D4: Gate停止時はoverride・fallback追加・上限緩和・手動unblockをしない。
            # STOPして報告する(P1は既に独立して完成済みのため、そちらは維持する)。
            p3_assemble = {"status": "GATE_BLOCKED", "error": str(e)}
            print(f"[TRIAL08-AUDIO][P3] Assembly GATE_BLOCKED(override無し、報告のみ): {e}")
        save_json(f"{OUT_DIR}/audit/p3_assemble_summary.json", p3_assemble)

        reconstructed = build_reconstructed_p3_article(p1_inputs["article_text"], sections, third_person)
        with open(f"{OUT_DIR}/audit/p3_reconstructed_article.md", "w", encoding="utf-8") as f:
            f.write(reconstructed)
        deviation = run_ledger_deviation_check(reconstructed)
        save_json(f"{OUT_DIR}/audit/p3_ledger_deviation.json", deviation["parsed"])

    if stage in ("monitoring", "all"):
        parts_p1 = load_json(f"{THEME_P1['out_dir']}/b1b/parts.json")
        canon_by_name_p1 = {
            "topic_intro": f"Today's topic is {parts_p1['title']}.",
            "preview": load_json(f"{THEME_P1['out_dir']}/b1b/b1_support_texts.json")["preview"],
            "comment_1": load_json(f"{THEME_P1['out_dir']}/b1b/b1_support_texts.json")["comment_1"],
            "comment_2": load_json(f"{THEME_P1['out_dir']}/b1b/b1_support_texts.json")["comment_2"],
            "comment_3": load_json(f"{THEME_P1['out_dir']}/b1b/b1_support_texts.json")["comment_3"],
            "comment_4": load_json(f"{THEME_P1['out_dir']}/b1b/b1_support_texts.json")["comment_4"],
            "point_one_heading": parts_p1["point_one_heading"], "point_two_heading": parts_p1["point_two_heading"],
            "full_story_part1": parts_p1["part1"], "full_story_part2": parts_p1["part2"],
            "point_one": parts_p1["point_one_body"], "point_two": parts_p1["point_two_body"],
            "in_one_line": parts_p1["in_one_line"], EXTRA_SEGMENT_NAME: parts_p1["tension_body"],
        }
        mon_p1 = run_monitoring_for_theme(THEME_P1, P1_MONITOR_SEGMENTS, canon_by_name_p1)
        save_json(f"{OUT_DIR}/audit/monitoring_p1.json", mon_p1)

        parts_p3 = load_json(f"{THEME_P3['out_dir']}/b1b/parts.json")
        canon_by_name_p3 = {"point_one": parts_p3["point_one_body"], "point_two": parts_p3["point_two_body"]}
        mon_p3 = run_monitoring_for_theme(THEME_P3, P3_REGENERATED_SEGMENTS, canon_by_name_p3)
        save_json(f"{OUT_DIR}/audit/monitoring_p3.json", mon_p3)

    if stage in ("player", "all"):
        parts_p1 = load_json(f"{THEME_P1['out_dir']}/b1b/parts.json")
        parts_p3 = load_json(f"{THEME_P3['out_dir']}/b1b/parts.json")
        p1_summary = load_json(f"{THEME_P1['out_dir']}/b1b/run_summary_assemble.json")
        p3_assemble_path = f"{THEME_P3['out_dir']}/b1b/run_summary_assemble.json"
        p3_summary = load_json(p3_assemble_path) if os.path.exists(p3_assemble_path) else \
            load_json(f"{OUT_DIR}/audit/p3_assemble_summary.json")
        player_path = build_player_html(p1_summary, p3_summary, parts_p1, parts_p3)
        print(f"[TRIAL08-AUDIO] player.html: {os.path.abspath(player_path)}")

    jpy, by_provider = compute_cost_jpy_so_far()
    print(f"[TRIAL08-AUDIO] 完了(stage={stage})。累積cost={jpy:.2f} JPY by_provider={by_provider}")


if __name__ == "__main__":
    main()
