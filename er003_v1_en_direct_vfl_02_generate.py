# ============================================================
# er003_v1_en_direct_vfl_02_generate.py
# ER-003-EN-DIRECT-VFL-02: Verified Fact Ledger方式 A01・ADD03 Cross-topic Stress Test
# ============================================================
# ER-003-EN-DIRECT-VFL-01でA02に対して確立したVerified Fact Ledger方式
# (Researcher→独立Verification→Verified Fact Ledger→Writer(Web検索なし)
# →独立Fact Checker→Ledger逸脱チェック)を、方式自体は変更せず、
# A01(スポーツ)・ADD03(経済ニュース)へ展開する。
#
# er003_v1_en_direct_vfl_01_generate.pyのschema・関数群を読み取り専用で
# 再利用し、Production(er002_ja_article_generation.py等)は一切変更しない。
# 記事ごとに完全に独立したResearch/Ledger/Writer/Fact Checkを実行する
# (A01とADD03を1回のwriter callへまとめない)。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_en_direct_vfl_02_generate.py

from __future__ import annotations

import json
import os
import time

from dotenv import load_dotenv

import er002_ja_web_research_r3 as r3
import er002_ja_free_markdown_restore_r2 as restore_r2
import er003_v1_en_direct_ab_01_generate as ab01
import er003_v1_en_direct_vfl_01_generate as vfl01

load_dotenv()

MASTER_PATH = vfl01.MASTER_PATH
MODEL = vfl01.MODEL
REASONING_EFFORT = vfl01.REASONING_EFFORT

# A02(既存Natural English Source 418語)と同じ考え方: 各記事の既存
# Natural English Source語数を基準にした±15% soft target(hard constraintではない)。
ARTICLES = {
    "A01": {
        "topic": "2026年ワールドカップ準決勝のイングランド対アルゼンチン",
        "a_version_word_count": 340,  # er003_output/p1b/A01/translation_metrics.json
        "focus_instructions": """【今回、特に構造化して含めるべきFact(この記事=スポーツ)】
1. 人物: 選手名・所属チーム・誰が得点したか・誰がassist/crossをしたかの関係を正確に区別する
2. 得点・試合経過: 得点順序、スコア、各得点の時間(何分)、added timeの扱い、最終的な勝敗
3. 時系列: 出来事の実際の順序(前後関係・因果)をFactとして保持する。Narrative上の並べ替えは後段のwriterの裁量に委ねるが、Fact Ledger自体には正しい時系列・得点順を記録すること
4. 統計値の確認: シュート数・ポゼッション等の試合統計は、公式のPost Match Statistics Report等、最も確定的な一次資料の数値を優先する。複数の情報源で数値に差がある場合は、断定せずambiguityフィールドへその旨を明記する
5. Factと演出の区別: 選手の感情、観客の反応、試合の具体的な雰囲気描写など、Sourceに明記されていない具体的場面はFactとして収集しない(演出はwriter段階でSourceにない範囲として許容されるが、Fact Ledgerには含めない)

このテーマ(サッカーの試合結果)と無関係な、他の記事・他のトピックのFactは一切収集しないでください。""",
    },
    "ADD03": {
        "topic": "ホルムズ海峡を通航する船舶への20％通航料をめぐる発言の撤回と市場反応",
        "a_version_word_count": 407,  # er003_output/p1b/ADD03/translation_metrics.json
        "focus_instructions": """【今回、特に構造化して含めるべきFact(この記事=経済ニュース)】
1. 日付: 7月13日と7月14日、それぞれの出来事を明確に区別し、実際の時系列順(7/13が先、7/14が後)をFactとして保持する。7/14の出来事を7/13の原因であるかのように記録しない
2. 数字: Brent原油価格、値動きの比率、金額等について、各Factでnumeric_value・numeric_scope・date_or_periodを明示し、どの日のどの時点の数字かを区別する(例: intraday高値なのか、その日の終値なのか)。特にintraday高値については、速報段階の一時的な報道水準と、確定した日中高値・終値を区別し、複数のSourceで数値に差がある場合は断定せずambiguityへ明記する
3. 因果: 価格変動について、Sourceが明示的に因果関係を述べているのか、市場関係者の見方(推測)なのか、単なる同時発生(相関)なのかをcausal_strengthで区別する。Source以上に因果関係を強めない
4. 時系列: 7/13→7/14の実際の順序を壊さないよう、各Factのdate_or_periodを正確に記録する。writerが物語として並べ替える場合でも、Ledger上の時系列関係自体は正しく保持すること

このテーマ(ホルムズ海峡・原油価格)と無関係な、他の記事・他のトピックのFactは一切収集しないでください。""",
    },
}


# vfl01.RESEARCHER_PROMPT_TEMPLATEは【今回、特に構造化して含めるべきFact】節に
# A02固有の内容(Overnight curfew/Autoplay/Pilot sample 309等)がハードコードされて
# おり、そのままtopicだけ差し替えて再利用すると、A01/ADD03のResearcherにも誤って
# A02の調査項目が指示されてしまう(初回実行で発覚したバグ。ADD03のFact Ledgerに
# 実際に無関係なUK SNS curfew関連Factが混入した)。この関数では、記事非依存の
# 部分(役割・Source優先順位・出力形式)だけをvfl01のテンプレートから切り出し、
# 【今回、特に構造化して含めるべきFact】をarticle固有のfocus_instructionsで
# 完全に置き換える。
_GENERIC_RESEARCHER_PROMPT_HEADER = """今回のテーマについて、Webで調査し、Verified Fact Ledgerの下書きを作成してください。

【今回のテーマ】
{topic}

【役割】
あなたはResearcherです。以下を行いません:
- 記事本文を書く
- Narrativeを作る
- 比喩を考える
- 阪神マスターのstyleを模倣する
あなたが行うのは、Factだけを収集・整理することです。

【Source優先順位】
1. 政府・規制当局等の一次資料
2. 公式調査・報告書
3. 信頼できる二次資料
一次Sourceで確認できるFactを、二次Sourceだけで確定しないでください。
"""

_GENERIC_RESEARCHER_PROMPT_FOOTER = """
【出力形式】
各Factについて、fact_id・claim・subject・date_or_period・scope・conditions・numeric_value・
numeric_scope・causal_strength・source_title・source_url・source_type・support_level・
ambiguity・notes_for_writerを埋めてください(該当しない項目はnullで構いません)。
数字・期間・対象範囲があるFactについては、該当項目を必ず明示してください。"""


def build_researcher_prompt(topic: str, focus_instructions: str) -> str:
    header = _GENERIC_RESEARCHER_PROMPT_HEADER.format(topic=topic)
    return header + "\n" + focus_instructions + "\n" + _GENERIC_RESEARCHER_PROMPT_FOOTER


def run_researcher(client, topic: str, focus_instructions: str) -> dict:
    prompt = build_researcher_prompt(topic, focus_instructions)
    response = client.responses.create(
        model=MODEL,
        reasoning={"effort": REASONING_EFFORT},
        tools=[{"type": "web_search"}],
        text={"format": {"type": "json_schema", **vfl01.FACT_LEDGER_JSON_SCHEMA}},
        input=[
            {"role": "developer", "content": vfl01.RESEARCHER_DEVELOPER_MESSAGE},
            {"role": "user", "content": prompt},
        ],
    )
    text = response.output_text
    search_usage = r3.extract_web_search_usage(response)
    sources = r3.extract_sources(response)
    parsed = json.loads(text)
    return {
        "prompt": prompt, "raw_text": text, "parsed": parsed, "model": response.model,
        "response_id": response.id, "search_usage": search_usage, "sources": sources,
    }


def run_one_article(client, master_full_text: str, topic_id: str, out_root: str):
    cfg = ARTICLES[topic_id]
    topic = cfg["topic"]
    a_word_count = cfg["a_version_word_count"]
    lower_bound = round(a_word_count * 0.85)
    upper_bound = round(a_word_count * 1.15)

    out_dir = f"{out_root}/{topic_id}"
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(f"{out_dir}/audit", exist_ok=True)

    # --- Step 1: Fact Ledger生成 ---
    print(f"[VFL2:{topic_id}] Step1: Researcher呼び出し開始...")
    researcher_result = run_researcher(client, topic, cfg["focus_instructions"])
    print(f"[VFL2:{topic_id}] Step1完了: facts={len(researcher_result['parsed']['facts'])} "
          f"web_search_calls={researcher_result['search_usage']['web_search_call_count']}")
    with open(f"{out_dir}/fact_ledger_draft.json", "w", encoding="utf-8") as f:
        json.dump(researcher_result["parsed"], f, ensure_ascii=False, indent=2)
    with open(f"{out_dir}/audit/researcher_full_record.json", "w", encoding="utf-8") as f:
        json.dump({k: v for k, v in researcher_result.items() if k != "parsed"}, f, ensure_ascii=False, indent=2, default=str)

    # --- Step 2: Verification ---
    print(f"[VFL2:{topic_id}] Step2: Verification呼び出し開始...")
    verification_result = vfl01.run_verification(client, researcher_result["parsed"])
    verdict_counts_raw = {}
    for v in verification_result["parsed"]["verifications"]:
        verdict_counts_raw[v["verdict"]] = verdict_counts_raw.get(v["verdict"], 0) + 1
    print(f"[VFL2:{topic_id}] Step2完了: {verdict_counts_raw} "
          f"web_search_calls={verification_result['search_usage']['web_search_call_count']}")
    with open(f"{out_dir}/fact_ledger_verification.json", "w", encoding="utf-8") as f:
        json.dump(verification_result["parsed"], f, ensure_ascii=False, indent=2)
    with open(f"{out_dir}/audit/verification_full_record.json", "w", encoding="utf-8") as f:
        json.dump({k: v for k, v in verification_result.items() if k != "parsed"}, f, ensure_ascii=False, indent=2, default=str)

    # build_verified_ledger_textはVFL-01の関数をそのまま再利用(記事非依存の汎用ロジック)
    verified_ledger_text, counts, kept_facts = vfl01.build_verified_ledger_text(
        researcher_result["parsed"], verification_result["parsed"])
    with open(f"{out_dir}/verified_fact_ledger.txt", "w", encoding="utf-8") as f:
        f.write(verified_ledger_text)
    with open(f"{out_dir}/verified_fact_ledger_structured.json", "w", encoding="utf-8") as f:
        json.dump({"counts": counts, "kept_facts": kept_facts}, f, ensure_ascii=False, indent=2)
    print(f"[VFL2:{topic_id}] Verified Ledger確定: {counts}")

    writer_prompt = vfl01.WRITER_PROMPT_TEMPLATE.format(
        hanshin_master_full_text=master_full_text, topic=topic,
        verified_ledger_text=verified_ledger_text,
        a_version_word_count=a_word_count, lower_bound=lower_bound, upper_bound=upper_bound,
    )
    with open(f"{out_dir}/audit/writer_prompt.txt", "w", encoding="utf-8") as f:
        f.write(writer_prompt)

    # --- Step 3: Writer(Web検索なし、初回1runのみ) ---
    print(f"[VFL2:{topic_id}] writer呼び出し開始...")
    writer_result = vfl01.run_writer_with_technical_retry(client, writer_prompt)
    with open(f"{out_dir}/audit/writer_attempts.json", "w", encoding="utf-8") as f:
        json.dump(writer_result["attempts"], f, ensure_ascii=False, indent=2, default=str)

    if writer_result["status"] != "STRUCTURE_PASS" or not writer_result.get("raw_text"):
        print(f"[VFL2:{topic_id}] writer失敗 status={writer_result['status']}")
        return {"topic_id": topic_id, "status": writer_result["status"]}

    raw_text = writer_result["raw_text"]
    with open(f"{out_dir}/article.md", "w", encoding="utf-8") as f:
        f.write(raw_text)

    structure = restore_r2.validate_point_structure(raw_text)
    word_count = ab01.compute_word_count(raw_text)
    diagnostics = {
        "topic_id": topic_id, "model": writer_result["model"], "response_id": writer_result["response_id"],
        "technical_attempts": len(writer_result["attempts"]), "structure_status": structure.status,
        "h3_count": structure.h3_count, "word_count": word_count,
        "length_lower_bound_words": lower_bound, "length_upper_bound_words": upper_bound,
        "length_status": "WITHIN_SOFT_TARGET" if lower_bound <= word_count <= upper_bound else "OUTSIDE_SOFT_TARGET",
    }
    with open(f"{out_dir}/diagnostics.json", "w", encoding="utf-8") as f:
        json.dump(diagnostics, f, ensure_ascii=False, indent=2)
    print(f"[VFL2:{topic_id}] word_count={word_count} structure={structure.status}")

    # --- 独立fact checker ---
    print(f"[VFL2:{topic_id}] fact checker呼び出し開始...")
    fc_prompt = r3.build_fact_check_prompt(topic, raw_text, [])

    def make_fc_fn():
        return r3.make_fact_checker_fn(fc_prompt)

    fc_result, fc_status, fc_attempts, fc_model, fc_response_id, fc_search_usage, fc_sources = r3.run_fact_checker_with_gates(
        make_fc_fn, sleep_fn=time.sleep)
    verdict = fc_result.get("verdict") if fc_result else None
    print(f"[VFL2:{topic_id}] fact_check status={fc_status} verdict={verdict}")
    fact_qa_record = {
        "topic_id": topic_id, "final_status": fc_status, "model": fc_model, "response_id": fc_response_id,
        "web_search_call_count": fc_search_usage["web_search_call_count"] if fc_search_usage else None,
        "attempts": len(fc_attempts), "result": fc_result,
    }
    with open(f"{out_dir}/fact_qa.json", "w", encoding="utf-8") as f:
        json.dump(fact_qa_record, f, ensure_ascii=False, indent=2)
    with open(f"{out_dir}/audit/fact_check_attempts.json", "w", encoding="utf-8") as f:
        json.dump(fc_attempts, f, ensure_ascii=False, indent=2, default=str)

    # --- Ledger逸脱チェック ---
    print(f"[VFL2:{topic_id}] ledger逸脱チェック開始...")
    deviation_result = vfl01.run_deviation_check(client, verified_ledger_text, raw_text)
    print(f"[VFL2:{topic_id}] deviation overall_status={deviation_result['parsed']['overall_status']} "
          f"deviations={len(deviation_result['parsed']['deviations'])}")
    with open(f"{out_dir}/ledger_deviation.json", "w", encoding="utf-8") as f:
        json.dump(deviation_result["parsed"], f, ensure_ascii=False, indent=2)
    with open(f"{out_dir}/audit/deviation_full_record.json", "w", encoding="utf-8") as f:
        json.dump({k: v for k, v in deviation_result.items() if k != "parsed"}, f, ensure_ascii=False, indent=2, default=str)

    return {
        "topic_id": topic_id, "status": "OK", "word_count": word_count,
        "fact_status": fc_status, "fact_verdict": verdict,
        "ledger_status": deviation_result["parsed"]["overall_status"],
        "ledger_deviation_count": len(deviation_result["parsed"]["deviations"]),
        "technical_attempts": len(writer_result["attempts"]),
    }


def main():
    out_root = "er003_output/en_direct_vfl_02"
    os.makedirs(out_root, exist_ok=True)
    client = vfl01.get_client()
    master_full_text = vfl01.load_master_full_text()

    summary = {}
    for topic_id in ("A01", "ADD03"):
        summary[topic_id] = run_one_article(client, master_full_text, topic_id, out_root)

    print("[VFL2] 完了。summary:")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    with open(f"{out_root}/run_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
