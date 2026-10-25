# Trial-06 オフライン分析(API 0)。PREREGISTERED_CRITERIA_06.md の許容集合(§2)・合格条件(§3)を機械的に当てはめる。
# 許容集合は Step A'' 実行前に登録した値。実行結果を見て変更しない(変更時は「事後変更」と明記し、合否は事前登録版を使う)。
#   py analyze_06.py          -> analysis_06.json
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_trial_06 as t6
import run_trial_04 as t4
BASE = t6.BASE

# 許容集合: 作品 -> 種別 -> 段落ごとの目印語句(本文から逐語。選定文がこの語句を含めば一致)。
CORE = {
    "open_window": {"P21": "Across the quiet garden came a young voice:"},
    "ig_nobel": {"P4": "what you got was a map of molecules", "P5": "more than three times as much energy as the same weight of milk",
                 "P8": "What’s more interesting is", "P9": "there should be a sign"},
    "gift": {"P4": "handed down from his grandfather to his father", "P22": "Inside were the tortoise-shell combs",
             "P30": "sat two foolish young people whose love made them the wisest"},
    "paw": {"P24": "Then came a soft knock."},
    "tth": {"P8": "From the bed came a small groan of terror.", "P15": "At four in the morning came a knock."},
    "promise": {},
}
EITHER = {
    "open_window": {"P29": "Inventing convincing stories at a moment’s notice was Vera’s speciality."},
    "ig_nobel": {"P2": "research on nutrient-rich crystals that had been published earlier", "P3": "protein crystals containing nutrients from the gut of the unborn young",
                 "P11": "Rather than seeing this as a possible breakfast for people"},
    "gift": {"P12": "Nothing showy, nothing unnecessary.", "P29": "Each had sold their greatest treasure to buy the other a gift."},
    "paw": {"P2": "a retired sergeant-major home from India", "P8": "Enough to pay off the house!", "P18": "Wish him alive again!",
            "P19": "I’m afraid of what might come back.", "P22": "I wish Herbert alive again.", "P32": "The street lamp opposite shone on a quiet, deserted road."},
    "tth": {"P2": "that pale blue eye, covered by a thin film like a vulture’s, made his blood turn cold",
            "P4": "Always closed.", "P5": "He hated the eye, not the man.", "P10": "Wide open.",
            "P11": "Then he heard it: a low, quick beating, like a watch wrapped in cotton.",
            "P11b": "Faster it beat, and louder.", "P17": "Calm and confident, he sat directly above the hidden body."},
    "promise": {"P23": "Twenty years can change a man, but not the shape of his nose."},
}
def _match(rec, table):
    """選定記録が表(段落: 目印語句)のいずれかに一致するか。戻り値=一致した表のキー or None。"""
    for k, key in table.items():
        if k.rstrip("b") == rec["para"] and t4._qn(key) in t4._qn(rec["sentence"]): return k
    return None
def kind_of(w, rec):
    if _match(rec, CORE[w]): return "core"
    if _match(rec, EITHER[w]): return "either"
    return "outside"

def load(w):
    out = []
    for i in range(1, t6.NSAMP + 1):
        p = os.path.join(BASE, f"OUTPUT_06_{w}_r{i}_STEPA_DEV.json")
        out.append(json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None)
    return out
def recs(feats, sel): return [t6.sel_record(f) for f in sel(feats)]

def analyze():
    out = {}
    for w in t6.WORKS6:
        S = load(w); r = dict(samples=[], present=sum(1 for j in S if j), parse_errors=sum(1 for j in S if j and j.get("parse_error")))
        for i, j in enumerate(S, 1):
            if not j: r["samples"].append(dict(run=f"r{i}", missing=True)); continue
            F = j["features"]
            main = recs(F, t6.select_main)
            def tag(rs): return [dict(r_, kind=kind_of(w, r_)) for r_ in rs]
            samp = dict(run=f"r{i}", main=tag(main), orig=tag(recs(F, t6.select_cmp_orig)), nosame=tag(recs(F, t6.select_cmp_nosame)),
                        n_features=len(F), n_eligible_main=sum(1 for f in F if t6.eligible_main(f)), n_resolve_fail=sum(1 for f in F if not f.get("resolve_ok")),
                        n_replaced_by_body=sum(1 for f in F if f.get("sentence_replaced_by_body")), uncovered=j.get("uncovered_paras"),
                        basic_true=sum(1 for f in F if t6._as_bool(f.get("basic_only", True))),
                        material_missing_eligible=sum(1 for f in F if t6.base_ok(f) and not t6.materials_ok(f)),
                        cost=j["usage"]["cost_jpy_at_160"], sec=j["usage"]["elapsed_sec"], status=j["usage"].get("status"),
                        # 登録済み文の分類コード(標本間の安定の記録)
                        registered_classes={k: [t6._cls(f) for f in F if f.get("resolve_ok") and f["para"] == k.rstrip("b") and t4._qn(key) in t4._qn(f["sentence"])]
                                            for k, key in {**CORE[w], **EITHER[w]}.items()},
                        mid_cond_rejected=[dict(para=f["para"], cls=t6._cls(f), target=f.get("misread_target"), quote=f.get("misread_quote"), q_in=f.get("misread_quote_in_sentence"))
                                           for f in F if t6.base_ok(f) and t6.materials_ok(f) and not t6.eligible_main(f)])
            samp["main_selection_details"] = [dict(para=f["para"], cls=t6._cls(f), construct=f.get("construct_ja"), points=f.get("points_ja"), sentence=f["sentence"], misread=f.get("misread_ja"))
                                              for f in t6.select_main(F)]
            r["samples"].append(samp)
        ok = [s for s in r["samples"] if not s.get("missing")]
        r["n"] = len(ok)
        r["zero_samples"] = [s["run"] for s in ok if not s["main"]]
        r["outside"] = {s["run"]: [m["para"] + ":" + m["sentence"][:50] for m in s["main"] if m["kind"] == "outside"] for s in ok}
        r["strict_core_all"] = all(all(m["kind"] == "core" for m in s["main"]) for s in ok)
        has_core = bool(CORE[w])
        pass_sel = all(all(m["kind"] != "outside" for m in s["main"]) for s in ok)
        r["rule_pass"] = pass_sel and (not has_core or not r["zero_samples"]) and r["n"] == t6.NSAMP and r["parse_errors"] == 0
        r["requirement"] = "難所のある作品: 全標本で選定⊆許容集合・0件標本なし(基礎のみ選定0はSonnet目視)" if has_core else "平易な作品: 許容集合外を選ばない(0件可)"
        r["cmp_rule_summary"] = {k: dict(outside=sum(1 for s in ok for m in s[k] if m["kind"] == "outside"), zero=sum(1 for s in ok if not s[k]))
                                 for k in ("orig", "nosame")}
        r["cost"] = round(sum(s["cost"] for s in ok), 4)
        out[w] = r
    out["_all_pass"] = all(out[w]["rule_pass"] for w in t6.WORKS6)
    json.dump(out, open(os.path.join(BASE, "analysis_06.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return out

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        # 許容集合の目印語句が本文に逐語で存在する(事前登録の書き写し誤りの検出)
        for w in t6.WORKS6:
            body = " ".join(t6.work_data6(w)["body"])
            for tab in (CORE[w], EITHER[w]):
                for k, key in tab.items(): assert t4._qn(key) in t4._qn(body), (w, k, key)
        # 一致判定
        assert kind_of("tth", dict(para="P15", sentence="At four in the morning came a knock.")) == "core"
        assert kind_of("tth", dict(para="P11", sentence="Faster it beat, and louder.")) == "either"
        assert kind_of("tth", dict(para="P19", sentence="Still the beating grew louder.")) == "outside"
        assert kind_of("promise", dict(para="P23", sentence="Twenty years can change a man, but not the shape of his nose.")) == "either"
        assert kind_of("promise", dict(para="P28", sentence="I recognized your face as the man wanted in Chicago.")) == "outside"
        print("analyze_06 selftest OK"); sys.exit(0)
    o = analyze()
    for w in t6.WORKS6:
        r = o[w]; print("==", w, NAME := t6.NAME_JA[w], "n", r["n"], "pass", r["rule_pass"], "zero", r["zero_samples"], "outside", r["outside"], "strict_core", r["strict_core_all"])
        for s in r["samples"]:
            if s.get("missing"): print("  ", s["run"], "MISSING"); continue
            print("  ", s["run"], "main", [(m["para"], m["feature_class"], m["kind"]) for m in s["main"]], "orig", [(m["para"], m["feature_class"], m["kind"]) for m in s["orig"]],
                  "elig", s["n_eligible_main"], "feat", s["n_features"], "cost", s["cost"])
        print("   cmp", r["cmp_rule_summary"], "cost", r["cost"])
    print("ALL_PASS", o["_all_pass"])
