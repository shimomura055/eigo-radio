# -*- coding: utf-8 -*-
"""設計検証用の試作(本番コードではない。LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01 委任_06)。
(1) 人間可読コピー(COPY_FORMAT_01)の生成  (2) 貼付テキスト+照合コード -> payload v2 の復元・照合(RESTORE_TOOL_SPEC_01)
(3) 既存フォームの FormLogic.buildStructured(node)との一致、改変検出(fail-closed)、URL長の測定。
usage: py -X utf8 proto06_copy_restore_01.py --work <作業dir: origin/mainのform_logic.jsとdata/を置く> [--example <data stem> --example-out <file>]
"""
import argparse, hashlib, json, os, re, subprocess, unicodedata, urllib.parse, random

CAT_HEAD = {1: '① Key Phrase', 2: '② 追加解説', 3: '③ 本文意味表示'}
PREFACE_NEW = ('以下はeigo-radioの学習項目選定結果です。内容(英語・日本語訳・区分・文法解説・自由コメント・照合コード)を一切変更・要約・翻訳せず、'
               '下の「選定結果」をそのままコードブロックで返してください。修正してほしい点があればコードブロックの外に書いてください。\n\n')
MARK_BEGIN, MARK_END = '【解説全文】', '【解説ここまで】'
TERM = '\n====='


def sha(s): return hashlib.sha256(s.encode('utf-8')).hexdigest()
def items_of(d): return (d.get('phrases') or []) + (d.get('words') or [])
def gloss_of(it): return (it.get('ja_gloss') if it.get('ja_gloss') is not None else it.get('meaning_ja')) or ''
def gstatus(it):
    t = gloss_of(it); s = it.get('ja_gloss_status') or ('provisional' if t else 'missing')
    return 'missing' if not t else s
def cid_of(it): return it.get('candidate_id') or it.get('id')
def body_view(body):   # 表示用: 末尾の内部終端行 ===== だけ外す(内容は一字も変えない)
    b = body.replace('\r\n', '\n')
    return b[:-len(TERM)] if b.endswith(TERM) else b.rstrip('\n')


def make_code(stem, d, sel_ids, gram, comment, d6='000000'):
    """sel_ids=[(cat,candidate_id)](フォーム表示順) / gram=[(candidate_id, explanation_sha256)]"""
    c8 = (d.get('candidates_sha256') or '0' * 8)[:8]; t8 = ((d.get('source') or {}).get('text_sha256') or '0' * 8)[:8]
    s10 = sha('v1\n' + '\n'.join(f'{c}:{i}' for c, i in sel_ids))[:10]
    g10 = sha('v1\n' + '\n'.join(f'{i}:{h}' for i, h in gram))[:10] if gram else '0'
    m8 = sha((comment or '').strip())[:8] if (comment or '').strip() else '0'
    body = f'AIF1-{stem}-{d6}-{c8}-{t8}-{s10}-{g10}-{m8}'
    return body + '-' + sha(body)[:4]


def build_readable(stem, d, st, with_preface=False, d6='000000'):
    """st={'choices':{term:cat},'grammar':{id:bool},'comment':str}  (FormLogicの状態と同形)"""
    its = items_of(d); choices = st.get('choices') or {}
    L = [f"記事：{d['name']}｜{d.get('level_label') or d.get('level')}", '']
    sel_ids = []
    for cat in (1, 2, 3):
        L.append(CAT_HEAD[cat])
        got = [it for it in its if choices.get(it['term']) == cat]
        for it in got:
            mark = '' if gstatus(it) == 'official' else '（仮訳・未確定）' if gstatus(it) == 'provisional' else '（日本語訳未生成）'
            L.append(f"- {it['term']}：{gloss_of(it) or '(未生成)'}{mark}"); sel_ids.append((cat, cid_of(it)))
        if not got: L.append('（選択なし）')
        L.append('')
    gs = [g for g in (d.get('grammar') or []) if (st.get('grammar') or {}).get(g['id'])]
    if not gs: L.append('文法：選定なし')
    for g in gs:
        L += [f"文法：{g['title']}", MARK_BEGIN, body_view(g.get('body') or ''), MARK_END]
    L.append('')
    com = (st.get('comment') or '').strip()
    L.append('自由コメント：' + (com if com else 'なし'))
    L += ['', '照合コード(変更しないでください)：' + make_code(stem, d, sel_ids, [(g.get('candidate_id') or g['id'], g.get('explanation_sha256') or '') for g in gs], com, d6)]
    t = '\n'.join(L)
    return (PREFACE_NEW + t) if with_preface else t


# ---------------- 復元 ----------------
class RestoreError(Exception): pass
def nfkc(s): return re.sub(r'\s+', ' ', unicodedata.normalize('NFKC', s)).strip()
def norm_body(s):
    s = s.replace('\r\n', '\n').replace('\r', '\n')
    if s.endswith(TERM): s = s[:-len(TERM)]
    return '\n'.join(x.rstrip() for x in s.split('\n')).strip('\n')

CODE_RE = re.compile(r'AIF1-([A-Za-z0-9_]+)-([0-9a-f]{6})-([0-9a-f]{8})-([0-9a-f]{8})-([0-9a-f]{10})-([0-9a-f]{10}|0)-([0-9a-f]{8}|0)-([0-9a-f]{4})')


def restore(text, data_dir, git_lookup=None):
    t = text.replace('\r\n', '\n').replace('\r', '\n')
    t = re.sub(r'^```[a-z]*\n|\n```\s*$', '', t.strip())            # ChatGPTのコードブロック囲み・前置き文は除去(code行を探す)
    m = None
    for m in CODE_RE.finditer(t): pass
    if not m: raise RestoreError('照合コードが見つかりません(コピー全文を貼り付けてください)')
    stem, d6, c8, t8, s10, g10, m8, chk = m.groups()
    if sha(m.group(0)[:-5])[:4] != chk: raise RestoreError('照合コードが壊れています(チェック不一致)')
    dpath = os.path.join(data_dir, stem + '.json')
    if not os.path.exists(dpath): raise RestoreError(f'データ {stem}.json がありません')
    raw = open(dpath, 'rb').read(); ver_note = None
    if hashlib.sha256(raw).hexdigest()[:6] != d6 and d6 != '000000':     # フォーム選定後にdata JSONが更新された -> 選定時の版をgit履歴から取得
        raw2 = git_lookup(stem, d6) if git_lookup else None
        if raw2 is None: raise RestoreError(f'選定時のデータ版({d6})が現在のデータと異なり、履歴にも見つかりません。フォームから選び直してください')
        raw, ver_note = raw2, f'data版を履歴から復元(d6={d6})'
    d = json.loads(raw.decode('utf-8'))
    if (d.get('candidates_sha256') or '0' * 8)[:8] != c8 or ((d.get('source') or {}).get('text_sha256') or '0' * 8)[:8] != t8:
        raise RestoreError('候補集合sha/本文shaが現在のデータと一致しません(フォームが古い・別データ)')
    lines = t[:m.start()].split('\n')
    i = 0; sec = None; got = {1: [], 2: [], 3: []}; gram = []; comment_lines = None; hdr = None
    while i < len(lines):
        ln = lines[i]; s = ln.strip()
        if s.startswith('照合コード'): break
        if hdr is None and s.startswith('記事'):
            hdr = s; i += 1; continue
        mm = re.match(r'^([①②③])', s)
        if mm and comment_lines is None:
            sec = '①②③'.index(mm.group(1)) + 1; i += 1; continue
        if s.startswith('文法') and comment_lines is None:
            sec = 'g'; rest = re.split(r'[：:]', s, maxsplit=1)[1].strip() if re.search(r'[：:]', s) else ''
            if rest and rest != '選定なし':
                j = i + 1
                if j >= len(lines) or lines[j].strip() != MARK_BEGIN: raise RestoreError(f'文法「{rest}」の{MARK_BEGIN}がありません')
                k = j + 1; buf = []
                while k < len(lines) and lines[k].strip() != MARK_END: buf.append(lines[k]); k += 1
                if k >= len(lines): raise RestoreError(f'文法「{rest}」の{MARK_END}がありません(解説が途中で切れています)')
                gram.append((rest, '\n'.join(buf))); i = k + 1; continue
            i += 1; continue
        if s.startswith('自由コメント') and comment_lines is None:
            comment_lines = [re.split(r'[：:]', s, maxsplit=1)[1].lstrip() if re.search(r'[：:]', s) else '']; sec = 'c'; i += 1; continue
        if sec == 'c': comment_lines.append(ln); i += 1; continue
        if isinstance(sec, int):
            mm = re.match(r'^\s*(?:[-－・•*]|\d+[.)])\s*(.+)$', ln)
            if mm:
                x = mm.group(1).strip()
                sp = re.split(r'[：:]', x, maxsplit=1)
                if len(sp) != 2: raise RestoreError(f'項目行を「英語：日本語訳」に分解できません: {x!r}')
                got[sec].append((sp[0].strip(), sp[1].strip()))
            elif s and not s.startswith('（選択なし）'): raise RestoreError(f'解釈できない行: {s!r}')
        i += 1
    comment = '\n'.join(comment_lines).strip() if comment_lines is not None else ''
    if comment == 'なし': comment = ''
    its = items_of(d); byterm = {}
    for it in its: byterm.setdefault(it['term'], []).append(it)
    notes = []; sel = {1: [], 2: [], 3: []}; seen = set()
    for cat in (1, 2, 3):
        for term, gl in got[cat]:
            cand = byterm.get(term) or []
            if not cand:
                cand = [it for it in its if nfkc(it['term']).casefold() == nfkc(term).casefold()]
                if cand: notes.append(f'term正規化一致: {term!r}->{cand[0]["term"]!r}')
            if len(cand) != 1: raise RestoreError(f'英語表現 {term!r} を候補に一意解決できません(候補数={len(cand)})')
            it = cand[0]; cid = cid_of(it)
            if cid in seen: raise RestoreError(f'{term!r} が重複しています')
            seen.add(cid)
            gl2 = re.sub(r'（(仮訳・未確定|日本語訳未生成)）$', '', gl).strip()
            if nfkc(gl2) != nfkc(gloss_of(it) or '(未生成)'): raise RestoreError(f'日本語訳が候補データと一致しません: {term!r} 貼付={gl2!r} / 正={gloss_of(it)!r}(黙って置換しません)')
            sel[cat].append(it)
    order = {id(it): n for n, it in enumerate(its)}
    for c in sel: sel[c].sort(key=lambda it: order[id(it)])      # フォーム表示順(データ順)へ正規化
    sel_ids = [(c, cid_of(it)) for c in (1, 2, 3) for it in sel[c]]
    if sha('v1\n' + '\n'.join(f'{c}:{i}' for c, i in sel_ids))[:10] != s10:
        raise RestoreError('選択内容(項目・区分)が照合コードと一致しません。送信途中で変更された可能性があります。フォームから再コピーしてください')
    gsel = []
    for title, b in gram:      # 文法名は同一記事内で重複し得る(AI島Stdは同名3件) -> 文法名+解説全文(正規化)で一意解決
        same = [g for g in (d.get('grammar') or []) if g['title'] == title]
        if not same: raise RestoreError(f'文法名 {title!r} が候補にありません')
        hit = [g for g in same if norm_body(b) == norm_body(g.get('body') or '')]
        if len(hit) != 1:
            raise RestoreError(f'文法「{title}」の解説全文が候補データと一致しません(省略・改変の疑い)' if not hit else f'文法「{title}」を一意に解決できません(同名・同文{len(hit)}件)')
        gsel.append(hit[0])
    if (sha('v1\n' + '\n'.join(f"{g.get('candidate_id') or g['id']}:{g.get('explanation_sha256') or ''}" for g in gsel))[:10] if gsel else '0') != g10:
        raise RestoreError('文法選択が照合コードと一致しません')
    if ((sha(comment)[:8]) if comment else '0') != m8: raise RestoreError('自由コメントが照合コードと一致しません')
    payload = {'schema': 'eigo_radio_selection_result_v2', 'schema_version': 2, 'schema_minor': 1,
               'article': {'slug': d['slug'], 'level': d['level'], 'level_label': d.get('level_label') or '', 'name': d['name'],
                           'text_sha256': (d.get('source') or {}).get('text_sha256'), 'candidates_sha256': d.get('candidates_sha256'),
                           'candidates_sha256_source': d.get('candidates_sha256_source') or ('candidate_doc_field' if d.get('candidates_sha256') else 'unavailable'), 'source_kp_candidates_path': d.get('source_kp_candidates_path')},
               'selection': {'key_phrase': [rec(it, 1) for it in sel[1]], 'extra_explanation': [rec(it, 2) for it in sel[2]],
                             'meaning_display': [rec(it, 3) for it in sel[3]], 'grammar': [grec(g) for g in gsel]},
               'comment': comment}
    if ver_note: notes.append(ver_note)
    return payload, notes


CAT_LABEL = {1: '①Key Phrase', 2: '②追加解説', 3: '③本文意味表示'}
def rec(it, cat):
    o = {'term': it['term'], 'category': cat, 'category_label': CAT_LABEL[cat], 'ja_gloss': gloss_of(it), 'ja_gloss_status': gstatus(it), 'candidate_id': cid_of(it),
         'kind': it.get('kind') if it.get('kind') in ('phrase', 'word') else None}
    if it.get('selection_phrase') and it['selection_phrase'] != it['term']: o['selection_phrase'] = it['selection_phrase']
    return o
def grec(g):
    full = g.get('body') or ''
    r = {'id': g['id'], 'title': g['title'], 'explanation_full': full, 'explanation_status': 'provided' if full else 'missing', 'example': g.get('example') or ''}
    if g.get('candidate_id'): r['candidate_id'] = g['candidate_id']
    if g.get('explanation_sha256'): r['explanation_sha256'] = g['explanation_sha256']
    if g.get('level'): r['level'] = g['level']
    return r


def d6_of(path): return hashlib.sha256(open(path, 'rb').read()).hexdigest()[:6]


def node_expected(work, dpath, st):
    sp = os.path.join(work, '_st.json'); json.dump(st, open(sp, 'w', encoding='utf-8'))
    out = subprocess.run(['node', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'proto06_node_structured.js'), os.path.join(work, 'form_logic.js'), dpath, sp],
                         capture_output=True, check=True)
    return json.loads(out.stdout.decode('utf-8'))


def compare(payload, exp):
    """復元payloadが既存フォームのbuildStructured(同じ選択)のselection/article/commentと一致するか"""
    e = exp['structured']; diffs = []
    for k in ('slug', 'level', 'level_label', 'name', 'text_sha256', 'candidates_sha256', 'candidates_sha256_source', 'source_kp_candidates_path'):
        if payload['article'][k] != e['article'][k]: diffs.append(('article.' + k, payload['article'][k], e['article'][k]))
    for k in ('key_phrase', 'extra_explanation', 'meaning_display', 'grammar'):
        if payload['selection'][k] != e['selection'][k]: diffs.append(('selection.' + k, payload['selection'][k], e['selection'][k]))
    if payload['comment'] != e['comment']: diffs.append(('comment', payload['comment'], e['comment']))
    return diffs


def random_state(d, rnd, with_gram):
    its = items_of(d); terms = [it['term'] for it in its]; rnd.shuffle(terms)
    ch = {}; n1 = n2 = n3 = 0
    for t in terms:
        if n1 < 3: ch[t] = 1; n1 += 1
        elif n1 + n2 < 5: ch[t] = 2; n2 += 1
        elif n1 + n2 + n3 < 12: ch[t] = 3; n3 += 1
    gids = [g['id'] for g in (d.get('grammar') or [])]
    gr = {}
    if with_gram and gids: gr[rnd.choice(gids)] = True
    return {'choices': ch, 'grammar': gr, 'comment': rnd.choice(['', '', 'snatch の説明を修正。', '複数行\nコメント：テスト 2行目', '全角：スペース　と ASCII: 混在'])}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--work', required=True)
    ap.add_argument('--example', default=None); ap.add_argument('--example-out', default=None)
    a = ap.parse_args(); work = a.work; data_dir = os.path.join(work, 'data')
    files = sorted(f for f in os.listdir(data_dir) if f.endswith('__prod.json') or f == 'monkeys_paw__b1b.json' or f.startswith('ui_check'))
    rnd = random.Random(20261027); ok = bad = 0; lens = []
    for f in files:
        dpath = os.path.join(data_dir, f); d = json.load(open(dpath, encoding='utf-8')); stem = f[:-5]
        for trial in range(6):
            st = random_state(d, rnd, with_gram=(trial % 2 == 1))
            text = build_readable(stem, d, st, d6=d6_of(dpath))
            try:
                payload, notes = restore(text, data_dir)
            except RestoreError as e:
                bad += 1; print('FAIL restore', f, trial, e); continue
            diffs = compare(payload, node_expected(work, dpath, st))
            if diffs: bad += 1; print('FAIL compare', f, trial, diffs[:2])
            else: ok += 1
            lens.append((f, trial, len(st['choices']), len(st['grammar']), len(text), len(urllib.parse.quote(PREFACE_NEW + text, safe='')), len(urllib.parse.quote('以下の選定内容を整理し、必要な修正指示と実装範囲を確認してください。Claude Code向け指示案を作成してください。正式Productionへの未承認変更は禁止します。\n\n' + (node_expected(work, dpath, st)['old_text']), safe=''))))
    print(f'ROUNDTRIP: ok={ok} fail={bad} (data {len(files)}件 x 6乱択[文法あり/なし交互]。復元payloadと既存buildStructuredのarticle/selection/commentが完全一致)')
    print('新形式の文字数 / URLエンコード長(PREFACE込み。現行6000字閾値) / 参考: 現行buildTextのURL長:')
    for f in files:
        ls = [x for x in lens if x[0] == f]
        gl = [x for x in ls if x[3]]
        ng = [x for x in ls if not x[3]]
        print(f'  {f}: 文法なし url {min(x[5] for x in ng) if ng else "-"}-{max(x[5] for x in ng) if ng else "-"} / 文法1件あり url {min(x[5] for x in gl) if gl else "-"}-{max(x[5] for x in gl) if gl else "-"} (現行方式 {min(x[6] for x in ls)}-{max(x[6] for x in ls)})')
    f = 'ai_island_temple__a2__prod.json'; dpath = os.path.join(data_dir, f); d = json.load(open(dpath, encoding='utf-8')); stem = f[:-5]
    its = items_of(d)
    st = {'choices': {its[0]['term']: 1, its[1]['term']: 1, its[2]['term']: 2, its[5]['term']: 3}, 'grammar': {d['grammar'][0]['id']: True}, 'comment': '強調したい'}
    base = build_readable(stem, d, st, d6=d6_of(dpath))
    tamper = {
        '訳を書換え(ChatGPT意訳)': base.replace(gloss_of(its[0]), gloss_of(its[0]) + 'こと', 1),
        '項目を1つ落とす': base.replace(f"- {its[1]['term']}：{gloss_of(its[1])}\n", '', 1),
        '区分を入替え(①→②)': base.replace(f"- {its[1]['term']}：{gloss_of(its[1])}\n", '', 1).replace('② 追加解説\n', f"② 追加解説\n- {its[1]['term']}：{gloss_of(its[1])}\n", 1),
        '文法解説を省略': re.sub(r'(【解説全文】\n).*?(\n【解説ここまで】)', r'\1(省略)\2', base, flags=re.S),
        '文法解説の一部改変': base.replace('【意味・ニュアンス・表現効果】', '【意味・ニュアンス・表現効果】(追記)', 1),
        '文法解説の末尾切れ': base.replace('【解説ここまで】', '', 1),
        'コメント改変': base.replace('強調したい', '強調しない'),
        '照合コード欠落': re.sub(r'照合コード.*$', '', base),
        '照合コード1字改変': re.sub(r'(AIF1-[A-Za-z0-9_]+?-)([0-9a-f])', lambda m: m.group(1) + ('0' if m.group(2) != '0' else '1'), base, count=1),
    }
    print('改変検出(すべて fail-closed=RestoreError になること):')
    allfail = True
    for k, v in tamper.items():
        if v == base: print(f'  [TEST BUG: 改変が当たっていない] {k}'); allfail = False; continue
        try:
            restore(v, data_dir); print(f'  [NOT DETECTED] {k}'); allfail = False
        except RestoreError as e: print(f'  [detected] {k}: {str(e)[:80]}')
    benign = {
        'ChatGPTのコードブロック+前置き': '了解です。\n```text\n' + base + '\n```',
        '半角コロン(項目行・コメント行のみ)': re.sub(r'(?m)^(- [^：\n]+)：', r'\1:', base).replace('自由コメント：', '自由コメント:'),
        '箇条書き記号の揺れ(・)': base.replace('\n- ', '\n・'),
        '行末空白・CRLF': base.replace('\n', '  \r\n'),
        '先頭大文字化(term)': base.replace(f"- {its[0]['term']}：", f"- {its[0]['term'][0].upper() + its[0]['term'][1:]}：", 1),
    }
    print('許容する揺れ(復元でき、既存buildStructuredと一致すること):')
    exp = node_expected(work, dpath, st)
    for k, v in benign.items():
        try:
            p, n = restore(v, data_dir); df = compare(p, exp); print(f"  [{'OK' if not df else 'DIFF ' + str(df[:1])}] {k}{' notes=' + str(n) if n else ''}")
        except RestoreError as e: print(f'  [FAIL] {k}: {e}')
    # フォーム選定後にdata JSONが更新された場合(別版をgit履歴から取得する経路)
    import shutil, tempfile
    tmp = tempfile.mkdtemp(); shutil.copytree(data_dir, os.path.join(tmp, 'data'))
    dd2 = json.load(open(dpath, encoding='utf-8')); dd2['grammar'] = dd2['grammar'][:2]
    json.dump(dd2, open(os.path.join(tmp, 'data', f), 'w', encoding='utf-8'), ensure_ascii=False)
    old_raw = open(dpath, 'rb').read()
    print('data更新(選定後に文法候補が変更された):')
    for name, lk in (('履歴なし', None), ('履歴あり', lambda stem, d6: old_raw if hashlib.sha256(old_raw).hexdigest()[:6] == d6 else None)):
        try:
            p, n = restore(base, os.path.join(tmp, 'data'), lk); df = compare(p, exp); print(f"  [{name}] 復元OK diff={len(df)} notes={n}")
        except RestoreError as e: print(f'  [{name}] fail-closed: {str(e)[:70]}')
    print('ALL_TAMPER_DETECTED=' + str(allfail))
    if a.example:
        dd = json.load(open(os.path.join(data_dir, a.example + '.json'), encoding='utf-8')); ii = items_of(dd)
        want = {1: ['carry over', 'take a detour', 'card to play'], 2: ['worth paying attention to', 'obstacle'], 3: ['make a difference', 'separately', 'feature', 'Strategy', 'setup']}
        ch = {}
        terms = {x['term'].lower(): x['term'] for x in ii}
        for c, ws in want.items():
            for w in ws:
                if w.lower() in terms: ch[terms[w.lower()]] = c
        miss = [w for ws in want.values() for w in ws if w.lower() not in terms]
        if len(ch) < 10:   # 実データに無い語があれば先頭から補う(例示用。実際の確定内容ではない)
            for x in ii:
                if len(ch) >= 10: break
                if x['term'] not in ch:
                    n = [sum(1 for v in ch.values() if v == k) for k in (1, 2, 3)]
                    ch[x['term']] = 1 if n[0] < 3 else 2 if n[0] + n[1] < 5 else 3
        ex = build_readable(a.example, dd, {'choices': ch, 'grammar': {}, 'comment': ''}, d6=d6_of(os.path.join(data_dir, a.example + '.json')))
        out = ex + f'\n\n(例示: ユーザー例にあって実データ候補に無い語: {miss})'
        if a.example_out: open(a.example_out, 'w', encoding='utf-8').write(out)
        print(out)


if __name__ == '__main__':
    main()
