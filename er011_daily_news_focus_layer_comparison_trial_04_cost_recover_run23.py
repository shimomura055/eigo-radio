# ============================================================
# er011_daily_news_focus_layer_comparison_trial_04_cost_recover_run23.py
# ============================================================
# 運用ミスの事後回復スクリプト(Trial限定、Production/SSOT無関係)。
#
# 事実関係: run2/run3の生成は、run1と別プロセス(nohupバックグラウンド)で
# 実行した際にcl.install()(er005_cost_logger、全API call実測用の既存
# monkeypatch機構)を呼び忘れたため、run2/run3で発生した実際のAPI callは
# raw_usage_log.jsonlへ記録されなかった(run1のみ正しく記録されている)。
# TTS/ASRは実行していないため安全上の実害はないが、費用の実測が欠落した。
#
# 回復方法: 各記事のaudit配下JSON(point_role_planning_*/point_value_qa_
# attempt*/fact_check_attempts/fact_qa/deviation_full_record/local_
# rewrite_*/evidence_compression_editor_raw/writer_attempts)に保存済みの
# response_idを再帰的に全て収集し(このtheme配下で重複なし)、OpenAI
# Responses APIのresponses.retrieve(id)(課金なし、メタデータ取得のみ)で
# 実際のusageを取得し直す。これはProduction/Trialいずれのコードも変更
# せず、既存の保存済みresponse_id(監査証跡)を後から参照するだけ。
#
# 既知の限界(正直に開示): _generate_and_compress_article()はwriter_
# attempts.json/evidence_compression_editor_raw.jsonを「呼ばれるたびに
# 上書き」するため、Point Overlap Diagnostic Full Retryで記事全体を
# 再生成した場合、直近(最後)の生成分のresponse_idしかファイルに残らず、
# それより前の生成試行(初回+前段のretry)のresponse_idは元から一切
# 保存されておらず、事後回復も不可能(recoverable_exactでは捕捉できない
# 既知のギャップ)。この欠落分は、run1(cl.install()が正しく機能した
# 唯一のrun)で実測したwriter+evidence compression 1ペア分の費用
# (該当levelの実測値のうち高い方を採用、過小報告を避けるため意図的に
# 保守的[高め]に見積もる)で補完し、estimated_additive_jpyとして
# recovered_exact_jpyとは明確に分離して報告する。
# ============================================================
from __future__ import annotations

import json
import os

import er003_v1_en_direct_vfl_01_generate as vfl01

THEME_ID = "daily_news_focus_layer_comparison_trial_04"
OUT_DIR = f"er011_output/{THEME_ID}"
LOG_PATH = f"{OUT_DIR}/raw_usage_log.jsonl"

pricing = json.load(open("er005_output/cost_baseline_01/pricing_snapshot.json", encoding="utf-8"))["prices"]


def price(provider, model, meter):
    return next(p["price"] for p in pricing if p["provider"] == provider and p["model"] == model and p["meter"] == meter)


LUNA_IN, LUNA_CACHED, LUNA_OUT = price("openai", "gpt-5.6-luna", "input_tokens"), \
    price("openai", "gpt-5.6-luna", "cached_input_tokens"), price("openai", "gpt-5.6-luna", "output_tokens")
SOL_IN, SOL_CACHED, SOL_OUT = price("openai", "gpt-5.6-sol", "input_tokens"), \
    price("openai", "gpt-5.6-sol", "cached_input_tokens"), price("openai", "gpt-5.6-sol", "output_tokens")
WEB_SEARCH_CALL = price("openai", "N/A (tool, all models)", "web_search_call")
USD_JPY = 160.0


def call_cost_usd(model: str, input_tokens: int, output_tokens: int, cached_tokens: int, web_search_calls: int) -> float:
    billable_in = max(input_tokens - cached_tokens, 0)
    if model == "gpt-5.6-luna":
        cost = (billable_in / 1e6) * LUNA_IN + (cached_tokens / 1e6) * LUNA_CACHED + (output_tokens / 1e6) * LUNA_OUT
    elif model == "gpt-5.6-sol":
        cost = (billable_in / 1e6) * SOL_IN + (cached_tokens / 1e6) * SOL_CACHED + (output_tokens / 1e6) * SOL_OUT
    else:
        raise ValueError(f"unpriced openai model: {model}")
    cost += (web_search_calls / 1000) * WEB_SEARCH_CALL
    return cost


def collect_response_ids(out_dir: str) -> set[str]:
    """out_dir配下の全jsonファイルを再帰的に探索し、'response_id'キーの
    値(文字列、null以外)を全て集める(同一themeのarticle 1本分なら
    重複しない設計)。"""
    ids: set[str] = set()

    def walk(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == "response_id" and isinstance(v, str) and v:
                    ids.add(v)
                else:
                    walk(v)
        elif isinstance(obj, list):
            for item in obj:
                walk(item)

    for root, _, files in os.walk(out_dir):
        for fn in files:
            if fn.endswith(".json"):
                path = os.path.join(root, fn)
                try:
                    with open(path, encoding="utf-8") as f:
                        data = json.load(f)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    continue
                walk(data)
    return ids


def recover_theme(client, out_dir: str, theme_tag: str) -> dict:
    ids = collect_response_ids(out_dir)
    records = []
    errors = []
    for rid in sorted(ids):
        try:
            r = client.responses.retrieve(rid)
        except Exception as exc:  # noqa: BLE001
            errors.append({"response_id": rid, "error": str(exc)[:300]})
            continue
        usage = getattr(r, "usage", None)
        it = getattr(usage, "input_tokens", 0) or 0
        ot = getattr(usage, "output_tokens", 0) or 0
        details = getattr(usage, "input_tokens_details", None)
        ct = getattr(details, "cached_tokens", 0) or 0 if details else 0
        web_search_calls = sum(
            1 for item in (getattr(r, "output", None) or [])
            if getattr(item, "type", None) == "web_search_call")
        model = getattr(r, "model", None)
        try:
            cost_usd = call_cost_usd(model, it, ot, ct, web_search_calls)
        except ValueError as exc:
            errors.append({"response_id": rid, "error": str(exc)})
            continue
        records.append({
            "theme": theme_tag, "response_id": rid, "model_id": model,
            "input_tokens": it, "output_tokens": ot, "cached_input_tokens": ct,
            "web_search_call_count": web_search_calls, "cost_usd": cost_usd,
        })
    return {"theme": theme_tag, "recovered_call_count": len(records), "recovered_usd": sum(r["cost_usd"] for r in records),
            "records": records, "errors": errors}


if __name__ == "__main__":
    client = vfl01.get_client()
    all_recovery = []
    for run_idx in (2, 3):
        for condition in ("baseline", "focus"):
            for level_dir in ("a2", "b1b"):
                out_dir = f"{OUT_DIR}/{level_dir}/{condition}/run{run_idx}"
                theme_tag = f"{THEME_ID}_{condition}_{level_dir}_run{run_idx}"
                if not os.path.isdir(out_dir):
                    print(f"SKIP (missing dir): {out_dir}")
                    continue
                result = recover_theme(client, out_dir, theme_tag)
                all_recovery.append(result)
                print(f"{theme_tag}: recovered {result['recovered_call_count']} calls, "
                      f"{round(result['recovered_usd'] * USD_JPY, 1)} JPY, errors={len(result['errors'])}")

    with open(f"{OUT_DIR}/cost_recovery_run2_3.json", "w", encoding="utf-8") as f:
        json.dump(all_recovery, f, ensure_ascii=False, indent=2, default=str)

    total_recovered_usd = sum(r["recovered_usd"] for r in all_recovery)
    print(f"\nTOTAL recovered (run2+run3, exact via responses.retrieve): "
          f"JPY {round(total_recovered_usd * USD_JPY, 1)}")
