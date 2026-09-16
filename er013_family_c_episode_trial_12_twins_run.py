# ============================================================
# er013_family_c_episode_trial_12_twins_run.py
# 管理ID: FAMILY-C-SEGMENT-COMMENT-TRIAL-12(委任2: Digital Twins A2)
# ============================================================
# 目的: Memory A2 Trial-11でユーザーが試聴し「問題なし」と評価したStory
# segmentation方式(できるだけ自然な連続発話としてまとめ、Voice変化点/
# Comment挿入位置/scene・semantic boundaryだけで分割する)と、Comment
# 1〜3の英文理解ガイド型Promptを、Digital Twins A2(Mara/Echo)へ展開する。
#
# 本ファイルは`er013_family_c_episode_trial_11_memory_run.py`(segmentation
# アルゴリズム設計・Comment Promptロジック)と`er013_family_c_episode_
# trial_10_twins_run.py`(記事設定: ARTICLE_PATH/Voice割当[narrator=Aoede/
# digital twin Echo=Erinome]/Echo表記個別対応/Comment位置)を複製・統合した
# ものであり(両ファイルとも無編集のまま保持)、Story本文は無変更・Writer
# 再実行なし。
#
# 重要な発見(本タスクの分析結果): Trial-10 Twins A2のSTORY_SEGMENT_PLANは
# すでに「Voice変化点/Comment挿入位置/scene boundaryのみで分割する」という
# Trial-11原則に沿って手作業で設計されていた(Memory/Twins B1のような
# 段落ごとの機械的分割ではなかった)。そのため、本タスクでTrial-11型の
# 分割アルゴリズム(build_all_story_segments_trial12_twins、Voice変化点+
# scene boundary force splitのみで分割理由を判定)を独立に適用した結果、
# 新segmentationは旧22 segmentと完全に同一(tts_text・voice列とも一致)に
# なることを確認した(下記main()内でassertし、一致しない場合はSTOPする)。
# したがって物語Story音声はTrial-10から**re-TTSせずbyte-identicalに再利用**
# する(理由なき再生成を避けるTokenGuard/Cost Guard方針に合致)。実際に
# 新規生成するのはComment 1〜3(新Prompt)のみである。
#
# 実行方法:
#   .venv/Scripts/python.exe er013_family_c_episode_trial_12_twins_run.py \
#       --plan-only
#   .venv/Scripts/python.exe er013_family_c_episode_trial_12_twins_run.py \
#       --budget-jpy 45
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import time

os.environ.setdefault("TTS_EXECUTION_MODE", "STANDARD")

import numpy as np

import er002_common as common
import er003_b1_p9a_audio as p9a
import er003_v1_iran01_a2_generate as a2gen
import er003_v1_n3_01_assemble as assemble_mod
import er003_v1_repro01_main_generate as repro01
import er005_cost_logger as cl
import er006_asr_provider_routing_01 as asr_routing
import er012_b_family_voices_production_01 as bvoices

import audio_review_player as player_mod

# ============================================================
# パス定数
# ============================================================
ARTICLE_PATH = "er013_output/family_c_future_trial_08/digital_twins/reader_facing_article.txt"
PREV_OUT_DIR = "er013_output/family_c_episode_trial_10/twins_a2"  # 旧版(参照・reuse元、無編集)
OUT_DIR = "er013_output/family_c_episode_trial_12/twins_a2"
AUDIO_DIR = f"{OUT_DIR}/audio"
ASSEMBLED_DIR = f"{OUT_DIR}/assembled"
KEY_PHRASE_DIR = f"{OUT_DIR}/key_phrases"
AUDIT_DIR = f"{OUT_DIR}/audit"
WEB_DIR = f"{OUT_DIR}/web"
WEB_SEG_DIR = f"{WEB_DIR}/segments"

SR = p9a.TARGET_SAMPLE_RATE  # 48000
MONO_SR = common.SAMPLE_RATE  # 24000

ARTICLE_ID = "family_c_twins_trial_12"
LEVEL = "FAMILY_C_TRIAL_12_TWINS_A2"  # 新規level文字列、既存Gateの辞書は無変更。

TOPIC_TITLE = "Digital Twins"
TOPIC_INTRO_EN_TEXT = f"Today's topic is {TOPIC_TITLE}."
JAPANESE_TITLE_TEXT = "デジタルツイン"  # Trial-10と同一(直訳1件、既登録)

B1_SHARED_SOURCE_DIR = "er003_output/b1redesign_audio_01/IRAN01/narration"
SHARED_CHARON_NAV = {
    "welcome": ("welcome_charon.wav", "Welcome to English Your Way."),
    "preview_intro": ("preview_intro_charon.wav", "Here's a quick preview."),
    "key_phrases_intro": ("key_phrases_intro_charon.wav", "Here are today's key phrases."),
    "full_story_intro": ("full_story_intro_charon.wav", "Now, the full story."),
}
NUMBER_WORDS = {1: "One.", 2: "Two.", 3: "Three.", 4: "Four.", 5: "Five."}
_SHARED_NUMBER_WORD_SOURCE = {
    1: f"{B1_SHARED_SOURCE_DIR}/num_one_charon.wav",
    2: f"{B1_SHARED_SOURCE_DIR}/num_two_charon.wav",
    3: f"{B1_SHARED_SOURCE_DIR}/num_three_charon.wav",
    4: f"{B1_SHARED_SOURCE_DIR}/num_four_charon.wav",
    5: f"{B1_SHARED_SOURCE_DIR}/num_five_charon.wav",
}

INTRO_MP3_PATH = p9a.INTRO_MP3_PATH
OUTRO_MP3_PATH = p9a.OUTRO_MP3_PATH
NOTIFICATION_MP3_PATH = p9a.NOTIFICATION_MP3_PATH

TWIN_VOICE_NAME = "Erinome"  # デジタルツインEchoのvoice(Trial-10と同一、変更なし)

# ============================================================
# 予算管理(Trial-11と同一方式)
# ============================================================
TTS_CALL_EST_JPY = 0.9
LLM_CALL_EST_JPY = 1.8
ASR_DIAG_CALL_EST_JPY = 0.3


class BudgetTracker:
    def __init__(self, cap_jpy: float, warn_jpy: float, log_path: str):
        self.cap = cap_jpy
        self.warn = warn_jpy
        self.spent = 0.0
        self.warned = False
        self.log_path = log_path
        self.records = []

    def check_before(self, estimated_next_jpy: float, label: str) -> None:
        projected = self.spent + estimated_next_jpy
        if projected > self.cap:
            raise RuntimeError(
                f"BUDGET_WOULD_EXCEED: stage '{label}' の見込み追加費用(推定)"
                f"¥{estimated_next_jpy:.2f}を加えると累計¥{projected:.2f}が"
                f"上限¥{self.cap:.2f}を超えます。ここで停止します。")

    def add(self, label: str, kind: str, count: int, unit_jpy: float, meta: dict | None = None) -> None:
        jpy = count * unit_jpy
        self.spent += jpy
        rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "label": label, "kind": kind,
               "count": count, "unit_jpy_estimate": unit_jpy, "jpy_estimate": round(jpy, 4),
               "cumulative_jpy_estimate": round(self.spent, 4), "meta": meta or {}}
        self.records.append(rec)
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        if not self.warned and self.spent >= self.warn:
            self.warned = True
            print(f"[BUDGET WARNING] cumulative(estimate)=Y{self.spent:.2f} >= warn threshold Y{self.warn:.2f}")
        if self.spent > self.cap:
            raise RuntimeError(
                f"BUDGET_EXCEEDED: cumulative(estimate)=Y{self.spent:.2f} > cap Y{self.cap:.2f}"
                f"(stage '{label}' 実行後)。")


# ============================================================
# 1. Format normalization + segment分割(決定的、API不要)
#    段落0-indexedで33段落。Echo(digital twin)の直接発話・表示メッセージを
#    twin voiceへ分離する(Trial-10 twins_run.pyのTWIN_QUOTE_PARAGRAPH_
#    INDICES/TWIN_DISPLAY_PARAGRAPH_INDICESをそのまま踏襲、変更なし)。
#    Mara本人の台詞はnarrator(Aoede)のまま分離しない(Trial-10と同一方針)。
#
#    Trial-11型の分割アルゴリズム(Voice変化点/Comment挿入位置/scene
#    boundaryのみを分割理由とし、同一Voiceが連続する部分は段落境界を
#    跨いで統合する)を適用する。段落23(Comment 3挿入位置、"The door
#    opened."の直後で"Inside, the panel waited..."と区切る scene
#    boundary)のみforce splitとして明示する(前後とも同じnarrator Voice
#    だが、Comment挿入位置を保持するために分割する。これは委任文が定める
#    有効な分割理由の一つ[Comment挿入位置]である)。
# ============================================================
QUOTE_RE = re.compile("“[^”]*”")

TWIN_QUOTE_PARAGRAPH_INDICES = {3, 5, 11, 13, 19, 21, 25}
TWIN_DISPLAY_PARAGRAPH_INDICES = {16}
FORCE_SPLIT_BEFORE_PARAGRAPH = {23}  # Comment 3挿入位置(段落22/23境界)を維持するための明示的分割

COMMENT_2_AFTER_SEGMENT_ID = "story_010"  # 段落13直後(旧Trial-10 comment_2_after_plan_index=7と同一の
                                           # 意味的位置: 私的な会話からオーディション会場前への場面転換)
COMMENT_3_AFTER_SEGMENT_ID = "story_019"  # 段落22直後(旧Trial-10 comment_3_after_plan_index=14と同一の
                                           # 意味的位置: "The door opened."の直後、決断場面の手前)
# C1はStory開始直前に固定(Trial-10と同一)。Comment 4は使用しない。


def load_article_text(path: str = ARTICLE_PATH) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def split_into_paragraphs(text: str) -> list:
    return text.split("\n\n")


def split_paragraph_by_quotes(paragraph_text: str, quote_voice: str) -> list:
    """段落内の“...”を境に(voice, raw_text)へ分割する。raw_textを順に連結
    するとparagraph_textへ完全一致で復元できる(新しい語・語順変更なし)。"""
    chunks = []
    pos = 0
    for m in QUOTE_RE.finditer(paragraph_text):
        if m.start() > pos:
            chunks.append(("narrator", paragraph_text[pos:m.start()]))
        chunks.append((quote_voice, m.group(0)))
        pos = m.end()
    if pos < len(paragraph_text):
        chunks.append(("narrator", paragraph_text[pos:]))
    return chunks


def normalize_for_tts(raw_text: str) -> str:
    t = raw_text
    t = t.replace("“", '"').replace("”", '"')
    t = t.replace("‘", "'").replace("’", "'")
    t = t.replace("**", "")
    t = re.sub(r"\s+", " ", t).strip()
    return t


SEGMENT_SPLIT_REASON_NOTE = (
    "Voice変化点(narrator[Aoede]⇄twin[Erinome])は分割不可避。段落23の分割のみ"
    "Comment 3挿入位置(scene boundary、有効な分割理由)を保持するための明示分割。"
    "それ以外は同一Voiceが連続する限り段落境界を跨いで統合する。"
)


def build_all_story_segments_trial12_twins(paragraphs: list) -> list:
    """Trial-11型segmentation設計をDigital Twins A2記事へ適用する。段落を
    quoteで細分し、(paragraph_index, voice, raw_text)のflatな列を作った上で、
    Voice変化点またはFORCE_SPLIT_BEFORE_PARAGRAPHのみで区切りを入れ、それ以外は
    連続する同一Voiceを一つのTTS segmentへ統合する(段落境界を跨ぐ結合時は
    半角スペース1個を補い、normalize_for_ttsが余分な空白を圧縮する)。"""
    flat = []  # (p_idx, voice, raw_text)
    for p_idx, para in enumerate(paragraphs):
        if p_idx in TWIN_QUOTE_PARAGRAPH_INDICES:
            for voice, raw in split_paragraph_by_quotes(para, "twin"):
                if raw.strip() != "" or True:  # 空chunkも later flush()側でraw保持(空白復元のため許容)
                    flat.append((p_idx, voice, raw))
        elif p_idx in TWIN_DISPLAY_PARAGRAPH_INDICES:
            flat.append((p_idx, "twin", para))
        else:
            flat.append((p_idx, "narrator", para))

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
            "raw_text": raw_text, "tts_text": normalize_for_tts(raw_text),
            "paragraph_contributions": list(current_chunks),
        })

    for p_idx, voice, raw in flat:
        starts_new_paragraph = (not current_chunks) or (p_idx != current_chunks[-1][0])
        force_break = starts_new_paragraph and p_idx in FORCE_SPLIT_BEFORE_PARAGRAPH
        if current_voice is not None and (voice != current_voice or force_break):
            flush()
            current_chunks = []
        current_voice = voice
        current_chunks.append((p_idx, raw))
    flush()

    return segments


def reconstruct_article_from_story_segments(segments: list, num_paragraphs: int) -> str:
    per_para: dict = {}
    for seg in segments:
        for idx, text in seg["paragraph_contributions"]:
            per_para.setdefault(idx, []).append(text)
    paras = ["".join(per_para[i]) for i in range(num_paragraphs)]
    return "\n\n".join(paras)


def build_segmentation_plan_report(segments: list) -> list:
    rows = []
    for seg in segments:
        idxs = seg["source_paragraph_indices"]
        rows.append({
            "id": seg["id"], "voice": seg["voice"], "kind": seg["kind"],
            "paragraph_range": [min(idxs), max(idxs)],
            "word_count": len(seg["tts_text"].split()),
            "split_reason": SEGMENT_SPLIT_REASON_NOTE,
        })
    return rows


# ============================================================
# 2. Preview(既存Trial-10音声reuse、内容変更なし) / Comment(新Prompt)
# ============================================================
_JA_SUPPORT_COMMON_NOTE = (
    "表記の注意: デジタルツインの名前は必ず片仮名で「エコー」と書いて"
    "ください(英字の\"Echo\"は使わないでください)。数字は算用数字で"
    "書いてください。"
)
_BANNED_PHRASES_INSTRUCTION = (
    "「聞いてみましょう」「耳を傾けて」「耳を澄ませて」「注目してみましょう」"
    "「これからどうなるでしょう」のような、聞く行為だけを促す言い回しは"
    "使わないでください。雰囲気だけの抽象的な誘導や、本文を聞けば分かる"
    "だけの無内容な予告も避けてください。"
)

COMMENT_1_ROLE_JA_TRIAL12_TWINS = (
    "あなたは英語学習者向け音声番組で、物語の直前に置く短い日本語コメントを"
    "書く担当です。これから始まる物語の理解を助けるため、雰囲気作りの声かけ"
    "ではなく状況説明に徹してください。本文に書かれている事実のみを使い、"
    "次の点のうち必要なものだけを2〜3文・80〜110字程度で簡潔にまとめて"
    "ください: 主人公マラが、自分のデータで学習したデジタルツイン「エコー」と"
    "10年間暮らしていること、エコーが最近マラに無断でお金や仕事に関わる"
    "選択をし始めていること、マラ自身はピアニストになりたいという夢を"
    "周囲に隠してきたこと。結末や主人公の最終的な選択には触れないで"
    "ください。新しい設定・登場人物を追加しないでください。"
    + _BANNED_PHRASES_INSTRUCTION + _JA_SUPPORT_COMMON_NOTE
)
COMMENT_2_ROLE_JA_TRIAL12_TWINS = (
    "あなたは英語学習者向け音声番組で、物語の途中に挿入する短い日本語"
    "コメントを書く担当です。これから、私的な会話の場面から一転して、"
    "主人公マラがオーディション会場の外に立つ場面へ切り替わります。英文の"
    "理解を助けるため、雰囲気作りではなく状況整理に徹してください。本文の"
    "事実のみを使い、次の点のうち必要なものだけを2〜3文・80〜110字程度で"
    "まとめてください: 時刻は九時でマラがオーディション会場の外に立って"
    "いること、手が冷たくガラスの向こうにピアノが見えていること、まもなく"
    "コンタクトレンズにエコーからのメッセージが届くこと。結末や主人公の"
    "選択には触れないでください。新しい設定・事実を追加しないでください。"
    + _BANNED_PHRASES_INSTRUCTION + _JA_SUPPORT_COMMON_NOTE
)
COMMENT_3_ROLE_JA_TRIAL12_TWINS = (
    "あなたは英語学習者向け音声番組で、物語の途中に挿入する短い日本語"
    "コメントを書く担当です。これから、扉が開き、主人公マラが審査員の前で"
    "ピアノに向かおうとする場面が続きます。英文の理解を助けるため、雰囲気"
    "作りではなく状況整理に徹してください。本文の事実のみを使い、次の点の"
    "うち必要なものだけを2〜3文・80〜110字程度でまとめてください: 扉が"
    "開いてマラが部屋の中へ進もうとしていること、手の動きをエコーに委ねる"
    "か自分の手で弾くかという選択がこの先で迫られること。結末(実際に"
    "どちらを選んだか)には触れないでください。新しい設定・事実を追加"
    "しないでください。" + _BANNED_PHRASES_INSTRUCTION + _JA_SUPPORT_COMMON_NOTE
)
COMMENT_ROLES = {1: COMMENT_1_ROLE_JA_TRIAL12_TWINS, 2: COMMENT_2_ROLE_JA_TRIAL12_TWINS,
                  3: COMMENT_3_ROLE_JA_TRIAL12_TWINS}
COMMENT_NUMBERS = (1, 2, 3)  # Family C既定(Comment 4なし、Trial-10から無変更)

BANNED_COMMENT_PHRASES_RE = re.compile(
    "聞いてみましょう|耳を傾け|耳を澄ま|注目して|どうなるでしょう")


def run_ja_support_text(client, role_instruction: str, article_text: str, label: str,
                         budget: BudgetTracker) -> dict:
    budget.check_before(LLM_CALL_EST_JPY, label)
    context = f"【物語全文(参考、新しい設定・事実の追加禁止)】\n{article_text}"
    result = a2gen.run_support_text(client, role_instruction, context, model=a2gen.MODEL)
    budget.add(label, "llm", 1, LLM_CALL_EST_JPY, {"status": result.get("status")})
    if result.get("status") != "OK":
        raise RuntimeError(f"SUPPORT_TEXT_FAILED({label}): {result}")
    return result


def run_ja_comment_text(client, comment_num: int, article_text: str, budget: BudgetTracker) -> str:
    result = run_ja_support_text(client, COMMENT_ROLES[comment_num], article_text,
                                  f"comment_{comment_num}_llm", budget)
    text = result["text"].strip()
    if BANNED_COMMENT_PHRASES_RE.search(text):
        result2 = run_ja_support_text(client, COMMENT_ROLES[comment_num], article_text,
                                       f"comment_{comment_num}_llm_retry1", budget)
        text2 = result2["text"].strip()
        if not BANNED_COMMENT_PHRASES_RE.search(text2):
            return text2
        raise RuntimeError(
            f"COMMENT_BANNED_PHRASE_AFTER_RETRY(comment_{comment_num}): "
            f"再生成後も禁止語句が残存: {text2!r}")
    return text


# ============================================================
# 3. TTS呼び出しラッパ(Trial-10/11と同一実装)
# ============================================================
def _ok_marker_path(out_path: str) -> str:
    return out_path + ".ok"


def _resumable_reuse(out_path: str) -> dict | None:
    if os.path.exists(out_path) and os.path.exists(_ok_marker_path(out_path)):
        return {"status": "REUSED_EXISTING_FILE", "path": out_path,
                "sha256": p9a.sha256_file(out_path)}
    return None


def _mark_ok_if_success(r: dict, out_path: str) -> None:
    if r.get("status") == "OK":
        with open(_ok_marker_path(out_path), "w", encoding="utf-8") as f:
            f.write("ok")
    else:
        debug_path = out_path + ".debug.json"
        with open(debug_path, "w", encoding="utf-8") as f:
            json.dump(r, f, ensure_ascii=False, indent=2, default=str)


def reuse_shared_number_word(rank: int, out_path: str) -> dict:
    if not os.path.exists(out_path):
        shutil.copyfile(_SHARED_NUMBER_WORD_SOURCE[rank], out_path)
    with open(_ok_marker_path(out_path), "w", encoding="utf-8") as f:
        f.write("ok")
    return {"status": "OK", "path": out_path, "sha256": p9a.sha256_file(out_path), "reused_shared_asset": True}


def copy_shared_charon_nav(out_dir: str) -> dict:
    result = {}
    for key, (fname, _text) in SHARED_CHARON_NAV.items():
        dst = f"{out_dir}/{key}.wav"
        if not os.path.exists(dst):
            shutil.copyfile(f"{B1_SHARED_SOURCE_DIR}/{fname}", dst)
        with open(_ok_marker_path(dst), "w", encoding="utf-8") as f:
            f.write("ok")
        result[key] = {"status": "OK", "path": dst, "sha256": p9a.sha256_file(dst), "reused_shared_asset": True}
    return result


def copy_from_prev_if_missing(rel_name: str) -> None:
    """Trial-10 twins_a2の既存正常asset(Intro/Outro/SFX/Welcome/Key Phrase/
    Preview/日本語タイトル/topic_intro等、Story segment/Comment以外)を新
    OUT_DIRへコピーする(.okマーカー含む、再TTSしない)。"""
    src = f"{PREV_OUT_DIR}/{rel_name}"
    dst = f"{OUT_DIR}/{rel_name}"
    if os.path.isdir(src):
        shutil.copytree(src, dst, dirs_exist_ok=True)
        return
    if os.path.exists(dst):
        return
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.exists(src):
        shutil.copyfile(src, dst)


def copy_story_audio_from_prev(seg_id: str) -> None:
    src = f"{PREV_OUT_DIR}/audio/{seg_id}.wav"
    dst = f"{AUDIO_DIR}/{seg_id}.wav"
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


def tts_narrator(text: str, out_path: str, language: str, label: str, budget: BudgetTracker,
                  disfluency_qa: bool = False) -> dict:
    reused = _resumable_reuse(out_path)
    if reused is not None:
        return reused
    budget.check_before(TTS_CALL_EST_JPY, label)
    expected_substring = text[:20]
    r = repro01.generate_narration_snippet_verified_strict(
        text, language, out_path, expected_substring, disfluency_qa=disfluency_qa)
    budget.add(label, "tts", 1, TTS_CALL_EST_JPY, {"status": r.get("status"), "language": language})
    _mark_ok_if_success(r, out_path)
    return r


def tts_twin(text: str, out_path: str, label: str, budget: BudgetTracker) -> dict:
    """デジタルツインEcho voice(Erinome)。既存Production関数
    bvoices.generate_voice_body_wide_margin()をそのまま呼ぶ(Trial-10と
    同一実装、本タスクでは未使用[Story音声はTrial-10からreuse]だが、
    将来の再実行[本タスクの前提が崩れた場合]のために関数として保持する)。"""
    reused = _resumable_reuse(out_path)
    if reused is not None:
        return reused
    budget.check_before(TTS_CALL_EST_JPY, label)
    r = bvoices.generate_voice_body_wide_margin(text, out_path, TWIN_VOICE_NAME)
    budget.add(label, "tts", 1, TTS_CALL_EST_JPY, {"status": r.get("status")})
    _mark_ok_if_success(r, out_path)
    return r


def asr_diag(out_path: str, language: str, budget: BudgetTracker, label: str) -> str | None:
    budget.check_before(ASR_DIAG_CALL_EST_JPY, label)
    asr_lang = "en-US" if language == "en" else "ja-JP"
    text, err = asr_routing.transcribe(out_path, asr_lang)
    budget.add(label, "asr_diag", 1, ASR_DIAG_CALL_EST_JPY, {"error": err})
    return text


def load_mono(path: str) -> np.ndarray:
    mono, sr, _, _ = common.read_wav_float(path)
    assert sr == MONO_SR, f"unexpected sample rate: {sr}"
    return mono


def sha256_text_file(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _normalize_loose(text: str | None) -> str:
    if text is None:
        return ""
    t = text.lower()
    t = re.sub(r"[^\w\s]", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def _to_audit_entry(r: dict, canonical_text: str) -> dict:
    status = r.get("status")
    if status == "REUSED_EXISTING_FILE" or r.get("reused_shared_asset"):
        return {"status": "OK", "path": r.get("path"), "sha256": r.get("sha256"),
                "canonical_text": canonical_text, "disfluency_checked": True, "reused": True,
                "asr_text": None}
    return {
        "status": status,
        "path": r.get("path"), "sha256": r.get("sha256"),
        "canonical_text": canonical_text,
        "disfluency_checked": bool(r.get("disfluency_checked", False)),
        "asr_text": r.get("asr_text"),
    }


# ============================================================
# main
# ============================================================
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--budget-jpy", type=float, default=45.0)
    parser.add_argument("--plan-only", action="store_true",
                         help="TTSなし。segmentation_plan.jsonのみ生成し語数分布を表示して終了する。")
    args = parser.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)

    article_text = load_article_text()
    paragraphs = split_into_paragraphs(article_text)
    assert len(paragraphs) == 33, f"unexpected paragraph count: {len(paragraphs)}"

    story_segments = build_all_story_segments_trial12_twins(paragraphs)
    reconstructed = reconstruct_article_from_story_segments(story_segments, len(paragraphs))
    assert reconstructed == article_text, "STORY_SEGMENT reconstruction mismatch(生成前チェック)"

    # --- 旧segmentation(Trial-10)との一致確認 ---
    # 本タスクの分析により、新segmentationは旧22 segmentと完全一致することが
    # 判明している(ファイル冒頭コメント参照)。一致しない場合はTrial-10音声を
    # 誤って再利用することになるため、ここで必ず検証しSTOPする。
    with open(f"{PREV_OUT_DIR}/segments.json", encoding="utf-8") as f:
        prev_segments = json.load(f)
    new_key = [(s["voice"], s["tts_text"]) for s in story_segments]
    prev_key = [(s["voice"], s["tts_text"]) for s in prev_segments]
    segments_identical_to_prev = (new_key == prev_key)
    if not segments_identical_to_prev:
        raise RuntimeError(
            "SEGMENTATION_CHANGED_FROM_TRIAL10: 新segmentationが旧Trial-10と異なります。"
            "本スクリプトはStory音声をTrial-10からreuseする前提で書かれているため、"
            "この場合はSTORY TTSの新規実行方針を人間へ確認してください"
            "(STOP条件: 今回承認されていない新仕様が必要)。")

    plan_rows = build_segmentation_plan_report(story_segments)
    with open(f"{OUT_DIR}/segmentation_plan.json", "w", encoding="utf-8") as f:
        json.dump({
            "policy": ("Trial安全ガイド[概ね100語以内、120語を大きく超えない、150-200語級を"
                       "作らない]。正式Production hard capではない。分割理由=話者Voice変化/"
                       "Comment挿入位置/scene・semantic boundaryのみ。"),
            "segment_count": len(plan_rows),
            "min_word_count": min(r["word_count"] for r in plan_rows),
            "max_word_count": max(r["word_count"] for r in plan_rows),
            "comment_2_after_segment_id": COMMENT_2_AFTER_SEGMENT_ID,
            "comment_3_after_segment_id": COMMENT_3_AFTER_SEGMENT_ID,
            "segments_identical_to_trial10": segments_identical_to_prev,
            "note": ("新segmentationが旧Trial-10 STORY_SEGMENT_PLANと完全一致したため、"
                     "Story音声はTrial-10からbyte-identicalにreuseする(re-TTSなし)。"
                     "新規TTS対象はComment 1〜3のみ。"),
            "segments": plan_rows,
        }, f, ensure_ascii=False, indent=2)

    print(f"[PLAN] segment_count={len(plan_rows)} "
          f"min_word_count={min(r['word_count'] for r in plan_rows)} "
          f"max_word_count={max(r['word_count'] for r in plan_rows)} "
          f"identical_to_trial10={segments_identical_to_prev}")
    for r in plan_rows:
        print(f"  {r['id']:10s} voice={r['voice']:9s} words={r['word_count']:3d} "
              f"paragraphs={r['paragraph_range']}")

    if args.plan_only:
        print("[PLAN-ONLY] TTSは実行せずここで終了します。")
        return

    os.makedirs(AUDIO_DIR, exist_ok=True)
    os.makedirs(ASSEMBLED_DIR, exist_ok=True)
    os.makedirs(KEY_PHRASE_DIR, exist_ok=True)
    os.makedirs(AUDIT_DIR, exist_ok=True)

    cl.install(f"{AUDIT_DIR}/er005_cost_log.jsonl")
    budget = BudgetTracker(args.budget_jpy, 35.0, f"{OUT_DIR}/raw_usage_log.jsonl")

    # --- 本文固定確認(sha256記録) ---
    normalized = normalize_for_tts(article_text)
    with open(f"{OUT_DIR}/article_normalized.txt", "w", encoding="utf-8") as f:
        f.write(normalized)
    src_sha = sha256_text_file(ARTICLE_PATH)
    with open(f"{AUDIT_DIR}/article_fixed_sha256.json", "w", encoding="utf-8") as f:
        json.dump({"source_article_sha256": src_sha, "source_path": ARTICLE_PATH,
                   "policy": "Trial-08正本固定、再生成・書き換えなし(ユーザー指示2026-09-16)"},
                   f, ensure_ascii=False, indent=2)

    audit_segments: dict = {}
    audit_key_phrases: dict = {}
    gain_report: dict = {}
    consistency_rows: list = []

    client = a2gen.get_client()

    # === Stage A: SFX/Nav資産の読み込み + Trial-10既存asset reuse ===
    intro_mp3 = p9a.load_and_resample_to_target(INTRO_MP3_PATH)
    outro_mp3 = p9a.load_and_resample_to_target(OUTRO_MP3_PATH)
    notification_mp3 = p9a.load_and_resample_to_target(NOTIFICATION_MP3_PATH)
    nav = copy_shared_charon_nav(AUDIO_DIR)

    for rel in ("audio/topic_intro_en.wav", "audio/topic_intro_en.wav.ok",
                "audio/japanese_title.wav", "audio/japanese_title.wav.ok",
                "preview.txt", "key_phrases"):
        copy_from_prev_if_missing(rel)
    for rank in (1, 2, 3, 4, 5):
        reuse_shared_number_word(rank, f"{AUDIO_DIR}/kp{rank}_number.wav")
        for kind in ("english", "japanese"):
            copy_from_prev_if_missing(f"audio/kp{rank}_{kind}.wav")
            copy_from_prev_if_missing(f"audio/kp{rank}_{kind}.wav.ok")
    with open(f"{PREV_OUT_DIR}/key_phrase_consistency.json", encoding="utf-8") as f:
        kp_consistency_prev = json.load(f)
    with open(f"{OUT_DIR}/key_phrase_consistency.json", "w", encoding="utf-8") as f:
        json.dump(kp_consistency_prev, f, ensure_ascii=False, indent=2)

    with open(f"{KEY_PHRASE_DIR}/keywords_canonicalized.json", encoding="utf-8") as f:
        kp_items = sorted(json.load(f)["items"], key=lambda it: it["rank"])

    with open(f"{PREV_OUT_DIR}/audit/tts_generation_results.json", encoding="utf-8") as f:
        prev_tts_results = json.load(f)

    # === Stage B: Topic intro(EN) + Japanese title(JA) — Trial-10からreuse ===
    audit_segments["topic_intro_en"] = prev_tts_results["segments"]["topic_intro_en"]
    audit_segments["japanese_title"] = prev_tts_results["segments"]["japanese_title"]

    # === Stage C: Preview(日本語) — Trial-10からreuse(既にコピー済み、内容不変) ===
    with open(f"{OUT_DIR}/preview.txt", encoding="utf-8") as f:
        preview_text = f.read().strip()
    audit_segments["preview_ja"] = prev_tts_results["segments"]["preview_ja"]
    preview_wav_path = f"{PREV_OUT_DIR}/audio/preview_ja.wav"
    copy_from_prev_if_missing("audio/preview_ja.wav")
    copy_from_prev_if_missing("audio/preview_ja.wav.ok")
    preview_wav_path = f"{AUDIO_DIR}/preview_ja.wav"

    # === Stage D: Key Phrase — Trial-10からreuse(既にコピー済み) ===
    audit_key_phrases = prev_tts_results["key_phrases"]
    kp_blocks_stereo = []
    for item in kp_items:
        rank = item["rank"]
        kp_blocks_stereo.append((rank, f"{AUDIO_DIR}/kp{rank}_number.wav",
                                  f"{AUDIO_DIR}/kp{rank}_english.wav",
                                  f"{AUDIO_DIR}/kp{rank}_japanese.wav"))

    # === Stage E: Story segment音声 — segmentation一致確認済みにつきTrial-10から
    #     byte-identicalにreuse(re-TTSなし、Comment以外の新規TTSはこの記事に
    #     存在しない)。===
    for seg in story_segments:
        copy_story_audio_from_prev(seg["id"])
        out_path = f"{AUDIO_DIR}/{seg['id']}.wav"
        prev_entry = prev_tts_results["segments"][seg["id"]]
        entry = dict(prev_entry)
        entry["path"] = out_path
        audit_segments[seg["id"]] = entry
        seg["audio_path"] = out_path

    with open(f"{OUT_DIR}/segments.json", "w", encoding="utf-8") as f:
        json.dump([{k: v for k, v in s.items() if k != "paragraph_contributions"}
                   for s in story_segments], f, ensure_ascii=False, indent=2)

    # === Stage F: Comment 1〜3(日本語、Trial-12新規LLM+TTS。Comment 4は使用しない) ===
    comments_md_path = f"{OUT_DIR}/comments_ja.md"
    comment_texts = {}
    if os.path.exists(comments_md_path):
        with open(comments_md_path, encoding="utf-8") as f:
            existing_md_text = f.read()
        for n in COMMENT_NUMBERS:
            marker = f"## Comment {n}\n\n"
            after = existing_md_text.split(marker, 1)[1]
            comment_texts[n] = after.split("\n\n", 1)[0].strip()
    else:
        for n in COMMENT_NUMBERS:
            comment_texts[n] = run_ja_comment_text(client, n, article_text, budget)
        with open(comments_md_path, "w", encoding="utf-8") as f:
            for n in COMMENT_NUMBERS:
                f.write(f"## Comment {n}\n\n{comment_texts[n]}\n\n")

    comment_wavs = {}
    for n in COMMENT_NUMBERS:
        txt = comment_texts[n]
        path = f"{AUDIO_DIR}/comment_{n}_ja.wav"
        r = tts_narrator(txt, path, "ja", f"comment_{n}_ja", budget)
        audit_segments[f"comment_{n}_ja"] = _to_audit_entry(r, txt)
        comment_wavs[n] = (path, r)

    # === Stage G: speaker_map.json(話者判定表、Trial-10と同一の固定判定を継承) ===
    speaker_map = []
    for seg in story_segments:
        if seg["kind"] == "split" and seg["voice"] == "twin":
            speaker_map.append({"segment_id": seg["id"], "voice": seg["voice"],
                                 "source_paragraph_indices": seg["source_paragraph_indices"],
                                 "quote_text": seg["raw_text"],
                                 "attribution_basis": ("固定段落indices(TWIN_QUOTE_PARAGRAPH_INDICES/"
                                                        "TWIN_DISPLAY_PARAGRAPH_INDICES、Trial-10と同一、"
                                                        "変更なし)")})
    with open(f"{OUT_DIR}/speaker_map.json", "w", encoding="utf-8") as f:
        json.dump({
            "narrator_voice": "Aoede", "twin_voice": TWIN_VOICE_NAME,
            "mara_split_decision": "Mara本人の台詞はnarrator(Aoede)のまま分離しない(Trial-10から無変更)。",
            "entries": speaker_map,
        }, f, ensure_ascii=False, indent=2)

    # === Stage H: gain + timeline構築(Trial-10 twins_a2構成をそのまま踏襲) ===
    def gs(mono: np.ndarray, label: str) -> np.ndarray:
        gain = p9a.compute_gain_for_target_rms(mono, target_rms)
        gained = mono * gain
        gain_report[label] = {"gain": round(float(gain), 4), "rms_before": round(p9a.rms(mono), 5),
                               "rms_after": round(p9a.rms(gained), 5), "peak_after": round(p9a.peak(gained), 5)}
        return p9a.mono_24k_to_stereo_target(gained)

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
    seq.append(("Topic intro", gs(load_mono(f"{AUDIO_DIR}/topic_intro_en.wav"), "topic_intro_en")))
    sil(0.65)
    seq.append(("Japanese title", gs(load_mono(f"{AUDIO_DIR}/japanese_title.wav"), "japanese_title")))
    sil(0.5)
    seq.append(("Notification 1", notification_gained))
    sil(0.4)
    seq.append(("Preview intro (Charon)", gs(load_mono(f"{AUDIO_DIR}/preview_intro.wav"), "preview_intro")))
    sil(0.65)
    seq.append(("Preview", gs(preview_mono, "preview_ja")))
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

    c1_path, c1_r = comment_wavs[1]
    seq.append(("Comment 1", gs(load_mono(c1_path), "comment_1")))
    sil(0.8)

    for seg in story_segments:
        seq.append((seg["id"], gs(load_mono(seg["audio_path"]), seg["id"])))
        sil(0.2 if seg["kind"] == "split" else 0.5)
        if seg["id"] == COMMENT_2_AFTER_SEGMENT_ID:
            sil(1.0)
            c2_path, c2_r = comment_wavs[2]
            seq.append(("Comment 2", gs(load_mono(c2_path), "comment_2")))
            sil(0.8)
        if seg["id"] == COMMENT_3_AFTER_SEGMENT_ID:
            sil(1.0)
            c3_path, c3_r = comment_wavs[3]
            seq.append(("Comment 3", gs(load_mono(c3_path), "comment_3")))
            sil(0.8)

    sil(0.5)
    seq.append(("Outro", outro_gained))

    with open(f"{AUDIT_DIR}/gain_report.json", "w", encoding="utf-8") as f:
        json.dump(gain_report, f, ensure_ascii=False, indent=2)

    assembled_result = assemble_mod.assemble_with_timeline(seq)
    safety_result = assemble_mod.apply_headroom_safety_valve(assembled_result["assembled"], seq)
    with open(f"{AUDIT_DIR}/headroom_report.json", "w", encoding="utf-8") as f:
        json.dump(safety_result["report"], f, ensure_ascii=False, indent=2)

    final_path = f"{ASSEMBLED_DIR}/family_c_twins_trial_12.wav"
    common.write_wav_float(final_path, safety_result["assembled"], SR, 2)

    run_summary = {
        "duration_seconds": assembled_result["total_duration_seconds"],
        "peak_before_headroom": safety_result["report"]["peak_before"],
        "peak_after_headroom": safety_result["report"]["peak_after"],
        "headroom_applied": safety_result["report"]["applied"],
        "timeline": assembled_result["timeline"],
    }
    with open(f"{AUDIT_DIR}/run_summary_assemble.json", "w", encoding="utf-8") as f:
        json.dump(run_summary, f, ensure_ascii=False, indent=2)

    # === Stage I: tts_generation_results.json(Gate入力) + Audio Validation Gate ===
    tts_results = {"segments": audit_segments, "key_phrases": audit_key_phrases}
    with open(f"{AUDIT_DIR}/tts_generation_results.json", "w", encoding="utf-8") as f:
        json.dump(tts_results, f, ensure_ascii=False, indent=2)

    gate_error = None
    try:
        assemble_mod.verify_episode_audio_validation_gate(OUT_DIR, LEVEL)
        gate_status = "PASS"
    except RuntimeError as e:
        gate_status = "BLOCKED"
        gate_error = str(e)
    with open(f"{OUT_DIR}/audio_validation.json", "w", encoding="utf-8") as f:
        json.dump({"status": gate_status, "level": LEVEL, "error": gate_error}, f,
                   ensure_ascii=False, indent=2)
    if gate_status != "PASS":
        print(f"[AUDIO VALIDATION GATE] BLOCKED: {gate_error}")

    # === Stage J: article/audio consistency ===
    story_concat_canonical = " ".join(s["tts_text"] for s in story_segments)
    with open(f"{OUT_DIR}/article_audio_consistency.json", "w", encoding="utf-8") as f:
        json.dump({
            "method": ("Story本文全体(article_normalized.txt)と、story segment群の"
                       "tts_text連結が、読み整形分(引用符正規化・空白圧縮)を除いて"
                       "一致することを確認する。"),
            "story_segment_concat_tts_text": story_concat_canonical,
            "article_normalized_text": normalized,
        }, f, ensure_ascii=False, indent=2)

    # === Stage K: player/display/audio consistency ===
    # Story segment分はTrial-10からreuse(音声byte-identicalのためASR再実行不要)。
    with open(f"{PREV_OUT_DIR}/player_display_audio_consistency.json", encoding="utf-8") as f:
        prev_consistency_rows = json.load(f)
    story_ids = {s["id"] for s in story_segments}
    consistency_rows = [r for r in prev_consistency_rows if r["segment_id"] in story_ids
                         or r["voice"] == "nav/fixed"]
    # Comment行は新規(旧Commentの行を除外し、下で新Comment分を追加)。
    consistency_rows = [r for r in consistency_rows if not r["segment_id"].startswith("comment_")]

    fixed_checks = []
    for n in COMMENT_NUMBERS:
        fixed_checks.append((f"comment_{n}_ja", comment_texts[n], "ja",
                              audit_segments[f"comment_{n}_ja"].get("asr_text")))
    for name, text, lang, precomputed in fixed_checks:
        asr_text = precomputed
        if asr_text is None:
            path = f"{AUDIO_DIR}/{name}.wav"
            asr_text = asr_diag(path, lang, budget, f"{name}_asr_diag")
        consistency_rows.append({
            "segment_id": name, "voice": "nav/fixed",
            "player_display_text": text, "canonical_text": text, "tts_input_text": text,
            "asr_text": asr_text, "match": _normalize_loose(asr_text) == _normalize_loose(text),
        })

    with open(f"{OUT_DIR}/player_display_audio_consistency.json", "w", encoding="utf-8") as f:
        json.dump(consistency_rows, f, ensure_ascii=False, indent=2)

    # === Stage L: Comment consistency ===
    comment_consistency = []
    for n in COMMENT_NUMBERS:
        path, r = comment_wavs[n]
        asr_text = r.get("asr_text") or asr_diag(path, "ja", budget, f"comment_{n}_reconfirm_asr")
        comment_consistency.append({
            "comment": n, "player_display_text": comment_texts[n], "canonical_text": comment_texts[n],
            "tts_input_text": comment_texts[n], "asr_text": asr_text,
            "match": _normalize_loose(asr_text) == _normalize_loose(comment_texts[n]),
        })
    with open(f"{OUT_DIR}/comment_consistency.json", "w", encoding="utf-8") as f:
        json.dump(comment_consistency, f, ensure_ascii=False, indent=2)

    # === Stage M: comment_placement.json ===
    def _wav_duration(path: str) -> float:
        mono, sr, _, _ = common.read_wav_float(path)
        return round(len(mono) / sr, 3)

    seg_by_id_all = {s["id"]: s for s in story_segments}
    ids_in_order = [s["id"] for s in story_segments]
    placement = [
        {"comment": 1, "position_description": "導入部(Preview後・Story前、Full story introの直後)",
         "before_segment_id": None, "after_segment_id": story_segments[0]["id"],
         "before_segment_word_count": None,
         "after_segment_word_count": len(story_segments[0]["tts_text"].split()),
         "comment_duration_seconds": _wav_duration(comment_wavs[1][0]),
         "comment_word_count_ja_chars": len(comment_texts[1])},
    ]
    for n, seg_id, desc in ((2, COMMENT_2_AFTER_SEGMENT_ID,
                              "段落13直後(私的な会話からオーディション会場前への場面転換、Trial-10と同一の意味的位置)"),
                             (3, COMMENT_3_AFTER_SEGMENT_ID,
                              "段落22直後('The door opened.'の直後、決断場面の手前。Trial-10と同一の意味的位置)")):
        idx = ids_in_order.index(seg_id)
        after_id = ids_in_order[idx + 1] if idx + 1 < len(ids_in_order) else None
        placement.append({
            "comment": n, "position_description": desc,
            "before_segment_id": seg_id, "after_segment_id": after_id,
            "before_segment_word_count": len(seg_by_id_all[seg_id]["tts_text"].split()),
            "after_segment_word_count": (len(seg_by_id_all[after_id]["tts_text"].split())
                                          if after_id else None),
            "comment_duration_seconds": _wav_duration(comment_wavs[n][0]),
            "comment_word_count_ja_chars": len(comment_texts[n]),
        })
    with open(f"{OUT_DIR}/comment_placement.json", "w", encoding="utf-8") as f:
        json.dump(placement, f, ensure_ascii=False, indent=2)

    # === Stage N: family_a_reuse_map.md ===
    write_family_a_reuse_map()

    # === Stage O: mp3化 + player再生成 ===
    web_result = convert_all_to_mp3()
    build_player_html(seq_labels=[name for name, _ in seq], story_segments=story_segments,
                       kp_items=kp_items, comment_texts=comment_texts, run_summary=run_summary)

    # === Stage P: cost_summary.json ===
    all_records = []
    if os.path.exists(f"{OUT_DIR}/raw_usage_log.jsonl"):
        with open(f"{OUT_DIR}/raw_usage_log.jsonl", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    all_records.append(json.loads(line))
    total_jpy = sum(r["jpy_estimate"] for r in all_records)
    tts_count = sum(r["count"] for r in all_records if r["kind"] == "tts")
    llm_count = sum(r["count"] for r in all_records if r["kind"] == "llm")
    asr_diag_count = sum(r["count"] for r in all_records if r["kind"] == "asr_diag")
    cost_summary = {
        "budget_cap_jpy": args.budget_jpy, "warn_threshold_jpy": 35.0,
        "total_estimate_jpy": round(total_jpy, 2),
        "note": ("Story segment(22件)は新旧segmentation完全一致のためTrial-10からbyte-identical"
                 "reuse(re-TTS・re-ASRなし)。新規費用はComment 1〜3のLLM/TTS/ASRのみ。"),
        "tts_call_count_estimate_basis": tts_count, "llm_call_count_estimate_basis": llm_count,
        "asr_diag_call_count_estimate_basis": asr_diag_count,
        "gate_status": gate_status,
    }
    with open(f"{OUT_DIR}/cost_summary.json", "w", encoding="utf-8") as f:
        json.dump(cost_summary, f, ensure_ascii=False, indent=2)

    print(f"[DONE] duration={run_summary['duration_seconds']}s gate={gate_status} "
          f"cost_estimate=Y{total_jpy:.2f}")


def write_family_a_reuse_map() -> None:
    rows = [
        ("Intro/Outro/Notification(SFXジングル)", "p9a.INTRO/OUTRO/NOTIFICATION_MP3_PATH", "そのまま流用"),
        ("Welcome/Preview intro/Key phrases intro/Full story intro(Charon)",
         "B1_SHARED_NAMES(共有ソース)", "そのまま流用"),
        ("番号読み上げ(One.〜Five.)", "B1_SHARED_NAMES num_X_charon.wav", "そのまま流用"),
        ("Topic intro(EN)/Japanese title/Preview(JA)/Key Phrase英語・日本語音声",
         "Trial-10 twins_a2/audio(コピー、再TTSなし)", "本文・テキスト不変のため再生成不要"),
        ("Story segment(22件、narrator/twin)", "Trial-10 twins_a2/audio(byte-identicalコピー、再TTSなし)",
         "新旧segmentation完全一致のためreuse(本タスクの主要な発見、RESULT_PACKET参照)"),
        ("Key Phrase選定・canonicalization", "Trial-10 twins_a2/key_phrases(コピー)", "再選定なし"),
        ("Comment 1〜3(日本語)", "新規生成(Trial-12 Comment Prompt、英文理解ガイド役割)",
         "本タスクの唯一の新規TTS対象"),
        ("Assembly/Gate/player", "assemble_with_timeline/apply_headroom_safety_valve/"
         "verify_episode_audio_validation_gate/audio_review_player.py", "そのまま流用(無変更)"),
        ("Voice(narrator=Aoede、digital twin Echo=Erinome)", "er012_b_family_voices_production_01",
         "Trial-10から無変更"),
    ]
    lines = ["# Family A流用表(Digital Twins A2、Trial-12)\n", "| 項目 | 流用元 | 扱い |", "|---|---|---|"]
    for a, b, c in rows:
        lines.append(f"| {a} | {b} | {c} |")
    lines.append("\n新規Family C専用演出・新規SFXは追加していない(禁止事項どおり)。")
    with open(f"{OUT_DIR}/family_a_reuse_map.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def convert_all_to_mp3() -> dict:
    import soundfile as sf

    os.makedirs(WEB_DIR, exist_ok=True)
    os.makedirs(WEB_SEG_DIR, exist_ok=True)

    def convert_one(wav_path: str, mp3_path: str) -> dict:
        data, sr = sf.read(wav_path)
        sf.write(mp3_path, data, sr, format="MP3")
        return {"wav_path": wav_path, "mp3_path": mp3_path,
                "wav_bytes": os.path.getsize(wav_path), "mp3_bytes": os.path.getsize(mp3_path)}

    results = []
    ep_wav = f"{ASSEMBLED_DIR}/family_c_twins_trial_12.wav"
    ep_mp3 = f"{WEB_DIR}/family_c_twins_trial_12.mp3"
    results.append({"kind": "episode", **convert_one(ep_wav, ep_mp3)})

    wav_names = sorted(n for n in os.listdir(AUDIO_DIR) if n.endswith(".wav"))
    for name in wav_names:
        stem = name[:-4]
        results.append({"kind": "segment", "segment_id": stem,
                         **convert_one(f"{AUDIO_DIR}/{name}", f"{WEB_SEG_DIR}/{stem}.mp3")})

    web_result = {"episode_mp3": ep_mp3, "segment_count": len(wav_names), "conversions": results}
    with open(f"{OUT_DIR}/web_delivery.json", "w", encoding="utf-8") as f:
        json.dump(web_result, f, ensure_ascii=False, indent=2)
    return web_result


def build_player_html(seq_labels, story_segments, kp_items, comment_texts, run_summary) -> None:
    rows = []
    seg_by_id = {s["id"]: s for s in story_segments}
    kp_by_rank = {it["rank"]: it for it in kp_items}
    fixed_label_to_text = {
        "Intro": None, "Outro": None,
        "Welcome (Charon)": (SHARED_CHARON_NAV["welcome"][1], "Charon(nav)"),
        "Topic intro": (TOPIC_INTRO_EN_TEXT, "Aoede(narrator)"),
        "Japanese title": (JAPANESE_TITLE_TEXT, "Aoede(narrator)"),
        "Preview intro (Charon)": (SHARED_CHARON_NAV["preview_intro"][1], "Charon(nav)"),
        "Key phrases intro (Charon)": (SHARED_CHARON_NAV["key_phrases_intro"][1], "Charon(nav)"),
        "Full story intro (Charon)": (SHARED_CHARON_NAV["full_story_intro"][1], "Charon(nav)"),
        "Notification 1": ("(SFX、通知音)", "SFX"), "Notification 2": ("(SFX、通知音)", "SFX"),
        "Notification 3": ("(SFX、通知音)", "SFX"),
    }
    for _n, _txt in comment_texts.items():
        fixed_label_to_text[f"Comment {_n}"] = (_txt, "Aoede(narrator)")
    name_to_seg_id = {
        "Welcome (Charon)": "welcome", "Topic intro": "topic_intro_en", "Japanese title": "japanese_title",
        "Preview intro (Charon)": "preview_intro", "Preview": "preview_ja",
        "Key phrases intro (Charon)": "key_phrases_intro", "Full story intro (Charon)": "full_story_intro",
    }
    for _n in comment_texts:
        name_to_seg_id[f"Comment {_n}"] = f"comment_{_n}_ja"

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
            with open(f"{OUT_DIR}/preview.txt", encoding="utf-8") as f:
                ptext = f.read()
            audio_html = player_mod.render_single_audio_html("./web/segments/preview_ja.mp3")
            rows.append(player_mod.render_timeline_row(start, name, "Aoede(narrator)", ptext, audio_html))
            continue
        if name in fixed_label_to_text:
            text, voice_disp = fixed_label_to_text[name]
            seg_id = name_to_seg_id.get(name, name)
            audio_html = player_mod.render_single_audio_html(f"./web/segments/{seg_id}.mp3")
            rows.append(player_mod.render_timeline_row(start, name, voice_disp, text, audio_html))
            continue
        seg = seg_by_id.get(name)
        if seg is not None:
            voice_disp = {"narrator": "Aoede(narrator)", "twin": f"{TWIN_VOICE_NAME}(digital twin Echo)"}[seg["voice"]]
            audio_html = player_mod.render_single_audio_html(f"./web/segments/{seg['id']}.mp3")
            rows.append(player_mod.render_timeline_row(start, name, voice_disp, seg["tts_text"], audio_html))

    table_html = player_mod.render_timeline_table(rows)
    episode_url = "./web/family_c_twins_trial_12.mp3"
    html = f"""<!doctype html><html><head><meta charset="utf-8">
<title>Family C Trial-12: Digital Twins(A2、segmentation展開+Comment理解ガイド化)</title>
<style>{player_mod.PLAYER_STANDARD_CSS}</style>
<script>{player_mod.SEEK_SCRIPT}</script>
</head><body>
<h1>Family C Future — Digital Twins(Trial-12 A2 / VALIDATED候補・USER_LISTENING_PENDING、
Production未採用)</h1>
<p>duration={run_summary['duration_seconds']}s / peak={run_summary['peak_after_headroom']}</p>
<p>Trial-12変更点: Comment 1〜3を英文理解ガイドへ変更(Story segmentationは
Trial-10と完全一致のためStory音声はbyte-identical reuse)。旧版は
<a href="../../family_c_episode_trial_10/twins_a2/player.html">Trial-10 player</a>参照。</p>
<audio id="episode_audio" class="main" controls preload="none" src="{episode_url}"></audio>
{table_html}
</body></html>"""
    with open(f"{OUT_DIR}/player.html", "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    main()
