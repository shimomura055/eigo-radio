# -*- coding: utf-8 -*-
"""NUANCE-EXPLANATION-PRODUCTION-WIRING-01 委任_02C Track E: 生成されたindex.htmlから、level節ごとの『ニュアンス解説』コーナーの有無・個数・空枠を機械集計し、
コーナーのHTML断片をevidenceへ保存する。API 0。
  py extract_nuance_fragment_02c.py --html <index.html> --label y1_adopt_adv --out-dir docs/research/NUANCE-EXPLANATION-PRODUCTION-WIRING-01/evidence
出力: <out-dir>/<label>__summary.json と、採用level節ごとの <label>__<levelid>__nuance_fragment.html(コーナーが無い節は書かない)。"""
import argparse
import hashlib
import json
import os
import re
import sys

HEADING = "ニュアンス解説"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--html", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--repo", default=None, help="count_empty_study_sections用にrepo rootを指定(省略時は空枠検査をスキップ)")
    a = ap.parse_args(argv)
    raw = open(a.html, "rb").read()
    s = raw.decode("utf-8")
    alias = {"std": "standard", "adv": "advanced"}   # Z: <h2 id='std'> / Y: <h2 id='standard'> / X player: <h2>Standard(A2)</h2>
    heads = [(m.start(), alias.get((m.group(1) or m.group(2)).lower(), (m.group(1) or m.group(2)).lower()))
             for m in re.finditer(r"<h2 id='([a-z0-9_]+)'|<h2>(Advanced|Standard)\(", s)]
    heads = [h for h in heads if h[1] in ("standard", "advanced")]
    secs = {}
    for i, (pos, hid) in enumerate(heads):
        end = heads[i + 1][0] if i + 1 < len(heads) else len(s)
        secs[hid] = s[pos:end]
    os.makedirs(a.out_dir, exist_ok=True)
    summ = {"label": a.label, "html": a.html.replace("\\", "/"), "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(), "sections": {}}
    for hid, body in secs.items():
        n = body.count(f"<h3>{HEADING}</h3>")
        m = re.search(r"<section class='study'><h3>" + HEADING + r"</h3>.*?</section>", body, re.S)
        info = {"nuance_heading_count": n, "has_vocab_h3": "Vocabulary &amp; Expressions" in body, "grammar_h3_count": body.count("<h3>Grammar &amp; Sentence Structure</h3>")}
        if m:
            frag = m.group(0)
            fn = f"{a.label}__{hid}__nuance_fragment.html"
            with open(os.path.join(a.out_dir, fn), "w", encoding="utf-8", newline="\n") as f:
                f.write(frag)
            info["fragment_file"] = fn
            info["fragment_sha256"] = hashlib.sha256(frag.encode("utf-8")).hexdigest()
            info["fragment_chars"] = len(frag)
            info["fragment_empty_body"] = bool(re.fullmatch(r"<section class='study'><h3>" + HEADING + r"</h3>\s*</section>", frag))
        summ["sections"][hid] = info
    summ["total_nuance_heading_count"] = s.count(f"<h3>{HEADING}</h3>")
    if a.repo:
        sys.path.insert(0, a.repo)
        import er120_part2_grammar_production_01 as g
        summ["count_empty_study_sections"] = g.count_empty_study_sections(s)
    with open(os.path.join(a.out_dir, f"{a.label}__summary.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(summ, f, ensure_ascii=False, indent=2)
    print(json.dumps(summ, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
