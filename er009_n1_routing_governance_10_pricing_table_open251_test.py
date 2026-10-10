# OPEN-251: er009 PRICING_USD_PER_M がRouting contractのOpenAI model(本表を使う経路)を網羅するか
import json, os, pytest
import er009_n1_routing_governance_10_actual_model_cost as cost
import er006_model_routing_contract_01 as routing

HERE = os.path.dirname(os.path.abspath(__file__))
SNAP = os.path.join(HERE, "er005_output", "cost_baseline_01", "pricing_snapshot.json")

# 本表(cost_jpy_for_call)を呼ぶ経路(KP選定/KP説明等)がSUPPORT/WRITER系で使うmodel。
# gpt-6-astraはW-1 Writer(er053 factlock)専用で別の費用集計経路(pricing_snapshot直接)を使う。
TABLE_PATH_PROCESSES = ["B1_SUPPORT", "A2_SUPPORT", "B1_WRITER", "A2_WRITER", "SUPPORT_FACT_CHECK",
                        "WRITER_FACT_CHECK", "KEY_PHRASE_ADVANCED_EXPLANATION", "EVIDENCE_PACK"]

def _snap(model):
    d = json.load(open(SNAP, encoding="utf-8"))
    out = {}
    for e in d["prices"]:
        if e.get("provider") == "openai" and e.get("model") == model:
            out[e["meter"]] = e["price"]
    return out

def test_table_path_models_all_priced():
    missing = [m for m in {routing.PROCESS_MODEL_MAP[p] for p in TABLE_PATH_PROCESSES}
               if ("openai", m) not in cost.PRICING_USD_PER_M]
    assert missing == []

def test_luna_values_match_snapshot():
    s = _snap("gpt-6-luna")
    assert cost.PRICING_USD_PER_M[("openai", "gpt-6-luna")] == (
        s["input_tokens"], s["cached_input_tokens"], s["output_tokens"])

def test_unknown_still_fail_closed():
    with pytest.raises(cost.UnknownModelPricingError):
        cost.cost_jpy_for_call("openai", "gpt-6.1-sol", 1000, 0, 1000)

def test_luna_cost_computes():
    # 1M in, 1M out -> (0.10+0.50)*160
    assert cost.cost_jpy_for_call("openai", "gpt-6-luna", 1_000_000, 0, 1_000_000) == 96.0
