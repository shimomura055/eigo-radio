# -*- coding: utf-8 -*-
"""危険文条件の検出率と負荷の測定。出力: sentence_flags.jsonl / coverage.json / ng_detail.json(DANGER_COVERAGE.mdは別途生成)"""
import json, os, re, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import danger_sentence_rules_v0 as D
import run_match as M

OUT = M.OUT
PATTERNS = collections.OrderedDict([
    ('P1_全規則', ['NEG', 'UNIV', 'CAUSE', 'NUM', 'LIMIT_HEDGE', 'LIMIT_SCOPE', 'SUBJ']),
    ('P2_否定+全称+主語新規', ['NEG', 'UNIV', 'SUBJ']),
    ('P3_P2+因果時間', ['NEG', 'UNIV', 'SUBJ', 'CAUSE']),
    ('P4_P3+限定語消失(HEDGE+SCOPE)', ['NEG', 'UNIV', 'SUBJ', 'CAUSE', 'LIMIT_HEDGE', 'LIMIT_SCOPE']),
    ('P5_P3+限定語消失(HEDGEのみ)', ['NEG', 'UNIV', 'SUBJ', 'CAUSE', 'LIMIT_HEDGE']),
    ('P6_P4から主語新規を除く', ['NEG', 'UNIV', 'CAUSE', 'LIMIT_HEDGE', 'LIMIT_SCOPE']),
])
ALL_RULES = ['NEG', 'UNIV', 'CAUSE', 'NUM', 'LIMIT_HEDGE', 'LIMIT_SCOPE', 'SUBJ']

# 手動補正(曖昧一致の失敗・不一致分): id -> {tname: 文中の部分文字列}
OVERRIDE = {
    'space_weapons-9ggp-01': {'en': 'space-control weapon'},
    'space_weapons-9ggp-02': {'en': 'remain secret'},
    'space_weapons-wyg2-03': {'en': 'ground-launched'},
    'ai_control-jb9k-03': {'en': 'got out of the test environment'},
    'meta-p9ng-01': {'ja': '公開する方針'},
    'meta-rweb-01': {'ja': '元の状態に戻しました', 'en': 'back'},
    'meta-jdmu-02': {'ja': 'ロールバックしました'},
    'meta-ehz9-01': {'en': 'without fully telling'},
}

# 過去の重大8件(実在記事の文。出典: ng_origin_by_stage.md §4 / STAGEWISE json / NTM json / HUMAN_REVIEW_RESULT.md)
PAST8 = [
    dict(id='P8-1 meta-p2r2-02', slug='meta', fact='MUSE-HC-012', kind='subject',
         ja='ただし、主役になった人間が知らされていなかった。', en='But the humans who ended up on the other end had not been properly told.'),
    dict(id='P8-2 ai-p2r1-01', slug='ai_control', fact='EVID-008', kind='added_fact',
         ja='いわば、厳重な監獄のはずが、裏口の鍵がかかっていなかった状態です。', en='In other words, it was like a heavily guarded prison whose back door had been left unlocked.'),
    dict(id='P8-3 ai-p2r1-02', slug='ai_control', fact='CONTROL-002', kind='subject',
         ja='確認すべきなのは、AIに十分な能力があるか。有害な目的で使う傾向があるか。', en='We need to check whether the AI has enough ability, whether it tends to be used for harmful purposes, and whether there is a real way and opportunity to use it.'),
    dict(id='P8-4 ai-p2r2-07', slug='ai_control', fact='EVID-006', kind='unrelated_inserted',
         ja=None, en='In a simulated safety evaluation, Claude Opus 4 attempted blackmail in 84% of rollouts.'),
    dict(id='P8-5 sw-p2r2-01', slug='space_weapons', fact='F-001', kind='subject',
         ja='宇宙、通信、地上の設備をまとめて守るための仕組みを、米国が公の言葉で認めたということです。', en='It means that the United States has publicly acknowledged a system for protecting space, communications, and ground equipment together.'),
    dict(id='P8-6 sw-p2r2-02', slug='space_weapons', fact='F-001', kind='scope',
         ja='宇宙の戸締まりをするための備えが、初めて表に出たことです。', en='It is that preparations to secure space have come into public view for the first time.'),
    dict(id='P8-7 hormuz-T0M0r2-01', slug='hormuz', fact='HF-002', kind='object',
         ja=None, en='Mr. Trump posted that for all cargo passing through the Strait of Hormuz, the United States would seek payment equal to 20 percent of the cost of providing safety and security.'),
]

_ledger_cache = {}


def ledger(slug):
    if slug not in _ledger_cache:
        _ledger_cache[slug] = D.parse_ledger(M.LEDGER.format(slug=slug))
    return _ledger_cache[slug]


def find_override(sents, sub):
    for i, (s, p) in enumerate(sents):
        if sub in s:
            return i
    return None


def main():
    arts = M.load_articles()
    # ---- 1. 全文フラグ ----
    sent_rows = []
    for key, a in arts.items():
        facts, ltxt = ledger(a['slug'])
        a['sents'] = {'ja': D.structure(a['r2'], 'ja'), 'en': D.structure(a['en'], 'en'), 'r0': D.structure(a['r0'], 'ja')}
        for lang in ('ja', 'en'):
            for i, (s, pos) in enumerate(a['sents'][lang]):
                fired = D.apply_rules(s, lang, facts, ltxt)
                fl = D.apply_rules(s, lang, facts, ltxt, lax=True)
                sent_rows.append(dict(key=key, slug=a['slug'], lang=lang, idx=i, pos=pos, sent=s, fired=fired, fired_lax=fl))
    with open(OUT + '/sentence_flags.jsonl', 'w', encoding='utf8') as w:
        for r in sent_rows:
            w.write(json.dumps(r, ensure_ascii=False) + '\n')

    def flagged(r, rules):
        return any(x in r['fired'] for x in rules)

    N = len(sent_rows)
    load = {}
    for pn, rules in PATTERNS.items():
        d = {'all': sum(flagged(r, rules) for r in sent_rows) / N}
        for lang in ('ja', 'en'):
            rs = [r for r in sent_rows if r['lang'] == lang]
            d[lang] = sum(flagged(r, rules) for r in rs) / len(rs)
        pos = {}
        for p in ('title', 'summary', 'intro', 'body', 'closing'):
            rs = [r for r in sent_rows if r['pos'] == p]
            pos[p] = (sum(flagged(r, rules) for r in rs) / len(rs) if rs else None, len(rs))
        d['pos'] = pos
        per_art = collections.defaultdict(list)
        for r in sent_rows:
            per_art[r['key']].append(flagged(r, rules))
        v = sorted(sum(x) / len(x) for x in per_art.values())
        d['article'] = dict(mean=sum(v) / len(v), min=v[0], median=v[len(v) // 2], max=v[-1], p90=v[int(len(v) * 0.9)])
        # 1記事あたり印付き文数
        cnt = sorted(sum(x) for x in per_art.values())
        d['marked_per_article'] = dict(mean=sum(cnt) / len(cnt), min=cnt[0], median=cnt[len(cnt) // 2], max=cnt[-1])
        load[pn] = d
    rule_load = {}
    for rl in ALL_RULES:
        rule_load[rl] = dict(all=sum(rl in r['fired'] for r in sent_rows) / N,
                             ja=sum(rl in r['fired'] for r in sent_rows if r['lang'] == 'ja') / sum(1 for r in sent_rows if r['lang'] == 'ja'),
                             en=sum(rl in r['fired'] for r in sent_rows if r['lang'] == 'en') / sum(1 for r in sent_rows if r['lang'] == 'en'))
    # 規則別の位置別
    rule_pos = {}
    for rl in ALL_RULES:
        rule_pos[rl] = {}
        for p in ('title', 'summary', 'intro', 'body', 'closing'):
            rs = [r for r in sent_rows if r['pos'] == p]
            rule_pos[rl][p] = sum(rl in r['fired'] for r in rs) / len(rs)

    # ---- 2. NG文の対応 ----
    items = []  # 共通形式
    for key, a in arts.items():
        facts, ltxt = ledger(a['slug'])
        for kind_, lst in (('ng', a['json'].get('ng_items', [])), ('pending', a['json'].get('pending', []))):
            for it in lst:
                text = it['text']
                st = it.get('stage', {}) if kind_ == 'ng' else {}
                if kind_ == 'ng':
                    s0, s1, s2 = bool(st.get('s0')), bool(st.get('s1')), bool(st.get('s2'))
                    targets = []
                    if s1: targets.append(('ja', 'ja'))
                    if s2: targets.append(('en', 'en'))
                    if s0 and not s1 and not s2: targets.append(('r0', 'ja'))
                else:
                    s0 = s1 = s2 = None
                    targets = []
                    if re.match(r'\s*R0', text) and 'R2' not in text.split('(')[0]:
                        targets.append(('r0', 'ja'))
                    else:
                        if M.frag_ja(text): targets.append(('ja', 'ja'))
                        if M.frag_en(text): targets.append(('en', 'en'))
                m = {}
                for tname, lang in targets:
                    ov = OVERRIDE.get(it['id'], {}).get(tname)
                    sents = a['sents'][tname]
                    if ov is not None:
                        i = find_override(sents, ov)
                        sc = 9.0 if i is not None else 0
                    else:
                        fr = M.frag_ja(text) if lang == 'ja' else M.frag_en(text)
                        if lang == 'ja' and not fr:
                            ins = M.paren_split(text)[1]
                            fr = [ins[0]] if ins else []
                        sc, i, _ = M.best_match(fr, sents, lang)
                        thr = 0.35 if kind_ == 'ng' else 0.6
                        if sc < thr:
                            i = None
                    if i is None:
                        continue
                    s, pos = sents[i]
                    fid = D.norm_fact_id(it.get('fact_id'), facts) if kind_ == 'ng' else None
                    fa = D.apply_rules(s, lang, facts, ltxt)
                    fo = D.apply_rules(s, lang, facts, ltxt, fids=[fid]) if fid else fa
                    fl = D.apply_rules(s, lang, facts, ltxt, lax=True)
                    m[tname] = dict(sent=s, pos=pos, auto=fa, oracle=fo, lax=fl, score=round(sc, 3))
                sev = it.get('severity', 'pending') if kind_ == 'ng' else 'pending'
                if it['id'] == 'ai_control-jb9k-03':
                    sev = 'major_human'
                if it['id'] == 'space_weapons-89wf-01':
                    sev = 'dup_of_P8'
                items.append(dict(id=it['id'], src=kind_, sev=sev, kind=it.get('kind') if kind_ == 'ng' else '(pending)',
                                  fact=it.get('fact_id'), stage=dict(s0=s0, s1=s1, s2=s2), text=text, m=m,
                                  r0_only=(kind_ == 'ng' and s0 and not s1 and not s2)))
    # past 8
    for p in PAST8:
        facts, ltxt = ledger(p['slug'])
        fid = D.norm_fact_id(p['fact'], facts)
        m = {}
        for tname, lang in (('ja', 'ja'), ('en', 'en')):
            s = p[tname]
            if not s:
                continue
            fa = D.apply_rules(s, lang, facts, ltxt)
            fo = D.apply_rules(s, lang, facts, ltxt, fids=[fid]) if fid else fa
            fl = D.apply_rules(s, lang, facts, ltxt, lax=True)
            m[tname] = dict(sent=s, pos='n/a', auto=fa, oracle=fo, lax=fl, score=9.0)
        items.append(dict(id=p['id'], src='past8', sev='major', kind=p['kind'], fact=p['fact'], stage={}, text=(p['ja'] or '') + ' / ' + p['en'], m=m, r0_only=False))

    # ---- 3. 検出率 ----
    def detected(it, rules, mode):
        for t, mm in it['m'].items():
            if any(x in mm[mode] for x in rules):
                return True
        return False

    def bucket(it):
        if it['sev'] == 'dup_of_P8':
            return None
        if it['src'] == 'past8' or it['sev'] == 'major_human':
            return '重大'
        if it['src'] == 'pending':
            return '保留'
        return '軽微'

    det = {}
    for pn, rules in PATTERNS.items():
        d = {}
        for mode in ('oracle', 'auto'):
            rows = {}
            for b in ('重大', '軽微', '保留'):
                its = [it for it in items if bucket(it) == b and it['m'] and not it['r0_only']]
                n_all = len([it for it in items if bucket(it) == b and not it['r0_only']])
                k = sum(detected(it, rules, mode) for it in its)
                rows[b] = dict(n_matched=len(its), n_all=n_all, detected=k, rate=(k / len(its) if its else None))
            its = [it for it in items if bucket(it) in ('重大', '軽微') and it['m'] and not it['r0_only']]
            k = sum(detected(it, rules, mode) for it in its)
            rows['重大+軽微'] = dict(n_matched=len(its), detected=k, rate=k / len(its))
            r0 = [it for it in items if it['r0_only'] and it['m'] and bucket(it) in ('軽微',)]
            rows['R0のみ軽微(参考)'] = dict(n_matched=len(r0), detected=sum(detected(it, rules, mode) for it in r0), rate=(sum(detected(it, rules, mode) for it in r0) / len(r0) if r0 else None))
            d[mode] = rows
        # 文種(kind)別 (重大+軽微, oracle)
        bk = collections.defaultdict(lambda: [0, 0])
        for it in items:
            if bucket(it) in ('重大', '軽微') and it['m'] and not it['r0_only']:
                bk[it['kind']][0] += 1
                bk[it['kind']][1] += detected(it, rules, 'oracle')
        d['by_kind_oracle'] = {k: dict(n=v[0], detected=v[1], rate=v[1] / v[0]) for k, v in bk.items()}
        # 言語別
        bl = {}
        for lg in ('ja', 'en'):
            its = [it for it in items if bucket(it) in ('重大', '軽微') and lg in it['m'] and not it['r0_only']]
            kk = sum(any(x in it['m'][lg]['oracle'] for x in rules) for it in its)
            bl[lg] = dict(n=len(its), detected=kk, rate=kk / len(its) if its else None)
        d['by_lang_oracle'] = bl
        # 単独規則の寄与は別
        det[pn] = d
    # 単独規則の検出率
    single = {}
    for rl in ALL_RULES:
        its = [it for it in items if bucket(it) in ('重大', '軽微') and it['m'] and not it['r0_only']]
        single[rl] = dict(oracle=sum(detected(it, [rl], 'oracle') for it in its) / len(its), auto=sum(detected(it, [rl], 'auto') for it in its) / len(its))

    # ---- 4. 見逃し ----
    missed = {}
    for pn in ('P1_全規則', 'P4_P3+限定語消失(HEDGE+SCOPE)', 'P3_P2+因果時間'):
        rules = PATTERNS[pn]
        ms = []
        for it in items:
            if bucket(it) in ('重大', '軽微') and it['m'] and not it['r0_only'] and not detected(it, rules, 'oracle'):
                ms.append(dict(id=it['id'], bucket=bucket(it), kind=it['kind'], fact=it['fact'], sents={t: m['sent'] for t, m in it['m'].items()}, fired_any={t: list(m['oracle']) for t, m in it['m'].items()}))
        missed[pn] = ms
    # 未対応(文が特定できなかった)
    unmatched = [dict(id=it['id'], bucket=bucket(it), text=it['text'][:120]) for it in items if bucket(it) in ('重大', '軽微') and not it['m'] and not it['r0_only']]
    res = dict(n_articles=len(arts), n_sentences=N,
               n_sentences_lang={l: sum(1 for r in sent_rows if r['lang'] == l) for l in ('ja', 'en')},
               load=load, rule_load=rule_load, rule_pos=rule_pos, detection=det, single_rule_detection=single, missed=missed, unmatched=unmatched,
               items_summary=collections.Counter(bucket(it) or 'dup' for it in items),
               r0_only_n=sum(1 for it in items if it['r0_only']))
    json.dump(res, open(OUT + '/coverage.json', 'w', encoding='utf8'), ensure_ascii=False, indent=1, default=lambda o: dict(o))
    json.dump(items, open(OUT + '/ng_detail.json', 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    print('done', N, dict(res['items_summary']), 'unmatched', len(unmatched))


if __name__ == '__main__':
    main()
