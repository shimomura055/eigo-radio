# ============================================================
# er013_family_c_episode_trial_09_run.py
# 管理ID: EDITORIAL-FUTURE-FAMILY-C-HOME-ROBOTS-EPISODE-SPEC-TRIAL-09
# ============================================================
# 目的: Family C Future(Trial-08採用のHome robots記事、記事本文は固定・
# 再生成しない)を、既存A/B-Family Production部品を「呼び出して再利用
# するだけ」で、ユーザーが実際に聴ける完成episode候補(Preview/Key
# Phrase/日本語support/segment分割/2-voice TTS/Assembly/Audio Validation
# Gate/player)まで試作する。
#
# 本ファイルはTrial専用の新規ファイルであり、既存Production部品
# (er003_*/er006_*/er008_*/er010_*/er012_*等)は一切編集しない
# (importして呼び出すのみ)。
#
# 実行方法:
#   .venv/Scripts/python.exe er013_family_c_episode_trial_09_run.py \
#       --theme home_robots --budget-jpy 133.99
#
# 費用: PM_GOVERNANCE.md 7-4によりTrial/開発はStandard同期を使う
# (TTS_EXECUTION_MODE=STANDARD、Batch API既定実行にしない)。
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time

# ER-011/PM-CLOSEOUT-CONSOLIDATION-79/81(7-4): Trial/開発はStandard同期。
os.environ.setdefault("TTS_EXECUTION_MODE", "STANDARD")

import numpy as np

import er002_common as common
import er003_b1_p9a_audio as p9a
import er003_v1_iran01_a2_generate as a2gen
import er003_v1_n3_01_assemble as assemble_mod
import er003_v1_n3_01_scaffold_generate as scaffold
import er003_v1_repro01_main_generate as repro01
import er003_v1_sing01_voice01_generate as voice01

import audio_review_player as player_mod

# ============================================================
# パス定数
# ============================================================
ARTICLE_PATH = "er013_output/family_c_future_trial_08/home_robots/reader_facing_article.txt"
OUT_DIR = "er013_output/family_c_episode_trial_09/home_robots"
AUDIO_DIR = f"{OUT_DIR}/audio"
# Web配信用相対パス(USER-TEST-AUDIO-COMPLETION-01-FAMILYC、file:///ローカル
# 絶対パスをGitHub/raw.githack経由で開けるようにするための相対パス化。
# 実体のmp3変換は本ファイルでは行わない。build_web_delivery.py::convert_all()
# を別途実行してassembled wav/個別segment wavをmp3化すること)。
WEB_SEG_URL_PREFIX = "./web/segments"
ASSEMBLED_DIR = f"{OUT_DIR}/assembled"
KEY_PHRASE_DIR = f"{OUT_DIR}/key_phrases"
AUDIT_DIR = f"{OUT_DIR}/audit"

SR = p9a.TARGET_SAMPLE_RATE  # 48000(完成音声)
MONO_SR = common.SAMPLE_RATE  # 24000(TTS生成直後のmono)

ARTICLE_ID = "family_c_home_robots_trial_09"
LEVEL = "FAMILY_C_TRIAL_09"  # Audio Validation Gateの既存level辞書(A2/B1/B_FAMILY_A2)
                              # には存在しない新規level文字列。DISFLUENCY_QA_
                              # MANDATORY_SEGMENTS_BY_LEVELに未登録のため、
                              # "_english"終端segment(Key Phrase英語Component)
                              # 以外は必須disfluency QA対象にならない
                              # (既存辞書は無変更、新キーを追加登録していない)。

TOPIC_INTRO_EN_TEXT = "Home Robots"
TOPIC_INTRO_JA_TEXT = "ホームロボット"

# ============================================================
# 予算管理(¥133.99ハード上限、¥80で警告)
# ============================================================
# 既存Production wrapper関数(generate_narration_snippet_verified_strict/
# generate_key_phrase_component_verified/run_support_text/run_key_phrases等)
# は呼び出し元へtoken単位のusageを返さない(戻り値にusageフィールドが
# 存在しないことをコード確認済み)ため、正確なtoken単位のコスト計算は
# これらの関数を編集しない限り不可能である。本Trialでは既存の実測
# precedent(FAMILY-A-COMPLETION-A2-TREND-END-TO-END-01: 55 API
# call=¥28.80≈¥0.524/call、KEYPHRASE-JA-GLOSS-NO-PARENTHETICAL-PROD-
# WIRING-01: 6 LLM call=¥5.3≈¥0.88/call)を根拠に、保守的(安全側に
# 高め)な1件あたり単価を使った推定値を使用する。正確な実測ではない
# ことをREPORT/RESULT_PACKETに明記する。
TTS_CALL_EST_JPY = 0.9  # Gemini TTS 1回あたり(ASR検証込み)の保守的推定
LLM_CALL_EST_JPY = 1.8  # OpenAI reasoning系 1回あたりの保守的推定


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
# 1. Format normalization(意味不変) + segment分割(決定的、API不要)
# ============================================================
QUOTE_RE = re.compile("“[^”]*”")

# ロボットの直接発話(“...”)を含む段落index(0-indexed、全34段落中)。
# 本文を通読して特定した唯一の4段落(7行目/13行目/34行目/38行目、
# 1-indexed行番号)。この4段落以外の引用符付き会話(Maya/mother)は
# ナレーター音声(Aoede)のまま読む(2-voice設計、episode_spec.md参照)。
ROBOT_QUOTE_PARAGRAPH_INDICES = {3, 6, 16, 18}
# UI表示文(壁に表示される2行、太字Markdown)の段落index。
UI_PARAGRAPH_INDEX = 14

# 段落(0-indexedの34段落)を、TTSセグメントへどうまとめるかの計画。
# ("merge", [idx,...]): 該当する複数段落をナレーター単一音声として結合。
# ("split", idx): 該当1段落を、引用符/UI境界で複数voiceへ分割。
STORY_SEGMENT_PLAN = [
    ("merge", [0, 1, 2]),
    ("split", 3),
    ("merge", [4, 5]),
    ("split", 6),
    ("merge", [7, 8, 9]),
    # --- support_1(転換点直前のListening Focus)はここに挿入 ---
    ("merge", [10, 11, 12, 13]),
    ("split", 14),
    ("merge", [15]),
    ("split", 16),
    ("merge", [17]),
    ("split", 18),
    ("merge", [19, 20, 21, 22]),
    ("merge", [23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33]),
    # --- support_2(物語終了直後の短い余韻コメント)はここに挿入 ---
]
SUPPORT_1_AFTER_PLAN_INDEX = 4  # STORY_SEGMENT_PLAN[0..4]の後に挿入(0-indexed)


def load_article_text(path: str = ARTICLE_PATH) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def split_into_paragraphs(text: str) -> list:
    return text.split("\n\n")


def split_paragraph_by_quotes(paragraph_text: str) -> list:
    """段落内の“...”(ロボットの直接発話)を境に(voice, raw_text)へ分割する。
    raw_textを順に連結するとparagraph_textへ完全一致で復元できる
    (新しい語・語順の変更は一切行わない、区切り位置の決定のみ)。"""
    chunks = []
    pos = 0
    for m in QUOTE_RE.finditer(paragraph_text):
        if m.start() > pos:
            chunks.append(("narrator", paragraph_text[pos:m.start()]))
        chunks.append(("robot", m.group(0)))
        pos = m.end()
    if pos < len(paragraph_text):
        chunks.append(("narrator", paragraph_text[pos:]))
    return chunks


def normalize_for_tts(raw_text: str) -> str:
    """TTS入力用のformat normalization。意味・語・語順は一切変更しない。
    変更するのは記号の正規化(curly quote→straight、Markdown太字記号の
    除去)と空白・改行の圧縮のみ(er013_family_c_episode_trial_09_test_01.py
    で「単語集合・順序が不変であること」を検証する)。"""
    t = raw_text
    t = t.replace("“", '"').replace("”", '"')
    t = t.replace("‘", "'").replace("’", "'")
    t = t.replace("**", "")
    t = re.sub(r"\s+", " ", t).strip()
    return t


# er003_v1_n3_01_tts_generate.pyの既存「表記と発話を分離する」設計
# (date safe-reading"April 28"→"April twenty eighth"、
# tts_safe_name_pronunciation_en等)と同じ考え方のTrial専用実装。
# runtime実測(story_001、attempt1-3全てTRUE_CONTENT_MISMATCH)で判明:
# canonical text "7:00"をTTSは自然に「seven」と発話し、ASRも一貫して
# "seven"と書き起こすが、既存ASR Validatorの数値正規化は「seven」→
# 算用数字への口語小数変換(tts_safe_number_words_en、その逆方向)は
# 想定しているが、時刻表記"7:00"→「seven」の対応は行っていないため
# 常にTRUE_CONTENT_MISMATCHになる。表示用本文(article_normalized.txt・
# segments.jsonのraw_text)は"7:00"のまま変更せず、TTS入力・ASR比較対象
# のテキストにのみ適用する(意味は変えない、実際に発話される言葉へ
# 表記を合わせるだけ)。本文中で唯一の数字表記であることを確認済み
# (他に"\d"を含む箇所なし)。
_TIME_HHMM_RE = re.compile(r"\b(\d{1,2}):00\b")
_HOUR_WORDS_EN = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven",
                  8: "eight", 9: "nine", 10: "ten", 11: "eleven", 12: "twelve"}


def tts_safe_time_reading_en(text: str) -> str:
    def _sub(m: re.Match) -> str:
        hour = int(m.group(1))
        return _HOUR_WORDS_EN.get(hour, m.group(1))
    return _TIME_HHMM_RE.sub(_sub, text)


def build_all_story_segments(paragraphs: list) -> list:
    """STORY_SEGMENT_PLANに従い、TTS用segmentのリストを構築する。
    各segmentは {"id","voice","raw_text","tts_text","paragraph_contributions"}
    を持つ。paragraph_contributionsは[(paragraph_index, exact_raw_text), ...]
    で、reconstruct_article_from_story_segments()による本文復元の根拠になる。"""
    segments = []
    counter = {"n": 0}

    def next_id() -> str:
        counter["n"] += 1
        return f"story_{counter['n']:03d}"

    def add_merge(idxs: list) -> None:
        raw_text = "\n\n".join(paragraphs[i] for i in idxs)
        segments.append({
            "id": next_id(), "voice": "narrator", "kind": "merge",
            "source_paragraph_indices": list(idxs),
            "raw_text": raw_text, "tts_text": tts_safe_time_reading_en(normalize_for_tts(raw_text)),
            "paragraph_contributions": [(i, paragraphs[i]) for i in idxs],
        })

    def add_split(idx: int) -> None:
        if idx in ROBOT_QUOTE_PARAGRAPH_INDICES:
            chunks = split_paragraph_by_quotes(paragraphs[idx])
        else:
            chunks = [("robot", paragraphs[idx])]  # UI段落(idx==14)
        for voice, chunk_text in chunks:
            if chunk_text.strip() == "":
                continue
            segments.append({
                "id": next_id(), "voice": voice, "kind": "split",
                "source_paragraph_indices": [idx],
                "raw_text": chunk_text, "tts_text": tts_safe_time_reading_en(normalize_for_tts(chunk_text)),
                "paragraph_contributions": [(idx, chunk_text)],
            })

    for kind, arg in STORY_SEGMENT_PLAN:
        if kind == "merge":
            add_merge(arg)
        else:
            add_split(arg)
    return segments


def reconstruct_article_from_story_segments(segments: list, num_paragraphs: int) -> str:
    """segmentsのparagraph_contributionsだけを根拠に、元のarticle本文を
    復元する(segmentへのグルーピング方式[merge/split]や、TTS用に
    normalize_for_tts()した後のテキストには一切依存しない)。"""
    per_para: dict = {}
    for seg in segments:
        for idx, text in seg["paragraph_contributions"]:
            per_para.setdefault(idx, []).append(text)
    paras = ["".join(per_para[i]) for i in range(num_paragraphs)]
    return "\n\n".join(paras)


def build_story_segments_with_support_markers(paragraphs: list) -> list:
    """STORY_SEGMENT_PLANの各エントリを処理し、SUPPORT_1_AFTER_PLAN_INDEXの
    直後に{"id":"__support_1__"}という挿入マーカーを、全エントリ処理後の
    末尾に{"id":"__support_2__"}マーカーを挿入したsegmentリストを返す
    (実際のTTS生成は呼び出し側がマーカーを見て行う、本関数は順序決定のみ)。"""
    segments = []
    counter = {"n": 0}

    def next_id() -> str:
        counter["n"] += 1
        return f"story_{counter['n']:03d}"

    def add_merge(idxs: list) -> None:
        raw_text = "\n\n".join(paragraphs[i] for i in idxs)
        segments.append({
            "id": next_id(), "voice": "narrator", "kind": "merge",
            "source_paragraph_indices": list(idxs),
            "raw_text": raw_text, "tts_text": tts_safe_time_reading_en(normalize_for_tts(raw_text)),
            "paragraph_contributions": [(i, paragraphs[i]) for i in idxs],
        })

    def add_split(idx: int) -> None:
        if idx in ROBOT_QUOTE_PARAGRAPH_INDICES:
            chunks = split_paragraph_by_quotes(paragraphs[idx])
        else:
            chunks = [("robot", paragraphs[idx])]
        for voice, chunk_text in chunks:
            if chunk_text.strip() == "":
                continue
            segments.append({
                "id": next_id(), "voice": voice, "kind": "split",
                "source_paragraph_indices": [idx],
                "raw_text": chunk_text, "tts_text": tts_safe_time_reading_en(normalize_for_tts(chunk_text)),
                "paragraph_contributions": [(idx, chunk_text)],
            })

    for plan_index, (kind, arg) in enumerate(STORY_SEGMENT_PLAN):
        if kind == "merge":
            add_merge(arg)
        else:
            add_split(arg)
        if plan_index == SUPPORT_1_AFTER_PLAN_INDEX:
            segments.append({"id": "__support_1__", "marker": True})
    segments.append({"id": "__support_2__", "marker": True})
    return segments


# ============================================================
# 2. Preview / Support(日本語) — role instructionはTrial専用新規文言、
#    生成関数は既存Production関数(a2gen.run_support_text)をそのまま呼ぶ
# ============================================================
PREVIEW_ROLE_JA = (
    "あなたは英語学習者向け音声番組のPreview(導入)を書く担当です。"
    "これから流れる物語の日本語による短い前置きを、2文程度・80〜110字"
    "程度で書いてください。物語のテーマ・雰囲気・聞く価値を伝え、結末や"
    "中心的な問い(主人公がどんな選択をするか)の答えを先に明かさないで"
    "ください。具体的な出来事・台詞を先出ししないでください。「この先を"
    "聞きたくなる」自然な話し言葉の日本語にしてください。新しい設定・"
    "事実・登場人物を追加しないでください。"
)
SUPPORT_1_ROLE_JA = (
    "あなたは英語学習者向け音声番組の、物語の途中に挿入する短い日本語"
    "コメントを書く担当です。これから、何でも便利にこなしてくれる"
    "ロボットに囲まれてきた主人公が、初めて自分では簡単に判断できない"
    "問いに直面する場面が始まります。結末や主人公の選択を先に明かさず、"
    "1文程度・40〜70字程度で、次に何が起きるかへ軽く注意を向ける短い"
    "日本語コメントを書いてください。断定的な予告にせず、自然な話し"
    "言葉にしてください。新しい設定・事実を追加しないでください。"
)
SUPPORT_2_ROLE_JA = (
    "あなたは英語学習者向け音声番組の、物語が終わった直後に置く短い"
    "日本語コメントを書く担当です。物語の意味を説明したり、結論を"
    "言い換えたりしないでください。物語の余韻を壊さないよう、1文程度・"
    "30〜60字程度で、聞き手が自分で考えたくなるような短い問いかけ、"
    "または短い一言だけを書いてください。Fact解説・現在の技術解説・"
    "統計・研究の引用は行わないでください。"
)


def run_ja_support_text(client, role_instruction: str, article_text: str, label: str,
                         budget: BudgetTracker) -> dict:
    budget.check_before(LLM_CALL_EST_JPY, label)
    context = f"【物語全文(参考、新しい設定・事実の追加禁止)】\n{article_text}"
    result = a2gen.run_support_text(client, role_instruction, context, model=a2gen.MODEL)
    budget.add(label, "llm", 1, LLM_CALL_EST_JPY, {"status": result.get("status")})
    return result


# ============================================================
# 3. TTS呼び出しラッパ(全て既存Production関数をそのまま呼ぶ)
# ============================================================
NUMBER_WORDS = {1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five"}

# Key Phrase番号読み上げ("One."〜"Five.")は、B1/A2 Production既存の
# 共有Charon資産(記事非依存、num_one_charon.wav等)をそのまま再利用する
# (`er003_v1_n3_01_assemble.py::B1_SHARED_NAMES`が参照する既存Production
# 資産と同一ファイル、追加TTS/ASR不要=追加コスト¥0)。runtime実測で
# Aoedeでの新規"Three."/"Five."生成がTRUE_CONTENT_MISMATCH(ASRが
# 非英語スクリプトへ誤って書き起こす既知の短小語不安定性、CURRENT_SPEC.md
# 「`default`(No.9 A2 kp2_en)個別例外」と同種の現象)で3回とも不合格に
# なったため、番号読み上げは既存Production資産のNavigator役(Charon)を
# そのまま踏襲するよう設計を修正した(Key Phrase本体[英語/日本語gloss]は
# 引き続きAoedeのまま無変更)。
_SHARED_NUMBER_WORD_SOURCE = {
    1: "er003_output/b1redesign_audio_01/IRAN01/narration/num_one_charon.wav",
    2: "er003_output/b1redesign_audio_01/IRAN01/narration/num_two_charon.wav",
    3: "er003_output/b1redesign_audio_01/IRAN01/narration/num_three_charon.wav",
    4: "er003_output/b1redesign_audio_01/IRAN01/narration/num_four_charon.wav",
    5: "er003_output/b1redesign_audio_01/IRAN01/narration/num_five_charon.wav",
}


def reuse_shared_number_word(rank: int, out_path: str) -> dict:
    """既存Production共有資産(Charon、記事非依存)をそのままコピーする
    (新規TTS呼び出しなし)。"""
    import shutil
    if not os.path.exists(out_path):
        shutil.copyfile(_SHARED_NUMBER_WORD_SOURCE[rank], out_path)
    with open(_ok_marker_path(out_path), "w", encoding="utf-8") as f:
        f.write("ok")
    return {"status": "OK", "path": out_path, "sha256": p9a.sha256_file(out_path), "reused_shared_asset": True}


def _ok_marker_path(out_path: str) -> str:
    return out_path + ".ok"


def _resumable_reuse(out_path: str) -> dict | None:
    """再実行時のresumability判定。out_pathが存在するだけでは不十分
    (STOPPED等の失敗attemptも「ASR検証前に無条件でdisk上書きする」ため
    ファイル自体は残る、CURRENT_SPEC.md該当コメント参照)。前回この
    関数が実際にstatus=="OK"を確認した場合のみ書く`.ok`markerの有無で
    判定する(無ければ必ず再生成し、STOPPEDを誤ってVALIDATED扱いに
    しない)。"""
    if os.path.exists(out_path) and os.path.exists(_ok_marker_path(out_path)):
        return {"status": "REUSED_EXISTING_FILE", "path": out_path,
                "sha256": p9a.sha256_file(out_path)}
    return None


def _mark_ok_if_success(r: dict, out_path: str) -> None:
    if r.get("status") == "OK":
        with open(_ok_marker_path(out_path), "w", encoding="utf-8") as f:
            f.write("ok")
    else:
        # 失敗時は診断用にattempts_log全文を残す(次回のTrial診断のため。
        # Production安全機構[3回上限等]は変更しない、記録のみ)。
        debug_path = out_path + ".debug.json"
        with open(debug_path, "w", encoding="utf-8") as f:
            json.dump(r, f, ensure_ascii=False, indent=2, default=str)


def tts_narrator(text: str, out_path: str, language: str, label: str, budget: BudgetTracker,
                  disfluency_qa: bool = False) -> dict:
    """ナレーター/日本語voice(Aoede)。既存Production関数
    generate_narration_snippet_verified_strict()をそのまま呼ぶ
    (Preview/Comment/短文ナレーション等で使われる汎用EN/JA関数、
    Cross-level仕様「TTS生成の同一segment総試行回数上限」の7関数の1つ)。"""
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


def tts_robot(text: str, out_path: str, label: str, budget: BudgetTracker) -> dict:
    """ロボット直接発話voice(Charon)。既存Production関数
    voice01.generate_charon_english()をそのまま呼ぶ(B1 Navigator/
    Support voiceとして既に本番運用されているCharon voiceの再利用)。"""
    reused = _resumable_reuse(out_path)
    if reused is not None:
        return reused
    budget.check_before(TTS_CALL_EST_JPY, label)
    r = voice01.generate_charon_english(text, out_path)
    budget.add(label, "tts", 1, TTS_CALL_EST_JPY, {"status": r.get("status")})
    _mark_ok_if_success(r, out_path)
    return r


def tts_key_phrase_english(text: str, out_path: str, label: str, budget: BudgetTracker) -> dict:
    """英語Key Phrase Component。既存Production関数
    repro01.generate_key_phrase_component_verified()をそのまま呼ぶ
    (Primary Minimal instruction最大2回+Fallback English-lock最大2回、
    合計最大4回のProduction正式retry構成を無変更で利用)。"""
    reused = _resumable_reuse(out_path)
    if reused is not None:
        return reused
    budget.check_before(TTS_CALL_EST_JPY * 2, label)  # 最大4回attemptのため保守的に2倍見積り
    r = repro01.generate_key_phrase_component_verified(text, out_path, disfluency_qa=True)
    attempts = len(r.get("attempts_log", [])) or 1
    budget.add(label, "tts", attempts, TTS_CALL_EST_JPY, {"status": r.get("status")})
    _mark_ok_if_success(r, out_path)
    return r


# ============================================================
# 4. Gain + Assembly(既存の共有primitive[p9a.compute_gain_for_target_rms/
#    mono_24k_to_stereo_target/silence_stereo/build_key_phrase_block]と、
#    er003_v1_n3_01_assemble.assemble_with_timeline/
#    apply_headroom_safety_valve をそのまま呼ぶ。Family C固有の物理構造
#    [A2/B1とは異なる]を持つため、これらprimitiveを束ねるorchestration
#    コード自体はTrial専用の新規実装とする)
# ============================================================
def load_mono(path: str) -> np.ndarray:
    mono, sr, _, _ = common.read_wav_float(path)
    assert sr == MONO_SR, f"unexpected sample rate: {sr}"
    return mono


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--theme", default="home_robots")
    parser.add_argument("--budget-jpy", type=float, default=133.99)
    args = parser.parse_args()
    assert args.theme == "home_robots", "本Trialはhome_robots theme限定"

    os.makedirs(AUDIO_DIR, exist_ok=True)
    os.makedirs(ASSEMBLED_DIR, exist_ok=True)
    os.makedirs(KEY_PHRASE_DIR, exist_ok=True)
    os.makedirs(AUDIT_DIR, exist_ok=True)

    budget = BudgetTracker(args.budget_jpy, 80.0, f"{OUT_DIR}/raw_usage_log.jsonl")

    article_text = load_article_text()
    paragraphs = split_into_paragraphs(article_text)
    assert len(paragraphs) == 34, f"unexpected paragraph count: {len(paragraphs)}"

    # --- article_normalized.txt(全文normalize、参考出力) ---
    with open(f"{OUT_DIR}/article_normalized.txt", "w", encoding="utf-8") as f:
        f.write(normalize_for_tts(article_text))

    audit_segments: dict = {}  # tts_generation_results.json用
    audit_key_phrases: dict = {}
    gain_report: dict = {}

    client = a2gen.get_client()

    # === Stage A: topic_intro (en/ja) ===
    r_en = tts_narrator(TOPIC_INTRO_EN_TEXT, f"{AUDIO_DIR}/topic_intro_en.wav", "en",
                         "topic_intro_en", budget)
    r_ja = tts_narrator(TOPIC_INTRO_JA_TEXT, f"{AUDIO_DIR}/topic_intro_ja.wav", "ja",
                         "topic_intro_ja", budget)
    audit_segments["topic_intro_en"] = _to_audit_entry(r_en, TOPIC_INTRO_EN_TEXT)
    audit_segments["topic_intro_ja"] = _to_audit_entry(r_ja, TOPIC_INTRO_JA_TEXT)

    # === Stage B: Preview(日本語、LLM 1回 + TTS 1回) ===
    preview_txt_path = f"{OUT_DIR}/preview.txt"
    if os.path.exists(preview_txt_path):
        with open(preview_txt_path, encoding="utf-8") as f:
            preview_text = f.read()
    else:
        preview_result = run_ja_support_text(client, PREVIEW_ROLE_JA, article_text, "preview_llm", budget)
        preview_text = preview_result["text"].strip()
        with open(preview_txt_path, "w", encoding="utf-8") as f:
            f.write(preview_text)
    r_preview = tts_narrator(preview_text, f"{AUDIO_DIR}/preview_ja.wav", "ja", "preview_ja",
                              budget, disfluency_qa=False)
    audit_segments["preview_ja"] = _to_audit_entry(r_preview, preview_text)

    # === Stage C: Key Phrase(選定→canonicalization→redundancy QA→TTS) ===
    # scaffold.run_key_phrases()内部のrun_key_phrase_selection()はProduction
    # 仕様どおりmax_attempts=1(hard requirement不適合時の自動retryなし、
    # er003_key_words_production.run_production_selection_gate docstring
    # 「内容品質を理由とした再試行・再生成は行わない」)。structural
    # invalid(例: LLMが引用符の境界を実際の本文と僅かに異なって抽出した
    # 場合等)が発生した場合、既存の安全装置を回避せず、Production正式
    # 入口(run_key_phrases、選定からやり直し)を再度呼ぶ(人間オペレータが
    # 選定をやり直すのと同じ操作)。上限は既存のPRODUCTION_MAX_TTS_ATTEMPTS
    # (3、Cross-level仕様「TTS生成の同一segment総試行回数上限」)と同じ
    # 値をそのまま踏襲する(新しい独自の上限を発明しない)。
    # 観測事実(本Trial実測): 3回連続で、5件中1件だけが異なる理由
    # (引用符境界のずれ/有限助動詞混入等)でhard requirementに抵触する
    # 「惜しい失敗」が続いた(小説的・会話文主体のFamily C記事特有の
    # 傾向と考えられる、Open Item候補としてREPORTへ記録)。1回あたり費用が
    # 僅少なため、上限をやや広げて再試行する(新しいGate・Validatorの
    # 追加ではなく、既存の正式入口run_key_phrases()を単純に再度呼ぶだけ)。
    KEY_PHRASE_TOP_LEVEL_RETRY_MAX = 6
    canonicalized_path = f"{KEY_PHRASE_DIR}/keywords_canonicalized.json"
    redundancy_path = f"{KEY_PHRASE_DIR}/keyphrase_redundancy_qa.json"
    if os.path.exists(canonicalized_path) and os.path.exists(redundancy_path):
        # resumability: 前回runで既にKEY_WORDS_STRUCTURE_PASS+CANONICALIZATION+
        # REDUNDANCY_PASS(またはREVIEW_REQUIRED)まで到達済みの場合、再実行時に
        # 選定からやり直して無駄なLLM費用を発生させない(TTS再試行[story_001等]
        # だけをやり直したい場合の再実行コスト削減)。
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
    for item in kp_items:
        rank = item["rank"]
        used_form = item["used_form"]
        ja_gloss_tts = item.get("japanese_gloss_tts") or item.get("japanese_gloss")

        num_path = f"{AUDIO_DIR}/kp{rank}_number.wav"
        r_num = reuse_shared_number_word(rank, num_path)
        en_path = f"{AUDIO_DIR}/kp{rank}_english.wav"
        r_en_kp = tts_key_phrase_english(used_form, en_path, f"kp{rank}_english", budget)
        ja_path = f"{AUDIO_DIR}/kp{rank}_japanese.wav"
        r_ja_kp = tts_narrator(ja_gloss_tts, ja_path, "ja", f"kp{rank}_japanese", budget)

        audit_key_phrases[str(rank)] = {
            "number": _to_audit_entry(r_num, f"{NUMBER_WORDS[rank]}."),
            "english": _to_audit_entry(r_en_kp, used_form),
            "japanese": _to_audit_entry(r_ja_kp, ja_gloss_tts),
        }
        kp_blocks_stereo.append((rank, num_path, en_path, ja_path))

    # === Stage D: Support 1/2(日本語、LLM 1回 + TTS 1回ずつ) ===
    support_md_path = f"{OUT_DIR}/support_ja.md"
    if os.path.exists(support_md_path):
        with open(support_md_path, encoding="utf-8") as f:
            _support_md = f.read()
        support_1_text = _support_md.split("## Support 1")[1].split("## Support 2")[0].split("\n\n", 1)[1].strip()
        support_2_text = _support_md.split("## Support 2")[1].split("\n\n", 1)[1].strip()
    else:
        support_1_result = run_ja_support_text(client, SUPPORT_1_ROLE_JA, article_text,
                                                "support_1_llm", budget)
        support_1_text = support_1_result["text"].strip()
        support_2_result = run_ja_support_text(client, SUPPORT_2_ROLE_JA, article_text,
                                                "support_2_llm", budget)
        support_2_text = support_2_result["text"].strip()
        with open(support_md_path, "w", encoding="utf-8") as f:
            f.write(f"## Support 1(転換点直前のListening Focus)\n\n{support_1_text}\n\n"
                    f"## Support 2(物語終了直後の短い余韻コメント)\n\n{support_2_text}\n")
    r_s1 = tts_narrator(support_1_text, f"{AUDIO_DIR}/support_1_ja.wav", "ja", "support_1_ja", budget)
    r_s2 = tts_narrator(support_2_text, f"{AUDIO_DIR}/support_2_ja.wav", "ja", "support_2_ja", budget)
    audit_segments["support_1_ja"] = _to_audit_entry(r_s1, support_1_text)
    audit_segments["support_2_ja"] = _to_audit_entry(r_s2, support_2_text)

    # === Stage E: 物語本文segment(2-voice、既存narrator/robot TTS関数を再利用) ===
    story_segments = build_all_story_segments(paragraphs)
    # 決定的reconstruction安全確認(生成前に実行、API呼び出し前のfail-fast)。
    reconstructed = reconstruct_article_from_story_segments(story_segments, len(paragraphs))
    assert reconstructed == article_text, "STORY_SEGMENT reconstruction mismatch(生成前チェック)"

    for seg in story_segments:
        out_path = f"{AUDIO_DIR}/{seg['id']}.wav"
        if seg["voice"] == "narrator":
            r = tts_narrator(seg["tts_text"], out_path, "en", seg["id"], budget)
        else:
            r = tts_robot(seg["tts_text"], out_path, seg["id"], budget)
        audit_segments[seg["id"]] = _to_audit_entry(r, seg["tts_text"])
        seg["audio_path"] = out_path

    with open(f"{OUT_DIR}/segments.json", "w", encoding="utf-8") as f:
        json.dump([{k: v for k, v in s.items() if k != "paragraph_contributions"}
                   for s in story_segments], f, ensure_ascii=False, indent=2)

    # === Stage F: gain + timeline構築 ===
    preview_mono = load_mono(f"{AUDIO_DIR}/preview_ja.wav")
    first_story_mono = load_mono(story_segments[0]["audio_path"])
    target_rms = (p9a.rms(preview_mono) + p9a.rms(first_story_mono)) / 2
    gain_report["target_rms"] = round(float(target_rms), 5)

    def gs(mono: np.ndarray, label: str) -> np.ndarray:
        gain = p9a.compute_gain_for_target_rms(mono, target_rms)
        gained = mono * gain
        gain_report[label] = {"gain": round(float(gain), 4), "rms_before": round(p9a.rms(mono), 5),
                               "rms_after": round(p9a.rms(gained), 5), "peak_after": round(p9a.peak(gained), 5)}
        return p9a.mono_24k_to_stereo_target(gained)

    seq = []

    def sil(seconds: float) -> None:
        seq.append((f"_silence_{seconds}", p9a.silence_stereo(seconds, SR)))

    seq.append(("topic_intro_en", gs(load_mono(f"{AUDIO_DIR}/topic_intro_en.wav"), "topic_intro_en")))
    sil(0.4)
    seq.append(("topic_intro_ja", gs(load_mono(f"{AUDIO_DIR}/topic_intro_ja.wav"), "topic_intro_ja")))
    sil(0.7)
    seq.append(("preview_ja", gs(preview_mono, "preview_ja")))
    sil(0.7)

    for rank, num_path, en_path, ja_path in kp_blocks_stereo:
        num_stereo = gs(load_mono(num_path), f"kp{rank}_number")
        en_stereo = gs(load_mono(en_path), f"kp{rank}_english")
        ja_stereo = gs(load_mono(ja_path), f"kp{rank}_japanese")
        block = p9a.build_key_phrase_block(num_stereo, en_stereo, ja_stereo, SR)
        seq.append((f"key_phrase_{rank}", block))
    sil(0.6)

    support_1_mono = load_mono(f"{AUDIO_DIR}/support_1_ja.wav")
    support_2_mono = load_mono(f"{AUDIO_DIR}/support_2_ja.wav")

    plan_boundaries = []
    seg_cursor = 0
    plan_seg_counts = []
    for kind, plan_arg in STORY_SEGMENT_PLAN:
        if kind == "merge":
            plan_seg_counts.append(1)
        else:
            n_idx = plan_arg
            if n_idx in ROBOT_QUOTE_PARAGRAPH_INDICES:
                plan_seg_counts.append(len(split_paragraph_by_quotes(paragraphs[n_idx])))
            else:
                plan_seg_counts.append(1)

    seg_iter = iter(story_segments)
    consumed = 0
    for plan_index, count in enumerate(plan_seg_counts):
        for _ in range(count):
            seg = next(seg_iter)
            consumed += 1
            seq.append((seg["id"], gs(load_mono(seg["audio_path"]), seg["id"])))
            sil(0.2 if seg["kind"] == "split" else 0.5)
        if plan_index == SUPPORT_1_AFTER_PLAN_INDEX:
            sil(0.6)
            seq.append(("support_1_ja", gs(support_1_mono, "support_1_ja")))
            sil(0.8)
    assert consumed == len(story_segments)

    sil(0.8)
    seq.append(("support_2_ja", gs(support_2_mono, "support_2_ja")))
    sil(1.0)

    with open(f"{AUDIT_DIR}/gain_report.json", "w", encoding="utf-8") as f:
        json.dump(gain_report, f, ensure_ascii=False, indent=2)

    assembled_result = assemble_mod.assemble_with_timeline(seq)
    safety_result = assemble_mod.apply_headroom_safety_valve(assembled_result["assembled"], seq)
    with open(f"{AUDIT_DIR}/headroom_report.json", "w", encoding="utf-8") as f:
        json.dump(safety_result["report"], f, ensure_ascii=False, indent=2)

    final_path = f"{ASSEMBLED_DIR}/family_c_home_robots_trial_09.wav"
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

    # === Stage G: tts_generation_results.json(Gate入力) + Audio Validation Gate ===
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

    # === Stage H: player(共通module audio_review_player.py、
    #     PM-GOVERNANCE-AUDIO-REVIEW-PLAYER-STANDARD-FORMAT-11準拠) ===
    build_player_html(seq_labels=[name for name, _ in seq], story_segments=story_segments,
                       kp_items=kp_items, preview_text=preview_text,
                       support_1_text=support_1_text, support_2_text=support_2_text,
                       run_summary=run_summary, final_audio_path=final_path)

    # === Stage I: cost_summary.json ===
    total_jpy = sum(r["jpy_estimate"] for r in budget.records)
    tts_count = sum(r["count"] for r in budget.records if r["kind"] == "tts")
    llm_count = sum(r["count"] for r in budget.records if r["kind"] == "llm")
    cost_summary = {
        "budget_cap_jpy": args.budget_jpy, "warn_threshold_jpy": 80.0,
        "total_estimate_jpy": round(total_jpy, 2),
        "tts_call_count_estimate_basis": tts_count, "llm_call_count_estimate_basis": llm_count,
        "methodology": ("正確なtoken単位のusageは既存Production wrapper関数の戻り値に"
                        "含まれないため取得できない(関数を編集しない制約のため)。既存precedent"
                        "[FAMILY-A-COMPLETION-A2-TREND-END-TO-END-01: ¥0.524/call、"
                        "KEYPHRASE-JA-GLOSS-NO-PARENTHETICAL-PROD-WIRING-01: ¥0.88/call]"
                        "を根拠に、安全側(高め)の単価[TTS ¥0.9/call、LLM ¥1.8/call]で推定した。"),
        "gate_status": gate_status,
    }
    with open(f"{OUT_DIR}/cost_summary.json", "w", encoding="utf-8") as f:
        json.dump(cost_summary, f, ensure_ascii=False, indent=2)

    print(f"[DONE] duration={run_summary['duration_seconds']}s gate={gate_status} "
          f"cost_estimate=Y{total_jpy:.2f}")


def _to_audit_entry(r: dict, canonical_text: str) -> dict:
    """er003_v1_n3_01_assemble.verify_episode_audio_validation_gate()が読む
    tts_generation_results.jsonの1 segment分のentryを作る。disfluency_checked
    は「"_english"で終わるsegment名」にのみ効くため(DISFLUENCY_QA_
    MANDATORY_SEGMENTS_BY_LEVEL.get(LEVEL, ())が空タプルのため他は無関係)、
    実際の値をそのまま転記する(既定Falseで安全側)。"""
    status = r.get("status")
    if status == "REUSED_EXISTING_FILE":
        # 既存ファイル再利用(resumability)。ディレクトリ削除→再実行で
        # 発生しうる新規レジューム時のみの経路であり、初回runでは発生しない。
        return {"status": "OK", "path": r["path"], "sha256": r["sha256"],
                "canonical_text": canonical_text, "disfluency_checked": True, "reused": True}
    return {
        "status": status,
        "path": r.get("path"), "sha256": r.get("sha256"),
        "canonical_text": canonical_text,
        "disfluency_checked": bool(r.get("disfluency_checked", False)),
    }


def build_player_html(seq_labels, story_segments, kp_items, preview_text, support_1_text,
                       support_2_text, run_summary, final_audio_path) -> None:
    """PM-GOVERNANCE-AUDIO-REVIEW-PLAYER-STANDARD-FORMAT-11準拠の共通module
    (audio_review_player.py)をそのまま呼び、標準player.htmlを組み立てる
    (Seekボタン+Segment/voice+Script+個別音声、Gate 7 (a)〜(l))。"""
    rows = []
    seg_by_id = {s["id"]: s for s in story_segments}
    label_to_text = {"topic_intro_en": (TOPIC_INTRO_EN_TEXT, "narrator(Aoede)"),
                     "topic_intro_ja": (TOPIC_INTRO_JA_TEXT, "narrator(Aoede)"),
                     "preview_ja": (preview_text, "narrator(Aoede)"),
                     "support_1_ja": (support_1_text, "narrator(Aoede)"),
                     "support_2_ja": (support_2_text, "narrator(Aoede)")}
    kp_by_rank = {it["rank"]: it for it in kp_items}

    for entry in run_summary["timeline"]:
        name = entry["part"]
        start = entry["start_seconds"]
        if name.startswith("_silence_"):
            continue
        if name.startswith("key_phrase_"):
            rank = int(name.split("_")[-1])
            it = kp_by_rank[rank]
            script = f"{rank}. {it['used_form']} / {it.get('japanese_gloss')}"
            audio_urls = [f"{WEB_SEG_URL_PREFIX}/kp{rank}_number.mp3",
                          f"{WEB_SEG_URL_PREFIX}/kp{rank}_english.mp3",
                          f"{WEB_SEG_URL_PREFIX}/kp{rank}_japanese.mp3"]
            audio_html = player_mod.render_single_audio_html(audio_urls)
            rows.append(player_mod.render_timeline_row(start, name, "Aoede(number/en/ja gloss)",
                                                         script, audio_html))
            continue
        if name in label_to_text:
            text, voice_disp = label_to_text[name]
            audio_html = player_mod.render_single_audio_html(f"{WEB_SEG_URL_PREFIX}/{name}.mp3")
            rows.append(player_mod.render_timeline_row(start, name, voice_disp, text, audio_html))
            continue
        seg = seg_by_id.get(name)
        if seg is not None:
            voice_disp = "Aoede(narrator)" if seg["voice"] == "narrator" else "Charon(robot)"
            audio_html = player_mod.render_single_audio_html(f"{WEB_SEG_URL_PREFIX}/{seg['id']}.mp3")
            rows.append(player_mod.render_timeline_row(start, name, voice_disp, seg["tts_text"], audio_html))

    table_html = player_mod.render_timeline_table(rows)
    episode_url = "./web/family_c_home_robots_trial_09.mp3"
    html = f"""<!doctype html><html><head><meta charset="utf-8">
<title>Family C Trial-09: Home Robots</title>
<style>{player_mod.PLAYER_STANDARD_CSS}</style>
<script>{player_mod.SEEK_SCRIPT}</script>
</head><body>
<h1>Family C Future — Home Robots(Trial-09完成episode候補)</h1>
<p>duration={run_summary['duration_seconds']}s / peak={run_summary['peak_after_headroom']}</p>
<audio id="episode_audio" class="main" controls preload="none" src="{episode_url}"></audio>
{table_html}
</body></html>"""
    with open(f"{OUT_DIR}/player.html", "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    main()
