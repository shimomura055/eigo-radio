# 追加: v2の同一表現(Y Adv at least)と、再現性(同一条件の再生成)確認。DEV/Trial専用。
import sys, os, json, time, threading
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nqt01 as q, nqt02 as n2
T = q.v02a.trial.load_targets(); client = q.v02a.get_client()
jobs = [("y_surname_adv", "NEW2FIXAT", "at least"), ("y_surname_adv", "NEW2FIXAT_r2", "at least"), ("y_surname_adv", "NEW2FIXAT_r3", "at least"),
        ("y_surname_std", "NEW2FIX_r2", "at least a little"), ("y_surname_std", "NEW2FIX_r3", "at least a little")]
res = {}
def w(cell, cond, fx):
    inputs = q.build_inputs_for(cell, T); t0 = time.time()
    d = q.er.run_candidate(inputs, call_fn=q.make_fn(client, f"{cell}_{cond}", override_prompt=n2.build_new2(inputs, fx)), judge_fn=q.make_fn(client, f"{cell}_{cond}j", max_out=5000))
    d["trial_extra_issues"] = q.check_new_extras(d, inputs); d["wall_sec"] = round(time.time() - t0, 2); q._save(cell, cond, d); res[f"{cell}_{cond}"] = d["status"]
ths = [threading.Thread(target=w, args=j) for j in jobs]
[t.start() for t in ths]; [t.join() for t in ths]
print(res, "spent", round(q.spent(), 3))
