# -*- coding: utf-8 -*-
"""FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_14: 課題① C arm(独立検査 -> flag項目のみ再生成)・C-recheck・盲検表・集計 (DEV専用)。
検査版: KP04_INSPECT_VERSION=v2, KP04_INSPECT_EFFORT=low (Phase 0 v2low、事前宣言のflag規則=V2_inv: usage=figurative かつ gloss_conveys=literal_image_only。内容語重なり[検査不成立]でもflag)。
サブコマンド: inspect / regen / recheck / blind / report
"""
from __future__ import annotations

import argparse, json, os, random, re, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed

os.environ.setdefault("KP04_INSPECT_VERSION", "v2")
os.environ.setdefault("KP04_INSPECT_EFFORT", "low")
import er112_kp_gm_trial_04 as X                      # noqa: E402
import er112_kp_gm_trial_04_gen as G                  # noqa: E402

OUT = X.OUT
sys.stdout.reconfigure(encoding="utf-8")
INSP = OUT / "inspect_main.jsonl"


def trial_set():
    return json.load(open(OUT / "strata_04.json", encoding="utf-8"))["trial_set"]


def b0_rows():
    keys = set(trial_set())
    A = X.all_kps()
    return {(k, rep): r for (k, rep), r in G.b0_outputs(keys).items()}, A


def arm_outputs(arm):
    return {(k, rep): r for (a, k, rep), r in G.load_res().items() if a == arm and r.get("gloss")}


def is_flag(o):
    """事前宣言のflag規則(V2_inv)。"""
    return bool(o) and o["usage_in_sentence"] == "figurative" and o["gloss_conveys"] == "literal_image_only"


def cmd_inspect(a):
    b0, A = b0_rows()
    rows = {}
    for (k, rep), r in list(b0.items()) + list(arm_outputs("M").items()):
        key = (A[k]["key"], A[k]["sent"], r["gloss"])
        rows.setdefault(key, dict(key_phrase=key[0], source_sentence=key[1], gloss=key[2]))
    print("unique triples", len(rows))
    X.run_inspect_rows(list(rows.values()), INSP, a.cap, tag="main_inspect")


def inspect_map(path=INSP):
    return {(r["key_phrase"], r["source_sentence"], r["gloss"]): r["out"] for r in X.read_jsonl(path)}


def reason_text(o):
    return "日本語意味だけを読むと『%s』の意味に取れ、本文での意味『%s』を伝えていない。本文での意味を日本語で表す" % (o["gloss_alone_reading_en"], o["usage_meaning_en"])


def regen_batch(arm_tag, items, cap):
    """items: [(key, rep, prior_gloss, reason)] -> arm_tag='C'(B0由来)/'CpR'(Cp由来)。attempt 2(previous_attempt_rejected)。"""
    A = X.all_kps()
    done = G.load_res()
    todo = [it for it in items if (arm_tag, it[0], it[1]) not in done]
    groups = {}
    for k, rep, g, why in todo:
        groups.setdefault((G.art_id(A[k]), rep), []).append((k, g, why))
    print(arm_tag, "regen items", len(todo), "calls", len(groups), flush=True)

    def w(kv):
        (aid, rep), lst = kv
        if X.stop() or X.total() >= cap:
            return ("SKIP", rep)
        kps = [A[k] for k, g, why in lst]
        prior = {i + 1: {"gloss": g, "reasons": [why]} for i, (k, g, why) in enumerate(lst)}
        items_, c, u = G.gloss_gen("B0", kps, prior=prior)
        X.ledger_add(dict(kind="regen", arm=arm_tag, keys=[k for k, g, why in lst], rep=rep, usage=u, cost_jpy=round(c, 5), ts=time.strftime("%Y-%m-%dT%H:%M:%S")))
        by = {it["rank"]: it for it in items_}
        for i, (k, g, why) in enumerate(lst):
            it = by.get(i + 1) or {}
            G.res_add(dict(arm=arm_tag, key=k, rep=rep, kind="G", sent=A[k]["sent"], gloss=it.get("japanese_gloss"), prior_gloss=g, reason=why, call_cost_jpy=round(c, 5)))
        return (arm_tag, rep, [k for k, g, why in lst], round(c, 4))
    with ThreadPoolExecutor(4) as ex:
        for f in as_completed([ex.submit(w, kv) for kv in groups.items()]):
            print(f.result(), "cum=%.3f" % X.total(), flush=True)


def cmd_regen(a):
    b0, A = b0_rows()
    im = inspect_map()
    items = []
    for (k, rep), r in sorted(b0.items()):
        o = im.get((A[k]["key"], A[k]["sent"], r["gloss"]))
        if is_flag(o):
            items.append((k, rep, r["gloss"], reason_text(o)))
    print("C flagged outputs:", len(items), "of", len(b0))
    regen_batch("C", items, a.cap)
    cp = arm_outputs("Cp")
    items2 = []
    for (k, rep), r in sorted(cp.items()):
        au = r.get("audit") or {}
        if au.get("usage_in_sentence") == "figurative" and au.get("gloss_conveys") == "literal_image_only":
            items2.append((k, rep, r["gloss"], reason_text(au)))
    print("Cp self-audit flagged outputs:", len(items2), "of", len(cp))
    regen_batch("CpR", items2, a.cap)


def cmd_recheck(a):
    A = X.all_kps()
    rows = {}
    for arm in ("C", "CpR"):
        for (k, rep), r in arm_outputs(arm).items():
            key = (A[k]["key"], A[k]["sent"], r["gloss"])
            rows.setdefault(key, dict(key_phrase=key[0], source_sentence=key[1], gloss=key[2]))
    X.run_inspect_rows(list(rows.values()), INSP, a.cap, tag="recheck")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd")
    ap.add_argument("--cap", type=float, default=X.CAP_JPY)
    a = ap.parse_args()
    {"inspect": cmd_inspect, "regen": cmd_regen, "recheck": cmd_recheck}[a.cmd](a)
