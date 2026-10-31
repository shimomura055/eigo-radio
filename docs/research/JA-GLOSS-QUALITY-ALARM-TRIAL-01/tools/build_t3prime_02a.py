# -*- coding: utf-8 -*-
"""委任_02A (M-2): 巧妙型の合成T3' を eval_set/items.json に追加(冪等: 既存のtier=T3Pを除去してから追加)。API 0。
作成規則は TRIAL_PLAN_02.md / T3PRIME_RULES_02.md に固定済み(特定語を狙わない: 下の選定アルゴリズムで機械的に選ぶ)。
選定アルゴリズム(文書化): 各類型の適用基準を満たす承認済みT2項目のうち、(a)T1の表現・T3の置換元・裁定でproblemになった項目を除き、
(b)T2のid昇順で、dev/held-out(記事単位の分割)を交互に、同一表現は1回までで、類型ごと4件(dev2+held-out2)選ぶ。
置換後の訳(GLOSS)は類型ごとの変換規則を機械的に適用した結果を人手で記述したもの(下の表)。"""
import json, os, hashlib

R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
IT = os.path.join(R, 'eval_set', 'items.json')
RULE = {
    2: ('C2', '辞書第一義への一般化', '文脈上の語義でなく、主要語の辞書第一義(最頻義)へ差し替える。品詞・文型は元訳に合わせ、見た目を自然に保つ'),
    3: ('C3', '比喩・物語像の喪失(平板化)', '比喩・婉曲・含みのある語句を、含意を落とした字義/平板な訳へ置換し、意味(含意)が変わるようにする'),
    4: ('C4', '定訳・専門用語の不適切な言い換え', '定訳のある語を、近縁だが指す対象が異なる別語(または別範疇の語)へ置換する'),
    5: ('C5', '日本語の不自然・冗長・分かりにくさ', '意味は変えず、冗長な言い回し・不要な迂言・説明過剰で訳語として不自然にする(minor)'),
}
# (T2 id, category, severity, 置換後の訳)
SPEC = [
    ('JAQ-T2-006', 2, 'major', '偏見をもった'),
    ('JAQ-T2-022', 2, 'major', '新聞や雑誌の購読'),
    ('JAQ-T2-042', 3, 'major', '質問の場になる'),
    ('JAQ-T2-008', 3, 'major', 'そのように見えた'),
    ('JAQ-T2-040', 4, 'major', 'ゴミ'),
    ('JAQ-T2-005', 4, 'major', '広告'),
    ('JAQ-T2-051', 5, 'minor', '結果的に最終的には受け取るという形に落ち着いてしまう'),
    ('JAQ-T2-050', 5, 'minor', 'その人にとって都合がよいと言えるような状況であるときに'),
    ('JAQ-T2-055', 2, 'major', '採用された'),
    ('JAQ-T2-083', 2, 'major', '出入りを禁じる'),
    ('JAQ-T2-075', 3, 'major', '自分にふさわしいものを手に入れる'),
    ('JAQ-T2-028', 3, 'major', '押し合いの試合'),
    ('JAQ-T2-012', 4, 'major', '周波数'),
    ('JAQ-T2-078', 4, 'major', '白人の'),
    ('JAQ-T2-074', 5, 'minor', '誰かを説得することによって、その人がその場に残るという状態にしてもらう'),
    ('JAQ-T2-081', 5, 'minor', 'それよりも先の方向へと進むという行為をしない'),
]
items = json.load(open(IT, encoding='utf8'))
items = [x for x in items if x['tier'] != 'T3P']
byid = {x['id']: x for x in items}
new = []
for n, (sid, cat, sev, gloss) in enumerate(SPEC):
    s = byid[sid]
    assert s['tier'] == 'T2'
    code, name, rule = RULE[cat]
    x = dict(s)
    x.update(id='JAQ-T3P-%03d' % (116 + n), tier='T3P', label='problem', severity=sev, category=cat, category_name_ja=name,
             rule_id=code, current_ja=gloss, synthetic_of=s['current_ja'], synthetic_of_id=sid,
             must_not_share_batch_with=[sid], existing_explanation_ja=None, existing_sentence_ja=None,
             source="合成T3'(巧妙型・人手作成、委任_02A。規則 " + code + ")", item_kind='vocab(synthetic-T3p)',
             note="合成T3': 承認済み正常訳『" + s['current_ja'] + "』を類型" + str(cat) + '(' + name + ')の規則で置換。元のT2と同じバッチに入れない')
    new.append(x)
items += new
json.dump(items, open(IT, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
print(len(items), len(new))
for x in new:
    print(x['id'], x['split'], x['category'], x['severity'], x['expression'], x['synthetic_of'], '=>', x['current_ja'])
sp = os.path.join(R, 'eval_set', 'summary.json')
sm = json.load(open(sp, encoding='utf8'))
sm['t3prime_added_02a'] = dict(total=len(new), by_split={s: sum(1 for x in new if x['split'] == s) for s in ('dev', 'held_out')},
                               by_category={str(c): sum(1 for x in new if x['category'] == c) for c in (2, 3, 4, 5)},
                               note='total(115)は委任_01のT1〜T4。T3Pは別掲(tier=T3P)。items.jsonの総数は131')
json.dump(sm, open(sp, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
