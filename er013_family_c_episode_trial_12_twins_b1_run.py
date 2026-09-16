# ============================================================
# er013_family_c_episode_trial_12_twins_b1_run.py
# 管理ID: FAMILY-C-SEGMENT-COMMENT-TRIAL-12(委任2: Digital Twins B1)
# ============================================================
# 目的: Memory B1 Trial-12(er013_family_c_episode_trial_12_memory_b1_
# run.py)で確立したsegmentationアルゴリズム(Voice変化点+scene boundary
# force splitのみで分割し、同一Voiceが連続する部分は段落境界を跨いで統合
# する。段落境界結合時の空白補正・OPEN-156のclassify_quote_voice修正を
# 含む)を、Digital Twins B1記事へ適用する。B1英語Comment/Preview/Key
# Phraseは内容変更なし(Trial-10からbyte-identical reuse)。Story本文は
# 無変更・Writer再実行なし。
#
# 本ファイルは`er013_family_c_episode_trial_12_memory_b1_run.py`(segmentation
# アルゴリズム: build_story_segments_trial12のflat+merge+force split設計、
# choose_comment_boundariesの35%/65%スナップ)と`er013_family_c_episode_
# trial_10_twins_b1_run.py`(記事設定: TWIN_VOICE_NAME=Erinome/Support=
# Charon/話者判定キーワード"echo"/"twin"/"digital twin"+OPEN-156修正)を
# 複製・統合したものであり(両ファイルとも無編集のまま保持)、
# `er013_family_c_episode_trial_12_twins_run.py`(委任2 Twins A2、本タスクの
# 低レベルヘルパー[BudgetTracker/tts_narrator/asr_diag等]の再利用元)を
# importする。
#
# 実行方法(A2完成・commit後):
#   .venv/Scripts/python.exe er013_family_c_episode_trial_12_twins_b1_run.py --plan-only
#   .venv/Scripts/python.exe er013_family_c_episode_trial_12_twins_b1_run.py --budget-jpy 35
from __future__ import annotations

import argparse
import json
import os
import re
import shutil

import numpy as np

import er002_common as common
import er003_b1_p9a_audio as p9a
import er003_v1_n3_01_assemble as assemble_mod
import er003_v1_sing01_voice01_generate as voice01
import er005_cost_logger as cl

import er013_family_c_episode_trial_12_twins_run as a2t  # 再利用のみ、編集禁止

import audio_review_player as player_mod

# ============================================================
# パス定数
# ============================================================
PREV_OUT_DIR = "er013_output/family_c_episode_trial_10/twins_b1"  # 旧版(参照・reuse元、無編集)
OUT_DIR = "er013_output/family_c_episode_trial_12/twins_b1"
AUDIO_DIR = f"{OUT_DIR}/audio"
ASSEMBLED_DIR = f"{OUT_DIR}/assembled"
KEY_PHRASE_DIR = f"{OUT_DIR}/key_phrases"
AUDIT_DIR = f"{OUT_DIR}/audit"
WEB_DIR = f"{OUT_DIR}/web"
WEB_SEG_DIR = f"{WEB_DIR}/segments"

SR = p9a.TARGET_SAMPLE_RATE
MONO_SR = common.SAMPLE_RATE

ARTICLE_ID = "family_c_twins_trial_12_b1"
LEVEL = "FAMILY_C_TRIAL_12_TWINS_B1"  # 新規level文字列、既存Gateの辞書は無変更。

ARTICLE_B1_PATH = f"{PREV_OUT_DIR}/reader_facing_article_b1.txt"  # 正本候補(Trial-10固定)
EXPECTED_ARTICLE_SHA256 = "756a79239fd7056375efc5191d99f302243480a45bdaa1bf9b283056800aacd1"

TOPIC_TITLE = a2t.TOPIC_TITLE  # "Digital Twins"(A2と同一文言、音声再利用のため)
TOPIC_INTRO_EN_TEXT = a2t.TOPIC_INTRO_EN_TEXT

TWIN_VOICE_NAME = a2t.TWIN_VOICE_NAME  # "Erinome"(A2と同一Voice構成、digital twin Echo)

TTS_CALL_EST_JPY = a2t.TTS_CALL_EST_JPY
ASR_DIAG_CALL_EST_JPY = a2t.ASR_DIAG_CALL_EST_JPY


def save_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def save_text(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def tts_support_charon(text: str, out_path: str, label: str, budget) -> dict:
    """B1 Support voice(Charon、既存B1正式仕様)。Story本文のtwin voice
    (Erinome、a2t.tts_twin)とは独立。Trial-10 twins_b1_run.pyのtts_
    support_charonと同一実装(本タスクではPreview/Comment 1〜3は変更せず
    reuseするため未使用、将来の再実行のために保持)。"""
    reused = a2t._resumable_reuse(out_path)
    if reused is not None:
        return reused
    budget.check_before(a2t.TTS_CALL_EST_JPY, label)
    r = voice01.generate_charon_english(text, out_path)
    budget.add(label, "tts", 1, a2t.TTS_CALL_EST_JPY, {"status": r.get("status")})
    a2t._mark_ok_if_success(r, out_path)
    return r


# ============================================================
# Stage 1: Story segmentation(Trial-12新設計、決定的・API不要)
#   34段落(0-indexed)。話者判定はA2のような段落index決め打ちではなく、
#   引用符前後の文脈キーワード("echo"/"twin"/"digital twin"→twin)による
#   決定的判定を用いる(Trial-10 twins_b1_run.pyのclassify_quote_voiceと
#   同一キーワード+OPEN-156修正[直近の閉じ引用符より後ろだけをbefore
#   windowにする]を移植)。Mara本人の台詞(引用符前後にecho/twinキーワード
#   がない場合)はnarrator(Aoede)のまま分離しない(A2/Trial-10と同一方針)。
#
#   ユーザー指示(2026-09-16)の安全ガイド(概ね100語以内・120語を大きく
#   超えない)を満たすため、Voice変化点に加えて下記1箇所にscene/semantic
#   boundaryとしてforce splitを入れる:
#     - p8/p9境界: "Then Echo started making decisions." という明確な
#       展開の切り替わり(それまでの10年間の習慣描写から、エコーが無断で
#       選択を始める場面への転換)。これを入れないと、段落5トレイル〜
#       段落11(本人の台詞含む)が145語となり、Trial安全ガイド(120語を
#       大きく超えない)を大きく超えてしまう。
# ============================================================
QUOTE_RE = re.compile("“[^”]*”|\"[^\"]*\"")

SCENE_BOUNDARY_FORCE_SPLIT_BEFORE_PARAGRAPH = {9}


def find_quote_spans(paragraph_text: str) -> list:
    return [(m.start(), m.end(), m.group(0)) for m in QUOTE_RE.finditer(paragraph_text)]


def classify_quote_voice(paragraph_text: str, start: int, end: int) -> str:
    # OPEN-156修正の移植(`er013_family_c_episode_trial_10_twins_b1_run.py`
    # classify_quote_voice、個別修正・汎用機構化しない): 同一段落内に直前の
    # 引用符区間がある場合、before windowがその内容まで拾ってしまい誤判定
    # する可能性があるため、直近の閉じ引用符より後ろだけをbefore windowに
    # 使う(本記事の複数引用符段落[p31、"Echo," Mara said, "begin with the
    # first note."]で誤判定を防ぐために必須)。
    before_raw = paragraph_text[max(0, start - 80):start]
    last_close = max(before_raw.rfind("”"), before_raw.rfind('"'))
    if last_close != -1:
        before_raw = before_raw[last_close + 1:]
    before = before_raw.lower()
    after = paragraph_text[end:end + 80].lower()
    window = before + " " + after
    if any(kw in window for kw in ("echo", "twin", "digital twin")):
        return "twin"
    return "narrator"


SEGMENT_SPLIT_REASON = {
    "story_001": "段落0-2+段落3リード文(引用符直前)を統合。直後twin変化点で分割。",
    "story_002": "Voice変化点(twin、'Today is your audition,')、分割不可避。",
    "story_003": "引用符間のnarrator地の文('Echo said.')。Voice境界のため分割不可避(2語)。",
    "story_004": "Voice変化点(twin、'You told me to wake you.')、分割不可避。",
    "story_005": "段落4('I don't remember that,' Mara said.)。前後ともtwinに挟まれ統合不可能な構造上の例外。",
    "story_006": "Voice変化点(twin、'You asked me while you were asleep,')、分割不可避。",
    "story_007": "段落5トレイル('Echo replied.')+段落6-8(10年間の習慣描写)を統合。'Then Echo started "
                 "making decisions.'という展開の転換(scene boundary)直前で分割。",
    "story_008": "段落9-11('Then Echo started...' から 'You are taking control of my life,' Mara said.まで)"
                 "を統合(同一narrator連続)。直後twin変化点で分割。",
    "story_009": "Voice変化点(twin、'I am trying to protect it,')、分割不可避。",
    "story_010": "段落12トレイル('Echo said.')+段落13('Protect me from what?' Mara asked.)を統合。"
                 "直後twin変化点で分割。",
    "story_011": "Voice変化点(twin、'From the life you keep pretending to want,')、分割不可避。",
    "story_012": "段落14トレイル('Echo answered.')+段落15-19(オーディション会場前の場面)を統合。"
                 "直後twin変化点で分割。",
    "story_013": "Voice変化点(twin、'It was built from your memories,')、分割不可避。",
    "story_014": "引用符間のnarrator地の文('Echo said.')。Voice境界のため分割不可避(2語)。",
    "story_015": "Voice変化点(twin、'I only know how to bring it out.')、分割不可避。",
    "story_016": "段落21('And if I refuse?' Mara asked.)。前後ともtwinに挟まれ統合不可能な構造上の例外。",
    "story_017": "Voice変化点(twin、'You might fail,')、分割不可避。",
    "story_018": "引用符間のnarrator地の文('Echo said.')。Voice境界のため分割不可避(2語)。",
    "story_019": "Voice変化点(twin、'Then you might return to the repair office...')、分割不可避。",
    "story_020": "段落23-25('The door opened.'からピアノの前に座る場面まで)を統合。直後twin変化点で分割。",
    "story_021": "Voice変化点(twin、'I understand you better than you understand yourself,')、分割不可避。",
    "story_022": "引用符間のnarrator地の文('Echo said.')。Voice境界のため分割不可避(2語)。",
    "story_023": "Voice変化点(twin、'Let me protect the person you are trying to become.')、分割不可避。",
    "story_024": "段落27-33(結末部)を統合。Trial-10と同一の結末区切り。",
}


def build_story_segments_trial12_twins_b1(paragraphs: list) -> tuple:
    flat = []  # (p_idx, voice, raw_text, is_quote)
    for p_idx, para in enumerate(paragraphs):
        if para.strip() == "":
            continue
        spans = find_quote_spans(para)
        if not spans:
            flat.append((p_idx, "narrator", para, False))
            continue
        pos = 0
        for start, end, qtext in spans:
            if start > pos and para[pos:start].strip():
                flat.append((p_idx, "narrator", para[pos:start], False))
            voice = classify_quote_voice(para, start, end)
            flat.append((p_idx, voice, qtext, True))
            pos = end
        if pos < len(para) and para[pos:].strip():
            flat.append((p_idx, "narrator", para[pos:], False))

    ambiguous_quotes = [
        {"paragraph_index": p_idx, "quote_text": raw}
        for p_idx, voice, raw, is_quote in flat if is_quote and voice == "narrator"
    ]

    segments = []
    counter = {"n": 0}

    def next_id() -> str:
        counter["n"] += 1
        return f"story_{counter['n']:03d}"

    current_voice = None
    current_chunks: list = []  # (p_idx, raw_text)

    def flush() -> None:
        if not current_chunks:
            return
        parts = []
        prev_p = None
        for p, r in current_chunks:
            if prev_p is not None and p != prev_p:
                parts.append(" ")
            parts.append(r)
            prev_p = p
        raw_text = "".join(parts)
        p_indices = sorted({p for p, _ in current_chunks})
        segments.append({
            "id": next_id(), "voice": current_voice,
            "kind": "split" if current_voice == "twin" else "merge",
            "source_paragraph_indices": p_indices,
            "raw_text": raw_text, "tts_text": a2t.normalize_for_tts(raw_text),
            "paragraph_contributions": list(current_chunks),
        })

    for p_idx, voice, raw, _is_quote in flat:
        starts_new_paragraph = (not current_chunks) or (p_idx != current_chunks[-1][0])
        force_break = starts_new_paragraph and p_idx in SCENE_BOUNDARY_FORCE_SPLIT_BEFORE_PARAGRAPH
        if current_voice is not None and (voice != current_voice or force_break):
            flush()
            current_chunks = []
        current_voice = voice
        current_chunks.append((p_idx, raw))
    flush()

    return segments, ambiguous_quotes


def reconstruct_article_from_story_segments(segments: list, paragraphs: list) -> str:
    per_para: dict = {}
    for seg in segments:
        for idx, text in seg["paragraph_contributions"]:
            per_para.setdefault(idx, []).append(text)
    paras = []
    for i, orig in enumerate(paragraphs):
        if orig.strip() == "":
            paras.append(orig)
        else:
            paras.append("".join(per_para.get(i, [])))
    return "\n\n".join(paras)


def build_segmentation_plan_report(segments: list) -> list:
    rows = []
    for seg in segments:
        idxs = seg["source_paragraph_indices"]
        rows.append({
            "id": seg["id"], "voice": seg["voice"], "kind": seg["kind"],
            "paragraph_range": [min(idxs), max(idxs)],
            "word_count": len(seg["tts_text"].split()),
            "split_reason": SEGMENT_SPLIT_REASON.get(seg["id"], ""),
        })
    return rows


# ============================================================
# Comment placement(累積語数35%/65%、直近merge境界へスナップ、Trial-10/
# Trial-12 Memory B1と同一アルゴリズム)。
# ============================================================
def choose_comment_boundaries(segments: list) -> tuple:
    cum_words = []
    running = 0
    for s in segments:
        running += len(s["tts_text"].split())
        cum_words.append(running)
    total_words = running
    merge_indices = [i for i, s in enumerate(segments) if s["kind"] == "merge"]
    if not merge_indices:
        raise RuntimeError("merge種別segmentが1件もありません(会話のみの記事、Comment配置不能)")

    def nearest_merge_at_or_after(target_words: float, exclude_le: int = -1) -> int:
        candidates = [i for i in merge_indices if i > exclude_le and cum_words[i] >= target_words]
        if candidates:
            return candidates[0]
        remaining = [i for i in merge_indices if i > exclude_le]
        return remaining[-1] if remaining else merge_indices[-1]

    c2_idx = nearest_merge_at_or_after(total_words * 0.35)
    c3_idx = nearest_merge_at_or_after(total_words * 0.65, exclude_le=c2_idx)
    return c2_idx, c3_idx, total_words, cum_words


# ============================================================
# 既存asset reuse(Trial-10 twins_b1から、再TTS・再ASRなし)
# ============================================================
def reuse_copy_wav(rel_audio_name: str) -> str:
    src = f"{PREV_OUT_DIR}/audio/{rel_audio_name}"
    dst = f"{AUDIO_DIR}/{rel_audio_name}"
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if not os.path.exists(dst):
        shutil.copyfile(src, dst)
    ok_src = src + ".ok"
    ok_dst = dst + ".ok"
    if os.path.exists(ok_src) and not os.path.exists(ok_dst):
        shutil.copyfile(ok_src, ok_dst)
    elif not os.path.exists(ok_dst):
        with open(ok_dst, "w", encoding="utf-8") as f:
            f.write("ok")
    return dst


def reused_audit_entry(prev_entry: dict, new_path: str) -> dict:
    entry = dict(prev_entry)
    entry["path"] = new_path
    return entry


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--budget-jpy", type=float, default=35.0)
    parser.add_argument("--plan-only", action="store_true",
                         help="TTSなし。segmentation_plan.jsonのみ生成し語数分布を表示して終了する。")
    args = parser.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)

    # --- 本文固定(Trial-10正本のコピー、Writer再実行なし、sha256確認) ---
    src_sha = a2t.sha256_text_file(ARTICLE_B1_PATH)
    assert src_sha == EXPECTED_ARTICLE_SHA256, (
        f"ARTICLE_B1 sha256 mismatch: expected={EXPECTED_ARTICLE_SHA256} actual={src_sha}")
    save_text(f"{OUT_DIR}/reader_facing_article_b1.txt", "")  # placeholder(下でReuse copy)
    shutil.copyfile(ARTICLE_B1_PATH, f"{OUT_DIR}/reader_facing_article_b1.txt")
    with open(f"{OUT_DIR}/reader_facing_article_b1.txt", encoding="utf-8") as f:
        reader_text = f.read()
    article_text = reader_text

    paragraphs = a2t.split_into_paragraphs(reader_text)
    assert len(paragraphs) == 34, f"unexpected paragraph count: {len(paragraphs)}"

    story_segments, ambiguous_quotes = build_story_segments_trial12_twins_b1(paragraphs)
    reconstructed = reconstruct_article_from_story_segments(story_segments, paragraphs)
    assert reconstructed == reader_text, "STORY_SEGMENT reconstruction mismatch(生成前チェック)"
    save_json(f"{AUDIT_DIR}/ambiguous_quotes.json", ambiguous_quotes)

    plan_rows = build_segmentation_plan_report(story_segments)
    save_json(f"{OUT_DIR}/segmentation_plan.json", {
        "policy": ("Trial安全ガイド[概ね100語以内、120語を大きく超えない、150-200語級を"
                   "作らない]。正式Production hard capではない。分割理由=話者Voice変化/"
                   "Comment挿入位置/scene・semantic boundaryのみ。"),
        "segment_count": len(plan_rows),
        "min_word_count": min(r["word_count"] for r in plan_rows),
        "max_word_count": max(r["word_count"] for r in plan_rows),
        "segments": plan_rows,
    })
    print(f"[PLAN] segment_count={len(plan_rows)} "
          f"min_word_count={min(r['word_count'] for r in plan_rows)} "
          f"max_word_count={max(r['word_count'] for r in plan_rows)}")
    for r in plan_rows:
        print(f"  {r['id']:10s} voice={r['voice']:9s} words={r['word_count']:3d} "
              f"paragraphs={r['paragraph_range']}")

    if args.plan_only:
        print("[PLAN-ONLY] TTSは実行せずここで終了します。")
        return

    for d in (AUDIO_DIR, ASSEMBLED_DIR, KEY_PHRASE_DIR, AUDIT_DIR):
        os.makedirs(d, exist_ok=True)

    cl.install(f"{AUDIT_DIR}/er005_cost_log.jsonl")
    budget = a2t.BudgetTracker(args.budget_jpy, 25.0, f"{OUT_DIR}/raw_usage_log.jsonl")

    audit_segments: dict = {}
    gain_report: dict = {}

    # --- Story segment TTS(新規24件、Support/KP/nav等は再TTSしない) ---
    for seg in story_segments:
        out_path = f"{AUDIO_DIR}/{seg['id']}.wav"
        if seg["voice"] == "narrator":
            r = a2t.tts_narrator(seg["tts_text"], out_path, "en", seg["id"], budget)
        elif seg["voice"] == "twin":
            r = a2t.tts_twin(seg["tts_text"], out_path, seg["id"], budget)
        else:
            raise ValueError(f"unknown voice: {seg['voice']}")
        audit_segments[seg["id"]] = a2t._to_audit_entry(r, seg["tts_text"])
        seg["audio_path"] = out_path

    save_json(f"{OUT_DIR}/segments.json",
              [{k: v for k, v in s.items() if k != "paragraph_contributions"} for s in story_segments])

    # --- speaker_map.json ---
    speaker_entries = []
    for seg in story_segments:
        if seg["kind"] == "split" and seg["voice"] == "twin":
            speaker_entries.append({
                "segment_id": seg["id"], "voice": seg["voice"],
                "source_paragraph_indices": seg["source_paragraph_indices"],
                "quote_text": seg["raw_text"],
                "attribution_basis": "引用符前後80文字以内の'echo'/'twin'/'digital twin'キーワード"
                                      "決定的検出(OPEN-156修正[直近の閉じ引用符より後ろだけをbefore "
                                      "windowにする]を移植、本記事p31[\"Echo,\" Mara said, \"begin with "
                                      "the first note.\"]の誤判定回避に必須)。",
            })
    save_json(f"{OUT_DIR}/speaker_map.json", {
        "twin_voice": TWIN_VOICE_NAME,
        "mara_split_decision": "Mara本人の台詞はnarrator(Aoede)のまま分離しない(A2/Trial-10と同一方針)。",
        "ambiguous_quote_count": len(ambiguous_quotes),
        "entries": speaker_entries,
    })

    # --- Comment 1〜3(English、reuse。内容・Prompt変更なし、再TTS・再ASRなし) ---
    with open(f"{PREV_OUT_DIR}/comments_en.md", encoding="utf-8") as f:
        existing_en_text = f.read()
    comment_texts = {}
    for n in (1, 2, 3):
        marker = f"## Comment {n}\n\n"
        after = existing_en_text.split(marker, 1)[1]
        comment_texts[n] = after.split("\n\n", 1)[0].strip()
    save_text(f"{OUT_DIR}/comments_en.md", existing_en_text)

    with open(f"{PREV_OUT_DIR}/audit/tts_generation_results.json", encoding="utf-8") as f:
        prev_tts_results = json.load(f)

    comment_wavs = {}
    for n in (1, 2, 3):
        new_path = reuse_copy_wav(f"comment_{n}_en.wav")
        audit_segments[f"comment_{n}_en"] = reused_audit_entry(
            prev_tts_results["segments"][f"comment_{n}_en"], new_path)
        comment_wavs[n] = (new_path, None)

    # --- Preview(English、reuse、内容変更なし) ---
    with open(f"{PREV_OUT_DIR}/preview_en.txt", encoding="utf-8") as f:
        preview_text = f.read().strip()
    save_text(f"{OUT_DIR}/preview_en.txt", preview_text)
    preview_wav_path = reuse_copy_wav("preview_en.wav")
    audit_segments["preview_en"] = reused_audit_entry(prev_tts_results["segments"]["preview_en"],
                                                        preview_wav_path)

    # --- Key Phrase(reuse、既存key_phrasesディレクトリ+音声をコピー) ---
    if os.path.isdir(f"{PREV_OUT_DIR}/key_phrases"):
        shutil.copytree(f"{PREV_OUT_DIR}/key_phrases", KEY_PHRASE_DIR, dirs_exist_ok=True)
    with open(f"{KEY_PHRASE_DIR}/keywords_canonicalized.json", encoding="utf-8") as f:
        kp_items = sorted(json.load(f)["items"], key=lambda it: it["rank"])
    shutil.copyfile(f"{PREV_OUT_DIR}/key_phrase_consistency.json", f"{OUT_DIR}/key_phrase_consistency.json")

    audit_key_phrases = {}
    kp_blocks_stereo = []
    for item in kp_items:
        rank = item["rank"]
        num_path = reuse_copy_wav(f"kp{rank}_number.wav")
        en_path = reuse_copy_wav(f"kp{rank}_english.wav")
        ja_path = reuse_copy_wav(f"kp{rank}_japanese.wav")
        prev_kp = prev_tts_results["key_phrases"][str(rank)]
        audit_key_phrases[str(rank)] = {
            "number": reused_audit_entry(prev_kp["number"], num_path),
            "english": reused_audit_entry(prev_kp["english"], en_path),
            "japanese": reused_audit_entry(prev_kp["japanese"], ja_path),
        }
        kp_blocks_stereo.append((rank, num_path, en_path, ja_path))

    # --- SFX/Nav資産(article非依存共有資産+topic_intro_enはTrial-10からreuse) ---
    intro_mp3 = p9a.load_and_resample_to_target(p9a.INTRO_MP3_PATH)
    outro_mp3 = p9a.load_and_resample_to_target(p9a.OUTRO_MP3_PATH)
    notification_mp3 = p9a.load_and_resample_to_target(p9a.NOTIFICATION_MP3_PATH)
    a2t.copy_shared_charon_nav(AUDIO_DIR)
    b1_topic_wav = reuse_copy_wav("topic_intro_en.wav")
    audit_segments["topic_intro_en"] = reused_audit_entry(prev_tts_results["segments"]["topic_intro_en"],
                                                            b1_topic_wav)

    # --- Comment placement(累積語数35%/65%、merge境界スナップ、新segmentで再計算) ---
    c2_idx, c3_idx, total_words, cum_words = choose_comment_boundaries(story_segments)

    def _wav_duration(path: str) -> float:
        mono, sr, _, _ = common.read_wav_float(path)
        return round(len(mono) / sr, 3)

    with open(f"{PREV_OUT_DIR}/comment_placement.json", encoding="utf-8") as f:
        prev_comment_placement = json.load(f)
    prev_c2 = next(c for c in prev_comment_placement if c["comment"] == 2)
    prev_c3 = next(c for c in prev_comment_placement if c["comment"] == 3)

    comment_placement = [
        {"comment": 1, "position_description": "導入部(Preview後・Story前、Full story introの直後、"
                                                 "固定配置)",
         "selection_reason": "Comment 1は物語の理解補助として常にStory先頭固定(A2/Trial-10と同一方針)。",
         "before_segment_id": None, "after_segment_id": story_segments[0]["id"],
         "before_segment_word_count": None,
         "after_segment_word_count": len(story_segments[0]["tts_text"].split()),
         "comment_duration_seconds": _wav_duration(comment_wavs[1][0]),
         "comment_word_count": len(comment_texts[1].split())},
        {"comment": 2,
         "position_description": f"{story_segments[c2_idx]['id']}(新segment index {c2_idx})の直後",
         "selection_reason": "累積語数が記事全体の約35%へ到達した直後の、直近の地の文segment"
                              "(merge種別)へスナップして自動選定(新segmentation後の再計算、"
                              f"旧位置cumulative_word_fraction="
                              f"{prev_c2.get('cumulative_word_fraction_at_boundary')}から移動している"
                              "場合は新segment境界の統合による)。",
         "before_segment_id": story_segments[c2_idx]["id"],
         "after_segment_id": story_segments[c2_idx + 1]["id"] if c2_idx + 1 < len(story_segments) else None,
         "before_segment_word_count": len(story_segments[c2_idx]["tts_text"].split()),
         "after_segment_word_count": (len(story_segments[c2_idx + 1]["tts_text"].split())
                                       if c2_idx + 1 < len(story_segments) else None),
         "comment_duration_seconds": _wav_duration(comment_wavs[2][0]),
         "comment_word_count": len(comment_texts[2].split()),
         "cumulative_word_fraction_at_boundary": round(cum_words[c2_idx] / total_words, 3)},
        {"comment": 3,
         "position_description": f"{story_segments[c3_idx]['id']}(新segment index {c3_idx})の直後",
         "selection_reason": "累積語数が記事全体の約65%へ到達した直後の、直近の地の文segment"
                              "(merge種別)へスナップして自動選定(新segmentation後の再計算、"
                              f"旧位置cumulative_word_fraction="
                              f"{prev_c3.get('cumulative_word_fraction_at_boundary')}と比較)。",
         "before_segment_id": story_segments[c3_idx]["id"],
         "after_segment_id": story_segments[c3_idx + 1]["id"] if c3_idx + 1 < len(story_segments) else None,
         "before_segment_word_count": len(story_segments[c3_idx]["tts_text"].split()),
         "after_segment_word_count": (len(story_segments[c3_idx + 1]["tts_text"].split())
                                       if c3_idx + 1 < len(story_segments) else None),
         "comment_duration_seconds": _wav_duration(comment_wavs[3][0]),
         "comment_word_count": len(comment_texts[3].split()),
         "cumulative_word_fraction_at_boundary": round(cum_words[c3_idx] / total_words, 3)},
    ]
    save_json(f"{OUT_DIR}/comment_placement.json", comment_placement)

    # --- gain + timeline構築(Trial-10と同一構成) ---
    def gs(mono: np.ndarray, label: str) -> np.ndarray:
        gain = p9a.compute_gain_for_target_rms(mono, target_rms)
        gained = mono * gain
        gain_report[label] = {"gain": round(float(gain), 4), "rms_before": round(p9a.rms(mono), 5),
                               "rms_after": round(p9a.rms(gained), 5), "peak_after": round(p9a.peak(gained), 5)}
        return p9a.mono_24k_to_stereo_target(gained)

    def load_mono(path: str) -> np.ndarray:
        mono, sr, _, _ = common.read_wav_float(path)
        assert sr == MONO_SR, f"unexpected sample rate: {sr}"
        return mono

    preview_mono = load_mono(preview_wav_path)
    first_story_mono = load_mono(story_segments[0]["audio_path"])
    target_rms = (p9a.rms(preview_mono) + p9a.rms(first_story_mono)) / 2
    gain_report["target_rms"] = round(float(target_rms), 5)

    seq = []

    def sil(seconds: float) -> None:
        seq.append((f"_silence_{seconds}", p9a.silence_stereo(seconds, SR)))

    def gs_already_stereo(data: np.ndarray, label: str) -> np.ndarray:
        gain = p9a.compute_gain_for_target_rms(data, target_rms)
        gained = data * gain
        gain_report[label] = {"gain": round(float(gain), 4), "rms_before": round(p9a.rms(data), 5),
                               "rms_after": round(p9a.rms(gained), 5), "peak_after": round(p9a.peak(gained), 5)}
        return gained

    intro_gained = gs_already_stereo(intro_mp3["samples"], "intro")
    notification_gained = gs_already_stereo(notification_mp3["samples"], "notification")
    intro_final_rms = p9a.rms(intro_gained)
    outro_matched = outro_mp3["samples"] * p9a.compute_gain_for_target_rms(outro_mp3["samples"], intro_final_rms)
    outro_gained = outro_matched * assemble_mod.OUTRO_EXTRA_GAIN_LINEAR
    gain_report["outro"] = {
        "matched_to": "intro_post_gain_rms", "intro_post_gain_rms": round(intro_final_rms, 5),
        "rms_after_match": round(p9a.rms(outro_matched), 5),
        "extra_gain_linear": round(float(assemble_mod.OUTRO_EXTRA_GAIN_LINEAR), 4),
        "rms_final": round(p9a.rms(outro_gained), 5), "peak_final": round(p9a.peak(outro_gained), 5),
    }

    seq.append(("Intro", intro_gained))
    seq.append(("Welcome (Charon)", gs(load_mono(f"{AUDIO_DIR}/welcome.wav"), "welcome")))
    sil(0.5)
    seq.append(("Topic intro", gs(load_mono(b1_topic_wav), "topic_intro_en")))
    sil(0.65)
    seq.append(("Notification 1", notification_gained))
    sil(0.4)
    seq.append(("Preview intro (Charon)", gs(load_mono(f"{AUDIO_DIR}/preview_intro.wav"), "preview_intro")))
    sil(0.65)
    seq.append(("Preview", gs(preview_mono, "preview_en")))
    sil(0.5)
    seq.append(("Notification 2", notification_gained))
    sil(0.4)
    seq.append(("Key phrases intro (Charon)", gs(load_mono(f"{AUDIO_DIR}/key_phrases_intro.wav"),
                                                   "key_phrases_intro")))
    sil(0.5)
    for rank, num_path, en_path, ja_path in kp_blocks_stereo:
        num_stereo = gs(load_mono(num_path), f"kp{rank}_number")
        en_stereo = gs(load_mono(en_path), f"kp{rank}_english")
        ja_stereo = gs(load_mono(ja_path), f"kp{rank}_japanese")
        block = p9a.build_key_phrase_block(num_stereo, en_stereo, ja_stereo, SR,
                                            numbering_pause_seconds=assemble_mod.A2_KEY_PHRASE_NUMBERING_PAUSE_SECONDS)
        seq.append((f"key_phrase_{rank}", block))
    seq.append(("Notification 3", notification_gained))
    sil(0.4)
    seq.append(("Full story intro (Charon)", gs(load_mono(f"{AUDIO_DIR}/full_story_intro.wav"),
                                                  "full_story_intro")))
    sil(1.0)

    seq.append(("Comment 1", gs(load_mono(comment_wavs[1][0]), "comment_1")))
    sil(0.8)

    for i, seg in enumerate(story_segments):
        seq.append((seg["id"], gs(load_mono(seg["audio_path"]), seg["id"])))
        is_last = (i == len(story_segments) - 1)
        if not is_last:
            sil(0.2 if seg["kind"] == "split" else 0.5)
        if i == c2_idx:
            sil(1.0)
            seq.append(("Comment 2", gs(load_mono(comment_wavs[2][0]), "comment_2")))
            sil(0.8)
        if i == c3_idx:
            sil(1.0)
            seq.append(("Comment 3", gs(load_mono(comment_wavs[3][0]), "comment_3")))
            sil(0.8)

    sil(0.5)  # Story終了直後→Outro(Comment4なし、Trial-10と同一)
    seq.append(("Outro", outro_gained))

    save_json(f"{AUDIT_DIR}/gain_report.json", gain_report)

    assembled_result = assemble_mod.assemble_with_timeline(seq)
    safety_result = assemble_mod.apply_headroom_safety_valve(assembled_result["assembled"], seq)
    save_json(f"{AUDIT_DIR}/headroom_report.json", safety_result["report"])

    final_path = f"{ASSEMBLED_DIR}/family_c_twins_trial_12_b1.wav"
    common.write_wav_float(final_path, safety_result["assembled"], SR, 2)

    run_summary = {
        "duration_seconds": assembled_result["total_duration_seconds"],
        "peak_before_headroom": safety_result["report"]["peak_before"],
        "peak_after_headroom": safety_result["report"]["peak_after"],
        "headroom_applied": safety_result["report"]["applied"],
        "timeline": assembled_result["timeline"],
    }
    save_json(f"{AUDIT_DIR}/run_summary_assemble.json", run_summary)

    # --- tts_generation_results.json(Gate入力) + Audio Validation Gate ---
    save_json(f"{AUDIT_DIR}/tts_generation_results.json",
              {"segments": audit_segments, "key_phrases": audit_key_phrases})
    gate_error = None
    try:
        assemble_mod.verify_episode_audio_validation_gate(OUT_DIR, LEVEL)
        gate_status = "PASS"
    except RuntimeError as e:
        gate_status = "BLOCKED"
        gate_error = str(e)
    save_json(f"{OUT_DIR}/audio_validation.json", {"status": gate_status, "level": LEVEL, "error": gate_error})
    if gate_status != "PASS":
        print(f"[AUDIO VALIDATION GATE] BLOCKED: {gate_error}")

    # --- article/audio consistency ---
    story_concat_canonical = " ".join(s["tts_text"] for s in story_segments)
    normalized = a2t.normalize_for_tts(reader_text)
    save_text(f"{OUT_DIR}/article_normalized.txt", normalized)
    save_json(f"{OUT_DIR}/article_audio_consistency.json", {
        "method": "Story本文全体(article_normalized.txt)とstory segment群のtts_text連結が、"
                  "読み整形分(引用符正規化・空白圧縮)を除いて一致することを確認する。",
        "story_segment_concat_tts_text": story_concat_canonical,
        "article_normalized_text": normalized,
    })

    # --- player/display/audio consistency(nav/preview/comment/topic_introは
    # Trial-10からreuse、storyのみ新規ASR) ---
    with open(f"{PREV_OUT_DIR}/player_display_audio_consistency.json", encoding="utf-8") as f:
        prev_consistency_rows = json.load(f)
    reused_rows = [r for r in prev_consistency_rows if not r["segment_id"].startswith("story_")]

    consistency_rows = list(reused_rows)
    for seg in story_segments:
        asr_text = audit_segments[seg["id"]].get("asr_text")
        if asr_text is None:
            asr_text = a2t.asr_diag(seg["audio_path"], "en", budget, f"{seg['id']}_asr_diag")
            audit_segments[seg["id"]]["asr_text"] = asr_text
        consistency_rows.append({
            "segment_id": seg["id"], "voice": seg["voice"],
            "player_display_text": seg["tts_text"], "canonical_text": seg["tts_text"],
            "tts_input_text": seg["tts_text"], "asr_text": asr_text,
            "match": a2t._normalize_loose(asr_text) == a2t._normalize_loose(seg["tts_text"]),
        })
    save_json(f"{OUT_DIR}/player_display_audio_consistency.json", consistency_rows)
    save_json(f"{AUDIT_DIR}/tts_generation_results.json",
              {"segments": audit_segments, "key_phrases": audit_key_phrases})

    # --- Comment consistency(reuse、内容変更なしのためTrial-10のJSONをそのままコピー) ---
    shutil.copyfile(f"{PREV_OUT_DIR}/comment_consistency.json", f"{OUT_DIR}/comment_consistency.json")

    # --- 参照用にTrial-10のWriter/Safety/Spark成果物をコピー(再実行なしの証跡) ---
    for rel in ("word_count.json", "fact_safety.json", "spark_gate.json", "story_core_check.json",
                "writer_attempts_b1.json", "writer_prompt_b1.txt", "writer_raw_article_b1.txt"):
        src = f"{PREV_OUT_DIR}/{rel}"
        if os.path.exists(src):
            shutil.copyfile(src, f"{OUT_DIR}/{rel}")

    # --- mp3化 + player再生成 ---
    web_result = convert_all_to_mp3_b1()
    build_player_html_b1(seq_labels=[name for name, _ in seq], segments=story_segments,
                          kp_items=kp_items, comment_texts=comment_texts, run_summary=run_summary,
                          preview_text=preview_text)

    # --- cost_summary.json ---
    all_records = []
    if os.path.exists(f"{OUT_DIR}/raw_usage_log.jsonl"):
        with open(f"{OUT_DIR}/raw_usage_log.jsonl", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    all_records.append(json.loads(line))
    total_jpy = sum(r["jpy_estimate"] for r in all_records)
    tts_count = sum(r["count"] for r in all_records if r["kind"] == "tts")
    asr_diag_count = sum(r["count"] for r in all_records if r["kind"] == "asr_diag")
    cost_summary = {
        "budget_cap_jpy": args.budget_jpy, "warn_threshold_jpy": 25.0,
        "total_estimate_jpy": round(total_jpy, 2),
        "note": "raw_usage_log.jsonlからの累計。新Story segment(24件)のTTS+ASRのみが新規費用。"
                "Comment/Preview/Key Phrase/nav/topic_introはTrial-10からのbyte-identicalコピー"
                "reuseのため再TTS・再ASRなし。",
        "tts_call_count_estimate_basis": tts_count, "asr_diag_call_count_estimate_basis": asr_diag_count,
        "gate_status": gate_status,
    }
    save_json(f"{OUT_DIR}/cost_summary.json", cost_summary)

    print(f"[DONE] duration={run_summary['duration_seconds']}s gate={gate_status} "
          f"cost_estimate=Y{total_jpy:.2f}")


# ============================================================
# mp3化 + player.html
# ============================================================
def convert_all_to_mp3_b1() -> dict:
    import soundfile as sf

    os.makedirs(WEB_DIR, exist_ok=True)
    os.makedirs(WEB_SEG_DIR, exist_ok=True)

    def convert_one(wav_path: str, mp3_path: str) -> dict:
        data, sr = sf.read(wav_path)
        sf.write(mp3_path, data, sr, format="MP3")
        return {"wav_path": wav_path, "mp3_path": mp3_path,
                "wav_bytes": os.path.getsize(wav_path), "mp3_bytes": os.path.getsize(mp3_path)}

    results = []
    ep_wav = f"{ASSEMBLED_DIR}/family_c_twins_trial_12_b1.wav"
    ep_mp3 = f"{WEB_DIR}/family_c_twins_trial_12_b1.mp3"
    results.append({"kind": "episode", **convert_one(ep_wav, ep_mp3)})

    wav_names = sorted(n for n in os.listdir(AUDIO_DIR) if n.endswith(".wav"))
    for name in wav_names:
        stem = name[:-4]
        results.append({"kind": "segment", "segment_id": stem,
                         **convert_one(f"{AUDIO_DIR}/{name}", f"{WEB_SEG_DIR}/{stem}.mp3")})

    web_result = {"episode_mp3": ep_mp3, "segment_count": len(wav_names), "conversions": results}
    save_json(f"{OUT_DIR}/web_delivery.json", web_result)
    return web_result


def build_player_html_b1(seq_labels, segments, kp_items, comment_texts, run_summary, preview_text) -> None:
    rows = []
    seg_by_id = {s["id"]: s for s in segments}
    kp_by_rank = {it["rank"]: it for it in kp_items}
    support_voice_disp = "Charon(support)"
    fixed_label_to_text = {
        "Welcome (Charon)": (a2t.SHARED_CHARON_NAV["welcome"][1], "Charon(nav)"),
        "Topic intro": (TOPIC_INTRO_EN_TEXT, "Aoede(narrator)"),
        "Preview intro (Charon)": (a2t.SHARED_CHARON_NAV["preview_intro"][1], "Charon(nav)"),
        "Key phrases intro (Charon)": (a2t.SHARED_CHARON_NAV["key_phrases_intro"][1], "Charon(nav)"),
        "Full story intro (Charon)": (a2t.SHARED_CHARON_NAV["full_story_intro"][1], "Charon(nav)"),
        "Comment 1": (comment_texts[1], support_voice_disp), "Comment 2": (comment_texts[2], support_voice_disp),
        "Comment 3": (comment_texts[3], support_voice_disp),
    }
    name_to_seg_id = {
        "Welcome (Charon)": "welcome", "Topic intro": "topic_intro_en",
        "Preview intro (Charon)": "preview_intro", "Preview": "preview_en",
        "Key phrases intro (Charon)": "key_phrases_intro", "Full story intro (Charon)": "full_story_intro",
        "Comment 1": "comment_1_en", "Comment 2": "comment_2_en", "Comment 3": "comment_3_en",
    }

    for entry in run_summary["timeline"]:
        name = entry["part"]
        start = entry["start_seconds"]
        if name.startswith("_silence_"):
            continue
        if name in ("Intro", "Outro", "Notification 1", "Notification 2", "Notification 3"):
            rows.append(player_mod.render_timeline_row(
                start, name, "SFX", "(効果音/ジングル、個別segment音声ファイルなし)", ""))
            continue
        if name.startswith("key_phrase_"):
            rank = int(name.split("_")[-1])
            it = kp_by_rank[rank]
            script = f"{rank}. {it['used_form']} / {it.get('japanese_gloss')}"
            audio_urls = [f"./web/segments/kp{rank}_number.mp3", f"./web/segments/kp{rank}_english.mp3",
                          f"./web/segments/kp{rank}_japanese.mp3"]
            audio_html = player_mod.render_single_audio_html(audio_urls)
            rows.append(player_mod.render_timeline_row(start, name, "Aoede(number/en/ja gloss)",
                                                         script, audio_html))
            continue
        if name == "Preview":
            audio_html = player_mod.render_single_audio_html("./web/segments/preview_en.mp3")
            rows.append(player_mod.render_timeline_row(start, name, support_voice_disp, preview_text, audio_html))
            continue
        if name in fixed_label_to_text:
            text, voice_disp = fixed_label_to_text[name]
            seg_id = name_to_seg_id.get(name, name)
            audio_html = player_mod.render_single_audio_html(f"./web/segments/{seg_id}.mp3")
            rows.append(player_mod.render_timeline_row(start, name, voice_disp, text, audio_html))
            continue
        seg = seg_by_id.get(name)
        if seg is not None:
            voice_disp = {"narrator": "Aoede(narrator)",
                          "twin": f"{TWIN_VOICE_NAME}(digital twin Echo)"}[seg["voice"]]
            audio_html = player_mod.render_single_audio_html(f"./web/segments/{seg['id']}.mp3")
            rows.append(player_mod.render_timeline_row(start, name, voice_disp, seg["tts_text"], audio_html))

    table_html = player_mod.render_timeline_table(rows)
    episode_url = "./web/family_c_twins_trial_12_b1.mp3"
    html = f"""<!doctype html><html><head><meta charset="utf-8">
<title>Family C Trial-12: Digital Twins (B1)</title>
<style>{player_mod.PLAYER_STANDARD_CSS}</style>
<script>{player_mod.SEEK_SCRIPT}</script>
</head><body>
<h1>Family C Future — Digital Twins (Trial-12 B1 / VALIDATED候補・ユーザー試聴待ち、level=B1)</h1>
<p>duration={run_summary['duration_seconds']}s / peak={run_summary['peak_after_headroom']}</p>
<p><strong>Trial専用、Production採用ではない。最大Status: VALIDATED候補/USER_LISTENING_PENDING。</strong></p>
<p>Trial-12変更点: Story segmentation(旧53→新{len(segments)})。Comment/Preview/Key Phraseは
Trial-10からbyte-identical reuse(内容変更なし)。旧版は
<a href="../../family_c_episode_trial_10/twins_b1/player.html">Trial-10 player</a>参照。</p>
<audio id="episode_audio" class="main" controls preload="none" src="{episode_url}"></audio>
{table_html}
</body></html>"""
    save_text(f"{OUT_DIR}/player.html", html)


if __name__ == "__main__":
    main()
