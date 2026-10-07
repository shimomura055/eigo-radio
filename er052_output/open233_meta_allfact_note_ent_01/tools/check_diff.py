# -*- coding: utf-8 -*-
import sys, json
from pathlib import Path
sys.path.insert(0, "er052_output/open233_ledger_clarity_p_trial_01/tools")
import ledger_diff_p01 as L
B = Path("er052_output/open233_meta_allfact_note_ent_01/ledger")
c = (Path("er052_output/open233_meta_rollback_minimal_note_01/ledger/control/research_ledger/verified_fact_ledger.txt")).read_bytes()
cl = c.decode("utf-8").split("\r\n")
res = {}
for m in ("p1", "p2"):
    n = (B / m / "research_ledger" / "verified_fact_ledger.txt").read_bytes().decode("utf-8").split("\r\n")
    ok = len(cl) == len(n)
    nonnote_diff = [i for i, (a, b) in enumerate(zip(cl, n)) if a != b and not a.startswith("  notes_for_writer:")]
    changed = sum(1 for a, b in zip(cl, n) if a != b)
    C, co, ci = L.parse("er052_output/open233_meta_rollback_minimal_note_01/ledger/control/research_ledger/verified_fact_ledger.txt"); N, no, ni = L.parse(str(B / m / "research_ledger" / "verified_fact_ledger.txt"))
    ex_ok = all(N[f]["keys"]["notes_for_writer"].find(C[f]["keys"]["notes_for_writer"]) >= 0 for f in co)
    res[m] = {"line_count_equal": ok, "non_notes_diff_lines": nonnote_diff, "changed_lines": changed, "fact_ids_equal": co == no, "fact_count": len(co), "existing_notes_preserved": ex_ok, "crlf_only": b"\n" not in (B / m / "research_ledger" / "verified_fact_ledger.txt").read_bytes().replace(b"\r\n", b""), "PASS": ok and not nonnote_diff and co == no and ex_ok and changed == len(co)}
print(json.dumps(res, ensure_ascii=False, indent=1))
(B / "diff_report.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
