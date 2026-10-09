# -*- coding: utf-8 -*-
"""FIX01-B read-only audit: ledger heading count (all formats) vs facts actually passed to Risk Flagger.
Reads only; writes ledger_audit_01.json next to this script. No API, no edits to existing code."""
import json, os, re, sys, glob, collections
HERE = os.path.dirname(os.path.abspath(__file__))
RF = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(RF, "..", ".."))
sys.path.insert(0, os.path.join(RF, "detectors"))
import ledger_restore_01 as LR  # read-only import (existing parser, unchanged)

# lenient heading: column0 '[' TAG ']' ID ':'  (TAG = anything without ']'; ID = no whitespace/colon). Half/full-width colon.
LEN = re.compile(r"^\[(?P<tag>[^\]\n]+)\]\s+(?P<id>[^\s:：]+)\s*[:：]\s*(?P<text>.*)$")

def rel(p): return os.path.relpath(p, REPO).replace("\\", "/")
def jl(p): return json.load(open(p, encoding="utf-8"))

def lenient_headings(path):
    out = []
    for i, ln in enumerate(open(path, encoding="utf-8", errors="replace").read().splitlines(), 1):
        m = LEN.match(ln)
        if m:
            out.append(dict(line=i, tag=m.group("tag"), fact_id=m.group("id"), head=ln[:160]))
    return out

def block_text(path, fid):
    for f in LR.parse_ledger_file(path):
        if f["fact_id"] == fid: return f["text"]
    # not parsed: re-read lenient block
    lines = open(path, encoding="utf-8", errors="replace").read().splitlines()
    for i, ln in enumerate(lines):
        m = LEN.match(ln)
        if m and m.group("id") == fid:
            blk = [m.group("text")]
            for l2 in lines[i+1:]:
                if not l2.strip(): break
                blk.append(l2.rstrip())
            return "\n".join(blk)

def ledger_report(path):
    strict = {f["fact_id"] for f in LR.parse_ledger_file(path)}
    heads = lenient_headings(path)
    miss = [h for h in heads if h["fact_id"] not in strict]
    for h in miss: h["text"] = block_text(path, h["fact_id"])
    tags = collections.Counter(h["tag"] for h in heads)
    return dict(path=rel(path), n_headings_lenient=len(heads), n_parsed_strict=len(strict),
                n_missing=len(miss), tags=dict(tags),
                lenient_ids=[h["fact_id"] for h in heads], missing=miss)

def main():
    cb = jl(os.path.join(RF, "casebank", "casebank_01.json"))
    origin = jl(os.path.join(RF, "casebank", "casebank_01_ledger_origin.json"))
    manifest = jl(os.path.join(RF, "casebank", "p3_manifest_01.json"))
    res = dict(ledgers={}, cases=[], articles=[], note="n_sent = facts actually given to detector (blind file ledger[]); n_full = lenient heading count of origin ledger")
    def L(path):
        if path not in res["ledgers"]: res["ledgers"][path] = ledger_report(os.path.join(REPO, path))
        return res["ledgers"][path]
    # --- case mode
    cases_by_id = {c["case_id"]: c for c in cb["cases"]}
    for split in ["dev", "dev_reg3", "holdout", "synthetic_dev", "synthetic_holdout"]:
        b = jl(os.path.join(RF, "casebank", "casebank_01_%s_blind.json" % split))
        for c in b["cases"]:
            cid = c["case_id"]; sent = [f["fact_id"] for f in c["ledger"]]
            o = origin.get(cid); row = dict(set=split, case_id=cid, lang=c["lang"], fact_id=c["fact"]["id"], n_sent=len(sent), sent_ids=sent)
            if o:
                lp = o.split(":", 1)[1]; row["ledger_path"] = lp; row["origin_kind"] = o.split(":", 1)[0]
                rep = L(lp); full = rep["lenient_ids"]
                row["n_full"] = len(full); row["missing_ids"] = [x for x in full if x not in sent]
                row["extra_ids_sent"] = [x for x in sent if x not in full]
                row["case_fact_is_missing_in_parser"] = c["fact"]["id"] in [m["fact_id"] for m in rep["missing"]]
            else:
                row["ledger_path"] = None; row["note"] = "ledger origin not in casebank_01_ledger_origin.json (synthetic or unresolved)"
            if cid in cases_by_id: row["theme_src"] = (cases_by_id[cid].get("fact") or {}).get("src")
            res["cases"].append(row)
    # --- article mode
    for m in manifest:
        if "ledger_path" in m:
            rep = L(m["ledger_path"]); sent = [f["fact_id"] for f in LR.parse_ledger_file(os.path.join(REPO, m["ledger_path"]))]
            lp = m["ledger_path"]
        else:
            b = jl(os.path.join(RF, "casebank", "casebank_01_%s_blind.json" % m["ledger_split"]))
            c = next(x for x in b["cases"] if x["case_id"] == m["ledger_case"]); sent = [f["fact_id"] for f in c["ledger"]]
            lp = origin[m["ledger_case"]].split(":", 1)[1]; rep = L(lp)
        full = rep["lenient_ids"]
        res["articles"].append(dict(article_id=m["article_id"], role=m["role"], theme=m["theme"], arm=m["arm"], lang=m["lang"],
            ledger_path=lp, n_sent=len(sent), n_full=len(full), missing_ids=[x for x in full if x not in sent]))
    # --- repo-wide survey of ledger heading forms (root-cause evidence)
    surv = dict(files=0, strict_headings=0, lenient_headings=0, by_tag=collections.Counter(), files_with_parser_miss={}, other_col0_bracket_lines=collections.Counter(), other_col0_examples={})
    cands = []
    for root, dirs, fs in os.walk(REPO):
        dirs[:] = [d for d in dirs if d not in (".git", "node_modules", "__pycache__")]
        for fn in fs:
            if fn in ("verified_fact_ledger.txt", "ledger.txt"): cands.append(os.path.join(root, fn))
    for p in sorted(cands):
        txt = open(p, encoding="utf-8", errors="replace").read(); surv["files"] += 1
        strict = LR.parse_ledger_text(txt); heads = []
        for ln in txt.splitlines():
            m = LEN.match(ln)
            if m: heads.append((m.group("tag"), m.group("id")))
            elif ln.startswith("[") or ln.startswith("［"):
                k = re.sub(r"[A-Za-z0-9_\-]+", "X", ln[:18]); surv["other_col0_bracket_lines"][k] += 1; surv["other_col0_examples"].setdefault(k, rel(p) + " :: " + ln[:100])
        surv["strict_headings"] += len(strict); surv["lenient_headings"] += len(heads)
        for t, _ in heads: surv["by_tag"][t] += 1
        sids = {f["fact_id"] for f in strict}; miss = [i for t, i in heads if i not in sids]
        if miss: surv["files_with_parser_miss"][rel(p)] = dict(n_headings=len(heads), n_parsed=len(strict), missing_ids=miss)
    surv["by_tag"] = dict(surv["by_tag"]); surv["other_col0_bracket_lines"] = dict(surv["other_col0_bracket_lines"])
    res["repo_survey"] = surv
    # --- heading variant matrix against the existing strict parser (synthetic probes, existing code unchanged)
    probes = [
        ("[VERIFIED] F01: x", "normal"),
        ("[AMBIGUOUS - 断定禁止、曖昧さを保持すること] F01: x", "generator AMBIGUOUS tag (space, hyphen, Japanese in tag)"),
        ("[AMBIGUOUS] F01: x", "plain AMBIGUOUS tag"),
        ("[PARTIALLY_SUPPORTED] F01: x", "other uppercase_underscore tag"),
        ("[verified] F01: x", "lowercase tag"),
        ("[VERIFIED]F01: x", "no space after tag"),
        ("[VERIFIED]  F01: x", "two spaces"),
        ("[VERIFIED] F01： x", "fullwidth colon after id"),
        ("［VERIFIED］ F01: x", "fullwidth brackets"),
        ("[VERIFIED] F-01: x", "hyphen id"),
        ("[VERIFIED] F01 : x", "space before colon"),
        ("[VERIFIED] [F01]: x", "bracketed id"),
        ("- [VERIFIED] F01: x", "list bullet prefix"),
        (" [VERIFIED] F01: x", "leading space"),
        ("[F-001] x (no tag/colon style in pool_pilot ledgers)", "pool_pilot style"),
        ("[VOICE_1_EVIDENCE] 1-01(R1_x): x", "voices ledger style"),
        ("[VERIFIED] F01:x", "no space after colon"),
    ]
    vm = []
    for line, note in probes:
        vm.append(dict(line=line[:70], note=note, strict_parser_reads=bool(LR.parse_ledger_text(line + chr(10))), lenient_reads=bool(LEN.match(line))))
    res["variant_matrix"] = vm
    # --- contamination check: does a skipped heading's block leak into the previous fact's text?
    leaks = []
    for lp, rep in res["ledgers"].items():
        if not rep["n_missing"]: continue
        facts = LR.parse_ledger_file(os.path.join(REPO, lp))
        for m in rep["missing"]:
            probe = (m["text"] or "").split(chr(10))[0][:20]
            for f in facts:
                if probe and probe in f["text"]: leaks.append((lp, m["fact_id"], f["fact_id"]))
    res["contamination_leaks"] = leaks
    json.dump(res, open(os.path.join(HERE, "ledger_audit_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("ledgers", len(res["ledgers"]), "with missing:", [(k, v["n_missing"]) for k, v in res["ledgers"].items() if v["n_missing"]])
    print("cases", len(res["cases"]), "cases w/ missing:", sum(1 for r in res["cases"] if r.get("missing_ids")))
    print("survey files", surv["files"], "strict", surv["strict_headings"], "lenient", surv["lenient_headings"], "files_with_miss", len(surv["files_with_parser_miss"]))
    print("leaks", res["contamination_leaks"]); print("articles", len(res["articles"]), "w/ missing:", sum(1 for r in res["articles"] if r["missing_ids"]))
main()
