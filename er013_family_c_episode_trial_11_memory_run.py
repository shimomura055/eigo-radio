# ============================================================
# er013_family_c_episode_trial_11_memory_run.py
# 管理ID: FAMILY-C-MEMORY-A2-SEGMENT-COMMENT-TRIAL-11
# ============================================================
# 目的: Family C「The future of memory」A2(er013_family_c_episode_trial_10_
# memory_run.pyで完成済み・USER-TEST-FINAL-AUDIO-BATCH-06)に対するユーザー
# 試聴フィードバックを踏まえた**仕様変更Trial**(ユーザー承認済み、2026-09-16)。
# 目的2点: (1) Story TTS segmentの細切れによる音色・tone・声の強さの不連続を
# 減らす(segmentation見直し)、(2) A2 Commentをメタナレーション(「聞いて
# みましょう」型)から英文理解ガイドへ変更(Comment Prompt Trial版)。加えて
# 兄の台詞Voiceを、既存承認Voice候補の中から明確に男性的に聞こえるものへ
# 変更する。
#
# 本ファイルはTrial-10 memory版(er013_family_c_episode_trial_10_memory_
# run.py)を複製したもの(Trial-10成果物は一切上書き・編集しない、旧OUT_DIR
# はそのまま保存)。本文(reader_facing_article.txt)は無変更・Writer再実行
# なし。Preview/Key Phraseは既存正常assetをTrial-10からコピーして再利用し、
# 再TTSしない(再TTS対象はStory segment全件+Comment 1〜3のみ)。
#
# 変更点サマリ:
#   - Story segmentation: 段落インデックス1:1のSTORY_SEGMENT_PLANを廃止し、
#     build_all_story_segments_trial11()で「Voice変化点/Comment挿入位置/
#     scene・semantic boundary」のみを分割理由とする新設計(14→10 segment、
#     詳細は本ファイル内コメントおよびsegmentation_plan.json参照)。
#   - Comment Prompt: COMMENT_*_ROLE_JA_TRIAL11を新設(英文理解ガイド役割、
#     メタナレーション禁止語句を明記)。旧COMMENT_*_ROLE_JAは
#     COMMENT_*_ROLE_JA_TRIAL10_PREVとして残置(比較用、未使用)。
#   - Brother Voice: BROTHER_VOICE_NAME = "Erinome" → "Algieba"
#     (既存承認Voice候補6種[Algieba/Erinome/Schedar/Sulafat/Aoede/Charon]の
#     うち、音響的ピッチ推定[自己相関法、既存sample wav使用、追加TTSなし]で
#     Algiebaが最低median F0[111.9Hz、Charon133.3Hz/Schedar137.9Hzより低い]
#     であり、既存候補中もっとも男性的に聞こえる可能性が高いため選定。詳細は
#     RESULT_PACKET参照。装置Voice[Charon]との衝突なし[Algiebaは本記事で
#     未使用だったため]、変更不要)。
#
# 実行方法:
#   .venv/Scripts/python.exe er013_family_c_episode_trial_11_memory_run.py \
#       --plan-only                     # segmentation_plan.jsonのみ生成(TTSなし)
#   .venv/Scripts/python.exe er013_family_c_episode_trial_11_memory_run.py \
#       --budget-jpy 50
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import time

os.environ.setdefault("TTS_EXECUTION_MODE", "STANDARD")

import numpy as np

import er002_common as common
import er003_b1_p9a_audio as p9a
import er003_v1_iran01_a2_generate as a2gen
import er003_v1_n3_01_assemble as assemble_mod
import er003_v1_n3_01_scaffold_generate as scaffold
import er003_v1_repro01_main_generate as repro01
import er003_v1_sing01_voice01_generate as voice01
import er005_cost_logger as cl
import er006_asr_provider_routing_01 as asr_routing
import er012_b_family_voices_production_01 as bvoices

import audio_review_player as player_mod

# ============================================================
# パス定数
# ============================================================
ARTICLE_PATH = "er013_output/family_c_future_trial_08/memory/reader_facing_article.txt"
PREV_OUT_DIR = "er013_output/family_c_episode_trial_10/memory_a2"  # 旧版(参照のみ、無編集)
OUT_DIR = "er013_output/family_c_episode_trial_11/memory_a2"
AUDIO_DIR = f"{OUT_DIR}/audio"
ASSEMBLED_DIR = f"{OUT_DIR}/assembled"
KEY_PHRASE_DIR = f"{OUT_DIR}/key_phrases"
AUDIT_DIR = f"{OUT_DIR}/audit"
WEB_DIR = f"{OUT_DIR}/web"
WEB_SEG_DIR = f"{WEB_DIR}/segments"

SR = p9a.TARGET_SAMPLE_RATE  # 48000
MONO_SR = common.SAMPLE_RATE  # 24000

ARTICLE_ID = "family_c_memory_trial_11"
LEVEL = "FAMILY_C_TRIAL_11_MEMORY_A2"  # Trial-10と同一方式の新規level文字列
                                        # (既存level辞書には存在せず、Audio
                                        # Validation Gateの既存required_
                                        # structure/disfluency辞書は無変更)。

TOPIC_TITLE = "The Future of Memory"
TOPIC_INTRO_EN_TEXT = f"Today's topic is {TOPIC_TITLE}."
JAPANESE_TITLE_TEXT = "記憶の未来"  # Trial-10と同一(直訳1件、既登録)

# B1_SHARED(記事非依存Charon資産、er003_v1_n3_01_assemble.py::B1_SHARED_NAMES
# と同一ファイル、追加TTS不要)。
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

# Family A SFXジングル(ローカル絶対パス、既存Production定数をそのまま参照)。
INTRO_MP3_PATH = p9a.INTRO_MP3_PATH
OUTRO_MP3_PATH = p9a.OUTRO_MP3_PATH
NOTIFICATION_MP3_PATH = p9a.NOTIFICATION_MP3_PATH

BROTHER_VOICE_NAME = "Algieba"  # Trial-11変更点: 旧Erinome(median F0約221Hz、
                                 # 女性域)→Algieba(median F0約112Hz、既存承認
                                 # 候補6種中最も低く男性域に近い、装置Charon
                                 # [約133Hz]より低い)。既存承認Voice候補内、
                                 # 新規Voice探索なし。装置Voice(Charon)との
                                 # 衝突なし(Algiebaは本記事で未使用だった)。

# 既存承認Voice候補(CURRENT_SPEC.md記載、6種)の参考記録(選定根拠)。
APPROVED_VOICE_CANDIDATES_PITCH_ESTIMATE_HZ = {
    # median F0(自己相関法、既存sample wav使用、追加TTS費用ゼロ)。
    # 出典sample: Algieba/Erinome/Schedar/Sulafat/Aoede=
    # er012_output/editorial_b_voices_trial_09_audio(旧voice_samples_review.htmlの
    # 5voice)、Charon=既存preview_charon.wav(19.45秒)。
    "Algieba": 111.9, "Charon": 133.3, "Schedar": 137.9,
    "Aoede": 190.5, "Sulafat": 216.2, "Erinome": 221.2,
}

# ============================================================
# 予算管理(Trial-10と同一方式、¥50ハード上限、¥40で警告)
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
#    段落0-indexedで29段落。装置(screen)の直接発話2箇所[2,4]をCharon、
#    兄の直接発話1箇所[14]をAlgiebaへ分離する。Lena本人の台詞(段落5,19)は
#    narrator(Aoede)のまま分離しない(Trial-10から無変更の方針)。
#
#    Trial-11のsegmentation方針(ユーザー指示2026-09-16):
#    「できるだけ自然な連続発話としてまとめ、必要な理由がある場所だけ分割
#    する」。分割してよい理由=話者Voiceが変わる/Comment挿入位置/scene・
#    semantic boundary。1文・数語だけの独立TTSを避ける。Trial-10では、
#    device/brother引用符の直前直後にある短いnarrator地の文(例:
#    "The memory-storage screen asked,"=4語、"the screen asked."=3語、
#    "he whispered."=2語)がそれぞれ独立segmentになっていたが、Trial-11では
#    これらを「同じVoice(Aoede)が連続する側」の隣接segmentへ統合する
#    (Voice変化点そのものは分割不可避、その前後のAoede部分のみ統合)。
# ============================================================
QUOTE_RE = re.compile("“[^”]*”")

DEVICE_QUOTE_PARAGRAPH_INDICES = {2, 4}  # "Return date?" / "Are you sure?"
BROTHER_QUOTE_PARAGRAPH_INDICES = {14}   # "Do not make my last day your whole life,"

# Comment挿入位置(Trial-10の意味的判断を維持: C2=段落8/9境界のscene
# transition、C3=段落23/24境界のturning point直前)。Trial-11では
# plan_indexではなくsegment idで指定する(new segmentationで境界segment
# 自体が変わるため)。
COMMENT_2_AFTER_SEGMENT_ID = "story_005"  # 段落8/9境界(Trial-10と同じ意味的位置)
COMMENT_3_AFTER_SEGMENT_ID = "story_009"  # 段落23/24境界(Trial-10と同じ意味的位置)
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


# Trial-11: segment id -> 分割理由(報告・segmentation_plan.json共通)。
SEGMENT_SPLIT_REASON = {
    "story_001": "段落0-1のnarrator地の文+段落2のリード文(引用符直前)を統合。"
                 "直後がdevice voiceへ変わるため、そこでのみ分割。",
    "story_002": "Voice変化点(device、段落2の引用句 'Return date?')。分割不可避。",
    "story_003": "前後とも別Voice(device)に挟まれた孤立段落(段落3)。統合不可能な"
                 "構造上やむを得ない例外(6語)。",
    "story_004": "Voice変化点(device、段落4の引用句 'Are you sure?')。分割不可避。",
    "story_005": "段落4のトレイル文(引用符直後)+段落5-8のnarrator地の文を統合。"
                 "Comment 2挿入位置(段落8/9境界、scene transition)の直前で分割。",
    "story_006": "段落9-13のnarrator地の文を統合。直後がbrother voiceへ変わるため、"
                 "そこでのみ分割。",
    "story_007": "Voice変化点(brother、段落14の引用句 'Do not make my last day "
                 "your whole life,')。Brother Voice変更対象。分割不可避。",
    "story_008": "段落14のトレイル文(引用符直後)+段落15-19のnarrator地の文を統合"
                 "(回想の帰還〜内的独白の終わりまで)。次のscene/semantic boundary"
                 "(段落19/20境界、回想から現在の行動への回帰)で分割。",
    "story_009": "段落20-23のnarrator地の文を統合(現在の行動の記述)。Comment 3"
                 "挿入位置(段落23/24境界、turning point直前)の直前で分割。",
    "story_010": "段落24-28のnarrator地の文(結末部)を統合。Trial-10と同一区切り"
                 "(既存のComment後〜Outro前の構成を維持)。",
}


def build_all_story_segments_trial11(paragraphs: list) -> list:
    """Trial-11新segmentation設計。Voice変化点(device/brother)・Comment挿入
    位置・scene/semantic boundaryのみを分割理由とし、同一Voice(Aoede)が
    連続する部分は可能な限り一つのTTS callへ統合する(概ね100語以内、120語を
    大きく超えない範囲)。各segmentは{"id","voice","kind","source_paragraph_
    indices","raw_text","tts_text","paragraph_contributions"}を持つ
    (reconstruct_article_from_story_segmentsとの互換性を維持)。"""
    segments = []
    counter = {"n": 0}

    def next_id() -> str:
        counter["n"] += 1
        return f"story_{counter['n']:03d}"

    def add(voice: str, kind: str, source_idxs: list, raw_text: str,
            paragraph_contributions: list) -> None:
        segments.append({
            "id": next_id(), "voice": voice, "kind": kind,
            "source_paragraph_indices": source_idxs,
            "raw_text": raw_text, "tts_text": normalize_for_tts(raw_text),
            "paragraph_contributions": paragraph_contributions,
        })

    chunks2 = split_paragraph_by_quotes(paragraphs[2], "device")
    chunks4 = split_paragraph_by_quotes(paragraphs[4], "device")
    chunks14 = split_paragraph_by_quotes(paragraphs[14], "brother")
    lead2_text = chunks2[0][1]
    q1_text = chunks2[1][1]
    q2_text = chunks4[0][1]
    trail4_text = chunks4[1][1]
    q_brother_text = chunks14[0][1]
    trail14_text = chunks14[1][1]

    # story_001: narrator(merge)、段落0,1+段落2リード文
    raw1 = paragraphs[0] + "\n\n" + paragraphs[1] + "\n\n" + lead2_text
    add("narrator", "merge", [0, 1, 2], raw1,
        [(0, paragraphs[0]), (1, paragraphs[1]), (2, lead2_text)])

    # story_002: device(split)、段落2引用句
    add("device", "split", [2], q1_text, [(2, q1_text)])

    # story_003: narrator(merge)、段落3単独(前後ともdeviceに挟まれ統合不可)
    add("narrator", "merge", [3], paragraphs[3], [(3, paragraphs[3])])

    # story_004: device(split)、段落4引用句
    add("device", "split", [4], q2_text, [(4, q2_text)])

    # story_005: narrator(merge)、段落4トレイル文+段落5-8(Comment 2直前まで)
    raw5 = (trail4_text + "\n\n" + paragraphs[5] + "\n\n" + paragraphs[6] + "\n\n"
            + paragraphs[7] + "\n\n" + paragraphs[8])
    add("narrator", "merge", [4, 5, 6, 7, 8], raw5,
        [(4, trail4_text), (5, paragraphs[5]), (6, paragraphs[6]),
         (7, paragraphs[7]), (8, paragraphs[8])])

    # [Comment 2 挿入位置: story_005の直後]

    # story_006: narrator(merge)、段落9-13
    raw6 = "\n\n".join(paragraphs[i] for i in (9, 10, 11, 12, 13))
    add("narrator", "merge", [9, 10, 11, 12, 13], raw6,
        [(i, paragraphs[i]) for i in (9, 10, 11, 12, 13)])

    # story_007: brother(split)、段落14引用句
    add("brother", "split", [14], q_brother_text, [(14, q_brother_text)])

    # story_008: narrator(merge)、段落14トレイル文+段落15-19
    raw8 = (trail14_text + "\n\n"
            + "\n\n".join(paragraphs[i] for i in (15, 16, 17, 18, 19)))
    add("narrator", "merge", [14, 15, 16, 17, 18, 19], raw8,
        [(14, trail14_text)] + [(i, paragraphs[i]) for i in (15, 16, 17, 18, 19)])

    # story_009: narrator(merge)、段落20-23(Comment 3直前まで)
    raw9 = "\n\n".join(paragraphs[i] for i in (20, 21, 22, 23))
    add("narrator", "merge", [20, 21, 22, 23], raw9,
        [(i, paragraphs[i]) for i in (20, 21, 22, 23)])

    # [Comment 3 挿入位置: story_009の直後]

    # story_010: narrator(merge)、段落24-28(結末部)
    raw10 = "\n\n".join(paragraphs[i] for i in (24, 25, 26, 27, 28))
    add("narrator", "merge", [24, 25, 26, 27, 28], raw10,
        [(i, paragraphs[i]) for i in (24, 25, 26, 27, 28)])

    return segments


def reconstruct_article_from_story_segments(segments: list, num_paragraphs: int) -> str:
    per_para: dict = {}
    for seg in segments:
        for idx, text in seg["paragraph_contributions"]:
            per_para.setdefault(idx, []).append(text)
    paras = ["".join(per_para[i]) for i in range(num_paragraphs)]
    return "\n\n".join(paras)


def build_segmentation_plan_report(segments: list) -> list:
    """segmentation_plan.json用の設計表(id/voice/段落範囲/word count/
    分割理由)。TTS実行前のドライラン(--plan-only)で語数分布確認に使う。"""
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
# 2. Preview / Comment(日本語)
#    Preview roleはTrial-10と同一(Preview仕様は変更対象外、ユーザー指示は
#    Comment 1〜3のみ)。Comment roleはTrial-11新設(英文理解ガイド役割)。
#    生成関数は既存Production関数(a2gen.run_support_text)をそのまま呼ぶ。
# ============================================================
PREVIEW_ROLE_JA = (
    "あなたは英語学習者向け音声番組のPreview(導入)を書く担当です。"
    "これから流れる物語の日本語による短い前置きを、2文程度・80〜110字"
    "程度で書いてください。物語は、辛い記憶を小さな銀色の箱に預けて"
    "五年後に戻ってくるよう設定する女性レナの物語です。物語のテーマ・"
    "雰囲気・聞く価値を伝え、結末や中心的な問い(記憶が戻ったとき彼女が"
    "どうするか)の答えを先に明かさないでください。具体的な出来事・台詞を"
    "先出ししないでください。「この先を聞きたくなる」自然な話し言葉の"
    "日本語にしてください。新しい設定・事実・登場人物を追加しないで"
    "ください。"
)

# --- Trial-10旧Comment Prompt(_TRIAL10_PREV、比較用に残置。未使用) ---
COMMENT_1_ROLE_JA_TRIAL10_PREV = (
    "あなたは英語学習者向け音声番組で、物語が始まる直前に置く短い日本語"
    "コメントを書く担当です。これから、辛い記憶を小さな箱に預けて五年後に"
    "戻すことにした女性レナの物語が始まります。結末や主人公の選択を先に"
    "明かさず、1文程度・30〜50字程度で、物語の世界に耳を傾けるよう促す"
    "短い一言を書いてください。直前に流れるPreview(短い前置き)と同じ"
    "内容を繰り返さないでください。断定的な予告にせず、自然な話し言葉に"
    "してください。新しい設定・事実・登場人物を追加しないでください。"
)
COMMENT_2_ROLE_JA_TRIAL10_PREV = (
    "あなたは英語学習者向け音声番組の、物語の途中に挿入する短い日本語"
    "コメントを書く担当です。これから、五年前に箱へ預けた記憶が、五年後の"
    "ある朝に主人公のもとへ戻ってくる場面が始まります。結末や主人公の"
    "選択を先に明かさず、1文程度・40〜70字程度で、次に何が起きるかへ"
    "軽く注意を向ける短い日本語コメントを書いてください。断定的な予告に"
    "せず、自然な話し言葉にしてください。新しい設定・事実を追加しないで"
    "ください。"
)
COMMENT_3_ROLE_JA_TRIAL10_PREV = (
    "あなたは英語学習者向け音声番組の、物語の途中に挿入する短い日本語"
    "コメントを書く担当です。これから、主人公が辛い記憶を再び箱へ戻す"
    "べきかどうか、手を止めて迷う場面が続きます。結末や主人公の選択を"
    "先に明かさず、1文程度・40〜70字程度で、この迷いの重さへ軽く注意を"
    "向ける短い日本語コメントを書いてください。断定的な予告にせず、"
    "自然な話し言葉にしてください。新しい設定・事実を追加しないでください。"
)

# --- Trial-11新Comment Prompt(英文理解ガイド役割) ---
_BANNED_PHRASES_INSTRUCTION = (
    "「聞いてみましょう」「耳を傾けて」「耳を澄ませて」「注目してみましょう」"
    "「これからどうなるでしょう」のような、聞く行為だけを促す言い回しは"
    "使わないでください。雰囲気だけの抽象的な誘導や、本文を聞けば分かる"
    "だけの無内容な予告も避けてください。"
)
COMMENT_1_ROLE_JA_TRIAL11 = (
    "あなたは英語学習者向け音声番組で、物語の直前に置く短い日本語コメントを"
    "書く担当です。これから始まる物語の理解を助けるため、雰囲気作りの声かけ"
    "ではなく状況説明に徹してください。本文に書かれている事実のみを使い、"
    "次の点のうち必要なものだけを2〜3文・80〜110字程度で簡潔にまとめて"
    "ください: 主人公レナが小さな銀色の箱を持っていること、箱の中には"
    "亡くなった兄との最後の記憶が一つだけ収められていること、レナはその"
    "記憶をまだ開けていないこと。結末や主人公の選択(記憶を戻すかどうか)"
    "には触れないでください。新しい設定・登場人物を追加しないでください。"
    + _BANNED_PHRASES_INSTRUCTION
)
COMMENT_2_ROLE_JA_TRIAL11 = (
    "あなたは英語学習者向け音声番組で、物語の途中に挿入する短い日本語"
    "コメントを書く担当です。これから、レナが五年前に箱へ預けた記憶を、"
    "五年後のある朝に取り戻す場面が始まります。英文の理解を助けるため、"
    "雰囲気作りではなく状況整理に徹してください。本文の事実のみを使い、"
    "次の点のうち必要なものだけを2〜3文・80〜110字程度でまとめてください: "
    "五年という時間が経過したこと、記憶が箱から戻ってくる朝であること、"
    "これから兄の最期の言葉を含む記憶がよみがえること。結末や主人公の選択"
    "には触れないでください。新しい設定・事実を追加しないでください。"
    + _BANNED_PHRASES_INSTRUCTION
)
COMMENT_3_ROLE_JA_TRIAL11 = (
    "あなたは英語学習者向け音声番組で、物語の途中に挿入する短い日本語"
    "コメントを書く担当です。これから、記憶を取り戻したレナが、その記憶を"
    "再び箱へ戻して先送りするか、それとも今ここで受け止めるかを選ぶ場面が"
    "続きます。英文の理解を助けるため、雰囲気作りではなく状況整理に徹して"
    "ください。本文の事実のみを使い、次の点のうち必要なものだけを2〜3文・"
    "80〜110字程度でまとめてください: レナが箱に手を伸ばしたまま迷って"
    "いること、記憶を先送りするか受け止めるかという選択の対立点。結末"
    "(実際にどちらを選んだか)には触れないでください。新しい設定・事実を"
    "追加しないでください。" + _BANNED_PHRASES_INSTRUCTION
)
COMMENT_ROLES = {1: COMMENT_1_ROLE_JA_TRIAL11, 2: COMMENT_2_ROLE_JA_TRIAL11,
                  3: COMMENT_3_ROLE_JA_TRIAL11}
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
        # 品質不足(禁止語句混入)時のみ、同一Promptで最大1回再生成(委任文の
        # 上限どおり)。
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
# 3. TTS呼び出しラッパ(Trial-10と同一実装)
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


def copy_from_trial10_if_missing(rel_name: str) -> None:
    """Trial-10 memory_a2の既存正常asset(Intro/Outro/SFX/Welcome/Key Phrase/
    Preview/日本語タイトル/topic_intro等)を新OUT_DIRへコピーする(.okマーカー
    含む、再TTSしない)。Story segment(story_*)・Comment(comment_*)は対象外
    (Trial-11で再生成するため呼び出さない)。"""
    src = f"{PREV_OUT_DIR}/{rel_name}"
    dst = f"{OUT_DIR}/{rel_name}"
    if os.path.isdir(src):
        # dirs_exist_ok=True: KEY_PHRASE_DIR等が先にos.makedirsで空dirとして
        # 作成済みでも、中身のファイルコピーが正しく行われるようにする。
        shutil.copytree(src, dst, dirs_exist_ok=True)
        return
    if os.path.exists(dst):
        return
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.exists(src):
        shutil.copyfile(src, dst)


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


def tts_device(text: str, out_path: str, label: str, budget: BudgetTracker) -> dict:
    """装置(記憶保管画面)voice(Charon)。既存Production関数
    voice01.generate_charon_english()をそのまま呼ぶ(Trial-10と同一実装、
    Trial-11でも変更なし)。"""
    reused = _resumable_reuse(out_path)
    if reused is not None:
        return reused
    budget.check_before(TTS_CALL_EST_JPY, label)
    r = voice01.generate_charon_english(text, out_path)
    budget.add(label, "tts", 1, TTS_CALL_EST_JPY, {"status": r.get("status")})
    _mark_ok_if_success(r, out_path)
    return r


def tts_brother(text: str, out_path: str, label: str, budget: BudgetTracker) -> dict:
    """兄voice(Trial-11: Algieba)。既存Production関数
    bvoices.generate_voice_body_wide_margin()をそのまま呼ぶ(voice_name引数
    のみBROTHER_VOICE_NAMEへ差し替え)。"""
    reused = _resumable_reuse(out_path)
    if reused is not None:
        return reused
    budget.check_before(TTS_CALL_EST_JPY, label)
    r = bvoices.generate_voice_body_wide_margin(text, out_path, BROTHER_VOICE_NAME)
    budget.add(label, "tts", 1, TTS_CALL_EST_JPY, {"status": r.get("status")})
    _mark_ok_if_success(r, out_path)
    return r


def tts_key_phrase_english(text: str, out_path: str, label: str, budget: BudgetTracker) -> dict:
    reused = _resumable_reuse(out_path)
    if reused is not None:
        return reused
    budget.check_before(TTS_CALL_EST_JPY * 2, label)
    r = repro01.generate_key_phrase_component_verified(text, out_path, disfluency_qa=True)
    attempts = len(r.get("attempts_log", [])) or 1
    budget.add(label, "tts", attempts, TTS_CALL_EST_JPY, {"status": r.get("status")})
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


# ============================================================
# main
# ============================================================
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--budget-jpy", type=float, default=50.0)
    parser.add_argument("--plan-only", action="store_true",
                         help="TTSなし。segmentation_plan.jsonのみ生成し語数分布を表示して終了する。")
    args = parser.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)

    article_text = load_article_text()
    paragraphs = split_into_paragraphs(article_text)
    assert len(paragraphs) == 29, f"unexpected paragraph count: {len(paragraphs)}"

    story_segments = build_all_story_segments_trial11(paragraphs)
    reconstructed = reconstruct_article_from_story_segments(story_segments, len(paragraphs))
    assert reconstructed == article_text, "STORY_SEGMENT reconstruction mismatch(生成前チェック)"

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
            "segments": plan_rows,
        }, f, ensure_ascii=False, indent=2)

    print(f"[PLAN] segment_count={len(plan_rows)} "
          f"min_word_count={min(r['word_count'] for r in plan_rows)} "
          f"max_word_count={max(r['word_count'] for r in plan_rows)}")
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

    # er005_cost_logger初期化(既存パターン、er013_family_c_episode_trial_10_
    # memory_b1_run.py L542と同一呼び出し。Trial-10 A2側スクリプトはこの
    # 初期化を欠いていたが、ASR cascadeがAzure二次検証まで到達しなかった
    # ため問題が顕在化していなかった[既知gap、本タスクでは仕様変更せず
    # 単に正しく初期化するのみ]。er005/er006自体は無変更。
    cl.install(f"{AUDIT_DIR}/er005_cost_log.jsonl")

    budget = BudgetTracker(args.budget_jpy, 40.0, f"{OUT_DIR}/raw_usage_log.jsonl")

    # --- 本文固定確認(sha256記録、Trial-08正本をTrial-10と同一値で固定) ---
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

    # === Stage A: SFX/Nav資産の読み込み + Trial-10既存asset reuse(新規TTSなし) ===
    intro_mp3 = p9a.load_and_resample_to_target(INTRO_MP3_PATH)
    outro_mp3 = p9a.load_and_resample_to_target(OUTRO_MP3_PATH)
    notification_mp3 = p9a.load_and_resample_to_target(NOTIFICATION_MP3_PATH)
    nav = copy_shared_charon_nav(AUDIO_DIR)

    # 非Story・非Comment asset(topic_intro_en/japanese_title/preview_ja/
    # kp_*[Key Phrase英語5+日本語5+number5]、preview.txt、key_phrases/*)を
    # Trial-10からコピー(再TTSしない)。welcome.wav等のB1_SHARED navは
    # copy_shared_charon_nav()で共有ソースから直接コピー済み(上記)。
    for rel in ("audio/topic_intro_en.wav", "audio/topic_intro_en.wav.ok",
                "audio/japanese_title.wav", "audio/japanese_title.wav.ok",
                "audio/preview_ja.wav", "audio/preview_ja.wav.ok",
                "preview.txt", "key_phrases"):
        copy_from_trial10_if_missing(rel)
    for rank in (1, 2, 3, 4, 5):
        reuse_shared_number_word(rank, f"{AUDIO_DIR}/kp{rank}_number.wav")  # B1_SHARED、記事非依存
        for kind in ("english", "japanese"):
            copy_from_trial10_if_missing(f"audio/kp{rank}_{kind}.wav")
            copy_from_trial10_if_missing(f"audio/kp{rank}_{kind}.wav.ok")
    with open(f"{PREV_OUT_DIR}/key_phrase_consistency.json", encoding="utf-8") as f:
        kp_consistency_prev = json.load(f)
    with open(f"{OUT_DIR}/key_phrase_consistency.json", "w", encoding="utf-8") as f:
        json.dump(kp_consistency_prev, f, ensure_ascii=False, indent=2)

    with open(f"{KEY_PHRASE_DIR}/keywords_canonicalized.json", encoding="utf-8") as f:
        kp_items = sorted(json.load(f)["items"], key=lambda it: it["rank"])

    # === Stage B: Topic intro(EN) + Japanese title(JA) — Trial-10からreuse ===
    with open(f"{PREV_OUT_DIR}/audit/tts_generation_results.json", encoding="utf-8") as f:
        prev_tts_results = json.load(f)
    audit_segments["topic_intro_en"] = prev_tts_results["segments"]["topic_intro_en"]
    audit_segments["japanese_title"] = prev_tts_results["segments"]["japanese_title"]

    # === Stage C: Preview(日本語) — Trial-10からreuse(既にコピー済み) ===
    with open(f"{OUT_DIR}/preview.txt", encoding="utf-8") as f:
        preview_text = f.read().strip()
    audit_segments["preview_ja"] = prev_tts_results["segments"]["preview_ja"]

    # === Stage D: Key Phrase — Trial-10からreuse(既にコピー済み) ===
    audit_key_phrases = prev_tts_results["key_phrases"]
    kp_blocks_stereo = []
    for item in kp_items:
        rank = item["rank"]
        kp_blocks_stereo.append((rank, f"{AUDIO_DIR}/kp{rank}_number.wav",
                                  f"{AUDIO_DIR}/kp{rank}_english.wav",
                                  f"{AUDIO_DIR}/kp{rank}_japanese.wav"))

    # === Stage E: Comment 1〜3(日本語、Trial-11新規LLM+TTS。Comment 4は使用しない) ===
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

    # === Stage F: 物語本文segment(Trial-11新segmentation、全件新規TTS) ===
    for seg in story_segments:
        out_path = f"{AUDIO_DIR}/{seg['id']}.wav"
        if seg["voice"] == "narrator":
            r = tts_narrator(seg["tts_text"], out_path, "en", seg["id"], budget)
        elif seg["voice"] == "device":
            r = tts_device(seg["tts_text"], out_path, seg["id"], budget)
        elif seg["voice"] == "brother":
            r = tts_brother(seg["tts_text"], out_path, seg["id"], budget)
        else:
            raise ValueError(f"unknown voice: {seg['voice']}")
        audit_segments[seg["id"]] = _to_audit_entry(r, seg["tts_text"])
        seg["audio_path"] = out_path

    with open(f"{OUT_DIR}/segments.json", "w", encoding="utf-8") as f:
        json.dump([{k: v for k, v in s.items() if k != "paragraph_contributions"}
                   for s in story_segments], f, ensure_ascii=False, indent=2)

    # === Stage G: speaker_map.json(話者判定表) ===
    speaker_map = []
    for seg in story_segments:
        if seg["kind"] == "split" and seg["voice"] in ("device", "brother"):
            attribution = ("引用符直後の地の文(段落2/4: 'the screen asked')" if seg["voice"] == "device"
                            else "引用符直後の地の文+直前文脈(段落13: 'His voice returned.'"
                                 "、代名詞heは段落12'her brother'を指す)")
            speaker_map.append({"segment_id": seg["id"], "voice": seg["voice"],
                                 "source_paragraph_indices": seg["source_paragraph_indices"],
                                 "quote_text": seg["raw_text"], "attribution_basis": attribution})
    with open(f"{OUT_DIR}/speaker_map.json", "w", encoding="utf-8") as f:
        json.dump({
            "narrator_voice": "Aoede", "device_voice": "Charon", "brother_voice": BROTHER_VOICE_NAME,
            "brother_voice_change_note": (
                "Trial-11変更: Erinome(旧、median F0約221Hz)→Algieba(新、median F0約112Hz)。"
                "既存承認Voice候補6種中Algiebaが最も低いピッチ(男性域に近い)と推定されたため選定"
                "(自己相関法によるピッチ推定、既存sample wav使用、追加TTS費用ゼロ)。"),
            "lena_split_decision": ("Lena本人の台詞(段落5, 19)はnarrator(Aoede)のまま分離しない"
                                     "(Trial-10から無変更の設計判断)。"),
            "entries": speaker_map,
        }, f, ensure_ascii=False, indent=2)

    # === Stage H: gain + timeline構築(Family A構成をそのまま踏襲) ===
    def gs(mono: np.ndarray, label: str) -> np.ndarray:
        gain = p9a.compute_gain_for_target_rms(mono, target_rms)
        gained = mono * gain
        gain_report[label] = {"gain": round(float(gain), 4), "rms_before": round(p9a.rms(mono), 5),
                               "rms_after": round(p9a.rms(gained), 5), "peak_after": round(p9a.peak(gained), 5)}
        return p9a.mono_24k_to_stereo_target(gained)

    preview_mono = load_mono(f"{AUDIO_DIR}/preview_ja.wav")
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
    sil(1.0)  # pause_1.0_en_to_ja(A2既存値)

    # --- Comment 1(導入、Story前) ---
    c1_path, c1_r = comment_wavs[1]
    seq.append(("Comment 1", gs(load_mono(c1_path), "comment_1")))
    sil(0.8)  # pause_0.8_ja_to_en(A2既存値)

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

    # Comment 4は使用しない(Family C既定)。Story終了後は既存Family A構成
    # どおりpause→Outroとする。
    sil(0.5)  # pause_0.5(A2既存値、Outro直前)
    seq.append(("Outro", outro_gained))

    with open(f"{AUDIT_DIR}/gain_report.json", "w", encoding="utf-8") as f:
        json.dump(gain_report, f, ensure_ascii=False, indent=2)

    assembled_result = assemble_mod.assemble_with_timeline(seq)
    safety_result = assemble_mod.apply_headroom_safety_valve(assembled_result["assembled"], seq)
    with open(f"{AUDIT_DIR}/headroom_report.json", "w", encoding="utf-8") as f:
        json.dump(safety_result["report"], f, ensure_ascii=False, indent=2)

    final_path = f"{ASSEMBLED_DIR}/family_c_memory_trial_11.wav"
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

    # === Stage K: player/display/audio consistency(story segment分) ===
    for seg in story_segments:
        asr_text = audit_segments[seg["id"]].get("asr_text")
        if asr_text is None:
            asr_text = asr_diag(seg["audio_path"], "en", budget, f"{seg['id']}_asr_diag")
            audit_segments[seg["id"]]["asr_text"] = asr_text
        consistency_rows.append({
            "segment_id": seg["id"], "voice": seg["voice"],
            "player_display_text": seg["tts_text"], "canonical_text": seg["tts_text"],
            "tts_input_text": seg["tts_text"], "asr_text": asr_text,
            "match": _normalize_loose(asr_text) == _normalize_loose(seg["tts_text"]),
        })
    fixed_checks = [
        ("topic_intro_en", TOPIC_INTRO_EN_TEXT, "en", audit_segments["topic_intro_en"].get("asr_text")),
        ("japanese_title", JAPANESE_TITLE_TEXT, "ja", audit_segments["japanese_title"].get("asr_text")),
        ("preview_ja", preview_text, "ja", None),
    ]
    for n in COMMENT_NUMBERS:
        fixed_checks.append((f"comment_{n}_ja", comment_texts[n], "ja",
                              audit_segments[f"comment_{n}_ja"].get("asr_text")))
    for key, (_fname, text) in SHARED_CHARON_NAV.items():
        fixed_checks.append((key, text, "en", None))
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

    # === Stage M: comment_placement.json(前後text volume/duration、根拠記録) ===
    def _wav_duration(path: str) -> float:
        mono, sr, _, _ = common.read_wav_float(path)
        return round(len(mono) / sr, 3)

    seg_by_id_all = {s["id"]: s for s in story_segments}
    placement = []
    boundary_defs = [
        (1, "導入部(Preview後・Story前、Full story introの直後)", None,
         story_segments[0]["id"]),
        (2, "段落8/9境界(scene transition: 'For a while, Lena felt free...'から"
            "'Five years later, on a cold morning, the box opened.'への時間跳躍。"
            "Trial-10と同一の意味的位置)",
         COMMENT_2_AFTER_SEGMENT_ID,
         story_segments[[s["id"] for s in story_segments].index(COMMENT_2_AFTER_SEGMENT_ID) + 1]["id"]),
        (3, "段落23/24境界(turning point直前: 'would that be healing? Or would she "
            "only be leaving a frightened part of herself alone in a dark room?'という"
            "問いの直後、'Lena did not press the button.'という結末を明かす一文の直前。"
            "Trial-10と同一の意味的位置)",
         COMMENT_3_AFTER_SEGMENT_ID,
         story_segments[[s["id"] for s in story_segments].index(COMMENT_3_AFTER_SEGMENT_ID) + 1]["id"]),
    ]
    for n, desc, before_id, after_id in boundary_defs:
        before_words = len(seg_by_id_all[before_id]["tts_text"].split()) if before_id else None
        after_words = len(seg_by_id_all[after_id]["tts_text"].split()) if after_id else None
        path, _r = comment_wavs[n]
        placement.append({
            "comment": n, "position_description": desc,
            "before_segment_id": before_id, "after_segment_id": after_id,
            "before_segment_word_count": before_words, "after_segment_word_count": after_words,
            "comment_duration_seconds": _wav_duration(path),
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
        "budget_cap_jpy": args.budget_jpy, "warn_threshold_jpy": 40.0,
        "total_estimate_jpy": round(total_jpy, 2),
        "note": "raw_usage_log.jsonl全体(複数回のresume実行を含む)からの累計。",
        "tts_call_count_estimate_basis": tts_count, "llm_call_count_estimate_basis": llm_count,
        "asr_diag_call_count_estimate_basis": asr_diag_count,
        "methodology": ("既存Production wrapper関数がtoken単位usageを返さないため、"
                        "precedentベースの安全側単価推定(Trial-10と同一単価)。"),
        "gate_status": gate_status,
    }
    with open(f"{OUT_DIR}/cost_summary.json", "w", encoding="utf-8") as f:
        json.dump(cost_summary, f, ensure_ascii=False, indent=2)

    print(f"[DONE] duration={run_summary['duration_seconds']}s gate={gate_status} "
          f"cost_estimate=Y{total_jpy:.2f}")


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


def write_family_a_reuse_map() -> None:
    rows = [
        ("Intro(SFXジングル)", "p9a.INTRO_MP3_PATH", "そのまま流用(mp3読み込みのみ)"),
        ("Outro(SFXジングル)", "p9a.OUTRO_MP3_PATH", "そのまま流用"),
        ("Notification(通知音、3箇所)", "p9a.NOTIFICATION_MP3_PATH",
         "Topic intro前/Preview前/Key phrases intro前の3箇所に挿入(Trial-10と同一位置)"),
        ("Welcome(Charon)", "Trial-10 memory_a2/audio/welcome.wav(コピー、再TTSなし)", "そのまま流用"),
        ("Preview intro(Charon)", "B1_SHARED_NAMES preview_intro_charon.wav", "同上"),
        ("Key phrases intro(Charon)", "B1_SHARED_NAMES key_phrases_intro_charon.wav", "同上"),
        ("Full story intro(Charon)", "B1_SHARED_NAMES full_story_intro_charon.wav", "同上"),
        ("番号読み上げ(One.〜Five.)", "B1_SHARED_NAMES num_X_charon.wav", "そのまま流用"),
        ("Topic intro(EN)音声/Japanese title音声/Preview(JA)音声/Key Phrase英語・日本語音声",
         "Trial-10 memory_a2/audio(コピー、再TTSなし)",
         "本文・テキストは無変更のため再生成不要。再TTS対象はStory segment全件+Comment 1〜3のみ"),
        ("Key Phrase選定・canonicalization", "Trial-10 memory_a2/key_phrases(コピー)", "再選定なし"),
        ("Comment前後pause(1.0秒 en→ja、0.8秒 ja→en)",
         "er003_v1_n3_01_assemble.py::build_a2_timeline pause_1.0_en_to_ja/pause_0.8_ja_to_en",
         "Comment1〜3の前後遷移にそのまま適用(Trial-10と同一)"),
        ("Outro直前pause(0.5秒)", "build_a2_timeline pause_0.5(In One Line→Outro)",
         "Story末尾→Outroの遷移にそのまま適用"),
        ("Assembly/Gate/player", "assemble_with_timeline/apply_headroom_safety_valve/"
         "verify_episode_audio_validation_gate/audio_review_player.py", "そのまま流用(無変更)"),
        ("Voice(Charon=装置、Algieba=兄)", "er012_b_family_voices_production_01/"
         "er003_v1_sing01_voice01_generate", "Trial-11変更点: 兄voiceのみErinome→Algiebaへ"
         "変更(既存承認Voice候補の範囲内、ピッチ推定に基づく選定)。装置Voice(Charon)は無変更"),
    ]
    lines = ["# Family A流用表(memory A2、Trial-11)\n", "| 項目 | 流用元 | 扱い |", "|---|---|---|"]
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
    ep_wav = f"{ASSEMBLED_DIR}/family_c_memory_trial_11.wav"
    ep_mp3 = f"{WEB_DIR}/family_c_memory_trial_11.mp3"
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
            voice_disp = {"narrator": "Aoede(narrator)", "device": "Charon(device)",
                          "brother": f"{BROTHER_VOICE_NAME}(brother)"}[seg["voice"]]
            audio_html = player_mod.render_single_audio_html(f"./web/segments/{seg['id']}.mp3")
            rows.append(player_mod.render_timeline_row(start, name, voice_disp, seg["tts_text"], audio_html))

    table_html = player_mod.render_timeline_table(rows)
    episode_url = "./web/family_c_memory_trial_11.mp3"
    html = f"""<!doctype html><html><head><meta charset="utf-8">
<title>Family C Trial-11: The Future of Memory(A2、segmentation統合+Comment理解ガイド化)</title>
<style>{player_mod.PLAYER_STANDARD_CSS}</style>
<script>{player_mod.SEEK_SCRIPT}</script>
</head><body>
<h1>Family C Future — The Future of Memory(Trial-11 A2 / VALIDATED候補・USER_LISTENING_PENDING、
Production未採用)</h1>
<p>duration={run_summary['duration_seconds']}s / peak={run_summary['peak_after_headroom']}</p>
<p>Trial-11変更点: Story segment統合(旧14→新10)、Comment 1〜3を英文理解ガイドへ変更、
兄Voice(Erinome→Algieba)。旧版は
<a href="../../family_c_episode_trial_10/memory_a2/player.html">Trial-10 player</a>参照。</p>
<audio id="episode_audio" class="main" controls preload="none" src="{episode_url}"></audio>
{table_html}
</body></html>"""
    with open(f"{OUT_DIR}/player.html", "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    main()
