# ukus_census_01.py -- UKUS 委任_01 §1 定量(API 0・read-only)。保存ASR転写から『英米綴り差が原因のNG/不要retry/LR/HR』を機械抽出する。
# 使い方: .venv\Scripts\python.exe docs/research/ASR-QUALITY-2ITEMS-COMPREHENSIVE-01/UKUS/work/ukus_census_01.py --out <json>
import sys, os, re, json, glob, difflib, collections, argparse
sys.path.insert(0, "."); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import er006_preprod_hardening_01_validation as val
import er006_secondary_asr_01 as S
import er109_stored_census_01 as census
import ukus_lexicon_01 as lex

UK2US, US2UK, AMB = lex.build_pair_index()
WORD = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")

def words(t): return [w.lower() for w in WORD.findall(t or "")]

def ukus_diffs(canon, asr):
    """canonical語列とASR語列のdifflib 'replace' で、(c,a) が英米対応表の対になっている箇所を返す(同一語長1:1のみ)。"""
    c, a = words(canon), words(asr)
    sm = difflib.SequenceMatcher(None, c, a, autojunk=False)
    hits, other = [], False
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal": continue
        if tag == "replace" and (i2 - i1) == (j2 - j1):
            ok = True
            for cw, aw in zip(c[i1:i2], a[j1:j2]):
                # 所有格/複数 s の差は語幹で見る
                if aw in UK2US.get(cw, ()) or cw in UK2US.get(aw, ()) :
                    hits.append((cw, aw))
                else:
                    ok = False
            if not ok: other = True
        else:
            other = True
    return hits, other

def current_pass(c, a, seg):
    cls = val.classify_asr_match(c, a, segment_id=seg)
    if cls.should_pass: return True, cls.classification
    alt = S._step_alternate_pass(cls)
    if alt: return True, str(alt)
    return False, cls.classification

def us_normalize(text):
    """全語をUS形へ(調査用の理想的な対策後シミュレーション。語境界でのみ置換)。"""
    def sub(m):
        w = m.group(0); lw = w.lower()
        if lw in UK2US:
            r = sorted(UK2US[lw])[0]
            return r.capitalize() if w[0].isupper() else r
        return w
    return WORD.sub(sub, text or "")

def collect():
    rows = []
    files = sorted(f for f in glob.glob("**/*tts_generation_results*.json", recursive=True) if not f.startswith(".venv"))
    seen = set()
    for f in files:
        for r in census.rows_from_results(f):
            for kind, txt in (("primary", r["asr"]), ("azure", r.get("azure"))):
                if not txt: continue
                k = (r["canonical"], txt, r["seg"], kind)
                if k in seen: continue
                seen.add(k)
                rows.append({"set": "stored_" + kind, "c": r["canonical"], "a": txt, "seg": r["seg"], "kp": bool(r["kp"]), "src": r["src"],
                             "attempt": r.get("attempt"), "stored_cls": r.get("stored_cls"), "verified": r.get("verified"), "final_status": r.get("final_status")})
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
                if c and a and census.is_english(c): rows.append({"set": "hr_queue", "c": c, "a": a, "seg": "hr", "kp": False, "src": p})
    for f in glob.glob("er011_output/**/local_rewrite_recovery_*.json", recursive=True):
        try: d = json.load(open(f, encoding="utf-8"))
        except Exception: continue
        c, a = d.get("canonical_text"), d.get("last_asr_text")
        if c and a and census.is_english(c):
            rows.append({"set": "lr_recovery", "c": c, "a": a, "seg": d.get("segment_id"), "kp": False, "src": f.replace("\\", "/"),
                         "lr_selected": ((d.get("selection") or {}).get("selected") or {}).get("changed_span_after")})
    return rows

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); args = ap.parse_args()
    rows = collect()
    res = collections.defaultdict(list)
    n_by_set = collections.Counter(r["set"] for r in rows)
    for r in rows:
        hits, other = ukus_diffs(r["c"], r["a"])
        if not hits: continue
        pas, lab = current_pass(r["c"], r["a"], None if r["kp"] else r["seg"])
        # 対策後シミュ: ASR側・canonical側とも US 正規化してから現行判定
        pas2, lab2 = current_pass(us_normalize(r["c"]), us_normalize(r["a"]), None if r["kp"] else r["seg"])
        res[r["set"]].append({"hits": hits, "other_diff": other, "now_pass": pas, "now_label": lab, "sim_pass": pas2, "sim_label": lab2,
                              "seg": r["seg"], "src": r["src"], "attempt": r.get("attempt"), "stored_cls": r.get("stored_cls"),
                              "c": r["c"][:300], "a": r["a"][:300], "lr": r.get("lr_selected")})
    summ = {}
    for s, L in res.items():
        summ[s] = {"rows_total": n_by_set[s], "ukus_rows": len(L), "ukus_only_diff_rows": sum(1 for x in L if not x["other_diff"]),
                   "now_NG": sum(1 for x in L if not x["now_pass"]),
                   "now_NG_and_ukus_only": sum(1 for x in L if not x["now_pass"] and not x["other_diff"]),
                   "sim_would_pass_of_now_NG": sum(1 for x in L if not x["now_pass"] and x["sim_pass"]),
                   "now_PASS_sim_NG": sum(1 for x in L if x["now_pass"] and not x["sim_pass"])}
    pairs = collections.Counter(h for L in res.values() for x in L for h in x["hits"])
    json.dump({"generated_by": "ukus_census_01.py", "api_calls": 0, "cost_jpy": 0, "n_by_set": dict(n_by_set), "summary": summ,
               "pair_counts": [[list(k), v] for k, v in pairs.most_common()], "rows": res}, open(args.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(summ, indent=1)); print(pairs.most_common(40))
main()
