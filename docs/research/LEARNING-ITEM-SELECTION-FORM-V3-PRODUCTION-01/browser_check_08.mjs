// headless Chrome(CDP)で送信・コピー改善(委任_08(07の再実行+コメント既定語/末尾=====): 人間可読コピー+照合コード、送信=常時コピー+URL閾値内でChatGPT起動)を実DOMで確認する。
// 用法: node browser_check_08.mjs <baseUrl> <chromePath> [port] [capturedOut.json]
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const base = process.argv[2];
const chrome = process.argv[3];
const port = Number(process.argv[4] || 9348);
const capOut = process.argv[5] || null;
const udd = fs.mkdtempSync(path.join(os.tmpdir(), 'selform8-chrome-'));
const proc = spawn(chrome, ['--headless=new', '--disable-gpu', '--no-first-run', `--remote-debugging-port=${port}`, `--user-data-dir=${udd}`, 'about:blank'], { stdio: 'ignore' });
const results = []; const consoleErrors = []; const captured = [];
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
  try { await send('Emulation.setFocusEmulationEnabled', { enabled: true }); } catch (e) { }
  const origin = new URL(base).origin;
  try { await send('Browser.grantPermissions', { origin, permissions: ['clipboardReadWrite', 'clipboardSanitizedWrite'] }); } catch (e) { rec('grant clipboard permission (info)', true, 'not granted: ' + String(e).slice(0, 80)); }
  await goto(base);
  await ev('localStorage.clear()'); await goto(base);

  const opts = await ev(`[...document.querySelectorAll('#article option')].map((o,i)=>i+':'+o.textContent)`);
  const switchTo = async (...keys) => { const o = opts.find(x => keys.every(k => x.includes(k))); if (!o) throw new Error('article not found ' + keys); await ev(`(()=>{const s=document.querySelector('#article');s.value='${o.split(':')[0]}';s.dispatchEvent(new Event('change'))})()`); await sleep(800); };
  const click = (term, cat) => ev(`(()=>{const el=[...document.querySelectorAll('input[data-term]')].find(e=>e.dataset.term==="${term}"&&e.dataset.cat==="${cat}");if(!el)return 'nf';if(el.disabled)return 'disabled';el.click();return 'ok'})()`);
  const instrument = () => ev(`(()=>{window.__log=[];window.__w=[];window.__opened=[];
    const cb=navigator.clipboard;if(!window.__origWrite)window.__origWrite=cb.writeText.bind(cb);const orig=window.__origWrite;
    window.__failMode=false;
    cb.writeText=function(t){window.__log.push('write');window.__w.push(t);return window.__failMode?Promise.reject(new Error('denied')):orig(t)};
    if(!window.__execOrig)window.__execOrig=document.execCommand.bind(document);document.execCommand=function(c){return window.__failMode?false:window.__execOrig(c)};
    window.open=function(u){window.__log.push('open');window.__opened.push(u);return null};return true})()`);
  const statusOf = () => ev(`({t:document.querySelector('#status').textContent,c:document.querySelector('#status').className})`);
  const waitStatus = async (re) => { for (let i = 0; i < 20; i++) { const s = await statusOf(); if (re.test(s.t)) return s; await sleep(150); } return statusOf(); };
  const CODE = /照合コード\(変更しないでください\)：AIF1-[A-Za-z0-9_]+-[0-9a-f]{6}-[0-9a-f]{8}-[0-9a-f]{8}-[0-9a-f]{10}-([0-9a-f]{10}|0)-([0-9a-f]{8}|0)-[0-9a-f]{4}$/;
  const dataOf = async stem => JSON.parse(await ev(`fetch('data/${stem}.json').then(r=>r.text())`));
  const lastW = () => ev(`window.__w[window.__w.length-1]`);
  const urlMsg = u => decodeURIComponent(u.slice(u.indexOf('?q=') + 3));

  // ---- A. AI島 Standard(KP/KW確定ロック・文法Top2から0件): コピー ----
  await switchTo('AIの仮想の島', 'Standard');
  await instrument();
  await ev(`document.querySelector('#copy').click()`);
  let s = await statusOf();
  rec('undecided grammar blocks copy: no clipboard write, guidance shown', (await ev('window.__w.length')) === 0 && s.t.includes('文法が未決定'), s.t.slice(0, 40));
  await ev(`document.querySelector('input[data-grammar-none]').click()`); await sleep(200);
  const stBefore = await ev(`localStorage.getItem('eigo-kp-form-v3')`);
  await ev(`document.querySelector('#copy').click()`);
  s = await waitStatus(/コピー/);
  const aStd = await lastW();
  captured.push({ case: 'ai_island_a2_copy', text: aStd });
  rec('A. copy (AI島Std locked, grammar none): human-readable text with header/sections/grammar none/free comment/code line', typeof aStd === 'string' && aStd.startsWith('記事：AIの仮想の島｜Standard') && aStd.includes('① Key Phrase\n- ') && aStd.includes('② 追加解説\n- ') && aStd.includes('③ 本文意味表示\n- ') && aStd.includes('文法：選定なし') && aStd.includes('自由コメント：なし') && CODE.test(aStd.trim()), (aStd || '').split('\n').slice(0, 4).join(' / '));
  rec('A. copy text has no JSON / candidate_id / kind / SHA full / AI reason', !/```|candidate_id|"selection"|candidates_sha256|AI選定理由|reason_ja/.test(aStd), '');
  rec('A. copy shows clear success message in OK style', s.t.includes('選定結果をコピーしました') && s.c === 'okmsg', s.t + ' [' + s.c + ']');
  const d6 = aStd.match(/AIF1-ai_island_temple__a2__prod-([0-9a-f]{6})-/)[1];
  const rawSha = await ev(`fetch('data/ai_island_temple__a2__prod.json',{cache:'no-cache'}).then(r=>r.arrayBuffer()).then(b=>crypto.subtle.digest('SHA-256',b)).then(h=>[...new Uint8Array(h)].map(x=>x.toString(16).padStart(2,'0')).join(''))`);
  rec('A. code d6 == SHA-256 of the data file bytes the browser fetched (WebCrypto cross-check of pure-JS sha)', rawSha.startsWith(d6), d6 + ' vs ' + rawSha.slice(0, 6));
  const bodyCnt = await ev(`document.querySelectorAll('#candidates .lockitem').length`);
  rec('A. confirmed 10 items shown locked (UI unchanged)', bodyCnt === 10, String(bodyCnt));
  try {
    const rt = await ev(`navigator.clipboard.readText()`);
    rec('A. real clipboard content == copied text (readText; CRLF-normalized by OS clipboard)', rt.split('\r\n').join('\n') === aStd, 'len ' + (rt || '').length);
  } catch (e) { rec('A. real clipboard readText (info: not readable in this environment)', true, String(e).slice(0, 80)); }
  rec('A. selection state unchanged by copy', (await ev(`localStorage.getItem('eigo-kp-form-v3')`)) === stBefore, '');

  // ---- B. AI島 Standard: 送信 ----
  await instrument();
  await ev(`document.querySelector('#send').click()`);
  s = await waitStatus(/ChatGPT/);
  const bW = await lastW(), bOpen = await ev(`window.__opened[0]`), bLog = await ev(`window.__log.join(',')`);
  captured.push({ case: 'ai_island_a2_send', text: bW });
  rec('B. send: clipboard write starts before window.open (same click)', bLog === 'write,open', bLog);
  rec('B. send: text = PREFACE(verbatim-return request) + readable + code; no "Claude Code向け指示案"', bW.startsWith('以下はeigo-radioの学習項目選定結果です。') && bW.includes('そのままコードブロックで返してください') && !bW.includes('Claude Code向け指示案') && CODE.test(bW.trim()) && bW.includes('記事：AIの仮想の島｜Standard'), bW.split('\n')[0].slice(0, 30));
  rec('B. send within threshold: opens chatgpt.com/?q= with the full text (<=6000 chars)', typeof bOpen === 'string' && bOpen.startsWith('https://chatgpt.com/?q=') && bOpen.length <= 6000 && urlMsg(bOpen) === bW, 'url len ' + (bOpen || '').length);
  rec('B. send within threshold: normal-style message (copied + opened)', s.t.includes('コピーし、ChatGPTを開きました') && s.c === 'okmsg', s.t.slice(0, 50));

  // ---- C. AI島 Advanced: 文法Top1を選択+コメント。解説全文が逐語で入る。URL閾値超なら貼付案内 ----
  await switchTo('AIの仮想の島', 'Advanced');
  await instrument();
  await ev(`document.querySelector('input[data-grammar]').click()`); await sleep(200);
  await ev(`(()=>{const c=document.querySelector('#comment');c.value='文法の例文を\\nもう少し短く';c.dispatchEvent(new Event('input'))})()`);
  const advData = await dataOf('ai_island_temple__b1b__prod');
  const g1 = advData.grammar.slice().sort((a, b) => (a.rank || 99) - (b.rank || 99))[0];
  await ev(`document.querySelector('#copy').click()`); await waitStatus(/コピー/);
  const cW = await lastW(); captured.push({ case: 'ai_island_b1b_copy_grammar1', text: cW });
  const bodyV = g1.body.split(String.fromCharCode(13,10)).join(String.fromCharCode(10)).replace(/\s*=+\s*$/, '');   // 委任_08: 末尾の内部終端記号(直前に改行が無い「。=====」を含む)を除去
  rec('C. copy (Adv, grammar Top1): grammar title + 【解説全文】<verbatim body>【解説ここまで】 without omission', cW.includes('文法：' + g1.title + '\n【解説全文】\n' + bodyV + '\n【解説ここまで】'), 'body chars ' + bodyV.length);
  rec('C. copy: multi-line free comment preserved, code line last', cW.includes('自由コメント：文法の例文を\nもう少し短く\n\n照合コード') && CODE.test(cW.trim()), '');
  await ev(`document.querySelector('#send').click()`); s = await waitStatus(/ChatGPT|貼り付け/);
  const cSendW = await lastW(), cOpen = await ev(`window.__opened[window.__opened.length-1]`);
  captured.push({ case: 'ai_island_b1b_send_grammar1', text: cSendW });
  const longUrl = ('https://chatgpt.com/?q=' + encodeURIComponent(cSendW)).length;
  if (longUrl > 6000) {
    rec('C. send over threshold: opens plain https://chatgpt.com/ (no q), full text copied, normal paste guidance (not an error)', cOpen === 'https://chatgpt.com/' && cSendW.includes(bodyV) && s.t.includes('貼り付け方式') && s.c === 'okmsg', 'url would be ' + longUrl + ' | ' + s.t.slice(0, 60));
  } else {
    rec('C. send within threshold: q= URL carries full text', cOpen.startsWith('https://chatgpt.com/?q=') && urlMsg(cOpen) === cSendW, 'url ' + longUrl);
  }

  // ---- D. 閾値超の強制(長いコメント): AI島Std ----
  await switchTo('AIの仮想の島', 'Standard');
  await instrument();
  await ev(`(()=>{const c=document.querySelector('#comment');c.value='あ'.repeat(1200);c.dispatchEvent(new Event('input'))})()`);
  await ev(`document.querySelector('#send').click()`); s = await waitStatus(/貼り付け|ChatGPT/);
  const dW = await lastW(), dOpen = await ev(`window.__opened[0]`);
  rec('D. over-threshold (long comment): opens chatgpt.com without q, text with the full comment copied, paste guidance in OK style', dOpen === 'https://chatgpt.com/' && dW.includes('あ'.repeat(1200)) && s.t.includes('貼り付け方式') && s.c === 'okmsg', s.t.slice(0, 70));
  await ev(`(()=>{const c=document.querySelector('#comment');c.value='';c.dispatchEvent(new Event('input'))})()`);

  // ---- E. クリップボード失敗: 状態保持+手動コピー枠 ----
  await instrument(); await ev(`window.__failMode=true`);
  const stE = await ev(`localStorage.getItem('eigo-kp-form-v3')`);
  await ev(`document.querySelector('#send').click()`); s = await waitStatus(/自動コピー/);
  const fb = await ev(`({hidden:document.querySelector('#fallback').hidden,v:document.querySelector('#fallback').value})`);
  const eOpen = await ev(`window.__opened[0]`);
  rec('E. clipboard failure: guidance + manual-copy textarea shows the full text; selection state preserved', s.t.includes('自動コピーできませんでした') && fb.hidden === false && fb.v.includes('照合コード(変更しないでください)') && (await ev(`localStorage.getItem('eigo-kp-form-v3')`)) === stE, s.t.slice(0, 40));
  rec('E. clipboard failure on send still opens ChatGPT (q= when within threshold)', typeof eOpen === 'string' && eOpen.startsWith('https://chatgpt.com/'), (eOpen || '').slice(0, 30));
  await ev(`window.__failMode=false`);

  // ---- F. 技術情報付きコピー: 既定非表示の details 内 ----
  const det = await ev(`({open:document.querySelector('details.techbox').open,vis:document.querySelector('#copyTech').checkVisibility()})`);
  rec('F. 技術情報付きコピー is inside collapsed <details> (hidden by default)', det.open === false && det.vis === false, JSON.stringify(det));
  await instrument(); await ev(`document.querySelector('#copyTech').click()`); await waitStatus(/技術情報/);
  const fW = await lastW();
  rec('F. technical copy keeps legacy JSON (candidates_all, candidate_id) for er128 confirm --from-form fallback', fW.includes('```json') && fW.includes('"candidates_all"') && fW.includes('"candidate_id"'), 'len ' + fW.length);

  // ---- G. 上限ロジック不変(非ロック記事・3/5/12・文法1件) ----
  await switchTo('電車マナー', 'Production', 'Advanced');
  const terms = await ev(`[...document.querySelectorAll('input[data-term][data-cat="1"]')].map(e=>e.dataset.term)`);
  const r1 = []; for (let i = 0; i < 4; i++) r1.push(await click(terms[i], 1));
  rec('G. limits unchanged: 4th cat1 disabled (<=3)', r1.join(',') === 'ok,ok,ok,disabled', r1.join(','));
  const r2 = []; for (let i = 3; i < 6; i++) r2.push(await click(terms[i], 2));
  rec('G. limits unchanged: cat1+cat2 <=5', r2.join(',') === 'ok,ok,disabled', r2.join(','));
  const r3 = []; for (let i = 5; i < 12; i++) r3.push(await click(terms[i], 3));
  rec('G. limits unchanged: total 12 selectable', r3.every(x => x === 'ok'), r3.join(','));
  await instrument();
  const gAvail = await ev(`!!document.querySelector('input[data-grammar]')`);
  if (gAvail) await ev(`document.querySelector('input[data-grammar]').click()`);
  await sleep(200);
  await ev(`document.querySelector('#copy').click()`); await waitStatus(/コピー/);
  const gW = await lastW(); captured.push({ case: 'melos_a2_full_12', text: gW });
  const items = (gW.match(/^- /gm) || []).length;
  rec('G. 12 selected items all appear as "- 英語：訳" lines (no omission), code line present', items === 12 && CODE.test(gW.trim()), 'items ' + items);

  rec('no console errors/exceptions', consoleErrors.length === 0, consoleErrors.join(' | '));
  rec('C. (委任_08) AI島b1b Top1 data ends with 。===== but copy text has no =====', /。=====$/.test(g1.body.replace(/\r\n/g, '\n')) && !cW.includes('====='), 'data tail ' + JSON.stringify(g1.body.slice(-6)));
  rec('C. (委任_08) copy text ends at 【解説ここまで】 right after the explanation, then comment', cW.includes('。\n【解説ここまで】\n\n自由コメント：文法の例文を\nもう少し短く\n'), '');
  // ---- D. コメント既定語(委任_08) ----
  for (const [label, val] of [['特になし', '特になし'], ['なし', 'なし'], ['whitespace', '   ']]) {
    await ev(`(()=>{const c=document.querySelector('#comment');c.value=${JSON.stringify(val)};c.dispatchEvent(new Event('input'))})()`);
    await instrument(); await ev(`document.querySelector('#copy').click()`); await waitStatus(/コピー/);
    const w = await lastW();
    rec('D. (委任_08) comment ' + label + ' => 自由コメント：なし and m8=0', typeof w === 'string' && w.includes('\n自由コメント：なし\n') && /-0-[0-9a-f]{4}$/.test(w.trim()), (w || '').slice(-60));
  }
  await ev(`(()=>{const c=document.querySelector('#comment');c.value='本当のコメント';c.dispatchEvent(new Event('input'))})()`);
  await instrument(); await ev(`document.querySelector('#copy').click()`); await waitStatus(/コピー/);
  const wr = await lastW();
  rec('D. (委任_08) real comment kept, m8 != 0', wr.includes('自由コメント：本当のコメント\n') && !/-0-[0-9a-f]{4}$/.test(wr.trim()), '');
  rec('console error 0 (all checks)', consoleErrors.length === 0, consoleErrors.join(' | ').slice(0, 200));
  if (capOut) fs.writeFileSync(capOut, JSON.stringify(captured, null, 1));
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
