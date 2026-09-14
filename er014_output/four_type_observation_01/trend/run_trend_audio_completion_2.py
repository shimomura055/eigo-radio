# ============================================================
# er014_output/four_type_observation_01/trend/run_trend_audio_completion_2.py
# 管理ID: USER-TEST-AUDIO-COMPLETION-01-TREND-CONT1(継続、Fable修正指示1回目)
# ============================================================
# 目的: 前回(run_trend_audio_completion.py、管理ID
# USER-TEST-AUDIO-COMPLETION-01-TREND)がHuman Review Cost Guardにより
# STOPしたA2(full_story_part1/full_story_part2/point_two)・B1B
# (full_story_part1/full_story_part2/point_one/comment_4)を、記事本文は
# 一切変更せず、driver側のTTS入力「読み整形」(Markdownインラインリンク
# の表示テキストのみ残す・記号/ハイフン複合語の読み形統一)のみで解消し、
# 完成episode・Web試聴playerまで仕上げる。
#
# 既存Production関数は無変更で直接呼ぶ(前回driverと同じ関数群)。本
# ファイルは前回driver(run_trend_audio_completion.py)をモジュールとして
# importし、Assembly以降(Gate/consistency/player/cost集計)はそのまま
# 再利用する。新規に追加するのは「読み整形」と、それを使った対象segment
# のみの再TTS、およびB1B comment_4のみの再生成(既存run_b1_scaffold内部で
# comment_4に使っているのと同じ関数b1s.run_support_textを、comment_4単体
# のみに対して直接呼ぶ)。
#
# Human Review Lockの扱い: er011_human_review_lock_01.check_before_
# generation()はcanonical_text_sha256が前回lockと異なる場合
# "canonical_text changed since last lock; treated as new version"として
# proceed=Trueを返す(er011_human_review_lock_01.py L229-232)。approve_
# regenerate()は本driverでは一切呼ばない。旧lockエントリの削除・編集も
# 行わない(新textでの初回TTS/ASRを通常どおり行うのみ)。
#
# 実行方法(root直下から、レベルごとに個別実行):
#   .venv/Scripts/python.exe er014_output/four_type_observation_01/trend/run_trend_audio_completion_2.py --level a2
#   .venv/Scripts/python.exe er014_output/four_type_observation_01/trend/run_trend_audio_completion_2.py --level b1b
from __future__ import annotations

import argparse
import difflib
import os
import re
import sys
import time
from datetime import datetime, timezone

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)
_TREND_DIR_FOR_IMPORT = os.path.dirname(os.path.abspath(__file__))
if _TREND_DIR_FOR_IMPORT not in sys.path:
    sys.path.insert(0, _TREND_DIR_FOR_IMPORT)

import run_trend_audio_completion as base  # 前回driver(Production関数を無変更で直接呼ぶ既存呼び出しをそのまま再利用)

sc = base.sc
tts_gen = base.tts_gen
asm = base.asm
cl = base.cl
arp = base.arp
shared_narration = base.shared_narration
load_json = base.load_json
save_json = base.save_json
sha = base.sha

OUT_DIR = base.OUT_DIR
THEME_ID = base.THEME_ID
TREND_DIR = base.TREND_DIR

# 本タスク(CONT1)専用の追加費用上限(委任文: 本タスク¥100、A2+B1B合計)。
# 前回runまでの累積費用(raw_usage_log_audio_completion.jsonl、既に
# ¥122.15消費済み)とは独立に、「このCONT1タスクで新規に発生した額」だけを
# 追跡する(base.cost_so_far_jpy()はログファイル全体の累積を返すため、
# 開始時点のスナップショットとの差分を使う)。
CONT1_BUDGET_JPY = 100.0
CONT1_ROUND_MAX = 2  # 同一(読み整形後)テキストでの追加re-invocationの上限


def cont1_baseline_cost_jpy() -> float:
    return base.cost_so_far_jpy()


def cont1_check_budget(baseline: float, note: str) -> float:
    so_far = base.cost_so_far_jpy()
    delta = round(so_far - baseline, 4)
    print(f"[CONT1-BUDGET] this_task_delta={delta:.2f} JPY / budget={CONT1_BUDGET_JPY} JPY (次段階: {note})")
    if delta >= CONT1_BUDGET_JPY:
        raise RuntimeError(
            f"[CONT1] 本タスク費用上限到達のためSTOP: delta={delta:.2f} JPY >= "
            f"budget={CONT1_BUDGET_JPY} JPY (次段階「{note}」を実行せず停止)")
    return delta


# ============================================================
# 読み整形(TTS入力専用。記事本文[article.md]は一切変更しない)
# ============================================================
# (a) Markdownインラインリンク "[text](url)" -> "text"(表示テキストのみ
#     残す。URLはTTSが読まず、ASR照合が構造的に不一致になるため)。
_MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def strip_markdown_links(text: str) -> str:
    return _MARKDOWN_LINK_RE.sub(lambda m: m.group(1), text)


# (b)(c) 記号・ハイフン複合語の読み形統一(意味・語順は不変、既存の
#     tts_safe_kp_en()のhealthspan/lifespan対応と同種の"読み形統一"パターン)。
#     Fable診断(2): "Alexa+"をASRが"Alexa Plus"と書き起こす。
#     Fable診断(4)特定結果: B1B full_story_part2/point_oneのASR書き起こしで
#     "natural-language"が一貫して"natural language"(ハイフン脱落)へ
#     正規化される(3 attempts全てで再現、attempts_log突合で確認)。
SYMBOL_TRANSFORMS = [
    ("Alexa+", "Alexa Plus"),
    ("natural-language", "natural language"),
]


def apply_reading_transforms(text: str) -> str:
    out = strip_markdown_links(text)
    for old, new in SYMBOL_TRANSFORMS:
        out = out.replace(old, new)
    return out


def _word_tokens(s: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9']+", s)


def verify_reading_transform_word_safety(original_text: str, transformed_text: str) -> dict:
    """機械確認: 「語の追加削除なし」を、SYMBOL_TRANSFORMSを逆適用した
    transformed_textの単語トークン列が、Markdownリンクの表示テキストのみを
    残したoriginal_textの単語トークン列と完全一致することで検証する
    (逆適用で一致する = 適用した差分がSYMBOL_TRANSFORMSの置換以外に
    存在しないことの独立した機械チェック)。"""
    original_visible_words = _word_tokens(strip_markdown_links(original_text))
    reversed_transformed = transformed_text
    for old, new in SYMBOL_TRANSFORMS:
        reversed_transformed = reversed_transformed.replace(new, old)
    reversed_words = _word_tokens(reversed_transformed)
    match = original_visible_words == reversed_words
    diff = None
    if not match:
        diff = list(difflib.unified_diff(original_visible_words, reversed_words, lineterm=""))
    return {
        "match": match,
        "original_visible_word_count": len(original_visible_words),
        "reversed_transformed_word_count": len(reversed_words),
        "diff_if_mismatch": diff,
    }


# ============================================================
# 対象segment定義
# ============================================================
A2_FIX_SEGMENTS = {
    "full_story_part1": "part1",
    "full_story_part2": "part2",
    "point_two": "point_two_body",
}
B1B_FIX_SEGMENTS = {
    "full_story_part1": "part1",
    "full_story_part2": "part2",
    "point_one": "point_one_body",
}


def _load_parts_and_results(level: str):
    level_out_dir = f"{OUT_DIR}/{level}"
    parts = load_json(f"{level_out_dir}/parts.json")
    results_path = f"{level_out_dir}/audit/tts_generation_results.json"
    results = load_json(results_path)
    return level_out_dir, parts, results, results_path


def _reconstruct_transform_log_entry(seg_entry: dict) -> dict:
    original_text = seg_entry.get("reading_transform_original_text")
    new_text = seg_entry.get("canonical_text")
    word_check = verify_reading_transform_word_safety(original_text, new_text)
    rules = (["markdown_link_strip"] if original_text != strip_markdown_links(original_text) else []) + \
            [old for old, _ in SYMBOL_TRANSFORMS if old in original_text]
    return {
        "original_text": original_text, "new_text": new_text,
        "changed": original_text != new_text, "rules_applied": rules,
        "word_safety_check": word_check,
    }


def _fill_missing_transform_log_from_results(transform_log: dict, fix_segments: dict, final_results: dict) -> dict:
    """今回のround loopで処理しなかった(=既にstatus=OKだった)対象segmentも、
    tts_generation_results.jsonに永続化済みのreading_transform_original_text/
    canonical_textから再構成してtransform_logへ補完する(再実行[resume]時に
    tts_reading_transforms.jsonのsegmentsが空になるバグの防止、本タスク中に
    実際に発生・修正した不整合)。"""
    for name in fix_segments:
        if name in transform_log:
            continue
        entry = final_results["segments"].get(name, {})
        if entry.get("reading_transform_applied") and entry.get("reading_transform_original_text"):
            transform_log[name] = _reconstruct_transform_log_entry(entry)
    return transform_log


def fix_a2_segments(baseline: float) -> dict:
    level_out_dir, parts, results, results_path = _load_parts_and_results("a2")
    narration_dir = f"{level_out_dir}/narration"
    transform_log = {}

    for round_i in range(1, CONT1_ROUND_MAX + 1):
        pending = [n for n in A2_FIX_SEGMENTS if results["segments"].get(n, {}).get("status") != "OK"]
        if not pending:
            break
        cont1_check_budget(baseline, f"tts_a2_reading_fix_round{round_i}")
        print(f"[CONT1][a2][round {round_i}] 読み整形の上で再TTS対象: {pending}")
        for name in pending:
            parts_key = A2_FIX_SEGMENTS[name]
            original_text = parts[parts_key]
            transformed_text = apply_reading_transforms(original_text)
            if name not in transform_log:
                word_check = verify_reading_transform_word_safety(original_text, transformed_text)
                transform_log[name] = {
                    "original_text": original_text, "new_text": transformed_text,
                    "changed": original_text != transformed_text,
                    "rules_applied": (["markdown_link_strip"] if original_text != strip_markdown_links(original_text) else [])
                                     + [old for old, _ in SYMBOL_TRANSFORMS if old in original_text],
                    "word_safety_check": word_check,
                }
            if name in ("point_one", "point_two"):
                sc.assert_no_point_number_label(transformed_text, name)
            tts_input = tts_gen.tts_safe_news_en(transformed_text)
            with cl.logging_context(THEME_ID, "tts_a2_reading_fix"):
                with cl.segment_context(name):
                    r = tts_gen.generate_a2_segment_with_slowdown(
                        tts_input, f"{narration_dir}/{name}.wav", tts_gen.first_words(transformed_text),
                        style_prefix_override=tts_gen.A2_ENGLISH_STYLE_PREFIX_SLOWER,
                        disfluency_qa=False,
                        enable_connected_speech_equivalence_layer=True,
                        enable_repetition_qa=True)
            r["canonical_text"] = transformed_text
            r["reading_transform_applied"] = True
            r["reading_transform_original_text"] = original_text
            results["segments"][name] = r
            print(f"[CONT1][a2][round {round_i}] {name} -> status={r.get('status')}")
        save_json(results_path, results)

    final = load_json(results_path)
    still_stopped = [n for n in A2_FIX_SEGMENTS if final["segments"].get(n, {}).get("status") != "OK"]
    transform_log = _fill_missing_transform_log_from_results(transform_log, A2_FIX_SEGMENTS, final)
    return {"transform_log": transform_log, "still_stopped": still_stopped}


def fix_b1b_comment_4(baseline: float) -> dict:
    level_out_dir, parts, results, results_path = _load_parts_and_results("b1b")
    narration_dir = f"{level_out_dir}/narration"
    support_path = f"{level_out_dir}/b1_support_texts.json"
    support = load_json(support_path)
    old_comment_4_text = support.get("comment_4")

    # 再実行(resume)ガード: comment_4が既にstatus=OK(ASR検証済み音声が存在)
    # であれば、LLM再呼び出し・TTS再生成のどちらも行わない。既にOKなsegmentへ
    # 追加のLLM呼び出しを行うと、b1_support_texts.json(表示・resume用の
    # テキスト台帳)と実際にASR検証済みの音声[canonical_text]が食い違う
    # (本タスク中に実際に発生・修正した不整合、audit/comment_4_regeneration.json
    # のnote_fix参照)。
    existing_status = results["segments"].get("comment_4", {}).get("status")
    if existing_status == "OK":
        existing_canonical = results["segments"]["comment_4"].get("canonical_text")
        print(f"[CONT1][b1b] comment_4: 既にstatus=OK(ASR検証済み)のため再生成しない(新規LLM/TTS呼び出し0件): "
              f"{results_path}")
        reg_path = f"{level_out_dir}/audit/comment_4_regeneration.json"
        reg = load_json(reg_path) if os.path.exists(reg_path) else {}
        return {
            "old_comment_4_text": reg.get("old_comment_4_text", old_comment_4_text),
            "new_comment_4_text": existing_canonical,
            "scaffold_status": reg.get("scaffold_status", "OK"),
            "final_status": existing_status,
            "resumed_no_new_calls": True,
        }

    cont1_check_budget(baseline, "scaffold_b1b_comment4_fix")
    client = sc.get_client()
    c4_context = (f"【Point One(聞き終えた内容)】\n{parts['point_one_heading']}\n{parts['point_one_body']}\n\n"
                  f"【Point Two(聞き終えた内容)】\n{parts['point_two_heading']}\n{parts['point_two_body']}")
    c4_role = sc.b1s.COMMENT_4_ROLE
    with cl.logging_context(THEME_ID, "scaffold_b1b_comment4_fix"):
        c4_result = sc.b1s.run_support_text(client, c4_role, c4_context, model=sc._b1_support_model())
    if c4_result.get("status") != "OK" or not c4_result.get("text"):
        raise RuntimeError(f"[CONT1][b1b] comment_4再生成(Scaffold)がSTOP: status={c4_result.get('status')}"
                            "(既存run_support_text内部max_attempts=2を使い切り。ユーザー判断が必要)。")
    new_comment_4_text = c4_result["text"]

    support["comment_4"] = new_comment_4_text
    save_json(support_path, support)
    save_json(f"{level_out_dir}/audit/comment_4_regeneration.json", {
        "reason": ("[Fable診断(3)] TTSは正しく読んでいるがASRが\"assistants\"を\"assistance\"と誤認(3回とも同一箇所で"
                   "再現)。記事本文[canonical article]は変更せず、Comment/Preview(補助生成テキスト)のみを"
                   "既存Scaffold関数(er003_v1_b1_scaffold_01_generate.run_support_text、"
                   "run_b1_scaffold内部でcomment_4に使っているのと同一の呼び出し)で単独再生成した。"),
        "old_comment_4_text": old_comment_4_text, "new_comment_4_text": new_comment_4_text,
        "scaffold_status": c4_result.get("status"), "attempts": c4_result.get("attempts"),
        "preview_and_comment_1_2_3_unchanged": True,
    })

    for round_i in range(1, CONT1_ROUND_MAX + 1):
        status = results_status = load_json(results_path)["segments"].get("comment_4", {}).get("status")
        if status == "OK":
            break
        cont1_check_budget(baseline, f"tts_b1b_comment4_fix_round{round_i}")
        with cl.logging_context(THEME_ID, "tts_b1b_comment4_fix"):
            with cl.segment_context("comment_4"):
                r = tts_gen.voice01.generate_charon_english(
                    new_comment_4_text, f"{narration_dir}/comment_4.wav",
                    style_prefix_override=tts_gen.B1_PREVIEW_STYLE_PREFIX_CALM, disfluency_qa=True)
        r["canonical_text"] = new_comment_4_text
        r["reading_transform_applied"] = False
        r["comment_4_scaffold_regenerated"] = True
        data = load_json(results_path)
        data["segments"]["comment_4"] = r
        save_json(results_path, data)
        print(f"[CONT1][b1b][round {round_i}] comment_4(再生成テキスト) -> status={r.get('status')}")

    final = load_json(results_path)
    return {
        "old_comment_4_text": old_comment_4_text, "new_comment_4_text": new_comment_4_text,
        "scaffold_status": c4_result.get("status"),
        "final_status": final["segments"]["comment_4"].get("status"),
    }


def fix_b1b_reading_segments(baseline: float) -> dict:
    level_out_dir, parts, results, results_path = _load_parts_and_results("b1b")
    narration_dir = f"{level_out_dir}/narration"
    transform_log = {}

    for round_i in range(1, CONT1_ROUND_MAX + 1):
        pending = [n for n in B1B_FIX_SEGMENTS if results["segments"].get(n, {}).get("status") != "OK"]
        if not pending:
            break
        cont1_check_budget(baseline, f"tts_b1b_reading_fix_round{round_i}")
        print(f"[CONT1][b1b][round {round_i}] 読み整形の上で再TTS対象: {pending}")
        for name in pending:
            parts_key = B1B_FIX_SEGMENTS[name]
            original_text = parts[parts_key]
            transformed_text = apply_reading_transforms(original_text)
            if name not in transform_log:
                word_check = verify_reading_transform_word_safety(original_text, transformed_text)
                transform_log[name] = {
                    "original_text": original_text, "new_text": transformed_text,
                    "changed": original_text != transformed_text,
                    "rules_applied": (["markdown_link_strip"] if original_text != strip_markdown_links(original_text) else [])
                                     + [old for old, _ in SYMBOL_TRANSFORMS if old in original_text],
                    "word_safety_check": word_check,
                }
            if name in ("point_one", "point_two"):
                sc.assert_no_point_number_label(transformed_text, name)
            with cl.logging_context(THEME_ID, "tts_b1b_reading_fix"):
                with cl.segment_context(name):
                    r = tts_gen.news_tail_fix.generate_news_narration_wide_margin(
                        tts_gen.tts_safe_news_en(transformed_text), f"{narration_dir}/{name}.wav",
                        disfluency_qa=False,
                        enable_connected_speech_equivalence_layer=True,
                        enable_repetition_qa=True)
            r["canonical_text"] = transformed_text
            r["reading_transform_applied"] = True
            r["reading_transform_original_text"] = original_text
            results["segments"][name] = r
            print(f"[CONT1][b1b][round {round_i}] {name} -> status={r.get('status')}")
        save_json(results_path, results)

    final = load_json(results_path)
    still_stopped = [n for n in B1B_FIX_SEGMENTS if final["segments"].get(n, {}).get("status") != "OK"]
    transform_log = _fill_missing_transform_log_from_results(transform_log, B1B_FIX_SEGMENTS, final)
    return {"transform_log": transform_log, "still_stopped": still_stopped}


def save_tts_reading_transforms_doc(level: str, transform_log: dict, comment_4_result: dict | None) -> None:
    doc_path = f"{OUT_DIR}/tts_reading_transforms.json"
    doc = load_json(doc_path) if os.path.exists(doc_path) else {
        "note": ("TTS入力テキストのみに適用する「読み整形」の記録(記事本文[article.md]は一切変更しない、"
                  "Trial-09の「7:00→seven」と同種の表示を変えない前処理)。levelごとに、実際に読み整形が"
                  "適用されたsegmentのみ列挙する。"),
        "transform_rules": [
            {"id": "markdown_link_strip", "pattern": "[text](url)", "replacement": "text",
             "reason": "TTSはMarkdownリンクのURL部分を読まず、ASR照合が構造的に不一致になるため"
                       "(Fable診断1)。表示テキストのみを残す。"},
            {"id": "alexaplus_symbol", "pattern": "Alexa+", "replacement": "Alexa Plus",
             "reason": "ASRが記号「+」を含む「Alexa+」を「Alexa Plus」と書き起こすため(Fable診断2)。"},
            {"id": "natural_language_hyphen", "pattern": "natural-language", "replacement": "natural language",
             "reason": "ASRがハイフン複合語「natural-language」をスペース区切りへ正規化して書き起こすため"
                       "(Fable診断4、B1B full_story_part2/point_oneのattempts_log突合で3回とも再現確認)。"},
        ],
        "levels": {},
    }
    doc["levels"][level] = {
        "segments": transform_log,
        "comment_4_regeneration": comment_4_result,
    }
    save_json(doc_path, doc)


def augment_consistency_with_transforms(level: str, transform_log: dict, comment_4_result) -> None:
    path = f"{OUT_DIR}/{level}/article_audio_consistency.json"
    doc = load_json(path)
    doc["reading_transforms_applied_segments"] = list(transform_log.keys())
    doc["reading_transforms_word_safety_all_pass"] = all(
        v["word_safety_check"]["match"] for v in transform_log.values()
    ) if transform_log else True
    doc["reading_transforms_reference"] = f"{OUT_DIR}/tts_reading_transforms.json"
    if comment_4_result is not None:
        doc["comment_4_regenerated"] = True
        doc["comment_4_regeneration_reference"] = f"{OUT_DIR}/{level}/audit/comment_4_regeneration.json"
    save_json(path, doc)


# ============================================================
# base.build_consistency_check()のバグ修正版(read-only診断関数、本タスクの
# 新規ファイル内でのみ修正。base側[run_trend_audio_completion.py、前回
# タスクの成果物]は無変更のまま)。base版はA2のkey_phrases構造
# (kpv["japanese_meaning"])のみを想定しており、B1Bのkey_phrases構造
# (kpv["japanese"]、Charon読み上げのみでAoede"meaning"segmentが無い)では
# KeyError: 'japanese_meaning'で例外になる(実際に本タスクb1b実行で発生・
# 確認済み)。ロジックはbase.build_consistency_check()と完全に同一、
# 対象キー名の解決だけを両構造対応にする。
# ============================================================
def build_consistency_check_fixed(level: str) -> dict:
    level_out_dir = f"{OUT_DIR}/{level}"
    article_text = open(f"{level_out_dir}/article.md", encoding="utf-8").read()
    recomputed_parts = sc.split_article_text(article_text)
    saved_parts = load_json(f"{level_out_dir}/parts.json")
    structure_match = recomputed_parts == saved_parts

    tts_results = load_json(f"{level_out_dir}/audit/tts_generation_results.json")
    seg = tts_results["segments"]
    names = base.A2_CONTENT_SEGMENT_NAMES if level == "a2" else base.B1B_CONTENT_SEGMENT_NAMES
    checked = []
    unverified = []
    for name in names:
        entry = seg.get(name)
        if entry is None:
            unverified.append({"segment": name, "reason": "MISSING"})
            continue
        status_ok = entry.get("status") == "OK" or entry.get("verified") is True
        checked.append({"segment": name, "status": entry.get("status"), "verified": entry.get("verified")})
        if not status_ok:
            unverified.append({"segment": name, "status": entry.get("status"), "verified": entry.get("verified")})

    kp_unverified = []
    kp_checked = []
    for rank, kpv in tts_results.get("key_phrases", {}).items():
        en_status = kpv["english"].get("status")
        ja_entry = kpv.get("japanese_meaning") or kpv.get("japanese")
        ja_status = ja_entry.get("status") if ja_entry is not None else None
        kp_checked.append({"rank": rank, "en_status": en_status, "ja_status": ja_status})
        if en_status != "OK" or ja_status != "OK":
            kp_unverified.append({"rank": rank, "en_status": en_status, "ja_status": ja_status})

    result = {
        "level": level,
        "article_structure_roundtrip_match": structure_match,
        "content_segments_checked": checked,
        "content_segments_unverified": unverified,
        "key_phrases_checked": kp_checked,
        "key_phrases_unverified": kp_unverified,
        "all_pass": structure_match and not unverified and not kp_unverified,
        "note": ("article.mdを再読込しsplit_article_text()を再実行した結果とparts.json(TTS入力の元)が"
                 "byte-identicalであること、かつ全content segment/Key Phraseの生成ステータスがOK/"
                 "verifiedであることを確認した(既存Production TTS関数内部でASR verify済みのため、"
                 "本チェックはstatus/verifiedフラグの再確認+記事構造の再突合のみ行う)。"
                 "[CONT1修正] base.build_consistency_check()のB1B key_phrases構造"
                 "(kpv[\"japanese\"]、A2のkpv[\"japanese_meaning\"]とはキー名が異なる)対応バグを"
                 "本ファイル内のローカル版で修正して使用(base側ファイルは無変更)。"),
    }
    save_json(f"{level_out_dir}/article_audio_consistency.json", result)
    return result


def run_level_cont1(level: str) -> dict:
    print(f"===== [CONT1] level={level} 開始 =====")
    baseline = cont1_baseline_cost_jpy()
    print(f"[CONT1-BUDGET] baseline(累積, 前回runまで込み)={baseline:.2f} JPY, 本タスク上限={CONT1_BUDGET_JPY} JPY")

    comment_4_result = None
    if level == "a2":
        fix_result = fix_a2_segments(baseline)
        transform_log = fix_result["transform_log"]
        # STOPする場合でも、ここまでの診断・読み整形結果は必ず保存する
        # (途中経過が失われないよう、raise前にtts_reading_transforms.jsonへ記録)。
        save_tts_reading_transforms_doc(level, transform_log, None)
        if fix_result["still_stopped"]:
            raise RuntimeError(
                f"[CONT1][a2] STOP: 読み整形後の新テキストでも{CONT1_ROUND_MAX}回再TTSして "
                f"segment {fix_result['still_stopped']} がSTOPPEDのままです(既存retry/fallback機構を"
                "使い切った状態。上限回数を独自判断でさらに引き上げない。ユーザー判断が必要)。")
    else:
        comment_4_result = fix_b1b_comment_4(baseline)
        if comment_4_result["final_status"] != "OK":
            save_tts_reading_transforms_doc(level, {}, comment_4_result)
            raise RuntimeError(
                f"[CONT1][b1b] STOP: comment_4再生成テキストでも{CONT1_ROUND_MAX}回再TTSして "
                f"STOPPEDのままです(status={comment_4_result['final_status']})。"
                "ユーザー判断が必要。")
        fix_result = fix_b1b_reading_segments(baseline)
        transform_log = fix_result["transform_log"]
        save_tts_reading_transforms_doc(level, transform_log, comment_4_result)
        if fix_result["still_stopped"]:
            raise RuntimeError(
                f"[CONT1][b1b] STOP: 読み整形後の新テキストでも{CONT1_ROUND_MAX}回再TTSして "
                f"segment {fix_result['still_stopped']} がSTOPPEDのままです(既存retry/fallback機構を"
                "使い切った状態。上限回数を独自判断でさらに引き上げない。ユーザー判断が必要)。")

    save_tts_reading_transforms_doc(level, transform_log, comment_4_result)

    cont1_check_budget(baseline, f"assemble_{level}")
    assemble_result = base.run_assembly(level)
    if assemble_result.get("gate_off_result") != "PASS":
        raise RuntimeError(f"[CONT1][{level}] Assembly(Gate OFF経路)がPASSしませんでした、STOP: {assemble_result}")

    gate_on = base.run_gate_opt_in_check(level)
    consistency = build_consistency_check_fixed(level)
    augment_consistency_with_transforms(level, transform_log, comment_4_result)
    consistency = load_json(f"{OUT_DIR}/{level}/article_audio_consistency.json")
    web = base.build_player_and_web_delivery(level, assemble_result)

    this_task_delta_jpy = round(base.cost_so_far_jpy() - baseline, 4)

    return {
        "level": level, "transform_log": transform_log, "comment_4_result": comment_4_result,
        "assemble_result": assemble_result, "gate_opt_in_result": gate_on,
        "consistency": consistency, "web": web,
        "cost_breakdown_jpy": base.cost_breakdown_by_stage(),
        "this_task_delta_jpy": this_task_delta_jpy,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--level", choices=["a2", "b1b"], required=True)
    args = parser.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)
    cl.install(base.LOG_PATH)

    t0 = time.time()
    level_result = run_level_cont1(args.level)
    base.update_shared_outputs(args.level, level_result)
    base.append_progress_log(args.level, level_result)
    elapsed = round(time.time() - t0, 1)

    save_json(f"{OUT_DIR}/{args.level}/run_result_audio_completion_cont1.json", {
        "level": args.level, "elapsed_seconds": elapsed,
        "gate_off_result": level_result["assemble_result"].get("gate_off_result"),
        "gate_on_result": level_result["gate_opt_in_result"].get("gate_on_result"),
        "duration_seconds": level_result["assemble_result"].get("duration_seconds"),
        "consistency_all_pass": level_result["consistency"].get("all_pass"),
        "this_task_delta_jpy": level_result["this_task_delta_jpy"],
        "cost_breakdown_jpy_cumulative": level_result["cost_breakdown_jpy"],
    })
    print(f"===== [CONT1] level={args.level} 完了(elapsed={elapsed}s, "
          f"this_task_delta_jpy={level_result['this_task_delta_jpy']:.2f}) =====")


if __name__ == "__main__":
    main()
