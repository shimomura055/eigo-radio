# Trial_03 Std出力の出力単位データセット(Fable最終判定を付与)
import sys, re, json
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent))
from audit_01_common import *

rows, bad = load_jsonl(T3/'results.jsonl')
G = [r for r in rows if r['kind']=='G']
E = [r for r in rows if r['kind']=='E']
key = json.load(open(T3/'fable_blind_std_03_key.json', encoding='utf-8'))
PAT = re.compile(r'^\| (\d+) \| (\w+)/([^/]*)/([XZ-]) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \|\s*$')
blind = {}
for l in open(T3/'fable_blind_std_03.md', encoding='utf-8'):
    m = PAT.match(l)
    if m:
        n = int(m.group(1))
        blind[n] = dict(n=n, tier=m.group(2), typ=m.group(3), fam=m.group(4), key=m.group(5), sent=m.group(6),
                        cells=dict(zip('ABCDEF', [m.group(i) for i in range(7, 13)])))
gl = {}
for r in G:
    gl[(r['arm'], r['key'].lower(), r['rep'])] = r
cell_ar = {}
for n, b in blind.items():
    kkey = [k for k in key if k.lower() == b['key'].lower()]
    assert kkey, b['key']
    kkey = kkey[0]
    b['kkey'] = kkey
    b['byarm'] = {}
    for c, ar in key[kkey].items():
        arm, rep = ar.split('/'); rep = int(rep[3:])
        b['byarm'][(arm, rep)] = (c, b['cells'][c])
# Fable最終判定(FABLE_BLIND_RESULT_03 逐語。PASS以外のセルのみ列挙されている)
FAIL = [(1,'F'),(5,'D'),(15,'D'),(15,'E'),(23,'B'),(23,'D'),(50,'F')]
TIN = [(2,'A'),(13,'E'),(15,'A'),(44,'E'),(54,'A'),(54,'E'),(54,'F')]
def fable(n, c):
    if (n,c) in FAIL: return 'FAIL'
    if (n,c) in TIN: return 'THIN'
    return 'PASS'
if __name__ == '__main__':
    print(len(G), len(E), bad, len(blind))
    mism = 0
    for n, b in blind.items():
        for (arm, rep), (c, s) in b['byarm'].items():
            r = gl.get((arm, b['key'].lower(), rep))
            if r is None: print('MISSING', arm, b['key'], rep); mism += 1; continue
            if r['gloss'] != s: print('MISMATCH', n, arm, rep, r['gloss'], '|', s); mism += 1
    print('mism', mism)
    for (n, c) in FAIL + TIN:
        b = blind[n]; ar = [k for k,v in b['byarm'].items() if v[0]==c][0]
        print(n, c, fable(n,c), b['key'], ar, b['cells'][c], '|', b['sent'][:70])
