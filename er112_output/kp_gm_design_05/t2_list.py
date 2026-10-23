import json,collections
def rows(n):
    for i,l in enumerate(open(f'er112_output/kp_gm_trial_0{n}/results.jsonl',encoding='utf-8'),1):
        if l.strip():
            try: yield i,json.loads(l)
            except Exception: pass
for n in (2,3):
    c=collections.Counter((d.get('kind'),d.get('arm')) for i,d in rows(n))
    print(n,sorted(c.items(),key=str))
for n in (2,3):
    for i,d in rows(n):
        if d['key'] in ('draw a line','an unseen clock') and d['kind'] in('G','E'):
            print(n,i,d['kind'],d['arm'],d['rep'],d['gloss'] if d['kind']=='G' else json.dumps({k:d.get(k) for k in d if k not in('sent','call_cost_jpy','key','kind')},ensure_ascii=False)[:260])
