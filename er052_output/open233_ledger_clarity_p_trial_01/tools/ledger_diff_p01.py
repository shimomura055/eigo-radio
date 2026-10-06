#!/usr/bin/env python3
"""ledger_diff_p01: Before/After verified_fact_ledger.txt の決定論diff(判定はしない、照合材料のみ)。
regex出典: er052_open233_stage1_coverage_checker_01.py L428-429(_NUM_RE/_SCALE), L437(CAUSAL_JA_RE), L442-446(否定語)。
checker本体はdotenv未導入環境でimport不可のため複製(try importで可能なら本物を使う)。"""
import argparse, json, re, unicodedata
from pathlib import Path

REGEX_SOURCE = "duplicated(checker L428-446 equivalent)"
_NUM_RE = re.compile(r"(?<![A-Za-z0-9_.])(\d[\d,]*(?:\.\d+)?)(\s*(?:million|billion|thousand)\b)?", re.I)
CAUSAL_JA_RE = re.compile(r"因果|原因|引き起こ|もたらし|を受けて|を受け、|影響を(?:与え|及ぼ)|によって|により|結果|ため、|ためで|ことで|せい|理由|CAUSAL_STATED")
NEGATION_MARKERS_JA = ("ない", "じゃない", "ではない", "でない", "せず", "未", "非", "無", "なく", "なかっ")
_EN_NEG = ["not", "no", "nor", "none", "neither", "cannot", "nobody", "nothing", "never", "without", "no longer"]
NEGATION_EN_RE = re.compile(r"(?<![\w'-])(?:" + "|".join(re.escape(w).replace(r"\ ", r"\s+") for w in sorted(set(_EN_NEG), key=len, reverse=True)) + r")(?![\w-])|n't\b", re.I)
try:  # 可能ならchecker本物へ差し替え
    import er052_open233_stage1_coverage_checker_01 as _c  # noqa
    _NUM_RE, CAUSAL_JA_RE, NEGATION_MARKERS_JA, NEGATION_EN_RE = _c._NUM_RE, _c.CAUSAL_JA_RE, _c.NEGATION_MARKERS_JA, _c.NEGATION_EN_RE
    REGEX_SOURCE = "imported from checker"
except Exception:
    pass

HEAD_RE = re.compile(r"^\[(?P<tag>[^\]]*)\]\s*(?P<id>[^:\s]+):\s*(?P<claim>.*)$")
KEY_RE = re.compile(r"^\s+([A-Za-z_][A-Za-z0-9_]*):\s?(.*)$")
DATE_RE = re.compile(r"\d{4}年(?:\d{1,2}月(?:\d{1,2}日)?)?|\d{1,2}月\d{1,2}日|\d{4}-\d{2}-\d{2}")
KATA_RE = re.compile(r"[ァ-ヶー]{2,}")
CAP_RE = re.compile(r"\b[A-Z][A-Za-z0-9.\-]*\b")
MIX_RE = re.compile(r"\b(?=[A-Za-z0-9\-]*\d)(?=[A-Za-z0-9\-]*[A-Za-z])[A-Za-z0-9\-]+\b")
BRACKET_RE = re.compile(r"[()（）「」『』\[\]【】]")
NUMBER_MARK_RE = re.compile(r"[①-⑳]|\(\d+\)|（\d+）|第\d+")


def parse(path):
    lines = Path(path).read_text(encoding="utf-8").split("\n")
    blocks, order, issues, cur = {}, [], [], None
    for i, ln in enumerate(lines, 1):
        m = HEAD_RE.match(ln)
        if m:
            cur = {"fact_id": m["id"], "tag": m["tag"], "claim": m["claim"], "keys": {}, "line": i}
            blocks[m["id"]] = cur
            order.append(m["id"])
            continue
        if ln.strip() == "":
            nxt = next((x for x in lines[i:] if x.strip()), None)
            if cur is not None and nxt is not None and not HEAD_RE.match(nxt):
                issues.append({"fact_id": cur["fact_id"], "line": i, "kind": "blank_line_inside_block", "next": nxt[:60]})
            else:
                cur = None
            continue
        if cur is None:
            issues.append({"line": i, "kind": "text_outside_block", "text": ln[:80]})
            continue
        k = KEY_RE.match(ln)
        if k:
            cur["keys"][k[1]] = k[2]
        else:
            issues.append({"fact_id": cur["fact_id"], "line": i, "kind": "non_ascii_or_malformed_key_line", "text": ln.strip()[:80]})
    return blocks, order, issues


def feats(text):
    t = unicodedata.normalize("NFKC", text or "")
    nums = {m.group(1).replace(",", "") + (m.group(2) or "").strip().lower() for m in _NUM_RE.finditer(t)}
    neg = {m for m in NEGATION_MARKERS_JA if m in text} | {x.group(0).lower() for x in NEGATION_EN_RE.finditer(text)}
    cau = {x.group(0) for x in CAUSAL_JA_RE.finditer(text)}
    names = set(KATA_RE.findall(text)) | set(CAP_RE.findall(text)) | set(MIX_RE.findall(t))
    return {"numbers": nums, "dates": set(DATE_RE.findall(t)), "proper": names, "negation": neg, "causal": cau}


def sd(a, b):
    return {"added": sorted(b - a), "removed": sorted(a - b)}


def toks(s):
    return set(re.findall(r"[A-Za-z0-9]+|[ぁ-んァ-ヶー一-龥]{2}", unicodedata.normalize("NFKC", s)))


def best_match(claim, pool):
    a, best = toks(claim), (None, 0.0)
    for fid, b in pool.items():
        tb = toks(b["claim"])
        u = len(a | tb)
        j = len(a & tb) / u if u else 0
        if j > best[1]:
            best = (fid, j)
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--before", required=True)
    ap.add_argument("--after", required=True)
    ap.add_argument("--before-draft")
    ap.add_argument("--after-draft")
    ap.add_argument("--out", required=True, help="出力prefix(.json/.mdを付与)")
    a = ap.parse_args()
    B, bo, bi = parse(a.before)
    A, ao, ai = parse(a.after)
    res = {"regex_source": REGEX_SOURCE, "judgement": "none(照合材料のみ)",
           "fact_ids": {"added": sorted(set(A) - set(B)), "removed": sorted(set(B) - set(A)),
                        "common": sorted(set(A) & set(B)), "n_before": len(B), "n_after": len(A)},
           "per_fact": {}, "unmatched_candidates": {}, "format_issues": {"before": bi, "after": ai}, "claim_m4": {}}
    allids = bo + [x for x in ao if x not in B]
    for fid in allids:
        b, af = B.get(fid), A.get(fid)
        if b and af:
            fb = feats(b["claim"] + " " + " ".join(b["keys"].values()))
            fa = feats(af["claim"] + " " + " ".join(af["keys"].values()))
            res["per_fact"][fid] = {"claim_same": b["claim"] == af["claim"], "tag_before": b["tag"], "tag_after": af["tag"],
                                    "keys_before": sorted(b["keys"]), "keys_after": sorted(af["keys"]),
                                    **{k: sd(fb[k], fa[k]) for k in fb}}
            cb, ca = feats(b["claim"]), feats(af["claim"])
            bb, ba = len(BRACKET_RE.findall(b["claim"])), len(BRACKET_RE.findall(af["claim"]))
            nb, na = len(NUMBER_MARK_RE.findall(b["claim"])), len(NUMBER_MARK_RE.findall(af["claim"]))
            res["claim_m4"][fid] = {"bracket_before": bb, "bracket_after": ba, "numbermark_before": nb, "numbermark_after": na,
                                    "new_negation": sorted(ca["negation"] - cb["negation"]),
                                    "new_causal": sorted(ca["causal"] - cb["causal"]),
                                    "flag_increase": ba > bb or na > nb or bool(ca["negation"] - cb["negation"]) or bool(ca["causal"] - cb["causal"])}
        elif b:
            f, j = best_match(b["claim"], {k: v for k, v in A.items() if k not in B})
            res["unmatched_candidates"][fid] = {"side": "before_only", "candidate_in_after": f, "jaccard": round(j, 3)}
        else:
            f, j = best_match(af["claim"], {k: v for k, v in B.items() if k not in A})
            res["unmatched_candidates"][fid] = {"side": "after_only", "candidate_in_before": f, "jaccard": round(j, 3)}
    for tag, p in (("before_draft", a.before_draft), ("after_draft", a.after_draft)):
        if p:
            try:
                d = json.loads(Path(p).read_text(encoding="utf-8"))
                res[tag] = {"path": p, "n_facts": len(d.get("facts", [])) if isinstance(d, dict) else None}
            except Exception as e:
                res[tag] = {"path": p, "error": str(e)}
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    Path(str(out) + ".json").write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    md = ["# ledger_diff_p01 (判定なし/照合材料)", f"regex: {REGEX_SOURCE}", "",
          f"- fact数 Before={len(B)} After={len(A)} / 追加={res['fact_ids']['added']} 削除={res['fact_ids']['removed']}", "",
          "## 共通factの集合差(空=差分0)"]
    nd = 0
    for fid, r in res["per_fact"].items():
        diffs = {k: r[k] for k in ("numbers", "dates", "proper", "negation", "causal") if r[k]["added"] or r[k]["removed"]}
        if diffs or not r["claim_same"] or r["keys_before"] != r["keys_after"]:
            nd += 1
            md.append(f"- {fid}: claim_same={r['claim_same']} keys {r['keys_before']}->{r['keys_after']} {json.dumps(diffs, ensure_ascii=False)}")
    md += [f"(差分あり {nd}/{len(res['per_fact'])})", "", "## M4 claim行の新規括弧/番号/否定/因果"]
    fl = [f for f, r in res["claim_m4"].items() if r["flag_increase"]]
    md.append("該当: " + (", ".join(fl) if fl else "なし"))
    md += ["", "## 書式違反(M4: 日本語キー行/ブロック内空行)", f"- Before {len(bi)}件 / After {len(ai)}件"]
    for s, lst in (("B", bi), ("A", ai)):
        md += [f"  - {s} {json.dumps(x, ensure_ascii=False)}" for x in lst]
    md += ["", "## ID不一致の類似候補(自動対応付けは確定しない)"]
    md += [f"- {fid}: {json.dumps(r, ensure_ascii=False)}" for fid, r in res["unmatched_candidates"].items()]
    md += ["", "## claim逐語併記", "| fact_id | Before claim | After claim |", "|---|---|---|"]
    for fid in allids:
        def cl(d):
            return d[fid]["claim"].replace("|", "\\|") if fid in d else "(なし)"
        md.append(f"| {fid} | {cl(B)} | {cl(A)} |")
    Path(str(out) + ".md").write_text("\n".join(md), encoding="utf-8")
    print(json.dumps({"n_before": len(B), "n_after": len(A), "facts_with_diff": nd, "m4_flags": fl, "format_issues": [len(bi), len(ai)]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
