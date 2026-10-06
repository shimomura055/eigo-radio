# -*- coding: utf-8 -*-
"""eval_notes_p03: パターン×テーマの要素評価(DEV/Trial専用、API非呼出)。
正解表eval/targets.json(評価専用)と照合し recall/対象外付与/付与率/字数/source_quote空/却下理由を集計。
内容一致(noteが既知誤読を扱うか)は自動判定せず、label sheetを出力して人手ラベル付けに回す。"""
import argparse, json, sys
from collections import Counter
from pathlib import Path

TRIAL = Path(__file__).resolve().parents[1]


def _load(p, default=None):
    p = Path(p)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default


def eval_theme(notes, targets, rejected=None, prov=None, jall=None, prefix=None):
    """notes: [{fact_id,note,source_quote,..}], targets: {fid:{type,known_misreading}}。"""
    rejected, prov = rejected or [], prov or {}
    attached = [n["fact_id"] for n in notes]
    hit = [f for f in targets if f in attached]
    extra = [f for f in attached if f not in targets]
    lens = [len(n["note"]) for n in notes]
    fc = prov.get("fact_count")
    jall = jall or []
    rev_true = [x for x in jall if (x.get("judgment") or {}).get("reversible") is True]
    qmiss = [x for x in rev_true if "ledger_quote_not_in_ledger" in (x.get("dropped_by") or [])]
    # 接頭辞の空白だけ違う却下(bad_prefix)を寛容に救済した場合の参考値(公式評価ではない)
    tol = []
    if prefix:
        pf = prefix.strip()
        for r in rejected:
            if r["reason"].startswith("bad_prefix") and (r.get("note") or "").startswith(pf):
                tol.append(r["fact_id"])
    return {"warnings": sum(len(n.get("warnings") or []) for n in notes), "tolerant_prefix_ids": tol, "tolerant_hit": [f for f in tol if f in targets],
            "reversible_true": len(rev_true), "quote_mismatch": len(qmiss), "cost_jpy": prov.get("cost_jpy", 0.0),
            "targets": len(targets), "hit": len(hit), "hit_ids": hit, "missed_ids": [f for f in targets if f not in attached],
            "extra": len(extra), "extra_ids": extra, "stage1_candidates": prov.get("stage1_candidate_count"),
            "attached": len(attached), "fact_count": fc, "attach_rate": (len(attached) / fc) if fc else None,
            "avg_len": (sum(lens) / len(lens)) if lens else 0.0, "max_len": max(lens) if lens else 0,
            "empty_source_quote": sum(1 for n in notes if not (n.get("source_quote") or "").strip()),
            "rejected": len(rejected), "rejected_reasons": dict(Counter(r["reason"].split("(")[0] for r in rejected))}


def aggregate(rows):
    t = lambda k: sum(r[k] for r in rows)
    fc = sum(r["fact_count"] or 0 for r in rows)
    lens = [r["avg_len"] * r["attached"] for r in rows]
    rr = Counter()
    for r in rows:
        rr.update(r["rejected_reasons"])
    return {"warnings": t("warnings"), "tolerant_prefix_n": sum(len(r["tolerant_prefix_ids"]) for r in rows), "tolerant_hit": sum(len(r["tolerant_hit"]) for r in rows),
            "reversible_true": t("reversible_true"), "quote_mismatch": t("quote_mismatch"), "cost_jpy": t("cost_jpy"),
            "targets": t("targets"), "hit": t("hit"), "extra": t("extra"), "attached": t("attached"), "fact_count": fc,
            "stage1_candidates": sum(r["stage1_candidates"] or 0 for r in rows),
            "attach_rate": (t("attached") / fc) if fc else None,
            "avg_len": (sum(lens) / t("attached")) if t("attached") else 0.0,
            "max_len": max((r["max_len"] for r in rows), default=0), "empty_source_quote": t("empty_source_quote"),
            "rejected": t("rejected"), "rejected_reasons": dict(rr)}


def label_sheet(pattern, slug, notes, targets):
    """内容一致ラベル用(一致Y/Nは空欄)。対象外付与も一覧に含め、既知誤読は(対象外)と表示。"""
    lines = ["| theme | fact_id | note(逐語) | 既知誤読 | 一致(Y/N) |", "|---|---|---|---|---|"]
    for n in notes:
        t = targets.get(n["fact_id"])
        lines.append("| %s | %s | %s | %s |  |" % (slug, n["fact_id"], n["note"].replace("|", "\\|"),
                                                  t["known_misreading"] if t else "(対象外)"))
    return lines


def fmt(v):
    return "-" if v is None else ("%.2f" % v if isinstance(v, float) else str(v))


COLS = ["pattern", "theme", "recall", "extra", "cand", "attach", "rate", "avg_len", "max_len", "empty_sq", "rev_true/quote_mismatch", "warn", "cost", "rejected(reasons)"]


def row_cells(pat, theme, r):
    return [pat, theme, "%d/%d" % (r["hit"], r["targets"]), str(r["extra"]), fmt(r["stage1_candidates"]),
            "%d/%s" % (r["attached"], fmt(r["fact_count"])), fmt(r["attach_rate"]), fmt(r["avg_len"]), str(r["max_len"]),
            str(r["empty_source_quote"]), "%d/%d" % (r["reversible_true"], r["quote_mismatch"]), str(r["warnings"]), fmt(r["cost_jpy"]), "%d %s" % (r["rejected"], json.dumps(r["rejected_reasons"], ensure_ascii=False))]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--patterns", required=True)
    ap.add_argument("--runs-dir", default=str(TRIAL / "runs"))
    ap.add_argument("--targets", default=str(TRIAL / "eval" / "targets.json"))
    ap.add_argument("--eval-dir", default=str(TRIAL / "eval"))
    ap.add_argument("--holdout", default=str(TRIAL / "eval" / "holdout.json"))
    ap.add_argument("--out", default=None, help="結果表の出力prefix(未指定はeval-dir/eval_table.md)")
    a = ap.parse_args(argv)
    themes = dict(_load(a.targets)["themes"])
    hold = (_load(a.holdout, {"themes": {}}) or {"themes": {}})["themes"]
    for k, v in hold.items():
        themes.setdefault(k, v)
    core = [k for k in themes if k not in hold]
    counts = {}
    out = ["| " + " | ".join(COLS) + " |", "|" + "---|" * len(COLS)]
    for pat in a.patterns.split(","):
        rows, sheet = [], ["# content label sheet: %s" % pat, ""]
        for slug, th in themes.items():
            d = Path(a.runs_dir) / pat / slug
            notes = _load(d / "notes.json")
            if notes is None:
                out.append("| %s | %s | (no run) |" % (pat, slug))
                continue
            prv = _load(d / "provenance.json", {})
            r = eval_theme(notes, th["targets"], _load(d / "rejected.json", []), prv, _load(d / "judgments_all.json", []), prv.get("prefix"))
            if slug in core:
                rows.append(r)
            counts.setdefault(pat, {})[slug] = (r["attached"], r["fact_count"])
            out.append("| " + " | ".join(row_cells(pat, slug, r)) + " |")
            sheet += label_sheet(pat, slug, notes, th["targets"]) + [""]
        if rows:
            agg = aggregate(rows)
            out.append("| " + " | ".join(row_cells(pat, "ALL(core5)", agg)) + " |")
            out.append("<!-- %s tolerant_prefix: rescued_notes=%d rescued_target_hits=%d ; quote_mismatch/reversible_true=%d/%d -->" % (
                pat, agg["tolerant_prefix_n"], agg["tolerant_hit"], agg["quote_mismatch"], agg["reversible_true"]))
            cs = [v[0] for k, v in counts.get(pat, {}).items() if k in core]
            if len(cs) > 1 and len(set(cs)) == 1:
                out.append("WARNING(sycophancy): %s: 全core台帳で同件数(%s)" % (pat, cs))
            out.append("<!-- %s attach_distribution: %s -->" % (pat, json.dumps(counts.get(pat, {}), ensure_ascii=False)))
        Path(a.eval_dir).mkdir(parents=True, exist_ok=True)
        (Path(a.eval_dir) / ("%s_content_label_sheet.md" % pat)).write_text("\n".join(sheet), encoding="utf-8")
    (Path(a.out) if a.out else Path(a.eval_dir) / "eval_table.md").write_text("\n".join(out), encoding="utf-8")
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
