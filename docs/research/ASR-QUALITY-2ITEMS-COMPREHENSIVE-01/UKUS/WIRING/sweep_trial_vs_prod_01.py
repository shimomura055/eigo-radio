# ============================================================
# sweep_trial_vs_prod_01.py -- ASR-QUALITY-2ITEMS ②UKUS 委任_04 W-01: Trial(er111 evaluate_trial) <-> Production(er109 evaluate(ukus=True)) 同等性sweep。API 0。
# 一回限りの証跡script(Trial撤去前に実行。Trial撤去後は git履歴[撤去commit直前]のTrial moduleが必要)。Production(repo root)からはimportされない。
# 使い方(cwd=repo root): .venv\Scripts\python.exe docs/research/ASR-QUALITY-2ITEMS-COMPREHENSIVE-01/UKUS/WIRING/sweep_trial_vs_prod_01.py [--limit N] [--stored]
# 比較項目(W-01(2)): equivalent / reason / warnings(集合) / ukus_pairs(完全一致) / rules(集合比較・差分全件列挙)。spans は比較対象外(Trial=位置別分解、Production=不合格span位置のみ)。
# 追加: Production(ukus=False) <-> HEAD版er109(v1)の出力同一性(reason/rules/warnings/spans/equivalent)、Production(ukus=True)で PASS->NG 0。
# ============================================================
import argparse
import collections
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import time

ROOT = os.getcwd()
sys.path.insert(0, ROOT)
OUT = os.path.join(ROOT, "docs", "research", "ASR-QUALITY-2ITEMS-COMPREHENSIVE-01", "UKUS", "WIRING")

import er109_asr_orthographic_equivalence_01 as P          # Production(新)
import er111_ukus_spelling_trial_01 as T                   # Trial
TBL = T.PairTable(os.path.join(ROOT, "er109_ukus_pairs_v1.json"))   # 対表は内容不変でgit mv済み(同一ファイル)


def load_head_e109():
    src = subprocess.run(["git", "show", "HEAD:er109_asr_orthographic_equivalence_01.py"], capture_output=True, cwd=ROOT).stdout
    d = tempfile.mkdtemp()
    p = os.path.join(d, "e109_head_v1.py")
    open(p, "wb").write(src)
    spec = importlib.util.spec_from_file_location("e109_head_v1", p)
    m = importlib.util.module_from_spec(spec)
    sys.modules["e109_head_v1"] = m
    spec.loader.exec_module(m)
    return m


def cap(w):
    return w[:1].upper() + w[1:]


TEMPLATES = {
    "initial_lower_word_mid": ("She said the {w} was very important to them.", "She said the {v} was very important to them."),
    "sentence_initial_cap": ("{W} is here today.", "{V} is here today."),
    "initial_cap_next_cap": ("{W} Street is closed today.", "{V} Street is closed today."),
    "possessive": ("The {w}'s role was clear to all of them.", "The {v}'s role was clear to all of them."),
    "hyphen_compound": ("A {w}-based plan worked for the team.", "A {v}-based plan worked for the team."),
    "v1_span_adjacent_their_there": ("Their {w} was fine at the time.", "There {v} was fine at the time."),
    "v1_span_separate": ("Their dog liked the {w} a lot.", "There dog liked the {v} a lot."),
    "number_adjacent": ("The {w} cost 3 dollars for them.", "The {v} cost three dollars for them."),
    "negation_present": ("He did not see the {w} at all.", "He did not see the {v} at all."),
    "contraction_adjacent": ("The {w} I'm sure about is here.", "The {v} I am sure about is here."),
    "entity_midcap": ("She said {W} was important to them.", "She said {V} was important to them."),
    "len_mismatch_flags": ("The U.S.-based {w} paid 3.5% of $4,000 to them.", "The U.S.-based {v} paid 3.5% of $4,000 to them."),
    "two_positions_nn": ("The {w} and the {w} were nice here.", "The {v} and the {v} were nice here."),
}


def cases(pairs, limit=None):
    out = []
    for e in pairs[: limit or None]:
        uk, us = e["uk"], e["us"]
        for a, b in ((uk, us), (us, uk)):
            for name, (tc, ta) in TEMPLATES.items():
                out.append((name, f"{a}->{b}", tc.format(w=a, W=cap(a)), ta.format(v=b, V=cap(b))))
    return out


def cmp_fields(t, p):
    d = {}
    if t.equivalent != p.equivalent:
        d["equivalent"] = [t.equivalent, p.equivalent]
    if t.equivalent and p.equivalent:
        if t.reason != p.reason:
            d["reason"] = [t.reason, p.reason]
        if set(t.warnings) != set(p.warnings):
            d["warnings"] = [sorted(t.warnings), sorted(p.warnings)]
        if list(t.ukus_pairs) != list(p.ukus_pairs):
            d["ukus_pairs"] = [t.ukus_pairs, p.ukus_pairs]
        if set(t.rules) != set(p.rules):
            d["rules"] = [sorted(t.rules), sorted(p.rules)]
    return d


def span_sig(r):
    return [[s.canon_span, s.asr_span, s.equivalent, s.rule, s.why, s.matched, s.representative_match, s.heteronym_guard, s.warnings] for s in r.spans]


def full_sig(r):
    return (r.equivalent, r.reason, tuple(r.rules), tuple(r.warnings), r.contraction_expanded, json.dumps(span_sig(r), sort_keys=True, default=str))


def run(items, head, label, res, max_listed=400):
    stats = collections.Counter()
    diffs = []
    for item in items:
        name, pair, c, a = item[:4]
        stats["n"] += 1
        t = T.evaluate_trial(c, a, tbl=TBL)
        p = P.evaluate(c, a, ukus=True)
        po = P.evaluate(c, a, ukus=False)
        ho = head.evaluate(c, a)
        # 1) ukus=False は HEAD(v1) と出力同一(version文字列を除く)
        if full_sig(po) != full_sig(ho):
            stats["off_vs_head_DIFF"] += 1
            diffs.append({"kind": "off_vs_head", "name": name, "pair": pair, "c": c, "a": a})
        # 2) PASS->NG 0(ukus=True は ukus=False の PASS を落とさない。PASS行の出力も同一)
        if po.equivalent:
            stats["off_pass"] += 1
            if not p.equivalent:
                stats["PASS_to_NG"] += 1
                diffs.append({"kind": "PASS_to_NG", "name": name, "pair": pair, "c": c, "a": a})
            elif full_sig(po) != full_sig(p):
                stats["off_pass_output_changed"] += 1
                diffs.append({"kind": "off_pass_output_changed", "name": name, "pair": pair, "c": c, "a": a})
        elif p.equivalent:
            stats["NG_to_PASS"] += 1
            if not p.ukus_pairs or "ukus_spelling_variant" not in p.rules:
                stats["NG_to_PASS_without_ukus"] += 1
                diffs.append({"kind": "NG_to_PASS_without_ukus", "name": name, "pair": pair, "c": c, "a": a, "reason": p.reason})
        # 3) Trial <-> Production
        d = cmp_fields(t, p)
        if d:
            stats["trial_vs_prod_DIFF"] += 1
            for k in d:
                stats["trial_vs_prod_DIFF_" + k] += 1
            diffs.append({"kind": "trial_vs_prod", "name": name, "pair": pair, "c": c, "a": a, "diff": d, "trial_rules": t.rules, "prod_rules": p.rules})
        else:
            stats["trial_vs_prod_same"] += 1
        # NG時のreasonは別集計(比較項目外)
        if (not t.equivalent) and (not p.equivalent):
            stats["both_NG"] += 1
            if t.reason != p.reason:
                stats["both_NG_reason_differs"] += 1
    res[label] = {"stats": dict(stats), "diffs_total": len(diffs), "diffs_listed": diffs[:max_listed]}
    return diffs


def classify_trial_vs_prod(diffs):
    c = collections.Counter()
    for x in diffs:
        if x["kind"] != "trial_vs_prod":
            continue
        d = x["diff"]
        if "equivalent" in d:
            c["equivalent:trial=%s,prod=%s" % tuple(d["equivalent"])] += 1
        else:
            c["fields:" + "+".join(sorted(d))] += 1
    return dict(c)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--stored", action="store_true")
    a = ap.parse_args()
    t0 = time.time()
    head = load_head_e109()
    pj = json.load(open(os.path.join(ROOT, "er109_ukus_pairs_v1.json"), encoding="utf-8"))
    pairs = [e for e in pj["pairs"] if e.get("active")]
    res = {"meta": {"n_active_pairs": len(pairs), "templates": list(TEMPLATES), "api_calls": 0}}
    if not a.stored:
        items = cases(pairs, a.limit)
        res["meta"]["n_cases_pairs_sweep"] = len(items)
        diffs = run(items, head, "pairs_sweep", res)
        res["pairs_sweep"]["classification_trial_vs_prod"] = classify_trial_vs_prod(diffs)
    else:
        import er111_ukus_trial_eval_01 as E
        rows = E._collect_rows()
        items = [("stored:" + r["set"], r.get("seg") or "", r["c"], r["a"]) for r in rows]
        res["meta"]["n_cases_stored"] = len(items)
        diffs = run(items, head, "stored_rows", res)
        res["stored_rows"]["classification_trial_vs_prod"] = classify_trial_vs_prod(diffs)
    res["meta"]["elapsed_s"] = round(time.time() - t0, 1)
    out = os.path.join(OUT, "DIFF_TEST_RESULT_%s_01.json" % ("stored" if a.stored else "pairs"))
    json.dump(res, open(out, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "meta"} if False else {"meta": res["meta"], **{k: res[k]["stats"] for k in res if k not in ("meta",)}}, ensure_ascii=False, indent=1))
    print("saved", out)


if __name__ == "__main__":
    main()
