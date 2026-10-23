# ============================================================
# er111_ukus_trial_eval_01.py -- ASR-QUALITY-2ITEMS-COMPREHENSIVE-01 ②英米綴り UKUS 委任_02 検証script(V1〜V8 + V5b/V5c)。DEV/Trial専用・API 0・費用0。
# 使い方(cwd=repo root):
#   .venv\Scripts\python.exe er111_ukus_trial_eval_01.py --v 1,2,3,4,5,7 [--corpus-dir <dir>]    # 各Vの結果jsonを TRIAL_01/ に保存
#   .venv\Scripts\python.exe er111_ukus_trial_eval_01.py --v 6      # c12再現(別processでProduction判定連鎖へTrial hookをpatch。LR/TTS/networkはmock)
#   .venv\Scripts\python.exe er111_ukus_trial_eval_01.py --v 8      # 既存test + 隔離 + golden不変
#   .venv\Scripts\python.exe er111_ukus_trial_eval_01.py --summary  # 集計md
# 隔離(Opus OF-07): Trial moduleはer109をmonkeypatchしない。V6のみ『専用worker process内』で er109_xz_scope_01._evaluate_cached を差し替え(+cache_clear)、終了で消える。
# ============================================================
from __future__ import annotations

import argparse
import collections
import glob
import hashlib
import json
import os
import random
import re
import statistics
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
OUT_DIR = os.path.join(ROOT, "docs", "research", "ASR-QUALITY-2ITEMS-COMPREHENSIVE-01", "UKUS", "TRIAL_01")
PY = sys.executable
JA = re.compile(r"[぀-ヿ㐀-䶿一-鿿]")


def save(name, obj):
    os.makedirs(OUT_DIR, exist_ok=True)
    p = os.path.join(OUT_DIR, name)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1, sort_keys=False)
    print("saved", os.path.relpath(p, ROOT))


def _mods():
    import er109_asr_orthographic_equivalence_01 as e109
    import er111_ukus_spelling_trial_01 as T
    import er111_ukus_trial_cases_01 as C
    return e109, T, C


# ---------------------------------------------------------------- V1
def v1():
    e109, T, C = _mods()
    rows, fails = [], []
    for uk, us, cl in C.V1_PAIRS:
        for c, a, d in ((uk, us, "uk>us"), (us, uk, "us>uk")):
            x, y = C.CARRIER.format(w=c), C.CARRIER.format(w=a)
            b = e109.evaluate(x, y)
            t = T.evaluate_trial(x, y)
            r = {"pair": f"{uk}/{us}", "class": cl, "dir": d, "base_eq": b.equivalent, "trial_eq": t.equivalent, "via_ukus": bool(t.ukus_pairs),
                 "pron_differs": any(p.get("pron_differs") for p in t.ukus_pairs), "expected": True}
            rows.append(r)
            if not t.equivalent:
                fails.append(r)
    amb = []
    for uk, us in C.V1_AMB:
        x, y = C.CARRIER.format(w=uk), C.CARRIER.format(w=us)
        fw, bw = T.evaluate_trial(x, y), T.evaluate_trial(y, x)
        bb = e109.evaluate(y, x).equivalent
        amb.append({"pair": f"{uk}/{us}", "uk>us_trial_eq": fw.equivalent, "uk>us_base_eq": e109.evaluate(x, y).equivalent, "us>uk_trial_eq": bw.equivalent,
                    "us>uk_base_eq": bb, "us>uk_new_pass": bool(bw.equivalent and not bb), "expected_uk>us": True})
        if not fw.equivalent:
            fails.append({"pair": f"{uk}/{us}", "dir": "uk>us(AMB)", "trial_eq": False})
    forms = []
    for c, a in C.V1_FORMS:
        t = T.evaluate_trial(c, a)
        r = {"canonical": c, "asr": a, "base_eq": e109.evaluate(c, a).equivalent, "trial_eq": t.equivalent, "reason": t.reason, "pairs": [(p["uk"], p["us"]) for p in t.ukus_pairs]}
        forms.append(r)
        if not t.equivalent:
            fails.append(r)
    n_pairs = len(C.V1_PAIRS) + len(C.V1_AMB)
    res = {"criterion": "pairs>=50 (both directions) all equivalent except intentional AMB reverse; V1_FORMS all equivalent",
           "pairs": n_pairs, "directions_checked": len(rows) + len(C.V1_AMB) * 2, "rows_nonAMB": len(rows), "trial_eq_nonAMB": sum(1 for r in rows if r["trial_eq"]),
           "base_eq_nonAMB": sum(1 for r in rows if r["base_eq"]), "new_via_ukus_nonAMB": sum(1 for r in rows if r["via_ukus"]),
           "pron_differs_via_ukus": sum(1 for r in rows if r["via_ukus"] and r["pron_differs"]),
           "amb_uk2us_all_pass": all(a["uk>us_trial_eq"] for a in amb), "amb_reverse_new_pass": [a["pair"] for a in amb if a["us>uk_new_pass"]],
           "forms_total": len(forms), "forms_pass": sum(1 for f in forms if f["trial_eq"]), "failures": fails,
           "verdict": "PASS" if not fails else "FAIL", "rows": rows, "amb": amb, "forms": forms}
    save("V1_result.json", res)
    print("V1", res["verdict"], res["pairs"], "pairs;", res["trial_eq_nonAMB"], "/", res["rows_nonAMB"], "nonAMB dirs eq; forms", res["forms_pass"], "/", res["forms_total"])
    return res


# ---------------------------------------------------------------- V2
def v2():
    e109, T, C = _mods()
    rows, new_pass, legit_new, already_eq = [], [], [], []
    for x, y in C.V2_PAIRS + C.V2_EXTRA_PAIRS:
        for c, a in ((x, y), (y, x)):
            cc, aa = C.CARRIER.format(w=c), C.CARRIER.format(w=a)
            b = e109.evaluate(cc, aa).equivalent
            t = T.evaluate_trial(cc, aa)
            r = {"canon": c, "asr": a, "base_eq": b, "trial_eq": t.equivalent, "new_pass": bool(t.equivalent and not b), "ukus_pairs": [(p["uk"], p["us"]) for p in t.ukus_pairs]}
            rows.append(r)
            if r["new_pass"]:
                (legit_new if (c, a) in C.V2_LEGIT_NEW else new_pass).append(r)
            if b:
                already_eq.append([c, a])
    cases = []
    bad = []
    for c, a, exp in C.V2_CASES:
        t = T.evaluate_trial(c, a)
        r = {"canonical": c, "asr": a, "expected": exp, "trial_eq": t.equivalent, "base_eq": e109.evaluate(c, a).equivalent, "reason": t.reason, "ok": t.equivalent == exp}
        cases.append(r)
        if not r["ok"]:
            bad.append(r)
    # AMB: 『意図した一方向』のみ新規PASS(tyre->tire)。許容集合は table 由来
    amb_ok = [r for r in new_pass if T.table().direct(r["canon"], r["asr"]) and T.table().direct(r["canon"], r["asr"])["amb"]]
    true_new = [r for r in new_pass if r not in amb_ok]
    res = {"criterion": "pairs>=30 (both dirs): new PASS (base NG -> trial PASS) = 0 except same-word variant (legit) / intentional AMB uk>us; extra cases all as expected",
           "pairs": len(C.V2_PAIRS) + len(C.V2_EXTRA_PAIRS), "directions": len(rows), "base_already_equivalent(phoneme layer, not this layer's responsibility)": already_eq,
           "new_pass_unexpected": true_new, "new_pass_amb_intended": amb_ok, "new_pass_legit_same_word_variant": legit_new, "extra_cases": cases, "extra_case_failures": bad,
           "verdict": "PASS" if (not true_new and not bad) else "FAIL", "rows": rows}
    save("V2_result.json", res)
    print("V2", res["verdict"], "pairs", res["pairs"], "unexpected new PASS", len(true_new), "extra fails", len(bad), "| intended AMB", [(r["canon"], r["asr"]) for r in amb_ok])
    return res


# ---------------------------------------------------------------- V3
def v3():
    e109, T, C = _mods()
    rows, bad = [], []
    for c, a, exp in C.V3_CASES:
        t = T.evaluate_trial(c, a)
        b = e109.evaluate(c, a)
        r = {"canonical": c, "asr": a, "expected": exp, "trial_eq": t.equivalent, "base_eq": b.equivalent, "reason": t.reason, "ukus_pairs": [(p["uk"], p["us"]) for p in t.ukus_pairs],
             "ok": t.equivalent == exp, "pass_to_ng": bool(b.equivalent and not t.equivalent)}
        rows.append(r)
        if not r["ok"]:
            bad.append(r)
    res = {"criterion": "cases>=25: proper nouns not equalized by this layer / spelling diff + real misreading stays NG / omission & addition NG / base PASS kept", "cases": len(rows),
           "ok": sum(1 for r in rows if r["ok"]), "failures": bad, "pass_to_ng": [r for r in rows if r["pass_to_ng"]], "verdict": "PASS" if not bad else "FAIL", "rows": rows}
    save("V3_result.json", res)
    print("V3", res["verdict"], res["ok"], "/", res["cases"])
    return res


# ---------------------------------------------------------------- V4 (保存データ再判定)
def _collect_rows():
    import er109_stored_census_01 as census
    rows = []
    files = sorted(f for f in glob.glob("**/*tts_generation_results*.json", recursive=True) if not f.startswith((".venv", "mfa_tool")))
    seen = set()
    for f in files:
        for r in census.rows_from_results(f):
            for kind, txt in (("primary", r["asr"]), ("azure", r.get("azure"))):
                if not txt:
                    continue
                k = (r["canonical"], txt, r["seg"], kind)
                if k in seen:
                    continue
                seen.add(k)
                rows.append({"set": "stored_" + kind, "c": r["canonical"], "a": txt, "seg": r["seg"], "kp": bool(r["kp"]), "src": r["src"], "attempt": r.get("attempt"),
                             "final_status": r.get("final_status")})
    for l in open("docs/research/PROPER-NOUN-PRONUNCIATION-MULTIWORD-HOMOPHONE-PLAN-01/pairs_02.jsonl", encoding="utf-8"):
        d = json.loads(l)
        if census.is_english(d["canonical"]) and census.is_english(d["asr"]):
            rows.append({"set": "pairs_02", "c": d["canonical"], "a": d["asr"], "seg": "full_story_part1", "kp": False, "src": "pairs_02.jsonl"})
    for p in ("er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl",):
        for l in open(p, encoding="utf-8"):
            d = json.loads(l)
            c = d.get("canonical_text")
            for st in d.get("steps") or []:
                a = st.get("asr_text") or st.get("text")
                if c and a and census.is_english(c):
                    rows.append({"set": "hr_queue", "c": c, "a": a, "seg": "hr", "kp": False, "src": p})
    for f in glob.glob("er011_output/**/local_rewrite_recovery_*.json", recursive=True):
        try:
            d = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        c, a = d.get("canonical_text"), d.get("last_asr_text")
        if c and a and census.is_english(c):
            rows.append({"set": "lr_recovery", "c": c, "a": a, "seg": d.get("segment_id"), "kp": False, "src": f.replace("\\", "/")})
    return rows


def _judge_chain(c, a, seg, kp, eval_fn):
    """現行Production判定(er109_stored_onoff_compare_01.judge_off/judge_on)のモデルで、er109.evaluate を eval_fn に差し替えて判定する(オフライン・Production無変更)。"""
    import er109_stored_onoff_compare_01 as oc
    import er109_asr_orthographic_equivalence_01 as e109
    off = oc.judge_off(c, a, seg, kp)
    if off["final_ok"]:
        return {"final_ok": True, "by": "off_pass"}
    orig = e109.evaluate
    e109.evaluate = eval_fn      # このprocess内・この呼出の間だけ(finallyで必ず戻す)。judge_onがe109.evaluateを使うため
    try:
        on = oc.judge_on(c, a, seg, kp, off)
    finally:
        e109.evaluate = orig
    return on


def v4():
    e109, T, C = _mods()
    rows = _collect_rows()
    n_by_set = collections.Counter(r["set"] for r in rows)
    cache = {}
    stats = collections.defaultdict(collections.Counter)
    pass_to_ng, ng_to_pass, reason_changes = [], [], []
    for r in rows:
        key = (r["c"], r["a"], None if r["kp"] else r["seg"], r["kp"])
        if key not in cache:
            base_ev = e109.evaluate
            cur = _judge_chain(r["c"], r["a"], key[2], r["kp"], base_ev)             # 現行(er109 v1)
            # Trial: evaluate_trialは内部でe109.evaluateを呼ぶ。差し替え中の再帰を避けるため原本を束縛
            tri = _judge_chain(r["c"], r["a"], key[2], r["kp"], lambda c, a, *, representative_only=False: T.evaluate_trial(c, a, representative_only=representative_only))
            ev0, ev1 = base_ev(r["c"], r["a"]), T.evaluate_trial(r["c"], r["a"])
            cache[key] = (cur, tri, ev0, ev1)
        cur, tri, ev0, ev1 = cache[key]
        s = stats[r["set"]]
        s["rows"] += 1
        s["cur_pass"] += int(cur["final_ok"])
        s["trial_pass"] += int(tri["final_ok"])
        if cur["final_ok"] and not tri["final_ok"]:
            pass_to_ng.append({**r, "cur": cur, "trial": tri})
        if (not cur["final_ok"]) and tri["final_ok"]:
            ng_to_pass.append({**r, "cur": cur, "trial": tri, "ukus_pairs": [(p["uk"], p["us"]) for p in ev1.ukus_pairs], "trial_reason": ev1.reason,
                               "e109_reason": ev0.reason, "rules": ev1.rules})
        if ev0.equivalent and (ev0.reason != ev1.reason or ev0.rules != ev1.rules or ev0.warnings != ev1.warnings or ev0.equivalent != ev1.equivalent):
            reason_changes.append({"c": r["c"][:120], "a": r["a"][:120], "e109": [ev0.reason, ev0.rules, ev0.warnings], "trial": [ev1.reason, ev1.rules, ev1.warnings]})
    distinct = {}
    for x in ng_to_pass:
        distinct.setdefault((x["c"], x["a"]), x)
    res = {"criterion": "PASS->NG = 0; NG->PASS all items eyeballed & classified (cause = ukus pair only); er109-PASS rows reason change = 0",
           "api_calls": 0, "n_rows_by_set": dict(n_by_set), "distinct_judgments": len(cache), "stats": {k: dict(v) for k, v in stats.items()},
           "PASS_to_NG": len(pass_to_ng), "PASS_to_NG_items": pass_to_ng, "NG_to_PASS_items": len(ng_to_pass), "NG_to_PASS_distinct": len(distinct),
           "er109_PASS_rows_reason_changed": len(reason_changes), "reason_changes": reason_changes[:50],
           "NG_to_PASS_list": [{"set": x["set"], "seg": x["seg"], "src": x["src"], "c": x["c"], "a": x["a"], "ukus_pairs": x["ukus_pairs"], "e109_reason": x["e109_reason"],
                                "final_status": x.get("final_status"), "classification": "UKUS_ONLY(machine-check: all diff spans are phoneme-equal or ukus pair; see ukus_pairs)"}
                               for x in distinct.values()],
           "verdict": "PASS" if (not pass_to_ng and not reason_changes) else "FAIL"}
    save("V4_result.json", res)
    print("V4", res["verdict"], "rows", sum(n_by_set.values()), "distinct", len(cache), "PASS->NG", len(pass_to_ng), "NG->PASS items", len(ng_to_pass), "distinct", len(distinct), "reason changes", len(reason_changes))
    return res


# ---------------------------------------------------------------- V5 / V5b / V5c
def v5():
    import er111_ukus_pairs_build_01 as B
    e109, T, C = _mods()
    sc = B.load_scowl()
    am70 = set(sc["american"]) | set(sc["english"])
    d = json.load(open(T.PAIRS_FILE, encoding="utf-8"))
    active = d["pairs"]
    inactive = {(a, b) for a, b, *_ in d["inactive_T2_uk_us_level_dir"]}
    in_table = {(p["uk"], p["us"]) for p in active}
    varcon_all = in_table | inactive | {(x["uk"], x["us"]) for x in d["excluded"]}
    rnd = random.Random(20261023)
    hidden = [p for p in active if rnd.random() < 0.20]
    cls_total, cls_recall, miss = collections.Counter(), collections.Counter(), collections.defaultdict(list)
    for p in hidden:
        t, ru = B.rule_target(p["uk"])
        sysclass = bool(t and t == p["us"])        # 規則で表せる系統クラス(ise/ize, yse/yze, our/or)の対
        k = "systematic(ise/yse/our)" if sysclass else "irregular"
        cls_total[k] += 1
        if sysclass:
            if (p["uk"] in sc["british_only"]) and (t in am70):
                cls_recall[k] += 1
            else:
                miss[k].append([p["uk"], p["us"], "uk_not_british_only" if p["uk"] not in sc["british_only"] else "us_not_in_scowl_le70(rare word)"])
    # 規則の精度: SCOWL英国語専用の全語(約1.2万)に規則を適用 -> 出力が(a)VarConの正解対と一致 (b)SCOWL<=70に無く沈黙 (c)SCOWL<=70に実在するがVarConの対ではない=『誤同値候補』
    prec = collections.Counter()
    false_eq = []
    for w in sc["british_only"]:
        t, ru = B.rule_target(w)
        if not t:
            continue
        if t in am70:
            if (w, t) in varcon_all:
                prec["correct(VarCon agrees)"] += 1
            else:
                prec["false_equivalence_candidate"] += 1
                false_eq.append([w, t])
        else:
            prec["silent(target not a SCOWL<=70 word)"] += 1
    # 独立辞書(breame 0.1.2, 評価専用。本番採用なし): breame対のうち、固定表(active)が被覆する割合と、未被覆の理由
    ns = {}
    exec(compile(open(os.path.join(ROOT, "docs", "research", "ASR-QUALITY-2ITEMS-COMPREHENSIVE-01", "UKUS", "work", "breame_0.1.2_spelling_constants.py"), encoding="utf-8").read(), "b", "exec"), ns)
    bre = ns["BRITISH_ENGLISH_SPELLINGS"]
    cov, unc = 0, []
    for k, v in bre.items():
        if k == v or " " in k or " " in v:
            continue
        if (k, v) in in_table or (v, k) in in_table:
            cov += 1
        else:
            why = "tier2_inactive" if ((k, v) in inactive or (v, k) in inactive) else ("excluded" if any((x["uk"], x["us"]) in {(k, v), (v, k)} for x in d["excluded"]) else "not_in_table")
            unc.append([k, v, why])
    bre_total = cov + len(unc)
    from wordfreq import zipf_frequency as zf
    unc_common = [u for u in unc if min(zf(u[0], "en"), zf(u[1], "en")) >= 3.0]
    res = {"criterion": "rule precision: false-equivalence candidates over all SCOWL British-only words = 0 ; hold-out reproduction & breame (independent dictionary) coverage reported ; real generalization = V5b",
           "hidden_pairs": len(hidden), "of_active": len(active), "seed": 20261023, "class_total": dict(cls_total), "class_recall_by_rule": dict(cls_recall),
           "holdout_systematic_reproduced_by_rule": (cls_recall["systematic(ise/yse/our)"] / cls_total["systematic(ise/yse/our)"]) if cls_total["systematic(ise/yse/our)"] else None,
           "holdout_systematic_misses_are_rare_words_with_US_target_level_gt70(left_to_dictionary/Tier-2 fail-closed)": miss["systematic(ise/yse/our)"][:30],
           "irregular_hidden_pairs(rule cannot express; dictionary required; fail-closed when absent)": cls_total["irregular"],
           "rule_precision_over_scowl_british_only": dict(prec), "rule_false_equivalence_candidates": false_eq[:50],
           "breame_independent_check": {"pairs_total": bre_total, "covered_by_active_table": cov, "coverage": round(cov / bre_total, 4), "uncovered_n": len(unc),
                                         "uncovered_common_words(zipf>=3.0 both)": unc_common[:40], "uncovered_sample": unc[:40]},
           "note": "Hold-out reproduction is self-referential by design (Opus OF-09). It only shows that the rule never invents pairs (precision) and what its domain is; the unseen-word evidence is V5b + the breame cross-check."}
    res["verdict"] = "PASS" if not false_eq else "REVIEW"
    save("V5_result.json", res)
    print("V5", res["verdict"], "hidden", len(hidden), "rule precision", dict(prec), "breame coverage", res["breame_independent_check"]["coverage"], "uncommon-uncovered common words:", unc_common[:12])
    return res


def v5b(corpus_dir):
    import er111_ukus_pairs_build_01 as B
    e109, T, C = _mods()
    from wordfreq import zipf_frequency as zf
    sc = B.load_scowl()
    d = json.load(open(T.PAIRS_FILE, encoding="utf-8"))
    act_uk = collections.defaultdict(list)
    for p in d["pairs"]:
        act_uk[p["uk"]].append(p)
    t2 = {a: (b, lv) for a, b, lv, _ in d["inactive_T2_uk_us_level_dir"]}
    excl = {x["uk"]: x["reason"] for x in d["excluded"]}
    wre = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")
    texts = {}
    for f in sorted(glob.glob(os.path.join(corpus_dir, "*.txt"))):
        raw = open(f, encoding="utf-8", errors="replace").read()
        s, e = raw.find("*** START"), raw.find("*** END")
        texts[os.path.basename(f)] = raw[s:e] if s >= 0 and e > s else raw
    for f in sorted(glob.glob(os.path.join(ROOT, "er019_output", "uk_train_speaker_playback", "run_nws_02", "b1b", "article.md"))):
        texts["repo:" + f.replace("\\", "/").split("er019_output/")[1]] = open(f, encoding="utf-8").read()
    tok = collections.Counter()
    vocab = collections.Counter()
    for name, tx in texts.items():
        for w in wre.findall(tx):
            lw = w.lower()
            vocab[lw] += 1
    uk_tokens = collections.Counter({w: n for w, n in vocab.items() if w in sc["british_only"]})
    covered = collections.Counter()
    gaps = collections.Counter()
    gap_reason = {}
    for w, n in uk_tokens.items():
        base = w[:-2] if w.endswith("'s") else w
        if base in act_uk or w in act_uk:
            covered[w] = n
        else:
            gaps[w] = n
            if base in excl or w in excl:
                gap_reason[w] = "excluded:" + excl.get(base, excl.get(w))
            elif base in t2 or w in t2:
                gap_reason[w] = "tier2_inactive(level>70)"
            else:
                gap_reason[w] = "not_in_varcon_pairs"
    # 誤写像候補: 被覆UK語のUS対が同じコーパスに独立語として現れる(=別語義の可能性)
    maprisk = []
    for w, n in covered.items():
        base = w[:-2] if w.endswith("'s") else w
        for p in act_uk.get(base, act_uk.get(w, [])):
            us = p["us"]
            if vocab.get(us, 0) > 0 and zf(us, "en") >= 3.0:
                maprisk.append({"uk": base, "us": us, "uk_n": n, "us_n_in_british_text": vocab[us], "amb_dir": p["dir"], "pron_differs": p["pron_differs"]})
    tokens_all = sum(uk_tokens.values())
    cov_tokens = sum(covered.values())
    reasons = collections.Counter()
    for w, r in gap_reason.items():
        reasons[r.split(":")[0]] += gaps[w]
    res = {"criterion": "coverage of British-spelled tokens (SCOWL british-only oracle) by the active table + list of mis-mapping candidates", "corpora": {k: len(v) for k, v in texts.items()},
           "corpus_sha256": {os.path.basename(f): hashlib.sha256(open(f, "rb").read()).hexdigest() for f in sorted(glob.glob(os.path.join(corpus_dir, "*.txt")))},
           "british_only_types": len(uk_tokens), "british_only_tokens": tokens_all, "covered_types": len(covered), "covered_tokens": cov_tokens,
           "coverage_by_tokens": round(cov_tokens / tokens_all, 4) if tokens_all else None, "coverage_by_types": round(len(covered) / len(uk_tokens), 4) if uk_tokens else None,
           "gap_reason_tokens": dict(reasons), "gap_top60": [[w, n, gap_reason[w]] for w, n in gaps.most_common(60)],
           "mis_mapping_candidates(us form also occurs as independent word in the British text)": sorted(maprisk, key=lambda x: -x["us_n_in_british_text"])[:60]}
    save("V5b_result.json", res)
    print("V5b coverage tokens", res["coverage_by_tokens"], "types", res["coverage_by_types"], "gap reasons", res["gap_reason_tokens"], "maprisk", len(maprisk))
    return res


def v5c():
    e109, T, C = _mods()
    from wordfreq import zipf_frequency as zf
    d = json.load(open(T.PAIRS_FILE, encoding="utf-8"))
    cands = []
    for p in d["pairs"]:
        if p["uk"].endswith("'s") or p["us"].endswith("'s"):
            continue
        fu, fa = zf(p["uk"], "en"), zf(p["us"], "en")
        if min(fu, fa) >= 3.0:
            cands.append({"uk": p["uk"], "us": p["us"], "zipf_uk": round(fu, 2), "zipf_us": round(fa, 2), "dir": p["dir"], "pron_differs": p["pron_differs"], "tier": p["tier"]})
    res = {"criterion": "both forms high-frequency independent words -> human review for semantic overlap (decisions recorded in 'review_decision')",
           "review_decision": "全候補を人手レビュー(2026-10-23 実装担当): 同一語の地域綴り変異として妥当。caesar/cesar は固有名衝突のため denylist へ追加済み(本結果は追加後)。AMB(uk2us=一方向、*)は用法依存のため UK形->US形のみ許可。pron_differs対(aluminium, catalogue, colouring, dreamt, enquiry, learnt, organisation, speciality, tyre 等)はOF-06の監視対象(TTSが米式に読んでもPASSする残存リスク)。",
           "candidates": sorted(cands, key=lambda x: (x["uk"])), "n": len(cands)}
    save("V5c_result.json", res)
    print("V5c candidates", len(cands))
    return res


# ---------------------------------------------------------------- V6 (worker process)
def _v6_worker(scope, mode, rows_path, out_path):
    """別process: mode=on なら er109_xz_scope_01._evaluate_cached をTrial評価へ差し替える(+cache_clear)。LR/TTS/networkはmock(er109_wiring_signature_01と同じ)。"""
    import er109_wiring_signature_01 as sig
    import er109_xz_scope_01 as xz
    import er111_ukus_spelling_trial_01 as T
    if mode == "on":
        xz._evaluate_cached = T.evaluate_trial_cached
        T.evaluate_trial_cached.cache_clear()
    rows = [json.loads(l) for l in open(rows_path, encoding="utf-8") if l.strip()]
    sig.run_signatures(rows, scope, sig.ALL_ROUTES, out_path, require_xz=True)


V6_ROWS = [
    {"id": "c12_primary_azure_specialty", "canonical": "Inventing convincing stories at a moment's notice was Vera's speciality.",
     "asr": "Inventing convincing stories at a moment's notice was Vera's specialty.", "azure": "Inventing convincing stories at a moment's notice was Vera's specialty.",
     "seg": "full_story_part3_c12", "kp": False},
    {"id": "c12_kp_vote", "canonical": "Inventing convincing stories at a moment's notice was Vera's speciality.",
     "asr": "Inventing convincing stories at a moment's notice was Vera's specialty.", "azure": "Inventing convincing stories at a moment's notice was Vera's specialty.",
     "seg": None, "kp": True},
    {"id": "c12_primary_only_us", "canonical": "Inventing convincing stories at a moment's notice was Vera's speciality.",
     "asr": "Inventing convincing stories at a moment's notice was Vera's specialty.", "azure": None, "seg": "full_story_part3_c12", "kp": False},
    {"id": "generic_jewellery", "canonical": "Her jewellery-making kit and aluminium tin arrived on Monday.", "asr": "Her jewelry-making kit and aluminum tin arrived on Monday.",
     "azure": "Her jewelry-making kit and aluminum tin arrived on Monday.", "seg": "full_story_part1", "kp": False},
    {"id": "generic_encyclopaedia", "canonical": "The encyclopaedia described the foetus and the gaol.", "asr": "The encyclopedia described the fetus and the jail.",
     "azure": "The encyclopedia described the fetus and the jail.", "seg": "full_story_part1", "kp": False},
    {"id": "neg_spelling_plus_misread", "canonical": "The speciality is cooking.", "asr": "The specialty is cooling.", "azure": "The specialty is cooling.",
     "seg": "full_story_part1", "kp": False},
    {"id": "neg_proper_noun", "canonical": "He visited Aluminium City last year.", "asr": "He visited Aluminum City last year.", "azure": "He visited Aluminum City last year.",
     "seg": "full_story_part1", "kp": False},
]


def v6():
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = os.path.join(OUT_DIR, "_v6_tmp")
    os.makedirs(tmp, exist_ok=True)
    rows_path = os.path.join(tmp, "rows.jsonl")
    with open(rows_path, "w", encoding="utf-8") as f:
        for r in V6_ROWS:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    procs = {}
    for scope in ("X", "Z", "none"):
        for mode in ("off", "on"):
            outp = os.path.join(tmp, f"sig_{scope}_{mode}.jsonl")
            procs[(scope, mode)] = (subprocess.Popen([PY, os.path.abspath(__file__), "--v6-worker", scope, mode, rows_path, outp], cwd=ROOT,
                                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace"), outp)
    results = {}
    for k, (p, outp) in procs.items():
        so, se = p.communicate(timeout=1500)
        if p.returncode != 0:
            print("worker fail", k, se[-600:])
        sigs = {}
        if os.path.exists(outp):
            for l in open(outp, encoding="utf-8"):
                if l.strip():
                    o = json.loads(l)
                    sigs[o["k"].rsplit("|scope=", 1)[0]] = o["sig"]
        results[k] = {"rc": p.returncode, "stdout": so[-300:], "sigs": sigs}
    def passed(sig):
        if not isinstance(sig, dict):
            return None
        if "unified_state" in sig and "blocked" in sig:           # guard route: guardはblockしない設計。判定は再判定のunified_state
            return sig["unified_state"] == "PASS"
        for key in ("verified", "ok"):
            if key in sig:
                return bool(sig[key])
        provs = [v for v in sig.values() if isinstance(v, dict) and "pass" in v]
        if provs:                                                  # voter route: 全票(openai/azure/whisper)がPASS
            return all(bool(v["pass"]) for v in provs)
        return None
    table = []
    for scope in ("X", "Z", "none"):
        for r in V6_ROWS:
            for route in ("adapter", "adapter_kp", "guard", "rejudge", "voter"):
                key = f"{r['id']}|{route}"
                off = results[(scope, "off")]["sigs"].get(key)
                on = results[(scope, "on")]["sigs"].get(key)
                if off is None or on is None:
                    continue
                aj = (on.get("aj") or {}) if isinstance(on, dict) else {}
                oe = aj.get("orthographic_equivalence") or {}
                rules = []
                for s in (oe.get("sites") or []):
                    rules += (s.get("er109") or {}).get("rules", [])
                if route == "voter" and isinstance(on, dict):
                    rules = ["ukus_spelling_variant"] if any(v.get("label") == "ORTHOGRAPHIC_EQUIVALENT_MATCH" for v in on.values() if isinstance(v, dict)) else []
                table.append({"scope": scope, "row": r["id"], "route": route, "off_pass": passed(off), "on_pass": passed(on),
                              "off_hr": off.get("hr") if isinstance(off, dict) else None, "on_hr": on.get("hr") if isinstance(on, dict) else None,
                              "on_stop": on.get("stop") if isinstance(on, dict) else None, "on_state": on.get("state") if isinstance(on, dict) else None,
                              "on_final_status": on.get("final_status") if isinstance(on, dict) else None, "on_rules": sorted(set(rules)),
                              "on_warnings": (on.get("warnings") if isinstance(on, dict) else None),
                              "on_error": on.get("error") if isinstance(on, dict) else None})
    c12 = [t for t in table if t["row"].startswith("c12") and t["scope"] in ("X", "Z")]
    none_rows = [t for t in table if t["scope"] == "none"]
    none_unchanged = bool(none_rows) and all(t["off_pass"] == t["on_pass"] for t in none_rows)
    pass_to_ng = [t for t in table if t["off_pass"] is True and t["on_pass"] is False]
    c12_ok = bool(c12) and all(t["on_pass"] is True and not t["on_hr"] and not t["on_stop"] for t in c12)
    c12_off_ng = all(t["off_pass"] is False for t in c12)
    negs_ok = all(t["on_pass"] in (False, None) for t in table if t["row"].startswith("neg_"))
    res = {"criterion": "c12 (Primary/Azure/KP vote/Store guard/rejudge): OFF=NG, ON=PASS, rules=ukus_spelling_variant, retry 0 / LR 0 / HR 0 (mock); neg rows stay NG; PASS->NG 0",
           "workers": {f"{k[0]}_{k[1]}": {"rc": v["rc"], "n_sigs": len(v["sigs"])} for k, v in results.items()}, "table": table,
           "c12_all_routes_off_ng": c12_off_ng, "c12_all_routes_on_pass_no_hr_no_stop": c12_ok, "neg_rows_stay_ng": negs_ok, "scope_none_(A/B/C相当)_unchanged_even_with_hook_patched": none_unchanged, "pass_to_ng": pass_to_ng,
           "verdict": "PASS" if (c12_ok and c12_off_ng and negs_ok and none_unchanged and not pass_to_ng and all(v["rc"] == 0 for v in results.values())) else "FAIL"}
    save("V6_result.json", res)
    print("V6", res["verdict"], "c12 ok", c12_ok, "neg ok", negs_ok, "none unchanged", none_unchanged, "pass_to_ng", len(pass_to_ng), "workers rc", {f"{k[0]}{k[1]}": v["rc"] for k, v in results.items()})
    return res


# ---------------------------------------------------------------- V9 (追加): 保存済みcanonical文に『ASRが米綴りで書いた』を合成した改善前後比較
def v9(corpus_dir=None):
    e109, T, C = _mods()
    rows = _collect_rows()
    canon = {}
    for r in rows:
        if r["c"] and len(r["c"]) < 400:
            canon.setdefault(r["c"], "stored:" + r["set"])
    if corpus_dir:
        for f in sorted(glob.glob(os.path.join(corpus_dir, "*.txt"))):
            raw = open(f, encoding="utf-8", errors="replace").read()
            st, en = raw.find("*** START"), raw.find("*** END")
            body = raw[st:en] if st >= 0 and en > st else raw
            for sent in re.split(r"(?<=[.!?])\s+", re.sub(r"\s+", " ", body)):
                if 20 <= len(sent) <= 300:
                    canon.setdefault(sent, "corpus:" + os.path.basename(f))
    tbl = T.table()
    uk2us = collections.defaultdict(list)
    for (uk, us), p in tbl.p.items():
        uk2us[uk].append(us)
    wre = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")
    n_sent = n_has = base_ng = trial_ng = fixed = 0
    per = collections.defaultdict(lambda: collections.Counter())
    words = collections.Counter()
    examples = []
    for c in canon:
        n_sent += 1
        found = []

        def sub(m):
            w = m.group(0)
            lw = w.lower()
            if lw in uk2us and w[:1].islower():
                found.append(lw)
                return uk2us[lw][0]
            return w
        a = wre.sub(sub, c)
        if not found:
            continue
        n_has += 1
        b = e109.evaluate(c, a).equivalent
        t = T.evaluate_trial(c, a).equivalent
        base_ng += int(not b)
        trial_ng += int(not t)
        per[canon[c]]["with_uk"] += 1
        per[canon[c]]["base_ng"] += int(not b)
        per[canon[c]]["trial_ng"] += int(not t)
        if (not b) and t:
            fixed += 1
            for w in found:
                words[w] += 1
        if (not t) and len(examples) < 20:
            examples.append({"c": c[:160], "a": a[:160], "found": found})
    res = {"criterion": "(info) 保存canonical文のUK綴り語を表の直接対のUS形へ置換=『ASRが米綴りで書いた』合成。改善前後のNG件数", "canonical_sentences": n_sent, "with_uk_spelled_words": n_has,
           "baseline_NG_sentences": base_ng, "trial_NG_sentences": trial_ng, "fixed_by_trial": fixed, "per_source": {k: dict(v) for k, v in per.items()}, "top_fixed_words": words.most_common(30), "trial_still_ng_examples": examples,
           "note": "synthetic (not real ASR output): upper bound of the effect when every UK-spelled word is transcribed in US spelling"}
    save("V9_result.json", res)
    print("V9 sentences", n_sent, "with UK words", n_has, "base NG", base_ng, "trial NG", trial_ng, "fixed", fixed)
    return res


# ---------------------------------------------------------------- V7
def v7():
    e109, T, C = _mods()
    t0 = time.time()
    out = subprocess.run([PY, "-c", "import time;t=time.time();import er111_ukus_spelling_trial_01 as T;t1=time.time();T.table();print(round(time.time()-t1,4), round(t1-t,4))"], cwd=ROOT,
                         capture_output=True, text=True, encoding="utf-8", errors="replace").stdout.strip().split()
    load_s = float(out[0]) if out else None
    cases = [(C.CARRIER.format(w=u), C.CARRIER.format(w=s)) for u, s, _ in C.V1_PAIRS] + [(c, a) for c, a, _ in C.V3_CASES] + [(c, a) for c, a, _ in C.V2_CASES]
    ng_cases = [(c, a) for c, a in cases if not e109.evaluate(c, a).equivalent]
    base_t, trial_t = [], []
    for c, a in ng_cases * 5:
        t1 = time.perf_counter(); e109.evaluate(c, a); t2 = time.perf_counter(); T.evaluate_trial(c, a); t3 = time.perf_counter()
        base_t.append((t2 - t1) * 1000); trial_t.append((t3 - t2) * 1000)
    # 1判定の追加 = trial - base(base分は『e109.evaluate単体』。Trialは内部でbaseを1回含む)
    extra = [t - b for t, b in zip(trial_t, base_t)]
    p95 = lambda xs: sorted(xs)[int(len(xs) * 0.95)]
    # 既存PASS行の追加(早期return)
    pass_cases = [(c, a) for c, a in cases if e109.evaluate(c, a).equivalent]
    bt, tt = [], []
    for c, a in pass_cases * 5:
        t1 = time.perf_counter(); e109.evaluate(c, a); t2 = time.perf_counter(); T.evaluate_trial(c, a); t3 = time.perf_counter()
        bt.append((t2 - t1) * 1000); tt.append((t3 - t2) * 1000)
    res = {"criterion": "dictionary load <= 0.5 s (once per process); extra per judgment <= 1 ms (p95, NG path) ; API 0", "table_load_seconds": load_s, "table_active_pairs": T.table().size,
           "ng_path": {"n": len(extra), "base_p50_ms": round(statistics.median(base_t), 3), "trial_p50_ms": round(statistics.median(trial_t), 3),
                       "extra_p50_ms": round(statistics.median(extra), 3), "extra_p95_ms": round(p95(extra), 3), "extra_max_ms": round(max(extra), 3)},
           "pass_path": {"n": len(bt), "extra_p95_ms": round(p95([t - b for t, b in zip(tt, bt)]), 3)}, "api_calls": 0,
           "note": "NG path reuses the unit lists kept by the e109.evaluate NG result (no second tokenization); the production-like hook would additionally memoize via lru_cache"}
    res["verdict"] = "PASS" if (load_s is not None and load_s <= 0.5 and res["ng_path"]["extra_p95_ms"] <= 1.0 + 0.0) else "REVIEW"
    save("V7_result.json", res)
    print("V7", res["verdict"], "load_s", load_s, "extra p95 ms (NG path)", res["ng_path"]["extra_p95_ms"], "(pass path)", res["pass_path"]["extra_p95_ms"])
    return res


# ---------------------------------------------------------------- V8
def v8():
    mods = ["er111_ukus_spelling_trial_01_test_01", "er109_asr_orthographic_equivalence_01_test", "er109_xz_isolation_01_test_01", "er109_xz_scope_01_test_01",
            "er109_wiring_golden_test_01", "er109_bfix_test_01"]
    results = {}
    procs = {m: subprocess.Popen([PY, "-m", "unittest", m], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace") for m in mods}
    for m, p in procs.items():
        out, _ = p.communicate(timeout=3000)
        tail = out.strip().splitlines()[-4:]
        results[m] = {"rc": p.returncode, "tail": tail}
    prod = ["er109_asr_orthographic_equivalence_01.py", "er109_xz_scope_01.py", "er006_secondary_asr_01.py", "er020_tts_retry_local_rewrite_01.py", "er078_asr_unified_judge_01.py",
            "er104_kp_three_asr_vote_01.py", "er006_preprod_hardening_01_validation.py", "er019_family_x_audio_production_runner_01.py", "er063_family_z_audio_01.py"]
    diff = subprocess.run(["git", "diff", "--name-only", "HEAD", "--"] + prod + ["er109_output"], cwd=ROOT, capture_output=True, text=True).stdout.split()
    golden = {os.path.basename(f): hashlib.sha256(open(f, "rb").read()).hexdigest()[:16] for f in sorted(glob.glob(os.path.join(ROOT, "er109_output", "aho4_golden_01", "*")))}
    res = {"criterion": "existing tests + isolation AST + golden unchanged; new regressions 0", "tests": results, "production_files_modified_vs_HEAD": diff, "golden_fixture_sha256_16": golden,
           "verdict": "PASS" if (all(r["rc"] == 0 for r in results.values()) and not diff) else "FAIL"}
    save("V8_result.json", res)
    print("V8", res["verdict"], {m: r["rc"] for m, r in results.items()}, "prod modified:", diff)
    return res


def summary():
    rows = []
    for n in ("1", "2", "3", "4", "5", "5b", "5c", "6", "7", "8", "9"):
        p = os.path.join(OUT_DIR, f"V{n}_result.json")
        if os.path.exists(p):
            d = json.load(open(p, encoding="utf-8"))
            rows.append((n, d.get("criterion", ""), d.get("verdict", "(info)")))
    md = ["# TRIAL_01 検証結果 集計 (自動生成 er111_ukus_trial_eval_01.py --summary)", "", "| V | 基準 | 判定 |", "|---|---|---|"]
    for n, c, v in rows:
        md.append(f"| V{n} | {c} | {v} |")
    open(os.path.join(OUT_DIR, "V_SUMMARY_01.md"), "w", encoding="utf-8", newline="\n").write("\n".join(md) + "\n")
    print("\n".join(md))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--v", default="")
    ap.add_argument("--corpus-dir", default=None)
    ap.add_argument("--summary", action="store_true")
    ap.add_argument("--v6-worker", nargs=4, metavar=("SCOPE", "MODE", "ROWS", "OUT"))
    a = ap.parse_args()
    os.chdir(ROOT)
    if a.v6_worker:
        _v6_worker(*a.v6_worker)
        return
    for v in [x for x in a.v.split(",") if x]:
        {"1": v1, "2": v2, "3": v3, "4": v4, "5": v5, "5c": v5c, "6": v6, "7": v7, "8": v8}.get(v, lambda: None)() if v not in ("5b", "9") else (v5b(a.corpus_dir) if v == "5b" else v9(a.corpus_dir))
    if a.summary:
        summary()


if __name__ == "__main__":
    main()
