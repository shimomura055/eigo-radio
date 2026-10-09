# -*- coding: utf-8 -*-
"""Risk Flagger 集計(委任_01B -> 委任_02 P0で全面改修)。results/*.jsonl と casebank_01_labels.json(make_blind_01.pyの出力)を突き合わせる。
ラベルを読むのはこの集計だけ(検出器側は読まない)。

KPI定義式は設計書 DESIGN_RISK_FLAGGER_01.md §4(不変)。ここで算出するもの:
  Recall_human(主) = ヒット数 / ラベル根拠が『ユーザー確認』の重大数      Recall_all(副) = ヒット数 / 重大数  (Wilson 95%区間つき)
  FPR_clear / FPR_boundary / FPR_hardneg(重大と同一Factの忠実文: K12/K08/K09/RC-K10/S0系) = 誤Flagケース数 / 該当ケース数
  Flag数 = (unit,sentence,type)件数 と 固有文数 の両方 / unit
  タイプ別Recall(accident_type別) / 既知事故別(known_incident: Rollback系ほか) / 合成の方向反転(別Fact)の副指標
  confidence閾値曲線(--conf-sweep) / 費用
  記事モード: aggregate_article(既知重大文の±2文窓照合、Recall@top3)
ヒット = 重大ケース(1文unit)に severity=重大 かつ confidence>=閾値 のFlagが1件以上。種別一致はヒットの条件にしない。
S0_USER_CHECK 3件(S0-1/S0-2/S0-3)の反転時再計算規則(事前登録): ユーザーが S0-n を『重大』と回答したら、--s0-flip S0-n で
  そのケースを重大(ラベル根拠=ユーザー確認)へ移す。Recall_all/Recall_humanの分母が+1、FPR_boundary/FPR_hardnegの分母が-1(当該ケースを除く)に
  再計算され、他のケースの扱いは変えない。
"""
import argparse
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

SEVERE = {"重大", "c", "critical", "major", "severe"}
THRESHOLDS_DEFAULT = (0.0, 0.3, 0.5, 0.7, 0.9)


def norm_label(v):
    s = str(v or "").strip().lower()
    if s in SEVERE or s.startswith("重大"):
        return "severe"
    return "nonsevere"


def wilson(k, n, z=1.96):
    if not n:
        return None
    p = k / float(n)
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (max(0.0, c - h), min(1.0, c + h))


def load_rows(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for ln in f:
            if ln.strip():
                r = json.loads(ln)
                if "unit_id" in r:
                    rows.append(r)
    return rows


def _rate(k, n):
    return dict(k=k, n=n, rate=(k / float(n)) if n else None, wilson=wilson(k, n))


def _neg_group(l):
    g = l.get("neg_group")
    if g:
        return g
    t = str(l.get("accident_type") or l.get("type_label") or "")
    return "boundary" if ("境界" in t or "軽微" in t) else "clear"


def _is_rollback(l):
    t = str(l.get("accident_type") or l.get("type_label") or "")
    return t.lower().startswith("rollback") or str(l.get("known_incident") or "").startswith("Rollback")


def effective_labels(labels, s0_flip=()):
    """s0_flip: legacy id(例 'S0-1')のcollection。該当ケースを重大(ユーザー確認)へ反転した複製ラベルを返す。"""
    flip = set(s0_flip or ())
    out = {}
    for uid, l in labels.items():
        l = dict(l)
        if flip and set(l.get("legacy_ids") or []) & flip:
            l["label"] = "重大"
            l["label_basis"] = "ユーザー確認"
            l["neg_group"] = None
            l["hard_negative"] = False
            l["flipped_by_s0_rule"] = True
        out[uid] = l
    return out


def aggregate(labels, rows, min_conf=0.0, severe_only=True, split=None, s0_flip=(), exclude_gate_only=False):
    """labels: {unit_id: {...}}  rows: 1検出器分のresult行。split指定時はそのsplitのケースだけ。"""
    labels = effective_labels(labels, s0_flip)
    flagged, nflags, sent_keys = {}, 0, set()
    all_keys = set()
    for r in rows:
        uid = r["unit_id"]
        if uid not in labels:
            continue
        if split and labels[uid].get("split") != split:
            continue
        fl = [x for x in r["flags"] if x["confidence"] >= min_conf and (x.get("severity") == "重大" or not severe_only)
              and not (exclude_gate_only and x.get("gate_only"))]
        flagged[uid] = fl
        for x in fl:
            all_keys.add((uid, x["sentence_id"], x["type"]))
            sent_keys.add((uid, x["sentence_id"]))
    nflags = len(all_keys)
    cls = {u: norm_label(labels[u].get("label")) for u in flagged}
    sev = [u for u, c in cls.items() if c == "severe"]
    human = [u for u in sev if str(labels[u].get("label_basis", "")).startswith("ユーザー確認")]
    neg = [u for u, c in cls.items() if c == "nonsevere"]
    groups = {"clear": [], "boundary": [], "hard_negative": []}
    for u in neg:
        groups[_neg_group(labels[u])].append(u)
    hit = lambda u: bool(flagged[u])  # noqa: E731
    res = dict(n_units=len(flagged), n_severe=len(sev), n_human=len(human), n_neg=len(neg))
    res["recall_human"] = _rate(sum(hit(u) for u in human), len(human))
    res["recall_all"] = _rate(sum(hit(u) for u in sev), len(sev))
    for g in ("clear", "boundary", "hard_negative"):
        res["fpr_" + g] = _rate(sum(hit(u) for u in groups[g]), len(groups[g]))
        res["fp_cases_" + g] = [u for u in groups[g] if hit(u)]
    flags_on_sev = sum(len(flagged[u]) for u in sev)
    flags_on_neg = sum(len(flagged[u]) for u in neg)
    res["flag_precision"] = (flags_on_sev / float(flags_on_sev + flags_on_neg)) if (flags_on_sev + flags_on_neg) else None
    res["flags_utype"] = nflags
    res["flags_unique_sentences"] = len(sent_keys)
    res["flags_per_unit_utype"] = (nflags / float(len(flagged))) if flagged else None
    res["flags_per_unit_sentences"] = (len(sent_keys) / float(len(flagged))) if flagged else None
    res["missed_severe"] = [u for u in sev if not hit(u)]
    res["cost_jpy"] = sum((r.get("cost_jpy") or 0) for r in rows if r["unit_id"] in flagged)
    res["invalid_units"] = [r["unit_id"] for r in rows if r["unit_id"] in flagged and not r.get("valid_json", True)]
    by_type = {}
    for u in sev:
        t = labels[u].get("accident_type") or labels[u].get("type_label") or "(未指定)"
        d = by_type.setdefault(t, dict(n=0, hit=0))
        d["n"] += 1
        d["hit"] += int(hit(u))
    res["recall_by_type"] = {t: dict(d, recall=d["hit"] / float(d["n"])) for t, d in by_type.items()}
    inc = {}
    for u in sev:
        k = labels[u].get("known_incident")
        if k:
            d = inc.setdefault(k, dict(n=0, hit=0, units=[]))
            d["n"] += 1
            d["hit"] += int(hit(u))
            d["units"].append(u)
    res["known_incidents"] = inc
    rb = [u for u in sev if _is_rollback(labels[u])]
    res["rollback"] = dict(n=len(rb), hit=sum(hit(u) for u in rb), units=rb)
    sd = [u for u in sev if str(labels[u].get("accident_type")) == "方向反転(別Fact)"]
    res["synthetic_direction_reversal"] = dict(n=len(sd), hit=sum(hit(u) for u in sd), units=sd)
    return res


def conf_sweep(labels, rows, thresholds=THRESHOLDS_DEFAULT, split=None, s0_flip=(), exclude_gate_only=False):
    out = []
    for t in thresholds:
        r = aggregate(labels, rows, min_conf=t, split=split, s0_flip=s0_flip, exclude_gate_only=exclude_gate_only)
        out.append(dict(thr=t, recall_human=r["recall_human"], recall_all=r["recall_all"], fpr_clear=r["fpr_clear"],
                        fpr_boundary=r["fpr_boundary"], fpr_hard_negative=r["fpr_hard_negative"],
                        flags_utype=r["flags_utype"], flags_unique_sentences=r["flags_unique_sentences"]))
    return out


# ---------------------------------------------------------------- 記事モード
def _norm_text(s):
    return re.sub(r"[\s\"'“”‘’「」#*_`-]+", "", (s or "").lower())


def locate_sentence(article_sentences, known_sentence):
    """記事の文リスト(run_flagger._split_sentencesの出力)から既知重大文の位置(0始まり)。一致=正規化後の包含。未特定=None。"""
    k = _norm_text(known_sentence)
    if not k:
        return None
    for i, s in enumerate(article_sentences):
        n = _norm_text(s)
        if n and (k in n or n in k) and min(len(n), len(k)) >= 0.6 * max(len(n), len(k)):
            return i
    for i, s in enumerate(article_sentences):  # 文分割が違う場合: 先頭30字一致
        if _norm_text(s)[:30] == k[:30]:
            return i
    return None


def aggregate_article(article_sentences, flags, known_sentences, window=2, topk=3, min_conf=0.0):
    """flags: 1記事分のFlag(sentence_idは's<番号>'、番号は1始まり)。known_sentences: 既知重大文のlist(逐語)。
    戻り値: 既知重大文ごとの {located, hit_window(±window文内にFlag), rank(Flagされた固有文のconfidence降順順位), in_topk}
            + 全体 flags_utype / flags_unique_sentences / recall_window / recall_at_topk。"""
    fl = [x for x in flags if x["confidence"] >= min_conf]
    best = {}
    for x in fl:
        i = int(re.sub(r"\D", "", x["sentence_id"])) - 1
        best[i] = max(best.get(i, 0.0), x["confidence"])
    order = [i for i, _c in sorted(best.items(), key=lambda kv: (-kv[1], kv[0]))]
    items = []
    for ks in known_sentences:
        pos = locate_sentence(article_sentences, ks)
        if pos is None:
            items.append(dict(sentence=ks, located=False, hit_window=None, rank=None, in_topk=None))
            continue
        hw = any(abs(i - pos) <= window for i in best)
        rk = (order.index(pos) + 1) if pos in order else None
        near_rk = min([order.index(i) + 1 for i in order if abs(i - pos) <= window], default=None)
        items.append(dict(sentence=ks, located=True, pos=pos, hit_window=hw, rank=rk, best_rank_in_window=near_rk,
                          in_topk=bool(near_rk and near_rk <= topk)))
    loc = [x for x in items if x["located"]]
    return dict(items=items, n_known=len(known_sentences), n_located=len(loc),
                flags_utype=len({(x["sentence_id"], x["type"]) for x in fl}), flags_unique_sentences=len(best),
                recall_window=_rate(sum(1 for x in loc if x["hit_window"]), len(loc)),
                recall_at_topk=_rate(sum(1 for x in loc if x["in_topk"]), len(loc)))


# ---------------------------------------------------------------- 出力
def fmt(x, pct=True):
    if x is None:
        return "-"
    return ("%.0f%%" % (100 * x)) if pct else ("%.2f" % x)


def fr(d):
    if not d or d["n"] == 0:
        return "-"
    w = d["wilson"]
    return "%d/%d (%s, CI %s-%s)" % (d["k"], d["n"], fmt(d["rate"]), fmt(w[0]), fmt(w[1]))


def to_markdown(table):
    lines = ["| 検出器 | units(重大/人間確認/非重大) | Recall_human(主) | Recall_all(副) | FPR_clear | FPR_boundary | FPR_hardneg | "
             "Flag(unit,sent,type)/unit | Flag固有文/unit | Rollback | 方向反転(別Fact) | 費用JPY |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for name, r in table:
        lines.append("| %s | %d(%d/%d/%d) | %s | %s | %s | %s | %s | %s | %s | %d/%d | %d/%d | %.2f |" % (
            name, r["n_units"], r["n_severe"], r["n_human"], r["n_neg"], fr(r["recall_human"]), fr(r["recall_all"]),
            fr(r["fpr_clear"]), fr(r["fpr_boundary"]), fr(r["fpr_hard_negative"]), fmt(r["flags_per_unit_utype"], False),
            fmt(r["flags_per_unit_sentences"], False), r["rollback"]["hit"], r["rollback"]["n"],
            r["synthetic_direction_reversal"]["hit"], r["synthetic_direction_reversal"]["n"], r["cost_jpy"]))
    lines += ["", "見逃し重大 / 誤Flag(clear・boundary・hardneg):"]
    for name, r in table:
        lines.append("- %s: 見逃し=%s / 誤Flag clear=%s boundary=%s hardneg=%s" % (
            name, ",".join(r["missed_severe"]) or "-", ",".join(r["fp_cases_clear"]) or "-",
            ",".join(r["fp_cases_boundary"]) or "-", ",".join(r["fp_cases_hard_negative"]) or "-"))
    ks = sorted({k for _n, r in table for k in r["known_incidents"]})
    if ks:
        lines += ["", "### 既知事故別(拾った/件数)", "| 検出器 | " + " | ".join(ks) + " |", "|---|" + "---|" * len(ks)]
        for name, r in table:
            lines.append("| %s | " % name + " | ".join(
                ("%d/%d" % (r["known_incidents"][k]["hit"], r["known_incidents"][k]["n"])) if k in r["known_incidents"] else "-"
                for k in ks) + " |")
    ts = sorted({t for _n, r in table for t in r["recall_by_type"]})
    lines += ["", "### タイプ別Recall(重大ケースのaccident_type別、hit/n)", "| 検出器 | " + " | ".join(ts) + " |", "|---|" + "---|" * len(ts)]
    for name, r in table:
        lines.append("| %s | " % name + " | ".join(
            ("%d/%d" % (r["recall_by_type"][t]["hit"], r["recall_by_type"][t]["n"])) if t in r["recall_by_type"] else "-"
            for t in ts) + " |")
    return "\n".join(lines)


def sweep_markdown(name, sweep):
    lines = ["", "### confidence閾値曲線: %s" % name,
             "| 閾値 | Recall_human | Recall_all | FPR_clear | FPR_boundary | FPR_hardneg | Flag(unit,sent,type) | Flag固有文 |",
             "|---|---|---|---|---|---|---|---|"]
    for s in sweep:
        lines.append("| %.2f | %s | %s | %s | %s | %s | %d | %d |" % (
            s["thr"], fr(s["recall_human"]), fr(s["recall_all"]), fr(s["fpr_clear"]), fr(s["fpr_boundary"]),
            fr(s["fpr_hard_negative"]), s["flags_utype"], s["flags_unique_sentences"]))
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--labels", required=True)
    ap.add_argument("--results", nargs="+", required=True)
    ap.add_argument("--split", help="dev / holdout / synthetic_dev / synthetic_holdout (省略=全て)")
    ap.add_argument("--min-conf", type=float, default=0.0)
    ap.add_argument("--conf-sweep", help="例: 0,0.3,0.5,0.7,0.9 (閾値曲線を追加出力)")
    ap.add_argument("--s0-flip", help="例: S0-1,S0-3 (ユーザーが重大と回答したS0のlegacy id)")
    ap.add_argument("--include-nonsevere-flags", action="store_true")
    ap.add_argument("--exclude-gate-only", action="store_true", help="D0のgate_only Flag(不在断定・数量・増減/許可)を数えない(和集合と同じ扱い)")
    ap.add_argument("--out-md")
    ap.add_argument("--out-json")
    a = ap.parse_args(argv)
    with open(a.labels, encoding="utf-8") as f:
        labels = json.load(f)
    flip = a.s0_flip.split(",") if a.s0_flip else ()
    thr = [float(x) for x in a.conf_sweep.split(",")] if a.conf_sweep else None
    table, sweeps = [], []
    for p in a.results:
        rows = load_rows(p)
        name = os.path.splitext(os.path.basename(p))[0]
        table.append((name, aggregate(labels, rows, a.min_conf, not a.include_nonsevere_flags, a.split, flip, a.exclude_gate_only)))
        if thr:
            sweeps.append((name, conf_sweep(labels, rows, thr, a.split, flip, a.exclude_gate_only)))
    md = to_markdown(table) + "".join(sweep_markdown(n, s) for n, s in sweeps)
    print(md)
    if a.out_md:
        with open(a.out_md, "w", encoding="utf-8") as f:
            f.write(md + "\n")
    if a.out_json:
        with open(a.out_json, "w", encoding="utf-8") as f:
            json.dump({"table": {n: r for n, r in table}, "sweeps": {n: s for n, s in sweeps}}, f, ensure_ascii=False, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
