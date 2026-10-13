# Round2 Step A: P5の逐語・token・sha・P0/P3比較・差分表を prompts_r2.json に出力(¥0)
import difflib, json, os, re, sys
sys.path.insert(0, os.getcwd())
import er064_kp_int_01_prompts as PR
OUT = "er064_output/kp_integrated_opt_01/round2"
r1 = json.load(open("er064_output/kp_integrated_opt_01/round1/prompts_r1.json", encoding="utf-8"))
res = {"purpose": "Round2 Prompt P5(P3土台の全面書き直し)。P0=Production逐語、P3=Round1(再利用比較用)", "line_a_verbatim": PR.LINE_A, "prompts": {}}
for pid in ("P0", "P3", "P5"):
    e = {}
    for lv in ("std", "adv"):
        h, t = PR.head(pid, lv), PR.tail(pid)
        e[lv] = {"head": h, "tail": t, "tokens_text_only": PR.tokens(h) + PR.tokens(t), "head_sha256": PR.sha(h), "tail_sha256": PR.sha(t),
                 "line_a_verbatim_in_head": PR.LINE_A in h}
    res["prompts"][pid] = e
for lv in ("std", "adv"):
    assert res["prompts"]["P3"][lv]["head_sha256"] == r1["prompts"]["P3"][lv]["head_sha256"], "P3 head sha drift"
    assert res["prompts"]["P0"][lv]["head_sha256"] == r1["prompts"]["P0"][lv]["head_sha256"]
res["round1_sha_match_P0_P3"] = True
t0, t3, t5 = (res["prompts"][p]["std"]["tokens_text_only"] for p in ("P0", "P3", "P5"))
res["token_compare_std"] = {"P0": t0, "P3": t3, "P5": t5, "P5_vs_P0_pct": round((t5 / t0 - 1) * 100, 1), "P5_vs_P3_pct": round((t5 / t3 - 1) * 100, 1)}
a0, a3, a5 = (res["prompts"][p]["adv"]["tokens_text_only"] for p in ("P0", "P3", "P5"))
res["token_compare_adv"] = {"P0": a0, "P3": a3, "P5": a5, "P5_vs_P0_pct": round((a5 / a0 - 1) * 100, 1), "P5_vs_P3_pct": round((a5 / a3 - 1) * 100, 1)}
# 段落単位の差分(P3 -> P5, std)
def paras(s): return [p for p in re.split(r"\n\s*\n", s.strip()) if p.strip()]
p3 = paras(res["prompts"]["P3"]["std"]["head"] + res["prompts"]["P3"]["std"]["tail"])
p5 = paras(res["prompts"]["P5"]["std"]["head"] + res["prompts"]["P5"]["std"]["tail"])
diff = []
for l in difflib.unified_diff(p3, p5, lineterm="", n=0):
    diff.append(l)
res["diff_P3_to_P5_paragraphs_std"] = diff
json.dump(res, open(f"{OUT}/prompts_r2.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({k: res[k] for k in ("token_compare_std", "token_compare_adv")}, ensure_ascii=False))
print("sha P5 std head", res["prompts"]["P5"]["std"]["head_sha256"][:16], "tail", res["prompts"]["P5"]["std"]["tail_sha256"][:16])
