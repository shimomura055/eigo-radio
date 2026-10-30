# -*- coding: utf-8 -*-
"""usage: py kpd03_run_01.py luna1|luna2|gemini1|gemini2 [set名...]  held-out評価(Cap 6円固定)。"""
import json, os, sys, time, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kpd03_common_01 as k
mode = sys.argv[1]; only = set(sys.argv[2:])
from dotenv import load_dotenv; load_dotenv(k.MAIN + r'\.env')
import er005_cost_logger as cl; cl.install(os.path.join(k.OUT, f'kpd03_{mode}_cost_logger_raw.jsonl'))
import er119_kp_difficulty_01 as dg
if mode.endswith('2'):
    dg.PROMPT_TEXT = k.v2_text(dg.PROMPT_TEXT)
sha = hashlib.sha256(dg.PROMPT_TEXT.encode('utf-8')).hexdigest()
res = {}
rf = os.path.join(k.OUT, f'kpd03_{mode}_results.json')
if os.path.exists(rf): res = json.load(open(rf, encoding='utf-8'))['results']

def gemini_call(msg, tag):
    from google import genai
    from google.genai import types
    def strip(s):
        if isinstance(s, dict): return {a: strip(b) for a, b in s.items() if a != 'additionalProperties'}
        if isinstance(s, list): return [strip(x) for x in s]
        return s
    client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])
    cfg = types.GenerateContentConfig(response_mime_type='application/json', response_schema=strip(dg.JSON_SCHEMA['schema']), thinking_config=types.ThinkingConfig(thinking_budget=0))
    r = client.models.generate_content(model='gemini-3.8-flash', contents=msg, config=cfg)
    um = r.usage_metadata
    tin, tout = um.prompt_token_count or 0, (um.candidates_token_count or 0) + (getattr(um, 'thoughts_token_count', 0) or 0)
    k.ledger({'tag': tag, 'model': 'gemini-3.8-flash', 'in': tin, 'out': tout, 'cost_jpy': round(k.cost_of('gemini-3.8-flash', tin, tout), 5), 'ts': time.strftime('%Y-%m-%dT%H:%M:%S')})
    return r.text

for name, cands, level in k.jobs():
    if only and name not in only: continue
    if name in res: continue
    if k.ledger_total() > k.CAP_JPY * 0.85:
        print('Cap接近 停止', k.ledger_total()); break
    if mode.startswith('luna'):
        g = dg.grade(cands, level)
        res[name] = {cid: {'level': v['level'], 'reason_ja': v['reason_ja'], 'source': v['source']} for cid, v in g['by_id'].items()}
        rec = g['record']
        raw = open(os.path.join(k.OUT, f'kpd03_{mode}_cost_logger_raw.jsonl'), encoding='utf-8').read().splitlines()
        last = json.loads(raw[-1]) if raw else {}
        k.ledger({'tag': f'{mode}:{name}', 'model': rec.get('model_id'), 'in': last.get('input_tokens'), 'out': last.get('output_tokens'), 'cached': last.get('cached_input_tokens'),
                  'cost_jpy': round(k.cost_of('gpt-6-luna', last.get('input_tokens') or 0, last.get('output_tokens') or 0, last.get('cached_input_tokens') or 0), 5), 'response_id': rec.get('response_id'), 'status': rec['status'], 'ts': time.strftime('%Y-%m-%dT%H:%M:%S')})
        print(name, rec['status'], rec['model_id'], rec['n_graded'], '/', rec['n_candidates'])
    else:
        p = dg.parse_response(gemini_call(dg.build_message(cands, level), f'{mode}:{name}'), {c['candidate_id'] for c in cands})
        res[name] = p
        print(name, len(p), '/', len(cands))
    json.dump({'prompt_sha256': sha, 'mode': mode, 'results': res}, open(rf, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('sha', sha, 'ledger_total', round(k.ledger_total(), 4))
