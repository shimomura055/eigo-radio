# NUANCE-QUALITY-IMPROVEMENT-TRIAL-01: 改善Prompt v2 (v1の観察に基づく1回の見直し)。nqt01のhelperを再利用。DEV/Trial専用。
# v1の観察: (1)比較が2文(有無の二項)に偏り「段階が見える」並びが少ない (2)explanation冒頭が「〜と訳すと…」定型 (3)Y Advの現行Production候補(at least)と同一表現の比較がない
import sys, os, json, time, threading
sys.argv = [sys.argv[0]] + sys.argv[1:]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nqt01 as q
V2_FROM = "- comparison型(比較が有効な場合):"
V2_NEW = ("- comparison型(比較が有効な場合): 差が『段階』や『選択肢』として見える並びを優先する(例: 焦点の要素なし → 弱い/中間の形 → 本文の形、または同じ場面で使える複数の語の選択)。"
          "この並びで差が見えるなら3〜4個、二項の対比で足りるなら2個。")
V2_EXPL_FROM = "- 比較または文脈の説明を踏まえ、"
V2_EXPL_NEW = "- 冒頭を毎回『〜と訳すと』の定型にしない。場面に合わせ、読者が最初に抱きそうな誤解・疑問、または具体的な違いの一言から始める。\n- 比較または文脈の説明を踏まえ、"
def new2_tail():
    t = q.NEW_TAIL
    assert V2_FROM in t and V2_EXPL_FROM in t
    t = t.replace(V2_FROM, V2_NEW + " 以下の条件を満たすこと:", 1).replace(V2_EXPL_FROM, V2_EXPL_NEW, 1)
    return t
def build_new2(inputs, fixed=None):
    cur = q.er.build_gen_prompt(inputs); head = cur[:cur.index(q.MARK)]
    return head + new2_tail().format(explen=q.EXPLEN[inputs["level"]], fixed=(q.FIX_TMPL.format(e=fixed) if fixed else ""))
def worker(client, cell, T, res, plan):
    try:
        inputs = q.build_inputs_for(cell, T); r = {"cell": cell}
        def run(cond, prompt):
            t0 = time.time()
            d = q.er.run_candidate(inputs, call_fn=q.make_fn(client, f"{cell}_{cond}", override_prompt=prompt), judge_fn=q.make_fn(client, f"{cell}_{cond}j", max_out=5000))
            r[f"{cond}_wall_sec"] = round(time.time() - t0, 2)
            if not cond.startswith("CUR"): d["trial_extra_issues"] = q.check_new_extras(d, inputs)
            q._save(cell, cond, d); r[cond] = {"status": d["status"], "reason": d.get("no_candidate_reason"), "usage": d["usage"], "extra_issues": d.get("trial_extra_issues")}
        for cond, kind, fx in plan:
            if kind == "new2": run(cond, build_new2(inputs, fx))
            elif kind == "curfix": run(cond, q.build_fixed_current(inputs, fx))
            elif kind == "newfix": run(cond, q.build_new_prompt(inputs, fx))
        res[cell] = r
    except Exception as e:
        import traceback; res[cell] = {"cell": cell, "error": repr(e), "tb": traceback.format_exc()}
def main():
    T = q.v02a.trial.load_targets(); client = q.v02a.get_client(); res = {}; ths = []; plans = {}
    for c in q.CELLS:
        cur = json.load(open(os.path.join(q.ODIR, f"{c}_CUR.json"), encoding="utf-8")); ce = (cur.get("candidate") or {}).get("expression")
        fixed = ce or {"y_surname_std": "at least a little", "y_surname_adv": "at least"}.get(c)
        plans[c] = [("NEW2", "new2", None)] + ([("NEW2FIX", "new2", fixed)] if fixed else [])
    # Y Adv: 現行Production候補(at least)と同一表現の比較
    plans["y_surname_adv"] += [("CURFIXAT", "curfix", "at least"), ("NEWFIXAT", "newfix", "at least")]
    for c, plan in plans.items():
        th = threading.Thread(target=worker, args=(client, c, T, res, plan)); th.start(); ths.append(th)
    for th in ths: th.join()
    p = os.path.join(q.ODIR, "summary_v2_" + time.strftime("%H%M%S") + ".json"); json.dump(res, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print({k: {kk: (vv["status"] if isinstance(vv, dict) and "status" in vv else vv) for kk, vv in v.items() if kk != "tb"} for k, v in res.items()}); print("spent_total_jpy", round(q.spent(), 4))
if __name__ == "__main__":
    main()
