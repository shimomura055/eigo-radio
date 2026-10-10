# -*- coding: utf-8 -*-
"""Phase1(API非呼び出し): 9記事の入力固定確認。article/ledger sha を FIX02 manifest と照合、Fact件数==見出し数 assert、文数を記録。"""
import json, os, re, sys, hashlib
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "er052_output", "writer_dev_risk_flagger_01", "detectors"))
import ledger_restore_01 as LR, run_flagger_01 as R
HDR = re.compile(r"^\[(?P<st>[A-Z_]+)(?:\s+-\s+[^\]]*)?\]\s+(?P<id>[^\s:]+):\s*(?P<text>.*)$"); LR._HDR = HDR
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
man = json.load(open(os.path.join(REPO, "er052_output/writer_r0_model_impact_trial_01/fix02/manifest_fix02.json"), encoding="utf-8"))
out = {}
for th in ["streaming_price", "space_weapons", "byd_recall"]:
    for m in ["gpt-6-luna", "gpt-6.1-sol", "gpt-6-astra"]:
        e = man["cells"]["%s/%s" % (th, m)]
        art, lp = os.path.join(REPO, e["article_path"]), os.path.join(REPO, e["ledger_path"])
        assert sha(art) == e["article_sha256"] and sha(lp) == e["ledger_sha256"]
        f = LR.parse_ledger_file(lp); nh = sum(1 for l in open(lp, encoding="utf-8").read().splitlines() if HDR.match(l))
        assert len(f) == nh == e["n_headings"]
        out["%s/%s" % (th, m)] = dict(article_path=e["article_path"], article_sha256=e["article_sha256"], ledger_sha256=e["ledger_sha256"], n_facts=len(f), n_headings=nh,
                                       n_sentences=len(R._split_sentences(open(art, encoding="utf-8").read())))
json.dump(out, open(os.path.join(HERE, "inputs_manifest_antenna.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for k, v in out.items(): print(k, v["n_facts"], v["n_sentences"], v["article_sha256"][:12], v["ledger_sha256"][:12])
