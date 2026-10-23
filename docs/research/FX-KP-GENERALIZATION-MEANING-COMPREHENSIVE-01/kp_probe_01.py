# FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_01 原因究明probe(仮説->反証)。
# 目的: 『key_phraseが一般化形(draw a line)なら、既存Prompt/既存model(gpt-6-luna)のままでStd日本語意味/Adv英語説明が改善するか』を
#   実測し、一般化の過不足と意味生成の寄与を切り分ける。既存Promptは無改変(送信文は本番builderの出力そのまま)。DEV専用・Production不触。
import json, os, sys, copy, re
sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.chdir(ROOT); sys.path.insert(0, ROOT)
import er019_family_x_kp_explanation_01 as kx
import er003_key_words_gloss_alignment as ga
import er009_n1_routing_governance_10_actual_model_cost as pricing
import er003_v1_b1_scaffold_01_generate as b1s
D = "er019_output/family_x_audio_production_wiring_01/uk_train_speaker_playback__run_nws_02/"
OUT = "docs/research/FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01/kp_probe_01_result.json"
client = b1s.get_client()
MODEL = kx.MODEL
article = open(D + "a2/key_phrases/gloss_alignment_prompt.txt", encoding="utf-8").read().split("【記事本文(参考)】\n", 1)[1]
b1b = json.load(open(D + "b1b/key_phrases/keywords_canonicalized.json", encoding="utf-8"))["items"]
cost_total = 0.0
log = []
def run_explanation(items, tag):
    global cost_total
    msg = kx.build_explanation_user_message(items)
    resp = client.responses.create(model=MODEL, reasoning={"effort": kx.REASONING_EFFORT},
        text={"format": {"type": "json_schema", **kx._build_explanation_json_schema(len(items))}},
        input=[{"role": "developer", "content": kx.DEVELOPER_MESSAGE}, {"role": "user", "content": msg}])
    u = kx._usage_dict(resp.usage)
    c = pricing.cost_jpy_for_call("openai", resp.model, u.get("input_tokens"), u.get("cached_input_tokens"), u.get("output_tokens"))
    cost_total += c
    rows = json.loads(resp.output_text)["explanations"]
    log.append(dict(kind="explanation", tag=tag, model=resp.model, cost=c, out=rows))
    return rows
def run_gloss(targets, tag):
    global cost_total
    msg = ga.build_user_message_corrected(targets, article)
    resp = client.responses.create(model=MODEL, reasoning={"effort": "high"},
        text={"format": {"type": "json_schema", **ga.GLOSS_ALIGNMENT_JSON_SCHEMA}},
        input=[{"role": "developer", "content": ga.DEVELOPER_MESSAGE}, {"role": "user", "content": msg}])
    u = kx._usage_dict(resp.usage)
    c = pricing.cost_jpy_for_call("openai", resp.model, u.get("input_tokens"), u.get("cached_input_tokens"), u.get("output_tokens"))
    cost_total += c
    rows = json.loads(resp.output_text)["items"]
    log.append(dict(kind="gloss", tag=tag, model=resp.model, cost=c, out=[(r["rank"], r["japanese_gloss"], r["reasoning"]) for r in rows]))
    return rows
def exp_items(kp3_phrase, kp3_gloss):
    its = []
    for it in b1b:
        p = it["used_form"]; g = it["japanese_gloss"]
        if it["rank"] == 3: p, g = kp3_phrase, kp3_gloss
        its.append({"rank": it["rank"], "display_phrase": p, "source_sentence": it["source_sentence"], "japanese_gloss": g})
    return its
N = int(sys.argv[1]) if len(sys.argv) > 1 else 3
for i in range(N):
    run_explanation(exp_items("draw that line", "その境界線を引く"), f"P1_explanation_as_produced_{i+1}")
for i in range(N):
    run_explanation(exp_items("draw a line", "境界線を引く"), f"P2_explanation_kp_draw_a_line_{i+1}")
def gl_target(kp):
    return [{"rank": 1, "key_phrase": kp, "display_phrase": "draw that line", "japanese_gloss": None,
             "source_sentence": "The words draw that line simply", "fulltext_source_ref": "fulltext_exact_v1"}]
for i in range(N):
    run_gloss(gl_target("draw that line"), f"P3_gloss_as_produced_{i+1}")
for i in range(N):
    run_gloss(gl_target("draw a line"), f"P4_gloss_kp_draw_a_line_{i+1}")
json.dump(dict(model=MODEL, total_cost_jpy=round(cost_total, 4), calls=len(log), log=log), open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("cost_total_jpy", round(cost_total, 4), "calls", len(log))
for l in log:
    if l["kind"] == "explanation":
        print(l["tag"], "|", [r["english_explanation"] for r in l["out"] if "line" in r["phrase"]])
    else:
        print(l["tag"], "|", l["out"][0][1], "|", l["out"][0][2][:100])
