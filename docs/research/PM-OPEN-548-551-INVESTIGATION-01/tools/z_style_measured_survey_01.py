import json,sys,glob,collections,os
sys.path.insert(0,'.')
import er063_family_z_audio_01 as a63
base='er026_output/family_z_production_e2e_01'
runs=['the_tell_tale_heart/run_sf_prod_02','the_monkeys_paw/run_sf_prod_01','the_gift_of_the_magi/run_sf_prod_01','the_open_window/run_sf_prod_01','after_twenty_years/run_sf_prod_01','melos/run_e2e_06']
out={}
for r in runs:
  for lv in ('a2','b1b'):
    p=f'{base}/{r}/{lv}/audit/tts_generation_results.json'
    if not os.path.exists(p): continue
    d=json.load(open(p,encoding='utf-8'))
    ents=list(d['segments'].items())
    for kp,v in d.get('key_phrases',{}).items():
        if isinstance(v,dict):
            for k2,e in v.items():
                if isinstance(e,dict) and 'style' in e: ents.append((f'kp{kp}_{k2}',e))
    c=collections.Counter()
    rows=collections.defaultdict(collections.Counter)
    for name,e in ents:
        if not isinstance(e,dict) or 'style' not in e: c['no_style']+=1; continue
        rk=e.get('role_style_key'); kind=e.get('clip_kind')
        exp=a63.style_prefix_sha256(a63.FAMILY_Z_ROLE_STYLE[rk]['text']) if rk in a63.FAMILY_Z_ROLE_STYLE and kind!='dialogue' else None
        att=[a for a in e.get('attempts',[]) if a.get('phase') in('standard','fallback')]
        meas=[a.get('style_prefix_sha256') for a in att]
        last=meas[-1] if meas else 'NOATT'
        if kind=='shell': cls='shell'
        elif last=='NOATT': cls='no_attempts'
        elif last is None: cls='measured_null'
        elif exp is None: cls='dialogue_measured_present'
        elif last==exp: cls='measured_match'
        else: cls='measured_MISMATCH'
        if e['style'].get('fallback_used'): cls+='+fallback'
        rows[rk][cls]+=1
    out[f'{r}/{lv}']={k:dict(v) for k,v in rows.items()}
for k,v in out.items():
    print('==',k)
    for rk,cc in sorted(v.items(), key=lambda x:str(x[0])): print('  ',rk,cc)
