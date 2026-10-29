import os,sys,json,time
sys.path.insert(0,'.')
import er012_e_family_entertainment_two_level_runner_01 as efam
price=efam._load_pricing(); J=efam.USD_JPY
cut=time.time()-60*60*40
START="2026-10-28T15:00:00"
tot=0.0; per={}
for root,ds,fs in os.walk('.'):
    ds[:]=[d for d in ds if d not in ('.git','.venv','node_modules','er_fx4_scratch','__pycache__')]
    for f in fs:
        if not f.endswith('.jsonl') or 'usage' not in f: continue
        p=os.path.join(root,f)
        if os.path.getmtime(p)<cut: continue
        s=0.0
        for line in open(p,encoding='utf-8',errors='replace'):
            try: r=json.loads(line)
            except: continue
            ts=r.get('timestamp') or ''
            if ts[:19]<START: continue
            prov=r.get('provider'); m=r.get('model_id') or r.get('model')
            if prov not in('openai','gemini') or not m or r.get('success') is False: continue
            try:
                u=(r.get('input_tokens') or 0)*price(prov,m,'input_tokens')/1e6+(r.get('output_tokens') or 0)*price(prov,m,'output_tokens')/1e6
                if prov=='openai': u+=efam.web_search_call_usd(r,price)
            except Exception as e: continue
            s+=u*J
        if s: per[p]=round(s,1); tot+=s
print('TOTAL_JPY_approx(text-token only)',round(tot,1))
for p,v in sorted(per.items(),key=lambda x:-x[1])[:12]: print(v,p)
