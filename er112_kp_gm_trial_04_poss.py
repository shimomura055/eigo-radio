# -*- coding: utf-8 -*-
"""FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_14: 課題② Trial runner(DEV専用)。units構築 / 実行(C0A=a1_c, C1A=a1r_c) / 決定論スコア。
Production fileは編集しない。C0AとC1Aは**別プロセス**で実行する(C1Aは許可表へmy/ourのsomeone'sを一時追加するため。同一プロセスでC0Aを走らせない)。
サブコマンド: units / run --arms a1_c|a1r_c / score
"""
from __future__ import annotations

import argparse, hashlib, json, os, re, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")
import er112_kp_gm_trial_04 as X                    # noqa: E402
import er112_kp_gm_trial_01 as t1                   # noqa: E402
import er112_kp_gm_poss_04 as P                     # noqa: E402

OUT = X.OUT
UNITS = OUT / "poss_units.json"
RUNS = OUT / "poss_runs"
BS = chr(92)

# 目視ラベル(出現順の所有格ごとのrole)。出典=er112_output/kp_gm_design_05/t1_referent_table.py REF(委任_13、T-1)。
GOLD = {
    "pumps its fist": ["self"], "pump its fist": ["self"], "in your place": ["other_person"], "held out his hands": ["self"], "go out of their way": ["self"],
    "reach for your wallet": ["self"], "told her the truth": ["none"], "lose her job": ["self"], "shock your wallet": ["other_person"],
    "apply its findings": ["non_person"], "use its results": ["non_person"], "at their own pace": ["self"], "room for their own pace": ["self"],
    "a place of my own": ["self"], "change my surroundings": ["self"], "make something your whole life": ["self"], "occupy their thoughts": ["self"],
    "give my word": ["self"], "my word": ["self"], "catch your breath": ["self"], "catch my breath": ["self"], "choose their words": ["self"],
    "turned on its head": ["non_person"], "catch their attention": ["other_person"], "a piece of your attention": ["other_person"],
    "compete through its presence": ["non_person"], "enforce their rules": ["non_person"], "out of our hands": ["self"], "find its way back": ["non_person"],
    "look her in the face": ["none"],
}

# 型の網羅用合成unit(個別対策ではなく、再帰+別の人/二重所有/物が動作主の定型句/組織/話者my/総称you+物主語/複数名詞を含むrole型の確認)。
# 例示(Promptの規則3の例)とは別の語句を使う。articleは短い自作文(特定記事の語句ではない)。gold=所有格の出現順role。
SYN04 = [
    ("syn6", "When Anna read the angry letter from her neighbors, she paused and tried to put herself in their shoes. Maria always pulled her own weight on the team. "
             "Every river eventually runs its course and reaches the sea.",
     [("put herself in their shoes", "When Anna read the angry letter from her neighbors, she paused and tried to put herself in their shoes.", ["other_person"]),
      ("pulled her own weight", "Maria always pulled her own weight on the team.", ["self"]),
      ("runs its course", "Every river eventually runs its course and reaches the sea.", ["non_person"])]),
    ("syn7", "The airline keeps its promise to refund every customer within a week. The young pilot offered to take my place on the final flight, and I thanked him. "
             "At the market, something always catches your eye. If you see a fight, mind your own business.",
     [("keeps its promise", "The airline keeps its promise to refund every customer within a week.", ["non_person"]),
      ("take my place", "The young pilot offered to take my place on the final flight, and I thanked him.", ["other_person"]),
      ("catches your eye", "At the market, something always catches your eye.", ["other_person"]),
      ("mind your own business", "If you see a fight, mind your own business.", ["self"])]),
    ("syn8", "After the third delay, the manager raised her voice at the whole team. The teacher admired their courage in front of the class. "
             "A new paper questioned its methods. After the meeting, the voters changed their minds about the plan.",
     [("raised her voice", "After the third delay, the manager raised her voice at the whole team.", ["self"]),
      ("admired their courage", "The teacher admired their courage in front of the class.", ["other_person"]),
      ("questioned its methods", "A new paper questioned its methods.", ["non_person"]),
      ("changed their minds", "After the meeting, the voters changed their minds about the plan.", ["self"])]),
]


def _orig_item(i, disp, sent, span=None):
    return dict(rank=i, source_span=span or disp, source_sentence=sent, display_phrase=disp, fulltext_source_ref="fulltext_exact_v1",
                source_sentence_id=f"S{i}", occurrence_count=1, occurrence_sentence_ids=[f"S{i}"], selection_resolution_method="fulltext_exact_unique",
                declared_word_count_mismatch=False)


def _article_for(fdir: Path):
    for cand in (fdir / "canonicalization_prompt.txt", fdir.parent / "canonicalization_prompt.txt"):
        if cand.exists():
            try:
                return t1._article_from_prompt(cand)
            except Exception:
                pass
    # key_phrases/<level>/ 形式
    for cand in fdir.glob("**/canonicalization_prompt.txt"):
        try:
            return t1._article_from_prompt(cand)
        except Exception:
            continue
    return None


def build_units():
    rows = json.load(open(ROOT / "er112_output/kp_gm_design_05/t1_possessive_items.json", encoding="utf-8"))
    units, covered, skipped = [], set(), []
    for r in rows:
        f = ROOT / r["file"].replace(BS, "/")
        if "er112_output" in str(f).replace(BS, "/"):
            continue     # DEV Trial出力は元データではない(SYN unitはtrial_01のunits.jsonから別途取り込む)
        pair = (r["display"].lower(), r["sent"])
        if pair in covered:
            continue
        try:
            merged = json.load(open(f, encoding="utf-8"))
        except Exception as e:      # noqa: BLE001
            skipped.append((r["display"], "load:" + str(e)))
            continue
        items = merged.get("items") or []
        mine = [it for it in items if (it.get("display_phrase") or "").lower() == r["display"].lower() and it.get("source_sentence") == r["sent"]]
        if not mine:
            skipped.append((r["display"], "item_not_found"))
            continue
        art = _article_for(f.parent)
        ctx = "article"
        if not art:
            ctx = "sentences_only"
            art = " ".join(dict.fromkeys(it.get("source_sentence", "") for it in items if it.get("source_sentence")))
        # 同一ファイルの全item(<=5)を入力にする(非所有格itemは非劣化の対照)
        sel = sorted(items, key=lambda it: it.get("rank", 99))[:5]
        if not any(it in sel for it in mine):
            sel = mine + [it for it in sel if it not in mine][:4]
        orig = []
        for i, it in enumerate(sel, 1):
            orig.append(_orig_item(i, it.get("display_phrase") or it.get("used_form"), it.get("source_sentence") or "", it.get("source_span")))
        uid = "R_" + hashlib.sha256((art + "|".join(o["display_phrase"] for o in orig)).encode("utf-8")).hexdigest()[:10]
        if any(u["unit_id"] == uid for u in units):
            continue
        gold = {str(o["rank"]): GOLD.get(o["display_phrase"].lower()) for o in orig}
        for o in orig:
            covered.add((o["display_phrase"].lower(), o["source_sentence"]))
        units.append(dict(unit_id=uid, run=str(r["file"]).replace(BS, "/"), level="b1b", family="R", article_text=art, original_items=orig, production={}, synthetic=True,
                          context=ctx, gold=gold, src_file=r["file"].replace(BS, "/")))
    # trial_01の既存SYN(syn2/syn4/syn5)
    u1 = json.load(open(ROOT / "er112_output/kp_gm_trial_01/inputs/units.json", encoding="utf-8"))["units"]
    for u in u1:
        if u["unit_id"].startswith("SYN_syn") and any(P.possessive_slots(o["display_phrase"]) or o["display_phrase"].lower() in GOLD for o in u["original_items"]):
            u = dict(u)
            u["gold"] = {str(o["rank"]): GOLD.get(o["display_phrase"].lower()) for o in u["original_items"]}
            u["context"] = "article"
            units.append(u)
    for sid, art, items in SYN04:
        oi = [_orig_item(i, d, s) for i, (d, s, g) in enumerate(items, 1)]
        gold = {str(i): g for i, (d, s, g) in enumerate(items, 1)}
        units.append(dict(unit_id=f"SYN_{sid}__b1b", run=f"SYN/{sid}", level="b1b", family="SYN", article_text=art, original_items=oi, production={}, synthetic=True,
                          context="article", gold=gold))
    return units, skipped


def cmd_units(a):
    units, skipped = build_units()
    OUT.mkdir(parents=True, exist_ok=True)
    UNITS.write_text(json.dumps(dict(units=units, skipped=skipped), ensure_ascii=False, indent=1), encoding="utf-8")
    n_it = sum(len(u["original_items"]) for u in units)
    n_poss = sum(1 for u in units for o in u["original_items"] if P.possessive_slots(o["display_phrase"]))
    n_lab = sum(1 for u in units for k, g in u["gold"].items() if g is not None)
    print("units", len(units), "items", n_it, "possessive-slot items", n_poss, "gold-labelled", n_lab, "skipped", skipped)
    for u in units:
        print(u["unit_id"], u["context"], [o["display_phrase"] for o in u["original_items"]])


def cmd_run(a):
    arms = a.arms.split(",")
    poss = [x for x in arms if x in P.POSS_ARMS]
    assert not (poss and len(poss) != len(arms)), "C0A(a1_c)とC1A(a1r_c)は別プロセスで実行する"
    t1.LEDGER = X.LEDGER
    if poss:
        P.install_poss_patches(mode=a.mode)
    else:
        t1.install_dev_patches()
    start_h = t1.prod_hashes()
    hs = OUT / "production_hash_start.json"
    if not hs.exists():
        hs.write_text(json.dumps(start_h, indent=1), encoding="utf-8")
    else:
        assert json.loads(hs.read_text(encoding="utf-8")) == start_h, "Production module hash drift since Trial start"
    units = json.load(open(UNITS, encoding="utf-8"))["units"]
    reps = [int(x) for x in a.reps.split(",")]
    if a.units:
        units = [u for u in units if any(w in u["unit_id"] for w in a.units.split(","))]
    jobs = [(arm, rep, u) for arm in arms for rep in reps for u in units]

    def w(j):
        arm, rep, u = j
        if X.stop() or X.total() >= a.cap:
            return (arm, rep, u["unit_id"], "SKIP")
        rec = t1.run_unit(arm, rep, u, out_root=RUNS)
        d = RUNS / arm / f"rep{rep}" / u["unit_id"]
        if poss:
            with P._LOG_LOCK:
                lg = P.LOGS.get((arm, rep, u["unit_id"]))
            if lg is not None:
                (d / "poss_log.json").write_text(json.dumps(lg, ensure_ascii=False, indent=1), encoding="utf-8")
        return (arm, rep, u["unit_id"], rec.get("canon_status") or rec.get("error"))
    with ThreadPoolExecutor(a.workers) as ex:
        for f in as_completed([ex.submit(w, j) for j in jobs]):
            print(f.result(), "cum=%.3f" % X.total(), flush=True)
    end_h = t1.prod_hashes()
    (OUT / ("production_hash_end_%s.json" % "_".join(arms))).write_text(json.dumps(end_h, indent=1), encoding="utf-8")
    print("production_hash_unchanged:", start_h == end_h)


def load_run(arm, rep, uid):
    p = RUNS / arm / f"rep{rep}" / uid / "result.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def cmd_score(a):
    units = json.load(open(UNITS, encoding="utf-8"))["units"]
    import collections
    arms = ["a1_c", "a1r_c"]
    reps = [1, 2]
    tab = {arm: collections.Counter() for arm in arms + ["a1r_c:raw", "a1r_c:revert", "a1r_c:role_roles_only"]}
    detail, role_acc = [], collections.Counter()
    statuses = {arm: collections.Counter() for arm in arms}
    repair_status = collections.Counter()
    ctrl_same = collections.Counter()
    for u in units:
        gold = u["gold"]
        for rep in reps:
            rs = {arm: load_run(arm, rep, u["unit_id"]) for arm in arms}
            for arm in arms:
                r = rs[arm]
                if r:
                    statuses[arm][r.get("canon_status") or "ERR"] += 1
            lg = None
            p = RUNS / "a1r_c" / f"rep{rep}" / u["unit_id"] / "poss_log.json"
            if p.exists():
                lg = json.loads(p.read_text(encoding="utf-8"))
            for o in u["original_items"]:
                rank = o["rank"]
                disp = o["display_phrase"]
                slots = P.possessive_slots(disp)
                g = gold.get(str(rank))
                keys = {}
                for arm in arms:
                    r = rs[arm]
                    it = next((x for x in (r or {}).get("items", []) if x["rank"] == rank), None) if r else None
                    keys[arm] = it["key_phrase"] if it else None
                if not slots:   # 対照item: 非所有格(keyの同一性)
                    if keys["a1_c"] is not None and keys["a1r_c"] is not None:
                        ctrl_same["c0a_vs_c1a_same" if keys["a1_c"] == keys["a1r_c"] else "c0a_vs_c1a_diff"] += 1
                    continue
                if g is None or keys["a1_c"] is None:
                    continue
                sc0 = P.score_headword(disp, keys["a1_c"], g)
                tab["a1_c"][sc0] += 1
                if keys["a1r_c"] is not None:
                    tab["a1r_c"][P.score_headword(disp, keys["a1r_c"], g)] += 1
                # a1r_c: 生出力(修復前)と revert モードを同じ出力から事後計算
                if lg:
                    last = lg[-1] if lg and "items" in lg[-1] else None
                    li = next((x for x in (last or {}).get("items", []) if x["rank"] == rank), None)
                    if li:
                        raw = li["key_before"]
                        tab["a1r_c:raw"][P.score_headword(disp, raw, g)] += 1
                        tab["a1r_c:revert"][P.score_headword(disp, li["repair_revert"]["key_after"], g)] += 1
                        ok, why = P.validate_roles(li["roles"], disp)
                        repair_status[li["repair_role"]["status"]] += 1
                        if ok:
                            for (di, dt), gr, rr in zip(slots, g, li["roles"]):
                                role_acc["role==gold" if rr["role"] == gr else "role!=gold(%s->%s)" % (gr, rr["role"])] += 1
                        else:
                            role_acc["roles_unverified"] += 1
                        detail.append(dict(unit=u["unit_id"], rep=rep, disp=disp, gold=g, c0a=keys["a1_c"], raw=raw, c1a=keys["a1r_c"], roles=li["roles"], status=li["repair_role"]["status"]))
    print("== 見出し語スコア(所有格を含む目視ラベル付きitem x rep)")
    for k, c in tab.items():
        n = sum(c.values())
        print("%-24s n=%d  %s" % (k, n, dict(c)))
    print("== role判定 vs 目視gold:", dict(role_acc))
    print("== 修復status(role mode):", dict(repair_status))
    print("== canon_status:", {k: dict(v) for k, v in statuses.items()})
    print("== 対照(非所有格item)のC0A vs C1A key同一性:", dict(ctrl_same))
    (OUT / "poss_score_detail.json").write_text(json.dumps(detail, ensure_ascii=False, indent=1), encoding="utf-8")
    for d in detail:
        sc_raw = P.score_headword(d["disp"], d["raw"], d["gold"])
        sc_c1a = P.score_headword(d["disp"], d["c1a"], d["gold"]) if d["c1a"] else None
        sc_c0a = P.score_headword(d["disp"], d["c0a"], d["gold"])
        if "WRONG" in (sc_raw, sc_c1a, sc_c0a):
            print("[rep%d] %s | gold=%s | C0A=%s(%s) | C1A-raw=%s(%s) | C1A-final=%s(%s) | roles=%s | %s" % (
                d["rep"], d["disp"], d["gold"], d["c0a"], sc_c0a, d["raw"], sc_raw, d["c1a"], sc_c1a, [x["role"] for x in (d["roles"] or [])], d["status"]))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd")
    ap.add_argument("--arms", default="a1_c")
    ap.add_argument("--reps", default="1,2")
    ap.add_argument("--cap", type=float, default=X.CAP_JPY)
    ap.add_argument("--mode", default="role")
    ap.add_argument("--workers", type=int, default=5)
    ap.add_argument("--units", default="")
    a = ap.parse_args()
    if a.cmd == "units":
        cmd_units(a)
    elif a.cmd == "run":
        cmd_run(a)
    elif a.cmd == "score":
        cmd_score(a)
