# -*- coding: utf-8 -*-
"""P1(M1 `_post_check`の受理面変更案)の辞書レベル上限census(FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01 委任_03、Opus_G必須修正)。
API 0・費用JPY0・Production無接続(読取専用)。**P1は実装しない**。ユーザー判断(REGISTER #120)の判断材料を作る。

P1の4条件(ITEM1_PHONETIC_EQUIVALENCE_ROOT_CAUSE_01.md §5-1、M1 `_enumerate_subs`/`forms_from`/`_post_check`):
  (1) ASR語wがCMU収録
  (2) wが「canonicalの期待綴りs(`expected_spellings(c)`)」とCMU同音(wとsのCMU音素列が一致する異読を持つ)かつ w != s
  (3) sの音素列が、canonical側の候補音素列から導く受理形(exact / drop_final_S_or_Z / add_s)のいずれかと一致
  (4) (c, s) がbenign単複対(`_is_benign_plural_pair`、規則的な単数/複数の揺れ)
これらを全て満たす (c, s, w) の**辞書レベル上限**(=P1で新たに受理され得る最大集合。実際の受理はF1残差0・Production判定should_passも要る
ため、これは上限)を、(A)CMU収録のs/z終わり語cの全件、(B)OOV c(Melos型)一般の(s,w)対、の2面で数える。
分離集計: 「別実在語型」=w がsと編集距離2以上(Jones←Joan型: 別の実在語が音だけで一致)、「綴り違い型」=編集距離1(Melos←Mello型)。
除外確認: Hayes←Hey型は、sが`hay`の経路は(4)で除外される(`hayes`のbenign単数形は`haye`)が、CMUに`haye`が収録されているため`s=haye`経路では
(1)〜(4)を満たし得る(=辞書レベルでは完全には除外されない。probesで事実を記録)。
使い方: python -I p1_dictionary_census_01.py --out p1_dictionary_census_01_result.json"""
from __future__ import annotations

import argparse
import collections
import json
import os
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
sys.path.insert(0, REPO)

import pronouncing  # noqa: E402

import er006_m1_multi_candidate_01 as M  # noqa: E402
import er006_preprod_hardening_01_validation as val  # noqa: E402


def lev(a: str, b: str) -> int:
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


class Cand:
    """FrozenCandidate互換の最小形(forms_fromが参照するのはpronのみ)。"""
    def __init__(self, pron):
        self.pron = pron
        self.source = "C1_cmu_variant"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    pronouncing.init_cmu()
    cmu_map: dict = collections.defaultdict(list)
    for w, ph in pronouncing.pronunciations:
        w = w.lower()
        if not w.isalpha():
            continue
        cmu_map[w].append(tuple(M._strip_stress(x) for x in ph.split()))
    cmu_map = {w: sorted(set(v)) for w, v in cmu_map.items()}
    by_pron: dict = collections.defaultdict(set)
    for w, vs in cmu_map.items():
        for v in vs:
            by_pron[v].add(w)

    def homophones(s):
        out = set()
        for v in cmu_map.get(s, []):
            out |= by_pron[v]
        out.discard(s)
        return out

    # ---------- (A) CMU収録のs/z終わり語cの全件 ----------
    pop = sorted(c for c in cmu_map if c[-1] in "sz" and len(c) > 2)
    pairs_a = []                       # (c, s, w, rule)
    pairs_a_excluded_nonbenign = 0     # (1)(2)(3)は満たすが(4)で除外された(c,s,w)数
    excluded_examples = []
    for c in pop:
        cands = [Cand(v) for v in cmu_map[c]]
        forms = M.forms_from(c, cands)
        for s in sorted(M.expected_spellings(c)):
            if s == c or s not in cmu_map:
                continue
            svs = cmu_map[s]
            rules = [r for v in svs for r, _cd in forms.get(tuple(v), [])]
            if not rules:
                continue                                    # (3)不成立
            rule = sorted(set(rules))[0]
            ws = [w for w in homophones(s) if w != c]       # (1)(2)
            if not ws:
                continue
            if not val._is_benign_plural_pair(c, s):          # (4)
                pairs_a_excluded_nonbenign += len(ws)
                if len(excluded_examples) < 2000:
                    excluded_examples.append((c, s, sorted(ws)[0]))
                continue
            for w in ws:
                pairs_a.append((c, s, w, rule))

    def classify(p):
        c, s, w, rule = p
        return "別実在語型(編集距離>=2)" if lev(w, s) >= 2 else "綴り違い型(編集距離1)"

    set_a = {(p[0], p[1], p[2]) for p in pairs_a}
    cls_a = collections.Counter(classify(p) for p in pairs_a)
    uniq_c_a = len({p[0] for p in pairs_a})

    # ---------- (B) OOV c(Melos型)一般: (s, w) 同音対の上限。c=s+"s"/"es"で(4)を満たす語が存在し得るsのみ ----------
    pairs_b = []
    for s in sorted(cmu_map):
        if len(s) < 2:
            continue
        for w in sorted(homophones(s)):
            # cを仮想的に s+"s" / s+"es" として(4)benign判定(OOV cは任意綴りなので、benignな複数形が構成できるsのみ対象)
            c_virtual = [x for x in (s + "s", s + "es") if val._is_benign_plural_pair(x, s) and x != s]
            if c_virtual:
                pairs_b.append((c_virtual[0], s, w))
    cls_b = collections.Counter("別実在語型(編集距離>=2)" if lev(w, s) >= 2 else "綴り違い型(編集距離1)" for _c, s, w in pairs_b)

    # ---------- probes ----------
    def probe(c, w):
        out = {"c": c, "w": w, "w_in_cmu": w in cmu_map, "c_in_cmu": c in cmu_map, "per_s": []}
        for s in sorted(M.expected_spellings(c)):
            if s == c:
                continue
            in_cmu = s in cmu_map
            homo = (w in homophones(s)) if in_cmu else False
            out["per_s"].append({"s": s, "s_in_cmu": in_cmu, "w_homophone_of_s": homo,
                                 "benign_pair(c,s)": val._is_benign_plural_pair(c, s)})
        p1 = [x for x in out["per_s"] if x["s_in_cmu"] and x["w_homophone_of_s"] and x["benign_pair(c,s)"]]
        out["p1_conditions_2_and_4_satisfiable"] = bool(p1)
        # 条件(3)(音素形)まで含めた完全判定=上限集合(A)への所属。(A)はcがCMU収録の場合のみ定義される。
        out["in_upper_bound_A_all_four_conditions"] = any((c, x["s"], w) in set_a for x in p1)
        out["p1_satisfying_s"] = [x["s"] for x in p1]
        return out

    probes = [probe("melos", "mello"), probe("hayes", "hey"), probe("jones", "joan"), probe("james", "jame"),
              probe("hughes", "hue"), probe("lewis", "louie"), probe("charles", "charlie")]
    # Melos(OOV)は(s, w)=("melo","mello")が上限集合に含まれるか
    melo_in_b = any(s == "melo" and w == "mello" for _c, s, w in pairs_b)

    def rep(pairs, n=20):
        # 別実在語型を先に、次に綴り違い型。決定的順序(語長の短い順→辞書順)で代表例を取る
        d = [p for p in pairs if lev(p[2], p[1]) >= 2]
        v = [p for p in pairs if lev(p[2], p[1]) < 2]
        pick = d[: n // 2] + v[: n - len(d[: n // 2])]
        return [{"c": p[0], "s": p[1], "w": p[2], **({"rule": p[3]} if len(p) == 4 else {}),
                 "type": "別実在語型" if lev(p[2], p[1]) >= 2 else "綴り違い型"} for p in pick]

    result = {
        "management_id": "FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01 委任_03", "api_calls": 0, "cost_jpy": 0,
        "p1_implemented": False, "purpose": "P1の辞書レベル上限census(判断材料。P1は未実装)",
        "cmu_words_alpha": len(cmu_map), "population_A_sz_ending_cmu_words": len(pop),
        "A_cmu_c_all": {
            "upper_bound_pairs_c_s_w": len(pairs_a), "distinct_c": uniq_c_a, "by_type": dict(cls_a),
            "excluded_by_condition4_nonbenign_pairs": pairs_a_excluded_nonbenign,
            "excluded_examples": [{"c": c, "s": s, "w": w} for c, s, w in excluded_examples[:10]],
            "representative_20": rep(pairs_a)},
        "B_oov_c_generic_s_w": {
            "upper_bound_pairs_s_w": len(pairs_b), "by_type": dict(cls_b), "melos_mello_in_set": melo_in_b,
            "representative_20": rep([(c, s, w) for c, s, w in pairs_b])},
        "probes": probes,
        "notes": [
            "上限=辞書上で条件(1)〜(4)を満たす最大集合。実際の受理は更にF1残差0・Production判定(classify_asr_match should_pass)・"
            "入口条件(entity-like UNCERTAIN)を要するため、これより小さい。",
            "(A)はcが辞書収録語の場合、(B)はcがOOV(Melos型でLedger候補あり)の場合の(s,w)上限。"
            "編集距離>=2を『別実在語型』(Jones←Joan型)、編集距離1を『綴り違い型』(Melos←Mello型)と定義した分離集計。",
            "実データcensus(E21 telemetry)では新規受理は(melos,mello)1ペア・24行のみ(ITEM1 §5-2)。本censusは辞書上の最大値。",
        ],
    }
    json.dump(result, open(args.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: result[k] for k in ("cmu_words_alpha", "population_A_sz_ending_cmu_words")}, ensure_ascii=False))
    print("A:", result["A_cmu_c_all"]["upper_bound_pairs_c_s_w"], result["A_cmu_c_all"]["by_type"],
          "excluded_nonbenign:", pairs_a_excluded_nonbenign)
    print("B:", result["B_oov_c_generic_s_w"]["upper_bound_pairs_s_w"], result["B_oov_c_generic_s_w"]["by_type"],
          "melos/mello in set:", melo_in_b)
    for p in probes:
        print(p["c"], "<-", p["w"], "(2)(4)ok:", p["p1_conditions_2_and_4_satisfiable"], "all4(A):", p["in_upper_bound_A_all_four_conditions"], "s:", p["p1_satisfying_s"])


if __name__ == "__main__":
    main()
