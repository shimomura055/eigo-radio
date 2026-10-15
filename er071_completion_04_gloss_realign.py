# -*- coding: utf-8 -*-
"""委任_04: 記録済みKP canonicalization結果(keywords_canonicalized.json)へ、Productionの
gloss再整合工程(er003_key_words_gloss_alignment.align_glosses、scaffoldと同じfactory/routing)を適用する。
KP選定/canonicalizationは再実行しない(1レベル1回の再生成上限・非決定性の回避)。旧recordは退避する。
usage: python er071_completion_04_gloss_realign.py <kp_dir> <article.md> <process: A2_SUPPORT|B1_SUPPORT> <article_id>"""
# KGCPW 委任_02 (OF-KGCPW-13): 撤去済みlegacy方式に依存する過去証跡script。冒頭で停止する(有料APIを叩く前に落とす)。
raise SystemExit("HISTORICAL: 過去証跡(KP-GLOSS-ALIGNMENT Trial/census/replay)の再現用scriptです。KGCPW(2026-10-15)でlegacy方式(slot/fallback/mode)を撤去し修正版が唯一の方式になったため再実行不能・実行すると有料APIを叩く前に停止します(OF-KGCPW-13)。")
import json, os, shutil, sys
import er003_key_words_gloss_alignment as ga
import er006_model_routing_contract_01 as routing

kp_dir, article_path, process, article_id = sys.argv[1:5]
rec_path = f"{kp_dir}/keywords_canonicalized.json"
bak = f"{kp_dir}/keywords_canonicalized_before_gloss_align_04.json"
if os.path.exists(bak):
    raise SystemExit(f"[STOP] 既に適用済み({bak})。再実行しない。")
merged = json.load(open(rec_path, encoding="utf-8"))
article_text = open(article_path, encoding="utf-8").read()
model = routing.require_model(process, routing.SUPPORT_MODEL)
res = ga.align_glosses(merged, article_text, lambda msg: ga.make_alignment_fn(msg, model=model),
                       out_dir=kp_dir, article_id=article_id)
print("status:", res["status"], "targets:", res["targets"], "model:", res.get("model_id"))
if res["status"] == "NO_TARGETS":
    raise SystemExit(0)
shutil.copyfile(rec_path, bak)
json.dump(res["merged"], open(rec_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
for it in res["merged"]["items"]:
    print(it["rank"], it["key_phrase"], "|", it["japanese_gloss"], "|", it["japanese_gloss_tts"], "|", (it.get("gloss_alignment") or {}).get("status"))
