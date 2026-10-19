# 委任_10: OPEN-283 what-if(完全offline、API 0)。減速後ASR転写を「書換え前canonical」と「書換え後の実送信文」で
# 既存classify_asr_match(Primary判定のみ)にかけた場合の分類差。コード変更なし・判定の適用ではなく診断のみ。
import sys, os, json
sys.path.insert(0, os.getcwd())
import er006_preprod_hardening_01_validation as val
canon = ("He remembered the hands held out for the chains. His friend trusted him without asking for another promise. Water came slowly through a crack in the rock. Melos drank, got onto his knees, and stood up. He managed one step, then took another. At the city gates, the bell rang for his friend's death. He raced to the square, where the sword was already raised above his friend.")
rewritten = canon.replace("Melos drank", "He drank")
post_slow_asr = ("He remembered the hands held out for the chains. His friend trusted him, without asking for another promise. Water came slowly through a crack in the rock. He drank, got onto his knees, and stood up. He managed one step, then took another. At the city gates, the bell rang for his friend's death. He raced to the square where the sword was already raised above his friend.")
out = {}
for k, c in (("vs_pre_rewrite_canonical(現行配線)", canon), ("vs_rewritten_text(OPEN-283案)", rewritten)):
    r = val.classify_asr_match(c, post_slow_asr)
    out[k] = {"classification": r.classification, "should_pass": r.should_pass}
print(json.dumps(out, ensure_ascii=False, indent=1))
json.dump(out, open("docs/research/FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01/lr_slowdown_whatif_part3c1_10_result.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
