# -*- coding: utf-8 -*-
"""END-USER-LISTENING-PAGE-PROTOTYPE-01 委任_01b: 公開済み/候補の試聴ページHTML(正本の表示)から
視聴ページ試作用の構造化データ(JSON)を作る。本文・解説・音声は改変しない(表示に不要な検証用注記のみ除外)。
入力: user_test/<source>/index.html + run_dir/<lv>/audit/timeline.json
出力: user_test/dev_enduser_page_01/data/<article>.json (+ 確認用ダミー同期 sync_dummy_<article>_<lv>.json)
"""
import re, json, html, hashlib, sys, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
OUT = os.path.join(ROOT, 'user_test', 'dev_enduser_page_01', 'data')

ARTICLES = {
    'ai_island': dict(
        source='user_test/family_x_ai_island_form_01',
        run='er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_form_prod_01',
        family='X', levels={'std': 'a2', 'adv': 'b1b'}),
    'moon': dict(
        source='user_test/family_x_moon_shrinking_reselect_01',
        run='er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_reselect_01',
        family='X', levels={'adv': 'b1b'}),
}
SANITIZED = []  # 表示用に除去した文字列の記録


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def clean_script_html(frag):
    frag = re.sub(r"<span class='chunk-mark'>.*?</span>", '', frag)            # 内部Chunk記号
    frag = re.sub(r"<span class='rpt-lr'[^>]*>(.*?)</span>", r'\1', frag)       # Local Rewrite着色(本文は保持)
    return frag.strip()


ABBR = re.compile(r'(?:\b(?:Mr|Mrs|Ms|Dr|St|vs|etc|No|Inc|Jr|Sr)|\b[A-Z])\.$')


def find_cuts(text):
    cuts = []
    for m in re.finditer(r'([.!?]+["”’\')]*)(\s+|$)|([。！？]+[」』）)"”]*)', text):
        end = m.end(1) if m.group(1) else m.end(3)
        if m.group(1):
            before = text[:m.end(1)]
            if ABBR.search(before):  # 略語のピリオドは文末にしない
                continue
            rest = text[m.end():]
            if rest and rest[0].islower():
                continue
        if end < len(text.rstrip()):
            cuts.append(end)
    return cuts


def split_sentences(frag):
    """HTML断片(span/strong入り)を文単位に分割。開いているtagは閉じ/再開して整合を保つ。"""
    toks = [t for t in re.split(r'(<[^>]+>)', frag) if t != '']
    plain = ''.join(html.unescape(t) for t in toks if not t.startswith('<'))
    cutset = set(find_cuts(plain))
    sents, cur, stack, pos = [], '', [], 0
    for t in toks:
        if t.startswith('<'):
            cur += t
            if t.startswith('</'):
                if stack:
                    stack.pop()
            else:
                stack.append(t)
            continue
        for ch in html.unescape(t):
            cur += html.escape(ch, quote=False)
            pos += 1
            if pos in cutset:
                close = ''.join('</%s>' % re.match(r'<(\w+)', s).group(1) for s in reversed(stack))
                sents.append(cur + close)
                cur = ''.join(stack)
    if re.sub(r'<[^>]+>', '', cur).strip():
        sents.append(cur)
    out = []
    for s in sents:
        s = re.sub(r'^((?:<[^>]+>)*)\s+', r'\1', s)
        s = re.sub(r'\s+((?:</[^>]+>)*)$', r'\1', s)
        if re.sub(r'<[^>]+>', '', s).strip():
            out.append(s)
    return out


def parse_kp(content):
    hdr = re.findall(r'<th>([^<]*)</th>', content)
    rows = re.findall(r'<tr><td>(.*?)</td><td>(.*?)</td></tr>', content, re.S)
    return hdr, [(html.unescape(a), html.unescape(b)) for a, b in rows]


def parse_meanings(content):
    m = re.search(r'<ul class="lk-meaning">(.*?)</ul>', content, re.S)
    if not m:
        return []
    return [html.unescape(x) for x in re.findall(r'<li>(.*?)</li>', m.group(1), re.S)]


def parse_dl(sec):
    items = []
    chunks = re.findall(r"<div class='study-item'>(.*?)</div>(?=<div class='study-item'>|\Z)", sec, re.S)
    for it in chunks:
        if '<dl>' not in it:
            continue
        h4 = re.search(r'<h4>(.*?)</h4>', it)
        pairs = re.findall(r'<dt>(.*?)</dt><dd>(.*?)</dd>', it, re.S)
        items.append(dict(heading=html.unescape(h4.group(1)) if h4 else None,
                          fields=[dict(label=html.unescape(a), html=b) for a, b in pairs]))
    return items


def sanitize_html(h):
    n = re.sub(r'\s*={3,}\s*(?=</p>|$)', '', h)
    if n != h:
        SANITIZED.append(dict(removed='末尾の区切り記号(=====)', before_tail=h[-40:], after_tail=n[-40:]))
    return n


KIND = [
    (r'^Intro$', 'sfx'), (r'^Notification', 'sfx'),
    (r'^(Welcome|Preview intro|Key phrases intro|Full story intro|Outro)', 'fixed'),
    (r'^Topic intro', 'topic'), (r'^Japanese title', 'jtitle'), (r'^Preview', 'preview'),
    (r'^Key Phrase \d', 'kp'), (r'^Comment \d', 'comment'), (r'^Full Story Part \d', 'story'),
    (r'^In One Line', 'oneline'),
]


def kind_of(label):
    for pat, k in KIND:
        if re.search(pat, label):
            return k
    return 'other'


def build(aid, cfg):
    src_dir = os.path.join(ROOT, cfg['source'])
    page = open(os.path.join(src_dir, 'index.html'), encoding='utf-8').read()
    rel = '../' + os.path.basename(cfg['source']) + '/'
    art = dict(id=aid, family=cfg['family'], source_page=cfg['source'] + '/index.html',
               source_page_sha256=sha(os.path.join(src_dir, 'index.html')), levels={})
    title_ja = None
    for lv, run_lv in cfg['levels'].items():
        m = re.search(r"<h2 id='%s'>.*?(?=<h2 id='|\Z)" % lv, page, re.S)
        sec = m.group(0)
        main = re.search(r"<audio id='main_%s'[^>]*src='([^']+)'" % lv, sec).group(1)
        tl = json.load(open(os.path.join(ROOT, cfg['run'], run_lv, 'audit', 'timeline.json'), encoding='utf-8'))
        tl = [x for x in tl if not x['part'].startswith('pause_')]
        rows = re.split(r"(?=<tr><td><b>)", sec.split('<tbody>', 1)[1].split('</tbody>')[0])
        rows = [r for r in rows if r.startswith('<tr><td><b>')]
        assert len(rows) == len(tl), (aid, lv, len(rows), len(tl))
        parts, sid_total = [], 0
        for i, (r, t) in enumerate(zip(rows, tl)):
            label = html.unescape(re.search(r'<b>(.*?)</b>', r).group(1))
            data_t = float(re.search(r"data-t='([\d.]+)'", r).group(1))
            assert abs(data_t - t['start_seconds']) < 0.01, (label, data_t, t)
            seg = re.search(r"<audio[^>]*src='([^']+)'", r).group(1)
            tds = r.split("<td class='play'>", 1)[1].split('</audio></td>', 1)[1]
            content = tds[4:] if tds.startswith('<td>') else tds
            kind = kind_of(label)
            p = dict(idx=i, key='%s_%02d' % (lv, i), label=re.sub(r'\s*\(.*\)$', '', label), kind=kind,
                     start=t['start_seconds'], dur=t['duration_seconds'], seg=seg)
            if kind in ('topic', 'jtitle', 'preview', 'comment', 'story', 'oneline'):
                s = re.search(r"<div class='script'>(.*?)</div>", content, re.S)
                frag = clean_script_html(s.group(1))
                paras = [x for x in re.split(r'\n\s*\n', frag) if x.strip()]
                p['paragraphs'] = []
                for para in paras:
                    sents = []
                    for sh in split_sentences(para.replace('\n', ' ')):
                        sents.append(dict(sid='%s-s%03d' % (p['key'], sid_total), html=sh,
                                          text=html.unescape(re.sub(r'<[^>]+>', '', sh))))
                        sid_total += 1
                    p['paragraphs'].append(sents)
                if kind == 'story':
                    p['meanings'] = parse_meanings(content)
                if kind == 'jtitle' and lv == 'std':
                    title_ja = html.unescape(re.sub(r'<[^>]+>', '', s.group(1))).strip()
            elif kind == 'kp':
                hdr, rows_ = parse_kp(content)
                p['kp_header'] = hdr
                p['kp'] = [dict(en=a, text=b) for a, b in rows_]
            parts.append(p)
        study = re.findall(r"<section class='study'>(.*?)</section>", sec, re.S)
        vocab = grammar = None
        for sx in study:
            if sx.startswith('<h3>Vocabulary'):
                vocab = parse_dl(sx)
            if sx.startswith('<h3>Grammar'):
                grammar = parse_dl(sx)
        for it in (grammar or []):
            for f in it['fields']:
                f['html'] = sanitize_html(f['html'])
        mp3s = {main: sha(os.path.join(src_dir, main))}
        for p in parts:
            mp3s[p['seg']] = sha(os.path.join(src_dir, p['seg']))
        art['levels'][lv] = dict(level=lv, main=main, parts=parts, vocab=vocab or [], grammar=grammar or [],
                                 total_sec=round(tl[-1]['start_seconds'] + tl[-1]['duration_seconds'], 3),
                                 sentence_count=sid_total, audio_sha256=mp3s)
    topic_en = ''
    for lv, L in art['levels'].items():
        for p in L['parts']:
            if p['kind'] == 'topic':
                topic_en = ' '.join(x['text'] for x in p['paragraphs'][0])
    art['topic_en'] = re.sub(r"^Today's topic is\s*", '', topic_en).strip()
    art['title_ja'] = title_ja or re.search(r'<title>(.*?) 試聴ページ</title>', page).group(1)
    art['audio_base'] = rel
    os.makedirs(OUT, exist_ok=True)
    json.dump(art, open(os.path.join(OUT, aid + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    # 確認用ダミー同期(文字数比例の仮配分。精度を主張しない。フック動作確認専用)
    for lv, L in art['levels'].items():
        out = []
        for p in L['parts']:
            sents = [s for para in p.get('paragraphs', []) for s in para]
            tot = sum(max(1, len(s['text'])) for s in sents)
            t = p['start']
            for s in sents:
                d = p['dur'] * max(1, len(s['text'])) / tot
                out.append(dict(sid=s['sid'], start=round(t, 3), end=round(t + d, 3)))
                t += d
        json.dump(dict(kind='DUMMY_PROPORTIONAL', note='文字数比例の仮配分。実同期ではない(フック動作確認専用)',
                       article=aid, level=lv, sentences=out),
                  open(os.path.join(OUT, 'sync_dummy_%s_%s.json' % (aid, lv)), 'w', encoding='utf-8'),
                  ensure_ascii=False)
    print(aid, {lv: (len(L['parts']), L['sentence_count'], len(L['vocab']), len(L['grammar']))
                for lv, L in art['levels'].items()})


if __name__ == '__main__':
    for aid, cfg in ARTICLES.items():
        build(aid, cfg)
    print('sanitized:', SANITIZED)
    json.dump(SANITIZED, open(os.path.join(OUT, '_sanitized_log.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
