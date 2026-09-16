# ============================================================
# er014_output/user_test_news_2ep_01/space_weapons/run_pipeline.py
# 管理ID: USER-TEST-NEWS-2EP-COMPLETION-01 (Theme 1: Space Weapons)
#
# 目的: ユーザー実検証用に、既存の通常News正式生成経路(Reference:
# Hanshin ER-003-A2-B1-N3-01)をそのまま再利用してA2/B1完成episodeを
# 作る。新しいPrompt/Validator/Story構造/Model routingは一切変更しない。
#
# Research/Ledger構造は er014_output/four_type_observation_01/news/
# run_news_a2.py・run_news_b1b.py と同一のclient呼び出し構造
# (vfl01.build_researcher_prompt/build_verification_prompt +
# client.responses.create、web_search tool)を、topicだけ本タスクの
# Themeへ差し替えて再現する(コピー関数の新規発明ではなく、同型の
# 呼び出しをtopicパラメータ化しただけ)。
#
# 記事生成自体は Production関数 er003_v1_n3_01_articles_generate.
# run_one_pattern() をそのまま呼ぶ(editorial_type_module_block未指定
# =News既定、Focus Module/Point Role hintなし)。
#
# Scaffold/Key Phrase/TTS/Assemblyは er011_household_unified_final_
# candidate_01_run.py と同一のProduction関数呼び出し構造(無変更)。
#
# 出力先: er014_output/user_test_news_2ep_01/space_weapons/
#   research/ (Ledger、A2/B1共有)
#   a2/, b1b/ (記事・scaffold・key_phrases・narration・audit)
#   web/ (segments/a2, segments/b1b, episode_a2.mp3, episode_b1.mp3)
#
# 実行方法(root直下から):
#   .venv/Scripts/python.exe er014_output/user_test_news_2ep_01/space_weapons/run_pipeline.py [stage ...]
#   stage: ledger / a2 / b1b / cost (省略時 = all)
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

THEME_ID = "user_test_news_2ep_01_space_weapons"
BASE_DIR = "er014_output/user_test_news_2ep_01/space_weapons"
RESEARCH_DIR = f"{BASE_DIR}/research"
TOPIC_ID = "space_weapons_deployment_era"
BUDGET_JPY_CAP = 700.0

# ユーザー指示原文の区別要件を、既存build_researcher_promptのtopic引数
# として渡す(Promptテンプレート自体は無変更)。
TOPIC_EN = (
    "Current news topic: the emerging era of weapons and counterspace "
    "capabilities being deployed in or for use against space systems. "
    "In researching this, clearly distinguish between: (1) events, "
    "systems, or capabilities that have actually been announced, "
    "tested, launched, or confirmed by governments, militaries, "
    "space agencies, or credible reporting (Reuters, AP, official "
    "government/military statements, etc.); (2) terminology "
    "differences between space-based weapons (weapons placed in "
    "space), counterspace weapons (systems meant to disable or "
    "destroy satellites, including anti-satellite/ASAT weapons, "
    "jamming, cyberattacks, and directed-energy systems), and "
    "defensive or protective space systems; (3) what can legitimately "
    "be described as 'deploying weapons to space' versus existing, "
    "long-standing space security activities (such as surveillance "
    "or missile-warning satellites) that are not new; (4) facts that "
    "can be confirmed under existing treaties and international rules "
    "(such as the Outer Space Treaty and UN discussions on space "
    "arms control); and (5) forward-looking predictions or expert "
    "interpretation, clearly separated from confirmed current fact. "
    "Do not sensationalize. Do not use language such as 'a space war "
    "has begun' unless directly and explicitly supported by a source. "
    "Do not make political or security-policy judgments; focus the "
    "coverage on confirmed events and how they differ from prior "
    "space activity, using only facts confirmed by web search (no "
    "invented details, no facts supplied from the assistant's own "
    "prior knowledge)."
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
    article_id = f"USER_TEST_NEWS_2EP_SPACE_WEAPONS_{label}"
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
