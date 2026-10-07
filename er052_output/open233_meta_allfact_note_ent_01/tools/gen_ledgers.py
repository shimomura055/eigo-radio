# -*- coding: utf-8 -*-
import hashlib, json, re, sys
from pathlib import Path
B = Path("er052_output/open233_meta_allfact_note_ent_01")
SRC = Path("er052_output/open233_meta_rollback_minimal_note_01/ledger/control/research_ledger/verified_fact_ledger.txt")
TXT = "この表現は多義的なので、単語だけで機械的に解釈・翻訳せず、原文の文脈・主体・対象・前後関係から意味を確定して記事化すること。"
raw = SRC.read_bytes()
lines = raw.decode("utf-8").split("\r\n")
def build(mode):
    out, n = [], 0
    for ln in lines:
        m = re.match(r"^(  notes_for_writer:)\s?(.*)$", ln)
        if not m:
            out.append(ln); continue
        n += 1
        ex = m.group(2).strip()
        if mode == "p1":
            new = f"{m.group(1)} {ex} / 注意(多義): {TXT}" if ex else f"{m.group(1)} 注意(多義): {TXT}"
        else:
            new = f"{m.group(1)} 注意: {ex} / 注意(多義): {TXT}" if ex else f"{m.group(1)} 注意: {TXT}"
        out.append(new)
    return "\r\n".join(out).encode("utf-8"), n
fr = {"control_sha256": hashlib.sha256(raw).hexdigest(), "note_text": TXT}
for mode in ("p1", "p2"):
    b, n = build(mode)
    p = B / "ledger" / mode / "research_ledger" / "verified_fact_ledger.txt"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(b)
    fr[mode + "_sha256"] = hashlib.sha256(b).hexdigest(); fr[mode + "_notes_lines"] = n
(B / "ledger" / "FREEZE.json").write_text(json.dumps(fr, ensure_ascii=False, indent=1), encoding="utf-8")
print(fr)
