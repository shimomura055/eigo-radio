# 引数: 次に報告する complete 数。STOP条件でlogs/STOPを作る。
import json,glob,os,sys,time,subprocess
B="er052_output/open233_b3_trial_01"; R=B+"/runs"; target=int(sys.argv[1])
def stat():
    done=part=0;tot=0;mx=0
    for f in glob.glob(f"{R}/*/nb/*/b*/w1/cost.json"):
        try: c=json.load(open(f,encoding="utf-8"))["total_jpy"]
        except Exception: continue
        w=os.path.dirname(f)
        if os.path.exists(w+"/writer_run_summary.json") and os.path.exists(w+"/b1b/article.md"): done+=1
        else: part+=1
        tot+=c; mx=max(mx,c)
    return done,part,tot,mx
while True:
    d,p,t,m=stat(); cum=55.49+68.27+t
    log=open(B+"/logs/driver_stage2_A4.log",encoding="utf-8",errors="replace").read()
    alive="python" in subprocess.run("tasklist",capture_output=True,text=True).stdout.lower()
    if "WinError 1455" in log or "MemoryError" in log: print("STOP-COND memory"); open(B+"/logs/STOP","w").close(); break
    if m>15: print("STOP-COND run>15"); open(B+"/logs/STOP","w").close(); break
    if cum>=480: print("STOP-COND cum"); open(B+"/logs/STOP","w").close(); break
    if d>=target or not alive: print(f"complete={d} partial={p} stage2_w1_sum={t:.2f} max={m:.2f} cum_est={cum:.2f} alive={alive}"); break
    time.sleep(30)
