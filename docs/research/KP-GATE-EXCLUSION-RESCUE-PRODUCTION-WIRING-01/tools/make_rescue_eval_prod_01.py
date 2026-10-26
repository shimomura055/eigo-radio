# -*- coding: utf-8 -*-
r"""KPRW1 委任_01: er125(Production module)の11件最終期待結果 + 実データ回帰(既受理itemが救済で不変)を rescue_eval_prod_01.json へ出力する(API 0)。
使い方: .venv\Scripts\python.exe docs/research/KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01/tools/make_rescue_eval_prod_01.py <out.json>"""
import contextlib, json, os, socket, sys
def _b(*a, **k): raise RuntimeError("net blocked")
socket.socket.connect = _b; socket.create_connection = _b
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
sys.path.insert(0, ROOT)
WD = os.path.join(ROOT, "docs", "research", "KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01")
import er003_key_words_canonicalization as kc
import er030_key_phrase_db_hybrid_core_01 as core
import er105_kp_fulltext_selector_01 as ft
import er108_kp_cmu_lexicon_gate_01 as cmu
import er125_kp_rescue_production_01 as r
import er125_kp_rescue_production_test_01 as T

fx = json.load(open(os.path.join(WD, "case_fixtures_01.json"), encoding="utf-8"))
CASE = {c["table_no"]: c for c in fx if c["table_no"]}
LLM_KEY = {2: "study separately", 3: "have our eye on", 4: "rise above the other voices", 5: "hold out one's hands", 6: "ring through",
           8: "redelivery fee", 10: "have a say", 11: "catch their interest"}
rows = []
with T._wired_h1():
    for no in range(1, 12):
        c = CASE[no]; u = T.units_of(c); d = c["display"]
        row = {"no": no, "family": c["family"], "level": c["level"], "display": d}
        reasons = T.sel_reasons(d, u)
        row["selection_reasons_now"] = reasons
        if no == 1:
            row.update(result="NOT_RESCUED(短縮不採用)", route="-", code=None, final=None)
        elif no in (7, 11):
            res = r.rescue_selection_item(d, reasons, u)
            row.update(result="RESCUED", route="選定段(救済フロー)", code=res["selection_rescue"]["code"], final=res["phrase"])
        elif no == 9:
            row.update(result="PASS(通常フロー・慣用句例外)", route="通常(H1: 有限助動詞guard例外)", code=r.R_IDIOM_AUX, final=d, idiom=r.idiom_exception(d))
        elif no == 8:
            o = T.original_item(c); it = T.llm_item(1, "redelivery fee", reason="none", changed=False)
            m = r.rescue_canonicalization_item(it, o, T.view_span(o))
            row.update(result="NOT_RESCUED(CMU分解不採用)", route="-", code=None, final=None, cmu=cmu.reasons_for_phrase(d), rescue_meta=m)
        else:
            o = T.original_item(c); it = T.llm_item(1, LLM_KEY[no]); m = r.rescue_canonicalization_item(it, o, T.view_span(o))
            if m:
                row.update(result="RESCUED", route="canonicalization段(救済フロー)", code=m["code"], final=it["key_phrase"], dropped_tail=m["dropped_tail"])
            else:
                row.update(result="PASS(通常フロー・区分1是正)", route="通常", code=None, final=LLM_KEY[no],
                           validator_ok=kc.validate_canonicalization_item(LLM_KEY[no], d, T.view_span(o), normalization_reason="lemma_normalization" if LLM_KEY[no].lower()!=d.lower() else "none", original_span=o["source_span"], allow_inflection_normalization=True)["ok"])
        rows.append(row)

# 実データ回帰: 過去のX/Y/Z成果物の(display,key)対で、承認済みGate(最終Gate同一引数)を通る既存itemは救済で不変
import glob
pairs = set()
for pat in ("er019_output", "er026_output", "er121_output"):
    for f in glob.glob(os.path.join(ROOT, pat, "**", "keywords_canonicalized.json"), recursive=True):
        try:
            d = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        for it in d.get("items", []):
            dp, kp = it.get("display_phrase"), it.get("key_phrase") or it.get("used_form")
            if dp and kp:
                pairs.add((dp, kp, it.get("normalization_reason") or "none", it.get("canonicalization_source_span") or it.get("source_span") or dp,
                           it.get("source_span") or dp, tuple(sorted(((it.get("person_role_repair") or {}).get("role_ok_poss")) or []))))
changed, passing, failing, rescued_when_failing = 0, 0, 0, []
for dp, kp, nr, vspan, ospan, rok in sorted(pairs):
    o = {"rank": 1, "display_phrase": dp, "source_span": ospan, "source_sentence": dp, "fulltext_source_ref": "fulltext_exact_v1"}
    item = T.llm_item(1, kp, reason=nr if nr in ("none", "lemma_normalization", "generalize_person_dependent_reference", "generalize_reference_word") else "lemma_normalization")
    item["person_role_repair"] = {"role_ok_poss": list(rok)}
    g = r._gate(kp, dp, vspan, ospan, frozenset(rok), item["normalization_reason"])
    before = item["key_phrase"]
    m = r.rescue_canonicalization_item(item, o, vspan)
    if g["ok"]:
        passing += 1
        if m is not None or item["key_phrase"] != before:
            changed += 1
    else:
        failing += 1
        if m is not None:
            rescued_when_failing.append([dp, kp, item["key_phrase"], m["code"]])
out = {"cases": rows, "real_data": {"n_pairs": len(pairs), "gate_passing": passing, "gate_failing": failing, "passing_but_changed_by_rescue": changed,
                                     "failing_and_rescued": rescued_when_failing},
       "lexicon": r.lexicon_status(), "provenance": "synthetic/frozen fixtures(case_fixtures_01.json)+過去成果物(keywords_canonicalized.json)。API 0。fresh runtime evidenceは委任_02"}
json.dump(out, open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in out["real_data"].items() if k != "failing_and_rescued"}), len(rescued_when_failing))
for x in rows: print(x["no"], x["display"], "|", x["result"], "|", x.get("code"), "|", x.get("final"))
