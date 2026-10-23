# ukus_exposure_01.py -- 台本中のUK専用綴り語の露出度(API 0)。Family別・記事別に「英米異綴りで一方に偏る語」を数える。
import sys, os, re, glob, json, collections
sys.path.insert(0, "."); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ukus_lexicon_01 as lex
UK2US, US2UK, AMB = lex.build_pair_index()
W = re.compile(r"[A-Za-z]+")
out = {}
def scan(globs, label, min_words=300):
    arts = []
    for g in globs:
        for f in glob.glob(g, recursive=True):
            if ".venv" in f: continue
            try: t = open(f, encoding="utf-8").read()
            except Exception: continue
            ws = [w.lower() for w in W.findall(t)]
            if len(ws) < min_words: continue
            uk = [w for w in ws if w in UK2US and w not in US2UK]   # UK専用形
            us = [w for w in ws if w in US2UK and w not in UK2US]   # US専用形(参考)
            arts.append((f, len(ws), len(uk), len(us), collections.Counter(uk)))
    n = len(arts)
    with_uk = [a for a in arts if a[2] > 0]
    out[label] = {"n_files": n, "files_with_ukonly_word": len(with_uk), "total_ukonly_tokens": sum(a[2] for a in arts),
                  "top_ukonly_words": collections.Counter(w for a in arts for w, c in a[4].items() for _ in range(c)).most_common(25),
                  "sample_files": [(a[0].replace("\\", "/"), a[1], a[2], dict(a[4])) for a in with_uk[:12]]}
scan(["er026_output/family_z_production_e2e_01/*/*/writer/*.md", "er026_output/family_z_production_e2e_01/*/*/*/audit/*.md"], "Z_writer_md")
scan(["er026_output/**/seed/**/*.md", "docs/research/FAMILY-Z-*/**/*.md"], "Z_seed_and_docs", 500)
scan(["er019_output/**/*.md", "er012_output/**/article.md", "er012_output/**/*.md"], "X_and_misc_md", 300)
json.dump(out, open("docs/research/ASR-QUALITY-2ITEMS-COMPREHENSIVE-01/UKUS/work/ukus_exposure_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for k, v in out.items(): print(k, v["n_files"], v["files_with_ukonly_word"], v["total_ukonly_tokens"], v["top_ukonly_words"][:12])
