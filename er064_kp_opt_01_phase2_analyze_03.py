# KP-OPT-01 委任_03 Phase 2 集計(API呼出なし、JPY0、Trial専用)。出力: phase2/analysis_03.json, analysis_03.md
import collections
import glob
import itertools
import json
import os
import re

OUT = "er064_output/kp_extraction_selection_opt_01/phase2"
COV = json.load(open("er064_output/kp_extraction_selection_opt_01/phase1_fix/phase2_label_coverage_02.json", encoding="utf-8"))["coverage"]
ABC = json.load(open("er064_output/kp_idiom_priority_abc_01/final_summary_01.json", encoding="utf-8"))["runs"]
R7 = json.load(open("er064_output/kp_extraction_selection_opt_01/phase1_a/rule7_predicted_invalid_01.json", encoding="utf-8"))["predicted_invalid_cells"]
LOW = ["take time", "right away", "on a regular basis", "price measure", "retail prices", "usual cup"]
CREATIVE = ["two numbers in the ring", "in the ring", "its own hidden clock", "hidden clock"]


def nk(s):
    return re.sub(r"[\s\-]+", " ", (s or "").lower().replace("’", "'")).strip()


def is_pump(s):
    s = (s or "").lower()
    return "pump" in s and "fist" in s


runs = []
for p in sorted(glob.glob(f"{OUT}/runs/*/job_result.json")):
    runs.append(json.load(open(p, encoding="utf-8")))
errors = []
for p in sorted(glob.glob(f"{OUT}/stage*_summary_03.json")):
    errors += json.load(open(p, encoding="utf-8")).get("errors", [])


def final_items(r):
    """層1: gate前のselector生出力5件(display_phrase, role)"""
    return [(nk(i["display_phrase"]), i["role"], i.get("candidate_surface")) for i in r.get("selected_items", [])]


def gate(r):
    if r["selection_status"] != "KEY_WORDS_STRUCTURE_PASS":
        return "SELECTION_INVALID"
    cs = r.get("canonicalization_status")
    if cs != "CANONICALIZATION_PASS":
        return cs
    return "PASS" if r.get("redundancy_status") == "REDUNDANCY_PASS" else (r.get("redundancy_status") or "NO_QA")


def jacc(a, b):
    a, b = set(a), set(b)
    return len(a & b) / len(a | b) if a | b else 1.0


def label_ok(art, lvl, group, label):
    return COV.get(f"{art}_{lvl}", {}).get(group, {}).get(label, {}).get("comparable_C0_vs_C2", False)


GLOSS_BAD = [("括弧", re.compile(r"[（(）)]")), ("算用数字", re.compile(r"[0-9０-９]")), ("三点リーダ", re.compile(r"…|\.\.\.")),
             ("穴埋め~", re.compile(r"[～〜]\s*[%％]|[～〜]{2}"))]


def gloss_flags(r):
    out = []
    for i in r.get("selected_items", []):
        g = i.get("ja_gloss") or ""
        for n, rx in GLOSS_BAD:
            if rx.search(g):
                out.append((i["display_phrase"], n, g))
    return out


# --- rule7 predicted
R7_TOKENS = {(c["display_token"], c["prompt_suggested_generic"]) for c in R7}


def rule7_explained(r):
    """canonicalization INVALIDのうち、Rule7予測の(表示語->一般化語)組を含む項目があるか。item_reasonsと正規化後keyで判定。"""
    reasons = json.dumps(r.get("canonicalization_item_reasons"), ensure_ascii=False)
    hit = []
    for tok, gen in R7_TOKENS:
        if (re.search(rf"\b{re.escape(tok)}\b", reasons) and gen in reasons):
            hit.append((tok, gen))
    # 項目reasonsにperson_dependent/generalize系文言があるか
    kw = any(k in reasons for k in ("generalize", "person", "一般化", "所有格", "someone", "somebody"))
    return bool(hit), hit  # kw(一般的な文言)だけでは予測内扱いにしない(Rule7文言は汎用)


cells = collections.defaultdict(list)
for r in runs:
    cells[(r["article"], r["level"], r["cond"])].append(r)
cells_abc = collections.defaultdict(list)
for r in ABC:
    if r["version"] == "A":
        cells_abc[("coffee", r["level"], "C0p")].append(r)

res = {"cells": {}, "errors": errors}
md = []
md.append("# Phase 2 集計(層1=gate前selector生出力、層2=gate別)\n")
for (art, lv, cond), rs in sorted(cells.items()):
    rs.sort(key=lambda r: r["run"])
    sets = [set(x[0] for x in final_items(r)) for r in rs if r.get("selected_items")]
    pairs = [jacc(a, b) for a, b in itertools.combinations(sets, 2)]
    freq = collections.Counter(itertools.chain.from_iterable(sets))
    allitems = [x for r in rs for x in final_items(r)]
    c = {"n": len(rs), "jaccard_mean": round(sum(pairs) / len(pairs), 3) if pairs else None, "jaccard_pairs": [round(x, 3) for x in pairs],
         "freq": dict(freq.most_common()),
         "time_lag_selected_runs": sum(1 for r in rs if any(x[0] == "time lag" for x in final_items(r))),
         "lag_only_selected_runs": sum(1 for r in rs if any(x[0] == "lag" for x in final_items(r))),
         "pump_fist_selected_runs": sum(1 for r in rs if any(is_pump(x[0]) for x in final_items(r))),
         "low_priority_slots": {k: sum(1 for x in allitems if x[0] == k) for k in LOW if any(x[0] == k for x in allitems)},
         "low_priority_slots_total": sum(1 for x in allitems if x[0] in LOW),
         "creative_in_important": sum(1 for r in rs for x in final_items(r) if x[1] == "important" and (x[0] in CREATIVE)),
         "creative_in_topic": sum(1 for r in rs for x in final_items(r) if x[1] == "topic" and (x[0] in CREATIVE)),
         "topic_phrases": [[x[0] for x in final_items(r) if x[1] == "topic"] for r in rs],
         "role_counts_ok": sum(1 for r in rs if r.get("selected_items") and sum(1 for i in r["selected_items"] if i["role"] == "topic") == 1),
         "gate": dict(collections.Counter(gate(r) for r in rs)),
         "cost_mean_jpy": round(sum(r["cost_jpy"] for r in rs) / len(rs), 4),
         "cost_sum_jpy": round(sum(r["cost_jpy"] for r in rs), 4),
         "elapsed_mean_sec": round(sum(r["elapsed_sec"] for r in rs) / len(rs), 1)}
    # usage
    def usum(ph, f):
        return sum((u["usage"].get(f) or 0) for r in rs for u in r["usage"][ph])
    c["usage_sum"] = {ph: {f: usum(ph, f) for f in ("input_tokens", "output_tokens", "reasoning_tokens", "cached_input_tokens")} for ph in ("selection", "canon_qa")}
    c["calls_sum"] = {ph: sum(len(r["usage"][ph]) for r in rs) for ph in ("selection", "canon_qa")}
    c["selection_calls_per_job"] = round(c["calls_sum"]["selection"] / len(rs), 2)
    # expected labels (comparable only)
    lab = {}
    for g, items in COV.get(f"{art}_{lv}", {}).items():
        for it in items:
            if label_ok(art, lv, g, it):
                lab.setdefault(g, {})[it] = sum(1 for r in rs if any(x[0] == nk(it) for x in final_items(r)))
    c["comparable_label_hits_runs"] = lab
    g_flags = [f for r in rs for f in gloss_flags(r)]
    c["gloss_flags"] = g_flags
    c["gloss_flag_runs"] = sum(1 for r in rs if gloss_flags(r))
    # gate layer
    q = [r for r in rs if r.get("canonicalization_status") in ("CANONICALIZATION_PASS", "CANONICALIZATION_REVIEW_REQUIRED")]
    c["redundancy_denominator"] = len(q)
    c["redundancy_ng"] = sum(1 for r in q if r.get("redundancy_status") not in (None, "REDUNDANCY_PASS"))
    c["canon_invalid_runs"] = []
    for r in rs:
        if r.get("canonicalization_status") not in (None, "CANONICALIZATION_PASS", "CANONICALIZATION_REVIEW_REQUIRED"):
            ex, hit = rule7_explained(r)
            c["canon_invalid_runs"].append({"tag": r["tag"], "status": r["canonicalization_status"], "rule7_predicted": ex, "hit": hit})
    res["cells"][f"{art}_{lv}_{cond}"] = c
# C0' (ABC-A)
for (art, lv, cond), rs in sorted(cells_abc.items()):
    sets = [set(nk(i["display_phrase"]) for i in r.get("selected_items", [])) for r in rs]
    pairs = [jacc(a, b) for a, b in itertools.combinations(sets, 2)]
    allit = [(nk(i["display_phrase"]), i.get("role")) for r in rs for i in r.get("selected_items", [])]
    res["cells"][f"{art}_{lv}_C0p"] = {"n": len(rs), "jaccard_mean": round(sum(pairs) / len(pairs), 3) if pairs else None,
                                       "freq": dict(collections.Counter(itertools.chain.from_iterable(sets)).most_common()),
                                       "time_lag_selected_runs": sum(1 for s in sets if "time lag" in s), "lag_only_selected_runs": sum(1 for s in sets if "lag" in s),
                                       "pump_fist_selected_runs": sum(1 for s in sets if any(is_pump(x) for x in s)),
                                       "creative_in_important": sum(1 for x, ro in allit if ro == "important" and x in CREATIVE),
                                       "creative_in_topic": sum(1 for x, ro in allit if ro == "topic" and x in CREATIVE),
                                       "low_priority_slots_total": sum(1 for x, _ in allit if x in LOW),
                                       "note": "ABC-A(現行Prompt+V2 shortlist) 既存結果の再利用(新規費用0)"}
json.dump(res, open(f"{OUT}/analysis_03.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---- md: 5件全文表(層1) ----
for art in ("coffee", "meta", "hormuz"):
    for lv in ("std", "adv"):
        keys = [(c, rs) for (a, l, c), rs in sorted(cells.items()) if a == art and l == lv]
        if not keys:
            continue
        md.append(f"\n## {art} {lv.upper()} 5件全文(gate前selector生出力、rank順、[T]=topic)\n")
        md.append("| 条件 | run | 5件 | backup | gate | 費用 |\n|---|---|---|---|---|---|")
        order = {"C0": 0, "C1": 1, "C2": 2, "C2p": 3}
        for c, rs in sorted(keys, key=lambda x: order[x[0]]):
            for r in sorted(rs, key=lambda r: r["run"]):
                its = " / ".join(("[T]" if i["role"] == "topic" else "") + i["display_phrase"] for i in r.get("selected_items", [])) or "(選定INVALID)"
                bk_ = "(未記録)"
                md.append(f"| {c} | {r['run']} | {its} | {bk_} | {gate(r)} | {r['cost_jpy']:.2f} |")
        if art == "coffee" and lv == "adv":
            for r in cells_abc.get(("coffee", "adv", "C0p"), []):
                its = " / ".join(("[T]" if i.get("role") == "topic" else "") + i["display_phrase"] for i in r.get("selected_items", []))
                md.append(f"| C0'(ABC-A) | {r['run']} | {its} | - | - | - |")
md.append("\n## セル別サマリー\n")
md.append("| セル | n | Jaccard平均 | time lag | lag単独 | pump-fist | 低優先枠(件) | 創作Imp/Topic | gate | 費用/job | 秒/job | gloss旗 |\n|---|---|---|---|---|---|---|---|---|---|---|---|")
for k, c in res["cells"].items():
    md.append(f"| {k} | {c['n']} | {c['jaccard_mean']} | {c['time_lag_selected_runs']} | {c['lag_only_selected_runs']} | {c['pump_fist_selected_runs']} | "
              f"{c.get('low_priority_slots_total')} | {c.get('creative_in_important')}/{c.get('creative_in_topic')} | {c.get('gate', '-')} | {c.get('cost_mean_jpy', '-')} | {c.get('elapsed_mean_sec', '-')} | {c.get('gloss_flag_runs', '-')} |")
open(f"{OUT}/analysis_03.md", "w", encoding="utf-8").write("\n".join(md))
print("\n".join(md))
