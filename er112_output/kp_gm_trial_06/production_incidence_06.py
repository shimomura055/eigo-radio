# -*- coding: utf-8 -*-
"""委任_30 OF-KP2-08(F): 本番KPにおける『比喩・慣用を認識したKP』の発生率と、通常KPへの持ち込み率の比較素材(API 0、既存artifactの再集計のみ)。
 (1) canonicalization reasoning が比喩/慣用を述べるKPの割合(canon_reasoning_census.py と同一pattern)。全artifact版と、mock/dev除外版(K3.RECENT/EXCL)の両方。
 (2) Stage 2 54KP: B0(Trial_04 2rep) と X2p の gloss に対する record-only 持ち込み検出(er112_kp_gm_trial_06.detect_import)の件数。"""
import glob, json, re, sys, collections
sys.path.insert(0, '.')
sys.stdout.reconfigure(encoding='utf-8')
import er112_kp_gm_kpset_03 as K3
pat = re.compile(r'比喩|慣用|イディオム|熟語|figurative|idiom')

def scan(strict):
    seen = {}
    for f in glob.glob('**/keywords_canonicalized.json', recursive=True):
        rel = f.replace(chr(92), '/')
        if strict and (not rel.startswith(K3.RECENT) or any(x in rel.lower() for x in K3.EXCL)):
            continue
        try:
            d = json.load(open(f, encoding='utf-8'))
        except Exception:
            continue
        for it in d.get('items', []):
            if not it.get('fulltext_source_ref'):
                continue
            k = (it.get('source_sentence'), it.get('key_phrase'))
            if k not in seen:
                fam = 'Z' if any(x in rel.lower() for x in ('er026', 'family_z', 'er073', 'melos', 'lemon', 'open_window')) else 'X'
                seen[k] = dict(it, _fam=fam, _file=rel)
    return seen

res = {}
for name, strict in (('all_artifacts', False), ('production_runs_only', True)):
    s = scan(strict)
    hit = {k: v for k, v in s.items() if pat.search(v.get('reasoning') or '')}
    by = collections.Counter(v['_fam'] for v in s.values())
    byh = collections.Counter(v['_fam'] for v in hit.values())
    # run(level)単位: figurative KPを1つ以上含むlevel
    lv = collections.defaultdict(lambda: [0, 0])
    for k, v in s.items():
        lv[v['_file']][0] += 1
        lv[v['_file']][1] += k in hit
    res[name] = dict(unique_items=len(s), figurative=len(hit), rate=round(len(hit) / len(s), 4), by_family=dict(by), figurative_by_family=dict(byh),
                     levels=len(lv), levels_with_figurative=sum(1 for a, b in lv.values() if b), mean_figurative_per_level=round(sum(b for a, b in lv.values()) / len(lv), 3),
                     mean_items_per_level=round(sum(a for a, b in lv.values()) / len(lv), 2), figurative_keys=sorted(k[1] for k in hit))
json.dump(res, open('er112_output/kp_gm_trial_06/production_incidence_06.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for n, r in res.items():
    print(n, {k: v for k, v in r.items() if k != 'figurative_keys'})
print(res['production_runs_only']['figurative_keys'])
