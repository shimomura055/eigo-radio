import json,os,hashlib,sys
sys.path.insert(0,'.')
R=json.load(open('er079_output/family_c_ja_tts_production_fix_01/evidence_02/run_c_prime/run_c_prime.json',encoding='utf-8'))
fn=[r['clip'] for r in R['phase1_rows'] if r['false_negative']]
base='er013_output/family_c_episode_trial_11/memory_a2'
shas={c:hashlib.sha256(open(f'{base}/audio/{c}','rb').read()).hexdigest() for c in fn}
hits={c:[] for c in fn}
for root,d,files in os.walk('.'):
    if '.venv' in root or '.git' in root.split(os.sep): continue
    if 'tts_generation_results.json' in files and root.endswith('audit'):
        try: a=json.load(open(os.path.join(root,'tts_generation_results.json'),encoding='utf-8'))
        except Exception: continue
        for k,v in (a.get('segments') or {}).items():
            for c,s in shas.items():
                if isinstance(v,dict) and v.get('sha256')==s:
                    hits[c].append((root,k,v.get('reused')))
for c in fn:
    fresh=[h for h in hits[c] if not h[2]]
    print(c,len(hits[c]),'fresh:',[h[0] for h in fresh][:3])
