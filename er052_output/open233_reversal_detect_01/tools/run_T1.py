# -*- coding: utf-8 -*-
"""T1測定: 反転型検出器の型別再現率(既知NG)と負荷(記事・文)。API不使用。
使い方: python run_T1.py dev <tag>   /   python run_T1.py heldout final   (held-outは1回のみ。既存出力があれば拒否)"""
import sys
import os
import json
import re
import random
import collections

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
OUTROOT = os.path.abspath(os.path.join(HERE, '..'))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'er052_output', 'open233_stage0_01', 'danger'))
import importlib
R = importlib.import_module(os.environ.get('DET_MODULE', 'reversal_detector_v0'))  # noqa: E402
import danger_sentence_rules_v0 as D  # noqa: E402
import run_match as M  # noqa: E402

RC = os.path.join(ROOT, 'er052_output', 'open233_stage0_01', 'reclass')
split = json.load(open(os.path.join(RC, 'split.json'), encoding='utf8'))
rows = [json.loads(l) for l in open(os.path.join(RC, 'known_relation_ng.jsonl'), encoding='utf8')]
md = {r['id']: r for r in json.load(open(os.path.join(ROOT, 'er052_output', 'open233_stage0_01', 'danger', 'match_dump.json'), encoding='utf8'))}

which, tag = sys.argv[1], sys.argv[2]
outdir = os.path.join(OUTROOT, f'{which}_{tag}')
if which == 'heldout' and os.path.exists(outdir):
    sys.exit('held-out output exists: 1回のみ')
os.makedirs(outdir, exist_ok=True)

ho_keys = {f"{r['src']}:{r['article']}" for r in rows if r.get('article') and r['split'] == 'heldout'}
arts = M.load_articles()
scan_keys = sorted(k for k in arts if ((k in ho_keys) == (which == 'heldout')))
ledgers = {}


def ledger(slug):
    if slug not in ledgers:
        ledgers[slug] = D.parse_ledger(M.LEDGER.format(slug=slug))
    return ledgers[slug]


# 手動位置補正(match_dumpでEN文が特定できなかったai_control項目。EN本文の文index、目視)
EN_OVERRIDE = {'ai_control-jb9k-n3': 23, 'ai_control-jb9k-n4': 24, 'ai_control-jb9k-n5': 14, 'ai_control-cupe-n1': 25}


def det_lang(slug):
    return 'en' if slug == 'ai_control' else 'ja'


# --- 全文走査 ---
art_res = {}
sent_flags = {}  # (key, idx) -> res
for k in scan_keys:
    a = arts[k]
    slug = a['slug']
    lang = det_lang(slug)
    facts, ltxt = ledger(slug)
    sents = D.structure(a['en'], 'en') if lang == 'en' else D.structure(a['r2'], 'ja')
    flagged = []
    for i, (s, pos) in enumerate(sents):
        r = R.detect(s, lang, facts, ltxt)
        sent_flags[(k, i)] = r
        if r['tags']:
            flagged.append((i, pos, s, r['tags']))
    art_res[k] = {'slug': slug, 'lang': lang, 'n_sents': len(sents), 'flagged': flagged, 'sents': sents}

# --- 既知NG再現率 ---
items = [r for r in rows if r.get('article') and r['split'] == which and r['record'] == 'in_set']
item_res = []
known_sent = set()  # (key, idx) 既知NG/pending項目の文
for it in items:
    key = f"{it['src']}:{it['article']}"
    if key not in art_res:
        continue
    m = md.get(it['orig_id'])
    ar = art_res[key]
    lang = ar['lang']
    sev = it['severity_final']
    row = {'item_id': it['item_id'], 'type': it['sentence_type'], 'sev': sev, 'key': key, 'lang': lang, 'fact_id': it.get('fact_id'),
           'located': False}
    mm = (m or {}).get('matches', {}).get(lang)
    idx = None
    if mm and mm['score'] >= 0.5 and mm['idx'] is not None:
        idx = mm['idx']
    elif it['item_id'] in EN_OVERRIDE:  # 手動補正(Stage0 OVERRIDEの流儀): ai_control項目のEN文位置
        idx = EN_OVERRIDE[it['item_id']]
    if idx is not None:
        row['located'] = True
        row['idx'] = idx
        row['sent'] = ar['sents'][idx][0]
        r = sent_flags[(key, idx)]
        row['frame_excluded'] = r['frame']
        row['tags'] = r['tags']
        row['detail'] = r['detail']
        # oracle link版(fact_id既知)
        facts, ltxt = ledger(ar['slug'])
        fid = D.norm_fact_id(it.get('fact_id'), facts)
        ro = R.detect(row['sent'], lang, facts, ltxt, oracle_fid=fid) if fid else None
        row['tags_oracle'] = ro['tags'] if ro else None
        if sev != 'pending':
            known_sent.add((key, idx))
        else:
            known_sent.add((key, idx, 'pending'))
    item_res.append(row)


def recall(tp, tagset, include_oracle=False):
    ng = [x for x in item_res if x['type'] == tp and x['sev'] != 'pending']
    ev = [x for x in ng if x['located']]
    tags_key = 'tags_oracle' if include_oracle else 'tags'
    hit = [x for x in ev if x.get(tags_key) and set(x[tags_key]) & tagset]
    return {'n_ng': len(ng), 'n_located': len(ev), 'n_frame_excluded': sum(1 for x in ev if x['frame_excluded']),
            'hit': len(hit), 'recall_located': (len(hit) / len(ev)) if ev else None,
            'recall_strict_all_ng': (len(hit) / len(ng)) if ng else None, 'hit_items': [x['item_id'] for x in hit],
            'miss_items': [x['item_id'] for x in ev if x not in hit], 'unlocated_items': [x['item_id'] for x in ng if not x['located']]}


summary = {'version': R.VERSION, 'which': which, 'tag': tag, 'n_articles': len(scan_keys)}
summary['recall'] = {
    'neg_absence_items(tags neg_absence|neg_subject)': recall('否定・不在', {'neg_absence', 'neg_subject'}),
    'subject_items(tags subj_class|neg_subject)': recall('主語新規出現・置換', {'subj_class', 'neg_subject'}),
    'neg_absence_items_any_tag': recall('否定・不在', {'neg_absence', 'subj_class', 'neg_subject'}),
    'subject_items_any_tag': recall('主語新規出現・置換', {'neg_absence', 'subj_class', 'neg_subject'}),
}
summary['recall_oracle_link'] = {
    'neg': recall('否定・不在', {'neg_absence', 'neg_subject'}, True),
    'subj': recall('主語新規出現・置換', {'subj_class', 'neg_subject'}, True),
}
# 他の型(参考)
other = collections.defaultdict(lambda: [0, 0])
for x in item_res:
    if x['sev'] != 'pending' and x['located'] and x['type'] not in ('否定・不在', '主語新規出現・置換'):
        other[x['type']][0] += 1
        other[x['type']][1] += 1 if x['tags'] else 0
summary['other_types_hit(located)'] = {k: v for k, v in other.items()}

# --- 負荷 ---
n_s = sum(a['n_sents'] for a in art_res.values())
n_f = sum(len(a['flagged']) for a in art_res.values())
flag_art = [k for k, a in art_res.items() if a['flagged']]
tagc = collections.Counter(t for a in art_res.values() for (_, _, _, ts) in a['flagged'] for t in ts)
posc = collections.Counter(p for a in art_res.values() for (_, p, _, _) in a['flagged'])
posn = collections.Counter(p for a in art_res.values() for (_, p) in a['sents'])
per_art = sorted(len(a['flagged']) for a in art_res.values())
by_lang = {}
for lg in ('ja', 'en'):
    ks = [k for k, a in art_res.items() if a['lang'] == lg]
    by_lang[lg] = {'articles': len(ks), 'flagged_articles': sum(1 for k in ks if art_res[k]['flagged']),
                   'sents': sum(art_res[k]['n_sents'] for k in ks), 'flagged_sents': sum(len(art_res[k]['flagged']) for k in ks)}
by_tag_art = {t: sum(1 for a in art_res.values() if any(t in ts for (_, _, _, ts) in a['flagged'])) for t in ('neg_absence', 'subj_class', 'neg_subject')}
summary['load'] = {'n_sentences': n_s, 'flagged_sentences': n_f, 'flagged_sentence_rate': n_f / n_s,
                   'flagged_articles': len(flag_art), 'flagged_article_rate': len(flag_art) / len(art_res),
                   'flagged_per_article_mean': n_f / len(art_res), 'flagged_per_article_sorted': per_art,
                   'by_tag_sentences': dict(tagc), 'by_tag_articles': by_tag_art,
                   'by_position': {p: {'flagged': posc[p], 'all': posn[p], 'rate': posc[p] / posn[p]} for p in posn},
                   'by_lang': by_lang}
# 既知NG文・pending文を除いた「NGでない文(未評価含む)」への印
known_ng = {x[:2] for x in known_sent if len(x) == 2}
known_pend = {x[:2] for x in known_sent if len(x) == 3}
fp = [(k, i, s, ts) for k, a in art_res.items() for (i, p, s, ts) in a['flagged'] if (k, i) not in known_ng and (k, i) not in known_pend]
summary['load']['flagged_not_known_ng_or_pending'] = len(fp)
summary['load']['flagged_not_known_ng_rate_of_nonNG_sentences'] = len(fp) / (n_s - len(known_ng) - len(known_pend))
rnd = random.Random(20261008)
sample = rnd.sample(fp, min(10, len(fp)))
summary['fp_sample'] = [{'article': k, 'idx': i, 'sent': s, 'tags': ts, 'detail': sent_flags[(k, i)]['detail']} for k, i, s, ts in sample]
# 型の内訳(サンプルでなく全誤検出のタグ分布)
summary['fp_tag_counts'] = dict(collections.Counter(t for (_, _, _, ts) in fp for t in ts))
summary['flagged_articles_list'] = flag_art

json.dump(summary, open(os.path.join(outdir, 'summary.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=1)
json.dump(item_res, open(os.path.join(outdir, 'items.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=1)
with open(os.path.join(outdir, 'flagged_sentences.jsonl'), 'w', encoding='utf8') as w:
    for k, a in art_res.items():
        for (i, p, s, ts) in a['flagged']:
            w.write(json.dumps({'article': k, 'idx': i, 'pos': p, 'sent': s, 'tags': ts, 'detail': sent_flags[(k, i)]['detail'],
                                'known': 'ng' if (k, i) in known_ng else ('pending' if (k, i) in known_pend else '')}, ensure_ascii=False) + '\n')
print(json.dumps({k: summary[k] for k in ('recall', 'recall_oracle_link', 'other_types_hit(located)')}, ensure_ascii=False, indent=1))
lo = summary['load']
print({k: lo[k] for k in ('n_sentences', 'flagged_sentences', 'flagged_sentence_rate', 'flagged_articles', 'flagged_article_rate', 'flagged_per_article_mean', 'by_tag_sentences', 'by_tag_articles', 'by_lang', 'flagged_not_known_ng_or_pending', 'flagged_not_known_ng_rate_of_nonNG_sentences')})
