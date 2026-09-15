# ============================================================
# er013_family_c_episode_trial_09b_b1_run.py
# 管理ID: USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03-FAMILYC-B1
# ============================================================
# 目的: Family C(home_robots)のB1版Trial episodeを新規生成する。
# 同一Story core(A2版Trial-08 reader_facing_article.txtを参照)を維持
# しながら、er013_family_c_future_writer_08_b1.py(Trial専用派生Writer)で
# B1向け独立生成本文を作り、Family A由来のIntro/Outro/Title/SFX/Pause・
# Preview・Key Phrase 5件・Comment 1〜3(Comment 4なし)・Story
# (Narrator=Aoede/Robot=Charon/Mother=Erinome)で完成episodeを組み立てる。
#
# 既存Production/Trial資産は一切編集せず、呼び出す・importするだけ:
#   - er013_family_c_episode_trial_09b_run.py(v2、`home_robots_v2/`用)を
#     モジュールとしてimportし、TTS wrapper関数・BudgetTracker・共有Charon
#     資産定数のみ再利用する(**編集禁止**)。
#   - Production API層(er003_v1_iran01_a2_generate/er003_b1_p9a_audio/
#     er003_v1_n3_01_assemble/er002_common/audio_review_player)は直接
#     importして呼び出すのみ。
#
# v2との主な違い(詳細は`../spec/episode_spec_b1.md`):
#   - 本文は完全新規生成(v1/v2音声の再利用なし、記事非依存の共有Charon
#     nav資産[Welcome/Preview intro/Key phrases intro/Full story intro/
#     番号読み上げ]・v2と同一文言のTopic intro(EN)/Japanese titleのみ再利用)
#   - 話者判定(robot/mother)は固定段落indexではなく、引用符+近傍文脈の
#     決定的キーワード判定(汎用アルゴリズム、どの生成本文にも適用可能)
#   - Comment 1〜3のみ(Comment 4は生成しない、ユーザー正式決定)
#   - Comment 2/3の挿入位置は、累積語数の割合(概ね35%/65%)を基準に、
#     直近の「merge種別(会話を含まない地の文段落)」segment境界へスナップ
#     する決定的アルゴリズムで自動選定する(v2の固定paragraph境界の
#     ハードコードに代わる汎用版)。選定理由はcomment_placement.jsonへ記録。
#
# Status: Trial専用、未承認draft実装(`APPROVED_FOR_PRODUCTION`ではない)。
# 最大Status: VALIDATED。Production採用判断はしない。
#
# 実行方法(root直下から):
#   .venv/Scripts/python.exe er013_family_c_episode_trial_09b_b1_run.py \
#       --budget-jpy 90
# ============================================================
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
import er003_v1_en_direct_vfl_01_generate as vfl01
import er005_cost_logger as cl
import er006_model_routing_contract_01 as routing
import er013_family_c_future_eval_08 as eval8
import er013_family_c_future_qa_01 as fcq1
import er013_family_c_future_qa_02 as fcq2
import er013_family_c_future_safety_06 as safety6
import er013_family_c_future_writer_08_b1 as writer_b1

import er013_family_c_episode_trial_09b_run as v2run  # 再利用のみ、編集禁止

import audio_review_player as player_mod

# ============================================================
# パス定数
# ============================================================
OUT_DIR = "er013_output/family_c_episode_trial_09/home_robots_b1"
AUDIO_DIR = f"{OUT_DIR}/audio"
ASSEMBLED_DIR = f"{OUT_DIR}/assembled"
KEY_PHRASE_DIR = f"{OUT_DIR}/key_phrases"
AUDIT_DIR = f"{OUT_DIR}/audit"
WEB_DIR = f"{OUT_DIR}/web"
WEB_SEG_DIR = f"{WEB_DIR}/segments"

SR = p9a.TARGET_SAMPLE_RATE
MONO_SR = common.SAMPLE_RATE

ARTICLE_ID = "family_c_home_robots_trial_09b_b1"
LEVEL = "FAMILY_C_TRIAL_09B_B1"  # 新規level文字列(既存A2/B1/B_FAMILY_A2/FAMILY_C_TRIAL_09B
                                  # には存在せず、Gateの既存level別辞書は無変更)。

TOPIC_TITLE = "Home Robots"
TOPIC_INTRO_EN_TEXT = f"Today's topic is {TOPIC_TITLE}."  # v2と同一文言(音声再利用のため)
JAPANESE_TITLE_TEXT = "ホームロボット"  # v2と同一(音声再利用のため)

MOTHER_VOICE_NAME = v2run.MOTHER_VOICE_NAME  # "Erinome"(v2と同一Voice構成)

# Core Provocation(er013_output/family_c_future_trial_08/home_robots/writer_prompt.txt
# より転記、事前指定外Read。A2版と完全同一のCore Provocationを使う)。
CORE_PROVOCATION = (
    "A home robot makes life effortless by quietly choosing hundreds of tiny things "
    "for its owner—what to eat, wear, watch, and say—until one day the owner must "
    "make a genuinely important choice and discovers they no longer know how. Is "
    "convenience slowly training humans out of having preferences?"
)
THEME_LABEL = "the future of home robots"

MAX_WRITER_ATTEMPTS = 2  # 技術的marker retryのみ(trial-08と同一方針)
WRITER_REASONING_EFFORT = vfl01.REASONING_EFFORT  # "high"
JUDGE_REASONING_EFFORT = "medium"
MAX_KP_ATTEMPTS = 4  # Key Phrase Validator不合格時の入口再呼び出し上限(委任文どおり)

TTS_CALL_EST_JPY = v2run.TTS_CALL_EST_JPY
LLM_CALL_EST_JPY = v2run.LLM_CALL_EST_JPY
ASR_DIAG_CALL_EST_JPY = v2run.ASR_DIAG_CALL_EST_JPY

COMMENT_1_ROLE_JA = (
    "あなたは英語学習者向け音声番組で、物語が始まる直前に置く短い日本語"
    "コメントを書く担当です。これから、家のロボットに囲まれて生活する"
    "マヤの物語が始まります。結末や主人公の選択を先に明かさず、1文程度・"
    "30〜50字程度で、物語の世界に耳を傾けるよう促す短い一言を書いて"
    "ください。直前に流れるPreview(短い前置き)と同じ内容を繰り返さない"
    "でください。断定的な予告にせず、自然な話し言葉にしてください。"
    "新しい設定・事実・登場人物を追加しないでください。"
)
COMMENT_2_ROLE_JA = (
    "あなたは英語学習者向け音声番組の、物語の途中に挿入する短い日本語"
    "コメントを書く担当です。これから、何でも便利にこなしてくれるロボット"
    "に囲まれてきた主人公が、初めて自分では簡単に判断できない問いに直面"
    "する場面が始まります。結末や主人公の選択を先に明かさず、1文程度・"
    "40〜70字程度で、次に何が起きるかへ軽く注意を向ける短い日本語コメント"
    "を書いてください。断定的な予告にせず、自然な話し言葉にしてください。"
    "新しい設定・事実を追加しないでください。"
)
COMMENT_3_ROLE_JA = (
    "あなたは英語学習者向け音声番組の、物語の途中に挿入する短い日本語"
    "コメントを書く担当です。これから、いつも頼りになるロボットが、"
    "お金・睡眠・仕事・安全について質問を重ねても、主人公の答えを"
    "見つけられない場面が続きます。結末や主人公の選択を先に明かさず、"
    "1文程度・40〜70字程度で、「今回はロボットのいつものやり方では"
    "答えが出ない」ということへ軽く注意を向ける短い日本語コメントを"
    "書いてください。断定的な予告にせず、自然な話し言葉にしてください。"
    "新しい設定・事実を追加しないでください。"
)
COMMENT_ROLES = {1: COMMENT_1_ROLE_JA, 2: COMMENT_2_ROLE_JA, 3: COMMENT_3_ROLE_JA}

# USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03-FAMILYC-B1(継続CONT1、
# 2026-09-15): 旧Comment 3(「お金や仕事、睡眠、安全について答えても、
# 今回はロボットのいつものやり方だけでは答えが見つからないようです。」)は
# 「誰が問いかけ誰が答えたか」の主語が曖昧で、A2 v2でユーザーが指摘した
# 問題(RESULT_PACKET_FU03_FAMILYC_A2.md記載)と同種。ユーザーがA2向けに
# 指定した文と同趣旨で、B1本文(story_035「The robot asked about money,
# work, sleep, and safety. Maya answered each question, but the two
# plans remained on the wall. No answer became the right one.」)の
# 語順・内容に合わせて主語を明示した日本語へ差し替える
# (--fix-comment3指定時のみ適用、意味・Factは変更しない)。
COMMENT_3_FIXED_TEXT_OVERRIDE = (
    "ロボットがお金や仕事、睡眠、安全について問いかけ、マヤは一つずつ答え"
    "ましたが、今回はいつものようにロボットが最適解を示してくれることは"
    "ありませんでした。"
)

STORY_CORE_CHECKPOINTS = [
    {"id": "protagonist_name", "description": "主人公の名前(Maya)", "keywords": ["Maya"]},
    {"id": "robot_manages_life", "description": "家のロボットが日常の細かい選択を管理する設定",
     "keywords": ["robot"]},
    {"id": "mother_arrival", "description": "母親が訪れ、一人暮らしできない旨を伝え、選択を求める",
     "keywords": ["mother"]},
    {"id": "robot_needs_preference", "description": "ロボットが『あなたの好み(意向)が必要』と繰り返す",
     "keywords": ["preference", "prefer"]},
    {"id": "cannot_answer", "description": "主人公が自分の答えを見つけられない(What do you want等)",
     "keywords": ["want", "know", "sure"]},
    {"id": "turn_off", "description": "『すべてを消して』という主人公の決定的行動(climax)",
     "keywords": ["turn", "off", "dark", "quiet"]},
    {"id": "invite_mother_in", "description": "主人公が自ら母親を招き入れる結末",
     "keywords": ["come in", "mother"]},
]


def save_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def save_text(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


# ============================================================
# Stage 0: Writer(B1、technical marker retry最大2回)
# ============================================================
def generate_writer_with_marker_retry(client, reference_article: str) -> tuple:
    model = routing.require_model_or_override(
        "A2_WRITER", routing.WRITER_MODEL,
        override_reason="USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03-FAMILYC-B1: "
                         "Family C B1 Trial WriterにA2_WRITER Approved Model(Luna)を転用"
                         "(新規process未定義、コスト影響なし、DEV/Trial限定)")
    prompt = writer_b1.build_family_c_writer_v8_b1_prompt(
        core_provocation=CORE_PROVOCATION, theme_label=THEME_LABEL,
        reference_article=reference_article,
        story_core_bullets=writer_b1.HOME_ROBOTS_STORY_CORE_BULLETS)
    save_text(f"{OUT_DIR}/writer_prompt_b1.txt", prompt)
    attempts = []
    for attempt in range(1, MAX_WRITER_ATTEMPTS + 1):
        result = writer_b1.generate_family_c_article_v8_b1(
            client, model=model, reasoning_effort=WRITER_REASONING_EFFORT, prompt=prompt)
        text_no_meta = fcq2.strip_meta_blocks(result["raw_text"])
        imagined_check = fcq1.validate_markers_balanced(text_no_meta)
        fact_check_balance = fcq2.validate_fact_markers_balanced(text_no_meta)
        balanced = imagined_check["balanced"] and fact_check_balance["balanced"]
        attempts.append({"attempt": attempt, "imagined_check": imagined_check,
                          "fact_check_balance": fact_check_balance, "response_id": result["response_id"]})
        if balanced:
            save_json(f"{OUT_DIR}/writer_attempts_b1.json", attempts)
            return result["raw_text"], attempts
        print(f"[writer_b1] attempt {attempt}: マーカー不整合(technical retry) "
              f"imagined={imagined_check} fact={fact_check_balance}")
    save_json(f"{OUT_DIR}/writer_attempts_b1.json", attempts)
    raise RuntimeError(f"マーカー整合の取れたB1 Writer出力が{MAX_WRITER_ATTEMPTS}回の技術的試行でも"
                        "得られませんでした。STOP(NG_REVIEW_REQUIRED)。")


_CURRENT_FACT_LEAK_PATTERNS = [
    r"\bin (19|20)\d{2}\b", r"\baccording to\b", r"\bstud(y|ies)\b", r"\bresearch(er|ers)?\b",
    r"\bsurvey(s|ed)?\b", r"\breport(s|ed)?\b", r"\b\d+(\.\d+)?\s?(million|billion|percent|%)\b",
]
_LEAK_RE = [re.compile(p, re.IGNORECASE) for p in _CURRENT_FACT_LEAK_PATTERNS]


def scan_current_fact_leak(reader_text: str) -> dict:
    hits = []
    for rx in _LEAK_RE:
        for m in rx.finditer(reader_text):
            hits.append({"pattern": rx.pattern, "match": m.group(0)})
    return {"leak_hits": hits, "leak_count": len(hits)}


def stage_writer_and_safety(client) -> dict:
    if os.path.exists(f"{OUT_DIR}/reader_facing_article_b1.txt"):
        with open(f"{OUT_DIR}/reader_facing_article_b1.txt", encoding="utf-8") as f:
            reader_text = f.read()
        with open(f"{OUT_DIR}/word_count.json", encoding="utf-8") as f:
            word_count_info = json.load(f)
        print(f"[stage_writer_and_safety] REUSED existing reader_facing_article_b1.txt "
              f"(word_count={word_count_info['word_count']})")
        return {"reader_text": reader_text, "word_count_info": word_count_info}

    reference_article = v2run.load_article_text()  # A2版Story core参照元(read-onlyで再利用)
    article_text, attempts = generate_writer_with_marker_retry(client, reference_article)
    save_text(f"{OUT_DIR}/writer_raw_article_b1.txt", article_text)

    layers = safety6.extract_layers(article_text)
    reader_text = layers["reader_text"]
    save_text(f"{OUT_DIR}/reader_facing_article_b1.txt", reader_text)

    word_count = len(reader_text.split())
    fact_count = len(layers["fact_blocks"])
    word_count_info = {
        "word_count": word_count, "target": writer_b1.WORD_TARGET,
        "acceptable_range": list(writer_b1.WORD_ACCEPTABLE_RANGE),
        "within_acceptable_range": writer_b1.WORD_ACCEPTABLE_RANGE[0] <= word_count <= writer_b1.WORD_ACCEPTABLE_RANGE[1],
        "current_fact_marker_count": fact_count,
        "note": ("CURRENT_SPEC.mdのB1 News節には数値の語数上限は存在しない"
                 "(全体語数「上限なし」)。target/acceptable_rangeはTrial限定の暫定目安"
                 "(writer_08[A2]の350語/300-420語を土台にした概算)であり、正式仕様値では"
                 "ない。超過時は本ファイルのwithin_acceptable_range=falseとして記録する。"),
    }
    save_json(f"{OUT_DIR}/word_count.json", word_count_info)

    # --- Fact Safety(trial-08と同一方針、CURRENT FACT 0件ならFact Checker A'をskip) ---
    judge_model = routing.require_model_or_override(
        "A2_WRITER", routing.WRITER_MODEL,
        override_reason="USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03-FAMILYC-B1: "
                         "Plausibility Bridge/Imagined Future軽判定にA2_WRITER Approved Model"
                         "(Luna)を転用(新規process未定義、コスト影響なし、DEV/Trial限定)")
    fact_blocks = layers["fact_blocks"]
    if not fact_blocks:
        current_fact_result = {"skipped": True,
                                "reason": "CURRENT FACT 0件(B1 Trial限定skip、trial-08と同一方針)。",
                                "layer_pass": True}
    else:
        current_fact_result = safety6.run_current_fact_layer(client, ARTICLE_ID, TOPIC_TITLE, fact_blocks, "")
    bridge_result = safety6.run_plausibility_bridge_layer(client, judge_model, JUDGE_REASONING_EFFORT,
                                                            layers["bridge_text"])
    imagined_result = safety6.run_imagined_future_layer(client, judge_model, JUDGE_REASONING_EFFORT,
                                                          layers["imagined_blocks"])
    overall_pass = current_fact_result["layer_pass"] and bridge_result["layer_pass"] and imagined_result["layer_pass"]
    leak_scan = scan_current_fact_leak(reader_text)
    fact_safety = {
        "current_fact_layer": current_fact_result, "plausibility_bridge_layer": bridge_result,
        "imagined_future_layer": imagined_result, "overall_pass": overall_pass,
        "current_fact_leak_scan": leak_scan,
    }
    save_json(f"{OUT_DIR}/fact_safety.json", fact_safety)
    if fact_count > 0 or leak_scan["leak_count"] > 0 or not overall_pass:
        raise RuntimeError(f"FACT_SAFETY_NOT_CLEAN: fact_count={fact_count} "
                            f"leak_count={leak_scan['leak_count']} overall_pass={overall_pass}。STOP。")

    # --- 補助Story Spark評価(6軸、trial-08と同一方針) ---
    eval_model = routing.require_model_or_override(
        "A2_WRITER", routing.WRITER_MODEL,
        override_reason="USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03-FAMILYC-B1: "
                         "補助Story Spark評価(6軸)にA2_WRITER Approved Model(Luna)を転用"
                         "(新規process未定義、コスト影響なし、DEV/Trial限定)")
    eval_prompt = eval8.build_eval_prompt(CORE_PROVOCATION, reader_text)
    eval_result = eval8.run_story_eval(client, eval_model, JUDGE_REASONING_EFFORT, eval_prompt)
    character_count = eval8.count_characters_heuristic(reader_text)
    listening_metrics = eval8.compute_listening_metrics(reader_text)
    spark_gate = {"eval": eval_result, "character_count": character_count,
                  "listening_metrics": listening_metrics}
    save_json(f"{OUT_DIR}/spark_gate.json", spark_gate)

    # --- Story core check(機械的キーワード照合、目視確認はRESULT_PACKETに記録) ---
    story_core_check = []
    for cp in STORY_CORE_CHECKPOINTS:
        found = None
        for kw in cp["keywords"]:
            idx = reader_text.lower().find(kw.lower())
            if idx >= 0:
                found = reader_text[max(0, idx - 40):idx + len(kw) + 40]
                break
        story_core_check.append({"id": cp["id"], "description": cp["description"],
                                  "keywords_checked": cp["keywords"], "found": found is not None,
                                  "matched_context": found})
    save_json(f"{OUT_DIR}/story_core_check.json", {
        "method": "決定的キーワード照合(機械)。文意の同一性そのものはこのJSONだけでは保証されず、"
                  "RESULT_PACKETに記載する目視比較(A2版との対応関係の要約)と併せて判断する。",
        "reference_article_path": v2run.ARTICLE_PATH,
        "checkpoints": story_core_check,
        "all_found": all(c["found"] for c in story_core_check),
    })

    normalized = v2run.normalize_for_tts(reader_text)
    save_text(f"{OUT_DIR}/article_normalized.txt", normalized)

    return {"reader_text": reader_text, "word_count_info": word_count_info}


# ============================================================
# Stage 1: Format normalization + 3-voice segment分割(決定的、汎用)
# ============================================================
QUOTE_RE = re.compile("“[^”]*”|\"[^\"]*\"")


def find_quote_spans(paragraph_text: str) -> list:
    return [(m.start(), m.end(), m.group(0)) for m in QUOTE_RE.finditer(paragraph_text)]


def classify_quote_voice(paragraph_text: str, start: int, end: int) -> str:
    before = paragraph_text[max(0, start - 80):start].lower()
    after = paragraph_text[end:end + 80].lower()
    window = before + " " + after
    if "robot" in window:
        return "robot"
    if "mother" in window:
        return "mother"
    return "narrator"


def build_all_story_segments_b1(paragraphs: list) -> tuple:
    segments = []
    ambiguous_quotes = []
    counter = {"n": 0}

    def next_id() -> str:
        counter["n"] += 1
        return f"story_{counter['n']:03d}"

    def add_seg(voice: str, kind: str, p_idx: int, raw_text: str) -> None:
        segments.append({
            "id": next_id(), "voice": voice, "kind": kind,
            "source_paragraph_indices": [p_idx], "raw_text": raw_text,
            "tts_text": v2run.tts_safe_time_reading_en(v2run.normalize_for_tts(raw_text)),
            "paragraph_contributions": [(p_idx, raw_text)],
        })

    for p_idx, para in enumerate(paragraphs):
        if para.strip() == "":
            continue
        spans = find_quote_spans(para)
        if not spans:
            add_seg("narrator", "merge", p_idx, para)
            continue
        pos = 0
        for start, end, qtext in spans:
            if start > pos and para[pos:start].strip():
                add_seg("narrator", "split", p_idx, para[pos:start])
            voice = classify_quote_voice(para, start, end)
            if voice == "narrator":
                ambiguous_quotes.append({"paragraph_index": p_idx, "quote_text": qtext})
            add_seg(voice, "split", p_idx, qtext)
            pos = end
        if pos < len(para) and para[pos:].strip():
            add_seg("narrator", "split", p_idx, para[pos:])
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


# ============================================================
# Stage 2: Comment 1〜3(日本語、新規LLM)
# ============================================================
def run_ja_comment_text(client, comment_num: int, article_text: str, budget) -> str:
    label = f"comment_{comment_num}_llm"
    budget.check_before(LLM_CALL_EST_JPY, label)
    context = f"【物語全文(参考、新しい設定・事実の追加禁止)】\n{article_text}"
    result = a2gen.run_support_text(client, COMMENT_ROLES[comment_num], context, model=a2gen.MODEL)
    budget.add(label, "llm", 1, LLM_CALL_EST_JPY, {"status": result.get("status")})
    if result.get("status") != "OK":
        raise RuntimeError(f"COMMENT_{comment_num}_LLM_FAILED: {result}")
    return result["text"].strip()


def run_ja_preview_text(client, article_text: str, comment_1: str, comment_2: str, budget) -> str:
    label = "preview_llm"
    budget.check_before(LLM_CALL_EST_JPY, label)
    preview_role = a2gen.PREVIEW_ROLE.format(comment_1=comment_1, comment_2=comment_2)
    context = f"【エピソード全文(参考、新しいFactの追加禁止)】\n{article_text}"
    result = a2gen.run_support_text(client, preview_role, context, model=a2gen.MODEL)
    budget.add(label, "llm", 1, LLM_CALL_EST_JPY, {"status": result.get("status")})
    if result.get("status") != "OK":
        raise RuntimeError(f"PREVIEW_LLM_FAILED: {result}")
    return result["text"].strip()


# ============================================================
# Stage 3: Key Phrase(既存正式経路、Validator不合格時は入口再呼び出し最大4回)
# ============================================================
def run_key_phrase_pipeline(article_text: str, kp_dir: str, budget) -> tuple:
    os.makedirs(kp_dir, exist_ok=True)
    for attempt in range(1, MAX_KP_ATTEMPTS + 1):
        label_sel = f"key_phrase_selection_attempt{attempt}"
        budget.check_before(LLM_CALL_EST_JPY * 2, label_sel)
        sel = a2gen.run_key_phrase_selection(article_text, kp_dir)
        budget.add(label_sel, "llm", 1, LLM_CALL_EST_JPY * 2, {"status": sel["status"]})
        if sel["status"] != "KEY_WORDS_STRUCTURE_PASS":
            print(f"[key_phrase] attempt {attempt}: selection status={sel['status']}(再試行)")
            continue
        label_canon = f"key_phrase_canon_attempt{attempt}"
        budget.check_before(LLM_CALL_EST_JPY * 2, label_canon)
        canon = a2gen.run_key_phrase_canonicalization(article_text, sel["original_items"], kp_dir)
        budget.add(label_canon, "llm", 1, LLM_CALL_EST_JPY * 2, {"status": canon["status"]})
        if canon["status"] in ("CANONICALIZATION_PASS", "CANONICALIZATION_REVIEW_REQUIRED"):
            return canon["merged"], attempt
        print(f"[key_phrase] attempt {attempt}: canonicalization status={canon['status']}(再試行)")
    raise RuntimeError(f"KEY_PHRASE_PIPELINE_FAILED_AFTER_{MAX_KP_ATTEMPTS}_ATTEMPTS")


# ============================================================
# Comment placement(累積語数35%/65%、直近merge境界へスナップ)
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
# USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03-FAMILYC-B1(CONT1、
# 2026-09-15): --reassemble時のみ有効な既存artifact ASRキャッシュ(v2の
# _load_prior_asr_cache/_load_prior_comment_asr_cache相当をB1の
# 自ディレクトリ向けに実装)。Comment 3以外の内容が変わっていない
# segment/nav/key phraseの再ASR診断を避け、低コスト再Assemblyを可能にする。
# ============================================================
def _load_prior_seg_asr_cache(reassemble: bool) -> dict:
    """既存player_display_audio_consistency.jsonからasr_textを読み込む
    キャッシュ({segment_id: asr_text})。"""
    cache: dict = {}
    if not reassemble:
        return cache
    path = f"{OUT_DIR}/player_display_audio_consistency.json"
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for row in json.load(f):
                cache[row["segment_id"]] = row.get("asr_text")
    return cache


def _load_prior_comment_asr_cache(reassemble: bool) -> dict:
    """既存comment_consistency.jsonからasr_textを読み込むキャッシュ
    ({comment_number: asr_text})。"""
    cache: dict = {}
    if not reassemble:
        return cache
    path = f"{OUT_DIR}/comment_consistency.json"
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for row in json.load(f):
                cache[row["comment"]] = row.get("asr_text")
    return cache


def _load_prior_kp_asr_cache(reassemble: bool) -> dict:
    """既存key_phrase_consistency.jsonからasr_en/asr_jaを読み込むキャッシュ
    ({rank_str: {"asr_en":..., "asr_ja":...}})。"""
    cache: dict = {}
    if not reassemble:
        return cache
    path = f"{OUT_DIR}/key_phrase_consistency.json"
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            prior = json.load(f)
        for rank_str, row in prior.items():
            cache[rank_str] = {"asr_en": row.get("asr_en"), "asr_ja": row.get("asr_ja")}
    return cache


# ============================================================
# main
# ============================================================
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--budget-jpy", type=float, default=90.0)
    # USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03-FAMILYC-B1(CONT1、
    # 2026-09-15): Comment 3固定差し替え+既存artifact再利用による低コスト
    # 再Assemblyの2フラグ(v2[er013_family_c_episode_trial_09b_run.py]の
    # --fix-comment3/--reassembleと同一方針をB1へ適用)。
    parser.add_argument("--fix-comment3", action="store_true",
                         help="Comment 3をCOMMENT_3_FIXED_TEXT_OVERRIDEへ差し替え、"
                              "既存Comment 3音声を無効化して再TTSする")
    parser.add_argument("--reassemble", action="store_true",
                         help="既存の完了済みartifact(音声/consistency結果)を再利用し、"
                              "変更箇所(Comment 3)のみ新規API呼び出しを行う低コスト"
                              "再Assemblyモード。TTS/LLM/ASRは全て既存関数・既存retry"
                              "構成をそのまま使う(フル再生成はしない)")
    args = parser.parse_args()

    for d in (AUDIO_DIR, ASSEMBLED_DIR, KEY_PHRASE_DIR, AUDIT_DIR):
        os.makedirs(d, exist_ok=True)

    # er005_cost_logger初期化(Production共有部品、既存API利用のみ・編集なし)。
    # Secondary ASR Cascade(er006_secondary_asr_01.py)がAzure STTフォールバック
    # 経路で無条件にcl.record()を呼ぶため、未初期化のままだとRuntimeErrorになる
    # (trial_08_run.pyと同一の初期化パターンをそのまま踏襲。ログ先はBudgetTracker
    # のraw_usage_log.jsonlと形式が異なるため別ファイルに分離する)。
    cl.install(f"{AUDIT_DIR}/er005_cost_log.jsonl")

    budget = v2run.BudgetTracker(args.budget_jpy, 70.0, f"{OUT_DIR}/raw_usage_log.jsonl")
    client = a2gen.get_client()

    # --reassemble時のみ有効な既存artifact ASRキャッシュ(Comment 3以外の
    # 内容が変わっていないsegment/nav/key phraseの再ASR診断を避ける)。
    seg_asr_cache = _load_prior_seg_asr_cache(args.reassemble)
    prior_comment_asr_cache = _load_prior_comment_asr_cache(args.reassemble)
    kp_asr_cache = _load_prior_kp_asr_cache(args.reassemble)

    # --- Stage 0: Writer + Fact Safety + Story Spark Gate + Story core check ---
    writer_result = stage_writer_and_safety(client)
    reader_text = writer_result["reader_text"]
    article_text = reader_text  # reader-facing本文(IMAGINEDマーカーは既にsafety6.extract_layersで除去済み)

    paragraphs = v2run.split_into_paragraphs(reader_text)
    segments, ambiguous_quotes = build_all_story_segments_b1(paragraphs)
    reconstructed = reconstruct_article_from_story_segments(segments, paragraphs)
    assert reconstructed == reader_text, "STORY_SEGMENT reconstruction mismatch(生成前チェック)"
    save_json(f"{AUDIT_DIR}/ambiguous_quotes.json", ambiguous_quotes)
    if ambiguous_quotes:
        print(f"[WARNING] speaker判定が曖昧な引用符が{len(ambiguous_quotes)}件narratorへfallbackしました"
              "(audit/ambiguous_quotes.json参照、要目視確認)")

    audit_segments: dict = {}
    audit_key_phrases: dict = {}
    gain_report: dict = {}

    # --- Stage F: Story segment TTS(全件新規、v1/v2 reuseなし) ---
    for seg in segments:
        out_path = f"{AUDIO_DIR}/{seg['id']}.wav"
        if seg["voice"] == "narrator":
            r = v2run.tts_narrator(seg["tts_text"], out_path, "en", seg["id"], budget)
        elif seg["voice"] == "robot":
            r = v2run.tts_robot(seg["tts_text"], out_path, seg["id"], budget)
        elif seg["voice"] == "mother":
            r = v2run.tts_mother(seg["tts_text"], out_path, seg["id"], budget)
        else:
            raise ValueError(f"unknown voice: {seg['voice']}")
        audit_segments[seg["id"]] = v2run._to_audit_entry(r, seg["tts_text"])
        seg["audio_path"] = out_path

    save_json(f"{OUT_DIR}/segments.json",
              [{k: v for k, v in s.items() if k != "paragraph_contributions"} for s in segments])

    # --- speaker_map.json ---
    speaker_entries = []
    for seg in segments:
        if seg["kind"] == "split" and seg["voice"] in ("robot", "mother"):
            speaker_entries.append({
                "segment_id": seg["id"], "voice": seg["voice"],
                "source_paragraph_indices": seg["source_paragraph_indices"],
                "quote_text": seg["raw_text"],
                "attribution_basis": "引用符前後160文字以内の'robot'/'mother'キーワード決定的検出"
                                      "(汎用アルゴリズム、build_all_story_segments_b1参照)",
            })
    save_json(f"{OUT_DIR}/speaker_map.json", {
        "mother_voice": MOTHER_VOICE_NAME,
        "maya_split_decision": "Mayaの台詞はnarrator(Aoede)のまま分離しない(v2と同一方針、"
                                "話者を増やしすぎない既存2-voice設計思想を踏襲)。",
        "ambiguous_quote_count": len(ambiguous_quotes),
        "entries": speaker_entries,
    })

    # --- Stage E: Comment 1〜3(resumable) ---
    comments_md_path = f"{OUT_DIR}/comments_ja.md"
    comments_md_prev_path = f"{OUT_DIR}/comments_ja_prev.md"
    comment_texts = {}
    existing_md_text = None
    if os.path.exists(comments_md_path):
        with open(comments_md_path, encoding="utf-8") as f:
            existing_md_text = f.read()
        for n in (1, 2, 3):
            marker = f"## Comment {n}\n\n"
            after = existing_md_text.split(marker, 1)[1]
            comment_texts[n] = after.split("\n\n", 1)[0].strip()
    else:
        for n in (1, 2, 3):
            comment_texts[n] = run_ja_comment_text(client, n, article_text, budget)

    # USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03-FAMILYC-B1(CONT1):
    # --fix-comment3指定時、Comment 3を固定文へ差し替える(主語明確化)。
    comment3_overridden = False
    if args.fix_comment3 and comment_texts.get(3) != COMMENT_3_FIXED_TEXT_OVERRIDE:
        comment3_overridden = True
        comment_texts[3] = COMMENT_3_FIXED_TEXT_OVERRIDE

    if existing_md_text is None or comment3_overridden:
        if existing_md_text is not None:
            with open(comments_md_prev_path, "w", encoding="utf-8") as f:
                f.write(existing_md_text)
        with open(comments_md_path, "w", encoding="utf-8") as f:
            for n in (1, 2, 3):
                f.write(f"## Comment {n}\n\n{comment_texts[n]}\n\n")

    if comment3_overridden:
        # 内容が変わったため既存音声(stale)を無効化する(_resumable_reuse()は
        # ファイル+.okマーカーの存在のみで判定し内容一致を検証しないため、
        # 削除せずに放置すると古い本文の音声が再利用され続ける)。
        stale_base = f"{AUDIO_DIR}/comment_3_ja.wav"
        for suffix in ("", ".ok", ".debug.json"):
            stale_path = stale_base + suffix
            if os.path.exists(stale_path):
                os.remove(stale_path)

    comment_wavs = {}
    for n in (1, 2, 3):
        txt = comment_texts[n]
        path = f"{AUDIO_DIR}/comment_{n}_ja.wav"
        r = v2run.tts_narrator(txt, path, "ja", f"comment_{n}_ja", budget)
        audit_segments[f"comment_{n}_ja"] = v2run._to_audit_entry(r, txt)
        comment_wavs[n] = (path, r)

    # --- Stage C: Preview(resumable) ---
    preview_path = f"{OUT_DIR}/preview.txt"
    if os.path.exists(preview_path):
        with open(preview_path, encoding="utf-8") as f:
            preview_text = f.read().strip()
    else:
        preview_text = run_ja_preview_text(client, article_text, comment_texts[1], comment_texts[2], budget)
        save_text(preview_path, preview_text)
    r_preview = v2run.tts_narrator(preview_text, f"{AUDIO_DIR}/preview_ja.wav", "ja", "preview_ja", budget)
    audit_segments["preview_ja"] = v2run._to_audit_entry(r_preview, preview_text)

    # --- Stage D: Key Phrase(resumable、既存正式経路+入口再呼び出し最大4回) ---
    kp_canon_path = f"{KEY_PHRASE_DIR}/keywords_canonicalized.json"
    if os.path.exists(kp_canon_path):
        with open(kp_canon_path, encoding="utf-8") as f:
            kp_merged = json.load(f)
        kp_attempt_used = None
    else:
        kp_merged, kp_attempt_used = run_key_phrase_pipeline(article_text, KEY_PHRASE_DIR, budget)
    kp_items = sorted(kp_merged["items"], key=lambda it: it["rank"])
    save_json(f"{OUT_DIR}/audit/key_phrase_attempt_used.json", {"attempt_used": kp_attempt_used})

    kp_blocks_stereo = []
    kp_consistency = {}
    for item in kp_items:
        rank = item["rank"]
        used_form = item["used_form"]
        ja_gloss_display = item.get("japanese_gloss")
        ja_gloss_tts = item.get("japanese_gloss_tts") or ja_gloss_display

        num_path = f"{AUDIO_DIR}/kp{rank}_number.wav"
        r_num = v2run.reuse_shared_number_word(rank, num_path)
        en_path = f"{AUDIO_DIR}/kp{rank}_english.wav"
        r_en_kp = v2run.tts_key_phrase_english(used_form, en_path, f"kp{rank}_english", budget)
        ja_path = f"{AUDIO_DIR}/kp{rank}_japanese.wav"
        r_ja_kp = v2run.tts_narrator(ja_gloss_tts, ja_path, "ja", f"kp{rank}_japanese", budget)

        audit_key_phrases[str(rank)] = {
            "number": v2run._to_audit_entry(r_num, v2run.NUMBER_WORDS[rank]),
            "english": v2run._to_audit_entry(r_en_kp, used_form),
            "japanese": v2run._to_audit_entry(r_ja_kp, ja_gloss_tts),
        }
        kp_blocks_stereo.append((rank, num_path, en_path, ja_path))

        en_asr = r_en_kp.get("asr_text") or kp_asr_cache.get(str(rank), {}).get("asr_en") \
            or v2run.asr_diag(en_path, "en", budget, f"kp{rank}_english_asr_diag")
        ja_asr = r_ja_kp.get("asr_text") or kp_asr_cache.get(str(rank), {}).get("asr_ja") \
            or v2run.asr_diag(ja_path, "ja", budget, f"kp{rank}_japanese_asr_diag")
        kp_consistency[str(rank)] = {
            "player_display_en": used_form, "canonical_en": used_form, "tts_input_en": used_form,
            "asr_en": en_asr, "match_en": v2run._normalize_loose(en_asr) == v2run._normalize_loose(used_form),
            "player_display_ja": ja_gloss_display, "canonical_ja": ja_gloss_display,
            "tts_input_ja": ja_gloss_tts, "asr_ja": ja_asr,
            "match_ja": v2run._normalize_loose(ja_asr) == v2run._normalize_loose(ja_gloss_tts),
        }
    save_json(f"{OUT_DIR}/key_phrase_consistency.json", kp_consistency)

    # --- Stage A: SFX/Nav資産(article非依存共有資産+v2同一文言の再利用) ---
    intro_mp3 = p9a.load_and_resample_to_target(p9a.INTRO_MP3_PATH)
    outro_mp3 = p9a.load_and_resample_to_target(p9a.OUTRO_MP3_PATH)
    notification_mp3 = p9a.load_and_resample_to_target(p9a.NOTIFICATION_MP3_PATH)
    v2run.copy_shared_charon_nav(AUDIO_DIR)
    r_topic_en = v2run.reuse_v1_wav(f"{v2run.AUDIO_DIR}/topic_intro_en.wav", f"{AUDIO_DIR}/topic_intro_en.wav")
    audit_segments["topic_intro_en"] = v2run._to_audit_entry(r_topic_en, TOPIC_INTRO_EN_TEXT)
    r_title = v2run.reuse_v1_wav(f"{v2run.AUDIO_DIR}/japanese_title.wav", f"{AUDIO_DIR}/japanese_title.wav")
    audit_segments["japanese_title"] = v2run._to_audit_entry(r_title, JAPANESE_TITLE_TEXT)

    # --- Comment placement(累積語数35%/65%、merge境界スナップ) ---
    c2_idx, c3_idx, total_words, cum_words = choose_comment_boundaries(segments)

    def _wav_duration(path: str) -> float:
        mono, sr, _, _ = common.read_wav_float(path)
        return round(len(mono) / sr, 3)

    comment_placement = [
        {"comment": 1, "position_description": "導入部(Preview後・Story前、Full story introの直後、"
                                                 "固定配置)",
         "selection_reason": "Comment 1は物語の理解補助として常にStory先頭固定(v2と同一方針)。",
         "before_segment_id": None, "after_segment_id": segments[0]["id"],
         "before_segment_word_count": None,
         "after_segment_word_count": len(segments[0]["tts_text"].split()),
         "comment_duration_seconds": _wav_duration(comment_wavs[1][0]),
         "comment_word_count_ja_chars": len(comment_texts[1])},
        {"comment": 2, "position_description": f"story_{c2_idx+1:03d}(segment index {c2_idx})の直後",
         "selection_reason": "累積語数が記事全体の約35%へ到達した直後の、直近の地の文段落"
                              "(merge種別、会話を含まない自然な段落境界)へスナップして自動選定"
                              "(semantic breakの機械的近似、目視確認結果はRESULT_PACKETに記載)。",
         "before_segment_id": segments[c2_idx]["id"],
         "after_segment_id": segments[c2_idx + 1]["id"] if c2_idx + 1 < len(segments) else None,
         "before_segment_word_count": len(segments[c2_idx]["tts_text"].split()),
         "after_segment_word_count": (len(segments[c2_idx + 1]["tts_text"].split())
                                       if c2_idx + 1 < len(segments) else None),
         "comment_duration_seconds": _wav_duration(comment_wavs[2][0]),
         "comment_word_count_ja_chars": len(comment_texts[2]),
         "cumulative_word_fraction_at_boundary": round(cum_words[c2_idx] / total_words, 3)},
        {"comment": 3, "position_description": f"story_{c3_idx+1:03d}(segment index {c3_idx})の直後",
         "selection_reason": "累積語数が記事全体の約65%へ到達した直後の、直近の地の文段落"
                              "(merge種別)へスナップして自動選定(story後半・結末直前の自然な"
                              "節目の機械的近似、目視確認結果はRESULT_PACKETに記載)。",
         "before_segment_id": segments[c3_idx]["id"],
         "after_segment_id": segments[c3_idx + 1]["id"] if c3_idx + 1 < len(segments) else None,
         "before_segment_word_count": len(segments[c3_idx]["tts_text"].split()),
         "after_segment_word_count": (len(segments[c3_idx + 1]["tts_text"].split())
                                       if c3_idx + 1 < len(segments) else None),
         "comment_duration_seconds": _wav_duration(comment_wavs[3][0]),
         "comment_word_count_ja_chars": len(comment_texts[3]),
         "cumulative_word_fraction_at_boundary": round(cum_words[c3_idx] / total_words, 3),
         "note": ("位置決定方式(累積語数35%/65%→直近merge境界へのスナップ)は"
                  "semantic break/volume balanceの暫定Trial実装であり、恒久仕様"
                  "ではない。USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03-"
                  "FAMILYC-B1(継続CONT1)でComment 3のテキストのみ主語明確化の"
                  "ため差し替えた(位置[story_027/028境界]は変更していない)。")},
    ]
    save_json(f"{OUT_DIR}/comment_placement.json", comment_placement)

    # --- Stage H: gain + timeline構築(Family A構成をそのまま踏襲、v2と同一pause値) ---
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

    preview_mono = load_mono(f"{AUDIO_DIR}/preview_ja.wav")
    first_story_mono = load_mono(segments[0]["audio_path"])
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

    seq.append(("Comment 1", gs(load_mono(comment_wavs[1][0]), "comment_1")))
    sil(0.8)

    for i, seg in enumerate(segments):
        seq.append((seg["id"], gs(load_mono(seg["audio_path"]), seg["id"])))
        is_last = (i == len(segments) - 1)
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

    sil(0.5)  # Story終了直後→Outro(Comment4なしのため、A2既存のOutro直前pause値[0.5秒]を直接適用)
    seq.append(("Outro", outro_gained))

    save_json(f"{AUDIT_DIR}/gain_report.json", gain_report)

    assembled_result = assemble_mod.assemble_with_timeline(seq)
    safety_result = assemble_mod.apply_headroom_safety_valve(assembled_result["assembled"], seq)
    save_json(f"{AUDIT_DIR}/headroom_report.json", safety_result["report"])

    final_path = f"{ASSEMBLED_DIR}/family_c_home_robots_trial_09b_b1.wav"
    # USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03-FAMILYC-B1(CONT1):
    # Comment 3差し替え時、旧assembled wav/episode mp3/player.htmlは削除せず
    # web/prevへ退避してから上書きする(v2のComment4削除時と同一方針)。
    prev_dir = f"{WEB_DIR}/prev"
    old_episode_mp3 = f"{WEB_DIR}/family_c_home_robots_trial_09b_b1.mp3"
    if comment3_overridden:
        os.makedirs(prev_dir, exist_ok=True)
        if os.path.exists(final_path):
            shutil.copyfile(final_path, f"{prev_dir}/family_c_home_robots_trial_09b_b1_pre_comment3_fix.wav")
        if os.path.exists(old_episode_mp3):
            shutil.copyfile(old_episode_mp3, f"{prev_dir}/family_c_home_robots_trial_09b_b1_pre_comment3_fix.mp3")
    common.write_wav_float(final_path, safety_result["assembled"], SR, 2)

    run_summary = {
        "duration_seconds": assembled_result["total_duration_seconds"],
        "peak_before_headroom": safety_result["report"]["peak_before"],
        "peak_after_headroom": safety_result["report"]["peak_after"],
        "headroom_applied": safety_result["report"]["applied"],
        "timeline": assembled_result["timeline"],
    }
    save_json(f"{AUDIT_DIR}/run_summary_assemble.json", run_summary)

    # --- Stage I: tts_generation_results.json(Gate入力) + Audio Validation Gate ---
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

    # --- Stage J: article/audio consistency ---
    story_concat_canonical = " ".join(s["tts_text"] for s in segments)
    normalized_path = f"{OUT_DIR}/article_normalized.txt"
    normalized = open(normalized_path, encoding="utf-8").read() if os.path.exists(normalized_path) \
        else v2run.normalize_for_tts(reader_text)
    save_json(f"{OUT_DIR}/article_audio_consistency.json", {
        "method": "Story本文全体(article_normalized.txt)とstory segment群のtts_text連結が、"
                  "読み整形分(引用符正規化・時刻表記読み・空白圧縮)を除いて一致することを確認する。",
        "story_segment_concat_tts_text": story_concat_canonical,
        "article_normalized_text": normalized,
    })

    # --- Stage K: player/display/audio consistency ---
    # --reassemble時: 内容が変わっていないsegment/navはseg_asr_cache(前回の
    # player_display_audio_consistency.json)からasr_textを再利用し、
    # 変更が無いのにASR診断を再課金しない(v2の_load_prior_asr_cache相当)。
    consistency_rows = []
    for seg in segments:
        asr_text = audit_segments[seg["id"]].get("asr_text")
        if asr_text is None:
            asr_text = seg_asr_cache.get(seg["id"])
        if asr_text is None:
            asr_text = v2run.asr_diag(seg["audio_path"], "en", budget, f"{seg['id']}_asr_diag")
        consistency_rows.append({
            "segment_id": seg["id"], "voice": seg["voice"],
            "player_display_text": seg["tts_text"], "canonical_text": seg["tts_text"],
            "tts_input_text": seg["tts_text"], "asr_text": asr_text,
            "match": v2run._normalize_loose(asr_text) == v2run._normalize_loose(seg["tts_text"]),
        })
    fixed_checks = [
        ("topic_intro_en", TOPIC_INTRO_EN_TEXT, "en", audit_segments["topic_intro_en"].get("asr_text")),
        ("japanese_title", JAPANESE_TITLE_TEXT, "ja", None),
        ("preview_ja", preview_text, "ja", audit_segments["preview_ja"].get("asr_text")),
    ]
    for n in (1, 2, 3):
        fixed_checks.append((f"comment_{n}_ja", comment_texts[n], "ja",
                              audit_segments[f"comment_{n}_ja"].get("asr_text")))
    for key, (_fname, text) in v2run.SHARED_CHARON_NAV.items():
        fixed_checks.append((key, text, "en", None))
    for name, text, lang, precomputed in fixed_checks:
        asr_text = precomputed
        if asr_text is None and not (name == "comment_3_ja" and comment3_overridden):
            asr_text = seg_asr_cache.get(name)
        if asr_text is None:
            path = f"{AUDIO_DIR}/{name}.wav"
            asr_text = v2run.asr_diag(path, lang, budget, f"{name}_asr_diag")
        consistency_rows.append({
            "segment_id": name, "voice": "nav/fixed",
            "player_display_text": text, "canonical_text": text, "tts_input_text": text,
            "asr_text": asr_text, "match": v2run._normalize_loose(asr_text) == v2run._normalize_loose(text),
        })
    save_json(f"{OUT_DIR}/player_display_audio_consistency.json", consistency_rows)

    # --- Stage L: Comment consistency ---
    # --reassemble時: comment_1/2は内容不変のためprior_comment_asr_cache
    # (前回comment_consistency.json)のasr_textを再利用する。comment_3は
    # 新規TTS結果(r.get("asr_text"))をそのまま使う(キャッシュ参照しない、
    # comment3_overridden時に古いasr_textを誤って再利用しないため)。
    comment_consistency = []
    for n in (1, 2, 3):
        path, r = comment_wavs[n]
        cached = None if (n == 3 and comment3_overridden) else prior_comment_asr_cache.get(n)
        asr_text = r.get("asr_text") or cached or v2run.asr_diag(path, "ja", budget, f"comment_{n}_reconfirm_asr")
        comment_consistency.append({
            "comment": n, "player_display_text": comment_texts[n], "canonical_text": comment_texts[n],
            "tts_input_text": comment_texts[n], "asr_text": asr_text,
            "match": v2run._normalize_loose(asr_text) == v2run._normalize_loose(comment_texts[n]),
        })
    save_json(f"{OUT_DIR}/comment_consistency.json", comment_consistency)

    # --- Stage O: mp3化 + player再生成 ---
    web_result = convert_all_to_mp3_b1()
    old_player_path = f"{OUT_DIR}/player.html"
    if comment3_overridden and os.path.exists(old_player_path):
        shutil.copyfile(old_player_path, f"{OUT_DIR}/player_prev_pre_comment3_fix.html")
    build_player_html_b1(seq_labels=[name for name, _ in seq], segments=segments,
                          kp_items=kp_items, comment_texts=comment_texts, run_summary=run_summary,
                          preview_text=preview_text)

    # --- Stage P: cost_summary.json ---
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
        "budget_cap_jpy": args.budget_jpy, "warn_threshold_jpy": 70.0,
        "total_estimate_jpy": round(total_jpy, 2),
        "note": "raw_usage_log.jsonl全体(複数回のresume実行を含む)からの累計。v2と同じ方式論"
                "(precedentベースの安全側単価推定)。全segment/preview/comment/key phraseが新規"
                "生成のため、v1/v2のような音声reuseによる費用削減はない(共有Charon nav資産・"
                "Topic intro/Japanese titleの流用のみ)。",
        "tts_call_count_estimate_basis": tts_count, "llm_call_count_estimate_basis": llm_count,
        "asr_diag_call_count_estimate_basis": asr_diag_count,
        "gate_status": gate_status,
        "word_count": writer_result["word_count_info"]["word_count"],
        "word_count_within_acceptable_range": writer_result["word_count_info"]["within_acceptable_range"],
    }
    save_json(f"{OUT_DIR}/cost_summary.json", cost_summary)

    print(f"[DONE] duration={run_summary['duration_seconds']}s gate={gate_status} "
          f"cost_estimate=Y{total_jpy:.2f} word_count={writer_result['word_count_info']['word_count']}")


# ============================================================
# mp3化 + player.html(v2の構造を踏襲、B1用に汎用segments対応)
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
    ep_wav = f"{ASSEMBLED_DIR}/family_c_home_robots_trial_09b_b1.wav"
    ep_mp3 = f"{WEB_DIR}/family_c_home_robots_trial_09b_b1.mp3"
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
    fixed_label_to_text = {
        "Welcome (Charon)": (v2run.SHARED_CHARON_NAV["welcome"][1], "Charon(nav)"),
        "Topic intro": (TOPIC_INTRO_EN_TEXT, "Aoede(narrator)"),
        "Japanese title": (JAPANESE_TITLE_TEXT, "Aoede(narrator)"),
        "Preview intro (Charon)": (v2run.SHARED_CHARON_NAV["preview_intro"][1], "Charon(nav)"),
        "Key phrases intro (Charon)": (v2run.SHARED_CHARON_NAV["key_phrases_intro"][1], "Charon(nav)"),
        "Full story intro (Charon)": (v2run.SHARED_CHARON_NAV["full_story_intro"][1], "Charon(nav)"),
        "Comment 1": (comment_texts[1], "Aoede(narrator)"), "Comment 2": (comment_texts[2], "Aoede(narrator)"),
        "Comment 3": (comment_texts[3], "Aoede(narrator)"),
    }
    name_to_seg_id = {
        "Welcome (Charon)": "welcome", "Topic intro": "topic_intro_en", "Japanese title": "japanese_title",
        "Preview intro (Charon)": "preview_intro", "Preview": "preview_ja",
        "Key phrases intro (Charon)": "key_phrases_intro", "Full story intro (Charon)": "full_story_intro",
        "Comment 1": "comment_1_ja", "Comment 2": "comment_2_ja", "Comment 3": "comment_3_ja",
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
            audio_html = player_mod.render_single_audio_html("./web/segments/preview_ja.mp3")
            rows.append(player_mod.render_timeline_row(start, name, "Aoede(narrator)", preview_text, audio_html))
            continue
        if name in fixed_label_to_text:
            text, voice_disp = fixed_label_to_text[name]
            seg_id = name_to_seg_id.get(name, name)
            audio_html = player_mod.render_single_audio_html(f"./web/segments/{seg_id}.mp3")
            rows.append(player_mod.render_timeline_row(start, name, voice_disp, text, audio_html))
            continue
        seg = seg_by_id.get(name)
        if seg is not None:
            voice_disp = {"narrator": "Aoede(narrator)", "robot": "Charon(robot)",
                          "mother": "Erinome(mother)"}[seg["voice"]]
            audio_html = player_mod.render_single_audio_html(f"./web/segments/{seg['id']}.mp3")
            rows.append(player_mod.render_timeline_row(start, name, voice_disp, seg["tts_text"], audio_html))

    table_html = player_mod.render_timeline_table(rows)
    episode_url = "./web/family_c_home_robots_trial_09b_b1.mp3"
    html = f"""<!doctype html><html><head><meta charset="utf-8">
<title>Family C Trial-09b: Home Robots (B1)</title>
<style>{player_mod.PLAYER_STANDARD_CSS}</style>
<script>{player_mod.SEEK_SCRIPT}</script>
</head><body>
<h1>Family C Future — Home Robots (Trial-09 B1 / VALIDATED候補・ユーザー試聴待ち、level=B1)</h1>
<p>duration={run_summary['duration_seconds']}s / peak={run_summary['peak_after_headroom']}</p>
<p><strong>Trial専用、Production採用ではない。最大Status: VALIDATED。</strong></p>
<audio id="episode_audio" class="main" controls preload="none" src="{episode_url}"></audio>
{table_html}
</body></html>"""
    save_text(f"{OUT_DIR}/player.html", html)


if __name__ == "__main__":
    main()
