import json,glob,os,collections
BS=chr(92)
def load_all():
    files=set()
    for p in ['er052_output/**/checker/**/*.json','er052_output/**/runs/*.json']:
        files|=set(f.replace(BS,'/') for f in glob.glob(p,recursive=True))
    rows=[]
    for f in sorted(files):
        try: d=json.load(open(f,encoding='utf-8'))
        except Exception: continue
        if isinstance(d,dict) and isinstance(d.get('stage1_coverage'),dict):
            rows.append((f,d))
    return rows
if __name__=='__main__':
    rows=load_all()
    print(len(rows))
    print(collections.Counter('/'.join(f.split('/')[1:2]) for f,d in rows))
    print(collections.Counter('/'.join(f.split('/')[1:3]) for f,d in rows))
    f,d=rows[0]; print(sorted(d['switches'].keys()))
    print(collections.Counter(d['stage1_coverage'].get('candidate_filter') is not None for f,d in rows))
    print(collections.Counter(str(d['switches'].get('STAGE1_RECLASSIFY','<absent>'))+'|'+str(d['switches'].get('FLOOR_MODE','<absent>')) for f,d in rows))
    print(collections.Counter(str(sorted(d.keys())) for f,d in rows).most_common(3))
