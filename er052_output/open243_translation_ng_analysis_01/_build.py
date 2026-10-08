# OPEN-243-TRANSLATION-NG-ANALYSIS-01 build script (read-only on existing artifacts, API cost 0)
# usage: python er052_output/open243_translation_ng_analysis_01/_build.py   (run from repo root)
# input : _all_ng_raw.json (Trial A/B judgments resolved through MAP.json; created by an inline collection step)
# output: items.jsonl
import json, glob, re, os, collections
BS = chr(92)
OUT = 'er052_output/open243_translation_ng_analysis_01'
raw = json.load(open(OUT + '/_all_ng_raw.json', encoding='utf8'))

# ---------- manual annotations: idx -> origin/type/position/cause/ja_corr/note ----------
# origin: translation=翻訳段由来 / ja=JA由来 / amplified=翻訳で増幅
# type: subject/number/scope/causal/strength/addition/term/tense/other
A = {}
def a(idxs, origin, typ, loc, cause, ja=None, note=''):
    for i in (idxs if isinstance(idxs, (list, tuple)) else [idxs]):
        A[i] = dict(origin=origin, type=typ, loc=loc, cause=cause, ja_corr=ja, note=note)

# --- EN_ONLY (judge: in_r0=false, in_r2=false, in_en=true) ---
a([0, 5, 109], 'translation', 'number', 'body', 'number_unmarked(機関=集合名詞,単複無標)', '米政府機関は、宇宙軍による宇宙への兵器配備を初めて認めた発言として記録した', 'JA「米政府機関」は数無標。ENで "agencies" と複数形化。台帳F-001は単一の公式記事')
a([7, 126], 'translation', 'tense', 'body', 'tense_marker(「超えました」->"There are now")', '追跡できるデブリは一千五百個を超えました', 'JAは過去の結果。ENは "There are now" と現在存在へ時間含意を追加')
a(11, 'translation', 'addition', 'summary', 'summary_generation(JA本文に要約文なし)', None, 'JA本文はテストと限定。EN要約が "sometimes relied on hidden human helpers" とテスト限定を落とし hidden を付加')
a(12, 'translation', 'scope', 'summary', 'summary_generation(JA本文に要約文なし)', 'そして、人間コンシェルジュ機能を当面ロールバックしました', 'JAは人間コンシェルジュ機能のロールバック。EN要約が "Muse test" と対象を広げた')
a([15, 114], 'translation', 'strength', 'summary', 'summary_generation(JA本文に要約文なし)', '適切な開示がないまま人間が電話を担当すると', 'JA本文は「適切な開示がないまま」。EN要約が "without users being told" と開示ゼロの断定に強めた')
a([13, 85], 'translation', 'number', 'body', 'collective_noun_number(幹部=役職の集合名詞,単複無標)', 'Metaの幹部は、適切な開示なしにテストを始めたのは「ミス」だったと認め', 'JA「幹部」は数無標。ENで "executives" と複数化。台帳は副社長1名')
a(26, 'amplified', 'scope', 'body', 'modifier_scope(並列の係り受け「対米貿易や投資」)', '湾岸諸国との対米貿易や投資の案件', 'JA R2も係りがやや曖昧。ENは "trade with the United States and investment with Gulf countries" と誤分割')
a(105, 'amplified', 'scope', 'body', 'modifier_scope(並列の係り受け「対米貿易や投資」)', '湾岸諸国との対米貿易や投資の案件', '#26と同一文(Trial B判定者はR0+ENと判定)')
a(33, 'translation', 'number', 'body', 'collective_noun_number(幹部)', 'Metaの幹部は、適切な説明がないままテストを始めたのはミスだったと認め', 'JA「幹部」->EN "Meta executives"')
a(34, 'translation', 'subject', 'summary', 'summary_generation + 受け手/かけ手の語義反転(「電話の相手」->callers)', '電話の相手に、誰が話しているのかをきちんと伝えられるかどうかです', 'JA本文は受け手へ伝える。EN要約 "callers were not clearly told" は caller=かける側の語義。盲検 重大')
a([42, 53], 'translation', 'number', 'body', 'collective_noun_number(幹部)', 'Metaの幹部は、適切な開示をしないまま契約スタッフが電話をかけるテストを始めたのは「ミス」だったと認めました', 'JA「Metaの幹部」->EN "Meta executives"')
a(54, 'translation', 'subject', 'body', 'subject_omission(「認めた発言だ」の主語省略)', '米政府の公式記事によれば、宇宙軍が宇宙に兵器を配備したと初めて認めた発言だ', 'JAは認めた主体が省略。ENが "anyone" と補完し主体を広げた')
a(58, 'translation', 'number', 'body', 'collective_noun_number(幹部)', 'Meta幹部はミスと認め', 'JA「Meta幹部」->EN "Meta executives"')
a(59, 'translation', 'addition', 'summary', 'summary_generation(JA本文に要約文なし)', '誰が電話しているのか、きちんと伝えたのか', 'EN要約 "call recipients that human staff were calling" と開示の相手・内容を具体化')
a(72, 'translation', 'subject', 'body', 'subject_omission(「...交渉を頼んだ一件では」の依頼者省略)', 'インターネットとケーブル料金の交渉を頼んだ一件では、人間の契約スタッフが人種に関する不適切な発言をした', 'JAは依頼した主体が省略。ENが "Meta was asked" と誤補完(台帳MUSE-HC-011は従業員)。ユーザー判定 重大')
a(83, 'translation', 'causal', 'summary', 'summary_generation(JA本文に要約文なし)', None, 'JA本文は懸念が「続いていた」と並置。EN要約が "stayed high as shipping concerns persisted" と因果化')
a(86, 'translation', 'number', 'body', 'number_unmarked(従業員)', 'インターネットやケーブル料金の交渉をミューズに依頼した従業員からは...これは報道で紹介された一件の従業員報告', 'JA「従業員」数無標。ENで "employees who asked" と複数化(直後で one employee と限定)')
a(87, 'translation', 'term', 'body', 'pronoun_reference(「電話機能」->the feature)', 'Metaは、事業者との改善を続け、準備が整い、適切な開示ができる場合にのみ、電話機能を公開展開すると説明しています', 'JA「電話機能」->EN "the feature"。直前が human concierge feature のため指示対象が曖昧化')
a(89, 'translation', 'number', 'body', 'collective_noun_number(幹部)', 'Metaの幹部は「ミス」だったと認めた', 'JA「Metaの幹部」->EN "Meta executives also admitted"')
a(93, 'translation', 'causal', 'summary', 'summary_generation(JA本文に要約文なし)', '海峡をめぐる緊張という舞台装置は残ったままだったのです', 'JAは緊張が残ったと述べるのみ。EN要約 "kept oil prices high" と因果化')
a(98, 'translation', 'subject', 'body', 'word_choice("involving"で主体の方向が消える)', '湾岸諸国によるアメリカとの貿易や投資の案件に置き換える', 'JA「湾岸諸国による」->EN "involving the Gulf states and the United States"。主体・方向が不明瞭')
a(104, 'translation', 'addition', 'summary', 'summary_generation(JA本文に要約文なし)', 'システムの名前は不明です。攻撃能力も、標的も確認されていません', 'JAは名称・能力・標的不明。EN要約 "their purpose and treaty status remain unclear" と purpose を不明に拡張')
a(74, 'translation', 'causal', 'summary', 'summary_generation(R0にあった因果主張がR2で除去されたがEN要約で再出現)', '(R2末尾)料金案と供給不安が別々に動く、二幕構成のドラマだと分かります', 'R0 original.md 15行目に「理由は...別の心配が残っていたからです」。R2で除去。EN要約 "fears ... kept prices high" が復活')

# --- JA+EN (judge: R2 or R0 contains) ---
a(2, 'ja', 'scope', 'body', 'ja_same', '敵対する相手の行動から米軍の部隊を守るため', 'JA R2に「米軍の部隊」。ENは忠実訳 "U.S. forces"')
a([4, 123], 'ja', 'addition', 'body', 'ja_same', '比べる相手としてよく話題になるのが、ロシアの衛星破壊です', 'JA R2に同文。ENは "A common comparison"')
a(8, 'ja', 'causal', 'body', 'ja_same', '答えを間違えると、私たちの通信や移動にも関わる話なのです', 'JA R2に同文')
a(9, 'ja', 'scope', 'body', 'ja_same', '敵対的な相手の行動から米軍全体を守るため', 'JA R2に「米軍全体」。ENは "the entire U.S. military"')
a(116, 'ja', 'scope', 'body', 'ja_same', '敵対的な相手の行動から米軍全体を守るため', 'JA R2に同文')
a([16, 102], 'ja', 'strength', 'body', 'ja_same', '配備が確認されたことと、条約に違反するかどうかは別問題です', 'JA R2に同文。ENは忠実訳。ユーザー判定 軽微(HUMAN_CHECK候補2)')
a(47, 'ja', 'strength', 'body', 'ja_same', '配備が確認されたこと', 'JA R2に同文')
a([19, 119], 'ja', 'scope', 'body', 'ja_same', '相場は一度下がって終わりではなく、また高い水準へ戻ったことです', 'JA R2に同文。ENは直訳')
a([20, 62], 'ja', 'addition', 'body', 'ja_same', 'それがAIに伝わると思っていたのに、意図せず契約スタッフにも共有されるかもしれない', 'JA R2に同文')
a(27, 'ja', 'addition', 'body', 'ja_same', '問題は、情報を扱う人がいる仕組みを十分に整理しないまま、テストが始まったことです', 'JA R2に同文')
a([31, 50], 'ja', 'addition', 'body', 'ja_same', '主役が二度入れ替わるのに', 'JA R2に同文。ENも "changed twice"')
a([32, 71], 'ja', 'scope', 'body', 'ja_same', '企業や店に電話をかける機能があります', 'JA R2で「米国」限定が欠落(R0は米国と明記)。ENは忠実訳')
a(36, 'ja', 'addition', 'body', 'ja_same', '軍事基地、軍事施設、要塞の設置', 'JA R2に同文')
a(40, 'ja', 'scope', 'body', 'ja_same', 'Museは、散髪の予約や商品の在庫確認などを電話で頼めるAIエージェントです', 'JA R2に同文')
a(41, 'ja', 'scope', 'body', 'ja_same', '電話機能は改善を続け、準備が整い、適切な開示ができる場合にだけ公開する方針です', 'JA R2に同文。ENは "the phone feature" と忠実訳。盲検 重大')
a(46, 'ja', 'addition', 'body', 'ja_same', '古い衛星', 'JA R2に同文。ENも "old satellite"')
a(48, 'ja', 'addition', 'body', 'ja_same', '原油価格が動けば、燃料代や輸送費を通じて私たちの暮らしに届きます', 'JA R2に同趣旨(R0も同)')
a(51, 'ja', 'scope', 'body', 'ja_same', '公開されたのは物件の存在までだ', 'JA R2に同文')
a(52, 'ja', 'addition', 'body', 'ja_same', 'いわば、台本を受け取ったAIの後ろから、人間キャストが登場する仕組みです', 'JA R2に同文')
a(61, 'ja', 'addition', 'body', 'ja_same', '健康やお金、家族のことなど、電話では機微な情報が出てくる可能性があります', 'JA R2に同文')
a(70, 'ja', 'causal', 'body', 'ja_same', 'ここで「20％案のせいで上がった」と決めつけるのは早い', 'JA R2に同文。ENは "too soon to conclude" と忠実訳')
a(75, 'ja', 'causal', 'body', 'ja_same', '前日の上昇も、料金案だけの話ではありません', 'JA R2に同文')
a(77, 'ja', 'scope', 'body', 'ja_same', '供給への懸念はそのまま残ったようだ', 'JA R2に同文。ENも "seemed to remain unchanged" とヘッジ保持')
a(103, 'ja', 'addition', 'body', 'ja_same', '壊されても動き続ける衛星の仕組み', 'JA R2に同文')
a(118, 'ja', 'scope', 'body', 'ja_same', '電話の出演者が誰なのかを、頼んだ側にも伝える必要があったわけです', 'JA R2に同文。ENは "The user who made the request"')
a(120, 'ja', 'addition', 'body', 'ja_same', '人が話せば、会話がスムーズに進む場面もありそう', 'JA R2に同文')
a(125, 'ja', 'scope', 'body', 'ja_same', '天体上の軍事基地や要塞、兵器試験、軍事演習も禁じる', 'JA R2に同文')
a(127, 'ja', 'scope', 'body', 'ja_same', '月などの天体に軍事基地や兵器を設けること', 'JA R2に同文')
a([49, 82, 91], 'amplified', 'subject', 'body', 'ambiguous_possessive(「AとBの攻撃」=間の攻撃/による攻撃)', '米国とイランの攻撃、海上封鎖、タンカーの安全をめぐる懸念', 'JAは「米国とイランの攻撃」(台帳は米・イラン間の攻撃)。ENで "attacks by the United States and Iran" と実行主体化')

# --- pending (保留) EN-related, not counted in main statistics ---
PEND = {
 10: dict(origin='translation', type='scope', loc='summary', cause='summary_generation', ja_corr=None, note='EN要約 "A 20 percent fee on Hormuz shipping"(shipping と cargo のずれ)。判定: 手動(要約文のためJA対応文なし)'),
 60: dict(origin='translation', type='term', loc='title', cause='word_choice(電話代行->Phone-Answering)', ja_corr='AI電話代行に、人間キャストが登場', note='ENタイトル訳語。phone-answering は着信応答を想起'),
 66: dict(origin='translation', type='addition', loc='summary', cause='summary_generation', ja_corr=None, note='EN要約 "exact nature and role remain unclear"。判定: 手動(要約文のためJA対応文なし)'),
 67: dict(origin='translation', type='addition', loc='body', cause='added_label', ja_corr=None, note='EN "commonly called the Space Treaty" の呼称付け足し。JA対応語の有無は未突合(判定: 手動・簡易)'),
 73: dict(origin='translation', type='subject', loc='summary', cause='summary_generation + 語義(callers)', ja_corr='電話の相手に、誰が話しているのかをきちんと伝えられるかどうか', note='#34と同一文(Trial B判定者は保留扱い)'),
 80: dict(origin='translation', type='scope', loc='summary', cause='summary_generation', ja_corr=None, note='#12と同一文(Trial B判定者は保留扱い) EN要約 "Muse test"'),
 97: dict(origin='translation', type='other', loc='title', cause='word_choice(比喩 The Star)', ja_corr=None, note='EN見出しの "The Star" の比喩。判定者は事実NGに算入しない'),
 99: dict(origin='amplified', type='subject', loc='body', cause='ambiguous_possessive', ja_corr='米国とイランの攻撃', note='#49/#82/#91と同一語。Trial B判定者は保留扱い'),
}

EN_KW = {  # regex to locate the EN sentence for JA-only quoted items
 2: r'protect U\.S\. forces', 4: r'common comparison', 8: r'answer wrong', 9: r'entire U\.S\. military|entire US military|protect the entire',
 16: r'deployment has been confirmed', 19: r'fall once', 20: r'shared with contract|thought', 27: r'The problem was that',
 31: r'changed twice', 32: r'can call companies', 36: r'military bases', 40: r'haircut', 41: r'keep improving the phone feature',
 46: r'old satellite', 47: r'deployment has been confirmed', 48: r'oil prices move', 49: r'attacks by', 50: r'changed twice', 51: r'existence of the property',
 52: r'script', 61: r'health|sensitive', 62: r'Users thought', 70: r'too soon to conclude', 71: r'can call companies', 75: r'previous day was not only',
 77: r'unchanged', 82: r'attacks by', 91: r'attacks by', 102: r'deployment has been confirmed', 103: r'keep working|damaged', 116: r'entire U\.S\. military|protect the entire|all US forces',
 118: r'The user who made', 119: r'fall once', 120: r'When a person speaks', 123: r'common comparison', 125: r'military bases', 127: r'bases or weapons|military bases',
 7: r'now more than 1,500', 126: r'now more than 1,500', 26: r'investment with Gulf', 105: r'deals on trade', 98: r'trade and investment deals involving',
 99: r'attacks by', 89: r'Meta executives also admitted', 58: r'Meta executives admitted', 5: r'agencies', 0: r'agencies', 109: r'agencies',
}

def norm(s): return re.sub(r'[^a-z0-9]+', ' ', s.lower()).strip()
def toks(s): return set(w for w in norm(s).split() if len(w) > 2)
def split_en(t):
    t = t.replace('\r', '')
    for ab in ('U.S.', 'Mr.', 'Dr.', 'Ms.', 'St.'):
        t = t.replace(ab, ab.replace('.', '<DOT>'))
    return [x.strip().replace('<DOT>', '.') for x in re.split(r'(?<=[.!?”])\s+|\n+', t) if x.strip()]
def jacc(a_, b_):
    A_, B_ = toks(a_), toks(b_)
    return len(A_ & B_) / max(1, len(A_ | B_)) if A_ and B_ else 0
def contain(a_, b_):
    A_, B_ = toks(a_), toks(b_)
    return len(A_ & B_) / max(1, min(len(A_), len(B_))) if A_ and B_ else 0

def en_quote(text):
    m = re.findall(r'[A-Za-z][^／」]{20,}', text)
    return m[0].strip(' “”"') if m else None

def find_sentence(en_text, idx, text):
    sents = split_en(en_text)
    if idx in EN_KW:
        for s in sents:
            if re.search(EN_KW[idx], s): return s
    q = en_quote(text)
    if q and sents:
        best = max(sents, key=lambda s: jacc(s, q))
        if jacc(best, q) >= 0.3: return best
    return None

def models_for_run(run):
    d = {}
    f = run + '/raw_usage_log.jsonl'
    if os.path.exists(f):
        for l in open(f, encoding='utf8'):
            try: x = json.loads(l)
            except Exception: continue
            st = x.get('stage')
            if st in ('advanced', 'ja_r2', 'ja_original'): d.setdefault(st, set()).add(x.get('model_id'))
    return {k: sorted(v) for k, v in d.items()}

def en_dev(run, sent):
    res = []
    fs = sorted(glob.glob(run + '/b1b/audit/deviation_checks/advanced_attempt*.json')) + [run + '/b1b/audit/deviation_check.json']
    for f in fs:
        if not os.path.exists(f): continue
        d = json.load(open(f, encoding='utf8'))
        p = d.get('parsed', d)
        kind = 'final' if f.endswith('deviation_check.json') else os.path.basename(f).replace('.json', '')
        for dv in p.get('deviations', []):
            c = dv.get('claim_in_article', '')
            if sent and (jacc(c, sent) >= 0.5 or (contain(c, sent) >= 0.8 and contain(sent, c) >= 0.5)):
                res.append(dict(src=kind, severity=dv.get('severity'), origin=dv.get('origin'), related_fact_id=dv.get('related_fact_id'),
                                flags=[k[8:] if k.startswith('changed_') else k for k in dv if (k.startswith('changed_') or k == 'unsupported_new_claim') and dv.get(k)]))
    return res

def checker_info(run, sent):
    out = dict(has_checker=False)
    fs = glob.glob(run + '/checker/runs/*.json')
    if not fs: return out
    d = json.load(open(fs[0], encoding='utf8'))
    out['has_checker'] = True; out['final_state'] = d.get('final_state')
    out['cycles'] = []
    cand = False
    if sent:
        for u in d.get('stage1_coverage', {}).get('union_candidates', []):
            c = u.get('claim_text', '')
            if c and (jacc(c, sent) >= 0.5 or contain(c, sent) >= 0.85):
                cand = True; out['stage1_union_candidate'] = dict(sources=u.get('sources'), sub_reasons=u.get('sub_reasons'))
        for cy in d.get('cycles', []):
            for s in cy.get('stage2_results', []):
                c = s.get('claim_text', '')
                if c and (jacc(c, sent) >= 0.5 or contain(c, sent) >= 0.85):
                    cand = True
                    out['cycles'].append(dict(cycle=cy.get('cycle'), materiality=s.get('materiality'), llm_materiality=s.get('llm_materiality'),
                                              section_type=s.get('section_type'), basis=s.get('basis'), related_fact_id=s.get('related_fact_id')))
        last = None
        for cy in d.get('cycles', []):
            t = cy.get('en_text_after_rewrite')
            if t: last = t
        if last:
            out['sentence_in_final_text'] = any(norm(x) == norm(sent) for x in split_en(last))
        else:
            out['sentence_in_final_text'] = 'no_rewrite_text'
    out['candidate'] = cand
    return out

items = []
for i, it in enumerate(raw):
    if i in A: ann = A[i]; counted = True
    elif i in PEND: ann = PEND[i]; counted = False
    else: continue
    run = it['run_dir'].replace(BS, '/')
    en_path = run + '/b1b/article.md'
    en_text = open(en_path, encoding='utf8').read() if os.path.exists(en_path) else ''
    sent = find_sentence(en_text, i, it['text'])
    ja_path = run + '/ja_writer/revision2.md'
    mods = models_for_run(run)
    tr = 'A' if it['trial'].startswith('all6') else 'B'
    rec = dict(
        id=f'T{tr}-{i:03d}', raw_index=i, trial=tr, source_judgment=f"er052_output/{it['trial']}/eval/judgments/{it['code']}.json",
        article_key=it['key'], cell=it['arm'], run_dir=run, judge=it['judge'],
        counted=counted, severity=(it.get('severity') or 'pending'), judge_kind=it.get('kind'), fact_id=it.get('fact_id'),
        in_r0=it.get('in_r0'), in_r2=it.get('in_r2'), in_en=it.get('in_en'),
        location_class=('EN_ONLY' if (it.get('in_en') and not it.get('in_r0') and not it.get('in_r2')) else ('JA+EN' if it.get('in_en') else 'pending(所在不明)')),
        ng_text=it['text'], judge_reason=it.get('reason'), en_sentence_matched=sent,
        origin=ann['origin'], type=ann['type'], position=ann['loc'], linguistic_cause=ann['cause'], ja_r2_corresponding=ann['ja_corr'], judgment_basis=ann['note'],
        judgment_method='手動(JA R2と EN の突合。根拠は ja_r2_corresponding と judgment_basis)',
        en_writer_models=mods.get('advanced'), ja_r2_models=mods.get('ja_r2'),
        has_en_article=bool(en_text), ja_exists=os.path.exists(ja_path),
        en_deviation_check=en_dev(run, sent), checker=checker_info(run, sent),
    )
    items.append(rec)
# event ids (same run_dir + same EN sentence = one event; counted items only)
ev_keys = sorted({(r['run_dir'], (r['en_sentence_matched'] or r['ng_text'])[:60]) for r in items if r['counted']})
ev_id = {k: f'EV-{n+1:02d}' for n, k in enumerate(ev_keys)}
for r in items:
    k = (r['run_dir'], (r['en_sentence_matched'] or r['ng_text'])[:60])
    r['event_id'] = ev_id.get(k) if r['counted'] else None
    ak = r['article_key']
    r['theme'] = 'meta' if 'meta' in ak else ('hormuz' if 'hormuz' in ak else ('space_weapons' if 'space_weapons' in ak else 'unknown'))
with open(OUT + '/items.jsonl', 'w', encoding='utf8') as f:
    for r in items: f.write(json.dumps(r, ensure_ascii=False) + '\n')
print('items', len(items), 'counted', sum(1 for r in items if r['counted']))
