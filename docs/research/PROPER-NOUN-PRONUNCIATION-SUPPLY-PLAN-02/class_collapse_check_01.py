"""PNPS-PLAN-02: 決定不要判定(解釈間の共通読み)の机上検証(読取専用・API 0)。
解釈(a)=CMU収録綴り全体の全variant、解釈(b)=CamelCase境界で分割した各語のCMU variantの直積連結。ストレス記号を除去。
受理に使うのは両解釈の共通部分(積集合)のみ。積集合が空、またはどちらかが辞書外なら『判定不能』(調査/HR側へ)。
注意: 計画段階の机上例であり、Productionの判定ではない。公式発音は確定しない。"""
import re, itertools, pronouncing
def strip(p): return tuple(re.sub(r'\d', '', x) for x in p.split())
def vs(w):
    ps = pronouncing.phones_for_word(w.lower()); return [strip(p) for p in ps] if ps else None
def split_camel(w): return [x for x in re.sub(r'([a-z])([A-Z])', r'\1 \2', w).split()]
for w in ['byUs', 'YouTube', 'McCartney', 'KitchenAid', 'iCapital', 'FamilyMart']:
    whole = vs(w); parts = [vs(x) for x in split_camel(w)]
    if whole is None or any(p is None for p in parts):
        print(f"{w}: 全体辞書内={whole is not None} 分割語辞書内={[p is not None for p in parts]} => 判定不能(辞書外を含む)"); continue
    joined = {sum(c, ()) for c in itertools.product(*parts)}
    inter = set(whole) & joined
    print(f"{w}: 全体variant={len(set(whole))} 分割連結variant={len(joined)} 共通={[' '.join(x) for x in sorted(inter)]} 分割側のみ={[' '.join(x) for x in sorted(joined - set(whole))]} => {'共通読みあり(受理は共通部分のみ)' if inter else '判定不能(分岐)'}")
