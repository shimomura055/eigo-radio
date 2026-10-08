# OPEN-243-TRANSLATION-NG-ANALYSIS-01: generate markdown table fragments from items.jsonl / _dev_all.json (read-only). run from repo root.
import json, collections, re
OUT = 'er052_output/open243_translation_ng_analysis_01'
rows = [json.loads(l) for l in open(OUT + '/items.jsonl', encoding='utf8')]
C = [r for r in rows if r['counted']]
ev = {}
for r in C: ev.setdefault(r['event_id'], []).append(r)

def esc(s): return (s or '').replace('|', '/').replace('\n', ' ')
def short_run(r):
    k = r['run_dir'].split('/runs/')[-1].replace('/control/', '/').replace('__', ' ')
    return k
def sev_label(rs):
    labs = []
    for x in rs:
        labs.append(f"{x['trial']}:{'重大' if x['severity']=='major' else '軽微'}")
    return ','.join(sorted(set(labs)))
def ed_label(rs):
    seen = {}
    for x in rs:
        for e in x['en_deviation_check']:
            key = (e['src'] if e['src'] == 'final' else 'attempt', e['severity'], str(e['origin']), '+'.join(e['flags']))
            seen[key] = 1
    if not seen: return '指摘なし'
    fin = [k for k in seen if k[0] == 'final']
    use = fin or list(seen)
    return '; '.join(f"{k[1]}/origin={k[2]}({k[3]})" for k in use[:2])
def ck_label(rs):
    if not any(x['checker']['has_checker'] for x in rs): return 'Checkerデータなし(予算STOP)'
    c = [x['checker'] for x in rs if x['checker']['has_checker']][0]
    if not any(x['checker'].get('candidate') for x in rs): return '候補化なし'
    mats = sorted({m['materiality'] for x in rs for m in x['checker'].get('cycles', [])})
    present = [x['checker'].get('sentence_in_final_text') for x in rs if x['checker']['has_checker']][0]
    fin = '除去/改変' if present is False else '残存'
    return f"候補化 Stage2={'/'.join(mats) or 'stage1のみ'} → 最終文{fin}"

def table_nonja():
    L = ['| EV | 判定ID | run | 盲検重大度 | 起源(判定:手動) | 型 | 箇所 | 言語構造要因 | JA R2対応文(引用) | EN文(引用) | EN deviation check | Checker |', '|---|---|---|---|---|---|---|---|---|---|---|---|']
    om = {'translation': '翻訳段由来', 'amplified': '翻訳で増幅', 'ja': 'JA由来'}
    tm = dict(subject='主体', number='数', scope='範囲', causal='因果', strength='断定の強さ', addition='付け足し', term='訳語選択/指示対象', tense='時制', other='その他')
    pm = dict(body='本文', summary='末尾要約', title='タイトル')
    for eid, rs in sorted(ev.items()):
        r0 = rs[0]
        if r0['origin'] == 'ja': continue
        L.append('| ' + ' | '.join([eid, ','.join(x['id'] for x in rs), esc(short_run(r0)), sev_label(rs), om[r0['origin']], tm[r0['type']], pm[r0['position']],
                                     esc(r0['linguistic_cause']), '「' + esc(r0['ja_r2_corresponding'] or '(JA本文に対応文なし=EN側で新規生成)') + '」', '"' + esc((r0['en_sentence_matched'] or r0['ng_text'])[:130]) + '"',
                                     esc(ed_label(rs)), esc(ck_label(rs))]) + ' |')
    return '\n'.join(L)

def table_ja():
    L = ['| EV | 判定ID | run | 盲検重大度 | 型 | JA R2対応文(引用) | EN deviation check | Checker |', '|---|---|---|---|---|---|---|---|']
    tm = dict(subject='主体', number='数', scope='範囲', causal='因果', strength='断定の強さ', addition='付け足し', term='訳語', tense='時制', other='その他')
    for eid, rs in sorted(ev.items()):
        r0 = rs[0]
        if r0['origin'] != 'ja': continue
        L.append('| ' + ' | '.join([eid, ','.join(x['id'] for x in rs), esc(short_run(r0)), sev_label(rs), tm[r0['type']], '「' + esc(r0['ja_r2_corresponding'])[:60] + '」', esc(ed_label(rs)), esc(ck_label(rs))]) + ' |')
    return '\n'.join(L)

def table_pending():
    L = ['| 判定ID | run | 箇所 | 型 | 起源(判定:手動) | NG文(引用) | 備考 |', '|---|---|---|---|---|---|---|']
    for r in rows:
        if r['counted']: continue
        L.append(f"| {r['id']} | {esc(short_run(r))} | {r['position']} | {r['type']} | {r['origin']} | {esc(r['ng_text'])[:100]} | {esc(r['judgment_basis'])[:120]} |")
    return '\n'.join(L)

def table_dev():
    dev = json.load(open(OUT + '/_dev_all.json', encoding='utf8'))
    tr = [x for x in dev if x.get('origin') == 'translation']
    flags = ['changed_fact', 'changed_scope', 'changed_causality', 'changed_certainty', 'changed_number', 'changed_actor', 'changed_negation', 'changed_comparison', 'changed_time', 'unsupported_new_claim']
    L = ['| # | 出典(deviation_check.json / 各attempt) | 種別 | severity | changed_*フラグ | related_fact_id | 箇所 | 文(claim_in_article) |', '|---|---|---|---|---|---|---|---|']
    n = 0
    for x in sorted(tr, key=lambda z: (z['file'], z['attempt'], z['kind'])):
        n += 1
        fl = '+'.join(k.replace('changed_', '') for k in flags if x.get(k) is True) or '-'
        f = x['file'].replace('er052_output/', '').replace('/runs/', ' ').replace('/audit/deviation_checks/', ' ').replace('/audit/', ' ').replace('/control/', '/').replace('/b1b', ' [b1b]').replace('/a2', ' [a2]')
        L.append(f"| {n} | {esc(f)} | {x['kind']}{'' if x['kind']=='final' else x['attempt']} | {x['severity']} | {fl} | {x.get('related_fact_id')} | {x['pos']} | {esc(x['claim_in_article'])[:110]} |")
    return '\n'.join(L), n

if __name__ == '__main__':
    d, n = table_dev()
    open(OUT + '/_frag_nonja.md', 'w', encoding='utf8').write(table_nonja())
    open(OUT + '/_frag_ja.md', 'w', encoding='utf8').write(table_ja())
    open(OUT + '/_frag_pending.md', 'w', encoding='utf8').write(table_pending())
    open(OUT + '/_frag_dev.md', 'w', encoding='utf8').write(d)
    print('ok', n)
