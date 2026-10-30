# -*- coding: utf-8 -*-
"""独立判定(別系列: gemini-3.8-flash、非thinking、出力上限付き)。D'の候補(main/alt)を1 caseにつき1 callで判定。"""
import json, os, sys, glob
import kpg02_llm as L
import kpg01_judge as J1
HERE = os.path.dirname(os.path.abspath(__file__))
JD = os.path.join(HERE, "kpg02_work", "judge"); os.makedirs(JD, exist_ok=True)
corpus = {c["id"]: c for c in json.load(open(os.path.join(HERE, "kpg01_work", "corpus.json"), encoding="utf-8"))}
SCHEMA = {"name": "kp_judge", "schema": {"type": "object", "additionalProperties": False, "required": ["judgements"], "properties": {
    "judgements": {"type": "array", "items": {"type": "object", "additionalProperties": False, "required": ["id", "cls", "selectable", "code"],
        "properties": {"id": {"type": "integer"}, "cls": {"type": "string", "enum": ["W", "F", "C"]}, "selectable": {"type": "boolean"},
                       "code": {"type": "string", "enum": ["OK", "NOT_GENERALIZED", "OVER_GENERALIZED", "FREE_COMBINATION", "WORD_ONLY", "GLOSS_MISMATCH", "MEANING_CHANGED", "UNNATURAL", "TOO_EASY", "OTHER"]}}}}}}}
RUBRIC = J1.RUBRIC.split("## 出力")[0] + "\n## 出力\n各候補についてid・cls・selectable・codeのみを返す(説明文は書かない)。不合格のときcodeは最も主要な理由1つ、合格はOK。"

def judge_case(cid, method="D2_luna"):
    r = json.load(open(os.path.join(HERE, "kpg02_work", "results", f"{cid}__{method}.json"), encoding="utf-8"))
    rows = [("main", i) for i in r["items"]] + [("alt", i) for i in r.get("alt_items", [])]
    lines = [f"{n}. 表示形: {i['display_form']} / 意味: {i['gloss_ja']} / 本文の語句: {i['source_span']} / 本文の文: {i['source_sentence']}" for n, (t, i) in enumerate(rows, 1)]
    o, m = L.call("gemini-3.8-flash", RUBRIC + "\n\n【候補】\n" + "\n".join(lines), SCHEMA, tag=f"judge2:{cid}", think_budget=0, max_out=1500)
    jm = {x["id"]: x for x in o["judgements"]}
    out = {"case": cid, "method": method, "cost": m["cost_jpy"], "rows": [dict(track=t, display_form=i["display_form"], span=i["source_span"], j=jm.get(n)) for n, (t, i) in enumerate(rows, 1)]}
    json.dump(out, open(os.path.join(JD, f"{cid}__{method}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return out

if __name__ == "__main__":
    method = sys.argv[1]
    for cid in sys.argv[2:]:
        o = judge_case(cid, method)
        print(cid, "¥", o["cost"], "; ".join(f"{r['track']}:{r['display_form']}[{(r['j'] or {}).get('code')}]" for r in o["rows"]), flush=True)
