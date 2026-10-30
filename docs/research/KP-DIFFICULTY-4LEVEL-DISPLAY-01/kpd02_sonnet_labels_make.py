# Sonnet(実読)の目視ラベル。LLM結果を見る前に確定(blind)。candidates_blind.jsonの出現順に対応。 e=easy m=medium h=hard r=rare
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
L = {
 'X-a2': 'e m m h m m m e m m',
 'X-b1b': 'm h m m h m m h m m',
 'Y-a2': 'm h h e m m m m',
 'Y-b1b': 'h m h m m h m m m m',
 'Z-a2': 'h m m m m h m m',
 'Z-b1b': 'h h m m m h h m m',
}
full = {'e': 'easy', 'm': 'medium', 'h': 'hard', 'r': 'rare'}
rows = json.load(open(os.path.join(HERE, 'kpd02_out', 'kpd02_candidates_blind.json'), encoding='utf-8'))
out = {}
for s, v in L.items():
    ids = [r['candidate_id'] for r in rows if r['set'] == s]
    labs = v.split()
    assert len(ids) == len(labs), (s, len(ids), len(labs))
    out[s] = {i: full[l] for i, l in zip(ids, labs)}
json.dump(out, open(os.path.join(HERE, 'kpd02_out', 'kpd02_sonnet_labels.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print({k: len(v) for k, v in out.items()})
