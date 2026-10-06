import json
ids="G-01 G-02 G-03 F-09 F-10 F-19 G-04 G-05 G-06 S-06".split()
L=["","## D. repeat別内訳(選択subject / ledger_state / article_state / compare)","","| id | label | rep | selected_subject | ledger_state | article_state | compare |","|---|---|---|---|---|---|---|"]
for l in open('run/results_merged.jsonl',encoding='utf-8'):
    r=json.loads(l)
    if r['id'] in ids:
        for x in r['repeats']:
            L.append(f"| {r['id']} | {r['label']} | {x['rep']} | {x['selected_subject']} | {x['ledger_state']} | {x['article_state']} | {x['compare']} |")
L+=["","注: S-06は事象リスト外(outside_event_list)の人工反転。前回検出→今回見逃し=新重大見逃し候補(判断はFable)。"]
open('trial_summary_02.md','a',encoding='utf-8').write("\n".join(L)+"\n")
