# -*- coding: utf-8 -*-
"""委任_07 Trial: Judge実行(DEV専用、評価側)。er112_kp_gm_judge_01の2系統Judge基盤を再利用し、出力先をkp_gm_trial_02へ切替。
armラベルは評価者に見せない(blind: 行にはkey/sentence/textのみ。arm対応はrow_map_02.jsonに分離保存)。
行kind: E3(英語説明) / G(日本語gloss) / P(Std/Adv整合) 。hard20のみgold_reference(draft)を付与。
"""
from __future__ import annotations
import argparse, json, sys, time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")
import er112_kp_gm_judge_01 as jd   # noqa: E402
import er112_kp_gm_trial_01 as tr   # noqa: E402
import er112_kp_gm_trial_02 as T    # noqa: E402

OUT = T.OUT
jd.configure_out(OUT)
tr.LEDGER = T.LEDGER
ROWMAP = OUT / "row_map_02.json"
GOLD_PATH = OUT / "gold_labels_draft_01.json"
KINDS = {"E": "E3", "G": "G"}


def gold_text(key):
    g = json.load(open(GOLD_PATH, encoding="utf-8"))
    for k, v in g.items():
        if k.lower() == key.lower() and isinstance(v, dict):
            return "用法=%s / 許容される意味=%s / 不可=%s / 英語の許容範囲=%s / 別解釈=%s" % (v["usage"], v["ok_ja"], v["ng_ja"], v["ok_en"], v["alt"])
    return None


def build(res=None):
    res = res or T.load_res()
    rows, rmap = {}, defaultdict(list)
    for (arm, key, rep), r in res.items():
        if r["kind"] == "E":
            row = dict(kind="E3", key_phrase=key if False else r.get("key_phrase", key), source_sentence=r["sent"], explanation=r["text"])
            row["key_phrase"] = key
            text = r["text"]
        elif r["kind"] == "G" and r.get("gloss"):
            row = dict(kind="G", key_phrase=key, source_sentence=r["sent"], gloss=r["gloss"])
            text = r["gloss"]
        else:
            continue
        g = gold_text(key)
        if g:
            row["gold_reference"] = g
        row["id"] = jd.rid(row["kind"], key, r["sent"], text)
        rows.setdefault(row["id"], row)
        rmap[row["id"]].append([arm, key, rep])
    # P(Std/Adv整合): hard20の (Std gloss arm, Adv arm) 組。arm名は "P:<G>+<E>"
    for (garm, earm) in PAIRS:
        for (a, key, rep), r in res.items():
            if a != garm or rep != 1 or r["kind"] != "G" or not r.get("gloss"):
                continue
            e = res.get((earm, key, 1))
            if not e:
                continue
            row = dict(kind="P", key_phrase=key, source_sentence=r["sent"], gloss_ja=r["gloss"], explanation_en=e["text"])
            g = gold_text(key)
            if g:
                row["gold_reference"] = g
            row["id"] = jd.rid("P", key, r["gloss"], e["text"])
            rows.setdefault(row["id"], row)
            rmap[row["id"]].append(["P:%s+%s" % (garm, earm), key, 1])
    return rows, rmap


PAIRS = [("G3", "E4"), ("G0", "E0@G0")]


def run(judges, kinds, arms_filter, hard_only, cap, workers=4, limit_ids=None, dry=False, reps=None, keys=None):
    rows, rmap = build()
    json.dump(rmap, open(ROWMAP, "w", encoding="utf-8"), ensure_ascii=False)
    gold = json.load(open(GOLD_PATH, encoding="utf-8"))
    goldkeys = {k.lower() for k in gold if not k.startswith("_")}
    todo = defaultdict(list)
    caches = {j: jd.load_cache(j) for j in judges}
    for rid_, rw in rows.items():
        if kinds and rw["kind"] not in kinds:
            continue
        refs = rmap[rid_]
        if (arms_filter or reps or keys) and not any((not arms_filter or a in arms_filter) and (not reps or r in reps) and (not keys or k.lower() in keys) for a, k, r in refs):
            continue
        if hard_only and rw["key_phrase"].lower() not in goldkeys:
            continue
        if limit_ids is not None and rid_ not in limit_ids:
            continue
        for j in judges:
            if rid_ not in caches[j]:
                todo[(j, rw["kind"])].append(rw)
    jobs = []
    for (j, kind), rs in todo.items():
        rs.sort(key=lambda x: x["id"])
        for i in range(0, len(rs), jd.BATCH):
            jobs.append((j, kind, rs[i:i + jd.BATCH]))
    print("rows", len(rows), "jobs", len(jobs), {f"{k[0]}:{k[1]}": len(v) for k, v in todo.items()}, flush=True)
    if dry:
        return
    with ThreadPoolExecutor(max_workers=workers) as ex:
        for f in as_completed([ex.submit(jd.run_batch, j, k, b, cap) for j, k, b in jobs]):
            print(f.result(), f"cum={T.total():.3f}", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--judges", default="sonnet")
    ap.add_argument("--kinds", default="")
    ap.add_argument("--arms", default="")
    ap.add_argument("--hard-only", action="store_true")
    ap.add_argument("--cap", type=float, default=T.CAP_JPY)
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--reps", default="")
    ap.add_argument("--keys", default="")
    a = ap.parse_args()
    run(a.judges.split(","), set(a.kinds.split(",")) if a.kinds else None, set(a.arms.split(",")) if a.arms else None, a.hard_only, a.cap, dry=a.dry, reps={int(x) for x in a.reps.split(",")} if a.reps else None, keys={x.lower() for x in a.keys.split("|") if x} or None)
