# ============================================================
# er019_family_x_entertainment_production_runner_01.py
# NEWS-FAMILY-X-B3-FACT-SELECTION-PRODUCTION-WIRING-01
# ============================================================
# 目的: Family X/Entertainment系統の正式Production入口(新entry point)。
# ユーザー確定事項(2026-09-26)の正式フローを実装する:
#   Research -> Full Fact Ledger -> AIが中心Storylineを1つ決定
#   -> B3 4テストを全Factへ適用 -> Selected Fact Brief -> Writer
#   -> Original->R1->R2 -> Advanced -> Standard
#
# 既存Production primitiveの再利用のみで構成する(新規実装は
# Storyline+B3 1 call [er019_family_x_storyline_b3_fact_selection_01.py]
# とJA Writer Production移設[er019_family_x_ja_writer_o_r1_r2_01.py]の
# 2点のみ):
#   - Research/Ledger: er012_e_family_entertainment_two_level_runner_01.
#     run_researcher_for_topic/run_verification_for_topic
#     (関数を直接呼ぶ。ステージ別costタグ付けのため、同runnerの
#     build_ledger_for_topic()の保存ロジックをここで踏襲するが、
#     API呼び出し自体はrun_researcher_for_topic/run_verification_for_topic
#     をそのまま呼ぶ[重複実装しない])。
#   - Advanced/Standard/deviation check/retry: 同runnerの
#     run_writer_stage()をそのまま呼ぶ(無改変)。
#
# **Mandatory STOP(構造的)**: 本runnerはscaffold/tts/assemble/player関連の
# 関数を一切importしない。Standard生成までで必ず停止する
# (--stop-after既定"standard"、それ以降のstage自体がコード上存在しない)。
#
# 実行方法:
#   .venv/Scripts/python.exe er019_family_x_entertainment_production_runner_01.py \
#       --theme "<Research用topic文字列>" --slug <slug> --out-dir <dir> \
#       [--source-note "<由来メモ>"] [--budget-jpy 150] \
#       [--stage research|ledger|storyline_b3|writer|advanced|standard|all] \
#       [--regenerate-stage storyline_b3|writer|advanced|standard] \
#       [--stop-after storyline_b3|writer|advanced|standard(既定)]
# ============================================================
from __future__ import annotations

import argparse
import hashlib
import json
import os
import time

import er003_v1_en_direct_vfl_01_generate as vfl01
import er005_cost_logger as cl
import er012_e_family_entertainment_two_level_runner_01 as efam
import er019_family_x_ja_writer_o_r1_r2_01 as jaw
import er019_family_x_storyline_b3_fact_selection_01 as b3

MANAGEMENT_ID = "NEWS-FAMILY-X-B3-FACT-SELECTION-PRODUCTION-WIRING-01"
RUNNER_TAG = "NEWS_FAMILY_X_B3_PRODUCTION_RUNNER_01"

STAGE_ORDER = ["research_ledger", "storyline_b3", "writer", "advanced", "standard"]
# CLI --stage/--stop-after 語彙("research"/"ledger"はどちらもresearch_ledger
# stageへ写像する。既存primitive[run_researcher_for_topic単独では検証まで
# 到達しないためLedgerとして未確定]がResearcherとVerificationを1組として
# 構築する設計であり、分割再実行はサポートしない、既存er012runnerと同じ
# 制約)。
STAGE_ALIASES = {
    "research": "research_ledger",
    "ledger": "research_ledger",
    "research_ledger": "research_ledger",
    "storyline_b3": "storyline_b3",
    "writer": "writer",
    "advanced": "advanced",
    "standard": "standard",
    "all": "all",
}


# ------------------------------------------------------------
# 共通ヘルパー(efamのものをそのまま再利用、独自実装しない)
# ------------------------------------------------------------
load_json = efam.load_json
save_json = efam.save_json
load_text = efam.load_text
save_text = efam.save_text
sha256_text = efam.sha256_text
sha256_file = efam.sha256_file


def self_sha256(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


# ------------------------------------------------------------
# Stage 1: Research -> Full Fact Ledger(既存efam primitiveをそのまま呼ぶ、
# stage別costタグ付けのため保存ロジックのみここで踏襲する)
# ------------------------------------------------------------
def run_research_and_ledger(client, topic: str, ledger_dir: str) -> dict:
    if os.path.exists(f"{ledger_dir}/verified_fact_ledger.txt"):
        print(f"[B3-RUNNER][research_ledger] 既存Ledgerを再利用(既生成済み): {ledger_dir}")
        return {
            "ledger_text": load_text(f"{ledger_dir}/verified_fact_ledger.txt"),
            "reused": True,
        }

    os.makedirs(f"{ledger_dir}/audit", exist_ok=True)
    print(f"[B3-RUNNER][research] Researcher呼び出し開始(topic={topic[:60]!r}...)...")
    with cl.logging_context(RUNNER_TAG, "research"):
        research = efam.run_researcher_for_topic(client, topic)
    print(f"[B3-RUNNER][research] facts={len(research['parsed']['facts'])} "
          f"web_search_calls={research['search_usage']['web_search_call_count']}")
    save_json(f"{ledger_dir}/fact_ledger_draft.json", research["parsed"])
    save_json(f"{ledger_dir}/audit/researcher_full_record.json",
              {k: v for k, v in research.items() if k != "parsed"})

    print("[B3-RUNNER][ledger] Verification呼び出し開始...")
    with cl.logging_context(RUNNER_TAG, "ledger"):
        verification = efam.run_verification_for_topic(client, topic, research["parsed"])
    save_json(f"{ledger_dir}/fact_ledger_verification.json", verification["parsed"])
    save_json(f"{ledger_dir}/audit/verification_full_record.json",
              {k: v for k, v in verification.items() if k != "parsed"})

    ledger_text, verdict_counts, kept_facts = vfl01.build_verified_ledger_text(
        research["parsed"], verification["parsed"])
    save_text(f"{ledger_dir}/verified_fact_ledger.txt", ledger_text)
    save_json(f"{ledger_dir}/verdict_counts.json", verdict_counts)
    print(f"[B3-RUNNER][ledger] Ledger確定。verdict_counts={verdict_counts} "
          f"kept_facts={len(kept_facts)}")

    runtime_evidence = {
        "research": {
            "model_id_actual": research["model"], "response_id": research["response_id"],
            "web_search_call_count": research["search_usage"]["web_search_call_count"],
        },
        "ledger_verification": {
            "model_id_actual": verification["model"], "response_id": verification["response_id"],
        },
        "verdict_counts": verdict_counts, "kept_facts_count": len(kept_facts),
        "reused": False,
    }
    save_json(f"{ledger_dir}/runtime_evidence.json", runtime_evidence)
    return {"ledger_text": ledger_text, "reused": False, "runtime_evidence": runtime_evidence}


# ------------------------------------------------------------
# Stage 2: AI Storyline決定 + B3 4テスト(LLM 1 call)
# ------------------------------------------------------------
def run_storyline_b3(client, topic: str, ledger_text: str, out_dir: str) -> dict:
    stage_dir = f"{out_dir}/storyline_b3"
    os.makedirs(stage_dir, exist_ok=True)
    selection = b3.run_storyline_b3_selection(
        client, topic, ledger_text, model=vfl01.MODEL, effort=vfl01.REASONING_EFFORT)

    ledger_fact_ids = selection["ledger_fact_ids"]
    full_ledger_record = b3.build_full_ledger_record(topic, ledger_text, ledger_fact_ids)
    save_json(f"{stage_dir}/full_ledger.json", full_ledger_record)

    brief_md = b3.build_selected_brief_markdown(selection)
    save_text(f"{stage_dir}/selected_brief.md", brief_md)

    fact_selection_evidence = {
        "selected_storyline": selection["parsed"]["selected_storyline"],
        "full_ledger_fact_ids": ledger_fact_ids,
        "fact_tests": selection["parsed"]["fact_tests"],
        "selected_fact_ids": selection["parsed"]["selected_fact_ids"],
        "selected_fact_brief_text": selection["parsed"]["selected_fact_brief"],
        "recheck_note": selection["parsed"]["recheck_note"],
        "soft_warnings": selection["soft_warnings"],
    }
    save_json(f"{stage_dir}/fact_selection_evidence.json", fact_selection_evidence)

    runtime_evidence = {
        "model_id_actual": selection["model"], "response_id": selection["response_id"],
        "latency_seconds": selection["latency_seconds"], "attempts": selection["attempts"],
        "retried": selection["retried"], "prompt_shas": selection["prompt_shas"],
        "attempts_log": selection["attempts_log"],
    }
    save_json(f"{stage_dir}/runtime_evidence.json", runtime_evidence)
    return {
        "selected_storyline": selection["parsed"]["selected_storyline"],
        "selected_fact_brief_text": selection["parsed"]["selected_fact_brief"],
        "selected_brief_markdown": brief_md,
        "fact_selection_evidence": fact_selection_evidence,
        "runtime_evidence": runtime_evidence,
    }


# ------------------------------------------------------------
# Stage 3: JA Writer(Original -> R1 -> R2)
# ------------------------------------------------------------
def run_ja_writer(client, storyline_line: str, selected_fact_brief_text: str, out_dir: str) -> dict:
    stage_dir = f"{out_dir}/ja_writer"
    os.makedirs(stage_dir, exist_ok=True)
    result = jaw.run_ja_writer_o_r1_r2(client, storyline_line, selected_fact_brief_text)

    save_text(f"{stage_dir}/original.md", result["stages"]["original"]["text"])
    save_text(f"{stage_dir}/revision1.md", result["stages"]["r1"]["text"])
    save_text(f"{stage_dir}/revision2.md", result["stages"]["r2"]["text"])

    runtime_evidence = {
        "original": {k: v for k, v in result["stages"]["original"].items() if k != "text"},
        "r1": {k: v for k, v in result["stages"]["r1"].items() if k != "text"},
        "r2": {k: v for k, v in result["stages"]["r2"].items() if k != "text"},
        "chain_method": result["chain_method"], "verbatim_shas": result["verbatim_shas"],
        "title": result["title"],
    }
    save_json(f"{stage_dir}/runtime_evidence.json", runtime_evidence)
    return {"ja_text": result["final_text"], "title": result["title"], "runtime_evidence": runtime_evidence}


# ------------------------------------------------------------
# コスト集計(stage別、web_search_call費用も含める。
# efam.compute_cost_jpy_so_far()はtoken費用のみでweb_search_call費用を
# 含まないため[既存の既知の粒度差、Production budget guardは
# efam.assert_budget_ok経由でそのまま流用し変更しない]、本runnerの
# cost.json用に別途web_search_call費用込みで集計する)。
# ------------------------------------------------------------
def compute_stage_cost_breakdown(cost_log_path: str) -> dict:
    if not os.path.exists(cost_log_path):
        return {"by_stage": {}, "total_jpy": 0.0}
    price = efam._load_pricing()
    by_stage = {}
    total_usd = 0.0
    with open(cost_log_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            provider = rec.get("provider")
            model = rec.get("model_id") or rec.get("model")
            stage = rec.get("stage") or "UNTAGGED"
            usd = 0.0
            if provider == "openai" and model:
                in_tok = rec.get("input_tokens") or 0
                out_tok = rec.get("output_tokens") or 0
                try:
                    usd += in_tok * price("openai", model, "input_tokens") / 1e6
                    usd += out_tok * price("openai", model, "output_tokens") / 1e6
                except StopIteration:
                    pass
                ws_calls = rec.get("web_search_call_count") or 0
                if ws_calls:
                    try:
                        usd += ws_calls * price("openai", "N/A (tool, all models)", "web_search_call") / 1000
                    except StopIteration:
                        pass
            total_usd += usd
            by_stage[stage] = by_stage.get(stage, 0.0) + usd
    usd_jpy = efam.USD_JPY
    return {
        "by_stage_jpy": {k: round(v * usd_jpy, 3) for k, v in by_stage.items()},
        "total_jpy": round(total_usd * usd_jpy, 3),
    }


# ------------------------------------------------------------
# CLI
# ------------------------------------------------------------
def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--theme", required=True,
                         help="Research用topic文字列(記事テーマの説明)。")
    parser.add_argument("--slug", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--source-note", default="",
                         help="由来メモ(evidenceとして記録のみ、Research promptには使わない)。")
    parser.add_argument("--budget-jpy", type=float, default=150.0)
    parser.add_argument("--stage", default="all",
                         choices=("research", "ledger", "storyline_b3", "writer",
                                  "advanced", "standard", "all"))
    parser.add_argument("--regenerate-stage", default=None,
                         choices=("storyline_b3", "writer", "advanced", "standard"))
    parser.add_argument("--stop-after", default="standard",
                         choices=("storyline_b3", "writer", "advanced", "standard"))
    return parser


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()

    out_dir = args.out_dir
    os.makedirs(out_dir, exist_ok=True)
    cl.install(f"{out_dir}/raw_usage_log.jsonl")

    save_json(f"{out_dir}/entry_point.json", {
        "runner": "er019_family_x_entertainment_production_runner_01.py",
        "management_id": MANAGEMENT_ID,
        "runner_sha256": self_sha256(__file__),
        "b3_module_sha256": self_sha256(b3.__file__),
        "ja_writer_module_sha256": self_sha256(jaw.__file__),
        "args": vars(args),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
    })

    theme = {"theme_id": args.slug, "topic": args.theme, "out_dir": out_dir,
              "ledger_path": f"{out_dir}/research_ledger/verified_fact_ledger.txt"}

    client = vfl01.get_client()
    stage = STAGE_ALIASES[args.stage]

    ledger_dir = f"{out_dir}/research_ledger"
    ledger_result = run_research_and_ledger(client, args.theme, ledger_dir)
    ledger_text = ledger_result["ledger_text"]
    efam.assert_budget_ok(out_dir, args.budget_jpy, "after research_ledger")
    if stage == "research_ledger":
        print("[B3-RUNNER] stage=research/ledger 完了。--stage storyline_b3以降は未実行。")
        _write_cost_json(out_dir)
        return

    storyline_dir = f"{out_dir}/storyline_b3"
    need_storyline = (stage in ("storyline_b3", "writer", "advanced", "standard", "all")
                       or args.regenerate_stage == "storyline_b3")
    if need_storyline:
        if (os.path.exists(f"{storyline_dir}/selected_brief.md")
                and args.regenerate_stage != "storyline_b3"
                and stage != "storyline_b3"):
            print(f"[B3-RUNNER][storyline_b3] 既存Selected Fact Briefを再利用: {storyline_dir}")
            fact_evidence = load_json(f"{storyline_dir}/fact_selection_evidence.json")
            storyline_result = {
                "selected_storyline": fact_evidence["selected_storyline"],
                "selected_fact_brief_text": fact_evidence["selected_fact_brief_text"],
            }
        else:
            storyline_result = run_storyline_b3(client, args.theme, ledger_text, out_dir)
            efam.assert_budget_ok(out_dir, args.budget_jpy, "after storyline_b3")
        if stage == "storyline_b3" or args.stop_after == "storyline_b3":
            print("[B3-RUNNER] stage=storyline_b3で停止(--stop-after storyline_b3)。")
            _write_cost_json(out_dir)
            return
    else:
        storyline_result = None

    ja_writer_dir = f"{out_dir}/ja_writer"
    need_writer = stage in ("writer", "advanced", "standard", "all") or args.regenerate_stage == "writer"
    if need_writer:
        if (os.path.exists(f"{ja_writer_dir}/revision2.md")
                and args.regenerate_stage != "writer" and stage != "writer"):
            print(f"[B3-RUNNER][writer] 既存JA記事(R2)を再利用: {ja_writer_dir}/revision2.md")
            ja_text = load_text(f"{ja_writer_dir}/revision2.md")
        else:
            writer_result = run_ja_writer(
                client, storyline_result["selected_storyline"],
                storyline_result["selected_fact_brief_text"], out_dir)
            ja_text = writer_result["ja_text"]
            efam.assert_budget_ok(out_dir, args.budget_jpy, "after ja_writer")
        if stage == "writer" or args.stop_after == "writer":
            print("[B3-RUNNER] stage=writerで停止(--stop-after writer)。")
            _write_cost_json(out_dir)
            return
    else:
        ja_text = load_text(f"{ja_writer_dir}/revision2.md") if os.path.exists(f"{ja_writer_dir}/revision2.md") else ""

    if stage in ("advanced", "all") or args.regenerate_stage == "advanced":
        with cl.logging_context(RUNNER_TAG, "advanced"):
            efam.run_writer_stage(client, theme, ja_text, ledger_text, args.budget_jpy, only="advanced")
        efam.assert_budget_ok(out_dir, args.budget_jpy, "after advanced")
        if stage == "advanced" or args.stop_after == "advanced":
            print("[B3-RUNNER] stage=advancedで停止(--stop-after advanced、Mandatory STOP)。")
            _write_cost_json(out_dir)
            return

    if stage in ("standard", "all") or args.regenerate_stage == "standard":
        with cl.logging_context(RUNNER_TAG, "standard"):
            efam.run_writer_stage(client, theme, ja_text, ledger_text, args.budget_jpy, only="standard")
        efam.assert_budget_ok(out_dir, args.budget_jpy, "after standard")

    print("[B3-RUNNER] Standardまで完了。Mandatory STOP(ユーザー確認前に後工程[scaffold/tts/"
          "assemble/player]へは進みません。本runnerにはそれらのstage自体が実装されていません)。")
    _write_cost_json(out_dir)


def _write_cost_json(out_dir: str) -> None:
    breakdown = compute_stage_cost_breakdown(f"{out_dir}/raw_usage_log.jsonl")
    save_json(f"{out_dir}/cost.json", breakdown)
    print(f"[B3-RUNNER][cost] {breakdown}")


if __name__ == "__main__":
    main()
