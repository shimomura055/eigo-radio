// headless Chrome(CDP)でフォームの実DOM動作を確認する。用法: node browser_check_01.mjs <baseUrl> <chromePath> [port]
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const base = process.argv[2];
const chrome = process.argv[3];
const port = Number(process.argv[4] || 9333);
const udd = fs.mkdtempSync(path.join(os.tmpdir(), 'selform-chrome-'));
const proc = spawn(chrome, ['--headless=new', '--mute-audio', '--autoplay-policy=user-gesture-required', '--disable-gpu', '--no-first-run', `--remote-debugging-port=${port}`, `--user-data-dir=${udd}`, 'about:blank'], { stdio: 'ignore' });
process.on('exit', () => { try { proc.kill(); } catch (e) {} });  // PLAYWRIGHT-AUDIO-SAFETY-01: 異常終了でもChromeを残さない
const results = []; const consoleErrors = [];
const rec = (name, ok, detail = '') => { results.push({ name, ok, detail }); console.log((ok ? 'PASS ' : 'FAIL ') + name + (detail ? ' :: ' + detail : '')); };
const sleep = ms => new Promise(r => setTimeout(r, ms));

async function getWs() {
  for (let i = 0; i < 50; i++) {
    try { const r = await fetch(`http://127.0.0.1:${port}/json`); const j = await r.json(); const p = j.find(x => x.type === 'page'); if (p) return p.webSocketDebuggerUrl; } catch (e) { }
    await sleep(200);
  }
  throw new Error('chrome debug port not ready');
}
let ws, id = 0; const pend = {};
function send(method, params = {}) { return new Promise((res, rej) => { const i = ++id; pend[i] = { res, rej }; ws.send(JSON.stringify({ id: i, method, params })); }); }
async function ev(expr) { const r = await send('Runtime.evaluate', { expression: expr, awaitPromise: true, returnByValue: true }); if (r.exceptionDetails) throw new Error(JSON.stringify(r.exceptionDetails).slice(0, 300)); return r.result.value; }
async function goto(url) { await send('Page.navigate', { url }); await sleep(1500); }

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

  await goto(base);
  const q = s => `document.querySelector('${s}')`;
  const sel0 = await ev(`${q('#article')}.selectedOptions[0].textContent`);
  rec('page loads, default article = 猿の手 Advanced', sel0.includes('猿の手') && sel0.includes('Advanced'), sel0);
  rec('10 options in selector (9 slots + UI check dummy)', (await ev(`${q('#article')}.options.length`)) === 10);
  rec('candidates: 7 phrases + 4 words rendered', (await ev(`document.querySelectorAll('.item').length`)) === 11);
  rec('source note (DEV Trial-02) shown', (await ev(`${q('#srcnote')}.textContent`)).includes('DEV Trial-02'));
  rec('rescued flag displayed', (await ev(`document.querySelectorAll('.flag').length`)) >= 1);
  rec('grammar notice: 候補なし・要生成, no grammar items', (await ev(`${q('#grammarNotice')}.textContent`)).includes('要生成') && (await ev(`document.querySelectorAll('.grammar').length`)) === 0);

  const click = (term, cat) => ev(`(()=>{const el=[...document.querySelectorAll('input[data-term]')].find(e=>e.dataset.term==="${term}"&&e.dataset.cat==="${cat}");if(!el)return 'nf';if(el.disabled)return 'disabled';el.click();return 'ok'})()`);
  const stat = () => ev(`[...document.querySelectorAll('.stat')].map(e=>e.querySelector('strong').textContent+'|'+e.className).join(' ; ')`);
  const checkedN = () => ev(`[...document.querySelectorAll('input[data-term]')].filter(e=>e.checked).length`);
  const phrases = ['accept no responsibility', 'pay off the house', 'interfere with fate', 'pulled free', 'caught in the machinery', 'wail of loss', "shake one's husband awake"];
  const words = ['compensation', 'snatch', 'deserted', 'burial'];
  for (let i = 0; i < 3; i++) await click(phrases[i], 1);
  rec('(1) 3 chosen -> stat full', (await stat()).startsWith('3 / 3|stat full'), await stat());
  rec('(1) 4th disabled', (await click(phrases[3], 1)) === 'disabled');
  rec('(1) locked styling present', await ev(`document.querySelectorAll('.pick.locked').length>0`));
  await click(phrases[3], 2); await click(phrases[4], 2);
  const s5 = await stat();
  rec('(1)+(2)=5 -> stat full, 6th (2) disabled', s5.includes('5 / 5|stat full') && (await click(phrases[5], 2)) === 'disabled', s5);
  for (let i = 0; i < 4; i++) await click(words[i], 3);
  await click(phrases[5], 3); await click(phrases[6], 3);
  const s11 = await stat();
  rec('total 11 (not yet full)', s11.includes('11 / 12|stat'), s11);
  rec('same item switch (1)->(2) allowed at (1)+(2)=5? (expected: allowed, (1) 3->2,(2) 2->3 => (1)+(2) stays 5)', (await click(phrases[0], 2)) === 'disabled' ? false : true);
  rec('after switch, item has exactly one checked cat', (await ev(`[...document.querySelectorAll('input[data-term]')].filter(e=>e.dataset.term==="${phrases[0]}"&&e.checked).length`)) === 1);
  const n1 = await checkedN();
  await click(phrases[0], 2);   // 解除
  rec('deselect at limit works', (await checkedN()) === n1 - 1, `${n1}->${await checkedN()}`);
  // 現在: ③ を含め 10件
  await click(phrases[0], 3);
  const nChecked = await checkedN();
  rec('checked count before reload recorded', nChecked >= 10, String(nChecked));

  await goto(base);
  rec('state persists after reload', (await checkedN()) === nChecked);

  await ev(`(()=>{const t=document.querySelector('#comment');t.value='別の上級単語を2件追加探索してください';t.dispatchEvent(new Event('input',{bubbles:true}))})()`);
  await goto(base);
  rec('comment persists after reload', (await ev(`${q('#comment')}.value`)).includes('追加探索'));

  await ev(`(()=>{const s=document.querySelector('#article');s.value='9';s.dispatchEvent(new Event('change'))})()`); await sleep(700);
  rec('dummy article: 3 grammar items shown', (await ev(`document.querySelectorAll('.grammar').length`)) === 3);
  rec('dummy: selection empty (no cross-article mixing)', (await checkedN()) === 0);
  rec('dummy: comment empty', (await ev(`${q('#comment')}.value`)) === '');
  await ev(`document.querySelector('input[data-grammar="g1"]').click()`); await ev(`document.querySelector('input[data-grammar="g2"]').click()`);
  rec('grammar 2 chosen -> 3rd disabled', await ev(`document.querySelector('input[data-grammar="g3"]').disabled`));
  const sg = await stat();
  rec('grammar stat full', sg.includes('2 / 2|stat full'), sg);
  await ev(`document.querySelector('input[data-grammar="g1"]').click()`);
  rec('grammar deselect re-enables 3rd', !(await ev(`document.querySelector('input[data-grammar="g3"]').disabled`)));
  await ev(`(()=>{const s=document.querySelector('#article');s.value='5';s.dispatchEvent(new Event('change'))})()`); await sleep(700);
  rec('switch back: 猿の手 selection retained', (await checkedN()) === nChecked);
  rec('switch back: comment retained', (await ev(`${q('#comment')}.value`)).includes('追加探索'));
  await ev(`(()=>{const s=document.querySelector('#article');s.value='0';s.dispatchEvent(new Event('change'))})()`); await sleep(400);
  rec('unregistered slot shows 未登録 message', (await ev(`${q('#candidates')}.textContent`)).includes('未登録'));
  await ev(`(()=>{const s=document.querySelector('#article');s.value='5';s.dispatchEvent(new Event('change'))})()`); await sleep(700);

  await ev(`window.__opened=null;window.open=function(u){window.__opened=u;return null}`);
  await ev(`document.querySelector('#send').click()`);
  const url = await ev(`window.__opened`);
  rec('send builds chatgpt URL', typeof url === 'string' && url.startsWith('https://chatgpt.com/?q='), String(url).slice(0, 60));
  if (url) {
    const msg = decodeURIComponent(url.slice(url.indexOf('?q=') + 3));
    rec('send message contains selection + comment + JSON', msg.includes('① Key Phrase') && msg.includes('追加探索') && msg.includes('"schema":"eigo_radio_selection_result_v1"'));
    rec('send URL length <= 6000', url.length <= 6000, String(url.length));
  }
  await ev(`document.querySelector('#copy').click()`); await sleep(600);
  const st = await ev(`${q('#status')}.textContent`);
  rec('copy: status message shown (clipboard API or fallback)', st.includes('コピーしました') || st.includes('手動'), st);
  await ev(`Object.defineProperty(navigator,'clipboard',{value:{writeText:()=>Promise.reject(new Error('denied'))},configurable:true})`);
  await ev(`document.querySelector('#copy').click()`); await sleep(600);
  const st2 = await ev(`${q('#status')}.textContent`); const fb = await ev(`({hidden:document.querySelector('#fallback').hidden,len:document.querySelector('#fallback').value.length})`);
  rec('copy fallback path: textarea filled', fb.hidden === false && fb.len > 100 && (st2.includes('代替方式') || st2.includes('手動')), st2 + ' len=' + fb.len);
  rec('no console errors/exceptions', consoleErrors.length === 0, consoleErrors.join(' | '));
} catch (e) {
  rec('script error', false, String(e));
} finally {
  try { ws && ws.close(); } catch (e) { }
  proc.kill();
  await sleep(500);
  try { fs.rmSync(udd, { recursive: true, force: true }); } catch (e) { }
  const failed = results.filter(r => !r.ok).length;
  console.log(`SUMMARY pass=${results.length - failed} fail=${failed}`);
  process.exit(failed ? 1 : 0);
}
