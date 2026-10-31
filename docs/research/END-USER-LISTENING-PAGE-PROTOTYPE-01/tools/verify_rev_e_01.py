# -*- coding: utf-8 -*-
"""END-USER-LISTENING-PAGE-DEV-REVISION-01 rev01-e: 引用英文内の太字化検証 + rev01-d全チェック再実行(verify_rev_d_01を継承)。
使い方: py verify_rev_e_01.py <BASE_URL> [expected_build_id]
        py verify_rev_e_01.py --baseline <BASE_URL>   (rev01-d側のtranscript構造署名を保存。rev01-d公開ページに対して実行)
出力: ../verify_result_rev_e_{local,live}_01.json, ../shots_rev_e{,_live}/, ../rev_e_baseline_signature_01.json"""
import json, os, re, sys
BL = len(sys.argv) > 1 and sys.argv[1] == '--baseline'
if BL:
    sys.argv.pop(1)
import verify_rev_d_01 as D
import sys as _pws_sys, pathlib as _pws_p; _pws_sys.path.insert(0, str(next(_q for _q in _pws_p.Path(__file__).resolve().parents if (_q / "tools" / "playwright_safe_01.py").exists()) / "tools")); from playwright_safe_01 import sync_playwright  # PLAYWRIGHT-AUDIO-SAFETY-01: 無音+終了保証+hard timeout

HERE = os.path.dirname(os.path.abspath(__file__))
OUTD = os.path.abspath(os.path.join(HERE, '..'))
D.SHOTS = os.path.join(OUTD, 'shots_rev_e_live' if D.LIVE else 'shots_rev_e')
os.makedirs(D.SHOTS, exist_ok=True)
SIG = os.path.join(OUTD, 'rev_e_baseline_signature_01.json')


def TXT(h):
    return re.sub(r'<[^>]+>', '', h).replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"').replace('&#39;', "'")


SIGJS = """() => ({
  sents: Array.from(document.querySelectorAll('.sent')).map(e => [e.dataset.sid, e.className, e.textContent, e.outerHTML.length]),
  datasets: Array.from(document.querySelectorAll('[data-sid],[data-part],[data-act],[data-i],[data-vi]')).map(e => [e.tagName, e.className, JSON.stringify(e.dataset)]),
  kp: Array.from(document.querySelectorAll('.kpitem button')).map(b => [b.dataset.act, b.dataset.i, b.textContent]),
  seek: Array.from(document.querySelectorAll('button.seek')).map(b => [b.dataset.act, b.dataset.i, b.textContent]) })"""

def signature(page):
    S = {}
    for a, lv in D.CASES:
        D.open_article(page, a, lv)
        S['%s_%s' % (a, lv)] = page.evaluate(SIGJS)
    return S


def run_view_e(p, view, opts):
    D.run_view(p, view, opts)   # rev01-d全チェック(継承)
    R = D.RES['views'][view]
    browser = p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
    page = browser.new_context(**opts).new_page()

    def rec(item, key, ok, detail=None):
        R.setdefault(item, {})[key] = {'ok': bool(ok), 'detail': detail}
        print(view, item, key, 'OK' if ok else 'NG', detail if detail is not None else '')

    base = json.load(open(SIG, encoding='utf-8')) if os.path.exists(SIG) else None
    cur = signature(page)
    counts = D.RES.setdefault('bold_counts', {})
    for a, lv in D.CASES:
        k = '%s_%s' % (a, lv)
        D.open_article(page, a, lv)
        L = D.DATAJ[a]['levels'][lv]
        em = page.evaluate('() => window.__EMPH')
        for kind, sel in (('vocab', '#vocab details.vi'), ('nuance', '#nuance .gr')):
            items = L.get(kind, [])
            boxes = page.query_selector_all(sel)
            zero = []
            for it, bx in zip(items, boxes):
                n = bx.evaluate("e => { const dt = Array.from(e.querySelectorAll('dt')).filter(d => d.textContent === '本文の英文')[0]; return dt.nextElementSibling.querySelectorAll('strong.target-term').length; }")
                if n < 1:
                    zero.append(it['heading'])
            rec('E', '%s_%s_all_have_bold' % (k, kind), len(boxes) == len(items) and not zero, dict(items=len(items), zero=zero))
            counts['%s_%s' % (k, kind)] = [e['bold'] for e in em[kind]]
        g = em['grammar']
        counts['%s_grammar' % k] = dict(bold=sum(1 for x in g if x['bold']), unresolved=sum(1 for x in g if not x['bold']), total=len(g),
                                        reasons=[x['reason'] for x in g if not x['bold']], phrases=[x['heading'] for x in g if x['bold']])
        rec('E', '%s_grammar_counts_reported' % k, len(g) == len(L.get('grammar', [])), counts['%s_grammar' % k])
        bad = []
        for kind, sel, lab in (('vocab', '#vocab details.vi', '本文の英文'), ('nuance', '#nuance .gr', '本文の英文'), ('grammar', '#grammar .gr', '対象となる本文英文')):
            for it, bx in zip(L.get(kind, []), page.query_selector_all(sel)):
                want = TXT([f for f in it['fields'] if f['label'] == lab][0]['html'])
                got = bx.evaluate("(el, l) => { const dt = Array.from(el.querySelectorAll('dt')).filter(x => x.textContent === l)[0]; return dt.nextElementSibling.textContent; }", lab)
                if got.encode('utf-8') != want.encode('utf-8'):
                    bad.append((kind, want[:40], got[:40]))
        rec('E', '%s_quote_text_byte_identical' % k, not bad, bad[:3])
        rec('E', '%s_no_bold_in_transcript_or_gloss' % k, page.evaluate("() => document.querySelectorAll('.sent .target-term, .gloss .target-term, .tr .target-term, .kpitem .target-term').length") == 0)
        rec('E', '%s_bold_font_weight_700' % k, page.evaluate("() => { const e = document.querySelector('strong.target-term'); return e ? getComputedStyle(e).fontWeight : null; }") in ('700', 'bold'))
        if base:
            rec('E', '%s_transcript_signature_equals_rev01d' % k, base[k] == cur[k],
                dict(sents=len(cur[k]['sents']), kp=len(cur[k]['kp']), seek=len(cur[k]['seek']), datasets=len(cur[k]['datasets'])))
        else:
            rec('E', '%s_baseline_missing' % k, False, 'baseline signature not found')
        rec('E', '%s_strong_only_in_quote_dd' % k, page.evaluate("() => Array.from(document.querySelectorAll('strong.target-term')).every(s => { const dd = s.closest('dd'); const dt = dd && dd.previousElementSibling; return !!dt && ['本文の英文', '対象となる本文英文'].includes(dt.textContent); })"))
    # 汎用性の単体確認(記事非依存): 語形変化・プレースホルダ・不規則・曖昧時の不太字
    D.open_article(page, 'ai_island', 'std')
    cases = [('give up', 'She gave it up quickly.', None), ('give sth up', 'She gave it up quickly.', ['gave', 'up']), ("hold one's breath", 'They held their breath for a minute.', ['held', 'breath']),
             ('carry over', 'It carried over.', ['carried over']), ('study', 'He studies hard.', ['studies']), ('stop', 'We stopped.', ['stopped']),
             ('go on', 'Go on and on.', ['Go on']), ('on', 'Go on and on.', None), ('get', 'He had gotten it.', ['gotten']), ('foo bar', 'nothing here', None)]
    for h, t, want in cases:
        r = page.evaluate("([h, t]) => { const m = window.__matchPhrase(h, t, true); return {n: m.n, txt: m.ranges.map(x => t.slice(x[0], x[1]))}; }", [h, t])
        got = r['txt'] if r['n'] == 1 else None
        rec('U', 'generic_%s' % h.replace(' ', '_').replace("'", ''), got == want or (want is None and got is None), dict(text=t, result=r))
    D.open_article(page, 'ai_island', 'std')
    page.evaluate("document.querySelector('#vocab').scrollIntoView()")
    page.screenshot(path=os.path.join(D.SHOTS, '%s_E_vocab.png' % view))
    D.open_article(page, 'moon', 'adv')
    page.evaluate("document.querySelector('#grammar').scrollIntoView()")
    page.screenshot(path=os.path.join(D.SHOTS, '%s_E_grammar.png' % view))
    page.evaluate("document.querySelector('#nuance').scrollIntoView()")
    page.screenshot(path=os.path.join(D.SHOTS, '%s_E_nuance.png' % view))
    browser.close()


if __name__ == '__main__':
    with sync_playwright() as p:
        if BL:
            b = p.chromium.launch()
            pg = b.new_context(**D.VIEWS['pc']).new_page()
            json.dump(signature(pg), open(SIG, 'w', encoding='utf-8'), ensure_ascii=False)
            b.close()
            print('baseline saved', SIG)
            sys.exit(0)
        for v, o in D.VIEWS.items():
            run_view_e(p, v, o)
    allr = [(v, it, k, c['ok']) for v, R in D.RES['views'].items() for it, d in R.items() if isinstance(d, dict) for k, c in d.items()]
    D.RES['summary'] = dict(total=len(allr), ng=[x for x in allr if not x[3]])
    out = os.path.join(OUTD, 'verify_result_rev_e_%s_01.json' % ('live' if D.LIVE else 'local'))
    json.dump(D.RES, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('TOTAL', len(allr), 'NG', len(D.RES['summary']['ng']))
    for x in D.RES['summary']['ng']:
        print('NG', x)
