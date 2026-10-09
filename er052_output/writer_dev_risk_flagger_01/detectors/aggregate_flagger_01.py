# -*- coding: utf-8 -*-
"""Risk Flagger 集計(委任_01B)。results/*.jsonl と <stem>_labels.json(make_blind_01.pyの出力)を突き合わせる。
ラベルを読むのはこの集計だけ(検出器側は読まない)。
指標: Recall(重大) / 精度(ケース単位・Flag単位) / Flag数/ユニット(記事) / タイプ別Recall / 既知事故別の拾い有無 / 費用。
ラベル値の正規化: 重大系={重大,C,critical,major,severe} / 問題なし系={問題なし,非重大,A,ok,軽微} / それ以外(B,境界等)は
『境界』として精度・Recallの分母から除外し、別掲する。
使い方: python aggregate_flagger_01.py --labels casebank_01_labels.json --results results/d0_none_cb01.jsonl [...] [--min-conf 0.0] [--out-md x.md]
"""
import argparse
import json
import os
import sys

SEVERE = {"重大", "c", "critical", "major", "severe"}
OK = {"問題なし", "非重大", "a", "ok", "軽微", "none"}


def norm_label(v):
    s = str(v or "").strip().lower()
    if s in SEVERE or s.startswith("重大"):
        return "severe"
    if s in OK:
        return "ok"
    return "border"


def load_rows(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for ln in f:
            if ln.strip():
                r = json.loads(ln)
                if "unit_id" in r:
                    rows.append(r)
    return rows


def aggregate(labels, rows, min_conf=0.0, severe_only=True):
    """labels: {unit_id: {label, known_incident?, type_label?}}  rows: 1検出器分のresult行。"""
    flagged = {}
    nflags = 0
    for r in rows:
        fl = [x for x in r["flags"] if x["confidence"] >= min_conf and (x.get("severity") == "重大" or not severe_only)]
        flagged[r["unit_id"]] = fl
        nflags += len(fl)
    cls = {uid: norm_label(l.get("label")) for uid, l in labels.items() if uid in flagged}
    sev = [u for u, c in cls.items() if c == "severe"]
    okc = [u for u, c in cls.items() if c == "ok"]
    bor = [u for u, c in cls.items() if c == "border"]
    hit = [u for u in sev if flagged[u]]
    fp_cases = [u for u in okc if flagged[u]]
    bor_flagged = [u for u in bor if flagged[u]]
    flags_on_sev = sum(len(flagged[u]) for u in sev)
    flags_on_ok = sum(len(flagged[u]) for u in okc)
    res = dict(
        n_units=len(flagged), n_severe=len(sev), n_ok=len(okc), n_border=len(bor),
        recall_severe=(len(hit) / len(sev)) if sev else None,
        case_precision=(len(hit) / (len(hit) + len(fp_cases))) if (hit or fp_cases) else None,
        flag_precision=(flags_on_sev / (flags_on_sev + flags_on_ok)) if (flags_on_sev + flags_on_ok) else None,
        flags_total=nflags, flags_per_unit=(nflags / len(flagged)) if flagged else None,
        false_positive_cases=fp_cases, border_flagged=bor_flagged, missed_severe=[u for u in sev if not flagged[u]],
        cost_jpy=sum((r.get("cost_jpy") or 0) for r in rows),
        invalid_units=[r["unit_id"] for r in rows if not r.get("valid_json", True)],
    )
    by_type = {}
    for u in sev:
        t = labels[u].get("type_label") or "(未指定)"
        d = by_type.setdefault(t, dict(n=0, hit=0))
        d["n"] += 1
        if flagged[u]:
            d["hit"] += 1
    res["recall_by_type"] = {t: dict(d, recall=d["hit"] / d["n"]) for t, d in by_type.items()}
    inc = {}
    for u, l in labels.items():
        k = l.get("known_incident")
        if k and u in flagged:
            inc[k] = dict(unit_id=u, hit=bool(flagged[u]), flag_types=sorted({x["type"] for x in flagged[u]}))
    res["known_incidents"] = inc
    return res


def fmt(x, pct=True):
    if x is None:
        return "-"
    return ("%.0f%%" % (100 * x)) if pct else ("%.2f" % x)


def to_markdown(table):
    lines = ["| 検出器 | units(重大/問題なし/境界) | Recall(重大) | 精度(ケース) | 精度(Flag) | Flag/unit | 見逃し | 誤Flagケース | 費用JPY |",
             "|---|---|---|---|---|---|---|---|---|"]
    for name, r in table:
        lines.append("| %s | %d(%d/%d/%d) | %s | %s | %s | %s | %s | %s | %.2f |" % (
            name, r["n_units"], r["n_severe"], r["n_ok"], r["n_border"], fmt(r["recall_severe"]), fmt(r["case_precision"]),
            fmt(r["flag_precision"]), fmt(r["flags_per_unit"], False), ",".join(r["missed_severe"]) or "-",
            ",".join(r["false_positive_cases"]) or "-", r["cost_jpy"]))
    lines += ["", "### 既知事故別", "| 検出器 | " + " | ".join(sorted({k for _n, r in table for k in r["known_incidents"]})) + " |"]
    ks = sorted({k for _n, r in table for k in r["known_incidents"]})
    lines.append("|---|" + "---|" * len(ks))
    for name, r in table:
        lines.append("| %s | " % name + " | ".join(("拾った" if r["known_incidents"].get(k, {}).get("hit") else "見逃し")
                                                    if k in r["known_incidents"] else "-" for k in ks) + " |")
    lines += ["", "### タイプ別Recall(重大ケースのtype_label別)"]
    ts = sorted({t for _n, r in table for t in r["recall_by_type"]})
    lines += ["| 検出器 | " + " | ".join(ts) + " |", "|---|" + "---|" * len(ts)]
    for name, r in table:
        lines.append("| %s | " % name + " | ".join(
            ("%d/%d" % (r["recall_by_type"][t]["hit"], r["recall_by_type"][t]["n"])) if t in r["recall_by_type"] else "-"
            for t in ts) + " |")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--labels", required=True)
    ap.add_argument("--results", nargs="+", required=True)
    ap.add_argument("--min-conf", type=float, default=0.0)
    ap.add_argument("--include-nonsevere-flags", action="store_true")
    ap.add_argument("--out-md")
    ap.add_argument("--out-json")
    a = ap.parse_args(argv)
    with open(a.labels, encoding="utf-8") as f:
        labels = json.load(f)
    table = []
    for p in a.results:
        rows = load_rows(p)
        table.append((os.path.splitext(os.path.basename(p))[0],
                      aggregate(labels, rows, a.min_conf, not a.include_nonsevere_flags)))
    md = to_markdown(table)
    print(md)
    if a.out_md:
        with open(a.out_md, "w", encoding="utf-8") as f:
            f.write(md + "\n")
    if a.out_json:
        with open(a.out_json, "w", encoding="utf-8") as f:
            json.dump({n: r for n, r in table}, f, ensure_ascii=False, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
