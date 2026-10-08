# -*- coding: utf-8 -*-
"""V2 集計: 旧(OPEN243_M2未設定)/新(OPEN243_M2=1)の run_deviation_check 結果を事象 fixture と突合して混同行列を作る。"""
from __future__ import annotations

import collections
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
import v2_en_check as V  # noqa: E402

FLAGS = C.vfl01.DEVIATION_FLAG_KEYS
TOL_KW = {"TOL_G02_users": "users", "TOL_G09_so": " so ", "TOL_G06_oil": "oil prices",
          "TOLX_G07_users": "users", "TOLX_G12_users": "users"}


def load(arm, f):
    p = f"{V.V2}/{arm}/{f['key']}.json"
    if os.path.exists(p):
        d = json.load(open(p, encoding="utf-8"))
        return d["parsed"]["deviations"], "rerun", d.get("cost_jpy", 0.0)
    if arm == "old" and f["kind"] == "article":
        sp = f"{f['run']}/b1b/audit/deviation_check.json"
        if os.path.exists(sp):
            d = json.load(open(sp, encoding="utf-8"))
            return d.get("deviations", []), "stored", 0.0
    return None, "none", 0.0


def match(ev_sentence, devs):
    return [d for d in devs if C.sent_match(ev_sentence, d.get("claim_in_article", ""))]


def agg(ms):
    if not ms:
        return {"detected": False}
    sev = "MAJOR" if any(d["severity"] == "MAJOR" for d in ms) else "MINOR"
    origins = sorted({d.get("origin") for d in ms})
    actor = any(d.get("changed_actor") for d in ms)
    return {"detected": True, "severity": sev, "origins": origins, "changed_actor": actor,
            "flags": sorted({k for d in ms for k in FLAGS if d.get(k)})}


def main():
    fx, _, _ = V.build_fixtures()
    arts = [f for f in fx if f["kind"] == "article"]
    tols = [f for f in fx if f["kind"] == "tolerance"]
    res = {"old": {}, "new": {}}
    srcs = {"old": {}, "new": {}}
    src = {"old": collections.Counter(), "new": collections.Counter()}
    for arm in ("old", "new"):
        for f in fx:
            devs, s, c = load(arm, f)
            res[arm][f["key"]] = devs
            srcs[arm][f["key"]] = s
            src[arm][s] += 1
    out = []
    out.append(f"fixtures: article={len(arts)} tolerance={len(tols)}; source old={dict(src['old'])} new={dict(src['new'])}")

    # ---- 事象別 ----
    ev_rows = []
    for f in arts:
        for e in f["events"]:
            row = {"old_src": srcs["old"][f["key"]], "event": e["event_id"], "origin_truth": e["origin"], "type": e["type"], "sev_truth": e["severity"],
                   "sentence": e["sentence"], "key": f["key"]}
            for arm in ("old", "new"):
                devs = res[arm][f["key"]]
                row[arm] = agg(match(e["sentence"], devs)) if devs is not None else {"detected": None}
            ev_rows.append(row)
    json.dump(ev_rows, open(f"{V.V2}/event_rows.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    pos = [r for r in ev_rows if r["origin_truth"] in ("translation", "amplified")]
    neg_all = [r for r in ev_rows if r["origin_truth"] == "ja"]
    neg = [r for r in neg_all if r["old_src"] == "rerun"]  # 旧が再実行された記事内のJA事象のみ(storedは終了時COMPLIANTの選択バイアスがあるため比較しない)
    subj = [r for r in pos if r["type"] == "subject"]
    out.append(f"\n事象: 陽性(翻訳由来/増幅)={len(pos)} (subject型={len(subj)}), JA由来={len(neg)}")

    def cnt(rows, arm, pred):
        return sum(1 for r in rows if r[arm].get("detected") and pred(r[arm]))

    for name, rows in (("陽性26", pos), ("JA由来(旧再実行記事内)", neg)):
        out.append(f"\n[{name}] 検出/origin/severity (旧 -> 新)")
        for arm in ("old", "new"):
            det = cnt(rows, arm, lambda a: True)
            tr = cnt(rows, arm, lambda a: "translation" in a["origins"])
            ja = cnt(rows, arm, lambda a: "ja_source" in a["origins"])
            maj = cnt(rows, arm, lambda a: a["severity"] == "MAJOR")
            out.append(f"  {arm}: 検出={det}/{len(rows)}  origin=translation含む={tr}  origin=ja_source含む={ja}  MAJOR={maj}  MINOR={det - maj}")
    out.append(f"\n[主体型(subject)陽性 {len(subj)}件] changed_actor=true")
    for arm in ("old", "new"):
        out.append(f"  {arm}: 検出={cnt(subj, arm, lambda a: True)}  changed_actor=true={cnt(subj, arm, lambda a: a['changed_actor'])}  translation判定={cnt(subj, arm, lambda a: 'translation' in a['origins'])}")
    out.append("\n事象別(陽性、旧->新)")
    for r in pos:
        def s(a):
            return "未検出" if not a.get("detected") else f"{a['severity']}/{'+'.join(map(str, a['origins']))}/actor={'Y' if a['changed_actor'] else 'n'}"
        out.append(f"  {r['event']} {r['origin_truth']}/{r['type']}/{r['sev_truth']}: 旧[{s(r['old'])}] 新[{s(r['new'])}] | {r['sentence'][:70]}")
    out.append("\n事象別(JA由来、旧->新)")
    for r in neg:
        def s(a):
            return "未検出" if not a.get("detected") else f"{a['severity']}/{'+'.join(map(str, a['origins']))}/actor={'Y' if a['changed_actor'] else 'n'}"
        out.append(f"  {r['event']} {r['type']}/{r['sev_truth']}: 旧[{s(r['old'])}] 新[{s(r['new'])}] | {r['sentence'][:70]}")

    # ---- 許容文 ----
    out.append("\n[ユーザー許容文] 該当文のseverity(旧->新)と、その記事のMAJOR全件")
    for f in tols:
        kw = TOL_KW[f["key"]]
        line = f"  {f['key']} ({f['tolerated_type']}): "
        for arm in ("old", "new"):
            devs = res[arm][f["key"]]
            if devs is None:
                line += f"{arm}=NA "
                continue
            hits = [d for d in devs if kw in (" " + (d.get("claim_in_article") or "").lower() + " ")]
            line += f"{arm}: 該当文dev={[(d['severity'], d.get('origin')) for d in hits]} MAJOR総数={sum(1 for d in devs if d['severity'] == 'MAJOR')}  "
        out.append(line)
        for arm in ("old", "new"):
            for d in (res[arm][f["key"]] or []):
                if d["severity"] == "MAJOR":
                    out.append(f"      {arm} MAJOR: {d.get('origin')} {[k for k in FLAGS if d.get(k)]} {(d.get('claim_in_article') or '')[:80]} | {(d.get('issue') or '')[:90]}")

    # ---- 59記事 ----
    out.append("\n[最終英文の MAJOR 件数] 旧を再実行した記事(同一記事で旧/新を比較) と 新の全59記事")
    for label, sel in ((f"旧再実行={sum(1 for f in arts if srcs['old'][f['key']] == 'rerun')}記事", [f for f in arts if srcs["old"][f["key"]] == "rerun"]), ("全59記事(旧=storedを含む)", arts)):
        for arm in ("old", "new"):
            tot = tr = ja = arts_major = arts_ja = arts_tr = 0
            for f in sel:
                devs = res[arm][f["key"]]
                if devs is None:
                    continue
                m = [d for d in devs if d["severity"] == "MAJOR"]
                tot += len(m)
                tr += sum(1 for d in m if d.get("origin") == "translation")
                ja += sum(1 for d in m if d.get("origin") == "ja_source")
                arts_major += 1 if m else 0
                arts_ja += 1 if any(d.get("origin") == "ja_source" for d in m) else 0
                arts_tr += 1 if any(d.get("origin") == "translation" for d in m) else 0
            out.append(f"  [{label}] {arm}: MAJOR総数={tot} (translation={tr}, ja_source={ja})  MAJORを含む記事={arts_major}/{len(sel)} (ja_source MAJOR記事={arts_ja}, translation MAJOR記事={arts_tr})")
    # 新で増えたMAJOR(旧に同文MAJORなし)の一覧
    out.append("\n[新でMAJORになり、旧では同文がMAJORでない件(誤検知候補の目視用)]")
    n_new_major = 0
    for f in arts:
        o, n = res["old"][f["key"]], res["new"][f["key"]]
        if o is None or n is None or srcs["old"][f["key"]] != "rerun":
            continue
        for d in n:
            if d["severity"] == "MAJOR" and not any(C.sent_match(d.get("claim_in_article", ""), x.get("claim_in_article", "")) and x["severity"] == "MAJOR" for x in o):
                n_new_major += 1
                out.append(f"  {f['key'].replace('ART_', '')[:60]}: {d.get('origin')} {[k for k in FLAGS if d.get(k)]} {(d.get('claim_in_article') or '')[:90]} | {(d.get('issue') or '')[:100]}")
    out.append(f"  (件数 {n_new_major})")
    out.append("\n[旧でMAJOR・新でMAJORでない件]")
    n_gone = 0
    for f in arts:
        o, n = res["old"][f["key"]], res["new"][f["key"]]
        if o is None or n is None or srcs["old"][f["key"]] != "rerun":
            continue
        for d in o:
            if d["severity"] == "MAJOR" and not any(C.sent_match(d.get("claim_in_article", ""), x.get("claim_in_article", "")) and x["severity"] == "MAJOR" for x in n):
                n_gone += 1
                out.append(f"  {f['key'].replace('ART_', '')[:60]}: {d.get('origin')} {[k for k in FLAGS if d.get(k)]} {(d.get('claim_in_article') or '')[:90]}")
    out.append(f"  (件数 {n_gone})")
    # 費用
    for arm in ("old", "new"):
        c = sum(load(arm, f)[2] for f in fx)
        out.append(f"\n費用(rerun分のみ) {arm}: ¥{c:.3f}")
    txt = "\n".join(out)
    open(f"{V.V2}/V2_RESULTS.txt", "w", encoding="utf-8").write(txt)
    print(txt)


if __name__ == "__main__":
    main()
