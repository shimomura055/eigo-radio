# ============================================================
# er014_output/user_test_news_convenience_ai_01/convenience_ai/run_pipeline.py
# 管理ID: USER-TEST-NEWS-CONVENIENCE-AI-01
#
# 目的: er014_output/user_test_news_light_01/tiny_bags/run_pipeline.py
# (USER-TEST-NEWS-LIGHT-TOPIC-01)をそのまま複製し、TOPIC/THEME_ID/
# BASE_DIR/TOPIC_ID/BUDGET_JPY_CAP/TOPIC_ENのみ差し替えたもの。Prompt本文
# (build_researcher_prompt/build_verification_prompt/A2_KAI1_INSTRUCTION/
# B1_B_DIRECT_INSTRUCTION等)・関数構造・呼び出し順序は一切変更しない。
#
# 記事生成自体は Production関数 er003_v1_n3_01_articles_generate.
# run_one_pattern() をそのまま呼ぶ(通常News既定、Focus Module/Point
# Role hintなし)。Scaffold/Key Phrase/TTS/Assemblyも同一Production
# 関数呼び出し構造(無変更)。
#
# TOPIC_ENは、Researcher/Verificationのtopic引数と、Writer共通block
# (build_common_block)の{topic}引数の両方へ渡す既存の入力チャネル
# (Tiny Bags driverと同一の使い方)。ここへ委任文の編集方針(中心軸・
# 構成イメージ・数字最小限・前提知識不要・避けるべき語)を明記することで、
# Production Writer Prompt本体・共通moduleを変更せずに難易度・情報密度を
# 制御する(USER-TEST-NEWS-CONVENIENCE-AI-01委任文「編集判断の実装手段」)。
#
# 出力先: er014_output/user_test_news_convenience_ai_01/convenience_ai/
#   research/ (Ledger、A2/B1共有)
#   a2/, b1b/ (記事・scaffold・key_phrases・narration・audit)
#   a2/web/, b1b/web/ (segments・episode.mp3)
#
# 実行方法(root直下から):
#   .venv/Scripts/python.exe er014_output/user_test_news_convenience_ai_01/convenience_ai/run_pipeline.py [stage ...]
#   stage: ledger / a2 / b1b / cost (省略時 = all)
#   scaffold/keyphrase/japanese_title/tts/assembly/playerの各stageは
#   python -c 経由で個別関数を呼ぶ(tiny_bags/space_weapons版と同一運用)。
# ============================================================
from __future__ import annotations

import json
import os
import sys
import time

sys.path.insert(0, os.getcwd())

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

os.environ["TTS_EXECUTION_MODE"] = "STANDARD"  # PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-01

import er002_ja_web_research_r3 as r3
import er003_v1_en_direct_ab_01_generate as ab01
import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_articles_generate as prod_gen
import er003_v1_n3_01_assemble as asm
import er003_v1_n3_01_scaffold_generate as sc
import er003_v1_n3_01_tts_generate as tts_gen
import er005_cost_logger as cl

THEME_ID = "user_test_news_convenience_ai_01_convenience_ai"
BASE_DIR = "er014_output/user_test_news_convenience_ai_01/convenience_ai"
RESEARCH_DIR = f"{BASE_DIR}/research"
TOPIC_ID = "convenience_store_ai_product_development"
BUDGET_JPY_CAP = 600.0

# ユーザー指示原文(USER-TEST-NEWS-CONVENIENCE-AI-01)を、既存
# build_researcher_prompt/build_common_blockのtopic引数として渡す
# (Promptテンプレート自体は無変更)。Research対象を絞り、Writerへは
# 「前提知識不要・数字最小限・専門語を避ける」編集方針を明示する。
TOPIC_EN = (
    "Current news/lifestyle topic: Japanese convenience store chains have "
    "started using AI to help come up with new food product ideas. The "
    "entry point / hook example is Lawson using AI to suggest an unusual "
    "combination idea (for example, a lemon tart idea paired with "
    "pickles), which surprised people, and which human staff then "
    "actually tried, tasted, and adjusted before deciding whether and how "
    "to turn it into a real product. If a different but related use "
    "exists at another chain such as FamilyMart, where AI is used to "
    "look at past sales data to suggest what kind of product might sell "
    "well (a distinctly different use of AI than 'suggesting a weird "
    "combination'), report that too as a separate, clearly distinguished "
    "fact — do not blend the two uses together as if they were the same "
    "thing. Research ONLY what is needed to support these five points, "
    "and confirm concrete specifics (exact product name, launch timing/ "
    "region, and whether it was a trial sale or a more established / "
    "continuing product) wherever possible: "
    "(1) Japanese convenience stores have started using AI in food "
    "product development; "
    "(2) one real use of AI is to generate an unusual, surprising "
    "combination idea that a person might not think of on their own; "
    "(3) AI does not make the finished product by itself — a person "
    "still tastes, tests, and adjusts the idea before it becomes an "
    "actual product; "
    "(4) a different chain uses AI in a different way, to look at past "
    "sales data and suggest what might sell well; "
    "(5) AI is best understood here as an idea-generation or "
    "decision-support tool, not a replacement for the human "
    "product-development team. "
    "Prioritize official Lawson and FamilyMart sources (press releases, "
    "official announcements) and credible reporting (such as the Japan "
    "Times or other reputable outlets covering Japanese retail/consumer "
    "news), and primary or near-primary sources where possible. Do not "
    "include claims that cannot be traced to a credible source. Do not "
    "research or add general background on how generative AI / machine "
    "learning works, AI ethics, job-replacement debates, broader retail "
    "digital-transformation strategy, or market-size/competitive "
    "analysis beyond what is needed for point (4) above — this story is "
    "about a simple, concrete human-interest angle (AI suggests ideas, "
    "people decide), not an AI-technology explainer or a retail-industry "
    "analysis. "
    "\n\nWriting guidance for whoever writes the audio news script from "
    "this Ledger (this is a listening-only news story for English "
    "learners, so it must be understandable with no prior knowledge of "
    "AI, retail, or Japanese convenience store chains): Assume the "
    "listener knows nothing about AI beyond 'a computer program that can "
    "suggest ideas.' Do not explain how AI or machine learning works "
    "technically, and avoid technical or abstract vocabulary such as "
    "'product development process,' 'consumer behavior,' 'predictive "
    "analytics,' 'optimization,' 'generative model,' or 'market "
    "segmentation' — use everyday words instead (idea, try, taste, make, "
    "sell, store, product, unusual, popular, data about what people "
    "buy). Keep numbers to the minimum needed to understand the story "
    "(exact dates/figures are not the point of this story). Do not turn "
    "this into a debate about whether AI will replace jobs, an ethics "
    "discussion, or a retail-strategy analysis — stay concrete and "
    "human-focused: an AI suggests an idea, a person tries it and "
    "decides if it actually tastes good, and a different store uses AI "
    "in a different, simpler way (looking at what has sold well before). "
    "A natural shape for the story: open with the surprising combination "
    "example as a hook, then explain simply that stores are using AI to "
    "help think up new food ideas and that people still taste-test and "
    "adjust before anything is sold, then use the two Points to note (a) "
    "AI can suggest ideas a person might not think of, and (b) a "
    "different store uses AI to look at past sales data to guess what "
    "might sell — and close with a simple one-line takeaway in the "
    "spirit of: AI is helping with ideas, but people still decide what "
    "actually reaches the shelf. Avoid overgeneralizations such as "
    "claims that AI is now designing most convenience store products, "
    "and do not present a single Lawson example as proof of an "
    "industry-wide shift unless the Ledger actually supports that scope."
)

LEVELS = {
    "a2": {"label": "A2", "instruction": None, "stage_tag": "writer_a2", "gate_level": "A2"},
    "b1b": {"label": "B1B", "instruction": None, "stage_tag": "writer_b1", "gate_level": "B1"},
}


def save_json(path: str, data) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ============================================================
# 費用実測(household driverと同一ロジック、複製のみ・独自単価定義なし)
# ============================================================
USD_JPY = 160.0
_PRICING = json.load(open("er005_output/cost_baseline_01/pricing_snapshot.json", encoding="utf-8"))["prices"]


def _price(provider, model, meter, tier="Standard"):
    for p in _PRICING:
        if p["provider"] == provider and p["model"] == model and p["meter"] == meter and p.get("tier", "Standard") == tier:
            return p["price"]
    raise KeyError((provider, model, meter, tier))


def _call_cost_usd(r: dict) -> tuple:
    provider = r.get("provider")
    model = r.get("model_id") or r.get("model")
    it, ot = r.get("input_tokens") or 0, r.get("output_tokens") or 0
    ct = r.get("cached_input_tokens") or 0
    try:
        if provider == "openai":
            billable_in = max(it - ct, 0)
            cost = (billable_in / 1e6) * _price("openai", model, "input_tokens") \
                + (ct / 1e6) * _price("openai", model, "cached_input_tokens") \
                + (ot / 1e6) * _price("openai", model, "output_tokens")
            wsc = r.get("web_search_call_count") or 0
            cost += (wsc / 1000) * _price("openai", "N/A (tool, all models)", "web_search_call")
            return cost, False
        if provider == "gemini":
            return (it / 1e6) * _price("gemini", model, "input_tokens") \
                + (ot / 1e6) * _price("gemini", model, "output_tokens"), False
        if provider == "gemini_batch":
            return (it / 1e6) * _price("gemini", model, "input_tokens", tier="Batch") \
                + (ot / 1e6) * _price("gemini", model, "output_tokens", tier="Batch"), False
        if provider == "openai_asr":
            return (it / 1e6) * _price("openai_asr", model, "input_tokens") \
                + (ot / 1e6) * _price("openai_asr", model, "output_tokens"), False
        return 0.0, True
    except KeyError:
        return 0.0, True


def compute_cost_jpy_so_far() -> dict:
    log_path = f"{BASE_DIR}/raw_usage_log.jsonl"
    if not os.path.exists(log_path):
        return {"total_jpy": 0.0, "by_provider_jpy": {}, "unpriced_records": 0, "total_records": 0}
    total_usd, by_provider, unpriced = 0.0, {}, 0
    n = 0
    with open(log_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            cost, up = _call_cost_usd(rec)
            total_usd += cost
            by_provider[rec.get("provider")] = by_provider.get(rec.get("provider"), 0.0) + cost
            unpriced += int(up)
            n += 1
    return {
        "total_jpy": round(total_usd * USD_JPY, 2),
        "by_provider_jpy": {k: round(v * USD_JPY, 2) for k, v in by_provider.items()},
        "unpriced_records": unpriced, "total_records": n,
    }


def cost_stage() -> dict:
    result = compute_cost_jpy_so_far()
    save_json(f"{BASE_DIR}/cost_summary.json", result)
    print(f"[{THEME_ID}][cost] 実測合計={result['total_jpy']} JPY (上限{BUDGET_JPY_CAP}) "
          f"by_provider={result['by_provider_jpy']} unpriced_records={result['unpriced_records']}")
    if result["total_jpy"] > BUDGET_JPY_CAP:
        raise RuntimeError(f"費用上限超過(実測{result['total_jpy']}円 > 上限{BUDGET_JPY_CAP}円)。STOP。")
    return result


# ============================================================
# Research / Verification(run_news_a2.py L152-270と同一のclient呼び出し
# 構造、topicのみ本タスクのTOPIC_ENへ差し替え)
# ============================================================
def run_researcher_for_topic(client, topic: str) -> dict:
    prompt = vfl01.build_researcher_prompt(topic=topic)
    response = client.responses.create(
        model=vfl01.MODEL,
        reasoning={"effort": vfl01.REASONING_EFFORT},
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
    return {"prompt": prompt, "raw_text": text, "parsed": parsed, "model": response.model,
            "response_id": response.id, "search_usage": search_usage, "sources": sources}


def run_verification_for_topic(client, topic: str, ledger_parsed: dict) -> dict:
    prompt = vfl01.build_verification_prompt(topic, ledger_parsed)
    response = client.responses.create(
        model=vfl01.MODEL,
        reasoning={"effort": vfl01.REASONING_EFFORT},
        tools=[{"type": "web_search"}],
        text={"format": {"type": "json_schema", **vfl01.VERIFICATION_JSON_SCHEMA}},
        input=[
            {"role": "developer", "content": vfl01.VERIFICATION_DEVELOPER_MESSAGE},
            {"role": "user", "content": prompt},
        ],
    )
    text = response.output_text
    search_usage = r3.extract_web_search_usage(response)
    sources = r3.extract_sources(response)
    parsed = json.loads(text)
    return {"prompt": prompt, "raw_text": text, "parsed": parsed, "model": response.model,
            "response_id": response.id, "search_usage": search_usage, "sources": sources}


def build_ledger_stage() -> dict:
    os.makedirs(RESEARCH_DIR, exist_ok=True)
    structured_path = f"{RESEARCH_DIR}/verified_fact_ledger_structured.json"
    ledger_txt_path = f"{RESEARCH_DIR}/verified_fact_ledger.txt"
    if os.path.exists(structured_path) and os.path.exists(ledger_txt_path):
        structured = load_json(structured_path)
        verified_ledger_text = open(ledger_txt_path, encoding="utf-8").read()
        print(f"[{THEME_ID}] Resume: 既存research/成果物を再利用(API call再実行なし)。"
              f"counts={structured['counts']}")
        return {"verified_ledger_text": verified_ledger_text, "counts": structured["counts"]}

    client = vfl01.get_client()
    with cl.logging_context(THEME_ID, "researcher"):
        research_result = run_researcher_for_topic(client, TOPIC_EN)
    save_json(f"{RESEARCH_DIR}/fact_ledger_draft.json", research_result)
    print(f"[{THEME_ID}] Researcher完了: {len(research_result['parsed']['facts'])}件のFact下書き、"
          f"web_search={research_result['search_usage']}")

    with cl.logging_context(THEME_ID, "verification"):
        verification_result = run_verification_for_topic(client, TOPIC_EN, research_result["parsed"])
    save_json(f"{RESEARCH_DIR}/fact_ledger_verification.json", verification_result)

    ledger_parsed = research_result["parsed"]
    verdict_map = {v["fact_id"]: v for v in verification_result["parsed"]["verifications"]}
    lines, kept_facts = [], []
    counts = {"VERIFIED": 0, "AMBIGUOUS": 0, "REJECTED": 0}
    for fact in ledger_parsed["facts"]:
        v = verdict_map.get(fact["fact_id"])
        verdict = v["verdict"] if v else "AMBIGUOUS"
        counts[verdict] = counts.get(verdict, 0) + 1
        if verdict != "VERIFIED":
            continue
        kept_facts.append({**fact, "verification_verdict": verdict, "verification_notes": v["verification_notes"]})
        lines.append(f"[VERIFIED] {fact['fact_id']}: {fact['claim']}")
        if fact.get("scope"):
            lines.append(f"  scope: {fact['scope']}")
        if fact.get("conditions"):
            lines.append(f"  conditions: {fact['conditions']}")
        if fact.get("numeric_value"):
            lines.append(f"  numeric_value: {fact['numeric_value']} (numeric_scope: {fact.get('numeric_scope') or 'unspecified'})")
        if fact.get("date_or_period"):
            lines.append(f"  date_or_period: {fact['date_or_period']}")
        if fact.get("causal_strength") and fact["causal_strength"] != "NOT_APPLICABLE":
            lines.append(f"  causal_strength: {fact['causal_strength']}")
        if fact.get("notes_for_writer"):
            lines.append(f"  notes_for_writer: {fact['notes_for_writer']}")
        lines.append("")
    verified_ledger_text = "\n".join(lines)
    print(f"[{THEME_ID}] Verification完了: {counts}(CONFIRMED-onlyフィルタ適用後 kept={len(kept_facts)}件)")

    with open(ledger_txt_path, "w", encoding="utf-8") as f:
        f.write(verified_ledger_text)
    save_json(structured_path, {"topic": TOPIC_EN, "topic_id": TOPIC_ID, "kept_facts": kept_facts,
                                 "counts": counts, "note": "CONFIRMED(VERIFIED)のみ採用。"})
    # Directional Fact Precheck Layer 1(vfl_internal)向け、Production同型形式。
    save_json(f"{RESEARCH_DIR}/stage_b3_vfl.json", {"parsed": research_result["parsed"]})
    return {"verified_ledger_text": verified_ledger_text, "counts": counts}


# ============================================================
# Article生成(Production関数run_one_patternをそのまま呼ぶ)
# ============================================================
def generate_article_stage(level: str, verified_ledger_text: str) -> dict:
    instruction = prod_gen.A2_KAI1_INSTRUCTION if level == "a2" else prod_gen.B1_B_DIRECT_INSTRUCTION
    stage_tag = "writer_a2" if level == "a2" else "writer_b1"
    out_dir = f"{BASE_DIR}/{level}"
    client = vfl01.get_client()
    master_full_text = ab01.load_master_full_text()
    common_block = prod_gen.build_common_block(master_full_text, TOPIC_EN, verified_ledger_text)
    prompt = prod_gen.build_prompt(common_block, instruction)

    t0 = time.time()
    with cl.logging_context(THEME_ID, stage_tag):
        result = prod_gen.run_one_pattern(
            client, THEME_ID, level.upper(), prompt, verified_ledger_text, TOPIC_EN, out_dir)
    elapsed = round(time.time() - t0, 2)

    article_text = result.get("article_text")
    summary = {k: v for k, v in result.items() if k != "article_text"}
    summary["elapsed_seconds"] = elapsed
    summary["word_count"] = len((article_text or "").split())
    save_json(f"{out_dir}/run_summary.json", summary)
    print(f"[{THEME_ID}][{level}] article: status={result.get('status')} "
          f"fact_verdict={result.get('fact_verdict')} ledger_status={result.get('ledger_status')} "
          f"word_count={summary['word_count']} elapsed={elapsed}s")
    return summary


def scaffold_stage(level: str) -> dict:
    out_dir = f"{BASE_DIR}/{level}"
    with open(f"{out_dir}/article.md", encoding="utf-8") as f:
        article_text = f.read()
    parts = sc.split_article_text(article_text)
    save_json(f"{out_dir}/parts.json", parts)
    client = sc.get_client()
    run_fn = sc.run_a2_scaffold if level == "a2" else sc.run_b1_scaffold
    with cl.logging_context(THEME_ID, f"scaffold_{level}"):
        support = run_fn(client, parts, out_dir, article_text)
    status = {k: v.get("status") for k, v in support.items()}
    print(f"[{THEME_ID}][{level}] scaffold完了。status={status}")
    return {"support_status": status}


def keyphrase_stage(level: str) -> dict:
    label = "A2" if level == "a2" else "B1B"
    out_dir = f"{BASE_DIR}/{level}"
    kp_dir = f"{out_dir}/key_phrases"
    with open(f"{out_dir}/article.md", encoding="utf-8") as f:
        article_text = f.read()
    article_id = f"USER_TEST_NEWS_CONVENIENCE_AI_{label}"
    source_level = "B1-B(N3-01, direct generation)" if level == "b1b" else "A2(V2改1, N3-01)"
    process = "B1_SUPPORT" if level == "b1b" else "A2_SUPPORT"
    with cl.logging_context(THEME_ID, f"keyphrase_{level}"):
        kp = sc.run_key_phrases(article_text, kp_dir, article_id, source_level, process=process)
    sel_status = kp["selection"]["status"]
    canon_status = (kp.get("canonicalization") or {}).get("status")
    redundancy_status = (kp.get("redundancy_qa") or {}).get("status")
    summary = {"selection_status": sel_status, "canonicalization_status": canon_status,
               "redundancy_qa_status": redundancy_status}
    save_json(f"{out_dir}/audit/run_key_phrases_result_summary.json", summary)
    print(f"[{THEME_ID}][{level}] key phrase: selection={sel_status} canonicalization={canon_status} "
          f"redundancy={redundancy_status}")
    if kp.get("canonicalization") is None or canon_status not in (
            "CANONICALIZATION_PASS", "CANONICALIZATION_REVIEW_REQUIRED"):
        raise RuntimeError(f"[{level}] Key Phraseパイプライン失敗、STOP。selection={sel_status} "
                            f"canonicalization={canon_status}")
    if redundancy_status == "REDUNDANCY_NG":
        raise RuntimeError(f"[{level}] Key Phrase Redundancy QAがretry上限到達後もNG、STOP。")
    return summary


def japanese_title_stage(japanese_title: str) -> dict:
    tts_gen.JAPANESE_TITLES.update({THEME_ID: japanese_title})
    note = {"reused_title": japanese_title, "supplied_by": "driver script author (translation of Writer's EN title, "
                                                             "no new facts/claims added)"}
    save_json(f"{BASE_DIR}/audit/a2_japanese_title_note.json", note)
    print(f"[{THEME_ID}][a2] JAPANESE_TITLES登録: {japanese_title!r}")
    return note


def tts_stage(level: str) -> dict:
    theme = {"theme_id": THEME_ID, "out_dir": BASE_DIR}
    with cl.logging_context(THEME_ID, f"tts_{level}"):
        result = tts_gen.generate_a2_segments(theme) if level == "a2" else tts_gen.generate_b1_segments(theme)
    print(f"[{THEME_ID}][{level}] TTS完了。")
    return result


def assembly_stage(level: str) -> dict:
    theme = {"theme_id": THEME_ID, "out_dir": BASE_DIR}
    out_dir = f"{BASE_DIR}/{level}"
    assemble_fn = asm.stage_assemble_a2 if level == "a2" else asm.stage_assemble_b1
    with cl.logging_context(THEME_ID, f"assemble_{level}"):
        try:
            result = assemble_fn(theme)
            result["gate_off_result"] = "PASS"
        except RuntimeError as e:
            result = {"status": "GATE_BLOCKED", "gate_off_result": "BLOCKED", "error": str(e)}
    print(f"[{THEME_ID}][{level}] Assembly(Gate OFF経路)結果: {result.get('gate_off_result')}")

    gate_on = {"gate_on_result": "SKIPPED_ASSEMBLE_NOT_PASS"}
    if result.get("gate_off_result") == "PASS":
        gate_level = "A2" if level == "a2" else "B1"
        rs = asm.derive_a_family_required_structure(gate_level)
        try:
            asm.verify_episode_audio_validation_gate(out_dir, gate_level, required_structure=rs)
            gate_on = {"gate_on_result": "PASS"}
        except RuntimeError as e:
            gate_on = {"gate_on_result": "BLOCKED", "gate_on_message": str(e)[:1200]}
    print(f"[{THEME_ID}][{level}] Gate opt-in ON経路結果: {gate_on.get('gate_on_result')}")
    result["gate_opt_in_result"] = gate_on
    save_json(f"{out_dir}/audit/assembly_and_gate_summary.json", result)
    return result


# ============================================================
# player生成(regen_a2_topic_intro_title_fix_01.pyのrebuild_web_and_player()
# と同一のbuild_web_player_common呼び出し構造。segment名は narration/*.wav
# を動的列挙し、A2/B1どちらの構造にも固定segmentリストを複製しない)。
# ============================================================
def player_stage(level: str, title: str) -> str:
    sys.path.insert(0, "er014_output/user_test_news_2ep_01")
    import build_web_player_common as bwpc  # noqa: E402 (読み取り専用の既存共通module、無変更で呼ぶだけ)

    out_dir = f"{BASE_DIR}/{level}"
    narration_dir = f"{out_dir}/narration"
    assemble_result = load_json(f"{out_dir}/audit/assembly_and_gate_summary.json")
    seg_names = sorted(f[:-4] for f in os.listdir(narration_dir) if f.endswith(".wav"))
    web_delivery = bwpc.build_web_delivery(out_dir, out_dir, narration_dir, assemble_result["out_path"], seg_names)
    build_rows_fn = bwpc.build_a2_rows if level == "a2" else bwpc.build_b1b_rows
    rows, kp_table_html, parts = build_rows_fn(out_dir, "web/segments")
    label = "A2 (Beginner)" if level == "a2" else "B1 (Advanced)"
    note_html = f"USER-TEST(AI Product Development at Japanese Convenience Stores)。{THEME_ID}。"
    out_path = bwpc.render_player_page(
        f"{title} - {label}", note_html, web_delivery["episode_mp3"],
        assemble_result["duration_seconds"], assemble_result["peak"], assemble_result["clipping_detected"],
        rows, kp_table_html, f"{out_dir}/player.html")
    print(f"[{THEME_ID}][{level}] player.html生成: {out_path}")
    return out_path


def main() -> dict:
    stages = sys.argv[1:] or ["all"]
    os.makedirs(f"{BASE_DIR}/audit", exist_ok=True)
    cl.install(f"{BASE_DIR}/raw_usage_log.jsonl")

    result = {}
    if "ledger" in stages or stages == ["all"]:
        result["ledger"] = build_ledger_stage()
        cost_stage()
    for s in stages:
        if s in ("a2", "b1b"):
            verified = result.get("ledger") or build_ledger_stage()
            result[f"article_{s}"] = generate_article_stage(s, verified["verified_ledger_text"])
            cost_stage()
    if s := ("cost" if "cost" in stages else None):
        result["cost"] = cost_stage()
    save_json(f"{BASE_DIR}/e2e_run_summary_partial_{'_'.join(stages)}.json", result)
    return result


if __name__ == "__main__":
    main()
