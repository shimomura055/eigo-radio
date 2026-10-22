# er109_machine_pairs_eval_01.py
# ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01 委任_01 §4: 機械生成ペアによる網羅テスト(API 0・ローカル)。
# 母集団: 保存distinct期待文 = (a) 全 keywords_canonicalized.json の used_form(KP。tts_safe_kp_en適用後) (b) 保存本文segmentのcanonicalから切り出した文。
# 正例(発音同一の異表記): 数字<->語(独立実装=val._words_to_number / inflect)・記号(%,&,vs.,Mr.,Dr.,OK)・contraction・ハイフン・大小/句読点・頭字語・CMU同音語置換。
# 負例(発音が異なる改変): 数の変更・否定語の脱落/付加・語の置換・音素1つ違いの最小対・内容語の脱落/挿入。
# 判定: er109.evaluate と、既存経路(classify_asr_match+同音救済。KPはsegment_id=kpN_en、本文はfull_story_part1)の両方。
# 目標: 正例の同値率(提案/既存/合算)、負例の誤同値率(提案層による『既存が不合格→提案が同値』=新規誤PASSは0)。
import argparse
import collections
import glob
import json
import random
import re
import sys

import inflect
import pronouncing

sys.path.insert(0, ".")
import er006_preprod_hardening_01_validation as val
import er006_secondary_asr_01 as S
import er109_asr_orthographic_equivalence_01 as e109
import er008_asr_variant_hardening_15_homophone_en as hp

INF = inflect.engine()
RNG = random.Random(20261022)
REP = False   # --rep: er109を代表発音のみ(厳格)で評価
NEG_WORDS = {"not", "no", "never", "none", "nobody", "nothing", "neither", "nor", "cannot", "without"}
NUM_WORDS = set(val._ONES) | set(val._TENS) | {"hundred", "thousand", "million"}


def load_kp_phrases():
    import er003_v1_n3_01_tts_generate as tg
    out = set()
    for f in glob.glob("**/keywords_canonicalized.json", recursive=True):
        if f.startswith(".venv"):
            continue
        try:
            d = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        for it in d.get("items", []):
            u = it.get("used_form")
            if u and re.search(r"[A-Za-z]", u) and not re.search(r"[぀-鿿]", u):
                out.add(tg.tts_safe_kp_en(u))
    return sorted(out)


def load_body_sentences(limit=700):
    seen, sents = set(), []
    for f in sorted(glob.glob("**/*tts_generation_results*.json", recursive=True)):
        if f.startswith(".venv"):
            continue
        try:
            d = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        for k, v in (d.get("segments") or {}).items():
            t = (v or {}).get("text") if isinstance(v, dict) else None
            if not t or re.search(r"[぀-鿿]", t) or k.startswith("kp"):
                continue
            for s in re.split(r"(?<=[.!?])\s+", t):
                s = s.strip()
                if 4 <= len(s.split()) <= 25 and s not in seen:
                    seen.add(s)
                    sents.append(s)
    RNG.shuffle(sents)
    return sents[:limit]


# ---------------------------------------------------------------- 正例生成
def strip_p(tok):
    m = re.match(r"^([^\w$%'\-]*)(.*?)([^\w%'\-]*)$", tok)
    return m.group(1), m.group(2), m.group(3)


def gen_words_to_digits(text):
    toks = text.split()
    out, i, changed = [], 0, False
    while i < len(toks):
        pre, core, post = strip_p(toks[i])
        low = core.lower()
        if low in NUM_WORDS or ("-" in low and all(p in NUM_WORDS for p in low.split("-"))):
            j, run, lastpost = i, [], ""
            while j < len(toks):
                pr, cr, po = strip_p(toks[j])
                parts = cr.lower().split("-")
                if all(p in NUM_WORDS or p == "and" for p in parts) and cr:
                    run += [p for p in parts if p]
                    lastpost = po
                    j += 1
                    if po:
                        break
                else:
                    break
            run2 = [w for w in run if w != "and" or True]
            n = val._words_to_number(run2)
            if n is not None and not (len(run2) == 1 and n < 2 and False):
                out.append(pre + str(n) + lastpost)
                changed = True
                i = j
                continue
        if low == "percent" and out and re.fullmatch(r"\d+", strip_p(out[-1])[1] or ""):
            pr, cr, po = strip_p(out[-1])
            out[-1] = pr + cr + "%" + post
            changed = True
            i += 1
            continue
        out.append(toks[i])
        i += 1
    return (" ".join(out), "num_words_to_digits") if changed else None


def gen_digits_to_words(text):
    changed = [False]

    def rep(m):
        s = m.group(0)
        raw = s.replace(",", "")
        if not re.fullmatch(r"\d{1,9}", raw):
            return s
        changed[0] = True
        return INF.number_to_words(int(raw)).replace(",", "").replace("-", " ")
    t = re.sub(r"(?<![\w.])\d[\d,]*(?![\w.]|st|nd|rd|th)", rep, text)
    t2 = re.sub(r"(?<!\w)(\d+)(st|nd|rd|th)\b", lambda m: (changed.__setitem__(0, True) or INF.number_to_words(m.group(0)).replace("-", " ")), t)
    return (t2, "num_digits_to_words") if changed[0] and t2 != text else None


def gen_one_to_1(text):
    t = re.sub(r"\b[Oo]ne\b", "1", text)
    return (t, "one_to_1") if t != text else None


def gen_symbols(text):
    t = text
    for a, b in ((r"\band\b", "&"), (r"\bversus\b", "vs."), (r"\bmister\b", "Mr."), (r"\bdoctor\b", "Dr."), (r"\bokay\b", "OK"),
                 (r"\bplus\b", "+"), (r"\bpercent\b", "%")):
        t2 = re.sub(a, b, t, count=1, flags=re.I)
        if t2 != t and not (b == "%" and not re.search(r"\d", t)):
            return (t2, "symbol_" + (re.sub(r"\W", "", b) or "sym"))
    return None


_C_INV = {v: k for k, v in val._ALL_STANDARD_CONTRACTIONS.items()}


def gen_contraction(text):
    t = text
    for exp, con in sorted(_C_INV.items(), key=lambda kv: -len(kv[0])):
        t2 = re.sub(r"\b" + re.escape(exp) + r"\b", con, t, count=1, flags=re.I)
        if t2 != t:
            return (t2, "contraction_contract")
    t2 = val.expand_standard_contractions(t)
    return (t2, "contraction_expand") if t2 != t else None


def gen_hyphen(text):
    if "-" in text:
        return (text.replace("-", " "), "hyphen_to_space")
    return None


def gen_hyphen_join(text):
    if "-" in text:
        return (text.replace("-", ""), "hyphen_removed")
    return None


def gen_case_punct(text):
    t = re.sub(r"[.,;:!?\"“”]", "", text).lower()
    return (t, "case_punct") if t != text else None


def gen_trailing_period(text):
    return (text.rstrip(".") + ".", "trailing_period") if not text.endswith(".") else None


def gen_acronym_dots(text):
    def rep(m):
        return ".".join(m.group(0)) + "."
    t = re.sub(r"\b[A-Z]{2,4}\b", rep, text, count=1)
    return (t, "acronym_dots") if t != text else None


_HOMO_CACHE = {}


def homophones_of(word):
    w = word.lower()
    if w in _HOMO_CACHE:
        return _HOMO_CACHE[w]
    out = []
    ph = pronouncing.phones_for_word(w)
    if ph:
        mine = {tuple(re.sub(r"\d", "", p).split()) for p in ph}
        for cand in set(pronouncing.search("^" + re.escape(ph[0]) + "$")):
            if cand != w and re.fullmatch(r"[a-z]{2,}", cand):
                cp = {tuple(re.sub(r"\d", "", p).split()) for p in pronouncing.phones_for_word(cand)}
                if cp & mine:
                    out.append(cand)
    _HOMO_CACHE[w] = sorted(out)
    return _HOMO_CACHE[w]


def gen_homophone(text):
    toks = text.split()
    idx = list(range(len(toks)))
    RNG.shuffle(idx)
    for i in idx:
        pre, core, post = strip_p(toks[i])
        if re.fullmatch(r"[A-Za-z]{2,}", core) and core.lower() not in NEG_WORDS and core.lower() not in NUM_WORDS:
            hs = [h for h in homophones_of(core) if h.lower() not in NEG_WORDS and h not in NUM_WORDS]
            if hs:
                toks[i] = pre + RNG.choice(hs) + post
                return (" ".join(toks), "cmu_homophone_swap")
    return None


POS_GENS = [gen_words_to_digits, gen_digits_to_words, gen_one_to_1, gen_symbols, gen_contraction, gen_hyphen, gen_hyphen_join,
            gen_case_punct, gen_trailing_period, gen_acronym_dots, gen_homophone]


# ---------------------------------------------------------------- 負例生成
def _variants(word):
    ph = pronouncing.phones_for_word(word.lower())
    return {tuple(re.sub(r"\d", "", p).split()) for p in ph} if ph else None


def neg_number_change(text):
    toks = text.split()
    for i, t in enumerate(toks):
        pre, core, post = strip_p(t)
        if re.fullmatch(r"\d+", core):
            toks[i] = pre + str(int(core) + 1 if int(core) < 9 else int(core) * 10 + 1) + post
            return " ".join(toks), "neg_number_digit_changed"
        if core.lower() in val._ONES and core.lower() != "zero":
            nxt = {v: k for k, v in val._ONES.items()}.get(val._ONES[core.lower()] % 19 + 1)
            if nxt and nxt != core.lower():
                toks[i] = pre + nxt + post
                return " ".join(toks), "neg_number_word_changed"
    return None


def neg_negation_drop(text):
    t = re.sub(r"\b(not|never|no|nothing|nobody|without)\b\s*", "", text, count=1, flags=re.I)
    if t != text and t.strip():
        return t.strip(), "neg_negation_dropped"
    t = re.sub(r"\b(\w+)n't\b", r"\1", text, count=1)
    if t != text:
        return t, "neg_negation_dropped"
    return None


def neg_negation_add(text):
    toks = text.split()
    if len(toks) >= 2:
        return "not " + text, "neg_negation_added"
    return None


def neg_content_delete(text):
    toks = text.split()
    cands = [i for i, t in enumerate(toks) if len(strip_p(t)[1]) >= 4]
    if len(toks) >= 2 and cands:
        i = RNG.choice(cands)
        return " ".join(toks[:i] + toks[i + 1:]), "neg_content_word_deleted"
    return None


def neg_word_insert(text, vocab):
    toks = text.split()
    w = RNG.choice(vocab)
    i = RNG.randrange(len(toks) + 1)
    return " ".join(toks[:i] + [w] + toks[i:]), "neg_word_inserted"


def neg_word_sub(text, vocab):
    toks = text.split()
    cands = [i for i, t in enumerate(toks) if re.fullmatch(r"[A-Za-z]{4,}", strip_p(t)[1])]
    if not cands:
        return None
    i = RNG.choice(cands)
    pre, core, post = strip_p(toks[i])
    orig = _variants(core)
    for _ in range(20):
        w = RNG.choice(vocab)
        v = _variants(w)
        if v and orig and not (v & orig) and w.lower() != core.lower():
            toks[i] = pre + w + post
            return " ".join(toks), "neg_word_replaced_random"
    return None


def neg_minimal_pair(text):
    """単語内の音素1つ違い(全variantで不一致)の語へ置換。"""
    toks = text.split()
    idx = list(range(len(toks)))
    RNG.shuffle(idx)
    for i in idx:
        pre, core, post = strip_p(toks[i])
        if not re.fullmatch(r"[a-z]{3,}", core.lower()):
            continue
        ph = pronouncing.phones_for_word(core.lower())
        if not ph:
            continue
        mine = _variants(core)
        p0 = ph[0].split()
        pos_order = list(range(len(p0)))
        RNG.shuffle(pos_order)
        for pos in pos_order[:3]:
            pat = " ".join(p0[:pos] + [r"\S+"] + p0[pos + 1:])
            hits = [h for h in pronouncing.search("^" + pat + "$") if re.fullmatch(r"[a-z]{3,}", h) and h != core.lower()]
            hits = [h for h in hits if (_variants(h) and not (_variants(h) & mine))]
            if hits:
                toks[i] = pre + RNG.choice(hits) + post
                return " ".join(toks), "neg_minimal_pair_one_phoneme"
    return None


# ---------------------------------------------------------------- 実行
def existing_pass(canon, text, sid):
    cls = val.classify_asr_match(canon, text, segment_id=sid)
    return bool(cls.should_pass or S._step_alternate_pass(cls))


def evaluate_set(phrases, sid, vocab, kind):
    pos = collections.defaultdict(lambda: collections.Counter())
    neg = collections.defaultdict(lambda: collections.Counter())
    pos_miss, neg_new_accept, neg_e109_equiv, neg_existing_pass = collections.defaultdict(list), [], [], []
    for c in phrases:
        for g in POS_GENS:
            r = g(c)
            if not r:
                continue
            a, cat = r
            ex = existing_pass(c, a, sid)
            eq = e109.evaluate(c, a, representative_only=REP).equivalent
            P = pos[cat]
            P["n"] += 1
            P["existing"] += int(ex)
            P["e109"] += int(eq)
            P["union"] += int(ex or eq)
            if not (ex or eq) and len(pos_miss[cat]) < 6:
                pos_miss[cat].append([c, a])
        for g in (neg_number_change, neg_negation_drop, neg_negation_add, neg_content_delete, neg_minimal_pair,
                  lambda t: neg_word_insert(t, vocab), lambda t: neg_word_sub(t, vocab)):
            r = g(c)
            if not r:
                continue
            a, cat = r
            ex = existing_pass(c, a, sid)
            eq = e109.evaluate(c, a, representative_only=REP)
            N = neg[cat]
            N["n"] += 1
            N["existing_pass"] += int(ex)
            N["e109_equiv"] += int(eq.equivalent)
            N["new_accept"] += int(eq.equivalent and not ex)
            if ex:
                neg_existing_pass.append({"canonical": c, "asr": a, "cat": cat})
            if eq.equivalent:
                neg_e109_equiv.append({"canonical": c, "asr": a, "cat": cat, "existing": ex, "rules": eq.rules,
                                       "spans": [(s.canon_span, s.asr_span, s.rule) for s in eq.spans]})
            if eq.equivalent and not ex:
                neg_new_accept.append({"canonical": c, "asr": a, "cat": cat, "rules": eq.rules,
                                       "spans": [(s.canon_span, s.asr_span, s.rule) for s in eq.spans]})
    return {"kind": kind, "phrases": len(phrases), "positive": {k: dict(v) for k, v in pos.items()},
            "negative": {k: dict(v) for k, v in neg.items()}, "pos_missed_examples": dict(pos_miss),
            "neg_new_accept": neg_new_accept, "neg_existing_pass(既存Productionの誤PASS)": neg_existing_pass, "neg_e109_equiv_all": neg_e109_equiv}


def totals(res):
    p = res["positive"]
    n = res["negative"]
    pn = sum(v["n"] for v in p.values())
    nn = sum(v["n"] for v in n.values())
    return {
        "positive_n": pn, "positive_existing": sum(v["existing"] for v in p.values()), "positive_e109": sum(v["e109"] for v in p.values()),
        "positive_union": sum(v["union"] for v in p.values()),
        "negative_n": nn, "negative_existing_pass(既存の誤PASS)": sum(v["existing_pass"] for v in n.values()),
        "negative_e109_equiv": sum(v["e109_equiv"] for v in n.values()),
        "negative_NEW_false_accept(既存不合格→e109同値)": sum(v["new_accept"] for v in n.values()),
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="docs/research/ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01/machine_pairs_eval_01.json")
    ap.add_argument("--body", type=int, default=700)
    ap.add_argument("--rep", action="store_true")
    a = ap.parse_args()
    REP = bool(a.rep)
    kp = load_kp_phrases()
    body = load_body_sentences(a.body)
    vocab = sorted({w.lower() for p in kp + body for w in re.findall(r"[A-Za-z]{4,}", p) if pronouncing.phones_for_word(w.lower())})
    out = {"generated_by": "er109_machine_pairs_eval_01.py", "api_calls": 0, "cost_jpy": 0, "seed": 20261022,
           "kp_phrases": len(kp), "body_sentences": len(body), "vocab": len(vocab)}
    r_kp = evaluate_set(kp, "kp1_en", vocab, "KP(distinct used_form)")
    r_body = evaluate_set(body, "full_story_part1", vocab, "body sentences")
    out["kp"], out["body"] = r_kp, r_body
    out["totals"] = {"kp": totals(r_kp), "body": totals(r_body)}
    json.dump(out, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(out["totals"], ensure_ascii=False, indent=1))
    for nm, r in (("KP", r_kp), ("BODY", r_body)):
        print("==", nm)
        for k, v in sorted(r["positive"].items()):
            print(f"  +{k:28} n={v['n']:4} existing={v['existing']:4} e109={v['e109']:4} union={v['union']:4}")
        for k, v in sorted(r["negative"].items()):
            print(f"  -{k:28} n={v['n']:4} existing_pass={v['existing_pass']:3} e109_equiv={v['e109_equiv']:3} NEW={v['new_accept']:3}")
