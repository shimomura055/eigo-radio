# -*- coding: utf-8 -*-
"""未使用記事の『現行Production方式』Before再現: 現行P7(select_p7)+canonicalization(sc.run_key_phrase_canonicalization)をread-onlyで呼ぶ。
Production file無変更。telemetry書込はこのprocess内でno-opに差替え。Gate連鎖(CMU/QA等)・gloss整合の後段・補完は省略(=簡易再現。結果に明記)。"""
import json, os, sys, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, ROOT)
os.chdir(ROOT)
import er003_v1_n3_01_scaffold_generate as sc
sc._log_kp_backend_telemetry = lambda *a, **k: None
import er119_kp_candidates_01 as kc19
import er105_kp_fulltext_selector_01 as ft
corpus = {c["id"]: c for c in json.load(open(os.path.join(HERE, "kpg01_work", "corpus.json"), encoding="utf-8"))}
def replica(cid):
    c = corpus[cid]
    work = os.path.join(HERE, "kpg01_work", "before_replica", cid)
    os.makedirs(work, exist_ok=True)
    proc = "A2_SUPPORT" if c["level"] == "a2" else "B1_SUPPORT"
    res = kc19.select_p7(c["text"], work, "kpg01_" + cid, c["level"], process=proc)
    out = {"select_status": res.get("status"), "items": []}
    items = res.get("original_items") or []
    if items:
        canon = sc.run_key_phrase_canonicalization(c["text"], items, work, "kpg01_" + cid, process=proc, rescue=False)
        out["canon_status"] = canon.get("status")
        if canon.get("merged"):
            for it in canon["merged"]["items"]:
                out["items"].append({"selection_phrase": it.get("source_span") or it.get("display_phrase"), "used_form": it.get("used_form") or it.get("key_phrase"),
                                     "gloss": it.get("japanese_gloss"), "origin": "call1", "kind": "phrase", "sentence": it.get("source_sentence")})
    json.dump(out, open(os.path.join(work, "before_replica.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return out
if __name__ == "__main__":
    for cid in sys.argv[1:]:
        r = replica(cid)
        print(cid, r.get("select_status"), r.get("canon_status"))
        for i in r["items"]: print("  ", i["selection_phrase"], "->", i["used_form"], "|", i["gloss"])
