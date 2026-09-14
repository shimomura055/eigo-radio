# ============================================================
# er014_output/four_type_observation_01/aggregate_usage.py
# 管理ID: EDITORIAL-4TYPE-NEW-ARTICLE-PRODUCTION-OBSERVATION-01
#
# 目的: 各記事タイプrunディレクトリのraw_usage_log.jsonl(er005_cost_
# logger.py実測)を集計し、observation.jsonを出力する(4記事共通で
# 再利用可能な引数化スクリプト)。Production/Trialコードは一切変更・
# 実行しない。読み取り専用の集計のみ。
#
# 費用/カテゴリ分けの根拠: 既存Cost Loggerは呼び出し単位でtheme/stageを
# 記録するが、Writer本体・Point Role Planning・Evidence Compression・
# Point Value QA・Fact Checker・Ledger Deviation Checkのように、単一の
# stageタグ(例: "writer_a2")の中に複数の異なるAPI呼び出し種別が混在する
# (Production側で細分化タグ付けされていない)。本スクリプトは、各工程が
# 自分の呼び出し結果をaudit/配下のJSONへresponse_idごと保存している
# 事実を利用し、raw_usage_log.jsonlの各レコードのresponse_idを
# audit/*.json内のresponse_idと突き合わせることで、Writer/QA/
# rewrite-regenerationをカテゴリ分けする(response_id完全一致による
# 決定的な対応付けであり、順序やヒューリスティックな推測ではない)。
# 対応が見つからないレコードはcategory="uncategorized"として集計に
# 残し、正直に報告する(隠さない)。
# ============================================================
from __future__ import annotations

import argparse
import glob
import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PRICING_PATH = "er005_output/cost_baseline_01/pricing_snapshot.json"
USD_JPY = 160.0

# ファイル名(basename、拡張子込み、globパターン)→カテゴリの対応表。
# 4記事(News/Trend/Discovery/Voices)で共通して使われるProduction
# audit出力ファイル名パターンを列挙。未知のファイルは無視する
# (response_idが無い、またはこの表に無いファイルは単に集計対象に
# 加わらないだけで、rawログ自体は総額計算に含まれる)。
CATEGORY_FILE_PATTERNS = [
    ("research/fact_ledger_draft.json", "research_ledger"),
    ("research/fact_ledger_verification.json", "research_ledger"),
    ("*/audit/point_role_planning_initial.json", "writer"),
    ("*/audit/point_role_planning_retry*.json", "writer"),
    ("*/audit/writer_attempts.json", "writer"),
    ("*/audit/evidence_compression_editor_raw.json", "writer"),
    ("*/audit/point_value_qa_attempt*.json", "qa"),
    ("*/audit/fact_check_attempts.json", "qa"),
    ("*/audit/deviation_full_record.json", "qa"),
    ("*/audit/local_rewrite_results.json", "rewrite_regeneration"),
    ("*/audit/local_rewrite_cycles.json", "rewrite_regeneration"),
]


def _find_ids(obj, acc: list) -> None:
    if isinstance(obj, dict):
        rid = obj.get("response_id")
        if isinstance(rid, str):
            acc.append(rid)
        for v in obj.values():
            _find_ids(v, acc)
    elif isinstance(obj, list):
        for v in obj:
            _find_ids(v, acc)


def build_response_id_category_map(run_dir: str) -> dict:
    mapping = {}
    for pattern, category in CATEGORY_FILE_PATTERNS:
        for path in glob.glob(os.path.join(run_dir, pattern)):
            try:
                with open(path, encoding="utf-8") as f:
                    data = json.load(f)
            except (OSError, json.JSONDecodeError):
                continue
            ids: list = []
            _find_ids(data, ids)
            for rid in ids:
                mapping[rid] = category
    return mapping


def _load_pricing():
    with open(PRICING_PATH, encoding="utf-8") as f:
        return json.load(f)["prices"]


def _price(pricing, provider, model, meter, tier="Standard"):
    return next(p["price"] for p in pricing if p["provider"] == provider and p["model"] == model
                and p["meter"] == meter and p.get("tier", "Standard") == tier)


def _call_cost_usd(pricing, rec: dict) -> float:
    provider, model = rec.get("provider"), rec.get("model_id")
    if provider != "openai":
        return 0.0
    it, ot = rec.get("input_tokens") or 0, rec.get("output_tokens") or 0
    ct = rec.get("cached_input_tokens") or 0
    billable_in = max(it - ct, 0)
    cost = ((billable_in / 1e6) * _price(pricing, "openai", model, "input_tokens")
            + (ct / 1e6) * _price(pricing, "openai", model, "cached_input_tokens")
            + (ot / 1e6) * _price(pricing, "openai", model, "output_tokens"))
    web_search_calls = rec.get("web_search_call_count") or 0
    cost += (web_search_calls / 1000) * _price(pricing, "openai", "N/A (tool, all models)", "web_search_call")
    return cost


def load_records(run_dir: str) -> list:
    log_path = os.path.join(run_dir, "raw_usage_log.jsonl")
    recs = []
    if not os.path.exists(log_path):
        return recs
    with open(log_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                recs.append(json.loads(line))
    return recs


def load_result_meta(run_dir: str) -> dict:
    for fname in ("cost_summary.json", "run_result.json"):
        path = os.path.join(run_dir, fname)
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                return json.load(f)
    return {}


def derive_retry_from_stage_trace(stage_trace_path: str) -> dict:
    """audit/stage_trace.json(er003_discovery_focus_staged_production_01の
    実行トレース、フェーズごとのdictのlist)からretry回数を直接読む補助
    処理(EDITORIAL-4TYPE-NEW-ARTICLE-PRODUCTION-OBSERVATION-01委任文で
    許可された集計ツールの新規オプション。Production/Trialコードは
    無変更、読み取り専用)。

    Discovery S2は`run_result.json`(driver保存)のフィールド名が
    `stage2_3_retry_attempts`/`stage1_regen_attempts`であり、News/Trend用に
    設計された既存の`point_overlap_article_retry_attempts`検出ロジックでは
    ネスト構造・フィールド名の違いから正しく検出できない(Trend記事で
    判明した限界と同種の問題)。本関数はstage_trace.json自体を直接読み、
    フェーズ名から機械的にretry回数を数える(推測ではなく列挙)。
    """
    with open(stage_trace_path, encoding="utf-8") as f:
        trace = json.load(f)
    stage1_phases = [e for e in trace if e.get("phase") in ("stage1", "stage1_escalated")]
    stage1_regen_attempts = max([e.get("attempt", 0) for e in stage1_phases], default=0)
    stage1_escalated_occurred = any(e.get("phase") == "stage1_escalated" for e in trace)
    stage2_3_phases = [e for e in trace if e.get("phase") == "stage2_3"]
    stage2_3_retry_attempts = max([e.get("retry_attempt", 0) or 0 for e in stage2_3_phases], default=0)
    final_fact_checker_fail_occurred = any(
        e.get("phase") == "final_fact_checker" and e.get("verdict") == "FAIL" for e in trace)
    final_ledger_blocking_occurred = any(
        e.get("phase") == "final_ledger" and e.get("blocking") for e in trace)
    retry_occurred = bool(stage1_regen_attempts) or bool(stage2_3_retry_attempts) \
        or stage1_escalated_occurred or final_fact_checker_fail_occurred
    return {
        "stage_trace_path": stage_trace_path,
        "n_trace_entries": len(trace),
        "stage1_regen_attempts": stage1_regen_attempts,
        "stage1_escalated_occurred": stage1_escalated_occurred,
        "stage2_3_retry_attempts": stage2_3_retry_attempts,
        "final_fact_checker_fail_occurred": final_fact_checker_fail_occurred,
        "final_ledger_blocking_occurred": final_ledger_blocking_occurred,
        "retry_occurred": retry_occurred,
    }


def aggregate(run_dir: str, stage_trace_path: str | None = None) -> dict:
    pricing = _load_pricing()
    recs = load_records(run_dir)
    id_category = build_response_id_category_map(run_dir)

    def categorize(rec: dict) -> str:
        if rec.get("stage") in ("researcher", "verification"):
            return "research_ledger"
        rid = rec.get("response_id")
        return id_category.get(rid, "uncategorized")

    per_call = []
    for rec in recs:
        if rec.get("success") is False:
            continue
        cost_usd = _call_cost_usd(pricing, rec)
        per_call.append({
            "category": categorize(rec), "provider": rec.get("provider"), "model_id": rec.get("model_id"),
            "stage": rec.get("stage"), "response_id": rec.get("response_id"),
            "input_tokens": rec.get("input_tokens") or 0, "output_tokens": rec.get("output_tokens") or 0,
            "cached_input_tokens": rec.get("cached_input_tokens") or 0,
            "total_tokens": rec.get("total_tokens") or 0,
            "web_search_call_count": rec.get("web_search_call_count") or 0,
            "cost_usd": cost_usd, "cost_jpy": cost_usd * USD_JPY,
        })

    failed_calls = [rec for rec in recs if rec.get("success") is False]

    cost_breakdown = {}
    for c in per_call:
        b = cost_breakdown.setdefault(c["category"], {"calls": 0, "input_tokens": 0, "output_tokens": 0,
                                                        "cached_input_tokens": 0, "total_tokens": 0,
                                                        "cost_jpy": 0.0})
        b["calls"] += 1
        b["input_tokens"] += c["input_tokens"]
        b["output_tokens"] += c["output_tokens"]
        b["cached_input_tokens"] += c["cached_input_tokens"]
        b["total_tokens"] += c["total_tokens"]
        b["cost_jpy"] += c["cost_jpy"]
    for b in cost_breakdown.values():
        b["cost_jpy"] = round(b["cost_jpy"], 2)

    by_provider_model = {}
    for c in per_call:
        key = (c["provider"], c["model_id"])
        b = by_provider_model.setdefault(key, {"calls": 0, "input_tokens": 0, "output_tokens": 0,
                                                "cached_input_tokens": 0, "total_tokens": 0, "cost_jpy": 0.0})
        b["calls"] += 1
        b["input_tokens"] += c["input_tokens"]
        b["output_tokens"] += c["output_tokens"]
        b["cached_input_tokens"] += c["cached_input_tokens"]
        b["total_tokens"] += c["total_tokens"]
        b["cost_jpy"] += c["cost_jpy"]
    provider_model_usage = [
        {"provider": p, "model_id": m, **{k: (round(v, 2) if k == "cost_jpy" else v) for k, v in b.items()}}
        for (p, m), b in by_provider_model.items()
    ]

    total_cost_jpy = round(sum(c["cost_jpy"] for c in per_call), 2)
    total_calls = len(per_call)
    total_input = sum(c["input_tokens"] for c in per_call)
    total_output = sum(c["output_tokens"] for c in per_call)
    total_cached = sum(c["cached_input_tokens"] for c in per_call)
    total_tokens = sum(c["total_tokens"] for c in per_call)

    # retry分離: point_overlap_article_retry_attempts(run_result.json)と
    # local_rewrite件数から、retry追加分/retryなし部分を分ける。0件の場合は
    # 全額retryなし部分となる(本Observationタスクの実測ではretry=0)。
    result_meta = load_result_meta(run_dir)
    run_result_path = None
    for cand in [os.path.join(run_dir, "run_result.json")] + glob.glob(os.path.join(run_dir, "*/run_result.json")):
        if os.path.exists(cand):
            run_result_path = cand
            break
    article_retry_attempts = None
    if run_result_path and os.path.exists(run_result_path):
        with open(run_result_path, encoding="utf-8") as f:
            article_run_result = json.load(f)
        article_retry_attempts = article_run_result.get("point_overlap_article_retry_attempts")

    retry_occurred = bool(article_retry_attempts) or cost_breakdown.get("rewrite_regeneration", {}).get("calls", 0) > 0

    stage_trace_summary = None
    if stage_trace_path:
        stage_trace_summary = derive_retry_from_stage_trace(stage_trace_path)
        # stage_trace.json由来の判定の方が、Discovery S2のようにフィールド名/
        # ネスト構造がNews/Trend既定ロジックと異なる記事タイプでは正確なため、
        # 与えられた場合はこちらを優先する(既定ロジックの値は
        # article_point_overlap_retry_attempts_legacy_detectionとして残す)。
        retry_occurred = stage_trace_summary["retry_occurred"]

    observation = {
        "run_dir": run_dir,
        "status": result_meta.get("status"),
        "topic": result_meta.get("topic"),
        "level": result_meta.get("level"),
        "started_at": result_meta.get("started_at"),
        "finished_at": result_meta.get("finished_at"),
        "budget_jpy": result_meta.get("budget_jpy"),
        "api_calls_total": total_calls,
        "api_calls_failed": len(failed_calls),
        "input_tokens_total": total_input,
        "output_tokens_total": total_output,
        "cached_input_tokens_total": total_cached,
        "total_tokens_total": total_tokens,
        "cost_jpy_total": total_cost_jpy,
        "cost_breakdown_jpy": {k: v["cost_jpy"] for k, v in cost_breakdown.items()},
        "cost_breakdown_detail": cost_breakdown,
        "provider_model_usage": provider_model_usage,
        "article_point_overlap_retry_attempts": article_retry_attempts,
        "stage_trace_summary": stage_trace_summary,
        "retry_occurred": retry_occurred,
        "retry_occurred_source": "stage_trace" if stage_trace_summary else "run_result_legacy_detection",
        "retry_extra_cost_jpy": 0.0 if not retry_occurred else None,
        "no_retry_cost_jpy": total_cost_jpy if not retry_occurred else None,
        "note_on_categorization": (
            "cost_breakdown_jpyのwriter/qa/rewrite_regenerationは、各audit "
            "JSONファイルに保存されたresponse_idとraw_usage_log.jsonlの "
            "response_idを完全一致で突き合わせて分類した(推測ではない)。"
            "対応が見つからなかった呼び出しは'uncategorized'に計上する。"
            "retry_extra_cost_jpy/no_retry_cost_jpyは、記事全体retry回数"
            "(point_overlap_article_retry_attempts)とlocal_rewrite件数が"
            "共に0の場合のみ機械的に分離できる(0の場合は全額no_retry扱い)。"
            "1以上の場合は本スクリプトはNoneを返すため、手動確認が必要。"
        ),
    }
    return observation


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--stage-trace", default=None,
                     help="audit/stage_trace.json(Discovery S2等のstaged production関数の実行トレース)への"
                          "パス。指定した場合、retry_occurredの判定をこのファイルの直接読み取りに"
                          "切り替える(EDITORIAL-4TYPE-NEW-ARTICLE-PRODUCTION-OBSERVATION-01委任文で"
                          "許可された新規オプション、任意)。")
    args = ap.parse_args()
    obs = aggregate(args.run_dir, stage_trace_path=args.stage_trace)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(obs, f, ensure_ascii=False, indent=2, default=str)
    print(f"observation.json書き出し完了: {args.out}")
    print(f"status={obs['status']} cost_jpy_total={obs['cost_jpy_total']} "
          f"breakdown={obs['cost_breakdown_jpy']} calls={obs['api_calls_total']}")


if __name__ == "__main__":
    main()
