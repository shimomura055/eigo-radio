# ============================================================
# er013_family_c_future_trial_07_run.py
# 管理ID: EDITORIAL-FUTURE-FAMILY-C-PROVOCATION-SCALE-COMPARISON-TRIAL-07
# ============================================================
# 目的: Core Provocationのスケール/レンズ比較Trial driver。
# flow: (BCIのみ)最小CURRENT FACT収集 -> スケール/レンズ別候補生成
#       -> 相対比較・強制ランキング -> 代表案(A/B/C各1+D/E最大1)を
#       それぞれWriter(v7契約、CURRENT FACTデフォルト0件) -> Story Spark
#       Gate(補助評価、記録のみ) -> Fact Safety 3層(safety_06再利用)
#       -> Framing QA v2決定的スキャン(参考記録のみ、任意)-> 比較HTML/MD
#
# 既存er013_family_c_future_*_01〜06.py・er013_output/family_c_future_
# trial_01〜06*/は一切変更しない(read-only importでの再利用のみ)。
# SSOT・Git操作もこのファイルからは行わない。**Production採用・配線では
# ない**(Gate 1材料までのTrial、最大Status: VALIDATED)。
#
# 実行方法(root直下から):
#   .venv/Scripts/python.exe er013_family_c_future_trial_07_run.py \
#       --theme home_robots --level a2 --budget-jpy 60
#   .venv/Scripts/python.exe er013_family_c_future_trial_07_run.py \
#       --theme bci --level a2 --budget-jpy 40
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
import er013_family_c_future_provocation_07 as prov7
import er013_family_c_future_qa_01 as fcq1
import er013_family_c_future_qa_02 as fcq2
import er013_family_c_future_safety_06 as safety6
import er013_family_c_future_spark_gate_06 as spark6
import er013_family_c_future_trial_06_run as trial06  # read-onlyでの再利用(テーマ設定・BCI収集・費用集計)
import er013_family_c_future_writer_07 as writer7
import er003_v1_en_direct_vfl_01_generate as vfl01

# ------------------------------------------------------------
# 費用実測(Trial-06のcompute_cost_jpy_for_logをそのまま再利用)
# ------------------------------------------------------------
FAMILY_C_RESIDUAL_HARD_CAP_JPY = 160.97  # ユーザー指定のFamily C残額ハード上限(委任文記載、変更不可)

MAX_WRITER_MARKER_RETRY = 3
WRITER_REASONING_EFFORT = vfl01.REASONING_EFFORT  # "high"(記事本文の質を優先)
JUDGE_REASONING_EFFORT = "medium"  # 候補生成/ランキング/Spark Gate/Safety軽判定はmediumでコスト抑制

THEME_CONFIG = trial06.THEME_CONFIG  # read-only再利用(home_robots/bciのtheme_label・inspiration_note・ledger_path)


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


def budget_guard(stage_label: str, log_path: str, per_run_budget_jpy: float) -> dict:
    """総額ガード: trial_07全体(home_robots+bci合算、単一log_pathへappendされる)
    がハード上限を超えたらここでSTOPする(各API呼び出し直後、次のより高コストな
    段へ進む**前**に毎回チェックする)。"""
    total = trial06.compute_cost_jpy_for_log(log_path)
    print(f"[budget_guard][{stage_label}] Trial-07合算={total['total_jpy']} JPY "
          f"(ハード上限{FAMILY_C_RESIDUAL_HARD_CAP_JPY}, 本run目安{per_run_budget_jpy})")
    if total["total_jpy"] > FAMILY_C_RESIDUAL_HARD_CAP_JPY:
        raise RuntimeError(
            f"[budget_guard][{stage_label}] Trial-07合算 {total['total_jpy']} JPY が"
            f"Family C残額ハード上限{FAMILY_C_RESIDUAL_HARD_CAP_JPY} JPYを超過しました。"
            "STOP(以降のAPI呼び出しは行わない)。")
    if total["total_jpy"] > per_run_budget_jpy:
        print(f"[budget_guard][{stage_label}] 警告: 本run向け目安予算{per_run_budget_jpy} JPYを超過"
              "(ハード上限内のため続行、目安超過として記録)。")
    return total


# ------------------------------------------------------------
# Stage 1: スケール/レンズ別候補生成 + 相対比較・強制ランキング
# ------------------------------------------------------------
def stage_provocation_and_ranking(client, theme_id: str, prov_dir: str, theme_cfg: dict,
                                   ledger_context_text: str, log_path: str, per_run_budget_jpy: float) -> tuple:
    prompt = prov7.build_candidate_prompt(
        theme_cfg["theme_label_en"], theme_cfg["inspiration_note"], ledger_context_text)
    save_text(f"{prov_dir}/candidate_prompt.txt", prompt)
    model = routing.require_model_or_override(
        "A2_WRITER", routing.WRITER_MODEL,
        override_reason="Trial-07: スケール/レンズ別Core Provocation候補生成にA2_WRITER Approved "
                         "Model(Luna)を転用(新規process未定義、コスト影響なし、DEV/Trial限定)")
    with cl.logging_context(theme_id, "provocation_candidates"):
        cand_result = prov7.generate_candidates(client, model, JUDGE_REASONING_EFFORT, prompt)
    parsed = cand_result["parsed"]
    candidates = parsed["candidates"]
    reference_table = prov7.build_score_table_reference(parsed)

    ranking_prompt = prov7.build_ranking_prompt(theme_cfg["theme_label_en"], candidates)
    save_text(f"{prov_dir}/ranking_prompt.txt", ranking_prompt)
    with cl.logging_context(theme_id, "provocation_ranking"):
        rank_result = prov7.generate_ranking(client, model, JUDGE_REASONING_EFFORT, ranking_prompt)
    ranking_parsed = rank_result["parsed"]
    prov7.validate_ranking(ranking_parsed, [c["id"] for c in candidates])

    selection = prov7.compute_representative_selection(candidates, ranking_parsed)

    save_json(f"{prov_dir}/candidates.json", {
        "parsed": parsed, "reference_score_table": reference_table,
        "model": cand_result["model"], "response_id": cand_result["response_id"],
    })
    save_json(f"{prov_dir}/ranking.json", {
        "parsed": ranking_parsed, "selection": selection,
        "model": rank_result["model"], "response_id": rank_result["response_id"],
    })
    ranking_md = prov7.build_ranking_md(theme_cfg["theme_label_en"], candidates, ranking_parsed, selection)
    save_text(f"{prov_dir}/ranking.md", ranking_md)

    budget_guard("after_provocation_and_ranking", log_path, per_run_budget_jpy)
    return candidates, selection


# ------------------------------------------------------------
# Stage 2: Writer(v7契約、マーカー技術的retryのみ)
# ------------------------------------------------------------
def generate_writer_with_marker_retry(client, theme_id: str, article_dir: str, prompt: str) -> tuple:
    model = routing.require_model("A2_WRITER", routing.WRITER_MODEL)
    attempts = []
    for attempt in range(1, MAX_WRITER_MARKER_RETRY + 1):
        with cl.logging_context(theme_id, f"writer_attempt{attempt}"):
            result = writer7.generate_family_c_article_v7(
                client, model=model, reasoning_effort=WRITER_REASONING_EFFORT, prompt=prompt)
        text_no_meta = fcq2.strip_meta_blocks(result["raw_text"])
        imagined_check = fcq1.validate_markers_balanced(text_no_meta)
        fact_check_balance = fcq2.validate_fact_markers_balanced(text_no_meta)
        balanced = imagined_check["balanced"] and fact_check_balance["balanced"]
        attempts.append({"attempt": attempt, "imagined_check": imagined_check,
                          "fact_check_balance": fact_check_balance, "response_id": result["response_id"]})
        if balanced:
            save_json(f"{article_dir}/writer_attempts.json", attempts)
            return result["raw_text"], attempts
        print(f"[{theme_id}] Writer attempt {attempt}: マーカー不整合(technical retry)"
              f" imagined={imagined_check} fact={fact_check_balance}")
    save_json(f"{article_dir}/writer_attempts.json", attempts)
    raise RuntimeError(f"マーカー整合の取れたWriter出力が{MAX_WRITER_MARKER_RETRY}回の技術的retryでも"
                        "得られませんでした。STOP(NG_REVIEW_REQUIRED)。")


def stage_writer(client, theme_id: str, article_dir: str, theme_cfg: dict, candidate: dict,
                  ledger_context_text: str, log_path: str, per_run_budget_jpy: float) -> dict:
    prompt = writer7.build_family_c_writer_v7_prompt(
        core_provocation=candidate["core_provocation"], premise=candidate["premise"],
        theme_label=theme_cfg["theme_label_en"], ledger_excerpt=ledger_context_text)
    save_text(f"{article_dir}/writer_prompt.txt", prompt)
    article_text, attempts = generate_writer_with_marker_retry(client, theme_id, article_dir, prompt)
    save_text(f"{article_dir}/writer_raw_article.txt", article_text)
    layers = safety6.extract_layers(article_text)
    save_text(f"{article_dir}/reader_facing_article.txt", layers["reader_text"])
    word_count = len(layers["reader_text"].split())
    fact_count = len(layers["fact_blocks"])
    save_json(f"{article_dir}/word_count.json", {
        "word_count": word_count, "target": writer7.WORD_TARGET,
        "acceptable_range": list(writer7.WORD_ACCEPTABLE_RANGE),
        "within_acceptable_range": writer7.WORD_ACCEPTABLE_RANGE[0] <= word_count <= writer7.WORD_ACCEPTABLE_RANGE[1],
        "current_fact_marker_count": fact_count,
    })
    budget_guard("after_writer", log_path, per_run_budget_jpy)
    return {"article_text": article_text, "layers": layers, "word_count": word_count, "fact_count": fact_count}


# ------------------------------------------------------------
# Stage 3: Story Spark Gate(補助評価、記録のみ。PASS/FAILで採用・破棄しない)
# ------------------------------------------------------------
def stage_spark_gate(client, theme_id: str, article_dir: str, core_provocation: str, reader_text: str,
                      log_path: str, per_run_budget_jpy: float) -> dict:
    prompt = spark6.build_spark_gate_prompt(core_provocation, reader_text)
    save_text(f"{article_dir}/spark_gate_prompt.txt", prompt)
    model = routing.require_model_or_override(
        "A2_WRITER", routing.WRITER_MODEL,
        override_reason="Trial-07: Story Spark Gate(補助評価)判定にA2_WRITER Approved Model(Luna)を転用"
                         "(新規process未定義、コスト影響なし、DEV/Trial限定)")
    with cl.logging_context(theme_id, "spark_gate"):
        result = spark6.run_story_spark_gate(client, model, JUDGE_REASONING_EFFORT, prompt)
    verdict = spark6.compute_verdict(result["parsed"])
    save_json(f"{article_dir}/spark_gate_result.json", {
        "parsed": result["parsed"], "verdict": verdict, "model": result["model"], "response_id": result["response_id"],
        "note": "補助評価のみ。PASS/FAILで採用・破棄は決定しない(委任文の方針)。",
    })
    budget_guard("after_spark_gate", log_path, per_run_budget_jpy)
    return verdict


# ------------------------------------------------------------
# Stage 4: Fact Safety(3レイヤー、safety_06をそのまま再利用。全代表案で実行)
# ------------------------------------------------------------
def stage_safety(client, theme_id: str, article_dir: str, theme_cfg: dict, layers: dict,
                  layer1_ledger_text: str, log_path: str, per_run_budget_jpy: float) -> dict:
    judge_model = routing.require_model_or_override(
        "A2_WRITER", routing.WRITER_MODEL,
        override_reason="Trial-07: Plausibility Bridge/Imagined Future軽判定にA2_WRITER Approved "
                         "Model(Luna)を転用(新規process未定義、コスト影響なし、DEV/Trial限定)")
    result = safety6.run_safety_boundary_check(
        client, theme_id, theme_cfg["topic_ja_placeholder"], judge_model, JUDGE_REASONING_EFFORT,
        layers, layer1_ledger_text)
    if not layers["fact_blocks"]:
        result["current_fact_layer_skip_note"] = (
            "CURRENT FACT文0件(v7のデフォルト方針)。Fact Checker A'はプレースホルダ"
            "テキストに対して形式的に実行されたのみで、実質的な検証対象は存在しない。"
            "Layer1 Ledger Deviation Checkerはfact_blocks空のため明示的にskipされている"
            "(current_fact_layer.layer1_deviation_check.skipped参照)。")
    save_json(f"{article_dir}/safety_result.json", result)
    budget_guard("after_safety", log_path, per_run_budget_jpy)
    return result


# ------------------------------------------------------------
# Stage 5: Framing QA v2 決定的スキャン(参考記録のみ、任意。qa_02.scan_editorial_gate再利用)
# ------------------------------------------------------------
def stage_framing_qa_v2_reference(article_dir: str, reader_text: str, fact_blocks: list) -> dict:
    """後段の決定的スキャンとして利用可能かの設計確認を兼ねる。今回の採用・破棄は
    左右しない(参考記録のみ、委任文の方針)。"""
    result = fcq2.scan_editorial_gate(reader_text, fact_blocks, banned_product_names=[])
    save_json(f"{article_dir}/framing_qa_v2_reference.json", {
        "result": result,
        "note": "参考記録のみ。今回の採用・破棄はこの結果で左右しない(委任文の方針)。",
    })
    return result


# ------------------------------------------------------------
# 代表案1件をフルパイプラインで処理
# ------------------------------------------------------------
def process_one_article(client, theme_id: str, article_dir: str, theme_cfg: dict, candidate: dict,
                         ledger_context_text: str, layer1_ledger_text: str, log_path: str,
                         per_run_budget_jpy: float) -> dict:
    writer_out = stage_writer(client, theme_id, article_dir, theme_cfg, candidate,
                               ledger_context_text, log_path, per_run_budget_jpy)
    spark_verdict = stage_spark_gate(client, theme_id, article_dir, candidate["core_provocation"],
                                      writer_out["layers"]["reader_text"], log_path, per_run_budget_jpy)
    safety_result = stage_safety(client, theme_id, article_dir, theme_cfg, writer_out["layers"],
                                  layer1_ledger_text, log_path, per_run_budget_jpy)
    framing_qa_v2 = stage_framing_qa_v2_reference(
        article_dir, writer_out["layers"]["reader_text"], writer_out["layers"]["fact_blocks"])
    return {
        "candidate": candidate, "writer_out": writer_out, "spark_verdict": spark_verdict,
        "safety_result": safety_result, "framing_qa_v2_reference": framing_qa_v2,
    }


SCALE_SLUG = {"A_intimate": "intimate", "B_societal": "societal", "C_radical": "radical"}


def run_theme(client, theme_id_for_log: str, out_root: str, theme_cfg: dict, ledger_context_text: str,
              layer1_ledger_text: str, log_path: str, per_run_budget_jpy: float) -> dict:
    prov_dir = f"{out_root}/provocation"
    candidates, selection = stage_provocation_and_ranking(
        client, theme_id_for_log, prov_dir, theme_cfg, ledger_context_text, log_path, per_run_budget_jpy)
    candidates_by_id = {c["id"]: c for c in candidates}

    articles = {}
    for scale, cid in selection["top_pick_by_scale"].items():
        slug = SCALE_SLUG[scale]
        article_dir = f"{out_root}/{slug}"
        candidate = candidates_by_id[cid]
        articles[slug] = process_one_article(
            client, f"{theme_id_for_log}_{slug}", article_dir, theme_cfg, candidate,
            ledger_context_text, layer1_ledger_text, log_path, per_run_budget_jpy)

    if selection["extra_lens_included"]:
        cid = selection["extra_lens_id"]
        candidate = candidates_by_id[cid]
        article_dir = f"{out_root}/lens_extra"
        articles["lens_extra"] = process_one_article(
            client, f"{theme_id_for_log}_lens_extra", article_dir, theme_cfg, candidate,
            ledger_context_text, layer1_ledger_text, log_path, per_run_budget_jpy)

    return {"candidates": candidates, "selection": selection, "articles": articles}


# ------------------------------------------------------------
# 比較Artifact
# ------------------------------------------------------------
V6_REFERENCE_PATHS = {
    "06 (home_robots)": "er013_output/family_c_future_trial_06/a2/reader_facing_article.txt",
    "06b (home_robots improved)": "er013_output/family_c_future_trial_06b/a2/reader_facing_article.txt",
    "06_bmi (bci)": "er013_output/family_c_future_trial_06_bmi/a2/reader_facing_article.txt",
}

SEVEN_HUMAN_AXES = [
    "Future Leap", "面白さ", "わくわく・ドキドキ", "想像したことのない未来感",
    "Storyとしての自然さ", "読後に問いが残るか", "現在の延長説明に落ちていないか",
]


def build_comparison_md(out_dir: str, results_by_theme: dict) -> None:
    md = ["# Trial-07 -- Core Provocationスケール/レンズ比較\n",
          "Trial専用、Production採用ではない。最大Status: VALIDATED。\n"]
    for theme_id, result in results_by_theme.items():
        md.append(f"\n## {theme_id}\n")
        for slug, art in result["articles"].items():
            c = art["candidate"]
            md.append(f"\n### {slug} -- scale={c['scale']}"
                       f"{' (combined_with=' + c['combined_with'] + ')' if c.get('combined_with') else ''}\n")
            md.append(f"**Core Provocation**: {c['core_provocation']}\n")
            md.append(f"- what_is_the_future: {c['what_is_the_future']}")
            md.append(f"- what_is_interesting: {c['what_is_interesting']}")
            md.append(f"- what_would_surprise_the_reader: {c['what_would_surprise_the_reader']}")
            md.append(f"- what_happens_as_a_story: {c['what_happens_as_a_story']}\n")
            md.append(f"語数: {art['writer_out']['word_count']} / CURRENT FACT件数: {art['writer_out']['fact_count']} / "
                       f"Spark Gate(補助): {art['spark_verdict']['verdict']} / "
                       f"Fact Safety overall_pass: {art['safety_result']['overall_pass']}\n")
            md.append("```\n" + art["writer_out"]["layers"]["reader_text"] + "\n```\n")
    md.append("\n## v6参考記事(比較用、再生成なし)\n")
    for label, path in V6_REFERENCE_PATHS.items():
        if os.path.exists(path):
            md.append(f"\n### {label}\n```\n{load_text(path)}\n```\n")
        else:
            md.append(f"\n### {label}\n(見つかりません: {path})\n")
    save_text(f"{out_dir}/comparison.md", "\n".join(md))


def _html_escape(text: str) -> str:
    return (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def build_index_html(out_dir: str, results_by_theme: dict) -> None:
    parts = ["""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>Family C Trial-07 -- Core Provocation Scale Comparison</title></head>
<body style="font-family: sans-serif; max-width: 960px; margin: 2em auto; line-height: 1.6;">
<h1>Family C Trial-07 -- Core Provocation Scale Comparison</h1>
<p><strong>Status: Trial only, NOT Production-approved (max Status: VALIDATED).</strong></p>
"""]
    for theme_id, result in results_by_theme.items():
        parts.append(f"<h2>{_html_escape(theme_id)}</h2>")
        parts.append("<h3>1. Candidate list (scale/lens, 4 short fields, relative rank, reason)</h3>")
        parts.append("<table border='1' cellpadding='4' style='border-collapse:collapse; font-size:0.9em;'>")
        parts.append("<tr><th>rank</th><th>id</th><th>scale</th><th>combined_with</th>"
                      "<th>core_provocation</th><th>what_is_interesting</th>"
                      "<th>what_would_surprise_the_reader</th><th>reason</th></tr>")
        candidates_by_id = {c["id"]: c for c in result["candidates"]}
        for cid, rank in sorted(result["selection"]["rank_by_id"].items(), key=lambda kv: kv[1]):
            c = candidates_by_id[cid]
            reason = result["selection"]["reason_by_id"][cid]
            parts.append(
                f"<tr><td>{rank}</td><td>{_html_escape(cid)}</td><td>{_html_escape(c['scale'])}</td>"
                f"<td>{_html_escape(c.get('combined_with') or '')}</td>"
                f"<td>{_html_escape(c['core_provocation'])}</td>"
                f"<td>{_html_escape(c['what_is_interesting'])}</td>"
                f"<td>{_html_escape(c['what_would_surprise_the_reader'])}</td>"
                f"<td>{_html_escape(reason)}</td></tr>")
        parts.append("</table>")

        parts.append("<h3>2. Adopted representative candidates and rationale</h3><ul>")
        for scale, cid in result["selection"]["top_pick_by_scale"].items():
            parts.append(f"<li><strong>{_html_escape(scale)}</strong>: {_html_escape(cid)} "
                          f"(rank {result['selection']['rank_by_id'][cid]}) -- "
                          f"{_html_escape(result['selection']['reason_by_id'][cid])}</li>")
        if result["selection"]["extra_lens_included"]:
            cid = result["selection"]["extra_lens_id"]
            parts.append(f"<li><strong>extra lens</strong>: {_html_escape(cid)} -- "
                          f"{_html_escape(result['selection']['extra_lens_recommendation_raw']['reason'])}</li>")
        parts.append("</ul>")

        parts.append("<h3>3-5. Articles side by side (word count / FACT count / Spark Gate / Fact Safety)</h3>")
        for slug, art in result["articles"].items():
            c = art["candidate"]
            parts.append(f"<div style='border:1px solid #ccc; padding:1em; margin-bottom:1em;'>")
            parts.append(f"<h4>{_html_escape(slug)} -- {_html_escape(c['scale'])}</h4>")
            parts.append(f"<p><strong>Core Provocation:</strong> {_html_escape(c['core_provocation'])}</p>")
            parts.append(f"<p>word_count={art['writer_out']['word_count']} | "
                          f"current_fact_markers={art['writer_out']['fact_count']} | "
                          f"spark_gate(aux)={art['spark_verdict']['verdict']} | "
                          f"fact_safety_overall_pass={art['safety_result']['overall_pass']}</p>")
            parts.append(f"<pre style='white-space: pre-wrap;'>{_html_escape(art['writer_out']['layers']['reader_text'])}</pre>")
            parts.append(f"<p><a href='{slug}/reader_facing_article.txt'>reader_facing_article.txt</a> | "
                          f"<a href='{slug}/spark_gate_result.json'>spark_gate_result.json</a> | "
                          f"<a href='{slug}/safety_result.json'>safety_result.json</a></p>")
            parts.append("</div>")

    parts.append("<h3>Reference: v6 articles (06 / 06b / 06_bmi, not regenerated)</h3><ul>")
    for label, path in V6_REFERENCE_PATHS.items():
        if os.path.exists(path):
            parts.append(f"<li><a href='../{path}'>{_html_escape(label)}</a></li>")
    parts.append("</ul>")

    parts.append("<h3>5. Human evaluation checklist (7 axes, per article) -- Sonnet self-score is a separate 'aux' column</h3>")
    parts.append("<table border='1' cellpadding='4' style='border-collapse:collapse;'>")
    parts.append("<tr><th>article</th>" + "".join(f"<th>{_html_escape(a)} (human)</th><th>{_html_escape(a)} (Sonnet aux)</th>"
                                                     for a in SEVEN_HUMAN_AXES) + "</tr>")
    for theme_id, result in results_by_theme.items():
        for slug in result["articles"]:
            parts.append(f"<tr><td>{_html_escape(theme_id)}/{_html_escape(slug)}</td>" +
                          "".join("<td></td><td></td>" for _ in SEVEN_HUMAN_AXES) + "</tr>")
    parts.append("</table>")

    parts.append("<h3>Links</h3><ul>")
    parts.append("<li><a href='comparison.md'>comparison.md (full text of all articles + v6 reference)</a></li>")
    parts.append("<li><a href='cost_summary.json'>cost_summary.json</a></li>")
    parts.append("</ul></body></html>")
    save_text(f"{out_dir}/index.html", "\n".join(parts))


# ------------------------------------------------------------
# main
# ------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--theme", choices=["home_robots", "bci"], required=True)
    parser.add_argument("--level", choices=["a2"], default="a2")
    parser.add_argument("--budget-jpy", type=float, required=True)
    args = parser.parse_args()

    out_root_top = "er013_output/family_c_future_trial_07"
    log_path = f"{out_root_top}/raw_usage_log.jsonl"  # home_robots/bci共有(単一ハード上限を合算判定するため)
    cl.install(log_path)
    theme_cfg = THEME_CONFIG[args.theme]

    budget_guard("start", log_path, args.budget_jpy)

    client = vfl01.get_client()

    theme_id_for_log = f"family_c_future_trial_07_{args.theme}"
    out_root = out_root_top if args.theme == "home_robots" else f"{out_root_top}/bci"

    if theme_cfg["ledger_path"]:
        ledger_context_text = load_text(theme_cfg["ledger_path"])
        layer1_ledger_text = ledger_context_text
    else:
        model = routing.require_model_or_override(
            "A2_WRITER", routing.WRITER_MODEL,
            override_reason="Trial-07(BCI): 最小CURRENT FACT収集にA2_WRITER Approved Model(Luna)を転用"
                             "(trial_06_runの既存関数をそのまま再利用)")
        with cl.logging_context(theme_id_for_log, "bci_current_fact_collection"):
            bci_result = trial06.generate_bci_current_fact_candidates(client, model, JUDGE_REASONING_EFFORT)
        save_json(f"{out_root}/research/bci_current_fact_candidates.json", bci_result)
        layer1_ledger_text = trial06.build_ledger_text_from_bci_candidates(bci_result["parsed"])
        ledger_context_text = layer1_ledger_text
        budget_guard("after_bci_research", log_path, args.budget_jpy)

    result = run_theme(client, theme_id_for_log, out_root, theme_cfg, ledger_context_text,
                        layer1_ledger_text, log_path, args.budget_jpy)

    results_path = f"{out_root}/theme_result_summary.json"
    save_json(results_path, {
        "theme": args.theme,
        "top_pick_by_scale": result["selection"]["top_pick_by_scale"],
        "extra_lens_included": result["selection"]["extra_lens_included"],
        "extra_lens_id": result["selection"]["extra_lens_id"],
        "articles_word_counts": {slug: a["writer_out"]["word_count"] for slug, a in result["articles"].items()},
        "articles_fact_counts": {slug: a["writer_out"]["fact_count"] for slug, a in result["articles"].items()},
        "articles_spark_verdicts": {slug: a["spark_verdict"]["verdict"] for slug, a in result["articles"].items()},
        "articles_safety_overall_pass": {slug: a["safety_result"]["overall_pass"] for slug, a in result["articles"].items()},
    })

    # 比較Artifactはhome_robots実行時点で作れる分のみ作る(bci追加実行時は再生成して両方載せる)
    results_by_theme = {args.theme: result}
    home_robots_summary_path = f"{out_root_top}/theme_result_summary.json"
    bci_summary_path = f"{out_root_top}/bci/theme_result_summary.json"
    if args.theme == "bci" and os.path.exists(home_robots_summary_path):
        print(f"[trial_07] 注記: 比較ArtifactはCLI呼び出し単位のresultのみを対象にする"
              "(home_robots実行時に生成済みのindex.html/comparison.mdへ追記はしない、"
              "別レポートで両方を手動突合する)。")
    build_comparison_md(out_root, results_by_theme)
    build_index_html(out_root, results_by_theme)

    final_cost = trial06.compute_cost_jpy_for_log(log_path)
    save_json(f"{out_root_top}/cost_summary.json", final_cost)
    print(f"[trial_07][{args.theme}] DONE. "
          f"top_pick_by_scale={result['selection']['top_pick_by_scale']} "
          f"extra_lens_included={result['selection']['extra_lens_included']} cost={final_cost}")


if __name__ == "__main__":
    main()
