import json, os, sys, re, random, glob
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, "er052_output/factlock_writer_trial_01/step1_chat_repro_01/../r3_minimal_01")
import run_r3_minimal as m
sys.path.insert(0, "er052_output/factlock_writer_trial_01/sweep_01/tools")
import style_metrics as sm
import er003_audio_tts_asr_safety as safety
B = "er052_output/factlock_writer_trial_01/step1_chat_repro_01"
R2 = "er052_output/all6_writer_redesign_necessity_01/runs/meta/control/b2__all6__r1/ja_writer/revision2.md"
ids = ["F0_luna","F0_sol","F1_luna","F1_sol","F2_luna","F2_sol","F3_luna","F3_sol","F2_astra","F3_astra","chatgpt_logout","orig_r2"]
path = lambda i: R2 if i=="orig_r2" else (f"{B}/chatgpt_logout.txt" if i=="chatgpt_logout" else f"{B}/runs/{i}.md")
rows = {}
for i in ids:
    t = m.read(path(i)).strip()
    has_title = i != "chatgpt_logout"   # ChatGPT版はタイトル無し
    lines = t.split("\n")
    body_t = t if has_title else "T\n\n" + t
    s = sm.metrics(body_t)
    body = "\n".join(body_t.split("\n")[1:])
    paras = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
    one = sum(1 for p in paras if len(sm.split_sentences(p.replace("\n",""))) == 1)
    fc = json.load(open(f"{B}/fc/{i}.json", encoding="utf-8"))["parsed"]
    iss = fc.get("issues") or fc.get("deviations") or []
    syms = [str(x) for x in safety.detect_prohibited_symbols(t, language="ja")]
    meta = {}
    if os.path.exists(f"{B}/runs/{i}_meta.json"): meta = json.load(open(f"{B}/runs/{i}_meta.json", encoding="utf-8"))
    rows[i] = {"chars": s["chars"], "paras": len(paras), "one_sent_paras": one, "questions": s["questions"],
               "dash": body.count("――")+body.count("——")+body.count("―")*0, "dewa": s["negation_dewa_arimasen"], "polite": s["polite_ratio"],
               "sym": len(syms), "sym_list": syms, "fc_status": fc.get("overall_status"), "fc_keys": list(fc.keys()),
               "fc_issues": iss, "cost": meta.get("cost_jpy"), "sec": meta.get("sec"), "first_line": lines[0][:40]}
json.dump(rows, open(f"{B}/observations.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
for i,r in rows.items(): print(i, {k:v for k,v in r.items() if k not in ("fc_issues","sym_list","fc_keys")}, "issues", len(r["fc_issues"]))
print(rows["chatgpt_logout"]["fc_keys"])
