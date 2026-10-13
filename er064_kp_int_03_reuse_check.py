# Round3 再利用可否 ¥0: Round1のM2P0 run / Round2のM2P5 runが、現在の構築(Prompt/rows)とsha一致するか。Stage1未実施でも再利用資産の有効性を確認する。
import glob, json, os, sys
sys.path.insert(0, os.getcwd())
import er064_kp_int_03_run as RUN3
RUN = RUN3.RUN
OUT = "er064_output/kp_integrated_opt_01/round3"
SRC = {"M2P0": "er064_output/kp_integrated_opt_01/round1", "M2P5": "er064_output/kp_integrated_opt_01/round2"}
rep = {"stage1_executed": False, "combos": {}}
ok = True
for art in ("coffee", "meta", "hormuz"):
    ctx = RUN.build_ctx(art, ["M2P0", "M2P5"])
    for (a, lv, cn), c in ctx.items():
        fs = sorted(glob.glob(f"{SRC[cn]}/runs/{a}_{lv}_{cn}_run*/job_result.json"))
        shas = {(json.load(open(f, encoding="utf-8"))["msg_sha256"], json.load(open(f, encoding="utf-8"))["rows_sha256"]) for f in fs}
        m = shas == {(c["prompt_sha256"], c["rows_sha256"])} and len(fs) > 0
        ok &= m
        rep["combos"][f"{a}_{lv}_{cn}"] = {"source": SRC[cn], "n_runs_existing": len(fs), "prompt_sha256_match": m}
rep["all_match"] = ok
json.dump(rep, open(f"{OUT}/reuse_check_r3.json", "w", encoding="utf-8"), indent=1)
print("all_match", ok, {k: (v["n_runs_existing"], v["prompt_sha256_match"]) for k, v in rep["combos"].items()})
