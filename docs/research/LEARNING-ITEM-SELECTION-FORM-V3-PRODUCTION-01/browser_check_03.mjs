// headless Chrome(CDP)でフォームの実DOM動作を確認する(委任_03: candidate_id/kind/candidates_sha256が送信データに出ること)。用法: node browser_check_03.mjs <baseUrl> <chromePath> [port]
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

  // メロスa2(Production正式経路): 候補docのcandidate_id/sha/kindが送信文・コピーJSONに出る
  await switchTo('走れメロス');
  const dat = JSON.parse(await ev(`fetch('data/melos__a2__prod.json').then(r=>r.text())`));
  const byTerm = Object.fromEntries(dat.phrases.concat(dat.words).map(x => [x.term, x]));
  const terms = await ev(`[...document.querySelectorAll('input[data-term][data-cat="1"]')].map(e=>e.dataset.term)`);
  await click(terms[0], 1); await click(terms[1], 1); await click(terms[3], 2); await click(terms[4], 3);
  const sel = [[terms[0], 1], [terms[1], 1], [terms[3], 2], [terms[4], 3]];
  await ev(`window.__opened=null;window.open=function(u){window.__opened=u;return null}`);
  await ev(`document.querySelector('#send').click()`);
  const url = await ev(`window.__opened`);
  rec('send URL built (<=6000)', typeof url === 'string' && url.length <= 6000, String(url && url.length));
  if (url) {
    const msg = urlMsg(url);
    rec('send message: candidate_id + kind for each selected item (verbatim from data)', sel.every(([t]) => msg.includes('｜candidate_id: ' + byTerm[t].candidate_id + '｜種類: ' + byTerm[t].kind)));
    rec('send message: candidates_sha256 line equals data value', msg.includes('候補集合sha256: ' + dat.candidates_sha256));
    rec('send message: AI reason lines carry candidate_id', sel.every(([t]) => msg.includes('・' + t + '(' + byTerm[t].candidate_id + '): ')));
    rec('send message: first 5 blocks unchanged format', msg.includes('① Key Phrase (2/3): ') && msg.includes('② 追加解説 (①＋②=3/5): ') && msg.includes('③ 本文意味表示 (累計=4/12): '));
  }
  await ev(`Object.defineProperty(navigator,'clipboard',{value:{writeText:()=>Promise.reject(new Error('denied'))},configurable:true})`);
  await ev(`document.querySelector('#copy').click()`); await sleep(600);
  const cp = await ev(`document.querySelector('#fallback').value`);
  const j = JSON.parse(cp.slice(cp.indexOf('```json\n') + 8, cp.lastIndexOf('\n```')));
  rec('copy JSON: schema_version 2 / minor 1, article sha fields', j.schema_version === 2 && j.schema_minor === 1 && j.article.candidates_sha256 === dat.candidates_sha256 && j.article.candidates_sha256_source === 'candidate_doc_field' && j.article.source_kp_candidates_path === dat.source_kp_candidates_path);
  rec('copy JSON: selected items have candidate_id/kind equal to data; candidates_all has all 8 ids', sel.every(([t, c]) => { const it = j.selection[['key_phrase', 'extra_explanation', 'meaning_display'][c - 1]].find(x => x.term === t); return it && it.candidate_id === byTerm[t].candidate_id && it.kind === byTerm[t].kind; }) && j.candidates_all.length === 8 && j.candidates_all.every((x, i) => x.candidate_id === dat.phrases.concat(dat.words)[i].candidate_id) && j.ai_reference.items.every(x => x.candidate_id));
  // 猿の手 replay由来: sha null を明示
  await switchTo('猿の手｜Advanced');
  await ev(`document.querySelector('#copy').click()`); await sleep(600);
  const cp2 = await ev(`document.querySelector('#fallback').value`);
  rec('Trial-02/replay data: sha null + reason shown in text, not fabricated', cp2.includes('候補集合sha256: なし(取得不可: unavailable_') && cp2.includes('"candidates_sha256": null'));
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
