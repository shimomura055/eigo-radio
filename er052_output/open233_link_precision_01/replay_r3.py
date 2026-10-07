# -*- coding: utf-8 -*-
"""T3 Stage1 r3のみのreplay(有料API、Trial専用)。support_fact_idsを保存(OPEN233_SAVE_R3_SUPPORT_IDS=1)。
使い方: replay_r3.py --set main|b3x|heldout|reps --tag NAME [--rep N]
r3 prompt・コードは変更しない。budget: 全cost_*.jsonの合計が35円超でSTOP。"""
import os, sys, json, glob, argparse, time, hashlib
os.environ["OPEN233_SAVE_R3_SUPPORT_IDS"] = "1"
sys.path.insert(0, 'er052_output/open233_link_precision_01')
import units_lib as U
RL, runner, cov, OUT = U.RL, U.runner, U.cov, U.OUT
STOP_JPY = 35.0

def total_cost():
    t = 0.0
    for f in glob.glob(str(OUT / 'cost_*.json')):
        t += sum(e['cost_jpy'] for e in json.load(open(f, encoding='utf-8'))['entries'])
    return t

def targets(which):
    import oracle_dev as O
    if which == 'main':
        return [(r, None) for r in U.article_runs('dev')]
    if which == 'heldout':
        return [(r, None) for r in U.article_runs('heldout')]
    if which == 'b3x':
        b = RL.ROOT / 'er052_output/open233_b3_trial_01/runs'
        return [(str(b / k), 'b3') for k in sorted({m[1] for m in O.B3X})]
    if which == 'reps':  # (d): 3記事。1回目はmain、追加2回
        dev = list(U.article_runs('dev'))
        pick = [[r for r in dev if 'allfact_note_e2e_02/runs/ai_control/nb/p2/rep2' in r][0],
                [r for r in dev if 'allfact_note_e2e_02/runs/hormuz/nb/p2/rep2' in r][0],
                [r for r in dev if 'allfact_note_e2e_02/runs/meta/nb/p2/rep1' in r][0]]
        return [(r, None) for r in pick]

def load(run, kind):
    if kind == 'b3':
        d = pathlib_p(run)
        led = (d / 'research_ledger/verified_fact_ledger.txt').read_text(encoding='utf-8')
        art = (d / 'b1b/article.md').read_text(encoding='utf-8')
        return led, art
    r, led, art = RL.load_run(run)
    return led, art

def pathlib_p(x):
    import pathlib; return pathlib.Path(x)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--set', required=True); ap.add_argument('--tag', required=True); ap.add_argument('--rep', type=int, default=1)
    a = ap.parse_args()
    client = RL.setup(40.0, run_budget_jpy=6.0)
    runner.STAGE1_ROUTES = "r3_only"
    cfg = {"negation_mode": runner.STAGE1_NEGATION_MODE, "r3_reasoning": runner.STAGE1_R3_REASONING}
    print('cfg', cfg, flush=True)
    od = OUT / 'r3' / a.tag; od.mkdir(parents=True, exist_ok=True)
    costf = OUT / f'cost_{a.tag}.json'
    cost = json.load(open(costf, encoding='utf-8')) if costf.exists() else {"entries": []}
    for run, kind in targets(a.set):
        name = (run.replace(chr(92), '/').split('er052_output/')[-1]).replace('/', '__')
        of = od / f'{name}__rep{a.rep}.json'
        if of.exists():
            continue
        if total_cost() >= STOP_JPY:
            print('STOP: cost cap', total_cost(), flush=True); break
        led, art = load(run, kind)
        fixture = {"ledger_text": led, "article_text": art, "source_article_text": None}
        state, ce, call_log = RL.new_state(), [0], []
        call_fn = runner.make_stage1_call_fn(client, state, ce, call_log, f"t3_{a.tag}")
        t0 = time.time()
        res = cov.run_stage1_coverage(fixture, call_fn, routes="r3_only", segment_fn=runner.vs_sentence_segments_l6,
                                      initial_extra=runner.CAUSAL_SENTENCE_INITIAL_EN, negation_mode=runner.STAGE1_NEGATION_MODE)
        au = res["audit"]; r3 = au["per_route"]["r3"]
        sp = U.split(art)
        out = {"run": run, "kind": kind, "rep": a.rep, "tag": a.tag, "cfg": cfg, "api_failure": res["api_failure"],
               "article_sha256": hashlib.sha256(art.encode('utf-8')).hexdigest(),
               "units": [{k: u[k] for k in ('id', 'type', 'judged', 'text')} for u in sp['units']],
               "support_fact_ids": r3.get("support_fact_ids"), "model_verdict": r3.get("model_verdict"), "unit_status": r3.get("unit_status"),
               "candidates": [{"unit_ids": c.get("unit_ids"), "related_fact_ids": c.get("related_fact_ids"), "sub_reasons": c.get("sub_reasons")}
                              for c in r3.get("candidates", [])],
               "missing_after_rerun": r3.get("missing_after_rerun"), "cost_jpy": au["total_cost_jpy"], "n_calls": au["n_calls"],
               "calls": [{k: c.get(k) for k in ('label', 'cost_jpy', 'reasoning_effort', 'error')} for c in r3["calls"]],
               "elapsed": round(time.time() - t0, 1)}
        of.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8')
        cost["entries"].append({"run": name, "rep": a.rep, "cost_jpy": au["total_cost_jpy"], "n_calls": au["n_calls"], "t": time.strftime('%Y-%m-%d %H:%M:%S')})
        costf.write_text(json.dumps(cost, ensure_ascii=False, indent=1), encoding='utf-8')
        print(name, a.rep, au["total_cost_jpy"], 'cum_all', round(total_cost(), 3), flush=True)

main()
