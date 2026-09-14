# ============================================================
# er014_output/four_type_observation_01/news/run_news_b1b.py
# 管理ID: EDITORIAL-4TYPE-FOLLOWUP-01-NEWS-B1-ADDITION
#
# 目的: 既存A2 driver(run_news_a2.py)と同一テーマ「AI regulation vs AI
# race」について、既存作成済みのVerified Fact Ledger(research/配下)を
# 再利用し、Research/Verificationを再実行せずにB1B(label="B1B")を
# Production関数 er003_v1_n3_01_articles_generate.run_one_pattern() で
# そのまま追加生成する(monkeypatch・再実装なし、editorial_mode=None相当
# [Focus Module/Point Role hintなし]のNews既定)。run_news_a2.pyからの
# 差分は「Research/Verification部分を削除しdiskの既存Ledgerを読むだけ」
# 「label/instruction/out_dirをB1B用に変更」の2点のみ。
#
# 出力先: er014_output/four_type_observation_01/news/
#   b1b/                       (run_one_pattern()がaudit/等一式を出力)
#   reader_facing_article_b1b.txt
#   run_result_b1b.json
#   raw_usage_log_b1b.jsonl    (A2のraw_usage_log.jsonlとは別ファイル、
#                                混在させない)
#   cost_summary_b1b.json
#
# 費用上限: BUDGET_JPY(50円)。run_one_pattern()自体は分割実行できない
# ため事前ゲートは無い(Ledger再利用のみで事前コストは¥0)。生成後に
# BUDGET_JPYを超過した場合は結果へ記録するのみ(生成済み記事は破棄しない、
# Fact Safety上の問題ではないため)。
# ============================================================
from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone

sys.path.insert(0, os.getcwd())

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import er003_v1_en_direct_ab_01_generate as ab01
import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_articles_generate as prod_gen
import er005_cost_logger as cl

THEME_ID = "news_ai_regulation_vs_ai_race_b1b"
BASE_DIR = "er014_output/four_type_observation_01/news"
RESEARCH_DIR = f"{BASE_DIR}/research"
ARTICLE_OUT_DIR = f"{BASE_DIR}/b1b"
LOG_PATH = f"{BASE_DIR}/raw_usage_log_b1b.jsonl"

TOPIC_ID = "ai_regulation_vs_ai_race"
LEVEL = "b1b"
BUDGET_JPY = 50.0

# run_news_a2.pyと同一文(Ledgerは既に確定済みのためTOPIC_ENの差し替えは
# しない。同一Ledger+同一topicでA2/B1を対にするのが本タスクの目的)。
TOPIC_EN = (
    "Current news topic: the tension between AI regulation and the AI race. "
    "On one side, governments, regulators, and international bodies are pushing "
    "new AI safety rules, oversight requirements, and governance frameworks. "
    "On the other side, major AI companies and competing nations continue to "
    "race intensely to build and deploy more powerful AI systems faster than "
    "rivals. Aim: cover this tension between AI safety/regulation efforts and "
    "the competitive AI race as a current-events news story, using only facts "
    "confirmed by web search (no invented details, no facts supplied from the "
    "assistant's own prior knowledge)."
)

PRICING_PATH = "er005_output/cost_baseline_01/pricing_snapshot.json"
USD_JPY = 160.0


def _load_pricing():
    with open(PRICING_PATH, encoding="utf-8") as f:
        return json.load(f)["prices"]


PRICING = _load_pricing()


def _price(provider, model, meter, tier="Standard"):
    return next(p["price"] for p in PRICING if p["provider"] == provider and p["model"] == model
                and p["meter"] == meter and p.get("tier", "Standard") == tier)


def _call_cost_usd(rec: dict) -> float:
    provider, model = rec.get("provider"), rec.get("model_id")
    if provider != "openai":
        return 0.0
    it, ot = rec.get("input_tokens") or 0, rec.get("output_tokens") or 0
    ct = rec.get("cached_input_tokens") or 0
    billable_in = max(it - ct, 0)
    in_price = _price("openai", model, "input_tokens")
    cached_price = _price("openai", model, "cached_input_tokens")
    out_price = _price("openai", model, "output_tokens")
    cost = (billable_in / 1e6) * in_price + (ct / 1e6) * cached_price + (ot / 1e6) * out_price
    web_search_calls = rec.get("web_search_call_count") or 0
    web_search_price = _price("openai", "N/A (tool, all models)", "web_search_call")
    cost += (web_search_calls / 1000) * web_search_price
    return cost


def cost_so_far_jpy() -> float:
    if not os.path.exists(LOG_PATH):
        return 0.0
    total_usd = 0.0
    with open(LOG_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if rec.get("success") is False:
                continue
            total_usd += _call_cost_usd(rec)
    return total_usd * USD_JPY


def load_existing_ledger() -> tuple[str, dict]:
    """Research/Verificationを再実行せず、既存のA2 driverが作成した
    research/配下の成果物をそのまま読み込む(Ledgerの新規作成・改変なし)。
    存在しない場合はSTOPする(Fact Safety: 未検証Ledgerで記事を作らない)。"""
    structured_path = f"{RESEARCH_DIR}/verified_fact_ledger_structured.json"
    ledger_txt_path = f"{RESEARCH_DIR}/verified_fact_ledger.txt"
    if not (os.path.exists(structured_path) and os.path.exists(ledger_txt_path)):
        raise SystemExit(f"[{THEME_ID}] STOP: 既存Ledgerが見つかりません"
                          f"({structured_path} / {ledger_txt_path})。Research再実行は本タスクの禁止事項です。")
    with open(structured_path, encoding="utf-8") as f:
        structured = json.load(f)
    with open(ledger_txt_path, encoding="utf-8") as f:
        verified_ledger_text = f.read()
    print(f"[{THEME_ID}] 既存Ledger再利用(API call再実行なし)。counts={structured['counts']}")
    return verified_ledger_text, structured["counts"]


def main():
    os.makedirs(ARTICLE_OUT_DIR, exist_ok=True)
    cl.install(LOG_PATH)
    started_at = datetime.now(timezone.utc).isoformat()

    client = vfl01.get_client()
    verified_ledger_text, counts = load_existing_ledger()

    master_full_text = ab01.load_master_full_text()
    common_block = prod_gen.build_common_block(master_full_text, TOPIC_EN, verified_ledger_text)
    prompt = prod_gen.build_prompt(common_block, prod_gen.B1_B_DIRECT_INSTRUCTION)

    print(f"[{THEME_ID}] run_one_pattern(B1B)開始...")
    t0 = time.time()
    with cl.logging_context(THEME_ID, "writer_b1b"):
        gen_result = prod_gen.run_one_pattern(
            client, THEME_ID, "B1B", prompt, verified_ledger_text, TOPIC_EN, ARTICLE_OUT_DIR)
    elapsed = round(time.time() - t0, 2)
    print(f"[{THEME_ID}] run_one_pattern(B1B)完了: status={gen_result.get('status')} elapsed={elapsed}s")

    finished_at = datetime.now(timezone.utc).isoformat()
    cost_final = cost_so_far_jpy()

    if gen_result.get("article_text"):
        with open(f"{BASE_DIR}/reader_facing_article_b1b.txt", "w", encoding="utf-8") as f:
            f.write(gen_result["article_text"])

    with open(f"{BASE_DIR}/run_result_b1b.json", "w", encoding="utf-8") as f:
        json.dump({k: v for k, v in gen_result.items() if k != "article_text"},
                   f, ensure_ascii=False, indent=2, default=str)

    result = {
        "status": gen_result.get("status"), "topic": TOPIC_EN, "topic_id": TOPIC_ID, "level": LEVEL,
        "counts": counts, "elapsed_seconds": elapsed, "cost_jpy_final": cost_final,
        "started_at": started_at, "finished_at": finished_at,
        "budget_jpy": BUDGET_JPY, "budget_exceeded": cost_final > BUDGET_JPY,
    }
    with open(f"{BASE_DIR}/cost_summary_b1b.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
    print(f"[{THEME_ID}] 完了: status={result['status']} 費用実測(累計)=¥{cost_final:.2f} "
          f"(budget=¥{BUDGET_JPY:.2f}, exceeded={result['budget_exceeded']})")
    return result


if __name__ == "__main__":
    main()
    sys.exit(0)
