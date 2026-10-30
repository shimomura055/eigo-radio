# -*- coding: utf-8 -*-
"""P4 独立評価(別系列)の一括実行と、Sonnet実読ラベルとの突合。
対象: 各arm(PROD/D/E1L/E4/N1a/N1/N2/N4/N4d/N5/N5d)の『変化があった項目』(PRODは全項目)を(case, span, display_form, gloss)でdedupeして1回だけ評価。
評価器の独立性(M10): ds-v4-pro は deepseek を検査器に使うarm(N4d/N5d)に固有の項目を評価しない。それらと『検査にsolを使うN4/N5固有の変化』のうちsolが検査したものはdsが評価、N4d/N5d固有項目はsolが評価。
使い方: KPG4_CAP=180 python kpg04_eval_all.py --stage ds   (dedupe全件をdsで) / --stage sol (N4d/N5d固有項目と、突合で割れた項目をsolで) / --stage diff (API 0: 実読ラベルとの突合表)"""
import os, sys, json, argparse, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kpg04_llm as L
import kpg04_eval as E
import kpg04_stats as S
import kpg04_run as R

ARMS = ["PROD", "D", "E1L", "E4", "N1a", "N1", "N2", "N4", "N4d", "N5", "N5d"]
OUT = os.path.join(E.EVAL_DIR, "all_items.json")


def build(cases, arms=ARMS):
    corpus = S.corpus()
    U = collections.OrderedDict()
    for arm in arms:
        for x in E.eval_items_for(arm, cases, corpus, only_changed=True):
            k = (x["case"], S.nkey(x["span"]), S.nkey(x["display_form"]), (x["gloss"] or "").strip())
            u = U.setdefault(k, dict(case=x["case"], span=x["span"], display_form=x["display_form"], gloss=x["gloss"], context=x["context"], arms=[]))
            u["arms"].append(arm)
    return U


def judge_model(u):
    """このitemを評価してよい別系列モデル: N4d/N5d(検査器=deepseek)にしか現れない項目はsol、それ以外はds。"""
    only_ds_checked = all(a in ("N4d", "N5d") for a in u["arms"])
    return "gpt-6.1-sol" if only_ds_checked else "deepseek-v4-pro"


def load():
    return json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {}


def save(d):
    json.dump(d, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def run_stage(stage, cases):
    U = build(cases)
    d = load()
    key = lambda k: "|".join(k)
    todo = {"ds": [], "sol": []}
    for k, u in U.items():
        m = judge_model(u)
        if key(k) in d and m in d[key(k)].get("verdicts", {}):
            continue
        todo["sol" if m.startswith("gpt") else "ds"].append((k, u))
    if stage in todo:
        items = todo[stage]
        model = "deepseek-v4-pro" if stage == "ds" else "gpt-6.1-sol"
        res = E.run_eval([u for _, u in items], model, tag=f"all:{stage}", batch=40 if stage == "ds" else 30) if items else []
        d = load()
        for (k, u), r in zip(items, res):
            e = d.setdefault(key(k), dict(case=u["case"], span=u["span"], display_form=u["display_form"], gloss=u["gloss"], arms=u["arms"], verdicts={}, reasons={}))
            e["verdicts"][model] = r["verdict"]; e["reasons"][model] = r["reason_ja"]
        save(d)
    return len(U), {k: len(v) for k, v in todo.items()}


def label_of(u_arm_list, case, display_form, span, gloss):
    """実読ラベル(いずれかのarmでS軸ラベルがあればそれ)を返す。"""
    for arm in u_arm_list:
        it = dict(source_span=span, display_form=display_form, gloss_ja=gloss)
        c, lv, rs = S.label(arm, case, it)
        if c:
            return c, lv, rs, arm
    return None, None, None, None


def diff():
    d = load()
    rows = []
    for k, e in d.items():
        c, lv, rs, arm = label_of(e["arms"], e["case"], e["display_form"], e["span"], e["gloss"])
        v = list(e["verdicts"].values())
        non_ok = [x for x in v if x not in ("OK",)]
        mine_s = c in S.S_CODES
        rows.append((e, c, lv, mine_s, non_ok))
    dis = [(e, c, lv, no) for e, c, lv, ms, no in rows if (ms and lv == "strict" and not no) or ((not ms or lv != "strict") and no and not (c in ("FREE", "NAT", "UNDER_GEN", "OTHER") and not no))]
    return rows, dis


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=["ds", "sol", "diff", "count"])
    ap.add_argument("--cases", default="ALL14,HELDOUT"); ap.add_argument("--phase", default=""); ap.add_argument("--phase-cap", type=float, default=0); ap.add_argument("--mock", action="store_true")
    a = ap.parse_args()
    cases = []
    for c in a.cases.split(","):
        cases += {"ALL14": R.ALL14, "HELDOUT": R.HELDOUT, "HARD6": R.HARD6}.get(c) or [c]
    L.set_mock(a.mock)
    if a.stage == "count":
        U = build(cases)
        ms = collections.Counter(judge_model(u) for u in U.values())
        print("unique items", len(U), dict(ms))
        sys.exit(0)
    if a.stage == "diff":
        rows, dis = diff()
        print("評価済み", len(rows), "/ 突合で割れた", len(dis))
        for e, c, lv, no in dis:
            print(f"  {e['case']} | {e['span']} => {e['display_form']} | {e['gloss']} | arms={','.join(sorted(set(e['arms'])))} | 実読={c}/{lv} | 別系列={e['verdicts']} {list(e['reasons'].values())}")
        sys.exit(0)
    try:
        if a.phase:
            L.enter_phase(a.phase)
        if a.phase_cap and not a.mock:
            L.set_phase_cap(a.phase_cap)
        print(run_stage(a.stage, cases))
    except L.CapReached as e:
        print("CAP_REACHED", e)
        sys.exit(3)
    print("TOTAL ¥", round(L.total_cost(), 2))
