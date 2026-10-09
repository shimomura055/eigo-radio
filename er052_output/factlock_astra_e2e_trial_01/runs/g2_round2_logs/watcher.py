import json,os,glob,time,sys
R="er052_output/factlock_astra_e2e_trial_01/runs"
T0=time.strftime("%Y-%m-%dT%H:%M:%S")
while True:
    raw=0;chk=None;
    for p in glob.glob(f"{R}/ledger_costs_worker*.jsonl"):
        for l in open(p,encoding="utf-8"):
            try:e=json.loads(l)
            except:continue
            if e["kind"]=="settle":
                raw+=e["jpy_raw"]
                if "_check_" in e["stage"] and e["jpy_raw"]>20: chk=e
    nf=0
    for p in glob.glob(f"{R}/*/*/state.jsonl"):
        for l in open(p,encoding="utf-8"):
            try:e=json.loads(l)
            except:continue
            if e.get("ev")=="stage_failed" and e["ts"]>=T0: nf+=1
    reason=None
    if raw>=800: reason=f"raw累計{raw:.2f}>=800"
    if chk: reason=f"Checker run raw>20: {chk}"
    if nf>3: reason=f"stage_failed増分{nf}>3"
    if reason and not os.path.exists(f"{R}/STOP.json"):
        json.dump({"reason":"watcher: "+reason,"ts":time.strftime("%Y-%m-%dT%H:%M:%S")},open(f"{R}/STOP.json","w",encoding="utf-8"),ensure_ascii=False)
    open(f"{R}/g2_round2_logs/watcher_last.txt","w").write(f"{time.strftime('%H:%M:%S')} raw={raw:.2f} failed={nf}\n")
    time.sleep(20)
