# ukus_asr_behavior_01.py -- 保存転写で、canonicalにUK専用綴りがあるとき ASR(Primary/Azure)がUK形を保つ/US形へ変える割合(API 0)。
import sys, os, re, glob, json, collections
sys.path.insert(0, "."); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import er109_stored_census_01 as census
import ukus_lexicon_01 as lex
UK2US, US2UK, AMB = lex.build_pair_index(max_level=70, with_breame=False)
W = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")
cnt = collections.Counter(); ex = collections.defaultdict(collections.Counter)
seen = set()
for f in sorted(g for g in glob.glob("**/*tts_generation_results*.json", recursive=True) if not g.startswith(".venv")):
    for r in census.rows_from_results(f):
        for kind, a in (("openai", r["asr"]), ("azure", r.get("azure"))):
            if not a: continue
            k = (r["canonical"], a, kind)
            if k in seen: continue
            seen.add(k)
            cw = [w.lower() for w in W.findall(r["canonical"])]; aw = {w.lower() for w in W.findall(a)}
            for w in cw:
                if w in UK2US and w not in US2UK and not any((w, u) in AMB for u in UK2US[w]):
                    if w in aw: cnt[(kind, "kept_UK")] += 1; ex[kind]["kept:" + w] += 1
                    elif UK2US[w] & aw: cnt[(kind, "changed_to_US")] += 1; ex[kind]["to_US:" + w] += 1
                    else: cnt[(kind, "other(欠落/別語)")] += 1
print(dict(cnt))
for k, v in ex.items(): print(k, v.most_common(25))
json.dump({"counts": {f"{a}|{b}": v for (a, b), v in cnt.items()}, "examples": {k: dict(v.most_common(40)) for k, v in ex.items()}},
          open("docs/research/ASR-QUALITY-2ITEMS-COMPREHENSIVE-01/UKUS/work/ukus_asr_behavior_01.json", "w"), indent=1)
