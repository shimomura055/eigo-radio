# ============================================================
# er013_family_c_future_trial_06_run.py
# 管理ID: EDITORIAL-FUTURE-FAMILY-C-V6-CORE-PROVOCATION-REDESIGN-TRIAL-06
# ============================================================
# 目的: 新原則「Provocative Future Premise -> Core Provocation -> Story ->
# Evidence / Safety Boundary Check」のTrial driver。
# flow: (BCIのみ)最小CURRENT FACT収集 -> Core Provocation候補生成・選定
#       -> Writer(制約最小、v6契約) -> Story Spark Gate(最上位Gate)
#       -> (PASS時のみ)Fact Safety 3レイヤー -> 比較HTML/Markdown生成
#
# 既存er013_family_c_future_*_01〜05.py・er013_output/family_c_future_
# trial_01〜05/は一切変更しない。SSOT・Git操作もこのファイルからは行わ
# ない。**Production採用・配線ではない**(Gate 1材料までのTrial、最大
# Status: VALIDATED)。
#
# 実行方法(root直下から):
#   .venv/Scripts/python.exe er013_family_c_future_trial_06_run.py \
#       --theme home_robots --level a2 --budget-jpy 90
#   .venv/Scripts/python.exe er013_family_c_future_trial_06_run.py \
#       --theme home_robots --level a2 --budget-jpy 40 --variant 06b \
#       --improvement "<原因分類に対応する1変更>"
#   .venv/Scripts/python.exe er013_family_c_future_trial_06_run.py \
#       --theme bci --level a2 --budget-jpy 60 --variant 06_bmi
# ============================================================
from __future__ import annotations

import argparse
import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

import er005_cost_logger as cl
import er006_model_routing_contract_01 as routing
import er013_family_c_future_provocation_06 as prov6
import er013_family_c_future_qa_01 as fcq1
import er013_family_c_future_qa_02 as fcq2
import er013_family_c_future_safety_06 as safety6
import er013_family_c_future_spark_gate_06 as spark6
import er013_family_c_future_writer_06 as writer6
import er003_v1_en_direct_vfl_01_generate as vfl01

# ------------------------------------------------------------
# 費用実測(Trial-05と同一ロジック、read-onlyで転記。委任Read項目4)
# ------------------------------------------------------------
USD_JPY = 160.0
_PRICING = json.load(open("er005_output/cost_baseline_01/pricing_snapshot.json", encoding="utf-8"))["prices"]
FAMILY_C_V6_HARD_CAP_JPY = 182.13  # ユーザー指定のFamily C Trial残額ハード上限(06/06b/06_bmi合算、変更不可)
VARIANT_DIRS = ["family_c_future_trial_06", "family_c_future_trial_06b", "family_c_future_trial_06_bmi"]

MAX_WRITER_MARKER_RETRY = 3
WRITER_REASONING_EFFORT = vfl01.REASONING_EFFORT  # "high"(記事本文の質を優先)
JUDGE_REASONING_EFFORT = "medium"  # Provocation/Spark Gate/Safety軽判定はmediumでコスト抑制


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
        return 0.0, True
    except KeyError:
        return 0.0, True


def compute_cost_jpy_for_log(log_path: str) -> dict:
    if not os.path.exists(log_path):
        return {"total_jpy": 0.0, "by_provider_jpy": {}, "unpriced_records": 0, "total_records": 0}
    total_usd, by_provider, unpriced, n = 0.0, {}, 0, 0
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


def compute_family_c_v6_total_jpy() -> dict:
    """06/06b/06_bmiの3出力dir合算(ハード上限¥182.13はこの3つの合計に適用)。"""
    total, by_dir = 0.0, {}
    for d in VARIANT_DIRS:
        log_path = f"er013_output/{d}/raw_usage_log.jsonl"
        r = compute_cost_jpy_for_log(log_path)
        by_dir[d] = r["total_jpy"]
        total += r["total_jpy"]
    return {"total_jpy": round(total, 2), "by_dir_jpy": by_dir}


def save_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def save_text(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def load_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def budget_guard(stage_label: str, per_run_budget_jpy: float) -> dict:
    """総額ガード: 06/06b/06_bmi合算がハード上限を超えたらここでSTOPする
    (超過が確定してから停止するのではなく、各API呼び出し直後、次のより
    高コストな段へ進む**前**に毎回チェックする)。"""
    total = compute_family_c_v6_total_jpy()
    print(f"[budget_guard][{stage_label}] Family C v6合算={total['total_jpy']} JPY "
          f"(ハード上限{FAMILY_C_V6_HARD_CAP_JPY}, 本run上限{per_run_budget_jpy}) by_dir={total['by_dir_jpy']}")
    if total["total_jpy"] > FAMILY_C_V6_HARD_CAP_JPY:
        raise RuntimeError(
            f"[budget_guard][{stage_label}] Family C v6合算 {total['total_jpy']} JPY が"
            f"ハード上限{FAMILY_C_V6_HARD_CAP_JPY} JPYを超過しました。STOP(以降のAPI呼び出しは行わない)。")
    if total["total_jpy"] > per_run_budget_jpy:
        print(f"[budget_guard][{stage_label}] 警告: 本run向け目安予算{per_run_budget_jpy} JPYを超過"
              "(ハード上限内のため続行、目安超過として記録)。")
    return total


# ------------------------------------------------------------
# テーマ設定
# ------------------------------------------------------------
THEME_CONFIG = {
    "home_robots": {
        "topic_id": "home_robots",
        "theme_label_en": "the future of home robots",
        "topic_ja_placeholder": "家庭用ロボットと家事(home robots and housework)",
        "inspiration_note": (
            "A home robot is not scary because it might malfunction or go out of "
            "control. It is unsettling because it can become so convenient that a "
            "person slowly hands over small, everyday life choices to it, one at a "
            "time, without ever deciding to."
        ),
        "ledger_path": "er013_output/family_c_future_trial_01/research/layer1_only_ledger.txt",
    },
    "bci": {
        "topic_id": "bci",
        "theme_label_en": "the future of brain-computer interfaces",
        "topic_ja_placeholder": "脳とコンピュータをつなぐ技術(brain-computer interfaces)",
        "inspiration_note": (
            "When a brain connects directly to a machine, the privacy of a person's "
            "own unspoken thoughts becomes a new kind of problem -- not what a person "
            "says, but what a machine can read before they decide to say it."
        ),
        "ledger_path": None,
    },
}

# ------------------------------------------------------------
# BMI用: 事前指定Ledgerが無いテーマ向けの最小CURRENT FACT収集
# (LLM 1呼び出し、Web検索あり、候補5件程度 -> Fact Checker A'で事後検証)
# ------------------------------------------------------------
BCI_CANDIDATE_JSON_SCHEMA = {
    "name": "bci_current_fact_candidates",
    "schema": {
        "type": "object",
        "properties": {
            "facts": {
                "type": "array",
                "minItems": 4,
                "maxItems": 6,
                "items": {
                    "type": "object",
                    "properties": {
                        "fact_id": {"type": "string"},
                        "claim": {"type": "string"},
                        "source_title": {"type": "string"},
                        "source_url": {"type": "string"},
                    },
                    "required": ["fact_id", "claim", "source_title", "source_url"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["facts"],
        "additionalProperties": False,
    },
    "strict": True,
}

BCI_CANDIDATE_DEVELOPER_MESSAGE = (
    "You are a researcher collecting a small number of CURRENT, real, verifiable facts "
    "about brain-computer interface (BCI) technology as it exists today. Use web search. "
    "Only include facts you can point to a real, checkable source for."
)


def generate_bci_current_fact_candidates(client, model: str, reasoning_effort: str) -> dict:
    response = client.responses.create(
        model=model,
        reasoning={"effort": reasoning_effort},
        tools=[{"type": "web_search"}],
        text={"format": {"type": "json_schema", **BCI_CANDIDATE_JSON_SCHEMA}},
        input=[
            {"role": "developer", "content": BCI_CANDIDATE_DEVELOPER_MESSAGE},
            {"role": "user", "content": "List 5 current, real, verifiable facts about brain-computer "
                                         "interface technology today (e.g. approved medical devices, "
                                         "published clinical trial results, company product status). "
                                         "Give each a short fact_id like BCI-001."},
        ],
    )
    return {"parsed": json.loads(response.output_text), "model": response.model, "response_id": response.id}


def build_ledger_text_from_bci_candidates(parsed: dict) -> str:
    lines = ["[PRESENT_FACT] (Trial-06_bmi収集、事後Fact Checker A'検証対象)"]
    for f in parsed["facts"]:
        lines.append(f"[CANDIDATE] {f['fact_id']}: {f['claim']}")
        lines.append(f"  source: {f['source_title']} ({f['source_url']})")
    return "\n".join(lines)


# ------------------------------------------------------------
# Stage 1: Core Provocation候補生成・選定
# ------------------------------------------------------------
def stage_provocation(client, theme_id: str, out_dir: str, theme_cfg: dict, ledger_context_text: str,
                       per_run_budget_jpy: float) -> tuple:
    prompt = prov6.build_provocation_prompt(
        theme_cfg["theme_label_en"], theme_cfg["inspiration_note"], ledger_context_text)
    save_text(f"{out_dir}/provocation/prompt.txt", prompt)
    model = routing.require_model_or_override(
        "A2_WRITER", routing.WRITER_MODEL,
        override_reason="v6 Trial: Core Provocation候補生成にA2_WRITER Approved Model(Luna)を転用"
                         "(新規process未定義、コスト影響なし、DEV/Trial限定)")
    with cl.logging_context(theme_id, "provocation"):
        result = prov6.generate_core_provocation_candidates(client, model, JUDGE_REASONING_EFFORT, prompt)
    parsed = result["parsed"]
    table = prov6.build_score_table(parsed)
    selected = prov6.get_selected_candidate(parsed)
    save_json(f"{out_dir}/provocation/candidates.json", {
        "parsed": parsed, "score_table": table, "model": result["model"], "response_id": result["response_id"],
    })
    header = "| id | future_leap | excitement | tension | thought_prov | distance | evidence_conn | total | selected |\n"
    header += "|---|---|---|---|---|---|---|---|---|\n"
    rows = "".join(
        f"| {r['id']} | {r['future_leap_score']} | {r['excitement_score']} | {r['tension_score']} | "
        f"{r['thought_provoking_score']} | {r['distance_from_current_score']} | "
        f"{r['evidence_connection_score']} | {r['total_score']} | {'YES' if r['is_selected'] else ''} |\n"
        for r in table)
    selected_md = (
        f"# Core Provocation候補一覧({theme_cfg['theme_label_en']})\n\n{header}{rows}\n"
        f"## 選定: {selected['id']}\n\n**Core Provocation**: {selected['core_provocation']}\n\n"
        f"**Premise**: {selected['premise']}\n\n**Safety boundary note**: {selected['safety_boundary_note']}\n\n"
        f"**選定理由(LLM自己申告)**: {parsed['selection_rationale']}\n"
    )
    save_text(f"{out_dir}/provocation/selected.md", selected_md)
    budget_guard("after_provocation", per_run_budget_jpy)
    return parsed, selected, table


# ------------------------------------------------------------
# Stage 2: Writer(マーカー技術的retryのみ、内容再生成はしない)
# ------------------------------------------------------------
def generate_writer_with_marker_retry(client, theme_id: str, out_dir: str, prompt: str) -> tuple:
    model = routing.require_model("A2_WRITER", routing.WRITER_MODEL)
    attempts = []
    for attempt in range(1, MAX_WRITER_MARKER_RETRY + 1):
        with cl.logging_context(theme_id, f"writer_attempt{attempt}"):
            result = writer6.generate_family_c_article_v6(
                client, model=model, reasoning_effort=WRITER_REASONING_EFFORT, prompt=prompt)
        text_no_meta = fcq2.strip_meta_blocks(result["raw_text"])
        imagined_check = fcq1.validate_markers_balanced(text_no_meta)
        fact_check_balance = fcq2.validate_fact_markers_balanced(text_no_meta)
        balanced = imagined_check["balanced"] and fact_check_balance["balanced"]
        attempts.append({"attempt": attempt, "imagined_check": imagined_check,
                          "fact_check_balance": fact_check_balance, "response_id": result["response_id"]})
        if balanced:
            save_json(f"{out_dir}/a2/writer_attempts.json", attempts)
            return result["raw_text"], attempts
        print(f"[{theme_id}] Writer attempt {attempt}: マーカー不整合(technical retry)"
              f" imagined={imagined_check} fact={fact_check_balance}")
    save_json(f"{out_dir}/a2/writer_attempts.json", attempts)
    raise RuntimeError(f"マーカー整合の取れたWriter出力が{MAX_WRITER_MARKER_RETRY}回の技術的retryでも"
                        "得られませんでした。STOP(NG_REVIEW_REQUIRED)。")


def stage_writer(client, theme_id: str, out_dir: str, theme_cfg: dict, selected: dict,
                  ledger_context_text: str, improvement_note: str, per_run_budget_jpy: float) -> dict:
    prompt = writer6.build_family_c_writer_v6_prompt(
        core_provocation=selected["core_provocation"], premise=selected["premise"],
        theme_label=theme_cfg["theme_label_en"], ledger_excerpt=ledger_context_text,
        improvement_note=improvement_note or "")
    save_text(f"{out_dir}/a2/writer_prompt.txt", prompt)
    article_text, attempts = generate_writer_with_marker_retry(client, theme_id, out_dir, prompt)
    save_text(f"{out_dir}/a2/writer_raw_article.txt", article_text)
    layers = safety6.extract_layers(article_text)
    save_text(f"{out_dir}/a2/reader_facing_article.txt", layers["reader_text"])
    word_count = len(layers["reader_text"].split())
    save_json(f"{out_dir}/a2/word_count.json", {
        "word_count": word_count, "target": writer6.WORD_TARGET,
        "acceptable_range": list(writer6.WORD_ACCEPTABLE_RANGE),
        "within_acceptable_range": writer6.WORD_ACCEPTABLE_RANGE[0] <= word_count <= writer6.WORD_ACCEPTABLE_RANGE[1],
    })
    budget_guard("after_writer", per_run_budget_jpy)
    return {"article_text": article_text, "layers": layers, "word_count": word_count}


# ------------------------------------------------------------
# Stage 3: Story Spark Gate(最上位Gate)
# ------------------------------------------------------------
def stage_spark_gate(client, theme_id: str, out_dir: str, core_provocation: str, reader_text: str,
                      per_run_budget_jpy: float) -> dict:
    prompt = spark6.build_spark_gate_prompt(core_provocation, reader_text)
    save_text(f"{out_dir}/a2/spark_gate_prompt.txt", prompt)
    model = routing.require_model_or_override(
        "A2_WRITER", routing.WRITER_MODEL,
        override_reason="v6 Trial: Story Spark Gate判定にA2_WRITER Approved Model(Luna)を転用"
                         "(新規process未定義、コスト影響なし、DEV/Trial限定)")
    with cl.logging_context(theme_id, "spark_gate"):
        result = spark6.run_story_spark_gate(client, model, JUDGE_REASONING_EFFORT, prompt)
    verdict = spark6.compute_verdict(result["parsed"])
    save_json(f"{out_dir}/a2/spark_gate_result.json", {
        "parsed": result["parsed"], "verdict": verdict, "model": result["model"], "response_id": result["response_id"],
    })
    budget_guard("after_spark_gate", per_run_budget_jpy)
    return verdict


# ------------------------------------------------------------
# Stage 4: Fact Safety(3レイヤー、Spark Gate PASS時のみ)
# ------------------------------------------------------------
def stage_safety(client, theme_id: str, out_dir: str, theme_cfg: dict, layers: dict,
                  layer1_ledger_text: str, per_run_budget_jpy: float) -> dict:
    judge_model = routing.require_model_or_override(
        "A2_WRITER", routing.WRITER_MODEL,
        override_reason="v6 Trial: Plausibility Bridge/Imagined Future軽判定にA2_WRITER Approved "
                         "Model(Luna)を転用(新規process未定義、コスト影響なし、DEV/Trial限定)")
    result = safety6.run_safety_boundary_check(
        client, theme_id, theme_cfg["topic_ja_placeholder"], judge_model, JUDGE_REASONING_EFFORT,
        layers, layer1_ledger_text)
    save_json(f"{out_dir}/a2/safety_result.json", result)
    budget_guard("after_safety", per_run_budget_jpy)
    return result


# ------------------------------------------------------------
# 比較Artifact
# ------------------------------------------------------------
TRIAL_05_A2_PATH = "er013_output/family_c_future_trial_05/a2/reader_facing_article.txt"


def build_comparison_md(out_dir: str, theme_label: str, core_provocation: str, v6_reader_text: str,
                         v6_word_count: int, spark_verdict: dict) -> None:
    v5_text = load_text(TRIAL_05_A2_PATH) if os.path.exists(TRIAL_05_A2_PATH) else "(見つかりません)"
    v5_word_count = len(v5_text.split())
    md = f"""# Trial-05(v5) vs Trial-06(v6)比較 -- {theme_label}

v5はユーザー人間評価で「NG。論外」(QA全PASSだが面白くない、Future Leapが
弱い)。v6はStory Spark Gateを最上位に置いた新設計。

## Core Provocation(v6のみ、v5には存在しない概念)
{core_provocation}

## 語数
- v5: {v5_word_count}語
- v6: {v6_word_count}語(目標約350語)

## Story Spark Gate(v6のみ、v5には存在しない)
- verdict: {spark_verdict['verdict']}
- scores: {json.dumps(spark_verdict['scores'], ensure_ascii=False)}
- 何が面白いか(1文): {spark_verdict['one_sentence_why_interesting']}

## 本文全文(v5)
```
{v5_text}
```

## 本文全文(v6)
```
{v6_reader_text}
```
"""
    save_text(f"{out_dir}/comparison.md", md)


def build_index_html(out_dir: str, theme_label: str, spark_verdict: dict, safety_result: dict | None,
                      v6_reader_text: str) -> None:
    safety_line = "(Spark Gate FAILのため未実施)" if safety_result is None else \
        f"overall_pass={safety_result['overall_pass']}"
    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>Family C v6 Trial -- {theme_label}</title></head>
<body style="font-family: sans-serif; max-width: 720px; margin: 2em auto; line-height: 1.6;">
<h1>Family C v6 Trial -- {theme_label}</h1>
<p><strong>Status: Trial only, NOT Production-approved.</strong></p>
<p>Story Spark Gate verdict: <strong>{spark_verdict['verdict']}</strong></p>
<p>Fact Safety: {safety_line}</p>
<h2>Article (reader-facing text)</h2>
<pre style="white-space: pre-wrap;">{v6_reader_text}</pre>
<h2>Links</h2>
<ul>
<li><a href="a2/reader_facing_article.txt">reader_facing_article.txt</a></li>
<li><a href="a2/spark_gate_result.json">spark_gate_result.json</a></li>
<li><a href="a2/safety_result.json">safety_result.json</a></li>
<li><a href="provocation/selected.md">provocation/selected.md</a></li>
<li><a href="comparison.md">comparison.md (vs Trial-05)</a></li>
<li><a href="cost_summary.json">cost_summary.json</a></li>
</ul>
</body></html>
"""
    save_text(f"{out_dir}/index.html", html)


# ------------------------------------------------------------
# main
# ------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--theme", choices=["home_robots", "bci"], required=True)
    parser.add_argument("--level", choices=["a2"], default="a2")
    parser.add_argument("--budget-jpy", type=float, required=True)
    parser.add_argument("--variant", default="06")
    parser.add_argument("--improvement", default="")
    args = parser.parse_args()

    theme_id = f"family_c_future_trial_{args.variant}"
    out_dir = f"er013_output/{theme_id}"
    log_path = f"{out_dir}/raw_usage_log.jsonl"
    cl.install(log_path)
    theme_cfg = THEME_CONFIG[args.theme]

    budget_guard("start", args.budget_jpy)

    client = vfl01.get_client()

    if theme_cfg["ledger_path"]:
        ledger_context_text = load_text(theme_cfg["ledger_path"])
        layer1_ledger_text = ledger_context_text
    else:
        model = routing.require_model_or_override(
            "A2_WRITER", routing.WRITER_MODEL,
            override_reason="v6 Trial(BCI): 最小CURRENT FACT収集にA2_WRITER Approved Model(Luna)を転用")
        with cl.logging_context(theme_id, "bci_current_fact_collection"):
            bci_result = generate_bci_current_fact_candidates(client, model, JUDGE_REASONING_EFFORT)
        save_json(f"{out_dir}/research/bci_current_fact_candidates.json", bci_result)
        layer1_ledger_text = build_ledger_text_from_bci_candidates(bci_result["parsed"])
        ledger_context_text = layer1_ledger_text
        budget_guard("after_bci_research", args.budget_jpy)

    parsed_candidates, selected, table = stage_provocation(
        client, theme_id, out_dir, theme_cfg, ledger_context_text, args.budget_jpy)

    writer_out = stage_writer(
        client, theme_id, out_dir, theme_cfg, selected, ledger_context_text, args.improvement, args.budget_jpy)

    spark_verdict = stage_spark_gate(
        client, theme_id, out_dir, selected["core_provocation"], writer_out["layers"]["reader_text"],
        args.budget_jpy)

    if spark_verdict["verdict"] == "FAIL":
        cause = spark6.classify_failure_cause(spark_verdict)
        save_json(f"{out_dir}/a2/spark_gate_failure_cause.json", cause)
        print(f"[{theme_id}] Story Spark Gate FAIL. 原因分類={cause['category']}({cause['reason']})。"
              "他QA(Fact Safety)は実行せず停止する。最小改善Trial(--variant 06b)の判断へ回す。")
        build_comparison_md(out_dir, theme_cfg["theme_label_en"], selected["core_provocation"],
                             writer_out["layers"]["reader_text"], writer_out["word_count"], spark_verdict)
        build_index_html(out_dir, theme_cfg["theme_label_en"], spark_verdict, None,
                          writer_out["layers"]["reader_text"])
        final_cost = compute_cost_jpy_for_log(log_path)
        save_json(f"{out_dir}/cost_summary.json", final_cost)
        print(f"[{theme_id}] STOP: Story Spark Gate FAIL. cost={final_cost}")
        return

    safety_result = stage_safety(
        client, theme_id, out_dir, theme_cfg, writer_out["layers"], layer1_ledger_text, args.budget_jpy)

    build_comparison_md(out_dir, theme_cfg["theme_label_en"], selected["core_provocation"],
                         writer_out["layers"]["reader_text"], writer_out["word_count"], spark_verdict)
    build_index_html(out_dir, theme_cfg["theme_label_en"], spark_verdict, safety_result,
                      writer_out["layers"]["reader_text"])

    final_cost = compute_cost_jpy_for_log(log_path)
    save_json(f"{out_dir}/cost_summary.json", final_cost)
    print(f"[{theme_id}] DONE. spark_gate={spark_verdict['verdict']} "
          f"safety_overall_pass={safety_result['overall_pass']} cost={final_cost}")


if __name__ == "__main__":
    main()
