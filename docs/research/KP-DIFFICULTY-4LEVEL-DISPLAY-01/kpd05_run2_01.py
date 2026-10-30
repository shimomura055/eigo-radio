# -*- coding: utf-8 -*-
"""委任_05 補足: (A) 1回目run(kpd05_run_01.py)はtest_state_isolation_01のimportで難易度APIが遮断され全docがFAILED_OPENだったため、
生成済み6docの最終候補集合へ**本番と同一関数 dg.apply_to_candidates(実LLM gpt-6-luna)**を後付け適用(原docは .blocked_fail_open.json に保存)。
(B) 完全一括(生成+難易度が1 callチェーン)の実証としてX a2を新規copy(__kpd05full)で難易度APIを遮断解除して再実行。Cap 15円固定。"""
import json, os, shutil, sys, time
sys.argv = [sys.argv[0]]
import kpd05_run_01 as k
import er119_kp_difficulty_01 as dg
import er119_kp_human_review_01 as rv
dg.make_difficulty_fn = dg._REAL_make_difficulty_fn      # test_state_isolation_01による難易度API遮断を解除(他の隔離は維持)
res = json.load(open(os.path.join(k.OUT, 'kpd05_run_result.json'), encoding='utf-8'))
R2 = {'posthoc': {}, 'full': {}}
for fam in 'XYZ':
    for lv in ('a2', 'b1b'):
        dp = res[fam]['levels'][lv]['doc_path']
        doc = json.load(open(dp, encoding='utf-8'))
        assert doc['difficulty_grading']['status'] == 'FAILED_OPEN', (fam, lv)
        shutil.copy(dp, dp.replace('kp_candidates.json', 'kp_candidates.blocked_fail_open.json'))
        k.cap_guard(f'posthoc_{fam}_{lv}')
        n0 = sum(1 for _ in open(k.RAW, encoding='utf-8'))
        order_before = [c['candidate_id'] for c in doc['candidates']]
        rec = dg.apply_to_candidates(doc['candidates'], lv, process='A2_SUPPORT' if lv == 'a2' else 'B1_SUPPORT')
        assert [c['candidate_id'] for c in doc['candidates']] == order_before
        doc['difficulty_grading'] = rec
        doc.pop('candidates_sha256', None); doc['candidates_sha256'] = rv.candidates_sha256(doc)
        json.dump(doc, open(dp, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
        rows = [json.loads(l) for l in open(k.RAW, encoding='utf-8')][n0:]
        R2['posthoc'][f'{fam}_{lv}'] = {'status': rec['status'], 'model_id': rec['model_id'], 'prompt_sha256': rec['prompt_sha256'], 'response_id': rec.get('response_id'),
                                        'n_graded': rec['n_graded'], 'n_unknown': rec['n_unknown'], 'calls': len(rows), 'spent_after': round(k.spent(), 3)}
        print('posthoc', fam, lv, R2['posthoc'][f'{fam}_{lv}'], flush=True)
        json.dump(R2, open(os.path.join(k.OUT, 'kpd05_run2_result.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
# (B) 完全一括 X a2
src = k.SRC['X']; dst = src + '__kpd05full'
if os.path.exists(dst): shutil.rmtree(dst)
shutil.copytree(src, dst); shutil.rmtree(f'{dst}/a2/key_phrases')
for f in ('kp_review_pending.json', 'review_request.md'):
    if os.path.exists(f'{dst}/{f}'): os.remove(f'{dst}/{f}')
k.cap_guard('full_X_a2')
n0 = sum(1 for _ in open(k.RAW, encoding='utf-8')); err = None
try:
    r = k.run_x(dst, 'a2')
except BaseException as e:
    err = f'{type(e).__name__}: {e}'; r = None
rows = [json.loads(l) for l in open(k.RAW, encoding='utf-8')][n0:]
dp = f'{dst}/a2/key_phrases/kp_candidates.json'
doc = json.load(open(dp, encoding='utf-8')) if os.path.exists(dp) else {}
R2['full'] = {'dst': dst, 'doc_path': dp, 'error': err, 'grading': doc.get('difficulty_grading'), 'calls': [{x: y.get(x) for x in ('model_id', 'response_id', 'input_tokens', 'output_tokens', 'cached_input_tokens', 'stage', 'success')} for y in rows], 'spent_after': round(k.spent(), 3)}
json.dump(R2, open(os.path.join(k.OUT, 'kpd05_run2_result.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('full', err, (doc.get('difficulty_grading') or {}).get('status'), 'spent', round(k.spent(), 3), flush=True)
