import json,re,glob
def jsplit(t):
    # split after 。！？ (and following closing quotes/brackets)
    return [x for x in re.split(r'(?<=[。！？])(?![」』）])',t) if x.strip()]
tot=eq=paras=0
for f in sorted(glob.glob('user_test/*/enduser/data/article.json')):
    a=json.load(open(f,encoding='utf-8')); nm=f.replace(chr(92),'/').split('/')[1]
    for lv,L in a['levels'].items():
        pe=pq=se=sj=0
        for p in L['parts']:
            if not p.get('ja'): continue
            # pair EN paragraphs with JA paragraphs by index only when counts match
            if len(p['paragraphs'])==len(p['ja']):
                prs=list(zip(p['paragraphs'],p['ja']))
            else:
                prs=[(sum(p['paragraphs'],[]),'\n'.join(p['ja']))]
            for en,ja in prs:
                pe+=1; j=jsplit(ja); se+=len(en); sj+=len(j)
                if len(en)==len(j): pq+=1
        if pe: print(nm[:38],lv,'paras',pe,'eq',pq,'enS',se,'jaS',sj)
