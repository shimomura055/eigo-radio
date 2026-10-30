# -*- coding: utf-8 -*-
"""Prompt較正の候補(v2)をgpt-6-lunaのみで評価(オフライン。本番Promptは未変更)。ユーザー表示例・評価対象の表現はPromptに入れない。Cap残のみ使用。"""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.abspath(os.path.join(HERE, '..', '..', '..')))
sys.argv = [sys.argv[0], 'x']
import importlib.util
spec = importlib.util.spec_from_file_location('acc', os.path.join(HERE, 'kpd02_accuracy_01.py')); acc = importlib.util.module_from_spec(spec); spec.loader.exec_module(acc)
from dotenv import load_dotenv; load_dotenv(acc.MAIN + r'\.env')
import er005_cost_logger as cl; cl.install(os.path.join(acc.OUT, 'kpd02_variant_cost_logger_raw.jsonl'))
import er119_kp_difficulty_01 as dg
old = dg.PROMPT_TEXT
new = old.replace("4. 基準の目安(例): easy=look for, weather / medium=come up with, reliable / hard=stave off, disparity / rare=doff, perspicacious。\n",
  "4. 基準の目安(例): easy=look for, weather, pick up / medium=come up with, reliable, hold back / hard=stave off, disparity, bear out / rare=doff, perspicacious。\n")
new = new.replace("5. 迷ったときは極端な段階を避け、より近い段階を選ぶ。全項目に必ず1つの段階を付ける。\n",
  "5. 基準は日本の英語学習者の視点: easyは中学〜高校初級で習う基本語・基本熟語に限る。それ以外の句動詞・イディオム・比喩的/文語的な語・多義で用法に注意が要る語は原則medium以上。全項目に必ず1つの段階を付け、候補全体で段階を使い分ける(全部同じ段階にしない)。\n")
assert new != old and new.count('pick up') == 1 and '使い分ける' in new
dg.PROMPT_TEXT = new
import hashlib; sha = hashlib.sha256(new.encode('utf-8')).hexdigest()
res = {}; tot = 0.0
jobs = [(f"{s['family']}-{s['level']}", s['cands'], s['level']) for s in acc.load_sets()] + [('UX-a2', acc.USER_EXAMPLES, 'a2'), ('UX-b1b', acc.USER_EXAMPLES, 'b1b')]
for name, cands, level in jobs:
    if acc.ledger_total() > acc.CAP_JPY * 0.9: print('Cap接近 停止'); break
    g = dg.grade(cands, level)
    res[name] = {cid: {'level': v['level'], 'reason_ja': v['reason_ja'], 'source': v['source']} for cid, v in g['by_id'].items()}
    last = json.loads(open(os.path.join(acc.OUT, 'kpd02_variant_cost_logger_raw.jsonl'), encoding='utf-8').read().splitlines()[-1])
    acc.ledger({'tag': 'variantV2-luna:' + name, 'model': g['record']['model_id'], 'in': last.get('input_tokens'), 'out': last.get('output_tokens'), 'cached': last.get('cached_input_tokens'), 'cost_jpy': round(acc.cost_of('gpt-6-luna', last.get('input_tokens') or 0, last.get('output_tokens') or 0, last.get('cached_input_tokens') or 0), 5), 'ts': time.strftime('%Y-%m-%dT%H:%M:%S')})
    print(name, g['record']['status'], g['record']['n_graded'])
json.dump({'prompt_sha256_v2': sha, 'prompt_text_v2': new, 'luna_v2': res}, open(os.path.join(acc.OUT, 'kpd02_variant_results.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
