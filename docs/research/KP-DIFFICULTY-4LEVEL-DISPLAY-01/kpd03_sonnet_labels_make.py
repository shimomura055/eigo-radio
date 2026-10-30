# Sonnet(実読)の目視ラベル。LLM(luna/gemini)を一度も呼ぶ前に確定(blind)。kpd03_candidates_blind.jsonの出現順。 e=easy m=medium h=hard r=rare
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
L = {
 'X-a2': 'm m m m m e m e',
 'X-b1b': 'm h m e m m e m e m m m',
 'Y-a2': 'm m h m h m e e',
 'Y-b1b': 'm m m h m h',
 'Z-a2': 'h m h e m m m m h',
 'Z-b1b': 'h h h m m h m h h',
}
full = {'e': 'easy', 'm': 'medium', 'h': 'hard', 'r': 'rare'}
rows = json.load(open(os.path.join(HERE, 'kpd03_out', 'kpd03_candidates_blind.json'), encoding='utf-8'))
out = {}
for s, v in L.items():
    ids = [r['candidate_id'] for r in rows if r['set'] == s]
    labs = v.split()
    assert len(ids) == len(labs), (s, len(ids), len(labs))
    out[s] = {i: full[l] for i, l in zip(ids, labs)}
json.dump(out, open(os.path.join(HERE, 'kpd03_out', 'kpd03_sonnet_labels.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print({k: len(v) for k, v in out.items()})
