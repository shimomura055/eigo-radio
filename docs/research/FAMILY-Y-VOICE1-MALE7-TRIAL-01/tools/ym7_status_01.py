import json,os,sys
p=json.load(open("docs/research/FAMILY-Y-VOICE1-MALE7-TRIAL-01/plan_%s.json"%(sys.argv[1] if len(sys.argv)>1 else "phase1")))["items"]
for b in (1,2,3):
    its=[i for i in p if i["batch"]==b]; st=[]
    for i in its:
        d=f"er121_output/family_y_voice1_male7_trial_01/{i['level']}/body{i['body']}_{i['voice']}/take{i['take']}"
        st.append("D" if os.path.exists(d+"/result.json") else ("R" if os.path.isdir(d+"/narration") else "."))
    print(b,"".join(st))
