// AI-ISLAND-FORM-PRODUCTION-01 委任_02: 文法新仕様(Top1/Top2・1件・0件可・2件禁止)+確定済みKP/KWロックの実DOM確認(headless Chrome CDP)。用法: node browser_check_aif2.mjs <baseUrl> <chromePath> [port]
// 確認: AI島Std/Adv=確定済みKP/KW10件のロック表示(チェック不可)・文法はTop1/Top2のみ(rank表示/解説全文)・ラジオ排他(最大1件)・「適切な候補なし(0件)」の明示選択・未決定では送信/コピー不可・
//       送信payload(KP/KW=確定内容の逐語、文法0/1件)・旧フォーム保存状態の無害化・他記事(旧形式)の非回帰。
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const base = process.argv[2];
const chrome = process.argv[3];
const port = Number(process.argv[4] || 9351);
const udd = fs.mkdtempSync(path.join(os.tmpdir(), 'aif2-chrome-'));
const proc = spawn(chrome, ['--headless=new', '--disable-gpu', '--no-first-run', `--remote-debugging-port=${port}`, `--user-data-dir=${udd}`, 'about:blank'], { stdio: 'ignore' });
const results = []; const consoleErrors = [];
const rec = (name, ok, detail = '') => { results.push({ name, ok, detail }); console.log((ok ? 'PASS ' : 'FAIL ') + name + (detail ? ' :: ' + detail : '')); };
const sleep = ms => new Promise(r => setTimeout(r, ms));
async function getWs() { for (let i = 0; i < 50; i++) { try { const r = await fetch(`http://127.0.0.1:${port}/json`); const j = await r.json(); const p = j.find(x => x.type === 'page'); if (p) return p.webSocketDebuggerUrl; } catch (e) { } await sleep(200); } throw new Error('chrome debug port not ready'); }
let ws, id = 0; const pend = {};
function send(method, params = {}) { return new Promise((res, rej) => { const i = ++id; pend[i] = { res, rej }; ws.send(JSON.stringify({ id: i, method, params })); }); }
async function ev(expr) { const r = await send('Runtime.evaluate', { expression: expr, awaitPromise: true, returnByValue: true }); if (r.exceptionDetails) throw new Error(JSON.stringify(r.exceptionDetails).slice(0, 300)); return r.result.value; }
async function goto(url) { await send('Page.navigate', { url }); await sleep(1800); }

try {
  ws = new WebSocket(await getWs());
  await new Promise(r => ws.addEventListener('open', r));
  ws.addEventListener('message', m => {
    const d = JSON.parse(m.data);
    if (d.id && pend[d.id]) { d.error ? pend[d.id].rej(new Error(JSON.stringify(d.error))) : pend[d.id].res(d.result); delete pend[d.id]; return; }
    if (d.method === 'Runtime.exceptionThrown') consoleErrors.push('exception: ' + JSON.stringify(d.params.exceptionDetails).slice(0, 300));
    if (d.method === 'Runtime.consoleAPICalled' && d.params.type === 'error') consoleErrors.push('console.error: ' + JSON.stringify(d.params.args).slice(0, 300));
    if (d.method === 'Log.entryAdded' && d.params.entry.level === 'error') consoleErrors.push('log: ' + d.params.entry.text + ' ' + (d.params.entry.url || ''));
  });
  await send('Runtime.enable'); await send('Page.enable'); await send('Log.enable');
  await goto(base); await ev('localStorage.clear()'); await goto(base);

  const opts = await ev(`[...document.querySelectorAll('#article option')].map((o,i)=>i+'|'+o.textContent)`);
  const idx = JSON.parse(await ev(`fetch('data/articles.json').then(r=>r.text())`));
  const select = async i => { await ev(`(()=>{const s=document.querySelector('#article');s.value='${i}';s.dispatchEvent(new Event('change'))})()`); await sleep(700); };
  const aiIdx = lv => idx.articles.findIndex(a => a.slug === 'ai_island_temple' && a.level === lv);
  const radios = () => ev(`[...document.querySelectorAll('input[name=gram]')].map(e=>({g:e.dataset.grammar||null,n:!!e.dataset.grammarNone,c:e.checked}))`);
  const clickRadio = sel => ev(`(()=>{const el=document.querySelector('${sel}');if(!el)return 'nf';el.click();return 'ok'})()`);
  const captureCopy = async () => { await ev(`window.__copied=null;navigator.clipboard.writeText=function(t){window.__copied=t;return Promise.resolve()}`); await ev(`document.querySelector('#copy').click()`); await sleep(500); return ev(`window.__copied`); };
  const parseJson = t => JSON.parse(t.slice(t.indexOf('```json') + 7, t.lastIndexOf('```')));

  for (const level of ['a2', 'b1b']) {
    const label = level === 'a2' ? 'Standard' : 'Advanced';
    const ent = idx.articles.find(a => a.slug === 'ai_island_temple' && a.level === level);
    const dat = JSON.parse(await ev(`fetch('${ent.data}').then(r=>r.text())`));
    await ev('localStorage.clear()'); await goto(base);
    await select(aiIdx(level));
    const P = `AI島 ${label}: `;
    // ---- KP/KWロック表示 ----
    const locked = await ev(`[...document.querySelectorAll('#candidates .lockitem')].map(e=>({t:e.querySelector('strong').textContent,g:e.querySelector('.ja').textContent}))`);
    rec(P + 'confirmed KP/KW shown as 10 locked items (no checkbox)', locked.length === 10 && (await ev(`document.querySelectorAll('input[data-term]').length`)) === 0, String(locked.length));
    const exp = dat.kp_confirmed.selection;
    rec(P + 'locked items = user-confirmed English + Japanese gloss (verbatim, in category order)', exp.every((r, i) => locked[i].t === r.term && locked[i].g.includes(r.ja_gloss) && locked[i].g.includes('正式訳')));
    const groups = await ev(`[...document.querySelectorAll('#candidates .group')].map(e=>e.textContent)`);
    rec(P + 'category headers 3/2/5 confirmed', groups.length === 3 && groups[0].includes('3件') && groups[1].includes('2件') && groups[2].includes('5件'), groups.join(' // '));
    rec(P + 'lock banner shown, old candidate hint hidden', (await ev(`document.querySelector('.lockbox').textContent`)).includes('再選定は不要') && (await ev(`document.querySelector('#khint').hidden`)) === true);
    // ---- 文法: Top1/Top2のみ・ラジオ・0件選択肢 ----
    const gTitles = await ev(`[...document.querySelectorAll('#grammars .grammar:not(.gnone) strong')].map(e=>e.textContent)`);
    const gRanks = await ev(`[...document.querySelectorAll('#grammars .rank')].map(e=>e.textContent)`);
    rec(P + 'grammar shows exactly Top1/Top2 in AI order with rank badges', gTitles.length === 2 && gRanks.join(',') === 'Top 1,Top 2' && gTitles.join('|') === dat.grammar.map(g => g.title).join('|'), gRanks.join(',') + ' ' + gTitles.join('|'));
    const gBodies = await ev(`[...document.querySelectorAll('#grammars .grammar:not(.gnone) p')].map(e=>e.textContent)`);
    rec(P + 'grammar full explanation shown verbatim (both)', gBodies.every((b, i) => b === dat.grammar[i].explanation_full));
    rec(P + 'grammar explanation text keeps line breaks (pre-wrap)', (await ev(`getComputedStyle(document.querySelector('#grammars .grammar p')).whiteSpace`)) === 'pre-wrap');
    const rs0 = await radios();
    rec(P + 'radios: 2 candidates + 1 explicit "none" option; initially none checked (undecided)', rs0.length === 3 && rs0[2].n && rs0.every(r => !r.c), JSON.stringify(rs0));
    rec(P + 'old-form 0-grammar not carried: counter says 未決定', (await ev(`document.querySelector('#grammarCount').textContent`)).includes('未決定'));
    const bodyTxt = await ev('document.body.innerText');
    rec(P + 'hidden 3rd+ candidates do not appear in DOM', dat.grammar_spec.hidden_ids.length > 0 && !(await ev(`document.documentElement.innerHTML`)).includes(dat.grammar_spec.hidden_ids[0]));
    // ---- 未決定では送信/コピー不可 ----
    await ev(`window.__opened=null;window.open=function(u){window.__opened=u;return null}`);
    await ev(`document.querySelector('#send').click()`);
    rec(P + 'send blocked while undecided (no window.open, message shown)', (await ev(`window.__opened`)) === null && (await ev(`document.querySelector('#status').textContent`)).includes('文法が未決定'));
    const c0 = await captureCopy();
    rec(P + 'copy blocked while undecided', c0 === null);
    // ---- 排他(最大1件) ----
    await clickRadio('input[data-grammar="' + dat.grammar[0].id + '"]');
    let rs = await radios();
    rec(P + 'select Top 1 -> exactly 1 checked', rs.filter(r => r.c).length === 1 && rs[0].c);
    await clickRadio('input[data-grammar="' + dat.grammar[1].id + '"]');
    rs = await radios();
    rec(P + 'select Top 2 replaces Top 1 (2 simultaneous impossible)', rs.filter(r => r.c).length === 1 && rs[1].c && !rs[0].c);
    rec(P + 'counter 1/1', (await ev(`document.querySelector('#stats').textContent`)).includes('1 / 1'));
    // ---- 1件選択の送信内容 ----
    const c1 = await captureCopy();
    rec(P + 'copy works after selection; text states KP/KW confirmed + Top 2 title', typeof c1 === 'string' && c1.includes('ユーザー確定済み') && c1.includes('Top 2｜' + dat.grammar[1].title), String(c1 && c1.length));
    const j1 = parseJson(c1);
    rec(P + 'payload selection KP/KW == confirmed 10 verbatim', ['key_phrase', 'extra_explanation', 'meaning_display'].every(k => JSON.stringify(j1.selection[k]) === JSON.stringify(exp.filter(r => r.category === ({ key_phrase: 1, extra_explanation: 2, meaning_display: 3 })[k]))));
    rec(P + 'payload grammar = 1 item (Top 2) with rank, full explanation, sha', j1.selection.grammar.length === 1 && j1.selection.grammar[0].rank === 2 && j1.selection.grammar[0].explanation_full === dat.grammar[1].explanation_full && j1.selection.grammar[0].explanation_sha256 === dat.grammar[1].explanation_sha256 && j1.grammar_status === 'user_selected_one');
    rec(P + 'payload sha/limits/locked flag', j1.article.text_sha256 === dat.kp_confirmed.text_sha256 && j1.article.candidates_sha256 === dat.kp_confirmed.candidates_sha256 && j1.limits.grammar === 1 && j1.kp_confirmed.locked === true && j1.counts.total_highlight === 10 && j1.counts.grammar === 1 && j1.production_connected === false);
    // ---- 0件(明示選択) ----
    await clickRadio('input[data-grammar-none]');
    rs = await radios();
    rec(P + 'explicit none -> only none checked, counter "0件を選択済み"', rs.filter(r => r.c).length === 1 && rs[2].c && (await ev(`document.querySelector('#grammarCount').textContent`)).includes('0件を選択済み'));
    const c2 = await captureCopy(); const j2 = parseJson(c2);
    rec(P + 'payload none: grammar [] + user_selected_none + KP/KW unchanged', j2.selection.grammar.length === 0 && j2.grammar_status === 'user_selected_none' && j2.grammar_decision.state === 'none' && j2.counts.total_highlight === 10);
    // ---- 旧フォームの保存状態(文法2件+別KP選択)を注入しても、KP/KW不変・文法は未決定に戻る ----
    const key = 'ai_island_temple__' + level;
    await ev(`localStorage.setItem('eigo-kp-form-v3', JSON.stringify({'${key}': {choices: {'carry over': 3, 'obstacle': 1}, grammar: {'${dat.grammar[0].id}': true, '${dat.grammar[1].id}': true}, comment: 'old'}}))`);
    await goto(base); await select(aiIdx(level));
    rs = await radios();
    const locked2 = await ev(`[...document.querySelectorAll('#candidates .lockitem')].map(e=>e.querySelector('strong').textContent)`);
    rec(P + 'old saved state (2 grammar + stray choices): grammar reset to undecided, KP/KW unchanged', rs.every(r => !r.c) && locked2.join('|') === exp.map(r => r.term).join('|') && (await ev(`document.querySelector('#grammarCount').textContent`)).includes('未決定'));
  }
  // ---- 他記事(旧形式)はKP選定UIが従来どおり・文法枠は候補なし表示 ----
  const ukI = idx.articles.findIndex(a => a.slug.startsWith('uk_train') && a.data && a.level === 'b1b');
  if (ukI >= 0) {
    await select(ukI);
    const terms = await ev(`[...document.querySelectorAll('input[data-term][data-cat="1"]')].map(e=>e.dataset.term)`);
    const r1 = []; for (let i = 0; i < 4; i++) r1.push(await ev(`(()=>{const el=[...document.querySelectorAll('input[data-term]')].find(e=>e.dataset.term==="${terms[i]}"&&e.dataset.cat==="1");if(!el)return 'nf';if(el.disabled)return 'disabled';el.click();return 'ok'})()`));
    rec('other article: KP selection UI unchanged (limit 3 on category 1)', terms.length > 3 && r1.join(',') === 'ok,ok,ok,disabled', r1.join(','));
    rec('other article: no grammar candidates -> no radios, notice shown, send not blocked', (await ev(`document.querySelectorAll('input[name=gram]').length`)) === 0 && (await ev(`document.querySelector('#grammarNotice').hidden`)) === false);
    const cc = await captureCopy();
    rec('other article: copy works without grammar decision', typeof cc === 'string' && cc.includes('文法'));
  }
  rec('no console errors/exceptions', consoleErrors.length === 0, consoleErrors.join(' | '));
} catch (e) {
  rec('script error', false, String(e));
} finally {
  try { ws && ws.close(); } catch (e) { }
  proc.kill(); await sleep(500);
  try { fs.rmSync(udd, { recursive: true, force: true }); } catch (e) { }
  const failed = results.filter(r => !r.ok).length;
  console.log(`SUMMARY pass=${results.length - failed} fail=${failed}`);
  process.exit(failed ? 1 : 0);
}
