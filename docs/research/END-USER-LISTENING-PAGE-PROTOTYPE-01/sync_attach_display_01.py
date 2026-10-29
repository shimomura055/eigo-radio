"""Attach the DISPLAYED page text of each sentence (from the shipped listening page) to sync/<out>/<part>.sentences.json, and report count mismatches.
The sentence splitter is applied to the page's script text (tags stripped); sentence i of the page == sentence i of the TTS script iff counts agree.
usage: sync_attach_display_01.py <article_key> <page_index_html>"""
import sys, os, re, json, html
sys.path.insert(0, os.path.dirname(__file__))
from sync_common_01 import *
import sync_build_01 as B

key, page = sys.argv[1], sys.argv[2]
a, units = load_article(key)
doc = open(os.path.join(ROOT, page), encoding='utf-8').read()
# level section: AI island page has Standard (#std) then Advanced (#adv)
i_std, i_adv = doc.find("id='std'"), doc.find("id='adv'")
if a['prefix'] == 'std':
    sec = doc[i_std:i_adv]
elif i_adv >= 0 and i_std >= 0:
    sec = doc[i_adv:]
else:
    sec = doc[i_adv:] if i_adv >= 0 else doc
rows = {}
for tr in re.findall(r'<tr>(.*?)</tr>', sec, re.S):
    m = re.search(r"src='audio/([^']+\.mp3)'", tr)
    sc = re.search(r"<div class='script'>(.*?)</div>", tr, re.S)
    if m and sc:
        t = re.sub(r'<[^>]+>', '', sc.group(1))
        t = html.unescape(t).replace('⏸', '')
        rows[m.group(1)] = re.sub(r'\s+', ' ', t).strip()
report = []
for u in units:
    p = os.path.join(ROOT, 'docs/research/END-USER-LISTENING-PAGE-PROTOTYPE-01/sync', a['out'], u['key'] + '.sentences.json')
    if not os.path.exists(p):
        continue
    d = json.load(open(p, encoding='utf-8'))
    txt = rows.get(os.path.basename(u['mp3']))
    if txt is None:
        report.append((u['key'], 'NO_PAGE_SCRIPT_ROW')); continue
    ps = [txt] if u['key'] in ('topic_intro', 'japanese_title') else B.split_sentences(txt, u['lang'])
    ok = len(ps) == len(d['sentences'])
    d['page_text_sentence_count'] = len(ps)
    d['display_match'] = ok
    d['page_script_text'] = txt
    for k, s in enumerate(d['sentences']):
        s['display_text'] = ps[k] if ok else None
    json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    report.append((u['key'], 'OK' if ok else 'COUNT_MISMATCH page=%d sync=%d' % (len(ps), len(d['sentences']))))
for r in report:
    print(key, *r)
