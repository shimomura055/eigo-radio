# -*- coding: utf-8 -*-
"""check_notes_only_diff_p02: control txt vs nb txt が「notes_for_writer以外差分0」かを機械判定(PASS/FAIL)。"""
import argparse, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "open233_ledger_clarity_p_trial_01" / "tools"))
import ledger_diff_p01 as L  # noqa: E402

PREFIX = "注意(多義): "
SEP = " / "
KEYS = ("scope", "conditions", "numeric_value", "date_or_period", "causal_strength", "ambiguity_note")


def check(control_txt, nb_txt):
    C, co, ci = L.parse(control_txt)
    N, no, ni = L.parse(nb_txt)
    fails, added = [], {}
    if co != no:
        fails.append({"check": "fact_id_set_or_order", "control": co, "nb": no})
    if ci or ni:
        fails.append({"check": "parse_issues", "control": ci, "nb": ni})
    for fid in co:
        if fid not in N:
            continue
        c, n = C[fid], N[fid]
        if c["claim"] != n["claim"] or c["tag"] != n["tag"]:
            fails.append({"check": "claim_or_tag", "fact_id": fid})
        for k in KEYS:
            if c["keys"].get(k) != n["keys"].get(k):
                fails.append({"check": "field_" + k, "fact_id": fid, "control": c["keys"].get(k), "nb": n["keys"].get(k)})
        if set(c["keys"]) - {"notes_for_writer"} != set(n["keys"]) - {"notes_for_writer"}:
            fails.append({"check": "key_set", "fact_id": fid})
        cn, nn = c["keys"].get("notes_for_writer"), n["keys"].get("notes_for_writer")
        if cn != nn:
            if not nn or (cn and not nn.startswith(cn + SEP)):
                fails.append({"check": "existing_notes_modified", "fact_id": fid, "control": cn, "nb": nn})
                continue
            add = nn[len(cn) + len(SEP):] if cn else nn
            added[fid] = add
            if not add.startswith(PREFIX):
                fails.append({"check": "bad_prefix", "fact_id": fid, "added": add})
            if len(add) > 80:
                fails.append({"check": "too_long", "fact_id": fid, "len": len(add)})
            if "\n" in add:
                fails.append({"check": "newline", "fact_id": fid})
    # 行単位: notes_for_writer行を除いた全行が完全一致
    cl = [x for x in Path(control_txt).read_text(encoding="utf-8").split("\n") if "notes_for_writer:" not in x]
    nl = [x for x in Path(nb_txt).read_text(encoding="utf-8").split("\n") if "notes_for_writer:" not in x]
    if cl != nl:
        fails.append({"check": "non_notes_line_diff", "control_lines": len(cl), "nb_lines": len(nl)})
    return {"result": "PASS" if not fails else "FAIL", "added_notes": added, "added_count": len(added), "fails": fails}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--control", required=True)
    ap.add_argument("--nb", required=True)
    ap.add_argument("--out", required=True, help="出力prefix(.json/.md)")
    a = ap.parse_args()
    r = check(a.control, a.nb)
    Path(a.out + ".json").write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
    md = ["# notes以外差分0検査: " + r["result"], "付与note数: %d" % r["added_count"], ""]
    md += ["- %s: %s" % (k, v) for k, v in r["added_notes"].items()] + [""] + ["- FAIL %s" % f for f in r["fails"]]
    Path(a.out + ".md").write_text("\n".join(md), encoding="utf-8")
    print(r["result"])
    return 0 if r["result"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
