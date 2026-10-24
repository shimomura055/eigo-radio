import json
b=json.load(open('runtime_base_06.json',encoding='utf-8'))['records'];a=json.load(open('runtime_after_06.json',encoding='utf-8'))['records']
def k(r): return ('BLOCKED' if r.get('blocked') else 'ok', r.get('unified_state'), r.get('reason_code'))
n=0;stored=0;api=0
for x,y in zip(b,a):
    ch = k(x)!=k(y)
    n+=ch
    if y.get('variant')=='stored' and ch: stored+=1
    api+=(y.get('api_calls') or 0)+(y.get('secondary_new_calls') or 0)
    if ch or 'OPEN-491' in str(y.get('variant')): print('*' if ch else ' ', y['scope'], y['segment'], y['variant'], '|', k(x),'->',k(y))
print('records',len(a),'changed',n,'; 保存entry(variant=stored)の変化:',stored,'; api/secondary新規呼出合計',api)
