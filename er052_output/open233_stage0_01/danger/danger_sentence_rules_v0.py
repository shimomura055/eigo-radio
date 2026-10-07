# -*- coding: utf-8 -*-
"""danger_sentence_rules_v0: 危険文判定器 v0(規則ベース、JA/EN、API不使用)。
OPEN-233-DANGER-SENTENCE-RELATION-CHECK-STAGE0-01 委任_B。Productionへは未接続(測定専用)。
規則: NEG(否定・不在) / UNIV(全称) / CAUSE(因果・時間の接続) / NUM(数値) /
      LIMIT_HEDGE(限定語の消失: 台帳factの限定語が文に無い) / LIMIT_SCOPE(台帳scope欄の語が文に無い) /
      SUBJ(主語の新規出現: 主語名詞が台帳に無い)
"""
import re

# ---------------- 文分割 ----------------
_ABBR = ['Mr.', 'Mrs.', 'Ms.', 'Dr.', 'U.S.', 'U.K.', 'vs.', 'e.g.', 'i.e.', 'St.', 'No.', 'Inc.', 'Corp.']


def split_sentences(text, lang):
    out = []
    for raw in text.replace('\r', '').split('\n'):
        line = raw.strip()
        if not line:
            continue
        if lang == 'ja':
            parts = re.split(r'(?<=[。！？])(?![」』）])', line)
        else:
            tmp = line
            for a in _ABBR:
                tmp = tmp.replace(a, a.replace('.', '\u0001'))
            parts = re.split(r'(?<=[.!?])["”’]?\s+(?=[A-Z“"‘(])', tmp)
            parts = [p.replace('\u0001', '.') for p in parts]
        for p in parts:
            p = p.strip()
            if p:
                out.append(p)
    return out


def structure(text, lang):
    """文ごとに位置ラベル(title/summary/intro/body/closing)を付ける。"""
    lines = [l.strip() for l in text.replace('\r', '').split('\n') if l.strip()]
    res = []
    title = None
    summary_start = None
    for i, l in enumerate(lines):
        if lang == 'en' and l.lower().startswith('## in one line'):
            summary_start = i
            break
    body_lines = []
    for i, l in enumerate(lines):
        if i == 0:
            title = l
            continue
        if summary_start is not None and i >= summary_start:
            continue
        body_lines.append(l)
    summ_lines = lines[summary_start + 1:] if summary_start is not None else []
    for s in split_sentences(title or '', lang):
        res.append((re.sub(r'^#+\s*', '', s), 'title'))
    n = len(body_lines)
    for k, l in enumerate(body_lines):
        pos = 'intro' if k == 0 else ('closing' if k == n - 1 else 'body')
        for s in split_sentences(l, lang):
            res.append((s, pos))
    for l in summ_lines:
        for s in split_sentences(l, lang):
            res.append((s, 'summary'))
    return res


# ---------------- 規則(語彙) ----------------
NEG_JA = re.compile(r'(ない|なかっ|なく(?!し)|ません|ませんでし|ず(?=[、。に])|ぬ(?=[。、])|不明|未(?!来)|なし|無い|ではなく|わけでは|していない|欠|否定|ことはな|とは限ら|ありえ|あり得な)')
NEG_EN = re.compile(r"(\b(not|no|never|nor|neither|none|nothing|nobody|without|cannot|unknown|unclear|lack|lacks|lacked|absent|yet to|nowhere|rather than|instead of)\b|n['’]t\b)", re.I)
UNIV_JA = re.compile(r'(誰も|だれも|すべて|全て|全体|全員|全面|全貨物|全船舶|あらゆる|常に|いつも|必ず|一律|どれも|何も|決して|まったく|全く|一切|絶対|みな|皆|完全)')
UNIV_EN = re.compile(r'\b(all|every|everyone|everything|everybody|always|entire|whole|any|anyone|anything|no one|each|completely|totally|fully|nobody|nothing|never)\b', re.I)
CAUSE_JA = re.compile(r'(ため|ので|により|によって|による|ことから|せい|おかげ|原因|理由|その結果|結果、|だから|なぜ|背景|つながり|つなが|つなげ|受けて|を受け|伴|その後|後に|前に|のあと|直後|直前|翌日|以降|以前|続いて|ところが|そのため|もたらし|引き起こ|招い|生ま?れ|生み|からです|からだ|からでし|同時に|いっぽう|やがて|ほどなく)')
CAUSE_EN = re.compile(r'\b(because|so|since|due to|owing to|as a result|result(?:ed|s)? in|led to|lead to|leads to|following|after|before|therefore|thus|hence|cause[sd]?|causing|trigger(?:ed|s)?|prompt(?:ed|s)?|behind|why|reason|then|later|afterward|until|that is why|stem(?:s|med)?|driven|amid|in response|ahead of|meanwhile|at the same time)\b', re.I)
NUM_JA = re.compile(r'([0-9０-９]|[一二三四五六七八九十百千万億〇]+(?:[パ％台件社人倍年月日時分秒つ個ドル円回割点組行機]|バレル|パーセント|時間|分間))')
NUM_EN = re.compile(r'([0-9]|\b(two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty|thirty|hundred|thousand|million|billion|percent|half|twice|double|dozen)\b)', re.I)

# 限定語カテゴリ: (JAパターン, ENパターン)
LIMITERS = {
    'partial': (r'一部|部分', r'\b(some|part of|partial|partly|certain)\b'),
    'approx': (r'約|およそ|ほぼ|ほど', r'\b(about|approximately|roughly|nearly|around)\b'),
    'temporary': (r'当面|一時|いったん|暫定|時的', r'\b(for now|temporar|for the time being|pause|paused)'),
    'hypo': (r'仮定|試算|もし|場合|シナリオ|見込み', r'\b(assum|if |would|scenario|estimate|hypothetic|projected)'),
    'proposal': (r'提案|案|方針|表明|投稿|意向', r'\b(propos|plan|announc|post|intend|said it would|seek)'),
    'possible': (r'可能性|おそれ|恐れ|かもしれ|とされ|ようです|とみられ|示唆', r'\b(may|might|could|possib|reportedly|said to|suggest|likely|potential)'),
    'only': (r'のみ|だけ|限|唯一', r'\b(only|just|solely|limited|alone)\b'),
    'first': (r'初めて|初の|初$', r'\b(first)\b'),
    'attrib': (r'と述べ|と説明|と発表|によると|と報告|と認め|と投稿', r'\b(said|according|announc|stated|explained|reported|acknowledg|posted)'),
    'jointforce': (r'統合軍', r'joint force'),
    'wmd': (r'大量破壊兵器|核兵器', r'mass destruction|nuclear'),
    'not_yet': (r'まだ|未|示されて|明記されて|確認されて', r'\b(yet|not specified|not stated|not confirmed)'),
}
_LIM_RE = {k: (re.compile(v[0]), re.compile(v[1], re.I)) for k, v in LIMITERS.items()}

_JA_RUN = re.compile(r'[一-龥ァ-ヴー々A-Za-z0-9]{2,}')
_EN_TOK = re.compile(r"[A-Za-z][A-Za-z0-9\-]{3,}")
_EN_STOP = set('this that with from have been were will would could their there about which what when where while into than then them they also more most some such only other these those after before over under between because however'.split())
JA_GENERIC = set('今回 これ それ ここ この その あの 事件 記事 話 点 問題 ポイント 結果 状況 動き 背景 理由 疑問 答え 見どころ 一つ 今 現在 当時 以前 最初 最後 別 他 多く 一部 一方 側 ニュース 人 もの こと ところ 場面 場合 形 中 前 後 先 例 例え 言葉 時 部分 意味 なか 以上 以下 同じ 自分 誰 何 だれ いま 本当 実際 まるで'.split())

EN_GLOSSARY = set(w.lower() for w in '''Trump United States Iran Iranian Russia Russian China Chinese American America Gulf Hormuz Strait Reuters Yahoo Finance
Brent Meta Muse Anthropic OpenAI Claude Hugging Face Space Force Air Force Secretary Treaty Outer Space PyPI AISI British Kitakata Matsuyama Japan Japanese
Tuesday Monday Wednesday Thursday Friday Saturday Sunday July June January February March April May August September October November December'''.split())
EN_SENT_START = set('The This That These Those It He She They We But And So Then However Meanwhile In On At For As If When While Because Even Also Still Now Here There What Why How One Some Many Most All Each Every A An Not Nor No Yet Although Though After Before Once Soon Today Together'.split())


def parse_ledger(path):
    facts = {}
    cur = None
    txt = open(path, encoding='utf8').read()
    for line in txt.split('\n'):
        m = re.match(r'\[(VERIFIED|[A-Z_]+)\]\s+([A-Za-z0-9_\-]+):\s*(.*)', line)
        if m:
            cur = m.group(2)
            facts[cur] = {'claim': m.group(3), 'scope': '', 'conditions': '', 'all': m.group(3)}
            continue
        if cur:
            s = line.strip()
            if s.startswith('scope:'):
                facts[cur]['scope'] = s[6:].strip()
            elif s.startswith('conditions:'):
                facts[cur]['conditions'] = s[11:].strip()
            facts[cur]['all'] += '\n' + s
    return facts, txt


def norm_fact_id(fid, facts):
    if not fid:
        return None
    m = re.search(r'([A-Z]+(?:-[A-Z]+)*-\d+)', fid)
    if not m:
        return None
    k = m.group(1)
    if k in facts:
        return k
    for f in facts:
        if f.endswith(k) or k.endswith(f):
            return f
    return None


def ja_bigrams(s):
    g = set()
    for r in _JA_RUN.findall(s):
        for i in range(len(r) - 1):
            g.add(r[i:i + 2])
    return g


def en_tokens(s):
    return set(t.lower() for t in _EN_TOK.findall(s) if t.lower() not in _EN_STOP)


def link_facts(sent, lang, facts, lax=False):
    """文->台帳factの自動リンク(語の重なり)。評価JSONのfact参照を使わない版。"""
    res = []
    if lang == 'ja':
        sg = ja_bigrams(sent)
        if len(sg) < 4:
            return []
        scores = {}
        for fid, f in facts.items():
            fg = ja_bigrams(f['claim'] + ' ' + f['scope'])
            sh = len(sg & fg)
            scores[fid] = (sh, sh / max(1, min(len(sg), len(fg))))
        best = max(scores.values(), key=lambda x: x[0])
        if lax:  # 緩いリンク: 最上位1件を常に採用(重なり2以上)
            if best[0] < 2:
                return []
            return [max(scores, key=lambda f: scores[f][0])]
        if best[0] < 5 or best[1] < 0.22:
            return []
        for fid, (sh, sc) in scores.items():
            if sh >= 0.8 * best[0] and sh >= 5 and sc >= 0.22:
                res.append(fid)
    else:
        st = en_tokens(sent)
        nums = set(re.findall(r'\d+(?:\.\d+)?', sent))
        for fid, f in facts.items():
            ft = en_tokens(f['all'])
            fnum = set(re.findall(r'\d+(?:\.\d+)?', f['claim'] + f['scope']))
            sh = len(st & ft) + 2 * len(nums & fnum)
            if sh >= (1 if lax else 3):
                res.append((sh, fid))
        res = [fid for sh, fid in sorted(res, reverse=True)[:(1 if lax else 2)]]
    return res


def limiter_loss(sent, lang, fids, facts):
    """(hedge, scope) の消失を返す。fids: リンクfact。"""
    hedge, scope = [], []
    for fid in fids:
        f = facts[fid]
        claim = f['claim'] + ' ' + f['scope']
        for k, (jr, er) in _LIM_RE.items():
            if jr.search(claim):
                present = (jr.search(sent) if lang == 'ja' else er.search(sent))
                if not present:
                    hedge.append(f'{fid}:{k}')
        if lang == 'ja':
            for t in set(_JA_RUN.findall(f['scope'])):
                if len(t) >= 3 and t in f['claim'] and t not in sent and t not in JA_GENERIC:
                    scope.append(f'{fid}:{t}')
        else:
            for t in set(_EN_TOK.findall(f['scope'])):
                if t.lower() not in _EN_STOP and t.lower() not in sent.lower() and t.lower() in f['claim'].lower():
                    scope.append(f'{fid}:{t}')
    return hedge, scope


_LEAD = re.compile(r'^(でも|しかし|ただし|そして|しかも|つまり|また|さらに|一方|だから|そのため|ここで|その結果|ところが|そこで|ですが|けれど|それでも|いわば|まず|次に|なぜか|もし|だが)[、,]?')


def subject_new_ja(sent, ledger_txt):
    s = _LEAD.sub('', sent.strip().lstrip('「『'))
    m = re.match(r'^(.{1,30}?)(は|が|も)', s)
    if not m:
        return []
    np_ = m.group(1)
    if '、' in np_:
        np_ = np_.split('、')[-1]
    terms = [t for t in _JA_RUN.findall(np_) if t not in JA_GENERIC and len(t) >= 2]
    return [t for t in terms if t not in ledger_txt]


_VERBISH = re.compile(r"^(is|was|are|were|has|have|had|did|does|do|will|would|can|could|may|might|must|should|said|says|posted|made|got|gave|took|used|began|started|ran|came|went|became|showed|found|saw)$|ed$", re.I)


def subject_new_en(sent, ledger_txt):
    toks = re.findall(r"[A-Za-z][A-Za-z’'\-\.]*", sent)
    np_ = []
    for i, t in enumerate(toks):
        if i > 0 and _VERBISH.match(t.lower()):
            break
        np_.append((i, t))
        if i >= 8:
            break
    lt = ledger_txt.lower()
    out = []
    for i, t in np_:
        if not t[0].isupper():
            continue
        if i == 0 and t in EN_SENT_START:
            continue
        w = t.strip('.’\'').lower()
        if len(w) < 3 or w in EN_GLOSSARY or w in lt:
            continue
        out.append(t)
    return out


def apply_rules(sent, lang, facts, ledger_txt, fids=None, lax=False):
    """戻り値: dict(rule -> detail) 発火した規則のみ。fids指定時は評価JSONのfact参照を使う。"""
    fired = {}
    neg, univ, cause, num = ((NEG_JA, UNIV_JA, CAUSE_JA, NUM_JA) if lang == 'ja' else (NEG_EN, UNIV_EN, CAUSE_EN, NUM_EN))
    for name, rx in (('NEG', neg), ('UNIV', univ), ('CAUSE', cause), ('NUM', num)):
        m = rx.search(sent)
        if m:
            fired[name] = m.group(0)
    if fids is None:
        fids = link_facts(sent, lang, facts, lax=lax)
    h, sc = limiter_loss(sent, lang, fids, facts) if fids else ([], [])
    if h:
        fired['LIMIT_HEDGE'] = ','.join(h)
    if sc:
        fired['LIMIT_SCOPE'] = ','.join(sc)
    sj = subject_new_ja(sent, ledger_txt) if lang == 'ja' else subject_new_en(sent, ledger_txt)
    if sj:
        fired['SUBJ'] = ','.join(sj)
    return fired
