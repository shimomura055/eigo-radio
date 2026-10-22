# -*- coding: utf-8 -*-
"""Stage 1 効果測定(API 0・Web 0・保存データ再集計のみ)+M1候補集合不変replay。実行: .venv/Scripts/python.exe <this>"""
import collections, datetime as dt, hashlib, json, re, sys, os
sys.path.insert(0, os.getcwd())
import er097_pronunciation_supply_stage1_01 as s1
import er006_m1_multi_candidate_01 as m1

LEDGER = 'er006_output/pronunciation_ledger_01/ledger.json'
HRQ = 'er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl'
AH = 'er011_output/attempt_history.jsonl'
L = json.load(open(LEDGER, encoding='utf8'))
print('ledger sha256', s1.sha256_file(LEDGER), 'entries', len(L))
rows = [json.loads(l) for l in open(HRQ, encoding='utf8')]
real = [r for r in rows if 'Temp' not in r['wav_path'] and 'tmp' not in r['wav_path'].lower()]
def art(p):
    p = p.replace(chr(92), '/'); m = re.match(r'(er\d+_output/[^/]+/[^/]+)', p); return m.group(1) if m else p[:40]
print('HR queue rows', len(rows), 'real-path rows', len(real), 'rows with pronunciation_lookups', sum(1 for r in real if r.get('pronunciation_lookups')))

# ---- (A) span単位: 18 distinct spans / 24 (記事群,語) pairs
pairs = collections.defaultdict(list)
for r in real:
    for w, info in (r.get('pronunciation_lookups') or {}).items():
        pairs[(art(r['wav_path']), w)].append(r['timestamp'])
spans = sorted({w for _, w in pairs})
print('distinct spans', len(spans), 'pairs', len(pairs))
# Stage 1適用判断: そのspanが「まだLedgerに無い(=最初の調査)」状態をLedger空で再現
rec = {}
for w in spans:
    d = s1.decide_span_action(w, {}, None, now=dt.datetime(2026, 10, 22))
    rec[w] = d['action']
cnt = collections.Counter(rec.values())
print('first-research decision per span (empty ledger):', dict(cnt))
print('  SKIP_GENERAL spans:', [w for w, a in rec.items() if a == s1.ACTION_SKIP_GENERAL])
print('  RESEARCH spans    :', [w for w, a in rec.items() if a == s1.ACTION_RESEARCH])
# 現在のLedgerで再判定(= Stage1適用後の将来挙動): 隔離/命中/一般語
cur = {w: s1.decide_span_action(w, L, None, now=dt.datetime(2026, 10, 22))['action'] for w in spans}
print('decision with CURRENT ledger:', dict(collections.Counter(cur.values())))
# 取りこぼし解消(別entity_type命中): 旧lookup=cascade fixed key想定
def old_hit(w):
    return any(e['entity_type'] == 'cascade_unresolved_entity' and e['surface'].strip().lower() == w for e in L.values())
def new_hit_other_type(w):
    e, meta = s1.unified_lookup(L, w)
    return bool(e) and e['entity_type'] != 'cascade_unresolved_entity' and not old_hit(w)
print('spans where unified lookup newly hits (old miss, other type hit):', [w for w in spans if new_hit_other_type(w)])
print('Ledger-wide: surfaces with >=2 entity types:', {k: v for k, v in collections.Counter(
    s1.norm_surface(e['surface']) for e in L.values()).items() if v > 1})
# 理論上の取りこぼし(同綴り別type=person/place等のentryに対し旧lookupは常にmiss): ledger内の非cascade・非JA entry
oth = [e['surface'] for e in L.values() if e['entity_type'] not in ('cascade_unresolved_entity', 'ja_reading_katakana')]
print('non-cascade EN entries that old lookup could never hit:', len(oth), oth)

# ---- (B) 研究呼出ログ(実測ログの件数。単価は未確認)
import subprocess
files = [f for f in subprocess.run(['grep', '-rl', '--include=*.jsonl', 'pronunciation_research', '.'], capture_output=True, text=True).stdout.split() if 'venv' not in f]
seen, calls = set(), []
for f in files:
    for l in open(f, encoding='utf8', errors='ignore'):
        if '"pronunciation_research"' not in l: continue
        try: d = json.loads(l)
        except Exception: continue
        if d.get('api') != 'pronunciation_research': continue
        k = (d.get('timestamp'), d.get('total_tokens'), d.get('elapsed_seconds'))
        if k in seen: continue
        seen.add(k); calls.append(d)
print('logged pronunciation_research calls (dedup)', len(calls), 'success', sum(1 for c in calls if c.get('success')),
      'single-item', sum(1 for c in calls if c.get('items_returned') == 1), 'items=0', sum(1 for c in calls if c.get('items_returned') == 0),
      'total_tokens', sum(c.get('total_tokens') or 0 for c in calls))

# ---- (C) HR表示改善: HR行(real)でlookupsに一般語spanを含む行
gen = {w for w in spans if s1.is_general_word_span(w)}
hr_rows_gen = [r for r in real if any(w in gen for w in (r.get('pronunciation_lookups') or {}))]
print('general-word spans', sorted(gen), '-> HR rows whose lookup was about a general word:', len(hr_rows_gen), '/', sum(1 for r in real if r.get('pronunciation_lookups')))
junk = [w for w in gen if any(e['surface'].lower() == w and (e.get('ledger_disabled')) for e in L.values())]
print('general spans already isolated(ledger_disabled) by OPEN-436:', sorted(junk), ' not isolated (valid-looking entry):', sorted(gen - set(junk)))

# ---- (D) M1候補集合不変replay: 現Ledger vs Stage1相当Ledger(一般語cascade entryを持たない)
def stage1_ledger(Ld):
    out = {}
    for k, e in Ld.items():
        if e['entity_type'] == 'cascade_unresolved_entity' and s1.is_general_word_span(e['surface']):
            continue
        out[k] = e
    return out
L1 = stage1_ledger(L)
removed = len(L) - len(L1)
texts = {r['canonical_text'] for r in rows}
for l in open(AH, encoding='utf8'):
    if not l.strip(): continue
    try: d = json.loads(l)
    except Exception: continue
    if isinstance(d.get('canonical_text'), str): texts.add(d['canonical_text'])
texts |= {e['surface'] for e in L.values()}
diff = 0; oov_words = 0
for t in texts:
    a = m1.freeze_candidates(t, ledger_snapshot=L, segment_started_at=None)
    b = m1.freeze_candidates(t, ledger_snapshot=L1, segment_started_at=None)
    if a.candidate_set_hash != b.candidate_set_hash:
        diff += 1
    oov_words += sum(1 for w in a.words if not any(c.source == 'C1_cmu_variant' for c in w.candidates))
print(f'M1 replay: ledger entries removed (general cascade)={removed}; texts={len(texts)}; candidate_set_hash differing={diff}; OOV words seen={oov_words}')
# 統一lookupで追加される/消える候補: 追加するentryは無い(lookupは読取専用)ため M1入力Ledgerは不変

# ---- (E) Phrase List(Secondary ASRへ渡る語句)経由の間接影響: get_hint_for_text(min_confidence="low")のLedger差し替えreplay
import er006_pronunciation_ledger_01 as pl
def phrases(Ld, text):
    orig = pl._load
    pl._load = lambda: Ld
    try:
        return sorted(h['canonical_spelling'] for h in pl.get_hint_for_text(text, min_confidence='low'))
    finally:
        pl._load = orig
dphr = []
for t in texts:
    a, b = phrases(L, t), phrases(L1, t)
    if a != b:
        dphr.append((t[:60], sorted(set(a) - set(b))))
print(f'PhraseList replay: texts={len(texts)} differing={len(dphr)}', dphr[:5])
print('Phrase List contribution of removed entries (current ledger, low+): ',
      sorted((e['surface'], e['confidence'], bool(e.get('ledger_disabled'))) for k, e in L.items() if k not in L1))
