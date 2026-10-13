import json,glob
def load(p): return [json.load(open(f,encoding="utf-8")) for f in sorted(glob.glob(p))]
C=load("er064_output/kp_integrated_opt_01/round1/runs/meta_adv_M2P0_run*/job_result.json")
T=load("er064_output/kp_no_way_fix_01/runs/meta_adv_M2P0X_run*/job_result.json")
def usage(r):
    s=r["usage"]["selection"]; return s
print(json.dumps(T[0]["usage"]["selection"],ensure_ascii=False)[:600])
for n,L in (("ctl",C),("trt",T)):
    print(n,[ (r["tag"],r["cost_jpy"],r["elapsed_sec"],r.get("backup_item")) for r in L])
rows=open("er064_output/kp_no_way_fix_01/offline_gate/selector_prompt.txt",encoding="utf-8").read() if False else ""
for r in T: print(r["tag"],"concierge" in json.dumps(r,ensure_ascii=False).lower(), r.get("backup_item"))
