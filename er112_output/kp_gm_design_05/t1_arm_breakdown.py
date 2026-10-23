import json,glob,re,collections,os
rows=[]
for f in glob.glob('er112_output/kp_gm_trial_0*/**/keywords_canonicalized.json',recursive=True):
    f=f.replace(os.sep,'/')
    arm=re.search(r'runs/([^/]+)/(rep\d)',f)
    d=json.load(open(f,encoding='utf-8'))
    for it in d['items']:
        dp,kp=it['display_phrase'],it['key_phrase']
        if re.search(r"\b(my|your|his|her|their|our|its|you|yourself)\b",dp.lower()):
            rows.append((arm.group(1) if arm else '?',arm.group(2) if arm else '?',dp,kp,it.get('normalization_reason')))
c=collections.Counter(rows)
for k,v in sorted(c.items()): print(v,k)
