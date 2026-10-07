# -*- coding: utf-8 -*-
"""見逃し型への追加規則案(v0.1候補)の負荷/検出率を試算。DANGER_COVERAGE.mdの補足。Productionへは未接続。"""
import json, os, re, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import danger_sentence_rules_v0 as D
import run_match as M

OUT = M.OUT
rows = [json.loads(l) for l in open(OUT + '/sentence_flags.jsonl', encoding='utf8')]
items = json.load(open(OUT + '/ng_detail.json', encoding='utf8'))
led = {}
for s in ('ai_control', 'hormuz', 'meta', 'sewer', 'space_weapons'):
    led[s] = D.parse_ledger(M.LEDGER.format(slug=s))

DIR_JA = re.compile(r'(戻[しさせ]|元に|ロールバック|巻き戻|撤回|取り下げ|置き換え)')
DIR_EN = re.compile(r'\b(roll(?:ed)? back|rollback|put .{0,30}back|returned|revert|restor|withdr|replac)', re.I)
ANAPH_JA = re.compile(r'(^|[、。])(この|その|あの)[一-龥ァ-ヴー]{1,6}(は|が|を|も)')
ANAPH_EN = re.compile(r'\b(this|that|these|those) (feature|plan|move|case|system|test|idea|step)\b', re.I)
FREQ_JA = re.compile(r'(たびに|ごとに|毎回|その都度)')
FREQ_EN = re.compile(r'\b(each time|every time|per |whenever)\b', re.I)
INCL_JA = re.compile(r'(含まれ|含む|含め|入っていた|まとめて)')
INCL_EN = re.compile(r'\b(includes?|including|encompass|covers?|all of)\b', re.I)


def extras(sent, lang, slug):
    facts, ltxt = led[slug]
    f = {}
    if lang == 'ja':
        if DIR_JA.search(sent): f['DIRWORD'] = 1
        if ANAPH_JA.search(sent): f['ANAPH'] = 1
        if FREQ_JA.search(sent): f['FREQ'] = 1
        if INCL_JA.search(sent): f['INCL'] = 1
        terms = [t for t in D._JA_RUN.findall(sent) if len(t) >= 3 and t not in D.JA_GENERIC]
        nov = [t for t in terms if t not in ltxt]
        if len(nov) >= 3: f['NOVEL3'] = 1
        if len(nov) >= 2: f['NOVEL2'] = 1
    else:
        if DIR_EN.search(sent): f['DIRWORD'] = 1
        if ANAPH_EN.search(sent): f['ANAPH'] = 1
        if FREQ_EN.search(sent): f['FREQ'] = 1
        if INCL_EN.search(sent): f['INCL'] = 1
    ids = D.link_facts(sent, lang, facts)
    if len(ids) >= 2: f['MULTIFACT'] = 1
    return f


slug_of = {}
for r in rows:
    r['x'] = extras(r['sent'], r['lang'], r['slug'])
N = len(rows)
sel = [it for it in items if it['src'] != 'pending' and it['sev'] != 'dup_of_P8' and not it['r0_only'] and it['m']]
slug_for_item = {}
for it in sel:
    sl = None
    if it['src'] == 'past8':
        sl = {'meta': 'meta', 'ai': 'ai_control', 'sw': 'space_weapons', 'hormuz': 'hormuz'}[re.search(r'P8-\d (meta|ai|sw|hormuz)', it['id']).group(1)]
    else:
        sl = it['id'].split('-')[0]
    it['slug'] = sl
    for t, m in it['m'].items():
        m['x'] = extras(m['sent'], 'en' if t == 'en' else 'ja', sl)
P3 = ['NEG', 'UNIV', 'SUBJ', 'CAUSE']
base_missed = [it for it in sel if not any(any(x in m['auto'] for x in P3) for m in it['m'].values())]
out = {}
for k in ('DIRWORD', 'ANAPH', 'FREQ', 'INCL', 'NOVEL2', 'NOVEL3', 'MULTIFACT'):
    load = sum(k in r['x'] for r in rows) / N
    det_all = sum(any(k in m['x'] for m in it['m'].values()) for it in sel) / len(sel)
    rescued = [it['id'] for it in base_missed if any(k in m['x'] for m in it['m'].values())]
    out[k] = dict(load=load, det_all=det_all, rescued_of_P3_missed=len(rescued), rescued_ids=rescued)
# P3 + 追加規則
for combo in (['DIRWORD', 'ANAPH'], ['DIRWORD', 'ANAPH', 'FREQ', 'INCL', 'MULTIFACT'], ['DIRWORD', 'ANAPH', 'FREQ', 'INCL', 'MULTIFACT', 'NOVEL3']):
    def fl(r): return any(x in r['fired'] for x in P3) or any(x in r['x'] for x in combo)
    load = sum(fl(r) for r in rows) / N
    det = sum(any(any(x in m['auto'] for x in P3) or any(x in m['x'] for x in combo) for m in it['m'].values()) for it in sel) / len(sel)
    out['P3+' + '+'.join(combo)] = dict(load=load, det=det)
json.dump(out, open(OUT + '/extra_rules_trial.json', 'w', encoding='utf8'), ensure_ascii=False, indent=1)
for k, v in out.items():
    print(k, {a: (round(b, 3) if isinstance(b, float) else b) for a, b in v.items() if a != 'rescued_ids'})
print('base P3 missed', len(base_missed), 'of', len(sel))


# ---- 拡張規則集合(基本7+追加7)の部分集合探索(ビットマスク)。deployable=auto linkのみ ----
import itertools
BASE = ['NEG', 'UNIV', 'CAUSE', 'NUM', 'LIMIT_HEDGE', 'LIMIT_SCOPE', 'SUBJ']
EXTRA = ['DIRWORD', 'ANAPH', 'FREQ', 'INCL', 'NOVEL2', 'MULTIFACT']
ALLR = BASE + EXTRA
def has(fd, x): return (x in fd['fired']) if x in BASE else (x in fd['x'])
rmask = {x: sum((1 << i) for i, r in enumerate(rows) if has(r, x)) for x in ALLR}
imask = {x: sum((1 << j) for j, it in enumerate(sel) if any((x in m['auto']) if x in BASE else (x in m['x']) for m in it['m'].values())) for x in ALLR}
res = []
for k in range(1, len(ALLR) + 1):
    for sub in itertools.combinations(ALLR, k):
        rm = 0; im = 0
        for x in sub:
            rm |= rmask[x]; im |= imask[x]
        res.append(('+'.join(sub), bin(rm).count('1') / N, bin(im).count('1') / len(sel)))
ok = sorted([r for r in res if r[1] <= 0.40], key=lambda r: -r[2])[:8]
ok30 = sorted([r for r in res if r[1] <= 0.30], key=lambda r: -r[2])[:3]
passing = [r for r in res if r[1] <= 0.40 and r[2] >= 0.80]
print('EXT best load<=40:'); [print('  ', r[0], round(r[1], 3), round(r[2], 3)) for r in ok]
print('EXT best load<=30:'); [print('  ', r[0], round(r[1], 3), round(r[2], 3)) for r in ok30]
print('EXT passing(det>=0.8 & load<=0.4):', len(passing)); [print('  ', r[0], round(r[1], 3), round(r[2], 3)) for r in sorted(passing, key=lambda r: r[1])[:5]]
out['ext_best_le40'] = [dict(rules=r[0], load=r[1], det=r[2]) for r in ok]
out['ext_best_le30'] = [dict(rules=r[0], load=r[1], det=r[2]) for r in ok30]
out['ext_passing'] = [dict(rules=r[0], load=r[1], det=r[2]) for r in sorted(passing, key=lambda r: r[1])[:10]]
json.dump(out, open(OUT + '/extra_rules_trial.json', 'w', encoding='utf8'), ensure_ascii=False, indent=1)
