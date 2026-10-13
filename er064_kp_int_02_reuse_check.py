# Round1 runの再利用可否: 現在のPrompt/shortlist構築が Round1 job_result の msg_sha256/rows_sha256 と一致するかを確認(¥0)
import glob, hashlib, json, os, sys
sys.path.insert(0, os.getcwd())
import er064_kp_int_01_run as RUN
OUT = "er064_output/kp_integrated_opt_01/round2"
R1 = "er064_output/kp_integrated_opt_01/round1"
rep = {"shortlists_r1_sha256_file": open(f"{R1}/shortlists_r1.sha256.txt").read().strip(),
       "shortlists_r1_sha256_actual": hashlib.sha256(open(f"{R1}/shortlists_r1.json", "rb").read()).hexdigest(), "combos": {}}
ok = True
for art in ("coffee", "meta", "hormuz"):
    ctx = RUN.build_ctx(art, ["M2P0", "M2P3"])
    for (a, lv, cn), c in ctx.items():
        fs = sorted(glob.glob(f"{R1}/runs/{a}_{lv}_{cn}_run*/job_result.json"))
        shas = {(json.load(open(f, encoding="utf-8"))["msg_sha256"], json.load(open(f, encoding="utf-8"))["rows_sha256"]) for f in fs}
        m = shas == {(c["prompt_sha256"], c["rows_sha256"])} and len(fs) > 0
        ok &= m
        rep["combos"][f"{a}_{lv}_{cn}"] = {"n_runs_round1": len(fs), "prompt_sha256_match": m, "msg_sha256": c["prompt_sha256"][:16], "rows_sha256": c["rows_sha256"][:16]}
rep["all_match"] = ok
json.dump(rep, open(f"{OUT}/reuse_check_r2.json", "w", encoding="utf-8"), indent=1)
print("all_match", ok, rep["shortlists_r1_sha256_file"][:16], rep["shortlists_r1_sha256_actual"][:16])
for k, v in rep["combos"].items(): print(k, v["n_runs_round1"], v["prompt_sha256_match"])
