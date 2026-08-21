# ============================================================
# er003_v1_iran01_a2_generate.py
# ER-003-IRAN-A2-B1-01: IRAN01 A2 Preview/Comment1-4(日本語)+
# Key Phrase(方式L+Canonicalization、A2最終本文から独自選定)生成
# ============================================================
# CURRENT_SPEC.mdのA2仕様(Preview言語=日本語のみ、単一Aoede voice、
# Comment役割はB1と同じ定義=Listening Focus/Mid-story Recovery+Next
# Question/Story Meaning+Bridge/Point Recovery+Bridge)に基づく。
# 今回のB1 Voice AllocationをA2へ移植しない(ユーザー明示指示)。
# A2の英文本文(Full Story/Point/In One Line)は一切変更せず、日本語の
# Preview/Comment1-4のみを新規生成する。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_iran01_a2_generate.py

from __future__ import annotations

import json
import os
import re
import time

from dotenv import load_dotenv

import er002_ja_web_research_r3 as r3
import er003_b1_p2_keywords as bk
import er003_key_words_canonicalization as kc
import er003_key_words_production as prod
import er003_v1_en_direct_ab_01_generate as ab01
import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_iran01_articles_generate as gen

load_dotenv()

ARTICLE_ID = "IRAN01_A2"
TOPIC = gen.TOPIC
A2_ARTICLE_PATH = f"{gen.OUT_DIR}/a2/article.md"
LEDGER_TEXT_PATH = gen.LEDGER_TEXT_PATH
OUT_DIR = f"{gen.OUT_DIR}/a2"

MODEL = vfl01.MODEL
REASONING_EFFORT = vfl01.REASONING_EFFORT

PART1_SPLIT_MARKER = "Then, on August 15, a quieter but more practical development arrived."


def get_client():
    return vfl01.get_client()


def load_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def split_fixed_news_text(a2_text: str) -> dict:
    title_match = re.match(r"^#\s+(.+?)\s*\n", a2_text)
    title = title_match.group(1).strip() if title_match else ""

    h3_matches = list(re.finditer(r"^###\s+(.+?)\s*$", a2_text, flags=re.MULTILINE))
    if len(h3_matches) != 2:
        raise RuntimeError(f"###見出しがちょうど2つではありません(検出数: {len(h3_matches)})。")
    in_one_line_match = re.search(r"^##\s+In one line[…\.]*\s*\n(.+)", a2_text, flags=re.MULTILINE | re.DOTALL)
    if not in_one_line_match:
        raise RuntimeError("『## In one line…』見出しが見つかりません。")

    intro_text = a2_text[title_match.end():h3_matches[0].start()].strip() if title_match else a2_text[:h3_matches[0].start()].strip()
    point_one_heading = h3_matches[0].group(1).strip()
    point_one_body = a2_text[h3_matches[0].end():h3_matches[1].start()].strip()
    point_two_heading = h3_matches[1].group(1).strip()
    point_two_body = a2_text[h3_matches[1].end():in_one_line_match.start()].strip()
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


# ============================================================
# Preview/Comment1-4(日本語Listening Support、A2既存spec準拠)
# ============================================================
SUPPORT_DEVELOPER_MESSAGE = "日本語のListening Support原稿を作成してください。"

SUPPORT_JA_PRINCIPLE = """とても分かりやすく、易しい日本語を使ってください。リスナーが一度聞いただけで
理解できるようにしてください。一度に一つの考えだけを述べてください。日常的で
親しみやすい語彙を優先してください。考えと考えの関係を明示的に述べてください。
圧縮した説明・抽象的な言い回し・解釈を要する比喩表現は避けてください。目的は、
これから聞く英語のニュース本文を理解しやすくすることであり、日本語自体を学習
課題にすることではありません。トーンは自然で大人向けを保ちつつ、理解の負荷を
最小限にしてください。"""

SUPPORT_PROHIBITIONS = """【禁止事項(重要)】
- 本文にない新しい具体的Factを追加しない
- Verified Fact Ledgerに存在しないFactを追加しない
- 本文が述べていない因果関係を新たに説明しない
- 過度な一般化をしない
- 本文より強い断定をしない
- 推測を書かない
- Point One/Twoの答え(結論)を先出ししない
- 本文の長いparaphraseにしない(本文を全部言い換えて説明し直さない)
- 一度に複数の論点を詰め込まない"""


def build_support_prompt(role_instruction: str, context_block: str) -> str:
    return f"""{role_instruction}

{SUPPORT_JA_PRINCIPLE}

{SUPPORT_PROHIBITIONS}

{context_block}

【出力形式】
日本語の地の文だけを出力してください。見出し・箇条書き・引用符・Markdown記法は
使わないでください。"""


COMMENT_1_ROLE = """あなたはPodcastのナビゲーターです。これから、あるニュースのFull Story Part 1
(本文前半、英語)をリスナーが聞きます。その直前に流す、Comment 1(役割: Listening
Focus)を日本語で書いてください。

役割: リスナーが次に何を聞けばよいか、注目点を示します。答え・結論を先に言っては
いけません。原則1文の、非常に短いListening Focusにしてください。"""

COMMENT_2_ROLE = """あなたはPodcastのナビゲーターです。リスナーはFull Story Part 1(本文前半)を
すでに聞き終わり、これからFull Story Part 2(本文後半)を聞きます。その間に流す、
Comment 2(役割: Mid-story Recovery + Next Question)を日本語で書いてください。

役割: Part 1で聞いた内容の核心を1点だけ短く回収し、Part 2で何を聞けばよいかという
問いを提示します。長いsummaryにしないでください。本文を日本語で言い換え直して
全部説明してはいけません。1〜2文にしてください。"""

COMMENT_3_ROLE = """あなたはPodcastのナビゲーターです。リスナーはFull Story Part 1・Part 2
(本文全体)をすでに聞き終わり、これからPoint One・Point Two(補足の視点)を
聞きます。その間に流す、Comment 3(役割: Story Meaning + Bridge to Points)を
日本語で書いてください。

役割: このニュース全体の意味を短く整理し、これから聞くPointへの橋渡しをします。
Pointの具体的な内容(答え)を先に言ってはいけません。新しいFactを追加しないで
ください。易しい日本語で2〜3文にしてください。"""

COMMENT_4_ROLE = """あなたはPodcastのナビゲーターです。リスナーはPoint One・Point Twoを
すでに聞き終わり、これからIn One Line(結びのまとめ、英語)を聞きます。その間に流す、
Comment 4(役割: Point Recovery + Bridge to In One Line)を日本語で書いてください。

役割: 2つのPointの意味を軽く回収し、In One Lineへつなぎます。Pointの内容を
再説明しすぎないでください。2〜3文にしてください。

注意: In One Lineの実際のsentence数は記事により異なります(1文とは限り
ません)。「一文で」「one sentenceで」「一言で」等、sentence数を断定する
表現は使わないでください。"""

PREVIEW_ROLE = """あなたはPodcastの冒頭を担当するナビゲーターです。これからリスナーは、
このエピソードのニュース本文(Preview・Key Phrasesに続いてMain Story・Points・
In One Line、英語)を聞きます。エピソードの一番最初に流すPreviewを日本語で
書いてください。

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
# Key Phrases(A2最終本文から独自選定。B1 Key Phraseの機械的流用はしない)
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
        "article_id": ARTICLE_ID, "strategy_id": prod.STANDARD_STRATEGY_ID, "source_level": "A2(V2改1)",
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


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(f"{OUT_DIR}/audit", exist_ok=True)
    client = get_client()

    a2_text = load_text(A2_ARTICLE_PATH)
    ledger_text = load_text(LEDGER_TEXT_PATH)
    parts = split_fixed_news_text(a2_text)
    with open(f"{OUT_DIR}/fixed_news_parts.json", "w", encoding="utf-8") as f:
        json.dump(parts, f, ensure_ascii=False, indent=2)
    print(f"[IRAN01-A2] 固定A2本文分割完了: part1={ab01.compute_word_count(parts['part1'])}語 "
          f"part2={ab01.compute_word_count(parts['part2'])}語")

    print("[IRAN01-A2] Comment 1生成開始...")
    c1_context = f"【Full Story Part 1(これから聞く本文、英語)】\n{parts['part1']}"
    c1_result = run_support_text(client, COMMENT_1_ROLE, c1_context)

    print("[IRAN01-A2] Comment 2生成開始...")
    c2_context = f"【Full Story Part 1(聞き終えた本文)】\n{parts['part1']}\n\n【Full Story Part 2(これから聞く本文)】\n{parts['part2']}"
    c2_result = run_support_text(client, COMMENT_2_ROLE, c2_context)

    print("[IRAN01-A2] Comment 3生成開始...")
    c3_context = (f"【Full Story Part 1】\n{parts['part1']}\n\n【Full Story Part 2】\n{parts['part2']}\n\n"
                  f"【これから聞くPointの見出しのみ(内容は伏せる)】\n"
                  f"Point One heading: {parts['point_one_heading']}\nPoint Two heading: {parts['point_two_heading']}")
    c3_result = run_support_text(client, COMMENT_3_ROLE, c3_context)

    print("[IRAN01-A2] Comment 4生成開始...")
    c4_context = (f"【Point One(聞き終えた内容)】\n{parts['point_one_heading']}\n{parts['point_one_body']}\n\n"
                  f"【Point Two(聞き終えた内容)】\n{parts['point_two_heading']}\n{parts['point_two_body']}\n\n"
                  f"【これから聞くIn One Line】\n{parts['in_one_line']}")
    c4_result = run_support_text(client, COMMENT_4_ROLE, c4_context)

    comments = {"comment_1": c1_result, "comment_2": c2_result, "comment_3": c3_result, "comment_4": c4_result}
    for key, result in comments.items():
        with open(f"{OUT_DIR}/audit/{key}_attempts.json", "w", encoding="utf-8") as f:
            json.dump(result["attempts"], f, ensure_ascii=False, indent=2, default=str)
        if result["status"] != "OK":
            print(f"[IRAN01-A2] {key}生成失敗: {result['status']}")

    print("[IRAN01-A2] Preview生成開始...")
    preview_role = PREVIEW_ROLE.format(
        comment_1=c1_result.get("text") or "(生成失敗)",
        comment_2=c2_result.get("text") or "(生成失敗)",
    )
    preview_context = f"【エピソード全文(参考、新しいFactの追加禁止)】\n{a2_text}"
    preview_result = run_support_text(client, preview_role, preview_context)
    with open(f"{OUT_DIR}/audit/preview_attempts.json", "w", encoding="utf-8") as f:
        json.dump(preview_result["attempts"], f, ensure_ascii=False, indent=2, default=str)

    support_texts = {
        "preview": preview_result.get("text"), "comment_1": c1_result.get("text"),
        "comment_2": c2_result.get("text"), "comment_3": c3_result.get("text"),
        "comment_4": c4_result.get("text"),
    }
    with open(f"{OUT_DIR}/support_texts_ja.json", "w", encoding="utf-8") as f:
        json.dump(support_texts, f, ensure_ascii=False, indent=2)

    kp_dir = f"{OUT_DIR}/key_phrases"
    print("[IRAN01-A2] Key Phrase選定開始(A2最終テキスト全体から、B1とは独立)...")
    kp_selection = run_key_phrase_selection(a2_text, kp_dir)
    print(f"[IRAN01-A2] Key Phrase選定status={kp_selection['status']}")
    kp_final = None
    if kp_selection["status"] == "KEY_WORDS_STRUCTURE_PASS":
        print("[IRAN01-A2] Key Phrase Canonicalization開始...")
        kp_canon = run_key_phrase_canonicalization(a2_text, kp_selection["original_items"], kp_dir)
        print(f"[IRAN01-A2] Canonicalization status={kp_canon['status']}")
        kp_final = kp_canon.get("merged")

    support_concat = "\n\n".join(t for t in support_texts.values() if t)
    print("[IRAN01-A2] Support Ledger Deviation Check開始...")
    deviation_result = vfl01.run_deviation_check(client, ledger_text, support_concat)
    with open(f"{OUT_DIR}/support_ledger_deviation.json", "w", encoding="utf-8") as f:
        json.dump(deviation_result["parsed"], f, ensure_ascii=False, indent=2)
    print(f"[IRAN01-A2] deviation overall_status={deviation_result['parsed']['overall_status']} "
          f"deviations={len(deviation_result['parsed']['deviations'])}")

    print("[IRAN01-A2] Support Fact Check開始...")
    fc_prompt = r3.build_fact_check_prompt(TOPIC, support_concat, [])

    def make_fc_fn():
        return r3.make_fact_checker_fn(fc_prompt)

    fc_result, fc_status, fc_attempts, fc_model, fc_response_id, fc_search_usage, fc_sources = r3.run_fact_checker_with_gates(
        make_fc_fn, sleep_fn=time.sleep)
    verdict = fc_result.get("verdict") if fc_result else None
    print(f"[IRAN01-A2] Support fact_check status={fc_status} verdict={verdict}")
    with open(f"{OUT_DIR}/support_fact_qa.json", "w", encoding="utf-8") as f:
        json.dump({"final_status": fc_status, "result": fc_result}, f, ensure_ascii=False, indent=2)

    script_lines = [
        f"# A2 V2改1 — {parts['title']}", "",
        "## 1. Preview(日本語)", support_texts["preview"] or "(生成失敗)", "",
        "## 2. Key Phrases",
    ]
    if kp_final:
        for item in kp_final["items"]:
            script_lines.append(f"{item['rank']}. {item['used_form']} — {item['japanese_gloss']} — {item['used_form']}")
    else:
        script_lines.append("(Key Phrase選定未完了)")
    script_lines += [
        "", "## 3. Comment 1(日本語)", support_texts["comment_1"] or "(生成失敗)", "",
        "## 4. Full Story Part 1(英語、無変更)", parts["part1"], "",
        "## 5. Comment 2(日本語)", support_texts["comment_2"] or "(生成失敗)", "",
        "## 6. Full Story Part 2(英語、無変更)", parts["part2"], "",
        "## 7. Comment 3(日本語)", support_texts["comment_3"] or "(生成失敗)", "",
        "## 8. Point One(英語、無変更)", f"### {parts['point_one_heading']}", parts["point_one_body"], "",
        "## 9. Point Two(英語、無変更)", f"### {parts['point_two_heading']}", parts["point_two_body"], "",
        "## 10. Comment 4(日本語)", support_texts["comment_4"] or "(生成失敗)", "",
        "## 11. In One Line(英語、無変更)", parts["in_one_line"],
    ]
    with open(f"{OUT_DIR}/a2_supported_script.md", "w", encoding="utf-8") as f:
        f.write("\n".join(script_lines))

    summary = {
        "article_id": ARTICLE_ID, "a2_source_path": A2_ARTICLE_PATH,
        "comment_status": {k: v["status"] for k, v in comments.items()},
        "preview_status": preview_result["status"],
        "key_phrase_selection_status": kp_selection["status"],
        "key_phrase_canonicalization_status": (kp_final is not None),
        "support_ledger_status": deviation_result["parsed"]["overall_status"],
        "support_ledger_deviation_count": len(deviation_result["parsed"]["deviations"]),
        "support_fact_status": fc_status, "support_fact_verdict": verdict,
    }
    with open(f"{OUT_DIR}/run_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    print("[IRAN01-A2] 完了。summary:", json.dumps(summary, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
