# er109_adversarial_negatives_01.py
# ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01 委任_02 (Opus P-05): 敵対的負例の再構築 + 是正後er109の誤同値測定。API 0・ローカル。
# 委任_01の負例生成器は『stress除去後の全variantで交わらない語』だけを置換先にしており、er109自身の判定基準と循環していた
# (弱形/stress除去/代表以外variant/同形異音語/曖昧略語の誤同値を構造上検出できない)。本scriptは逆に
#   『CMU全体から、(stress除去/弱形/代表以外variantのいずれかでしか交わらない、綴りの異なる語の組)』を全数列挙し、er109へ渡す。
# 判定: er109.evaluate(w1,w2) / (w2,w1) が同値になった組を「suspect」とし、代表(先頭)発音が2値強勢で完全一致する組は
#       『真の同音(benign)』として別集計。suspectは1件ずつ分類する(true_homophone / false_equivalent)。
import argparse
import collections
import itertools
import json
import random
import re
import sys

sys.path.insert(0, ".")
import er008_asr_variant_hardening_15_homophone_en as hp
import er109_asr_orthographic_equivalence_01 as e109

CMU_PATH = ".venv/Lib/site-packages/cmudict/data/cmudict.dict"
RNG = random.Random(20261022)


def load_cmu():
    d = collections.OrderedDict()
    for line in open(CMU_PATH, encoding="latin-1"):
        line = line.split("#")[0].strip()
        if not line:
            continue
        w, _, ph = line.partition(" ")
        w = re.sub(r"\(\d+\)$", "", w)
        if not re.fullmatch(r"[a-z]+(?:'[a-z]+)?", w):
            continue
        d.setdefault(w, []).append(ph.strip())
    return d


def nostress(ph):
    return tuple(re.sub(r"\d", "", ph).split())


def bin2(ph):
    return hp._stress2_tokens(ph)


def strong(ph):
    return hp._has_stressed_vowel(bin2(ph))


def category(w1, w2, cmu):
    """この組が『なぜ危険か』: er109が受けてはいけない系統の分類。"""
    v1, v2 = cmu[w1], cmu[w2]
    ns1 = {nostress(p) for p in v1}
    ns2 = {nostress(p) for p in v2}
    common = ns1 & ns2
    if not common:
        return None
    b1 = {bin2(p) for p in v1}
    b2 = {bin2(p) for p in v2}
    cats = []
    if not (b1 & b2):
        cats.append("stress_diff_only")             # billow/below: stress除去でしか交わらない
    else:
        inter = b1 & b2
        if not any(hp._has_stressed_vowel(x) for x in inter):
            cats.append("weak_form_only")           # are/or
        if bin2(v1[0]) != bin2(v2[0]) and not (bin2(v1[0]) in b2 and bin2(v2[0]) in b1):
            cats.append("nonrep_variant")
        elif bin2(v1[0]) != bin2(v2[0]):
            cats.append("nonrep_variant")
        s1 = {x for x in b1 if hp._has_stressed_vowel(x)}
        s2 = {x for x in b2 if hp._has_stressed_vowel(x)}
        if (len(s1) > 1 and not s1 <= s2) or (len(s2) > 1 and not s2 <= s1):
            cats.append("heteronym")
    return cats or ["benign_all_variants_equal_or_rep_equal"]


def benign(w1, w2, cmu):
    """代表(先頭)発音が2値強勢で一致する = 通常の同音語(正例側)。"""
    return bin2(cmu[w1][0]) == bin2(cmu[w2][0]) and hp._has_stressed_vowel(bin2(cmu[w1][0]))


def run_word_pairs(cmu, limit_pairs=None):
    """CMU全体の『綴りの異なる語の組で、stress除去・any-variantで音素列が交わるもの』を全数。
    adversarial(=代表強勢読みが一致しない): 非代表variant/弱形/stress差/同形異音語でしか交わらない -> er109の同値は全て誤同値候補(0であるべき)
    positive_rep_equal(=代表強勢読みが一致): 通常の同音語 -> 同値率(取りこぼしの理由別内訳)を測る。"""
    idx = collections.defaultdict(set)
    for w, vs in cmu.items():
        for p in vs:
            idx[nostress(p)].add(w)
    pairs = set()
    for ws in idx.values():
        if len(ws) > 1:
            for a, b in itertools.permutations(sorted(ws), 2):
                pairs.add((a, b))
    pairs = sorted(pairs)
    if limit_pairs:
        RNG.shuffle(pairs)
        pairs = sorted(pairs[:limit_pairs])
    out = {"pairs": len(pairs), "adversarial_by_category": collections.Counter(), "adversarial_false_equiv": collections.Counter(),
           "positive_rep_equal_total": 0, "positive_rep_equal_equiv": 0, "positive_miss_reason": collections.Counter(),
           "positive_pass_with_warning": 0}
    suspects = []
    for a, b in pairs:
        ra, rb = hp.representative_strong_reading(a), hp.representative_strong_reading(b)
        r = e109.evaluate(a, b)
        if ra is not None and ra == rb:
            out["positive_rep_equal_total"] += 1
            if r.equivalent:
                out["positive_rep_equal_equiv"] += 1
                if r.warnings:
                    out["positive_pass_with_warning"] += 1
            else:
                sr = hp.strong_readings(a)
                out["positive_miss_reason"]["canonical_heteronym(複数の強勢読み)" if sr and len(sr) > 1 else r.reason[:40]] += 1
            continue
        key = "+".join(sorted(category(a, b, cmu) or ["none"]))
        out["adversarial_by_category"][key] += 1
        if r.equivalent:
            out["adversarial_false_equiv"][key] += 1
            suspects.append({"canon": a, "asr": b, "category": key, "reason": r.reason, "rules": r.rules,
                             "canon_prons": cmu[a][:4], "asr_prons": cmu[b][:4], "verdict": r.verdict})
    return out, suspects


def run_two_word_oronyms(cmu, n_targets=1500):
    """w3(1語)をCMU音素列でw1 w2(2語)へ分割できる組(for tea/forty型)。er109が同値にしてはいけない(承認済みer094条件の外)。"""
    byseq = collections.defaultdict(set)
    for w, vs in cmu.items():
        for p in vs:
            byseq[nostress(p)].add(w)
    targets = [w for w in cmu if len(w) >= 5]
    RNG.shuffle(targets)
    n = bad = tested = existing_route = 0
    suspects = []
    for w3 in targets[:n_targets]:
        done = set()
        for p in cmu[w3]:
            ph = nostress(p)
            for k in range(1, len(ph)):
                for w1 in byseq.get(ph[:k], ()):
                    for w2 in byseq.get(ph[k:], ()):
                        if (w1, w2) in done or w3 in (w1, w2) or w1 + w2 == w3:
                            continue
                        done.add((w1, w2))
                        if len(done) > 12:
                            break
        for w1, w2 in list(done)[:12]:
            for c, a in ((w3, f"{w1} {w2}"), (f"{w1} {w2}", w3)):
                tested += 1
                r = e109.evaluate(c, a)
                if r.equivalent:
                    if set(r.rules) <= {"multiword_homophone_er094", "compound_spacing"}:
                        existing_route += 1     # 承認済みの既存ルート(er094 PNMH-01 / despaced)の判定そのもの。er109の新規救済ではない
                        continue
                    bad += 1
                    suspects.append({"canon": c, "asr": a, "reason": r.reason, "rules": r.rules, "verdict": r.verdict})
    return {"targets": min(n_targets, len(targets)), "tested": tested, "false_equiv_new_routes": bad,
            "equiv_via_existing_approved_routes(er094/despaced)": existing_route}, suspects


def reading_words(n):
    ws = e109.cardinal_variants(n)
    return ws[0] if ws else None


def run_number_oronyms(cmu, ns):
    """数字<->語のoronym: 数の読みの音素列を、数詞語彙以外の語列(for tea 等)で再現する組。"""
    byseq = collections.defaultdict(set)
    for w, vs in cmu.items():
        for p in vs:
            byseq[nostress(p)].add(w)
    vocab = e109._NUMBER_VOCAB
    tested = bad = true_homophone = vocab_oronym = 0
    true_list = []
    suspects = []
    for n in ns:
        words = reading_words(n)
        if not words or any(w not in cmu for w in words):
            continue
        ph = tuple(x for w in words for x in nostress(cmu[w][0]))
        found = []

        def rec(i, acc):
            if len(found) >= 40 or len(acc) > 3:
                return
            if i == len(ph):
                found.append(list(acc))
                return
            for j in range(i + 1, len(ph) + 1):
                for w in byseq.get(ph[i:j], ()):
                    acc.append(w)
                    rec(j, acc)
                    acc.pop()
        rec(0, [])
        for combo in found:
            if combo == words or all(w in vocab for w in combo):
                continue
            for c, a in ((str(n), " ".join(combo)), (" ".join(combo), str(n))):
                tested += 1
                r = e109.evaluate(c, a)
                if r.equivalent:
                    phrase = a if not a.isdigit() else c
                    if len(phrase.split()) == 1:
                        true_homophone += 1      # 数詞1語と発音が同一の1語(to/too/two, for/four, won/one 等)= 承認済みTrack Bと同方向の真の同音
                        true_list.append(phrase)
                        continue
                    ws = phrase.split()
                    if all(w in vocab or any(hp.strict_homophone_pair(v, w) for v in vocab if len(v) > 1 and v.isalpha()) for w in ws):
                        vocab_oronym += 1        # 数詞語彙(とその同音語)だけで同じ音になる語列(thirty four <-> third e fore)= 音素列が同一の真の同音
                        continue
                    bad += 1
                    suspects.append({"canon": c, "asr": a, "reason": r.reason, "rules": r.rules, "verdict": r.verdict})
    return {"numbers": len(ns), "equiv_multiword_all_words_in_number_vocab_or_homophones": vocab_oronym, "tested": tested, "false_equiv_multiword": bad, "equiv_single_word_true_homophone": true_homophone,
            "true_homophone_words": sorted(set(true_list))}, suspects


def run_abbreviations(cmu):
    """曖昧略語の誤展開 + 大文字略語のCMU展開variant(tv->television)。"""
    cases = []
    for c, a in [("St. Louis", "Street Louis"), ("St. Louis", "Saint Louis"), ("Saint Louis", "St. Louis"), ("Street Louis", "St. Louis"),
                 ("Dr. Lee", "drive Lee"), ("Dr. Lee", "doctor Lee"), ("doctor Lee", "Dr. Lee"), ("drive Lee", "Dr. Lee"),
                 ("Mt. Fuji", "mount Fuji"), ("Mt. Fuji", "mountain Fuji"), ("# 5", "number 5"), ("# 5", "hash 5"), ("# 5", "pound 5"),
                 ("number 5", "# 5"), ("Main St.", "Main Street"), ("Main Dr.", "Main Drive"), ("TV", "television"), ("television", "TV"),
                 ("Mr. Lee", "mister Lee"), ("Mr. Lee", "master Lee"), ("Ms. Lee", "miss Lee"), ("OK", "okay"), ("US", "us"), ("us", "US")]:
        cases.append((c, a))
    tested = bad = 0
    suspects = []
    for c, a in cases:
        r = e109.evaluate(c, a)
        tested += 1
        suspects.append({"canon": c, "asr": a, "equivalent": r.equivalent, "verdict": r.verdict, "reason": r.reason})
    # CMU全語: 2-5字の大文字略語 vs 同音(any variant)の別語
    idx = collections.defaultdict(set)
    for w, vs in cmu.items():
        for p in vs:
            idx[nostress(p)].add(w)
    caps_tested = caps_bad = 0
    caps_suspects = []
    for w in cmu:
        if not (2 <= len(w) <= 5) or "'" in w:
            continue
        others = set()
        for p in cmu[w]:
            others |= idx[nostress(p)]
        for x in others:
            if x == w:
                continue
            for c, a in ((w.upper(), x), (x, w.upper())):
                caps_tested += 1
                r = e109.evaluate(c, a)
                if r.equivalent and w not in e109.ABBREVIATIONS and hp.representative_strong_reading(w) != hp.representative_strong_reading(x)                         and not (e109._letters_prons(w) and tuple(t for p in [bin2(cmu[x][0])] for t in p) in e109._letters_prons(w)):
                    caps_bad += 1
                    caps_suspects.append({"canon": c, "asr": a, "reason": r.reason, "rules": r.rules, "verdict": r.verdict})
    return {"cases": tested, "caps_pairs_tested": caps_tested, "caps_false_equiv": caps_bad}, suspects, caps_suspects


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="docs/research/ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01/adversarial_negatives_02_aho02.json")
    ap.add_argument("--limit-pairs", type=int, default=0)
    ap.add_argument("--targets", type=int, default=1500)
    a = ap.parse_args()
    cmu = load_cmu()
    print("cmu words", len(cmu), file=sys.stderr)
    wp, wp_s = run_word_pairs(cmu, a.limit_pairs or None)
    print("word pairs done", wp["pairs"], dict(wp["adversarial_false_equiv"]), file=sys.stderr)
    oro, oro_s = run_two_word_oronyms(cmu, a.targets)
    print("oronyms", oro, file=sys.stderr)
    ns = list(range(0, 201)) + [250, 300, 400, 500, 1000, 1100, 1200, 1500, 1900, 1990, 2000, 2005, 2020, 2024, 2025, 5000, 10000]
    num, num_s = run_number_oronyms(cmu, ns)
    print("number oronyms", num, file=sys.stderr)
    ab, ab_cases, caps_s = run_abbreviations(cmu)
    print("abbrev", ab, file=sys.stderr)
    out = {"layer_version": e109.LAYER_VERSION, "cmu_words": len(cmu),
           "word_pairs": {k: (dict(v) if isinstance(v, collections.Counter) else v) for k, v in wp.items()}, "word_pair_suspects": wp_s,
           "two_word_oronyms": oro, "two_word_oronym_suspects": oro_s, "number_oronyms": num, "number_oronym_suspects": num_s,
           "abbreviations": ab, "abbreviation_cases": ab_cases, "caps_acronym_suspects": caps_s}
    json.dump(out, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: out[k] for k in ("word_pairs", "two_word_oronyms", "number_oronyms", "abbreviations")}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
