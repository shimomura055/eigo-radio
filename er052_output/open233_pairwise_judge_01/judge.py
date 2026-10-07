# -*- coding: utf-8 -*-
"""T4 1文x1factの狭い対判定(有料API、Trial専用)。使い方: judge.py --cond A|B --set dev|heldout --reps N [--effort medium] [--probe]
A=gpt-6-luna(現行判定モデル)、B=gpt-6-sol。出力: er052_output/open233_pairwise_judge_01/out/<set>/<cond>_rep<k>.json(1件ずつ追記・再開可)。
費用: out/cost_log.jsonl(全call)。合計>=27円でSTOP。"""
import os, sys, json, time, argparse, pathlib
os.environ["PYTHONUTF8"] = "1"
ROOT = pathlib.Path(__file__).resolve().parents[2]; os.chdir(ROOT); sys.path.insert(0, str(ROOT))
OUT = ROOT / 'er052_output/open233_pairwise_judge_01'
MODELS = {"A": "gpt-6-luna", "B": "gpt-6-sol"}
PRICE = {"gpt-6-luna": (0.10, 0.01, 0.50), "gpt-6-sol": (2.00, 0.20, 10.00)}  # USD/1M(in, cached, out)、DECISION_LOG 2026-09-29確認値
USD_JPY = 156.88
STOP_JPY = 27.0
DEV_MSG = """You are a narrow consistency checker. You get ONE English sentence from a news-explainer article and ONE verified fact entry (the fact may be written in Japanese or English, and may include notes). Judge ONLY this sentence against ONLY this fact entry. Use no outside knowledge. Another fact in the article may support other parts of the sentence, but your job is to say what this sentence claims beyond or against THIS entry.

Verdicts:
- contradicts: the sentence conflicts with the entry on subject (who/what), polarity (affirmed vs negated), number/date/amount, scope (all/some, only/also), direction/meaning of an action, or cause/time relation.
- asserts_unstated: the sentence asserts something the entry does not state: a new actor, a cause/reason, a universal or general claim, or that something exists / does not exist / has or has not happened, when the entry only says it was not reported, not shown, unknown, or says nothing about it. Turning "not stated/not shown/unclear" into a definite statement counts here.
- consistent: everything the sentence claims on this topic is stated by the entry (a faithful paraphrase is fine; harmless connective or framing words are fine).
- unclear: you cannot tell.
Give a one-line reason."""
SCHEMA = {"name": "pairwise_verdict", "schema": {"type": "object", "properties": {
    "verdict": {"type": "string", "enum": ["contradicts", "asserts_unstated", "consistent", "unclear"]},
    "reason": {"type": "string"}}, "required": ["verdict", "reason"], "additionalProperties": False}, "strict": True}

def user_msg(sentence, fact):
    return f"SENTENCE:\n{sentence}\n\nFACT ENTRY:\n{fact}\n\nReturn the verdict."

def cost_of(model, usage):
    pi, pc, po = PRICE[model]
    it, ct, ot = usage.get("input_tokens") or 0, (usage.get("input_tokens_details") or {}).get("cached_tokens") or 0, usage.get("output_tokens") or 0
    return ((max(it - ct, 0) * pi + ct * pc + ot * po) / 1e6) * USD_JPY

def total_cost():
    f = OUT / 'out/cost_log.jsonl'
    return sum(json.loads(l)['cost_jpy'] for l in open(f, encoding='utf-8')) if f.exists() else 0.0

def call(client, model, effort, sentence, fact):
    last = None
    for _ in range(3):
        try:
            r = client.responses.create(model=model, reasoning={"effort": effort}, text={"format": {"type": "json_schema", **SCHEMA}},
                                        input=[{"role": "developer", "content": DEV_MSG}, {"role": "user", "content": user_msg(sentence, fact)}])
            u = r.usage
            usage = {"input_tokens": u.input_tokens, "output_tokens": u.output_tokens,
                     "input_tokens_details": {"cached_tokens": getattr(u.input_tokens_details, 'cached_tokens', 0) or 0},
                     "reasoning_tokens": getattr(getattr(u, 'output_tokens_details', None), 'reasoning_tokens', None)}
            j = json.loads(r.output_text)
            return j, usage, getattr(r, 'model', model), None
        except Exception as e:
            last = f"{type(e).__name__}: {e}"; time.sleep(1)
    return None, {}, model, last

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cond', required=True); ap.add_argument('--set', default='dev'); ap.add_argument('--reps', type=int, default=3)
    ap.add_argument('--effort', default='medium'); ap.add_argument('--probe', action='store_true'); ap.add_argument('--rep_from', type=int, default=1); ap.add_argument('--ids_file', default=None)
    a = ap.parse_args()
    from dotenv import load_dotenv; load_dotenv()
    from openai import OpenAI
    client = OpenAI(); model = MODELS[a.cond]
    (OUT / 'out').mkdir(exist_ok=True)
    if a.probe:
        d = json.load(open(OUT / 'items_dev.json', encoding='utf-8'))['items']
        it = [i for i in d if i['group'] == 'control'][0]
        for s in ("The component was public for about an hour.", "Nobody has ever downloaded the component."):
            j, usage, m, err = call(client, model, a.effort, s, it['fact'])
            c = cost_of(model, usage) if usage else 0
            print(m, j, usage, round(c, 4), err)
            with open(OUT / 'out/cost_log.jsonl', 'a', encoding='utf-8') as f:
                f.write(json.dumps({"kind": "probe", "cond": a.cond, "model": model, "cost_jpy": round(c, 5), "usage": usage}) + "\n")
        return
    items = json.load(open(OUT / f'items_{a.set}.json', encoding='utf-8'))['items']
    if a.ids_file:
        keep = set(json.load(open(a.ids_file, encoding='utf-8'))); items = [i for i in items if i['id'] in keep]
    od = OUT / 'out' / a.set; od.mkdir(parents=True, exist_ok=True)
    for rep in range(a.rep_from, a.reps + 1):
        fp = od / f'{a.cond}_rep{rep}.json'
        res = json.load(open(fp, encoding='utf-8')) if fp.exists() else {"cond": a.cond, "model": model, "effort": a.effort, "rep": rep, "results": {}}
        for it in items:
            if it['id'] in res['results']: continue
            if total_cost() >= STOP_JPY:
                print('STOP cost', total_cost(), flush=True); json.dump(res, open(fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1); return
            j, usage, m, err = call(client, model, a.effort, it['sentence'], it['fact'])
            c = cost_of(model, usage) if usage else 0.0
            res['results'][it['id']] = {"verdict": (j or {}).get('verdict'), "reason": (j or {}).get('reason'), "error": err, "cost_jpy": round(c, 5),
                                        "usage": usage, "model_returned": m}
            with open(OUT / 'out/cost_log.jsonl', 'a', encoding='utf-8') as f:
                f.write(json.dumps({"kind": "run", "set": a.set, "cond": a.cond, "rep": rep, "id": it['id'], "cost_jpy": round(c, 5)}) + "\n")
            json.dump(res, open(fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print(a.cond, a.set, 'rep', rep, 'done; total', round(total_cost(), 3), flush=True)

if __name__ == '__main__':
    main()
