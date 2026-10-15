# -*- coding: utf-8 -*-
"""daily_dev_cost_01.py: 当日(JST)の開発費を、費用ログとREPORT_LEDGERの両方から集計する(read-only、API 0)。

管理ID: PM-AUTONOMOUS-OPERATING-MODEL-ROLLOUT-01 Day3 Phase2 委任_F1 (W9b、U5書 3-3)。
- `**/raw_usage_log.jsonl`・`**/cost_log*.jsonl`のtimestamp(UTC)をJST日付へ変換して絞り込む。
- 換算: cost_usdがあれば採用、なければtoken x pricing_snapshot.json、USD_JPY=160。web_search=件数x単価/1000。
  azure=audio秒/3600 x audio_hour単価。単価未登録は0円にせずunpricedとして列挙する。
- ledger当日行の「費用JPY<数>」を合計し、採用値=max(ログ,ledger)。
- 既存runner(46コピーのcompute_cost_jpy_so_far等)はimportしない。ログ・ledgerを書き換えない。
- 自動停止・実行時ガードは作らない(日次1,000円は7-9。到達で自動STOPしない)。
実行: python docs/pm/tools/daily_dev_cost_01.py --date 2026-10-15 --repo-root . --ledger docs/pm/REPORT_LEDGER.md --json-out <path>
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import sys

USD_JPY = 160.0
JST = datetime.timezone(datetime.timedelta(hours=9))
PRICING_REL = "er005_output/cost_baseline_01/pricing_snapshot.json"
SKIP_DIRS = {".git", ".venv", "node_modules", "__pycache__"}


def load_prices(repo_root):
    path = os.path.join(repo_root, PRICING_REL)
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)["prices"]
    except (OSError, ValueError, KeyError):
        return []


def find_price(prices, provider, model, meter, tier="Standard"):
    """見つからなければNone(0円にしない)。"""
    for p in prices:
        if (p.get("provider") == provider and p.get("model") == model and p.get("meter") == meter
                and p.get("tier", "Standard") == tier):
            return p["price"]
    return None


def to_jst_date(ts):
    try:
        d = datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=datetime.timezone.utc)
    return d.astimezone(JST).date().isoformat()


def price_record(rec, prices):
    """(usd, None) または (None, unpriced理由)。"""
    if rec.get("cost_usd") is not None:
        return float(rec["cost_usd"]), None
    provider = rec.get("provider")
    model = rec.get("model_id") or rec.get("model")
    in_tok = rec.get("input_tokens") or 0
    out_tok = rec.get("output_tokens") or 0
    usd = 0.0
    if provider in ("gemini", "gemini_batch", "openai", "openai_asr", "deepseek"):
        base = "gemini" if provider.startswith("gemini") else provider
        tier = "Batch" if provider == "gemini_batch" else "Standard"
        pi = find_price(prices, base, model, "input_tokens", tier)
        po = find_price(prices, base, model, "output_tokens", tier)
        if (in_tok and pi is None) or (out_tok and po is None):
            return None, "%s/%s" % (provider, model)
        usd += in_tok * (pi or 0) / 1e6 + out_tok * (po or 0) / 1e6
        ws = rec.get("web_search_call_count") or 0
        if ws:
            pw = next((p["price"] for p in prices if p.get("provider") == "openai"
                       and p.get("meter") == "web_search_call"), None)
            if pw is None:
                return None, "%s/web_search_call" % provider
            usd += ws * pw / 1000
        return usd, None
    if provider == "azure":
        dur = rec.get("audio_duration_submitted_seconds") or 0.0
        pa = find_price(prices, "azure", "real-time transcription (S0/S1 standard tier)", "audio_hour")
        if dur and pa is None:
            return None, "azure/audio_hour"
        return dur / 3600.0 * (pa or 0), None
    return None, "%s/%s" % (provider, model)


def iter_log_files(repo_root):
    for dirpath, dirnames, filenames in os.walk(repo_root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if fn == "raw_usage_log.jsonl" or (fn.startswith("cost_log") and fn.endswith(".jsonl")):
                yield os.path.join(dirpath, fn)


def aggregate_logs(repo_root, date, prices):
    total_usd = 0.0
    by_provider, by_dir, unpriced = {}, {}, {}
    files = records = 0
    for path in iter_log_files(repo_root):
        files += 1
        try:
            with open(path, encoding="utf-8") as f:
                lines = f.readlines()
        except OSError:
            continue
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            if not isinstance(rec, dict) or to_jst_date(rec.get("timestamp")) != date:
                continue
            records += 1
            usd, why = price_record(rec, prices)
            if usd is None:
                unpriced[why] = unpriced.get(why, 0) + 1
                continue
            total_usd += usd
            pv = rec.get("provider")
            by_provider[pv] = by_provider.get(pv, 0.0) + usd * USD_JPY
            dname = os.path.relpath(os.path.dirname(path), repo_root).replace("\\", "/")
            by_dir[dname] = by_dir.get(dname, 0.0) + usd * USD_JPY
    return {
        "total_jpy": round(total_usd * USD_JPY, 2),
        "by_provider_jpy": {k: round(v, 2) for k, v in by_provider.items()},
        "top_run_dirs_jpy": sorted(((k, round(v, 2)) for k, v in by_dir.items()), key=lambda x: -x[1])[:10],
        "records": records, "files_scanned": files, "unpriced": unpriced,
    }


_COST = re.compile(r"費用\s*JPY\s*([0-9]+(?:\.[0-9]+)?)")


def aggregate_ledger(ledger_path, date):
    total, rows = 0.0, 0
    try:
        with open(ledger_path, encoding="utf-8") as f:
            for line in f:
                if date in line:
                    m = _COST.search(line)
                    if m:
                        total += float(m.group(1))
                        rows += 1
    except OSError:
        return {"total_jpy": None, "rows": 0, "error": "ledger not readable"}
    return {"total_jpy": round(total, 2), "rows": rows}


def run(date, repo_root, ledger, json_out=None):
    prices = load_prices(repo_root)
    logs = aggregate_logs(repo_root, date, prices)
    led = aggregate_ledger(ledger, date)
    adopted = max(logs["total_jpy"], led["total_jpy"] or 0.0)
    result = {
        "date_jst": date, "log": logs, "ledger": led, "adopted_jpy": adopted,
        "adopted_rule": "max(log, ledger)",
        "uncaptured_kinds": ["run dir外・ログ外課金", "Batch未完了", "単価未登録(unpriced)", "推定値(ledger側)",
                             "Claude Code自体の利用料(別項目)"],
        "assumption": "input_tokensはcachedを含めた全入力として標準単価で換算(cached割引は考慮しない=やや過大側)",
    }
    if json_out:
        os.makedirs(os.path.dirname(os.path.abspath(json_out)), exist_ok=True)
        with open(json_out, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    return result


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=datetime.datetime.now(JST).date().isoformat())
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--ledger", default="docs/pm/REPORT_LEDGER.md")
    ap.add_argument("--json-out")
    a = ap.parse_args(argv)
    print(json.dumps(run(a.date, a.repo_root, a.ledger, a.json_out), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
