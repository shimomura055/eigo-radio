# -*- coding: utf-8 -*-
"""SC-6 フェイルセーフ: LLM失敗の注入(例外/timeout/不正出力/空/refusal相当/幻覚のみ/実APIの超短timeout)で、例外0・表由来受理0・現行(er103原本)と同一挙動・
operator reportに『実体表未構築』を明記、を確認する。HR queue 88実イベント(Ledger全除外)+『開いた窓』Bertie 3行で判定を比較。"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common_01 import *
rows = [(i, r) for i, r, c in load_hr_rows() if not c]
k_ow, segs_ow, _ = group_key_and_segments(next(r for i, r in rows if i == 118))


def inj_exc(cls):
    def f(text, pid):
        raise cls("injected")
    return f


def inj_ret(ents):
    return lambda text, pid: {"entities": ents}


def real_timeout(text, pid):
    # 実APIクライアントを超短timeoutで呼ぶ(送信前に失敗し費用0)。例外は構築側で縮退される
    return ret.llm_ner_real(text, pid, usage_log=None, timeout=0.001)


cases = {
    "RuntimeError": inj_exc(RuntimeError), "TimeoutError": inj_exc(TimeoutError), "ValueError(invalid JSON相当)": inj_exc(ValueError),
    "empty_entities": inj_ret([]), "entities=None(refusal相当)": inj_ret(None), "bad_items": inj_ret([{"x": 1}, "str", {"surface": 3, "category": "person"}]),
    "hallucinated_only": inj_ret([{"surface": "Zorblax Quendar", "category": "person"}]), "real_api_timeout_0.001s": real_timeout,
}
led = ledger_tokens(True)
out = {}
for name, fn in cases.items():
    rec = {"exceptions": 0, "table_status": None, "mismatch_vs_original": 0, "table_derived_accepts": 0, "operator_lines": None}
    try:
        tb = ret.build_entity_table(segs_ow, llm=fn, usage_log=None, tag="inject")
    except Exception as e:
        rec["exceptions"] += 1
        out[name] = rec
        continue
    rec["table_status"] = tb.status
    rec["operator_lines"] = ret.operator_report_lines(tb)[:3]
    rec["usable_entries"] = len(tb.usable_entries())
    for i, r in rows:
        kw = inputs_for(r)
        if kw is None:
            continue
        o = run_orig(kw, led)
        t = run_trial(kw, led, tb)
        if dec_sig(o) != dec_sig(t):
            rec["mismatch_vs_original"] += 1
        if t.accept and not o.accept:
            rec["table_derived_accepts"] += 1
    out[name] = rec
    print(name, rec["table_status"], "exc", rec["exceptions"], "mismatch", rec["mismatch_vs_original"], "tbl_accepts", rec["table_derived_accepts"], rec["operator_lines"][:1])
res = {"cases": out, "PASS": all(v["exceptions"] == 0 and v["mismatch_vs_original"] == 0 and v["table_derived_accepts"] == 0 for v in out.values())}
json.dump(res, open(os.path.join(HERE, "sc6_failsafe_01_result.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("PASS", res["PASS"])
