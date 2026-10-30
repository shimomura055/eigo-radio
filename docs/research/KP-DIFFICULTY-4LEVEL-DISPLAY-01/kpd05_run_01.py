# -*- coding: utf-8 -*-
"""KP-DIFFICULTY-4LEVEL-DISPLAY-01 委任_05: X/Y/Z x Std/Adv の正式Production KP候補生成段をmockなしの実APIで実行(Cap 15円固定・直列)。
既存run(書換禁止)を <run>__kpd05 へコピーしKP候補状態だけ除去 -> 各Familyの正式KP段(X: er119_kp_wiring.run_kp_with_review をer019と同一引数で / Y: er121._kp_review_step / Z: er026._kp_review_step)を実行。
HR確定・TTS・ページ生成は行わない(候補生成+難易度判定でPENDINGになるまで)。usage: python kpd05_run_01.py [X|Y|Z ...]"""
import hashlib, json, os, shutil, sys, time, types
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
MAIN = r'C:\Users\tensh\eigo-radio'
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, 'docs', 'research', 'KP-GATE-DROP-BACKFILL-PRODUCTION-01', 'tools'))
OUT = os.path.join(HERE, 'kpd05_out'); os.makedirs(OUT, exist_ok=True)
CAP = 15.0; USD_JPY = 160.0
PRICE = {"gpt-6-luna": (0.10, 0.01, 0.50), "gemini-3.8-flash": (0.75, 0.075, 3.75)}
RAW = os.path.join(OUT, 'kpd05_cost_logger_raw.jsonl')
from dotenv import load_dotenv; load_dotenv(MAIN + r'\.env')
import test_state_isolation_01  # noqa: F401  (HR queue等のProduction監査logへ書かない)
import er005_cost_logger as cl; cl.install(RAW)
import er119_kp_difficulty_01 as dg
import er119_kp_wiring_01 as kw

SRC = {
    'X': MAIN + r'\er019_output\family_x_audio_production_wiring_01\ai_island_temple__run_kp75_ev_01',
    'Y': MAIN + r'\er121_output\family_y_production_01\redelivery_fee\run_kp75_ev_01',
    'Z': MAIN + r'\er026_output\family_z_production_e2e_01\melos\run_kp75_ev_01',
}
X_TEXT_DIR = MAIN + r'\er019_output\ai_island_temple\run_kp75_ev_01'


def spent():
    t = 0.0
    if not os.path.exists(RAW): return 0.0
    for l in open(RAW, encoding='utf-8'):
        r = json.loads(l)
        if r.get('success') is False: continue
        p = PRICE.get(r.get('model_id'))
        if not p: t += 0.0; continue
        tin, tout, c = r.get('input_tokens') or 0, r.get('output_tokens') or 0, r.get('cached_input_tokens') or 0
        t += (((tin - c) * p[0] + c * p[1] + tout * p[2]) / 1e6) * USD_JPY
    return t


class BudgetStop(Exception): pass


def cap_guard(label):
    s = spent()
    if s > CAP * 0.85:
        raise BudgetStop(f'Cap接近 {s:.2f}円 > {CAP*0.85:.2f}円 (label={label})')


class Budget:
    def guard(self, label, est): cap_guard(label)


def tree_sha(d):
    h = hashlib.sha256(); n = 0
    for r, ds, fs in sorted(os.walk(d)):
        ds.sort()
        for f in sorted(fs):
            p = os.path.join(r, f); h.update(os.path.relpath(p, d).encode()); h.update(open(p, 'rb').read()); n += 1
    return h.hexdigest(), n


def prep(fam):
    src = SRC[fam]; dst = src + '__kpd05'
    before = tree_sha(src)
    if os.path.exists(dst): shutil.rmtree(dst)
    shutil.copytree(src, dst)
    for lv in ('a2', 'b1b'):
        for p in (f'{dst}/{lv}/key_phrases', f'{dst}/key_phrases/{lv}'):
            if os.path.exists(p): shutil.rmtree(p)
    for f in ('kp_review_pending.json', 'review_request.md'):
        if os.path.exists(f'{dst}/{f}'): os.remove(f'{dst}/{f}')
    return src, dst, before


def kp_doc_path(fam, dst, lv):
    return f'{dst}/{lv}/key_phrases/kp_candidates.json' if fam == 'X' else f'{dst}/key_phrases/{lv}/kp_candidates.json'


def run_x(dst, lv):
    text = open(f'{X_TEXT_DIR}/{lv}/article.md', encoding='utf-8').read()
    return kw.run_kp_with_review(text=text, kp_dir=f'{dst}/{lv}/key_phrases', run_dir=dst, family='x', slug='ai_island_temple', level=lv,
                                 article_id=f'FAMILY_X_AUDIO_{os.path.basename(dst)}_{lv}', stop_run_dir=dst, run_hint=dst, guard_fn=cap_guard)


def run_y(dst, lv):
    import er121_family_y_runner_01 as y
    import er121_family_y_structure_01 as ys  # noqa
    ctx = types.SimpleNamespace(out_dir=dst, hooks={}, mode='real', slug='redelivery_fee', budget=Budget(), regenerate_stage=None)
    text = y.ys.canonical_body(y._rd(y._level_text_path(ctx, lv)))
    return y._kp_review_step(ctx, lv, text)


def run_z(dst, lv):
    import er026_family_z_fiction_production_runner_01 as z
    m = z._m()
    ctx = types.SimpleNamespace(out_dir=dst, hooks={}, mode='real', slug='melos', budget=Budget(), regenerate_stage=None, llm_client=None)
    text = z.canonical_article_text(m.w62.rd(z._level_text_path(ctx, lv)))
    return z._kp_review_step(ctx, lv, text)


def main():
    fams = sys.argv[1:] or ['X', 'Y', 'Z']
    res = {}
    rf = os.path.join(OUT, 'kpd05_run_result.json')
    if os.path.exists(rf): res = json.load(open(rf, encoding='utf-8'))
    for fam in fams:
        src, dst, before = prep(fam)
        res.setdefault(fam, {'src': src, 'dst': dst, 'src_sha_before': before[0], 'src_files': before[1], 'levels': {}})
        res[fam].update({'src_sha_before': before[0]})
        for lv in ('a2', 'b1b'):
            cap_guard(f'{fam}_{lv}_start')
            n0 = sum(1 for _ in open(RAW, encoding='utf-8')) if os.path.exists(RAW) else 0
            t0 = time.time(); err = None; r = None
            try:
                r = {'X': run_x, 'Y': run_y, 'Z': run_z}[fam](dst, lv)
            except BaseException as e:
                err = f'{type(e).__name__}: {e}'
            rows = [json.loads(l) for l in open(RAW, encoding='utf-8')][n0:] if os.path.exists(RAW) else []
            dp = kp_doc_path(fam, dst, lv)
            res[fam]['levels'][lv] = {'elapsed_s': round(time.time() - t0, 1), 'error': err, 'doc_exists': os.path.exists(dp), 'doc_path': dp,
                                      'result_status': (r or {}).get('status') or ((r or {}).get('kp_review') or {}).get('state'),
                                      'calls': [{k: x.get(k) for k in ('model_id', 'api', 'response_id', 'input_tokens', 'output_tokens', 'cached_input_tokens', 'success')} for x in rows],
                                      'spent_after': round(spent(), 3)}
            print(fam, lv, res[fam]['levels'][lv]['result_status'], err, 'spent', round(spent(), 3), flush=True)
            json.dump(res, open(rf, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
            if err and 'Cap接近' in err: return
        after = tree_sha(src)
        res[fam]['src_sha_after'] = after[0]; res[fam]['src_unchanged'] = (after[0] == before[0])
        json.dump(res, open(rf, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
