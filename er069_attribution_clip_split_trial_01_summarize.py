# -*- coding: utf-8 -*-
"""results_01.json から結果表を作る(API呼出なし)。python ... --results <json> --out <md>"""
import sys, json, argparse, math


def fisher_p(a, b, c, d):
    """2x2 Fisher exact two-sided (a,b / c,d)。"""
    from math import comb
    n1, n2, k = a + b, c + d, a + c
    tot = n1 + n2
    def p(x):
        return comb(n1, x) * comb(n2, k - x) / comb(tot, k)
    p0 = p(a)
    return sum(p(x) for x in range(max(0, k - n2), min(n1, k) + 1) if p(x) <= p0 + 1e-12)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    R = json.load(open(a.results, encoding="utf8"))
    rows = R["rows"]
    md = ["# results summary (Phase 2)\n", f"obs={R['n_obs']} gen_tts_jpy={R['gen_tts_jpy']} total_jpy={R['total_jpy']}\n"]

    def tab(title, sel):
        md.append(f"\n## {title}\n| level/target | boundary | length | n | OpenAI PASS | Azure PASS | OR PASS | HR proxy | spell OA | spell Az | spell WH |\n|---|---|---|---|---|---|---|---|---|---|---|")
        keys = sorted({(r["level"], r["target"], r["boundary"], r["length"]) for r in rows if sel(r)},
                      key=lambda k: (k[0], k[1], k[3], k[2]))
        for k in keys:
            v = [r for r in rows if sel(r) and (r["level"], r["target"], r["boundary"], r["length"]) == k]
            n = len(v)
            md.append(f"| {k[0]}/{k[1]} | {k[2]} | {k[3]} | {n} | {sum(r['openai_verified'] for r in v)} | {sum(r['azure_pass'] for r in v)} | "
                      f"{sum(r['or_pass'] for r in v)} | {sum(r['hr_proxy'] for r in v)} | {sum(r['spell_openai'] for r in v)} | "
                      f"{sum(r['spell_azure'] for r in v)} | {sum(r['spell_whisper'] for r in v)} |")
    tab("OOV names only (Melos/Brontes/Pelias)", lambda r: r["name"] != "Kallis")
    tab("Control name (Kallis, CMU-registered)", lambda r: r["name"] == "Kallis")

    def cnt(sel, key):
        v = [r for r in rows if sel(r)]
        return sum(r[key] for r in v), len(v)

    md.append("\n## Effects (OOV names; metric = OR PASS / OpenAI PASS; Fisher two-sided p; pooled over level/target)\n")
    for metric in ("or_pass", "openai_verified", "spell_openai"):
        md.append(f"\n### metric={metric}")
        oov = lambda r: r["name"] != "Kallis"
        for desc, s1, s2 in [
            ("length effect within nss: L7 vs L2", lambda r: oov(r) and r["boundary"] == "nss" and r["length"] == "L7", lambda r: oov(r) and r["boundary"] == "nss" and r["length"] == "L2"),
            ("length effect within ss : L7 vs L2", lambda r: oov(r) and r["boundary"] == "ss" and r["length"] == "L7", lambda r: oov(r) and r["boundary"] == "ss" and r["length"] == "L2"),
            ("s+s effect within L2: nss vs ss", lambda r: oov(r) and r["length"] == "L2" and r["boundary"] == "nss", lambda r: oov(r) and r["length"] == "L2" and r["boundary"] == "ss"),
            ("s+s effect within L7: nss vs ss", lambda r: oov(r) and r["length"] == "L7" and r["boundary"] == "nss", lambda r: oov(r) and r["length"] == "L7" and r["boundary"] == "ss"),
            ("s+s effect within L4: nss vs ss", lambda r: oov(r) and r["length"] == "L4" and r["boundary"] == "nss", lambda r: oov(r) and r["length"] == "L4" and r["boundary"] == "ss"),
            ("length effect within nss: L4 vs L2", lambda r: oov(r) and r["boundary"] == "nss" and r["length"] == "L4", lambda r: oov(r) and r["boundary"] == "nss" and r["length"] == "L2"),
        ]:
            x1, n1 = cnt(s1, metric)
            x2, n2 = cnt(s2, metric)
            p = fisher_p(x1, n1 - x1, x2, n2 - x2)
            md.append(f"- {desc}: {x1}/{n1} vs {x2}/{n2}  Fisher p={p:.4f}")
        # 交互作用(差の差)
        def rate(b, L):
            x, n = cnt(lambda r: r["name"] != "Kallis" and r["boundary"] == b and r["length"] == L, metric)
            return x / n if n else float("nan")
        did = (rate("nss", "L7") - rate("nss", "L2")) - (rate("ss", "L7") - rate("ss", "L2"))
        md.append(f"- 2x2 rates: ss/L2={rate('ss','L2'):.2f} ss/L7={rate('ss','L7'):.2f} nss/L2={rate('nss','L2'):.2f} nss/L7={rate('nss','L7'):.2f}; 交互作用(差の差: 長さ効果[nss]-長さ効果[ss])={did:+.2f}")
    md.append("\n## by name x boundary x length (OR PASS / n)")
    names = sorted({r["name"] for r in rows})
    for nm in names:
        line = [f"{nm}:"]
        for L in ("L2", "L4", "L7"):
            for b in ("ss", "nss"):
                v = [r for r in rows if r["name"] == nm and r["length"] == L and r["boundary"] == b]
                line.append(f"{L}/{b}={sum(r['or_pass'] for r in v)}/{len(v)}")
        md.append("- " + " ".join(line))
    # Std slowdown effect
    md.append("\n## Std: raw(減速前) -> slow6(減速後)")
    for tg in ("raw", "slow6"):
        v = [r for r in rows if r["level"] == "std" and r["target"] == tg and r["name"] != "Kallis"]
        md.append(f"- {tg}: OpenAI PASS {sum(r['openai_verified'] for r in v)}/{len(v)}, Azure PASS {sum(r['azure_pass'] for r in v)}/{len(v)}, OR {sum(r['or_pass'] for r in v)}/{len(v)}")
    v = [r for r in rows if r["level"] == "adv" and r["name"] != "Kallis"]
    md.append(f"- adv(raw): OpenAI PASS {sum(r['openai_verified'] for r in v)}/{len(v)}, Azure PASS {sum(r['azure_pass'] for r in v)}/{len(v)}, OR {sum(r['or_pass'] for r in v)}/{len(v)}")
    # sample transcripts
    md.append("\n## transcript samples (OpenAI / Azure) L2 ss vs nss, OOV names, raw")
    for b in ("ss", "nss"):
        for r in [x for x in rows if x["name"] != "Kallis" and x["length"] == "L2" and x["boundary"] == b and x["target"] == "raw"][:9]:
            md.append(f"- {r['job']}: OA='{r['openai']['text']}' AZ='{r['azure']['text']}' WH='{r['whisper_small']['text']}'")
    open(a.out, "w", encoding="utf8").write("\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    main()
