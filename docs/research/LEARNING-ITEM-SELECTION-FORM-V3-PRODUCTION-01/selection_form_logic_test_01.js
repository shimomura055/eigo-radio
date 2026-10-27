// form_logic.js の単体test(node)。ブラウザ不要。終了コード0=全PASS。
const assert = require('assert');
const fs = require('fs');
const path = require('path');
const ROOT = path.resolve(__dirname, '..', '..', '..');
const FD = path.join(ROOT, 'user_test', 'selection_form_v3');
const FL = require(path.join(FD, 'form_logic.js'));
const rd = p => JSON.parse(fs.readFileSync(path.join(FD, p), 'utf8'));
const SO = f => ({ stem: path.basename(f, '.json') });   // 委任_07: 照合コードのstem(データファイル名)
let n = 0; const t = (name, fn) => { fn(); n++; console.log('PASS', name); };

const mp = rd('data/monkeys_paw__b1b.json');
const dummy = rd('data/ui_check_dummy__dummy.json');
const idx = rd('data/articles.json');
const TL = FL.terms(dummy);

t('limits constants', () => { assert.deepStrictEqual(FL.LIMITS, [3, 5, 12]); assert.strictEqual(FL.GRAMMAR_MAX, 1); assert.strictEqual(FL.GRAMMAR_TOP_N, 2); });   // 新仕様(2026-10-27): 提示Top2・選択最大1
t('data schema: monkeys_paw b1b', () => { assert.deepStrictEqual(FL.validateArticle(mp), []); assert.strictEqual(mp.phrases.length, 7); assert.strictEqual(mp.words.length, 4); assert.deepStrictEqual(mp.grammar, []); });
t('data: rescued flag shown for pulled free', () => { const f = mp.phrases.filter(p => p.flag === 'rescued').map(p => p.term); assert.ok(f.includes('pulled free')); });
t('data: gate-dropped interferes not present', () => { assert.ok(!FL.terms(mp).some(x => x === 'interferes')); });
t('data schema: dummy', () => { assert.deepStrictEqual(FL.validateArticle(dummy), []); assert.strictEqual(dummy.grammar.length, 3); });
t('index schema + 9 slots + default exists', () => { assert.deepStrictEqual(FL.validateIndex(idx), []); assert.strictEqual(idx.articles.filter(a => !a.slug.startsWith('ui_check') && !a.slug.endsWith('_prod')).length, 9); assert.ok(idx.articles.some(a => FL.stateKey(a) === idx.default)); });
t('index data files exist and valid', () => { idx.articles.filter(a => a.data).forEach(a => assert.deepStrictEqual(FL.validateArticle(rd(a.data)), [])); });

t('cumulative: (1) max 3', () => {
  const st = FL.newState();
  assert.ok(FL.setChoice(st, TL, TL[0], 1, true)); assert.ok(FL.setChoice(st, TL, TL[1], 1, true)); assert.ok(FL.setChoice(st, TL, TL[2], 1, true));
  assert.strictEqual(FL.allowed(st.choices, TL, TL[3], 1), false);
  assert.strictEqual(FL.setChoice(st, TL, TL[3], 1, true), false);
  assert.strictEqual(FL.counts(st.choices, TL)[0], 3);
});
t('cumulative: (1)+(2) max 5', () => {
  const st = FL.newState();
  [0, 1, 2].forEach(i => FL.setChoice(st, TL, TL[i], 1, true));
  FL.setChoice(st, TL, TL[3], 2, true); FL.setChoice(st, TL, TL[4], 2, true);
  assert.strictEqual(FL.allowed(st.choices, TL, TL[5], 2), false);
  assert.strictEqual(FL.allowed(st.choices, TL, TL[5], 1), false);
  assert.strictEqual(FL.allowed(st.choices, TL, TL[5], 3), true);  // (3)は(1)+(2)=5でも可(総計<=12)
});
t('cumulative: total max 12', () => {
  const st = FL.newState();
  [0, 1, 2].forEach(i => FL.setChoice(st, TL, TL[i], 1, true));
  [3, 4].forEach(i => FL.setChoice(st, TL, TL[i], 2, true));
  for (let i = 5; i < 12; i++) assert.ok(FL.setChoice(st, TL, TL[i], 3, true), 'i=' + i);
  assert.strictEqual(FL.counts(st.choices, TL).reduce((a, b) => a + b, 0), 12);
  assert.strictEqual(TL.length, 12);
});
t('total 12 reached blocks (3) for a 13th (synthetic)', () => {
  const tl = Array.from({ length: 14 }, (_, i) => 't' + i); const st = FL.newState();
  for (let i = 0; i < 12; i++) FL.setChoice(st, tl, tl[i], 3, true);
  assert.strictEqual(FL.allowed(st.choices, tl, tl[12], 3), false);
  assert.strictEqual(FL.allowed(st.choices, tl, tl[12], 1), false);
});
t('same candidate only one category (switching keeps exactly one)', () => {
  const st = FL.newState(); FL.setChoice(st, TL, TL[0], 1, true); FL.setChoice(st, TL, TL[0], 2, true);
  assert.strictEqual(st.choices[TL[0]], 2); assert.deepStrictEqual(FL.counts(st.choices, TL), [0, 1, 0]);
});
t('deselect always possible, even at limit', () => {
  const st = FL.newState(); [0, 1, 2].forEach(i => FL.setChoice(st, TL, TL[i], 1, true));
  assert.ok(FL.setChoice(st, TL, TL[0], 1, false)); assert.strictEqual(FL.counts(st.choices, TL)[0], 2);
  assert.ok(FL.allowed(st.choices, TL, TL[3], 1));
});
t('change at limit: (1)->(2) at (1)=3 allowed; (2)->(1) at (1)=3 blocked', () => {
  const st = FL.newState(); [0, 1, 2].forEach(i => FL.setChoice(st, TL, TL[i], 1, true)); FL.setChoice(st, TL, TL[3], 2, true);
  assert.ok(FL.allowed(st.choices, TL, TL[0], 2)); assert.strictEqual(FL.allowed(st.choices, TL, TL[3], 1), false);
});
t('stale choices (term not in candidates) not counted', () => {
  const st = FL.newState(); st.choices['gone'] = 1; st.choices['gone2'] = 1; st.choices['gone3'] = 1;
  assert.deepStrictEqual(FL.counts(st.choices, TL), [0, 0, 0]); assert.ok(FL.allowed(st.choices, TL, TL[0], 1));
});

t('grammar independent of phrase/word limits; new spec: presented Top2 only, max 1 (2nd rejected)', () => {
  const st = FL.newState(); const gids = FL.grammarIds(dummy);
  assert.deepStrictEqual(gids, ['g1', 'g2']);   // 3件データでも提示は先頭2件のみ
  [0, 1, 2].forEach(i => FL.setChoice(st, TL, TL[i], 1, true));
  assert.ok(FL.setGrammar(st, gids, 'g1', true)); assert.strictEqual(FL.setGrammar(st, gids, 'g2', true), false);
  assert.strictEqual(FL.grammarChosen(st.grammar, gids).length, 1);
  assert.deepStrictEqual(FL.counts(st.choices, TL), [3, 0, 0]);   // 文法はフレーズ・単語の累積に影響しない
  assert.ok(FL.setGrammar(st, gids, 'g1', false)); assert.ok(FL.setGrammar(st, gids, 'g2', true));
});

t('9-article switching keeps states separate', () => {
  const nine = Array.from({ length: 9 }, (_, i) => ({ slug: 'dummy' + i, level: i % 2 ? 'b1b' : 'a2', name: 'D' + i }));
  assert.deepStrictEqual(FL.validateIndex({ schema: 'eigo_radio_selection_index_v1', articles: nine }), []);
  const store = {}; const get = e => store[FL.stateKey(e)] || (store[FL.stateKey(e)] = FL.newState());
  const tl = ['a', 'b', 'c', 'd'];
  nine.forEach((e, i) => { FL.setChoice(get(e), tl, tl[i % 4], (i % 3) + 1, true); get(e).comment = 'c' + i; });
  nine.forEach((e, i) => { assert.strictEqual(get(e).choices[tl[i % 4]], (i % 3) + 1); assert.strictEqual(get(e).comment, 'c' + i); assert.strictEqual(Object.keys(get(e).choices).length, 1); });
  assert.strictEqual(Object.keys(store).length, 9);
  // 往復しても消失しない(JSON往復=localStorage相当)
  const re = JSON.parse(JSON.stringify(store)); nine.forEach((e, i) => assert.strictEqual(re[FL.stateKey(e)].comment, 'c' + i));
});
t('same slug different level are different keys', () => { assert.notStrictEqual(FL.stateKey({ slug: 'x', level: 'a2' }), FL.stateKey({ slug: 'x', level: 'b1b' })); });
t('duplicate index key rejected', () => { assert.ok(FL.validateIndex({ schema: 'eigo_radio_selection_index_v1', articles: [{ slug: 'x', level: 'a', name: 'n' }, { slug: 'x', level: 'a', name: 'n' }] }).length > 0); });

t('output text matches reference format', () => {
  const st = FL.newState(); const tl = FL.terms(mp);
  FL.setChoice(st, tl, 'accept no responsibility', 1, true); FL.setChoice(st, tl, 'compensation', 2, true); FL.setChoice(st, tl, 'snatch', 3, true); st.comment = 'テスト';
  const txt = FL.buildText(mp, st);
  assert.ok(txt.startsWith('記事: 猿の手 Advanced\n① Key Phrase (1/3): accept no responsibility\n② 追加解説 (①＋②=2/5): compensation\n③ 本文意味表示 (累計=3/12): snatch\n文法 (0/1｜AI評価Top 1・Top 2から1件、または適切な候補なしで0件): なし\n自由コメント: テスト'));
});
t('structured output has required keys and is JSON round-trippable', () => {
  const st = FL.newState(); const tl = FL.terms(mp); FL.setChoice(st, tl, 'burial', 1, true); st.comment = 'c';
  const o = FL.buildStructured(mp, st, '2026-10-26T00:00:00Z'); const r = JSON.parse(JSON.stringify(o));
  assert.strictEqual(r.schema, 'eigo_radio_selection_result_v2'); assert.strictEqual(r.schema_version, 2);   // 委任_02でv2へ(日本語訳・区分・文法解説全文を追加)
  assert.deepStrictEqual(r.article, { slug: 'monkeys_paw', level: 'b1b', level_label: 'Advanced', name: '猿の手', text_sha256: mp.source.text_sha256,
    candidates_sha256: null, candidates_sha256_source: 'unavailable_dev_trial_doc', source_kp_candidates_path: mp.source_kp_candidates_path });   // 委任_03で追加(additive)
  assert.deepStrictEqual(r.selection.key_phrase.map(x => x.term), ['burial']); assert.strictEqual(r.counts.key_phrase, 1); assert.strictEqual(r.comment, 'c');
  assert.strictEqual(r.generated_at, '2026-10-26T00:00:00Z'); assert.strictEqual(r.production_connected, false);
  assert.deepStrictEqual(r.limits, { key_phrase: 3, key_phrase_plus_extra: 5, total_highlight: 12, grammar: 1, grammar_presented_max: 2 });
});
t('chatgpt url (v3, 委任_07): readable text + 照合コード, <=6000 => url, over => url null (paste guidance, not an error)', () => {
  const st = FL.newState(); const tl = FL.terms(mp); FL.setChoice(st, tl, 'burial', 1, true);
  const r = FL.buildChatGptUrl(mp, st, 'T', SO('data/monkeys_paw__b1b.json')); assert.ok(r.url && r.url.length <= 6000 && r.url.startsWith('https://chatgpt.com/?q=')); assert.strictEqual(r.mode, 'url');
  const msg = decodeURIComponent(r.url.slice('https://chatgpt.com/?q='.length)); assert.strictEqual(msg, r.text); assert.ok(msg.includes('- burial：')); assert.ok(!msg.includes('"selection"') && !msg.includes('candidate_id') && !msg.includes('```json'));   // JSON同梱は廃止
  assert.ok(msg.startsWith(FL.PREFACE)); assert.ok(!msg.includes('Claude Code向け指示案'));
  st.comment = 'あ'.repeat(3000); const r2 = FL.buildChatGptUrl(mp, st, 'T', SO('data/monkeys_paw__b1b.json')); assert.strictEqual(r2.url, null); assert.strictEqual(r2.mode, 'paste'); assert.ok(r2.text.includes('あ'.repeat(3000)));   // 長文は貼付案内(textは全文)
  st.comment = 'あ'.repeat(330); const r3 = FL.buildChatGptUrl(mp, st, 'T', SO('data/monkeys_paw__b1b.json')); if (r3.url) assert.ok(r3.url.length <= 6000);
});
t('dummy output is marked as not a formal article', () => {
  const st = FL.newState(); assert.ok(FL.buildText(dummy, st).includes('正式記事ではない'));
});
t('no reference placeholder grammar leaked into monkeys_paw data', () => {
  const s = JSON.stringify(mp); assert.ok(!s.includes('過去完了形') && !s.includes('分詞による名詞の後置修飾'));
});
// 参照HTML本体のcounts/allowedを抽出し、乱数状態でform_logic.jsと同値であることを確認(参照コードとの等価性)
t('equivalence with reference counts/allowed (fuzz 20000)', () => {
  const ref = fs.readFileSync(path.join(ROOT, 'docs', 'pm', 'Phrase_Form', 'eigo_radio_selection_form_reference.html'), 'utf8');
  const c0 = ref.indexOf('function counts()'), c1 = ref.indexOf('function render()');
  assert.ok(c0 > 0 && c1 > c0);
  let cur = { choices: {} };
  const get = () => cur;
  const refFns = new Function('get', ref.slice(c0, c1) + '; return {counts, allowed};')(get);
  let seed = 12345; const rnd = () => (seed = (seed * 1103515245 + 12345) & 0x7fffffff) / 0x7fffffff;
  const tl = Array.from({ length: 12 }, (_, i) => 't' + i);
  for (let k = 0; k < 20000; k++) {
    const ch = {}; tl.forEach(x => { const r = rnd(); ch[x] = r < 0.5 ? 0 : 1 + Math.floor(rnd() * 3); });
    cur = { choices: ch };
    // 参照は不正な(上限超過)状態もそのまま数える。等価性は counts と、あらゆる状態での allowed について確認
    assert.deepStrictEqual(refFns.counts(), FL.counts(ch, tl));
    const term = tl[Math.floor(rnd() * 12)], cat = 1 + Math.floor(rnd() * 3);
    assert.strictEqual(refFns.allowed(term, cat), FL.allowed(ch, tl, term, cat));
  }
});
// ---- 委任_02: 日本語訳・AI選定理由・送信データ(schema v2) ----
const STATUSES = ['official', 'provisional', 'missing'];
const dataFiles = idx.articles.filter(a => a.data).map(a => a.data);
const PLACEHOLDER = ['replay', 'mock', 'fixture'];
t('v2 data: every candidate has ja_gloss/status/reason_source; placeholder reasons never shown; official only from Production formal path', () => {
  dataFiles.filter(f => !f.includes('ui_check')).forEach(f => {
    const d = rd(f);
    d.phrases.concat(d.words).forEach(it => {
      const term = it.term;
      assert.ok(STATUSES.includes(it.ja_gloss_status), f + ':' + term + ' status');
      assert.strictEqual(it.ja_gloss, it.meaning_ja, f + ' ja_gloss===meaning_ja(既存項目の再利用)');
      assert.ok(it.reason_source, f + ':' + term + ' reason_source');
      assert.ok(!PLACEHOLDER.includes((it.reason_ja || '').toLowerCase()), f + ':' + term + ' placeholder reason');
      assert.strictEqual(it.ja_gloss.length > 0, it.ja_gloss_status !== 'missing', f + ':' + term);
      if (it.ja_gloss_status === 'official') assert.strictEqual(d.source.kind, 'PRODUCTION_FORMAL_PATH', f + ' official only from formal path');
      if (it.reason_ja) assert.ok(it.reason_source.startsWith('ai_')); else assert.ok(it.reason_source.startsWith('none_'));
    });
  });
});
t('v2 data: DEV Trial / replay glosses are provisional (not formal)', () => {
  ['data/monkeys_paw__b1b.json', 'data/monkeys_paw__b1b__prod.json'].forEach(f => rd(f).phrases.concat(rd(f).words).forEach(it => assert.strictEqual(it.ja_gloss_status, 'provisional', f + it.term)));
  assert.ok(rd('data/melos__a2__prod.json').phrases.every(it => it.ja_gloss_status === 'official'));
});
t('v2 data (legacy 3+5 doc): call1 has no AI reason (explicit), replay placeholder suppressed, call2 reasons present', () => {
  const m = rd('data/legacy/ai_island_temple__a2__prod.json');
  m.phrases.filter(x => x.origin === 'call1').forEach(x => { assert.strictEqual(x.reason_ja, ''); assert.strictEqual(x.reason_source, 'none_call1_has_no_reason'); });
  m.phrases.filter(x => x.origin === 'call2').forEach(x => { assert.ok(x.reason_ja.length > 0); assert.strictEqual(x.reason_source, 'ai_call2'); });
  const r = rd('data/monkeys_paw__b1b__prod.json'); const rr = r.phrases.concat(r.words);
  assert.ok(rr.some(x => x.reason_source === 'none_placeholder_not_real' && x.reason_ja === ''));
});
t('glossOf/reasonOf: old data without status is never treated as official; missing is explicit', () => {
  assert.strictEqual(FL.glossOf({ term: 'a', meaning_ja: '訳' }).status, 'provisional');
  assert.strictEqual(FL.glossOf({ term: 'a', ja_gloss: '', ja_gloss_status: 'official' }).status, 'missing');
  assert.strictEqual(FL.glossOf({ term: 'a' }).label, '日本語訳未生成');
  assert.strictEqual(FL.glossOf({ term: 'a', ja_gloss: '訳', ja_gloss_status: 'official' }).label, '正式訳');
  assert.strictEqual(FL.reasonOf({ term: 'a' }).has, false); assert.ok(!('note' in FL.reasonOf({ term: 'a' }))); assert.strictEqual(FL.reasonOf({ term: 'a', reason_ja: '理由' }).has, true);
});

const mpp = rd('data/melos__a2__prod.json');
const pick = (d, st, spec) => { const tl = FL.terms(d); spec.forEach(([term, cat]) => assert.ok(FL.setChoice(st, tl, term, cat, true), term)); };
t('send text: contains EN, JA gloss+status, category, grammar full body, comment; AI reason in a separate later section', () => {
  const d = rd('data/ui_check_dummy__dummy.json'); const st = FL.newState(); const tl = FL.terms(d);
  pick(d, st, [[tl[0], 1], [tl[1], 2], [tl[2], 3]]); FL.setGrammar(st, d.grammar.map(g => g.id), 'g1', true); st.comment = '自由コメント本文テスト';
  const txt = FL.buildText(d, st); const iConf = txt.indexOf('【ユーザー確定内容の詳細'), iAi = txt.indexOf('【AI選定理由');
  assert.ok(iConf > 0 && iAi > iConf);
  const conf = txt.slice(iConf, iAi), ai = txt.slice(iAi);
  [tl[0], tl[1], tl[2]].forEach((x, i) => { assert.ok(conf.includes(['①Key Phrase', '②追加解説', '③本文意味表示'][i] + '｜' + x + '｜日本語訳: '), x); });
  assert.ok(conf.includes(d.grammar[0].title) && conf.includes(d.grammar[0].body), 'grammar full body');
  assert.ok(txt.includes('自由コメント: 自由コメント本文テスト'));
  assert.ok(ai.includes('確認用情報'));
});
t('send text: official gloss and reason; provisional/missing marked; reasons only in AI section', () => {
  const d = mpp; const st = FL.newState();
  const all = d.phrases.concat(d.words), call2 = all.find(x => x.origin === 'call2'), call1 = all.find(x => x.origin === 'call1');
  pick(d, st, [[call1.term, 1], [call2.term, 2]]);
  const txt = FL.buildText(d, st); const iAi = txt.indexOf('【AI選定理由'); const conf = txt.slice(0, iAi), ai = txt.slice(iAi);
  assert.ok(conf.includes('日本語訳: ' + call1.ja_gloss + '【正式訳】') && conf.includes('日本語訳: ' + call2.ja_gloss + '【正式訳】'));
  assert.ok(!conf.includes(call2.reason_ja), 'reason must not be in the confirmed section');
  assert.ok(ai.includes(call2.term + '(' + call2.candidate_id + '): ' + call2.reason_ja)); assert.ok(ai.includes(call1.term + '(' + call1.candidate_id + '): ' + call1.reason_ja));   // 委任_03: 行末にcandidate_id。委任_04: 7+5ではcall1にも理由がある
  const lg = rd('data/legacy/melos__a2__prod.json'), lc1 = lg.phrases.find(x => x.origin === 'call1'), st4 = FL.newState(); pick(lg, st4, [[lc1.term, 1]]);
  const lt = FL.buildText(lg, st4); assert.ok(!lt.includes('AI理由なし') && !lt.includes(lc1.candidate_id + '):'), 'no-reason candidate has no line / no placeholder text');   // 旧3+5 docのcall1は理由なし=行ごと出さない(委任_05)
  const mp1 = rd('data/monkeys_paw__b1b.json'); const st2 = FL.newState(); pick(mp1, st2, [['burial', 1]]);
  const t2 = FL.buildText(mp1, st2); assert.ok(t2.includes('【仮訳・未確定】') && t2.includes('黙って確定・変更しないこと'));
  const miss = { slug: 'x', level: 'a2', name: 'X', phrases: [{ id: 'a', term: 'foo bar' }], words: [], grammar: [] }; const st3 = FL.newState(); pick(miss, st3, [['foo bar', 1]]);
  assert.ok(FL.buildText(miss, st3).includes('日本語訳: (未生成)【日本語訳未生成】'));
});
t('structured v2: complete user-confirmed fields; AI reason separated and flagged reference-only', () => {
  const d = rd('data/ui_check_dummy__dummy.json'); const st = FL.newState(); const tl = FL.terms(d); const gids = d.grammar.map(g => g.id);
  pick(d, st, [[tl[0], 1], [tl[1], 1], [tl[2], 2], [tl[3], 3]]); FL.setGrammar(st, gids, 'g1', true); assert.strictEqual(FL.setGrammar(st, gids, 'g3', true), false); st.comment = 'C';
  const o = JSON.parse(JSON.stringify(FL.buildStructured(d, st, 'T')));
  assert.strictEqual(o.schema, 'eigo_radio_selection_result_v2'); assert.strictEqual(o.schema_version, 2);
  assert.deepStrictEqual(o.selection.key_phrase.map(x => x.term), [tl[0], tl[1]]); assert.deepStrictEqual(o.selection.extra_explanation.map(x => x.term), [tl[2]]); assert.deepStrictEqual(o.selection.meaning_display.map(x => x.term), [tl[3]]);
  o.selection.key_phrase.concat(o.selection.extra_explanation, o.selection.meaning_display).forEach(x => { ['term', 'category', 'category_label', 'ja_gloss', 'ja_gloss_status'].forEach(k => assert.ok(k in x, k)); assert.ok(!('reason_ja' in x), 'AI reason must not be mixed into confirmed item'); });
  assert.deepStrictEqual(o.selection.grammar.map(g => g.id), ['g1']); o.selection.grammar.forEach(g => { const src = d.grammar.find(z => z.id === g.id); assert.strictEqual(g.explanation_full, src.body); assert.strictEqual(g.explanation_status, 'provided'); assert.strictEqual(g.title, src.title); });
  assert.strictEqual(o.comment, 'C'); assert.strictEqual(o.ai_reference.for_reference_only, true); assert.strictEqual(o.ai_reference.items.length, 0);   // ダミーは理由なし→ai_referenceに含めない(委任_05)
  assert.ok(o.user_confirmed_note_ja.includes('変更しない')); assert.ok(!('candidates_all' in o));
  const full = FL.buildStructured(d, st, 'T', { all_candidates: true }); assert.strictEqual(full.candidates_all.length, 12);
  assert.strictEqual(full.candidates_all.filter(x => x.category > 0).length, 4);
});
t('structured v2: grammar absent (ungenerated) is explicit, not fabricated', () => {
  const o = FL.buildStructured(rd('data/monkeys_paw__b1b.json'), FL.newState(), 'T'); assert.strictEqual(o.grammar_status, 'no_candidates_ungenerated'); assert.deepStrictEqual(o.selection.grammar, []);
  const g = FL.grammarRecord({ id: 'z', title: 'T', body: '' }); assert.strictEqual(g.explanation_status, 'missing');
});
t('no omission for every article x full selection (3/2/7 + 2 grammar + comment): text always has all; JSON complete', () => {
  let maxLen = 0;
  dataFiles.forEach(f => {
    const d = rd(f); const tl = FL.terms(d); const st = FL.newState(); const gids = FL.grammarIds(d);
    tl.forEach((x, i) => FL.setChoice(st, tl, x, i < 3 ? 1 : i < 5 ? 2 : 3, true)); gids.slice(0, 1).forEach(g => FL.setGrammar(st, gids, g, true)); st.comment = '全項目コメント';
    const txt = FL.buildText(d, st), o = FL.buildStructured(d, st, 'T', { all_candidates: true });
    const items = d.phrases.concat(d.words);
    tl.forEach((x, i) => {
      const it = items[i], g = FL.glossOf(it), ro = FL.reasonOf(it);
      if (st.choices[x]) { assert.ok(txt.includes('｜' + x + '｜日本語訳: ' + (g.text || '(未生成)') + '【' + g.label + '】'), f + x); if (ro.has) assert.ok(txt.includes(x + '(' + it.candidate_id + '): ' + ro.text), f + 'reason ' + x); }
    });
    d.grammar.slice(0, 1).forEach(g => assert.ok(txt.includes(g.body) && txt.includes(g.title)));
    assert.ok(txt.includes('自由コメント: 全項目コメント'));
    const sel = o.selection.key_phrase.concat(o.selection.extra_explanation, o.selection.meaning_display);
    assert.strictEqual(sel.length, FL.counts(st.choices, tl).reduce((a, b) => a + b, 0)); assert.strictEqual(o.candidates_all.length, tl.length); assert.strictEqual(o.comment, '全項目コメント');
    const u = FL.buildChatGptUrl(d, st, 'T', SO(f)); maxLen = Math.max(maxLen, u.url ? u.url.length : 99999);
    if (u.url) { const m = decodeURIComponent(u.url.slice('https://chatgpt.com/?q='.length)); assert.ok(m.includes('全項目コメント') && m.includes('照合コード(変更しないでください)：AIF1-')); assert.ok(u.url.length <= 6000); }
  });
  console.log('  (max send URL length over all articles, full selection [99999=url null => copy guidance]:', maxLen, ')');
});
t('url: when too long never silently truncates (url null => paste guidance with full text); url mode keeps all selected items', () => {
  const d = mpp; const tl = FL.terms(d); const st = FL.newState(); pick(d, st, [[tl[0], 1], [tl[1], 1], [tl[2], 1], [tl[3], 2], [tl[4], 2]]);
  const r = FL.buildChatGptUrl(d, st, 'T', SO('data/melos__a2__prod.json'));
  [tl[0], tl[1], tl[2], tl[3], tl[4]].forEach(x => assert.ok(r.text.includes('- ' + x + '：'))); if (r.url) assert.strictEqual(decodeURIComponent(r.url.slice('https://chatgpt.com/?q='.length)), r.text);
  st.comment = 'あ'.repeat(2500); const r2 = FL.buildChatGptUrl(d, st, 'T', SO('data/melos__a2__prod.json')); assert.strictEqual(r2.url, null); assert.ok(r2.text.includes('あ'.repeat(2500)));
});
t('copy text includes JSON with all candidates and is parseable', () => {
  const d = mpp; const st = FL.newState(); pick(d, st, [[d.phrases[0].term, 1]]);
  const c = FL.buildCopyText(d, st, 'T'); const j = JSON.parse(c.slice(c.indexOf('```json\n') + 8, c.lastIndexOf('\n```')));
  assert.strictEqual(j.candidates_all.length, d.phrases.length + d.words.length); assert.strictEqual(j.selection.key_phrase[0].ja_gloss, d.phrases[0].ja_gloss);
});

// ---- 委任_03: candidate_id / kind / candidates_sha256 (payload v2 minor 1) ----
const dataFiles03 = idx.articles.filter(a => a.data && !a.data.includes('ui_check')).map(a => a.data);
t('v2.1: candidate_id unique + present in every real data file; kind valid; id==candidate_id', () => {
  assert.strictEqual(dataFiles03.length, 10);
  dataFiles03.forEach(f => {
    const d = rd(f), all = d.phrases.concat(d.words), ids = all.map(x => x.candidate_id);
    assert.ok(ids.length > 0 && ids.every(x => typeof x === 'string' && x), f);
    assert.strictEqual(new Set(ids).size, ids.length, f);
    all.forEach(x => { assert.ok(x.kind === 'phrase' || x.kind === 'word', f); assert.strictEqual(x.id, x.candidate_id); });
  });
});
t('v2.1: structured payload carries candidate_id/kind on selected items, ai_reference, candidates_all; article has sha fields; text has candidate_id lines', () => {
  dataFiles03.forEach(f => { if (rd(f).kp_confirmed) return;   // ユーザー確定済み記事は選定不可(ロック)=専用testで検証
    const d = rd(f), all = d.phrases.concat(d.words), tl = FL.terms(d), st = FL.newState();
    all.slice(0, 3).forEach(x => FL.setChoice(st, tl, x.term, 1, true)); FL.setChoice(st, tl, all[3].term, 2, true); FL.setChoice(st, tl, all[4] ? all[4].term : all[5].term, 3, true);
    const j = FL.buildStructured(d, st, 'T', { all_candidates: true });
    assert.strictEqual(j.schema_version, 2); assert.strictEqual(j.schema_minor, 1);
    let ns = 0;
    ['key_phrase', 'extra_explanation', 'meaning_display'].forEach(k => j.selection[k].forEach(it => {
      ns++; const o = all.filter(x => x.term === it.term)[0]; assert.strictEqual(it.candidate_id, o.candidate_id); assert.strictEqual(it.kind, o.kind); }));
    assert.strictEqual(ns, 5);
    const nWithReason = ['key_phrase', 'extra_explanation', 'meaning_display'].reduce((a, k) => a + j.selection[k].filter(it => (all.filter(x => x.term === it.term)[0].reason_ja || '').trim()).length, 0);
    assert.strictEqual(j.ai_reference.items.length, nWithReason); j.ai_reference.items.forEach(it => assert.ok(it.candidate_id && it.reason_ja));   // 委任_05: 理由がある候補のみ
    j.candidates_all.forEach((it, i) => { assert.strictEqual(it.candidate_id, all[i].candidate_id); assert.strictEqual(it.kind, all[i].kind); });
    assert.ok('candidates_sha256' in j.article && j.article.candidates_sha256_source && 'source_kp_candidates_path' in j.article);
    assert.strictEqual(j.article.candidates_sha256, d.candidates_sha256);
    const txt = FL.buildText(d, st);
    assert.ok(txt.includes('候補集合sha256: ' + (d.candidates_sha256 || 'なし(取得不可: ')));
    ['key_phrase', 'extra_explanation', 'meaning_display'].forEach(k => j.selection[k].forEach(it => assert.ok(txt.includes('candidate_id: ' + it.candidate_id + '｜種類: ' + it.kind))));
  });
});
t('v2.1: null sha stays null (replay / DEV Trial) and is stated, not fabricated', () => {
  ['data/monkeys_paw__b1b.json', 'data/monkeys_paw__b1b__prod.json'].forEach(f => {
    const d = rd(f), st = FL.newState(); assert.strictEqual(d.candidates_sha256, null); assert.ok(/^unavailable_/.test(d.candidates_sha256_source));
    assert.strictEqual(FL.buildStructured(d, st, 'T').article.candidates_sha256, null);
    assert.ok(FL.buildText(d, st).includes('候補集合sha256: なし(取得不可: unavailable_'));
  });
});
t('v2.1: duplicate candidate_id rejected by validateArticle; legacy data (no candidate_id) uses id or null', () => {
  const d = JSON.parse(JSON.stringify(rd('data/melos__a2__prod.json'))); d.phrases[1].candidate_id = d.phrases[0].candidate_id;
  assert.ok(FL.validateArticle(d).some(e => e.startsWith('dup_candidate_id')));
  assert.strictEqual(FL.candIdOf({ term: 'x' }), null); assert.strictEqual(FL.candIdOf({ term: 'x', id: 'i1' }), 'i1');
  assert.strictEqual(FL.itemRecord({ term: 'x' }, 1).kind, null);
});
t('v2.1: URL length with 3 selected (informational) never exceeds 6000 or is null (copy guidance)', () => {
  dataFiles03.forEach(f => {
    const d = rd(f), tl = FL.terms(d), st = FL.newState(); tl.slice(0, 3).forEach(x => FL.setChoice(st, tl, x, 1, true));
    const r = FL.buildChatGptUrl(d, st, 'T', SO(f)); assert.ok(r.url === null || r.url.length <= 6000);
    console.log('  url len', f, r.url ? r.url.length : 'null(paste)', 'mode', r.mode);
  });
});

// ================= AI-ISLAND-FORM-PRODUCTION-01 委任_02: 文法新仕様(Top1/Top2・最大1件・0件可・2件禁止)+確定済みKP/KWロック =================
const NSLUG = ['a2', 'b1b'];
const aiD = l => rd('data/ai_island_temple__' + l + '__prod.json');
const PAY = l => JSON.parse(fs.readFileSync(path.join(ROOT, 'docs', 'research', 'AI-ISLAND-FORM-PRODUCTION-01', 'payloads', 'ai_island_temple__' + l + '__user_confirmed_01.json'), 'utf8'));
t('newspec: AI island data valid; Top1/Top2 only with rank 1,2 in AI order; 3rd+ not in data; spec presented_ids match', () => {
  NSLUG.forEach(l => {
    const d = aiD(l); assert.deepStrictEqual(FL.validateArticle(d), []);
    assert.strictEqual(d.grammar.length, 2); assert.deepStrictEqual(d.grammar.map(g => g.rank), [1, 2]);
    assert.deepStrictEqual(FL.grammarPresented(d).map(g => g.display_rank), [1, 2]);
    assert.deepStrictEqual(d.grammar_spec.presented_ids, d.grammar.map(g => g.candidate_id)); assert.strictEqual(d.grammar_spec.max_select, 1); assert.strictEqual(d.grammar_spec.allow_zero, true);
    d.grammar.forEach(g => { assert.strictEqual(g.explanation_status, 'provided'); assert.ok(g.explanation_full.length > 100); assert.strictEqual(g.body, g.explanation_full); });
    assert.strictEqual(d.grammar_spec.hidden_ids.length + 2, l === 'a2' ? 4 : 3);   // 旧4候補/3候補の3位以降は非表示
  });
});
t('newspec: presentation sorted by rank even if data order differs; legacy (no rank) keeps array order, Top2 cut', () => {
  const d = JSON.parse(JSON.stringify(aiD('a2'))); d.grammar.reverse(); assert.deepStrictEqual(FL.grammarPresented(d).map(g => g.rank), [1, 2]);
  const d3 = { grammar: [{ id: 'a' }, { id: 'b' }, { id: 'c' }] }; assert.deepStrictEqual(FL.grammarIds(d3), ['a', 'b']);
  const d4 = { grammar: [{ id: 'z', rank: 3 }, { id: 'y', rank: 1 }, { id: 'x', rank: 2 }] }; assert.deepStrictEqual(FL.grammarIds(d4), ['y', 'x']);
});
t('newspec: initial state is undecided (old form 0-grammar not carried over) and send/copy is blocked; exactly-one or explicit none unblocks', () => {
  NSLUG.forEach(l => {
    const d = aiD(l), st = FL.newState(), gids = FL.grammarIds(d);
    assert.strictEqual(FL.grammarDecision(d, st), 'undecided'); assert.strictEqual(FL.grammarBlocked(d, st), true);
    assert.strictEqual(FL.buildStructured(d, st, 'T').grammar_status, 'pending_reselection');
    assert.ok(FL.chooseGrammar(st, gids, gids[0])); assert.strictEqual(FL.grammarDecision(d, st), 'selected'); assert.strictEqual(FL.grammarBlocked(d, st), false);
    assert.ok(FL.chooseGrammar(st, gids, gids[1])); assert.deepStrictEqual(FL.grammarChosen(st.grammar, gids), [gids[1]]);   // ラジオ=置換。常に1件
    assert.strictEqual(FL.setGrammar(st, gids, gids[0], true), false);                                                         // チェック方式での2件目は拒否
    assert.ok(FL.chooseGrammarNone(st, gids)); assert.strictEqual(FL.grammarDecision(d, st), 'none'); assert.strictEqual(FL.grammarBlocked(d, st), false);
    assert.strictEqual(FL.chooseGrammar(st, gids, 'not_presented'), false);
  });
  const legacy = rd('data/monkeys_paw__b1b.json'); assert.strictEqual(FL.grammarBlocked(legacy, FL.newState()), false);   // 旧形式(grammar_spec無し・候補0)はブロックしない
});
t('newspec: old saved state with 2 grammar selected is reset to undecided (not silently trimmed); old 0-selection state stays undecided', () => {
  const d = aiD('a2'), gids = FL.grammarIds(d);
  const st = { choices: { 'carry over': 1 }, grammar: {}, comment: 'x' }; gids.forEach(g => st.grammar[g] = true);
  assert.strictEqual(FL.normalizeGrammar(st, gids), true); assert.strictEqual(FL.grammarDecision(d, st), 'undecided');
  const old0 = { choices: {}, grammar: {}, comment: '' }; assert.strictEqual(FL.normalizeGrammar(old0, gids), false); assert.strictEqual(FL.grammarDecision(d, old0), 'undecided');
});
t('newspec: payload for selected / none / pending; selected has rank+explanation verbatim+sha; none has [] with user_selected_none', () => {
  NSLUG.forEach(l => {
    const d = aiD(l), gids = FL.grammarIds(d), st = FL.newState();
    FL.chooseGrammar(st, gids, gids[1]); let o = JSON.parse(JSON.stringify(FL.buildStructured(d, st, 'T')));
    assert.strictEqual(o.grammar_status, 'user_selected_one'); assert.strictEqual(o.selection.grammar.length, 1);
    const g = o.selection.grammar[0], src = d.grammar[1];
    assert.strictEqual(g.rank, 2); assert.strictEqual(g.rank_label, 'Top 2'); assert.strictEqual(g.explanation_full, src.explanation_full); assert.strictEqual(g.explanation_sha256, src.explanation_sha256); assert.strictEqual(g.candidate_id, src.candidate_id);
    assert.strictEqual(o.counts.grammar, 1); assert.strictEqual(o.limits.grammar, 1); assert.strictEqual(o.grammar_decision.state, 'selected'); assert.strictEqual(o.grammar_decision.selected_candidate_id, src.candidate_id);
    assert.deepStrictEqual(o.grammar_decision.presented.map(x => x.rank), [1, 2]);
    FL.chooseGrammarNone(st, gids); o = JSON.parse(JSON.stringify(FL.buildStructured(d, st, 'T')));
    assert.strictEqual(o.grammar_status, 'user_selected_none'); assert.deepStrictEqual(o.selection.grammar, []); assert.strictEqual(o.grammar_decision.state, 'none'); assert.strictEqual(o.grammar_decision.selected_candidate_id, null);
    const txt = FL.buildText(d, FL.newState()); assert.ok(txt.includes('未決定'));
  });
});
t('newspec: confirmed KP/KW are locked: payload selection == saved user-confirmed payload verbatim, regardless of saved choices; 10 items 3/2/5', () => {
  NSLUG.forEach(l => {
    const d = aiD(l), pay = PAY(l), gids = FL.grammarIds(d);
    const st = FL.newState(); st.choices = { 'carry over': 3, 'obstacle': 1, 'separately': 2 };   // 旧フォームの残骸があっても無視される
    FL.chooseGrammar(st, gids, gids[0]);
    const o = JSON.parse(JSON.stringify(FL.buildStructured(d, st, 'T')));
    ['key_phrase', 'extra_explanation', 'meaning_display'].forEach(k => assert.deepStrictEqual(o.selection[k], pay.selection[k], k));
    assert.deepStrictEqual(o.counts, { key_phrase: 3, key_phrase_plus_extra: 5, total_highlight: 10, grammar: 1 });
    assert.strictEqual(o.article.text_sha256, pay.article.text_sha256); assert.strictEqual(o.article.candidates_sha256, pay.article.candidates_sha256);
    assert.strictEqual(o.kp_confirmed.locked, true); assert.strictEqual(o.kp_confirmed.status, 'USER_CONFIRMED'); assert.strictEqual(o.production_connected, false);
    o.selection.key_phrase.concat(o.selection.extra_explanation, o.selection.meaning_display).forEach(x => assert.strictEqual(x.ja_gloss_status, 'official'));
    const txt = FL.buildText(d, st); pay.selection.key_phrase.concat(pay.selection.extra_explanation, pay.selection.meaning_display).forEach(x => assert.ok(txt.includes(x.term + '｜日本語訳: ' + x.ja_gloss + '【正式訳】｜candidate_id: ' + x.candidate_id), x.term));
    assert.ok(txt.includes('ユーザー確定済み'));
    const full = FL.buildStructured(d, st, 'T', { all_candidates: true }); assert.strictEqual(full.candidates_all.filter(x => x.category > 0).length, 10);
  });
});
t('newspec: article-level exact expectations (user table) for Standard and Advanced', () => {
  const exp = { a2: [[1, 'carry over', '持ち越す'], [1, 'take a detour', '寄り道をする'], [1, 'card to play', '使える手'], [2, 'worth paying attention to', '注目する価値がある'], [2, 'obstacle', '障害物'], [3, 'make a difference', '影響を与える'], [3, 'separately', '個別に'], [3, 'feature', '性質'], [3, 'Strategy', '作戦'], [3, 'setup', '設定']],
    b1b: [[1, 'carry over', '次に持ち越す'], [1, 'call on', '頼む'], [1, 'take a detour', '遠回りをする'], [2, 'card to play', '打てる手'], [2, 'obstacle', '障害物'], [3, 'look at separately', '別々に検討する'], [3, 'exploration', 'いろいろ探ること'], [3, 'technique', 'やり方'], [3, 'overlook', '見過ごす'], [3, 'erase', '消し去る']] };
  NSLUG.forEach(l => { const got = aiD(l).kp_confirmed.selection.map(r => [r.category, r.term, r.ja_gloss]); assert.deepStrictEqual(got, exp[l]); });
});
t('newspec: validateArticle fail-closed on tampered kp_confirmed / 3 grammar items / wrong presented_ids', () => {
  const base = aiD('a2'), cp = () => JSON.parse(JSON.stringify(base));
  let d = cp(); d.kp_confirmed.selection[0].ja_gloss = '別の訳'; assert.ok(FL.validateArticle(d).some(e => e.startsWith('kp_confirmed: ja_gloss')));
  d = cp(); d.kp_confirmed.selection[0].candidate_id = 'p_zzz'; assert.ok(FL.validateArticle(d).some(e => e.includes('候補に無いcandidate_id')));
  d = cp(); d.kp_confirmed.selection[0].category = 2; assert.ok(FL.validateArticle(d).some(e => e.includes('件数')));
  d = cp(); d.kp_confirmed.candidates_sha256 = '0'.repeat(64); assert.ok(FL.validateArticle(d).some(e => e.includes('candidates_sha256')));
  d = cp(); d.kp_confirmed.text_sha256 = '0'.repeat(64); assert.ok(FL.validateArticle(d).some(e => e.includes('text_sha256')));
  d = cp(); d.grammar.push(Object.assign({}, d.grammar[0], { id: 'gx', rank: 3 })); assert.ok(FL.validateArticle(d).some(e => e.includes('2件を超えて')));
  d = cp(); d.grammar_spec.presented_ids = ['x', 'y']; assert.ok(FL.validateArticle(d).some(e => e.includes('presented_ids')));
});
t('newspec: index.html uses radio (name=gram) + explicit zero option + rank badge + gating; no checkbox for grammar; no 2-select path', () => {
  const h = fs.readFileSync(path.join(FD, 'index.html'), 'utf8');
  assert.ok(h.includes('type="radio" name="gram" data-grammar=') && h.includes('data-grammar-none') && h.includes('適切な候補なし（0件）') && h.includes("'Top '+g.display_rank"));
  assert.ok(!/type="checkbox"[^>]*data-grammar/.test(h)); assert.ok(h.includes('FL.grammarBlocked(D,get())')); assert.ok(h.includes('FL.chooseGrammar(') && h.includes('FL.chooseGrammarNone('));
  assert.ok(h.includes('conf=!!d.kp_confirmed') && h.includes('確定済み'));
  assert.ok(!h.includes('gch>=2'));   // 旧上限(2件)の残骸なし
});

console.log('ALL PASS', n);

// ---- 委任_04: P7/W5' 7+5 配線追従(cap 12・kind別cap 7/5・reason_ja逐語) ----
const KP75_FILES = { 'ai_island_temple__a2__prod': 'er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_kp75_ev_01/a2', 'ai_island_temple__b1b__prod': 'er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_kp75_ev_01/b1b', 'uk_train_speaker_playback__a2__prod': 'er019_output/family_x_audio_production_wiring_01/uk_train_speaker_playback__run_kp75_ev_01/a2', 'uk_train_speaker_playback__b1b__prod': 'er019_output/family_x_audio_production_wiring_01/uk_train_speaker_playback__run_kp75_ev_01/b1b', 'redelivery_fee__a2__prod': 'er121_output/family_y_production_01/redelivery_fee/run_kp75_ev_01/key_phrases/a2', 'redelivery_fee__b1b__prod': 'er121_output/family_y_production_01/redelivery_fee/run_kp75_ev_01/key_phrases/b1b', 'melos__a2__prod': 'er026_output/family_z_production_e2e_01/melos/run_kp75_ev_01/key_phrases/a2', 'melos__b1b__prod': 'er026_output/family_z_production_e2e_01/melos/run_kp75_ev_01/key_phrases/b1b' };
const kp75Root = require('path').resolve(__dirname, '..', '..', '..');
const srcDoc = (rel) => { const f = require('path').join(kp75Root, rel, (rel.includes('/key_phrases/') ? '' : 'key_phrases/') + 'kp_candidates.json'); return JSON.parse(require('fs').readFileSync(f, 'utf8')); };
t('7+5: 8 evidence data files exist, cap 12 and cap_by_kind {phrase:7, word:5}, shortfall_detail.cap is 12 (doc value)', () => {
  Object.keys(KP75_FILES).forEach(k => {
    const d = rd('data/' + k + '.json'); const src = srcDoc(KP75_FILES[k]);
    assert.strictEqual(d.cap, 12, k); assert.deepStrictEqual(d.cap_by_kind, { phrase: 7, word: 5 }, k);
    if (d.shortfall_detail) { assert.strictEqual(d.shortfall_detail.cap, 12, k); assert.deepStrictEqual(d.shortfall_detail.cap_by_kind, { phrase: 7, word: 5 }, k); assert.strictEqual(d.shortfall_detail.cap, src.shortfall_detail.cap); }
    assert.ok(d.phrases.length <= 7 && d.words.length <= 5, k); assert.ok(d.phrases.length + d.words.length <= 12, k);
    assert.strictEqual((d.overflow || []).length, 0, k);
    assert.ok(/source_kp_candidates_path/.test(JSON.stringify(Object.keys(d))) && d.source_kp_candidates_path.includes('run_kp75_ev_01'), k);
    if (d.shortfall) assert.ok(d.shortfall_note_ja.includes('上限12件') && d.shortfall_note_ja.includes('フレーズ最大7') && d.shortfall_note_ja.includes('単語最大5'), d.shortfall_note_ja);
  });
});
t('7+5: kind taken verbatim from candidate doc (candidate_doc), gloss official, reason_ja verbatim for every candidate (call1 included)', () => {
  let n = 0;
  Object.keys(KP75_FILES).forEach(k => {
    const d = rd('data/' + k + '.json'); const src = srcDoc(KP75_FILES[k]); const by = {}; src.candidates.forEach(c => { by[c.candidate_id] = c; });
    d.phrases.concat(d.words).forEach(e => { const c = by[e.candidate_id]; assert.ok(c, e.term);
      assert.strictEqual(e.kind, c.kind); assert.strictEqual(e.kind_source, 'candidate_doc'); assert.strictEqual(e.ja_gloss, c.japanese_gloss); assert.strictEqual(e.ja_gloss_status, 'official');
      assert.ok(c.reason_ja && c.reason_ja.length > 0); assert.strictEqual(e.reason_ja, c.reason_ja); assert.ok(e.reason_source.startsWith('ai_'), e.reason_source); n++; });
    assert.strictEqual(d.phrases.length + d.words.length, src.candidates.length, k);
    assert.strictEqual(d.candidates_sha256, src.candidates_sha256);
  });
  assert.ok(n >= 70, String(n));
});
t('7+5: legacy 3+5 versions are kept under data/legacy and are not in the index; index has the 8 evidence slots', () => {
  const fs2 = require('fs'), pa = require('path'); const base = pa.join(kp75Root, 'user_test', 'selection_form_v3', 'data');
  ['ai_island_temple__a2__prod', 'ai_island_temple__b1b__prod', 'redelivery_fee__a2__prod', 'redelivery_fee__b1b__prod', 'melos__a2__prod'].forEach(k => { assert.ok(fs2.existsSync(pa.join(base, 'legacy', k + '.json')), k); assert.strictEqual(rd('data/legacy/' + k + '.json').shortfall_detail.cap, 8, k); });
  const datas = idx.articles.map(a => a.data); Object.keys(KP75_FILES).forEach(k => assert.ok(datas.includes('data/' + k + '.json'), k)); assert.ok(!datas.some(x => x && x.includes('legacy')));
  assert.strictEqual(idx.articles.filter(a => !a.slug.startsWith('ui_check') && !a.slug.endsWith('_prod')).length, 9);
});
t('7+5: a full 12-candidate article (7 phrases + 5 words) validates and selection limits (3/5/12) are unchanged', () => {
  const d = rd('data/uk_train_speaker_playback__b1b__prod.json'); assert.strictEqual(d.phrases.length + d.words.length, 12); assert.deepStrictEqual(FL.validateArticle(d), []);
  const st = FL.newState(), tl = FL.terms(d); assert.strictEqual(tl.length, 12);
  for (let i = 0; i < 3; i++) assert.ok(FL.setChoice(st, tl, tl[i], 1, true)); assert.ok(!FL.setChoice(st, tl, tl[3], 1, true));
  for (let i = 3; i < 5; i++) assert.ok(FL.setChoice(st, tl, tl[i], 2, true)); assert.ok(!FL.setChoice(st, tl, tl[5], 2, true));
  for (let i = 5; i < 12; i++) assert.ok(FL.setChoice(st, tl, tl[i], 3, true));
});

// ---- 委任_05: 理由が実在しない候補は理由欄を出さず、送信にも含めない(ユーザー決定2026-10-27 §4) ----
t('no-reason candidates: excluded from ai_reference / candidates_all reason fields; no "AI理由なし" text anywhere', () => {
  const lg = rd('data/legacy/melos__a2__prod.json'); const all = lg.phrases.concat(lg.words);
  const c1 = all.find(x => x.origin === 'call1' && !x.reason_ja), c2 = all.find(x => x.origin === 'call2' && x.reason_ja);
  const st = FL.newState(); pick(lg, st, [[c1.term, 1], [c2.term, 2]]);
  const o = JSON.parse(JSON.stringify(FL.buildStructured(lg, st, 'T', { all_candidates: true })));
  assert.deepStrictEqual(o.ai_reference.items.map(x => x.candidate_id), [c2.candidate_id]);
  o.ai_reference.items.forEach(x => assert.ok(x.reason_ja && x.reason_source));
  const rec1 = o.candidates_all.find(x => x.candidate_id === c1.candidate_id); assert.ok(!('reason_ja' in rec1) && !('reason_source' in rec1));
  const js = JSON.stringify(o); assert.ok(!js.includes('AI理由なし') && !js.includes('なし)')); assert.ok(!FL.buildText(lg, st).includes('AI理由なし'));
  const none = rd('data/ui_check_dummy__dummy.json'); const st2 = FL.newState(); pick(none, st2, [[FL.terms(none)[0], 1]]);
  assert.deepStrictEqual(FL.buildStructured(none, st2, 'T').ai_reference.items, []);
});
t('index.html: reason details rendered only when reason exists; no "(なし)"/placeholder markup', () => {
  const h = fs.readFileSync(path.join(FD, 'index.html'), 'utf8');
  assert.ok(/ro\.has\?'<details class="why"/.test(h)); assert.ok(!h.includes('ro.note') && !h.includes("（なし）"));
});
