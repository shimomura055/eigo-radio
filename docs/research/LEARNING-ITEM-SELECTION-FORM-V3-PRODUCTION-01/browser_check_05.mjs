// headless Chrome(CDP)でフォームの実DOM動作を確認する(委任_05: 理由なし候補は理由欄非表示・理由ありは表示、上限ロジック不変)。用法: node browser_check_05.mjs <baseUrl> <chromePath> [port]
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const base = process.argv[2];
const chrome = process.argv[3];
const port = Number(process.argv[4] || 9334);
const udd = fs.mkdtempSync(path.join(os.tmpdir(), 'selform3-chrome-'));
const proc = spawn(chrome, ['--headless=new', '--disable-gpu', '--no-first-run', `--remote-debugging-port=${port}`, `--user-data-dir=${udd}`, 'about:blank'], { stdio: 'ignore' });
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

  // 委任_05: 全記事枠で、理由がある候補は「AI理由・確認用」を表示し、理由がない候補は理由欄(details)自体が存在しない。「AI理由なし」「（なし）」は画面のどこにも出ない
  const idx = JSON.parse(await ev(`fetch('data/articles.json').then(r=>r.text())`));
  let withReason = 0, withoutReason = 0, articlesChecked = 0;
  for (let i = 0; i < idx.articles.length; i++) {
    const ent = idx.articles[i]; if (!ent.data) continue;
    const dat = JSON.parse(await ev(`fetch('${ent.data}').then(r=>r.text())`));
    await ev(`(()=>{const s=document.querySelector('#article');s.value='${i}';s.dispatchEvent(new Event('change'))})()`); await sleep(700);
    const items = dat.phrases.concat(dat.words); articlesChecked++;
    const dom = await ev(`[...document.querySelectorAll('#candidates .item')].map(i=>({t:i.querySelector('label').textContent,w:!!i.querySelector('details.why'),b:i.querySelector('.whybody')?i.querySelector('.whybody').textContent:''}))`);
    const ok = dom.length === items.length && items.every((it, k) => { const has = !!(it.reason_ja || '').trim(); const d = dom[k]; return d.t === it.term && d.w === has && (!has || d.b.includes(it.reason_ja.trim())); });
    items.forEach(it => ((it.reason_ja || '').trim() ? withReason++ : withoutReason++));
    rec(ent.slug + '/' + ent.level + ': reason pane iff reason exists (' + items.filter(it => (it.reason_ja || '').trim()).length + '/' + items.length + ' with reason)', ok);
    const body = await ev(`document.body.innerText`);
    rec(ent.slug + '/' + ent.level + ': no "AI理由なし"/"（なし）" text', !body.includes('AI理由なし') && !body.includes('（なし）'));
    if (dat.data_warnings) rec(ent.slug + ': data_warnings shown in srcnote', (await ev(`document.querySelector('#srcnote').textContent`)).includes('データ警告'));
  }
  rec('covered both cases (with reason>0, without reason>0)', withReason > 0 && withoutReason > 0, withReason + ' / ' + withoutReason);
  // 12件満載(uk_train b1b)で選択上限(UI不変)と、理由なし候補を選んでも送信が崩れない確認
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
  // 理由なし記事(猿の手 DEV Trial)を選んで送信文面に「AI理由なし」が出ない
  const mpKey = opts.find(x => x.includes('猿の手') && !x.includes('Production候補'));
  if (mpKey) {
    await ev(`(()=>{const s=document.querySelector('#article');s.value='${mpKey.split(':')[0]}';s.dispatchEvent(new Event('change'))})()`); await sleep(700);
    const mt = await ev(`[...document.querySelectorAll('input[data-term][data-cat="1"]')].map(e=>e.dataset.term)`);
    await click(mt[0], 1);
    await ev(`window.__opened=null;window.open=function(u){window.__opened=u;return null}`);
    await ev(`document.querySelector('#send').click()`);
    const u2 = await ev(`window.__opened`);
    rec('no-reason article send: text has no "AI理由なし"', typeof u2 === 'string' ? !urlMsg(u2).includes('AI理由なし') : true, String(u2 && u2.length));
  }
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
