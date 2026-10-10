import json, os, re, sys, hashlib
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, ".."); E2E = os.path.join(OUT, "..", "factlock_astra_e2e_trial_01")
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
HDR = re.compile(r"^\[(?P<st>[A-Z_]+)(?:\s+-\s+[^\]]*)?\]\s+(?P<id>[^\s:]+):\s*(?P<text>.*)$")
cells = {}
for t in ["streaming_price", "space_weapons", "byd_recall"]:
    lp = os.path.join(E2E, "runs", t, "new", "research_ledger", "verified_fact_ledger.txt")
    nh = sum(1 for l in open(lp, encoding="utf-8").read().splitlines() if HDR.match(l))
    for s in ["prev_r0", "gpt-6-luna", "gpt-6.1-sol", "gpt-6-astra"]:
        a = os.path.join(E2E, "runs", t, "new", "new_writer", "r0.md") if s == "prev_r0" else os.path.join(OUT, "r0", t, s + ".md")
        gen = {"prev_r0": "gpt-6-luna (FACTLOCK-ASTRA-E2E-TRIAL-01 new腕 r0_meta.json、Fact Lock付き、Fact Check前の生成物)"}.get(s, s + " (WRITER-R0-MODEL-IMPACT-TRIAL-01 今回生成)")
        cells["%s/%s" % (t, s)] = dict(article_path=os.path.relpath(a, os.path.join(HERE, "..", "..", "..")).replace("\\", "/"), article_sha256=sha(a), stage="R0(生成直後)", generator=gen,
                                       ledger_path=os.path.relpath(lp, os.path.join(HERE, "..", "..", "..")).replace("\\", "/"), ledger_sha256=sha(lp), n_headings=nh)
json.dump(dict(cells=cells), open(os.path.join(HERE, "manifest_fix02.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
for k, v in cells.items(): print(k, v["article_sha256"][:12], v["ledger_sha256"][:12], v["n_headings"])
