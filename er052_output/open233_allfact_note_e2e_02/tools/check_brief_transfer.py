# -*- coding: utf-8 -*-
"""briefに出現するfact_idごとに、台帳の既存notes全文と多義語注意全文の両方が逐語で含まれるか判定。
usage: check_brief_transfer.py <brief.md> <ledger.txt> [--json-out path]"""
import json, re, sys
TXT = "この表現は多義的なので、単語だけで機械的に解釈・翻訳せず、原文の文脈・主体・対象・前後関係から意味を確定して記事化すること。"
def check(brief_path, ledger_path):
    led = open(ledger_path, encoding="utf-8", newline="").read().split("\r\n")
    notes, cur = {}, None
    for ln in led:
        m = re.match(r"^\[[A-Z_]+\]\s+([A-Za-z0-9_\-]+):", ln)
        if m: cur = m.group(1); continue
        m = re.match(r"^  notes_for_writer:\s?(.*)$", ln)
        if m and cur: notes[cur] = m.group(1).strip()
    brief = open(brief_path, encoding="utf-8").read()
    # bullet境界で分割
    parts = re.split(r"(?m)^(?=(?:- )?[A-Z][A-Za-z0-9_\-]*[：:])", brief)
    res = {}
    for p in parts:
        m = re.match(r"(?:- )?([A-Z][A-Za-z0-9_\-]*)[：:]", p)
        if not m or m.group(1) not in notes: continue
        fid = m.group(1); full = notes[fid]
        ex = full[:-len(" / 注意(多義): " + TXT)] if full.endswith(" / 注意(多義): " + TXT) else full
        ex_body = ex[len("注意:"):].strip() if ex.startswith("注意:") else ex
        has_ex = ex_body in p; has_poly = TXT in p
        res[fid] = {"existing_note": has_ex, "poly_note": has_poly, "PASS": has_ex and has_poly}
    out = {"selected_facts": len(res), "both_reached": sum(v["PASS"] for v in res.values()),
           "existing_only": sum(v["existing_note"] and not v["poly_note"] for v in res.values()),
           "poly_only": sum(v["poly_note"] and not v["existing_note"] for v in res.values()),
           "ALL_PASS": bool(res) and all(v["PASS"] for v in res.values()), "per_fact": res}
    return out
if __name__ == "__main__":
    o = check(sys.argv[1], sys.argv[2])
    if "--json-out" in sys.argv:
        open(sys.argv[sys.argv.index("--json-out") + 1], "w", encoding="utf-8").write(json.dumps(o, ensure_ascii=False, indent=1))
    print({k: v for k, v in o.items() if k != "per_fact"})
