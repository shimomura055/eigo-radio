# -*- coding: utf-8 -*-
"""rev01-d: DEV data に仮ニュアンス解説を追加(02C実機証拠の採用1件fragmentを流用。DEVページdataのみ)。"""
import json, re, os
R = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
EV = R + '/docs/research/NUANCE-EXPLANATION-PRODUCTION-WIRING-01/evidence/'
D = R + '/user_test/dev_enduser_page_01/data/'
SRC = {'std': 'X_nxm1_std_adopt_adv_reject__standard__nuance_fragment.html', 'adv': 'X_nxm2_std_reject_adv_adopt__advanced__nuance_fragment.html'}
def parse(fn):
    h = open(EV + fn, encoding='utf8').read()
    items = []
    for m in re.finditer(r"<div class='study-item'><h4>(.*?)</h4><dl>(.*?)</dl></div>", h, re.S):
        fields = [{'label': a, 'html': b} for a, b in re.findall(r'<dt>(.*?)</dt><dd>(.*?)</dd>', m.group(2), re.S)]
        items.append({'heading': m.group(1), 'fields': fields})
    assert len(items) == 1, fn
    return items
for aid, lvs in (('ai_island', ('std', 'adv')), ('moon', ('adv',))):
    p = D + aid + '.json'
    d = json.load(open(p, encoding='utf8'))
    for lv in lvs:
        L = d['levels'][lv]
        L['nuance'] = parse(SRC[lv]); L['nuance_source'] = 'placeholder_for_layout_check'
        L['nuance_placeholder_from'] = SRC[lv]
    json.dump(d, open(p, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    print(aid, lvs)
