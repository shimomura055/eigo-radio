// headless Chrome(CDP)でフォームの実DOM動作を確認する(委任_02: 日本語訳・AI理由・送信データ)。用法: node browser_check_02.mjs <baseUrl> <chromePath> [port]
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const base = process.argv[2];
const chrome = process.argv[3];
const port = Number(process.argv[4] || 9334);
const udd = fs.mkdtempSync(path.join(os.tmpdir(), 'selform2-chrome-'));
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

  // 1) 猿の手 Advanced(Trial-02): 全11候補に日本語訳・仮訳ラベル・AI理由欄
  rec('default article loads with 11 candidate rows', (await ev(`document.querySelectorAll('.item').length`)) === 11);
  rec('every row shows a Japanese gloss line with a status label', (await ev(`document.querySelectorAll('.item .ja .gl').length`)) === 11 && (await ev(`[...document.querySelectorAll('.item .ja .jatext')].every(e=>e.textContent.length>0)`)));
  rec('Trial-02 glosses are labelled 仮訳・未確定 (not 正式訳)', await ev(`[...document.querySelectorAll('.item .gl')].every(e=>e.textContent==='仮訳・未確定')`));
  rec('every row has AI reason details (確認用) collapsed', (await ev(`document.querySelectorAll('.item details.why').length`)) === 11 && !(await ev(`[...document.querySelectorAll('details.why')].some(e=>e.open)`)));
  const body = await ev(`document.body.textContent`);
  rec('hint explains 日本語訳/確認用/仮訳', body.includes('AI理由・確認用') && body.includes('仮訳・未生成'));
  rec('call2 row shows AI reason when opened (compensation)', await ev(`(()=>{const d=[...document.querySelectorAll('details.why')].find(e=>e.dataset.why==='compensation');d.open=true;return d.textContent.includes('補償')&&d.textContent.includes('確認用情報')})()`));
  rec('call1 row says AI reason not available (explicit)', await ev(`(()=>{const d=[...document.querySelectorAll('details.why')].find(e=>e.dataset.why==='accept no responsibility');d.open=true;return d.textContent.includes('AI理由なし')})()`));
  await click('compensation', 3);
  rec('open state survives re-render (checked a box)', await ev(`[...document.querySelectorAll('details.why')].find(e=>e.dataset.why==='compensation').open`));
  await click('compensation', 3);

  // 2) メロスa2(Production正式経路): 正式訳ラベル
  await switchTo('走れメロス');
  rec('melos prod: 7 rows all 正式訳', (await ev(`document.querySelectorAll('.item').length`)) === 7 && (await ev(`[...document.querySelectorAll('.item .gl')].every(e=>e.textContent==='正式訳')`)));
  rec('melos prod: backfill row shows AI reason text', await ev(`(()=>{const d=[...document.querySelectorAll('details.why')].find(e=>e.dataset.why==='a knife flashed');return !!d && !d.textContent.includes('AI理由なし')})()`));

  // 3) 選定→送信文の内容
  const terms = await ev(`[...document.querySelectorAll('input[data-term][data-cat="1"]')].map(e=>e.dataset.term)`);
  await click(terms[0], 1); await click(terms[1], 1); await click(terms[3], 2); await click(terms[4], 3);
  await ev(`(()=>{const t=document.querySelector('#comment');t.value='日本語訳テスト用コメント';t.dispatchEvent(new Event('input',{bubbles:true}))})()`);
  await ev(`window.__opened=null;window.open=function(u){window.__opened=u;return null}`);
  await ev(`document.querySelector('#send').click()`);
  const url = await ev(`window.__opened`);
  rec('send: URL built (<=6000)', typeof url === 'string' && url.length <= 6000, String(url && url.length));
  if (url) {
    const msg = urlMsg(url);
    const gl = await ev(`[...document.querySelectorAll('.item')].map(e=>[e.querySelector('label').textContent,e.querySelector('.jatext').textContent])`);
    const map = Object.fromEntries(gl);
    rec('send message has EN + JA gloss + 正式訳 + category for each selected', [[terms[0], 1], [terms[1], 1], [terms[3], 2], [terms[4], 3]].every(([t, c]) => msg.includes(['', '①Key Phrase', '②追加解説', '③本文意味表示'][c] + '｜' + t + '｜日本語訳: ' + map[t] + '【正式訳】')));
    rec('send message has comment and AI reason section (確認用, separate, after confirmed section)', msg.includes('自由コメント: 日本語訳テスト用コメント') && msg.indexOf('【AI選定理由') > msg.indexOf('【ユーザー確定内容の詳細'));
    rec('send message has grammar section (none selected => 選択なし)', msg.includes('【文法解説(選択分の解説全文)】'));
  }

  // 4) コピー: JSONに全候補・日本語訳・状態
  await ev(`Object.defineProperty(navigator,'clipboard',{value:{writeText:()=>Promise.reject(new Error('denied'))},configurable:true})`);
  await ev(`document.querySelector('#copy').click()`); await sleep(600);
  const cp = await ev(`document.querySelector('#fallback').value`);
  const j = JSON.parse(cp.slice(cp.indexOf('```json\n') + 8, cp.lastIndexOf('\n```')));
  rec('copy JSON v2: schema/selection/ai_reference/candidates_all', j.schema_version === 2 && j.selection.key_phrase.length === 2 && j.selection.key_phrase.every(x => x.ja_gloss && x.ja_gloss_status === 'official') && j.ai_reference.for_reference_only === true && j.candidates_all.length === 7 && j.comment.includes('日本語訳テスト'));
  rec('copy JSON: AI reason not inside confirmed items', j.selection.key_phrase.concat(j.selection.extra_explanation, j.selection.meaning_display).every(x => !('reason_ja' in x)));

  // 5) 文法(ダミー)でも全文が送信文へ
  await switchTo('UI確認用');
  await ev(`document.querySelector('input[data-grammar="g1"]').click()`);
  await ev(`window.__opened=null`); await ev(`document.querySelector('#send').click()`);
  const u2 = await ev(`window.__opened`);
  const gbody = await ev(`document.querySelector('.grammar.selected p').textContent`);
  rec('dummy: selected grammar full body in send message', !!u2 && urlMsg(u2).includes(gbody), u2 ? '' : 'url null');

  // 6) 長文超過: 猿の手で11件選択 -> URL null -> 自動コピー誘導(全項目入りtextareaが出る)
  await switchTo('猿の手｜Advanced');
  const all = await ev(`[...document.querySelectorAll('input[data-term][data-cat="1"]')].map(e=>e.dataset.term)`);
  for (let i = 0; i < all.length; i++) await click(all[i], i < 3 ? 1 : i < 5 ? 2 : 3);
  await ev(`window.__opened=null`); await ev(`document.querySelector('#send').click()`); await sleep(600);
  const u3 = await ev(`window.__opened`); const st3 = await ev(`${q('#status')}.textContent`); const fb3 = await ev(`document.querySelector('#fallback').value`);
  rec('too long: no truncated URL; copy guidance with full text (all selected JA glosses)', u3 === null && st3.includes('長く') && all.every(t => fb3.includes('｜' + t + '｜日本語訳: ')), st3);
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
