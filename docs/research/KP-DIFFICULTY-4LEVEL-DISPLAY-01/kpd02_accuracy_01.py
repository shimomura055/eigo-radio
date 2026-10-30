# -*- coding: utf-8 -*-
"""KP-DIFFICULTY-4LEVEL-DISPLAY-01 委任_02 精度検証(Cap 5円固定)。docは書き換えない(別出力のみ)。
usage: py kpd02_accuracy_01.py dump | run | compare
  dump   : 既存runのkp_candidates.jsonから対象6セットを抽出(API 0)。Sonnet実読用に表を出力。
  run    : gpt-6-luna(本番と同じer119_kp_difficulty_01.grade)と gemini-3.8-flash(別系列, 同じPrompt/schema)で判定。
  compare: Sonnet実読ラベル(kpd02_sonnet_labels.json)と3者比較。
"""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
MAIN = r'C:\Users\tensh\eigo-radio'
OUT = os.path.join(HERE, 'kpd02_out'); os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, ROOT)
CAP_JPY = 5.0
USD_JPY = 160.0
PRICE = {"gpt-6-luna": (0.10, 0.01, 0.50), "gemini-3.8-flash": (0.75, 0.075, 3.75)}   # $/1M (in, cached, out) 出典: docs/pm/dev_eval_model_inventory_01.md
SETS = [  # (family, level, path)
    ('X', 'a2', MAIN + r'\er019_output\family_x_audio_production_wiring_01\ai_island_temple__run_kp75_ev_01\a2\key_phrases\kp_candidates.json'),
    ('X', 'b1b', MAIN + r'\er019_output\family_x_audio_production_wiring_01\ai_island_temple__run_kp75_ev_01\b1b\key_phrases\kp_candidates.json'),
    ('Y', 'a2', MAIN + r'\er121_output\family_y_production_01\redelivery_fee\run_kp75_ev_01\key_phrases\a2\kp_candidates.json'),
    ('Y', 'b1b', MAIN + r'\er121_output\family_y_production_01\redelivery_fee\run_kp75_ev_01\key_phrases\b1b\kp_candidates.json'),
    ('Z', 'a2', MAIN + r'\er026_output\family_z_production_e2e_01\melos\run_kp75_ev_01\key_phrases\a2\kp_candidates.json'),
    ('Z', 'b1b', MAIN + r'\er026_output\family_z_production_e2e_01\melos\run_kp75_ev_01\key_phrases\b1b\kp_candidates.json'),
]
USER_EXAMPLES = [  # ユーザー表示例の確認用(実記事の文脈に近い例文を付ける。判定Promptには含まれない)
    {"candidate_id": "ux_rely", "selection_phrase": "rely on", "used_form": "rely on", "japanese_gloss": "〜に頼る", "source_sentence": "Many people rely on public transport to get to work.", "kind": "phrase"},
    {"candidate_id": "ux_room", "selection_phrase": "make room for", "used_form": "make room for", "japanese_gloss": "〜のために場所・余地を空ける", "source_sentence": "We need to move the table to make room for the new sofa.", "kind": "phrase"},
    {"candidate_id": "ux_narrow", "selection_phrase": "narrow down", "used_form": "narrow down", "japanese_gloss": "(候補などを)絞り込む", "source_sentence": "The committee tried to narrow down the list to three finalists.", "kind": "phrase"},
]


def load_sets():
    out = []
    for fam, lv, p in SETS:
        d = json.load(open(p, encoding='utf-8'))
        out.append({'family': fam, 'level': lv, 'path': p, 'cands': d['candidates'], 'doc_level': d.get('level')})
    return out


def cost_of(model, tin, tout, cached=0):
    p = PRICE[model]
    return (((tin - cached) * p[0] + cached * p[1] + tout * p[2]) / 1e6) * USD_JPY


def ledger_total():
    f = os.path.join(OUT, 'kpd02_cost_ledger.jsonl')
    return sum(json.loads(l).get('cost_jpy', 0.0) for l in open(f, encoding='utf-8') if l.strip()) if os.path.exists(f) else 0.0


def ledger(rec):
    with open(os.path.join(OUT, 'kpd02_cost_ledger.jsonl'), 'a', encoding='utf-8') as f:
        f.write(json.dumps(rec, ensure_ascii=False) + '\n')


def dump():
    rows = []
    for s in load_sets():
        for c in s['cands']:
            rows.append({'set': f"{s['family']}-{s['level']}", 'candidate_id': c['candidate_id'], 'expr': c.get('used_form') or c.get('selection_phrase'),
                         'kind': c.get('kind') or 'phrase', 'gloss': c.get('japanese_gloss'), 'example': c.get('source_sentence')})
    json.dump(rows, open(os.path.join(OUT, 'kpd02_candidates_blind.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for r in rows:
        print(f"{r['set']}\t{r['candidate_id']}\t{r['expr']}\t{r['kind']}\t{r['gloss']}\t| {r['example']}")
    print('N', len(rows))


def gemini_grade(msg, dg, tag):
    from dotenv import load_dotenv
    load_dotenv(MAIN + r'\.env')
    from google import genai
    from google.genai import types
    def strip(s):
        if isinstance(s, dict):
            return {k: strip(v) for k, v in s.items() if k != 'additionalProperties'}
        if isinstance(s, list):
            return [strip(x) for x in s]
        return s
    if ledger_total() > CAP_JPY * 0.8:
        raise SystemExit('Cap接近のため停止')
    client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])
    cfg = types.GenerateContentConfig(response_mime_type='application/json', response_schema=strip(dg.JSON_SCHEMA['schema']), thinking_config=types.ThinkingConfig(thinking_budget=0))
    r = client.models.generate_content(model='gemini-3.8-flash', contents=msg, config=cfg)
    um = r.usage_metadata
    tin, tout = um.prompt_token_count or 0, (um.candidates_token_count or 0) + (getattr(um, 'thoughts_token_count', 0) or 0)
    ledger({'tag': tag, 'model': 'gemini-3.8-flash', 'in': tin, 'out': tout, 'cost_jpy': round(cost_of('gemini-3.8-flash', tin, tout), 5), 'ts': time.strftime('%Y-%m-%dT%H:%M:%S')})
    return r.text


def run():
    from dotenv import load_dotenv
    load_dotenv(MAIN + r'\.env')
    import er005_cost_logger as cl
    cl.install(os.path.join(OUT, 'kpd02_cost_logger_raw.jsonl'))    # 本番と同じ経路のcost logger(OpenAI/Gemini patch)
    import er119_kp_difficulty_01 as dg
    res = {'luna': {}, 'gemini': {}, 'meta': {}}
    jobs = [(f"{s['family']}-{s['level']}", s['cands'], s['level']) for s in load_sets()] + [('UX-a2', USER_EXAMPLES, 'a2'), ('UX-b1b', USER_EXAMPLES, 'b1b')]
    for name, cands, level in jobs:
        if ledger_total() > CAP_JPY * 0.8:
            print('Cap接近のため停止', ledger_total()); break
        g = dg.grade(cands, level)   # 本番と同じgrade()(process=None -> routing.SUPPORT_MODEL=gpt-6-luna)
        rec = g['record']
        res['luna'][name] = {cid: {'level': v['level'], 'reason_ja': v['reason_ja'], 'source': v['source']} for cid, v in g['by_id'].items()}
        res['meta'][name] = {'luna_record': rec}
        raw = open(os.path.join(OUT, 'kpd02_cost_logger_raw.jsonl'), encoding='utf-8').read().splitlines()
        last = json.loads(raw[-1]) if raw else {}
        ledger({'tag': 'luna:' + name, 'model': rec.get('model_id'), 'in': last.get('input_tokens'), 'out': last.get('output_tokens'), 'cached': last.get('cached_input_tokens'), 'cost_jpy': round(cost_of('gpt-6-luna', last.get('input_tokens') or 0, last.get('output_tokens') or 0, last.get('cached_input_tokens') or 0), 5), 'response_id': rec.get('response_id'), 'ts': time.strftime('%Y-%m-%dT%H:%M:%S')})
        try:
            raw_g = gemini_grade(dg.build_message(cands, level), dg, 'gemini:' + name)
            p = dg.parse_response(raw_g, {c['candidate_id'] for c in cands})
            res['gemini'][name] = {k: v for k, v in p.items()}
        except Exception as e:   # noqa
            res['gemini'][name] = {'error': f'{type(e).__name__}: {e}'}
        print(name, rec['status'], rec['model_id'], 'luna n_graded', rec['n_graded'], '/', rec['n_candidates'], 'gemini n', len(res['gemini'][name]))
        json.dump(res, open(os.path.join(OUT, 'kpd02_llm_results.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('prompt_sha256', dg.PROMPT_SHA256)


if __name__ == '__main__':
    {'dump': dump, 'run': run}[sys.argv[1]]()
