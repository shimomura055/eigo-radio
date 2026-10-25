# Trial-07 オフライン分析(API 0)。PREREGISTERED_CRITERIA_07.md の許容集合(§2)・合格条件(§4)を機械的に当てはめる。
# 許容集合はStep A'' 実行前に登録した値(既存6作品はanalyze_06.pyから継承)。実行結果を見て変更しない。
#   py analyze_07.py          -> analysis_07.json
#   py analyze_07.py selftest
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_trial_07 as t7
import run_trial_04 as t4
import analyze_06 as a6
BASE = t7.BASE

CORE = dict(a6.CORE); EITHER = dict(a6.EITHER)
CORE["boredom"] = {"P5": "were more likely to reduce the other person’s reward after watching the stone video than after watching the magician video",
                   "P7": "those who watched the stone video were more likely to reduce another person’s reward than those in the other conditions"}
EITHER["boredom"] = {"P2": "either a five-minute video of a stone, where nothing happened, or a video of a magician",
                     "P8": "Along with “what kind of person someone is,” there’s also “what they can do in that situation.”"}
CORE["melos"] = {}; EITHER["melos"] = {}      # 許容集合=∅(0件が正解)
ZERO_CORRECT = {"melos", "promise"}           # promiseはP23(可)のみ許容(PREREGISTERED_CRITERIA_07 §2)
def _match(rec, table):
    for k, key in table.items():
        if k.rstrip("b") == rec["para"] and t4._qn(key) in t4._qn(rec["sentence"]): return k
    return None
def kind_of(w, rec):
    if _match(rec, CORE[w]): return "core"
    if _match(rec, EITHER[w]): return "either"
    return "outside"
def load(w):
    out = []
    for i in range(1, t7.NSAMP7[w] + 1):
        p = os.path.join(BASE, f"OUTPUT_07_{w}_r{i}_STEPA_DEV.json")
        out.append(json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None)
    return out

def analyze():
    out = {}
    for w in t7.WORKS7:
        S = load(w); r = dict(samples=[], present=sum(1 for j in S if j), parse_errors=sum(1 for j in S if j and j.get("parse_error")))
        for i, j in enumerate(S, 1):
            if not j: r["samples"].append(dict(run=f"r{i}", missing=True)); continue
            F = j["features"]; sel = t7.select_one(F)
            main = [dict(t7.sel_record(f), kind=kind_of(w, t7.sel_record(f))) for f in sel]
            cand = [f for f in F if f.get("resolve_ok")]
            samp = dict(run=f"r{i}", main=main, n_features=len(F), n_eligible=sum(1 for f in F if t7.eligible7(f)),
                        n_resolve_fail=sum(1 for f in F if not f.get("resolve_ok")), resolve_errors=[f.get("resolve_error") for f in F if not f.get("resolve_ok")],
                        n_cross_para=sum(1 for f in F if f.get("cross_para_flag")), cross_para=[dict(para=f["para"], flag=f["cross_para_flag"], raw=f.get("sentence_llm_raw", "")[:90]) for f in F if f.get("cross_para_flag")],
                        n_replaced_by_body=sum(1 for f in F if f.get("sentence_replaced_by_body")), uncovered=j.get("uncovered_paras"),
                        selected_single_span_ok=all(m.get("single_span_ok") for m in main),
                        front_kinds={k: sum(1 for f in F if t7._cls(f) == "FRONT" and str(f.get("front_kind", "")).upper() == k) for k in sorted({str(f.get("front_kind", "")).upper() for f in F if t7._cls(f) == "FRONT"})},
                        front_rejected=[dict(para=f["para"], kind=f.get("front_kind"), sentence=f["sentence"][:70]) for f in F if t7.base_ok(f) and t7._cls(f) == "FRONT" and not t7.front_ok(f)],
                        tv_low_rejected=dict(strong=sum(1 for f in F if t7.base_ok(f) and t7.materials_ok(f) and t7._cls(f) in t7.STRONG and not t7.teaching_ok(f)),
                                             mid=sum(1 for f in F if t7.base_ok(f) and t7.materials_ok(f) and t7._cls(f) in t7.MID and not t7.teaching_ok(f))),
                        ell_no_omitted=sum(1 for f in F if t7.base_ok(f) and t7._cls(f) == "ELL" and not str(f.get("omitted_words", "")).strip()),
                        mid_cond_rejected=[dict(para=f["para"], cls=t7._cls(f), target=f.get("misread_target"), quote=f.get("misread_quote"), q_in=f.get("misread_quote_in_sentence"))
                                           for f in F if t7.base_ok(f) and t7.materials_ok(f) and t7.teaching_ok(f) and t7._cls(f) in t7.MID and not t7.mid_cond(f)],
                        eligible_list=[dict(para=f["para"], cls=t7._cls(f), kind=kind_of(w, t7.sel_record(f)), sentence=f["sentence"][:70]) for f in sorted([f for f in F if t7.eligible7(f)], key=t7._order_key)],
                        registered_classes={k: [t7._cls(f) for f in cand if f["para"] == k.rstrip("b") and t4._qn(key) in t4._qn(f["sentence"])] for k, key in {**CORE[w], **EITHER[w]}.items()},
                        cost=j["usage"]["cost_jpy_at_160"], sec=j["usage"]["elapsed_sec"], status=j["usage"].get("status"))
            samp["main_details"] = [dict(para=f["para"], cls=t7._cls(f), front_kind=f.get("front_kind"), construct=f.get("construct_ja"), points=f.get("points_ja"), teaching_value_ja=f.get("teaching_value_ja"),
                                          sentence=f["sentence"], misread=f.get("misread_ja")) for f in sel]
            r["samples"].append(samp)
        ok = [s for s in r["samples"] if not s.get("missing")]
        r["n"] = len(ok); r["expected_n"] = t7.NSAMP7[w]
        r["zero_samples"] = [s["run"] for s in ok if not s["main"]]
        r["outside"] = {s["run"]: [m["para"] + ":" + m["sentence"][:60] for m in s["main"] if m["kind"] == "outside"] for s in ok}
        r["strict_core_all"] = all(all(m["kind"] == "core" for m in s["main"]) for s in ok)
        r["single_span_all"] = all(s["selected_single_span_ok"] for s in ok)
        paras = [tuple(m["para"] for m in s["main"]) for s in ok]
        r["agree_para"] = (max(paras.count(p) for p in set(paras)) / len(paras)) if paras else None      # 同一段落(0件含む)の選定一致率
        has_core = bool(CORE[w])
        pass_sel = all(all(m["kind"] != "outside" for m in s["main"]) for s in ok)
        pass_zero = all(not s["main"] for s in ok) if w == "melos" else True
        r["rule_pass"] = pass_sel and pass_zero and (not has_core or not r["zero_samples"]) and r["n"] == r["expected_n"] and r["parse_errors"] == 0 and r["single_span_all"]
        r["requirement"] = ("難所のある作品: 全標本で選定⊆許容集合・0件標本なし・単一span" if has_core else ("0件が正解(許容集合∅): 選定0" if w == "melos" else "平易(P23のみ可): 許容集合外を選ばない(0件可)"))
        r["cost"] = round(sum(s["cost"] for s in ok), 4)
        out[w] = r
    out["_all_pass"] = all(out[w]["rule_pass"] for w in t7.WORKS7)
    out["_total_cost"] = round(sum(out[w]["cost"] for w in t7.WORKS7), 4)
    json.dump(out, open(os.path.join(BASE, "analysis_07.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return out

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        for w in t7.WORKS7:                                  # 許容集合の目印語句が本文に逐語で存在する(事前登録の書き写し誤りの検出)
            body = " ".join(t7.work_data7(w)["body"])
            for tab in (CORE[w], EITHER[w]):
                for k, key in tab.items(): assert t4._qn(key) in t4._qn(body), (w, k, key)
        assert kind_of("tth", dict(para="P15", sentence="At four in the morning came a knock.")) == "core"
        assert kind_of("boredom", dict(para="P7", sentence="This time, regardless of how strongly participants were inclined to enjoy seeing others suffer, those who watched the stone video were more likely to reduce another person’s reward than those in the other conditions.")) == "core"
        assert kind_of("melos", dict(para="P11", sentence="Melos struck the man holding it with his walking stick and ran uphill, their shouts following him.")) == "outside"
        assert kind_of("promise", dict(para="P23", sentence="Twenty years can change a man, but not the shape of his nose.")) == "either"
        print("analyze_07 selftest OK"); sys.exit(0)
    o = analyze()
    for w in t7.WORKS7:
        r = o[w]; print("==", w, t7.NAME_JA[w], "n", r["n"], "/", r["expected_n"], "pass", r["rule_pass"], "zero", r["zero_samples"], "outside", r["outside"], "strict_core", r["strict_core_all"], "agree", r["agree_para"])
        for s in r["samples"]:
            if s.get("missing"): print("  ", s["run"], "MISSING"); continue
            print("  ", s["run"], "main", [(m["para"], m["feature_class"], m["kind"]) for m in s["main"]], "elig", s["n_eligible"], "feat", s["n_features"], "cross", s["n_cross_para"], "rf", s["n_resolve_fail"], "cost", s["cost"])
    print("ALL_PASS", o["_all_pass"], "TOTAL_COST", o["_total_cost"])
