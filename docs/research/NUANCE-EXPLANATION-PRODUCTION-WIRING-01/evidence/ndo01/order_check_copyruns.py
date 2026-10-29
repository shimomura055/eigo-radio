# ①表示順序の実run証跡(API 0・read-only)。copy-run(X/Y/Z)のnuance_result.jsonを現行の共通builderで描画し、順序・件数を検証する。
import json, glob, os, re, sys
sys.path.insert(0, '.')
import er120_part2_grammar_production_01 as g
import er120_part2_wiring_01 as p2w
ORDER = [f"<h3>{g.NUANCE_HEADING}</h3>", "<h4>", "<dt>本文の英文</dt>", "<dt>日本語訳</dt>", "<dt>ポイント</dt>", "<dt>解説</dt>"]
rows = []
for f in sorted(glob.glob('C:/Users/tensh/eigo-radio-evidence/NXW02C/*/*/**/nuance_result.json', recursive=True)):
    f = f.replace(chr(92), '/')
    if '_saved' in f: continue
    r = json.load(open(f, encoding='utf-8'))
    fam = f.split('NXW02C/')[1].split('/')[0].upper()
    run = f.split('NXW02C/')[1].split('/')[1] + ('/' + f.split('NXW02C/')[1].split('/')[2] if 'run_' not in f.split('NXW02C/')[1].split('/')[1] else '')
    lvl = 'a2(Standard)' if '/a2/' in f else 'b1b(Advanced)'
    st = r.get('status')
    html = g.render_nuance_html_block(r, include_css=False) if st == 'ADOPTED' else ''
    if st == 'ADOPTED':
        pos = [html.index(m) for m in ORDER]
        ok = pos == sorted(pos) and len(set(pos)) == 6
        exp = g.expected_nuance_blocks(r); got = g.count_nuance_blocks(html)
    else:
        ok = html == '' ; exp = got = 0
    rows.append(dict(family=fam, run=run, level=lvl, status=st, order_ok=ok, blocks_expected=exp, blocks_rendered=got))
json.dump(rows, open(os.path.join(os.path.dirname(__file__), 'order_check_copyruns.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for r in rows: print(r)
print('ALL_OK', all(r['order_ok'] and r['blocks_expected'] == r['blocks_rendered'] for r in rows))
