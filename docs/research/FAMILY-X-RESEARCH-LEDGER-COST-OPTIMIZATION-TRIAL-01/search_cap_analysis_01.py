"""FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01 委任_01 案1事前分析(read-only、API呼出なし、JPY0)。

目的: 既存Ledger検証ログから、Factごとの (a)関連クエリ数 (b)ツール呼出数 (c)最終判定
(d)上限2/3/5での打切りシミュレーションを集計する。

重要な限界(ログ構造由来。推測で補わない):
  * verification_full_record.json の search_usage は {web_search_call_count: 総数, queries: [クエリ文字列...]} のみ。
    各クエリがどの呼出に属するか、呼出の種別(search/open_page/find)、クエリ→Factの対応、
    「何回目で裏付けに到達したか」は保存されていない => Fact単位の呼出数は復元不能。
  * クエリ→Factの対応は、数値トークン・固有語の一致による**推定(heuristic)**であり、事実ではない。
    推定が一意でないクエリは unassigned/ambiguous として別計上する(打切り削減額は一意割当分のみ=下限側)。
  * 「到達回」(何回目で十分な裏付けに達したか)は復元不能。first/last_query_index は
    ラン全体のクエリ列内の位置(Fact別の回数ではない)であり、到達回の代替ではない。
"""
import argparse
import json
import math
import os
import re
import sys

USD_JPY = 160.0  # er012_e_family_entertainment_two_level_runner_01.py:68
WS_MODEL = "N/A (tool, all models)"
SEARCH_CONTENT_TOKENS_PER_CALL = 9000  # RLCO ANALYSIS_REPORT_01 §6 の 8.3〜9.4千token の中央付近(仮定)
STOP = set("site http https www com org html pdf news press the and for with from that this 2024 2025 2026 2027".split())


def load_price(path):
    d = json.load(open(path, encoding="utf-8"))
    return {(p["model"], p["meter"]): p["price"] for p in d["prices"]}


def jpy_per_call(tbl, model):
    fee = tbl[(WS_MODEL, "web_search_call")] / 1000 * USD_JPY
    tok = SEARCH_CONTENT_TOKENS_PER_CALL * tbl[(model, "input_tokens")] / 1e6 * USD_JPY
    return fee, tok


def toks(text):
    out = set()
    for m in re.findall(r"\d[\d,\.]*\d", text):
        t = m.replace(",", "")
        if len(t) >= 3:
            out.add(t)
    for m in re.findall(r"[A-Za-z][A-Za-z\-]{3,}", text):
        w = m.lower()
        if w not in STOP:
            out.add(w)
    return out


def analyze_run(run, tbl):
    L = lambda f: os.path.join(run, f)
    vr = json.load(open(L("research_ledger/audit/verification_full_record.json"), encoding="utf-8"))
    su = vr["search_usage"]
    queries = su.get("queries") or []
    calls = su.get("web_search_call_count")
    model = vr.get("model")
    draft = json.load(open(L("research_ledger/fact_ledger_draft.json"), encoding="utf-8"))["facts"]
    ver = json.load(open(L("research_ledger/fact_ledger_verification.json"), encoding="utf-8"))["verifications"]
    vmap = {v["fact_id"]: v for v in ver}
    sel = []
    sp = L("storyline_b3/fact_selection_evidence.json")
    if os.path.exists(sp):
        sel = json.load(open(sp, encoding="utf-8")).get("selected_fact_ids", [])
    slug = None
    ep = L("entry_point.json")
    if os.path.exists(ep):
        slug = json.load(open(ep, encoding="utf-8")).get("args", {}).get("slug")

    ftext = {}
    for f in draft:
        fid = f["fact_id"]
        t = " ".join(str(f.get(k) or "") for k in ("claim", "subject", "date_or_period", "numeric_value", "numeric_scope", "source_title", "source_url", "scope"))
        t += " " + str(vmap.get(fid, {}).get("verification_notes") or "")
        ftext[fid] = toks(t)
    df = {}
    for fid, ts in ftext.items():
        for t in ts:
            df[t] = df.get(t, 0) + 1

    # クエリ→Fact 推定割当
    assign = []
    for qi, q in enumerate(queries):
        qt = toks(q)
        scores = {}
        for fid, ts in ftext.items():
            s = sum(1.0 / df[t] for t in qt if t in ts)
            if s > 0:
                scores[fid] = s
        if not scores:
            assign.append({"q": qi, "fact": None, "status": "unmapped"})
            continue
        best = max(scores.values())
        top = [k for k, v in scores.items() if v >= best - 1e-9]
        runner = sorted(scores.values(), reverse=True)
        second = runner[1] if len(runner) > 1 else 0
        if best < 0.9:
            assign.append({"q": qi, "fact": None, "status": "weak", "cand": top})
        elif len(top) == 1 and second < 0.7 * best:
            assign.append({"q": qi, "fact": top[0], "status": "unique"})
        else:
            assign.append({"q": qi, "fact": None, "status": "ambiguous", "cand": top})
    per_fact = {}
    for f in draft:
        fid = f["fact_id"]
        qs = [a["q"] for a in assign if a["fact"] == fid]
        per_fact[fid] = {
            "fact_id": fid,
            "verdict": vmap.get(fid, {}).get("verdict"),
            "selected_by_b3": fid in sel,
            "n_queries_unique_assigned_HEURISTIC": len(qs),
            "first_query_index_in_run": qs[0] if qs else None,
            "last_query_index_in_run": qs[-1] if qs else None,
            "calls_per_fact": "復元不能(ログに呼出単位・クエリ→Fact対応なし)",
            "calls_to_sufficient_support": "復元不能(判定は応答末尾のみ。中間状態は未保存)",
        }
    n_q = len(queries)
    ratio = (calls / n_q) if (calls is not None and n_q) else None
    n_dup = n_q - len(set(queries))
    fee, tok = jpy_per_call(tbl, model) if model else (None, None)
    # 同一文書を共有するFact群(曖昧割当の候補集合)は「群」として扱う: 群のクエリ数 = 群内ambiguous割当 + 群メンバーへのunique割当。
    # 群の打切り上限 = N x 群サイズ(メンバー各Factに上限Nを与える最も寛容な解釈 = 削減額は下限側)。
    groups = {}
    for a_ in assign:
        if a_["status"] == "ambiguous" and len(a_["cand"]) <= 3:
            groups.setdefault(frozenset(a_["cand"]), 0)
            groups[frozenset(a_["cand"])] += 1
    units = []  # (label, member_fact_ids, n_queries)
    in_group = set()
    for g, n_amb in groups.items():
        n_uni = sum(per_fact[f]["n_queries_unique_assigned_HEURISTIC"] for f in g)
        units.append(("group:" + "+".join(sorted(g)), sorted(g), n_amb + n_uni))
        in_group |= set(g)
    for fid, pf in per_fact.items():
        if fid not in in_group:
            units.append(("fact:" + fid, [fid], pf["n_queries_unique_assigned_HEURISTIC"]))
    sims = {}
    for N in (2, 3, 5):
        for unit in ("cap_on_queries", "cap_on_calls_via_ratio"):
            if ratio is None:
                continue
            qcap_per_fact = N if unit == "cap_on_queries" else (N / ratio)
            cut_q = 0.0
            at_risk_units = []
            at_risk = {"facts_over_cap": 0, "VERIFIED": 0, "AMBIGUOUS": 0, "REJECTED": 0, "selected": 0, "VERIFIED_and_selected": 0}
            for label, members, nq in units:
                excess = max(0.0, nq - qcap_per_fact * len(members))
                if excess > 0:
                    cut_q += excess
                    at_risk_units.append({"unit": label, "queries": nq, "cut_queries": round(excess, 2)})
                    for fid in members:
                        pf = per_fact[fid]
                        at_risk["facts_over_cap"] += 1
                        at_risk[pf["verdict"]] = at_risk.get(pf["verdict"], 0) + 1
                        if pf["selected_by_b3"]:
                            at_risk["selected"] += 1
                            if pf["verdict"] == "VERIFIED":
                                at_risk["VERIFIED_and_selected"] += 1
            cut_calls = cut_q * ratio
            sims[f"N{N}_{unit}"] = {
                "effective_query_cap_per_fact": round(qcap_per_fact, 2),
                "cut_queries_lower_bound": round(cut_q, 2),
                "cut_calls_est": round(cut_calls, 2),
                "saving_jpy_est": round(cut_calls * (fee + tok), 2),
                "at_risk_units": at_risk_units,
                "at_risk_facts_upper_bound": at_risk,
            }
    status_counts = {}
    for a in assign:
        status_counts[a["status"]] = status_counts.get(a["status"], 0) + 1
    return {
        "run": run.replace(os.sep, "/"), "slug": slug, "model": model,
        "n_facts": len(draft), "selected_fact_ids": sel,
        "verdicts": {k: sum(1 for v in ver if v["verdict"] == k) for k in ("VERIFIED", "AMBIGUOUS", "REJECTED")},
        "ledger_web_search_call_count": calls, "n_queries_logged": n_q, "calls_per_query_ratio": (round(ratio, 3) if ratio else None),
        "calls_gt_queries": (calls is not None and calls > n_q),
        "n_duplicate_queries_exact": n_dup,
        "calls_per_fact_mean": (round(calls / len(draft), 2) if calls is not None and draft else None),
        "query_assignment_status_HEURISTIC": status_counts,
        "jpy_per_call_fee_and_token_assumed": [round(fee, 3), round(tok, 3)] if fee is not None else None,
        "per_fact": list(per_fact.values()),
        "cap_simulation": sims,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--pricing", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    tbl = load_price(a.pricing)
    results, skipped = [], []
    for r in a.runs:
        if not os.path.exists(os.path.join(r, "research_ledger/audit/verification_full_record.json")):
            skipped.append(r)
            continue
        results.append(analyze_run(r, tbl))
    out = {"schema": "search_cap_analysis_01", "jpy": 0, "api_calls": 0,
           "limitations": ["call-unit per fact NOT recoverable", "query->fact mapping is heuristic", "calls-to-sufficient-support NOT recoverable"],
           "skipped_runs": skipped, "runs": results}
    json.dump(out, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("runs", len(results), "skipped", skipped)


if __name__ == "__main__":
    main()
