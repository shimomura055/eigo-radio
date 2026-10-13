# FAMILY-X-KP-IDIOM-PRIORITY-ABC-TRIAL-01 集計(API呼出なし、費用JPY0)。出力: analysis_01.json / analysis_01.md
import itertools
import json
import re
from collections import Counter

OUT = "er064_output/kp_idiom_priority_abc_01"
V0 = {"std": ["raw bean", "push prices up", "take time", "right away", "on a regular basis"],
      "adv": ["lag", "price tag", "show up", "come down", "come with"]}
d = json.load(open(f"{OUT}/final_summary_01.json", encoding="utf-8"))["runs"]


def nk(s):
    return re.sub(r"[\s\-]+", " ", (s or "").lower().replace("’", "'")).strip()


def is_pump(s):
    s = (s or "").lower()
    return "pump" in s and "fist" in s


def final_items(r):
    """run最終の5件。canonicalization後があればそのkey_phrase(正規化後)、無ければ選定時display_phrase。"""
    if r.get("canonicalized"):
        return [(i["key_phrase"], i["display_phrase"]) for i in r["canonicalized"]]
    return [(i["display_phrase"], i["display_phrase"]) for i in r.get("selected_items", [])]


def jacc(a, b):
    a, b = set(a), set(b)
    return len(a & b) / len(a | b) if a | b else 1.0


def gate(r):
    if r["selection_status"] != "KEY_WORDS_STRUCTURE_PASS":
        return "SELECTION_INVALID"
    cs = r.get("canonicalization_status")
    if cs not in ("CANONICALIZATION_PASS",):
        return cs
    return "PASS" if r.get("redundancy_status") == "REDUNDANCY_PASS" else (r.get("redundancy_status") or "NO_QA")


res = {}
md = []
for lv in ("std", "adv"):
    md.append(f"\n## {lv.upper()} 全run Key Phrase 5件(正規化後key_phrase)\n")
    md.append(f"V0(Phase B既存、Production現行shortlist+現行guidance)最終5: {' / '.join(V0[lv])}\n")
    md.append("| Version | run | Key Phrase 5件(rank順) | pump-fist | run最終gate | 重複QA | 費用 |\n|---|---|---|---|---|---|---|")
    for v in "ABC":
        runs = [r for r in d if r["level"] == lv and r["version"] == v]
        sets = []
        pump = 0
        gp = 0
        for r in runs:
            it = final_items(r)
            keys = [nk(k) for k, _ in it]
            sets.append(set(keys))
            p = any(is_pump(k) or is_pump(dp) for k, dp in it)
            pump += p
            g = gate(r)
            gp += g == "PASS"
            md.append(f"| {v} | {r['run']} | {' / '.join(k for k, _ in it) or '(なし)'} | {'採択' if p else '-'} | {g} | {r.get('redundancy_status')} | {r['cost_jpy']:.2f} |")
        pairs = [jacc(a, b) for a, b in itertools.combinations([s for s in sets if s], 2)]
        cnt = Counter(itertools.chain.from_iterable(sets))
        v0n = {nk(x) for x in V0[lv]}
        union = set(cnt)
        res[f"{lv}_{v}"] = {"runs": len(runs), "pump_selected": pump, "gate_all_pass": gp,
                            "jaccard_pairs": [round(x, 3) for x in pairs], "jaccard_mean": round(sum(pairs) / len(pairs), 3) if pairs else None,
                            "freq": dict(cnt.most_common()),
                            "gone_vs_V0": sorted(v0n - union), "v0_kept": sorted(v0n & union),
                            "new_vs_V0": sorted(union - v0n)}
    md.append(f"\n### {lv.upper()} Version別サマリー\n")
    md.append("| Version | pump-fist採択 | run最終gate完全PASS | Jaccard(平均/各対) | 出現頻度(n=3中) | V0から消えた(全run不在) | V0から残った | V0に無い新規 |\n|---|---|---|---|---|---|---|---|")
    for v in "ABC":
        x = res[f"{lv}_{v}"]
        md.append(f"| {v} | {x['pump_selected']}/{x['runs']} | {x['gate_all_pass']}/{x['runs']} | {x['jaccard_mean']} ({x['jaccard_pairs']}) | "
                  + ", ".join(f"{k}:{c}" for k, c in x["freq"].items()) + f" | {', '.join(x['gone_vs_V0'])} | {', '.join(x['v0_kept'])} | {', '.join(x['new_vs_V0'])} |")
    # A/B/C間の入替わり
    md.append(f"\n### {lv.upper()} A/B/C間の入替わり(頻度合計、同一run数n=3)\n")
    allk = sorted({k for v in "ABC" for k in res[f"{lv}_{v}"]["freq"]})
    md.append("| 表現 | A | B | C |\n|---|---|---|---|")
    for k in sorted(allk, key=lambda k: -sum(res[f"{lv}_{v}"]["freq"].get(k, 0) for v in "ABC")):
        md.append(f"| {k} | " + " | ".join(str(res[f"{lv}_{v}"]["freq"].get(k, 0)) for v in "ABC") + " |")

md.append("\n## 選定理由(LLM出力 selection_reason / listening_difficulty_reason、全run全件)\n")
for r in d:
    if not r.get("raw_selected_items"):
        md.append(f"\n### {r['tag']}: 選定structure INVALID(項目なし)")
        continue
    md.append(f"\n### {r['tag']}")
    for i in r["raw_selected_items"]:
        md.append(f"- r{i.get('rank')} `{i.get('display_phrase')}` ({i.get('phrase_type')}/{i.get('portfolio_category')}/{i.get('key_phrase_role')}) : {i.get('selection_reason')} | 聞き取り困難: {i.get('listening_difficulty_reason')}")
json.dump(res, open(f"{OUT}/analysis_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
open(f"{OUT}/analysis_01.md", "w", encoding="utf-8").write("\n".join(md))

print(open(f"{OUT}/analysis_01.md", encoding="utf-8").read().split("## 選定理由")[0])
