# -*- coding: utf-8 -*-
"""KP-DIFFICULTY-4LEVEL-DISPLAY-01 委任_02 配線証跡: 本番の候補生成経路(kcand.make_generate_fn -> rv.ensure_kp_review -> _generate_candidates_impl)
を通し、**難易度判定だけ実LLM(gpt-6-luna, 本番routing B1_SUPPORT/A2_SUPPORT)**、他の段(P7/W5'/canon/gloss/QA)はtest用mock(Env)で実行する。
生成docのdifficulty_grading(model_id・prompt sha・response_id)・cost logger記録・export_form_data出力・フォームJS(difficultyOf)までの一貫性を確認。
費用: 難易度callのみ(a2/b1b 各1 call、約0.1円)。"""
import json, os, subprocess, sys, tempfile, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, 'docs', 'research', 'KP-GATE-DROP-BACKFILL-PRODUCTION-01', 'tools'))
import test_state_isolation_01  # noqa: F401  (HR queue等のProduction監査logへ書かない)
import unittest
from unittest import mock
from dotenv import load_dotenv
load_dotenv(r'C:\Users\tensh\eigo-radio\.env')
OUT = os.path.join(HERE, 'kpd02_out'); os.makedirs(OUT, exist_ok=True)
import er005_cost_logger as cl
RAW = os.path.join(OUT, 'kpd02_wiring_cost_logger_raw.jsonl')
if os.path.exists(RAW):
    os.remove(RAW)
cl.install(RAW)
import er119_kp_difficulty_01 as dg
REAL_MAKER = dg._REAL_make_difficulty_fn
from er119_test_support_01 import ARTICLE, Env, KpTestCase
import er119_kp_human_review_01 as rv
import export_form_data_01 as xf

RESULT = {}


class WiringReal(KpTestCase):
    def test_real_difficulty_through_production_generation_path(self):
        for level in ('a2', 'b1b'):
            with Env(self.tmp) as env:
                dg.make_difficulty_fn = REAL_MAKER        # 難易度だけ実LLM(Envのmockを外す)
                try:
                    self.ensure(env, level=level)
                finally:
                    dg.make_difficulty_fn = env._difficulty
                kp = self.kp_dir if level == 'b1b' else self.kp_dir_a2
                doc = rv.load_candidates(kp)
                g = doc['difficulty_grading']; print('REC', json.dumps(g, ensure_ascii=False)[:900])
                self.assertEqual(g['model_id'], 'gpt-6-luna'); self.assertEqual(g['prompt_sha256'], dg.PROMPT_SHA256); self.assertEqual(g['status'], 'OK')
                self.assertTrue(g['response_id'].startswith('resp_'))
                self.assertEqual(env.n['difficulty'], 0)   # mockは呼ばれていない(=実LLM)
                lab = [(c['used_form'], c['difficulty']['label_ja'], c['difficulty']['source']) for c in doc['candidates']]
                self.assertTrue(all(s == 'llm' for _, _, s in lab))
                form = xf.convert(doc, slug='kpd02wire', level=level, name='wiring', family='x', run='kpd02', source_kind='PRODUCTION_FORMAL_PATH', note_ja='')
                ents = form['phrases'] + form['words']
                self.assertEqual(len(ents), len(doc['candidates']))
                by = {c['candidate_id']: c['difficulty'] for c in doc['candidates']}
                for e in ents:
                    d = by[e['candidate_id']] if 'candidate_id' in e else None
                    self.assertIsNotNone(e['difficulty']); self.assertEqual(e['difficulty']['label_ja'], d['label_ja'] if d else e['difficulty']['label_ja'])
                fp = os.path.join(OUT, f'kpd02_wiring_form_data_{level}.json')
                json.dump(form, open(fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
                dp = os.path.join(OUT, f'kpd02_wiring_candidates_{level}.json')
                json.dump({'difficulty_grading': g, 'candidates': [{'candidate_id': c['candidate_id'], 'used_form': c['used_form'], 'difficulty': c['difficulty']} for c in doc['candidates']]}, open(dp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
                RESULT[level] = {'grading': g, 'labels': lab, 'form_data': fp, 'form_difficulty_grading': form.get('difficulty_grading')}
                # フォームJS側(本番form_logic.js)で同じdataが検証・表示判定できること
                js = ("const FL=require(%s);const d=JSON.parse(require('fs').readFileSync(%s,'utf8'));"
                      "const its=d.phrases.concat(d.words);console.log(JSON.stringify({valid:FL.validateArticle(d),labels:its.map(x=>FL.difficultyOf(x).label)}))"
                      % (json.dumps(os.path.join(ROOT, 'user_test', 'selection_form_v3', 'form_logic.js')), json.dumps(fp)))
                r = subprocess.run(['node', '-e', js], capture_output=True, text=True, encoding='utf-8')
                j = json.loads(r.stdout)
                self.assertEqual(j['valid'], [])
                self.assertEqual(j['labels'], [e['difficulty']['label_ja'] if e['difficulty']['level'] != 'rare' else '激難(レア)' for e in ents])
                RESULT[level]['js_labels'] = j['labels']


if __name__ == '__main__':
    r = unittest.main(exit=False, argv=['x'])
    raw = [json.loads(l) for l in open(RAW, encoding='utf-8')] if os.path.exists(RAW) else []
    RESULT['cost_logger'] = [{k: x.get(k) for k in ('provider', 'api', 'model_id', 'response_id', 'input_tokens', 'output_tokens', 'cached_input_tokens', 'success')} for x in raw]
    json.dump(RESULT, open(os.path.join(OUT, 'kpd02_wiring_real_result.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(json.dumps(RESULT['cost_logger'], ensure_ascii=False))
    for k in ('a2', 'b1b'):
        if k in RESULT:
            print(k, RESULT[k]['grading']['model_id'], RESULT[k]['grading']['prompt_sha256'][:12], RESULT[k]['grading']['response_id'], RESULT[k]['labels'])
    sys.exit(0 if r.result.wasSuccessful() else 1)
