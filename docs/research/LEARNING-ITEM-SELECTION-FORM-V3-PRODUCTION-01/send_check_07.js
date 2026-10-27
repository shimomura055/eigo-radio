// 委任_07 SEND_CHECK_04 生成: 全データ×主要ケースの送信文字数・URL長・分岐(URL起動/貼付案内)を新実装(buildChatGptUrl)で実測する。API 0。
// usage: node send_check_07.js  (標準出力にMarkdown表)
const fs = require('fs'), path = require('path'), crypto = require('crypto');
const FD = path.resolve(__dirname, '..', '..', '..', 'user_test', 'selection_form_v3');
const FL = require(path.join(FD, 'form_logic.js'));
const idx = JSON.parse(fs.readFileSync(path.join(FD, 'data', 'articles.json'), 'utf8'));
const files = idx.articles.filter(a => a.data).map(a => a.data);
function stateFor(d, mode) {
  const tl = FL.terms(d), st = FL.newState(), gids = FL.grammarIds(d);
  tl.forEach((x, i) => FL.setChoice(st, tl, x, i < 3 ? 1 : i < 5 ? 2 : 3, true));          // 上限いっぱい(3/2/7、候補不足なら全件)
  if (mode.g && gids.length) FL.chooseGrammar(st, gids, gids[0]); else if (gids.length) FL.chooseGrammarNone(st, gids);
  st.comment = mode.c ? 'あ'.repeat(mode.c) : '';
  return st;
}
const cases = [['KP/KW上限+文法なし+コメントなし', { g: 0, c: 0 }], ['同+文法Top1(解説全文)', { g: 1, c: 0 }], ['同+文法Top1+コメント330字', { g: 1, c: 330 }], ['同+文法なし+コメント1000字', { g: 0, c: 1000 }]];
const rows = [];
files.forEach(f => {
  const raw = fs.readFileSync(path.join(FD, f)), d = JSON.parse(raw.toString('utf8')), sha = crypto.createHash('sha256').update(raw).digest('hex');
  const opts = { stem: path.basename(f, '.json'), file_sha256: sha };
  const cells = cases.map(([n, m]) => {
    if (m.g && !FL.grammarIds(d).length) return '(文法候補なし)';
    const st = stateFor(d, m), r = FL.buildChatGptUrl(d, st, 'T', opts);
    return r.text.length + '字 / URL ' + r.url_length + ' / ' + (r.mode === 'url' ? 'URL起動' : '貼付案内');
  });
  // コメント長の閾値(文法なし・上限選択): 何字までURL起動か
  const st0 = stateFor(d, { g: 0, c: 0 }); let lo = 0, hi = 4000;
  while (lo < hi) { const mid = (lo + hi + 1) >> 1; st0.comment = 'あ'.repeat(mid); if (FL.buildChatGptUrl(d, st0, 'T', opts).url) lo = mid; else hi = mid - 1; }
  rows.push('| ' + f.replace('data/', '').replace('.json', '') + ' | ' + FL.terms(d).length + ' | ' + cells.join(' | ') + ' | ' + lo + '字 |');
});
console.log('| データ | 候補数 | ' + cases.map(c => c[0]).join(' | ') + ' | 文法なしでURL起動を保てる最大コメント長 |');
console.log('|---|---|' + cases.map(() => '---').join('|') + '|---|');
rows.forEach(r => console.log(r));
