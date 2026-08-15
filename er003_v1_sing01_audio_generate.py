# ============================================================
# er003_v1_sing01_audio_generate.py
# ER-003-B1-NOVEL-AUDIO-01: SING01(AI/Technological Singularity) Full Audio
# ============================================================
# 完全新規記事(SING01)のB1 Supported Natural English完成版音声を、
# ER-003-B1-SCAFFOLD-AUDIO-03で確立したShell/voice構成(A2 Audio Shell
# 継承・B1英語Shell narration・Comment=Charon・News/Preview=Aoede・
# trim安全マージン修正)をそのまま適用して生成する。B1専用News本文は
# 作らない(B2本文をFull Story/Point One/Two/In One Lineでそのまま共有)。
#
# 新しいTTS/ASR安全処理ロジックは作らず、er003_audio_tts_asr_safety.py
# (HARDENING-01)とAUDIO-01/03で確立したgenerate_long_form_narration_
# verified/generate_point_explanation_en相当の関数をそのまま踏襲する。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_sing01_audio_generate.py

from __future__ import annotations

import json
import os
import re
import time

import numpy as np

import er002_common as common
import er002_ja_web_research_r3 as r3
import er002_gemini_client as gclient
import er003_audio_tts_asr_safety as safety
import er003_b1_p3u_audio as p3u
import er003_b1_p4_audio as p4
import er003_b1_p9a_audio as p9a
import er003_v1_a2_audio_02_generate as audio02
import er003_v1_b1_scaffold_audio_03_generate as audio03
import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_repro01_main_generate as repro01

ARTICLE_ID = "SING01"
OUT_DIR = "er003_output/novel_audio_01/SING01"
ARTICLE_PATH = f"{OUT_DIR}/article/B2_article.md"
LEDGER_PATH = f"{OUT_DIR}/research/verified_fact_ledger.txt"
SUPPORT_TEXTS_PATH = f"{OUT_DIR}/article/support_texts.json"
KP_CANONICALIZED_PATH = f"{OUT_DIR}/keyphrases/keywords_canonicalized.json"
NARRATION_DIR = f"{OUT_DIR}/narration"
TOPIC = "AI / Technological Singularity — 2026年の著名AIリーダー発言 vs 研究者調査データ"

SR = p9a.TARGET_SAMPLE_RATE
NEWS_VOICE_NAME = audio03.NEWS_VOICE_NAME  # "Aoede"(無変更)
COMMENT_VOICE_NAME = audio03.COMMENT_VOICE_NAME  # "Charon"(AUDIO-03と同一)
LONG_FORM_TRIM_SAFETY_MARGIN_SECONDS = audio03.LONG_FORM_TRIM_SAFETY_MARGIN_SECONDS  # 0.35秒(AUDIO-03のtail修正を継承)

ENGLISH_TITLE_TEXT = "Sam Altman Says We're in the Singularity. Not Everyone Agrees"
TOPIC_INTRO_TEXT = f"Today's topic is {ENGLISH_TITLE_TEXT}."
POINT_EXPLANATION_EN_TEXT = audio03.POINT_EXPLANATION_EN_TEXT  # "Here's the point."(AUDIO-03を無変更で再利用)


def load_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


# ============================================================
# Step 0: B2記事をPart1/Part2/Point One/Point Two/In One Lineへ分割
# ============================================================
def split_article_text(b2_text: str) -> dict:
    """AUDIO-01のsplit_fixed_news_text相当だが、A02専用の
    PART1_SPLIT_MARKERチェックを外し、段落単位でPart1/Part2を分ける
    (このSING01記事の段落構成は固定として扱う)。見出し検出ロジックは
    同一(###を2つ、## In one line…を1つ要求する)。"""
    title_match = re.match(r"^#\s+(.+?)\s*\n", b2_text)
    title = title_match.group(1).strip() if title_match else ""

    h3_matches = list(re.finditer(r"^###\s+(.+?)\s*$", b2_text, flags=re.MULTILINE))
    if len(h3_matches) != 2:
        raise RuntimeError(f"###見出しがちょうど2つではありません(検出数: {len(h3_matches)})。")
    in_one_line_match = re.search(r"^##\s+In one line[…\.]*\s*\n(.+)", b2_text, flags=re.MULTILINE | re.DOTALL)
    if not in_one_line_match:
        raise RuntimeError("『## In one line…』見出しが見つかりません。")

    body = b2_text[title_match.end():h3_matches[0].start()].strip()
    paragraphs = [p.strip() for p in body.split("\n\n") if p.strip()]
    if len(paragraphs) != 4:
        raise RuntimeError(f"本文段落数が想定(4段落)と異なります(検出数: {len(paragraphs)})。")
    part1 = f"{paragraphs[0]} {paragraphs[1]}"
    part2 = f"{paragraphs[2]} {paragraphs[3]}"

    point_one_heading = h3_matches[0].group(1).strip()
    point_one_body = b2_text[h3_matches[0].end():h3_matches[1].start()].strip()
    point_two_heading = h3_matches[1].group(1).strip()
    point_two_body = b2_text[h3_matches[1].end():in_one_line_match.start()].strip()
    in_one_line_text = in_one_line_match.group(1).strip()

    return {
        "title": title, "part1": part1, "part2": part2,
        "point_one_heading": point_one_heading, "point_one_body": point_one_body,
        "point_two_heading": point_two_heading, "point_two_body": point_two_body,
        "in_one_line": in_one_line_text,
    }


# ============================================================
# Step 1: News本文音声(Full Story/Point/In One Line) — AUDIO-01方式を継承
# ============================================================
def generate_news_narration_verified(text: str, out_path: str, max_attempts: int = 6,
                                      max_extra_chars: int = 15) -> dict:
    """AUDIO-01のgenerate_news_narration_verifiedと同一方式(ENGLISH_STYLE_
    PREFIX主経路→MINIMAL_INSTRUCTION fallback)。ASR検証はHARDENING-01の
    共通モジュールへ置き換える(判定ロジックは同等、監査trailが強化される)。"""
    max_len = len(text) + max_extra_chars
    attempts_log = []
    for attempt in range(1, max_attempts + 1):
        r = p9a.generate_narration_snippet(text, "en", out_path)
        instruction_type = "english_style_prefix"
        if r.get("status") != "OK":
            attempts_log.append({"attempt": attempt, "status": r.get("status"), "reason": r.get("reason"),
                                  "instruction_type": instruction_type})
            r = repro01.generate_english_component_minimal_instruction(text, out_path)
            instruction_type = "minimal_fallback"
            if r.get("status") != "OK":
                attempts_log.append({"attempt": attempt, "status": r.get("status"), "reason": r.get("reason"),
                                      "instruction_type": instruction_type})
                continue
        asr_text, asr_err = p4.get_full_text_via_azure_stt_continuous(out_path, language="en-US")
        match = safety.validate_asr_match(text, asr_text, n=6, asr_error=asr_err)
        length_ok = asr_text is not None and len(asr_text) <= max_len
        verified = match["passed"] and length_ok
        attempts_log.append({"attempt": attempt, "status": "OK", "asr_text": asr_text,
                              "instruction_type": instruction_type, "asr_verdict": match["verdict"],
                              "length_ok": length_ok, "verified": verified})
        if verified:
            r["asr_verified"] = True
            r["asr_text"] = asr_text
            r["attempts_log"] = attempts_log
            r["instruction_type"] = instruction_type
            return r
    return {"status": "STOPPED", "reason": f"{max_attempts}回試行してもASR検証に合格しませんでした",
            "attempts_log": attempts_log}


# ============================================================
# Step 2: Support(Preview/Comment)・Point explanation・Topic introの生成
# ============================================================
def generate_long_form(text: str, out_path: str, voice_name: str) -> dict:
    """AUDIO-03のgenerate_long_form_narration_verifiedをそのまま再利用
    (trim安全マージン修正込み)。"""
    return audio03.generate_long_form_narration_verified(text, out_path, voice_name=voice_name)


def generate_short_shell_narration(text: str, out_path: str) -> dict:
    """AUDIO-03のgenerate_point_explanation_en相当(ENGLISH_STYLE_PREFIX
    主経路+MINIMAL_INSTRUCTION fallback、通常trim)。Topic introのような
    記事固有だが短いShell要素の生成に使う。"""
    def primary(t, p):
        return p9a.generate_narration_snippet(t, "en", p)

    def fallback(t, p):
        return repro01.generate_english_component_minimal_instruction(t, p)

    for attempt in range(1, 7):
        r = safety.generate_tts_with_fallback(text, out_path, primary, fallback)
        if r.get("status") != "OK":
            continue
        asr_text, asr_err = p4.get_full_text_via_azure_stt_continuous(out_path, language="en-US")
        match = safety.validate_asr_match(text, asr_text, asr_error=asr_err)
        if match["passed"]:
            r["asr_verified"] = True
            r["asr_text"] = asr_text
            r["asr_match"] = match
            return r
    return {"status": "STOPPED", "reason": "6回試行してもASR検証に合格しませんでした"}


# ============================================================
# Step 3: Fact Safety再確認(Support文言、AUDIO-01の思想を継承)
# ============================================================
def run_support_safety_recheck(support_texts: dict, ledger_text: str) -> dict:
    support_concat = "\n\n".join(t for t in support_texts.values() if t)
    print("[SING01-AUDIO] Support Ledger Deviation Check開始...")
    client = vfl01.get_client()
    deviation_result = vfl01.run_deviation_check(client, ledger_text, support_concat)
    print(f"[SING01-AUDIO] deviation={deviation_result['parsed']['overall_status']} "
          f"count={len(deviation_result['parsed']['deviations'])}")

    print("[SING01-AUDIO] Support Fact Check開始...")
    fc_prompt = r3.build_fact_check_prompt(TOPIC, support_concat, [])

    def make_fc_fn():
        return r3.make_fact_checker_fn(fc_prompt)

    fc_result, fc_status, fc_attempts, fc_model, fc_response_id, fc_search_usage, fc_sources = \
        r3.run_fact_checker_with_gates(make_fc_fn, sleep_fn=time.sleep)
    verdict = fc_result.get("verdict") if fc_result else None
    print(f"[SING01-AUDIO] fact_check status={fc_status} verdict={verdict}")

    return {"ledger_deviation": deviation_result["parsed"],
            "fact_check": {"final_status": fc_status, "result": fc_result}}


def main():
    os.makedirs(NARRATION_DIR, exist_ok=True)
    os.makedirs(f"{OUT_DIR}/assembled", exist_ok=True)
    os.makedirs(f"{OUT_DIR}/audit", exist_ok=True)

    b2_text = load_text(ARTICLE_PATH)
    ledger_text = load_text(LEDGER_PATH)
    support_texts = json.loads(load_text(SUPPORT_TEXTS_PATH))
    kp_canon = json.loads(load_text(KP_CANONICALIZED_PATH))
    parts = split_article_text(b2_text)
    with open(f"{OUT_DIR}/audit/article_parts.json", "w", encoding="utf-8") as f:
        json.dump(parts, f, ensure_ascii=False, indent=2)

    # --- Step 0: Support Fact Safety再確認 ---
    safety_result = run_support_safety_recheck(support_texts, ledger_text)
    with open(f"{OUT_DIR}/audit/support_safety_recheck.json", "w", encoding="utf-8") as f:
        json.dump(safety_result, f, ensure_ascii=False, indent=2, default=str)
    if safety_result["ledger_deviation"]["overall_status"] != "LEDGER_COMPLIANT":
        print("[SING01-AUDIO] SupportがLEDGER_COMPLIANTではないため中断します。")
        return
    # Fact Checkはbinding gateにしない(AUDIO-01と同じ方針)。Support文は
    # News本文より先にFactを明かさないよう意図的に曖昧な案内文として
    # 書いており、一般的なFact Checkerは「具体性がなく検証不能」という
    # 指摘を返しやすい(これは設計上の意図であり、欠陥ではない)。binding
    # gateはLedger Deviation Check(LEDGER_COMPLIANT)のみとし、Fact Check
    # の結果はrun_summaryへ記録した上で監査資料として残す。
    fc_status = safety_result["fact_check"]["final_status"]
    fc_verdict = (safety_result["fact_check"]["result"] or {}).get("verdict")
    print(f"[SING01-AUDIO] Support Fact Check結果(参考記録、binding gateではない): "
          f"status={fc_status} verdict={fc_verdict}")

    # --- Step 1: Topic intro(記事固有Shell要素、英語のみ) ---
    print("[SING01-AUDIO] Topic intro生成...")
    topic_intro_path = f"{NARRATION_DIR}/topic_intro.wav"
    topic_intro_result = generate_short_shell_narration(TOPIC_INTRO_TEXT, topic_intro_path)
    print(f"[SING01-AUDIO] topic_intro: status={topic_intro_result.get('status')}")

    # --- Step 2: Preview(Aoede、tail安全マージン修正版) ---
    print("[SING01-AUDIO] Preview生成...")
    preview_path = f"{NARRATION_DIR}/preview.wav"
    preview_result = generate_long_form(support_texts["preview"], preview_path, NEWS_VOICE_NAME)
    print(f"[SING01-AUDIO] preview: status={preview_result.get('status')}")

    # --- Step 3: Comment 1-4(Charon) ---
    comment_results = {}
    for name in ("comment_1", "comment_2", "comment_3", "comment_4"):
        print(f"[SING01-AUDIO] {name}生成(Charon)...")
        out_path = f"{NARRATION_DIR}/{name}.wav"
        r = generate_long_form(support_texts[name], out_path, COMMENT_VOICE_NAME)
        comment_results[name] = r
        print(f"[SING01-AUDIO] {name}: status={r.get('status')}")

    # --- Step 4: News本文(Aoede) ---
    news_jobs = [
        ("full_story_part1", parts["part1"]),
        ("full_story_part2", parts["part2"]),
        ("point_one", f"{parts['point_one_heading']}. {parts['point_one_body']}"),
        ("point_two", f"{parts['point_two_heading']}. {parts['point_two_body']}"),
        ("in_one_line", parts["in_one_line"]),
    ]
    news_results = {}
    for name, text in news_jobs:
        print(f"[SING01-AUDIO] {name}生成...")
        out_path = f"{NARRATION_DIR}/{name}.wav"
        r = generate_news_narration_verified(text, out_path)
        news_results[name] = r
        print(f"[SING01-AUDIO] {name}: status={r.get('status')}")

    with open(f"{OUT_DIR}/audit/segment_generation_results.json", "w", encoding="utf-8") as f:
        json.dump({"topic_intro": topic_intro_result, "preview": preview_result,
                    **comment_results, **news_results}, f, ensure_ascii=False, indent=2, default=str)

    all_results = {"preview": preview_result, "topic_intro": topic_intro_result, **comment_results, **news_results}
    failed = [k for k, v in all_results.items() if v.get("status") != "OK"]
    if failed:
        print(f"[SING01-AUDIO] 生成失敗segmentあり、中断します: {failed}")
        return

    # --- Step 5: Key Phrase Components(English) + Japanese meaning ---
    kp_items = sorted(kp_canon["items"], key=lambda it: it["rank"])
    kp_results = {}
    for item in kp_items:
        rank = item["rank"]
        used_form = item["used_form"]
        ja_gloss = item["japanese_gloss"]
        print(f"[SING01-AUDIO] Key Phrase {rank} 英語Component生成: {used_form!r}...")
        en_path = f"{NARRATION_DIR}/kp{rank}_en.wav"
        en_result = repro01.generate_key_phrase_component_verified(used_form, en_path)
        print(f"[SING01-AUDIO] Key Phrase {rank} 日本語meaning生成: {ja_gloss!r}...")
        ja_path = f"{NARRATION_DIR}/kp{rank}_ja.wav"
        ja_result = repro01.generate_narration_snippet_verified_strict(
            ja_gloss, "ja", ja_path, ja_gloss[:4])
        kp_results[rank] = {"english": en_result, "japanese": ja_result}
        print(f"[SING01-AUDIO] Key Phrase {rank}: en={en_result.get('status')} ja={ja_result.get('status')}")

    with open(f"{OUT_DIR}/audit/key_phrase_generation_results.json", "w", encoding="utf-8") as f:
        json.dump(kp_results, f, ensure_ascii=False, indent=2, default=str)

    kp_failed = [r for r, v in kp_results.items()
                 if v["english"].get("status") != "OK" or v["japanese"].get("status") != "OK"]
    if kp_failed:
        print(f"[SING01-AUDIO] Key Phrase生成失敗あり、中断します: {kp_failed}")
        return

    summary = {
        "status": "OK", "article_id": ARTICLE_ID,
        "segment_status": {k: v.get("status") for k, v in all_results.items()},
        "key_phrase_status": {r: {"en": v["english"].get("status"), "ja": v["japanese"].get("status")}
                               for r, v in kp_results.items()},
        "support_ledger_status": safety_result["ledger_deviation"]["overall_status"],
        "support_fact_status": safety_result["fact_check"]["final_status"],
        "support_fact_verdict": (safety_result["fact_check"]["result"] or {}).get("verdict"),
    }
    with open(f"{OUT_DIR}/run_summary_content.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    print("[SING01-AUDIO] 全content生成完了。summary:", json.dumps(summary, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
