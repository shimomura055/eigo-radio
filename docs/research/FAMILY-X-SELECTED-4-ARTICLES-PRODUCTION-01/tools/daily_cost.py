# 本日(JST)累計費用の概算。使い方: .venv/Scripts/python.exe daily_cost.py [UTC開始時刻 既定=JST 0:00=前日15:00Z]
# 対象: ファイル名に'usage'または'cost_log'を含む*.jsonl(token記録: openai/gemini/openai_asr/azure)と、provider無しで cost_jpy を持つ記録(Trial usage_log等)。
# 除外: *pre02a*(退避コピー)、.claude/worktrees(コピー)、.git/.venv。限界: gemini_batch・TTS等の単価未登録providerは0円扱い(概算の下限)。
import os,sys,json,time
sys.path.insert(0,'.')
import er012_e_family_entertainment_two_level_runner_01 as efam
import er005_cost_logger as cl
price=efam._load_pricing(); J=efam.USD_JPY
cut=time.time()-60*60*48
START=sys.argv[1] if len(sys.argv)>1 else "2026-10-28T15:00:00"
tot=0.0; per={}; skipped={}
for root,ds,fs in os.walk('.'):
    ds[:]=[d for d in ds if d not in ('.git','.venv','node_modules','__pycache__','worktrees') and 'pre02a' not in d]
    for f in fs:
        if not f.endswith('.jsonl') or not ('usage' in f or 'cost_log' in f): continue
        p=os.path.join(root,f)
        if os.path.getmtime(p)<cut: continue
        s=0.0
        for line in open(p,encoding='utf-8',errors='replace'):
            try: r=json.loads(line)
            except: continue
            if not isinstance(r,dict): continue
            ts=r.get('timestamp') or ''
            if isinstance(ts,str) and ts and ts[:19]<START: continue
            prov=r.get('provider'); m=r.get('model_id') or r.get('model')
            if r.get('success') is False: continue
            try:
                if prov is None and isinstance(r.get('cost_jpy'),(int,float)):
                    s+=r['cost_jpy']; continue            # Trial usage_log(timestamp無し=ファイルmtimeが48h以内の全件。過大側)
                if prov=='azure': u=cl.azure_stt_cost_usd(r,price)
                elif prov in('openai','gemini','openai_asr') and m:
                    u=(r.get('input_tokens') or 0)*price(prov,m,'input_tokens')/1e6+(r.get('output_tokens') or 0)*price(prov,m,'output_tokens')/1e6
                    if prov=='openai': u+=efam.web_search_call_usd(r,price)
                else:
                    skipped[prov]=skipped.get(prov,0)+1; continue
            except Exception as e:
                skipped['ERR:'+str(prov)]=skipped.get('ERR:'+str(prov),0)+1; continue
            s+=u*J
        if s: per[p]=round(s,1); tot+=s
print('TOTAL_JPY_approx',round(tot,1),'skipped(0円扱い)=',skipped)
for p,v in sorted(per.items(),key=lambda x:-x[1])[:25]: print(v,p)
