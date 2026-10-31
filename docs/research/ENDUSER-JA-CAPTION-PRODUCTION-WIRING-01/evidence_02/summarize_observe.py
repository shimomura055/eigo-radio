"""observe.json群を集計: 組数・PASS数・NG項目・空欄期待文数・バー高さ検査・error数・build-id・nowLabel省略状態。使い方: summarize_observe.py out.md observe.json..."""
import json, sys, collections
out = sys.argv[1]; R = {}
for p in sys.argv[2:]:
    for k, v in json.load(open(p, encoding="utf-8")).items():
        R[f"{v.get('browser','chromium')}|{k}"] = v
lines = []; ng = []; tot = collections.Counter(); blank = collections.Counter(); bid = collections.Counter(); errs = 0
for k, r in sorted(R.items()):
    bad = [c for c, v in r["checks"].items() if v is not True and not str(v).startswith("N/A")]
    errs += len(r.get("errors", []))
    bid[r.get("build_id")] += 1
    dev = k.split("|")[1].split(":")
    lines.append(f"| {k.split('|')[0]} | {dev[0]} | {dev[1].replace('family_','')} | {dev[2]} | {'PASS' if not bad else 'NG:' + ','.join(bad)} | {r.get('sentences')} | {r.get('with_caption')} | {r.get('expected_blank_sentences')} | {r.get('bar_rows')} | {len(r.get('errors', []))} |")
    if bad: ng.append((k, bad))
    tot[(k.split('|')[0], dev[0])] += 1
hdr = "| browser | view | dir | lv | result | sentences | with_caption | expected_blank | bar_rows | errors |\n|---|---|---|---|---|---|---|---|---|---|\n"
body = hdr + "\n".join(lines)
body += f"\n\n組数={len(R)} PASS={len(R)-len(ng)} NG={len(ng)} console/HTTP error合計={errs} build-id分布={dict(bid)}\n"
body += "NG詳細=" + json.dumps(ng, ensure_ascii=False) + "\n"
nl = []
for k, r in sorted(R.items()):
    for s in r.get("nowlabel_states", []):
        nl.append(f"{k}: {s['state']} text={s['nowLabel']!r} trunc={s['nowLabelTrunc']} w={s['nowLabelW']}")
body += "\n## nowLabel状態(R-8)\n" + "\n".join(nl[:200]) + "\n"
open(out, "w", encoding="utf-8").write(body)
print(f"groups={len(R)} PASS={len(R)-len(ng)} NG={len(ng)} errors={errs} build_id={dict(bid)}")
