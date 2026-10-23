# 原因究明probe-02(慣用句の逐語度): 現行gloss Prompt・現行model・本番builderのまま、生成済みKP(慣用句を含む)の日本語意味を各3回再生成し、
# 本番値との一致・揺れを見る。DEV専用・Production不触・Prompt無改変。
import json, os, sys
sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.chdir(ROOT); sys.path.insert(0, ROOT)
import er019_family_x_kp_explanation_01 as kx
import er003_key_words_gloss_alignment as ga
import er009_n1_routing_governance_10_actual_model_cost as pricing
import er003_v1_b1_scaffold_01_generate as b1s
client = b1s.get_client(); MODEL = kx.MODEL
W = "er019_output/family_x_audio_production_wiring_01/"
CASES = [("uk_train_speaker_playback__run_nws_02", "b1b", [2]),
         ("prix_pascal_ai_novel_prize__run_nws_01", "b1b", [3]),
         ("tesla_spacex_merger_talks__run_nws_01", "b1b", [1, 3]),
         ("small_bag__run_jre_01", "a2", [2, 3])]
N = int(sys.argv[1]) if len(sys.argv) > 1 else 3
OUT = "docs/research/FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01/kp_probe_02_result.json"
cost = 0.0; res = []
for run, lv, ranks in CASES:
    base = W + run + "/" + lv + "/key_phrases/"
    article = open(base + "gloss_alignment_prompt.txt", encoding="utf-8").read().split("【記事本文(参考)】\n", 1)[1]
    items = json.load(open(base + "keywords_canonicalized.json", encoding="utf-8"))["items"]
    tg = []
    for it in items:
        if it["rank"] in ranks:
            tg.append({"rank": it["rank"], "key_phrase": it["key_phrase"], "display_phrase": it["display_phrase"], "japanese_gloss": None,
                       "source_sentence": it["source_sentence"], "fulltext_source_ref": "fulltext_exact_v1", "_prod": it["japanese_gloss"]})
    for i in range(N):
        msg = ga.build_user_message_corrected([{k: v for k, v in t.items() if k != "_prod"} for t in tg], article)
        r = client.responses.create(model=MODEL, reasoning={"effort": "high"},
            text={"format": {"type": "json_schema", **ga.GLOSS_ALIGNMENT_JSON_SCHEMA}},
            input=[{"role": "developer", "content": ga.DEVELOPER_MESSAGE}, {"role": "user", "content": msg}])
        u = kx._usage_dict(r.usage)
        cost += pricing.cost_jpy_for_call("openai", r.model, u.get("input_tokens"), u.get("cached_input_tokens"), u.get("output_tokens"))
        out = {x["rank"]: x["japanese_gloss"] for x in json.loads(r.output_text)["items"]}
        for t in tg:
            res.append(dict(run=run, level=lv, key_phrase=t["key_phrase"], prod=t["_prod"], regen=out.get(t["rank"]), rep=i + 1))
json.dump(dict(model=MODEL, total_cost_jpy=round(cost, 4), rows=res), open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("cost", round(cost, 4))
for x in res: print(x["key_phrase"], "| prod:", x["prod"], "| regen:", x["regen"])
