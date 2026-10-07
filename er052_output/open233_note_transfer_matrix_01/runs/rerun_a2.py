import os,subprocess,sys,threading,json
sys.path.insert(0,"er052_output/open233_note_transfer_matrix_01/tools")
import driver
res={}
def go(slug,cond,rep):
    env=dict(os.environ,OPEN233_RUNS_ROOT=driver.RUNS,OPEN233_B3_VARIANT="nb",PYTHONUTF8="1",PYTHONIOENCODING="utf-8")
    for ph,bud in (("phase1","8"),("phase2","14")):
        c,out=driver.cmd_for(slug,cond,rep,ph)
        if ph=="phase2": c[c.index("--budget-jpy")+1]=bud
        log=f"{driver.RUNS}/_logs/{slug}_{cond}_rep{rep}_{ph}_a2.log"
        with open(log,"w",encoding="utf-8") as lf: rc=subprocess.call(c,stdout=lf,stderr=subprocess.STDOUT,env=env)
        fin=os.path.exists(f"{out}/ja_writer/revision2.md" if ph=="phase1" else f"{out}/b1b/article.md")
        res[f"{slug}/{cond}/rep{rep}"+"_"+ph]=[rc,fin]
        if rc!=0 or not fin: break
ts=[threading.Thread(target=go,args=a) for a in (("hormuz","T2M0",1),("sewer","T0M1",2))]
[t.start() for t in ts];[t.join() for t in ts]
print(res)
