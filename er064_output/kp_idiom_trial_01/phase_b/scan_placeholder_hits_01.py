# Phase B2: 400本走査(Phase Aと同一の記事集合・同一の重複除去)で、(a)の新規ヒット全件を文脈つきで列挙する。
# Phase A strict版(proto)と、Phase Bの硬化版(er064_kp_idiom_trial_01_matcher)の両方で判定し差分を残す。
import sys, os, glob, json, hashlib, importlib.util
sys.path.insert(0, os.getcwd())
import er030_key_phrase_db_hybrid_core_01 as core
import er064_kp_idiom_trial_01_matcher as M
spec = importlib.util.spec_from_file_location("proto", "er064_output/kp_idiom_trial_01/phase_a/proto_placeholder_match_02_strict.py")
proto = importlib.util.module_from_spec(spec); spec.loader.exec_module(proto)
dbs = core.load_group1_dbs()
ppats = proto.build_index(dbs); hpats = M.build_pattern_index(dbs)
print("proto patterns", len(ppats), "hardened patterns", len(hpats))
allf = sorted(glob.glob("er0*_output/**/article.md", recursive=True))
files, seen = [], set()
for f in allf:
    try: t = open(f, encoding="utf8").read()
    except Exception: continue
    h = hashlib.sha256(t.encode("utf8")).hexdigest()
    if h in seen or len(t.split()) < 150: continue
    seen.add(h); files.append(f)
rows = []
for f in files[:400]:
    text = open(f, encoding="utf8").read()
    units = core.build_sentence_units(text)
    pk, hk = {}, {}
    for u in units:
        for h in proto.match_sentence(u["tokens"], ppats):
            if not proto.baseline_hit(h["surface"], dbs):
                pk.setdefault((h["surface"].lower(), h["title"]), u["raw_text"])
        for h in M.match_sentence_tokens(u["tokens"], hpats):
            if not M.baseline_hit(h["surface"], dbs):
                hk.setdefault((h["surface"].lower(), h["title"]), u["raw_text"])
    for (s, t), sent in pk.items():
        rows.append({"file": f, "surface": s, "title": t, "sentence": sent, "in_hardened": (s, t) in hk})
    for (s, t), sent in hk.items():
        if (s, t) not in pk:
            rows.append({"file": f, "surface": s, "title": t, "sentence": sent, "in_hardened": True, "only_hardened": True})
json.dump({"files_scanned": len(files[:400]), "rows": rows}, open("er064_output/kp_idiom_trial_01/phase_b/scan_placeholder_hits_01.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
print(len(rows), sum(r["in_hardened"] for r in rows))
for i, r in enumerate(rows): print(i, r["surface"], "<=", r["title"], "| H" if r["in_hardened"] else "| --", "|", r["sentence"][:140], "|", r["file"].split("/")[0])
