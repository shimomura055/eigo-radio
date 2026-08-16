# ============================================================
# er003_v1_iran01_b1_generate.py
# ER-003-IRAN-A2-B1-01: IRAN01 B1 Support(Preview/Comment1-4)+
# Key Phrase(方式L+Canonicalization)生成
# ============================================================
# er003_v1_b1_scaffold_01_generate.py(ER-003-B1-SCAFFOLD-01)の
# ロジックをそのまま再利用する。B2本文(Full Story/Point/In One Line)
# は一字一句変更せず、Preview/Comment1-4という易しいSupport英語のみ
# 新規生成する。新しいニュース英文は生成しない。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_iran01_b1_generate.py

from __future__ import annotations

import json
import os
import time

from dotenv import load_dotenv

import er002_ja_web_research_r3 as r3
import er003_b1_p2_keywords as bk
import er003_key_words_canonicalization as kc
import er003_key_words_production as prod
import er003_v1_b1_scaffold_01_generate as b1s
import er003_v1_en_direct_ab_01_generate as ab01
import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_iran01_articles_generate as gen
import er003_v1_spoken_first_01_generate as sf1

load_dotenv()

ARTICLE_ID = "IRAN01_B1"
TOPIC = gen.TOPIC
B2_ARTICLE_PATH = f"{gen.OUT_DIR}/b2/article.md"
LEDGER_TEXT_PATH = gen.LEDGER_TEXT_PATH
OUT_DIR = f"{gen.OUT_DIR}/b1"

PART1_SPLIT_MARKER = "But while Washington and Tehran traded words about control"


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(f"{OUT_DIR}/audit", exist_ok=True)
    client = b1s.get_client()

    b2_text = b1s.load_text(B2_ARTICLE_PATH)
    ledger_text = b1s.load_text(LEDGER_TEXT_PATH)
    parts = split_fixed_news_text(b2_text)
    with open(f"{OUT_DIR}/fixed_news_parts.json", "w", encoding="utf-8") as f:
        json.dump(parts, f, ensure_ascii=False, indent=2)
    print(f"[IRAN01-B1] 固定B2本文分割完了: part1={ab01.compute_word_count(parts['part1'])}語 "
          f"part2={ab01.compute_word_count(parts['part2'])}語")

    print("[IRAN01-B1] Comment 1生成開始...")
    c1_context = f"【Full Story Part 1(これから聞く本文)】\n{parts['part1']}"
    c1_result = b1s.run_support_text(client, b1s.COMMENT_1_ROLE, c1_context)

    print("[IRAN01-B1] Comment 2生成開始...")
    c2_context = f"【Full Story Part 1(聞き終えた本文)】\n{parts['part1']}\n\n【Full Story Part 2(これから聞く本文)】\n{parts['part2']}"
    c2_result = b1s.run_support_text(client, b1s.COMMENT_2_ROLE, c2_context)

    print("[IRAN01-B1] Comment 3生成開始...")
    c3_context = (f"【Full Story Part 1】\n{parts['part1']}\n\n【Full Story Part 2】\n{parts['part2']}\n\n"
                  f"【これから聞くPointの見出しのみ(内容は伏せる)】\n"
                  f"Point One heading: {parts['point_one_heading']}\nPoint Two heading: {parts['point_two_heading']}")
    c3_result = b1s.run_support_text(client, b1s.COMMENT_3_ROLE, c3_context)

    print("[IRAN01-B1] Comment 4生成開始...")
    c4_context = (f"【Point One(聞き終えた内容)】\n{parts['point_one_heading']}\n{parts['point_one_body']}\n\n"
                  f"【Point Two(聞き終えた内容)】\n{parts['point_two_heading']}\n{parts['point_two_body']}\n\n"
                  f"【これから聞くIn One Line】\n{parts['in_one_line']}")
    c4_result = b1s.run_support_text(client, b1s.COMMENT_4_ROLE, c4_context)

    comments = {"comment_1": c1_result, "comment_2": c2_result, "comment_3": c3_result, "comment_4": c4_result}
    for key, result in comments.items():
        with open(f"{OUT_DIR}/audit/{key}_attempts.json", "w", encoding="utf-8") as f:
            json.dump(result["attempts"], f, ensure_ascii=False, indent=2, default=str)
        if result["status"] != "OK":
            print(f"[IRAN01-B1] {key}生成失敗: {result['status']}")

    print("[IRAN01-B1] Preview生成開始...")
    preview_role = b1s.PREVIEW_ROLE.format(
        comment_1=c1_result.get("text") or "(生成失敗)",
        comment_2=c2_result.get("text") or "(生成失敗)",
    )
    preview_context = f"【エピソード全文(参考、新しいFactの追加禁止)】\n{b2_text}"
    preview_result = b1s.run_support_text(client, preview_role, preview_context)
    with open(f"{OUT_DIR}/audit/preview_attempts.json", "w", encoding="utf-8") as f:
        json.dump(preview_result["attempts"], f, ensure_ascii=False, indent=2, default=str)

    support_texts = {
        "preview": preview_result.get("text"), "comment_1": c1_result.get("text"),
        "comment_2": c2_result.get("text"), "comment_3": c3_result.get("text"),
        "comment_4": c4_result.get("text"),
    }
    with open(f"{OUT_DIR}/support_texts.json", "w", encoding="utf-8") as f:
        json.dump(support_texts, f, ensure_ascii=False, indent=2)

    kp_dir = f"{OUT_DIR}/key_phrases"
    print("[IRAN01-B1] Key Phrase選定開始(B1最終テキスト全体から)...")
    kp_selection = run_key_phrase_selection(b2_text, kp_dir)
    print(f"[IRAN01-B1] Key Phrase選定status={kp_selection['status']}")
    kp_final = None
    if kp_selection["status"] == "KEY_WORDS_STRUCTURE_PASS":
        print("[IRAN01-B1] Key Phrase Canonicalization開始...")
        kp_canon = b1s.run_key_phrase_canonicalization(b2_text, kp_selection["original_items"], kp_dir)
        print(f"[IRAN01-B1] Canonicalization status={kp_canon['status']}")
        kp_final = kp_canon.get("merged")

    print("[IRAN01-B1] Number Treatment監査開始...")
    number_audit = sf1.run_classification(client, b2_text, ledger_text)
    with open(f"{OUT_DIR}/number_treatment_audit.json", "w", encoding="utf-8") as f:
        json.dump(number_audit["parsed"], f, ensure_ascii=False, indent=2)
    print(f"[IRAN01-B1] Number Treatment監査完了: numbers={len(number_audit['parsed']['numbers'])}")

    support_concat = "\n\n".join(t for t in support_texts.values() if t)
    print("[IRAN01-B1] Support Ledger Deviation Check開始...")
    deviation_result = vfl01.run_deviation_check(client, ledger_text, support_concat)
    with open(f"{OUT_DIR}/support_ledger_deviation.json", "w", encoding="utf-8") as f:
        json.dump(deviation_result["parsed"], f, ensure_ascii=False, indent=2)
    print(f"[IRAN01-B1] deviation overall_status={deviation_result['parsed']['overall_status']} "
          f"deviations={len(deviation_result['parsed']['deviations'])}")

    print("[IRAN01-B1] Support Fact Check開始...")
    fc_prompt = r3.build_fact_check_prompt(TOPIC, support_concat, [])

    def make_fc_fn():
        return r3.make_fact_checker_fn(fc_prompt)

    fc_result, fc_status, fc_attempts, fc_model, fc_response_id, fc_search_usage, fc_sources = r3.run_fact_checker_with_gates(
        make_fc_fn, sleep_fn=time.sleep)
    verdict = fc_result.get("verdict") if fc_result else None
    print(f"[IRAN01-B1] Support fact_check status={fc_status} verdict={verdict}")
    with open(f"{OUT_DIR}/support_fact_qa.json", "w", encoding="utf-8") as f:
        json.dump({"final_status": fc_status, "result": fc_result}, f, ensure_ascii=False, indent=2)

    script_lines = [
        f"# B1 Supported Natural English — {parts['title']}", "",
        "## 1. Preview", support_texts["preview"] or "(生成失敗)", "",
        "## 2. Key Phrases",
    ]
    if kp_final:
        for item in kp_final["items"]:
            script_lines.append(f"{item['rank']}. {item['used_form']} — {item['japanese_gloss']} — {item['used_form']}")
    else:
        script_lines.append("(Key Phrase選定未完了)")
    script_lines += [
        "", "## 3. Comment 1", support_texts["comment_1"] or "(生成失敗)", "",
        "## 4. Full Story Part 1(B2共通、無変更)", parts["part1"], "",
        "## 5. Comment 2", support_texts["comment_2"] or "(生成失敗)", "",
        "## 6. Full Story Part 2(B2共通、無変更)", parts["part2"], "",
        "## 7. Comment 3", support_texts["comment_3"] or "(生成失敗)", "",
        "## 8. Point One(B2共通、無変更)", f"### {parts['point_one_heading']}", parts["point_one_body"], "",
        "## 9. Point Two(B2共通、無変更)", f"### {parts['point_two_heading']}", parts["point_two_body"], "",
        "## 10. Comment 4", support_texts["comment_4"] or "(生成失敗)", "",
        "## 11. In One Line(B2共通、無変更)", parts["in_one_line"],
    ]
    with open(f"{OUT_DIR}/b1_supported_script.md", "w", encoding="utf-8") as f:
        f.write("\n".join(script_lines))

    summary = {
        "article_id": ARTICLE_ID, "b2_source_path": B2_ARTICLE_PATH, "b2_source_sha256": b1s.sha256_text(b2_text),
        "comment_status": {k: v["status"] for k, v in comments.items()},
        "preview_status": preview_result["status"],
        "key_phrase_selection_status": kp_selection["status"],
        "key_phrase_canonicalization_status": (kp_final is not None),
        "number_treatment_count": len(number_audit["parsed"]["numbers"]),
        "support_ledger_status": deviation_result["parsed"]["overall_status"],
        "support_ledger_deviation_count": len(deviation_result["parsed"]["deviations"]),
        "support_fact_status": fc_status, "support_fact_verdict": verdict,
    }
    with open(f"{OUT_DIR}/run_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    print("[IRAN01-B1] 完了。summary:", json.dumps(summary, ensure_ascii=False, default=str))


def split_fixed_news_text(b2_text: str) -> dict:
    import re
    title_match = re.match(r"^#\s+(.+?)\s*\n", b2_text)
    title = title_match.group(1).strip() if title_match else ""

    h3_matches = list(re.finditer(r"^###\s+(.+?)\s*$", b2_text, flags=re.MULTILINE))
    if len(h3_matches) != 2:
        raise RuntimeError(f"###見出しがちょうど2つではありません(検出数: {len(h3_matches)})。")
    in_one_line_match = re.search(r"^##\s+In one line[…\.]*\s*\n(.+)", b2_text, flags=re.MULTILINE | re.DOTALL)
    if not in_one_line_match:
        raise RuntimeError("『## In one line…』見出しが見つかりません。")

    intro_text = b2_text[title_match.end():h3_matches[0].start()].strip() if title_match else b2_text[:h3_matches[0].start()].strip()
    point_one_heading = h3_matches[0].group(1).strip()
    point_one_body = b2_text[h3_matches[0].end():h3_matches[1].start()].strip()
    point_two_heading = h3_matches[1].group(1).strip()
    point_two_body = b2_text[h3_matches[1].end():in_one_line_match.start()].strip()
    in_one_line_text = in_one_line_match.group(1).strip()

    if PART1_SPLIT_MARKER not in intro_text:
        raise RuntimeError(f"Part1/Part2分割マーカー『{PART1_SPLIT_MARKER}』がMain Storyに見つかりません。")
    idx = intro_text.index(PART1_SPLIT_MARKER)
    part1 = intro_text[:idx].strip()
    part2 = intro_text[idx:].strip()

    return {
        "title": title, "part1": part1, "part2": part2,
        "point_one_heading": point_one_heading, "point_one_body": point_one_body,
        "point_two_heading": point_two_heading, "point_two_body": point_two_body,
        "in_one_line": in_one_line_text,
    }


def run_key_phrase_selection(article_text: str, out_dir: str) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    template = bk.load_prompt_template()
    user_message = bk.build_user_message(article_text, template=template)
    with open(f"{out_dir}/keywords_selector_prompt.txt", "w", encoding="utf-8") as f:
        f.write(user_message)

    def make_selector_factory():
        return bk.make_selector_fn(user_message)

    parsed, status, attempts, model_id, response_id = prod.run_production_selection_gate(
        ARTICLE_ID, make_selector_factory, article_text,
        strategy_id=prod.STANDARD_STRATEGY_ID, max_attempts=1,
    )
    runtime_metadata = {
        "article_id": ARTICLE_ID, "strategy_id": prod.STANDARD_STRATEGY_ID, "source_level": "B1_SUPPORTED(B2本文共有)",
        "record_status": "PROTOTYPE", "approval_status": "NOT_APPROVED",
        "model": bk.SELECTOR_MODEL, "reasoning_effort": bk.SELECTOR_REASONING_EFFORT,
        "final_status": status, "model_id": model_id, "response_id": response_id,
        "attempts_detail": [{k: v for k, v in a.items() if k != "raw_text"} for a in attempts],
    }
    with open(f"{out_dir}/keywords_runtime_metadata.json", "w", encoding="utf-8") as f:
        json.dump(runtime_metadata, f, ensure_ascii=False, indent=2)

    result = {"status": status, "parsed": parsed}
    if status != "KEY_WORDS_STRUCTURE_PASS":
        return result
    result["original_items"] = parsed["items"]
    return result


if __name__ == "__main__":
    main()
