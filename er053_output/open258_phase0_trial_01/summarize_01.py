import sys, json, math
sys.path.insert(0, "er053_output/open258_phase0_trial_01")
from open258_phase0_common import *
res = [json.loads(l) for l in open(OUT + "/results_01.jsonl", encoding="utf8")]
W = json.load(open(OUT + "/whisper_aux_01.json", encoding="utf8"))
ev = json.load(open(EVID, encoding="utf8"))["impact_estimate_from_logs"]["groups"]
tot_s = sum(r["duration_s"] for r in res); tot_wall = sum(r["wall_seconds"] for r in res)
print("calls", len(res), "audio_s", round(tot_s, 1), "wall_s", round(tot_wall, 1), "est_yen_exact", round(tot_s * JPY_PER_SEC, 2), "est_yen_ceil", res[-1]["cum_est_cost_jpy"])
print("false pass C:", [r["key"] for r in res if r["role"].startswith("C_") and r["sec_pass"]])
for r in res:
    r["extra_now"] = extra_exclusion(javal.normalize_ja(r["canonical"]), javal.normalize_ja(r["primary_asr"]))
    w = W[r["key"]]
    print(f'{r["key"]:28s} {r["role"][:2]} pass={r["sec_pass"]!s:5} {r["sec_cls"]:22s} extra={r["extra_now"]} wS={w["small"]["agrees_with_canonical"]} wM={w["medium"]["agrees_with_canonical"]}')
# 14群
GROUPS = [2, 7, 8, 11, 17, 20, 21, 23, 24, 26, 27, 31, 33, 36]
dup = {24: 21, 26: 23}
byg = {}
for r in res: byg.setdefault(r["group"], []).append(r)
succ = fail = excl = 0; avoided = 0; extra_block = []
for g in GROUPS:
    gg = dup.get(g, g); rs = byg.get(gg, [])
    ok = [r for r in rs if r["sec_pass"]]
    n = ev[g]["n_attempts"]
    if g == 7: status = "除外(既存ratio<0.4)->救済漏れ(プローブではSecondary PASS)"; excl += 1
    elif ok:
        k = min(r["attempt"] for r in ok); status = f"救済成功(attempt{k}でSecondary PASS)"; succ += 1; avoided += max(n - k, 0)
        if any(r["extra_now"] for r in ok): extra_block.append(g)
    else: status = "救済失敗(Secondary NG)"; fail += 1
    print(g, ev[g]["seg"], "n_attempts", n, status)
print("success", succ, "fail", fail, "excluded", excl, "avoided_regens(n_attempts-k)", avoided, "extra_rule_would_block_success_groups", extra_block)
