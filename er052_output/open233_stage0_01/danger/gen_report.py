# -*- coding: utf-8 -*-
import json, os
OUT = os.path.dirname(os.path.abspath(__file__))
c = json.load(open(OUT + '/coverage.json', encoding='utf8'))
x = json.load(open(OUT + '/extra_rules_trial.json', encoding='utf8'))
items = json.load(open(OUT + '/ng_detail.json', encoding='utf8'))
P3 = ['NEG', 'UNIV', 'SUBJ', 'CAUSE']
P1 = ['NEG', 'UNIV', 'CAUSE', 'NUM', 'LIMIT_HEDGE', 'LIMIT_SCOPE', 'SUBJ']
pc = lambda v: '-' if v is None else f'{v*100:.1f}%'
L = []
w = L.append
w('# DANGER_COVERAGE: 危険文条件の検出率と負荷(OPEN-233-DANGER-SENTENCE-RELATION-CHECK-STAGE0-01 委任_B)')
w('')
w('位置づけ: 規則ベースv0(API不使用、費用0円)の測定のみ。Production未接続・仕様候補であり`APPROVED_FOR_PRODUCTION`ではない。重大/軽微/保留の判定は既存の評価JSONに従い再判定していない(単独評価、人間確認は一部のみ)。成立ライン(検出率80%以上かつ負荷40%以下)は仮置き(Fableが確定)。')
w('')
w('## 0. 対象と方法')
w(f"- 記事{c['n_articles']}本(B3 55 + CCP 18 + RCA 27)。文数 {c['n_sentences']}(JA R2 {c['n_sentences_lang']['ja']} / EN最終 {c['n_sentences_lang']['en']})。title・導入(最初の段落)・本文・締め(最後の段落)・EN一行要約(summary)に位置分類。JAに一行要約は無い。")
w('- 規則: NEG(否定・不在) / UNIV(全称) / CAUSE(因果・時間) / NUM(数値) / LIMIT_HEDGE(台帳factの限定語[一部・約・当面・可能性・のみ・初めて・統合軍等12種]が文に無い) / LIMIT_SCOPE(台帳scope欄の語が文に無い) / SUBJ(主語名詞が台帳に無い。EN側は固有名詞のみ)。実装 `danger_sentence_rules_v0.py`、文ごとの発火は `sentence_flags.jsonl`。')
w('- LIMIT系は台帳factとの対応が必要。負荷計算は語の重なりによる自動リンク(auto)。既知NG文は評価JSONのfact_idを使う版(oracle=指示どおり)と自動リンク版(auto)の両方を測定。`lax`=全文を最上位1factへ強制リンクした場合の負荷(LIMIT系の上限)。')
w('- 既存precheck実装の流用は行っていない(独立実装。流用すれば数値抽出・否定語の精度が上がる可能性)。')
w(f"- 既知NG: 評価JSONのng_items 92件(重大1・軽微91)から、`ai_control-jb9k-03`をユーザー確定の重大へ、`space_weapons-89wf-01`をP8-5/6との重複として除外。これに過去重大8件のうち実在記事に無い7件(`P8-1`〜`P8-7`)を文で追加。結果: 重大8(jb9k-03+P8の7件)、軽微90、保留48。うち最終稿(JA R2またはEN)に存在する重大8・軽微74を主集計、R0のみで最終稿に残らない軽微16を参考集計。保留は評価JSONのpendingから文を曖昧一致で特定(43/48件)。")
w('- NG項目と文の対応は文字列の曖昧一致+手動補正8件(`run_coverage.py` OVERRIDE)。JA由来でEN側の文が特定できない項目はJA文のみで判定(いずれかの文が発火で検出)。EN側未特定は検出率を下げる方向のため保守的。')
w('')
w('## 1. 負荷(全文のうち印が付く割合)')
w('| パターン | 全文 | JA | EN | title | summary | intro | body | closing | 1記事あたり印付き文数(平均/中央/最大) | 記事別割合 平均[min-max] |')
w('|---|---|---|---|---|---|---|---|---|---|---|')
for pn, d in c['load'].items():
    p = d['pos']
    mp = d['marked_per_article']
    a = d['article']
    w(f"| {pn} | {pc(d['all'])} | {pc(d['ja'])} | {pc(d['en'])} | {pc(p['title'][0])} | {pc(p['summary'][0])} | {pc(p['intro'][0])} | {pc(p['body'][0])} | {pc(p['closing'][0])} | {mp['mean']:.1f}/{mp['median']}/{mp['max']} | {pc(a['mean'])} [{pc(a['min'])}-{pc(a['max'])}] |")
w(f"- 文数: title {c['load']['P1_全規則']['pos']['title'][1]} / summary {c['load']['P1_全規則']['pos']['summary'][1]} / intro {c['load']['P1_全規則']['pos']['intro'][1]} / body {c['load']['P1_全規則']['pos']['body'][1]} / closing {c['load']['P1_全規則']['pos']['closing'][1]}。")
w('')
w('### 規則別の負荷(単独)と単独検出率(重大+軽微の最終稿NG 82件)')
w('| 規則 | 負荷(全文) | JA | EN | 検出率auto | 検出率oracle | 検出/負荷(auto) |')
w('|---|---|---|---|---|---|---|')
for r, d in c['rule_load'].items():
    s = c['single_rule_detection'][r]
    w(f"| {r} | {pc(d['all'])} | {pc(d['ja'])} | {pc(d['en'])} | {pc(s['auto'])} | {pc(s['oracle'])} | {s['auto']/d['all']:.2f} |")
w('- 検出/負荷が1に近い規則は「ランダムに文を選ぶのと変わらない」。NEG(1.1)・NUM(1.4)・SUBJ(1.4)は弁別力が低く、LIMIT_HEDGE(auto 2.3)・CAUSE(1.9)・UNIV(2.0)がやや高い。基準: 82件はおよそ全文の1.4%(NG文の事前確率)。')
w('')
w('### 規則別の位置別負荷')
w('| 規則 | title | summary | intro | body | closing |')
w('|---|---|---|---|---|---|')
for r, d in c['rule_pos'].items():
    w(f"| {r} | {pc(d['title'])} | {pc(d['summary'])} | {pc(d['intro'])} | {pc(d['body'])} | {pc(d['closing'])} |")
w('- SUBJ(主語新規)はtitleで59%と突出(題名は主語助詞を含まない名詞句が多く、固有表現・造語が多い)。titleとsummaryは全規則でも高負荷。')
w('')
w('## 2. 検出率(既知NG文のうち危険文と判定される割合)')
w('| パターン | 重大(8) auto/oracle | 軽微(74) auto/oracle | 重大+軽微(82) auto/oracle | 保留(43) | R0のみ軽微(16,参考) auto/oracle |')
w('|---|---|---|---|---|---|')
for pn, d in c['detection'].items():
    a, o = d['auto'], d['oracle']
    w(f"| {pn} | {a['重大']['detected']}/{a['重大']['n_matched']} / {o['重大']['detected']}/{o['重大']['n_matched']} | {pc(a['軽微']['rate'])} / {pc(o['軽微']['rate'])} | {pc(a['重大+軽微']['rate'])} / {pc(o['重大+軽微']['rate'])} | {pc(a['保留']['rate'])} | {pc(a['R0のみ軽微(参考)']['rate'])} / {pc(o['R0のみ軽微(参考)']['rate'])} |")
w('- 保留はfact参照が無いためautoのみ。')
w('')
w('### 文種(評価JSONの`kind`)別・言語別の検出率(重大+軽微、oracle)')
kinds = sorted({k for d in c['detection'].values() for k in d['by_kind_oracle']})
w('| パターン | ' + ' | '.join(f'{k}' for k in kinds) + ' | JA文 | EN文 |')
w('|---|' + '---|' * (len(kinds) + 2))
for pn, d in c['detection'].items():
    cells = []
    for k in kinds:
        v = d['by_kind_oracle'].get(k)
        cells.append(f"{v['detected']}/{v['n']}" if v else '-')
    bl = d['by_lang_oracle']
    w(f"| {pn} | " + ' | '.join(cells) + f" | {bl['ja']['detected']}/{bl['ja']['n']} | {bl['en']['detected']}/{bl['en']['n']} |")
w('')
w('## 3. トレードオフ(規則の組合せ)')
w('| パターン | 負荷 | 検出率(重大+軽微) auto | oracle | 仮ライン(検出>=80%かつ負荷<=40%) |')
w('|---|---|---|---|---|')
for pn, d in c['detection'].items():
    ld = c['load'][pn]['all']
    a = d['auto']['重大+軽微']['rate']
    o = d['oracle']['重大+軽微']['rate']
    ok = 'oracleのみ検出OKだが負荷NG' if (o >= 0.8 and ld > 0.4) else ('未達' if a < 0.8 else ('達成' if ld <= 0.4 else '負荷NG'))
    w(f"| {pn} | {pc(ld)} | {pc(a)} | {pc(o)} | {ok} |")
fr = c['frontier']
w('')
w('### 全部分集合(2^7-1=127通り)の探索')
w(f"- 仮ライン(検出80%以上かつ負荷40%以下)を満たす組合せ: auto(自動リンク) **{len(fr['passing_auto'])}通り**、lax(全文を最上位1factへ強制リンク) **{len(fr['passing_lax'])}通り**、oracle(既知NGのみ正しいfactリンク) {len(fr['passing_oracle'])}通り。")
w('- oracleの{0}通りは「既知NG文にだけ正しいfactを付けた」上限値で、負荷側は自動リンクのため整合しない参考値(全文に正しいfactリンクが付くなら成立し得る、という意味にとどまる)。'.format(len(fr['passing_oracle'])))
w('- 負荷40%以下での最大検出率(auto): ' + '; '.join(f"{r['rules']} 負荷{pc(r['load'])}/検出{pc(r['det_auto'])}(oracle {pc(r['det_oracle'])})" for r in fr['best_auto_load_le_40'][:3]))
w('- 負荷50%以下での最大検出率(auto): ' + '; '.join(f"{r['rules']} 負荷{pc(r['load'])}/検出{pc(r['det_auto'])}" for r in fr['best_auto_load_le_50'][:2]))
w('- lax(全文強制リンク)では、LIMIT系は1文を必ずどれかのfactに紐づけるため負荷が跳ね上がる: ' + '; '.join(f"{r['rules']} 負荷{pc(r['load_lax'])}/検出{pc(r['det_lax'])}" for r in fr['best_lax_load_le_40'][:3]) + '(負荷40%以下に収まる組合せの最大検出率)。')
w('')
w('## 4. 見逃し一覧(P3=否定+全称+主語新規+因果時間 で危険文と判定されない重大+軽微21件)')
w('P3はfactリンク不要の規則のみ。右3列は、同じ文がP1(全規則)で拾われるか(auto/oracle)を示す。型: T1=台帳外の具体化(新規内容語)、T2=指示語・方向語(「この機能」「元に戻す」)、T3=複数fact連結、T4=主体・視点のずれ・規則外、T5=数・比較基準、T6=無関係文の挿入。')
W = {
    'meta-j7e5-01': ('T4', '複数fact(HC-011の報告内容とMetaの依頼)を1文に連結し主体を取り違える。規則では拾えない(文をまたぐ暗黙関係)'),
    'meta-p9ng-01': ('T1', '台帳「適切な開示」の中身(誰が対応/情報共有)を具体化。台帳外内容語の新規率ルール(NOVEL)で一部拾える可能性、完全には不可'),
    'meta-p9ng-02': ('T1', '機微情報の具体例(予定・希望)を追加。台帳外名詞の新規率ルール'),
    'meta-rweb-02': ('T1', '「AIだけでは難しい」という理由の追加。台帳外の評価語・理由語ルール'),
    'meta-sccn-01': ('T4', '利用者を通話当事者に置く視点・役割割当。語彙規則では拾えない'),
    'meta-v6r6-01': ('T2', '「この機能」の指示対象と戻す方向が不明。DIRWORD(戻す/ロールバック)+ANAPHで拾える(auto P1ではLIMIT_HEDGE偶発)'),
    'meta-x5wg-01': ('T2', '同上(「この機能」+ロールバック)'),
    'meta-x5wg-02': ('T4', '「AIに話していると思っている」主体(利用者/相手)のずれ+断定。語彙規則では拾えない(「可能性」消失のLIMIT_HEDGEが偶発で拾う)'),
    'space_weapons-wyg2-03': ('T5', '単一事例(2021年COSMOS 1408)を過去一般(複数)へ。「In the past」+過去形の一般叙述ルールまたは台帳の件数・日付限定語の消失'),
    'meta-249j-01': ('T2', '「この機能」+戻す+未来形(出来事は過去)。DIRWORD+ANAPH+時制ルール'),
    'meta-jdmu-01': ('T3', 'HC-009とHC-008を同一報告として連結。1文が2fact以上にリンクするMULTIFACTで拾える'),
    'meta-n6vy-01': ('T2', '「戻された」の方向が確定しない。DIRWORDで拾える'),
    'meta-qvqc-01': ('T2', '「元に戻された」(方向不明)。DIRWORDで拾える'),
    'meta-ua6f-02': ('T2', '「ロールバック」(方向不明)。DIRWORDで拾える'),
    'space_weapons-4mjq-01': ('T3', 'F-015の任務(監視・ミサイル追跡)をF-011の定義へ混入。「含まれる」型INCL+MULTIFACTで拾える可能性(oracleのfact参照では拾えない=評価JSONのfact_idが片方のみ)'),
    'hormuz-j7gv-01': ('T1', '「船が通るたびに…払う」で徴収方法を具体化。頻度語(たびに/each time)をUNIV系へ追加で拾える'),
    'hormuz-kbds-01': ('T4', '「for the United States」の受益者/主体の係り先が曖昧。前置詞句の係り受け解析が必要で規則では不可'),
    'hormuz-qc67-01': ('T5', '「前日比」という比較基準の付加。NUM規則(数値)で拾える(P1では発火)'),
    'meta-78bg-01': ('T1', 'p9ng-02と同型(予定・希望の具体例)'),
    'meta-78bg-02': ('T1', 'p9ng-01と同型(公開条件の具体化)'),
    'P8-4 ai-p2r2-07': ('T6', 'Rewriteが挿入した無関係文(Opus 4の脅迫84%)。どのfactにもリンクしない+数値を含む文、というUNLINKED+NUMで拾える(NUM規則で発火)'),
}
w('| ID | 重大/軽微 | kind | 文(JAまたはEN) | P1 auto | P1 oracle | 型 | どの規則を足せば拾えるか/規則外か |')
w('|---|---|---|---|---|---|---|---|')
def det(it, rules, mode):
    return any(any(x in m[mode] for x in rules) for m in it['m'].values())
types = {}
cnt = 0
for it in items:
    if it['src'] == 'pending' or it['sev'] == 'dup_of_P8' or it['r0_only'] or not it['m']:
        continue
    if det(it, P3, 'auto'):
        continue
    cnt += 1
    sent = ' / '.join(m['sent'] for m in it['m'].values())
    if len(sent) > 110:
        sent = sent[:110] + '...'
    t, why = W.get(it['id'], ('?', ''))
    types.setdefault(t, []).append(it['id'])
    b = '重大' if (it['src'] == 'past8' or it['sev'] == 'major_human') else '軽微'
    w(f"| {it['id']} | {b} | {it['kind']} | {sent} | {'拾う' if det(it, P1, 'auto') else '見逃し'} | {'拾う' if det(it, P1, 'oracle') else '見逃し'} | {t} | {why} |")
w('')
w(f"- 型別件数: " + ', '.join(f"{t}={len(v)}" for t, v in sorted(types.items())) + f" (計{cnt})。")
w('- P1(全規則)でも拾えないのは oracle で2件(`meta-j7e5-01`=T4、`space_weapons-4mjq-01`=T3)、auto で ' + str(sum(1 for it in items if it['src'] != 'pending' and it['sev'] != 'dup_of_P8' and not it['r0_only'] and it['m'] and not det(it, P1, 'auto'))) + '件。')
w('- 見逃し型トップ3(P3基準): (1) T1 台帳外の具体化(6件)・(1) T2 指示語/方向語(6件、同数1位)、(3) T4 主体・視点のずれ(4件、規則では拾えない型)。')
w('- 規則では拾えない型(T4): 4件(見逃し21件の19%)。ほかのT1〜T3・T5・T6(17件)は規則追加で拾える見込み(下の試算)。')
w('')
w('## 5. 規則改善案と追加規則の試算(`run_extra_rules.py`、`extra_rules_trial.json`)')
w('| 追加規則 | 内容 | 負荷(全文) | 82件中の検出 | P3見逃し21件のうち拾える数 |')
w('|---|---|---|---|---|')
desc = {'DIRWORD': '戻す/元に/ロールバック/撤回/置き換え等の方向語(EN: rolled back/put back/returned)', 'ANAPH': '「この/その+名詞」が主語・目的語(EN: this feature等)',
        'FREQ': 'たびに/ごとに/each time', 'INCL': '含まれる/含む/まとめて(EN: includes)', 'NOVEL2': '台帳に出ない内容語(3字以上)が2語以上', 'NOVEL3': '同3語以上', 'MULTIFACT': '1文が2fact以上にリンク'}
for k in ('DIRWORD', 'ANAPH', 'FREQ', 'INCL', 'NOVEL2', 'NOVEL3', 'MULTIFACT'):
    v = x[k]
    w(f"| {k} | {desc[k]} | {pc(v['load'])} | {pc(v['det_all'])} | {v['rescued_of_P3_missed']} |")
w('')
w('- 追加規則は負荷が低い(各2〜7%)が、現在の高負荷(NEG 27%・SUBJ 27%・CAUSE 18%)を下げないと全体は40%以下にならない。P3に追加しても負荷61〜66%/検出82〜85%。')
w('- 基本7規則+追加6規則の部分集合探索(auto、負荷40%以下): 最大検出率 ' + pc(x['ext_best_le40'][0]['det']) + f"({x['ext_best_le40'][0]['rules']}、負荷{pc(x['ext_best_le40'][0]['load'])})。負荷30%以下では最大 {pc(x['ext_best_le30'][0]['det'])}。仮ライン達成は " + str(len(x['ext_passing'])) + '通り。')
w('- 改善案(優先順): (1) NEG/SUBJ/CAUSEの絞り込み(NEGは「ていない・されていない・ありません」等の存在否定に限定、SUBJはtitle除外とEN側の語彙拡張、CAUSEは因果語のみ[ため/により/その結果/because/led to]へ限定し時間語[後/前/直後/after/before]は別扱い)。(2) factリンクの精度向上(Writer/LLMが文ごとにfact_idを付ける、または台帳のfactキーワード辞書)。LIMIT系の検出力はリンク精度に依存(auto 63%対oracle 94%)。(3) DIRWORD+ANAPH+MULTIFACT+INCLの追加(T2・T3を拾う)。(4) T4(主体・視点・受益者のずれ)は語彙規則の外。LLM判定または文ペア関係検査が必要。')
w('')
w('## 6. 判断材料の要約(仮の成立ライン: 検出率80%以上かつ負荷40%以下)')
b = c['detection']
w('- 自動リンクのv0規則では、成立する組合せは0通り。負荷40%以下で届く最大検出率は約65%(CAUSE+NUM+LIMIT_HEDGE+LIMIT_SCOPE、負荷39.5%)。')
w('- 検出率80%以上に届く組合せ(P1全規則 auto 86.6%、P4 86.6%、P5 85.4%)は負荷が67〜71%で、全文の7割に印が付く=「危険文限定」の趣旨(絞り込み)を満たさない。')
w('- oracle(正しいfactリンクが付く前提)では9通りが成立(例: UNIV+CAUSE+LIMIT_HEDGE+LIMIT_SCOPE 負荷37.6%/検出93.9%)。ただし負荷はautoリンクの値で、全文に正しいfactリンクを付けた場合の負荷は未測定(laxでは40%以下の最大検出が約60%)。')
w('- 結論の読み方: 「条件による危険文の絞り込み」はfactリンク(文→台帳fact)の精度が鍵。語彙規則だけでは負荷が下がらず、検出率80%と負荷40%の両立は未達。重大8件はP1/P4で8/8、P3で7/8、P2で6/8拾える(重大は拾えるが、軽微を含めると負荷が許容を超える)。')
w('')
w('## 7. 限界')
w('- サンプル: 重大8は件数が少なく(うち7件は評価JSON外の記事の文)、割合の誤差が大きい。軽微の判定は単独評価で境界のぶれがある(REPORT §100-5)。')
w('- 検出率はNG文のみの測定で、NG文の「周辺の文」の印付きは負荷に含まれる。NGの総数が少ない(全文の1.4%)ため、どの規則も精度(印付き文のうちNGの割合)は2%前後。')
w('- EN側の主語新規は固有名詞のみ、EN側のfactリンクは英語トークンの重なりのみ(台帳が日本語のため精度低)。ENのLIMIT系検出は過小評価の可能性。')
w('- 一部NG文の特定は曖昧一致。JA由来の項目でEN文が特定できないものはJA文のみで判定。R0のみ16件は最終稿に残らないため主集計から除外(参考表示)。')
w('- `meta-475j-01`(軽微)と`P8-1`(重大)は同一文で評価者判定が分かれたもの。両方を集計に含む。')
w('- 本測定はAPI不使用(費用0円)。LLM分類は未使用。')
open(OUT + '/DANGER_COVERAGE.md', 'w', encoding='utf8').write('\n'.join(L) + '\n')
print('written', len(L))
