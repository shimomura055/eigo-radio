# -*- coding: utf-8 -*-
"""T3 集計(API無し、決定論)。使い方: analyze.py --oracle oracle_dev --tags dev [--reps devreps] [--b3x b3x] --out NAME"""
import sys, re, json, glob, argparse, collections, importlib, pathlib
sys.path.insert(0, 'er052_output/open233_link_precision_01')
import units_lib as U
RL, cov, OUT = U.RL, U.cov, U.OUT

NEG = re.compile(r"\b(no|not|nor|never|none|neither|without|nothing|nobody|cannot)\b|n't|\b(lack|lacks|unknown|unclear)\b", re.I)
MARK = re.compile(r"未提示|示されて(い)?ない|示されていません|明記(されて)?(い)?ない|不明|確認できない|公表されて(い)?ない|開示されて(い)?ない|言及(が|は)ない|"
                  r"not (stated|specified|provided|disclosed|shown|explained|identified|reported|confirmed|clear|known|available)|unknown|unclear|unspecified|"
                  r"not been (shown|reported|explained)", re.I)
STOP = set("that this with from have been were they their there which what when about also only than into more some other while then will would could does said such just even still much many most like these those each every because after before over under between through being where whether verified scope conditions notes writer numeric value period date source sources fact facts".split())


def toks(s):
    return {w.lower() for w in re.findall(r"[A-Za-z][A-Za-z\-']{3,}|\d[\d,\.]*", s)} - STOP


def strip_keys(block):
    return re.sub(r"(?m)^\s*(scope|conditions|numeric_value|numeric_scope|date_or_period|notes_for_writer)\s*:", " ", block)


def load_ng():
    ng = {}
    for l in open('er052_output/open233_stage0_01/reclass/known_relation_ng.jsonl', encoding='utf-8'):
        j = json.loads(l)
        ng[j['item_id']] = j
    return ng


def run_info(run, kind):
    d = pathlib.Path(run)
    led = (d / 'research_ledger/verified_fact_ledger.txt').read_text(encoding='utf-8')
    ids = list(cov.ledger_fact_blocks(led).keys())
    sel = None
    for p in (d / 'storyline_b3/fact_selection_evidence.json', d.parent / 'storyline_b3/fact_selection_evidence.json',
              d.parent / 'b1/storyline_b3/fact_selection_evidence.json'):
        if p.exists():
            sel = json.loads(p.read_text(encoding='utf-8')).get('selected_fact_ids')
            break
    return led, ids, sel


def _num(s):
    m = re.search(r"(\d+)\s*$", s or "")
    return int(m.group(1)) if m else None


def norm_id(x, ledger_ids):
    if x in ledger_ids:
        return x
    n = _num(x)
    if n is None:
        return None
    c = [i for i in ledger_ids if _num(i) == n and i[:1].lower() == (x or '')[:1].lower()]
    return c[0] if len(c) == 1 else None


def load_outputs(tag):
    out = {}
    for f in glob.glob(str(OUT / 'r3' / tag / '*.json')):
        d = json.loads(pathlib.Path(f).read_text(encoding='utf-8'))
        out[(d['run'], d['rep'])] = d
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--oracle', default='oracle_dev')
    ap.add_argument('--tags', default='dev')
    ap.add_argument('--reps', default=None)
    ap.add_argument('--b3x', default=None)
    ap.add_argument('--out', default='dev_summary')
    a = ap.parse_args()
    O = importlib.import_module(a.oracle)
    ng = load_ng()
    outs = {}
    for t in a.tags.split(','):
        outs.update(load_outputs(t))
    runs_all = sorted({k[0] for k in outs})

    def find_run(sfx):
        key = sfx.split('/runs/')[-1]
        c = [r for r in runs_all if r.replace(chr(92), '/').endswith(key) and sfx.split('/')[0] in r]
        assert len(c) == 1, (sfx, c)
        return c[0]

    S = {"per_run": {}, "items": [], "n_runs": len(runs_all)}
    rows = []
    for r in runs_all:
        d = outs[(r, 1)]
        led, ids, sel = run_info(r, d['kind'])
        S['per_run'][r] = {"n_ledger_ids": len(ids), "selected": sel}
        for u in d['units']:
            if not u['judged']:
                continue
            sf = (d['support_fact_ids'] or {}).get(u['id'])
            if sf is None:
                continue
            rows.append({"run": r, "unit": u['id'], "text": u['text'], "raw": sf, "norm": [norm_id(x, ids) for x in sf],
                         "verdict": (d['model_verdict'] or {}).get(u['id']), "ledger_ids": ids, "sel": sel})
    S['n_judged_units_with_record'] = len(rows)
    nonempty = [x for x in rows if x['raw']]
    S['c_empty_rate'] = {"empty": len(rows) - len(nonempty), "total": len(rows), "rate": round((len(rows) - len(nonempty)) / max(1, len(rows)), 4)}
    S['c_empty_by_verdict'] = {v: {"empty": sum(1 for x in rows if x['verdict'] == v and not x['raw']),
                                   "total": sum(1 for x in rows if x['verdict'] == v)} for v in ('SUPPORTED', 'CANDIDATE', 'CONFLICT', 'MISSING')}

    def b_stats(key):
        tot = ok_sel = ok_led = out_sel = unresolved = 0
        for x in nonempty:
            ids = x[key]
            tot += 1
            if any(i is None for i in ids):
                unresolved += 1
                continue
            if x['sel'] is not None and set(ids) <= set(x['sel']):
                ok_sel += 1
            if all(i in x['ledger_ids'] for i in ids):
                ok_led += 1
            if x['sel'] is not None and (set(ids) - set(x['sel'])):
                out_sel += 1
        return {"n_nonempty_units": tot, "subset_of_selected": ok_sel, "rate_selected": round(ok_sel / max(1, tot), 4),
                "ids_exist_in_ledger": ok_led, "rate_in_ledger": round(ok_led / max(1, tot), 4), "refs_outside_selected": out_sel, "unresolved_ids_units": unresolved}

    exact_sel = sum(1 for x in nonempty if x['sel'] is not None and set(x['raw']) <= set(x['sel']))
    exact_led = sum(1 for x in nonempty if all(i in x['ledger_ids'] for i in x['raw']))
    S['b_strict_exact'] = {"n_nonempty_units": len(nonempty), "subset_of_selected": exact_sel, "rate_selected": round(exact_sel / max(1, len(nonempty)), 4),
                           "ids_exact_in_ledger": exact_led, "rate_in_ledger": round(exact_led / max(1, len(nonempty)), 4)}
    S['b_normalized_post_hoc'] = b_stats('norm')
    nonled = collections.Counter(i for x in nonempty for i in x['raw'] if i not in x['ledger_ids'])
    S['nonledger_id_examples'] = nonled.most_common(12)
    S['n_ids_nonledger_of_total'] = [sum(nonled.values()), sum(len(x['raw']) for x in nonempty)]

    cand_by = {}
    for (r, rep), d in outs.items():
        if rep != 1:
            continue
        for c in d['candidates']:
            for uid in c['unit_ids'] or []:
                cand_by.setdefault((r, uid), set()).update(c.get('related_fact_ids') or [])
    A = []
    for it, sfx, uids in O.MAIN:
        r = find_run(sfx)
        d = outs[(r, 1)]
        led, ids, sel = run_info(r, d['kind'])
        j = ng[it]
        sf, rel, verd = set(), set(), []
        for u in uids:
            sf |= set((d['support_fact_ids'] or {}).get(u, []))
            rel |= cand_by.get((r, u), set())
            verd.append((d['model_verdict'] or {}).get(u))
        nsf = {norm_id(x, ids) or x for x in sf}
        nrel = {norm_id(x, ids) or x for x in rel}
        oracle = j['fact_id']
        A.append({"item": it, "type": j['sentence_type'], "ledger_corr": j['ledger_correspondence'], "oracle": oracle, "units": uids,
                  "support_raw": sorted(sf), "related": sorted(rel), "verdict": verd, "empty": not sf,
                  "hit_strict": (oracle in sf) if oracle else None, "hit_norm": (oracle in nsf) if oracle else None,
                  "hit_with_related": (oracle in (nsf | nrel)) if oracle else None})
    S['items'] = A
    known = [x for x in A if x['oracle']]
    S['a'] = {"n_known_ng": len(known), "hit_strict": sum(x['hit_strict'] for x in known), "hit_norm_post_hoc": sum(x['hit_norm'] for x in known),
              "hit_with_related_a2": sum(x['hit_with_related'] for x in known)}
    bt = collections.defaultdict(lambda: [0, 0, 0, 0])
    for x in known:
        b = bt[x['type']]
        b[0] += 1
        b[1] += x['hit_strict']
        b[2] += x['hit_norm']
        b[3] += x['hit_with_related']
    S['a_by_type'] = {k: {"n": v[0], "strict": v[1], "norm": v[2], "with_related": v[3]} for k, v in bt.items()}
    S['c_ng'] = {"located": len(A), "empty": sum(x['empty'] for x in A),
                 "by_type": {t: {"n": sum(1 for x in A if x['type'] == t), "empty": sum(1 for x in A if x['type'] == t and x['empty'])}
                             for t in sorted({x['type'] for x in A})},
                 "by_ledger_corr": {t: {"n": sum(1 for x in A if x['ledger_corr'] == t), "empty": sum(1 for x in A if x['ledger_corr'] == t and x['empty'])}
                                    for t in sorted({x['ledger_corr'] for x in A})}}
    if a.reps:
        ro = load_outputs(a.reps)
        by_run = collections.defaultdict(dict)
        for (r, rep), d in list(outs.items()) + list(ro.items()):
            by_run[r][rep] = d
        res = {}
        for r, reps in by_run.items():
            if not all(k in reps for k in (1, 2, 3)):
                continue
            ds = [reps[k] for k in (1, 2, 3)]
            ids = run_info(r, ds[0]['kind'])[1]
            tot = same_s = same_n = sup3 = sup3_same = vs = 0
            for u in ds[0]['units']:
                if not u['judged']:
                    continue
                sets = [frozenset((d['support_fact_ids'] or {}).get(u['id'], [])) for d in ds]
                nsets = [frozenset(norm_id(x, ids) or x for x in s) for s in sets]
                tot += 1
                same_s += len(set(sets)) == 1
                same_n += len(set(nsets)) == 1
                vv = [(d['model_verdict'] or {}).get(u['id']) for d in ds]
                vs += len(set(vv)) == 1
                if all(v == 'SUPPORTED' for v in vv):
                    sup3 += 1
                    sup3_same += len(set(nsets)) == 1
            res[r] = {"n_judged": tot, "same_strict": same_s, "same_norm": same_n, "all3_supported": sup3, "all3_supported_same_norm": sup3_same, "verdict_same": vs}
        n = sum(v['n_judged'] for v in res.values())
        T = lambda k: sum(v[k] for v in res.values())
        S['d'] = {"runs": res, "n_units": n, "same_strict": T('same_strict'), "rate_strict": round(T('same_strict') / max(1, n), 4),
                  "same_norm_post_hoc": T('same_norm'), "rate_norm_post_hoc": round(T('same_norm') / max(1, n), 4),
                  "all3_supported": T('all3_supported'), "all3_supported_same_norm": T('all3_supported_same_norm'), "verdict_same": T('verdict_same')}
    S['cost_jpy'] = round(sum(sum(e['cost_jpy'] for e in json.load(open(f, encoding='utf-8'))['entries']) for f in glob.glob(str(OUT / 'cost_*.json'))), 4)

    all_runs = [(r, outs[(r, 1)]) for r in runs_all]
    if a.b3x:
        bo = load_outputs(a.b3x)
        all_runs += [(r, d) for (r, rep), d in bo.items()]
    flagged, arts = [], {}
    for r, d in all_runs:
        led, ids, sel = run_info(r, d['kind'])
        blocks = cov.ledger_fact_blocks(led)
        ns_blocks = {fid: b for fid, b in blocks.items() if MARK.search(b)}
        ns_tok = set().union(*[toks(strip_keys(b)) for b in ns_blocks.values()]) if ns_blocks else set()
        n_j = n1 = n2 = 0
        for u in d['units']:
            if not u['judged']:
                continue
            sf = (d['support_fact_ids'] or {}).get(u['id'])
            if sf is None:
                continue
            n_j += 1
            if sf or not NEG.search(u['text']):
                continue
            r1 = bool(ns_blocks)
            sh = toks(u['text']) & ns_tok
            r2 = bool(sh)
            n1 += r1
            n2 += r2
            flagged.append({"run": r, "unit": u['id'], "R1": r1, "R2": r2, "shared": sorted(sh)[:6], "text": u['text'][:120]})
        arts[r] = {"n_judged": n_j, "R1": n1, "R2": n2, "n_notstated_facts": len(ns_blocks), "n_ledger_ids": len(ids)}
    S['rule_R'] = {"articles": len(arts), "judged_units": sum(v['n_judged'] for v in arts.values()),
                   "flagged_units_R1": sum(v['R1'] for v in arts.values()), "flagged_units_R2": sum(v['R2'] for v in arts.values()),
                   "articles_with_flag_R1": sum(1 for v in arts.values() if v['R1']), "articles_with_flag_R2": sum(1 for v in arts.values() if v['R2']),
                   "per_article": arts}
    S['flagged'] = flagged
    (OUT / f'{a.out}.json').write_text(json.dumps(S, ensure_ascii=False, indent=1), encoding='utf-8')
    brief = {k: S[k] for k in S if k not in ('items', 'per_run', 'flagged')}
    brief['rule_R'] = {k: v for k, v in S['rule_R'].items() if k != 'per_article'}
    if 'd' in brief:
        brief['d'] = {k: v for k, v in S['d'].items() if k != 'runs'}
    print(json.dumps(brief, ensure_ascii=False, indent=1)[:6000])


main()
