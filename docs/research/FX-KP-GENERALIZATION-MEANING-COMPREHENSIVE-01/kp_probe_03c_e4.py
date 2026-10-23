# probe-03c: E4 = 説明call内sense-first(JA gloss不使用・1文のみ。usage_type→core_sense→explanation をその1 callで決める)。独立した『第2の目』を保ちつつgloss連想を遮断する構造の切り分け。
import sys, json, re, concurrent.futures as cf
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\tensh\eigo-radio\docs\research\FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01")
import kp_probe_03 as P
P.CAP = 14.8
P.client = P.b1s.get_client()
kps, miss = P.load_kps()
SCHEMA = {"name": "kp_expl_e4", "strict": True, "schema": {"type": "object", "properties": {"explanations": {"type": "array", "items": {
    "type": "object", "properties": {"phrase": {"type": "string"}, "usage_type": {"type": "string", "enum": ["literal", "figurative", "phrasal", "term"]},
    "core_sense": {"type": "string"}, "english_explanation": {"type": "string"}},
    "required": ["phrase", "usage_type", "core_sense", "english_explanation"], "additionalProperties": False}}}, "required": ["explanations"], "additionalProperties": False}}
RULE = ("- First decide how the phrase is used in the source sentence (usage_type: literal / figurative / phrasal / term), then state its core sense in core_sense "
        "(general, no story-specific details), then write english_explanation from that core sense.\n")
def job(args):
    key, rep = args
    kp = kps[key]
    if P.total() >= P.CAP: return (key, rep, "SKIP")
    msg = P.kx.build_explanation_user_message([{"display_phrase": kp["key"], "source_sentence": kp["sent"], "japanese_gloss": "x"}])
    msg = re.sub(r"   japanese_reference_meaning[^\n]*\n", "", msg)
    msg = msg.replace("\nKey Phrases:\n", RULE + "\nKey Phrases:\n", 1)
    r = P.client.responses.create(model=P.MODEL, reasoning={"effort": P.kx.REASONING_EFFORT}, text={"format": {"type": "json_schema", **SCHEMA}},
        input=[{"role": "developer", "content": P.kx.DEVELOPER_MESSAGE}, {"role": "user", "content": msg}])
    c, u = P.cost_of(r)
    P.log_cost(dict(kind="expl_e4", key=key, rep=rep, usage=u, cost_jpy=round(c, 5)))
    x = json.loads(r.output_text)["explanations"][0]
    P.save(dict(arm="E4", key=key, rep=rep, kind="E", sent=kp["sent"], gloss_in=None, sense_in=None, text=x["english_explanation"], usage_type=x["usage_type"], core_sense=x["core_sense"]))
    return (key, rep, x["usage_type"], x["english_explanation"])
with cf.ThreadPoolExecutor(6) as ex:
    for r in ex.map(job, [(k, i) for k in kps for i in (1, 2)]): print(r)
print("cum", round(P.total(), 3))
