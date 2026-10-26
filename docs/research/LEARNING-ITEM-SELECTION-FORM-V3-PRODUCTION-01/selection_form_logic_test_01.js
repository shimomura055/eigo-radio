// form_logic.js の単体test(node)。ブラウザ不要。終了コード0=全PASS。
const assert = require('assert');
const fs = require('fs');
const path = require('path');
const ROOT = path.resolve(__dirname, '..', '..', '..');
const FD = path.join(ROOT, 'user_test', 'selection_form_v3');
const FL = require(path.join(FD, 'form_logic.js'));
const rd = p => JSON.parse(fs.readFileSync(path.join(FD, p), 'utf8'));
let n = 0; const t = (name, fn) => { fn(); n++; console.log('PASS', name); };

const mp = rd('data/monkeys_paw__b1b.json');
const dummy = rd('data/ui_check_dummy__dummy.json');
const idx = rd('data/articles.json');
const TL = FL.terms(dummy);

t('limits constants', () => { assert.deepStrictEqual(FL.LIMITS, [3, 5, 12]); assert.strictEqual(FL.GRAMMAR_MAX, 2); });
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

t('grammar independent of phrase/word limits and max 2', () => {
  const st = FL.newState(); const gids = dummy.grammar.map(g => g.id);
  [0, 1, 2].forEach(i => FL.setChoice(st, TL, TL[i], 1, true));
  assert.ok(FL.setGrammar(st, gids, 'g1', true)); assert.ok(FL.setGrammar(st, gids, 'g2', true));
  assert.strictEqual(FL.setGrammar(st, gids, 'g3', true), false);
  assert.strictEqual(FL.grammarChosen(st.grammar, gids).length, 2);
  assert.deepStrictEqual(FL.counts(st.choices, TL), [3, 0, 0]);   // 文法はフレーズ・単語の累積に影響しない
  assert.ok(FL.setGrammar(st, gids, 'g1', false)); assert.ok(FL.setGrammar(st, gids, 'g3', true));
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
  assert.ok(txt.startsWith('記事: 猿の手 Advanced\n① Key Phrase (1/3): accept no responsibility\n② 追加解説 (①＋②=2/5): compensation\n③ 本文意味表示 (累計=3/12): snatch\n文法 (0/2): なし\n自由コメント: テスト'));
});
t('structured output has required keys and is JSON round-trippable', () => {
  const st = FL.newState(); const tl = FL.terms(mp); FL.setChoice(st, tl, 'burial', 1, true); st.comment = 'c';
  const o = FL.buildStructured(mp, st, '2026-10-26T00:00:00Z'); const r = JSON.parse(JSON.stringify(o));
  assert.strictEqual(r.schema, 'eigo_radio_selection_result_v2'); assert.strictEqual(r.schema_version, 2);   // 委任_02でv2へ(日本語訳・区分・文法解説全文を追加)
  assert.deepStrictEqual(r.article, { slug: 'monkeys_paw', level: 'b1b', level_label: 'Advanced', name: '猿の手', text_sha256: mp.source.text_sha256 });
  assert.deepStrictEqual(r.selection.key_phrase.map(x => x.term), ['burial']); assert.strictEqual(r.counts.key_phrase, 1); assert.strictEqual(r.comment, 'c');
  assert.strictEqual(r.generated_at, '2026-10-26T00:00:00Z'); assert.strictEqual(r.production_connected, false);
  assert.deepStrictEqual(r.limits, { key_phrase: 3, key_phrase_plus_extra: 5, total_highlight: 12, grammar: 2 });
});
t('chatgpt url: contains selection, <=6000, falls back when too long', () => {
  const st = FL.newState(); const tl = FL.terms(mp); FL.setChoice(st, tl, 'burial', 1, true);
  const r = FL.buildChatGptUrl(mp, st, 'T'); assert.ok(r.url && r.url.length <= 6000 && r.url.startsWith('https://chatgpt.com/?q='));
  const msg = decodeURIComponent(r.url.slice('https://chatgpt.com/?q='.length)); assert.ok(msg.includes('① Key Phrase (1/3): burial')); assert.ok(r.with_json && msg.includes('"selection"'));
  st.comment = 'あ'.repeat(3000); const r2 = FL.buildChatGptUrl(mp, st, 'T'); assert.strictEqual(r2.url, null);   // 長文はコピー誘導
  st.comment = 'あ'.repeat(330); const r3 = FL.buildChatGptUrl(mp, st, 'T'); if (r3.url) assert.ok(r3.url.length <= 6000);
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
t('v2 data: call1 has no AI reason (explicit), replay placeholder suppressed, call2 reasons present', () => {
  const m = rd('data/ai_island_temple__a2__prod.json');
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
  assert.strictEqual(FL.reasonOf({ term: 'a' }).has, false); assert.strictEqual(FL.reasonOf({ term: 'a', reason_ja: '理由' }).has, true);
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
  const call2 = d.phrases.find(x => x.origin === 'call2'), call1 = d.phrases.find(x => x.origin === 'call1');
  pick(d, st, [[call1.term, 1], [call2.term, 2]]);
  const txt = FL.buildText(d, st); const iAi = txt.indexOf('【AI選定理由'); const conf = txt.slice(0, iAi), ai = txt.slice(iAi);
  assert.ok(conf.includes('日本語訳: ' + call1.ja_gloss + '【正式訳】') && conf.includes('日本語訳: ' + call2.ja_gloss + '【正式訳】'));
  assert.ok(!conf.includes(call2.reason_ja), 'reason must not be in the confirmed section');
  assert.ok(ai.includes(call2.term + ': ' + call2.reason_ja)); assert.ok(ai.includes(call1.term + ': (AI理由なし'));
  const mp1 = rd('data/monkeys_paw__b1b.json'); const st2 = FL.newState(); pick(mp1, st2, [['burial', 1]]);
  const t2 = FL.buildText(mp1, st2); assert.ok(t2.includes('【仮訳・未確定】') && t2.includes('黙って確定・変更しないこと'));
  const miss = { slug: 'x', level: 'a2', name: 'X', phrases: [{ id: 'a', term: 'foo bar' }], words: [], grammar: [] }; const st3 = FL.newState(); pick(miss, st3, [['foo bar', 1]]);
  assert.ok(FL.buildText(miss, st3).includes('日本語訳: (未生成)【日本語訳未生成】'));
});
t('structured v2: complete user-confirmed fields; AI reason separated and flagged reference-only', () => {
  const d = rd('data/ui_check_dummy__dummy.json'); const st = FL.newState(); const tl = FL.terms(d); const gids = d.grammar.map(g => g.id);
  pick(d, st, [[tl[0], 1], [tl[1], 1], [tl[2], 2], [tl[3], 3]]); FL.setGrammar(st, gids, 'g1', true); FL.setGrammar(st, gids, 'g3', true); st.comment = 'C';
  const o = JSON.parse(JSON.stringify(FL.buildStructured(d, st, 'T')));
  assert.strictEqual(o.schema, 'eigo_radio_selection_result_v2'); assert.strictEqual(o.schema_version, 2);
  assert.deepStrictEqual(o.selection.key_phrase.map(x => x.term), [tl[0], tl[1]]); assert.deepStrictEqual(o.selection.extra_explanation.map(x => x.term), [tl[2]]); assert.deepStrictEqual(o.selection.meaning_display.map(x => x.term), [tl[3]]);
  o.selection.key_phrase.concat(o.selection.extra_explanation, o.selection.meaning_display).forEach(x => { ['term', 'category', 'category_label', 'ja_gloss', 'ja_gloss_status'].forEach(k => assert.ok(k in x, k)); assert.ok(!('reason_ja' in x), 'AI reason must not be mixed into confirmed item'); });
  assert.deepStrictEqual(o.selection.grammar.map(g => g.id), ['g1', 'g3']); o.selection.grammar.forEach(g => { const src = d.grammar.find(z => z.id === g.id); assert.strictEqual(g.explanation_full, src.body); assert.strictEqual(g.explanation_status, 'provided'); assert.strictEqual(g.title, src.title); });
  assert.strictEqual(o.comment, 'C'); assert.strictEqual(o.ai_reference.for_reference_only, true); assert.strictEqual(o.ai_reference.items.length, 4);
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
    const d = rd(f); const tl = FL.terms(d); const st = FL.newState(); const gids = (d.grammar || []).map(g => g.id);
    tl.forEach((x, i) => FL.setChoice(st, tl, x, i < 3 ? 1 : i < 5 ? 2 : 3, true)); gids.slice(0, 2).forEach(g => FL.setGrammar(st, gids, g, true)); st.comment = '全項目コメント';
    const txt = FL.buildText(d, st), o = FL.buildStructured(d, st, 'T', { all_candidates: true });
    const items = d.phrases.concat(d.words);
    tl.forEach((x, i) => {
      const it = items[i], g = FL.glossOf(it), ro = FL.reasonOf(it);
      if (st.choices[x]) { assert.ok(txt.includes('｜' + x + '｜日本語訳: ' + (g.text || '(未生成)') + '【' + g.label + '】'), f + x); if (ro.has) assert.ok(txt.includes(x + ': ' + ro.text), f + 'reason ' + x); }
    });
    d.grammar.slice(0, 2).forEach(g => assert.ok(txt.includes(g.body) && txt.includes(g.title)));
    assert.ok(txt.includes('自由コメント: 全項目コメント'));
    const sel = o.selection.key_phrase.concat(o.selection.extra_explanation, o.selection.meaning_display);
    assert.strictEqual(sel.length, FL.counts(st.choices, tl).reduce((a, b) => a + b, 0)); assert.strictEqual(o.candidates_all.length, tl.length); assert.strictEqual(o.comment, '全項目コメント');
    const u = FL.buildChatGptUrl(d, st, 'T'); maxLen = Math.max(maxLen, u.url ? u.url.length : 99999);
    if (u.url) { const m = decodeURIComponent(u.url.slice('https://chatgpt.com/?q='.length)); assert.ok(m.includes('全項目コメント') && m.includes('日本語訳: ')); assert.ok(u.url.length <= 6000); }
  });
  console.log('  (max send URL length over all articles, full selection [99999=url null => copy guidance]:', maxLen, ')');
});
t('url: when too long never silently truncates (url null => copy guidance); text-only fallback keeps all fields', () => {
  const d = mpp; const tl = FL.terms(d); const st = FL.newState(); pick(d, st, [[tl[0], 1], [tl[1], 1], [tl[2], 1], [tl[3], 2], [tl[4], 2]]);
  const r = FL.buildChatGptUrl(d, st, 'T');
  if (r.url) { const m = decodeURIComponent(r.url.slice('https://chatgpt.com/?q='.length)); [tl[0], tl[1], tl[2], tl[3], tl[4]].forEach(x => assert.ok(m.includes(x))); assert.ok(m.includes('【AI選定理由')); }
  st.comment = 'あ'.repeat(2500); assert.strictEqual(FL.buildChatGptUrl(d, st, 'T').url, null);
});
t('copy text includes JSON with all candidates and is parseable', () => {
  const d = mpp; const st = FL.newState(); pick(d, st, [[d.phrases[0].term, 1]]);
  const c = FL.buildCopyText(d, st, 'T'); const j = JSON.parse(c.slice(c.indexOf('```json\n') + 8, c.lastIndexOf('\n```')));
  assert.strictEqual(j.candidates_all.length, 7); assert.strictEqual(j.selection.key_phrase[0].ja_gloss, d.phrases[0].ja_gloss);
});
console.log('ALL PASS', n);
