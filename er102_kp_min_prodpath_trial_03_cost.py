# -*- coding: utf-8 -*-
"""KPMP3 費用集計(API 0)。usage_A/B.jsonl(er005_cost_logger raw)+paid_calls.jsonl(評価) -> cost_summary.json"""
import json, glob, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
O = ROOT / "er102_output" / "kp_min_prodpath_trial_03"
import er009_n1_routing_governance_10_actual_model_cost as pr


def usage_cost(arm):
    t = 0; ti = 0; to = 0; n = 0
    for l in open(O / ("usage_%s.jsonl" % arm), encoding="utf-8"):
        if not l.strip():
            continue
        r = json.loads(l)
        if r["success"]:
            t += pr.cost_jpy_for_call("openai", r["model_id"], r.get("input_tokens"), r.get("cached_input_tokens"), r.get("output_tokens"))
            ti += r.get("input_tokens") or 0; to += r.get("output_tokens") or 0; n += 1
    return round(t, 4), n, ti, to


def main():
    a = usage_cost("A"); b = usage_cost("B")
    ev = [json.loads(l) for l in open(O / "paid_calls.jsonl", encoding="utf-8") if l.strip()]
    evc = round(sum(e["cost_jpy"] for e in ev), 4)
    sel = {}
    for arm in "AB":
        sel[arm] = round(sum(json.load(open(f, encoding="utf-8"))["cost_jpy"] for f in glob.glob(str(O / "runs" / arm / "*" / "key_phrases" / "key_phrases_db_hybrid" / "keywords_runtime_metadata.json"))), 4)
    d = {
        "使用モデル": "gpt-6-luna(選定・canonicalization・gloss整合・Redundancy QA。er006 SUPPORT_MODEL=Production既定) / 評価者 claude-sonnet-5-5(最新世代、前回と同一尺度)",
        "ArmA_全工程費用JPY": a[0], "ArmA_OpenAI呼出数": a[1], "ArmA_input_tokens": a[2], "ArmA_output_tokens": a[3],
        "ArmB_全工程費用JPY": b[0], "ArmB_OpenAI呼出数": b[1], "ArmB_input_tokens": b[2], "ArmB_output_tokens": b[3],
        "ArmA_選定のみJPY_最終attempt": sel["A"], "ArmB_選定のみJPY_最終attempt": sel["B"],
        "評価JPY_Sonnet5_5_24呼出": evc, "Trial合計JPY": round(a[0] + b[0] + evc, 4),
        "per_unit_全工程": {"A": round(a[0] / 14, 4), "B": round(b[0] / 14, 4)},
        "per_unit_選定": {"A": round(sel["A"] / 14, 4), "B": round(sel["B"] / 14, 4)},
        "per_記事セット(2レベル)_全工程_B_minus_A": round((b[0] - a[0]) / 14 * 2, 4),
        "per_記事セット(2レベル)_選定_B_minus_A": round((sel["B"] - sel["A"]) / 14 * 2, 4),
        "注記": "起動順序の事故: 初回起動直後にSTOP確認rc=3(STOP_ALLが一時出現、直後に消滅=他agentのtest由来と推定)を見る前にprocessを起動してしまい、直ちに終了。usage logは0件(応答前)で、課金発生の可能性は最大8呼出(Luna選定1呼出約0.4円、合計約3円以下)で上記費用に含まず。再確認rc=0後に1回のみ再起動。",
        "単価": "er009 PRICING(Luna)/ er098 PRICES(Sonnet 5.5 $2入力/$0.10キャッシュ/$10出力 per 1M、USD_JPY=160)",
    }
    (O / "cost_summary.json").write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(d, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
