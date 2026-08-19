import json

LUNA_INPUT = 0.20 / 1_000_000
LUNA_CACHED = 0.02 / 1_000_000
LUNA_OUTPUT = 1.20 / 1_000_000
LUNA_SEARCH = 10.00 / 1000

GEMINI_INPUT = 0.30 / 1_000_000
GEMINI_OUTPUT = 2.50 / 1_000_000
# Grounding: 5,000 free/month shared pool, then $14/1,000 requests -> marginal $0 this experiment (well under free pool)

rows = [json.loads(l) for l in open("er005_output/e2e_research_ab_01_p1/raw_usage_log.jsonl", encoding="utf-8") if l.strip()]

print(f"{'stage':35s} {'in_tok':>8s} {'out_tok':>8s} {'cached':>7s} {'searches':>9s} {'token_cost':>11s} {'search_cost':>11s} {'total':>10s}")
total_by_model = {}
for r in rows:
    stage = r["stage"]
    is_luna = "luna" in stage
    it, ot, ct = r["input_tokens"], r["output_tokens"], r.get("cached_input_tokens", 0)
    sc = r.get("web_search_call_count", 0)
    if is_luna:
        token_cost = (it - ct) * LUNA_INPUT + ct * LUNA_CACHED + ot * LUNA_OUTPUT
        search_cost = sc * LUNA_SEARCH
    else:
        token_cost = it * GEMINI_INPUT + ot * GEMINI_OUTPUT
        search_cost = 0.0  # within free grounding pool
    total = token_cost + search_cost
    model = "luna" if is_luna else "gemini"
    total_by_model.setdefault(model, {"token": 0.0, "search": 0.0})
    total_by_model[model]["token"] += token_cost
    total_by_model[model]["search"] += search_cost
    print(f"{stage:35s} {it:8d} {ot:8d} {ct:7d} {sc:9d} {token_cost:11.5f} {search_cost:11.5f} {total:10.5f}")

print()
for model, d in total_by_model.items():
    print(f"{model}: token={d['token']:.5f} search={d['search']:.5f} total={d['token']+d['search']:.5f}")
