# -*- coding: utf-8 -*-
"""委任_04: Production関数 sc.run_key_phrase_canonicalization(gloss再整合の配線先)を実LLMで1回実行(in-line経路のruntime evidence)。
入力=Coffee Std記録済みの選定結果(before-gloss-align backupから復元)。出力はrun dirとは別の証跡dirのみ(run dirは変更しない)。"""
import json, os, sys
sys.stdout.reconfigure(encoding="utf-8")
import er003_v1_n3_01_scaffold_generate as sc
RUN = "er019_output/family_x_audio_production_wiring_01/coffee_prices__run_m2p0_n01_01/a2"
OUT = "er071_output/m2p0_n01_production_wiring_01/completion_04/inline_runtime_04"
os.makedirs(OUT, exist_ok=True)
rec = json.load(open(f"{RUN}/key_phrases/keywords_canonicalized_before_gloss_align_04.json", encoding="utf-8"))
originals = []
for it in rec["items"]:
    o = {k: it[k] for k in ("rank", "source_span", "source_sentence", "display_phrase", "source_reference_contract", "source_candidate_id", "key_phrase_role") if k in it}
    o["ja_gloss"] = it["japanese_gloss"]
    originals.append(o)
article = open("er019_output/coffee_prices/run_v5_ms_01/a2/article.md", encoding="utf-8").read()
res = sc.run_key_phrase_canonicalization(article, originals, OUT, "COFFEE_STD_INLINE_RUNTIME_04", process="A2_SUPPORT")
print("canonicalization status:", res["status"], "| gloss_alignment_status:", res.get("gloss_alignment_status"))
for it in (res.get("merged") or {}).get("items", []):
    print(it["rank"], it["key_phrase"], "|", it["japanese_gloss"], "|", it["japanese_gloss_tts"], "|", (it.get("gloss_alignment") or {}).get("status"), "| extends:", it.get("kp_extends_beyond_candidate"))
