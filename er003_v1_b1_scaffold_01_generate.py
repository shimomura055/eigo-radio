# ============================================================
# er003_v1_b1_scaffold_01_generate.py
# ER-003-B1-SCAFFOLD-01: B1 Supported Natural English Prototype
# ============================================================
# B1をB2専用英文の別生成ではなく、「B2と完全共通のNatural English本文
# + 易しいListening Support英語(Preview/Comment1-4) + Key Phrases
# (English->Japanese->English)」という支援量で成立させられるかを検証
# する。ニュース本文(Full Story Part1/Part2/Point One/Point Two/
# In One Line)はER-003-CEFR-DIRECT-02のB2 V2版を一字一句そのまま使用し、
# 新しいニュース英文は一切生成しない。
#
# Key Phrase選定(Strategy L + Canonicalization)はProduction機構
# (er003_key_words_production.py/er003_key_words_min_unit.py/
# er003_key_words_canonicalization.py/er003_b1_p2_keywords.py)を
# 読み取り専用でimportし、er003_v1_a2_kp_select_generate.pyと同一の
# 呼び出しパターンで再利用する(新しい選定ロジックは設計しない)。
# Number Treatment分類はer003_v1_spoken_first_01_generate.run_
# classificationをそのまま再利用する(監査のみ、本文書き換えは行わない)。
#
# Production(CURRENT_SPEC.md、R4 Production prompt、上記の各Production
# モジュール本体)は一切変更せず、この独立スクリプトから関数を読み取り
# 専用でimportするのみ。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_b1_scaffold_01_generate.py

from __future__ import annotations

import json
import os
import re
import time

from dotenv import load_dotenv

import er002_ja_web_research_r3 as r3
import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_en_direct_ab_01_generate as ab01
import er003_v1_spoken_first_01_generate as sf1
import er003_v1_spoken_first_01_r1_generate as sf1r1
import er003_b1_p2_keywords as bk
import er003_key_words_canonicalization as kc
import er003_key_words_production as prod
import er003_natural_source as natural_source

load_dotenv()

ARTICLE_ID = "A02"
TOPIC = "英国の未成年向け夜間SNS設定"
B2_ARTICLE_PATH = "er003_output/cefr_direct_02/A02/B2_v2/article.md"
LEDGER_TEXT_PATH = "er003_output/en_direct_vfl_01/A02/verified_fact_ledger.txt"
OUT_DIR = "er003_output/b1_scaffold_01/A02"

MODEL = vfl01.MODEL
REASONING_EFFORT = vfl01.REASONING_EFFORT

PART1_SPLIT_MARKER = "And the plan does not stop at bedtime."

sha256_text = natural_source.sha256_text


def get_client():
    return vfl01.get_client()


def load_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


# ============================================================
# Step 0: 固定B2本文をParts / Points / In One Lineへ分割(語を一切変更しない)
# ============================================================
def split_fixed_news_text(b2_text: str) -> dict:
    """sf1r1.split_sectionsは###見出し行自体を捨てて本文のみを集計する
    ため(word count専用に設計されている)、見出しテキストが必要な
    Point One/Twoの分割には使えない。ここでは生のMarkdownを直接
    正規表現で解析し、見出し行を保持したまま分割する。"""
    title_match = re.match(r"^#\s+(.+?)\s*\n", b2_text)
    title = title_match.group(1).strip() if title_match else ""

    h3_matches = list(re.finditer(r"^###\s+(.+?)\s*$", b2_text, flags=re.MULTILINE))
    if len(h3_matches) != 2:
        raise RuntimeError(f"###見出しがちょうど2つではありません(検出数: {len(h3_matches)})。固定B2本文が想定と異なります。")
    in_one_line_match = re.search(r"^##\s+In one line[…\.]*\s*\n(.+)", b2_text, flags=re.MULTILINE | re.DOTALL)
    if not in_one_line_match:
        raise RuntimeError("『## In one line…』見出しが見つかりません。固定B2本文が想定と異なります。")

    intro_text = b2_text[title_match.end():h3_matches[0].start()].strip() if title_match else b2_text[:h3_matches[0].start()].strip()
    point_one_heading = h3_matches[0].group(1).strip()
    point_one_body = b2_text[h3_matches[0].end():h3_matches[1].start()].strip()
    point_two_heading = h3_matches[1].group(1).strip()
    point_two_body = b2_text[h3_matches[1].end():in_one_line_match.start()].strip()
    in_one_line_text = in_one_line_match.group(1).strip()

    if PART1_SPLIT_MARKER not in intro_text:
        raise RuntimeError(
            f"Part1/Part2分割マーカー『{PART1_SPLIT_MARKER}』がMain Storyに見つかりません。"
            "固定B2本文が変更された可能性があります。"
        )
    idx = intro_text.index(PART1_SPLIT_MARKER)
    part1 = intro_text[:idx].strip()
    part2 = intro_text[idx:].strip()

    return {
        "title": title, "part1": part1, "part2": part2,
        "point_one_heading": point_one_heading, "point_one_body": point_one_body,
        "point_two_heading": point_two_heading, "point_two_body": point_two_body,
        "in_one_line": in_one_line_text,
    }


# ============================================================
# Step 1: Listening Support英語(Preview / Comment 1-4)
# ============================================================
SUPPORT_DEVELOPER_MESSAGE = "英語のListening Support原稿を作成してください。"

SUPPORT_ENGLISH_PRINCIPLE = """Use very clear, easy spoken English. The listener should understand it immediately on the first listen. Say one simple idea at a time. Prefer familiar everyday wording. Make the relationship between ideas explicit. Avoid compressed explanations, abstract wording, or idiomatic expressions that require interpretation. The purpose is to help the listener understand the harder news English that comes next, not to teach more difficult English. Keep the tone natural and adult, but make comprehension effortless."""

SUPPORT_PROHIBITIONS = """【禁止事項(重要)】
- 本文にない新しい具体的Factを追加しない
- Verified Fact Ledgerに存在しないFactを追加しない
- 本文が述べていない因果関係を新たに説明しない
- 過度な一般化をしない
- 本文より強い断定をしない
- 推測を書かない
- Point One/Twoの答え(結論)を先出ししない
- 本文の長いparaphraseにしない(本文を全部言い換えて説明し直さない)
- Support英語自体を学習課題にしない(難しい言い換え・比喩・抽象語を増やさない)
- 一度に複数の論点を詰め込まない"""


def build_support_prompt(role_instruction: str, context_block: str) -> str:
    return f"""{role_instruction}

{SUPPORT_ENGLISH_PRINCIPLE}

{SUPPORT_PROHIBITIONS}

{context_block}

【出力形式】
英語の地の文だけを出力してください。見出し・箇条書き・引用符・Markdown記法は使わないでください。"""


COMMENT_1_ROLE = """あなたはPodcastのナビゲーターです。これから、あるニュースのFull Story Part 1
(本文前半、易しくない自然な英語)をリスナーが聞きます。その直前に流す、Comment 1
(役割: Listening Focus)を書いてください。

役割: リスナーが次に何を聞けばよいか、注目点を示します。答え・結論を先に言っては
いけません。原則1文の、非常に短いListening Focusにしてください。"""

COMMENT_2_ROLE = """あなたはPodcastのナビゲーターです。リスナーはFull Story Part 1(本文前半)を
すでに聞き終わり、これからFull Story Part 2(本文後半)を聞きます。その間に流す、
Comment 2(役割: Mid-story Recovery + Next Question)を書いてください。

役割: Part 1で聞いた内容の核心を1点だけ短く回収し、Part 2で何を聞けばよいかという
問いを提示します。長いsummaryにしないでください。本文を英語で言い換え直して全部
説明してはいけません。1〜2文にしてください。"""

COMMENT_3_ROLE = """あなたはPodcastのナビゲーターです。リスナーはFull Story Part 1・Part 2
(本文全体)をすでに聞き終わり、これからPoint One・Point Two(補足の視点)を
聞きます。その間に流す、Comment 3(役割: Story Meaning + Bridge to Points)を
書いてください。

役割: このニュース全体の意味を短く整理し、これから聞くPointへの橋渡しをします。
Pointの具体的な内容(答え)を先に言ってはいけません。新しいFactを追加しないで
ください。易しい英語で2〜3文にしてください。"""

COMMENT_4_ROLE = """あなたはPodcastのナビゲーターです。リスナーはPoint One・Point Twoを
すでに聞き終わり、これからIn One Line(結びのまとめ)を聞きます。その間に流す、
Comment 4(役割: Point Recovery + Bridge to In One Line)を書いてください。

役割: 2つのPointの意味を軽く回収し、In One Lineへつなぎます。Pointの内容を
再説明しすぎないでください。2〜3文にしてください。

注意: In One Lineの実際のsentence数は記事により異なります(1文とは限り
ません)。「一文で」「one sentenceで」「一言で」等、sentence数を断定する
表現は使わないでください。"""

PREVIEW_ROLE = """あなたはPodcastの冒頭を担当するナビゲーターです。これからリスナーは、
このエピソードのニュース本文(Preview・Key Phrasesに続いてMain Story・Points・
In One Line)を聞きます。エピソードの一番最初に流すPreviewを書いてください。

役割: このニュースの
- theme(何についての話か)
- problem(何が問題・論点か)
- value(なぜ聞く価値があるか)
- question(聞き終える頃に何が分かるようになるか)
を短く提示し、リスナーの関心を引きます。

以下は避けてください:
- 答えを先に言う
- 重要な数字を先出しする
- 結論を先に言う
- turning point(展開の転換点)を先に明かす
- 後で流れるComment 1・Comment 2と内容が重複する

Comment 1・Comment 2は以下の通りです。これらと重複する内容にしないでください。
【Comment 1】
{comment_1}

【Comment 2】
{comment_2}"""


def run_support_text(client, role_instruction: str, context_block: str, max_attempts: int = 2,
                      model: str = MODEL) -> dict:
    """modelはER-006-MODEL-ROUTING-CONTRACT-01以降、呼び出し側がSSOT経由で
    明示指定できる(未指定時はモジュール既定のMODEL)。"""
    prompt = build_support_prompt(role_instruction, context_block)
    attempts = []
    for attempt in range(1, max_attempts + 1):
        try:
            response = client.responses.create(
                model=model,
                reasoning={"effort": REASONING_EFFORT},
                input=[
                    {"role": "developer", "content": SUPPORT_DEVELOPER_MESSAGE},
                    {"role": "user", "content": prompt},
                ],
            )
            text = (response.output_text or "").strip()
            if not text:
                raise RuntimeError("support応答が空です")
            attempts.append({"attempt": attempt, "status": "OK", "model": response.model,
                              "response_id": response.id, "raw_text": text})
            return {"status": "OK", "text": text, "prompt": prompt, "attempts": attempts}
        except Exception as e:
            attempts.append({"attempt": attempt, "status": "TECHNICAL_FAILED", "error": f"{type(e).__name__}: {e}"})
            if attempt < max_attempts:
                time.sleep(2)
                continue
            return {"status": "TECHNICAL_GENERATION_FAILED", "text": None, "prompt": prompt, "attempts": attempts}
    return {"status": "TECHNICAL_GENERATION_FAILED", "text": None, "prompt": prompt, "attempts": attempts}


# ============================================================
# Step 2: Key Phrases(Strategy L選定 + Canonicalization、B2本文全体に適用)
# ============================================================
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


def run_key_phrase_canonicalization(article_text: str, original_items: list, out_dir: str) -> dict:
    template = kc.load_prompt_template()
    user_message = kc.build_user_message(original_items, article_text, template=template)
    with open(f"{out_dir}/canonicalization_prompt.txt", "w", encoding="utf-8") as f:
        f.write(user_message)

    def make_factory():
        return kc.make_canonicalization_fn(user_message)

    parsed, status, attempts, model_id, response_id = kc.run_canonicalization_gate(make_factory, original_items)
    with open(f"{out_dir}/canonicalization_runtime_metadata.json", "w", encoding="utf-8") as f:
        json.dump({
            "article_id": ARTICLE_ID, "canonicalization_version": kc.CANONICALIZATION_VERSION,
            "record_status": "PROTOTYPE", "approval_status": "NOT_APPROVED",
            "final_status": status, "model_id": model_id, "response_id": response_id,
            "attempts_detail": [{k: v for k, v in a.items() if k != "raw_text"} for a in attempts],
        }, f, ensure_ascii=False, indent=2)

    result = {"status": status}
    if status not in ("CANONICALIZATION_PASS", "CANONICALIZATION_REVIEW_REQUIRED"):
        return result
    merged = kc.merge_canonicalization_result(original_items, parsed["items"])
    with open(f"{out_dir}/keywords_canonicalized.json", "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    result["merged"] = merged
    return result


# ============================================================
# メイン実行
# ============================================================
def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(f"{OUT_DIR}/audit", exist_ok=True)
    client = get_client()

    b2_text = load_text(B2_ARTICLE_PATH)
    ledger_text = load_text(LEDGER_TEXT_PATH)
    parts = split_fixed_news_text(b2_text)
    with open(f"{OUT_DIR}/fixed_news_parts.json", "w", encoding="utf-8") as f:
        json.dump(parts, f, ensure_ascii=False, indent=2)
    print(f"[B1-SCAFFOLD] 固定B2本文分割完了: part1={ab01.compute_word_count(parts['part1'])}語 "
          f"part2={ab01.compute_word_count(parts['part2'])}語")

    # --- Comment 1〜4 ---
    print("[B1-SCAFFOLD] Comment 1生成開始...")
    c1_context = f"【Full Story Part 1(これから聞く本文)】\n{parts['part1']}"
    c1_result = run_support_text(client, COMMENT_1_ROLE, c1_context)

    print("[B1-SCAFFOLD] Comment 2生成開始...")
    c2_context = f"【Full Story Part 1(聞き終えた本文)】\n{parts['part1']}\n\n【Full Story Part 2(これから聞く本文)】\n{parts['part2']}"
    c2_result = run_support_text(client, COMMENT_2_ROLE, c2_context)

    print("[B1-SCAFFOLD] Comment 3生成開始...")
    c3_context = (f"【Full Story Part 1】\n{parts['part1']}\n\n【Full Story Part 2】\n{parts['part2']}\n\n"
                  f"【これから聞くPointの見出しのみ(内容は伏せる)】\n"
                  f"Point One heading: {parts['point_one_heading']}\nPoint Two heading: {parts['point_two_heading']}")
    c3_result = run_support_text(client, COMMENT_3_ROLE, c3_context)

    print("[B1-SCAFFOLD] Comment 4生成開始...")
    c4_context = (f"【Point One(聞き終えた内容)】\n{parts['point_one_heading']}\n{parts['point_one_body']}\n\n"
                  f"【Point Two(聞き終えた内容)】\n{parts['point_two_heading']}\n{parts['point_two_body']}\n\n"
                  f"【これから聞くIn One Line】\n{parts['in_one_line']}")
    c4_result = run_support_text(client, COMMENT_4_ROLE, c4_context)

    comments = {"comment_1": c1_result, "comment_2": c2_result, "comment_3": c3_result, "comment_4": c4_result}
    for key, result in comments.items():
        with open(f"{OUT_DIR}/audit/{key}_attempts.json", "w", encoding="utf-8") as f:
            json.dump(result["attempts"], f, ensure_ascii=False, indent=2, default=str)
        if result["status"] != "OK":
            print(f"[B1-SCAFFOLD] {key}生成失敗: {result['status']}")

    # --- Preview(Comment1/2完成後に生成し、重複を避ける) ---
    print("[B1-SCAFFOLD] Preview生成開始...")
    preview_role = PREVIEW_ROLE.format(
        comment_1=c1_result.get("text") or "(生成失敗)",
        comment_2=c2_result.get("text") or "(生成失敗)",
    )
    preview_context = f"【エピソード全文(参考、新しいFactの追加禁止)】\n{b2_text}"
    preview_result = run_support_text(client, preview_role, preview_context)
    with open(f"{OUT_DIR}/audit/preview_attempts.json", "w", encoding="utf-8") as f:
        json.dump(preview_result["attempts"], f, ensure_ascii=False, indent=2, default=str)

    support_texts = {
        "preview": preview_result.get("text"), "comment_1": c1_result.get("text"),
        "comment_2": c2_result.get("text"), "comment_3": c3_result.get("text"),
        "comment_4": c4_result.get("text"),
    }
    with open(f"{OUT_DIR}/support_texts.json", "w", encoding="utf-8") as f:
        json.dump(support_texts, f, ensure_ascii=False, indent=2)

    # --- Key Phrases(B2本文全体に対してStrategy L + Canonicalization) ---
    kp_dir = f"{OUT_DIR}/key_phrases"
    print("[B1-SCAFFOLD] Key Phrase選定開始...")
    kp_selection = run_key_phrase_selection(b2_text, kp_dir)
    print(f"[B1-SCAFFOLD] Key Phrase選定status={kp_selection['status']}")
    kp_final = None
    if kp_selection["status"] == "KEY_WORDS_STRUCTURE_PASS":
        print("[B1-SCAFFOLD] Key Phrase Canonicalization開始...")
        kp_canon = run_key_phrase_canonicalization(b2_text, kp_selection["original_items"], kp_dir)
        print(f"[B1-SCAFFOLD] Canonicalization status={kp_canon['status']}")
        kp_final = kp_canon.get("merged")

    # --- Number Treatment Audit(監査のみ、本文は書き換えない) ---
    print("[B1-SCAFFOLD] Number Treatment監査開始...")
    number_audit = sf1.run_classification(client, b2_text, ledger_text)
    with open(f"{OUT_DIR}/number_treatment_audit.json", "w", encoding="utf-8") as f:
        json.dump(number_audit["parsed"], f, ensure_ascii=False, indent=2)
    print(f"[B1-SCAFFOLD] Number Treatment監査完了: numbers={len(number_audit['parsed']['numbers'])}")

    # --- Fact Safety(Support部分のみ。ニュース本文はDIRECT-02で検証済みのため対象外) ---
    support_concat = "\n\n".join(t for t in support_texts.values() if t)
    print("[B1-SCAFFOLD] Support Ledger Deviation Check開始...")
    deviation_result = vfl01.run_deviation_check(client, ledger_text, support_concat)
    with open(f"{OUT_DIR}/support_ledger_deviation.json", "w", encoding="utf-8") as f:
        json.dump(deviation_result["parsed"], f, ensure_ascii=False, indent=2)
    print(f"[B1-SCAFFOLD] deviation overall_status={deviation_result['parsed']['overall_status']} "
          f"deviations={len(deviation_result['parsed']['deviations'])}")

    print("[B1-SCAFFOLD] Support Fact Check開始...")
    fc_prompt = r3.build_fact_check_prompt(TOPIC, support_concat, [])

    def make_fc_fn():
        return r3.make_fact_checker_fn(fc_prompt)

    fc_result, fc_status, fc_attempts, fc_model, fc_response_id, fc_search_usage, fc_sources = r3.run_fact_checker_with_gates(
        make_fc_fn, sleep_fn=time.sleep)
    verdict = fc_result.get("verdict") if fc_result else None
    print(f"[B1-SCAFFOLD] Support fact_check status={fc_status} verdict={verdict}")
    with open(f"{OUT_DIR}/support_fact_qa.json", "w", encoding="utf-8") as f:
        json.dump({"final_status": fc_status, "result": fc_result}, f, ensure_ascii=False, indent=2)

    # --- 完成版B1 Supported Scriptの組み立て(11パート) ---
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
        "article_id": ARTICLE_ID, "b2_source_path": B2_ARTICLE_PATH, "b2_source_sha256": sha256_text(b2_text),
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
    print("[B1-SCAFFOLD] 完了。summary:", json.dumps(summary, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
