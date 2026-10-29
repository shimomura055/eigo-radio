import json,glob,os,sys
for cell in ["y_surname_std","y_surname_adv","ai_island_std","ai_island_adv","tth_std","tth_adv","y_redelivery_std","y_redelivery_adv"]:
    for cond in ["CUR","CURFIX","CURFIXAT","NEW","NEWFIX","NEWFIXAT","NEW2","NEW2FIX","NEW2FIXAT","NEW2FIXAT_r2","NEW2FIXAT_r3","NEW2FIX_r2","NEW2FIX_r3","NEW3","NEW3FIX","NEW3FIX_r2","NEW3FIX_r3","NEW3FIXAT","NEW3FIXAT_r2","NEW3FIXAT_r3"]:
        p=f"{cell}_{cond}.json"
        if not os.path.exists(p): continue
        d=json.load(open(p,encoding="utf-8")); c=d.get("candidate") or (d.get("rejected_candidate_audit") or {}).get("candidate")
        print(f"=== {cell} {cond} status={d['status']} reason={d.get('no_candidate_reason')} cost={d['usage']['cost_jpy']} extra={d.get('trial_extra_issues')}")
        if not c: print("  gen:", json.dumps((d.get('generation') or {}).get('model_reason_ja'),ensure_ascii=False)); continue
        print(" expr:",c['expression'],"|",c['focus']); print(" quote:",c['quote_en'])
        if c.get('point_ja'): print(" point:",c['point_ja'])
        print(" type:",c.get('comparison_type'))
        for x in c.get('comparisons') or []: print("   ",x['label'],("[TEXT]" if x.get('is_text') else ""),x['en'],"/",x['ja'],"/",x['note_ja'])
        print(" expl:",c['explanation_ja'], f"({len(c['explanation_ja'])}字)")
