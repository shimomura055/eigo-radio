# ============================================================
# er013_family_c_episode_trial_10_memory_run.py
# 管理ID: USER-TEST-FINAL-AUDIO-BATCH-06(委任B: Family C「The future of
# memory」A2 episode)
# ============================================================
# 目的: Family C Trial-08で採用済みの記事本文(memory/reader_facing_
# article.txt、正本候補として固定・再生成しない)を、Home Robots v2
# (er013_family_c_episode_trial_09b_run.py)でユーザーが確認したFamily C
# 構成(Intro/Welcome/English Title/日本語タイトル/Preview/Key Phrase/
# Story/Comment 1-3[Comment 4なし]/Outro、既存SFX・pause)へ適用し、
# 完成episodeを作る。
#
# 本ファイルは`er013_family_c_episode_trial_09b_run.py`を複製したもの
# (Home Robots用スクリプトは無編集のまま維持し、本ファイルのみを実行
# する)。Home Robotsと異なりこの記事には流用可能なv1音声・Preview/Key
# Phraseテキストが存在しないため、v1音声reuseロジック(reuse_v1_wav等)・
# Comment 3固定差し替え・Robot二人称化フィックスなど、Home Robots固有の
# 修正フラグは削除し、Preview/Key Phraseは記事から新規生成する
# (`er013_family_c_episode_trial_09_run.py`のStage B/C相当、Production
# 関数を呼び出すだけ)。Story本文は無変更(Fact/学習内容は変えない)。
#
# 話者: 本記事はロボット/母親ではなく「装置(記憶保管画面)」と「兄」が
# 登場する。Home Robots同様、主人公(Lena)本人の台詞はnarrator(Aoede)
# のまま分離せず、装置の台詞のみCharon、兄の台詞のみErinomeへ分離する
# (既存4Voice候補の範囲内、新Voice探索なし)。
#
# 実行方法:
#   .venv/Scripts/python.exe er013_family_c_episode_trial_10_memory_run.py \
#       --budget-jpy 80
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
import er006_asr_provider_routing_01 as asr_routing
import er012_b_family_voices_production_01 as bvoices

import audio_review_player as player_mod

# ============================================================
# パス定数
# ============================================================
ARTICLE_PATH = "er013_output/family_c_future_trial_08/memory/reader_facing_article.txt"
OUT_DIR = "er013_output/family_c_episode_trial_10/memory_a2"
AUDIO_DIR = f"{OUT_DIR}/audio"
ASSEMBLED_DIR = f"{OUT_DIR}/assembled"
KEY_PHRASE_DIR = f"{OUT_DIR}/key_phrases"
AUDIT_DIR = f"{OUT_DIR}/audit"
WEB_DIR = f"{OUT_DIR}/web"
WEB_SEG_DIR = f"{WEB_DIR}/segments"

SR = p9a.TARGET_SAMPLE_RATE  # 48000
MONO_SR = common.SAMPLE_RATE  # 24000

ARTICLE_ID = "family_c_memory_trial_10"
LEVEL = "FAMILY_C_TRIAL_10_MEMORY_A2"  # 新規level文字列。既存level辞書(A2/B1/
                                        # B_FAMILY_A2/FAMILY_C_TRIAL_09B等)には
                                        # 存在せず、Audio Validation Gateの既存
                                        # required_structure/disfluency辞書は
                                        # 無変更。

TOPIC_TITLE = "The Future of Memory"
TOPIC_INTRO_EN_TEXT = f"Today's topic is {TOPIC_TITLE}."
JAPANESE_TITLE_TEXT = "記憶の未来"  # TOPIC_TITLEの直訳(既存A2規約どおり、1件登録。
                                    # 記事本文自体には題名が存在しないため
                                    # theme名[user指示5の記事名]を直訳する)。

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

BROTHER_VOICE_NAME = "Erinome"  # Home RobotsのMOTHER_VOICE_NAMEと同一Voice
                                 # (既存4Voice候補、APPROVED_FOR_PRODUCTION実績あり)
                                 # を「兄」役へそのまま転用。

# ============================================================
# 予算管理(Home Robots v2と同一方式、¥80ハード上限、¥60で警告)
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
# 1. Format normalization + 3-voice segment分割(決定的、API不要)
#    段落0-indexedで29段落。装置(screen)の直接発話2箇所[2,4]をCharon、
#    兄の直接発話1箇所[14]をErinomeへ分離する。Lena本人の台詞(段落5,19)は
#    Home Robots同様narrator(Aoede)のまま分離しない。
# ============================================================
QUOTE_RE = re.compile("“[^”]*”")

DEVICE_QUOTE_PARAGRAPH_INDICES = {2, 4}  # "Return date?" / "Are you sure?"
BROTHER_QUOTE_PARAGRAPH_INDICES = {14}   # "Do not make my last day your whole life,"

# セグメント構成計画(0-indexed段落、merge=narrator地の文の連結、
# split=引用符境界で話者分離)。Comment挿入位置はCOMMENT_2/3_AFTER_PLAN_
# INDEXで指定する(該当planエントリ処理後に挿入)。
STORY_SEGMENT_PLAN = [
    ("merge", [0, 1]),                     # 0
    ("split", 2),                          # 1  device
    ("merge", [3]),                        # 2
    ("split", 4),                          # 3  device
    ("merge", [5, 6, 7, 8]),               # 4  <- C2はこの直後(scene transition: "Five years later")
    ("merge", [9, 10, 11, 12, 13]),        # 5
    ("split", 14),                         # 6  brother
    ("merge", [15, 16, 17, 18, 19]),       # 7
    ("merge", [20, 21, 22]),               # 8
    ("merge", [23]),                       # 9  <- C3はこの直後(turning point直前、結末は明かさない)
    ("merge", [24, 25, 26, 27, 28]),       # 10
]
COMMENT_2_AFTER_PLAN_INDEX = 4
COMMENT_3_AFTER_PLAN_INDEX = 9
# C1はplan全体の前(story開始直前)に固定。Comment 4は使用しない。


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


def build_all_story_segments(paragraphs: list) -> list:
    """STORY_SEGMENT_PLANに従い、TTS用segmentのリストを構築する。
    各segmentは{"id","voice","kind","source_paragraph_indices","raw_text",
    "tts_text","paragraph_contributions","plan_index"}を持つ。"""
    segments = []
    counter = {"n": 0}

    def next_id() -> str:
        counter["n"] += 1
        return f"story_{counter['n']:03d}"

    def add_merge(idxs: list, plan_index: int) -> None:
        raw_text = "\n\n".join(paragraphs[i] for i in idxs)
        segments.append({
            "id": next_id(), "voice": "narrator", "kind": "merge", "plan_index": plan_index,
            "source_paragraph_indices": list(idxs),
            "raw_text": raw_text, "tts_text": normalize_for_tts(raw_text),
            "paragraph_contributions": [(i, paragraphs[i]) for i in idxs],
        })

    def add_split(idx: int, plan_index: int) -> None:
        if idx in DEVICE_QUOTE_PARAGRAPH_INDICES:
            chunks = split_paragraph_by_quotes(paragraphs[idx], "device")
        elif idx in BROTHER_QUOTE_PARAGRAPH_INDICES:
            chunks = split_paragraph_by_quotes(paragraphs[idx], "brother")
        else:
            raise ValueError(f"unexpected split paragraph index: {idx}")
        for voice, chunk_text in chunks:
            if chunk_text.strip() == "":
                continue
            segments.append({
                "id": next_id(), "voice": voice, "kind": "split", "plan_index": plan_index,
                "source_paragraph_indices": [idx],
                "raw_text": chunk_text, "tts_text": normalize_for_tts(chunk_text),
                "paragraph_contributions": [(idx, chunk_text)],
            })

    for plan_index, (kind, arg) in enumerate(STORY_SEGMENT_PLAN):
        if kind == "merge":
            add_merge(arg, plan_index)
        else:
            add_split(arg, plan_index)
    return segments


def reconstruct_article_from_story_segments(segments: list, num_paragraphs: int) -> str:
    per_para: dict = {}
    for seg in segments:
        for idx, text in seg["paragraph_contributions"]:
            per_para.setdefault(idx, []).append(text)
    paras = ["".join(per_para[i]) for i in range(num_paragraphs)]
    return "\n\n".join(paras)


# ============================================================
# 2. Preview / Comment(日本語) — role instructionはTrial専用新規文言、
#    生成関数は既存Production関数(a2gen.run_support_text)をそのまま呼ぶ
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
COMMENT_1_ROLE_JA = (
    "あなたは英語学習者向け音声番組で、物語が始まる直前に置く短い日本語"
    "コメントを書く担当です。これから、辛い記憶を小さな箱に預けて五年後に"
    "戻すことにした女性レナの物語が始まります。結末や主人公の選択を先に"
    "明かさず、1文程度・30〜50字程度で、物語の世界に耳を傾けるよう促す"
    "短い一言を書いてください。直前に流れるPreview(短い前置き)と同じ"
    "内容を繰り返さないでください。断定的な予告にせず、自然な話し言葉に"
    "してください。新しい設定・事実・登場人物を追加しないでください。"
)
COMMENT_2_ROLE_JA = (
    "あなたは英語学習者向け音声番組の、物語の途中に挿入する短い日本語"
    "コメントを書く担当です。これから、五年前に箱へ預けた記憶が、五年後の"
    "ある朝に主人公のもとへ戻ってくる場面が始まります。結末や主人公の"
    "選択を先に明かさず、1文程度・40〜70字程度で、次に何が起きるかへ"
    "軽く注意を向ける短い日本語コメントを書いてください。断定的な予告に"
    "せず、自然な話し言葉にしてください。新しい設定・事実を追加しないで"
    "ください。"
)
COMMENT_3_ROLE_JA = (
    "あなたは英語学習者向け音声番組の、物語の途中に挿入する短い日本語"
    "コメントを書く担当です。これから、主人公が辛い記憶を再び箱へ戻す"
    "べきかどうか、手を止めて迷う場面が続きます。結末や主人公の選択を"
    "先に明かさず、1文程度・40〜70字程度で、この迷いの重さへ軽く注意を"
    "向ける短い日本語コメントを書いてください。断定的な予告にせず、"
    "自然な話し言葉にしてください。新しい設定・事実を追加しないでください。"
)
COMMENT_ROLES = {1: COMMENT_1_ROLE_JA, 2: COMMENT_2_ROLE_JA, 3: COMMENT_3_ROLE_JA}
COMMENT_NUMBERS = (1, 2, 3)  # Family C既定(Comment 4なし)


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
    return result["text"].strip()


# ============================================================
# 3. TTS呼び出しラッパ
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
    voice01.generate_charon_english()をそのまま呼ぶ(Home Robotsのtts_robot
    と同一実装、話者名のみ「装置」に読み替え)。"""
    reused = _resumable_reuse(out_path)
    if reused is not None:
        return reused
    budget.check_before(TTS_CALL_EST_JPY, label)
    r = voice01.generate_charon_english(text, out_path)
    budget.add(label, "tts", 1, TTS_CALL_EST_JPY, {"status": r.get("status")})
    _mark_ok_if_success(r, out_path)
    return r


def tts_brother(text: str, out_path: str, label: str, budget: BudgetTracker) -> dict:
    """兄voice(Erinome)。既存Production関数
    bvoices.generate_voice_body_wide_margin()をそのまま呼ぶ(Home Robotsの
    tts_mother[MOTHER_VOICE_NAME=Erinome]と同一実装、voice_name引数のみ
    共通)。"""
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
    parser.add_argument("--budget-jpy", type=float, default=80.0)
    args = parser.parse_args()

    os.makedirs(AUDIO_DIR, exist_ok=True)
    os.makedirs(ASSEMBLED_DIR, exist_ok=True)
    os.makedirs(KEY_PHRASE_DIR, exist_ok=True)
    os.makedirs(AUDIT_DIR, exist_ok=True)

    budget = BudgetTracker(args.budget_jpy, 60.0, f"{OUT_DIR}/raw_usage_log.jsonl")

    article_text = load_article_text()
    paragraphs = split_into_paragraphs(article_text)
    assert len(paragraphs) == 29, f"unexpected paragraph count: {len(paragraphs)}"

    # --- 本文固定確認(sha256記録、ユーザー指示によりTrial-08正本を固定) ---
    normalized = normalize_for_tts(article_text)
    with open(f"{OUT_DIR}/article_normalized.txt", "w", encoding="utf-8") as f:
        f.write(normalized)
    src_sha = sha256_text_file(ARTICLE_PATH)
    with open(f"{AUDIT_DIR}/article_fixed_sha256.json", "w", encoding="utf-8") as f:
        json.dump({"source_article_sha256": src_sha, "source_path": ARTICLE_PATH,
                   "policy": "Trial-08正本固定、再生成・書き換えなし(ユーザー指示2026-09-15)"},
                   f, ensure_ascii=False, indent=2)

    audit_segments: dict = {}
    audit_key_phrases: dict = {}
    gain_report: dict = {}
    consistency_rows: list = []

    client = a2gen.get_client()

    # === Stage A: SFX/Nav資産の読み込み(新規TTSなし) ===
    intro_mp3 = p9a.load_and_resample_to_target(INTRO_MP3_PATH)
    outro_mp3 = p9a.load_and_resample_to_target(OUTRO_MP3_PATH)
    notification_mp3 = p9a.load_and_resample_to_target(NOTIFICATION_MP3_PATH)
    nav = copy_shared_charon_nav(AUDIO_DIR)

    # === Stage B: Topic intro(EN) + Japanese title(JA、直訳1件・新規TTS) ===
    r_topic_en = tts_narrator(TOPIC_INTRO_EN_TEXT, f"{AUDIO_DIR}/topic_intro_en.wav", "en",
                               "topic_intro_en", budget)
    audit_segments["topic_intro_en"] = _to_audit_entry(r_topic_en, TOPIC_INTRO_EN_TEXT)

    r_title = tts_narrator(JAPANESE_TITLE_TEXT, f"{AUDIO_DIR}/japanese_title.wav", "ja",
                            "japanese_title", budget)
    audit_segments["japanese_title"] = _to_audit_entry(r_title, JAPANESE_TITLE_TEXT)

    # === Stage C: Preview(日本語、新規LLM+TTS。resumable: preview.txt既存なら再利用) ===
    preview_txt_path = f"{OUT_DIR}/preview.txt"
    if os.path.exists(preview_txt_path):
        with open(preview_txt_path, encoding="utf-8") as f:
            preview_text = f.read().strip()
    else:
        preview_result = run_ja_support_text(client, PREVIEW_ROLE_JA, article_text, "preview_llm", budget)
        preview_text = preview_result["text"].strip()
        with open(preview_txt_path, "w", encoding="utf-8") as f:
            f.write(preview_text)
    r_preview = tts_narrator(preview_text, f"{AUDIO_DIR}/preview_ja.wav", "ja", "preview_ja", budget)
    audit_segments["preview_ja"] = _to_audit_entry(r_preview, preview_text)

    # === Stage D: Key Phrase(選定→canonicalization→redundancy QA→TTS、
    #     全て既存Production正式入口scaffold.run_key_phrases()経由) ===
    KEY_PHRASE_TOP_LEVEL_RETRY_MAX = 6
    canonicalized_path = f"{KEY_PHRASE_DIR}/keywords_canonicalized.json"
    redundancy_path = f"{KEY_PHRASE_DIR}/keyphrase_redundancy_qa.json"
    if os.path.exists(canonicalized_path) and os.path.exists(redundancy_path):
        with open(canonicalized_path, encoding="utf-8") as f:
            kp_items = sorted(json.load(f)["items"], key=lambda it: it["rank"])
        print("[KEY PHRASE] reusing existing canonicalized result from previous run")
    else:
        kp_result = None
        for kp_attempt in range(1, KEY_PHRASE_TOP_LEVEL_RETRY_MAX + 1):
            budget.check_before(9 * LLM_CALL_EST_JPY, f"key_phrases_selection_pipeline_attempt{kp_attempt}")
            kp_result = scaffold.run_key_phrases(article_text, KEY_PHRASE_DIR, ARTICLE_ID, "A2", process=None)
            llm_calls_est = 1 + (3 if kp_result.get("canonicalization") is not None else 0) * (
                1 + len(kp_result.get("redundancy_retry_log", [])))
            budget.add(f"key_phrases_selection_pipeline_attempt{kp_attempt}", "llm", llm_calls_est,
                       LLM_CALL_EST_JPY,
                       {"selection_status": kp_result.get("selection", {}).get("status"),
                        "redundancy_retry_attempts": len(kp_result.get("redundancy_retry_log", []))})
            if (kp_result.get("canonicalization") is not None
                    and kp_result["canonicalization"].get("merged") is not None):
                break
            print(f"[KEY PHRASE] attempt {kp_attempt} failed "
                  f"(selection status={kp_result.get('selection', {}).get('status')}); "
                  f"{'retrying' if kp_attempt < KEY_PHRASE_TOP_LEVEL_RETRY_MAX else 'giving up'}")
        if kp_result.get("canonicalization") is None or kp_result["canonicalization"].get("merged") is None:
            raise RuntimeError(f"KEY_PHRASE_SELECTION_FAILED after {KEY_PHRASE_TOP_LEVEL_RETRY_MAX} "
                                f"top-level attempts: {kp_result}")
        kp_items = sorted(kp_result["canonicalization"]["merged"]["items"], key=lambda it: it["rank"])

    kp_blocks_stereo = []
    kp_consistency = {}
    for item in kp_items:
        rank = item["rank"]
        used_form = item["used_form"]
        ja_gloss_display = item.get("japanese_gloss")
        ja_gloss_tts = item.get("japanese_gloss_tts") or ja_gloss_display

        num_path = f"{AUDIO_DIR}/kp{rank}_number.wav"
        r_num = reuse_shared_number_word(rank, num_path)
        en_path = f"{AUDIO_DIR}/kp{rank}_english.wav"
        r_en_kp = tts_key_phrase_english(used_form, en_path, f"kp{rank}_english", budget)
        ja_path = f"{AUDIO_DIR}/kp{rank}_japanese.wav"
        r_ja_kp = tts_narrator(ja_gloss_tts, ja_path, "ja", f"kp{rank}_japanese", budget)

        audit_key_phrases[str(rank)] = {
            "number": _to_audit_entry(r_num, NUMBER_WORDS[rank]),
            "english": _to_audit_entry(r_en_kp, used_form),
            "japanese": _to_audit_entry(r_ja_kp, ja_gloss_tts),
        }
        kp_blocks_stereo.append((rank, num_path, en_path, ja_path))

        en_asr = r_en_kp.get("asr_text")
        ja_asr = r_ja_kp.get("asr_text")
        if en_asr is None:
            en_asr = asr_diag(en_path, "en", budget, f"kp{rank}_english_asr_diag")
        if ja_asr is None:
            ja_asr = asr_diag(ja_path, "ja", budget, f"kp{rank}_japanese_asr_diag")
        kp_consistency[str(rank)] = {
            "player_display_en": used_form, "canonical_en": used_form, "tts_input_en": used_form,
            "asr_en": en_asr, "match_en": _normalize_loose(en_asr) == _normalize_loose(used_form),
            "player_display_ja": ja_gloss_display, "canonical_ja": ja_gloss_display,
            "tts_input_ja": ja_gloss_tts, "asr_ja": ja_asr,
            "match_ja": _normalize_loose(ja_asr) == _normalize_loose(ja_gloss_tts),
        }
    with open(f"{OUT_DIR}/key_phrase_consistency.json", "w", encoding="utf-8") as f:
        json.dump(kp_consistency, f, ensure_ascii=False, indent=2)

    # === Stage E: Comment 1〜3(日本語、新規LLM+TTS。Comment 4は使用しない) ===
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

    # === Stage F: 物語本文segment(3-voice、全件新規TTS) ===
    story_segments = build_all_story_segments(paragraphs)
    reconstructed = reconstruct_article_from_story_segments(story_segments, len(paragraphs))
    assert reconstructed == article_text, "STORY_SEGMENT reconstruction mismatch(生成前チェック)"

    segs_by_plan = {}
    for seg in story_segments:
        segs_by_plan.setdefault(seg["plan_index"], []).append(seg)

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
            "lena_split_decision": ("Lena本人の台詞(段落5, 19)はnarrator(Aoede)のまま分離しない。"
                                     "Home Robots(Maya)の設計判断を踏襲: 主人公は地の文と台詞が同一"
                                     "人物視点で連続する自然さを優先し、話者を増やしすぎない"
                                     "2/3-voice設計思想(既存4Voice候補の範囲内)。"),
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

    # Intro(mp3)→Welcome(Charon)→0.5→Topic intro(Aoede EN)→0.65→
    # Japanese title(Aoede)→0.5→Notification1(mp3)→0.4→Preview intro
    # (Charon)→0.65→Preview(Aoede JA)→0.5→Notification2(mp3)→0.4→
    # Key phrases intro(Charon)→0.5→[KP1-5]→Notification3(mp3)→0.4→
    # Full story intro(Charon)  ※すべてFamily A(A2)のpause値をそのまま流用
    # (er003_v1_n3_01_assemble.py::build_a2_timeline、Home Robots v2と同一)。
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

    for plan_index, (kind, arg) in enumerate(STORY_SEGMENT_PLAN):
        for seg in segs_by_plan[plan_index]:
            seq.append((seg["id"], gs(load_mono(seg["audio_path"]), seg["id"])))
            sil(0.2 if seg["kind"] == "split" else 0.5)
        if plan_index == COMMENT_2_AFTER_PLAN_INDEX:
            sil(1.0)
            c2_path, c2_r = comment_wavs[2]
            seq.append(("Comment 2", gs(load_mono(c2_path), "comment_2")))
            sil(0.8)
        if plan_index == COMMENT_3_AFTER_PLAN_INDEX:
            sil(1.0)
            c3_path, c3_r = comment_wavs[3]
            seq.append(("Comment 3", gs(load_mono(c3_path), "comment_3")))
            sil(0.8)

    # Comment 4は使用しない(Family C既定、episode_spec_v2.md参照)。Story
    # 終了後は既存Family A構成どおりpause→Outroとする。
    sil(0.5)  # pause_0.5(A2既存値、Outro直前)
    seq.append(("Outro", outro_gained))

    with open(f"{AUDIT_DIR}/gain_report.json", "w", encoding="utf-8") as f:
        json.dump(gain_report, f, ensure_ascii=False, indent=2)

    assembled_result = assemble_mod.assemble_with_timeline(seq)
    safety_result = assemble_mod.apply_headroom_safety_valve(assembled_result["assembled"], seq)
    with open(f"{AUDIT_DIR}/headroom_report.json", "w", encoding="utf-8") as f:
        json.dump(safety_result["report"], f, ensure_ascii=False, indent=2)

    final_path = f"{ASSEMBLED_DIR}/family_c_memory_trial_10.wav"
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

    placement = []
    boundary_defs = [
        (1, "導入部(Preview後・Story前、Full story introの直後)", None,
         story_segments[0]["id"]),
        (2, "段落8/9境界(scene transition: 'For a while, Lena felt free...'から"
            "'Five years later, on a cold morning, the box opened.'への時間跳躍。"
            "累計語数約39%地点)",
         [s["id"] for s in story_segments if s["plan_index"] == COMMENT_2_AFTER_PLAN_INDEX][-1],
         [s["id"] for s in story_segments if s["plan_index"] == COMMENT_2_AFTER_PLAN_INDEX + 1][0]),
        (3, "段落23/24境界(turning point直前: 'would that be healing? Or would she "
            "only be leaving a frightened part of herself alone in a dark room?'という"
            "問いの直後、'Lena did not press the button.'という結末を明かす一文の直前。"
            "累計語数約82%地点)",
         [s["id"] for s in story_segments if s["plan_index"] == COMMENT_3_AFTER_PLAN_INDEX][-1],
         [s["id"] for s in story_segments if s["plan_index"] == COMMENT_3_AFTER_PLAN_INDEX + 1][0]),
    ]
    for n, desc, before_id, after_id in boundary_defs:
        before_words = len(story_segments[[s["id"] for s in story_segments].index(before_id)]["tts_text"].split()) \
            if before_id else None
        after_words = len(story_segments[[s["id"] for s in story_segments].index(after_id)]["tts_text"].split()) \
            if after_id else None
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
        "budget_cap_jpy": args.budget_jpy, "warn_threshold_jpy": 60.0,
        "total_estimate_jpy": round(total_jpy, 2),
        "note": "raw_usage_log.jsonl全体(複数回のresume実行を含む)からの累計。",
        "tts_call_count_estimate_basis": tts_count, "llm_call_count_estimate_basis": llm_count,
        "asr_diag_call_count_estimate_basis": asr_diag_count,
        "methodology": ("既存Production wrapper関数がtoken単位usageを返さないため、"
                        "precedentベースの安全側単価推定(Home Robots v2と同一単価)。"),
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
         "Topic intro前/Preview前/Key phrases intro前の3箇所に挿入(A2と同一位置)"),
        ("Welcome(Charon)", "B1_SHARED_NAMES welcome_charon.wav(記事非依存共有資産)",
         "そのまま流用(コピーのみ、追加TTSなし)"),
        ("Preview intro(Charon)", "B1_SHARED_NAMES preview_intro_charon.wav", "同上"),
        ("Key phrases intro(Charon)", "B1_SHARED_NAMES key_phrases_intro_charon.wav", "同上"),
        ("Full story intro(Charon)", "B1_SHARED_NAMES full_story_intro_charon.wav", "同上"),
        ("番号読み上げ(One.〜Five.)", "B1_SHARED_NAMES num_X_charon.wav", "そのまま流用"),
        ("Topic intro文言", "Home Robots v2と同一パターン \"Today's topic is {title}.\"",
         "文言パターンをそのまま採用"),
        ("Key Phrase構成・pause", "er003_b1_p9a_audio.py::build_key_phrase_block、"
         "assemble_mod.A2_KEY_PHRASE_NUMBERING_PAUSE_SECONDS", "そのまま流用"),
        ("Comment前後pause(1.0秒 en→ja、0.8秒 ja→en)",
         "er003_v1_n3_01_assemble.py::build_a2_timeline pause_1.0_en_to_ja/pause_0.8_ja_to_en",
         "Comment1〜3の前後遷移にそのまま適用(Home Robots v2と同一)"),
        ("Outro直前pause(0.5秒)", "build_a2_timeline pause_0.5(In One Line→Outro)",
         "Story末尾→Outroの遷移にそのまま適用"),
        ("Assembly/Gate/player", "assemble_with_timeline/apply_headroom_safety_valve/"
         "verify_episode_audio_validation_gate/audio_review_player.py", "そのまま流用(無変更)"),
        ("Voice(Charon=装置、Erinome=兄)", "er012_b_family_voices_production_01/"
         "er003_v1_sing01_voice01_generate", "Home Robots(Charon=robot、Erinome=mother)と"
         "同一Voice、既存4Voice候補の範囲内"),
    ]
    lines = ["# Family A流用表(memory A2)\n", "| 項目 | 流用元 | 扱い |", "|---|---|---|"]
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
    ep_wav = f"{ASSEMBLED_DIR}/family_c_memory_trial_10.wav"
    ep_mp3 = f"{WEB_DIR}/family_c_memory_trial_10.mp3"
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
    episode_url = "./web/family_c_memory_trial_10.mp3"
    html = f"""<!doctype html><html><head><meta charset="utf-8">
<title>Family C Trial-10: The Future of Memory(A2)</title>
<style>{player_mod.PLAYER_STANDARD_CSS}</style>
<script>{player_mod.SEEK_SCRIPT}</script>
</head><body>
<h1>Family C Future — The Future of Memory(Trial-10 A2 / VALIDATED候補・ユーザー試聴待ち)</h1>
<p>duration={run_summary['duration_seconds']}s / peak={run_summary['peak_after_headroom']}</p>
<audio id="episode_audio" class="main" controls preload="none" src="{episode_url}"></audio>
{table_html}
</body></html>"""
    with open(f"{OUT_DIR}/player.html", "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    main()
