# -*- coding: utf-8 -*-
"""JA-GLOSS-QUALITY-ALARM-TRIAL-01 委任_02B: 評価単位・バッチ計画の構築(API 0・決定論、seed=20261101)。
出力: trial/units.json, trial/batches_dev.json, trial/batches_final.json
unit: 検査される1項目(uid)。eval(JAQ-T*)とpool(JAQ-P-*)を持つ。評価ラベルは凍結ファイルのみ(labels_frozen_01.json、T1/T3はitems.json)。
"""
import json, os, re, random, collections
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.path.dirname(HERE)
J = lambda p: json.load(open(os.path.join(BASE, p), encoding="utf-8"))
SEED = 20261101
MAXB = 12


def n(s):
    return re.sub(r"\s+", " ", s.replace("’", "'").replace("‘", "'")).strip().lower()


def build():
    items = J("eval_set/items.json"); arts = J("eval_set/articles.json"); pool = J("adjudication/pool.json")
    pool_arts = J("eval_set/pool_articles.json"); L = J("labels_frozen_01.json")
    fl = {x["source_id"]: x for x in L["items"]}; t3p = {x["source_id"]: x for x in L["t3prime"]}
    units = {}
    # pool units
    pidx = collections.defaultdict(list)
    for q in pool:
        lab = fl[q["pid"]]
        u = dict(uid=q["pid"], kind="pool", slug=q["slug"], level=q["level"], family=q["family"], expression=q["expression"], current_ja=q["current_ja"],
                 sentence_en=q["sentence_en"], context_before=q["context_before"] or "", context_after=q["context_after"] or "", file=q["file"],
                 label=lab["label"], severity=lab["severity"], category=lab["category"], reason_ja_frozen=lab["reason_ja"], suggestion_frozen=lab["suggestion"],
                 borderline_normal=lab["borderline_normal"], in_dev_set=q["in_dev_set"], tier="POOL", split="pool", eval_ids=[])
        units[q["pid"]] = u
        pidx[(q["slug"], q["level"], n(q["expression"]), n(q["current_ja"]))].append(q["pid"])
    # eval units
    for i in items:
        if i["tier"] in ("T2", "T4"):
            lab = fl[i["id"]]; label, sev, cat, reason, sug, bn = lab["label"], lab["severity"], lab["category"], lab["reason_ja"], lab["suggestion"], lab["borderline_normal"]
        elif i["tier"] == "T3P":
            lab = t3p[i["id"]]; label, sev, cat, reason, sug, bn = "problem", lab["severity"], lab["category"], lab.get("basis", ""), "", False
        else:
            label, sev, cat, reason, sug, bn = i["label"], i["severity"], None, i.get("note", ""), "", False
        # 対応pool (real項目のみ)
        pm = None
        if i["tier"] in ("T1", "T2", "T4"):
            for (sl, lv, ex, cj), ps in pidx.items():
                if sl in i["article_key"] and lv == i["level"] and ex == n(i["expression"]) and cj == n(i["current_ja"]):
                    pm = ps[0]; break
        u = dict(uid=i["id"], kind="eval", tier=i["tier"], split=i["split"], article_key=i["article_key"], level=i["level"], family=i["family"],
                 expression=i["expression"], current_ja=i["current_ja"], sentence_en=i["sentence_en"], context_before=i["context_before"] or "",
                 context_after=i["context_after"] or "", label=label, severity=sev, category=cat, reason_ja_frozen=reason, suggestion_frozen=sug,
                 borderline_normal=bn, synthetic_of_id=i.get("synthetic_of_id"), synthetic_of=i.get("synthetic_of"), must_not_share=i.get("must_not_share_batch_with", []),
                 pool_uid=pm)
        u["severity_agent"] = sev
        if i["tier"] == "T1" and pm:   # Fable決定(2): T1 severityは rubric適用後(=凍結pool裁定)を主、agent案(items.json)を併記
            u["severity"] = units[pm]["severity"]; u["category"] = units[pm]["category"]
        units[i["id"]] = u
        if pm:
            units[pm]["eval_ids"].append(i["id"]); units[pm]["eval_split"] = i["split"]
    return units, arts, pool_arts


def art_text(u, arts, pool_arts):
    lk = "adv" if u["level"] == "Advanced" else "std"
    if u["kind"] == "eval":
        return arts[u["article_key"]][lk]
    return pool_arts[u["file"]]


def make_batches(units, arts, pool_arts, phase, rng):
    """phase: dev -> 評価対象=eval split=dev(全tier)。final -> 評価対象=自然batch(全pool)+eval held_out のうちpool未対応/合成。"""
    B = []
    evals = [u for u in units.values() if u["kind"] == "eval"]
    pool_by = collections.defaultdict(list)
    for u in units.values():
        if u["kind"] == "pool": pool_by[(u["slug"], u["level"])].append(u["uid"])
    if phase == "final":
        # 自然batch: pool group
        for (sl, lv), ids in sorted(pool_by.items()):
            ids = sorted(ids)
            u0 = units[ids[0]]
            B.append(dict(bid=f"N|{sl}|{lv}", kind="natural", level=lv, art=u0["file"], article_text=pool_arts[u0["file"]], uids=ids, scored=ids))
        target = [u for u in evals if u["split"] == "held_out" and (u["tier"] in ("T3", "T3P") or u["pool_uid"] is None)]
    else:
        target = [u for u in evals if u["split"] == "dev"]
    # E batch: (article_key, level, synthetic?) ごと
    grp = collections.defaultdict(list)
    for u in target:
        syn = u["tier"] in ("T3", "T3P")
        grp[(u["article_key"], u["level"], syn)].append(u)
    for (ak, lv, syn), us in sorted(grp.items()):
        slug = next((u["slug"] for u in units.values() if u["kind"] == "pool" and u["slug"] in ak), None)
        text = art_text(us[0], arts, pool_arts)
        # 分割(合成は元項目とbatchを分ける: viewBに集約済み。 realとsynの混在なし)
        for k in range(0, len(us), MAXB):
            chunk = us[k:k + MAXB]
            ids = [u["uid"] for u in chunk]
            excl = set()
            for u in chunk:
                if u["synthetic_of_id"]: excl.add(u["synthetic_of_id"])
                excl.update(u["must_not_share"])
                if u["pool_uid"]: excl.add(u["pool_uid"])
            # 対応するpool uid(評価項目のpool相当)・合成元のpool相当は除外(同表現の二重出現回避)
            exprs = {n(units[i]["expression"]) for i in ids}
            for e in list(excl):
                if e in units:
                    pu = units[e].get("pool_uid")
                    if pu: excl.add(pu)
                    for x in units[e].get("eval_ids", []): excl.add(x)
            cand = [p for p in sorted(pool_by.get((slug, lv), [])) if p not in excl and n(units[p]["expression"]) not in exprs]
            # 優先: dev phaseでは devでもheld-outでもないpool、final phaseでは自然batchで別途採点されるのでどれでも
            if phase == "dev":
                cand.sort(key=lambda p: (bool(units[p]["eval_ids"]), p))
            rng.shuffle(cand) if phase == "final" else None
            fill = cand[:max(0, MAXB - len(ids))]
            B.append(dict(bid=f"E|{ak}|{lv}|{'S' if syn else 'R'}|{k//MAXB}", kind="eval", level=lv, art=ak, article_text=text, uids=ids + fill, scored=ids, filler=fill))
    return B


def main():
    units, arts, pool_arts = build()
    rng = random.Random(SEED)
    dev = make_batches(units, arts, pool_arts, "dev", rng)
    fin = make_batches(units, arts, pool_arts, "final", rng)
    json.dump(units, open(os.path.join(BASE, "trial/units.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(dev, open(os.path.join(BASE, "trial/batches_dev.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(fin, open(os.path.join(BASE, "trial/batches_final.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for nm, B in (("dev", dev), ("final", fin)):
        print(nm, "batches", len(B), "items", sum(len(b["uids"]) for b in B), "scored", sum(len(b["scored"]) for b in B))
    return units, dev, fin


if __name__ == "__main__":
    main()
