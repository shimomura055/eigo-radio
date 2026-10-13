# ============================================================
# er064_kp_int_01_analyze.py (Round1 集計: 層1[gate前の選定生出力5件+backup]と層2[gate]を分離。評価専用、¥0)
# 出力: round1/analysis_r1.json, round1/analysis_r1.md
# ============================================================
import collections
import glob
import itertools
import json
import os
import re
import sys

sys.path.insert(0, os.getcwd())
import er064_kp_int_01_eval as EV  # noqa: E402
import er064_kp_opt_01_upstream_core as U  # noqa: E402

OUT = "er064_output/kp_integrated_opt_01/round1"
P2 = "er064_output/kp_extraction_selection_opt_01/phase2"
PERSON = re.compile(r"\b(my|your|his|her|its|their|our)\b", re.I)


def load_runs():
    runs = []
    for f in sorted(glob.glob(f"{OUT}/runs/*/job_result.json")):
        r = json.load(open(f, encoding="utf-8"))
        r["source"] = "round1"
        runs.append(r)
    # 他記事のM0P0基準 = 前回Phase2のC0(同一Prompt byte一致をshaで確認済み。再実行しない)
    for f in sorted(glob.glob(f"{P2}/runs/*_C0_run*/job_result.json")):
        r = json.load(open(f, encoding="utf-8"))
        if r["article"] in ("meta", "hormuz"):
            r["combo"], r["M"], r["P"], r["source"] = "M0P0", "M0", "P0", "phase2_C0_reuse"
            runs.append(r)
    return runs


def backup_of(r):
    """Stage2以降はselection callの生出力(output_text)にbackup_itemが残る。Stage1(未保存)はNone。"""
    for u in reversed((r.get("usage") or {}).get("selection", [])):
        t = u.get("output_text")
        if t:
            try:
                b = json.loads(t).get("backup_item") or {}
                return f"{b.get('display_phrase')}<{b.get('resolved_candidate_surface_form') or b.get('surface_echo')}>"
            except Exception:
                return None
    return None


def jacc(a, b):
    return len(a & b) / len(a | b) if a | b else 1.0


def cand_key(it):
    return (it.get("candidate_surface") or it.get("display_phrase") or "").lower()


def analyze():
    runs = load_runs()
    groups = collections.defaultdict(list)
    for r in runs:
        groups[(r["article"], r["level"], r["combo"])].append(r)
    art_anchor = {lv: EV.in_article(U.read_article(f"coffee_{lv}")) for lv in ("std", "adv")}
    sl = json.load(open(f"{OUT}/shortlists_r1.json", encoding="utf-8"))["articles"]
    res = {}
    for (art, lv, cn), rs in sorted(groups.items()):
        valid = [r for r in rs if r.get("selected_items")]
        ent = {"article": art, "level": lv, "combo": cn, "source": rs[0]["source"], "n": len(rs), "n_valid": len(valid),
               "sel_pass": sum(1 for r in rs if r["selection_status"] == "KEY_WORDS_STRUCTURE_PASS"),
               "sel_status": dict(collections.Counter(r["selection_status"] for r in rs)),
               "canon": dict(collections.Counter(str(r.get("canonicalization_status")) for r in rs)),
               "redundancy": dict(collections.Counter(str(r.get("redundancy_status")) for r in rs if r.get("canonicalization_status"))),
               "all_gate_pass": sum(1 for r in rs if r["selection_status"] == "KEY_WORDS_STRUCTURE_PASS" and r.get("canonicalization_status") == "CANONICALIZATION_PASS" and r.get("redundancy_status") in ("PASS", "REDUNDANCY_QA_PASS", "REDUNDANCY_PASS")),
               "cost_mean": round(sum(r["cost_jpy"] for r in rs) / len(rs), 3), "cost_total": round(sum(r["cost_jpy"] for r in rs), 3),
               "elapsed_mean": round(sum(r["elapsed_sec"] for r in rs) / len(rs), 1), "reasoning_tokens_sel_mean": None, "runs": []}
        rt = [sum(u["usage"].get("reasoning_tokens", 0) or 0 for u in r["usage"]["selection"]) for r in rs if r.get("usage")]
        ent["reasoning_tokens_sel_mean"] = round(sum(rt) / len(rt)) if rt else None
        sets = []
        scores, low, creative_imp, creative_topic = [], [], [], []
        adopt = collections.Counter()
        adopt_frag = collections.Counter()
        for r in valid:
            items = r["selected_items"]
            sc = EV.run_score(items) if art == "coffee" else None
            ci = sum(1 for i in items if i["role"] == "important" and EV.is_creative(i)) if art == "coffee" else None
            ct = sum(1 for i in items if i["role"] == "topic" and EV.is_creative(i)) if art == "coffee" else None
            if sc:
                scores.append(sc["score"])
                low.append(sc["low_slots"])
                creative_imp.append(ci)
                creative_topic.append(ct)
                for rk in sc["full_ranks"]:
                    adopt[rk] += 1
                for rk in sc["fragment_ranks"]:
                    adopt_frag[rk] += 1
            sets.append({cand_key(i) for i in items})
            canon_items = [(c["key_phrase"], c["display_phrase"], c["normalization_reason"]) for c in r.get("canonicalized", [])]
            ent["runs"].append({"run": r["run"], "sel_status": r["selection_status"], "canon": r.get("canonicalization_status"), "redundancy": r.get("redundancy_status"),
                                "items": [(i["rank"], i["role"], i["display_phrase"], i.get("candidate_surface"), i.get("evidence")) for i in items],
                                "backup": backup_of(r), "score": sc, "creative_important": ci,
                                "canon_items": canon_items, "canon_reasons": r.get("canonicalization_item_reasons"),
                                "dup_pairs": r.get("redundancy_duplicate_pairs"), "person_items": [i["display_phrase"] for i in items if PERSON.search(i.get("display_phrase") or "")],
                                "source_span_missing": r.get("source_span_missing"), "validation_reasons": r.get("validation_reasons"), "cost": r["cost_jpy"]})
        # invalid runsも記録
        for r in rs:
            if not r.get("selected_items"):
                ent["runs"].append({"run": r["run"], "sel_status": r["selection_status"], "validation_reasons": r.get("validation_reasons"), "item_reasons": r.get("item_reasons"), "cost": r["cost_jpy"]})
        ent["runs"].sort(key=lambda x: x["run"])
        if len(sets) >= 2:
            ent["jaccard_mean"] = round(sum(jacc(a, b) for a, b in itertools.combinations(sets, 2)) / len(list(itertools.combinations(sets, 2))), 3)
        else:
            ent["jaccard_mean"] = None
        if art == "coffee":
            ent["score_mean"] = round(sum(scores) / len(scores), 2) if scores else None
            ent["score_ceiling"] = EV.ceiling(art_anchor[lv])
            ent["low_slots_per_run"] = round(sum(low) / len(low), 2) if low else None
            ent["creative_important_per_run"] = round(sum(creative_imp) / len(creative_imp), 2) if creative_imp else None
            ent["creative_topic_runs"] = sum(creative_topic) if creative_topic else 0
            ent["adopt_full"] = {str(k): adopt[k] for k in sorted(adopt)}
            ent["adopt_fragment"] = {str(k): adopt_frag[k] for k in sorted(adopt_frag)}
            m = cn[:2]
            reach = EV.reach_in_shortlist(sl[f"coffee_{lv}"][m]["candidates"]) if m in sl[f"coffee_{lv}"] else {}
            ent["reach"] = {str(k): v for k, v in reach.items() if k in art_anchor[lv]}
            ent["reached_not_selected"] = [k for k, v in ent["reach"].items() if v and adopt[int(k)] == 0 and adopt_frag[int(k)] == 0]
        res[f"{art}_{lv}_{cn}"] = ent
    json.dump(res, open(f"{OUT}/analysis_r1.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return res


def md(res):
    L = ["# analysis_r1 (自動生成。層1=gate前の選定生出力、層2=gate。Coffeeのみアンカー採点)", ""]
    L.append("## 比較表(Coffee)")
    L.append("| combo | Lv | valid/n | score平均/上限 | アンカー採用(full rank:回数) | fragment | 低優先枠/run | 創作比喩Imp/run | Jaccard | sel PASS | canon | redundancy | 費用/job | reasoning tok(sel) |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for k, e in res.items():
        if e["article"] != "coffee":
            continue
        L.append(f"| {e['combo']} | {e['level']} | {e['n_valid']}/{e['n']} | {e['score_mean']}/{e['score_ceiling']} | {e['adopt_full']} | {e['adopt_fragment']} | {e['low_slots_per_run']} | {e['creative_important_per_run']} | {e['jaccard_mean']} | {e['sel_pass']}/{e['n']} | {e['canon']} | {e['redundancy']} | {e['cost_mean']} | {e['reasoning_tokens_sel_mean']} |")
    L.append("")
    L.append("## 最終5件(層1: gate前の選定生出力のdisplay_phrase。role:display(候補)。全run)")
    for k, e in res.items():
        L.append(f"### {k} ({e['source']})")
        for r in e["runs"]:
            if "items" not in r:
                L.append(f"- run{r['run']}: **{r['sel_status']}** {r.get('validation_reasons')} {r.get('item_reasons')}")
                continue
            its = " / ".join(f"{x[1][0].upper()}:{x[2]}" + (f"<{x[3]}>" if x[3] and x[3].lower() != (x[2] or '').lower() else "") for x in r["items"])
            sc = f" score={r['score']['score']}" if r.get("score") else ""
            L.append(f"- run{r['run']}: {its} | backup={r['backup']}{sc} | canon={r['canon']} red={r['redundancy']}")
    L.append("")
    L.append("## 層2 gate詳細(canonicalization/Redundancyの非PASS)")
    for k, e in res.items():
        for r in e["runs"]:
            if "items" in r and (r["canon"] != "CANONICALIZATION_PASS" or r["redundancy"] not in ("PASS", "REDUNDANCY_QA_PASS", "REDUNDANCY_PASS")):
                L.append(f"- {k} run{r['run']}: canon={r['canon']} reasons={r['canon_reasons']} red={r['redundancy']} dup={r['dup_pairs']} person_items={r['person_items']}")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    res = analyze()
    open(f"{OUT}/analysis_r1.md", "w", encoding="utf-8").write(md(res))
    print(f"groups {len(res)}")
