# DEV診断(委任_02): 既存Production関数(er120.extract_candidates)を無変更で呼び、LLM生応答を保存する。runの成果物は書き換えない。
import json, os, sys
ROOT = r"C:\Users\tensh\eigo-radio"
sys.path.insert(0, ROOT); os.chdir(ROOT)
import er120_part2_grammar_production_01 as g
import er026_family_z_fiction_production_runner_01 as zr
import er003_v1_b1_scaffold_01_generate as b1s
OUT = os.path.join(ROOT, "docs", "research", "FZ-TELL-TALE-HEART-RESELECT-REMAKE-01", "grammar_zero_probe_02")
RUN = os.path.join(ROOT, "er026_output", "family_z_production_e2e_01", "the_tell_tale_heart", "run_reselect_01", "writer")
level, f, n = sys.argv[1], sys.argv[2], sys.argv[3]
text = open(os.path.join(RUN, f), encoding="utf-8").read()
paras = zr.canonical_article_text(text).split("\n\n")
client = b1s.get_client()
base = g._default_call_fn_factory(client, g.MODEL, g.MAXOUT_EXTRACT)
raws = []
def cf(prompt):
    r = base(prompt); raws.append(r[0]); return r
doc = g.extract_candidates(paras, "The Tell-Tale Heart", level=level, call_fn=cf)
json.dump({"level": level, "text_sha256": doc["text_sha256"], "raw_response": raws, "n_candidates": len(doc["candidates"]),
           "tier_table": doc["tier_table"], "no_feature_paras": doc["no_feature_paras"], "audit": doc["audit"]},
          open(os.path.join(OUT, f"probe_{level}_{n}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(level, n, "cands", len(doc["candidates"]), "tier_table", len(doc["tier_table"]), "cost", doc["audit"]["total_cost_jpy"], "rawlen", len(raws[0]))
