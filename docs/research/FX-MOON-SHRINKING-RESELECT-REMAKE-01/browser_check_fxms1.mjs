// FX-MOON-SHRINKING-RESELECT-REMAKE-01 委任_01: 公開V3フォームの月(Std/Adv)DOM確認。用法: node browser_check_fxms1.mjs <baseUrl> <chromePath> [port]
import { spawn } from 'node:child_process';
import fs from 'node:fs'; import os from 'node:os'; import path from 'node:path';
const base = process.argv[2], chrome = process.argv[3], port = Number(process.argv[4] || 9361);
const udd = fs.mkdtempSync(path.join(os.tmpdir(), 'fxms1-chrome-'));
const proc = spawn(chrome, ['--headless=new', '--disable-gpu', '--no-first-run', `--remote-debugging-port=${port}`, `--user-data-dir=${udd}`, 'about:blank'], { stdio: 'ignore' });
const sleep = ms => new Promise(r => setTimeout(r, ms)); const errs = []; let bad = 0;
const rec = (n, ok, d = '') => { if (!ok) bad++; console.log((ok ? 'PASS ' : 'FAIL ') + n + (d ? ' :: ' + d : '')); };
async function getWs() { for (let i = 0; i < 50; i++) { try { const j = await (await fetch(`http://127.0.0.1:${port}/json`)).json(); const p = j.find(x => x.type === 'page'); if (p) return p.webSocketDebuggerUrl; } catch (e) { } await sleep(200); } throw new Error('no chrome'); }
let ws, id = 0; const pend = {};
const send = (method, params = {}) => new Promise((res, rej) => { const i = ++id; pend[i] = { res, rej }; ws.send(JSON.stringify({ id: i, method, params })); });
const ev = async e => { const r = await send('Runtime.evaluate', { expression: e, awaitPromise: true, returnByValue: true }); if (r.exceptionDetails) throw new Error(JSON.stringify(r.exceptionDetails).slice(0, 300)); return r.result.value; };
try {
  ws = new WebSocket(await getWs()); await new Promise(r => ws.addEventListener('open', r));
  ws.addEventListener('message', m => { const d = JSON.parse(m.data); if (d.id && pend[d.id]) { d.error ? pend[d.id].rej(new Error(JSON.stringify(d.error))) : pend[d.id].res(d.result); delete pend[d.id]; return; } if (d.method === 'Runtime.exceptionThrown') errs.push(JSON.stringify(d.params.exceptionDetails).slice(0, 200)); if (d.method === 'Runtime.consoleAPICalled' && d.params.type === 'error') errs.push('console.error'); });
  await send('Runtime.enable'); await send('Page.enable');
  for (const lv of ['a2', 'b1b']) {
    await send('Page.navigate', { url: `${base}?a=moon_shrinking__${lv}` }); await sleep(2500);
    const dat = JSON.parse(await ev(`fetch('data/moon_shrinking__${lv}__prod.json').then(r=>r.text())`));
    const sel = await ev(`document.querySelector('#article').selectedOptions[0].textContent`);
    rec(lv + ' 記事枠選択=月', sel.includes('月は少しずつ縮んでいる'), sel);
    const items = dat.phrases.concat(dat.words);
    const dom = await ev(`[...document.querySelectorAll('#candidates .item')].map(i=>({t:i.querySelector('label').textContent,txt:i.innerText}))`);
    rec(lv + ' 候補件数・順序=データ', dom.length === items.length && items.every((it, k) => dom[k].t === it.term), dom.length + '/' + items.length);
    rec(lv + ' 全候補に日本語訳', items.every((it, k) => dom[k].txt.includes(it.meaning_ja)), '');
    const g = await ev(`[...document.querySelectorAll('#grammars .grammar')].filter(g=>!g.querySelector('input[data-grammar-none]')).map(g=>({t:g.querySelector('strong').textContent,p:g.querySelector('p').textContent,id:g.querySelector('input').dataset.grammar||''}))`);
    rec(lv + ' 文法件数=' + dat.grammar.length + '・名称/解説全文=データ', g.length === dat.grammar.length && dat.grammar.every((x, k) => g[k].t === x.title && g[k].p === x.body), String(g.length));
  }
  rec('console error 0', errs.length === 0, errs.join(' | '));
} catch (e) { bad++; console.log('ERROR ' + e.message); } finally { try { ws && ws.close(); } catch (e) { } proc.kill(); console.log(bad ? 'FAILED ' + bad : 'ALL PASS'); process.exit(bad ? 1 : 0); }
