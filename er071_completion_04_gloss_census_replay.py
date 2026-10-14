# -*- coding: utf-8 -*-
"""委任_04: 記録済みの『KPが候補より伸びたitem』(全records)へgloss再整合を適用(実API少額、記事ごとに1呼出)。
Before/After(gloss)と、既に整合しているitemを不必要に書き換えないか(over-rewrite)を確認する。"""
import glob, json, sys, collections
sys.stdout.reconfigure(encoding="utf-8")
import er003_key_words_gloss_alignment as ga
import er006_model_routing_contract_01 as routing

model = routing.require_model("A2_SUPPORT", routing.SUPPORT_MODEL)
seen = {}
for p in glob.glob("er*_output/**/keywords_canonicalized.json", recursive=True):
    try: d = json.load(open(p, encoding="utf-8"))
    except Exception: continue
    if not isinstance(d, dict): continue
    for it in d.get("items", []):
        if not it.get("key_phrase") or not it.get("display_phrase"): continue
        if ga.select_alignment_targets([it]):
            seen.setdefault((it["display_phrase"], it["key_phrase"], it.get("japanese_gloss")), (p, it))
print("unique targets", len(seen))
items = []
for i, (k, (p, it)) in enumerate(sorted(seen.items(), key=lambda kv: str(kv[0])), 1):
    x = dict(it); x["rank"] = i; items.append(x)
merged = {"items": items, "overall_status": "PASS"}
res = ga.align_glosses(merged, "(記事本文は省略。source_sentenceを参照)", lambda msg: ga.make_alignment_fn(msg, model=model))
rows = []
for before, after in zip(items, res["merged"]["items"]):
    st = (after.get("gloss_alignment") or {}).get("status")
    rows.append({"display_phrase": before["display_phrase"], "key_phrase": before["key_phrase"], "gloss_before": before.get("japanese_gloss"),
                 "gloss_after": after.get("japanese_gloss"), "status": st, "source_sentence": before.get("source_sentence")})
    print(f"{before['display_phrase']!r} -> {before['key_phrase']!r} | {before.get('japanese_gloss')} => {after.get('japanese_gloss')} [{st}]")
print("status", res["status"], "attempts", len(res["attempts"]))
json.dump({"status": res["status"], "model": res.get("model_id"), "rows": rows}, open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
