#!/usr/bin/env python3
"""fact_safety_p01: After台帳のFact安全性 照合材料を出す(合否判定はしない)。
入力: After台帳txt / After draft JSON / After verification JSON / Before台帳txt(類似fact比較用)。
regex・parseは ledger_diff_p01.py から流用(import)。
verification JSONの引用source相当フィールドは 'verification_notes' のみ(Before構造確認済み、専用のsource引用フィールドは無い)。"""
import argparse, json, re, statistics, sys, unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ledger_diff_p01 as L  # noqa: E402

CHECK_KEYS = ("notes_for_writer", "conditions")  # claim は別扱い
URL_MD_RE = re.compile(r"\(\[[^\]]*\]\([^)]*\)\)|\[[^\]]*\]\([^)]*\)|https?://\S+")
ARBITRARY_RE = re.compile(r"^\s*(順序|語義)\s*[:：]")


def nfkc(s):
    return unicodedata.normalize("NFKC", s or "").replace(",", "")


def load_json(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def strip_urls(s):
    return URL_MD_RE.sub("", s or "")


def n_neg(text):
    return sum(text.count(m) for m in L.NEGATION_MARKERS_JA) + len(L.NEGATION_EN_RE.findall(text))


def n_cau(text):
    return len(L.CAUSAL_JA_RE.findall(text))


def fact_text(b):
    return " ".join([b["claim"]] + [b["keys"].get(k, "") for k in CHECK_KEYS])


def best_before(text_claim, B):
    a, best = L.toks(text_claim), (None, 0.0)
    for fid, b in B.items():
        t = L.toks(b["claim"])
        u = len(a | t)
        j = len(a & t) / u if u else 0
        if j > best[1]:
            best = (fid, j)
    return best


def count_nl(o):
    if isinstance(o, str):
        return o.count("\n")
    if isinstance(o, dict):
        return sum(count_nl(v) for v in o.values())
    if isinstance(o, list):
        return sum(count_nl(v) for v in o)
    return 0


def mean(xs):
    return round(statistics.mean(xs), 2) if xs else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--after-txt", required=True)
    ap.add_argument("--after-draft", required=True)
    ap.add_argument("--after-verif", required=True)
    ap.add_argument("--before-txt", required=True)
    ap.add_argument("--out", required=True, help="出力prefix(.json/.md)")
    a = ap.parse_args()
    A, ao, ai = L.parse(a.after_txt)
    B, bo, bi = L.parse(a.before_txt)
    draft = load_json(a.after_draft)
    verif = load_json(a.after_verif)
    dmap = {f.get("fact_id"): f for f in draft.get("facts", [])}
    vmap = {v.get("fact_id"): v for v in verif.get("verifications", [])}

    per, ungrounded_total = {}, 0
    for fid in ao:
        b = A[fid]
        d, v = dmap.get(fid, {}), vmap.get(fid, {})
        # (a) 接地: 同factのdraft構造化フィールド + verification_notes(引用source相当)
        ground = nfkc(" ".join(str(d.get(k) or "") for k in
                               ("numeric_value", "numeric_scope", "date_or_period", "subject", "source_title", "source_url"))
                      + " " + str(v.get("verification_notes") or ""))
        glow = ground.lower()
        ungr = {}
        for fld, txt in [("claim", b["claim"])] + [(k, b["keys"].get(k, "")) for k in CHECK_KEYS]:
            s = strip_urls(txt)
            f = L.feats(s)
            claim_n = nfkc(strip_urls(b["claim"]))
            miss = {"numbers": sorted(x for x in f["numbers"] if x.split()[0] not in ground),
                    "dates": sorted(x for x in f["dates"] if nfkc(x) not in ground),
                    "proper": sorted(x for x in f["proper"] if x.lower() not in glow
                                     and (fld == "claim" or x not in claim_n))}
            miss = {k: x for k, x in miss.items() if x}
            if miss:
                ungr[fld] = miss
        ungrounded_total += sum(len(x) for m in ungr.values() for x in m.values())
        # (b)(e) Before類似fact比較
        bf, j = best_before(b["claim"], B)
        bb = B.get(bf)
        txt_a = fact_text(b)
        r = {"claim": b["claim"], "ungrounded_tokens": ungr, "has_draft": fid in dmap, "has_verif": fid in vmap,
             "before_match": {"fact_id": bf, "jaccard": round(j, 3)}}
        if bb:
            txt_b = fact_text(bb)
            r["negation_count"] = {"after": n_neg(txt_a), "before_similar": n_neg(txt_b), "delta": n_neg(txt_a) - n_neg(txt_b)}
            r["causal_count"] = {"after": n_cau(txt_a), "before_similar": n_cau(txt_b), "delta": n_cau(txt_a) - n_cau(txt_b)}
            ca, cb = L.feats(b["claim"]), L.feats(bb["claim"])
            br_a, br_b = len(L.BRACKET_RE.findall(b["claim"])), len(L.BRACKET_RE.findall(bb["claim"]))
            nm_a, nm_b = len(L.NUMBER_MARK_RE.findall(b["claim"])), len(L.NUMBER_MARK_RE.findall(bb["claim"]))
            r["m4_claim"] = {"bracket_before_after": [br_b, br_a], "numbermark_before_after": [nm_b, nm_a],
                             "new_negation": sorted(ca["negation"] - cb["negation"]), "new_causal": sorted(ca["causal"] - cb["causal"]),
                             "flag": br_a > br_b or nm_a > nm_b or bool(ca["negation"] - cb["negation"]) or bool(ca["causal"] - cb["causal"])}
        # (c) 改行(draft/verification全フィールド)
        r["newlines_draft"] = count_nl(d)
        r["newlines_verif"] = count_nl(v)
        # (d)
        r["claim_chars"] = len(b["claim"])
        nfw = b["keys"].get("notes_for_writer", "")
        r["notes_chars"] = len(nfw)
        # (f)
        m = ARBITRARY_RE.match(nfw)
        r["notes_arbitrary_prefix"] = m.group(1) if m else None
        per[fid] = r

    ca_mean = mean([r["claim_chars"] for r in per.values()])
    cb_mean = mean([len(b["claim"]) for b in B.values()])
    summary = {
        "n_facts_after": len(A), "n_facts_before": len(B),
        "ungrounded_token_total": ungrounded_total,
        "facts_with_ungrounded": [f for f, r in per.items() if r["ungrounded_tokens"]],
        "negation_delta_total": sum(r.get("negation_count", {}).get("delta", 0) for r in per.values()),
        "causal_delta_total": sum(r.get("causal_count", {}).get("delta", 0) for r in per.values()),
        "newlines_total_draft": sum(r["newlines_draft"] for r in per.values()),
        "newlines_total_verif": sum(r["newlines_verif"] for r in per.values()),
        "claim_chars_mean_after": ca_mean, "claim_chars_mean_before": cb_mean,
        "claim_chars_ratio_after_over_before": round(ca_mean / cb_mean, 3) if cb_mean else None,
        "notes_chars_mean_after": mean([r["notes_chars"] for r in per.values()]),
        "notes_chars_mean_before": mean([len(b["keys"].get("notes_for_writer", "")) for b in B.values()]),
        "m4_flagged_facts": [f for f, r in per.items() if r.get("m4_claim", {}).get("flag")],
        "notes_with_arbitrary_prefix": {f: r["notes_arbitrary_prefix"] for f, r in per.items() if r["notes_arbitrary_prefix"]},
        "format_issue_count_after": len(ai), "format_issue_count_before": len(bi),
        "draft_fact_ids_missing_in_txt": sorted(set(dmap) - set(A)),
        "txt_fact_ids_missing_in_draft": sorted(set(A) - set(dmap)),
        "txt_fact_ids_missing_in_verif": sorted(set(A) - set(vmap)),
    }
    res = {"tool": "fact_safety_p01", "judgement": "none(照合材料のみ。合否はFable/ユーザー)", "regex_source": L.REGEX_SOURCE,
           "grounding_note": "接地源=同factのdraft(numeric_value/numeric_scope/date_or_period/subject/source_title/source_url)+verification_notes。URL/リンクは検査対象から除外。",
           "inputs": {"after_txt": a.after_txt, "after_draft": a.after_draft, "after_verif": a.after_verif, "before_txt": a.before_txt},
           "summary": summary, "format_issues": {"after": ai, "before": bi}, "per_fact": per}
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    Path(str(out) + ".json").write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    md = ["# fact_safety_p01 (判定なし/照合材料)", f"regex: {L.REGEX_SOURCE}", "", "## summary", "```json",
          json.dumps(summary, ensure_ascii=False, indent=1), "```",
          f"- 書式違反(非ASCIIキー行/ブロック内空行等) After {len(ai)}件 / Before {len(bi)}件"]
    md += [f"  - A {json.dumps(x, ensure_ascii=False)}" for x in ai]
    md += ["", "## 未接地トークン(fact別)"]
    md += [f"- {f}: {json.dumps(r['ungrounded_tokens'], ensure_ascii=False)}" for f, r in per.items() if r["ungrounded_tokens"]] or ["なし"]
    md += ["", "## 否定語・因果語 増減(Before類似fact比)", "| fact | Before類似(J) | 否定 B→A | 因果 B→A | M4flag | claim文字 |", "|---|---|---|---|---|---|"]
    for f, r in per.items():
        n, c = r.get("negation_count", {}), r.get("causal_count", {})
        md.append(f"| {f} | {r['before_match']['fact_id']}({r['before_match']['jaccard']}) | {n.get('before_similar')}→{n.get('after')} | {c.get('before_similar')}→{c.get('after')} | {r.get('m4_claim', {}).get('flag')} | {r['claim_chars']} |")
    Path(str(out) + ".md").write_text("\n".join(md), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
