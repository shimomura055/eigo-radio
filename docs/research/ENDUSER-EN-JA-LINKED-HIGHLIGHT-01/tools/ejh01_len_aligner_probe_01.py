import json,re,sys,math
def jsplit(t): return [x for x in re.split(r'(?<=[。！？])(?![」』）])',t) if x.strip()]
def plain(h): return re.sub('<[^>]+>','',h)
def align(en,ja,ratio=None):
    # monotone DP, moves (i,j) in {1:1,1:2,2:1,2:2,1:3,3:1}; cost by length log-ratio + anchors (digits)
    le=[len(x) for x in en]; lj=[len(x) for x in ja]
    r = ratio or (sum(le)/max(1,sum(lj)))
    def digs(s): return set(re.findall(r'\d[\d,\.]*',s.replace('，',',')))
    def cost(a,b):
        e=sum(le[a[0]:a[1]]); j=sum(lj[b[0]:b[1]])*r
        c=abs(math.log((e+5)/(j+5)))
        c2=0.35*((a[1]-a[0]-1)+(b[1]-b[0]-1))
        return c+c2
    n,m=len(en),len(ja); INF=1e9
    D={(0,0):(0,None)}
    moves=[(1,1),(1,2),(2,1),(2,2),(1,3),(3,1),(1,0),(0,1)]
    for i in range(n+1):
        for j in range(m+1):
            if (i,j) not in D: continue
            c0=D[(i,j)][0]
            for di,dj in moves:
                ni,nj=i+di,j+dj
                if ni>n or nj>m: continue
                cc = c0 + (cost((i,ni),(j,nj)) if di and dj else 1.5)
                if (ni,nj) not in D or cc<D[(ni,nj)][0]: D[(ni,nj)]=(cc,(i,j))
    out=[];k=(n,m)
    while k!=(0,0):
        p=D[k][1]; out.append(((p[0],k[0]),(p[1],k[1]))); k=p
    return out[::-1]
if __name__=='__main__':
    f,lv,label=sys.argv[1:4]
    a=json.load(open(f,encoding='utf-8'))
    for p in a['levels'][lv]['parts']:
        if p['label']==label:
            for pa,ja in zip(p['paragraphs'],p['ja']):
                en=[plain(s['html']) for s in pa]; j=jsplit(ja)
                for (e0,e1),(j0,j1) in align(en,j):
                    print([x[-5:] for x in [s['sid'] for s in pa[e0:e1]]],'<->',[x[:14] for x in j[j0:j1]])
                print()
