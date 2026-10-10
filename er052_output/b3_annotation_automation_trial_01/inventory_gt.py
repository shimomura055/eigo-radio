# -*- coding: utf-8 -*-
"""B3-ANNOTATION-AUTOMATION-TRIAL-01 Phase1: Ground Truth棚卸(読み取り専用・API無し)。"""
import json, os, re, hashlib, subprocess, sys
R = "er052_output/factlock_astra_e2e_trial_01"
OUT = "er052_output/b3_annotation_automation_trial_01"
THEMES = ["byd_recall","central_bank_mortgage","hormuz","inbound_tourism","meta","openai_copyright","semiconductor_earnings","small_bag","space_weapons","streaming_price"]
V2 = {"hormuz","streaming_price"}
def sha(p):
    return hashlib.sha256(open(p,"rb").read()).hexdigest()
def tags(t):
    return dict(fact=len(re.findall(r"【事実\d+】",t)), core=t.count("【中核数値】"), periph=t.count("【周辺数値】"))
rows=[]
for s in THEMES:
    d = "storyline_b3_v2" if s in V2 else "storyline_b3"
    br = f"{R}/stage_r/{s}/{d}/selected_brief.md"; led=f"{R}/stage_r/{s}/research_ledger/verified_fact_ledger.txt"
    r = dict(theme=s, b3_version="v2" if s in V2 else "v1", brief=br, brief_sha=sha(br), brief_chars=len(open(br,encoding='utf-8').read()),
             ledger=led, ledger_sha=sha(led), ledger_chars=len(open(led,encoding='utf-8').read()))
    fin=f"{R}/annotation/final/{s}/selected_brief_factlock.md"
    if os.path.exists(fin):
        t=open(fin,encoding="utf-8",newline="").read()
        r.update(final=fin, final_sha=sha(fin), final_tags=tags(t), final_sidecar=f"{R}/annotation/final/{s}/annotation.json")
        for N in "AB":
            p=f"{R}/annotation/out/{N}/{s}/annotated.md"
            if os.path.exists(p):
                r[f"{N}_annotated_sha"]=sha(p); r[f"{N}_tags"]=tags(open(p,encoding="utf-8",newline="").read())
            r[f"{N}_reply"]=f"{R}/annotation/out/{N}/{s}/reply.md"
        r["merged_dir"]=f"{R}/annotation/out/merged/{s}"
        for f in ("merged_core_numbers.json","agreement.json","resolution_log.json","merged_annotation.json"):
            p=f"{r['merged_dir']}/{f}"
            if os.path.exists(p): r[f+"_sha"]=sha(p)
        ag=json.load(open(f"{r['merged_dir']}/agreement.json",encoding="utf-8"))
        r["agree"]=dict(split=ag.get("split_agreement_rate"),core_jaccard=ag.get("core_jaccard"),cls=ag.get("classification_agreement_rate"))
        pr=f"{R}/annotation/prompts/{s}__A.md"; r["promptA_chars"]=len(open(pr,encoding="utf-8").read())
        c=subprocess.run([sys.executable,"-X","utf8",f"{R}/b3_annotation_check_01.py","--brief",br,"--annotated",fin,"--ledger",led],capture_output=True,text=True,encoding="utf-8")
        r["baseline_check_exit"]=c.returncode
    else:
        r["final"]=None
    rows.append(r)
json.dump(rows,open(f"{OUT}/gt_inventory.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
for r in rows: print(r["theme"],r["b3_version"],r["brief_chars"],r["ledger_chars"],r.get("final_tags"),r.get("agree"),r.get("baseline_check_exit"),r.get("promptA_chars"))
