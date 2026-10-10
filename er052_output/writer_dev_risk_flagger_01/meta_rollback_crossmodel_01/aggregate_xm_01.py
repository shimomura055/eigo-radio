# -*- coding: utf-8 -*-
"""META-ROLLBACK-CROSSMODEL-01 Phase2 集計。事前登録(PREREGISTRATION_01.md 7節)の語基準で機械判定。API呼び出しなし。"""
import json, os, re, sys
sys.dont_write_bytecode = True
H = os.path.dirname(os.path.abspath(__file__))
TARGET_SID = "s23"
TARGET = "The company also restored the human concierge feature to the way it had been before, at least for now."
ORDER = ["luna", "sol", "gemini35fl", "gemini38f", "dsflash", "dsflash_think", "haiku45", "sonnet5"]
# 機械判定語(事前登録7節の方針。判定前に固定): Yes = 台帳側(rollback等) AND 本文側(restore等) AND 明示的な食い違い表現
LEDGER_RE = re.compile(r"ロールバック|rolled back|rollback|撤回|保留|当面|停止|縮小|撤退|中止|取り下げ")
BODY_RE = re.compile(r"restore|復元|元に戻|以前の状態|再開|復活|戻した")
CONTRAST_RE = re.compile(r"逆|反転|ではなく|読め|ように|とありますが|ありますが|に見え|一方")

def classify(flag):
    if flag is None: return "No"
    q = flag["question"]
    if LEDGER_RE.search(q) and BODY_RE.search(q) and CONTRAST_RE.search(q): return "Yes"
    return "Partial"

prev = None
res = {}; total = 0.0
ledger = [json.loads(l) for l in open(os.path.join(H, "cost_ledger_xm_01.jsonl"), encoding="utf-8") if l.strip()]
for k in ORDER:
    m = dict(model_key=k, levels={})
    for lv in (3, 4):
        d = json.load(open(os.path.join(H, "runs", k, "A%d.json" % lv), encoding="utf-8"))
        m["label"] = d["label"]; m["model_id_requested"] = d["model_id_requested"]; m["model_ids_returned"] = d["model_ids_returned"]
        assert d["sentences"][TARGET_SID] == TARGET
        s23 = [f for f in d["flags"] if f["sentence_id"] == TARGET_SID and f["sentence"] == TARGET]
        best = None
        for f in s23:
            c = classify(f)
            if best is None or ["No", "Partial", "Yes"].index(c) > ["No", "Partial", "Yes"].index(best[1]): best = (f, c)
        flag, cls = best if best else (None, "No")
        others = [dict(sentence_id=f["sentence_id"], type=f["type"], confidence=f["confidence"], fact_ids=f["fact_ids"]) for f in d["flags"] if f["sentence_id"] != TARGET_SID]
        u = d["usage"]
        m["levels"]["A%d" % lv] = dict(
            valid_json=d["valid_json"], attempts=d["attempts"], cost_jpy=round(d["cost_jpy"], 4), elapsed_s=d["elapsed_s"],
            s23_flagged=bool(s23), s23_class=cls, s23_flag=flag,
            n_flags=len(d["flags"]), other_flags=others,
            usage=u, thinking_setting=d["thinking_setting"],
            thinking_blocks=[x.get("thinking_blocks") for x in u],
            reasoning_tokens=[x.get("reasoning_tokens") for x in u],
            sonnet_thinking_tokens=[((r.get("body") or {}).get("usage") or {}).get("output_tokens_details", {}).get("thinking_tokens") for r in d["raw_http"]] if d["provider"] == "anthropic" else None,
            finish_reasons=[x.get("finish_reason") or x.get("stop_reason") for x in u],
            checksums=dict(article=d["article_sha256"], ledger=d["ledger_sha256"], system=d["system_prompt_sha256"]))
        total += d["cost_jpy"]
    L3, L4 = m["levels"]["A3"], m["levels"]["A4"]
    m["cost_jpy_2call"] = round(L3["cost_jpy"] + L4["cost_jpy"], 4)
    cl = [L3["s23_class"], L4["s23_class"]]
    m["overall_direction"] = "Yes" if "Yes" in cl else ("Partial" if "Partial" in cl else "No")
    m["closeout"] = dict(Yes="DETECTED", Partial="PARTIALLY_DETECTED", No="NOT_DETECTED")[m["overall_direction"]]
    m["invalid_output_levels"] = [x for x in ("A3", "A4") if not m["levels"][x]["valid_json"]]
    res[k] = m
# 無効出力(validate_flags不合格)内のs23(参考のみ。集計対象外)
for k in ORDER:
    for lv in (3, 4):
        L = res[k]["levels"]["A%d" % lv]
        if not L["valid_json"]:
            d = json.load(open(os.path.join(H, "runs", k, "A%d.json" % lv), encoding="utf-8"))
            info = []
            for i, r in enumerate(d["raw_http"]):
                try:
                    c = json.loads(r["body"]["choices"][0]["message"]["content"] or "")
                    info.append(dict(attempt=i + 1, s23=[dict(type=f["type"], confidence=f["confidence"], question=f["question"]) for f in c.get("flags", []) if f["sentence_id"] == TARGET_SID]))
                except Exception as e:
                    info.append(dict(attempt=i + 1, s23=None, note="JSONとして解釈不能/空(%s)" % type(e).__name__))
            L["invalid_output_reference"] = info
est = json.load(open(os.path.join(H, "estimate_01.json"), encoding="utf-8"))
est_tot = est["total"]
lists = dict(
    A3_detected=[k for k in ORDER if res[k]["levels"]["A3"]["s23_flagged"]],
    A4_detected=[k for k in ORDER if res[k]["levels"]["A4"]["s23_flagged"]],
    both_detected=[k for k in ORDER if res[k]["levels"]["A3"]["s23_flagged"] and res[k]["levels"]["A4"]["s23_flagged"]],
    flagged_without_direction=[k for k in ORDER if res[k]["overall_direction"] == "Partial"],
    not_detected=[k for k in ORDER if res[k]["overall_direction"] == "No"],
    unavailable=[],
    direction_yes=[k for k in ORDER if res[k]["overall_direction"] == "Yes"])
out = dict(task="WRITER-RISK-FLAGGER-META-ROLLBACK-CROSSMODEL-01", target=dict(sid=TARGET_SID, text=TARGET), rule=dict(ledger_re=LEDGER_RE.pattern, body_re=BODY_RE.pattern, contrast_re=CONTRAST_RE.pattern,
           note="Yes=3語群すべて一致 / Partial=s23 Flagありでそれ以外 / No=s23 Flagなし(出力無効含む)。人間確認なし"),
           models=res, lists=lists, cost=dict(actual_total_jpy=round(total, 4), ledger_rows=len(ledger), ledger_sum=round(sum(r["cost_jpy"] for r in ledger), 4), estimate_total=est_tot,
           per_model_estimate={k: est["per_model"][k]["total_2call"] for k in ORDER}))
json.dump(out, open(os.path.join(H, "aggregate_xm_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(dict(lists=lists, cost=out["cost"]["actual_total_jpy"], per=[(k, res[k]["overall_direction"], res[k]["levels"]["A3"]["s23_class"], res[k]["levels"]["A4"]["s23_class"], res[k]["cost_jpy_2call"], res[k]["invalid_output_levels"]) for k in ORDER]), ensure_ascii=False, indent=1))
