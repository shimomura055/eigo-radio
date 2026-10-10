# -*- coding: utf-8 -*-
"""ROOTFIX-02 Phase 2b 段階1: D-det v2 評価(決定論・LLM/API不使用・費用0)。
  python b3r2_v2eval_03.py [freeze|--probe]    (--probe: freeze前の動作確認。frozen照合なし・結果は評価に使わない)
  出力: eval_v2/v2_eval_results_03.json, eval_v2/diff_v1_v2_03.md, eval_v2/blind_sheet_v2_03.md, eval_v2/m11_v2/..."""
import sys, os, json, hashlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import b3r2_eval_01 as E
import b3r2_rank_01 as R1
import b3r2_rank_02 as R2
from b3sep_common_01 import THEMES, theme_inputs, rj, wj, wt, sha
OUT = f"{HERE}/eval_v2"
FROZEN3 = f"{HERE}/frozen_b3r2_03.json"


def sha_file(p):
    return sha(open(p, encoding="utf-8", newline="").read().replace("\r\n", "\n"))


MODS = ("b3r2_rank_01.py", "b3r2_rank_02.py", "b3r2_eval_01.py")


def freeze():
    out = {"_prereg_sha256": sha_file(f"{HERE}/PREREGISTRATION_03.md"), "_modules": {k: sha_file(f"{HERE}/{k}") for k in MODS}, "themes": {}}
    for th in THEMES:
        ti = theme_inputs(th)
        out["themes"][th] = {"ledger_sha256": sha(ti["ledger"]), "topic_sha256": sha(ti["topic"]), "c0_selected_fact_ids": ti["ev"]["selected_fact_ids"],
                             "c0_storyline_sha256": sha(ti["ev"]["selected_storyline"])}
    wj(FROZEN3, out)
    print("frozen", out["_prereg_sha256"][:12], out["_modules"])


def verify_frozen():
    fz = rj(FROZEN3)
    cur = {k: sha_file(f"{HERE}/{k}") for k in MODS}
    for k, v in cur.items():
        assert fz["_modules"][k] == v, f"frozen module changed: {k}"
    assert fz["_prereg_sha256"] == sha_file(f"{HERE}/PREREGISTRATION_03.md"), "PREREGISTRATION_03 changed after freeze"
    for th in THEMES:
        ti = theme_inputs(th)
        assert sha(ti["ledger"]) == fz["themes"][th]["ledger_sha256"], th
    return fz


def run(RK, th, c0):
    E.RK = RK
    ti = theme_inputs(th)
    return E.ddet(ti["ledger"], c0[th]["ids"], c0[th]["story"])


def sig(d):
    return [(i["fact_id"], i["surface"], i["role"], i["eligible"]) for i in d["items"]]


def main():
    if "freeze" in sys.argv:
        return freeze()
    probe = "--probe" in sys.argv
    if not probe:
        verify_frozen()
    E.EV = OUT
    os.makedirs(OUT, exist_ok=True)
    c0 = {th: {"ids": theme_inputs(th)["ev"]["selected_fact_ids"], "story": theme_inputs(th)["ev"]["selected_storyline"]} for th in THEMES}
    res = {"probe": probe, "per_theme": {}, "rerun_equal": True}
    md = ["# D-det v1 vs v2 差分一覧(9テーマ、C0のID+Storyline)\n"]
    for th in THEMES:
        d1 = run(R1, th, c0); d2 = run(R2, th, c0)
        d2b = run(R2, th, c0)
        res["rerun_equal"] &= sig(d2) == sig(d2b)
        m1 = {(i["fact_id"], i["surface"]): (i["role"], i["eligible"]) for i in d1["items"]}
        m2 = {(i["fact_id"], i["surface"]): (i["role"], i["eligible"]) for i in d2["items"]}
        # 表記単位(fact_idが変わる_STORY->Fact紐付けは表記で比較)
        s1 = {i["surface"]: (i["fact_id"], i["role"], i["eligible"]) for i in d1["items"]}
        s2 = {i["surface"]: (i["fact_id"], i["role"], i["eligible"]) for i in d2["items"]}
        diffs = []
        for s in sorted(set(s1) | set(s2)):
            if s1.get(s) != s2.get(s):
                diffs.append({"surface": s, "v1": s1.get(s), "v2": s2.get(s)})
        res["per_theme"][th] = {"identical": not diffs and d1["cap"] == d2["cap"] and d1["capped_off"] == d2["capped_off"], "diffs": diffs,
                                "cap_v1": d1["cap"], "cap_v2": d2["cap"], "n_concepts_v1": d1["n_concepts"], "n_concepts_v2": d2["n_concepts"],
                                "capped_off_v1": d1["capped_off"], "capped_off_v2": d2["capped_off"],
                                "core_v1": [i["surface"] for i in d1["items"] if i["role"] == "core"], "core_v2": [i["surface"] for i in d2["items"] if i["role"] == "core"]}
        md.append(f"\n## {th}: {'同一' if res['per_theme'][th]['identical'] else '差分あり'}  (cap {d1['cap']}->{d2['cap']}, 概念数 {d1['n_concepts']}->{d2['n_concepts']})")
        for x in diffs:
            md.append(f"- 表記「{x['surface']}」 v1(fact,role,適格)={x['v1']} -> v2={x['v2']}")
        md.append(f"- core v1: {res['per_theme'][th]['core_v1']}\n- core v2: {res['per_theme'][th]['core_v2']}")
    # GT比較(v1 / v2。既知値の参考)
    for tag, RK in (("v1", R1), ("v2", R2)):
        E.RK = RK
        rows = []
        for th in THEMES:
            d = run(RK, th, c0)
            rows.append({"theme": th, **E.gt_compare(th, E.role_by_key(d["items"]))})
        res["GT_" + tag] = {"per_theme": rows, "total": E.sum_gt(rows)}
        nc = [r for r in rows if r["theme"] != "central_bank_mortgage"]
        res["GT_" + tag]["excluding_central_bank"] = E.sum_gt(nc)
    # M11(既存注記検査、v2)
    E.RK = R2
    m = E.m11("ddet_v2_c0", lambda th: (theme_inputs(th)["ledger"], c0[th]["ids"], c0[th]["story"], E.ddet(theme_inputs(th)["ledger"], c0[th]["ids"], c0[th]["story"])))
    res["M11_v2"] = {"summary": E.summarize_m11(m), "per_theme": m}
    meta_only = all(all(E.categorize_problem(p) == "meta:annotator" for ps in r["problems"].values() for p in ps) for r in m.values())
    res["M11_v2"]["only_meta_annotator_problems"] = meta_only
    wj(f"{OUT}/v2_eval_results_03.json", res)
    wt(f"{OUT}/diff_v1_v2_03.md", "\n".join(md))
    # Blind(v2のcore集合)
    lines = ["# v2 中核/周辺一覧(Blind目視用)\n"]
    for th in THEMES:
        d = run(R2, th, c0)
        core = [f"{i['surface']}({i['fact_id']})" for i in d["items"] if i["role"] == "core"]
        per = [f"{i['surface']}({i['fact_id']})" for i in d["items"] if i["role"] != "core"]
        lines.append(f"\n## {th}\n- Storyline: {c0[th]['story']}\n- 中核: {', '.join(core)}\n- 周辺: {', '.join(per)}\n")
    wt(f"{OUT}/blind_sheet_v2_03.md", "\n".join(lines))
    print(json.dumps({"rerun_equal": res["rerun_equal"], "identical": {t: v["identical"] for t, v in res["per_theme"].items()},
                      "GT_v1": res["GT_v1"]["total"], "GT_v2": res["GT_v2"]["total"], "M11_v2": res["M11_v2"]["summary"], "only_meta": meta_only}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
