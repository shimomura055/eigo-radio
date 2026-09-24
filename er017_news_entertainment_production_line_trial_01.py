# ============================================================
# er017_news_entertainment_production_line_trial_01.py
# NEWS-ENTERTAINMENT-PRODUCTION-LINE-TRIAL-01 Phase B
# ============================================================
# 目的: 既存NewsのProduction Research/Verification primitiveでVerified
# Fact Ledgerを正式に作成し、新しい英語Entertainment Writer Prompt+
# Production contractでOriginal(Stage0)->R1(Stage1)->R2(Stage2)を生成、
# R2を既存parser/Structure Validator/Ledger Deviation Checker/Fact
# Check block/Point Overlap QAへ通し、全PASSした場合のみ既存downstream
# (Key Phrase->TTS[Standard同期]->Assembly->Audio Validation Gate)へ
# 進める1記事Trialスクリプト。
#
# Production code(er003_*/er006_*/er010_*/er011_*/er012_*等)は一切
# 変更しない。既存Production関数をimportして読み取り専用のまま呼ぶのみ
# (sha256を実行前後で記録・比較する)。R3は生成しない(code pathも無い)。
#
# 実行方法(委任文の実行コマンド全文と一致させること):
#   .venv/Scripts/python.exe er017_news_entertainment_production_line_trial_01.py \
#       --out-dir er017_output/news_entertainment_production_line_trial_01 --step research
#   ... --step write --stages 0,1,2 --level b1
#   ... --step gates
#   ... --step downstream --only-if-gates-pass --budget-jpy 250
#   ... --step side-hook
# ============================================================
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import time

# PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-01: 正式リリース前はStandard同期を
# 使う。er003_v1_n3_01_tts_generateをimportする前に設定する必要がある
# (er011_news_stage3_new_theme_ledger_trial_09_b1b_full_pipeline.pyの
# 既存precedentと同一パターン)。
os.environ.setdefault("TTS_EXECUTION_MODE", "STANDARD")

THEME_ID = "entertainment_trial_meta_muse"
ARTICLE_ID = "ENT_TRIAL01_B1B"
SOURCE_LEVEL = "B1-B(N3-01, direct generation, Entertainment Trial)"

TOPIC_JA = (
    "AIに店への電話を頼んだら、裏では人間が話していた"
    "（MetaのAI電話代行機能「Muse」の人間コンシェルジュ実験、Reuters 2026年9月22日報道）"
)
THEME_EN = (
    "I asked an AI to call a store for me, and it turned out a human was "
    "secretly on the line (Meta's AI phone-calling feature, Muse, and its "
    "\"human concierge\" experiment, as reported by Reuters on September 22, 2026)."
)

ALLOWED_STAGES = (0, 1, 2)  # R3は生成しない(committed contract、テストで検証)
STAGE_FILES = {0: "stage0_original.md", 1: "stage1_r1.md", 2: "stage2_r2.md"}
STAGE_LABELS = {0: "original", 1: "r1", 2: "r2"}

PRODUCTION_FILES = [
    "er003_v1_n3_01_articles_generate.py",
    "er003_v1_en_direct_vfl_01_generate.py",
    "er002_ja_free_markdown_restore_r2.py",
    "er011_open146_ledger_canonical_en_spelling_production_01.py",
    "er012_b_family_production_runner_01.py",
    "er006_model_routing_contract_01.py",
    "er003_v1_n3_01_scaffold_generate.py",
    "er003_v1_n3_01_tts_generate.py",
    "er003_v1_n3_01_assemble.py",
]

# ============================================================
# 英語Entertainment Prompt(骨子。委任文のP7対応ブロックそのまま、
# 追加・削除なし)。既存News Editorial instruction
# (B1_B_DIRECT_INSTRUCTION/COMMON_BLOCK_TEMPLATE)は混ぜない。
# ============================================================
ENTERTAINMENT_PROMPT_LINES = [
    "Turn the news below into a piece you might share with a friend, the way "
    "you'd say \"Hey, isn't this kind of interesting?\"",
    "From the news, pick not the most surprising fact but the single most "
    "interesting way of looking at it, and build the piece around that. Use "
    "mainly the facts needed for that viewpoint; do not try to cover the "
    "whole story.",
    "Keep the tone natural and light. Do not write like a newspaper, a "
    "government document, or a school textbook.",
    "Write so that a learner of English can understand it by listening to "
    "it once.",
    "If the news might look like something specific to a distant place "
    "only, show its connection to the reader's own life or to a larger "
    "social change, just once. But you don't need to force the story to "
    "feel bigger than it is.",
    "Stick strictly to the facts. Do not add fictional events or quotes.",
    f"Theme: {THEME_EN}",
]

# Production contract(追加部分。Phase A recon(REPORT §A「前提」節)で
# 確定したheading表記・Length Targetと一致させる)。
CONTRACT_LINES = [
    "Write in English.",
    "Length: about 280–420 words in total.",
    "Format (Markdown): start with \"# \" followed by the title; then the "
    "main story; then exactly two \"### \" subsections, each 30–60 "
    "words, with headings that describe their content in your own words "
    "(do not use labels like \"Point One\"); then a final section headed "
    "exactly \"## In one line\" containing one sentence.",
]

DEVELOPER_MESSAGE = "You are a writer who explains the news clearly and makes it enjoyable to read."

STAGE0_USER_TEMPLATE = (
    "\n\n".join(ENTERTAINMENT_PROMPT_LINES) + "\n\n" + "\n".join(CONTRACT_LINES)
    + "\n\n[News — Verified Fact Ledger]\n{ledger_text}"
)

REVISION_CONTRACT_LINE = (
    "Keep the same Markdown structure (the \"# \" title, the main story, "
    "exactly two \"### \" subsections, and the \"## In one line\" section); "
    "do not add or remove sections. Write in English."
)
R1_INSTRUCTION_JA = "この記事を、事実関係は変えずに、もっとエンターテインメント性の高い記事に修正してください。"
R2_INSTRUCTION_JA = "この記事を、事実関係は変えずに、さらにもっとエンターテインメント性の高い記事に修正してください。"
STAGE1_USER = R1_INSTRUCTION_JA + "\n\n" + REVISION_CONTRACT_LINE
STAGE2_USER = R2_INSTRUCTION_JA + "\n\n" + REVISION_CONTRACT_LINE
STAGE_USER_TEXT = {1: STAGE1_USER, 2: STAGE2_USER}

PROMPT_ECHO_PATTERNS = [
    r"isn't this kind of interesting",
    r"isn't it interesting",
    r"here's something interesting",
    r"kind of interesting",
    r"これ、ちょっと面白くない",
]

# ============================================================
# Side Hook(er016_news_r2_to_hook_trial_01.pyのPrompt逐語、そのまま流用)
# ============================================================
HOOK_DEVELOPER = "あなたはHook Writerです。"
HOOK_USER_TEMPLATE = """以下は、音声番組で読み上げる予定の完成記事です。この記事をまだ聞いていない人が、聞いた瞬間に「ちょっと知りたい」と思う短いHookを1つ作ってください。

記事タイトルの言い換えや要約ではなく、記事の中にすでにある一番面白い見方や、具体的な場面を使ってください。友人に話しかけるような短い一文の問いにし、目安は30字前後。「〜でしょうか」は使わず、「〜？」で終えてください。記事にない事実は加えず、誇張はしないでください。

【テーマ】
{topic}

【記事】
{article_full_text}

hook_ja(Hook 1文)と、used_angle_ja(記事のどの見方・場面を使ったか、1文)を返してください。"""

HOOK_SCHEMA = {
    "name": "r2_hook",
    "schema": {
        "type": "object",
        "properties": {
            "hook_ja": {"type": "string"},
            "used_angle_ja": {"type": "string"},
        },
        "required": ["hook_ja", "used_angle_ja"],
        "additionalProperties": False,
    },
    "strict": True,
}
HOOK_MODEL = "gpt-5.6-luna"
HOOK_EFFORT = "medium"


# ============================================================
# 共通ユーティリティ
# ============================================================
def save_json(path: str, data) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_text(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def load_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def sha256_file(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def record_sha256_snapshot(out_dir: str, tag: str) -> dict:
    path = f"{out_dir}/production_code_sha256.json"
    data = load_json(path) if os.path.exists(path) else {}
    snapshot = {f: sha256_file(f) for f in PRODUCTION_FILES}
    data[tag] = snapshot
    save_json(path, data)
    return snapshot


_PRICING_CACHE = None


def load_pricing() -> dict:
    global _PRICING_CACHE
    if _PRICING_CACHE is None:
        with open("er005_output/cost_baseline_01/pricing_snapshot.json", encoding="utf-8") as f:
            _PRICING_CACHE = json.load(f)
    return _PRICING_CACHE


def price(provider: str, model: str, meter: str) -> float:
    data = load_pricing()
    for row in data["prices"]:
        if row["provider"] == provider and row["model"] == model and row["meter"] == meter:
            return row["price"]
    raise KeyError(f"pricing not found: {provider}/{model}/{meter}")


USD_TO_JPY = 160.0


def compute_call_cost_usd(usage: dict, model: str = "gpt-5.6-luna", web_search_calls: int = 0) -> float:
    in_tok = usage.get("input_tokens") or 0
    out_tok = usage.get("output_tokens") or 0
    cached_tok = usage.get("cached_input_tokens") or 0
    non_cached_in = max(in_tok - cached_tok, 0)
    usd = (non_cached_in * price("openai", model, "input_tokens") / 1e6
           + cached_tok * price("openai", model, "cached_input_tokens") / 1e6
           + out_tok * price("openai", model, "output_tokens") / 1e6)
    if web_search_calls:
        usd += web_search_calls * (price("openai", "N/A (tool, all models)", "web_search_call") / 1000.0)
    return usd


def usage_to_dict(usage) -> dict:
    if usage is None:
        return {}
    d = {
        "input_tokens": getattr(usage, "input_tokens", None),
        "output_tokens": getattr(usage, "output_tokens", None),
        "total_tokens": getattr(usage, "total_tokens", None),
    }
    in_details = getattr(usage, "input_tokens_details", None)
    if in_details is not None:
        d["cached_input_tokens"] = getattr(in_details, "cached_tokens", None)
    out_details = getattr(usage, "output_tokens_details", None)
    if out_details is not None:
        d["reasoning_tokens"] = getattr(out_details, "reasoning_tokens", None)
    return d


def append_cost_entry(out_dir: str, entry: dict) -> None:
    path = f"{out_dir}/cost.json"
    data = load_json(path) if os.path.exists(path) else {"theme": THEME_ID, "per_call": []}
    data["per_call"].append(entry)
    data["total_usd"] = round(sum(e.get("usd", 0.0) for e in data["per_call"]), 6)
    data["total_jpy"] = round(data["total_usd"] * USD_TO_JPY, 2)
    data["usd_to_jpy"] = USD_TO_JPY
    save_json(path, data)


def current_total_jpy(out_dir: str) -> float:
    """budget判定の権威ある合計は、cl.install()が全stage共通で書き込む
    raw_usage_log.jsonlをrunner.compute_cost_jpy_so_far()(既存Production
    関数、無変更)で読んだ値とする(全stageで同一logファイルへ記録する
    ため、research/write/gates/downstream/side-hookの累計が一意に合算
    される)。cost.json(per_call詳細付き、report用)は補助記録。"""
    import er012_b_family_production_runner_01 as runner

    cost_log_path = f"{out_dir}/raw_usage_log.jsonl"
    if os.path.exists(cost_log_path):
        jpy, _ = runner.compute_cost_jpy_so_far(cost_log_path)
        return jpy
    path = f"{out_dir}/cost.json"
    if not os.path.exists(path):
        return 0.0
    return load_json(path).get("total_jpy", 0.0)


def get_client():
    from dotenv import load_dotenv
    from openai import OpenAI

    load_dotenv()
    return OpenAI()


def word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z']+", text))


def extract_title(text: str) -> str:
    m = re.match(r"^#\s+(.+?)\s*\n", text)
    return m.group(1).strip() if m else ""


def check_prompt_echo(text: str) -> dict:
    hits = []
    for pat in PROMPT_ECHO_PATTERNS:
        if re.search(pat, text, flags=re.IGNORECASE):
            hits.append(pat)
    return {"echo_detected": bool(hits), "matched_patterns": hits}


# ============================================================
# Step 1: Research / Verification(既存Production primitive、topic差替え。
# vfl01.run_researcher()/run_verification()自体はモジュール定数TOPIC
# [Hanshin固定]を暗黙に使うため直接は呼べない(実測で確認済みの制約、
# er011_news_stage3_new_theme_ledger_trial_09.pyの既存precedentと同一)。
# build_researcher_prompt(topic=)/build_verification_prompt(topic, ...)
# というtopic引数を明示的に渡せる既存関数を使い、vfl01.run_researcher()/
# run_verification()と全く同じ呼び出し構造(model/reasoning/tools/
# text.format/developer+user message)を、topicだけ差し替えて再現する。
# ============================================================
def run_researcher_for_topic(client, topic: str):
    import er003_v1_en_direct_vfl_01_generate as vfl01

    prompt = vfl01.build_researcher_prompt(topic=topic)
    t0 = time.time()
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
    latency = time.time() - t0
    import er002_ja_web_research_r3 as r3

    search_usage = r3.extract_web_search_usage(response)
    sources = r3.extract_sources(response)
    parsed = json.loads(response.output_text)
    return {
        "prompt": prompt, "raw_text": response.output_text, "parsed": parsed,
        "model": response.model, "response_id": response.id,
        "search_usage": search_usage, "sources": sources, "latency_seconds": latency,
        "usage": usage_to_dict(getattr(response, "usage", None)),
    }


def run_verification_for_topic(client, topic: str, ledger_parsed: dict):
    import er003_v1_en_direct_vfl_01_generate as vfl01

    prompt = vfl01.build_verification_prompt(topic, ledger_parsed)
    t0 = time.time()
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
    latency = time.time() - t0
    import er002_ja_web_research_r3 as r3

    search_usage = r3.extract_web_search_usage(response)
    sources = r3.extract_sources(response)
    parsed = json.loads(response.output_text)
    return {
        "prompt": prompt, "raw_text": response.output_text, "parsed": parsed,
        "model": response.model, "response_id": response.id,
        "search_usage": search_usage, "sources": sources, "latency_seconds": latency,
        "usage": usage_to_dict(getattr(response, "usage", None)),
    }


def step_research(out_dir: str) -> None:
    import er003_v1_en_direct_vfl_01_generate as vfl01

    import er005_cost_logger as cl

    record_sha256_snapshot(out_dir, "pre_research")
    client = vfl01.get_client()
    ledger_dir = f"{out_dir}/ledger"
    os.makedirs(f"{ledger_dir}/audit", exist_ok=True)
    cl.install(f"{out_dir}/raw_usage_log.jsonl")

    print(f"[ENT-TRIAL][research] Researcher呼び出し開始(topic={TOPIC_JA})...")
    with cl.logging_context(THEME_ID, "research_researcher"):
        research = run_researcher_for_topic(client, TOPIC_JA)
    print(f"[ENT-TRIAL][research] facts={len(research['parsed']['facts'])} "
          f"web_search_calls={research['search_usage']['web_search_call_count']} "
          f"model={research['model']}")
    save_json(f"{ledger_dir}/fact_ledger_draft.json", research["parsed"])
    save_json(f"{ledger_dir}/audit/researcher_full_record.json",
              {k: v for k, v in research.items() if k != "parsed"})
    research_cost = compute_call_cost_usd(
        research["usage"], model=research["model"],
        web_search_calls=research["search_usage"]["web_search_call_count"])
    append_cost_entry(out_dir, {
        "stage": "research_researcher", "model": research["model"],
        "response_id": research["response_id"], "usage": research["usage"],
        "web_search_call_count": research["search_usage"]["web_search_call_count"],
        "latency_seconds": research["latency_seconds"], "usd": research_cost,
    })

    print("[ENT-TRIAL][research] Verification呼び出し開始...")
    with cl.logging_context(THEME_ID, "research_verification"):
        verification = run_verification_for_topic(client, TOPIC_JA, research["parsed"])
    print(f"[ENT-TRIAL][research] verification web_search_calls="
          f"{verification['search_usage']['web_search_call_count']} model={verification['model']}")
    save_json(f"{ledger_dir}/fact_ledger_verification.json", verification["parsed"])
    save_json(f"{ledger_dir}/audit/verification_full_record.json",
              {k: v for k, v in verification.items() if k != "parsed"})
    verification_cost = compute_call_cost_usd(
        verification["usage"], model=verification["model"],
        web_search_calls=verification["search_usage"]["web_search_call_count"])
    append_cost_entry(out_dir, {
        "stage": "research_verification", "model": verification["model"],
        "response_id": verification["response_id"], "usage": verification["usage"],
        "web_search_call_count": verification["search_usage"]["web_search_call_count"],
        "latency_seconds": verification["latency_seconds"], "usd": verification_cost,
    })

    ledger_text, verdict_counts, kept_facts = vfl01.build_verified_ledger_text(
        research["parsed"], verification["parsed"])
    save_text(f"{ledger_dir}/verified_fact_ledger.txt", ledger_text)
    save_json(f"{ledger_dir}/verdict_counts.json", verdict_counts)
    print(f"[ENT-TRIAL][research] Ledger確定。verdict_counts={verdict_counts} "
          f"kept_facts={len(kept_facts)}")
    print(f"[ENT-TRIAL][research] 累計費用: ¥{current_total_jpy(out_dir):.2f}")
    record_sha256_snapshot(out_dir, "post_research")


# ============================================================
# Step 2-4: Writer(previous_response_idで連鎖、Web検索なし、
# 既存News Editorial instructionは混ぜない)
# ============================================================
def call_fresh(client, developer: str, user: str, effort: str, model: str):
    t0 = time.time()
    response = client.responses.create(
        model=model, reasoning={"effort": effort},
        input=[{"role": "developer", "content": developer}, {"role": "user", "content": user}],
    )
    return response, time.time() - t0


def call_with_previous(client, user: str, effort: str, model: str, previous_response_id: str):
    t0 = time.time()
    response = client.responses.create(
        model=model, reasoning={"effort": effort}, previous_response_id=previous_response_id,
        input=[{"role": "user", "content": user}],
    )
    return response, time.time() - t0


def step_write(out_dir: str, stages: list) -> None:
    import er003_v1_en_direct_vfl_01_generate as vfl01
    import er005_cost_logger as cl

    for s in stages:
        if s not in ALLOWED_STAGES:
            raise ValueError(f"許可されていないstageです: {s}(R3は生成しない、許可={ALLOWED_STAGES})")

    record_sha256_snapshot(out_dir, "pre_write")
    ledger_text = load_text(f"{out_dir}/ledger/verified_fact_ledger.txt")
    client = get_client()
    model = vfl01.MODEL
    effort = vfl01.REASONING_EFFORT
    cl.install(f"{out_dir}/raw_usage_log.jsonl")

    titles = load_json(f"{out_dir}/titles.json") if os.path.exists(f"{out_dir}/titles.json") else {}

    prev_response_id = None
    for s in sorted(stages):
        if s == 0:
            user = STAGE0_USER_TEMPLATE.format(ledger_text=ledger_text)
            print(f"[ENT-TRIAL][write] Stage0(Original)呼び出し開始(model={model}, effort={effort})...")
            with cl.logging_context(THEME_ID, f"write_stage{s}_{STAGE_LABELS[s]}"):
                response, latency = call_fresh(client, DEVELOPER_MESSAGE, user, effort, model)
        else:
            if prev_response_id is None:
                prev_meta = load_json(f"{out_dir}/api_meta_stage{s - 1}.json")
                prev_response_id = prev_meta["response_id"]
            user = STAGE_USER_TEXT[s]
            print(f"[ENT-TRIAL][write] Stage{s}({STAGE_LABELS[s]})呼び出し開始(previous_response_id連鎖)...")
            with cl.logging_context(THEME_ID, f"write_stage{s}_{STAGE_LABELS[s]}"):
                response, latency = call_with_previous(client, user, effort, model, prev_response_id)

        text = response.output_text
        if not text or not text.strip():
            raise RuntimeError(f"Stage{s}: writer応答が空です(技術的失敗、新しいretry仕様は追加しない)")
        save_text(f"{out_dir}/{STAGE_FILES[s]}", text)

        usage = usage_to_dict(getattr(response, "usage", None))
        cost_usd = compute_call_cost_usd(usage, model=response.model)
        api_meta = {
            "stage": s, "label": STAGE_LABELS[s], "model": response.model,
            "response_id": response.id,
            "previous_response_id": (prev_response_id if s != 0 else None),
            "usage": usage, "latency_seconds": latency, "usd": cost_usd,
        }
        save_json(f"{out_dir}/api_meta_stage{s}.json", api_meta)
        append_cost_entry(out_dir, {
            "stage": f"write_stage{s}_{STAGE_LABELS[s]}", "model": response.model,
            "response_id": response.id, "usage": usage, "latency_seconds": latency, "usd": cost_usd,
        })

        titles[str(s)] = extract_title(text)
        save_json(f"{out_dir}/titles.json", titles)

        metrics = {
            "total_word_count": word_count(re.sub(r"^#{1,3}.*$", "", text, flags=re.MULTILINE)),
        }
        import er003_v1_n3_01_articles_generate as gen

        sections = gen.split_common_sections_for_point_qa(text)
        if sections is not None:
            metrics["point_one_word_count"] = word_count(sections["point_one_body"])
            metrics["point_two_word_count"] = word_count(sections["point_two_body"])
        metrics["total_within_soft_range"] = (
            gen.TOTAL_SOFT_LOWER <= metrics["total_word_count"] <= gen.TOTAL_SOFT_UPPER)
        save_json(f"{out_dir}/metrics_stage{s}.json", metrics)

        save_json(f"{out_dir}/prompt_echo_stage{s}.json", check_prompt_echo(text))

        prev_response_id = response.id
        print(f"[ENT-TRIAL][write] Stage{s} 完了。model={response.model} "
              f"title=\"{titles[str(s)]}\" word_count={metrics['total_word_count']} "
              f"累計費用=¥{current_total_jpy(out_dir):.2f}")

    record_sha256_snapshot(out_dir, "post_write")


# ============================================================
# Step 5: 既存Gate(検査のみ、再生成なし)
# ============================================================
def run_gate_for_stage(client, out_dir: str, stage: int, ledger_text: str) -> dict:
    import er002_ja_free_markdown_restore_r2 as restore_r2
    import er003_v1_en_direct_vfl_01_generate as vfl01
    import er003_v1_n3_01_articles_generate as gen
    import er011_open146_ledger_canonical_en_spelling_production_01 as canon_spelling

    text = load_text(f"{out_dir}/{STAGE_FILES[stage]}")

    sections = gen.split_common_sections_for_point_qa(text)
    parser_status = "PARSE_OK" if sections is not None else "PARSE_FAIL_STRUCTURE_NOT_2_H3"

    structure = restore_r2.validate_point_structure(text)

    print(f"[ENT-TRIAL][gates] Stage{stage}: Ledger Deviation Checker呼び出し開始...")
    # 正確なusage/costはraw_usage_log.jsonl(cl.install経由、呼び出し元で
    # logging_contextを張っている)側で自動計上されるため、ここでは
    # response_id/modelの記録のみ行う(二重計上しない)。
    deviation = vfl01.run_deviation_check(client, ledger_text, text)

    fact_check_block = canon_spelling.build_canonical_spelling_fact_check_block(ledger_text)

    gate_out_dir = f"{out_dir}/gates/stage{stage}"
    os.makedirs(gate_out_dir, exist_ok=True)
    if sections is not None:
        print(f"[ENT-TRIAL][gates] Stage{stage}: Point Overlap QA(検査のみ、"
              f"POINT_ONLY_REGENERATION_ENABLED={gen.POINT_ONLY_REGENERATION_ENABLED})...")
        point_overlap = gen.run_point_overlap_qa_and_regenerate(
            client, text, ledger_text, model=vfl01.MODEL,
            reasoning_effort=vfl01.REASONING_EFFORT, out_dir=gate_out_dir)
        point_overlap_note = ("検査のみで実行(POINT_ONLY_REGENERATION_ENABLED=False、"
                               "Productionの既定値のまま、再生成は発生しない)")
    else:
        point_overlap = {"status": "SKIPPED", "reason": "parser失敗のためQAをスキップ"}
        point_overlap_note = "未実行(parser失敗)"

    deviation_major = [d for d in deviation["parsed"]["deviations"] if d["severity"] == "MAJOR"]
    deviation_minor = [d for d in deviation["parsed"]["deviations"] if d["severity"] == "MINOR"]
    stage_pass = (
        parser_status == "PARSE_OK"
        and structure.status == "STRUCTURE_PASS"
        and deviation["parsed"]["overall_status"] == "LEDGER_COMPLIANT"
    )

    result = {
        "stage": stage,
        "parser_status": parser_status,
        "structure": {
            "status": structure.status, "h3_count": structure.h3_count,
            "headings": structure.headings, "reasons": structure.reasons,
        },
        "deviation": {
            "overall_status": deviation["parsed"]["overall_status"],
            "major_count": len(deviation_major), "minor_count": len(deviation_minor),
            "major_items": deviation_major, "minor_items": deviation_minor,
            "model": deviation["model"], "response_id": deviation["response_id"],
        },
        "fact_check_block": {
            "canonical_spelling_block_present": bool(fact_check_block.strip()),
            "canonical_spelling_block_text": fact_check_block,
            "note": "Ledgerにcanonical_en_spelling行が無いため空文字が正常(local検査、API呼び出しなし)",
        },
        "point_overlap_qa": {"status": point_overlap.get("status"), "note": point_overlap_note,
                              "report": point_overlap.get("report")},
        "stage_pass": stage_pass,
    }
    save_json(f"{out_dir}/gate_stage{stage}.json", result)
    print(f"[ENT-TRIAL][gates] Stage{stage}: parser={parser_status} structure={structure.status} "
          f"deviation={deviation['parsed']['overall_status']}(MAJOR={len(deviation_major)}) "
          f"stage_pass={stage_pass}")
    return result


def step_gates(out_dir: str) -> None:
    import er003_v1_en_direct_vfl_01_generate as vfl01
    import er005_cost_logger as cl

    record_sha256_snapshot(out_dir, "pre_gates")
    ledger_text = load_text(f"{out_dir}/ledger/verified_fact_ledger.txt")
    client = vfl01.get_client()
    cl.install(f"{out_dir}/raw_usage_log.jsonl")

    results = {}
    for stage in ALLOWED_STAGES:
        if not os.path.exists(f"{out_dir}/{STAGE_FILES[stage]}"):
            print(f"[ENT-TRIAL][gates] Stage{stage}: 記事ファイルが無いためスキップ")
            continue
        with cl.logging_context(THEME_ID, f"gate_stage{stage}"):
            results[stage] = run_gate_for_stage(client, out_dir, stage, ledger_text)

    save_json(f"{out_dir}/gates_summary.json",
              {str(k): v["stage_pass"] for k, v in results.items()})
    record_sha256_snapshot(out_dir, "post_gates")

    if 2 in results and not results[2]["stage_pass"]:
        print("[ENT-TRIAL][gates] STOP: Stage2(final)がGate FAILです。downstreamへは進みません。")


# ============================================================
# Step 6: downstream(Stage2全PASS時のみ、既存関数そのまま)
# ============================================================
def step_downstream(out_dir: str, only_if_gates_pass: bool, budget_jpy: float) -> None:
    import er012_b_family_production_runner_01 as runner

    record_sha256_snapshot(out_dir, "pre_downstream")
    downstream_log = {"theme_id": THEME_ID, "steps": []}

    gate2_path = f"{out_dir}/gate_stage2.json"
    if only_if_gates_pass:
        if not os.path.exists(gate2_path):
            downstream_log["status"] = "SKIPPED_NO_GATE_RESULT"
            save_json(f"{out_dir}/downstream_log.json", downstream_log)
            print("[ENT-TRIAL][downstream] STOP: gate_stage2.jsonが無いため実行しません。")
            return
        gate2 = load_json(gate2_path)
        if not gate2.get("stage_pass"):
            downstream_log["status"] = "SKIPPED_GATE_FAIL"
            downstream_log["gate_stage2"] = gate2
            save_json(f"{out_dir}/downstream_log.json", downstream_log)
            print("[ENT-TRIAL][downstream] STOP: Stage2 GateがFAILのためdownstreamへ進みません。")
            return

    cost_log_path = f"{out_dir}/raw_usage_log.jsonl"
    jpy, by_provider = runner.compute_cost_jpy_so_far(cost_log_path)
    if jpy >= budget_jpy:
        downstream_log["status"] = "SKIPPED_BUDGET_EXCEEDED_BEFORE_START"
        downstream_log["jpy_so_far"] = jpy
        save_json(f"{out_dir}/downstream_log.json", downstream_log)
        print(f"[ENT-TRIAL][downstream] STOP: 累計費用¥{jpy:.2f}が上限¥{budget_jpy}に到達済み。")
        return

    level_dir = f"{out_dir}/b1b"
    os.makedirs(f"{level_dir}/audit", exist_ok=True)
    src_path = f"{out_dir}/stage2_r2.md"
    dst_path = f"{level_dir}/article.md"
    # shutil.copyfile(バイト単位のコピー、テキストmodeの改行変換を経由
    # しない)を使う(er011_news_stage3_new_theme_ledger_trial_09_b1b_full_
    # pipeline.pyの既存precedentと同一パターン)。
    shutil.copyfile(src_path, dst_path)
    assert sha256_file(src_path) == sha256_file(dst_path), "article.mdコピー時に内容が変化しました"
    src_text = load_text(dst_path)
    downstream_log["steps"].append({"step": "copy_article", "status": "OK"})

    import er003_v1_n3_01_scaffold_generate as sc

    try:
        parts = sc.split_article_text(src_text)
    except RuntimeError as e:
        downstream_log["status"] = "STOPPED_STRUCTURE_INCOMPATIBLE"
        downstream_log["steps"].append({"step": "split_article_text", "status": "FAIL", "error": str(e)})
        save_json(f"{out_dir}/downstream_log.json", downstream_log)
        print(f"[ENT-TRIAL][downstream] STOP: sc.split_article_text失敗: {e}")
        return
    save_json(f"{level_dir}/parts.json", parts)
    downstream_log["steps"].append({"step": "split_article_text", "status": "OK"})

    import er005_cost_logger as cl

    cl.install(cost_log_path)
    client = sc.get_client()

    print("[ENT-TRIAL][downstream] Scaffold(Preview/Comment 1-4)開始...")
    with cl.logging_context(THEME_ID, "scaffold_b1b"):
        support = sc.run_b1_scaffold(client, parts, level_dir, src_text)
    support_status = {k: v.get("status") for k, v in support.items()}
    downstream_log["steps"].append({"step": "scaffold", "status": "OK", "support_status": support_status})

    jpy, _ = runner.compute_cost_jpy_so_far(cost_log_path)
    if jpy >= budget_jpy:
        downstream_log["status"] = "STOPPED_BUDGET_EXCEEDED_AFTER_SCAFFOLD"
        downstream_log["jpy_so_far"] = jpy
        save_json(f"{out_dir}/downstream_log.json", downstream_log)
        print(f"[ENT-TRIAL][downstream] STOP: scaffold後の累計費用¥{jpy:.2f}が上限到達。")
        return

    print("[ENT-TRIAL][downstream] Key Phrase選定開始...")
    with cl.logging_context(THEME_ID, "keyphrase_b1b"):
        kp = sc.run_key_phrases(src_text, f"{level_dir}/key_phrases", ARTICLE_ID, SOURCE_LEVEL,
                                 process="B1_SUPPORT")
    sel_status = kp["selection"]["status"]
    canon_status = (kp.get("canonicalization") or {}).get("status")
    redundancy_status = (kp.get("redundancy_qa") or {}).get("status")
    downstream_log["steps"].append({
        "step": "key_phrases", "selection_status": sel_status,
        "canonicalization_status": canon_status, "redundancy_qa_status": redundancy_status,
    })
    if kp.get("canonicalization") is None or canon_status not in (
            "CANONICALIZATION_PASS", "CANONICALIZATION_REVIEW_REQUIRED"):
        downstream_log["status"] = "STOPPED_KEY_PHRASE_FAIL"
        save_json(f"{out_dir}/downstream_log.json", downstream_log)
        print(f"[ENT-TRIAL][downstream] STOP: Key Phrase失敗 selection={sel_status} canon={canon_status}")
        return
    if redundancy_status == "REDUNDANCY_NG":
        downstream_log["status"] = "STOPPED_KEY_PHRASE_REDUNDANCY_NG"
        save_json(f"{out_dir}/downstream_log.json", downstream_log)
        print("[ENT-TRIAL][downstream] STOP: Key Phrase Redundancy QAがretry上限到達後もNG。")
        return

    jpy, _ = runner.compute_cost_jpy_so_far(cost_log_path)
    if jpy >= budget_jpy:
        downstream_log["status"] = "STOPPED_BUDGET_EXCEEDED_BEFORE_TTS"
        downstream_log["jpy_so_far"] = jpy
        save_json(f"{out_dir}/downstream_log.json", downstream_log)
        print(f"[ENT-TRIAL][downstream] STOP: TTS前の累計費用¥{jpy:.2f}が上限到達。")
        return

    import er003_v1_n3_01_tts_generate as tts_gen

    theme = {"theme_id": THEME_ID, "out_dir": out_dir}
    print("[ENT-TRIAL][downstream] TTS(Standard同期)開始...")
    with cl.logging_context(THEME_ID, "tts_b1b"):
        tts_result = tts_gen.generate_b1_segments(theme)
    downstream_log["steps"].append({"step": "tts", "result_keys": list(tts_result.keys())
                                     if isinstance(tts_result, dict) else None})

    jpy, _ = runner.compute_cost_jpy_so_far(cost_log_path)
    if jpy >= budget_jpy:
        downstream_log["status"] = "STOPPED_BUDGET_EXCEEDED_AFTER_TTS"
        downstream_log["jpy_so_far"] = jpy
        save_json(f"{out_dir}/downstream_log.json", downstream_log)
        print(f"[ENT-TRIAL][downstream] STOP: TTS後の累計費用¥{jpy:.2f}が上限到達。Assemblyへは進みません。")
        return

    import er003_v1_n3_01_assemble as asm

    print("[ENT-TRIAL][downstream] Assembly開始...")
    with cl.logging_context(THEME_ID, "assemble_b1b"):
        try:
            assemble_result = asm.stage_assemble_b1(theme)
            assemble_result["gate_off_result"] = "PASS"
        except RuntimeError as e:
            assemble_result = {"status": "GATE_BLOCKED", "gate_off_result": "BLOCKED", "error": str(e)}
    downstream_log["steps"].append({
        "step": "assemble",
        "result": {k: v for k, v in assemble_result.items() if k not in ("article_text",)},
    })

    gate_on = {"gate_on_result": "SKIPPED(gate_off_blocked)"}
    if assemble_result.get("gate_off_result") == "PASS":
        rs = asm.derive_a_family_required_structure("B1")
        try:
            asm.verify_episode_audio_validation_gate(level_dir, "B1", required_structure=rs)
            gate_on = {"gate_on_result": "PASS"}
        except RuntimeError as e:
            gate_on = {"gate_on_result": "BLOCKED", "gate_on_message": str(e)[:800]}
    downstream_log["steps"].append({"step": "audio_validation_gate_opt_in", "result": gate_on})

    jpy, by_provider = runner.compute_cost_jpy_so_far(cost_log_path)
    downstream_log["status"] = "COMPLETED"
    downstream_log["gate_off_result"] = assemble_result.get("gate_off_result")
    downstream_log["gate_on_result"] = gate_on.get("gate_on_result")
    downstream_log["jpy_so_far"] = jpy
    downstream_log["by_provider_jpy"] = by_provider
    save_json(f"{out_dir}/downstream_log.json", downstream_log)
    print(f"[ENT-TRIAL][downstream] 完了。gate_off={assemble_result.get('gate_off_result')} "
          f"gate_on={gate_on.get('gate_on_result')} 累計費用=¥{jpy:.2f}")
    record_sha256_snapshot(out_dir, "post_downstream")


# ============================================================
# Step 7: Side Hook(合否に無関係、失敗しても継続)
# ============================================================
def step_side_hook(out_dir: str) -> None:
    import er005_cost_logger as cl

    record_sha256_snapshot(out_dir, "pre_side_hook")
    article_path = f"{out_dir}/stage2_r2.md"
    result = {"status": "NOT_RUN"}
    try:
        article_text = load_text(article_path)
        client = get_client()
        cl.install(f"{out_dir}/raw_usage_log.jsonl")
        user = HOOK_USER_TEMPLATE.format(topic=TOPIC_JA, article_full_text=article_text)
        with cl.logging_context(THEME_ID, "side_hook"):
            t0 = time.time()
            response = client.responses.create(
                model=HOOK_MODEL, reasoning={"effort": HOOK_EFFORT},
                text={"format": {"type": "json_schema", **HOOK_SCHEMA}},
                input=[{"role": "developer", "content": HOOK_DEVELOPER}, {"role": "user", "content": user}],
            )
            latency = time.time() - t0
        parsed = json.loads(response.output_text)
        usage = usage_to_dict(getattr(response, "usage", None))
        cost_usd = compute_call_cost_usd(usage, model=response.model)
        result = {
            "status": "OK", "hook_ja": parsed.get("hook_ja"), "used_angle_ja": parsed.get("used_angle_ja"),
            "model": response.model, "response_id": response.id, "usage": usage,
            "latency_seconds": latency, "usd": cost_usd,
        }
        append_cost_entry(out_dir, {"stage": "side_hook", "model": response.model,
                                     "response_id": response.id, "usage": usage,
                                     "latency_seconds": latency, "usd": cost_usd})
    except Exception as e:
        result = {"status": "FAILED", "error": f"{type(e).__name__}: {e}"}
        print(f"[ENT-TRIAL][side-hook] 失敗(Main Trialの合否には影響しません): {result['error']}")

    save_json(f"{out_dir}/side_hook_luna.json", result)

    titles = load_json(f"{out_dir}/titles.json") if os.path.exists(f"{out_dir}/titles.json") else {}
    r2_title = titles.get("2", "(unknown)")
    hook_ja = result.get("hook_ja", "(FAILED)")
    comparison_md = (
        "# R2 Title vs Luna Hook\n\n"
        "| R2 Title (English, Production正式表示Hook) | Luna Hook (比較観測用、合否に無関係) |\n"
        "|---|---|\n"
        f"| {r2_title} | {hook_ja} |\n"
    )
    save_text(f"{out_dir}/hook_comparison.md", comparison_md)
    print(f"[ENT-TRIAL][side-hook] status={result['status']} hook_ja={hook_ja!r}")
    record_sha256_snapshot(out_dir, "post_side_hook")


# ============================================================
# CLI
# ============================================================
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--step", required=True,
                         choices=["research", "write", "gates", "downstream", "side-hook"])
    parser.add_argument("--stages", default="0,1,2")
    parser.add_argument("--level", default="b1")
    parser.add_argument("--only-if-gates-pass", action="store_true")
    parser.add_argument("--budget-jpy", type=float, default=250.0)
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    if args.step == "research":
        step_research(args.out_dir)
    elif args.step == "write":
        if args.level != "b1":
            raise ValueError("levelはb1のみ対応(A2は対象外、委任文6節)")
        stages = [int(s) for s in args.stages.split(",") if s.strip() != ""]
        step_write(args.out_dir, stages)
    elif args.step == "gates":
        step_gates(args.out_dir)
    elif args.step == "downstream":
        step_downstream(args.out_dir, args.only_if_gates_pass, args.budget_jpy)
    elif args.step == "side-hook":
        step_side_hook(args.out_dir)


if __name__ == "__main__":
    main()
