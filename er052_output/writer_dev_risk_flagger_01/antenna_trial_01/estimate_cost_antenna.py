# -*- coding: utf-8 -*-
"""Phase1 費用見積(API非呼び出し)。入力token=FIX02実測(同一セル・Antenna1相当)+プロンプト差分の推定。出力tokenは3シナリオ(推測)。
単価=pricing_snapshot.json登録値(gpt-6.1-sol Standard)、USD/JPY=160。"""
import json, os, sys, re
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "er052_output", "writer_dev_risk_flagger_01", "detectors")); sys.path.insert(0, HERE)
import flagger_lib as L, antenna_prompts as A
pr = L.load_prices("gpt-6.1-sol"); assert pr == (2.0, 0.1, 10.0), pr
led = [json.loads(x) for x in open(os.path.join(REPO, "er052_output/writer_r0_model_impact_trial_01/fix02/cost_ledger_fix02.jsonl"), encoding="utf-8") if x.strip()]
cells = [r for r in led if r["source"] != "prev_r0"]
assert len(cells) == 9
base_in = {(r["theme"], r["source"]): r["usage"]["input_tokens"] for r in cells}
base_out = {(r["theme"], r["source"]): r["usage"]["output_tokens"] for r in cells}
s1 = L.estimate_tokens(A.antenna_system(1))
res = {}
# 出力tokenの1セル平均(推測): 低/中/高。根拠: D2rank実測(3Flag+mismatch_terms、推論込み)=約500-750tok => 約150-200tok/Flag + 推論増
OUT = {"low": [60, 250, 600, 1000, 1500, 2100], "mid": [60, 400, 900, 1600, 2400, 3300], "high": [100, 700, 1500, 2600, 3800, 5200]}
tot = {}
for sc, outs in OUT.items():
    t = 0.0; per = []
    for k in range(1, 7):
        d = L.estimate_tokens(A.antenna_system(k)) - s1
        c_in = sum(L.cost_yen(pr, base_in[c] + d, 0) for c in base_in)
        c_out = sum(L.cost_yen(pr, 0, outs[k - 1]) for c in base_in)
        per.append(dict(level=k, delta_in_tok_per_call=d, input_jpy=round(c_in, 2), output_jpy=round(c_out, 2), total_jpy=round(c_in + c_out, 2)))
        t += c_in + c_out
    tot[sc] = dict(total_jpy=round(t, 2), per_level=per)
a1_actual = sum(r["cost_jpy"] for r in cells)
print(json.dumps(dict(fix02_9cells_actual_jpy=round(a1_actual, 2), prompt_chars={k: len(A.antenna_system(k)) for k in range(1, 7)}, scenarios=tot,
                      out_tokens_per_cell_assumed=OUT), ensure_ascii=False, indent=1))
