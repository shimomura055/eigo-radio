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
t('index schema + 9 slots + default exists', () => { assert.deepStrictEqual(FL.validateIndex(idx), []); assert.strictEqual(idx.articles.filter(a => !a.slug.startsWith('ui_check')).length, 9); assert.ok(idx.articles.some(a => FL.stateKey(a) === idx.default)); });
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
  assert.strictEqual(r.schema, 'eigo_radio_selection_result_v1'); assert.strictEqual(r.schema_version, 1);
  assert.deepStrictEqual(r.article, { slug: 'monkeys_paw', level: 'b1b', level_label: 'Advanced', name: '猿の手', text_sha256: mp.source.text_sha256 });
  assert.deepStrictEqual(r.selection.key_phrase, ['burial']); assert.strictEqual(r.counts.key_phrase, 1); assert.strictEqual(r.comment, 'c');
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
console.log('ALL PASS', n);
