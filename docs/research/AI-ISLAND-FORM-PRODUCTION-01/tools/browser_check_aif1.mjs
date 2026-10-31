// AI-ISLAND-FORM-PRODUCTION-01 委任_01: AI島Standard/Advancedの実DOM確認(headless Chrome CDP)。用法: node browser_check_aif1.mjs <baseUrl> <chromePath> [port]
// 確認: 記事枠(重複/旧版なし)・候補の英語/日本語訳/AI理由・文法(名称+解説全文+例文)の表示と元データ一致・選定上限(①3/①+②5/全12/文法2)・
//       送信payload(buildStructured)とコピー本文に文法解説全文・candidate_id・sha・日本語訳が欠落なく入ること。
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const base = process.argv[2];
const chrome = process.argv[3];
const port = Number(process.argv[4] || 9341);
const udd = fs.mkdtempSync(path.join(os.tmpdir(), 'aif1-chrome-'));
const proc = spawn(chrome, ['--headless=new', '--mute-audio', '--autoplay-policy=user-gesture-required', '--disable-gpu', '--no-first-run', `--remote-debugging-port=${port}`, `--user-data-dir=${udd}`, 'about:blank'], { stdio: 'ignore' });
process.on('exit', () => { try { proc.kill(); } catch (e) {} });  // PLAYWRIGHT-AUDIO-SAFETY-01: 異常終了でもChromeを残さない
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
  const aiOpts = opts.filter(o => o.includes('AIの仮想の島'));
  rec('article select: AIの仮想の島 appears exactly twice (Standard+Advanced), no old Production候補/evidence duplicate', aiOpts.length === 2 && aiOpts.some(o => o.includes('Standard')) && aiOpts.some(o => o.includes('Advanced')) && !aiOpts.some(o => o.includes('Production候補') || o.includes('evidence')), aiOpts.join(' // '));
  rec('AIの仮想の島 slots are in the first two positions', opts[0].includes('AIの仮想の島') && opts[1].includes('AIの仮想の島'), opts.slice(0, 2).join(' // '));
  const idx = JSON.parse(await ev(`fetch('data/articles.json').then(r=>r.text())`));

  for (const level of ['a2', 'b1b']) {
    const label = level === 'a2' ? 'Standard' : 'Advanced';
    const ent = idx.articles.find(a => a.slug === 'ai_island_temple' && a.level === level);
    const dat = JSON.parse(await ev(`fetch('${ent.data}').then(r=>r.text())`));
    const optIdx = idx.articles.indexOf(ent);
    await ev(`(()=>{localStorage.clear();const s=document.querySelector('#article');s.value='${optIdx}';s.dispatchEvent(new Event('change'))})()`); await sleep(900);
    const tag = 'AI島 ' + label;
    // --- 候補表示
    const items = dat.phrases.concat(dat.words);
    const dom = await ev(`[...document.querySelectorAll('#candidates .item')].map(i=>({t:i.querySelector('label').textContent,txt:i.innerText,w:!!i.querySelector('details.why'),b:i.querySelector('.whybody')?i.querySelector('.whybody').textContent:''}))`);
    rec(tag + ': candidate count/order = data (phrases then words)', dom.length === items.length && items.every((it, k) => dom[k].t === it.term), dom.length + '/' + items.length);
    rec(tag + ': every candidate shows its Japanese gloss (data.meaning_ja); all gloss status official', items.every((it, k) => dom[k].txt.includes(it.meaning_ja) && it.ja_gloss_status === 'official'), '');
    rec(tag + ': every candidate shows AI reason verbatim', items.every((it, k) => dom[k].w && dom[k].b.includes(it.reason_ja.trim())), '');
    rec(tag + ': AI reason <= 40 chars', items.every(it => [...it.reason_ja].length <= 40), items.map(it => [...it.reason_ja].length).join(','));
    // --- 文法表示
    const gdom = await ev(`[...document.querySelectorAll('#grammars .grammar')].map(g=>({t:g.querySelector('strong').textContent,p:g.querySelector('p').textContent,s:g.querySelector('.sample')?g.querySelector('.sample').textContent:'',id:g.querySelector('input').dataset.grammar}))`);
    rec(tag + ': grammar count = data (' + dat.grammar.length + ')', gdom.length === dat.grammar.length && gdom.length > 0, String(gdom.length));
    rec(tag + ': grammar name + full explanation + example identical to data (verbatim)', dat.grammar.every((g, k) => gdom[k].id === g.id && gdom[k].t === g.title && gdom[k].p === g.body && gdom[k].s === g.example && g.body === g.explanation_full), '');
    rec(tag + ': explanation contains 【日本語訳】 and 【文法・構文の仕組み】', dat.grammar.every(g => g.body.includes('【日本語訳】') && g.body.includes('【文法・構文の仕組み】')), '');
    // --- 上限
    const click = (term, cat) => ev(`(()=>{const el=[...document.querySelectorAll('input[data-term]')].find(e=>e.dataset.term==="${term}"&&e.dataset.cat==="${cat}");if(!el)return 'nf';if(el.disabled)return 'disabled';el.click();return 'ok'})()`);
    const terms = items.map(i => i.term);
    const r1 = []; for (let i = 0; i < 4; i++) r1.push(await click(terms[i], 1));
    rec(tag + ': limit 1 <=3 (4th disabled)', r1.join(',') === 'ok,ok,ok,disabled', r1.join(','));
    const r2 = []; for (let i = 3; i < 6; i++) r2.push(await click(terms[i], 2));
    rec(tag + ': limit 1+2 <=5', r2.join(',') === 'ok,ok,disabled', r2.join(','));
    const r3 = []; for (let i = 5; i < items.length; i++) r3.push(await click(terms[i], 3));
    rec(tag + ': 3 fills remaining candidates (<=12)', r3.every(x => x === 'ok'), r3.join(','));
    const gc = []; for (const g of dat.grammar) gc.push(await ev(`(()=>{const el=document.querySelector('input[data-grammar="${g.id}"]');if(el.disabled)return 'disabled';el.click();return 'ok'})()`));
    const expectG = dat.grammar.map((_, k) => k < 2 ? 'ok' : 'disabled');
    rec(tag + ': grammar limit 2 (independent frame; 3rd+ disabled)', gc.join(',') === expectG.join(','), gc.join(','));
    rec(tag + ': grammar counter shows 2/2', (await ev(`document.querySelector('#grammarCount').textContent`)).includes('2/2'));
    await ev(`(()=>{const c=document.querySelector('#comment');c.value='AI島 検証コメント: 日本語\\n2行目';c.dispatchEvent(new Event('input'))})()`);
    // --- 送信payload
    const st = JSON.parse(await ev(`JSON.stringify(FL.buildStructured(D,get()))`));
    const g2 = dat.grammar.slice(0, 2);
    rec(tag + ': payload grammar = first 2 with explanation_full verbatim + candidate_id + explanation_sha256 + provided',
      st.selection.grammar.length === 2 && g2.every((g, k) => { const r = st.selection.grammar[k]; return r.id === g.id && r.candidate_id === g.candidate_id && r.title === g.title && r.explanation_full === g.explanation_full && r.explanation_sha256 === g.explanation_sha256 && r.explanation_status === 'provided' && r.example === g.example; }), '');
    const kpAll = st.selection.key_phrase.concat(st.selection.extra_explanation, st.selection.meaning_display);
    const byTerm = Object.fromEntries(items.map(i => [i.term, i]));
    rec(tag + ': payload KP items keep candidate_id/kind/ja_gloss(official) identical to data', kpAll.length === items.length && kpAll.every(r => { const it = byTerm[r.term]; return it && r.candidate_id === it.candidate_id && r.kind === it.kind && r.ja_gloss === it.ja_gloss && r.ja_gloss_status === 'official'; }), String(kpAll.length));
    rec(tag + ': payload categories 3/2/rest and counts', st.selection.key_phrase.length === 3 && st.selection.extra_explanation.length === 2 && st.selection.meaning_display.length === items.length - 5 && st.counts.total_highlight === items.length && st.counts.grammar === 2, JSON.stringify(st.counts));
    rec(tag + ': payload carries candidates_sha256 / text_sha256 / grammar_status / comment', st.article.candidates_sha256 === dat.candidates_sha256 && st.article.text_sha256 === dat.source.text_sha256 && st.grammar_status === 'candidates_available' && st.comment.includes('2行目'), '');
    // --- コピー本文(クリップボードをstub)
    await ev(`window.__clip=null;navigator.clipboard.writeText=function(t){window.__clip=t;return Promise.resolve()}`);
    await ev(`document.querySelector('#copy').click()`); await sleep(400);
    const clip = await ev(`window.__clip`);
    const m = /```json\n([\s\S]*)\n```/.exec(clip || '');
    let cj = null; try { cj = JSON.parse(m[1]); } catch (e) { }
    rec(tag + ': copy text contains full grammar explanations of both selected items', !!clip && g2.every(g => clip.includes(g.explanation_full) && clip.includes(g.example)), 'len=' + (clip ? clip.length : 0));
    rec(tag + ': copy JSON block parses; grammar explanation_full verbatim; candidates_all complete', !!cj && g2.every((g, k) => cj.selection.grammar[k].explanation_full === g.explanation_full) && !!cj.candidates_all && cj.candidates_all.length === items.length, '');
    // --- ChatGPT送信
    await ev(`window.__opened=null;window.open=function(u){window.__opened=u;return null};window.__clip=null`);
    await ev(`document.querySelector('#send').click()`); await sleep(500);
    const opened = await ev(`window.__opened`); const status = await ev(`document.querySelector('#status').textContent`); const clip2 = await ev(`window.__clip`);
    const info = opened ? 'ChatGPT URL opened, len=' + opened.length : 'URL too long -> auto-copy fallback (' + status.slice(0, 60) + '), clip len=' + (clip2 ? clip2.length : 0);
    rec(tag + ': send opens ChatGPT URL within limit or falls back to full-text copy (no silent truncation)', (!!opened && opened.length <= 6030) || (!opened && !!clip2 && g2.every(g => clip2.includes(g.explanation_full))), info);
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
