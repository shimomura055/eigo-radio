// headless Chrome(CDP)でフォームの実DOM動作を確認する(委任_04: 7+5 evidence(候補最大12・kind別cap 7/5)の表示と上限ロジック不変)。用法: node browser_check_04.mjs <baseUrl> <chromePath> [port]
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const base = process.argv[2];
const chrome = process.argv[3];
const port = Number(process.argv[4] || 9334);
const udd = fs.mkdtempSync(path.join(os.tmpdir(), 'selform3-chrome-'));
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
  await ev('localStorage.clear()'); await goto(base);

  const q = s => `document.querySelector('${s}')`;
  const opts = await ev(`[...document.querySelectorAll('#article option')].map((o,i)=>i+':'+o.textContent)`);
  const idxOf = key => Number(opts.find(o => o.includes(key)).split(':')[0]);
  const switchTo = async key => { await ev(`(()=>{const s=document.querySelector('#article');s.value='${idxOf(key)}';s.dispatchEvent(new Event('change'))})()`); await sleep(700); };
  const click = (term, cat) => ev(`(()=>{const el=[...document.querySelectorAll('input[data-term]')].find(e=>e.dataset.term==="${term}"&&e.dataset.cat==="${cat}");if(!el)return 'nf';if(el.disabled)return 'disabled';el.click();return 'ok'})()`);
  const urlMsg = u => decodeURIComponent(u.slice(u.indexOf('?q=') + 3));

  // 8件の7+5 evidence記事: 候補行数=データ件数、グループ見出しに上限(フレーズ7/単語5)、選択UI(①<=3/①+②<=5/①+②+③<=12)が12件でも崩れない
  const files = ['ai_island_temple__a2', 'ai_island_temple__b1b', 'uk_train_speaker_playback__a2', 'uk_train_speaker_playback__b1b', 'redelivery_fee__a2', 'redelivery_fee__b1b', 'melos__a2', 'melos__b1b'];
  const names = { ai_island_temple: 'AIの仮想の島', uk_train_speaker_playback: '英国の電車マナー', redelivery_fee: '再配達手数料', melos: '走れメロス' };
  for (const f of files) {
    const [slug, lv] = f.split('__'); const key = names[slug] + '｜Production候補・7+5 evidence';
    const dat = JSON.parse(await ev(`fetch('data/${f}__prod.json').then(r=>r.text())`));
    const lvLabel = lv === 'a2' ? 'Standard' : 'Advanced';
    const o = opts.find(x => x.includes(key) && x.includes(lvLabel));
    if (!o) { rec(f + ' option exists', false, 'not found'); continue; }
    await ev(`(()=>{const s=document.querySelector('#article');s.value='${o.split(':')[0]}';s.dispatchEvent(new Event('change'))})()`); await sleep(700);
    const rows = await ev(`document.querySelectorAll('#candidates .item').length`);
    const groups = await ev(`[...document.querySelectorAll('#candidates .group')].map(g=>g.textContent)`);
    rec(f + ': rows == data candidates', rows === dat.phrases.length + dat.words.length, rows + ' vs ' + (dat.phrases.length + dat.words.length));
    rec(f + ': group headers show kind cap (7/5)', groups[0] === `フレーズ（${dat.phrases.length}件／上限7件）` && groups[1] === `単語（${dat.words.length}件／上限5件）`, groups.join(' / '));
    rec(f + ': every row has gloss label 正式訳 and AI reason (summary has no "なし")', await ev(`[...document.querySelectorAll('#candidates .item')].every(i=>i.querySelector('.gl-official')&&!/（なし）/.test(i.querySelector('summary').textContent))`));
    if (dat.shortfall) { const sn = await ev(`document.querySelector('#srcnote').textContent`); rec(f + ': srcnote shows 上限12件/フレーズ最大7・単語最大5', sn.includes('上限12件') && sn.includes('フレーズ最大7') && sn.includes('単語最大5'), sn.slice(-90)); }
  }
  // 12件満載(uk_train b1b)で選択上限を確認(UI不変): ①3件で打止め、①+②5件、①+②+③12件
  const ukKey = opts.find(x => x.includes('英国の電車マナー｜Production候補・7+5 evidence') && x.includes('Advanced'));
  await ev(`(()=>{const s=document.querySelector('#article');s.value='${ukKey.split(':')[0]}';s.dispatchEvent(new Event('change'))})()`); await sleep(700);
  const terms = await ev(`[...document.querySelectorAll('input[data-term][data-cat="1"]')].map(e=>e.dataset.term)`);
  rec('uk b1b: 12 candidates listed', terms.length === 12, String(terms.length));
  const r1 = []; for (let i = 0; i < 4; i++) r1.push(await click(terms[i], 1));
  rec('limit: 4th cat1 is disabled (<=3)', r1.join(',') === 'ok,ok,ok,disabled', r1.join(','));
  const r2 = []; for (let i = 3; i < 6; i++) r2.push(await click(terms[i], 2));
  rec('limit: cat1+cat2 <=5', r2.join(',') === 'ok,ok,disabled', r2.join(','));
  const r3 = []; for (let i = 5; i < 12; i++) r3.push(await click(terms[i], 3));
  rec('limit: total 12 selectable', r3.every(x => x === 'ok'), r3.join(','));
  rec('stats show 12 / 12', (await ev(`document.querySelector('#stats').textContent`)).includes('12 / 12'));
  await ev(`window.__opened=null;window.open=function(u){window.__opened=u;return null}`);
  await ev(`document.querySelector('#send').click()`);
  const url = await ev(`window.__opened`);
  rec('send flow with 12 selected does not break (URL or copy guidance)', url === null || typeof url === 'string', String(url && url.length));
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
