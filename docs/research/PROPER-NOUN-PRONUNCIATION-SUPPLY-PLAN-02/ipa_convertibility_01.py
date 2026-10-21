"""PNPS-PLAN-02: 既存Ledger(38件)のIPAを、M1の既存変換器(ipa_to_arpa、新しい近似なし)でARPAbet化できる割合(読取専用・API 0)。"""
import json, sys, os
sys.path.insert(0, os.getcwd())
import er006_m1_multi_candidate_01 as m1
L = json.load(open('er006_output/pronunciation_ledger_01/ledger.json', encoding='utf8'))
tot = conv = noipa = 0; fails = []
for k, e in L.items():
    raws = [e.get('expected_pronunciation_ipa') or ''] + list(e.get('alternate_pronunciations') or [])
    segs = []
    for r in raws: segs += [s for s, why in m1._ipa_segments(r) if not why]
    if not segs: noipa += 1; continue
    ok = [m1.ipa_to_arpa(s) for s in segs]
    tot += 1
    if any(o is not None for o in ok): conv += 1
    else: fails.append((e['surface'], segs[:2]))
print(f"entries={len(L)} IPA無し(または非英語ラベルのみ)={noipa} IPAあり={tot} 1つ以上ARPAbet化できた={conv} 全て変換不能={tot-conv}")
for s, g in fails: print('  変換不能:', s, g)
