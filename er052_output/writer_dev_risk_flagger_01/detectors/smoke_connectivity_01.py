# -*- coding: utf-8 -*-
"""疎通確認(各モデル1回・最小入力)。実費をcost_ledger.jsonlへ記録。委任_01B。"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import flagger_lib as L

# 1モデルあたりの出力上限(推論込み)を小さく固定し、最悪費用を抑える
CAP = {"gpt-6.1-sol": 300, "gpt-6-astra": 200, "deepseek-v4-pro": 300}
out = []
for model in ("gpt-6.1-sol", "gpt-6-astra", "deepseek-v4-pro"):
    prices = L.load_prices(model)
    if not prices:
        out.append(dict(model=model, ok=False, error="単価未登録")); continue
    rec = dict(model=model)
    try:
        client = L.client_for(L.MODELS[model])
        text, usage, rid, mid = L.call_model(client, model, "Reply with the JSON object {\"ok\": true} only.", "ping",
                                             max_out=CAP[model], effort="low")
        c = L.cost_yen(prices, usage["input_tokens"] or 0, usage["output_tokens"] or 0, usage.get("cached_tokens") or 0)
        L.ledger_append(dict(purpose="connectivity", model=model, cost_jpy=c, usage=usage, response_id=rid))
        rec.update(ok=True, text=text[:80], usage=usage, model_id=mid, cost_jpy=c)
    except Exception as e:  # noqa: BLE001
        rec.update(ok=False, error=(type(e).__name__ + ": " + str(e))[:300].replace(os.environ.get("OPENAI_API_KEY", "\0"), "***"))
    out.append(rec)
print(json.dumps(out, ensure_ascii=False, indent=1))
print("total_jpy=", sum(r.get("cost_jpy") or 0 for r in out))
