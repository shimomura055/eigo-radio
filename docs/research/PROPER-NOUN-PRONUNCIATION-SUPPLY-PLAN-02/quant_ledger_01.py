"""PNPS-PLAN-02: 現行Pronunciation Ledger(38 entry)の棚卸し(読取専用・API 0)。"""
import json, collections, pronouncing, unicodedata
L = json.load(open('er006_output/pronunciation_ledger_01/ledger.json', encoding='utf8'))
def fold(s): return ''.join(c for c in unicodedata.normalize('NFKD', s.lower()) if not unicodedata.combining(c))
c = collections.Counter(); rows = []
for k, e in L.items():
    ws = fold(e['surface']).split()
    cmu = all(bool(pronouncing.phones_for_word(w)) for w in ws)
    ipa = bool((e.get('expected_pronunciation_ipa') or '').strip())
    c['total'] += 1; c['cmu_all_tokens'] += cmu; c['has_en_ipa'] += ipa
    c['disabled'] += bool(e.get('ledger_disabled')); c['tts_inj_disabled'] += bool(e.get('tts_injection_disabled'))
    c['conf_' + e['confidence']] += 1; c['type_' + e['entity_type']] += 1
    c['has_sources'] += bool(e.get('sources')); c['sources_len_15'] += (len(e.get('sources') or []) == 15)
    c['has_quote_field'] += ('quote' in e); c['has_human_approved_field'] += ('human_approved' in e)
    rows.append((e['surface'], e['entity_type'], e['confidence'], int(cmu), int(ipa), len(e.get('sources') or [])))
print(dict(c))
fs = collections.Counter(fold(e['surface']) for e in L.values())
print('surface duplicated across entity_type:', {k: v for k, v in fs.items() if v > 1})
