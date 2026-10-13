# JA-ASR-ORTHOGRAPHIC-EQUIVALENCE-COMPREHENSIVE-01: オフライン Before/After 評価(¥0、ASR再呼出なし)
# 入力: harvest_raw_01.json(過去の実転写)+ cases_01(合成の正常例/敵対的反例)
# Before = 現行Production相当(classify_ja_asr_match + Cascade側D-2、Resolver LLM OFF)
# After  = Before + Trial層(er066_*_trial)
import collections
import difflib
import json
import re
import sys
import unicodedata

sys.path.insert(0, ".")
import er066_ja_asr_orthographic_equivalence_01_trial as trial
import er066_ja_asr_orthographic_equivalence_01_cases as cases
import er007_ja_asr_validator_01 as javal

OUT = "er066_output/ja_asr_orthographic_equivalence_01"
KANJI_NUM = set("〇零一二三四五六七八九十百千万")
LATIN = re.compile(r"[A-Za-z]")
KATA = re.compile(r"[゠-ヿ]")
# 出所がHR承認/ユーザー試聴で『実際は正しく発音されていた』と確認済みの事例(真値あり)
TRUTH_OK = {
    ("妹の結婚式に出るため3日間の猶予", "Melos Std comment_1: ユーザー試聴で問題なし、個別HR承認済み(2026-10-13)"),
}


SYN = re.compile(r"zero_yen_checks|synthetic|test_dataset|additive_|counterexample|reproduction_cases|candidate_a_dry|"
                 r"ja_local_rewrite_applicability|regression_result|regression_run|er066_output|rev[12]_|"
                 r"variant_trial_01/(results|existing)|er011_output/ja_asr_variant_trial_01/historical")


def _spans(c, a):
    c = unicodedata.normalize("NFKC", c)
    a = unicodedata.normalize("NFKC", a)
    sm = difflib.SequenceMatcher(None, c, a, autojunk=False)
    return [(c[i1:i2], a[j1:j2], t) for t, i1, i2, j1, j2 in sm.get_opcodes() if t != "equal"], sm


def categorize(c, a, tr) -> str:
    """診断用の機械分類(人手確認は代表例のみ)。"""
    cn = unicodedata.normalize("NFKC", c)
    an = unicodedata.normalize("NFKC", a)
    if len(an) > max(60, 1.8 * len(cn)) or len(re.findall(r"[A-Za-z]{3,}", an)) >= 3 and not re.findall(r"[A-Za-z]{3,}", cn):
        return "その他(ASR幻覚・プロンプト漏洩・混入)"
    diffs, sm = _spans(c, a)
    if tr.rescued:
        return "数値表記差(漢数字/算用数字・助数詞・単位)"
    if tr.verdict == "AMBIGUOUS_NO_RESCUE":
        return "数値表記差(曖昧語を含み自動救済せず)"
    if tr.spans_c or tr.spans_a:
        if tr.spans_c and tr.spans_a and sorted(tr.spans_c) != sorted(tr.spans_a):
            return "真の誤読(値/助数詞の違い)"
    if any(any(ch in KANJI_NUM or ch.isdigit() for ch in x + y) for x, y, _ in diffs):
        return "数値を含む差(他の誤読を併発または対象外)"
    if diffs and all(t == "delete" for _, _, t in diffs) or (len(an) < 0.5 * len(cn)):
        return "その他(ASR断片・脱落)"
    if any(LATIN.search(x + y) and KATA.search(x + y) for x, y, _ in diffs):
        return "外来語・固有名詞(ラテン⇔カタカナ)"
    if any(KATA.search(x) and KATA.search(y) for x, y, _ in diffs):
        return "外来語・固有名詞(カタカナ長音・促音等)"
    from_reading = tr.prod_class == "ASR_VALIDATION_UNCERTAIN"
    if from_reading:
        return "同音異表記・漢字/かな(Cascade域)"
    return "真の誤読(別語・脱落・挿入)"


def main():
    rows = json.load(open(f"{OUT}/harvest_raw_01.json", encoding="utf-8"))
    corpus = []
    for r in rows:
        prod = trial.prod_effective(r["canonical"], r["asr"])
        tr = trial.trial_judge(r["canonical"], r["asr"], prod)
        is_real = any(not SYN.search(x) for x in r["sources"])
        corpus.append({"canonical": r["canonical"], "asr": r["asr"], "n_sources": len(r["sources"]), "is_real": is_real,
                       "src0": r["sources"][0],
                       "before_class": prod.classification, "before_pass": prod.should_pass,
                       "after_verdict": tr.verdict, "after_pass": tr.would_pass,
                       "category": categorize(r["canonical"], r["asr"], tr), "detail": tr.detail,
                       "reason_E": "Candidate E" in (prod.reason or "")})
    # 集計(コーパス)
    agg = collections.OrderedDict()
    for x in corpus:
        if not x["is_real"]:
            continue
        k = x["category"] if not x["before_pass"] else "(既存PASS: 現行Productionで通過)"
        d = agg.setdefault(k, collections.Counter())
        d["n"] += 1
        d["before_pass"] += int(x["before_pass"])
        d["after_pass"] += int(x["after_pass"])
        d["rescued"] += int((not x["before_pass"]) and x["after_pass"])
        d["vetoed_prod_pass"] += int(x["before_pass"] and not x["after_pass"])
    # 合成(正常例/敵対的)
    pos, neg = [], []
    for c, a, k in cases.POSITIVE:
        prod = trial.prod_effective(c, a)
        tr = trial.trial_judge(c, a, prod)
        pos.append({"canonical": c, "asr": a, "kind": k, "before_pass": prod.should_pass, "before_class": prod.classification,
                    "after_pass": tr.would_pass, "after_verdict": tr.verdict})
    for c, a, k in cases.NEGATIVE:
        prod = trial.prod_effective(c, a)
        tr = trial.trial_judge(c, a, prod)
        neg.append({"canonical": c, "asr": a, "kind": k, "before_pass": prod.should_pass, "before_class": prod.classification,
                    "before_reason": (prod.reason or "")[:80],
                    "after_pass": tr.would_pass, "after_verdict": tr.verdict, "detail": tr.detail})
    summary = {
        "corpus_pairs": len(corpus),
        "corpus_before_pass": sum(x["before_pass"] for x in corpus),
        "corpus_after_pass": sum(x["after_pass"] for x in corpus),
        "corpus_rescued": sum((not x["before_pass"]) and x["after_pass"] for x in corpus),
        "corpus_rescued_real": sum((not x["before_pass"]) and x["after_pass"] and x["is_real"] for x in corpus),
        "corpus_rescued_synthetic_fixture": sum((not x["before_pass"]) and x["after_pass"] and not x["is_real"] for x in corpus),
        "corpus_real_nonpass_before": sum((not x["before_pass"]) and x["is_real"] for x in corpus),
        "corpus_vetoed_prod_pass": sum(x["before_pass"] and not x["after_pass"] for x in corpus),
        "positive_total": len(pos), "positive_before_pass": sum(p["before_pass"] for p in pos),
        "positive_after_pass": sum(p["after_pass"] for p in pos),
        "negative_total": len(neg), "negative_before_false_pass": sum(n["before_pass"] for n in neg),
        "negative_after_false_pass": sum(n["after_pass"] for n in neg),
        "category_table": {k: dict(v) for k, v in agg.items()},
    }
    json.dump({"summary": summary, "corpus": corpus, "positive": pos, "negative": neg},
              open(f"{OUT}/before_after_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    print("--- rescued (corpus)")
    for x in corpus:
        if (not x["before_pass"]) and x["after_pass"]:
            print(x["after_verdict"], x["n_sources"], x["canonical"][:40], "|", x["asr"][:40])
    print("--- vetoed prod pass (corpus)")
    for x in corpus:
        if x["before_pass"] and not x["after_pass"]:
            print(x["canonical"][:40], "|", x["asr"][:40])
    print("--- negative before false pass")
    for n in neg:
        if n["before_pass"]:
            print(n["canonical"], n["asr"], n["kind"], n["before_reason"])


if __name__ == "__main__":
    main()
