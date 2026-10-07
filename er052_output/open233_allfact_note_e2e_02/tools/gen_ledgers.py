# -*- coding: utf-8 -*-
import hashlib, json, re, sys
from pathlib import Path
sys.path.insert(0, "er052_output/open233_ledger_clarity_p_trial_01/tools")
import ledger_diff_p01 as L
B = Path("er052_output/open233_allfact_note_e2e_02")
T2 = Path("er052_output/open233_polysemy_trial_02/ledgers")
TXT = "この表現は多義的なので、単語だけで機械的に解釈・翻訳せず、原文の文脈・主体・対象・前後関係から意味を確定して記事化すること。"
EMPTY = {"", "なし", "無し", "-", "—", "特になし", "(なし)", "（なし）", "none", "None", "N/A"}
fr = {"note_text": TXT, "themes": {}}
allpass = True
for slug in ["meta", "hormuz", "space_weapons", "sewer", "ai_control"]:
    src = T2 / slug / "control/research_ledger/verified_fact_ledger.txt"
    raw = src.read_bytes()
    prov = json.load(open(f"er052_output/open233_polysemy_trial_04/runs/{slug}/control/rep1/nb_provenance_phase1.json", encoding="utf-8"))
    base_ok = hashlib.sha256(raw).hexdigest() == prov["ledger_txt_sha256"]
    lines = raw.decode("utf-8").split("\r\n")
    out, n, empty = [], 0, 0
    for ln in lines:
        m = re.match(r"^(  notes_for_writer:)\s?(.*)$", ln)
        if not m:
            out.append(ln); continue
        n += 1; ex = m.group(2).strip()
        if ex in EMPTY:
            empty += 1; out.append(f"{m.group(1)} 注意: {TXT}")
        else:
            out.append(f"{m.group(1)} 注意: {ex} / 注意(多義): {TXT}")
    b = "\r\n".join(out).encode("utf-8")
    dst = B / "ledger" / slug / "research_ledger/verified_fact_ledger.txt"
    dst.parent.mkdir(parents=True, exist_ok=True); dst.write_bytes(b)
    nl = b.decode("utf-8").split("\r\n")
    nonnote = [i for i, (a, c) in enumerate(zip(lines, nl)) if a != c and not a.startswith("  notes_for_writer:")]
    C, co, ci = L.parse(str(src)); N, no, ni = L.parse(str(dst))
    ex_ok = all(C[f]["keys"]["notes_for_writer"].strip() in N[f]["keys"]["notes_for_writer"] for f in co)
    both = all(TXT in N[f]["keys"]["notes_for_writer"] for f in no)
    crlf = b"\n" not in b.replace(b"\r\n", b"")
    ok = base_ok and len(lines) == len(nl) and not nonnote and co == no and ex_ok and both and crlf and n == len(co)
    allpass &= ok
    fr["themes"][slug] = {"base_sha256": hashlib.sha256(raw).hexdigest(), "base_matches_trial04_provenance": base_ok,
        "p2_sha256": hashlib.sha256(b).hexdigest(), "fact_count": len(co), "notes_lines": n, "empty_notes": empty,
        "non_notes_diff_lines": nonnote, "fact_ids_equal": co == no, "existing_notes_preserved": ex_ok, "all_have_poly_note": both, "crlf": crlf, "PASS": ok}
fr["ALL_PASS"] = allpass
(B / "ledger/FREEZE.json").write_text(json.dumps(fr, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps(fr, ensure_ascii=False, indent=1))
