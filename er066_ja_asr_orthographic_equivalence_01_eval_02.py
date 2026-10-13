# JA-ASR-ORTHOGRAPHIC-EQUIVALENCE-COMPREHENSIVE-01 委任_02: オフライン再Trial(¥0、ASR再呼出なし)
# 入力: harvest_raw_01.json(委任_01で収集済みの実転写1,002ペア)+ cases_01 + cases_02
# 列: Before(現行Production相当) / Stage1 / Stage1'(S1+S1') / Stage2(S1+S1'+S2) の累積3列
import collections
import json
import re
import sys

sys.path.insert(0, ".")
import er066_ja_asr_orthographic_equivalence_01_trial as trial
import er066_ja_asr_orthographic_equivalence_01_cases as cases1
import er066_ja_asr_orthographic_equivalence_01_cases_02 as cases2
import er066_ja_asr_orthographic_equivalence_01_eval as ev01

OUT = "er066_output/ja_asr_orthographic_equivalence_01"
STAGES = ("S1", "S1P", "S2")
# 真値確認済み: asr_root_cause_01/pre_regen_backup由来のユニーク1組(HR承認済み、ユーザー試聴で問題なし)のみ。
TRUTH_SRC = "asr_root_cause_01/pre_regen_backup"


def col(tr, prod_pass, stage):
    """stage列(S1/S1P/S2)でのPASS: Production通過(取消除く) or 当該段階までの救済"""
    if tr.verdict == "VETO_PROD_PASS":
        return False
    return prod_pass or tr.rescued_at(stage)


def main():
    rows = json.load(open(f"{OUT}/harvest_raw_01.json", encoding="utf-8"))
    corpus = []
    for r in rows:
        prod = trial.prod_effective(r["canonical"], r["asr"])
        tr = trial.trial_judge(r["canonical"], r["asr"], prod)
        real = any(not ev01.SYN.search(x) for x in r["sources"])
        truth = any(TRUTH_SRC in x for x in r["sources"])
        corpus.append({"canonical": r["canonical"], "asr": r["asr"], "is_real": real, "truth_confirmed": truth,
                       "src0": r["sources"][0], "n_sources": len(r["sources"]),
                       "before_pass": prod.should_pass, "before_class": prod.classification,
                       "verdict": tr.verdict, "stage": tr.stage, "warning": tr.warning, "detail": tr.detail,
                       "spans_c": tr.spans_c, "spans_a": tr.spans_a,
                       "category": ev01.categorize(r["canonical"], r["asr"], tr),
                       "passes": {s: col(tr, prod.should_pass, s) for s in STAGES}})
    resc = [x for x in corpus if (not x["before_pass"]) and x["verdict"] in ("TRIAL_NOTATION_MATCH", "TRIAL_READING_MATCH")]
    resc_real = [x for x in resc if x["is_real"]]
    summary = {
        "corpus_pairs": len(corpus),
        "before_pass": sum(x["before_pass"] for x in corpus),
        "after_pass": {s: sum(x["passes"][s] for x in corpus) for s in STAGES},
        "vetoed_prod_pass": sum(x["before_pass"] and x["verdict"] == "VETO_PROD_PASS" for x in corpus),
        "rescued_real_by_stage_cumulative": {s: sum(1 for x in resc_real if trial.STAGE_ORDER[x["stage"]] <= trial.STAGE_ORDER[s]) for s in STAGES},
        "rescued_real_total": len(resc_real),
        "rescued_real_with_warning": sum(x["warning"] for x in resc_real),
        "rescued_real_without_warning": sum(not x["warning"] for x in resc_real),
        "rescued_real_truth_confirmed": sum(x["truth_confirmed"] for x in resc_real),
        "rescued_synthetic_fixture": sum(not x["is_real"] for x in resc),
    }
    # 真値確認件数のユニーク組数
    summary["truth_confirmed_unique_pairs"] = len({(x["canonical"], x["asr"]) for x in resc_real if x["truth_confirmed"]})
    # 合成: 正常例
    pos = []
    for c, a, k in cases1.POSITIVE + cases2.POSITIVE_02:
        prod = trial.prod_effective(c, a)
        tr = trial.trial_judge(c, a, prod)
        pos.append({"canonical": c, "asr": a, "kind": k, "before_pass": prod.should_pass, "verdict": tr.verdict,
                    "stage": tr.stage, "warning": tr.warning, "passes": {s: col(tr, prod.should_pass, s) for s in STAGES},
                    "after_pass": tr.would_pass})
    # 合成: 敵対的反例(旧35件+新規)
    neg = []
    for set_name, lst in (("v1", cases1.NEGATIVE), ("v2", cases2.NEGATIVE_02)):
        for c, a, k in lst:
            prod = trial.prod_effective(c, a)
            tr = trial.trial_judge(c, a, prod)
            neg.append({"set": set_name, "canonical": c, "asr": a, "kind": k, "before_pass": prod.should_pass,
                        "before_class": prod.classification, "before_reason": (prod.reason or "")[:80],
                        "verdict": tr.verdict, "stage": tr.stage,
                        "passes": {s: col(tr, prod.should_pass, s) for s in STAGES}, "after_pass": tr.would_pass,
                        "trial_rescued": tr.rescued})
    pb = []
    for c, a, k in cases2.PRODBUG:
        prod = trial.prod_effective(c, a)
        tr = trial.trial_judge(c, a, prod)
        pb.append({"canonical": c, "asr": a, "kind": k, "before_pass": prod.should_pass, "before_class": prod.classification,
                   "verdict": tr.verdict, "after_pass": tr.would_pass, "trial_rescued": tr.rescued})
    amb = []
    for c, a in cases2.AMBIGUITY_NO_RESCUE:
        tr = trial.trial_judge(c, a)
        amb.append({"canonical": c, "asr": a, "verdict": tr.verdict, "after_pass": tr.would_pass})
    summary.update({
        "positive_total": len(pos), "positive_before_pass": sum(p["before_pass"] for p in pos),
        "positive_after_pass_by_stage": {s: sum(p["passes"][s] for p in pos) for s in STAGES},
        "positive_warning": sum(p["warning"] for p in pos),
        "negative_total": len(neg), "negative_v1": sum(n["set"] == "v1" for n in neg), "negative_v2": sum(n["set"] == "v2" for n in neg),
        "negative_before_false_pass": sum(n["before_pass"] for n in neg),
        "negative_after_false_pass_by_stage": {s: sum(n["passes"][s] for n in neg) for s in STAGES},
        "negative_after_false_pass_total": sum(n["after_pass"] for n in neg),
        "negative_trial_rescued": sum(n["trial_rescued"] for n in neg),
        "negative_vetoed": sum(n["before_pass"] and n["verdict"] == "VETO_PROD_PASS" for n in neg),
        "prodbug_total": len(pb), "prodbug_prod_pass": sum(p["before_pass"] for p in pb),
        "prodbug_trial_rescued": sum(p["trial_rescued"] for p in pb),
        "ambiguity_total": len(amb), "ambiguity_after_pass": sum(a["after_pass"] for a in amb),
        "ambiguity_not_rescued": sum(a["verdict"] in ("AMBIGUOUS_NO_RESCUE", "NO_RESCUE") for a in amb),
    })
    # 範囲/列挙パターンのコーパス出現(normalize_ja副次発見の影響調査)
    pat = re.compile(r"\d\s*[〜~～、]\s*\d")
    summary["corpus_canonical_with_digit_separator_digit"] = sum(bool(pat.search(x["canonical"])) for x in corpus)
    json.dump({"summary": summary, "corpus": corpus, "positive": pos, "negative": neg, "prodbug": pb, "ambiguity": amb},
              open(f"{OUT}/before_after_02.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    print("--- rescued (corpus)")
    for x in resc:
        print(x["stage"], "warn" if x["warning"] else "-", "real" if x["is_real"] else "syn", "truth" if x["truth_confirmed"] else "",
              x["src0"][:60], "|", x["canonical"][:30], "|", x["asr"][:30])
    print("--- vetoed (corpus)")
    for x in corpus:
        if x["before_pass"] and x["verdict"] == "VETO_PROD_PASS":
            print(x["canonical"][:40], "|", x["asr"][:40])
    print("--- negatives passing")
    for n in neg:
        if n["after_pass"]:
            print(n["set"], n["canonical"], n["asr"], n["kind"], n["verdict"], n["before_class"], n["before_reason"])
    print("--- positives failing (after S2)")
    for p in pos:
        if not p["after_pass"]:
            print(p["canonical"], p["asr"], p["kind"], p["verdict"])
    print("--- prodbug")
    for p in pb:
        print(p["canonical"], p["asr"], p["before_class"], p["before_pass"], p["verdict"])
    print("--- ambiguity")
    for a in amb:
        print(a)


if __name__ == "__main__":
    main()
