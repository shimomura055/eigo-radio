import json, random, re, sys
sys.stdout.reconfigure(encoding="utf-8")
B = "er052_output/factlock_writer_trial_01/step1_chat_repro_01"
obs = json.load(open(f"{B}/observations.json", encoding="utf-8"))
ids = list(obs); random.Random(20261008).shuffle(ids)
path = lambda i: "er052_output/all6_writer_redesign_necessity_01/runs/meta/control/b2__all6__r1/ja_writer/revision2.md" if i=="orig_r2" else (f"{B}/chatgpt_logout.txt" if i=="chatgpt_logout" else f"{B}/runs/{i}.md")
mp = {f"記事{n}": i for n, i in enumerate(ids, 1)}
import os; os.makedirs(f"{B}/_private", exist_ok=True)
json.dump(mp, open(f"{B}/_private/MAP.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
out = ["# BLIND_PACK(Step1)\n\n同じニュース(メタ「ミューズ」AI電話)の記事12本。ラベルのみ・順序はシャッフル済み。条件名・モデル名は伏せてあります。\n(注: 先頭の「# 」記号のみ除去。ChatGPT版を含む一部にはタイトル行がない場合があります。)\n"]
for k, i in mp.items():
    t = open(path(i), encoding="utf-8").read().strip()
    t = re.sub(r"^#+\s*", "", t)
    out.append(f"\n---\n\n## {k}\n\n{t}\n")
open(f"{B}/BLIND_PACK.md","w",encoding="utf-8").write("".join(out))
inv = {v:k for k,v in mp.items()}
rows = ["# SUMMARY_STEP1(MAP開封済み、Fable用)\n\n| 記事 | 条件 | 字数 | 段落 | 1文段落 | 問い | ダッシュ | ではない型 | です・ます率 | 記号Gate | FC | 費用¥ | 秒 |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
for i, r in obs.items():
    st = r["fc_status"].replace("LEDGER_","")
    n = {"MAJOR":0,"MINOR":0}
    for d in r["fc_issues"]: n[d["severity"]] = n.get(d["severity"],0)+1
    rows.append(f"| {inv[i]} | {i} | {r['chars']} | {r['paras']} | {r['one_sent_paras']} | {r['questions']} | {r['dash']} | {r['dewa']} | {r['polite']} | {r['sym']} | {st} M{n['MAJOR']}/m{n['MINOR']} | {r['cost'] if r['cost'] is not None else '-'} | {r['sec'] if r['sec'] is not None else '-'} |")
rows.append("\n(F2_astra/F3_astra の費用は単価未登録のため gpt-6-sol単価x2.5の推定概算。chatgpt_logoutはタイトル行なしのため仮タイトルを補って指標算出。ダッシュは「――」と「——」の合計。)")
rows.append("\nFC詳細:")
for i, r in obs.items():
    for d in r["fc_issues"]: rows.append(f"- {i} [{d['severity']}] 「{d['claim_in_article']}」: {d['issue']}")
open(f"{B}/SUMMARY_STEP1.md","w",encoding="utf-8").write("\n".join(rows)+"\n")
print("\n".join(rows[:20]))
