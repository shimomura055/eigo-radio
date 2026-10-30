# Sonnet(実読)の目視ラベル。LLM(luna/gemini)を一度も呼ぶ前に確定(blind)。kpd04_candidates_blind.jsonの出現順。 e=easy m=medium h=hard r=rare
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
L = {
 'X:coffee-a2': 'm m m h m e m',
 'X:coffee-b1b': 'h e m m m m m m',
 'X:yemen-a2': 'm m m m m m',
 'X:yemen-b1b': 'h m m h m m m m',
 'Y:surname-a2': 'm m m m m e m e m e e',
 'Y:surname-b1b': 'h m m m e m h m m m m m',
 'Z:grove-a2': 'h h m h m m m',
 'Z:grove-b1b': 'h h h m h h h h h',
}
full = {'e': 'easy', 'm': 'medium', 'h': 'hard', 'r': 'rare'}
rows = json.load(open(os.path.join(HERE, 'kpd04_out', 'kpd04_candidates_blind.json'), encoding='utf-8'))
out = {}
for s, v in L.items():
    ids = [r['candidate_id'] for r in rows if r['set'] == s]
    labs = v.split()
    assert len(ids) == len(labs), (s, len(ids), len(labs))
    out[s] = {i: full[l] for i, l in zip(ids, labs)}
json.dump(out, open(os.path.join(HERE, 'kpd04_out', 'kpd04_sonnet_labels.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print({k: len(v) for k, v in out.items()})
