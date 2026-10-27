# -*- coding: utf-8 -*-
"""KCP委任_03 evidence用(コピーdirのみ・API 0): 旧run(review無し)のZ a2に確定を後から入れると kp_a2 の来歴input_sha(=sha(text) → sha(text|署名))が変わる。
確定がkp stage前に入っていた状況の再現として、コピーの来歴entryのinput_shaだけを現在値へ付け替える(出力shaは触らない)。"""
import argparse, json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
sys.path.insert(0, ROOT)
import er026_family_z_fiction_production_runner_01 as zr  # noqa: E402
import er062_family_z_writer_01 as w62  # noqa: E402
import er119_kp_human_review_01 as rv  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--run", required=True)
ap.add_argument("--level", default="a2")
a = ap.parse_args()
run = a.run.replace("\\", "/").rstrip("/")
pj = f"{run}/writer/provenance.json"
prov = json.load(open(pj, encoding="utf-8"))
text = zr.canonical_article_text(w62.rd(w62.level_text_path(run, a.level)))
sig = rv.load_review(f"{run}/key_phrases/{a.level}")["selection_signature"]
new = w62.sha(f"{text}|{sig}") if hasattr(w62, "sha") else None
e = prov["downstream_stages"][f"kp_{a.level}"]
out = {"old": e["input_sha256"], "new": new, "changed": e["input_sha256"] != new}
e["input_sha256"] = new
json.dump(prov, open(pj, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(json.dumps(out, ensure_ascii=False))
