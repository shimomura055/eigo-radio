# -*- coding: utf-8 -*-
"""委任_02 集計(API呼出なし)。python ... --results results_02.json --results01 results_01.json --out results_summary_02.md"""
import sys, os, json, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from er069_attribution_clip_split_trial_01_summarize import fisher_p

VORDER = ["said", "says", "sighed", "replied", "answered", "asked"]


def cnt(rows, key):
    return sum(bool(r.get(key)) for r in rows), len(rows)


def fmt(rows, key):
    x, n = cnt(rows, key)
    return f"{x}/{n}"


def compare(rows, sel1, sel2, key):
    a = [r for r in rows if sel1(r)]
    b = [r for r in rows if sel2(r)]
    x1, n1 = cnt(a, key)
    x2, n2 = cnt(b, key)
    return x1, n1, x2, n2, fisher_p(x1, n1 - x1, x2, n2 - x2) if n1 and n2 else float("nan")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True)
    ap.add_argument("--results01", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    R = json.load(open(a.results, encoding="utf8"))
    rows = R["rows"]
    R1 = json.load(open(a.results01, encoding="utf8"))
    rows1 = [r for r in R1["rows"] if r["length"] == "L2" and r["name"] in ("Melos", "Brontes")]
    md = [f"# results summary (委任_02)\n\nobs={R['n_obs']} gen_tts_jpy={R['gen_tts_jpy']} total_jpy={R['total_jpy']}\n"]
    md.append("## (i) 動詞 x 名前 (全level/target pooled)\n| 名前 | 動詞 | 群 | n | OR PASS | OpenAI PASS | Azure PASS | spell OA | spell Az | spell WH |\n|---|---|---|---|---|---|---|---|---|---|")
    for nm in ("Melos", "Brontes"):
        for v in VORDER:
            v_ = [r for r in rows if r["name"] == nm and r["verb"] == v]
            md.append(f"| {nm} | {v} | {v_[0]['vgroup']} | {len(v_)} | {fmt(v_,'or_pass')} | {fmt(v_,'openai_verified')} | {fmt(v_,'azure_pass')} | {fmt(v_,'spell_openai')} | {fmt(v_,'spell_azure')} | {fmt(v_,'spell_whisper')} |")
    md.append("\n## (ii) 要因分離 (s群{said,says,sighed} vs 非s群{replied,answered,asked}; Fisher two-sided、観測単位=過小評価)")
    for nm in ("Melos", "Brontes", None):
        sel = (lambda r, nm=nm: nm is None or r["name"] == nm)
        for key in ("or_pass", "openai_verified", "spell_openai", "spell_azure"):
            x1, n1, x2, n2, p = compare(rows, lambda r: sel(r) and r["vgroup"] == "ns", lambda r: sel(r) and r["vgroup"] == "s", key)
            md.append(f"- {nm or 'pooled'} {key}: 非s群 {x1}/{n1} vs s群 {x2}/{n2} p={p:.4f}")
    md.append("\n動詞別 vs 非s群(Melos):")
    for key in ("or_pass", "openai_verified", "spell_openai"):
        for v in ("said", "says", "sighed"):
            x1, n1, x2, n2, p = compare(rows, lambda r: r["name"] == "Melos" and r["vgroup"] == "ns", lambda r, v=v: r["name"] == "Melos" and r["verb"] == v, key)
            md.append(f"- Melos {key}: 非s群 {x1}/{n1} vs {v} {x2}/{n2} p={p:.4f}")
        x1, n1, x2, n2, p = compare(rows, lambda r: r["name"] == "Melos" and r["verb"] in ("says", "sighed"), lambda r: r["name"] == "Melos" and r["verb"] == "said", key)
        md.append(f"- Melos {key}: said以外のs始まり(says+sighed) {x1}/{n1} vs said {x2}/{n2} p={p:.4f}")
    md.append("\n## (iii) 委任_01(L2)との再現一致 (Melos/Brontes, said=ss, replied=nss; OR PASS / OpenAI PASS / spell OA)")
    for nm in ("Melos", "Brontes"):
        for v in ("said", "replied"):
            a1 = [r for r in rows1 if r["name"] == nm and r["verb"] == v] if rows1 and "verb" in rows1[0] else [r for r in rows1 if r["name"] == nm and r["boundary"] == ("ss" if v == "said" else "nss")]
            a2 = [r for r in rows if r["name"] == nm and r["verb"] == v]
            md.append(f"- {nm} {v}: 委任_01 OR {fmt(a1,'or_pass')} / OA {fmt(a1,'openai_verified')} / spell {fmt(a1,'spell_openai')}  |  委任_02 OR {fmt(a2,'or_pass')} / OA {fmt(a2,'openai_verified')} / spell {fmt(a2,'spell_openai')}")
    md.append("\n## (iv) level/target別 (Melos | Brontes; OR PASS / OpenAI PASS) 群別")
    md.append("| level/target | 群 | Melos n | Melos OR | Melos OA | Brontes n | Brontes OR | Brontes OA |\n|---|---|---|---|---|---|---|---|")
    for lv, tg in (("std", "raw"), ("std", "slow6"), ("adv", "raw")):
        for vg in ("s", "ns"):
            m = [r for r in rows if r["level"] == lv and r["target"] == tg and r["vgroup"] == vg and r["name"] == "Melos"]
            b = [r for r in rows if r["level"] == lv and r["target"] == tg and r["vgroup"] == vg and r["name"] == "Brontes"]
            md.append(f"| {lv}/{tg} | {vg} | {len(m)} | {fmt(m,'or_pass')} | {fmt(m,'openai_verified')} | {len(b)} | {fmt(b,'or_pass')} | {fmt(b,'openai_verified')} |")
    md.append("\n## (v) Azure Phrase Listなし (Melos x said/replied、全take x 3obs)")
    for v in ("said", "replied"):
        v_ = [r for r in rows if r["name"] == "Melos" and r["verb"] == v and "azure_np" in r]
        np_ = sum(r["azure_np_pass"] for r in v_)
        ors = sum(r["openai_verified"] or r["azure_np_pass"] for r in v_)
        md.append(f"- Melos {v}: n={len(v_)} Azure(PhraseListなし) PASS {np_}/{len(v_)}, 綴り一致 {sum(r['spell_azure_np'] for r in v_)}/{len(v_)}; Azure(PhraseListあり) PASS {fmt(v_,'azure_pass')}; OpenAI PASS {fmt(v_,'openai_verified')}; OR(OpenAI or AzureなしPL) {ors}/{len(v_)}; OR(Phrase Listあり) {fmt(v_,'or_pass')}")
    md.append("\n## transcript samples (Melos, raw/adv, 動詞別 OpenAI | Azure)")
    for v in VORDER:
        for r in [x for x in rows if x["name"] == "Melos" and x["verb"] == v and x["target"] == "raw"][:4]:
            md.append(f"- {r['job']}: OA='{r['openai']['text']}' AZ='{r['azure']['text']}' WH='{r['whisper_small']['text']}'")
    open(a.out, "w", encoding="utf8").write("\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    main()
