// 委任_07 test補助: states(JSON配列 [{file:'data/xxx.json', st:{choices,grammar,grammar_zero,comment}}])を受け取り、
// フォーム実装(form_logic.js)の人間可読コピー(buildReadable)・送信文(buildChatGptUrl)・既存buildStructuredを出力する。
// 照合コードのd6は、フォームがfetchする生バイト列と同じ=ファイルの生バイトのsha256(node標準cryptoで独立算出し、form_logic.jsのsha256Hexと一致を検査)。
// usage: node readable_dump_07.js <states.json>
const fs = require('fs'), path = require('path'), crypto = require('crypto');
const FD = path.resolve(__dirname, '..', '..', '..', 'user_test', 'selection_form_v3');
const FL = require(path.join(FD, 'form_logic.js'));
const states = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const out = states.map(s => {
  const raw = fs.readFileSync(path.resolve(FD, s.file)); const d = JSON.parse(raw.toString('utf8'));
  const sha = crypto.createHash('sha256').update(raw).digest('hex');
  if (FL.sha256Hex(new Uint8Array(raw)) !== sha) throw new Error('sha256Hex mismatch for ' + s.file);
  const opts = { stem: path.basename(s.file, '.json'), file_sha256: sha };
  const st = Object.assign(FL.newState(), s.st);
  return { file: s.file, readable: FL.buildReadable(d, st, opts), send: FL.buildChatGptUrl(d, st, 'T0', opts), structured: FL.buildStructured(d, st, 'T0', { all_candidates: true }) };
});
process.stdout.write(JSON.stringify(out));
