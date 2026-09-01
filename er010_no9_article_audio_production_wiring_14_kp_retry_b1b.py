# B1B Key Phrase selection failed this run (KEY_WORDS_STRUCTURE_INVALID,
# "source_spanがsource_sentence内に存在しない") which skipped canonicalization
# entirely, leaving keywords_canonicalized.json stale from the 2026-08-29
# baseline. This re-invokes the exact same official run_key_phrases()
# function once more (no prompt/code changes) to see if a fresh attempt
# passes structural validation.
import er003_v1_n3_01_scaffold_generate as sc

out_dir = "er006_output/pool_pilot_01/pool_n9_tip_screens/b1b"
with open(f"{out_dir}/article.md", encoding="utf-8") as f:
    article_text = f.read()

kp = sc.run_key_phrases(article_text, f"{out_dir}/key_phrases",
                         "ER006_pool_n9_tip_screens_b1b", "B1-B(N3-01, direct generation)",
                         process="B1_SUPPORT")
sel_status = kp["selection"]["status"]
canon_status = (kp["canonicalization"] or {}).get("status")
print(f"RETRY_RESULT selection_status={sel_status} canonicalization_status={canon_status}", flush=True)
